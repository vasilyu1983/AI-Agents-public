# Multiplicity: Holm, BH, BY, and when to use FDR versus FWER

Use this reference when more than one hypothesis feeds a decision. Examples include metrics, slices, variants, prompts, models and repeated looks. Define the family before you look at the data.

## FWER or FDR: choose by the cost of one false claim

| Criterion | Controls | Use when |
|---|---|---|
| FWER (family-wise error rate) | P(at least one false rejection) ≤ α | Each claim triggers an action: a release gate, a safety or regression block, a confirmatory primary-plus-secondary claim, or a claim in a paper. |
| FDR (false discovery rate) | E[false rejections / rejections] ≤ q | Screening many candidates where a few false leads are acceptable and each is followed up: slice discovery, feature screening, or a first pass over dozens of variants. |

A procedure that controls FDR does not protect a gate. If any single false "regression cleared" matters, you need FWER.

## Procedures

- **Holm** [Holm1979]. FWER control under arbitrary dependence.
  - Sort the p-values in ascending order and compare p₍ᵢ₎ with α/(m − i + 1).
  - Stop at the first failure.
  - Holm is uniformly at least as powerful as Bonferroni, so use it as the FWER default.
- **Benjamini–Hochberg (BH)** [BH1995]. FDR control when the p-values are independent or positively dependent (PRDS) [BY2001].
  - Find the largest i with p₍ᵢ₎ ≤ i·q/m and reject every hypothesis up to it.
- **Benjamini–Yekutieli (BY)** [BY2001]. FDR control under arbitrary dependence.
  - Apply BH at q / c(m), where c(m) = Σ 1/i.
  - This is much more conservative. Use it when the dependence sign is unknown, for example overlapping slices or metrics that trade off against each other.
- **e-BH** [WangRamdas2022]. FDR control on e-values under arbitrary dependence. Suits sequential or anytime-valid evidence.
- **Fixed-sequence gatekeeping.** Test each hypothesis at full α in a pre-specified order, and stop testing at the first non-rejection. Opening several parallel secondary tests after a primary rejection needs its own multiplicity procedure; the primary gate alone does not control their FWER. See the [FDA 2017 draft](https://www.fda.gov/media/102657/download), §IV.C.5, for the fixed-sequence construction.

## Worked example (re-derived with python3)

Ten p-values: 0.001, 0.004, 0.006, 0.012, 0.021, 0.030, 0.040, 0.20, 0.50, 0.80. The level is α = q = 0.05.

| Procedure | Rejects | Why |
|---|---|---|
| Bonferroni (0.005 each) | 2 | 0.006 > 0.005 |
| Holm | 3 | Thresholds 0.005, 0.0056, 0.0063, 0.0071… Stops at 0.012 > 0.0071 |
| BH | 6 | 0.030 ≤ 6 × 0.005; 0.040 > 7 × 0.005 = 0.035 |
| BY (c(10) = 2.929) | 1 | Thresholds 0.0017, 0.0034… 0.004 > 0.0034 |

The choice of procedure changes the conclusion by a factor of six on the same data, so pre-register it.

## Dependence traps in eval and experiment work

- Slices that share items, metrics computed from the same users, and prompts evaluated on the same cases are not independent.
- Positive dependence (PRDS) is plausible for one-sided tests on positively correlated statistics. It is not automatic for two-sided tests or for metrics that trade off. When unsure, use Holm for FWER or BY for FDR.
- Selecting the best of k prompts and then testing it on the same data is a multiplicity problem even when only one test is run. Use a held-out confirmation set.

## When not to correct

- Purely descriptive dashboards that make no claims. Label them exploratory instead.
- A single pre-registered primary endpoint that carries the decision. Secondaries are then reported as supportive, not confirmatory.

Sources: see [sources.json](../data/sources.json) IDs Holm1979, BH1995, BY2001, WangRamdas2022.
