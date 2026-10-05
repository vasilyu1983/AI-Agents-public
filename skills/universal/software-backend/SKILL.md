---
name: software-backend
description: "Builds backend services and APIs with durable defaults. Use when implementing REST, GraphQL, tRPC, or gRPC services with auth, queues, data, or observability."
compatibility: Portable core. Works on Claude Code and Codex.
version: "1.3"
last_validated: 2026-07-11
---

# Software Backend Engineering

Use this skill for backend service implementation and review: API boundaries, auth, data access, jobs, caching, observability, and production hardening. If the main question is platform selection, system topology, or API-contract design without implementation, hand off early.

## Quick Reference

| Need | Default Direction |
|------|-------------------|
| Public HTTP API | REST with explicit contracts and timeouts |
| Internal TS monorepo API | tRPC when end-to-end type safety matters |
| High-throughput internal RPC | Connect by default; plain gRPC only when you don't need browser/gRPC-Web compatibility |
| Complex client-shaped reads | GraphQL |
| Relational data | PostgreSQL with migrations and pooling |
| Background work | Queue plus idempotent handlers and DLQ policy |
| Browser auth | OIDC (authorization code with PKCE) plus httpOnly cookies |
| Service auth | prefer workload identity (cloud IAM, SPIFFE) over long-lived static credentials where the platform provides it; short-lived tokens or signed service credentials when it isn't available (multi-cloud, third-party, legacy) |
| Caching | explicit TTLs and invalidation rules |
| Observability | correlation IDs, traces, structured logs, saturation metrics |

## Route Elsewhere

- frontend-only work -> [software-frontend](../software-frontend/SKILL.md)
- infrastructure provisioning and cluster design -> [ops-devops-platform](../ops-devops-platform/SKILL.md)
- API contract design without implementation -> [dev-api-design](../dev-api-design/SKILL.md)
- BaaS platform selection (data/auth layer) -> [software-baas-platforms](../software-baas-platforms/SKILL.md)
- PaaS hosting selection (compute layer: Vercel, Fly.io, Railway, Render, Cloudflare Workers, Deno Deploy) -> [software-paas-hosting](../software-paas-hosting/SKILL.md)
- SQL tuning and indexing deep dives -> [data-sql-optimization](../data-sql-optimization/SKILL.md)
- schema design and migration choreography -> [software-database-design](../software-database-design/SKILL.md)
- WebSockets, SSE, and realtime transport design -> [software-realtime](../software-realtime/SKILL.md)
- security reviews and threat modelling -> [software-security-appsec](../software-security-appsec/SKILL.md)
- broader system architecture -> [software-architecture-design](../software-architecture-design/SKILL.md)
- C#/.NET backend services (ASP.NET Core, EF Core, Minimal API) -> [software-csharp-backend](../software-csharp-backend/SKILL.md)

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

## Technology Selection

Pick based on the strongest operational constraint:

- TypeScript-heavy team -> keep the repo's existing framework and ORM; for a new service, Fastify plus Drizzle (matches the Fastify/Drizzle template), NestJS plus Prisma for DI-heavy CRUD apps, Hono for edge or multi-runtime targets
- audited SQL and predictable concurrency -> Go with `sqlc/pgx`
- Python ecosystem or ML adjacency -> FastAPI plus SQLAlchemy
- memory safety and explicitness -> Rust with Axum plus SQLx
- edge or serverless first -> lightweight stateless handlers with hard CPU and timeout budgets

Use [software-baas-platforms](../software-baas-platforms/SKILL.md) first when the real requirement is "ship auth, storage, and realtime quickly with less custom service code."

---

## Backend Non-Negotiables

**Mutation correctness contract.**

For every externally retried mutation, define the idempotency scope, transaction boundary, authorization point, and observable terminal states before choosing transport or framework. Persist the idempotency record with the business write when possible; distinguish “not attempted,” “committed,” and “outcome unknown.” A retry must return the original result or resume safely, never duplicate the effect.

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

## Multi-Tenancy Decision

Decide tenancy explicitly for any service that stores more than one customer's data; choose per tenant tier, not once for the whole product.

- **Model:** shared schema + `tenant_id` enforced by row-level security (many small tenants; isolation depends on every query path) / schema-per-tenant (moderate counts, some customization; migrations fan out) / database-per-tenant (regulated or very large tenants, per-tenant restore or residency; highest ops cost).
- **Tenant context propagation:** derive the tenant from the authenticated principal, never from a client-supplied field; carry it through handlers, jobs, and outbound calls; set it transaction-locally (pooler-safe) and fail closed when unset; scope cache keys, idempotency keys, storage prefixes, and search indexes by tenant.
- **Noisy neighbours:** per-tenant rate limits, queue concurrency, and statement timeouts; give large tenants their own partition or limit. Prove isolation with a cross-tenant read test.

Rule: `rules/common/security.md` loads this invariant in every coding session.

Details, RLS SQL, and pooling traps: [references/database-patterns.md](references/database-patterns.md#multi-tenancy-isolation).

---

## Load and failure budget

For each downstream dependency, bound in-flight requests and queued work. When the bound is reached, reject new work with 429 or 503 and `Retry-After` where meaningful; do not accept work that cannot finish within the caller's deadline. Propagate cancellation, reserve time for the response, and shed lower-priority work before the critical path. Set one retry owner, a retry budget, exponential backoff with jitter, and an idempotency contract; test a slow or failed dependency under load to see whether p99, memory, and queue depth recover. For resilience test design and failure-budget review, load [qa-resilience](../qa-resilience/SKILL.md).

## Job runtime decision

Use a PostgreSQL-backed queue when the service already operates PostgreSQL, job volume fits measured database capacity, and a short transaction can claim each job. Use a managed broker or Redis-backed worker when throughput, isolation, or operational ownership justifies another dependency. Use durable execution when a job must resume a multi-step workflow across crashes or long waits; check the runtime's retry and history semantics before choosing it. A database queue needs `FOR UPDATE SKIP LOCKED`, lease expiry, idempotent effects, poison-job handling, and queue-depth monitoring. See [message queues and background jobs](references/message-queues-background-jobs.md#job-runtime-and-outbox-dispatch) for the claim and outbox alternatives.

---

## Performance and Reliability Triage

When a service is slow or unstable, debug in this order:

| Step | Check | Signal |
|------|-------|--------|
| 1 | Query behavior and N+1s | EXPLAIN output, ORM query log showing repeated identical queries |
| 2 | Indexes and execution plans | Seq scans on large tables, missing index on FK or filter columns |
| 3 | Connection pooling and queue depth | Sustained pool wait time; idle connections exhausted |
| 4 | Timeout and cancellation gaps | Requests hanging past deadline; no context propagation through outbound calls |
| 5 | Caching or read-shaping opportunities | Same query with same result executing repeatedly in a short window; hot read path with no invalidation |
| 6 | Runtime or tier limits | CPU throttling, memory pressure, rate limit headers from upstream |

Do not add caching before you understand the real bottleneck.

---

## Production Readiness Checklist

- [ ] Every row in Backend Non-Negotiables holds for the changed surface
- [ ] DLQ policy defined for every queue consumer (what happens to poison messages)

## Navigation

### Core references

- [references/operational-playbook.md](references/operational-playbook.md) — core backend patterns: task flow, API, auth, errors, caching, circuit breakers
- [references/backend-best-practices.md](references/backend-best-practices.md) — meta-guide for adding a new stack template to this skill; read only when authoring a template, not during backend implementation work
- [references/edge-deployment-guide.md](references/edge-deployment-guide.md)
- [references/infrastructure-economics.md](references/infrastructure-economics.md)
- [references/database-patterns.md](references/database-patterns.md)
- [references/message-queues-background-jobs.md](references/message-queues-background-jobs.md)
- [references/rpc-and-transport-patterns.md](references/rpc-and-transport-patterns.md)
- [references/go-best-practices.md](references/go-best-practices.md)
- [references/rust-best-practices.md](references/rust-best-practices.md)
- [references/python-best-practices.md](references/python-best-practices.md)
- [references/nodejs-best-practices.md](references/nodejs-best-practices.md)
- C#/.NET -> [software-csharp-backend](../software-csharp-backend/SKILL.md) (owns C#/.NET backend guidance)
- [data/sources.json](data/sources.json)

### Shared review utilities

Read one of these when the matching workflow step is active, not up front:

- [backend-api-review-checklist.md](../software-clean-code-standard/assets/checklists/backend-api-review-checklist.md) — read at the Production Readiness Checklist step
- [secure-code-review-checklist.md](../software-clean-code-standard/assets/checklists/secure-code-review-checklist.md) — read when the task includes a security review handoff
- [auth-utilities.md](../software-clean-code-standard/references/auth-utilities.md) — read while implementing auth (Workflow step 3)
- [error-handling.md](../software-clean-code-standard/references/error-handling.md) — read while defining the error model (Workflow step 3)
- [config-validation.md](../software-clean-code-standard/references/config-validation.md) — read during environment/config setup
- [resilience-utilities.md](../software-clean-code-standard/references/resilience-utilities.md) — read while defining retries, timeouts, or the async path (Workflow steps 5-6)
- [logging-utilities.md](../software-clean-code-standard/references/logging-utilities.md) — read while wiring structured logs (Workflow step 6)
- [testing-utilities.md](../software-clean-code-standard/references/testing-utilities.md) — read while writing tests for the bounded slice
- [observability-utilities.md](../software-clean-code-standard/references/observability-utilities.md) — read while wiring traces and metrics (Workflow step 6)

### Templates

Load the one matching the Technology Selection choice made for this task, not the whole set:

- [template-nodejs-prisma-postgres.md](assets/nodejs/template-nodejs-prisma-postgres.md) — NestJS/CRUD-heavy TS default
- [template-nodejs-fastify-drizzle-postgres.md](assets/nodejs/template-nodejs-fastify-drizzle-postgres.md) — Fastify/Drizzle TS default
- [template-go-fiber-gorm.md](assets/go/template-go-fiber-gorm.md) — Go, ORM-first
- [template-go-chi-sqlc-pgx.md](assets/go/template-go-chi-sqlc-pgx.md) — Go, audited SQL
- [template-rust-axum-seaorm.md](assets/rust/template-rust-axum-seaorm.md) — Rust, ORM-first
- [template-rust-axum-sqlx.md](assets/rust/template-rust-axum-sqlx.md) — Rust, explicit SQL
- [template-python-fastapi-sqlalchemy.md](assets/python/template-python-fastapi-sqlalchemy.md) — Python/ML-adjacent
- Other stacks: [Django REST](assets/python-django/template-python-django-rest.md), [Express](assets/nodejs-express/template-nodejs-express.md), [Spring Boot](assets/java/template-java-spring-boot.md)
- Enterprise .NET (C#) templates -> [software-csharp-backend/assets](../software-csharp-backend/assets/)

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

## Learnings Loop

When prior decisions or pitfalls are relevant, consult `learnings.consolidated.md` if present; use `learnings.md` only for needed history or as the available fallback. Otherwise skip both.

After applying it, if you encountered a pattern worth remembering, a mistake worth preventing, or a domain fact that surprised you, append one dated bullet to `learnings.md` via `agents-skills-feedback-loop/scripts/append_learning.py`. Do not modify `SKILL.md` itself.
