# Express.js Complete API Template

Production-ready Express.js/TypeScript API with authentication, database, validation, error handling, and OpenAPI docs.

## Project Structure

```
express-api/
├── src/
│   ├── index.ts              # Application entry point
│   ├── app.ts                # Express app configuration
│   ├── config/
│   │   └── index.ts          # Environment configuration
│   ├── db/
│   │   ├── client.ts         # Database connection (Prisma/TypeORM)
│   │   └── migrations/
│   ├── middleware/
│   │   ├── auth.ts           # JWT authentication
│   │   ├── errorHandler.ts  # Global error handling
│   │   ├── validate.ts       # Request validation
│   │   └── rateLimit.ts      # Rate limiting
│   ├── models/               # Database models
│   │   └── User.ts
│   ├── routes/
│   │   ├── index.ts
│   │   ├── auth.routes.ts
│   │   └── users.routes.ts
│   ├── controllers/
│   │   ├── auth.controller.ts
│   │   └── users.controller.ts
│   ├── services/
│   │   └── user.service.ts   # Business logic
│   ├── validators/
│   │   └── user.validator.ts # Zod schemas
│   └── utils/
│       ├── jwt.ts            # Token utilities
│       ├── password.ts       # Hashing utilities
│       └── pagination.ts     # Pagination helpers
├── tests/
│   ├── integration/
│   └── unit/
├── prisma/
│   └── schema.prisma         # Database schema
├── .env.example
├── package.json
├── tsconfig.json
└── openapi.yaml              # API documentation
```

## Centralization Guide

> **Important**: The code patterns in this template should be extracted to `src/utils/`. **Do not duplicate** these utilities across controllers/services.

| Utility | Extract To | Reference |
|---------|------------|-----------|
| Config (Zod validation) | `src/config/index.ts` | [config-validation.md](../../../software-clean-code-standard/utilities/config-validation.md) |
| JWT (`createToken`, `verifyToken`) | `src/utils/jwt.ts` | [auth-utilities.md](../../../software-clean-code-standard/utilities/auth-utilities.md) |
| Password (`hashPassword`, `comparePassword`) | `src/utils/password.ts` | [auth-utilities.md](../../../software-clean-code-standard/utilities/auth-utilities.md) |
| Errors (`ApiError`, `errorHandler`) | `src/utils/errors.ts` | [error-handling.md](../../../software-clean-code-standard/utilities/error-handling.md) |
| Logging (Winston/Pino) | `src/utils/logger.ts` | [logging-utilities.md](../../../software-clean-code-standard/utilities/logging-utilities.md) |

**Pattern**: Create utilities once in `src/utils/`, import everywhere via:

```typescript
import { hashPassword, verifyToken } from '@/utils/auth';
import { ApiError, NotFoundError } from '@/utils/errors';
```

## 1. Dependencies (package.json)

```json
{
  "name": "express-api",
  "version": "1.0.0",
  "scripts": {
    "dev": "tsx watch src/index.ts",
    "build": "tsc",
    "start": "node dist/index.js",
    "test": "jest",
    "migrate": "prisma migrate dev",
    "generate": "prisma generate"
  },
  "dependencies": {
    "express": "^4.18.2",
    "express-async-errors": "^3.1.1",
    "@prisma/client": "^5.8.0",
    "zod": "^3.22.4",
    "bcrypt": "^5.1.1",
    "jsonwebtoken": "^9.0.2",
    "dotenv": "^16.3.1",
    "helmet": "^7.1.0",
    "cors": "^2.8.5",
    "express-rate-limit": "^7.1.5",
    "redis": "^4.6.12",
    "morgan": "^1.10.0",
    "winston": "^3.11.0"
  },
  "devDependencies": {
    "@types/express": "^4.17.21",
    "@types/node": "^20.10.6",
    "@types/bcrypt": "^5.0.2",
    "@types/jsonwebtoken": "^9.0.5",
    "@types/cors": "^2.8.17",
    "@types/morgan": "^1.9.9",
    "typescript": "^5.3.3",
    "tsx": "^4.7.0",
    "jest": "^29.7.0",
    "@types/jest": "^29.5.11",
    "supertest": "^6.3.3",
    "@types/supertest": "^6.0.2",
    "prisma": "^5.8.0"
  }
}
```

## 2. TypeScript Configuration (tsconfig.json)

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "commonjs",
    "lib": ["ES2022"],
    "outDir": "./dist",
    "rootDir": "./src",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "resolveJsonModule": true,
    "moduleResolution": "node",
    "declaration": true,
    "sourceMap": true
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules", "dist", "tests"]
}
```

## 3. Configuration (src/config/index.ts)

```typescript
import dotenv from 'dotenv';
import { z } from 'zod';

dotenv.config();

const envSchema = z.object({
  NODE_ENV: z.enum(['development', 'production', 'test']).default('development'),
  PORT: z.string().default('3000'),
  DATABASE_URL: z.string(),
  JWT_SECRET: z.string(),
  JWT_ACCESS_EXPIRE: z.string().default('15m'),
  JWT_REFRESH_EXPIRE: z.string().default('7d'),
  REDIS_URL: z.string().optional(),
  CORS_ORIGINS: z.string().default('http://localhost:3000'),
  RATE_LIMIT_WINDOW_MS: z.string().default('60000'),
  RATE_LIMIT_MAX_REQUESTS: z.string().default('100'),
});

const parsed = envSchema.safeParse(process.env);

if (!parsed.success) {
  console.error('Invalid environment variables:', parsed.error.flatten().fieldErrors);
  process.exit(1);
}

export const config = {
  env: parsed.data.NODE_ENV,
  port: parseInt(parsed.data.PORT),
  database: {
    url: parsed.data.DATABASE_URL,
  },
  jwt: {
    secret: parsed.data.JWT_SECRET,
    accessExpire: parsed.data.JWT_ACCESS_EXPIRE,
    refreshExpire: parsed.data.JWT_REFRESH_EXPIRE,
  },
  redis: {
    url: parsed.data.REDIS_URL,
  },
  cors: {
    origins: parsed.data.CORS_ORIGINS.split(','),
  },
  rateLimit: {
    windowMs: parseInt(parsed.data.RATE_LIMIT_WINDOW_MS),
    maxRequests: parseInt(parsed.data.RATE_LIMIT_MAX_REQUESTS),
  },
} as const;
```

## 4. Database Client (src/db/client.ts)

```typescript
import { PrismaClient } from '@prisma/client';
import { config } from '../config';

const prisma = new PrismaClient({
  log: config.env === 'development' ? ['query', 'error', 'warn'] : ['error'],
});

// Graceful shutdown
process.on('beforeExit', async () => {
  await prisma.$disconnect();
});

export { prisma };
```

## 5. Prisma Schema (prisma/schema.prisma)

```prisma
datasource db {
  provider = "postgresql"
  url      = env("DATABASE_URL")
}

generator client {
  provider = "prisma-client-js"
}

enum UserStatus {
  ACTIVE
  INACTIVE
  SUSPENDED
}

model User {
  id        String     @id @default(uuid())
  email     String     @unique
  password  String
  fullName  String     @map("full_name")
  status    UserStatus @default(ACTIVE)
  isAdmin   Boolean    @default(false) @map("is_admin")
  createdAt DateTime   @default(now()) @map("created_at")
  updatedAt DateTime   @updatedAt @map("updated_at")

  @@map("users")
  @@index([email])
}
```

## 6. Request Validators (src/validators/user.validator.ts)

```typescript
import { z } from 'zod';

export const createUserSchema = z.object({
  body: z.object({
    email: z.string().email(),
    fullName: z.string().min(2).max(100),
    password: z.string().min(8).max(100),
  }),
});

export const updateUserSchema = z.object({
  body: z.object({
    fullName: z.string().min(2).max(100).optional(),
    status: z.enum(['ACTIVE', 'INACTIVE', 'SUSPENDED']).optional(),
  }),
  params: z.object({
    id: z.string().uuid(),
  }),
});

export const getUserSchema = z.object({
  params: z.object({
    id: z.string().uuid(),
  }),
});

export const listUsersSchema = z.object({
  query: z.object({
    limit: z.string().transform(Number).pipe(z.number().min(1).max(100)).default('20'),
    offset: z.string().transform(Number).pipe(z.number().min(0)).default('0'),
    sort: z.string().optional(),
  }),
});

export const loginSchema = z.object({
  body: z.object({
    email: z.string().email(),
    password: z.string().min(1),
  }),
});

export type CreateUserInput = z.infer<typeof createUserSchema>;
export type UpdateUserInput = z.infer<typeof updateUserSchema>;
export type GetUserInput = z.infer<typeof getUserSchema>;
export type ListUsersInput = z.infer<typeof listUsersSchema>;
export type LoginInput = z.infer<typeof loginSchema>;
```

## 7. Validation Middleware (src/middleware/validate.ts)

```typescript
import { Request, Response, NextFunction } from 'express';
import { ZodSchema, ZodError } from 'zod';
import { ApiError } from '../utils/errors';

export const validate = (schema: ZodSchema) => {
  return async (req: Request, res: Response, next: NextFunction) => {
    try {
      await schema.parseAsync({
        body: req.body,
        query: req.query,
        params: req.params,
      });
      next();
    } catch (error) {
      if (error instanceof ZodError) {
        const errors = error.errors.map((e) => ({
          field: e.path.join('.'),
          message: e.message,
          code: e.code,
        }));

        next(
          new ApiError(422, 'Validation Error', {
            errors,
            type: 'https://api.example.com/errors/validation',
          })
        );
      } else {
        next(error);
      }
    }
  };
};
```

## 8. JWT Utilities (src/utils/jwt.ts)

```typescript
import jwt from 'jsonwebtoken';
import { config } from '../config';

export interface JwtPayload {
  userId: string;
  email: string;
  isAdmin: boolean;
}

export const createAccessToken = (payload: JwtPayload): string => {
  return jwt.sign(payload, config.jwt.secret, {
    expiresIn: config.jwt.accessExpire,
  });
};

export const createRefreshToken = (payload: JwtPayload): string => {
  return jwt.sign(payload, config.jwt.secret, {
    expiresIn: config.jwt.refreshExpire,
  });
};

export const verifyToken = (token: string): JwtPayload => {
  try {
    return jwt.verify(token, config.jwt.secret) as JwtPayload;
  } catch (error) {
    throw new Error('Invalid token');
  }
};
```

## 9. Password Utilities (src/utils/password.ts)

```typescript
import bcrypt from 'bcrypt';

const SALT_ROUNDS = 10;

export const hashPassword = async (password: string): Promise<string> => {
  return bcrypt.hash(password, SALT_ROUNDS);
};

export const comparePassword = async (
  password: string,
  hash: string
): Promise<boolean> => {
  return bcrypt.compare(password, hash);
};
```

## 10. Auth Middleware (src/middleware/auth.ts)

```typescript
import { Request, Response, NextFunction } from 'express';
import { verifyToken, JwtPayload } from '../utils/jwt';
import { ApiError } from '../utils/errors';

declare global {
  namespace Express {
    interface Request {
      user?: JwtPayload;
    }
  }
}

export const authenticate = (req: Request, res: Response, next: NextFunction) => {
  try {
    const authHeader = req.headers.authorization;
    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      throw new ApiError(401, 'No token provided');
    }

    const token = authHeader.substring(7);
    const payload = verifyToken(token);

    req.user = payload;
    next();
  } catch (error) {
    next(new ApiError(401, 'Invalid or expired token'));
  }
};

export const requireAdmin = (req: Request, res: Response, next: NextFunction) => {
  if (!req.user?.isAdmin) {
    return next(new ApiError(403, 'Admin privileges required'));
  }
  next();
};
```

## 11. Error Handler (src/middleware/errorHandler.ts)

```typescript
import { Request, Response, NextFunction } from 'express';
import { config } from '../config';

export class ApiError extends Error {
  constructor(
    public statusCode: number,
    public message: string,
    public details?: any
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

export const errorHandler = (
  error: Error | ApiError,
  req: Request,
  res: Response,
  next: NextFunction
) => {
  if (error instanceof ApiError) {
    return res.status(error.statusCode).json({
      type: error.details?.type || `https://api.example.com/errors/${error.statusCode}`,
      title: error.message,
      status: error.statusCode,
      detail: error.message,
      instance: req.path,
      ...(error.details && { errors: error.details.errors }),
      ...(config.env === 'development' && { stack: error.stack }),
    });
  }

  // Unhandled errors
  console.error('Unhandled error:', error);
  res.status(500).json({
    type: 'https://api.example.com/errors/500',
    title: 'Internal Server Error',
    status: 500,
    detail: config.env === 'production' ? 'An unexpected error occurred' : error.message,
    instance: req.path,
    ...(config.env === 'development' && { stack: error.stack }),
  });
};

export const notFoundHandler = (req: Request, res: Response) => {
  res.status(404).json({
    type: 'https://api.example.com/errors/404',
    title: 'Not Found',
    status: 404,
    detail: `Route ${req.method} ${req.path} not found`,
    instance: req.path,
  });
};
```

## 12. Rate Limiting (src/middleware/rateLimit.ts)

```typescript
import rateLimit from 'express-rate-limit';
import { config } from '../config';

export const rateLimiter = rateLimit({
  windowMs: config.rateLimit.windowMs,
  max: config.rateLimit.maxRequests,
  message: {
    type: 'https://api.example.com/errors/429',
    title: 'Too Many Requests',
    status: 429,
    detail: 'Rate limit exceeded',
  },
  standardHeaders: true,
  legacyHeaders: false,
});
```

## 13. User Service (src/services/user.service.ts)

```typescript
import { prisma } from '../db/client';
import { hashPassword } from '../utils/password';
import { ApiError } from '../middleware/errorHandler';
import { User, UserStatus } from '@prisma/client';

export class UserService {
  async createUser(data: {
    email: string;
    password: string;
    fullName: string;
  }): Promise<Omit<User, 'password'>> {
    const existing = await prisma.user.findUnique({
      where: { email: data.email },
    });

    if (existing) {
      throw new ApiError(409, 'Email already registered');
    }

    const hashedPassword = await hashPassword(data.password);

    const user = await prisma.user.create({
      data: {
        email: data.email,
        password: hashedPassword,
        fullName: data.fullName,
      },
      select: {
        id: true,
        email: true,
        fullName: true,
        status: true,
        isAdmin: true,
        createdAt: true,
        updatedAt: true,
      },
    });

    return user;
  }

  async getUserById(id: string): Promise<Omit<User, 'password'> | null> {
    return prisma.user.findUnique({
      where: { id },
      select: {
        id: true,
        email: true,
        fullName: true,
        status: true,
        isAdmin: true,
        createdAt: true,
        updatedAt: true,
      },
    });
  }

  async getUserByEmail(email: string): Promise<User | null> {
    return prisma.user.findUnique({
      where: { email },
    });
  }

  async listUsers(limit: number, offset: number) {
    const [users, total] = await Promise.all([
      prisma.user.findMany({
        take: limit,
        skip: offset,
        orderBy: { createdAt: 'desc' },
        select: {
          id: true,
          email: true,
          fullName: true,
          status: true,
          isAdmin: true,
          createdAt: true,
          updatedAt: true,
        },
      }),
      prisma.user.count(),
    ]);

    return { users, total };
  }

  async updateUser(
    id: string,
    data: { fullName?: string; status?: UserStatus }
  ): Promise<Omit<User, 'password'>> {
    const user = await prisma.user.update({
      where: { id },
      data,
      select: {
        id: true,
        email: true,
        fullName: true,
        status: true,
        isAdmin: true,
        createdAt: true,
        updatedAt: true,
      },
    });

    return user;
  }

  async deleteUser(id: string): Promise<void> {
    await prisma.user.delete({
      where: { id },
    });
  }
}

export const userService = new UserService();
```

## 14. Auth Controller (src/controllers/auth.controller.ts)

```typescript
import { Request, Response, NextFunction } from 'express';
import { userService } from '../services/user.service';
import { comparePassword } from '../utils/password';
import { createAccessToken, createRefreshToken } from '../utils/jwt';
import { ApiError } from '../middleware/errorHandler';

export class AuthController {
  async login(req: Request, res: Response, next: NextFunction) {
    try {
      const { email, password } = req.body;

      const user = await userService.getUserByEmail(email);
      if (!user || !(await comparePassword(password, user.password))) {
        throw new ApiError(401, 'Invalid email or password');
      }

      const payload = {
        userId: user.id,
        email: user.email,
        isAdmin: user.isAdmin,
      };

      const accessToken = createAccessToken(payload);
      const refreshToken = createRefreshToken(payload);

      res.json({
        accessToken,
        refreshToken,
        tokenType: 'Bearer',
        expiresIn: 900, // 15 minutes
      });
    } catch (error) {
      next(error);
    }
  }
}

export const authController = new AuthController();
```

## 15. Users Controller (src/controllers/users.controller.ts)

```typescript
import { Request, Response, NextFunction } from 'express';
import { userService } from '../services/user.service';
import { ApiError } from '../middleware/errorHandler';

export class UsersController {
  async create(req: Request, res: Response, next: NextFunction) {
    try {
      const user = await userService.createUser(req.body);
      res.status(201).json(user);
    } catch (error) {
      next(error);
    }
  }

  async list(req: Request, res: Response, next: NextFunction) {
    try {
      const { limit, offset } = req.query as { limit: string; offset: string };
      const { users, total } = await userService.listUsers(
        parseInt(limit),
        parseInt(offset)
      );

      res.json({
        data: users,
        meta: {
          total,
          limit: parseInt(limit),
          offset: parseInt(offset),
          hasMore: parseInt(offset) + parseInt(limit) < total,
        },
      });
    } catch (error) {
      next(error);
    }
  }

  async getById(req: Request, res: Response, next: NextFunction) {
    try {
      const user = await userService.getUserById(req.params.id);
      if (!user) {
        throw new ApiError(404, 'User not found');
      }
      res.json(user);
    } catch (error) {
      next(error);
    }
  }

  async getCurrent(req: Request, res: Response, next: NextFunction) {
    try {
      const user = await userService.getUserById(req.user!.userId);
      if (!user) {
        throw new ApiError(404, 'User not found');
      }
      res.json(user);
    } catch (error) {
      next(error);
    }
  }

  async update(req: Request, res: Response, next: NextFunction) {
    try {
      // Authorization check
      if (req.params.id !== req.user!.userId && !req.user!.isAdmin) {
        throw new ApiError(403, 'Not authorized to update this user');
      }

      const user = await userService.updateUser(req.params.id, req.body);
      res.json(user);
    } catch (error) {
      next(error);
    }
  }

  async delete(req: Request, res: Response, next: NextFunction) {
    try {
      await userService.deleteUser(req.params.id);
      res.status(204).send();
    } catch (error) {
      next(error);
    }
  }
}

export const usersController = new UsersController();
```

## 16. Routes (src/routes/users.routes.ts)

```typescript
import { Router } from 'express';
import { usersController } from '../controllers/users.controller';
import { authenticate, requireAdmin } from '../middleware/auth';
import { validate } from '../middleware/validate';
import {
  createUserSchema,
  updateUserSchema,
  getUserSchema,
  listUsersSchema,
} from '../validators/user.validator';

const router = Router();

router.post(
  '/',
  authenticate,
  requireAdmin,
  validate(createUserSchema),
  usersController.create
);

router.get('/', authenticate, validate(listUsersSchema), usersController.list);

router.get('/me', authenticate, usersController.getCurrent);

router.get(
  '/:id',
  authenticate,
  validate(getUserSchema),
  usersController.getById
);

router.patch(
  '/:id',
  authenticate,
  validate(updateUserSchema),
  usersController.update
);

router.delete(
  '/:id',
  authenticate,
  requireAdmin,
  validate(getUserSchema),
  usersController.delete
);

export default router;
```

## 17. Express App (src/app.ts)

```typescript
import express from 'express';
import 'express-async-errors';
import helmet from 'helmet';
import cors from 'cors';
import morgan from 'morgan';
import { config } from './config';
import { errorHandler, notFoundHandler } from './middleware/errorHandler';
import { rateLimiter } from './middleware/rateLimit';
import authRoutes from './routes/auth.routes';
import usersRoutes from './routes/users.routes';

const app = express();

// Security middleware
app.use(helmet());
app.use(cors({ origin: config.cors.origins, credentials: true }));
app.use(rateLimiter);

// Logging
app.use(morgan(config.env === 'production' ? 'combined' : 'dev'));

// Body parsing
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Health check
app.get('/health', (req, res) => {
  res.json({ status: 'healthy', timestamp: new Date().toISOString() });
});

// API routes
app.use('/api/v1/auth', authRoutes);
app.use('/api/v1/users', usersRoutes);

// Error handling (must be last)
app.use(notFoundHandler);
app.use(errorHandler);

export { app };
```

## 18. Server Entry Point (src/index.ts)

```typescript
import { app } from './app';
import { config } from './config';
import { prisma } from './db/client';

const server = app.listen(config.port, () => {
  console.log(`Server running on port ${config.port}`);
  console.log(`Environment: ${config.env}`);
});

// Graceful shutdown
const gracefulShutdown = async () => {
  console.log('Shutting down gracefully...');

  server.close(async () => {
    await prisma.$disconnect();
    process.exit(0);
  });

  setTimeout(() => {
    console.error('Forced shutdown');
    process.exit(1);
  }, 10000);
};

process.on('SIGTERM', gracefulShutdown);
process.on('SIGINT', gracefulShutdown);
```

## 19. Environment Variables (.env.example)

```env
NODE_ENV=development
PORT=3000

DATABASE_URL="postgresql://user:password@localhost:5432/dbname"

JWT_SECRET="your-secret-key-change-in-production"
JWT_ACCESS_EXPIRE="15m"
JWT_REFRESH_EXPIRE="7d"

REDIS_URL="redis://localhost:6379"

CORS_ORIGINS="http://localhost:3000,http://localhost:8080"

RATE_LIMIT_WINDOW_MS=60000
RATE_LIMIT_MAX_REQUESTS=100
```

## Running the Application

```bash
# Install dependencies
npm install

# Generate Prisma client
npm run generate

# Run migrations
npm run migrate

# Development
npm run dev

# Production build
npm run build
npm start

# Testing
npm test
```

## Key Features

[check] **TypeScript**: Full type safety
[check] **Zod**: Runtime validation
[check] **Prisma**: Type-safe ORM
[check] **JWT**: Authentication with access/refresh tokens
[check] **RBAC**: Role-based authorization
[check] **Error handling**: RFC 9457 (Problem Details)
[check] **Rate limiting**: Express rate limit
[check] **Security**: Helmet, CORS, bcrypt
[check] **Logging**: Morgan + Winston ready
[check] **Testing**: Jest + Supertest setup
[check] **Graceful shutdown**: Proper cleanup

## Best Practices Applied

- Controller-Service-Repository pattern
- Request validation with Zod
- Centralized error handling
- JWT token security
- Database connection pooling
- Environment-based configuration
- Structured logging
- Graceful shutdown handling
- Type safety throughout
- Async error handling with express-async-errors
