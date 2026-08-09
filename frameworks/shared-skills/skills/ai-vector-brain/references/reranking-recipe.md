# Reranking Recipe

Two-stage retrieval: ANN/hybrid first stage produces a deep candidate list,
then a **cross-encoder reranker** rescores the top-N to produce the final
top-K passed to the generator. Reranking is **always app-layer**, never in
the database.

Reranking is the single largest accuracy lever after retrieval is wired up.
Anthropic's Contextual Retrieval study reports ~67% reduction in retrieval
failures when rerank is layered on top of hybrid + contextual.

## Table of Contents

- [The Pattern](#the-pattern)
- [Reranker Choice](#reranker-choice)
- [Sizing N And K](#sizing-n-and-k)
- [API Recipes](#api-recipes)
- [When To Use](#when-to-use)
- [When To Skip](#when-to-skip)
- [Cost And Latency](#cost-and-latency)
- [Anti-Patterns](#anti-patterns)

## The Pattern

```text
query
  ↓
[hybrid retrieval: vector + lexical → RRF]   ← top-N (oversampled, 20–100)
  ↓
[cross-encoder reranker: scores (query, chunk) jointly]
  ↓
top-K passed to generator                     ← typically 4–12
```

The reason this works: a bi-encoder (dense embedding) compresses the query
and the chunk into separate vectors and only sees their dot product. A
cross-encoder reads query + chunk together, attending across both, and
captures interactions a single dot product cannot. It is too expensive to
run over the full corpus, but cheap enough on the top-N candidate window.

## Reranker Choice

Decision rule: pick by license/hosting first, quality second. Quality
differences on most corpora are within a few points of each other; cost,
latency, and licensing are the load-bearing axes.

| Reranker | Type | When to pick | Hosting |
|---|---|---|---|
| **Voyage Rerank 2.5** | Hosted API | Default for hosted stacks; strong on technical, code, multilingual | Voyage AI |
| **Cohere Rerank 3.5** | Hosted API | Default when already on Cohere stack; strong general-purpose | Cohere |
| **Amazon Bedrock Rerank API** | Hosted API | Default on AWS — serves Cohere Rerank 3.5 + Amazon Rerank in-region, IAM-scoped; wired natively into Bedrock KB retrieval | AWS Bedrock |
| **BGE-reranker-v2-M3** | Open weights (MIT) | Self-hosted requirement, on-prem, EU data residency, cost floor | Run locally on GPU |
| **Jina Reranker v2** | Hosted or self-hosted | Multilingual, long-context (8k tokens), permissive license | Jina or self |
| **mxbai-rerank-large-v2** | Open weights (Apache 2.0) | Open-weights alternative if BGE is undesirable | Run locally |

Verify pricing, model names, context windows, and benchmark positioning
against current vendor docs before committing — the reranker market moves
faster than the embedding-model market.

## Sizing N And K

- **N (rerank input)**: 20 for default, 50 for high-recall corpora (compliance,
  citation-precision-critical), up to 100 if a single API call covers it.
- **K (final top)**: 4–8 for chat, 8–12 for compliance/citation, 12–20 for
  exploratory research surfaces.

Rule of thumb: `N ≈ 5–10x K`. Below 3x, you starve the reranker of
candidates and lose its lift. Above 15x, you spend latency for no measurable
recall gain — verify on your eval set.

## API Recipes

### Voyage Rerank 2.5

```python
import voyageai

vo = voyageai.Client()  # reads VOYAGE_API_KEY

reranked = vo.rerank(
    query=query_text,
    documents=[c["content"] for c in candidates],
    model="rerank-2.5",
    top_k=8,
)

# reranked.results: list of {index, relevance_score, document}
ordered = [candidates[r.index] for r in reranked.results]
```

### Cohere Rerank 3.5

```python
import cohere

co = cohere.Client()  # reads COHERE_API_KEY

resp = co.rerank(
    query=query_text,
    documents=[c["content"] for c in candidates],
    model="rerank-v3.5",
    top_n=8,
)

ordered = [candidates[r.index] for r in resp.results]
```

### BGE-reranker-v2-M3 (self-hosted)

```python
from FlagEmbedding import FlagReranker

reranker = FlagReranker("BAAI/bge-reranker-v2-m3", use_fp16=True)

pairs = [[query_text, c["content"]] for c in candidates]
scores = reranker.compute_score(pairs, normalize=True)

ranked = sorted(zip(candidates, scores), key=lambda x: x[1], reverse=True)
ordered = [c for c, _ in ranked[:8]]
```

### End-To-End Wrapper

```python
def hybrid_retrieve_then_rerank(
    query: str,
    *,
    top_n_for_rerank: int = 50,
    top_k_final: int = 8,
    rerank_model: str = "voyage/rerank-2.5",
):
    candidates = call_hybrid_search(query, n=top_n_for_rerank)
    if not candidates or len(candidates) <= top_k_final:
        return candidates
    return rerank(query, candidates, model=rerank_model, top_k=top_k_final)
```

The hybrid search call should be `hybrid_retrieve_context(...)` from
`assets/sql/003_hybrid_search_function.sql` with `final_limit` set to the
oversample size (`top_n_for_rerank`), not the final K.

## When To Use

- Default-on for compliance, policy, and citation-critical corpora
- Recall@5 below 0.85 on the eval set after hybrid is wired up
- High-stakes generation surface (legal, medical, financial advice) where the
  precision of the top-1 chunk dominates user-perceived quality
- Corpora with many near-duplicate or topically-adjacent chunks where
  semantic + lexical fusion alone leaves the wrong one on top

## When To Skip

- Latency budget < 200ms p95 and reranker adds > 100ms — measure first
- Tiny corpora (< 5k chunks) where simple retrieval already nails it
- Exploratory/discovery surfaces where K is large (> 20) and ordering inside
  the window matters less than coverage
- Ingest-time-bound corpora where eval is not yet in place — rerank without
  evals invites silent regressions

## Cost And Latency

Rough order of magnitude (verify against current pricing):

| Reranker | Latency (50 chunks, ~512 tok each) | Cost per 1k queries |
|---|---|---|
| Voyage Rerank 2.5 | ~80–150 ms | ~\$0.05–\$0.10 |
| Cohere Rerank 3.5 | ~80–150 ms | ~\$0.10–\$0.20 |
| BGE-v2-M3 self-hosted (single A10G) | ~100–200 ms | server cost only |
| Jina Reranker v2 (hosted) | ~80–150 ms | ~\$0.05–\$0.10 |

For local rerankers, batch all candidates in a single call. Streaming or
per-candidate calls 50× the cost.

## Anti-Patterns

- **Reranking inside the database.** Cross-encoder inference does not belong
  in SQL. The reranker is an app-layer concern, period.
- **Rerank without oversampling.** Calling rerank with N == K throws away
  the entire point. Always over-fetch first.
- **Trusting the rerank score as a calibrated probability.** Different models
  produce different score ranges. Use it for ordering only, not for
  thresholding without a model-specific calibration step.
- **Skipping rerank but still claiming "RAG with reranking" in marketing.**
  The eval gates need to reflect the actual stack.
- **Mixing reranker outputs from different models in the same evaluation
  cohort.** Score distributions diverge; eval comparisons become noise.
- **Re-running rerank when the candidate list didn't change.** Cache by
  `(query_hash, candidate_id_set, rerank_model_id)`.
- **Forgetting to update `model_id`-style provenance** when changing
  rerankers. Eval regressions become unattributable.

For the upstream candidate generator, see `postgres-pgvector-default.md`
(Hybrid Retrieval). For where reranker output is surfaced to agents, see
`agent-tool-contract.md` (the `rerank_score` field).
