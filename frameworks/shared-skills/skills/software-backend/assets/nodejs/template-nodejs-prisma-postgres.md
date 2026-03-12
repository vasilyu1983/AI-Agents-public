# Backend Engineering - Node.js + Prisma + PostgreSQL Template

*Purpose: A comprehensive template for building production-grade REST APIs with Node.js, Prisma ORM, and PostgreSQL.*

---

# When to Use

Use this template when building:

- REST APIs with Express/Fastify/NestJS
- CRUD applications with PostgreSQL
- Authentication systems
- Multi-tenant SaaS backends
- Microservices
- Admin dashboards and internal tools

---

# TEMPLATE STARTS HERE

# 1. Project Overview

**Project Name:**
[Name]

**Description:**
[Brief description of the API purpose]

**Tech Stack:**
- [ ] Node.js (v18+ recommended)
- [ ] TypeScript
- [ ] Express.js / Fastify / NestJS
- [ ] Prisma ORM
- [ ] PostgreSQL (v14+)
- [ ] Redis (caching/sessions)
- [ ] BullMQ (background jobs)

**Team:**
- Owner: [Name]
- Backend Lead: [Name]
- Database Admin: [Name]

**Timeline:**
- Start: [YYYY-MM-DD]
- MVP: [YYYY-MM-DD]
- Launch: [YYYY-MM-DD]

---

# 2. Project Structure

```
project-root/
|-- src/
|   |-- api/
|   |   |-- routes/
|   |   |   |-- index.ts           # Route aggregator
|   |   |   |-- auth.routes.ts
|   |   |   |-- users.routes.ts
|   |   |   `-- posts.routes.ts
|   |   |-- controllers/
|   |   |   |-- auth.controller.ts
|   |   |   |-- users.controller.ts
|   |   |   `-- posts.controller.ts
|   |   |-- middlewares/
|   |   |   |-- auth.middleware.ts
|   |   |   |-- error.middleware.ts
|   |   |   |-- validation.middleware.ts
|   |   |   `-- rateLimit.middleware.ts
|   |   `-- validators/
|   |       |-- auth.schema.ts
|   |       |-- users.schema.ts
|   |       `-- posts.schema.ts
|   |-- services/
|   |   |-- auth.service.ts
|   |   |-- users.service.ts
|   |   |-- posts.service.ts
|   |   |-- email.service.ts
|   |   `-- cache.service.ts
|   |-- repositories/
|   |   |-- users.repository.ts
|   |   `-- posts.repository.ts
|   |-- config/
|   |   |-- env.ts                 # Environment variables
|   |   |-- database.ts            # Prisma client
|   |   |-- redis.ts               # Redis client
|   |   `-- logger.ts              # Winston/Pino config
|   |-- utils/
|   |   |-- errors.ts              # Custom error classes
|   |   |-- jwt.ts                 # Token utilities
|   |   |-- password.ts            # Bcrypt utilities
|   |   `-- pagination.ts          # Pagination helpers
|   |-- types/
|   |   |-- express.d.ts           # Express type extensions
|   |   `-- index.ts               # Shared types
|   |-- jobs/                      # Background job workers
|   |   `-- email.worker.ts
|   |-- app.ts                     # Express app setup
|   `-- server.ts                  # Server entry point
|-- prisma/
|   |-- schema.prisma              # Database schema
|   |-- migrations/                # Migration files
|   `-- seed.ts                    # Database seeding
|-- tests/
|   |-- unit/
|   |-- integration/
|   `-- e2e/
|-- .env.example
|-- .env
|-- .gitignore
|-- docker-compose.yml
|-- Dockerfile
|-- package.json
|-- tsconfig.json
`-- README.md
```

---

# 3. Environment Configuration

## 3.1 `.env.example`

```env
# Node
NODE_ENV=development
PORT=3000

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/dbname

# Redis
REDIS_URL=redis://localhost:6379

# JWT
JWT_SECRET=your-secret-key-change-in-production
JWT_EXPIRES_IN=7d

# Email (optional)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-password

# External APIs (if needed)
API_KEY=your-api-key

# Monitoring (optional)
SENTRY_DSN=your-sentry-dsn
```

## 3.2 Environment Validation

```typescript
// src/config/env.ts
import { z } from 'zod';

const envSchema = z.object({
  NODE_ENV: z.enum(['development', 'production', 'test']),
  PORT: z.string().transform(Number),
  DATABASE_URL: z.string().url(),
  REDIS_URL: z.string().url(),
  JWT_SECRET: z.string().min(32),
  JWT_EXPIRES_IN: z.string(),
});

export const env = envSchema.parse(process.env);
```

**Checklist:**
- [ ] All required variables defined
- [ ] Validation at startup
- [ ] Separate `.env` per environment (dev/staging/prod)
- [ ] Never commit `.env` to git
- [ ] Use secrets manager in production (AWS Secrets Manager, Vault)

---

# 4. Database Setup (Prisma + PostgreSQL)

## 4.1 Prisma Schema

```prisma
// prisma/schema.prisma
generator client {
  provider = "prisma-client-js"
}

datasource db {
  provider = "postgresql"
  url      = env("DATABASE_URL")
}

model User {
  id        String   @id @default(cuid())
  email     String   @unique
  password  String
  name      String
  role      Role     @default(USER)
  isActive  Boolean  @default(true)
  createdAt DateTime @default(now())
  updatedAt DateTime @updatedAt

  posts     Post[]
  sessions  Session[]

  @@index([email])
  @@index([createdAt])
  @@map("users")
}

model Post {
  id        String   @id @default(cuid())
  title     String
  content   String
  published Boolean  @default(false)
  authorId  String
  author    User     @relation(fields: [authorId], references: [id], onDelete: Cascade)
  createdAt DateTime @default(now())
  updatedAt DateTime @updatedAt

  @@index([authorId])
  @@index([published, createdAt])
  @@map("posts")
}

model Session {
  id        String   @id @default(cuid())
  token     String   @unique
  userId    String
  user      User     @relation(fields: [userId], references: [id], onDelete: Cascade)
  expiresAt DateTime
  createdAt DateTime @default(now())

  @@index([token])
  @@index([userId])
  @@map("sessions")
}

enum Role {
  USER
  ADMIN
}
```

## 4.2 Prisma Client Setup

```typescript
// src/config/database.ts
import { PrismaClient } from '@prisma/client';
import { env } from './env';

const prisma = new PrismaClient({
  log: env.NODE_ENV === 'development' ? ['query', 'error', 'warn'] : ['error'],
});

export { prisma };
```

## 4.3 Migration Workflow

```bash
# Development
npx prisma migrate dev --name init

# Production
npx prisma migrate deploy

# Generate Prisma Client
npx prisma generate

# Open Prisma Studio
npx prisma studio
```

**Checklist:**
- [ ] Schema follows naming conventions
- [ ] Indexes on foreign keys and query columns
- [ ] Cascade deletes configured
- [ ] Timestamps (createdAt, updatedAt) on all models
- [ ] Connection pooling configured for production

---

# 5. Application Setup (Express)

## 5.1 Express App Configuration

```typescript
// src/app.ts
import express from 'express';
import helmet from 'helmet';
import cors from 'cors';
import compression from 'compression';
import { rateLimit } from 'express-rate-limit';
import routes from './api/routes';
import { errorHandler } from './api/middlewares/error.middleware';
import { requestLogger } from './api/middlewares/logger.middleware';

const app = express();

// Security
app.use(helmet());
app.use(cors({
  origin: process.env.ALLOWED_ORIGINS?.split(',') || '*',
  credentials: true,
}));

// Parsing
app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true }));

// Compression
app.use(compression());

// Rate limiting
const limiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 100, // Limit each IP to 100 requests per windowMs
});
app.use('/api/', limiter);

// Logging
app.use(requestLogger);

// Health check
app.get('/health', (req, res) => {
  res.json({ status: 'ok', timestamp: new Date().toISOString() });
});

// Routes
app.use('/api/v1', routes);

// Error handling
app.use(errorHandler);

export { app };
```

## 5.2 Server Entry Point

```typescript
// src/server.ts
import { app } from './app';
import { env } from './config/env';
import { logger } from './config/logger';
import { prisma } from './config/database';

const PORT = env.PORT || 3000;

const server = app.listen(PORT, () => {
  logger.info(`Server running on port ${PORT} in ${env.NODE_ENV} mode`);
});

// Graceful shutdown
const shutdown = async () => {
  logger.info('Shutting down gracefully...');

  server.close(async () => {
    await prisma.$disconnect();
    process.exit(0);
  });

  // Force shutdown after 10 seconds
  setTimeout(() => {
    logger.error('Forced shutdown');
    process.exit(1);
  }, 10000);
};

process.on('SIGTERM', shutdown);
process.on('SIGINT', shutdown);
```

**Checklist:**
- [ ] Security headers (Helmet)
- [ ] CORS configured
- [ ] Rate limiting enabled
- [ ] Request logging
- [ ] Health check endpoint
- [ ] Graceful shutdown

---

# 6. Authentication Implementation

## 6.1 Auth Service

```typescript
// src/services/auth.service.ts
import bcrypt from 'bcrypt';
import jwt from 'jsonwebtoken';
import { prisma } from '../config/database';
import { env } from '../config/env';
import { AppError } from '../utils/errors';

class AuthService {
  async register(email: string, password: string, name: string) {
    const existingUser = await prisma.user.findUnique({ where: { email } });
    if (existingUser) {
      throw new AppError(409, 'Email already registered');
    }

    const hashedPassword = await bcrypt.hash(password, 12);

    const user = await prisma.user.create({
      data: { email, password: hashedPassword, name },
      select: { id: true, email: true, name: true, role: true },
    });

    const token = this.generateToken(user.id, user.role);

    return { user, token };
  }

  async login(email: string, password: string) {
    const user = await prisma.user.findUnique({ where: { email } });
    if (!user) {
      throw new AppError(401, 'Invalid credentials');
    }

    const isValidPassword = await bcrypt.compare(password, user.password);
    if (!isValidPassword) {
      throw new AppError(401, 'Invalid credentials');
    }

    if (!user.isActive) {
      throw new AppError(403, 'Account is deactivated');
    }

    const token = this.generateToken(user.id, user.role);

    return {
      user: {
        id: user.id,
        email: user.email,
        name: user.name,
        role: user.role,
      },
      token,
    };
  }

  private generateToken(userId: string, role: string) {
    return jwt.sign(
      { userId, role },
      env.JWT_SECRET,
      { expiresIn: env.JWT_EXPIRES_IN }
    );
  }
}

export const authService = new AuthService();
```

## 6.2 Auth Middleware

```typescript
// src/api/middlewares/auth.middleware.ts
import jwt from 'jsonwebtoken';
import { Request, Response, NextFunction } from 'express';
import { prisma } from '../../config/database';
import { env } from '../../config/env';
import { AppError } from '../../utils/errors';

export const authenticate = async (
  req: Request,
  res: Response,
  next: NextFunction
) => {
  try {
    const token = req.headers.authorization?.replace('Bearer ', '');

    if (!token) {
      throw new AppError(401, 'Authentication required');
    }

    const payload = jwt.verify(token, env.JWT_SECRET) as {
      userId: string;
      role: string;
    };

    const user = await prisma.user.findUnique({
      where: { id: payload.userId },
      select: { id: true, email: true, name: true, role: true, isActive: true },
    });

    if (!user || !user.isActive) {
      throw new AppError(401, 'Invalid or expired token');
    }

    req.user = user;
    next();
  } catch (error) {
    next(new AppError(401, 'Invalid or expired token'));
  }
};

export const authorize = (...roles: string[]) => {
  return (req: Request, res: Response, next: NextFunction) => {
    if (!req.user || !roles.includes(req.user.role)) {
      return next(new AppError(403, 'Insufficient permissions'));
    }
    next();
  };
};
```

**Checklist:**
- [ ] Password hashing with bcrypt (12 rounds minimum)
- [ ] JWT token with expiration
- [ ] Refresh token mechanism (if needed)
- [ ] Role-based authorization
- [ ] Secure token storage on client (httpOnly cookies recommended)

---

# 7. API Routes & Controllers

## 7.1 User Routes

```typescript
// src/api/routes/users.routes.ts
import { Router } from 'express';
import { usersController } from '../controllers/users.controller';
import { authenticate, authorize } from '../middlewares/auth.middleware';
import { validate } from '../middlewares/validation.middleware';
import { updateUserSchema } from '../validators/users.schema';

const router = Router();

router.get('/', authenticate, authorize('ADMIN'), usersController.getAll);
router.get('/:id', authenticate, usersController.getById);
router.patch(
  '/:id',
  authenticate,
  validate(updateUserSchema),
  usersController.update
);
router.delete('/:id', authenticate, authorize('ADMIN'), usersController.delete);

export default router;
```

## 7.2 Users Controller

```typescript
// src/api/controllers/users.controller.ts
import { Request, Response, NextFunction } from 'express';
import { usersService } from '../../services/users.service';

class UsersController {
  async getAll(req: Request, res: Response, next: NextFunction) {
    try {
      const { cursor, limit } = req.query;
      const result = await usersService.listUsers({
        cursor: cursor as string,
        limit: limit ? parseInt(limit as string) : undefined,
      });
      res.json(result);
    } catch (error) {
      next(error);
    }
  }

  async getById(req: Request, res: Response, next: NextFunction) {
    try {
      const user = await usersService.getUserById(req.params.id);
      res.json(user);
    } catch (error) {
      next(error);
    }
  }

  async update(req: Request, res: Response, next: NextFunction) {
    try {
      const user = await usersService.updateUser(req.params.id, req.body);
      res.json(user);
    } catch (error) {
      next(error);
    }
  }

  async delete(req: Request, res: Response, next: NextFunction) {
    try {
      await usersService.deleteUser(req.params.id);
      res.status(204).send();
    } catch (error) {
      next(error);
    }
  }
}

export const usersController = new UsersController();
```

**Checklist:**
- [ ] Proper HTTP methods (GET, POST, PUT, PATCH, DELETE)
- [ ] Authentication on protected routes
- [ ] Authorization checks
- [ ] Input validation
- [ ] Error handling via next()

---

# 8. Repository Pattern

```typescript
// src/repositories/users.repository.ts
import { prisma } from '../config/database';
import { Prisma } from '@prisma/client';

interface PaginationParams {
  cursor?: string;
  limit?: number;
}

class UsersRepository {
  async findMany({ cursor, limit = 20 }: PaginationParams) {
    const users = await prisma.user.findMany({
      take: limit + 1,
      ...(cursor && { skip: 1, cursor: { id: cursor } }),
      orderBy: { createdAt: 'desc' },
      select: {
        id: true,
        email: true,
        name: true,
        role: true,
        createdAt: true,
      },
    });

    const hasMore = users.length > limit;
    const items = hasMore ? users.slice(0, -1) : users;

    return {
      items,
      nextCursor: hasMore ? items[items.length - 1].id : null,
      hasMore,
    };
  }

  async findById(id: string) {
    return prisma.user.findUnique({
      where: { id },
      select: {
        id: true,
        email: true,
        name: true,
        role: true,
        createdAt: true,
        updatedAt: true,
      },
    });
  }

  async findByEmail(email: string) {
    return prisma.user.findUnique({ where: { email } });
  }

  async create(data: Prisma.UserCreateInput) {
    return prisma.user.create({ data });
  }

  async update(id: string, data: Prisma.UserUpdateInput) {
    return prisma.user.update({ where: { id }, data });
  }

  async delete(id: string) {
    await prisma.user.delete({ where: { id } });
  }
}

export const usersRepository = new UsersRepository();
```

**Checklist:**
- [ ] Repository layer isolates data access
- [ ] Select only needed fields
- [ ] Support pagination
- [ ] Transaction support where needed

---

# 9. Testing

## 9.1 Unit Test Example

```typescript
// tests/unit/services/auth.service.test.ts
import { authService } from '../../../src/services/auth.service';
import { prisma } from '../../../src/config/database';
import bcrypt from 'bcrypt';

jest.mock('../../../src/config/database', () => ({
  prisma: {
    user: {
      findUnique: jest.fn(),
      create: jest.fn(),
    },
  },
}));

describe('AuthService', () => {
  describe('register', () => {
    it('should create user with hashed password', async () => {
      (prisma.user.findUnique as jest.Mock).mockResolvedValue(null);
      (prisma.user.create as jest.Mock).mockResolvedValue({
        id: '1',
        email: 'test@example.com',
        name: 'Test User',
        role: 'USER',
      });

      const result = await authService.register(
        'test@example.com',
        'password123',
        'Test User'
      );

      expect(result.user.email).toBe('test@example.com');
      expect(result.token).toBeDefined();
    });

    it('should throw error if email exists', async () => {
      (prisma.user.findUnique as jest.Mock).mockResolvedValue({
        id: '1',
        email: 'test@example.com',
      });

      await expect(
        authService.register('test@example.com', 'password123', 'Test User')
      ).rejects.toThrow('Email already registered');
    });
  });
});
```

## 9.2 Integration Test Example

```typescript
// tests/integration/api/auth.test.ts
import request from 'supertest';
import { app } from '../../../src/app';
import { prisma } from '../../../src/config/database';

describe('POST /api/v1/auth/register', () => {
  beforeAll(async () => {
    // Setup test database
  });

  afterAll(async () => {
    await prisma.$disconnect();
  });

  it('should register new user', async () => {
    const response = await request(app)
      .post('/api/v1/auth/register')
      .send({
        email: 'newuser@example.com',
        password: 'password123',
        name: 'New User',
      })
      .expect(201);

    expect(response.body.user.email).toBe('newuser@example.com');
    expect(response.body.token).toBeDefined();
  });

  it('should return 409 if email exists', async () => {
    // First registration
    await request(app).post('/api/v1/auth/register').send({
      email: 'duplicate@example.com',
      password: 'password123',
      name: 'User',
    });

    // Duplicate registration
    const response = await request(app)
      .post('/api/v1/auth/register')
      .send({
        email: 'duplicate@example.com',
        password: 'password123',
        name: 'User 2',
      })
      .expect(409);

    expect(response.body.message).toBe('Email already registered');
  });
});
```

**Checklist:**
- [ ] Unit tests for services and utilities
- [ ] Integration tests for API endpoints
- [ ] Test database separate from development
- [ ] Mock external dependencies
- [ ] Test both success and error cases
- [ ] 80%+ code coverage

---

# 10. Docker Setup

## 10.1 Dockerfile

```dockerfile
FROM node:18-alpine AS builder

WORKDIR /app

COPY package*.json ./
COPY prisma ./prisma/

RUN npm ci

COPY . .

RUN npx prisma generate
RUN npm run build

FROM node:18-alpine

WORKDIR /app

COPY --from=builder /app/dist ./dist
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package*.json ./
COPY --from=builder /app/prisma ./prisma

EXPOSE 3000

CMD ["npm", "start"]
```

## 10.2 docker-compose.yml

```yaml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=production
      - DATABASE_URL=postgresql://postgres:password@postgres:5432/mydb
      - REDIS_URL=redis://redis:6379
      - JWT_SECRET=your-secret-key
    depends_on:
      - postgres
      - redis

  postgres:
    image: postgres:15-alpine
    environment:
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=mydb
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

volumes:
  postgres_data:
```

**Checklist:**
- [ ] Multi-stage build for smaller image
- [ ] Non-root user
- [ ] Health checks
- [ ] Volume mounts for persistence
- [ ] Environment variables

---

# 11. Production Checklist

## 11.1 Security
- [ ] HTTPS enabled
- [ ] Security headers (Helmet)
- [ ] Rate limiting
- [ ] CORS configured
- [ ] Input validation
- [ ] SQL injection prevention (Prisma handles this)
- [ ] XSS prevention
- [ ] CSRF protection (if using cookies)
- [ ] Secrets in environment variables/secrets manager
- [ ] Dependency vulnerability scanning

## 11.2 Performance
- [ ] Database indexes on query columns
- [ ] Connection pooling configured
- [ ] Caching layer (Redis)
- [ ] Response compression
- [ ] Pagination for list endpoints
- [ ] Query optimization (select only needed fields)

## 11.3 Monitoring
- [ ] Structured logging (Pino/Winston)
- [ ] Error tracking (Sentry)
- [ ] APM (New Relic/Datadog)
- [ ] Health check endpoint
- [ ] Database query monitoring
- [ ] Cache hit ratio monitoring

## 11.4 Deployment
- [ ] CI/CD pipeline configured
- [ ] Automated tests in pipeline
- [ ] Database migrations automated
- [ ] Environment variables managed
- [ ] Graceful shutdown handling
- [ ] Zero-downtime deployments
- [ ] Rollback plan

---

# 12. API Documentation

## 12.1 OpenAPI/Swagger Setup

```typescript
// src/config/swagger.ts
import swaggerJSDoc from 'swagger-jsdoc';

const options = {
  definition: {
    openapi: '3.0.0',
    info: {
      title: 'My API',
      version: '1.0.0',
      description: 'API documentation',
    },
    servers: [
      {
        url: 'http://localhost:3000/api/v1',
        description: 'Development server',
      },
    ],
    components: {
      securitySchemes: {
        bearerAuth: {
          type: 'http',
          scheme: 'bearer',
          bearerFormat: 'JWT',
        },
      },
    },
  },
  apis: ['./src/api/routes/*.ts'],
};

export const swaggerSpec = swaggerJSDoc(options);
```

**Checklist:**
- [ ] API documentation generated
- [ ] All endpoints documented
- [ ] Request/response schemas defined
- [ ] Authentication documented

---

# END

This template provides a production-ready foundation for Node.js + Prisma + PostgreSQL backends. Customize based on specific project requirements.
