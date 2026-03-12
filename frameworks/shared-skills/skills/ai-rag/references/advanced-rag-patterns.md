# Advanced RAG Patterns

Modern RAG paradigms beyond static retrieval: structured data, graph RAG, multimodal retrieval, online evaluation, and production telemetry.

---

## Structured, Graph, and Multimodal RAG

**Use when:** Data has strong structure (tables/graphs), relationships, or images that text-only chunks miss.

### Graph/Knowledge RAG

- Build entity/relation graph
- Store text evidence per edge
- Use graph traversal (k-hop, path ranking) before generation
- Fall back to text RAG when graph thin
- **Example use cases:** Knowledge bases, entity-heavy documents, technical manuals with component relationships

### Table/Structured Data RAG

- Normalize tables
- Add row/column headers to text
- Use hybrid retrieval (lexical + dense) with schema-aware metadata
- Cite cell coordinates
- **Example use cases:** Financial reports, scientific data, product specifications

### Multimodal RAG

- Encode images with vision encoder + connector
- Store image embeddings alongside text
- Retrieve both text and images
- Include low-res thumbnails/alt-text for grounding
- Gate unsafe images
- **Example use cases:** Product catalogs, medical imaging, technical diagrams

### Two-Stage Pipelines

- **Stage 1:** Structured/graph retrieval first
- **Stage 2:** Augment with unstructured context
- Use reranker that can handle structured hints
- **Benefit:** Best of both worlds - precision from structure, coverage from text

### Freshness/Governance

- Keep graph/table versioning
- Backfill after schema changes
- Per-tenant/index isolation when required
- Track lineage and provenance

### Implementation Checklist

- [ ] Graph/table indexing path defined with versioning and rollback
- [ ] Multimodal retrieval tested (vision encoder + connector latency)
- [ ] Hybrid pipeline returns structured + unstructured context
- [ ] Safety filter for images and PII in structured data
- [ ] Evaluated on structured/multimodal benchmarks or slice sets

---

## Online Evaluation, Telemetry, and Freshness

**Use when:** Running RAG in production with changing data.

### Online Signals

- Capture click/open, dwell/scroll, abandonment, manual edits
- Link to request IDs
- Scrub PII before logging
- **Metrics to track:**
  - Click-through rate (CTR)
  - Time to first action
  - Session abandonment rate
  - Manual edit frequency

### Shadow/Canary Testing

- Route small % of traffic to new retrievers/chunkers/rerankers
- Measure solve rate, cost, latency, groundedness
- Abort on regressions
- **Best practice:** Start with 1-5% traffic, expand gradually

### Freshness Telemetry

- Track ingestion lag per source
- Alert on staleness
- Surface index/version in responses for audit
- **SLA targets:**
  - Real-time systems: <5min lag
  - Batch systems: <24hr lag
  - Archive systems: <7d lag

### Slice Dashboards

Track metrics by dimension:
- Domain/source/task slices
- Multilingual slices
- Structured vs unstructured
- Hallucination/grounding errors tracked separately
- **Purpose:** Identify performance degradation in specific segments

### Eval Set Protection

- Prevent production data (with IDs) from contaminating eval sets
- Log hash of eval items
- Periodic refresh with human review
- **Anti-pattern:** Using production queries directly as eval set

### Production Checklist

- [ ] Online metrics wired (solve rate, grounding, latency, cost)
- [ ] Shadow/canary gates with auto-abort on regression
- [ ] Ingestion lag + index/version surfaced and monitored
- [ ] Sliced dashboards (domain, language, data type)
- [ ] Eval contamination checks in place

---

## Context Compression & Budgeting

**Use when context window is tight.**

### Compression Strategies

1. **Merge adjacent chunks** - Combine semantically related chunks
2. **Deduplicate repeated sentences** - Remove redundant information
3. **Summarize long chunks (LLM distillation)** - Use smaller model to compress
4. **Prioritize by relevance score** - Include highest-scoring chunks first
5. **Structure context as sections** - Group by topic/source

### Token Budget Management

- Calculate token budget: `model_context_window - prompt_tokens - max_output_tokens`
- Reserve 20-30% buffer for formatting overhead
- Track actual usage vs budget
- **Example:** Claude 200k context → reserve ~150k for retrieved content

### Context Optimization Checklist

- [ ] Fits within model's token budget
- [ ] Includes top-ranked chunks
- [ ] Avoids filler / irrelevant content
- [ ] Document titles preserved
- [ ] Compression tested on eval set (no quality degradation)

---

## Modern Paradigm Shift

**The era of static RAG is over.** Modern RAG systems are:

### Adaptive Retrieval
- Query complexity determines retrieval strategy
- Simple queries: direct vector search
- Complex queries: multi-hop, graph traversal, iterative refinement

### Self-Correcting Systems
- Monitor retrieval quality in real-time
- Automatic fallback strategies
- Query reformulation on poor results

### Wise Retrieval
- Context-aware chunking (Contextual Retrieval)
- Learned ranking (rerankers trained on domain data)
- Personalized retrieval (user history, preferences)

### Multimodal & Structured Integration
- Text + images + tables + graphs
- Unified retrieval across modalities
- Structure-aware generation

---

## GEAR: Graph-Enhanced Agentic RAG

**2026 Update**: GEAR combines knowledge graphs with agentic retrieval for enterprise use cases where relationships between entities are critical.

### Architecture

```text
GEAR Pipeline:
  1. Query → Entity extraction (NER)
  2. Graph lookup → Find related entities and relationships
  3. Decision: Graph-only, vector-only, or hybrid?
  4. Hybrid retrieval:
     - Graph traversal for structured facts
     - Vector search for unstructured context
  5. Merge results with entity grounding
  6. Generate with structured + unstructured evidence
```

### When GEAR Outperforms Standard RAG

| Scenario | Standard RAG | GEAR |
|----------|-------------|------|
| "What products does Company X sell?" | May retrieve tangential docs | Direct graph traversal |
| "How are A and B related?" | Struggles with multi-hop | Graph path finding |
| "All contracts mentioning Entity Y" | Keyword-dependent | Entity-linked retrieval |
| Compliance: "Clauses affecting Party Z" | High miss rate | Relationship-aware |

### Implementation Components

1. **Knowledge Graph Construction**
   - Entity extraction from documents
   - Relationship extraction (LLM or rule-based)
   - Graph storage (Neo4j, Amazon Neptune, or embedded)

2. **Query Understanding**
   - Entity recognition in query
   - Intent classification (factual vs relational vs aggregation)
   - Graph query generation (Cypher, SPARQL, or custom)

3. **Hybrid Retrieval**
   - Graph: Entities + 1-2 hop neighbors + edge evidence
   - Vector: Semantically similar chunks
   - Fusion: Interleave or prioritize based on query type

### GEAR Checklist

- [ ] Entity extraction pipeline defined
- [ ] Graph schema designed for domain
- [ ] Query router distinguishes factual vs relational queries
- [ ] Hybrid fusion tested (graph + vector)
- [ ] Evaluated on relationship-heavy queries

---

## Contextual Memory: RAG Alternative for Agentic AI

**2026 Trend**: For agentic AI systems, contextual memory (also called agentic memory or long-context memory) is emerging as an alternative to traditional RAG.

### RAG vs Contextual Memory

| Aspect | Traditional RAG | Contextual Memory |
|--------|-----------------|-------------------|
| Retrieval | Per-query, stateless | Persistent, evolving |
| Context | Retrieved chunks | Accumulated session state |
| Best for | Factual Q&A | Multi-turn agentic workflows |
| Latency | Retrieval + generation | Direct generation (if fits context) |
| Freshness | Depends on index | Real-time updates |

### When to Use Contextual Memory

**Good candidates**:

- Long-running agent sessions
- Conversational AI with persistent state
- Workflows where previous actions inform future decisions
- Small-to-medium knowledge bases (<200K tokens)

**Stick with RAG when**:

- Large corpus (>500K tokens)
- Strict citation requirements
- Multi-user with different access permissions
- Freshness from external sources needed

### Hybrid Approach

Many production systems combine both:

```text
Hybrid Memory Architecture:
  1. Session context: Recent interactions in context window
  2. Short-term memory: Important facts from current session (contextual)
  3. Long-term memory: Persistent knowledge base (RAG)
  4. Query routing: Decide which memory tier to query
```

### Implementation Patterns

1. **Sliding Window + RAG**
   - Keep last N turns in context
   - RAG for older or external knowledge

2. **Memory Compression**
   - Summarize old context periodically
   - Store summaries in vector DB
   - Retrieve relevant summaries

3. **Memory Types**
   - Episodic: What happened (events, actions)
   - Semantic: What is true (facts, knowledge)
   - Procedural: How to do things (workflows, rules)

---

## Related Resources

- [Agentic RAG Patterns](agentic-rag-patterns.md) - Loop-based RAG architectures

- [Contextual Retrieval Guide](contextual-retrieval-guide.md) - Anthropic's 2024 technique
- [Retrieval Patterns](retrieval-patterns.md) - Hybrid search and reranking
- [Grounding Checklists](grounding-checklists.md) - Hallucination prevention
- [RAG Troubleshooting](rag-troubleshooting.md) - Debugging production issues
