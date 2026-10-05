#!/usr/bin/env python3
"""Shared training arithmetic for the pretraining skills (scaling laws, pretraining,
data curation, distributed training, post-training).

Pure Python, no dependencies. Every function states its formula and assumptions in
its docstring. Use it to re-derive worked examples instead of doing the arithmetic
by hand: the 2026-09 audit found 14 wrong hand-computed numbers across these skills.

CLI (each subcommand prints its inputs and results; add --json for machine output):

  training_math.py params --layers 12 --d-model 768 --vocab 50257 --context 1024
  training_math.py flops --params 1.244e8 --tokens 1e10 --layers 12 --d-model 768 --context 1024
  training_math.py mfu --tokens-per-sec 65430 --flops-per-token 3.18e12 --gpus 2240 --peak 312e12
  training_math.py hours --flops 6e20 --gpus 8 --peak 312e12 --mfu 0.40
  training_math.py optimum --compute 5.76e23
  training_math.py lsh --bands 14 --rows 8 --similarity 0.5 0.75 0.8
  training_math.py activations --seq 8192 --batch 1 --hidden 4096 --layers 32 --heads 32

Invalid input exits 2 with a message on stderr; nothing is guessed or clamped.
"""

from __future__ import annotations

import argparse
import json
import math
import sys


def _positive(name: str, value: float) -> None:
    if not (isinstance(value, (int, float)) and math.isfinite(value) and value > 0):
        raise ValueError(f"{name} must be a finite number > 0, got {value!r}")


def _positive_int(name: str, value: int) -> None:
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise ValueError(f"{name} must be an integer > 0, got {value!r}")


# --------------------------------------------------------------------------- params
def decoder_params(
    n_layer: int,
    d_model: int,
    vocab: int,
    context: int = 0,
    ffn_hidden: int | None = None,
    n_head: int | None = None,
    n_kv_head: int | None = None,
    gated_ffn: bool = False,
    rmsnorm: bool = False,
    bias: bool = True,
    tied: bool = True,
) -> dict:
    """Parameter count of a decoder-only transformer.

    Per layer (pre-norm block, two norms):
      attention  = d*(d + 2*d_kv) + d*d            (Q, K, V, output projections)
                   + (d + 2*d_kv + d) if bias
      ffn        = k * d * f  (k = 3 for a gated/SwiGLU FFN, 2 for GELU-MLP)
                   + (f + d) if bias and not gated
      norms      = 2 * (2d for LayerNorm with bias, d for RMSNorm)
    where d_kv = d * n_kv_head / n_head (GQA/MQA; equals d for multi-head attention)
    and f = ffn_hidden (default 4d).
    Model = token embedding V*d + learned position table context*d (0 for RoPE/ALiBi:
    pass context=0) + L * per_layer + final norm + (V*d if the LM head is untied).

    Assumptions: no biases on a gated FFN, norms have a bias only when LayerNorm and
    bias=True, the LM head has no bias. Conventions: "non_embedding" excludes the token
    and position tables (Kaplan's N); "total" includes them (Chinchilla's N); "matmul"
    is the N to use in 6N / PaLM FLOPs: total minus the position table (a lookup),
    and minus the input embedding when the head is untied (a tied head reuses the
    embedding matrix as the output matmul, so it counts once).
    """
    for name, v in (("n_layer", n_layer), ("d_model", d_model), ("vocab", vocab)):
        _positive_int(name, v)
    if isinstance(context, bool) or not isinstance(context, int) or context < 0:
        raise ValueError(f"context must be an integer >= 0, got {context!r}")
    f = 4 * d_model if ffn_hidden is None else ffn_hidden
    _positive_int("ffn_hidden", f)
    if (n_head is None) != (n_kv_head is None):
        raise ValueError("give both n_head and n_kv_head, or neither")
    if n_head is None:
        d_kv = d_model
    else:
        _positive_int("n_head", n_head)
        _positive_int("n_kv_head", n_kv_head)
        if d_model % n_head or n_head % n_kv_head:
            raise ValueError("d_model must divide by n_head, and n_head by n_kv_head")
        d_kv = d_model * n_kv_head // n_head

    d = d_model
    attn = d * (d + 2 * d_kv) + d * d + ((d + 2 * d_kv + d) if bias else 0)
    ffn = (3 if gated_ffn else 2) * d * f + ((f + d) if bias and not gated_ffn else 0)
    norm = d if rmsnorm else (2 * d if bias else d)
    per_layer = attn + ffn + 2 * norm
    embedding = vocab * d
    position = context * d
    lm_head = 0 if tied else vocab * d
    total = embedding + position + n_layer * per_layer + norm + lm_head
    return {
        "total": total,
        "embedding": embedding,
        "position": position,
        "per_layer": per_layer,
        "lm_head_untied": lm_head,
        "non_embedding": total - embedding - position - lm_head,
        "matmul": total - position - (0 if tied else embedding),
    }


# ---------------------------------------------------------------------------- FLOPs
def training_flops_6nd(n_params: float, tokens: float) -> float:
    """Training compute C = 6 * N * D.

    2N FLOPs per token forward and 4N backward (two matmuls per forward matmul),
    counting dense matmuls only. Excludes the attention score/value matmuls (see
    palm_flops_per_token), norms, softmax and optimizer steps, and activation
    recomputation. State which N you use: Kaplan fits count non-embedding N,
    Chinchilla counts total N. For MoE, N is the activated parameter count.
    """
    _positive("n_params", n_params)
    _positive("tokens", tokens)
    return 6.0 * n_params * tokens


def palm_flops_per_token(n_params: float, n_layer: int, d_model: int, context: int) -> float:
    """Model FLOPs per training token, PaLM form: 6N + 12 * L * d * T.

    From PaLM (Chowdhery et al. 2022, arXiv 2204.02311, App. B), written there as
    6N + 12*L*H*Q*T with H heads of size Q (H*Q = d). The second term is the
    attention QK^T and AV matmuls over a context of T, forward plus backward, for
    dense causal attention counted without masking savings. N should be the
    parameters that take part in matmuls (for a tied head, count the embedding once;
    leave out a learned position table). Recomputation is not counted: this is the
    numerator for MFU, not HFU.
    """
    _positive("n_params", n_params)
    for name, v in (("n_layer", n_layer), ("d_model", d_model), ("context", context)):
        _positive_int(name, v)
    return 6.0 * n_params + 12.0 * n_layer * d_model * context


def mfu(tokens_per_sec: float, flops_per_token: float, n_gpus: int, peak_flops: float) -> float:
    """Model FLOPs utilization = tokens/s * model FLOPs per token / (GPUs * peak FLOP/s).

    Peak is the dense (not 2:4-sparse) datasheet figure for the training dtype.
    flops_per_token excludes recomputation (use palm_flops_per_token, or 6N when the
    source omits attention; say which). A result above 1 means an input or the
    FLOP convention is wrong.
    """
    _positive("tokens_per_sec", tokens_per_sec)
    _positive("flops_per_token", flops_per_token)
    _positive_int("n_gpus", n_gpus)
    _positive("peak_flops", peak_flops)
    utilization = tokens_per_sec * flops_per_token / (n_gpus * peak_flops)
    if not math.isfinite(utilization) or utilization > 1:
        raise ValueError(f"mfu must be finite and no greater than 1, got {utilization!r}")
    return utilization


def train_hours(total_flops: float, n_gpus: int, peak_flops: float, utilization: float) -> float:
    """Wall-clock hours = FLOPs / (GPUs * peak FLOP/s * MFU * 3600).

    The inverse of the MFU definition. utilization must be in (0, 1]; solve for it
    from a quoted run time to sanity-check the quote (above ~0.6 for dense training
    needs an explanation, above 1 is impossible).
    """
    _positive("total_flops", total_flops)
    _positive_int("n_gpus", n_gpus)
    _positive("peak_flops", peak_flops)
    _positive("utilization", utilization)
    if utilization > 1:
        raise ValueError(f"utilization is a fraction in (0, 1], got {utilization}")
    return total_flops / (n_gpus * peak_flops * utilization * 3600.0)


# ------------------------------------------------------------------ compute-optimal
def chinchilla_20to1(compute: float, tokens_per_param: float = 20.0) -> tuple[float, float]:
    """(N*, D*) from C = 6ND with D = k*N: N* = sqrt(C / (6k)), D* = k*N*.

    With k = 20 this is N* = (C/120)^0.5 and D* = (C/0.3)^0.5: algebra on the 20:1
    heuristic, not a table from Hoffmann et al. Refit k on your own data.
    """
    _positive("compute", compute)
    _positive("tokens_per_param", tokens_per_param)
    n = math.sqrt(compute / (6.0 * tokens_per_param))
    return n, tokens_per_param * n


def parametric_optimum(compute: float, A: float, B: float, alpha: float, beta: float) -> tuple[float, float]:
    """(N*, D*) minimizing L = E + A/N^alpha + B/D^beta subject to C = 6ND.

    Closed form (Hoffmann et al. 2022, eq. 4): G = (alpha*A / (beta*B))^(1/(alpha+beta)),
    N* = G * (C/6)^(beta/(alpha+beta)), D* = (C/6) / N*. E does not move the optimum.
    Published constants: Hoffmann eq. 3 A=406.4, B=410.7, alpha=0.34, beta=0.28;
    Besiroglu et al. 2024 refit (arXiv 2404.10102) A=482.01, B=2085.43,
    alpha=0.3478, beta=0.3658. The fit is only as good as its corpus and budget range.
    """
    for name, v in (("compute", compute), ("A", A), ("B", B), ("alpha", alpha), ("beta", beta)):
        _positive(name, v)
    g = (alpha * A / (beta * B)) ** (1.0 / (alpha + beta))
    n = g * (compute / 6.0) ** (beta / (alpha + beta))
    return n, (compute / 6.0) / n


# ------------------------------------------------------------------------ MinHash LSH
def lsh_candidate_probability(similarity: float, bands: int, rows: int) -> float:
    """P(a pair becomes an LSH candidate) = 1 - (1 - s^r)^b.

    b bands of r rows use b*r MinHash permutations. Assumes each MinHash row matches
    with probability s (the pair's Jaccard similarity) independently. The S-curve's
    steep point is near lsh_threshold(b, r); recall at that similarity is well below 1.
    """
    if not (isinstance(similarity, (int, float)) and 0.0 <= similarity <= 1.0):
        raise ValueError(f"similarity must be in [0, 1], got {similarity!r}")
    _positive_int("bands", bands)
    _positive_int("rows", rows)
    return 1.0 - (1.0 - similarity ** rows) ** bands


def lsh_threshold(bands: int, rows: int) -> float:
    """Approximate steep point of the LSH S-curve: (1/b)^(1/r)."""
    _positive_int("bands", bands)
    _positive_int("rows", rows)
    return (1.0 / bands) ** (1.0 / rows)


# ----------------------------------------------------------------- activation memory
def activation_memory_bytes(
    seq: int,
    micro_batch: int,
    hidden: int,
    n_layer: int,
    n_heads: int,
    tp: int = 1,
    sequence_parallel: bool = False,
    flash_attention: bool = False,
) -> dict:
    """Stored activations for backward, Korthikanti et al. 2022 (arXiv 2205.05198).

    Per layer, in bytes, with s = seq, b = micro-batch, h = hidden, a = heads, t = TP:
      no parallelism           s*b*h*(34 + 5*a*s/h)
      tensor parallel          s*b*h*(10 + 24/t + 5*a*s/(h*t))
      tensor + sequence par.   s*b*h*(34/t + 5*a*s/(h*t))
    Assumptions: 16-bit activations, 1-byte dropout masks, GPT-style block (GELU MLP
    of width 4h), no activation recomputation. The 5*a*s/h term is the stored
    attention scores, softmax output and its dropout mask; FlashAttention (or
    selective recomputation) never stores them, so flash_attention=True drops it.
    Full per-layer recomputation instead stores about 2*s*b*h per layer.
    Excludes weights, gradients, optimizer state, embeddings and the output layer.
    """
    for name, v in (("seq", seq), ("micro_batch", micro_batch), ("hidden", hidden),
                    ("n_layer", n_layer), ("n_heads", n_heads), ("tp", tp)):
        _positive_int(name, v)
    sbh = seq * micro_batch * hidden
    quad = 0.0 if flash_attention else 5.0 * n_heads * seq / (hidden * tp)
    if sequence_parallel:
        linear = 34.0 / tp
    else:
        linear = 10.0 + 24.0 / tp
    per_layer_without_quad = sbh * linear
    per_layer = sbh * (linear + quad)
    return {
        "per_layer": per_layer,
        "total": per_layer * n_layer,
        "quadratic_share": (per_layer - per_layer_without_quad) / per_layer,
    }


# ------------------------------------------------------------------------------- CLI
def _cli(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(
        prog="training_math.py",
        description="Training arithmetic: params, FLOPs, MFU, hours, compute-optimal "
        "sizing, MinHash LSH banding, activation memory. Formulas are in each "
        "function's docstring.",
    )
    p.add_argument("--json", action="store_true", help="print JSON instead of text")
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("params", help="decoder-only transformer parameter count")
    s.add_argument("--layers", type=int, required=True)
    s.add_argument("--d-model", type=int, required=True)
    s.add_argument("--vocab", type=int, required=True)
    s.add_argument("--context", type=int, default=0, help="learned position table size; 0 for RoPE")
    s.add_argument("--ffn-hidden", type=int, help="FFN width (default 4*d_model)")
    s.add_argument("--heads", type=int, help="query heads (with --kv-heads, for GQA/MQA)")
    s.add_argument("--kv-heads", type=int)
    s.add_argument("--gated-ffn", action="store_true", help="SwiGLU-style 3-matrix FFN")
    s.add_argument("--rmsnorm", action="store_true")
    s.add_argument("--no-bias", action="store_true")
    s.add_argument("--untied", action="store_true", help="separate LM head matrix")

    s = sub.add_parser("flops", help="6ND and PaLM-form training FLOPs")
    s.add_argument("--params", type=float, required=True, help="N for 6N (matmul params)")
    s.add_argument("--tokens", type=float, required=True)
    s.add_argument("--layers", type=int, help="with --d-model and --context: PaLM attention term")
    s.add_argument("--d-model", type=int)
    s.add_argument("--context", type=int)

    s = sub.add_parser("mfu", help="model FLOPs utilization")
    s.add_argument("--tokens-per-sec", type=float, required=True)
    s.add_argument("--flops-per-token", type=float, required=True)
    s.add_argument("--gpus", type=int, required=True)
    s.add_argument("--peak", type=float, required=True, help="dense peak FLOP/s per GPU")

    s = sub.add_parser("hours", help="wall-clock hours from FLOPs, GPUs, peak and MFU")
    s.add_argument("--flops", type=float, required=True)
    s.add_argument("--gpus", type=int, required=True)
    s.add_argument("--peak", type=float, required=True)
    s.add_argument("--mfu", type=float, required=True, help="fraction in (0, 1]")

    s = sub.add_parser("optimum", help="compute-optimal N and D for a FLOP budget")
    s.add_argument("--compute", type=float, required=True)
    s.add_argument("--tokens-per-param", type=float, default=20.0)

    s = sub.add_parser("lsh", help="MinHash LSH candidate probability")
    s.add_argument("--bands", type=int, required=True)
    s.add_argument("--rows", type=int, required=True)
    s.add_argument("--similarity", type=float, nargs="+", default=[0.5, 0.75, 0.8])

    s = sub.add_parser("activations", help="stored activation memory (Korthikanti 2022)")
    s.add_argument("--seq", type=int, required=True)
    s.add_argument("--batch", type=int, required=True)
    s.add_argument("--hidden", type=int, required=True)
    s.add_argument("--layers", type=int, required=True)
    s.add_argument("--heads", type=int, required=True)
    s.add_argument("--tp", type=int, default=1)
    s.add_argument("--sequence-parallel", action="store_true")

    args = p.parse_args(argv)
    try:
        if args.cmd == "params":
            out = decoder_params(args.layers, args.d_model, args.vocab, args.context,
                                 args.ffn_hidden, args.heads, args.kv_heads, args.gated_ffn,
                                 args.rmsnorm, not args.no_bias, not args.untied)
        elif args.cmd == "flops":
            out = {"flops_6nd": training_flops_6nd(args.params, args.tokens)}
            extra = (args.layers, args.d_model, args.context)
            if any(v is not None for v in extra):
                if any(v is None for v in extra):
                    raise ValueError("--layers, --d-model and --context go together")
                fpt = palm_flops_per_token(args.params, *extra)
                out.update({"palm_flops_per_token": fpt, "flops_palm": fpt * args.tokens,
                            "palm_over_6n": fpt / (6 * args.params)})
        elif args.cmd == "mfu":
            out = {"mfu": mfu(args.tokens_per_sec, args.flops_per_token, args.gpus, args.peak)}
        elif args.cmd == "hours":
            h = train_hours(args.flops, args.gpus, args.peak, args.mfu)
            out = {"hours": h, "gpu_hours": h * args.gpus}
        elif args.cmd == "optimum":
            n, d = chinchilla_20to1(args.compute, args.tokens_per_param)
            out = {"n_opt": n, "d_opt": d}
            for label, consts in (("hoffmann", (406.4, 410.7, 0.34, 0.28)),
                                  ("besiroglu", (482.01, 2085.43, 0.3478, 0.3658))):
                pn, pd = parametric_optimum(args.compute, *consts)
                out[f"{label}_n_opt"], out[f"{label}_d_opt"] = pn, pd
                out[f"{label}_tokens_per_param"] = pd / pn
        elif args.cmd == "lsh":
            out = {"threshold": lsh_threshold(args.bands, args.rows),
                   "permutations": args.bands * args.rows}
            for sim in args.similarity:
                out[f"p_at_{sim:g}"] = lsh_candidate_probability(sim, args.bands, args.rows)
        else:  # activations
            out = {}
            for flash in (False, True):
                r = activation_memory_bytes(args.seq, args.batch, args.hidden, args.layers,
                                            args.heads, args.tp, args.sequence_parallel, flash)
                key = "flash" if flash else "materialized"
                out[f"{key}_total_GB"] = r["total"] / 1e9
                out[f"{key}_per_layer_GB"] = r["per_layer"] / 1e9
                if not flash:
                    out["quadratic_share"] = r["quadratic_share"]
        for name, value in out.items():
            if isinstance(value, float) and not math.isfinite(value):
                raise ValueError(f"{name} is non-finite; reduce input magnitude")
    except ValueError as exc:
        p.error(str(exc))  # exits 2
    if args.json:
        print(json.dumps(out, indent=2))
    else:
        for k, v in out.items():
            print(f"{k:28s} {v:,}" if isinstance(v, int) else f"{k:28s} {v:.4g}")
    return 0


if __name__ == "__main__":
    sys.exit(_cli())
