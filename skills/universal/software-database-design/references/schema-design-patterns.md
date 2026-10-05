# Schema Design Patterns

Use this file when the request is about table shape, entity boundaries, or long-lived schema evolution.

## Table of Contents

- [Core Relational Patterns](#core-relational-patterns)
- [PostgreSQL 18 Schema Boundaries](#postgresql-18-schema-boundaries)
- [MySQL InnoDB Schema Notes](#mysql-innodb-schema-notes)
- [Common Shapes](#common-shapes)
- [Temporal / Audit Table Patterns](#temporal--audit-table-patterns)
- [Identifier Guidance](#identifier-guidance)
- [PostgreSQL Type-Choice Forensics](#postgresql-type-choice-forensics)
- [UUIDv4 Primary Key Costs](#uuidv4-primary-key-costs)
- [Upserting NULLs in a Composite Unique Key](#upserting-nulls-in-a-composite-unique-key)
- [Hierarchy Storage Models](#hierarchy-storage-models)
- [Partition Rebalancing Strategies](#partition-rebalancing-strategies)

## Core Relational Patterns

- Normalize by default for transactional data.
- Denormalize only when the read path proves it is necessary.
- Prefer explicit join tables for many-to-many relations when metadata or history matters.
- Use foreign keys unless there is a concrete, measured reason not to.

## PostgreSQL 18 Schema Boundaries

- Generated columns can be `VIRTUAL` (computed on read, now the default) or `STORED` (computed on write). A virtual expression cannot use user-defined functions or types; check [generated-column restrictions](https://www.postgresql.org/docs/18/ddl-generated-columns.html) before replacing an application-calculated field.
- `CHECK` and foreign-key constraints can be declared `NOT ENFORCED`; PostgreSQL will not validate writes against them. Use this for documentation or a separately enforced invariant, never as a substitute for a validated database guard. [CREATE TABLE](https://www.postgresql.org/docs/18/sql-createtable.html#SQL-CREATETABLE-PARMS).
- `INSERT`, `UPDATE`, `DELETE`, and `MERGE` can refer to `OLD` and `NEW` in `RETURNING`. Use the explicit aliases when a migration or audit write must compare before and after values. [PostgreSQL 18 release notes](https://www.postgresql.org/docs/18/release-18.html).

These are PostgreSQL 18 feature boundaries, not a blanket recommendation to upgrade; choose a supported target from the [version policy](https://www.postgresql.org/support/versioning/) and test feature availability on that deployment.

## MySQL InnoDB Schema Notes

- InnoDB stores rows in its clustered primary-key index and copies primary-key columns into each secondary index entry. Prefer a short, stable primary key and measure secondary-index growth before choosing a wide composite key. [InnoDB index types](https://dev.mysql.com/doc/refman/8.4/en/innodb-index-types.html).
- `ALGORITHM=INSTANT` handles only supported `ALTER TABLE` operations and has table and operation restrictions; specify it when a table-copy fallback would be unacceptable, so unsupported changes fail instead of silently taking a slower path. Check the target series' [online DDL table](https://dev.mysql.com/doc/refman/8.4/en/innodb-online-ddl-operations.html) for the exact operation.
- MySQL DDL, including `ALTER TABLE`, normally causes implicit commits. Do not rely on a transaction wrapper to roll back a multi-step schema change; plan a compatible application rollback and verify each step separately. [Implicit-commit statements](https://dev.mysql.com/doc/refman/8.4/en/implicit-commit.html).

## Common Shapes

| Pattern | Use When | Notes |
|---|---|---|
| Tenant column | Most SaaS multi-tenancy | Simpler than per-tenant schema, needs strong indexing and RLS if used |
| Join table | Many-to-many relation | Keep business metadata on the join when needed |
| Append-only audit table | Compliance or history matters | Separate from primary hot-path table when possible |
| Soft delete | Recovery or legal retention matters | Add explicit cleanup/reporting plan; do not use by reflex |
| Event table | Immutable business facts | Pair with snapshots/materialized read models for performance |
| Temporal / system-versioned table | Need to answer "what did this row look like at time T" | See Temporal/Audit Patterns below — SQL Server, MariaDB, and Db2 have native system-versioning; PostgreSQL 18 added application-time temporal keys (`WITHOUT OVERLAPS`/`PERIOD`), not full system versioning; MySQL still needs an explicit pattern |

## Temporal / Audit Table Patterns

Pick based on what question the system must answer later — these are not interchangeable:

- **Append-only audit log** (event sourcing lite): a separate `*_events` or `*_audit` table, one row per change, storing `(entity_id, changed_at, changed_by, field, old_value, new_value)` or a full before/after snapshot as JSON. Answers "what happened and when" and "who did it." Cheapest to build; does not let you efficiently query "what was the full row state at time T" without replaying events.
- **System-versioned (temporal) table**: every row carries `valid_from`/`valid_to` (or `sys_period` as a range type), and updates insert a new row + close out the old one instead of overwriting. Answers "what did the full entity look like at time T" directly with a `WHERE valid_from <= T AND valid_to > T` predicate. SQL Server, MariaDB, and Db2 support this as a native `SYSTEM VERSIONING` (or equivalent) feature. PostgreSQL 18 adds native application-time temporal primary/unique/foreign keys (`WITHOUT OVERLAPS`, `PERIOD`), which enforce non-overlapping valid-time ranges but are not full system versioning; MySQL still requires building it with triggers, a range representation, or an extension — budget for that build cost, it is not a checkbox.
- **Soft delete is a narrower tool, not a temporal pattern**: a `deleted_at TIMESTAMP` only answers "is this row currently considered deleted," not "what did it look like before." Don't reach for soft delete when the actual requirement is audit history — that needs one of the two patterns above. Soft delete earns its complexity (every query must remember to filter it, every unique constraint must account for it) only when there's a real recovery window or legal retention requirement; default to hard delete otherwise and let the audit log (if one exists) carry the history.

## Identifier Guidance

- Prefer integer or time-ordered identifiers for clustered indexes and write-heavy tables.
- Use UUIDs when cross-system generation or client-side generation matters.
- Be consistent: mix fewer identifier strategies, not more.
- See the primary-key trade-off note in `SKILL.md` (Anti-Patterns section) for the concrete bigint-vs-UUIDv7 decision — it is a real trade-off between insert locality/index size and distributed-generation needs, not a default to apply by reflex.
- For the measured cost of native random UUIDv4 as a Postgres primary key, see [UUIDv4 Primary Key Costs](#uuidv4-primary-key-costs) below.

## PostgreSQL Type-Choice Forensics

Source: Jimmy Angelakos, *PostgreSQL Mistakes and How to Avoid Them* (Manning, 2025), §3.4–3.7. Written against a PostgreSQL 16/17-era Postgres; re-verify against the target major version before relying on a version-specific detail.

Three types that look like the obvious choice and are not. The common thread: none of them buys you storage or performance, and each imposes a correctness or operational cost.

### `MONEY` — use `NUMERIC` plus an explicit currency column

- **It does not store the currency.** Angelakos: "MONEY doesn't actually store the currency type but goes with whatever is configured on your server" — specifically the `LC_MONETARY` locale. A database whose locale inherits `en_GB` silently interprets an inserted `99.99` as £99.99. Move the dump to a server with a different `LC_MONETARY` and the same bytes mean a different currency.
- **It cannot hold fractions of the minor unit.** `99.99 * 0.25` evaluates to `24.9975` in `NUMERIC`, but the same multiplication against a `MONEY` column returns `£25.00`. Angelakos: "MONEY cannot handle fractions of a penny or a cent, or any other denomination, so you will end up losing money, which is unacceptable for most intents and purposes." He adds that this also rules it out for currency conversion, "where rounding is not an option."
- **It accepts garbage.** `SELECT ',123,456,,7,8.1,0,9'::MONEY` yields `£12,345,678.11` rather than an error. Angelakos calls accepting invalid input into a monetary type "astoundingly bad."
- **Deprecation has been attempted and reverted.** "the PostgreSQL core developers have tried to deprecate MONEY multiple times," each time blocked by users with existing databases on the type.
- **The fix:** "The proposed solution is to use NUMERIC instead of MONEY, and it's also a very good idea to store the currency associated with the monetary value in another adjacent column on the table." Note that `NUMERIC` and `DECIMAL` are the same type in PostgreSQL. Floating-point types (`real`, `double precision`) are *also* wrong here — they are inexact by definition and carry rounding error.

### `SERIAL` / `BIGSERIAL` — use `GENERATED ... AS IDENTITY`

`SERIAL` is a non-standard PostgreSQL shorthand that creates a sequence and wires it up as the column default. Angelakos: "It used to be a useful shorthand, but today, it is actually more trouble than it's worth." Two concrete failures:

- **Sequence permissions are separate from table permissions.** `GRANT ALL ON TABLE transactions TO jimmy` is not enough — an insert by that role fails with `ERROR: permission denied for sequence transactions_id_seq`. "permissions for sequences created via the use of SERIAL need to be managed separately from the actual table."
- **`CREATE TABLE ... LIKE ... INCLUDING ALL` shares the original sequence.** The copied table's `id` default still reads `nextval('transactions_id_seq')` — the *source* table's sequence. Angelakos flags the knock-on: "you can't drop the original table because the sequence the new table uses depends on it." With identity columns the copy gets its own new sequence instead.

Identity columns also let you manipulate the sequence without knowing its generated name: `ALTER TABLE new_tx ALTER COLUMN id RESTART WITH 1000`.

**Gapless sequences are a separate problem.** Neither `SERIAL` nor `IDENTITY` gives you one. "PostgreSQL sequences will generate new numbers even for transactions that are not committed and then rolled back." If a locality requires gapless receipt numbering, Angelakos' guidance is to "generate the sequence on the application side to guarantee correctness."

### `CHAR(n)` — use `TEXT` (plus a `CHECK` constraint if a limit is genuinely required)

`CHAR(n)` is blank-padded to length `n`. The padding is *stored*, and it is semantically significant in some operations but not others — which is where the bugs come from:

- Equality ignores the padding: `'postgres'::CHAR(10) = 'postgres'::CHAR(20)` is true.
- **`LIKE` and regex do not.** `'postgres'::CHAR(10) LIKE '%ostgres'` returns **false**, because the value ends in two blanks. Same for the POSIX operator: `'postgres'::CHAR(10) ~ '.*ostgres$'` is false.
- Over-length casts truncate silently — `'I heart PostgreSQL'::CHAR(10)` yields `I heart Po` with "no warning or error raised, as this behavior is required by the SQL Standard."
- It does not even enforce a minimum: "Even if you need to enforce the length of a string in a column as exactly n characters, using CHAR(n) is not the proper way to do that, as it will happily accept shorter strings."
- **There is no performance or storage win.** Internally it is not a fixed-width field — "the stored string is represented as a variable-length value on disk," so the blanks cost real space, and "when you use CHAR(n), your server spends extra computation time stripping spaces in order to perform string operations and comparisons."
- Indexes on `CHAR(n)` columns "may not work for queries with a TEXT parameter passed to the database from a PostgreSQL connector or driver."

`VARCHAR(n)` avoids the padding problems but still buys nothing: "the storage on disk is identical to TEXT," and the length limit becomes a migration liability — widening it needs an `ALTER TABLE` with the associated DDL locking, and "shrinking down to a smaller limit is impossible." Where a limit is a real requirement (compliance, say), Angelakos' recommendation is `TEXT` with a `CHECK` constraint, "which you can then change easily," or a `CREATE DOMAIN` over `TEXT` to avoid repeating the `CHECK` definition.

## UUIDv4 Primary Key Costs

**Scope this finding carefully.** It measures *native random UUIDv4* — what `gen_random_uuid()` produces and what PostgreSQL supported natively as of the book's writing (Angelakos: "The variety of UUID that is supported natively in PostgreSQL is UUIDv4"). It is **not** a general verdict on UUID primary keys, and it does not carry over to time-ordered UUIDs. PostgreSQL 18 ships a native `uuidv7()` function; UUIDv7 is time-ordered, so it does not incur the random-insert index-locality penalty that drives most of the gap below. As of PG ≤ 17 you needed an extension or application-side generation for UUIDv7 — Angelakos, writing earlier, describes it as "at the time of writing, coming soon to Postgres." Verify what your target major version actually offers.

Angelakos' table 5.4, reproduced verbatim:

| | bigint | uuid | Difference |
|---|---|---|---|
| INSERT | 01:23 | 06:28 | 367% slower |
| CREATE INDEX | 00:38 | 01:16 | 100% slower |
| Index size | 2142 MB | 3008 MB | 40% bigger |

**Test conditions, which the percentages are meaningless without:**

- 100,000,000 rows, inserted in a single statement from `generate_series(1,100000000)`.
- Table shape `(id, content text)` with `content` a constant `'test'` in both runs.
- UUID arm: `INSERT INTO test.tab SELECT gen_random_uuid(), 'test' FROM generate_series(...)` — i.e. `gen_random_uuid()` called 100M times, so UUID *generation* cost is inside the INSERT number, not just index maintenance.
- bigint arm: `INSERT INTO test.tab SELECT generate_series(1,100000000), 'test'` — strictly monotonic, so every insert lands at the right edge of the eventual index.
- The primary key was added *after* the load in both arms (`ALTER TABLE ... ADD PRIMARY KEY (id)`), so the CREATE INDEX row is a bulk build over already-loaded data, not incremental index maintenance during OLTP inserts. A steady-state write workload has a different (and typically worse) profile for random UUIDs, because of page splits and buffer-cache misses that a bulk build does not exercise.
- Single machine, single run, no repetitions reported; the book gives no variance figures.

Angelakos' own explanation: "UUIDv4 is at the same time larger than a big integer, and it requires generating the next value randomly (something computers are not very good at)." He also notes a second-order effect worth remembering at schema-design time: "Using lots of UUIDs in your table can also push your other data columns to spill over into the TOAST table and make everything somewhat less efficient." Per table 5.3, `uuid` is 16 bytes against `bigint`'s 8.

**Design guidance.** The legitimate case for UUIDs is unchanged: "a conflict-free and fast way to generate identifiers for INSERTs from multiple nodes of a distributed system (because there needs to be no coordination regarding the identifiers among the nodes)." But Angelakos flags that plain UUIDv4 gives up sort order — "sorting keys such as sequence numbers, timestamps, and node identifiers are not encoded in the UUID" — and points to Snowflake IDs or UUIDv7 as the better answer for that use case, since both "encode within them precise timestamps and are sortable by time." Also worth checking whether you need the range at all: "Even a PostgreSQL big integer, with 18 quintillion (and change) available values, might offer too big a range for what you're trying to do."

## Upserting NULLs in a Composite Unique Key

Source: Angelakos §2.8. A silent data-duplication bug that only appears once a nullable column joins a composite unique key.

The setup: a unique index over `(product_id, warehouse_id, area)` where `area` is nullable, because some stock sits in a generic location rather than a named one. An `INSERT ... ON CONFLICT (product_id, warehouse_id, area) DO UPDATE` works correctly for every row where `area` has a value — and silently inserts a duplicate every time `area` is `NULL`.

**Why.** A `NULL` is not equal to another `NULL`, so a unique index treats two rows differing only by a `NULL` as distinct. Angelakos: "PostgreSQL (or any database, for that matter) cannot compare NULL values for equality. Therefore, the two rows with NULL in the area column are treated as distinct, even though they look like they should represent the same record in the database." `ON CONFLICT` finds no conflict, so it takes the insert branch. The table accumulates one extra row per upsert attempt, with no error.

This generalizes past PostgreSQL: it is standard SQL unique-index semantics. The failure mode is that it is invisible in testing unless a test case exercises the `NULL` path specifically.

**The fix, and the version number is load-bearing.** PostgreSQL **15** introduced the `NULLS NOT DISTINCT` clause on unique indexes:

```sql
CREATE UNIQUE INDEX ON erp.inventory (product_id, warehouse_id, area)
NULLS NOT DISTINCT;
```

Angelakos: "From version 15 onward, PostgreSQL allows you to address this issue by explicitly defining the conflict resolution behavior of ON CONFLICT with unique constraints containing NULL fields. All you have to do is add the NULLS NOT DISTINCT clause when creating the index. This changes the legacy default behavior of treating NULL values as distinct and enables proper upserts in this scenario."

On PostgreSQL 14 and earlier there is no such clause, and Angelakos describes the pre-15 situation as worse than merely unsupported: "the behavior of ON CONFLICT when NULL values were involved was unpredictable. In some cases, it would insert new rows, and in others, it wouldn't."

**Design implication.** Before adding a nullable column to a composite unique key, decide explicitly which `NULL` semantics you want. If `NULL` means "one specific unnamed bucket" (as `area` does here), you want `NULLS NOT DISTINCT` — or, often cleaner, a `NOT NULL` column with a sentinel value like `'common'`, which sidesteps the whole class of bug and works on every version. If `NULL` genuinely means "unknown, could be anything," the default distinct behavior is correct and an upsert on that key is the wrong operation.

## Hierarchy Storage Models

Source: Bill Karwin, *SQL Antipatterns, Volume 1* (Pragmatic Bookshelf, 2022), Ch. 3 "Naive Trees". Karwin's comparison matrix, reproduced verbatim:

| Design | Tables | Query Child | Query Tree | Insert | Delete | Ref. Integ. |
|---|---|---|---|---|---|---|
| Adjacency List | 1 | Easy | Hard | Easy | Easy | Yes |
| Recursive Query | 1 | Easy | Easy | Easy | Easy | Yes |
| Path Enumeration | 1 | Easy | Easy | Easy | Easy | No |
| Nested Sets | 1 | Hard | Easy | Hard | Hard | No |
| Closure Table | 2 | Easy | Easy | Easy | Easy | Yes |

Karwin frames the choice plainly: "Each of the designs has its own strengths and weaknesses. Choose the design depending on which operations you need to be most efficient."

**Adjacency List** — each row carries a `parent_id` foreign key to its own table. Karwin: "the most conventional design, and many software developers recognize it. It has the advantage over the other designs that it's normalized. In other words, it has no redundancies, and it's not possible to create conflicting data." The weakness is the "Query Tree: Hard" cell — fetching an arbitrary-depth subtree needs one query per level, or a recursive query (next row). Default to this unless you have a concrete reason not to.

**Recursive Query** — the same adjacency-list table, queried with `WITH RECURSIVE` (or Oracle's `CONNECT BY PRIOR`). This is the row that turns adjacency list's only weakness into a non-issue: Karwin notes recursive queries "make it more efficient to use the Adjacency List design, provided you use a version of SQL database that supports the syntax." That proviso is the whole decision — every mainstream engine supports it now, so on a modern stack this is usually the right answer, and the exotic designs below are for cases where recursive queries measurably do not perform.

**Path Enumeration** — store each node's full ancestry as a delimited string (`1/4/6/`). Queries for ancestors and subtrees become prefix `LIKE` matches. Karwin: "good for breadcrumbs in user interfaces, but it's fragile because it fails to enforce referential integrity and stores information redundantly." Nothing stops a path from naming a node that no longer exists. Reach for it when you display breadcrumbs constantly and can tolerate the integrity gap.

**Nested Sets** — each node stores `nsleft`/`nsright` numbers encoding its position in a depth-first traversal; a subtree is everyone whose numbers fall inside the parent's range. Karwin: "a clever solution—maybe too clever. It also fails to support referential integrity. It's best used when you need to query a tree more frequently than you need to modify the tree." That is the matrix's Insert/Delete "Hard" cells: an insert must "recalculate all the left and right values greater than the left value of the new node," touching right siblings, ancestors, and ancestors' right siblings. "If your usage of the tree involves frequent insertions, Nested Sets isn't the best choice."

**Closure Table** — a second table holding one row per ancestor/descendant pair at *every* depth, plus a self-reference for each node. Karwin: "the most versatile of the alternative designs, and the only design in this chapter that allows a node to belong to multiple trees. It requires an additional table to store the relationships. This design also uses a lot of rows when encoding deep hierarchies, increasing space consumption as a trade-off for reducing computing." Adding a `path_length` column makes immediate-children queries trivial (`WHERE ancestor = 4 AND path_length = 1`). This is the strongest option when you need fast queries in both directions *and* referential integrity, and can pay the row-count cost.

Karwin's closing rule for the chapter: "A hierarchy consists of entries and relationships. Model both of these in a way that supports the queries you need to make against the hierarchy."

## Partition Rebalancing Strategies

Source: Martin Kleppmann, *Designing Data-Intensive Applications* (O'Reilly, 1st ed. 2017), Ch. 6 "Rebalancing Partitions". The mechanisms are durable; every named product below is a 2017-era example and should be re-verified against current documentation before you rely on it.

Rebalancing is "the process of moving load from one node in the cluster to another." It is triggered by throughput growth, dataset growth, and node failure alike. Kleppmann's three requirements for any scheme:

- After rebalancing, load (storage, reads, writes) "should be shared fairly between the nodes in the cluster."
- "While rebalancing is happening, the database should continue accepting reads and writes."
- "No more data than necessary should be moved between nodes, to make rebalancing fast and to minimize the network and disk I/O load."

That third requirement is what rules out the obvious approach.

### Why hash-mod-N fails

Assigning keys with `hash(key) mod N` where N is the node count looks natural and is the one scheme Kleppmann labels "How not to do it." The problem is that N appears in the assignment function, so changing N reassigns nearly everything. His worked example: with `hash(key) = 123456`, the key sits on node 6 at 10 nodes (`123456 mod 10 = 6`), moves to node 3 at 11 nodes (`mod 11 = 3`), and to node 0 at 12 nodes (`mod 12 = 0`). "The problem with the mod N approach is that if the number of nodes N changes, most of the keys will need to be moved from one node to another... Such frequent moves make rebalancing excessively expensive."

The general fix, shared by all three working schemes below: **decouple the number of partitions from the number of nodes**, so adding a node changes only which node owns a partition, never which partition owns a key.

### Fixed number of partitions

Create many more partitions than nodes and assign several to each — Kleppmann's example is a 10-node cluster split into 1,000 partitions, ~100 per node. Adding a node lets it "steal a few partitions from every existing node until partitions are fairly distributed once again"; removing one runs the same process in reverse. Crucially: "Only entire partitions are moved between nodes. The number of partitions does not change, nor does the assignment of keys to partitions. The only thing that changes is the assignment of partitions to nodes." Because transfers take time, "the old assignment of partitions is used for any reads and writes that happen while the transfer is in progress." Heterogeneous hardware is handled by assigning more partitions to bigger nodes.

**The cost is that you must guess the partition count up front, and you cannot revise it.** It is "usually fixed when the database is first set up and not changed afterward," which makes "the number of partitions configured at the outset is the maximum number of nodes you can have." Too few and you cap your cluster; too many and per-partition management overhead bites. And since each partition holds a fixed fraction of the data, partition size grows with the dataset: "If partitions are very large, rebalancing and recovery from node failures become expensive. But if partitions are too small, they incur too much overhead." Hard to get right when the dataset size is highly variable. As of the book's writing, used by Riak, Elasticsearch, Couchbase, and Voldemort.

### Dynamic partitioning

Partitions split and merge based on size, the way a B-tree's top level does. Key-range-partitioned stores need this — with fixed boundaries, "if you got the boundaries wrong, you could end up with all of the data in one partition and all of the other partitions empty." When a partition exceeds a configured size it splits in two, roughly half the data each side; when it shrinks below a threshold it merges with a neighbor. After a split, one half can move to another node to balance load. HBase's default split threshold was 10 GB as of the book's writing, with transfers going through HDFS.

**The advantage:** "the number of partitions adapts to the total data volume," so small datasets carry small overhead and large ones stay bounded by the configured maximum. **The caveat:** an empty database starts with exactly one partition, "since there is no a priori information about where to draw the partition boundaries," so "all writes have to be processed by a single node while the other nodes sit idle" until the first split. The mitigation is *pre-splitting* — configuring an initial partition set on an empty database, which HBase and MongoDB both allow. For key-range partitioning that "requires that you already know what the key distribution is going to look like." Not limited to key-range data: MongoDB (since 2.4, as of the book's writing) splits dynamically under both key-range and hash partitioning.

### Partitioning proportionally to nodes

The third option fixes the partition count *per node* rather than per cluster, so the total is proportional to the number of nodes. Consequence: "the size of each partition grows proportionally to the dataset size while the number of nodes remains unchanged, but when you increase the number of nodes, the partitions become smaller again. Since a larger data volume generally requires a larger number of nodes to store, this approach also keeps the size of each partition fairly stable."

Mechanically, a joining node "randomly chooses a fixed number of existing partitions to split, and then takes ownership of one half of each of those split partitions while leaving the other half of each partition in place." Random boundaries can produce unfair splits, but averaged over enough partitions the new node takes a fair share — Cassandra's default was 256 partitions per node, and Cassandra 3.0 added an alternative algorithm that avoids unfair splits. Note the constraint: picking boundaries randomly "requires that hash-based partitioning is used." Used by Cassandra and Ketama as of the book's writing.

### Kleppmann's correction on consistent hashing

This scheme is the one that "corresponds most closely to the original definition of consistent hashing" (Karger et al., 1997) — and Kleppmann's own sidebar is explicit that the classic construction is not what databases actually run:

> "Consistent hashing, as defined by Karger et al., is a way of evenly distributing load across an internet-wide system of caches such as a content delivery network (CDN). It uses randomly chosen partition boundaries to avoid the need for central control or distributed consensus... this particular approach actually doesn't work very well for databases, so it is rarely used in practice (the documentation of some databases still refers to consistent hashing, but it is often inaccurate). Because this is so confusing, it's best to avoid the term consistent hashing and just call it hash partitioning instead."

Two things follow. First, do not treat a vendor's "we use consistent hashing" as a specification — check which of the three schemes above it actually implements. Second, "consistent" here has nothing to do with replica consistency or ACID consistency; it names an approach to rebalancing. Kleppmann also notes newer hash functions "can achieve a similar effect with lower metadata overhead."

### Automatic vs manual rebalancing

Independent of scheme. Fully automatic rebalancing reduces routine operational work but "can be unpredictable," and rebalancing is expensive — "it requires rerouting requests and moving a large amount of data from one node to another. If it is not done carefully, this process can overload the network or the nodes and harm the performance of other requests."

The failure mode to design against is the interaction with automatic failure detection: an overloaded node responds slowly, peers conclude it is dead and rebalance away from it, and the rebalancing traffic "puts additional load on the overloaded node, other nodes, and the network—making the situation worse and potentially causing a cascading failure." Kleppmann's conclusion: "it can be a good thing to have a human in the loop for rebalancing. It's slower than a fully automatic process, but it can help prevent operational surprises." The middle ground — a system that computes a suggested assignment and waits for an administrator to commit it — was what Couchbase, Riak, and Voldemort did as of the book's writing.
