---
description: Decision-theory rules for agent teams: an EVPI gate before adding a member, regret-based debate stopping, dominance tie-breaks, a hold verdict with a deadline, and weights locked before dispatch.
last_verified: 2026-09-24
status: stable
---

# Decision Theory Applied to Multi-Agent Teams

> **Gate before invoking:** Check [`foundations-decision-theory` § When to Apply](../../foundations-decision-theory/SKILL.md#when-to-apply) first. The recipes below assume the foundation is the right tool for the situation; the foundation's skip-conditions route you to a different foundation if not.

EVPI, minimax regret, stochastic dominance, real options, MCDA and bandits are explained in the [foundation's templates](../../foundations-decision-theory/assets/templates/decision-theory/). This file keeps the rules that decide when a team expands, stops, breaks a tie or waits.

## Decision rules

1. **Dispatch another member only if a plausible answer could flip the action.** List the actions on the table and the range of answers the member could return. If every plausible answer leaves the recommended action unchanged, EVPI ≈ 0: skip the member. If unsure, dispatch and log it as exploration. Cap additions per session (`expansion_gate.max_dynamic_members`).
2. **Stop debating when the worst remaining regret is small.** After each round, estimate for each open question the loss if it resolves worst-case against the lead candidate. Stop when the largest is below 20% of the decision's value for reversible decisions, or below 5% for irreversible ones (otherwise escalate to a human). Continue only on the highest-regret question. Consensus is not a stopping rule.
3. **Break ties by dominance, not preference.** If option A is at least as good as B in every plausible scenario, A wins whatever the risk appetite. If neither dominates, run one devil's-advocate round. When members score on different criteria, lock the MCDA weights before dispatch so no one tunes them after seeing results.
4. **Allow a `hold` verdict only with an unblocking signal and a deadline** (starting default 14 days). At the deadline, force go/no-go. Hold fits a cheap-to-reverse decision whose uncertainty resolves with time. A hold without a deadline is a stall.

For substitutable reviewers, UCB over a usefulness score (cited in synthesis, dissent registered, action adopted) keeps under-tested members in rotation. Never demote a member on fewer than 5 dispatches. Compute the score from your own run logs.

## Worked recipe — stop or continue a debate

```text
Decision: migrate the queue library (reversible, value ≈ 10 engineer-days)
Lead candidate: migrate now
Open questions and worst-case regret if committed now:
  Q1 perf regression under peak load        ≈ 3.0 days  (30%)
  Q2 missing dead-letter feature            ≈ 1.0 day   (10%)
  Q3 licence change next year               ≈ 0.5 day   ( 5%)
max = 30% ≥ 20% threshold → one more round, on Q1 only
After a load-test member returns: Q1 ≈ 0.8 day (8%) → max 10% < 20% → STOP, commit
```

Manifest wiring, using fields the shipped `agents/teams/*/team.yaml` files already carry:

```yaml
expansion_gate: { rule: evpi, evpi_threshold: low, max_dynamic_members: 2 }
stopping_rule: { protocol: regret-min, reversibility: reversible, max_regret_threshold: 0.20 }  # 0.05 if irreversible
hold_policy: { required: deadline, default_deadline_days: 14, escalate_on_deadline: forced_decision }
synthesis: { aggregation: mcda, weights_locked_before_dispatch: true }
```

## Related

- [dynamic-team-expansion.md](dynamic-team-expansion.md): where the EVPI gate fires.
- [behavioral-economics-applied.md](behavioral-economics-applied.md): three-option verdicts that include `hold`.
- [game-theory-agent-teams.md](game-theory-agent-teams.md): voting and Shapley at the same layer.
