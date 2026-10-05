# Online Evaluation: Operational Wiring

Online-evaluation method (A/B design and statistics, shadow and canary analysis, human review sampling, online judges, drift of quality) lives in [ai-evals online-production-eval](../../ai-evals/references/online-production-eval.md), with comparison statistics in [ai-evals eval-statistics](../../ai-evals/references/eval-statistics.md). Judge calibration and threshold choice live in ai-evals. This file keeps what the platform owns: wiring the gate into CI/CD, blocking, rollback, and logging.

## Contents

- [Who Owns What](#who-owns-what)
- [Eval Gate In CI/CD](#eval-gate-in-cicd)
- [Rollout And Rollback Wiring](#rollout-and-rollback-wiring)
- [Feedback Logging](#feedback-logging)
- [Checklist](#checklist)

## Who Owns What

| Need | Owner |
|------|-------|
| A/B design, sample size, peeking, interleaving, guardrail metrics | [online-production-eval](../../ai-evals/references/online-production-eval.md#ab-tests-with-guardrails) |
| Shadow and canary analysis, sticky routing, concurrent control | [online-production-eval](../../ai-evals/references/online-production-eval.md#shadow-and-canary-traffic) |
| Production judge pipeline: sampling rate, judge choice, cost per judged request | [online-production-eval](../../ai-evals/references/online-production-eval.md#online-judges-and-sampling) |
| Human review sampling and feedback signals | [online-production-eval](../../ai-evals/references/online-production-eval.md#human-in-the-loop-feedback) |
| Gate thresholds and judge calibration | [ai-evals threshold-derivation](../../ai-evals/references/threshold-derivation.md) |
| Champion/challenger on the same window, paired interval | [automated-retraining-patterns](automated-retraining-patterns.md#pattern-4-championchallenger-validation-gates) |
| Retraining triggers and cadence | [automated-retraining-patterns](automated-retraining-patterns.md) |
| Preference data from feedback | [ai-post-training](../../ai-post-training/SKILL.md) |

## Eval Gate In CI/CD

- Run the versioned regression suite on every model, prompt, retrieval-index or provider change, against the current champion **in the same run** (same cases, same judge), and block the deploy when the gate fails. Thresholds and the paired comparison come from ai-evals; the pipeline enforces them.
- Record with every run: suite version, judge model and rubric version, candidate and champion identifiers, per-case scores. A score without those is not auditable and cannot be re-compared later.
- Re-run the suite on a schedule after go-live, not only on deploys: a hosted model can change behind the same name.
- Every production failure, incident, or new edge case becomes a suite case before its fix ships.

## Rollout And Rollback Wiring

- Stages: shadow (no user exposure) → canary (small, sticky slice) → ramp → full. Each stage has abort criteria written before it starts, and the abort is automated.
- **On a production quality regression, roll back first and diagnose second**: revert to the last version that passed the gate (prompt, model, index or provider), keep the previous path warm until the new one has held for a full traffic cycle, then add the failing cases to the regression suite.
- Promotion and rollback move registry aliases, not stages; keep the previous champion's version in a tag or CI artifact because aliases do not stack. See [model-registry-patterns](model-registry-patterns.md).

## Feedback Logging

- Log request ID, model and prompt version, the prediction, and later the outcome, so any online metric can be recomputed per version and slice.
- Hash user identifiers and redact personal data before logging; set retention for raw logs. Governance: [governance-checklists](governance-checklists.md).

## Checklist

- [ ] Eval gate runs on every model, prompt, index and provider change, against the champion in the same run
- [ ] Suite, judge and rubric versions logged with every result
- [ ] Scheduled post-launch re-runs catch provider-side changes
- [ ] Shadow → canary → ramp with automated, pre-written abort criteria
- [ ] Rollback first on a production regression; failing cases added to the suite
- [ ] Feedback logged with version identifiers; personal data hashed or redacted
