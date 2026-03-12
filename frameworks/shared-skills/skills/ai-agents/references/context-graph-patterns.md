# Context Graph Patterns — Structured Agent State

**Purpose**: Operational patterns for building, querying, and maintaining context graphs in agent systems. A context graph is the agent's structured working memory — entities, relationships, and reasoning traces that inform decisions.

---

## 1. Node/Edge Schema

### Pattern: Typed Entity Graph

```yaml
node_schema:
  id: "string (uuid)"
  type: "entity | concept | tool_result | inference | user_input"
  label: "string (human-readable)"
  properties:
    source: "retrieval | inference | user_input | tool_call"
    confidence: "float (0.0 - 1.0)"
    created_at: "ISO 8601"
    updated_at: "ISO 8601"
    event_time: "ISO 8601 (when the fact actually occurred)"
    ingestion_time: "ISO 8601 (when we recorded it)"
    ttl: "int (seconds, 0 = permanent)"
    embedding: "float[] (optional, for similarity search)"

edge_schema:
  source_id: "string"
  target_id: "string"
  relation: "string (from relation_types)"
  weight: "float (0.0 - 1.0)"
  provenance: "string (how this relation was established)"
  created_at: "ISO 8601"
  valid_from: "ISO 8601 (when this relation became true)"
  valid_until: "ISO 8601 | null (when this relation was invalidated)"
```

### Relation Types

| Relation | Meaning | Example |
|----------|---------|---------|
| `depends_on` | Target is prerequisite for source | step-2 depends_on step-1 |
| `authored_by` | Source was created by target | document authored_by user |
| `references` | Source cites or links to target | answer references doc-X |
| `contradicts` | Source conflicts with target | fact-A contradicts fact-B |
| `supports` | Source provides evidence for target | evidence supports claim |
| `supersedes` | Source replaces target (newer version) | doc-v2 supersedes doc-v1 |
| `co_occurs` | Source and target appear together | entity-A co_occurs entity-B |
| `inferred_from` | Source was derived from target | conclusion inferred_from premise |

### Bi-Temporal Model

Track two distinct timestamps on every node to enable point-in-time queries ("what did the agent know at time T?"):

| Timestamp | Records | Example |
|-----------|---------|---------|
| `event_time` | When the fact actually occurred in the real world | "User changed preference on Jan 5" |
| `ingestion_time` | When the agent learned about the fact | "Agent ingested this on Jan 7" |

**Why this matters**: An agent reviewing a past decision needs to know what information was *available* at that point, not what exists now. Bi-temporal queries like "show me the context graph as of Jan 6" return nodes with `ingestion_time <= Jan 6`, which excludes the Jan 7 ingestion — accurately reflecting the agent's state at decision time.

Edges use `valid_from` / `valid_until` to track when relationships were active, enabling temporal graph traversals (e.g., "who was the account owner in Q3?" vs. "who is the account owner now?").

**Reference**: [Graphiti](https://github.com/getzep/graphiti) by Zep popularized this pattern for production agent knowledge graphs.

### Checklist: Node Creation

- [ ] Assign unique ID (UUID v4 or deterministic hash).
- [ ] Set type from allowed enum — never use freeform strings.
- [ ] Record source provenance (where did this node come from?).
- [ ] Set confidence score (1.0 for user input, lower for inference).
- [ ] Set `event_time` (when the fact occurred) and `ingestion_time` (when we recorded it).
- [ ] Set TTL based on volatility (user prefs = long, search results = short).
- [ ] Generate embedding if node will participate in similarity queries.

---

## 2. Traversal Patterns

### Pattern: Breadth-First Context Expansion

```text
Given: query node Q
1. Retrieve direct neighbors of Q (depth 1)
2. Score neighbors by edge weight × node confidence
3. If insufficient context: expand to depth 2 (neighbors of neighbors)
4. Filter by relevance threshold (> 0.5)
5. Return ranked context set
```

**When to use**: Exploratory queries where the agent needs to discover related context.

### Pattern: Multi-Hop Reasoning Chain

```text
Given: start node S, target node T
1. Find all paths from S to T (max depth: 4)
2. Score each path: product of edge weights along path
3. Select top-K paths by score
4. Extract reasoning chain: S → relation → intermediate → relation → T
5. Present chain as evidence for the S–T relationship
```

**When to use**: Answering "how does X relate to Y?" or building justification chains.

### Pattern: Subgraph Extraction

```text
Given: task context C (set of relevant node IDs)
1. Extract induced subgraph over C
2. Add 1-hop neighbors with edge weight > 0.7
3. Prune nodes with confidence < 0.3
4. Serialize subgraph to context window
```

**When to use**: Preparing a focused context snapshot for an LLM call.

### Decision Tree: Which Traversal?

```text
What does the agent need?
├── Discover related context? → Breadth-First Expansion
├── Explain a relationship? → Multi-Hop Reasoning Chain
├── Prepare LLM context? → Subgraph Extraction
└── Find contradictions? → Full-Graph Conflict Scan (see Section 5)
```

---

## 3. Graph-Augmented Retrieval (Graph-RAG)

### Pattern: Retrieve → Graph-Enrich → Generate

```text
1. RETRIEVE: Vector search for top-K documents
2. GRAPH-ENRICH:
   a. Extract entities from retrieved documents
   b. Query knowledge graph for entity relationships
   c. Add related entities not in original retrieval
3. GENERATE: Pass enriched context to LLM
```

### Schema: Graph-RAG Pipeline

```yaml
graph_rag:
  retrieval:
    method: "hybrid"  # vector + keyword
    top_k: 10
    reranker: "cross-encoder"
  enrichment:
    entity_extraction: "NER or LLM-based"
    graph_lookup:
      max_hops: 2
      min_edge_weight: 0.5
      max_additional_nodes: 20
    merge_strategy: "union_deduplicate"
  generation:
    context_format: "documents + entity_relationships"
    max_context_tokens: 8000
```

### When Graph-RAG Beats Plain RAG

| Scenario | Plain RAG | Graph-RAG |
|----------|-----------|-----------|
| Single-document answer | Sufficient | Overkill |
| Cross-document reasoning | Misses connections | Finds entity links |
| "How does X relate to Y?" | Poor | Strong |
| Temporal reasoning | Weak | Strong (date edges) |
| Contradictory sources | Picks one | Surfaces conflict |

**Existing depth**: [`../../../ai-rag/references/graph-rag-patterns.md`](../../../ai-rag/references/graph-rag-patterns.md) — full graph-RAG implementation patterns.

---

## 4. Memory Tiers

### Pattern: Three-Tier Memory Model

| Tier | Purpose | Storage | TTL | Context Graph Role |
|------|---------|---------|-----|-------------------|
| **Short-term** | Current conversation state | In-memory | Session duration | Active subgraph |
| **Episodic** | Past task outcomes and reasoning traces | Redis / DB | Days to weeks | Archived subgraph, rehydratable |
| **Semantic** | Stable knowledge and entity relationships | Knowledge graph | Months to permanent | Persistent graph partition |

### Lifecycle: Short-term → Episodic → Semantic

```text
During session:
  Context graph nodes are SHORT-TERM (in active subgraph)

At session end:
  1. Score each node: importance = confidence × usage_count × recency
  2. Nodes with importance > threshold → promote to EPISODIC
  3. Discard remaining short-term nodes

Periodic consolidation:
  1. Scan episodic nodes older than 7 days
  2. Nodes referenced by 3+ sessions → promote to SEMANTIC
  3. Merge duplicates (same entity, different sessions)
  4. Archive remaining episodic nodes beyond retention window
```

### Consolidation Rules

```yaml
consolidation:
  episodic_promotion:
    min_confidence: 0.7
    min_usage_count: 2
    recency_weight: 0.3
  semantic_promotion:
    min_session_references: 3
    min_age_days: 7
    merge_strategy: "keep_highest_confidence"
  cleanup:
    episodic_retention_days: 30
    orphan_node_removal: true  # nodes with no edges
```

**Existing depth**: [`memory-systems.md`](memory-systems.md) — four-memory model, write patterns, extraction, consolidation.

---

## 5. Conflict Detection and Resolution

### Pattern: Contradiction Scan

```text
For each entity E in the graph:
  1. Collect all edges where E is source or target
  2. Group edges by relation type
  3. For each group:
     - If "supports" and "contradicts" edges exist for same target → CONFLICT
     - If "supersedes" edge exists → mark older node as stale
  4. Flag conflicts for resolution
```

### Resolution Strategies

| Strategy | When to Use | Action |
|----------|-------------|--------|
| **Recency wins** | Time-sensitive facts | Keep newer node, archive older |
| **Confidence wins** | Uncertain sources | Keep higher-confidence node |
| **Source priority** | Mixed source quality | Rank: user_input > official_doc > inference |
| **Human review** | High-stakes decisions | Flag for human, block automation |

---

## 6. Implementation Options

### Lightweight (Single-Session)

```python
# In-memory graph using networkx
import networkx as nx

graph = nx.DiGraph()
graph.add_node("entity-1", type="concept", confidence=0.9, source="user_input")
graph.add_node("entity-2", type="document", confidence=0.8, source="retrieval")
graph.add_edge("entity-1", "entity-2", relation="references", weight=0.85)

# Breadth-first context expansion
neighbors = list(nx.bfs_edges(graph, "entity-1", depth_limit=2))
```

### Mid-Scale (Multi-Session, Redis)

```python
# Redis-backed graph with JSON serialization
# Use RedisGraph module or manual adjacency lists
# Supports TTL on nodes via Redis EXPIRE
```

### Production (Persistent Knowledge Graph)

```python
# Neo4j with Cypher queries
# MATCH (a:Entity)-[r:REFERENCES]->(b:Entity)
# WHERE a.confidence > 0.5
# RETURN a, r, b

# FalkorDB for Redis-compatible graph DB
# Amazon Neptune for managed cloud graph
```

### Decision Tree: Which Implementation?

```text
How many entities?
├── < 100, single session? → networkx (in-memory)
├── 100–10K, multi-session? → Redis + JSON graph
└── > 10K, cross-agent? → Neo4j / FalkorDB / Neptune
```

### Commercial Context Graph Options (March 2026)

| Product | Approach | Differentiator | Best For |
|---------|----------|---------------|----------|
| **Graphiti** (by Zep) | Bi-temporal knowledge graph, OSS | 11 operation abstractions, pluggable drivers (Neo4j, FalkorDB, Kuzu, Neptune). 94.8% on DMR benchmark. | Production agent KG with temporal queries |
| **Cognee** | KG from unstructured data, 6 lines of code | Transforms raw docs into structured memory. Rust engine for edge/on-device coming. €7.5M funded. | Regulated/knowledge-intensive domains |
| **Glean** | Enterprise KG across 100+ connectors | Unified index of company content, people, and activity. Results preferred 1.9× over ChatGPT on enterprise queries. | Enterprise-scale org-wide context |
| **Neo4j** | Native graph database | Mature ecosystem, Cypher query language, AuraDB managed service. Publishes context engineering best practices. | Self-hosted production graph |

**Pattern validated**: Our bi-temporal node schema (Section 1, `event_time` + `ingestion_time`) aligns with Graphiti's approach — the leading OSS implementation of temporal knowledge graphs for agents.

**Pattern validated**: Our three-tier implementation model (lightweight → mid-scale → production) maps to the market: in-memory for prototyping, Redis for mid-scale, and Graphiti/Neo4j/FalkorDB for production — exactly the progression these products serve.

---

## Related Resources

| Resource | Covers |
|----------|--------|
| [`ai-engine-layers.md`](ai-engine-layers.md) | Full 5-layer architecture overview |
| [`context-engineering.md`](context-engineering.md) | Progressive disclosure, session management, provenance |
| [`memory-systems.md`](memory-systems.md) | Four-memory model, write patterns, consolidation |
| [`rag-patterns.md`](rag-patterns.md) | Retrieval pipelines, hybrid search |
| [`../../../ai-rag/references/graph-rag-patterns.md`](../../../ai-rag/references/graph-rag-patterns.md) | Full graph-RAG implementation |
