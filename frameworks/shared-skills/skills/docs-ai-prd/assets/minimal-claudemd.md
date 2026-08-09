# Minimal CLAUDE.md Template

Quick-start template for project context. Fill in the sections below.

---

```markdown
# [Project Name]

[One sentence describing what this project does]

## Tech Stack

- **Language**: [e.g., TypeScript 5.x]
- **Framework**: [e.g., Next.js 16, Express, FastAPI]
- **Database**: [e.g., PostgreSQL, MongoDB]
- **Key deps**: [list 3-5 main libraries]

## Architecture

[2-3 sentences describing the high-level design]

### Key Directories

```
src/
├── api/          # HTTP handlers
├── services/     # Business logic
├── models/       # Data models
├── utils/        # Shared utilities
└── config/       # Configuration
```

## Conventions

### Naming
- Files: `kebab-case.ts`
- Functions: `camelCase()`
- Classes: `PascalCase`

### Patterns
- [List 2-3 key patterns used, e.g., "Repository pattern for data access"]

## Key Files

| Purpose | Location |
|---------|----------|
| Entry point | `src/index.ts` |
| Config | `src/config/index.ts` |
| Routes | `src/api/routes.ts` |

## Commands

```bash
npm run dev      # Development
npm run test     # Tests
npm run build    # Production build
```

## Important Context

### Gotchas
- [List any non-obvious behaviors]
- [Known issues or workarounds]

### Recent Changes
- [Any recent significant changes AI should know about]
```

---

## Usage

1. Copy the template above
2. Replace bracketed placeholders with your project info
3. Add to project root as `CLAUDE.md` or `.claude/CLAUDE.md`
4. Update as project evolves

## Expansion

For more comprehensive context, add:

- **Dependencies section** - external services, APIs
- **Tribal knowledge** - why decisions were made
- **Testing patterns** - how tests are organized
- **Deployment info** - environments, CI/CD
- **AI-specific guidance** - patterns to follow/avoid
