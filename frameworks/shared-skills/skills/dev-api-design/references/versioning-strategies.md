# API Versioning Strategies

Comprehensive guide to versioning REST APIs, managing breaking changes, and migrating clients safely.

---

## Why Version APIs?

**Breaking changes include:**
- Removing or renaming fields
- Changing field types (`string` → `number`)
- Changing response structure
- Adding required request parameters
- Removing endpoints
- Changing error response formats

**Non-breaking changes (no version needed):**
- Adding optional fields to responses
- Adding optional request parameters
- Adding new endpoints
- Deprecating (but not removing) fields
- Expanding enum values (if clients ignore unknowns)

---

## Versioning Strategies

### 1. URL Path Versioning (Recommended)

**Format:**
```
https://api.example.com/v1/users
https://api.example.com/v2/users
```

**Pros:**
- [OK] Explicit and visible
- [OK] Easy to route at load balancer/gateway level
- [OK] Works in browser (easy to test with curl)
- [OK] Cache-friendly (different URLs = different cache keys)
- [OK] Most widely adopted (Stripe, GitHub, Twitter)

**Cons:**
- [FAIL] URL proliferation over time
- [FAIL] Clients must update URLs when migrating

**Implementation (Express.js):**
```javascript
// Router per version
const v1Router = express.Router();
const v2Router = express.Router();

v1Router.get('/users', getUsersV1);
v2Router.get('/users', getUsersV2);

app.use('/api/v1', v1Router);
app.use('/api/v2', v2Router);
```

**Migration Example:**
```javascript
// v1: Returns array
app.get('/api/v1/users', (req, res) => {
  const users = await User.find();
  res.json(users);  // [{ id: 1, name: "..." }]
});

// v2: Returns envelope with pagination
app.get('/api/v2/users', (req, res) => {
  const users = await User.find().limit(20);
  res.json({
    data: users,
    meta: { total: 1000, page: 1 }
  });
});
```

---

### 2. Header Versioning

**Format:**
```http
GET /api/users HTTP/1.1
Host: api.example.com
Accept: application/vnd.api+json; version=1
API-Version: 1
```

**Pros:**
- [OK] Clean URLs (no version in path)
- [OK] RESTful (uses content negotiation)
- [OK] Multiple versions on same URL

**Cons:**
- [FAIL] Less visible (hidden in headers)
- [FAIL] Harder to test in browser
- [FAIL] Requires middleware to parse headers
- [FAIL] Caching complexity (must include `Vary: API-Version` header)

**Implementation (Express.js):**
```javascript
const parseVersion = (req, res, next) => {
  req.apiVersion = req.headers['api-version'] || '1';
  next();
};

app.get('/api/users', parseVersion, (req, res) => {
  if (req.apiVersion === '2') {
    return getUsersV2(req, res);
  }
  return getUsersV1(req, res);
});

// IMPORTANT: Add Vary header for caching
res.setHeader('Vary', 'API-Version');
```

---

### 3. Query Parameter Versioning

**Format:**
```
https://api.example.com/users?version=1
https://api.example.com/users?v=2
```

**Pros:**
- [OK] Simple to implement
- [OK] Backward compatible (default version if not specified)
- [OK] Easy to test

**Cons:**
- [FAIL] Pollutes query parameter space
- [FAIL] Not RESTful (version is not a filter)
- [FAIL] Caching complexity (must vary on query param)

**Implementation:**
```javascript
app.get('/api/users', (req, res) => {
  const version = req.query.version || '1';

  if (version === '2') {
    return getUsersV2(req, res);
  }
  return getUsersV1(req, res);
});
```

---

### 4. Content Negotiation (Media Type Versioning)

**Format:**
```http
Accept: application/vnd.example.v1+json
Accept: application/vnd.example.v2+json
```

**Pros:**
- [OK] Most RESTful approach
- [OK] Fine-grained versioning (per resource)
- [OK] Follows HTTP standards

**Cons:**
- [FAIL] Complex to implement
- [FAIL] Poor tooling support
- [FAIL] Difficult to test manually
- [FAIL] Rarely used in practice

**Implementation:**
```javascript
app.get('/api/users', (req, res) => {
  const accept = req.headers['accept'];

  if (accept.includes('application/vnd.example.v2+json')) {
    res.setHeader('Content-Type', 'application/vnd.example.v2+json');
    return getUsersV2(req, res);
  }

  res.setHeader('Content-Type', 'application/vnd.example.v1+json');
  return getUsersV1(req, res);
});
```

---

### 5. Subdomain Versioning

**Format:**
```
https://v1.api.example.com/users
https://v2.api.example.com/users
```

**Pros:**
- [OK] Clean URLs
- [OK] Easy to route to different servers
- [OK] DNS-level routing

**Cons:**
- [FAIL] Requires DNS configuration
- [FAIL] SSL certificate for each subdomain
- [FAIL] Organizational overhead

---

## Choosing a Strategy

| Strategy | Adoption | Complexity | Testability | Best For |
|----------|----------|------------|-------------|----------|
| **URL Path** | [STAR][STAR][STAR][STAR][STAR] | Low | Easy | Public APIs, recommended for most cases |
| **Header** | [STAR][STAR][STAR] | Medium | Hard | Internal APIs, API gateways |
| **Query Param** | [STAR][STAR] | Low | Easy | Simple APIs, backward compat focus |
| **Media Type** | [STAR] | High | Hard | Hypermedia APIs (rare) |
| **Subdomain** | [STAR][STAR] | High | Easy | Large-scale systems with separate infra |

**Recommendation:** Use **URL Path Versioning** unless you have specific constraints. It's the industry standard and balances simplicity with explicitness.

---

## Versioning Best Practices

### 1. Version Only Breaking Changes

**Don't increment version for:**
- Adding new endpoints
- Adding optional fields to requests/responses
- Adding new error codes
- Improving performance

**Do increment version for:**
- Removing fields
- Changing field types
- Renaming fields
- Changing required fields
- Changing response structure

### 2. Use Semantic Versioning

**Format:** `v{major}.{minor}.{patch}` or just `v{major}` for public APIs

```
v1.0.0 → v1.1.0  (new features, backward compatible)
v1.1.0 → v1.1.1  (bug fixes, backward compatible)
v1.1.1 → v2.0.0  (breaking changes)
```

**Public APIs:** Only expose major version (`/v1`, `/v2`)
**Internal APIs:** Full semantic versioning (`/v1.2.3`)

### 3. Document Breaking Changes

**Changelog Example:**
```markdown
## v2.0.0 (2025-01-20)

### Breaking Changes
- `GET /users` now returns paginated response with envelope
  - Before: `[{ id: 1, name: "..." }]`
  - After: `{ data: [...], meta: { total: 1000 } }`
- Removed deprecated `phone` field (use `phone_number` instead)
- Changed `created` field from Unix timestamp to ISO 8601

### Migration Guide
1. Update response parsing to handle `data` envelope
2. Replace `phone` references with `phone_number`
3. Parse dates as ISO 8601 instead of Unix timestamps
```

### 4. Support N-1 Versions (Minimum)

**Example:**
- Current version: v3
- Supported versions: v2, v3
- Deprecated: v1 (sunset date: 2025-06-01)

**Timeline:**
```
2024-01-01: v1 released
2024-07-01: v2 released (v1 still supported)
2025-01-01: v3 released (v1 deprecated, v2 supported)
2025-06-01: v1 sunset (only v2, v3 supported)
```

### 5. Use Sunset Headers

**Deprecation Warning:**
```http
GET /api/v1/users HTTP/1.1

HTTP/1.1 200 OK
Deprecation: true
Sunset: Sat, 01 Jun 2025 00:00:00 GMT
Link: <https://api.example.com/v2/users>; rel="successor-version"

{ "data": [...] }
```

**Implementation:**
```javascript
app.use('/api/v1', (req, res, next) => {
  res.setHeader('Deprecation', 'true');
  res.setHeader('Sunset', 'Sat, 01 Jun 2025 00:00:00 GMT');
  res.setHeader('Link', '<https://api.example.com/v2>; rel="successor-version"');
  next();
});
```

### 6. Default to Latest Stable

```javascript
// If no version specified, default to latest stable
app.get('/api/users', (req, res) => {
  res.redirect('/api/v2/users');
});
```

### 7. Version OpenAPI Specs

```yaml
# openapi-v1.yaml
openapi: 3.1.0
info:
  title: API v1
  version: 1.0.0
servers:
  - url: https://api.example.com/v1

# openapi-v2.yaml
openapi: 3.1.0
info:
  title: API v2
  version: 2.0.0
servers:
  - url: https://api.example.com/v2
```

---

## Migration Strategies

### 1. Dual-Write Pattern

Write to both old and new versions during transition:

```javascript
// During migration period
app.post('/api/v2/users', async (req, res) => {
  const user = await createUser(req.body);

  // Also update v1 data store if needed
  await updateV1Cache(user);

  res.status(201).json(user);
});
```

### 2. Adapter Pattern

Translate v1 requests to v2 internally:

```javascript
const adaptV1ToV2 = (v1Response) => {
  return {
    data: v1Response,
    meta: { total: v1Response.length }
  };
};

app.get('/api/v1/users', async (req, res) => {
  const v2Response = await getUsersV2(req);
  const v1Response = v2Response.data;  // Extract array
  res.json(v1Response);
});
```

### 3. Feature Flags

Gradually roll out v2 to subset of users:

```javascript
app.get('/api/v1/users', async (req, res) => {
  const useV2 = await isUserInV2Rollout(req.user.id);

  if (useV2) {
    return getUsersV2(req, res);
  }
  return getUsersV1(req, res);
});
```

### 4. Proxy Pattern

Route traffic based on version:

```javascript
// API Gateway (Kong, Nginx)
location /api/v1 {
  proxy_pass http://api-v1-service:8080;
}

location /api/v2 {
  proxy_pass http://api-v2-service:8080;
}
```

---

## Monitoring & Analytics

### Track Version Adoption

```javascript
// Log version usage
app.use((req, res, next) => {
  const version = req.path.split('/')[2];  // Extract v1, v2, etc.

  analytics.track('api_request', {
    version,
    endpoint: req.path,
    userId: req.user?.id
  });

  next();
});
```

### Deprecation Alerts

```javascript
// Alert when deprecated version is used
app.use('/api/v1', (req, res, next) => {
  if (req.user) {
    alerting.send({
      message: `User ${req.user.id} still using deprecated v1`,
      severity: 'warning'
    });
  }
  next();
});
```

---

## Real-World Examples

### Stripe API

**Versioning:**
- URL: `https://api.stripe.com/v1/charges`
- Header: `Stripe-Version: 2024-12-18`
- Combines both approaches (path + header)

**Features:**
- Dated versions (2024-12-18) instead of v1, v2
- Account-level version pinning
- Automatic upgrades with warnings

### GitHub API

**Versioning:**
- URL: `https://api.github.com/users`
- Header: `X-GitHub-Api-Version: 2022-11-28`
- Default version if header not provided

**Features:**
- Sunset headers for deprecated endpoints
- Extensive migration guides
- Version per resource (not global)

### Twitter API

**Versioning:**
- URL: `https://api.twitter.com/2/tweets`
- Simple major versions: v1.1, v2
- Long support windows (v1.1 supported for years)

---

## GraphQL Versioning

**Key Difference:** GraphQL discourages versioning because clients control what fields they request.

**Instead of versioning:**
```graphql
# BAD: Don't version entire schema
type Query {
  usersV1: [UserV1]
  usersV2: [UserV2]
}

# GOOD: Deprecate fields, add new ones
type User {
  id: ID!
  name: String!
  phone: String @deprecated(reason: "Use phoneNumber instead")
  phoneNumber: String
}
```

**Evolution Strategy:**
1. Add new field
2. Deprecate old field
3. Clients migrate at their own pace
4. Remove deprecated field in future release

---

## Checklist for New Version

Before releasing new API version:

- [ ] Document all breaking changes
- [ ] Write migration guide with before/after examples
- [ ] Update OpenAPI spec
- [ ] Set up routing for new version
- [ ] Implement sunset headers on old version
- [ ] Update client SDKs
- [ ] Notify all API consumers (email, blog post)
- [ ] Set sunset date (6-12 months out)
- [ ] Monitor adoption metrics
- [ ] Provide sandbox environment for testing
- [ ] Create comparison table (v1 vs v2 features)

---

## Resources

- [Stripe API Versioning](https://stripe.com/docs/api/versioning)
- [GitHub API Versioning](https://docs.github.com/en/rest/overview/api-versions)
- [Semantic Versioning](https://semver.org/)
- [RFC 8594 - Sunset Header](https://datatracker.ietf.org/doc/html/rfc8594)
- [REST API Versioning Guide](https://restfulapi.net/versioning/)
