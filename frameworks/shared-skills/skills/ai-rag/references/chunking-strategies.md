# Chunking Strategy Selection (Production)

Chunking is a major quality lever in RAG, but **there is no universal best chunk size**. Choose a baseline strategy, then validate against a test set.

**2026 Update**: Semantic chunking is now the enterprise default. Late chunking is gaining traction for relationship-heavy documents.

References:
- RAG paper (https://arxiv.org/abs/2005.11401)
- Failure taxonomy (https://arxiv.org/abs/2401.05856)
- [Chunking strategies comprehensive guide](https://medium.com/@adnanmasood/chunking-strategies-for-retrieval-augmented-generation-rag-a-comprehensive-guide-5522c4ea2a90)
- [Semantic boundaries reduce RAG errors 60%](https://ragaboutit.com/the-chunking-strategy-shift-why-semantic-boundaries-cut-your-rag-errors-by-60/)

---

## 1. Baseline Decision Rule (Start Simple)

```text
What are you chunking?
    ├─ Structured documents (PDFs with pages/sections)?
    │   └─ Prefer structure-aware chunking (page/section boundaries + metadata)
    │
    ├─ Technical docs / Markdown / API refs?
    │   └─ Prefer header-aware chunking (H1/H2/H3 boundaries + code fences)
    │
    ├─ Source code?
    │   └─ Prefer syntax-aware chunking (symbols, functions, classes) + file path metadata
    │
    └─ Unstructured text?
        └─ Start with fixed-size token chunks + overlap, then tune
```

---

## 2. Strategy Table (Operational Defaults)

| Content type | Recommended baseline | Key metadata | Common pitfalls |
|-------------|----------------------|--------------|-----------------|
| PDFs/reports | Page/section boundaries | source id, page, section | losing page refs; OCR noise |
| Technical docs | Header-aware (sections) | source id, heading path | splitting code blocks; losing anchors |
| Code | Syntax-aware (symbols) | repo, path, symbol, commit | mixing files; missing imports/context |
| Tables | Convert to row/column text | table id, row/col, units | losing units; flattening joins |
| Emails/chats | Message-aware | thread id, author, timestamp | mixing threads; missing chronology |

---

## 3. Validation Protocol (REQUIRED)

### Build a chunking test set

- 50–200 queries representative of production traffic.
- For each query, record:
  - expected sources (doc IDs, sections, pages)
  - unacceptable sources (near-miss docs that are commonly retrieved but wrong)

### Measure retrieval separately from generation

- Retrieval metrics: recall@k, nDCG/MRR, empty-result rate, latency.
- Generation metrics: citation coverage, groundedness/faithfulness, refusal correctness.

### Iterate with one variable at a time

- Change only chunking (hold embedder/index/reranker constant), re-run test set, then decide.

---

## 4. Anti-Patterns (AVOID)

- Over-chunking (tiny chunks): high recall but poor synthesis and high latency.
- Under-chunking (huge chunks): high cost and more irrelevant context.
- Dropping structure metadata: no stable citations and poor debugging.
- Mixing tenants/corpora without ACL metadata: security and correctness failures.

---

## 5. Semantic Chunking (2026 Enterprise Default)

**What it is**: Split documents at semantically meaningful boundaries by comparing sentence embeddings, not arbitrary token counts.

**Why it matters**: IBM research shows 20-30% reduction in irrelevant retrieval vs fixed-size. Enterprise adoption accelerated in 2025-2026.

### How It Works

```text
Semantic Chunking Pipeline:
  1. Split document into sentences
  2. Generate embedding for each sentence
  3. Calculate similarity between adjacent sentences
  4. Identify breakpoints where similarity drops significantly
  5. Group sentences between breakpoints into chunks
```

### Boundary Detection Methods

| Method | Logic | Best For |
|--------|-------|----------|
| **Percentile-based** | Split when similarity < Nth percentile | General use, stable |
| **Standard deviation** | Split when similarity > N std devs below mean | Documents with clear topic shifts |
| **Interquartile (IQR)** | Split using IQR outlier detection | Robust to noisy embeddings |
| **Max-Min** | Novel algorithm optimizing semantic coherence | Research shows AMI scores of 0.85-0.90 |

### Cost Considerations

Semantic chunking has hidden costs:
- **Embedding computation**: Generate embeddings for every sentence to detect boundaries
- **Ingestion overhead**: 15-40% longer ingestion time vs fixed-size
- **API costs**: For 1GB dataset, can mean millions of embedding calls

**Recommendation**: Use for high-value corpora where retrieval quality justifies cost. For large, low-value corpora, fixed-size may be more practical.

### Implementation Libraries

| Library | Approach | Notes |
|---------|----------|-------|
| **LangChain SemanticChunker** | Percentile/std-dev/IQR methods | Easy integration |
| **LlamaIndex SemanticSplitterNodeParser** | Configurable boundaries | Production-ready |
| **Chonkie** | Multiple strategies including semantic | Optimized for different doc types |

---

## 6. Late Chunking (Emerging 2026)

**What it is**: Embed the full document first (preserving context), then chunk the embeddings. Opposite of traditional "chunk then embed."

**Why it matters**: Solves the "relationship problem" where meaning depends on surrounding sections. The "only if" clause on page 3 that modifies the statement on page 1.

### Traditional vs Late Chunking

```text
Traditional (Chunk-Then-Embed):
  Document → Split into chunks → Embed each chunk independently
  Problem: Each chunk loses context from the rest of the document

Late Chunking (Embed-Then-Chunk):
  Document → Embed full document (model sees everything) →
  Split embeddings into chunks (preserving contextual understanding)
  Benefit: Each chunk embedding "knows" about the whole document
```

### When to Use Late Chunking

**Good candidates**:
- Legal contracts (clauses reference each other)
- Technical specifications (definitions on page 1, usage throughout)
- Research papers (methods section context needed for results)
- Policy documents (exceptions and conditions scattered)

**Poor candidates**:
- Independent FAQ entries
- Product descriptions (self-contained)
- News articles (mostly self-contained paragraphs)

### Trade-offs

| Aspect | Late Chunking | Contextual Retrieval (Anthropic) |
|--------|---------------|----------------------------------|
| Context preservation | Via embedding | Via prepended text summary |
| Computational cost | High (full doc embedding) | Medium (LLM summary per chunk) |
| Retrieval relevance | Better for relationship-heavy docs | Better for isolated facts |
| Implementation complexity | Requires compatible embedding model | Works with any embedder |

### Implementation

```python
# Conceptual example - Chonkie library
from chonkie import LateChunker

chunker = LateChunker(
    embedding_model="sentence-transformers/all-MiniLM-L6-v2",
    chunk_size=512,
    # Model processes full document before chunking
)

chunks = chunker.chunk(document_text)
# Each chunk embedding has full document context
```

**Library**: [Chonkie](https://github.com/bhavnicksm/chonkie) - Built around the idea that chunking is not one generic operation.

---

## 7. Chunking Strategy Decision Tree (2026)

```text
Choosing a chunking strategy:
  │
  ├─ Document structure?
  │   ├─ Strong structure (headers, sections) → Structure-aware chunking
  │   ├─ Code → Syntax-aware chunking
  │   └─ Unstructured prose → Continue below
  │
  ├─ Relationship density?
  │   ├─ High (legal, specs, cross-references) → Late chunking or Contextual Retrieval
  │   └─ Low (independent paragraphs) → Continue below
  │
  ├─ Retrieval quality critical?
  │   ├─ Yes (high-stakes domain) → Semantic chunking
  │   └─ No (general use) → Fixed-size with overlap
  │
  └─ Cost constraints?
      ├─ Tight budget → Fixed-size (cheapest)
      └─ Quality over cost → Semantic + reranking
```

---

## 8. Implementation Examples

See `../assets/chunking/`:
- `../assets/chunking/template-basic-chunking.md`
- `../assets/chunking/template-code-chunking.md`
- `../assets/chunking/template-long-doc-chunking.md`
