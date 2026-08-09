# Stream Processing Patterns

Use this reference when the user asks how to shape a streaming topology, processor, or sink path.

## Table of Contents

- [Choose The Simplest Pattern That Preserves Correctness](#choose-the-simplest-pattern-that-preserves-correctness)
- [Pattern Guide](#pattern-guide)
- [Filter And Enrich](#filter-and-enrich)
- [Windowed Aggregation](#windowed-aggregation)
- [Stream-Table Join](#stream-table-join)
- [Stream-Stream Join](#stream-stream-join)
- [Deduplication](#deduplication)
- [Event Time Default](#event-time-default)
- [Delivery Semantics](#delivery-semantics)
- [At-least-once](#at-least-once)
- [Exactly-once Or Business-Level Idempotency](#exactly-once-or-business-level-idempotency)
- [Reprocessing Rules](#reprocessing-rules)

## Choose The Simplest Pattern That Preserves Correctness

Start with the minimal topology that satisfies the business requirement:

- Pass-through routing
- Filter and enrich
- Stateful deduplication
- Windowed aggregation
- Stream-table enrichment
- Stream-stream correlation
- CDC normalization into a sink-ready model

Do not jump to complex joins or exactly-once claims without proving the business need.

## Pattern Guide

### Filter And Enrich

Use when:

- Events need normalization, validation, or a small lookup enrichment
- State size is modest and the main goal is downstream cleanliness

Prefer:

- Kafka Streams for light Kafka-native transformations
- Flink when event-time semantics or complex state are involved

### Windowed Aggregation

Use when:

- The user needs rolling metrics, counts, sums, sessions, or periodic summaries

Important decisions:

- Processing time vs event time
- Allowed lateness
- Watermark strategy
- Re-emit behavior when late events update prior windows

### Stream-Table Join

Use when:

- An event stream needs reference or slowly changing context

Guardrails:

- Define freshness expectations for the table side
- Decide how missing reference data is handled
- Avoid per-event database lookups when the platform can maintain state locally

### Stream-Stream Join

Use when:

- Two event streams need temporal correlation

Guardrails:

- Define join windows explicitly
- State what happens when one side is delayed or absent
- Budget for state growth and late data

### Deduplication

Use when:

- Upstream retries or CDC resends can produce duplicates

Guardrails:

- Choose the dedupe key and TTL intentionally
- Confirm the dedupe horizon covers realistic retries and backfills
- Avoid unbounded state

## Event Time Default

Default to event-time processing for analytical or stateful workloads unless the user clearly only needs low-complexity operational routing.

Why:

- It handles late or out-of-order data more honestly
- It aligns better with CDC and replay
- It reduces false confidence from processing-time windows

## Delivery Semantics

### At-least-once

Default when:

- Duplicate-tolerant downstream systems already exist
- Simplicity is more important than strict dedupe

### Exactly-once Or Business-Level Idempotency

Use when:

- Financial, billing, inventory, or user-facing correctness depends on duplicate suppression

Remember:

- Processor guarantees do not remove the need for sink idempotency or transactional boundaries
- Document the exact end-to-end boundary of the guarantee

## Reprocessing Rules

- Define checkpoint and savepoint policy for processors
- Define replay boundaries for topics and sinks
- Define whether reprocessing overwrites, upserts, or appends
- Define how delete events and tombstones behave during replay
