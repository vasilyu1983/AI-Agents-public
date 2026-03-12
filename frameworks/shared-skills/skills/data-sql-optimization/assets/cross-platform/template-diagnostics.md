```markdown
# SQL Diagnostics Template

*Purpose: A specialized template for diagnosing slow queries, lock contention, deadlocks, storage bloat, CPU/I/O pressure, or unexplained database performance regressions.*

---

## 1. Incident Overview

**Issue Type:**  
- [ ] Slow query  
- [ ] Locking/blocking  
- [ ] Deadlock  
- [ ] High CPU  
- [ ] High I/O  
- [ ] Memory pressure  
- [ ] Table/index bloat  
- [ ] Replication lag  
- [ ] Connection saturation  

**Impact:**  
[Describe user/system impact]

**Start Time:**  
[Timestamp]

**Severity:**  
- [ ] P0  
- [ ] P1  
- [ ] P2  

---

## 2. Reproduction Details

**Query or Operation:**
```

-- Paste query or operation

```

**Example Parameters:**
| Parameter | Example | Notes |
|----------|----------|-------|
| user_id | 123 | high-frequency |
| date_to | 2023-01-01 | optional |

**Frequency:**  
- [ ] Consistent  
- [ ] Intermittent  
- [ ] Parameter-dependent  
- [ ] Spike under load  

---

## 3. Environment Snapshot

### 3.1 Postgres Metrics (if applicable)
- `pg_stat_activity` sample  
- `pg_locks` snapshot  
- Check blocked/blocked_by columns  
- autovacuum activity  
- replication lag  
- checkpoints & WAL stats  

### 3.2 MySQL Metrics (if applicable)
- `INNODB_TRX`, `INNODB_LOCKS`, `INNODB_LOCK_WAITS`  
- slow query log entries  
- buffer pool hit rate  
- temp table usage  
- row lock waits  

**Paste relevant metric samples here**

---

## 4. Execution Plan Capture

Use real parameters.

```

EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON)
<query>

```

### Quick Checks:
- [ ] Seq Scan (unexpected)  
- [ ] Slow nested loop  
- [ ] Hash join spilling to disk  
- [ ] Sort spilling to disk  
- [ ] Rows out of estimation  
- [ ] Low filter ratio  
- [ ] High memory usage  

---

## 5. Diagnostics Workflows

### 5.1 Slow Query Root Cause Analysis

**Checklist:**
- [ ] Inefficient filter (no index)  
- [ ] Poor join ordering  
- [ ] Misestimated row counts  
- [ ] Large table scan  
- [ ] Function on indexed column  
- [ ] OR conditions causing seq scan  
- [ ] Too many nested loops  
- [ ] Distinct / Group By causing heavy sort  
- [ ] Missing LIMIT  
- [ ] Inefficient pagination (OFFSET)  

---

### 5.2 Lock Contention Analysis

**Queries:**
```

SELECT pid, state, wait_event_type, wait_event, query
FROM pg_stat_activity;

```

```

SELECT * FROM pg_locks;

```

**Identify:**
- [ ] Blocking PID  
- [ ] Type of lock (RowExclusive, AccessExclusive, etc.)  
- [ ] Query causing blockage  
- [ ] Long-running transaction (> 60s)  
- [ ] Uncommitted write holding locks  

**Fix Patterns:**
- Kill blocker (only if safe)  
- Rewrite transaction to commit sooner  
- Convert update to batch mode  
- Avoid `ALTER TABLE` in peak hours  

---

### 5.3 Deadlock Analysis

**Postgres Example Log:**
```

ERROR: deadlock detected
DETAIL: Process X waits for ShareLock on transaction Y...

```

**Checklist:**
- [ ] Identify conflicting statements  
- [ ] Normalize lock ordering  
- [ ] Reduce transaction scope  
- [ ] Avoid selecting rows “FOR UPDATE” unnecessarily  
- [ ] Review foreign key cascades  

---

### 5.4 Memory / Sort Spill Analysis

**Indicators:**
- Hash Join using temp files  
- Sort using disk (external sort)  
- EXPLAIN shows: `Disk: 120MB`  

**Fix Patterns:**
- Add index aligning with ORDER BY  
- Rewrite GROUP BY  
- Reduce result set size  
- Tune `work_mem` (Postgres) per query via SET LOCAL  

---

### 5.5 I/O Pressure Diagnosis

Check:
- Index fragmentation  
- Bloat percentage  
- Buffer cache miss rate  
- Vacuum lag  
- Large sequential scans on frequently accessed tables  

**Fix Patterns:**
- Add targeted indexes  
- Rebuild index if > 30% bloat  
- Adjust autovacuum scale factors  
- Analyze table  

---

### 5.6 Replication Lag

Check:
- WAL generation spikes  
- Large batch updates  
- Long-running vacuum  
- Write-amplifying indexes  

**Fix Patterns:**
- Break writes into batches  
- Increase replica resources  
- Move large maintenance operations off-peak  

---

## 6. Change Experiments

List small reversible experiments:

- [ ] Add temporary index  
- [ ] Rewrite join order  
- [ ] Add LIMIT during debugging  
- [ ] Sample parameters differently  
- [ ] Tune memory parameters (session-based)  
- [ ] Toggle `enable_seqscan` or `enable_indexscan` (debug only)  

---

## 7. Fix Summary

**Primary Root Cause:**  
[e.g., Missing composite index]

**Fix Applied:**  
[Describe changes]

**Expected Improvement:**  
[ms -> ms]

**Risk Level:**  
- [ ] Low  
- [ ] Medium  
- [ ] High  

---

## 8. Verification Checklist

**After Fix:**
- [ ] Latency meets SLO  
- [ ] Execution plan stable  
- [ ] No new regressions  
- [ ] No increased lock contention  
- [ ] No disk spills  
- [ ] CPU/I/O stable  
- [ ] Stats updated (`ANALYZE`)  
- [ ] Index usage confirmed  

---

## 9. Complete Example

### Issue:
Query slow when filtering orders by customer_id and date range.

### Root Cause:
Seq Scan scanning 2M rows due to missing index.

### Fix:
```

CREATE INDEX idx_orders_customer_ts
ON orders(customer_id, created_at DESC)
INCLUDE (total);

```

### Result:
Latency improved from 900ms -> 6ms.

### Verification:
[check] Index Scan  
[check] Sort removed  
[check] No lock contention  

---

# END
```
