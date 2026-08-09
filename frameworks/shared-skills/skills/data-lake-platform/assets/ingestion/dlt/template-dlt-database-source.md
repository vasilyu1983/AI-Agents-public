# dlt Database Source Template

*Purpose: Extract data from relational databases (Postgres, MySQL, MongoDB) using dlt for ELT pipelines.*

## Installation

```bash
# PostgreSQL
pip install dlt[postgres]
pip install psycopg2-binary

# MySQL
pip install dlt[mysql]
pip install pymysql

# MongoDB
pip install dlt[mongodb]
pip install pymongo

# SQL Server
pip install dlt[mssql]
pip install pyodbc
```

## PostgreSQL Source

### Basic Table Extraction

```python
import dlt
from dlt.sources.sql_database import sql_database

# Extract all tables from schema
source = sql_database(
    credentials="postgresql://user:password@localhost:5432/database",
    schema="public"
)

pipeline = dlt.pipeline(
    pipeline_name="postgres_to_duckdb",
    destination="duckdb",
    dataset_name="postgres_raw"
)

load_info = pipeline.run(source)
print(load_info)
```

### Select Specific Tables

```python
source = sql_database(
    credentials="postgresql://user:password@localhost:5432/database",
    schema="public",
    table_names=["customers", "orders", "products"]
)

pipeline = dlt.pipeline(
    pipeline_name="postgres_selected",
    destination="bigquery",
    dataset_name="postgres_raw"
)

load_info = pipeline.run(source)
```

### Custom SQL Query

```python
import dlt
from sqlalchemy import create_engine

# Create engine
engine = create_engine("postgresql://user:password@localhost:5432/database")

# Define custom query
@dlt.resource(name="active_customers")
def get_active_customers():
    query = """
    SELECT
        customer_id,
        email,
        created_at,
        last_order_date
    FROM customers
    WHERE status = 'active'
      AND last_order_date >= CURRENT_DATE - INTERVAL '30 days'
    """

    with engine.connect() as conn:
        result = conn.execute(query)
        yield from result

pipeline = dlt.pipeline(
    pipeline_name="custom_query",
    destination="snowflake",
    dataset_name="analytics"
)

load_info = pipeline.run([get_active_customers()])
```

## MySQL Source

### Extract with Reflection

```python
import dlt
from dlt.sources.sql_database import sql_database

source = sql_database(
    credentials="mysql+pymysql://user:password@localhost:3306/database",
    schema="production",
    reflection_level="full"  # Extract schema metadata
)

pipeline = dlt.pipeline(
    pipeline_name="mysql_to_postgres",
    destination="postgres",
    dataset_name="mysql_raw"
)

load_info = pipeline.run(source)
```

### Incremental Loading by Timestamp

```python
import dlt
from dlt.sources.sql_database import sql_table

@dlt.resource(
    name="orders",
    write_disposition="append",
    primary_key="order_id"
)
def load_orders_incremental():
    # Use dlt.sources.incremental for cursor-based loading
    last_value = dlt.sources.incremental(
        "updated_at",
        initial_value="2024-01-01T00:00:00"
    )

    from sqlalchemy import create_engine
    engine = create_engine("mysql+pymysql://user:password@localhost:3306/database")

    query = f"""
    SELECT * FROM orders
    WHERE updated_at >= '{last_value.start_value}'
    ORDER BY updated_at
    """

    with engine.connect() as conn:
        result = conn.execute(query)
        yield from result

pipeline = dlt.pipeline(
    pipeline_name="mysql_incremental",
    destination="duckdb",
    dataset_name="mysql_raw"
)

load_info = pipeline.run([load_orders_incremental()])
```

## MongoDB Source

### Collection Extraction

```python
import dlt
from pymongo import MongoClient

@dlt.resource(name="users")
def load_mongodb_collection():
    client = MongoClient("mongodb://localhost:27017/")
    db = client["production"]
    collection = db["users"]

    # Stream documents
    for doc in collection.find():
        # Remove MongoDB _id (not JSON serializable)
        doc["_id"] = str(doc["_id"])
        yield doc

pipeline = dlt.pipeline(
    pipeline_name="mongodb_to_postgres",
    destination="postgres",
    dataset_name="mongodb_raw"
)

load_info = pipeline.run([load_mongodb_collection()])
```

### Incremental MongoDB Loading

```python
import dlt
from pymongo import MongoClient
from datetime import datetime

@dlt.resource(
    name="events",
    write_disposition="append",
    primary_key="event_id"
)
def load_events_incremental():
    last_timestamp = dlt.sources.incremental(
        "timestamp",
        initial_value=datetime(2024, 1, 1)
    )

    client = MongoClient("mongodb://localhost:27017/")
    db = client["analytics"]
    collection = db["events"]

    # Query with incremental filter
    query = {"timestamp": {"$gte": last_timestamp.start_value}}

    for doc in collection.find(query).sort("timestamp", 1):
        doc["_id"] = str(doc["_id"])
        yield doc

pipeline = dlt.pipeline(
    pipeline_name="mongodb_incremental",
    destination="snowflake",
    dataset_name="events_raw"
)

load_info = pipeline.run([load_events_incremental()])
```

## SQL Server Source

```python
import dlt
from dlt.sources.sql_database import sql_database

source = sql_database(
    credentials="mssql+pyodbc://user:password@localhost:1433/database?driver=ODBC+Driver+17+for+SQL+Server",
    schema="dbo",
    table_names=["sales", "customers"]
)

pipeline = dlt.pipeline(
    pipeline_name="sqlserver_to_bigquery",
    destination="bigquery",
    dataset_name="sqlserver_raw"
)

load_info = pipeline.run(source)
```

## Advanced Patterns

### Parallel Table Loading

```python
import dlt
from dlt.sources.sql_database import sql_database

source = sql_database(
    credentials="postgresql://user:password@localhost:5432/database",
    schema="public",
    parallel=True,  # Enable parallel extraction
    chunk_size=10000  # Rows per chunk
)

pipeline = dlt.pipeline(
    pipeline_name="parallel_extract",
    destination="duckdb",
    dataset_name="postgres_raw"
)

load_info = pipeline.run(source)
```

### Schema Evolution Handling

```python
import dlt

source = sql_database(
    credentials="postgresql://user:password@localhost:5432/database",
    schema="public",
    detect_precision_hints=True  # Preserve column types
)

pipeline = dlt.pipeline(
    pipeline_name="schema_evolution",
    destination="postgres",
    dataset_name="raw"
)

# Schema will auto-evolve if source changes
load_info = pipeline.run(source)
```

### Cross-Database Joins

```python
import dlt
from sqlalchemy import create_engine

# Extract from two databases
@dlt.resource(name="enriched_orders")
def join_across_databases():
    pg_engine = create_engine("postgresql://user:password@localhost:5432/sales")
    mysql_engine = create_engine("mysql+pymysql://user:password@localhost:3306/customers")

    # Extract from PostgreSQL
    with pg_engine.connect() as conn:
        orders = conn.execute("SELECT * FROM orders").fetchall()

    # Extract from MySQL
    with mysql_engine.connect() as conn:
        customers = {row[0]: row for row in conn.execute("SELECT * FROM customers")}

    # Join in Python
    for order in orders:
        customer = customers.get(order.customer_id)
        if customer:
            yield {
                **dict(order),
                "customer_name": customer.name,
                "customer_email": customer.email
            }

pipeline = dlt.pipeline(
    pipeline_name="cross_db_join",
    destination="snowflake",
    dataset_name="enriched"
)

load_info = pipeline.run([join_across_databases()])
```

## Configuration (.dlt/config.toml)

```toml
[sources.postgres]
schema = "public"
chunk_size = 10000
parallel = true

[sources.mysql]
schema = "production"
reflection_level = "full"

[sources.mongodb]
database = "analytics"
batch_size = 1000

[destination.postgres]
credentials = "postgres://user:password@localhost:5432/warehouse"

[destination.snowflake]
database = "ANALYTICS"
schema = "RAW_DATA"
```

## Secrets (.dlt/secrets.toml)

```toml
[sources.postgres.credentials]
database = "sales"
username = "etl_user"
password = "your_password"
host = "localhost"
port = 5432

[sources.mysql.credentials]
database = "customers"
username = "etl_user"
password = "your_password"
host = "localhost"
port = 3306

[sources.mongodb.credentials]
connection_string = "mongodb://user:password@localhost:27017/"

[sources.mssql.credentials]
connection_string = "mssql+pyodbc://user:password@localhost:1433/database?driver=ODBC+Driver+17+for+SQL+Server"
```

## Performance Optimization

### Chunked Extraction

```python
import dlt
from dlt.sources.sql_database import sql_table

@dlt.resource(name="large_table")
def extract_in_chunks():
    from sqlalchemy import create_engine
    engine = create_engine("postgresql://user:password@localhost:5432/database")

    chunk_size = 50000
    offset = 0

    while True:
        query = f"SELECT * FROM large_table LIMIT {chunk_size} OFFSET {offset}"

        with engine.connect() as conn:
            result = conn.execute(query).fetchall()

            if not result:
                break

            yield from result
            offset += chunk_size

pipeline = dlt.pipeline(
    pipeline_name="chunked_extract",
    destination="duckdb",
    dataset_name="raw"
)

load_info = pipeline.run([extract_in_chunks()])
```

### Connection Pooling

```python
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

engine = create_engine(
    "postgresql://user:password@localhost:5432/database",
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20
)
```

## Monitoring

```python
import dlt

pipeline = dlt.pipeline(
    pipeline_name="monitored_pipeline",
    destination="postgres",
    dataset_name="raw"
)

load_info = pipeline.run(source)

# Check statistics
print(f"Packages: {len(load_info.load_packages)}")
print(f"Loaded tables: {load_info.loads_ids}")

# Query loaded data
with pipeline.sql_client() as client:
    result = client.execute_sql("SELECT COUNT(*) FROM customers")
    print(f"Loaded {result[0][0]} customers")
```

## Best Practices

- BEST: Use connection pooling for large extractions
- BEST: Implement incremental loading for large tables
- BEST: Extract in parallel when possible
- BEST: Use chunking for tables with millions of rows
- BEST: Store credentials in secrets.toml
- BEST: Enable schema evolution for dynamic sources
- BEST: Monitor extraction performance and row counts
- BEST: Use SQL queries to filter data at source (reduce transfer)
