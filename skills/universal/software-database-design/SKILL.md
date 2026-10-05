---
name: software-database-design
description: "Designs database schemas, migrations, and data models for PostgreSQL, MySQL, MongoDB, and Redis. Use when planning tables, relationships, indexes, or ORM-backed schema changes."
compatibility: Portable core. Works on Claude Code and Codex.
version: "1.3"
last_validated: 2026-07-11
---

# Database Design

Schema design, data modeling, migration safety, and ORM patterns. This skill covers structural decisions — what tables exist, how they relate, how schemas evolve. For tuning queries on an existing schema, use `data-sql-optimization`.

## Quick Reference

| Task | Default Picks | Notes |
|------|---------------|-------|
| Relational database | PostgreSQL (a supported stable major) | Transactions, complex queries, JSON support; verify the supported major at https://www.postgresql.org/support/versioning/ |
| Relational (MySQL family) | A supported MySQL LTS series | Use an LTS series for production, not an Innovation release; Innovation releases use calendar versioning, so the version number alone does not tell you the track. Check which series are LTS and their support end dates at https://dev.mysql.com/doc/mysql-lts-innovation-release-model/en/ before naming a version |
| Embedded / edge relational | SQLite | Release train moves fast (monthly point releases); pin a version, don't chase latest blindly |
| Flexible schema | MongoDB (a supported major) | Rapid iteration, embedded relationships; verify the major at https://www.mongodb.com/docs/manual/release-notes/ |
| Caching / sessions | Redis | Ephemeral data, counters, pub/sub |
| Graph traversals | Neo4j | Relationship-heavy queries (social, fraud) |
| Time-series | TimescaleDB, InfluxDB | Metrics, IoT, event streams |
| Managed app backend | [../software-baas-platforms/SKILL.md](../software-baas-platforms/SKILL.md) | Use when auth, realtime, storage, and functions are part of the platform choice |
| Schema migrations | expand-contract pattern | Zero-downtime changes |
| ORM | Prisma, Drizzle, SQLAlchemy, EF Core | Match stack; review generated SQL |
| Vector similarity | pgvector (co-located with PostgreSQL) | Start with exact search; add HNSW when measured latency requires ANN, then test recall under filters. See [storage selection](references/storage-paradigm-selection.md#paradigm-comparison-matrix). |
| Full-text search as the product | Elasticsearch / OpenSearch | For relevance and facets beyond the database's text search; see `software-search`. |

## When to Use This Skill

- Design table/collection schemas and normalization strategies
- Model relationships (1:N, M:N, polymorphic associations)
- Plan zero-downtime migrations (expand-contract)
- Define indexing strategies based on access patterns
- Configure ORMs and avoid common anti-patterns
- Choose between relational, document, key-value, and graph databases

## When NOT to Use This Skill

| Problem | Go here |
|---------|---------|
| Query optimization on existing schemas | [data-sql-optimization](../data-sql-optimization/SKILL.md) |
| Backend service implementation | [software-backend](../software-backend/SKILL.md) |
| Managed app backend platform (Supabase, Convex, Firebase, Appwrite, PocketBase) | [software-baas-platforms](../software-baas-platforms/SKILL.md) |
| SwiftData/Core Data schemas mirrored to CloudKit | [software-ios-native](../software-ios-native/SKILL.md) |
| On-device iOS semantic/vector retrieval | [software-ios-ai-engine](../software-ios-ai-engine/SKILL.md) |
| Data lake or warehouse architecture | [data-lake-platform](../data-lake-platform/SKILL.md) |
| Streaming or real-time pipelines | [data-streaming](../data-streaming/SKILL.md) |
| System-level data architecture decisions | [software-architecture-design](../software-architecture-design/SKILL.md) |

## Workflow

1. Define the entities, access patterns, integrity constraints, and migration constraints first.
2. Route query tuning, backend implementation, or lakehouse design to the adjacent skill when schema design is not the real problem.
3. Choose the data model and normalization stance from the decision tree.
4. Apply the migration, indexing, and ORM guidance needed for the target stack.
5. Validate current engine-specific behavior with the navigation references before final recommendations.

## Decision Tree

```text
1) Identify entities and their relationships
2) Choose data model:
   - Relational (PostgreSQL, MySQL) for structured data with complex joins
   - Document (MongoDB) for flexible schemas with embedded relationships
   - Key-value (Redis) for caching, sessions, counters
   - Graph (Neo4j) when variable-depth traversals or path queries dominate
3) Normalize to 3NF by default; denormalize with justification
4) Define primary keys, foreign keys, and constraints
5) Plan indexing strategy based on access patterns
6) Design migration path (can it be applied with zero downtime?)
```

For the full relational vs. graph vs. vector decision matrix, see [references/storage-paradigm-selection.md](references/storage-paradigm-selection.md).

## Normalization Decision Table

| Situation | Approach | Rationale |
|-----------|----------|-----------|
| Transactional data (orders, users) | Normalize to 3NF | Data integrity, reduce anomalies |
| Read-heavy dashboards | Denormalize or materialized views | Query performance |
| Audit logs | Append-only, denormalized | Immutability, query speed |
| User preferences/settings | JSON column or document | Flexible schema, rarely joined |
| Hierarchical data (categories, org charts) | Adjacency list or materialized path | Query pattern determines choice |
| Many-to-many with attributes | Junction table with columns | Clean modeling |

**When to stop normalizing.** Keep independently managed entities separate. If measured queries repeatedly rejoin fields with no independent lifecycle, consider a combined table or a cached field with an explicit invalidation owner. Treat denormalization as an operational decision because copies can drift.

**The "one big table + JSON" failure mode.** JSON is useful for variable, rarely joined attributes. Repeated filters on an inner field may need an expression or GIN index, but JSON keys still lack ordinary foreign-key integrity; if an attribute becomes central to joins or constraints, promote it to a typed column. Validate the real predicates with `EXPLAIN` before changing the model.

## Migration Safety Checklist

- [ ] Migration runs while the application serves traffic
- [ ] Lock level and duration checked for each DDL operation; PostgreSQL `ALTER TABLE` subcommands do not all take the same lock (see [migration strategies](references/migration-strategies.md#postgresql-lock-levels-verify-against-the-target-version-before-relying-on-this))
- [ ] Every DDL statement runs with `SET lock_timeout` (a few seconds) and `SET statement_timeout`, plus a retry loop — lock requests queue in arrival order, so even a fast `ACCESS EXCLUSIVE` request queues behind, and then blocks, every later reader/writer if it waits behind a long-running transaction. Check `pg_stat_activity` for long-running transactions on the target table before running DDL.
- [ ] New columns are nullable, or have a constant default (metadata-only since Postgres 11 — no table rewrite), or a volatile/expression default (this one *does* rewrite the table and holds `ACCESS EXCLUSIVE` for the duration — treat as high-risk)
- [ ] Schema change is backward-compatible with current application code
- [ ] Rollback plan exists (reverse migration or expand-contract)
- [ ] No already-applied migration edited (fix forward); concurrent index builds outside a transaction; no imports of current application models ([rules](references/migration-strategies.md#rules))
- [ ] Data backfill runs as a separate step, not inside the migration
- [ ] Migration tested against production-sized dataset
- [ ] Foreign key constraints added after data is consistent
- [ ] Migration SQL linted with a tool suited to the stack; generated SQL and online-DDL limitations reviewed ([tool choices](references/migration-strategies.md#migration-tooling))

Rule: `rules/sql/safety.md` loads this invariant when Claude edits a matching file.

## Zero-Downtime Migration Pattern (Expand-Contract)

### Compatibility Invariant

Write the compatibility matrix before the change: old code on old schema, old code on expanded schema, new code on expanded schema, and rollback code after partial backfill. The expand phase must preserve old reads and writes; backfills must be restartable and observable; the contract phase begins only after production evidence shows no caller depends on the old shape. Treat destructive DDL as final cleanup, not the migration itself.

```text
Phase 1: EXPAND
  - Add new column/table (nullable, no constraints yet)
  - Deploy app code that writes to both old and new
  - Backfill existing data into new structure

Phase 2: MIGRATE
  - Deploy app code that reads from new structure
  - Verify data consistency between old and new
  - Add constraints and indexes on new structure

Phase 3: CONTRACT
  - Deploy app code that only uses new structure
  - Remove old column/table in a follow-up migration
  - Each phase is a separate deployment — never combine
```

## Indexing Strategy

Choose index types from measured access patterns: B-tree by default, GIN/GiST/BRIN only for the query shapes they serve. In composite indexes put equality columns first, then sort, then range (Equality → Sort → Range); do not order by cardinality. Full access-pattern table and indexing rules (partial, covering, BRIN, `fillfactor`/HOT): [references/indexing-strategy.md](references/indexing-strategy.md).

## ORM Patterns

Use eager loading to prevent N+1, keep domain logic out of persistence models, review generated SQL, and drop to raw SQL for bulk work and reports. Pattern and anti-pattern tables: [references/orm-framework-guide.md](references/orm-framework-guide.md).

## Partitioning and Connection Pooling

Partition only on measured signals (maintenance time, scheduled retention drops, consistent filtering on the partition key), not because a table "feels big". Transaction-mode poolers break session-scoped state (`search_path`, advisory locks, session `SET`), so run migrations over a direct connection. Decision gates and pooler traps: [references/partitioning-and-pooling.md](references/partitioning-and-pooling.md).

## Known Traps

- Adding `NOT NULL`, uniqueness, or foreign-key constraints before a data cleanup and backfill plan exists.
- Treating a nullable "temporary" column or JSON blob as a harmless stopgap — it becomes permanent schema debt.
- Planning partitioning, sharding, or exotic indexes before real access patterns and retention rules are measured — see [Partitioning Decision Gates](references/partitioning-and-pooling.md#partitioning-decision-gates).
- Rolling out schema changes in an order that breaks mixed-version application deployments during blue/green or rolling releases.
- Assuming ORM migration generators understand operational rollout safety without a manual expand-contract review.
- For MongoDB retrieval and graph-model traps, load [MongoDB Atlas context](references/mongodb-atlas-ai-context.md#operational-checklist) or [NoSQL modeling](references/nosql-modeling.md#graph-stores). For vector-index consistency, load [storage selection](references/storage-paradigm-selection.md#paradigm-comparison-matrix).

## Anti-Patterns

| Avoid | Do Instead |
|-------|------------|
| EAV (Entity-Attribute-Value) tables | JSON columns or document store |
| Storing money as floats | Use DECIMAL / NUMERIC or integer cents |
| Soft deletes everywhere | Use only when audit trail required; otherwise hard delete |
| UUID v4 as clustered primary key | UUID v7 (RFC 9562; time-ordered, `uuidv7()` built in since PostgreSQL 18) or `BIGINT GENERATED ALWAYS AS IDENTITY` |
| Storing files in the database | Store in object storage; keep metadata/URL in DB |
| No foreign keys "for performance" | FK constraints prevent data corruption; index the FK column |
| One migration per PR with schema + data | Separate schema migration from data backfill |
| Graph: indexing every property on every label | Index only properties used in `WHERE`/`MATCH` lookup positions |
| Graph: generic relationship types (`CONNECTED_TO`, `RELATED`) | Use specific typed edges (`FOLLOWS`, `OWNS`, `REPORTS_TO`) |

**Primary-key choice.** Default to `BIGINT GENERATED ALWAYS AS IDENTITY` when one database generates IDs. Use UUIDv7 when clients or multiple services must generate IDs before insertion; its time ordering improves index locality compared with UUIDv4, but exposes approximate creation time. InnoDB's clustered-primary-key trade-off differs from PostgreSQL; see [MySQL schema notes](references/schema-design-patterns.md#mysql-innodb-schema-notes).

## Scenarios

Worked scenarios S1-S5 (multi-tenant shared vs schema-per-tenant, Postgres expand-contract with online backfill and version-specific `NOT NULL` steps, high-cardinality index design, soft-delete vs archival, JSONB versioning): [references/schema-design-scenarios.md](references/schema-design-scenarios.md).

### S6 — MongoDB Atlas as context layer for AI agents

Full pattern (collection topology, vector index, memory schema, operational checklist): see [references/mongodb-atlas-ai-context.md](references/mongodb-atlas-ai-context.md).

## Navigation

### References

- [schema-design-patterns.md](references/schema-design-patterns.md) — Common schema patterns, PostgreSQL 18 schema boundaries, MySQL InnoDB design, type-choice forensics, hierarchy models
- [migration-strategies.md](references/migration-strategies.md) — Expand-contract, migration tooling, online DDL, major-version upgrade regressions and support dates
- [sharding-decision-framework.md](references/sharding-decision-framework.md) — When to shard (after vertical/read-pool/queuing options), ER-diagram method for choosing a partitioning key, what cross-shard joins and transactions cost
- [orm-framework-guide.md](references/orm-framework-guide.md) — EF Core, SQLAlchemy, Prisma, Drizzle, Mongoose patterns; ORM pattern and anti-pattern tables
- [indexing-strategy.md](references/indexing-strategy.md) — Access-pattern to index-type table and indexing rules (ESR, partial, covering, BRIN, HOT)
- [partitioning-and-pooling.md](references/partitioning-and-pooling.md) — Partitioning decision gates and connection-pooler effects on schema and migrations
- [schema-design-scenarios.md](references/schema-design-scenarios.md) — Worked scenarios S1-S5
- [nosql-modeling.md](references/nosql-modeling.md) — Document, key-value, and graph modeling patterns
- [storage-paradigm-selection.md](references/storage-paradigm-selection.md) — Relational vs. graph vs. vector decision matrix and common polyglot combinations
- [transactions-and-storage-engines.md](references/transactions-and-storage-engines.md) — Isolation anomaly taxonomy (write skew, phantoms), serializability implementations, LSM vs B-tree tradeoffs, LSM compaction strategies and tombstone rules, RUM conjecture, Bw-trees
- [mongodb-atlas-ai-context.md](references/mongodb-atlas-ai-context.md) — MongoDB Atlas as an AI agent context layer (RAG, memory, hybrid search)

### Related Skills

| Skill | Relationship |
|-------|--------------|
| [data-sql-optimization](../data-sql-optimization/SKILL.md) | Query tuning on existing schemas |
| [software-backend](../software-backend/SKILL.md) | Data access patterns in backend services |
| [software-baas-platforms](../software-baas-platforms/SKILL.md) | Managed app-backend platform choice and migration boundaries |
| [software-csharp-backend](../software-csharp-backend/SKILL.md) | EF Core data access and migration patterns |
| [software-architecture-design](../software-architecture-design/SKILL.md) | System-level data architecture decisions |
| [data-lake-platform](../data-lake-platform/SKILL.md) | Analytical storage and lakehouse design |
| [software-ios-native](../software-ios-native/SKILL.md) | SwiftData/Core Data + CloudKit persistence in native iOS apps |
| [software-ios-ai-engine](../software-ios-ai-engine/SKILL.md) | On-device iOS semantic search and local vector retrieval |

---

Primary sources live in [data/sources.json](data/sources.json).

## Verification Gate

Before delivering output:

- [ ] Every referenced table, collection, index, and migration step is internally consistent with the proposed schema.
- [ ] If the repo already contains migration tooling, name the exact validation command; otherwise mark migration validation as unverified.
- [ ] Expand-contract guidance includes rollout order and rollback notes for breaking schema changes.
- [ ] Every referenced schema file, migration path, or ORM config path exists in the repo or is explicitly marked as proposed.

## Learnings Loop

When prior decisions or pitfalls are relevant, consult `learnings.consolidated.md` if present; use `learnings.md` only for needed history or as the available fallback. Otherwise skip both.

After applying it, if you encountered a pattern worth remembering, a mistake worth preventing, or a domain fact that surprised you, append one dated bullet to `learnings.md` via `agents-skills-feedback-loop/scripts/append_learning.py`. Do not modify `SKILL.md` itself.
