# Index Selection Guide for RAG Vector Stores

Choosing the right index is crucial for recall, latency, and cost.

**2026 Update**: pgvectorscale has emerged as a strong contender for PostgreSQL users, with benchmarks showing competitive performance up to 50M vectors.

---

## 1. Decision Rules by Dataset Size

| Dataset Size | Recommended Index | Notes |
|--------------|-------------------|-------|
| < 100k chunks | Flat (exact search) | Perfect recall, simple |
| 100k–10M | HNSW | Best general-purpose |
| 10M–50M | pgvectorscale or HNSW | pgvectorscale competitive here |
| > 50M | IVF / ScaNN / DiskANN | Specialized scaling needed |

---

## 2. Index Types Summary

### Flat Index

- Exact search  
- Perfect recall, poor scalability  
- Use for prototypes or small datasets  

---

### HNSW (Hierarchical Navigable Small World)

- Best general-purpose ANN  
- Great recall/latency tradeoff  
- Works well with metadata filtering  

**Key parameters**

- M (graph degree)  
- ef_search (controls recall)  
- ef_construction  

---

### IVF (Inverted File Index)

- Clusters vectors into centroids  
- Faster search on large collections  
- Tune nlist, nprobe  

---

### ScaNN

- Fastest for large embedding sets  
- Good for high-dimensional vectors (>1000 dims)  
- Use for Google-scale workloads  

---

### DiskANN

- Very large datasets (hundreds of millions)  
- Stores index on SSD  
- High throughput  

---

## 3. Embedding Model Compatibility

Rules:

- Normalize embeddings when model expects it  
- Avoid mixing embedding model versions  
- Reindex whenever embedding model changes  

---

## 4. Index Refresh Strategy

### When to refresh

- Content changes >10%  
- New embedding model  
- Major chunking redesign  
- Drift detected in embedding centroids  

---

## 5. Index Validation Checklist

- [ ] Recall@k measured
- [ ] Latency measured
- [ ] ef_search/nprobe tuned
- [ ] Multithreading/GPU acceleration tested
- [ ] Metadata filtering enabled if needed

---

## 6. Vector Database Comparison (2026)

### Managed Services

| Database | Strengths | Scale | Best For |
|----------|-----------|-------|----------|
| **Pinecone** | Fully managed, enterprise compliance (SOC2, HIPAA) | Billions | Zero-ops, enterprise |
| **Weaviate Cloud** | Multi-modal, GraphQL, hybrid search | Large | Feature-rich applications |
| **Qdrant Cloud** | Rust performance, filtering, ACID | Large | High-performance filtering |
| **Zilliz/Milvus** | Open-source option, GPU acceleration | Billions | Cost-conscious scale |

### Self-Hosted / Embedded

| Database | Strengths | Scale Limit | Best For |
|----------|-----------|-------------|----------|
| **pgvector** | Postgres integration, familiar | ~10M | Existing Postgres users |
| **pgvectorscale** | pgvector + Timescale optimizations | ~50M | Postgres at scale |
| **Chroma** | Simple API, embedded | ~1M | Prototyping, small apps |
| **LanceDB** | Embedded, serverless, multimodal | ~10M | Edge, local-first apps |
| **FAISS** | Research-grade, GPU support | Billions | Custom infrastructure |

### pgvectorscale Deep Dive

**What it is**: Timescale's extension to pgvector that adds StreamingDiskANN index and performance optimizations.

**Benchmark highlights** (at 50M vectors, 99% recall):

| Database | QPS | Notes |
|----------|-----|-------|
| pgvectorscale | 471 | With StreamingDiskANN |
| Qdrant | 41.47 | Default configuration |

**Caveats**:
- Benchmarks vary by workload and configuration
- Qdrant excels at filtered queries
- pgvectorscale requires Postgres infrastructure

**When to choose pgvectorscale**:
- Already running PostgreSQL
- Need transactional consistency with vector data
- 10M-50M vector range
- Want to avoid new infrastructure

**When to choose dedicated vector DB**:
- >100M vectors
- Complex filtering requirements
- Need managed service
- Multi-tenant isolation required

### Emerging: LanceDB

**2026 trend**: LanceDB gaining traction for embedded/serverless use cases.

**Strengths**:
- Zero-copy, columnar format (Lance)
- Serverless-friendly (S3-native)
- Multimodal (text, images, video)
- Python-native, no server needed

**Best for**:
- Local-first applications
- Edge deployment
- Data science workflows
- Cost-sensitive projects

---

## 7. Selection Decision Tree

```text
Choosing a vector database:
  │
  ├─ Existing infrastructure?
  │   ├─ PostgreSQL → pgvector/pgvectorscale
  │   ├─ Elasticsearch → ES vector search
  │   └─ None → Continue below
  │
  ├─ Scale requirements?
  │   ├─ <1M vectors → Chroma, LanceDB (embedded)
  │   ├─ 1M-50M → pgvectorscale, Qdrant, Weaviate
  │   └─ >50M → Pinecone, Milvus, custom FAISS
  │
  ├─ Operational preference?
  │   ├─ Zero-ops → Pinecone (managed)
  │   ├─ Self-hosted → Qdrant, Milvus, Weaviate
  │   └─ Embedded → Chroma, LanceDB
  │
  └─ Special requirements?
      ├─ Multimodal → Weaviate, LanceDB
      ├─ Complex filtering → Qdrant
      ├─ Hybrid search → Weaviate, Elasticsearch
      └─ GPU acceleration → Milvus, FAISS
```

---

## Related Resources

- [Retrieval Patterns](retrieval-patterns.md) - Search strategies
- [Pipeline Architecture](pipeline-architecture.md) - End-to-end RAG design  
