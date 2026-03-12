# Node.js Backend Best Practices

Comprehensive guide for building production-grade backend services with Node.js. Covers event loop, async patterns, framework selection, error handling, memory management, security, performance profiling, and deployment.

## Contents

- [Event Loop and Async Patterns](#event-loop-and-async-patterns)
- [Framework Comparison](#framework-comparison)
- [Error Handling](#error-handling)
- [Memory Management](#memory-management)
- [Process Management and Clustering](#process-management-and-clustering)
- [Security Hardening](#security-hardening)
- [Performance Profiling](#performance-profiling)
- [Production Deployment](#production-deployment)
- [Common Pitfalls](#common-pitfalls)
- [LTS and Version Guidance](#lts-and-version-guidance)
- [Resources](#resources)

---

## Event Loop and Async Patterns

### Event Loop Fundamentals

```text
   ┌───────────────────────────┐
┌─▶│           timers          │  ← setTimeout, setInterval
│  └─────────────┬─────────────┘
│  ┌─────────────▼─────────────┐
│  │     pending callbacks     │  ← I/O callbacks deferred
│  └─────────────┬─────────────┘
│  ┌─────────────▼─────────────┐
│  │       idle, prepare       │  ← internal use
│  └─────────────┬─────────────┘
│  ┌─────────────▼─────────────┐
│  │           poll            │  ← I/O events (network, file)
│  └─────────────┬─────────────┘
│  ┌─────────────▼─────────────┐
│  │           check           │  ← setImmediate
│  └─────────────┬─────────────┘
│  ┌─────────────▼─────────────┐
│  │      close callbacks      │  ← socket.on('close')
│  └─────────────┬─────────────┘
└─────────────────┘

Critical rule: NEVER block the event loop.
Blocking operations (CPU-heavy, synchronous I/O) stall ALL concurrent requests.
```

### Async/Await Best Practices

```typescript
// Good: Parallel independent operations
async function getDashboard(userId: string) {
  const [profile, orders, notifications] = await Promise.all([
    getProfile(userId),
    getRecentOrders(userId),
    getNotifications(userId),
  ]);
  return { profile, orders, notifications };
}

// Bad: Sequential when parallel is possible
async function getDashboard(userId: string) {
  const profile = await getProfile(userId);        // waits...
  const orders = await getRecentOrders(userId);     // then waits...
  const notifications = await getNotifications(userId); // then waits...
  return { profile, orders, notifications };
}
```

```typescript
// Good: Handle partial failures in parallel operations
async function getDashboardResilient(userId: string) {
  const results = await Promise.allSettled([
    getProfile(userId),
    getRecentOrders(userId),
    getNotifications(userId),
  ]);

  return {
    profile: results[0].status === 'fulfilled' ? results[0].value : null,
    orders: results[1].status === 'fulfilled' ? results[1].value : [],
    notifications: results[2].status === 'fulfilled' ? results[2].value : [],
  };
}
```

### Streams for Large Data

```typescript
import { pipeline } from 'node:stream/promises';
import { createReadStream, createWriteStream } from 'node:fs';
import { Transform } from 'node:stream';

// Good: Stream processing for large files (constant memory)
async function processLargeFile(input: string, output: string) {
  const transform = new Transform({
    transform(chunk, encoding, callback) {
      const processed = chunk.toString().toUpperCase();
      callback(null, processed);
    },
  });

  await pipeline(
    createReadStream(input),
    transform,
    createWriteStream(output)
  );
}

// Bad: Loading entire file into memory
async function processLargeFile(input: string, output: string) {
  const data = await fs.readFile(input, 'utf-8');  // OOM for large files
  const processed = data.toUpperCase();
  await fs.writeFile(output, processed);
}
```

### Worker Threads for CPU-Intensive Tasks

```typescript
import { Worker, isMainThread, parentPort, workerData } from 'node:worker_threads';

// Main thread: offload CPU work
function runWorker(data: unknown): Promise<unknown> {
  return new Promise((resolve, reject) => {
    const worker = new Worker(new URL('./worker.ts', import.meta.url), {
      workerData: data,
    });
    worker.on('message', resolve);
    worker.on('error', reject);
    worker.on('exit', (code) => {
      if (code !== 0) reject(new Error(`Worker exited with code ${code}`));
    });
  });
}

// worker.ts — runs in separate thread
if (!isMainThread) {
  const result = heavyComputation(workerData);
  parentPort?.postMessage(result);
}

// Use cases for worker threads:
// - Image processing, resizing
// - PDF generation
// - Data parsing (large CSV, XML)
// - Cryptographic operations
// - Machine learning inference
```

---

## Framework Comparison

| Feature | Express | Fastify | NestJS | Hono |
|---------|---------|---------|--------|------|
| Performance | Baseline | 2-3x Express | Similar to Express | 3-5x Express |
| TypeScript | Community types | Native | Native | Native |
| Validation | Middleware (manual) | JSON Schema (built-in) | Pipes + class-validator | Zod/Valibot middleware |
| DI container | None | None (plugin system) | Built-in (IoC) | None |
| Plugin ecosystem | Massive (npm) | Growing | Modules | Growing |
| Learning curve | Low | Low-Medium | Medium-High | Low |
| Edge/Serverless | Possible (adapters) | Possible | Heavy for edge | Native (designed for it) |
| Best for | Simple APIs, prototypes | High-performance APIs | Enterprise, DDD, complex apps | Edge, serverless, Bun |

### Framework Selection Decision Tree

```text
What are you building?
  ├─ Simple REST API, rapid prototype → Express (widest ecosystem)
  ├─ Performance-critical API service → Fastify (schema-based validation, fast serialization)
  ├─ Enterprise app with DI, modules, complex domain → NestJS (batteries-included)
  ├─ Edge/serverless, multi-runtime → Hono (Cloudflare Workers, Bun, Deno, Node)
  └─ Internal API in TS monorepo → Consider tRPC (no framework needed)
```

### Express Production Setup

```typescript
import express from 'express';
import helmet from 'helmet';
import cors from 'cors';
import compression from 'compression';
import { pinoHttp } from 'pino-http';

const app = express();

// Security
app.use(helmet());
app.use(cors({ origin: process.env.ALLOWED_ORIGINS?.split(',') }));

// Performance
app.use(compression());
app.use(express.json({ limit: '1mb' }));

// Observability
app.use(pinoHttp({ level: process.env.LOG_LEVEL || 'info' }));

// Trust proxy (when behind load balancer)
app.set('trust proxy', 1);

// Request timeout
app.use((req, res, next) => {
  res.setTimeout(30_000, () => {
    res.status(408).json({ error: 'Request timeout' });
  });
  next();
});
```

### Fastify Production Setup

```typescript
import Fastify from 'fastify';
import fastifyHelmet from '@fastify/helmet';
import fastifyCors from '@fastify/cors';
import fastifyRateLimit from '@fastify/rate-limit';

const fastify = Fastify({
  logger: {
    level: process.env.LOG_LEVEL || 'info',
    transport: process.env.NODE_ENV === 'development'
      ? { target: 'pino-pretty' }
      : undefined,
  },
  requestTimeout: 30_000,
  bodyLimit: 1_048_576, // 1MB
});

await fastify.register(fastifyHelmet);
await fastify.register(fastifyCors, { origin: true });
await fastify.register(fastifyRateLimit, {
  max: 100,
  timeWindow: '1 minute',
});

// Schema-based validation (Fastify's strength)
fastify.post('/api/users', {
  schema: {
    body: {
      type: 'object',
      required: ['email', 'name'],
      properties: {
        email: { type: 'string', format: 'email' },
        name: { type: 'string', minLength: 2, maxLength: 100 },
      },
    },
    response: {
      201: {
        type: 'object',
        properties: {
          id: { type: 'string' },
          email: { type: 'string' },
        },
      },
    },
  },
}, async (request, reply) => {
  const user = await createUser(request.body);
  reply.status(201).send(user);
});
```

---

## Error Handling

### Unhandled Rejection and Exception Handling

```typescript
// MUST handle these in production — otherwise the process crashes silently

process.on('unhandledRejection', (reason, promise) => {
  logger.fatal({ reason, promise }, 'Unhandled Promise Rejection');
  // Log, alert, and shut down gracefully
  gracefulShutdown(1);
});

process.on('uncaughtException', (error) => {
  logger.fatal({ error }, 'Uncaught Exception');
  // MUST exit after uncaught exception — process state is unreliable
  gracefulShutdown(1);
});

async function gracefulShutdown(exitCode: number) {
  logger.info('Starting graceful shutdown...');
  // 1. Stop accepting new requests
  server.close();
  // 2. Finish in-flight requests (with timeout)
  await Promise.race([
    closeAllConnections(),
    new Promise(resolve => setTimeout(resolve, 10_000)),
  ]);
  // 3. Exit
  process.exit(exitCode);
}
```

### Async Error Wrapper

```typescript
// Express: async errors must be caught and forwarded to error middleware
function asyncHandler(fn: (req: Request, res: Response, next: NextFunction) => Promise<void>) {
  return (req: Request, res: Response, next: NextFunction) => {
    fn(req, res, next).catch(next);
  };
}

app.get('/api/users/:id', asyncHandler(async (req, res) => {
  const user = await getUserById(req.params.id);
  if (!user) {
    throw new NotFoundError('User not found');
  }
  res.json(user);
}));

// Centralized error middleware (MUST be last)
app.use((err: Error, req: Request, res: Response, _next: NextFunction) => {
  logger.error({ err, path: req.path, method: req.method }, 'Request error');

  if (err instanceof AppError) {
    res.status(err.statusCode).json({
      type: err.type,
      title: err.message,
      status: err.statusCode,
      detail: err.detail,
      instance: req.path,
    });
  } else {
    res.status(500).json({
      type: 'https://example.com/problems/internal-error',
      title: 'Internal Server Error',
      status: 500,
      instance: req.path,
    });
  }
});
```

### Domain Error Classes

```typescript
abstract class AppError extends Error {
  abstract statusCode: number;
  abstract type: string;
  detail?: string;

  constructor(message: string, detail?: string) {
    super(message);
    this.name = this.constructor.name;
    this.detail = detail;
  }
}

class NotFoundError extends AppError {
  statusCode = 404;
  type = 'https://example.com/problems/not-found';
}

class ValidationError extends AppError {
  statusCode = 400;
  type = 'https://example.com/problems/validation-error';
}

class ConflictError extends AppError {
  statusCode = 409;
  type = 'https://example.com/problems/conflict';
}
```

---

## Memory Management

### Common Memory Leak Sources

| Source | Symptom | Fix |
|--------|---------|-----|
| Event listeners not removed | RSS grows steadily | `removeListener`, `AbortController` |
| Global caches without TTL/LRU | Heap grows until OOM | Use `lru-cache` with `maxSize` |
| Closures retaining large objects | Heap snapshot shows unexpected retention | Break closure references |
| Unfinished streams | Buffers accumulate | Proper `pipeline()`, error handling |
| `setInterval` without `clearInterval` | Callbacks accumulate | Clear intervals on shutdown |

### Leak Detection

```typescript
// 1. Monitor heap in production
import v8 from 'node:v8';

function reportMemory() {
  const heap = v8.getHeapStatistics();
  metrics.gauge('nodejs.heap.used', heap.used_heap_size);
  metrics.gauge('nodejs.heap.total', heap.total_heap_size);
  metrics.gauge('nodejs.heap.limit', heap.heap_size_limit);
  metrics.gauge('nodejs.external', heap.external_memory);
}

setInterval(reportMemory, 30_000);

// 2. Development: use --inspect and Chrome DevTools heap snapshots
// node --inspect dist/server.js
// Chrome → chrome://inspect → Take heap snapshot

// 3. CLI profiling
// clinic heapprofile -- node dist/server.js
// autocannon -c 100 -d 30 http://localhost:3000/api/users
```

### Memory Best Practices

```typescript
// Use LRU cache instead of plain objects
import { LRUCache } from 'lru-cache';

const cache = new LRUCache<string, UserProfile>({
  max: 5000,              // Max entries
  ttl: 1000 * 60 * 5,     // 5 minutes TTL
  maxSize: 50_000_000,     // 50MB max
  sizeCalculation: (value) => JSON.stringify(value).length,
});

// Set memory limits for the process
// node --max-old-space-size=512 dist/server.js  (512MB heap limit)
```

---

## Process Management and Clustering

### Clustering for Multi-Core Utilization

```typescript
import cluster from 'node:cluster';
import { cpus } from 'node:os';

if (cluster.isPrimary) {
  const numCPUs = cpus().length;
  console.log(`Primary ${process.pid} forking ${numCPUs} workers`);

  for (let i = 0; i < numCPUs; i++) {
    cluster.fork();
  }

  cluster.on('exit', (worker, code, signal) => {
    console.log(`Worker ${worker.process.pid} exited (${signal || code})`);
    // Restart crashed workers
    if (code !== 0) {
      cluster.fork();
    }
  });
} else {
  // Workers run the HTTP server
  startServer();
}
```

### Container-Based Deployment (Preferred)

```text
In containerized environments (Docker, Kubernetes), prefer:

1 process per container (no clustering)

Reasoning:
  - Kubernetes handles horizontal scaling (replicas)
  - Health checks are per-container
  - Resource limits are per-container
  - Simpler debugging (1 PID per container)

Use clustering only for:
  - Bare metal / VM deployments without orchestration
  - PM2-managed non-containerized deployments
```

### Graceful Shutdown Pattern

```typescript
const server = app.listen(port);

const signals: NodeJS.Signals[] = ['SIGTERM', 'SIGINT'];

for (const signal of signals) {
  process.on(signal, async () => {
    logger.info({ signal }, 'Received shutdown signal');

    // 1. Stop accepting new connections
    server.close(() => {
      logger.info('HTTP server closed');
    });

    // 2. Close database connections
    await db.$disconnect();

    // 3. Close Redis connections
    await redis.quit();

    // 4. Drain message queues
    await queue.close();

    // 5. Exit
    process.exit(0);
  });
}
```

---

## Security Hardening

### Essential Security Middleware

```typescript
import helmet from 'helmet';
import rateLimit from 'express-rate-limit';
import cors from 'cors';

// Helmet: sets security headers
app.use(helmet({
  contentSecurityPolicy: {
    directives: {
      defaultSrc: ["'self'"],
      scriptSrc: ["'self'"],
    },
  },
  hsts: { maxAge: 31536000, includeSubDomains: true },
}));

// CORS: restrict origins
app.use(cors({
  origin: ['https://app.example.com'],
  methods: ['GET', 'POST', 'PUT', 'DELETE'],
  credentials: true,
}));

// Rate limiting: sliding window
const limiter = rateLimit({
  windowMs: 15 * 60 * 1000,  // 15 minutes
  max: 100,                   // 100 requests per window
  standardHeaders: true,      // Return rate limit info in headers
  legacyHeaders: false,
  store: new RedisStore({ client: redis }),  // Distributed rate limiting
});
app.use('/api/', limiter);
```

### Security Checklist

| Concern | Implementation |
|---------|---------------|
| Input validation | Zod/Valibot at API boundary, never trust client |
| SQL injection | Parameterized queries (Prisma, Drizzle, prepared statements) |
| XSS | Helmet CSP headers, sanitize output |
| CSRF | SameSite cookies, CSRF tokens for forms |
| Auth tokens | httpOnly, Secure, SameSite cookies (not localStorage) |
| Password hashing | Argon2id (preferred) or bcrypt (cost >= 12) |
| Secrets management | Environment variables + secret manager (Vault, AWS SM) |
| Dependency auditing | `npm audit`, Socket.dev, Snyk in CI |
| HTTPS | TLS everywhere, HSTS header |
| Request size limits | `express.json({ limit: '1mb' })` |

---

## Performance Profiling

### Profiling Tools

| Tool | Purpose | Usage |
|------|---------|-------|
| `clinic doctor` | Identify bottleneck category (I/O, event loop, GC) | `clinic doctor -- node server.js` |
| `clinic flame` | CPU flame graph (function-level hotspots) | `clinic flame -- node server.js` |
| `clinic heapprofile` | Memory allocation profiling | `clinic heapprofile -- node server.js` |
| `0x` | Lightweight CPU flame graph | `0x server.js` |
| `autocannon` | HTTP load testing | `autocannon -c 100 -d 30 http://localhost:3000` |
| `--inspect` | Chrome DevTools debugging and profiling | `node --inspect dist/server.js` |
| Node.js `perf_hooks` | Programmatic performance measurement | Built-in, no external dependency |

### Performance Measurement

```typescript
import { performance, PerformanceObserver } from 'node:perf_hooks';

// Measure specific operations
async function measureDbQuery() {
  const start = performance.now();
  const result = await db.query('SELECT * FROM users WHERE active = true');
  const duration = performance.now() - start;

  metrics.histogram('db.query.duration', duration, { query: 'active_users' });
  return result;
}

// Monitor event loop lag
import { monitorEventLoopDelay } from 'node:perf_hooks';

const histogram = monitorEventLoopDelay({ resolution: 20 });
histogram.enable();

setInterval(() => {
  metrics.gauge('nodejs.event_loop.p50', histogram.percentile(50) / 1e6);
  metrics.gauge('nodejs.event_loop.p99', histogram.percentile(99) / 1e6);
  metrics.gauge('nodejs.event_loop.max', histogram.max / 1e6);
  histogram.reset();
}, 10_000);
```

### Performance Budgets

| Metric | Target | Action If Exceeded |
|--------|--------|--------------------|
| Event loop lag P99 | < 50ms | Profile CPU-heavy code, offload to workers |
| Heap usage | < 70% of limit | Check for leaks, add LRU cache limits |
| Response time P95 | < 200ms | Profile hot paths, add caching |
| GC pause time | < 100ms | Reduce allocation rate, tune GC flags |

---

## Production Deployment

### Docker Best Practices

```dockerfile
# Use specific LTS version, not :latest
FROM node:22-alpine AS base

# Install production deps in a separate stage
FROM base AS deps
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci --omit=dev

# Build TypeScript
FROM base AS build
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
RUN npm run build

# Production image
FROM base AS production
WORKDIR /app
ENV NODE_ENV=production

# Non-root user
RUN addgroup --system --gid 1001 nodejs && \
    adduser --system --uid 1001 appuser
USER appuser

COPY --from=deps /app/node_modules ./node_modules
COPY --from=build /app/dist ./dist
COPY package.json ./

EXPOSE 3000
CMD ["node", "dist/server.js"]
```

### Health Check Endpoints

```typescript
// Kubernetes-compatible health checks
app.get('/health/live', (req, res) => {
  res.status(200).json({ status: 'alive' });
});

app.get('/health/ready', async (req, res) => {
  const checks = await Promise.allSettled([
    db.$queryRaw`SELECT 1`,
    redis.ping(),
  ]);

  const allHealthy = checks.every(c => c.status === 'fulfilled');
  res.status(allHealthy ? 200 : 503).json({
    status: allHealthy ? 'ready' : 'not ready',
    checks: {
      database: checks[0].status === 'fulfilled' ? 'ok' : 'fail',
      cache: checks[1].status === 'fulfilled' ? 'ok' : 'fail',
    },
  });
});
```

---

## Common Pitfalls

| Pitfall | Impact | Fix |
|---------|--------|-----|
| Synchronous `fs` methods (`readFileSync`) | Blocks event loop | Use `fs/promises` |
| `JSON.parse` on untrusted input without try/catch | Crashes process | Wrap in try/catch or use schema validation |
| No timeout on HTTP client calls | Hangs indefinitely | `AbortSignal.timeout(5000)` on fetch |
| Logging with `console.log` | No structure, no levels, slow | Use pino with structured JSON |
| Starting without `NODE_ENV=production` | Debug overhead, verbose errors | Set in Dockerfile and deployment config |
| Not setting `--max-old-space-size` | Default may be too high or too low | Set explicitly based on container memory limit |
| Using `npm start` in Docker | Extra process, no signal handling | Use `node dist/server.js` directly |
| Global error handlers that do not exit | Process in unknown state | Always exit after uncaughtException |

---

## LTS and Version Guidance

### Node.js Release Schedule

| Version | Status | Active LTS Start | Maintenance End |
|---------|--------|-------------------|-----------------|
| Node.js 22 | Active LTS | October 2024 | April 2027 |
| Node.js 20 | Maintenance | October 2023 | April 2026 |
| Node.js 18 | End of Life | April 2023 | April 2025 |

**Recommendation (2026):** Use Node.js 22 LTS for new projects. Node.js 20 is acceptable for existing projects in maintenance.

### Notable Node.js 22 Features

- Built-in `fetch` (stable)
- Native `WebSocket` client
- `node --watch` for development
- Improved `node:test` runner
- ESM loader hooks (stable)
- Performance improvements in V8

**Always check [nodejs.org/en/about/releases/](https://nodejs.org/en/about/releases/) for the current LTS schedule.**

---

## Resources

- [Node.js Best Practices (goldbergyoni)](https://github.com/goldbergyoni/nodebestpractices) — Comprehensive community guide
- [Node.js Official Docs](https://nodejs.org/docs/latest/api/) — API reference
- [Fastify Documentation](https://fastify.dev/docs/latest/) — Fastify framework
- [NestJS Documentation](https://docs.nestjs.com/) — NestJS framework
- [Hono Documentation](https://hono.dev/) — Hono framework
- [Clinic.js](https://clinicjs.org/) — Node.js performance profiling suite
- Related: [go-best-practices.md](go-best-practices.md), [rust-best-practices.md](rust-best-practices.md), [python-best-practices.md](python-best-practices.md)
