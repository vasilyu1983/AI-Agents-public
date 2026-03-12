# Large Codebase Strategy (100K-1M LOC)

Configuration patterns for enterprise-scale codebases with Claude Code and Codex. Use `AGENTS.md` as the primary memory file and symlink `CLAUDE.md` to it.

---

## Overview

Large codebases require hierarchical documentation, strategic context loading, and careful token management. This guide covers patterns for 100K-1M+ line codebases.

---

## Hierarchical Documentation Structure

```text
enterprise-app/
├── AGENTS.md                    # Primary memory file
├── CLAUDE.md                    # Symlink → AGENTS.md
├── .claude/
│   ├── rules/
│   │   ├── security.md          # Global security rules
│   │   ├── testing.md           # Global testing standards
│   │   └── code-style.md        # Global style guide
│   └── settings.json
│
├── packages/
│   ├── api/
│   │   ├── AGENTS.md              # API-specific context
│   │   └── CLAUDE.md              # Symlink → AGENTS.md
│   ├── web/
│   │   ├── AGENTS.md              # Frontend-specific context
│   │   └── CLAUDE.md              # Symlink → AGENTS.md
│   ├── mobile/
│   │   ├── AGENTS.md              # Mobile-specific context
│   │   └── CLAUDE.md              # Symlink → AGENTS.md
│   └── shared/
│       ├── AGENTS.md              # Shared library context
│       └── CLAUDE.md              # Symlink → AGENTS.md
│
└── services/
    ├── auth/
    │   ├── AGENTS.md              # Auth service context
    │   └── CLAUDE.md              # Symlink → AGENTS.md
    ├── payments/
    │   ├── AGENTS.md              # Payments context
    │   └── CLAUDE.md              # Symlink → AGENTS.md
    └── notifications/
        ├── AGENTS.md              # Notifications context
        └── CLAUDE.md              # Symlink → AGENTS.md
```

---

## Root Memory File Template (AGENTS.md / CLAUDE.md)

Keep root file **under 100 lines**. Focus on navigation and high-level architecture.

```markdown
# Enterprise App

Monorepo with 500K+ LOC across 12 packages.

## Quick Navigation

| Package | Purpose | Memory File |
|---------|---------|-----------|
| api | REST/GraphQL backend | @packages/api/AGENTS.md |
| web | Next.js frontend | @packages/web/AGENTS.md |
| mobile | React Native app | @packages/mobile/AGENTS.md |
| shared | Shared utilities | @packages/shared/AGENTS.md |

Keep `AGENTS.md` as primary and symlink `CLAUDE.md` to it. Keep the same @imports in the primary file.

## Architecture Overview

- **Monorepo**: Turborepo + pnpm workspaces
- **Backend**: Node.js + TypeScript + PostgreSQL
- **Frontend**: Next.js 16 + React 19
- **Mobile**: React Native + Expo

## Critical Rules (All Packages)

1. All code must pass `pnpm lint` and `pnpm test`
2. No direct database access outside `/packages/api`
3. Shared types MUST go in `/packages/shared`
4. Security rules: @.claude/rules/security.md

## When Working Here

- In Claude Code, use `/memory` to check loaded memory
- Navigate to specific package before detailed work
- Reference package-specific memory files for domain context
```

---

## Package-Level Memory File Template (AGENTS.md / CLAUDE.md)

Each package gets focused, domain-specific context.

```markdown
# API Package

REST and GraphQL API server.

## Stack

- Node.js 24 LTS
- Fastify 5.x + tRPC
- PostgreSQL 18 + Prisma 6
- Redis for caching

## Directory Structure

```text
packages/api/
├── src/
│   ├── routes/          # HTTP endpoints
│   ├── services/        # Business logic
│   ├── repositories/    # Data access
│   └── middleware/      # Auth, validation
├── prisma/
│   └── schema.prisma    # Database schema
└── tests/
    ├── unit/
    └── integration/
```

## Patterns

- Repository pattern for data access
- Service layer for business logic
- Zod for request validation
- Prisma for ORM

## Testing

- Unit: Vitest
- Integration: Supertest + test DB
- Coverage target: 80%

## When Working Here

1. Run `pnpm prisma generate` after schema changes
2. Add migrations with `pnpm prisma migrate dev`
3. All endpoints need Zod schemas
4. See @tests/fixtures for test data patterns
```

---

## Context Loading Strategy

### Automatic Loading (Claude Code)

Claude Code automatically loads:
- Root `CLAUDE.md`
- `.claude/rules/*.md` files
- Subdirectory `CLAUDE.md` when you access files there

### Codex Notes

Codex reads `AGENTS.md` in the working directory. For package-level context, run Codex from that package directory or mirror the package context into the root file.

### Manual Context Management

```bash
# Check what's loaded
/memory

# Navigate to package for focused context
cd packages/api

# Edit/view memory
/memory
```

---

## Token Budget Management

### Estimation

| Content | ~Tokens |
|---------|---------|
| 100 lines primary memory file | ~500 |
| Package memory file | ~300 |
| Rule file | ~200 |

### Budget Allocation (200K context)

| Category | Budget | Purpose |
|----------|--------|---------|
| System prompt | 10K | Claude Code internals |
| Memory files | 5K | Project memory file hierarchy |
| Conversation | 50K | Chat history |
| Working files | 100K | Code you're editing |
| Reserve | 35K | Safety margin |

---

## File Reference Patterns

### From Root

```markdown
## Package Docs
@packages/api/AGENTS.md
@packages/web/AGENTS.md

## Architecture
@docs/architecture/overview.md
@docs/architecture/data-flow.md
```

### From Package

```markdown
## API Routes
@src/routes/README.md

## Testing
@tests/README.md

## Root Standards
@../../.claude/rules/security.md
```

---

## Monorepo Patterns

### Turborepo Setup

```markdown
# Root memory file (AGENTS.md / CLAUDE.md)

## Turbo Commands

- `pnpm build` - Build all packages
- `pnpm dev` - Start dev servers
- `pnpm test` - Run all tests
- `pnpm lint` - Lint all packages

## Package Dependencies

```text
shared → api, web, mobile
api → (standalone)
web → shared
mobile → shared
```
```

### Package Isolation

Each package memory file should:
1. Be self-contained for that domain
2. Reference shared standards via @
3. Not duplicate root-level rules

---

## Performance Tips

### Keep Memory Files Small

- Root memory file: <100 lines
- Package memory file: <150 lines
- Rule files: <50 lines each

### Use @references

Instead of duplicating content:

```markdown
# Bad - duplicates content
[paste entire style guide here]

# Good - reference external file
See @docs/style-guide.md for code style.
```

### Strategic Navigation

```bash
# Don't work from root on large changes
cd packages/api

# Now Claude loads API-specific context
# and you have more token budget for code
```

---

## Scaling Checklist

- [ ] Root memory file is navigation-focused (<100 lines)
- [ ] Each package has focused memory file
- [ ] Global rules in `.claude/rules/`
- [ ] No duplicated content across files
- [ ] @references for detailed docs
- [ ] Token budget allows for code context
- [ ] `/memory` shows expected files

---

## Example: 500K LOC Migration

### Before (Single File)

```markdown
# App (500K LOC)

[2000 lines of everything]
```

### After (Hierarchical)

```text
AGENTS.md (80 lines - navigation)
├── .claude/rules/ (3 files, ~150 lines total)
├── packages/api/AGENTS.md (100 lines)
├── packages/web/AGENTS.md (120 lines)
├── packages/mobile/AGENTS.md (90 lines)
└── packages/shared/AGENTS.md (60 lines)

Total: ~600 lines across 8 files
Loaded per session: ~200-400 lines (context-dependent)
```

---

## Related Resources

- [memory-patterns.md](memory-patterns.md) - Common memory patterns
- [memory-examples.md](memory-examples.md) - Full examples
- [agents-skills](../../agents-skills/SKILL.md) - Skill creation
