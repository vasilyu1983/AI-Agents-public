# Disaster Recovery Testing

DR drill execution, RTO/RPO verification, and failover validation for production systems.

## Contents

- [DR Plan Components](#dr-plan-components)
- [Types of DR Tests](#types-of-dr-tests)
- [Database Failover Testing](#database-failover-testing)
- [Backup Verification](#backup-verification)
- [Multi-Region Failover](#multi-region-failover)
- [DNS Failover](#dns-failover)
- [Stateful Service Recovery](#stateful-service-recovery)
- [DR Test Scheduling](#dr-test-scheduling)
- [Runbook Validation](#runbook-validation)
- [Compliance Requirements](#compliance-requirements)
- [Post-Drill Report Template](#post-drill-report-template)
- [Related Resources](#related-resources)

---

## DR Plan Components

### RTO and RPO Definitions

| Metric | Definition                               | Measured From           |
|--------|------------------------------------------|-------------------------|
| **RTO** | Recovery Time Objective -- max acceptable downtime | Incident detection to service restoration |
| **RPO** | Recovery Point Objective -- max acceptable data loss | Last good backup/replica to failure point |

### Tiered Recovery Objectives

| Tier   | System Example          | RTO        | RPO       | Recovery Method         |
|--------|-------------------------|------------|-----------|-------------------------|
| Tier 0 | Payment processing      | < 1 min    | 0 (zero)  | Active-active multi-region |
| Tier 1 | User authentication     | < 15 min   | < 1 min   | Hot standby failover    |
| Tier 2 | Product catalog         | < 1 hour   | < 15 min  | Warm standby + replication |
| Tier 3 | Reporting, analytics    | < 4 hours  | < 1 hour  | Cold restore from backup |
| Tier 4 | Internal tools          | < 24 hours | < 24 hours| Manual restore          |

### DR Plan Document Structure

```text
1. SCOPE AND OBJECTIVES
   - Systems covered
   - RTO/RPO targets per tier
   - Responsible teams

2. CONTACT INFORMATION
   - Escalation chain
   - Vendor support contacts
   - Communication channels

3. RECOVERY PROCEDURES
   - Step-by-step per system tier
   - Decision trees for failure scenarios
   - Rollback procedures

4. DEPENDENCIES
   - Inter-service dependencies
   - Infrastructure requirements
   - Third-party service dependencies

5. TESTING SCHEDULE
   - Test frequency per tier
   - Success criteria
   - Reporting requirements
```

---

## Types of DR Tests

### Test Types Comparison

| Type           | Scope              | Risk  | Duration   | Frequency     |
|----------------|--------------------|-------|------------|---------------|
| **Tabletop**   | Discussion only    | None  | 1-2 hours  | Quarterly     |
| **Walkthrough**| Step-by-step review| None  | 2-4 hours  | Quarterly     |
| **Simulation** | Partial failover   | Low   | 4-8 hours  | Semi-annual   |
| **Full Failover** | Complete DR activation | Medium | 8-24 hours | Annual    |

### Tabletop Exercise

No actual systems are touched. Teams walk through scenarios verbally.

```text
TABLETOP SCENARIO: Primary database corruption

Facilitator reads:
"At 2:00 AM, the on-call engineer receives alerts that the primary
PostgreSQL database is returning corruption errors. Write queries are
failing. Read replicas are 30 seconds behind and may have replicated
corrupted data."

Discussion questions:
1. What is your first action?
2. How do you determine if replicas are safe?
3. What is the failover procedure?
4. How do you validate data integrity after failover?
5. What is the communication plan for affected users?
```

### Simulation Test

Trigger partial failover in a controlled environment.

```bash
#!/bin/bash
# DR simulation: database primary failover

set -euo pipefail

DR_LOG="/var/log/dr-drill-$(date +%Y%m%d).log"
START_TIME=$(date +%s)

log() { echo "[$(date -u +%H:%M:%S)] $1" | tee -a "$DR_LOG"; }

log "=== DR DRILL START: Database Failover Simulation ==="

# Step 1: Verify pre-conditions
log "Checking replication lag..."
LAG=$(psql -h replica.internal -c \
  "SELECT EXTRACT(EPOCH FROM replay_lag) FROM pg_stat_replication;" -t)
if (( $(echo "$LAG > 5" | bc -l) )); then
  log "ABORT: Replication lag ${LAG}s exceeds threshold"
  exit 1
fi

# Step 2: Record baseline metrics
log "Recording baseline..."
BASELINE_QPS=$(curl -s http://metrics.internal/api/v1/query?query=rate\(http_requests_total[1m]\) \
  | jq '.data.result[0].value[1]' -r)
log "Baseline QPS: $BASELINE_QPS"

# Step 3: Promote replica
log "Promoting replica to primary..."
pg_ctl promote -D /var/lib/postgresql/data

# Step 4: Update DNS / connection string
log "Updating service discovery..."
consul kv put db/primary/host replica.internal

# Step 5: Validate
log "Validating write capability on new primary..."
psql -h replica.internal -c \
  "INSERT INTO dr_validation (tested_at) VALUES (NOW());"

# Step 6: Measure recovery time
END_TIME=$(date +%s)
RECOVERY_SECONDS=$((END_TIME - START_TIME))
log "Recovery time: ${RECOVERY_SECONDS}s"

# Step 7: Verify RTO
RTO_TARGET=900  # 15 minutes
if [ "$RECOVERY_SECONDS" -le "$RTO_TARGET" ]; then
  log "PASS: RTO ${RECOVERY_SECONDS}s <= target ${RTO_TARGET}s"
else
  log "FAIL: RTO ${RECOVERY_SECONDS}s > target ${RTO_TARGET}s"
fi

log "=== DR DRILL COMPLETE ==="
```

---

## Database Failover Testing

### Primary-Replica Promotion

```bash
# PostgreSQL: verify replication status before failover
psql -h primary.internal -c "
  SELECT
    client_addr,
    state,
    sent_lsn,
    write_lsn,
    flush_lsn,
    replay_lsn,
    replay_lag
  FROM pg_stat_replication;
"

# Promote replica
pg_ctl promote -D /var/lib/postgresql/data

# Verify new primary accepts writes
psql -h new-primary.internal -c "
  CREATE TABLE IF NOT EXISTS dr_test (id SERIAL, ts TIMESTAMPTZ DEFAULT NOW());
  INSERT INTO dr_test DEFAULT VALUES;
  SELECT * FROM dr_test ORDER BY ts DESC LIMIT 1;
"
```

### Cross-Region Database Failover

| Step | Action                              | Validation                     | Rollback               |
|------|-------------------------------------|--------------------------------|------------------------|
| 1    | Verify replica lag < RPO            | `SELECT replay_lag`            | Abort if lag too high  |
| 2    | Stop writes to primary              | Drain connections              | Re-enable primary      |
| 3    | Wait for replica to catch up        | LSN comparison                 | --                     |
| 4    | Promote replica in DR region        | Write test query               | Demote and re-sync     |
| 5    | Update DNS/service discovery        | Health check returns healthy   | Revert DNS             |
| 6    | Verify application connectivity     | End-to-end transaction         | Rollback application   |
| 7    | Monitor for 15 minutes              | Error rates, latency           | Full rollback          |

---

## Backup Verification

### Restore Testing

Backups that are never tested are not backups. Run restore tests on every backup type.

```bash
#!/bin/bash
# Automated backup restore verification

BACKUP_FILE="s3://backups/db/daily/2025-01-15.sql.gz"
TEST_DB="dr_restore_test_$(date +%Y%m%d)"

log "Downloading backup..."
aws s3 cp "$BACKUP_FILE" /tmp/restore.sql.gz

log "Restoring to test database..."
createdb "$TEST_DB"
gunzip -c /tmp/restore.sql.gz | psql "$TEST_DB"

log "Running integrity checks..."

# Row count comparison
EXPECTED_USERS=50000
ACTUAL_USERS=$(psql "$TEST_DB" -t -c "SELECT COUNT(*) FROM users;")
if [ "$ACTUAL_USERS" -lt "$EXPECTED_USERS" ]; then
  log "FAIL: Expected >= $EXPECTED_USERS users, got $ACTUAL_USERS"
fi

# Schema validation
EXPECTED_TABLES=42
ACTUAL_TABLES=$(psql "$TEST_DB" -t -c \
  "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='public';")
if [ "$ACTUAL_TABLES" -ne "$EXPECTED_TABLES" ]; then
  log "FAIL: Expected $EXPECTED_TABLES tables, got $ACTUAL_TABLES"
fi

# Foreign key integrity
FK_VIOLATIONS=$(psql "$TEST_DB" -t -c "
  SELECT COUNT(*) FROM orders o
  LEFT JOIN users u ON o.user_id = u.id
  WHERE u.id IS NULL;
")
if [ "$FK_VIOLATIONS" -gt 0 ]; then
  log "FAIL: $FK_VIOLATIONS orphaned order records"
fi

# Cleanup
dropdb "$TEST_DB"
rm /tmp/restore.sql.gz

log "Restore verification complete."
```

### Data Integrity Checklist

- [ ] Backup file can be downloaded from storage
- [ ] Backup file is not corrupted (checksum verification)
- [ ] Restore completes without errors
- [ ] Row counts match expected values (within RPO window)
- [ ] Schema matches production (tables, indexes, constraints)
- [ ] Foreign key relationships are intact
- [ ] Application can connect and perform basic operations
- [ ] Point-in-time recovery (PITR) works to a specific timestamp

---

## Multi-Region Failover

### Active-Passive Failover Pattern

```text
Normal Operation:
  Users → DNS (us-east-1) → Primary Region
                             └── DB Primary
                             └── App Servers (active)

  Standby: us-west-2 (warm, receiving replication)

Failover:
  Users → DNS (us-west-2) → DR Region
                             └── DB Replica (promoted)
                             └── App Servers (activated)
```

### Failover Orchestration Script

```python
import boto3
import time

class RegionFailover:
    """Orchestrate multi-region failover."""

    def __init__(self, primary_region: str, dr_region: str):
        self.primary = primary_region
        self.dr = dr_region
        self.route53 = boto3.client("route53")
        self.rds = boto3.client("rds", region_name=dr_region)

    def execute_failover(self, hosted_zone_id: str, record_name: str):
        steps = [
            ("Verify DR health", self.verify_dr_health),
            ("Promote DR database", self.promote_dr_database),
            ("Scale up DR compute", self.scale_dr_compute),
            ("Update DNS", lambda: self.update_dns(hosted_zone_id, record_name)),
            ("Validate end-to-end", self.validate_e2e),
        ]

        for step_name, step_fn in steps:
            print(f"[{time.strftime('%H:%M:%S')}] {step_name}...")
            try:
                step_fn()
                print(f"  -> OK")
            except Exception as e:
                print(f"  -> FAILED: {e}")
                raise FailoverAborted(f"Failed at: {step_name}")

    def promote_dr_database(self):
        self.rds.promote_read_replica_db_cluster(
            DBClusterIdentifier="dr-cluster"
        )
        waiter = self.rds.get_waiter("db_cluster_available")
        waiter.wait(
            DBClusterIdentifier="dr-cluster",
            WaiterConfig={"Delay": 10, "MaxAttempts": 60},
        )

    def update_dns(self, hosted_zone_id: str, record_name: str):
        self.route53.change_resource_record_sets(
            HostedZoneId=hosted_zone_id,
            ChangeBatch={
                "Changes": [{
                    "Action": "UPSERT",
                    "ResourceRecordSet": {
                        "Name": record_name,
                        "Type": "CNAME",
                        "TTL": 60,
                        "ResourceRecords": [
                            {"Value": f"app.{self.dr}.internal"},
                        ],
                    },
                }],
            },
        )
```

---

## DNS Failover

### TTL Considerations

| TTL Value | Trade-off                                          |
|-----------|----------------------------------------------------|
| 30s       | Fast failover, high DNS query volume               |
| 60s       | Good balance for most services                     |
| 300s      | Slower failover, lower DNS cost                    |
| 3600s     | Unsuitable for DR -- 1 hour stale resolution       |

**Rule:** DR-critical records should have TTL <= 60 seconds.

### Health Check Configuration

```bash
# AWS Route 53 health check (CLI)
aws route53 create-health-check --caller-reference "dr-$(date +%s)" \
  --health-check-config '{
    "IPAddress": "203.0.113.10",
    "Port": 443,
    "Type": "HTTPS",
    "ResourcePath": "/health",
    "RequestInterval": 10,
    "FailureThreshold": 3,
    "EnableSNI": true
  }'
```

---

## Stateful Service Recovery

### Recovery Priority Order

```text
1. DNS / Load Balancers (stateless, fast)
2. Databases (stateful, promote replicas)
3. Message Queues (drain or replay)
4. Cache Layer (cold start acceptable)
5. Application Servers (stateless, scale up)
6. Background Workers (restart, reprocess)
```

### Message Queue Recovery

```python
# Kafka: verify consumer group lag after failover
from confluent_kafka.admin import AdminClient

admin = AdminClient({"bootstrap.servers": "dr-kafka:9092"})

def check_consumer_lag(group_id: str, max_lag: int = 10000):
    """Verify consumer group is catching up after DR failover."""
    groups = admin.list_consumer_group_offsets([group_id])
    total_lag = 0

    for topic_partition, offset_and_metadata in groups[group_id].result().items():
        watermarks = consumer.get_watermark_offsets(topic_partition)
        high_watermark = watermarks[1]
        committed = offset_and_metadata.offset
        lag = high_watermark - committed
        total_lag += lag

    if total_lag > max_lag:
        print(f"WARNING: Consumer lag {total_lag} exceeds threshold {max_lag}")
    return total_lag
```

---

## DR Test Scheduling

| Test Type       | Tier 0-1 Systems | Tier 2 Systems | Tier 3-4 Systems |
|-----------------|-------------------|----------------|-------------------|
| Tabletop        | Monthly           | Quarterly      | Semi-annual       |
| Walkthrough     | Quarterly         | Semi-annual    | Annual            |
| Simulation      | Quarterly         | Semi-annual    | Annual            |
| Full Failover   | Semi-annual       | Annual         | As needed         |
| Backup Restore  | Weekly (automated)| Monthly        | Quarterly         |

---

## Runbook Validation

Every DR drill should validate the runbook itself, not just the systems.

### Runbook Validation Checklist

- [ ] Runbook is accessible when primary systems are down
- [ ] Contact information is current
- [ ] Commands execute successfully (copy-paste test)
- [ ] Credentials and access are pre-provisioned
- [ ] Screenshots and diagrams match current architecture
- [ ] Estimated times match actual drill times
- [ ] Escalation paths work (test page the on-call)
- [ ] External vendor contacts are reachable
- [ ] Runbook covers rollback/failback procedures

---

## Compliance Requirements

### SOC 2

- DR plan must be documented and reviewed annually
- DR tests must be executed at least annually
- Test results must be documented with evidence
- Gaps must have remediation plans with deadlines

### ISO 27001

- Business continuity plan required (Annex A.17)
- DR capabilities must be tested at regular intervals
- Results must be reported to management
- Plans must be updated after organizational changes

### Audit Evidence Template

```text
DR TEST EVIDENCE
Date: ___________
Test type: [Tabletop | Walkthrough | Simulation | Full Failover]
Systems tested: ___________
Participants: ___________

Results:
- RTO achieved: ___ minutes (target: ___ minutes) [PASS/FAIL]
- RPO achieved: ___ minutes (target: ___ minutes) [PASS/FAIL]
- Data integrity verified: [YES/NO]
- All runbook steps valid: [YES/NO]

Findings:
1. ___________
2. ___________

Remediation items:
1. ___________ (owner: ___, due: ___)
2. ___________ (owner: ___, due: ___)

Approved by: ___________
```

---

## Post-Drill Report Template

```text
# DR Drill Report

## Summary
- Date: YYYY-MM-DD
- Duration: X hours
- Type: [Tabletop | Simulation | Full Failover]
- Scope: [Systems and regions tested]
- Overall result: [PASS | PARTIAL PASS | FAIL]

## Objectives
1. Validate RTO of X minutes for Tier Y systems
2. Verify RPO of X minutes for database Z
3. Test runbook accuracy for scenario W

## Results

| Objective                  | Target    | Actual    | Result |
|----------------------------|-----------|-----------|--------|
| RTO - Payment Service      | 15 min    | 12 min    | PASS   |
| RPO - User Database        | 1 min     | 45 sec    | PASS   |
| Runbook accuracy           | 100%      | 85%       | FAIL   |

## Findings
1. [Finding]: [Description and impact]
2. [Finding]: [Description and impact]

## Action Items
| Item                       | Owner     | Priority  | Due Date   |
|----------------------------|-----------|-----------|------------|
| Update DNS TTL             | SRE Team  | High      | YYYY-MM-DD |
| Fix runbook step 7         | On-call   | Medium    | YYYY-MM-DD |

## Lessons Learned
1. ___________
2. ___________

## Next Drill
- Scheduled: YYYY-MM-DD
- Focus areas: ___________
```

---

## Related Resources

- [chaos-engineering-guide.md](chaos-engineering-guide.md) -- Chaos experiment design for failure injection
- [health-check-patterns.md](health-check-patterns.md) -- Liveness and readiness probes
- [graceful-degradation.md](graceful-degradation.md) -- Fallback strategies during partial failure
- [resilience-checklists.md](resilience-checklists.md) -- Comprehensive resilience verification
- [circuit-breaker-patterns.md](circuit-breaker-patterns.md) -- Preventing cascade during failover
