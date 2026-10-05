# ClickHouse Replication and Sharding

Use when running ClickHouse with replicas and/or shards. Decide first whether you need sharding at all ([template-clickhouse-setup.md](template-clickhouse-setup.md#deployment-shape)). Replication buys availability; sharding buys capacity and costs distributed-query complexity.

## Keeper (Coordination)

- **Run 3 Keeper nodes** (tolerates 1 failure) or 5 (tolerates 2). An even count adds no fault tolerance, and a single node is a single point of failure for every replicated table.
- **Losing Keeper quorum makes replicated tables read-only:** inserts fail and `ALTER`/DDL hang, but `SELECT` keeps working. Alert on `system.replicas.is_readonly = 1`, not only on Keeper process health.
- In production, put Keeper on its own hosts or at least its own disks. Keeper is latency-sensitive to fsync, and a merge-heavy ClickHouse node on the same disk causes session timeouts that look like random read-only flaps.
- Choose ClickHouse Keeper or ZooKeeper, not both. Migrating between them is an offline, planned operation (converter tooling exists; follow the vendor migration guide).

## Replicated Tables

```sql
CREATE TABLE db.events ON CLUSTER analytics
( ... )
ENGINE = ReplicatedMergeTree('/clickhouse/tables/{shard}/{database}/{table}', '{replica}')
PARTITION BY toYYYYMM(created_at)
ORDER BY (tenant_id, created_at);
```

- The Keeper path must be unique per shard and per table. Two tables sharing a path silently become replicas of each other. The `{shard}`, `{replica}` macros, and `{database}/{table}` or `{uuid}`, prevent that; set macros correctly on every node.
- Re-creating a table at a path that still has metadata fails with "replica already exists". Use `DROP TABLE ... SYNC` so the Keeper metadata is removed before re-creating.
- What replicates: inserts, merges, and `ALTER`s including `DELETE`/`TRUNCATE`/`DROP PARTITION`. **Replication is not backup.** An accidental delete reaches every replica within seconds.

## Distributed Tables and Sharding Key

- Set `internal_replication = true` in the cluster config when the local tables are `Replicated*`. With `false`, the Distributed table writes to every replica *and* replication copies the data again.
- **Sharding key:** hash the entity you join or group by (`cityHash64(tenant_id)` or `sipHash64(user_id)`), so per-entity joins and `GROUP BY` run shard-local. `rand()` spreads load evenly but forces every join and distinct count across the network. Check skew: one huge tenant on a tenant-hash makes one hot shard.
- **Distributed inserts are asynchronous by default.** The initiating node queues data on local disk and acknowledges before shards have it. If that node dies, queued data is lost or delayed. Monitor `system.distribution_queue`. For durability either enable synchronous distributed inserts (the setting name has changed across versions; check your docs) or have the loader write directly to local tables on each shard with its own routing.
- `skip_unavailable_shards = 1` returns **partial results with no error**. Use it only for dashboards that explicitly tolerate incomplete answers, never for reports or reconciliation.

## Distributed DDL

`ON CLUSTER` DDL goes through a Keeper queue. If one node is down, the statement waits until `distributed_ddl_task_timeout` and then returns an error for the missing hosts, while the other nodes have already applied it. After any `ON CLUSTER` failure, check `system.distributed_ddl_queue` and confirm the schema is identical on every node before the next DDL.

## Scaling

- **Adding a replica:** create the table on the new node with the same path; it fetches all parts from peers. Plan for the network and disk load on the source replicas.
- **Adding a shard does not rebalance.** Existing data stays where it is and new data spreads by the sharding key, or by `weight`. To rebalance, re-insert partitions through the Distributed table into a new table, or move partitions deliberately. Budget this before promising "just add a node".

## Failure Runbook

| Symptom | Check | Action |
|---------|-------|--------|
| Replica read-only | `system.replicas.is_readonly`, Keeper connectivity (`system.zookeeper_connection`) | Restore Keeper quorum/network; the replica recovers its session. If Keeper metadata was lost, `SYSTEM RESTORE REPLICA` rebuilds it from local parts |
| Replica lagging | `absolute_delay`, `queue_size` in `system.replicas`; stuck entries with `last_exception` in `system.replication_queue` | Fix the root cause shown in `last_exception` (disk full, missing part, memory). `SYSTEM SYNC REPLICA` waits for catch-up; it does not repair |
| Replica diverged or broken | Parts count differs from peers; detached parts in `system.detached_parts` | Rebuild the replica: `DROP TABLE ... SYNC` on that node only, then re-create; it refetches from healthy peers. Never clear Keeper paths by hand while peers are alive |
| Inserts rejected cluster-wide | "Too many parts" | Part-count problem, not replication; see [template-clickhouse-ingestion.md](template-clickhouse-ingestion.md#part-count-and-insert-batching) |

## Backup and Restore

- Back up independently of replication: native `BACKUP ... TO` object storage, or a dedicated backup tool. Keep backups in a different account or bucket from the cluster's own credentials.
- Retention follows the recovery point you promised. Rebuilding from the lake is also a valid recovery path for gold tables, if it has been timed.
- **A backup you have not restored is a hope.** Restore one table into a scratch database on a schedule and compare row counts and checksums with production.

## Verify

- Stop one Keeper node: inserts still succeed. Stop two of three: replicas go read-only and alerts fire.
- Stop one replica per shard: queries through the Distributed table still return complete results, with `skip_unavailable_shards` off.
- Every node shows the same `create_table_query` for each replicated table.
- The last restore test is recent and its duration fits the recovery time objective.
