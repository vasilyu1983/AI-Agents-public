# Cross-Tool Context Template

*Purpose: Unified project context template that works across multiple AI coding assistants (Claude Code, Cursor, Copilot, Windsurf, Cline).*

---

## Quick Setup

Copy this template to the appropriate location for your tool:

| Tool | Primary Location | Alternative |
|------|------------------|-------------|
| Claude Code | `CLAUDE.md` (repo root) | `.claude/CLAUDE.md` |
| Cursor | `.cursor/rules/project.md` | `.cursorrules` |
| Windsurf | `.windsurf/rules/project.md` | — |
| Copilot | `.github/copilot-instructions.md` | — |
| Cline | `.cline/rules.md` | `.clinerules` |
| Generic | `AGENTS.md` (repo root) | — |

---

## Universal Context Template

```markdown
# [Project Name]

Brief description of purpose and what this project does.

## Tech Stack

- Language: [e.g., TypeScript 5.x, Python 3.12]
- Framework: [e.g., Next.js 15, FastAPI]
- Database: [e.g., PostgreSQL 16, SQLite]
- Package Manager: [e.g., pnpm, uv]

## Architecture

### Key Directories

- `src/` - Main source code
- `src/api/` - API routes/handlers
- `src/services/` - Business logic
- `src/models/` - Data models/schemas
- `tests/` - Test files

### Data Flow

1. Request → API handler
2. Handler → Service → Database
3. Response ← Service ← Handler

## Conventions

### Naming

- Files: kebab-case (`user-service.ts`)
- Functions: camelCase (`getUserById`)
- Classes: PascalCase (`UserService`)
- Constants: SCREAMING_SNAKE (`MAX_RETRIES`)

### Patterns

- [Pattern 1, e.g., Repository pattern for data access]
- [Pattern 2, e.g., DTOs for API input/output]

## Key Files

| Purpose | Location | Notes |
|---------|----------|-------|
| Entry point | `src/index.ts` | Server bootstrap |
| Config | `src/config/index.ts` | Environment loading |
| Auth | `src/middleware/auth.ts` | JWT validation |

## Commands

```bash
# Development
[package-manager] run dev

# Testing
[package-manager] test

# Build
[package-manager] run build

# Lint
[package-manager] run lint
```

## Important Context

### Design Decisions

- [Decision 1 with rationale]
- [Decision 2 with rationale]

### Known Gotchas

- [Gotcha 1 - what to watch out for]
- [Gotcha 2 - non-obvious behavior]

## For AI Assistants

### When modifying code:

- Follow existing patterns in similar files
- Add tests for new functionality
- Run lint before committing
- Keep functions small and focused

### Avoid:

- Direct database queries outside repositories
- Console.log in production code (use logger)
- Hardcoded configuration values
- Breaking existing API contracts
```

---

## Tool-Specific Additions

### Claude Code Specific

Add to `CLAUDE.md`:

```markdown
## Claude Code Settings

### Preferred Tools
- Use Read over cat for file contents
- Use Grep over grep/rg for searching
- Use Edit over sed for modifications

### Session Patterns
- Use planning mode for >3 file changes
- Update this file after major refactors
- Log session discoveries in ## Recent Changes
```

### Cursor Specific

Add to `.cursor/rules/project.md`:

```markdown
## Cursor Settings

### Composer Preferences
- Prefer atomic changes over large refactors
- Always show file diffs before applying
- Use @codebase for context when needed

### Agent Mode
- Enable for multi-file changes
- Disable for quick single-file edits
```

### Copilot Specific

Add to `.github/copilot-instructions.md`:

```markdown
## Copilot Settings

### Workspace Context
- Reference package.json for dependencies
- Check tsconfig.json for TypeScript settings
- Review existing tests for patterns

### Code Style
- Match surrounding code style
- Use existing utility functions
- Follow established error patterns
```

---

## Multi-Tool Projects

For projects using multiple AI coding tools, create a shared `AGENTS.md` at repo root with common context, then tool-specific files for overrides:

```text
repo/
├── AGENTS.md              # Shared context (all tools read this)
├── CLAUDE.md              # Claude-specific additions
├── .cursor/
│   └── rules/
│       └── project.md     # Cursor-specific additions
├── .github/
│   └── copilot-instructions.md  # Copilot-specific additions
└── ...
```

In tool-specific files, reference shared context:

```markdown
# Cursor Project Rules

See `AGENTS.md` for shared project context.

## Cursor-Specific Settings
[Cursor-only additions here]
```

---

## Context Sync Checklist

When updating project context:

- [ ] Update primary context file (CLAUDE.md or AGENTS.md)
- [ ] Sync key changes to tool-specific files
- [ ] Verify commands still work
- [ ] Check file paths are still valid
- [ ] Update tech stack versions if changed
- [ ] Add new design decisions or gotchas

---

## Security Considerations

### Do NOT include:

- API keys, secrets, or credentials
- Internal URLs or IP addresses
- Customer data or PII
- Security vulnerability details
- Production database connection strings

### Safe to include:

- Public documentation URLs
- Open source dependency names
- General architecture patterns
- Coding conventions and style guides

---

> **Tip**: Keep context files under 500 lines. Link to detailed docs rather than embedding everything. AI tools work better with focused, actionable context.
