#!/usr/bin/env python3
"""Pre-flight checks for a from-scratch language model, run on YOUR model.

    python3 check_loop.py --model mypkg.model:build        # importable module
    python3 check_loop.py --model path/to/model.py:build   # file path
    python3 check_loop.py                                   # built-in demo model only

`build` is a zero-argument factory returning a freshly initialized nn.Module
whose forward takes token ids of shape (B, T) and returns logits (B, T, V),
or a tuple whose first element is the logits (nanoGPT's `(logits, loss)` works).

Checks (all in model.eval(), fp32, CPU unless the model lives elsewhere):
1. Step-0 loss is within --tol of ln(V) (V inferred from the logits).
   A checkpointed or badly initialized model fails this on purpose.
2. Gradients accumulated over micro-batches, each loss divided by the number
   of micro-batches, equal the gradient of one large batch.
3. Causality: changing tokens at positions >= t must not change the logits
   at positions < t (catches a missing or wrong mask in any attention).

Without --model the checks run on a tiny built-in causal LM. That is a demo
of the checks, not evidence about your model.

Exit codes: 0 all checks pass, 1 a check failed, 2 usage or import error.
"""
import argparse
import importlib
import importlib.util
import math
import os
import sys

try:
    import torch
    import torch.nn as nn
    import torch.nn.functional as F
except ImportError:
    print("check_loop.py requires PyTorch (pip install torch); no checks were run.", file=sys.stderr)
    sys.exit(2)


class DemoLM(nn.Module):
    """Built-in demo: embedding -> one causal self-attention layer -> tied head."""

    def __init__(self, vocab_size=257, n_embd=32, block_size=64):
        super().__init__()
        self.emb = nn.Embedding(vocab_size, n_embd)
        self.pos = nn.Embedding(block_size, n_embd)
        self.qkv = nn.Linear(n_embd, 3 * n_embd)
        self.out = nn.Linear(n_embd, n_embd)
        self.head = nn.Linear(n_embd, vocab_size, bias=False)
        self.head.weight = self.emb.weight  # weight tying
        nn.init.normal_(self.emb.weight, std=0.02)
        nn.init.normal_(self.pos.weight, std=0.02)

    def forward(self, idx):
        T = idx.size(1)
        x = self.emb(idx) + self.pos(torch.arange(T, device=idx.device))
        q, k, v = self.qkv(x).chunk(3, dim=-1)
        y = F.scaled_dot_product_attention(q, k, v, is_causal=True)
        return self.head(x + self.out(y))


def load_factory(spec):
    if ":" not in spec:
        raise ValueError(f"--model must look like module:factory or file.py:factory, got {spec!r}")
    target, attr = spec.rsplit(":", 1)
    if target.endswith(".py"):
        if not os.path.isfile(target):
            raise ValueError(f"model file not found: {target}")
        mod_spec = importlib.util.spec_from_file_location("user_model", target)
        module = importlib.util.module_from_spec(mod_spec)
        mod_spec.loader.exec_module(module)
    else:
        sys.path.insert(0, os.getcwd())
        module = importlib.import_module(target)
    factory = getattr(module, attr, None)
    if not callable(factory):
        raise ValueError(f"{attr!r} is not a callable in {target}")
    return factory


def logits_of(model, idx):
    out = model(idx)
    if isinstance(out, (tuple, list)):
        out = out[0]
    if not torch.is_tensor(out) or out.dim() != 3:
        raise ValueError("forward(idx) must return logits of shape (B, T, V) or a tuple starting with them")
    return out.float()


def lm_loss(logits, targets):
    return F.cross_entropy(logits.reshape(-1, logits.size(-1)), targets.reshape(-1))


def check_baseline_loss(model, vocab, device, seq_len, tol):
    g = torch.Generator().manual_seed(0)
    x = torch.randint(0, vocab, (4, seq_len), generator=g).to(device)
    y = torch.randint(0, vocab, (4, seq_len), generator=g).to(device)
    with torch.no_grad():
        loss = lm_loss(logits_of(model, x), y).item()
    expected = math.log(vocab)
    rel = abs(loss - expected) / expected
    if not rel < tol:
        raise AssertionError(f"step-0 loss {loss:.4f} vs ln({vocab})={expected:.4f} (rel {rel:.1%} > {tol:.0%})")
    return f"step-0 loss {loss:.4f} ~= ln({vocab}) = {expected:.4f}"


def check_grad_accumulation(model, vocab, device, seq_len, n_micro=4, micro_b=2):
    g = torch.Generator().manual_seed(1)
    x = torch.randint(0, vocab, (n_micro * micro_b, seq_len), generator=g).to(device)
    y = torch.randint(0, vocab, (n_micro * micro_b, seq_len), generator=g).to(device)
    params = [p for p in model.parameters() if p.requires_grad]

    model.zero_grad(set_to_none=True)
    lm_loss(logits_of(model, x), y).backward()
    full = [p.grad.detach().clone() if p.grad is not None else None for p in params]

    model.zero_grad(set_to_none=True)
    for i in range(n_micro):
        sl = slice(i * micro_b, (i + 1) * micro_b)
        (lm_loss(logits_of(model, x[sl]), y[sl]) / n_micro).backward()
    accum = [p.grad.detach().clone() if p.grad is not None else None for p in params]
    model.zero_grad(set_to_none=True)

    for a, b in zip(full, accum):
        if a is None or b is None:
            if a is not None or b is not None:
                raise AssertionError("a parameter got a gradient in only one of the two runs")
            continue
        if not torch.allclose(a, b, rtol=1e-4, atol=1e-6):
            raise AssertionError(
                f"accumulated grad != large-batch grad (max abs diff {(a - b).abs().max().item():.3e})")
    return f"{n_micro} micro-batches of {micro_b} == one batch of {n_micro * micro_b} (allclose)"


def check_causality(model, vocab, device, seq_len):
    g = torch.Generator().manual_seed(2)
    idx = torch.randint(0, vocab, (1, seq_len), generator=g).to(device)
    t = seq_len // 2
    changed = idx.clone()
    changed[:, t:] = (idx[:, t:] + 1 + torch.randint(0, vocab - 1, (1, seq_len - t), generator=g).to(device)) % vocab
    with torch.no_grad():
        a = logits_of(model, idx)[:, :t]
        b = logits_of(model, changed)[:, :t]
    diff = (a - b).abs().max().item()
    if not diff <= 1e-5:
        raise AssertionError(f"logits before position {t} changed by {diff:.3e} when only later tokens changed (future leak)")
    return f"logits at positions < {t} unchanged when tokens >= {t} change (max diff {diff:.1e})"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--model", help="module:factory or file.py:factory returning a fresh nn.Module")
    ap.add_argument("--seq-len", type=int, default=16, help="sequence length for the checks (default 16)")
    ap.add_argument("--tol", type=float, default=0.10, help="relative tolerance for the ln(V) check (default 0.10)")
    args = ap.parse_args(argv)
    if args.seq_len < 2:
        ap.error("--seq-len must be at least 2")
    if not math.isfinite(args.tol) or args.tol <= 0:
        ap.error("--tol must be a positive finite number")

    if args.model is not None:
        try:
            model = load_factory(args.model)()
        except Exception as exc:  # import or construction failure is a usage error, not a check result
            print(f"ERROR loading --model {args.model}: {exc}", file=sys.stderr)
            return 2
        print(f"Checking user model from {args.model}")
    else:
        torch.manual_seed(0)
        model = DemoLM()
        print("DEMO: no --model given; running the checks on the built-in DemoLM (says nothing about your model)")

    model.eval()  # disable dropout so the gradient and causality checks are deterministic
    device = next(model.parameters()).device
    with torch.no_grad():
        vocab = logits_of(model, torch.zeros(1, args.seq_len, dtype=torch.long, device=device)).size(-1)

    failures = 0
    for name, fn in (
        ("baseline loss ~ ln(V)", lambda: check_baseline_loss(model, vocab, device, args.seq_len, args.tol)),
        ("grad accumulation == large batch", lambda: check_grad_accumulation(model, vocab, device, args.seq_len)),
        ("causality (no future leak)", lambda: check_causality(model, vocab, device, args.seq_len)),
    ):
        try:
            print(f"PASS  {name}: {fn()}")
        except AssertionError as exc:
            failures += 1
            print(f"FAIL  {name}: {exc}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
