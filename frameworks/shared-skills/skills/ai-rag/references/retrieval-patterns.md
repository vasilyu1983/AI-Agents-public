# Retrieval Patterns for RAG Systems

A library of operational retrieval architectures for high-quality RAG pipelines.

---

## 1. Retrieval Pipeline Blueprint

1. Query preprocessing  
2. Embedding generation  
3. ANN vector search  
4. Optional: hybrid lexical + dense search  
5. Optional: reranking  
6. Context packaging  

---

## 2. Query Preprocessing Patterns

### Steps

- Normalize whitespace  
- Lowercase (unless case-sensitive domain)  
- Remove markdown/HTML  
- Optional: LLM-based query rewriting  

**Checklist**

- [ ] Preprocessing deterministic  
- [ ] Matches embedding model's expectations

---

## 3. Dense Retrieval Pattern

### Use when

- Queries are semantic  
- Synonyms matter  
- Content varies by vocabulary  

### Steps

1. Embed query  
2. Search ANN index (HNSW, IVF, ScaNN)  
3. Retrieve top K=5–20  
4. Return chunks + metadata  

**Checklist**

- [ ] Same embedding model for docs & queries  
- [ ] Vector normalization consistent  
- [ ] K validated  

---

## 4. Hybrid Retrieval Pattern (Lexical + Dense)

Use when documents include both **structured semantic** and **keyword-heavy** text.

### Fusion methods

- Weighted sum (α*bm25 + β*sim)  
- Reciprocal Rank Fusion (RRF)  
- Score scaling  

### Pipeline

1. BM25 retrieve K=20  
2. Dense retrieve K=20  
3. Merge + fuse ranking  
4. Keep top N=5–10  

---

## 5. Retrieval Optimization Pattern

**Use when retrieval returns irrelevant documents.**

### Optimization Strategies

1. **Tune K**
   - Start with 5, try 8, 10, 15
   - Evaluate precision/recall trade-off
   - Monitor relevance at different K values

2. **Query Expansion**
   - Add synonyms
   - Reformulate query with LLM
   - Generate multiple query variants

3. **Metadata Filters**
   - Restrict by document type, date, topic
   - Apply domain-specific constraints
   - Use hierarchical filtering

4. **Hybrid Search**
   - Combine BM25 + vectors
   - Weighted blending (α*bm25 + β*sim)
   - Reciprocal Rank Fusion (RRF)

5. **Index Parameters**
   - Increase ef_search / nprobe for higher recall
   - Trade latency for quality when needed
   - Benchmark parameter changes

### Retrieval Debugging Checklist

- [ ] K validated via evaluation
- [ ] Metadata filters tested
- [ ] Hybrid search tested
- [ ] Index parameters tuned
- [ ] Precision/recall measured

---

## 6. Reranking Workflow (Modern Best Practice)

**Use when retrieval results are noisy.**

Modern cross-encoder reranking drastically improves accuracy with minimal overhead.

### Recommended Approach

1. Retrieve **K=20–50** candidates (broad initial retrieval)
2. Apply cross-encoder reranker:
   - **ms-marco-TinyBERT-L-2-v2** (4.3M params, outperforms larger models)
   - BGE Reranker (BAAI)
   - Cohere Rerank-3 (API-based)
   - Jina Reranker
3. Select top N=3–5 for context

### Why Cross-Encoders

- Higher accuracy than bi-encoders for ranking
- TinyBERT achieves state-of-the-art with only 4.3M parameters
- Latency: 10-50ms per query (acceptable for most applications)
- Significantly better than increasing K alone

### Performance Comparison

| Approach | Relevance | Latency | Notes |
|----------|-----------|---------|-------|
| Vector only (K=5) | Baseline | 10ms | Fast but may miss relevant docs |
| Vector only (K=20) | +15% | 15ms | Better recall, more noise |
| Vector + Reranking | +60% | 30-60ms | Best quality/speed trade-off |

### Reranking Integration Checklist

- [ ] Cross-encoder chosen (TinyBERT recommended for speed/accuracy)
- [ ] Reranking latency measured (<100ms target)
- [ ] Top N size tuned (3-5 for generation)
- [ ] Verified relevance improvement (A/B test against no reranking)
- [ ] Fallback strategy if reranker fails

---

## 7. Metadata-Filtered Retrieval

Use for domain-specific filtering:

- Document type
- Department / team
- Source system
- Timestamp range

**Checklist**

- [ ] Metadata indexed
- [ ] Filters reduce noise without harming recall

---

## 8. Multi-Document Retrieval Pattern

For questions needing multi-part reasoning.

### Steps

1. Retrieve many (K=50+)  
2. Rerank  
3. Package top N=3–7  
4. Insert hierarchical context blocks  

---

## 9. Query Rewriting Pattern (LLM-Assisted)

Use to fix poor queries or abstract queries.

### Techniques

- Expand synonyms
- Reformulate into answerable queries
- Remove ambiguity

**Checklist**

- [ ] No hallucinated domain drift
- [ ] Improved recall validated

---

## 10. Late Interaction Retrieval (ColBERT)

**2026 Update**: ColBERT and late interaction models have matured significantly. RAGatouille library enables easy integration. ECIR 2026 workshop dedicated to late interaction research.

### What is Late Interaction?

Traditional dense retrieval: Query → single vector, Document → single vector, compute similarity.

Late interaction: Query → **multiple token vectors**, Document → **multiple token vectors**, compute token-level similarities and aggregate.

```text
Traditional Dense Retrieval:
  Query: "best RAG practices" → [0.2, 0.5, ...] (single vector)
  Document → [0.3, 0.4, ...] (single vector)
  Score = cosine_similarity(query_vec, doc_vec)

Late Interaction (ColBERT):
  Query: "best RAG practices" → [[0.1, ...], [0.2, ...], [0.3, ...], [0.4, ...]] (per-token)
  Document → [[0.2, ...], [0.3, ...], ...] (per-token)
  Score = MaxSim aggregation over token pairs
```

### Why ColBERT Outperforms Dense

| Aspect | Dense Retrieval | ColBERT Late Interaction |
|--------|-----------------|--------------------------|
| Representation | Compress entire text to single vector | Preserve per-token semantics |
| Precision | Information loss in compression | Fine-grained matching |
| Generalization | Struggles on OOD queries | Strong zero-shot transfer |
| Best for | Simple semantic similarity | Complex, technical queries |

### ColBERT Variants (2026)

| Model | Parameters | Strength | Use Case |
|-------|------------|----------|----------|
| **ColBERTv2** | 110M | Centroid-residual compression (10x smaller index) | Production at scale |
| **ColPali** | VLM-based | Multimodal (PDF → image) | Document retrieval without OCR |
| **ColQwen** | VLM-based | Chinese + multimodal | Multilingual visual retrieval |
| **JaColBERT** | 110M | Japanese-optimized | Japanese document search |

### RAGatouille Implementation

[RAGatouille](https://github.com/AnswerDotAI/RAGatouille) - Bridge between research and practical RAG pipelines.

```python
# Conceptual example - RAGatouille
from ragatouille import RAGPretrainedModel

# Load ColBERTv2
RAG = RAGPretrainedModel.from_pretrained("colbert-ir/colbertv2.0")

# Index documents
RAG.index(
    collection=documents,
    index_name="my_index",
    max_document_length=512,
    split_documents=True
)

# Search with late interaction
results = RAG.search(query="RAG evaluation best practices", k=10)
```

### When to Use Late Interaction

**Good candidates**:

- Legal/compliance search (precise terminology matching)
- Technical documentation (exact API/method names matter)
- Academic/research retrieval (specialized vocabulary)
- Financial document analysis (specific figures, dates)

**May be overkill for**:

- General Q&A with conversational queries
- Simple FAQ lookup
- Short document collections (<10K docs)

### ColPali: Multimodal Late Interaction

**Problem**: Traditional RAG requires OCR + chunking for PDFs. OCR errors propagate.

**ColPali solution**: Treat PDF pages as images, apply vision-language model with late interaction.

```text
ColPali Pipeline:
  1. PDF → Page images (no OCR)
  2. VLM encodes each page → per-patch token embeddings
  3. Query → token embeddings
  4. MaxSim matching between query tokens and page patches
  5. Retrieve top pages by visual-semantic similarity
```

**Best for**: Scanned documents, forms, diagrams, tables, charts where OCR fails.

### Late Interaction Checklist

- [ ] Evaluated ColBERT vs dense on your query distribution
- [ ] Index size acceptable (ColBERTv2 compression helps)
- [ ] Latency within budget (typically 20-100ms)
- [ ] RAGatouille or equivalent library integrated
- [ ] For PDFs: considered ColPali vs OCR pipeline
- [ ] Reranking still beneficial on top of ColBERT (cross-encoder)

---

## 11. Retrieval Strategy Decision Tree (2026)

```text
Choosing retrieval approach:
  │
  ├─ Query type?
  │   ├─ Simple semantic → Dense retrieval (fastest)
  │   ├─ Keyword + semantic mix → Hybrid (BM25 + dense)
  │   └─ Technical/precise terminology → Late interaction (ColBERT)
  │
  ├─ Document type?
  │   ├─ Text-only → Dense or hybrid
  │   ├─ PDFs with tables/diagrams → ColPali or structured extraction
  │   └─ Code → Syntax-aware + dense
  │
  ├─ Corpus size?
  │   ├─ <100K docs → ColBERT viable (higher quality)
  │   ├─ 100K-10M → Dense + reranking (balanced)
  │   └─ >10M → Dense with IVF/ScaNN (scale)
  │
  └─ Quality requirements?
      ├─ Approximate OK → Dense only
      ├─ High precision needed → Add reranking
      └─ Mission-critical → ColBERT + cross-encoder rerank
```

---

## Related Resources

- [Index Selection Guide](index-selection-guide.md) - Vector DB configuration
- [Hybrid Fusion Patterns](hybrid-fusion-patterns.md) - BM25 + dense fusion
- [Query Rewriting Patterns](query-rewriting-patterns.md) - LLM-assisted query improvement
- [Contextual Retrieval Guide](contextual-retrieval-guide.md) - Anthropic's chunk context technique  
