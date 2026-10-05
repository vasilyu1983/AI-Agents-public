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

*Source: Botros & Tinley, High Performance MySQL, 4th ed. (O'Reilly, 2021), Ch. 9. Two topologies cover nearly every use case: active/passive (all reads and writes to one source, a small number of passive replicas) and active/read pool (writes to the source, reads spread across a replica pool). Everything below is a deviation to justify or avoid.*

#### Discouraged topologies checklist

Tick any that describe the current or proposed topology. Each is a finding, not a neutral observation.

- [ ] **Dual source in active-active mode** (bidirectional replication, writes to both sides). The book: "Active/active is very difficult to do correctly." Even/odd-hash write routing keeps read-after-write consistent per row, but "queries that include rows that are canonical on the other side may not be consistent" — a query spanning IDs 1–6 has no correct side to go to. Capacity is the second trap: "each server is the other server's replica and the most likely target of the failover. You have to plan your capacity in a way that ensures that when you shift traffic from one side to the other, you do not run out of CPU," and failover introduces a different working set so "the InnoDB buffer pool now churns, removing entries to make room for the new hot set of data." Verdict quoted: "Take our advice and stay away from this one... You'll end up introducing data inconsistencies into the application and always be on edge that you don't have enough capacity to failover. Once you lose your failover strategy, you've lost resilience."
- [ ] **Dual source in active-passive mode** (one side read-only). Not dangerous, just pointless — it differs from plain active/passive only in that reverse replication is preconfigured, and "This only works in a two-server configuration. If you run more than two servers, you'll need to decide which node is the best target for a failover. Preconfiguring replication only ties you directly to one and doesn't give you flexibility in an outage situation." Setting up replication is an automatable failover step; this is "an unnecessary configuration that only invites confusion."
- [ ] **Dual sources with replicas.** Resolves the capacity and buffer-pool-churn concerns but "maintains most of the problems with dual source in active-active, the most important being how you route traffic," and adds failover steps. "Cosources only lead to trouble."
- [ ] **Ring / circular replication** (three or more sources, each a replica of the one before and source of the one after). "If any server in this topology goes offline, your topology is broken and updates stop flowing around the ring." Attached-replica variants still leave the ring broken until a replica is promoted into the gap. Verdict quoted: "This topology is the opposite of simple and has no advantages."
- [ ] **Multisource replication as a permanent topology.** Legitimate as a temporary tool — merging two clusters into one via replication channels, then cutting over — but "We cite it as discouraged only in the case where you build a permanent topology around this concept." Known limitation: "you cannot configure a replica to use multisource replication multiple times against the same source."
- [ ] **Writes to more than one server in the topology.** Stated as a flat rule: "Do not try to write to multiple servers in a replication topology at the same time. This includes using cosources with writes on both sides or ring replication. The most practical replication topology is to use one source, taking all your writes, and one or more replicas, optionally taking reads."

**Star topology note.** A single source fanning out to many replicas is the recommended shape, not a discouraged one — but read-pool size is an operational cost, not just a capacity number: "A 16-node pool will mean that you have to do kernel updates or security patching 16 times. Automating this task to gracefully depool a node, perform patching, reboot, and repool will reduce the amount of work you do by hand in the future."

#### Capacity rules

- [ ] **n+2 redundancy on physical hardware.** Quoted: "In a physical hardware environment, you really want n+2 redundancy for at least three total servers. In the event of a hardware failure, you still have one additional server for failover. You can also use one of the replicas as a backup server if you are uncomfortable or unable to take backups on your source."
- [ ] **n+1 acceptable in cloud, conditionally.** Quoted: "In a cloud environment, you can get away with n+1 redundancy for two total servers if your data is small enough or you can copy the data easily. Otherwise, n+2 is needed." If you take n+1, lean on dynamic provisioning for maintenance: provision a third replica on demand, patch it, replace the other replica, fail over, repeat on the former source. "The goal is to keep a replica ready to be the target of a failover at all times."
- [ ] **Failover targets must match the source's configuration.** Active/passive assumes "the source and replicas are identical configurations in terms of CPU, memory, and so forth" so you can "sustain the traffic capacity and throughput as before you failed over." In a read pool, keep "at least one, preferably two" replicas at source-equivalent spec. Mixed-spec pools should be traffic-weighted: "If you have 32 cores for the failover targets and 8 cores for other replicas, try to send four times more traffic to the 32-core node to ensure you get utilization."
- [ ] **50–60% CPU utilization ceiling per read-pool node.** Quoted: "With reads, your most likely indicator of utilization will be CPU, and as such, target somewhere between 50%–60% utilization per node in the pool. As CPU increases, it spends more time context switching between work and latency increases. Try to find the right balance between latency and utilization that meets your application expectations." This is a headroom rule, not a target to drive toward — the gap absorbs failover load and node failures.

Current per-node read CPU: __________  |  Redundancy level (n+_): __________

#### Semisynchronous replication caveat

If `rpl_semi_sync` is enabled anywhere in this topology, record why. Semisync means every committed transaction "must be acknowledged as received by at least one replica" — acknowledging receipt into the relay log, "but not necessarily applied it to the local data" — and adds latency to every transaction.

**The failure mode that matters: it degrades to asynchronous silently.** Quoted: "if no replicas acknowledge the transaction during the time frame, MySQL reverts to its standard asynchronous replication. It will not fail the transaction. This really helps illustrate that semisynchronous replication is not a tool to prevent data loss but rather a building block for a larger set of tooling that allows you to have more resilient failover."

So the intuitive use case does not hold: you might expect semisync to stop a network-partitioned source from accepting writes its replicas never saw, but "that source will just revert back to asynchronous and keep accepting writes." The book's position: "we'd recommend not relying on this for any data integrity." If semisync is part of your RPO story, that story has a hole in it — either back it with tooling that fences the source, or restate the RPO.

- [ ] Semisync enabled? If so, `rpl_semi_sync_source_wait_for_replica_count` = ______ (wider topologies may want 2–3 acknowledgments)
- [ ] Documented what happens on degrade-to-async, and whether the stated RPO survives it

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
