# Index Selection Guide

Pick the index after you know the retrieval mode, corpus scale, and filtering needs.

## First Questions

1. Do you need a dedicated vector index at all?
2. What is the corpus size in chunks or vectors?
3. How much filtering and ACL enforcement must happen at query time?
4. Is the system embedded, self-hosted, or managed?
5. Do you need multivectors, multimodal retrieval, or graph integration?

## Durable Rules

| Situation | Good default |
|-----------|--------------|
| Small collections and high accuracy | exact or flat search |
| General-purpose ANN | HNSW |
| Very large collections | IVF, DiskANN, or vendor-managed large-scale ANN |
| Heavy filtering and tenant isolation | choose stores that are strong at metadata filtering and query-time constraints |
| Postgres-native stack | pgvector-style options can be pragmatic if scale and latency fit |
| Embedded or local-first | embedded vector stores can simplify operations |

## Scale Optimization: Embedding Quantization

When memory or cost is the binding constraint at scale, apply quantization on top of the chosen index type.

| Corpus scale | First lever | Second lever |
|-------------|-------------|--------------|
| < 1M vectors | Usually unnecessary — raw float32 fits in memory | Matryoshka truncation if model supports it |
| 1M–10M | Scalar quantization (4x, minimal accuracy loss) | Matryoshka + scalar for ~16x combined |
| > 10M | Binary quantization + rescore (32x, ~96% accuracy with rescore) | Matryoshka + binary for up to 128x |

**Rules:**
- Quantization is orthogonal to index type — apply it to HNSW, IVF, flat, or vendor-managed indexes
- Binary quantization requires a rescore pass to recover accuracy; budget for storing original float32 vectors alongside the compressed index
- Matryoshka dimension reduction requires model support — check the model card before assuming it works
- Always benchmark recall@k on your eval set at the target compression level before deploying

See [vector-search-patterns.md — Pattern 3b](vector-search-patterns.md#pattern-3b-embedding-quantization) for implementation details and code.

## Evaluation Before Adoption

- Measure recall@k, MRR, nDCG, and P95 latency on your own queries.
- Test filtered and ACL-constrained retrieval, not just open search.
- Measure rebuild time, deletion propagation, and incremental update behavior.
- Validate fallback behavior when reranking or multivector stages are disabled.

## Special Cases

### Hosted Retrieval

If provider-managed file search already satisfies your product requirements, do not add a custom index just for perceived flexibility.

### Tool-First Retrieval

If the source of truth is SQL or APIs, use those systems first. A vector index should support prose search, not replace authoritative structured lookup.

### Multivectors And Late Interaction

If you need token-level precision, prefer stores that explicitly support named vectors or multivector-style retrieval. Verify latency and memory overhead on your corpus.

## Anti-Patterns

- Choosing a database from generic benchmark screenshots
- Comparing stores without the same filter, recall, and hardware settings
- Using vector infrastructure to solve a problem that is really SQL, graph, or API lookup
- Ignoring deletion, ACL, and freshness behavior while optimizing raw QPS

## March 2026 Note

Vendor capabilities change quickly. Verify current support for multivectors, named vectors, hosted retrieval, multimodal retrieval, and operational limits from official docs before recommending a concrete product.
