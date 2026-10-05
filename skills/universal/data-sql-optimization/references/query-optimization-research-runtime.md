# Query Optimization Research and Runtime

Version-specific facts about optimizer and runtime features. Check the vendor's current docs and release notes (URLs in `data/sources.json`) before quoting a version, default, or support status.

## PostgreSQL 18 — Asynchronous I/O (AIO)

AIO ships in PostgreSQL 18.

- New `io_method` GUC: `worker` (default), `io_uring` (Linux), `sync`
- New `pg_aios` system view for monitoring in-flight async I/O operations
- AIO covers: sequential scans, bitmap heap scans, vacuum
- Performance: gains show up on I/O-bound scans; measure on your own workload and storage before attributing a speedup to AIO
- Skip scan: PostgreSQL 18 supports skip scan for multicolumn B-tree indexes where the leading column has no equality predicate; helps most when leading column has low cardinality — verify with `EXPLAIN (ANALYZE, BUFFERS)`
- `uuidv7()` built-in function generates time-ordered UUIDs; better index locality than UUIDv4 for append-heavy OLTP
- `pg_upgrade` retains optimizer statistics from 18 on, reducing post-upgrade plan churn

Verify exact `io_method` defaults and per-OS availability against current docs before recommending.

## MySQL

Release line: run production on an LTS line, not an Innovation release. Which LTS lines are supported, and their end-of-life dates, change: read the MySQL support-policy page before recommending a line, and plan upgrades before the line in use reaches EOL. Current minor releases: `data/versions.json` → `mysql`.

- HyperGraph optimizer (DPhyp join enumeration): strongest gains on JOIN-heavy analytic queries; enable per session with `optimizer_switch='hypergraph_optimizer=on'`. Check the release notes for which versions and editions ship it and whether it is on by default
  - Do not enable globally in production without benchmarking the specific workload first
- JSON Duality Views and JavaScript stored programs: edition and version support differ; check the release notes for the user's edition before designing around them
- Replication-connection encryption defaults differ by version; check them before assuming replication traffic is encrypted
- Stay on the validated LTS line until the next line has passed a workload replay

## SQL Server IQP

DOP feedback, CE feedback, CE feedback for expressions and OPPO have different release and compatibility requirements. Read the [Microsoft IQP feature matrix](https://learn.microsoft.com/en-us/sql/relational-databases/performance/intelligent-query-processing?view=sql-server-ver17) for the user's engine, then check that feature's Query Store and database-scoped configuration prerequisites.

- DOP feedback adjusts parallelism for repeated queries.
- CE feedback addresses estimation assumptions; expression feedback extends the scope to repeating expressions.
- OPPO selects plan variants for optional-parameter predicates; test representative NULL and non-NULL inputs.
- Adaptive joins and memory-grant feedback are distinct features; verify each rather than grouping them under a single release label.

## pgvector (PostgreSQL Vector Search)

Read the current release from the upstream CHANGELOG before quoting a version number. Security floor: 0.8.2 fixed a buffer overflow in parallel HNSW index builds (CVE-2026-3172), so treat anything older as needing an upgrade. Managed PostgreSQL services bundle their own pgvector build and lag upstream; confirm the service's bundled version supports the index type and feature before recommending it.

- Index types in pgvector: HNSW (default ANN choice) and IVFFlat. pgvector itself has no DiskANN index; DiskANN-style indexes come from separate extensions — Timescale's `pgvectorscale` (StreamingDiskANN) and Microsoft's `pg_diskann` (Azure Database for PostgreSQL)
- Iterative index scans (pgvector 0.8.0+, `hnsw.iterative_scan` / `ivfflat.iterative_scan`): keep scanning the ANN index until enough rows pass a `WHERE` filter — the first fix to try when filtered vector queries return too few results
- pgvector 0.8+ improves filtered ANN: the planner estimates when a B-tree or other index better serves a filtered vector query than HNSW/IVFFlat
- HNSW tuning knobs: `m` (16 default, increase for recall), `ef_construction` (64 default), `hnsw.ef_search` (query-time search effort)
- Hybrid search (vector + scalar filter): use partial indexes or `lists`/`probes` tuning to reduce scan scope

```sql
-- HNSW index creation
CREATE INDEX ON items USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);

-- Set search effort at query time
SET hnsw.ef_search = 100;

-- Filtered ANN query (pgvector 0.8+ may use B-tree for the scalar filter first)
SELECT id, content
FROM items
WHERE tenant_id = $1
ORDER BY embedding <=> $2
LIMIT 10;
```

Verify `pgvector` version and managed-service availability before advising on specific index types.

## LITHE — LLM-Based SQL Query Rewrite

- arXiv: 2502.12918 (submitted 2025-02-18 — this is a **2025 arXiv**, not 2026)
- Published: EDBT 2026, "LITHE: A Query Rewrite Advisor using LLMs"
- URL: https://openproceedings.org/2026/conf/edbt/paper-93.pdf
- Result: The [EDBT 2026 paper](https://openproceedings.org/2026/conf/edbt/paper-93.pdf), abstract and §1, reports TPC-DS/PostgreSQL slow-query geometric-mean runtime speedups over the native optimizer of **13.2x** for LITHE and **4.9x** for SOTA; these are benchmark results, not production guarantees.

Use for framing LLM-assisted query-rewriting discussions. Verify reproducibility before citing in production recommendations.
