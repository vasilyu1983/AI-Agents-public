---
description: Designs consumers hit when the 12 canonical primitives do not fit - interrupted time series, off-policy evaluation from logs, surrogate index for long-term outcomes, partial-identification bounds, negative controls and proximal inference.
status: stable
---

# Beyond the Canonical 12: Designs for the Cases Product, Eval and Agent Teams Actually Hit

Read this when the question is one of these:

- "We shipped to everyone on one date and nothing is comparable."
- "Evaluate a new router or ranking policy from logged traffic."
- "The test runs for 2 weeks, but the decision metric is 90-day retention."
- "Some runs crashed or timed out, and not equally in both arms."
- "We cannot measure the confounder."

## Contents

- [Pick the design from the symptom](#pick-the-design-from-the-symptom)
- [Interrupted time series (ITS) and BSTS](#interrupted-time-series-its-and-bsts)
- [Off-policy evaluation from logged data](#off-policy-evaluation-from-logged-data)
- [Surrogate index for long-term outcomes](#surrogate-index-for-long-term-outcomes)
- [Partial identification: bounds instead of a point](#partial-identification-bounds-instead-of-a-point)
- [Negative controls and proximal inference](#negative-controls-and-proximal-inference)
- [Sources](#sources)

## Pick the design from the symptom

| Symptom | Design | Use a canonical primitive instead when |
|---|---|---|
| One series, a known intervention date, no untreated comparison units | ITS / BSTS (CausalImpact) | Comparable untreated units exist. Use synthetic control or SDiD (#7) or DiD (#6), which difference out concurrent shocks and ITS cannot |
| A new policy (router, ranker, bandit, prompt selector) must be judged from logs made by the old policy | Off-policy evaluation (OPE) | The change is a single fixed switch with no per-request action choice. Then it is an ordinary treatment effect (#8) |
| Randomized test, but the decision outcome arrives months later | Surrogate index | The long-term outcome can be waited for at acceptable cost, or no historical data link the surrogates to the outcome |
| Outcomes missing or censored differently by arm (attrition, timeouts, crashes, opt-outs) | Lee bounds (randomized) / Manski bounds (no assumptions) | Missingness is plausibly unrelated to potential outcomes and you can defend that. Then use weighting or imputation, with sensitivity analysis |
| A confounder is known but unmeasured, and proxies for it exist | Negative controls to detect it; proximal inference to adjust for it | A valid instrument (#4) or threshold (#5) exists. Design beats proxy modelling |

## Interrupted time series (ITS) and BSTS

**Estimand.** The post-intervention gap between the observed series and a forecast of the series without the intervention. It is identified only if nothing else that affects the outcome changed at the intervention date.

**Decision rules**

- **Model the pre-period structure before reading the gap.** Model trend, seasonality (weekly, monthly, holidays) and autocorrelation. Ordinary least squares standard errors on autocorrelated daily data understate uncertainty. Use segmented regression with autocorrelation-robust errors or an explicit time-series model (Lopez Bernal, Cummins & Gasparrini 2017).
- **Pre-specify the impact shape.** State whether you expect a level step, a slope change or a lagged ramp. Choosing the shape after looking at the post-period is a forking-paths error.
- **Use control series with care.** BSTS/CausalImpact (Brodersen et al. 2015) builds the counterfactual from covariate series. It assumes those series are unaffected by the intervention and keep a stable pre-period relationship with the outcome. A covariate that the launch moved, such as sitewide traffic after a homepage change, biases the estimate toward zero.
- **Run placebo dates.** Re-run the model at several fake intervention dates in the pre-period. If fake dates produce gaps as large as the real one, report "not distinguishable from normal variation".

**Failure modes specific to product and agent systems**

- **Concurrent change.** The same release changed tracking, logging, the eval harness or the judge model. ITS then measures the instrumentation change. Check the deploy log for anything else that shipped in the window.
- **Anticipation and novelty.** Pre-launch marketing moved the pre-period, or a novelty spike decays. Report the effect over time, not one average.
- **Seasonality aliasing.** A launch on a holiday or at a month boundary coincides with a seasonal break. Fit at least one full seasonal cycle before the date. If the pre-period cannot show that cycle, say that the effect is not separable from the season.

**When NOT to use ITS.** Do not use it when donor units exist; synthetic control or SDiD is strictly more credible. Do not use it when the intervention date is fuzzy, as with a gradual ramp and no recorded exposure. Do not use it when the pre-period is shorter than the seasonality you must model.

## Off-policy evaluation from logged data

Decision-theory owns the estimator table (IPS, SNIPS, doubly robust) and the rule for acting on the result: [foundations-decision-theory thresholds-stopping-and-ope](../../foundations-decision-theory/references/thresholds-stopping-and-ope.md#5-off-policy-evaluation-ope-before-switching-a-policy). This section owns the identification conditions those estimators assume.

**Estimand.** The expected reward V(π_new) = E_x E_{a~π_new(·|x)}[r(x,a)], estimated from logs of (x, a, r, π_old(a|x)).

**Identification conditions (check them before choosing an estimator)**

1. **Logged propensities.** π_old(a|x) must be recorded at decision time. You cannot recover it later from a deterministic router. Refitting a propensity model to the logs turns OPE into observational causal inference and inherits its unmeasured-confounding problem (#8, #12).
2. **Support (positivity).** Every action π_new takes with positive probability must have positive logging probability in the same context. A deterministic logger gives zero support for every action it never chose, and no estimator repairs that. The fix is randomized exploration in the logging policy.
3. **No unlogged confounding of the reward.** The reward must depend only on (x, a) plus noise. Anything that drove both the old action and the reward, such as an on-call override or a manual escalation, must be in x.
4. **Stable reward and context.** The reward process and the context distribution must be the same at deployment as in the logs. Model or judge upgrades, traffic-mix shifts and feedback loops break this.

**Diagnostics to report**

- The effective sample size of the importance weights, ESS = (Σw)² / Σw², next to the raw log count.
- The share of π_new's probability mass on actions with small logging probability.
- The weight-clipping or self-normalization rule and how much it moved the estimate.

**When NOT to use OPE**

- **Slate or long-horizon actions.** Examples are multi-step agent trajectories and full ranked lists. Importance weights multiply across steps, and variance explodes. Use structure-exploiting estimators or go online.
- **LLM-judge rewards.** The reward model's bias is shared by the direct-method and DR estimators. Validate the judge against human labels before the OPE.
- **As the decision itself.** OPE is a screening step. Confirm online, as decision-theory specifies.

## Surrogate index for long-term outcomes

**What it does.** Athey, Chetty, Imbens & Kang combine several short-term outcomes into a surrogate index: the predicted long-term outcome given the surrogates. The index is fitted on an observational or historical sample where the long-term outcome is observed. The index is then applied to the short experiment. Under their assumptions, the treatment effect on the index equals the treatment effect on the long-term outcome.

**The two assumptions that carry the result**

1. **Surrogacy.** Given the surrogates, the long-term outcome is independent of treatment. Every causal path from the treatment to the long-term outcome runs through the measured surrogates.
2. **Comparability.** The relationship between surrogates and outcome in the fitting sample also holds in the experimental population.

**Decision rules**

- **Validate the index against history.** Use past experiments where the long-term outcome was eventually observed. Report how often the index predicted the sign and rough size of the realized long-term effect. With no such history, label the index "unvalidated".
- **Use many qualitatively different surrogates.** Surrogacy is more plausible with many distinct surrogates, such as engagement, revenue, support contacts and feature adoption, than with a single proxy metric.
- **Watch for treatments that act after the surrogate window.** Price changes, billing-cycle effects, delayed churn and trust erosion act through paths that 2-week surrogates do not capture. Surrogacy is least credible for exactly these decisions.
- **Keep a holdout.** A long-running holdout on the real outcome audits the index.

**When NOT to use it.** Do not use it for novel treatment types unlike anything in the fitting data. Do not use it when the treatment plausibly changes the surrogate-to-outcome relationship itself, such as a feature that inflates engagement without adding value. Do not use it when the fitting sample comes from a different population or era.

## Partial identification: bounds instead of a point

Use bounds when point identification needs an assumption you cannot defend. Report an honest interval rather than a precise wrong number.

- **Manski (1990) worst-case bounds.** Missing potential outcomes are filled with the extreme possible values of a bounded outcome. They need only that bound. Without further assumptions, the ATE bounds always contain zero, and for a binary outcome they have width 1. Their value is a floor. Add explicit monotonicity or monotone-instrument assumptions to narrow them, and name each assumption.
- **Lee (2009) bounds.** These fit a randomized experiment where outcomes are observed only for units that "survive" (respond, complete, do not time out) and survival differs by arm. Trim the arm with the higher survival rate by the excess share, from the top and then from the bottom, to get sharp bounds for the always-observed subpopulation. The key assumption is monotonicity: treatment moves selection in only one direction for everyone.
  - **Eval-harness case.** A new agent version times out on 8% of tasks and the old one on 3%. Comparing scores on completed tasks alone compares different task mixes. Lee bounds, or scoring timeouts as failures, keep the comparison causal.
- **Report both ends.** Report both bounds and the assumption that produced them. If the interval spans the decision threshold, the data do not settle the decision. Route to foundations-decision-theory for choosing under that ambiguity.

## Negative controls and proximal inference

- **Negative-control outcome.** Pick an outcome the treatment cannot affect but that shares the suspected confounders. An example is pre-launch activity for users who later adopt a feature. A non-null "effect" on it detects confounding or bias.
- **Negative-control exposure.** Pick an exposure that cannot affect the outcome but shares the confounders. An example is a feature that was exposed but never used. It serves the same detection purpose (Lipsitch, Tchetgen Tchetgen & Cohen 2010).
- **Use them to detect bias first.** A clean negative control is evidence, not proof, of no confounding. It checks only the confounding paths it shares.
- **Proximal causal inference.** This goes one step further. With a treatment-side proxy and an outcome-side proxy of the unmeasured confounder that meet the framework's conditions, the effect can be identified by the proximal g-formula (Tchetgen Tchetgen et al., arXiv:2009.10982). These conditions are strong and hard to check. Treat proximal estimates as a sensitivity check alongside a design-based estimate, not as a replacement for one. Tooling maturity is not verified here; check the current state before relying on a package.

## Sources

- Lopez Bernal, Cummins & Gasparrini (2017). Interrupted time series regression for the evaluation of public health interventions: a tutorial. *International Journal of Epidemiology* 46(1), 348–355. doi:10.1093/ije/dyw098
- Brodersen, Gallusser, Koehler, Remy & Scott (2015). Inferring causal impact using Bayesian structural time-series models. *Annals of Applied Statistics* 9(1), 247–274. doi:10.1214/14-AOAS788
- Dudík, Langford & Li (2011). Doubly Robust Policy Evaluation and Learning. ICML 2011.
- Swaminathan & Joachims (2015). The Self-Normalized Estimator for Counterfactual Learning. NeurIPS 2015.
- Athey, Chetty, Imbens & Kang. The Surrogate Index: Combining Short-Term Proxies to Estimate Long-Term Treatment Effects More Rapidly and Precisely. *Review of Economic Studies* 93(4), 2284–2312. doi:10.1093/restud/rdaf087; NBER w26463.
- Manski (1990). Nonparametric Bounds on Treatment Effects. *AER Papers & Proceedings* 80(2), 319–323.
- Lee (2009). Training, Wages, and Sample Selection: Estimating Sharp Bounds on Treatment Effects. *Review of Economic Studies* 76(3), 1071–1102. doi:10.1111/j.1467-937X.2009.00536.x
- Lipsitch, Tchetgen Tchetgen & Cohen (2010). Negative Controls: A Tool for Detecting Confounding and Bias in Observational Studies. *Epidemiology* 21(3), 383–388. doi:10.1097/EDE.0b013e3181d61eeb
- Tchetgen Tchetgen, Ying, Cui, Shi & Miao (2020). An Introduction to Proximal Causal Learning. arXiv:2009.10982
