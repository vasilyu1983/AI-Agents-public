# Claude Code Kit

**Last Updated**: 2026-01-28
**Official Documentation**: [Claude Code Overview](https://code.claude.com/docs/en/overview)
**Skills Format**: [Agent Skills Specification](https://agentskills.io/specification)
**Status**: PORTABLE - Works for any repository

Production-ready Claude Code setup with 92 skills + 3 hooks.

**Skills**: 92 skills in `frameworks/shared-skills/` (shared with Codex Kit)

**v3.9** (2026-01-28): Simplified to skills-only architecture. Removed agents (skills provide knowledge directly). Reduced to 3 essential hooks.

---

## What is Claude Code?

Claude Code is Anthropic's official CLI tool for AI-assisted software development. Key features:

1. **Skills** - Knowledge bases with progressive disclosure (includes slash commands)
2. **Hooks** - Event-driven bash automation
3. **CLAUDE.md** - Project memory and instructions
4. **MCP** - External data source integration

For detailed documentation on each feature, see the corresponding skills:
- Skills → [agents-skills](../shared-skills/skills/agents-skills/SKILL.md)
- Hooks → [agents-hooks](../shared-skills/skills/agents-hooks/SKILL.md)
- CLAUDE.md → [agents-project-memory](../shared-skills/skills/agents-project-memory/SKILL.md)
- MCP → [agents-mcp](../shared-skills/skills/agents-mcp/SKILL.md)

---

## Quick Start

### 5-Minute Setup

```bash
cd your-project/

# Create .claude directories
mkdir -p .claude/{skills,hooks}

# Copy hooks
cp frameworks/claude-code-kit/framework/hooks/*.sh .claude/hooks/
chmod +x .claude/hooks/*.sh

# Copy settings
cp frameworks/claude-code-kit/framework/example-settings.json .claude/settings.json
cp frameworks/claude-code-kit/framework/example-settings.local.json .claude/settings.local.json

# Copy skills from shared source
cp -r frameworks/shared-skills/skills/* .claude/skills/
```

### Verify Installation

```bash
ls .claude/skills/ | wc -l      # Should show 92
ls -l .claude/hooks/*.sh        # Should show 3 executable files
```

---

## What's Included

| Component | Count | Source |
|-----------|-------|--------|
| **Skills** | 92 | `shared-skills/skills/` |
| **Hooks** | 3 | `framework/hooks/` |

### Hooks

| Hook | Event | Purpose |
|------|-------|---------|
| `pre-tool-validate.sh` | PreToolUse | Security - blocks `rm -rf`, `sudo`, force-push |
| `post-tool-format.sh` | PostToolUse | Auto-format code (Prettier, Black, gofmt) |
| `stop-run-tests.sh` | Stop | Run tests when Claude finishes |

### Router Architecture

Intelligent skill orchestration across 92 skills through domain-specific routers:

| Router | Skills | Domain |
|--------|--------|--------|
| [router-main](../shared-skills/skills/router-main/SKILL.md) | — | Universal entry point |
| [router-startup](../shared-skills/skills/router-startup/SKILL.md) | 30 | Startup, marketing, documents, product |
| [router-engineering](../shared-skills/skills/router-engineering/SKILL.md) | 32 | AI/ML, software, data, dev tools, Claude Code |
| [router-operations](../shared-skills/skills/router-operations/SKILL.md) | 18 | QA, DevOps, git, documentation |
| [router-qa](../shared-skills/skills/router-qa/SKILL.md) | 12 | Testing, debugging, observability |

See [INDEX.md](../shared-skills/skills/INDEX.md) for the complete skill catalog.

---

## Core Concepts

### Skills - Knowledge + Slash Commands

Skills provide domain knowledge and can work as slash commands:

```text
You: "Design a REST API"
Claude: [Consults software-backend skill automatically]

You: "/review auth.js"
Claude: [Invokes review skill as slash command]
```

### Hooks - Event Automation

Hooks run automatically on events:

```text
PreToolUse: Block dangerous commands (rm -rf, sudo)
PostToolUse: Auto-format files after editing
Stop: Run tests when Claude finishes
```

### CLAUDE.md - Project Memory

Project-specific instructions:

```markdown
# Project: E-commerce Platform

## Architecture
Node.js microservices...

## Code Standards
- TypeScript strict mode
- 80% test coverage required
```

---

## Example Usage

```text
You: "Use the startup-idea-validation skill to validate my AI writing assistant"
Claude: [Runs 9-dimension validation with GO/NO-GO recommendation]

You: "Use software-backend to design a REST API for task management"
Claude: [Generates backend with Prisma schema, auth, tests, deployment]

You: "Use software-frontend to create a dashboard with data table"
Claude: [Creates Next.js components with TypeScript, Tailwind, accessibility]

You: "Use data-sql-optimization to optimize this slow query"
Claude: [Analyzes query, suggests indexes, shows improvement]
```

---

## Create a Skill

See [agents-skills](../shared-skills/skills/agents-skills/SKILL.md) for the complete guide.

```text
.claude/skills/
└── skill-name/
    ├── SKILL.md           # Main reference (required)
    ├── references/        # Detailed docs
    └── data/sources.json  # Curated URLs
```

```markdown
---
name: skill-name
description: What this provides
---

# Skill Name

High-level concepts...

See `references/` for details.
```

### Create a Slash Command (via Skill)

Skills with `disable-model-invocation: true` work as slash commands:

```markdown
---
name: my-command
description: What this command does
disable-model-invocation: true
---

# My Command

Instructions for: $ARGUMENTS
```

**Usage**: `/my-command some arguments`

---

## Best Practices

### Skill Creation

Per [agentskills.io/specification](https://agentskills.io/specification):

**DO**:
- Keep SKILL.md under 500 lines (<5000 tokens)
- Use `references/` for detailed content (progressive disclosure)
- Include practical code examples

**DON'T**:
- Put everything in SKILL.md
- Create overlapping skills

### Hook Development

**DO**:
- Validate all inputs with regex
- Quote variables properly
- Keep hooks fast (<1 second)

**DON'T**:
- Use `eval` with user input
- Trust unvalidated file paths

---

## Security

1. **Hooks run with your user permissions** - No sandboxing
2. **Validate all hook inputs** - Prevent injection attacks
3. **Use environment variables** - Never hardcode credentials

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Skill not accessible | Verify `SKILL.md` exists, check frontmatter |
| Slash command not found | Check skill has `name:` in frontmatter |
| Hook not running | Make executable: `chmod +x .claude/hooks/*.sh` |

---

## Official Resources

- **[Agent Skills Specification](https://agentskills.io/specification)** - Format spec
- **[Claude Code Overview](https://code.claude.com/docs/en/overview)** - Official docs
- **[Skills](https://code.claude.com/docs/en/skills)** - Skills documentation
- **[Hooks](https://code.claude.com/docs/en/hooks)** - Hooks documentation
- **[Best Practices](https://www.anthropic.com/engineering/claude-code-best-practices)** - Official best practices

---

## Quick Links

**Skills Reference**: [INDEX.md](../shared-skills/skills/INDEX.md)

**Claude Code Skills**:
- [agents-skills](../shared-skills/skills/agents-skills/SKILL.md) - Creating skills
- [agents-hooks](../shared-skills/skills/agents-hooks/SKILL.md) - Event automation
- [agents-mcp](../shared-skills/skills/agents-mcp/SKILL.md) - External data
- [agents-project-memory](../shared-skills/skills/agents-project-memory/SKILL.md) - CLAUDE.md

**Official**: [Claude Code Docs](https://docs.claude.com/en/docs/claude-code/overview) | [Agent Skills Spec](https://agentskills.io/specification)
