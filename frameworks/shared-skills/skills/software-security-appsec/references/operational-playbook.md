## Core Security Principles

**Defense in Depth**: Layer multiple security controls
**Least Privilege**: Grant minimum necessary permissions
**Secure by Default**: Security controls enabled out-of-the-box
**Fail Securely**: Errors should not expose sensitive data or bypass security
**Complete Mediation**: Validate every access attempt
**Open Design**: Security through architecture, not obscurity

See [references/secure-design-principles.md](secure-design-principles.md) for detailed implementation guidance.

---

## OWASP Top 10

1. **Broken Access Control** - Unauthorized access to resources
2. **Cryptographic Failures** - Weak encryption or exposed sensitive data
3. **Injection** - SQL, NoSQL, OS command, LDAP injection
4. **Security Misconfiguration** - Insecure defaults, incomplete configs
5. **Vulnerable Components** - Outdated libraries with known CVEs
6. **Insecure Design** - Missing threat modeling and secure patterns
7. **Authentication Failures** - Weak credential management
8. **Data Integrity Failures** - Unverified code/data modifications
9. **Logging Failures** - Insufficient monitoring and incident response
10. **Server-Side Request Forgery (SSRF)** - Unauthorized server requests

See [references/owasp-top-10.md](owasp-top-10.md) for detailed prevention strategies.

---

## Pattern: Authentication

**Use when:** Verifying user identity

### JWT-Based Authentication

```javascript
// Good: Secure JWT implementation
const jwt = require('jsonwebtoken');

// Generate token
const token = jwt.sign(
  { userId: user.id, role: user.role },
  process.env.JWT_SECRET,
  {
    expiresIn: '15m',
    algorithm: 'HS256',
    issuer: 'your-app',
    audience: 'your-api'
  }
);

// Verify token
const verifyToken = (token) => {
  try {
    return jwt.verify(token, process.env.JWT_SECRET, {
      algorithms: ['HS256'],
      issuer: 'your-app',
      audience: 'your-api'
    });
  } catch (error) {
    throw new AuthenticationError('Invalid token');
  }
};
```

### OAuth 2.0 Flow

```text
Client → Authorization Request → Auth Server
Auth Server → Authorization Grant → Client
Client → Access Token Request → Auth Server
Auth Server → Access Token → Client
Client → Protected Resource Request (with token) → Resource Server
```

**Security checklist:**

- [ ] Use secure token storage (httpOnly cookies or secure storage)
- [ ] Implement token refresh mechanism
- [ ] Set short token expiration (15-30 minutes)
- [ ] Use secure JWT signing algorithms (HS256, RS256)
- [ ] Validate token signature, expiration, issuer, and audience
- [ ] Never store sensitive data in JWT payload
- [ ] Implement token revocation/blacklisting
- [ ] Use HTTPS only

See [references/authentication-authorization.md](authentication-authorization.md) and [assets/web-application/template-authentication.md](../assets/web-application/template-authentication.md) for complete implementations.

---

## Pattern: Authorization

**Use when:** Controlling access to resources

### Role-Based Access Control (RBAC)

```javascript
// Good: RBAC middleware
const requireRole = (...allowedRoles) => {
  return (req, res, next) => {
    if (!req.user) {
      return res.status(401).json({ error: 'Not authenticated' });
    }

    if (!allowedRoles.includes(req.user.role)) {
      return res.status(403).json({ error: 'Insufficient permissions' });
    }

    next();
  };
};

// Usage
app.delete('/api/users/:id',
  authenticate,
  requireRole('admin', 'moderator'),
  deleteUser
);
```

### Attribute-Based Access Control (ABAC)

```javascript
// Good: Fine-grained ABAC
const canAccessResource = (user, resource, action) => {
  const policy = {
    subject: {
      userId: user.id,
      role: user.role,
      department: user.department
    },
    resource: {
      id: resource.id,
      ownerId: resource.ownerId,
      classification: resource.classification
    },
    action: action,
    context: {
      time: new Date(),
      ipAddress: user.ipAddress
    }
  };

  return evaluatePolicy(policy);
};
```

**Authorization Models:**
- **RBAC**: Simple role-based permissions (admin, user, moderator)
- **ABAC**: Complex attribute-based rules (time, location, resource attributes)
- **ReBAC**: Relationship-based (owner, collaborator, viewer)

**When to use:**
- RBAC: Limited, well-defined roles (<10 roles)
- ABAC: Complex, context-dependent permissions
- Hybrid: Combine RBAC + ABAC for most systems

See [references/authentication-authorization.md](authentication-authorization.md) and [assets/web-application/template-authorization.md](../assets/web-application/template-authorization.md).

---

## Pattern: Input Validation & Sanitization

**Use when:** Processing any user input

### Allowlist Validation

```javascript
// Good: Strict allowlist validation
const validateUsername = (username) => {
  // Allowlist: alphanumeric + underscore, 3-20 chars
  const regex = /^[a-zA-Z0-9_]{3,20}$/;

  if (!regex.test(username)) {
    throw new ValidationError('Invalid username format');
  }

  return username;
};

// Good: Email validation
const validateEmail = (email) => {
  const regex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;

  if (!regex.test(email) || email.length > 254) {
    throw new ValidationError('Invalid email format');
  }

  return email.toLowerCase();
};
```

### SQL Injection Prevention

```javascript
// Bad: String concatenation
const query = `SELECT * FROM users WHERE id = ${userId}`;

// Good: Parameterized queries
const query = 'SELECT * FROM users WHERE id = ?';
const results = await db.execute(query, [userId]);

// Good: ORM (Sequelize example)
const user = await User.findOne({ where: { id: userId } });
```

### XSS Prevention

```javascript
// Good: HTML sanitization
const DOMPurify = require('dompurify');
const { JSDOM } = require('jsdom');

const sanitizeHtml = (dirty) => {
  const window = new JSDOM('').window;
  const purify = DOMPurify(window);

  return purify.sanitize(dirty, {
    ALLOWED_TAGS: ['b', 'i', 'em', 'strong', 'a', 'p'],
    ALLOWED_ATTR: ['href']
  });
};

// Good: Output encoding
const escapeHtml = (text) => {
  const map = {
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#x27;'
  };

  return text.replace(/[&<>"']/g, (char) => map[char]);
};
```

**Advanced XSS Vectors (2024-2025):**

- SVG-based XSS via embedded scripts and foreignObject
- Mutation XSS (mXSS) through DOM reparsing
- Polyglot payloads working across multiple contexts
- Context-aware encoding (HTML, JavaScript, CSS, URL)

See [references/advanced-xss-techniques.md](advanced-xss-techniques.md) for comprehensive coverage of modern attack vectors and defenses.

### CSRF Prevention

```javascript
// Good: CSRF token validation
const csrf = require('csurf');
const csrfProtection = csrf({ cookie: true });

app.post('/api/transfer',
  csrfProtection,
  (req, res) => {
    // Token automatically validated
    processTransfer(req.body);
  }
);

// Client-side: Include token in requests
<input type="hidden" name="_csrf" value="{{csrfToken}}">
```

**Validation checklist:**

- [ ] Server-side validation (never trust client-side only)
- [ ] Allowlist approach (define what IS allowed)
- [ ] Input length limits
- [ ] Data type validation
- [ ] Parameterized queries for database operations
- [ ] HTML sanitization for user content
- [ ] Output encoding before rendering
- [ ] CSRF tokens for state-changing operations
- [ ] Content Security Policy (CSP) headers
- [ ] SVG file sanitization or conversion to raster (2024)
- [ ] File upload content validation (magic bytes)

See [references/input-validation.md](input-validation.md) for comprehensive patterns including SVG upload security.

---

## Pattern: Cryptography

**Use when:** Protecting sensitive data

### Password Hashing

```javascript
// Good: Modern password hashing
const bcrypt = require('bcrypt');

// Hash password
const hashPassword = async (password) => {
  const saltRounds = 12;
  return await bcrypt.hash(password, saltRounds);
};

// Verify password
const verifyPassword = async (password, hash) => {
  return await bcrypt.compare(password, hash);
};

// Alternative: Argon2 (recommended for new projects)
const argon2 = require('argon2');

const hashPassword = async (password) => {
  return await argon2.hash(password, {
    type: argon2.argon2id,
    memoryCost: 2 ** 16,
    timeCost: 3,
    parallelism: 1
  });
};
```

### Data Encryption

```javascript
// Good: AES-256-GCM encryption
const crypto = require('crypto');

const encrypt = (text, key) => {
  const iv = crypto.randomBytes(16);
  const cipher = crypto.createCipheriv('aes-256-gcm', key, iv);

  let encrypted = cipher.update(text, 'utf8', 'hex');
  encrypted += cipher.final('hex');

  const authTag = cipher.getAuthTag();

  return {
    encrypted,
    iv: iv.toString('hex'),
    authTag: authTag.toString('hex')
  };
};

const decrypt = (encrypted, key, iv, authTag) => {
  const decipher = crypto.createDecipheriv(
    'aes-256-gcm',
    key,
    Buffer.from(iv, 'hex')
  );

  decipher.setAuthTag(Buffer.from(authTag, 'hex'));

  let decrypted = decipher.update(encrypted, 'hex', 'utf8');
  decrypted += decipher.final('utf8');

  return decrypted;
};
```

**Cryptography standards:**
- **Password hashing**: bcrypt (cost 12+), scrypt, Argon2id
- **Symmetric encryption**: AES-256-GCM
- **Asymmetric encryption**: RSA-2048+ or ECC (secp256r1)
- **TLS**: Version 1.3 only
- **Random values**: Use crypto.randomBytes(), not Math.random()
- **Key derivation**: PBKDF2, scrypt, or Argon2

See [references/cryptography-standards.md](cryptography-standards.md) for detailed implementation.

---

## Pattern: Secure API Design

**Use when:** Building REST or GraphQL APIs

### Security Headers

```javascript
// Good: Comprehensive security headers
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
  }
}));

// Additional headers
app.use((req, res, next) => {
  res.setHeader('X-Content-Type-Options', 'nosniff');
  res.setHeader('X-Frame-Options', 'DENY');
  res.setHeader('X-XSS-Protection', '1; mode=block');
  res.setHeader('Referrer-Policy', 'strict-origin-when-cross-origin');
  next();
});
```

### Rate Limiting

```javascript
// Good: Rate limiting
const rateLimit = require('express-rate-limit');

const limiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 100, // Limit each IP to 100 requests per window
  message: 'Too many requests, please try again later',
  standardHeaders: true,
  legacyHeaders: false
});

app.use('/api/', limiter);

// Stricter limits for sensitive endpoints
const authLimiter = rateLimit({
  windowMs: 15 * 60 * 1000,
  max: 5,
  skipSuccessfulRequests: true
});

app.post('/api/auth/login', authLimiter, loginHandler);
```

### CORS Configuration

```javascript
// Good: Strict CORS configuration
const cors = require('cors');

const corsOptions = {
  origin: (origin, callback) => {
    const allowedOrigins = [
      'https://app.example.com',
      'https://admin.example.com'
    ];

    if (!origin || allowedOrigins.includes(origin)) {
      callback(null, true);
    } else {
      callback(new Error('Not allowed by CORS'));
    }
  },
  credentials: true,
  optionsSuccessStatus: 200,
  methods: ['GET', 'POST', 'PUT', 'DELETE'],
  allowedHeaders: ['Content-Type', 'Authorization']
};

app.use(cors(corsOptions));
```

See [assets/api/template-secure-api.md](../assets/api/template-secure-api.md) for complete API security implementation.

---

## Common Vulnerabilities & Fixes

### Path Traversal

```javascript
// Bad: Unsafe file access
const filePath = path.join('/uploads', req.params.filename);

// Good: Validate and sanitize
const sanitizeFilename = (filename) => {
  // Remove path separators and null bytes
  const clean = filename.replace(/[\/\\.\0]/g, '');

  if (clean !== filename || clean.length === 0) {
    throw new ValidationError('Invalid filename');
  }

  return clean;
};

const filePath = path.join('/uploads', sanitizeFilename(req.params.filename));
```

### Command Injection

```javascript
// Bad: Shell command with user input
exec(`convert ${userInput} output.png`);

// Good: Use libraries or sanitize
const sharp = require('sharp');
await sharp(validatedInput).toFile('output.png');

// If shell is necessary: strict validation + escaping
const { execFile } = require('child_process');
const allowedCommands = ['convert', 'ffmpeg'];

if (!allowedCommands.includes(command)) {
  throw new Error('Invalid command');
}

execFile(command, [validatedArg1, validatedArg2]);
```

### Insecure Deserialization

```javascript
// Bad: Unsafe deserialization
const obj = eval(userInput);

// Good: Use JSON.parse with validation
const parseData = (input) => {
  try {
    const data = JSON.parse(input);
    return validateSchema(data);
  } catch (error) {
    throw new ValidationError('Invalid data format');
  }
};
```

See [references/common-vulnerabilities.md](common-vulnerabilities.md) for comprehensive vulnerability catalog.

---

## Security Testing Checklist

**Authentication:**
- [ ] Password strength requirements enforced
- [ ] Multi-factor authentication available
- [ ] Account lockout after failed attempts
- [ ] Secure password reset flow
- [ ] Session timeout configured

**Authorization:**
- [ ] Principle of least privilege applied
- [ ] Authorization checked on every request
- [ ] Direct object references protected
- [ ] Vertical privilege escalation prevented
- [ ] Horizontal privilege escalation prevented

**Input Validation:**
- [ ] Server-side validation on all inputs
- [ ] Allowlist validation approach
- [ ] Output encoding before rendering
- [ ] Parameterized queries for database
- [ ] File upload validation (type, size, content)

**Data Protection:**
- [ ] Sensitive data encrypted at rest
- [ ] TLS 1.3 for data in transit
- [ ] Secrets in environment variables, not code
- [ ] PII handling complies with regulations
- [ ] Secure key management

**Error Handling:**
- [ ] Generic error messages to users
- [ ] Detailed errors logged server-side
- [ ] Stack traces not exposed
- [ ] Failed operations don't leak information

**Logging & Monitoring:**
- [ ] Security events logged
- [ ] Sensitive data not in logs
- [ ] Log integrity protected
- [ ] Alerting for suspicious activity
- [ ] Incident response plan documented

---

## Resources (Detailed Guides)

For comprehensive implementation guides, see:

- [OWASP Top 10 Guide](owasp-top-10.md)
- [Authentication & Authorization Patterns](authentication-authorization.md)
- [Input Validation & Sanitization](input-validation.md) - Including SVG upload security
- [Advanced XSS Techniques](advanced-xss-techniques.md) - SVG XSS, mXSS, polyglots, context-aware encoding (2024-2025)
- [Cryptography Standards](cryptography-standards.md)
- [Secure Design Principles](secure-design-principles.md)
- [Common Vulnerabilities Catalog](common-vulnerabilities.md)

## Templates (Production-Ready)

### Web Application Templates

- [Authentication Template](../assets/web-application/template-authentication.md) — JWT, OAuth2, sessions, MFA implementation
- [Authorization Template](../assets/web-application/template-authorization.md) — RBAC/ABAC/ReBAC patterns

### API Templates

- [Secure API Template](../assets/api/template-secure-api.md) — API gateway, rate limiting, CORS, security headers

### Cloud-Native Templates

- [Cryptography Template](../assets/cloud-native/crypto-security.md) — Encryption, key management, HSM integration

## External Resources

See [data/sources.json](../data/sources.json) for 70+ curated security resources including OWASP 2025, supply chain security, zero trust, API security, and compliance standards.
