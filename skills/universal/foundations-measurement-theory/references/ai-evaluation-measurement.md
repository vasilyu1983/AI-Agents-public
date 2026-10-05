# AI evaluation measurement

Read this when an LLM benchmark score, LLM-judge score, or eval-suite trend is used to support a claim about a capability. It covers the psychometric concepts that the operational eval guidance does not: facets and generalizability, linking across versions, IRT and DIF for benchmark items, saturation, and a construct-validity checklist.

## Contents

- [Ownership boundary](#ownership-boundary)
- [Facets and generalizability (G-theory)](#facets-and-generalizability-g-theory)
- [Linking after an instrument change](#linking-after-an-instrument-change)
- [IRT and DIF for benchmark items](#irt-and-dif-for-benchmark-items)
- [Saturation and ceiling effects](#saturation-and-ceiling-effects)
- [Construct-validity checklist for a benchmark claim](#construct-validity-checklist-for-a-benchmark-claim)
- [Neuro and biometric instruments](#neuro-and-biometric-instruments)

## Ownership boundary

This file owns the measurement concepts. Operational controls stay in [ai-evals](../../ai-evals/SKILL.md). Do not restate them here:

- Judge bias catalog and controls: [llm-judge-bias.md](../../ai-evals/references/llm-judge-bias.md).
- Kappa and agreement procedure and threshold derivation: [threshold-derivation.md](../../ai-evals/references/threshold-derivation.md) and [advanced-judging.md](../../ai-evals/references/advanced-judging.md). The latter also has an experimental IRT judge-calibration diagnostic.
- Contamination, leakage and flake controls: [flake-and-reproducibility.md](../../ai-evals/references/flake-and-reproducibility.md).
- Bootstrap CIs, paired tests and power: [eval-statistics.md](../../ai-evals/references/eval-statistics.md) and [statistical inference](../../foundations-statistical-inference/SKILL.md).

**When NOT to use this file:** a fixed, deterministic regression suite used only as a pass/fail gate for the same system. It needs flake control, not G-theory, IRT, DIF or linking. Use it only when a score is interpreted as a capability, compared across groups or versions, or used to pick between systems.

## Facets and generalizability (G-theory)

A score from an LLM pipeline depends on more than the item. Name each facet over which you want the conclusion to generalize:

| Facet | Typical levels | Question it answers |
|---|---|---|
| Item / task | Benchmark items, eval cases | Does the result hold for other tasks from the same domain? |
| Judge / rater | Judge models, human raters, rubric versions | Does it hold for another acceptable scorer? |
| Prompt template | Paraphrased instructions, answer order | Does it hold for other reasonable wordings? |
| Seed / repeat | Sampling repeats at a fixed configuration | Is it more than call-to-call noise? |
| Occasion / version | Model or API snapshot, date | Does it hold after silent provider changes? |

Procedure:

1. **G-study.** Run a crossed design on a pilot: every object of measurement (answer, or system) × every level of each facet you intend to generalize over. Estimate variance components for the object, each facet, and their interactions ([Brennan 2001](https://doi.org/10.1007/978-1-4757-3456-0)).
2. **Decide what is fixed.** A facet you will never vary in use, such as a single frozen judge, is fixed. Its variance is not error, but the conclusion is then restricted to that level. State the restriction.
3. **D-study.** Project the dependability of alternative designs (numbers of templates, repeats, judges, items) from the components, then choose the cheapest design that meets the decision's precision need. Use relative error for rankings and absolute error for pass/fail against a cutoff.

Synthetic D-study (invented components; re-derived with python3): answers `p` crossed with templates `t` and repeats `r`. σ²(p) = 0.50, σ²(pt) = 0.20, σ²(pr) = 0.05, σ²(ptr,e) = 0.25. The relative error is σ²(pt)/n_t + σ²(pr)/n_r + σ²(ptr,e)/(n_t·n_r), and the generalizability coefficient is σ²(p) / (σ²(p) + relative error).

| Templates | Repeats | Calls per answer | Relative error | Eρ² |
|---|---|---|---|---|
| 1 | 1 | 1 | 0.500 | 0.500 |
| 1 | 4 | 4 | 0.275 | 0.645 |
| 3 | 1 | 3 | 0.200 | 0.714 |
| 3 | 2 | 6 | 0.133 | 0.789 |
| 5 | 1 | 5 | 0.140 | 0.781 |

When the answer × template interaction is large, 3 templates × 1 call beats 1 template × 4 calls. Repeating a single prompt cannot remove template variance. The components are illustrative, so estimate your own before choosing a design.

Evidence that ignoring facets misstates precision. Both are unrefereed preprints; cite them as single-study results, not general magnitudes:

- Messing (2026, [arXiv 2604.11581](https://arxiv.org/abs/2604.11581)) reports that across its demonstrations "naive standard errors are 40 - 60% smaller" than SEs that account for judge, temperature and prompt variance.
- Feng et al. (2026, [arXiv 2608.16253](https://arxiv.org/abs/2608.16253)) show the plug-in prompt-instability estimate is "biased upward at finite repeat budgets". A crossed prompt × answer-order design separates prompt, order, interaction and residual variance.

## Linking after an instrument change

A judge swap, rubric edit, prompt change or benchmark v2 creates a new instrument. Old and new scores are on different scales until they are linked ([Kolen & Brennan 2014](https://doi.org/10.1007/978-1-4939-0317-7)).

- **Common-object design.** Score an overlap sample of answers, or run the same systems, with both instruments. Link on the overlap and report linking error.
- **Common-item (anchor) design.** Keep a set of unchanged anchor items across benchmark versions. Check the anchors themselves for drift, such as contamination, parameter change or ceiling, before trusting them.
- **High correlation is not a link.** Old and new judges can correlate highly while one is systematically more lenient, or lenient only on one slice. Check the offset, the slope and the slice-level agreement.
- **Without a bridge, the trend is broken.** Label continuity conditional or insufficient, keep the old series with its provenance, and never silently rescore history. See [comparability and drift](comparability-and-drift.md).

## IRT and DIF for benchmark items

Item response theory models each item's difficulty and discrimination and each system's latent ability. Two practical consequences:

- **Information is local.** An item informs most near the ability level where it discriminates. Items that every frontier system passes add almost nothing at the frontier.
- **Subsets and adaptive selection are possible, under conditions.** The calibration sample of prior systems must span the new system's ability. Item parameters can drift as model generations change. The subset must preserve the construct, not just reproduce a ranking.

Evidence, scoped to what each abstract states:

- tinyBenchmarks ([Polo et al. 2024](https://arxiv.org/abs/2402.14992)): for MMLU (14K items) "it is sufficient to evaluate this LLM on 100 curated examples" to estimate performance.
- Fluid Benchmarking ([Hofmann et al. 2025](https://arxiv.org/abs/2509.11106)): adaptive IRT selection gives "higher validity and less variance on MMLU with fifty times fewer items". The comparison is on MMLU against random sampling and IRT baselines; do not generalize it to other benchmarks.
- Counter-evidence ([Madaan et al. 2024](https://arxiv.org/abs/2406.10229)): human-testing methods "such as item analysis and item response theory" struggle "to meaningfully reduce variance". Validate any subset on your own systems before replacing the full set.

**Differential item functioning (DIF)** means that systems of equal overall ability have different success on an item across groups, such as language, locale or model family. DIF is the concrete invariance test for a multilingual or cross-family claim. Global MMLU ([Singh et al. 2024](https://arxiv.org/abs/2412.03304)) found "28% of all questions requiring culturally sensitive knowledge", and model rankings changed between the full set and the culturally sensitive subset. Stratify by item type and check rank stability before claiming one system is better for a language. DIF flags an item-level difference without explaining its cause.

## Saturation and ceiling effects

Saturation is a scale-range failure. When top systems cluster near the maximum, remaining differences are dominated by label errors, ambiguous items and noise.

- **Signs:** most top systems fall within the run-to-run noise band; residual failures concentrate on items with disputed gold labels; rankings flip across seeds or templates.
- **Actions:** report signal against noise. Heineman et al. ([2025](https://arxiv.org/abs/2508.13144)) define signal as a benchmark's ability to separate better models from worse ones and noise as its sensitivity to random variability between training steps; benchmarks with a better signal-to-noise ratio were more reliable for small-scale decisions. Then audit the remaining failures for label errors, and add harder items calibrated at the frontier, or retire the benchmark for this decision.
- **Do not** read a 0.5-point leaderboard gap on a saturated benchmark as a capability difference. It is at most a descriptive difference on that instrument.

## Construct-validity checklist for a benchmark claim

Bean et al. ([2025](https://arxiv.org/abs/2511.04703), NeurIPS 2025 Datasets & Benchmarks) had 29 expert reviewers review 445 LLM benchmarks. They found that only "16.0% used uncertainty estimates or statistical tests to compare the results", and gave eight recommendations. Use them as an audit checklist mapped to the primitives:

| Recommendation (Bean et al. heading) | Audit question | Primitive |
|---|---|---|
| Define the phenomenon | Is the target capability defined, with its scope and exclusions? | Construct |
| Measure the phenomenon and only the phenomenon | Do format, parsing, tool access or scaffold drive the score? | Operationalization |
| Construct a representative dataset for the task | Do items sample the deployment task space, or only an easy corner of it? | Validity (content) |
| Acknowledge limitations of reusing datasets | Is a dataset built for another purpose being reinterpreted? | Validity |
| Prepare for contamination | Could the systems have seen the items? (controls in ai-evals) | Error / validity |
| Use statistical methods to compare models | Are uncertainty and facet variance reported? | Reliability |
| Conduct an error analysis | Do the failures reflect the construct or nuisance factors? | Validity (response process) |
| Justify construct validity | Is there an explicit argument from the score to the claim? | Validity |

For each claim, write the claim-to-evidence mapping: whether the score supports "solves these test items", "has this narrow skill", or "has this broad ability". Salaudeen et al. ([2025](https://arxiv.org/abs/2505.10573)) give a validity-centred framework for making that mapping. Broad-ability claims need evidence beyond a single benchmark.

## Neuro and biometric instruments

"Does this signal measure that state?" is the same validity question: EEG, GSR, eye-tracking or fMRI as an index of emotion, attention or preference. Apply the primitives here. The consumer-specific evidence contract and the reverse-inference confound table live in [consumer neuroscience evidence-to-product](../../foundations-consumer-neuroscience/references/evidence-to-product.md).
