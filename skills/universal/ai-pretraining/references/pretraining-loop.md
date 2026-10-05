# Pretraining Loop

Reference for the GPT pretraining training loop, covering mixed precision, gradient accumulation, learning rate scheduling, and checkpointing.

## Table of Contents

- [Canonical Sources](#canonical-sources)
- [GPT-2 124M Reference Card](#gpt-2-124m-reference-card)
- [Loop Anatomy](#loop-anatomy)
- [Mixed Precision](#mixed-precision)
- [Gradient Accumulation](#gradient-accumulation)
- [Cosine LR with Warmup](#cosine-lr-with-warmup)
- [WSD / Trapezoidal Schedule](#wsd--trapezoidal-schedule)
- [Annealing: Data Probe and Mid-Training Stage](#annealing-data-probe-and-mid-training-stage)
- [Throughput: TF32, Vocab Padding, MFU](#throughput-tf32-vocab-padding-mfu)
- [Gradient Clipping](#gradient-clipping)
- [Loss-Spike Protocol](#loss-spike-protocol)
- [Checkpointing](#checkpointing)
- [Baseline Loss Check](#baseline-loss-check)
- [Eval During Pretraining](#eval-during-pretraining)
- [Common Mistakes](#common-mistakes)

## Canonical Sources

- Karpathy "Let's reproduce GPT-2 (124M)" — [youtube.com/watch?v=l8pRSuU81PU](https://www.youtube.com/watch?v=l8pRSuU81PU)
- nanoGPT `train.py` — [github.com/karpathy/nanoGPT](https://github.com/karpathy/nanoGPT/blob/master/train.py)
- PyTorch AMP docs — [pytorch.org/docs/stable/amp.html](https://pytorch.org/docs/stable/amp.html)
- GPT-3 paper (Brown et al. 2020) for hyperparameter reference — [arxiv.org/abs/2005.14165](https://arxiv.org/abs/2005.14165)

## GPT-2 124M Reference Card

This skill owns these numbers; other skills link here instead of restating them. Config: 12 layers, width 768, 12 heads, context 1024, vocab 50257, tied LM head. All figures are reproduced by `ai-scaling-laws/scripts/training_math.py` (`params`, `flops`, `hours`); run it for any other config.

| Quantity | Value |
|---|---|
| Total parameters (tied head) | 124,439,808 |
| Token embedding `wte` | 38,597,376 (31.0% of total) |
| Position embedding `wpe` | 786,432 |
| Per transformer block | 7,087,872 |
| Non-embedding parameters | 85,056,000 |
| Untied LM head instead | 163,037,184 total (+31%, not 2×) |
| Tokens at 20:1 (total N) | ≈2.49B |

**FLOPs per token (training):**

| Accounting | FLOP/token | Note |
|---|---|---|
| 6·N_nonemb (Kaplan-style) | 5.10e8 | Drops the LM-head matmul and attention; undercounts |
| 6·N_total | 7.47e8 | Includes the head matmul |
| 6·N_matmul + 12·L·d·T (PaLM-style) | 8.55e8 | N_matmul = total minus `wpe` (a lookup, not a matmul); attention term 12·L·d·T = 1.13e8 |

PaLM-style / 6·N_nonemb = 1.68: an MFU of 40% computed with 6·N_nonemb is really ≈67% under PaLM accounting. MFU and HFU definitions: [ai-distributed-training](../../ai-distributed-training/SKILL.md#mfu-and-hfu).

**Time for 10B tokens (8.55e18 FLOP, PaLM-style)** = FLOP / (GPUs × dense peak × MFU): 8×A100 at 40% ≈ 2.4 h; 8×A100 at 60% ≈ 1.6 h; 8×H100 at 40% ≈ 0.75 h (peaks 312 and 989 TFLOP/s dense BF16). For comparison, llm.c reported "Reproducing GPT-2 (124M) in llm.c in 90 minutes for $20" at up to about 60% MFU on one 8×A100 node, consistent with the 1.6 h row.

**Warmup:** nanoGPT's `warmup_iters = 715` at 524,288 tokens/step is ≈375M tokens, GPT-3's absolute warmup. It is 3.75% of a 10B-token run (19,073 steps) but 0.125% of GPT-3's 300B-token run, so state warmup in tokens or steps, never as a percentage of the run.

**Activation recompute:** full recompute adds one forward pass, 8N instead of 6N FLOPs per token (+33%). It counts toward HFU, not MFU.

## Loop Anatomy

```python
model = GPT(config).to(device)
optimizer = model.configure_optimizers(weight_decay=0.1, lr=6e-4, betas=(0.9, 0.95))

for step in range(max_steps):
    optimizer.zero_grad(set_to_none=True)  # already the default in current PyTorch

    # Gradient accumulation micro-steps
    loss_accum = torch.zeros((), device=device)
    for micro_step in range(grad_accum_steps):
        x, y = get_batch('train')
        if ddp:
            # DDP resets this to True inside every forward() — re-assign each micro-step,
            # before the forward, so the guard covers forward AND backward.
            model.require_backward_grad_sync = (micro_step == grad_accum_steps - 1)
        with torch.autocast(device_type='cuda', dtype=torch.bfloat16):
            logits, loss = model(x, y)
        loss = loss / grad_accum_steps  # normalize
        loss_accum += loss.detach()     # .detach(), not .item() — .item() forces a GPU sync
        loss.backward()  # accumulates into .grad

    if ddp:
        # loss_accum is per-rank; average it before logging or you print one rank's view.
        dist.all_reduce(loss_accum, op=dist.ReduceOp.AVG)

    # Gradient clipping
    norm = torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)

    # LR schedule
    lr = get_lr(step)
    for param_group in optimizer.param_groups:
        param_group['lr'] = lr

    optimizer.step()

    if step % eval_interval == 0:
        val_loss = estimate_loss(model, 'val')  # see below — no periodic eval means
        # a shard-repeat or overfit can hide behind a healthy-looking train curve
```

Held-out eval — the loop above is not complete without it (the checkpoint dict below stores
`val_loss`, which nothing else computes):

```python
@torch.no_grad()
def estimate_loss(model, split, eval_iters=20):
    model.eval()
    losses = torch.zeros(eval_iters, device=device)
    for k in range(eval_iters):
        x, y = get_batch(split)
        with torch.autocast(device_type='cuda', dtype=torch.bfloat16):
            _, loss = model(x, y)
        losses[k] = loss.detach()
    model.train()
    return losses.mean()
```

## Mixed Precision

Use `torch.autocast` with `bfloat16` on Ampere+ GPUs (A100, 3090, 4090):

```python
with torch.autocast(device_type='cuda', dtype=torch.bfloat16):
    logits, loss = model(x, y)
```

- `bfloat16`: same exponent range as float32, lower mantissa precision. Stable without loss scaling.
- `float16`: narrower exponent range — requires `GradScaler` to prevent NaN/inf in gradients.
- Prefer `bfloat16` when hardware supports it; fall back to `float16` + `GradScaler` on older GPUs (V100, T4).
- The autocast context wraps the forward pass only; backward accumulates in float32.

## Gradient Accumulation

Purpose: simulate a large batch size across multiple small micro-batches to fit GPU memory.

```python
# Effective batch = batch_size * seq_len * grad_accum_steps * num_gpus
# GPT-3 used ~0.5M tokens per step
# nanoGPT target: total_batch_size = 524288 tokens
# Example (1 GPU): batch_size=16, seq_len=1024, grad_accum_steps=32 -> 16*1024*32 = 524288

assert total_batch_size % (batch_size * seq_len * ddp_world_size) == 0
grad_accum_steps = total_batch_size // (batch_size * seq_len * ddp_world_size)
```

The divisor must include `ddp_world_size`: under DDP every rank contributes to a single optimizer step. Omitting it on 8 GPUs gives an effective batch 8× the intended one, with a peak LR tuned for the smaller batch — a silent scaling error. nanoGPT does the equivalent (`gradient_accumulation_steps //= ddp_world_size`) and carries the assert; without the assert the off-by-N goes unnoticed.

Critical: divide `loss` by `grad_accum_steps` inside the micro-batch loop. Failing to do this means each micro-batch contributes at full scale and the effective gradient is `grad_accum_steps` times too large.

Equal-token caveat: dividing by N gives a mean-of-means, which equals the true batch mean **only when every micro-batch contains the same number of loss-contributing tokens**. True for fixed `(B, T)` packed pretraining batches. With padding or variable-length sequences (an SFT loop, for example), accumulate the token count and normalize by the total, not by N.

### DDP gradient sync

Wrap the model with `torch.nn.parallel.DistributedDataParallel`, then suppress the all-reduce on every micro-step except the last — otherwise you pay `grad_accum_steps`× the communication for the same gradient.

`model.require_backward_grad_sync` is **one-shot**: DDP's reducer resets it to `True` inside every `forward()`. Setting it once before the micro-loop does nothing after the first iteration. Re-assign it per micro-step, keyed on the index, before that micro-step's forward (as in the loop above):

```python
model.require_backward_grad_sync = (micro_step == grad_accum_steps - 1)
```

`model.no_sync()` is the supported public API and the equivalent; `require_backward_grad_sync` is the private-but-conventional nanoGPT shortcut. Either way the guard must enclose the **forward as well as the backward**:

```python
ctx = model.no_sync() if micro_step < grad_accum_steps - 1 else contextlib.nullcontext()
with ctx:
    with torch.autocast(device_type='cuda', dtype=torch.bfloat16):
        logits, loss = model(x, y)
    (loss / grad_accum_steps).backward()
```

Both failure modes here are silent at small scale: sync-every-step is a throughput regression with correct gradients; never-restoring-sync means each rank steps on its own local gradient and the run silently stops being data-parallel.

`loss_accum` is per-rank. All-reduce it (`op=ReduceOp.AVG`) before logging, or the printed loss is one rank's view.

## Cosine LR with Warmup

GPT-2/GPT-3 training schedule:

```python
def get_lr(it):
    # Linear warmup for warmup_iters steps
    if it < warmup_iters:
        return max_lr * (it + 1) / warmup_iters
    # After max_iters: minimum LR
    if it > max_iters:
        return min_lr
    # Cosine decay between warmup and max
    decay_ratio = (it - warmup_iters) / (max_iters - warmup_iters)
    coeff = 0.5 * (1.0 + math.cos(math.pi * decay_ratio))
    return min_lr + coeff * (max_lr - min_lr)
```

Typical values for GPT-2 (124M) reproduction:

- `max_lr = 6e-4`, `min_lr = 6e-5` (10% of peak)
- `warmup_iters = 715` (≈375M tokens at 524,288 tokens/step: GPT-3's absolute warmup; see the reference card)
- AdamW `betas=(0.9, 0.95)`, `eps=1e-8`, `weight_decay=0.1` (GPT-3's settings, used by nanoGPT; the GPT-2 paper does not report betas)

AdamW weight decay: apply only to 2D+ tensors (weight matrices), not to biases or LayerNorm parameters. Configure two parameter groups:

```python
decay_params = [p for p in params if p.dim() >= 2]
nodecay_params = [p for p in params if p.dim() < 2]
```

The GPT-3-derived warmup is a conservative default, not a law: shorter warmups often work. Carry it over in tokens or steps; as a percentage of the run it means something different at every run length.

## WSD / Trapezoidal Schedule

Cosine requires committing to `max_iters` up front. WSD (warmup–stable–decay, a.k.a. trapezoidal) does not: warm up, hold a constant plateau, then decay over the final ~10–20% of whatever budget you end up with.

```python
def get_lr_wsd(it, total_iters, warmup_iters, decay_frac=0.1):
    if it < warmup_iters:
        return max_lr * (it + 1) / warmup_iters
    decay_start = total_iters - int(decay_frac * total_iters)
    if it < decay_start:
        return max_lr                                    # stable plateau
    r = (it - decay_start) / max(1, total_iters - decay_start)
    return min_lr + (1 - r) * (max_lr - min_lr)          # linear decay (1-sqrt also used)
```

Decision rule: **cosine** when the token budget is fixed and known — it remains the GPT-2/GPT-3 reproduction default and is what the hyperparameters above are tuned for. **WSD** when you may extend the run, want annealed intermediate checkpoints, or want to branch data-mixture experiments off one plateau. Consistent with [ai-scaling-laws](../../ai-scaling-laws/SKILL.md) ("cosine decay or trapezoidal schedule over D tokens") and with the Kimi K2 recipe recorded in [ai-distributed-training](../../ai-distributed-training/SKILL.md) (MuonClip + WSD).

## Annealing: Data Probe and Mid-Training Stage

The decay phase of WSD (or a short re-decay from an intermediate checkpoint) is where the LR falls and the loss drops fastest, so the data seen there carries extra weight. Two uses:

- **Data probe.** Branch a plateau checkpoint, run the same short decay twice — once on the base mixture, once with a candidate dataset upweighted — and compare held-out loss and target probes. The difference is a cheap estimate of that dataset's value; it is a relative signal for ranking candidates, not a prediction of full-run gains. Keep the decay length, LR floor, and token count identical across arms.
- **Mid-training stage.** Put the highest-quality and task-shaped data (curated code, math, long-context, instruction-like text) into the final decay. Decontaminate this slice with extra care: benchmarks leaking into the anneal inflate scores the most.

Hold out a probe set that the anneal data never touches, and compare against a base-mixture anneal of equal length, not against the pre-decay checkpoint.

## Throughput: TF32, Vocab Padding, MFU

Three cheap wins that a from-scratch loop usually leaves on the floor:

- **TF32 matmuls.** `torch.set_float32_matmul_precision('high')` lets fp32 matmuls run on TensorFloat-32 tensor cores on Ampere+. Karpathy's GPT-2 video treats it as the *first* optimization to apply; it is one line and needs no other change. Verify the speedup on your own hardware.
- **Pad the vocab to a multiple of 128.** GPT-2's `vocab_size = 50257` is a bad number for tensor-core tiling; setting `vocab_size = 50304` (50257 rounded up to a multiple of 128) adds unused rows that the model learns to never predict, and buys a few percent throughput for free. Measure on your setup.
- **MFU (model FLOP utilization)** is the throughput metric to track, not tokens/sec alone. Count FLOPs per token PaLM-style, `6·N_matmul + 12·L·d·T` (6N alone skips attention and, with non-embedding N, the LM head: at 124M that undercounts by 1.68×; see the reference card), multiply by tokens per step, divide by step wall-clock, then by the GPU's peak dense FLOP/s for your dtype. Definitions and the MFU/HFU split: [ai-distributed-training](../../ai-distributed-training/SKILL.md#mfu-and-hfu). Without MFU you have no way to tell whether the loop is leaving 3× on the table — the usual outcome of a from-scratch reproduction. Also check you are not CPU-bound in `get_batch` before blaming the model.

## Gradient Clipping

```python
norm = torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
```

Clip global gradient norm to 1.0 before the optimizer step. This caps the update magnitude when the loss landscape has sharp curvature (common early in training and at LR peaks).

Log `norm` every step: a consistently high norm (>1.0) suggests the model is struggling; a sudden spike often indicates a bad batch.

Wire a watchdog on loss and gradient norm: when either spikes far above its running level, pause, inspect the batch window, and resume from the last good checkpoint rather than training through it.

## Loss-Spike Protocol

A working protocol assembled from common practice, not a validated standard; tune the thresholds to your run.

1. **Log the precursors every step:** loss, global grad norm, max attention logit (pre-softmax) per layer, max output logit, and the update-to-weight norm ratio per parameter group. Spikes are usually preceded by attention-logit growth or a jump in the update/weight ratio.
2. **Prevent:** QK-norm (or logit capping) bounds attention-logit growth; a small z-loss on the output softmax normalizer keeps output logits from drifting; warmup and gradient clipping stay on.
3. **Respond by severity:** a single isolated spike that recovers within a few steps → note it and continue. A spike that repeats or does not recover → skip the offending batch window and resume from the last good checkpoint, with the data position advanced past it. Repeated spikes after skipping → lower the peak LR or add the missing stabilizer, and re-run from an earlier checkpoint.
4. **Record** each spike (step, batch shard, which precursor moved first). A spike that reproduces on the same data points at the data; one that moves with the seed points at the optimizer or architecture.

## Checkpointing

```python
checkpoint = {
    'model': model.state_dict(),
    'optimizer': optimizer.state_dict(),
    'config': asdict(config),   # plain dict — see note below
    'step': step,
    'data_pos': loader.position,  # shard index + offset, so the data stream resumes too
    'val_loss': val_loss,
}
torch.save(checkpoint, f'ckpt_{step:05d}.pt')

# Resume — weights_only=True prevents arbitrary code execution via pickle
ckpt = torch.load('ckpt_05000.pt', weights_only=True)
model.load_state_dict(ckpt['model'])
optimizer.load_state_dict(ckpt['optimizer'])
step = ckpt['step']
loader.seek(ckpt['data_pos'])
```

- **Resume the data position, not just the weights.** Restoring `model` and `optimizer` but restarting the loader at shard 0 silently re-trains on data the model has already seen. Nothing errors; the loss curve looks fine. Store the shard index and within-shard offset in the checkpoint and seek on resume.
- **`weights_only=True` and `config`.** The flag is right and should stay, but it will *raise* on load if `config` is a dataclass or custom object — only plain types round-trip unless the class is registered via `torch.serialization.add_safe_globals`. Store the config as a plain dict.
- **`torch.compile` changes state_dict keys.** A compiled model's parameters are prefixed `_orig_mod.`; save from (or strip back to) the uncompiled module, or loading into an uncompiled model fails on every key.

Gradient checkpointing (activation checkpointing) — trades compute for memory by recomputing activations during backward instead of storing them:

```python
from torch.utils.checkpoint import checkpoint
# Wrap each block's forward in checkpoint(): the backward recomputes one extra forward,
# so ~33% more FLOPs (8N vs 6N per token; it shows in HFU, not MFU), and stored activations drop from every layer's
# intermediates to roughly one block's worth plus the saved block boundaries.
```

The classic O(√n) activation-memory result is the bound for *optimally placed* checkpoints, not for wrapping every block — don't quote it for per-block wrapping. Modern practice is **selective / op-level checkpointing** (`torch.utils.checkpoint` with an SAC policy, or `checkpoint_wrapper`): recompute the cheap ops, keep the expensive matmuls stored. It dominates all-or-nothing per-block wrapping. Multi-GPU specifics stay with [ai-distributed-training](../../ai-distributed-training/SKILL.md).

## Baseline Loss Check

Before training more than ~100 steps, verify the initial loss matches theory:

- For `vocab_size=50257` (GPT-2 tokenizer): expected initial loss ≈ `ln(50257) ≈ 10.82`
- For a character-level model with 65 chars: ≈ `ln(65) ≈ 4.17`

If step-0 loss is far from this baseline, likely causes:

- Weight initialization is wrong (check init scaling)
- LM head weights are not tied to embeddings
- Loss function is computing something unexpected (shape mismatch)

## Eval During Pretraining

Training loss alone does not show what the model is learning. At a fixed checkpoint cadence, log:

- **Validation loss / perplexity per domain slice** (code, math, prose, each language), so one slice regressing is not hidden by the average.
- **Small probe tasks** for the capabilities the run is meant to build.
- **A long-context stress set** if the run targets long context (see [Architecture Limitations and Workarounds](architecture-limitations-and-workarounds.md)).

Stop and investigate when training loss keeps falling or flattens while probes or a slice regress. Keep probe sets out of the training corpus; decontamination belongs to `ai-data-curation-pretraining`, benchmark design to `ai-evals`.

## Common Mistakes

- **Not zeroing gradients**: call `optimizer.zero_grad()` at the start of each outer step (not after `.step()`). `set_to_none=True` is faster and is already the default in current PyTorch — pass it explicitly only for clarity.
- **Setting `require_backward_grad_sync` once, outside the micro-loop**: DDP resets it on every forward, so it must be re-assigned per micro-step (or use `model.no_sync()`).
- **Resuming weights without resuming the data position**: silently re-trains on the same shard.
- **Dividing loss outside the micro-step loop**: the division by `grad_accum_steps` must happen inside the loop, per micro-batch.
- **Using default Adam betas**: GPT-3 (and nanoGPT, following it) used `betas=(0.9, 0.95)`, not PyTorch's default `(0.9, 0.999)`; the GPT-2 paper does not report betas.
- **Skipping LR warmup**: the loss will spike at the start without warmup, especially with large LRs.
- **Checkpoint includes stale optimizer state**: when resuming, restore both `model` and `optimizer` state, and set the LR scheduler to the correct step.
- **`torch.compile` on PyTorch < 2.0**: `torch.compile` requires PyTorch 2.0+. On eligible hardware it often gives a large throughput gain via kernel fusion; measure it on your model rather than assuming a multiple.
