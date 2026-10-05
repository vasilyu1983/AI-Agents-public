```markdown
# High Availability & Disaster Recovery (HA/DR) Template

*Purpose: A complete operational template for designing, validating, and executing high-availability (HA) and disaster recovery (DR) strategies across infrastructure, applications, Kubernetes clusters, and databases.*

---

# 1. Overview

**System / Service Name:**  
[name]

**Environment:**  
- [ ] dev  
- [ ] staging  
- [ ] prod  
- [ ] multi-region  

**DR Tier:**  
- [ ] Tier 0 (mission critical)  
- [ ] Tier 1 (critical)  
- [ ] Tier 2 (important)  
- [ ] Tier 3 (non-critical)  

**Owner:**  
[Team/Engineer]

**Last DR Test:**  
[date]

---

# 2. Business Continuity Objectives

## 2.1 RTO (Recovery Time Objective)
```

Service must be fully restored within <N> minutes/hours after outage.

```

## 2.2 RPO (Recovery Point Objective)
```

Data loss must not exceed <N> minutes/hours.

```

Checklist:
- [ ] RTO < service tolerance  
- [ ] RPO aligned with backup/replication frequency  
- [ ] Business impact documented  

---

# 3. HA Architecture

## 3.1 Redundancy Model

- [ ] Multi-AZ  
- [ ] Multi-region  
- [ ] Active/active  
- [ ] Active/passive  
- [ ] N+1 redundancy  
- [ ] Self-healing Kubernetes workloads  
- [ ] DNS/LB-based failover  

## 3.2 HA Component Map  
(List each infra component)

| Component | HA Method | Notes |
|-----------|-----------|--------|
| API Service | Multi-AZ + HPA | |
| Database | Multi-AZ failover | |
| Storage | Replicated volumes | |
| Load Balancer | Multi-region | |

---

# 4. DR Architecture

## 4.1 DR Regions & Replication

| Region | Role | Replication Type | Notes |
|--------|-------|-------------------|--------|
| us-east-1 | primary | async/sync | |
| us-west-2 | failover | async | |

## 4.2 Replication Patterns

- **Synchronous replication:** zero data loss, higher latency  
- **Asynchronous replication:** low latency, possible data loss  
- **Log shipping:** WAL/binlog streaming  
- **Object storage replication:** S3/GCS cross-region  
- **Snapshot replication:** scheduled recovery points  

---

# 5. Backup & Restore Strategy

## 5.1 Backup Types

- [ ] Full backup (daily)  
- [ ] Incremental backups  
- [ ] WAL/Binlog streaming  
- [ ] Snapshot backups  
- [ ] Application-level backups  

## 5.2 Backup Locations

- [ ] Offsite region  
- [ ] Cross-account replication  
- [ ] Encrypted storage  
- [ ] Immutable/Write-once (WORM) backup  

## 5.3 Restore Procedures

```

1. Fetch backup artifact
2. Restore into isolated environment
3. Replay logs to target time (PITR)
4. Validate data integrity
5. Promote to primary if needed

```

Checklist:
- [ ] Restore tested recently  
- [ ] PITR validated  
- [ ] Backups encrypted  
- [ ] Access restrictions in place  

---

# 6. Failover Procedures

## 6.1 Application-Level Failover

```

1. Detect primary region outage
2. Freeze deploys
3. Shift traffic to standby
4. Update DNS/global load balancer
5. Validate service health
6. Notify on-call and engineering

```

Checklist:
- [ ] Failover < RTO  
- [ ] DR region warmed and ready  
- [ ] Secrets/configs replicated  
- [ ] Observability validated after failover  

---

## 6.2 Kubernetes Failover

### Option A — Multi-Cluster Active/Active

- [ ] Traffic split between clusters  
- [ ] Global load balancer configured  
- [ ] Shared service mesh (Istio/Linkerd)  
- [ ] Cross-region secrets sync  

### Option B — Active/Passive (DR cluster)

Failover steps:
```

1. Ensure cluster API available
2. Sync manifests via GitOps
3. Scale up workloads
4. Redirect traffic
5. Validate pods/services

```

Checklist:
- [ ] CI/CD supports region-aware deployments  
- [ ] etcd backups configured  
- [ ] Cluster version parity maintained  

---

## 6.3 Database Failover

### Automatic (recommended when safe)

- [ ] Synchronous commit for Tier 0  
- [ ] Health-based promotion  
- [ ] Application retries configured  

### Manual Failover

```

1. Promote replica
2. Repoint application connections
3. Rebuild old primary as replica

```

Checklist:
- [ ] Failover tested  
- [ ] Application uses retry logic  
- [ ] Read/write separation considered  

---

# 7. DR Test Procedure

## 7.1 Test Types

- [ ] Full failover drill  
- [ ] Partial component failure  
- [ ] Network cut test  
- [ ] Backup restore test  
- [ ] Data corruption simulation  
- [ ] Chaos test (pod/node failure)  

## 7.2 Standard DR Drill Template

```

1. Announce test
2. Disable production alerts
3. Trigger failover or restore
4. Measure time to recovery
5. Validate application behavior
6. Evaluate data correctness
7. Restore normal topology
8. Document results

```

Checklist:
- [ ] Test performed in isolated environment  
- [ ] Monitoring enabled  
- [ ] Logs collected  
- [ ] Action items created  

---

# 8. Resilience Engineering

## 8.1 Failure Scenarios

- [ ] Region outage  
- [ ] AZ failure  
- [ ] Network partition  
- [ ] Data corruption  
- [ ] DNS outage  
- [ ] Load balancer failure  
- [ ] Secrets manager outage  
- [ ] Container registry outage  

## 8.2 Mitigation Patterns

- [ ] Retry with exponential backoff  
- [ ] Circuit breakers  
- [ ] Timeouts  
- [ ] Bulkheads  
- [ ] Fallback logic  
- [ ] Idempotent operations  

---

# 9. Post-Failover Verification

## 9.1 Infrastructure Health

- [ ] Pods healthy  
- [ ] Nodes stable  
- [ ] Autoscaling resumed  
- [ ] Load balancer routes correct  
- [ ] K8s controllers active  

## 9.2 Application Health

- [ ] p95/p99 latency normal  
- [ ] Error rate stable  
- [ ] Background jobs operational  
- [ ] No data loss detected  

## 9.3 Data Validation

- [ ] Schema matches primary  
- [ ] Row counts match  
- [ ] Referential integrity intact  
- [ ] No orphaned data  

---

# 10. DR Readiness Checklist

### Must-Haves

- [ ] Backups tested quarterly  
- [ ] PITR validated  
- [ ] Failover scripts documented  
- [ ] DR cluster/region ready  
- [ ] Observability active in DR region  
- [ ] Secrets synchronized  
- [ ] Config stored in Git  
- [ ] Environment parity validated  
- [ ] RTO/RPO targets monitored  

### Nice-to-Have

- [ ] Automated failover  
- [ ] Self-healing K8s cluster  
- [ ] Multi-region service mesh  
- [ ] DB proxy with auto-retry  

---

# 11. Completed Example

**Service:** User Accounts API  
**RTO:** 15 minutes  
**RPO:** 5 minutes  
**Primary Region:** us-east-1  
**DR Region:** us-west-2  
**DB Replication:** Async cross-region  
**Cluster:** EKS multi-cluster active/passive  

**Last DR Drill Outcome:**  
- Failover time: 11 minutes  
- Data loss: 0 minutes (WAL replay successful)  
- Issues: Missing environment variable sync  
- Fixes: Implement secrets replication via SOPS + GitOps  

---

# END
```
