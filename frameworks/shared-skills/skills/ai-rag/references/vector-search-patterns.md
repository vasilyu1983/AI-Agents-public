# Vector Search Patterns

Operational patterns for dense retrieval using embeddings and ANN indexes.

---
## Table of Contents

- [When to Use Dense Vector Retrieval](#when-to-use-dense-vector-retrieval)
- [Pattern 1: Embedding Model Selection](#pattern-1-embedding-model-selection)
- [Decision Rules](#decision-rules)
- [Evaluation](#evaluation)
- [Pattern 2: Embedding Pipeline](#pattern-2-embedding-pipeline)
- [Preprocessing Steps](#preprocessing-steps)
- [Embedding Generation](#embedding-generation)
- [Storage Pattern](#storage-pattern)
- [Pattern 3: ANN Index Selection](#pattern-3-ann-index-selection)
- [Decision Tree](#decision-tree)
- [HNSW Pattern (General Purpose)](#hnsw-pattern-general-purpose)
- [IVF Pattern (Large Collections)](#ivf-pattern-large-collections)
- [ScaNN Pattern (High Dimensional)](#scann-pattern-high-dimensional)
- [Pattern 3b: Embedding Quantization](#pattern-3b-embedding-quantization)
- [Quantization Ladder](#quantization-ladder)
- [Binary Quantization](#binary-quantization)
- [Scalar Quantization](#scalar-quantization)
- [Two-Phase Retrieval (Rescore Pattern)](#two-phase-retrieval-rescore-pattern)
- [Matryoshka Dimension Reduction](#matryoshka-dimension-reduction)
- [Pattern 4: Retrieval Workflow](#pattern-4-retrieval-workflow)
- [Practitioner Baseline: Manual Similarity Before ANN](#practitioner-baseline-manual-similarity-before-ann)
- [Similarity Geometry Traps](#similarity-geometry-traps)
- [Basic Retrieval](#basic-retrieval)
- [With Metadata Filtering](#with-metadata-filtering)
- [Pattern 5: Monitoring & Drift Detection](#pattern-5-monitoring--drift-detection)
- [Embedding Drift](#embedding-drift)
- [Vector Search Quality Checklist](#vector-search-quality-checklist)


## When to Use Dense Vector Retrieval

Use dense vector search when:
- Meaning matters more than exact keyword matching
- Semantic similarity is critical
- Documents use varied terminology
- Cross-language retrieval needed
- Handling paraphrased or conceptually similar queries

---

## Pattern 1: Embedding Model Selection

### Decision Rules

**Choose embedding model based on:**

#### Domain Fit

- **Technical docs** → Code-specific embeddings (CodeBERT, GraphCodeBERT)
- **Legal/medical** → Domain models (Legal-BERT, BioBERT, PubMedBERT)
- **General semantic search** → Sentence-transformer or LLM embedding (all-MiniLM, E5, OpenAI)
- **Multilingual** → Multilingual models (multilingual-e5, LaBSE, mBERT)

#### Performance Characteristics

| Model Type | Dimensions | Use Case | Speed | Quality |
|------------|-----------|----------|-------|---------|
| Small (BERT-mini) | 384 | High-throughput apps | Fast | Good |
| Medium (all-MiniLM-L6) | 384-768 | Balanced performance | Medium | Very Good |
| Large (E5-large) | 1024 | Quality-critical apps | Slow | Excellent |
| LLM embeddings (OpenAI) | 1536-3072 | Maximum quality | Slow | Best |

#### Dimensionality Trade-offs

- **< 768 dims**: Good for speed, lower memory footprint
- **1024-1536 dims**: Balanced accuracy/performance
- **> 4096 dims**: Highest accuracy, consider dimension reduction or ScaNN

### Evaluation

```python
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

def evaluate_embedding_model(model_name, test_pairs):
    """
    Test embedding quality on domain-specific pairs
    """
    model = SentenceTransformer(model_name)

    scores = []
    for query, positive_doc, negative_doc in test_pairs:
        query_emb = model.encode(query)
        pos_emb = model.encode(positive_doc)
        neg_emb = model.encode(negative_doc)

        pos_score = cosine_similarity([query_emb], [pos_emb])[0][0]
        neg_score = cosine_similarity([query_emb], [neg_emb])[0][0]

        # Should be: positive score > negative score
        scores.append(pos_score > neg_score)

    accuracy = sum(scores) / len(scores)
    return accuracy
```

**Checklist**
- [ ] Model chosen based on domain + cost
- [ ] Dimensionality known and documented
- [ ] Evaluated on domain-specific test pairs
- [ ] Same embedding model used for query + index
- [ ] Model version tracked and logged

---

## Pattern 2: Embedding Pipeline

### Preprocessing Steps

```python
def preprocess_text(text):
    """
    Clean text before embedding
    """
    import re

    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text)

    # Remove markup (if applicable)
    text = re.sub(r'<[^>]+>', '', text)

    # Truncate to model's max length (most models: 512 tokens)
    max_length = 512
    tokens = text.split()
    if len(tokens) > max_length:
        text = ' '.join(tokens[:max_length])

    return text.strip()
```

### Embedding Generation

Three invariants regardless of library:

- always **L2-normalize** embeddings; cosine similarity becomes dot product
- always pin **`model_version`** alongside the vector — required for the
  shadow-column migration pattern when you change models
- always pass query and document text through the **same preprocessing**

```python
from sentence_transformers import SentenceTransformer

class EmbeddingPipeline:
    def __init__(self, model_name='all-MiniLM-L6-v2'):
        self.model = SentenceTransformer(model_name)
        self.model_name = model_name

    def embed_documents(self, documents):
        """
        Generate embeddings for documents
        """
        embeddings = []

        for doc in documents:
            # Preprocess
            clean_text = preprocess_text(doc['text'])

            # Encode
            embedding = self.model.encode(
                clean_text,
                normalize_embeddings=True  # L2 normalization
            )

            embeddings.append({
                'doc_id': doc['doc_id'],
                'text': doc['text'],
                'embedding': embedding.tolist(),
                'metadata': doc.get('metadata', {}),
                'model_version': self.model_name
            })

        return embeddings
```

For the canonical `documents / chunks / embeddings` Postgres schema (with
`model_id` shadow column for safe model migration), see
`frameworks/shared-skills/skills/ai-vector-brain/assets/sql/001_schema.sql`.

### Storage Pattern

Store these fields for each document:
- **Vector** (embedding)
- **Raw text** (original document)
- **Metadata** (source, tags, timestamp, language)
- **Model version** (for tracking)

**Checklist**
- [ ] Text preprocessing consistent across indexing & querying
- [ ] Embeddings deterministic (same input → same output)
- [ ] Same model used for indexing & querying
- [ ] Metadata stored with vectors
- [ ] Model version tracked

---

## Pattern 3: ANN Index Selection

### Decision Tree

**Dataset size < 100k** → **Flat index** (exact search, no approximation)

**Dataset 100k–10M** → **HNSW** (best performer in ANN benchmarks)
- Parameters: `M` (graph degree), `ef_search`, `ef_construction`
- Best for: Low-latency applications, metadata filtering

**Dataset > 10M** → **IVF / ScaNN / DiskANN** (billion-scale)
- Parameters: `nlist` (clusters), `nprobe` (search clusters)
- Best for: Very large corpora, GPU acceleration (ScaNN)

**Need filtering (metadata)** → **HNSW or specialized vector DB**
- Weaviate, Qdrant, Milvus, Vespa

### HNSW Pattern (General Purpose)

**Concept:** HNSW builds a hierarchical proximity graph where higher layers are
sparse "highways" and lower layers are dense neighborhoods. Search descends
greedily, expanding `ef_search` candidates at each level. Recall and latency
are tuned per-query at search time; build cost is paid once.

**Implementation boundary:** this skill explains HNSW tradeoffs only. Do not
copy standalone library code from here. Operational index DDL, loader scripts,
and backend-specific examples live in `ai-vector-brain`.

For HNSW inside Postgres (DDL, per-session `ef_search`, `halfvec` for
>2000-dim, `iterative_scan` for filtered queries), see
`frameworks/shared-skills/skills/ai-vector-brain/assets/sql/002_indexes_hnsw.sql`.

**Parameter Guidelines:**

| Parameter | Range | Use Case |
|-----------|-------|----------|
| M | 8-64 | 16 for balanced, 32+ for high quality |
| ef_construction | 100-500 | 200 for balanced build time/quality |
| ef_search | 10-500 | 50 for 95%+ recall, 100+ for 99% |

**Checklist**
- [ ] M chosen based on quality requirements
- [ ] ef_construction tuned during index build
- [ ] ef_search tuned for recall/latency tradeoff
- [ ] Recall@k measured on eval set (target: >95%)

---

### IVF Pattern (Large Collections)

**Concept:** IVF partitions the vector space into `nlist` Voronoi cells via
k-means; search visits only `nprobe` nearest cells. Trades recall for speed
linearly in `nprobe`. Requires a training pass on a representative sample.

**Implementation boundary:** IVF setup is backend-specific and belongs in the
serving stack's implementation docs, not this theory skill. Capture `nlist`,
`nprobe`, training sample size, and recall/latency deltas in eval results.

In Postgres, IVFFlat is rarely the right choice today — pgvector's HNSW or
**pgvectorscale's StreamingDiskANN** outperform it on both recall and latency
for the corpus sizes IVF used to win at. Treat IVF as a legacy pattern unless
you are operating outside Postgres on a billion-scale corpus.

**Parameter Guidelines:**

| Dataset Size | nlist | nprobe | Notes |
|--------------|-------|--------|-------|
| 1M-10M | 1024 | 16-32 | Balanced |
| 10M-100M | 4096 | 32-64 | Larger clusters |
| >100M | 16384 | 64-128 | Billion-scale |

**Checklist**
- [ ] Index trained on representative sample
- [ ] nlist sized appropriately for dataset
- [ ] nprobe tuned for recall/latency
- [ ] Reindexing schedule defined (< weekly for changing corpora)

---

### ScaNN Pattern (High Dimensional)

**Use when:**
- Embeddings > 768 dimensions
- GPU acceleration available
- Need maximum throughput

**Concept:** ScaNN combines tree-based partitioning with anisotropic vector
quantization (penalizes quantization error along directions that matter for
inner-product) and a rescoring pass. Best on high-dimension vectors where
quantization error otherwise dominates.

Implementation is stack-specific. Record the tree partition count,
leaves-to-search, quantization settings, and rerank count in eval notes rather
than keeping runnable serving code in this reference.

ScaNN lives outside Postgres — consider it only when you have ruled out
pgvector HNSW + halfvec and pgvectorscale. For the in-Postgres path, see
`ai-vector-brain/references/backend-selection.md`.

---

## Pattern 3b: Embedding Quantization

Reduce vector memory footprint without changing the embedding model or index algorithm. Quantization is orthogonal to index choice — apply it on top of HNSW, IVF, or flat indexes.

### Quantization Ladder

| Technique | Compression | Bits per dim | Distance metric | Accuracy loss | Best for |
|-----------|-------------|-------------|-----------------|---------------|----------|
| **None (float32)** | 1x | 32 | Cosine, L2, dot | Baseline | Small corpora, max accuracy |
| **Scalar (int8)** | 4x | 8 | Same as original | Minimal (~1-2%) | Medium corpora, easy win |
| **Product (PQ)** | 8-32x | 1-4 (codebook) | Asymmetric distance | Moderate (~3-5%) | Billion-scale, GPU-friendly |
| **Binary** | 32x | 1 | Hamming | High without rescore; low with rescore (~4%) | Large corpora with rescore budget |

**Decision rule**: Start with scalar quantization. Move to binary only when memory is the binding constraint and you can afford a rescore pass.

### Binary Quantization

Convert float32 embeddings to single-bit vectors. Each dimension becomes 1 if positive, 0 otherwise. Search uses Hamming distance (XOR + popcount, ~2 CPU cycles).

```python
import numpy as np

def binary_quantize(embeddings: np.ndarray) -> np.ndarray:
    """
    Convert float32 embeddings to binary.
    Input:  (N, D) float32 array, L2-normalized
    Output: (N, D) uint8 array of 0s and 1s
    """
    return (embeddings > 0).astype(np.uint8)


def hamming_distance(a: np.ndarray, b: np.ndarray) -> int:
    """Count differing bits between two binary vectors."""
    return np.sum(a != b)
```

**Requirements:**
- Embeddings **must** be L2-normalized before quantization (the sign boundary must be meaningful)
- Models trained with cosine similarity work best — dot-product-only models may lose more accuracy
- Works with any vector DB that supports binary indexes (Milvus, Qdrant, Weaviate, MongoDB Atlas)

**Production adoption:** Perplexity (search index), Azure AI Search, HubSpot (AI assistant), MongoDB Atlas Vector Search.

### Scalar Quantization

Convert float32 to int8 per dimension. Simpler than binary, retains distance metric compatibility.

```python
import numpy as np

def scalar_quantize(embeddings: np.ndarray) -> np.ndarray:
    """
    Quantize float32 embeddings to int8.
    Uses min-max scaling per dimension across the corpus.
    """
    mins = embeddings.min(axis=0)
    maxs = embeddings.max(axis=0)
    scale = maxs - mins
    scale[scale == 0] = 1  # avoid division by zero

    normalized = (embeddings - mins) / scale  # [0, 1]
    quantized = (normalized * 255).astype(np.uint8)
    return quantized, mins, scale  # store mins/scale for query quantization
```

**Use when:** You want a 4x memory win with minimal code change and no accuracy-recovery step.

### Two-Phase Retrieval (Rescore Pattern)

Binary and PQ quantization lose accuracy. Recover it with a two-phase search:

1. **Broad retrieval** — search compressed index for top-N candidates (N >> k, e.g. 100-500)
2. **Rescore** — recompute exact distance on original float32 vectors for the N candidates, return top-k

```python
def two_phase_search(query_embedding, binary_index, float_store, k=5, oversample=100):
    """
    Phase 1: Fast Hamming search on binary index
    Phase 2: Exact cosine rescore on float32 vectors
    """
    # Phase 1: binary search
    query_binary = binary_quantize(query_embedding.reshape(1, -1))
    candidate_ids, _ = binary_index.search(query_binary, oversample)

    # Phase 2: rescore with full-precision vectors
    candidate_vectors = np.array([float_store[cid] for cid in candidate_ids[0]])
    scores = candidate_vectors @ query_embedding  # dot product (assumes normalized)

    top_k_idx = np.argsort(scores)[-k:][::-1]
    return [(candidate_ids[0][i], scores[i]) for i in top_k_idx]
```

**Oversample ratio:** Start at 10-20x k. Tune by measuring recall@k against exact search.

**Storage implication:** You need both the compressed index (for Phase 1) and the original float32 vectors (for Phase 2). Total memory = compressed index + float32 store. The float32 store can live on disk or in a separate column — it's only read for N candidates, not scanned.

### Matryoshka Dimension Reduction

Some newer embedding models (e.g. `nomic-embed-text-v1.5`, OpenAI `text-embedding-3-*`) support **Matryoshka representation learning** — the first M dimensions of the full D-dimensional vector are independently useful. This gives a dimension-reduction lever orthogonal to quantization.

```python
# Truncate embeddings to first M dimensions
def matryoshka_truncate(embeddings: np.ndarray, target_dim: int) -> np.ndarray:
    """Truncate to first target_dim dimensions. Re-normalize after."""
    truncated = embeddings[:, :target_dim]
    norms = np.linalg.norm(truncated, axis=1, keepdims=True)
    return truncated / norms
```

**Combine with quantization:** Truncate dimensions first, then quantize. A 1024-dim model truncated to 256 dims + binary quantization = 256 bits per vector (vs. 32,768 bits original). That's a **128x** compression.

**Checklist:**
- [ ] Verify embedding model supports Matryoshka (check model card)
- [ ] Benchmark recall at 2-3 truncation levels on your eval set before deploying
- [ ] Re-normalize after truncation
- [ ] Combine with scalar or binary quantization for maximum compression

---

## Pattern 4: Retrieval Workflow

The retrieval workflow has three logical phases — **embed query → ANN search →
hydrate results**. Each phase has tradeoffs:

- **Embed query** — same preprocessing and same model as indexing time. A
  silent mismatch here is the #1 reason retrieval looks broken.
- **ANN search** — tune `ef_search` (HNSW) or `nprobe` (IVF) per query class
  rather than globally. Long-tail queries often need a higher recall budget.
- **Hydrate results** — never trust the score field as a calibrated
  probability. Treat it as an opaque ordering signal; do thresholding only
  after a reranker.

### Practitioner Baseline: Manual Similarity Before ANN

Before choosing HNSW, IVF, DiskANN, or a managed vector database, build a tiny
exact-search baseline:

1. Select 20-100 representative source items.
2. Generate embeddings with the same preprocessing planned for production.
3. Compute cosine similarity or dot product in process.
4. Print top-k results with source IDs, titles, and scores.
5. Hand-label whether each result is relevant, adjacent, duplicate, or wrong.

This baseline is not production architecture. It is a geometry and data-quality
debugger. If exact search over a small corpus produces bad neighbors, an ANN
index will only return the same bad neighborhood faster. Fix source selection,
retrieval units, preprocessing, or embedding model before adding index
complexity.

Use the baseline to answer:

- Does the embedder capture the domain vocabulary?
- Are query and document texts normalized the same way?
- Are duplicates crowding top-k?
- Is lexical recall still needed for product names, code symbols, acronyms, or
  policy clauses?
- Are score differences meaningful enough to support thresholds?

### Similarity Geometry Traps

Vector search borrows geometric language, but geometry is not grounding.

- **Direction is not truth.** Cosine similarity says two vectors point in a
  similar direction; it does not prove that the chunk answers the question.
- **Magnitude policy must be explicit.** If embeddings are not normalized, dot
  product mixes direction with vector length. If they are normalized, dot
  product and cosine ranking are equivalent.
- **Orthogonal is not always irrelevant.** In high-dimensional embedding space,
  a useful exact identifier or rare term can be weakly represented in the
  semantic direction. Keep lexical recall in hybrid systems.
- **Chunk size is a smoothing domain.** Large chunks blur local signal the same
  way a broad smoothing window blurs a field. If evals show near misses or
  vague citations, reduce the unit size, switch to parent-child retrieval, or
  use typed knowledge packets.
- **Similarity scores are not comparable across model or preprocessing changes.**
  Re-run evals when dimensions, normalization, tokenization, or model version
  changes.

### Basic Retrieval

```python
def vector_search(query, index, embedding_model, k=10):
    """
    Standard vector search
    """
    # 1. Embed query
    query_vector = embedding_model.encode(query, normalize_embeddings=True)

    # 2. Vector search
    distances, indices = index.search(query_vector.reshape(1, -1), k=k)

    # 3. Fetch documents
    results = []
    for i, idx in enumerate(indices[0]):
        results.append({
            'doc_id': doc_store[idx]['doc_id'],
            'text': doc_store[idx]['text'],
            'score': 1 - distances[0][i],  # Convert distance to similarity
            'metadata': doc_store[idx]['metadata']
        })

    return results
```

### With Metadata Filtering

Naïve "fetch top-k vectors then filter" silently undercounts when the filter
is selective — you may filter every candidate away. Two correct patterns:

1. **Pre-filter, then search.** Apply the filter as a candidate constraint
   before the ANN call. In pgvector, set `hnsw.iterative_scan='relaxed_order'`
   so the index walks until enough rows pass the filter; otherwise use a
   partial index keyed on the filter column.
2. **Over-fetch then filter.** Fetch `k * oversample` candidates, apply the
   filter in app code, return the first `k`. Choose the oversample empirically
   — usually 3–10x is enough; if the filter is highly selective, prefer
   pattern 1.

```python
def vector_search_with_filter(query, index, filters, k=10):
    """
    Vector search with metadata filters (over-fetch + filter pattern)
    """
    query_vector = embedding_model.encode(query)

    # Search larger K for filtering
    distances, indices = index.search(query_vector.reshape(1, -1), k=k*3)

    # Filter by metadata
    filtered_results = []
    for i, idx in enumerate(indices[0]):
        doc = doc_store[idx]

        # Apply filters
        if matches_filters(doc['metadata'], filters):
            filtered_results.append({
                'doc_id': doc['doc_id'],
                'text': doc['text'],
                'score': 1 - distances[0][i],
                'metadata': doc['metadata']
            })

            if len(filtered_results) >= k:
                break

    return filtered_results
```

For the runnable hybrid retrieval function with filters baked into SQL (the
pre-filter pattern), see
`ai-vector-brain/assets/sql/003_hybrid_search_function.sql`.

**Checklist**
- [ ] K validated for task (typical: 5-20)
- [ ] Metadata filters tested
- [ ] Hybrid search tested (BM25 + vector)
- [ ] Reranking integrated for top results
- [ ] Embedding drift monitored

---

## Pattern 5: Monitoring & Drift Detection

### Embedding Drift

Monitor when embeddings change due to:
- Model updates
- Data distribution shifts
- Query pattern changes

```python
def detect_embedding_drift(old_embeddings, new_embeddings, threshold=0.1):
    """
    Detect significant embedding drift
    """
    from sklearn.metrics.pairwise import cosine_similarity

    similarities = []
    for old_emb, new_emb in zip(old_embeddings, new_embeddings):
        sim = cosine_similarity([old_emb], [new_emb])[0][0]
        similarities.append(sim)

    avg_similarity = np.mean(similarities)
    drift = 1 - avg_similarity

    if drift > threshold:
        return True, drift
    else:
        return False, drift
```

**Checklist**
- [ ] Embedding version tracked per document
- [ ] Drift detection on model updates
- [ ] Reindexing triggered on drift
- [ ] A/B test new models before deployment

---

## Vector Search Quality Checklist

- [ ] Model domain-appropriate and evaluated
- [ ] Same model version for indexing & querying
- [ ] Index type fits dataset size (Flat < HNSW < IVF)
- [ ] Index parameters tuned (ef_search, nprobe)
- [ ] Recall@k measured on eval set (≥95%)
- [ ] Latency within SLO (p95 < 300ms)
- [ ] Metadata filtering tested
- [ ] Hybrid search (BM25 + vector) evaluated
- [ ] Embedding drift monitoring active
- [ ] Model version tracked and logged  
