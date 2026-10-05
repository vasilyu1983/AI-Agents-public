# ai-ml-data-science — Consolidated Learnings

Curated, dated, committed memory for this skill. Pruned from raw `learnings.md` via `agents-skills-feedback-loop/scripts/consolidate.py`. Human-approved.

Cap: 60 entries. When exceeded, promote durable rules to `references/`.

## Filter Override

<!-- Add 2-4 bullets that sharpen what counts as a learning for this skill. Leave empty to use the default filter from agents-skills-feedback-loop/references/learnings-format.md. -->

## Patterns That Work

## Mistakes to Avoid

## Domain Knowledge

- [2026-05-17] Neptune.ai hosted service shut down 2026-03-05 following OpenAI acquisition; all hosted data was deleted. Remove from any live tool recommendation; replace with MLflow (open-source default) or Comet ML / ClearML as cloud alternatives.
- [2026-05-17] (corrected 2026-09-30: row limits removed; later releases raised them well beyond 50k) TabPFN-family models are a comparison candidate within the limits on the exact checkpoint's model card; read those limits and the licence before the bake-off. Does NOT replace LightGBM/CatBoost by default at scale and should be framed as an additional comparison candidate, not a default. Specific win-rate figures from arXiv 2511.08667 are model-version-specific; always verify against current paper before asserting numbers.
- [2026-05-17] CQF (classifier quality filtering) limitation: filtering pretraining data toward a quality classifier's distribution improves downstream benchmark scores, but does not necessarily improve LM performance on the reference corpus itself. Benchmark gains may reflect distributional alignment, not genuine capability gains. Hedge any claim about classifier filtering benefits when the evidence is benchmark-only.
- [2026-05-17] Pure-synthetic pretraining does not consistently match natural-text pretraining. Synthetic data helps most as a targeted supplement (rare domains, instruction formats, reasoning chains) or in fine-tuning mixtures. No universal optimal mixing ratio is established across settings; treat published ratios as dataset- and task-specific.
- [2026-05-17] Benchmark contamination from large crawled corpora is a systematic risk for LLM evaluation. MinHash near-dup (Jaccard 0.5–0.7) + n-gram exact matching are the standard detection pair (corrected 2026-09-25: choose n per benchmark — GPT-3 used 13-grams, Llama 3 scored 8-grams). Min-K% Prob (arXiv 2310.16789) is the standard post-training detection method. Always decontaminate synthetic data against target benchmarks before including in training.

## Open Questions

## Consolidated Principles

