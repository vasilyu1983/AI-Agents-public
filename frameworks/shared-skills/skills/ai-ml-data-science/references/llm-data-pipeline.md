# LLM Training Data Pipelines

Practical patterns for preparing large-scale text corpora for LLM pretraining and fine-tuning. Route here first when building an LLM from scratch or curating a pretraining mixture. For model selection, evaluation, and serving, see the sibling references.

---
## Table of Contents

- [1. Deduplication](#1-deduplication)
- [1.1 Exact Dedup](#11-exact-dedup)
- [1.2 Fuzzy Dedup — MinHash LSH](#12-fuzzy-dedup--minhash-lsh)
- [1.3 Semantic Dedup](#13-semantic-dedup)
- [1.4 Scale Guidance](#14-scale-guidance)
- [2. Quality Filtering](#2-quality-filtering)
- [2.1 Heuristic Filters](#21-heuristic-filters)
- [2.2 Classifier-Based Filters](#22-classifier-based-filters)
- [2.3 Model-Scoring Filters](#23-model-scoring-filters)
- [2.4 CQF Caveat](#24-cqf-caveat)
- [3. Synthetic Data Mixing](#3-synthetic-data-mixing)
- [4. Decontamination](#4-decontamination)
- [4.1 Detection Methods](#41-detection-methods)
- [4.2 Contamination-Resistant Benchmarks](#42-contamination-resistant-benchmarks)
- [Related Resources](#related-resources)


## 1. Deduplication

Deduplication is the highest-leverage single step in data curation. Duplicate documents inflate token counts, bias the model toward repeated phrasings, and inflate benchmark scores on seen text.

### 1.1 Exact Dedup

- Hash-based: SHA-256 or xxHash over normalized document text (strip whitespace, lowercase optional)
- Fast and cheap; catches byte-for-byte copies
- Always run exact dedup before fuzzy dedup

### 1.2 Fuzzy Dedup — MinHash LSH

- MinHash with Locality-Sensitive Hashing (LSH) finds near-duplicate documents without pairwise comparison
- Jaccard similarity threshold typically 0.7–0.8 for aggressive dedup; 0.85–0.9 for conservative
- Implementation references: `datasketch` (Python), `text-dedup` library
- Scales to hundreds of billions of tokens on a single machine or small cluster

### 1.3 Semantic Dedup

- Embed documents; cluster or threshold by cosine similarity
- Catches paraphrases and format-converted duplicates that evade MinHash
- Expensive: requires embedding inference at corpus scale
- Use selectively: apply to high-value domains or as a post-MinHash pass

### 1.4 Scale Guidance

| Corpus size | Recommended approach |
|-------------|----------------------|
| < 10 TB | Exact dedup + MinHash LSH |
| > 10 TB | Add Bloom filter for streaming exact dedup; keep MinHash for near-dup |
| All scales | Semantic dedup is a targeted pass, not a default |

**Bloom filter note:** At corpus sizes above ~10 TB, streaming exact dedup with a Bloom filter avoids loading the full hash set into memory. False-positive rate is tunable; 1e-6 is a typical target for large corpora.

---

## 2. Quality Filtering

### 2.1 Heuristic Filters

Apply first — cheap, interpretable, and effective at removing the worst content:

- Remove documents below minimum token count (e.g., < 50 tokens)
- Remove by content type: code dumps in prose corpora, boilerplate, navigational text
- Remove by repetition: character n-gram repetition ratio > threshold (e.g., same 20-gram repeating > 3 times)
- Remove by perplexity floor: documents with extremely low perplexity under a small LM may be templated boilerplate
- Language filter: keep target language(s); fastText lid.176 is standard for language identification

### 2.2 Classifier-Based Filters

- Train a fastText or similar binary classifier on high-quality vs low-quality documents
- Common training signal: web text curated by humans (Wikipedia, books, curated forums) as positive; random crawl as negative
- Apply score threshold; threshold is a quality dial — higher threshold keeps fewer but better documents

### 2.3 Model-Scoring Filters

- Use a small LM to score documents: low perplexity on a reference quality model indicates "on distribution"
- More expensive than fastText but captures subtler quality signals
- Apply after heuristic + classifier passes to avoid scoring junk

### 2.4 CQF Caveat

**Classifier quality filtering (CQF) limitation:** Filtering toward a reference classifier's training distribution improves downstream benchmark scores but does not necessarily improve LM performance on the reference corpus itself. The benchmark gains may reflect distribution match rather than genuine capability improvement. Cite: this pattern is described in corpus curation literature (verify against primary papers before asserting specific figures). Do not treat classifier filtering as unconditionally beneficial — it shapes the model's distribution, which may exclude useful diversity.

**Checklist: Quality Filtering**

- [ ] Heuristic passes applied first (length, repetition, language ID)
- [ ] Classifier or model-scoring applied after heuristics
- [ ] Threshold choices documented and reversible (filtered documents kept for audit)
- [ ] CQF limitation noted if classifier-filtered data is used in benchmark claims

---

## 3. Synthetic Data Mixing

Synthetic data (LLM-generated) can supplement natural text but does not replace it.

**Key constraints (hedge: specific ratios are dataset- and model-specific; verify against primary experiments):**

- Pure-synthetic pretraining does not consistently match natural-text pretraining on held-out evals
- Mixtures of natural + synthetic can outperform natural-only when synthetic fills coverage gaps (rare domains, instruction formats, reasoning chains)
- The optimal mixing ratio depends on the synthetic data generator quality, the domain, and the target task — no universal ratio is established
- A common pattern reported in the literature is using synthetic data for 20–50% of domain-specific fine-tuning data, not for the majority of pretraining; verify against the specific papers before asserting a ratio

**Anti-patterns:**
- Using purely synthetic data for pretraining and expecting benchmark parity with natural-data models
- Mixing synthetic without decontaminating against evaluation benchmarks (see §4)
- Synthetic-only instruction tuning without human-curated seed data for quality anchoring

**Checklist: Synthetic Mixing**

- [ ] Synthetic fraction is a deliberate choice, not a default
- [ ] Synthetic data source and generator model documented
- [ ] Decontamination run on synthetic data against target benchmarks
- [ ] Natural-vs-synthetic ablation exists or is planned

---

## 4. Decontamination

Contamination (test data appearing verbatim or near-verbatim in training data) inflates benchmark scores and makes comparisons unreliable.

### 4.1 Detection Methods

**MinHash near-duplicate detection:**
- Compute MinHash signatures for all benchmark examples
- Check against training corpus with LSH at low Jaccard threshold (0.5–0.7)
- Remove or quarantine matching training documents

**Min-K% Prob (Black-box contamination detection):**
- For a given text, extract the k% of tokens with lowest log-probability under the model
- Contaminated examples tend to have higher minimum-k% probability than non-contaminated examples
- Can be applied post-training to detect contamination without corpus access
- Reference: Min-K% Prob (arXiv 2310.16789, verify URL before citing)

**Exact string matching:**
- n-gram overlap (13-gram is a common threshold from LLaMA and similar work)
- Fast, but misses paraphrased contamination

### 4.2 Contamination-Resistant Benchmarks

When contamination risk is high (large crawled corpora, frequently cited benchmarks), prefer:

- Recently released benchmarks not present in the training window
- Private held-out test sets
- Benchmarks with procedural generation (new problems per evaluation run)
- Contamination-resistant benchmark suites (e.g., LiveBench, MMLU-Pro-style holdouts)

**Scope:** This section applies to LLM-based models or any setting where pretraining or fine-tuning data overlaps with evaluation data. For classical ML with small curated datasets, standard train/test split hygiene (see `modelling-patterns.md` §2) is sufficient.

**Checklist: Decontamination**

- [ ] MinHash near-dup run between training corpus and all target benchmarks
- [ ] Exact n-gram matching checked (13-gram or tighter)
- [ ] Contaminated documents quarantined and re-evaluated without them
- [ ] Min-K% Prob check considered for post-training contamination audit
- [ ] Benchmark choice accounts for contamination risk

---

## Related Resources

- [Modelling Patterns](modelling-patterns.md) - Model family selection and tabular baselines
- [Evaluation Patterns](evaluation-patterns.md) - Benchmark contamination detection and evaluation design
- [Data Contracts & Lineage](data-contracts-lineage.md) - Annotation quality and data governance
- [Reproducibility Checklist](reproducibility-checklist.md) - Experiment tracking and artifact versioning
