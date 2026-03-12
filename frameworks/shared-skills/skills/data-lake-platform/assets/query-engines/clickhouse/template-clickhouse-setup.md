# ClickHouse Setup Template

## Overview

Production-ready ClickHouse deployment for data lake analytics.

## Deployment Options

| Option | Best For | Complexity |
|--------|----------|------------|
| **Single node** | Development, <1TB | Low |
| **Cluster** | Production, scaling | Medium |
| **ClickHouse Cloud** | Managed, zero-ops | Low |
| **Kubernetes** | Cloud-native, elastic | High |

---

## Single Node Setup

### Docker Compose

```yaml
# docker-compose.yml
version: '3.8'

services:
  clickhouse:
    image: clickhouse/clickhouse-server:24.3
    container_name: clickhouse
    ports:
      - "8123:8123"   # HTTP
      - "9000:9000"   # Native
      - "9009:9009"   # Interserver
    volumes:
      - clickhouse_data:/var/lib/clickhouse
      - clickhouse_logs:/var/log/clickhouse-server
      - ./config/users.xml:/etc/clickhouse-server/users.d/users.xml
      - ./config/config.xml:/etc/clickhouse-server/config.d/config.xml
    environment:
      CLICKHOUSE_DB: analytics
      CLICKHOUSE_USER: admin
      CLICKHOUSE_PASSWORD: ${CLICKHOUSE_PASSWORD}
    ulimits:
      nofile:
        soft: 262144
        hard: 262144
    healthcheck:
      test: ["CMD", "clickhouse-client", "--query", "SELECT 1"]
      interval: 30s
      timeout: 10s
      retries: 3

volumes:
  clickhouse_data:
  clickhouse_logs:
```

### User Configuration

```xml
<!-- config/users.xml -->
<clickhouse>
    <users>
        <admin>
            <password_sha256_hex><!-- sha256 hash --></password_sha256_hex>
            <networks>
                <ip>::/0</ip>
            </networks>
            <profile>default</profile>
            <quota>default</quota>
            <access_management>1</access_management>
        </admin>
        <readonly>
            <password_sha256_hex><!-- sha256 hash --></password_sha256_hex>
            <networks>
                <ip>::/0</ip>
            </networks>
            <profile>readonly</profile>
            <quota>default</quota>
        </readonly>
    </users>

    <profiles>
        <default>
            <max_memory_usage>10000000000</max_memory_usage>
            <max_execution_time>300</max_execution_time>
        </default>
        <readonly>
            <readonly>1</readonly>
            <max_memory_usage>5000000000</max_memory_usage>
        </readonly>
    </profiles>
</clickhouse>
```

### Server Configuration

```xml
<!-- config/config.xml -->
<clickhouse>
    <logger>
        <level>information</level>
        <log>/var/log/clickhouse-server/clickhouse-server.log</log>
        <errorlog>/var/log/clickhouse-server/clickhouse-server.err.log</errorlog>
        <size>1000M</size>
        <count>10</count>
    </logger>

    <http_port>8123</http_port>
    <tcp_port>9000</tcp_port>

    <max_connections>4096</max_connections>
    <keep_alive_timeout>3</keep_alive_timeout>
    <max_concurrent_queries>100</max_concurrent_queries>

    <path>/var/lib/clickhouse/</path>
    <tmp_path>/var/lib/clickhouse/tmp/</tmp_path>

    <mark_cache_size>5368709120</mark_cache_size>

    <timezone>UTC</timezone>
</clickhouse>
```

---

## Cluster Setup

### 3-Node Cluster Architecture

```text
┌─────────────────────────────────────────────────────────┐
│                   ClickHouse Keeper                      │
│              (ZooKeeper alternative)                     │
│    ┌──────────┐  ┌──────────┐  ┌──────────┐           │
│    │ Keeper 1 │  │ Keeper 2 │  │ Keeper 3 │           │
│    └──────────┘  └──────────┘  └──────────┘           │
└─────────────────────────────────────────────────────────┘
                          │
        ┌─────────────────┼─────────────────┐
        ▼                 ▼                 ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│   Shard 1    │  │   Shard 2    │  │   Shard 3    │
│  ┌────────┐  │  │  ┌────────┐  │  │  ┌────────┐  │
│  │Replica1│  │  │  │Replica1│  │  │  │Replica1│  │
│  └────────┘  │  │  └────────┘  │  │  └────────┘  │
│  ┌────────┐  │  │  ┌────────┐  │  │  ┌────────┐  │
│  │Replica2│  │  │  │Replica2│  │  │  │Replica2│  │
│  └────────┘  │  │  └────────┘  │  │  └────────┘  │
└──────────────┘  └──────────────┘  └──────────────┘
```

### Cluster Configuration

```xml
<!-- config/cluster.xml -->
<clickhouse>
    <remote_servers>
        <analytics_cluster>
            <shard>
                <replica>
                    <host>clickhouse-01</host>
                    <port>9000</port>
                </replica>
                <replica>
                    <host>clickhouse-02</host>
                    <port>9000</port>
                </replica>
            </shard>
            <shard>
                <replica>
                    <host>clickhouse-03</host>
                    <port>9000</port>
                </replica>
                <replica>
                    <host>clickhouse-04</host>
                    <port>9000</port>
                </replica>
            </shard>
        </analytics_cluster>
    </remote_servers>

    <zookeeper>
        <node>
            <host>keeper-01</host>
            <port>2181</port>
        </node>
        <node>
            <host>keeper-02</host>
            <port>2181</port>
        </node>
        <node>
            <host>keeper-03</host>
            <port>2181</port>
        </node>
    </zookeeper>

    <macros>
        <cluster>analytics_cluster</cluster>
        <shard>01</shard>
        <replica>clickhouse-01</replica>
    </macros>
</clickhouse>
```

### ClickHouse Keeper Configuration

```xml
<!-- keeper_config.xml -->
<clickhouse>
    <keeper_server>
        <tcp_port>2181</tcp_port>
        <server_id>1</server_id>
        <log_storage_path>/var/lib/clickhouse/coordination/log</log_storage_path>
        <snapshot_storage_path>/var/lib/clickhouse/coordination/snapshots</snapshot_storage_path>

        <coordination_settings>
            <operation_timeout_ms>10000</operation_timeout_ms>
            <session_timeout_ms>30000</session_timeout_ms>
        </coordination_settings>

        <raft_configuration>
            <server>
                <id>1</id>
                <hostname>keeper-01</hostname>
                <port>9234</port>
            </server>
            <server>
                <id>2</id>
                <hostname>keeper-02</hostname>
                <port>9234</port>
            </server>
            <server>
                <id>3</id>
                <hostname>keeper-03</hostname>
                <port>9234</port>
            </server>
        </raft_configuration>
    </keeper_server>
</clickhouse>
```

---

## Kubernetes Deployment

### Helm Chart

```bash
# Add Altinity operator
helm repo add altinity https://charts.altinity.com
helm repo update

# Install ClickHouse operator
helm install clickhouse-operator altinity/clickhouse-operator

# Deploy cluster
kubectl apply -f clickhouse-cluster.yaml
```

### ClickHouse Cluster CRD

```yaml
# clickhouse-cluster.yaml
apiVersion: "clickhouse.altinity.com/v1"
kind: "ClickHouseInstallation"
metadata:
  name: "analytics"
spec:
  configuration:
    clusters:
      - name: "analytics"
        layout:
          shardsCount: 2
          replicasCount: 2
        templates:
          podTemplate: clickhouse-pod
          volumeClaimTemplate: storage

    users:
      admin/password_sha256_hex: "..."
      admin/networks/ip: "::/0"
      admin/profile: default
      admin/quota: default
      admin/access_management: 1

    profiles:
      default/max_memory_usage: 10000000000
      default/max_execution_time: 300

  templates:
    podTemplates:
      - name: clickhouse-pod
        spec:
          containers:
            - name: clickhouse
              image: clickhouse/clickhouse-server:24.3
              resources:
                requests:
                  memory: "8Gi"
                  cpu: "4"
                limits:
                  memory: "16Gi"
                  cpu: "8"

    volumeClaimTemplates:
      - name: storage
        spec:
          accessModes:
            - ReadWriteOnce
          resources:
            requests:
              storage: 100Gi
          storageClassName: fast-ssd
```

---

## Initial Database Setup

### Create Databases

```sql
-- Create analytics databases
CREATE DATABASE IF NOT EXISTS bronze;
CREATE DATABASE IF NOT EXISTS silver;
CREATE DATABASE IF NOT EXISTS gold;
CREATE DATABASE IF NOT EXISTS meta;

-- Set default database
USE gold;
```

### Create Initial Tables

```sql
-- Events table (example)
CREATE TABLE bronze.raw_events (
    _dlt_load_id String,
    _dlt_id String,
    _ingested_at DateTime DEFAULT now(),
    raw_data String
)
ENGINE = MergeTree()
PARTITION BY toYYYYMM(_ingested_at)
ORDER BY (_ingested_at, _dlt_id)
TTL _ingested_at + INTERVAL 2 YEAR;

-- Staging table
CREATE TABLE silver.stg_events (
    event_id UUID,
    user_id UInt64,
    event_type LowCardinality(String),
    properties String CODEC(ZSTD(3)),
    created_at DateTime,
    _loaded_at DateTime DEFAULT now()
)
ENGINE = ReplacingMergeTree(_loaded_at)
PARTITION BY toYYYYMM(created_at)
ORDER BY (user_id, created_at, event_id);

-- Fact table
CREATE TABLE gold.fct_daily_events (
    date Date,
    event_type LowCardinality(String),
    event_count UInt64,
    unique_users UInt64
)
ENGINE = SummingMergeTree()
PARTITION BY toYYYYMM(date)
ORDER BY (date, event_type);
```

---

## Connection Examples

### Python (clickhouse-connect)

```python
import clickhouse_connect

client = clickhouse_connect.get_client(
    host='localhost',
    port=8123,
    username='admin',
    password='password',
    database='gold'
)

# Query
result = client.query("SELECT * FROM fct_daily_events LIMIT 10")
print(result.result_rows)

# Insert
client.insert(
    'fct_daily_events',
    data=[[date.today(), 'click', 1000, 500]],
    column_names=['date', 'event_type', 'event_count', 'unique_users']
)
```

### dlt Destination

```python
import dlt

pipeline = dlt.pipeline(
    pipeline_name="to_clickhouse",
    destination="clickhouse",
    dataset_name="bronze"
)

# Configure in .dlt/secrets.toml
# [destination.clickhouse.credentials]
# host = "localhost"
# port = 8123
# username = "admin"
# password = "password"
# database = "analytics"
```

---

## Health Checks

```sql
-- Cluster health
SELECT * FROM system.clusters;

-- Replication status
SELECT
    database, table, is_leader, total_replicas, active_replicas
FROM system.replicas;

-- Disk usage
SELECT
    name,
    formatReadableSize(free_space) AS free,
    formatReadableSize(total_space) AS total
FROM system.disks;

-- Active queries
SELECT query_id, user, query, elapsed
FROM system.processes;
```
