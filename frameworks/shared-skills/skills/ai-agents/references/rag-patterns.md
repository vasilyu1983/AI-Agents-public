# RAG Patterns — Best Practices 

*Purpose: Provide operational patterns, checklists, and decision logic for building reliable Retrieval-Augmented Generation pipelines with Agentic RAG and Contextual Retrieval.*

**Modern Update**: Chunk context augmentation and agentic retrieval can improve retrieval on ambiguous corpora, but must be validated on your own test set (see `../../ai-rag/references/contextual-retrieval-guide.md`).

---

## Agentic RAG Pattern (Current Standard)

### Pattern: Dynamic Multi-Step Retrieval

**Old (Static RAG)**:
```text
query → embed → retrieve top-k → inject → generate
```

**New (Agentic RAG)**:
```text
query → plan retrieval → multi-step search → adapt → contextual rerank → cite → generate
```

**Key differences**:
- **Static**: One-shot retrieval, fixed top-k
- **Agentic**: Iterative retrieval, adapts to findings, analyzes intermediate results

**When to use Agentic RAG**:
- Complex multi-domain queries
- Research tasks requiring multiple sources
- Queries needing iterative refinement
- High-accuracy requirements (legal, medical, technical)

**Anthropic's Research System Example**:
```text
Lead agent plans research → Spawns parallel search agents → Each searches independently →
Agents summarize findings → Store in external memory → Retrieve context for synthesis →
Generate final answer with citations
```

---

## Contextual Retrieval (Anthropic 2024)

### Pattern: Context-Enhanced Chunks

**Standard chunking**:
```text
Document → Split into chunks → Embed each chunk → Store
```

**Contextual chunking**:
```text
Document → Split into chunks → Add document context to each chunk → Embed enhanced chunks → Store
```

**Example**:
```text
Original chunk: "Revenue increased 15% QoQ"

Contextual chunk: "In ACME Corp's Q4 2024 financial report, revenue increased 15% QoQ"
```

**Implementation**:
1. Use LLM to generate 50-100 token context prefix for each chunk
2. Prepend context to chunk before embedding
3. Store original chunk + context separately
4. Use context-enhanced embeddings for retrieval
5. Return original chunk (without context) in results

**Validation (REQUIRED)**:
- Compare baseline vs augmented retrieval on a held-out retrieval test set (recall@k, nDCG/MRR, empty-result rate).
- Measure end-to-end impact on groundedness/citation coverage (not only retrieval metrics).

---

## 1. Core RAG Pipeline (Enhanced)

### Pattern: Standard RAG Flow

```
query
→ rewrite
→ embed
→ retrieve
→ rerank
→ filter
→ inject context
→ generate answer
```

**Checklist**

- [ ] Query rewritten when ambiguous.  
- [ ] Embeddings use consistent model/version.  
- [ ] Retrieval uses top-k defined (k=5–20).  
- [ ] Reranker always applied.  
- [ ] Chunks filtered for domain relevance.  
- [ ] Context injected using standard wrapper (below).  

**Injection Format**

```
<retrieved>
[chunk_1]
[chunk_2]
...
</retrieved>
```

**Anti-Patterns**

- AVOID: Generating answers without injected context.  
- AVOID: Using only semantic search for domain-heavy queries.  
- AVOID: Passing unbounded chunks (>1500 tokens).  

---

# 2. Hybrid Retrieval Pattern

### Pattern: Semantic + Keyword Search

```
semantic_k = 20
keyword_k = 20
combine → rerank → filter
```

**Checklist**

- [ ] Keyword retrieval used for structured or fact-heavy data.  
- [ ] Semantic retrieval used for narrative/semantic data.  
- [ ] Deduplicate results before reranking.  

**Decision Tree**

```
Does the user ask for facts, numbers, or strict terms?
→ Yes → Include keyword search
→ No → Semantic-only is acceptable
```

**Anti-Patterns**

- AVOID: Using semantic-only for regulatory or code documentation.  
- AVOID: Not deduplicating overlapping results.  

---

# 3. Query Rewriting

### Pattern: Clarification Rewrite

```
rewrite(query) → high-precision query
```

**Checklist**

- [ ] Expand abbreviations or acronyms.  
- [ ] Add missing domain terms.  
- [ ] Convert vague phrases to explicit intents.  
- [ ] Route to the correct domain before retrieval.  

**Examples**

```
"Summarize finances" → "Summarize Q4 financial statements for ACME Corp."
```

---

# 4. Chunking Strategy

### Pattern: Overlapping Windows

**Parameters**

- Chunk size: 200–400 tokens  
- Overlap: 20–40 tokens  

**Checklist**

- [ ] Do not break sentences across chunks.  
- [ ] Keep domain-consistent content within each chunk.  
- [ ] Store metadata (source, page, section).  

**Anti-Patterns**

- AVOID: Mixing unrelated concepts in a single chunk.  
- AVOID: Using large chunk sizes (>800 tokens).  
- AVOID: Not storing metadata for grounding.  

---

# 5. Reranking Pattern

### Pattern: Second-Stage Reranker

```
retrieve_top_50 → rerank_to_top_5
```

**Checklist**

- [ ] Use cross-encoder / heavy reranker.  
- [ ] Score based on semantic alignment to rewritten query.  
- [ ] Keep top 3–7 only.  

**Anti-Patterns**

- AVOID: Using retriever top-k directly.  
- AVOID: Reranking fewer than 20 candidates.  

---

# 6. Filtering & Relevance Validation

### Pattern: Post-Rerank Filtering

```
for each chunk:
    validate relevance
    validate recency
    validate domain alignment
```

**Checklist**

- [ ] Discard stale or deprecated content.  
- [ ] Ensure domain matches query domain.  
- [ ] Remove near-duplicates.  

**Decision Tree**

```
Is chunk relevant to the final question?
→ No → discard
→ Yes → inject
```

---

# 7. Response Generation Pattern

### Pattern: Evidence-Grounded Answer

```
answer must:
- cite retrieved chunks
- avoid unsupported claims
- reflect only injected evidence
```

**Checklist**

- [ ] Use only retrieved text for factual claims.  
- [ ] Include citations or chunk references.  
- [ ] Summaries must align 1:1 with provided evidence.  

**Anti-Patterns**

- AVOID: Mixing external world knowledge with retrieved facts.  
- AVOID: Adding claims inconsistent with chunks.  

---

# 8. Advanced RAG Techniques

## 8.1 HyDE (Hypothetical Document Embedding)

**Purpose:** When retrieval fails or query sparse.

**Pattern**

```
generate hypothetical_doc
embed hypothetical_doc
retrieve based on hypothetical embedding
```

**Checklist**

- [ ] Hypothetical doc ≤ 150 tokens.  
- [ ] Use domain constraints in generation.  

---

## 8.2 Query Routing

**Pattern**

```
route(query) → domain
domain → index
retrieve(domain-specific)
```

**Checklist**

- [ ] Routing based on classification prompt or rules.  
- [ ] Reject multi-domain injection.  

**Routing Table Example**

| Domain | Trigger Keywords | Index |
|--------|------------------|-------|
| Legal  | statute, case    | legal_idx |
| Code   | function, bug    | code_idx |
| Finance| q4, revenue      | finance_idx |

---

## 8.3 Context Enrichment

### Pattern: Expand With Auxiliary Metadata

```
query → enrich(metadata) → retrieve → rerank → inject
```

**Checklist**

- [ ] Add metadata fields (product ID, region, date).  
- [ ] Remove irrelevant metadata before injection.  

---

## 8.4 Hierarchical Retrieval

**Pattern**

```
retrieve(topic-level)
→ retrieve(section-level)
→ retrieve paragraph-level
```

**Checklist**

- [ ] Escalate retrieval depth only if matches drop.  
- [ ] Keep 1–3 top matches per level.  

---

# 9. Modular RAG Architecture

### Pattern: Clean Separation of Components

**Modules**

- Query Processor  
- Embedder  
- Retriever  
- Reranker  
- Context Filter  
- Generator  

**Checklist**

- [ ] Each module testable independently.  
- [ ] Embedding model is versioned.  
- [ ] Retriever swaps allowed without pipeline redesign.  

---

# 10. Evaluation of RAG Systems

### Pattern: RAG Evaluation Loop

```
query_set → retrieve → judge → score → adjust pipeline
```

**Metrics**

- Retrieval relevance (RR)  
- Grounding score (GS)  
- Answer accuracy (AA)  
- Context precision (CP)  
- Context recall (CR)  

**Checklist**

- [ ] Validate citations exist.  
- [ ] Score grounding separately from correctness.  
- [ ] Detect hallucinations explicitly.  

---

# 11. RAG Anti-Patterns (Master List)

- AVOID: Using retrieval only after answer generation.  
- AVOID: Large chunks with mixed topics.  
- AVOID: No reranking stage.  
- AVOID: Combining multi-domain results without routing.  
- AVOID: Blindly trusting embedding similarity.  
- AVOID: Passing full documents into prompt.  
- AVOID: Using unfiltered retrieval outputs as context.  
- AVOID: Answering without evidence or citations.  

---

# 12. Quick Reference Tables

### Chunk Size Table

| Type of Data | Size (tokens) |
|--------------|----------------|
| Narrative    | 250–350        |
| Technical    | 150–250        |
| Legal/Code   | 100–200        |

### Retrieval Strategy Table

| Query Type | Strategy |
|------------|----------|
| Highly specific | semantic only |
| Fact-heavy | semantic + keyword |
| Sparse query | HyDE |
| Multi-domain | router + domain indexes |

---

# End of File
