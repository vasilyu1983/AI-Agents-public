# API Design Best Practices

Comprehensive guide to building scalable, maintainable, and developer-friendly APIs in 2025.

---

## Core Design Principles

### 1. Resource-Oriented Design (REST)

**Think Resources, Not Actions:**
- URLs represent resources (nouns), not operations (verbs)
- Use HTTP methods to express intent
- Keep URLs predictable and hierarchical

**Good Examples:**
```
GET    /api/v1/users              # List users
POST   /api/v1/users              # Create user
GET    /api/v1/users/123          # Get specific user
PUT    /api/v1/users/123          # Replace user
PATCH  /api/v1/users/123          # Update user
DELETE /api/v1/users/123          # Delete user

# Nested resources (max 2 levels)
GET    /api/v1/users/123/orders   # User's orders
POST   /api/v1/users/123/orders   # Create order for user
```

**Bad Examples:**
```
[FAIL] GET  /api/v1/getUser?id=123
[FAIL] POST /api/v1/createUser
[FAIL] GET  /api/v1/users/123/delete
[FAIL] GET  /api/v1/users/123/orders/456/items/789/reviews  # Too deep
```

### 2. HTTP Method Semantics

**Proper Method Usage:**

| Method | Purpose | Idempotent | Safe | Request Body | Response Body |
|--------|---------|------------|------|--------------|---------------|
| GET | Retrieve resource | Yes | Yes | No | Yes |
| POST | Create resource | No | No | Yes | Yes (created resource) |
| PUT | Replace entire resource | Yes | No | Yes | Yes (updated resource) |
| PATCH | Partial update | No | No | Yes | Yes (updated resource) |
| DELETE | Remove resource | Yes | No | Optional | Optional |
| HEAD | Get metadata only | Yes | Yes | No | No (headers only) |
| OPTIONS | Get allowed methods | Yes | Yes | No | Yes (capabilities) |

**Idempotency Importance:**
- GET, PUT, DELETE must produce same result on repeated calls
- POST creates new resource each time (not idempotent)
- Use PUT for full replacement, PATCH for partial updates

### 3. HTTP Status Codes

**2xx Success:**
```
200 OK                - Successful GET, PUT, PATCH, DELETE
201 Created           - Successful POST (include Location header)
202 Accepted          - Async operation started
204 No Content        - Successful DELETE with no response body
```

**4xx Client Errors:**
```
400 Bad Request       - Malformed syntax, invalid JSON
401 Unauthorized      - Authentication required or failed
403 Forbidden         - Authenticated but insufficient permissions
404 Not Found         - Resource doesn't exist
405 Method Not Allowed - HTTP method not supported for resource
409 Conflict          - Duplicate resource or state conflict
422 Unprocessable     - Validation error (semantically incorrect)
429 Too Many Requests - Rate limit exceeded
```

**5xx Server Errors:**
```
500 Internal Server   - Unexpected server error
502 Bad Gateway       - Upstream service error
503 Service Unavailable - Temporary downtime, maintenance
504 Gateway Timeout   - Upstream service timeout
```

---

## URL Design Patterns

### Naming Conventions

**Resource Names:**
- Use **plural nouns** for collections: `/users`, `/orders`, `/products`
- Use **lowercase** with hyphens (kebab-case): `/product-categories`
- Avoid underscores or camelCase in URLs
- Keep URLs concise (under 2048 characters)

**Query Parameters:**
```
# Filtering
GET /api/v1/users?status=active&role=admin
GET /api/v1/orders?created_after=2025-01-01&amount_gt=100

# Sorting
GET /api/v1/users?sort=created_at          # Ascending
GET /api/v1/users?sort=-created_at         # Descending (prefix -)
GET /api/v1/users?sort=last_name,first_name  # Multi-field

# Pagination
GET /api/v1/users?limit=20&offset=40       # Offset-based
GET /api/v1/users?limit=20&cursor=abc123   # Cursor-based

# Field selection (sparse fieldsets)
GET /api/v1/users?fields=id,name,email
GET /api/v1/users?include=orders,addresses  # Expand related resources
```

### Versioning in URLs

```
# Version in path (recommended)
https://api.example.com/v1/users
https://api.example.com/v2/users

# Version in subdomain
https://v1.api.example.com/users
https://v2.api.example.com/users
```

See [versioning-strategies.md](versioning-strategies.md) for full comparison.

---

## Response Design

### Standard Response Envelope

**Success Response (200/201):**
```json
{
  "data": {
    "id": "123",
    "email": "user@example.com",
    "name": "John Doe",
    "created_at": "2025-01-15T10:30:00Z"
  },
  "meta": {
    "timestamp": "2025-01-20T14:25:00Z"
  }
}
```

**Collection Response with Pagination:**
```json
{
  "data": [
    {"id": "1", "name": "User 1"},
    {"id": "2", "name": "User 2"}
  ],
  "meta": {
    "total": 1500,
    "limit": 20,
    "offset": 40,
    "hasMore": true
  },
  "links": {
    "self": "/api/v1/users?limit=20&offset=40",
    "next": "/api/v1/users?limit=20&offset=60",
    "prev": "/api/v1/users?limit=20&offset=20"
  }
}
```

**Error Response (4xx/5xx):**
```json
{
  "error": {
    "type": "https://api.example.com/errors/validation-error",
    "title": "Validation Error",
    "status": 422,
    "detail": "Email address is already registered",
    "instance": "/api/v1/users",
    "errors": [
      {
        "field": "email",
        "code": "DUPLICATE_EMAIL",
        "message": "Email address is already registered"
      }
    ],
    "traceId": "abc123-def456"
  }
}
```

See [RFC 9457 Problem Details](https://datatracker.ietf.org/doc/html/rfc9457) for error format standard (obsoletes RFC 7807).

---

## Data Formats

### JSON Best Practices

**Field Naming:**
- Use `snake_case` (recommended): `created_at`, `first_name`
- Or `camelCase` (JavaScript ecosystems): `createdAt`, `firstName`
- Be consistent across entire API

**Date/Time Format:**
- Use ISO 8601 format: `2025-01-20T14:25:00Z`
- Always include timezone (prefer UTC with Z suffix)
- For date-only: `2025-01-20`
- For time-only: `14:25:00`

**Null vs Omitted Fields:**
```json
# Option 1: Include null fields
{
  "name": "John Doe",
  "middle_name": null,
  "phone": null
}

# Option 2: Omit null fields (preferred for bandwidth)
{
  "name": "John Doe"
}
```

**Boolean Fields:**
```json
{
  "is_active": true,        // Prefix with "is_" or "has_"
  "has_verified_email": false,
  "can_edit": true
}
```

### Content Negotiation

**Request Headers:**
```http
Accept: application/json                          # JSON response
Accept: application/xml                           # XML response
Accept: application/vnd.api+json; version=2       # Custom MIME type
Accept-Language: en-US,en;q=0.9                   # Language preference
```

**Response Headers:**
```http
Content-Type: application/json; charset=utf-8
Content-Language: en-US
```

---

## Performance Optimization

### 1. Pagination

**Offset-Based (Simple but has limitations):**
```
GET /api/v1/users?limit=20&offset=40

Pros: Simple, allows jumping to any page
Cons: Performance degrades with large offsets, inconsistent if data changes
```

**Cursor-Based (Recommended for real-time data):**
```
GET /api/v1/users?limit=20&cursor=eyJpZCI6MTIzfQ

Pros: Consistent results, efficient for large datasets
Cons: Can't jump to arbitrary page
```

**Keyset Pagination (Best performance):**
```
GET /api/v1/users?limit=20&since_id=123

Pros: Fastest, most efficient database queries
Cons: Requires indexed sort field
```

### 2. Caching

**HTTP Cache Headers:**
```http
# Response headers
Cache-Control: public, max-age=3600                # Cache for 1 hour
Cache-Control: private, max-age=300                # User-specific, 5 min
Cache-Control: no-cache                            # Revalidate on each request
Cache-Control: no-store                            # Don't cache sensitive data
ETag: "686897696a7c876b7e"                         # Resource version
Last-Modified: Wed, 15 Jan 2025 10:30:00 GMT

# Conditional requests
If-None-Match: "686897696a7c876b7e"                # ETag validation
If-Modified-Since: Wed, 15 Jan 2025 10:30:00 GMT
```

**Cache Strategy:**
- Static resources: `Cache-Control: public, max-age=31536000, immutable`
- User data: `Cache-Control: private, max-age=300`
- Dynamic/realtime: `Cache-Control: no-cache` with ETags
- Sensitive data: `Cache-Control: no-store`

### 3. Compression

```http
# Request
Accept-Encoding: gzip, deflate, br

# Response
Content-Encoding: gzip
```

Enable compression for text-based responses (JSON, XML, HTML). Reduces bandwidth by 70-90%.

### 4. Field Selection

Allow clients to request only needed fields:
```
GET /api/v1/users?fields=id,name,email
```

Reduces response size and database load.

---

## Security Best Practices

### 1. HTTPS Only

- **Never** serve APIs over HTTP
- Redirect HTTP to HTTPS with 301
- Use TLS 1.3 (TLS 1.2 minimum)
- Implement HSTS header: `Strict-Transport-Security: max-age=31536000; includeSubDomains`

### 2. Authentication

**Bearer Tokens (Recommended):**
```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**API Keys (For server-to-server):**
```http
X-API-Key: your-api-key-here
```

**Basic Auth (Avoid for production):**
```http
Authorization: Basic dXNlcm5hbWU6cGFzc3dvcmQ=
```

See [api-security-checklist.md](api-security-checklist.md) for comprehensive security guide.

### 3. Rate Limiting

**Response Headers:**
```http
X-RateLimit-Limit: 1000           # Requests per window
X-RateLimit-Remaining: 987        # Requests left
X-RateLimit-Reset: 1640000060     # Window reset time (Unix timestamp)
```

**429 Response:**
```http
HTTP/1.1 429 Too Many Requests
Retry-After: 60

{
  "error": {
    "status": 429,
    "message": "Rate limit exceeded. Try again in 60 seconds."
  }
}
```

### 4. Input Validation

- Validate all input server-side
- Use allow-lists, not deny-lists
- Enforce length limits on strings
- Validate data types strictly
- Sanitize before database storage

---

## Documentation Best Practices

### OpenAPI Specification

**Benefits:**
- Auto-generated interactive docs
- Client SDK generation
- API testing tools integration
- Contract-first development

**Example:**
```yaml
openapi: 3.1.0
info:
  title: User API
  version: 1.0.0
paths:
  /users:
    get:
      summary: List users
      parameters:
        - name: limit
          in: query
          schema:
            type: integer
            default: 20
      responses:
        '200':
          description: Success
          content:
            application/json:
              schema:
                type: array
                items:
                  $ref: '#/components/schemas/User'
```

See [openapi-guide.md](openapi-guide.md) for full OpenAPI 3.1 reference.

### Developer Portal Must-Haves

1. **Getting Started Guide** - Quick 5-minute tutorial
2. **Authentication Guide** - How to get and use API keys/tokens
3. **Rate Limits** - Documented per tier
4. **Code Examples** - In multiple languages (curl, Python, JavaScript, etc.)
5. **Error Reference** - All error codes with solutions
6. **Changelog** - Version history with migration guides
7. **Interactive Playground** - Try API without coding

---

## REST vs GraphQL vs gRPC

| Aspect | REST | GraphQL | gRPC |
|--------|------|---------|------|
| **Best For** | Public APIs, CRUD operations | Complex queries, mobile apps | Microservices, high performance |
| **Learning Curve** | Low | Medium | High |
| **Caching** | Excellent (HTTP caching) | Challenging | None built-in |
| **Tooling** | Mature (OpenAPI, Postman) | Good (GraphiQL, Apollo) | Limited (mainly for Go, Java) |
| **Bandwidth** | Higher (can over-fetch) | Optimized (request exactly what's needed) | Most efficient (binary protocol) |
| **Versioning** | Required | Optional (evolving schema) | Required |
| **Browser Support** | Native | Native | Requires proxy (no HTTP/2) |
| **Real-time** | WebSockets/SSE | Subscriptions (native) | Streaming (native) |

**Choose REST when:**
- Building public APIs
- Simple CRUD operations
- Caching is critical
- Team is familiar with HTTP

**Choose GraphQL when:**
- Clients need flexible queries
- Mobile/web apps with varying data needs
- Rapid frontend iteration
- Multiple clients with different requirements

**Choose gRPC when:**
- Internal microservices
- High throughput required
- Strong typing needed
- Polyglot environment (multiple languages)

See [graphql-patterns.md](graphql-patterns.md) for GraphQL-specific guidance.

---

## Testing APIs

### Contract Testing

Use OpenAPI specs to validate API contracts:
```bash
# Dredd - API testing framework
dredd openapi.yaml https://api.example.com
```

### Load Testing

```bash
# Apache Bench
ab -n 10000 -c 100 https://api.example.com/users

# wrk
wrk -t12 -c400 -d30s https://api.example.com/users
```

### Security Testing

- OWASP ZAP - Automated security scans
- Burp Suite - Manual penetration testing
- Postman - API functional testing

---

## Common Anti-Patterns

### 1. Verbs in URLs
```
[FAIL] POST /api/v1/createUser
[OK] POST /api/v1/users
```

### 2. Ignoring HTTP Methods
```
[FAIL] GET /api/v1/users/123/delete
[OK] DELETE /api/v1/users/123
```

### 3. No Versioning
```
[FAIL] https://api.example.com/users  (no version)
[OK] https://api.example.com/v1/users
```

### 4. Inconsistent Naming
```
[FAIL] /api/v1/Users (capitalized)
[FAIL] /api/v1/user_profiles (mixed conventions)
[OK] /api/v1/users, /api/v1/user-profiles (consistent)
```

### 5. Missing Pagination
```
[FAIL] GET /api/v1/users  (returns all 1M users)
[OK] GET /api/v1/users?limit=20&offset=0
```

### 6. Exposing Internal IDs
```
[FAIL] Auto-incrementing IDs (predictable, leaks growth rate)
[OK] UUIDs or opaque tokens
```

### 7. Generic Error Messages
```
[FAIL] { "error": "Something went wrong" }
[OK] { "error": { "code": "DUPLICATE_EMAIL", "field": "email", "message": "..." } }
```

---

## Resources

**Official Standards:**
- [RFC 9457 - Problem Details](https://datatracker.ietf.org/doc/html/rfc9457)
- [RFC 6749 - OAuth 2.0](https://datatracker.ietf.org/doc/html/rfc6749)
- [RFC 7519 - JWT](https://datatracker.ietf.org/doc/html/rfc7519)

**Style Guides:**
- [Microsoft REST API Guidelines](https://github.com/microsoft/api-guidelines)
- [Google API Design Guide](https://cloud.google.com/apis/design)
- [Stripe API Design](https://stripe.com/docs/api)

**Books:**
- "API Design Patterns" by JJ Geewax (Manning)
- "RESTful Web API Patterns & Practices Cookbook" by Mike Amundsen (O'Reilly)

---

**Related Resources:**
- [OpenAPI 3.1 Guide](openapi-guide.md)
- [API Security Checklist](api-security-checklist.md)
- [GraphQL Patterns](graphql-patterns.md)
- [Versioning Strategies](versioning-strategies.md)
