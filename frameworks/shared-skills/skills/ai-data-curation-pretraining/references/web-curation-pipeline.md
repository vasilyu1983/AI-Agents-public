# Web Curation Pipeline Reference

Canonical source: [ai-data-curation-pretraining/SKILL.md](../SKILL.md)

## Table of Contents

- [Stage 0: WARC Acquisition](#stage-0-warc-acquisition)
- [Stage 1: Extraction](#stage-1-extraction)
- [Stage 2: Language Identification](#stage-2-language-identification)
- [Stage 3: Heuristic Quality Filtering](#stage-3-heuristic-quality-filtering)
- [Stage 4: Classifier-Based Quality Filtering](#stage-4-classifier-based-quality-filtering)
- [Stage 5: Near-Deduplication — MinHash + LSH](#stage-5-near-deduplication--minhash--lsh)
- [Stage 6: Exact-Substring Deduplication](#stage-6-exact-substring-deduplication)
- [Stage 6b: Semantic Deduplication (optional, frontier)](#stage-6b-semantic-deduplication-optional-frontier)
- [Stage 7: Decontamination](#stage-7-decontamination)
- [Stage 8: PII and Safety Scrub](#stage-8-pii-and-safety-scrub)
- [Stage 9: Tokenization and Sharding](#stage-9-tokenization-and-sharding)
- [Logging Discipline](#logging-discipline)

---

## Stage 0: WARC Acquisition

CommonCrawl releases ~80 crawls since 2013; each contains WARC (Web ARChive) files at `s3://commoncrawl/`.

```bash
# List available crawls
aws s3 ls s3://commoncrawl/crawl-data/ --no-sign-request

# Download a WARC segment
aws s3 cp s3://commoncrawl/crawl-data/CC-MAIN-2024-10/segments/.../warc/*.warc.gz . --no-sign-request
```

With datatrove, use `CommonCrawlWARCReader` to stream WARC records without downloading full dumps. Preferred for cluster jobs.

**Decision**: which crawls to include? Recent crawls (< 2 years) have less spam but fewer URLs. Stacking multiple crawls increases token count but also duplicate rate — run dedup after stacking.

---

## Stage 1: Extraction

**Tool**: `datatrove.pipeline.extractors.Trafilatura` or `datatrove.pipeline.readers.WARCReader` + `HTMLExtractor`.

trafilatura strips HTML boilerplate (nav, footer, sidebars, ads) using a combination of HTML tree analysis and density heuristics. It outperforms newspaper3k and goose3 on recall for body text.

```python
from datatrove.pipeline.extractors import Trafilatura
from datatrove.pipeline.readers import WARCReader

pipeline = [
    WARCReader("s3://commoncrawl/..."),
    Trafilatura(timeout=0.5, favour_recall=True),
]
```

`favour_recall=True` keeps more text at the cost of some nav bleed — better for large-scale curation where downstream filtering cleans residual noise.

**Metadata to keep**: URL, WARC timestamp, content-type, HTTP status code, crawl ID. These fields are needed for decontamination, datasheets, and debugging quality issues.

---

## Stage 2: Language Identification

**Tool**: `fastText` language identification model (`lid.176.bin`, 176 languages) for English-heavy or bilingual corpora. For 1000+ language coverage or heavy code-switching, use **GlotLID** (the model FineWeb2, arXiv 2506.20920, standardized on) or **OpenLID** instead — lid.176's 176-language ceiling under-serves low-resource languages and its confidence calibration degrades on code-switched text.

```python
import fasttext

model = fasttext.load_model("lid.176.bin")
label, score = model.predict(text.replace("\n", " "), k=1)
# label is '__label__en', score is confidence
```

**Threshold guidance**:
- `≥ 0.65`: standard for large multilingual corpora; keeps dialectal and code-switched text
- `≥ 0.80`: use for English-only corpora where you want less multilingual bleed
- `≥ 0.90`: conservative; loses some valid text from pages with mixed-language headers

Log per-language token counts before and after. A sudden drop in a language indicates an upstream extraction issue, not a language-ID problem.

---

## Stage 3: Heuristic Quality Filtering

Apply Gopher (Rae et al., DeepMind 2021) and C4 (Raffel et al.) rules sequentially. Each rule removes a distinct noise type.

**Gopher rules** (document-level):

| Rule | Threshold | Noise Targeted |
|------|-----------|----------------|
| `word_count` | 50 ≤ n ≤ 100,000 | Stubs and near-infinite pages |
| `mean_word_length` | 3–10 chars | Garbled encodings, hashtag spam |
| `symbol_to_word_ratio` | < 0.1 | Code bleed, markdown tables, ASCII art |
| `fraction_lines_ending_ellipsis` | < 0.3 | Paginated content, truncated SEO pages |
| `fraction_lines_starting_bullet` | < 0.9 | Nav-heavy or list-only pages |
| `stopword_density` | ≥ 2 stopwords per 100 words | Non-prose content (logs, CSS) |

**C4 rules** (line- and document-level):

| Rule | Logic | Noise Targeted |
|------|-------|----------------|
| `no_javascript_warning` | Drop docs with "javascript must be enabled" | Browser-warning fallback pages |
| `line_terminal_punctuation` | ≥ 0.95 lines end in `. ! ? "` | Nav lists, broken extraction |
| `no_curly_braces` | Drop docs containing `{` or `}` | Template/code bleed |
| `deduplicated_3gram` | Remove exact duplicate lines within document | Boilerplate repeated headers/footers |

**Log drop rate per rule**. If any single rule removes > 40% of documents, investigate whether extraction is producing garbage or the rule threshold is miscalibrated.

---

## Stage 4: Classifier-Based Quality Filtering

Train a binary classifier on human-labeled examples (high-quality vs. low-quality). FineWeb-Edu uses a DistilBERT classifier trained on Llama-3-70B annotations of educational quality.

**Why classifiers outperform heuristics**: heuristics target noise proxies (symbol ratio, bullet density); a classifier targets the construct of interest (educational value, factual density, writing quality). On FineWeb ablations, the edu-score classifier added 3–5 percentage points on ARC and HellaSwag over heuristics-only.

**Recipe**:
1. Sample 1,000–10,000 documents from heuristic-filtered corpus.
2. Annotate with a strong model (Llama-3-70B, GPT-4) using a quality rubric.
3. Train DistilBERT or a fastText classifier on annotations.
4. Set threshold on a held-out labeled set (target precision ≥ 0.85).
5. Apply to full corpus; log score distribution.

**Trap**: classifier trained on one domain generalizes poorly. If your corpus has significant code, math, or non-English content, train domain-specific classifiers or use separate filters per domain.

**Frontier baseline — DCLM (arXiv 2406.11794)**: the DataComp-LM benchmark showed that a single fastText classifier trained to separate a high-quality reference set (e.g., instruction-formatted / ELI5-style text) from random CommonCrawl beats large heuristic stacks under fixed compute. Replicate DCLM-Baseline filtering before hand-tuning Gopher thresholds; it is the current reference recipe for model-based filtering. For multilingual corpora, FineWeb-2 (arXiv 2506.20920) applies the same classifier approach with per-language thresholds.

**Token-yield caution**: aggressive edu/DCLM-style filtering discards ~90% of tokens. For multi-trillion-token runs, recover yield with synthetic rephrasing (Nemotron-CC, arXiv 2412.02595; WRAP, arXiv 2401.16380) rather than loosening the filter — see the synthetic-data reference.

---

## Stage 5: Near-Deduplication — MinHash + LSH

**Tool**: `datasketch.MinHash` + `datasketch.MinHashLSH`, or datatrove's built-in `MinhashDedupFilter`.

**Algorithm**:
1. Tokenize each document into overlapping n-grams (n=9 tokens is standard).
2. Compute MinHash signature: 128 hash permutations, each permutation produces one value representing the minimum hash over all n-grams.
3. Apply LSH banding: divide 128 permutations into `b` bands of `r` rows each. Two documents that share an identical band are candidate duplicates.
4. Compute exact Jaccard similarity for candidates; remove if Jaccard ≥ threshold (0.8 typical).

**Banding parameters** for 0.8 Jaccard threshold at 128 permutations: `b=20, r=6`.

```python
from datasketch import MinHash, MinHashLSH

lsh = MinHashLSH(threshold=0.8, num_perm=128)
m = MinHash(num_perm=128)
for shingle in shingles(text, n=9):
    m.update(shingle.encode("utf8"))
```

Near-dedup reduces the corpus by 20–40% on CommonCrawl; the exact fraction depends on crawl age and source diversity.

---

## Stage 6: Exact-Substring Deduplication

**Tool**: suffix-array based exact-substring matching (e.g., the `dedup` tool from Ippolito et al. 2022, used in The Pile and SlimPajama).

MinHash catches paragraph-level near-duplicates. Suffix-array catches short exact repeated sequences (boilerplate phrases, repeated legal disclaimers, repeated nav text) that MinHash misses because they constitute < 80% of the document.

Threshold: sequences of ≥ 50 tokens that appear in ≥ 2 documents are candidates for removal or truncation.

---

## Stage 6b: Semantic Deduplication (optional, frontier)

**Tool**: SemDeDup (arXiv 2303.09540) — embed each document (e.g., with a sentence encoder), cluster embeddings (k-means), and within each cluster drop documents whose cosine similarity to a kept neighbor exceeds a threshold.

MinHash and suffix-array catch *surface-form* duplicates. SemDeDup catches *semantic* near-duplicates — paraphrases, translations, lightly reworded reposts — that share little literal n-gram overlap. It **complements, does not replace** MinHash; run it after surface dedup. SemDeDup can remove ~50% of web data at minimal quality loss; tune the similarity threshold on a held-out ablation, since over-aggressive semantic dedup erases legitimately diverse coverage of common topics.

---

## Stage 7: Decontamination

**This is mandatory before reporting any evaluation numbers.**

**Method**: extract n-grams (n=13) from every evaluation benchmark split (train and test). Hash them. Scan corpus documents for any document containing a ≥ 13-gram match. Remove matching documents entirely.

Benchmarks to check: HellaSwag, ARC (Easy + Challenge), MMLU, WinoGrande, GSM8K, HumanEval, MBPP, TruthfulQA — and any domain-specific benchmark you plan to report.

**Fail loud**: log every removed document with its URL, the matching n-gram, and the benchmark it matched. Do not silently drop documents.

datatrove provides `SentenceDedupFilter` which can be repurposed for decontamination by treating benchmark sentences as the "duplicate" set.

---

## Stage 8: PII and Safety Scrub

**PII regex cascade** (fast, runs first):
- Email: `[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+`
- Phone (US): `\b\d{3}[-.]?\d{3}[-.]?\d{4}\b`
- SSN: `\b\d{3}-\d{2}-\d{4}\b`
- Credit card: Luhn-validated 13–19 digit sequences

**PII classifier** (slower, runs after regex): catches context-dependent PII (full name + address combinations, medical identifiers) that regex misses.

**Safety classifier**: hate speech, CSAM, graphic violence — use a pre-trained safety classifier (e.g., Perspective API, Llama Guard) or fine-tune on a labeled safety dataset.

Document removal rates at each step. Rates above 5% indicate a quality filtering gap upstream.

---

## Stage 9: Tokenization and Sharding

**Tokenizer choice**: match the tokenizer of the model you plan to train. HF tokenizers for open models; tiktoken for OpenAI-style vocabulary. Do not mix tokenizers across corpus shards.

**Shard size**: target ≤ 1 GB Parquet per shard for practical I/O. Larger shards slow down dataloader workers.

**Document boundary handling**: insert end-of-document tokens between documents within a shard. This prevents the model from learning cross-document context that would not exist at inference time.

**Verify**: after tokenization, assert total token count matches expected estimate (characters / 4 ≈ tokens for English). A 20%+ deviation indicates extraction or encoding issues.

---

## Logging Discipline

At each stage, log:
- Documents in / documents out
- Tokens in / tokens out
- Drop rate (%) and top drop reasons
- Wall-clock time and compute cost

Store logs in a structured format (JSON lines) alongside the corpus artifacts. These logs are the audit trail for the datasheet.
