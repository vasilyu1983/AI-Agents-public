# Distributed Systems Applied to DevOps and Platform Engineering

> **Gate before invoking:** Check [`foundations-distributed-systems` § When to Apply](../../foundations-distributed-systems/SKILL.md#when-to-apply) first. The recipes below assume the foundation is the right tool for the situation; the foundation's skip-conditions route you to a different foundation if not.


_Last verified: 2026-05-02._

Distributed systems theory is not ornamental. Every etcd cluster, Terraform state backend, Kubernetes controller, and multi-region database your platform depends on is a concrete instantiation of consensus, quorum, fencing, and consistency models. This reference maps the 11 primitives from [foundations-distributed-systems](../../foundations-distributed-systems/SKILL.md) onto the specific decisions and failure modes that platform and DevOps engineers encounter in daily operations.

---

## Table of Contents

- [Why This Matters for Platform Engineering](#why-this-matters-for-platform-engineering)
- [Patterns](#patterns)
  - [P1 etcd and Kubernetes Control-Plane Quorum Sizing](#p1-etcd-and-kubernetes-control-plane-quorum-sizing)
  - [P2 Terraform State Locking via Leases with Fencing](#p2-terraform-state-locking-via-leases-with-fencing)
  - [P3 Idempotent Deployment Scripts and GitOps Reconciliation](#p3-idempotent-deployment-scripts-and-gitops-reconciliation)
  - [P4 Kubernetes CronJob Leader Election](#p4-kubernetes-cronjob-leader-election)
  - [P5 Multi-Region Failover with Quorum-Loss Runbook](#p5-multi-region-failover-with-quorum-loss-runbook)
  - [P6 CRDT-Backed Feature-Flag State for Multi-Region GitOps](#p6-crdt-backed-feature-flag-state-for-multi-region-gitops)
  - [P7 Cross-Region Rolling Restart Correctness via Causal Consistency](#p7-cross-region-rolling-restart-correctness-via-causal-consistency)
- [Anti-Patterns](#anti-patterns)
  - [A1 Redlock and the Distributed-Lock Trap](#a1-redlock-and-the-distributed-lock-trap)
  - [A2 Even-Node etcd Clusters](#a2-even-node-etcd-clusters)
  - [A3 Terraform State Locking Without Fencing](#a3-terraform-state-locking-without-fencing)
  - [A4 Non-Idempotent Deployment Scripts](#a4-non-idempotent-deployment-scripts)
  - [A5 Assuming Leader-Elected Workers Are Unique Without a Fencing Token](#a5-assuming-leader-elected-workers-are-unique-without-a-fencing-token)
- [Recipes](#recipes)
  - [R1 etcd Quorum Sizing and Health Runbook](#r1-etcd-quorum-sizing-and-health-runbook)
  - [R2 Multi-Region Failover with Quorum-Loss Recovery](#r2-multi-region-failover-with-quorum-loss-recovery)
  - [R3 Idempotent Deployment Pipeline with Fenced Terraform State](#r3-idempotent-deployment-pipeline-with-fenced-terraform-state)
- [Cross-References](#cross-references)

---

## Why This Matters for Platform Engineering

Platform teams manage systems where distributed systems guarantees are invisible until they fail. The failure modes are non-obvious and expensive:

- A 5-node etcd cluster drops to 2 healthy members — writes block silently while Kubernetes appears to function until the next API call that mutates state.
- Two CI jobs run `terraform apply` against the same workspace — one corrupts the state file because the lock expired during a slow provider operation.
- A CronJob spawns 3 replicas during a rolling node drain — all three process the same work item because leader election used a library that does not enforce fencing.
- A cross-region restart sequence triggers a CAP event — the region you brought down last holds the only quorum-capable set of replicas.

The primitives below explain what is happening and give you the vocabulary to diagnose, prevent, and recover from each class of failure.

---

## Patterns

### P1 etcd and Kubernetes Control-Plane Quorum Sizing

**Primitives**: [#04 Raft](../../foundations-distributed-systems/assets/templates/distributed-systems/04-raft.md), [#09 Quorums](../../foundations-distributed-systems/assets/templates/distributed-systems/09-quorums.md), [#01 CAP/PACELC](../../foundations-distributed-systems/assets/templates/distributed-systems/01-cap-pacelc.md)

**Problem**: etcd is the single source of truth for Kubernetes cluster state. Its sizing determines both fault tolerance and write availability. Under-sizing creates hidden fragility; over-sizing adds unnecessary election latency and replication overhead.

**Raft majority rule**:

```
Cluster size N → fault tolerance f = floor(N/2)
Quorum required = floor(N/2) + 1

N=3: tolerates 1 failure, quorum=2
N=5: tolerates 2 failures, quorum=3
N=7: tolerates 3 failures, quorum=4
```

**Sizing decision table**:

| Cluster type | Recommended N | Tolerated failures | Notes |
|---|---|---|---|
| Single-region production | 3 | 1 | Standard for most clusters |
| Multi-region production | 5 | 2 | Survive loss of one region + one node |
| Multi-region critical | 7 | 3 | High-compliance environments; election latency increases |
| Development / staging | 1 | 0 | Not HA — document this explicitly |

**CAP position**: etcd chooses CP. Under a network partition that prevents a quorum from forming, etcd blocks writes rather than accepting them without majority consensus. This is correct for a control-plane store where stale state is worse than unavailability. Platform teams must plan for write unavailability during quorum loss — Kubernetes API mutations queue or fail; read operations against cached state continue.

**Regional placement for N=5**: Place 3 members in the primary region and 2 in the secondary. This means the primary region can sustain a quorum independently (3 of 5 members). A full loss of the secondary region does not lose quorum. A full loss of the primary region loses quorum — the 2 secondary members cannot form a majority. This is intentional: a primary region failure is treated as a full incident requiring human intervention, not an automatic failover.

**Election timeout tuning for cross-region etcd**:

```
# Measure inter-region RTT first
ping -c 100 <secondary-region-etcd-ip> | tail -1

# Election timeout must be >> heartbeat interval >> 99th-pct RTT
# Example: cross-region RTT p99 = 40ms
heartbeat_interval = 250ms    # 6× p99 RTT
election_timeout   = 1250ms   # 5× heartbeat_interval

# In etcd flags:
--heartbeat-interval=250
--election-timeout=1250
```

**Observability**:

```
# etcd health: all members must be members of the same cluster
etcdctl endpoint health --cluster -w table

# Check which member is leader
etcdctl endpoint status --cluster -w table

# Election count — rising count indicates instability
etcd_server_leader_changes_seen_total  # Prometheus metric

# Quorum loss alert
alert: EtcdQuorumLost
expr: etcd_server_has_leader == 0
for: 1m
severity: critical
```

---

### P2 Terraform State Locking via Leases with Fencing

**Primitives**: [#08 Leases and Fencing](../../foundations-distributed-systems/assets/templates/distributed-systems/08-leases-fencing.md), [#07 Idempotency](../../foundations-distributed-systems/assets/templates/distributed-systems/07-idempotency.md)

**Problem**: Terraform state is a shared mutable document. Concurrent `terraform apply` runs against the same workspace corrupt state. The built-in locking mechanism (DynamoDB for S3 backends, GCS object locking, Azure Blob lease) is a lease — but many teams do not configure or enforce it correctly.

**How Terraform state locking maps to leases**:

```
Lease authority  = DynamoDB table (or GCS bucket lock, Azure Blob lease)
Lease holder     = the terraform process that acquired the lock
Lease duration   = indefinite while process is alive (heartbeat via table item TTL)
Fencing token    = LockID (UUID written to the lock record at acquisition time)

Write condition:
  terraform only writes state if it holds the lock with the current LockID
  → any concurrent process that acquired the lock later has a different LockID
  → first process's writes are rejected by the backend on LockID mismatch
```

**S3 + DynamoDB backend configuration**:

```hcl
terraform {
  backend "s3" {
    bucket         = "myorg-tfstate"
    key            = "prod/us-east-1/cluster.tfstate"
    region         = "us-east-1"
    encrypt        = true

    # Lease + fencing: DynamoDB table for state locking
    dynamodb_table = "myorg-tfstate-locks"

    # S3 versioning provides the audit trail of state versions
    # (analogous to fencing token history)
  }
}
```

**DynamoDB table requirements**:

```
Table name:   myorg-tfstate-locks
Partition key: LockID (String)
Billing mode:  PAY_PER_REQUEST

# Terraform writes this item structure on lock acquisition:
{
  "LockID": "prod/us-east-1/cluster.tfstate",
  "Info": "{\"ID\":\"<uuid>\",\"Operation\":\"OperationTypeApply\",
            \"Who\":\"ci-runner@build-123\",\"Created\":\"2026-05-02T...\"}",
  "Digest": "<state-md5>"
}
```

**Lock hygiene in CI pipelines**:

```yaml
# GitHub Actions: ensure only one apply runs per workspace at a time
jobs:
  terraform-apply:
    concurrency:
      group: terraform-${{ inputs.workspace }}  # one job per workspace
      cancel-in-progress: false                  # queue, do not cancel
    steps:
      - run: terraform init
      - run: terraform apply -auto-approve

      # On failure: force-unlock only via manual runbook step
      # Never add -lock=false to the apply command
```

**Manual lock recovery runbook** (for stale locks after CI crash):

```bash
# 1. Verify the lock is stale (the locking process is dead)
terraform force-unlock <LockID>
# LockID found in DynamoDB or in the error message from a failed apply

# 2. Before unlocking: confirm no apply is in progress
# Check: are there any running CI jobs targeting this workspace?
# Check: is there a partial state from a failed apply? (inspect S3 versions)

# 3. If partial state exists, restore previous version first
aws s3api list-object-versions \
  --bucket myorg-tfstate \
  --prefix prod/us-east-1/cluster.tfstate \
  --query 'Versions[*].[VersionId,LastModified]' \
  --output table

# 4. Restore and re-plan before any new apply
```

---

### P3 Idempotent Deployment Scripts and GitOps Reconciliation

**Primitive**: [#07 Idempotency](../../foundations-distributed-systems/assets/templates/distributed-systems/07-idempotency.md)

**Problem**: Deployment scripts that are not idempotent fail during retries, partial failures, and reconciliation loops. In a GitOps model, the reconciler calls `apply` repeatedly — any non-idempotent side effect is executed multiple times.

**Idempotency contract for deployment operations**:

```
f(f(x)) = f(x) for all x

Concrete implications:
  kubectl apply  → idempotent (server-side apply, desired-state)
  kubectl create → NOT idempotent (fails if resource exists)
  helm upgrade --install → idempotent (upsert semantics)
  helm install  → NOT idempotent (fails on second call)
  terraform apply → idempotent (plan diff, then converge)
  raw shell scripts that create resources → NOT idempotent without guards
```

**Pattern: guard all non-idempotent shell operations**:

```bash
#!/usr/bin/env bash
set -euo pipefail

# Non-idempotent: fails if namespace exists
# kubectl create namespace my-app

# Idempotent form:
kubectl create namespace my-app --dry-run=client -o yaml \
  | kubectl apply -f -

# Non-idempotent: creates duplicate secrets
# kubectl create secret generic db-creds --from-literal=password=...

# Idempotent form:
kubectl create secret generic db-creds \
  --from-literal=password="${DB_PASSWORD}" \
  --dry-run=client -o yaml \
  | kubectl apply -f -

# Non-idempotent: adds duplicate lines to a config file
# echo "config_value=true" >> /etc/myapp/config.ini

# Idempotent form (grep guard):
grep -qxF "config_value=true" /etc/myapp/config.ini \
  || echo "config_value=true" >> /etc/myapp/config.ini
```

**GitOps reconciliation and idempotency**: ArgoCD and Flux both call their sync/apply logic on a recurring interval (default 3 minutes for ArgoCD). Every resource applied by the reconciler must survive repeated application. Use `kubectl apply` (server-side apply preferred), never `kubectl create`. Helm chart hooks that use `kubectl create` must be annotated with `"helm.sh/hook-delete-policy": hook-succeeded` to clean up before the next run.

**Idempotency keys for external API calls in deployment scripts**:

```bash
# Any deployment script that calls external APIs must use idempotency keys
# Example: registering a service with a service mesh control plane

register_service() {
  local service_name="$1"
  local idempotency_key="deploy-${service_name}-${GIT_SHA}"

  curl -X POST https://control-plane/services \
    -H "Idempotency-Key: ${idempotency_key}" \
    -H "Content-Type: application/json" \
    -d "{\"name\": \"${service_name}\", \"version\": \"${GIT_SHA}\"}"
  # Duplicate calls with the same key return the same response
  # without creating duplicate registrations
}
```

---

### P4 Kubernetes CronJob Leader Election

**Primitives**: [#08 Leases and Fencing](../../foundations-distributed-systems/assets/templates/distributed-systems/08-leases-fencing.md), [#04 Raft](../../foundations-distributed-systems/assets/templates/distributed-systems/04-raft.md)

**Problem**: A CronJob with `parallelism > 1`, or a Deployment with multiple replicas where only one should perform a periodic task, requires leader election. Kubernetes provides a lease-based leader election mechanism in `client-go`. Misuse leads to multiple workers processing the same item simultaneously.

**Kubernetes lease mechanics**:

```
Kubernetes Lease object (coordination.k8s.io/v1):
  - leaseDurationSeconds: how long the lease is valid
  - renewTime:            when the current holder last renewed
  - holderIdentity:       pod name of the current leader
  - leaseTransitions:     fencing token (monotonically increasing)

Leader election cycle:
  1. All replicas watch the Lease object
  2. The holder sets holderIdentity = <own pod name>, updates renewTime
  3. Other replicas see holderIdentity != own name → become followers
  4. If renewTime + leaseDurationSeconds < now → lease expired → election
  5. New leader acquires the lease and increments leaseTransitions
```

**CronJob with leader election via controller-runtime**:

```go
// Leader election configuration in a multi-replica operator or worker
mgr, err := ctrl.NewManager(ctrl.GetConfigOrDie(), ctrl.Options{
    LeaderElection:                true,
    LeaderElectionID:              "myapp-worker-leader",
    LeaderElectionNamespace:       "myapp",
    LeaderElectionReleaseOnCancel: true,

    // Lease duration: how long a leader holds authority without renewing
    LeaseDuration: ptr(15 * time.Second),
    // Retry period: how often followers try to acquire the lease
    RetryPeriod: ptr(5 * time.Second),
    // Renew deadline: leader must renew within this time or lose the lease
    RenewDeadline: ptr(10 * time.Second),
})
```

**Fencing at the work layer** — the lease alone is not enough if work involves external state:

```go
func (w *Worker) ProcessItem(ctx context.Context, item *WorkItem) error {
    // Read the current lease to get the fencing token
    lease, err := w.k8sClient.Get(ctx, "myapp-worker-leader", ...)
    if err != nil {
        return err
    }
    fencingToken := lease.Spec.LeaseTransitions

    // Include the fencing token in any downstream write
    // The downstream store must reject writes with a lower token
    return w.store.Write(ctx, item, WriteOptions{
        FencingToken: fencingToken,
    })
}
```

**Tuning guidance for CronJob lease timeouts**:

```
leaseDurationSeconds  = max(3 × renewDeadlineSeconds, 15s)
renewDeadlineSeconds  = max(2 × retryPeriodSeconds, 10s)
retryPeriodSeconds    = max(2 × leader_work_cycle_ms / 1000, 5s)

For a CronJob that runs a 30-second work item:
  retryPeriod    = 5s
  renewDeadline  = 10s
  leaseDuration  = 15s

For a CronJob that runs a 5-minute batch job:
  retryPeriod    = 15s
  renewDeadline  = 30s
  leaseDuration  = 60s
  # Prevents premature leadership failover during long-running jobs
```

---

### P5 Multi-Region Failover with Quorum-Loss Runbook

**Primitives**: [#09 Quorums](../../foundations-distributed-systems/assets/templates/distributed-systems/09-quorums.md), [#04 Raft](../../foundations-distributed-systems/assets/templates/distributed-systems/04-raft.md), [#01 CAP/PACELC](../../foundations-distributed-systems/assets/templates/distributed-systems/01-cap-pacelc.md), [#02 FLP Impossibility](../../foundations-distributed-systems/assets/templates/distributed-systems/02-flp-impossibility.md)

**Problem**: A multi-region Kubernetes cluster backed by a 5-member etcd loses a region containing 3 etcd members. The cluster has lost quorum. Kubernetes API writes block. The runbook must restore quorum without losing committed data.

**Quorum-loss detection**:

```bash
# Symptom: kubectl commands hang or return "etcdserver: no leader"
kubectl get pods --timeout=5s
# Error: etcdserver: no leader

# Confirm quorum loss
etcdctl endpoint health --cluster -w table
# ENDPOINT    HEALTH  TOOK    ERROR
# 10.0.1.10   false   5.01s   context deadline exceeded
# 10.0.1.11   false   5.01s   context deadline exceeded
# 10.0.2.10   true    1.2ms   -
# 10.0.2.11   true    1.3ms   -
# Only 2 of 5 members reachable — quorum (3) lost

# Check etcd leader status on surviving members
etcdctl endpoint status --cluster -w table
```

**Recovery decision tree**:

```
Q: Are any members of the lost region recoverable?
  YES (network partition, not data loss):
    → Wait for partition to heal; do not intervene
    → etcd recovers automatically when quorum is restored
    → Confirm: etcd_server_leader_changes_seen_total stabilizes

  NO (region is gone, data loss is confirmed):
    → Proceed to manual quorum recovery below
```

**Manual quorum recovery (data-loss path)**:

```bash
# Step 1: Stop the Kubernetes API server on all nodes
# (Prevents writes to a partially recovered etcd that could diverge)
systemctl stop kube-apiserver  # on all control-plane nodes

# Step 2: Identify the most up-to-date surviving member
# Check member with highest raft index
etcdctl endpoint status -w json \
  --endpoints=10.0.2.10:2379,10.0.2.11:2379 \
  | jq '.[].Status.header.revision'
# Use the member with the highest revision as the recovery source

# Step 3: Force a new cluster from the surviving member
# !! DESTRUCTIVE: data on lost members is abandoned !!
# Run ONLY on the designated recovery source member
ETCD_FORCE_NEW_CLUSTER=true etcd \
  --data-dir=/var/lib/etcd \
  --name=etcd-surviving-1 \
  --initial-cluster=etcd-surviving-1=https://10.0.2.10:2380 \
  --initial-advertise-peer-urls=https://10.0.2.10:2380

# Step 4: Verify new single-member cluster is healthy
etcdctl endpoint health
etcdctl endpoint status -w table

# Step 5: Add replacement members one at a time
etcdctl member add etcd-new-2 --peer-urls=https://10.0.2.20:2380
# Start the new member with --initial-cluster-state=existing

# Step 6: Restart the Kubernetes API server
systemctl start kube-apiserver

# Step 7: Run conformance checks
kubectl get nodes
kubectl get componentstatuses
```

**Prevention — region placement rule**:

```
For N=5 across 2 regions:
  Primary region:   3 members  ← can sustain quorum independently
  Secondary region: 2 members

For N=5 across 3 regions:
  Region A: 2 members
  Region B: 2 members
  Region C: 1 member (tiebreaker)
  ← Loss of any one region preserves quorum (minimum: 3 of 5 remain)
  ← This is the preferred topology for 3-region active-active
```

---

### P6 CRDT-Backed Feature-Flag State for Multi-Region GitOps

**Primitives**: [#06 CRDTs](../../foundations-distributed-systems/assets/templates/distributed-systems/06-crdts.md), [#10 Causal Consistency](../../foundations-distributed-systems/assets/templates/distributed-systems/10-causal-consistency.md)

**Problem**: Feature flags toggled in one region must be visible in other regions without requiring strong consistency — but conflicting flag updates (two operators toggle the same flag in different directions simultaneously in two regions) must resolve deterministically.

**CRDT flag model**:

```
Flag state: Observed-Remove Set (OR-Set) of enabled flag IDs
  → ADD(flag_id, unique_tag) is convergent
  → REMOVE(flag_id, all_known_tags) is convergent
  → Concurrent ADD and REMOVE: ADD wins (availability bias)

Implementation in a GitOps model:
  Each region maintains its own flag state in a Git repository
  Merge conflicts are resolved by a CRDT merge function, not by
  human conflict resolution or last-write-wins

Merge function (OR-Set):
  merged_enabled = union(region_A.enabled_set, region_B.enabled_set)
  merged_removed = intersect(region_A.removed_set, region_B.removed_set)
  result.enabled = merged_enabled - merged_removed
```

**Simpler alternative for most platform teams**: Use a feature-flag service (LaunchDarkly, Unleash, Flagsmith) with multi-region replication and eventual consistency. Treat it as a read-mostly system: reads are always available from the local region; writes go to the primary region and propagate within seconds. Reserve CRDT modeling for scenarios where flag state must be updated during a partition (no network to primary region) with automatic merge on recovery.

**Causal dependency tracking**: When a feature flag gates a database migration (`flag: run_migration_v2`), the flag activation and the migration must be causally ordered. Use causal consistency (#10): record the flag activation with a vector clock entry, and require the migration job to observe the flag activation before proceeding. This prevents a scenario where a flag is toggled on, propagated to region A but not region B, and region B runs an incompatible migration path.

---

### P7 Cross-Region Rolling Restart Correctness via Causal Consistency

**Primitives**: [#10 Causal Consistency](../../foundations-distributed-systems/assets/templates/distributed-systems/10-causal-consistency.md), [#05 Vector Clocks and Lamport Timestamps](../../foundations-distributed-systems/assets/templates/distributed-systems/05-vector-clocks-lamport.md), [#11 Broadcast Protocols](../../foundations-distributed-systems/assets/templates/distributed-systems/11-broadcast-protocols.md)

**Problem**: A rolling restart of a stateful service across three regions must ensure that the new version is fully healthy in each region before proceeding to the next. If the health check reads stale state from a replica that has not yet applied the latest configuration, the restart controller may incorrectly advance to the next region.

**Causal constraint for rolling restart**:

```
Restart must respect the happens-before relation:
  region_A_healthy → start_region_B_restart
  region_B_healthy → start_region_C_restart

"healthy" must be causally consistent, not clock-consistent:
  A timestamp check is insufficient (clock skew can cause false positives)
  A version vector check is sufficient:
    region is healthy iff all replicas in the region have applied
    config version V (where V is the version that triggered the restart)
```

**Implementation with Kubernetes annotations as a vector clock**:

```bash
# Tag the config update with a restart version
kubectl annotate configmap myapp-config \
  restart-version="$(date +%s)" \
  --overwrite

# Rolling restart with version propagation
kubectl rollout restart deployment/myapp -n myapp

# Before advancing to next region: verify all pods report the new version
wait_for_causal_consistency() {
  local namespace="$1"
  local restart_version="$2"
  local timeout=300

  while true; do
    local stale_pods
    stale_pods=$(kubectl get pods -n "${namespace}" \
      -o jsonpath='{.items[*].metadata.annotations.restart-version}' \
      | tr ' ' '\n' \
      | grep -v "^${restart_version}$" \
      | wc -l)

    if [[ "${stale_pods}" -eq 0 ]]; then
      echo "All pods at version ${restart_version} — region is consistent"
      return 0
    fi

    timeout=$((timeout - 5))
    if [[ "${timeout}" -le 0 ]]; then
      echo "TIMEOUT: ${stale_pods} pods still stale"
      return 1
    fi
    sleep 5
  done
}
```

**Causal broadcast for config propagation**: When a configuration change must reach all regions before any region acts on it, use a causal broadcast protocol (#11). In a GitOps model, this maps to: push the config change to the main branch; wait for the GitOps operator in each region to confirm it has applied the change (via ArgoCD sync status or Flux reconciliation event) before triggering the restart workflow. The GitOps operator's sync confirmation is the causal acknowledgement.

---

## Anti-Patterns

### A1 Redlock and the Distributed-Lock Trap

**Primitives violated**: [#08 Leases and Fencing](../../foundations-distributed-systems/assets/templates/distributed-systems/08-leases-fencing.md), [#02 FLP Impossibility](../../foundations-distributed-systems/assets/templates/distributed-systems/02-flp-impossibility.md)

**What Redlock does**: Redlock is Redis's multi-node distributed lock algorithm. A client acquires a lock by writing to a majority of N independent Redis instances within a time window shorter than the lock TTL. It claims to provide mutual exclusion across failures.

**Why Redlock is unsafe**:

```
Scenario (Martin Kleppmann's analysis):

1. Client A acquires Redlock on 3 of 5 Redis nodes. TTL = 10s.
2. Client A experiences a 15-second GC pause.
3. The lock TTL expires on all Redis nodes.
4. Client B acquires Redlock on all 5 nodes. TTL = 10s.
5. Client B writes to shared storage with its lock.
6. Client A wakes from GC pause, believes it holds the lock (no
   expiry check in its local state), and writes to shared storage.
7. Both A and B hold the lock simultaneously → split-brain.

Root cause: Redlock relies on time (TTL) for safety, but time is
not a reliable distributed primitive. GC pauses, VM clock adjustments,
and network delays can all cause a process to exceed its TTL without
knowing it. FLP impossibility guarantees that no algorithm based solely
on timing can distinguish a crashed process from a slow one.
```

**Correct alternative**: Use a lease-backed lock from a CP system (etcd, ZooKeeper, Chubby) and always pass a fencing token with every write. The fencing token allows the storage layer to reject stale writes even if the lock holder is unaware its lease has expired.

```python
# etcd-based distributed lock with fencing token
import etcd3

client = etcd3.client()

# Acquire lease
lease = client.lease(ttl=15)  # 15-second TTL

# Write lock key with the lease
lock_key = "/locks/myapp/critical-section"
client.put(lock_key, "holder-pod-name", lease=lease)

# Get the fencing token (etcd revision is monotonically increasing)
_, metadata = client.get(lock_key)
fencing_token = metadata.mod_revision

# Pass fencing_token to every downstream write
do_critical_work(fencing_token=fencing_token)

# Renew the lease periodically while work is in progress
lease.refresh()

# On completion: revoke the lease (releases the lock immediately)
lease.revoke()
```

**Rule**: Never use Redlock or any time-based distributed lock for operations that mutate shared persistent state. Use it only for advisory locking where a stale lock holder completing its operation is acceptable (e.g., cache warming, non-critical deduplication).

---

### A2 Even-Node etcd Clusters

**Primitive violated**: [#04 Raft](../../foundations-distributed-systems/assets/templates/distributed-systems/04-raft.md), [#09 Quorums](../../foundations-distributed-systems/assets/templates/distributed-systems/09-quorums.md)

**Pattern**: A team runs a 4-node etcd cluster because they have 4 control-plane nodes.

**Why this is wrong**:

```
N=4, quorum = floor(4/2) + 1 = 3
Fault tolerance: floor(4/2) = 2? No.
If 2 nodes fail, only 2 remain — quorum (3) is lost.
Effective fault tolerance = 1 (same as N=3).

N=3, quorum = 2
Fault tolerance = 1

N=4 provides the same fault tolerance as N=3 but adds one node's cost,
complexity, and one more failure point. The fourth member does not
help — it only makes quorum harder to achieve.
```

**Fix**: Always use odd-sized clusters. For 4 control-plane nodes, either:
1. Run etcd on 3 of the 4 nodes (etcd membership ≠ control-plane node count).
2. Add a fifth etcd member (possibly a lightweight etcd-only node) to reach N=5.

**Detecting this in existing clusters**:

```bash
etcdctl member list -w table | grep -c started
# If output is 2 or 4, the cluster is at an even size — fix it
```

---

### A3 Terraform State Locking Without Fencing

**Primitives violated**: [#08 Leases and Fencing](../../foundations-distributed-systems/assets/templates/distributed-systems/08-leases-fencing.md)

**Pattern**: A team uses S3 as the Terraform backend but does not configure the DynamoDB locking table. Or they use `-lock=false` to work around a stale lock.

**Failure mode**:

```
CI job 1: terraform apply (workspace: prod-us-east-1)
CI job 2: terraform apply (workspace: prod-us-east-1) [triggered simultaneously]

Both jobs read the same state version → compute different plans
  (because job 2's plan is based on job 1's pre-apply state)
Both jobs write different new state versions to S3

Result: the state file reflects one job's changes; the other's are silently
discarded. The next plan will show spurious diffs from the overwritten
job's changes being re-detected as drift.
```

**Fix**: Always configure the DynamoDB locking table. Treat `-lock=false` as a break-glass operation that requires a second pair of eyes and is documented in the incident log. Configure CI pipeline concurrency groups (see P2) to enforce serialization at the job level as a second layer.

---

### A4 Non-Idempotent Deployment Scripts

**Primitive violated**: [#07 Idempotency](../../foundations-distributed-systems/assets/templates/distributed-systems/07-idempotency.md)

**Pattern**: A deployment script uses `kubectl create`, `helm install`, or raw shell commands that fail on retry. When the CI pipeline retries a failed deployment step, the script errors out at the first non-idempotent operation, leaving the system in a partial state.

**Failure cascade**:

```
Step 1: Deploy app v2 — succeeds
Step 2: Create ConfigMap — fails (ConfigMap already exists from v1 deploy)
        kubectl create configmap myapp-config --from-file=... → AlreadyExists
Step 3: Steps 3–8 never run
Result: app v2 running with v1 ConfigMap → runtime misconfiguration
```

**Audit command** to find non-idempotent operations in existing scripts:

```bash
# Find kubectl create and helm install in deployment scripts
rg "kubectl create(?! .* --dry-run)" deploy/ scripts/
rg "helm install(?! --generate-name)" deploy/ scripts/

# These are candidates for conversion to:
#   kubectl apply -f -  (from --dry-run=client -o yaml pipe)
#   helm upgrade --install
```

---

### A5 Assuming Leader-Elected Workers Are Unique Without a Fencing Token

**Primitives violated**: [#08 Leases and Fencing](../../foundations-distributed-systems/assets/templates/distributed-systems/08-leases-fencing.md), [#02 FLP Impossibility](../../foundations-distributed-systems/assets/templates/distributed-systems/02-flp-impossibility.md)

**Pattern**: A team implements leader election for a worker that sends notifications or mutates external state. The implementation acquires a Kubernetes Lease and then performs work, but does not pass a fencing token to the downstream system. When a GC pause causes the lease to expire mid-work, two workers execute the same work item.

**Consequence**: Duplicate notifications sent to users, duplicate database rows, duplicate external API calls, or double-billing. FLP impossibility guarantees that no leader election algorithm can distinguish a paused worker from a crashed one in finite time — fencing at the storage/destination layer is the only correct defense.

**Detection**: Any worker that holds a Kubernetes Lease and writes to an external system (database, message queue, third-party API) without a conditional write (idempotency key, compare-and-swap, or fencing token) is vulnerable. Audit with:

```bash
# Find leader election usage
rg "leaderelection\|LeaderElection\|coordinator.Lease" \
  --type go internal/ pkg/

# For each file found, verify the downstream write includes a conditional:
#   - idempotency key in the request header
#   - compare-and-swap (etcd Put with prevValue/revision condition)
#   - database UPDATE ... WHERE version = expected_version
```

---

## Recipes

### R1 etcd Quorum Sizing and Health Runbook

**Goal**: Right-size an etcd cluster for a production Kubernetes environment, instrument it, and provide an operational runbook for health assessment.

**Primitives used**: Raft (#04), Quorums (#09), CAP/PACELC (#01).

**Sizing calculator**:

```
inputs:
  regions: 2
  max_tolerable_node_failures: 2   # must survive loss of one region
  → N = 2 * max_tolerable_node_failures + 1 = 5
  → quorum = 3
  → placement: 3 primary / 2 secondary
```

**Cluster provisioning checklist**:

```bash
# 1. Provision 5 VMs with dedicated SSDs (etcd is I/O-sensitive)
#    Instance type: at least 2 vCPU, 8 GB RAM, 50 GB NVMe SSD

# 2. Set OS-level parameters
sysctl -w vm.swappiness=0          # etcd must not swap
sysctl -w net.core.rmem_max=2500000

# 3. Tune etcd for cross-region deployment
cat > /etc/etcd/etcd.conf.yml <<EOF
heartbeat-interval: 250
election-timeout: 1250
snapshot-count: 10000
max-snapshots: 5
max-wals: 5
quota-backend-bytes: 8589934592  # 8 GB
EOF

# 4. Enable TLS for peer and client communication
# (omitted for brevity — use cert-manager or cfssl)

# 5. Verify cluster formation
etcdctl member list -w table
etcdctl endpoint health --cluster -w table
```

**Ongoing health monitoring** (Prometheus alerts):

```yaml
groups:
  - name: etcd-quorum
    rules:
      - alert: EtcdNoLeader
        expr: etcd_server_has_leader == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "etcd cluster has no leader — Kubernetes API writes are blocked"

      - alert: EtcdMemberDown
        expr: count(etcd_server_has_leader == 1) < 3
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "etcd quorum at risk: fewer than 3 healthy members"

      - alert: EtcdHighLeaderChanges
        expr: increase(etcd_server_leader_changes_seen_total[1h]) > 3
        labels:
          severity: warning
        annotations:
          summary: "etcd leader instability — check network or disk I/O"

      - alert: EtcdDatabaseSizeNearQuota
        expr: etcd_mvcc_db_total_size_in_bytes / etcd_server_quota_backend_bytes > 0.8
        labels:
          severity: warning
        annotations:
          summary: "etcd database at 80% of quota — compact and defrag soon"
```

**Defragmentation runbook** (run monthly or when database size > 80% of quota):

```bash
# Run defrag one member at a time, never all simultaneously
MEMBERS=$(etcdctl member list -w json | jq -r '.members[].clientURLs[0]')

for endpoint in ${MEMBERS}; do
  echo "Defragging ${endpoint}"
  etcdctl defrag --endpoints="${endpoint}"
  sleep 30  # allow member to re-join cleanly before defragging next
done

# Verify after defrag
etcdctl endpoint status --cluster -w table
```

---

### R2 Multi-Region Failover with Quorum-Loss Recovery

**Goal**: Provide a tested, step-by-step runbook for recovering a Kubernetes cluster from etcd quorum loss in a multi-region deployment.

**Primitives used**: Raft (#04), Quorums (#09), FLP Impossibility (#02), CAP/PACELC (#01).

**Pre-requisites** (must be in place before the incident):

```
1. etcd data directories on persistent volumes with snapshot-to-S3 enabled
2. Velero or etcd snapshot CronJob running every 15 minutes
3. etcd member list documented and accessible offline (out-of-band runbook)
4. kubectl access to surviving members from bastion host
5. Terraform or Ansible to provision replacement etcd members
```

**Incident response sequence**:

```
Phase 1 — Assess (target: < 5 minutes)
  1. Confirm quorum loss: etcdctl endpoint health --cluster
  2. Identify surviving members and their raft revision
  3. Determine cause: network partition (recoverable) vs. node failure (data may be lost)
  4. Declare incident severity: P1 (all writes blocked)

Phase 2 — Contain (target: < 10 minutes)
  5. Stop non-critical workloads from retrying writes (they will queue)
  6. Notify downstream teams: Kubernetes API mutations are blocked;
     reads from cached state continue; no new deployments or config changes
  7. If network partition: check if partition is healing (do not intervene yet)

Phase 3 — Recover (target: < 30 minutes from quorum loss)
  8. If partition healed: verify etcd auto-recovers; confirm leader elected
  9. If nodes are lost:
     a. Restore from latest snapshot to a new member
     b. Force-new-cluster on the surviving member with highest revision
     c. Add replacement members (one at a time)
     d. Restart kube-apiserver

Phase 4 — Verify (target: < 15 minutes after recovery)
  10. kubectl get nodes -- all nodes Ready
  11. kubectl get pods -A -- no unexpected pending/failed pods
  12. ArgoCD sync status -- all applications Synced
  13. Run conformance smoke test: deploy a test pod, verify it runs, delete it

Phase 5 — Post-incident
  14. Identify what data was lost (compare pre-incident snapshot with current state)
  15. Reconcile any missing resources (missing deployments, configmaps, secrets)
  16. Write postmortem: placement rule violated? snapshot interval too long?
```

**Snapshot restore procedure**:

```bash
# List available snapshots
aws s3 ls s3://myorg-etcd-snapshots/ --recursive | sort -k1,2 | tail -20

# Restore snapshot to new member data directory
SNAPSHOT_FILE="etcd-snapshot-2026-05-02T14:30:00Z.db"
aws s3 cp s3://myorg-etcd-snapshots/${SNAPSHOT_FILE} /tmp/

etcdutl snapshot restore /tmp/${SNAPSHOT_FILE} \
  --name etcd-recovery-1 \
  --initial-cluster etcd-recovery-1=https://10.0.2.10:2380 \
  --initial-cluster-token etcd-recovery-token \
  --initial-advertise-peer-urls https://10.0.2.10:2380 \
  --data-dir /var/lib/etcd

# Start etcd with the restored data directory
# (do not set ETCD_FORCE_NEW_CLUSTER if restoring from snapshot)
```

---

### R3 Idempotent Deployment Pipeline with Fenced Terraform State

**Goal**: Build a CI/CD pipeline where all deployment steps are safe to retry, Terraform state is properly locked with fencing semantics, and partial failures do not corrupt infrastructure state.

**Primitives used**: Idempotency (#07), Leases and Fencing (#08), Raft (#04, via etcd for any Kubernetes steps).

**Pipeline structure** (GitHub Actions):

```yaml
name: Deploy Infrastructure

on:
  push:
    branches: [main]
    paths: ['terraform/**']

jobs:
  terraform:
    runs-on: ubuntu-latest
    environment: production

    # Fencing layer 1: CI-level serialization
    # Only one apply per workspace at a time; queue, do not cancel
    concurrency:
      group: terraform-${{ inputs.workspace || 'prod-us-east-1' }}
      cancel-in-progress: false

    steps:
      - uses: actions/checkout@v4

      - name: Configure AWS credentials (workload identity, not long-lived keys)
        uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::123456789:role/GitHubActionsDeployRole
          aws-region: us-east-1

      - name: Terraform Init
        run: |
          terraform -chdir=terraform/envs/prod-us-east-1 init
        # init is idempotent — safe to retry

      - name: Terraform Plan
        id: plan
        run: |
          terraform -chdir=terraform/envs/prod-us-east-1 plan \
            -out=tfplan \
            -lock=true \
            -lock-timeout=120s
        # plan acquires the DynamoDB lock (fencing layer 2)
        # -lock-timeout=120s: wait up to 2 min for a stale lock to expire
        # before failing; do NOT use -lock=false

      - name: Terraform Apply
        run: |
          terraform -chdir=terraform/envs/prod-us-east-1 apply \
            -auto-approve \
            tfplan
        # apply holds the lock for the duration
        # tfplan was computed with the same state version that the lock protects
        # concurrent apply by another job: lock contention → one wins, one queues

      - name: Idempotent Kubernetes resource sync
        run: |
          # All kubectl operations use apply (server-side), not create
          kubectl apply -f k8s/prod/ --server-side --force-conflicts
          # --server-side: field manager semantics prevent conflicting updates
          # --force-conflicts: CI pipeline wins field ownership conflicts

      - name: Verify deployment converged (causal consistency check)
        run: |
          kubectl rollout status deployment/myapp -n myapp --timeout=300s
          # rollout status blocks until all replicas have the new version
          # (causal consistency: wait for the new config to propagate to all pods)
```

**Stale lock recovery** (break-glass, requires two approvals):

```bash
# Never automate this step — always requires human judgment

# 1. Verify the locking process is dead
aws dynamodb get-item \
  --table-name myorg-tfstate-locks \
  --key '{"LockID": {"S": "prod/us-east-1/cluster.tfstate"}}' \
  | jq '.Item.Info.S | fromjson'
# Review "Who" and "Created" fields — is the CI job still running?

# 2. Check S3 state for partial apply
aws s3api list-object-versions \
  --bucket myorg-tfstate \
  --prefix prod/us-east-1/cluster.tfstate \
  --query 'sort_by(Versions, &LastModified)[-3:].[VersionId, LastModified]' \
  --output table

# 3. If safe: force unlock
terraform force-unlock <LockID> -force

# 4. Re-run plan before apply to detect any partial state
terraform plan -chdir=terraform/envs/prod-us-east-1
```

**Idempotency validation gate** (run in CI before merge):

```bash
# Detect non-idempotent patterns in Terraform and Kubernetes scripts
rg "kubectl create(?! .*(--dry-run|-h|--help))" \
  --type sh --type yaml -g '!**/.archive/**' .

rg "helm install(?! --generate-name)" \
  --type sh --type yaml -g '!**/.archive/**' .

# Apply twice against a test environment and diff the plans
# A correctly idempotent stack produces an empty plan on the second run
terraform plan -detailed-exitcode  # exit code 0 = no changes (idempotent)
```

---

## Cross-References

### Foundation

- [foundations-distributed-systems](../../foundations-distributed-systems/SKILL.md) — all 11 primitives this file applies
  - [01-cap-pacelc.md](../../foundations-distributed-systems/assets/templates/distributed-systems/01-cap-pacelc.md)
  - [02-flp-impossibility.md](../../foundations-distributed-systems/assets/templates/distributed-systems/02-flp-impossibility.md)
  - [03-paxos.md](../../foundations-distributed-systems/assets/templates/distributed-systems/03-paxos.md)
  - [04-raft.md](../../foundations-distributed-systems/assets/templates/distributed-systems/04-raft.md)
  - [05-vector-clocks-lamport.md](../../foundations-distributed-systems/assets/templates/distributed-systems/05-vector-clocks-lamport.md)
  - [06-crdts.md](../../foundations-distributed-systems/assets/templates/distributed-systems/06-crdts.md)
  - [07-idempotency.md](../../foundations-distributed-systems/assets/templates/distributed-systems/07-idempotency.md)
  - [08-leases-fencing.md](../../foundations-distributed-systems/assets/templates/distributed-systems/08-leases-fencing.md)
  - [09-quorums.md](../../foundations-distributed-systems/assets/templates/distributed-systems/09-quorums.md)
  - [10-causal-consistency.md](../../foundations-distributed-systems/assets/templates/distributed-systems/10-causal-consistency.md)
  - [11-broadcast-protocols.md](../../foundations-distributed-systems/assets/templates/distributed-systems/11-broadcast-protocols.md)

### Sibling Applied References (ops-devops-platform)

- [control-theory-applied.md](control-theory-applied.md) — PID-based deployment control, canary fusion, CI queue stabilization
- [queueing-theory-applied.md](queueing-theory-applied.md) — capacity planning, saturation SLOs, multi-stage pipeline bottleneck analysis
- [theory-of-constraints-applied.md](theory-of-constraints-applied.md) — CI/CD throughput recovery, review-SLA constraint surfacing

### Related Skills

- [ops-incident-response](../../ops-incident-response/SKILL.md) — incident management patterns; quorum-loss recovery feeds directly into incident runbooks
- [qa-resilience](../../qa-resilience/SKILL.md) — chaos engineering and fault injection to validate quorum behavior and fencing correctness
- [software-architecture-design](../../software-architecture-design/SKILL.md) — distributed system design decisions upstream of platform operations

---

_Sources: Ongaro & Ousterhout (2014) Raft; Kleppmann (2017) DDIA Ch. 5, 7, 8, 9; DeCandia et al. (2007) Dynamo; Gifford (1979) Quorum Systems; Gray & Cheriton (1989) Leases; Fischer, Lynch & Paterson (1985) FLP; Brewer (2000) CAP; Abadi (2012) PACELC; etcd documentation [etcd.io/docs](https://etcd.io/docs/); Terraform S3 backend docs [developer.hashicorp.com/terraform/language/backend/s3](https://developer.hashicorp.com/terraform/language/backend/s3); Kubernetes leader election [pkg.go.dev/k8s.io/client-go/tools/leaderelection](https://pkg.go.dev/k8s.io/client-go/tools/leaderelection)._
