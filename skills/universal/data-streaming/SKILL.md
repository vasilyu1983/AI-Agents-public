---
name: data-streaming
description: "Designs streaming platforms for Kafka, Flink, CDC, and lakehouse ingestion. Use when planning event backbones, CDC pipelines, schema governance, or real-time lakehouse delivery."
compatibility: Portable core. Works on Claude Code and Codex.
version: "1.2"
last_validated: 2026-07-11
---

# Data Streaming

**Modern Best Practices:** choose the event backbone and stream processor separately, treat schemas and replay as product interfaces, default to event-time processing for stateful analytics, and verify managed-service behavior from primary docs before making vendor-specific recommendations.

Primary sources live in `data/sources.json`. Refresh time-sensitive claims against official docs before making definitive recommendations about managed services, version-specific features, limits, or pricing.

This skill covers the **data platform side** of streaming: event backbones, CDC, stateful processing, schema governance, and real-time delivery into lakes, warehouses, search, or serving systems.

## When to Use

- Choose between Kafka, Redpanda, Pulsar, Kinesis, or managed Kafka offerings
- Design topic strategy, partitioning, retention, replay, and ordering guarantees
- Build or fix CDC pipelines with Debezium, Flink CDC, or managed database-streaming tools
- Choose between Flink, Kafka Streams, Spark Structured Streaming, or lighter transformation paths
- Define schema registry, compatibility, contract, and tombstone handling rules
- Deliver streams into Iceberg, Hudi, Delta, ClickHouse, warehouses, caches, or search systems
- Review streaming SLOs, lag, checkpointing, reprocessing, and operational failure modes
- Plan Kafka broker upgrades, the ZooKeeper-to-KRaft migration, consumer-protocol (KIP-848) or share-group (KIP-932) adoption, and client producer defaults

## When NOT to Use

- Lakehouse storage formats, catalogs, or medallion architecture -> Use [data-lake-platform](../data-lake-platform/SKILL.md)
- OLTP schema tuning or transactional query optimization -> Use [data-sql-optimization](../data-sql-optimization/SKILL.md)
- Event-driven application architecture, CQRS, or domain event design -> Use [software-architecture-design](../software-architecture-design/SKILL.md)
- BI dashboard automation and Metabase APIs -> Use [data-metabase](../data-metabase/SKILL.md)
- Product instrumentation and attribution strategy -> Use `marketing-product-analytics`

## Triage Questions

1. What is the real requirement: operational events, CDC, analytical enrichment, or customer-facing low-latency delivery?
2. What matters most: portability, managed simplicity, geo-replication, cost, or end-to-end latency?
3. Where must ordering hold: globally, per key, or only within a local processing step?
4. What is the replay model: full retention, compacted snapshots, time-bounded backfills, or one-shot delivery?
5. Which guarantees are required: at-most-once, at-least-once, or business-level exactly-once with idempotent sinks?
6. Which downstream systems consume the stream: lakehouse tables, warehouses, search, caches, APIs, or ML features?
7. What is the operational baseline: small team, platform team, managed service, or self-hosted multi-region cluster?

## Default Workflow (Use Unless User Overrides)

1. Choose the backbone first with `references/platform-selection.md`.
2. Define topic, key, retention, replay, and schema strategy before discussing processors. Use [assets/topic-contract-template.md](assets/topic-contract-template.md).
3. Choose the processing model with `references/stream-processing-patterns.md`: pass-through, enrich, aggregate, join, dedupe, or CDC normalization.
4. Lock CDC and schema-governance rules with `references/cdc-and-schema-governance.md` and [assets/cdc-rollout-checklist.md](assets/cdc-rollout-checklist.md).
5. Define delivery and sink behavior: upserts, deletes, late data, watermarking, and reprocessing boundaries.
6. Add SLOs, lag monitoring, checkpoint and savepoint policy, and incident drills with `references/operations-and-slos.md`.
7. Score tradeoffs explicitly with [assets/streaming-platform-scorecard.md](assets/streaming-platform-scorecard.md) when the user asks for the "best" platform.

## Default Baseline

- Backbone: Kafka-compatible event log unless a clear managed-service or multi-tenant requirement pushes elsewhere
- Stream processing: Flink for stateful event-time pipelines; Kafka Streams for lighter in-app processing
- CDC: log-based CDC first; avoid trigger-based CDC unless constraints force it
- Contracts: registry-backed schemas for shared or long-lived topics
- Reprocessing: plan for replay before launch; do not treat backfills as exceptional
- Sinks: design sink idempotency explicitly; "exactly-once" claims are incomplete without sink behavior

## Backbone Decision Table

| Requirement | Kafka (self-hosted) | Redpanda | WarpStream / AutoMQ | Pulsar | Kinesis |
|---|---|---|---|---|---|
| Broadest connector/CDC ecosystem | best | good | good (Kafka API) | limited | limited |
| Operational simplicity | medium (KRaft-only in 4.x, no ZooKeeper to run) | good (single binary) | best (serverless or S3-backed) | poor | best |
| Cost at high throughput | price the workload | price the workload | price storage, requests, and egress | price the workload | price capacity mode and reads |
| Multi-tenancy / namespace isolation | limited | limited | limited | best | AWS-only |
| Geo-replication built-in | via MirrorMaker 2 | via MirrorMaker 2 | limited | native | AWS-only |
| Kafka API compatibility | canonical | verify required APIs and versions | verify required APIs and versions | partial | no |
| Queue semantics (share groups) | KIP-932 (check status for your version) | check vendor docs | check vendor docs | native | no |
| Cloud portability | high | high | medium (S3 dependency) | high | none |

Ownership and product lines of managed Kafka-compatible services change through acquisitions. Check the vendor's current docs and support terms before recommending one.

## Exactly-Once Decision Path

```text
Need exactly-once?
  -> Is the sink idempotent or transactional?
       No  -> Add sink-level deduplication key or upsert semantics first
       Yes -> Enable broker/processor exactly-once:
                Kafka: enable.idempotence=true + transactional.id
                Flink: CheckpointingMode.EXACTLY_ONCE + Sink V2 committer (two-phase commit)
                Downstream Kafka consumers: isolation.level=read_committed
                  (the default read_uncommitted also reads aborted records)
  -> Does the sink support two-phase commit?
       No  -> Business-level idempotency (dedupe key + conditional write)
       Yes -> End-to-end exactly-once boundary confirmed
  -> Document the exact guarantee boundary — broker, processor, AND sink
```

## Version-Sensitive Facts (Look Up, Do Not Quote)

Release lines, feature status, and patch regressions change faster than this skill. Before naming a version or calling a feature GA:

- **Kafka:** read the Apache Kafka release announcements for the current stable line, known regressions fixed in patch releases (Kafka Streams state-store issues in particular), and the status of KIP-932 share groups (preview vs GA) for the exact broker and client versions in use.
- **Flink:** read the release announcement for the target version. Carry over its own qualifiers: a feature it calls experimental stays experimental in your recommendation. Do not call a feature GA (for example Materialized Tables or disaggregated state) unless the release notes say so.
- **Kafka upgrades and adoption:** migration order, upgrade traps, consumer-protocol and share-group adoption checks, and per-client producer defaults live in `references/kafka-upgrades-and-client-defaults.md`.
- **Iceberg engines:** per-engine v3 read, write, and maintenance status lives in `references/engine-table-format-state.md` as lookup steps; confirm it in each vendor's current docs.

Stable facts that do not need a lookup:

- Kafka 4.0 removed ZooKeeper; every 4.x cluster is KRaft-only. Controller quorum sizing differs from ZooKeeper ensemble sizing, so do not map 1:1. Migrate non-production first and verify the controller quorum before cutting over.
- KIP-932 share groups let several consumers cooperate on one partition with per-record acknowledgment. That gives queue semantics without partition-per-consumer assignment, and it is the one Kafka mode where pooled (M/M/c) sizing applies.
- Flink 2.0 removed the legacy `SinkFunction`/`TwoPhaseCommitSinkFunction` and `AssignerWith*Watermarks` APIs. Use Sink V2 and `WatermarkStrategy`. For a 1.x-to-2.x upgrade, take a savepoint and test restore with the target job: compatible state, stable operator IDs, supported connectors, and changed APIs determine whether it works. Check the [Flink upgrade guide](https://nightlies.apache.org/flink/flink-docs-release-2.0/docs/ops/upgrading/) before migrating Table API jobs or relying on SQL Gateway behavior.

## Iceberg Streaming Ingestion Pattern

Standard production stack: Kafka -> Flink (Dynamic Iceberg Sink) -> Iceberg table -> compaction job.

```
# Illustrative starting point, not from the Flink Dynamic Iceberg Sink blog — tune on the real workload
execution.checkpointing.interval = 5 min   # each checkpoint is one commit opportunity
write.target-file-size-bytes = 536870912   # Iceberg table default (512 MB); lowering it creates more small files
write.fanout.enabled = true                # unordered writes across partitions
# Schema compatibility (e.g. FULL_TRANSITIVE) is a schema-registry subject setting, not a sink option
# Compaction: run on cold partitions; skip hot (current) partition
```

- Every streaming approach produces small files — pair ingestion with a scheduled compaction job.
- With one commit opportunity per checkpoint and all else equal, a 5-minute interval creates one-fifth as many commit opportunities as a 1-minute interval (80% fewer). That arithmetic does not predict file count: partitions, writer parallelism, rollover, traffic shape, and compaction also matter. Measure file count, size distribution, recovery time, and latency on the real workload before tuning.
- Iceberg v3 (ratified spec): deletion vectors, row lineage (`_row_id`), variant data, default column values, geometry/geography types, nanosecond timestamps, encryption foundations. Do not quote a DML speed-up multiplier for deletion vectors; the spec gives none. Engine support differs per engine and per operation, so check each engine's current read, write, and maintenance support (`references/engine-table-format-state.md`) before committing a multi-engine stack to v3 features.

## Replay Acceptance Gate

A replay plan is complete only when it answers four separate questions:

1. **Source position:** Which offsets, timestamps, snapshot, or CDC log position define the replay boundary?
2. **State reset:** Which processor state and checkpoints are restored, discarded, or rebuilt?
3. **Sink behavior:** Which idempotency key, upsert, transaction, or dedupe window prevents duplicate business effects?
4. **Consumer isolation:** How are replay records kept from triggering emails, payments, alerts, or other irreversible side effects twice?

Rehearse one bounded replay through the real sink before launch. Pass only if row/event counts reconcile at source and sink, deletes and late events behave as contracted, consumer lag recovers inside the SLO, and a second replay produces the same business state.

## Quick Reference

| Task | Resource | When to Use |
|------|----------|-------------|
| Choose Kafka vs Redpanda vs Pulsar vs Kinesis | `references/platform-selection.md` | New platform selection or platform migration |
| Choose Flink vs Kafka Streams vs Spark | `references/stream-processing-patterns.md` | Stateful processing, joins, windows, or low-latency transforms |
| Design CDC and schema evolution | `references/cdc-and-schema-governance.md` | Debezium, snapshots, tombstones, contracts, registry policy |
| Define lag, replay, failover, and checkpoint policy | `references/operations-and-slos.md` | Production hardening and incident prevention |
| Draft topic naming, keys, retention, and schema rules | [assets/topic-contract-template.md](assets/topic-contract-template.md) | New topic or shared event contract |
| Plan a CDC rollout safely | [assets/cdc-rollout-checklist.md](assets/cdc-rollout-checklist.md) | Database-to-stream launch or CDC migration |
| Compare platform options side by side | [assets/streaming-platform-scorecard.md](assets/streaming-platform-scorecard.md) | Decision reviews and recommendation memos |

## Operating Principles

### 1. Ordering Is Scoped, Not Global

- Promise ordering only where the platform can really preserve it, usually per partition and key.
- If the business process needs entity-level sequencing, make the key choice explicit.

### 2. Schemas Are Contracts

- Shared topics need governed evolution rules, owners, compatibility mode, and deprecation windows.
- Plain JSON is acceptable for prototyping, not for durable shared interfaces.

### 3. Replay Is A First-Class Operation

- Retention, compaction, checkpoints, and sink idempotency define whether replay is safe.
- Do not ship a pipeline that cannot be re-run after bad code or bad data.

### 4. "Exactly-Once" Is End-To-End, Not A Checkbox

- Broker or processor guarantees are insufficient if the sink can duplicate writes or mishandle deletes.
- State the exact boundary where deduplication or transactional guarantees end.

### 5. CDC Needs Delete And Snapshot Strategy

- Decide how snapshots, schema changes, tombstones, and source failover behave before launch.
- Downstream consumers must know whether deletes arrive as tombstones, hard deletes, or soft-delete flags.

## Templates

- [assets/topic-contract-template.md](assets/topic-contract-template.md)
- [assets/cdc-rollout-checklist.md](assets/cdc-rollout-checklist.md)
- [assets/streaming-platform-scorecard.md](assets/streaming-platform-scorecard.md)

## Known Traps

- Designing the event backbone around broker features before defining domain ownership, event contracts, and replay expectations.
- Treating topic retention as a substitute for a durable system of record, replay plan, or downstream recovery workflow.
- Claiming exactly-once behavior without specifying the guarantee boundary across broker, processor, sink, and side effects.
- Mixing operational events, analytical CDC, and integration commands into the same topics without independent retention, schema, and consumer-SLA rules.
- Shipping CDC streams without idempotency keys, snapshot semantics, tombstone handling, and late-arrival rules agreed by consumers.
- Scaling partitions, consumer groups, and stateful processors independently and then discovering the keying model breaks ordering or hotspot behavior.

## Common Anti-Patterns

- Using the stream platform as a generic dumping ground for every event rather than curating contracts by domain and use case.
- Putting business-critical enrichment or policy decisions in opaque stream jobs with no replay procedure, lineage, or owner.
- Letting producers evolve schemas opportunistically while expecting consumers to absorb breaking changes.
- Building low-latency pipelines on top of unstable event keys, non-deterministic joins, or external side-effect calls inside hot-path processors.
- Choosing real-time processing because it sounds strategic when batch or micro-batch would meet the product and cost requirements.
- Treating DLQs as the main error-handling strategy instead of fixing classifier logic, validation, backpressure, and recovery paths upstream.

## Navigation

- [references/platform-selection.md](references/platform-selection.md) — Load when choosing between Kafka, Redpanda, Pulsar, Kinesis, or managed offerings; includes decision axes and recommendation protocol.
- [references/stream-processing-patterns.md](references/stream-processing-patterns.md) — Load when designing topology, windows, joins, deduplication, or delivery semantics.
- [references/cdc-and-schema-governance.md](references/cdc-and-schema-governance.md) — Load when building CDC pipelines, handling deletes/tombstones, or setting schema registry policy.
- [references/operations-and-slos.md](references/operations-and-slos.md) — Load when defining SLOs, dashboards, incident patterns, or consumer commit/DLQ policy.
- [references/engine-table-format-state.md](references/engine-table-format-state.md) — Load when reasoning about Iceberg v3, Paimon, or Kafka KIP-1150 diskless status.
- [references/control-theory-applied.md](references/control-theory-applied.md) — Load when designing lag-aware autoscalers, producer flow control, or watermark tuning.
- [references/queueing-theory-applied.md](references/queueing-theory-applied.md) — Load when sizing partitions, modeling lag SLOs, or scaling coordinator throughput.
- [references/streaming-patterns.md](references/streaming-patterns.md) — Load for starter code: Kafka producer/consumer, Kafka Connect, Flink and Spark streaming jobs, and Kappa/Lambda sketches.
- [assets/template-kafka-ingestion.md](assets/template-kafka-ingestion.md) — Load when scaffolding Kafka ingestion into a lake: producers, batch consumers, connectors, and lag alerts.
- [references/kafka-upgrades-and-client-defaults.md](references/kafka-upgrades-and-client-defaults.md) — Load when planning a Kafka broker upgrade or ZooKeeper-to-KRaft migration, adopting KIP-848 or share groups, or checking producer defaults for a specific client.
- [references/distributed-systems-applied.md](references/distributed-systems-applied.md) — Load when reasoning about ISR quorum, exactly-once via idempotency, leader-epoch fencing, or consumer-group rebalance correctness.
- [Formal methods](../foundations-formal-methods/SKILL.md) — Load only when a replay, offset/side-effect, rebalance, or fencing protocol has an explicit invariant to check. Return the state/transition boundary and counterexample or bounded safety result; keep delivery guarantees conditional on runtime semantics. Skip routine connector setup.
- `data/sources.json` — Primary-source URLs for all platforms, processors, CDC tools, and table formats.

## Current-Source Policy

- Prefer `trust_tier: primary` entries in `data/sources.json` for platform capabilities, service limits, compatibility, and release-sensitive behavior.
- For recommendation questions, verify current managed-service behavior, connector support, quotas, and pricing from official docs instead of relying on frozen comparisons.
- Separate verified facts from judgment calls when comparing Kafka, Redpanda, Pulsar, Kinesis, Flink, and managed offerings.
- If web access is unavailable, say the recommendation is partially unverified.

## Related Skills

- [data-lake-platform](../data-lake-platform/SKILL.md) for storage formats, catalogs, serving layers, and lakehouse architecture
- [data-analytics-engineering](../data-analytics-engineering/SKILL.md) for marts, semantic layers, and metric governance on top of streaming data
- [data-sql-optimization](../data-sql-optimization/SKILL.md) for database-side performance and transactional operations
- [software-architecture-design](../software-architecture-design/SKILL.md) for application eventing, CQRS, and domain architecture
- [ops-devops-platform](../ops-devops-platform/SKILL.md) for deployment, infra automation, and runbook operations

## Learnings Loop

When prior decisions or pitfalls are relevant, consult `learnings.consolidated.md` if present; use `learnings.md` only for needed history or as the available fallback. Otherwise skip both.

After applying it, if you encountered a pattern worth remembering, a mistake worth preventing, or a domain fact that surprised you, append one dated bullet to `learnings.md` via `agents-skills-feedback-loop/scripts/append_learning.py`. Do not modify `SKILL.md` itself.
