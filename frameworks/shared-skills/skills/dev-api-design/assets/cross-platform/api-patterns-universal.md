# Universal API Design Patterns

Cross-framework patterns and best practices applicable to REST, GraphQL, and gRPC APIs regardless of implementation stack.

## Table of Contents

1. [Authentication Patterns](#authentication-patterns)
2. [Authorization Patterns](#authorization-patterns)
3. [Error Handling](#error-handling)
4. [Pagination Strategies](#pagination-strategies)
5. [Rate Limiting](#rate-limiting)
6. [Caching Strategies](#caching-strategies)
7. [API Versioning](#api-versioning)
8. [Input Validation](#input-validation)
9. [Response Formatting](#response-formatting)
10. [Performance Optimization](#performance-optimization)

---

## Authentication Patterns

### Pattern 1: JWT (JSON Web Tokens)

**Use when:** Stateless authentication needed, distributed systems, microservices

**Structure:**
```
Header.Payload.Signature
```

**Payload Example:**
```json
{
  "sub": "user-id",
  "email": "user@example.com",
  "role": "admin",
  "iat": 1640000000,
  "exp": 1640003600
}
```

**Best Practices:**
- Short access token lifetime (15-60 minutes)
- Long refresh token lifetime (7-30 days)
- Store refresh tokens securely (httpOnly cookies or secure storage)
- Rotate refresh tokens on each use
- Include minimal claims in payload
- Use strong signing algorithms (RS256, HS256)

**Security Checklist:**
- [ ] Token expiration enforced
- [ ] Signature verification on every request
- [ ] Sensitive data not in payload
- [ ] HTTPS only for token transmission
- [ ] Token revocation strategy implemented
- [ ] Rate limiting on token endpoints

### Pattern 2: OAuth 2.0 Flows

**Authorization Code Flow (Recommended for Web Apps):**
```
1. Client → Authorization Server: GET /authorize?client_id=...&redirect_uri=...&scope=...
2. User authenticates and grants permission
3. Authorization Server → Client: Redirect with authorization code
4. Client → Authorization Server: POST /token with code + client_secret
5. Authorization Server → Client: Access token + refresh token
6. Client → Resource Server: Request with Bearer token
```

**Client Credentials Flow (Service-to-Service):**
```
1. Service → Authorization Server: POST /token with client_id + client_secret
2. Authorization Server → Service: Access token
3. Service → API: Request with Bearer token
```

**Best Practices:**
- Use PKCE (Proof Key for Code Exchange) for public clients
- Implement state parameter for CSRF protection
- Store client secrets securely (never in frontend)
- Scope tokens to minimum required permissions
- Use short-lived access tokens with refresh rotation

### Pattern 3: API Key Authentication

**Use when:** Simple service-to-service communication, webhooks, public APIs with usage tracking

**Implementation Options:**

**Option 1: Header-based**
```http
GET /api/v1/resources
X-API-Key: your-api-key-here
```

**Option 2: Query parameter (not recommended for sensitive data)**
```http
GET /api/v1/resources?api_key=your-api-key-here
```

**Best Practices:**
- Generate cryptographically random keys (32+ characters)
- Support multiple keys per user/service
- Enable key rotation without downtime
- Track usage per API key
- Allow key expiration and revocation
- Never log API keys
- Store hashed versions only

**Rate Limiting Per Key:**
```
Free tier:     100 requests/hour
Paid tier:    1000 requests/hour
Enterprise:  10000 requests/hour
```

---

## Authorization Patterns

### Pattern 1: Role-Based Access Control (RBAC)

**Use when:** Fixed set of roles, hierarchical permissions

**Structure:**
```
User → Role → Permissions

Example:
- Admin: [read, write, delete, manage_users]
- Editor: [read, write]
- Viewer: [read]
```

**Implementation:**
```python
# Pseudocode
def check_permission(user, action, resource):
    user_roles = get_user_roles(user)
    required_permissions = get_required_permissions(action, resource)

    for role in user_roles:
        if role.has_permission(required_permissions):
            return True
    return False
```

**Best Practices:**
- Check permissions on every request
- Deny by default
- Least privilege principle
- Audit permission changes
- Cache role lookups

### Pattern 2: Attribute-Based Access Control (ABAC)

**Use when:** Complex, context-dependent permissions

**Policy Example:**
```json
{
  "policy": "Allow user to edit document if they are the owner OR they are in the same department AND document is not locked",
  "conditions": {
    "owner": "user.id == document.owner_id",
    "department": "user.department == document.department",
    "not_locked": "document.status != 'locked'"
  }
}
```

**Best Practices:**
- Define policies as code
- Cache policy evaluations
- Log policy decisions
- Test policies thoroughly

### Pattern 3: Resource-Based Authorization

**Use when:** Users own resources, multi-tenancy

**Check:**
```
if (resource.owner_id !== current_user.id && !current_user.is_admin) {
    throw Forbidden("Not authorized to access this resource");
}
```

**Multi-Tenancy Pattern:**
```sql
SELECT * FROM resources
WHERE tenant_id = :current_tenant_id
  AND (owner_id = :current_user_id OR is_public = true);
```

---

## Error Handling

### RFC 9457 Problem Details Format (Obsoletes RFC 7807)

**Standard Error Response:**
```json
{
  "type": "https://api.example.com/errors/validation-error",
  "title": "Validation Error",
  "status": 422,
  "detail": "Email address is already registered",
  "instance": "/api/v1/users",
  "code": "DUPLICATE_EMAIL",
  "retryable": false,
  "errors": [
    {
      "field": "email",
      "code": "DUPLICATE_EMAIL",
      "message": "Email address is already registered"
    }
  ],
  "traceId": "abc123def456"
}
```

### HTTP Status Code Guide

**Success (2xx):**
- `200 OK` - Successful GET, PUT, PATCH
- `201 Created` - Successful POST (include Location header)
- `204 No Content` - Successful DELETE or operation with no return

**Client Errors (4xx):**
- `400 Bad Request` - Malformed request syntax
- `401 Unauthorized` - Authentication required or failed
- `403 Forbidden` - Authenticated but insufficient permissions
- `404 Not Found` - Resource not found
- `409 Conflict` - Duplicate resource or state conflict
- `422 Unprocessable Entity` - Validation error
- `429 Too Many Requests` - Rate limit exceeded

**Server Errors (5xx):**
- `500 Internal Server Error` - Unexpected server error
- `502 Bad Gateway` - Upstream service error
- `503 Service Unavailable` - Temporary downtime
- `504 Gateway Timeout` - Upstream timeout

### Error Handling Best Practices

**Production vs Development:**
```javascript
if (environment === 'production') {
    return {
        status: 500,
        detail: "An unexpected error occurred"
    };
} else {
    return {
        status: 500,
        detail: error.message,
        stack: error.stack
    };
}
```

**Checklist:**
- [ ] Consistent error format across all endpoints
- [ ] Machine-readable error codes
- [ ] Human-readable messages
- [ ] Field-level validation errors
- [ ] Trace IDs for debugging
- [ ] No sensitive data in responses
- [ ] Different messages for dev vs prod

---

## Pagination Strategies

### Strategy 1: Offset-Based Pagination

**Use when:** Displaying page numbers, static data

**Request:**
```http
GET /api/v1/users?limit=20&offset=40
```

**Response:**
```json
{
  "data": [...],
  "meta": {
    "total": 1500,
    "limit": 20,
    "offset": 40,
    "hasMore": true,
    "totalPages": 75,
    "currentPage": 3
  }
}
```

**Pros:**
- Simple to implement
- Jump to any page
- Total count available

**Cons:**
- Performance degrades with large offsets
- Inconsistent results if data changes
- Not suitable for real-time feeds

### Strategy 2: Cursor-Based Pagination

**Use when:** Real-time data, infinite scroll, large datasets

**Request:**
```http
GET /api/v1/users?limit=20&cursor=eyJpZCI6MTIzLCJjcmVhdGVkX2F0IjoiMjAyNS0wMS0xNVQxMDowMDowMFoifQ==
```

**Response:**
```json
{
  "data": [...],
  "meta": {
    "nextCursor": "eyJpZCI6MTQzLCJjcmVhdGVkX2F0IjoiMjAyNS0wMS0xNVQxMTowMDowMFoifQ==",
    "hasMore": true
  }
}
```

**Cursor Structure (Base64 encoded):**
```json
{
  "id": 143,
  "created_at": "2025-01-15T11:00:00Z"
}
```

**SQL Implementation:**
```sql
SELECT * FROM users
WHERE (created_at, id) < (:cursor_created_at, :cursor_id)
ORDER BY created_at DESC, id DESC
LIMIT :limit;
```

**Pros:**
- Consistent results
- Excellent performance
- Real-time data support

**Cons:**
- Cannot jump to specific page
- No total count
- More complex implementation

### Strategy 3: Keyset Pagination

**Use when:** Efficient pagination on indexed columns

**Request:**
```http
GET /api/v1/users?limit=20&after_id=100
```

**SQL:**
```sql
SELECT * FROM users
WHERE id > :after_id
ORDER BY id
LIMIT :limit;
```

**Best Practices:**
- Default limit (e.g., 20)
- Maximum limit (e.g., 100)
- Include pagination metadata
- Document pagination strategy
- Validate cursor integrity
- Use indexed fields for cursors

---

## Rate Limiting

### Implementation Strategies

**1. Token Bucket Algorithm (Recommended)**

**Concept:**
- Bucket holds tokens
- Each request consumes a token
- Tokens refill at fixed rate
- Allows burst traffic

**Parameters:**
```
capacity: 100 tokens
refill_rate: 100 tokens/minute
```

**Headers:**
```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 73
X-RateLimit-Reset: 1640000060
Retry-After: 60
```

**429 Response:**
```json
{
  "type": "https://api.example.com/errors/rate-limit",
  "title": "Rate Limit Exceeded",
  "status": 429,
  "detail": "Too many requests",
  "retryAfter": 60
}
```

**2. Fixed Window Counter**

**Simple but less accurate:**
```
Window: 1 minute (00:00-00:59)
Max requests: 100
Reset: At minute boundary
```

**3. Sliding Window Log**

**Most accurate but memory-intensive:**
```
Track timestamp of each request
Count requests in last N seconds
Remove expired timestamps
```

### Tiered Rate Limits

```
Free tier:     100 requests/hour   (per API key)
Paid tier:    1000 requests/hour   (per API key)
Enterprise:  10000 requests/hour   (per API key)
Per IP:        60 requests/minute  (global)
```

### Best Practices

- [ ] Rate limit headers in all responses
- [ ] Different limits for different endpoints
- [ ] Per-user and per-IP limits
- [ ] Burst allowance for spiky traffic
- [ ] Graceful degradation
- [ ] Monitor and alert on limit hits
- [ ] Document limits clearly

---

## Caching Strategies

### HTTP Caching Headers

**Cache-Control:**
```http
Cache-Control: public, max-age=3600
Cache-Control: private, max-age=600
Cache-Control: no-cache
Cache-Control: no-store
```

**ETag (Entity Tag):**
```http
# Response
ETag: "33a64df551425fcc55e4d42a148795d9f25f89d4"
Cache-Control: max-age=3600

# Subsequent request
If-None-Match: "33a64df551425fcc55e4d42a148795d9f25f89d4"

# Response (if not modified)
HTTP/1.1 304 Not Modified
```

**Last-Modified:**
```http
# Response
Last-Modified: Wed, 15 Jan 2025 10:00:00 GMT

# Subsequent request
If-Modified-Since: Wed, 15 Jan 2025 10:00:00 GMT

# Response (if not modified)
HTTP/1.1 304 Not Modified
```

### Server-Side Caching

**1. Application Cache (Redis/Memcached)**

**Pattern:**
```python
cache_key = f"user:{user_id}"
cached_data = cache.get(cache_key)

if cached_data:
    return cached_data

data = database.query(user_id)
cache.set(cache_key, data, ttl=600)  # 10 minutes
return data
```

**2. Cache Invalidation Strategies**

**Time-based (TTL):**
```
cache.set(key, value, ttl=3600)
```

**Event-based:**
```python
def update_user(user_id, data):
    database.update(user_id, data)
    cache.delete(f"user:{user_id}")
```

**Cache-Aside Pattern:**
```
1. Check cache
2. If miss, query database
3. Store in cache
4. Return data
```

### Best Practices

- [ ] Cache immutable data aggressively
- [ ] Short TTL for frequently changing data
- [ ] Include cache headers in responses
- [ ] Invalidate cache on writes
- [ ] Monitor cache hit rates
- [ ] Use versioned cache keys
- [ ] Handle cache failures gracefully

---

## API Versioning

### Strategy 1: URL Versioning (Recommended)

**Example:**
```
/api/v1/users
/api/v2/users
```

**Pros:**
- Explicit and visible
- Easy to route
- Cache-friendly
- Browser-testable

**Cons:**
- URL proliferation
- Clients must update URLs

### Strategy 2: Header Versioning

**Example:**
```http
GET /api/users
Accept: application/vnd.api+json; version=2
```

**Pros:**
- Clean URLs
- Content negotiation

**Cons:**
- Less visible
- Harder to test

### Strategy 3: Query Parameter

**Example:**
```
/api/users?version=2
```

**Pros:**
- Simple
- Backward compatible

**Cons:**
- Pollutes query space
- Not RESTful

### Versioning Best Practices

- [ ] Version only on breaking changes
- [ ] Support N-1 versions (current + previous)
- [ ] Deprecation policy (6-12 months notice)
- [ ] Sunset headers for deprecated versions
- [ ] Migration guides documented
- [ ] Changelog maintained

**Sunset Header:**
```http
Sunset: Sat, 01 Jan 2026 00:00:00 GMT
Link: <https://api.example.com/docs/migration>; rel="deprecation"
```

---

## Input Validation

### Validation Layers

**1. Schema Validation (Structure)**
```json
{
  "email": "string, required, format: email",
  "age": "number, optional, min: 0, max: 150"
}
```

**2. Business Logic Validation**
```
- Email uniqueness
- Password strength
- Date range validity
- Referential integrity
```

### Validation Best Practices

**Whitelist vs Blacklist:**
```javascript
// Good: Whitelist
const allowedFields = ['name', 'email'];
const data = pick(request.body, allowedFields);

// Bad: Blacklist
const data = omit(request.body, ['admin', 'password_hash']);
```

**Sanitization:**
```javascript
const sanitized = {
    email: input.email.toLowerCase().trim(),
    name: stripHtml(input.name),
    age: parseInt(input.age)
};
```

**Error Messages:**
```json
{
  "errors": [
    {
      "field": "email",
      "code": "INVALID_FORMAT",
      "message": "Email must be a valid email address"
    },
    {
      "field": "password",
      "code": "TOO_SHORT",
      "message": "Password must be at least 8 characters"
    }
  ]
}
```

### Checklist

- [ ] Validate all inputs
- [ ] Fail fast (validate early)
- [ ] Specific error messages
- [ ] Sanitize before storage
- [ ] Reject unknown fields
- [ ] Type coercion documented
- [ ] Max request size enforced

---

## Response Formatting

### Consistent Response Structure

**Success Response:**
```json
{
  "data": {
    "id": "123",
    "name": "John Doe"
  }
}
```

**List Response:**
```json
{
  "data": [...],
  "meta": {
    "total": 1500,
    "limit": 20,
    "offset": 40
  }
}
```

**Error Response:**
```json
{
  "type": "https://api.example.com/errors/validation",
  "title": "Validation Error",
  "status": 422,
  "detail": "Request validation failed",
  "errors": [...]
}
```

### Field Naming Conventions

**camelCase (JavaScript/TypeScript):**
```json
{
  "userId": "123",
  "createdAt": "2025-01-15T10:00:00Z"
}
```

**snake_case (Python/Ruby):**
```json
{
  "user_id": "123",
  "created_at": "2025-01-15T10:00:00Z"
}
```

**Consistency is key** - choose one and stick with it.

### Date/Time Formatting

**Use ISO 8601:**
```json
{
  "created_at": "2025-01-15T10:30:00Z",
  "updated_at": "2025-01-15T14:30:00+02:00"
}
```

---

## Performance Optimization

### 1. Database Query Optimization

**N+1 Query Problem:**
```javascript
// Bad: N+1 queries
const users = await User.findAll();
for (const user of users) {
    user.orders = await Order.findByUserId(user.id);  // N queries
}

// Good: Join or eager loading
const users = await User.findAll({
    include: [{ model: Order }]  // 1 query
});
```

**Indexing:**
```sql
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_orders_user_id ON orders(user_id);
```

### 2. Response Compression

**Enable gzip/brotli:**
```http
Accept-Encoding: gzip, deflate, br
Content-Encoding: gzip
```

### 3. Field Selection

**Allow clients to request specific fields:**
```http
GET /api/v1/users?fields=id,name,email
```

**GraphQL approach:**
```graphql
{
  users {
    id
    name
    email
  }
}
```

### 4. Batch Endpoints

**Instead of:**
```http
GET /api/v1/users/1
GET /api/v1/users/2
GET /api/v1/users/3
```

**Use:**
```http
GET /api/v1/users?ids=1,2,3
```

### Checklist

- [ ] Database indexes on foreign keys
- [ ] Connection pooling configured
- [ ] Response compression enabled
- [ ] Slow query logging
- [ ] API response time monitoring
- [ ] Caching strategy implemented
- [ ] CDN for static assets

---

## Summary: Universal Best Practices

1. **Security First**: HTTPS, authentication, authorization, input validation
2. **Consistency**: Naming, error formats, response structures
3. **Documentation**: OpenAPI specs, examples, migration guides
4. **Performance**: Caching, indexing, pagination, compression
5. **Reliability**: Error handling, rate limiting, timeouts, retries
6. **Observability**: Logging, metrics, tracing, monitoring
7. **Versioning**: Clear strategy, deprecation policy, migration support
8. **Developer Experience**: Clear docs, predictable behavior, helpful errors
