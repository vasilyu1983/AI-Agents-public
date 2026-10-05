# Storage Paradigm Selection

Pick the **storage shape** before schema, indexes, or engine. The quick-reference table in SKILL.md gives default engines; this matrix tests when a specialist store earns its extra operational cost.

## Paradigm Comparison Matrix

| Axis | Relational | Graph | Vector |
|------|------------|-------|--------|
| **Primary unit** | Row in a typed table | Node + typed edge | Embedding (float[N]) + payload |
| **Query shape** | Set algebra: filter, join, aggregate on known keys | Traversal: "N hops from X where edge type Y", shortest path, pattern match | k-NN by semantic similarity to a query vector |
| **Schema** | Fixed, declarative, enforced at write | Schema-lite (labels + edge types); shape evolves | Fixed dim per index; payload schema separate |
| **Consistency** | Strong (ACID), referential integrity | Strong on most engines (Neo4j ACID; some eventual) | Engine-dependent: pgvector indexes are WAL-logged and ACID with the rows they index; separately synced indexes (dedicated vector DBs, Atlas Search) can lag writes — check the engine's consistency docs |
| **Write pattern** | High-throughput OLTP, bulk loads | Moderate; edge writes dominate | Append-heavy; re-embed on model change |
| **Read pattern** | Predictable joins on indexed keys | Variable-depth traversals, recursive | ANN scan; recall/latency tradeoff |
| **Capacity test** | Measure hot data, throughput, lock and restore windows | Measure traversal shape and relationship density | Benchmark filtered recall, p99 latency, index build time and memory on the target corpus |
| **Indexing cost** | B-tree, GIN, GiST: workload-dependent | Edge indexes and label scans: workload-dependent | ANN index build, memory and recall are workload-dependent; vector payload bytes alone omit index overhead |
| **Default engine** | A supported PostgreSQL major | Neo4j or a relational model until variable-depth traversal justifies a graph engine | Start with exact pgvector beside the source row; add HNSW for measured latency, or use Atlas Vector Search when MongoDB is the source of truth |
| **Use when** | Source of truth, transactions, reporting, anything with FK integrity | Relationships are first-class queries, depth > 3 hops, pattern matching | Semantic search, RAG, dedup, recommendation by similarity |
| **Avoid when** | Variable-depth traversals dominate; deeply nested polymorphism | Workload is mostly set operations on known keys; team has no graph experience | Queries are exact-match on known fields; an exact scan meets measured latency |
| **Killer failure mode** | Recursive self-joins for hierarchies > 3 deep | Forced into graph for tabular data because "everything is connected" | Embeddings stored in a sidecar collection, forcing `$lookup`/JOIN on every retrieval |

## Decision Rules

1. **Default to relational.** Cheapest source of truth, easiest to operate. Add a specialist store only when relational measurably fails on a *measured* access pattern, not a hypothetical one.
2. **Graph only when traversal shape justifies it.** A fixed shallow relationship can be a relational join; variable-depth shortest-path or pattern queries may justify graph storage. Validate against the application's actual query mix rather than a hop-count threshold.
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

- **Relational + Vector** (PG + pgvector): RAG over private docs, source of truth in the same engine. For filtered ANN, pgvector applies ordinary SQL filters after the approximate index scan, so a selective filter can return too few rows; use a filter-column index or partitioning, then evaluate `hnsw.iterative_scan`/`ivfflat.iterative_scan` against recall and latency. Indexed `vector` supports up to 2,000 dimensions and indexed `halfvec` up to 4,000; check the installed extension's supported types before designing a larger embedding column. [pgvector README](https://github.com/pgvector/pgvector#filtering).
- **Relational + Graph** (PG + Neo4j): Transactional system of record, graph for fraud/recommendations/access control. Sync via CDC.
- **Relational + Search** (PG + Elasticsearch): OLTP + product search. Sync via outbox or CDC; never dual-write.
- **Document + Vector** (MongoDB + Atlas Vector Search): When document is already the source of truth — see the MongoDB Atlas scenario in SKILL.md.
- **Vector + Graph**: vector retrieval finds entry nodes, then traversal returns related records. Measure cross-store latency and consistency if the two stages live in different engines.

For AI-context-specific selection (memory, RAG, grounding), see `ai-context-layer` and `ai-rag` skills. For pgvector implementation, see `ai-vector-brain` skill.
