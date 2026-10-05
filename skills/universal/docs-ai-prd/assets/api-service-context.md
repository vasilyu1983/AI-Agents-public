# API Service CLAUDE.md Template

Language-agnostic template for backend API services. Customize for your stack.

---

```markdown
# [Service Name] API

[One-line description of what this API does]

## Tech Stack

- **Language**: [TypeScript / Python / Go / Java / Rust]
- **Framework**: [Express / FastAPI / Gin / Spring Boot / Actix]
- **Database**: [PostgreSQL / MySQL / MongoDB] via [ORM/Driver]
- **Cache**: [Redis / Memcached / None]
- **Auth**: [JWT / OAuth2 / API Keys / Session]
- **API Style**: [REST / GraphQL / gRPC]

## API Overview

### Base URL

```
Production: https://api.example.com/v1
Staging:    https://api-staging.example.com/v1
Local:      http://localhost:3000/v1
```

### Authentication

```http
Authorization: Bearer <jwt_token>
# or
X-API-Key: <api_key>
```

### Rate Limits

| Tier | Requests/min | Burst |
|------|-------------|-------|
| Free | 60 | 10 |
| Pro | 600 | 100 |
| Enterprise | Custom | Custom |

## Architecture

[2-3 sentences describing the service design]

### Directory Structure

```
src/
├── api/              # HTTP layer
│   ├── routes/       # Route definitions
│   ├── handlers/     # Request handlers
│   ├── middleware/   # Auth, validation, logging
│   └── validators/   # Request validation schemas
├── services/         # Business logic
├── repositories/     # Data access
├── models/           # Domain entities
├── dto/              # Request/response objects
├── errors/           # Custom error types
├── config/           # Configuration
└── utils/            # Shared utilities
```

### Request Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                         HTTP Layer                               │
├──────────┬──────────┬──────────┬──────────┬─────────────────────┤
│  Router  │   Auth   │ Validate │  Rate    │      Handler        │
│          │ Middleware│ Middleware│ Limiter │                     │
└──────────┴──────────┴──────────┴──────────┴──────────┬──────────┘
                                                        │
                                                        ▼
┌─────────────────────────────────────────────────────────────────┐
│                       Service Layer                              │
│              (Business logic, orchestration)                     │
└──────────────────────────────────────────┬──────────────────────┘
                                           │
                                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                     Repository Layer                             │
│               (Database, cache, external APIs)                   │
└─────────────────────────────────────────────────────────────────┘
```

## Key Endpoints

### Users

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/users` | List users (paginated) | API Key |
| GET | `/users/:id` | Get user by ID | API Key |
| POST | `/users` | Create user | Admin |
| PATCH | `/users/:id` | Update user | Owner/Admin |
| DELETE | `/users/:id` | Delete user | Admin |

### [Other Resource]

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| ... | ... | ... | ... |

## Request/Response Patterns

### Success Response

```json
{
  "data": {
    "id": "123",
    "name": "Example"
  },
  "meta": {
    "requestId": "req_abc123"
  }
}
```

### Paginated Response

```json
{
  "data": [...],
  "meta": {
    "page": 1,
    "perPage": 20,
    "total": 100,
    "totalPages": 5
  }
}
```

### Error Response (RFC 7807)

```json
{
  "type": "https://api.example.com/errors/validation",
  "title": "Validation Error",
  "status": 400,
  "detail": "Email is required",
  "instance": "/users",
  "errors": [
    { "field": "email", "message": "Email is required" }
  ]
}
```

## Key Files

| Purpose | Location | Notes |
|---------|----------|-------|
| Entry point | `src/index.ts` | Server bootstrap |
| Routes | `src/api/routes/index.ts` | Route registration |
| Auth middleware | `src/api/middleware/auth.ts` | JWT/API key validation |
| Error handler | `src/api/middleware/error.ts` | Global error handling |
| Database client | `src/db/client.ts` | Connection pool |
| Config | `src/config/index.ts` | Environment loading |
| OpenAPI spec | `docs/openapi.yaml` | API documentation |

## Configuration

### Environment Variables

```bash
# .env.example
NODE_ENV=development
PORT=3000
DATABASE_URL=postgresql://user:pass@localhost:5432/db
REDIS_URL=redis://localhost:6379
JWT_SECRET=your-jwt-secret
JWT_EXPIRES_IN=7d
API_KEY_SALT=your-salt
LOG_LEVEL=debug
CORS_ORIGIN=http://localhost:3001
```

## Commands

```bash
# Development
npm run dev              # Start with hot reload

# Database
npm run db:migrate       # Run migrations
npm run db:seed          # Seed test data
npm run db:reset         # Reset database

# Testing
npm test                 # All tests
npm run test:unit        # Unit tests only
npm run test:integration # Integration tests
npm run test:e2e         # End-to-end API tests

# Documentation
npm run docs:generate    # Generate OpenAPI from code
npm run docs:serve       # Serve Swagger UI

# Quality
npm run lint             # ESLint
npm run typecheck        # Type checking
```

## Important Context

### Technical Decisions

#### [Why REST over GraphQL]
**Context**: Public API for external developers
**Decision**: REST for simplicity and cacheability
**Trade-off**: More endpoints, but easier to understand and cache

#### [Why JWT over sessions]
**Context**: Stateless API for horizontal scaling
**Decision**: JWT with short expiry + refresh tokens
**Trade-off**: Can't revoke instantly, but enables stateless auth

### Known Gotchas

- **Pagination cursor**: Use cursor-based pagination for large datasets, not offset
- **N+1 queries**: Always eager-load related entities in list endpoints
- **Timeout handling**: Set request timeout at 30s, database timeout at 10s
- **Idempotency**: POST requests with `Idempotency-Key` header for payment-like operations

### Historical Context

- [Any API version migrations, breaking changes, or legacy endpoints]

## Error Codes

| Code | HTTP Status | Description | Action |
|------|-------------|-------------|--------|
| `AUTH_INVALID_TOKEN` | 401 | JWT invalid or expired | Refresh token |
| `AUTH_FORBIDDEN` | 403 | Insufficient permissions | Check role |
| `RESOURCE_NOT_FOUND` | 404 | Resource doesn't exist | Verify ID |
| `VALIDATION_ERROR` | 400 | Invalid request body | Check errors[] |
| `RATE_LIMITED` | 429 | Too many requests | Wait and retry |
| `INTERNAL_ERROR` | 500 | Server error | Contact support |

## Testing

### API Test Example

```typescript
describe('POST /users', () => {
  it('creates user with valid input', async () => {
    const res = await request(app)
      .post('/v1/users')
      .set('Authorization', `Bearer ${adminToken}`)
      .send({ email: 'test@example.com', name: 'Test' });

    expect(res.status).toBe(201);
    expect(res.body.data).toMatchObject({
      email: 'test@example.com',
      name: 'Test',
    });
  });

  it('returns 400 for invalid email', async () => {
    const res = await request(app)
      .post('/v1/users')
      .set('Authorization', `Bearer ${adminToken}`)
      .send({ email: 'invalid', name: 'Test' });

    expect(res.status).toBe(400);
    expect(res.body.errors).toContainEqual(
      expect.objectContaining({ field: 'email' })
    );
  });
});
```

## For AI Assistants

### When modifying this API:

- Update OpenAPI spec for any endpoint changes
- Add request validation for all inputs
- Include error handling with appropriate error codes
- Write integration tests for new endpoints
- Follow existing response format patterns

### Patterns to follow:

- Validate all input at API boundary
- Use transactions for multi-step operations
- Log all requests with correlation ID
- Return consistent error format
- Version breaking changes (v1 → v2)

### Avoid:

- Business logic in handlers (use services)
- Direct database queries in handlers (use repositories)
- Exposing internal IDs (use UUIDs publicly)
- Silent failures (always log and respond)
- Breaking changes without version bump
```

---

## Quick Start Commands

Run these to gather API context:

```bash
# Find all routes
grep -rn "router\.\|app\.\(get\|post\|put\|patch\|delete\)" --include="*.ts" --include="*.js" --include="*.py" --include="*.go"

# Find OpenAPI spec
find . -name "openapi*" -o -name "swagger*"

# Check for validation
grep -rn "validate\|schema\|zod\|yup\|joi" --include="*.ts" --include="*.js"

# Find middleware
find . -name "*middleware*" -type f

# Check auth
grep -rn "jwt\|bearer\|apikey\|auth" -i --include="*.ts" --include="*.js" --include="*.py"
```
