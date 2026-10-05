# Chaos Engineering & Resilience Testing

Chaos engineering, fault injection, game days and resilience tooling moved to **qa-resilience**, which owns them. Start at [qa-resilience/SKILL.md](../../qa-resilience/SKILL.md), then [chaos-engineering-guide.md](../../qa-resilience/references/chaos-engineering-guide.md) (method, blast radius, steady state) and [chaos-tooling-recipes.md](../../qa-resilience/references/chaos-tooling-recipes.md) (LitmusChaos, Chaos Mesh, Gremlin, CI integration).

Strategy-level rules that stay here:

- Rank fault-injection scenarios by minimal-cut-set rate (λ × MTTR, see [reliability-theory-applied.md](reliability-theory-applied.md#corrected-formulas-layered-detection-and-minimal-cut-sets)), not by what the tool makes easy to inject.
- Chaos runs are evidence only when they record hypothesis, steady-state metric, blast radius, result and owner. For regulated resilience-testing duties (for example the EU DORA testing programme, Art. 24–26, and threat-led penetration testing for in-scope entities), route the obligation question to qualified counsel; do not treat a chaos report as proof of compliance.
