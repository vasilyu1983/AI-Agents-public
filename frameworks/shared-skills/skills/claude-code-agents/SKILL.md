---
name: claude-code-agents
description: Create and configure Claude Code agents with YAML frontmatter, tool selection, model specification, and naming conventions. Reference for building specialized AI subagents that handle complex, multi-step tasks.
---

# Claude Code Agents — Meta Reference

This skill provides the definitive reference for creating Claude Code agents. Use this when building new agents or understanding agent architecture.

---

## Quick Reference

| Field | Purpose | Required |
|-------|---------|----------|
| `name` | Agent identifier (kebab-case) | Yes |
| `description` | When to invoke this agent | Yes |
| `tools` | Allowed tool list | No (defaults: all) |
| `model` | Claude model variant | No (default: sonnet) |

## Agent Structure

```text
.claude/agents/
├── code-reviewer.md
├── security-auditor.md
├── test-architect.md
└── system-architect.md
```

---

## Agent Template

```markdown
---
name: agent-name
description: When to use this agent (single line)
tools: Read, Grep, Glob, Bash
model: sonnet
---

# Agent Name

You are a [role description].

## Responsibilities

- Responsibility 1
- Responsibility 2
- Responsibility 3

## Workflow

1. Step 1: [action]
2. Step 2: [action]
3. Step 3: [action]

## Output Format

[Specify expected output structure]
```

---

## Frontmatter Specification

### name (required)

```yaml
name: security-auditor
```

**Rules**:
- Kebab-case only
- Match filename (without .md)
- Descriptive but concise

### description (required)

```yaml
description: Analyze code for security vulnerabilities using OWASP Top 10
```

**Rules**:
- Single line, under 200 characters
- Explain WHEN Claude should invoke this agent
- Include key capabilities

### tools (optional)

```yaml
tools: Read, Grep, Glob, Bash, Edit, Write
```

**Available tools**:
| Tool | Purpose | Use When |
|------|---------|----------|
| `Read` | Read files | Always include |
| `Grep` | Search content | Code analysis |
| `Glob` | Find files | File discovery |
| `Bash` | Run commands | Build, test, git |
| `Edit` | Modify files | Code changes |
| `Write` | Create files | New files |
| `WebFetch` | Fetch URLs | Documentation lookup |
| `WebSearch` | Search web | Research tasks |
| `Task` | Spawn subagents | Delegation |

**Minimal permissions principle**: Only include tools the agent needs.

### model (optional)

```yaml
model: sonnet  # or opus, haiku
```

| Model | Use For | Cost |
|-------|---------|------|
| `haiku` | Simple, fast tasks | Low |
| `sonnet` | Most tasks (default) | Medium |
| `opus` | Complex reasoning | High |

---

## Agent Categories

### Analysis Agents (Read-only)

```yaml
tools: Read, Grep, Glob
```

Examples:
- `code-reviewer` - Review code quality
- `security-auditor` - Find vulnerabilities
- `architecture-analyzer` - Analyze system design

### Implementation Agents (Read-write)

```yaml
tools: Read, Grep, Glob, Edit, Write, Bash
```

Examples:
- `backend-engineer` - Build APIs
- `frontend-engineer` - Build UIs
- `test-engineer` - Write tests

### Research Agents (Web access)

```yaml
tools: Read, WebFetch, WebSearch
```

Examples:
- `documentation-researcher` - Find docs
- `technology-scout` - Evaluate options

---

## Agent Design Patterns

### Single-Responsibility Agent

```markdown
---
name: sql-optimizer
description: Analyze and optimize SQL queries for performance
tools: Read, Grep, Glob
model: sonnet
---

# SQL Optimizer

You optimize SQL queries. Focus on:

1. Index usage analysis
2. Query plan examination
3. Performance recommendations

Output optimization suggestions with before/after examples.
```

### Orchestrator Agent

```markdown
---
name: fullstack-builder
description: Coordinate frontend, backend, and database changes
tools: Read, Grep, Glob, Task
model: sonnet
---

# Fullstack Builder

You coordinate multi-layer changes by delegating to specialized agents:

1. Analyze requirements
2. Delegate database changes to sql-engineer
3. Delegate API changes to backend-engineer
4. Delegate UI changes to frontend-engineer
5. Verify integration
```

### Verification Agent

```markdown
---
name: pre-commit-checker
description: Verify code quality before commits
tools: Read, Grep, Bash
model: haiku
---

# Pre-Commit Checker

Run quality checks:
- [ ] Linting passes
- [ ] Tests pass
- [ ] No console.logs
- [ ] No TODO comments
- [ ] Types correct

Return PASS or FAIL with details.
```

---

## Agent ↔ Skill Relationship

**Agents** do work → **Skills** provide knowledge

```text
Agent: backend-engineer
  ├── Uses skill: software-backend (API patterns)
  ├── Uses skill: dev-api-design (REST/GraphQL)
  └── Uses skill: data-sql-optimization (query optimization)
```

Agents reference skills implicitly—Claude loads relevant skill content based on context.

---

## Naming Conventions

| Pattern | Example | Use For |
|---------|---------|---------|
| `{role}` | `code-reviewer` | General role |
| `{domain}-{role}` | `security-auditor` | Domain-specific |
| `{action}-{target}` | `test-generator` | Action-focused |
| `{tech}-{role}` | `typescript-migrator` | Tech-specific |

---

## Invocation Patterns

### Direct (user triggers)

```
User: "Review this code for security issues"
Claude: [invokes security-auditor agent]
```

### Via Command

```markdown
<!-- .claude/commands/security.md -->
Run security analysis using the security-auditor agent.
```

### Via Another Agent

```yaml
# Parent agent
tools: Task  # Can spawn subagents
```

---

## Quality Checklist

```text
AGENT VALIDATION CHECKLIST

Frontmatter:
[ ] name matches filename (kebab-case)
[ ] description explains when to invoke
[ ] tools are minimal necessary
[ ] model appropriate for task complexity

Content:
[ ] Clear role definition
[ ] Specific responsibilities listed
[ ] Workflow steps defined
[ ] Output format specified

Integration:
[ ] Related skills identified
[ ] Commands reference this agent (if applicable)
```

---

## Security Best Practices

### Deny-All Default

Start with no tools, add only what's needed:

```yaml
# Reviewer: read-only
tools: Read, Grep, Glob

# Builder: add write access
tools: Read, Grep, Glob, Edit, Write, Bash
```

### Dangerous Command Awareness

Require explicit confirmation for:
- `rm -rf` — Recursive delete
- `git push --force` — Overwrite history
- `sudo` — Elevated permissions
- `DROP TABLE` — Database destruction
- Infrastructure changes (Terraform, K8s)

### Context Isolation

- Each subagent has isolated context window
- Orchestrator maintains global state (compact)
- Use CLAUDE.md for shared conventions
- Never pass full codebase to subagents

---

## Navigation

**Resources**
- [resources/agent-patterns.md](resources/agent-patterns.md) — Common agent patterns
- [resources/agent-tools.md](resources/agent-tools.md) — Tool capabilities reference
- [data/sources.json](data/sources.json) — Official documentation links

**Related Skills**
- [../claude-code-skills/SKILL.md](../claude-code-skills/SKILL.md) — Skill creation
- [../claude-code-commands/SKILL.md](../claude-code-commands/SKILL.md) — Command creation
- [../claude-code-hooks/SKILL.md](../claude-code-hooks/SKILL.md) — Hook automation
