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

Rented GPU infrastructure (RunPod, Lambda Labs, Vast.ai, Modal, CoreWeave) enables LLM pre-training without owned hardware. Cost discipline is a first-class concern: a forgotten idle 8-GPU H100-class node bills 8 GPU-hours every wall-clock hour whether or not it trains.

Rule: **debug on the smallest GPU that fits; scale only when the run is validated**.

## Cost Estimation Formula

```
cost ≈ $/GPU-hr × num_GPUs × training_hours
```

Add measured setup, checkpoint stall, expected retry time, and a contingency chosen for the run. Async checkpointing may overlap writing with training; count the measured stall rather than treating all upload time as idle GPU time.

Example: 8×A100 × 12 hours = **96 GPU-hours** before measured overhead; multiply by the provider's current quoted $/GPU-hr.

Training hours estimate:
```
training_hours ≈ (num_tokens × model_flops_per_token) / (num_gpus × peak_flop_per_s × mfu × 3600)
```
`model_flops_per_token` is about 6N (add the attention term for long context; see [MFU and HFU](../SKILL.md#mfu-and-hfu)). Estimate `mfu` from a measured run; take `peak_flop_per_s` from the vendor datasheet for the GPU you rent (dense, not sparse). The worked table below uses historical dense-bf16 datasheet peaks of A100 312 TFLOP/s and H100 989 TFLOP/s.

**Sanity check.** Solve the formula for MFU from any quoted run time. Check unusually high results against the precision and FLOP definition; above 100% against the correct dense peak is impossible.

## Provider Comparison

For each candidate provider, check the live GPU catalog and topology, availability, interruption terms, billing unit, storage and egress charges, and the current quoted rate. The links under Canonical Sources are starting points; confirm the terms for the exact region and instance before provisioning.

## Spot / Interruptible Instances

Spot or interruptible capacity may cost less than on-demand and may end with little or no warning. Check the provider's current termination notice and signal behavior. Plan around completed durable checkpoints rather than an emergency checkpoint that may not finish.

**Strategies**:
- Choose an interval from measured checkpoint stall, durable-copy time, and observed interruption risk; see [Failure Budget and Checkpoint Interval](failure-budget-and-checkpointing.md).
- Publish a checkpoint only after DCP's save future and the durable copy succeed, then test restore. A local-only checkpoint can disappear with the instance.
- Treat a termination signal as an opportunity to finish an in-flight save only if the provider's grace period permits. A handler must not exit successfully while the save or upload is incomplete.

## Checkpoint Strategy for Spot Instances

1. **Save to durable storage**: after DCP completes on shared storage, use `rclone`, `aws-cli`, or a provider-native SDK to copy the whole checkpoint, or configure a supported DCP object-store writer. Check current storage and egress fees.
2. **Checkpoint frequency**: derive the interval from the run's interruption rate and measured stalled save plus durable-copy time.
3. **Checkpoint naming**: include the step number and retain at least one prior restorable checkpoint so a failed new save has a fallback.
4. **Test restore before the long run**: always do a checkpoint → terminate → restore → continue cycle on a short test run before committing to hours of training.
5. **Resume logic**: training script should accept `--resume-from-checkpoint` and correctly restore optimizer state, LR scheduler state, and RNG state.

## Reference Run Cost Estimates

Hours from the formula above at **40% MFU** with the historical dense-bf16 peaks (reproduce with `ai-scaling-laws/scripts/training_math.py hours`). Cost = GPU-hours × the rate you look up today.

| Run | GPUs | 6·N·D (FLOP) | Hours at 40% MFU | GPU-hours |
|-----|------|--------------|------------------|-----------|
| GPT-2 124M, 10B tokens | 4–8 GPUs | see card | see the [GPT-2 124M Reference Card](../../ai-pretraining/references/pretraining-loop.md#gpt-2-124m-reference-card) | — |
| 1B model, 100B tokens | 8×A100 | 6.0e20 | ~167 h | ~1,340 |
| 7B model, 100B tokens | 8×A100 | 4.2e21 | ~1,170 h | ~9,350 |
| 7B model, 1T tokens | 64×H100 | 4.2e22 | ~461 h | ~29,500 |

Add overhead for checkpointing, debugging and restarts. A quoted run time far below these rows implies an MFU the hardware cannot reach.

## Cost Discipline Checklist

- [ ] Debug on the smallest GPU that fits (A10G or L4 before A100/H100).
- [ ] Estimate training hours using the formula before provisioning.
- [ ] Set a billing alert with headroom for the measured checkpoint and shutdown time.
- [ ] Enable spot/interruptible only when the expected lost work fits the run's budget.
- [ ] Verify a completed checkpoint exists in durable storage.
- [ ] Test checkpoint restore before starting the long run.
- [ ] Confirm the provider's termination notice and test the shutdown path.
- [ ] Profile utilization and exposed bottlenecks before scaling to more GPUs.
- [ ] Stop the instance immediately when training completes.
- [ ] Confirm billing stopped after termination (check provider dashboard).

## Canonical Sources

- RunPod pricing: https://www.runpod.io/gpu-instance/pricing
- Lambda Labs pricing: https://lambdalabs.com/service/gpu-cloud#pricing
- Modal pricing: https://modal.com/pricing
- Vast.ai marketplace: https://vast.ai/pricing
- rclone for checkpoint sync: https://rclone.org/
