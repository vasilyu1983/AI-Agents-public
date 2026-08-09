# Embedded / Local Brain — DuckDB-VSS & sqlite-vec

When the corpus lives on a single machine — a developer's laptop, a notebook,
a CI step, or a single-binary service that ships its own data — a server is
the wrong tier. DuckDB with the `vss` extension gives HNSW vector search
inside an in-process analytics engine; sqlite-vec gives KNN vector search
via a `vec0` virtual table inside any SQLite connection. Both run without a
network listener, scale to millions of vectors on laptop-class hardware, and
use the same schema/stable-anchor/eval contract as the pgvector default —
only the engine changes. This toolkit is **not** a guide to deploying a
vector service for multi-writer or production workloads — for those, use the
pgvector default ([postgres-pgvector-default.md](postgres-pgvector-default.md))
or consult [backend-selection.md](backend-selection.md). It is also **not**
the guide for on-device iOS retrieval — that surfaces to
[`../../software-ios-ai-engine/SKILL.md`](../../software-ios-ai-engine/SKILL.md).
The scope is: when the whole brain fits on one machine and no server is
warranted, what are the paste-ready engine recipes?

> Verified against primary sources fetched 2026-05-19 (see Verified-against
> table). Backend feature claims are volatile — re-verify before production
> adoption. Scope: single-machine / embedded / CI / notebook usage only;
> multi-writer and managed-service tiers are out of scope and routed to
> [backend-selection.md](backend-selection.md).

## Table of Contents

- [When you need this](#when-you-need-this)
- [Decision](#decision)
- [Worked recipe — DuckDB vss and sqlite-vec](#worked-recipe--duckdb-vss-and-sqlite-vec)
- [Per-backend coverage](#per-backend-coverage)
- [Anti-patterns](#anti-patterns)
- [Known traps](#known-traps)
- [Verified against](#verified-against)

## When you need this

**Trigger signals (adopt an embedded engine when you see these):**

- The corpus never leaves a single machine: a developer laptop, a
  data-science notebook, a CI evaluation step, or a bundled offline tool.
- A server process would be the biggest operational complexity in the
  deployment — dependency on Postgres, a vector service, or a managed cloud
  API is not acceptable (no persistent infra, no network, no credentials).
- The corpus is small-to-medium (up to a few million vectors) and
  write traffic is single-writer (one notebook, one process, one CI job).
- Fast local iteration is the priority: embed → query → eval in a single
  Python process or shell session, with no migration overhead.

**When you do NOT need this (YAGNI gate):**

- Multi-writer or concurrent-write production workload — use
  [postgres-pgvector-default.md](postgres-pgvector-default.md) instead;
  DuckDB and sqlite-vec are single-writer embedded engines.
- Governance / ACL-bound corpus — row-level security and access policies
  require a server-managed engine; see `postgres-pgvector-default.md` for
  RLS patterns and `assets/sql/006_rls_multitenant.sql`.
- Scale past single-machine memory+disk — when the corpus requires distributed
  storage or multi-shard HNSW, use a dedicated service from
  [backend-selection.md](backend-selection.md).
- The team already runs Postgres — pgvector is the right default; adding a
  second engine for local work is rarely worth the cognitive split.
- On-device iOS brain — route to
  [`../../software-ios-ai-engine/SKILL.md`](../../software-ios-ai-engine/SKILL.md);
  sqlite-vec on iOS is that skill's concern, not this toolkit's.

## Decision

This toolkit covers the **embedded-engine tier** of the deployment spectrum:

```
Corpus → [embed in-process] → [DuckDB vss HNSW  ] → KNN results
                             [sqlite-vec vec0 KNN]
```

This is a **deployment-tier** choice, not a retrieval-leg choice — it does not interact with [lexical-vs-vector-vs-hybrid.md](lexical-vs-vector-vs-hybrid.md).

The schema contract, stable-anchor design, and eval contract are
**identical** to the pgvector default — only the engine changes. Column
names (`content`, `contextual_summary`, `section_path`, `doc_type`,
`symbol_name`, `model_id`, `content_hash`, `source_uri`, `as_of`), chunk
sizes, embedding models, and `scripts/build_eval_seed.py` eval patterns are
all portable across engines. This means a corpus developed locally with
DuckDB or sqlite-vec can be promoted to a Postgres + pgvector server by
re-ingesting the same chunks into the pgvector schema — no data-model
redesign required.

Cross-links:

- [postgres-pgvector-default.md](postgres-pgvector-default.md) — the V1
  server default; same schema, server tier
- [backend-selection.md](backend-selection.md) — full matrix and decision
  flow for all 21 backends

## Worked recipe — DuckDB vss and sqlite-vec

### DuckDB vss (HNSW)

**Prerequisite:** DuckDB ≥ 0.10 (vss extension available from the official
extension repository; no separate install step beyond the INSTALL command).

```python
import duckdb

con = duckdb.connect("brain.duckdb")  # or ":memory:" for ephemeral

# Install and load the vss extension (once per environment)
con.execute("INSTALL vss;")
con.execute("LOAD vss;")

# Enable experimental persistence for disk-backed HNSW indexes
# WARNING: WAL recovery not fully implemented — avoid unexpected shutdowns
con.execute("SET hnsw_enable_experimental_persistence = true;")

# Schema — same column contract as the pgvector default
con.execute("""
CREATE TABLE IF NOT EXISTS chunks (
    id           VARCHAR PRIMARY KEY,
    content      TEXT    NOT NULL,
    contextual_summary TEXT,
    section_path TEXT,
    doc_type     TEXT,
    symbol_name  TEXT,
    source_uri   TEXT,
    content_hash TEXT,
    model_id     TEXT    NOT NULL,
    as_of        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    embedding    FLOAT[1536]   -- adjust dimension to match model
);
""")

# HNSW index — only FLOAT (32-bit) vectors supported
con.execute("""
CREATE INDEX IF NOT EXISTS idx_chunks_hnsw
    ON chunks USING HNSW (embedding);
""")
```

**KNN query using `array_distance`:**

```python
import json

query_vec = embed(user_query)  # list[float], same model as index time

results = con.execute("""
    SELECT id, content, source_uri,
           array_distance(embedding, $1::FLOAT[1536]) AS dist
    FROM   chunks
    WHERE  model_id = $2
    ORDER BY dist
    LIMIT  10;
""", [query_vec, MODEL_ID]).fetchall()
```

**Down (remove index):**

```sql
DROP INDEX IF EXISTS idx_chunks_hnsw;
-- Table and data remain; queries fall back to sequential scan.
```

---

### sqlite-vec vec0 (KNN)

**Prerequisite:** `sqlite-vec` loadable extension (`.so`/`.dylib`/`.dll`)
available for the platform. Install via the project release page at
https://github.com/asg017/sqlite-vec.

```python
import sqlite3
import sqlite_vec  # pip install sqlite-vec (Python wrapper)

con = sqlite3.connect("brain.db")  # single-file, no server
con.enable_load_extension(True)
sqlite_vec.load(con)               # loads the vec0 extension

# Schema — same column contract; vec0 table holds the vectors
con.executescript("""
CREATE TABLE IF NOT EXISTS chunks (
    id                  TEXT PRIMARY KEY,
    content             TEXT NOT NULL,
    contextual_summary  TEXT,
    section_path        TEXT,
    doc_type            TEXT,
    symbol_name         TEXT,
    source_uri          TEXT,
    content_hash        TEXT,
    model_id            TEXT NOT NULL,
    as_of               TEXT DEFAULT (datetime('now'))
);

-- vec0 virtual table: stores embeddings and enables KNN
CREATE VIRTUAL TABLE IF NOT EXISTS chunk_embeddings USING vec0(
    chunk_id TEXT PRIMARY KEY,
    embedding FLOAT[1536]
);
""")
```

**Insert (must write to both tables).** sqlite-vec accepts a vector as a
JSON-text array (`"[0.1, 0.2, ...]"`) or a compact binary blob; this recipe
uses the JSON-text form via `json.dumps`:

```python
con.execute(
    "INSERT INTO chunks (id, content, model_id, ...) VALUES (?, ?, ?, ...)",
    (chunk_id, content, MODEL_ID, ...)
)
con.execute(
    "INSERT INTO chunk_embeddings (chunk_id, embedding) VALUES (?, ?)",
    (chunk_id, json.dumps(embedding))   # `embedding` = this chunk's vector
)
```

**KNN query:**

```python
results = con.execute("""
    SELECT c.id, c.content, c.source_uri, e.distance
    FROM   chunk_embeddings e
    JOIN   chunks c ON c.id = e.chunk_id
    WHERE  e.embedding MATCH ?
      AND  c.model_id = ?
    ORDER BY e.distance
    LIMIT 10;
""", [json.dumps(query_vec), MODEL_ID]).fetchall()
```

**Down (drop vec0 table):**

```sql
DROP TABLE IF EXISTS chunk_embeddings;
-- chunks table and all metadata remain intact.
```

## Per-backend coverage

| Backend | Verdict | Pointer / caveat |
|---|---|---|
| pgvector | wrong-tier | Server-managed Postgres extension — use [postgres-pgvector-default.md](postgres-pgvector-default.md) |
| pgvectorscale | wrong-tier | Server-managed Postgres extension — use [backend-selection.md](backend-selection.md) |
| ParadeDB | wrong-tier | Server-managed Postgres extension + BM25; use [backend-selection.md](backend-selection.md) |
| Qdrant | wrong-tier | Dedicated vector service (server process required); use [backend-selection.md](backend-selection.md) |
| Weaviate | wrong-tier | Server-managed vector DB; use [backend-selection.md](backend-selection.md) |
| Milvus/Zilliz | wrong-tier | Distributed vector service; use [backend-selection.md](backend-selection.md) |
| Vespa | wrong-tier | Server-managed search+ML engine; use [backend-selection.md](backend-selection.md) |
| LanceDB | native | OSS embedded library; runs locally in-process — same tier as the recipe; use its own `lancedb.connect()` API (no server) |
| Chroma | native | Supports local/self-hosted mode; runs without a managed service; embedded-friendly |
| AWS S3 Vectors | wrong-tier | Managed AWS service; use [backend-selection.md](backend-selection.md) |
| Turbopuffer | wrong-tier | Serverless managed service; use [backend-selection.md](backend-selection.md) |
| Pinecone Serverless | wrong-tier | Managed cloud service; use [backend-selection.md](backend-selection.md) |
| Cloudflare Vectorize | wrong-tier | Managed edge service; use [backend-selection.md](backend-selection.md) |
| Upstash Vector | wrong-tier | Managed edge service; use [backend-selection.md](backend-selection.md) |
| AWS Bedrock KB | wrong-tier | Managed AWS RAG service; use [backend-selection.md](backend-selection.md) |
| Azure AI Search | wrong-tier | Managed Azure service; use [backend-selection.md](backend-selection.md) |
| Vertex AI Vector Search | wrong-tier | Managed GCP service; use [backend-selection.md](backend-selection.md) |
| OpenAI File Search | wrong-tier | Managed OpenAI service; use [backend-selection.md](backend-selection.md) |
| Elasticsearch/OpenSearch | wrong-tier | Server-managed search engine; use [backend-selection.md](backend-selection.md) |
| Redis Stack | wrong-tier | Server-managed Redis module; use [backend-selection.md](backend-selection.md) |
| MongoDB Atlas | wrong-tier | Managed cloud DB service; use [backend-selection.md](backend-selection.md) |

Legend: native (recipe/operator pointer) · emulate (how + "anti-pattern unless X") · wrong-tier (use correct tier) · unverified (not primary-source-confirmed at build)

This matrix is a binary deployment-tier filter — a backend is either embedded-capable (native) or the wrong tier for a no-server brain (wrong-tier). The shared-template verdicts emulate and unverified do not arise here: there is no "emulate embedded" middle state, and every verdict is primary-source-confirmed at build.

**iOS routing note:** sqlite-vec runs anywhere SQLite runs, which includes iOS.
However, on-device iOS retrieval (sqlite-vec / `NLEmbedding` / Core Spotlight)
is the concern of
[`../../software-ios-ai-engine/SKILL.md`](../../software-ios-ai-engine/SKILL.md),
not this toolkit. Do not absorb iOS patterns here.

## Anti-patterns

**Pattern → Anti-pattern → Recipe**

**Pattern: use an embedded engine for single-machine, single-writer workloads.**

- Anti-pattern: choosing DuckDB or sqlite-vec for a multi-writer or
  multi-process production workload — concurrent writes are not supported
  (DuckDB: one writer at a time; sqlite-vec inherits SQLite WAL single-writer
  semantics). Under concurrent write pressure both engines produce locking
  errors or silently drop writes.
- Recipe: if concurrent writes are needed, use Postgres + pgvector
  ([postgres-pgvector-default.md](postgres-pgvector-default.md)); use DuckDB
  or sqlite-vec only when a single process owns all writes.

**Pattern: keep the same schema/model_id contract as the pgvector default.**

- Anti-pattern: inventing a local-only schema that omits `model_id`,
  `content_hash`, or `source_uri`. When the corpus later graduates to pgvector,
  the schema mismatch forces a full re-ingest from scratch.
- Recipe: match the pgvector schema exactly (same column names, same `model_id`
  pinning convention, same stable-anchor design). Only the DDL dialect
  and index type change — everything else is portable.

**Pattern: enable DuckDB HNSW persistence explicitly.**

- Anti-pattern: creating an HNSW index on a disk-backed DuckDB file without
  setting `hnsw_enable_experimental_persistence = true`. The index silently
  falls back to in-memory only; the table persists but the index is gone on
  reconnect, causing unindexed sequential scans that appear correct but are
  slow.
- Recipe: always set `SET hnsw_enable_experimental_persistence = true;` before
  `CREATE INDEX … USING HNSW` on a disk-backed database. Accept the WAL
  recovery caveat (no unexpected shutdowns with uncommitted changes).

**Pattern: use separate tables for metadata and vectors in sqlite-vec.**

- Anti-pattern: storing all fields including the vector in a single regular
  SQLite table and trying to do KNN via a manual loop in Python. The `vec0`
  virtual table is what enables efficient KNN; using regular `BLOB` storage
  for vectors eliminates the index and degrades to O(n) scan.
- Recipe: always create a `vec0` virtual table alongside the metadata table,
  joined by a stable `chunk_id`. See the worked recipe above.

## Known traps

- **DuckDB HNSW persistence is experimental** — the `hnsw_enable_experimental_persistence`
  flag is required for disk-backed HNSW indexes, and the docs warn that WAL
  recovery is not properly implemented. An unexpected shutdown with uncommitted
  changes can corrupt the index. For CI/notebook use this is acceptable; for
  any data-critical local use, keep a re-ingest script so the index can be
  rebuilt from the raw chunk table.
- **DuckDB HNSW supports only FLOAT (32-bit) vectors** — `FLOAT[n]` columns
  only; `DOUBLE` or integer vector types are not supported for HNSW indexing.
  Verify the embedding model output type before creating the index; most
  providers return `float32` which maps correctly.
- **sqlite-vec requires a two-table design** — metadata lives in a regular
  SQLite table; the vector lives in the `vec0` virtual table. Both must be
  kept in sync manually (no foreign-key enforcement across virtual tables in
  SQLite). Add an application-layer assertion or a test fixture that counts
  both tables and alerts on divergence.
- **array_distance vs cosine** — DuckDB `array_distance` computes Euclidean
  (L2) distance. For cosine similarity use `array_cosine_distance`; for inner
  product use `array_negative_inner_product`. Match the distance function to
  the embedding model's recommended metric (most OpenAI and Voyage models are
  cosine; many matryoshka models also support cosine). Wrong metric produces
  silently degraded retrieval quality with no error.
- **Promotion path to pgvector requires re-embedding if dimensions differ** —
  if the local brain used a smaller/different model than the production pgvector
  index, vectors are incompatible and the entire corpus must be re-embedded.
  Pin `model_id` in the schema from day one to make the mismatch detectable.
- **Chroma local mode is not the same as Chroma Cloud** — Chroma's self-hosted
  local mode does not support all Chroma Cloud features (e.g. multi-tenant
  governance, managed backups). For single-machine use, self-hosted local mode
  is appropriate; do not assume feature parity with the managed offering.
- **`sqlite3.executescript()` issues an implicit COMMIT** — running the
  schema-setup script inside an open transaction silently commits whatever was
  pending before it. Run the `vec0` DDL only at setup time, outside any
  in-flight transaction, or the surrounding unit of work is committed early
  with no error.

## Verified against

| Claim | Source id |
|---|---|
| DuckDB vss: `vss` extension name; `INSTALL vss; LOAD vss;` syntax | `duckdb-vss` |
| DuckDB vss: HNSW index type; `CREATE INDEX … USING HNSW` | `duckdb-vss` |
| DuckDB vss: `array_distance`, `array_cosine_distance`, `array_negative_inner_product` distance functions | `duckdb-vss` |
| DuckDB vss: `hnsw_enable_experimental_persistence` required for disk-backed HNSW | `duckdb-vss` |
| DuckDB vss: only FLOAT (32-bit) vectors supported for HNSW | `duckdb-vss` |
| sqlite-vec: `vec0` virtual table; `CREATE VIRTUAL TABLE … USING vec0(…)` | `sqlite-vec` |
| sqlite-vec: KNN via `WHERE embedding MATCH … ORDER BY distance` | `sqlite-vec` |
| sqlite-vec: "Written in pure C, no dependencies, runs anywhere SQLite runs" | `sqlite-vec` |
| LanceDB: "open-source embedded library" — runs locally without a server | `lancedb-embedded` |
| Chroma: "Run it locally, self-host, or use Chroma Cloud" | `chroma-local` |
| Server/managed backends (pgvector, pgvectorscale, ParadeDB, Qdrant, Weaviate, Milvus/Zilliz, Vespa, S3 Vectors, Turbopuffer, Pinecone, Vectorize, Upstash, Bedrock KB, Azure AI Search, Vertex AI, OpenAI File Search, ES/OpenSearch, Redis Stack, MongoDB Atlas): server-process or managed-service tier — confirmed via their respective primary sources listed in data/sources.json; "wrong-tier" is an architecture ruling, not a per-feature claim | `backend-selection.md` (internal routing) + respective primary sources per backend |
