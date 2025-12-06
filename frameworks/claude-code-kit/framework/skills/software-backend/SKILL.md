---
name: software-backend
description: Production-grade backend API development with Node.js 24 LTS/25 Current (Express/Fastify/NestJS), Python 3.14+ (FastAPI), Go 1.25+, Rust 1.91+ (Axum), Prisma ORM, PostgreSQL 18. Includes GraphQL, TypeScript 5.9+ strict mode, modern logging (Pino/Winston), secret managers, PM2 process management, and Prisma Accelerate for serverless/edge deployments.
---

# Backend Engineering Skill — Quick Reference

This skill equips backend engineers with execution-ready patterns for modern API development, database design, authentication, caching, observability, error handling, testing, and deployment. Claude should apply these patterns when users ask for REST/GraphQL API design, database schema modeling, authentication flows, performance optimization, or production-grade backend architectures.

**Modern Best Practices (December 2025)**: GraphQL adoption, TypeScript 5.9+ strict mode enforcement (TypeScript 7 "Corsa" Go-based compiler in preview with 10x speedup), `unknown` over `any`, Prisma Accelerate for serverless, PM2 process management, structured logging (Pino/Winston), secret managers (AWS Secrets Manager, HashiCorp Vault), and enhanced security with Helmet.js.

---

## Quick Reference

| Task | Tool/Framework | Command | When to Use |
|------|----------------|---------|-------------|
| REST API | Express/Fastify/NestJS | `npm create express-app` | Traditional CRUD APIs, public APIs |
| GraphQL API | Apollo Server/Pothos | `npm install @apollo/server` | Flexible data fetching, avoiding over-fetching |
| Database ORM | Prisma/Drizzle | `npx prisma init` | Type-safe database access, migrations |
| Authentication | JWT/NextAuth.js/Passport | `npm install jsonwebtoken` | User sessions, API authentication |
| Validation | Zod/Joi | `npm install zod` | Runtime type validation at API boundaries |
| Caching | Redis/Upstash | `npm install ioredis` | Read-heavy operations, session storage |
| Background Jobs | BullMQ/Agenda | `npm install bullmq` | Email sending, async processing |
| Testing | Vitest/Jest/Supertest | `vitest run` | Unit, integration, E2E testing |
| Logging | Pino/Winston | `npm install pino` | Structured logging, observability |
| API Documentation | Swagger/OpenAPI | `@nestjs/swagger` | Auto-generated API docs |

# When to Use This Skill

Claude should invoke this skill when a user requests:

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
    │   ├─ Simple CRUD → Express + Prisma
    │   ├─ Enterprise features → NestJS (built-in DI, modules)
    │   └─ High performance → Fastify (faster than Express)
    │
    ├─ GraphQL API?
    │   ├─ Code-first → Pothos GraphQL (TypeScript)
    │   └─ Schema-first → Apollo Server + GraphQL Codegen
    │
    ├─ Authentication Strategy?
    │   ├─ JWT tokens → jsonwebtoken + httpOnly cookies
    │   ├─ OAuth/Social → NextAuth.js or Passport.js
    │   └─ Magic links → Custom implementation + email service
    │
    ├─ Database Layer?
    │   ├─ Type-safe ORM → Prisma (best for TypeScript)
    │   ├─ SQL-first → Drizzle ORM or Kysely
    │   └─ Raw SQL → pg (PostgreSQL driver)
    │
    ├─ Caching Strategy?
    │   ├─ Distributed cache → Redis (multi-server)
    │   ├─ Serverless cache → Upstash Redis
    │   └─ In-memory cache → Node.js Map (single server)
    │
    └─ Background Jobs?
        ├─ Complex workflows → BullMQ (Redis-backed, retries)
        └─ Simple scheduling → node-cron or Agenda
```

**Language Alternatives:**

- **Node.js 24 LTS / 25 Current** (Express/Fastify/NestJS + Prisma): TypeScript-first, async/await, Web Storage API
- **Python 3.14+** (FastAPI + SQLAlchemy): ML/DS backends, async support, free-threaded Python, t-strings
- **Go 1.25+** (Fiber + GORM): High concurrency, native performance, experimental encoding/json/v2
- **Rust 1.91+** (Axum + SeaORM): Memory safety, zero-cost abstractions, Rust 2024 edition

See [templates/](templates/) for language-specific starter templates.

---

## Navigation

**Resources**
- [resources/backend-best-practices.md](resources/backend-best-practices.md) — Node.js patterns for auth, error handling, database, performance, testing, observability
- [resources/go-best-practices.md](resources/go-best-practices.md) — Go idioms, concurrency, error handling, GORM usage, testing, profiling
- [resources/rust-best-practices.md](resources/rust-best-practices.md) — Ownership, async, Axum, SeaORM, error handling, testing
- [resources/python-best-practices.md](resources/python-best-practices.md) — FastAPI, SQLAlchemy, async patterns, validation, testing, performance
- [README.md](README.md) — Folder overview and usage notes
- [data/sources.json](data/sources.json) — External references per language/runtime

**Templates**
- [templates/nodejs/template-nodejs-prisma-postgres.md](templates/nodejs/template-nodejs-prisma-postgres.md) — Node.js + Prisma + PostgreSQL
- [templates/go/template-go-fiber-gorm.md](templates/go/template-go-fiber-gorm.md) — Go + Fiber + GORM + PostgreSQL
- [templates/rust/template-rust-axum-seaorm.md](templates/rust/template-rust-axum-seaorm.md) — Rust + Axum + SeaORM + PostgreSQL
- [templates/python/template-python-fastapi-sqlalchemy.md](templates/python/template-python-fastapi-sqlalchemy.md) — Python + FastAPI + SQLAlchemy + PostgreSQL

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

## Operational Playbooks
- [resources/operational-playbook.md](resources/operational-playbook.md) — Full backend architecture patterns, checklists, TypeScript notes, and decision tables
