# Secure API Implementation Template

Copy-paste ready implementation for building secure REST APIs with comprehensive security controls.

---

## Complete Secure API Setup

### Dependencies

```bash
npm install express helmet cors express-rate-limit express-validator winston morgan
```

### Environment Configuration

```bash
# .env
NODE_ENV=production
PORT=3000
API_VERSION=v1

# Security
JWT_SECRET=your-secret-key-min-32-characters
ALLOWED_ORIGINS=https://app.example.com,https://admin.example.com
RATE_LIMIT_WINDOW_MS=900000
RATE_LIMIT_MAX_REQUESTS=100

# Logging
LOG_LEVEL=info
```

### Security Headers

```javascript
// config/security.js
const helmet = require('helmet');

const securityHeaders = helmet({
  // Content Security Policy
  contentSecurityPolicy: {
    directives: {
      defaultSrc: ["'self'"],
      styleSrc: ["'self'", "'unsafe-inline'"],
      scriptSrc: ["'self'"],
      imgSrc: ["'self'", 'data:', 'https:'],
      fontSrc: ["'self'", 'data:'],
      connectSrc: ["'self'"],
      frameSrc: ["'none'"],
      objectSrc: ["'none'"],
      upgradeInsecureRequests: []
    }
  },

  // HTTP Strict Transport Security
  hsts: {
    maxAge: 31536000, // 1 year
    includeSubDomains: true,
    preload: true
  },

  // X-Frame-Options
  frameguard: {
    action: 'deny'
  },

  // X-Content-Type-Options
  noSniff: true,

  // X-XSS-Protection
  xssFilter: true,

  // Referrer-Policy
  referrerPolicy: {
    policy: 'strict-origin-when-cross-origin'
  },

  // X-Permitted-Cross-Domain-Policies
  permittedCrossDomainPolicies: {
    permittedPolicies: 'none'
  },

  // Hide X-Powered-By
  hidePoweredBy: true
});

module.exports = securityHeaders;
```

### CORS Configuration

```javascript
// config/cors.js
const cors = require('cors');

const allowedOrigins = process.env.ALLOWED_ORIGINS
  ? process.env.ALLOWED_ORIGINS.split(',')
  : [];

const corsOptions = {
  origin: (origin, callback) => {
    // Allow requests with no origin (mobile apps, Postman, etc.)
    if (!origin) {
      return callback(null, true);
    }

    if (allowedOrigins.includes(origin)) {
      callback(null, true);
    } else {
      callback(new Error('Not allowed by CORS'));
    }
  },
  credentials: true,
  optionsSuccessStatus: 200,
  methods: ['GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'OPTIONS'],
  allowedHeaders: [
    'Content-Type',
    'Authorization',
    'X-Requested-With',
    'X-CSRF-Token'
  ],
  exposedHeaders: ['X-Total-Count', 'X-Page-Count'],
  maxAge: 86400 // 24 hours
};

module.exports = cors(corsOptions);
```

### Rate Limiting

```javascript
// config/rateLimiting.js
const rateLimit = require('express-rate-limit');

// General API rate limiter
const apiLimiter = rateLimit({
  windowMs: parseInt(process.env.RATE_LIMIT_WINDOW_MS) || 15 * 60 * 1000,
  max: parseInt(process.env.RATE_LIMIT_MAX_REQUESTS) || 100,
  message: {
    error: 'Too many requests from this IP, please try again later'
  },
  standardHeaders: true,
  legacyHeaders: false,
  // Skip successful requests from the count
  skipSuccessfulRequests: false,
  // Key generator (use IP + user ID if authenticated)
  keyGenerator: (req) => {
    return req.user ? `${req.ip}-${req.user.userId}` : req.ip;
  }
});

// Stricter rate limiter for auth endpoints
const authLimiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 5,
  skipSuccessfulRequests: true,
  message: {
    error: 'Too many authentication attempts, please try again later'
  }
});

// Very strict rate limiter for password reset
const passwordResetLimiter = rateLimit({
  windowMs: 60 * 60 * 1000, // 1 hour
  max: 3,
  message: {
    error: 'Too many password reset requests, please try again later'
  }
});

// Strict limiter for sensitive operations
const sensitiveLimiter = rateLimit({
  windowMs: 15 * 60 * 1000,
  max: 10,
  message: {
    error: 'Too many requests for this operation'
  }
});

module.exports = {
  apiLimiter,
  authLimiter,
  passwordResetLimiter,
  sensitiveLimiter
};
```

### Input Validation

```javascript
// middleware/validation.js
const { body, param, query, validationResult } = require('express-validator');

// Validation error handler
const handleValidationErrors = (req, res, next) => {
  const errors = validationResult(req);

  if (!errors.isEmpty()) {
    return res.status(400).json({
      error: 'Validation failed',
      details: errors.array().map(err => ({
        field: err.param,
        message: err.msg,
        value: err.value
      }))
    });
  }

  next();
};

// Common validators
const validators = {
  email: body('email')
    .trim()
    .isEmail().withMessage('Invalid email format')
    .normalizeEmail()
    .isLength({ max: 254 }).withMessage('Email too long'),

  password: body('password')
    .isLength({ min: 12 }).withMessage('Password must be at least 12 characters')
    .matches(/[A-Z]/).withMessage('Password must contain uppercase letter')
    .matches(/[a-z]/).withMessage('Password must contain lowercase letter')
    .matches(/\d/).withMessage('Password must contain number')
    .matches(/[!@#$%^&*(),.?":{}|<>]/).withMessage('Password must contain special character'),

  id: param('id')
    .isMongoId().withMessage('Invalid ID format'),

  uuid: param('id')
    .isUUID().withMessage('Invalid UUID format'),

  pagination: [
    query('page')
      .optional()
      .isInt({ min: 1 }).withMessage('Page must be positive integer')
      .toInt(),
    query('limit')
      .optional()
      .isInt({ min: 1, max: 100 }).withMessage('Limit must be between 1 and 100')
      .toInt()
  ],

  string: (field, minLength = 1, maxLength = 255) =>
    body(field)
      .trim()
      .isLength({ min: minLength, max: maxLength })
      .withMessage(`${field} must be between ${minLength} and ${maxLength} characters`)
      .escape(),

  enum: (field, allowedValues) =>
    body(field)
      .isIn(allowedValues)
      .withMessage(`${field} must be one of: ${allowedValues.join(', ')}`)
};

module.exports = {
  handleValidationErrors,
  validators
};
```

### Logging

```javascript
// config/logger.js
const winston = require('winston');
const morgan = require('morgan');

// Winston logger configuration
const logger = winston.createLogger({
  level: process.env.LOG_LEVEL || 'info',
  format: winston.format.combine(
    winston.format.timestamp(),
    winston.format.errors({ stack: true }),
    winston.format.json()
  ),
  defaultMeta: { service: 'api' },
  transports: [
    // Write all logs to console
    new winston.transports.Console({
      format: winston.format.combine(
        winston.format.colorize(),
        winston.format.simple()
      )
    }),
    // Write all logs to combined.log
    new winston.transports.File({ filename: 'logs/combined.log' }),
    // Write error logs to error.log
    new winston.transports.File({
      filename: 'logs/error.log',
      level: 'error'
    }),
    // Write security events to security.log
    new winston.transports.File({
      filename: 'logs/security.log',
      level: 'warn'
    })
  ]
});

// Security logger (separate from general logging)
const securityLogger = winston.createLogger({
  level: 'info',
  format: winston.format.combine(
    winston.format.timestamp(),
    winston.format.json()
  ),
  defaultMeta: { type: 'security' },
  transports: [
    new winston.transports.File({ filename: 'logs/security.log' })
  ]
});

// Morgan HTTP request logger
const httpLogger = morgan('combined', {
  stream: {
    write: (message) => logger.http(message.trim())
  }
});

// Sanitize logs (remove sensitive data)
const sanitizeForLogging = (data) => {
  const sensitiveFields = [
    'password',
    'passwordHash',
    'token',
    'refreshToken',
    'accessToken',
    'apiKey',
    'ssn',
    'creditCard',
    'cvv'
  ];

  const sanitized = { ...data };

  for (const field of sensitiveFields) {
    if (sanitized[field]) {
      sanitized[field] = '[REDACTED]';
    }
  }

  return sanitized;
};

module.exports = {
  logger,
  securityLogger,
  httpLogger,
  sanitizeForLogging
};
```

### Error Handling

```javascript
// middleware/errorHandler.js
const { logger } = require('../config/logger');

// Custom error classes
class AppError extends Error {
  constructor(message, statusCode) {
    super(message);
    this.statusCode = statusCode;
    this.isOperational = true;
    Error.captureStackTrace(this, this.constructor);
  }
}

class ValidationError extends AppError {
  constructor(message) {
    super(message, 400);
  }
}

class AuthenticationError extends AppError {
  constructor(message) {
    super(message, 401);
  }
}

class AuthorizationError extends AppError {
  constructor(message) {
    super(message, 403);
  }
}

class NotFoundError extends AppError {
  constructor(message) {
    super(message, 404);
  }
}

// Global error handler
const errorHandler = (err, req, res, next) => {
  let { statusCode = 500, message } = err;

  // Log error
  logger.error('Error occurred', {
    error: err.message,
    stack: err.stack,
    url: req.originalUrl,
    method: req.method,
    ip: req.ip,
    userId: req.user?.userId
  });

  // Mongoose validation error
  if (err.name === 'ValidationError') {
    statusCode = 400;
    message = Object.values(err.errors).map(e => e.message).join(', ');
  }

  // Mongoose duplicate key error
  if (err.code === 11000) {
    statusCode = 400;
    message = 'Duplicate field value';
  }

  // JWT errors
  if (err.name === 'JsonWebTokenError') {
    statusCode = 401;
    message = 'Invalid token';
  }

  if (err.name === 'TokenExpiredError') {
    statusCode = 401;
    message = 'Token expired';
  }

  // Send error response
  if (process.env.NODE_ENV === 'production') {
    // Production: Generic error message
    res.status(statusCode).json({
      error: err.isOperational ? message : 'Internal server error',
      ...(statusCode === 400 && err.details ? { details: err.details } : {})
    });
  } else {
    // Development: Detailed error
    res.status(statusCode).json({
      error: message,
      stack: err.stack,
      ...(err.details ? { details: err.details } : {})
    });
  }
};

// 404 handler
const notFoundHandler = (req, res) => {
  res.status(404).json({
    error: 'Endpoint not found',
    path: req.originalUrl
  });
};

// Async error wrapper
const asyncHandler = (fn) => {
  return (req, res, next) => {
    Promise.resolve(fn(req, res, next)).catch(next);
  };
};

module.exports = {
  AppError,
  ValidationError,
  AuthenticationError,
  AuthorizationError,
  NotFoundError,
  errorHandler,
  notFoundHandler,
  asyncHandler
};
```

### Main Application

```javascript
// app.js
const express = require('express');
const securityHeaders = require('./config/security');
const corsConfig = require('./config/cors');
const { apiLimiter } = require('./config/rateLimiting');
const { httpLogger } = require('./config/logger');
const { errorHandler, notFoundHandler } = require('./middleware/errorHandler');

const app = express();

// Trust proxy (if behind reverse proxy)
app.set('trust proxy', 1);

// Security middleware (apply first)
app.use(securityHeaders);
app.use(corsConfig);

// Body parsing
app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true, limit: '10mb' }));

// HTTP request logging
app.use(httpLogger);

// Rate limiting
app.use('/api/', apiLimiter);

// Health check (no rate limit, no auth)
app.get('/health', (req, res) => {
  res.json({
    status: 'ok',
    timestamp: new Date().toISOString(),
    uptime: process.uptime()
  });
});

// API versioning
const API_VERSION = process.env.API_VERSION || 'v1';

// Routes
app.use(`/api/${API_VERSION}/auth`, require('./routes/auth'));
app.use(`/api/${API_VERSION}/users`, require('./routes/users'));
app.use(`/api/${API_VERSION}/posts`, require('./routes/posts'));

// 404 handler
app.use(notFoundHandler);

// Global error handler (must be last)
app.use(errorHandler);

module.exports = app;
```

### Secure Route Example

```javascript
// routes/posts.js
const express = require('express');
const authenticate = require('../middleware/authenticate');
const { requirePermission } = require('../middleware/authorize');
const { validators, handleValidationErrors } = require('../middleware/validation');
const { asyncHandler, NotFoundError } = require('../middleware/errorHandler');
const { sensitiveLimiter } = require('../config/rateLimiting');
const { PERMISSIONS } = require('../config/permissions');
const Post = require('../models/Post');

const router = express.Router();

// List posts (public, with pagination)
router.get('/',
  validators.pagination,
  handleValidationErrors,
  asyncHandler(async (req, res) => {
    const { page = 1, limit = 20 } = req.query;
    const skip = (page - 1) * limit;

    const [posts, total] = await Promise.all([
      Post.find({ published: true })
        .skip(skip)
        .limit(limit)
        .sort({ createdAt: -1 }),
      Post.countDocuments({ published: true })
    ]);

    res.json({
      data: posts,
      pagination: {
        page,
        limit,
        total,
        totalPages: Math.ceil(total / limit)
      }
    });
  })
);

// Get single post (public)
router.get('/:id',
  validators.id,
  handleValidationErrors,
  asyncHandler(async (req, res) => {
    const post = await Post.findById(req.params.id);

    if (!post || !post.published) {
      throw new NotFoundError('Post not found');
    }

    res.json(post);
  })
);

// Create post (authenticated, requires permission)
router.post('/',
  authenticate,
  requirePermission(PERMISSIONS.POSTS_WRITE),
  [
    validators.string('title', 1, 200),
    validators.string('content', 1, 10000),
    validators.enum('status', ['draft', 'published'])
  ],
  handleValidationErrors,
  asyncHandler(async (req, res) => {
    const post = await Post.create({
      ...req.body,
      authorId: req.user.userId
    });

    res.status(201).json(post);
  })
);

// Update post (authenticated, requires ownership or permission)
router.put('/:id',
  authenticate,
  validators.id,
  [
    validators.string('title', 1, 200).optional(),
    validators.string('content', 1, 10000).optional(),
    validators.enum('status', ['draft', 'published']).optional()
  ],
  handleValidationErrors,
  asyncHandler(async (req, res) => {
    const post = await Post.findById(req.params.id);

    if (!post) {
      throw new NotFoundError('Post not found');
    }

    // Check ownership or permission
    if (post.authorId !== req.user.userId && req.user.role !== 'moderator') {
      throw new AuthorizationError('Not authorized to update this post');
    }

    Object.assign(post, req.body);
    await post.save();

    res.json(post);
  })
);

// Delete post (authenticated, requires permission, rate limited)
router.delete('/:id',
  sensitiveLimiter,
  authenticate,
  requirePermission(PERMISSIONS.POSTS_DELETE),
  validators.id,
  handleValidationErrors,
  asyncHandler(async (req, res) => {
    const post = await Post.findById(req.params.id);

    if (!post) {
      throw new NotFoundError('Post not found');
    }

    await post.remove();

    res.json({ message: 'Post deleted successfully' });
  })
);

module.exports = router;
```

### Server Entry Point

```javascript
// server.js
require('dotenv').config();
const app = require('./app');
const { logger } = require('./config/logger');
const mongoose = require('mongoose');

const PORT = process.env.PORT || 3000;

// Database connection
mongoose.connect(process.env.MONGODB_URI, {
  useNewUrlParser: true,
  useUnifiedTopology: true
})
  .then(() => {
    logger.info('Connected to MongoDB');
  })
  .catch((error) => {
    logger.error('MongoDB connection error:', error);
    process.exit(1);
  });

// Start server
const server = app.listen(PORT, () => {
  logger.info(`Server running on port ${PORT} in ${process.env.NODE_ENV} mode`);
});

// Graceful shutdown
const gracefulShutdown = () => {
  logger.info('Received shutdown signal, closing server gracefully');

  server.close(() => {
    logger.info('Server closed');

    mongoose.connection.close(false, () => {
      logger.info('MongoDB connection closed');
      process.exit(0);
    });
  });

  // Force shutdown after 10 seconds
  setTimeout(() => {
    logger.error('Forced shutdown after timeout');
    process.exit(1);
  }, 10000);
};

process.on('SIGTERM', gracefulShutdown);
process.on('SIGINT', gracefulShutdown);

// Handle unhandled promise rejections
process.on('unhandledRejection', (reason, promise) => {
  logger.error('Unhandled Rejection:', { reason, promise });
  gracefulShutdown();
});

// Handle uncaught exceptions
process.on('uncaughtException', (error) => {
  logger.error('Uncaught Exception:', error);
  gracefulShutdown();
});
```

---

## API Documentation Template

```javascript
/**
 * @api {get} /api/v1/posts List posts
 * @apiName ListPosts
 * @apiGroup Posts
 * @apiVersion 1.0.0
 *
 * @apiParam {Number} [page=1] Page number
 * @apiParam {Number} [limit=20] Items per page (max 100)
 *
 * @apiSuccess {Object[]} data Array of posts
 * @apiSuccess {Object} pagination Pagination info
 *
 * @apiSuccessExample Success Response:
 *   HTTP/1.1 200 OK
 *   {
 *     "data": [...],
 *     "pagination": {
 *       "page": 1,
 *       "limit": 20,
 *       "total": 100,
 *       "totalPages": 5
 *     }
 *   }
 *
 * @apiError (400) ValidationError Invalid parameters
 * @apiError (429) RateLimitExceeded Too many requests
 *
 * @apiRateLimit 100 requests per 15 minutes
 */
```

---

## Security Testing

```javascript
// tests/security.test.js
const request = require('supertest');
const app = require('../app');

describe('Security', () => {
  test('Should set security headers', async () => {
    const res = await request(app).get('/health');

    expect(res.headers['x-content-type-options']).toBe('nosniff');
    expect(res.headers['x-frame-options']).toBe('DENY');
    expect(res.headers['x-xss-protection']).toBe('1; mode=block');
    expect(res.headers['strict-transport-security']).toBeTruthy();
  });

  test('Should enforce rate limiting', async () => {
    const endpoint = '/api/v1/auth/login';

    // Make 6 requests (limit is 5)
    for (let i = 0; i < 6; i++) {
      const res = await request(app)
        .post(endpoint)
        .send({ email: 'test@example.com', password: 'password' });

      if (i < 5) {
        expect(res.status).not.toBe(429);
      } else {
        expect(res.status).toBe(429);
      }
    }
  });

  test('Should reject XSS attempts', async () => {
    const res = await request(app)
      .post('/api/v1/posts')
      .send({
        title: '<script>alert("XSS")</script>',
        content: 'Normal content'
      });

    expect(res.body.title).not.toContain('<script>');
  });

  test('Should validate input', async () => {
    const res = await request(app)
      .post('/api/v1/posts')
      .send({
        title: 'a'.repeat(201), // Exceeds max length
        content: 'content'
      });

    expect(res.status).toBe(400);
  });
});
```

---

## Security Checklist

- [ ] HTTPS enforced (TLS 1.3)
- [ ] Security headers configured (Helmet)
- [ ] CORS properly configured
- [ ] Rate limiting on all endpoints
- [ ] Input validation on all inputs
- [ ] Output encoding/sanitization
- [ ] Authentication required where needed
- [ ] Authorization checked on every request
- [ ] Comprehensive error handling
- [ ] Security logging for sensitive operations
- [ ] Secrets in environment variables
- [ ] API versioning implemented
- [ ] Request size limits
- [ ] Graceful error messages (no stack traces in production)
- [ ] 404 handler for unknown endpoints
- [ ] Health check endpoint
- [ ] Graceful shutdown handling
