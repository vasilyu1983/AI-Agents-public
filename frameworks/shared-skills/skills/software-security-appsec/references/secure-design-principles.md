# Secure Design Principles

Foundational security principles for building secure systems from the ground up.

---

## Core Security Principles

### 1. Defense in Depth

**Concept**: Layer multiple security controls so failure of one doesn't compromise the system.

**Implementation:**
```javascript
// Layer 1: Input validation
const validateInput = (data) => {
  if (!isValid(data)) throw new ValidationError();
  return data;
};

// Layer 2: Authentication
const authenticate = (req, res, next) => {
  if (!req.user) return res.status(401).json({ error: 'Unauthorized' });
  next();
};

// Layer 3: Authorization
const authorize = (req, res, next) => {
  if (!hasPermission(req.user, req.resource)) {
    return res.status(403).json({ error: 'Forbidden' });
  }
  next();
};

// Layer 4: Rate limiting
const rateLimit = createRateLimiter({ max: 100, windowMs: 15 * 60 * 1000 });

// Layer 5: Logging and monitoring
const logSecurityEvent = (event) => {
  securityLogger.info(event);
};

// Apply all layers
app.post('/api/sensitive-action',
  rateLimit,
  authenticate,
  authorize,
  validateRequest,
  async (req, res) => {
    logSecurityEvent({ action: 'sensitive-action', user: req.user.id });
    const result = await performAction(validateInput(req.body));
    res.json(result);
  }
);
```

---

### 2. Principle of Least Privilege

**Concept**: Grant minimum permissions necessary for a task.

**Implementation:**
```javascript
// Bad: Single admin role with all permissions
const ROLES = {
  ADMIN: ['users:*', 'posts:*', 'settings:*', 'billing:*']
};

// Good: Granular roles with specific permissions
const ROLES = {
  USER_ADMIN: ['users:read', 'users:write'],
  CONTENT_MODERATOR: ['posts:read', 'posts:delete'],
  BILLING_ADMIN: ['billing:read', 'billing:write'],
  SYSTEM_ADMIN: ['settings:read', 'settings:write']
};

// Database access with least privilege
const createDatabaseUser = async () => {
  // App user: only necessary permissions
  await db.execute(`
    CREATE USER app_user WITH PASSWORD 'secure-password';
    GRANT SELECT, INSERT, UPDATE ON users TO app_user;
    GRANT SELECT, INSERT, UPDATE, DELETE ON posts TO app_user;
    -- No DROP, TRUNCATE, or admin privileges
  `);

  // Read-only analytics user
  await db.execute(`
    CREATE USER analytics_user WITH PASSWORD 'secure-password';
    GRANT SELECT ON users TO analytics_user;
    GRANT SELECT ON posts TO analytics_user;
  `);
};
```

---

### 3. Fail Securely

**Concept**: System should fail in a secure state, not expose sensitive data or bypass security.

**Implementation:**
```javascript
// Bad: Error exposes sensitive information
app.get('/api/users/:id', async (req, res) => {
  try {
    const user = await User.findById(req.params.id);
    res.json(user);
  } catch (error) {
    res.status(500).json({ error: error.message, stack: error.stack });
  }
});

// Good: Fail securely with generic error
app.get('/api/users/:id', async (req, res) => {
  try {
    const user = await User.findById(req.params.id);

    if (!user) {
      return res.status(404).json({ error: 'User not found' });
    }

    res.json(user);
  } catch (error) {
    // Log detailed error server-side
    logger.error('Failed to retrieve user', { error, userId: req.params.id });

    // Return generic error to client
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Bad: Default to allow on error
const checkPermission = (user, resource) => {
  try {
    return policyEngine.evaluate(user, resource);
  } catch (error) {
    return true; // BAD: Dangerous: grants access on error
  }
};

// Good: Default to deny on error
const checkPermission = (user, resource) => {
  try {
    return policyEngine.evaluate(user, resource);
  } catch (error) {
    logger.error('Permission check failed', { error, user, resource });
    return false; // GOOD: Secure: denies access on error
  }
};
```

---

### 4. Complete Mediation

**Concept**: Check authorization on every access attempt, never cache authorization decisions.

**Implementation:**
```javascript
// Bad: Cache authorization decision
const userPermissions = {};

const authorize = async (req, res, next) => {
  const userId = req.user.id;

  // BAD: Uses cached permissions (may be stale)
  if (!userPermissions[userId]) {
    userPermissions[userId] = await getPermissions(userId);
  }

  if (userPermissions[userId].includes(req.permission)) {
    next();
  } else {
    res.status(403).json({ error: 'Forbidden' });
  }
};

// Good: Check authorization on every request
const authorize = async (req, res, next) => {
  // GOOD: Always fetch fresh permissions
  const permissions = await getPermissions(req.user.id);

  if (permissions.includes(req.permission)) {
    next();
  } else {
    res.status(403).json({ error: 'Forbidden' });
  }
};

// Good: Verify ownership on every access
app.put('/api/posts/:id', authenticate, async (req, res) => {
  const post = await Post.findById(req.params.id);

  // GOOD: Verify ownership every time
  if (post.authorId !== req.user.id && req.user.role !== 'admin') {
    return res.status(403).json({ error: 'Forbidden' });
  }

  await post.update(req.body);
  res.json(post);
});
```

---

### 5. Separation of Duties

**Concept**: Critical operations require multiple parties or approvals.

**Implementation:**
```javascript
// Example: Financial transaction approval
const initiateTransfer = async (userId, amount, recipient) => {
  // User initiates transfer
  const transfer = await Transfer.create({
    initiatedBy: userId,
    amount,
    recipient,
    status: 'pending',
    createdAt: new Date()
  });

  // Notify approvers
  await notifyApprovers(transfer);

  return transfer;
};

const approveTransfer = async (transferId, approverId) => {
  const transfer = await Transfer.findById(transferId);

  // Cannot approve own transfer
  if (transfer.initiatedBy === approverId) {
    throw new SecurityError('Cannot approve own transfer');
  }

  // Require admin role for approval
  const approver = await User.findById(approverId);
  if (approver.role !== 'admin') {
    throw new AuthorizationError('Insufficient permissions');
  }

  // Execute transfer
  transfer.status = 'approved';
  transfer.approvedBy = approverId;
  transfer.approvedAt = new Date();

  await transfer.save();
  await executeTransfer(transfer);

  return transfer;
};
```

---

### 6. Open Design (No Security Through Obscurity)

**Concept**: Security should not rely on secrecy of design, only on keys/credentials.

**Implementation:**
```javascript
// Bad: Custom "encryption" algorithm
const obfuscate = (data) => {
  return data.split('').reverse().join(''); // BAD: Weak, obscure
};

// Good: Standard encryption with secret key
const encrypt = (data, key) => {
  const iv = crypto.randomBytes(16);
  const cipher = crypto.createCipheriv('aes-256-gcm', key, iv);
  // ... standard encryption
};

// Bad: Hide API endpoints
// /api/v1/secret_admin_panel_xyz123

// Good: Use authentication/authorization
app.get('/api/v1/admin', authenticate, requireRole('admin'), adminHandler);
```

---

### 7. Secure by Default

**Concept**: Most secure configuration should be the default.

**Implementation:**
```javascript
// Good: Secure defaults
const createUser = async (userData) => {
  return await User.create({
    ...userData,
    // GOOD: Secure defaults
    emailVerified: false,
    mfaEnabled: false,
    accountLocked: false,
    role: 'user', // Not admin
    permissions: [], // No permissions by default
    createdAt: new Date()
  });
};

// Good: Secure cookie defaults
app.use(session({
  secret: process.env.SESSION_SECRET,
  cookie: {
    secure: true,        // GOOD: HTTPS only
    httpOnly: true,      // GOOD: No JavaScript access
    sameSite: 'strict',  // GOOD: CSRF protection
    maxAge: 30 * 60 * 1000
  }
}));

// Good: Secure CORS defaults
const cors = require('cors');

app.use(cors({
  origin: false, // GOOD: Deny all by default
  credentials: true,
  optionsSuccessStatus: 200
}));

// Explicitly allow specific origins
app.use('/api/public', cors({
  origin: ['https://app.example.com']
}));
```

---

### 8. Keep It Simple

**Concept**: Simpler systems are easier to secure and audit.

**Implementation:**
```javascript
// Bad: Overly complex authorization logic
const checkAccess = (user, resource) => {
  if (user.role === 'admin') return true;
  if (user.role === 'moderator' && resource.type === 'post') {
    if (resource.reportCount > 5 || resource.flags.includes('spam')) {
      return true;
    }
  }
  if (user.id === resource.ownerId) {
    if (resource.status !== 'locked' || user.hasPremium) {
      return true;
    }
  }
  // ... more complex conditions
  return false;
};

// Good: Clear, simple policy-based authorization
const policies = [
  new AdminPolicy(),              // Admins can do anything
  new OwnershipPolicy(),          // Owners can edit their resources
  new ModeratorPolicy()           // Moderators can moderate flagged content
];

const checkAccess = async (user, resource, action) => {
  for (const policy of policies) {
    const result = await policy.evaluate(user, resource, action);
    if (result === 'allow') return true;
    if (result === 'deny') return false;
  }
  return false; // Deny by default
};
```

---

## Secure Design Patterns

### Pattern 1: Threat Modeling (STRIDE)

**STRIDE Framework:**
- **S**poofing: Identity verification
- **T**ampering: Data integrity
- **R**epudiation: Audit logging
- **I**nformation Disclosure: Data protection
- **D**enial of Service: Availability
- **E**levation of Privilege: Authorization

**Example Threat Model:**
```
Component: User Authentication API

Threats:
1. Spoofing:
   - Attacker impersonates legitimate user
   - Mitigation: Strong password policy, MFA, rate limiting

2. Tampering:
   - JWT tokens modified by attacker
   - Mitigation: Verify JWT signature, use short expiration

3. Repudiation:
   - User denies performing action
   - Mitigation: Log all authentication events with timestamp

4. Information Disclosure:
   - Password hashes leaked via SQL injection
   - Mitigation: Parameterized queries, bcrypt hashing

5. Denial of Service:
   - Brute force login attempts
   - Mitigation: Rate limiting, account lockout, CAPTCHA

6. Elevation of Privilege:
   - Regular user gains admin access
   - Mitigation: Role-based access control, verify on every request
```

---

### Pattern 2: Zero Trust Architecture

**Concept**: Never trust, always verify - verify every request regardless of source.

**Implementation:**
```javascript
// Every request must be authenticated and authorized
const zeroTrustMiddleware = [
  // 1. Verify identity
  authenticate,

  // 2. Verify device/client
  verifyDeviceFingerprint,

  // 3. Verify permissions
  authorize,

  // 4. Verify request integrity
  verifyRequestSignature,

  // 5. Check risk score
  evaluateRiskScore,

  // 6. Log access
  logAccess
];

app.use('/api/*', zeroTrustMiddleware);

// No implicit trust for internal services
const callInternalAPI = async (endpoint, data) => {
  const token = await getServiceToken();

  return await fetch(`https://internal-api/${endpoint}`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'X-Service-ID': process.env.SERVICE_ID
    },
    body: JSON.stringify(data)
  });
};
```

---

### Pattern 3: Secure Session Management

```javascript
const session = require('express-session');
const RedisStore = require('connect-redis').default;

app.use(session({
  store: new RedisStore({ client: redisClient }),
  secret: process.env.SESSION_SECRET,
  resave: false,
  saveUninitialized: false,
  cookie: {
    secure: true,
    httpOnly: true,
    sameSite: 'strict',
    maxAge: 30 * 60 * 1000
  },
  // Regenerate session ID periodically
  rolling: true,

  // Session versioning
  genid: (req) => {
    return crypto.randomUUID();
  }
}));

// Regenerate session on privilege change
const elevatePrivileges = (req, res, next) => {
  const oldSessionId = req.sessionID;

  req.session.regenerate((err) => {
    if (err) return next(err);

    // Copy session data
    req.session.userId = req.user.id;
    req.session.role = 'admin';

    // Log session change
    logger.info('Session elevated', {
      oldSessionId,
      newSessionId: req.sessionID,
      userId: req.user.id
    });

    next();
  });
};

// Destroy session on logout
app.post('/auth/logout', (req, res) => {
  const sessionId = req.sessionID;

  req.session.destroy((err) => {
    if (err) {
      logger.error('Session destruction failed', { err, sessionId });
      return res.status(500).json({ error: 'Logout failed' });
    }

    res.clearCookie('connect.sid');
    logger.info('User logged out', { sessionId });
    res.json({ message: 'Logged out' });
  });
});
```

---

### Pattern 4: Security Boundaries

**Concept**: Define trust boundaries and validate all data crossing them.

```javascript
// Trust boundary: External API → Application
const externalAPIBoundary = async (req, res, next) => {
  // 1. Authenticate API client
  const apiKey = req.headers['x-api-key'];
  if (!await verifyAPIKey(apiKey)) {
    return res.status(401).json({ error: 'Invalid API key' });
  }

  // 2. Validate input schema
  try {
    req.validatedData = validateAPISchema(req.body);
  } catch (error) {
    return res.status(400).json({ error: 'Invalid request format' });
  }

  // 3. Rate limit
  const allowed = await checkRateLimit(apiKey);
  if (!allowed) {
    return res.status(429).json({ error: 'Rate limit exceeded' });
  }

  // 4. Log crossing of trust boundary
  logger.info('External API request', {
    apiKey,
    endpoint: req.path,
    ip: req.ip
  });

  next();
};

// Trust boundary: Application → Database
const databaseBoundary = {
  query: async (sql, params) => {
    // 1. Validate SQL (parameterized queries only)
    if (!Array.isArray(params)) {
      throw new SecurityError('Parameterized queries required');
    }

    // 2. Log query
    logger.debug('Database query', { sql, params });

    // 3. Execute with timeout
    const result = await db.execute(sql, params, { timeout: 5000 });

    return result;
  }
};
```

---

## Security Checklist

### Design Phase
- [ ] Conduct threat modeling (STRIDE)
- [ ] Define security requirements
- [ ] Identify trust boundaries
- [ ] Design authentication/authorization
- [ ] Plan data encryption strategy
- [ ] Define logging and monitoring
- [ ] Review architecture with security team

### Implementation Phase
- [ ] Follow secure coding standards
- [ ] Implement defense in depth
- [ ] Apply principle of least privilege
- [ ] Validate all inputs
- [ ] Encode all outputs
- [ ] Use parameterized queries
- [ ] Implement proper error handling

### Testing Phase
- [ ] Penetration testing
- [ ] Security code review
- [ ] Dependency vulnerability scanning
- [ ] Static analysis (SAST)
- [ ] Dynamic analysis (DAST)
- [ ] Verify authentication/authorization
- [ ] Test error handling

### Deployment Phase
- [ ] Secure configuration management
- [ ] Environment separation
- [ ] Secrets management
- [ ] TLS/HTTPS enforcement
- [ ] Security headers configured
- [ ] Monitoring and alerting enabled
- [ ] Incident response plan documented

---

## References

- [OWASP Secure Product Design](https://cheatsheetseries.owasp.org/cheatsheets/Secure_Product_Design_Cheat_Sheet.html)
- [Microsoft Threat Modeling](https://www.microsoft.com/en-us/securityengineering/sdl/threatmodeling)
- [NIST Secure Software Development Framework](https://csrc.nist.gov/projects/ssdf)
