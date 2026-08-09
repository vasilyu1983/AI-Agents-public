# Mechanism: Shapley Contribution Scoring

**Source**: ShapleyFlow, AgentSHAP ([2512.12597](https://www.arxiv.org/pdf/2512.12597)), HiveMind / DAG-Shapley ([2512.06432](https://arxiv.org/html/2512.06432)), Shapley-Coop, SELFORG (2025–2026).

## Domain Applications

- **Ad attribution / marketing mix**: Shapley splits conversion credit across touchpoints (paid search, social, email) proportional to marginal contribution; replaces last-touch or linear heuristics.
- **Revenue sharing in partnerships**: each partner's marginal contribution to joint revenue computed via subset simulation; Shapley split agreed at contract time prevents post-hoc disputes.
- **Feature importance in ML pipelines**: Shapley values identify which features or data sources drive model accuracy; guides data acquisition budget.
- **Agent team composition**: score each member's marginal contribution after a team run; remove low-contribution members from future similar tasks.

## Problem

After a team run, you don't know which members actually contributed value vs. which produced redundant or low-quality output.

## Solution

Compute each member's **marginal contribution** using Shapley values from cooperative game theory.

## Shapley Value (Simplified)

A member's Shapley value = the average marginal value they add across all possible team compositions.

**Practical approximation for agent teams:**

```
For each member M in the team:
  1. Compare team output quality WITH M vs. WITHOUT M
  2. M's contribution = quality difference

Score each member:
  - High contribution (>30% of total): core member — keep in future runs
  - Medium contribution (10-30%): useful but replaceable — rotate or merge role
  - Low contribution (<10%): redundant — remove from future similar tasks
```

## Applying to Team Optimization

| After Team Run | Shapley Insight | Action |
|---------------|-----------------|--------|
| `startup-monetization-board` consistently shows `startup-operating-system-reviewer` adds little on early-stage products | Finance and operating-system perspective is redundant before revenue scale | Remove from early-stage runs, keep for Series B+ |
| `software-code-review-board` shows `security-reviewer` catches issues others miss 80% of the time | Security perspective is high-marginal-value | Consider promoting to synthesis co-owner |
| `startup-strategy` shows `ux-designer` output overlaps with `product-strategist` | Redundant perspectives — correlated contributions | Merge into one member or differentiate their briefs |

## Implementation

After each team run, the synthesis owner adds a contribution assessment:

```
## Member Contributions (Shapley Estimate)

| Member | Unique Insights | Redundant With | Contribution |
|--------|----------------|----------------|:------------:|
| pricing-advisor | 3 pricing-specific findings | — | High |
| growth-specialist | 2 channel insights | 1 overlapped with marketing-strategist | Medium |
| product-strategist | 1 activation insight, wrote synthesis | — | High |
| ux-designer | 0 unique insights | All covered by product-strategist | Low |
```

## Cost Reduction: DAG-Shapley

True Shapley computation requires `2^N` evaluations and is intractable past ~6 members. The 2026 **DAG-Shapley** approach (HiveMind, [2512.06432](https://arxiv.org/html/2512.06432)) exploits the fact that agent workflows form a Directed Acyclic Graph: members downstream of M cannot have contributed to M's output, so most of the `2^N` coalitions collapse to a small set of topologically valid ones. This **cuts LLM calls by over 80%** while keeping attribution accuracy comparable to full Shapley.

Practical rule: if your team has a clear DAG (member B reads member A's output), compute Shapley only over coalitions consistent with the DAG. For fully parallel teams (no inter-member reads), DAG-Shapley collapses to the full computation — use the cosine-similarity approximation in mechanism 14 instead.

## Related

- [`05-reputation-gating.md`](05-reputation-gating.md) — Shapley scores feed reputation tiers
- [`06-cooperation-defection.md`](06-cooperation-defection.md) — Shapley makes free-riding detectable
- [`14-credibility-scoring.md`](14-credibility-scoring.md) — per-claim credibility is the within-run analog of cross-run Shapley
