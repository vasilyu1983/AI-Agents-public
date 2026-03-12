# Knowledge Base Architecture — Unified Agent Memory

**Purpose**: Architecture template for building a unified Knowledge Base that combines vector store, knowledge graph, and document index with provenance tracking. This is the persistent semantic memory layer for agent systems.

---

## 1. Unified KB Schema

### Pattern: Three-Store Architecture

```text
┌─────────────────────────────────────────────────┐
│                 QUERY INTERFACE                   │
│  semantic search | entity lookup | keyword filter │
├────────────┬──────────────┬─────────────────────┤
│  VECTOR    │  KNOWLEDGE   │   DOCUMENT          │
│  STORE     │  GRAPH       │   INDEX             │
│  (embeddings│ (entities,  │  (full-text,        │
│   + cosine) │  relations) │   filters, facets)  │
├────────────┴──────────────┴─────────────────────┤
│              PROVENANCE LAYER                    │
│  source | timestamp | confidence | lineage       │
├─────────────────────────────────────────────────┤
│              STORAGE ENGINE                      │
│  (provider-specific: Pinecone, Neo4j, ES, etc.) │
└─────────────────────────────────────────────────┘
```

### Schema Definition

```yaml
knowledge_base:
  # Layer 1: Vector Store — semantic similarity search
  vector_store:
    provider: "pinecone | qdrant | pgvector | chroma | weaviate"
    config:
      embedding_model: "text-embedding-3-large"
      dimensions: 3072
      distance_metric: "cosine"  # cosine | euclidean | dot_product
      index_type: "hnsw"
      namespace_strategy: "per_source"  # per_source | per_domain | single
    record_schema:
      id: "string (deterministic hash of content + source)"
      embedding: "float[3072]"
      text: "string (original chunk text)"
      metadata:
        source_url: "string"
        source_type: "api | document | web | database"
        domain: "string"
        ingested_at: "ISO 8601"
        chunk_index: "int"
        parent_doc_id: "string"

  # Layer 2: Knowledge Graph — entity relationships
  knowledge_graph:
    provider: "neo4j | falkordb | amazon_neptune | memgraph"
    config:
      persistence: "disk"
      consistency: "eventual"  # strong | eventual
    schema:
      entity_types:
        - "person"
        - "organization"
        - "concept"
        - "document"
        - "event"
        - "tool"
        - "metric"
      relation_types:
        - "authored_by"
        - "belongs_to"
        - "references"
        - "contradicts"
        - "supersedes"
        - "depends_on"
        - "measured_by"
      entity_properties:
        - name: "string"
        - type: "enum (entity_types)"
        - source: "string"
        - confidence: "float"
        - created_at: "ISO 8601"
        - updated_at: "ISO 8601"

  # Layer 3: Document Index — keyword search + filtering
  document_index:
    provider: "elasticsearch | typesense | meilisearch | opensearch"
    config:
      analyzers: ["standard", "keyword"]
      shards: 1
      replicas: 0
    fields:
      - name: "title"
        type: "text"
        searchable: true
      - name: "content"
        type: "text"
        searchable: true
      - name: "source_url"
        type: "keyword"
        filterable: true
      - name: "domain"
        type: "keyword"
        filterable: true
      - name: "ingested_at"
        type: "date"
        sortable: true
      - name: "tags"
        type: "keyword[]"
        filterable: true
```

---

## 2. Provenance Tracking

### Pattern: Every Record Has Lineage

```yaml
provenance_record:
  lineage_id: "string (uuid — traces full lifecycle)"
  source:
    url: "string (where the data came from)"
    type: "api | document | web | database | user_input | inference"
    fetch_method: "crawl | webhook | poll | upload | A2A"
  timestamps:
    source_created_at: "ISO 8601 (when source published)"
    ingested_at: "ISO 8601 (when we fetched it)"
    last_validated_at: "ISO 8601 (when we last checked freshness)"
    expires_at: "ISO 8601 (TTL expiration)"
  quality:
    confidence: "float (0.0 - 1.0)"
    validation_method: "checksum | schema_match | llm_verify | human_review"
    error_rate: "float (historical accuracy of this source)"
  lineage:
    parent_doc_id: "string (if chunked from larger doc)"
    transformation: "string (chunked | summarized | translated | extracted)"
    pipeline_version: "string (which pipeline version produced this)"
```

### Checklist: Provenance Requirements

- [ ] Every record has a `lineage_id` that traces back to its origin.
- [ ] `source.url` is populated — never store data without knowing where it came from.
- [ ] `ingested_at` is set at write time — never backdate.
- [ ] `confidence` is set based on source type (user_input=1.0, inference=0.5-0.8).
- [ ] `expires_at` is set based on freshness policy (see Section 3).
- [ ] `transformation` records what happened to the data (chunked, summarized, etc.).

---

## 3. Freshness Management

### Pattern: TTL + Invalidation + Re-Index

```yaml
freshness_policy:
  # Default TTL by source type
  ttl_by_source:
    api_data: 3600           # 1 hour
    web_page: 86400          # 24 hours
    document: 604800         # 7 days
    user_input: 2592000      # 30 days
    reference_data: 7776000  # 90 days

  # Invalidation triggers (immediate re-fetch)
  invalidation_triggers:
    - webhook_received          # source pushes update
    - schema_change_detected    # source structure changed
    - confidence_below: 0.3     # quality degraded
    - contradiction_detected    # conflicting data found
    - user_reported_stale       # user flags outdated info

  # Re-indexing strategy
  re_index:
    strategy: "incremental"     # full | incremental | differential
    schedule: "0 2 * * *"       # daily at 2 AM
    priority_sources_first: true
    max_concurrent_fetches: 10
    backoff_on_failure:
      base_ms: 5000
      max_ms: 300000
      max_retries: 3
```

### Freshness Check Pattern

```text
Before serving a KB result:
1. Check expires_at against current time
2. If expired:
   a. Return stale result with staleness warning
   b. Trigger background re-fetch
   c. Mark record as "stale_pending_refresh"
3. If not expired:
   a. Return result normally
4. After re-fetch:
   a. Compare new content hash with stored hash
   b. If changed: update record, bump ingested_at, recalculate embedding
   c. If unchanged: bump last_validated_at only
```

### Decision Tree: When to Invalidate

```text
What triggered the check?
├── Webhook received? → Invalidate immediately, re-fetch
├── Scheduled re-index? → Check content hash, update if changed
├── Query returned low confidence? → Flag for review, don't invalidate
├── Contradiction detected? → Invalidate both records, fetch fresh
└── User reported stale? → Invalidate, re-fetch, log user feedback
```

---

## 4. Access Control and Multi-Tenant Patterns

### Pattern: Namespace Isolation

```yaml
multi_tenant:
  isolation_strategy: "namespace"  # namespace | separate_index | row_level
  namespace_key: "tenant_id"

  # Vector store: separate namespace per tenant
  vector_store_namespaces:
    tenant_a: "ns-tenant-a"
    tenant_b: "ns-tenant-b"
    shared: "ns-shared"        # shared knowledge (docs, policies)

  # Knowledge graph: label-based isolation
  knowledge_graph_labels:
    tenant_a: "TenantA"
    tenant_b: "TenantB"
    shared: "Shared"

  # Document index: filter-based isolation
  document_index_filter:
    field: "tenant_id"
    enforce_on_every_query: true
```

### Access Control Matrix

| Role | Read Shared | Read Own Tenant | Write Own Tenant | Admin |
|------|:-----------:|:---------------:|:----------------:|:-----:|
| **Agent (tenant-scoped)** | Yes | Yes | Yes | No |
| **Agent (cross-tenant)** | Yes | All | No | No |
| **Data Agent** | Yes | All | All | No |
| **Admin** | Yes | All | All | Yes |

### Checklist: Multi-Tenant Safety

- [ ] Every query includes tenant_id filter — never return cross-tenant data by accident.
- [ ] Shared namespace is read-only for tenant-scoped agents.
- [ ] Data Agent writes enforce tenant_id on every record.
- [ ] Audit log tracks all cross-tenant queries.
- [ ] PII is encrypted at rest and tenant-scoped encryption keys are isolated.

---

## 5. Integration with Data Agent

### Pattern: Data Agent → KB Write Pipeline

```text
Data Agent output → KB write path:

1. RECEIVE transformed data from Data Agent
2. VALIDATE against KB schema (reject malformed)
3. EMBED text fields using configured model
4. CHECK for existing record (same source + content hash)
   ├── New record → INSERT across all three stores
   └── Updated record → UPSERT (vector + doc index), UPDATE (graph)
5. SET provenance metadata (lineage_id, ingested_at, confidence)
6. CONFIRM write success, return record IDs
```

### Write Consistency

| Store | Write Order | Rollback Strategy |
|-------|-------------|-------------------|
| Vector store | First (embedding is expensive, do once) | Delete embedding on downstream failure |
| Document index | Second (fast, keyword index) | Delete document on graph failure |
| Knowledge graph | Third (entity + relation extraction) | Soft-delete (mark as pending) |

```yaml
write_transaction:
  strategy: "best_effort_ordered"  # not ACID across stores
  order: ["vector_store", "document_index", "knowledge_graph"]
  on_partial_failure:
    rollback_completed_writes: true
    retry_failed_store: true
    max_retries: 2
    alert_on_inconsistency: true
```

---

## 6. Access Protocol: MCP

Agents access the Knowledge Base through **Model Context Protocol (MCP)** — the standard interface for agent-to-data connectivity (the "USB-C for AI").

### Pattern: MCP-First KB Access

```yaml
kb_mcp_server:
  name: "knowledge-base"
  transport: "stdio | sse | streamable-http"
  tools:
    - name: "kb_semantic_search"
      description: "Search KB by semantic similarity"
      input_schema:
        query: "string"
        top_k: "int (default: 10)"
        namespace: "string (optional, for multi-tenant)"
        filters: "object (optional, date/source/domain)"
      output: "array of {text, score, provenance}"

    - name: "kb_entity_lookup"
      description: "Look up entity and relationships in knowledge graph"
      input_schema:
        entity: "string (name or ID)"
        max_hops: "int (default: 2)"
      output: "entity node + edges + neighbor nodes"

    - name: "kb_keyword_search"
      description: "Keyword search with filters and facets"
      input_schema:
        terms: "string"
        filters: "object (date, source, tags)"
      output: "array of {title, content_snippet, highlights, provenance}"

    - name: "kb_hybrid_search"
      description: "Combined semantic + keyword + entity enrichment"
      input_schema:
        query: "string"
        filters: "object (optional)"
      output: "array of {text, score, entities, provenance}"
```

**Why MCP over direct DB access**: Agents should never connect directly to vector stores or graph databases. MCP provides tool-level abstraction with schema validation, rate limiting, access control, and audit logging — all enforced at the protocol layer rather than relying on each agent to implement correctly.

### Pluggable Driver Architecture

Use a database-agnostic core with swappable backend drivers. This prevents vendor lock-in and enables per-environment configuration (e.g., Chroma for dev, Pinecone for production).

```yaml
driver_abstraction:
  interface_operations:
    - "upsert_record"
    - "delete_record"
    - "search_semantic"
    - "search_keyword"
    - "get_entity"
    - "traverse_graph"
    - "batch_write"
  drivers:
    pinecone:
      vector_store: true
      config: { api_key: "${PINECONE_API_KEY}", index: "kb-prod" }
    neo4j:
      knowledge_graph: true
      config: { uri: "${NEO4J_URI}", auth: "${NEO4J_AUTH}" }
    typesense:
      document_index: true
      config: { host: "${TYPESENSE_HOST}", api_key: "${TYPESENSE_API_KEY}" }
```

**Reference**: [Graphiti](https://github.com/getzep/graphiti) implements this pattern with 11 operation abstractions across Neo4j, FalkorDB, Kuzu, and Neptune drivers.

---

## 7. Query Patterns

### Pattern: Unified Query Interface

```yaml
query_interface:
  # Semantic search (vector store)
  semantic:
    input: "natural language query"
    method: "embed_query → cosine_similarity → top_k"
    returns: "ranked documents with scores"

  # Entity lookup (knowledge graph)
  entity:
    input: "entity_id or entity_name + type"
    method: "graph traversal (BFS, max 2 hops)"
    returns: "entity + relationships + neighbors"

  # Keyword/filter (document index)
  keyword:
    input: "search terms + filters (date, source, tags)"
    method: "full-text search + faceted filter"
    returns: "matching documents with highlights"

  # Hybrid (all three)
  hybrid:
    input: "natural language + optional filters"
    method: |
      1. Semantic search → top 20
      2. Keyword search → top 20
      3. Entity enrichment → add related entities
      4. Reciprocal rank fusion → merged top 10
    returns: "enriched results with provenance"
```

### Decision Tree: Which Query?

```text
What does the agent need?
├── "Find similar content" → Semantic search
├── "What is entity X?" → Entity lookup
├── "All docs matching [filter]" → Keyword/filter
├── "Answer question about X" → Hybrid (semantic + entity enrichment)
└── "Cross-reference X and Y" → Entity lookup → Semantic on results
```

---

## Implementation Checklist

### Phase 1: Single Store (MVP)

- [ ] Choose primary vector store (Pinecone, Qdrant, or pgvector).
- [ ] Define record schema with provenance fields.
- [ ] Implement embed → upsert → query pipeline.
- [ ] Add TTL-based freshness checks.
- [ ] Connect Data Agent write path.

### Phase 2: Add Document Index

- [ ] Add Typesense/Meilisearch for keyword search.
- [ ] Implement hybrid query (semantic + keyword with RRF).
- [ ] Add filter/facet support (source, date, domain).
- [ ] Sync document index with vector store on writes.

### Phase 3: Add Knowledge Graph

- [ ] Add Neo4j/FalkorDB for entity relationships.
- [ ] Implement entity extraction on ingest (NER or LLM).
- [ ] Build graph-augmented retrieval pipeline.
- [ ] Add contradiction detection across stores.

### Phase 4: Production Hardening

- [ ] Implement multi-tenant namespace isolation.
- [ ] Add write consistency with ordered rollback.
- [ ] Deploy freshness management (TTL + invalidation + re-index).
- [ ] Add OpenTelemetry metrics (query latency, index size, freshness).
- [ ] Load test with 10× expected query volume.

---

## Commercial Reference Implementations (March 2026)

Products that validate and extend our three-store KB architecture:

### Memory Layer Platforms

| Product | Architecture | Key Metric | Best For |
|---------|-------------|------------|----------|
| **Mem0** | Hierarchical memory (user, session, agent) + vector search + optional graph | 26% accuracy boost. $24M funded. AWS exclusive memory provider for their Agent SDK. | Universal memory across any model/framework |
| **Redis Agent Memory Server** | In-memory vector library + hybrid search (vector + full-text + attribute) | Sub-millisecond retrieval. Open-source Agent Memory Server. | High-speed context serving, mid-scale tier |

**Maps to our architecture**: Mem0 covers our Knowledge Base + Context Graph layers with a single-API opinionated approach. Redis is a strong implementation choice for our mid-scale KB tier (Section 1 provider options).

### Enterprise KB Platforms

| Product | Architecture | Key Metric | Best For |
|---------|-------------|------------|----------|
| **Glean** | 100+ connectors → unified index → knowledge graph → personalized AI | Results preferred 1.9× over ChatGPT on enterprise queries (blind evaluation, 280 queries) | Enterprise-scale unified knowledge |
| **AWS Bedrock Knowledge Bases** | Managed RAG with vector store + embedding + retrieval, integrated with AgentCore memory layers | Three context layers: long-term memory + short-term session + knowledge base | Managed KB with agent infrastructure |
| **Tabnine Enterprise Context Engine** | Vector + graph + agentic retrieval from code, docs, APIs, infrastructure | 82% lift in code consumption rates vs out-of-the-box LLM. GA February 2026. | Code-specific organizational context |

**Pattern validated**: Tabnine's vector + graph + agentic retrieval confirms our three-store architecture (vector store + knowledge graph + document index) as the production pattern for enterprise KB.

### Vector/Search Infrastructure

| Product | Relevance to Our Architecture |
|---------|------------------------------|
| **Pinecone** | Managed vector store with MCP server and Context API. Fits our vector_store provider slot. |
| **Qdrant** | Open-source vector DB with rich filtering. Alternative vector_store provider. |
| **Typesense / Meilisearch** | Fast keyword search with facets. Fits our document_index provider slot. |

### Key Industry Patterns

1. **MCP as KB access protocol** — Pinecone, Confluent, and others ship native MCP servers. Our MCP-First KB Access pattern (Section 6) is aligned with industry direction.
2. **Driver abstraction** — Graphiti's 11-operation abstraction across Neo4j, FalkorDB, Kuzu, and Neptune validates our Pluggable Driver Architecture (Section 6).
3. **Freshness as non-negotiable** — Materialize identifies three context engine requirements: freshness (current reality, not snapshots), correctness (no partial/stale state), composability (derived views stack without gaps). Our TTL + invalidation + re-index pattern (Section 3) addresses all three.

---

## Related Resources

| Resource | Covers |
|----------|--------|
| [`../references/ai-engine-layers.md`](../references/ai-engine-layers.md) | Full 5-layer architecture overview |
| [`../references/memory-systems.md`](../references/memory-systems.md) | Four-memory model, retrieval patterns |
| [`../references/rag-patterns.md`](../references/rag-patterns.md) | Retrieval pipelines, hybrid search |
| [`../references/context-graph-patterns.md`](../references/context-graph-patterns.md) | Graph-augmented retrieval |
| [`../../ai-rag/SKILL.md`](../../ai-rag/SKILL.md) | Chunking, embedding, reranking depth |
