```markdown
# SQL Schema Design Template

*Purpose: A complete template for designing new database schema structures or refactoring existing ones. Covers modeling, normalization, integrity, sizing, indexing, and operational impacts.*

---

## 1. Overview

**Feature / Component Name:**  
[Describe what this schema enables]

**Author:**  
[Name]

**Date:**  
[YYYY-MM-DD]

**Business Requirements (Summary):**  
- [Requirement 1]  
- [Requirement 2]  
- [Requirement 3]  

**Functional Requirements Impacting Schema:**  
- [ ] Must store historical versions  
- [ ] Must support search/filtering  
- [ ] Must support high write throughput  
- [ ] Must support analytics queries  
- [ ] Must support soft deletes  
- [ ] Must support multi-tenancy  
- [ ] Must support GDPR deletion  

---

## 2. Data Model Definition

### 2.1 Table Definitions

Use this format for each new/modified table.

```

Table: <table_name>

Columns:

- id BIGSERIAL PRIMARY KEY
- <column_name> <datatype> [NULL|NOT NULL] [DEFAULT ...]
- created_at TIMESTAMPTZ DEFAULT NOW()
- updated_at TIMESTAMPTZ DEFAULT NOW()

Notes:

- <describe purpose of table>
- <expected relationships>
- <expected row growth>

```

---

### 2.2 Column Details Table

| Column | Type | Nullable | Default | Description | Notes |
|--------|------|----------|----------|-------------|--------|
| id | BIGSERIAL | no | PK | unique identifier | |
|  |  |  |  |  | |

---

### 2.3 Relationship Plan

List all foreign keys and referential rules.

| Relation | Type | Cardinality | FK? | On Delete | Notes |
|----------|------|-------------|-----|-----------|--------|
| orders -> users | parent-child | N:1 | Yes | NO ACTION | |
| product_attributes -> products | detail | N:1 | Yes | CASCADE | |

---

## 3. Normalization & Data Modeling Decisions

### 3.1 Normalization Level

- [ ] 1NF  
- [ ] 2NF  
- [ ] 3NF  
- [ ] BCNF  
- [ ] Intentional denormalization  

**Rationale:**  
[Explain choice and trade-offs]

---

### 3.2 Anti-pattern Check

Mark any found:

- [ ] EAV (Entity-Attribute-Value)  
- [ ] Multi-value columns  
- [ ] Polymorphic associations  
- [ ] Oversized JSONB fields  
- [ ] Tables without primary keys  
- [ ] Overloaded “bucket” tables  

**Fix Strategy:**  
[Describe approach]

---

### 3.3 Cardinality & Fan-out Checks

| Table | Expected Rows | Growth Rate | High Fan-out? | Notes |
|--------|----------------|-------------|----------------|--------|
|  |  |  |  | |

---

### 3.4 Soft Delete Strategy

- [ ] Use `deleted_at` timestamp  
- [ ] Use status column  
- [ ] Avoid hard deletes  
- [ ] Partition deleted rows  

---

## 4. Index Strategy

### 4.1 Required Indexes

List required indexes and purpose:

| Index Name | Table | Columns | Type | Purpose |
|------------|--------|---------|------|---------|
| idx_orders_user_ts | orders | (user_id, created_at) | btree | lookup/sort |  
|  |  |  |  | |

---

### 4.2 Optional / Conditional Indexes

| Index | Condition to Add (when traffic reaches X) | Notes |
|--------|--------------------------------------------|--------|
| | | |

---

### 4.3 Fulltext / Search Indexes

If search heavy:

- [ ] Postgres GIN + `to_tsvector`  
- [ ] Trigram index for LIKE '%pattern%'  
- [ ] MySQL FULLTEXT  

---

## 5. Constraints & Integrity

### 5.1 Constraint Inventory

| Type | Applied? | Details |
|-------|----------|---------|
| NOT NULL | | |
| CHECK | | |
| UNIQUE | | |
| FOREIGN KEY | | |
| Composite Key | | |
| Exclusion Constraints (PG) | | |

---

### 5.2 CHECK Constraint Examples

```

ALTER TABLE orders
ADD CONSTRAINT chk_total_nonnegative
CHECK (total >= 0);

```

---

### 5.3 Multi-table Integrity Rules

- [ ] FK ensures referential integrity  
- [ ] No cascading deletes unless intentional  
- [ ] Use soft deletes with care when FKs exist  

---

## 6. Performance & Workload Considerations

### 6.1 Access Patterns

Mark applicable:

- [ ] Key-based lookups  
- [ ] Range scans  
- [ ] Aggregations  
- [ ] Joins across many tables  
- [ ] Time-series data  
- [ ] Batch writes  
- [ ] Read-heavy workload  
- [ ] Write-heavy workload  

---

### 6.2 Expected Query Examples

Paste sample queries:

```

SELECT ...
FROM ...
WHERE ...

```

---

### 6.3 Partitioning (if needed)

| Partition Type | Use Case |
|----------------|-----------|
| Range | date-based tables |
| List | tenants, categories |
| Hash | write scalability |

---

## 7. Storage Estimates

| Table | Expected Rows (1yr) | Row Size | Table Size | Index Size |
|--------|-----------------------|-----------|------------|-------------|
| users | 12M | 180 bytes | ~2GB | ~700MB |
|  |  |  |  | |

---

## 8. Migration & Deployment Strategy

- [ ] Expand -> Migrate -> Contract  
- [ ] Backfill in batches  
- [ ] Add indexes concurrently (Postgres)  
- [ ] Staged constraint validation  
- [ ] Dual-write and dual-read if needed  
- [ ] Application compatibility checked  
- [ ] Rollback plan documented  

---

## 9. Operational Considerations

### 9.1 Vacuum (Postgres)

- [ ] Expected dead tuple impact  
- [ ] HOT update friendliness  
- [ ] Autovacuum scaling required?  

### 9.2 Replication

- [ ] Will writes increase WAL/binlog?  
- [ ] Will schema affect replica performance?  

### 9.3 Backups / HA

- [ ] Large tables require PITR?  
- [ ] Partitioning helps backups?  

---

## 10. Final Review Checklist

### Modeling
- [ ] No anti-patterns present  
- [ ] Primary key defined  
- [ ] Constraints validated  
- [ ] Schema normalized appropriately  

### Performance
- [ ] Indexes validated with sample queries  
- [ ] ORDER BY coverage ensured  
- [ ] JOIN patterns evaluated  

### Safety
- [ ] Migration plan safe  
- [ ] Rollback documented  
- [ ] No blocking DDL in production  

### Maintenance
- [ ] Stats & autovacuum considered  
- [ ] Long-term scaling evaluated  

---

## 11. Complete Example

**Feature:** Tiered user profiles  
**New Table:** `user_profile_metadata`

```

CREATE TABLE user_profile_metadata (
  user_id BIGINT PRIMARY KEY REFERENCES users(id),
  bio TEXT,
  tier TEXT NOT NULL,
  preferences JSONB,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

```

**Indexes:**
```

CREATE INDEX idx_user_profile_tier ON user_profile_metadata(tier);
CREATE INDEX idx_user_profile_prefs_gin ON user_profile_metadata USING GIN (preferences);

```

**Notes:**
- Tier is filterable -> btree index  
- JSONB preferences search -> GIN  
- Data expected: ~50M rows in 12 months  

**Migration Strategy:**
- Add table  
- Backfill key metadata for active users  
- Deploy app writing to new table  

---

# END
```
