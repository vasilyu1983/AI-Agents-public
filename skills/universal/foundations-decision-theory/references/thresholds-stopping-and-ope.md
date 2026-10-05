---
description: Decision rules for cost-based thresholds and abstention, pick-the-winner stopping (best-arm identification, expected loss), and off-policy evaluation before switching a routing or bandit policy.
status: stable
---

# Thresholds, Stopping, and Off-Policy Evaluation

Read this when a probability must become an action (approve / block / escalate / abstain), when a team asks "do we ship the leading variant now", or when a new routing, ranking, or bandit policy must be judged from logs before rollout. Sources are in [`../data/sources.json`](../data/sources.json).

## 1. Cost-sensitive thresholds

**Rule.** With a calibrated probability p that the item is positive (bad, fraudulent, wrong), and costs c_FN for letting a positive through and c_FP for blocking a negative, act ("block") when

```text
p > p* = c_FP / (c_FP + c_FN)
```

This is the Bayes decision for a two-action, two-state loss matrix (Elkan 2001 gives the general cost-matrix form). Example: blocking a good transaction costs 5, passing a fraud costs 200, so p* = 5/205 ≈ 0.024. Block anything above 2.4% risk, not above 50%.

**Conditions that decide whether the rule is valid:**

- **Calibration is the input contract.** A threshold on an uncalibrated score (raw LLM confidence, a ranker logit, a verbalised "90% sure") is not this rule. Estimate calibration on held-out outcomes first ([foundations-statistical-inference](../../foundations-statistical-inference/SKILL.md)); validate the score itself with [foundations-measurement-theory](../../foundations-measurement-theory/SKILL.md).
- **Prevalence shift moves the posterior, and so the decision.** If the base rate at deployment (π′) differs from the calibration set (π), reweight before thresholding: multiply the odds by (π′/π)/((1−π′)/(1−π)) (Saerens, Latinne & Decaestecker 2002, who also give an EM estimate of π′ when it is unknown). Example: p = 0.02 calibrated at π = 5% becomes ≈ 0.004 at π′ = 1%.
- **Costs are rarely a point.** When c_FN/c_FP is contested, report the decision across a cost-ratio range. Decision curves plot net benefit against threshold probability for exactly this purpose (Vickers & Elkin 2006).
- **Capacity limits change the rule.** If only N items per day can be reviewed, the operating point is "top-N by expected cost saved", not p*.

## 2. Abstention (reject option)

**Rule (Chow 1970).** Add a third action, "defer to a human / ask / abstain", with cost c_r. Pick the action with the lowest expected cost:

```text
approve: p · c_FN      block: (1 − p) · c_FP      defer: c_r
```

Deferral is used only when c_r is below both. Example: c_FN = 200, c_FP = 5, c_r = 2 gives approve for p ≤ 0.01, defer for 0.01 < p < 0.6, block for p ≥ 0.6. If c_r ≥ c_FP·c_FN/(c_FP+c_FN) (≈ 4.9 here), deferral is never optimal.

- **Selective prediction** trades coverage for risk: choose the confidence cut that meets a target error on the accepted set with a stated confidence (Geifman & El-Yaniv 2017). Report risk *and* coverage; a 99% accurate system that answers 10% of cases is a different product.
- **Do not abstain on model uncertainty the human cannot resolve.** Deferral pays only when the reviewer has information or authority the model lacks. Otherwise it only adds cost.
- Applied recipes already exist: two-threshold act/abstain for eval gates in [ai-evals threshold-derivation](../../ai-evals/references/threshold-derivation.md), operating-point choices in [ai-ml-data-science evaluation-patterns](../../ai-ml-data-science/references/evaluation-patterns.md), and the RAG pattern in [ai-rag abstention-recipe](../../ai-rag/references/abstention-recipe.md). This section owns the decision rule; those files own the domain wiring.

## 3. Best-arm identification vs regret

Two different objectives are often mixed up:

| Objective | You care about | Algorithms | Stop when |
|---|---|---|---|
| **Regret minimisation** | Reward collected *during* the experiment (ads, live routing) | UCB, Thompson sampling ([template 10](../assets/templates/decision-theory/10-multi-armed-bandit.md)) | Never, as an ongoing policy; cumulative regret grows (O(log T) for UCB1 on stochastic arms). It is not bounded |
| **Best-arm identification (pure exploration)** | Committing to the right winner *after* the test | Fixed-confidence or fixed-budget BAI (Audibert, Bubeck & Munos 2010); top-two Thompson sampling (Russo 2016) | A declared confidence or budget is reached, or expected loss falls below the threshold of caring (§4) |

"Pick the winner among four prompt variants" is BAI, not regret minimisation. Running a regret-minimising bandit starves the runner-up arms, so it identifies the winner more slowly.

**When not to use a bandit at all.** Use a fixed-allocation randomised test when:

- you need an unbiased effect size;
- the decision metric is long-horizon or a guardrail (retention, complaints);
- rewards are delayed.

Adaptive allocation biases naive per-arm means. Valid confidence intervals after a bandit need adaptively weighted estimators (Hadad et al. 2021). Hand inference to [foundations-statistical-inference](../../foundations-statistical-inference/SKILL.md).

## 4. Expected-loss stopping

**Rule.** Declare a threshold of caring ε in the metric's units before the test. Choose the arm with the smallest posterior expected loss, E[max_j θ_j − θ_i]. Stop and ship when that loss is below ε. This is the rule described in Stucchio's 2015 VWO whitepaper.

Why not "P(best) > 0.99"? Probability of being best ignores magnitude. When two arms are nearly identical it can stay low forever, even though choosing either costs almost nothing. It can also clear 0.99 on a difference too small to matter. Template 10's posteriors (Beta(9,13), Beta(5,15), Beta(4,10); numerical integration) give P(best) = 0.716 / 0.094 / 0.190 and expected loss 0.026 / 0.185 / 0.15 CTR. With ε = 0.005 CTR you keep testing. With ε = 0.03 you ship A now, although P(A best) is only 0.72.

**Caveats:**

- Expected loss inherits the prior and model. Report it next to the posterior of the effect.
- Bayesian stopping is not immune to optional-stopping effects on frequentist error rates. If you must also report a p-value, use an anytime-valid method (statistical-inference).
- Guardrail metrics still need their own non-inferiority check. A small expected loss on the primary metric does not clear a guardrail.

## 5. Off-policy evaluation (OPE) before switching a policy

Use OPE when a new router, ranker, or bandit policy π_new is to be judged from logs collected under π_old, before any online exposure.

| Estimator | Idea | Failure mode |
|---|---|---|
| **IPS** | Reweight each logged reward by π_new(a\|x)/π_old(a\|x) | Unbiased only with correct logged propensities; variance explodes when the ratio is large |
| **SNIPS** (Swaminathan & Joachims 2015) | Normalise IPS by the sum of weights | Small bias, much lower variance; still needs overlap |
| **Doubly robust** (Dudík, Langford & Li 2011) | Reward model + IPS correction | Accurate if either the reward model or the propensities are good. Not a fix for missing overlap |
| **Replay** (Li et al. 2011) | Keep only logged events where π_new picks the logged action, with uniformly random logging | Unbiased under uniform logging; wastes most data otherwise |

**Hard requirements:**

- **Log propensities at decision time.** You cannot reconstruct π_old(a|x) later from a deterministic router, and a deterministic logging policy gives zero overlap for any action it never takes.
- **Reserve exploration traffic.** Keep a small randomised share (for example ε-uniform) so that future policies have support.
- **Handle weight tails explicitly.** Clip or truncate large weights and report both the bias this trades and the effective sample size. Do not report a single IPS point estimate.
- **Validate the estimate.** Treat OPE as a screening step. Confirm the chosen policy with a fixed-allocation online test sized by the value-of-information calculation ([template 04](../assets/templates/decision-theory/04-value-of-information.md)).

The propensity, overlap, and doubly-robust logic is shared with observational causal inference. See [foundations-causal-inference propensity-score template](../../foundations-causal-inference/assets/templates/causal-inference/08-propensity-score.md) for overlap diagnostics and DR conditions.

## Exit checks

- [ ] The threshold is derived from stated costs and calibrated probabilities, and deployment prevalence is checked.
- [ ] Abstention has an explicit cost and a reviewer who can actually resolve the case.
- [ ] The objective is declared as regret or best-arm identification before choosing an algorithm.
- [ ] The stopping rule is expected loss against a pre-declared ε, and guardrails are checked separately.
- [ ] Before OPE: propensities are logged, overlap is reported, weight clipping is disclosed, and online confirmation is planned.
