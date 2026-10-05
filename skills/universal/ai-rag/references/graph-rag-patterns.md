# Graph RAG Patterns

> Operational guide for graph-based retrieval-augmented generation. Covers knowledge graph construction, entity extraction, hybrid graph+vector retrieval, GraphRAG-style patterns, and when graph retrieval outperforms flat vector search. Focus on implementation and production decisions.

Use this pattern when questions require relationship traversal or aggregation. Verify current framework and platform capabilities from official docs before making vendor-specific recommendations.

> **Empirical bounds.** Before building a graph layer, read
> [`../../ai-context-layer/references/agent-memory-benchmarks.md`](../../ai-context-layer/references/agent-memory-benchmarks.md)
> and the **A33** entry in
> [`../../ai-context-layer/references/anti-patterns-catalog.md`](../../ai-context-layer/references/anti-patterns-catalog.md).
> GraphRAG-Bench (ICLR 2026) shows multi-hop wins of +5–20pts but *single-hop
> losses* against plain RAG — route single-hop around the graph or skip the
> graph entirely. RA11 (`ai-context-layer/references/reference-architectures.md`)
> is the policy-doc-shaped recipe that combines vector + graph correctly.

---
## Table of Contents

- [Decision Tree: When to Use Graph RAG](#decision-tree-when-to-use-graph-rag)
- [Routing Rule: Graph First vs Hybrid First](#routing-rule-graph-first-vs-hybrid-first)
- [Quick Reference: Graph RAG vs Vector RAG](#quick-reference-graph-rag-vs-vector-rag)
- [Operational Patterns](#operational-patterns)
- [KG Lifecycle and Quality Dimensions](#kg-lifecycle-and-quality-dimensions)
- [Retrieval-Granularity Ladder](#retrieval-granularity-ladder)
- [Pattern 1: Knowledge Graph Construction](#pattern-1-knowledge-graph-construction)
- [Step 1: Entity and relationship extraction via LLM](#step-1-entity-and-relationship-extraction-via-llm)
- [Step 2: Entity resolution (deduplicate)](#step-2-entity-resolution-deduplicate)
- [Step 3: Store in Neo4j](#step-3-store-in-neo4j)
- [Pattern 1b: Semantic Knowledge Graph — Construction with No LLM](#pattern-1b-semantic-knowledge-graph--construction-with-no-llm)
- [Pattern 2: LazyGraphRAG — Default Starting Point for Graph-Augmented Retrieval](#pattern-2-lazygraphrag--default-starting-point-for-graph-augmented-retrieval)
- [Pattern 3: Microsoft GraphRAG (Community Summaries)](#pattern-3-microsoft-graphrag-community-summaries)
- [Step 1: Initialize](#step-1-initialize)
- [Step 2: Configure settings.yaml (llm, chunks, entity_extraction, embeddings)](#step-2-configure-settingsyaml-llm-chunks-entityextraction-embeddings)
- [Step 3: Index (builds graph + communities + summaries)](#step-3-index-builds-graph-communities-summaries)
- [Step 4: Query](#step-4-query)
- [Pattern 4: Hybrid Graph + Vector Retrieval](#pattern-4-hybrid-graph-vector-retrieval)
- [Pattern 5: Entity-Aware Chunking](#pattern-5-entity-aware-chunking)
- [Pattern 6: Subgraph Context Packing](#pattern-6-subgraph-context-packing)
- [Context Packing Formats: Graph-to-LLM Serialization](#context-packing-formats-graph-to-llm-serialization)
- [Pattern 7: Graph Maintenance and Updates](#pattern-7-graph-maintenance-and-updates)
- [Anti-Patterns](#anti-patterns)
- [Validation Checklist](#validation-checklist)
- [Cross-References](#cross-references)


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
│   │   └─ Evaluate typed graph traversal; iterative retrieval is another baseline
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

## Routing Rule: Graph First vs Hybrid First

Use graph traversal as the first hop only when the question is about
relationships, membership, paths, counts, or changes over typed entities. Use
hybrid lexical + vector retrieval first when the question is about evidence
text, quotations, explanatory passages, or open-ended document lookup.

| Query shape | First route | Follow-up |
|---|---|---|
| "Who works at X?" | Graph edge lookup | Pull supporting page chunks for citations. |
| "How is A connected to B?" | Graph path traversal | Retrieve evidence for each edge before answering. |
| "What changed since date D?" | Event ledger or temporal graph | Retrieve source snippets only for disputed claims. |
| "What does doc X say about Y?" | Hybrid retrieval | Use graph only to expand related entities if recall fails. |
| "Summarize themes across this corpus" | Hybrid retrieval or community summaries, based on eval | Avoid graph if single-hop evals already pass. |

The `garrytan/gbrain` operational-brain pattern is a useful concrete reference:
typed edges answer relationship questions, while hybrid search supplies the
source text and citations. Do not force every query through GraphRAG.

---

## Quick Reference: Graph RAG vs Vector RAG

| Dimension | Vector RAG | Graph RAG | Hybrid |
|-----------|-----------|-----------|--------|
| Factual retrieval | Passage lookup | Entity lookup plus source text | Evaluate combined candidates |
| Multi-hop reasoning | Needs query decomposition or repeated retrieval | Explicit paths where edges are accurate | Paths plus supporting passages |
| Global summarization | Requires corpus coverage beyond top passages | Community summaries | Evaluate coverage and source fidelity |
| Setup complexity | Low | High | High |
| Maintenance cost | Low | Medium-High | High |
| Latency | Measure on the workload | Include traversal and generation | Include all retrieval legs |
| Corpus size | Benchmark recall and index cost | Graph value depends on query shape and edge quality | Add only for a measured gap |

---

## KG Lifecycle and Quality Dimensions

Pattern 1 below builds the graph. This section is the lifecycle that surrounds it:
building the graph is stage one of five, and the three middle stages are a loop,
not a one-time pass.

```
creation ──▶ ┌─ assessment ⇄ cleaning ⇄ enrichment ─┐ ──▶ deployment
             └────── knowledge curation loop ───────┘
```

- **Creation** — define purpose and ontology first, then extract triplets (NER + relation extraction). Pattern 1 is this stage.
- **Assessment** — measure quality against the dimensions below before anything downstream trusts the graph.
- **Cleaning** — detect and correct errors (taxonomy and detection ladder below).
- **Enrichment** — KG completion: fill gaps, merge additional sources, re-run entity resolution. Heterogeneous sources make resolution *more* load-bearing, not less.
- **Deployment** — host and serve, with update, conflict, deletion, and access pipelines already designed. Deployment is not the end of the lifecycle; a deployed KG without an update pipeline goes stale by default.

**Quality dimensions to assess** (each needs a named owner and a measurement, or it is not being assessed):

| Dimension | What it asks | Failure it catches |
|---|---|---|
| Syntactic accuracy | Are triplets well-formed against the schema? | Malformed types, bad literals |
| Semantic accuracy | Are the asserted facts true? | Plausible-looking wrong edges |
| Completeness | Does the graph contain the entities/relations the domain needs? | Silent coverage gaps — compare against a golden-standard KG where one exists |
| Conciseness | Is knowledge expressed without redundancy? | Blank-node proliferation (anonymous/unnamed nodes generated during creation) bloating the graph |
| Timeliness | How stale is the graph, and on what cadence does it refresh? | Confidently answering from outdated facts |
| Accessibility | Can it actually be queried, manipulated, and updated in practice? | A correct graph nobody can use |
| Human interpretability | Can a person read and audit the representation? | Ungovernable graphs — ties to the transparency requirement |
| Security, privacy, traceability | Who can access it, and which source did each fact come from? | No deletion path for a user's data; no way to correct a bad source. Source tracking is the mechanism that makes record deletion (GDPR-style) possible at all |

Traceability is the one dimension that is cheap at creation time and near-impossible
to retrofit: tag every node and edge with its source at write time (see Pattern 7).

**Error taxonomy for cleaning:**

| Error class | Example |
|---|---|
| Syntactic | Malformed entity or relationship |
| Ontology-related | Assigned to a nonexistent ontology, wrong ontology, wrong property |
| Semantic | Fact is well-formed and ontologically valid but wrong |
| Source-inherited | The source document itself was wrong; the extraction faithfully copied the error |

**Detection ladder** — run cheapest first, escalate only for what survives:

1. **Statistical** — probabilistic outlier detection over the graph. Cheapest, catches gross anomalies.
2. **ML models** — learned variants of the same. Better recall; accuracy is still limited.
3. **Ontology / logical-rule reasoning** — exploit the ontology to derive contradictions (an instance cannot be both a Person and a Place). Precise where the ontology is expressive.
4. **LLM fact-check of individual triplets** — an LLM verifies a single triplet against its own knowledge (e.g. flagging `(Vienna, CapitalOf, Hungary)`). Most expensive per triplet; reserve for what the earlier rungs surfaced, and treat its verdicts as candidates for review rather than as ground truth.

Primary sources for the LLM-KG construction and completion framing:
[arXiv:2306.08302](https://arxiv.org/abs/2306.08302) (unifying LLMs and knowledge
graphs). Book treatment: Raieli & Iuculano, *Building AI Agents with LLMs, RAG,
and Knowledge Graphs* (Packt, 2025), Ch. 7.

---

## Retrieval-Granularity Ladder

Graph retrieval adds a granularity choice: nodes, edges, paths, or subgraphs.
Document-backed GraphRAG still uses chunks: Microsoft's indexing pipeline creates
TextUnits for extraction and provenance ([dataflow](https://microsoft.github.io/graphrag/index/default_dataflow/)).
Tune graph granularity for traversal loss and chunking for extraction or evidence loss.

| Granularity | What is returned | Use when |
|---|---|---|
| **Nodes** | Individual entities plus their properties | Targeted attribute lookup ("what is X's founding year?") |
| **Triplets** | Entities *and* their relationships | The relationship itself is the answer |
| **Paths** | A chain of nodes and edges from X to Y | Connection and multi-hop questions |
| **Subgraphs** | A connected region of the KG | Complex patterns and dependencies among several entities |
| **Hybrid / adaptive** | Several granularities at once, or chosen per query | Mixed query distribution — the production default once simple retrieval passes eval |

**Rule: adapt granularity to query complexity.** Simple queries are answered at
low granularity; complex queries benefit from higher. Over-retrieving saturates
the context with irrelevant elements and degrades generation — the same
redundant-context failure that GraphRAG was meant to fix. Path retrieval needs a
bound (shortest path, explicit rules, or a learned selector) because the number
of paths between two entities grows sharply with graph size.

This ladder governs *what to retrieve*; [Pattern 6](#pattern-6-subgraph-context-packing)
and the serialization formats after it govern *how to render it*. Pick the rung
first, then the format.

Primary source: [arXiv:2408.08921](https://arxiv.org/abs/2408.08921) (GraphRAG
survey — G-indexing / G-retrieval / G-generation, retrieval granularity, and
graph formats).

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

### Pattern 1b: Semantic Knowledge Graph — Construction with No LLM

**Use when** you want relatedness between terms/entities and you already have an inverted index. This is the cheap alternative to Pattern 1: no extraction pass, no LLM, no separate graph store.

Source: Grainger, Turnbull & Irwin, *AI-Powered Search* (Manning, 2025) §5.4; originally Grainger et al., "The Semantic Knowledge Graph: A compact, auto-generated model for real-time traversal and ranking of any relationship within a domain," *2016 IEEE International Conference on Data Science and Advanced Analytics (DSAA)*, pp. 420–429.

**The core idea.** Pattern 1 *builds* a graph by extracting entities and edges into storage. A semantic knowledge graph (SKG) doesn't build anything — the graph is already latent in the inverted index, as the co-occurrence structure of terms across documents. Traversal is a query. The book describes it as a search engine that, instead of matching and ranking documents, finds and ranks *terms* that best match a query.

Indexed over a health corpus, querying `advil` returns conceptually related terms with relatedness scores — the book's example output:

```text
advil     0.71
motrin    0.60
aleve     0.47
ibuprofen 0.38
alleve    0.37
```

These behave like "dynamic synonyms" — not same-meaning terms, but conceptually related ones, including the misspelling `alleve`, which no curated synonym list would have contained.

**How relatedness is scored.** Compare a foreground document set against a background set:

- `Dx` — documents matching the query `x` whose relatedness is being scored.
- `Dfg` — documents matching the **foreground** query. Relatedness of `x` is computed relative to this set.
- `Dbg` — documents matching the **background** query. Should be uncorrelated with `x` and `fg`, and is usually the entire collection or a random sample of it.
- `Px` — the probability of finding `x` in a random document in the background set.

The calculation is **conceptually similar to a z-score in a normal distribution**: it statistically compares the distribution of term `x` between the two sets. With foreground = documents matching `pain` and background = all documents, the relatedness of `advil` measures how much more often `advil` occurs in documents also containing `pain` than in a random document.

Scores are normally passed through a sigmoid to the range **−1.0 to 1.0**:

- Highly related terms → positive, approaching 1.0
- Highly unrelated terms (occurring only in divergent domains) → closer to −1.0
- Terms not semantically related at all, such as stop words → close to 0.0

That last property is what makes the method work without a stopword list. Stop words co-occur heavily with everything, so their foreground distribution matches their background distribution and the score collapses toward zero — they are filtered by the statistics rather than by a curated list.

**Implementation.** Apache Solr has SKG capabilities built into its faceting API: faceting traverses terms → document sets → terms, and the `relatedness` aggregation function implements the comparison.

```python
# Solr JSON facet: rank terms in `body` by relatedness to the foreground set
{"facet": {
    "related_terms": {
        "type": "terms",
        "field": "body",
        "limit": 10,
        "min_count": 2,          # exclude rare terms — noise reduction
        "sort": {"relatedness": "desc"},
        "facet": {"relatedness": {
            "type": "func",
            "func": "relatedness($fore,$back)"}}}}}
```

On engines without a native relatedness function, the same computation runs off term-document frequencies you can already retrieve — foreground count, background count, and collection size per candidate term.

**Traversal.** An SKG is not limited to one hop or one field. It can traverse *between* fields ("find the skills most related to this job title"), traverse multiple levels deep ("find the job titles most related to this query, then the skills most related to each of those"), and use any arbitrary engine query as a node in the traversal.

**Use cases the book names:** query expansion, content-based recommendations, query classification, query disambiguation, anomaly detection, data cleansing, predictive analytics.

**Corpus requirement — the real constraint.** An SKG needs term co-occurrence across many documents. The book is explicit that **Wikipedia is a poor dataset** for this: it tends to have a single authoritative page per major topic, so there is little cross-document overlap. Good corpora are user-submitted content with repeated overlapping vocabulary — forum posts, questions, job postings, reviews, social posts. A corpus of unique, non-overlapping documents produces a weak graph regardless of size.

**Why this matters as LLM extraction spreads.** Pattern 1's per-document LLM extraction pass is the dominant cost of a graph layer and the dominant source of its latency and its extraction errors. An SKG has none: construction cost is zero beyond the index you already maintain, traversal is a query at query latency, and there is no extraction step to hallucinate an edge. Where relatedness is the relationship you actually need, this is strictly cheaper.

**Where it does not substitute for Pattern 1.** An SKG gives you *statistical relatedness between terms*, not typed entities with typed edges. It cannot tell you that Alice `REPORTS_TO` Bob — only that "Alice" and "Bob" co-occur unusually often. Multi-hop questions requiring edge semantics, provenance per edge, or graph constraints still need an extracted graph.

**Decision rule:** if the query is "what is related to X" → SKG. If the query is "what is the *relationship* between X and Y", or answering requires traversing typed edges → Pattern 1. Running both is reasonable: SKG for query expansion at retrieval time, an extracted graph for relationship traversal.

### Pattern 2: LazyGraphRAG — Default Starting Point for Graph-Augmented Retrieval

**Evidence grade B** (corporate study, open benchmark, multi-baseline comparison — not independently peer-reviewed).

LazyGraphRAG is a cost-optimized variant of Microsoft GraphRAG that **defers LLM use entirely to query time**. At index time it runs only cheap noun-phrase extraction (no LLM entity summarization), keeping indexing cost at approximately vector-RAG levels. At query time it uses an LLM to reason over retrieved graph context.

Microsoft's [LazyGraphRAG study](https://www.microsoft.com/en-us/research/blog/lazygraphrag-setting-a-new-standard-for-quality-and-cost/)
reports comparable global-query quality at more than 700 times lower query cost
for a particular configuration on AP news articles with synthetic queries and
pairwise LLM judgments. This is a study result, not a workload-independent ratio.

**Decision rule:** Compare deferred query-time synthesis against precomputed
community summaries on the same corpus and query slices; choose from measured
quality, indexing cost, and query cost.

Before implementing, check the installed package's CLI help against the
[official CLI](https://microsoft.github.io/graphrag/cli/) and its method configuration.
Do not assume `entity_extraction.async_mode: lazy` enables LazyGraphRAG:
the study's algorithm and GraphRAG's documented indexing methods are distinct.

---

### Pattern 3: Microsoft GraphRAG (Community Summaries)

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

### Pattern 4: Hybrid Graph + Vector Retrieval

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

### Pattern 5: Entity-Aware Chunking

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

### Pattern 6: Subgraph Context Packing

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

### Context Packing Formats: Graph-to-LLM Serialization

The table above compares the formats most teams reach for first. The survey
literature describes a wider set of *graph translators* — converters that turn a
retrieved node, path, or subgraph into something an LLM ingests well. A graph is
non-Euclidean; text is a sequence. Every format below is a lossy projection, and
which loss you accept is the design decision.

| Format | What it is | Preserves | Costs |
|---|---|---|---|
| **Adjacency / edge table** | The node and edge set as a table | Relational structure compactly | Reads as data, not prose; needs an explicit instruction |
| **Natural-language templating** | Templates that render a subgraph as descriptive sentences, optionally labelling 1-hop vs 2-hop neighbours | Congenial to the LLM; hop distance can be made explicit | Verbose; template design is real work. An LLM can do the conversion instead, at extra cost and one more hallucination surface |
| **Node sequence** | Nodes emitted in a predetermined order | Very compact; conveys ordering | Drops most edge information |
| **Code-like forms** (GraphML, GML) | A standard graph markup language | Designed for graphs; structural + textual hybrid | Token-heavy; assumes the model has seen the format |
| **Syntax tree** | The graph flattened into a hierarchy | Hierarchical structure and topological order | Only faithful where the region is tree-shaped |

**The tradeoff, stated plainly:** the conversion must be *concise*, *complete*,
and *understandable to the LLM* at the same time — and optimally should also
carry the structural information. No format maximizes all of these. Choose which
one to sacrifice deliberately per query shape rather than defaulting to whatever
the driver emits.

**Caveat that shapes the choice:** studies of LLM graph understanding report that
models understand graphs presented in linear form and read **node labels better
than topological structure**. So label-rich, structure-light formats
(natural-language templating, node sequence) tend to outperform
structure-faithful but label-sparse ones — which is the opposite of what a graph
engineer's intuition suggests. Verify on your own eval before committing.

Primary sources: [arXiv:2408.08921](https://arxiv.org/abs/2408.08921) (graph
formats for G-generation); [arXiv:2404.14809](https://arxiv.org/abs/2404.14809)
(graph-task taxonomy and prompting methods for LLMs on graphs).

### Pattern 7: Graph Maintenance and Updates

- **Use when:** Keeping knowledge graph fresh as documents change
- **Operations:**
  - **New document:** chunk → extract entities/relationships → resolve against existing graph → store
  - **Updated document:** remove old extractions by source doc ID → re-extract
  - **Deleted document:** remove entities/relationships where this was the only source doc
- **Key rule:** Track `source_docs` array on every node — only delete nodes with zero remaining sources

---

## Graph + Vector Backends

The choice of graph backend shapes everything downstream — co-located vector + graph storage, query language, hosting model, and cost. Pick from real options, not abstractions.

| Backend | Graph + vector co-located? | Query | Hosted | Cost shape | When to pick |
|---|---|---|---|---|---|
| **Neo4j + vector index** | Yes (since v5.13) | Cypher + native vector | Self-host or Aura | Per-node + per-vector | Default if Cypher is the team's language; mature ecosystem |
| **AWS Neptune Analytics** | Yes (graph + vector in one engine) | openCypher + Gremlin + vector | Managed AWS | Per-instance hour + storage | **AWS-native GraphRAG** — pair with Bedrock KB; lowest-friction option on AWS |
| **LightRAG** | Yes (dual-level KG + vector) | REST API or Python SDK | Self-host | Extraction, embedding, storage, and query costs | Compare quality and update cost against the same graph baseline |
| **Memgraph** | Yes | Cypher + vector | Self-host or Cloud | Per-node | In-memory speed for hot graphs |
| **TigerGraph** | Yes | GSQL | Self-host or Cloud | Per-node | Multi-hop performance at scale (10+ hops) |
| **ArangoDB** | Yes (multi-model) | AQL | Self-host or Cloud | Per-instance | If you need document + graph + vector in one DB |
| **Postgres + AGE + pgvector** | Yes | Cypher (via AGE) + SQL + pgvector | Self-host | Per-instance | Don't add a new DB; SQL team already operating Postgres |
| **Vector DB + edge table** | No (graph faked in SQL) | Custom | Any | Per-vector | Avoid — DIY graph traversal usually loses to a real graph DB |

### LightRAG: Framework-Agnostic Alternative

LightRAG (HKUDS/LightRAG, MIT) is a dual-level graph + vector RAG framework that drastically reduces LLM calls during indexing by structuring knowledge at both fine-grained (entity/relationship) and abstract (theme) levels. It is framework-agnostic: available as a Python SDK or REST API server, integrating into LangChain, LlamaIndex, or custom pipelines without a fixed runtime dependency.

**Positioning vs LazyGraphRAG:**
- LazyGraphRAG (Microsoft) defers LLM use to query time; verify the available implementation and query-time budget before selecting it.
- LightRAG offers graph and vector retrieval with deployment and update options in its [official repository](https://github.com/HKUDS/LightRAG). Measure indexing time, model usage, and answer quality on the same corpus before claiming a cost advantage.

**When to pick LightRAG over LazyGraphRAG:**
- Team is not invested in the `graphrag` CLI or Microsoft tool ecosystem
- Incremental updates without full rebuilds are required
- Multimodal inputs (text + images + tables) via MinerU/Docling are in scope
- You want REST API deployment rather than Python process management

**When to pick LazyGraphRAG:**
- Already using Microsoft GraphRAG and want to reduce cost without switching stack
- Community summary (global-query) quality is the primary benchmark

### AWS Neptune Analytics: The AWS-Native GraphRAG Pick

Neptune Analytics is the **AWS-native GraphRAG pick** (re-check AWS's current graph and vector offerings before committing). It stores graph and vector in one engine, so traversal + similarity in the same query are first-class. Pair with **Bedrock Knowledge Bases** as the ingestion + chunking + LLM-extraction layer; Neptune Analytics handles storage and query.

**Why this composition wins on AWS:**

- Bedrock KB does the heavy lifting on entity/relationship extraction via LLM-driven ingestion (no custom extraction pipeline)
- Neptune Analytics stores both the resulting graph and the vector embeddings of nodes/chunks
- One AWS-managed billing surface; no separate Neo4j Aura subscription
- IAM-shaped access control; integrates with AgentCore Identity for per-agent graph scoping

**When to pick Neptune Analytics over Neo4j Aura on AWS:**

- Already on AWS, want one bill and one IAM model
- Multimodal RAG (H5) where vector and graph live next to each other matters
- Compliance regions where AWS residency is pinned
- Team is light on Cypher expertise — openCypher in Neptune is close enough that switching costs are real but bounded

**When to stay with Neo4j (Aura or self-host) on AWS:**

- Cypher expertise is deep on the team
- Need APOC procedures or community plugins that Neptune doesn't ship
- Multi-cloud roadmap — Neo4j ports; Neptune doesn't

**Anti-pattern**: Picking Neptune (the classic Neptune service, not Neptune Analytics) for GraphRAG. Classic Neptune is graph-only; you'd need to bolt on a vector store and write the join logic yourself. Use **Neptune Analytics** specifically.

See also: `../../router-engineering/references/engineering-scenarios.md#j2-build-managed-rag-on-bedrock-knowledge-bases` for the J2 hosting scenario that composes with this backend.

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
| Handing a large raw graph to the LLM and expecting topological reasoning | LLM structural reasoning degrades as graph size and task complexity increase; models read node labels better than topology | Retrieve a bounded region first (granularity ladder), then serialize label-rich — do not delegate traversal to the model |
| Routing abstractive or entity-free questions through GraphRAG | The literature's own concession: GraphRAG underperforms on abstractive QA and when the question names no explicit entity; text nuance is lost in the graph projection | Detect entity-free/abstractive queries at routing time and send them to hybrid vector retrieval instead |

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
