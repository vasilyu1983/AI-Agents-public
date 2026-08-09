# Mechanism: Online Shapley-Driven Prompt Evolution (HiveMind)

## Problem

Mechanism #10 (AlphaEvolve / ShinkaEvolve) evolves coordination rules **offline** against a measured fitness signal. That works when:

- you have a stable benchmark to optimize against
- you can re-run the team many times before deploying changes

It does **not** work for live teams whose contribution-weighted prompts need to drift inside a single high-frequency workflow (support triage, ticket classification, monitoring response). For that case, evolution must be **online** — feedback per-run, not per-benchmark — and the fitness signal must be **per-member**, not team-aggregate, so weak members are tightened without disturbing strong ones.

## Solution — HiveMind-Style Loop

Use Shapley contribution (mechanism #4) as a per-member fitness signal, then mutate each member's prompt in proportion to its contribution gap.

```
Per-run loop:
  1. Run team with current prompts
  2. Compute Shapley contribution per member (DAG-Shapley for efficiency)
  3. For each member m:
       if shapley(m) < threshold:
         propose prompt mutation targeting m's failure pattern
         A/B test mutation against current prompt on next N runs
       else:
         lock prompt — don't perturb a working member
  4. Adopt mutations that improve member-level Shapley without dropping team output
```

The key constraint: mutations target **only the underperforming member's prompt**, not the team protocol. The team manifest, debate rule, and synthesis owner are stable.

## How It Differs From #10

| Axis | #10 AlphaEvolve | #17 HiveMind |
|---|---|---|
| Cadence | Offline, between deployments | Online, per-run |
| Search target | Team coordination rules (round count, debate trigger, synthesis protocol) | Individual member prompts |
| Fitness signal | Team-aggregate quality on a benchmark | Per-member Shapley delta |
| Perturbation scope | Whole-team protocol | One member at a time |
| Exit criterion | Plateau on benchmark | Member Shapley above threshold |
| Cost | High (many full team runs) | Amortized across normal runs |

Use #10 when redesigning a team. Use #17 when running an existing team.

## Operator Rules

- **Lock the team protocol.** Mutate prompts; don't mutate roles, debate rules, or synthesis order. Otherwise you're conflating two search axes.
- **A/B per member, not whole team.** Variant prompts on member m must run against current prompts on the same task or matched-pair tasks. Cross-team-run comparisons don't isolate member m's effect.
- **Shapley threshold is task-relative.** A member with 5% Shapley on a 5-member team is at parity. The trigger is *gap from expected share*, not absolute value.
- **Cap mutation rounds.** Three consecutive sub-threshold rounds → mutate. More than five mutation cycles without improvement → demote member, don't keep mutating.
- **Audit for drift toward sycophancy.** Online prompt evolution can quietly tune members toward agreeing with the synthesis owner (the loudest credit-receiving signal). Run an adversarial-debate spot-check (mechanism #2) every K runs to catch convergence-as-collapse.

## Failure Modes

- **Reward hacking the Shapley signal.** Members learn to claim credit for synthesis findings. Mitigation: synthesis owner attributes each finding to source member explicitly; no implicit credit.
- **Mutation cascade.** Mutating member m changes the contribution distribution, which then triggers mutation of member n, which triggers... Use a hysteresis band (don't mutate if Shapley moved within ±20% in last cycle).
- **Prompt drift away from interpretability.** Online-mutated prompts accumulate cruft. Periodically run a prompt-distillation pass (preserve behavior, drop dead instructions).

## Composes Well With

- [`04-shapley-contribution.md`](04-shapley-contribution.md) — the fitness signal
- [`05-reputation-gating.md`](05-reputation-gating.md) — long-term member retention decision
- [`02-adversarial-debate.md`](02-adversarial-debate.md) — periodic anti-sycophancy spot-check

## When to Skip

- Team runs fewer than ~50 times (insufficient signal for evolution)
- Member prompts are already heavily hand-tuned (mutations regress quality)
- Stakes per run are too high to A/B test (each run is a real decision; can't afford a worse variant)
- You're still designing the team — use #10 first, #17 after the team stabilizes

## Source

- HiveMind: Contribution-Guided Online Prompt Optimization of LLM Multi-Agent Systems. arXiv 2512.06432 (Dec 2025). [arxiv.org/abs/2512.06432](https://arxiv.org/abs/2512.06432)
- DAG-Shapley efficiency: ShapleyFlow [arxiv.org/abs/2502.00510](https://arxiv.org/abs/2502.00510), Shapley-Coop [openreview.net/pdf?id=HnJ1UkuJXS](https://openreview.net/pdf?id=HnJ1UkuJXS)
