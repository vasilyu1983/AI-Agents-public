# OWASP Top 10:2025 — Detailed Guide

Comprehensive guide to the OWASP Top 10:2025 (final release) web application security risks with modern prevention strategies and code examples.

---

## Jan 2026 Baseline

**OWASP Top 10:2025 is now FINAL** (released late 2025): https://owasp.org/Top10/2025/

### Key Changes from 2021 → 2025

| 2021 | 2025 | Change |
|------|------|--------|
| A01: Broken Access Control | A01: Broken Access Control | Same (includes SSRF now) |
| A05: Security Misconfiguration | A02: Security Misconfiguration | Moved UP from #5 |
| A06: Vulnerable Components | **A03: Software Supply Chain Failures** | **NEW scope** (expanded) |
| A02: Cryptographic Failures | A04: Cryptographic Failures | Moved DOWN from #2 |
| A03: Injection | A05: Injection | Moved DOWN from #3 |
| A04: Insecure Design | A06: Insecure Design | Moved DOWN from #4 |
| A07: Auth Failures | A07: Authentication Failures | Same |
| A08: Integrity Failures | A08: Software or Data Integrity Failures | Same |
| A09: Logging Failures | A09: Logging & Alerting Failures | Same |
| A10: SSRF | **A10: Mishandling of Exceptional Conditions** | **NEW** (SSRF merged into A01) |

### 2025 Methodology Updates

- Analyzed **589 CWEs** (vs ~400 in 2021)
- Incorporated **175,000 CVE records** with CVSS scores
- Focus on **root causes** rather than symptoms
- Emphasis on design flaws, misconfigurations, and dependency weaknesses

### How to Use This Document

- Use the sections below as practical mitigations and review prompts.
- For supply chain (A03), see [supply-chain-security.md](supply-chain-security.md).
- For zero trust context, see [zero-trust-architecture.md](zero-trust-architecture.md).

---

## 1. Broken Access Control

**Risk**: Users can access resources or perform actions beyond their authorization.

### Common Vulnerabilities

- Missing authorization checks on API endpoints
- Insecure direct object references (IDOR)
- Vertical privilege escalation (regular user → admin)
- Horizontal privilege escalation (accessing other users' data)
- Force browsing to unauthorized pages
- CORS misconfiguration

### Prevention

```javascript
// Bad: No authorization check
app.get('/api/users/:id', async (req, res) => {
  const user = await User.findById(req.params.id);
  res.json(user);
});

// Good: Verify user can access resource
app.get('/api/users/:id', authenticate, async (req, res) => {
  const requestedUserId = req.params.id;
  const currentUserId = req.user.id;
  const isAdmin = req.user.role === 'admin';

  // Users can only access their own data unless they're admin
  if (requestedUserId !== currentUserId && !isAdmin) {
    return res.status(403).json({ error: 'Forbidden' });
  }

  const user = await User.findById(requestedUserId);
  res.json(user);
});
```

**Best Practices:**
- Deny by default, grant access explicitly
- Check authorization on every request
- Use indirect object references (tokens/UUIDs instead of sequential IDs)
- Log and alert on authorization failures
- Implement server-side access control lists (ACLs)
- Test for privilege escalation scenarios

---

## 2. Cryptographic Failures

**Risk**: Sensitive data exposed due to weak or missing encryption.

### Common Issues

- Transmitting data in cleartext (HTTP instead of HTTPS)
- Weak encryption algorithms (DES, MD5, SHA-1)
- Hard-coded encryption keys
- Insecure random number generation
- Missing encryption for sensitive data at rest

### Prevention

```javascript
// Bad: Weak hashing
const crypto = require('crypto');
const hash = crypto.createHash('md5').update(password).digest('hex');

// Good: Strong password hashing
const bcrypt = require('bcrypt');
const hash = await bcrypt.hash(password, 12);

// Good: Secure data encryption
const encrypt = (data, key) => {
  const iv = crypto.randomBytes(16);
  const cipher = crypto.createCipheriv('aes-256-gcm', key, iv);

  let encrypted = cipher.update(data, 'utf8', 'hex');
  encrypted += cipher.final('hex');

  return {
    encrypted,
    iv: iv.toString('hex'),
    authTag: cipher.getAuthTag().toString('hex')
  };
};
```

**Best Practices:**
- Enforce HTTPS/TLS 1.3 for all traffic
- Use AES-256-GCM for symmetric encryption
- Use bcrypt, scrypt, or Argon2 for password hashing
- Store encryption keys in secure key management systems (AWS KMS, HashiCorp Vault)
- Classify data and encrypt sensitive data at rest
- Use cryptographically secure random number generators

---

## 3. Injection

**Risk**: Untrusted data sent to an interpreter leads to unauthorized commands execution.

### Types

- SQL Injection
- NoSQL Injection
- LDAP Injection
- OS Command Injection
- XPath Injection

### Prevention

```javascript
// SQL Injection Prevention
// Bad: String concatenation
const query = `SELECT * FROM users WHERE email = '${userEmail}'`;

// Good: Parameterized query
const query = 'SELECT * FROM users WHERE email = ?';
const [rows] = await db.execute(query, [userEmail]);

// Good: ORM (Sequelize)
const user = await User.findOne({ where: { email: userEmail } });

// NoSQL Injection Prevention
// Bad: Direct object injection
const user = await User.findOne({ email: req.body.email });

// Good: Validate and sanitize
const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
if (!emailRegex.test(req.body.email)) {
  throw new ValidationError('Invalid email format');
}
const user = await User.findOne({ email: req.body.email });

// OS Command Injection Prevention
// Bad: Unvalidated shell execution
const { exec } = require('child_process');
exec(`ping ${userInput}`);

// Good: Use libraries or strict validation
const { execFile } = require('child_process');
const allowedHosts = ['example.com', 'test.com'];

if (!allowedHosts.includes(userInput)) {
  throw new ValidationError('Invalid host');
}

execFile('ping', ['-c', '4', userInput]);
```

**Best Practices:**
- Use parameterized queries or ORMs
- Apply input validation with allowlists
- Escape special characters for the specific interpreter
- Use least privilege for database accounts
- Implement Web Application Firewall (WAF)

---

## 4. Security Misconfiguration

**Risk**: Insecure default configurations, incomplete setups, or verbose error messages.

### Common Misconfigurations

- Default credentials still in use
- Unnecessary features enabled
- Directory listing enabled
- Detailed error messages exposing stack traces
- Missing security headers
- Outdated software versions

### Prevention

```javascript
// Good: Security headers with Helmet
const helmet = require('helmet');

app.use(helmet({
  contentSecurityPolicy: {
    directives: {
      defaultSrc: ["'self'"],
      styleSrc: ["'self'", "'unsafe-inline'"],
      scriptSrc: ["'self'"],
      imgSrc: ["'self'", 'data:', 'https:']
    }
  },
  hsts: {
    maxAge: 31536000,
    includeSubDomains: true,
    preload: true
  },
  frameguard: { action: 'deny' },
  noSniff: true,
  xssFilter: true
}));

// Good: Generic error messages in production
app.use((err, req, res, next) => {
  // Log detailed error server-side
  logger.error('Error:', { error: err, stack: err.stack });

  // Return generic message to client
  if (process.env.NODE_ENV === 'production') {
    res.status(500).json({ error: 'Internal server error' });
  } else {
    res.status(500).json({ error: err.message, stack: err.stack });
  }
});
```

**Best Practices:**
- Harden all configurations (OS, framework, database, web server)
- Disable unnecessary features and services
- Remove default accounts and passwords
- Implement security headers (CSP, HSTS, X-Frame-Options)
- Keep all software up to date
- Use automated configuration scanning tools

---

## 5. Vulnerable and Outdated Components

**Risk**: Using libraries, frameworks, or modules with known vulnerabilities.

### Prevention

```bash
# Check for vulnerabilities
npm audit
npm audit fix

# Use dependency scanning tools
npm install -g snyk
snyk test
snyk monitor

# Check Python dependencies
pip-audit

# Use Dependabot or Renovate for automated updates
```

**Best Practices:**
- Inventory all components and versions
- Monitor CVE databases for component vulnerabilities
- Use Software Composition Analysis (SCA) tools
- Remove unused dependencies
- Only obtain components from official sources
- Subscribe to security bulletins for components in use
- Implement automated dependency updates

---

## 6. Insecure Design

**Risk**: Missing or ineffective security controls in design phase.

### Key Concepts

- **Threat modeling**: Identify threats before implementation
- **Secure design patterns**: Use proven security architectures
- **Security requirements**: Define security needs early

### Prevention

```javascript
// Bad: No rate limiting, account enumeration vulnerability
app.post('/api/auth/login', async (req, res) => {
  const user = await User.findOne({ email: req.body.email });

  if (!user) {
    return res.status(401).json({ error: 'Email not found' });
  }

  const valid = await bcrypt.compare(req.body.password, user.password);

  if (!valid) {
    return res.status(401).json({ error: 'Invalid password' });
  }

  const token = generateToken(user);
  res.json({ token });
});

// Good: Rate limiting, generic error, account lockout
const rateLimit = require('express-rate-limit');

const loginLimiter = rateLimit({
  windowMs: 15 * 60 * 1000,
  max: 5,
  message: 'Too many login attempts, please try again later'
});

app.post('/api/auth/login', loginLimiter, async (req, res) => {
  const user = await User.findOne({ email: req.body.email });

  // Check account lockout
  if (user && user.lockedUntil && user.lockedUntil > Date.now()) {
    return res.status(429).json({ error: 'Account temporarily locked' });
  }

  // Validate credentials (constant-time comparison)
  const valid = user && await bcrypt.compare(req.body.password, user.password);

  if (!valid) {
    // Increment failed attempts
    if (user) {
      await incrementFailedAttempts(user);
    }

    // Generic error (prevent enumeration)
    return res.status(401).json({ error: 'Invalid credentials' });
  }

  // Reset failed attempts on success
  await resetFailedAttempts(user);

  const token = generateToken(user);
  res.json({ token });
});
```

**Best Practices:**
- Conduct threat modeling during design phase
- Use established secure design patterns
- Implement defense in depth
- Separate duties and enforce least privilege
- Apply secure defaults
- Design for failure (fail securely)

---

## 7. Identification and Authentication Failures

**Risk**: Weak authentication mechanisms allowing unauthorized access.

### Common Issues

- Weak password policies
- Credential stuffing attacks
- Session fixation
- Missing multi-factor authentication
- Predictable session IDs
- Passwords stored in plaintext

### Prevention

```javascript
// Good: Strong authentication implementation
const authenticateUser = async (email, password, mfaCode) => {
  // Rate limiting handled by middleware

  // Find user
  const user = await User.findOne({ email });

  if (!user || !(await bcrypt.compare(password, user.passwordHash))) {
    // Constant-time response to prevent timing attacks
    await bcrypt.compare(password, '$2b$12$fixedHashForConstantTime');
    throw new AuthenticationError('Invalid credentials');
  }

  // Check MFA if enabled
  if (user.mfaEnabled) {
    const validMfa = await verifyTOTP(user.mfaSecret, mfaCode);

    if (!validMfa) {
      throw new AuthenticationError('Invalid MFA code');
    }
  }

  // Generate secure session
  const sessionId = crypto.randomBytes(32).toString('hex');

  await Session.create({
    sessionId,
    userId: user.id,
    expiresAt: new Date(Date.now() + 30 * 60 * 1000) // 30 minutes
  });

  return sessionId;
};
```

**Best Practices:**
- Enforce strong password policies (length, complexity, no common passwords)
- Implement multi-factor authentication
- Use account lockout after failed attempts
- Implement secure session management
- Generate cryptographically random session IDs
- Invalidate sessions on logout
- Implement password reset flow securely

---

## 8. Software and Data Integrity Failures

**Risk**: Code and infrastructure that does not protect against integrity violations.

### Common Issues

- Unsigned software updates
- Insecure CI/CD pipelines
- Untrusted serialized data
- Missing Subresource Integrity (SRI)
- Unsigned commits

### Prevention

```html
<!-- Good: Subresource Integrity for CDN resources -->
<script
  src="https://cdn.example.com/library.js"
  integrity="sha384-oqVuAfXRKap7fdgcCY5uykM6+R9GqQ8K/uxy9rx7HNQlGYl1kPzQho1wx4JwY8wC"
  crossorigin="anonymous"
></script>

<link
  rel="stylesheet"
  href="https://cdn.example.com/styles.css"
  integrity="sha384-ABC123..."
  crossorigin="anonymous"
>
```

```javascript
// Good: Verify software signatures
const verifySignature = (data, signature, publicKey) => {
  const verify = crypto.createVerify('SHA256');
  verify.update(data);
  verify.end();

  return verify.verify(publicKey, signature, 'hex');
};
```

**Best Practices:**
- Use digital signatures for software updates
- Verify integrity of downloaded packages
- Implement SRI for third-party resources
- Secure CI/CD pipelines
- Sign commits and tags in version control
- Avoid deserializing untrusted data
- Use dependency lock files

---

## 9. Security Logging and Monitoring Failures

**Risk**: Insufficient logging and monitoring to detect breaches.

### What to Log

- Authentication events (success/failure)
- Authorization failures
- Input validation failures
- Suspicious activity patterns
- Administrative actions
- Application errors

### Prevention

```javascript
// Good: Comprehensive security logging
const logger = require('winston');

const securityLogger = logger.createLogger({
  level: 'info',
  format: logger.format.json(),
  defaultMeta: { service: 'api' },
  transports: [
    new logger.transports.File({ filename: 'security.log' }),
    new logger.transports.Console()
  ]
});

// Log authentication attempts
app.post('/api/auth/login', async (req, res) => {
  const { email, password } = req.body;

  securityLogger.info('Login attempt', {
    email,
    ip: req.ip,
    userAgent: req.get('user-agent'),
    timestamp: new Date().toISOString()
  });

  const user = await authenticateUser(email, password);

  if (!user) {
    securityLogger.warn('Failed login', {
      email,
      ip: req.ip,
      reason: 'invalid_credentials'
    });

    return res.status(401).json({ error: 'Invalid credentials' });
  }

  securityLogger.info('Successful login', {
    userId: user.id,
    email,
    ip: req.ip
  });

  res.json({ token: generateToken(user) });
});

// Never log sensitive data
// Bad: Logging passwords
securityLogger.info('User data', { email, password });

// Good: Sanitize before logging
securityLogger.info('User data', { email, password: '[REDACTED]' });
```

**Best Practices:**
- Log all authentication and authorization events
- Use centralized logging (ELK, Splunk, CloudWatch)
- Implement real-time alerting for suspicious activity
- Never log sensitive data (passwords, tokens, PII)
- Protect log integrity (append-only, signed logs)
- Retain logs for adequate period
- Implement automated log analysis

---

## 10. Mishandling of Exceptional Conditions (NEW in 2025)

**Risk**: Poor error and exception handling leads to unpredictable or insecure behavior.

> **Note**: SSRF (previously A10:2021) is now consolidated into A01: Broken Access Control.

### Common Issues

- **Fail-open behavior**: System grants access when errors occur
- **Incomplete error recovery**: Partial state changes left after failures
- **Improper input validation**: Missing validation for edge cases
- **Resource exhaustion**: Unhandled memory/connection limits
- **Inconsistent exception handling**: Different error paths with different security postures

### Attack Scenarios

- Triggering errors to bypass authentication checks
- Exploiting race conditions during error recovery
- Causing resource exhaustion via malformed inputs
- Extracting information from verbose error messages

### Prevention

```javascript
// Bad: Fail-open pattern
const checkAuthorization = async (user, resource) => {
  try {
    const hasAccess = await authService.check(user, resource);
    return hasAccess;
  } catch (error) {
    // DANGEROUS: Grants access on error!
    console.error('Auth check failed:', error);
    return true;
  }
};

// Good: Fail-secure pattern
const checkAuthorization = async (user, resource) => {
  try {
    const hasAccess = await authService.check(user, resource);
    return hasAccess;
  } catch (error) {
    // SECURE: Deny access on any error
    logger.error('Authorization check failed', {
      userId: user.id,
      resource,
      error: error.message
    });
    return false;
  }
};

// Bad: Incomplete transaction recovery
const transferFunds = async (from, to, amount) => {
  await debitAccount(from, amount);
  await creditAccount(to, amount); // If this fails, funds are lost!
};

// Good: Atomic transactions with proper recovery
const transferFunds = async (from, to, amount) => {
  const transaction = await db.beginTransaction();

  try {
    await debitAccount(from, amount, { transaction });
    await creditAccount(to, amount, { transaction });
    await transaction.commit();
  } catch (error) {
    await transaction.rollback();
    logger.error('Transfer failed, rolled back', { from, to, amount, error });
    throw new TransferError('Transfer failed, no funds moved');
  }
};

// Good: Resource exhaustion protection
const processUpload = async (req, res) => {
  const maxFileSize = 10 * 1024 * 1024; // 10MB
  const timeout = 30000; // 30 seconds

  const timeoutPromise = new Promise((_, reject) =>
    setTimeout(() => reject(new Error('Upload timeout')), timeout)
  );

  try {
    const result = await Promise.race([
      handleUpload(req, { maxSize: maxFileSize }),
      timeoutPromise
    ]);
    res.json(result);
  } catch (error) {
    if (error.message === 'Upload timeout') {
      return res.status(408).json({ error: 'Request timeout' });
    }
    if (error.code === 'LIMIT_FILE_SIZE') {
      return res.status(413).json({ error: 'File too large' });
    }
    logger.error('Upload failed', { error });
    res.status(500).json({ error: 'Upload failed' });
  }
};
```

**Best Practices:**

- **Fail-secure by default**: Deny access when errors occur
- **Use atomic transactions**: Ensure all-or-nothing operations
- **Implement timeouts**: Set limits on all external calls and long operations
- **Handle all error paths**: Every catch block should have explicit handling
- **Resource limits**: Set memory, connection, and time limits
- **Consistent error responses**: Same security posture regardless of error type
- **Log errors server-side**: Detailed logs internally, generic messages to clients
- **Test error conditions**: Include error scenarios in test suites

### SSRF Prevention (Now Part of A01)

For Server-Side Request Forgery prevention patterns, see the Broken Access Control section above. Key controls:

- Validate and allowlist all user-supplied URLs
- Block requests to private IP ranges (127.0.0.0/8, 10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16)
- Disable or validate URL redirects
- Use network segmentation

---

## References

- [OWASP Top 10](https://owasp.org/Top10/)
- [OWASP Cheat Sheet Series](https://cheatsheetseries.owasp.org/)
- [OWASP ASVS](https://owasp.org/www-project-application-security-verification-standard/)
