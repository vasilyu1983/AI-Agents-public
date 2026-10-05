# A/B test craft: validity checks, variance, ratio metrics, and stopping

Use this reference for online controlled experiments: significance of an uplift, sample size, peeking, and "can we ship?". Channel and funnel workflow belongs to marketing-cro, marketing-product-analytics and ai-evals online evaluation. This file owns the inference rules.

## Contents

- [1. Validity gates](#1-validity-gates-in-order-before-reading-any-effect)
- [2. CUPED](#2-variance-reduction-cuped--regression-adjustment)
- [3. Delta method](#3-ratio-metrics-the-delta-method)
- [4. Heavy tails](#4-heavy-tails-and-outliers)
- [5. Stopping designs and peeking](#5-stopping-pick-one-design-before-launch)
- [6. After the test](#6-after-the-test)

## 1. Validity gates, in order, before reading any effect

1. **Sample-ratio mismatch (SRM).**
   - Run a chi-square goodness-of-fit test of the observed assignment counts against the configured split.
   - One published platform uses a conservative p < 0.0005. It reports SRM in about 6% of A/B tests at Microsoft and about 10% of a zoomed-in set at LinkedIn [Fabijan2019].
   - An SRM invalidates the readout. Find the cause (assignment, logging, bot filtering, redirect loss) before interpreting any metric.
   - *Worked:* a 50.8/49.2 split on 10,000 users gives χ² = 2.56, p = 0.11, which passes. The same split on 100,000 users gives χ² = 25.6, p = 4.2e-7, which fails. A split that looks small becomes decisive at scale.
2. **Randomization unit equals analysis unit.** Randomize by user and analyse per user, or use the delta method (§3). Treating sessions, page views or tokens as independent when users were randomized understates the SE (pseudo-replication).
3. **A/A evidence.** The platform's A/A false-positive rate should be close to α. If it is not, the variance estimator or the assignment is broken.
4. **Novelty and primacy.** Early lift from novelty can fade, and a change in a learned workflow can dip first and then recover. Plot the effect by exposure day or cohort and do not extrapolate a week-1 effect [Kohavi2020].

## 2. Variance reduction: CUPED / regression adjustment

- **Adjustment:** Y_adj = Y − θ(X − mean(X)), where X is a pre-experiment covariate (usually the same metric in the pre-period) and θ = Cov(Y, X)/Var(X).
- **Effect:** the variance falls by a factor (1 − ρ²), where ρ = corr(Y, X) [Deng2013].
- **Worked:**

  | ρ | Variance factor | Equivalent sample multiplier |
  |---|---|---|
  | 0.3 | 0.91 | 1.10× |
  | 0.5 | 0.75 | 1.33× |
  | 0.8 | 0.36 | 2.78× |

**Rules:**

- The covariate must be unaffected by treatment. Pre-period data is safe; anything measured post-assignment is not.
- Use the pooled θ across arms, and fix the covariate choice before looking at results.
- For new users with no pre-period data, set X to 0 and add a has-history indicator. This is a design convention, not from [Deng2013].

## 3. Ratio metrics: the delta method

Metrics such as CTR per session, revenue per session and tokens per task are ratios of two per-user sums, randomized by user. The per-user pairs (C_u, S_u) are independent across users; the sessions are not.

- Var(C̄/S̄) ≈ [Var(C) − 2R·Cov(C, S) + R²·Var(S)] / (n·μ_S²), where R = μ_C/μ_S [Deng2018].
- *Worked:* n = 10,000 users, μ_S = 5 sessions, μ_C = 1 click, Var(S) = 16, Var(C) = 2.25, Cov = 4.2.
  - Delta-method SE = 0.00220.
  - A naive session-level binomial SE = 0.00179, about 19% too small here (the correct SE is 1.23× the naive one).
  - The gap grows with heterogeneity in sessions per user.
- The equivalent alternative is a user-level cluster-robust regression, or a bootstrap over users.

## 4. Heavy tails and outliers

- Revenue-type metrics can make the mean's SE unstable.
- Pre-register capping or winsorization (for example at a high percentile of control), or a trimmed or quantile estimand.
- State that the estimand changed. A capped-revenue lift is not a revenue lift.
- Never choose the cap after seeing results.

## 5. Stopping: pick one design before launch

| Design | Use when | Cost | Guarantee |
|---|---|---|---|
| Fixed horizon | You can commit to one analysis at a pre-computed n | None; the most power for that n | Only if nobody acts on interim looks |
| Group sequential, alpha spending [LanDeMets1983] | A few planned interim looks (for example weekly) with the option to stop early for large effects or harm | Small inflation of maximum n; the O'Brien–Fleming shape costs little power | Type I error ≤ α at the planned looks; the look times can vary if you use a spending function |
| Always-valid: mSPRT, confidence sequences, e-processes [Johari2022; Howard2021; Ramdas2023] | Continuous monitoring, dashboards, or unknown stopping times | Wider at any fixed n than a fixed-horizon test | p-values and intervals valid at every n under optional stopping |

**Group sequential (O'Brien–Fleming-like spending):**

- The spending function is α(t) = 2 − 2Φ(z_{α/2}/√t) [LanDeMets1983].
- *Worked,* two-sided α = 0.05, with cumulative α spent at each information fraction:

  | Information fraction | Cumulative α spent |
  |---|---|
  | 0.25 | 0.00009 |
  | 0.50 | 0.0056 |
  | 0.75 | 0.0236 |
  | 1.00 | 0.05 |

- Almost nothing is spent early, so a final analysis at the planned n is close to a fixed-horizon test.
- Pocock-like spending (α·ln(1 + (e − 1)t): 0.018 / 0.031 / 0.041 / 0.05) spends more early and costs more at the end.

**mSPRT (normal data, normal mixture with variance τ² around θ₀):**

- Λ_n = √(σ²/(σ² + nτ²)) · exp(n²τ²(x̄ − θ₀)² / (2σ²(σ² + nτ²))).
- Reject when Λ_n ≥ 1/α.
- The always-valid p-value is p_n = min(p_{n−1}, 1/Λ_n). This follows from the test–p-value correspondence of [Johari2022], Theorem 1.
- The closed form was checked against numerical integration.
- τ is a tuning choice. Set it from the effect sizes you expect, not from the data.

**e-values:**

- Use them to combine evidence across sequential batches or across experiments by multiplication (for independent e-values) or by averaging (for arbitrary dependence) [VovkWang2021].
- e-BH controls FDR over e-values under arbitrary dependence [WangRamdas2022].

**Peeking penalty:**

- Checking a fixed-horizon z-test at 5 equally spaced looks and stopping at the first |z| > 1.96 gives a false-positive rate of about 14.2%, not 5%. This is a simulation of 200,000 null runs with seed 20260923 and MCSE 0.08 pp.

**Already peeked?**

- Label the result exploratory. Do not report the stopped p-value as confirmatory.
- Either run a confirmation on fresh traffic, or re-analyse with an always-valid method computed from t = 0 over all the data you saw. The always-valid result is honest but wider.
- Record the looks that actually happened.

## 6. After the test

- **Winner's curse.** The effect of a variant selected because it won is biased upward. Expect shrinkage on rollout, and shrink toward the prior (hierarchical or empirical Bayes) when you report many experiments.
- **Many metrics or variants.** Choose FWER or FDR as in [multiplicity procedures](multiplicity-procedures.md), and declare one primary metric before launch.
- **Ship decision.** Compare the interval with the pre-declared minimum meaningful effect or non-inferiority margin, not with zero alone.

Sources: see [sources.json](../data/sources.json) IDs Fabijan2019, Kohavi2020, Deng2013, Deng2018, LanDeMets1983, OBrienFleming1979, Johari2022, Howard2021, Ramdas2023, VovkWang2021, WangRamdas2022.
