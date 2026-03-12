# API Security Patterns — Comprehensive Guide (Jan 2026)

Practical API security patterns covering OWASP API Security Top 10 (2023), authorization vulnerabilities, rate limiting, API key management, and protocol-specific security for REST, GraphQL, and gRPC.

---

## OWASP API Security Top 10 (2023)

The OWASP API Security Top 10 focuses exclusively on API-specific risks. These are distinct from the general OWASP Top 10 and warrant separate treatment.

Reference: https://owasp.org/API-Security/editions/2023/en/0x11-t10/

| # | Risk | Description | Impact |
|---|------|-------------|--------|
| API1 | Broken Object Level Authorization (BOLA) | Attacker manipulates object IDs to access other users' data | Data breach, privacy violation |
| API2 | Broken Authentication | Weak auth mechanisms in APIs | Account takeover |
| API3 | Broken Object Property Level Authorization | Mass assignment and excessive data exposure | Data leak, privilege escalation |
| API4 | Unrestricted Resource Consumption | No rate limiting or resource caps | DoS, financial damage |
| API5 | Broken Function Level Authorization (BFLA) | Attacker calls admin/privileged endpoints | Privilege escalation |
| API6 | Unrestricted Access to Sensitive Business Flows | Automated abuse of business logic | Revenue loss, fraud |
| API7 | Server-Side Request Forgery (SSRF) | API fetches attacker-controlled URLs | Internal network access |
| API8 | Security Misconfiguration | Insecure defaults, verbose errors, CORS | Information disclosure |
| API9 | Improper Inventory Management | Undocumented or deprecated endpoints exposed | Shadow API exploitation |
| API10 | Unsafe Consumption of APIs | Blindly trusting third-party API responses | Injection, data corruption |

---

## BOLA — Broken Object Level Authorization

BOLA (API1) is the most prevalent and most exploited API vulnerability. It occurs when an API endpoint accepts an object identifier from the client but does not verify that the authenticated user is authorized to access that specific object.

### Detection Patterns

```text
BOLA indicators:
  ├─ Endpoint uses client-supplied IDs: /api/users/{id}/orders
  ├─ ID is sequential or predictable (integer auto-increment)
  ├─ No server-side ownership check against authenticated user
  ├─ Response includes data from other users when ID is changed
  └─ Horizontal privilege escalation succeeds with modified IDs
```

### Vulnerable Code

```javascript
// VULNERABLE: No ownership check
app.get('/api/orders/:orderId', authenticate, async (req, res) => {
  const order = await Order.findById(req.params.orderId);
  res.json(order); // Any authenticated user can view any order
});
```

### Secure Code

```javascript
// SECURE: Ownership verification
app.get('/api/orders/:orderId', authenticate, async (req, res) => {
  const order = await Order.findOne({
    _id: req.params.orderId,
    userId: req.user.id  // Scoped to authenticated user
  });
  if (!order) {
    return res.status(404).json({ error: 'Order not found' });
  }
  res.json(order);
});
```

### Prevention Checklist

- [ ] Every data-access query includes the authenticated user's context
- [ ] Use UUIDs instead of sequential IDs for external-facing identifiers
- [ ] Implement authorization middleware that checks object ownership
- [ ] Write integration tests that attempt cross-user object access
- [ ] Use database-level row security (PostgreSQL RLS) as defense in depth

---

## BFLA — Broken Function Level Authorization

BFLA (API5) occurs when users can invoke API functions beyond their privilege level, typically accessing admin or privileged operations.

### Common Patterns

| Pattern | Example | Risk |
|---------|---------|------|
| Predictable admin paths | `GET /api/admin/users` accessible to regular users | Full admin access |
| HTTP method confusion | `GET /api/users` allowed, but `DELETE /api/users/123` not checked | Data deletion |
| Role parameter tampering | `POST /api/users { "role": "admin" }` accepted | Privilege escalation |
| Hidden endpoints | Undocumented `/api/internal/migrate` exposed | System compromise |

### Prevention Architecture

```javascript
// Middleware-based BFLA prevention
const authorize = (...requiredRoles) => {
  return (req, res, next) => {
    if (!req.user) {
      return res.status(401).json({ error: 'Authentication required' });
    }
    if (!requiredRoles.includes(req.user.role)) {
      // Log the attempt for security monitoring
      logger.warn('BFLA attempt', {
        userId: req.user.id,
        role: req.user.role,
        requiredRoles,
        endpoint: req.originalUrl,
        method: req.method
      });
      return res.status(403).json({ error: 'Insufficient permissions' });
    }
    next();
  };
};

// Apply to routes
app.delete('/api/users/:id', authenticate, authorize('admin'), deleteUser);
app.post('/api/users/bulk-import', authenticate, authorize('admin'), bulkImport);
app.get('/api/users/me', authenticate, authorize('user', 'admin'), getProfile);
```

### BFLA Testing Strategy

```text
For each endpoint:
  1. Call as unauthenticated user → expect 401
  2. Call as lowest-privilege role → expect 403 for privileged operations
  3. Call with each role → verify correct access matrix
  4. Call with expired/invalid token → expect 401
  5. Call admin endpoints with regular user token → expect 403
```

---

## Mass Assignment Protection

Mass assignment (part of API3) occurs when an API binds client-supplied data directly to internal models, allowing attackers to set fields they should not control.

### Vulnerable Pattern

```javascript
// VULNERABLE: Binds all request fields to model
app.put('/api/users/:id', authenticate, async (req, res) => {
  const user = await User.findByIdAndUpdate(req.params.id, req.body);
  // Attacker sends: { "name": "Hacker", "role": "admin", "verified": true }
  res.json(user);
});
```

### Secure Pattern — Allowlist

```javascript
// SECURE: Explicit field allowlist
app.put('/api/users/:id', authenticate, async (req, res) => {
  const allowedFields = ['name', 'email', 'avatar', 'preferences'];
  const updates = {};
  for (const field of allowedFields) {
    if (req.body[field] !== undefined) {
      updates[field] = req.body[field];
    }
  }
  const user = await User.findOneAndUpdate(
    { _id: req.params.id, _id: req.user.id }, // ownership check
    updates,
    { new: true, runValidators: true }
  );
  res.json(user);
});
```

### DTOs and Schema Validation

```typescript
// Zod schema as DTO (TypeScript)
import { z } from 'zod';

const UpdateUserSchema = z.object({
  name: z.string().min(1).max(100).optional(),
  email: z.string().email().optional(),
  avatar: z.string().url().optional(),
  preferences: z.object({
    theme: z.enum(['light', 'dark']).optional(),
    language: z.string().length(2).optional()
  }).optional()
});
// Fields like 'role', 'verified', 'isAdmin' are excluded by schema design

app.put('/api/users/:id', authenticate, async (req, res) => {
  const validated = UpdateUserSchema.parse(req.body);
  // Only validated fields reach the database
});
```

---

## Rate Limiting Strategies

Rate limiting (API4) prevents abuse, DoS, and brute-force attacks. Choose the strategy based on your API's threat model.

### Strategy Comparison

| Strategy | How It Works | Best For | Drawback |
|----------|-------------|----------|----------|
| **Fixed window** | Count requests per time window (e.g., 100/min) | Simple APIs | Burst at window boundary |
| **Sliding window** | Rolling time window | General use | Moderate memory |
| **Token bucket** | Tokens replenish at fixed rate, requests consume tokens | Bursty traffic | Implementation complexity |
| **Leaky bucket** | Requests processed at fixed rate, excess queued/dropped | Smooth throughput | Latency for queued requests |
| **Per-user** | Limits scoped to authenticated user | Authenticated APIs | Requires user identification |
| **Per-endpoint** | Different limits per route | Mixed-criticality APIs | Configuration overhead |

### Implementation — Express.js

```javascript
import rateLimit from 'express-rate-limit';
import RedisStore from 'rate-limit-redis';
import Redis from 'ioredis';

const redis = new Redis(process.env.REDIS_URL);

// General API rate limit
const generalLimiter = rateLimit({
  store: new RedisStore({ sendCommand: (...args) => redis.call(...args) }),
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 100,                   // 100 requests per window
  standardHeaders: true,      // RateLimit-* headers (RFC 6585)
  legacyHeaders: false,
  keyGenerator: (req) => req.user?.id || req.ip,
  message: { error: 'Rate limit exceeded', retryAfter: '15 minutes' }
});

// Strict limit for auth endpoints
const authLimiter = rateLimit({
  store: new RedisStore({ sendCommand: (...args) => redis.call(...args) }),
  windowMs: 15 * 60 * 1000,
  max: 5,                     // 5 attempts per 15 minutes
  keyGenerator: (req) => req.ip,
  skipSuccessfulRequests: true // Only count failures
});

app.use('/api/', generalLimiter);
app.use('/api/auth/login', authLimiter);
app.use('/api/auth/reset-password', authLimiter);
```

### Rate Limit Headers (RFC 6585 / Draft RFC 9110)

```text
RateLimit-Limit: 100
RateLimit-Remaining: 42
RateLimit-Reset: 1672531200
Retry-After: 900
```

Always return these headers so clients can self-regulate.

---

## API Key Management

API keys are low-assurance credentials suitable for machine-to-machine communication, developer access, and usage tracking. They are not a substitute for user authentication.

### Lifecycle

| Phase | Best Practice |
|-------|--------------|
| **Generation** | Cryptographically random, 32+ bytes, prefix for identification (e.g., `sk_live_`, `pk_test_`) |
| **Storage** | Hash keys server-side (SHA-256 minimum); store only the hash + metadata |
| **Scoping** | Assign minimum permissions; scope to specific endpoints, methods, and IP ranges |
| **Distribution** | Show key once at creation; require re-generation, never email or log |
| **Rotation** | Support overlapping validity; old key works during grace period |
| **Revocation** | Immediate invalidation; audit log entry; notify key owner |
| **Monitoring** | Alert on unusual patterns: geographic anomaly, rate spike, scope violation |

### Key Generation Example

```javascript
import crypto from 'crypto';

function generateApiKey(environment = 'live') {
  const prefix = environment === 'live' ? 'sk_live_' : 'sk_test_';
  const key = crypto.randomBytes(32).toString('base64url');
  const fullKey = `${prefix}${key}`;

  // Store only the hash
  const hash = crypto.createHash('sha256').update(fullKey).digest('hex');

  return {
    key: fullKey,       // Show to user once
    hash: hash,         // Store in database
    prefix: prefix,
    lastFour: key.slice(-4),
    createdAt: new Date(),
    expiresAt: new Date(Date.now() + 365 * 24 * 60 * 60 * 1000) // 1 year
  };
}
```

### Key Validation Middleware

```javascript
async function validateApiKey(req, res, next) {
  const apiKey = req.headers['x-api-key'];
  if (!apiKey) return res.status(401).json({ error: 'API key required' });

  const hash = crypto.createHash('sha256').update(apiKey).digest('hex');
  const keyRecord = await ApiKey.findOne({ hash, revoked: false });

  if (!keyRecord) return res.status(401).json({ error: 'Invalid API key' });
  if (keyRecord.expiresAt < new Date()) {
    return res.status(401).json({ error: 'API key expired' });
  }

  // Check IP allowlist if configured
  if (keyRecord.allowedIps?.length && !keyRecord.allowedIps.includes(req.ip)) {
    logger.warn('API key used from unauthorized IP', { keyId: keyRecord.id, ip: req.ip });
    return res.status(403).json({ error: 'IP not authorized' });
  }

  req.apiKey = keyRecord;
  next();
}
```

---

## GraphQL-Specific Security

GraphQL introduces unique security concerns not present in REST APIs: query complexity attacks, introspection exposure, and batching abuse.

### Query Depth and Complexity Limiting

```javascript
import depthLimit from 'graphql-depth-limit';
import { createComplexityLimitRule } from 'graphql-validation-complexity';

const server = new ApolloServer({
  typeDefs,
  resolvers,
  validationRules: [
    depthLimit(5),  // Max nesting depth
    createComplexityLimitRule(1000, {
      scalarCost: 1,
      objectCost: 2,
      listFactor: 10   // Lists multiply cost
    })
  ]
});
```

### Field-Level Authorization

```javascript
// Directive-based auth
const typeDefs = gql`
  directive @auth(requires: Role = ADMIN) on FIELD_DEFINITION

  enum Role { USER ADMIN SUPERADMIN }

  type User {
    id: ID!
    name: String!
    email: String! @auth(requires: USER)
    ssn: String @auth(requires: ADMIN)
    internalNotes: String @auth(requires: SUPERADMIN)
  }
`;
```

### Introspection Control

```javascript
// Disable introspection in production
const server = new ApolloServer({
  typeDefs,
  resolvers,
  introspection: process.env.NODE_ENV !== 'production',
  plugins: [
    process.env.NODE_ENV === 'production'
      ? ApolloServerPluginLandingPageDisabled()
      : ApolloServerPluginLandingPageLocalDefault()
  ]
});
```

### GraphQL Security Checklist

| Concern | Control | Implementation |
|---------|---------|----------------|
| Query depth attack | Depth limiting | `graphql-depth-limit` (max 5-7) |
| Query complexity attack | Cost analysis | Assign cost per field and list multiplier |
| Batching abuse | Query count limit | Max 5-10 operations per request |
| Introspection leak | Disable in production | `introspection: false` |
| Persisted queries | Allowlisted queries only | Automatic Persisted Queries (APQ) |
| Field-level auth | Directive or middleware | `@auth` directive on sensitive fields |
| Error information leak | Error masking | Custom `formatError` in production |
| N+1 data loading | DataLoader | Batch and cache resolver calls |

---

## gRPC Security

gRPC uses HTTP/2 and Protocol Buffers, requiring specific security patterns.

### Mutual TLS (mTLS)

```javascript
// Node.js gRPC server with mTLS
const grpc = require('@grpc/grpc-js');
const fs = require('fs');

const serverCredentials = grpc.ServerCredentials.createSsl(
  fs.readFileSync('ca.pem'),           // CA certificate
  [{
    cert_chain: fs.readFileSync('server.pem'),  // Server certificate
    private_key: fs.readFileSync('server-key.pem')
  }],
  true  // Request client certificate (mutual TLS)
);

const server = new grpc.Server();
server.addService(MyService, implementation);
server.bindAsync('0.0.0.0:50051', serverCredentials, () => {
  server.start();
});
```

### Interceptors for Auth

```javascript
// Server-side unary interceptor for token validation
function authInterceptor(call, callback, next) {
  const metadata = call.metadata.get('authorization');
  if (!metadata.length) {
    callback({
      code: grpc.status.UNAUTHENTICATED,
      message: 'Missing authorization token'
    });
    return;
  }

  try {
    const token = metadata[0].replace('Bearer ', '');
    const decoded = jwt.verify(token, process.env.JWT_SECRET);
    call.user = decoded;
    next(call, callback);
  } catch (err) {
    callback({
      code: grpc.status.UNAUTHENTICATED,
      message: 'Invalid token'
    });
  }
}
```

### Deadline Propagation

```javascript
// Client: Set deadline to prevent hung requests
const deadline = new Date();
deadline.setSeconds(deadline.getSeconds() + 5); // 5-second deadline

client.getUser({ id: '123' }, { deadline }, (err, response) => {
  if (err?.code === grpc.status.DEADLINE_EXCEEDED) {
    console.error('Request timed out');
  }
});

// Server: Check deadline before expensive operations
function getUser(call, callback) {
  if (call.getDeadline() < new Date()) {
    callback({ code: grpc.status.DEADLINE_EXCEEDED });
    return;
  }
  // Proceed with operation
}
```

---

## API Versioning Security Implications

Versioning introduces security risks when old API versions remain accessible.

### Version Deprecation Security

| Risk | Description | Mitigation |
|------|-------------|------------|
| Zombie APIs | Old versions with known vulnerabilities still serve traffic | Enforce sunset headers and deadlines |
| Auth bypass | V1 has weaker auth than V2 | Apply current auth policy to all versions |
| Missing patches | Security fixes applied to V3 but not V2 | Backport critical patches or force migration |
| Schema drift | V1 returns fields removed from V2 for security | Audit response schemas across versions |

### Sunset Header Implementation

```javascript
// Middleware for deprecated API versions
function apiVersionMiddleware(req, res, next) {
  const version = req.headers['api-version'] || 'v3';

  const deprecatedVersions = {
    'v1': '2026-06-01',
    'v2': '2026-12-01'
  };

  if (deprecatedVersions[version]) {
    res.set('Sunset', new Date(deprecatedVersions[version]).toUTCString());
    res.set('Deprecation', 'true');
    res.set('Link', '</api/v3/docs>; rel="successor-version"');
  }

  next();
}
```

---

## OpenAPI/Swagger Security Definitions

Define security requirements in your API specification to ensure consistent enforcement and documentation.

```yaml
# openapi.yaml
openapi: 3.1.0
info:
  title: My API
  version: 3.0.0

components:
  securitySchemes:
    BearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT
    ApiKeyAuth:
      type: apiKey
      in: header
      name: X-API-Key
    OAuth2:
      type: oauth2
      flows:
        authorizationCode:
          authorizationUrl: https://auth.example.com/authorize
          tokenUrl: https://auth.example.com/token
          scopes:
            read:users: Read user data
            write:users: Create and update users
            admin: Full administrative access

security:
  - BearerAuth: []   # Default: all endpoints require Bearer token

paths:
  /users/{id}:
    get:
      security:
        - BearerAuth: []
        - OAuth2: [read:users]
      # ...
    delete:
      security:
        - OAuth2: [admin]
      # ...
  /public/health:
    get:
      security: []   # Explicitly no auth required
```

---

## Anti-Patterns

| Anti-Pattern | Why It Fails | Correct Approach |
|-------------|-------------|------------------|
| Auth check only at gateway | Internal services trust each other blindly | Zero-trust: verify at every service boundary |
| Sequential integer IDs in URLs | Enumeration attacks trivial | UUIDs for external-facing identifiers |
| Trusting `Content-Type` header | Attacker sends malicious payload with legitimate type | Validate actual content, not just headers |
| Same rate limit for all endpoints | Auth endpoints get same limit as read endpoints | Tiered rate limiting by endpoint sensitivity |
| Logging full request/response bodies | PII and secrets in logs | Structured logging with field-level redaction |
| API keys as sole authentication | No user context, no MFA, no expiry | API keys for identification; OAuth/JWT for authentication |
| No request size limits | Memory exhaustion attacks | `express.json({ limit: '1mb' })` per endpoint |
| Ignoring `Accept` header | Unexpected response format leaks data | Enforce `Content-Type` negotiation |

---

## Decision Framework: Choosing API Auth

```text
What kind of API consumer?
  ├─ Browser (SPA/web app)
  │   └─ OAuth 2.1 + PKCE with short-lived tokens
  ├─ Mobile app
  │   └─ OAuth 2.1 + PKCE (app-claimed HTTPS scheme)
  ├─ Server-to-server (your own services)
  │   └─ mTLS or OAuth 2.1 client credentials
  ├─ Third-party developer
  │   └─ OAuth 2.1 + scoped API keys for identification
  ├─ Webhook receiver
  │   └─ HMAC signature verification
  └─ Public read-only
      └─ API key (usage tracking) + aggressive rate limiting
```

---

## References

- [OWASP API Security Top 10 (2023)](https://owasp.org/API-Security/editions/2023/en/0x11-t10/)
- [OWASP API Security Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/REST_Security_Cheat_Sheet.html)
- [GraphQL Security Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/GraphQL_Cheat_Sheet.html)
- [RFC 6585 — Additional HTTP Status Codes (429 Too Many Requests)](https://www.rfc-editor.org/rfc/rfc6585)
- [gRPC Authentication Guide](https://grpc.io/docs/guides/auth/)

---

## Cross-References

- [SKILL.md](../SKILL.md) — Parent skill overview and decision tree
- [authentication-authorization.md](authentication-authorization.md) — AuthN/AuthZ flows, OAuth 2.1, JWT patterns
- [input-validation.md](input-validation.md) — Request validation and injection prevention
- [owasp-top-10.md](owasp-top-10.md) — OWASP Top 10:2025 general web application risks
- [zero-trust-architecture.md](zero-trust-architecture.md) — Zero-trust principles for service-to-service auth
