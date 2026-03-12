# API Security Checklist

Comprehensive security checklist based on OWASP API Security Top 10 2023 and industry best practices.

---

## OWASP Updates (January 2026)

**OWASP API Security Top 10 (2023)** remains the current API-specific list. No 2025/2026 update has been released.

**OWASP Top 10 (2025)** for web applications was released November 2025 with key changes:

| New/Changed | Category | API Relevance |
|-------------|----------|---------------|
| **A03:2025** | Software Supply Chain Failures | Third-party API dependencies, SDK vulnerabilities |
| **A02:2025** | Security Misconfiguration (now #2) | API gateway configs, CORS, headers |
| **A01:2025** | Broken Access Control (SSRF merged) | BOLA, BFLA, SSRF all under access control |

**Key Takeaway**: Supply chain security is now critical — audit third-party API clients, SDK dependencies, and transitive vulnerabilities.

See: [OWASP Top 10 2025](https://owasp.org/www-project-top-ten/)

---

## OWASP API Security Top 10 (2023)

### API1:2023 Broken Object Level Authorization (BOLA)

**Risk:** Users can access objects belonging to other users by manipulating IDs in requests.

**Example Vulnerability:**
```
GET /api/v1/users/123/orders/456
# User 123 can access order 456 even if it belongs to user 789
```

**Mitigation:**
```javascript
// BAD: No authorization check
app.get('/api/v1/users/:userId/orders/:orderId', async (req, res) => {
  const order = await Order.findById(req.params.orderId);
  res.json(order);
});

// GOOD: Verify ownership
app.get('/api/v1/users/:userId/orders/:orderId', async (req, res) => {
  const order = await Order.findById(req.params.orderId);

  if (order.userId !== req.params.userId) {
    return res.status(403).json({ error: 'Access denied' });
  }

  res.json(order);
});
```

**Checklist:**
- [ ] Implement authorization checks on every endpoint
- [ ] Verify user owns or has access to requested resource
- [ ] Don't rely on client-provided object IDs alone
- [ ] Use UUIDs instead of sequential IDs
- [ ] Log authorization failures for monitoring

---

### API2:2023 Broken Authentication

**Risk:** Weak authentication allows attackers to impersonate users or bypass auth entirely.

**Common Vulnerabilities:**
- Accepting unsigned JWT tokens (`{"alg":"none"}`)
- Not validating JWT expiration
- Weak password policies
- Exposing credentials in URLs
- Missing rate limiting on login

**Mitigation - JWT:**
```javascript
// BAD: Accepts unsigned tokens
jwt.verify(token, secret, { algorithms: ['HS256', 'none'] });

// GOOD: Only signed tokens
jwt.verify(token, secret, { algorithms: ['HS256'] });

// GOOD: Full validation
const payload = jwt.verify(token, secret, {
  algorithms: ['HS256'],
  maxAge: '15m',  // Short-lived access tokens
  issuer: 'api.example.com',
  audience: 'api.example.com'
});

// Verify token not revoked (check Redis/DB)
if (await isTokenRevoked(token)) {
  throw new Error('Token revoked');
}
```

**Mitigation - Password Policies:**
```javascript
// GOOD: Strong password requirements
const passwordSchema = z.string()
  .min(12, 'Password must be at least 12 characters')
  .regex(/[A-Z]/, 'Must contain uppercase letter')
  .regex(/[a-z]/, 'Must contain lowercase letter')
  .regex(/[0-9]/, 'Must contain number')
  .regex(/[^A-Za-z0-9]/, 'Must contain special character');

// GOOD: Use bcrypt with high cost factor
const hashedPassword = await bcrypt.hash(password, 12);
```

**Checklist:**
- [ ] Use strong signing algorithms (HS256, RS256, never 'none')
- [ ] Validate JWT expiration, issuer, audience
- [ ] Short-lived access tokens (5-15 min) + refresh tokens
- [ ] Implement token revocation (blacklist or Redis)
- [ ] Use bcrypt/scrypt/Argon2 for password hashing (cost >= 12)
- [ ] Enforce strong password policies
- [ ] Never send credentials in URL query parameters
- [ ] Implement rate limiting on login endpoints
- [ ] Require MFA for sensitive operations

---

### API3:2023 Broken Object Property Level Authorization

**Risk:** Users can access or modify object properties they shouldn't (mass assignment, excessive data exposure).

**Example - Mass Assignment:**
```javascript
// BAD: Allows any field to be updated
app.patch('/api/v1/users/:id', async (req, res) => {
  await User.update(req.params.id, req.body);
  // Attacker sends: { "role": "admin", "is_verified": true }
});

// GOOD: Whitelist allowed fields
app.patch('/api/v1/users/:id', async (req, res) => {
  const allowedFields = ['name', 'email', 'phone'];
  const updates = pick(req.body, allowedFields);

  await User.update(req.params.id, updates);
});
```

**Example - Excessive Data Exposure:**
```javascript
// BAD: Exposes sensitive fields
app.get('/api/v1/users/:id', async (req, res) => {
  const user = await User.findById(req.params.id);
  res.json(user);  // Returns password_hash, credit_card, ssn, etc.
});

// GOOD: Explicit field selection
app.get('/api/v1/users/:id', async (req, res) => {
  const user = await User.findById(req.params.id)
    .select('id name email created_at');  // Only safe fields
  res.json(user);
});
```

**Checklist:**
- [ ] Whitelist allowed fields for all write operations
- [ ] Never blindly trust `req.body` for updates
- [ ] Use DTOs (Data Transfer Objects) to define safe schemas
- [ ] Explicitly select fields in responses (don't return full models)
- [ ] Separate admin/user schemas with different field access
- [ ] Never expose internal fields (password_hash, tokens, internal_id)

---

### API4:2023 Unrestricted Resource Consumption

**Risk:** APIs without rate limiting or resource limits can be abused, leading to DoS or excessive costs.

**Mitigation - Rate Limiting:**
```javascript
// GOOD: Token Bucket with Redis
const rateLimit = require('express-rate-limit');
const RedisStore = require('rate-limit-redis');

const limiter = rateLimit({
  store: new RedisStore({
    client: redis,
    prefix: 'rl:'
  }),
  windowMs: 15 * 60 * 1000,  // 15 minutes
  max: 100,  // 100 requests per window
  standardHeaders: true,  // Return rate limit info in headers
  legacyHeaders: false,
  handler: (req, res) => {
    res.status(429).json({
      error: 'Too many requests',
      retryAfter: req.rateLimit.resetTime
    });
  }
});

app.use('/api/', limiter);
```

**Mitigation - Request Size Limits:**
```javascript
// GOOD: Limit request body size
app.use(express.json({ limit: '1mb' }));

// GOOD: Limit uploaded files
app.post('/api/v1/upload',
  upload.single('file', {
    limits: { fileSize: 10 * 1024 * 1024 }  // 10 MB max
  }),
  async (req, res) => { /* ... */ }
);
```

**Mitigation - Pagination Limits:**
```javascript
// BAD: No limit
app.get('/api/v1/users', async (req, res) => {
  const users = await User.find().limit(req.query.limit);
  // Attacker: ?limit=1000000
});

// GOOD: Enforce max limit
app.get('/api/v1/users', async (req, res) => {
  const limit = Math.min(req.query.limit || 20, 100);  // Max 100
  const users = await User.find().limit(limit);
});
```

**Checklist:**
- [ ] Implement rate limiting per API key/user/IP
- [ ] Tiered rate limits (free: 100/hr, paid: 1000/hr)
- [ ] Limit request body size (default: 1 MB)
- [ ] Limit file upload size
- [ ] Enforce max pagination limits (max 100 items)
- [ ] Timeout long-running requests (30s default)
- [ ] Implement query complexity limits (GraphQL)
- [ ] Monitor resource usage and alert on anomalies

---

### API5:2023 Broken Function Level Authorization

**Risk:** Users can access admin/privileged functions by guessing URLs or manipulating requests.

**Example:**
```javascript
// BAD: No role check
app.delete('/api/v1/users/:id', async (req, res) => {
  await User.delete(req.params.id);
  // Any authenticated user can delete any user
});

// GOOD: Role-based access control
const requireAdmin = (req, res, next) => {
  if (req.user.role !== 'admin') {
    return res.status(403).json({ error: 'Admin access required' });
  }
  next();
};

app.delete('/api/v1/users/:id', requireAdmin, async (req, res) => {
  await User.delete(req.params.id);
});
```

**Checklist:**
- [ ] Implement RBAC (Role-Based Access Control)
- [ ] Check permissions on every privileged endpoint
- [ ] Deny by default, allow explicitly
- [ ] Don't rely on client-side role checks
- [ ] Hide admin endpoints from public docs
- [ ] Log all privileged actions with user context

---

### API6:2023 Unrestricted Access to Sensitive Business Flows

**Risk:** Automated abuse of business-critical flows (bulk purchases, scalping, account takeovers).

**Mitigation - CAPTCHA for Sensitive Actions:**
```javascript
// GOOD: Require CAPTCHA for registration
app.post('/api/v1/register', async (req, res) => {
  // Verify CAPTCHA
  const captchaValid = await verifyCaptcha(req.body.captcha_token);
  if (!captchaValid) {
    return res.status(400).json({ error: 'Invalid CAPTCHA' });
  }

  // Create user...
});
```

**Mitigation - Device Fingerprinting:**
```javascript
// GOOD: Track suspicious patterns
const deviceId = generateFingerprint(req);
const recentAttempts = await redis.get(`register:${deviceId}`);

if (recentAttempts > 3) {
  return res.status(429).json({ error: 'Too many registrations from this device' });
}
```

**Checklist:**
- [ ] Identify critical business flows (payments, signups, booking)
- [ ] Implement CAPTCHA for high-value operations
- [ ] Rate limit per user + per IP + per device
- [ ] Detect automation (consistent timing, user-agent patterns)
- [ ] Require additional verification for bulk operations
- [ ] Monitor for anomalies (sudden spikes, unusual patterns)

---

### API7:2023 Server-Side Request Forgery (SSRF)

**Risk:** Attacker tricks server into making requests to internal services or external URLs.

**Example:**
```javascript
// BAD: No URL validation
app.post('/api/v1/fetch-avatar', async (req, res) => {
  const response = await axios.get(req.body.url);
  // Attacker: { "url": "http://localhost:8080/admin" }
});

// GOOD: Whitelist allowed hosts
const ALLOWED_HOSTS = ['cdn.example.com', 's3.amazonaws.com'];

app.post('/api/v1/fetch-avatar', async (req, res) => {
  const url = new URL(req.body.url);

  // Block private IP ranges
  if (isPrivateIP(url.hostname)) {
    return res.status(400).json({ error: 'Invalid URL' });
  }

  // Whitelist allowed hosts
  if (!ALLOWED_HOSTS.includes(url.hostname)) {
    return res.status(400).json({ error: 'Host not allowed' });
  }

  const response = await axios.get(req.body.url);
});
```

**Checklist:**
- [ ] Validate all user-provided URLs
- [ ] Whitelist allowed hosts/domains
- [ ] Block private IP ranges (127.0.0.1, 10.0.0.0/8, 192.168.0.0/16)
- [ ] Block localhost and internal service URLs
- [ ] Disable URL redirects or validate redirect targets
- [ ] Use separate network segment for internal services

---

### API8:2023 Security Misconfiguration

**Risk:** Default credentials, verbose errors, missing security headers, outdated dependencies.

**Mitigation - Security Headers:**
```javascript
// GOOD: Security headers middleware
app.use((req, res, next) => {
  res.setHeader('X-Content-Type-Options', 'nosniff');
  res.setHeader('X-Frame-Options', 'DENY');
  res.setHeader('X-XSS-Protection', '1; mode=block');
  res.setHeader('Strict-Transport-Security', 'max-age=31536000; includeSubDomains');
  res.setHeader('Content-Security-Policy', "default-src 'self'");
  next();
});
```

**Mitigation - Error Handling:**
```javascript
// BAD: Exposes stack traces
app.use((err, req, res, next) => {
  res.status(500).json({ error: err.message, stack: err.stack });
});

// GOOD: Generic errors in production
app.use((err, req, res, next) => {
  console.error(err);  // Log internally

  if (process.env.NODE_ENV === 'production') {
    res.status(500).json({ error: 'Internal server error' });
  } else {
    res.status(500).json({ error: err.message });  // Dev only
  }
});
```

**Checklist:**
- [ ] Change all default credentials
- [ ] Disable directory listing
- [ ] Remove server version headers (`X-Powered-By`)
- [ ] Generic error messages in production (no stack traces)
- [ ] Implement security headers (HSTS, CSP, X-Frame-Options)
- [ ] Keep dependencies updated (automated scanning)
- [ ] Disable unnecessary HTTP methods (TRACE, OPTIONS)
- [ ] Remove development endpoints in production

---

### API9:2023 Improper Inventory Management

**Risk:** Unauthenticated endpoints, old API versions, undocumented endpoints accessible.

**Mitigation:**
```javascript
// GOOD: Centralized API documentation
const swaggerSpec = {
  openapi: '3.1.0',
  info: { title: 'API', version: '1.0.0' },
  paths: { /* All endpoints documented */ }
};

// GOOD: Automated endpoint discovery testing
describe('API Endpoints', () => {
  it('all endpoints require authentication', async () => {
    const endpoints = getAllEndpoints();
    for (const endpoint of endpoints) {
      const res = await request(app).get(endpoint);
      expect(res.status).not.toBe(200);  // Should fail without auth
    }
  });
});
```

**Checklist:**
- [ ] Document all endpoints in OpenAPI spec
- [ ] Deprecate old API versions with sunset headers
- [ ] Audit endpoints regularly (automated scans)
- [ ] Remove unused endpoints
- [ ] Ensure all endpoints have authentication
- [ ] Track which clients use which endpoints
- [ ] Version APIs and communicate deprecations

---

### API10:2023 Unsafe Consumption of APIs

**Risk:** Blindly trusting data from third-party APIs without validation.

**Mitigation:**
```javascript
// BAD: Trusts external API response
app.get('/api/v1/user-repos', async (req, res) => {
  const ghResponse = await axios.get(`https://api.github.com/users/${req.params.username}/repos`);
  const repos = ghResponse.data;
  await saveToDatabase(repos);  // No validation!
});

// GOOD: Validate external data
const repoSchema = z.array(z.object({
  id: z.number(),
  name: z.string().max(100),
  description: z.string().max(500).nullable(),
  html_url: z.string().url()
}));

app.get('/api/v1/user-repos', async (req, res) => {
  const ghResponse = await axios.get(`https://api.github.com/users/${req.params.username}/repos`);

  // Validate schema
  const repos = repoSchema.parse(ghResponse.data);

  await saveToDatabase(repos);
});
```

**Checklist:**
- [ ] Validate all data from external APIs
- [ ] Use schemas (Zod, Joi, JSON Schema)
- [ ] Set timeouts for external calls (5-10s)
- [ ] Handle errors gracefully (don't expose to clients)
- [ ] Sanitize URLs before redirecting
- [ ] Don't trust redirect chains
- [ ] Rate limit calls to external APIs

---

## Additional Security Best Practices

### HTTPS Configuration

**Checklist:**
- [ ] TLS 1.3 only (TLS 1.2 minimum)
- [ ] Strong cipher suites only
- [ ] HSTS header with `includeSubDomains`
- [ ] Valid SSL certificates (not self-signed)
- [ ] Automatic certificate renewal (Let's Encrypt)

### Logging & Monitoring

```javascript
// GOOD: Log security events
logger.warn('Failed login attempt', {
  ip: req.ip,
  username: req.body.username,
  timestamp: new Date()
});

logger.error('Authorization failure', {
  userId: req.user.id,
  resource: req.params.id,
  action: 'DELETE'
});
```

**Checklist:**
- [ ] Log all authentication failures
- [ ] Log all authorization failures
- [ ] Log sensitive operations (deletes, privilege changes)
- [ ] Don't log sensitive data (passwords, tokens, PII)
- [ ] Set up alerts for anomalies
- [ ] Retain logs for compliance (90+ days)

### Input Validation

**Checklist:**
- [ ] Validate all input server-side
- [ ] Use allow-lists, not deny-lists
- [ ] Enforce type safety (TypeScript, Zod)
- [ ] Validate content-type headers
- [ ] Sanitize input before database queries
- [ ] Parameterized queries for SQL
- [ ] Validate file uploads (type, size, content)

---

## Security Testing

### Automated Scans

```bash
# OWASP ZAP
zap-cli quick-scan https://api.example.com

# Dependency scanning
npm audit
pip check

# SAST (Static Analysis)
semgrep --config=auto src/
```

### Penetration Testing

- Run OWASP ZAP/Burp Suite against staging
- Test BOLA by manipulating IDs
- Test authentication bypass techniques
- Fuzz inputs with unexpected data
- Test rate limiting effectiveness

---

## Resources

- [OWASP API Security Top 10 2023](https://owasp.org/API-Security/editions/2023/en/0x11-t10/)
- [OWASP Authentication Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html)
- [JWT Best Practices](https://datatracker.ietf.org/doc/html/rfc8725)
- [OAuth 2.0 Security Best Practices](https://datatracker.ietf.org/doc/html/draft-ietf-oauth-security-topics)
