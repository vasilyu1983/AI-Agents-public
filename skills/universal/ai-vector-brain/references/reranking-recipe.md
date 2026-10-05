# Reranking Recipe — pgvector Implementation

Two-stage retrieval: ANN/hybrid first stage produces a deep candidate list,
then a **cross-encoder reranker** rescores the top-N to produce the final
top-K passed to the generator. Reranking is **always app-layer**, never in
the database. Anthropic's Contextual Retrieval study reports ~67% fewer retrieval failures
when rerank is layered on top of hybrid + contextual. **For reranking theory
and model comparisons, see `ai-rag/references/ranking-pipeline-guide.md` (the owning skill for
retrieval theory) — this file covers the pgvector-specific candidate-fetch
and cost recipe.**

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

| Reranker class | When to pick | Hosting |
|---|---|---|
| Hosted rerank API from your embedding vendor | Default for hosted stacks; one vendor contract and key | Vendor API |
| Cloud-provider rerank API (in-region, IAM-scoped) | Default when the stack already runs on that cloud's knowledge-base retrieval | Cloud provider |
| Open-weights cross-encoder | Self-hosted requirement, on-prem, data residency, cost floor | Local GPU |
| Multilingual or long-context reranker | Mixed-language corpora or chunks longer than a standard cross-encoder window | Hosted or self-hosted |

Pick the class here, then look up current model names, context windows,
licences (some open-weight rerankers are non-commercial), and prices in the
vendor docs at decision time. The criteria for choosing within a class are in
[ai-rag ranking-pipeline-guide.md](../../ai-rag/references/ranking-pipeline-guide.md#5-reranking-stage).

## Sizing N And K

The budget rule for N (candidates sent to the reranker) and K (items kept)
is owned by
[ai-rag ranking-pipeline-guide.md](../../ai-rag/references/ranking-pipeline-guide.md#5-reranking-stage);
set both from your eval set, not from this file. The pgvector-specific part:

- Fetch N from `hybrid_retrieve_context(...)` with `match_count = N`, and keep
  `candidate_count >= N` (each leg is capped at `candidate_count` before fusion).
- Pass the caller's ACL scope (`p_acl_scope`) on that call, so the N
  candidates are already filtered. Never ACL-filter the reranked list.
- Rerank cost is linear in N; price it with Formula 5 in
  [cost-calculation.md](cost-calculation.md).

## API Recipes

### Hosted API (Voyage SDK)

```python
import voyageai

vo = voyageai.Client()  # reads VOYAGE_API_KEY

reranked = vo.rerank(
    query=query_text,
    documents=[c["content"] for c in candidates],
    model=RERANK_MODEL,  # current model id from the vendor docs
    top_k=8,
)

# reranked.results: list of {index, relevance_score, document}
ordered = [candidates[r.index] for r in reranked.results]
```

### Hosted API (Cohere SDK)

```python
import cohere

co = cohere.Client()  # reads COHERE_API_KEY

resp = co.rerank(
    query=query_text,
    documents=[c["content"] for c in candidates],
    model=RERANK_MODEL,  # current model id from the vendor docs
    top_n=8,
)

ordered = [candidates[r.index] for r in resp.results]
```

### Self-hosted cross-encoder (FlagEmbedding)

```python
from FlagEmbedding import FlagReranker

reranker = FlagReranker(RERANK_MODEL_PATH, use_fp16=True)  # check the weights' licence

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
    acl_scope: dict | None,
    top_n_for_rerank: int,
    top_k_final: int,
    rerank_model: str,
):
    # ACL is applied inside the SQL call (candidate generation), never to the
    # reranked list. acl_scope=None means public chunks only.
    candidates = call_hybrid_search(
        query, match_count=top_n_for_rerank, acl_scope=acl_scope
    )
    if not candidates or len(candidates) <= top_k_final:
        return candidates
    return rerank(query, candidates, model=rerank_model, top_k=top_k_final)
```

The hybrid search call should be `hybrid_retrieve_context(...)` from
`assets/sql/003_hybrid_search_function.sql` with `match_count` set to
`top_n_for_rerank` (not the final K), `candidate_count >= match_count`, and
`p_acl_scope` set to the caller's scope.

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

Latency and price change with each model release, so this file keeps no
table. Measure p95 latency for reranking N candidates at your chunk length on
your hardware or the vendor API. Price hosted rerankers with Formula 5 in
[cost-calculation.md](cost-calculation.md), using the per-search or
per-token rate from the vendor's pricing page; self-hosted cost is the GPU
server cost.

For local rerankers, batch all candidates in a single call. Streaming or
per-candidate calls 50× the cost.

## Anti-Patterns

- **Reranking inside the database.** Cross-encoder inference does not belong
  in SQL. The reranker is an app-layer concern, period.
- **Rerank without oversampling.** Calling rerank with N == K throws away
  the entire point. Always over-fetch first.
- **ACL-filtering after retrieval or rerank.** Over-fetching without the ACL
  predicate and dropping rows afterwards returns fewer than K results and
  lets unseen rows shape the ranking. Pass `p_acl_scope` to the SQL call.
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
