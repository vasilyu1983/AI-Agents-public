---
name: ai-data-curation-pretraining
description: "Builds and audits LLM pretraining corpora: extraction, filtering, dedup, decontamination, data mixing, synthetic data. Use when curating or ablating a pretraining data pipeline."
compatibility: Portable core. Works on Claude Code and Codex.
version: "1.1"
last_validated: 2026-07-11
---

# Pretraining Data Curation — Functional Reference Skill

**Domain**: Building web-scale and synthetic pretraining corpora, running controlled data ablations. Distinct from applications-layer retrieval (RAG) and general data engineering.

No theory. No generic pipeline intros. Focus on stage-by-stage decisions, heuristic thresholds, tooling choices, and ablation protocol.

## ASCII Flow

```text
CommonCrawl WARCs
  |
  v
[Extract]  trafilatura / datatrove HTMLExtractor
  raw text + metadata (URL, timestamp, content-type)
  |
  v
[Language ID]  fastText lid.176.bin
  keep target language(s), threshold ≥ 0.65
  |
  v
[Quality Filter — Heuristic]  Gopher / C4 rules
  symbol-to-word ratio, fraction lines ending ellipsis,
  stopword density, word count bounds, mean word length
  |
  v
[Quality Filter — Classifier]  FineWeb-Edu edu-score / custom
  trained on human labels; outperforms heuristics on recall
  |
  v
[Near-Dedup]  MinHash + LSH banding (datasketch)
  n-gram shingles -> MinHash signature -> band partitioning
  |
  v
[Exact-Substring Dedup]  suffix-array substring match
  remove exact repeated sequences across documents
  |
  v
[Decontamination]  n-gram match against eval benchmarks
  FAIL LOUD — contaminated eval numbers are the field's #1 silent failure
  |
  v
[PII / Safety Scrub]  regex + classifier
  email, phone, SSN, credit card patterns; hate/CSAM removal
  |
  v
[Tokenize + Shard]  HF tokenizers / tiktoken; Parquet shards
  |
  v
[Domain Mix + Weight]  dolma toolkit / custom sampling
  web / books / code / math / synthetic — proportions are a research lever
  |
  v
[Train + Eval]  nanotron / lighteval / lm-evaluation-harness
  ablation output: eval delta per pipeline stage
```

## When to Use This Skill

Activate when the task involves:

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
| Extract | datatrove `HTMLExtractor`, trafilatura | Extractor choice sets noise ceiling for all downstream stages |
| Language ID | fastText `lid.176.bin`; GlotLID (2000+ languages) or OpenLID for low-resource/multilingual | Threshold: ≥ 0.65 keeps recall; ≥ 0.85 kills noisy multilingual. Use GlotLID over lid.176 once >176 languages or heavy code-switching is in scope — it's what FineWeb2 standardized on |
| Heuristic quality | Gopher rules, C4 rules | Symbol-to-word ratio < 0.1; stopword density > 2 words per 100 |
| Classifier quality | FineWeb-Edu edu-score | Single classifier outperforms 20+ Gopher rules on recall |
| Near-dedup | MinHash + LSH (datasketch) | Jaccard threshold 0.8, 9-gram shingles, 128 permutations |
| Exact-dedup | Suffix-array substring | Catches boilerplate that MinHash misses (short repeated blocks) |
| Semantic-dedup | SemDeDup (arXiv 2303.09540) | Embedding-cluster dedup catches paraphrases MinHash misses; complements (not replaces) MinHash |
| Decontamination | n-gram overlap vs eval sets | ≥ 13-gram match = contaminated; remove entire document |
| PII / safety | Regex + classifier cascade | Email/phone regex first (fast), then classifier for context-dependent PII |
| Tokenize + shard | HF tokenizers, tiktoken | Shard to ≤ 1 GB Parquet; document boundaries matter for context windows |
| Domain mix | dolma toolkit; DoReMi / RegMix for weights | Mix proportions are the single most impactful knob after basic filtering — set them with a method, not by hand (see Data Mixing Methods) |

## Frontier Recipes & Methods (2024–2026)

The pipeline above is the durable backbone. These are the recipes a current practitioner is expected to know and cite; treat them as the modern defaults, not optional extras.

| Recipe / Method | What it changed | Use it for |
|-----------------|-----------------|------------|
| **DataComp-LM (DCLM)** — arXiv 2406.11794 | First controlled benchmark for data curation (240T-token pool, fixed compute, 53 evals). Showed a single fastText classifier trained on high-quality reference text (DCLM-Baseline) beats heuristic stacks decisively. | The reference point when arguing any filtering choice. Replicate its model-based filtering before hand-tuning Gopher rules. |
| **Nemotron-CC** — arXiv 2412.02595 | Solves the token-yield problem: aggressive edu-style filters discard ~90% of tokens. Uses a classifier *ensemble* + **synthetic rephrasing** of mid/low-quality pages to recover 6.3T usable tokens. | Multi-trillion-token runs where filtering would otherwise starve the corpus. Pairs with the synthetic-data reference. |
| **WRAP (rephrase-the-web)** — arXiv 2401.16380 | Rephrases web pages into cleaner styles ("like Wikipedia", QA format) instead of only filtering — ~3x pretraining speedup at fixed compute. The paradigm Nemotron-CC scales. | Lifting quality of pages that filtering would drop; augmenting scarce high-quality domains. |
| **FineWeb-2** — arXiv 2506.20920 | Extends the FineWeb/datatrove pipeline to 1000+ languages with per-language threshold tuning (20TB, 5B docs). | Any non-English or multilingual corpus. The default multilingual baseline. |
| **Common Pile v0.1 / Comma** — arXiv 2506.05209 | 8TB public-domain + openly licensed corpus across 30 sources; 7B models competitive with unlicensed-data peers. | Corpora with IP/copyright exposure (enterprise, public release). See licensing traps. |
| **Common Corpus** — arXiv 2506.01732 (Pleias / AI Alliance) | ~2T-token openly licensed corpus with heavy non-English (French, German, multilingual) coverage; complements Common Pile's English/code skew. | Open-license corpora needing broader multilingual coverage than Common Pile alone. |
| **Blu-WERP** — arXiv 2511.18054 (Nov 2025) | Reports +4.0% vs. DCLM-Baseline and +9.5% vs. FineWeb, aggregate, at 1B scale, via JusText extraction + Bloom-filter dedup + semantic classifier. Not yet independently replicated or adopted by a frontier lab as of this writing — treat as an emerging challenger, not a settled successor. | Sanity-checking whether your extraction+filter stack is still state-of-the-art; a candidate to benchmark against, not yet a default to copy blind. |

## Data Mixing Methods

Domain mix is the highest-leverage knob after basic filtering — but "tune via ablations" is no longer the frontier answer. Set it with a principled method:

| Method | Mechanism | When to reach for it |
|--------|-----------|----------------------|
| **DoReMi** — arXiv 2305.10429 | Train a small proxy with group-DRO to find domain weights that minimize worst-case excess loss; transfer weights to the full run. +6.5pp few-shot vs Pile defaults. | You have fixed domains and want robust weights without a full sweep. |
| **Data Mixing Laws** — arXiv 2403.16952 | Fit a scaling-law surface over mixture ratios from small proxy runs; extrapolate the optimum before spending full compute. | Predicting the optimal mix at target scale from cheap experiments. |
| **RegMix** — arXiv 2407.01492 | Train many small models on random mixtures, regress performance on ratios, pick the predicted-best mixture. Matches DoReMi at lower compute. | Compute-cheaper alternative to DoReMi; many candidate domains. |

Whichever you use, still validate the chosen mix with a held-out ablation run (Run E) — the methods set the prior, the ablation confirms it.

## Default Workflow

1. **Define corpus goal**: target language, domain distribution, token budget, training compute budget.
2. **Extract**: run datatrove `HTMLExtractor` over WARC dumps; keep URL + source metadata.
3. **Language filter**: fastText lid; log per-language token counts before and after.
4. **Heuristic filter**: apply Gopher + C4 rules; log drop rate per rule to identify dominant removals.
5. **Classifier filter**: train or apply FineWeb-Edu edu-score / custom classifier; set threshold on a held-out labeled set.
6. **Dedup**: MinHash + LSH near-dedup first (catches paragraph-level duplicates), then suffix-array exact-substring.
7. **Decontaminate**: match against every evaluation benchmark you plan to report; fail loud on any ≥ 13-gram overlap.
8. **PII / safety scrub**: regex sweep + safety classifier; document removal rates.
9. **Tokenize + shard**: produce indexed Parquet shards; verify document count and total token count.
10. **Mix + ablate**: design controlled ablation runs (one change per run); train small proxy model; measure eval delta with lm-evaluation-harness.
11. **Datasheet**: write Gebru et al. datasheet before publishing or using the corpus externally.

## Data Ablation Table

Run small proxy model (e.g., 1B param) at fixed compute budget. One change per run. Evaluate on the same benchmark suite with lm-evaluation-harness.

| Run | Corpus | Change vs Prior | Expected Signal |
|-----|--------|-----------------|-----------------|
| A | Raw CC extract (no filter) | Baseline | Noisy ceiling |
| B | +Heuristic filter + near-dedup | Gopher + MinHash | +3–8 pts on perplexity benchmarks |
| C | +Classifier filter | FineWeb-Edu score | +2–5 pts over heuristics alone |
| D | +Synthetic data (10% mix) | Cosmopedia / Self-Instruct | Varies by task domain |
| E | Method-driven mix (DoReMi / RegMix prior, then validate) | Vary web:books:code:synth | Identifies optimal mix for target tasks |

**Protocol**: hold compute constant across A–E. Evaluate on HellaSwag, ARC, MMLU, and a domain task. Do not change model architecture between runs. Do not change eval prompt format between runs. Decontaminate before each run independently.

## ASCII Heuristic Rules Cheat Sheet

```text
Gopher rules (sample):
  word_count: 50 ≤ n ≤ 100_000
  mean_word_length: 3 ≤ chars ≤ 10
  symbol_to_word_ratio: < 0.1  (symbols = #, %, |, …)
  fraction_lines_ending_ellipsis: < 0.3
  fraction_lines_starting_bullet: < 0.9
  stopword_density: ≥ 2 of {the, be, to, of, and, that, have, with} per 100 words

C4 rules (sample):
  no_lorem_ipsum: True
  no_javascript_warning: True  (blocks containing "javascript" must-be-enabled)
  line_terminal_punctuation: ≥ 0.95 of lines end in {. ! ? "}
  no_curly_braces: True  (proxy for code / template bleed)
  deduplicated_3gram: remove exact 3-gram repeated lines
```

## MinHash + LSH Banding Intuition

```text
Choose:
  n = 9  (shingle size in tokens)
  k = 128  (MinHash permutations)
  bands b = 20, rows r = 128/20 ≈ 6

P(collision) ≈ 1 - (1 - s^r)^b
At s=0.8 (80% Jaccard): P ≈ 0.86  -> most duplicates found
At s=0.5 (50% Jaccard): P ≈ 0.28  -> most near-matches missed (safe)

Increase b / decrease r to catch lower-Jaccard near-dups (more aggressive).
Decrease b / increase r to tighten threshold (less aggressive, faster).
```

## Known Traps

1. **Contamination** — the field's most common silent failure. Benchmark text appears in training data, scores look inflated, but the model learned the answer key. Decontaminate against every benchmark you plan to report, using n-gram overlap. Fail loud: if any document matches ≥ 13 grams, remove it and log the URL.

2. **Model collapse from synthetic data** — iteratively training on model outputs concentrates the distribution; tail capabilities and rare knowledge erode. Canonical reference: Shumailov et al., "AI models collapse when trained on recursively generated data," *Nature* 631:755–759 (2024), DOI 10.1038/s41586-024-07566-y. Mitigation: always mix human-sourced web data with synthetic; monitor output diversity metrics (distinct-n, entropy) during generation. The picture is more nuanced than "synthetic = collapse risk": scaling-law work on mixed corpora finds collapse is not inevitable at moderate synthetic ratios (arXiv 2510.01631, Oct 2025 — mixes around 1/3 rephrased-synthetic + 2/3 natural web reduced loss without collapse), and external verification against a stronger model or human judge — not just mixing — is the mechanism that reliably prevents collapse under fully recursive retraining (ICLR 2026 workshop, "Escaping Model Collapse via Synthetic Data Verification"). Treat "mix with real data" as necessary but insufficient; pair it with a verifier gate (see synthetic-data reference).

3. **Diversity collapse** — heavy classifier filtering removes stylistically unusual but high-quality text (dialects, domain jargon, informal registers). Check: does the filtered corpus have narrower vocabulary size and sentence-length distribution than the input?

4. **Generator contamination** — when a generative model produces synthetic data, it may reproduce memorized benchmark content. Decontaminate the synthetic data independently, not just the web data.

5. **Distillation licensing** — GPT-4 / Claude ToS prohibit using model outputs to train competing models. Verify the generator's license before mixing distilled data into a publicly released corpus.

6. **Single-change ablation discipline** — changing two variables in one run makes the delta uninterpretable. Always one change per run.

7. **EU AI Act training-data transparency (live enforcement risk, not theoretical)** — under Article 53(1)(d), GPAI model providers placing a model on the EU market must publish a "sufficiently detailed summary" of training content using the AI Office's mandatory template (published 2025-07-24), covering categories including crawled/scraped data, licensed data, user data, and synthetic data. The obligation took effect 2025-08-02 for new GPAI models (models already on the market by then have until 2027-08-02); the AI Office may begin compliance checks and corrective measures from 2026-08-02. Non-compliance exposes providers to fines up to €15M or 3% of global annual revenue. Separately, the DSM Directive Article 4 TDM exception requires crawlers to detect and honor machine-readable rightsholder opt-outs (robots.txt-style signals); the Commission is still finalizing standard opt-out protocols as of mid-2026. Practical implication for curation pipelines: log data-source category (crawled / licensed / synthetic / user) per document from Stage 0 onward — retrofitting this after the fact for a training-data summary is far more expensive than logging it during extraction.

## Common Anti-Patterns

- Pulling a HF dataset and calling it "curation" — curation requires documented filtering decisions and a datasheet.
- Running ablations with more than one pipeline change per run — you cannot attribute the eval delta.
- Reporting evaluation numbers without decontamination — always contamination-check first.
- Using the full-size model for ablations — proxy model at 1B params + fixed compute budget is the standard.
- Skipping PII scrub because "it's just pretraining data" — PII memorization is a real attack surface.

## Core Principles

1. **Every pipeline stage is a measurable research lever** — log drop rates, token counts, and eval deltas at each stage separately.
2. **One change per ablation run** — this is the entire discipline of data ablations.
3. **Decontaminate or your numbers lie** — fail loud on contamination; it is not optional.
4. **Verifier-gate synthetic data** — only include generated examples that pass a verifier or judge; unfiltered synthetic data degrades quality.
5. **Datasheet everything** — Gebru et al. datasheet for every dataset you publish or hand off.

## Navigation: Core References

- **[Web Curation Pipeline](references/web-curation-pipeline.md)** — datatrove stage-by-stage: WARC download, extraction, language ID, heuristic filter, dedup, decontamination
- **[Synthetic Data Generation](references/synthetic-data-generation.md)** — Cosmopedia / Self-Instruct / Evol-Instruct recipes, verifier gating, collapse traps
- **[Data Ablation Method](references/data-ablation-method.md)** — controlled-run protocol, proxy model setup, metric collection, datasheet

## External Sources

See **[data/sources.json](data/sources.json)** for curated primary sources across:

- Open corpus recipes and papers (FineWeb, Dolma, The Pile, RedPajama, C4, RefinedWeb)
- Deduplication and decontamination methods
- Synthetic data generation papers
- Evaluation harness

## Fact-Checking Rule

- Known bugs, regressions, framework/compiler/runtime footguns, and version-specific crash or workaround guidance must be verified against current primary web sources before being treated as current fact.
- Verify volatile external facts before final answers.
- Prefer official docs, standards, release notes, and GitHub READMEs.
- If you cannot verify, say so explicitly and present the guidance as a dated assumption instead of a fact.

## Learnings Loop

Before applying this skill on a non-trivial task, read `learnings.consolidated.md` in this directory (and `learnings.md` if present).

After applying it, if you encountered a pattern worth remembering, a mistake worth preventing, or a domain fact that surprised you, append one dated bullet to `learnings.md` via `agents-skills-feedback-loop/scripts/append_learning.py`. Do not modify `SKILL.md` itself.
