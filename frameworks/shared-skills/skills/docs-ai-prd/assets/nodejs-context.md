# Node.js/TypeScript CLAUDE.md Template

Copy and customize for Node.js or TypeScript projects.

---

```markdown
# [Project Name]

[One-line description of what this project does]

## Tech Stack

- **Runtime**: Node.js [version] / Bun / Deno
- **Language**: TypeScript [version] / JavaScript (ESM/CJS)
- **Framework**: [Express / Fastify / NestJS / Hono / None]
- **Database**: [PostgreSQL / MySQL / MongoDB / SQLite] via [Prisma / TypeORM / Drizzle / Mongoose]
- **Cache**: [Redis / Memcached / None]
- **Queue**: [BullMQ / RabbitMQ / SQS / None]
- **Testing**: [Jest / Vitest / Mocha] + [Supertest / MSW]

## Architecture

[2-3 sentences describing the overall design approach]

### Directory Structure

```
src/
├── api/              # HTTP handlers (routes, controllers)
│   ├── routes/       # Route definitions
│   ├── middleware/   # Express/Fastify middleware
│   └── handlers/     # Request handlers
├── services/         # Business logic layer
├── repositories/     # Data access layer
├── models/           # Database models/entities
│   ├── entities/     # ORM entities
│   └── dto/          # Data transfer objects
├── utils/            # Shared utilities
├── config/           # Configuration management
├── types/            # TypeScript type definitions
└── __tests__/        # Test files (or co-located)
```

### Key Patterns

- **Repository Pattern**: Data access abstracted via `src/repositories/`
- **Service Layer**: Business logic in `src/services/`, no direct DB access in handlers
- **Dependency Injection**: [NestJS DI / tsyringe / manual / none]
- **Error Handling**: Custom error classes in `src/errors/`, global handler in middleware

### Data Flow

```
Request → Middleware (auth, validation) → Handler → Service → Repository → Database
                                                                    ↓
Response ← Handler ← Service ← Repository ←─────────────────────────┘
```

## Conventions

### Naming

| Type | Convention | Example |
|------|------------|---------|
| Files | kebab-case | `user-service.ts` |
| Classes | PascalCase | `UserService` |
| Functions | camelCase | `getUserById` |
| Constants | SCREAMING_SNAKE | `MAX_RETRY_COUNT` |
| Interfaces | PascalCase + I prefix (optional) | `IUserRepository` or `UserRepository` |
| Types | PascalCase | `UserCreateInput` |
| Enums | PascalCase + SCREAMING values | `UserRole.ADMIN` |

### File Organization

- One class/service per file
- Barrel exports via `index.ts` in each directory
- Tests co-located as `*.test.ts` or `*.spec.ts`
- DTOs separate from entities

### TypeScript

- Strict mode enabled (`strict: true`)
- Explicit return types on public functions
- Avoid `any` - use `unknown` + type guards
- Prefer interfaces for objects, types for unions/primitives

### Imports

```typescript
// Order: external → internal → relative
import { Injectable } from '@nestjs/common';
import { PrismaService } from '@/db/prisma';
import { UserDto } from './dto/user.dto';
```

## Key Files

| Purpose | Location | Notes |
|---------|----------|-------|
| Entry point | `src/index.ts` or `src/main.ts` | Server bootstrap |
| App setup | `src/app.ts` | Express/Fastify app configuration |
| Routes | `src/api/routes/index.ts` | Route registration |
| Database client | `src/db/client.ts` | Prisma/TypeORM instance |
| Config | `src/config/index.ts` | Environment variable loading |
| Types | `src/types/index.ts` | Shared type definitions |
| Constants | `src/constants/index.ts` | App-wide constants |

## Configuration

### Environment Variables

```bash
# .env.example
NODE_ENV=development
PORT=3000
DATABASE_URL=postgresql://user:pass@localhost:5432/db
REDIS_URL=redis://localhost:6379
JWT_SECRET=your-secret-here
LOG_LEVEL=debug
```

### Config Loading Pattern

```typescript
// src/config/index.ts
export const config = {
  port: parseInt(process.env.PORT || '3000'),
  db: { url: process.env.DATABASE_URL },
  // ... validated with zod/joi
};
```

## Commands

```bash
# Development
npm run dev              # Start with hot reload (nodemon/tsx)
npm run build            # Compile TypeScript
npm start                # Run compiled JS

# Database
npm run db:migrate       # Run migrations
npm run db:generate      # Generate Prisma client
npm run db:seed          # Seed database
npm run db:studio        # Open Prisma Studio

# Testing
npm test                 # Run all tests
npm run test:watch       # Watch mode
npm run test:cov         # With coverage
npm run test:e2e         # E2E tests

# Quality
npm run lint             # ESLint
npm run lint:fix         # Auto-fix
npm run format           # Prettier
npm run typecheck        # tsc --noEmit
```

## Important Context

### Technical Decisions

#### [Why Prisma over TypeORM]
**Context**: Needed type-safe database access
**Decision**: Prisma for better DX and type generation
**Trade-off**: Less flexible raw queries, migration workflow different

### Known Gotchas

- **Prisma client regeneration**: Run `npm run db:generate` after schema changes
- **Circular dependencies**: Use barrel exports carefully, may need lazy imports
- **BigInt handling**: JSON.stringify fails on BigInt, use `BigInt.prototype.toJSON`
- **Date timezone**: All dates stored as UTC, convert on display

### Historical Context

- [Any migrations, refactors, or legacy patterns to know about]

## Testing

### Test Structure

```typescript
// src/services/__tests__/user.service.test.ts
describe('UserService', () => {
  describe('create', () => {
    it('should create user with valid input', async () => {});
    it('should throw on duplicate email', async () => {});
  });
});
```

### Mocking

- Database: Mock repository layer, not Prisma directly
- External APIs: Use MSW for HTTP mocks
- Time: Use `jest.useFakeTimers()` for time-dependent tests

## For AI Assistants

### When modifying this codebase:

- Follow existing patterns in similar files
- Add tests for new functionality
- Update DTOs when changing API contracts
- Run `npm run lint && npm run typecheck` before committing
- Use existing error classes from `src/errors/`

### Patterns to follow:

- Services return domain objects, handlers transform to DTOs
- All database operations through repositories
- Validation at API boundary (middleware or decorators)
- Async/await everywhere, no callbacks

### Avoid:

- Direct database queries outside repositories
- `console.log` in production code (use logger)
- Synchronous file operations
- Mutations in service layer (return new objects)
- `any` type without explicit justification
```

---

## Quick Start Commands

Run these to gather context for a new Node.js project:

```bash
# Basic structure
tree -L 3 -I 'node_modules|dist|.git|coverage'

# Dependencies
cat package.json | jq '{dependencies, devDependencies, scripts}'

# TypeScript config
cat tsconfig.json | jq '{compilerOptions: {target, module, strict}}'

# Entry point
head -50 src/index.ts || head -50 src/main.ts

# Find all services
find src -name "*service*" -o -name "*Service*"

# Check for ORM
ls prisma/ 2>/dev/null || ls src/entities/ 2>/dev/null
```
