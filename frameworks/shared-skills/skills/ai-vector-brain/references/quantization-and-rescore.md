# Quantization + Two-Pass Rescore

Vector quantization compresses dense embeddings to a cheaper bit representation for a fast first-pass ANN walk, then rescores the top candidates at full float32 precision to recover recall. This toolkit covers the default-tier RAM/latency/cost relief recipe: an HNSW expression index on `binary_quantize(embedding)` (no materialized column, no UPDATE backfill) followed by an exact cosine rescore pass. It fills a real gap — the default brain's SKILL.md operational defaults have no quantization recipe, and `graph-theory-at-scale.md` covers only the 100M+ scale tier with a different materialized-column approach. This reference is NOT a scale-tier guide and NOT a substitute for an eval-measured recall budget.

> Verified against primary sources (see Verified-against table). Scope: default tier, single-node pgvector brain, before any scale escalation.

## Table of Contents
- [When you need this](#when-you-need-this)
- [Decision](#decision)
- [Worked recipe — pgvector binary_quantize + two-pass rescore](#worked-recipe--pgvector-binary_quantize--two-pass-rescore)
- [Per-backend coverage](#per-backend-coverage)
- [Anti-patterns](#anti-patterns)
- [Known traps](#known-traps)
- [Verified against](#verified-against)

## When you need this

**Trigger:** RAM or query-latency budgets are failing evals on the default single-node brain. The symptom is typically that ANN scan cost or heap footprint is the bottleneck, not retrieval quality — meaning the corpus is large enough that float32 vector storage is materially expensive per query.

**When you do NOT need this:**

- Corpus < ~100k vectors — premature optimization; the overhead adds no measurable benefit and the recall-loss measurement cost outweighs the gain. See SKILL.md anti-pattern: "ingesting tens of millions of vectors because storage is cheap."
- Corpus is already in the scale tier where `graph-theory-at-scale.md`'s materialized-column SBQ/PQ/DiskANN path applies — point there, not here.
- Embedding dimension < ~512 — quantization noise dominates recall loss; the rescore step cannot fully recover it.

## Decision

This is a **storage/latency-tier optimization**, NOT a retrieval-leg choice — it does not change the lexical-vs-vector-vs-hybrid leg selection in [lexical-vs-vector-vs-hybrid.md](lexical-vs-vector-vs-hybrid.md). Quantize the vector leg independently; the lexical leg and RRF fusion are unaffected.

**Default-tier decision:** use `binary_quantize(embedding)::bit(N)` as an HNSW expression index (no extra column) + two-pass cosine rescore. See the worked recipe below and [assets/sql/011_quantize_rescore.sql](../assets/sql/011_quantize_rescore.sql).

For the 100M+ memory-wall framing, the materialized-column SBQ/PQ path, and the DiskANN scale tier, see [graph-theory-at-scale.md](graph-theory-at-scale.md) — not repeated here.

## Worked recipe — pgvector binary_quantize + two-pass rescore

**Approach:** HNSW expression index directly on `binary_quantize(embedding)::bit(N)` — no extra materialized column, no `UPDATE` backfill. pgvector evaluates the expression at index-build time and at query time. This is the "Use expression indexing for binary quantization" pattern from pgvector's own documentation.

**Prerequisites:** pgvector ≥ 0.7.0 (`binary_quantize(vector) → bit` added in 0.7.0).

For the full reversible DDL, see [assets/sql/011_quantize_rescore.sql](../assets/sql/011_quantize_rescore.sql).

```sql
-- UP: expression index (N = your embedding dimension, e.g. 1536)
CREATE INDEX idx_embeddings_bq_hnsw
  ON embeddings
  USING hnsw ((binary_quantize(embedding)::bit(1536)) bit_hamming_ops)
  WITH (m = 16, ef_construction = 64);

-- Two-pass query (embed in app layer or CTE):
-- Pass 1 — Hamming prefilter via the expression index
WITH candidates AS (
  SELECT id, embedding
  FROM   embeddings
  ORDER  BY binary_quantize(embedding)::bit(1536) <~>
            binary_quantize(:query_embedding)::bit(1536)
  LIMIT  :k * :oversample        -- :oversample = eval-measured multiplier
)
-- Pass 2 — exact cosine rescore at full float32 precision
SELECT id
FROM   candidates
ORDER  BY embedding <=> :query_embedding
LIMIT  :k;
```

**Recall-loss budget:** `:oversample` is NOT a constant — measure it on your labeled eval set per corpus before fixing a value. A common starting range is 4–10×, but dimension and corpus distribution determine the right value.

## Per-backend coverage

| Backend | Verdict | Pointer / caveat |
|---|---|---|
| pgvector | native | `binary_quantize(embedding)::bit(N)` expression index + `<~>` Hamming; two-pass rescore with `<=>` cosine. See recipe above. |
| pgvectorscale | native (scale tier) | SBQ via `storage_layout = memory_optimized`; `diskann.query_rescore` controls rescore depth. SBQ is the scale tier — cross-link [graph-theory-at-scale.md](graph-theory-at-scale.md); not duplicated here. |
| ParadeDB | unverified | ParadeDB extends pgvector for BM25; no verbatim quantization doc found on primary URL at build time. |
| Qdrant | native | Scalar (4x), Binary (up to 32x), Product (up to 64x) quantization; oversampling + rescore natively supported. |
| Weaviate | native | PQ ("multi-step quantization technique...available for use with `hnsw` indexes"), BQ (32x storage reduction), SQ (8-bit, 4x). |
| Milvus/Zilliz | unverified | IVF_PQ and SQ8 quantization reported in community docs; primary milvus.io/docs URL returned redirect loops at build time — re-fetch to verbatim-confirm. |
| Vespa | native | "Vespa supports double, float, bfloat16, int8 and single-bit values"; int8 = 4x compression; single-bit = 32x binary. |
| LanceDB | unverified | IVF-PQ referenced in community docs; no verbatim quantization token found on primary docs URL (lancedb.github.io/lancedb or docs.lancedb.com) at build time. |
| Chroma | unverified | No verbatim quantization support text found on primary Chroma docs at build time. |
| AWS S3 Vectors | unverified | Managed index; quantization control not described verbatim in primary S3 Vectors docs at build time. |
| Turbopuffer | unverified | Object-storage-backed; quantization not described verbatim in primary docs at build time. |
| Pinecone Serverless | unverified | Quantization is internal/opaque; no user-facing quantization control described verbatim in primary docs at build time. |
| Cloudflare Vectorize | unverified | No verbatim quantization control found in primary Vectorize docs at build time. |
| Upstash Vector | unverified | No verbatim quantization control found in primary Upstash Vector docs at build time. |
| AWS Bedrock KB | unverified | Managed RAG service; quantization is internal to the backing store; not described verbatim in primary Bedrock KB docs at build time. |
| Azure AI Search | unverified | Azure AI Search supports vector compression (scalar quantization described in Azure docs); no verbatim token found on the primary scoring URL used in this skill's sources.json at build time — re-fetch `learn.microsoft.com/azure/search/vector-search-how-to-quantization` to verify. |
| Vertex AI Vector Search | unverified | Managed; quantization is internal; not described verbatim in primary Vertex docs at build time. |
| OpenAI File Search | unverified | Fully managed; quantization is internal/opaque; not described verbatim in primary File Search docs at build time. |
| Elasticsearch/OpenSearch | native | ES: `bbq_hnsw` (32x, 96% footprint reduction), `int8_hnsw` (4x), `int4_hnsw` (8x); rescore via stored float vectors (`bbq_disk` is the default when available under the current license). OpenSearch HNSW Faiss/Lucene engines — quantization not verbatim confirmed on primary knn-index URL at build time. |
| Redis Stack | unverified | No verbatim quantization support found in Redis vector search primary docs at build time. |
| MongoDB Atlas | native | Scalar quantization (3.75x RAM reduction), Binary quantization (24x RAM reduction); "We recommend quantization for applications with a large number of vectors, such as over 100,000." |

Legend: native (recipe/operator pointer) · emulate (how + "anti-pattern unless X") · not-supported (use leg/toolkit Y) · unverified (not primary-source-confirmed at build)

## Anti-patterns

**Pattern → Anti-pattern → Recipe**

**Pattern: Always rescore the quantized prefilter at full precision.**
- Anti-pattern: Running only the Hamming prefilter pass without a full-precision rescore step. Recall loss at 32× is 5–15% without rescore.
- Recipe: Add the Pass-2 exact `<=>` cosine rescore over the oversampled candidate set; recall typically recovers to <1%.

**Pattern: Quantize only vectors with enough dimensions to absorb the noise.**
- Anti-pattern: Binary-quantizing < ~512-dim vectors — quantization noise dominates recall loss for short vectors and the rescore step cannot fully recover it.
- Recipe: Use `halfvec` (2× compression) or `int8` (4×) for short vectors instead of 1-bit binary quantization.

**Pattern: Quantize only when the corpus is large enough to pay back the eval cost.**
- Anti-pattern: Quantizing a corpus < ~100k vectors — the RAM/latency gain is negligible and the recall-measurement overhead outweighs it. This is the premature-optimization anti-pattern from SKILL.md.
- Recipe: Stay on plain float32 HNSW until the corpus crosses the "When you need this" trigger; revisit then.

**Pattern: Measure the oversample multiplier on your own labeled eval set.**
- Anti-pattern: Treating the `:oversample` recall-loss budget as a fixed constant copied from a blog post's example value.
- Recipe: Sweep `:oversample` against recall@k on your labeled eval set per corpus and model; fix the value from that measurement.

**Pattern: Use an expression index at the default tier.**
- Anti-pattern: Adding a separate materialized bit column plus an `UPDATE` backfill (the scale-tier approach in graph-theory-at-scale.md) at the default tier — extra write overhead and schema complexity.
- Recipe: `USING hnsw ((binary_quantize(embedding)::bit(N)) bit_hamming_ops)`; reserve the materialized-column path for the 100M+ scale tier (graph-theory-at-scale.md).

**Pattern: Hold the eval set constant when comparing quantized vs unquantized.**
- Anti-pattern: Comparing recall@k between a quantized and an unquantized run in different eval cohorts — conflates eval variance with quantization effect.
- Recipe: Run both arms against the same labeled eval set; attribute the delta only when the cohort is identical.

## Known traps

- **`binary_quantize(embedding)::bit(N)` where N doesn't match the index** — if the query-time cast `::bit(N)` uses a different N than the index expression, the expression index is skipped and the query falls back to a full scan. The N in the query must match exactly.
- **ef_search too low after quantization** — the HNSW graph-walk `ef_search` should be at least `:k * :oversample` to ensure the prefilter leg surfaces enough candidates for rescore. If ef_search < candidate_count the first pass is the bottleneck.
- **Forgetting the session knob for iterative scan** — pgvector's `hnsw.iterative_scan = relaxed_order` is required for filtered hybrid queries that combine the HNSW walk with a WHERE clause. Without it the planner may not use the expression index under filter predicates.
- **Rescore with a different query vector type** — if the rescore uses `embedding::halfvec <=> :query_embedding::halfvec`, the `:query_embedding` cast must match. Mismatched types force a row-by-row cast and lose the half-precision memory benefit.
- **Re-indexing cost at migration** — switching from a plain HNSW index to a `binary_quantize` expression index requires a concurrent rebuild. Budget the rebuild time against the SLA; see [production-runbook.md](production-runbook.md) for migration drills.

## Verified against

| Claim | Source id |
|---|---|
| pgvector `binary_quantize(vector) → bit` | pgvector-readme |
| pgvector "Use expression indexing for binary quantization" | pgvector-readme |
| pgvector `CREATE INDEX … USING hnsw ((binary_quantize(embedding)::bit(3)) bit_hamming_ops)` | pgvector-readme |
| pgvector `<~>` Hamming distance operator | pgvector-readme |
| pgvector "Re-rank by the original vectors for better recall" | pgvector-readme |
| pgvector "Use the `bit` type to store binary vectors" | pgvector-readme |
| pgvectorscale SBQ via `storage_layout = memory_optimized` | pgvectorscale-readme |
| pgvectorscale `diskann.query_rescore` rescore parameter | pgvectorscale-readme |
| Qdrant scalar quantization "compresses each vector component from a 32-bit float to an 8-bit integer, achieving 4x compression" | qdrant-quantization |
| Qdrant binary quantization "reduces each vector component to one to two bits for up to 32x compression" | qdrant-quantization |
| Qdrant product quantization "enables up to 64x compression when minimizing memory is the top priority" | qdrant-quantization |
| Qdrant oversampling "pre-select using quantized index, and then re-scored using original vectors" | qdrant-quantization |
| Qdrant rescore "Qdrant can re-evaluate top-k search results using the original vectors" | qdrant-quantization |
| Weaviate PQ "Product quantization is a multi-step quantization technique that is available for use with `hnsw` indexes in Weaviate." | weaviate-quantization |
| Weaviate BQ "Binary quantization (BQ) is a quantization technique that converts each vector embedding to a binary representation." | weaviate-quantization |
| Weaviate BQ "Usually each vector dimension requires 32 bits, but the binary representation only requires 1 bit, representing a 32x reduction in storage requirements." | weaviate-quantization |
| Weaviate SQ "Scalar quantization (SQ)...transforms the float representation to an 8 bit integer. This is a 4x reduction in size." | weaviate-quantization |
| Elasticsearch BBQ `bbq_hnsw` "reduces each dimension to a single bit precision. This reduces the memory footprint by 96% (or 32x)" | elasticsearch-dense-vector |
| Elasticsearch int8 `int8_hnsw` "Quantizes each dimension of the vector to 1-byte integers. This reduces the memory footprint by 75% (or 4x)" | elasticsearch-dense-vector |
| Elasticsearch "the default index type is `bbq_disk` when available under the current license" | elasticsearch-dense-vector |
| Elasticsearch index type `bbq_hnsw` (Better Binary Quantization + HNSW) | elasticsearch-dense-vector |
| Elasticsearch index type `int8_hnsw` (scalar int8 + HNSW) | elasticsearch-dense-vector |
| Elasticsearch index type `int4_hnsw` (half-byte int4 + HNSW) | elasticsearch-dense-vector |
| Vespa "Vespa supports double, float, bfloat16, int8 and single-bit values" | vespa-ann-hnsw |
| Vespa "single-bit values greatly reduce both memory and cpu costs, and can be effectively combined with larger vector values stored on disk as a paged attribute" | vespa-ann-hnsw |
| MongoDB Atlas scalar quantization "reduces the vector embedding's RAM cost to about one fourth (`1/3.75`) of the pre-quantization cost." | mongodb-atlas-quantization |
| MongoDB Atlas binary quantization "reduces the vector embedding's RAM cost to one twenty-fourth (`1/24`) of the pre-quantization cost." | mongodb-atlas-quantization |
| MongoDB Atlas "We recommend quantization for applications with a large number of vectors, such as over 100,000." | mongodb-atlas-quantization |
