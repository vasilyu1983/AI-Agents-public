---
name: foundations-decision-theory
description: "Chooses under uncertainty: value of more data, cost-based thresholds, abstention, when to stop a test and ship, robust choice. Use when deciding, not estimating."
compatibility: Portable core only.
version: "1.4"
last_validated: 2026-09-08
---

# Decision Theory Foundations

## When to Apply

**Apply when:**
- A go/no-go, launch/kill, or irreversible commitment must be made under uncertainty.
- Someone asks "is another experiment, pilot, spike, or clarifying question worth it?" (value of information).
- A probability must become an action: approve / block / escalate / abstain at unequal error costs.
- A test with several variants must stop and ship a winner, or traffic must be allocated adaptively.
- A new routing or ranking policy must be judged from logs before rollout.
- Options must be ranked on several criteria, or staged with kill criteria (real options).

**Skip and use something else when:**
- The decision is reversible and cheap: just try it.
- Other agents respond strategically: use [foundations-game-theory](../foundations-game-theory/SKILL.md).
- The question is "did X cause Y" or "how big is the effect": use [foundations-causal-inference](../foundations-causal-inference/SKILL.md) or [foundations-statistical-inference](../foundations-statistical-inference/SKILL.md).
- The question is about predicting or nudging human choice: use [foundations-behavioral-economics](../foundations-behavioral-economics/SKILL.md). This skill is normative.
- An oracle exists (a test suite, a hard KPI threshold), or one option dominates on every criterion.
- EVPI is below a utility-compatible additive information cost. Skip that study. Under nonlinear utility, evaluate terminal outcomes first.

## Quick Reference

Primitive index — the only one in this skill; each playbook has the definition, inputs, failure modes, and a worked example.

| # | Primitive | Reach for it when |
|---|---|---|
| 1 | [Expected Utility](assets/templates/decision-theory/01-expected-utility.md) | Ranking risky options with known or estimable probabilities |
| 2 | [Bayesian Decision](assets/templates/decision-theory/02-bayesian-decision.md) | Evidence has arrived and the action should update; posterior expected loss |
| 3 | [Minimax Regret](assets/templates/decision-theory/03-minimax-regret.md) | Probabilities unknown or contested; robustness check on a weak prior |
| 4 | [Value of Information](assets/templates/decision-theory/04-value-of-information.md) | Deciding whether a study, pilot, spike, call, or question is worth buying |
| 5 | [Multi-Criteria Decision Analysis](assets/templates/decision-theory/05-multi-criteria.md) | Incommensurable criteria; weights must be disclosed and stress-tested |
| 6 | [Risk Aversion](assets/templates/decision-theory/06-risk-aversion.md) | Variance or downside matters beyond the mean; certainty equivalent |
| 7 | [Real Options](assets/templates/decision-theory/07-real-options.md) | Irreversible commitment while uncertainty will resolve; defer/expand/abandon |
| 8 | [Prospect Theory](assets/templates/decision-theory/08-prospect-theory.md) | Normative-vs-descriptive boundary only; behavioral detail lives in behavioral-economics |
| 9 | [Ellsberg and Allais](assets/templates/decision-theory/09-ellsberg-allais.md) | Ambiguity or certainty effects make EU inputs unreliable |
| 10 | [Multi-Armed Bandit](assets/templates/decision-theory/10-multi-armed-bandit.md) | Reward collected during learning matters (regret objective) |
| 11 | [Stochastic Dominance](assets/templates/decision-theory/11-stochastic-dominance.md) | Utility-free ranking of *known* outcome distributions |
| — | [Thresholds, stopping, and OPE](references/thresholds-stopping-and-ope.md) | Cost-based thresholds, abstention, best-arm identification, expected-loss stopping, off-policy evaluation |

## Misuse Boundaries

| Misuse | Why it is wrong | Correction |
|---|---|---|
| Optimising expected value for a risk-averse or ruin-exposed decision maker | EV ignores utility curvature and absorbing losses | Expected utility and certainty equivalent (#6); ruin constraints (below) |
| Approving a study because EVPI exceeds its cost | EVPI is only an upper bound for a perfect reveal; real signals are noisy | Approve on EVSI of the specific design vs utility-compatible cost; EVPI < cost only *excludes* |
| Treating MCDA weights as objective, or skipping rank-reversal tests | Weights encode preferences. In one audit of 27 published MCDM pipeline/dataset combinations, recomposition consistency (RRT3) failed in about 48% and transitivity (RRT2) in about 15% | Disclose weights, run sensitivity, and run the Wang–Triantaphyllou RRT1–RRT3 tests (Cabral et al., arXiv:2508.00129) |
| Applying EU under deep ambiguity | Unknown probabilities break the input contract | Minimax regret, maximin, or ambiguity-aware criteria (#3, #9) |
| Using a bandit when you need an unbiased effect size | Adaptive allocation biases naive per-arm estimates; it fits badly with delayed, long-horizon, or guardrail metrics | Fixed-allocation randomised test; use bandits when in-experiment reward dominates ([OPE ref §3](references/thresholds-stopping-and-ope.md#3-best-arm-identification-vs-regret)) |
| Stopping on "P(best) > 0.99" | Ignores magnitude: it can hold forever on ties or clear on trivial gaps | Expected loss below a pre-declared threshold of caring ([§4](references/thresholds-stopping-and-ope.md#4-expected-loss-stopping)) |
| Reallocating on stochastic dominance of *sample* rewards | FSD of observed outcomes says nothing about posterior uncertainty in the mean; FSD is univariate | Scalarise quality and cost into one declared utility, then use expected loss |
| Thresholding an uncalibrated score, or a calibrated one after a prevalence shift | The Bayes threshold assumes calibrated probabilities at the deployment base rate | Calibrate, adjust for prevalence, then use c_FP/(c_FP+c_FN) ([§1](references/thresholds-stopping-and-ope.md#1-cost-sensitive-thresholds)) |
| Sunk-cost continuation | Past spend is irrelevant to the forward decision | Price the option to abandon (#7) |
| Comparing only means | Tails and dominance can reverse the choice | Stochastic dominance (#11) and downside risk (#6) |
| Treating a positive-EV recurring business (rake, spread, underwriting) as ergodic | The operator lives one path; correlated exposures collapse into a single joint loss | Bound the worst joint loss against capital |

More traps and pattern stacks: [references/patterns-scenarios-traps.md](references/patterns-scenarios-traps.md).

## When Expected-Value Reasoning Breaks Down (Non-Ergodicity, Ruin Risk, and Kelly)

EU ranks lotteries from stated probabilities and a utility function. It fails in practice when a one-period payoff model is reused for a repeated, multiplicative, path-dependent, or ruin-constrained process. There, the arithmetic expected return can be positive while long-run log growth is negative (Peters 2019).

- **Model the process.** Model wealth or state transitions and absorbing boundaries first. Use expected-log or time-average growth only when long-run growth is the stated objective.
- **Kelly** (Kelly 1956): for a repeated binary bet with known edge, f* = p − q/b. Betting above Kelly lowers long-run growth even when every bet has positive EV. Fractional Kelly (for example half-Kelly) is the usual correction for parameter uncertainty and risk tolerance.
- **Ruin is a constraint, not a tradeoff.** Gate absorbing-floor states with a survival or drawdown constraint *before* the EU calculation.

## Elicitation Failure Modes

Most failures are in the inputs, not the arithmetic.

| Trap | Correction |
|---|---|
| Anchoring on the first number stated | Elicit independently before discussion (Delphi-style), then aggregate |
| False-precision point estimates | Elicit ranges or 10/50/90 percentiles; calibration-train for high stakes |
| Analysis paralysis | Compute EVPI/EVSI (#4) before approving more elicitation or study |
| Weights presented as model output | Treat MCDA weights as negotiated inputs; disclose provenance |
| Stated vs revealed risk tolerance | Cross-check elicited risk parameters (#6) against past real-stakes choices |
| Ambiguity flattened into 50/50 | Run the Ellsberg/Allais diagnostic (#9) first |

### Machine-Elicited Probabilities

Score an LLM forecaster like any panel member:

- **Benchmark parity is not local calibration.** In its 2026-07-16 update, the Forecasting Research Institute reports that several models are statistically indistinguishable from human superforecasters on the ForecastBench tournament leaderboard. Its confidence intervals overlap substantially, so the result supports parity, not outperformance. Use machine forecasts as one panel member and score them on your own question class before trusting them on a high-stakes prior.
- **Directional miscalibration** (for example overconfidence on events rated likely) is not reported by the FRI sources. Check for it on your own resolved outcomes.
- **Verbalised confidence is not a probability.** Score against outcomes, not stated certainty.
- **Aggregate.** Sample independently across prompts or models before pooling.

## Composition Recipes

All VoI cost gates assume utility-compatible additive costs. Otherwise, put costs and delay into terminal outcomes and recompute expected utility ([practical contract](references/practical-contract.md)).

### Should we run this experiment, pilot, or spike?

1. Define the utility, the affected population, and the decision horizon. EVPI (#4) is the cost-free upper bound. If EVPI is below the additive cost, skip.
2. Compute EVSI for the specific design from its signal likelihoods, then choose the best option among no study, the feasible sample sizes, and the endpoints.
3. Run the study only if its net expected utility beats acting now, cost and delay included. Add minimax regret (#3) if the prior is weak.

**Worked example.** An outside action is worth 0. A risky action pays +1 or −1 with equal probability. Perfect information is worth 0.5. A symmetric signal that is right 75% of the time gives posterior means of ±0.5, so EVSI = 0.25. Run it only if it costs less than 0.25. A percentage reduction in posterior variance is not a percentage of EVPI. For small finite problems, use the [calculator](references/finite-state-calculator.md).

### Pick the winner among variants

1. Declare the objective. Choose *best-arm identification* if you will commit after the test, or *regret* if reward during the test matters ([OPE ref §3](references/thresholds-stopping-and-ope.md#3-best-arm-identification-vs-regret)).
2. For best-arm identification, use top-two Thompson sampling or fixed allocation. Stop when the expected loss of the leader falls below a pre-declared ε (§4). Check guardrails separately.
3. If an unbiased effect size is needed for later decisions, use fixed allocation. Hand inference to statistical-inference.

### Set an approve / escalate / abstain threshold

Calibrate the score and adjust it to the deployment prevalence. Derive p* = c_FP/(c_FP+c_FN). Add a deferral band where the review cost is below both error costs (Chow's rule), and report risk and coverage across a range of cost ratios ([§1–2](references/thresholds-stopping-and-ope.md#1-cost-sensitive-thresholds)).

### Roadmap ranking under multiple objectives

1. Elicit weights with their provenance. Score the options, run the ranking (#5), and perturb the weights to expose rank reversals. Run the RRT tests when the alternative set may change.
2. Price the option to defer on irreversible items (#7). Compute certainty equivalents on high-variance bets (#6); a lower CE can reverse the ranking.

### VoI gating for costly LLM calls and model routing

1. **Gate each costly call on EVSI** (#4), using the call's signal likelihoods. High confidence alone does not make information worthless. With prior (0.999, 0.001), a risky action (1, −100) and a safe action (0, 0), current EU is 0.899 and EVPI is 0.1, so a perfect check costing 0.01 pays. An uninformative check has EVSI 0.
2. **Route with a contextual bandit** (#10) when reward during routing matters. Poon et al. (arXiv:2506.17670, §4) prove sublinear *myopic* regret for their LinUCB-based policy under its assumptions; this does not establish optimal whole-trajectory routing.
3. **Evaluate a new router off-policy before rollout.** Use IPS, SNIPS, or DR on logged propensities with an overlap check, then confirm online ([§5](references/thresholds-stopping-and-ope.md#5-off-policy-evaluation-ope-before-switching-a-policy)).
4. **Tail latency:** compare certainty equivalents (#6), not mean latency, on SLA-sensitive paths.

### Clarify-or-commit: should the agent ask?

1. **Score each candidate question by EVSI** under its answer likelihoods. EVPI is only an upper bound. A question whose every answer leads to the same next step has zero value, however uncertain the agent is. EVPI-scored clarification cut question count by 1.5–2.7× with higher coverage of ambiguous tasks on ClarifyBench (Suri et al., arXiv:2511.08798; study-specific).
2. **Separate specification uncertainty from model uncertainty.** Only the first can be resolved by asking. The second needs verification or retrieval.
3. **Timing is part of value.** Recompute the remaining benefit of clarification as execution advances, including avoidable rework. Gulati et al. (arXiv:2605.07937, §4.1: more than 6,000 runs, 84 variants) find task-dependent decay under forced clarification injection. Their tested 10% and 50% injection points are not deadlines.
4. **Never suppress a question** whose answer changes safety, authorisation, or an irreversible action. Measure over-asking locally.

Sun (arXiv:2604.00414, §2–3) supports separating decision context, policy, and execution. Its contribution is architectural; cite Heath & Baio (arXiv:1709.02319, §2) for the EVSI calculation rather than treating Sun as a tested VoI policy.

## Workflow

1. Name the decision maker, the actions (including wait and outside options), the states, the probability provenance, the utility or loss, and the horizon ([practical contract](references/practical-contract.md)).
2. Pick primitives from the Quick Reference; load [structure-specific anti-patterns](references/primitives-overview.md) when deciding which primitive fits or checking a proposed decision model. For a small finite matrix, copy a case from [`data/finite-state-decision-fixtures.json`](data/finite-state-decision-fixtures.json) and run `python3 scripts/decision_calculator.py model.json` (see the [contract](references/finite-state-calculator.md)). Verify the calculator with `python3 scripts/test_decision_calculator.py` ([tests](scripts/test_decision_calculator.py)).
3. Run sensitivity on probabilities, utility curvature, and weights. Report where the preferred action flips.
4. Deliver the action, its assumptions, the tipping points, and what information would change it. Unknown utilities give a conditional recommendation, not decision authority.

## Navigation

- [references/thresholds-stopping-and-ope.md](references/thresholds-stopping-and-ope.md) — read for thresholds, abstention, pick-the-winner stopping, or evaluating a policy from logs.
- [references/practical-contract.md](references/practical-contract.md) — elicitation artifact, sensitivity, costs and delay, completion controls.
- [references/finite-state-calculator.md](references/finite-state-calculator.md) — exact EU / EVPI / EVSI / minimax regret on finite matrices.
- [references/patterns-scenarios-traps.md](references/patterns-scenarios-traps.md) — pattern stacks, deep uncertainty (RDM, DAPP), traps.
- [references/formal-theory-map.md](references/formal-theory-map.md) — theorem assumptions and the normative/descriptive split.
- [assets/templates/decision-theory/](assets/templates/decision-theory/README.md) — per-primitive playbooks (index).
- [data/sources.json](data/sources.json) — all citations, including textbooks and 2025–2026 papers.

## Related Skills

Cross-link only to other foundations when a task needs joint coverage: game-theory (strategic agents), causal-inference (identification, propensity logic shared with OPE), statistical-inference (calibration, anytime-valid inference after adaptive allocation), behavioral-economics (descriptive choice, loss-aversion estimates), measurement-theory (score validity).

## Learnings Loop

When prior decisions or pitfalls are relevant, consult `learnings.consolidated.md` if present; use `learnings.md` only for needed history or as the available fallback. Otherwise skip both.

After applying it, if you encountered a pattern worth remembering, a mistake worth preventing, or a domain fact that surprised you, append one dated bullet to `learnings.md` via `agents-skills-feedback-loop/scripts/append_learning.py`. Do not modify `SKILL.md` itself.
