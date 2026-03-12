# Airbyte Connection Template

## Overview

Setting up Airbyte connectors for data ingestion.

## Quick Setup

### Docker Compose

```bash
# Clone Airbyte
git clone https://github.com/airbytehq/airbyte.git
cd airbyte

# Start Airbyte
./run-ab-platform.sh

# Access UI: http://localhost:8000
# Default: airbyte / password
```

### Kubernetes (Helm)

```bash
helm repo add airbyte https://airbytehq.github.io/helm-charts
helm install airbyte airbyte/airbyte -n airbyte --create-namespace
```

---

## Connection Configuration

### Source: PostgreSQL

```yaml
# Terraform / API config
source:
  name: "postgres-source"
  sourceDefinitionId: "decd338e-5647-4c0b-adf4-da0e75f5a750"
  connectionConfiguration:
    host: "postgres.example.com"
    port: 5432
    database: "production"
    username: "${POSTGRES_USER}"
    password: "${POSTGRES_PASSWORD}"
    schemas: ["public"]
    ssl_mode:
      mode: "require"
    replication_method:
      method: "CDC"
      plugin: "pgoutput"
      publication: "airbyte_publication"
      replication_slot: "airbyte_slot"
```

### Source: REST API

```yaml
source:
  name: "api-source"
  sourceDefinitionId: "dfd88b22-b603-4c3d-aad7-3701784586b1"
  connectionConfiguration:
    api_url: "https://api.example.com"
    authentication:
      type: "Bearer"
      api_token: "${API_TOKEN}"
    pagination:
      type: "CursorPagination"
      cursor_value: "{{ response.next_cursor }}"
```

### Destination: ClickHouse

```yaml
destination:
  name: "clickhouse-dest"
  destinationDefinitionId: "ce0d828e-1dc4-496c-b122-2da42e637e48"
  connectionConfiguration:
    host: "clickhouse.example.com"
    port: 8123
    database: "bronze"
    username: "${CLICKHOUSE_USER}"
    password: "${CLICKHOUSE_PASSWORD}"
    ssl: true
    raw_data_schema: "_airbyte_raw"
```

### Destination: S3 (Data Lake)

```yaml
destination:
  name: "s3-dest"
  destinationDefinitionId: "4816b78f-1489-44c1-9060-4b19d5fa9362"
  connectionConfiguration:
    s3_bucket_name: "data-lake-bronze"
    s3_bucket_path: "airbyte/${SOURCE_NAME}"
    s3_bucket_region: "us-east-1"
    format:
      format_type: "Parquet"
      compression_codec: "ZSTD"
    access_key_id: "${AWS_ACCESS_KEY}"
    secret_access_key: "${AWS_SECRET_KEY}"
```

---

## Connection Settings

### Sync Configuration

```yaml
connection:
  name: "postgres-to-clickhouse"
  sourceId: "source-uuid"
  destinationId: "destination-uuid"

  # Sync mode
  syncCatalog:
    streams:
      - stream:
          name: "users"
          namespace: "public"
        config:
          syncMode: "incremental"
          destinationSyncMode: "append_dedup"
          cursorField: ["updated_at"]
          primaryKey: [["id"]]

      - stream:
          name: "events"
          namespace: "public"
        config:
          syncMode: "incremental"
          destinationSyncMode: "append"
          cursorField: ["created_at"]

  # Schedule
  scheduleType: "cron"
  scheduleData:
    cron:
      cronExpression: "0 */6 * * *"  # Every 6 hours
      cronTimeZone: "UTC"

  # Normalization
  normalizationOperation: "basic"

  # Resource requirements
  resourceRequirements:
    cpu_request: "1"
    cpu_limit: "2"
    memory_request: "1Gi"
    memory_limit: "2Gi"
```

### Sync Modes

| Source Mode | Destination Mode | Use Case |
|-------------|-----------------|----------|
| `full_refresh` | `overwrite` | Small tables, complete refresh |
| `full_refresh` | `append` | Snapshots, audit trails |
| `incremental` | `append` | Event logs, immutable data |
| `incremental` | `append_dedup` | Upserts, mutable data |

---

## API Usage

### Create Connection (Python)

```python
import requests

AIRBYTE_URL = "http://localhost:8000/api/v1"

# Create source
source_response = requests.post(
    f"{AIRBYTE_URL}/sources/create",
    json={
        "sourceDefinitionId": "decd338e-5647-4c0b-adf4-da0e75f5a750",
        "workspaceId": "workspace-uuid",
        "name": "postgres-source",
        "connectionConfiguration": {
            "host": "postgres.example.com",
            "port": 5432,
            "database": "production",
            "username": "airbyte",
            "password": "secret"
        }
    }
)

# Create destination
dest_response = requests.post(
    f"{AIRBYTE_URL}/destinations/create",
    json={
        "destinationDefinitionId": "ce0d828e-1dc4-496c-b122-2da42e637e48",
        "workspaceId": "workspace-uuid",
        "name": "clickhouse-dest",
        "connectionConfiguration": {
            "host": "clickhouse.example.com",
            "port": 8123,
            "database": "bronze"
        }
    }
)

# Create connection
conn_response = requests.post(
    f"{AIRBYTE_URL}/connections/create",
    json={
        "sourceId": source_response.json()["sourceId"],
        "destinationId": dest_response.json()["destinationId"],
        "syncCatalog": {...},
        "scheduleType": "cron",
        "scheduleData": {
            "cron": {
                "cronExpression": "0 */6 * * *",
                "cronTimeZone": "UTC"
            }
        }
    }
)
```

### Trigger Sync

```python
# Manual sync trigger
requests.post(
    f"{AIRBYTE_URL}/connections/sync",
    json={"connectionId": "connection-uuid"}
)

# Check sync status
status = requests.post(
    f"{AIRBYTE_URL}/jobs/get",
    json={"id": job_id}
)
```

---

## Terraform

```hcl
# provider.tf
terraform {
  required_providers {
    airbyte = {
      source  = "airbytehq/airbyte"
      version = "~> 0.3"
    }
  }
}

provider "airbyte" {
  server_url = "http://localhost:8000/api/public/v1"
  username   = var.airbyte_username
  password   = var.airbyte_password
}

# source.tf
resource "airbyte_source_postgres" "postgres" {
  name          = "postgres-source"
  workspace_id  = airbyte_workspace.main.workspace_id

  configuration = {
    host     = "postgres.example.com"
    port     = 5432
    database = "production"
    username = var.postgres_username
    password = var.postgres_password
    schemas  = ["public"]
  }
}

# destination.tf
resource "airbyte_destination_clickhouse" "clickhouse" {
  name          = "clickhouse-dest"
  workspace_id  = airbyte_workspace.main.workspace_id

  configuration = {
    host     = "clickhouse.example.com"
    port     = 8123
    database = "bronze"
    username = var.clickhouse_username
    password = var.clickhouse_password
  }
}

# connection.tf
resource "airbyte_connection" "postgres_to_clickhouse" {
  name           = "postgres-to-clickhouse"
  source_id      = airbyte_source_postgres.postgres.source_id
  destination_id = airbyte_destination_clickhouse.clickhouse.destination_id

  schedule = {
    schedule_type = "cron"
    cron_expression = "0 */6 * * *"
  }
}
```

---

## Monitoring

### Check Sync Status

```python
def get_sync_status(connection_id):
    response = requests.post(
        f"{AIRBYTE_URL}/jobs/list",
        json={
            "configTypes": ["sync"],
            "configId": connection_id
        }
    )

    jobs = response.json()["jobs"]
    if jobs:
        latest = jobs[0]
        return {
            "status": latest["job"]["status"],
            "started_at": latest["job"]["createdAt"],
            "bytes_synced": latest["attempts"][-1].get("bytesSynced"),
            "records_synced": latest["attempts"][-1].get("recordsSynced")
        }
```

### Alerts

```yaml
# Prometheus alerts
groups:
  - name: airbyte
    rules:
      - alert: AirbyteSyncFailed
        expr: airbyte_job_status{status="failed"} > 0
        for: 5m
        labels:
          severity: critical

      - alert: AirbyteSyncStale
        expr: time() - airbyte_last_successful_sync_timestamp > 86400
        for: 1h
        labels:
          severity: warning
```

---

## Best Practices

1. **Use CDC for databases** - Lower latency, less load
2. **Set appropriate schedules** - Based on data freshness needs
3. **Configure resource limits** - Prevent memory issues
4. **Enable normalization** - For structured destination tables
5. **Monitor sync durations** - Alert on anomalies
6. **Use secrets management** - Never hardcode credentials
