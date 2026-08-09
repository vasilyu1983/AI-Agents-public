---
name: software-backend
description: "Builds backend services and APIs with durable defaults. Use when implementing REST, GraphQL, tRPC, or gRPC services with auth, queues, data, or observability."
compatibility: Portable core. Works on Claude Code and Codex.
version: "1.1"
last_validated: 2026-07-11
---

# Software Backend Engineering

Use this skill for backend service implementation and review: API boundaries, auth, data access, jobs, caching, observability, and production hardening. If the main question is platform selection, system topology, or API-contract design without implementation, hand off early.

## Defaults

When this skill is active, prefer these defaults unless the repo or user says otherwise:

- validate at the boundary and keep types explicit
- use PostgreSQL plus pooling for relational workloads
- use structured logs, OpenTelemetry, explicit timeouts, and rate limits
- make mutations idempotent and background work retry-safe
- use RFC 9457 Problem Details for machine-readable errors

## Quick Reference

| Need | Default Direction |
|------|-------------------|
| Public HTTP API | REST with explicit contracts and timeouts |
| Internal TS monorepo API | tRPC when end-to-end type safety matters |
| High-throughput internal RPC | Connect or gRPC |
| Complex client-shaped reads | GraphQL |
| Relational data | PostgreSQL with migrations and pooling |
| Background work | Queue plus idempotent handlers and DLQ policy |
| Browser auth | OIDC or OAuth plus httpOnly cookies |
| Service auth | short-lived tokens, workload identity, or signed service credentials |
| Caching | explicit TTLs and invalidation rules |
| Observability | correlation IDs, traces, structured logs, saturation metrics |

## When to Use This Skill

- building or reviewing REST, GraphQL, tRPC, Connect, or gRPC services
- implementing auth, validation, rate limits, caching, queues, or webhook handling
- modelling schemas and running safe migrations
- hardening service behavior for retries, timeouts, and observability
- scaffolding or refactoring a backend with production defaults

## Route Elsewhere

- frontend-only work -> [software-frontend](../software-frontend/SKILL.md)
- infrastructure provisioning and cluster design -> [ops-devops-platform](../ops-devops-platform/SKILL.md)
- API contract design without implementation -> [dev-api-design](../dev-api-design/SKILL.md)
- BaaS platform selection (data/auth layer) -> [software-baas-platforms](../software-baas-platforms/SKILL.md)
- PaaS hosting selection (compute layer: Vercel, Fly.io, Railway, Render, Cloudflare Workers, Deno Deploy) -> [software-paas-hosting](../software-paas-hosting/SKILL.md)
- SQL tuning and indexing deep dives -> [data-sql-optimization](../data-sql-optimization/SKILL.md)
- security reviews and threat modelling -> [software-security-appsec](../software-security-appsec/SKILL.md)
- broader system architecture -> [software-architecture-design](../software-architecture-design/SKILL.md)

---

## Workflow

1. Confirm the real constraint: latency, team skill, runtime, compliance, data model, or delivery speed.
2. Choose the transport and framework based on that constraint, not on trend-chasing.
3. Define the boundary:
   - request and response contracts
   - auth and authorization rules
   - error model
   - idempotency and rate limiting
4. Define the data path:
   - schema and migrations
   - transaction boundaries
   - pooling and query budgets
   - cache and invalidation rules
5. Define the async path:
   - queue semantics
   - retry ownership
   - deduplication and DLQ
6. Add operability before calling it complete:
   - timeouts and cancellation
   - health checks
   - structured logs and traces
   - deploy and rollback expectations

---

## ASCII Flow

```text
Backend task
  -> Define endpoint, job, service, or data boundary
  -> Confirm runtime, framework, persistence, and integration contracts
  -> Design request validation, auth, errors, and idempotency
  -> Implement bounded slice with tests and observability
  -> Check performance, security, and rollout risk
  -> Verify behavior and document follow-up handoffs
```

## Technology Selection

Pick based on the strongest operational constraint:

- TypeScript-heavy team -> Fastify, Hono, or NestJS plus Prisma or Drizzle
- audited SQL and predictable concurrency -> Go with `sqlc/pgx`
- Python ecosystem or ML adjacency -> FastAPI plus SQLAlchemy
- enterprise .NET stack -> ASP.NET Core plus EF Core or explicit SQL access
- memory safety and explicitness -> Rust with Axum plus SQLx
- edge or serverless first -> lightweight stateless handlers with hard CPU and timeout budgets

Use [software-baas-platforms](../software-baas-platforms/SKILL.md) first when the real requirement is "ship auth, storage, and realtime quickly with less custom service code."

---

## Backend Non-Negotiables

| Category | Rule |
|----------|------|
| **API** | Mutating endpoints require idempotency keys where retries are plausible |
| **API** | List endpoints require explicit pagination (`limit`/`cursor`) and at least one filter |
| **API** | Errors are structured and machine-readable (RFC 9457 Problem Details) |
| **API** | Health endpoints separate liveness (`/healthz`) from readiness (`/readyz`) |
| **Data** | No `SELECT *` on wide or high-volume paths |
| **Data** | Transactions kept explicit; no implicit ambient transactions |
| **Data** | New or changed query plans verified with `EXPLAIN ANALYZE` before production |
| **Data** | ORM convenience layers bypassed on hot paths where auditability matters |
| **Dependencies** | Every outbound call has an explicit timeout; no framework-default infinite wait |
| **Dependencies** | Retries owned at exactly one layer (no double-retry across client + service) |
| **Dependencies** | Cache invalidation rule documented before caching is added |
| **Dependencies** | Background jobs safe to retry and observable (structured log on start/finish/failure) |
| **Operations** | Every request carries a correlation ID propagated to all downstream calls |
| **Operations** | Trace, log, and metric identifiers agree (no split identity) |
| **Operations** | Slow paths have explicit latency budgets (p99 target, not "fast enough") |
| **Operations** | Deploy procedure includes rollback step and smoke-check list |

---

## Performance and Reliability Triage

When a service is slow or unstable, debug in this order:

| Step | Check | Signal |
|------|-------|--------|
| 1 | Query behavior and N+1s | EXPLAIN output, ORM query log showing repeated identical queries |
| 2 | Indexes and execution plans | Seq scans on large tables, missing index on FK or filter columns |
| 3 | Connection pooling and queue depth | Pool wait time > 10ms; idle connections exhausted |
| 4 | Timeout and cancellation gaps | Requests hanging past deadline; no context propagation through outbound calls |
| 5 | Caching or read-shaping opportunities | Same query with same result executing > 10x/s; hot read path with no invalidation |
| 6 | Runtime or tier limits | CPU throttling, memory pressure, rate limit headers from upstream |

Do not add caching before you understand the real bottleneck.

---

## Operational Playbooks

- use [references/operational-playbook.md](references/operational-playbook.md) for full service design and review checklists
- use [qa-resilience](../qa-resilience/SKILL.md) when retries, deadlines, breakers, or degraded-mode behavior are the main question
- use [dev-api-design](../dev-api-design/SKILL.md) when the contract itself is the main artifact

## Production Readiness Checklist

Before marking a service production-ready:

- [ ] All mutating endpoints have idempotency keys or safe-retry semantics
- [ ] Every outbound call has an explicit timeout (no framework-default infinite waits)
- [ ] Health endpoint distinguishes liveness from readiness
- [ ] Correlation IDs propagated from inbound request to all downstream calls and logs
- [ ] DLQ policy defined for every queue consumer (what happens to poison messages)
- [ ] New query plans verified (`EXPLAIN ANALYZE`) before merge to main
- [ ] Rollback procedure documented and smoke-test list exists

## Known Traps

- Introducing asynchronous jobs to hide a broken synchronous path instead of fixing the contract, timeout budget, or workload shape.
- Shipping retries without deadlines, jitter, and idempotency keys, then multiplying load during incidents.
- Changing API or webhook behavior without a compatibility window, replay plan, or structured error-versioning posture.
- Adding caches before proving whether the real bottleneck is query shape, pooling, lock contention, or outbound dependency latency.
- Treating background consumers as “fire and forget” even though poison-message handling, replay semantics, and observability are undefined.

## Common Anti-Patterns

- Letting framework defaults define the service contract, error model, and cancellation semantics.
- Using one generic repository abstraction for every query, including hot paths that need explicit SQL, batching, or shape control.
- Mixing request handling, domain logic, external side effects, and persistence concerns in one controller or handler.
- Relying on eventual retries to clean up non-idempotent side effects.
- Calling a backend “production ready” before timeouts, readiness checks, trace correlation, and rollback smoke tests exist.

## Navigation

### Core references

- [references/backend-best-practices.md](references/backend-best-practices.md)
- [references/edge-deployment-guide.md](references/edge-deployment-guide.md)
- [references/infrastructure-economics.md](references/infrastructure-economics.md)
- [references/database-patterns.md](references/database-patterns.md)
- [references/message-queues-background-jobs.md](references/message-queues-background-jobs.md)
- [references/rpc-and-transport-patterns.md](references/rpc-and-transport-patterns.md)
- [references/go-best-practices.md](references/go-best-practices.md)
- [references/rust-best-practices.md](references/rust-best-practices.md)
- [references/python-best-practices.md](references/python-best-practices.md)
- [references/nodejs-best-practices.md](references/nodejs-best-practices.md)
- [references/csharp-best-practices.md](references/csharp-best-practices.md)
- [data/sources.json](data/sources.json)

### Shared review utilities

- [../software-clean-code-standard/assets/checklists/backend-api-review-checklist.md](../software-clean-code-standard/assets/checklists/backend-api-review-checklist.md)
- [../software-clean-code-standard/assets/checklists/secure-code-review-checklist.md](../software-clean-code-standard/assets/checklists/secure-code-review-checklist.md)
- [../software-clean-code-standard/references/auth-utilities.md](../software-clean-code-standard/references/auth-utilities.md)
- [../software-clean-code-standard/references/error-handling.md](../software-clean-code-standard/references/error-handling.md)
- [../software-clean-code-standard/references/config-validation.md](../software-clean-code-standard/references/config-validation.md)
- [../software-clean-code-standard/references/resilience-utilities.md](../software-clean-code-standard/references/resilience-utilities.md)
- [../software-clean-code-standard/references/logging-utilities.md](../software-clean-code-standard/references/logging-utilities.md)
- [../software-clean-code-standard/references/testing-utilities.md](../software-clean-code-standard/references/testing-utilities.md)
- [../software-clean-code-standard/references/observability-utilities.md](../software-clean-code-standard/references/observability-utilities.md)

### Templates

- [assets/nodejs/template-nodejs-prisma-postgres.md](assets/nodejs/template-nodejs-prisma-postgres.md)
- [assets/nodejs/template-nodejs-fastify-drizzle-postgres.md](assets/nodejs/template-nodejs-fastify-drizzle-postgres.md)
- [assets/go/template-go-fiber-gorm.md](assets/go/template-go-fiber-gorm.md)
- [assets/go/template-go-chi-sqlc-pgx.md](assets/go/template-go-chi-sqlc-pgx.md)
- [assets/rust/template-rust-axum-seaorm.md](assets/rust/template-rust-axum-seaorm.md)
- [assets/rust/template-rust-axum-sqlx.md](assets/rust/template-rust-axum-sqlx.md)
- [assets/python/template-python-fastapi-sqlalchemy.md](assets/python/template-python-fastapi-sqlalchemy.md)
- [assets/csharp/template-csharp-aspnet-efcore.md](assets/csharp/template-csharp-aspnet-efcore.md)

## Related Skills

> **Gate before invoking any foundation below:** Each foundation has a `When to Apply` / `When to Skip` section. If your task matches a skip-condition, route to the foundation it names instead — don't pull in primitives the task doesn't need.

- [software-architecture-design](../software-architecture-design/SKILL.md)
- [software-security-appsec](../software-security-appsec/SKILL.md)
- [ops-devops-platform](../ops-devops-platform/SKILL.md)
- [qa-resilience](../qa-resilience/SKILL.md)
- [qa-testing-strategy](../qa-testing-strategy/SKILL.md)
- [foundations-queueing-theory](../foundations-queueing-theory/SKILL.md) — Little's Law, M/M/c, and Kingman's formula for queue sizing in message-queue and rate-limiter design
- [foundations-distributed-systems](../foundations-distributed-systems/SKILL.md) — CAP, consistency models, quorum sizing, and idempotency contracts for service mesh and RPC patterns
- [foundations-reliability-theory](../foundations-reliability-theory/SKILL.md) — MTBF/MTTR, availability composition, and error-budget math for SLO-driven backend design
- [software-code-review](../software-code-review/SKILL.md)
- [dev-api-design](../dev-api-design/SKILL.md)
- [data-sql-optimization](../data-sql-optimization/SKILL.md)

## Fact-Checking

- Known bugs, regressions, framework/compiler/runtime footguns, and version-specific crash or workaround guidance must be verified against current primary web sources before being treated as current fact.
- Verify current runtime versions, support windows, framework capabilities, and cloud-platform constraints before final answers.
- Prefer official docs and release or support policy pages for version-sensitive recommendations.
- If web access is unavailable, mark version or support guidance as unverified.

## Learnings Loop

Before applying this skill on a non-trivial task, read `learnings.consolidated.md` in this directory (and `learnings.md` if present).

After applying it, if you encountered a pattern worth remembering, a mistake worth preventing, or a domain fact that surprised you, append one dated bullet to `learnings.md` via `agents-skills-feedback-loop/scripts/append_learning.py`. Do not modify `SKILL.md` itself.

