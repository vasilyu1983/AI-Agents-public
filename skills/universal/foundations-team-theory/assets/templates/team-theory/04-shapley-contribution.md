# Mechanism: Shapley Contribution Scoring

**Regime**: Shapley credit is a shared-payoff attribution tool (who added how much to the team's joint result), so it lives in team theory. It says nothing about incentives: if members can gain by misreporting their contribution, that is a mechanism-design problem, see `foundations-game-theory`. The exact worked example (three-member characteristic function, Shapley values [3.5, 2.5, -1]) and its self-test are in `foundations-game-theory/references/verified-artifacts.md` and `scripts/game_artifacts.py`.

**Source**: ShapleyFlow, AgentSHAP ([2512.12597](https://www.arxiv.org/pdf/2512.12597)), HiveMind / DAG-Shapley ([2512.06432](https://arxiv.org/html/2512.06432)), Shapley-Coop, SELFORG (2025–2026).

## Domain Applications

- **Ad attribution / marketing mix**: Shapley splits conversion credit across touchpoints (paid search, social, email) proportional to marginal contribution; replaces last-touch or linear heuristics.
- **Revenue sharing in partnerships**: each partner's marginal contribution to joint revenue computed via subset simulation; Shapley split agreed at contract time prevents post-hoc disputes.
- **Feature importance in ML pipelines**: Shapley values identify which features or data sources drive model accuracy; guides data acquisition budget.
- **Agent team composition**: score each member's marginal contribution after a team run; remove low-contribution members from future similar tasks.

> **Attribution caveats.** Shapley credit depends on the value function you choose: the empty-coalition baseline, the missing-member (or missing-feature) policy, and whether you evaluate interventionally or observationally. It is not a causal effect, and correlated features or overlapping members can distort it. See the empirical attribution contract in [`foundations-game-theory/references/verified-artifacts.md`](../../../../foundations-game-theory/references/verified-artifacts.md), SHAP caveats in `ai-ml-data-science/references/interpretability-explainability.md`, and `foundations-causal-inference` before using it for ad attribution or feature importance.

## Problem

After a team run, you don't know which members actually contributed value vs. which produced redundant or low-quality output.

## Solution

Compute each member's **marginal contribution** using Shapley values from cooperative game theory.

## Shapley Value (Simplified)

A member's Shapley value = the average marginal value they add across all possible team compositions.

**Practical approximation for agent teams:**

```
For each member M in the team:
  1. Define coalition utility, empty-team baseline and missing-member policy
  2. Average M's marginal utility over all predecessor coalitions/permutations
  3. Report estimate uncertainty and counterfactual evaluation cost
  A single WITH-vs-WITHOUT difference is leave-one-out, not a Shapley value.

Score each member:
  - Compare contribution with a role-relative expectation and uncertainty
  - Inspect interactions, redundancy and negative values before changing roles
  - Validate removal/rotation on held-out team quality, cost and constraints
  Fixed 10%/30% thresholds are not universal retention rules.
```

## Applying to Team Optimization

| After Team Run (hypothetical examples) | Shapley Insight | Action |
|---------------|-----------------|--------|
| `startup-monetization-board` consistently shows `startup-operating-system-reviewer` adds little on early-stage products | Finance and operating-system perspective is redundant before revenue scale | Remove from early-stage runs, keep for Series B+ |
| `software-code-review-board` shows `security-reviewer` catches issues others miss | Security perspective is high-marginal-value | Consider promoting to synthesis co-owner |
| `startup-strategy` shows `ux-designer` output overlaps with `product-strategist` | Redundant perspectives — correlated contributions | Merge into one member or differentiate their briefs |

## Implementation

After each team run, the synthesis owner adds a qualitative contribution review. This is a leave-one-out style narrative, not a Shapley value; compute Shapley only from coalition utilities as described above.

```
## Member Contributions (qualitative review; not Shapley)

| Member | Unique Insights | Redundant With | Contribution |
|--------|----------------|----------------|:------------:|
| pricing-advisor | 3 pricing-specific findings | — | High |
| growth-specialist | 2 channel insights | 1 overlapped with marketing-strategist | Medium |
| product-strategist | 1 activation insight, wrote synthesis | — | High |
| ux-designer | 0 unique insights | All covered by product-strategist | Low |
```

## Cost Reduction: DAG-Shapley

Exact Shapley computation needs up to `2^N` coalition evaluations, so its cost grows quickly with team size. The **DAG-Shapley** approach (HiveMind, [2512.06432](https://arxiv.org/html/2512.06432)) exploits the fact that agent workflows form a Directed Acyclic Graph: members downstream of M cannot have contributed to M's output, so coalitions that violate the DAG order need not be evaluated. How many that saves depends on the graph. The HiveMind authors report this cuts LLM calls by over 80% with attribution accuracy comparable to full Shapley (abstract-level claim, not re-verified against the paper here; unsourced beyond that, verify before quoting or planning capacity on it).

Practical rule: if your team has a clear DAG (member B reads member A's output), compute Shapley only over coalitions consistent with the DAG. For fully parallel teams (no inter-member reads), DAG-Shapley collapses to the full computation — estimate Shapley from a capped sample of permutations on matched tasks instead, and report the sampling uncertainty (see the empirical attribution contract in [`foundations-game-theory/references/verified-artifacts.md`](../../../../foundations-game-theory/references/verified-artifacts.md)).

## Related

- [`05-reputation-gating.md`](../../../../foundations-game-theory/assets/templates/game-theory/05-reputation-gating.md) — Shapley scores feed reputation tiers
- [`06-cooperation-defection.md`](../../../../foundations-game-theory/assets/templates/game-theory/06-cooperation-defection.md) — Shapley makes free-riding detectable
- [`14-credibility-scoring.md`](../../../../foundations-game-theory/assets/templates/game-theory/14-credibility-scoring.md) — per-claim credibility is the within-run analog of cross-run Shapley
