# Cookbook: Latency and Cost

Concrete budgets and recipes for keeping a context layer fast and cheap.
Numbers are illustrative ratios, not prices. Take every rate from your
provider's current price page before quoting a figure.

## The five levers, in order of leverage

1. **Smaller bundle** beats faster compress. Cutting tokens in half
   roughly halves cost and cuts latency more than that (attention is
   not linear in tokens at long context).
2. **KV-cache hits** beat better models. A cache hit costs a small
   fraction of a cache miss on the prefix portion (ratio from the provider's price page). Make your prompt prefix invariant
   across turns (see `order` recipe below).
3. **Just-in-time selection** beats compression. Not assembling 8K
   tokens of memory you don't need is cheaper than compressing it down
   to 2K.
4. **Cheaper model for sub-tasks** beats slower main model. Sub-agents
   (`isolate`) can run a small/fast model; only the parent needs the
   big one.
5. **Fewer evidence chunks** beats better reranker. Top-3 reranked
   beats top-20 unreranked at lower latency.

## Token budgets that actually work

A starting set of per-surface budgets the reference assembly layer
defaults map onto. Tune with your eval suite (Phase 4) — these are
priors, not laws.

| Surface | Total budget | live_facts | memory | evidence | guardrails | History |
|---------|--------------|------------|--------|----------|------------|---------|
| Chat (chatty) | 8,000 | 500 | 1,000 | 2,000 | 200 | rest |
| Chat (transactional) | 4,000 | 500 | 500 | 1,500 | 200 | rest |
| Dashboard / inline assist | 2,500 | 800 | 500 | 1,000 | 100 | n/a |
| Email (long-form draft) | 12,000 | 500 | 1,500 | 4,000 | 200 | rest |
| Background agent (long-horizon) | 8,000 base + sub-agents | 500 | 1,500 | 2,000 | 200 | compacted |

Defaults assume a model with ≥200K context. For smaller models, scale
the whole row down by the ratio.

## KV-cache layout: the cheap performance win

Anthropic and OpenAI both cache identical input prefixes across calls.
Cache hits typically cost 10–25% of a miss on the cached portion and
shave 30–60% off TTFT (time-to-first-token). The whole game is keeping
the *front of every prompt identical, every turn*.

The reference app's `order` verb enforces this layout. Wire it into
your prompt template like:

```
[ system prompt — frozen for the surface ]
[ tool definitions — frozen for the surface ]
[ persistent memory block — only changes when memory changes ]
[ retrieved evidence — changes per turn (this is fine) ]
[ conversation history — changes per turn (also fine) ]
[ current user turn ]
```

Concretely, the cache hits everything from the top down to the *first*
varying byte. Two common ways to break this without realizing:

1. **Putting a timestamp in the system prompt.** Caches miss every
   request. Put the timestamp in the user turn instead.
2. **Sorting tool definitions by relevance per request.** Same effect.
   Define them once, in alphabetical order, forever.
3. **Re-summarizing history every turn with `compress(strategy="summarize")`.**
   The summary text changes turn-to-turn, busting the cache from that
   row onward. Compact in batches (every N turns), not every turn.

## Cost estimation worksheet

Per request, the cost is dominated by input tokens at long context.
Order-of-magnitude formula:

    request_cost ≈ input_tokens × input_rate + output_tokens × output_rate
    cache_savings ≈ cached_input_tokens × (input_rate − cached_input_rate)

Take the cached input rate from the provider's price page. As a worked
example, if the cached rate is 10% of the fresh rate and 70% of your input
is cacheable and hits, you cut input cost by 70% × 90% = 63%.

Per-request cost example (illustrative, not pricing advice):

| Setup | Input | Output | Notes |
|-------|-------|--------|-------|
| Naive — full history every turn, no cache | 12K | 600 | baseline |
| + `order` for cache-friendly layout | 12K (8K cached) | 600 | input cost cut ~58% |
| + just-in-time `select` (drop unused memory) | 6K (4K cached) | 600 | additional ~45% input savings |
| + sub-agent for the analysis step | 3K parent + 4K sub | 200 + 400 | parent stays small |

## Latency budget anatomy

A typical end-to-end interactive request, p50:

```
   network ingress             5 ms
   bundle assembly            30–80 ms   (parallel: select + retrieve)
     ├─ memory.recall          10–30 ms
     ├─ retrieval.retrieve     20–60 ms (incl. embedding + reranker)
     └─ toolkit.fetch_live      5–20 ms (depends on your services)
   prompt order/compress       <5 ms
   LLM TTFT                  300–900 ms (huge cache effect here)
   LLM streaming             ~30–80 tok/s for the response
   feedback write              <5 ms (async)
```

Two failure modes that show up here:

- **TTFT > 1.2s consistently** → cache busted. Audit the prefix.
- **Bundle assembly > 200ms** → adapters serial, not parallel. Use
  `asyncio.gather` (or `concurrent.futures`) on the three select calls.

## When `compress` is too expensive

`compress(strategy="summarize")` calls the LLM. At 10 evidence items
per request, that's 10+ extra LLM calls. Use it only when:

- Your bundle is regularly >70% over budget (otherwise truncation is
  fine and free)
- Each item carries load-bearing detail you cannot afford to drop
- You can run summarize on a cheaper model (often a smaller Haiku-tier
  model is enough)

If neither holds, stay with `progressive_disclosure`.

## Embedding cost ceiling

A common cost trap: re-embedding the corpus on every nightly job. Don't.

- Embed only when `KnowledgeSource.content_hash` changes.
- For chunk-level changes, re-embed only the changed chunks.
- Local embedding models (BGE, Nomic) are now within ~5 BERT-points of
  hosted models for retrieval and cost ~zero per call. Worth the swap
  if your corpus is large and stable.

## Sub-agent cost discipline

`isolate(...)` is cheap if you constrain it:

- Always pass `max_tokens` — without it, sub-agents will use the parent
  budget by accident.
- Use a smaller model for the sub-task than the parent. The cited-id
  validation in `isolate()` catches the worst quality regressions.
- For long-horizon tasks, the sub-agent should consume a stale snapshot
  of the parent bundle, not a fresh assembly. Cache the snapshot.

## Where to measure

The only honest way to budget is to measure. Add these to your
observability stack on day one:

| Metric | Why it matters |
|--------|----------------|
| TTFT histogram per surface | Cache-hit health |
| Input tokens per request, p50/p95 | Bundle bloat detection |
| `compress` invocation rate | Tells you whether your budgets are right |
| Sub-agent dispatch rate per parent | F2 escape hatch usage |
| Cache hit ratio (provider-reported) | The single best lever signal |
| Evidence items returned per query, p50/p95 | Reranker truncation health |

Your assembly layer gets faster and cheaper in the order you instrument
these. You will tune the wrong thing without them.
