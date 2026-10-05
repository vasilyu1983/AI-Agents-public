# Transactions and Storage Engines

Two design-time concerns that sit *underneath* schema: which concurrency anomalies your isolation level actually blocks, and which storage engine shape fits your write/read mix. Both are schema decisions in disguise — a write-skew-prone invariant is usually fixable with a constraint or a lock target you design into the schema, and engine choice constrains what index and transaction behavior you can rely on.

Primary source for both sections: Martin Kleppmann, *Designing Data-Intensive Applications* (O'Reilly, 1st ed. 2017) — Ch.7 "Transactions" and Ch.3 "Storage and Retrieval". The **mechanisms** below are durable. Any **vendor-specific** claim about which isolation level a given database implements, or what its default is, changes between releases: DDIA's own tables are 2017-era. Verify against current vendor documentation before relying on a vendor detail.

## Table of Contents

- [Isolation Anomaly Taxonomy](#isolation-anomaly-taxonomy)
- [What Each Isolation Level Blocks](#what-each-isolation-level-blocks)
- [Write Skew: The Anomaly Snapshot Isolation Does Not Prevent](#write-skew-the-anomaly-snapshot-isolation-does-not-prevent)
- [Spotting Write-Skew-Prone Invariants](#spotting-write-skew-prone-invariants)
- [Mitigations, Ranked](#mitigations-ranked)
- [Serializability Implementations](#serializability-implementations)
- [LSM-Tree vs B-Tree Storage Engines](#lsm-tree-vs-b-tree-storage-engines)
- [Compaction Falling Behind Ingest](#compaction-falling-behind-ingest)
- [LSM Compaction Strategies](#lsm-compaction-strategies)
- [The RUM Conjecture](#the-rum-conjecture)
- [Bw-Trees](#bw-trees)
- [Choosing an Engine](#choosing-an-engine)

## Isolation Anomaly Taxonomy

DDIA's Ch.7 summary characterizes weak isolation by the race conditions each level permits. Learn the anomalies, not the level names — level names are inconsistently implemented across vendors ("the meaning of 'repeatable read' varies significantly").

| Anomaly | What happens | Prevented by |
|---------|--------------|--------------|
| **Dirty read** | One client reads another client's writes before they are committed. | Read committed and stronger. |
| **Dirty write** | One client overwrites data another client has written but not yet committed. | "Almost all transaction implementations prevent dirty writes." |
| **Read skew** (nonrepeatable read) | A client sees different parts of the database at different points in time. | Snapshot isolation — a consistent snapshot at one point in time, usually via MVCC. |
| **Lost update** | Two clients concurrently run a read-modify-write cycle; one overwrites the other's write without incorporating it. | Some snapshot-isolation implementations detect it automatically; others need an explicit `SELECT FOR UPDATE`. |
| **Write skew** | A transaction reads something, decides based on what it saw, and writes the decision — but by commit time the premise is no longer true. | **Only serializable isolation.** |
| **Phantom** | A write in one transaction changes the result of a search query in another transaction. | Snapshot isolation avoids phantoms in read-only queries; in read-write transactions they cause write skew. Serializable isolation prevents them outright. |

Concurrency bugs from weak isolation are not theoretical. DDIA notes they "have caused substantial loss of money, led to investigation by financial auditors, and caused customer data to be corrupted" — and that "use an ACID database" misses the point, because many relational databases considered ACID run weak isolation by default.

## What Each Isolation Level Blocks

| Level | Blocks | Still permits |
|-------|--------|---------------|
| **Read committed** | Dirty reads, dirty writes | Read skew, lost updates, write skew, phantoms |
| **Snapshot isolation** (often labeled "repeatable read") | + read skew; phantoms in read-only queries | Write skew, phantoms in read-write transactions; lost updates depending on implementation |
| **Serializable** | Everything above — result is "the same as if they had executed one at a time, serially" | Nothing (cost is throughput, latency variance, or abort rate depending on implementation) |

Read committed is a widely used default, and snapshot isolation is frequently exposed under the name "repeatable read" — but which level a specific engine and version defaults to is exactly the kind of fact that has moved since 2017. Check the vendor's current documentation rather than assuming; the anomaly table above is what stays true.

The critical asymmetry: **snapshot isolation does not prevent write skew, and does not detect it automatically.** DDIA is explicit that write skew "is not automatically detected in PostgreSQL's repeatable read, MySQL/InnoDB's repeatable read, Oracle's serializable, or SQL Server's snapshot isolation level" (2017 statement — re-verify per engine, but treat the design assumption "snapshot isolation will catch this for me" as unsafe by default). "Automatically preventing write skew requires true serializable isolation."

## Write Skew: The Anomaly Snapshot Isolation Does Not Prevent

Write skew occurs when two transactions read the same objects and then update *different* objects among them. It generalizes lost update: when both transactions update the *same* object you get a dirty write or lost update instead, depending on timing.

**On-call doctors.** The invariant is "at least one doctor must be on call for a shift." Alice and Bob each open a transaction to take themselves off call. Each checks that two or more doctors are currently on call; under snapshot isolation both checks return 2, so both proceed. Alice updates her own record, Bob updates his. Both commit. Now nobody is on call. No dirty write and no lost update occurred — the two transactions modified two different rows — yet the invariant is broken. Had they run one after another, the second doctor would have been blocked.

**Meeting room booking.** The invariant is "no two bookings for the same room at the same time." A transaction runs `SELECT COUNT(*) FROM bookings WHERE room_id = 123 AND end_time > '...12:00' AND start_time < '...13:00'`, sees zero, and inserts the booking. Snapshot isolation "does not prevent another user from concurrently inserting a conflicting meeting." Both transactions see zero conflicts; both insert; the room is double-booked.

Other instances DDIA lists: a multiplayer game where two players move different figures to the same board position; claiming a username; and double-spending, where two tentative spending items are inserted concurrently that together push a balance negative without either transaction noticing the other.

The doctors case and the booking case differ in a way that determines the fix. In the doctors case the row modified in step 3 was among the rows returned in step 1, so locking those rows works. The booking, username, game-position, and double-spend cases all **check for the absence of rows** matching a condition and then add a row matching that same condition. If the step-1 query returns no rows, `SELECT FOR UPDATE` has nothing to attach a lock to — this is the phantom problem.

## Spotting Write-Skew-Prone Invariants

All the examples share one shape. Look for it in application code during schema review:

1. A `SELECT` checks whether a requirement is satisfied by searching for rows matching some condition.
2. Application code branches on the result — proceed, or report an error and abort.
3. If proceeding, it writes (`INSERT`/`UPDATE`/`DELETE`) and commits — and that write **changes the precondition of the decision in step 2**. Re-running the step-1 query after the commit would return a different result.

The steps can be reordered (write first, then query, then decide whether to commit). The test that matters: **check-then-write against a constraint no single row enforces.** If the invariant spans multiple rows — a count, a sum, an absence, a non-overlap — no row-level mechanism protects it, and neither does snapshot isolation.

Concrete review questions:

- Is the invariant expressible as a `UNIQUE` or `CHECK` constraint on one row? If yes, it is safe. If it needs a count, a sum, or an overlap test across rows, it is a write-skew candidate.
- Does the guard query return the rows the transaction then writes to (lockable), or does it check for *absence* (phantom — not lockable)?
- Would running the two concurrent transactions in either serial order have prevented the outcome? If yes and they still both commit concurrently, that is write skew by definition.

## Mitigations, Ranked

1. **Serializable isolation.** The only thing that prevents write skew automatically and handles the phantom cases. "A serializable isolation level is much preferable in most cases." Cost varies by implementation — see the next section.
2. **Database constraints**, where the invariant fits one. A `UNIQUE` constraint fully solves the username case: the second transaction aborts on constraint violation. Postgres exclusion constraints cover the non-overlap booking case. This is the cheapest correct fix when available. The constraint has to span the invariant, though — "at least one doctor on call" needs a constraint involving multiple objects, and "most databases do not have built-in support for such constraints," though triggers or materialized views may work.
3. **`SELECT ... FOR UPDATE`** to lock the rows the decision depends on — but only where the guard query actually returns rows. For the doctors case: `SELECT * FROM doctors WHERE on_call = true AND shift_id = 1234 FOR UPDATE;` before the update. Useless against phantoms.
4. **Materializing conflicts** — last resort. Create rows to lock that would not otherwise exist: for room booking, pre-create a table of (room, 15-minute time slot) rows for the next six months, `SELECT FOR UPDATE` the slots for the desired range, then check and insert. The extra table stores no booking information; it is "purely a collection of locks." DDIA is blunt that this "can be hard and error-prone to figure out," that it is "ugly to let a concurrency control mechanism leak into the application data model," and that it "should be considered a last resort if no alternative is possible."

## Serializability Implementations

Most databases offering serializability use one of three techniques. Knowing which one your engine uses predicts its failure mode under load.

| | **Actual serial execution** | **Two-phase locking (2PL)** | **Serializable snapshot isolation (SSI)** |
|---|---|---|---|
| **Approach** | One transaction at a time, single thread. Isolation is serializable by definition. | Pessimistic. Shared/exclusive locks held until commit or abort. | Optimistic. Let transactions run; detect at commit whether a transaction acted on an outdated premise, and abort it if so. |
| **Readers vs writers** | N/A (no concurrency) | Writers block readers and readers block writers. | Writers don't block readers and readers don't block writers — as under snapshot isolation. |
| **Requires** | Entire active dataset in memory; transactions submitted as stored procedures, not interactive statement-at-a-time. | Nothing special; "for several decades was the only viable option." | MVCC plus read/write tracking. |
| **Throughput ceiling** | One CPU core, unless data is partitioned so each transaction touches one partition. | Reduced concurrency by design. | Not limited to one core; conflict detection can be distributed. |
| **Main failure mode** | One slow transaction stalls all transaction processing. Cross-partition transactions are "vastly slower." | "Quite unstable latencies... very slow at high percentiles if there is contention." One long transaction holding many locks can grind the system to a halt. Deadlocks occur much more frequently than under read committed, and each deadlock abort wastes the whole transaction's work. | Abort rate. A transaction that reads and writes over a long period is likely to conflict and abort — SSI "requires that read-write transactions be fairly short." |
| **Design implication** | Keep transactions small and fast; partition so transactions stay single-partition. | Keep transactions short *and* narrow — lock footprint matters as much as duration. Expect to implement retry-on-deadlock. | Keep read-write transactions short. Long-running *read-only* transactions are fine. Implement retry-on-abort. |

**Predicate locks vs index-range locks (2PL).** To prevent phantoms, 2PL conceptually needs a *predicate lock* — a lock belonging not to a particular row but to "all objects that match some search condition," including rows that do not yet exist but might be added. That is what makes 2PL fully serializable. But predicate locks "do not perform well: if there are many locks by active transactions, checking for matching locks becomes time-consuming." So most 2PL databases implement **index-range locking** (next-key locking), a simplified approximation: attach the lock to an index entry or index range covering the predicate — e.g. a shared lock on the `room_id = 123` index entry, or on a time range in a time index. It is safe to approximate a predicate by matching a *greater* set of objects, since any write matching the original predicate also matches the approximation. Index-range locks "are not as precise as predicate locks... but since they have much lower overheads, they are a good compromise." **If there is no suitable index to attach the range lock to, the database falls back to a shared lock on the entire table** — safe, but it stops all other writes to that table. This is a direct schema-design consequence: the indexes you create determine the lock granularity a serializable workload gets.

**How SSI detects the outdated premise.** A transaction acts on a premise (e.g. "there are currently two doctors on call"); the database must detect when that premise has changed by commit time. Two cases: (1) *stale MVCC reads* — the transaction ignored another transaction's uncommitted write due to snapshot visibility rules, and that write has since committed; the database tracks the ignored writes and aborts at commit if any of them landed. Detection is deferred to commit time deliberately — a read-only transaction never needs aborting, and the other transaction may yet abort, so waiting avoids unnecessary aborts and preserves long-running consistent-snapshot reads. (2) *writes affecting prior reads* — the database records which transactions read a given index entry, and a later write to that range acts as a "tripwire" that notifies readers their read is outdated, rather than blocking them. Tracking granularity is a tradeoff: detailed tracking aborts precisely but costs bookkeeping; coarse tracking is faster but aborts transactions unnecessarily.

## LSM-Tree vs B-Tree Storage Engines

DDIA's rule of thumb: "LSM-trees are typically faster for writes, whereas B-trees are thought to be faster for reads." Reads are slower on LSM-trees because they must check several structures and SSTables at different compaction stages. Immediately after stating it, DDIA cautions that "benchmarks are often inconclusive and sensitive to details of the workload. You need to test systems with your particular workload in order to make a valid comparison." Treat the table below as a hypothesis generator, not a verdict.

Three amplification factors trade against each other:

- **Write amplification** — "one write to the database resulting in multiple writes to the disk over the course of the database's lifetime." A B-tree writes every piece of data at least twice (write-ahead log, then the tree page), plus whole-page writes even when a few bytes changed, and some engines write a page twice to survive partial-page power failure. LSM-trees also rewrite data repeatedly via compaction. Of particular concern on SSDs, "which can only overwrite blocks a limited number of times before wearing out." In write-heavy applications it has a direct performance cost: more bytes written per logical write means fewer writes per second within the available disk bandwidth.
- **Read amplification** — the LSM penalty: a read may have to check the memtable plus multiple SSTables across compaction levels.
- **Space amplification** — B-trees "leave some disk space unused due to fragmentation" when a page splits or a row does not fit an existing page. LSM-trees "are not page-oriented and periodically rewrite SSTables to remove fragmentation," so they have lower storage overhead, "especially when using leveled compaction," and compress better, "often produc[ing] smaller files on disk than B-trees."

| | **LSM-tree** | **B-tree** |
|---|---|---|
| **Write path** | Sequential writes of compact SSTable files | Overwrites several pages in the tree, plus the WAL |
| **Write throughput** | Typically higher — partly lower write amplification (workload- and config-dependent), partly sequential rather than random writes | Lower under write-heavy load |
| **Read latency** | Variable; can be "quite high" at high percentiles when compaction competes for disk | "More predictable" |
| **Space on disk** | Better compression, less fragmentation | Fragmentation leaves pages partly unused |
| **Copies per key** | Multiple copies of a key may exist across segments | "Each key exists in exactly one place in the index" |
| **Transactional locking** | Harder — no single place to attach a range lock | Attractive for strong transactional semantics: range locks "can be directly attached to the tree" |

The last row connects directly to the transaction half of this file: index-range locking, the standard 2PL mechanism for preventing phantoms, depends on there being one place per key to attach the lock. That is a structural reason relational engines offering serializable isolation are predominantly B-tree based.

On SSDs the write-pattern difference is muted — "the firmware internally uses a log-structured algorithm to turn random writes into sequential writes on the underlying storage chips" — but lower write amplification and reduced fragmentation still help, because "representing data more compactly allows more read and write requests within the available I/O bandwidth." On magnetic drives the sequential-write advantage is much more pronounced.

## Compaction Falling Behind Ingest

The LSM operational failure mode worth designing monitoring for. Disk write bandwidth is finite and must be shared between the initial write (logging and flushing memtables) and background compaction threads. When the database is empty, the full bandwidth serves the initial write; **the bigger the database gets, the more disk bandwidth compaction requires.**

If write throughput is high and compaction is not configured carefully, compaction cannot keep up with incoming writes. Then, per DDIA:

- The number of unmerged segments on disk keeps growing **until you run out of disk space**.
- **Reads slow down**, because they must check more segment files — which compounds the LSM read-amplification penalty exactly when the system is already under stress.

The trap is that this does not self-correct: "typically, SSTable-based storage engines do not throttle the rate of incoming writes, even if compaction cannot keep up, so you need explicit monitoring to detect this situation." The database will accept writes right up to disk exhaustion. Nothing pushes back on the producer.

Practical monitoring, following from the mechanism: track pending/unmerged segment count and compaction backlog as a **trend**, not a threshold — a slowly rising segment count under steady write load is the early signal. Alert on it well before disk-usage alerts fire, because by the time disk is the symptom, read latency has already degraded and the remedy (compaction) needs the very bandwidth that is scarce. Also note that compaction interferes with ongoing reads and writes even in the healthy case: "disks have limited resources, so it can easily happen that a request needs to wait while the disk finishes an expensive compaction operation." Impact on average response time is usually small; the damage shows at high percentiles.

## LSM Compaction Strategies

The section above covers what happens when compaction falls behind. This one covers the strategies themselves — which one an engine uses determines *how* it falls behind and what tuning knobs exist. Source: Alex Petrov, *Database Internals* (O'Reilly, 2019), Ch. 7 §"Maintenance in LSM Trees", §"Leveled compaction", §"Size-tiered compaction".

Compaction "picks multiple disk-resident tables, iterates over their entire contents using the aforementioned merge and reconciliation algorithms, and writes out the results into the newly created table." Two operational properties hold across all strategies:

- **Memory is bounded, disk is not.** Because table contents are sorted and merge-sort consumes them sequentially, "compaction has a theoretical memory usage upper bound, since it should only hold iterator heads in memory."
- **You must have headroom for the output.** "Compacting tables remain available for reads until the compaction process finishes, which means that for the duration of compaction, it is required to have enough free space available on disk for a compacted table to be written." Sizing disk to current data volume with no margin will wedge compaction — which is the failure mode described in [Compaction Falling Behind Ingest](#compaction-falling-behind-ingest).

Multiple compactions can run concurrently, but "these concurrent compactions usually work on nonintersecting sets of tables."

### Leveled compaction

Used by RocksDB. Tables are grouped into numbered levels with target sizes. Level 0 is created by flushing memtables and is the one level where "tables in level 0 may contain overlapping key ranges." From level 1 up, key ranges within a level do not overlap — which is why level-0 tables "have to be partitioned during compaction, split into ranges, and merged with tables holding corresponding key ranges."

Higher-level compactions "pick tables from two consecutive levels with overlapping ranges and produce a new table on a higher level." Sizes "grow exponentially between the levels: tables on each next level are exponentially larger than tables on the previous one. This way, the freshest data is always on the level with the lowest index, and older data gradually migrates to the higher ones."

The read benefit is direct: "Keeping different key ranges in the distinct tables reduces the number of tables accessed during the read. This is done by inspecting the table metadata and filtering out the tables whose ranges do not contain a searched key." Note Petrov's terminology warning — "Somewhat counterintuitively, the level with the highest index is called the bottommost level."

Trade-off: non-overlapping ranges mean data gets rewritten repeatedly as it migrates upward, so leveled compaction buys read and space efficiency with write amplification.

### Size-tiered compaction

Tables are grouped by size rather than by level: "smaller tables are grouped with smaller ones, and bigger tables are grouped with bigger ones." A merged table "is written to the level holding tables with corresponding sizes," and the process recurses, "compacting and promoting larger tables to higher levels, and demoting smaller tables to lower levels."

**Compaction starvation is the named failure mode here.** Petrov's warning, quoted:

> "One of the problems with size-tiered compaction is called table starvation: if compacted tables are still small enough after compaction (e.g., records were shadowed by the tombstones and did not make it to the merged table), higher levels may get starved of compaction and their tombstones will not be taken into consideration, increasing the cost of reads. In this case, compaction has to be forced for a level, even if it doesn't contain enough tables."

The self-reinforcing shape is worth naming explicitly: heavy delete traffic shrinks compaction output, small output fails the size threshold that would trigger the next compaction, the tombstones stay resident, and reads get slower — while the size-based trigger never fires. The remedy is not a tuning value but an out-of-band forced compaction. If your workload is delete-heavy or TTL-heavy on a size-tiered engine, monitor for levels that stop compacting rather than assuming the strategy is self-correcting.

### Time-window compaction

Petrov cites Apache Cassandra's time window compaction strategy as "particularly useful for time-series workloads with records for which time-to-live is set (in other words, items have to be expired after a given time period)." It "takes write timestamps into consideration and allows dropping entire files that hold data for an already expired time range without requiring us to compact and rewrite their contents."

That is the whole point: for append-mostly time-series data with uniform TTL, expiry becomes a file delete rather than a read-merge-rewrite cycle. It avoids the write amplification the other two strategies pay to reclaim the same space. It only works when the data actually partitions cleanly by time — out-of-order or late-arriving writes that land in already-closed windows undermine it.

### Tombstone handling rules

Tombstones are the mechanism that makes deletes work in an append-only store, and dropping one too early resurrects deleted data. Petrov's rule:

> "Tombstones represent an important piece of information required for correct reconciliation, as some other table might still hold an outdated data record shadowed by the tombstone. During compaction, tombstones are not dropped right away. They are preserved until the storage engine can be certain that no data record for the same key with a smaller timestamp is present in any other table."

Two concrete implementations of "can be certain," which differ because the systems differ:

- **RocksDB** "keeps tombstones until they reach the bottommost level" — a single-node engine can establish certainty structurally, since a tombstone at the bottommost level has no older table beneath it.
- **Apache Cassandra** "keeps tombstones until the GC (garbage collection) grace period is reached because of the eventually consistent nature of the database, ensuring that other nodes observe the tombstone." A distributed eventually-consistent store cannot establish certainty from local structure alone; the grace period is a time-based proxy for "every replica has seen this."

Petrov's stated purpose for all of it: "Preserving tombstones during compaction is important to avoid data resurrection." The design consequence is that on Cassandra-like systems, a node down longer than the GC grace period must not simply rejoin — it may carry data whose tombstones have already been collected elsewhere.

Reconciliation itself is timestamp-ordered: "Records shadowed by the records with higher timestamps are not returned to the client or written during compaction." Note that in LSM trees "insert and update operations are indistinguishable... we can say that we upsert records by default."

## The RUM Conjecture

Source: *Database Internals*, Ch. 7 §"RUM Conjecture" (citing ATHANASSOULIS16). A cost model over three overheads — **R**ead, **U**pdate, **M**emory — which "states that reducing two of these overheads inevitably leads to change for the worse in the third one, and that optimizations can be done only at the expense of one of the three parameters."

Applied to the two engine families in this file: B-trees are read-optimized, paying in update cost (locating the record on disk, repeated page writes) and space (reserved free space for future updates). LSM trees do not locate the record on write and reserve no extra space, paying instead in read cost, "since multiple tables have to be accessed to return complete results."

**It is a conjecture and a design heuristic, not a theorem — treat it as a first-pass sorting tool, not a proof that some design is impossible.** Petrov is explicit about what it leaves out: "This cost model is not perfect, as it does not take into account other important metrics such as latency, access patterns, implementation complexity, maintenance overhead, and hardware-related specifics. Higher-level concepts important for distributed databases, such as consistency implications and replication overhead, are also not considered. However, this model can be used as a first approximation and a rule of thumb as it helps understand what the storage engine has to offer." He also cautions against using write amplification to compare the families directly, since its source differs — writeback and repeated node updates in B-trees, compaction data migration in LSM trees — so "comparing the two directly may lead to incorrect assumptions."

## Bw-Trees

Source: *Database Internals*, Ch. 6 §"Bw-Trees" (citing LEVANDOSKI14, WANG18). A latch-free B-tree variant that attacks write amplification, space amplification, and latch contention at once.

Instead of updating a page in place, a Bw-tree "writes a base node separately from its modifications. Modifications (delta nodes) form a chain: a linked list from the newest modification, through older ones, with the base node in the end." Because nothing is ever modified — updates only prepend — no free space needs reserving. The cost is on the read side: "during a read, all deltas have to be traversed and applied to the base node to reconstruct the actual node state," so delta chains are consolidated back into a new base node once they exceed a configurable length.

Latches are eliminated by indirection: nodes have logical identifiers resolved through "an in-memory mapping table from the identifiers to their locations on disk," and installing a new delta is a single compare-and-swap on the mapping-table entry. "all reads, concurrent to the pointer update, are ordered either before or after the write, without blocking either the readers or the writer." If two threads race, one wins and the other retries. Reclaiming superseded nodes needs epoch-based reclamation, since no reader ever registered at a barrier.

Petrov's assessment: "The Bw-Tree is an interesting B-Tree variant, making improvements on several important aspects: write amplification, nonblocking access, and cache friendliness." **Treat it as research and limited deployment, not a production option to select.** The deployments Petrov names are an experimental storage engine (Sled) and an in-memory research implementation (CMU's OpenBw-Tree, released with a practical implementation guide) — not mainstream databases. It is worth knowing as the answer to "can a B-tree be latch-free," not as a candidate in an engine-selection decision.

## Choosing an Engine

DDIA's own conclusion is deliberately unheroic: "There is no quick and easy rule for determining which type of storage engine is better for your use case, so it is worth testing empirically." B-trees "are very ingrained in the architecture of databases and provide consistently good performance for many workloads," while log-structured indexes are "becoming increasingly popular" in new datastores.

Given that, use engine shape as a starting hypothesis:

**Lean LSM when** the workload is write-heavy and ingest-dominated; sustained write throughput is the binding constraint; storage cost or compression matters at volume; and reads are tolerant of high-percentile variance. Budget for compaction tuning and the monitoring above as a standing operational cost, not a one-time setup.

**Lean B-tree when** read latency predictability matters (especially at high percentiles); the workload needs strong transactional semantics with range locking — see the serializability section; the read/write mix is balanced or read-heavy; or the team wants mature, well-understood operational behavior with fewer tuning knobs.

**In either case** validate against your own workload before committing. The claim that survives benchmarking is the mechanism (sequential vs random writes, one copy per key vs many, where amplification lands), not any particular throughput number.
