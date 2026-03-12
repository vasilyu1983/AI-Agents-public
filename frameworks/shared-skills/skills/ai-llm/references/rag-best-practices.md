# RAG (Retrieval-Augmented Generation) Best Practices

*Purpose: Field-ready checklists, templates, and anti-patterns for designing, deploying, and validating RAG (Retrieval-Augmented Generation) systems in LLM applications.*

---

## Core Patterns

---

### Pattern 1: Minimal RAG Pipeline

**Use when:** Implementing RAG for basic QA, document search, or LLM grounding.

**Structure:**

```
1. Chunk source docs (fixed/overlapping windows, 300–800 tokens)
2. Embed chunks (e.g., ada-002, BGE-large, Sentence Transformers)
3. Store in a vector database (Pinecone, Qdrant, Chroma)
4. On user query:
   a. Embed question
   b. Retrieve top-k most similar chunks
   c. Build prompt: [question + retrieved context]
   d. Generate answer (LLM)
5. Evaluate: retrieval recall, faithfulness, answer precision
```

**Checklist:**

- [ ] All source docs chunked with overlap (if needed)
- [ ] Embedding model tested for your language/domain
- [ ] Vector DB indexed and queryable
- [ ] Retrieval latency <1s (target)
- [ ] Top-k recall >85% on gold questions
- [ ] LLM prompt includes clear citations (if possible)
- [ ] Eval: faithfulness, hallucination, latency, cost

---

### Pattern 2: Advanced RAG (Reranking, Filtering, Hybrid)

**Use when:** Data is large, complex, or precision/faithfulness requirements are high.

**Structure:**

```
1. Advanced chunking (structure-aware: titles, sections, lists)
2. Hybrid retrieval (dense + keyword)
3. Post-retrieval reranking (cross-encoder, LLM reranker, metadata scoring)
4. Context window compression (summarize or select most relevant)
5. Prompt assembly with references/citations
6. Automated feedback/loop for missed retrievals
```

**Checklist:**

- [ ] Metadata fields available (source, timestamp, tags)
- [ ] Hybrid retrieval tuned: dense, keyword, BM25 weights
- [ ] Reranker in place and tuned (accuracy vs. speed trade-off)
- [ ] Chunk deduplication and source tracking enabled
- [ ] Chunk size/context window fits LLM prompt limit
- [ ] Retrievals and generations logged for eval/debug

---

### Pattern 3: Modular RAG

**Use when:** Multi-modal input, multi-agent, or dynamic knowledge bases.

**Structure:**

```
1. Multi-type index (text, images, tables, etc)
2. Routing module: route query to proper retriever/agent
3. Query rewriting (clarification, expansion, language switch)
4. Agent hand-off or tool invocation
5. Multi-hop retrieval (chain-of-retrievals, agents fetch iteratively)
6. End-to-end monitoring/feedback for improvement
```

**Checklist:**

- [ ] All modalities/indices mapped, routers defined
- [ ] Query rewriting tested for edge cases
- [ ] Multi-hop/agent hand-off working with fallback
- [ ] Logging and observability on all steps
- [ ] E2E tests: cross-modal, complex QA, tool integration

---

## Decision Matrices

### Chunking Strategy Table

| Data Type            | Best Chunking         | Overlap?   | Checklist               |
|----------------------|----------------------|------------|-------------------------|
| Markdown, docs      | Headings + fixed win | Yes (50–100)| Dedup, preserve context |
| PDFs, HTML          | Paragraphs or tokens | Sometimes  | OCR, tag clean, dedup   |
| Code                | Functions, classes   | No/Yes     | Keep signatures         |
| Tables, CSV         | Row or block         | Sometimes  | Context expansion       |

---

### RAG Mode Selector

| Scenario                      | Mode            | Pattern      | Checklist             |
|-------------------------------|-----------------|-------------|-----------------------|
| Small, static docs            | Naive           | Pattern 1    | Simple, fast deploy   |
| >50k docs, mixed format       | Advanced        | Pattern 2    | Hybrid, rerank        |
| Multimodal, agent workflow    | Modular         | Pattern 3    | Routers, hand-off     |

---

## Advanced RAG Architectures (2026)

### Pattern 4: Agentic RAG

**Use when:** LLM needs to decide when, what, and from where to retrieve dynamically.

**Structure:**

```
1. LLM receives query and decides if retrieval is needed
2. If yes: LLM selects retriever, formulates search query
3. Retrieval executed via function/tool calling
4. LLM evaluates retrieved context quality
5. LLM decides: use context, retrieve more, or answer directly
6. Generate answer with citations
```

**Key characteristics:**
- LLM acts as autonomous agent controlling retrieval
- Dynamic multi-source retrieval (multiple indexes, APIs, databases)
- Self-correcting: can re-retrieve if initial results insufficient
- Uses LangGraph or function calling for orchestration

**Checklist:**

- [ ] Tool definitions for each retrieval source
- [ ] Query rewriting/expansion logic in agent
- [ ] Retrieval quality evaluation step
- [ ] Maximum retrieval attempts configured (prevent infinite loops)
- [ ] Fallback to "no answer" when confidence low
- [ ] Full traceability of retrieval decisions

---

### Pattern 5: GraphRAG (Knowledge Graph RAG)

**Use when:** Need deterministic retrieval, entity relationships, or structured reasoning.

**Structure:**

```
1. Build knowledge graph from source documents
   - Entity extraction (NER, LLM-based)
   - Relationship mapping
   - Community detection for clustering
2. Query processing:
   a. Entity recognition in query
   b. Graph traversal to relevant nodes
   c. Context assembly from graph neighborhoods
3. LLM generation with graph-grounded context
4. Citation via entity/relationship paths
```

**Performance metrics (vs traditional RAG):**
- 26-97% fewer tokens used
- 86.31% accuracy on RobustQA benchmark
- Better handling of multi-hop questions

**Best for:**
- Legal/compliance documents with entity relationships
- Technical documentation with cross-references
- Any domain requiring traceable reasoning paths

**Checklist:**

- [ ] Knowledge graph constructed and validated
- [ ] Entity extraction quality >90%
- [ ] Relationship types defined and consistent
- [ ] Graph query latency acceptable (<500ms)
- [ ] Hybrid mode: graph + vector for coverage
- [ ] Graph update pipeline for new documents

---

### Architecture Comparison (2026)

| Architecture | Token Efficiency | Accuracy | Complexity | Best For |
|--------------|-----------------|----------|------------|----------|
| **Naive RAG** | Low | Good | Low | Simple QA, small corpora |
| **Advanced RAG** | Medium | High | Medium | Production systems |
| **Modular RAG** | Medium | High | High | Multi-modal, multi-source |
| **Agentic RAG** | Variable | Highest | High | Dynamic retrieval needs |
| **GraphRAG** | Highest (26-97% fewer) | 86%+ | High | Structured domains |

**Sources:** [Microsoft GraphRAG](https://microsoft.github.io/graphrag/), [RAG Models 2026 (Techment)](https://www.techment.com/blogs/rag-models-2026-enterprise-ai/)

---

## Common Mistakes & Anti-Patterns

---

[FAIL] **Over-chunking:** Chunks too small, lose context, increase irrelevant retrievals.  
[OK] **Instead:** Tune chunk size (usually 300–800 tokens), prefer semantically meaningful breaks.

[FAIL] **Context overload:** Dumping all retrieved chunks in the prompt; exceeds LLM limit, dilutes key info.  
[OK] **Instead:** Rerank top chunks, use compression, summarize, enforce hard context window.

[FAIL] **No retrieval eval:** Assuming recall is good; never measured.  
[OK] **Instead:** Set up retrieval recall benchmarks with labeled QA sets; optimize “top-k” until recall >85%.

[FAIL] **No deduplication:** Multiple near-duplicate chunks flood retrieval; model repeats or hallucinate.  
[OK] **Instead:** Hash/compare chunks, deduplicate in index and on retrieval.

[FAIL] **RAG hallucination ignored:** LLM invents facts when retrieval is poor or context missing.  
[OK] **Instead:** Set up faithfulness eval, trigger fallback/no-answer when context missing, monitor outputs.

---

## Quick Reference

### RAG Production Checklist

- [ ] Source docs chunked, deduped, updated
- [ ] Embeddings model fit for domain
- [ ] Vector DB live, retrieval latency <1s
- [ ] Retrieval recall benchmarked, >85% top-k
- [ ] Reranking, filtering in place for large KB
- [ ] Prompt assembly: context window fits, references/citations clear
- [ ] Logging, monitoring, fallback in place

---

### Emergency Playbook

- If retrievals irrelevant:  
  1. Tune chunk size and overlap  
  2. Improve embedding model/domain  
  3. Add hybrid/keyword retrieval

- If latency spikes:  
  1. Reduce chunk count (lower k)  
  2. Optimize or switch vector DB  
  3. Remove heavy rerankers, batch queries

- If hallucinations spike:  
  1. Tighten filtering, compress context  
  2. Increase “no answer”/fallback threshold  
  3. Patch chunker/index, re-ingest source docs

---

## Further Resources

See `data/sources.json` for:

- RAG frameworks: LlamaIndex, LangChain, Haystack, Chroma, Pinecone, Qdrant
- Retrieval strategies, eval tools, vector DBs, embedding models

---

**Next:**  
See [references/agentic-patterns.md](agentic-patterns.md) for operational agent design, orchestration, error handling, and multi-agent collaboration templates.
