---
name: claude-code-project-memory
description: Configure CLAUDE.md project memory files for persistent context, coding standards, architecture decisions, and team conventions. Reference for the 4-tier memory hierarchy, cross-platform AGENTS.md compatibility, and quick-add commands.
---

# Claude Code Project Memory — Meta Reference

This skill provides the definitive reference for configuring CLAUDE.md project memory. Use this when setting up project context that persists across sessions.

**Modern Best Practices (January 2026)**: Cross-platform documentation via AGENTS.md standard (supported by Codex, Cursor, Copilot, Gemini), symlink strategy for single-source-of-truth, hierarchical documentation for large codebases (100K-1M LOC), context packing tools (gitingest, repo2txt), and <300 line file size recommendation with @references for depth.

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

### /memory Command

Manage project memory files:

```bash
/memory           # Open memory file in system editor (for extensive edits)
/memory add "Always use TypeScript strict mode"   # Quick-add instruction
/memory show      # Display currently loaded memory files
```

**Editor mode**: Running `/memory` without arguments opens the memory file in your system editor (VS Code, Vim, etc.) for extensive multi-line editing. This is faster than adding instructions one-by-one.

**Verification**: Use `/memory show` to verify which rules are loaded, especially when using path-specific rules.

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

## Rules Directory

For larger projects, organize instructions into multiple files using `.claude/rules/`:

```text
project/
├── .claude/
│   ├── CLAUDE.md           # Main project memory
│   └── rules/              # Auto-loaded rule files
│       ├── code-style.md   # Coding standards
│       ├── testing.md      # Testing requirements
│       ├── security.md     # Security policies
│       └── workflows.md    # Team workflows
└── src/
```

**Key behavior**:

- All `.md` files in `.claude/rules/` are **automatically loaded** as project memory
- Same priority as `.claude/CLAUDE.md`
- Enables team collaboration (different members maintain different rule files)
- Better organization for complex projects
- Supports symlinks for sharing rules across projects

### Path-Specific Rules (Claude Code 2.0.64+)

Scope rules to specific files using YAML frontmatter with `paths:`:

```yaml
---
paths:
  - "src/api/**/*.ts"
  - "src/**/*.{ts,tsx}"
---

# API Development Rules

These rules only apply when working on API files.

- Use Zod for request validation
- Return RFC 7807 Problem Details for errors
- Document all endpoints with OpenAPI comments
```

**Important**: Quote glob patterns starting with `*` or `{`:

```yaml
# ❌ Wrong - YAML syntax error
paths:
  - **/*.ts

# ✅ Correct - quoted patterns
paths:
  - "**/*.ts"
  - "src/**/*.{ts,tsx}"
```

**Behavior**:

- Rules **without** `paths:` apply globally (loaded in every session)
- Rules **with** `paths:` only load when Claude works on matching files
- Run `/memory` to verify which rules are currently loaded

**Supported glob patterns**:

| Pattern | Matches |
|---------|---------|
| `"*.ts"` | TypeScript files in current dir |
| `"**/*.ts"` | TypeScript files recursively |
| `"src/**/*.{ts,tsx}"` | TS/TSX files under src/ |
| `"tests/**/*.test.ts"` | Test files under tests/ |

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

## Cross-Platform Compatibility (January 2026)

AGENTS.md is the cross-platform standard for AI coding assistants, now supported by **20+ tools**:

| Category | Tools |
|----------|-------|
| **AI Providers** | OpenAI Codex, GitHub Copilot, Google Jules, Gemini CLI |
| **IDEs & Editors** | Cursor, VS Code, Zed |
| **CLI Tools** | Aider, goose, opencode |
| **Platforms** | Factory, Amp, RooCode, Devin, Windsurf |
| **Enterprise** | Semgrep, Kilo Code, Phoenix, Ona, UiPath Autopilot |

**Claude Code still requires CLAUDE.md**. Use symlinks for single-source-of-truth.

### Option 1: New Project (Create Both from Scratch)

```bash
# 1. Create AGENTS.md as the single source of truth
cat > AGENTS.md << 'EOF'
# Project Name

Brief description.

## Quick Start

- Build: `npm run build`
- Test: `npm test`

## Architecture Overview

[3-5 sentences, link to ARCHITECTURE.md]

## Key Conventions

- [Convention 1]
- [Convention 2]

## Directory Structure

- `/src` - Source code
- `/tests` - Test files

@ARCHITECTURE.md
EOF

# 2. Create symlinks for each platform
ln -s AGENTS.md CLAUDE.md      # For Claude Code
ln -s AGENTS.md GEMINI.md      # For Gemini (optional)

# 3. Verify symlinks work
ls -la *.md
```

### Option 2: Existing CLAUDE.md (Migrate to Cross-Platform)

```bash
# 1. Rename existing CLAUDE.md to AGENTS.md
mv CLAUDE.md AGENTS.md

# 2. Create symlinks back
ln -s AGENTS.md CLAUDE.md
ln -s AGENTS.md GEMINI.md

# 3. Verify
cat CLAUDE.md  # Should show AGENTS.md content
```

### Option 3: Using Claude Code /init (Claude-First)

```bash
# 1. Let Claude Code generate CLAUDE.md
/init

# 2. Then migrate to cross-platform
mv CLAUDE.md AGENTS.md
ln -s AGENTS.md CLAUDE.md
```

### Platform Comparison

| Platform | Config File | Max Size | Loading Pattern |
|----------|-------------|----------|-----------------|
| Claude Code | CLAUDE.md | ~300 lines | Recursive up from cwd |
| Codex CLI | AGENTS.md | 32 KiB | Walk down from root |
| Cursor | AGENTS.md | Tool-dependent | Project-wide |
| Copilot | AGENTS.md | Tool-dependent | Project-wide |

### File Size Guidelines (January 2026)

| Platform | Limit | Recommendation |
|----------|-------|----------------|
| Claude Code | ~300 lines | Use `@references` for depth |
| Codex CLI | 32 KiB (`project_doc_max_bytes`) | Split across subdirectories |
| Cross-platform | Both limits | Keep main file lean, reference detailed docs |

**Sources**: [OpenAI AGENTS.md Guide](https://developers.openai.com/codex/guides/agents-md), [Anthropic Claude Code Best Practices](https://www.anthropic.com/engineering/claude-code-best-practices)

---

## Large Codebase Strategy (100K-1M LOC)

For large codebases, the key principle is: **LLMs don't need to remember everything—they need the right context at the right time**.

### Context Packing Tools

Before LLM sessions, extract relevant context using:

| Tool | Use Case | How to Use |
|------|----------|------------|
| **gitingest** | Quick codebase dump | Replace "github.com" with "gitingest.com" in URL |
| **repo2txt** | Selective extraction | Browser-based, choose specific files |
| **tree** | Structure overview | `tree -L 3 --dirsfirst -I 'node_modules\|.git\|dist'` |

### Hierarchical Documentation Pattern

```text
project-root/
├── AGENTS.md              # Main entry point (~300 lines max)
├── CLAUDE.md → AGENTS.md  # Symlink for Claude Code
├── DESIGN.md              # Features, requirements, goals
├── ARCHITECTURE.md        # Data structures, data flow, modules
│
├── api/
│   └── AGENTS.md          # API-specific conventions
├── frontend/
│   └── AGENTS.md          # Frontend patterns, components
├── services/
│   └── AGENTS.md          # Service boundaries, dependencies
└── docs/
    ├── adr/               # Architecture Decision Records
    └── runbooks/          # Operational procedures
```

### Working Strategy for Large Repos

1. **Scope tasks narrowly** — One function, one bug, one feature at a time
2. **Context pack** — Provide relevant files + AGENTS.md before each task
3. **Iterate in small steps** — Commit often, test thoroughly
4. **Update docs as you go** — Tell LLM to update AGENTS.md after changes while it has context

### Root File Template (Keep Under 300 Lines)

```markdown
# Project Name

Brief description (1-2 sentences).

## Quick Start

- Build: `npm run build`
- Test: `npm test`
- Lint: `npm run lint`

## Architecture Overview

[3-5 sentences max, link to ARCHITECTURE.md for details]

## Key Conventions

- [Convention 1]
- [Convention 2]
- [Convention 3]

## Directory Structure

- `/api` - REST endpoints, see api/AGENTS.md
- `/frontend` - React app, see frontend/AGENTS.md
- `/services` - Business logic, see services/AGENTS.md

## Domain Terms

- **Term1**: Definition
- **Term2**: Definition

@ARCHITECTURE.md
@docs/coding-standards.md
```

**Sources**: [Anthropic Claude Code Best Practices](https://www.anthropic.com/engineering/claude-code-best-practices), [OpenAI AGENTS.md Guide](https://developers.openai.com/codex/guides/agents-md)

---

## Best Practices

### DO

```markdown
## Good Memory Content

- Specific, actionable instructions
- Link to detailed docs: @docs/architecture.md
- Include examples where helpful
- Keep updated as project evolves
- Keep under 300 lines (use @references for depth)
- Update after completing features (while LLM has context)
```

### DON'T

```markdown
## Avoid

- Vague guidelines ("write good code")
- Outdated information
- Duplicate information from code comments
- Overly long documents (use @references)
- Feeding entire codebase to LLM (scope tasks narrowly)
```

### Performance Warnings

| Issue | Impact | Solution |
|-------|--------|----------|
| **Large CLAUDE.md files** | "Fading memory" — model accuracy degrades as file grows | Keep under 150 lines, use @references |
| **Waiting for context exhaustion** | Poor quality before `/compact` triggers | Run `/compact` proactively when Claude slows |
| **Loading unnecessary rules** | Wasted tokens on irrelevant context | Use path-specific rules with `paths:` frontmatter |
| **Generic instructions** | No value, wastes tokens | Only include project-specific instructions |

**Token optimization**: Memory files load at the start of every session. Each line costs tokens. Prioritize what's needed in every session; move the rest to `@` referenced files.

---

## File References

Use `@` to reference other files:

```markdown
## Architecture

See @docs/architecture.md for detailed diagrams.

## API Patterns

Follow patterns in @src/api/README.md.

## Shared Rules

Include @~/.claude/shared-rules.md for personal standards.
```

Claude loads referenced files as additional context.

### Import Constraints

| Constraint | Value |
|------------|-------|
| Max recursion depth | 5 hops (imports can chain up to 5 levels) |
| Code blocks | `@` imports inside code spans/blocks are ignored |
| Home directory | Use `~` for user home (e.g., `@~/.claude/rules.md`) |
| Relative paths | Resolved from the importing file's directory |

**Example of chained imports**:

```text
CLAUDE.md → @docs/standards.md → @docs/api/conventions.md → ...
   (1)            (2)                    (3)              (max 5)
```

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
- [references/memory-patterns.md](references/memory-patterns.md) — Common patterns
- [references/memory-examples.md](references/memory-examples.md) — Full examples
- [data/sources.json](data/sources.json) — Documentation links

**Related Skills**
- [../claude-code-skills/SKILL.md](../claude-code-skills/SKILL.md) — Skill creation
- [../claude-code-agents/SKILL.md](../claude-code-agents/SKILL.md) — Agent creation
- [../docs-codebase/SKILL.md](../docs-codebase/SKILL.md) — Documentation patterns
