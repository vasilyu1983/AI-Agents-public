```markdown
# SQL Server Index Design Template

*Purpose: Structured template for designing, creating, and maintaining indexes in SQL Server with focus on clustered, non-clustered, columnstore, and filtered indexes.*

---

## When to Use

Use this template for:
- Creating new indexes based on query patterns
- Optimizing existing index strategy
- Resolving missing index recommendations
- Reducing index fragmentation
- Designing covering indexes

---

## Structure

1. **Index Design Decision**
2. **Index Creation**
3. **Validation & Monitoring**
4. **Maintenance Strategy**

---

# TEMPLATE STARTS HERE

## 1. Index Design Decision

### 1.1 Query Pattern Analysis

**Query Pattern:**
[Paste query or describe access pattern]

**Workload Type:**
- [ ] OLTP (frequent small transactions)
- [ ] OLAP (analytical, large scans)
- [ ] Mixed workload

**Query Filters (WHERE clause):**
- Column 1: [e.g., CustomerId]
- Column 2: [e.g., OrderDate]

**Sort/Order By:**
- [ ] None
- [ ] Column(s): [e.g., OrderDate DESC]

**Columns Returned (SELECT):**
- [ ] All columns (SELECT *)
- [ ] Specific columns: [list]

---

### 1.2 Index Type Selection

#### Clustered Index
**Use when:**
- Primary key or unique identifier
- Range queries benefit from physical ordering
- One per table (defines physical storage)

**Default:** Primary key usually gets clustered index automatically

#### Non-Clustered Index
**Use when:**
- Supporting WHERE clause filters
- Supporting JOIN conditions
- Supporting ORDER BY
- Multiple per table allowed

#### Covering Index (with INCLUDE)
**Use when:**
- Query reads only specific columns frequently
- Avoid key lookups (bookmark lookups)
- INCLUDE non-key columns to satisfy SELECT list

#### Filtered Index
**Use when:**
- Query targets subset of rows (e.g., WHERE Status = 'Active')
- Reduces index size and maintenance cost

#### Columnstore Index
**Use when:**
- Analytical queries (large aggregations)
- Data warehouse workloads
- Read-heavy scenarios

---

## 2. Index Creation

### 2.1 Clustered Index

**Standard Clustered Index:**
```sql
CREATE CLUSTERED INDEX IX_TableName_ClusteredColumn
ON dbo.TableName (ColumnName);
```

**Primary Key with Clustered Index:**
```sql
ALTER TABLE dbo.TableName
ADD CONSTRAINT PK_TableName PRIMARY KEY CLUSTERED (Id);
```

---

### 2.2 Non-Clustered Index

**Single Column Index:**
```sql
CREATE NONCLUSTERED INDEX IX_TableName_ColumnName
ON dbo.TableName (ColumnName);
```

**Composite Index:**
```sql
CREATE NONCLUSTERED INDEX IX_TableName_Col1_Col2
ON dbo.TableName (Column1, Column2);
```

**Key Ordering Tips:**
- Most selective column first (for equality filters)
- ORDER BY columns follow WHERE columns
- Example: `(CustomerId, OrderDate DESC)` for `WHERE CustomerId = X ORDER BY OrderDate DESC`

---

### 2.3 Covering Index (with INCLUDE)

**Pattern:**
```sql
CREATE NONCLUSTERED INDEX IX_TableName_Covering
ON dbo.TableName (KeyColumn1, KeyColumn2)
INCLUDE (NonKeyColumn1, NonKeyColumn2, NonKeyColumn3);
```

**Example:**
```sql
-- Query: SELECT CustomerId, OrderDate, OrderTotal FROM Orders WHERE CustomerId = @Id
CREATE NONCLUSTERED INDEX IX_Orders_CustomerId_Covering
ON dbo.Orders (CustomerId)
INCLUDE (OrderDate, OrderTotal);
```

**Benefits:**
- Eliminates key lookups (bookmark lookups)
- All data retrieved from index (no heap/clustered index access)

---

### 2.4 Filtered Index

**Pattern:**
```sql
CREATE NONCLUSTERED INDEX IX_TableName_Filtered
ON dbo.TableName (ColumnName)
WHERE FilterCondition;
```

**Example:**
```sql
-- Only index active customers
CREATE NONCLUSTERED INDEX IX_Customers_Active
ON dbo.Customers (CustomerId)
WHERE Status = 'Active';
```

**Use Cases:**
- Sparse columns (many NULLs)
- Status-based filtering (Active/Inactive)
- Date ranges (recent data only)

---

### 2.5 Columnstore Index

**Clustered Columnstore (entire table):**
```sql
CREATE CLUSTERED COLUMNSTORE INDEX CCI_TableName
ON dbo.TableName;
```

**Non-Clustered Columnstore (subset):**
```sql
CREATE NONCLUSTERED COLUMNSTORE INDEX NCCI_TableName
ON dbo.TableName (Column1, Column2, Column3);
```

**Use Cases:**
- Data warehouse fact tables
- Large aggregations (SUM, AVG, COUNT)
- Analytical queries

---

### 2.6 Online Index Creation (Enterprise Edition)

**Create index without blocking:**
```sql
CREATE NONCLUSTERED INDEX IX_TableName_ColumnName
ON dbo.TableName (ColumnName)
WITH (ONLINE = ON);
```

**Rebuild index online:**
```sql
ALTER INDEX IX_TableName_ColumnName ON dbo.TableName
REBUILD WITH (ONLINE = ON);
```

---

## 3. Validation & Monitoring

### 3.1 Verify Index Usage

**Check if index is being used:**
```sql
SELECT
    OBJECT_NAME(s.object_id) AS table_name,
    i.name AS index_name,
    i.type_desc,
    s.user_seeks,
    s.user_scans,
    s.user_lookups,
    s.user_updates,
    s.last_user_seek,
    s.last_user_scan
FROM sys.dm_db_index_usage_stats s
JOIN sys.indexes i ON s.object_id = i.object_id AND s.index_id = i.index_id
WHERE s.database_id = DB_ID()
  AND OBJECT_NAME(s.object_id) = 'YourTableName'
ORDER BY s.user_seeks + s.user_scans + s.user_lookups DESC;
```

### 3.2 Check Execution Plan

**Run query with execution plan:**
```sql
SET STATISTICS IO ON;
SET STATISTICS TIME ON;

-- Your query here

SET STATISTICS IO OFF;
SET STATISTICS TIME OFF;
```

**Verify:**
- [ ] Index Seek (not Index Scan or Table Scan)
- [ ] Low logical reads
- [ ] No Key Lookup warnings

### 3.3 Index Fragmentation

**Check fragmentation:**
```sql
SELECT
    OBJECT_NAME(ips.object_id) AS table_name,
    i.name AS index_name,
    ips.index_type_desc,
    ips.avg_fragmentation_in_percent,
    ips.page_count
FROM sys.dm_db_index_physical_stats(DB_ID(), NULL, NULL, NULL, 'LIMITED') ips
JOIN sys.indexes i ON ips.object_id = i.object_id AND ips.index_id = i.index_id
WHERE ips.avg_fragmentation_in_percent > 10
  AND ips.page_count > 1000
ORDER BY ips.avg_fragmentation_in_percent DESC;
```

**Fragmentation thresholds:**
- < 10%: No action needed
- 10-30%: REORGANIZE
- > 30%: REBUILD

---

## 4. Index Maintenance

### 4.1 Reorganize Index (< 30% fragmentation)

```sql
ALTER INDEX IX_TableName_ColumnName
ON dbo.TableName
REORGANIZE;
```

### 4.2 Rebuild Index (> 30% fragmentation)

**Offline rebuild:**
```sql
ALTER INDEX IX_TableName_ColumnName
ON dbo.TableName
REBUILD;
```

**Online rebuild (Enterprise Edition):**
```sql
ALTER INDEX IX_TableName_ColumnName
ON dbo.TableName
REBUILD WITH (ONLINE = ON);
```

**Rebuild all indexes on a table:**
```sql
ALTER INDEX ALL ON dbo.TableName REBUILD;
```

### 4.3 Update Statistics

```sql
UPDATE STATISTICS dbo.TableName WITH FULLSCAN;
```

### 4.4 Drop Unused Indexes

**Find unused indexes:**
```sql
SELECT
    OBJECT_NAME(i.object_id) AS table_name,
    i.name AS index_name,
    i.type_desc,
    s.user_seeks,
    s.user_scans,
    s.user_lookups,
    s.user_updates
FROM sys.indexes i
LEFT JOIN sys.dm_db_index_usage_stats s
    ON i.object_id = s.object_id AND i.index_id = s.index_id
WHERE i.is_primary_key = 0
  AND i.is_unique_constraint = 0
  AND OBJECTPROPERTY(i.object_id, 'IsUserTable') = 1
  AND (s.user_seeks = 0 OR s.user_seeks IS NULL)
  AND (s.user_scans = 0 OR s.user_scans IS NULL)
  AND (s.user_lookups = 0 OR s.user_lookups IS NULL)
  AND s.user_updates > 0
ORDER BY s.user_updates DESC;
```

**Drop unused index:**
```sql
DROP INDEX IX_TableName_UnusedIndex ON dbo.TableName;
```

---

## 5. Common Index Patterns

### Pattern 1: Lookups by ID
```sql
-- Query: SELECT * FROM Orders WHERE OrderId = @Id
CREATE NONCLUSTERED INDEX IX_Orders_OrderId
ON dbo.Orders (OrderId);
```

### Pattern 2: Foreign Key Joins
```sql
-- Query: JOIN Orders ON Orders.CustomerId = Customers.CustomerId
CREATE NONCLUSTERED INDEX IX_Orders_CustomerId
ON dbo.Orders (CustomerId);
```

### Pattern 3: Range Queries with Sort
```sql
-- Query: WHERE OrderDate >= @StartDate ORDER BY OrderDate DESC
CREATE NONCLUSTERED INDEX IX_Orders_OrderDate
ON dbo.Orders (OrderDate DESC);
```

### Pattern 4: Composite Filter + Sort
```sql
-- Query: WHERE CustomerId = @Id ORDER BY OrderDate DESC
CREATE NONCLUSTERED INDEX IX_Orders_CustomerId_OrderDate
ON dbo.Orders (CustomerId, OrderDate DESC);
```

### Pattern 5: Covering Index for Report
```sql
-- Query: SELECT CustomerId, OrderDate, OrderTotal WHERE OrderDate >= @Date
CREATE NONCLUSTERED INDEX IX_Orders_Report
ON dbo.Orders (OrderDate)
INCLUDE (CustomerId, OrderTotal);
```

---

## 6. Complete Example

### Scenario: Optimize customer order history query

**Query:**
```sql
SELECT OrderId, OrderDate, OrderTotal, Status
FROM Orders
WHERE CustomerId = @CustomerId
  AND OrderDate >= DATEADD(MONTH, -6, GETDATE())
ORDER BY OrderDate DESC;
```

**Analysis:**
- Filter: CustomerId (equality), OrderDate (range)
- Sort: OrderDate DESC
- Select: OrderId, OrderDate, OrderTotal, Status

**Current Performance:**
- Clustered Index Scan
- 850,000 logical reads
- 1,200 ms execution time

**Index Design:**
```sql
CREATE NONCLUSTERED INDEX IX_Orders_CustomerId_OrderDate
ON dbo.Orders (CustomerId, OrderDate DESC)
INCLUDE (OrderTotal, Status);
```

**Reasoning:**
1. `CustomerId` first (equality filter, most selective)
2. `OrderDate DESC` second (range filter + sort order)
3. `INCLUDE` non-key columns to avoid key lookups

**After Optimization:**
- Index Seek
- 12 logical reads
- 8 ms execution time

**Results:**
- 99.1% reduction in execution time
- 99.999% reduction in I/O

---

## 7. Quality Checklist

Before finalizing index:

- [ ] Execution plan shows Index Seek (not Scan)
- [ ] Logical reads significantly reduced
- [ ] No key lookups for covering queries
- [ ] Index is actually being used (check DMV)
- [ ] Fragmentation monitored
- [ ] Statistics up to date
- [ ] Index maintenance plan in place
- [ ] Impact on INSERT/UPDATE/DELETE acceptable
- [ ] No duplicate or redundant indexes

---

## 8. Index Anti-Patterns

### BAD: Anti-Pattern 1: Too Many Indexes
**Problem:** Slows down INSERT/UPDATE/DELETE
**Fix:** Drop unused indexes, consolidate overlapping indexes

### BAD: Anti-Pattern 2: Wrong Column Order
**Problem:** Index not used for queries
**Fix:** Equality columns first, then range/sort columns

### BAD: Anti-Pattern 3: Index on Low Selectivity Column
**Problem:** Index scan instead of seek
**Fix:** Avoid indexing columns with few distinct values (e.g., boolean flags)

### BAD: Anti-Pattern 4: Missing INCLUDE Columns
**Problem:** Key lookups remain
**Fix:** Add frequently accessed columns to INCLUDE

### BAD: Anti-Pattern 5: Ignoring Fragmentation
**Problem:** Performance degrades over time
**Fix:** Regular maintenance (reorganize/rebuild)

```
