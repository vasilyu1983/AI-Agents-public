# Authentication Implementation Template

Copy-paste ready implementation for secure authentication with JWT, sessions, and MFA.

---

## JWT Authentication (Recommended for APIs)

### Dependencies

```bash
npm install bcrypt jsonwebtoken express express-rate-limit
```

### Environment Variables

```bash
# .env
JWT_SECRET=your-secret-key-min-32-characters
JWT_REFRESH_SECRET=your-refresh-secret-key-min-32-characters
JWT_EXPIRES_IN=15m
JWT_REFRESH_EXPIRES_IN=7d
BCRYPT_ROUNDS=12
```

### User Model

```javascript
// models/User.js
const mongoose = require('mongoose');

const userSchema = new mongoose.Schema({
  email: {
    type: String,
    required: true,
    unique: true,
    lowercase: true,
    trim: true
  },
  passwordHash: {
    type: String,
    required: true
  },
  name: {
    type: String,
    required: true
  },
  role: {
    type: String,
    enum: ['user', 'moderator', 'admin'],
    default: 'user'
  },
  emailVerified: {
    type: Boolean,
    default: false
  },
  mfaEnabled: {
    type: Boolean,
    default: false
  },
  mfaSecret: String,
  tokenVersion: {
    type: Number,
    default: 0
  },
  failedLoginAttempts: {
    type: Number,
    default: 0
  },
  lockedUntil: Date,
  createdAt: {
    type: Date,
    default: Date.now
  }
});

module.exports = mongoose.model('User', userSchema);
```

### Password Utilities

```javascript
// utils/password.js
const bcrypt = require('bcrypt');

const BCRYPT_ROUNDS = parseInt(process.env.BCRYPT_ROUNDS) || 12;

const hashPassword = async (password) => {
  return await bcrypt.hash(password, BCRYPT_ROUNDS);
};

const verifyPassword = async (password, hash) => {
  return await bcrypt.compare(password, hash);
};

const validatePasswordStrength = (password) => {
  const minLength = 12;
  const hasUpperCase = /[A-Z]/.test(password);
  const hasLowerCase = /[a-z]/.test(password);
  const hasNumbers = /\d/.test(password);
  const hasSpecialChar = /[!@#$%^&*(),.?":{}|<>]/.test(password);

  if (password.length < minLength) {
    throw new Error(`Password must be at least ${minLength} characters`);
  }

  const complexityScore = [hasUpperCase, hasLowerCase, hasNumbers, hasSpecialChar]
    .filter(Boolean).length;

  if (complexityScore < 3) {
    throw new Error('Password must include at least 3 of: uppercase, lowercase, numbers, special characters');
  }

  return true;
};

module.exports = {
  hashPassword,
  verifyPassword,
  validatePasswordStrength
};
```

### JWT Utilities

```javascript
// utils/jwt.js
const jwt = require('jsonwebtoken');

const JWT_SECRET = process.env.JWT_SECRET;
const JWT_REFRESH_SECRET = process.env.JWT_REFRESH_SECRET;
const JWT_EXPIRES_IN = process.env.JWT_EXPIRES_IN || '15m';
const JWT_REFRESH_EXPIRES_IN = process.env.JWT_REFRESH_EXPIRES_IN || '7d';

const generateAccessToken = (user) => {
  return jwt.sign(
    {
      userId: user.id,
      email: user.email,
      role: user.role
    },
    JWT_SECRET,
    {
      expiresIn: JWT_EXPIRES_IN,
      algorithm: 'HS256',
      issuer: 'your-app',
      audience: 'your-api'
    }
  );
};

const generateRefreshToken = (user) => {
  return jwt.sign(
    {
      userId: user.id,
      tokenVersion: user.tokenVersion
    },
    JWT_REFRESH_SECRET,
    {
      expiresIn: JWT_REFRESH_EXPIRES_IN,
      algorithm: 'HS256'
    }
  );
};

const verifyAccessToken = (token) => {
  try {
    return jwt.verify(token, JWT_SECRET, {
      algorithms: ['HS256'],
      issuer: 'your-app',
      audience: 'your-api'
    });
  } catch (error) {
    throw new Error('Invalid or expired token');
  }
};

const verifyRefreshToken = (token) => {
  try {
    return jwt.verify(token, JWT_REFRESH_SECRET, {
      algorithms: ['HS256']
    });
  } catch (error) {
    throw new Error('Invalid or expired refresh token');
  }
};

module.exports = {
  generateAccessToken,
  generateRefreshToken,
  verifyAccessToken,
  verifyRefreshToken
};
```

### Authentication Middleware

```javascript
// middleware/authenticate.js
const { verifyAccessToken } = require('../utils/jwt');

const authenticate = async (req, res, next) => {
  const authHeader = req.headers.authorization;

  if (!authHeader || !authHeader.startsWith('Bearer ')) {
    return res.status(401).json({ error: 'Missing authentication token' });
  }

  const token = authHeader.substring(7);

  try {
    const payload = verifyAccessToken(token);
    req.user = payload;
    next();
  } catch (error) {
    return res.status(401).json({ error: error.message });
  }
};

module.exports = authenticate;
```

### Auth Routes

```javascript
// routes/auth.js
const express = require('express');
const rateLimit = require('express-rate-limit');
const User = require('../models/User');
const { hashPassword, verifyPassword, validatePasswordStrength } = require('../utils/password');
const { generateAccessToken, generateRefreshToken, verifyRefreshToken } = require('../utils/jwt');

const router = express.Router();

// Rate limiters
const registerLimiter = rateLimit({
  windowMs: 60 * 60 * 1000, // 1 hour
  max: 5,
  message: 'Too many registration attempts, please try again later'
});

const loginLimiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 5,
  skipSuccessfulRequests: true,
  message: 'Too many login attempts, please try again later'
});

// Register
router.post('/register', registerLimiter, async (req, res) => {
  try {
    const { email, password, name } = req.body;

    // Validate inputs
    if (!email || !password || !name) {
      return res.status(400).json({ error: 'Missing required fields' });
    }

    // Validate password strength
    validatePasswordStrength(password);

    // Check if user exists
    const existingUser = await User.findOne({ email });
    if (existingUser) {
      return res.status(400).json({ error: 'Email already registered' });
    }

    // Hash password
    const passwordHash = await hashPassword(password);

    // Create user
    const user = await User.create({
      email,
      passwordHash,
      name
    });

    // Generate tokens
    const accessToken = generateAccessToken(user);
    const refreshToken = generateRefreshToken(user);

    res.status(201).json({
      user: {
        id: user.id,
        email: user.email,
        name: user.name,
        role: user.role
      },
      accessToken,
      refreshToken
    });
  } catch (error) {
    res.status(400).json({ error: error.message });
  }
});

// Login
router.post('/login', loginLimiter, async (req, res) => {
  try {
    const { email, password } = req.body;

    if (!email || !password) {
      return res.status(400).json({ error: 'Missing email or password' });
    }

    // Find user
    const user = await User.findOne({ email });

    // Check account lockout
    if (user && user.lockedUntil && user.lockedUntil > Date.now()) {
      const minutesRemaining = Math.ceil((user.lockedUntil - Date.now()) / 60000);
      return res.status(429).json({
        error: `Account locked. Try again in ${minutesRemaining} minutes`
      });
    }

    // Verify password (constant-time response)
    if (!user) {
      await verifyPassword(password, '$2b$12$constantTimeHashValue');
      return res.status(401).json({ error: 'Invalid credentials' });
    }

    const validPassword = await verifyPassword(password, user.passwordHash);

    if (!validPassword) {
      // Increment failed attempts
      user.failedLoginAttempts += 1;

      // Lock account after 5 failed attempts
      if (user.failedLoginAttempts >= 5) {
        user.lockedUntil = new Date(Date.now() + 30 * 60 * 1000); // 30 minutes
      }

      await user.save();

      return res.status(401).json({ error: 'Invalid credentials' });
    }

    // Reset failed attempts on successful login
    user.failedLoginAttempts = 0;
    user.lockedUntil = null;
    await user.save();

    // Generate tokens
    const accessToken = generateAccessToken(user);
    const refreshToken = generateRefreshToken(user);

    res.json({
      user: {
        id: user.id,
        email: user.email,
        name: user.name,
        role: user.role
      },
      accessToken,
      refreshToken
    });
  } catch (error) {
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Refresh token
router.post('/refresh', async (req, res) => {
  try {
    const { refreshToken } = req.body;

    if (!refreshToken) {
      return res.status(400).json({ error: 'Missing refresh token' });
    }

    // Verify refresh token
    const payload = verifyRefreshToken(refreshToken);

    // Find user
    const user = await User.findById(payload.userId);

    if (!user || user.tokenVersion !== payload.tokenVersion) {
      return res.status(401).json({ error: 'Invalid refresh token' });
    }

    // Generate new access token
    const accessToken = generateAccessToken(user);

    res.json({ accessToken });
  } catch (error) {
    res.status(401).json({ error: error.message });
  }
});

// Logout (invalidate all tokens)
router.post('/logout', async (req, res) => {
  try {
    const { userId } = req.body;

    // Increment token version to invalidate all existing tokens
    await User.findByIdAndUpdate(userId, {
      $inc: { tokenVersion: 1 }
    });

    res.json({ message: 'Logged out successfully' });
  } catch (error) {
    res.status(500).json({ error: 'Internal server error' });
  }
});

module.exports = router;
```

### Usage Example

```javascript
// app.js
const express = require('express');
const authRoutes = require('./routes/auth');
const authenticate = require('./middleware/authenticate');

const app = express();

app.use(express.json());

// Auth routes (public)
app.use('/api/auth', authRoutes);

// Protected routes
app.get('/api/profile', authenticate, async (req, res) => {
  const user = await User.findById(req.user.userId);
  res.json({
    id: user.id,
    email: user.email,
    name: user.name,
    role: user.role
  });
});

app.listen(3000, () => {
  console.log('Server running on port 3000');
});
```

---

## Multi-Factor Authentication (MFA) Extension

### Additional Dependencies

```bash
npm install speakeasy qrcode
```

### MFA Routes

```javascript
// routes/mfa.js
const express = require('express');
const speakeasy = require('speakeasy');
const QRCode = require('qrcode');
const User = require('../models/User');
const authenticate = require('../middleware/authenticate');

const router = express.Router();

// Enable MFA (generate secret)
router.post('/enable', authenticate, async (req, res) => {
  try {
    const user = await User.findById(req.user.userId);

    // Generate secret
    const secret = speakeasy.generateSecret({
      name: `YourApp (${user.email})`,
      length: 32
    });

    // Store secret (not enabled until verified)
    user.mfaSecret = secret.base32;
    await user.save();

    // Generate QR code
    const qrCode = await QRCode.toDataURL(secret.otpauth_url);

    res.json({
      secret: secret.base32,
      qrCode
    });
  } catch (error) {
    res.status(500).json({ error: 'Failed to enable MFA' });
  }
});

// Verify and activate MFA
router.post('/verify', authenticate, async (req, res) => {
  try {
    const { token } = req.body;
    const user = await User.findById(req.user.userId);

    const verified = speakeasy.totp.verify({
      secret: user.mfaSecret,
      encoding: 'base32',
      token,
      window: 2
    });

    if (!verified) {
      return res.status(400).json({ error: 'Invalid MFA code' });
    }

    // Activate MFA
    user.mfaEnabled = true;
    await user.save();

    res.json({ message: 'MFA enabled successfully' });
  } catch (error) {
    res.status(500).json({ error: 'Failed to verify MFA' });
  }
});

// Disable MFA
router.post('/disable', authenticate, async (req, res) => {
  try {
    const { password } = req.body;
    const user = await User.findById(req.user.userId);

    // Verify password before disabling MFA
    const validPassword = await verifyPassword(password, user.passwordHash);

    if (!validPassword) {
      return res.status(401).json({ error: 'Invalid password' });
    }

    user.mfaEnabled = false;
    user.mfaSecret = null;
    await user.save();

    res.json({ message: 'MFA disabled successfully' });
  } catch (error) {
    res.status(500).json({ error: 'Failed to disable MFA' });
  }
});

module.exports = router;
```

### Updated Login with MFA

```javascript
// Add to routes/auth.js login endpoint

// After password verification:
if (validPassword) {
  // Check if MFA is enabled
  if (user.mfaEnabled) {
    const { mfaToken } = req.body;

    if (!mfaToken) {
      return res.status(400).json({ error: 'MFA token required' });
    }

    const verified = speakeasy.totp.verify({
      secret: user.mfaSecret,
      encoding: 'base32',
      token: mfaToken,
      window: 2
    });

    if (!verified) {
      return res.status(401).json({ error: 'Invalid MFA code' });
    }
  }

  // Continue with token generation...
}
```

---

## Testing

```javascript
// tests/auth.test.js
const request = require('supertest');
const app = require('../app');
const User = require('../models/User');

describe('Authentication', () => {
  beforeEach(async () => {
    await User.deleteMany({});
  });

  test('Register user', async () => {
    const res = await request(app)
      .post('/api/auth/register')
      .send({
        email: 'test@example.com',
        password: 'SecurePass123!',
        name: 'Test User'
      });

    expect(res.status).toBe(201);
    expect(res.body).toHaveProperty('accessToken');
    expect(res.body.user.email).toBe('test@example.com');
  });

  test('Login with valid credentials', async () => {
    // Create user
    await request(app)
      .post('/api/auth/register')
      .send({
        email: 'test@example.com',
        password: 'SecurePass123!',
        name: 'Test User'
      });

    // Login
    const res = await request(app)
      .post('/api/auth/login')
      .send({
        email: 'test@example.com',
        password: 'SecurePass123!'
      });

    expect(res.status).toBe(200);
    expect(res.body).toHaveProperty('accessToken');
  });

  test('Reject weak password', async () => {
    const res = await request(app)
      .post('/api/auth/register')
      .send({
        email: 'test@example.com',
        password: 'weak',
        name: 'Test User'
      });

    expect(res.status).toBe(400);
  });

  test('Lock account after failed attempts', async () => {
    // Create user
    await request(app)
      .post('/api/auth/register')
      .send({
        email: 'test@example.com',
        password: 'SecurePass123!',
        name: 'Test User'
      });

    // 5 failed login attempts
    for (let i = 0; i < 5; i++) {
      await request(app)
        .post('/api/auth/login')
        .send({
          email: 'test@example.com',
          password: 'WrongPassword'
        });
    }

    // 6th attempt should be locked
    const res = await request(app)
      .post('/api/auth/login')
      .send({
        email: 'test@example.com',
        password: 'SecurePass123!'
      });

    expect(res.status).toBe(429);
    expect(res.body.error).toContain('Account locked');
  });
});
```

---

## Security Checklist

- [ ] Password minimum 12 characters with complexity requirements
- [ ] bcrypt with cost factor 12+
- [ ] JWT with short expiration (15 minutes)
- [ ] Refresh tokens with longer expiration (7 days)
- [ ] Rate limiting on auth endpoints
- [ ] Account lockout after 5 failed attempts
- [ ] Constant-time password comparison
- [ ] Token version for global logout
- [ ] MFA support
- [ ] Security logging for all auth events
- [ ] HTTPS only in production
- [ ] Secure cookie settings (httpOnly, secure, sameSite)
