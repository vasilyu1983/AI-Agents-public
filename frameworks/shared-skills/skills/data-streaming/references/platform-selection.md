# Streaming Platform Selection

Use this reference when the user needs a platform recommendation or migration path.

last_validated: 2026-07-11

## Table of Contents

- [Decision Table (July 2026)](#decision-table-july-2026)
- [Start With The Decision Axes](#start-with-the-decision-axes)
- [Kafka](#kafka)
- [Redpanda](#redpanda)
- [WarpStream / AutoMQ](#warpstream--automq)
- [Pulsar](#pulsar)
- [Kinesis](#kinesis)
- [Stream Processor Decision Table](#stream-processor-decision-table)
- [Recommendation Protocol](#recommendation-protocol)

## Decision Table (July 2026)

| Criterion | Kafka (self-hosted) | Redpanda | WarpStream / AutoMQ | Pulsar | Kinesis |
|---|---|---|---|---|---|
| Connector/CDC ecosystem | best | good | good (Kafka API) | limited | limited |
| Operational complexity | medium (KRaft quorum) | low (single binary) | lowest (serverless/S3-backed) | high | none |
| Cost at scale | medium | medium | lowest (S3 storage cost) | medium | high (shard billing) |
| Kafka API compatibility | canonical | full | full | partial | none |
| Multi-tenancy | limited | limited | limited | native | AWS-only |
| Geo-replication | MirrorMaker 2 | MirrorMaker 2 | limited | native | AWS cross-region |
| Queue semantics (KIP-932) | GA in 4.2+ | roadmap | roadmap | native | none |
| Cloud portability | high | high | medium (S3 lock-in) | high | none |
| Flink/lakehouse integration | best | good | good | good | limited |

**Diskless Kafka vendors (June 2026):** WarpStream (Confluent/IBM acquired) and AutoMQ are both in production. AutoMQ production: JD.com (13T msgs/day), Grab, HubSpot. WarpStream production: Grafana Labs, Cursor, Robinhood. KIP-1150 (Diskless Topics) accepted by Apache Kafka community March 2026 — not yet GA upstream.

## Start With The Decision Axes

Evaluate these before naming a platform:

- Operational model: self-hosted, cloud-managed, or fully managed
- Compatibility: Kafka API, connector ecosystem, existing client libraries
- Multi-tenancy and geo-replication needs
- Replay and retention expectations
- Peak throughput, sustained throughput, and latency targets
- Team capability for broker operations, upgrades, and incident response
- Downstream integration: Flink, lakehouse sinks, CDC tooling, schema registry

## Kafka

Prefer when:

- Broadest ecosystem for connectors, CDC, schema tooling, and client support is required
- Kafka compatibility matters more than reducing operational surface area
- Mixed open-source and managed deployment is the target state

Watch for:

- Partition-count inflation without a real consumer-parallelism need
- Weak retention planning that makes replay impractical
- Assuming broker guarantees solve sink deduplication
- Not planning KRaft controller quorum sizing before deployment (differs from ZooKeeper ensemble sizing)

**Kafka 4.x notes:** 4.0 removed ZooKeeper (March 2025). Latest stable: 4.3.1 (Jun 25, 2026) — a patch release fixing a critical Kafka Streams RocksDB native memory leak present in 4.3.0. KIP-932 share groups (queue semantics) GA in 4.2. KIP-848 next-gen consumer rebalance GA in 4.0.

## Redpanda

Prefer when:

- Kafka API compatibility is required
- Single-binary deployment model reduces operational surface
- Teams stay in the Kafka tooling universe

Watch for:

- Assuming every Kafka-adjacent integration behaves identically without testing
- Recommending solely for performance claims without workload evidence

## WarpStream / AutoMQ

Prefer when:

- Storage cost reduction is a primary driver (S3-backed, no local broker disks)
- Serverless (WarpStream) or S3-backend (AutoMQ) model fits the infrastructure
- High throughput workloads where storage dominates cost

Watch for:

- S3 dependency introduces latency variability; verify p99 latency against SLOs
- WarpStream: fully managed, Confluent/IBM-owned; AutoMQ: customer-operated control plane
- Not yet upstream GA — evaluate stability vs Apache Kafka mainstream for production

## Pulsar

Prefer when:

- Multi-tenancy, geo-replication, or topic-isolation controls are primary requirements
- Segment/tiered storage tightly integrated with platform design is needed

Watch for:

- Underestimating platform complexity if the team knows Kafka but not Pulsar
- Ecosystem depth gaps vs Kafka for connectors and CDC tooling

## Kinesis

Prefer when:

- AWS-managed simplicity outweighs open portability
- Low-ops streaming inside an AWS-first estate
- Downstream AWS integration (Lambda, Firehose, Analytics) is a primary use case

Watch for:

- Teams that need broad portability or non-AWS consumers
- Shard scaling, enhanced fan-out, and per-shard cost characteristics

## Stream Processor Decision Table

| Requirement | Flink | Kafka Streams | Spark Structured Streaming |
|---|---|---|---|
| Stateful event-time, joins, windows, timers | best | limited | good |
| Exactly-once with savepoints | best | good | good |
| Lightweight in-app processing | poor (separate cluster) | best | poor |
| Kafka-native without extra infra | no | yes | no |
| Lakehouse sinks (Iceberg, Hudi, Paimon) | best (Dynamic Iceberg Sink) | limited | good |
| Micro-batch acceptable | yes | yes | yes |
| Disaggregated state (Flink 2.x) | yes | no | no |
| Materialized tables | yes (Flink 2.x) | no | limited |

**Flink 2.x notes:** Latest stable: 2.3.0 (Jun 25, 2026) — changelog conversion SQL operators, redesigned native S3 filesystem on AWS SDK v2, adaptive partition selection for backpressure. Flink 2.2.0 (Dec 2025) added real-time data + AI integrations and native Paimon integration. Flink 2.0.x introduced disaggregated state backend, async execution, and Materialized Tables. Savepoints from 1.x require explicit migration.

## Recommendation Protocol

1. Write down the non-negotiables first.
2. Score at most 3 viable options, not every possible option.
3. Separate platform facts from strategic preference.
4. State the lock-in boundary: client protocol, registry, processor, or sink format.
5. If no workload numbers exist, recommend a pilot instead of overstating certainty.
