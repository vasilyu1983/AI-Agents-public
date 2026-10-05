# software-architecture-design — Learnings

## Patterns That Work

## Mistakes to Avoid

- [2026-07-11] Worked-arithmetic examples in applied-theory toolkits (queueing-theory-applied.md, reliability-theory-applied.md) had drifted: an Erlang-C probability transcribed as 0.23 instead of 0.023, a Kingman Wq off by 2x (53ms vs. the correct ~106ms), a per-component Kingman Wq/W pair computed at half its correct value (masking a budget overrun), and two availability-rollup downtime conversions (16h and 15.6h) that didn't match their own stated percentages (correct: ~18.4h and ~14.0h respectively). None of these were caught by a read-through — only re-deriving each number by hand surfaced them. Treat worked arithmetic in this skill as needing independent re-derivation on every audit, not just a plausibility skim.

## Domain Knowledge

- [2026-07-11] As of July 2026: AWS App Mesh's end-of-support date of September 30, 2026 is confirmed current (AWS retired new-customer onboarding in Sept 2024; migration target is Amazon ECS Service Connect or VPC Lattice — 2026-09-23: the EoS notice links the ECS Service Connect guide; AWS also publishes VPC Lattice migration guides for EKS and ECS). adr.github.io is actively maintained (tooling page updated July 7, 2026) and is a good live source for current ADR tooling. The Prime Video "monolith saved 90%" case study (Prime Video Tech blog, 2023-03-22; corrected 2026-09-23 from "AWS Compute Blog"; main bottleneck was Step Functions state-transition account limits, S3 calls secondary) is real but scoped to one audio/video monitoring service, not a company-wide reversal — cite it with that caveat to avoid overgeneralizing "microservices are bad."

## Open Questions

## Consolidated Principles
