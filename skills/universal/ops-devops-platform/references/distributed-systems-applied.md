# Distributed Systems Applied to DevOps and Platform Engineering

> **Gate before invoking:** Check [`foundations-distributed-systems` § When to Apply](../../foundations-distributed-systems/SKILL.md#when-to-apply) first. The recipes below assume the foundation is the right tool for the situation; the foundation's skip-conditions route you to a different foundation if not.



This file is a **link adapter**: it maps distributed-systems primitives onto platform decisions (etcd sizing and placement, Terraform state locking, GitOps idempotency, Kubernetes leader election, quorum-loss recovery, cross-region rollouts). Theory — CAP/PACELC, FLP, Raft, quorum math, fencing, CRDTs, causal consistency — lives in [foundations-distributed-systems](../../foundations-distributed-systems/SKILL.md); each section links to the file that owns it.

Foundation entry points used throughout:

- Primitive templates: [04-raft](../../foundations-distributed-systems/assets/templates/distributed-systems/04-raft.md) (incl. production-Raft pitfalls: PreVote, CheckQuorum, ReadIndex vs lease reads, fsync flapping, learners/joint consensus), [08-leases-fencing](../../foundations-distributed-systems/assets/templates/distributed-systems/08-leases-fencing.md), [09-quorums](../../foundations-distributed-systems/assets/templates/distributed-systems/09-quorums.md), [07-idempotency](../../foundations-distributed-systems/assets/templates/distributed-systems/07-idempotency.md)
- Split-brain prevention and multi-region writes: [composition-recipes.md](../../foundations-distributed-systems/references/composition-recipes.md)
- Gray failure, deadline propagation, clock uncertainty: [production-failure-modes.md](../../foundations-distributed-systems/references/production-failure-modes.md)
- Retry storms, metastable overload, load shedding (owned by qa-resilience): [cascading-failure-prevention.md](../../qa-resilience/references/cascading-failure-prevention.md)

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

Distributed-systems guarantees are invisible until they fail:

- A 5-member etcd cluster drops to 2 healthy members — writes block while Kubernetes appears to function until the next mutating API call.
- Two CI jobs run `terraform apply` on one workspace without effective locking — one job's changes are silently overwritten.
- A leader-elected worker pauses during a node drain, loses its lease, resumes, and processes the same item as the new leader because the downstream write is not fenced.
- A cross-region restart takes down the region that held the only quorum-capable set of etcd members.

---

## Patterns

### P1 etcd and Kubernetes Control-Plane Quorum Sizing

**Theory**: majority quorum and fault tolerance — [09-quorums](../../foundations-distributed-systems/assets/templates/distributed-systems/09-quorums.md); Raft election/commit — [04-raft](../../foundations-distributed-systems/assets/templates/distributed-systems/04-raft.md); CP-under-partition — [01-cap-pacelc](../../foundations-distributed-systems/assets/templates/distributed-systems/01-cap-pacelc.md).

**Quick reference** (majority quorum = ⌊N/2⌋+1; tolerated failures f = ⌊(N−1)/2⌋):

| N | Quorum | Tolerated failures |
|---|---|---|
| 3 | 2 | 1 |
| 4 | 3 | 1 |
| 5 | 3 | 2 |
| 6 | 4 | 2 |
| 7 | 4 | 3 |

**Sizing decision table**:

| Cluster type | N | Tolerated failures | Notes |
|---|---|---|---|
| Single-region production | 3 | 1 | Standard; spread across 3 zones |
| Single-region, tolerate a zone loss during maintenance | 5 | 2 | Spread 2/2/1 across 3 zones |
| Multi-region | 5 | 2 | Only survives a full region loss when spread 2/2/1 across **3** regions (see P5) |
| Large / high-compliance | 7 | 3 | etcd guidance is to stay at 7 or fewer members; commit waits on the 4th ack |
| Development / staging | 1 | 0 | Not HA — document explicitly |

The 3-vs-5 decision is tolerated failures (1 vs 2) against replica cost and cross-zone traffic — not a latency win for 3. Do not assume a 3-member cluster has lower write p99: its leader waits for the faster of 2 followers, a 5-member leader for the 2nd-fastest of 4, and with iid follower latency the 5-member ack wait is shorter.

**CAP position**: etcd is CP. Without a quorum it refuses writes (and linearizable reads). Kubernetes mutations fail; some reads may still be served from API-server watch caches, so "the cluster looks fine" is not evidence of quorum.

**Cross-region election tuning** (etcd's tuning guide; read the page for your etcd version under [etcd.io/docs](https://etcd.io/docs/)): heartbeat interval ≈ 0.5–1.5× average member RTT; election timeout ≥ 10× RTT. Measure RTT first and compare it with the configured values: at RTT ≈ 40 ms the rules give a 20–60 ms heartbeat and an election timeout of at least 400 ms. Raise both together only if leader changes correlate with RTT spikes or disk-fsync latency (see fsync flapping in [04-raft](../../foundations-distributed-systems/assets/templates/distributed-systems/04-raft.md)).

```
--heartbeat-interval=100     # ms; ~0.5–1.5× measured average RTT
--election-timeout=1000      # ms; ≥10× RTT
```

**Observability**:

```
etcdctl endpoint health --cluster -w table
etcdctl endpoint status --cluster -w table            # leader, raft index, DB size
etcd_server_leader_changes_seen_total                 # rising → instability
etcd_server_has_leader == 0 for 1m                    # quorum lost → page
etcd_disk_wal_fsync_duration_seconds (p99)            # slow disks cause elections
```

---

### P2 Terraform State Locking via Leases with Fencing

**Theory**: leases vs fencing tokens and why a lock alone is not enough — [08-leases-fencing](../../foundations-distributed-systems/assets/templates/distributed-systems/08-leases-fencing.md).

**What Terraform actually provides**: the S3 backend's lock (DynamoDB item keyed by `LockID` = state path, or the S3-native lockfile with `use_lockfile = true`; check the S3 backend docs for your Terraform version to see which locking modes it supports and whether `dynamodb_table` is deprecated) is a **mutual-exclusion lock with no lease and no fencing**:

- The lock does not expire. A crashed runner leaves a stale lock until someone runs `terraform force-unlock <lock-id>` (the UUID in the lock's `Info.ID`, shown in the error message — not the DynamoDB `LockID` key).
- There is no fencing token checked on state writes. A process that believes it still holds the lock (e.g. after a human force-unlocked it) can overwrite state written by the next holder. Safety therefore depends on never force-unlocking a live process.
- S3 bucket versioning is the audit trail and rollback path for state, not a fencing mechanism.

```hcl
terraform {
  backend "s3" {
    bucket       = "myorg-tfstate"
    key          = "prod/us-east-1/cluster.tfstate"
    region       = "us-east-1"
    encrypt      = true
    use_lockfile = true               # S3-native lock (check your Terraform version's backend docs)
    # dynamodb_table = "myorg-tfstate-locks"   # older DynamoDB-based locking
  }
}
```

**Compensating controls** (because there is no fencing):

1. CI-level serialization per workspace (`concurrency` group, queue not cancel) — see R3.
2. `force-unlock` only as a manual, two-person break-glass step after proving the holder is dead.
3. Saved plans: `terraform apply tfplan` refuses a plan whose state has changed since planning ("saved plan is stale"), which catches many lost-update races.

---

### P3 Idempotent Deployment Scripts and GitOps Reconciliation

**Theory**: idempotency keys and receiver contract — [07-idempotency](../../foundations-distributed-systems/assets/templates/distributed-systems/07-idempotency.md), [execution-histories.md](../../foundations-distributed-systems/references/execution-histories.md).

**Platform command semantics**:

| Command | Safe to repeat? |
|---|---|
| `kubectl apply` (prefer `--server-side`) | Yes — desired-state |
| `kubectl create` | No — `AlreadyExists` on retry |
| `helm upgrade --install` | Yes — upsert |
| `helm install` | No — fails on second call |
| `terraform apply` | Convergent (re-plans against current state) |
| Shell that creates resources or appends to files | No, without guards |

**Guard patterns**:

```bash
# create → apply
kubectl create namespace my-app --dry-run=client -o yaml | kubectl apply -f -
kubectl create secret generic db-creds --from-literal=password="${DB_PASSWORD}" \
  --dry-run=client -o yaml | kubectl apply -f -

# append → append-if-absent
grep -qxF "config_value=true" /etc/myapp/config.ini \
  || echo "config_value=true" >> /etc/myapp/config.ini
```

**GitOps**: Argo CD and Flux re-apply on an interval (read the reconciliation interval from your Argo CD or Flux configuration) plus on events, so every manifest must survive repeated application. Helm hooks that create resources are recreated each release; Helm's default hook delete policy is `before-hook-creation` (delete the previous hook resource before creating the new one) — do not remove it without another cleanup path.

**External API calls from deploy scripts** use a key derived from the logical operation, so pipeline retries reuse it:

```bash
curl -X POST https://control-plane/services \
  -H "Idempotency-Key: deploy-${SERVICE}-${GIT_SHA}" \
  -H "Content-Type: application/json" \
  -d "{\"name\": \"${SERVICE}\", \"version\": \"${GIT_SHA}\"}"
# Effect-once only if the control plane dedupes on the key; otherwise retries duplicate.
```

---

### P4 Kubernetes CronJob Leader Election

**Theory**: [08-leases-fencing](../../foundations-distributed-systems/assets/templates/distributed-systems/08-leases-fencing.md); split-brain prevention in [composition-recipes.md](../../foundations-distributed-systems/references/composition-recipes.md).

**Where it applies**: a multi-replica Deployment or operator where only one replica should run a periodic task (CronJobs themselves use `concurrencyPolicy: Forbid` for overlap control, which does not fence external writes either).

**Kubernetes mapping** (`coordination.k8s.io/v1` Lease): `holderIdentity` = leader; `renewTime` + `leaseDurationSeconds` = validity; `leaseTransitions` increments on each holder change and can serve as a monotonic epoch **if captured at acquisition** and enforced downstream.

```go
mgr, err := ctrl.NewManager(ctrl.GetConfigOrDie(), ctrl.Options{
    LeaderElection:                true,
    LeaderElectionID:              "myapp-worker-leader",
    LeaderElectionNamespace:       "myapp",
    LeaderElectionReleaseOnCancel: true,
    LeaseDuration: ptr(15 * time.Second), // controller-runtime defaults: 15s / 10s / 2s
    RenewDeadline: ptr(10 * time.Second),
    RetryPeriod:   ptr(2 * time.Second),
})
```

**Timing constraints** (client-go validates): `LeaseDuration > RenewDeadline > 1.2 × RetryPeriod`. Renewal runs in its own goroutine, so lease length is a failover-speed vs false-failover trade-off, **not** a function of job length — a 5-minute job does not need a 5-minute lease. Size `LeaseDuration` above worst-case API-server latency plus plausible GC/throttling pauses.

**Fencing at the work layer**: capture the epoch when leadership is acquired (not by re-reading the Lease inside the work loop, which races with loss of leadership) and pass it on every external write; the store rejects tokens below its max seen (conditional update, `WHERE epoch <= $token`, etcd txn on revision). See A5.

---

### P5 Multi-Region Failover with Quorum-Loss Runbook

**Theory**: [09-quorums](../../foundations-distributed-systems/assets/templates/distributed-systems/09-quorums.md), [04-raft](../../foundations-distributed-systems/assets/templates/distributed-systems/04-raft.md), [02-flp-impossibility](../../foundations-distributed-systems/assets/templates/distributed-systems/02-flp-impossibility.md) (why no automatic failover can distinguish "slow" from "dead").

**Placement rule** (N=5):

```
2 regions, 3/2 split:  losing the 2-member region keeps quorum;
                       losing the 3-member region loses quorum → manual recovery.
                       No 2-region placement survives loss of either region.
3 regions, 2/2/1:      losing any one region leaves ≥3 of 5 → quorum kept.
                       Preferred for surviving a full region loss.
```

**Detection**:

```bash
kubectl get pods --request-timeout=5s      # "etcdserver: no leader" / timeouts
etcdctl endpoint health --cluster -w table # count healthy members vs quorum
```

**Decision tree**:

```
Lost members recoverable (partition, not data loss)?
  YES → wait; etcd recovers when quorum reconnects. Do not force-new-cluster.
  NO  → manual recovery below (destructive: uncommitted data on lost members is abandoned).
```

**Manual quorum recovery (data-loss path)** — prefer restoring from a snapshot (R2); `--force-new-cluster` is the alternative when the surviving data dir is the freshest copy:

```bash
# 1. Stop kube-apiserver on all control-plane nodes (no writes to a diverging store)
# 2. Pick the survivor with the highest raft index
etcdctl endpoint status -w json --endpoints=10.0.2.10:2379,10.0.2.11:2379 \
  | jq '.[] | {Endpoint, raftIndex: .Status.raftIndex}'
# 3. On that member only: restart as a single-member cluster
etcd --force-new-cluster --data-dir=/var/lib/etcd --name=etcd-surviving-1 \
  --initial-advertise-peer-urls=https://10.0.2.10:2380
# 4. Verify health, then add replacements ONE at a time
etcdctl member add etcd-new-2 --peer-urls=https://10.0.2.20:2380
#    (start each with --initial-cluster-state=existing; wait for healthy before the next)
# 5. Start kube-apiserver; verify
kubectl get --raw='/readyz?verbose'        # componentstatuses is deprecated
kubectl get nodes
```

During quorum loss, clients and controllers retry mutations; stop non-critical retriers so recovery is not met by a retry storm ([qa-resilience](../../qa-resilience/references/cascading-failure-prevention.md)).

---

### P6 CRDT-Backed Feature-Flag State for Multi-Region GitOps

**Theory**: OR-Set semantics and merge — [06-crdts](../../foundations-distributed-systems/assets/templates/distributed-systems/06-crdts.md); multi-region writes — [composition-recipes.md](../../foundations-distributed-systems/references/composition-recipes.md).

**When it applies**: flags must be writable in a region **during a partition** from the primary and merge deterministically afterwards. Model enabled flags as an OR-Set (concurrent enable/disable → enable wins — confirm that bias is acceptable for kill switches; for kill switches you usually want disable-wins, which needs a different CRDT or a single-writer rule). Do not hand-roll the merge; use the foundation's definition.

**Default for most platform teams**: a managed flag service with multi-region replication, local reads, writes to one primary region. Reserve CRDTs for the partition-writable case.

**Flag → migration ordering**: when a flag gates a migration, the migration job must observe the flag write before acting (causal dependency — [10-causal-consistency](../../foundations-distributed-systems/assets/templates/distributed-systems/10-causal-consistency.md)). In practice: the migration job reads the flag's version from the same store and refuses to run on a version older than the one recorded in the release.

---

### P7 Cross-Region Rolling Restart Correctness via Causal Consistency

**Theory**: [10-causal-consistency](../../foundations-distributed-systems/assets/templates/distributed-systems/10-causal-consistency.md), [11-broadcast-protocols](../../foundations-distributed-systems/assets/templates/distributed-systems/11-broadcast-protocols.md); clock-skew hazards in [production-failure-modes.md](../../foundations-distributed-systems/references/production-failure-modes.md).

**Rule**: advance to region N+1 only after region N is observed healthy **at config version V**. A timestamp check is not enough (skew, stale replicas); gate on an explicit version that the pods themselves report.

```bash
# Stamp the pod template with the config version (this, unlike annotating the
# ConfigMap, reaches the pods and triggers a rollout)
V="$(git rev-parse --short HEAD)"
kubectl -n myapp patch deployment myapp --type merge \
  -p "{\"spec\":{\"template\":{\"metadata\":{\"annotations\":{\"config-version\":\"${V}\"}}}}}"

# Wait until every replica runs the new template and is Ready
kubectl -n myapp rollout status deployment/myapp --timeout=300s

# Double-check no Ready pod reports an older version before advancing regions
kubectl -n myapp get pods -l app=myapp \
  -o jsonpath='{range .items[*]}{.metadata.annotations.config-version}{"\n"}{end}' \
  | grep -vx "${V}" && { echo "stale pods remain"; exit 1; } || echo "region at ${V}"
```

**GitOps form**: push the change once; before restarting region N+1, require Argo CD sync status / Flux reconciliation for region N to report the same revision. That acknowledgement is the causal dependency.

---

## Anti-Patterns

### A1 Redlock and the Distributed-Lock Trap

**Theory**: [08-leases-fencing](../../foundations-distributed-systems/assets/templates/distributed-systems/08-leases-fencing.md) (why fencing is necessary), [02-flp-impossibility](../../foundations-distributed-systems/assets/templates/distributed-systems/02-flp-impossibility.md).

Redlock (lock on a majority of independent Redis nodes within the TTL) relies on timing for safety. Kleppmann's critique ("How to do distributed locking", 2016): client A takes the lock, stalls in a GC pause longer than the TTL, the lock expires, client B takes it and writes, A resumes and writes too. Nothing in the storage path rejects A. Clock jumps and network delay produce the same outcome.

**Correct alternative**: a lock from a CP store (etcd, ZooKeeper) **plus** a fencing token checked by the resource. With etcd, create the lock key only if absent, attached to a lease, and use its revision as the token:

```python
import etcd3
client = etcd3.client()
lease = client.lease(ttl=15)
key = "/locks/myapp/critical-section"
ok, _ = client.transaction(
    compare=[client.transactions.create(key) == 0],          # key must not exist
    success=[client.transactions.put(key, "holder-pod", lease)],
    failure=[],
)
if ok:
    _, meta = client.get(key)
    token = meta.mod_revision        # monotonic across grants → fencing token
    do_critical_work(fencing_token=token)   # storage must reject token < max seen
    lease.revoke()
```

**Rule**: never use Redlock or any TTL-only lock to protect shared persistent state. It is acceptable for advisory, efficiency-only locking (cache warming, best-effort dedupe) where a duplicate is harmless.

---

### A2 Even-Node etcd Clusters

**Theory**: [09-quorums](../../foundations-distributed-systems/assets/templates/distributed-systems/09-quorums.md).

A team runs 4 etcd members because it has 4 control-plane nodes. N=4 needs quorum 3 and tolerates only ⌊(4−1)/2⌋ = 1 failure — the same as N=3 — while adding a member that can fail and a larger quorum to reach.

**Fix**: etcd membership need not equal control-plane node count. Run etcd on 3 of the 4 nodes, or add a fifth etcd member to reach N=5.

```bash
etcdctl member list -w table | grep -c started   # 2, 4 or 6 → fix the size
```

---

### A3 Terraform State Locking Without Fencing

**Theory**: [08-leases-fencing](../../foundations-distributed-systems/assets/templates/distributed-systems/08-leases-fencing.md).

**Pattern**: no lock configured on the backend, or `-lock=false` used to get past a stale lock.

**Failure**: two applies read the same state version, each computes and applies its own plan, each writes a new state. The last write wins; the other job's resources exist in the cloud but not in state and resurface as drift or orphans on the next plan.

**Fix**: always configure locking (P2); treat `-lock=false` and `force-unlock` as logged, two-person break-glass actions; serialize per workspace in CI as a second layer (R3). Because the lock has no fencing, these process controls are the safety mechanism.

---

### A4 Non-Idempotent Deployment Scripts

**Theory**: [07-idempotency](../../foundations-distributed-systems/assets/templates/distributed-systems/07-idempotency.md).

A deploy step uses `kubectl create` / `helm install`. On pipeline retry it fails with `AlreadyExists` and later steps never run — e.g. app v2 is deployed but still reads the v1 ConfigMap.

**Audit** (lookarounds need PCRE2, hence `-P`):

```bash
rg -P "kubectl create(?!.*--dry-run)" deploy/ scripts/
rg -P "helm install(?!.*--generate-name)" deploy/ scripts/
# Convert to: kubectl apply (from --dry-run=client -o yaml) / helm upgrade --install
```

---

### A5 Assuming Leader-Elected Workers Are Unique Without a Fencing Token

**Theory**: [08-leases-fencing](../../foundations-distributed-systems/assets/templates/distributed-systems/08-leases-fencing.md), [02-flp-impossibility](../../foundations-distributed-systems/assets/templates/distributed-systems/02-flp-impossibility.md).

A worker holds a Kubernetes Lease and sends notifications or mutates external state without a conditional write. A pause (GC, CPU throttling, API-server slowness) lets the lease expire mid-work; a second leader starts; both act. Result: duplicate notifications, rows, API calls, or charges. No election mechanism can tell a paused leader from a dead one in bounded time, so the destination must reject stale writers.

**Audit**:

```bash
rg "leaderelection|LeaderElection|coordination.k8s.io" --type go internal/ pkg/
# For each hit, confirm the downstream write carries one of:
#   idempotency key | compare-and-swap (etcd txn on revision) |
#   UPDATE ... WHERE epoch <= $token (or version = expected)
```

---

## Recipes

### R1 etcd Quorum Sizing and Health Runbook

**Sizing**: choose f (member failures to survive), then N = 2f+1 and place so that no single failure domain holds a quorum's worth of the survivors you need. To survive a full region loss with N=5, use 3 regions at 2/2/1 (P5); two regions cannot guarantee it.

**Provisioning checklist**:

```bash
# Dedicated low-latency SSD/NVMe for the WAL; slow fsync is the top cause of
# spurious elections (see etcd hardware and tuning docs; sizing is workload-dependent)
sysctl -w vm.swappiness=0

cat > /etc/etcd/etcd.conf.yml <<EOF
heartbeat-interval: 100          # tune per P1 from measured RTT
election-timeout: 1000
snapshot-count: 10000
quota-backend-bytes: 8589934592  # 8 GiB; etcd's suggested upper bound
EOF

etcdctl member list -w table
etcdctl endpoint health --cluster -w table
```

**Prometheus alerts** (thresholds shown for N=5, quorum 3):

```yaml
groups:
  - name: etcd-quorum
    rules:
      - alert: EtcdNoLeader
        expr: etcd_server_has_leader == 0
        for: 1m
        labels: {severity: critical}
        annotations: {summary: "etcd member has no leader — Kubernetes writes blocked"}
      - alert: EtcdQuorumAtRisk
        expr: count(etcd_server_has_leader == 1) < 4     # one more loss → at quorum
        for: 5m
        labels: {severity: warning}
      - alert: EtcdHighLeaderChanges
        expr: increase(etcd_server_leader_changes_seen_total[1h]) > 3
        labels: {severity: warning}
        annotations: {summary: "leader instability — check RTT and WAL fsync latency"}
      - alert: EtcdDatabaseSizeNearQuota
        expr: etcd_mvcc_db_total_size_in_bytes / etcd_server_quota_backend_bytes > 0.8
        labels: {severity: warning}
```

**Defragmentation** (when DB size approaches quota; defrag blocks the member while it runs):

```bash
for ep in $(etcdctl member list -w json | jq -r '.members[].clientURLs[0]'); do
  etcdctl defrag --endpoints="${ep}"   # one member at a time, never all at once
  sleep 30
done
etcdctl endpoint status --cluster -w table
```

---

### R2 Multi-Region Failover with Quorum-Loss Recovery

**Pre-requisites** (in place before the incident):

1. Periodic `etcdctl snapshot save` shipped off-cluster (e.g. every 15 min). Velero backs up Kubernetes API objects, not etcd snapshots — it complements, not replaces, etcd snapshots.
2. Member list and runbook available offline.
3. Bastion access to surviving members; IaC to provision replacements.

**Incident sequence**:

```
Assess   — confirm quorum loss; list survivors and raft index; partition vs node loss; P1.
Contain  — stop non-critical retriers; announce "no deploys/config changes; reads may be stale".
           If partition: wait, do not intervene.
Recover  — partition healed → confirm leader elected.
           Nodes lost → restore snapshot (below) or --force-new-cluster from freshest survivor (P5);
           add members one at a time; restart kube-apiserver.
Verify   — /readyz, nodes Ready, no unexpected Pending/Failed pods, GitOps apps Synced,
           smoke-test pod.
After    — diff against the last snapshot to find lost writes; reconcile; postmortem
           (placement rule? snapshot interval?).
```

Target times for each phase are an organizational SLO choice; set them from your own drills.

**Snapshot restore**:

```bash
aws s3 cp s3://myorg-etcd-snapshots/${SNAPSHOT_FILE} /tmp/
etcdutl snapshot restore /tmp/${SNAPSHOT_FILE} \
  --name etcd-recovery-1 \
  --initial-cluster etcd-recovery-1=https://10.0.2.10:2380 \
  --initial-cluster-token etcd-recovery-token \
  --initial-advertise-peer-urls https://10.0.2.10:2380 \
  --data-dir /var/lib/etcd
# Start etcd on the restored data dir (no --force-new-cluster needed after a restore)
```

---

### R3 Idempotent Deployment Pipeline with Fenced Terraform State

**Goal**: every step safe to retry; Terraform writes serialized; partial failures do not corrupt state.

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
    concurrency:                                   # layer 1: one apply per workspace
      group: terraform-prod-us-east-1
      cancel-in-progress: false                    # queue, never cancel mid-apply
    steps:
      - uses: actions/checkout@v4
      - uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::123456789012:role/GitHubActionsDeployRole
          aws-region: us-east-1
      - run: terraform -chdir=terraform/envs/prod-us-east-1 init
      - name: Plan                                 # layer 2: backend lock
        run: terraform -chdir=terraform/envs/prod-us-east-1 plan -out=tfplan -lock-timeout=120s
        # -lock-timeout waits for a HELD lock to be released; stale locks never expire.
        # Never use -lock=false.
      - name: Apply
        run: terraform -chdir=terraform/envs/prod-us-east-1 apply tfplan
        # Re-acquires the lock; refuses a stale saved plan if state changed since plan.
      - name: Kubernetes sync (idempotent)
        run: kubectl apply -f k8s/prod/ --server-side --force-conflicts
      - name: Converged
        run: kubectl rollout status deployment/myapp -n myapp --timeout=300s
```

**Stale-lock break-glass** (human-only, two approvals):

```bash
# 1. Prove the holder is dead: read Who/Created from the lock info (DynamoDB item or
#    the error message) and confirm that CI job is no longer running.
# 2. Inspect recent state versions for a partial apply
aws s3api list-object-versions --bucket myorg-tfstate \
  --prefix prod/us-east-1/cluster.tfstate \
  --query 'sort_by(Versions, &LastModified)[-3:].[VersionId, LastModified]' --output table
# 3. Unlock with the lock ID (UUID), then re-plan before any apply
terraform -chdir=terraform/envs/prod-us-east-1 force-unlock <lock-id>
terraform -chdir=terraform/envs/prod-us-east-1 plan
```

**Idempotency gate** (CI, pre-merge):

```bash
rg -P "kubectl create(?!.*(--dry-run|-h|--help))" --type sh --type yaml -g '!**/.archive/**' .
rg -P "helm install(?!.*--generate-name)" --type sh --type yaml -g '!**/.archive/**' .
# After applying to a test env, a second plan must be empty:
terraform plan -detailed-exitcode   # 0 = no changes, 2 = changes pending, 1 = error
```

---

## Cross-References

### Foundation

- [foundations-distributed-systems](../../foundations-distributed-systems/SKILL.md) — all primitives; [primitives-overview.md](../../foundations-distributed-systems/references/primitives-overview.md); [patterns-scenarios-traps.md](../../foundations-distributed-systems/references/patterns-scenarios-traps.md); [composition-recipes.md](../../foundations-distributed-systems/references/composition-recipes.md); [production-failure-modes.md](../../foundations-distributed-systems/references/production-failure-modes.md)
- [foundations-formal-methods](../../foundations-formal-methods/SKILL.md) — when a custom coordination protocol (e.g. an in-house leader-election or lock service) needs model checking

### Sibling Applied References (ops-devops-platform)

- [control-theory-applied.md](control-theory-applied.md) — deployment control loops, canary analysis, CI queue stabilization
- [queueing-theory-applied.md](queueing-theory-applied.md) — capacity planning, saturation SLOs, pipeline bottlenecks
- [theory-of-constraints-applied.md](theory-of-constraints-applied.md) — CI/CD throughput recovery

### Related Skills

- [ops-incident-response](../../ops-incident-response/SKILL.md) — quorum-loss recovery feeds incident runbooks
- [qa-resilience](../../qa-resilience/SKILL.md) — chaos tests for quorum behavior and fencing; [cascading-failure-prevention](../../qa-resilience/references/cascading-failure-prevention.md) for retry storms and overload
- [software-architecture-design](../../software-architecture-design/SKILL.md) — upstream distributed-design decisions

---

_Sources: theory sources live in each foundation template's Sources section. Platform sources: etcd docs ([etcd.io/docs](https://etcd.io/docs/), incl. tuning and disaster recovery); Terraform S3 backend ([developer.hashicorp.com/terraform/language/backend/s3](https://developer.hashicorp.com/terraform/language/backend/s3)); client-go leader election ([pkg.go.dev/k8s.io/client-go/tools/leaderelection](https://pkg.go.dev/k8s.io/client-go/tools/leaderelection)); Kleppmann, "How to do distributed locking" (2016)._
