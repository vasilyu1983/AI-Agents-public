```markdown
# SQL Server Execution Plan Analysis Template

*Purpose: Standardize the process for capturing, analyzing, and optimizing SQL Server query execution plans using SET STATISTICS and execution plan XML.*

---

## When to Use

Use this template for:
- Diagnosing slow queries in SQL Server
- Reviewing execution plans before/after index changes
- Analyzing T-SQL stored procedures or ad-hoc queries
- Performance tuning for production workloads

---

## Structure

This template includes:
1. **Query & Context**
2. **Execution Plan Capture**
3. **Plan Analysis Checklist**
4. **Action Items & Validation**

---

# TEMPLATE STARTS HERE

## 1. Query & Context

- **Query:**
  [Paste T-SQL statement being reviewed]

- **Database:**
  [Database name, SQL Server version, environment]

- **Table(s) Involved:**
  [e.g., Orders, Customers, OrderDetails]

- **Expected Result Size:**
  [Rows, typical use-case]

- **Query Type:**
  - [ ] Ad-hoc query
  - [ ] Stored procedure
  - [ ] View
  - [ ] Function
  - [ ] Trigger

---

## 2. Execution Plan Capture

### Method 1: Graphical Execution Plan (SSMS)
```sql
-- Enable actual execution plan in SSMS (Ctrl+M)
-- Or use:
SET STATISTICS XML ON;
[Your SQL query here]
SET STATISTICS XML OFF;
```

### Method 2: Text Statistics
```sql
SET STATISTICS IO ON;
SET STATISTICS TIME ON;

[Your SQL query here]

SET STATISTICS IO OFF;
SET STATISTICS TIME OFF;
```

### Method 3: Query Store (SQL Server 2016+)
```sql
-- Query from Query Store
SELECT
    q.query_id,
    qt.query_sql_text,
    rs.avg_duration/1000 AS avg_duration_ms,
    rs.avg_logical_io_reads,
    rs.avg_physical_io_reads
FROM sys.query_store_query q
JOIN sys.query_store_query_text qt ON q.query_text_id = qt.query_text_id
JOIN sys.query_store_plan p ON q.query_id = p.query_id
JOIN sys.query_store_runtime_stats rs ON p.plan_id = rs.plan_id
WHERE qt.query_sql_text LIKE '%your_pattern%'
ORDER BY rs.avg_duration DESC;
```

---

## 3. Execution Plan Analysis Checklist

### 3.1 Scan Operations
- [ ] Is there a **Table Scan** on a large table?
  - [ ] Should an index be used instead?
- [ ] Is **Index Scan** being used where **Index Seek** would be better?
- [ ] Are **Clustered Index Scans** appearing on large tables?

### 3.2 Join Operations
- [ ] **Nested Loop Join** - Good for small result sets with indexes
- [ ] **Hash Join** - Good for large unsorted tables
- [ ] **Merge Join** - Good for pre-sorted or indexed data
- [ ] Are join predicates using indexed columns?
- [ ] Are there implicit conversions causing index scans?

### 3.3 Key Lookups (RID/Key Lookup)
- [ ] Are there **Key Lookup** operations?
  - High cost lookups indicate missing covering indexes
- [ ] Consider adding included columns to index

### 3.4 Sorts and Spills
- [ ] Are there **Sort** operators with high cost?
- [ ] Are sorts spilling to tempdb? (Check STATISTICS IO)
- [ ] Can sorting be eliminated with an index?

### 3.5 Warnings and Issues
- [ ] **Missing Index** recommendations in plan?
- [ ] **Implicit conversions** (data type mismatches)?
- [ ] **Parameter sniffing** issues?
- [ ] **Statistics out of date**?
- [ ] **Parallelism** issues (CXPACKET waits)?

### 3.6 I/O Statistics
- [ ] **Logical reads** - pages read from buffer cache
- [ ] **Physical reads** - pages read from disk
- [ ] **Read-ahead reads** - large scans
- [ ] High logical reads indicate missing indexes

---

## 4. SQL Server 2025 Query Optimization Features

### Optional Parameter Plan Optimization (OPPO)

Addresses parameter sniffing issues automatically by choosing optimal plans based on runtime parameters:

```sql
-- Enable OPPO at database level
ALTER DATABASE SCOPED CONFIGURATION SET PARAMETER_SENSITIVE_PLAN_OPTIMIZATION = ON;

-- Check if OPPO is active for a query
SELECT
    qsp.plan_id,
    qsp.is_plan_guide_plan,
    qsq.query_id
FROM sys.query_store_plan qsp
JOIN sys.query_store_query qsq ON qsp.query_id = qsq.query_id
WHERE qsp.plan_type = 2; -- Parameter sensitive plan
```

### Cardinality Estimation Feedback for Expressions

The engine learns from previous executions to improve row estimates:

- Automatically adjusts cardinality for calculated columns
- Learns from implicit conversions
- No manual intervention required

### Optimized Locking (TID + LAQ)

Reduces lock contention in high-concurrency environments:

```sql
-- Enable optimized locking
ALTER DATABASE YourDatabase SET OPTIMIZED_LOCKING = ON;

-- Verify optimized locking is active
SELECT name, is_optimized_locking_on
FROM sys.databases
WHERE name = 'YourDatabase';
```

**Benefits:**

- Transaction ID (TID) locking reduces lock memory consumption
- Lock After Qualification (LAQ) delays locks until predicates evaluated
- Lower `LCK_M_IX` wait times in benchmarks

### TempDB Resource Governance

Prevent runaway queries from filling tempdb:

```sql
-- Create resource pool with tempdb limit
CREATE RESOURCE POOL TempDBLimitedPool
WITH (
    MAX_TEMPDB_PERCENT = 25  -- 25% of tempdb max
);

-- Assign workload group to pool
CREATE WORKLOAD GROUP LimitedGroup
USING TempDBLimitedPool;

-- Classify sessions to workload group
CREATE FUNCTION dbo.TempDBClassifier()
RETURNS sysname
WITH SCHEMABINDING
AS
BEGIN
    IF APP_NAME() LIKE '%ReportingApp%'
        RETURN 'LimitedGroup';
    RETURN 'default';
END;
```

### Optimized sp_executesql

Reduces compilation storms for large dynamic SQL:

- Better caching of parameterized queries
- Lower CPU contention during parallel compilations

### Query Store on Readable Secondaries

Query Store now runs on readable replicas by default:

- Performance history preserved during failovers
- Better tuning of read-only workloads

```sql
-- Verify Query Store on secondary
SELECT actual_state_desc, readonly_reason
FROM sys.database_query_store_options;
```

---

## 5. Common SQL Server Performance Issues

### Issue 1: Missing Index
**Symptom:** Table/Index Scan + Missing Index warning in plan

**Fix:**
```sql
-- Check missing index DMV
SELECT
    OBJECT_NAME(d.object_id) AS table_name,
    d.equality_columns,
    d.inequality_columns,
    d.included_columns,
    s.avg_user_impact,
    s.user_seeks
FROM sys.dm_db_missing_index_details d
JOIN sys.dm_db_missing_index_groups g ON d.index_handle = g.index_handle
JOIN sys.dm_db_missing_index_group_stats s ON g.index_group_handle = s.group_handle
WHERE d.database_id = DB_ID()
ORDER BY s.avg_user_impact * s.user_seeks DESC;
```

### Issue 2: Key Lookup
**Symptom:** Index Seek + Key Lookup (expensive)

**Fix:** Create covering index
```sql
CREATE NONCLUSTERED INDEX IX_TableName_Covering
ON TableName (FilterColumn)
INCLUDE (Column1, Column2, Column3);
```

### Issue 3: Parameter Sniffing
**Symptom:** Query fast with some parameters, slow with others

**Fix Options:**
```sql
-- Option 1: OPTIMIZE FOR hint
SELECT * FROM Orders
WHERE CustomerId = @CustomerId
OPTION (OPTIMIZE FOR (@CustomerId = 123));

-- Option 2: RECOMPILE
SELECT * FROM Orders
WHERE CustomerId = @CustomerId
OPTION (RECOMPILE);

-- Option 3: Local variable
DECLARE @LocalCustomerId INT = @CustomerId;
SELECT * FROM Orders WHERE CustomerId = @LocalCustomerId;
```

### Issue 4: Implicit Conversion
**Symptom:** CONVERT_IMPLICIT in execution plan, index not used

**Fix:** Ensure data type match
```sql
-- Bad: CustomerId (INT) compared to VARCHAR
WHERE CustomerId = '123'

-- Good: Use correct data type
WHERE CustomerId = 123
```

### Issue 5: Statistics Out of Date
**Symptom:** Estimated rows << Actual rows in plan

**Fix:**
```sql
-- Update statistics
UPDATE STATISTICS TableName WITH FULLSCAN;

-- Check statistics age
SELECT
    OBJECT_NAME(s.object_id) AS table_name,
    s.name AS stats_name,
    STATS_DATE(s.object_id, s.stats_id) AS last_updated
FROM sys.stats s
WHERE OBJECT_NAME(s.object_id) = 'YourTableName';
```

---

## 6. Action Items & Validation

### 5.1 Optimization Steps Proposed
[List specific changes: index creation, query rewrite, statistics update, etc.]

**Example:**
```sql
-- Create missing index
CREATE NONCLUSTERED INDEX IX_Orders_CustomerId_OrderDate
ON Orders (CustomerId, OrderDate DESC)
INCLUDE (OrderTotal);

-- Update statistics
UPDATE STATISTICS Orders WITH FULLSCAN;
```

### 5.2 Execution Plan After Optimization
[Paste updated plan or screenshot]

**Changes:**
- Table Scan -> Index Seek
- Key Lookup eliminated
- Sort removed (index provides ordering)

### 5.3 Performance Before/After

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| Duration (ms) | | | |
| Logical reads | | | |
| Physical reads | | | |
| CPU time (ms) | | | |

### 5.4 Rollback Plan
[How to revert changes if needed]

**Example:**
```sql
DROP INDEX IX_Orders_CustomerId_OrderDate ON Orders;
```

---

## 7. Complete Example

### Problem: Slow customer order history query

**Query:**
```sql
SELECT o.OrderId, o.OrderDate, o.OrderTotal
FROM Orders o
WHERE o.CustomerId = 12345
ORDER BY o.OrderDate DESC;
```

**Issues Found:**
- [x] Clustered Index Scan (no non-clustered index on CustomerId)
- [x] Sort operation (expensive)
- [x] 1.2M logical reads for 10 rows returned

**Execution Plan Analysis:**
```
Clustered Index Scan (Cost: 95%)
  ├─ Rows: 10 (Estimated: 50000)
  ├─ Logical Reads: 1,200,000
  └─ Sort (Cost: 5%)
```

**Fix Applied:**
```sql
CREATE NONCLUSTERED INDEX IX_Orders_CustomerId_OrderDate
ON Orders (CustomerId, OrderDate DESC)
INCLUDE (OrderTotal);
```

**After Optimization:**
```
Index Seek (Cost: 100%)
  ├─ Rows: 10 (Estimated: 10)
  ├─ Logical Reads: 15
  └─ Sort: Eliminated (index provides ordering)
```

**Results:**
- Duration: 1,850 ms -> 3 ms (99.8% improvement)
- Logical reads: 1,200,000 -> 15 (99.999% improvement)
- Sort eliminated

---

## 8. Quality Checklist

Before finalizing:

- [ ] Execution plan captured (XML or graphical)
- [ ] Statistics IO/TIME reviewed
- [ ] Index or query rewrite tested in non-prod
- [ ] Performance improvement validated
- [ ] Rollback steps documented
- [ ] Query Store monitoring enabled (if available)
- [ ] No negative impact on other queries verified

---

## 9. Useful DMV Queries

### Most Expensive Queries
```sql
SELECT TOP 10
    qs.execution_count,
    qs.total_elapsed_time / 1000 AS total_elapsed_time_ms,
    qs.total_logical_reads,
    SUBSTRING(qt.text, (qs.statement_start_offset/2)+1,
        ((CASE qs.statement_end_offset
            WHEN -1 THEN DATALENGTH(qt.text)
            ELSE qs.statement_end_offset
        END - qs.statement_start_offset)/2) + 1) AS query_text
FROM sys.dm_exec_query_stats qs
CROSS APPLY sys.dm_exec_sql_text(qs.sql_handle) qt
ORDER BY qs.total_elapsed_time DESC;
```

### Index Usage Statistics
```sql
SELECT
    OBJECT_NAME(s.object_id) AS table_name,
    i.name AS index_name,
    s.user_seeks,
    s.user_scans,
    s.user_lookups,
    s.user_updates
FROM sys.dm_db_index_usage_stats s
JOIN sys.indexes i ON s.object_id = i.object_id AND s.index_id = i.index_id
WHERE OBJECT_NAME(s.object_id) = 'YourTableName';
```

```
