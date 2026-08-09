```markdown
# DuckDB Analytics Query Optimization Template

*Purpose: Standardize analytical query optimization for DuckDB, focusing on columnar storage, vectorized execution, and parallel query processing.*

---

## When to Use

Use this template for:
- Optimizing analytical queries on large datasets
- Leveraging DuckDB's columnar storage and vectorization
- Improving aggregation and window function performance
- Optimizing data loading and export workflows

---

## Structure

This template includes:
1. **Query & Context**
2. **EXPLAIN Output & Analysis**
3. **DuckDB-Specific Optimizations**
4. **Performance Validation**

---

# TEMPLATE STARTS HERE

## 1. Query & Context

- **Query:**
  [Paste analytical SQL being reviewed]

- **Dataset:**
  - Source: [Parquet, CSV, JSON, etc.]
  - Size: [GB/rows]
  - Format: [file format]

- **Expected Result:**
  [Aggregated metrics, analytical result]

- **Use Case:**
  - [ ] Ad-hoc analysis
  - [ ] Reporting dashboard
  - [ ] Data export
  - [ ] ETL transformation

---

## 2. EXPLAIN Output & Analysis

- **Command Used:**
  ```sql
  EXPLAIN ANALYZE [SQL...]
  ```

- **Plan Output:**
  [Paste execution plan]

### DuckDB Plan Analysis Checklist

- [ ] Is the query using columnar scan (should be default)?
- [ ] Are filters pushed down to file scan level?
- [ ] Is projection pushdown working (reading only needed columns)?
- [ ] Are aggregations using vectorized execution?
- [ ] Is parallelism being utilized (check thread count)?
- [ ] Are joins using hash join (optimal for analytics)?
- [ ] Is there unnecessary materialization?
- [ ] Are window functions partitioned efficiently?

---

## 3. DuckDB-Specific Optimizations

### 3.1 File Format Optimization

**Current Format:**
[CSV / JSON / Parquet / other]

**Recommendation:**
- [ ] Convert to Parquet for columnar storage
- [ ] Use compression (snappy, zstd, gzip)
- [ ] Partition large datasets by key columns
- [ ] Use appropriate row group size

**Example:**
```sql
COPY (SELECT * FROM source_table)
TO 'data.parquet' (FORMAT PARQUET, COMPRESSION ZSTD);
```

---

### 3.2 Projection Pushdown

**Optimization:** Only read needed columns

**Before:**
```sql
SELECT col1, col2 FROM read_parquet('data/*.parquet');
```

**After (already optimized in DuckDB):**
```sql
-- DuckDB automatically pushes projection to file scan
-- Only col1, col2 are read from Parquet
SELECT col1, col2 FROM read_parquet('data/*.parquet');
```

**Validation:**
- [ ] EXPLAIN shows only required columns in PARQUET_SCAN
- [ ] I/O reduced proportionally to column reduction

---

### 3.3 Filter Pushdown

**Optimization:** Push WHERE filters to file scan

**Example:**
```sql
-- DuckDB pushes filters to Parquet metadata
SELECT * FROM read_parquet('sales/*.parquet')
WHERE year = 2024 AND region = 'US';
```

**Checklist:**
- [ ] Filters on partition columns (if partitioned)
- [ ] Filters compatible with Parquet statistics
- [ ] Use equality/range filters (>, <, =, BETWEEN)

---

### 3.4 Parallel Query Execution

**Configuration:**
```sql
-- Check current thread setting
SELECT * FROM duckdb_settings() WHERE name = 'threads';

-- Adjust if needed
SET threads TO 8;
```

**Checklist:**
- [ ] Large aggregations show parallel execution
- [ ] File scans use multiple threads
- [ ] No thread contention (check system metrics)

---

### 3.5 Aggregation Optimization

**Pattern: Group by high-cardinality columns**

**Optimization:**
```sql
-- Use DISTINCT or GROUP BY efficiently
SELECT region, product, SUM(sales)
FROM large_table
GROUP BY region, product;
```

**Checklist:**
- [ ] Use appropriate aggregation functions (SUM, COUNT, AVG)
- [ ] Avoid SELECT DISTINCT on very large result sets
- [ ] Consider approximate aggregations for huge datasets

---

### 3.6 Window Function Optimization

**Pattern: Efficient partitioning**

```sql
-- Ensure PARTITION BY uses low-cardinality columns
SELECT *,
  ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY order_date DESC) AS rn
FROM orders;
```

**Checklist:**
- [ ] PARTITION BY columns have reasonable cardinality
- [ ] ORDER BY uses indexed or sorted data when possible
- [ ] Avoid unnecessary window functions

---

### 3.7 Join Optimization

**DuckDB Join Strategy:**
- Hash join for large-large joins
- Nested loop for small-large joins

**Example:**
```sql
-- Hash join (default for large tables)
SELECT a.*, b.name
FROM large_fact_table a
JOIN dimension_table b ON a.dim_id = b.id;
```

**Checklist:**
- [ ] Smaller table on the right side of join (best practice)
- [ ] Join keys have matching data types
- [ ] Avoid joining on expressions or functions

---

## 4. Performance Validation

### 4.1 Timing Comparison

| Test Case | Before (ms) | After (ms) | Improvement |
|-----------|-------------|------------|-------------|
| Full query | | | |
| File scan only | | | |
| Aggregation | | | |

### 4.2 Resource Usage

- **Memory:**
  - Before: [MB/GB]
  - After: [MB/GB]

- **Disk I/O:**
  - Before: [MB read]
  - After: [MB read]

- **CPU Utilization:**
  - Threads used: [N]
  - Parallelism: [Yes/No]

### 4.3 Query Plan Validation

- [ ] File scan shows column pruning
- [ ] Filters pushed to PARQUET_SCAN
- [ ] Aggregations vectorized
- [ ] Parallel execution visible
- [ ] No unnecessary sorts or materializations

---

## 5. DuckDB-Specific Best Practices

### Data Loading
```sql
-- Fast bulk loading from Parquet
CREATE TABLE target AS
SELECT * FROM read_parquet('source/*.parquet');

-- Append mode for incremental loads
INSERT INTO target
SELECT * FROM read_parquet('new_data/*.parquet');
```

### Using Views for Reusability
```sql
CREATE VIEW monthly_sales AS
SELECT
  DATE_TRUNC('month', order_date) AS month,
  region,
  SUM(amount) AS total_sales
FROM orders
GROUP BY month, region;
```

### Efficient Exports
```sql
-- Export large results to Parquet
COPY (SELECT * FROM analytical_query)
TO 'output.parquet' (FORMAT PARQUET, COMPRESSION ZSTD);

-- CSV export with compression
COPY (SELECT * FROM analytical_query)
TO 'output.csv.gz' (FORMAT CSV, COMPRESSION GZIP);
```

---

## 6. Common DuckDB Anti-Patterns

### BAD: Anti-Pattern: Reading CSV Instead of Parquet
```sql
-- Slow: CSV requires parsing
SELECT * FROM read_csv('data/*.csv');
```

### GOOD: Fix: Use Parquet
```sql
-- Fast: Columnar format with metadata
SELECT * FROM read_parquet('data/*.parquet');
```

---

### BAD: Anti-Pattern: SELECT * on Wide Tables
```sql
-- Reads all columns unnecessarily
SELECT * FROM wide_table WHERE id = 123;
```

### GOOD: Fix: Explicit Column List
```sql
-- Only reads required columns
SELECT id, name, email FROM wide_table WHERE id = 123;
```

---

### BAD: Anti-Pattern: Functions on Columns in WHERE
```sql
-- Prevents filter pushdown
SELECT * FROM data WHERE LOWER(region) = 'us';
```

### GOOD: Fix: Normalize Data or Use Direct Comparison
```sql
-- Filter pushdown works
SELECT * FROM data WHERE region = 'US';
```

---

## 7. Complete Example

### Scenario: Slow Aggregation on 10GB Parquet Dataset

**Before:**
```sql
SELECT customer_id, COUNT(*) AS order_count, SUM(amount) AS total
FROM read_csv('orders/*.csv')
WHERE year = 2024
GROUP BY customer_id;
```

**Issues:**
- CSV format (slow parsing)
- No filter pushdown
- Single-threaded execution

**After:**
```sql
-- Convert to Parquet first (one-time)
COPY (SELECT * FROM read_csv('orders/*.csv'))
TO 'orders.parquet' (FORMAT PARQUET, COMPRESSION ZSTD);

-- Optimized query
SET threads TO 8;

SELECT customer_id, COUNT(*) AS order_count, SUM(amount) AS total
FROM read_parquet('orders.parquet')
WHERE year = 2024
GROUP BY customer_id;
```

**Results:**
- Before: 45 seconds, 2.1 GB read, single-threaded
- After: 3.2 seconds, 420 MB read, 8 threads

**Optimizations Applied:**
- [OK] Parquet format (columnar storage)
- [OK] Compression (ZSTD)
- [OK] Projection pushdown (only needed columns)
- [OK] Filter pushdown (year = 2024)
- [OK] Parallel execution (8 threads)

---

## Quality Checklist

Before finalizing:

- [ ] Query plan shows columnar scan
- [ ] Filters pushed to file scan
- [ ] Only required columns read
- [ ] Parallel execution enabled
- [ ] File format optimized (Parquet preferred)
- [ ] Performance validated with timing
- [ ] Resource usage acceptable

```
