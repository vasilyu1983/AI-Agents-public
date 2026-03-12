```markdown
# SQL Lock & Concurrency Analysis Template

*Purpose: A dedicated template for diagnosing lock contention, blocking chains, deadlocks, long-running transactions, and concurrency-related performance regressions.*

---

## 1. Incident Overview

**Issue Title:**  
[Lock contention / blocking / deadlock / long-running txn]

**Severity:**  
- [ ] P0 – Production outage  
- [ ] P1 – Major degradation  
- [ ] P2 – Minor  
- [ ] P3 – Low  

**Start Time:**  
[Timestamp]

**Business/User Impact:**  
[Describe impact: e.g., checkout failures, API timeouts]

**Databases Affected:**  
[List instances/clusters]

---

## 2. Symptoms

Check all that apply:

- [ ] Slow queries  
- [ ] Increased latency  
- [ ] API timeouts  
- [ ] Failed transactions  
- [ ] Replication lag  
- [ ] High CPU  
- [ ] High idle-in-transaction connections  

**Notes:**  
[Add brief description]

---

## 3. Environment Snapshot

### 3.1 Postgres

Run:
```

SELECT pid, usename, application_name,
       state, wait_event_type, wait_event,
       backend_xmin, backend_xid,
       query_start, xact_start,
       query
FROM pg_stat_activity;

```

Locks:
```

SELECT * FROM pg_locks;

```

Blocking chain:
```

SELECT blocked_locks.pid     AS blocked_pid,
       blocking_locks.pid    AS blocking_pid,
       blocked_activity.query AS blocked_query,
       blocking_activity.query AS blocking_query
FROM pg_locks blocked_locks
JOIN pg_locks blocking_locks
  ON blocked_locks.locktype = blocking_locks.locktype
 AND blocked_locks.database IS NOT DISTINCT FROM blocking_locks.database
 AND blocked_locks.relation IS NOT DISTINCT FROM blocking_locks.relation
 AND blocked_locks.page IS NOT DISTINCT FROM blocking_locks.page
 AND blocked_locks.tuple IS NOT DISTINCT FROM blocking_locks.tuple
 AND blocked_locks.virtualxid IS NOT DISTINCT FROM blocking_locks.virtualxid
 AND blocked_locks.transactionid IS NOT DISTINCT FROM blocking_locks.transactionid
 AND blocked_locks.classid IS NOT DISTINCT FROM blocking_locks.classid
 AND blocked_locks.objid IS NOT DISTINCT FROM blocking_locks.objid
 AND blocked_locks.objsubid IS NOT DISTINCT FROM blocking_locks.objsubid
 AND blocked_locks.pid <> blocking_locks.pid
JOIN pg_stat_activity blocked_activity
  ON blocked_activity.pid = blocked_locks.pid
JOIN pg_stat_activity blocking_activity
  ON blocking_activity.pid = blocking_locks.pid
WHERE NOT blocked_locks.granted;

```

---

### 3.2 MySQL

Long-running transactions:
```

SELECT * FROM information_schema.innodb_trx;

```

Locks:
```

SELECT * FROM information_schema.innodb_locks;

```

Lock waits:
```

SELECT * FROM information_schema.innodb_lock_waits;

```

---

## 4. Findings

### 4.1 Blocking Query

**Blocking PID:**  
[x]

**Blocking Query Text:**  
```

<query>
```

**Start Time:**  
[Timestamp]

**App/Source:**  
[service name / migration / background worker]

---

### 4.2 Blocked Queries

List blocked PIDs and queries:

| PID | Duration | Query |
|-----|----------|--------|
| | | |
| | | |

**Notes:**  
[Describe patterns in blocked queries]

---

## 5. Lock Type Analysis

| Lock Type | Meaning | Impact |
|-----------|----------|---------|
| RowExclusiveLock | Writes | Medium |
| AccessShareLock | Reads | Low |
| AccessExclusiveLock | DDL | Highest |
| ShareLock | FK checks | Medium |
| RowShareLock | SELECT FOR SHARE | Medium |

Checklist:

- [ ] DDL causing lock?  
- [ ] Long-running UPDATE/DELETE?  
- [ ] SELECT FOR UPDATE misuse?  
- [ ] Index creation without CONCURRENTLY?  
- [ ] Idle in transaction but holding locks?  

---

## 6. Transaction Analysis

**Longest-running transaction:**

| PID | xact_start | Duration | Query |
|-----|------------|----------|--------|
| | | | |

Checklist:

- [ ] BEGIN without COMMIT/ROLLBACK  
- [ ] Large write transaction  
- [ ] Unbounded DELETE/UPDATE  
- [ ] ORM holding open session  
- [ ] App not releasing connection  

---

## 7. Deadlock Investigation

Paste deadlock log lines:

```
<deadlock logs>
```

Checklist:

- [ ] Conflicting UPDATE patterns  
- [ ] Opposite lock ordering  
- [ ] Same table accessed in different order  
- [ ] Conflicting FK cascades  
- [ ] SELECT FOR UPDATE used unnecessarily  

Common Fix Patterns:

- Normalize lock order across code paths  
- Reduce transaction scope  
- Remove FK cascades or reorder operations  
- Use SKIP LOCKED for concurrent workers  
- Replace SELECT FOR UPDATE with advisory locks if safe  

---

## 8. Bloat & Autovacuum Considerations (Postgres)

Check:

- [ ] Table bloat > 20%  
- [ ] Index bloat > 30%  
- [ ] Autovacuum stuck or lagging  
- [ ] HOT updates ineffective  
- [ ] Dead tuples accumulating  

Commands:

```
SELECT * FROM pg_stat_all_tables;
```

```
SELECT * FROM pgstattuple('table');
```

---

## 9. Root Cause Summary

**Primary Cause:**  
[e.g., ALTER TABLE blocking writes, long-running transaction, bad JOIN, deadlock loop]

**Contributing Factors:**  

- [ ] Missing index  
- [ ] ORM query explosion  
- [ ] Autovacuum freeze  
- [ ] Heavy write burst  
- [ ] Poor pagination  
- [ ] Unbounded updates  

---

## 10. Fixes Implemented

### Immediate Fixes

- [ ] Terminate blocking PID  
- [ ] Kill idle-in-transaction sessions  
- [ ] Disable problematic migration job  
- [ ] Reduce batch sizes  
- [ ] Apply temporary index  

### Permanent Fixes

- [ ] Rewrite blocking query  
- [ ] Adjust transaction scoping  
- [ ] Reorder operations to avoid deadlocks  
- [ ] Add missing index  
- [ ] Use CONCURRENTLY for DDL  

---

## 11. Verification

### 11.1 Lock & Activity Check

- [ ] No blocking PIDs  
- [ ] No long-running transactions  
- [ ] No deadlocks in logs  
- [ ] pg_locks normal  

### 11.2 Performance Check

- [ ] Latency normalized  
- [ ] CPU stable  
- [ ] I/O stable  
- [ ] No autovacuum starvation  

### 11.3 Replication Check

- [ ] Lag cleared  
- [ ] No WAL spikes  

---

## 12. Final Notes

[List follow-up tasks, monitoring additions, or code fixes required.]

---

## 13. Complete Example

**Issue:** `ALTER TABLE orders ADD COLUMN metadata JSONB` blocked all writes for 7 minutes.

**Root Cause:** DDL executed without `CONCURRENTLY` during traffic peak.

**Fix:**  

- Killed blocking PID  
- Postponed DDL to maintenance  
- Re-ran via online-safe alternative  
- Added alerts for AccessExclusiveLock > 3s

**Verification:** System stable, no replication lag.

---

# END

```
