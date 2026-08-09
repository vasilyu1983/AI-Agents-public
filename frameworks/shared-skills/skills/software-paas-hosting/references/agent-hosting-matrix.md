# Agent Hosting Matrix

Use this reference to map an agent workload to a concrete PaaS stack. Each entry includes the recommended platform, the supporting services, and the realistic alternative when the default doesn't fit.

Volatile facts were last checked on 2026-07-11. Verify hard limits, beta status, regions, and prices through [`../data/sources.json`](../data/sources.json) before making a final recommendation.

This file consumes the autonomy-shape model defined in [`../../ai-agents/SKILL.md`](../../ai-agents/SKILL.md):

- **Shape A** — Triggered / hosted run (webhook, queue, schedule, `/fire`)
- **Shape B** — Always-on bot or voice server
- **Shape C** — Autonomous loop (PRD-driven until acceptance met)

## Table of Contents

- [Quick Matrix](#quick-matrix)
- [Shape A — Triggered Agent Stacks](#shape-a--triggered-agent-stacks)
- [Shape B — Text Bot Stacks](#shape-b--text-bot-stacks)
- [Shape B-voice — Voice Bot Stacks](#shape-b-voice--voice-bot-stacks)
- [Shape C — Autonomous Loop Stacks](#shape-c--autonomous-loop-stacks)
- [Supporting Service Defaults](#supporting-service-defaults)
- [Reference Architectures](#reference-architectures)
- [When None of These Fit](#when-none-of-these-fit)

## Quick Matrix

| Workload | Recommended Stack | Realistic Alternative |
|---|---|---|
| Slack/Stripe/GitHub webhook → agent | **Vercel + Inngest + Upstash Redis** | Cloudflare Workers + Queues + KV/D1 |
| Daily scheduled report agent | **Vercel Cron + Anthropic API** | Render Cron + Upstash Redis |
| Fan-out queue → 100 concurrent agents | **AWS SQS + Lambda + Bedrock** (short calls) or **AgentCore Runtime** (long sessions) | Cloudflare Queues + Workers + AI Gateway |
| Long-running multi-step agent on AWS, framework-agnostic | **AgentCore Runtime + Memory + Gateway** | Modal / E2B (cross-cloud) + custom memory |
| Multi-step durable agent workflow | **Inngest on Vercel** | Temporal Cloud + Fly.io workers |
| Always-on text bot (support / sales) | **Fly.io + Upstash Redis + Neon Postgres** | Railway + Postgres + Redis |
| WhatsApp / Telegram bot | **Fly.io + webhook ingress** | Cloudflare Workers + Durable Objects |
| Internal copilot (web chat UI) | **Vercel (Next.js) + Convex or Upstash** | Fly.io + Postgres + Redis |
| Voice bot (PSTN inbound) | **LiveKit Cloud + Fly.io agent worker** | Twilio + Fly.io / self-host LiveKit on Fly |
| Autonomous code-refactor loop | **Inngest + Anthropic + Sandbox (Vercel)** | Fly.io Machine + Temporal worker |
| Overnight research loop (Ralph) | **Inngest + Anthropic + Phoenix telemetry** | Fly.io + LangGraph + Postgres checkpoints |
| Multi-tenant SaaS with per-tenant agents | **Fly.io + Postgres-per-tenant + AI Gateway** | Render + per-service workers |
| Edge AI proxy (caching, routing) | **Cloudflare Workers + AI Gateway** | Vercel Edge + AI Gateway |

## Shape A — Triggered Agent Stacks

The trigger fires, a fresh agent session runs to completion, the result is recorded. State is event-scoped, not session-scoped.

### Stack A1 — Vercel-native (default for new products)

```text
Trigger sources                     Compute                        State / data
┌──────────────────┐                ┌──────────────────┐           ┌──────────────────┐
│ Webhook (Stripe, │ ──────────────▶│ Vercel Functions │ ─────────▶│ Upstash Redis    │
│  GitHub, Linear) │                │ (Fluid Compute)  │           │ (idempotency,    │
└──────────────────┘                │                  │           │  dedup, slots)   │
                                    │ AI SDK +         │           └──────────────────┘
┌──────────────────┐                │ AI Gateway       │
│ Vercel Cron      │ ──────────────▶│                  │ ─────────▶┌──────────────────┐
└──────────────────┘                └──────────────────┘           │ Neon Postgres /  │
                                            │                      │ Supabase         │
┌──────────────────┐                        │                      └──────────────────┘
│ Vercel Queues    │ ──────────────▶        │
│ (Beta)           │                        │                      ┌──────────────────┐
└──────────────────┘                        ▼                      │ Inngest          │
                                    Optional handoff ─────────────▶│ (for multi-step  │
                                                                   │  durable)        │
                                                                   └──────────────────┘
```

**Use when:** product is Next.js / TS-heavy; you want AI Gateway routing; spike-friendly workloads.

**Watch out for:** Vercel Queues are Beta; verify retry, poison-message, dead-letter, and consumer limits before making them load-bearing. For multi-step durability, prefer Inngest, Temporal, Trigger.dev, Restate, or Vercel Workflow.

**Fits inside:** [`../../ai-coding-agents-tasks/references/webhook-and-queue-triggers.md`](../../ai-coding-agents-tasks/references/webhook-and-queue-triggers.md)

### Stack A2 — Cloudflare-native (edge-first)

```text
Webhook → Worker → Queue → Worker (agent) → Durable Object (state) → R2/D1
                          AI Gateway routes LLM calls
                          Vectorize for embeddings
```

**Use when:** latency-critical, global users, ultra-high request volume, cost discipline matters.

**Watch out for:** V8 runtime limitations vs Node; heaviest lock-in of any stack. CPU time, wall-clock duration, queue consumers, cron triggers, and Durable Object alarms have different limits; don't collapse them into one "30s limit."

### Stack A3 — AWS-native (compliance / enterprise) — Lambda path

```text
EventBridge / API Gateway → SQS → Lambda → Bedrock (Anthropic) → DynamoDB
                                  Step Functions for multi-step
                                  Secrets Manager for keys
```

**Use when:** AWS is the corporate standard; Bedrock is required for data residency or compliance; integration with existing AWS services; agent calls are short (< 15min) and stateless between turns.

**Watch out for:** Lambda 15-min cap forces long agents into Step Functions; cold starts can pile up under burst.

### Stack A3a — AWS-native AgentCore (preferred 2026 path)

```text
Client → AgentCore Runtime (microVM session, up to 8h)
             ├── AgentCore Memory (managed conversation + facts)
             ├── AgentCore Gateway (Lambda/API → MCP tools)
             ├── AgentCore Identity (per-agent IAM)
             ├── AgentCore Code Interpreter / Browser (as needed)
             ├── Bedrock model (any provider on Bedrock)
             ├── Bedrock Knowledge Bases (managed RAG, optional)
             └── AgentCore Observability + Evaluations + Policy + Registry
```

**Use when:** new AWS agent build; need long-running sessions (5min – 8h); want framework freedom (LangGraph / CrewAI / LlamaIndex / Strands / custom); want managed memory + identity + tools without building them; multi-tenant SaaS.

**Watch out for:** multiple AgentCore capabilities to learn; start with **Runtime + Memory + Gateway** and add others as needed. Strands is the lowest-friction AWS-native framework; LangGraph is more portable.

Deep dive: [`aws-bedrock-agentcore.md`](aws-bedrock-agentcore.md).

### Stack A3b — Bedrock Agents (classic) — legacy

```text
Configuration-only: Bedrock Agent → Knowledge Bases + Lambda action groups
```

**Use when:** already invested; want zero code; AWS-specific lock-in is acceptable. For new code-based agents, evaluate AgentCore first.

### Stack A4 — Durable orchestration (Temporal / Inngest)

```text
Trigger source → Inngest (or Temporal) → step.run("agent", ...) → side-effect step
                  Replay-safe, exactly-once, sagas + signals
```

**Use when:** multi-step work with compensation, human-in-the-loop, long workflows.

**Fits inside:** [`../../ai-coding-agents-tasks/references/durable-trigger-integration.md`](../../ai-coding-agents-tasks/references/durable-trigger-integration.md)

## Shape B — Text Bot Stacks

The bot serves sessions over HTTP / WebSocket / messaging-channel webhooks. State persists across turns.

### Stack B1 — Always-on container (default for stateful bots)

```text
Channel (web chat / WhatsApp / Slack) → Load balancer
                ↓
        Fly.io machines (multi-region)
        ├── LangGraph state graph
        ├── Anthropic via AI Gateway
        └── Tools via MCP servers
                ↓
        Upstash Redis (session state)
        Neon Postgres (LangGraph checkpoints)
        Pinecone / pgvector (KB)
```

**Use when:** sessions need persistent state, sticky routing, WebSocket, SSE, or long-held connections.

**Why Fly:** machines wake fast, multi-region near users, supports any Docker image, can hold sockets.

**Fits inside:** [`../../ai-bot-builder/references/production-deployment.md`](../../ai-bot-builder/references/production-deployment.md) and [`../../ai-bot-builder/references/stateful-rollout-and-blue-green.md`](../../ai-bot-builder/references/stateful-rollout-and-blue-green.md)

### Stack B2 — Hybrid Vercel + Fly (Next.js front + stateful back)

```text
User → Vercel (Next.js UI, public API)
        ↓ session API
        Fly.io (LangGraph worker, Postgres checkpointer)
                ↓
        Shared state (Upstash, Postgres)
```

**Use when:** product surface is Next.js heavy but the agent loop must be stateful and long-lived.

### Stack B3 — Cloudflare Durable Objects (edge-native bot)

```text
User → Worker → Durable Object instance per session
                 ├── State lives inside the DO
                 ├── LLM via AI Gateway
                 └── Vectorize for KB
```

**Use when:** sub-100ms latency budget globally, willing to commit to Cloudflare primitives.

**Trade-off:** highest lock-in; Durable Objects don't translate to other platforms. Model every message handler as at-least-once or replay-prone and keep state transitions idempotent.

### Stack B4 — Convex / Supabase Realtime (web-only bot)

```text
Convex (or Supabase Realtime) handles state + subscriptions
Functions invoke LLM directly
Vercel hosts the React/Next.js UI
```

**Use when:** product is web-only, realtime UI matters, team is TS-heavy, no telephony / WhatsApp / PSTN concerns.

## Shape B-voice — Voice Bot Stacks

Voice agents need media (RTP/Opus), telephony (SIP/PSTN), and the agent worker — three layers, three responsibilities.

### Stack BV1 — LiveKit Cloud + Fly agent worker (default)

```text
PSTN → Twilio/Telnyx SIP trunk → LiveKit Cloud (media)
                                          ↓ agent dispatch
                                  Fly.io machines (agent worker)
                                  ├── LiveKit Agents SDK
                                  ├── Deepgram STT
                                  ├── Anthropic via AI Gateway
                                  ├── ElevenLabs/Cartesia TTS
                                  └── Tools / MCP
                                          ↓
                                  S3 (recordings)
                                  Postgres (call state)
```

**Use when:** any voice agent in production. LiveKit Cloud carries the media; Fly carries the agent.

**Fits inside:** [`../../ai-voice-bots/references/production-deployment.md`](../../ai-voice-bots/references/production-deployment.md)

### Stack BV2 — Pipecat Cloud (lighter ops)

```text
Twilio SIP → Pipecat Cloud (media + pipeline) → agent function
                                                  └── Anthropic, STT, TTS providers
```

**Use when:** low call volume, fast prototype, Pipecat-native team.

### Stack BV3 — Self-host LiveKit on Fly.io (cost at scale)

```text
PSTN → Telnyx → LiveKit OSS on Fly Machines (turn + media)
                       ↓
                Agent worker on same Fly cluster
```

**Use when:** >1000 concurrent calls and LiveKit Cloud pricing dominates.

### What does NOT host voice bots

- Vercel — no SIP, no media, no PSTN
- Cloudflare Workers — same
- Deno Deploy — same, and Deploy Classic / subhosting v1 shut down July 20, 2026; any voice-adjacent service still on Classic needs an active migration, not a scheduled one
- Railway / Render — no SIP/media; possible to run agent worker but not media plane

## Shape C — Autonomous Loop Stacks

Long-running, PRD-driven, iterates until acceptance met or budget hit.

### Stack C1 — Inngest-orchestrated (default)

```text
Loop driver: Inngest function
  for each iteration:
    step.run("plan") → step.run("execute") → step.run("check")
    if acceptance met → return
    if budget breached → halt

Each step:
  - Vercel function (Fluid 800s GA; 1800s only via the beta extended-duration path on select runtimes — don't design around beta as the primary budget) or external worker
  - Anthropic via AI Gateway
  - Postgres checkpoint after each iteration
  - Phoenix / Langfuse telemetry
```

**Use when:** iteration count >5, total runtime hours, acceptance criteria are machine-checkable.

**Why Inngest:** durable steps survive function timeouts; signals for human-in-the-loop; replay-safe.

**Fits inside:** [`../../ai-agents/references/autonomous-loop-patterns.md`](../../ai-agents/references/autonomous-loop-patterns.md)

### Stack C2 — Fly Machine + LangGraph (single-machine loop)

```text
Fly Machine running:
  - LangGraph cyclic graph
  - PostgresSaver checkpointer (Neon)
  - Anthropic SDK + AI Gateway
  - Budget enforcement via hook (see budget-and-loop-hooks.md)
Restart policy: on-failure
```

**Use when:** loop is short (<1 hour), single-process is OK, Inngest feels like overkill.

### Stack C3 — Temporal Cloud (enterprise / multi-step)

```text
Temporal workflow:
  - run_iteration activity (Anthropic SDK)
  - check_acceptance activity
  - apply_side_effects activity (idempotent)
Workers run on Fly / Render / your existing infra
```

**Use when:** complex compensation needed; multi-step agent work; integrating with existing Temporal stack.

### Stack C4 — Ralph Loop on bare metal (research / prototype)

```text
tmux session running plain Python `while` loop:
  - reads PRD from file
  - calls Anthropic
  - writes checkpoint
  - checks acceptance
Runs on a single VM (Fly Machine, Hetzner, anywhere)
```

**Use when:** research, side-project, intentionally low-ceremony.

**Trade-off:** no replay safety, no durable signals, no operator UI.

## Supporting Service Defaults

These appear in most stacks above. Pick once per project.

| Service type | Default | Why | Alternative |
|---|---|---|---|
| Session cache / idempotency | **Upstash Redis** | Per-request pricing, no infra; global replicas | Redis on Fly / Render / Railway |
| Primary database | **Neon Postgres** or **Supabase** | Serverless / managed, branchable | Fly Managed Postgres, Railway Postgres, RDS |
| Vector store | **pgvector on Neon** for <10M vectors; **Pinecone / Turbopuffer** above | One database to operate vs separate vector tier | Vectorize (CF), Qdrant Cloud |
| Object storage | **Cloudflare R2** | No egress fees, S3-compatible | S3, Backblaze B2 |
| Secrets | **Doppler / Infisical / Vault** | Hot rotation, external to host | AWS Secrets Manager, platform-native (lower bar) |
| Observability | **Langfuse + Sentry** | LLM-aware + general APM | OpenLLMetry + Phoenix; Honeycomb for traces |
| Durable orchestration | **Inngest** | Native to Vercel; great for agent steps | Temporal Cloud, Trigger.dev, Restate |
| LLM gateway | **Vercel AI Gateway** or **Cloudflare AI Gateway** | Free routing, fallback, caching | Portkey, OpenRouter, self-built |
| Email / transactional | **Resend** | DX; deliverability | Postmark, SES |
| Auth | **Clerk** / **WorkOS** for B2B; **Supabase Auth** for B2C | Off-the-shelf SSO, MFA | Auth.js + own backend |

## Reference Architectures

### "EMI / fintech agent" (regulated)

```text
Webhook (Stripe, internal events)
  → API Gateway (auth)
  → SQS (idempotency, DLQ)
  → Lambda (agent invocation, Bedrock-Anthropic for data residency)
  → DynamoDB (audit log + state)
  → Step Functions (multi-step with approval gates)
  → Recording: S3 with Object Lock (WORM)
  → Observability: CloudWatch + Langfuse
```

Vercel/Fly are not the substrate when financial regulation demands AWS / Azure / GCP with explicit compliance attestation.

### "Indie hacker SaaS bot"

```text
Vercel (Next.js + serverless agent functions)
  → Upstash Redis (sessions, idempotency)
  → Neon Postgres (data + pgvector)
  → AI Gateway (provider fallback)
  → Clerk (auth)
  → Resend (email)
  → Langfuse (observability)
```

Cheapest production-grade stack; goes from prototype to paying customers without re-platforming.

### "Voice support bot for SMB"

```text
Twilio (DID + SIP) → LiveKit Cloud (media)
  → Fly.io (LiveKit Agents worker, multi-region)
  → AI Gateway (Anthropic + ElevenLabs)
  → Postgres (call records + state)
  → S3 (recordings, encrypted, retention 5y)
  → Langfuse (call traces)
```

### "Overnight research loop"

```text
Inngest (loop driver, cron-triggered)
  → Vercel functions (per iteration)
  → Anthropic via AI Gateway (Opus 4.7)
  → Postgres checkpoint
  → Slack webhook (progress reports)
  → Budget hook halts at $50
```

## When None of These Fit

Move off PaaS to self-managed infrastructure when:

- Compliance demands BYO-cloud (regulated finance, healthcare beyond covered platforms, government)
- Single-tenant isolation legally required
- Cost at scale dominates (typically >$50k/mo PaaS spend justifies platform team)
- Workload is fundamentally unfit (GPU training, custom hardware, ultra-low-latency trading)
- Multi-region active-active with strong consistency

Use [`../../ops-devops-platform/SKILL.md`](../../ops-devops-platform/SKILL.md) for that tier.

## Known Traps

- **Vercel Queues are not a mature queue by default.** Treat Beta status, poison messages, DLQ needs, retries, and consumer limits as design inputs, not implementation details.
- **Cloudflare duration is multi-dimensional.** HTTP wall-clock, CPU time, queue consumer duration, cron duration, and Durable Object alarm duration are separate constraints.
- **Deno Deploy Classic is an active migration risk, not a future one.** Classic and subhosting v1 shut down July 20, 2026 — treat any Classic-hosted project encountered after this date's check as needing immediate migration; projects do not transfer automatically, and new Deploy has different regions, APIs, and no queue support as of mid-2026 docs.
- **Fly Postgres terminology matters.** Legacy/self-managed Fly Postgres and Fly Managed Postgres have different support, backup, HA, and feature profiles.
- **Koyeb free instances are not production instances.** This is a permanent product-tier boundary, not a preview limitation: the single free instance per organization is single-region, cannot run as a Worker Service, and has no custom scaling or Volumes.
- **Cloudflare's subrequest cap moved in Feb 2026.** The old 1,000-subrequest ceiling is gone; paid Workers now default to 10,000 (configurable to 10M) while free stays at 50 external. High-fan-out agent patterns (parallel tool calls, wide Durable Object coordination) that were previously blocked may now be viable — re-verify current defaults before redesigning around the old limit.
- **Free/sleeping tiers distort bot behavior.** Cold starts, scale-to-zero, and CPU throttling create latency spikes and missed webhook deadlines.

## Cross-References

- [`platform-comparison.md`](platform-comparison.md) — platform-by-platform deep dive
- [`../../software-baas-platforms/SKILL.md`](../../software-baas-platforms/SKILL.md) — data layer companion
- [`../../ai-coding-agents-tasks/references/webhook-and-queue-triggers.md`](../../ai-coding-agents-tasks/references/webhook-and-queue-triggers.md) — Shape A triggers
- [`../../ai-coding-agents-tasks/references/durable-trigger-integration.md`](../../ai-coding-agents-tasks/references/durable-trigger-integration.md) — Shape A durable
- [`../../ai-bot-builder/references/production-deployment.md`](../../ai-bot-builder/references/production-deployment.md) — Shape B base
- [`../../ai-bot-builder/references/stateful-rollout-and-blue-green.md`](../../ai-bot-builder/references/stateful-rollout-and-blue-green.md) — Shape B rollout
- [`../../ai-bot-builder/references/secret-rotation-and-model-fallback.md`](../../ai-bot-builder/references/secret-rotation-and-model-fallback.md) — provider failover
- [`../../ai-voice-bots/references/production-deployment.md`](../../ai-voice-bots/references/production-deployment.md) — Shape B-voice
- [`../../ai-agents/references/autonomous-loop-patterns.md`](../../ai-agents/references/autonomous-loop-patterns.md) — Shape C
- [`../../ai-agents/references/24-7-operating-model.md`](../../ai-agents/references/24-7-operating-model.md) — SLOs and oncall
- [`../../agents-hooks/references/budget-and-loop-hooks.md`](../../agents-hooks/references/budget-and-loop-hooks.md) — budget enforcement
- [`../../software-workflow-automation/SKILL.md`](../../software-workflow-automation/SKILL.md) — Inngest / Temporal
