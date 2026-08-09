# dlt Data Warehouse Loading Template

*Purpose: Load data into modern data warehouses (Snowflake, BigQuery, Redshift, Postgres) using dlt.*

## Supported Destinations

- **Cloud Warehouses**: Snowflake, BigQuery, Redshift, Databricks
- **Databases**: PostgreSQL, DuckDB
- **Data Lakes**: S3, GCS, Azure Blob Storage (Parquet/Delta/Iceberg)

## Snowflake Destination

### Installation

```bash
pip install dlt[snowflake]
```

### Configuration (.dlt/secrets.toml)

```toml
[destination.snowflake.credentials]
database = "ANALYTICS"
password = "your_password"
username = "dlt_user"
host = "abc12345.snowflakecomputing.com"
warehouse = "COMPUTE_WH"
role = "TRANSFORMER"
```

### Basic Loading

```python
import dlt
from dlt.sources.rest_api import rest_api_source

# Define source
source = rest_api_source({
    "client": {"base_url": "https://api.example.com/"},
    "resources": ["users", "orders"]
})

# Create pipeline to Snowflake
pipeline = dlt.pipeline(
    pipeline_name="api_to_snowflake",
    destination="snowflake",
    dataset_name="RAW_DATA"  # Schema name in Snowflake
)

load_info = pipeline.run(source)
print(load_info)
```

### Advanced Snowflake Configuration

```python
import dlt

pipeline = dlt.pipeline(
    pipeline_name="advanced_snowflake",
    destination="snowflake",
    dataset_name="RAW_DATA"
)

# Configure Snowflake-specific options
pipeline.run(
    source,
    loader_file_format="parquet",  # Use Parquet for faster loads
    table_name="users",
    write_disposition="replace",
    primary_key="user_id"
)
```

### Snowflake with Staging

```toml
# .dlt/secrets.toml
[destination.snowflake.credentials]
database = "ANALYTICS"
password = "your_password"
username = "dlt_user"
host = "abc12345.snowflakecomputing.com"
warehouse = "COMPUTE_WH"
role = "TRANSFORMER"

# Use external stage (S3)
stage_name = "s3://my-bucket/dlt-staging/"
```

## Google BigQuery Destination

### Installation

```bash
pip install dlt[bigquery]
```

### Service Account Authentication

```toml
# .dlt/secrets.toml
[destination.bigquery.credentials]
project_id = "my-project"
private_key = "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
client_email = "dlt-loader@my-project.iam.gserviceaccount.com"
location = "US"  # Dataset location
```

### Loading to BigQuery

```python
import dlt

source = rest_api_source({
    "client": {"base_url": "https://api.example.com/"},
    "resources": ["products"]
})

pipeline = dlt.pipeline(
    pipeline_name="api_to_bigquery",
    destination="bigquery",
    dataset_name="raw_data"  # BigQuery dataset
)

load_info = pipeline.run(source)
```

### BigQuery Partitioning

```python
import dlt

@dlt.resource(
    name="events",
    write_disposition="append",
    table_format="delta"  # Use Delta Lake format
)
def load_events():
    # Your data source
    yield events_data

pipeline = dlt.pipeline(
    pipeline_name="partitioned_bigquery",
    destination="bigquery",
    dataset_name="events"
)

# BigQuery will auto-partition by _dlt_load_id
load_info = pipeline.run([load_events()])
```

### BigQuery Clustering

```python
# Configure via destination settings
import dlt

pipeline = dlt.pipeline(
    pipeline_name="clustered_bigquery",
    destination="bigquery",
    dataset_name="analytics"
)

# Load with hints for clustering
@dlt.resource(
    name="users",
    columns={
        "user_id": {"data_type": "bigint", "primary_key": True},
        "country": {"data_type": "text", "cluster": True},  # Cluster by country
        "created_at": {"data_type": "timestamp", "partition": True}  # Partition by date
    }
)
def load_users():
    yield users_data

load_info = pipeline.run([load_users()])
```

## PostgreSQL Destination

### Installation

```bash
pip install dlt[postgres]
```

### Configuration

```toml
# .dlt/secrets.toml
[destination.postgres.credentials]
database = "warehouse"
username = "dlt_user"
password = "your_password"
host = "localhost"
port = 5432
```

### Loading to PostgreSQL

```python
import dlt

source = sql_database(
    credentials="mysql+pymysql://user:password@localhost:3306/source_db",
    schema="public"
)

pipeline = dlt.pipeline(
    pipeline_name="mysql_to_postgres",
    destination="postgres",
    dataset_name="replicated"
)

load_info = pipeline.run(source)
```

### PostgreSQL with Indexes

```python
import dlt

@dlt.resource(
    name="orders",
    write_disposition="merge",
    primary_key="order_id",
    columns={
        "order_id": {"data_type": "bigint", "primary_key": True},
        "customer_id": {"data_type": "bigint", "index": True},  # Create index
        "order_date": {"data_type": "timestamp", "index": True}
    }
)
def load_orders():
    yield orders_data

pipeline = dlt.pipeline(
    pipeline_name="indexed_postgres",
    destination="postgres",
    dataset_name="sales"
)

load_info = pipeline.run([load_orders()])
```

## DuckDB Destination (Local Analytics)

### Installation

```bash
pip install dlt[duckdb]
```

### Local DuckDB Loading

```python
import dlt

source = rest_api_source({
    "client": {"base_url": "https://api.example.com/"},
    "resources": ["analytics_events"]
})

pipeline = dlt.pipeline(
    pipeline_name="api_to_duckdb",
    destination="duckdb",
    dataset_name="events"
)

load_info = pipeline.run(source)

# Query loaded data
import duckdb
con = duckdb.connect("api_to_duckdb.duckdb")
result = con.execute("SELECT COUNT(*) FROM events.analytics_events").fetchall()
print(f"Loaded {result[0][0]} events")
```

### DuckDB with Parquet Export

```python
import dlt

pipeline = dlt.pipeline(
    pipeline_name="duckdb_to_parquet",
    destination="duckdb",
    dataset_name="raw"
)

load_info = pipeline.run(source)

# Export to Parquet
import duckdb
con = duckdb.connect("duckdb_to_parquet.duckdb")
con.execute("""
    COPY raw.users
    TO 'users.parquet' (FORMAT PARQUET, COMPRESSION ZSTD)
""")
```

## Amazon Redshift Destination

### Installation

```bash
pip install dlt[redshift]
```

### Configuration

```toml
# .dlt/secrets.toml
[destination.redshift.credentials]
database = "analytics"
username = "dlt_user"
password = "your_password"
host = "redshift-cluster.abc123.us-east-1.redshift.amazonaws.com"
port = 5439

# Use S3 staging
staging_s3_bucket = "s3://my-redshift-staging/"
```

### Loading to Redshift

```python
import dlt

source = sql_database(
    credentials="postgresql://user:password@localhost:5432/source_db",
    schema="public"
)

pipeline = dlt.pipeline(
    pipeline_name="postgres_to_redshift",
    destination="redshift",
    dataset_name="replicated"
)

load_info = pipeline.run(source)
```

### Redshift Distribution & Sort Keys

```python
import dlt

@dlt.resource(
    name="sales",
    write_disposition="replace",
    columns={
        "sale_id": {"data_type": "bigint", "primary_key": True},
        "customer_id": {"data_type": "bigint", "dist_key": True},  # Distribution key
        "sale_date": {"data_type": "timestamp", "sort_key": True}  # Sort key
    }
)
def load_sales():
    yield sales_data

pipeline = dlt.pipeline(
    pipeline_name="optimized_redshift",
    destination="redshift",
    dataset_name="analytics"
)

load_info = pipeline.run([load_sales()])
```

## Multi-Destination Pattern

### Load to Multiple Warehouses

```python
import dlt

# Define source once
source = rest_api_source({
    "client": {"base_url": "https://api.example.com/"},
    "resources": ["events"]
})

# Load to Snowflake
snowflake_pipeline = dlt.pipeline(
    pipeline_name="to_snowflake",
    destination="snowflake",
    dataset_name="RAW_DATA"
)
snowflake_pipeline.run(source)

# Load to BigQuery
bigquery_pipeline = dlt.pipeline(
    pipeline_name="to_bigquery",
    destination="bigquery",
    dataset_name="raw_data"
)
bigquery_pipeline.run(source)

# Load to local DuckDB
duckdb_pipeline = dlt.pipeline(
    pipeline_name="to_duckdb",
    destination="duckdb",
    dataset_name="events"
)
duckdb_pipeline.run(source)
```

## Performance Optimization

### Parallel Loading

```python
import dlt

pipeline = dlt.pipeline(
    pipeline_name="parallel_load",
    destination="snowflake",
    dataset_name="RAW_DATA"
)

# dlt automatically parallelizes loads
load_info = pipeline.run(
    source,
    workers=4  # Number of parallel workers
)
```

### Batch Size Tuning

```python
import dlt

@dlt.resource(
    name="large_table",
    write_disposition="append"
)
def load_large_table():
    batch_size = 50000

    for batch in fetch_in_batches(batch_size):
        yield batch

pipeline = dlt.pipeline(
    pipeline_name="batched_load",
    destination="bigquery",
    dataset_name="raw"
)

load_info = pipeline.run([load_large_table()])
```

### Compression

```python
# Configure compression in secrets.toml
[destination.snowflake]
loader_file_format = "parquet"  # Compressed by default

[destination.bigquery]
file_format = "jsonl"
compression = "gzip"
```

## Monitoring and Validation

### Check Load Status

```python
import dlt

pipeline = dlt.pipeline(
    pipeline_name="monitored_load",
    destination="snowflake",
    dataset_name="RAW_DATA"
)

load_info = pipeline.run(source)

# Check load info
print(f"Pipeline: {pipeline.pipeline_name}")
print(f"Destination: {pipeline.destination}")
print(f"Dataset: {pipeline.dataset_name}")
print(f"Load packages: {len(load_info.load_packages)}")
print(f"First load ID: {load_info.loads_ids[0]}")

# Check for errors
if load_info.has_failed_jobs:
    print("Load failed!")
    for package in load_info.load_packages:
        for job in package.jobs["failed_jobs"]:
            print(f"Failed job: {job}")
```

### Validate Row Counts

```python
import dlt

pipeline = dlt.pipeline(
    pipeline_name="validated_load",
    destination="postgres",
    dataset_name="raw"
)

# Load data
load_info = pipeline.run(source)

# Validate with SQL
with pipeline.sql_client() as client:
    result = client.execute_sql("SELECT COUNT(*) FROM raw.users")
    row_count = result[0][0]
    print(f"Loaded {row_count} rows")

    # Check for nulls in critical columns
    result = client.execute_sql("""
        SELECT COUNT(*) FROM raw.users WHERE user_id IS NULL
    """)
    null_count = result[0][0]
    if null_count > 0:
        print(f"WARNING: {null_count} rows with null user_id")
```

## Cost Optimization

### Snowflake Warehouse Sizing

```toml
# .dlt/secrets.toml
[destination.snowflake.credentials]
warehouse = "LOADING_XS"  # Use smaller warehouse for loading
```

### BigQuery Slot Reservations

```python
# Use batch loading for cost savings
import dlt

pipeline = dlt.pipeline(
    pipeline_name="batch_bigquery",
    destination="bigquery",
    dataset_name="raw"
)

# BigQuery batch loading (lower cost, higher latency)
load_info = pipeline.run(source, priority="BATCH")
```

### Incremental to Reduce Scans

```python
import dlt

@dlt.resource(
    name="events",
    write_disposition="append"
)
def load_events_incremental():
    last_timestamp = dlt.sources.incremental(
        cursor_path="event_timestamp",
        initial_value="2024-01-01"
    )

    # Only load new data
    events = fetch_events_since(last_timestamp.start_value)
    yield events

# Incremental loads reduce cost and time
pipeline = dlt.pipeline(
    pipeline_name="cost_optimized",
    destination="snowflake",
    dataset_name="EVENTS"
)

load_info = pipeline.run([load_events_incremental()])
```

## Best Practices

- BEST: Use appropriate warehouse size (start small, scale up)
- BEST: Enable compression (Parquet for Snowflake/BigQuery)
- BEST: Implement incremental loading for large tables
- BEST: Use staging areas (S3 for Snowflake/Redshift)
- BEST: Partition and cluster tables in BigQuery
- BEST: Set distribution and sort keys in Redshift
- BEST: Monitor load times and costs
- BEST: Validate row counts after each load
- BEST: Use service accounts with minimal permissions
- BEST: Store credentials in secrets.toml (never commit)
- BEST: Implement retry logic for transient failures
- BEST: Archive old load packages to save storage
