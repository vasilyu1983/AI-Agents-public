# Primitive 8: Leases and Fencing Tokens

**Sources**: Chandra et al. 2007 (Paxos Made Live); Kleppmann 2017; Gray & Cheriton 1989 (leases).

---

## Definition

### Leases

A **lease** is a time-bounded grant of authority to a process. The holder may act as primary (write coordinator, lock holder, leader) until the lease expires. Leases prevent indefinite lock retention after process crashes.

**Properties**:
- Lease duration `T_L` must be longer than the maximum clock skew between nodes.
- The holder must renew before expiry (heartbeat to the lease authority).
- After expiry, the lease authority can grant a new lease to a different holder.
- Lease-based leadership is safe only if the holder stops acting as primary before the lease expires — not at expiry, but with a safety margin.

### Fencing Tokens

A **fencing token** is a monotonically increasing integer issued with each new lease grant. Every write operation must include the current fencing token. The storage layer (or any downstream service) **rejects writes with a token lower than the maximum token it has ever seen**.

**How it works**:
```
Lease authority grants lease to Node A: token = 42
Node A writes with token 42 → accepted

Node A pauses (GC, slow network)
Lease authority grants lease to Node B: token = 43
Node B writes with token 43 → accepted

Node A resumes, tries to write with token 42 → REJECTED (storage saw 43)
```

**Why fencing is necessary**: A lease expiry only prevents the holder from *knowing* it is still primary. A slow or paused process may not know its lease expired. The storage layer must independently reject stale writes.

---

## When to Use

- Distributed lock services (ZooKeeper, etcd, Chubby) where the lock holder may pause.
- Primary election in database replication (only one node writes at a time).
- Any system with a "primary" or "leader" role that must not be held by two nodes simultaneously.
- Object storage with conditional writes (S3 object versioning, ETag-based if-match).

---

## Inputs

| Input | Description |
|-------|-------------|
| Lease duration | Must be > max clock skew; typical range 5–30 seconds |
| Fencing token source | Monotonically increasing integer from the lease authority (ZooKeeper zxid, etcd revision) |
| Storage layer | Must enforce fencing token check on every write |
| Clock synchronisation | Bounded clock skew assumption required for lease safety |

---

## Outputs

| Output | Description |
|--------|-------------|
| At-most-one primary | At any point in time, at most one node holds a valid lease |
| Stale-write rejection | Storage rejects writes from deposed holders |
| Audit log | Sequence of lease grants with token numbers |

---

## Failure Modes

| Failure | Cause | Consequence |
|---------|-------|-------------|
| Lease without fencing token | Deposed leader resumes after GC pause believing it still holds the lease | Split-brain: two nodes write concurrently; later writes from the deposed leader are applied |
| Fencing token checked only by application, not storage | Application crashes after token check but before write; or an adversarial client bypasses the check | Split-brain corruption |
| Lease duration shorter than max GC pause | JVM stop-the-world GC can exceed lease duration; leader is demoted while still "running" | Unnecessary failover; or split-brain if fencing is absent |
| Clock synchronisation assumption violated | Nodes have unbounded clock skew; lease expiry on the authority happens before the holder's clock shows expiry | Both the old and new holders act as primary simultaneously |
| Renewing a lease after it has been revoked | Application renews via a cached authority connection; revocation is not seen | Holder believes it has a valid lease; writes proceed with a stale token |

---

## Worked Example

**Scenario**: A distributed PostgreSQL cluster with one primary and two replicas. Automatic failover promotes a replica to primary if the current primary is unreachable.

**Problem**: The primary (node A) experiences a 60-second GC pause. The failover system promotes node B as primary and grants it fencing token 2. Node A wakes up from the GC pause believing it is still primary (token 1) and attempts to write to the shared WAL storage.

**Without fencing**: Node A and node B both write to the WAL → data corruption.

**With fencing**:
1. Failover system grants node B lease + token 2.
2. Storage layer records: maximum token seen = 2.
3. Node A resumes and sends write with token 1.
4. Storage layer rejects: `token 1 < max seen (2)`.
5. Node A receives the rejection, queries the lease authority, learns it has been demoted, and stops accepting writes.

**Implementation note**: The fencing token must be passed through every layer of the write path (application → connection pool → storage). A single bypassed layer defeats the guarantee.

---

## Sources

- Gray, J., & Cheriton, D. (1989). Leases: An Efficient Fault-Tolerant Mechanism for Distributed File Cache Consistency. SOSP.
- Chandra, T., Griesemer, R., & Redstone, J. (2007). Paxos Made Live. PODC. [doi.org/10.1145/1281100.1281103](https://doi.org/10.1145/1281100.1281103)
- Kleppmann, M. (2017). Designing Data-Intensive Applications, Chapter 8. [dataintensive.net](https://dataintensive.net/)
- ZooKeeper documentation — ephemeral nodes and sequential znodes as fencing tokens. [zookeeper.apache.org/doc/current](https://zookeeper.apache.org/doc/current/)
