---
name: software-backend
description: Production-grade backend API development with Node.js 24 LTS/25 Current (Express 5.x/Fastify 5.2/NestJS 11.x/Hono 4.x), Bun 1.2+, Python 3.14+ (FastAPI 0.115+), Go 1.25+, Rust 1.92+ (Axum 0.8+), Prisma 6.x/Drizzle ORM, PostgreSQL 18. Includes tRPC for end-to-end type safety, edge computing (Cloudflare Workers/Vercel Edge), GraphQL, TypeScript 5.9+ strict mode, modern logging (Pino/Winston), secret managers, PM2 process management, and zero-trust security patterns.
---

# Backend Engineering Skill — Quick Reference

This skill equips backend engineers with execution-ready patterns for modern API development, database design, authentication, caching, observability, error handling, testing, and deployment. Apply these patterns when you need REST/GraphQL/tRPC API design, database schema modeling, authentication flows, performance optimization, edge deployment, or production-grade backend architectures.

**Modern Best Practices (January 2026)**: tRPC for end-to-end type safety, Hono/Elysia for edge-first APIs, Bun runtime for performance-critical workloads, zero-trust security (every request adversarial), OpenTelemetry as observability standard, TypeScript 5.9+ strict mode, [TypeScript 7 native preview (Project Corsa)](https://devblogs.microsoft.com/typescript/progress-on-typescript-7-december-2025/), vector databases for AI backends (Pinecone, Weaviate), and secure defaults (rate limiting, headers, input validation).

---

## Quick Reference

| Task | Tool/Framework | Command | When to Use |
|------|----------------|---------|-------------|
| REST API | Express 5.x / Fastify 5.2 / NestJS 11.x | `npm create express-app` | Traditional CRUD APIs, public APIs |
| Edge API | Hono 4.x / Elysia | `bun create hono` | Cloudflare Workers, Vercel Edge, serverless |
| Type-Safe API | tRPC 11.x | `npm install @trpc/server` | Full-stack TypeScript monorepos, no schema |
| GraphQL API | Apollo Server/Pothos | `npm install @apollo/server` | Flexible data fetching, avoiding over-fetching |
| Database ORM | Prisma 6.x / Drizzle | `npx prisma init` | Type-safe database access, migrations |
| Authentication | JWT/NextAuth.js/Passport | `npm install jsonwebtoken` | User sessions, API authentication |
| Validation | Zod/Joi | `npm install zod` | Runtime type validation at API boundaries |
| Caching | Redis/Upstash | `npm install ioredis` | Read-heavy operations, session storage |
| Background Jobs | BullMQ/Agenda | `npm install bullmq` | Email sending, async processing |
| Testing | Vitest/Jest/Supertest | `vitest run` | Unit, integration, E2E testing |
| Logging | Pino/Winston | `npm install pino` | Structured logging, observability |
| API Documentation | Swagger/OpenAPI | `@nestjs/swagger` | Auto-generated API docs |
| Vector Database | Pinecone/Weaviate | `npm install @pinecone-database/pinecone` | AI/ML backends, semantic search |

# When to Use This Skill

Use this skill when you need:

- REST or GraphQL API design and implementation (GraphQL adoption increasing)
- Database schema design and migrations (Prisma schema-first approach, Prisma Accelerate for serverless)
- Authentication and authorization patterns (JWT, OAuth2, sessions, NextAuth.js)
- Error handling and validation strategies (Zod/Joi TypeScript-first validation)
- API security best practices (Helmet.js headers, OWASP API Security Top 10, rate limiting)
- Performance optimization and caching (Redis, Prisma connection pooling, singleton pattern)
- Testing strategies (Vitest, Jest, Playwright for E2E, supertest for API testing)
- Background job processing (BullMQ, Agenda)
- API documentation and versioning (Swagger/OpenAPI auto-generation)
- Deployment and production readiness (PM2 process management, Docker, secret managers)
- Monitoring and observability (structured logging with Pino/Winston, Sentry, OpenTelemetry)

## Decision Tree: Backend Technology Selection

```text
Backend project needs: [API Type]
    ├─ REST API?
    │   ├─ Simple CRUD → Express 5.x + Prisma 6.x
    │   ├─ Enterprise features → NestJS 11.x (built-in DI, modules)
    │   ├─ High performance → Fastify 5.2 (faster than Express)
    │   └─ Edge/Serverless → Hono 4.x (Cloudflare Workers, Vercel Edge)
    │
    ├─ Type-Safe API? (NEW - 2026)
    │   ├─ Full-stack TypeScript monorepo → tRPC 11.x (no schema, no codegen)
    │   ├─ Public API with docs → REST + OpenAPI/Swagger
    │   └─ Flexible data fetching → GraphQL + Pothos/Apollo
    │
    ├─ GraphQL API?
    │   ├─ Code-first → Pothos GraphQL (TypeScript)
    │   └─ Schema-first → Apollo Server + GraphQL Codegen
    │
    ├─ Runtime Selection? (NEW - 2026)
    │   ├─ Enterprise stable → Node.js 24 LTS (battle-tested, largest ecosystem)
    │   ├─ Performance-critical → Bun 1.2+ (2-3x faster, native TypeScript)
    │   └─ Security-focused → Deno 2.x (secure by default, native TS)
    │
    ├─ Authentication Strategy?
    │   ├─ JWT tokens → jsonwebtoken + httpOnly cookies
    │   ├─ OAuth/Social → NextAuth.js or Passport.js
    │   └─ Magic links → Custom implementation + email service
    │
    ├─ Database Layer?
    │   ├─ Type-safe ORM → Prisma 6.x (DX-focused, migrations, studio)
    │   ├─ SQL-first/Performance → Drizzle ORM (lightweight, SQL-like API)
    │   ├─ Raw SQL → pg (PostgreSQL 18 driver)
    │   └─ Edge-compatible → Drizzle + D1/Turso/Neon
    │
    ├─ Caching Strategy?
    │   ├─ Distributed cache → Redis (multi-server)
    │   ├─ Serverless cache → Upstash Redis
    │   └─ In-memory cache → Node.js Map (single server)
    │
    ├─ Edge Deployment? (NEW - 2026)
    │   ├─ Global low-latency → Cloudflare Workers (<1ms cold start)
    │   ├─ Next.js integration → Vercel Edge Functions
    │   └─ AWS ecosystem → Lambda@Edge
    │
    └─ Background Jobs?
        ├─ Complex workflows → BullMQ (Redis-backed, retries)
        ├─ Serverless workflows → AWS Step Functions
        └─ Simple scheduling → node-cron or Agenda
```

**Runtime & Language Alternatives:**

- **Node.js 24 LTS / 25 Current** (Express 5.x / Fastify 5.2 / NestJS 11.x + Prisma 6.x): TypeScript-first, async/await, largest ecosystem, battle-tested
- **Bun 1.2+** (Hono / Elysia + Drizzle): 2-3.5x faster than Node.js, native TypeScript, built-in bundler/test runner, enterprise-ready (Anthropic acquisition)
- **Python 3.14+** (FastAPI 0.115+ + SQLAlchemy 2.0+): Data-heavy services, async support, evolving concurrency model, modern typing
- **Go 1.25+** (Fiber 2.x + GORM 1.25+): High concurrency, native performance, experimental encoding/json/v2
- **Rust 1.92+** (Axum 0.8+ + SeaORM 1.1+): Memory safety, zero-cost abstractions, Rust 2024 edition

See [assets/](assets/) for language-specific starter templates and [references/edge-deployment-guide.md](references/edge-deployment-guide.md) for edge computing patterns.

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

### Migration Rollback Strategies

| Strategy | Description | Use When |
|----------|-------------|----------|
| Backward-compatible | New code works with old schema | Zero-downtime deployments |
| Expand-contract | Add new, migrate, remove old | Schema changes |
| Shadow tables | Write to both during transition | High-risk migrations |

---

### Optional: AI/Automation Extensions

> **Note**: AI-assisted backend patterns. Skip if not using AI tooling.

#### AI-Assisted Code Generation

| Tool | Use Case |
|------|----------|
| GitHub Copilot | Inline suggestions, boilerplate |
| Cursor | AI-first IDE, context-aware |
| Claude Code | CLI-based development |

**Review requirements for AI-generated code:**

- All imports verified against package.json
- Type checker passes (strict mode)
- Security scan passes
- Tests cover generated code

---

## Infrastructure Economics & Business Impact

**Why this matters**: Backend decisions directly impact revenue. A 100ms latency increase can reduce conversions by 7%. A poorly chosen architecture can cost 10x more in cloud spend. Performance SLAs are revenue commitments.

### Cost Modeling Quick Reference

| Decision | Cost Impact | Revenue Impact |
|----------|-------------|----------------|
| Edge vs. Origin | 60-80% latency reduction | +2-5% conversion rate |
| Serverless vs. Containers | Variable cost, scales to zero | Better unit economics at low scale |
| Reserved vs. On-Demand | 30-60% cost savings | Predictable COGS |
| Connection pooling | 50-70% fewer DB connections | Lower database costs |
| Caching layer | 80-95% fewer origin requests | Reduced compute costs |

### Performance SLA → Revenue Mapping

```text
SLA Target → Business Metric

P50 latency < 100ms → Baseline user experience
P95 latency < 500ms → 95% users satisfied
P99 latency < 1000ms → Enterprise SLA compliance
Uptime 99.9% (43.8m downtime/month) → Standard SLA tier
Uptime 99.99% (4.4m downtime/month) → Enterprise tier ($$$)
```

### Infrastructure Cost Calculator (Quick Estimate)

```typescript
// Monthly cost estimation formula
const estimateMonthlyInfraCost = ({
  avgRPS,           // Average requests per second
  avgLatencyMs,     // Average response time
  dataTransferGB,   // Monthly data transfer
  storageGB,        // Database + file storage
  environment,      // 'serverless' | 'container' | 'vm'
}: InfraParams): CostEstimate => {
  const computeHours = (avgRPS * 3600 * 24 * 30 * avgLatencyMs) / 1000 / 3600;

  const rates = {
    serverless: { compute: 0.00001667, transfer: 0.09, storage: 0.023 },
    container: { compute: 0.0464, transfer: 0.09, storage: 0.10 },
    vm: { compute: 0.0416, transfer: 0.09, storage: 0.08 },
  };

  const r = rates[environment];
  return {
    compute: computeHours * r.compute,
    transfer: dataTransferGB * r.transfer,
    storage: storageGB * r.storage,
    total: computeHours * r.compute + dataTransferGB * r.transfer + storageGB * r.storage,
  };
};
```

### Unit Economics Checklist

Before deploying any backend service, calculate:

- [ ] **Cost per request**: Total infra cost / monthly requests
- [ ] **Cost per user**: Total infra cost / MAU
- [ ] **Gross margin impact**: How does infra cost affect product margin?
- [ ] **Scale economics**: At 10x traffic, does cost scale linearly or worse?
- [ ] **Break-even point**: At what traffic level does this architecture pay for itself?

### Architecture Decision → Business Impact

| Architecture Choice | Technical Benefit | Business Impact |
|---------------------|-------------------|-----------------|
| CDN + Edge caching | Lower latency | Higher conversion, better SEO |
| Read replicas | Scale reads | Handle traffic spikes without degradation |
| Queue-based processing | Decouple services | Smoother UX during high load |
| Multi-region deployment | Fault tolerance | Enterprise SLA compliance |
| Auto-scaling | Right-sized infra | Lower COGS, better margins |

### FinOps Practices for Backend Teams

1. **Tag all resources** - Every resource tagged with `team`, `service`, `environment`
2. **Set billing alerts** - Alert at 50%, 80%, 100% of budget
3. **Review weekly** - 15-minute weekly cost review meeting
4. **Right-size monthly** - Check CPU/memory utilization, downsize overprovisioned
5. **Spot/Preemptible for non-prod** - 60-90% savings on dev/staging

See [references/infrastructure-economics.md](references/infrastructure-economics.md) for detailed cost modeling, cloud provider comparisons, and ROI calculators.

---

## Navigation

**Resources**
- [references/backend-best-practices.md](references/backend-best-practices.md) — Node.js patterns for auth, error handling, database, performance, testing, observability
- [references/edge-deployment-guide.md](references/edge-deployment-guide.md) — Edge computing patterns, Cloudflare Workers vs Vercel Edge, tRPC, Hono, Bun
- [references/infrastructure-economics.md](references/infrastructure-economics.md) — Cost modeling, performance SLAs → revenue, FinOps practices, cloud optimization
- [references/go-best-practices.md](references/go-best-practices.md) — Go idioms, concurrency, error handling, GORM usage, testing, profiling
- [references/rust-best-practices.md](references/rust-best-practices.md) — Ownership, async, Axum, SeaORM, error handling, testing
- [references/python-best-practices.md](references/python-best-practices.md) — FastAPI, SQLAlchemy, async patterns, validation, testing, performance
- [README.md](README.md) — Folder overview and usage notes
- [data/sources.json](data/sources.json) — External references per language/runtime
- Shared checklists: [../software-clean-code-standard/assets/checklists/backend-api-review-checklist.md](../software-clean-code-standard/assets/checklists/backend-api-review-checklist.md), [../software-clean-code-standard/assets/checklists/secure-code-review-checklist.md](../software-clean-code-standard/assets/checklists/secure-code-review-checklist.md)

**Shared Utilities** (Centralized patterns — extract, don't duplicate)
- [../software-clean-code-standard/utilities/auth-utilities.md](../software-clean-code-standard/utilities/auth-utilities.md) — Argon2id, jose JWT, OAuth 2.1/PKCE
- [../software-clean-code-standard/utilities/error-handling.md](../software-clean-code-standard/utilities/error-handling.md) — Effect Result types, correlation IDs
- [../software-clean-code-standard/utilities/config-validation.md](../software-clean-code-standard/utilities/config-validation.md) — Zod 3.24+, Valibot, secrets management
- [../software-clean-code-standard/utilities/resilience-utilities.md](../software-clean-code-standard/utilities/resilience-utilities.md) — p-retry v6, opossum v8, OTel spans
- [../software-clean-code-standard/utilities/logging-utilities.md](../software-clean-code-standard/utilities/logging-utilities.md) — pino v9 + OpenTelemetry integration
- [../software-clean-code-standard/utilities/testing-utilities.md](../software-clean-code-standard/utilities/testing-utilities.md) — Vitest, MSW v2, factories, fixtures
- [../software-clean-code-standard/utilities/observability-utilities.md](../software-clean-code-standard/utilities/observability-utilities.md) — OpenTelemetry SDK, tracing, metrics
- [../software-clean-code-standard/references/clean-code-standard.md](../software-clean-code-standard/references/clean-code-standard.md) — Canonical clean code rules (`CC-*`) for citation

**Templates**
- [assets/nodejs/template-nodejs-prisma-postgres.md](assets/nodejs/template-nodejs-prisma-postgres.md) — Node.js + Prisma + PostgreSQL
- [assets/go/template-go-fiber-gorm.md](assets/go/template-go-fiber-gorm.md) — Go + Fiber + GORM + PostgreSQL
- [assets/rust/template-rust-axum-seaorm.md](assets/rust/template-rust-axum-seaorm.md) — Rust + Axum + SeaORM + PostgreSQL
- [assets/python/template-python-fastapi-sqlalchemy.md](assets/python/template-python-fastapi-sqlalchemy.md) — Python + FastAPI + SQLAlchemy + PostgreSQL

**Related Skills**
- [../software-architecture-design/SKILL.md](../software-architecture-design/SKILL.md) — System decomposition, SLAs, and data flows
- [../software-security-appsec/SKILL.md](../software-security-appsec/SKILL.md) — Authentication/authorization and secure API design
- [../ops-devops-platform/SKILL.md](../ops-devops-platform/SKILL.md) — CI/CD, infrastructure, and deployment safety
- [../qa-resilience/SKILL.md](../qa-resilience/SKILL.md) — Resilience, retries, and failure playbooks
- [../software-code-review/SKILL.md](../software-code-review/SKILL.md) — Review checklists and standards for backend changes
- [../qa-testing-strategy/SKILL.md](../qa-testing-strategy/SKILL.md) — Testing strategies, test pyramids, and coverage goals
- [../dev-api-design/SKILL.md](../dev-api-design/SKILL.md) — RESTful design, GraphQL, and API versioning patterns
- [../data-sql-optimization/SKILL.md](../data-sql-optimization/SKILL.md) — SQL optimization, indexing, and query tuning patterns

---

## Trend Awareness Protocol

**IMPORTANT**: When users ask recommendation questions about backend development, you MUST use WebSearch to check current trends before answering.

### Trigger Conditions

- "What's the best backend framework for [use case]?"
- "What should I use for [API design/auth/database]?"
- "What's the latest in Node.js/Go/Rust?"
- "Current best practices for [REST/GraphQL/tRPC]?"
- "Is [framework/runtime] still relevant in 2026?"
- "[Express] vs [Fastify] vs [Hono]?"
- "Best ORM for [database/use case]?"

### Required Searches

1. Search: `"backend development best practices 2026"`
2. Search: `"[Node.js/Go/Rust] frameworks 2026"`
3. Search: `"backend framework comparison 2026"`
4. Search: `"[specific framework/ORM] vs alternatives 2026"`

### What to Report

After searching, provide:

- **Current landscape**: What frameworks/runtimes are popular NOW
- **Emerging trends**: New patterns or tools gaining traction
- **Deprecated/declining**: Approaches that are losing relevance
- **Recommendation**: Based on fresh data and recent releases

### Example Topics (verify with fresh search)

- Node.js 24 LTS features
- Bun vs Deno vs Node.js
- Hono, Elysia, and edge-first frameworks
- Drizzle vs Prisma for TypeScript
- tRPC and end-to-end type safety
- Edge computing and serverless patterns

---

## Operational Playbooks
- [references/operational-playbook.md](references/operational-playbook.md) — Full backend architecture patterns, checklists, TypeScript notes, and decision tables
