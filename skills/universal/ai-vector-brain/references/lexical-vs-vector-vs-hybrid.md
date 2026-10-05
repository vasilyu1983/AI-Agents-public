# Lexical vs Vector vs Hybrid — Choosing the Retrieval Leg

Generative decision toolkit for **which retrieval leg answers a given query**:
`tsvector` (lexical), `pgvector` (semantic), both fused with RRF (hybrid), or
plain SQL. For general hybrid-fusion theory (RRF parameters, when hybrid beats
single-leg retrieval in the abstract), see
`ai-rag/references/hybrid-fusion-patterns.md`; this file is the pgvector/
tsvector-specific decision matrix. This is the upstream choice the
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
| Code symbol / function name (`getUserById`, `vb_unaccent_simple`) | **Indexed key equality** for lookup; **tsvector** for prose mentioning it | Preserve case and punctuation in the key according to identifier semantics. `simple` also lowercases; the parser may split tokens before any dictionary runs. |
| Error / status code (`ERR_5012`, HTTP 429, `SIGSEGV`) | **Indexed code equality** for lookup; **lexical** for prose search | Tokenized search is not literal equality. Check parser output for codes and use a dedicated key when exact identity matters. |
| Pure intent, no shared vocabulary (*"stop charging my card"*) | **pgvector** | The doc that answers it says "cancel subscription / billing cycle" — zero lexical overlap with the query. |
| Exact anchor **and** intent (*"refund window in clause 7.3.2"*) | **Scoped hybrid**, RRF initially | Resolve the clause ID and constrain every leg to it when it is a hard requirement; rank the intent within that scope. A fusion weight cannot enforce a clause constraint. |
| Proper-noun / regulation lookup (*"GDPR Article 17 erasure"*) | **Scoped hybrid** for a hard article constraint; otherwise **hybrid** | Resolve article identity before ranking when it is mandatory. Tune lexical weights only for soft preferences; calibrated fusion belongs to [ai-rag hybrid-fusion-patterns.md](../../ai-rag/references/hybrid-fusion-patterns.md). |
| Accented / multilingual names (*"Beyoncé"*, *"Zürich"*) | **tsvector** with an unaccent **configuration** | Fold diacritics deterministically. Embedding behaviour across scripts/accents is inconsistent and untunable. |
| "More like this" / FAQ dedup / near-duplicate collapse | **pgvector** | Similarity *is* the entire task; there is no anchor token to match. |
| "How many tickets mention X" / boolean filter + count | **plain SQL** (`@@` or `ILIKE` + aggregate) | It is a count, not a ranking. A GIN index speeds up the `@@` predicate being counted; HNSW returns an approximate top-k, so it cannot establish an exhaustive count. |
| Mixed corpus: code **+** docs **+** policy in one brain | **hybrid + RRF** (assume until evals say otherwise) | The query distribution spans every row above; no single leg is safe by default. |
| Rare/exact-term precision dense misses but tsvector too brittle (typos, morphology, cross-lingual) | **learned-sparse leg** (SPLADE/ELSER added to hybrid RRF) | Dense blurs rare terms; tsvector collapses on inflection. Learned sparse captures both exact-token weight and semantic expansion. Adopt only after labeled eval confirms the gap — see [learned-sparse-splade-leg.md](learned-sparse-splade-leg.md). |

## Smell test

Route in this order; stop when the query shape is covered.

1. **Count, aggregate, latest, or as-of fact?** → typed SQL, with identifiers
   in the predicate. Count exhaustive matches rather than ranked top-k.
2. **Only an exact identifier lookup?** → indexed key equality, with explicit
   case and punctuation semantics. Return the typed result without fusion.
3. **Anchor plus semantic intent?** → hybrid. If the anchor is a hard clause,
   document, or code constraint, resolve its key and constrain every leg first.
4. **Only tokenized terms or prose mentioning an identifier?** → lexical.
   Use `simple`/unaccent where appropriate, and check parser output; FTS is
   not verbatim equality.
5. **Pure semantic intent?** → vector. If the intent is mixed or uncertain,
   start with hybrid and compare legs on a labeled eval.

After selecting the legs, add learned sparse only if a labeled eval exposes
rare-term or vocabulary gaps that lexical+dense retrieval does not close.

## Worked examples

**1 — `TimeoutError retry backoff` (engineer searching a code+docs brain)**
Resolve `TimeoutError` as an exact symbol constraint if the caller requires
that class; retrieve retry/backoff prose within its scope. For general mentions,
start with lexical search and inspect parser output. Add the semantic leg only
if the judged query set shows a vocabulary gap.

**2 — *"the app keeps logging me out"* (support brain)**
Zero overlap with the doc that answers it ("session expiry, refresh-token
rotation"). Pure **pgvector**. A lexical leg here matches nothing useful and
only adds RRF noise — if evals confirm, drop it for this query class.

**3 — *"GDPR Article 17 data deletion timeline"* (compliance brain)**
If Article 17 is mandatory, resolve its typed article key and apply that
constraint to both legs before retrieving evidence about the deletion timeline.
Use hybrid within the scope. For a soft article preference, tune lexical weights
or normalized score fusion on a judged set; neither guarantees article identity.
See [hybrid-fusion-patterns.md](../../ai-rag/references/hybrid-fusion-patterns.md).
Refusal-on-no-evidence still applies — a high cosine score is not a citation.

**4 — *"Beyoncé tour dates"* (proper-noun-heavy docs brain)**
Users type `Beyonce` and `Beyoncé` interchangeably. **tsvector** over an
unaccent *configuration* (not an `IMMUTABLE` wrapper) folds both to one
lexeme. pgvector cannot be relied on to treat the two spellings identically.

**5 — Hypothetical: *"Metformin hydrochloride extended-release 500 mg NDC 71610-027-39"* (pharmaceutical corpus)**
Dense retrieval may confuse nearby formulations; tokenized FTS may split the
code or miss synonymous wording. Resolve the NDC with exact key equality and
apply typed formulation/dose constraints when required. Search prose within
that scope. Learned sparse may improve synonym recall, but does not guarantee
preservation of a full code or dose. Compare lexical+dense with a learned-sparse
leg using labeled near-miss cases (different code, dose, or formulation).
No rank or threshold outcome has been measured for this example.

## Patterns

- **Pick the leg from the query, default to hybrid only when the query
  distribution is genuinely mixed.** A single-purpose brain (pure code search,
  pure FAQ) often needs only one leg; paying for two is waste, not safety.
- **Default to RRF without labels.** Once a judged set exists, evaluate a
  calibrated convex combination of normalized scores against RRF; follow
  [hybrid-fusion-patterns.md](../../ai-rag/references/hybrid-fusion-patterns.md).
  Adding raw `ts_rank` and cosine scores is not calibrated fusion.
- **Filter ACL / authority / `as_of` inside *both* CTEs before fusion.**
  Post-fusion filtering corrupts RRF ranks and can leak rows. See
  [`postgres-pgvector-default.md`](postgres-pgvector-default.md).
- **For filtered ANN queries with recall loss, evaluate iterative scans**
  (pgvector ≥ 0.8.0), partial indexes, or partitions. Exact filtered search
  may be faster for a selective subset and needs no iterative ANN scan.
  ANN filters run after the index scan; iterative scans can still hit budgets.
  `relaxed_order` allows better recall but
  may return rows slightly out of distance order; RRF assigns ranks by
  position, so re-sort in an outer query over a materialized CTE
  (`ORDER BY distance + 0` on Postgres 17+) or use `strict_order`.
- **Use a named `TEXT SEARCH CONFIGURATION` for unaccent**, never a hand-rolled
  `IMMUTABLE` wrapper — see [`postgres-fts-tuning.md`](postgres-fts-tuning.md)
  failure mode 4.

## Anti-patterns

- **Pure vector search for code, policy, or proper-noun corpora.** FTS exists
  because substring/semantic matching has "no linguistic support" and "no
  ordering" — discarding the lexical leg re-introduces exactly that gap.
- **Adding raw `ts_rank` and cosine scores.** Their scales differ; normalized
  score fusion needs calibration and comparison with RRF on judged queries.
- **Treating FTS as exact identifier equality.** Parser splitting, lowercasing,
  stemming and unaccent can change identity. Keep exact keys beside prose FTS;
  inspect `ts_debug` output before choosing a text-search configuration.
- **Reaching for a vector index to answer a `COUNT`.** HNSW top-k is
  approximate and cannot establish an exhaustive count; a plain SQL predicate
  (GIN-indexed for `@@`) is exact and faster.
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
- **Filtered ANN can return plausible rows with inadequate recall.** Compare
  against exact search under the same filters; evaluate strict/relaxed iterative
  scans and their budgets rather than assuming one setting fixes every query.
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

Identifier semantics: [PostgreSQL parser](https://www.postgresql.org/docs/current/textsearch-parsers.html)
and [simple dictionary](https://www.postgresql.org/docs/current/textsearch-dictionaries.html#TEXTSEARCH-SIMPLE-DICTIONARY).
Filtered ANN and ordering: [pgvector filtering](https://github.com/pgvector/pgvector#filtering)
and [iterative scans](https://github.com/pgvector/pgvector#iterative-index-scans).
