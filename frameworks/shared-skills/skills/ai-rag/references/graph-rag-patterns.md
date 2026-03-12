# Graph RAG Patterns

> Operational guide for graph-based retrieval-augmented generation. Covers knowledge graph construction, entity extraction, hybrid graph+vector retrieval, Microsoft GraphRAG patterns, and when graph RAG outperforms flat vector search. Focus on implementation and production decisions.

**Freshness anchor:** January 2026 — Neo4j 5.x, LangChain 0.3+, LlamaIndex 0.11+, Microsoft GraphRAG 1.x

---

## Decision Tree: When to Use Graph RAG

```
START
│
├─ What kind of questions will users ask?
│   ├─ Factual lookup ("What is X?")
│   │   └─ Standard vector RAG is sufficient
│   │
│   ├─ Relational ("How is X related to Y?")
│   │   └─ Graph RAG strongly recommended
│   │
│   ├─ Multi-hop ("What companies does X's advisor also advise?")
│   │   └─ Graph RAG required — vector search cannot traverse
│   │
│   ├─ Aggregation ("What are the main themes across all documents?")
│   │   └─ Microsoft GraphRAG (community summaries)
│   │
│   └─ Comparison ("How do X and Y differ?")
│       └─ Graph RAG helpful (entity-pair retrieval)
│
├─ Corpus characteristics?
│   ├─ Highly structured (legal, medical, financial)
│   │   └─ Graph RAG — entities and relationships are well-defined
│   │
│   ├─ Loosely structured (blog posts, documentation)
│   │   └─ Vector RAG usually sufficient; graph adds marginal value
│   │
│   └─ Mixed (structured + unstructured)
│       └─ Hybrid graph + vector
│
└─ Maintenance budget?
    ├─ Low → Vector RAG only (graph requires ongoing maintenance)
    ├─ Medium → Graph RAG with automated entity extraction
    └─ High → Full knowledge graph with manual curation + automated updates
```

---

## Quick Reference: Graph RAG vs Vector RAG

| Dimension | Vector RAG | Graph RAG | Hybrid |
|-----------|-----------|-----------|--------|
| Factual retrieval | Good | Good | Best |
| Multi-hop reasoning | Poor | Excellent | Excellent |
| Global summarization | Poor | Good (GraphRAG) | Good |
| Setup complexity | Low | High | High |
| Maintenance cost | Low | Medium-High | High |
| Latency | Low (~100ms) | Medium (~500ms) | Medium (~500ms) |
| Corpus < 1000 docs | Sufficient | Over-engineered | Over-engineered |
| Corpus > 10000 docs | Degrades | Scales well | Best |

---

## Operational Patterns

### Pattern 1: Knowledge Graph Construction

- **Use when:** Building a graph from unstructured text
- **Pipeline:**

```
Documents → Chunking → Entity Extraction → Relationship Extraction
    → Entity Resolution → Graph Storage → Index Creation
```

- **Implementation:**

```python
from langchain_community.graphs import Neo4jGraph
from langchain_openai import ChatOpenAI
from langchain.chains import GraphCypherQAChain

# Step 1: Entity and relationship extraction via LLM
EXTRACTION_PROMPT = """
Extract entities and relationships from the following text.
Return as JSON with format:
{
  "entities": [{"name": "...", "type": "...", "properties": {...}}],
  "relationships": [{"source": "...", "target": "...", "type": "...", "properties": {...}}]
}

Entity types: Person, Organization, Product, Technology, Location, Event
Relationship types: WORKS_AT, FOUNDED, ACQUIRED, PARTNERS_WITH, USES, LOCATED_IN

Text: {text}
"""

def extract_entities_and_relationships(text, llm):
    """Extract structured knowledge from text chunk."""
    response = llm.invoke(EXTRACTION_PROMPT.format(text=text))
    return parse_json_response(response.content)

# Step 2: Entity resolution (deduplicate)
def resolve_entities(entities):
    """Merge duplicate entities with fuzzy matching."""
    from rapidfuzz import fuzz

    resolved = []
    for entity in entities:
        matched = False
        for existing in resolved:
            if (existing['type'] == entity['type'] and
                fuzz.ratio(existing['name'].lower(), entity['name'].lower()) > 85):
                # Merge properties
                existing['properties'].update(entity['properties'])
                existing['aliases'] = existing.get('aliases', []) + [entity['name']]
                matched = True
                break
        if not matched:
            resolved.append(entity)
    return resolved

# Step 3: Store in Neo4j
def store_in_neo4j(graph, entities, relationships, source_doc):
    """Write extracted knowledge to Neo4j."""
    for entity in entities:
        graph.query("""
            MERGE (e:{type} {{name: $name}})
            SET e += $properties
            SET e.source_docs = coalesce(e.source_docs, []) + [$source]
        """.format(type=entity['type']),
        params={
            'name': entity['name'],
            'properties': entity['properties'],
            'source': source_doc,
        })

    for rel in relationships:
        graph.query("""
            MATCH (s {{name: $source}})
            MATCH (t {{name: $target}})
            MERGE (s)-[r:{type}]->(t)
            SET r += $properties
        """.format(type=rel['type']),
        params={
            'source': rel['source'],
            'target': rel['target'],
            'properties': rel.get('properties', {}),
        })
```

### Pattern 2: Microsoft GraphRAG (Community Summaries)

- **Use when:** Need global queries ("What are the main themes?") or large corpus overview
- **Concept:** Build graph, detect communities (Leiden algorithm), summarize each community

```bash
# Step 1: Initialize
graphrag init --root ./ragproject

# Step 2: Configure settings.yaml (llm, chunks, entity_extraction, embeddings)

# Step 3: Index (builds graph + communities + summaries)
graphrag index --root ./ragproject

# Step 4: Query
graphrag query --root ./ragproject --method local --query "What is Company X's strategy?"
graphrag query --root ./ragproject --method global --query "What are the main industry trends?"
```

- **When to use Local vs Global:**

| Query Type | Method | Example |
|-----------|--------|---------|
| Specific entity questions | Local | "What products does X offer?" |
| Relationship questions | Local | "How is X connected to Y?" |
| Theme/trend questions | Global | "What are the key challenges?" |
| Summarization questions | Global | "Summarize the main topics" |
| Comparison questions | Local (both entities) | "Compare X and Y strategies" |

### Pattern 3: Hybrid Graph + Vector Retrieval

- **Use when:** Need both semantic similarity and structural traversal
- **Implementation:**

```python
from neo4j import GraphDatabase
import numpy as np

class HybridGraphVectorRetriever:
    """Combine vector similarity with graph traversal."""

    def __init__(self, neo4j_driver, embedding_model):
        self.driver = neo4j_driver
        self.embedder = embedding_model

    def retrieve(self, query, k_vector=10, k_graph=10, hop_depth=2):
        """
        Step 1: Vector search for relevant chunks
        Step 2: Extract entities from those chunks
        Step 3: Traverse graph from those entities
        Step 4: Merge and rank results
        """
        query_embedding = self.embedder.encode(query)

        # Step 1: Vector similarity search
        vector_results = self._vector_search(query_embedding, k=k_vector)

        # Step 2: Extract entities from vector results
        entity_names = self._extract_entities_from_chunks(vector_results)

        # Step 3: Graph traversal from entities
        graph_context = self._traverse_graph(entity_names, depth=hop_depth)

        # Step 4: Merge
        combined_context = self._merge_contexts(vector_results, graph_context)

        return combined_context

    def _vector_search(self, embedding, k):
        """Neo4j vector index search."""
        with self.driver.session() as session:
            result = session.run("""
                CALL db.index.vector.queryNodes('chunk_embeddings', $k, $embedding)
                YIELD node, score
                RETURN node.text AS text, node.source AS source, score
            """, k=k, embedding=embedding.tolist())
            return [dict(record) for record in result]

    def _traverse_graph(self, entity_names, depth):
        """Multi-hop graph traversal from seed entities."""
        with self.driver.session() as session:
            result = session.run("""
                UNWIND $entities AS entity_name
                MATCH (e {name: entity_name})
                CALL apoc.path.subgraphAll(e, {
                    maxLevel: $depth,
                    relationshipFilter: '>',
                    limit: 50
                })
                YIELD nodes, relationships
                RETURN nodes, relationships
            """, entities=entity_names, depth=depth)
            return self._format_graph_context(result)

    def _merge_contexts(self, vector_results, graph_context):
        """Interleave vector and graph results."""
        # Vector results: direct semantic matches
        # Graph results: structurally connected entities and relationships
        context_parts = []
        context_parts.append("## Relevant passages\n")
        for vr in vector_results[:5]:
            context_parts.append(f"- {vr['text']}")

        context_parts.append("\n## Related entities and relationships\n")
        context_parts.append(graph_context)

        return "\n".join(context_parts)
```

### Pattern 4: Entity-Aware Chunking

- **Use when:** Standard chunking breaks entities across chunks
- **Implementation:**

```python
def entity_aware_chunking(text, max_chunk_size=1000, overlap=100):
    """Chunk text while keeping entity mentions intact."""
    import spacy
    nlp = spacy.load("en_core_web_sm")
    doc = nlp(text)

    # Identify entity spans
    entity_spans = [(ent.start_char, ent.end_char) for ent in doc.ents]

    # Split on paragraph boundaries, respecting entity spans
    chunks = []
    current_chunk_start = 0

    for i, char in enumerate(text):
        if i - current_chunk_start >= max_chunk_size:
            # Find nearest paragraph break that doesn't split an entity
            split_point = find_safe_split(text, i, entity_spans)
            chunks.append(text[current_chunk_start:split_point])
            current_chunk_start = max(current_chunk_start, split_point - overlap)

    if current_chunk_start < len(text):
        chunks.append(text[current_chunk_start:])

    # Tag each chunk with its entities
    tagged_chunks = []
    for chunk in chunks:
        chunk_doc = nlp(chunk)
        entities = [(ent.text, ent.label_) for ent in chunk_doc.ents]
        tagged_chunks.append({
            'text': chunk,
            'entities': entities,
        })

    return tagged_chunks
```

### Pattern 5: Subgraph Context Packing

- **Use when:** Packing retrieved graph context into LLM prompt efficiently
- **Implementation:**

```python
def pack_subgraph_context(entities, relationships, max_tokens=2000):
    """
    Format graph context for LLM consumption.
    Priority: directly relevant entities > 1-hop > 2-hop
    """
    context_lines = []

    # Tier 1: Core entities (directly matched)
    context_lines.append("### Key Entities")
    for entity in entities[:10]:
        props = ", ".join(f"{k}: {v}" for k, v in entity.get('properties', {}).items())
        context_lines.append(f"- **{entity['name']}** ({entity['type']}): {props}")

    # Tier 2: Relationships
    context_lines.append("\n### Relationships")
    for rel in relationships[:20]:
        context_lines.append(
            f"- {rel['source']} --[{rel['type']}]--> {rel['target']}"
        )

    # Tier 3: Trim to token budget
    context = "\n".join(context_lines)
    if estimate_tokens(context) > max_tokens:
        context = truncate_to_tokens(context, max_tokens)

    return context
```

- **Context format comparison:**

| Format | Token Efficiency | LLM Comprehension | Use When |
|--------|-----------------|-------------------|----------|
| Triple notation (S→P→O) | High | Good | Many relationships |
| Natural language sentences | Low | Excellent | Few relationships, stakeholder-facing |
| Structured JSON | Medium | Good (with instruction) | API-based pipelines |
| Cypher-style text | High | Moderate | Technical users |

### Pattern 6: Graph Maintenance and Updates

- **Use when:** Keeping knowledge graph fresh as documents change
- **Operations:**
  - **New document:** chunk → extract entities/relationships → resolve against existing graph → store
  - **Updated document:** remove old extractions by source doc ID → re-extract
  - **Deleted document:** remove entities/relationships where this was the only source doc
- **Key rule:** Track `source_docs` array on every node — only delete nodes with zero remaining sources

---

## Anti-Patterns

| Anti-Pattern | Why It Fails | Fix |
|---|---|---|
| Graph RAG for simple factual Q&A | Over-engineered, higher latency, same quality | Use standard vector RAG |
| No entity resolution | Duplicate entities fragment the graph | Fuzzy matching + canonical name resolution |
| Extracting entities without relationship types | Graph without typed edges is hard to traverse | Define ontology upfront (entity + relationship types) |
| Storing full text in graph nodes | Slow queries, bloated graph | Store text in vector store, link via IDs |
| No source provenance on entities | Cannot trace facts back to documents | Tag every entity/relationship with source doc IDs |
| Building graph once, never updating | Graph becomes stale | Incremental update pipeline on document changes |
| Traversing too many hops (>3) | Context becomes noisy and irrelevant | Limit to 2 hops, rank by relevance |
| Using graph RAG without vector fallback | Misses entities not in graph | Always combine with vector search (hybrid) |
| Manual ontology for >50 entity types | Unsustainable maintenance | LLM-driven extraction with constrained output schema |
| Community summaries at wrong granularity | Too coarse = vague; too fine = redundant | Tune Leiden resolution parameter, evaluate summary quality |

---

## Validation Checklist

- [ ] Use case analysis confirms graph RAG value (multi-hop, relational queries)
- [ ] Entity types and relationship types defined in ontology
- [ ] Entity resolution pipeline prevents duplicates
- [ ] Source provenance tracked on all nodes and edges
- [ ] Hybrid retrieval combines graph traversal + vector similarity
- [ ] Graph context packed within LLM token budget
- [ ] Incremental update pipeline handles add/update/delete
- [ ] Query latency measured and within SLA (<1s typical)
- [ ] Graph quality evaluated (entity coverage, relationship accuracy)
- [ ] Fallback to vector-only if graph retrieval returns empty

---

## Cross-References

- `ai-rag/references/embedding-model-guide.md` — embeddings for vector component of hybrid search
- `ai-rag/references/rag-caching-patterns.md` — caching graph traversal results
- `ai-mlops/references/experiment-tracking-patterns.md` — tracking graph RAG quality experiments
- `ai-mlops/references/cost-management-finops.md` — LLM costs for entity extraction at scale
