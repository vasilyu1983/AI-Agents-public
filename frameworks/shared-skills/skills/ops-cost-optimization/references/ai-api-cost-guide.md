# AI API Cost Guide

Operational reference for understanding and reducing AI API spend. Covers provider pricing, cost drivers ranked by impact, and a repeatable optimization checklist.

## Table of Contents

- [Pricing Overview](#pricing-overview)
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
- [Common Optimization Checklist](#common-optimization-checklist)

---

## Pricing Overview

Prices are per million tokens (MTok). Output tokens are consistently more expensive than input tokens across all providers.

Prices verified against `platform.claude.com/docs/en/about-claude/pricing` and `openai.com/api/pricing` on 2026-07-11. **Re-verify against official pricing pages before recommendations or budget decisions — AI API prices change monthly and model line-ups shift every few months.**

| Provider | Model | Input (per MTok) | Output (per MTok) | Notes |
|----------|-------|------------------|--------------------|-------|
| Anthropic | Haiku 4.5 | $1.00 | $5.00 | Fast, cheap — best for classification and extraction |
| Anthropic | Sonnet 4.6 | $3.00 | $15.00 | Balanced cost/quality for most production tasks |
| Anthropic | Sonnet 5 (through 2026-08-31) | $2.00 | $10.00 | Introductory pricing; reverts to $3/$15 on 2026-09-01 |
| Anthropic | Opus 4.8 | $5.00 | $25.00 | Top-tier reasoning and complex generation |
| OpenAI | GPT-4.1 mini | $0.40 | $1.60 | Lowest-cost option for simple tasks |
| OpenAI | GPT-4.1 | $2.00 | $8.00 | General-purpose, competitive with Sonnet |
| OpenAI | GPT-5.6 Luna (or equivalent lowest tier) | ~$1.00 | ~$6.00 | Fast/cheap tier of the GPT-5.6 family — verify exact tier name, OpenAI's naming shifts frequently |
| OpenAI | GPT-5.6 Sol (or equivalent flagship tier) | ~$5.00 | ~$30.00 | Flagship reasoning tier — verify current flagship name before quoting |

**Correction note:** an earlier version of this table listed Opus at ~$15/$75 and Haiku at ~$0.80/$4 — those were stale figures (Opus 4.8 is actually $5/$25; $0.80/$4 is the retired Haiku 3.5 rate, not current Haiku 4.5 at $1/$5). This is exactly the kind of error this skill exists to catch in a customer's own bill — always cross-check a cited per-token rate against the live pricing page rather than trusting a cached table, including this one.

The OpenAI GPT-5.x tier names above are **unverified as of 2026-07-11** beyond secondary-source aggregation — OpenAI renames and re-tiers frequently. Confirm the current flagship/mini/nano naming and rate card at `openai.com/api/pricing` before quoting a number to a customer.

---

## Plan-Tier Users vs API Users

This guide defaults to API/dev billing — pricing per MTok, prompt caching,
Batch API, and quota dashboards. Plan-tier users (Pro / Max / Team /
Enterprise) are billed differently: a flat monthly fee with usage limits per
rolling window. The optimization toolkit overlaps but is not identical.

### Claude Code in-product cost levers

Documented operational knobs, useful for both plan-tier and API users.

- **`/usage`** — for plan subscribers, shows plan usage bars and activity
  stats; for API users, session cost. The dollar figure shown is a local
  estimate from token counts and is not authoritative billing. `/cost` and
  `/stats` are aliases.
- **`/plan` or Shift+Tab** — enter Plan Mode. The agent explores and proposes
  an approach before expensive edits, preventing rework when the initial
  direction is wrong. Cheap planning before expensive building is the largest
  single saving on multi-step tasks.
- **`/effort low|medium|high|xhigh|max|auto`** — switch reasoning effort
  mid-session. `low` is sufficient for most non-reasoning-bound work; reserve
  `high`/`xhigh` for hard debugging, cross-skill refactors, and architectural
  work. `auto` returns to the model default. Available levels depend on the
  model; `max` is session-only.
- **`/clear` between unrelated tasks** — stale context costs tokens on every
  subsequent message. Use `/rename` before clearing if the session may be
  worth resuming.
- **`/compact <focus>`** — accepts custom focus instructions so summarization
  preserves what matters (test output, code samples, API usage) instead of
  the default. Can also be set in `CLAUDE.md` under a `Compact instructions`
  section.
- **`/context`** — show what is currently consuming context space (CLAUDE.md,
  MCP tools, prior turns).
- **Extended Thinking** — on by default. Lower with `/effort low`, disable in
  `/config`, or cap with `MAX_THINKING_TOKENS=8000` for tasks that do not
  need deep reasoning. Thinking tokens bill as output tokens.
- **`/rewind` / `Esc Esc`** — restore a previous checkpoint instead of
  re-prompting your way out of a wrong direction. Cheaper than re-explaining
  context.
- **Lock the session model.** Switching mid-session via `/model` re-reads the
  full history without cached context — documented cache invalidation. Pick
  the model at session start; do not toggle.
- **Subagent model pinning.** Specify `model: haiku` (or `sonnet`) in
  subagent config for delegated work; per-skill `model:` and `effort:`
  overrides apply for the turn without invalidating the session cache.

### Plan-tier user mental model

- **Long single chats amplify token use.** Claude Code auto-compacts as
  context fills; consumer Claude.ai chat does not. On Claude.ai, prefer a
  Project with multiple short chats over one long-running chat for repetitive
  work.
- **Multi-surface budget caveat.** Different Anthropic products may share or
  split the plan budget. Verify the current split against the active plan
  terms — the principle is to avoid burning budget on a surface that has
  spare capacity elsewhere.
- **Agent teams scale costs.** Agent teams (`CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`)
  use ~7× more tokens than a standard session when teammates run in plan
  mode, because each teammate maintains its own context window. Keep teams
  small and tasks self-contained.

Primary sources (verified 2026-05-02):

- Claude Code Costs guide — https://code.claude.com/docs/en/costs
- Claude Code Commands reference — https://code.claude.com/docs/en/commands
- Skill frontmatter (`model`, `effort` overrides) — https://code.claude.com/docs/en/slash-commands

---

## Cost Drivers

Ranked by typical impact on total spend.

### Model Selection

The single biggest cost lever. Choosing the right model for each task can cut spend by 10-50x with no quality loss on simple workloads.

- **Common waste:** Using Opus or o3 for tasks that Haiku or GPT-4.1 mini handles well — classification, entity extraction, simple QA, formatting.
- **Optimization:** Implement model routing. Use cheap models for classification, extraction, and simple QA. Reserve expensive models for complex reasoning, long-form generation, and coding. Measure quality at each tier to find the cheapest model that meets the bar.

### Token Volume

Input and output tokens are the direct unit of cost. Output tokens are typically 3-5x more expensive than input tokens.

- **Common waste:** Sending full documents when summaries suffice. Not trimming conversation history. Including verbose system prompts in every turn. Allowing unconstrained output length.
- **Optimization:** Trim the context window aggressively. Summarize long conversations instead of forwarding full history. Use structured output (JSON, enums) to reduce output token count. Remove unused system prompt sections per request type.

### Prompt Caching

Repeated prompt prefixes can be served from cache at a steep discount.

- **Anthropic:** A cache write costs 1.25x base input price (5-minute TTL) or 2x base input price (1-hour TTL); a cache hit costs 0.1x base input price (a 90% discount vs. standard input). The write premium means a 5-minute cache pays for itself after one hit; a 1-hour cache pays for itself after two hits — below that, caching costs more than not caching.
- **OpenAI:** Similar caching mechanics for repeated prompt prefixes; verify current cache-hit discount and TTL against the live pricing page, as the discount rate has varied by generation.
- **Optimization:** Structure prompts with the static system prompt first and dynamic content last. Reuse conversation prefixes across requests. Batch requests that share the same system prompt to maximize cache hits. Do not cache prefixes reused fewer than once per TTL window — the write premium turns it into a net cost increase.

### Batch API

Non-real-time workloads qualify for significant discounts.

- **Anthropic:** 50% discount for batch processing.
- **OpenAI:** Similar batch pricing tiers.
- **Optimization:** Use batch API for offline analysis, bulk content generation, data processing, and evaluation runs — anything that does not need sub-second response. Queue work during off-peak hours when possible.

### Fine-Tuning Costs

Fine-tuning has an upfront training cost (per token) plus ongoing inference cost, which is often cheaper than the base model at volume.

- **When it is worth it:** High-volume, repetitive task where a fine-tuned small model replaces a large model. Examples: structured extraction at scale, domain-specific classification, consistent tone/format generation.
- **Break-even analysis:** Compare the fine-tuning training cost plus fine-tuned inference cost versus the saved inference cost of the larger model over 3-6 months. Factor in retraining frequency when the task evolves.

### Embeddings

Embedding models are much cheaper than generation models, typically $0.02-$0.13 per MTok.

- **Common waste:** Re-embedding unchanged content on every pipeline run. Using unnecessarily large embedding models. Embedding entire documents instead of meaningful chunks.
- **Optimization:** Cache embeddings and only re-embed changed content. Use incremental indexing. Choose the smallest embedding model that maintains retrieval quality — run a retrieval eval before upgrading model size.

---

## Cost Management Strategies

### Token Budget Management

- Set `max_tokens` on every request to prevent runaway output.
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

Set alerts on:

- Daily spend exceeding 2x the trailing 7-day average.
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
1. A lightweight model (Haiku, GPT-4.1 mini) classifies incoming request complexity.
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

**GPU procurement decision (unverified figures should be re-quoted at decision time — GPU spot/on-demand pricing moves weekly):**
- **On-demand GPU-hours** for bursty or exploratory workloads.
- **Reserved 1-3 year GPU capacity** for 24/7 production serving — typically cuts 30-50% off on-demand, mirroring the cloud-compute commitment math in [cloud-commitment-and-k8s-cost-guide.md](cloud-commitment-and-k8s-cost-guide.md). Same rule applies: do not commit before the serving traffic pattern is stable for at least one full traffic cycle.
- **Spot/interruptible GPU capacity** for batch offline inference, evaluation runs, and fine-tuning jobs that checkpoint — never for a synchronous production request path, since reclamation typically comes with only a short warning window.
- **Quantization (FP8/INT8) and continuous batching** reduce cost per token at the serving layer independent of the procurement decision — evaluate these before adding more GPU capacity, since they are usually cheaper to implement than they are to provision around.

**The build-vs-buy trap:** self-hosting looks cheaper on a per-token spreadsheet almost every time, because the spreadsheet rarely includes the engineering time to build and maintain a serving stack, the on-call burden of a new production dependency, and the opportunity cost of the team not shipping product features instead. Run the comparison against fully-loaded cost (engineer-hours at loaded rate + GPU spend + on-call), not GPU spend alone, before recommending a migration off a managed API.

For details on cloud committed-use pricing mechanics that also apply to GPU capacity purchases, see [cloud-commitment-and-k8s-cost-guide.md](cloud-commitment-and-k8s-cost-guide.md).

---

## Common Optimization Checklist

1. Audit model selection — can cheaper models handle 80% of current tasks?
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
