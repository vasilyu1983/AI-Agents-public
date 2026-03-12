```markdown
# Oracle Database Execution Plan Analysis Template

*Purpose: Standardize the process for capturing, analyzing, and optimizing Oracle SQL execution plans using EXPLAIN PLAN and DBMS_XPLAN.*

---

## When to Use

Use this template for:
- Diagnosing slow queries in Oracle Database
- Analyzing execution plans for SQL tuning
- Reviewing optimizer decisions
- Troubleshooting performance issues

---

## Structure

1. **Query & Context**
2. **Execution Plan Capture**
3. **Plan Analysis Checklist**
4. **Action Items & Validation**

---

# TEMPLATE STARTS HERE

## 1. Query & Context

- **Query:**
  [Paste SQL statement being reviewed]

- **Database:**
  [Database name, Oracle version, environment]

- **Schema/Tables:**
  [e.g., SALES.ORDERS, SALES.CUSTOMERS]

- **Expected Result Size:**
  [Rows, typical use-case]

- **Current Performance:**
  - Execution time: [seconds/minutes]
  - Buffer gets: [logical reads]

---

## 2. Execution Plan Capture

### Method 1: EXPLAIN PLAN (Estimated Plan)

```sql
EXPLAIN PLAN FOR
SELECT * FROM orders WHERE customer_id = 12345;

-- View the plan
SELECT * FROM TABLE(DBMS_XPLAN.DISPLAY);
```

### Method 2: Actual Execution Plan (with statistics)

```sql
-- Enable gathering of actual execution statistics
ALTER SESSION SET STATISTICS_LEVEL = ALL;

-- Run your query
SELECT * FROM orders WHERE customer_id = 12345;

-- Display actual plan with runtime statistics
SELECT * FROM TABLE(DBMS_XPLAN.DISPLAY_CURSOR(NULL, NULL, 'ALLSTATS LAST'));
```

### Method 3: Using SQL_ID (from V$SQL)

```sql
-- Find SQL_ID
SELECT sql_id, sql_text, executions, buffer_gets
FROM v$sql
WHERE sql_text LIKE '%customer_id%'
ORDER BY buffer_gets DESC;

-- Display plan for specific SQL_ID
SELECT * FROM TABLE(DBMS_XPLAN.DISPLAY_CURSOR('&sql_id', NULL, 'ALLSTATS LAST'));
```

### Method 4: AWR/Statspack Historical Plan

```sql
-- Display plan from AWR
SELECT * FROM TABLE(DBMS_XPLAN.DISPLAY_AWR('&sql_id'));
```

---

## 3. Execution Plan Analysis Checklist

### 3.1 Access Methods

- [ ] **TABLE ACCESS FULL** - Full table scan
  - Is the table small enough to justify full scan?
  - Should an index be used instead?

- [ ] **TABLE ACCESS BY INDEX ROWID** - Index seek + table access
  - Good for selective queries
  - Check cardinality (rows returned)

- [ ] **INDEX RANGE SCAN** - Scanning range of index
  - Good for range queries (BETWEEN, >, <)

- [ ] **INDEX UNIQUE SCAN** - Single row via unique index
  - Optimal for equality on unique column

- [ ] **INDEX FULL SCAN** - Reading entire index
  - May indicate missing better index
  - Can be useful if index is covering

- [ ] **INDEX FAST FULL SCAN** - Parallel index scan
  - Used when index contains all needed columns

### 3.2 Join Methods

- [ ] **NESTED LOOPS** - Good for small result sets with indexes
  - Driving table should be smaller
  - Joining column should be indexed

- [ ] **HASH JOIN** - Good for large unsorted tables
  - Requires memory for hash table
  - Check PGA memory allocation

- [ ] **SORT MERGE JOIN** - Good for pre-sorted data
  - Can be expensive if sorts required
  - Check for disk sorts (temp tablespace)

### 3.3 Cost and Cardinality

- [ ] Are estimated rows close to actual rows (E-Rows vs A-Rows)?
  - Large discrepancies indicate stale statistics
- [ ] Is the cost reasonable for the operation?
- [ ] Are there high-cost operations that could be optimized?

### 3.4 Predicates

- [ ] **Access predicates** - Used to seek into index
- [ ] **Filter predicates** - Applied after rows retrieved
  - Ideally, filters should be access predicates

### 3.5 Operations to Watch For

- [ ] **SORT ORDER BY** - Can be expensive for large result sets
- [ ] **SORT GROUP BY** - Consider using GROUP BY HASH if available
- [ ] **SORT UNIQUE** - For DISTINCT operations
- [ ] **HASH GROUP BY** - Preferred over SORT GROUP BY
- [ ] **VIEW** - Inline views or subqueries (check pushdown)
- [ ] **FILTER** - Row-by-row filtering (can be slow)

---

## 4. Common Oracle Performance Issues

### Issue 1: Full Table Scan on Large Table

**Symptom:** TABLE ACCESS FULL with high cost

**Check statistics:**
```sql
SELECT table_name, num_rows, last_analyzed
FROM user_tables
WHERE table_name = 'ORDERS';
```

**Gather statistics if stale:**
```sql
EXEC DBMS_STATS.GATHER_TABLE_STATS(
    ownname => 'SCHEMA_NAME',
    tabname => 'ORDERS',
    estimate_percent => DBMS_STATS.AUTO_SAMPLE_SIZE,
    method_opt => 'FOR ALL COLUMNS SIZE AUTO'
);
```

**Consider adding index:**
```sql
CREATE INDEX idx_orders_customer_id ON orders(customer_id);
```

---

### Issue 2: Cardinality Misestimation

**Symptom:** E-Rows (estimated) very different from A-Rows (actual)

**Causes:**
- Stale statistics
- Missing histograms for skewed data
- Bind variable peeking issues

**Fix: Gather extended statistics for correlated columns:**
```sql
-- Create column group for correlated columns
SELECT DBMS_STATS.CREATE_EXTENDED_STATS(
    ownname => 'SCHEMA_NAME',
    tabname => 'ORDERS',
    extension => '(customer_id, order_date)'
) FROM DUAL;

-- Gather statistics
EXEC DBMS_STATS.GATHER_TABLE_STATS(
    ownname => 'SCHEMA_NAME',
    tabname => 'ORDERS'
);
```

---

### Issue 3: Bind Variable Peeking

**Symptom:** Query fast with some parameter values, slow with others

**Fix: Use adaptive cursor sharing (11g+) or:**
```sql
-- Use hints to avoid peeking
SELECT /*+ BIND_AWARE */ * FROM orders WHERE customer_id = :cust_id;

-- Or use literals for dynamic sampling
SELECT /*+ DYNAMIC_SAMPLING(4) */ * FROM orders WHERE customer_id = 12345;
```

---

### Issue 4: Wrong Join Order

**Symptom:** Large table driving nested loop join

**Check join order:**
- Smaller table should drive the join in nested loops
- Use ORDERED hint to force specific join order (testing only)

**Fix with hints:**
```sql
SELECT /*+ LEADING(small_table large_table) USE_NL(large_table) */
    ...
FROM small_table, large_table
WHERE small_table.id = large_table.id;
```

---

### Issue 5: Index Not Being Used

**Reasons:**
- Function on indexed column (e.g., `WHERE UPPER(name) = 'SMITH'`)
- Implicit type conversion
- Statistics out of date
- Cost-based optimizer choosing full scan

**Check index usage:**
```sql
SELECT index_name, column_name, column_position
FROM user_ind_columns
WHERE table_name = 'ORDERS'
ORDER BY index_name, column_position;
```

**Fix: Create function-based index if needed:**
```sql
CREATE INDEX idx_customers_upper_name
ON customers(UPPER(last_name));
```

---

## 5. Action Items & Validation

### 5.1 Optimization Steps Proposed

**Example Actions:**
1. Gather statistics on ORDERS table
2. Create index on (customer_id, order_date)
3. Update SQL to avoid function on indexed column

**DDL:**
```sql
-- Gather statistics
EXEC DBMS_STATS.GATHER_TABLE_STATS('SCHEMA', 'ORDERS');

-- Create index
CREATE INDEX idx_orders_cust_date
ON orders(customer_id, order_date);
```

### 5.2 Execution Plan After Optimization

[Paste updated plan]

**Key Improvements:**
- TABLE ACCESS FULL -> INDEX RANGE SCAN
- Cost reduced from 5000 to 10
- Buffer gets reduced from 500,000 to 25

### 5.3 Performance Before/After

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| Execution time (sec) | | | |
| Buffer gets (logical I/O) | | | |
| Physical reads | | | |
| CPU time (sec) | | | |
| Rows processed | | | |

### 5.4 Rollback Plan

```sql
-- Drop index if needed
DROP INDEX idx_orders_cust_date;

-- Restore old statistics (if backed up)
EXEC DBMS_STATS.RESTORE_TABLE_STATS('SCHEMA', 'ORDERS', '&timestamp');
```

---

## 6. Complete Example

### Problem: Slow order lookup by customer

**Query:**
```sql
SELECT order_id, order_date, order_total
FROM orders
WHERE customer_id = 12345
ORDER BY order_date DESC;
```

**Current Plan:**
```
---------------------------------------------------------------------------
| Id | Operation          | Name   | Rows | Bytes | Cost (%CPU)| Time     |
---------------------------------------------------------------------------
|  0 | SELECT STATEMENT   |        |   50 |  2000 |  1234  (1)| 00:00:15 |
|  1 |  SORT ORDER BY     |        |   50 |  2000 |  1234  (1)| 00:00:15 |
|* 2 |   TABLE ACCESS FULL| ORDERS | 50   |  2000 |  1233  (1)| 00:00:15 |
---------------------------------------------------------------------------

Predicate Information (identified by operation id):
   2 - filter("CUSTOMER_ID"=12345)
```

**Issues:**
- [x] Full table scan (500,000 rows scanned for 50 returned)
- [x] Sort operation (expensive)
- [x] 500,000 buffer gets

**Fix:**
```sql
CREATE INDEX idx_orders_customer_date
ON orders(customer_id, order_date DESC);

-- Gather statistics
EXEC DBMS_STATS.GATHER_INDEX_STATS('SCHEMA', 'IDX_ORDERS_CUSTOMER_DATE');
```

**Optimized Plan:**
```
-----------------------------------------------------------------------------------
| Id | Operation                    | Name                   | Rows | Bytes | Cost |
-----------------------------------------------------------------------------------
|  0 | SELECT STATEMENT             |                        |   50 |  2000 |    3 |
|  1 |  TABLE ACCESS BY INDEX ROWID | ORDERS                 |   50 |  2000 |    3 |
|* 2 |   INDEX RANGE SCAN DESCENDING| IDX_ORDERS_CUSTOMER_DATE|   50 |       |    2 |
-----------------------------------------------------------------------------------

Predicate Information (identified by operation id):
   2 - access("CUSTOMER_ID"=12345)
```

**Results:**
- Execution time: 2.5s -> 0.02s (99.2% improvement)
- Buffer gets: 500,000 -> 15 (99.997% improvement)
- Sort eliminated (index provides ordering)

---

## 7. Useful Oracle Queries

### Find Expensive SQL
```sql
SELECT sql_id, executions, buffer_gets, disk_reads,
       elapsed_time/1000000 AS elapsed_seconds,
       SUBSTR(sql_text, 1, 100) AS sql_text
FROM v$sql
WHERE executions > 0
ORDER BY buffer_gets DESC
FETCH FIRST 20 ROWS ONLY;
```

### Check Table Statistics
```sql
SELECT table_name, num_rows, blocks, last_analyzed
FROM user_tables
WHERE table_name IN ('ORDERS', 'CUSTOMERS')
ORDER BY table_name;
```

### Check Index Statistics
```sql
SELECT index_name, blevel, leaf_blocks, distinct_keys, num_rows, last_analyzed
FROM user_indexes
WHERE table_name = 'ORDERS';
```

---

## 8. Quality Checklist

- [ ] Execution plan captured (estimated and actual)
- [ ] Statistics are up to date (< 1 week old for active tables)
- [ ] Access methods are optimal (index seeks vs full scans)
- [ ] Join methods appropriate for data volume
- [ ] Cardinality estimates are accurate
- [ ] Predicates optimized (access vs filter)
- [ ] Performance improvement validated
- [ ] Rollback plan documented

```
