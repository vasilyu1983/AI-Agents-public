---
name: software-paas-hosting
description: Chooses PaaS hosting for apps, agents, APIs, and workers. Use when picking Vercel, Fly.io, Railway, Render, Cloudflare, Netlify, Heroku, Cloud Run, or container PaaS.
compatibility: Portable core. Works on Claude Code and Codex.
version: "1.1"
last_validated: 2026-07-11
---

# PaaS Compute Hosting Selection

Use this skill to pick the right managed compute platform for an application, agent, or bot when you don't want to operate Kubernetes, EC2 fleets, or your own infrastructure.

This is a **selection skill**, not an implementation guide. If you already know the platform and need help building on it, hand off to the platform's docs or to `software-backend` / agent-stack skills.

## When NOT To Use This Skill

| Need | Use Instead |
|------|-------------|
| Managed data/auth platforms (Supabase, Convex, Firebase) | [`../software-baas-platforms/SKILL.md`](../software-baas-platforms/SKILL.md) |
| Kubernetes, Terraform, GitOps, self-managed clusters | [`../ops-devops-platform/SKILL.md`](../ops-devops-platform/SKILL.md) |
| Cost optimization across existing infra | [`../ops-cost-optimization/SKILL.md`](../ops-cost-optimization/SKILL.md) |
| Backend implementation defaults (REST, auth, queues, observability) | [`../software-backend/SKILL.md`](../software-backend/SKILL.md) |
| Always-on bot serving stack (FastAPI + Redis) | [`../ai-bot-builder/references/production-deployment.md`](../ai-bot-builder/references/production-deployment.md) |
| Voice bot deployment (SIP, media, recording) | [`../ai-voice-bots/references/production-deployment.md`](../ai-voice-bots/references/production-deployment.md) |
| Agent trigger integration | [`../ai-coding-agents-state/references/webhook-and-queue-triggers.md`](../ai-coding-agents-state/references/webhook-and-queue-triggers.md) |
| LLM inference cost and provider routing | [`../ai-llm-inference/SKILL.md`](../ai-llm-inference/SKILL.md) |

## Quick Reference

| Question | Read | Outcome |
|----------|------|---------|
| Which PaaS fits this workload? | [`references/platform-comparison.md`](references/platform-comparison.md) | Strengths, weaknesses, pricing model, lock-in profile for the main platforms, plus short rows and vendor status for Heroku, Netlify, DO App Platform, Cloud Run, App Runner/ECS Express Mode, and Coolify/Kamal/Dokku |
| Where should I host an agent / bot / loop? | [references/agent-hosting-matrix.md](references/agent-hosting-matrix.md) | Per-shape (A/B/C) reference architectures with concrete platform stacks |
| Which facts must be rechecked? | [`data/sources.json`](data/sources.json) | Primary docs for volatile limits, pricing, and beta platform features |

## Workflow

1. Classify the workload by statefulness: stateless request, stateful session, always-on worker, durable workflow, or media/voice.
2. Bound execution shape: max request duration, concurrency, WebSocket/SSE needs, queue semantics, cron cadence, and restart tolerance.
3. Choose the placement driver: near users, near data, compliance boundary, cost floor, or team familiarity.
4. Read [`references/platform-comparison.md`](references/platform-comparison.md) for 1-2 eligible platforms; reject ineligible options with a concrete reason.
5. For agents and bots, confirm the selection in [references/agent-hosting-matrix.md](references/agent-hosting-matrix.md).
6. Before giving current limits, queues, regions, free-tier, or pricing claims, verify against [`data/sources.json`](data/sources.json) and primary docs.
7. Hand off implementation details to the chosen platform docs plus `software-backend`, `software-baas-platforms`, or agent runtime skills.

## Lookups

Treat PaaS limits, pricing, regions, managed database maturity, and beta/preview features as volatile. Verify before relying on:

- Vercel Functions and Services: supported runtimes/container builds, bounded WebSocket connections, function duration, Queues maturity, Workflow, AI Gateway, Sandbox, and billing. Containers retain the Functions execution model; see the Services section of the comparison.
- Cloudflare Workers CPU versus wall-clock limits by trigger, subrequest caps by plan, Queue retries/DLQs, Durable Objects, Containers, Workflows, Vectorize, and AI Gateway.
- Deno Deploy regions, queue support, and framework/runtime compatibility (Deploy Classic is shut down; the new Deploy differs).
- Vendor status: Heroku sustaining-engineering mode, App Runner closed to new customers, Koyeb joining Mistral AI — see the vendor-status table in platform-comparison.md.
- Fly.io Managed Postgres vs legacy Fly Postgres, Machines autostart/autostop behavior, regions, and support boundaries.
- Railway, Render, Northflank, and Koyeb plan limits, free-tier behavior, sleep/scale-to-zero semantics, and production support.
- Amazon Bedrock AgentCore Runtime: platform V1/V2, snapshot-safe initialization, microVM versus Instances lifetime, WebSocket frames versus invocation payloads, managed-service scope, pricing, and region availability. Load [references/aws-bedrock-agentcore.md](references/aws-bedrock-agentcore.md) for AWS agent selection.

## Three-Question Selection

Answer these three before reading deeper:

1. **Is the workload stateless per request, stateful per session, or always-running?**
   - Stateless → Vercel, Cloudflare Workers, Netlify, Deno Deploy
   - Stateful (sessions, WebSocket, long-held) → Fly.io, Railway, Render
   - Always-running (loops, daemons, cron-driven) → Fly.io Machines, Railway Workers, Render Background Workers, Inngest

2. **Can one request complete within the selected runtime's limits?**
   - Compare measured CPU time, wall time, memory, and payload size with the target plan's docs; CPU and wall time are different budgets.
   - A bounded request may fit Vercel Functions/Services or Workers. Jobs that outlive a request need container workers or durable orchestration.
   - Multi-step work with retries, compensation, or human waits needs a durable runtime regardless of host; compare Inngest, Temporal, Trigger.dev, Vercel Workflow, and Render Workflows.

3. **Does it need to be near users (edge) or near data (region)?**
   - Edge / low-latency first byte → Cloudflare Workers, Vercel Edge, Deno Deploy
   - Region / co-located with database → Fly.io (multi-region capable), Railway, Render

## Default Picks

| Workload | Default | Why |
|----------|---------|-----|
| Next.js product site / web app | **Vercel** | First-party support; AI SDK and AI Gateway baked in |
| Always-on Python/Node bot | **Fly.io** | Long-held connections, WebSocket, explicit machine lifecycle |
| Triggered agent (webhook → run) | **Vercel + Inngest** or **Cloudflare Workers + Queues** | Durable handoff; application side effects still need idempotency |
| Autonomous loop (Shape C) | **Inngest on Vercel** or **Fly.io Machines** | Durable iteration + budget caps |
| Voice bot control plane | **Fly.io** (paired with LiveKit Cloud for media) | Persistent agent worker per call |
| Multi-tenant SaaS backend | **Fly.io** or **Railway** | Stateful, scales horizontally, owns Postgres |
| Edge AI (low-latency LLM proxy) | **Cloudflare Workers + AI Gateway** | Low-latency global request handling; verify CPU and subrequest limits |
| AWS enterprise agent | **AgentCore Runtime + Memory + Gateway** | Session isolation and managed identity/tooling; compare microVM versus Instances using the current quota, region, and pricing pages |
| Background workers and cron | **Render Background Workers**, **Railway Workers**, **Fly.io Machines** | Explicit worker lifecycle; compare the idle cost floor |

## Graduating From PaaS To Raw Cloud

PaaS is the right default until one of these becomes true; treat each as a concrete trigger, not a vague "we're big now" feeling:

| Signal | Why PaaS stops fitting |
|--------|-------------------------|
| Sustained monthly PaaS spend materially exceeds one platform-team engineer's fully-loaded cost | The math flips toward owning the infra; verify current spend against current salary bands rather than assuming a fixed dollar threshold |
| Compliance mandates a named cloud, region, or physical control (data residency, FedRAMP, sector-specific hosting rules) | No PaaS vendor can contractually satisfy a requirement it wasn't built for |
| Workload needs custom kernels, specialized network hardware, or deterministic latency that managed hosts cannot provide | Check specialized managed compute first; GPU use alone can fit Modal or Cloud Run and does not require raw cloud |
| Multi-region active-active with strong consistency guarantees | Most PaaS databases and compute are single-region-primary or eventually consistent by default |
| Platform-specific limits (duration, subrequests, memory, egress) are hit routinely, not as an edge case | Repeated limit-hugging is a sign the workload has outgrown the platform's target shape, not a config problem |

Migrate incrementally: keep the stateless front end on PaaS, move only the constrained workload (the GPU job, the compliance-scoped service) to raw cloud, and re-evaluate the rest only if the same pressure recurs elsewhere.

## Deploy-and-Forget Scope

**Runtime fit probe.**

Use the comparison table to produce a shortlist, then scale evidence to the commitment. For a reversible or low-risk choice, inspect official capability limits and use local, emulated, or vendor-published evidence for the representative workload shape. Before a material production commitment, when the authorized task includes external testing, use a disposable non-production target with a defined spend bound to measure the real protocol, background work, storage, egress, latency, memory, restart, and observability behavior. Exercise crash recovery or rollback only when it is material to the requirement and safe for that target.

For the responsibility split, use [the canonical deploy-and-forget checklist](references/platform-comparison.md#what-deploy-and-forget-means-in-practice). Confirm each shortlisted product actually supplies the claimed infrastructure service.

## Lock-in Discipline

| Rule | Why |
|------|-----|
| Use Dockerfile-based deploys | Buildpacks and platform-specific config tie you to the host |
| Keep data in external services (Supabase, Neon, Upstash, Cloudflare D1) | Data portability is the hardest part of a platform migration |
| Use portable secret stores (Doppler, Infisical, AWS Secrets Manager) | Platform-native env vars do not survive a migration |
| Avoid host-proprietary primitives unless they are load-bearing | Vercel Edge Config, Cloudflare Durable Objects — choose deliberately |
| Pin runtime versions in `package.json` / `Dockerfile` | A platform's default Node/Python upgrade can break silently |

## Cost Discipline

Use [the pricing-shape matrix and worked unit comparison](references/platform-comparison.md#pricing-shape-matrix). Fetch rates from the selected provider's pricing page and include idle capacity, warm pools, memory residency, storage, egress, and any subscription floor. Report the result as **unpriced** until rates and workload measurements are supplied. Set billing alerts before production use.

## Common Anti-Patterns

- Treating Vercel functions as always-on workers (they're stateless; use Fly.io or Render)
- Putting Postgres on the same Fly.io machine as the app (split for durability)
- Hosting voice agents on Vercel (no SIP/media; use LiveKit Cloud + Fly.io)
- Running a 6-hour autonomous loop in a single function (use durable orchestrator)
- Using a platform's in-cluster database without a migration plan
- Assuming a free tier meets production uptime, capacity, or commercial-use requirements without checking its terms
- Deploying a multi-tenant bot to edge functions without per-tenant rate limits
- Treating a Vercel WebSocket connection as an immortal process: it is bounded by function duration and reconnects may reach another instance; persist state externally and implement resume ([Vercel guidance](https://vercel.com/kb/guide/do-vercel-serverless-functions-support-websocket-connections))
- Treating Cloudflare CPU allowance as a wall-clock request limit; HTTP, queue, cron, and Durable Object alarm budgets differ
- Choosing Vercel Queues without checking product maturity, poison-message handling, and dead-letter requirements
- Assuming Deno Deploy Classic behavior still applies; Classic is shut down and the new Deploy has different regions, APIs, and no `Deno.Kv` queues
- Confusing legacy Fly Postgres guidance with Fly Managed Postgres; evaluate support, backups, HA, regions, and missing managed features explicitly
- Treating Koyeb's free instance as production-ready without checking its testing/hobby terms, region, worker, volume, scaling, and idle behavior
- Ignoring egress and subrequest fan-out costs: a background job that fans out to many external calls or streams large payloads through a serverless function can grow the bill independently of request count
- Picking a platform by brand familiarity instead of the three-question selection; a bounded WebSocket function still needs external state and reconnect handling

## Navigation

- [`references/platform-comparison.md`](references/platform-comparison.md) — Vercel, Fly.io, Railway, Render, Cloudflare Workers + Durable Objects, Deno Deploy, Northflank, Koyeb
- [references/agent-hosting-matrix.md](references/agent-hosting-matrix.md) — Shape A/B/C → recommended PaaS and AWS stacks with reference architectures
- [references/aws-bedrock-agentcore.md](references/aws-bedrock-agentcore.md) — AWS-native agent runtime, memory, gateway, identity, observability, evaluation, policy, and registry choices
- [`data/sources.json`](data/sources.json) — primary documentation sources for volatile platform facts
- [`../software-baas-platforms/SKILL.md`](../software-baas-platforms/SKILL.md) — managed data/auth platforms (sibling skill)
- [`../ops-devops-platform/SKILL.md`](../ops-devops-platform/SKILL.md) — for K8s/self-managed substrate decisions
- [`../ai-coding-agents-state/SKILL.md`](../ai-coding-agents-state/SKILL.md) — agent task and trigger model
- [`../ai-agents/references/24-7-operating-model.md`](../ai-agents/references/24-7-operating-model.md) — SLOs and on-call once deployed
- [`../ai-agents/references/autonomous-loop-patterns.md`](../ai-agents/references/autonomous-loop-patterns.md) — Shape C loop drivers
- [`../ai-bot-builder/references/production-deployment.md`](../ai-bot-builder/references/production-deployment.md) — bot serving stack patterns
- [`../ai-voice-bots/references/production-deployment.md`](../ai-voice-bots/references/production-deployment.md) — voice deployment (LiveKit-paired)

## Related Skills

- [`../software-baas-platforms/SKILL.md`](../software-baas-platforms/SKILL.md) — data layer
- [`../software-backend/SKILL.md`](../software-backend/SKILL.md) — backend defaults
- [`../ops-devops-platform/SKILL.md`](../ops-devops-platform/SKILL.md) — when PaaS isn't enough
- [`../ops-cost-optimization/SKILL.md`](../ops-cost-optimization/SKILL.md) — cost governance
- [`../ai-llm-inference/SKILL.md`](../ai-llm-inference/SKILL.md) — LLM provider routing
- [`../software-workflow-automation/SKILL.md`](../software-workflow-automation/SKILL.md) — Inngest/Temporal durable substrate

## Learnings Loop

When prior decisions or pitfalls are relevant, consult `learnings.consolidated.md` if present; use `learnings.md` only for needed history or as the available fallback. Otherwise skip both.

After applying it, if you encountered a pattern worth remembering, a mistake worth preventing, or a domain fact that surprised you, append one dated bullet to `learnings.md` via `agents-skills-feedback-loop/scripts/append_learning.py`. Do not modify `SKILL.md` itself.
