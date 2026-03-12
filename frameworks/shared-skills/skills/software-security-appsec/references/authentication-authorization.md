# Authentication & Authorization Patterns

Comprehensive guide to implementing secure authentication and authorization in modern applications (Jan 2026).

---

## Passkeys & WebAuthn (Primary Auth for 2026+)

**Status**: Phishing-resistant passwordless auth with broad platform support; recommended for new applications. Verify current adoption and regulatory guidance for your target markets.

### Why Passkeys?

- Phishing-resistant (public key cryptography; no shared secrets)
- Reduces credential stuffing and password reset exposure
- Works with platform authenticators (Touch ID/Face ID/Windows Hello) and roaming security keys
- Enables step-up authentication and transaction confirmation

**References**: See `data/sources.json` → `passkeys_webauthn_2026`.

### Implementation (WebAuthn Level 3)

```javascript
// 1. Registration - Create a new passkey
const registerPasskey = async (userId) => {
  // Generate challenge server-side
  const challenge = crypto.randomBytes(32);
  await storeChallenge(userId, challenge);

  // Return options for navigator.credentials.create()
  return {
    challenge: challenge.toString('base64url'),
    rp: {
      name: 'Your App',
      id: 'yourapp.com' // Must match origin
    },
    user: {
      id: Buffer.from(userId).toString('base64url'),
      name: user.email,
      displayName: user.name
    },
    pubKeyCredParams: [
      { alg: -7, type: 'public-key' },   // ES256
      { alg: -257, type: 'public-key' }  // RS256
    ],
    authenticatorSelection: {
      authenticatorAttachment: 'platform', // or 'cross-platform' for security keys
      residentKey: 'required',
      userVerification: 'required'
    },
    timeout: 60000,
    attestation: 'none' // Use 'direct' if you need device attestation
  };
};

// 2. Client-side registration
const credential = await navigator.credentials.create({
  publicKey: registrationOptions
});

// Send credential to server for verification and storage

// 3. Authentication - Verify passkey
const authenticateWithPasskey = async (userId) => {
  const challenge = crypto.randomBytes(32);
  await storeChallenge(userId, challenge);

  return {
    challenge: challenge.toString('base64url'),
    rpId: 'yourapp.com',
    allowCredentials: await getUserCredentials(userId), // Optional: for non-discoverable
    userVerification: 'required',
    timeout: 60000
  };
};

// 4. Client-side authentication
const assertion = await navigator.credentials.get({
  publicKey: authenticationOptions
});

// 5. Server-side verification
const verifyAssertion = async (assertion, expectedChallenge) => {
  // Verify challenge matches
  // Verify origin matches rpId
  // Verify signature with stored public key
  // Check sign count to detect cloned authenticators
  // Return user on success
};
```

### Migration Strategy

```text
Phase 1: Add passkey enrollment alongside passwords
Phase 2: Prompt users to add passkeys at login
Phase 3: Offer passwordless option for passkey users
Phase 4: Deprecate password-only accounts (2027+)
```

### Best Practices

- **Always offer password fallback** during transition
- **Store public keys securely** (not in localStorage)
- **Implement account recovery** via backup codes or secondary passkeys
- **Use platform authenticators** for consumer apps (Touch ID, Face ID, Windows Hello)
- **Use security keys** for high-security enterprise (YubiKey, etc.)

### Libraries

| Platform | Library |
|----------|---------|
| Node.js | `@simplewebauthn/server` |
| Python | `py_webauthn` |
| Go | `github.com/go-webauthn/webauthn` |
| .NET | `Fido2.AspNet` |

---

## Authentication Patterns

### Pattern 1: JWT-Based Authentication

**Use when:** Stateless authentication for APIs and SPAs (use with passkeys or as fallback)

```javascript
const jwt = require('jsonwebtoken');
const bcrypt = require('bcrypt');

// 1. User registration
const registerUser = async (email, password) => {
  // Validate password strength
  if (password.length < 12) {
    throw new ValidationError('Password must be at least 12 characters');
  }

  // Hash password
  const passwordHash = await bcrypt.hash(password, 12);

  // Create user
  const user = await User.create({
    email,
    passwordHash
  });

  return user;
};

// 2. User login
const loginUser = async (email, password) => {
  const user = await User.findOne({ email });

  if (!user) {
    // Use constant-time comparison to prevent timing attacks
    await bcrypt.compare(password, '$2b$12$constantTimeHashValue');
    throw new AuthenticationError('Invalid credentials');
  }

  const valid = await bcrypt.compare(password, user.passwordHash);

  if (!valid) {
    throw new AuthenticationError('Invalid credentials');
  }

  // Generate access token (short-lived)
  const accessToken = jwt.sign(
    {
      userId: user.id,
      email: user.email,
      role: user.role
    },
    process.env.JWT_SECRET,
    {
      expiresIn: '15m',
      algorithm: 'HS256',
      issuer: 'your-app',
      audience: 'your-api'
    }
  );

  // Generate refresh token (long-lived)
  const refreshToken = jwt.sign(
    { userId: user.id, tokenVersion: user.tokenVersion },
    process.env.JWT_REFRESH_SECRET,
    {
      expiresIn: '7d',
      algorithm: 'HS256'
    }
  );

  // Store refresh token hash
  const refreshTokenHash = await bcrypt.hash(refreshToken, 10);
  await RefreshToken.create({
    userId: user.id,
    tokenHash: refreshTokenHash,
    expiresAt: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000)
  });

  return { accessToken, refreshToken };
};

// 3. Token verification middleware
const authenticate = async (req, res, next) => {
  const authHeader = req.headers.authorization;

  if (!authHeader || !authHeader.startsWith('Bearer ')) {
    return res.status(401).json({ error: 'Missing authentication token' });
  }

  const token = authHeader.substring(7);

  try {
    const payload = jwt.verify(token, process.env.JWT_SECRET, {
      algorithms: ['HS256'],
      issuer: 'your-app',
      audience: 'your-api'
    });

    req.user = payload;
    next();
  } catch (error) {
    if (error.name === 'TokenExpiredError') {
      return res.status(401).json({ error: 'Token expired' });
    }

    return res.status(401).json({ error: 'Invalid token' });
  }
};

// 4. Token refresh
const refreshAccessToken = async (refreshToken) => {
  const payload = jwt.verify(refreshToken, process.env.JWT_REFRESH_SECRET, {
    algorithms: ['HS256']
  });

  const user = await User.findById(payload.userId);

  if (!user || user.tokenVersion !== payload.tokenVersion) {
    throw new AuthenticationError('Invalid refresh token');
  }

  // Verify refresh token exists in database
  const refreshTokenHash = await bcrypt.hash(refreshToken, 10);
  const storedToken = await RefreshToken.findOne({
    userId: user.id,
    expiresAt: { $gt: new Date() }
  });

  if (!storedToken) {
    throw new AuthenticationError('Refresh token not found or expired');
  }

  // Generate new access token
  const accessToken = jwt.sign(
    {
      userId: user.id,
      email: user.email,
      role: user.role
    },
    process.env.JWT_SECRET,
    {
      expiresIn: '15m',
      algorithm: 'HS256',
      issuer: 'your-app',
      audience: 'your-api'
    }
  );

  return accessToken;
};

// 5. Logout (invalidate refresh token)
const logoutUser = async (userId, refreshToken) => {
  await RefreshToken.deleteMany({ userId });

  // Optionally increment tokenVersion to invalidate all existing tokens
  await User.findByIdAndUpdate(userId, { $inc: { tokenVersion: 1 } });
};
```

**Security Considerations:**
- Use short expiration for access tokens (15-30 minutes)
- Store refresh tokens securely (httpOnly cookies or secure storage)
- Implement token rotation on refresh
- Use strong JWT signing algorithms (HS256, RS256)
- Never include sensitive data in JWT payload
- Validate all JWT claims (iss, aud, exp)

---

### Pattern 2: Session-Based Authentication

**Use when:** Traditional web applications with server-side rendering

```javascript
const session = require('express-session');
const RedisStore = require('connect-redis').default;
const { createClient } = require('redis');

// 1. Configure session store
const redisClient = createClient({
  host: process.env.REDIS_HOST,
  port: process.env.REDIS_PORT
});

redisClient.connect();

app.use(session({
  store: new RedisStore({ client: redisClient }),
  secret: process.env.SESSION_SECRET,
  resave: false,
  saveUninitialized: false,
  cookie: {
    secure: true,        // HTTPS only
    httpOnly: true,      // No client-side access
    sameSite: 'strict',  // CSRF protection
    maxAge: 30 * 60 * 1000 // 30 minutes
  }
}));

// 2. Login handler
app.post('/auth/login', async (req, res) => {
  const { email, password } = req.body;

  const user = await authenticateUser(email, password);

  // Regenerate session ID to prevent fixation
  req.session.regenerate((err) => {
    if (err) {
      return res.status(500).json({ error: 'Session error' });
    }

    req.session.userId = user.id;
    req.session.role = user.role;

    res.json({ message: 'Logged in successfully' });
  });
});

// 3. Authentication middleware
const requireAuth = (req, res, next) => {
  if (!req.session.userId) {
    return res.status(401).json({ error: 'Not authenticated' });
  }

  next();
};

// 4. Logout handler
app.post('/auth/logout', (req, res) => {
  req.session.destroy((err) => {
    if (err) {
      return res.status(500).json({ error: 'Logout failed' });
    }

    res.clearCookie('connect.sid');
    res.json({ message: 'Logged out successfully' });
  });
});
```

**Security Considerations:**
- Use secure session storage (Redis, database)
- Set secure cookie flags (secure, httpOnly, sameSite)
- Regenerate session ID on login
- Implement session timeout
- Clear sessions on logout

---

### Pattern 3: OAuth 2.0 / OpenID Connect

**Use when:** Third-party authentication (Google, GitHub, etc.)

```javascript
const passport = require('passport');
const GoogleStrategy = require('passport-google-oauth20').Strategy;

// 1. Configure OAuth strategy
passport.use(new GoogleStrategy({
  clientID: process.env.GOOGLE_CLIENT_ID,
  clientSecret: process.env.GOOGLE_CLIENT_SECRET,
  callbackURL: 'https://yourapp.com/auth/google/callback',
  scope: ['profile', 'email']
},
async (accessToken, refreshToken, profile, done) => {
  try {
    // Find or create user
    let user = await User.findOne({ googleId: profile.id });

    if (!user) {
      user = await User.create({
        googleId: profile.id,
        email: profile.emails[0].value,
        name: profile.displayName,
        avatar: profile.photos[0].value
      });
    }

    return done(null, user);
  } catch (error) {
    return done(error, null);
  }
}));

// 2. OAuth routes
app.get('/auth/google',
  passport.authenticate('google', { scope: ['profile', 'email'] })
);

app.get('/auth/google/callback',
  passport.authenticate('google', { failureRedirect: '/login' }),
  (req, res) => {
    // Generate JWT for subsequent API requests
    const token = generateJWT(req.user);
    res.redirect(`/dashboard?token=${token}`);
  }
);
```

**Security Considerations:**
- Validate state parameter to prevent CSRF
- Use PKCE (Proof Key for Code Exchange) for SPAs
- Verify token signatures from OAuth provider
- Store OAuth tokens securely
- Implement token refresh flow

---

### Pattern 4: Multi-Factor Authentication (MFA)

**Use when:** High-security applications requiring additional verification

```javascript
const speakeasy = require('speakeasy');
const QRCode = require('qrcode');

// 1. Enable MFA (generate secret)
const enableMFA = async (userId) => {
  const secret = speakeasy.generateSecret({
    name: `YourApp (${userId})`,
    length: 32
  });

  // Store secret
  await User.findByIdAndUpdate(userId, {
    mfaSecret: secret.base32,
    mfaEnabled: false // Enable after verification
  });

  // Generate QR code
  const qrCode = await QRCode.toDataURL(secret.otpauth_url);

  return {
    secret: secret.base32,
    qrCode
  };
};

// 2. Verify MFA setup
const verifyMFASetup = async (userId, token) => {
  const user = await User.findById(userId);

  const verified = speakeasy.totp.verify({
    secret: user.mfaSecret,
    encoding: 'base32',
    token: token,
    window: 2 // Allow 2 time steps (60 seconds)
  });

  if (verified) {
    await User.findByIdAndUpdate(userId, { mfaEnabled: true });
    return true;
  }

  return false;
};

// 3. Login with MFA
const loginWithMFA = async (email, password, mfaToken) => {
  const user = await authenticateUser(email, password);

  if (user.mfaEnabled) {
    const verified = speakeasy.totp.verify({
      secret: user.mfaSecret,
      encoding: 'base32',
      token: mfaToken,
      window: 2
    });

    if (!verified) {
      throw new AuthenticationError('Invalid MFA code');
    }
  }

  return generateTokens(user);
};

// 4. Backup codes
const generateBackupCodes = async (userId) => {
  const codes = [];

  for (let i = 0; i < 10; i++) {
    const code = crypto.randomBytes(4).toString('hex');
    codes.push(code);
  }

  // Hash and store codes
  const hashedCodes = await Promise.all(
    codes.map(code => bcrypt.hash(code, 10))
  );

  await User.findByIdAndUpdate(userId, {
    mfaBackupCodes: hashedCodes
  });

  return codes; // Return only once, user must save them
};
```

**Security Considerations:**
- Use TOTP (Time-based One-Time Password) algorithm
- Allow time window for code validation
- Provide backup codes for account recovery
- Implement rate limiting on MFA attempts
- Allow MFA disable only with additional verification

---

## Authorization Patterns

### Pattern 1: Role-Based Access Control (RBAC)

**Use when:** Simple, well-defined permission sets

```javascript
// 1. Define roles
const ROLES = {
  ADMIN: 'admin',
  MODERATOR: 'moderator',
  USER: 'user',
  GUEST: 'guest'
};

// 2. Define permissions
const PERMISSIONS = {
  USERS_READ: 'users:read',
  USERS_WRITE: 'users:write',
  USERS_DELETE: 'users:delete',
  POSTS_READ: 'posts:read',
  POSTS_WRITE: 'posts:write',
  POSTS_DELETE: 'posts:delete'
};

// 3. Role-permission mapping
const rolePermissions = {
  [ROLES.ADMIN]: [
    PERMISSIONS.USERS_READ,
    PERMISSIONS.USERS_WRITE,
    PERMISSIONS.USERS_DELETE,
    PERMISSIONS.POSTS_READ,
    PERMISSIONS.POSTS_WRITE,
    PERMISSIONS.POSTS_DELETE
  ],
  [ROLES.MODERATOR]: [
    PERMISSIONS.USERS_READ,
    PERMISSIONS.POSTS_READ,
    PERMISSIONS.POSTS_WRITE,
    PERMISSIONS.POSTS_DELETE
  ],
  [ROLES.USER]: [
    PERMISSIONS.POSTS_READ,
    PERMISSIONS.POSTS_WRITE
  ],
  [ROLES.GUEST]: [
    PERMISSIONS.POSTS_READ
  ]
};

// 4. Authorization middleware
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

const requirePermission = (...requiredPermissions) => {
  return (req, res, next) => {
    if (!req.user) {
      return res.status(401).json({ error: 'Not authenticated' });
    }

    const userPermissions = rolePermissions[req.user.role] || [];

    const hasPermission = requiredPermissions.every(
      permission => userPermissions.includes(permission)
    );

    if (!hasPermission) {
      return res.status(403).json({ error: 'Insufficient permissions' });
    }

    next();
  };
};

// 5. Usage
app.get('/api/users',
  authenticate,
  requirePermission(PERMISSIONS.USERS_READ),
  listUsers
);

app.delete('/api/users/:id',
  authenticate,
  requireRole(ROLES.ADMIN),
  deleteUser
);
```

---

### Pattern 2: Attribute-Based Access Control (ABAC)

**Use when:** Complex, context-dependent authorization

```javascript
// 1. Policy engine
class PolicyEngine {
  constructor() {
    this.policies = [];
  }

  addPolicy(policy) {
    this.policies.push(policy);
  }

  async evaluate(context) {
    for (const policy of this.policies) {
      const result = await policy.evaluate(context);

      if (result === 'allow') return true;
      if (result === 'deny') return false;
    }

    // Deny by default
    return false;
  }
}

// 2. Example policy: Users can edit their own posts
class OwnResourcePolicy {
  async evaluate(context) {
    const { user, resource, action } = context;

    if (action === 'edit' && resource.type === 'post') {
      return resource.authorId === user.id ? 'allow' : 'deny';
    }

    return 'continue';
  }
}

// 3. Example policy: Admins can do anything
class AdminPolicy {
  async evaluate(context) {
    if (context.user.role === 'admin') {
      return 'allow';
    }

    return 'continue';
  }
}

// 4. Example policy: Office hours restriction
class TimeBasedPolicy {
  async evaluate(context) {
    const { user, action } = context;

    // Sensitive operations only during business hours
    if (action === 'delete' && user.role !== 'admin') {
      const hour = new Date().getHours();

      if (hour < 9 || hour > 17) {
        return 'deny';
      }
    }

    return 'continue';
  }
}

// 5. Initialize policy engine
const policyEngine = new PolicyEngine();
policyEngine.addPolicy(new AdminPolicy());
policyEngine.addPolicy(new OwnResourcePolicy());
policyEngine.addPolicy(new TimeBasedPolicy());

// 6. Authorization middleware
const authorize = (action, resourceType) => {
  return async (req, res, next) => {
    const resourceId = req.params.id;
    const resource = await loadResource(resourceType, resourceId);

    const context = {
      user: req.user,
      resource,
      action,
      environment: {
        time: new Date(),
        ipAddress: req.ip
      }
    };

    const allowed = await policyEngine.evaluate(context);

    if (!allowed) {
      return res.status(403).json({ error: 'Access denied' });
    }

    req.resource = resource;
    next();
  };
};

// 7. Usage
app.put('/api/posts/:id',
  authenticate,
  authorize('edit', 'post'),
  updatePost
);
```

---

### Pattern 3: Relationship-Based Access Control (ReBAC)

**Use when:** Access based on relationships (owner, collaborator, viewer)

```javascript
// 1. Define relationships
const RELATIONSHIPS = {
  OWNER: 'owner',
  EDITOR: 'editor',
  VIEWER: 'viewer'
};

// 2. Permission model
const ResourcePermission = mongoose.model('ResourcePermission', {
  resourceType: String,
  resourceId: String,
  userId: String,
  relationship: String,
  grantedAt: Date
});

// 3. Check relationship
const hasRelationship = async (userId, resourceType, resourceId, relationship) => {
  const permission = await ResourcePermission.findOne({
    userId,
    resourceType,
    resourceId,
    relationship
  });

  return !!permission;
};

// 4. Grant access
const grantAccess = async (userId, resourceType, resourceId, relationship) => {
  await ResourcePermission.create({
    userId,
    resourceType,
    resourceId,
    relationship,
    grantedAt: new Date()
  });
};

// 5. Revoke access
const revokeAccess = async (userId, resourceType, resourceId) => {
  await ResourcePermission.deleteOne({
    userId,
    resourceType,
    resourceId
  });
};

// 6. Authorization middleware
const requireRelationship = (resourceType, ...allowedRelationships) => {
  return async (req, res, next) => {
    const resourceId = req.params.id;

    for (const relationship of allowedRelationships) {
      const hasAccess = await hasRelationship(
        req.user.id,
        resourceType,
        resourceId,
        relationship
      );

      if (hasAccess) {
        return next();
      }
    }

    return res.status(403).json({ error: 'Access denied' });
  };
};

// 7. Usage
app.get('/api/documents/:id',
  authenticate,
  requireRelationship('document', RELATIONSHIPS.OWNER, RELATIONSHIPS.EDITOR, RELATIONSHIPS.VIEWER),
  getDocument
);

app.put('/api/documents/:id',
  authenticate,
  requireRelationship('document', RELATIONSHIPS.OWNER, RELATIONSHIPS.EDITOR),
  updateDocument
);
```

---

## Best Practices

### Password Security

```javascript
// 1. Password strength validation
const validatePasswordStrength = (password) => {
  const minLength = 12;
  const hasUpperCase = /[A-Z]/.test(password);
  const hasLowerCase = /[a-z]/.test(password);
  const hasNumbers = /\d/.test(password);
  const hasSpecialChar = /[!@#$%^&*(),.?":{}|<>]/.test(password);

  if (password.length < minLength) {
    throw new ValidationError(`Password must be at least ${minLength} characters`);
  }

  const complexityScore = [hasUpperCase, hasLowerCase, hasNumbers, hasSpecialChar]
    .filter(Boolean).length;

  if (complexityScore < 3) {
    throw new ValidationError('Password must include at least 3 of: uppercase, lowercase, numbers, special characters');
  }

  // Check against common passwords
  const commonPasswords = ['password123', 'qwerty123', 'admin123'];
  if (commonPasswords.includes(password.toLowerCase())) {
    throw new ValidationError('Password is too common');
  }

  return true;
};

// 2. Password reset flow
const initiatePasswordReset = async (email) => {
  const user = await User.findOne({ email });

  if (!user) {
    // Don't reveal if email exists
    return;
  }

  // Generate reset token
  const resetToken = crypto.randomBytes(32).toString('hex');
  const resetTokenHash = await bcrypt.hash(resetToken, 10);

  await User.findByIdAndUpdate(user.id, {
    resetTokenHash,
    resetTokenExpires: new Date(Date.now() + 60 * 60 * 1000) // 1 hour
  });

  // Send email with reset link
  await sendEmail(email, 'Password Reset', `
    Reset your password: https://yourapp.com/reset-password?token=${resetToken}
    This link expires in 1 hour.
  `);
};

const resetPassword = async (token, newPassword) => {
  const users = await User.find({
    resetTokenExpires: { $gt: new Date() }
  });

  for (const user of users) {
    const valid = await bcrypt.compare(token, user.resetTokenHash);

    if (valid) {
      validatePasswordStrength(newPassword);

      const passwordHash = await bcrypt.hash(newPassword, 12);

      await User.findByIdAndUpdate(user.id, {
        passwordHash,
        resetTokenHash: null,
        resetTokenExpires: null,
        tokenVersion: user.tokenVersion + 1 // Invalidate existing tokens
      });

      return true;
    }
  }

  throw new ValidationError('Invalid or expired reset token');
};
```

### Rate Limiting

```javascript
const rateLimit = require('express-rate-limit');
const RedisStore = require('rate-limit-redis');
const { createClient } = require('redis');

const redisClient = createClient();

// General API rate limiter
const apiLimiter = rateLimit({
  store: new RedisStore({ client: redisClient }),
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 100,
  message: 'Too many requests',
  standardHeaders: true,
  legacyHeaders: false
});

// Strict limiter for authentication endpoints
const authLimiter = rateLimit({
  store: new RedisStore({ client: redisClient }),
  windowMs: 15 * 60 * 1000,
  max: 5,
  skipSuccessfulRequests: true,
  message: 'Too many login attempts'
});

app.use('/api/', apiLimiter);
app.use('/api/auth/', authLimiter);
```

---

## References

- [OAuth 2.0 RFC 6749](https://tools.ietf.org/html/rfc6749)
- [JWT Best Practices](https://auth0.com/docs/secure/tokens/json-web-tokens)
- [OWASP Authentication Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html)
- [NIST Digital Identity Guidelines](https://pages.nist.gov/800-63-3/)
