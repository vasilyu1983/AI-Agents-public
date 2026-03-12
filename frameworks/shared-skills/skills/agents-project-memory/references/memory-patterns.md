# Project Memory Patterns (AGENTS.md / CLAUDE.md)

Common patterns for effective project memory configuration.

Use these templates as the content for `AGENTS.md` (Codex). If you support both tools, keep `AGENTS.md` as the single source of truth and symlink `CLAUDE.md` to it.

---

## Pattern 1: Minimal Core Memory

Best for small projects. Keep the primary memory file under 50 lines.

```markdown
# Project Name

Brief one-line description.

## Stack
- Frontend: React, TypeScript
- Backend: Node.js, PostgreSQL

## Commands
- `npm run dev` - Start development
- `npm test` - Run tests
- `npm run build` - Production build

## Code Standards
- TypeScript strict mode
- Prettier for formatting
- ESLint for linting
```

**When to use**: Projects with <10 files, solo developers, simple architectures.

---

## Pattern 2: Team Standards Memory

For teams needing consistent conventions across developers.

```markdown
# Project Name

## Architecture
- Monorepo with Turborepo
- Shared packages in /packages
- Apps in /apps

## Git Workflow
- Branch from `main`
- PR required for all changes
- Squash merge only
- Conventional commits: feat:, fix:, chore:

## Code Review
- 1 approval minimum
- CI must pass
- No console.log in production code

## Testing
- Unit tests for utilities
- Integration tests for APIs
- E2E for critical paths
- 80% coverage minimum
```

**When to use**: Teams of 2+, shared codebases, CI/CD pipelines.

---

## Pattern 3: Reference-Heavy Memory

Use `@` imports for detailed documentation.

```markdown
# Project Name

High-level overview only in this file.

## Quick Reference
- @docs/architecture.md - System design
- @docs/api-patterns.md - API conventions
- @docs/testing-guide.md - Test requirements
- @.claude/agents/README.md - Available agents

## Current Sprint
- Feature X in progress
- Bug Y needs fixing

## Agent Preferences
- Use `backend-engineer` for API work
- Use `test-architect` for coverage
```

**When to use**: Large codebases, detailed documentation exists, token optimization needed.

---

## Pattern 4: Monorepo Memory

Hierarchical memory for multi-package repositories.

```text
monorepo/
├── AGENTS.md              # Primary memory file
├── CLAUDE.md              # Symlink → AGENTS.md
├── packages/
│   ├── web/
│   │   ├── AGENTS.md      # Web-specific
│   │   └── CLAUDE.md      # Symlink → AGENTS.md
│   ├── api/
│   │   ├── AGENTS.md      # API-specific
│   │   └── CLAUDE.md      # Symlink → AGENTS.md
│   └── shared/
│       ├── AGENTS.md      # Shared lib
│       └── CLAUDE.md      # Symlink → AGENTS.md
```

**Root memory file (AGENTS.md or CLAUDE.md)**:
```markdown
# Monorepo Standards

## Shared Rules
- All packages use TypeScript
- Shared ESLint config
- Turborepo for builds

## Package Commands
- `turbo run build` - Build all
- `turbo run test` - Test all
- `turbo run dev --filter=web` - Dev specific
```

**Package memory file (AGENTS.md or CLAUDE.md)**:
```markdown
# Web Package

Inherits from root. Additional rules:

## Stack
- Next.js 16 App Router
- Tailwind CSS
- Zustand for state

## Testing
- Vitest for unit
- Playwright for E2E
```

---

## Pattern 5: Local Development Overrides

Use CLAUDE.local.md for personal preferences (git-ignored). If Codex is your primary tool, keep local overrides in a git-ignored notes file and merge into AGENTS.md only when needed.

```markdown
<!-- CLAUDE.local.md -->

# My Local Setup

## Environment
- Using Docker for database
- Node 20 instead of 18
- DATABASE_URL=postgresql://localhost:5432/dev

## Preferences
- Verbose logging enabled
- Skip slow E2E tests: --skip-e2e
- Use experimental features

## Debugging Notes
- Auth service on port 3001
- Redis on port 6379
```

---

## Anti-Patterns to Avoid

### Don't: Generic Instructions

```markdown
# Bad Example
- Write clean code
- Follow best practices
- Be efficient
```

### Don't: Duplicate Code Comments

```markdown
# Bad Example
## UserService
The UserService handles user operations...
(already documented in code)
```

### Don't: Outdated Information

```markdown
# Bad Example
## Database
Using MySQL 5.7  # Actually migrated to PostgreSQL
```

### Don't: Sensitive Data

```markdown
# Bad Example
API_KEY=sk-12345...  # Never put secrets here
```

---

## Pattern 6: Behavioral Coding Rules

Explicit cognitive guardrails to prevent common AI failure modes (assumption errors, scope creep, over-engineering).

**File**: `.claude/rules/coding-behavior.md`

```markdown
# Coding Behavior Rules

## Before Implementation

- **Surface assumptions**: List them explicitly, ask for correction before proceeding
- **Manage confusion**: STOP when encountering ambiguity, name the specific confusion, wait for resolution
- **Inline planning**: For multi-step tasks, emit lightweight plan before executing

## During Implementation

- **Scope discipline**: Touch only what's asked—no unsolicited cleanup, refactoring, or "improvements"
- **Simplicity enforcement**: Prefer boring, obvious solutions; if 100 lines suffice, don't write 1000
- **Push back when warranted**: Point out problems directly; "Of course!" to bad ideas helps no one

## After Changes

- **Change summary**: Report CHANGES MADE / INTENTIONALLY UNTOUCHED / POTENTIAL CONCERNS
- **Dead code hygiene**: Identify unreachable code explicitly, ask before deleting
- **Preserve unknowns**: Don't remove code or comments you don't fully understand
```

**When to use**: Teams experiencing AI over-engineering, scope creep, silent assumption errors, or sycophantic responses.

**Key failure modes this prevents**:
1. Making wrong assumptions without checking
2. Not surfacing inconsistencies or tradeoffs
3. Being sycophantic ("Of course!") to bad ideas
4. Overcomplicating code and APIs
5. Modifying code orthogonal to the task

---

## Pattern 7: Cross-Platform Memory (AGENTS.md + CLAUDE.md)

Share project memory and behavioral rules across multiple AI coding tools.

### Directory Structure

```text
your-project/
├── AGENTS.md                    # Primary (Codex) or mirror
├── CLAUDE.md                    # Primary (Claude Code) or mirror
└── .claude/
    └── rules/
        ├── coding-behavior.md   # Behavioral rules (tool-agnostic)
        ├── security.md          # Security rules
        └── testing.md           # Testing standards
```

### Setup Commands

**macOS/Linux** (symlink):
```bash
# AGENTS.md primary
ln -sf AGENTS.md CLAUDE.md
```

**Windows** (copy or script):
```powershell
# Copy approach (simpler, requires manual sync)
Copy-Item AGENTS.md CLAUDE.md

# Or create sync script in package.json
# "sync:agents": "cp AGENTS.md CLAUDE.md"
```

### Unified Memory File Template

```markdown
# Project Name

Cross-platform instructions for AI coding assistants.

## Overview
Brief project description...

## Architecture
@docs/architecture.md

## Code Standards
- TypeScript strict mode
- Prettier + ESLint
- 80% test coverage

## Behavioral Rules
@.claude/rules/coding-behavior.md

## Testing
@.claude/rules/testing.md

## Tool-Specific Notes

### Claude Code
- Full `.claude/rules/` support
- Skills available in `.claude/skills/`

### Codex CLI
- Reads AGENTS.md directly
- Use @imports only if your Codex tooling supports them; otherwise inline essentials

### Cursor
- Copy rules to `.cursorrules` if @imports unsupported
```

### Tool Compatibility Matrix

| Feature | Claude Code | Codex CLI | Cursor |
|---------|-------------|-----------|--------|
| Primary file | CLAUDE.md | AGENTS.md | .cursorrules |
| @imports | ✓ | Varies by setup | Limited |
| .claude/rules/ | ✓ | Via @import if supported | Copy needed |
| Symlink support | ✓ | ✓ | ✓ |

### Best Practices

1. **Single source of truth**: Keep AGENTS.md as primary, symlink CLAUDE.md
2. **Tool-agnostic rules**: Write rules that work for any AI assistant
3. **@import for depth**: Reference detailed docs, don't duplicate
4. **Git-track symlinks**: Symlinks work in git repos across platforms

**When to use**: Teams using multiple AI coding assistants (Claude Code + Cursor, Claude Code + Codex CLI, etc.) who want consistent behavior across all tools.

---

## Memory Size Guidelines

| Project Size | Primary File Lines | Strategy |
|--------------|-----------------|----------|
| Small (<10 files) | 20-50 | Single file, minimal |
| Medium (10-100 files) | 50-100 | Core + @references |
| Large (100+ files) | 50-100 | Hierarchy + @references |
| Monorepo | 30-50 per package | Inheritance pattern |

**Rule**: If the primary memory file exceeds 150 lines, split into @referenced files.
