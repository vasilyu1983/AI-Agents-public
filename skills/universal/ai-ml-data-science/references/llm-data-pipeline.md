# LLM Training Data Pipelines

Corpus curation for LLM pretraining — extraction, quality filtering, exact and near-duplicate removal, decontamination, data mixing, synthetic data and data ablations — is owned by **[ai-data-curation-pretraining](../../ai-data-curation-pretraining/SKILL.md)**. Go there first when building an LLM from scratch or curating a pretraining mixture. This file keeps only the evaluation-side checks a data scientist needs when an LLM's training data may overlap its test data.

---
## Table of Contents

- [Where Curation Lives](#where-curation-lives)
- [Contamination Checks Without Corpus Access](#contamination-checks-without-corpus-access)
- [Contamination-Resistant Benchmarks](#contamination-resistant-benchmarks)
- [Classifier-Filtered Data and Benchmark Claims](#classifier-filtered-data-and-benchmark-claims)
- [Related Resources](#related-resources)

## Where Curation Lives

| Task | Owner |
|------|-------|
| Extraction, heuristic and classifier filtering, language ID | [web-curation-pipeline.md](../../ai-data-curation-pretraining/references/web-curation-pipeline.md) |
| Exact dedup, MinHash-LSH near-dedup (banding math, per-snapshot scope), semantic dedup | [ai-data-curation-pretraining](../../ai-data-curation-pretraining/SKILL.md) and [web-curation-pipeline.md](../../ai-data-curation-pretraining/references/web-curation-pipeline.md) |
| Decontamination against benchmarks (n-gram length chosen per benchmark) | [data-ablation-method.md](../../ai-data-curation-pretraining/references/data-ablation-method.md) |
| Synthetic data and mixing ratios | [synthetic-data-generation.md](../../ai-data-curation-pretraining/references/synthetic-data-generation.md) |
| Whether a filter or mix helped (proxy-model ablations, benchmark selection) | [data-ablation-method.md](../../ai-data-curation-pretraining/references/data-ablation-method.md) |

## Contamination Checks Without Corpus Access

When you evaluate a model whose training corpus you cannot scan, use a membership-inference check instead of n-gram matching:

- **Min-K% Prob** (arXiv 2310.16789): for a candidate text, take the k% of tokens with the lowest log-probability under the model and average them. Seen text tends to score higher than unseen text of the same kind.
- Treat it as a screening signal, not proof: calibrate the threshold on text you know is unseen (for example, published after the model's training cutoff) before flagging a benchmark as contaminated.

## Contamination-Resistant Benchmarks

When contamination risk is high (large crawled corpora, frequently cited benchmarks), prefer:

- benchmarks released after the model's training window;
- private held-out test sets;
- procedurally generated benchmarks that produce new problems per run;
- contamination-resistant suites that refresh their items (check that the suite is still maintained).

**Scope:** this applies to LLMs or any setting where pretraining or fine-tuning data may overlap evaluation data. For classical ML on small curated datasets, standard train/test split hygiene (see `modelling-patterns.md` §2) is sufficient.

## Classifier-Filtered Data and Benchmark Claims

Filtering a corpus toward a quality classifier's reference distribution can raise benchmark scores by matching the benchmark's distribution rather than by adding capability. When a model trained on classifier-filtered data is compared on benchmarks, say so and, where possible, report an ablation against the unfiltered mix (method in [data-ablation-method.md](../../ai-data-curation-pretraining/references/data-ablation-method.md)).

**Checklist: evaluation-side contamination**

- [ ] Decontamination was run by the data owner (ask for the method and n-gram length), or a Min-K% screen was run here
- [ ] Benchmark choice accounts for the model's training window
- [ ] Classifier filtering disclosed next to any benchmark claim

## Related Resources

- [Modelling Patterns](modelling-patterns.md) - Model family selection and tabular baselines
- [Evaluation Patterns](evaluation-patterns.md) - Benchmark contamination detection and evaluation design
- [Data Contracts & Lineage](data-contracts-lineage.md) - Annotation quality and data governance
- [Reproducibility Checklist](reproducibility-checklist.md) - Experiment tracking and artifact versioning
