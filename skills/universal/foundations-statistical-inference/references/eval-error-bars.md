# Error bars on evals: clustered SEs, paired comparisons, and eval size

Use this reference for inference contracts on benchmark and eval scores. The operational workflow belongs to [ai-evals eval statistics](../../ai-evals/references/eval-statistics.md): the paired analyzer script, McNemar, bootstrap mechanics and the release-gate checklist. Link to it rather than restating it. This file adds the analytic formulas and decision rules from [Miller2024].

## Framing

Treat the eval questions as a sample from a super-population of questions. The target is the model's mean score on that population, not on this fixed list. For a fixed, exhaustive suite with deterministic scoring, report counts, not intervals. [ai-evals](../../ai-evals/references/eval-statistics.md) states the same rule.

## Formulas [Miller2024]

- **Independent questions:** SE = √(Var(s)/n), and the 95% CI is s̄ ± 1.96·SE.
  - With binary scores this reduces to √(s̄(1 − s̄)/n).
  - Using the Bernoulli formula on fractional scores such as F1 is conservative.
- **Clustered questions** (several questions per passage, one question translated into many languages, multi-turn items from one conversation):
  - SE²_clustered = SE²_CLT + (1/n²)·Σ_c Σ_i Σ_{j≠i} (s_{i,c} − s̄)(s_{j,c} − s̄).
  - Report the cluster count next to n.
  - In [Miller v1, Table 4](https://arxiv.org/html/2411.00640v1#S2.T4), the reported clustered-to-naive SE ratios are DROP: “3.05”, RACE-H: “1.10”, and MGSM: “1.88”. These are measured examples, not general correction factors.
- **Paired comparison on shared questions:** analyse d_i = s_{A,i} − s_{B,i}, with SE = √(Var(d)/n).
  - Equivalently, SE_paired = √(SE_A² + SE_B² − 2·SE_A·SE_B·corr(s_A, s_B)).
  - There is also a clustered version on the d_i.
- **Resampling K answers per question:** average the K scores within each question, *then* compute the SE across questions. Pooling all K·n answers as independent is inconsistent.
  - Once E[σ²_i]/K ≪ Var(x), adding more samples per question stops helping.
  - Do not lower the temperature to reduce variance, because it changes the estimand.
- **Eval size:** n = (z_{α/2} + z_β)²·(ω² + σ²_A/K_A + σ²_B/K_B)/δ², where ω² = Var(x_A − x_B) is the variance of the per-question difference in expected scores.

## Worked numbers (re-derived with python3)

| Case | Result |
|---|---|
| SE_A = SE_B = 0.010, corr 0 / 0.5 / 0.8 | SE of the difference = 0.0141 / 0.0100 / 0.0063. Pairing is free precision. |
| ω² = 1/9, δ = 0.03, α = 0.05, power 0.8, K = ∞ | n ≈ 969 questions (matches Miller) |
| Same, but a fixed n = 500 | MDE = 0.042. A 3-point difference is not reliably detectable. |
| Design-effect check, m = 10 items per cluster, ICC = 0.3 | DE = 1 + (m − 1)·ICC = 3.7, so SE × 1.92 |

## Decision rules

- **Identify the independent unit** before computing anything. Items that share a passage, template, conversation, seed document or translation source form a cluster.
- **Always pair** when two systems ran on the same items. Report the per-item correlation alongside the difference.
- **Few clusters** (a rule of thumb of fewer than about 30–50, not from a cited source): cluster-robust SEs are anti-conservative. Use a wild-cluster or cluster bootstrap. The [ai-evals analyzer](../../ai-evals/references/eval-statistics.md) resamples whole clusters. Alternatively, analyse the cluster-level means with a t-interval on G − 1 degrees of freedom.
- **Judge-graded evals** add judge error on top of sampling error. Use [PPI/PPI++](judge-assisted-inference.md) with a random human-labelled subset.
- **Many benchmarks or slices** need a multiplicity rule. See [multiplicity procedures](multiplicity-procedures.md).
- **Leaderboard ties.** If the paired 95% CI of the difference includes 0 and the MDE exceeds the gap, report the models as not distinguished. Do not rank them.

## When not to use these formulas

- Scores that are not approximately a mean of i.i.d. or cluster-i.i.d. units. Examples are Elo/Bradley–Terry ratings, pass@k computed from a fixed sample budget, and ranking metrics with cross-item dependence. Use an estimator-specific interval or a design-respecting bootstrap.
- Contaminated or saturated benchmarks. The error bar is then precise about the wrong construct. See [measurement theory](../../foundations-measurement-theory/SKILL.md).

Source: [Miller2024] Evan Miller, *Adding Error Bars to Evals: A Statistical Approach to Language Model Evaluations*, arXiv:2411.00640 (2024). The equations and the n ≈ 969 example are from v1; the measured SE ratios are quoted with their Table 4 source above.
