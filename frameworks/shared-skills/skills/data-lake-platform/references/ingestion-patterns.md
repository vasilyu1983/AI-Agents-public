# Data Ingestion Patterns

Choose ingestion around replay safety, delete handling, and operational ownership.

## Table of Contents

- [Tool Selection](#tool-selection)
- [CDC Decision Guide](#cdc-decision-guide)
- [AI-Assisted Pipeline Creation](#ai-assisted-pipeline-creation)
- [dlt Patterns](#dlt-patterns)
- [Basic Pipeline](#basic-pipeline)
- [Incremental Loading](#incremental-loading)
- [REST API Source](#rest-api-source)
- [Destination Example](#destination-example)
- [Airbyte Patterns](#airbyte-patterns)
- [Connection Configuration](#connection-configuration)
- [Debezium + Kafka](#debezium-kafka)
- [Flink CDC](#flink-cdc)
- [Incremental Loading Strategies](#incremental-loading-strategies)
- [Timestamp-based](#timestamp-based)
- [ID-based](#id-based)
- [Cursor-based](#cursor-based)
- [Full refresh with dedup](#full-refresh-with-dedup)
- [Operational Rules](#operational-rules)
- [Best Practices](#best-practices)

## Tool Selection

| Path | Best for | Strengths | Watch-outs |
|------|----------|-----------|------------|
| dlt | Python-led ingestion and AI-assisted development | Code-first, incremental patterns, easy review | You own runtime and connector logic |
| Airbyte | Large connector catalog and UI-driven operations | Managed connector breadth, low-code flows | Validate CDC semantics and maintenance overhead |
| Debezium + Kafka | Durable CDC event backbone | Strong database CDC patterns, replay via Kafka | Higher platform complexity |
| Flink CDC | Streaming-first CDC into mutable lakehouse tables | Tight fit with Flink and Paimon/Hudi patterns | Requires stronger stream-processing discipline |
| Batch APIs/files | Small systems or simple SLAs | Lowest complexity | Weakest freshness and delete semantics |

## CDC Decision Guide

```text
Need durable CDC log for many consumers?
    -> Debezium + Kafka

Need code-first ingestion owned by Python team?
    -> dlt first

Need broad connector catalog and UI operations?
    -> Airbyte first

Need streaming-first, Flink-native CDC into mutable tables?
    -> Flink CDC first

Need simple low-frequency sync with weak mutation pressure?
    -> batch incremental load may be enough
```

## AI-Assisted Pipeline Creation

AI tools are useful for scaffolding connectors and configs, but treat generated ingestion code as untrusted until it passes replay, backfill, and delete-handling tests.

**Do**

- Start from verified source templates.
- Review pagination, cursor logic, and retry behavior.
- Test with small datasets and known edge cases first.
- Keep generated code in version control.

**Avoid**

- Trusting generated auth or CDC logic without review.
- Deploying without replay tests.
- Assuming "incremental" covers deletes, tombstones, or late-arriving updates.

## dlt Patterns

Use dlt when the team wants code-first ingestion with readable Python and explicit review.

### Basic Pipeline

```python
import dlt

@dlt.source
def my_source():
    @dlt.resource(write_disposition="merge", primary_key="id")
    def users():
        for page in paginate_api("/users"):
            yield page

    return users

pipeline = dlt.pipeline(
    pipeline_name="my_pipeline",
    destination="clickhouse",
    dataset_name="raw"
)
pipeline.run(my_source())
```

### Incremental Loading

```python
@dlt.resource(
    write_disposition="merge",
    primary_key="id"
)
def orders(
    updated_at=dlt.sources.incremental("updated_at", initial_value="2024-01-01")
):
    for page in api.get_orders(since=updated_at.last_value):
        yield page
```

### REST API Source

```python
from dlt.sources.rest_api import rest_api_source

config = {
    "client": {
        "base_url": "https://api.example.com/v1",
        "auth": {"type": "bearer", "token": dlt.secrets["api_token"]}
    },
    "resources": [
        {
            "name": "users",
            "endpoint": {"path": "users", "paginator": "json_link"},
            "write_disposition": "merge",
            "primary_key": "id"
        }
    ]
}

source = rest_api_source(config)
```

### Destination Example

```python
pipeline = dlt.pipeline(
    pipeline_name="to_clickhouse",
    destination=dlt.destinations.clickhouse(
        credentials="clickhouse://user:pass@host:9000/db"
    ),
    dataset_name="raw"
)

pipeline.run(
    source,
    table_format="iceberg",
    loader_file_format="parquet"
)
```

## Airbyte Patterns

Use Airbyte when connector coverage and UI-driven operation matter more than code-level control.

### Connection Configuration

```yaml
sourceDefinitionId: postgres
destinationDefinitionId: clickhouse

source:
  host: source-db.example.com
  port: 5432
  database: production
  username: ${POSTGRES_USER}
  password: ${POSTGRES_PASSWORD}
  replication_method:
    method: CDC
    publication: airbyte_publication
    replication_slot: airbyte_slot

destination:
  host: clickhouse.example.com
  port: 8443
  database: raw
  username: ${CLICKHOUSE_USER}
  password: ${CLICKHOUSE_PASSWORD}
  ssl: true
```

## Debezium + Kafka

Use this path when CDC must be durable, replayable, and available to multiple downstream consumers.

```yaml
{
  "name": "postgres-connector",
  "config": {
    "connector.class": "io.debezium.connector.postgresql.PostgresConnector",
    "database.hostname": "postgres",
    "database.port": "5432",
    "database.user": "debezium",
    "database.password": "${DEBEZIUM_PASSWORD}",
    "database.dbname": "production",
    "database.server.name": "prod",
    "table.include.list": "public.users,public.orders",
    "plugin.name": "pgoutput",
    "slot.name": "debezium_slot",
    "publication.name": "debezium_publication"
  }
}
```

Use it when:

- more than one downstream system needs the CDC stream
- replay from a durable log is operationally important
- delete and late-event handling must be explicit

## Flink CDC

Use Flink CDC when the architecture is streaming-first and the target tables are mutable or changelog-oriented.

Good fit:

- Flink is already a core platform skill
- Paimon or Hudi is the target table layer
- low-latency propagation matters more than batch simplicity

Operational requirements:

- explicit checkpointing and savepoint policy
- sink idempotency
- delete and schema-change handling
- backfill and bootstrap plan

## Incremental Loading Strategies

### Timestamp-based

```python
@dlt.resource(write_disposition="merge", primary_key="id")
def orders(updated_at=dlt.sources.incremental("updated_at")):
    yield from api.get_orders(since=updated_at.last_value)
```

### ID-based

```python
@dlt.resource(write_disposition="append")
def events(last_id=dlt.sources.incremental("id", initial_value=0)):
    yield from api.get_events(after_id=last_id.last_value)
```

### Cursor-based

```python
@dlt.resource
def items(cursor=dlt.sources.incremental("cursor")):
    while True:
        response = api.get_items(cursor=cursor.last_value)
        yield response["items"]
        if not response.get("next_cursor"):
            break
        cursor.last_value = response["next_cursor"]
```

### Full refresh with dedup

```python
@dlt.resource(write_disposition="replace")
def config_table():
    yield from api.get_all_config()
```

## Operational Rules

Every ingestion design should answer these before rollout:

1. What is the replay source of truth: raw files, Kafka log, source database, or snapshots?
2. How are deletes represented and propagated?
3. What is the schema-change policy: additive only, reviewed widening, or contract-gated?
4. What is the bootstrap and backfill path?
5. What is the lag SLO and how is it monitored?

## Best Practices

1. Pick CDC tooling based on replay and delete semantics, not only setup convenience.
2. Treat checkpoints, cursors, and offsets as production state.
3. Make backfill and bootstrap procedures explicit before launch.
4. Enforce schema contracts before writes reach trusted layers.
5. Prefer one ingestion standard per team unless a second path solves a clear constraint.
