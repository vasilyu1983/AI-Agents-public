# Edge Deployment Guide - Backend Engineering

March 2026 guidance for edge runtimes, serverless backends, and multi-runtime JavaScript services.

## Table of Contents

- [Core Rule](#core-rule)
- [Quick Selection](#quick-selection)
- [What Changed By March 2026](#what-changed-by-march-2026)
- [Platform Notes](#platform-notes)
- [Cloudflare Workers](#cloudflare-workers)
- [Vercel](#vercel)
- [Bun](#bun)
- [Deno](#deno)
- [Framework Picks](#framework-picks)
- [Hono](#hono)
- [Elysia](#elysia)
- [Database Guidance At The Edge](#database-guidance-at-the-edge)
- [Observability At The Edge](#observability-at-the-edge)
- [Migration Guidance](#migration-guidance)
- [Node To Edge](#node-to-edge)
- [Prisma To Drizzle For Edge-First TypeScript](#prisma-to-drizzle-for-edge-first-typescript)
- [Volatile Facts Protocol](#volatile-facts-protocol)
- [Primary Sources](#primary-sources)

## Core Rule

Edge is a deployment constraint, not a badge.

Use edge runtimes only when the workload is:

- latency-sensitive across regions
- stateless or near-stateless
- light on CPU and memory
- tolerant of platform-specific runtime limits

If the workload is database-heavy, queue-heavy, or dependency-heavy, prefer a regular server runtime first.

## Quick Selection

| Constraint | Default Pick | Why |
|-----------|--------------|-----|
| Global request routing, auth checks, lightweight middleware | Cloudflare Workers + Hono | Strong edge ergonomics and mature docs |
| Next.js app on Vercel | Vercel Node.js runtime by default | Broader compatibility and current platform direction |
| Bun-specific app or local DX focus | Bun + Hono/Elysia | Fast startup and cohesive TS tooling |
| Security-focused JS runtime with permissions model | Deno | Web-standard APIs and explicit permissions |
| Stateful APIs, complex DB access, heavy libraries | Node.js server runtime | Fewer surprises and better library compatibility |

## What Changed By March 2026

- Vercel should not be modeled as "Edge Functions first". Use the Vercel Node.js runtime by default and choose edge only when the request path is explicitly edge-worthy.
- Cloudflare Workers now supports WebSockets and a virtual `node:fs` API, so old guidance saying "no native WebSockets" or "no Node.js APIs" is outdated.
- Avoid fixed claims about cold starts, POP counts, or free-tier quotas unless you verify them from the platform docs at answer time.

## Platform Notes

### Cloudflare Workers

Use Workers for:

- auth/session checks close to users
- request rewriting, bot filtering, feature flags
- lightweight APIs with KV, D1, Durable Objects, R2, or external HTTP backends

Current guidance:

- WebSockets are supported.
- Some Node compatibility exists, including a virtual `node:fs`; do not treat Workers like a full Node process.
- Keep CPU-heavy logic, large native dependencies, and driver-specific database code out of the hot path.

```typescript
import { Hono } from 'hono'

const app = new Hono()

app.get('/api/health', (c) => c.json({ status: 'ok' }))

app.get('/api/session', async (c) => {
  const token = c.req.header('authorization')
  if (!token) return c.json({ authenticated: false }, 401)

  // Keep edge handlers small and dependency-light.
  const session = await verifySession(token)
  return c.json({ authenticated: true, session })
})

export default app
```

### Vercel

Use Vercel Node.js runtime for:

- Next.js route handlers with normal backend dependencies
- Prisma/Drizzle/database-backed APIs
- queues, background work coordination, and most business logic

Use Vercel edge runtime only for:

- request personalization close to users
- auth gating and redirects
- tiny middleware-style handlers

```typescript
// app/api/health/route.ts
export async function GET() {
  return Response.json({ status: 'ok' })
}
```

### Bun

Use Bun for:

- greenfield TypeScript services
- teams that want one runtime, package manager, and test runner
- services with simple dependency graphs and measured runtime wins

Avoid Bun-first decisions when:

- you depend on broad Node compatibility
- the org needs conservative operational baselines
- you are betting on native add-ons or opaque third-party SDKs

### Deno

Use Deno when:

- explicit runtime permissions are part of the design
- the team prefers web-standard APIs
- the deployment target matches Deno well

Do not assume every package or host behaves like Node. Verify platform support before committing.

## Framework Picks

### Hono

Default edge-first framework.

Use when:

- you need one handler model across Cloudflare, Bun, Deno, and Node
- you want small handlers and composable middleware

```typescript
import { Hono } from 'hono'
import { cors } from 'hono/cors'

const app = new Hono()
app.use('*', cors())
app.get('/api/health', (c) => c.json({ status: 'ok' }))

export default app
```

### Elysia

Use when:

- Bun is the deliberate runtime choice
- you want Bun-native ergonomics and schema-driven handlers

```typescript
import { Elysia, t } from 'elysia'

new Elysia()
  .get('/api/health', () => ({ status: 'ok' }))
  .post('/api/users', ({ body }) => body, {
    body: t.Object({
      email: t.String({ format: 'email' }),
      name: t.String({ minLength: 2 }),
    }),
  })
  .listen(3000)
```

## Database Guidance At The Edge

Prefer:

- HTTP-native database access patterns
- Drizzle or explicit SQL for TypeScript edge apps
- provider-supported pooling/proxy layers

Avoid:

- opening many direct Postgres connections from highly elastic edge functions
- assuming your ORM behaves the same across Node, Bun, and Workers

Decision rule:

```text
Need simple edge reads/writes?
  ├─ Provider offers HTTP driver / serverless proxy -> acceptable
  ├─ Need complex transactions or long-lived connections -> move to Node/server runtime
  └─ Need auditable SQL with low abstraction -> Drizzle or explicit SQL
```

## Observability At The Edge

- Propagate request IDs from the first hop.
- Emit structured logs, but keep payloads small.
- Use OpenTelemetry where the platform and runtime integration is mature.
- Distinguish edge execution time from origin/database time in traces.

## Migration Guidance

### Node To Edge

Move only:

- auth checks
- redirects and rewrites
- lightweight read-mostly endpoints

Keep in Node/server runtime:

- file-heavy code
- database-heavy transactions
- CPU-heavy transforms
- jobs and long-running workflows

### Prisma To Drizzle For Edge-First TypeScript

Consider this migration when:

- the app is becoming edge-first
- SQL control matters more than schema-DSL convenience
- you need thinner runtime overhead

Basic path:

1. Freeze schema changes.
2. Model the existing schema in Drizzle.
3. Move one route or repository at a time.
4. Keep migrations SQL-first and test query parity.

## Volatile Facts Protocol

Before asserting runtime limits, pricing, quotas, POP counts, or current platform defaults:

1. Check `data/sources.json`.
2. Open the official platform docs.
3. Report the recommendation with a date if the fact is volatile.

## Primary Sources

- Cloudflare Workers: https://developers.cloudflare.com/workers/
- Cloudflare WebSockets: https://developers.cloudflare.com/workers/runtime-apis/websockets/
- Cloudflare `node:fs`: https://developers.cloudflare.com/workers/runtime-apis/nodejs/fs/
- Vercel runtimes: https://vercel.com/docs/functions/runtimes
- Vercel edge runtime: https://vercel.com/docs/functions/runtimes/edge
- Bun docs: https://bun.sh/docs
- Deno docs: https://docs.deno.com/
