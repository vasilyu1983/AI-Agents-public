```markdown
# Slow Query Analysis Template

*Purpose: A structured template for analyzing, diagnosing, and resolving slow SQL queries in production environments.*

---

## 1. Summary

**Query / Endpoint:**  
[Copy SQL or name of endpoint]

**Severity:**  
- [ ] P0 (critical outage)  
- [ ] P1 (major latency impact)  
- [ ] P2  
- [ ] P3  

**Start Time:**  
[Timestamp]

**User Impact:**  
[What users experience]

**System Impact:**  
- [ ] High CPU  
- [ ] High I/O  
- [ ] Connection saturation  
- [ ] Deadlocks  
- [ ] Increased error rate  
- [ ] Replication lag  

---

## 2. Query Example(s)

Paste real queries with real parameters:

```

SELECT ...
FROM ...
WHERE ...
ORDER BY ...

```

**Parameter Notes:**  
- Typical:  
- Slowest:  
- Skewed values:  

---

## 3. Workload Characteristics

| Attribute | Value |
|----------|-------|
| Frequency | High / Medium / Low |
| Latency Target | [ms] |
| Peak Latency Observed | [ms] |
| Table Size | [row count] |
| Query Source | API, cron, ORM, report |

---

## 4. Initial Findings

### 4.1 Observed Symptoms
- [ ] Increased latency  
- [ ] Timeouts  
- [ ] CPU spike  
- [ ] Disk reads rising  
- [ ] Temp file usage  
- [ ] Lock waits  

### 4.2 Application Logs
Paste relevant logs or errors.

```

<logs>
```

---

## 5. Metrics Snapshot

### 5.1 Postgres

- `pg_stat_statements` entry  
- buffer hit ratio  
- deadlocks  
- autovacuum/backfill interactions  
- seq scan count  

### 5.2 MySQL

- slow query log entry  
- InnoDB row lock waits  
- buffer pool hit rate  
- temporary table usage  

Paste metric excerpts:

```
<metrics>
```

---

## 6. Execution Plan

Paste EXPLAIN output:

```
EXPLAIN (ANALYZE, BUFFERS)
<query>
```

### Quick Checks

- [ ] Seq Scan unexpectedly  
- [ ] Bitmap scan that should be index scan  
- [ ] Hash join / sort spilled to disk  
- [ ] Estimated vs actual rows mismatch  
- [ ] Multiple nested loops  
- [ ] Wide rows causing I/O pressure  

---

## 7. Execution Plan Analysis

### 7.1 Scan Analysis

| Type | Reason | Notes |
|------|--------|-------|
| Seq Scan | Missing index | |
| Index Scan | Correct | |
| Index Only Scan | Ideal | |

Checklist:

- [ ] WHERE clause uses indexable patterns  
- [ ] No function on indexed column  
- [ ] Filter selectivity acceptable  

---

### 7.2 Join Analysis

| Join | Algorithm | Good? | Notes |
|------|-----------|--------|-------|
| table A -> B | Hash Join | Yes | |
| table B -> C | Nested Loop | No | Missing index |

Checklist:

- [ ] Join keys indexed  
- [ ] Large table joined first? (anti-pattern)  
- [ ] Rewrite join order needed?  

---

### 7.3 Sort / Aggregate Analysis

Issues:

- [ ] Sort too large -> disk spill  
- [ ] GROUP BY high cardinality  
- [ ] ORDER BY not backed by index  

Fixes:

- Add index matching ORDER BY  
- Pre-aggregate if meaningful  
- Reduce cardinality if possible  

---

## 8. Root Cause Hypotheses

Check all that apply:

- [ ] Missing composite index  
- [ ] Incorrect index order  
- [ ] Data skew (hot key)  
- [ ] Function preventing index usage  
- [ ] OR/filter causing full scan  
- [ ] JOIN reordering required  
- [ ] Statistics outdated  
- [ ] Table or index bloat  
- [ ] Lock contention  
- [ ] Inefficient pagination  
- [ ] ORM-generated inefficient SQL  

Notes:
[Explain key suspects]

---

## 9. Experiments

List short, reversible tests:

- [ ] Add temporary index  
- [ ] Force join order (`enable_hashjoin = off`, Postgres for debugging)  
- [ ] Parameter variation tests  
- [ ] Rewrite WHERE clause  
- [ ] Keyset pagination test  
- [ ] Increase memory locally (session-level work_mem)  
- [ ] Test LIMIT or narrowing results  

---

## 10. Final Fix

**Fix Implemented:**  
[Index added / Query rewritten / Stats updated / Pagination changed]

**SQL / DDL Applied:**

```
<paste changes>
```

**Reasoning:**  
[Why this fix works]

**Risk Level:**  

- [ ] Low  
- [ ] Medium  
- [ ] High  

---

## 11. Verification

### 11.1 Performance Comparison

| Test Case | Before (ms) | After (ms) |
|-----------|--------------|-------------|
| Typical params | | |
| Worst-case params | | |
| p95 latency | | |
| p99 latency | | |

### 11.2 Plan Verification

- [ ] Index scan used  
- [ ] Sort removed  
- [ ] Join algorithm optimal  
- [ ] Estimated vs actual rows aligned  

### 11.3 System Verification

- [ ] CPU normalized  
- [ ] I/O normalized  
- [ ] No lock waits  
- [ ] Replication lag normal  

---

## 12. Final Notes & Follow-Up

- [ ] Documented in runbook  
- [ ] Added regression test cases  
- [ ] Scheduled index review  
- [ ] Additional optimizations deferred list  

---

## 13. Complete Example

**Problem:** Slow user dashboard query scanning 2.1M rows.

**Root Cause:** Missing composite index on `(user_id, created_at DESC)`.

**Fix:**

```
CREATE INDEX idx_orders_user_ts
ON orders(user_id, created_at DESC)
INCLUDE (total);
```

**Result:**  
Latency improved 960ms -> 7ms.  
Sort eliminated.  
Index-only scan achieved.

**Verification:**  
[check] CPU drop  
[check] No spills  
[check] p95 < 10ms

---

# END

```
