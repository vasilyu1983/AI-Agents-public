# ClickHouse Replication Template

## Overview

High availability and replication setup for ClickHouse clusters.

## Replication Architecture

```text
┌─────────────────────────────────────────────────────────────┐
│                   ClickHouse Keeper                          │
│                 (Coordination Layer)                         │
│    ┌──────────┐  ┌──────────┐  ┌──────────┐                │
│    │ Keeper 1 │  │ Keeper 2 │  │ Keeper 3 │                │
│    └──────────┘  └──────────┘  └──────────┘                │
└───────────────────────┬─────────────────────────────────────┘
                        │
         ┌──────────────┼──────────────┐
         ▼              ▼              ▼
    ┌─────────┐    ┌─────────┐    ┌─────────┐
    │ Shard 1 │    │ Shard 2 │    │ Shard 3 │
    │ ┌─────┐ │    │ ┌─────┐ │    │ ┌─────┐ │
    │ │ R1  │ │    │ │ R1  │ │    │ │ R1  │ │
    │ └─────┘ │    │ └─────┘ │    │ └─────┘ │
    │ ┌─────┐ │    │ ┌─────┐ │    │ ┌─────┐ │
    │ │ R2  │ │    │ │ R2  │ │    │ │ R2  │ │
    │ └─────┘ │    │ └─────┘ │    │ └─────┘ │
    └─────────┘    └─────────┘    └─────────┘
```

---

## ClickHouse Keeper Setup

### Keeper Configuration

```xml
<!-- /etc/clickhouse-keeper/keeper_config.xml -->
<clickhouse>
    <logger>
        <level>information</level>
        <log>/var/log/clickhouse-keeper/clickhouse-keeper.log</log>
        <errorlog>/var/log/clickhouse-keeper/clickhouse-keeper.err.log</errorlog>
        <size>1000M</size>
        <count>3</count>
    </logger>

    <keeper_server>
        <tcp_port>2181</tcp_port>
        <server_id>1</server_id>  <!-- Unique per keeper -->

        <log_storage_path>/var/lib/clickhouse/coordination/log</log_storage_path>
        <snapshot_storage_path>/var/lib/clickhouse/coordination/snapshots</snapshot_storage_path>

        <coordination_settings>
            <operation_timeout_ms>10000</operation_timeout_ms>
            <session_timeout_ms>30000</session_timeout_ms>
            <raft_logs_level>warning</raft_logs_level>
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

### Docker Compose for Keeper

```yaml
# docker-compose-keeper.yml
version: '3.8'

services:
  keeper-01:
    image: clickhouse/clickhouse-keeper:24.3
    hostname: keeper-01
    volumes:
      - ./keeper-01/keeper_config.xml:/etc/clickhouse-keeper/keeper_config.xml
      - keeper-01-data:/var/lib/clickhouse
    ports:
      - "2181:2181"
      - "9234:9234"
    networks:
      - clickhouse-net

  keeper-02:
    image: clickhouse/clickhouse-keeper:24.3
    hostname: keeper-02
    volumes:
      - ./keeper-02/keeper_config.xml:/etc/clickhouse-keeper/keeper_config.xml
      - keeper-02-data:/var/lib/clickhouse
    ports:
      - "2182:2181"
    networks:
      - clickhouse-net

  keeper-03:
    image: clickhouse/clickhouse-keeper:24.3
    hostname: keeper-03
    volumes:
      - ./keeper-03/keeper_config.xml:/etc/clickhouse-keeper/keeper_config.xml
      - keeper-03-data:/var/lib/clickhouse
    ports:
      - "2183:2181"
    networks:
      - clickhouse-net

volumes:
  keeper-01-data:
  keeper-02-data:
  keeper-03-data:

networks:
  clickhouse-net:
    driver: bridge
```

---

## Cluster Configuration

### Remote Servers Config

```xml
<!-- /etc/clickhouse-server/config.d/cluster.xml -->
<clickhouse>
    <remote_servers>
        <analytics_cluster>
            <!-- Shard 1 with 2 replicas -->
            <shard>
                <internal_replication>true</internal_replication>
                <replica>
                    <host>clickhouse-01</host>
                    <port>9000</port>
                </replica>
                <replica>
                    <host>clickhouse-02</host>
                    <port>9000</port>
                </replica>
            </shard>
            <!-- Shard 2 with 2 replicas -->
            <shard>
                <internal_replication>true</internal_replication>
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

    <!-- Keeper connection -->
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
        <session_timeout_ms>30000</session_timeout_ms>
    </zookeeper>

    <!-- Macros for replica identification -->
    <macros>
        <cluster>analytics_cluster</cluster>
        <shard>01</shard>
        <replica>clickhouse-01</replica>
    </macros>
</clickhouse>
```

---

## ReplicatedMergeTree Tables

### Create Replicated Table

```sql
-- Create on each replica (table is synced automatically)
CREATE TABLE events ON CLUSTER analytics_cluster (
    event_id UUID,
    user_id UInt64,
    event_type LowCardinality(String),
    properties String,
    created_at DateTime
)
ENGINE = ReplicatedMergeTree(
    '/clickhouse/tables/{shard}/events',  -- ZK path
    '{replica}'                            -- Replica identifier
)
PARTITION BY toYYYYMM(created_at)
ORDER BY (user_id, created_at);
```

### Distributed Table

```sql
-- Create distributed table for queries across shards
CREATE TABLE events_distributed ON CLUSTER analytics_cluster
AS events
ENGINE = Distributed(
    analytics_cluster,   -- Cluster name
    default,             -- Database
    events,              -- Local table
    rand()               -- Sharding key (rand = round-robin)
);

-- Better: Shard by user_id for co-located queries
CREATE TABLE events_distributed ON CLUSTER analytics_cluster
AS events
ENGINE = Distributed(
    analytics_cluster,
    default,
    events,
    sipHash64(user_id)   -- Same user always on same shard
);
```

### Insert and Query

```sql
-- Insert via distributed table (auto-routes to shards)
INSERT INTO events_distributed VALUES (...);

-- Or insert directly to local table (faster, you manage routing)
INSERT INTO events VALUES (...);

-- Query via distributed table (merges results from all shards)
SELECT event_type, count()
FROM events_distributed
WHERE created_at >= '2024-01-01'
GROUP BY event_type;
```

---

## Replication Monitoring

### Check Replication Status

```sql
-- Replication lag
SELECT
    database,
    table,
    is_leader,
    total_replicas,
    active_replicas,
    queue_size,
    inserts_in_queue,
    merges_in_queue,
    log_max_index - log_pointer AS replication_lag
FROM system.replicas
ORDER BY replication_lag DESC;

-- Detailed replica info
SELECT *
FROM system.replicas
WHERE table = 'events';
```

### Check Keeper Status

```sql
-- Keeper connection
SELECT *
FROM system.zookeeper
WHERE path = '/clickhouse';

-- Keeper stats
SELECT *
FROM system.zookeeper_connection;
```

### Check Cluster Health

```sql
-- All cluster nodes
SELECT * FROM system.clusters;

-- Cluster errors
SELECT
    cluster,
    shard_num,
    replica_num,
    host_name,
    is_local,
    errors_count,
    slowdowns_count
FROM system.clusters
WHERE errors_count > 0 OR slowdowns_count > 0;
```

---

## Failover Handling

### Automatic Failover

```sql
-- ClickHouse auto-routes reads to healthy replicas
-- Configure in distributed table:

CREATE TABLE events_distributed ON CLUSTER analytics_cluster
AS events
ENGINE = Distributed(
    analytics_cluster,
    default,
    events,
    sipHash64(user_id)
)
SETTINGS
    -- Use first available replica
    load_balancing = 'first_or_random',
    -- Skip unavailable replicas
    skip_unavailable_shards = 1;
```

### Manual Recovery

```sql
-- Force sync from another replica
SYSTEM SYNC REPLICA events;

-- Restart replication queue
SYSTEM RESTART REPLICA events;

-- Drop and recreate replica (data loss on this node)
-- 1. Drop table
DROP TABLE events SYNC;

-- 2. Clear ZK path (be careful!)
-- Use clickhouse-client to delete ZK node

-- 3. Recreate table (will sync from other replica)
CREATE TABLE events ...
```

---

## Backup and Recovery

### Backup Strategy

```bash
# Using clickhouse-backup tool
# Install: https://github.com/Altinity/clickhouse-backup

# Create backup
clickhouse-backup create daily_backup

# Upload to S3
clickhouse-backup upload daily_backup

# List backups
clickhouse-backup list
```

### Configuration

```yaml
# /etc/clickhouse-backup/config.yml
general:
  remote_storage: s3
  backups_to_keep_local: 3
  backups_to_keep_remote: 30

clickhouse:
  host: localhost
  port: 9000
  username: admin
  password: "${CLICKHOUSE_PASSWORD}"

s3:
  bucket: clickhouse-backups
  region: us-east-1
  access_key: "${AWS_ACCESS_KEY}"
  secret_key: "${AWS_SECRET_KEY}"
```

### Restore

```bash
# Download backup
clickhouse-backup download daily_backup

# Restore specific tables
clickhouse-backup restore daily_backup --table events

# Full restore
clickhouse-backup restore daily_backup
```

---

## Best Practices

### DO

1. **Use odd number of Keepers** - 3 or 5 for quorum
2. **Enable internal_replication** - ClickHouse handles replication
3. **Shard by query patterns** - Co-locate related data
4. **Monitor replication lag** - Alert on high lag
5. **Test failover regularly** - Know recovery time

### DON'T

1. **Don't use single Keeper** - No fault tolerance
2. **Don't ignore replication errors** - Data inconsistency risk
3. **Don't shard by rand()** - Unless truly random access
4. **Don't skip backups** - Even with replication
5. **Don't mix Keeper and ZooKeeper** - Choose one

---

## Scaling Operations

### Add Shard

```xml
<!-- Add new shard to cluster config -->
<shard>
    <internal_replication>true</internal_replication>
    <replica>
        <host>clickhouse-05</host>
        <port>9000</port>
    </replica>
    <replica>
        <host>clickhouse-06</host>
        <port>9000</port>
    </replica>
</shard>
```

```sql
-- Create tables on new shard
CREATE TABLE events ON CLUSTER analytics_cluster ...

-- Rebalance data (manual)
-- Move partitions or re-insert data
```

### Add Replica

```xml
<!-- Add replica to existing shard -->
<replica>
    <host>clickhouse-07</host>
    <port>9000</port>
</replica>
```

```sql
-- Create table on new replica (auto-syncs)
CREATE TABLE events ...

-- Monitor sync progress
SELECT * FROM system.replicas WHERE table = 'events';
```
