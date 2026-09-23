# Verified Game Artifacts and Evidence Tiers

## Separate the evidence tiers

- **Formal mechanism:** specify actors, utilities, information, feasible actions and solution concept. A theorem applies only under its model; strategyproof auctions require their stated assumptions and actual enforcement.
- **Experimental agent recipe:** debate, reputation prompts, embedding consensus and prompt evolution are task-dependent hypotheses. Evaluate held-out outcomes against a simpler baseline; do not label a prompt an incentive-compatible mechanism merely because it asks for honesty.
- **Engineering default:** sample count, confidence cutoff, probation duration, mutation cadence and team size are configurable starting policies. Choose them from loss, uncertainty, dependence, drift and operating cost; no universal 3-success/5-candidate/50-run/60%-preference guarantee exists.

## Exact worked examples

Run from the bundle root:

```bash
python3 scripts/game_artifacts.py --self-test
```

The script checks pure Nash best responses in a two-player prisoner's dilemma with actions [cooperate, defect] and payoff matrix `[[[3,3],[0,5]],[[5,0],[1,1]]]`. Defection is each player's strict best response to either counterpart action, so (defect,defect) is the unique pure Nash equilibrium, although mutual cooperation gives both a higher payoff. This is a specified one-shot game; it does not establish a repeated-game strategy or describe real LLM preferences. Matching pennies has no pure equilibrium in the test; mixed equilibria remain possible.

For a three-member characteristic function, A contributes2, B contributes1, A+B adds synergy3 and C contributes−1. All eight coalition utilities are evaluated with rational (`Fraction`) arithmetic; JSON reports an exact fraction and a separately labeled float projection. Integer/rational inputs preserve exactness; passing a binary float preserves that float's rational value, not an intended decimal. Exact Shapley allocation is **[3.5, 2.5, −1]**, summing to the grand-coalition increment5. Negative credit is valid; do not silently clip it and claim efficiency. Five equal additive members each receive1, normalized to **20%**. Expected role-specific credit need not be equal.

## Empirical attribution contract

- Fix the utility metric, empty-coalition baseline, missing-member replacement, coalition feasibility and task distribution. Score through an independent oracle/reviewer, not member self-claims.
- Exact coalition evaluation costs up to 2^n utilities (eight in this example). For larger teams, cap sampled permutations and evaluate paired coalition increments on matched tasks/seeds; cache only identical evaluation conditions.
- Report estimate uncertainty from task/permutation resampling, and state dependence/drift limitations. Repeated runs with correlated tasks do not establish independent precision. Separate task variability from Monte Carlo approximation error; numerical exactness of a specified utility table says nothing about utility measurement error.
- Predefine an adoption margin against team-level held-out quality, cost and safety constraints. Inspect synergy, redundancy and negative contributions before demoting a member; validate each changed prompt independently and preserve a rollback version.

This demo computes specified finite examples, not empirical agent-performance results. Sources: Shapley (1953), value of cooperative games, and Osborne/Rubinstein's classical game theory; canonical source links remain in [sources.json](../data/sources.json) and the [formal theory map](formal-theory-map.md).
