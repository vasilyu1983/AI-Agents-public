# Utility Patterns Guide

When and how to extract utilities instead of duplicating code.

---

## Core Principle

**DRY (Don't Repeat Yourself)**: If you write the same function twice, extract it to a shared utility.

---

## Decision Tree: Extract or Inline?

```text
Is this code used in multiple files?
    ├─ Yes → EXTRACT to utils/
    └─ No
        ├─ Does it contain configuration (env vars, secrets)?
        │   └─ Yes → EXTRACT to config/
        ├─ Does it have error handling logic?
        │   └─ Yes → EXTRACT to utils/errors.ts
        ├─ Is it a stateful resource (DB pool, logger, cache)?
        │   └─ Yes → EXTRACT as singleton in utils/
        └─ Is it <5 lines and single-use?
            └─ Yes → Keep INLINE
```

---

## Naming Conventions

### File Names

| Pattern | Location | Example |
|---------|----------|---------|
| `{domain}.ts` | `src/utils/` | `auth.ts`, `validation.ts` |
| `{resource}.ts` | `src/config/` | `database.ts`, `cache.ts` |
| `{middleware-name}.ts` | `src/middleware/` | `auth.ts`, `rate-limit.ts` |

### Function Names

| Type | Convention | Example |
|------|------------|---------|
| Sync utilities | `verbNoun` | `hashPassword`, `formatDate` |
| Async utilities | `verbNoun` | `fetchUser`, `sendEmail` |
| Validators | `isNoun` / `validateNoun` | `isEmail`, `validateToken` |
| Factories | `createNoun` | `createLogger`, `createClient` |
| Getters | `getNoun` | `getConfig`, `getCurrentUser` |

---

## Utility Categories

### 1. Authentication Utilities

**Extract to**: `src/utils/auth.ts`

```typescript
// CENTRALIZED
export const hashPassword = async (password: string): Promise<string> => {
  return bcrypt.hash(password, 12);
};

export const verifyPassword = async (password: string, hash: string): Promise<boolean> => {
  return bcrypt.compare(password, hash);
};

export const generateToken = (payload: TokenPayload): string => {
  return jwt.sign(payload, config.jwtSecret, { expiresIn: '15m' });
};

export const verifyToken = (token: string): TokenPayload => {
  return jwt.verify(token, config.jwtSecret) as TokenPayload;
};
```

### 2. Error Utilities

**Extract to**: `src/utils/errors.ts`

```typescript
// CENTRALIZED
export class AppError extends Error {
  constructor(
    public statusCode: number,
    public message: string,
    public code?: string
  ) {
    super(message);
    this.name = 'AppError';
  }
}

export class NotFoundError extends AppError {
  constructor(resource: string) {
    super(404, `${resource} not found`, 'NOT_FOUND');
  }
}

export class ValidationError extends AppError {
  constructor(message: string, public errors?: Record<string, string[]>) {
    super(422, message, 'VALIDATION_ERROR');
  }
}
```

### 3. Config Utilities

**Extract to**: `src/config/index.ts`

```typescript
// CENTRALIZED
import { z } from 'zod';

const envSchema = z.object({
  NODE_ENV: z.enum(['development', 'production', 'test']),
  PORT: z.coerce.number().default(3000),
  DATABASE_URL: z.string().url(),
  JWT_SECRET: z.string().min(32),
  REDIS_URL: z.string().url().optional(),
});

export const config = envSchema.parse(process.env);
export type Config = z.infer<typeof envSchema>;
```

### 4. Logger Utilities

**Extract to**: `src/utils/logger.ts`

```typescript
// CENTRALIZED - Single logger instance for entire app
import pino from 'pino';
import { config } from '@/config';

export const logger = pino({
  level: config.NODE_ENV === 'production' ? 'info' : 'debug',
  transport: config.NODE_ENV !== 'production'
    ? { target: 'pino-pretty' }
    : undefined,
});
```

### 5. Resilience Utilities

**Extract to**: `src/utils/resilience.ts`

```typescript
// CENTRALIZED
import pRetry from 'p-retry';

export const withRetry = <T>(
  fn: () => Promise<T>,
  options?: { retries?: number; minTimeout?: number }
): Promise<T> => {
  return pRetry(fn, {
    retries: options?.retries ?? 3,
    minTimeout: options?.minTimeout ?? 1000,
    factor: 2,
    randomize: true,
  });
};
```

---

## Import Patterns

### Path Aliases (Recommended)

```json
// tsconfig.json
{
  "compilerOptions": {
    "paths": {
      "@/*": ["./src/*"],
      "@/utils/*": ["./src/utils/*"],
      "@/config": ["./src/config/index.ts"]
    }
  }
}
```

### Usage

```typescript
// Clean imports
import { hashPassword, verifyToken } from '@/utils/auth';
import { AppError, NotFoundError } from '@/utils/errors';
import { config } from '@/config';
import { logger } from '@/utils/logger';
import { withRetry } from '@/utils/resilience';
```

---

## Multi-Language Patterns

### TypeScript/Node.js

```
src/utils/auth.ts     → import { hashPassword } from '@/utils/auth';
```

### Python

```
src/utils/auth.py     → from utils.auth import hash_password
```

### Go

```
internal/utils/auth.go → import "myapp/internal/utils"
```

---

## Template Integration

When templates show utility code, they should include:

```markdown
> **Centralization**: Extract to `src/utils/auth.ts`
>
> ```typescript
> // src/utils/auth.ts
> export const hashPassword = async (password: string) => { ... };
> ```
>
> Then import: `import { hashPassword } from '@/utils/auth';`
```

---

## Checklist Before Copying Code

Before duplicating any utility function:

- [ ] Does this function already exist in `src/utils/`?
- [ ] Could this be useful in other files?
- [ ] Does it handle config, errors, or logging?
- [ ] Is it >5 lines of reusable logic?

If any answer is **yes** → **Extract to utility first**.
