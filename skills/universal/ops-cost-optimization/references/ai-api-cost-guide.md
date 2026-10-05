# AI API Cost Guide

Operational reference for understanding and reducing AI API spend. Covers provider pricing, cost drivers ranked by impact, and a repeatable optimization checklist.

## Table of Contents

- [Pricing Overview](#pricing-overview)
- [Cost Model](#cost-model)
- [Plan-Tier Users vs API Users](#plan-tier-users-vs-api-users)
- [Cost Drivers](#cost-drivers)
  - [Model Selection](#model-selection)
  - [Token Volume](#token-volume)
  - [Prompt Caching](#prompt-caching)
  - [Batch API](#batch-api)
  - [Fine-Tuning Costs](#fine-tuning-costs)
  - [Embeddings](#embeddings)
- [Cost Management Strategies](#cost-management-strategies)
  - [Token Budget Management](#token-budget-management)
  - [Caching Layers](#caching-layers)
  - [Model Routing](#model-routing)
  - [Rate Limiting and Quotas](#rate-limiting-and-quotas)
- [Monitoring](#monitoring)
- [LLM Cost Governance](#llm-cost-governance)
  - [Model Cascading and Routing](#model-cascading-and-routing)
  - [Semantic Caching](#semantic-caching)
  - [Per-Trace and Per-User Cost Attribution](#per-trace-and-per-user-cost-attribution)
- [Self-Hosted / Open-Weight Inference](#self-hosted--open-weight-inference)
  - [Breakeven: Self-Hosted vs API](#breakeven-self-hosted-vs-api)
- [Common Optimization Checklist](#common-optimization-checklist)

---

## Pricing Overview

Prices are per million tokens (MTok). Output tokens are consistently more expensive than input tokens across all providers.

This guide keeps no rate table: rates change within weeks. Before a recommendation or budget decision, read the per-model rates from the vendor's pricing page (Anthropic: https://claude.com/pricing; OpenAI: https://developers.openai.com/api/docs/pricing; Google: https://ai.google.dev/gemini-api/docs/pricing) and record the date next to each figure. The decision they feed is model routing, caching, and batch choices below.

Gotchas from past errors in this guide's own tables:

- Introductory prices do not always revert on schedule. A table that recorded "promo until date X, then list price" went wrong when the vendor made the promo rate permanent. Check the page, not the recorded end date.
- A retired model's rate is the most common stale figure in a customer's cost model, especially when a successor has a similar name. Match the exact model identifier to its row on the pricing page.
- Providers rename and re-tier model families. Confirm the current tier name and rate card on the vendor's pricing page before quoting a number.
- Cached-input and cache-write rates drift separately from input/output rates. A table whose input/output rates are correct can still misprice cache-heavy traffic badly.
- One model can carry several rates: standard vs batch or flex tiers, short vs long context, cache write vs cache hit. Price each request at the tier and context length it actually runs at.
- If a vendor's model fallback is enabled, some requests bill at the fallback model's rate. Budget at the blended rate you observe, not the primary model's rate.
- When a rate is marked promotional, write its end date into the cost model and re-check the page before and after that date.

---

## Cost Model

Treat prices as inputs to formulas, never as constants in a design doc. Keep rates in versioned configuration and put the price version and check date in every cost report.

```text
cost_per_request   = uncached_input_tokens × input_rate + output_tokens × output_rate
                     + cache_write_tokens × write_rate + cache_hit_tokens × hit_rate
cost_per_success   = total_AI_spend / successful_completions
monthly_TCO        = token spend + embeddings + vector DB + serving infra
                     + logging/observability + loaded engineering and on-call time
gross_margin       = (revenue − monthly_TCO) / revenue
```

Treat `uncached_input_tokens`, `cache_write_tokens`, and `cache_hit_tokens` as mutually exclusive input buckets. Map the provider's current usage fields and invoice categories into those buckets before calculating cost; do not add cached tokens again if a reported `input_tokens` field already includes them. Count reasoning tokens in the category and rate the provider actually bills, rather than assuming a universal mapping.

- Gate on cost per successful outcome, not cost per token. Retries, escalations, and human fallback raise it even when token efficiency improves (see [cloud-commitment-and-k8s-cost-guide.md](cloud-commitment-and-k8s-cost-guide.md#ai-spend-governance-for-platforminfra-leads)).
- Choose between candidate models by quality per dollar, subject to a minimum quality bar measured on your own eval set. A cheaper model below the bar is not a saving.

---

## Plan-Tier Users vs API Users

This guide defaults to API billing: rates per MTok, prompt caching, batch tiers and quota dashboards. Plan-tier users (flat monthly subscriptions) pay a fixed fee with usage limits per rolling window, so the lever is how much of the window each task consumes, not a per-token bill.

- **Context is the unit of spend on both.** Every turn re-sends the conversation, so long single conversations amplify use. Start a fresh conversation for unrelated work, and summarize or compact deliberately rather than carrying stale context.
- **Plan before expensive work.** An agent that proposes an approach before editing avoids paying twice for a wrong direction.
- **Lower reasoning effort for routine work.** Reasoning tokens bill as output; reserve high effort for tasks that need it.
- **Parallel agents multiply spend.** Each subagent or teammate holds its own context. For coding-agent session levers and team costs, see [ai-coding-agents-state](../../ai-coding-agents-state/SKILL.md) and [multi-agent coding patterns](../../ai-coding-agents/references/multi-agent-coding-patterns.md#cost-every-teammate-is-a-full-context).
- **Plan limits and how products share them change.** Read the current plan terms before budgeting a team on subscriptions versus API keys.

---

## Cost Drivers

Ranked by typical impact on total spend.

### Model Selection

The single biggest cost lever. The price gap between model tiers is often an order of magnitude or more (read it from the pricing data), and on simple workloads a cheaper tier often holds the quality bar.

- **Common waste:** Using a premium-tier model for tasks a value-tier model handles well — classification, entity extraction, simple QA, formatting.
- **Optimization:** Implement model routing. Use cheap models for classification, extraction, and simple QA. Reserve expensive models for complex reasoning, long-form generation, and coding. Measure quality at each tier to find the cheapest model that meets the bar.

| Quality need | Volume | Starting choice |
|---|---|---|
| Critical | Low | Premium tier |
| Critical | High | Balanced tier plus fine-tuning or distillation, once an eval shows it holds the bar |
| User-facing | Medium | Balanced tier |
| Internal, acceptable | High | Value tier |
| Mixed | Any, budget-bound | Cascade (see [Model Cascading and Routing](#model-cascading-and-routing)) |

### Token Volume

Input and output tokens are the direct unit of cost. Output tokens cost several times more than input tokens; read the ratio for the model in use from the pricing data.

- **Common waste:** Sending full documents when summaries suffice. Not trimming conversation history. Including verbose system prompts in every turn. Allowing unconstrained output length.
- **Optimization:** Trim the context window aggressively. Summarize long conversations instead of forwarding full history. Use structured output (JSON, enums) to reduce output token count. Remove unused system prompt sections per request type.

### Prompt Caching

Repeated prompt prefixes can be served from cache at a steep discount.

- **Anthropic:** A cache write carries a premium over base input (higher for the longer TTL) and a cache hit a steep discount. Both multipliers are per model: the hit rate is not always 0.1x of input, so read `cache_write_per_1m` and `cache_read_per_1m` for the model from the pricing data. With illustrative multipliers of 1.25x write (shorter TTL) or 2x write (longer TTL) and a 0.1x hit, a 5-minute cache pays for itself after one hit and a 1-hour cache after two; below that, caching costs more than not caching. Redo that arithmetic with the model's own multipliers.
- **OpenAI:** Similar caching mechanics for repeated prompt prefixes; verify current cache-hit discount and TTL against the live pricing page, as the discount rate has varied by generation.
- **The cache belongs to one model.** Switching models mid-conversation starts a new cache, so the next request pays a full write. Choose the model per session or per workflow step, not per turn.
- **Minimum cacheable length is model-specific.** Check the provider's caching docs for the current minimum prefix length, TTL options, and write/hit rates before designing around a cache.
- **Where caching pays:** static system prompts and tool definitions, RAG with a stable shared context, and multi-turn conversations whose history prefix repeats. Prompts whose prefix changes on every request rarely pay back the write premium.
- **Model ROI with the hit rate `h` you observe**, not the best case. For N requests sharing a P-token prefix: `uncached = N × P × input_rate`; `cached ≈ N × P × (h × hit_rate + (1 − h) × write_rate)`. Cache only when `cached < uncached`.
- **Optimization:** Structure prompts with the static system prompt first and dynamic content last. Reuse conversation prefixes across requests. Batch requests that share the same system prompt to maximize cache hits. Do not cache prefixes reused fewer than once per TTL window — the write premium turns it into a net cost increase.

### Batch API

Non-real-time workloads qualify for significant discounts.

- **Anthropic and OpenAI:** both sell a discounted batch tier; read the current discount and turnaround window from the pricing page.
- **Optimization:** Use batch API for offline analysis, bulk content generation, data processing, and evaluation runs — anything that does not need sub-second response. Queue work during off-peak hours when possible.

### Fine-Tuning Costs

Fine-tuning has an upfront training cost (per token) plus ongoing inference cost, which is often cheaper than the base model at volume.

- **When it is worth it:** High-volume, repetitive task where a fine-tuned small model replaces a large model. Examples: structured extraction at scale, domain-specific classification, consistent tone/format generation.
- **Break-even analysis:** Compare the fine-tuning training cost plus fine-tuned inference cost versus the saved inference cost of the larger model over 3-6 months. Factor in retraining frequency when the task evolves.

### Embeddings

Embedding models cost far less per token than generation models; read the current rate from the vendor pricing page.

- **Common waste:** Re-embedding unchanged content on every pipeline run. Using unnecessarily large embedding models. Embedding entire documents instead of meaningful chunks.
- **Optimization:** Cache embeddings and only re-embed changed content. Use incremental indexing. Choose the smallest embedding model that maintains retrieval quality — run a retrieval eval before upgrading model size.

---

## Cost Management Strategies

### Token Budget Management

- Set `max_tokens` on every request to prevent runaway output.
- Check estimated cost before the call against hard caps: per-request cost, per-request tokens, and remaining daily budget. Reject or queue the request when a cap would be exceeded; do not let it run and alert afterwards.
- Prune few-shot examples and system-prompt sections to the smallest set that holds eval quality, and re-run the eval after each cut.
- Track token usage per feature and per endpoint, not just aggregate spend.
- Implement cost attribution by feature so teams own their consumption.

### Caching Layers

Three levels, each with different hit rates and implementation cost:

1. **Application-level cache:** Cache identical prompt-response pairs. Cheapest to implement, highest precision.
2. **Semantic cache:** Cache responses for similar (not identical) queries using embedding similarity. Higher hit rate, requires quality threshold tuning.
3. **Prompt caching:** Structure prompts to maximize provider-side prefix reuse. No application code needed beyond prompt ordering.

### Model Routing

- **Classifier approach:** A lightweight classifier (or the cheap model itself) decides whether the task needs a cheap or expensive model.
- **Fallback chains:** Try the cheap model first. If confidence is low or output quality fails a check, escalate to the expensive model.
- **A/B testing:** Run quality evals across model tiers to find the cheapest model that meets the quality bar for each task type.

### Rate Limiting and Quotas

- Set spending limits in provider dashboards (both Anthropic and OpenAI support this).
- Implement per-user or per-feature rate limits in your application layer.
- Alert on unexpected usage spikes before they become budget problems.

---

## Monitoring

Track these metrics continuously:

- **Cost per request** — identifies expensive endpoints.
- **Cost per user** — catches single-user abuse or runaway automation.
- **Cost per feature** — shows where optimization effort pays off most.
- **Cost per request at p50 and p95** — averages hide the expensive tail.
- **Cache hit rate and model-tier mix** — a falling hit rate or a rising share of premium-tier calls is usually the first sign of a cost regression.

Set alerts on:

- Daily spend exceeding 2x the trailing 7-day average.
- Month-to-date spend crossing a set fraction of budget, early enough to act before the cap.
- Single-user spend spike (indicates automation loop or abuse).
- New endpoint driving disproportionate cost (catches unoptimized launches).

Tools:

- Provider dashboards (Anthropic Console, OpenAI Usage page) for aggregate tracking.
- API response headers (`usage` field in every response) for per-request tracking in your own systems.
- Custom dashboards aggregating usage data by feature, user, and model.

---

## LLM Cost Governance

Advanced cost controls for teams with significant AI API spend. These techniques go beyond per-call optimization and address systemic cost at the architecture and observability layer.

### Model Cascading and Routing

Route requests to the cheapest model that meets quality requirements, escalating only when necessary.

**Classifier-first pattern:**
1. A value-tier model classifies incoming request complexity.
2. Simple requests (extraction, classification, formatting, FAQ-style QA) are handled by the cheap model end-to-end.
3. Complex requests (multi-step reasoning, code generation, nuanced judgment) escalate to the expensive model.

**Quality gate fallback pattern:**
1. Send every request to the cheap model first.
2. Evaluate output quality against a confidence threshold or a simple heuristic (output length, structured output validity, presence of required fields).
3. If quality fails the gate, re-run with the expensive model.
4. Track the escalation rate — if it exceeds 30-40%, the quality bar is miscalibrated or the cheap model is wrong for this task type.

**Practitioner-reported savings (not guaranteed):** Teams implementing cascading on mixed-complexity workloads report 40-70% cost reduction versus routing all requests to the expensive model. Actual savings depend heavily on your task distribution.

**Implementation notes:**
- A/B test model tiers on a sample before full rollout. Quality regressions are invisible unless you measure.
- Log which model served each request — you need this for per-trace attribution (see below).
- Cascading adds latency on the escalation path. For latency-sensitive features, gate the cheap-model-first approach to async or background workloads.

### Semantic Caching

Exact-match response caches (application-level cache) have low hit rates for user-facing features because queries vary in wording. Semantic caching uses embedding similarity to reuse responses for queries that are different in wording but equivalent in intent.

**How it works:**
1. Embed each incoming query using a cheap embedding model.
2. Query a vector index of previously answered prompts.
3. If a cached result exceeds a similarity threshold (typically 0.92-0.97 cosine similarity), return the cached response without calling the generation model.
4. Below the threshold, call the model, cache the result with its embedding.

**When to apply:**
- High query volumes with predictable intent clusters (help center queries, FAQ-style assistants, product search with natural language).
- Not appropriate for queries where precise, up-to-date, or personalized answers are required — a cached response from a different user's context can produce wrong or stale answers.

**Tooling:** Semantic caching is built into LLM gateway tools including GPTCache (open source) and is available as a feature in Langfuse, Portkey, and some vector database SDKs. Verify the similarity threshold empirically before deploying — too low produces wrong answers, too high defeats the cache.

**Practitioner-reported savings (not guaranteed):** Cache hit rates of 20-50% are reported for high-volume assistants with clustered query patterns. Individual results vary by domain and query diversity.

### Per-Trace and Per-User Cost Attribution

Aggregate spend dashboards hide the cost distribution. A small percentage of users or sessions often account for a disproportionate fraction of cost.

**Attribution layers:**

| Layer | What to track | Why |
|-------|--------------|-----|
| Per-request | model used, input tokens, output tokens, cost estimate | Baseline — attach to every API call |
| Per-session | total cost across a conversation or task run | Identify expensive session patterns |
| Per-user | cumulative cost per user ID or tenant | Catch runaway automation, identify high-cost segments |
| Per-feature | cost attributed to product feature | Prioritize optimization investment |

**Implementation approach:**
- Pass a `metadata` object (Anthropic) or `user` field (OpenAI) on every request with at minimum: `feature_id`, `user_tier`, `session_id`.
- Collect the `usage` object from every API response — it contains exact token counts. Multiply by the model's per-token price to get cost per call.
- Aggregate in your own datastore or pipe to an observability tool.

**Observability tooling for LLM cost:**

- **Langfuse** — open source, self-hostable. Traces, cost per trace/user, token usage breakdown, latency. Strong for teams that want full data control.
- **Helicone** — hosted proxy layer. Wraps your API calls with zero code change, adds per-user and per-request cost tracking, rate limiting, caching.
- **Portkey** — hosted gateway. Multi-provider routing, cost attribution, semantic caching, fallback chains. Adds a proxy hop but simplifies multi-model setups.

All three are practitioner-adopted tools; pricing and feature sets change — verify current plans before committing.

**Alert patterns for per-user attribution:**
- Alert when a single user or session exceeds 10x the median session cost (indicates runaway loop or misconfigured agent).
- Alert when a feature's daily cost exceeds 2x its trailing 7-day average (indicates new code path or traffic spike).

---

## Self-Hosted / Open-Weight Inference

Managed API pricing (above) is not the only option once volume is high and predictable. Teams running open-weight models (Llama, Mixtral, Qwen, DeepSeek) on rented or owned GPUs face a different cost shape: capacity procurement instead of per-token billing.

**When self-hosting can beat managed API pricing:**
- Sustained, predictable request volume (not spiky) — idle GPU-hours are the thing that erases the savings.
- A model that is genuinely good enough at the open-weight tier for the task — do not self-host a worse model to save money on a task where quality loss has a larger cost than the token bill.
- In-house or contracted ability to run an inference server (vLLM, TGI, SGLang) with continuous batching — naive single-request serving wastes most of the GPU's throughput advantage.

**GPU procurement decision (re-quote every rate at decision time; GPU spot and on-demand prices move often):**
- **On-demand GPU-hours** for bursty or exploratory workloads.
- **Reserved GPU capacity** for steady production serving. Size it with the [d-quantile rule](cloud-commitment-and-k8s-cost-guide.md#sizing-rule-commit-to-the-d-quantile): commit to the level of hourly GPU use you exceed a (1 − d) share of the time, where d is the quoted discount. Do not commit before the serving traffic pattern is stable for at least one full traffic cycle.
- **Spot/interruptible GPU capacity** for batch offline inference, evaluation runs, and fine-tuning jobs that checkpoint — never for a synchronous production request path, since reclamation typically comes with only a short warning window.
- **Quantization (FP8/INT8) and continuous batching** reduce cost per token at the serving layer independent of the procurement decision — evaluate these before adding more GPU capacity, since they are usually cheaper to implement than they are to provision around.

**The build-vs-buy trap:** self-hosting looks cheaper on a per-token spreadsheet almost every time, because the spreadsheet rarely includes the engineering time to build and maintain a serving stack, the on-call burden of a new production dependency, and the opportunity cost of the team not shipping product features instead. Run the comparison against fully-loaded cost (engineer-hours at loaded rate + GPU spend + on-call), not GPU spend alone, before recommending a migration off a managed API.

For details on cloud committed-use pricing mechanics that also apply to GPU capacity purchases, see [cloud-commitment-and-k8s-cost-guide.md](cloud-commitment-and-k8s-cost-guide.md).

### Breakeven: Self-Hosted vs API

Compute breakeven from your own measured numbers; there is no universal volume threshold.

```text
api_monthly        = monthly_tokens × blended_API_rate_per_token
gpus_needed        = ceil(peak_tokens_per_s / measured_tokens_per_s_per_GPU)  + redundancy
                     (throughput measured on your prompts, at your latency target,
                      with continuous batching)
selfhost_monthly   = gpus_needed × GPU_hourly_rate × hours_provisioned
                     + loaded engineering and on-call cost + storage/network/observability
breakeven_tokens   = selfhost_monthly / blended_API_rate_per_token
```

- Self-hosting wins only when `monthly_tokens` stays above `breakeven_tokens` across a full traffic cycle **and** the open-weight model meets the same quality bar on your eval set.
- Size the fleet for peak, not average: idle provisioned GPU-hours are paid for. Low utilization is the usual reason the spreadsheet breakeven never arrives.
- Re-run the calculation when API rates, GPU rates, or traffic shape change; each input is volatile.

---

## Common Optimization Checklist

1. Audit model selection: which share of current tasks does a cheaper model handle at the quality bar on your eval set?
2. Implement prompt caching (structure prompts for prefix reuse).
3. Use Batch API for all non-real-time workloads.
4. Set `max_tokens` on every request.
5. Trim conversation context — summarize instead of sending full history.
6. Cache responses for repeated or near-identical queries.
7. Implement model cascading — route simple tasks to cheap models, escalate complex ones.
8. Add per-trace cost attribution — collect `usage` on every call and tag with feature and user-tier.
9. Evaluate semantic caching for high-volume assistants with clustered query patterns.
10. Set spending alerts in provider dashboards.
11. Track cost per feature, not just total spend.
