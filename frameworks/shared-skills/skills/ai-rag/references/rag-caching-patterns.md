# RAG Caching Patterns

> Operational guide for caching in RAG pipelines — semantic query cache, embedding cache, retrieval result cache, and response cache. Covers cache architecture, invalidation strategies, TTL policies, warming patterns, and cost/latency tradeoff analysis per cache layer. Focus on production implementation.

**Freshness anchor:** January 2026 — Redis 7.4+, GPTCache 0.1.44+, Pinecone/Weaviate caching features current

---

## Decision Tree: Which Cache Layers to Implement

```
START
│
├─ Primary goal?
│   ├─ Reduce LLM API cost
│   │   └─ Response cache (highest impact) + Semantic query cache
│   │
│   ├─ Reduce latency
│   │   └─ All layers: embedding → retrieval → response
│   │
│   └─ Reduce embedding API cost
│       └─ Embedding cache (avoid re-embedding same content)
│
├─ Query pattern?
│   ├─ Many similar/repeated queries (FAQ, support)
│   │   └─ Semantic cache → 50-80% hit rate typical
│   │
│   ├─ Diverse, unique queries (research, analysis)
│   │   └─ Semantic cache low hit rate → focus on embedding + retrieval cache
│   │
│   └─ Mixed
│       └─ All layers with appropriate TTLs
│
├─ Corpus update frequency?
│   ├─ Real-time updates (minutes)
│   │   └─ Short TTL (5-15 min) + event-based invalidation
│   │
│   ├─ Daily updates
│   │   └─ Medium TTL (1-24 hours) + daily full invalidation
│   │
│   └─ Rarely changes (weekly+)
│       └─ Long TTL (days-weeks) + manual invalidation
│
└─ Budget for cache infrastructure?
    ├─ Minimal → In-process LRU cache (no Redis needed)
    ├─ Moderate → Redis for hot layer, disk for warm layer
    └─ Enterprise → Redis Cluster + CDN for response cache
```

---

## Cache Layer Architecture

```
User Query
    │
    ▼
┌────────────────┐
│ Response Cache  │ ← Exact or semantic match on (query + filters)
│ (Layer 4)       │   Hit? Return cached response directly
└───────┬────────┘
        │ Miss
        ▼
┌────────────────┐
│ Semantic Cache  │ ← Embedding similarity on query
│ (Layer 3)       │   Hit? Return cached retrieval + response
└───────┬────────┘
        │ Miss
        ▼
┌────────────────┐
│ Retrieval Cache │ ← Exact match on (query embedding + filters + top_k)
│ (Layer 2)       │   Hit? Skip vector search, go to LLM
└───────┬────────┘
        │ Miss
        ▼
┌────────────────┐
│ Embedding Cache │ ← Exact match on text → embedding
│ (Layer 1)       │   Hit? Skip embedding API call
└───────┬────────┘
        │ Miss
        ▼
   Full RAG Pipeline
   (embed → search → retrieve → generate)
```

---

## Quick Reference: Cache Layers

| Layer | Key | Value | Hit Rate | Cost Savings | Latency Savings |
|-------|-----|-------|----------|--------------|-----------------|
| Embedding | text hash | embedding vector | 30-60% (corpus) | Embedding API cost | 50-100ms |
| Retrieval | embedding + filters | top-k doc IDs + scores | 10-30% | Vector DB compute | 100-300ms |
| Semantic | query embedding (fuzzy) | full response | 20-60% (FAQ-like) | LLM API cost | 500-2000ms |
| Response | exact query + filters | generated response | 5-20% | LLM API cost | 500-2000ms |

---

## Operational Patterns

### Pattern 1: Embedding Cache

- **Use when:** Re-embedding same content (corpus updates, query dedup)
- **Implementation:**

```python
import hashlib, redis, numpy as np

class EmbeddingCache:
    """Cache embeddings to avoid redundant API calls."""

    def __init__(self, redis_client, ttl_seconds=86400 * 7, model_version="v1"):
        self.redis = redis_client
        self.ttl = ttl_seconds
        self.model_version = model_version

    def _cache_key(self, text):
        content = f"{self.model_version}:{text}"
        return f"emb:{hashlib.sha256(content.encode()).hexdigest()}"

    def get_or_embed(self, text, embed_fn):
        """Get from cache or compute and cache."""
        key = self._cache_key(text)
        data = self.redis.get(key)
        if data:
            return np.frombuffer(data, dtype=np.float32)
        embedding = embed_fn(text)
        self.redis.setex(key, self.ttl, embedding.astype(np.float32).tobytes())
        return embedding

    def batch_get_or_embed(self, texts, embed_fn):
        """Batch: get cached, embed only misses."""
        results, misses, miss_idx = [None] * len(texts), [], []
        for i, text in enumerate(texts):
            data = self.redis.get(self._cache_key(text))
            if data:
                results[i] = np.frombuffer(data, dtype=np.float32)
            else:
                misses.append(text)
                miss_idx.append(i)
        if misses:
            new_embs = embed_fn(misses)
            for idx, emb in zip(miss_idx, new_embs):
                results[idx] = emb
                self.redis.setex(self._cache_key(texts[idx]), self.ttl,
                                 emb.astype(np.float32).tobytes())
        return results
```

- **Key decisions:**
  - Include model version in cache key (different models = different embeddings)
  - TTL: 7 days for corpus embeddings, 1 hour for query embeddings
  - Storage: ~4KB per embedding (1024 dims * 4 bytes float32)

### Pattern 2: Semantic Query Cache

- **Use when:** Many similar queries (customer support, FAQ, repeated questions)
- **Implementation:**

```python
class SemanticCache:
    """Cache RAG responses using embedding similarity for matching."""

    def __init__(self, embedding_model, vector_store, similarity_threshold=0.95,
                 ttl_seconds=3600):
        self.embedder = embedding_model
        self.store = vector_store  # Pinecone, Redis Vector, or FAISS
        self.threshold = similarity_threshold
        self.ttl = ttl_seconds

    def lookup(self, query, filters=None):
        """Find semantically similar cached query."""
        query_embedding = self.embedder.encode(query)

        results = self.store.query(
            vector=query_embedding,
            top_k=1,
            filter=self._build_filter(filters),
            include_metadata=True,
        )

        if results and results[0].score >= self.threshold:
            cached = results[0].metadata
            # Check TTL
            if time.time() - cached['timestamp'] < self.ttl:
                return {
                    'response': cached['response'],
                    'sources': cached['sources'],
                    'cache_hit': True,
                    'similarity': results[0].score,
                }
        return None

    def store_response(self, query, response, sources, filters=None):
        """Cache a query-response pair with embedding as key."""
        query_embedding = self.embedder.encode(query)
        self.store.upsert(id=hashlib.sha256(query.encode()).hexdigest(),
            vector=query_embedding,
            metadata={'query': query, 'response': response,
                      'sources': json.dumps(sources), 'timestamp': time.time()})
```

- **Similarity threshold tuning:**

| Threshold | Behavior | Use Case |
|-----------|----------|----------|
| 0.99 | Near-exact match only | High-precision (legal, medical) |
| 0.95 | Paraphrases match | General purpose (recommended start) |
| 0.90 | Broader matching | FAQ, support chatbot |
| 0.85 | Very broad | Risk of wrong cached response |

- **Threshold calibration process:**
  1. Collect 100 query pairs manually labeled as "same intent" or "different intent"
  2. Compute similarity scores for each pair
  3. Find threshold that maximizes F1 on intent matching
  4. Start conservative (0.95), lower if hit rate is too low

### Pattern 3: Retrieval Result Cache

- **Use when:** Same query+filters combination hits vector DB repeatedly
- **Implementation:**

```python
class RetrievalCache:
    """Cache vector search results to skip DB queries."""

    def __init__(self, redis_client, ttl_seconds=900):  # 15 min default
        self.redis = redis_client
        self.ttl = ttl_seconds

    def _cache_key(self, query_embedding, filters, top_k):
        """Key from embedding hash + filters + k."""
        emb_hash = hashlib.sha256(
            query_embedding.astype(np.float32).tobytes()
        ).hexdigest()[:16]
        filter_hash = hashlib.sha256(
            json.dumps(filters, sort_keys=True).encode()
        ).hexdigest()[:16]
        return f"retrieval:{emb_hash}:{filter_hash}:{top_k}"

    def get(self, query_embedding, filters=None, top_k=10):
        """Get cached retrieval results."""
        key = self._cache_key(query_embedding, filters or {}, top_k)
        data = self.redis.get(key)
        if data:
            return json.loads(data)
        return None

    def set(self, query_embedding, results, filters=None, top_k=10):
        """Cache retrieval results."""
        key = self._cache_key(query_embedding, filters or {}, top_k)
        self.redis.setex(key, self.ttl, json.dumps(results))
```

- **TTL by corpus update frequency:**

| Corpus Updates | Retrieval Cache TTL | Invalidation Strategy |
|---------------|--------------------|-----------------------|
| Real-time | 5 minutes | Event-based invalidation |
| Hourly | 30 minutes | Time-based |
| Daily | 4 hours | Time-based + daily flush |
| Weekly | 24 hours | Time-based + weekly flush |
| Static | 7 days | Manual only |

### Pattern 4: Response Cache with Invalidation

- **Use when:** Caching final LLM-generated responses
- **Cache key:** `hash(query.lower() + filters + model_version)` — exact match only
- **Invalidation:** Maintain secondary index `source_id → [response_cache_keys]` so corpus updates invalidate affected responses
- **TTL:** Same as retrieval cache TTL table above
- **Key rule:** Only cache successful responses — never cache errors or empty results

### Pattern 5: Cache Warming

- **Use when:** Need low latency from the start, or predictable query patterns
- **Warming strategies:**
  - **From query logs:** Get top 200-500 most frequent queries from last 7 days, run full pipeline with `cache_write=True, cache_read=False`
  - **From corpus updates:** Find cached queries that referenced updated documents, invalidate, re-run
  - **Scheduled:** Daily cron at off-peak hours (e.g., 5am) warms top queries
- **Key rule:** Warm top 200-500 by frequency only — warming rare queries wastes compute

### Pattern 6: Full Pipeline with All Cache Layers

- **Use when:** Production RAG with cost and latency optimization
- **Lookup order:** Response cache (exact) → Semantic cache (fuzzy) → Embedding cache → Retrieval cache → Full pipeline
- **Write order:** On miss, run full pipeline, then write to all cache layers for future hits
- **Key rule:** Check higher layers first (response/semantic save the most) before falling through to lower layers

---

## Cost/Latency Tradeoff Analysis

| Cache Layer | Latency Saved | Cost Saved per Hit | Cache Storage Cost | Break-Even Hits/Day |
|---|---|---|---|---|
| Embedding | 50-100ms | $0.00002/query | ~4KB/entry | Low (~100) |
| Retrieval | 100-300ms | $0.001-0.01/query | ~1KB/entry | Low (~50) |
| Semantic | 500-2000ms | $0.003-0.03/query | ~5KB/entry | Medium (~20) |
| Response | 500-2000ms | $0.003-0.03/query | ~2KB/entry | Medium (~10) |

- **Monthly savings example (100k queries/day, 40% semantic hit rate):**
  - LLM API saved: 40,000 queries/day * $0.01 * 30 = **$12,000/month**
  - Cache infra cost: Redis 16GB = **~$200/month**
  - Net savings: **~$11,800/month**

---

## Key Monitoring Metrics

- **cache_hit_rate_by_layer** (gauge) — per layer: embedding, retrieval, semantic, response
- **cache_latency_savings_ms** (histogram) — latency saved per cache hit
- **cache_cost_savings_usd** (counter) — cumulative cost saved
- **cache_size_bytes** (gauge) — per layer
- **cache_stale_hit_rate** (gauge) — hits on entries older than recommended TTL
- **cache_invalidation_count** (counter) — by reason: ttl_expired, corpus_update, manual

---

## Anti-Patterns

| Anti-Pattern | Why It Fails | Fix |
|---|---|---|
| Caching without TTL | Stale responses served indefinitely | Set TTL based on corpus update frequency |
| Semantic cache threshold too low (< 0.90) | Returns wrong cached answer for different query | Start at 0.95, calibrate on labeled pairs |
| No invalidation on corpus update | Cached answers reference outdated/deleted docs | Event-based invalidation + source tracking |
| Caching error responses | Errors get served repeatedly | Only cache successful responses |
| Single cache layer for all query types | Different patterns need different strategies | Layer caches by function (embed/retrieval/response) |
| Ignoring cache metrics | No visibility into hit rates, savings | Log hit/miss per layer, track savings weekly |
| Warming too many queries | Wastes compute and storage on rare queries | Warm top 200-500 by frequency only |
| Cache key includes non-deterministic elements | Timestamp, request_id in key = 0% hit rate | Keys: query + filters + model version only |
| No cache for embedding API calls | Re-embedding same corpus content on updates | Cache corpus embeddings with long TTL |
| Mixing model versions in cache | Different models produce different embeddings | Include model version in all cache keys |

---

## Validation Checklist

- [ ] Cache layers identified based on query patterns and cost goals
- [ ] TTL policies set per layer, aligned with corpus update frequency
- [ ] Semantic cache threshold calibrated on labeled query pairs
- [ ] Invalidation pipeline triggers on corpus updates
- [ ] Cache keys include model version (no cross-model contamination)
- [ ] Error responses excluded from cache
- [ ] Hit rate monitoring in place per layer
- [ ] Cost savings tracked and reported monthly
- [ ] Cache warming schedule configured for top queries
- [ ] Fallback to full pipeline on cache miss is tested and fast

---

## Cross-References

- `ai-rag/references/embedding-model-guide.md` — embedding cost reduction via caching
- `ai-rag/references/graph-rag-patterns.md` — caching graph traversal results
- `ai-mlops/references/cost-management-finops.md` — cache ROI in overall ML FinOps
- `ai-mlops/references/experiment-tracking-patterns.md` — tracking cache performance experiments
