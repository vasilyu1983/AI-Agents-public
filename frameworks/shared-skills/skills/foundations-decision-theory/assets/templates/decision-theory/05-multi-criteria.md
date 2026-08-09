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

Ranking: A > B > C. Sensitivity check: if reliability weight increases to 0.45 (−0.10 from cost), B overtakes A. Flag this rank-reversal to stakeholders.

## Sources

- Saaty, T. L. (1980). The Analytic Hierarchy Process. McGraw-Hill.
- Hwang, C. L. and Yoon, K. (1981). Multiple Attribute Decision Making. Springer.
- Belton, V. and Stewart, T. J. (2002). Multiple Criteria Decision Analysis: An Integrated Approach. Kluwer.
