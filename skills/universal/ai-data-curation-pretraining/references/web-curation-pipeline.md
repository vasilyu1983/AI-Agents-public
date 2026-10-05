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

# To fetch a WARC locally, select an exact key from the crawl's warc.paths.gz manifest,
# then pass that key to aws s3 cp with --no-sign-request.
```

With datatrove, use `WarcReader` against a Common Crawl segment prefix; see the [FineWeb pipeline example](https://github.com/huggingface/datatrove/blob/main/examples/fineweb.py) for its current import and constructor.

**Decision**: which crawls to include? More snapshots increase the candidate pool and duplicate exposure. FineWeb deduplicated each snapshot separately after finding that global dedup left a lower-quality remainder in one older crawl. FineWeb2 instead deduplicated globally per language and used cluster-size-aware upsampling. Compare these scopes on your corpus before choosing one.

---

## Stage 1: Extraction

**Tool**: datatrove's `WarcReader` followed by `Trafilatura` for WARC HTML, as in its [FineWeb example](https://github.com/huggingface/datatrove/blob/main/examples/fineweb.py).

trafilatura strips HTML boilerplate (nav, footer, sidebars, ads) using a combination of HTML tree analysis and density heuristics. It outperforms newspaper3k and goose3 on recall for body text.

```python
from datatrove.pipeline.extractors import Trafilatura
from datatrove.pipeline.readers import WarcReader

pipeline = [
    WarcReader("s3://commoncrawl/crawl-data/CC-MAIN-2023-50/segments/", glob_pattern="*/warc/*"),
    Trafilatura(favour_precision=True),
]
```

Tune extraction precision versus recall with a held-out sample; the FineWeb example uses `favour_precision=True`.

**Metadata to keep**: URL, WARC timestamp, content-type, HTTP status code, crawl ID. These fields are needed for decontamination, datasheets, and debugging quality issues.

---

## Stage 2: Language Identification

**Tool**: `fastText` `lid.176.bin` for English-focused corpora. For broad multilingual coverage, consider **GlotLID**, which FineWeb2 selected for its language and script coverage; compare performance on your target languages before choosing. GlotLID labels include language-script variants, so label count is not a count of distinct languages.

```python
import fasttext

model = fasttext.load_model("lid.176.bin")
label, score = model.predict(text.replace("\n", " "), k=1)
# label is '__label__en', score is confidence
```

**Threshold guidance**: FineWeb's `0.65` was an English filtering choice, not a multilingual default. Calibrate each target language on labeled samples and its confidence-score distribution. FineWeb2 found that languages preferred materially different thresholds and used a per-language rule; see its [LID section](https://arxiv.org/html/2506.20920v1#S4.SS2).

Log per-language token counts before and after. Investigate a sudden drop for extraction errors, classifier confusion, or a miscalibrated threshold.

---

## Stage 3: Heuristic Quality Filtering

Apply Gopher (Rae et al., DeepMind 2021) and C4 (Raffel et al.) rules sequentially. Each rule removes a distinct noise type.

**Gopher rules** (document-level):

| Rule | Threshold | Noise Targeted |
|------|-----------|----------------|
| `word_count` | 50 ≤ n ≤ 100,000 | Stubs and near-infinite pages |
| `mean_word_length` | 3–10 chars | Garbled encodings, hashtag spam |
| `symbol_to_word_ratio` | ≤ 0.1 (hash `#` and ellipsis) | Hashtag spam, truncated SEO pages |
| `fraction_lines_ending_ellipsis` | < 0.3 | Paginated content, truncated SEO pages |
| `fraction_lines_starting_bullet` | < 0.9 | Nav-heavy or list-only pages |
| `alphabetic_words` | ≥ 80% of words contain an alphabetic character | Number/symbol soup |
| `stopwords` | ≥ 2 of {the, be, to, of, and, that, have, with} in the document | Non-prose content (logs, CSS) |

**C4 rules** (line- and document-level):

| Rule | Logic | Noise Targeted |
|------|-------|----------------|
| `no_javascript_lines` | Drop **lines** containing "javascript" | Browser-warning fallback text |
| `line_terminal_punctuation` | Keep only lines ending in `. ! ? "` | Nav lists, broken extraction |
| `min_words_per_line` / `min_sentences` | Keep lines with ≥ 5 words; drop pages with < 3 sentences | Menus, stubs |
| `three_sentence_dedup` | Keep one copy of any repeated three-sentence span | Boilerplate repeated across pages |
| `no_curly_braces` | Drop docs containing `{` or `}` | Template/code bleed |
| `deduplicated_3gram` | Remove exact duplicate lines within document | Boilerplate repeated headers/footers |

**Log drop rate per rule**. If any single rule removes > 40% of documents, investigate whether extraction is producing garbage or the rule threshold is miscalibrated.

---

## Stage 4: Classifier-Based Quality Filtering

Train a binary classifier on human-labeled examples (high-quality vs. low-quality). FineWeb-Edu uses a DistilBERT classifier trained on Llama-3-70B annotations of educational quality.

**Why test classifiers**: heuristics target noise proxies (symbol ratio, bullet density); a classifier can target a labeled construct such as educational value. Compare it with the heuristic baseline under a fixed training budget rather than assuming an uplift.

**Recipe**:
1. Sample 1,000–10,000 documents from heuristic-filtered corpus.
2. Annotate with a strong model (Llama-3-70B, GPT-4) using a quality rubric.
3. Train DistilBERT or a fastText classifier on annotations.
4. Set threshold on a held-out labeled set (target precision ≥ 0.85).
5. Apply to full corpus; log score distribution.

**Trap**: classifier trained on one domain generalizes poorly. If your corpus has significant code, math, or non-English content, train domain-specific classifiers or use separate filters per domain.

**Frontier baseline — DCLM (arXiv 2406.11794)**: the DataComp-LM benchmark showed that model-based filtering is effective under fixed compute. Replicate DCLM-Baseline filtering before hand-tuning Gopher thresholds. For multilingual corpora, FineWeb2 instead adapted language-ID and heuristic-filter thresholds per language; it did not reuse the DCLM quality classifier.

**Token-yield caution**: aggressive edu/DCLM-style filtering discards ~90% of tokens. For multi-trillion-token runs, recover yield with synthetic rephrasing (Nemotron-CC, arXiv 2412.02595; WRAP, arXiv 2401.16380) rather than loosening the filter — see the synthetic-data reference.

---

## Stage 5: Near-Deduplication — MinHash + LSH

**Tool**: `datasketch.MinHash` + `datasketch.MinHashLSH`, or datatrove's built-in `MinhashDedupFilter`.

**Algorithm**:
1. Shingle each document into overlapping word n-grams (FineWeb uses 5-grams; there is no single standard n).
2. Compute MinHash signature: k hash permutations (FineWeb: 112), each permutation produces one value representing the minimum hash over all n-grams.
3. Apply LSH banding: divide the k permutations into `b` bands of `r` rows each (b·r = k). Two documents that share an identical band are candidate duplicates.
4. Compute exact Jaccard similarity for candidates; remove if Jaccard ≥ threshold (0.8 typical).

**Banding parameters**: P(candidate) = 1 − (1 − s^r)^b, steepest near s ≈ (1/b)^(1/r). FineWeb: 14 bands × 8 rows (≈0.72 threshold, targeting ≈75% similarity). Do not use `b=20, r=6` for a 0.8 target: that is 120 permutations, threshold ≈0.61, and it flags 27% of pairs at s = 0.5. With `MinHashLSH(threshold=0.8, num_perm=128)` and equal false-positive/negative weights, the error-minimizing split is 9 × 13 (our computation of datasketch's criterion), which catches only ≈40% of pairs at exactly 0.8; print `lsh.b, lsh.r` to see what your version chose. Table in [SKILL.md](../SKILL.md#minhash--lsh-banding-intuition).

```python
from datasketch import MinHash, MinHashLSH

lsh = MinHashLSH(threshold=0.8, num_perm=128)
m = MinHash(num_perm=128)
for shingle in shingles(text, n=5):
    m.update(shingle.encode("utf8"))
```

Measure the retained fraction per crawl and language; it depends on the source mix and dedup scope.

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

**Method**: extract n-grams from every evaluation benchmark split (train and test), hash them, and scan corpus documents for matches. Choose n per benchmark: long passages tolerate GPT-3's 13-grams, short items (math answers, code lines, multiple-choice stems) need smaller n; Llama 3 scored 8-gram overlap. Report the contamination rate per benchmark, then remove or flag matching documents.

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

Document removal rates at each step; investigate unexpected spikes against a labeled sample.

---

## Stage 9: Tokenization and Sharding

**Tokenizer choice**: match the tokenizer of the model you plan to train. HF tokenizers for open models; tiktoken for OpenAI-style vocabulary. Do not mix tokenizers across corpus shards.

**Shard size**: choose from measured dataloader throughput, object-store request cost, and worker parallelism; record the size used for reproducibility.

**Document boundary handling**: insert end-of-document tokens between documents within a shard. This prevents the model from learning cross-document context that would not exist at inference time.

**Verify**: count tokens with the exact training tokenizer and reconcile the sum of shard token counts with the pre-shard count. Investigate any mismatch before training.

---

## Logging Discipline

At each stage, log:
- Documents in / documents out
- Tokens in / tokens out
- Drop rate (%) and top drop reasons
- Wall-clock time and compute cost

Store logs in a structured format (JSON lines) alongside the corpus artifacts. These logs are the audit trail for the datasheet.
