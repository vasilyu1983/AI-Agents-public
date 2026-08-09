# Graph Theory For Vector DBs At Scale

Vector DBs *are* graph systems below the API. HNSW, DiskANN/Vamana, NSG, and
their variants are all proximity graphs over the embedding space. Once you
move past a few million vectors, the way the index graph is built, navigated,
quantized, partitioned, and combined with an external knowledge graph
dominates retrieval quality and cost more than the embedding model itself.

This reference is the operational map for that regime. Theory of *what* a
graph index is stays brief; the load is on tuning, escalation triggers,
graph-augmented retrieval, and reusable infra elsewhere in this repo.

## Table of Contents

- [Why This Reference Exists](#why-this-reference-exists)
- [The Two Graphs In Play](#the-two-graphs-in-play)
- [HNSW As A Graph: Tuning Levers](#hnsw-as-a-graph-tuning-levers)
- [DiskANN / Vamana / pgvectorscale](#diskann--vamana--pgvectorscale)
- [Quantization And The Memory Wall](#quantization-and-the-memory-wall)
- [Sharding And Partitioning](#sharding-and-partitioning)
- [Graph-Augmented Retrieval](#graph-augmented-retrieval)
- [Reusing The Existing Graph Infra](#reusing-the-existing-graph-infra)
- [Scale Decision Table](#scale-decision-table)
- [Anti-Patterns](#anti-patterns)
- [See Also](#see-also)

## Why This Reference Exists

Standard advice ("use HNSW with m=16, ef_construction=64") works to ~10M
vectors with strong filters. Beyond that, three things break:

1. **Build memory blows up** — HNSW keeps the whole graph in RAM during
   construction; m × N × bytes-per-link grows linearly.
2. **Filtered recall collapses** — the navigable graph was built without
   knowledge of your filters; selective predicates strand the search in
   regions that have no surviving candidates.
3. **Per-query latency drifts upward** — at 100M+ nodes, ef_search needed
   for target recall climbs faster than linearly.

The fixes are graph-shaped: switch index family (DiskANN), quantize the graph
nodes (PQ/BQ), partition the graph (shards), or compose the vector graph
with an external knowledge/code graph that bounds the candidate region
*before* ANN runs.

## The Two Graphs In Play

| Graph | What it is | Owned by |
|---|---|---|
| **Index graph** | Proximity graph the ANN engine traverses (HNSW layers, Vamana, NSG). Edges = "near in embedding space." | The vector backend (pgvector, pgvectorscale, Qdrant, Milvus, Vespa). |
| **Knowledge graph** | Domain graph whose nodes are documents/chunks/entities and edges are real relationships (cites, depends_on, supersedes, parent_of, authority_over). | The corpus model (your schema, code-graph artifacts, knowledge-graph builders). |

The two are independent. You almost always want both at scale: the index
graph makes ANN possible, and the knowledge graph makes ANN *correct* on
filtered, multi-hop, or authority-bounded questions where the index graph
alone returns plausible-but-wrong neighbors.

## HNSW As A Graph: Tuning Levers

HNSW is a multi-layer navigable small-world graph. Layer 0 holds every
node; higher layers hold exponentially fewer "highway" nodes. Search
descends from the top layer to layer 0 by greedy graph walk.

The four levers that matter at scale:

| Lever | What it controls | Default | At scale |
|---|---|---|---|
| `m` | Max edges per node per layer (higher = denser graph, better recall, more memory) | 16 | 24–48 for ≥10M nodes; cap at 64 |
| `ef_construction` | Candidate beam during build (higher = better graph, slower build) | 64 | 128–256 for ≥10M nodes |
| `ef_search` | Candidate beam during query | 40–100 | Tune per-recall target on the eval set; expect 200–400 at 50M+ |
| Distance op | `vector_cosine_ops`, `vector_ip_ops`, `vector_l2_ops`, or `halfvec_*_ops` | Cosine | Switch to `halfvec_*_ops` for >2000-dim or memory-bound builds |

Build memory rough estimate (pgvector): `m × N × 8 bytes × layers (~1.05)`.
At m=24 and N=50M that is ~10 GB just for graph links, on top of vectors.

**Trigger to leave HNSW:**
- Build OOMs even at m=16 on the largest box you can run
- Filtered recall@10 < 0.7 with selective predicates after `ef_search` > 400
- p95 query latency past your budget at acceptable recall
- Index rebuild SLO can no longer be hit during a maintenance window

When two of those fire, escalate to DiskANN.

## DiskANN / Vamana / pgvectorscale

DiskANN (Microsoft Research, 2019) and its open variant Vamana keep the
graph on SSD and a small in-memory cache. The construction algorithm
(`RobustPrune`) explicitly builds long-range edges so a small beam can still
reach distant neighbors, which is what makes disk-resident search viable.

`pgvectorscale` ships **StreamingDiskANN** as a Postgres index type. From a
schema perspective it is a drop-in replacement for HNSW:

```sql
CREATE INDEX ON embeddings
  USING diskann (embedding vector_cosine_ops);

-- Per-query tuning
SET LOCAL diskann.query_search_list_size = 100;  -- analogous to ef_search
SET LOCAL diskann.query_rescore = 50;             -- rescore top-N with full-precision vectors
```

When pgvectorscale wins:

- Corpus > 50–100M chunks where HNSW build memory is the gating factor
- Workload tolerates SSD-bound p95 latency in exchange for an order of
  magnitude lower RAM
- You want SBQ (statistical binary quantization) without leaving Postgres

When it does not win:

- Your stack already runs Qdrant, Vespa, or Milvus and you are not married
  to Postgres; their native disk graphs and quantization paths are mature
- You need multi-vector / late-interaction (ColBERT) — DiskANN is single-
  vector by design

Verify pgvectorscale version, supported Postgres versions, and managed
hosting support against current docs before committing — extension support
is the load-bearing constraint, not the algorithm.

**pgvectorscale 0.9.0 (November 2025):** adds PG18 support and concurrent
DiskANN index builds (previously builds were single-threaded and blocked
writes), drops PG13 support. If you are on PG13 and need pgvectorscale,
upgrade Postgres first. Concurrent builds are opt-in via
`diskann.concurrent_index_build` — test on a replica before enabling in
production; see the pgvectorscale README for the parameter and memory budget
guidance.

## Quantization And The Memory Wall

Past ~100M vectors, raw float32 storage becomes the dominant cost. The
graph index does not care about precision until the final rescore step, so
quantization fits naturally:

| Technique | Compression | Recall hit | Notes |
|---|---|---|---|
| `halfvec` (FP16) | 2× | Negligible | pgvector ≥0.7. Free win for >2000-dim. |
| Scalar (INT8) | 4× | ~1–3% | Common in Qdrant, Milvus. |
| Product Quantization (PQ) | 8–32× | 3–10% (recover with rescore) | Classic IVF-PQ; Faiss/Milvus default at scale. |
| Binary Quantization (BQ / SBQ) | 32× | 5–15% (recover with rescore) | pgvectorscale SBQ, Weaviate/Qdrant BQ. See two-pass recipe below. |

The pattern at scale is always *compress for the graph walk, rescore the
top-N with the full-precision vectors*. Skipping rescore is the most common
quantization anti-pattern.

### pgvector Binary Quantization Two-Pass Recipe

For corpora where 32× storage reduction justifies the rescore overhead, pgvector supports
BQ natively via `binary_quantize()` (requires pgvector ≥ 0.7.0; `binary_quantize` performance
optimised in 0.8.1):

**Step (a) — Build the BQ HNSW index:**
```sql
-- Store quantised bits alongside float32 vectors
ALTER TABLE embeddings ADD COLUMN embedding_bits bit(1536);
UPDATE embeddings SET embedding_bits = binary_quantize(embedding)::bit(1536);

CREATE INDEX ON embeddings
  USING hnsw (embedding_bits bit_hamming_ops)
  WITH (m = 16, ef_construction = 64);
```

**Step (b) — Inner query: fast first pass via Hamming distance:**
```sql
-- Returns N×K candidates ordered by Hamming distance
SELECT id, embedding
FROM embeddings
ORDER BY embedding_bits <~> binary_quantize($query_embedding)::bit(1536)
LIMIT :n_times_k;
```

**Step (c) — Outer query: rescore by original float32:**
```sql
-- Rescore the N×K candidates with full-precision cosine distance
SELECT id
FROM (
  <inner query above>
) candidates
ORDER BY embedding <=> $query_embedding
LIMIT :k;
```

**When BQ is a poor fit:**
- Embedding dimension < 512 — quantisation noise dominates recall loss; BQ-without-rescore loses ~5–17% recall on short vectors.
- Corpus requires exact per-query ordering — use `halfvec` (2×) or int8 (4×) instead.

Evidence: HuggingFace embedding-quantization blog (~96% recall at 32× storage with rescore); jkatz05 pgvector benchmarks confirm the rescore step is load-bearing.

## Sharding And Partitioning

Past the single-node ceiling, the graph has to be split. Three patterns,
in order of preference:

1. **Tenant / namespace shard** — partition by tenant_id, region, or
   corpus_version. Each shard is an independent HNSW/DiskANN graph; the
   query router picks one. Cleanest semantics, no cross-shard recall
   problem. First choice when the shape allows it.
2. **Hash shard with broadcast** — random shard assignment, query goes to
   all shards, top-K merged at the router. Simplest to scale, but every
   query pays the fan-out tax.
3. **Learned partition (IVF-style centroid routing)** — coarse k-means
   over the embedding space, query touches only the M closest centroids'
   shards. Faiss/Milvus/Vespa do this natively; bolting it onto pgvector
   is operational pain, not a clean win.

If you find yourself reaching for #3 on top of pgvector, that is the signal
to migrate the workload to Milvus, Vespa, or Qdrant rather than rebuild
their cluster machinery in SQL.

## Graph-Augmented Retrieval

This is where the **knowledge graph** earns its keep. Three composition
patterns, all on top of whatever ANN engine you picked:

### 1. Graph-Bounded Retrieval (filter the candidate region)

Walk the knowledge graph from the query's anchor entities to a candidate
node set, then run hybrid retrieval restricted to those nodes:

```text
query
  ↓
[anchor extraction → seed nodes in knowledge graph]
  ↓
[BFS / k-hop walk → candidate node_ids]
  ↓
[hybrid_retrieve_context(... WHERE node_id = ANY(:candidates))]
  ↓
[rerank → top-K]
```

Cuts recall@K by far less than expected and cuts irrelevant top-K returns
to near zero on selective questions ("what controls implement clause X
under authority Y as of date Z"). Already shipped as a deferred extension —
see [deferred-extensions.md](deferred-extensions.md#graph-bounded-retrieval).

### 2. Personalized PageRank Re-Scoring (rerank by graph proximity)

Run hybrid retrieval, then re-rank candidates by PPR score seeded at the
query's anchor entities. Surfaces "the chunk people who cited this would
also cite" answers that pure embedding similarity misses.

The skills already ship two PPR runners that work directly:

```bash
# Single-repo / context graph PPR (dev-context-engineering)
python3 ../dev-context-engineering/scripts/query_context_graph.py \
  context-graph.json --ppr --seed "doc:policies/aml.md#kyc-thresholds" --top 50

# Portfolio / multi-repo knowledge graph PPR (dev-context-multi-repo)
python3 ../dev-context-multi-repo/scripts/query_graph.py \
  knowledge-graph.json --ppr --seed entity:Customer --top 50
```

Both emit ranked node ids. Use those as a candidate set or as a re-rank
signal alongside the cross-encoder rerank score. Do **not** rebuild PPR
inside the vector brain — reuse these.

### 3. Community-Bounded Retrieval (Louvain partition → community summary)

Run Louvain over the knowledge graph, generate a per-community summary,
and at query time first pick the relevant community via summary similarity
before retrieving inside it. This is the GraphRAG pattern (Microsoft) at
its core. The Louvain runner already exists:

```bash
python3 ../dev-context-multi-repo/scripts/query_graph.py \
  knowledge-graph.json --communities --resolution 1.0
```

Pair with `assets/community-summary-template.md` in `dev-context-multi-repo`
for synthesis-heavy corpora. Full GraphRAG/LightRAG integration remains
deferred — see [deferred-extensions.md](deferred-extensions.md#knowledge-graph-hybrid-graphrag-lightrag).

## Reusing The Existing Graph Infra

The portfolio already contains production-grade graph machinery. Do not
rebuild it inside ai-vector-brain.

| Need | Use this | Why |
|---|---|---|
| Per-repo code graph (symbol/import/call) | [dev-context-code-graph](../../dev-context-code-graph/SKILL.md) | Articulation points, bridges, blast radius, PPR over symbols. Direct input to graph-bounded retrieval over a code corpus. |
| Cross-repo knowledge graph | [dev-context-multi-repo](../../dev-context-multi-repo/SKILL.md) | Repo profiles, edge calibration, Louvain communities, bitemporal slices. |
| AGENTS.md / context-graph layer | [dev-context-engineering](../../dev-context-engineering/SKILL.md) | PPR over context artifacts, tier-budget queries, supersession integrity. |
| RAG retrieval theory (vector + lexical, fusion) | [ai-rag](../../ai-rag/SKILL.md) | Library-agnostic patterns for hybrid retrieval. |
| Where context lives (memory vs retrieval vs tools) | `ai-context-layer` | Boundary owner for the broader context strategy. |

The brain's job is the **vector index** + **hybrid retrieval** + **rerank**.
The graphs above are inputs to bounding, re-scoring, and partitioning the
brain — not replacements for it.

## Scale Decision Table

Pick by `(N, filter selectivity, RAM budget, ops appetite)`:

| Scale (N chunks) | Index | Quantization | Graph augmentation |
|---|---|---|---|
| ≤ 1M | pgvector HNSW (m=16) | none | optional; PPR if corpus has rich link structure |
| 1M – 10M | pgvector HNSW (m=24) | `halfvec` for >2000-dim | graph-bounded retrieval if filters are multi-hop |
| 10M – 50M | pgvector HNSW (m=32–48) or pgvectorscale DiskANN | `halfvec` + SBQ (DiskANN path) | PPR re-score on top of hybrid |
| 50M – 500M | pgvectorscale DiskANN, or migrate to Qdrant/Milvus/Vespa | SBQ / PQ + rescore | Louvain communities + community-bounded retrieval |
| ≥ 500M | Dedicated vector cluster (Milvus, Vespa, Qdrant), shard by tenant or learned partition | PQ + rescore (mandatory) | Full GraphRAG-style hybrid; knowledge graph is the entry point, ANN is the second stage |

Verify the boundary numbers against your hardware and recall targets.
These are operating-experience defaults, not constants.

## Anti-Patterns

- **Treating HNSW as "infinite scale."** It is bounded by build RAM and the
  m × ef_search × log(N) latency curve. Plan the escalation path before
  N gets there.
- **Quantizing without rescore.** PQ/BQ recall numbers in vendor docs
  assume the rescore step. Skipping it converts "5% recall hit" into "20%
  recall hit" silently.
- **Rebuilding PPR or Louvain inside the brain.** The runners in
  `dev-context-code-graph`, `dev-context-engineering`, and
  `dev-context-multi-repo` are already calibrated, evaluated, and tested.
- **Mixing the index graph and the knowledge graph in one schema.** They
  have opposite update cadences and opposite access patterns. Keep them
  in separate tables (or separate stores) and join at query time.
- **Using IVF-style learned partitioning on top of pgvector.** That is a
  signal to migrate the workload, not to extend the SQL surface.
- **Sharding by random hash when tenant/namespace boundaries exist.**
  Broadcast queries cost more than the routing simplicity is worth.
- **Pretending "GraphRAG" with no actual graph.** A flat list of chunks
  with cosine similarity is still vanilla RAG; calling it GraphRAG because
  the response is bulleted does not change retrieval recall.
- **Optimizing index parameters before you have evals.** ef_search,
  query_search_list_size, and rescore counts only mean something against
  a labeled retrieval set. Build the eval first.

## See Also

- [postgres-pgvector-default.md](postgres-pgvector-default.md) — V1 HNSW
  parameters and the `halfvec` / `pgvectorscale` escalation note.
- [backend-selection.md](backend-selection.md) — when to leave Postgres for
  Qdrant, Weaviate, Milvus, Vespa, or LanceDB.
- [reranking-recipe.md](reranking-recipe.md) — the always-app-layer
  cross-encoder stage that closes the recall gap quantization opens.
- [contextual-retrieval.md](contextual-retrieval.md) — index-time lift
  that reduces dependence on raw ANN recall.
- [deferred-extensions.md](deferred-extensions.md) — graph-bounded
  retrieval, GraphRAG / LightRAG, ColBERT/ColPali integration paths.
- [dev-context-code-graph](../../dev-context-code-graph/SKILL.md),
  [dev-context-multi-repo](../../dev-context-multi-repo/SKILL.md),
  [dev-context-engineering](../../dev-context-engineering/SKILL.md) — the
  graph-building, PPR, and Louvain infrastructure to compose with.
