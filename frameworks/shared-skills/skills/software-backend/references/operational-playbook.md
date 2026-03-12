# Core Backend Patterns

Execution-ready patterns and checklists for common backend concerns.

## Contents

- [Pattern: Standard API Architecture](#pattern-standard-api-architecture)
- [Pattern: RESTful API Design](#pattern-restful-api-design)
- [Pattern: GraphQL API Design (2024-2025 Best Practice)](#pattern-graphql-api-design-2024-2025-best-practice)
- [Pattern: Authentication & Authorization](#pattern-authentication--authorization)
- [Pattern: Error Handling & Validation](#pattern-error-handling--validation)
- [Pattern: Database Layer (Prisma + PostgreSQL)](#pattern-database-layer-prisma--postgresql)
- [Pattern: Microservices & Circuit Breaker (2024-2025 Best Practice)](#pattern-microservices--circuit-breaker-2024-2025-best-practice)
- [Pattern: Performance & Caching](#pattern-performance--caching)
- [Pattern: Testing Strategy](#pattern-testing-strategy)
- [Pattern: Logging & Monitoring](#pattern-logging--monitoring)
- [Pattern: TypeScript Best Practices](#pattern-typescript-best-practices)
- [Pattern: API Security](#pattern-api-security)
- [Quick Decision Tables](#quick-decision-tables)
- [Templates](#templates)
- [Resources](#resources)

---

## Pattern: Standard API Architecture

**Use when:** Building production-grade backend services.

**Structure:**
```
src/
|-- api/
|   |-- routes/ # Route definitions
|   |-- controllers/ # Request handlers
|   |-- middlewares/ # Auth, validation, error handling
|   `-- validators/ # Input validation schemas
|-- services/ # Business logic
|-- repositories/ # Data access layer
|-- models/ # Domain models
|-- config/ # Configuration
|-- utils/ # Utilities
`-- types/ # TypeScript types
```

**Checklist:**
- [ ] Separation of concerns (routes/controllers/services/repos)
- [ ] Middleware for cross-cutting concerns
- [ ] Environment-based configuration
- [ ] Centralized error handling
- [ ] Request validation at API boundary
- [ ] Dependency injection for testability

---

## Pattern: RESTful API Design

**Use when:** Designing resource-based APIs.

**Principles:**
- Use HTTP methods correctly (GET, POST, PUT, PATCH, DELETE)
- Resource-based URLs: `/users/:id` not `/getUser?id=1`
- Use proper status codes (200, 201, 400, 401, 404, 500)
- Pagination for list endpoints
- Filtering and sorting support
- Versioning strategy (URL, header, or accept header)

**Example:**
```
GET /api/v1/users # List users
POST /api/v1/users # Create user
GET /api/v1/users/:id # Get user
PUT /api/v1/users/:id # Replace user
PATCH /api/v1/users/:id # Update user
DELETE /api/v1/users/:id # Delete user

GET /api/v1/users/:id/orders # Nested resources
```

**Checklist:**
- [ ] Consistent naming (plural nouns)
- [ ] Idempotent operations
- [ ] Proper HTTP methods
- [ ] Pagination metadata in response
- [ ] Filter/sort query parameters documented
- [ ] Rate limiting configured

---

## Pattern: GraphQL API Design (2024-2025 Best Practice)

**Use when:** Clients need flexible data fetching, avoiding over-fetching/under-fetching.

**Why GraphQL in 2025:**
- Single endpoint for all queries/mutations
- Strongly typed schema with automatic documentation
- Client-driven data requirements (request exactly what you need)
- Easier API evolution without breaking changes
- Built-in introspection and tooling support

**Quick Example - GraphQL Schema:**
```graphql
type User {
  id: ID!
  email: String!
  name: String!
  posts: [Post!]!
}

type Post {
  id: ID!
  title: String!
  content: String!
  author: User!
}

type Query {
  user(id: ID!): User
  users(limit: Int, offset: Int): [User!]!
  post(id: ID!): Post
}

type Mutation {
  createUser(email: String!, name: String!): User!
  updatePost(id: ID!, title: String, content: String): Post!
}
```

**Quick Example - GraphQL Resolver (Node.js + Apollo Server):**
```typescript
const resolvers = {
  Query: {
    user: async (_parent, { id }, context) => {
      return context.prisma.user.findUnique({ where: { id } });
    },
    users: async (_parent, { limit = 20, offset = 0 }, context) => {
      return context.prisma.user.findMany({ take: limit, skip: offset });
    },
  },
  Mutation: {
    createUser: async (_parent, { email, name }, context) => {
      return context.prisma.user.create({ data: { email, name } });
    },
  },
  User: {
    posts: async (parent, _args, context) => {
      return context.prisma.post.findMany({ where: { authorId: parent.id } });
    },
  },
};
```

**GraphQL Best Practices (2025):**
- Use **persisted queries** for caching and security
- Implement **DataLoader** to prevent N+1 query problems
- Apply **depth limiting** to prevent malicious deeply nested queries
- Use **GraphQL Federation** for microservices architectures
- Leverage **schema stitching** for composing multiple GraphQL APIs
- Enable **field-level authorization** for fine-grained access control

**Checklist:**
- [ ] Schema-first or code-first approach chosen
- [ ] Resolvers handle errors gracefully
- [ ] DataLoader for batching and caching
- [ ] Query complexity analysis enabled
- [ ] Depth limiting configured
- [ ] Persisted queries for production
- [ ] Field-level permissions implemented
- [ ] Apollo Server or Pothos GraphQL for type safety

---

## Pattern: Authentication & Authorization

**Use when:** Implementing user authentication and access control.

For comprehensive authentication patterns including JWT, OAuth2, sessions, RBAC, and API key management, see:

**Reference:** `references/backend-best-practices.md` (Authentication section)

**Quick Example - JWT Authentication:**
```typescript
// Generate token
const token = jwt.sign(
 { userId: user.id, role: user.role },
 process.env.JWT_SECRET,
 { expiresIn: '7d' }
);

// Verify middleware
const authenticate = async (req, res, next) => {
 const token = req.headers.authorization?.replace('Bearer ', '');
 if (!token) return next(new AppError(401, 'Unauthorized'));

 try {
 const payload = jwt.verify(token, process.env.JWT_SECRET);
 req.user = await userService.findById(payload.userId);
 next();
 } catch (error) {
 next(new AppError(401, 'Invalid token'));
 }
};
```

**Checklist:**
- [ ] Secure password hashing (bcrypt, argon2)
- [ ] Token expiration and refresh mechanism
- [ ] Role-based access control (RBAC)
- [ ] Session management for sensitive operations
- [ ] CSRF protection for session-based auth

---

## Pattern: Error Handling & Validation

**Use when:** Implementing robust error management and input validation.

For comprehensive error handling patterns including custom error classes, global error handlers, validation strategies, and error logging, see:

**Reference:** `references/backend-best-practices.md` (Error Handling section)

**Quick Example - Custom Error Class:**
```typescript
class AppError extends Error {
 constructor(
 public statusCode: number,
 public message: string,
 public isOperational = true
 ) {
 super(message);
 Error.captureStackTrace(this, this.constructor);
 }
}

// Usage
throw new AppError(404, 'User not found');
throw new AppError(400, 'Invalid email format');
```

**Quick Example - Request Validation (Zod):**
```typescript
import { z } from 'zod';

const createUserSchema = z.object({
 email: z.string().email(),
 password: z.string().min(8),
 name: z.string().min(2).max(50),
 role: z.enum(['user', 'admin']).optional(),
});

// Middleware
const validate = (schema) => (req, res, next) => {
 try {
 req.body = schema.parse(req.body);
 next();
 } catch (error) {
 next(new AppError(400, error.message));
 }
};
```

**Checklist:**
- [ ] Custom error classes
- [ ] Global error handler
- [ ] Validate at API boundary
- [ ] Client-friendly error messages
- [ ] Never expose stack traces in production

---

## Pattern: Database Layer (Prisma + PostgreSQL)

**Use when:** Implementing database access with Prisma ORM.

For comprehensive database patterns including repository pattern, schema design, migrations, query optimization, transactions, and connection pooling, see:

**Reference:** `references/backend-best-practices.md` (Database Patterns section)

**Prisma Best Practices:**
- **Prisma Accelerate** for serverless/edge deployments (HTTP-based connection pooling, global caching, eliminates cold start penalties)
- **Singleton pattern with globalThis** in Next.js to prevent connection pool exhaustion from hot reloading
- **Schema-first approach** (define models in `schema.prisma`, auto-generate type-safe client)
- **Connection pool configuration**: Default is `num_cpus * 2 + 1`; for serverless, start with `connection_limit=1` and optimize upward
- **Production migrations**: Always use `prisma migrate deploy` in production, never `prisma migrate dev`

**Quick Example - Repository Pattern:**
```typescript
interface UserRepository {
 findById(id: string): Promise<User | null>;
 findByEmail(email: string): Promise<User | null>;
 create(data: CreateUserInput): Promise<User>;
 update(id: string, data: UpdateUserInput): Promise<User>;
 delete(id: string): Promise<void>;
}

class PrismaUserRepository implements UserRepository {
 constructor(private prisma: PrismaClient) {}

 async findById(id: string) {
 return this.prisma.user.findUnique({ where: { id } });
 }

 async create(data: CreateUserInput) {
 return this.prisma.user.create({ data });
 }
}
```

**Checklist:**
- [ ] Repository pattern for data access
- [ ] Transaction support
- [ ] Query optimization (select only needed fields)
- [ ] Database constraints match application rules
- [ ] Soft deletes for audit trails

---

## Pattern: Microservices & Circuit Breaker (2024-2025 Best Practice)

**Use when:** Building distributed systems with multiple services requiring fault tolerance.

**Circuit Breaker Pattern:**
Prevents cascading failures by stopping requests to a failing service after a threshold is reached.

**Quick Example - Circuit Breaker (Node.js):**
```typescript
import CircuitBreaker from 'opossum';

// Wrap external service call
const options = {
  timeout: 3000, // Request timeout
  errorThresholdPercentage: 50, // Open circuit at 50% failure rate
  resetTimeout: 30000, // Try again after 30 seconds
};

const breaker = new CircuitBreaker(async (userId: string) => {
  return await fetch(`https://api.external.com/users/${userId}`);
}, options);

// Circuit states: CLOSED (normal) -> OPEN (failing) -> HALF_OPEN (testing)
breaker.on('open', () => logger.warn('Circuit breaker opened'));
breaker.on('halfOpen', () => logger.info('Circuit breaker half-open, testing'));
breaker.on('close', () => logger.info('Circuit breaker closed'));

// Use the breaker
try {
  const user = await breaker.fire(userId);
} catch (error) {
  // Fallback: return cached data or default response
  return getCachedUser(userId) || { id: userId, name: 'Unknown' };
}
```

**Retry with Exponential Backoff:**
```typescript
async function retryWithBackoff<T>(
  fn: () => Promise<T>,
  maxRetries = 3,
  baseDelay = 1000
): Promise<T> {
  for (let attempt = 0; attempt <= maxRetries; attempt++) {
    try {
      return await fn();
    } catch (error) {
      if (attempt === maxRetries) throw error;

      const delay = baseDelay * Math.pow(2, attempt); // Exponential backoff
      await new Promise(resolve => setTimeout(resolve, delay));
    }
  }
  throw new Error('Max retries exceeded');
}
```

**Microservices Best Practices (2025):**
- Use **service mesh** (Istio, Linkerd) for traffic management and observability
- Implement **health checks** (`/health`, `/ready`) for each service
- Apply **distributed tracing** (OpenTelemetry, Jaeger) to debug cross-service issues
- Use **API gateways** (Kong, Traefik) for centralized routing and auth
- Implement **saga pattern** for distributed transactions
- Enable **graceful degradation** with circuit breakers and fallbacks

**Checklist:**
- [ ] Circuit breakers for external service calls
- [ ] Retry logic with exponential backoff
- [ ] Health check endpoints implemented
- [ ] Service discovery configured (Consul, etcd)
- [ ] Distributed tracing enabled
- [ ] API gateway for routing
- [ ] Fallback mechanisms for failures
- [ ] Timeout configuration per service

---

## Pattern: Performance & Caching

**Use when:** Optimizing read-heavy operations and improving performance.

For comprehensive performance patterns including caching strategies (Redis, in-memory), pagination (cursor vs offset), background jobs (BullMQ), and horizontal scaling, see:

**Reference:** `references/backend-best-practices.md` (Performance Patterns section)

**Quick Example - Redis Caching:**
```typescript
class CacheService {
 constructor(
 private redis: Redis,
 private defaultTTL = 300 // 5 minutes
 ) {}

 async get<T>(key: string): Promise<T | null> {
 const cached = await this.redis.get(key);
 return cached ? JSON.parse(cached) : null;
 }

 async set(key: string, value: any, ttl = this.defaultTTL) {
 await this.redis.setex(key, ttl, JSON.stringify(value));
 }

 async invalidate(pattern: string) {
 const keys = await this.redis.keys(pattern);
 if (keys.length) await this.redis.del(...keys);
 }
}
```

**Quick Example - Cursor-based Pagination:**
```typescript
async function listUsers({ cursor, limit = 20 }: PaginationParams) {
 const users = await prisma.user.findMany({
 take: limit + 1,
 ...(cursor && { skip: 1, cursor: { id: cursor } }),
 orderBy: { createdAt: 'desc' },
 });

 const hasMore = users.length > limit;
 const items = hasMore ? users.slice(0, -1) : users;

 return {
 items,
 nextCursor: hasMore ? items[items.length - 1].id : null,
 hasMore,
 };
}
```

**Checklist:**
- [ ] Cache invalidation strategy
- [ ] TTL for all cached data
- [ ] Cursor-based pagination for infinite scroll
- [ ] Background jobs for async tasks
- [ ] Connection pooling configured

---

## Pattern: Testing Strategy

**Use when:** Ensuring code quality and reliability.

For comprehensive testing patterns including unit testing, integration testing, E2E testing, mocking strategies, and CI/CD integration, see:

**Reference:** `references/backend-best-practices.md` (Testing section)

**Test Pyramid:**
```
 E2E Tests (5%)
 ----------------
 Integration Tests (20%)
 ----------------------
 Unit Tests (75%)
 ---------------------------
```

**Quick Example - Unit Test:**
```typescript
describe('UserService', () => {
 let userService: UserService;
 let mockRepo: jest.Mocked<UserRepository>;

 beforeEach(() => {
 mockRepo = {
 findById: jest.fn(),
 create: jest.fn(),
 };
 userService = new UserService(mockRepo);
 });

 it('should create user with hashed password', async () => {
 const input = { email: 'test@example.com', password: 'password123' };
 mockRepo.create.mockResolvedValue({ id: '1', ...input });

 const result = await userService.createUser(input);

 expect(mockRepo.create).toHaveBeenCalledWith({
 email: input.email,
 password: expect.not.stringContaining('password123'),
 });
 });
});
```

**Checklist:**
- [ ] 80%+ code coverage
- [ ] Test happy paths and error cases
- [ ] Mock external dependencies
- [ ] Use test database
- [ ] Parallel test execution

---

## Pattern: Logging & Monitoring

**Use when:** Implementing observability.

For comprehensive observability patterns including structured logging (Pino/Winston), request tracing, APM integration, error tracking (Sentry), and monitoring best practices, see:

**Reference:** `references/backend-best-practices.md` (Observability section)

**Quick Example - Structured Logging:**
```typescript
import pino from 'pino';

const logger = pino({
 level: process.env.LOG_LEVEL || 'info',
 formatters: {
 level: (label) => ({ level: label }),
 },
});

// Usage
logger.info({ userId: user.id, action: 'login' }, 'User logged in');
logger.error({ err, requestId }, 'Database query failed');
```

**Checklist:**
- [ ] Structured JSON logs
- [ ] Correlation IDs for request tracing
- [ ] Log levels: error, warn, info, debug
- [ ] Never log sensitive data (passwords, tokens)
- [ ] APM integration (New Relic, Datadog)

---

## Pattern: TypeScript Best Practices

**Use when:** Writing type-safe backend code.

**Critical TypeScript Patterns:**
- **Enable strict mode** in `tsconfig.json` (catches subtle bugs)
- **Use `unknown` instead of `any`** for safer type handling
- **Template literal types** for dynamic string-based types
- **The `satisfies` operator** (TypeScript 4.9+) for enforcing constraints while maintaining inference
- **Discriminated unions** for state machines and API responses
- **Generics with constraints** for reusable type-safe functions
- **Composition over inheritance** for type definitions

**Quick Example - Discriminated Unions:**
```typescript
type ApiResponse<T> =
 | { status: 'success'; data: T }
 | { status: 'error'; error: string };

function handleResponse(response: ApiResponse<User>) {
 if (response.status === 'success') {
 return response.data; // TypeScript knows data exists
 } else {
 throw new Error(response.error); // TypeScript knows error exists
 }
}
```

**Quick Example - satisfies Operator:**
```typescript
const config = {
 database: 'postgres',
 port: 5432,
 ssl: true
} satisfies Record<string, string | number | boolean>;

// config.port is inferred as number, not string | number | boolean
```

**Checklist:**
- [ ] `strict: true` in tsconfig.json
- [ ] Avoid `any`, prefer `unknown` or proper types
- [ ] Use generics with extends constraints
- [ ] Leverage discriminated unions for API responses
- [ ] Apply `readonly` for immutability
- [ ] Use template literal types for string patterns

---

## Pattern: API Security

**Use when:** Securing backend APIs with modern best practices.

**IMPORTANT:** For comprehensive security patterns, see the **software-security-patterns** skill which covers:
- OWASP Top 10 vulnerabilities and prevention
- Authentication & Authorization (JWT, OAuth, MFA, RBAC, ABAC)
- Input validation & sanitization (SQL injection, XSS, CSRF)
- Cryptography standards (password hashing, encryption)
- Production-ready security templates

**Backend-Specific Security:** See `references/backend-best-practices.md` (Security section) for Node.js/Express-specific implementations.

**Modern Security Enhancements:**
- **Secret Managers**: Use AWS Secrets Manager, HashiCorp Vault, or Azure Key Vault instead of `.env` files in production
- **Helmet.js**: Add secure HTTP headers to protect against XSS, clickjacking, MIME sniffing
- **Rate Limiting**: Implement per-endpoint and per-user rate limits with Redis-backed stores
- **Input Validation**: Use Zod or Joi for runtime validation at API boundaries
- **Dependency Scanning**: Automate with Snyk, npm audit, or GitHub Dependabot

**Quick Example - Helmet.js:**
```typescript
import helmet from 'helmet';
import express from 'express';

const app = express();

app.use(helmet({
 contentSecurityPolicy: {
 directives: {
 defaultSrc: ["'self'"],
 styleSrc: ["'self'", "'unsafe-inline'"]
 }
 },
 hsts: {
 maxAge: 31536000,
 includeSubDomains: true,
 preload: true
 }
}));
```

**Security Checklist:**
- [ ] HTTPS only (enforce with HSTS headers)
- [ ] Rate limiting (express-rate-limit with Redis backend)
- [ ] CORS configuration (specific origins, no wildcards in production)
- [ ] Helmet.js security headers (CSP, XSS protection, HSTS)
- [ ] Input validation and sanitization (Zod/Joi at API boundary)
- [ ] SQL injection prevention (use Prisma/parameterized queries)
- [ ] XSS prevention (escape output, CSP headers)
- [ ] CSRF protection (for cookie-based auth)
- [ ] Secrets in secret managers (AWS Secrets Manager, HashiCorp Vault)
- [ ] Dependency vulnerability scanning (npm audit, Snyk, Dependabot)
- [ ] API key rotation and expiration policies

---

# Quick Decision Tables

## Database Relationship Matrix

| Relationship | Prisma Syntax | Example |
|--------------|---------------|---------|
| One-to-One | `@relation` with `@unique` | User <-> Profile |
| One-to-Many | `@relation` | User -> Posts |
| Many-to-Many | Implicit or explicit join table | Posts <-> Tags |

---

## HTTP Status Codes

| Code | Meaning | Use Case |
|------|---------|----------|
| 200 | OK | Successful GET, PUT, PATCH |
| 201 | Created | Successful POST |
| 204 | No Content | Successful DELETE |
| 400 | Bad Request | Validation error |
| 401 | Unauthorized | Missing/invalid auth |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found | Resource not found |
| 409 | Conflict | Duplicate resource |
| 500 | Internal Server Error | Server error |

---

## State Management Selection

| Scope | Solution |
|-------|----------|
| Request-scoped | req object |
| Application-wide | Singleton/DI container |
| User session | Redis/database session store |
| Background jobs | Queue (BullMQ, Agenda) |

---

# Templates

See `assets/` directory for tech-stack-specific implementations, organized by language:

- `nodejs/template-nodejs-prisma-postgres.md` - Node.js + Express/Fastify/NestJS + Prisma + PostgreSQL
- `go/template-go-fiber-gorm.md` - Go + Fiber + GORM + PostgreSQL (high-performance, native concurrency)
- `rust/template-rust-axum-seaorm.md` - Rust + Axum + SeaORM + PostgreSQL (memory-safe, zero-cost abstractions)
- `python/template-python-fastapi-sqlalchemy.md` - Python + FastAPI + SQLAlchemy + PostgreSQL (ML/DS backends, async)

More templates can be added for other stacks (Java Spring Boot, Ruby Rails, C# ASP.NET Core, etc.)

---

---

## Pattern: Supabase Query Patterns

**Use when:** Building applications with Supabase as the backend.

**Critical Patterns:**

### Safe `.single()` Usage

The `.single()` method throws an error if no rows or multiple rows are returned. Always handle this properly:

```typescript
// BAD: BAD - No error handling, crashes on missing data
const { data } = await supabase.from('users').select().eq('id', id).single();

// GOOD: GOOD - Explicit error + null check
const { data: user, error } = await supabase
  .from('users')
  .select('*')
  .eq('id', id)
  .single();

if (error || !user) {
  return NextResponse.json({ error: 'User not found' }, { status: 404 });
}

// GOOD: ALTERNATIVE - Use .maybeSingle() for optional data
const { data: profile } = await supabase
  .from('profiles')
  .select('*')
  .eq('user_id', userId)
  .maybeSingle(); // Returns null instead of throwing if not found

if (!profile) {
  // Handle missing profile gracefully
}
```

### Null Safety for Optional Fields

```typescript
// BAD: BAD - Assumes subscription exists
const tier = subscription.tier;

// GOOD: GOOD - Always provide defaults
const tier = (subscription?.tier as SubscriptionTier) || 'free';

// GOOD: BETTER - Validate type before casting
const rawTier = subscription?.tier;
const tier: SubscriptionTier = isValidTier(rawTier) ? rawTier : 'free';
```

### Error Destructuring Pattern

```typescript
// BAD: BAD - Ignoring error
const { data } = await supabase.from('users').select();

// GOOD: GOOD - Always destructure error
const { data, error } = await supabase.from('users').select();
if (error) {
  logger.error({ error, context: 'users.list' }, 'Database query failed');
  throw new DatabaseError('Failed to fetch users');
}
```

### RLS-Aware Queries

```typescript
// BAD: BAD - Querying without considering RLS
const { data } = await supabase.from('private_data').select();

// GOOD: GOOD - Use service role only when needed
const supabaseAdmin = createClient(url, serviceRoleKey, {
  auth: { autoRefreshToken: false, persistSession: false }
});

// For user-scoped queries, use the user's JWT
const supabaseUser = createClient(url, anonKey, {
  global: { headers: { Authorization: `Bearer ${userToken}` } }
});
```

**Checklist:**
- [ ] Always destructure `{ data, error }` from queries
- [ ] Use `.maybeSingle()` for optional relationships
- [ ] Validate data exists before accessing properties
- [ ] Provide sensible defaults for optional fields
- [ ] Use service role key only for admin operations
- [ ] Log errors with context before re-throwing

---

## Pattern: Next.js API Request Validation

**Use when:** Building API routes in Next.js App Router.

**Safe JSON Parsing:**

```typescript
// BAD: BAD - Crashes on invalid JSON (returns 500 error)
export async function POST(request: Request) {
  const body = await request.json(); // Throws if body is not valid JSON
  // ...
}

// GOOD: GOOD - Graceful error handling
export async function POST(request: Request) {
  let body: unknown;
  try {
    body = await request.json();
  } catch {
    return NextResponse.json(
      { error: 'Invalid JSON body' },
      { status: 400 }
    );
  }

  // Then validate with Zod
  const result = requestSchema.safeParse(body);
  if (!result.success) {
    return NextResponse.json(
      { error: 'Validation failed', details: result.error.flatten() },
      { status: 400 }
    );
  }

  const validatedBody = result.data;
  // Now safe to use validatedBody
}
```

**Reusable Validation Helper:**

```typescript
// src/lib/api/validate.ts
import { z } from 'zod';
import { NextResponse } from 'next/server';

export async function parseRequestBody<T extends z.ZodSchema>(
  request: Request,
  schema: T
): Promise<{ data: z.infer<T>; error?: never } | { data?: never; error: NextResponse }> {
  let body: unknown;

  try {
    body = await request.json();
  } catch {
    return {
      error: NextResponse.json({ error: 'Invalid JSON body' }, { status: 400 })
    };
  }

  const result = schema.safeParse(body);
  if (!result.success) {
    return {
      error: NextResponse.json(
        { error: 'Validation failed', details: result.error.flatten() },
        { status: 400 }
      )
    };
  }

  return { data: result.data };
}

// Usage
export async function POST(request: Request) {
  const { data, error } = await parseRequestBody(request, createUserSchema);
  if (error) return error;

  // data is fully typed!
  const user = await createUser(data);
  return NextResponse.json(user, { status: 201 });
}
```

**Checklist:**
- [ ] Wrap `request.json()` in try-catch
- [ ] Return 400 for invalid JSON (not 500)
- [ ] Validate body shape with Zod after parsing
- [ ] Create reusable validation helper
- [ ] Include validation details in error response

---

## Pattern: Standardized API Error Responses

**Use when:** Building consistent API error handling across routes.

**Error Response Interface:**

```typescript
// src/lib/api/errors.ts
interface ApiErrorResponse {
  error: string;          // Human-readable message
  code?: string;          // Machine-readable code (e.g., 'USER_NOT_FOUND')
  details?: unknown;      // Additional context (validation errors, etc.)
}

// Error codes for client handling
const ErrorCodes = {
  VALIDATION_ERROR: 'VALIDATION_ERROR',
  NOT_FOUND: 'NOT_FOUND',
  UNAUTHORIZED: 'UNAUTHORIZED',
  FORBIDDEN: 'FORBIDDEN',
  RATE_LIMITED: 'RATE_LIMITED',
  INTERNAL_ERROR: 'INTERNAL_ERROR',
} as const;
```

**Consistent Error Helper:**

```typescript
// src/lib/api/responses.ts
import { NextResponse } from 'next/server';

export function apiError(
  message: string,
  status: number,
  code?: string,
  details?: unknown
) {
  return NextResponse.json(
    { error: message, ...(code && { code }), ...(details && { details }) },
    { status }
  );
}

// Convenience methods
export const errors = {
  badRequest: (msg: string, details?: unknown) =>
    apiError(msg, 400, 'VALIDATION_ERROR', details),
  unauthorized: (msg = 'Unauthorized') =>
    apiError(msg, 401, 'UNAUTHORIZED'),
  forbidden: (msg = 'Forbidden') =>
    apiError(msg, 403, 'FORBIDDEN'),
  notFound: (resource: string) =>
    apiError(`${resource} not found`, 404, 'NOT_FOUND'),
  rateLimited: () =>
    apiError('Too many requests', 429, 'RATE_LIMITED'),
  internal: (msg = 'Internal server error') =>
    apiError(msg, 500, 'INTERNAL_ERROR'),
};

// Usage
return errors.notFound('User');
return errors.badRequest('Invalid email format', { field: 'email' });
```

**HTTP Status Code Reference:**

| Scenario | Status | Code | Example |
|----------|--------|------|---------|
| Invalid input | 400 | VALIDATION_ERROR | Missing required field |
| Invalid JSON | 400 | VALIDATION_ERROR | Malformed request body |
| Not authenticated | 401 | UNAUTHORIZED | No/invalid token |
| Not authorized | 403 | FORBIDDEN | Can't access resource |
| Not found | 404 | NOT_FOUND | Entity doesn't exist |
| Rate limited | 429 | RATE_LIMITED | Too many requests |
| Server error | 500 | INTERNAL_ERROR | Unexpected exception |

**Checklist:**
- [ ] Use consistent error response shape
- [ ] Include error codes for client handling
- [ ] Create helper functions for common errors
- [ ] Never expose stack traces in production
- [ ] Log full error context server-side

---

## Pattern: Serverless Performance & Timeouts

**Use when:** Running Next.js API routes on Vercel or similar serverless platforms.

**Route Duration Configuration:**

```typescript
// Set explicit duration for slow routes (Next.js 14+)
export const maxDuration = 30; // seconds (max 60 on Pro, 300 on Enterprise)
export const dynamic = 'force-dynamic'; // Disable static optimization
```

**Timeout Prevention Strategies:**

```typescript
// 1. WRAP EXPENSIVE OPERATIONS WITH TIMEOUT
async function withTimeout<T>(
  promise: Promise<T>,
  ms: number,
  errorMessage = 'Operation timed out'
): Promise<T> {
  let timeoutId: NodeJS.Timeout;

  const timeoutPromise = new Promise<never>((_, reject) => {
    timeoutId = setTimeout(() => reject(new Error(errorMessage)), ms);
  });

  try {
    return await Promise.race([promise, timeoutPromise]);
  } finally {
    clearTimeout(timeoutId!);
  }
}

// Usage - leave 5 second buffer for response
const result = await withTimeout(expensiveCalculation(), 25000);

// 2. PRE-COMPUTE EXPENSIVE DATA VIA CRON
// Instead of calculating in real-time, use cron jobs
// vercel.json
{
  "crons": [{
    "path": "/api/cron/precompute",
    "schedule": "0 * * * *" // Every hour
  }]
}

// 3. PROGRESSIVE LOADING
export async function GET(request: Request) {
  // Return fast initial response
  const basicData = await getBasicData(); // < 1 second

  // Optionally include a flag indicating more data is computing
  return NextResponse.json({
    ...basicData,
    detailedDataLoading: true,
    detailedDataEndpoint: '/api/detailed-data'
  });
}

// 4. CACHING AT MULTIPLE LAYERS
// In-memory (fastest, single server)
const cache = new Map<string, { data: unknown; expires: number }>();

function getCached<T>(key: string, ttlMs: number, fn: () => Promise<T>): Promise<T> {
  const cached = cache.get(key);
  if (cached && cached.expires > Date.now()) {
    return Promise.resolve(cached.data as T);
  }

  return fn().then(data => {
    cache.set(key, { data, expires: Date.now() + ttlMs });
    return data;
  });
}
```

**Common Timeout Causes & Solutions:**

| Cause | Solution |
|-------|----------|
| N+1 database queries | Use joins or DataLoader pattern |
| External API calls | Add timeouts, use circuit breakers |
| Complex calculations | Pre-compute via cron, cache results |
| Large data processing | Stream responses, paginate |
| Cold starts | Use Vercel's warm function feature |

**Checklist:**
- [ ] Set `maxDuration` for known slow routes
- [ ] Add timeout wrapper to expensive operations
- [ ] Pre-compute expensive data via cron jobs
- [ ] Cache at multiple layers (memory, database, CDN)
- [ ] Monitor route durations in production
- [ ] Use streaming for large responses

---

# Resources

**Best Practices Guides** (`references/`)
- `backend-best-practices.md` - Node.js backend engineering patterns including:
  - Authentication & Authorization (JWT, OAuth2, sessions, RBAC)
  - Error Handling & Validation (custom errors, global handlers, Zod/Joi)
  - Database Patterns (repository, schema design, migrations, query optimization, transactions)
  - Performance & Caching (Redis, pagination, background jobs, horizontal scaling)
  - Testing (unit, integration, E2E, mocking, CI/CD)
  - Observability (logging, tracing, APM, error tracking)
- `go-best-practices.md` - Go-specific patterns including:
  - Effective Go idioms and project structure
  - Concurrency patterns (goroutines, channels, worker pools)
  - Error handling and panic recovery
  - HTTP server patterns with context
  - GORM database patterns and migrations
  - Testing with table-driven tests and httptest
  - Performance optimization and profiling
- `rust-best-practices.md` - Rust-specific patterns including:
  - Ownership, borrowing, and lifetimes
  - Error handling with Result/Option and thiserror
  - Async/await patterns with Tokio
  - Type system patterns (newtype, typestate, builder)
  - Axum web framework patterns
  - SeaORM entity definitions and queries
  - Testing with mock databases
- `python-best-practices.md` - Python-specific patterns including:
  - Type hints and MyPy static analysis
  - Async/await patterns with asyncio
  - FastAPI dependency injection and middleware
  - SQLAlchemy 2.0 async ORM patterns
  - Pydantic validation and serialization
  - Pytest fixtures and async testing
  - Performance optimization and caching
 - Security (OWASP Top 10, password security, rate limiting, CORS)

**External Documentation:**
See [data/sources.json](../data/sources.json) for official documentation links and learning resources.

---

# END
```
