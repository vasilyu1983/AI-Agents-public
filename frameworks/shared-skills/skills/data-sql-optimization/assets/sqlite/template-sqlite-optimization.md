```markdown
# SQLite Query Optimization Template

*Purpose: Structured template for optimizing SQLite queries, indexes, and database configuration for embedded and mobile applications.*

---

## When to Use

Use this template for:
- Optimizing SQLite queries in mobile apps (iOS, Android)
- Embedded database performance tuning
- Local-first application optimization
- Desktop application SQLite optimization

---

## Structure

1. **Query & Context**
2. **EXPLAIN QUERY PLAN Analysis**
3. **Optimization Strategies**
4. **Configuration Tuning**

---

# TEMPLATE STARTS HERE

## 1. Query & Context

- **Query:**
  [Paste SQL statement]

- **Application Context:**
  - [ ] Mobile app (iOS/Android)
  - [ ] Desktop application
  - [ ] Embedded system
  - [ ] Web application (local storage)

- **Database Size:**
  [e.g., 10 MB, 500 MB, 2 GB]

- **Table(s) Involved:**
  [Table names and row counts]

- **Expected Result Size:**
  [Rows expected]

---

## 2. EXPLAIN QUERY PLAN Analysis

### Capture Query Plan

```sql
EXPLAIN QUERY PLAN
SELECT * FROM orders WHERE customer_id = 12345;
```

### Understanding SQLite Query Plans

**Scan Operations:**
- **SCAN TABLE** - Full table scan (no index used)
- **SEARCH TABLE USING INDEX** - Index is being used (good!)
- **SEARCH TABLE USING COVERING INDEX** - All columns in index (best!)
- **AUTOMATIC INDEX** - SQLite created temp index (consider permanent index)

**Join Operations:**
- **SCAN SUBQUERY** - Subquery scanned
- **USE TEMP B-TREE FOR ORDER BY** - Temporary index for sorting

---

### Analysis Checklist

- [ ] Is query using **SCAN TABLE** where index should be used?
- [ ] Are there **AUTOMATIC INDEX** warnings (create permanent index)?
- [ ] Is query using **COVERING INDEX** for SELECT columns?
- [ ] Are **TEMP B-TREE** structures being created (expensive)?
- [ ] Are joins using indexes on both sides?

---

## 3. Optimization Strategies

### 3.1 Index Creation

#### Single Column Index
```sql
CREATE INDEX idx_orders_customer_id
ON orders(customer_id);
```

#### Composite Index
```sql
CREATE INDEX idx_orders_customer_date
ON orders(customer_id, order_date);
```

#### Covering Index (Include all SELECT columns)
```sql
-- Query: SELECT customer_id, order_date, total FROM orders WHERE customer_id = ?
CREATE INDEX idx_orders_covering
ON orders(customer_id, order_date, total);
```

#### Partial Index (SQLite 3.8.0+)
```sql
-- Index only active orders
CREATE INDEX idx_orders_active
ON orders(customer_id)
WHERE status = 'active';
```

#### Expression Index (SQLite 3.9.0+)
```sql
-- Index on computed expression
CREATE INDEX idx_customers_lower_email
ON customers(LOWER(email));
```

---

### 3.2 Query Rewriting

#### Use WHERE Instead of HAVING
**Bad:**
```sql
SELECT customer_id, COUNT(*)
FROM orders
GROUP BY customer_id
HAVING customer_id > 1000;
```

**Good:**
```sql
SELECT customer_id, COUNT(*)
FROM orders
WHERE customer_id > 1000
GROUP BY customer_id;
```

#### Avoid Functions on Indexed Columns
**Bad:**
```sql
SELECT * FROM orders WHERE DATE(order_date) = '2025-11-18';
```

**Good:**
```sql
SELECT * FROM orders
WHERE order_date >= '2025-11-18 00:00:00'
  AND order_date < '2025-11-19 00:00:00';
```

#### Use LIMIT for Pagination
```sql
-- Efficient pagination
SELECT * FROM orders
WHERE customer_id = ?
ORDER BY order_date DESC
LIMIT 20 OFFSET 0;
```

#### Replace IN with JOIN for Large Lists
**Bad (slow for large IN lists):**
```sql
SELECT * FROM orders WHERE customer_id IN (1,2,3,...,1000);
```

**Good:**
```sql
-- Create temp table with IDs, then join
CREATE TEMP TABLE temp_ids(id INTEGER);
INSERT INTO temp_ids VALUES (1),(2),(3);

SELECT o.*
FROM orders o
JOIN temp_ids t ON o.customer_id = t.id;
```

---

### 3.3 Transaction Optimization

#### Batch Inserts in Single Transaction
**Bad (slow - 1 transaction per insert):**
```sql
INSERT INTO orders VALUES (...);
INSERT INTO orders VALUES (...);
INSERT INTO orders VALUES (...);
```

**Good (fast - 1 transaction for all):**
```sql
BEGIN TRANSACTION;
INSERT INTO orders VALUES (...);
INSERT INTO orders VALUES (...);
INSERT INTO orders VALUES (...);
COMMIT;
```

#### Use Prepared Statements
```python
# Python example
conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# Prepared statement (compiled once, executed many times)
cursor.execute('BEGIN TRANSACTION')
for order in orders:
    cursor.execute('INSERT INTO orders VALUES (?, ?, ?)', order)
cursor.execute('COMMIT')
```

---

## 4. SQLite Configuration Tuning

### 4.1 Pragma Settings (Connection-Level)

#### Journal Mode (Persistence vs Performance)
```sql
-- Default: DELETE (slow, safe)
PRAGMA journal_mode = DELETE;

-- WAL mode (fast, concurrent reads, recommended)
PRAGMA journal_mode = WAL;

-- MEMORY (fastest, not durable - testing only)
PRAGMA journal_mode = MEMORY;
```

**Recommendation:** Use WAL for production (much faster writes, concurrent reads).

#### Synchronous Mode (Durability vs Speed)
```sql
-- FULL: Safest (fsync after every write) - slowest
PRAGMA synchronous = FULL;

-- NORMAL: Safe for WAL mode (fsync at checkpoints) - recommended
PRAGMA synchronous = NORMAL;

-- OFF: Fastest, but risk of corruption on crash - avoid
PRAGMA synchronous = OFF;
```

**Recommendation:** Use NORMAL with WAL mode.

#### Cache Size (Memory for Pages)
```sql
-- Default: -2000 (2 MB)
-- Set to larger value for better performance

-- 10 MB cache (in KB, negative = KB)
PRAGMA cache_size = -10000;

-- Or in pages (positive = pages, default page size 4KB)
PRAGMA cache_size = 5000;  -- 20 MB
```

**Recommendation:** Set to 5-10% of database size, min 10 MB.

#### Page Size (Database File Structure)
```sql
-- Must be set BEFORE creating tables (cannot change after)
-- Default: 4096 bytes

-- Larger page size for analytical queries
PRAGMA page_size = 8192;

-- Create first table to apply page size
CREATE TABLE ...
```

**Recommendation:** Use 4096 (default) for OLTP, 8192-16384 for analytics.

#### Temp Store (Temporary Tables Storage)
```sql
-- Default: FILE (temp tables on disk)
PRAGMA temp_store = FILE;

-- MEMORY (temp tables in RAM - faster)
PRAGMA temp_store = MEMORY;
```

**Recommendation:** Use MEMORY for faster sorting/joins.

#### Memory-Mapped I/O (3.7.17+)
```sql
-- Enable memory-mapped I/O for faster reads
-- Size in bytes (e.g., 256 MB)
PRAGMA mmap_size = 268435456;
```

**Recommendation:** Use 256 MB for databases < 1 GB.

---

### 4.2 Optimal Configuration for Mobile Apps

```sql
-- Apply at connection open
PRAGMA journal_mode = WAL;
PRAGMA synchronous = NORMAL;
PRAGMA cache_size = -10000;  -- 10 MB
PRAGMA temp_store = MEMORY;
PRAGMA mmap_size = 268435456;  -- 256 MB
```

### 4.3 Optimal Configuration for Desktop Apps

```sql
-- Apply at connection open
PRAGMA journal_mode = WAL;
PRAGMA synchronous = NORMAL;
PRAGMA cache_size = -50000;  -- 50 MB
PRAGMA temp_store = MEMORY;
PRAGMA mmap_size = 1073741824;  -- 1 GB
```

---

## 5. Monitoring and Analysis

### 5.1 Check Current Settings
```sql
PRAGMA journal_mode;
PRAGMA synchronous;
PRAGMA cache_size;
PRAGMA page_size;
PRAGMA temp_store;
```

### 5.2 Analyze Database
```sql
-- Update query planner statistics
ANALYZE;

-- Check table info
PRAGMA table_info(orders);

-- Check indexes
PRAGMA index_list(orders);

-- Check index columns
PRAGMA index_info(idx_orders_customer_id);
```

### 5.3 Database Integrity
```sql
-- Check for corruption
PRAGMA integrity_check;

-- Quick check (faster)
PRAGMA quick_check;
```

### 5.4 Database Size
```sql
-- Page count
PRAGMA page_count;

-- Database size in pages
SELECT page_count * page_size / 1024 / 1024 AS size_mb
FROM (SELECT * FROM pragma_page_count), (SELECT * FROM pragma_page_size);
```

---

## 6. Complete Example

### Scenario: Slow order history in mobile app

**Query:**
```sql
SELECT order_id, order_date, total
FROM orders
WHERE customer_id = 12345
ORDER BY order_date DESC
LIMIT 20;
```

**Current Performance:**
- 450 ms execution time
- Full table scan (500,000 rows)
- No indexes

**EXPLAIN QUERY PLAN:**
```
SCAN TABLE orders
USE TEMP B-TREE FOR ORDER BY
```

**Issues:**
- [x] Full table scan (SCAN TABLE)
- [x] Temporary B-tree for sorting

**Optimizations Applied:**

**1. Create index:**
```sql
CREATE INDEX idx_orders_customer_date
ON orders(customer_id, order_date DESC);
```

**2. Apply configuration:**
```sql
PRAGMA journal_mode = WAL;
PRAGMA synchronous = NORMAL;
PRAGMA cache_size = -10000;
```

**After Optimization:**
```
SEARCH TABLE orders USING INDEX idx_orders_customer_date (customer_id=?)
```

**Results:**
- Execution time: 450 ms -> 8 ms (98.2% improvement)
- Index seek instead of full scan
- Sorting eliminated (index provides order)

---

## 7. SQLite Best Practices

### Do's
- [OK] Use WAL mode for production
- [OK] Batch writes in transactions
- [OK] Use prepared statements
- [OK] Create indexes on WHERE/JOIN columns
- [OK] Run ANALYZE after bulk data changes
- [OK] Use covering indexes for SELECT columns
- [OK] Set appropriate cache_size

### Don'ts
- [FAIL] Don't use synchronous=OFF (risks corruption)
- [FAIL] Don't forget BEGIN/COMMIT for bulk inserts
- [FAIL] Don't use functions on indexed columns
- [FAIL] Don't use OFFSET for deep pagination (use keyset instead)
- [FAIL] Don't create too many indexes (slows writes)
- [FAIL] Don't ignore EXPLAIN QUERY PLAN warnings

---

## 8. Mobile-Specific Considerations

### iOS (Swift/Objective-C)
```swift
// Open connection with optimal settings
let db = try Connection("app.db")
try db.execute("PRAGMA journal_mode = WAL")
try db.execute("PRAGMA synchronous = NORMAL")
try db.execute("PRAGMA cache_size = -10000")
```

### Android (Kotlin/Java)
```kotlin
// SQLiteOpenHelper with optimal settings
override fun onConfigure(db: SQLiteDatabase) {
    db.execSQL("PRAGMA journal_mode = WAL")
    db.execSQL("PRAGMA synchronous = NORMAL")
    db.execSQL("PRAGMA cache_size = -10000")
}
```

### React Native (expo-sqlite)
```javascript
// Apply settings on connection
db.transaction(tx => {
  tx.executeSql('PRAGMA journal_mode = WAL');
  tx.executeSql('PRAGMA synchronous = NORMAL');
  tx.executeSql('PRAGMA cache_size = -10000');
});
```

---

## 9. Quality Checklist

- [ ] EXPLAIN QUERY PLAN shows index usage (not full scan)
- [ ] WAL mode enabled
- [ ] Appropriate cache_size set
- [ ] Indexes created for WHERE/JOIN columns
- [ ] Bulk operations use transactions
- [ ] ANALYZE run after schema/data changes
- [ ] Query execution time acceptable (< 100ms for mobile)
- [ ] No TEMP B-TREE for ORDER BY (use index)

```
