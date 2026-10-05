-- pg_slow_query_triage.sql
-- PostgreSQL 14+ slow-query triage report using pg_stat_statements.
--
-- REQUIRED SETUP
-- --------------
-- 1. Add to postgresql.conf, then RESTART the server (shared_preload_libraries
--    is only read at server start; a reload is not enough):
--      shared_preload_libraries = 'pg_stat_statements'
--      pg_stat_statements.track = all                     -- 'all' captures nested statements too; use 'top' to reduce noise
--      pg_stat_statements.max = 10000                     -- max number of distinct query fingerprints kept
-- 2. Create the extension in each database you query it from (after the restart):
--      CREATE EXTENSION IF NOT EXISTS pg_stat_statements;
-- 3. Verify the view is populated:
--      SELECT count(*) FROM pg_stat_statements;
-- 4. Optional: reset to start a fresh measurement window. This DISCARDS all
--    accumulated statistics — export them first if you need the history:
--      SELECT pg_stat_statements_reset();
--
-- HOW TO READ THE RESULTS
-- -----------------------
-- Each section targets a different bottleneck type. Work through them in order:
--   Section 1 → CPU / wall-clock hogs (total cost to the system)
--   Section 2 → Individual-call latency (expensive even when called rarely)
--   Section 3 → I/O pressure (disk or buffer cache misses)
--   Section 4 → High variance (flapping queries; candidates for plan instability)
--   Section 5 → Low cache-hit ratio (cold queries bypassing shared_buffers)
--   Section 6 → Temp-file spill, planning time, and WAL volume per query
--
-- NEXT DIAGNOSTIC STEP FOR EACH SECTION
-- See inline comments per section.
--
-- LIMITATIONS
-- -----------
-- - pg_stat_statements normalises literals; query text shows $1, $2 placeholders.
--   To find real parameter values, cross-reference with your application logs or
--   pg_stat_activity (capture during a live spike with pg_sleep loops).
-- - Stats accumulate since last reset or server restart. Long-running servers may
--   show historical data that masks recent regressions. Consider resetting after
--   major deployments and re-sampling after ~15 minutes of load.
-- - This script is read-only and safe to run in production at any time.
-- - JIT timing (jit_*) columns are not parsed here; inspect the installed
--   pg_stat_statements extension schema before querying them.

-- ---------------------------------------------------------------------------
-- SECTION 1: Top 20 by TOTAL execution time
-- ---------------------------------------------------------------------------
-- Why: These queries burn the most aggregate CPU/wall-clock. Even a fast query
-- called millions of times will dominate here. Fix these first for overall
-- throughput improvement.
--
-- Next step: Run EXPLAIN (ANALYZE, BUFFERS) on the top 1-3 queries.
--            Look for sequential scans on large tables, hash joins spilling to
--            disk (Batches > 1), and misestimated rows (rows= vs actual rows=).
-- ---------------------------------------------------------------------------

WITH top_total AS (
    SELECT
        queryid,
        query,
        calls,
        round(total_exec_time::numeric, 2)        AS total_exec_time_ms,
        round(mean_exec_time::numeric, 2)          AS mean_exec_time_ms,
        round(stddev_exec_time::numeric, 2)        AS stddev_exec_time_ms,
        round((total_exec_time / NULLIF(sum(total_exec_time) OVER (), 0) * 100)::numeric, 2)
                                                   AS pct_of_total,
        shared_blks_hit,
        shared_blks_read,
        shared_blks_dirtied,
        shared_blks_written,
        rows
    FROM pg_stat_statements
    WHERE query NOT ILIKE '%pg_stat_statements%'   -- exclude self-referential queries
      AND calls > 0
    ORDER BY total_exec_time DESC
    LIMIT 20
)
SELECT
    queryid,
    calls,
    total_exec_time_ms,
    mean_exec_time_ms,
    stddev_exec_time_ms,
    pct_of_total          AS "% of total time",
    shared_blks_hit       AS blks_hit,
    shared_blks_read      AS blks_read,
    rows,
    left(query, 200)      AS query_preview
FROM top_total
ORDER BY total_exec_time_ms DESC;


-- ---------------------------------------------------------------------------
-- SECTION 2: Top 20 by MEAN execution time (min 100 calls)
-- ---------------------------------------------------------------------------
-- Why: Section 1 ranks by total time, which favours cheap-but-frequent queries.
-- Ranking by mean surfaces queries that are slow per call. The calls > 100
-- filter drops rare one-offs (e.g. a single ad-hoc report) so the list shows
-- queries that are *consistently* slow, which are the ones users feel.
--
-- Next step: Compare mean vs stddev. High stddev → plan instability or
--            lock contention. Low stddev → deterministically slow; look at
--            the plan for missing index or bad join order.
-- ---------------------------------------------------------------------------

WITH top_mean AS (
    SELECT
        queryid,
        query,
        calls,
        round(mean_exec_time::numeric, 2)          AS mean_exec_time_ms,
        round(stddev_exec_time::numeric, 2)        AS stddev_exec_time_ms,
        round(min_exec_time::numeric, 2)           AS min_exec_time_ms,
        round(max_exec_time::numeric, 2)           AS max_exec_time_ms,
        round(total_exec_time::numeric, 2)         AS total_exec_time_ms,
        rows
    FROM pg_stat_statements
    WHERE query NOT ILIKE '%pg_stat_statements%'
      AND calls > 100
    ORDER BY mean_exec_time DESC
    LIMIT 20
)
SELECT
    queryid,
    calls,
    mean_exec_time_ms,
    stddev_exec_time_ms,
    min_exec_time_ms,
    max_exec_time_ms,
    total_exec_time_ms,
    rows,
    left(query, 200) AS query_preview
FROM top_mean
ORDER BY mean_exec_time_ms DESC;


-- ---------------------------------------------------------------------------
-- SECTION 3: Top 10 by I/O pressure (shared_blks_read)
-- ---------------------------------------------------------------------------
-- Why: shared_blks_read counts 8 KB pages read from disk (or OS page cache)
-- that were NOT already in PostgreSQL's shared_buffers. High values indicate
-- that the query is bypassing the buffer cache — either because the working
-- set is too large for shared_buffers, or the data is cold and rarely reused.
--
-- Next step: Check if effective_cache_size and shared_buffers are sized
--            appropriately (starting points, not rules: shared_buffers
--            ≈ 25% of RAM, effective_cache_size ≈ 50-75% of RAM). Then look at whether an index can turn a
--            sequential scan into an index scan with smaller I/O footprint.
--            Also inspect pg_statio_user_tables for the target relation.
-- ---------------------------------------------------------------------------

WITH top_io AS (
    SELECT
        queryid,
        query,
        calls,
        shared_blks_read,
        shared_blks_hit,
        round(
            shared_blks_hit::numeric /
            NULLIF(shared_blks_hit + shared_blks_read, 0) * 100,
            2
        )                                          AS cache_hit_ratio_pct,
        round(total_exec_time::numeric, 2)         AS total_exec_time_ms,
        round(mean_exec_time::numeric, 2)          AS mean_exec_time_ms
    FROM pg_stat_statements
    WHERE query NOT ILIKE '%pg_stat_statements%'
      AND calls > 0
      AND shared_blks_read > 0
    ORDER BY shared_blks_read DESC
    LIMIT 10
)
SELECT
    queryid,
    calls,
    shared_blks_read      AS blks_read_from_disk,
    shared_blks_hit       AS blks_from_cache,
    cache_hit_ratio_pct   AS "cache_hit_%",
    total_exec_time_ms,
    mean_exec_time_ms,
    left(query, 200)      AS query_preview
FROM top_io
ORDER BY blks_read_from_disk DESC;


-- ---------------------------------------------------------------------------
-- SECTION 4: High variance queries (stddev / mean > 2.0, min 50 calls)
-- ---------------------------------------------------------------------------
-- Why: A query whose execution time varies wildly (high stddev relative to
-- mean) is a plan-instability or contention signal. Common causes:
--   - Multiple plans being selected depending on bind-parameter values (PSPS)
--   - Lock waits inflating some executions
--   - Buffer cache misses on infrequently-accessed partitions
--   - autovacuum or checkpoint I/O spikes interfering
--
-- Next step: Capture pg_stat_activity during a slow execution and look for
--            wait events (Lock, BufferPin, DataFileRead). Use auto_explain
--            (log_min_duration = 0 on a replica) to capture actual plans for
--            slow vs fast executions side-by-side.
-- ---------------------------------------------------------------------------

WITH variance_candidates AS (
    SELECT
        queryid,
        query,
        calls,
        round(mean_exec_time::numeric, 2)          AS mean_exec_time_ms,
        round(stddev_exec_time::numeric, 2)        AS stddev_exec_time_ms,
        round(min_exec_time::numeric, 2)           AS min_exec_time_ms,
        round(max_exec_time::numeric, 2)           AS max_exec_time_ms,
        round(
            (stddev_exec_time / NULLIF(mean_exec_time, 0))::numeric,
            3
        )                                          AS cv  -- coefficient of variation
    FROM pg_stat_statements
    WHERE query NOT ILIKE '%pg_stat_statements%'
      AND calls > 50
      AND mean_exec_time > 1          -- ignore sub-millisecond noise
      AND stddev_exec_time / NULLIF(mean_exec_time, 0) > 2.0
    ORDER BY cv DESC
    LIMIT 20
)
SELECT
    queryid,
    calls,
    mean_exec_time_ms,
    stddev_exec_time_ms,
    min_exec_time_ms,
    max_exec_time_ms,
    cv                    AS "stddev/mean (CV)",
    left(query, 200)      AS query_preview
FROM variance_candidates
ORDER BY cv DESC;


-- ---------------------------------------------------------------------------
-- SECTION 5: Low cache-hit ratio (< 80%, min 200 calls, min 1000 blks total)
-- ---------------------------------------------------------------------------
-- Why: A cache hit ratio below ~90% sustained for an active query usually
-- signals that either:
--   (a) shared_buffers is too small for the active working set, or
--   (b) the query scans data that is rarely reused (e.g. full-table analytics
--       on a large table — better served by a replica or OLAP engine).
--
-- Note: A brand-new table after a reset will show 0% until warmed. Combine
-- this with pg_statio_user_tables and pg_buffercache for deeper analysis.
--
-- Next step: For (a): increase shared_buffers (requires restart) and/or
--            enable huge pages. For (b): route the query to a read replica,
--            a materialised view, or an OLAP engine (e.g. ClickHouse, DuckDB).
-- ---------------------------------------------------------------------------

WITH cache_ratio AS (
    SELECT
        queryid,
        query,
        calls,
        shared_blks_hit,
        shared_blks_read,
        round(
            shared_blks_hit::numeric /
            NULLIF(shared_blks_hit + shared_blks_read, 0) * 100,
            2
        )                                          AS cache_hit_ratio_pct,
        round(total_exec_time::numeric, 2)         AS total_exec_time_ms,
        round(mean_exec_time::numeric, 2)          AS mean_exec_time_ms
    FROM pg_stat_statements
    WHERE query NOT ILIKE '%pg_stat_statements%'
      AND calls > 200
      AND (shared_blks_hit + shared_blks_read) > 1000   -- ignore trivially small queries
      AND shared_blks_hit::numeric /
          NULLIF(shared_blks_hit + shared_blks_read, 0) < 0.80
    ORDER BY cache_hit_ratio_pct ASC
    LIMIT 20
)
SELECT
    queryid,
    calls,
    shared_blks_hit       AS blks_from_cache,
    shared_blks_read      AS blks_from_disk,
    cache_hit_ratio_pct   AS "cache_hit_%",
    total_exec_time_ms,
    mean_exec_time_ms,
    left(query, 200)      AS query_preview
FROM cache_ratio
ORDER BY cache_hit_ratio_pct ASC;


-- ---------------------------------------------------------------------------
-- SECTION 6: Temp spill, planning time, and WAL volume (top 20 by temp written)
-- ---------------------------------------------------------------------------
-- Why: temp_blks_written > 0 means a sort, hash, or materialize step spilled
-- to disk because it did not fit in work_mem — a signal the other sections
-- miss. total_plan_time shows queries whose planning is a large share of the
-- cost (it stays 0 unless pg_stat_statements.track_planning = on). wal_bytes
-- shows write-heavy statements that drive replication lag and checkpoints.
-- Columns: temp_blks_*, total_plan_time and wal_bytes exist from PG13.
--
-- Next step: EXPLAIN (ANALYZE, BUFFERS) the query and look for
--            "Sort Method: external merge" or hash "Batches" > 1; then try a
--            better index, a narrower result, or a per-session/role work_mem
--            increase (not a global one — work_mem is per operation).
-- ---------------------------------------------------------------------------

SELECT
    queryid,
    calls,
    temp_blks_written,
    round(temp_blks_written::numeric / NULLIF(calls, 0), 1)  AS temp_blks_per_call,
    round(total_plan_time::numeric, 2)                       AS total_plan_time_ms,
    round(total_exec_time::numeric, 2)                       AS total_exec_time_ms,
    pg_size_pretty(wal_bytes)                                AS wal_total,
    left(query, 200)                                         AS query_preview
FROM pg_stat_statements
WHERE query NOT ILIKE '%pg_stat_statements%'
  AND (temp_blks_written > 0 OR wal_bytes > 0)
ORDER BY temp_blks_written DESC, wal_bytes DESC
LIMIT 20;
