# Rented GPU Cost Guide

## Table of Contents

- [Overview](#overview)
- [Cost Estimation Formula](#cost-estimation-formula)
- [Provider Comparison](#provider-comparison)
- [Spot / Interruptible Instances](#spot--interruptible-instances)
- [Checkpoint Strategy for Spot Instances](#checkpoint-strategy-for-spot-instances)
- [Reference Run Cost Estimates](#reference-run-cost-estimates)
- [Cost Discipline Checklist](#cost-discipline-checklist)
- [Canonical Sources](#canonical-sources)

## Overview

Rented GPU infrastructure (RunPod, Lambda Labs, Vast.ai, Modal, CoreWeave) enables LLM pre-training without owned hardware. Cost discipline is a first-class concern: a single forgotten idle H100 cluster at $4/GPU-hr × 8 GPUs = $32/hr can accumulate significant waste in hours.

Rule: **debug on the smallest GPU that fits; scale only when the run is validated**.

## Cost Estimation Formula

```
cost ≈ $/GPU-hr × num_GPUs × training_hours
```

Add overhead:
- 10-15% for profiling, setup, and debugging at scale
- 5-10% for checkpoint upload time (GPUs idle during large checkpoint saves)
- 20% buffer for unexpected re-runs

Example: 8×A100 80GB at $2.50/GPU-hr × 12 hours = **$240** + 20% buffer = **~$290**

Training hours estimate:
```
training_hours ≈ (num_tokens × model_flops_per_token) / (num_gpus × gpu_flops × mfu)
```
Where `mfu` (model FLOP utilization) is typically 30-50% for well-tuned runs. A10G: ~30 TFLOPS bf16; A100: ~312 TFLOPS bf16; H100: ~989 TFLOPS bf16.

## Provider Comparison

Prices shown are approximate mid-2026 rates. Always verify against current pricing pages before budgeting — prices change frequently and availability fluctuates.

| Provider | GPU Options | On-Demand $/hr (1x A100 80GB) | Spot Available | Notes |
|----------|-------------|-------------------------------|----------------|-------|
| RunPod | A10G, A100, H100, RTX 4090, B200 | ~$1.20-2.80 | Yes (interruptible) | Per-second billing; community + secure cloud |
| Lambda Labs | A100, H100, B200 | ~$1.79-2.49 (varies) | Limited | Reserved clusters; stable for long runs |
| Vast.ai | A100, RTX 4090, H100 | ~$1.00-2.50 | Market pricing | Cheapest option; quality varies by host |
| Modal | A100, H100, B200 | ~$3.00-4.00 | No (serverless) | Per-second; easiest setup; no idle billing |
| CoreWeave | A100, H100, GB200/Rubin NVL72 | Enterprise pricing | Yes | Reserved; best for multi-node/rack-scale clusters |

H100 SXM5 rates range roughly $2.00-4.30/GPU-hr on-demand across providers as of mid-2026 (marketplace rates like RunPod/Vast.ai trend toward the low end, reserved/enterprise clusters toward the high end); H100 PCIe is typically 20-30% cheaper. These numbers move often — re-check provider pricing pages, do not budget off this table alone. Rubin NVL72 capacity is new (production started ~June 2026) and is quote/reserve-only on most clouds; expect premium pricing until supply catches up.

## Spot / Interruptible Instances

Spot instances (called "interruptible" on RunPod, "spot" on CoreWeave) offer 30-70% discounts. The instance may be preempted with short notice (typically 30-90 seconds warning).

**Strategies**:
- Enable spot only if your checkpoint interval is short enough to lose at most N steps of work.
- Default checkpoint interval for spot: every 500-1000 steps or every 30-60 minutes.
- Store checkpoints to object storage immediately (not local disk) — local disk is lost on preemption.
- Implement a signal handler to checkpoint on SIGTERM (preemption warning).

```python
import signal, sys

def checkpoint_on_sigterm(signum, frame):
    save_checkpoint(model, optimizer, step, path="s3://bucket/checkpoint_emergency.pt")
    sys.exit(0)

signal.signal(signal.SIGTERM, checkpoint_on_sigterm)
```

## Checkpoint Strategy for Spot Instances

1. **Save to object storage**: use `rclone`, `aws-cli`, or provider-native SDK. S3-compatible storage (Cloudflare R2, Backblaze B2) typically costs $0.01-0.015/GB/month — cheap for model checkpoints.
2. **Checkpoint frequency**: every N steps where N is tuned so checkpoint upload takes <5% of training time.
3. **Checkpoint naming**: include step number and timestamp in the filename. Keep last 2-3 checkpoints to allow rollback.
4. **Test restore before the long run**: always do a checkpoint → terminate → restore → continue cycle on a short test run before committing to hours of training.
5. **Resume logic**: training script should accept `--resume-from-checkpoint` and correctly restore optimizer state, LR scheduler state, and RNG state.

## Reference Run Cost Estimates

| Run | GPUs | Hours | Provider | Est. Cost |
|-----|------|-------|----------|-----------|
| GPT-2 124M debug (single GPU) | 1×A10G | 2-4 h | RunPod spot | $0.50-2 |
| GPT-2 124M smoke test (4 GPU) | 4×A100 | 1-2 h | RunPod spot | $4-12 |
| GPT-2 124M full reproduction | 4×A100 | 8-12 h | RunPod spot | $50-150 |
| GPT-2 124M speed run (H100) | 8×H100 | 1-2 h | RunPod spot | $40-80 |
| 1B model (100B tokens) | 8×A100 | ~40 h | Lambda | ~$800 |
| 7B model (1T tokens) | 64×H100 | ~300 h | CoreWeave | ~$60,000+ |

These are rough estimates. Actual cost depends on MFU, checkpointing overhead, debugging time, and current provider pricing.

## Cost Discipline Checklist

- [ ] Debug on the smallest GPU that fits (A10G or L4 before A100/H100).
- [ ] Estimate training hours using the formula before provisioning.
- [ ] Set a billing alert at 80% of budget.
- [ ] Enable spot/interruptible if checkpoint interval is ≤30 min.
- [ ] Save checkpoint to object storage, not local disk.
- [ ] Test checkpoint restore before starting the long run.
- [ ] Add SIGTERM handler for graceful checkpoint on preemption.
- [ ] Verify MFU is above 30% before scaling to more GPUs.
- [ ] Stop the instance immediately when training completes.
- [ ] Confirm billing stopped after termination (check provider dashboard).

## Canonical Sources

- RunPod pricing: https://www.runpod.io/gpu-instance/pricing
- Lambda Labs pricing: https://lambdalabs.com/service/gpu-cloud#pricing
- Modal pricing: https://modal.com/pricing
- Vast.ai marketplace: https://vast.ai/pricing
- rclone for checkpoint sync: https://rclone.org/
