# Lexical vs Vector vs Hybrid — Choosing the Retrieval Leg

Generative decision toolkit for **which retrieval leg answers a given query**:
`tsvector` (lexical), `pgvector` (semantic), both fused with RRF (hybrid), or
plain SQL. This is the upstream choice the
[`postgres-pgvector-default.md`](postgres-pgvector-default.md) hybrid function
and [`postgres-fts-tuning.md`](postgres-fts-tuning.md) lexical toolkit assume
you have already made — pick the leg from the *query*, then tune the leg.

> Verified against PostgreSQL 18 docs and the pgvector README. PostgreSQL
> full-text search exists precisely because substring operators have **"no
> linguistic support"** and **"no ordering (ranking) of search results"**;
> vector search exists because lexical search cannot match intent that shares
> no vocabulary with the answer. Neither subsumes the other — the failure mode
> is forcing one leg to do the other leg's job.

## Table of Contents

- [Decision matrix](#decision-matrix)
- [Smell test](#smell-test)
- [Worked examples](#worked-examples)
- [Patterns](#patterns)
- [Anti-patterns](#anti-patterns)
- [Known traps](#known-traps)
- [Verified against](#verified-against)

## Decision matrix

Map the **query shape**, not the corpus average, to a leg.

| Query / need | Leg | Why |
|---|---|---|
| Code symbol / function name (`getUserById`, `vb_unaccent_simple`) | **tsvector** (`simple`+`unaccent`, weight A) | The identifier *is* the answer key. Stemming mangles it (`getUserById`→`getuserbyid`); embeddings blur near-identical symbols. |
| Error / status code (`ERR_5012`, HTTP 429, `SIGSEGV`) | **tsvector** | The token is exact and rare. Semantic similarity adds noise, not signal. |
| Pure intent, no shared vocabulary (*"stop charging my card"*) | **pgvector** | The doc that answers it says "cancel subscription / billing cycle" — zero lexical overlap with the query. |
| Exact anchor **and** intent (*"refund window in clause 7.3.2"*) | **hybrid + RRF** | `7.3.2` is lexical-exact; "refund window" is semantic. One leg alone drops half the signal. |
| Proper-noun / regulation lookup (*"GDPR Article 17 erasure"*) | **hybrid, lexical leg weighted up** | `Article 17` must match verbatim; "erasure timeline" is semantic. Bias RRF toward the lexical rank. |
| Accented / multilingual names (*"Beyoncé"*, *"Zürich"*) | **tsvector** with an unaccent **configuration** | Fold diacritics deterministically. Embedding behaviour across scripts/accents is inconsistent and untunable. |
| "More like this" / FAQ dedup / near-duplicate collapse | **pgvector** | Similarity *is* the entire task; there is no anchor token to match. |
| "How many tickets mention X" / boolean filter + count | **plain SQL** (`@@` or `ILIKE` + aggregate) | It is a count, not a ranking. Neither GIN nor HNSW improves a `COUNT`. |
| Mixed corpus: code **+** docs **+** policy in one brain | **hybrid + RRF** (assume until evals say otherwise) | The query distribution spans every row above; no single leg is safe by default. |
| Rare/exact-term precision dense misses but tsvector too brittle (typos, morphology, cross-lingual) | **learned-sparse leg** (SPLADE/ELSER added to hybrid RRF) | Dense blurs rare terms; tsvector collapses on inflection. Learned sparse captures both exact-token weight and semantic expansion. Adopt only after labeled eval confirms the gap — see [learned-sparse-splade-leg.md](learned-sparse-splade-leg.md). |

## Smell test

Four questions, in order. Stop at the first that fires.

1. **Is there a token that must appear verbatim in the answer?** (identifier,
   code, clause number, proper noun) → the **tsvector** leg is required.
2. **Is the match pure intent with no shared vocabulary?** → the **pgvector**
   leg is required.
3. **Both, or you cannot tell, or the corpus is code+docs+policy?** →
   **hybrid + RRF** until a labeled eval proves one leg is dead weight.
4. **Boolean predicate plus a count/aggregate, not a ranking?** → **plain
   SQL**. No vector index, no relevance ranking — it is an aggregate query
   wearing a search costume.
5. **Rare/exact terms dense misses but tsvector is too brittle?** → add the learned-sparse leg — see [learned-sparse-splade-leg.md](learned-sparse-splade-leg.md).

## Worked examples

**1 — `TimeoutError retry backoff` (engineer searching a code+docs brain)**
Verbatim tokens (`TimeoutError`) dominate. Lexical leg, `simple`+`unaccent`
weight-A contribution catches the identifier; the stemmed body still catches
"retry/backoff" prose. pgvector leg adds little — keep it for RRF but expect
the lexical rank to win.

**2 — *"the app keeps logging me out"* (support brain)**
Zero overlap with the doc that answers it ("session expiry, refresh-token
rotation"). Pure **pgvector**. A lexical leg here matches nothing useful and
only adds RRF noise — if evals confirm, drop it for this query class.

**3 — *"GDPR Article 17 data deletion timeline"* (compliance brain)**
`Article 17` is an exact anchor that *must* match; "deletion timeline" is
semantic. **Hybrid**, with the lexical leg weighted up so a body that cites
Article 17 outranks a semantically-close paragraph that never names it.
Refusal-on-no-evidence still applies — a high cosine score is not a citation.

**4 — *"Beyoncé tour dates"* (proper-noun-heavy docs brain)**
Users type `Beyonce` and `Beyoncé` interchangeably. **tsvector** over an
unaccent *configuration* (not an `IMMUTABLE` wrapper) folds both to one
lexeme. pgvector cannot be relied on to treat the two spellings identically.

**5 — *"Metformin hydrochloride extended-release 500 mg NDC 71610-027-39"* (pharmaceutical corpus)**
This query has two distinct failure modes. Dense retrieval: the embedding
clusters near "diabetes medication" docs but misses the specific NDC code and
formulation — cosine distance cannot discriminate a 500 mg from a 1000 mg
variant at the retrieval stage. tsvector: the full 10-digit NDC is an
identifier, so the exact-match leg is correct in theory, but inflected synonyms
("metformin HCl", "metformin hydrochloride") that appear in the target document
are not lexemes of the query tokens; the brittle tokenisation loses the match.
**Learned-sparse leg** closes both gaps: SPLADE expands "metformin
hydrochloride" to co-occurring tokens ("HCl", "antidiabetic", "biguanide") via
learned associations, while preserving the high weight on the exact NDC token.
Result: the 500 mg variant surfaces at rank 1; the 1000 mg variant ranks below
threshold. Adopt this leg only after a labeled eval confirms the failure mode —
if the hybrid (lexical+dense) already passes the pharmaceutical eval, the
learned-sparse leg adds cost without measurable gain.

## Patterns

- **Pick the leg from the query, default to hybrid only when the query
  distribution is genuinely mixed.** A single-purpose brain (pure code search,
  pure FAQ) often needs only one leg; paying for two is waste, not safety.
- **Fuse on rank position with RRF, not on blended scores.** The pgvector
  README explicitly recommends Reciprocal Rank Fusion or a cross-encoder to
  combine lexical and vector results — rank fusion, never `ts_rank + cosine`
  arithmetic.
- **Filter ACL / authority / `as_of` inside *both* CTEs before fusion.**
  Post-fusion filtering corrupts RRF ranks and can leak rows. See
  [`postgres-pgvector-default.md`](postgres-pgvector-default.md).
- **For any filtered vector query, set
  `hnsw.iterative_scan = 'relaxed_order'`.** A selective `WHERE` without it
  silently destroys recall (pgvector ≥ 0.8.0).
- **Use a named `TEXT SEARCH CONFIGURATION` for unaccent**, never a hand-rolled
  `IMMUTABLE` wrapper — see [`postgres-fts-tuning.md`](postgres-fts-tuning.md)
  failure mode 4.

## Anti-patterns

- **Pure vector search for code, policy, or proper-noun corpora.** FTS exists
  because substring/semantic matching has "no linguistic support" and "no
  ordering" — discarding the lexical leg re-introduces exactly that gap.
- **Blending `ts_rank` and cosine into one score before fusion.** RRF consumes
  *rank position*, not raw score; pre-fusion score shaping is wasted compute
  and biases nothing predictably.
- **One `english` config for an identifier corpus.** `english_stem` destroys
  exact tokens (`ERR_5012`→`err`). Layer a weight-A `simple`+`unaccent` leg.
- **Reaching for a vector index to answer a `COUNT`.** Neither GIN nor HNSW
  ranks an aggregate; a plain SQL predicate is correct and faster.
- **Tuning chunk size, embedder, or `ts_rank` normalization before deciding
  the leg.** The leg choice dominates every downstream knob. Decide it first.

## Known traps

- **`ts_rank`/`ts_rank_cd` is not BM25.** No IDF, no document-length
  saturation — it rewards keyword stuffing and a relevance `ORDER BY` on a
  large table can collapse from sub-second to tens of seconds. True BM25 is
  the `pg_search`/ParadeDB path, not a `ts_rank` tuning exercise. See [`bm25-when-ts_rank-isnt-enough.md`](bm25-when-ts_rank-isnt-enough.md).
- **"It indexed" ≠ "it ranked".** tsvector positions past 16383 are silently
  clamped (the lexeme still matches via `@@`; `ts_rank_cd` proximity
  degrades), positions beyond 256 per lexeme are discarded, and a tsvector
  caps at 1 MB. Long chunks rank worse than they appear to.
- **GIN vs GiST is a write/size/proximity tradeoff, not a ranking lever.**
  Neither index changes relevance order — choosing GiST will not "fix bad
  results", it only changes build/update cost and lossiness.
- **A selective `WHERE` on the vector leg without
  `hnsw.iterative_scan = 'relaxed_order'` looks healthy and returns rows** —
  it just silently drops the most relevant ones. The query never errors.
- **"It returned results" ≠ "it is relevant".** Verify the leg choice with a
  labeled retrieval eval, not by eyeballing top-k. A confident wrong leg is
  the most expensive outcome here.

## Verified against

| Claim | Source id |
|---|---|
| FTS purpose: "no linguistic support", "no ordering (ranking)", `tsvector`/`@@`, proximity ranking | `pg-textsearch-intro` |
| RRF / cross-encoder is the recommended hybrid combiner | `pgvector-readme` |
| `hnsw.iterative_scan`, `relaxed_order`, filtered-recall behaviour | `pgvector-readme`, `pgvector-releases` |
| `ts_rank` not BM25; `setweight`; normalization | `pg-textsearch-controls` |
| tsvector / position / lexeme limits (16383, 256, 1 MB) | `pg-textsearch-limitations` |
| GIN vs GiST tradeoff, not a ranking lever | `pg-textsearch-indexes` |
| unaccent via `TEXT SEARCH CONFIGURATION`, not `IMMUTABLE` wrapper | `pg-unaccent` |
