# Postgres FTS Tuning — tsvector Toolkit

Generative toolkit for the lexical leg of the vector brain. Each failure mode
is **Pattern → Anti-pattern → paste-ready recipe**. Companion SQL:
[`../assets/sql/008_fts_hardening.sql`](../assets/sql/008_fts_hardening.sql).
Query-side config is parameterized via `p_fts_config` in
[`../assets/sql/003_hybrid_search_function.sql`](../assets/sql/003_hybrid_search_function.sql).

> Verified against PostgreSQL 18 docs. `ts_rank`/`ts_rank_cd` is **not** Okapi
> BM25 — no IDF, no document-length saturation. If true BM25 ranking is the
> requirement, that is the `pg_search`/ParadeDB or search-engine path: see
> [`backend-selection-extended.md`](backend-selection-extended.md). Do not
> re-implement BM25 here.

## Table of Contents

- [Failure mode 1 — Exact tokens lost](#failure-mode-1--exact-tokens-lost)
- [Failure mode 2 — Ranking quality](#failure-mode-2--ranking-quality)
- [Failure mode 3 — fts_vector lifecycle](#failure-mode-3--fts_vector-lifecycle)
- [Failure mode 4 — Multilingual / config](#failure-mode-4--multilingual--config)
- [Cross-cutting — Debug loop](#cross-cutting--debug-loop)
- [Cross-cutting — Snippets (ts_headline)](#cross-cutting--snippets-ts_headline)
- [Advanced lever — RUM vs GIN](#advanced-lever--rum-vs-gin)

## Failure mode 1 — Exact tokens lost

**Pattern catalog**

- Use a stem-free `simple` + `unaccent` configuration for any content carrying
  identifiers, error codes, SKUs, version strings, or proper nouns.
- Layer the exact-token contribution at weight `A` in the *same* `fts_vector`
  rather than maintaining a second column.
- Add a `pg_trgm` typo-tolerant fallback on the identifier-bearing column for
  near-miss spellings.

**Anti-pattern catalog**

- Relying on the `english` config for code/identifier corpora — `english_stem`
  lowercases and stems, so `ERR_5012` → `err`, `v2.3.1` → `v`, destroying the
  exact tokens that should be the easiest to match.
- Wrapping `unaccent()` in a hand-rolled `IMMUTABLE` function to use it in a
  generated column — the index goes silently stale if the unaccent ruleset
  changes. Use a text-search **configuration** instead (the function is
  `STABLE`, configs with a constant name are immutable).
- A separate `pg_trgm` GIN index on full body text — trigram GIN bloats badly
  on long text. Index only the identifier/symbol column.
- Forgetting the cost of the full-body `simple` weight-`A` pass — running
  `section_path || content` through `vb_unaccent_simple` *in addition to* the
  stemmed `english` body roughly doubles weight-`A`/body lexeme volume. This is
  the **accepted** cost of in-prose exact-token recall, not a bug — but budget
  `tsvector` size against the 1 MB limit (see
  [Failure mode 3](#failure-mode-3--fts_vector-lifecycle)) accordingly.

**Recipe**

The exact-token layer is already built into
[`008_fts_hardening.sql`](../assets/sql/008_fts_hardening.sql) (the
`vb_unaccent_simple` weight-A contribution + `idx_chunks_symbol_trgm`). To
query the fuzzy fallback when an exact lexical match misses:

```sql
-- Typo-tolerant identifier lookup (threshold default 0.3).
SELECT id, symbol_name, similarity(symbol_name, :q) AS sml
FROM   chunks
WHERE  symbol_name % :q
ORDER  BY symbol_name <-> :q
LIMIT  10;
```

## Failure mode 2 — Ranking quality

**Pattern catalog**

- Assign `setweight` deliberately: navigational/title signal = `A`,
  summary = `B`, body = `C`. Default rank weight array is `{0.1, 0.2, 0.4,
  1.0}` for `{D, C, B, A}`.
- Prefer `ts_rank_cd` (cover-density) for prose where term proximity matters;
  `ts_rank` when only term frequency/weight matters.
- Use phrase (`<->`, `<N>`) and prefix (`:*`) operators for precision instead
  of broadening the query.

**Anti-pattern catalog**

- Re-tuning `ts_rank` normalization flags to "fix ranking" while RRF fusion in
  `003` is downstream — RRF consumes *rank position*, not the raw score, so
  pre-fusion score shaping is largely wasted. Tune at the right layer.
- `ts_rank` with no weight array and flag `0` on long documents — long bodies
  dominate by raw term count. If you must score length-fairly, use flag `2`
  (÷ length) or `32` (scale to 0..1).

**Recipe**

```sql
-- Inspect ranking in isolation BEFORE RRF, to choose flags empirically.
SELECT c.id,
       ts_rank_cd(c.fts_vector,
                  websearch_to_tsquery('vb_unaccent_english', :q),
                  32) AS rank_0_1
FROM   chunks c
WHERE  c.fts_vector @@ websearch_to_tsquery('vb_unaccent_english', :q)
ORDER  BY rank_0_1 DESC
LIMIT  20;
-- Normalization flags: 0 ignore len | 1 ÷1+log(len) | 2 ÷len |
-- 4 mean-harmonic-dist (ts_rank_cd only) | 8 ÷unique | 16 ÷1+log(unique) |
-- 32 ÷self+1 (0..1). Combine with | e.g. 2|32.
```

## Failure mode 3 — fts_vector lifecycle

**Pattern catalog**

- Default: a `GENERATED ALWAYS AS (...) STORED` column with a constant-named
  immutable config — zero application code, always consistent.
- Index with GIN (the preferred text-search index type).
- When the config must vary per row (mixed-language corpus), switch to a
  `BEFORE INSERT OR UPDATE` trigger — a generated column cannot choose its
  `regconfig` from another column.

**Anti-pattern catalog**

- Maintaining `fts_vector` from application code on write paths — every writer
  must remember; one that forgets silently under-indexes rows.
- Ignoring the documented limits: lexeme < 2 KB, **tsvector < 1 MB**,
  positions in `(0, 16383]`, ≤ 256 positions per lexeme, tsquery < 32768
  nodes. Positions past 16383 are **silently clamped to 16383** — the lexeme
  still matches (`@@` is unaffected), but `ts_rank_cd` proximity silently
  degrades on very large chunks because many late-document lexemes collapse to
  the same position. Separately, positions beyond the 256-per-lexeme cap are
  discarded. Guard chunk size; do not assume "it indexed" means "it ranked".
- Redefining the generated column in place — impossible; it requires
  DROP+ADD, which rewrites the table under `ACCESS EXCLUSIVE`. Plan a window
  or use the online parallel-column variant below.

**Recipe (online, zero-downtime alternative to 008's in-place supersede)**

```sql
-- Add the hardened vector as a NEW column, backfill, swap, drop old.
ALTER TABLE chunks ADD COLUMN fts_vector_v2 TSVECTOR GENERATED ALWAYS AS (
  setweight(to_tsvector('vb_unaccent_english', coalesce(section_path,'')), 'A')
  || setweight(to_tsvector('vb_unaccent_simple', coalesce(section_path,'') || ' ' || coalesce(content,'')), 'A')
  || setweight(to_tsvector('vb_unaccent_english', coalesce(contextual_summary,'')), 'B')
  || setweight(to_tsvector('vb_unaccent_english', coalesce(content,'')), 'C')
) STORED;
CREATE INDEX CONCURRENTLY idx_chunks_fts_v2 ON chunks USING GIN (fts_vector_v2);
-- cut 003 over to fts_vector_v2, verify, then:
-- DROP INDEX idx_chunks_fts; ALTER TABLE chunks DROP COLUMN fts_vector;
-- ALTER TABLE chunks RENAME COLUMN fts_vector_v2 TO fts_vector;
-- ALTER INDEX idx_chunks_fts_v2 RENAME TO idx_chunks_fts;
```

## Failure mode 4 — Multilingual / config

**Pattern catalog**

- Single dominant language: one constant config (the 008 default).
- Mixed language with a reliable per-row `chunks.language`: trigger-maintained
  `fts_vector` casting `language::regconfig` (commented variant in 008).
- Unknown/short text where stemming hurts more than helps: prefer `simple`.

**Anti-pattern catalog**

- Setting `default_text_search_config` and assuming generated columns follow it
  — a generated column's expression must name the config explicitly; it does
  not read the GUC.
- Building per-language dictionaries/thesaurus/synonym maps inside this skill —
  out of scope here; that is dictionary engineering. See
  [`deferred-extensions.md`](deferred-extensions.md).

**Recipe** — use the commented per-row-language trigger block in
[`008_fts_hardening.sql`](../assets/sql/008_fts_hardening.sql); map application
language codes to valid `regconfig` names before the cast.

## Cross-cutting — Debug loop

Every recipe above is diagnosable with three tools:

```sql
SELECT * FROM ts_debug('vb_unaccent_english', 'Café ERR_5012 restart');  -- tokenization
SELECT ts_lexize('unaccent', 'Café');                                    -- one dictionary
SELECT * FROM ts_stat('SELECT fts_vector FROM chunks') ORDER BY nentry DESC LIMIT 20; -- vocabulary
```

Anti-pattern: shipping a config change without `ts_debug` proof that the
target tokens survive tokenization.

## Cross-cutting — Snippets (ts_headline)

`ts_headline` turns a lexical hit into a displayable citation snippet for the
evidence contract ([`agent-tool-contract.md`](agent-tool-contract.md)).

```sql
SELECT ts_headline('vb_unaccent_english', c.content,
                    websearch_to_tsquery('vb_unaccent_english', :q),
                    'MaxFragments=2, MinWords=8, MaxWords=30, StartSel=<b>, StopSel=</b>')
FROM chunks c WHERE c.id = :hit_id;
```

Anti-pattern: running `ts_headline` over the whole candidate set — it
re-parses the document each call. Run it only on the final top-K after RRF.

## Advanced lever — RUM vs GIN

**Pattern:** RUM (`github.com/postgrespro/rum`) stores positions/rank *in* the
index → faster ranking (no heap scan), faster phrase search, fast
`ORDER BY rank/timestamp`. Use when read-heavy, phrase-heavy, rank-critical.

**Anti-pattern:** RUM on a write-heavy ingest path — build/insert is slower
than GIN. And RUM is a third-party extension: the build must match your
PostgreSQL major version; verify the release before relying on it (latest at
spec time: v1.3.15, 2025-10-23). Commented swap block is in
[`008_fts_hardening.sql`](../assets/sql/008_fts_hardening.sql).
