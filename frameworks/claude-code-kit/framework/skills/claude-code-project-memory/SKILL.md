---
name: claude-code-project-memory
description: Configure CLAUDE.md project memory files for persistent context, coding standards, architecture decisions, and team conventions. Reference for the 4-tier memory hierarchy and quick-add commands.
---

# Claude Code Project Memory — Meta Reference

This skill provides the definitive reference for configuring CLAUDE.md project memory. Use this when setting up project context that persists across sessions.

---

## Quick Reference

| File | Scope | Purpose |
|------|-------|---------|
| `CLAUDE.md` | Project root | Main project memory |
| `.claude/CLAUDE.md` | Project-specific | Additional context |
| `~/.claude/CLAUDE.md` | User global | Personal preferences |
| `CLAUDE.local.md` | Git-ignored | Local overrides |

## Memory Hierarchy

```text
4-Tier Precedence (highest to lowest):

1. Enterprise settings     (managed by admin)
2. Project memory          (CLAUDE.md, .claude/CLAUDE.md)
3. User global             (~/.claude/CLAUDE.md)
4. Local overrides         (CLAUDE.local.md)
```

### Recursive Loading

Claude reads memories recursively from cwd up to (but not including) root. This enables hierarchical memory in monorepos.

### On-Demand Loading

Subdirectory CLAUDE.md files are **only loaded when Claude accesses files in those directories**. This keeps context focused and prevents token waste on irrelevant parts of your codebase.

---

## CLAUDE.md Template

```markdown
# Project Name

Brief description of the project.

## Architecture

- **Stack**: [technologies]
- **Structure**: [monorepo/microservices/etc]
- **Key patterns**: [patterns used]

## Code Standards

- [Standard 1]
- [Standard 2]
- [Standard 3]

## Development Workflow

1. [Step 1]
2. [Step 2]
3. [Step 3]

## Testing Requirements

- [Testing standard 1]
- [Testing standard 2]

## When Working on This Project

- [Guideline 1]
- [Guideline 2]

## Agent Preferences

- Use `agent-name` for [task type]
- Prefer [approach] over [alternative]
```

---

## Content Categories

### Architecture Documentation

```markdown
## Architecture

### Tech Stack
- **Frontend**: Next.js 16, React 19, TypeScript, Tailwind CSS
- **Backend**: Node.js, Express, Prisma, PostgreSQL
- **Infrastructure**: Docker, Kubernetes, AWS

### Directory Structure
\`\`\`
src/
├── app/           # Next.js app router
├── components/    # React components
├── lib/           # Utilities
├── server/        # API routes
└── prisma/        # Database schema
\`\`\`

### Key Decisions
- ADR-001: Using App Router over Pages Router
- ADR-002: Prisma over raw SQL for type safety
```

### Code Standards

```markdown
## Code Standards

### TypeScript
- Strict mode enabled
- Use `unknown` over `any`
- Prefer interfaces over types for objects

### Naming
- Components: PascalCase
- Functions: camelCase
- Constants: SCREAMING_SNAKE_CASE
- Files: kebab-case

### Imports
- Absolute imports via @/ alias
- Group: external → internal → relative

### Testing
- Test files: `*.test.ts` or `*.spec.ts`
- Minimum 80% coverage for new code
- E2E tests for critical paths
```

### Workflow Instructions

```markdown
## When Working on This Project

1. Always run `npm run typecheck` before committing
2. Use conventional commits: `feat:`, `fix:`, `chore:`
3. Create PR for all changes (no direct push to main)
4. Request review from @team-lead for architecture changes
5. Update CHANGELOG.md for user-facing changes

## Agent Preferences

- Use `backend-engineer` for API changes
- Use `test-architect` for test coverage improvements
- Prefer Vitest over Jest for new tests
- Always run `npm run lint` after code changes
```

---

## Quick-Add Commands

### # Quick Memory Syntax

Start any input with `#` to instantly add to memory:

```text
# Always run tests before committing
# Use TypeScript strict mode
# Prefer Vitest over Jest
```

You'll be prompted to select which memory file to store in.

### /init Command

Creates initial CLAUDE.md by analyzing project:

```bash
/init
```

Generates memory from:
- package.json / pyproject.toml
- Directory structure
- Existing docs
- Git history

### /memory add

Quick-add to project memory:

```bash
/memory add "Always use TypeScript strict mode"
/memory add "Run tests before committing"
```

### /memory show

Display current memory:

```bash
/memory show
```

---

## Session Management

### /clear Command

Reset context for a new task:

```bash
/clear
```

Use `/clear` when switching tasks instead of `/compact`. Starting fresh is faster and avoids context confusion.

### /compact Command

Compress context when needed:

```bash
/compact
```

**Note**: `/compact` is slow (1+ minutes). Prefer `/clear` for new tasks. Only use `/compact` when you need the previous context but are running low on tokens.

---

## Location Strategies

### Single CLAUDE.md (Simple)

```text
project/
├── CLAUDE.md    # All context here
└── src/
```

Best for small projects.

### Split Memory (Modular)

```text
project/
├── CLAUDE.md           # High-level overview
├── .claude/
│   ├── CLAUDE.md       # Detailed standards
│   └── ...
└── src/
```

Best for larger projects with detailed standards.

### Monorepo

```text
monorepo/
├── CLAUDE.md           # Shared standards
├── packages/
│   ├── web/
│   │   └── CLAUDE.md   # Web-specific
│   ├── api/
│   │   └── CLAUDE.md   # API-specific
│   └── shared/
│       └── CLAUDE.md   # Shared lib specific
```

---

## Local Overrides

```markdown
<!-- CLAUDE.local.md (git-ignored) -->

# Local Development Overrides

## My Preferences
- Use verbose logging
- Skip slow tests with --skip-e2e

## Local Environment
- DATABASE_URL points to local Docker
- Using Node 20 instead of 18
```

---

## Enterprise Settings

```text
~/.claude/settings.json
/Library/Application Support/ClaudeCode/managed-settings.json
```

Enterprise admins can set organization-wide defaults that override project memory for:
- Security policies
- Approved tools
- Forbidden patterns

---

## Best Practices

### DO

```markdown
## Good Memory Content

- Specific, actionable instructions
- Link to detailed docs: @docs/architecture.md
- Include examples where helpful
- Keep updated as project evolves
```

### DON'T

```markdown
## Avoid

- Vague guidelines ("write good code")
- Outdated information
- Duplicate information from code comments
- Overly long documents (use @references)
```

---

## File References

Use `@` to reference other files:

```markdown
## Architecture

See @docs/architecture.md for detailed diagrams.

## API Patterns

Follow patterns in @src/api/README.md.
```

Claude loads referenced files as additional context.

---

## Validation Checklist

```text
CLAUDE.md VALIDATION

[ ] Describes project purpose
[ ] Lists tech stack
[ ] Defines code standards
[ ] Specifies testing requirements
[ ] Includes workflow instructions
[ ] Agent preferences documented
[ ] File references are valid (@paths exist)
[ ] Updated within last 30 days
[ ] No sensitive data (secrets, tokens)
```

---

## Navigation

**Resources**
- [resources/memory-patterns.md](resources/memory-patterns.md) — Common patterns
- [resources/memory-examples.md](resources/memory-examples.md) — Full examples
- [data/sources.json](data/sources.json) — Documentation links

**Related Skills**
- [../claude-code-skills/SKILL.md](../claude-code-skills/SKILL.md) — Skill creation
- [../claude-code-agents/SKILL.md](../claude-code-agents/SKILL.md) — Agent creation
- [../docs-codebase/SKILL.md](../docs-codebase/SKILL.md) — Documentation patterns
