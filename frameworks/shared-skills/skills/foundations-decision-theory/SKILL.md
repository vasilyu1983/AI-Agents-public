---
name: foundations-decision-theory
description: Decision-theory primitives for uncertain choices, utility, Bayesian decisions, regret, value of information, MCDA, options, and bandits. Use when choosing under uncertainty.
compatibility: Portable core only.
version: "1.3"
last_validated: 2026-09-08
---

# Decision Theory Foundations


11 canonical decision-theory primitives for decisions under uncertainty. Each primitive is a formal tool with defined inputs, outputs, and failure modes. Primitives are domain-agnostic: the same expected-utility calculation that gates a product launch gates a capital investment; the same EVPI formula that sizes a market research study sizes a pre-launch pilot.

## When to Apply

**Apply decision-theory when:**
- Single irreversible call under uncertainty (launch / kill / restructure)
- Value-of-information question — "is the next experiment worth running?"
- Real-options framing — staged investment with kill criteria
- Multi-criteria choice with explicit weights (MCDA, AHP)
- Multi-armed bandit allocation between treatments under regret minimisation

**Skip and use simpler alternatives when:**
- Decision is reversible and low-cost — just try it; analysis paralysis costs more than the wrong choice
- Multiple agents with strategic interaction — use foundations-game-theory
- Causal "did X cause Y" question — use foundations-causal-inference
- A clear oracle exists (test suite, KPI threshold) — use the oracle
- All candidate options are dominated by one option on every criterion — no decision-theory needed
- EVPI is below a justified utility-compatible additive information cost — skip that study; with nonlinear utility evaluate terminal costs before deciding

## Contents

- [Quick Reference](#quick-reference)
- [Primitive Index](#primitive-index)
- [Formal Supporting Theory](#formal-supporting-theory)
- [Misuse Boundaries](#misuse-boundaries)
- [When Expected-Value Reasoning Breaks Down](#when-expected-value-reasoning-breaks-down-non-ergodicity-ruin-risk-and-kelly)
- [Elicitation Failure Modes](#elicitation-failure-modes)
  - [Machine-Elicited Probabilities](#machine-elicited-probabilities)
- [Decision Checklist](#decision-checklist)
- [Anti-Patterns](#anti-patterns)
- [Composition Recipes](#composition-recipes)
- [Workflow](#workflow)
- [ASCII Flow](#ascii-flow)
- [Related Skills](#related-skills)
- [Fact-Checking](#fact-checking)

---

## Quick Reference

| # | Primitive | When to Reach For It |
|---|-----------|----------------------|
| 1 | [Expected Utility (EU)](#1-expected-utility) | Ranking risky options when outcomes are commensurable |
| 2 | [Bayesian Decision](#2-bayesian-decision) | Updating action after observing evidence; minimizing posterior expected loss |
| 3 | [Minimax Regret](#3-minimax-regret) | Adversarial or ambiguous probability; Savage-style robustness |
| 4 | [Value of Information](#4-value-of-information) | Deciding whether to run an experiment, study, or pilot |
| 5 | [Multi-Criteria Decision Analysis](#5-multi-criteria-decision-analysis) | Ranking options on incommensurable objectives |
| 6 | [Risk Aversion](#6-risk-aversion) | Adjusting EU for concave utility; certainty-equivalent pricing |
| 7 | [Real Options](#7-real-options) | Valuing flexibility: defer, expand, or abandon |
| 8 | [Prospect Theory](#8-prospect-theory) | Predicting or correcting human choice under risk |
| 9 | [Ellsberg and Allais Paradoxes](#9-ellsberg-and-allais-paradoxes) | Diagnosing EU violations under ambiguity and certainty effects |
| 10 | [Multi-Armed Bandit](#10-multi-armed-bandit) | Sequential exploration–exploitation under uncertainty |
| 11 | [Stochastic Dominance](#11-stochastic-dominance) | Distribution-level ranking without specifying a utility function |

---

## Primitive Index

Each primitive has a full playbook (definition, when to use, inputs, outputs, failure modes, worked example, sources).

| # | Primitive | Failure Mode It Addresses |
|---|-----------|--------------------------|
| 1 | [Expected Utility](assets/templates/decision-theory/01-expected-utility.md) | Choosing options by raw expected value, ignoring risk |
| 2 | [Bayesian Decision](assets/templates/decision-theory/02-bayesian-decision.md) | Acting on prior beliefs without updating on available evidence |
| 3 | [Minimax Regret](assets/templates/decision-theory/03-minimax-regret.md) | Paralysis or overconfidence under deep uncertainty |
| 4 | [Value of Information](assets/templates/decision-theory/04-value-of-information.md) | Running experiments whose cost exceeds their decision value |
| 5 | [Multi-Criteria Decision Analysis](assets/templates/decision-theory/05-multi-criteria.md) | Collapsing incommensurable objectives into a single number without disclosure |
| 6 | [Risk Aversion](assets/templates/decision-theory/06-risk-aversion.md) | Ignoring the difference between expected value and certainty equivalent |
| 7 | [Real Options](assets/templates/decision-theory/07-real-options.md) | Treating irreversible decisions as if they were reversible |
| 8 | [Prospect Theory](assets/templates/decision-theory/08-prospect-theory.md) | Prescriptive models failing to predict or explain actual human choice |
| 9 | [Ellsberg and Allais Paradoxes](assets/templates/decision-theory/09-ellsberg-allais.md) | Applying EU where ambiguity aversion or certainty effects dominate |
| 10 | [Multi-Armed Bandit](assets/templates/decision-theory/10-multi-armed-bandit.md) | Fixed allocation ignoring the value of exploration |
| 11 | [Stochastic Dominance](assets/templates/decision-theory/11-stochastic-dominance.md) | Comparing distributions only at their means |

---

## Formal Supporting Theory

| Theory Area | Use When | Applied Primitives It Grounds |
|---|---|---|
| Expected utility axioms | Need normative ranking under known probabilities | #1, #6, #11 |
| Bayesian decision theory | Need posterior expected loss, Bayes risk, or decision rules after evidence | #2, #4 |
| Robust decision criteria | Need action under ambiguity, adversarial states, or unclear probabilities | #3, #9 |
| Information economics | Need to decide whether evidence is worth buying | #4 |
| Multi-attribute utility | Need transparent tradeoffs across incommensurable goals | #5 |
| Real options theory | Need irreversibility, deferral, expansion, or abandonment value | #7 |
| Descriptive decision theory | Need to predict human deviations from EU | #8, #9 |
| Sequential learning theory | Need exploration-exploitation allocation | #10 |

Use [`references/formal-theory-map.md`](references/formal-theory-map.md) when the task needs theorem assumptions, estimand boundaries, or a normative-vs-descriptive split.

---

## Misuse Boundaries

| Misuse | Why It Is Wrong | Required Correction |
|---|---|---|
| Optimizing expected value for a risk-averse decision maker | EV ignores utility curvature and downside pain | Compute expected utility and certainty equivalent |
| Treating MCDA weights as objective truth | Weights encode stakeholder preferences | Disclose weights and run sensitivity analysis |
| Reporting an MCDA ranking without a rank-reversal test | Adding or dropping an irrelevant alternative silently reorders the result; an audit of 27 published MCDM pipeline/dataset combinations found recomposition consistency (RRT3) failing in ~48% of examples and transitivity (RRT2) in ~15% | Run the Wang–Triantaphyllou RRT1–RRT3 tests alongside weight sensitivity (Cabral et al., arXiv:2508.00129) |
| Running experiments without VoI | A study can be statistically interesting but decision-worthless | Compute EVPI/EVSI before funding research |
| Applying EU under deep ambiguity | Unknown probabilities violate the input contract | Use minimax regret, maximin, or ambiguity-aware criteria; or use Wasserstein DRRO when sample data on states are available |
| Treating bandits as free optimization | Exploration has opportunity cost and fairness/product constraints | Set regret budget, guardrails, and stopping rules |
| Comparing only means | Distribution tails and dominance can reverse decisions | Check stochastic dominance and downside risk |
| Treating a positive-EV recurring business (rake, spread, underwriting) as ergodic | Per-transaction EV is an ensemble statement; the operator lives one path and correlated exposures collapse into a single joint loss | Bound the worst joint loss against capital and separate collected from estimated edge — see [`finance-trading-investing`](../finance-trading-investing/references/alpha-and-edge-hunting.md#house-side-edge-fee-capture-vs-risk-warehousing) |

Check [`references/patterns-scenarios-traps.md`](references/patterns-scenarios-traps.md) before using outputs as decision authority.

---

## When Expected-Value Reasoning Breaks Down (Non-Ergodicity, Ruin Risk, and Kelly)

Expected utility (EU, #1) does not require literal parallel ensembles: it ranks lotteries from stated probabilities and a utility function. The practical failure occurs when a one-period payoff model is reused for a repeated, path-dependent, multiplicative, or ruin-constrained process without modeling wealth state and survival. In those settings an arithmetic expected return can be positive while long-run log growth is negative. Model the dynamic process directly; expected utility with an appropriate state-dependent utility can still be coherent, while expected log growth/Kelly is one specific objective rather than a universal replacement (Peters, 2019; Kelly, 1956).

Expert checks before applying EU/CE to a repeated or leveraged decision:

- **Does the payoff compound or depend on the path?** Model wealth/state transitions and absorbing boundaries before evaluating the choice. Compute expected-log or time-average growth only when long-run growth is the stated objective; otherwise evaluate the selected terminal or path-dependent utility and survival/drawdown constraints on that process.
- **Kelly criterion** (Kelly, 1956): for a repeated bet with a known edge, the growth-optimal wager fraction is f* = edge / odds (binary case: f* = p − q/b). Betting above Kelly reduces long-run growth even though each individual bet has positive EV. Full-Kelly is higher-variance than most real decision makers tolerate; fractional Kelly (e.g., half-Kelly) is the standard practitioner correction for parameter uncertainty and risk tolerance.
- **Ruin is a constraint, not a tradeoff.** Any state with an absorbing floor must be gated with a maximum-drawdown or survival constraint *before* the EU calculation — "the EV is positive" does not rescue a bet with non-negligible ruin probability.
- Use this alongside #1 and #6: state whether the objective is terminal expected utility, survival probability, drawdown control, or long-run growth. Apply Kelly only when growth optimality, repeated comparable opportunities, and credible probabilities match the decision.

**Sources**: Peters, O. (2019). "The ergodicity problem in economics." Nature Physics 15, 1216–1221. Kelly, J. L. (1956). "A New Interpretation of Information Rate." Bell System Technical Journal 35(4).

---

## Elicitation Failure Modes

Formal primitives are only as good as the probabilities, utilities, and weights fed into them. The most common failures are in elicitation, not in the arithmetic:

| Elicitation Trap | What Goes Wrong | Correction |
|---|---|---|
| Anchoring the first number | Whoever states a probability or weight first anchors the group; later "adjustments" under-correct | Elicit independently before group discussion (Delphi-style); aggregate afterward |
| False-precision point estimates | A single-point probability hides genuine uncertainty about the probability itself | Elicit ranges or a 10/50/90 percentile distribution; calibration-train the elicitor where the decision is high-stakes |
| Analysis paralysis | Teams keep requesting more studies or precision past the point where the information can change the action | Compute EVPI (#4) before approving further elicitation; stop when utility-compatible information cost exceeds its value; with nonlinear utility recalculate terminal-outcome EU |
| Weights presented as objective | MCDA (#5) weights are framed as model output rather than negotiated stakeholder preference | Disclose weight provenance and run sensitivity analysis; treat weights as an input to be negotiated, not a discovered fact |
| Stated risk tolerance vs. revealed risk tolerance | Survey-elicited utility/risk-aversion parameters diverge from what the same stakeholder actually does under real stakes | Cross-check elicited CARA/CRRA parameters (#6) against revealed past choices (insurance, past bets) where available |
| Ambiguity flattened into a probability | An unknown probability is silently converted to 50/50 or a base rate, hiding ambiguity aversion | Run the Ellsberg/Allais diagnostic (#9) first; do not treat "unknown" as "known and uniform" |

### Machine-Elicited Probabilities

Probability inputs increasingly come from an LLM rather than a human panel. Treat them as a calibrated-but-not-superhuman forecaster, and score them the same way you would score a person:

- **Accuracy is close but not yet at parity.** On ForecastBench (Forecasting Research Institute), human superforecasters led the best LLMs by 0.017 Brier points as of 2026-01-29, with extrapolated parity projected for November 2026 (95% CI Jan 2026 – Nov 2027). Machine forecasts are usable as one panel member; they are not yet a replacement for a calibrated human on a high-stakes prior.
- **Overconfidence is directional, not uniform.** Models skew overconfident on events they rate as likely, while staying reasonably calibrated in the low-probability tail. Discount high stated probabilities more than low ones.
- **Verbalized confidence is not the model's probability.** A stated "I'm 90% sure" diverges from both token-level likelihood and realized accuracy, and RLHF-style alignment training degrades calibration by rewarding confident phrasing. Score against outcomes; never take the sentence at face value.
- **Aggregate rather than single-shot.** The anchoring correction above applies unchanged: sample independently across prompts or models before pooling, rather than accepting one generation as the estimate.

---

## Decision Checklist

- [ ] **Risky choice**: Are outcomes probabilistic and commensurable? → EU (#1), check risk aversion (#6)
- [ ] **Evidence available**: Has new information arrived that should change the action? → Bayesian decision (#2)
- [ ] **Ambiguous probabilities**: Are likelihoods unknown or contested? → minimax regret (#3), check Ellsberg (#9)
- [ ] **Experiment proposed**: Does a study, pilot, or A/B test precede the decision? → VoI (#4) before approving it
- [ ] **Multiple objectives**: Are criteria incommensurable (cost, quality, speed, risk)? → MCDA (#5)
- [ ] **Risk-averse stakeholders**: Does the decision maker care about variance, not just mean? → risk aversion (#6), certainty equivalent
- [ ] **Irreversible action**: Does the option foreclose future choices? → real options (#7), option to defer
- [ ] **Human choice involved**: Are you predicting or nudging actual human behavior? → prospect theory (#8)
- [ ] **EU anomalies present**: Do choices violate independence or sure-thing principle? → Ellsberg or Allais (#9)
- [ ] **Sequential decisions under uncertainty**: Is exploration vs. exploitation the core tension? → MAB (#10)
- [ ] **Distribution comparison needed**: Compare options without assuming a specific utility function? → stochastic dominance (#11)

---

## Anti-Patterns

| Anti-Pattern | Decision Theory Diagnosis | Fix |
|-------------|--------------------------|-----|
| Running an experiment when EVPI < experiment cost | VoI ignored; the information cannot improve the decision enough to justify the cost | Compute EVPI before approving any study or pilot (#4) |
| Choosing the highest-expected-value option for a risk-averse decision maker | Conflating EV with EU under concave utility; CE < EV for risk-averse agents | Apply utility function and compute certainty equivalent (#6) |
| Treating MCDA weights as objective | AHP/TOPSIS weights embed subjective preferences; different weight schemes reverse rankings | Disclose weights, run sensitivity analysis on weight perturbations (#5) |
| Applying EU under Ellsberg-type ambiguity | Decision maker exhibits ambiguity aversion — unknown probabilities trigger non-EU behavior | Switch to minimax regret (#3) or maximin for robustness; flag the ambiguity (#9) |
| Sunk-cost fallacy: not abandoning a losing project | Irreversibility conflated with commitment; option to abandon ignored | Price the option to abandon using real-options logic (#7) |
| Fixing traffic to each variant before observing response | Ignores exploration value; foregone learning from early-stopping | Use Thompson sampling or UCB; regret scales with suboptimal arm pulls (#10) |
| Comparing options only at their mean outcomes | Mean may be identical while variance differs materially | Check FSD or SSD before concluding indifference (#11) |
| Using EU where loss aversion and probability weighting apply | EU predicts poorly for mixed gains/losses around a reference point | Use prospect theory value function and probability weighting for descriptive accuracy (#8) |

---

All VoI cost gates below assume utility-compatible additive costs; otherwise recalculate expected utility with costs/delay in terminal outcomes.

## Composition Recipes

### Should we run this experiment?

_Context_: A team proposes a study, pilot, or A/B test before making a decision.

1. Define utility, affected population and decision horizon. EVPI is the cost-free upper bound (#4); compare it to an additive study cost only on the same utility scale (e.g., risk-neutral net money).
2. Compute EVSI for the specific study design — account for noise and sample size (#4).
3. Compare study versus immediate-action expected utility including cost and delay. With nonlinear utility, incorporate costs into terminal outcomes before applying utility; do not subtract pounds or hours from utility EVSI. Optimize over discrete sample sizes, no study and endpoints; marginal gain=cost is only a differentiable interior condition.
4. If the decision maker exhibits ambiguity aversion over the prior distribution, apply minimax regret (#3) as a robustness check alongside EU.

**Worked example:** Choose between an outside action worth 0 and an action paying +1 or -1 with equal probability. The current value is 0 and perfect information is worth 0.5. A symmetric signal that identifies the payoff correctly 75% of the time produces posterior means +0.5 and -0.5, so the posterior-optimal expected value is 0.25 and EVSI is 0.25. Here utility is linear in payoff and cost is in those same payoff units; run the study only when its cost is below 0.25. EVPI exceeding cost merely leaves open the possibility that a study is worthwhile; it does not approve a particular study. Likewise, a percentage reduction in posterior variance is not a percentage of EVPI. Compute EVSI from the signal likelihoods and posterior-optimal actions.

---

### Feature roadmap ranking under multiple objectives

_Context_: A product team must rank features or bets across cost, reach, strategic value, and risk.

1. Enumerate criteria and elicit weights using AHP or direct assignment (#5). Document the weight provenance.
2. Score each option on each criterion. Run TOPSIS or weighted-sum to produce a ranking.
3. Apply sensitivity analysis: perturb each weight ±20% and observe rank stability. Surface rank-reversals to stakeholders.
4. For options with irreversible commitments, price the option to defer (#7) — deferral has value when uncertainty will resolve.
5. If the team is risk-averse, compute certainty equivalents (#6) for options with high-variance outcomes; a lower CE may reverse the MCDA ranking.

---

### Sequential resource allocation across uncertain alternatives

_Context_: Marketing budget, experiment slots, or engineering capacity must be allocated across options whose true performance is unknown.

1. Frame as a multi-armed bandit (#10): each option is an arm with an unknown reward distribution.
2. Choose a policy: Thompson sampling for Bayesian updating on observed rewards; UCB for frequentist regret guarantees.
3. Before the first pull, compute EVPI (#4) to bound the total value of optimal learning — this caps the budget worth spending on exploration.
4. After sufficient observations, check stochastic dominance (#11): if one arm FSD-dominates all others, reallocate fully to it regardless of remaining regret budget.
5. Apply risk aversion (#6) if the decision maker penalizes downside variance: a risk-averse CE may favor a lower-mean but lower-variance arm earlier than pure regret minimization would suggest.

---

### VoI gating for expensive LLM calls and bandit-driven model routing

_Context_: An AI agent or orchestration layer must decide whether to invoke an expensive large model, run a retrieval step, or route a query to one of several LLM backends — each with different quality-cost profiles.

1. **VoI gate before each costly call** (#4): define states, priors, actions, utilities and the call's signal likelihoods; compute EVSI from posterior-optimal actions and compare with utility-compatible cost. Confidence alone does not imply zero information value: prior (.999,.001), risky utilities (1,−100), safe (0,0) give current EU .899 and EVPI .1. Perfect observation costing .01 is worthwhile. An uninformative signal instead has EVSI=0. EVPI only supplies a cost-free upper bound: below additive cost it can exclude a call, above cost it does not approve that call. Apply the same logic to retrieval and model-tier selection; evaluate terminal outcomes when utility/cost is nonlinear.
2. **Bandit-driven model routing** (#10): treat each LLM backend (or prompt variant) as a bandit arm with unknown quality distribution per query class. Use Thompson sampling to learn the best arm per context cluster; a LinUCB-based policy achieves sublinear regret without predicting future prompts or accessing model internals, including under unstructured context evolution as users refine queries mid-session (Poon et al., arXiv:2506.17670).
3. **Risk aversion on tail latency** (#6): for SLA-sensitive paths, compute the certainty equivalent of the latency distribution — a risk-neutral mean-latency comparison may select a high-variance backend a risk-averse product cannot afford.
4. **Stochastic dominance check before full reallocation** (#11): once enough observations accumulate, verify that the preferred arm FSD-dominates alternatives across quality and cost dimensions before committing the full traffic budget.

---

### Clarify-or-commit: should the agent ask the user a question?

_Context_: An agent holds an ambiguous instruction and must decide whether to ask a clarifying question or proceed on its best reading. Each question costs user patience; a wrong assumption costs a wasted trajectory.

1. **Score each candidate question by EVSI** (#4) using its answer likelihoods, priors and action utilities; use EVPI only as an upper bound unless the answer reveals the full relevant state. The value of a question is the expected improvement in the *action*, so a question whose answers all lead to the same next step has zero value however uncertain the agent is. Compare with utility-compatible asking cost. Paper-specific EVPI-based surrogate scores are not exact EVSI; EVPI-scored clarification cut question count 1.5–2.7 times with higher ambiguous-task coverage on the study-specific ClarifyBench evaluation ([Suri et al., arXiv:2511.08798, §7 and Table 2](https://arxiv.org/html/2511.08798)).
2. **Separate specification uncertainty from model uncertainty.** Only the first is fixable by asking. Ambiguity about what the user wants is a question; ambiguity about whether the agent's own output is correct is a verification or retrieval step, and asking the user will not resolve it.
3. **Model timing as part of VoI.** Rework cost can reduce a question's value after execution begins, but the decay curve depends on task, ambiguity type, benchmark, and model. Gulati et al. (arXiv:2605.07937) tested 84 forced-injection variants across three benchmarks and four models in more than 6,000 runs; their 10% and 50% injection positions are experimental grid points, not universal deadlines.
4. **Budget asking explicitly and measure locally.** Front-load high-impact goal questions when rework is costly, but keep asking available whenever a possible answer changes the safe or authorized action. The paper's natural-asking results used 300 sessions; the reported 52% over-asking figure applies to GPT-5.2 on 100 TAC sessions, not to frontier models as a class.

---

## Workflow

1. Identify the decision structure: risky choice, ambiguous probabilities, sequential learning, or multi-objective ranking.
2. Use the [Decision Checklist](#decision-checklist) to select the applicable primitive(s).
3. For a small finite action-by-state matrix, copy a case from [`data/finite-state-decision-fixtures.json`](data/finite-state-decision-fixtures.json), edit its `input`, and run `python3 scripts/decision_calculator.py model.json`. Omit `prior` for minimax regret alone; add explicit `signal_likelihoods` and `study_cost` for exact finite-signal EVSI. Read the [input, calculation, and interpretation contract](references/finite-state-calculator.md) before using the result.
4. Open the per-primitive playbook in [`assets/templates/decision-theory/`](assets/templates/decision-theory/) for the full definition, inputs, outputs, failure modes, and worked example.
5. For compound decisions, use the [Composition Recipes](#composition-recipes) to stack primitives.
6. Verify inputs: probability estimates, utility function parameters, and criteria weights are the most common failure points.
7. Disclose assumptions explicitly before acting on any MCDA ranking or EU calculation.

---

## ASCII Flow

```text
Single-agent decision under uncertainty
  -> Define actions, states, outcomes, and constraints
  -> Classify structure: risk, ambiguity, sequential learning, or multi-criteria
  -> Select primitive and open playbook
  -> Elicit probabilities, utilities, regret, or weights
     +-- inputs weak -> run sensitivity or value-of-information check
     +-- inputs usable -> compute recommendation
  -> Report action, assumptions, uncertainty, and decision boundary
```

---

## Navigation

- Practical completion contract and known-answer controls: [references/practical-contract.md](references/practical-contract.md).

- Per-primitive playbooks: [`assets/templates/decision-theory/`](assets/templates/decision-theory/) (one file per primitive)
- Composition guide and selection matrix: [`assets/templates/decision-theory/README.md`](assets/templates/decision-theory/README.md)
- Formal theory map: [`references/formal-theory-map.md`](references/formal-theory-map.md)
- Patterns, scenarios, and traps: [`references/patterns-scenarios-traps.md`](references/patterns-scenarios-traps.md)
- Domain-agnostic primitives overview, anti-patterns by decision structure, and checklist: [`references/primitives-overview.md`](references/primitives-overview.md)
- Finite-state calculator contract and interpretation: [`references/finite-state-calculator.md`](references/finite-state-calculator.md)
- Exact calculator fixtures: [`data/finite-state-decision-fixtures.json`](data/finite-state-decision-fixtures.json)
- Sources: [`data/sources.json`](data/sources.json)

---

## Related Skills

This skill is a self-contained foundations primitive. Cross-link only to other `foundations-*` skills when a task requires joint coverage (e.g., `foundations-game-theory` for multi-agent settings, `foundations-causal-inference` for causal identification before decision framing).

---

## Fact-Checking

- EU axioms and vNM theorem: von Neumann and Morgenstern (1944/1947). Theory of Games and Economic Behavior.
- Bayesian decision theory and Bayes risk: Raiffa and Schlaifer (1961). Applied Statistical Decision Theory.
- Minimax regret: Savage (1954). The Foundations of Statistics.
- Value of information (EVPI, EVSI): Raiffa and Schlaifer (1961); Howard (1966) "Information Value Theory."
- AHP: Saaty (1980). The Analytic Hierarchy Process.
- CARA/CRRA, certainty equivalent: Pratt (1964) "Risk Aversion in the Small and in the Large."
- Real options: Dixit and Pindyck (1994). Investment under Uncertainty.
- Prospect theory, probability weighting: Kahneman and Tversky (1979) "Prospect Theory: An Analysis of Decision under Risk."
- Loss aversion re-estimate: Brown, Imai, Vieider, and Camerer (2024). "Meta-Analysis of Empirical Estimates of Loss Aversion." Journal of Economic Literature 62(2), 485–516. Mean λ ≈ 1.955 [1.820, 2.102] across 607 estimates — supersedes the original λ ≈ 2.25 point estimate as the best current population value; both are contested. [Primitive #8]
- Ergodicity economics and Kelly criterion: Peters (2019) "The ergodicity problem in economics," Nature Physics 15; Kelly (1956) "A New Interpretation of Information Rate," Bell System Technical Journal 35(4). [Primitive #6; expected-value breakdown section]
- Ellsberg paradox: Ellsberg (1961) "Risk, Ambiguity, and the Savage Axioms."
- Allais paradox: Allais (1953) "Le comportement de l'homme rationnel devant le risque."
- Multi-armed bandit and UCB: Robbins (1952); Auer, Cesa-Bianchi, and Fischer (2002).
- Thompson sampling: Thompson (1933); Russo et al. (2018). "A Tutorial on Thompson Sampling."
- Stochastic dominance: Hadar and Russell (1969); Levy (1992) review.
- Lattimore and Szepesvári (2020). Bandit Algorithms.
- Constrained bandits (best-of-both-worlds): Bernasconi, Castiglioni, Celli (ICML 2025, PMLR 267:3877–3898). [Primitive #10]
- LLM-based PSRL: Arumugam and Griffiths (ICLR 2026). arXiv:2504.20997. [Primitive #10]
- Wasserstein DRRO: Fiechtner and Blanchet (2025). arXiv:2504.10796. [Primitive #3]
- Gen-WDRO: NeurIPS 2025 poster. [Primitive #3]
- Distributionally Robust Performative Optimization: Jia et al. (NeurIPS 2025). arXiv:2407.01344. [Primitives #3, #1]
- Online Decision-Focused Learning: Capitaine et al. (ICLR 2026). arXiv:2505.13564. [Primitive #4]
- DFL via Dual Surrogates: Rodriguez-Diaz et al. (NeurIPS 2025). arXiv:2511.04909. [Primitive #4]
- Multi-LLM selection via contextual bandits: Poon, Dai, Liu, Kong, Lui, Zuo (arXiv:2506.17670, June 2025). LinUCB routing across LLM backends with sublinear regret under unstructured context evolution. [Primitive #10; app-builder recipe]
- Decision-Centric Design for LLM Systems: Sun (arXiv:2604.00414, April 2026). Separates the decision layer from generation in LLM systems; formalizes VoI gating and clarify-or-commit tradeoffs as explicit decision problems. [Primitive #4; app-builder recipe]
- EVPI-scored agent clarification: Suri, Mathur, Lipka, Dernoncourt, Rossi, Manocha (arXiv:2511.08798, Nov 2025, rev. Apr 2026). SAGE-Agent; cost-penalized EVPI over candidate questions; 1.5–2.7 times fewer questions on ClarifyBench with higher ambiguous-task coverage (study-specific results, §7 and Table 2). [Primitive #4; clarify-or-commit recipe]
- Clarification timing: Gulati, Gupta, Lumer, Sen, Subbiah (arXiv:2605.07937, May 2026). More than 6,000 forced-injection runs across 84 variants, 3 benchmarks, and 4 models, plus 300 natural-asking sessions. Timing effects vary by benchmark, ambiguity dimension, and model; the tested 10%/50% positions are not general policy cutoffs. [Primitive #4; clarify-or-commit recipe]
- MCDA rank-reversal prevalence: Cabral et al. (arXiv:2508.00129, July 2025, rev. Aug 2026). Operationalizes Wang–Triantaphyllou RRT1–RRT3 in Scikit-Criteria; RRT3 fails in ~48% and RRT2 in ~14.8% of the study's 27 selected published pipeline/dataset combinations (§7.2 and §8; not population prevalence). [Primitive #5; misuse boundaries]
- LLM vs. superforecaster calibration: Bastani, Kučinskas, Reynolds (Forecasting Research Institute, ForecastBench). Superforecasters ahead by 0.017 Brier points as of 2026-01-29; extrapolated parity Nov 2026 (95% CI Jan 2026 – Nov 2027). Verify the current leaderboard before citing the gap — it is a moving number. [Elicitation Failure Modes]
- Numeric thresholds (e.g., EVSI formulas, CE approximations) should be verified against primary sources before citing in decisions.

## Learnings Loop

When prior decisions or pitfalls are relevant, consult `learnings.consolidated.md` if present; use `learnings.md` only for needed history or as the available fallback. Otherwise skip both.

After applying it, if you encountered a pattern worth remembering, a mistake worth preventing, or a domain fact that surprised you, append one dated bullet to `learnings.md` via `agents-skills-feedback-loop/scripts/append_learning.py`. Do not modify `SKILL.md` itself.
