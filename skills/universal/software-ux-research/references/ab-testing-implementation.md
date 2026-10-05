# Experiment vs Research: A/B Testing from the Research Side

When a UX question needs a controlled experiment instead of (or after) qualitative research, and what the research lead must check before trusting an experiment readout. Experiment design, instrumentation, SRM checks, CUPED, feature-flag setup and rollout live in marketing-product-analytics/references/experimentation-framework.md; sequential testing and switchback designs in marketing-product-analytics/references/causal-inference-applied.md; power and multiplicity theory in [foundations-statistical-inference](../../foundations-statistical-inference/SKILL.md).

---
## Table of Contents

- [Experiment or Research?](#experiment-or-research)
- [Sequencing Research and Experiments](#sequencing-research-and-experiments)
- [Sample Size and Runtime](#sample-size-and-runtime)
- [Readout Checks for Researchers](#readout-checks-for-researchers)
- [Experimentation Maturity](#experimentation-maturity)
- [Results Report Skeleton](#results-report-skeleton)
- [Platforms](#platforms)

---

## Experiment or Research?

| Question shape | Use | Why |
|----------------|-----|-----|
| "Does change X move metric Y, and by how much?" | Controlled experiment | Only randomisation gives a causal effect size |
| "Why do users abandon at step X?" | Interviews, usability tests, session replay paired with follow-up | An experiment shows *that*, never *why* |
| "Which of these concepts do users understand?" | Concept or usability test | Comprehension failures surface in a small moderated round; an experiment needs a shipped build and enough traffic to be powered |
| "Is this redesign better?" (many simultaneous changes) | Usability benchmark (SUS, task success) first, then a staged rollout with guardrails | A multi-variable A/B gives one number you cannot attribute |
| Low traffic (cannot reach the sample size in a reasonable runtime) | Qualitative evaluation plus before/after cohort comparison | An underpowered test yields noise that looks like a decision |
| Legal, accessibility or bug fix | Ship; monitor | Not a candidate: you would not keep the control |
| Irreversible or trust-sensitive change (pricing, data use, AI autonomy) | Research first; experiment only with ethics review | Harm to the control or treatment group cannot be undone |

Good experiment candidates: a clear primary metric, enough traffic, an isolated and reversible change, and a runtime covering at least one full weekly cycle.

## Sequencing Research and Experiments

1. **Qual before the experiment** — find the friction and form the hypothesis (`[Observation] leads us to believe [Change] will cause [Effect] for [Segment] measured by [Metric]`).
2. **Experiment** — measure the effect of the chosen change.
3. **Qual after a surprising result** — a win or loss you cannot explain is a research question, not a shipping decision. Interview or test with users from the winning and losing arms.

A flat result is not evidence that users do not care; it can mean the change did not address the friction qualitative work found.

## Sample Size and Runtime

Per-variant sample size for a conversion metric (normal approximation):

```text
n = 2 × (Zα + Zβ)² × p(1-p) / (MDE × p)²
Zα = 1.96 (α = .05 two-sided), Zβ = 0.84 (power .80), p = baseline rate, MDE = relative minimum detectable effect
Minimum runtime = n / daily traffic per variant, rounded up to whole weeks
```

Set MDE at the smallest effect worth acting on, not the smallest the statistics can detect. Verify with a calculator or script before committing traffic; baseline and MDE assumptions swing n by an order of magnitude. Worked tables: experimentation-framework.md.

## Readout Checks for Researchers

- **Randomisation** — assignment happens before exposure, is sticky (a returning user sees the same variant), and is independent of other running experiments. Check the split with an SRM test before reading any metric.
- **Intent-to-treat by default** — analyse users by assigned arm, including those who never saw the change (caching, failures, opt-outs). A per-protocol analysis of only exposed users is a diagnostic, not the decision number; a large ITT/per-protocol gap usually signals a reliability problem.
- **Practical vs statistical significance** — a significant but tiny lift may not repay the maintenance cost; a non-significant lift in the right direction on a high-stakes metric is a reason to iterate, not a failure.
- **No peeking without a sequential design** — repeated looks at a fixed-horizon test inflate false positives. Pre-commit the end date or use a sequential method.
- **One primary metric** — pre-register it; treat segment cuts as exploratory unless pre-registered or corrected for multiplicity.
- **Novelty and primacy** — plot the effect over time and split new vs returning users before calling a winner.
- **Interference** — in marketplaces, social feeds and shared inventory, one user's treatment changes others' outcomes; user-level randomisation is biased. Use cluster or switchback designs.

## Experimentation Maturity

| Level | Characteristics | Next step |
|-------|-----------------|-----------|
| 1. Ad hoc | One-off tests, manual analysis, results often ignored | Plan template, central results log |
| 2. Standardised | Consistent method, powered samples, results shared | Pre-launch review, experiment catalog, automated SRM and power checks |
| 3. Platform | Dedicated tooling, feature flags, automated guardrails | Sequential testing, variance reduction |
| 4. Culture | Most changes tested, learnings documented and reused | Meta-analysis across experiments, long-term holdouts |

Research teams at level 1-2 should prioritise the research-to-hypothesis link; at level 3-4, the post-result qualitative follow-up is usually the missing step.

## Results Report Skeleton

```markdown
## Results: [Experiment]
- Result: WIN / LOSS / INCONCLUSIVE; decision: ship / keep control / iterate
- Primary metric: [+X%] (95% CI [a, b]); runtime [N] days, [N] users per arm; SRM check passed
- Segments (pre-registered only): [segment | control | treatment | lift | CI]
- Guardrails: [metric | change | status]
- Research link: which qualitative finding motivated the test; what the result says about it
- Open questions for follow-up research
```

## Platforms

Ownership, packaging and pricing of experimentation vendors change often, and several have been acquired or rebranded. Before recommending one, check the vendor's own site for its current owner, product name and plans. Categories to choose between: full hosted platforms, warehouse-native tools, open-source self-hosted tools, feature-flag platforms with experimentation, and analytics suites with built-in experiments. Platform selection and integration belong to `marketing-product-analytics`.
