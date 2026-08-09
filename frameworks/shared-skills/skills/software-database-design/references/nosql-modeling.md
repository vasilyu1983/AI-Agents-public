# NoSQL Modeling

Use this file when the request is about document, key-value, or graph-oriented data models.

## Document Stores (MongoDB-focused)

### Core Patterns

| Pattern | When to Use | Example |
|---|---|---|
| **Embedded documents** | 1:1 or bounded 1:few; data read and updated together | `user.address` embedded in `users` |
| **Referenced documents** | 1:many unbounded; child has independent lifecycle | `posts._id` referenced from `comments.post_id` |
| **Extended reference** | Frequently joined fields; tolerable staleness | Cache `author.name` inside `post` doc |
| **Subset pattern** | Hot subset of a large array kept inline | Last 10 comments embedded; rest in separate collection |
| **Bucketing** | High-volume time-series / IoT / chat | One doc per (sensor_id, hour) with array of readings |
| **Computed pattern** | Aggregate read often, recompute rarely | Pre-compute `total_orders` on user; refresh on write |
| **Schema versioning** | Document shape evolves over time | `_schemaVersion: 2` field; migrate on read or in batch |
| **Outlier pattern** | 99% small docs, 1% huge | Flag outliers, store overflow in side collection |
| **Polymorphic** | Mixed shapes in one collection | `type: "video"` vs `type: "article"` with shared base fields |

### MongoDB Anti-Patterns

| Avoid | Why | Do Instead |
|---|---|---|
| Unbounded arrays | 16 MB doc limit; index growth; slow updates | Bucket or extract to child collection at ~1000 elements |
| Massive embedded subdocuments | Whole-doc rewrites on update | Reference when subdoc > 100 KB or updated independently |
| `$lookup` as default | Cross-collection joins are not Mongo's strength | Embed or extended-reference; use `$lookup` for ad-hoc analytics |
| Treating Mongo as a relational DB | ALTER-style migrations, heavy normalization | Model around access patterns; embrace duplication |
| Indexing every field | Write amplification, RAM pressure | Index only fields in actual queries; check `$indexStats` |
| Case-sensitive equality on user input | Locale bugs, missed matches | Collation indexes (`strength: 2`) or store normalized form |
| Storing embeddings in separate collection from doc | Forces joins on every retrieval | Co-locate `embedding` field on the source document |

### Indexing — the ESR Rule

For compound indexes, order fields as **Equality → Sort → Range**:

```text
Query: find({ tenant_id: "X", status: "active", created_at: { $gt: T } })
              .sort({ priority: -1 })

Index:  { tenant_id: 1, status: 1, priority: -1, created_at: 1 }
         └─ Equality ─┘ └─ Sort ─┘ └─ Range ─┘
```

- Equality fields first (highest selectivity).
- Sort fields next, in the same direction as the query.
- Range fields last (Mongo cannot use later index keys after a range scan).
- Use partial indexes (`partialFilterExpression`) to exclude soft-deleted or inactive docs.
- Use TTL indexes (`expireAfterSeconds`) for sessions, ephemeral state, agent short-term memory.

### MongoDB 8.x Features to Know (current major: 8.3 as of July 2026)

- **Queryable Encryption** GA — encrypted equality and range queries; use for PII and PHI fields.
- **Time-series collections** with automatic compression and tiered Atlas storage (online → archive).
- **Block processing** in aggregation — meaningful speedup on `$group` over time-series.
- **Atlas Vector Search** — `$vectorSearch` aggregation stage; ANN over indexed `vector` fields; supports filtered vector search and hybrid (BM25 + vector via the `$rankFusion` stage, native since Atlas 8.1, plus the newer `$scoreFusion` for custom weighted-score blending — verify GA vs. preview status for your Atlas tier before depending on either in production).
- **Atlas Search** — Lucene-based full-text; same cluster, no ETL.
- **Atlas Stream Processing** — Kafka/Kinesis ingest with MongoDB-native pipelines.

## Key-Value Stores (Redis)

- Design keys around access patterns first; choose a stable, parseable scheme (`tenant:{id}:session:{sid}`).
- Keep values small and bounded (< 100 KB; ideally < 10 KB).
- Plan expiry (`EXPIRE`), invalidation triggers, and cold-start rebuild path up front.
- Prefer dedicated structures (Streams, Sorted Sets, HyperLogLog) over hand-rolled JSON in strings.
- For agent short-term memory: Streams for trace, Sorted Sets for recency-weighted recall, Hash for slot state.

## Graph Stores

- Use when traversals (≥ 3 hops) dominate. Below 3 hops, a relational schema with proper indexes wins on cost.
- Model edges as first-class with type and direction; avoid generic "related_to".
- Materialize frequently traversed shortest-path results when read-heavy.

## General Rule

Pick the model that matches the dominant access pattern. Do not recreate a relational schema inside a document or key-value store unless the workload truly needs it. For AI-agent workloads specifically, prefer co-locating operational data, full-text indexes, and vector embeddings in one engine to eliminate cross-store consistency problems.
