# PaaS Platform Comparison

Use this reference to pick a compute hosting platform when you've already decided you don't want to manage Kubernetes, EC2 fleets, or your own infrastructure.

Limits, beta status, regions, and prices in this file change often. Before giving hard claims about limits, beta status, regions, or prices, verify against [`../data/sources.json`](../data/sources.json). Fetch rates from provider pricing pages; this reference stores billing dimensions, not prices.

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
- [Other Platforms and Vendor Status](#other-platforms-and-vendor-status)
- [Feature Matrix](#feature-matrix)
- [Pricing Shape Matrix](#pricing-shape-matrix)
- [Decision Tree](#decision-tree)
- [Migration Paths](#migration-paths)
- [What "Deploy and Forget" Means in Practice](#what-deploy-and-forget-means-in-practice)

## The Eight Platforms

| Platform | Compute Model | Sweet Spot |
|---|---|---|
| **Vercel** | Functions + Services (including container builds) | Next.js, Jamstack, AI SDK workloads |
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
- AI applications using streaming, tool calls, and structured outputs from AI SDK
- Triggered agent runs via Cron Jobs, Queues, or Workflow; check product maturity
- Marketing sites, dashboards, content products

**Compute model:**

- Functions with supported language runtimes; check the duration page for plan/runtime eligibility, extended duration, and networking restrictions.
- [Services](https://vercel.com/docs/services) groups frontend and backend services in one deployment, with top-level public routing and internal bindings. Setting a service's `runtime` to `container` builds a Docker image; it still runs on Vercel Functions rather than an always-on container host ([container docs](https://vercel.com/docs/functions/container-images)).
- [WebSocket connections](https://vercel.com/kb/guide/do-vercel-serverless-functions-support-websocket-connections) are pinned to a Function for its maximum duration; reconnects may hit another instance. Use external durable state and resumable clients. Verify supported runtimes and maturity before selection.
- Durable workflows can span multiple bounded executions; validate per-step limits rather than treating one invocation as unbounded.
- Do not rely on local filesystem state surviving an invocation or deployment.

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

- Process state is ephemeral; bounded WebSockets need shared state and reconnect handling
- A function duration cap still applies, including to container builds and sockets
- Pricing scales steeply with bandwidth and function execution; runaway costs are common
- Env var rotation requires redeploy unless you use external secret store
- Verify Queues maturity, poison-message handling, and dead-letter behavior before making it load-bearing

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

- Fly Machines: VM-backed containers; size and benchmark startup for the target image/region
- Auto-start / auto-stop on demand
- Private 6PN network across regions
- Volumes for persistent storage
- Fly Managed Postgres is the supported production database path: automatic failover, backups, connection pooling, and cross-node storage replication across multiple regions (check the current region list and storage ceiling in Fly's MPG docs before sizing). Legacy/unmanaged Fly Postgres guidance should not be treated as managed Postgres guidance.

**Strengths:**

- Long-held connections work fine (WebSocket, SSE)
- Explicit placement in multiple regions; database topology remains a separate decision
- Predictable Docker model — minimal lock-in
- Powerful CLI; deploy from `fly.toml`

**Weaknesses:**

- CLI-first; less polished web UI than Vercel/Railway
- Legacy Fly Postgres and self-managed Postgres require more operational ownership; Managed Postgres adds HA, backups, support, and encryption but still has feature gaps to verify
- You manage machine sizing and scaling rules (defaults are sensible)
- Less hand-holding for first-time deployers

**Pricing shape:** Machine resources, bandwidth, volumes, and managed services; fetch [Fly rates](https://fly.io/docs/about/pricing/) and include stopped-machine storage and any warm capacity.

**Lock-in:** Low. Docker-based; migrates cleanly to any container host.

## Railway

**What it is:** Heroku-style PaaS with services, databases, cron, and worker primitives in one UI.

**Best for:**

- Full-stack startups deploying app + Postgres + worker as a bundle
- Teams that grew up on Heroku and want similar ergonomics
- Migration target from Heroku

**Compute model:**

- Services: web service or worker, auto-scaled
- Database services/templates; verify which operational guarantees the selected product actually manages
- Cron jobs
- Auto-detected builds or Dockerfile; check the current builder and reproducibility controls

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
- Managed Postgres and Key Value services
- [Render Workflows](https://render.com/docs/workflows): tasks execute in separate on-demand instances, with chaining and configurable retries. Tasks do not expose incoming ports; they initiate outbound connections. Check task duration, scheduling, preview, compliance, and replay/checkpoint limitations before treating this as interchangeable with Temporal.

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

- APIs that benefit from execution close to users; measure end-to-end latency including data and model calls
- Edge AI inference (Workers AI) or LLM proxying (AI Gateway)
- Agentic workloads needing stateful coordination at the edge
- High-volume, low-cost APIs

**Compute model:**

- Workers: V8 isolates. Check the [limits page](https://developers.cloudflare.com/workers/platform/limits/) for CPU, subrequest, and memory budgets by plan. CPU consumption differs from wall-clock time; HTTP connection lifetime, post-response work, and queue/cron/alarm durations have separate rules.
- Durable Objects: single-instance stateful workers, perfect for chat rooms, game state, agent sessions
- Queues: at-least-once async with retries
- Cron Triggers: scheduled workers with trigger-specific CPU/wall-time budgets.
- Containers: Docker workloads integrated with Workers/Durable Objects; verify availability and runtime limits. [Billing](https://developers.cloudflare.com/containers/pricing/) distinguishes active CPU from provisioned memory/disk.
- AI Gateway: provider routing, caching, observability
- Workers AI: run open models at the edge

**Strengths:**

- Execution close to users can reduce ingress latency; model/data placement still dominates many agent workloads
- Check the free tier against the workload and commercial requirements
- Globally distributed by default — no region choice
- Durable Objects fundamentally change what edge can do (per-entity state)
- AI Gateway is a major asset for multi-provider AI work

**Weaknesses:**

- V8 isolates ≠ Node.js — package compatibility is improving but still tighter
- Check Python and Node package/runtime compatibility for the workload
- CPU is not wall-clock: queue consumers, cron triggers, and Durable Object alarms have separate duration limits. Long work still needs Workflows, Queues, Durable Objects, or an external orchestrator.
- Queue handlers are at-least-once; configure retries, idempotency, and DLQs deliberately
- Durable Objects are an opinionated abstraction with learning curve
- Heaviest lock-in of any platform on this list

**Pricing shape:** Requests and CPU for Workers, plus product-specific storage/duration/operation units. Fetch [Workers rates](https://developers.cloudflare.com/workers/platform/pricing/) and price each binding separately.

**Lock-in:** High. Worker code generally needs adaptation to run elsewhere; Durable Objects have no portable equivalent.

## Deno Deploy

**What it is:** Deno's managed runtime platform. The new Deno Deploy platform is a rework of Deploy Classic, with stronger Deno/Node/framework support but different limits and regions.

**Best for:**

- Deno or Node apps that benefit from Deno 2 and integrated builds
- Teams already using Deno locally
- Framework apps where the new Deploy platform supports the target runtime well

**Compute model:**

- Deno 2 runtime with improved Node and framework support
- GitHub or CLI deploys with integrated builds
- Cron supported; `Deno.Kv` queues (`enqueue`/`listenQueue`) are not supported on the new Deploy platform — check the migration guide for changes

**Strengths:**

- TypeScript-native, no transpilation for Deno-native apps
- Web-standard APIs
- Better Node/framework support than Deploy Classic
- Clean DX

**Weaknesses:**

- Deploy Classic and the subhosting v1 API have been shut down. Projects were not transferred automatically; anything not migrated must be recreated and redeployed on the new Deploy.
- New Deploy has fewer managed regions than Classic had (check the current list), with self-hostable regions for extra coverage
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

**Pricing shape:** Container resources, jobs, add-ons, and environments. Fetch [Northflank rates](https://northflank.com/pricing) and account for replicas and idle capacity.

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
- Low-cost instances available; the single free instance per organization is a permanent testing/hobby tier, not a beta feature

**Weaknesses:**

- Smaller ecosystem
- Less battle-tested than larger players
- Documentation less comprehensive
- Vendor continuity: Koyeb announced a definitive agreement to join Mistral AI; re-check product and pricing direction before a long commitment
- Verify free-instance region, Worker Service, scaling, Volume, and idle restrictions before sizing a workload

**Pricing shape:** Per-instance per-hour; free instance has region, worker-service, scaling, volume, and scale-to-zero limits described above.

**Lock-in:** Low. Standard Docker.

## Other Platforms and Vendor Status

Short rows only; verify against the linked primary pages before recommending. Choosing a host that is winding down is the costliest mistake in this domain.

| Platform | What it is / status | Use it when |
|---|---|---|
| **Heroku** | Buildpack PaaS. Moved to a "sustaining engineering model": new customers can no longer buy Enterprise contracts; credit-card customers see no pricing or service changes (heroku.com/blog/an-update-on-heroku) | Existing apps that work. For new builds, weigh the maintenance posture; migrations need an add-on, Review Apps and buildpack mapping, not a "drop-in" swap |
| **Netlify** | Git-based static/serverless web platform on a credit-based pricing model; plans differ by included credits (check netlify.com/pricing) | Static and Jamstack sites with light functions; same stateless limits as Vercel-style hosts |
| **DigitalOcean App Platform** | Managed PaaS deploying from Git or container images; services, workers, cron/deployment jobs, static sites and functions; Dockerfile or buildpack builds (docs.digitalocean.com/products/app-platform) | Heroku/Render-style ergonomics inside a DigitalOcean account |
| **Modal** | GPU/CPU functions and containers with autoscaling; functions scale to zero when idle ([scaling docs](https://modal.com/docs/guide/scale), [GPU docs](https://modal.com/docs/guide/gpu)) | GPU inference or batch jobs when managed function/container execution fits; benchmark model loading, batching, warm-pool cost, regions and capacity before choosing hardware |
| **Google Cloud Run** | Container platform with services (HTTP, scale to zero), jobs (run to completion), worker pools (always-on queue consumers, manually scaled) and Instances (preview); GPUs supported (docs.cloud.google.com/run) | Container workloads that must live in GCP, need GPU inference without owning clusters, or need scale-to-zero containers |
| **AWS App Runner → ECS Express Mode** | App Runner is closed to new customers; existing customers keep full use but get no new features. AWS recommends ECS Express Mode: one API call provisions an ECS Fargate service, ALB, autoscaling and networking in your account, with no extra charge beyond the resources (App Runner availability-change page) | ECS Express Mode for simple container apps that must be on AWS; do not start new App Runner builds |
| **Coolify** | Open-source, self-hostable platform for deploying apps, databases and services on servers you control; a managed Coolify Cloud control plane also exists | Cost-floor self-host PaaS on your own VMs when you can own patching, backups and uptime |
| **Kamal** | Deploy tool that ships Docker containers to any server over SSH with zero-downtime deploys, rolling restarts and accessory services (kamal-deploy.org) | Teams comfortable with plain servers that want deploy ergonomics, not a hosted control plane |
| **Dokku** | Open-source single-server PaaS; `git push` builds via Dockerfile or buildpacks (dokku.com) | One-box hobby or internal apps; no multi-node HA |
| **Deno Deploy Classic** | Shut down (see Deno Deploy above) | Never; migrate |
| **Koyeb** | Announced agreement to join Mistral AI | See Koyeb above; treat as a vendor-continuity item |

Self-host options (Coolify, Kamal, Dokku) shift infrastructure ownership to the team; include VM and operational costs and use the responsibility checklist below.

## Feature Matrix

| Feature | Vercel | Fly.io | Railway | Render | CF Workers | Deno Deploy | Northflank | Koyeb |
|---|---|---|---|---|---|---|---|---|
| Always-on processes | No | Yes | Yes | Yes | partial (DO) | No | Yes | Yes |
| WebSocket / long-held conn | Bounded by Function duration; reconnect/shared state required | Yes | Yes | Yes | Yes (DO) | partial | Yes | Yes |
| Edge / multi-region default | Yes | Yes (explicit) | No | No | Yes | Yes | Yes | Yes |
| Execution limits | Check plan/runtime duration | Check Machine/process/proxy limits | Check service limits | Check service/task limits | CPU and wall time differ by trigger | Check new Deploy limits | Check service/job limits | Check service limits |
| Built-in cron | Yes | Yes | Yes | Yes | Yes | partial | Yes | partial |
| Async execution | Queues / Workflow; verify maturity | External queue + Machines | Workers + external queue | Workers / Workflows tasks | Queues / Workflows | Check new Deploy support | Jobs / pipelines | Workers; check available integrations |
| Managed Postgres | partial | Yes Managed Postgres; legacy PG differs | Yes | Yes | D1 is SQLite, not Postgres | No | Yes | Yes |
| Object storage | Caution (Blob) | partial | No | Yes | Yes (R2) | No | No | No |
| AI Gateway | Yes | No | No | No | Yes | No | No | No |
| Built-in vector DB | Caution | No | No | No | Yes (Vectorize) | No | No | No |
| Preview deployments | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes |
| Docker support | Services container builds on Functions | Yes | Yes | Yes | Containers; check limits | Check target runtime | Yes | Yes |

## Pricing Shape Matrix

These are dimensions to price, not a stored rate card. At selection time record the provider URL, plan, region, units, included usage, overage rates, and lookup date; compare idle and burst scenarios separately.

| Compute shape | Dominant billing inputs | Lookup |
|---|---|---|
| Vercel Functions / Services | Active CPU, provisioned memory, invocations, transfer, subscription, attached products | [Vercel pricing](https://vercel.com/pricing), [Services billing](https://vercel.com/docs/services/pricing) |
| Fly / Railway / Render / Northflank / Koyeb services | Provisioned resources or service-instance time, replicas, storage, egress, subscription/credit floor | [Fly](https://fly.io/docs/about/pricing/), [Railway](https://railway.com/pricing), [Render](https://render.com/pricing), [Northflank](https://northflank.com/pricing), [Koyeb](https://www.koyeb.com/pricing) |
| Cloudflare Workers / Containers | Requests and CPU plus binding-specific storage, duration, and operations; Containers provisioned memory/disk differs from active CPU | [Workers](https://developers.cloudflare.com/workers/platform/pricing/), [Containers](https://developers.cloudflare.com/containers/pricing/) |
| Render Workflows | Per-task compute duration plus retention of arguments/results | [Workflows pricing and limits](https://render.com/docs/workflows-limits) |
| Modal GPU functions | GPU/CPU/memory time, warm/idle reservation, storage, egress | [Modal pricing](https://modal.com/pricing), [warm-container trade-off](https://modal.com/docs/guide/cold-start) |
| Deno Deploy | Target platform's runtime, builds, transfer and subscription dimensions | [Deno pricing](https://deno.com/deploy/pricing) |

### Worked comparison: synthetic workload, unpriced

Assume **10,000 isolated requests per month**, each using **0.2 CPU-seconds**, **2 seconds of memory residency at 1 GiB**, no overlapping billing, and **20 GiB of transfer**. These are invented workload inputs for arithmetic, not measured performance or vendor rates.

- Usage-based compute: `10,000 × 0.2 = 2,000 CPU-seconds = 0.556 CPU-hours`; memory: `10,000 × 2 × 1 = 20,000 GiB-seconds = 5.556 GiB-hours`. Cost expression: `0.556 × CPU-hour rate + 5.556 × GiB-hour rate + 10,000 × invocation rate + 20 × GiB-transfer rate + plan floor`, less applicable included usage.
- Always-on service: in an illustrative **30-day month**, one provisioned instance runs `30 × 24 = 720 hours`. Cost expression: `720 × instance-hour rate + 20 × GiB-transfer rate + storage + plan floor`. If pricing is a monthly instance charge, use that charge directly.
- GPU variant: **1,000 isolated jobs × 15 billed GPU-seconds = 15,000 GPU-seconds = 4.167 GPU-hours**. Keeping one GPU reserved throughout the same month means **720 GPU-hours**, before CPU/memory and other charges. Cold starts, model loading, batching, and warm capacity can change both totals; measure them.

The comparison remains **unpriced** until verified rates are supplied. A CPU-hour unit does not guarantee equivalent throughput across products. Check billing concurrency/minimums, then test a representative authorized workload before choosing a cost winner.

## Decision Tree

```text
Q1: Does the workload need to hold an open connection
     (WebSocket, SSE longer than minutes, SIP, long polling)?
     │
     ├── YES → Fly.io / Railway / Render / CF Durable Objects / Koyeb; Vercel if bounded sockets and external state fit
     │
     └── NO → continue
             │
Q2: Does measured CPU or wall time exceed the target runtime budget?
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

Common patterns:

- **Heroku → Railway / Render / DO App Platform**: map add-ons, Review Apps, buildpacks and Postgres cut-over explicitly; none is a true drop-in
- **AWS App Runner → ECS Express Mode**: AWS-documented blue/green path with DNS weighted routing
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
- Health-check integration (the application must expose a meaningful check)
- Zero-downtime deploys
- Log aggregation
- Build pipeline boilerplate

Still your job:

- Application correctness
- Schema migrations
- Secret rotation (use external secret store — see [`../../ai-bot-builder/references/secret-rotation-and-model-fallback.md`](../../ai-bot-builder/references/secret-rotation-and-model-fallback.md))
- Cost monitoring (alerts at the billing platform)
- Provider failover for LLMs and external APIs
- Backups and restore testing (verify product-specific automated-backup guarantees)
- Compliance (recording retention, audit logs, GDPR / FCA / HIPAA)
- Observability beyond what the platform shows (Langfuse / OpenTelemetry / Phoenix)

Verify which responsibilities the selected product actually covers; feature and backup guarantees differ by service type.

## Cross-References

- [`agent-hosting-matrix.md`](agent-hosting-matrix.md) — pick a stack for an agent workload
- [`../../software-baas-platforms/SKILL.md`](../../software-baas-platforms/SKILL.md) — data-layer companion
- [`../../ai-coding-agents-state/references/webhook-and-queue-triggers.md`](../../ai-coding-agents-state/references/webhook-and-queue-triggers.md) — Shape A triggers
- [`../../ai-bot-builder/references/production-deployment.md`](../../ai-bot-builder/references/production-deployment.md) — Shape B bot stack
- [`../../ai-voice-bots/references/production-deployment.md`](../../ai-voice-bots/references/production-deployment.md) — Shape B-voice stack
- [`../../ai-agents/references/autonomous-loop-patterns.md`](../../ai-agents/references/autonomous-loop-patterns.md) — Shape C loop
- [`../../software-workflow-automation/SKILL.md`](../../software-workflow-automation/SKILL.md) — Inngest / Temporal substrate
- [`../../ops-cost-optimization/SKILL.md`](../../ops-cost-optimization/SKILL.md) — controlling spend once deployed
