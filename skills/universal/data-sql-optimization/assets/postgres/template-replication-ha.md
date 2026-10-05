# SQL Replication & High Availability Template

*Purpose: A production-ready template for diagnosing replication lag, evaluating high availability posture, planning failover, and documenting replica rebuild or resync procedures.*

---

## 1. Overview

**Database:**
- [ ] Postgres
- [ ] MySQL
- [ ] MariaDB
- [ ] Other: ___________

**Environment:**
- [ ] Production
- [ ] Staging
- [ ] DR region
- [ ] Read replica cluster

**Type of Issue / Task:**
- [ ] Replication lag investigation
- [ ] Replica rebuild
- [ ] Failover planning
- [ ] Failover execution
- [ ] HA readiness assessment
- [ ] Sync/async configuration review
- [ ] Backup-based replica provisioning
- [ ] Cross-region replication

**Severity:**
- [ ] P0 – Production at risk
- [ ] P1 – Partial degradation
- [ ] P2 – Non-critical
- [ ] P3 – Maintenance

---

## 2. Replication Topology Summary

### 2.1 Architecture

- Primary Node: ____________________
- Replica(s): ________________________
- Replication Mode:
  - [ ] Asynchronous
  - [ ] Synchronous
  - [ ] Semi-synchronous
  - [ ] Logical
  - [ ] Physical

### 2.2 Workload Notes

- Write volume:
- Read volume:
- Transaction size patterns:
- Cross-region latency:

---

### 2.3 Topology Review — Discouraged Shapes and Capacity Rules

*The topology and capacity reasoning below is adapted from Botros & Tinley, High Performance MySQL, 4th ed. (O'Reilly, 2021), Ch. 9. The rules are engine-independent — they follow from single-writer replication and from failover capacity arithmetic, not from anything MySQL-specific — but the mechanics are restated for PostgreSQL. Two topologies cover nearly every use case: a single primary with a small number of passive standbys, and a single primary with a read-replica pool. Everything below is a deviation to justify or avoid.*

#### Discouraged topologies checklist

Tick any that describe the current or proposed topology. Each is a finding, not a neutral observation.

- [ ] **Bidirectional / multi-master writes** (two nodes each replicating to the other, writes accepted on both). In PostgreSQL this means logical replication in both directions, or an external multi-master layer — physical streaming replication cannot do it, which is itself a signal. The source's verdict on the MySQL equivalent applies unchanged: "Active/active is very difficult to do correctly." Routing writes by even/odd hash keeps read-after-write consistent per row, but "queries that include rows that are canonical on the other side may not be consistent." The capacity trap is the same: "each server is the other server's replica and the most likely target of the failover. You have to plan your capacity in a way that ensures that when you shift traffic from one side to the other, you do not run out of CPU" — and after failover the node serves a working set it has not cached, so shared buffers churn while the new hot set is faulted in. Verdict quoted: "Take our advice and stay away from this one... You'll end up introducing data inconsistencies into the application and always be on edge that you don't have enough capacity to failover. Once you lose your failover strategy, you've lost resilience."
- [ ] **Preconfigured reverse replication from standby back to primary.** Harmless on the surface but pointless: it differs from a plain primary/standby pair only in that the reverse direction is already wired, and "This only works in a two-server configuration. If you run more than two servers, you'll need to decide which node is the best target for a failover. Preconfiguring replication only ties you directly to one and doesn't give you flexibility in an outage situation." Reattaching a demoted primary is a scripted failover step (`pg_rewind` plus re-following); precommitting to one direction is "an unnecessary configuration that only invites confusion."
- [ ] **Ring / circular replication** (three or more nodes, each replicating from the one before and to the one after). "If any server in this topology goes offline, your topology is broken and updates stop flowing around the ring." Attached-replica variants still leave the ring broken until a node is promoted into the gap. Verdict quoted: "This topology is the opposite of simple and has no advantages."
- [ ] **Multi-source aggregation as a permanent topology.** PostgreSQL logical replication can subscribe one node to several publishers — legitimate as a temporary tool for merging two clusters and cutting over, but a permanent design built around it inherits ambiguous write ownership and conflict handling. Treat a standing multi-publisher subscriber as a finding: "We cite it as discouraged only in the case where you build a permanent topology around this concept."
- [ ] **Writes accepted on more than one node.** Stated as a flat rule: "Do not try to write to multiple servers in a replication topology at the same time... The most practical replication topology is to use one source, taking all your writes, and one or more replicas, optionally taking reads." In PostgreSQL, enforce this structurally — standbys are physically read-only, but a logical-replication subscriber is *not*, so a subscriber that also takes application writes is exactly the failure this rule prohibits.

**Star and cascade topology notes.** A single primary fanning out to many standbys is the recommended shape, not a discouraged one. PostgreSQL additionally supports *cascading* replication (a standby feeding further standbys), which is a legitimate way to limit WAL-sender load on the primary and to keep a remote-region tree behind one WAN link — but each hop adds lag and, on failover, every downstream node must be re-pointed. Whichever shape you pick, pool size is an operational cost, not just a capacity number: "A 16-node pool will mean that you have to do kernel updates or security patching 16 times. Automating this task to gracefully depool a node, perform patching, reboot, and repool will reduce the amount of work you do by hand in the future."

#### Capacity rules

- [ ] **n+2 redundancy on physical hardware.** Quoted: "In a physical hardware environment, you really want n+2 redundancy for at least three total servers. In the event of a hardware failure, you still have one additional server for failover. You can also use one of the replicas as a backup server if you are uncomfortable or unable to take backups on your source." In PostgreSQL the backup-offload point is concrete: run `pg_basebackup` or pgBackRest against a standby rather than the primary.
- [ ] **n+1 acceptable in cloud, conditionally.** Quoted: "In a cloud environment, you can get away with n+1 redundancy for two total servers if your data is small enough or you can copy the data easily. Otherwise, n+2 is needed." If you take n+1, lean on dynamic provisioning for maintenance: provision a third standby on demand, patch it, replace the other standby, fail over, repeat on the former primary. "The goal is to keep a replica ready to be the target of a failover at all times."
- [ ] **Failover targets must match the primary's configuration.** The passive-standby model assumes "the source and replicas are identical configurations in terms of CPU, memory, and so forth" so you can "sustain the traffic capacity and throughput as before you failed over." In a read pool, keep "at least one, preferably two" replicas at primary-equivalent spec — and match `shared_buffers` and `work_mem` too, not just cores and RAM, or the promoted node plans and caches differently under production load. Mixed-spec pools should be traffic-weighted: "If you have 32 cores for the failover targets and 8 cores for other replicas, try to send four times more traffic to the 32-core node to ensure you get utilization."
- [ ] **50–60% CPU utilization ceiling per read-pool node.** Quoted: "With reads, your most likely indicator of utilization will be CPU, and as such, target somewhere between 50%–60% utilization per node in the pool. As CPU increases, it spends more time context switching between work and latency increases. Try to find the right balance between latency and utilization that meets your application expectations." This is a headroom rule, not a target to drive toward — the gap absorbs failover load and node failures. On PostgreSQL, remember standby CPU also serves WAL replay, which is single-threaded for the startup process: a node at 60% from queries can still fall behind on replay.

Current per-node read CPU: __________  |  Redundancy level (n+_): __________

#### Synchronous replication caveat (the PostgreSQL analogue)

MySQL's semisynchronous replication carries a well-known trap: on acknowledgment timeout "MySQL reverts to its standard asynchronous replication. It will not fail the transaction," which means "semisynchronous replication is not a tool to prevent data loss but rather a building block for a larger set of tooling that allows you to have more resilient failover."

**PostgreSQL's synchronous replication does not degrade this way — and that inversion is the thing to design for.** With `synchronous_commit = on` and a `synchronous_standby_names` list, a commit *waits* rather than silently downgrading: if no standby in the list can acknowledge, committing sessions block indefinitely. Postgres trades MySQL's silent data-loss risk for an availability risk. Both are failure modes; you must pick which one you are accepting and say so.

Record the decision here:

- [ ] `synchronous_commit` = ____________ (`off` / `local` / `remote_write` / `on` / `remote_apply`)
- [ ] `synchronous_standby_names` = ____________ (note the quorum form, e.g. `ANY 1 (s1, s2)`, vs. `FIRST`)
- [ ] If synchronous: what happens when the quorum is unreachable — does the application block, and for how long before an operator intervenes? Is there an agreed runbook for dropping to async under a declared incident?
- [ ] If asynchronous: what is the actual RPO, measured as replay lag under peak write load, not as a configured value?
- [ ] Beware the middle settings. `remote_write` acknowledges once the standby's OS has the WAL but before `fsync`; `remote_apply` waits for replay and is the only level that guarantees a read on that standby sees the committed write. Do not describe `on` as "no data loss on any failure" — it means the WAL is flushed on a standby, not applied.
- [ ] A standby listed in `synchronous_standby_names` is a capacity dependency as well as a durability one — if it saturates, primary commit latency rises. Do not put a synchronous standby behind a WAN link without measuring the added commit latency.

---

## 3. Replication Lag Investigation

### 3.1 Postgres Metrics

Run:
```

SELECT now() - pg_last_xact_replay_timestamp() AS replication_lag;

```

Additional:
- `pg_stat_wal_receiver`
- `pg_stat_replication` on primary
- Replay location vs flush location differences

### 3.2 MySQL Metrics

Run:
```

SHOW SLAVE STATUS\G;

```

Check:
- `Seconds_Behind_Master`
- `Relay_Log_Space`
- `Executed_Gtid_Set` vs `Retrieved_Gtid_Set`
- `Slave_IO_Running` / `Slave_SQL_Running`

---

### 3.3 Lag Diagnostics Checklist

- [ ] High write volume spike
- [ ] Long-running transactions on replica
- [ ] Network latency issues
- [ ] Disk I/O saturation
- [ ] WAL/binlog generation spike
- [ ] Replica SQL thread bottleneck
- [ ] Huge autovacuum (Postgres)
- [ ] Replica using slow storage
- [ ] Large batch updates on primary

**Notes:**
[Describe findings]

---

## 4. Root Cause Hypotheses

Select all relevant:

- [ ] Replica I/O too slow
- [ ] Large WAL/binlog burst from bulk ops
- [ ] Long transaction blocking WAL replay
- [ ] Vacuum freeze on replica
- [ ] Write amplification (too many indexes)
- [ ] Network bandwidth issue
- [ ] Replica CPU saturated
- [ ] Disk queue depth high
- [ ] Misconfigured sync settings

**Primary Suspect:**
[Describe]

---

## 5. Fix Patterns

### 5.1 Immediate Actions

- [ ] Throttle writes on primary
- [ ] Reduce large batch sizes
- [ ] Pause heavy migrations
- [ ] Stop read-intensive analytic jobs on replicas
- [ ] Restart WAL receiver / replication threads
- [ ] Increase network throughput
- [ ] Move replica to faster storage

---

### 5.2 Durable Long-Term Fixes

Postgres:
- Tune `max_wal_size`
- Tune `checkpoint_completion_target`
- Enable synchronous replication only when required
- Add more replicas for read scaling
- Reduce index count on write-heavy tables

MySQL:
- Enable parallel replication
- Tune replica SQL thread concurrency
- Reduce row-based binlog amplification
- Add appropriate covering indexes

---

## 6. Replica Rebuild Procedure

### 6.1 When to Rebuild

Rebuild a replica if:
- [ ] Replica is too far behind
- [ ] Replica has corruption or missing WAL/binlogs
- [ ] GTID set divergence
- [ ] Disk failure
- [ ] Version mismatch after upgrade
- [ ] Logical replication misalignment

---

### 6.2 Postgres Rebuild (Physical)

```

SELECT pg_terminate_backend(pid)
FROM pg_stat_replication
WHERE application_name='<replica_name>';

```

Then on replica:
```

rm -rf $PGDATA/*
pg_basebackup -h <primary> -D $PGDATA -U replicator -P -R

```

Restart:
```

systemctl restart postgresql

```

---

### 6.3 MySQL Rebuild (GTID)

1. Stop replica:
```

STOP SLAVE;

```
2. Drop data directory:
```

rm -rf /var/lib/mysql/*

```
3. Restore full backup:
```

xtrabackup --prepare
xtrabackup --copy-back

```
4. Reset and connect:
```

RESET SLAVE ALL;
CHANGE MASTER TO MASTER_HOST='...', MASTER_AUTO_POSITION=1;
START SLAVE;

```

---

## 7. HA (High Availability) Evaluation

### 7.1 Failover Requirements

- [ ] RTO target documented
- [ ] RPO target documented
- [ ] Synchronous replication required?
- [ ] Multi-AZ or multi-region required?
- [ ] Automated failover enabled?
- [ ] Stonith / fencing (if cluster-based)

### 7.2 Readiness Checklist

- [ ] Replicas healthy
- [ ] Replication lag < defined threshold
- [ ] Primary CPU/I/O below safety threshold
- [ ] WAL/binlog retention safe
- [ ] Backup tested
- [ ] Application connection retries configured

---

## 8. Failover Plan

### 8.1 Failover Type

- [ ] Manual
- [ ] Semi-automatic
- [ ] Fully automatic (patroni/repmgr/Orchestrator/ProxySQL)

### 8.2 Manual Failover Steps Example (Postgres)

1. Promote replica:
```

pg_ctl promote

```
2. Update connection strings
3. Reconfigure load balancer
4. Rebuild old primary as new replica

---

### 8.3 Manual Failover Steps Example (MySQL)

1. `STOP SLAVE;` on failing node
2. Promote replica:
```

RESET SLAVE ALL;

```
3. Update application configs
4. Point other replicas to new primary:
```

CHANGE MASTER TO MASTER_HOST='<new primary>';

```

---

## 9. Post-Failover Verification

### 9.1 Functional

- [ ] Application can read/write
- [ ] No stale replicas
- [ ] GTID/WAL positions correct

### 9.2 Performance

- [ ] Query latency normal
- [ ] CPU/I/O within thresholds
- [ ] No lock pile-ups

### 9.3 Consistency

- [ ] Data divergence check
- [ ] Row count validation
- [ ] Index structure validated
- [ ] Spot-check key business queries

---

## 10. DR (Disaster Recovery) Status

### 10.1 PITR Capability
- [ ] WAL/binlog archived
- [ ] PITR tested in last 6 months

### 10.2 Region Failure Simulation
- [ ] Replica in second region
- [ ] Network isolation test
- [ ] Restore-from-backup test
- [ ] Failover tested end-to-end

---

## 11. Final Notes

[Add any lessons learned, diagrams, improvements, or scheduled tasks.]

---

## 12. Completed Example

**Issue:** Replication lag > 45 minutes on Postgres.

**Root Cause:** Large UPDATE batch + replica on slow disk.

**Fixes:**
- Throttled writes
- Rebuilt replica using `pg_basebackup`
- Moved to faster NVMe storage
- Enabled monitoring for WAL spikes

**Post-Fix Lag:** < 500ms steady.

---

# END
