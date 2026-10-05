# ai-post-training — Learnings

## Patterns That Work

## Mistakes to Avoid

## Domain Knowledge

- [2026-07-11] As of mid-2026 GRPO is a family, not one fixed objective: DAPO is TRL's default GRPOTrainer loss_type, GSPO is a loss_type (not a separate trainer) [WRONG, see the 2026-09-25 correction below], and TRL also ships RLOOTrainer plus environment-owned rewards (Harbor/OpenEnv).
- [2026-09-25] Correction to the 2026-07-11 entry above: GSPO is **not** a `loss_type` in TRL; it is set with `importance_sampling_level="sequence"`, and `loss_type="gspo"` fails validation (see methods-and-pipeline.md, Routing to Depth). Also corrected: GSPO's paper omits the KL term "for brevity" (it does not set β=0); the original GRPO used β=0.04; TRL's PPO trainer was removed after being moved to `trl.experimental`.
## Open Questions

## Consolidated Principles

