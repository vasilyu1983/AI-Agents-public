# Large Codebase Strategy (100K-1M LOC)

Configuration patterns for enterprise-scale codebases with Claude Code and Codex. Use `AGENTS.md` as the primary memory file and symlink `CLAUDE.md` to it.

---
## Table of Contents

- [Overview](#overview)
- [Hierarchical Documentation Structure](#hierarchical-documentation-structure)
- [Root Memory File Template (AGENTS.md / CLAUDE.md)](#root-memory-file-template-agentsmd-claudemd)
- [Enterprise App](#enterprise-app)
- [Quick Navigation](#quick-navigation)
- [Architecture Overview](#architecture-overview)
- [Critical Rules (All Packages)](#critical-rules-all-packages)
- [When Working Here](#when-working-here)
- [Package-Level Memory File Template (AGENTS.md / CLAUDE.md)](#package-level-memory-file-template-agentsmd-claudemd)
- [API Package](#api-package)
- [Stack](#stack)
- [Directory Structure](#directory-structure)
- [Patterns](#patterns)
- [Testing](#testing)
- [When Working Here](#when-working-here)
- [Context Loading Strategy](#context-loading-strategy)
- [Automatic Loading (Claude Code)](#automatic-loading-claude-code)
- [Codex Notes](#codex-notes)
- [Manual Context Management](#manual-context-management)
- [Check what's loaded](#check-whats-loaded)
- [Navigate to package for focused context](#navigate-to-package-for-focused-context)
- [Edit/view memory](#editview-memory)
- [Token Budget Management](#token-budget-management)
- [Estimation](#estimation)
- [Budget Allocation (200K context)](#budget-allocation-200k-context)
- [File Reference Patterns](#file-reference-patterns)
- [From Root](#from-root)
- [Architecture](#architecture)
- [From Package](#from-package)
- [API Routes](#api-routes)
- [Testing](#testing)
- [Root Standards](#root-standards)
- [Monorepo Patterns](#monorepo-patterns)
- [Turborepo Setup](#turborepo-setup)
- [Root memory file (AGENTS.md / CLAUDE.md)](#root-memory-file-agentsmd-claudemd)
- [Turbo Commands](#turbo-commands)
- [Package Dependencies](#package-dependencies)
- [Package Isolation](#package-isolation)
- [Performance Tips](#performance-tips)
- [Keep Memory Files Small](#keep-memory-files-small)
- [Use Referenced Docs Sparingly](#use-referenced-docs-sparingly)
- [Bad - duplicates content](#bad-duplicates-content)
- [Good - reference external file for Claude](#good-reference-external-file-for-claude)
- [Strategic Navigation](#strategic-navigation)
- [Don't work from root on large changes](#dont-work-from-root-on-large-changes)
- [Now Claude loads API-specific context](#now-claude-loads-api-specific-context)
- [and you have more token budget for code](#and-you-have-more-token-budget-for-code)
- [Scaling Checklist](#scaling-checklist)
- [Example: 500K LOC Migration](#example-500k-loc-migration)
- [Before (Single File)](#before-single-file)
- [App (500K LOC)](#app-500k-loc)
- [After (Hierarchical)](#after-hierarchical)
- [Related Resources](#related-resources)


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
| api | REST/GraphQL backend | `packages/api/AGENTS.md` |
| web | Next.js frontend | `packages/web/AGENTS.md` |
| mobile | React Native app | `packages/mobile/AGENTS.md` |
| shared | Shared utilities | `packages/shared/AGENTS.md` |

Keep `AGENTS.md` as primary and symlink `CLAUDE.md` to it when you want a shared file. Put the shared essentials in the root file and let nested package files carry only their local rules.

## Architecture Overview

- **Monorepo**: Turborepo + pnpm workspaces
- **Backend**: Node.js + TypeScript + PostgreSQL
- **Frontend**: Next.js 16 + React 19
- **Mobile**: React Native + Expo

## Critical Rules (All Packages)

1. All code must pass `pnpm lint` and `pnpm test`
2. No direct database access outside `/packages/api`
3. Shared types MUST go in `/packages/shared`
4. Shared security rules belong in the root memory file; Claude can keep extra detail in `.claude/rules/security.md`

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

Codex should use a directory-based `AGENTS.md` hierarchy:
- Keep shared repo rules in the root `AGENTS.md`
- Add package-level `AGENTS.md` files only where local conventions matter
- Run Codex from the relevant subtree or keep the cwd inside that package so the directory chain applies naturally
- Keep personal behavioral instructions in `~/.codex/AGENTS.md`; keep runtime defaults in `~/.codex/config.toml`
- Use `AGENTS.override.md` when one directory needs higher-precedence guidance. It may be local or checked in; its defining behavior is that it wins over `AGENTS.md` at the same level

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
## Architecture
@docs/architecture/overview.md
@docs/architecture/data-flow.md
```

Use the `@...` form above for Claude-friendly references. For Codex, prefer nested `AGENTS.md` files in those package directories rather than depending on import syntax.

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
2. Repeat only the root rules that are essential locally
3. Not duplicate large tutorials or inventories

---

## Performance Tips

### Keep Memory Files Small

- Root memory file: <100 lines
- Package memory file: <150 lines
- Rule files: <50 lines each

### Use Referenced Docs Sparingly

Instead of duplicating content:

```markdown
# Bad - duplicates content
[paste entire style guide here]

# Good - reference external file for Claude
See @docs/style-guide.md for code style.
```

For Codex, prefer plain links in the prose and nested `AGENTS.md` files for directory-specific rules.

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
- [ ] Detailed docs stay outside the root memory file
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
