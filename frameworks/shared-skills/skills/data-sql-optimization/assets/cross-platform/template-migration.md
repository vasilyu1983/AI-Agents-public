```markdown
# SQL Migration Template (Zero-Downtime Safe Changes)

*Purpose: A production-ready template for designing, executing, and validating safe SQL schema changes, ensuring backward compatibility, no downtime, and minimal operational risk.*

---

## 1. Migration Summary

**Title:**  
[Add/modify/drop <column/table/index> safely]

**Author:**  
[Name]

**Date:**  
[YYYY-MM-DD]

**Environment(s):**  
- [ ] Production  
- [ ] Staging  
- [ ] Development  

**Migration Type:**  
- [ ] Add Column  
- [ ] Drop Column  
- [ ] Rename Column  
- [ ] Add Table  
- [ ] Change Type  
- [ ] Add/Modify Index  
- [ ] Add Constraint  
- [ ] Remove Constraint  
- [ ] Data Backfill  
- [ ] Structural Refactor  

**Business Rationale:**  
[Describe what this enables and why]

---

## 2. Impact Assessment

| Area | Impact |
|------|--------|
| Read workload | |
| Write workload | |
| Locking risk | |
| Disk growth | |
| Replication lag risk | |
| Rollout complexity | |

### Risk Level
- [ ] Low  
- [ ] Medium  
- [ ] High  

---

## 3. Compatibility Strategy

Is the migration **backward compatible**?

- [ ] Yes — Application works with old + new schema  
- [ ] No — Requires coordinated deployment  
- [ ] Partially — Requires dual-write or view abstraction  

### Strategy Selected

- [ ] Expand -> Migrate Data -> Contract  
- [ ] Blue/green rollout  
- [ ] Dual-read / dual-write  
- [ ] Shadow column  
- [ ] Compatibility view  
- [ ] Two-phase constraint validation  

---

## 4. Migration Steps (Detailed)

Document every step so ops/DBAs can execute safely.

### Step 1 — Pre-checks
- [ ] Backup available + verified  
- [ ] Sufficient disk space  
- [ ] No long-running transactions  
- [ ] No autovacuum freeze risk (Postgres)  
- [ ] No replication lag  
- [ ] Peak traffic window avoided  

---

### Step 2 — Schema Expansion (Non-Breaking)

(Add structures without removing or modifying existing ones.)

Examples:

**Add Column**
```

ALTER TABLE users ADD COLUMN timezone TEXT;

```

**Add Table**
```

CREATE TABLE audit_log (...);

```

**Add Index Concurrently (Postgres)**
```

CREATE INDEX CONCURRENTLY idx_users_timezone ON users(timezone);

```

Checklist:
- [ ] No blocking DDL  
- [ ] Constraints not enforced yet  
- [ ] Defaults not expensive (avoid volatile expressions)  

---

### Step 3 — Data Backfill (Batch Safe)

Perform in small chunks to avoid locks, I/O spikes, and replication lag.

```

UPDATE users
SET timezone='UTC'
WHERE timezone IS NULL
LIMIT 5000;

```

Checklist:
- [ ] Batch size tuned  
- [ ] Progress logged  
- [ ] Autovacuum impact monitored  
- [ ] Replication lag tracked  
- [ ] Use retry-safe logic  

---

### Step 4 — Application Rollout

- [ ] App reads both old + new fields  
- [ ] Writes new field (dual-write if needed)  
- [ ] Feature flags applied  
- [ ] Observability in place (metrics, logs, dashboards)  

---

### Step 5 — Constraint Enforcement

Enable constraints only after data is consistent.

Examples:

**Set NOT NULL after backfill**
```

ALTER TABLE users ALTER COLUMN timezone SET NOT NULL;

```

**Foreign Key (safe Postgres pattern)**
```

ALTER TABLE orders
ADD CONSTRAINT orders_user_fkey
FOREIGN KEY (user_id) REFERENCES users(id)
NOT VALID;

ALTER TABLE orders VALIDATE CONSTRAINT orders_user_fkey;

```

Checklist:
- [ ] No NULL/invalid values remain  
- [ ] Validate constraint usage in staging  
- [ ] Constraint validation monitored  

---

### Step 6 — Cleanup (Contract Phase)

Remove deprecated structures after verifying stability.

Examples:

**Drop Old Column**
```

ALTER TABLE users DROP COLUMN timezone_old;

```

**Rename Safe**
```

ALTER TABLE users RENAME COLUMN timezone_new TO timezone;

```

Checklist:
- [ ] Confirm no traffic uses old structures  
- [ ] No references in code, functions, or triggers  
- [ ] Run plan on queries that depend on this table  

---

## 5. Rollback Plan

**Rollback Steps:**

1. Stop new writes if corruption suspected  
2. Re-enable old column/tables if dual-write was used  
3. Drop partially created constraints or indexes  
4. Apply backup restore (worst-case scenario)  
5. Roll back application code version  

Checklist:
- [ ] Rollback tested in staging  
- [ ] Data integrity maintained  
- [ ] Clear owner assigned for rollback execution  

---

## 6. Verification & Post-Migration Checks

### Functional Validation
- [ ] Application reads/writes correct data  
- [ ] Old pathways disabled  
- [ ] New schema recognized by ORM/tooling  

### Performance Validation
- [ ] No new seq scans  
- [ ] No excessive sorting or temp files  
- [ ] Index usage verified  

### Integrity Validation
- [ ] FKs valid  
- [ ] Unique constraints correct  
- [ ] Row counts consistent  

### Operational Validation
- [ ] Replication lag normalized  
- [ ] No long-running autovacuum  
- [ ] No lock alerts  
- [ ] No error spikes  

---

## 7. Example Completed Migration Template

**Goal:** Add `timezone` to `users` table for scheduled notification feature.

**Impact:** Moderate. Write overhead negligible.

**Steps:**  
1. Add NULL-able column  
2. Backfill ~12M rows in 5k batches  
3. Deploy app writing new column  
4. Set NOT NULL  
5. Drop fallback logic  

**Rollback:**  
- Remove NOT NULL  
- Re-enable dual-write  
- Fallback to old timezone behavior  

**Validation:**  
[check] All rows backfilled  
[check] Constraints applied cleanly  
[check] Query plans unchanged  
[check] Replication lag < 250ms  

---

# END
```
