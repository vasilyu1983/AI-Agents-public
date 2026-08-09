# 2026 Query Optimization Research and Runtime

Verified facts (last validated 2026-07-11). Use sources.json entries for URLs.

## PostgreSQL 18 — Asynchronous I/O (AIO)

Released 2025-09-25. AIO is GA in PostgreSQL 18.

- New `io_method` GUC: `worker` (default), `io_uring` (Linux), `sync`
- New `pg_aios` system view for monitoring in-flight async I/O operations
- AIO covers: sequential scans, bitmap heap scans, vacuum
- Performance: up to ~3x throughput in I/O-bound scenarios per release benchmarks
- Skip scan: PostgreSQL 18 supports skip scan for multicolumn B-tree indexes where the leading column has no equality predicate; helps most when leading column has low cardinality — verify with `EXPLAIN (ANALYZE, BUFFERS)`
- `uuidv7()` built-in function generates time-ordered UUIDs; better index locality than UUIDv4 for append-heavy OLTP
- `pg_upgrade` now retains optimizer statistics, reducing post-upgrade plan churn

Verify exact `io_method` defaults and per-OS availability against current docs before recommending.

## MySQL 9.7 LTS (GA 2026-04-21)

MySQL 9.7.0 is the current LTS; first LTS since 8.4. MySQL 8.4 LTS remains supported.

- HyperGraph optimizer available in 9.7 Community Edition (not default; opt-in per session or globally)
  - DPhyp algorithm; strongest gains on JOIN-heavy analytics; enable with `optimizer_switch='hypergraph_optimizer=on'`
  - Do not enable globally in production without benchmarking the specific workload first
- JSON Duality Views: DML (INSERT/UPDATE/DELETE) now supported in Community Edition
- JavaScript stored programs: available in 9.x
- Enhanced replication security: encryption enabled by default for replication connections in 9.x
- MySQL 8.4 remains the safe default for teams that have not yet validated 9.7 workload behavior

## SQL Server 2025 — GA 2025-11-18

Released at Microsoft Ignite 2025. Key query-optimizer additions (IQP 3.0):

- **CE Feedback for expressions**: engine learns from prior executions to select better cardinality estimation models; improves row estimates without manual hints
- **DOP Feedback**: monitors actual vs ideal degree of parallelism and adjusts subsequent executions automatically
- **OPPO (Optional Parameter Plan Optimization)**: generates multiple plans per statement and selects at runtime based on parameter values; reduces parameter-sniffing issues
- **Adaptive query processing**: expanded; join strategies, memory grants, and execution paths adjust at runtime based on observed statistics

For all SQL Server 2025 optimizer specifics, fetch live from:
https://learn.microsoft.com/en-us/sql/sql-server/what-s-new-in-sql-server-2025

## pgvector (PostgreSQL Vector Search)

Current version: 0.8.x — 0.8.5 released 2026-07-08 (patch-only line; 0.8.2, released 2026-02-25, fixed a buffer overflow in parallel HNSW index builds — CVE-2026-3172). Ships by default on AWS RDS, Google Cloud SQL, Supabase, and Neon; confirm the managed-service's bundled version supports the index type before recommending it, since managed offerings lag upstream by weeks to months.

- Index types: HNSW (default ANN choice), IVFFlat, DiskANN (two implementations)
- pgvector 0.8+ improves filtered ANN: planner now estimates when a B-tree or other index better serves a filtered vector query than HNSW/IVFFlat
- HNSW tuning knobs: `m` (16 default, increase for recall), `ef_construction` (64 default), `ef` (search effort)
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
- Result: TPC-DS on PostgreSQL, geomean runtime speedup **13.2x** vs SOTA 4.9x

Use for framing LLM-assisted query-rewriting discussions. Verify reproducibility before citing in production recommendations.
