# AI Engine Layers — Unified Agent Architecture

**Purpose**: Define the five-layer AI Engine architecture as a composition model for production agent systems. Maps each layer to existing skill references and provides implementation checklists.

---

## Architecture Overview

```text
┌─────────────────────────────────────────────────────────┐
│                     INBOX ENGINE                        │
│  (event intake → triage → routing)                      │
├──────────────────────┬──────────────────────────────────┤
│     ACTION GRAPH     │        CONTEXT GRAPH             │
│  (plan → act →       │   (entities, relationships,      │
│   observe → update)  │    reasoning traces)             │
├──────────────────────┴──────────────────────────────────┤
│                     DATA AGENT                          │
│  (retrieve → transform → index → refresh)               │
├─────────────────────────────────────────────────────────┤
│                   KNOWLEDGE BASE                        │
│  (vector store + knowledge graph + document index)      │
└─────────────────────────────────────────────────────────┘
```

**Data flow**: Inbox Engine receives signals → routes to Action Graph → Action Graph queries Context Graph for state → Context Graph pulls from Knowledge Base via Data Agent → results flow back up.

---

## 1. Context Graph

**What**: Structured representation of entities, relationships, and reasoning traces the agent uses for decision-making.

**Core function**: Maintain a queryable graph of everything the agent "knows" during a task — who, what, when, how they relate, and what has been inferred.

### Schema

```yaml
context_graph:
  nodes:
    - id: "entity-001"
      type: "user | document | tool | concept | event"
      properties:
        name: "..."
        source: "retrieval | inference | user_input"
        confidence: 0.95
        created_at: "2026-01-01T00:00:00Z"
        ttl: 3600
  edges:
    - source: "entity-001"
      target: "entity-002"
      relation: "authored_by | depends_on | contradicts | supports"
      weight: 0.9
      provenance: "rag_retrieval"
  traces:
    - step: 1
      action: "retrieve"
      reasoning: "User asked about X, retrieving related documents"
      context_delta: ["entity-003 added"]
```

### When to Use

| Scenario | Context Graph Approach |
|----------|----------------------|
| Multi-turn conversation | Track entity mentions across turns, link co-references |
| Multi-step reasoning | Log reasoning trace as edges between intermediate conclusions |
| Tool result integration | Add tool outputs as nodes, link to triggering query |
| Contradiction detection | Query graph for conflicting edges on same entity pair |

### Implementation Tiers

| Tier | Storage | Best For |
|------|---------|----------|
| **Lightweight** | In-memory dict/map | Single-session, <100 entities |
| **Mid-scale** | Redis + JSON graph | Multi-session, <10K entities |
| **Production** | Neo4j / FalkorDB / Amazon Neptune | Cross-agent, persistent, >10K entities |

**Existing depth**: [`context-engineering.md`](context-engineering.md) — progressive disclosure, session management, memory provenance, retrieval timing.

**New patterns**: [`context-graph-patterns.md`](context-graph-patterns.md) — node/edge schema, traversal, graph-augmented retrieval, memory tiers.

---

## 2. Action Graph

**What**: DAG or FSM of agent operations — plan, act, observe, update — with tool orchestration and state transitions.

**Core function**: Define the execution topology of an agent: which actions happen, in what order, with what branching conditions, and how state flows between them.

### Schema

```yaml
action_graph:
  id: "workflow-001"
  type: "dag | fsm | hybrid"
  nodes:
    - id: "step-plan"
      action: "plan"
      inputs: ["user_query", "context_snapshot"]
      outputs: ["execution_plan"]
      max_retries: 0
    - id: "step-retrieve"
      action: "tool_call"
      tool: "mcp://knowledge-base/search"
      inputs: ["execution_plan.queries"]
      outputs: ["retrieved_documents"]
      max_retries: 2
      timeout_ms: 5000
    - id: "step-synthesize"
      action: "llm_call"
      inputs: ["retrieved_documents", "user_query"]
      outputs: ["response_draft"]
  edges:
    - from: "step-plan"
      to: "step-retrieve"
      condition: "plan.requires_retrieval == true"
    - from: "step-retrieve"
      to: "step-synthesize"
      condition: "always"
  guards:
    max_steps: 10
    max_tokens: 50000
    timeout_ms: 30000
```

### State Transitions

```text
IDLE → PLANNING → EXECUTING → OBSERVING → UPDATING → COMPLETE
                      │                        │
                      ├── ERROR ──→ RETRYING ──┘
                      └── BLOCKED → HUMAN_REVIEW
```

### Integration with MCP/A2A

| Protocol | Action Graph Role |
|----------|------------------|
| **MCP** | Tool nodes call MCP servers; tool schemas define inputs/outputs |
| **A2A** | Handoff edges delegate sub-DAGs to other agents |

**Existing depth**: [`operational-patterns.md`](operational-patterns.md) — PLAN→ACT→OBSERVE→UPDATE loop, tool specification, multi-agent workflow. [`agent-operations-best-practices.md`](agent-operations-best-practices.md) — action loops, planning, execution patterns.

---

## 3. Data Agent

**What**: Autonomous retrieval and transformation agent that connects to data sources, indexes content, and manages freshness.

**Core function**: Act as the bridge between raw data sources and the Knowledge Base — fetch, clean, chunk, embed, index, and keep content fresh.

### Pipeline

```text
SOURCE MONITOR → FETCH → TRANSFORM → CHUNK → EMBED → INDEX → VALIDATE
       │                                                         │
       └─────── REFRESH (TTL / webhook / schedule) ──────────────┘
```

### Source Types

| Source | Connector | Refresh Strategy |
|--------|-----------|-----------------|
| REST API | HTTP polling / webhook | Event-driven or cron |
| Database | CDC (Change Data Capture) | Real-time stream |
| Documents | File watcher / S3 events | On-change |
| Web pages | Crawler / scraper | Scheduled |
| Streams | Kafka / Pub/Sub consumer | Continuous |

### Freshness Management

```yaml
freshness_policy:
  default_ttl: 86400          # 24 hours
  source_overrides:
    pricing_api: 3600          # 1 hour
    legal_docs: 604800         # 7 days
    user_profiles: 300         # 5 minutes
  invalidation_triggers:
    - webhook_received
    - source_schema_changed
    - confidence_below_threshold
  re_index_strategy: "incremental"  # full | incremental | differential
```

**Existing depth**: [`../ai-rag/SKILL.md`](../../ai-rag/SKILL.md) — chunking strategies, embedding models, reranking, hybrid search. [`rag-patterns.md`](rag-patterns.md) — retrieval patterns, agentic RAG.

---

## 4. Knowledge Base

**What**: Persistent semantic memory combining vector store, knowledge graph, and document index with provenance tracking.

**Core function**: Serve as the agent's long-term memory — store everything the agent might need to recall, with lineage metadata for trust and freshness.

### Unified Schema

```yaml
knowledge_base:
  vector_store:
    provider: "pinecone | qdrant | pgvector | chroma"
    embedding_model: "text-embedding-3-large"
    dimensions: 3072
    distance_metric: "cosine"
  knowledge_graph:
    provider: "neo4j | falkordb | amazon_neptune"
    schema:
      entity_types: ["person", "org", "concept", "document", "event"]
      relation_types: ["authored", "references", "contradicts", "supersedes"]
  document_index:
    provider: "elasticsearch | typesense | meilisearch"
    fields: ["title", "content", "source", "date", "tags"]
  provenance:
    required_fields: ["source_url", "ingested_at", "confidence", "lineage_id"]
    retention_days: 365
```

### Access Patterns

| Query Type | Layer Used | Example |
|-----------|-----------|---------|
| Semantic similarity | Vector store | "Find docs about agent memory patterns" |
| Entity relationships | Knowledge graph | "What tools does agent-X use?" |
| Keyword / filter | Document index | "All docs from source=arxiv after 2025" |
| Hybrid | Vector + graph + filter | "Recent papers about X by author Y" |

**Existing depth**: [`memory-systems.md`](memory-systems.md) — four-memory model, retrieval patterns, write patterns, consolidation.

**New patterns**: [`../assets/knowledge-base/kb-architecture.md`](../assets/knowledge-base/kb-architecture.md) — unified KB schema, provenance, freshness, multi-tenant access control.

---

## 5. Inbox Engine

**What**: Event-driven intake layer that monitors sources, triages incoming signals, and routes to appropriate agents or workflows.

**Core function**: Act as the front door — everything that enters the agent system passes through the Inbox Engine for classification, deduplication, prioritization, and routing.

### Pipeline

```text
SOURCES → INGEST → CLASSIFY → DEDUPLICATE → PRIORITIZE → ROUTE
   │                                                        │
   │   ┌── actionable ──→ Action Graph                     │
   │   ├── informational → Knowledge Base (via Data Agent)  │
   │   └── noise ────────→ Log + discard                   │
   └────────── ACKNOWLEDGE / NACK ──────────────────────────┘
```

### Signal Classification

```yaml
signal_classes:
  actionable:
    description: "Requires agent action within SLA"
    examples: ["user request", "alert threshold breach", "approval needed"]
    routing: "action_graph"
  informational:
    description: "Updates knowledge, no immediate action"
    examples: ["data refresh", "status update", "new document published"]
    routing: "data_agent → knowledge_base"
  noise:
    description: "Irrelevant or duplicate, safe to discard"
    examples: ["heartbeat", "duplicate webhook", "stale notification"]
    routing: "log_and_discard"
```

### Routing Rules

| Trigger | Route To | SLA |
|---------|----------|-----|
| User message | Action Graph (conversational agent) | <2s |
| Webhook event | Action Graph (event handler) | <30s |
| Scheduled job | Data Agent (refresh pipeline) | best-effort |
| Agent handoff (A2A) | Action Graph (delegated task) | inherited |
| System alert | Action Graph (incident handler) | <5s |

**Existing depth**: [`multi-agent-patterns.md`](multi-agent-patterns.md) — orchestration, handoffs, group chat routing. [`a2a-handoff-patterns.md`](a2a-handoff-patterns.md) — agent-to-agent communication.

**New patterns**: [`inbox-engine-patterns.md`](inbox-engine-patterns.md) — event-driven intake, signal classification, priority routing, deduplication.

---

## Layer Interaction Matrix

| From ↓ / To → | Context Graph | Action Graph | Data Agent | Knowledge Base | Inbox Engine |
|---------------|:---:|:---:|:---:|:---:|:---:|
| **Context Graph** | — | state queries | — | graph queries | — |
| **Action Graph** | read/write state | — | trigger refresh | query KB | — |
| **Data Agent** | — | status updates | — | write index | — |
| **Knowledge Base** | serve entities | serve results | receive writes | — | — |
| **Inbox Engine** | — | route tasks | route data | — | — |

---

## Commercial Landscape (March 2026)

"Context engine" has crystallized as a recognized infrastructure category — the layer between raw data and AI agents that assembles, maintains, and serves the right context at the right time.

### Market Tiers

| Tier | Products | What They Solve |
|------|----------|-----------------|
| **Dedicated Context Platforms** | Zep/Graphiti, Mem0, Cognee, Letta | Pure-play context engineering: memory, knowledge graphs, stateful agents |
| **Enterprise Context Platforms** | Glean, Tabnine, AWS Bedrock AgentCore | Full-stack AI platforms with built-in context engines |
| **Infrastructure Context Engines** | Confluent, Materialize, Redis | Data infrastructure repositioned as context layer for AI |
| **Agent Frameworks** | LangGraph, Composio, Arcade | Orchestration frameworks with built-in context management |

### Layer-to-Product Alignment

| Our Layer | Closest Commercial Analog | Match |
|-----------|--------------------------|:-----:|
| **Context Graph** | Zep/Graphiti (temporal KG), Glean (enterprise KG) | Strong |
| **Action Graph** | LangGraph (state machine), Letta (stateful runtime) | Strong |
| **Data Agent** | Composio/Arcade (connectors), Confluent (streaming), Materialize (live data) | Strong |
| **Knowledge Base** | Mem0 (memory layer), Redis (in-memory), Pinecone (vector), Tabnine (code-specific) | Strong |
| **Inbox Engine** | Confluent (event-driven intake) | Medium — fewest pure-play products |

### Industry Standards

The Linux Foundation formed the **Agentic AI Foundation (AAIF)** with founding contributions from Anthropic (MCP), Block (goose), and OpenAI (AGENTS.md). MCP is the consensus protocol for agent-to-tool connectivity — adopted natively by Confluent, Pinecone, Merge, and others.

### What We Have That Others Don't

1. **Unified 5-layer taxonomy** — no single commercial product covers all five layers as a named, composable architecture. Zep comes closest (3/5) but lacks Inbox Engine and Action Graph formalization.
2. **Composability** — our architecture is provider-agnostic with pluggable drivers. Commercial products are typically locked to their implementation.
3. **Inbox Engine as first-class layer** — most products start at "agent receives query." Confluent is the only major player with explicit event-driven intake.

### What to Watch

| Pattern | Source | Status in Our Architecture |
|---------|--------|---------------------------|
| Bi-temporal knowledge graph | Zep/Graphiti | Added — see [`context-graph-patterns.md`](context-graph-patterns.md) |
| MCP as KB access protocol | Confluent, Pinecone, industry | Added — see [`../assets/knowledge-base/kb-architecture.md`](../assets/knowledge-base/kb-architecture.md) |
| Choreography pattern | Knative, Confluent | Added — see [`inbox-engine-patterns.md`](inbox-engine-patterns.md) |
| Per-layer evaluation benchmarks | Zep (DMR benchmark), Mem0 (accuracy lift) | Not yet covered |
| Edge/on-device deployment | Cognee (Rust engine) | Not yet covered |
| Git-based memory versioning | Letta Context Repositories (Feb 2026) | Not yet covered |

---

## Implementation Checklist

### Phase 1: Foundation (Week 1-2)

- [ ] Define Knowledge Base schema (vector store + document index)
- [ ] Implement Data Agent pipeline (fetch → chunk → embed → index)
- [ ] Set up basic Context Graph (in-memory, single-session)
- [ ] Build Action Graph for primary workflow (FSM or DAG)

### Phase 2: Integration (Week 3-4)

- [ ] Connect Action Graph → Knowledge Base (query path)
- [ ] Connect Data Agent → Knowledge Base (write path)
- [ ] Add Context Graph persistence (cross-session state)
- [ ] Implement basic Inbox Engine (single source, classification)

### Phase 3: Production (Week 5-6)

- [ ] Add Inbox Engine multi-source intake + deduplication
- [ ] Implement Context Graph → Knowledge Graph synchronization
- [ ] Add freshness management (TTL, invalidation, re-indexing)
- [ ] Deploy observability (OpenTelemetry traces per layer)
- [ ] Run safety checklist per [`assets/checklists/agent-safety-checklist.md`](../assets/checklists/agent-safety-checklist.md)

---

## Related Resources

| Resource | Covers |
|----------|--------|
| [`context-engineering.md`](context-engineering.md) | Progressive disclosure, session management, provenance |
| [`context-graph-patterns.md`](context-graph-patterns.md) | Node/edge schema, traversal, graph-RAG |
| [`operational-patterns.md`](operational-patterns.md) | PLAN→ACT→OBSERVE→UPDATE, tool specs |
| [`memory-systems.md`](memory-systems.md) | Four-memory model, retrieval, consolidation |
| [`rag-patterns.md`](rag-patterns.md) | Retrieval pipelines, hybrid search, agentic RAG |
| [`multi-agent-patterns.md`](multi-agent-patterns.md) | Orchestration, handoffs, group chat |
| [`inbox-engine-patterns.md`](inbox-engine-patterns.md) | Event intake, triage, routing |
| [`../assets/knowledge-base/kb-architecture.md`](../assets/knowledge-base/kb-architecture.md) | Unified KB schema, provenance, freshness |
