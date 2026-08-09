```markdown
# DuckDB Data Import & Export Template

*Purpose: Standardized workflows for importing data from various sources and exporting results efficiently in DuckDB.*

---

## When to Use

Use this template for:
- Loading data from files (CSV, Parquet, JSON, Excel)
- Importing from external databases (Postgres, MySQL, SQLite)
- Exporting query results to files
- ETL data transformation workflows
- Data format conversions

---

## Template Structure

1. **Import Workflows**
2. **Export Workflows**
3. **Format Conversion**
4. **Performance Optimization**

---

# IMPORT WORKFLOWS

## 1. Import from CSV

### Basic CSV Import
```sql
-- Read CSV file
SELECT * FROM read_csv('data/sales.csv');

-- Read with options
SELECT * FROM read_csv('data/sales.csv',
  header = true,
  delimiter = ',',
  quote = '"',
  nullstr = 'NULL'
);

-- Create table from CSV
CREATE TABLE sales AS
SELECT * FROM read_csv('data/sales.csv');
```

### Multiple CSV Files (Glob Pattern)
```sql
-- Read all CSV files in directory
SELECT * FROM read_csv('data/sales/*.csv');

-- Read with specific pattern
SELECT * FROM read_csv('data/sales_202*.csv');
```

### Large CSV Files (Streaming)
```sql
-- Process large CSV without loading into memory
COPY (
  SELECT * FROM read_csv('large_file.csv')
  WHERE region = 'US'
)
TO 'filtered_output.parquet' (FORMAT PARQUET);
```

---

## 2. Import from Parquet

### Basic Parquet Import
```sql
-- Read Parquet file (fastest format)
SELECT * FROM read_parquet('data/sales.parquet');

-- Create table from Parquet
CREATE TABLE sales AS
SELECT * FROM read_parquet('data/sales.parquet');
```

### Partitioned Parquet
```sql
-- Read partitioned Parquet dataset
SELECT * FROM read_parquet('data/sales/**/year=*/month=*/*.parquet',
  hive_partitioning = true
);

-- Filter on partition columns (very fast)
SELECT * FROM read_parquet('data/sales/**/year=*/month=*/*.parquet',
  hive_partitioning = true
)
WHERE year = 2024 AND month = 11;
```

### Column Pruning
```sql
-- Read only specific columns (projection pushdown)
SELECT customer_id, order_date, amount
FROM read_parquet('data/large_sales.parquet');
-- DuckDB reads only these 3 columns from file
```

---

## 3. Import from JSON

### Basic JSON Import
```sql
-- Read JSON file
SELECT * FROM read_json('data/events.json');

-- Read newline-delimited JSON (NDJSON)
SELECT * FROM read_json('data/events.ndjson', format = 'newline_delimited');

-- Auto-detect schema
SELECT * FROM read_json('data/events.json', auto_detect = true);
```

### Nested JSON
```sql
-- Flatten nested JSON
SELECT
  user_id,
  event_type,
  UNNEST(properties) AS property_key,
  UNNEST(properties.value) AS property_value
FROM read_json('data/events.json');
```

---

## 4. Import from Excel

```sql
-- Read Excel file (requires spatial extension)
INSTALL spatial;
LOAD spatial;

-- Read specific sheet
SELECT * FROM st_read('data/sales.xlsx', layer = 'Sheet1');

-- Alternative: Convert Excel to CSV first
-- Then use read_csv
```

---

## 5. Import from PostgreSQL

```sql
-- Install and load postgres extension
INSTALL postgres_scanner;
LOAD postgres_scanner;

-- Attach Postgres database
ATTACH 'dbname=mydb user=user password=pass host=localhost' AS postgres_db (TYPE postgres);

-- Query Postgres table
SELECT * FROM postgres_db.public.sales;

-- Copy to DuckDB table
CREATE TABLE local_sales AS
SELECT * FROM postgres_db.public.sales;

-- Detach when done
DETACH postgres_db;
```

---

## 6. Import from MySQL

```sql
-- Install and load mysql extension
INSTALL mysql_scanner;
LOAD mysql_scanner;

-- Attach MySQL database
ATTACH 'host=localhost user=root password=pass database=mydb' AS mysql_db (TYPE mysql);

-- Query MySQL table
SELECT * FROM mysql_db.sales;

-- Copy to DuckDB
CREATE TABLE local_sales AS
SELECT * FROM mysql_db.sales;

DETACH mysql_db;
```

---

## 7. Import from SQLite

```sql
-- Install and load sqlite extension
INSTALL sqlite_scanner;
LOAD sqlite_scanner;

-- Attach SQLite database
ATTACH 'data/mydb.sqlite' AS sqlite_db (TYPE sqlite);

-- Query SQLite table
SELECT * FROM sqlite_db.sales;

-- Copy to DuckDB
CREATE TABLE local_sales AS
SELECT * FROM sqlite_db.sales;

DETACH sqlite_db;
```

---

# EXPORT WORKFLOWS

## 1. Export to Parquet

### Basic Export
```sql
-- Export query result to Parquet
COPY (SELECT * FROM sales WHERE year = 2024)
TO 'output/sales_2024.parquet' (FORMAT PARQUET);

-- With compression
COPY (SELECT * FROM sales)
TO 'output/sales.parquet' (FORMAT PARQUET, COMPRESSION ZSTD);
```

### Partitioned Export
```sql
-- Export with Hive partitioning
COPY (SELECT * FROM sales)
TO 'output/sales' (FORMAT PARQUET, PARTITION_BY (year, month));

-- Creates structure: output/sales/year=2024/month=11/data.parquet
```

### Compression Options
```sql
-- Uncompressed (fastest write)
COPY (SELECT * FROM sales)
TO 'sales.parquet' (FORMAT PARQUET, COMPRESSION UNCOMPRESSED);

-- SNAPPY (balanced)
COPY (SELECT * FROM sales)
TO 'sales.parquet' (FORMAT PARQUET, COMPRESSION SNAPPY);

-- ZSTD (best compression)
COPY (SELECT * FROM sales)
TO 'sales.parquet' (FORMAT PARQUET, COMPRESSION ZSTD);

-- GZIP (good compression)
COPY (SELECT * FROM sales)
TO 'sales.parquet' (FORMAT PARQUET, COMPRESSION GZIP);
```

---

## 2. Export to CSV

### Basic CSV Export
```sql
-- Export to CSV
COPY (SELECT * FROM sales)
TO 'output/sales.csv' (FORMAT CSV, HEADER TRUE);

-- With delimiter and quote options
COPY (SELECT * FROM sales)
TO 'output/sales.csv' (FORMAT CSV, DELIMITER ',', QUOTE '"', HEADER TRUE);
```

### Compressed CSV
```sql
-- Export with GZIP compression
COPY (SELECT * FROM sales)
TO 'output/sales.csv.gz' (FORMAT CSV, COMPRESSION GZIP, HEADER TRUE);
```

---

## 3. Export to JSON

```sql
-- Export to JSON
COPY (SELECT * FROM sales)
TO 'output/sales.json' (FORMAT JSON);

-- Export as newline-delimited JSON (NDJSON)
COPY (SELECT * FROM sales)
TO 'output/sales.ndjson' (FORMAT JSON, ARRAY FALSE);
```

---

## 4. Export to Excel

```sql
-- Note: No direct Excel export in DuckDB
-- Workaround: Export to CSV, then convert externally
COPY (SELECT * FROM sales)
TO 'output/sales.csv' (FORMAT CSV, HEADER TRUE);
```

---

# FORMAT CONVERSION

## CSV → Parquet
```sql
-- One-step conversion
COPY (SELECT * FROM read_csv('input/sales.csv'))
TO 'output/sales.parquet' (FORMAT PARQUET, COMPRESSION ZSTD);
```

## JSON → Parquet
```sql
-- Convert JSON to Parquet
COPY (SELECT * FROM read_json('input/events.json'))
TO 'output/events.parquet' (FORMAT PARQUET, COMPRESSION ZSTD);
```

## Parquet → CSV
```sql
-- Convert Parquet to CSV
COPY (SELECT * FROM read_parquet('input/sales.parquet'))
TO 'output/sales.csv' (FORMAT CSV, HEADER TRUE);
```

## Multiple Files → Single Parquet
```sql
-- Merge multiple CSV files into one Parquet
COPY (SELECT * FROM read_csv('input/*.csv'))
TO 'output/merged.parquet' (FORMAT PARQUET, COMPRESSION ZSTD);
```

---

# PERFORMANCE OPTIMIZATION

## 1. Parallel Import
```sql
-- Set threads for parallel processing
SET threads TO 8;

-- Import large file with parallelism
CREATE TABLE large_sales AS
SELECT * FROM read_parquet('data/*.parquet');
```

## 2. Memory Management
```sql
-- Check memory limit
SELECT * FROM duckdb_settings() WHERE name = 'memory_limit';

-- Increase if needed for large imports
SET memory_limit = '8GB';
```

## 3. Batch Processing
```sql
-- Process large dataset in batches
CREATE TABLE processed_data AS
SELECT * FROM read_csv('large.csv')
WHERE MOD(row_number() OVER (), 10000) = 0;
```

## 4. Streaming Processing
```sql
-- Stream large file without loading into memory
COPY (
  SELECT *
  FROM read_csv('very_large.csv')
  WHERE condition = true
)
TO 'filtered.parquet' (FORMAT PARQUET);
-- Never loads full file into memory
```

---

# COMPLETE EXAMPLES

## Example 1: ETL Pipeline (CSV → Transform → Parquet)

```sql
-- Step 1: Load CSV with transformations
CREATE TABLE cleaned_sales AS
SELECT
  CAST(order_id AS INTEGER) AS order_id,
  STRPTIME(order_date, '%Y-%m-%d') AS order_date,
  UPPER(TRIM(customer_name)) AS customer_name,
  CAST(amount AS DECIMAL(10,2)) AS amount,
  CASE
    WHEN region IS NULL THEN 'Unknown'
    ELSE region
  END AS region
FROM read_csv('raw/sales.csv', auto_detect = true);

-- Step 2: Export to Parquet with partitioning
COPY (SELECT * FROM cleaned_sales)
TO 'processed/sales' (
  FORMAT PARQUET,
  COMPRESSION ZSTD,
  PARTITION_BY (YEAR(order_date), MONTH(order_date))
);
```

---

## Example 2: Migrate from PostgreSQL to Parquet

```sql
-- Install extension
INSTALL postgres_scanner;
LOAD postgres_scanner;

-- Attach database
ATTACH 'dbname=prod user=reader password=pass host=pg.example.com' AS pg (TYPE postgres);

-- Export tables to Parquet
COPY (SELECT * FROM pg.public.customers)
TO 'export/customers.parquet' (FORMAT PARQUET, COMPRESSION ZSTD);

COPY (SELECT * FROM pg.public.orders)
TO 'export/orders.parquet' (FORMAT PARQUET, COMPRESSION ZSTD);

COPY (SELECT * FROM pg.public.products)
TO 'export/products.parquet' (FORMAT PARQUET, COMPRESSION ZSTD);

DETACH pg;
```

---

## Example 3: Incremental Data Load

```sql
-- Initial load
CREATE TABLE sales AS
SELECT * FROM read_parquet('data/sales_historical.parquet');

-- Incremental append (new data only)
INSERT INTO sales
SELECT * FROM read_csv('data/sales_new.csv')
WHERE order_date > (SELECT MAX(order_date) FROM sales);

-- Export updated dataset
COPY (SELECT * FROM sales)
TO 'data/sales_updated.parquet' (FORMAT PARQUET, COMPRESSION ZSTD);
```

---

## Quality Checklist

Before finalizing import/export:

- [ ] File format optimized (Parquet preferred for large data)
- [ ] Compression enabled (ZSTD for Parquet, GZIP for CSV)
- [ ] Column pruning used (only needed columns)
- [ ] Parallel processing enabled (set threads)
- [ ] Memory limit appropriate for dataset size
- [ ] Partition strategy defined (for large exports)
- [ ] Data validation performed (row counts, nulls, types)
- [ ] File paths and permissions verified

```
