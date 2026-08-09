# PaaS Platform Comparison (July 2026)

Use this reference to pick a compute hosting platform when you've already decided you don't want to manage Kubernetes, EC2 fleets, or your own infrastructure.

Volatile facts in this file were last checked on 2026-07-11. Before giving hard claims about limits, beta status, regions, or prices, verify against [`../data/sources.json`](../data/sources.json). Pricing figures anywhere in this file are illustrative shape, not quotes — platform pricing pages change independently of this document.

Eight platforms covered. None is universally best — each has a workload shape it serves better than the others.

## Table of Contents

- [The Eight Platforms](#the-eight-platforms)
- [Vercel](#vercel)
- [Fly.io](#flyio)
- [Railway](#railway)
- [Render](#render)
- [Cloudflare Workers + Durable Objects](#cloudflare-workers--durable-objects)
- [Deno Deploy](#deno-deploy)
- [Northflank](#northflank)
- [Koyeb](#koyeb)
- [Feature Matrix](#feature-matrix)
- [Pricing Shape Matrix](#pricing-shape-matrix)
- [Decision Tree](#decision-tree)
- [Migration Paths](#migration-paths)
- [What "Deploy and Forget" Means in Practice](#what-deploy-and-forget-means-in-practice)

## The Eight Platforms

| Platform | Compute Model | Sweet Spot |
|---|---|---|
| **Vercel** | Serverless functions + edge | Next.js, Jamstack, AI SDK workloads |
| **Fly.io** | Always-on Docker machines, multi-region | Stateful apps, WebSocket, bots, near-user compute |
| **Railway** | Heroku-style services with managed Postgres | Full-stack startups, monolith + worker bundles |
| **Render** | Web services, workers, cron, managed databases | Mid-complexity products that outgrew Heroku |
| **Cloudflare Workers + Durable Objects** | Edge functions + globally-distributed stateful objects | Latency-critical APIs, edge AI, agentic state at the edge |
| **Deno Deploy** | Edge JS/TS runtime | Lightweight TypeScript APIs, no Node baggage |
| **Northflank** | Container PaaS with build pipelines | Teams wanting Render-style ergonomics + more control |
| **Koyeb** | Serverless containers globally | Always-on containers without Fly's CLI-first ops |

## Vercel

**What it is:** Serverless functions + static + edge runtime, with a Next.js-first DX and a complete AI stack (AI SDK, AI Gateway, Sandbox).

**Best for:**

- Next.js / React product sites with serverless API routes
- AI applications using `streamText` / `generateObject` from AI SDK
- Triggered agent runs via Cron Jobs, Queues (Beta), or Workflow
- Marketing sites, dashboards, content products

**Compute model:**

- Functions: Node 20+, Python, Edge runtime
- Fluid Compute (default): Hobby is hard-capped at 300s (no extended tier). Pro/Enterprise GA max is 800s.
- Extended max duration (beta, mid-2026): Pro/Enterprise can configure individual functions up to 1800s (30 min) on select runtimes (`nodejs20.x`/`22.x`/`24.x`, `python3.12`–`3.14`); not compatible with Secure Compute or Static IPs, and project-level defaults above 800s aren't supported yet — verify beta status before depending on it.
- For genuinely unbounded duration, use Vercel Workflows (built on Queues) instead of stretching a single function.
- Edge functions: lower latency, lighter limits
- No persistent disk; no always-on processes

**AI-specific features:**

- AI SDK: streaming, tool calls, structured output across providers
- AI Gateway: provider routing, fallback, caching, observability — biggest reason to start on Vercel for AI work
- Vercel Sandbox: secure code execution for agent-generated code

**Strengths:**

- Best-in-class Next.js DX
- AI Gateway saves you building provider failover (covered in [`../../ai-bot-builder/references/secret-rotation-and-model-fallback.md`](../../ai-bot-builder/references/secret-rotation-and-model-fallback.md))
- Preview deployments per PR
- Zero-config TLS, CDN, image optimization

**Weaknesses:**

- Stateless by design — sessions, WebSocket, long-held connections fail or are wasteful
- 800s function ceiling is generous but not enough for true long loops
- Pricing scales steeply with bandwidth and function execution; runaway costs are common
- Env var rotation requires redeploy unless you use external secret store
- Queues are Beta; verify poison-message and dead-letter behavior before using them as the sole durable substrate

**Pricing shape:** Per-execution, bandwidth, seats, storage, and AI-product usage. Hobby is for prototypes/non-commercial usage; Pro or Enterprise is the normal production baseline.

**Lock-in:** Medium. Next.js code is portable; Vercel-specific primitives (Edge Config, ISR) are not.

## Fly.io

**What it is:** Always-on Docker containers ("machines") deployable to many regions, with built-in private networking and optional Postgres choices.

**Best for:**

- Stateful Python/Node bots holding sessions or WebSocket connections
- Multi-region apps wanting low-latency near every user
- Background workers, autonomous loops
- Production voice agent control planes (paired with LiveKit Cloud for media)

**Compute model:**

- Fly Machines: tiny VMs (shared 256MB up to dedicated 64GB), boot in <1s
- Auto-start / auto-stop on demand
- Private 6PN network across regions
- Volumes for persistent storage
- Fly Managed Postgres is the supported production database path: automatic failover, backups, connection pooling, and cross-node storage replication across roughly a dozen regions as of mid-2026 (verify current region list and storage ceiling before sizing). Legacy/unmanaged Fly Postgres guidance should not be treated as managed Postgres guidance.

**Strengths:**

- Long-held connections work fine (WebSocket, SSE)
- Multi-region same-day setup
- Predictable Docker model — minimal lock-in
- Powerful CLI; deploy from `fly.toml`

**Weaknesses:**

- CLI-first; less polished web UI than Vercel/Railway
- Legacy Fly Postgres and self-managed Postgres require more operational ownership; Managed Postgres adds HA, backups, support, and encryption but still has feature gaps to verify
- You manage machine sizing and scaling rules (defaults are sensible)
- Less hand-holding for first-time deployers

**Pricing shape:** Per-machine + bandwidth. ~$2–10/month for small always-on machines.

**Lock-in:** Low. Docker-based; migrates cleanly to any container host.

## Railway

**What it is:** Heroku-style PaaS with services, databases, cron, and worker primitives in one UI.

**Best for:**

- Full-stack startups deploying app + Postgres + worker as a bundle
- Teams that grew up on Heroku and want similar ergonomics
- Migration target from Heroku

**Compute model:**

- Services: web service or worker, auto-scaled
- Managed Postgres, MySQL, Redis, Mongo
- Cron jobs
- Build via Nixpacks (auto-detect) or Dockerfile

**Strengths:**

- Excellent first-deploy experience (GitHub connect, build, done)
- All resources in one project; private networking between them
- Good observability built in
- Strong web UI

**Weaknesses:**

- Single-region-per-service by default; multi-region needs explicit setup
- Database and storage features are convenient, but portability, backup depth, and write-heavy maturity should be checked against production needs
- Cost can creep with multiple services on Pro tier

**Pricing shape:** Base subscription plus resource usage. Hobby suits personal projects; Pro suits teams shipping production. Verify current credits and resource limits.

**Lock-in:** Low–medium. Dockerfile deploys portable; Railway-specific config minor.

## Render

**What it is:** Web services + background workers + cron + managed databases + static sites + private services.

**Best for:**

- Mid-complexity backends that need multiple service types
- Background workers and cron-driven jobs
- Teams that want clean separation of service types

**Compute model:**

- Web services (HTTP)
- Background workers (always-on, no HTTP)
- Cron jobs (scheduled containers)
- Static sites
- Private services (internal)
- Managed Postgres, Redis

**Strengths:**

- Explicit service types match real workload shapes
- Good for the "web + worker + cron" trio
- Decent free tier (web service sleeps on free; paid is always-on)
- Reasonable autoscaling

**Weaknesses:**

- Cold starts on free tier
- Less developer mindshare than Vercel/Fly
- Limited edge / multi-region story
- AI integrations not first-party

**Pricing shape:** Per-instance and per-managed-service. Free web services may sleep; paid instances are the production baseline. Verify current instance prices before estimating.

**Lock-in:** Low. Dockerfile / buildpack deploys portable.

## Cloudflare Workers + Durable Objects

**What it is:** Edge JavaScript/TypeScript runtime + globally-distributed stateful objects + integrated Queues, R2, D1, KV, Vectorize, Workers AI.

**Best for:**

- Latency-critical APIs (<50ms first byte globally)
- Edge AI inference (Workers AI) or LLM proxying (AI Gateway)
- Agentic workloads needing stateful coordination at the edge
- High-volume, low-cost APIs

**Compute model:**

- Workers: V8 isolates, sub-ms cold start, CPU-limited execution. Free plan is 10ms CPU time per request; Paid plan defaults to 30s CPU time, configurable up to 5 minutes. HTTP-triggered Workers have no hard wall-clock limit while the client remains connected (`ctx.waitUntil()` extends up to 30s post-response for cleanup work).
- Subrequests per invocation: Free plan is 50 external (+1,000 to Cloudflare services). Paid plan defaults to 10,000, configurable up to 10M as of a February 2026 platform change — re-verify current defaults before sizing a high-fan-out agent or Durable Object workload.
- Queue consumers and Durable Object alarms: each capped around 15 minutes of wall-clock time per invocation — separate from the HTTP CPU limit above; don't conflate the two.
- Durable Objects: single-instance stateful workers, perfect for chat rooms, game state, agent sessions
- Queues: at-least-once async with retries
- Cron Triggers: scheduled workers (shorter duration budget than queue consumers/alarms; verify current cron duration tiers)
- AI Gateway: provider routing, caching, observability
- Workers AI: run open models at the edge

**Strengths:**

- Lowest latency at scale of any platform here
- Generous free tier (100k req/day)
- Globally distributed by default — no region choice
- Durable Objects fundamentally change what edge can do (per-entity state)
- AI Gateway is a major asset for multi-provider AI work

**Weaknesses:**

- V8 isolates ≠ Node.js — package compatibility is improving but still tighter
- Python in Workers is experimental
- CPU is not wall-clock: queue consumers, cron triggers, and Durable Object alarms have separate duration limits. Long work still needs Workflows, Queues, Durable Objects, or an external orchestrator.
- Queue handlers are at-least-once; configure retries, idempotency, and DLQs deliberately
- Durable Objects are an opinionated abstraction with learning curve
- Heaviest lock-in of any platform on this list

**Pricing shape:** $5/mo Workers Paid + per-million request + per-GB-second duration. Cheap until very high volume.

**Lock-in:** High. Worker code generally needs adaptation to run elsewhere; Durable Objects have no portable equivalent.

## Deno Deploy

**What it is:** Deno's managed runtime platform. The 2026 Deno Deploy platform is a rework of Deploy Classic, with stronger Deno/Node/framework support but different limits and regions.

**Best for:**

- Deno or Node apps that benefit from Deno 2 and integrated builds
- Teams already using Deno locally
- Framework apps where the new Deploy platform supports the target runtime well

**Compute model:**

- Deno 2 runtime with improved Node and framework support
- GitHub or CLI deploys with integrated builds
- Cron supported; queues are not supported on the new Deploy platform as of the May 2026 docs

**Strengths:**

- TypeScript-native, no transpilation for Deno-native apps
- Web-standard APIs
- Better Node/framework support than Deploy Classic
- Clean DX

**Weaknesses:**

- Deploy Classic and the subhosting v1 API are scheduled to shut down July 20, 2026 — as of this document's last check that is days away, not a future planning item. Any project still on `dash.deno.com` needs an active migration in flight now: projects do not transfer automatically, and a new app must be created and redeployed at the current console.
- New Deploy currently has fewer regions than Deploy Classic, with self-hostable regions for extra coverage
- Queues existed in Deploy Classic but are not supported in the new Deploy platform
- Smaller ecosystem and fewer first-party integrations than Cloudflare or Vercel

**Pricing shape:** Verify current Deno Deploy pricing and migration status; do not assume Deploy Classic pricing or limits.

**Lock-in:** Low–medium. Deno code mostly portable to Cloudflare Workers / self-host with `denoland/deno`.

## Northflank

**What it is:** Container-based PaaS with build pipelines, multi-cluster support, and more control than Render.

**Best for:**

- Teams wanting Render-style DX with more configurability
- Multi-environment (staging, prod, preview) workflows
- Microservices on containers

**Compute model:**

- Containers (Docker)
- Managed services (Postgres, Redis, etc.)
- Pipelines for build/deploy

**Strengths:**

- More flexible than Render
- Good multi-env workflows
- Reasonable pricing for small teams

**Weaknesses:**

- Smaller community
- Less mind share than competitors
- Documentation lighter

**Pricing shape:** Free trial + $9/mo+. Container-priced.

**Lock-in:** Low. Standard Docker.

## Koyeb

**What it is:** Serverless containers deployed globally; "always-on without machine ops."

**Best for:**

- Always-on containers when Fly.io's CLI-first model is too much
- Multi-region without Fly's complexity
- Bots and workers needing global presence

**Compute model:**

- Containers, auto-scaled
- Global anycast load balancing
- Postgres available

**Strengths:**

- Global by default
- Cleaner UI than Fly.io
- Low-cost instances available; the single free instance per organization is explicitly scoped to testing/hobby use, not a beta feature

**Weaknesses:**

- Smaller ecosystem
- Less battle-tested than larger players
- Documentation less comprehensive
- Free instance is capped to one region (typically Frankfurt or Washington, D.C.), cannot run as a Worker Service, has no custom scaling or Volumes, and scales to zero after roughly an hour idle — verify current specifics before treating any of these as fixed

**Pricing shape:** Per-instance per-hour; free instance has region, worker-service, scaling, volume, and scale-to-zero limits described above.

**Lock-in:** Low. Standard Docker.

## Feature Matrix

| Feature | Vercel | Fly.io | Railway | Render | CF Workers | Deno Deploy | Northflank | Koyeb |
|---|---|---|---|---|---|---|---|---|
| Always-on processes | No | Yes | Yes | Yes | partial (DO) | No | Yes | Yes |
| WebSocket / long-held conn | No | Yes | Yes | Yes | Yes (DO) | partial | Yes | Yes |
| Edge / multi-region default | Yes | Yes (explicit) | No | No | Yes | Yes | Yes | Yes |
| Max request duration | 300s Hobby / 800s Pro+ Fluid GA / 1800s Pro+ extended-duration beta | no fixed request cap for containers | container/service dependent | container/service dependent | CPU-limited (10ms free / 30s default–5min max paid); HTTP wall time not hard-capped while connected; queues/cron/DO alarms separately capped (~15 min) | platform-specific; verify new Deploy limits | container/service dependent | container/service dependent |
| Subrequests per invocation | n/a (not the limiting factor) | n/a | n/a | n/a | 50 free (+1,000 to CF services) / 10,000 default paid, configurable to 10M | n/a | n/a | n/a |
| Built-in cron | Yes | Yes | Yes | Yes | Yes | partial | Yes | partial |
| Built-in queue | Yes (Beta) | No | No | No | Yes | No on new Deploy | partial | partial |
| Managed Postgres | partial | Yes Managed Postgres; legacy PG differs | Yes | Yes | D1 is SQLite, not Postgres | No | Yes | Yes |
| Object storage | Caution (Blob) | partial | No | Yes | Yes (R2) | No | No | No |
| AI Gateway | Yes | No | No | No | Yes | No | No | No |
| Built-in vector DB | Caution | No | No | No | Yes (Vectorize) | No | No | No |
| Preview deployments | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes |
| Docker support | partial | Yes | Yes | Yes | No | No | Yes | Yes |
| Free tier (production-usable) | conditional | trial/credits vary | trial/free credits vary | sleeps after ~15 min idle | Yes for some workloads | verify current plan | trial/credits vary | No — free instance is a single-region hobby/testing tier, not preview software |

## Pricing Shape Matrix

| Platform | Free for prototyping? | Production entry point | Scales steeply with |
|---|---|---|---|
| Vercel | Yes, mostly prototype/non-commercial | Pro/Enterprise depending on workload | Bandwidth, function duration, seats, AI products |
| Fly.io | Trial/credits vary | Pay-as-you-go machines | Machine count, machine size, bandwidth, volumes, Managed Postgres |
| Railway | Free/trial credits vary | Hobby for personal; Pro for teams | Resource usage, replicas, storage, egress |
| Render | Free web services may sleep | Paid web/worker/database instances | Service count and instance size |
| Cloudflare Workers | Yes for many prototypes | Workers Paid plus usage | CPU, requests, storage products, bindings |
| Deno Deploy | Verify current platform | Verify current plan | Runtime, build, region, and usage limits |
| Northflank | Trial/credits vary | Container/team plans | Container hours, add-ons, environments |
| Koyeb | Free instance is preview/hobby only | Per-instance/hour | Instance count, instance type, bandwidth |

## Decision Tree

```text
Q1: Does the workload need to hold an open connection
     (WebSocket, SSE longer than minutes, SIP, long polling)?
     │
     ├── YES → Fly.io / Railway / Render / CF Durable Objects / Koyeb
     │
     └── NO → continue
             │
Q2: Single-request CPU or wall duration > 30s?
     │
     ├── YES: verify plan-specific limits; Vercel Fluid, Cloudflare Paid (CPU-configured), or containers may fit
     │
     └── NO: any platform, subject to runtime compatibility
             │
Q3: Need edge / global low latency?
     │
     ├── YES → Cloudflare Workers, Vercel Edge, Deno Deploy
     │
     └── NO → continue
             │
Q4: Is the stack Next.js / React-heavy?
     │
     ├── YES → Vercel
     │
     └── NO → continue
             │
Q5: Multiple service types (web + worker + cron)?
     │
     ├── YES → Render or Railway (explicit service types)
     │
     └── NO → Fly.io for always-on, Vercel for stateless
```

## Migration Paths

Common patterns observed in May 2026:

- **Heroku → Railway**: nearly drop-in
- **Heroku → Render**: clean, slightly more setup
- **Vercel → Fly.io**: when state holds you back (WebSocket, sessions, bots)
- **Fly.io → AWS ECS / Kubernetes**: when you need control / compliance beyond PaaS
- **Railway → AWS**: when finance/compliance demands AWS
- **Cloudflare Workers → AWS Lambda@Edge**: rare; Workers has better ergonomics
- **Anywhere → Cloudflare Workers**: when latency budget gets brutal

Plan exits before you depend on platform-specific primitives.

## What "Deploy and Forget" Means in Practice

Removed for you:

- OS patching
- TLS / certificates
- Load balancer config
- Health-check wiring
- Zero-downtime deploys
- Log aggregation
- Build pipeline boilerplate

Still your job:

- Application correctness
- Schema migrations
- Secret rotation (use external secret store — see [`../../ai-bot-builder/references/secret-rotation-and-model-fallback.md`](../../ai-bot-builder/references/secret-rotation-and-model-fallback.md))
- Cost monitoring (alerts at the billing platform)
- Provider failover for LLMs and external APIs
- Backups (the platform's automated backups are not your DR plan)
- Compliance (recording retention, audit logs, GDPR / FCA / HIPAA)
- Observability beyond what the platform shows (Langfuse / OpenTelemetry / Phoenix)

The platforms above remove infrastructure work. They don't remove engineering work — they let you spend it elsewhere.

## Cross-References

- [`agent-hosting-matrix.md`](agent-hosting-matrix.md) — pick a stack for an agent workload
- [`../../software-baas-platforms/SKILL.md`](../../software-baas-platforms/SKILL.md) — data-layer companion
- [`../../ai-coding-agents-tasks/references/webhook-and-queue-triggers.md`](../../ai-coding-agents-tasks/references/webhook-and-queue-triggers.md) — Shape A triggers
- [`../../ai-bot-builder/references/production-deployment.md`](../../ai-bot-builder/references/production-deployment.md) — Shape B bot stack
- [`../../ai-voice-bots/references/production-deployment.md`](../../ai-voice-bots/references/production-deployment.md) — Shape B-voice stack
- [`../../ai-agents/references/autonomous-loop-patterns.md`](../../ai-agents/references/autonomous-loop-patterns.md) — Shape C loop
- [`../../software-workflow-automation/SKILL.md`](../../software-workflow-automation/SKILL.md) — Inngest / Temporal substrate
- [`../../ops-cost-optimization/SKILL.md`](../../ops-cost-optimization/SKILL.md) — controlling spend once deployed
