# dlt Incremental Loading Template

*Purpose: Implement efficient incremental data loading strategies using dlt to avoid full table scans.*

## Why Incremental Loading?

- **Reduce data transfer**: Load only new/changed records
- **Faster pipelines**: Avoid scanning entire tables
- **Lower costs**: Minimize compute and network usage
- **Enable real-time**: Process changes as they happen

## Incremental by Timestamp

### Basic Timestamp Tracking

```python
import dlt
from dlt.sources.incremental import Incremental

@dlt.resource(
    name="orders",
    write_disposition="append",
    primary_key="order_id"
)
def load_orders_incremental():
    # Track last processed timestamp
    last_timestamp = dlt.sources.incremental(
        cursor_path="updated_at",
        initial_value="2024-01-01T00:00:00"
    )

    # Your data source (API, database, etc.)
    orders = fetch_orders_since(last_timestamp.start_value)

    yield orders

pipeline = dlt.pipeline(
    pipeline_name="orders_incremental",
    destination="duckdb",
    dataset_name="sales"
)

load_info = pipeline.run([load_orders_incremental()])
```

### Database Query with Incremental Filter

```python
import dlt
from sqlalchemy import create_engine

@dlt.resource(
    name="users",
    write_disposition="merge",  # Upsert existing records
    primary_key="user_id"
)
def load_users_incremental():
    last_updated = dlt.sources.incremental(
        cursor_path="updated_at",
        initial_value="2024-01-01"
    )

    engine = create_engine("postgresql://user:password@localhost:5432/db")

    query = f"""
    SELECT * FROM users
    WHERE updated_at >= '{last_updated.start_value}'
    ORDER BY updated_at
    """

    with engine.connect() as conn:
        result = conn.execute(query)
        yield from result

pipeline = dlt.pipeline(
    pipeline_name="users_incremental",
    destination="postgres",
    dataset_name="raw"
)

load_info = pipeline.run([load_users_incremental()])
```

### REST API with Date Range

```python
import dlt
from datetime import datetime, timedelta

@dlt.resource(
    name="api_events",
    write_disposition="append"
)
def load_events_incremental():
    last_date = dlt.sources.incremental(
        cursor_path="event_date",
        initial_value="2024-01-01"
    )

    # API endpoint with date filter
    response = requests.get(
        "https://api.example.com/events",
        params={
            "start_date": last_date.start_value,
            "end_date": datetime.now().isoformat()
        }
    )

    yield response.json()["events"]

pipeline = dlt.pipeline(
    pipeline_name="events_incremental",
    destination="snowflake",
    dataset_name="events"
)

load_info = pipeline.run([load_events_incremental()])
```

## Incremental by ID (Auto-Increment)

### Track Last Processed ID

```python
import dlt

@dlt.resource(
    name="transactions",
    write_disposition="append",
    primary_key="transaction_id"
)
def load_transactions_incremental():
    last_id = dlt.sources.incremental(
        cursor_path="transaction_id",
        initial_value=0
    )

    # Fetch records with ID > last_id
    transactions = fetch_transactions_after(last_id.start_value)

    yield transactions

pipeline = dlt.pipeline(
    pipeline_name="transactions_incremental",
    destination="bigquery",
    dataset_name="finance"
)

load_info = pipeline.run([load_transactions_incremental()])
```

## Incremental with Merge (Upsert)

### Handle Updates and Deletes

```python
import dlt

@dlt.resource(
    name="products",
    write_disposition="merge",  # Upsert mode
    primary_key="product_id",
    merge_key="updated_at"  # Track changes by timestamp
)
def load_products_incremental():
    last_updated = dlt.sources.incremental(
        cursor_path="updated_at",
        initial_value="2024-01-01"
    )

    from sqlalchemy import create_engine
    engine = create_engine("mysql+pymysql://user:password@localhost:3306/db")

    query = f"""
    SELECT * FROM products
    WHERE updated_at >= '{last_updated.start_value}'
    ORDER BY updated_at
    """

    with engine.connect() as conn:
        result = conn.execute(query)
        yield from result

pipeline = dlt.pipeline(
    pipeline_name="products_incremental",
    destination="postgres",
    dataset_name="catalog"
)

load_info = pipeline.run([load_products_incremental()])
```

### Soft Deletes with Merge

```python
import dlt

@dlt.resource(
    name="customers",
    write_disposition="merge",
    primary_key="customer_id"
)
def load_customers_with_deletes():
    last_updated = dlt.sources.incremental(
        cursor_path="updated_at",
        initial_value="2024-01-01"
    )

    # Fetch active and deleted records
    query = f"""
    SELECT
        customer_id,
        name,
        email,
        updated_at,
        is_deleted
    FROM customers
    WHERE updated_at >= '{last_updated.start_value}'
    ORDER BY updated_at
    """

    from sqlalchemy import create_engine
    engine = create_engine("postgresql://user:password@localhost:5432/db")

    with engine.connect() as conn:
        result = conn.execute(query)
        yield from result

pipeline = dlt.pipeline(
    pipeline_name="customers_with_deletes",
    destination="snowflake",
    dataset_name="crm"
)

load_info = pipeline.run([load_customers_with_deletes()])
```

## Incremental with Lookback Window

### Handle Late-Arriving Data

```python
import dlt
from datetime import datetime, timedelta

@dlt.resource(
    name="orders_with_lookback",
    write_disposition="merge",
    primary_key="order_id"
)
def load_orders_with_lookback():
    last_updated = dlt.sources.incremental(
        cursor_path="updated_at",
        initial_value="2024-01-01"
    )

    # Lookback 7 days to catch late updates
    lookback_start = (
        datetime.fromisoformat(last_updated.start_value) - timedelta(days=7)
    ).isoformat()

    query = f"""
    SELECT * FROM orders
    WHERE updated_at >= '{lookback_start}'
    ORDER BY updated_at
    """

    from sqlalchemy import create_engine
    engine = create_engine("postgresql://user:password@localhost:5432/db")

    with engine.connect() as conn:
        result = conn.execute(query)
        yield from result

pipeline = dlt.pipeline(
    pipeline_name="orders_lookback",
    destination="bigquery",
    dataset_name="sales"
)

load_info = pipeline.run([load_orders_with_lookback()])
```

## Nested Incremental (Parent-Child)

### Incremental Loading for Nested Resources

```python
import dlt

@dlt.resource(
    name="accounts",
    write_disposition="merge",
    primary_key="account_id"
)
def load_accounts_incremental():
    last_updated = dlt.sources.incremental(
        cursor_path="updated_at",
        initial_value="2024-01-01"
    )

    accounts = fetch_accounts_since(last_updated.start_value)
    yield accounts

@dlt.resource(
    name="account_transactions",
    write_disposition="append",
    primary_key="transaction_id"
)
def load_transactions_for_accounts(accounts):
    last_transaction_date = dlt.sources.incremental(
        cursor_path="transaction_date",
        initial_value="2024-01-01"
    )

    for account in accounts:
        transactions = fetch_transactions(
            account_id=account["account_id"],
            since=last_transaction_date.start_value
        )
        yield transactions

pipeline = dlt.pipeline(
    pipeline_name="accounts_incremental",
    destination="postgres",
    dataset_name="finance"
)

# Load both resources
accounts_data = load_accounts_incremental()
load_info = pipeline.run([
    accounts_data,
    load_transactions_for_accounts(accounts_data)
])
```

## State Management

### Check Current State

```python
import dlt

pipeline = dlt.pipeline(
    pipeline_name="my_pipeline",
    destination="duckdb",
    dataset_name="raw"
)

# View current incremental state
state = pipeline.state
print(state)

# Access specific resource state
orders_state = state.get("resources", {}).get("orders", {})
print(f"Last processed timestamp: {orders_state.get('incremental', {}).get('updated_at')}")
```

### Reset State

```python
# Drop state to force full refresh
pipeline.drop_state()
```

### Partial Reset

```python
# Reset state for specific resource
state = pipeline.state
if "resources" in state and "orders" in state["resources"]:
    del state["resources"]["orders"]
pipeline.sync_state()
```

## Advanced Patterns

### Multi-Field Incremental

```python
import dlt

@dlt.resource(
    name="events",
    write_disposition="append"
)
def load_events_multi_field():
    # Track by multiple fields
    last_date = dlt.sources.incremental(
        cursor_path="event_date",
        initial_value="2024-01-01"
    )

    last_id = dlt.sources.incremental(
        cursor_path="event_id",
        initial_value=0
    )

    # Fetch using both filters
    events = fetch_events(
        date_gte=last_date.start_value,
        id_gt=last_id.start_value
    )

    yield events
```

### Incremental with Deduplication

```python
import dlt

@dlt.resource(
    name="user_events",
    write_disposition="merge",
    primary_key="event_id",
    merge_key=["user_id", "event_timestamp"]
)
def load_deduplicated_events():
    last_timestamp = dlt.sources.incremental(
        cursor_path="event_timestamp",
        initial_value="2024-01-01"
    )

    # Fetch events
    events = fetch_events_since(last_timestamp.start_value)

    # dlt will deduplicate based on merge_key
    yield events

pipeline = dlt.pipeline(
    pipeline_name="deduplicated_events",
    destination="snowflake",
    dataset_name="events"
)

load_info = pipeline.run([load_deduplicated_events()])
```

## Monitoring Incremental Loads

```python
import dlt

pipeline = dlt.pipeline(
    pipeline_name="monitored_incremental",
    destination="postgres",
    dataset_name="raw"
)

load_info = pipeline.run([load_orders_incremental()])

# Check incremental metadata
print(f"Load info: {load_info}")
print(f"Loaded packages: {len(load_info.load_packages)}")

# Query state
state = pipeline.state
orders_state = state.get("resources", {}).get("orders", {})
print(f"Last cursor value: {orders_state.get('incremental', {})}")

# Verify loaded data
with pipeline.sql_client() as client:
    result = client.execute_sql("""
        SELECT
            COUNT(*) as total_rows,
            MAX(updated_at) as max_timestamp
        FROM orders
    """)
    print(f"Total rows: {result[0][0]}, Latest timestamp: {result[0][1]}")
```

## Best Practices

- BEST: Use `write_disposition="merge"` for updates/deletes
- BEST: Use `write_disposition="append"` for immutable events
- BEST: Add lookback windows for late-arriving data
- BEST: Always specify `primary_key` for merge operations
- BEST: Use indexed timestamp columns at source for fast queries
- BEST: Monitor state to detect stalled pipelines
- BEST: Test full refresh vs incremental results
- BEST: Handle edge cases (timezone conversions, null timestamps)
- BEST: Use `ORDER BY` on cursor field for consistent results
- BEST: Implement alerts for cursor value staleness
