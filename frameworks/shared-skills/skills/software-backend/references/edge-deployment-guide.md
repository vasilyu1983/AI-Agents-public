# Edge Deployment Guide - Backend Engineering

Patterns for edge computing, serverless backends, and modern JavaScript runtimes.

## Contents

- [When to Use Edge Computing](#when-to-use-edge-computing)
- [Platform Decision Matrix](#platform-decision-matrix)
- [Runtime Comparison (Verify Versions)](#runtime-comparison-verify-versions)
- [Edge-First Frameworks](#edge-first-frameworks)
- [tRPC: End-to-End Type Safety](#trpc-end-to-end-type-safety)
- [Edge-Compatible Databases](#edge-compatible-databases)
- [Zero-Trust Security Patterns](#zero-trust-security-patterns)
- [Observability at Edge](#observability-at-edge)
- [Migration Strategies](#migration-strategies)
- [Related Resources](#related-resources)

---

## When to Use Edge Computing

| Use Case | Edge | Traditional Server |
|----------|------|-------------------|
| Global low-latency APIs | Yes | No |
| Authentication/JWT validation | Yes | Yes |
| A/B testing, feature flags | Yes | Yes |
| Database-heavy CRUD | No | Yes |
| Long-running processes | No | Yes |
| WebSocket connections | Limited | Yes |

**Rule of thumb**: Edge is ideal for stateless, CPU-light operations close to users.

---

## Platform Decision Matrix

| Platform | Cold Start | Global Locations | Best For |
|----------|------------|------------------|----------|
| **Cloudflare Workers** | <1ms (V8 isolates) | 300+ | Pure edge logic, APIs |
| **Vercel Edge Functions** | ~50ms | 20+ | Next.js integration |
| **AWS Lambda@Edge** | ~100ms | CloudFront POPs | AWS ecosystem |
| **Deno Deploy** | <10ms | 35+ | Deno/Fresh apps |
| **Fly.io** | ~50ms | 30+ | Containers at edge |

### Cloudflare Workers

**Strengths**: Fastest cold starts, largest network, generous free tier (100k requests/day).

```typescript
// Hono on Cloudflare Workers
import { Hono } from 'hono'

const app = new Hono()

app.get('/api/user/:id', async (c) => {
  const id = c.req.param('id')
  // Use Cloudflare KV or D1 for data
  const user = await c.env.USERS_KV.get(id, 'json')
  return c.json(user)
})

export default app
```

**Limitations**: No Node.js APIs, 128MB memory, 30s CPU time (paid), no native WebSockets.

### Vercel Edge Functions

**Strengths**: Seamless Next.js integration, familiar DX, automatic ISR.

```typescript
// Next.js Edge API Route
export const config = { runtime: 'edge' }

export default function handler(req: Request) {
  return new Response(JSON.stringify({ message: 'Hello from edge' }), {
    headers: { 'content-type': 'application/json' },
  })
}
```

**Limitations**: Higher latency than Workers, usage-based pricing can escalate.

---

## Runtime Comparison (Verify Versions)

| Runtime | TypeScript | Package Manager | Best For |
|---------|------------|-----------------|----------|
| **Node.js (current LTS)** | Via transpile/runtime loaders | npm/pnpm/yarn | Production stability, broad ecosystem |
| **Bun** | Native | bun | Perf-sensitive services (verify constraints) |
| **Deno** | Native | deno add | Security-focused deployments (verify platform support) |

### Bun Quick Start

```bash
# Install Bun
curl -fsSL https://bun.sh/install | bash

# Create Hono project
bun create hono my-app
cd my-app
bun run dev

# Run tests
bun test

# Bundle for production
bun build ./src/index.ts --outdir ./dist --target bun
```

### When to Choose Bun

- Greenfield projects with performance requirements
- Serverless functions (often lower cold starts)
- Development tooling (instant installs, fast tests)
- Full-stack TypeScript with Elysia/Hono

### When to Stay with Node.js

- Large existing codebases
- Enterprise requirements with compliance audits
- Dependencies with native Node.js bindings
- Need for maximum ecosystem compatibility

### Runtime Sandboxing (Prefer Platform Controls)

Prefer OS/container sandboxing (containers, seccomp, gVisor, Firecracker) for untrusted workloads. If your runtime offers a permissions model, follow its official docs and verify flag stability before relying on it in production.

---

## Edge-First Frameworks

### Hono 4.x

**Best for**: Cloudflare Workers, multi-runtime deployment.

```typescript
import { Hono } from 'hono'
import { cors } from 'hono/cors'
import { jwt } from 'hono/jwt'

const app = new Hono()

// Middleware
app.use('*', cors())
app.use('/api/*', jwt({ secret: 'your-secret' }))

// Routes
app.get('/api/health', (c) => c.json({ status: 'ok' }))

app.post('/api/users', async (c) => {
  const body = await c.req.json()
  // Validate with Zod
  const user = userSchema.parse(body)
  return c.json(user, 201)
})

export default app
```

### Elysia (Bun-native)

**Best for**: Maximum performance on Bun, end-to-end type safety.

```typescript
import { Elysia, t } from 'elysia'

const app = new Elysia()
  .get('/api/health', () => ({ status: 'ok' }))
  .post('/api/users', ({ body }) => body, {
    body: t.Object({
      email: t.String({ format: 'email' }),
      name: t.String({ minLength: 2 }),
    }),
  })
  .listen(3000)

console.log(`Running at ${app.server?.hostname}:${app.server?.port}`)
```

---

## tRPC: End-to-End Type Safety

### Why tRPC in 2026

- No schemas or code generation; rely on TypeScript inference
- Type errors caught at compile time, not runtime
- Ideal for full-stack TypeScript monorepos
- Works with Next.js, Remix, SvelteKit, standalone

### Server Setup

```typescript
// server/trpc.ts
import { initTRPC } from '@trpc/server'
import { z } from 'zod'

const t = initTRPC.create()

export const router = t.router
export const publicProcedure = t.procedure

// server/routers/user.ts
export const userRouter = router({
  getById: publicProcedure
    .input(z.string())
    .query(async ({ input }) => {
      return db.user.findUnique({ where: { id: input } })
    }),

  create: publicProcedure
    .input(z.object({
      email: z.string().email(),
      name: z.string().min(2),
    }))
    .mutation(async ({ input }) => {
      return db.user.create({ data: input })
    }),
})
```

### Client Usage

```typescript
// Client automatically infers types from server
const user = await trpc.user.getById.query('user-123')
// ^? User | null (inferred from server return type)

await trpc.user.create.mutate({
  email: 'test@example.com',
  name: 'Test User',
})
// TypeScript error if fields don't match server schema
```

### tRPC vs REST vs GraphQL

| Aspect | tRPC | REST | GraphQL |
|--------|------|------|---------|
| Type Safety | Full (inference) | Manual (OpenAPI) | Partial (codegen) |
| Schema | None needed | OpenAPI/Swagger | SDL required |
| Bundle Size | ~2kb | N/A | ~20kb+ |
| Learning Curve | Low | Low | Medium |
| Public API | Not ideal | Yes | Yes |

**Use tRPC when**: Full-stack TypeScript, internal APIs, monorepos.
**Use REST when**: Public APIs, multi-language clients, OpenAPI requirement.
**Use GraphQL when**: Complex data fetching, multiple clients with different needs.

---

## Edge-Compatible Databases

| Database | Type | Edge Support | Best For |
|----------|------|--------------|----------|
| **Cloudflare D1** | SQLite | Native | Cloudflare Workers |
| **Turso** | SQLite (libSQL) | Yes | Multi-region SQLite |
| **Neon** | PostgreSQL | Yes (HTTP) | Serverless Postgres |
| **PlanetScale** | MySQL | Yes | Serverless MySQL |
| **Upstash Redis** | Redis | Yes | Caching, sessions |

### Drizzle + Turso Example

```typescript
import { drizzle } from 'drizzle-orm/libsql'
import { createClient } from '@libsql/client'

const client = createClient({
  url: process.env.TURSO_DATABASE_URL!,
  authToken: process.env.TURSO_AUTH_TOKEN,
})

const db = drizzle(client)

// Type-safe queries
const users = await db.select().from(usersTable).where(eq(usersTable.id, '123'))
```

---

## Zero-Trust Security Patterns

In 2026, every request is adversarial until proven otherwise.

### Authentication at Edge

```typescript
// JWT validation at edge (Hono)
import { jwt } from 'hono/jwt'

app.use('/api/*', jwt({
  secret: process.env.JWT_SECRET!,
  cookie: 'token', // Also check cookies
}))

// Access claims in handlers
app.get('/api/me', (c) => {
  const payload = c.get('jwtPayload')
  return c.json({ userId: payload.sub })
})
```

### Rate Limiting at Edge

```typescript
// Using Cloudflare Workers + Durable Objects
app.use('/api/*', async (c, next) => {
  const ip = c.req.header('CF-Connecting-IP')
  const rateLimiter = c.env.RATE_LIMITER.get(c.env.RATE_LIMITER.idFromName(ip))

  const { allowed } = await rateLimiter.check()
  if (!allowed) {
    return c.json({ error: 'Rate limited' }, 429)
  }

  await next()
})
```

### Security Checklist

- [ ] Validate JWT at edge before origin
- [ ] Implement rate limiting per IP/user
- [ ] Use httpOnly cookies for tokens
- [ ] Enable CORS with specific origins
- [ ] Sanitize all user input
- [ ] Use Cloudflare WAF or similar
- [ ] Rotate secrets via secret manager
- [ ] Log security events to observability backend

---

## Observability at Edge

### OpenTelemetry Integration

```typescript
import { trace } from '@opentelemetry/api'

const tracer = trace.getTracer('edge-api')

app.use('*', async (c, next) => {
  const span = tracer.startSpan(`${c.req.method} ${c.req.path}`)

  try {
    await next()
    span.setStatus({ code: 1 }) // OK
  } catch (error) {
    span.setStatus({ code: 2, message: error.message }) // ERROR
    throw error
  } finally {
    span.end()
  }
})
```

### Structured Logging

```typescript
// Edge-compatible logging (no Pino/Winston)
const log = (level: string, message: string, meta?: object) => {
  console.log(JSON.stringify({
    timestamp: new Date().toISOString(),
    level,
    message,
    ...meta,
  }))
}

app.use('*', async (c, next) => {
  const start = Date.now()
  await next()
  log('info', 'Request completed', {
    method: c.req.method,
    path: c.req.path,
    status: c.res.status,
    duration: Date.now() - start,
  })
})
```

---

## Migration Strategies

### Node.js to Bun

1. **Test compatibility**: `bun run test` with existing test suite
2. **Check native modules**: Replace with pure JS alternatives if needed
3. **Update scripts**: Change `npm run` to `bun run`
4. **Deploy gradually**: Run Bun in staging before production

### Express to Hono

```typescript
// Express
app.get('/users/:id', async (req, res) => {
  const user = await getUser(req.params.id)
  res.json(user)
})

// Hono (almost identical)
app.get('/users/:id', async (c) => {
  const user = await getUser(c.req.param('id'))
  return c.json(user)
})
```

### Prisma to Drizzle (for edge)

1. Export Prisma schema to SQL
2. Define Drizzle schema matching tables
3. Migrate queries (Drizzle API mirrors SQL)
4. Test with edge runtime before deploying

---

## Related Resources

- [SKILL.md](../SKILL.md) - Backend engineering skill overview
- [backend-best-practices.md](backend-best-practices.md) - Template authoring and best practices
- [data/sources.json](../data/sources.json) - External references
- [../software-security-appsec/SKILL.md](../../software-security-appsec/SKILL.md) - Security patterns
