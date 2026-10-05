# Nudge Calibration: What to Promise a Board or Product Owner

Read this before forecasting a nudge's effect size, before sizing a test, and before grading a primitive "A" on the strength of a single meta-analysis. It replaces a single second-order synthesis (Hu et al. 2025) with the four studies practitioners actually need, and gives the sample-size arithmetic re-derived with `python3`.

## The four calibration sources

| Source | What it measures | Headline number | Caveat |
|---|---|---|---|
| Mertens et al. 2022, *PNAS* (PMC8740589) | Raw pooled effect across 455 effect sizes, 214 publications, 2.15M participants | d = 0.45 [0.39, 0.52]; defaults d = 0.62 | Uncorrected for publication bias. A correction was later published (it removed retracted Shu 2012 data and fixed coding errors); read the corrected version for the revised pooled d before quoting one. |
| Maier et al. 2022, *PNAS* (PMC9351501) | Same literature, bias-corrected via multiple methods | Overall corrected 0.04 [0.00, 0.14] (BF₀₁ = 0.95, itself undecided). By category: information 0.00 (BF₀₁ 33.8, favors null), **structure 0.12 [0.00, 0.43]** (BF₀₁ 1.12, undecided), assistance 0.01, finance 0.00 (BF₀₁ 41.2, favors null) | "Structure" is the Mertens taxonomy bucket that *includes* defaults, not a defaults-only estimate — do not write "defaults = 0.12". Only information and finance show evidence *for* the null; the rest is undecided, not "no effect". |
| Szaszi et al. 2022, *PNAS* (PMC9351519) | Same debate, meta-scientific framing | "With a few exceptions [e.g., defaults], we see no reason to expect large and consistent effects." | Directional, not a number. |
| DellaVigna & Linos 2022, *Econometrica* 90(1) | 126 RCTs, 23M people, two real nudge units vs. published journal RCTs | As reported in the [author manuscript](https://sdellavi.com/pdf/NudgeToScale2021-04-19.pdf), abstract and §1: 8.7 pp (33.4% relative) in journals vs. **1.4 pp (8.0% relative) at scale** in nudge units; selective publication, exacerbated by low statistical power, explains about 70% of the gap | §1 reports control means of 26.0% (journals) and 17.3% (nudge units); do not recover a baseline by dividing rounded effect estimates. Use this government-service average as contextual calibration, not a promised product lift or a defaults estimate (default-change arms were excluded). |

**Do not use Hu et al. 2025 (JBDM) as the sole correction figure.** It is a second-order meta-analysis of 14 meta-analyses (1,638 studies, ~30M participants; d = 0.27 raw → 0.004 corrected) built mostly on meta-analyses its own authors rate low or critically low quality. Cite it as one more data point, not the calibration anchor — Maier and DellaVigna & Linos are the primary-analysis sources.

## Sample-size arithmetic

**Percentage-point framing (illustrative sizing case).** Assume a 1.4 pp target lift on a 17.5% local baseline (17.5% → 18.9%); this baseline is an example, not DellaVigna & Linos's reported control mean. Assumptions: two-sided α = .05, 1:1 allocation, independent arms. Re-derived with `python3`:

```
h = 2·asin(√0.189) − 2·asin(√0.175) = 0.0363
n/arm = 2·((z_0.975 + z_β) / h)²
  80% power:  n ≈ 11,920/arm  (≈24,000 total)
  90% power:  n ≈ 15,957/arm  (≈32,000 total)

Pooled-variance two-proportion formula (same assumptions):
n/arm = [z_0.975·√(2·p̄(1−p̄)) + z_β·√(p₁(1−p₁) + p₂(1−p₂))]² / (p₂ − p₁)²,  p̄ = 0.182
  80% power:  n ≈ 11,922/arm
  90% power:  n ≈ 15,960/arm
```

Both formulas agree to within a few users; quote ≈12k/arm (80%) or ≈16k/arm (90%).

A one-sample approximation (`n ≈ (z/h)²`) understates this by roughly 2×; use the two-sample formula above for A/B tests.

**Cohen's d framing (continuous-outcome sizing examples).** Choose a minimum useful standardized mean difference for the local outcome; the d-values below are illustrative targets, not a measured production-effect range. Formula: n/arm = 2·((z_0.975 + z_β)/d)², two-sided α = .05, 1:1 allocation.

```
d = 0.10, 80% power → n ≈ 1,570/arm   (90% power → n ≈ 2,101/arm)
d = 0.05, 80% power → n ≈ 6,279/arm
```

A "5,000+ per arm for d ≈ 0.10" figure is inconsistent with this arithmetic: even with a Bonferroni correction across 3 comparisons against control (α = .05/3) the number is ≈2,094/arm (80%) or ≈2,702/arm (90%), well under 5,000.

**Low-n red flag.** A large relative lift in a small pilot needs baseline rates, event counts, uncertainty intervals, and a check for selection or repeated-peeking bias. Neither sample size nor observed d alone proves noise or measurement error. Confirm a selected winner in new data before forecasting rollout impact.

## How to use this in a forecast

1. If the ask is "what lift can we promise," explain that none is guaranteed; for a binary outcome, use percentage points and contextual evidence such as DellaVigna & Linos, then choose a local minimum useful effect.
2. If the ask is "how big must the test be," derive from whichever framing matches the metric (proportion vs. continuous outcome) and re-run the arithmetic — do not copy a cached number across contexts.
3. Grade the underlying primitive from the [Expert Judgment table](../SKILL.md#expert-judgment-reading-evidence-strength), not from this calibration layer alone — Maier says "structure" (which includes defaults) is *undecided* after correction, so do not present a default-opt-out redesign as a guaranteed win.
4. Heterogeneity ("who responds") is a known gap here: Szaszi's directional caveat is the only heterogeneity evidence currently in this skill. Treat subgroup claims as untested until a local pilot confirms them.

## Sources

Maier et al. 2022 — https://pmc.ncbi.nlm.nih.gov/articles/PMC9351501/ · Mertens et al. 2022 — https://pmc.ncbi.nlm.nih.gov/articles/PMC8740589/ · Szaszi et al. 2022 — https://pmc.ncbi.nlm.nih.gov/articles/PMC9351519/ · DellaVigna & Linos 2022 — https://www.econometricsociety.org/publications/econometrica/2022/01/01/rcts-scale-comprehensive-evidence-two-nudge-units · Hu et al. 2025 — https://onlinelibrary.wiley.com/doi/10.1002/bdm.70053.
