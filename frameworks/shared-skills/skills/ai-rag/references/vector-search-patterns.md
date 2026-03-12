# Vector Search Patterns

Operational patterns for dense retrieval using embeddings and ANN indexes.

---

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

**Configuration:**

```python
import hnswlib

# Initialize HNSW index
index = hnswlib.Index(space='cosine', dim=384)

# Parameters
index.init_index(
    max_elements=1000000,
    ef_construction=200,  # Higher = better quality, slower build
    M=16                   # Higher = better quality, more memory
)

# Tuning for search
index.set_ef(50)  # Higher = better recall, slower search
```

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

**Configuration:**

```python
import faiss

# IVF index for >10M vectors
dim = 384
nlist = 4096  # Number of clusters
quantizer = faiss.IndexFlatL2(dim)
index = faiss.IndexIVFFlat(quantizer, dim, nlist)

# Train index on sample vectors
index.train(sample_vectors)

# Add vectors
index.add(vectors)

# Search parameters
index.nprobe = 32  # Number of clusters to search
```

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

```python
import scann

# Build ScaNN index
searcher = scann.scann_ops_pybind.builder(
    db=vectors,
    num_neighbors=10,
    distance_measure="dot_product"
).tree(
    num_leaves=2000,
    num_leaves_to_search=100,
    training_sample_size=100000
).score_ah(
    dimensions_per_block=2,
    anisotropic_quantization_threshold=0.2
).reorder(100).build()
```

---

## Pattern 4: Retrieval Workflow

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

```python
def vector_search_with_filter(query, index, filters, k=10):
    """
    Vector search with metadata filters
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
