---
name: foundations-decision-theory
description: Decision-theory primitives for uncertain choices, utility, Bayesian decisions, regret, value of information, MCDA, options, and bandits. Use when choosing under uncertainty.
compatibility: Portable core only.
version: "1.1"
last_validated: 2026-07-11
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
- EVPI is much smaller than the cost of acquiring info — skip the study and decide now

## Contents

- [Quick Reference](#quick-reference)
- [Primitive Index](#primitive-index)
- [Formal Supporting Theory](#formal-supporting-theory)
- [Misuse Boundaries](#misuse-boundaries)
- [When Expected-Value Reasoning Breaks Down](#when-expected-value-reasoning-breaks-down-non-ergodicity-ruin-risk-and-kelly)
- [Elicitation Failure Modes](#elicitation-failure-modes)
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
| Running experiments without VoI | A study can be statistically interesting but decision-worthless | Compute EVPI/EVSI before funding research |
| Applying EU under deep ambiguity | Unknown probabilities violate the input contract | Use minimax regret, maximin, or ambiguity-aware criteria; or use Wasserstein DRRO when sample data on states are available |
| Treating bandits as free optimization | Exploration has opportunity cost and fairness/product constraints | Set regret budget, guardrails, and stopping rules |
| Comparing only means | Distribution tails and dominance can reverse decisions | Check stochastic dominance and downside risk |

Check [`references/patterns-scenarios-traps.md`](references/patterns-scenarios-traps.md) before using outputs as decision authority.

---

## When Expected-Value Reasoning Breaks Down (Non-Ergodicity, Ruin Risk, and Kelly)

EU (#1) and certainty-equivalent (#6) reasoning implicitly average over an *ensemble* of parallel outcomes for a single decision. Repeated or leveraged bets compound multiplicatively instead — the ensemble average and the *time average* (the growth rate one actor actually experiences across repeated plays) diverge whenever there is a nonzero chance of an absorbing floor (ruin, bankruptcy, delisting, project death). This is the ergodicity-economics critique (Peters, 2019, *Nature Physics*): a bet with strictly positive expected value can still have a negative time-average growth rate once outcomes compound — no utility-curvature adjustment fixes this; the fix is switching from an ensemble average to a time average.

Expert checks before applying EU/CE to a repeated or leveraged decision:

- **Does the payoff compound?** If outcomes multiply (returns, survival odds, reputation, compounding debt) rather than add, compute the time-average growth rate, not the single-shot expectation.
- **Kelly criterion** (Kelly, 1956): for a repeated bet with a known edge, the growth-optimal wager fraction is f* = edge / odds (binary case: f* = p − q/b). Betting above Kelly reduces long-run growth even though each individual bet has positive EV. Full-Kelly is higher-variance than most real decision makers tolerate; fractional Kelly (e.g., half-Kelly) is the standard practitioner correction for parameter uncertainty and risk tolerance.
- **Ruin is a constraint, not a tradeoff.** Any state with an absorbing floor must be gated with a maximum-drawdown or survival constraint *before* the EU calculation — "the EV is positive" does not rescue a bet with non-negligible ruin probability.
- Use this alongside, not instead of, #1 and #6: EU/CE for single non-compounding decisions; add ergodicity/Kelly reasoning whenever the decision repeats, compounds, or has an absorbing failure state.

**Sources**: Peters, O. (2019). "The ergodicity problem in economics." Nature Physics 15, 1216–1221. Kelly, J. L. (1956). "A New Interpretation of Information Rate." Bell System Technical Journal 35(4).

---

## Elicitation Failure Modes

Formal primitives are only as good as the probabilities, utilities, and weights fed into them. The most common failures are in elicitation, not in the arithmetic:

| Elicitation Trap | What Goes Wrong | Correction |
|---|---|---|
| Anchoring the first number | Whoever states a probability or weight first anchors the group; later "adjustments" under-correct | Elicit independently before group discussion (Delphi-style); aggregate afterward |
| False-precision point estimates | A single-point probability hides genuine uncertainty about the probability itself | Elicit ranges or a 10/50/90 percentile distribution; calibration-train the elicitor where the decision is high-stakes |
| Analysis paralysis | Teams keep requesting more studies or precision past the point where the information can change the action | Compute EVPI (#4) before approving further elicitation; stop and decide once EVPI is below the cost of refinement |
| Weights presented as objective | MCDA (#5) weights are framed as model output rather than negotiated stakeholder preference | Disclose weight provenance and run sensitivity analysis; treat weights as an input to be negotiated, not a discovered fact |
| Stated risk tolerance vs. revealed risk tolerance | Survey-elicited utility/risk-aversion parameters diverge from what the same stakeholder actually does under real stakes | Cross-check elicited CARA/CRRA parameters (#6) against revealed past choices (insurance, past bets) where available |
| Ambiguity flattened into a probability | An unknown probability is silently converted to 50/50 or a base rate, hiding ambiguity aversion | Run the Ellsberg/Allais diagnostic (#9) first; do not treat "unknown" as "known and uniform" |

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

## Composition Recipes

### Should we run this experiment?

_Context_: A team proposes a study, pilot, or A/B test before making a decision.

1. Compute EVPI — the maximum value the perfect information could provide (primitive #4). If EVPI < study cost, skip the study.
2. Compute EVSI for the specific study design — account for noise and sample size (#4).
3. If EVSI > study cost, approve. Then apply EU (#1) + risk aversion check (#6) to the post-study decision: does the posterior expected utility exceed the certainty equivalent threshold of the decision maker?
4. If the decision maker exhibits ambiguity aversion over the prior distribution, apply minimax regret (#3) as a robustness check alongside EU.

**Worked example:** Decision: ship feature A or B. Current best estimate: A = $200k value, B = $180k. Uncertainty: P(B actually better) = 0.3; expected regret if wrong = $40k. EVPI = 0.3 × $40k = $12k. Proposed A/B test costs $30k + 6 weeks → EVPI < test cost, skip the test; just ship A. If variance were higher — say P(B better) = 0.6 and regret = $100k — then EVPI = 0.6 × $100k = $60k, which exceeds the $30k cost, so the test pays for itself. EVSI refinement: a study that reduces variance by 60% (e.g. smaller sample, noisier measurement) captures 0.6 · EVPI. In the first scenario: 0.6 × $12k = $7.2k → still below $30k cost, skip. In the second: 0.6 × $60k = $36k > $30k → approve the cheaper, noisier study rather than the full test.

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

1. **VoI gate before each costly call** (#4): estimate EVPI for the decision the LLM call is meant to inform. If the agent's current context already implies a high-confidence action, skip the call — the information cannot change the decision. Apply this gate to retrieval steps (is the retrieved chunk likely to shift the answer?) and to model-tier selection (does this query warrant the 175B model over the 7B?).
2. **Bandit-driven model routing** (#10): treat each LLM backend (or prompt variant) as a bandit arm with unknown quality distribution per query class. Use Thompson sampling to learn the best arm per context cluster; this yields provably-efficient exploration with sub-linear regret across the routing fleet (arXiv:2506.17670, 2026).
3. **Risk aversion on tail latency** (#6): for SLA-sensitive paths, compute the certainty equivalent of the latency distribution — a risk-neutral mean-latency comparison may select a high-variance backend a risk-averse product cannot afford.
4. **Stochastic dominance check before full reallocation** (#11): once enough observations accumulate, verify that the preferred arm FSD-dominates alternatives across quality and cost dimensions before committing the full traffic budget.

---

## Workflow

1. Identify the decision structure: risky choice, ambiguous probabilities, sequential learning, or multi-objective ranking.
2. Use the [Decision Checklist](#decision-checklist) to select the applicable primitive(s).
3. Open the per-primitive playbook in [`assets/templates/decision-theory/`](assets/templates/decision-theory/) for the full definition, inputs, outputs, failure modes, and worked example.
4. For compound decisions, use the [Composition Recipes](#composition-recipes) to stack primitives.
5. Verify inputs: probability estimates, utility function parameters, and criteria weights are the most common failure points.
6. Disclose assumptions explicitly before acting on any MCDA ranking or EU calculation.

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

- Per-primitive playbooks: [`assets/templates/decision-theory/`](assets/templates/decision-theory/) (one file per primitive)
- Composition guide and selection matrix: [`assets/templates/decision-theory/README.md`](assets/templates/decision-theory/README.md)
- Formal theory map: [`references/formal-theory-map.md`](references/formal-theory-map.md)
- Patterns, scenarios, and traps: [`references/patterns-scenarios-traps.md`](references/patterns-scenarios-traps.md)
- Domain-agnostic primitives overview, anti-patterns by decision structure, and checklist: [`references/primitives-overview.md`](references/primitives-overview.md)
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
- Multi-LLM selection via contextual bandits: arXiv:2506.17670 (2026). Online bandit policy for routing queries across LLM backends under unstructured context evolution. [Primitive #10; app-builder recipe]
- Decision-Centric Design for LLM Systems: arXiv:2604.00414 (2026). Formalizes VoI gating and clarify-or-commit tradeoffs as explicit decision problems in LLM orchestration. [Primitive #4; app-builder recipe]
- Numeric thresholds (e.g., EVSI formulas, CE approximations) should be verified against primary sources before citing in decisions.

## Learnings Loop

Before applying this skill on a non-trivial task, read `learnings.consolidated.md` in this directory (and `learnings.md` if present).

After applying it, if you encountered a pattern worth remembering, a mistake worth preventing, or a domain fact that surprised you, append one dated bullet to `learnings.md` via `agents-skills-feedback-loop/scripts/append_learning.py`. Do not modify `SKILL.md` itself.
