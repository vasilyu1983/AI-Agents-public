---
name: software-backend
description: Production-grade backend APIs for Node.js, Python, Go, Rust, and C# with PostgreSQL. Use when building REST/GraphQL/tRPC services or auth.
---

# Software Backend Engineering

Use this skill to design, implement, and review production-grade backend services: API boundaries, data layer, auth, caching, observability, error handling, testing, and deployment.

Defaults to bias toward: type-safe boundaries (validation at the edge), OpenTelemetry for observability, zero-trust assumptions, idempotency for retries, RFC 9457 errors, Postgres + pooling, structured logs, timeouts, and rate limiting.

**Scaffolding rule**: When scaffolding a new project, show full working implementations for all domain logic — fraud rules, audit logging, webhook handlers, validation pipelines, background jobs. Don't just reference file names or stub functions; show the actual code so the user can run it immediately.

---

## Quick Reference

| Task | Default Picks | Notes |
|------|---------------|-------|
| REST API | Fastify / Express / NestJS | Prefer typed boundaries + explicit timeouts |
| Edge API | Hono / platform-native handlers | Keep work stateless, CPU-light |
| Type-Safe API | tRPC | Prefer for TS monorepos and internal APIs |
| GraphQL API | Apollo Server / Pothos | Prefer for complex client-driven queries |
| Database | PostgreSQL | Use pooling + migrations + query budgets |
| ORM / Query Layer | Prisma / Drizzle / SQLAlchemy / GORM / SeaORM / EF Core | Prefer explicit transactions |
| Authentication | OIDC/OAuth + sessions/JWT | Prefer httpOnly cookies for browsers |
| Validation | Zod / Pydantic / validator libs | Validate at the boundary, not deep inside |
| Caching | Redis (or managed) | Use TTLs + invalidation strategy |
| Background Jobs | BullMQ / platform queues | Make jobs idempotent + retry-safe |
| Testing | Unit + integration + contract/E2E | Keep most tests below the UI layer |
| Observability | Structured logs + OpenTelemetry | Correlation IDs end-to-end |

## Scope

Use this skill to:

- Design and implement REST/GraphQL/tRPC APIs
- Model data schemas and run safe migrations
- Implement authentication/authorization (OIDC/OAuth, sessions/JWT)
- Add validation, error handling, rate limiting, caching, and background jobs
- Ship production readiness (timeouts, observability, deploy/runbooks)

## When NOT to Use This Skill

Use a different skill when:

- **Frontend-only concerns** -> See [software-frontend](../software-frontend/SKILL.md)
- **Infrastructure provisioning (Terraform, K8s manifests)** -> See [ops-devops-platform](../ops-devops-platform/SKILL.md)
- **API design patterns only (no implementation)** -> See [dev-api-design](../dev-api-design/SKILL.md)
- **SQL query optimization and indexing** -> See [data-sql-optimization](../data-sql-optimization/SKILL.md)
- **Security audits and threat modeling** -> See [software-security-appsec](../software-security-appsec/SKILL.md)
- **System architecture (beyond single service)** -> See [software-architecture-design](../software-architecture-design/SKILL.md)

## Technology Selection

Pick based on the strongest constraint, not feature lists:

| Constraint | Default Pick | Why |
|-----------|-------------|-----|
| Team knows TypeScript only | Fastify/Hono + Prisma/Drizzle | Ecosystem depth, hiring ease |
| Need <50ms P95, CPU-bound work | Go (net/http + sqlc/pgx) | Goroutines isolate CPU work; no event-loop risk |
| Data-heavy / ML integration | Python (FastAPI + SQLAlchemy) | Best ecosystem for numpy/pandas/ML pipelines |
| Memory-safety critical | Rust (Axum + SeaORM/SQLx) | Zero-cost abstractions, no GC |
| Enterprise/.NET team | C# (ASP.NET Core + EF Core) | Azure integration, mature tooling |
| Edge/serverless | Hono / platform-native handlers | Stateless, CPU-light, fast cold starts |
| Fintech/audit-sensitive | Go + sqlc (or raw SQL) | ORM magic is a liability; you need auditable SQL |

For detailed framework/ORM/auth/caching selection trees, see [references/edge-deployment-guide.md](references/edge-deployment-guide.md) and language-specific references.
See [assets/](assets/) for starter templates per language.

---

## API Design Patterns (Dec 2025)

### Idempotency Patterns

All mutating operations MUST support idempotency for retry safety.

**Implementation:**

```typescript
// Idempotency key header
const idempotencyKey = request.headers['idempotency-key'];
const cached = await redis.get(`idem:${idempotencyKey}`);
if (cached) return JSON.parse(cached);

const result = await processOperation();
await redis.set(`idem:${idempotencyKey}`, JSON.stringify(result), 'EX', 86400);
return result;
```

| Do | Avoid |
|----|-------|
| Store idempotency keys with TTL (24h typical) | Processing duplicate requests |
| Return cached response for duplicate keys | Different responses for same key |
| Use client-generated UUIDs | Server-generated keys |

### Pagination Patterns

| Pattern | Use When | Example |
|---------|----------|---------|
| Cursor-based | Large datasets, real-time data | `?cursor=abc123&limit=20` |
| Offset-based | Small datasets, random access | `?page=3&per_page=20` |
| Keyset | Sorted data, high performance | `?after_id=1000&limit=20` |

**Prefer cursor-based pagination** for APIs with frequent inserts.

### Error Response Standard (Problem Details)

Use a consistent machine-readable error format (RFC 9457 Problem Details): https://www.rfc-editor.org/rfc/rfc9457

```json
{
  "type": "https://example.com/problems/invalid-request",
  "title": "Invalid request",
  "status": 400,
  "detail": "email is required",
  "instance": "/v1/users"
}
```

### Health Check Patterns

```typescript
// Liveness: Is the process running?
app.get('/health/live', (req, res) => {
  res.status(200).json({ status: 'ok' });
});

// Readiness: Can the service handle traffic?
app.get('/health/ready', async (req, res) => {
  const dbOk = await checkDatabase();
  const cacheOk = await checkRedis();
  if (dbOk && cacheOk) {
    res.status(200).json({ status: 'ready', db: 'ok', cache: 'ok' });
  } else {
    res.status(503).json({ status: 'not ready', db: dbOk, cache: cacheOk });
  }
});
```

### Common Mistakes (Non-Obvious)

| Avoid | Instead | Why |
|-------|---------|-----|
| N+1 queries | `include`/`select` or DataLoader | 10-100x perf hit; easy to miss in ORM code |
| No request timeouts | Timeouts on HTTP clients, DB, handlers | Hung deps cascade; see Production Hardening below |
| Missing connection pooling | Prisma pool / PgBouncer / pgx pool | Exhaustion under load on shared DB tiers |
| Catching errors silently | Log + rethrow or handle explicitly | Hidden failures, impossible to debug |

---

## Production Hardening: Patterns Models Skip

These are the patterns that separate "works in dev" from "survives production." Models tend to skip them unless explicitly prompted — add them to every service.

### Request & Query Timeouts

Every outbound call needs a timeout. Without one, a hung dependency leaks connections and cascades failures.

```typescript
// HTTP client timeout
const response = await fetch(url, { signal: AbortSignal.timeout(5000) });

// Database query timeout (Prisma)
await prisma.$queryRaw`SET statement_timeout = '3000'`;

// Express/Fastify request timeout
server.register(import('@fastify/timeout'), { timeout: 30000 });
```

| Layer | Default Timeout | Rationale |
|-------|----------------|-----------|
| HTTP client calls | 5s | External APIs shouldn't block you |
| Database queries | 3s | Slow queries = missing index or bad plan |
| Request handler | 30s | Safety net for the whole request lifecycle |
| Background jobs | 5min | Jobs that run longer need chunking |

### Field-Level Selection (Don't `SELECT *`)

ORMs default to fetching all columns. On wide tables this wastes bandwidth and hides performance problems.

```typescript
// BAD: fetches all 30 columns
const users = await prisma.user.findMany({ include: { posts: true } });

// GOOD: fetch only what the endpoint needs
const users = await prisma.user.findMany({
  select: { id: true, name: true, email: true },
  include: { posts: { select: { id: true, title: true } } }
});
```

For Go (sqlc): write explicit column lists in SQL queries — sqlc enforces this naturally.
For Python (SQLAlchemy): use `load_only()` or explicit column selection.

### Structured Error Responses (RFC 9457)

Return machine-readable errors from day one. Clients shouldn't have to regex-parse error messages.

```json
{
  "type": "https://api.example.com/problems/validation-error",
  "title": "Validation failed",
  "status": 422,
  "detail": "email must be a valid email address",
  "instance": "/v1/users",
  "errors": [{ "field": "email", "message": "invalid format" }]
}
```

Set `Content-Type: application/problem+json`. This format is a standard (RFC 9457) and parseable by any HTTP client.

### Query Plan Verification

Before shipping any new query to production, verify its execution plan:

```sql
EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT)
SELECT ... FROM ... WHERE ...;
```

Red flags in the output: `Seq Scan` on large tables, `Nested Loop` with high row estimates, `Sort` without index. Add indexes or rewrite the query before deploying.

---

## Performance Debugging Workflow

When a service is slow, work through these layers in order. Fix the cheapest layer first — don't add caching before fixing N+1 queries.

| Step | What to Check | Fix |
|------|--------------|-----|
| 1. Query analysis | Enable query logging, find N+1s and slow queries | Rewrite with `include`/joins, add `select` for field-level optimization |
| 2. Indexing | Run `EXPLAIN ANALYZE` on slow queries | Add composite indexes matching WHERE + ORDER BY patterns |
| 3. Connection pooling | Check connection count vs. pool size | Configure pool limits (Prisma `connection_limit`, PgBouncer, pgx pool) |
| 4. Caching | Identify read-heavy, rarely-changing data | Add Redis/in-memory cache with TTL + invalidation strategy |
| 5. Timeouts | Check for missing timeouts on DB, HTTP, handlers | Add timeouts at every layer (see Production Hardening above) |
| 6. Platform tuning | Shared DB limits, cold starts, memory | Upgrade tier, add read replicas, tune runtime settings |

**Key principle**: always measure before and after. Use structured logging with request IDs to trace specific slow requests end-to-end.

---

## Infrastructure Economics

Backend architecture decisions directly impact cost and revenue. See [references/infrastructure-economics.md](references/infrastructure-economics.md) for detailed cost modeling, SLA-to-revenue mapping, unit economics checklists, and FinOps practices.

---

## Navigation

**Resources**
- [references/backend-best-practices.md](references/backend-best-practices.md) - Template authoring guide, quality checklist, and shared utilities pointers
- [references/edge-deployment-guide.md](references/edge-deployment-guide.md) - Edge computing patterns, Cloudflare Workers vs Vercel Edge, tRPC, Hono, Bun
- [references/infrastructure-economics.md](references/infrastructure-economics.md) - Cost modeling, performance SLAs -> revenue, FinOps practices, cloud optimization
- [references/go-best-practices.md](references/go-best-practices.md) - Go idioms, concurrency, error handling, GORM usage, testing, profiling
- [references/rust-best-practices.md](references/rust-best-practices.md) - Ownership, async, Axum, SeaORM, error handling, testing
- [references/python-best-practices.md](references/python-best-practices.md) - FastAPI, SQLAlchemy, async patterns, validation, testing, performance
- [references/nodejs-best-practices.md](references/nodejs-best-practices.md) - Event loop, async patterns, Express/Fastify/NestJS/Hono, error handling, memory management, security, profiling
- [references/csharp-best-practices.md](references/csharp-best-practices.md) - C# 14 / .NET 10 LTS, extension members, field keyword, ASP.NET Core 10 (validation, SSE, OpenAPI 3.1), EF Core 10 (LeftJoin, named filters), HybridCache, Polly v8 resilience
- [references/database-patterns.md](references/database-patterns.md) - PostgreSQL patterns (JSONB, CTEs, partitioning), connection pooling, migration strategies, ORM comparison, index design
- [references/message-queues-background-jobs.md](references/message-queues-background-jobs.md) - BullMQ patterns, broker comparison (Redis/SQS/Kafka/RabbitMQ), idempotent jobs, DLQ, scheduling, delivery guarantees
- [data/sources.json](data/sources.json) - External references per language/runtime
- Shared checklists: [../software-clean-code-standard/assets/checklists/backend-api-review-checklist.md](../software-clean-code-standard/assets/checklists/backend-api-review-checklist.md), [../software-clean-code-standard/assets/checklists/secure-code-review-checklist.md](../software-clean-code-standard/assets/checklists/secure-code-review-checklist.md)

**Shared Utilities** (Centralized patterns - extract, don't duplicate)
- [../software-clean-code-standard/utilities/auth-utilities.md](../software-clean-code-standard/utilities/auth-utilities.md) - Argon2id, jose JWT, OAuth 2.1/PKCE
- [../software-clean-code-standard/utilities/error-handling.md](../software-clean-code-standard/utilities/error-handling.md) - Effect Result types, correlation IDs
- [../software-clean-code-standard/utilities/config-validation.md](../software-clean-code-standard/utilities/config-validation.md) - Zod 3.24+, Valibot, secrets management
- [../software-clean-code-standard/utilities/resilience-utilities.md](../software-clean-code-standard/utilities/resilience-utilities.md) - p-retry v6, opossum v8, OTel spans
- [../software-clean-code-standard/utilities/logging-utilities.md](../software-clean-code-standard/utilities/logging-utilities.md) - pino v9 + OpenTelemetry integration
- [../software-clean-code-standard/utilities/testing-utilities.md](../software-clean-code-standard/utilities/testing-utilities.md) - Vitest, MSW v2, factories, fixtures
- [../software-clean-code-standard/utilities/observability-utilities.md](../software-clean-code-standard/utilities/observability-utilities.md) - OpenTelemetry SDK, tracing, metrics
- [../software-clean-code-standard/references/clean-code-standard.md](../software-clean-code-standard/references/clean-code-standard.md) - Canonical clean code rules (`CC-*`) for citation

**Templates**
- [assets/nodejs/template-nodejs-prisma-postgres.md](assets/nodejs/template-nodejs-prisma-postgres.md) - Node.js + Prisma + PostgreSQL
- [assets/go/template-go-fiber-gorm.md](assets/go/template-go-fiber-gorm.md) - Go + Fiber + GORM + PostgreSQL
- [assets/rust/template-rust-axum-seaorm.md](assets/rust/template-rust-axum-seaorm.md) - Rust + Axum + SeaORM + PostgreSQL
- [assets/python/template-python-fastapi-sqlalchemy.md](assets/python/template-python-fastapi-sqlalchemy.md) - Python + FastAPI + SQLAlchemy + PostgreSQL
- [assets/csharp/template-csharp-aspnet-efcore.md](assets/csharp/template-csharp-aspnet-efcore.md) - C# + ASP.NET Core + Entity Framework Core + PostgreSQL

**Related Skills**
- [../software-architecture-design/SKILL.md](../software-architecture-design/SKILL.md) - System decomposition, SLAs, and data flows
- [../software-security-appsec/SKILL.md](../software-security-appsec/SKILL.md) - Authentication/authorization and secure API design
- [../ops-devops-platform/SKILL.md](../ops-devops-platform/SKILL.md) - CI/CD, infrastructure, and deployment safety
- [../qa-resilience/SKILL.md](../qa-resilience/SKILL.md) - Resilience, retries, and failure playbooks
- [../software-code-review/SKILL.md](../software-code-review/SKILL.md) - Review checklists and standards for backend changes
- [../qa-testing-strategy/SKILL.md](../qa-testing-strategy/SKILL.md) - Testing strategies, test pyramids, and coverage goals
- [../dev-api-design/SKILL.md](../dev-api-design/SKILL.md) - RESTful design, GraphQL, and API versioning patterns
- [../data-sql-optimization/SKILL.md](../data-sql-optimization/SKILL.md) - SQL optimization, indexing, and query tuning patterns

---

## Freshness Protocol

When users ask version-sensitive recommendation questions, do a quick freshness check before asserting "best" choices or quoting versions.

### Trigger Conditions

- "What's the best backend framework for [use case]?"
- "What should I use for [API design/auth/database]?"
- "What's the latest in Node.js/Go/Rust?"
- "Current best practices for [REST/GraphQL/tRPC]?"
- "Is [framework/runtime] still relevant in 2026?"
- "[Express] vs [Fastify] vs [Hono]?"
- "Best ORM for [database/use case]?"

### How to Freshness-Check

1. Start from `data/sources.json` (official docs, release notes, support policies).
2. Run a targeted web search for the specific component and open release notes/support policy pages.
3. Prefer official sources over blogs for versions and support windows.

### What to Report

- **Current landscape**: what is stable and widely used now
- **Emerging trends**: what is gaining traction (and why)
- **Deprecated/declining**: what is falling out of favor (and why)
- **Recommendation**: default choice + 1-2 alternatives, with trade-offs

### Example Topics (verify with fresh search)

- Node.js LTS support window and major changes
- Bun vs Deno vs Node.js
- Hono, Elysia, and edge-first frameworks
- Drizzle vs Prisma for TypeScript
- tRPC and end-to-end type safety
- Edge computing and serverless patterns
- .NET 10 LTS (Nov 2025) and C# 14 adoption
- ASP.NET Core 10 built-in validation vs FluentValidation
- EF Core 10 vs Dapper for C# data access
- HybridCache vs manual IMemoryCache + IDistributedCache

---

## Operational Playbooks
- [references/operational-playbook.md](references/operational-playbook.md) - Full backend architecture patterns, checklists, TypeScript notes, and decision tables

## Fact-Checking

- Use web search/web fetch to verify current external facts, versions, pricing, deadlines, regulations, or platform behavior before final answers.
- Prefer primary sources; report source links and dates for volatile information.
- If web access is unavailable, state the limitation and mark guidance as unverified.
