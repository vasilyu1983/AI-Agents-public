# Inbox Engine Patterns — Event-Driven Agent Intake

**Purpose**: Operational patterns for building an Inbox Engine — the event-driven intake layer that monitors sources, classifies incoming signals, deduplicates, prioritizes, and routes to appropriate agents or workflows.

---

## 1. Architecture Overview

```text
┌──────────────────────────────────────────────────┐
│                  SOURCE MONITORS                  │
│  [webhook] [polling] [stream] [cron] [A2A]       │
└──────────┬───────────────────────────────────────┘
           │ raw events
┌──────────▼───────────────────────────────────────┐
│                    INGESTION                      │
│  normalize → validate → assign envelope ID       │
└──────────┬───────────────────────────────────────┘
           │ normalized events
┌──────────▼───────────────────────────────────────┐
│                  CLASSIFICATION                   │
│  actionable | informational | noise              │
└──────────┬───────────────────────────────────────┘
           │ classified events
┌──────────▼───────────────────────────────────────┐
│               DEDUPLICATION + BATCHING            │
│  content hash → sliding window → merge similar   │
└──────────┬───────────────────────────────────────┘
           │ deduplicated events
┌──────────▼───────────────────────────────────────┐
│                  PRIORITIZATION                   │
│  SLA assignment → urgency scoring → queue rank   │
└──────────┬───────────────────────────────────────┘
           │ prioritized events
┌──────────▼───────────────────────────────────────┐
│                     ROUTING                       │
│  actionable → Action Graph                       │
│  informational → Data Agent → Knowledge Base     │
│  noise → log + discard                           │
└──────────────────────────────────────────────────┘
```

---

## 2. Event Envelope Schema

### Pattern: Universal Event Envelope

```yaml
event_envelope:
  id: "string (uuid)"
  source:
    type: "webhook | poll | stream | cron | a2a | user"
    identifier: "string (source system ID)"
    received_at: "ISO 8601"
  payload:
    content_type: "text | json | binary"
    body: "..."
    content_hash: "sha256 (for deduplication)"
  classification:
    signal_class: "actionable | informational | noise"
    confidence: "float (0.0 - 1.0)"
    classified_by: "rule | llm | hybrid"
  priority:
    urgency: "critical | high | medium | low"
    sla_ms: 2000
    queue: "string (routing queue name)"
  routing:
    target: "action_graph | data_agent | discard"
    workflow_id: "string (if routed to action graph)"
    agent_id: "string (if routed to specific agent)"
  lifecycle:
    status: "received | classified | routed | processing | completed | failed"
    attempts: 0
    max_attempts: 3
    dead_letter_after: 3
```

### Checklist: Event Ingestion

- [ ] Assign unique envelope ID at ingestion (idempotency key).
- [ ] Normalize payload to standard format (strip transport metadata).
- [ ] Compute content hash for deduplication.
- [ ] Validate payload against expected schema (reject malformed early).
- [ ] Record received_at timestamp for SLA tracking.
- [ ] Acknowledge receipt to source (prevent redelivery).

---

## 3. Signal Classification

### Pattern: Three-Class Triage

| Class | Definition | Action | Examples |
|-------|-----------|--------|----------|
| **Actionable** | Requires agent action within SLA | Route to Action Graph | User request, alert breach, approval needed, error requiring fix |
| **Informational** | Updates knowledge, no immediate action | Route to Data Agent → Knowledge Base | Data refresh, status update, new doc published, metric report |
| **Noise** | Irrelevant or duplicate, safe to discard | Log and discard | Heartbeat, duplicate webhook, stale notification, health check |

### Classification Methods

| Method | Speed | Accuracy | Cost | Best For |
|--------|-------|----------|------|----------|
| **Rule-based** | <1ms | High (known patterns) | Zero | Structured events with clear signatures |
| **LLM-based** | 200-500ms | High (ambiguous content) | Token cost | Unstructured text, novel event types |
| **Hybrid** | 5-50ms | Highest | Low | Rules first, LLM fallback for uncertain |

### Hybrid Classification Pipeline

```text
1. RULE ENGINE: Match event against known patterns
   ├── Match found (confidence > 0.9)? → Use rule classification
   └── No match or low confidence? → Continue to step 2

2. LIGHTWEIGHT CLASSIFIER: Fast ML model or heuristic
   ├── Classification confident (> 0.8)? → Use classifier result
   └── Uncertain? → Continue to step 3

3. LLM CLASSIFICATION: Use small, fast model
   └── Return classification with confidence score
```

### Rule Examples

```yaml
classification_rules:
  - name: "user_message"
    match:
      source_type: "user"
    classify_as: "actionable"
    priority: "high"

  - name: "webhook_data_update"
    match:
      source_type: "webhook"
      payload_contains: ["data_updated", "record_changed"]
    classify_as: "informational"
    priority: "medium"

  - name: "heartbeat"
    match:
      source_type: "poll"
      payload_contains: ["heartbeat", "ping", "health_check"]
    classify_as: "noise"
```

---

## 4. Deduplication and Batching

### Pattern: Content-Hash Deduplication

```text
For each incoming event E:
1. Compute content_hash = SHA256(E.payload.body)
2. Check sliding window (last N minutes) for matching hash
3. If match found:
   a. Increment duplicate_count on original
   b. Discard duplicate (log for audit)
4. If no match:
   a. Add to sliding window
   b. Continue to prioritization
```

### Configuration

```yaml
deduplication:
  window_size_minutes: 15
  hash_algorithm: "sha256"
  hash_fields: ["payload.body"]  # which fields to hash
  strategy: "keep_first"  # keep_first | keep_latest | merge

batching:
  enabled: true
  window_ms: 1000           # batch window
  max_batch_size: 50        # max events per batch
  batch_key: "source.identifier"  # group by source
  merge_strategy: "latest_wins"   # for same-entity updates
```

### Batching Strategies

| Strategy | When to Use | Example |
|----------|-------------|---------|
| **Time-window** | Events arrive in bursts | Batch all events in 1s window |
| **Count-based** | Steady stream, process in chunks | Process every 50 events |
| **Entity-based** | Multiple updates to same entity | Merge 5 updates to user-123 into 1 |

---

## 5. Priority Queue and SLA Routing

### Pattern: SLA-Based Priority Assignment

```yaml
priority_matrix:
  critical:
    sla_ms: 1000
    queue: "immediate"
    triggers:
      - "security_alert"
      - "system_failure"
      - "user_escalation"
  high:
    sla_ms: 5000
    queue: "fast"
    triggers:
      - "user_message"
      - "approval_request"
      - "payment_event"
  medium:
    sla_ms: 30000
    queue: "standard"
    triggers:
      - "data_update"
      - "scheduled_task"
      - "report_ready"
  low:
    sla_ms: 300000
    queue: "background"
    triggers:
      - "analytics_event"
      - "log_aggregation"
      - "cleanup_task"
```

### Queue Implementation Options

| Implementation | Latency | Durability | Best For |
|---------------|---------|------------|----------|
| **In-memory (deque)** | <1ms | None | Single-process, dev/test |
| **Redis Sorted Set** | <5ms | Configurable | Multi-process, moderate scale |
| **SQS / Cloud Pub/Sub** | 10-100ms | High | Distributed, production |
| **Kafka** | 5-50ms | High | High-throughput, event sourcing |

---

## 6. Routing to Action Graph

### Pattern: Event → Workflow Mapping

```yaml
routing_table:
  - event_pattern:
      source_type: "user"
      signal_class: "actionable"
    route_to:
      target: "action_graph"
      workflow: "conversational_agent"
      entry_node: "step-classify-intent"

  - event_pattern:
      source_type: "webhook"
      payload_contains: ["order_created"]
    route_to:
      target: "action_graph"
      workflow: "order_processing"
      entry_node: "step-validate-order"

  - event_pattern:
      signal_class: "informational"
    route_to:
      target: "data_agent"
      pipeline: "ingest_and_index"

  - event_pattern:
      signal_class: "noise"
    route_to:
      target: "discard"
      log_level: "debug"
```

### Handoff Contract (Inbox → Action Graph)

```yaml
handoff_payload:
  event_id: "string (from envelope)"
  workflow_id: "string (from routing table)"
  entry_node: "string (starting node in action graph)"
  context:
    event_payload: "..."
    classification: "actionable"
    priority: "high"
    sla_remaining_ms: 4500
  metadata:
    source: "inbox_engine"
    routed_at: "ISO 8601"
    attempt: 1
```

### Choreography Pattern (Decentralized Alternative)

Instead of a centralized routing table, agents can react to each other's events directly — each agent emits events after completing work, and downstream agents subscribe to the events they care about.

```text
Centralized (routing table):
  Inbox → Router → Agent A
                 → Agent B

Choreography (event-driven):
  Inbox → emits "message.received"
  Agent A listens for "message.received" → processes → emits "structured.extracted"
  Agent B listens for "structured.extracted" → processes → emits "intent.classified"
  Agent C listens for "intent.classified" → routes to final destination
```

**When to use choreography**:

| Criteria | Centralized Routing | Choreography |
|----------|-------------------|--------------|
| Agent count | <5 agents | 5+ agents |
| Coupling tolerance | Tight (known routes) | Loose (agents are independent) |
| Failure isolation | Single point of failure at router | Independent — one agent failing doesn't block others |
| Debugging | Easy (single routing table) | Harder (distributed trace required) |
| Scaling | Vertical (router bottleneck) | Horizontal (add agents independently) |

**Recommendation**: Start with centralized routing (simpler, easier to debug). Migrate to choreography when agent count or throughput demands it.

**Reference**: [Knative eventing](https://knative.dev/blog/articles/knative-eventing-eda-agents/) uses broker-based choreography where agents are fully decoupled — no agent knows who produces its input or consumes its output.

---

## 7. Dead Letter and Retry

### Pattern: Failed Event Handling

```text
Event processing fails:
1. Increment attempt count
2. If attempts < max_attempts:
   a. Apply exponential backoff (base: 1s, max: 60s)
   b. Re-queue with incremented attempt
3. If attempts >= max_attempts:
   a. Move to Dead Letter Queue (DLQ)
   b. Alert on DLQ depth > threshold
   c. Log full event envelope for debugging
```

### Configuration

```yaml
retry_policy:
  max_attempts: 3
  backoff:
    type: "exponential"
    base_ms: 1000
    max_ms: 60000
    jitter: true
  dead_letter:
    queue: "inbox_dlq"
    retention_days: 14
    alert_threshold: 10  # alert if DLQ > 10 events
```

---

## 8. Observability

### Metrics to Track

| Metric | Type | Alert Threshold |
|--------|------|----------------|
| `inbox.events.received` | Counter | — |
| `inbox.events.classified` | Counter (by class) | — |
| `inbox.events.duplicates_discarded` | Counter | >50% of total |
| `inbox.events.routed` | Counter (by target) | — |
| `inbox.events.sla_breached` | Counter | Any >0 for critical |
| `inbox.queue.depth` | Gauge (by queue) | >1000 |
| `inbox.classification.latency_ms` | Histogram | p99 >500ms |
| `inbox.dlq.depth` | Gauge | >10 |

### Trace Span

```yaml
span:
  name: "inbox.process_event"
  attributes:
    event.id: "..."
    event.source_type: "webhook"
    event.signal_class: "actionable"
    event.priority: "high"
    event.queue: "fast"
    event.routing_target: "action_graph"
```

---

## Implementation Checklist

- [ ] Define event envelope schema for all source types.
- [ ] Implement source monitors (start with 1-2, expand).
- [ ] Build classification pipeline (rules first, add LLM fallback later).
- [ ] Add content-hash deduplication with sliding window.
- [ ] Set up priority queues (start with in-memory, graduate to Redis/SQS).
- [ ] Create routing table mapping events → Action Graph workflows.
- [ ] Implement retry + dead letter queue.
- [ ] Add OpenTelemetry metrics and trace spans.
- [ ] Set SLA alerts for critical and high-priority queues.
- [ ] Load test with 10× expected throughput.

---

## 9. Commercial Reference Implementations (March 2026)

The Inbox Engine is the **least commercially addressed** layer in the AI Engine stack. Most agent products start at "agent receives query" — they don't formalize how signals enter the system. Two notable exceptions:

### Confluent — Real-Time Context Engine

Confluent repositioned Kafka + Flink as a real-time context engine for AI agents:

| Component | Maps to Our Pattern |
|-----------|-------------------|
| Kafka streams (source intake) | Source Monitors (Section 1) |
| Flink processing (normalize, classify) | Classification + Deduplication (Sections 3-4) |
| In-memory cache (serving layer) | Priority Queue (Section 5) |
| MCP server (agent delivery) | Routing / Handoff Contract (Section 6) |
| Streaming Agents (Flink jobs) | Choreography pattern — agents run as pipeline stages |

**Key innovation**: First major platform to use MCP as native context delivery protocol. Q1 2026: Added A2A integration for cross-platform agent collaboration.

**Validates our patterns**: Event-driven intake with MCP-based delivery — exactly what our Inbox Engine + Data Agent layers document.

### Knative Eventing — Broker-Based Choreography

Knative's eventing model uses broker-based choreography where agents are fully decoupled — no agent knows who produces its input or consumes its output. This validates our Choreography Pattern (Section 6) as the scaling approach for 5+ agents.

### Market Gap

The Inbox Engine remains a genuine architectural gap in the market. While Confluent addresses streaming intake and Knative addresses event routing, no dedicated product offers the full pipeline our architecture defines: ingest → classify → deduplicate → prioritize → route with SLA enforcement. This is an opportunity for our composable approach.

---

## Related Resources

| Resource | Covers |
|----------|--------|
| [`ai-engine-layers.md`](ai-engine-layers.md) | Full 5-layer architecture overview |
| [`operational-patterns.md`](operational-patterns.md) | Action loop patterns (what inbox routes to) |
| [`multi-agent-patterns.md`](multi-agent-patterns.md) | Multi-agent orchestration and handoffs |
| [`a2a-handoff-patterns.md`](a2a-handoff-patterns.md) | Agent-to-agent communication protocol |
| [`../../../software-architecture-design/references/event-driven-architecture.md`](../../../software-architecture-design/references/event-driven-architecture.md) | Event-driven design patterns |
