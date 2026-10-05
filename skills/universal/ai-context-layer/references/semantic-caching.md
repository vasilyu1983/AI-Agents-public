# Semantic Caching

Semantic caching reuses previously assembled context bundles and retrieval results when a new request is semantically similar to a cached one. This is a performance optimization within the context assembly layer.

## How It Works

1. Build the cache key as a hard filter on (tenant, actor scope, surface) and embed the query text only. Scope is never an embedded feature: two tenants with similar queries must never share a cache line.
2. Compare the embedding against cached entries using cosine similarity.
3. If similarity exceeds the threshold, return the cached bundle instead of re-assembling from scratch.
4. If below the threshold, assemble fresh and store the result.

## Configuration

- **Similarity threshold**: 0.85-0.95 range. Lower thresholds increase hit rates but risk serving stale or slightly wrong context. Higher thresholds are safer but reduce cache effectiveness. Tune per domain — factual domains need higher thresholds, creative or exploratory domains tolerate lower.
- **Cache key design**: `surface + actor_scope + intent_hash + time_bucket`. Include the surface and actor scope to prevent cross-surface or cross-tenant cache hits.
- **TTL**: set per context type. Live facts (short TTL, 1-5 min), memory (medium TTL, 15-60 min), domain evidence (longer TTL, 1-24 hours depending on corpus update frequency).

## Invalidation Strategies

- **TTL-based**: simplest. Set per-entry expiry based on the staleness tolerance of the context type.
- **Entity-change-triggered**: invalidate all cache entries for an entity when that entity's operational data changes. Requires a change notification channel from source-of-truth systems.
- **Confidence-decay**: reduce the confidence score of cached entries over time. Below a threshold, re-assemble fresh. Useful when you cannot detect changes but know the data drifts.

## When Semantic Caching Helps

- Repeated similar queries from the same user or surface (dashboards, recurring reports).
- Stable corpora where retrieval results change slowly.
- High-latency context assembly pipelines where cache hits save hundreds of milliseconds.

## When Semantic Caching Hurts

- Rapidly changing live facts (billing, inventory, real-time status).
- High-stakes decisions where even slightly stale context is unacceptable.
- Low query volume where the cache never warms up and adds overhead.

## Implementation

A key-value store with vector search (Redis-class) is a common choice for semantic caching — it combines the cache store and similarity search in one system. Alternatively, use your existing vector database with a dedicated namespace for cache entries.

Track cache hit rate as an operational metric. Below 30% hit rate, the caching layer is overhead without benefit.
