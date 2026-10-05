# Operational Patterns and Standards

Operational guidance for production tuning and safe database changes. This file focuses on PostgreSQL, MySQL, and SQL Server. Oracle and SQLite remain lighter-support paths.

## Table of Contents

- [Production Tuning Workflow](#production-tuning-workflow)
- [PostgreSQL Operational Notes](#postgresql-operational-notes)
- [Features Added in PostgreSQL 18](#features-added-in-postgresql-18)
- [Planner and Estimation](#planner-and-estimation)
- [Operational Cautions](#operational-cautions)
- [work_mem Is Per-Node, Per-Connection](#work_mem-is-per-node-per-connection)
- [Idle in Transaction Blocks DDL, Which Then Blocks Everything](#idle-in-transaction-blocks-ddl-which-then-blocks-everything)
- [MySQL Operational Notes](#mysql-operational-notes)
- [Optimizer and Statistics](#optimizer-and-statistics)
- [Reliability and Change Safety](#reliability-and-change-safety)
- [Online Schema Change: gh-ost vs pt-online-schema-change](#online-schema-change-gh-ost-vs-pt-online-schema-change)
- [SQL Server Operational Notes](#sql-server-operational-notes)
- [Parameter-Sensitive Workloads](#parameter-sensitive-workloads)
- [Concurrency](#concurrency)
- [Shared Operational Defaults](#shared-operational-defaults)
- [Statistics Before Indexes](#statistics-before-indexes)
- [Safe Migrations](#safe-migrations)
- [Reliability Drills](#reliability-drills)
- [Template Selection](#template-selection)
- [Anti-Patterns](#anti-patterns)
- [Final Check](#final-check)

## Production Tuning Workflow

1. Measure baseline latency, reads, CPU, waits, and result size.
2. Capture plan evidence with the engine-appropriate tool.
3. Write the bottleneck hypothesis.
4. Change one variable.
5. Verify performance and result correctness.
6. Monitor long enough to catch low-frequency workloads.

Use [template-performance-tuning-worksheet.md](../assets/cross-platform/template-performance-tuning-worksheet.md) to keep the loop explicit.

## PostgreSQL Operational Notes

### Features Added in PostgreSQL 18

- async I/O is a PostgreSQL 18 capability; verify whether it is enabled and relevant before attributing gains to it
- `pg_aios` exists for async-I/O observability
- `uuidv7()` gives time-ordered UUIDs with better index locality than UUIDv4 in append-heavy OLTP patterns
- `pg_upgrade` retains optimizer statistics, which reduces post-upgrade plan churn

### Planner and Estimation

- PostgreSQL 18 skip scan improves some multicolumn B-tree cases; verify with plan output instead of assuming the composite index is now enough
- `CREATE STATISTICS` is still the preferred fix for correlated-predicate misestimation
- use `pg_stat_statements` plus `pg_stat_io` when latency and I/O stories disagree

### Operational Cautions

- avoid unbounded replication-slot retention
- monitor autovacuum lag, freeze age, and table bloat
- do not replace query-shape fixes with blanket `work_mem` increases

### work_mem Is Per-Node, Per-Connection

`work_mem` is not a per-connection budget and is definitely not a server-wide one. It
is the limit for **each node of the execution plan for each running query**. A single
query with several sorts and hash joins can allocate `work_mem` several times over, and
every concurrent session does the same independently.

The math that matters for OOM risk is therefore:

```text
worst-case memory ≈ work_mem × (plan nodes needing memory) × (concurrent queries)
```

Angelakos demonstrates this concretely: with `work_mem = 2GB` and 1,000 connections on
a 16 GB instance, *"we potentially allocated 2 GB of RAM for each node of the execution
plan for each running query"* (*PostgreSQL Mistakes and How to Avoid Them*, §6.2,
p. 103) — and the Linux OOM killer terminated a backend within seconds of the load
starting.

Why an OOM kill is worse than it looks: PostgreSQL responds to a killed backend by
terminating all other active backends, because shared memory may be corrupt, then
enters crash recovery. That can cascade into a failover. The OOM killer also picks its
victim by OOM score, so it may kill some other critical process rather than the
offending backend.

Additional factors when sizing:

- **`hash_mem_multiplier`** scales the limit for hash-based nodes (hash joins, hash
  aggregation) relative to `work_mem`, so those nodes get `work_mem ×
  hash_mem_multiplier`. It defaults to a value above 1 in current PostgreSQL versions —
  check your version's default, and include the multiplier in the worst-case math for
  hash-heavy plans.
- **Parallel query** multiplies again: each parallel worker gets its own allocation for
  its own nodes.

Practical approach: set a conservative global `work_mem` sized for ordinary queries,
and raise it per session for the specific reporting or batch queries that need it —
`work_mem` can be `SET` at session level. The tradeoff is real in both directions: too
small and sorts and aggregations spill to temporary files on disk, which is orders of
magnitude slower than memory; too large and the server dies. There is no formula that
avoids testing against a representative workload.

The same caution applies to `shared_buffers`: the widely repeated "25% of RAM" figure
is a starting point, not a rule. Angelakos notes an OLTP workload may benefit from
large shared memory that holds the working set, while the same setting is wasted on an
OLAP workload that visits each buffer once. Also verify units — bare integers for
`shared_buffers` mean 8 kB buffers, not megabytes.

### Idle in Transaction Blocks DDL, Which Then Blocks Everything

This is the single most common way a healthy-looking database stalls completely, and
the cause is often a developer's forgotten psql session.

The cascade, from Angelakos §6.5.1 (pp. 110–112):

1. **Client A** runs `BEGIN; SELECT * FROM mytable;` and then does nothing. The
   transaction stays open, holding an `ACCESS SHARE` lock — the weakest lock there is.
   It cannot block reads or writes.
2. **Client B** runs `ALTER TABLE mytable ADD COLUMN ...`, which needs `ACCESS
   EXCLUSIVE`. That conflicts with `ACCESS SHARE`, so Client B waits.
3. **Client C** runs `SELECT 1 FROM mytable` — an ordinary read that Client A's lock
   would never have blocked. It hangs anyway, because it has to queue *behind* the
   pending `ACCESS EXCLUSIVE` request.

That third step is the non-obvious part and the reason this becomes an outage rather
than a slow query. Angelakos: *"while Client B waits its turn to obtain the lock it
needs on mytable, any other transaction or query that needs to access mytable will be
blocked because they have to queue behind it!"* Every subsequent query on the table
stalls, and the table is effectively down until Client A commits.

The secondary damage: `idle in transaction` sessions can also prevent autovacuum from
cleaning up, if they have modified data or run at `REPEATABLE READ` / `SERIALIZABLE`.
Vacuum cannot remove rows that must stay visible to the open transaction, which drives
bloat and, over a long enough period, transaction ID wraparound risk.

**Mitigations, in order:**

- **Set `lock_timeout` before every DDL statement.** This is the highest-value control.
  It makes the DDL give up quickly instead of parking an `ACCESS EXCLUSIVE` request in
  the queue where it blocks all traffic. Failing fast and retrying is almost always
  better than an open-ended wait.

  ```sql
  BEGIN;
  SET LOCAL lock_timeout = '3s';
  ALTER TABLE mytable ADD COLUMN description text;
  COMMIT;
  ```

- **Set `idle_in_transaction_session_timeout`** so abandoned transactions cannot hold
  locks indefinitely. The tradeoff: applications that legitimately do processing between
  `BEGIN` and `COMMIT` need the timeout set above their longest such gap, and must
  tolerate being disconnected.
- **Monitor for it.** Alert on `state = 'idle in transaction'` with a large
  `now() - xact_start` — see the queries in
  [connection-pooling-patterns.md](connection-pooling-patterns.md#postgresql).
- **Retry loops for DDL.** With `lock_timeout` set, migrations should retry rather than
  fail the deploy.

Combine this with the migration checklist below: a schema change that is safe in
isolation is not safe on a database with long-lived transactions.

## MySQL Operational Notes

Run production on an LTS line, not an Innovation release. Read the MySQL support-policy page for which LTS lines are supported and when each reaches end of life, and schedule the upgrade before the line in use reaches EOL; the user's exact version comes from `SELECT @@version`.

### Optimizer and Statistics

- histograms help when skewed distributions confuse the optimizer
- invisible indexes are the safest way to test index removal
- OR predicates may be handled by index merge; verify before rewriting to UNION or UNION ALL
- HyperGraph optimizer: check whether your version ships it and whether it is on by default; test at session scope before any global change

```sql
-- Enable HyperGraph optimizer for a session (versions that ship it)
SET optimizer_switch='hypergraph_optimizer=on';
-- Verify with EXPLAIN (will show "hypergraph" in output)
```

### Reliability and Change Safety

- keep slow query log or Performance Schema visibility enabled
- monitor binlog retention and replica lag as part of change planning

#### Online Schema Change: gh-ost vs pt-online-schema-change

Both `gh-ost` and `pt-online-schema-change` make large-table DDL non-blocking, but they
do it by different mechanisms, and the choice constrains your schema platform. Start
by checking whether you need an external tool at all:

> any external tool running your schema changes for you will need to make entire
> copies of the table you are changing. The tool merely makes the process less
> impactful and does not require disruptive write locks, but only native DDL in MySQL
> can alter table schemas without a full table copy.
>
> — *High Performance MySQL*, 4th ed., ch. 6, p. 150

So native `INPLACE` / `INSTANT` DDL is the first thing to check. MySQL 8.0 expanded
native DDL coverage substantially but not universally — primary key changes, charset
changes, per-table encryption, and adding or removing foreign keys still cannot be done
with an `INPLACE` alter. Even a supported change on a very large table can roll back if
InnoDB's internal change log grows too large, and native DDL gives you no throttling
control. Those are the real reasons to reach for an external tool.

| Aspect | `pt-online-schema-change` | `gh-ost` |
|--------|---------------------------|----------|
| Change tracking | Triggers on the live table | Tails the binlog via a replica connection |
| Write amplification | Yes — trigger fires on every write | No triggers on the live table |
| Foreign keys | Attempts broader support, with tradeoffs | **Bails entirely** if the table has FKs |
| Concurrent migrations on one table | Not possible (trigger limits) | Possible |
| Requires binlog access | No | Yes (row-based preferred) |

The trigger mechanism is where pt-osc's costs come from: every write to the live table
does extra work for the duration of the copy. That penalty is usually invisible, but at
high transaction throughput it is measurable and must be watched and throttled. Before
MySQL 8.0, trigger limits also mean pt-osc cannot run against a table that already has
a trigger with the same action, and cannot run two migrations on one table at once.

gh-ost avoids all of that by connecting as a replica and consuming row-based
replication logs as its changelog — no triggers on the production table. The cost is
the foreign-key restriction, and it is not a small one: **choosing gh-ost is a
schema-platform commitment.** If you standardize on gh-ost you are committing to a
database platform without foreign keys, and that decision needs to be enforced in
schema linting and precommit checks, not left to convention. Botros and Tinley
recommend gh-ost for teams new to automated schema change *"as long as you are also
disciplined around not introducing foreign keys."*

Prefer `pt-online-schema-change` when foreign keys already exist and removing them is
not realistic, or when binlogs are not accessible to the tool.

## SQL Server Operational Notes

These features have different release, compatibility-level and configuration prerequisites. Check the [Microsoft IQP feature matrix](https://learn.microsoft.com/en-us/sql/relational-databases/performance/intelligent-query-processing?view=sql-server-ver17) for the installed engine and each feature before recommending it.

### Parameter-Sensitive Workloads

- Check DOP feedback and CE feedback for expressions separately; do not infer their availability or enabled state from one IQP release label. Check Query Store and the relevant database-scoped configuration.
- OPPO (Optional Parameter Plan Optimization) replaces manual hint-based workarounds for optional-parameter queries; check database compatibility level and `OPTIONAL_PARAMETER_OPTIMIZATION` database-scoped config before assuming it is active

### Concurrency

- Optimized locking reduces lock memory and blocking risk; verify prerequisites and isolation settings before recommending it
- Query Store should be part of the default incident workflow for plan regressions
- Readable-secondary Query Store can preserve plan history outside the primary

## Shared Operational Defaults

### Statistics Before Indexes

Prefer this order:

1. refresh or validate statistics
2. inspect parameter sensitivity
3. add or reshape indexes only if the access path still looks wrong

### Safe Migrations

- capture rollback path before DDL
- stage large-table changes
- validate row counts and critical query plans after the change
- pair schema changes with connection-pool and lock-risk checks

### Reliability Drills

- [ ] restore backups on a schedule
- [ ] test replica promotion or failover with a written runbook
- [ ] track storage growth, WAL/binlog growth, and replication lag
- [ ] set alerts for latency, error rate, connection pressure, and blocking

## Template Selection

| Problem | Template |
|---------|----------|
| Slow query intake | [template-slow-query.md](../assets/cross-platform/template-slow-query.md) |
| Plan review | [template-explain-analysis.md](../assets/cross-platform/template-explain-analysis.md) or engine-specific explain template |
| Index review | [template-index.md](../assets/cross-platform/template-index.md) or engine-specific index template |
| Locking / deadlocks | [template-lock-analysis.md](../assets/cross-platform/template-lock-analysis.md) |
| Migration planning | [template-migration.md](../assets/cross-platform/template-migration.md) |
| Backup / restore drill | [template-backup-restore.md](../assets/cross-platform/template-backup-restore.md) |
| Security / privilege review | [template-security-audit.md](../assets/cross-platform/template-security-audit.md) |

## Anti-Patterns

- using engine-version features without checking version and compatibility level
- dropping indexes based only on one day's usage
- treating planner improvements as a substitute for real workload validation
- changing query shape, index design, and memory knobs all at once
- tuning from synthetic tiny datasets

## Final Check

- [ ] Recommendation is tied to observed evidence
- [ ] Version-sensitive features checked against vendor docs
- [ ] Rollback path documented for risky changes
- [ ] Monitoring exists for the thing being changed
