# Primitive 05 — Multi-Criteria Decision Analysis (MCDA)

## Definition

Multi-criteria decision analysis (MCDA) provides structured methods for ranking alternatives when objectives are incommensurable — that is, when they cannot all be expressed in a single unit without arbitrary conversion. Key methods:

**Weighted Sum Model (WSM)**:
```
Score(aᵢ) = Σⱼ wⱼ · vⱼ(aᵢ)
```
where wⱼ are criteria weights (Σwⱼ = 1) and vⱼ(aᵢ) is the normalized score of alternative aᵢ on criterion j.

**Analytic Hierarchy Process (AHP)** — weights derived from pairwise comparisons between criteria and between options. Consistency ratio CR < 0.10 indicates acceptable judgement consistency.

**TOPSIS (Technique for Order of Preference by Similarity to Ideal Solution)** — ranks alternatives by their Euclidean distance to the positive-ideal solution and negative-ideal solution in the normalized weighted criteria space.

## When to Use

- Ranking options on criteria that cannot be reduced to a single number (e.g., cost, quality, delivery time, risk, strategic fit).
- Vendor selection, feature roadmap ranking, investment screening, hiring decisions.
- When the decision must be auditable and the trade-offs must be disclosed to stakeholders.

## Inputs

| Input | Description |
|-------|-------------|
| Alternative set {aᵢ} | Options to rank |
| Criterion set {cⱼ} | Objectives; each must be measurable or rateable |
| Weights {wⱼ} | Importance of each criterion; elicited from stakeholders |
| Scores vⱼ(aᵢ) | Performance of each alternative on each criterion |

## Outputs

| Output | Description |
|--------|-------------|
| Ranked alternatives | Ordering by composite score |
| Sensitivity report | How rankings change under weight perturbations |
| Rank-reversal flags | Pairs that swap order under ±20% weight perturbation |

## Failure Modes

- **Hidden weights**: Presenting MCDA output without disclosing weights makes the ranking appear objective. It is not.
- **No sensitivity analysis**: Rankings can reverse under small weight changes. Always perturb weights and report instabilities.
- **AHP consistency ignored**: CR ≥ 0.10 signals inconsistent pairwise judgements; weights derived from inconsistent matrices are unreliable.
- **TOPSIS treated as cardinal**: TOPSIS produces a proximity score between 0 and 1 but that score is not an interval scale. Use it for ranking, not for quantifying "how much better."
- **Criteria not independent**: Correlated criteria effectively double-weight a single underlying objective. Check for collinearity.

## Worked Example

Three cloud vendors evaluated on four criteria:

| Criterion | Weight | Vendor A | Vendor B | Vendor C |
|-----------|--------|----------|----------|----------|
| Cost (lower=better, inverted) | 0.35 | 0.9 | 0.7 | 0.6 |
| Reliability (SLA %) | 0.30 | 0.85 | 0.95 | 0.80 |
| Support quality | 0.20 | 0.7 | 0.8 | 0.9 |
| Integration ease | 0.15 | 0.8 | 0.6 | 0.85 |

WSM scores:
- A: 0.35×0.9 + 0.30×0.85 + 0.20×0.7 + 0.15×0.8 = 0.315 + 0.255 + 0.140 + 0.120 = **0.830**
- B: 0.35×0.7 + 0.30×0.95 + 0.20×0.8 + 0.15×0.6 = 0.245 + 0.285 + 0.160 + 0.090 = **0.780**
- C: 0.35×0.6 + 0.30×0.80 + 0.20×0.9 + 0.15×0.85 = 0.210 + 0.240 + 0.180 + 0.128 = **0.758**

Ranking: A > B > C. Sensitivity check: if reliability weight increases to 0.45 (−0.10 from cost), B overtakes A. Flag this reordering to stakeholders.

## Two Distinct Rank-Reversal Tests

The reordering above is *weight sensitivity* — the ranking moves because a stated preference moved. That is expected behavior and only needs disclosure. A separate and more damaging failure is **rank reversal in the Wang–Triantaphyllou sense**: the ranking changes when the *alternative set* changes, with weights and scores held fixed. Adding a new vendor D, or dropping a clearly dominated one, should not swap A and B. When it does, the method is producing an artifact rather than a preference.

Three standard tests, now operationalized in Scikit-Criteria by Cabral et al. (arXiv:2508.00129):

| Test | Checks | Audited failure rate |
| --- | --- | --- |
| RRT1 | The top alternative survives removal of a non-optimal alternative | ~3.7% (stable in 96.3%) |
| RRT2 | Rankings stay transitive across pairwise subproblems | ~14.8% fail |
| RRT3 | Decomposing into subproblems and recomposing reproduces the full ranking | ~48% fail |

Those rates come from auditing 27 pipeline/dataset combinations drawn from the published MCDM literature — so rank reversal is a routine property of methods in active use, not an adversarial edge case. Normalization choice drives much of it: TOPSIS and VIKOR are known-susceptible, while COMET and SPOTIS are constructed to resist it.

**Practical rule:** run both checks and report them separately. Weight sensitivity is disclosed as a preference boundary; an RRT2/RRT3 failure means the ranking should not be presented as a result at all until the method or normalization is changed.

## Sources

- Saaty, T. L. (1980). The Analytic Hierarchy Process. McGraw-Hill.
- Hwang, C. L. and Yoon, K. (1981). Multiple Attribute Decision Making. Springer.
- Belton, V. and Stewart, T. J. (2002). Multiple Criteria Decision Analysis: An Integrated Approach. Kluwer.
- Wang, X. and Triantaphyllou, E. (2008). "Ranking irregularities when evaluating alternatives by using some ELECTRE methods." Omega 36(1).
- Cabral, J. B. et al. (2025/2026). "Closing a 17-Year Gap: Algorithmic Detection and Empirical Prevalence of Rank Reversal in Multi-Criteria Decision Analysis." arXiv:2508.00129.
