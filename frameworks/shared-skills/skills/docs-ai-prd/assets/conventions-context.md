# Conventions Context Template

Template for documenting project conventions in CLAUDE.md.

---

```markdown
## Conventions

### Naming Conventions

| Type | Convention | Example |
|------|------------|---------|
| Files | kebab-case | `user-service.ts` |
| Directories | kebab-case | `api-handlers/` |
| Classes | PascalCase | `UserService` |
| Functions | camelCase | `getUserById` |
| Variables | camelCase | `userName` |
| Constants | SCREAMING_SNAKE | `MAX_RETRY_COUNT` |
| Interfaces | PascalCase (I prefix optional) | `IUserRepository` or `UserRepository` |
| Types | PascalCase | `UserCreateInput` |
| Enums | PascalCase + SCREAMING values | `UserRole.ADMIN` |
| Database tables | snake_case | `user_accounts` |
| Database columns | snake_case | `created_at` |
| API endpoints | kebab-case | `/api/user-profiles` |
| Environment vars | SCREAMING_SNAKE | `DATABASE_URL` |

### File Organization

- One class/service per file
- Barrel exports via `index.ts` in each directory
- Tests co-located as `*.test.ts` or in `__tests__/` directory
- DTOs separate from entities

### Import Order

```typescript
// 1. External libraries
import { Injectable } from '@nestjs/common';
import { z } from 'zod';

// 2. Internal absolute imports
import { PrismaService } from '@/db/prisma';
import { logger } from '@/utils/logger';

// 3. Relative imports
import { UserDto } from './dto/user.dto';
import { validateUser } from './validators';
```

### Code Style

- [Formatter]: Prettier with default config
- [Linter]: ESLint with recommended rules
- [Type checking]: TypeScript strict mode
- Max line length: 100 characters
- Indentation: 2 spaces
- Quotes: Single quotes for JS/TS, double for JSX attributes
- Semicolons: [Yes/No]
- Trailing commas: ES5

### Error Handling

- Use custom error classes from `src/errors/`
- Always catch and wrap external service errors
- Include error codes for client-facing errors
- Log errors with context (userId, requestId)

### Logging

- Use structured logging (JSON format)
- Include correlation IDs in all logs
- Log levels: ERROR, WARN, INFO, DEBUG
- Never log sensitive data (passwords, tokens)

### Testing Conventions

- Test file naming: `*.test.ts` or `*.spec.ts`
- Describe blocks match class/function names
- Use descriptive test names: "should [action] when [condition]"
- Arrange-Act-Assert pattern
- Mock external dependencies

### Git Conventions

- Branch naming: `feature/`, `fix/`, `chore/`, `refactor/`
- Commit format: Conventional Commits (`feat:`, `fix:`, `docs:`)
- PR titles match commit format
- Squash merge to main
```

---

## Usage

1. Copy the template above
2. Adjust conventions to match your project
3. Remove sections that don't apply
4. Add project-specific conventions

## Customization Tips

- Add language-specific conventions (Python, Go, Rust)
- Include framework-specific patterns (React, Django, Rails)
- Document team-specific conventions not in linter configs
