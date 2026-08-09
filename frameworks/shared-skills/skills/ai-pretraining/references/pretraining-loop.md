# Pretraining Loop

Reference for the GPT pretraining training loop, covering mixed precision, gradient accumulation, learning rate scheduling, and checkpointing.

## Table of Contents

- [Canonical Sources](#canonical-sources)
- [Loop Anatomy](#loop-anatomy)
- [Mixed Precision](#mixed-precision)
- [Gradient Accumulation](#gradient-accumulation)
- [Cosine LR with Warmup](#cosine-lr-with-warmup)
- [Gradient Clipping](#gradient-clipping)
- [Checkpointing](#checkpointing)
- [Baseline Loss Check](#baseline-loss-check)
- [Common Mistakes](#common-mistakes)

## Canonical Sources

- Karpathy "Let's reproduce GPT-2 (124M)" — [youtube.com/watch?v=l8pRSuU81PU](https://www.youtube.com/watch?v=l8pRSuU81PU)
- nanoGPT `train.py` — [github.com/karpathy/nanoGPT](https://github.com/karpathy/nanoGPT/blob/master/train.py)
- PyTorch AMP docs — [pytorch.org/docs/stable/amp.html](https://pytorch.org/docs/stable/amp.html)
- GPT-3 paper (Brown et al. 2020) for hyperparameter reference — [arxiv.org/abs/2005.14165](https://arxiv.org/abs/2005.14165)

## Loop Anatomy

```python
model = GPT(config).to(device)
optimizer = model.configure_optimizers(weight_decay=0.1, lr=6e-4, betas=(0.9, 0.95))

for step in range(max_steps):
    optimizer.zero_grad()

    # Gradient accumulation micro-steps
    loss_accum = 0.0
    for micro_step in range(grad_accum_steps):
        x, y = get_batch('train')
        with torch.autocast(device_type='cuda', dtype=torch.bfloat16):
            logits, loss = model(x, y)
        loss = loss / grad_accum_steps  # normalize
        loss_accum += loss.detach()
        loss.backward()  # accumulates into .grad

    # Gradient clipping
    norm = torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)

    # LR schedule
    lr = get_lr(step)
    for param_group in optimizer.param_groups:
        param_group['lr'] = lr

    optimizer.step()
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
# Example: batch_size=16, seq_len=1024, grad_accum_steps=32 -> 16*1024*32 = 524288

grad_accum_steps = total_batch_size // (batch_size * seq_len)
```

Critical: divide `loss` by `grad_accum_steps` inside the micro-batch loop. Failing to do this means each micro-batch contributes at full scale and the effective gradient is `grad_accum_steps` times too large.

When using DDP (multi-GPU): wrap the model with `torch.nn.parallel.DistributedDataParallel`. Use `model.require_backward_grad_sync = False` for all but the last micro-step to suppress gradient all-reduce on every backward pass — only sync on the final step.

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
- `warmup_iters = 715` (~1% of 19073 total steps for FineWeb-Edu)
- Adam `betas=(0.9, 0.95)`, `eps=1e-8`, `weight_decay=0.1`

AdamW weight decay: apply only to 2D+ tensors (weight matrices), not to biases or LayerNorm parameters. Configure two parameter groups:

```python
decay_params = [p for p in params if p.dim() >= 2]
nodecay_params = [p for p in params if p.dim() < 2]
```

## Gradient Clipping

```python
norm = torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
```

Clip global gradient norm to 1.0 before the optimizer step. This caps the update magnitude when the loss landscape has sharp curvature (common early in training and at LR peaks).

Log `norm` every step: a consistently high norm (>1.0) suggests the model is struggling; a sudden spike often indicates a bad batch.

## Checkpointing

```python
checkpoint = {
    'model': model.state_dict(),
    'optimizer': optimizer.state_dict(),
    'config': config,
    'step': step,
    'val_loss': val_loss,
}
torch.save(checkpoint, f'ckpt_{step:05d}.pt')

# Resume — weights_only=True prevents arbitrary code execution via pickle
ckpt = torch.load('ckpt_05000.pt', weights_only=True)
model.load_state_dict(ckpt['model'])
optimizer.load_state_dict(ckpt['optimizer'])
step = ckpt['step']
```

Gradient checkpointing (activation checkpointing) — trades compute for memory by recomputing activations during backward instead of storing them:

```python
from torch.utils.checkpoint import checkpoint
# Wrap each block's forward in checkpoint() to halve activation memory
# Adds ~30% compute overhead; worthwhile when memory is the bottleneck
```

## Baseline Loss Check

Before training more than ~100 steps, verify the initial loss matches theory:

- For `vocab_size=50257` (GPT-2 tokenizer): expected initial loss ≈ `ln(50257) ≈ 10.82`
- For a character-level model with 65 chars: ≈ `ln(65) ≈ 4.17`

If step-0 loss is far from this baseline, likely causes:

- Weight initialization is wrong (check init scaling)
- LM head weights are not tied to embeddings
- Loss function is computing something unexpected (shape mismatch)

## Common Mistakes

- **Not zeroing gradients**: call `optimizer.zero_grad()` at the start of each outer step (not after `.step()`). Setting `set_to_none=True` is faster.
- **Dividing loss outside the micro-step loop**: the division by `grad_accum_steps` must happen inside the loop, per micro-batch.
- **Using default Adam betas**: GPT-2/3 used `betas=(0.9, 0.95)`, not PyTorch's default `(0.9, 0.999)`.
- **Skipping LR warmup**: the loss will spike at the start without warmup, especially with large LRs.
- **Checkpoint includes stale optimizer state**: when resuming, restore both `model` and `optimizer` state, and set the LR scheduler to the correct step.
- **`torch.compile` on PyTorch < 2.0**: `torch.compile` requires PyTorch 2.0+. On eligible hardware, it can give 2-3x throughput improvement via kernel fusion.
