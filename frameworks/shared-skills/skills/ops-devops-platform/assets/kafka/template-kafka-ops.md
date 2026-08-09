```markdown
# Kafka Operations Template (DevOps)

*Purpose: A complete operational template for running, scaling, securing, monitoring, and troubleshooting Apache Kafka clusters, topics, partitions, consumers, and brokers.*

---

# 1. Overview

**Cluster / Environment:**  
- [ ] dev  
- [ ] staging  
- [ ] prod  
- [ ] multi-region  

**Kafka Distribution:**  
- [ ] Apache Kafka  
- [ ] Confluent  
- [ ] MSK (AWS Managed)  
- [ ] Strimzi / K8s operator  

**Purpose of Change / Task:**  
- [ ] Create topic  
- [ ] Update partitions  
- [ ] Add broker / scale cluster  
- [ ] Debug consumer lag  
- [ ] Fix under-replicated partitions  
- [ ] Rolling upgrade  
- [ ] ACL / security change  
- [ ] DR failover  

---

# 2. Kafka Topic Operations

## 2.1 Create Topic

```

kafka-topics.sh --create \
  --bootstrap-server <brokers> \
  --topic <name> \
  --partitions <N> \
  --replication-factor <R> \
  --config retention.ms=604800000

```

Checklist:
- [ ] Partitions sized for throughput  
- [ ] Replication factor ≥ 3 in prod  
- [ ] Retention policies set  
- [ ] Cleanup policy = compact / delete validated  
- [ ] Topic naming convention followed  

---

## 2.2 Update Topic Partitions

```

kafka-topics.sh --alter \
  --topic <name> \
  --partitions <new_count> \
  --bootstrap-server <brokers>

```

Checklist:
- [ ] Only increase allowed (never decrease)  
- [ ] Consumer group impact assessed  
- [ ] Rebalancing expected and monitored  

---

## 2.3 Retention Policies

```

retention.ms=604800000
cleanup.policy=delete

```

Checklist:
- [ ] Disk usage forecasted  
- [ ] Compaction required?  
- [ ] PII retention compliant?  

---

# 3. Consumer Group Operations

## 3.1 Check Consumer Lag

```

kafka-consumer-groups.sh \
  --bootstrap-server <brokers> \
  --describe \
  --group <group-id>

```

Checklist:
- [ ] Lag increasing?  
- [ ] Consumer offline?  
- [ ] Partition imbalance?  
- [ ] Slow or stuck consumers traced?  
- [ ] Application logs inspected?  

---

## 3.2 Reset Offsets (Safe)

**Dry run:**
```

kafka-consumer-groups.sh --reset-offsets \
  --to-earliest \
  --group <group> \
  --topic <topic> \
  --dry-run \
  --bootstrap-server <brokers>

```

**Apply:**
```

kafka-consumer-groups.sh --reset-offsets \
  --to-latest \
  --execute \
  --group <group> \
  --topic <topic> \
  --bootstrap-server <brokers>

```

Checklist:
- [ ] Confirm NO other consumers running  
- [ ] Confirm business impact of resetting  
- [ ] Confirm correct direction (earliest/latest/timestamp)  

---

# 4. Broker & Cluster Operations

## 4.1 Rolling Restart

```

systemctl stop kafka
systemctl start kafka

```

Checklist:
- [ ] One broker at a time  
- [ ] Controller stability monitored  
- [ ] No ISR shrinkage  
- [ ] Under-replicated partitions (URPs) = 0  

---

## 4.2 Add Broker to Cluster

Steps:
```

1. Provision node
2. Apply broker configs
3. Start broker
4. Rebalance partitions

```

Rebalance:
```

kafka-reassign-partitions.sh --execute --reassignment-json ...

```

Checklist:
- [ ] Disk/CPU/network sized  
- [ ] Inter-broker protocol version compatible  
- [ ] Auto-leader rebalance enabled  

---

## 4.3 Under-Replicated Partitions

Check:
```

kafka-topics.sh --describe --bootstrap-server <brokers>

```

Fix:
- [ ] Restart ISR follower  
- [ ] Verify network throughput  
- [ ] Reassign partition to healthy brokers  

---

# 5. Monitoring

## 5.1 Key Kafka Metrics (Prometheus / JMX)

### Broker
- UnderReplicatedPartitions  
- OfflinePartitions  
- ActiveControllerCount  
- ISR shrink count  
- RequestQueueSize  
- Network I/O  

### Consumer
- Consumer lag per partition  
- Commit latency  
- Rebalance activity  

### Producer
- Batch size  
- Request latency  
- Retries & errors  

Checklist:
- [ ] Alerts configured on URPs > 0  
- [ ] Alerts on controller election  
- [ ] Topic disk usage monitored  

---

# 6. Security & ACLs

## 6.1 Enable ACLs (if applicable)

```

kafka-acls.sh --add \
  --allow-principal User:<user> \
  --operation Read \
  --topic <topic>

```

Checklist:
- [ ] No anonymous access in prod  
- [ ] SASL/SSL enabled  
- [ ] Cert rotation procedure in place  
- [ ] Use least privilege ACLs  

---

# 7. Disaster Recovery (DR)

## 7.1 MirrorMaker 2 Setup

```

connect-mirror-maker.sh mm2.properties

```

Checklist:
- [ ] Inter-region connection stable  
- [ ] Topic whitelist/blacklist correct  
- [ ] Replication lag monitored  

---

## 7.2 Region Failover

```

1. Verify source cluster offline
2. Promote DR cluster
3. Repoint producers/consumers
4. Update DNS/env vars
5. Monitor consumer offsets

```

Checklist:
- [ ] DR tested quarterly  
- [ ] Retention mirrors business RPO  
- [ ] ACLs synced between regions  

---

# 8. Troubleshooting

## 8.1 Slow Consumers

- [ ] Check processing time  
- [ ] Check downstream DB latency  
- [ ] Scale horizontally  
- [ ] Increase partitions  

---

## 8.2 Producer Timeouts

- [ ] Network issues  
- [ ] Broker overloaded  
- [ ] Batch size too small  
- [ ] acks=all slows producers if RF low  

---

## 8.3 Rebalance Storms

- [ ] Consumer group session timeouts too low  
- [ ] Uneven partitions  
- [ ] Overloaded brokers  

---

# 9. Consumer Failure-Handling Contract

## 9.1 Contract-Level Change Recognition
- Retry topics + DLQ alter commit semantics even when public APIs stay the same — treat as a contract change, not an internal refactor.
- New failure-handling behavior must be explicitly opt-in (additive configuration or new registration path).
- Lock the backward-compatibility rule before implementation begins: preserve the public contract unless a breaking change is deliberately hidden behind an opt-in flag.

## 9.2 Cost and Schema Impact
- Extra partitions, write/read traffic, and retained bytes drive cost — not topic existence alone.
- Under a topic-based subject strategy, publishing the same payload to retry and DLQ topics multiplies schema subjects and versions.
- Prefer a shared retry/DLQ envelope or original-bytes-plus-metadata-headers approach to limit schema sprawl.

## 9.3 Exception Classification
- Classify non-retryable exceptions (validation errors, schema mismatches, poison messages) before the generic retry loop — otherwise the system repeats side effects and violates operator expectations.
- Treat `OperationCanceledException` as control flow (shutdown), not failure handling — do not swallow it inside the normal failure path.
- Consumer loops need an explicit shutdown path that exits cleanly before failure routing kicks in.

## 9.4 Failure Isolation
- A retry/DLQ publish failure must not silently kill the whole consumer task.
- Isolate failures to the affected partition: partition-scoped pause plus visible host-level faulting.
- For retry dispatch, pause only the affected retry partition rather than sleeping the entire loop.

## 9.5 Legacy Behavior Preservation
- New failure-handling modes must not break legacy shared-consumer or custom subscription extension points.
- Add dedicated regression coverage for shared-consumer composition and custom subscription registration whenever core consumer internals change.

## 9.6 Pre-Merge Checklist
- [ ] Backward compatibility is opt-in — legacy registration API behavior unchanged by default
- [ ] Cost impact assessed: extra partitions, traffic, retained bytes, schema subject count
- [ ] Non-retryable exceptions classified before retry loop entry
- [ ] Cancellation handled as shutdown control flow, not processing failure
- [ ] Failure isolation is partition-scoped, not whole-consumer
- [ ] Legacy shared fan-out and custom subscription regression tests pass
- [ ] Docs and ADRs updated in same delivery cycle (see Pattern 4 in `references/devops-best-practices.md`)

---

# 10. Final Checklist

- [ ] Topics configured correctly  
- [ ] Partition counts validated  
- [ ] Retention policies correct  
- [ ] ACLs enforced  
- [ ] Lag monitored  
- [ ] URPs = 0  
- [ ] DR working & tested  
- [ ] Cluster capacity within limits  

---

# END
```
