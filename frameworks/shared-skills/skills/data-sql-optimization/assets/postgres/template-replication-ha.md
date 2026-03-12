```markdown
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
```
