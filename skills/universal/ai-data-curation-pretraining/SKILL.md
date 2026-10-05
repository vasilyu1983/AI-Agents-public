---
name: ai-data-curation-pretraining
description: "Builds LLM pretraining corpora from Common Crawl: extract, filter, deduplicate, decontaminate, mix, synthesize. Use when curating or ablating a pretraining corpus or data pipeline."
compatibility: Portable core. Works on Claude Code and Codex.
version: "1.3"
last_validated: 2026-09-25
---

# Pretraining Data Curation — Functional Reference Skill

Build web-scale and synthetic pretraining corpora, then measure curation choices with controlled ablations.

## When to Use This Skill

Activate when the task involves:

- Finding existing high-quality datasets for pretraining or fine-tuning before building from scratch (see Dataset Discovery reference)
- Sourcing and filtering CommonCrawl WARCs or other web-scale corpora
- Implementing or debugging any stage of the curation pipeline above
- Designing quality filters (heuristic or classifier-based)
- Running MinHash / LSH deduplication or exact-substring dedup
- Decontaminating a dataset against evaluation benchmarks
- Generating synthetic pretraining data (Cosmopedia, Self-Instruct, Evol-Instruct, Nemotron)
- Designing and executing controlled data ablations
- Writing datasheets (Gebru et al.) for a curated dataset
- Understanding open recipe datasets: FineWeb, Dolma, The Pile, RedPajama, SlimPajama, C4, RefinedWeb, OLMo

## Scope Boundaries

This skill covers the corpus side of pretraining — from raw crawl to tokenized shards and ablation measurement. Use linked skills for adjacent concerns:

- **Pretraining run setup, distributed training, checkpointing** → [ai-pretraining](../ai-pretraining/SKILL.md)
- **Token budget, compute-optimal scaling (Chinchilla law)** → [ai-scaling-laws](../ai-scaling-laws/SKILL.md)
- **Benchmark harness setup, metric interpretation** → [ai-evals](../ai-evals/SKILL.md)
- **Applications-layer retrieval, chunking, reranking at inference time** → [ai-rag](../ai-rag/SKILL.md) — NOTE: RAG is *not* pretraining data curation; do not conflate corpus mixing with retrieval indexing
- **Storage, ingestion, workflow orchestration at platform level** → [data-lake-platform](../data-lake-platform/SKILL.md)

## Quick Reference

| Stage | Tooling | Highest-Leverage Lever |
|-------|---------|------------------------|
| Extract | datatrove `WarcReader` + `Trafilatura` | Extractor choice sets the noise ceiling for downstream stages |
| Language ID | fastText `lid.176.bin` for English; GlotLID for broad multilingual coverage | FineWeb used a 0.65 English threshold. FineWeb2 used GlotLID and calibrated thresholds per language; set thresholds from labeled samples and observed score distributions instead of transferring the English cutoff |
| Heuristic quality | Gopher rules, C4 rules | Gopher: ≥2 of 8 common English stopwords per document; hash/ellipsis-to-word ratio ≤ 0.1. C4: line-level filters (see cheat sheet) |
| Classifier quality | FineWeb-Edu edu-score | In DCLM's controlled comparison, a single model-based classifier beat heuristic rule stacks (see DCLM row below) |
| Near-dedup | MinHash + LSH (datasketch, datatrove) | Pick bands×rows for the similarity you target; FineWeb used 5-gram shingles and 14 bands × 8 rows. Compare per-snapshot and global-per-language dedup on your target corpus; FineWeb and FineWeb2 made different choices |
| Exact-dedup | Suffix-array substring | Catches boilerplate that MinHash misses (short repeated blocks) |
| Semantic-dedup | SemDeDup (arXiv 2303.09540) | Embedding-cluster dedup catches paraphrases MinHash misses; complements (not replaces) MinHash |
| Decontamination | n-gram overlap vs eval sets | Choose n by benchmark item length and tokenizer (GPT-3 used 13-grams, Llama 3 scored 8-grams); report the overlap rate per benchmark |
| PII / safety | Regex + classifier cascade | Email/phone regex first (fast), then classifier for context-dependent PII |
| Tokenize + shard | Model tokenizer; Parquet or training-format writer | Select shard size against dataloader and storage throughput; preserve document boundaries |
| Domain mix | dolma toolkit; DoReMi / RegMix for weights | Mix proportions are the single most impactful knob after basic filtering — set them with a method, not by hand (see Data Mixing Methods) |

## Frontier Recipes & Methods

The pipeline above is the durable backbone. These are recipes worth knowing and citing; check each against newer controlled comparisons before treating it as the default.

| Recipe / Method | What it changed | Use it for |
|-----------------|-----------------|------------|
| **DataComp-LM (DCLM)** — arXiv 2406.11794 | First controlled benchmark for data curation (240T-token pool, fixed compute, 53 evals). Showed a single fastText classifier trained on high-quality reference text (DCLM-Baseline) beats heuristic stacks decisively. | The reference point when arguing any filtering choice. Replicate its model-based filtering before hand-tuning Gopher rules. |
| **Nemotron-CC** — arXiv 2412.02595 | Solves the token-yield problem: aggressive edu-style filters discard ~90% of tokens. Uses a classifier *ensemble* + **synthetic rephrasing** of mid/low-quality pages to recover 6.3T usable tokens. | Multi-trillion-token runs where filtering would otherwise starve the corpus. Pairs with the synthetic-data reference. |
| **WRAP (rephrase-the-web)** — arXiv 2401.16380 | Rephrases web pages into cleaner styles ("like Wikipedia", QA format) instead of only filtering — ~3x pretraining speedup at fixed compute. The paradigm Nemotron-CC scales. | Lifting quality of pages that filtering would drop; augmenting scarce high-quality domains. |
| **FineWeb-2** — arXiv 2506.20920 | Extends the FineWeb/datatrove pipeline to 1000+ languages with per-language threshold tuning (20TB, 5B docs). | Any non-English or multilingual corpus. The default multilingual baseline. |
| **Common Pile v0.1 / Comma** — arXiv 2506.05209 | 8TB public-domain + openly licensed corpus across 30 sources; 7B models competitive with unlicensed-data peers. | Corpora with IP/copyright exposure (enterprise, public release). See licensing traps. |
| **Common Corpus** — arXiv 2506.01732 (Pleias / AI Alliance) | ~2T-token openly licensed corpus with heavy non-English (French, German, multilingual) coverage; complements Common Pile's English/code skew. | Open-license corpora needing broader multilingual coverage than Common Pile alone. |
| **Blu-WERP** — arXiv 2511.18054 | Reports 4.0% and 9.5% relative aggregate improvements over DCLM and FineWeb at 1B scale, respectively. Single-paper result: compare on your corpus before treating it as a successor. | Candidate extraction and filtering recipe to benchmark against the existing pipeline. |

## Data Mixing Methods

Domain mix is the highest-leverage knob after basic filtering — but "tune via ablations" is no longer the frontier answer. Set it with a principled method:

| Method | Mechanism | When to reach for it |
|--------|-----------|----------------------|
| **DoReMi** — arXiv 2305.10429 | Train a small proxy with group-DRO to find domain weights that minimize worst-case excess loss; transfer weights to the full run. +6.5pp few-shot vs Pile defaults. | You have fixed domains and want robust weights without a full sweep. |
| **Data Mixing Laws** — arXiv 2403.16952 | Fit a scaling-law surface over mixture ratios from small proxy runs; extrapolate the optimum before spending full compute. | Predicting the optimal mix at target scale from cheap experiments. |
| **RegMix** — arXiv 2407.01492 | Train many small models on random mixtures, regress performance on ratios, pick the predicted-best mixture. Matches DoReMi at lower compute. | Compute-cheaper alternative to DoReMi; many candidate domains. |

Whichever you use, still validate the chosen mix with a held-out ablation run (Run F) — the methods set the prior, the ablation confirms it.

## Default Workflow

1. **Define corpus goal**: target language, domain distribution, token budget, training compute budget.
2. **Extract**: run datatrove `WarcReader` + `Trafilatura` over WARC dumps; keep URL + source metadata.
3. **Language filter**: use fastText for an English-focused corpus or GlotLID for broad multilingual coverage; calibrate thresholds per target language and log token counts before and after.
4. **Heuristic filter**: apply Gopher + C4 rules; log drop rate per rule to identify dominant removals.
5. **Classifier filter**: train or apply FineWeb-Edu edu-score / custom classifier; set threshold on a held-out labeled set.
6. **Dedup**: MinHash + LSH near-dedup; compare per-snapshot and global-per-language scope on a held-out ablation, then apply exact-substring dedup where repeated spans remain.
7. **Decontaminate**: match against every evaluation benchmark you plan to report, with n chosen for that benchmark's item length and tokenizer; report overlap rates and fail loud on matches.
8. **PII / safety scrub**: regex sweep + safety classifier; document removal rates.
9. **Tokenize + shard**: produce indexed Parquet shards; verify document count and total token count.
10. **Mix + ablate**: design controlled ablation runs (one change per run); train small proxy model; measure eval delta with lm-evaluation-harness.
11. **Datasheet**: write Gebru et al. datasheet before publishing or using the corpus externally.

## Data Ablation Table

Run a small proxy model at fixed compute. One change per run. Evaluate on the same benchmark suite with the same harness and prompt format. For scale: FineWeb's filtering ablations used 1.71B-parameter models (embeddings included) on ≈28B tokens, two seeds/data subsets per variant.

| Run | Corpus | Change vs Prior | Measure |
|-----|--------|-----------------|-----------------|
| A | Raw CC extract | Baseline | Task scores and retained tokens |
| B | A + heuristic filter | Gopher/C4 rules | Score and yield change from filtering |
| C | B + near-dedup | MinHash | Score and yield change from deduplication |
| D | C + classifier filter | FineWeb-Edu-style score | Score and yield change from the classifier |
| E | D + synthetic data | One measured synthetic share | Task and diversity changes |
| F | E + method-driven mix | Vary domain weights, holding synthetic share fixed | Best mix on the locked evaluation suite |

**Protocol**: hold compute constant across A–F. Do not change model architecture or eval prompt format between runs. Decontaminate each corpus variant before training.

**Benchmark selection (FineWeb's criteria).** Keep a benchmark in the ablation suite only if, at proxy scale, it shows (1) low score variance between runs trained on different random subsets of the same data, (2) monotonic or nearly monotonic improvement over training, and (3) scores above the random baseline. Train at least 2 seeds or data subsets per variant and compare averages; a delta inside the seed spread is not a result.

**Judge filter aggressiveness at the final token horizon (hedged).** An aggressive filter can win a short ablation yet force many repeated epochs over a smaller corpus in the full run, where repetition costs more. If the target run will exhaust the filtered pool, re-run the comparison at the token count and epoch count the real run will see, not only at the proxy budget.

## ASCII Heuristic Rules Cheat Sheet

```text
Gopher rules (sample):
  word_count: 50 ≤ n ≤ 100_000
  mean_word_length: 3 ≤ chars ≤ 10
  symbol_to_word_ratio: ≤ 0.1  (symbols = hash "#" and ellipsis)
  fraction_lines_ending_ellipsis: < 0.3
  fraction_lines_starting_bullet: < 0.9
  alphabetic_words: ≥ 80% of words contain an alphabetic character
  stopwords: ≥ 2 of {the, be, to, of, and, that, have, with} present in the document

C4 rules (sample, mostly line-level):
  keep only lines ending in terminal punctuation (. ! ? ")
  drop lines with fewer than 5 words; drop pages with fewer than 3 sentences
  drop lines containing "javascript"
  drop pages containing "lorem ipsum" or a curly brace "{"
  dedup: remove repeated three-sentence spans (keep one occurrence)
```

Re-read the source paper's rule list before implementing; datatrove ships reference implementations.

## MinHash + LSH Banding Intuition

With b bands of r rows (b·r MinHash permutations), a pair with Jaccard similarity s becomes a candidate with probability

```text
P(candidate) = 1 - (1 - s^r)^b          threshold (steepest point) ≈ (1/b)^(1/r)
```

Computed values; re-derive for your own b, r with `ai-scaling-laws/scripts/training_math.py lsh --bands B --rows R --similarity 0.5 0.8`:

| b × r (perms) | threshold | P(s=0.5) | P(s=0.75) | P(s=0.8) | Use |
|---|---|---|---|---|---|
| 20 × 6 (120) | ≈0.61 | 0.27 | 0.98 | 0.998 | Aggressive: flags many 50–60% matches |
| 14 × 8 (112) | ≈0.72 | 0.05 | 0.77 | 0.92 | FineWeb's setting (5-grams, ≈75% target) |
| 16 × 8 (128) | ≈0.71 | 0.06 | 0.82 | 0.95 | Similar, using all 128 permutations |
| 9 × 13 (117) | ≈0.84 | 0.001 | 0.20 | 0.40 | Error-minimizing split for threshold=0.8, 128 perms (datasketch's criterion): misses most pairs *at* 0.8 |

More bands / fewer rows lowers the threshold (more aggressive, more false positives to verify); fewer bands / more rows raises it. A named "threshold" in a library is the steep point of the S-curve, not a guarantee: at exactly that similarity recall can be well under 50%. Check P at the similarity you actually care about.

## Mixture Change Gate

Change one mixture decision at a time: source inclusion, sampling weight, quality filter, dedup threshold, or synthetic-data share. Freeze the tokenizer, training budget, seed policy, and evaluation set; log document counts and effective tokens before and after the change. Promote the candidate only when target slices improve without unacceptable regression on retained-domain, contamination, memorization, and provenance checks. A higher aggregate benchmark score alone does not identify which data decision helped.

## Known Traps

1. **Contamination** — the field's most common silent failure. Benchmark text appears in training data, scores look inflated, but the model learned the answer key. Decontaminate against every benchmark you plan to report, using n-gram overlap. Choose n for each benchmark (GPT-3 used 13-grams; Llama 3 scored 8-grams; short items need smaller n), report the overlap rate, remove or flag matching documents, and log the URLs.

2. **Model collapse from synthetic data** — recursively training on unverified model outputs can erode tail knowledge (Shumailov et al., *Nature* 631:755–759, DOI 10.1038/s41586-024-07566-y). Keep a provenance-checked natural-data baseline, test synthetic mixes at the target training horizon, and verifier-gate generated examples. Mixing alone does not guarantee safety under fully recursive retraining; see the [synthetic-data reference](references/synthetic-data-generation.md#collapse-traps).

3. **Diversity collapse** — heavy classifier filtering removes stylistically unusual but high-quality text (dialects, domain jargon, informal registers). Check: does the filtered corpus have narrower vocabulary size and sentence-length distribution than the input?

4. **Generator contamination** — when a generative model produces synthetic data, it may reproduce memorized benchmark content. Decontaminate the synthetic data independently, not just the web data.

5. **Distillation licensing** — commercial model providers' terms and open-weight licences can restrict using outputs to train other models, and they change. **Lookup step:** read the generator's current terms of service or model licence before generation, record the version you read, and block release of any corpus whose generator terms forbid the intended use.

6. **Single-change ablation discipline** — changing two variables in one run makes the delta uninterpretable. Always one change per run.

7. **EU AI Act training-data transparency** — under Article 53(1)(d), providers of general-purpose AI models placed on the EU market must publish a "sufficiently detailed summary" of training content using the AI Office's template, covering categories such as crawled/scraped, licensed, user and synthetic data. Separately, the DSM Directive Article 4 text-and-data-mining exception requires honoring machine-readable rightsholder opt-outs. **Lookup step:** read the AI Office's current guidance and the Commission's opt-out protocol status for application dates, enforcement status and template version before a release decision; that feeds whether the release is blocked. Practical implication for curation pipelines, whatever the enforcement date: log data-source category (crawled / licensed / synthetic / user) and opt-out status per document from Stage 0 onward — retrofitting this for a training-data summary is far more expensive than logging it during extraction.

8. **Dedup scope** — FineWeb found that global dedup of an older crawl retained a lower-quality remainder and chose per-snapshot dedup. FineWeb2 deduplicated globally per language, then used cluster-size-aware upsampling. Test the scope on the target language, token horizon, and evaluation suite before committing to either recipe.

## Navigation: Core References

- **[Dataset Discovery](references/dataset-discovery.md)** — where to find existing datasets (HF, Kaggle, Google Dataset Search, government portals, lm-evaluation-harness) and the license/contamination gates before using them
- **[Web Curation Pipeline](references/web-curation-pipeline.md)** — datatrove stage-by-stage: WARC download, extraction, language ID, heuristic filter, dedup, decontamination
- **[Synthetic Data Generation](references/synthetic-data-generation.md)** — Cosmopedia / Self-Instruct / Evol-Instruct recipes, verifier gating, collapse traps
- **[Data Ablation Method](references/data-ablation-method.md)** — controlled-run protocol, proxy model setup, metric collection, datasheet

## External Sources

See **[data/sources.json](data/sources.json)** for curated primary sources across:

- Open corpus recipes and papers (FineWeb, Dolma, The Pile, RedPajama, C4, RefinedWeb)
- Deduplication and decontamination methods
- Synthetic data generation papers
- Evaluation harness

## Learnings Loop

When prior decisions or pitfalls are relevant, consult `learnings.consolidated.md` if present; use `learnings.md` only for needed history or as the available fallback. Otherwise skip both.

After applying it, if you encountered a pattern worth remembering, a mistake worth preventing, or a domain fact that surprised you, append one dated bullet to `learnings.md` via `agents-skills-feedback-loop/scripts/append_learning.py`. Do not modify `SKILL.md` itself.
