# Storage Paradigm Selection

Upstream decision: pick the **storage shape** before schema, indexes, or engine. This file answers "which paradigm fits the workload?" — engine choice within a paradigm lives in the Technology Selection table in SKILL.md. Most production systems end up polyglot (relational + one specialist store); the matrix below tells you when to add a second store, not replace the first.

## Paradigm Comparison Matrix

| Axis | Relational | Graph | Vector |
|------|------------|-------|--------|
| **Primary unit** | Row in a typed table | Node + typed edge | Embedding (float[N]) + payload |
| **Query shape** | Set algebra: filter, join, aggregate on known keys | Traversal: "N hops from X where edge type Y", shortest path, pattern match | k-NN by semantic similarity to a query vector |
| **Schema** | Fixed, declarative, enforced at write | Schema-lite (labels + edge types); shape evolves | Fixed dim per index; payload schema separate |
| **Consistency** | Strong (ACID), referential integrity | Strong on most engines (Neo4j ACID; some eventual) | Eventually consistent index; payload can be ACID if co-located |
| **Write pattern** | High-throughput OLTP, bulk loads | Moderate; edge writes dominate | Append-heavy; re-embed on model change |
| **Read pattern** | Predictable joins on indexed keys | Variable-depth traversals, recursive | ANN scan; recall/latency tradeoff |
| **Scale ceiling (single node)** | ~10 TB hot data, ~100k QPS | ~1B edges before sharding hurts | ~100M vectors with HNSW in RAM |
| **Indexing cost** | B-tree, GIN, GiST — cheap | Edge indexes + label scans — moderate | HNSW/IVF in RAM — expensive (≈ `dim × 4B × count × 1.5`) |
| **Default engine** | PostgreSQL 18 | Neo4j, Memgraph; or PG with `ltree`/recursive CTE for <3 hops | pgvector (co-located; HNSW default, IVFFlat for slower-build/lower-memory tradeoffs), Qdrant/Weaviate (scale beyond single-node RAM), Atlas Vector Search (if MongoDB) |
| **Use when** | Source of truth, transactions, reporting, anything with FK integrity | Relationships are first-class queries, depth > 3 hops, pattern matching | Semantic search, RAG, dedup, recommendation by similarity |
| **Avoid when** | Variable-depth traversals dominate; deeply nested polymorphism | Workload is mostly set operations on known keys; team has no graph experience | Queries are exact-match on known fields; corpus < 10k items (linear scan is fine) |
| **Killer failure mode** | Recursive self-joins for hierarchies > 3 deep | Forced into graph for tabular data because "everything is connected" | Embeddings stored in a sidecar collection, forcing `$lookup`/JOIN on every retrieval |

## Decision Rules

1. **Default to relational.** Cheapest source of truth, easiest to operate. Add a specialist store only when relational measurably fails on a *measured* access pattern, not a hypothetical one.
2. **Graph only when traversal depth is variable and unbounded.** "Friends of friends" up to 2 hops is a relational join. "Find the shortest fraud-ring path across N entities" is a graph query. A domain-specific RAG evaluation (arXiv:2604.11419, cyber-threat-intelligence QA) found hybrid graph-plus-text retrieval improved answer quality up to 35% over vector-only RAG specifically on multi-hop, relationship-heavy questions, while vector-only retrieval held up fine on single-entity factual lookups — the gap is in relationship reasoning, not raw entity count, and the magnitude is domain-specific. Treat any generic threshold ("N hops," "N entities") as a starting hypothesis to validate against your own query mix, not a portable constant.
3. **Vector is an index, not a primary store.** Keep source documents in the relational/document store; put embeddings *next to* the payload (same row or co-located collection). Sidecar vector stores create the consistency surface that breaks retrieval at scale.
4. **Don't blend paradigms in one query.** If you find yourself joining vector results back to a relational store across the network on every request, either co-locate (pgvector, Atlas Vector Search) or denormalize the payload into the vector store.
5. **Polyglot is normal; polyglot without ownership is debt.** Each additional paradigm doubles the on-call surface. Name an owner per store before adoption.

## Adjacent Paradigms

| Paradigm | Pick when | Don't pick when |
|----------|-----------|------------------|
| **Document** (MongoDB) | Schema varies per record, embedded relationships, rapid iteration | You need multi-document transactions across many collections |
| **Key-value** (Redis) | Ephemeral state, counters, sessions, rate limits, pub/sub | You need durability or queryability beyond `GET key` |
| **Time-series** (TimescaleDB, InfluxDB) | Append-only metrics with time-window aggregates | Mutable entities or low-volume event logs (relational is fine) |
| **Search** (Elasticsearch, OpenSearch, Meilisearch) | Full-text relevance, faceted search, autocomplete are the product | A `WHERE col LIKE '%x%'` would do |

## Common Polyglot Combinations

- **Relational + Vector** (PG + pgvector): RAG over private docs, source-of-truth in same engine. Default for AI features.
- **Relational + Graph** (PG + Neo4j): Transactional system of record, graph for fraud/recommendations/access control. Sync via CDC.
- **Relational + Search** (PG + Elasticsearch): OLTP + product search. Sync via outbox or CDC; never dual-write.
- **Document + Vector** (MongoDB + Atlas Vector Search): When document is already the source of truth — see the MongoDB Atlas scenario in SKILL.md.
- **Vector + Graph**: `$vectorSearch` (or pgvector / Qdrant) finds entry nodes by semantic similarity, then Cypher / graph traversal returns the relational context around them. Canonical implementation: Neo4j's `VectorCypherRetriever`. Standard hybrid-RAG pattern in 2026 when queries are both fuzzy ("find me docs about X") and structured ("…then show how X relates to Y and Z"). Failure mode: running both stages against unrelated stores over the network on every request — co-locate the index and the graph, or denormalize the payload into the vector store.

For AI-context-specific selection (memory, RAG, grounding), see `ai-context-layer` and `ai-rag` skills. For pgvector implementation, see `ai-vector-brain` skill.
