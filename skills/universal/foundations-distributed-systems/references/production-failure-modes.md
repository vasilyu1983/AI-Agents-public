# Production Failure Modes Beyond the Primitives

Load this when an incident or design review involves overload that outlives its trigger, a node that is "healthy" to the cluster but failing for clients, timeouts across several hops, tail latency, or time-based safety (leases, timestamps, snapshot reads). Each section gives the decision rule, the failure it prevents, and when not to apply it.

## Overload that persists after the trigger (metastable failure)

**Owner:** [`qa-resilience`](../../qa-resilience/references/cascading-failure-prevention.md#metastable-failures--the-class-cascading-failure-fixes-do-not-cure). Do not restate it here; the rules below are the distributed-systems view only.

- **Signature:** the dependency recovered but the system did not. Work that timed out is re-queued or retried, so the queue refills faster than it drains.
- **Worked case:** AWS us-east-1, 20 October 2025 ([post-event summary](https://aws.amazon.com/message/101925/)). After DynamoDB returned, EC2's DropletWorkflow Manager lease work timed out, "additional work was queued to reattempt establishing the droplet lease", and the service entered "congestive collapse". Engineers recovered by throttling incoming work and restarting hosts to clear the queues. AWS's stated fix is a rate limit on incoming work "based on the size of the waiting queue" for EC2 data propagation systems.
- **Rule:** client backoff and jitter do not break a loop that is internal to the server. Break it with queue-depth admission control, dropping work whose deadline has passed instead of re-queuing it, and retry budgets. Load-test the recovery path and keep watching after the trigger is removed.

## Gray failure

A component that the failure detector reports healthy while clients see errors or extreme latency: slow disks, partial packet loss, a stuck thread pool. Huang et al. ("Gray Failure: The Achilles' Heel of Cloud-Scale Systems", HotOS 2017) name the defining feature **differential observability**: the system's view of health differs from the application's.

- **Rule:** judge health from the requester's side (client-observed error and latency) as well as from heartbeats. A heartbeat proves a process can answer a heartbeat, nothing more.
- **Consensus link:** a leader that answers heartbeats but cannot fsync in time stalls commits without triggering an election; a follower that cannot fsync looks partitioned. See [`04-raft.md`](../assets/templates/distributed-systems/04-raft.md#production-pitfalls).
- **When not to:** do not eject nodes on a single client's reports; require agreement from several independent observers, or one bad client can evict healthy capacity.

## Deadlines across hops

A per-hop timeout of "above observed p99.9" is a floor for one call. Across a chain, nested per-hop timeouts can add up to more than the caller's own deadline, so downstream work continues after nobody is waiting for it. That wasted work is exactly what feeds the overload loop above.

- **Rule:** propagate an absolute deadline with the request (gRPC deadlines do this); each hop derives its timeout from the remaining budget and refuses work that cannot finish in time.
- **Retries:** a retry must fit inside the remaining deadline; otherwise fail fast.
- **When not to:** background jobs with no waiting caller need a job-level budget instead.

## Hedged and tied requests

Dean and Barroso ("The Tail at Scale", CACM 2013) describe **hedged** requests (send a second copy after a delay, such as the expected p95 latency, and cancel the loser) and **tied** requests (enqueue on two servers that cancel each other once one starts).

- **Rule:** hedge only idempotent reads or operations with an idempotency key; a hedged non-idempotent write is a duplicate generator.
- **Budget:** cap hedges as a fraction of traffic and disable them under overload, or hedging becomes amplification.
- **When not to:** when latency variance comes from the request itself (an expensive query) rather than from the server, a second copy is just as slow.

## Clocks and time-based safety

Wall clocks drift, jump and pause. Any safety property that depends on time needs a stated bound.

- **Leases:** a lease-based read or lock is safe only if clock drift is bounded and the lease margin exceeds it. etcd's raft library states that lease-based reads "can be affected by clock drift" and requires CheckQuorum ([go.etcd.io/raft/v3](https://pkg.go.dev/go.etcd.io/raft/v3)).
- **Hybrid logical clocks (HLC)** (Kulkarni, Demirbas et al., "Logical Physical Clocks", OPODIS 2014) combine physical time with a logical counter: timestamps stay close to wall time but still respect happens-before, which supports snapshot reads and ordering without a dedicated clock service. HLC gives causality, not real-time bounds.
- **Bounded-uncertainty clocks** (Spanner's TrueTime, Corbett et al. 2013) expose an uncertainty interval; commit-wait until the interval has passed buys external consistency at a latency cost equal to the uncertainty.
- **Rule:** if you cannot state the drift bound, do not use time for safety. Use fencing tokens or logical clocks, and keep time only for liveness (timeouts).
