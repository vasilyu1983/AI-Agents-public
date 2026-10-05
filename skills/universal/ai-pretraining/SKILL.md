---
name: ai-pretraining
description: "Builds a GPT and BPE tokenizer from scratch. Use when implementing autograd, attention, a nanoGPT loop, muP hyperparameter transfer, WSD annealing, loss spikes, or mid-training."
compatibility: Portable core. Works on Claude Code and Codex.
version: "1.5"
last_validated: 2026-09-25
---

# Pretraining From Scratch

**Domain**: building a transformer/GPT and a BPE tokenizer from first principles — the from-first-principles training-layer competency. Does NOT cover applications-layer fine-tuning, RLHF, or inference optimization; those belong to sibling skills.

Canonical teachers: Karpathy "Neural Networks: Zero to Hero" (micrograd → makemore → "Let's build GPT" → "Let's build the GPT Tokenizer" → "Let's reproduce GPT-2"), Karpathy nanochat (full-stack from-scratch successor to nanoGPT), Raschka "Build a Large Language Model From Scratch", nanoGPT, minbpe, "Attention Is All You Need".

GPT-2 is the pedagogical spine here — the right thing to build *first*. The modern from-scratch baseline then swaps four components onto that spine (RoPE, RMSNorm, SwiGLU, GQA) and runs attention through FlashAttention/SDPA; see [Modern Architecture Deltas](references/modern-architecture-deltas.md).

## When to Use This Skill

Activate when the user asks about:

- Implementing autograd / backprop from scratch (micrograd-style)
- Building makemore (bigram, MLP, WaveNet-style character LMs)
- Implementing self-attention, multi-head attention, causal masking
- Building the transformer block (pre-norm vs post-norm, residual, FFN)
- Stacking blocks into a GPT with an LM head and weight tying
- Writing the pretraining loop: cross-entropy, bf16 mixed precision, gradient accumulation, gradient checkpointing, cosine LR schedule with warmup, model checkpointing
- Building a BPE tokenizer from scratch: byte-level, merge algorithm, vocab construction, encode/decode (minbpe-style)
- Reproducing GPT-2 (124M) from scratch end-to-end (nanoGPT path)
- Implementing temperature scaling and top-k sampling for text generation

## Scope Boundaries (Use These Skills for Depth)

- **Fine-tuning and adaptation (SFT/PEFT/distillation)** -> [ai-llm](../ai-llm/SKILL.md); **model/provider selection** -> [ai-architecture-advisor](../ai-architecture-advisor/SKILL.md); **deployment** -> [ai-mlops](../ai-mlops/SKILL.md)
- **Multi-GPU training: DDP, FSDP, tensor/pipeline parallelism** -> [ai-distributed-training](../ai-distributed-training/SKILL.md)
- **Token/param budget, Chinchilla scaling, compute-optimal runs** -> [ai-scaling-laws](../ai-scaling-laws/SKILL.md)
- **Dataset curation, deduplication, quality filtering for pretraining** -> [ai-data-curation-pretraining](../ai-data-curation-pretraining/SKILL.md)
- **Evaluation harnesses, benchmark design, evals post-pretraining** -> [ai-evals](../ai-evals/SKILL.md)
- **Mixture-of-Experts (MoE)**: swaps the dense FFN for a router + expert FFNs (DeepSeek-V3/V4, Qwen3-MoE, Kimi-K2, Mixtral). A frontier architectural variant, not a from-scratch fundamental. Build-time mechanics (top-k routing, load-balancing loss, expert granularity, failure modes) are taught in §5 of [Architecture Limitations and Workarounds](references/architecture-limitations-and-workarounds.md); distributed training stays with [ai-distributed-training](../ai-distributed-training/SKILL.md) and serving/inference with [ai-llm-inference](../ai-llm-inference/SKILL.md).
- **Classification fine-tuning, instruction/SFT fine-tuning, LoRA/PEFT**: post-pretraining applications. Raschka's book covers these; this skill stops at pretraining. -> [ai-llm](../ai-llm/SKILL.md)

## Default Workflow

1. **Autograd first**: implement Value class with backward(), build MLP, verify gradients against PyTorch.
2. **Character LM ladder**: bigram table -> MLP (makemore) -> verify loss convergence and sampling.
3. **Attention module**: single-head self-attention with causal mask; verify attention weights sum to 1 per row.
4. **Multi-head attention**: split heads, concatenate, project; compare with `nn.MultiheadAttention` using the same weights, mask, dropout setting and a numerical tolerance.
5. **Transformer block**: add FFN (4x, GELU), pre-LayerNorm, residuals; match nanoGPT block.
6. **GPT assembly**: stack N blocks, add LM head, tie weights with embedding; verify forward pass shape.
7. **Pretraining loop**: DataLoader, cross-entropy, CUDA bf16 via `torch.autocast('cuda', dtype=torch.bfloat16)` when supported, gradient accumulation, cosine or WSD LR, checkpoint (weights *and* data position). Verify on **your** model with `python3 scripts/check_loop.py --model yourmodule:build` (a zero-argument factory returning a fresh model): it checks step-0 loss ≈ `ln(V)`, that accumulated micro-batch gradients equal the large-batch gradient, and that changing future tokens never changes earlier logits. Without `--model` it only runs a built-in demo. Then take the throughput wins: `torch.set_float32_matmul_precision('high')` for TF32, pad `vocab_size` 50257 → 50304, and track MFU rather than tokens/sec. See [Pretraining Loop](references/pretraining-loop.md); parameter counts, FLOPs per token and run times for GPT-2 124M are in its [reference card](references/pretraining-loop.md#gpt-2-124m-reference-card).
8. **BPE tokenizer**: byte-level text encoding, count bigram frequencies, greedy merge loop, build vocab, encode/decode round-trip.
9. **GPT-2 reproduction**: load OpenAI weights via HuggingFace, verify logits match, then train from scratch on FineWeb-Edu.
9a. **Sampling**: implement temperature scaling and top-k sampling for generation; optionally add a KV-cache for inference speed (see Quick Reference).
10. **Modernize**: swap to the modern baseline — RoPE for `wpe`, RMSNorm for LayerNorm, SwiGLU for the GELU-MLP, GQA, and `F.scaled_dot_product_attention`; optionally train with Muon. See [Modern Architecture Deltas](references/modern-architecture-deltas.md).

## Modern Baseline

Build GPT-2 first to understand the mechanics, then apply the deltas — the pre-norm residual skeleton is unchanged; you swap sublayers, not the architecture.

| GPT-2 (2019) | Modern baseline | Why |
|--------------|---------------|-----|
| Learned absolute pos embed (`wpe`) | RoPE (rotary, in attention) | Relative position without a learned position table; test quality beyond the trained context |
| LayerNorm | RMSNorm | Cheaper, no centering/bias, stable at depth |
| GELU-MLP (4×) | SwiGLU (`~8/3×`) | Gated FFN improves quality per param |
| MHA (KV heads = query heads) | GQA (fewer KV heads) | Shrinks KV cache for inference |
| Hand-rolled softmax attention | `F.scaled_dot_product_attention` | PyTorch selects an eligible fused kernel on supported CUDA inputs; check the selected backend before claiming its memory or speed gains |
| AdamW for all params | Muon (2D matrices) + AdamW (embed/head/norms) | Newton-Schulz orthogonalized updates; per-step speedup that shrinks with scale (~2× reported at Moonlight scale, ~1.1× at 1.2B in a controlled benchmark) |
| No q/k normalization | QK-Norm (RMSNorm on q/k before attention) | Bounds attention-logit growth — a stability default in new dense/MoE recipes, not just a speedrun trick (cf. Kimi K2's MuonClip QK-Clip) |

Frontier reference: the `modded-nanoGPT` speedrun stacks Muon, QK-Norm, ReLU², logit softcap, and embedding-skip connections to reach GPT-2-grade FineWeb validation loss far faster than the original nanoGPT on 8×H100. For the full from-scratch *pipeline* (tokenizer → pretrain → SFT → RL → serve), Karpathy's nanochat is the successor to nanoGPT. **Lookup step:** both records move; read the repo README for the current target loss, hardware and time before quoting one, and quote it with the date you read it.

## Hyperparameters, Schedule, Stability

- **Transfer hyperparameters instead of searching at target scale.** Default: parameterize with µP and tune LR/init on a small proxy, then transfer zero-shot to the wide target. µTransfer (Yang et al. 2022, arXiv 2203.03466) tuned on a 40M proxy and beat the published GPT-3 6.7B numbers, with a tuning cost of about 7% of the total pretraining cost. Never grid-search LR at target scale. If you are not using µP, fit η_opt(C) and B_opt(C) on 3+ small proxy budgets and read the target off the fitted law ([ai-scaling-laws](../ai-scaling-laws/SKILL.md), workflow step 6). Not needed for a single-scale 124M reproduction, where one LR sweep suffices.
- **Schedule and annealing.** Cosine when the token budget is fixed; WSD (warmup–stable–decay) when it may change. The decay phase doubles as a cheap data probe (same short anneal with and without a candidate dataset) and as a mid-training stage for the highest-quality data. State warmup in tokens or steps, not as a percentage of the run. See [Pretraining Loop](references/pretraining-loop.md#annealing-data-probe-and-mid-training-stage).
- **Loss spikes (working protocol, not a validated standard).** Log max attention logit, max output logit and the update/weight ratio every step; prevent with QK-norm and a small z-loss; on a spike that does not recover, skip the batch window and roll back to the last good checkpoint; if spikes repeat, lower peak LR. See [Pretraining Loop](references/pretraining-loop.md#loss-spike-protocol).

## Quick Reference

| Component | Key Detail | Common Mistake |
|-----------|-----------|----------------|
| Autograd | `Value.backward()` accumulates `+=` into `.grad`, not `=` | Forgetting to zero grads before `.backward()` |
| Embedding | `nn.Embedding(vocab_size, n_embd)` — random init, learned | Confusing token embed with positional embed shape |
| Causal mask | `torch.tril(torch.ones(T,T))` before softmax; fill `-inf` or `torch.finfo(dtype).min`, not 0 | Using `0` fill — attention leaks future tokens |
| Attention math | `softmax(QK^T / sqrt(d_k)) * V` | Forgetting `/sqrt(d_k)` — variance explodes |
| LayerNorm placement | Pre-norm (before attention/FFN) in GPT-2; original paper was post-norm | Post-norm makes deep stacks hard to train |
| FFN expansion | 4x hidden dim, GELU activation | Using ReLU — slight quality difference, matters at scale |
| Weight tying | LM head shares the embedding matrix (`head.weight = wte.weight`) | Forgetting tying adds a second V×d matrix: +38.6M params (+31%) at GPT-2 124M, not 2× |
| Init scaling | `std=0.02` for most; residual projections: `std=0.02/sqrt(2*n_layer)` | Flat 0.02 everywhere — residual stream variance grows |
| Gradient accumulation | accumulate N micro-batches, divide loss by N, step once | Forgetting to divide loss — effective LR N× too large |
| bf16 autocast | `torch.autocast('cuda', dtype=torch.bfloat16)` | Using fp16 without loss scaling — NaN on older GPUs |
| BPE merges | greedy highest-frequency pair; merge in-place, repeat | Not updating pair counts after each merge — wrong vocab |
| LR schedule | cosine: linear warmup (GPT-3 used ≈375M tokens; nanoGPT's 715 steps × 524,288 tokens matches it), then cosine decay to ~10% of peak. WSD (trapezoidal) when the token budget is not fixed up front | Skipping warmup — loss spike at start; stating warmup as a % of the run, which changes meaning with run length |
| Temperature | `logits / temperature` before softmax; `T<1` sharpens (more deterministic), `T>1` flattens (more random) | Applying temperature after softmax — has no effect on the distribution |
| Top-k sampling | zero out all logits except the top-k before softmax; draw from the remaining distribution | Top-k=1 is greedy decoding; top-k=vocab_size is pure sampling |
| KV-cache | at inference, cache K and V tensors for all past positions; on each new token only compute Q/K/V for the single new position and append to cache | Re-computing all K/V at each generation step; the cache removes the redundant *projection* work (O(T²) → O(T) for K/V), not the attention itself — scoring is still O(T) per step, so total generation stays O(T²) |

## Scale-Up Gate

Prove the tokenizer, data loader, masking, loss, optimizer order, checkpoint restore, and sample generation on a tiny run before reserving large compute. Then run a fixed-budget pilot that records effective tokens, loss by source slice, gradient and activation health, throughput, utilization, and restart equivalence. Scale only when the loss curve and downstream probes improve as expected, the input pipeline is not the bottleneck, and a costed stop rule is written. Successful allocation or falling training loss alone does not justify the next scale.

## Known Traps

- **Zero-grad placement**: call `optimizer.zero_grad()` before the forward pass (or `set_to_none=True` for speed), not after `.step()`.
- **Post-norm vs pre-norm**: original "Attention Is All You Need" uses post-norm; GPT-2 and nanoGPT use pre-norm. Pre-norm trains more stably at depth.
- **Causal mask fill value**: use `float('-inf')` or `torch.finfo(dtype).min`, not a hard-coded `-1e9`. In fp32, `-1e9` does not leak (future weights are exactly 0), but in fp16 `masked_fill(-1e9)` raises an overflow error. Guard fully masked rows (padding): with `-inf` they turn into NaN, with `finfo.min` into a uniform row.
- **Gradient accumulation scaling**: divide the loss by the accumulation steps inside the micro-batch loop, not outside.
- **Weight tying in state_dict**: when saving checkpoints, the LM head weight is the same tensor as the embedding weight — loading requires care to avoid double-counting params.
- **BPE encode-decode round-trip**: bytes, not characters — always encode text as UTF-8 bytes first before running BPE.
- **DataLoader seeding**: fix random seeds for reproducibility across runs; DataLoader worker seeds need explicit `worker_init_fn`.
- **`torch.compile` interaction**: `torch.compile` + gradient checkpointing can conflict in some PyTorch versions — test before enabling both. A compiled model also prefixes `state_dict` keys with `_orig_mod.`, which breaks checkpoint loading into an uncompiled model.
- **DDP gradient sync in the micro-loop**: `require_backward_grad_sync` is reset to `True` by DDP on every forward, so it must be re-assigned per micro-step (or use `model.no_sync()`). Setting it once outside the loop either all-reduces every micro-step or never syncs at all — both silent.
- **Resuming without the data position**: restoring weights and optimizer but restarting the loader re-trains on seen shards with no error.

- Verify PyTorch API details (autocast dtype names, `torch.compile` flags, DataLoader args) against current PyTorch docs before recommending.
- Verify current nanoGPT and minbpe repo states (file structure, hyperparameters) against the GitHub repos — they are actively maintained.

## Common Anti-Patterns

- Implementing attention without verifying `attn_weights.sum(dim=-1)` is all-ones (no causal leak check).
- Skipping the PyTorch parity check: always compare custom layer output to `torch.nn.` equivalent before stacking.
- Starting with the full GPT before the single-head attention works — build bottom-up.
- Training without a baseline loss: for character-level with vocab V, random model should give `ln(V)` loss; check this at step 0.
- Using Adam with default `betas=(0.9, 0.999)` — GPT-3 used `betas=(0.9, 0.95)` for stability at scale, and nanoGPT follows it (the GPT-2 paper does not report betas).
- Tokenizing the entire dataset in memory — stream and chunk for large corpora.
- Shipping the GPT-2 architecture as the *final* product — it is the teaching spine, not the modern baseline. Apply the [modern deltas](references/modern-architecture-deltas.md) (RoPE/RMSNorm/SwiGLU/GQA/SDPA) once the GPT-2 build verifies.

## Core Principles

1. **Build then read**: implement first, then verify against PyTorch source or the paper. Reading first encourages copy-paste, not understanding.
2. **No black boxes**: every component must be verified with a unit check before it's stacked.
3. **One component at a time**: single-head attention -> multi-head -> block -> GPT. Never jump layers.
4. **PyTorch parity check**: compare custom attention with `nn.MultiheadAttention` using matched weights, masks and dropout, within a numerical tolerance.
5. **Fail loud on training metrics**: if step-0 loss deviates from `ln(vocab_size)` by >10%, stop and debug — don't train through bad initialization.

## Navigation: Core References

- **[Transformer From Scratch](references/transformer-from-scratch.md)** — attention math, block assembly, weight init, GPT architecture notes
- **[BPE Tokenizer](references/bpe-tokenizer.md)** — byte-level BPE algorithm, merge loop, vocab construction, encode/decode; plus the tokenizer landscape (SentencePiece, Unigram, SuperBPE, vocab sizing, fertility/compression evaluation)
- **[Pretraining Loop](references/pretraining-loop.md)** — GPT-2 124M reference card (params, FLOPs/token, run times, warmup), training loop anatomy, mixed precision, gradient accumulation, cosine/WSD and annealing, MFU, loss-spike protocol, checkpointing, per-slice eval during pretraining
- **[Research Recipes](references/research-recipes.md)** — µP/muP hyperparameter transfer and the coordinate check, WSD cooldown shape and length, loss-spike classes and their fixes, mid-training and continued-pretraining mixes (replay, re-warming, anneal probes)
- **[Modern Architecture Deltas](references/modern-architecture-deltas.md)** — GPT-2 → modern baseline: RoPE, RMSNorm, SwiGLU, GQA, FlashAttention/SDPA, Muon and the speedrun frontier
- **[Architecture Limitations and Workarounds](references/architecture-limitations-and-workarounds.md)** — failure-mode companion: each component's limitation → workaround → tradeoff (softmax pathologies/attention sinks, MHA→MQA→GQA→MLA + decoupled RoPE, positional design space + YaRN/NTK, MoE routing pitfalls, norm/residual/depth stability, fp8/fp4 precision, long-context, encoder/decoder/encoder-decoder contrast)
- **[Adaptive Depth and Conditional Compute](references/adaptive-depth-and-conditional-compute.md)** — depth-axis conditional computation: Mixture-of-Depths, early exit (LayerSkip/TIDE), looped and recursive transformers (Mixture-of-Recursions, AdaPonderLM), cross-layer weight sharing (ALBERT, tied experts), modular-NN framing; lever-selection table
- **[Structured and Low-Rank Parameterization](references/structured-and-low-rank-parameterization.md)** — replacing dense weights: low-rank, block-diagonal, butterfly, Monarch, Kronecker, BLAST; SVD-LLM/ASVD post-hoc factorization; MLA as low-rank KV; `MonarchLinear` and `BlockLowRankLinear` sketches; when it beats or composes with pruning/quantization

## Scripts

- **`scripts/check_loop.py --model module:factory`** — runs three checks on your model: step-0 loss ≈ `ln(V)`, accumulated micro-batch gradient ≡ large-batch gradient, and no future leak (earlier logits unchanged when later tokens change). The factory takes no arguments and returns a fresh `nn.Module` whose forward returns logits or `(logits, ...)`. Without `--model` it runs a built-in demo that says nothing about your code. Requires PyTorch (CPU is fine). Exit 0 pass, 1 a check failed, 2 usage/import error. Tests: `python3 scripts/test_check_loop.py`.

## Learnings Loop

When prior decisions or pitfalls are relevant, consult `learnings.consolidated.md` if present; use `learnings.md` only for needed history or as the available fallback. Otherwise skip both.

After applying it, if you encountered a pattern worth remembering, a mistake worth preventing, or a domain fact that surprised you, append one dated bullet to `learnings.md` via `agents-skills-feedback-loop/scripts/append_learning.py`. Do not modify `SKILL.md` itself.
