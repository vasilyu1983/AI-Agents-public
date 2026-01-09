---
name: claude-code-commands
description: Create slash commands for Claude Code with $ARGUMENTS handling, agent invocation patterns, and template best practices. Reference for building user-triggered workflow shortcuts.
---

# Claude Code Commands — Meta Reference

This skill provides the definitive reference for creating Claude Code slash commands. Use this when building new commands or improving existing command patterns.

---

## When to Use This Skill

Use this skill when you need to:

- Create a new slash command for repeated workflows
- Add `$ARGUMENTS` handling to commands
- Invoke agents from commands
- Include file context or bash output in commands
- Organize commands for team sharing

---

## Quick Reference

| Component | Purpose | Example |
|-----------|---------|---------|
| Filename | Command name | `review.md` → `/review` |
| Content | Prompt template | Instructions for Claude |
| `$ARGUMENTS` | User input | `/review auth.js` → `$ARGUMENTS = "auth.js"` |
| `$1`, `$2` | Positional args | `/compare a.js b.js` → `$1 = "a.js"` |
| `@file` | Include file | `@CLAUDE.md` includes file contents |
| `!command` | Bash output | `!git status` includes command output |

## Command Locations

| Location | Scope | Use For |
|----------|-------|---------|
| `.claude/commands/` | Project | Team-shared commands (version control) |
| `~/.claude/commands/` | Personal | Cross-project commands (not shared) |

## Command Structure

```text
.claude/commands/
├── review.md           # /review
├── test.md             # /test
├── security-scan.md    # /security-scan
└── deploy.md           # /deploy
```

---

## Command Template

```markdown
---
description: Brief description for SlashCommand tool integration
---

# Command Title

[Clear instructions for what this command does]

User request: $ARGUMENTS

## Steps

1. [First action Claude should take]
2. [Second action]
3. [Third action]

## Output Format

[Specify expected output structure]
```

The `description:` frontmatter is required for the SlashCommand tool to reference the command.

---

## $ARGUMENTS Usage

### Single Argument

```markdown
# Code Review

Review the following file or code for quality, security, and best practices:

$ARGUMENTS

Focus on:
- Code quality issues
- Security vulnerabilities
- Performance concerns
- Best practice violations
```

**Usage**: `/review src/auth.js`

### Multiple Arguments

```markdown
# Compare Files

Compare these two files and explain the differences:

$ARGUMENTS

Provide:
- Line-by-line diff
- Semantic changes
- Impact analysis
```

**Usage**: `/compare old.js new.js`

### Optional Arguments

```markdown
# Run Tests

Run tests for the specified scope.

Scope: $ARGUMENTS

If no scope specified, run all tests.
If scope is a file, run tests for that file.
If scope is a directory, run tests in that directory.
```

**Usage**: `/test` or `/test auth/` or `/test login.test.ts`

### Positional Arguments

Use `$1`, `$2`, etc. for specific arguments (like shell scripts):

```markdown
# Compare Files

Compare $1 with $2.

Show:
- Line differences
- Semantic changes
- Which version is preferred
```

**Usage**: `/compare old.js new.js` → `$1 = "old.js"`, `$2 = "new.js"`

---

## File References (@ Prefix)

Include file contents directly in the command with `@`:

```markdown
# Review with Context

Review this code following our standards.

Project standards:
@CLAUDE.md

Code to review:
$ARGUMENTS
```

**Usage**: `/review-context src/auth.js` includes CLAUDE.md contents automatically.

---

## Bash Execution (! Prefix)

Include bash command output with `!`:

```markdown
# Smart Commit

Current status:
!git status --short

Recent commits:
!git log --oneline -5

Staged changes:
!git diff --cached

Generate a commit message for the staged changes.
```

**Usage**: `/smart-commit` runs git commands and includes their output.

---

## Command Patterns

### Agent Invocation

```markdown
# Security Audit

Perform a comprehensive security audit.

Target: $ARGUMENTS

Use the **security-auditor** agent to:
1. Scan for OWASP Top 10 vulnerabilities
2. Check authentication patterns
3. Review data validation
4. Analyze dependencies

Provide a severity-rated findings report.
```

### Multi-Agent Orchestration

```markdown
# Fullstack Feature

Build a complete fullstack feature.

Feature: $ARGUMENTS

Workflow:
1. Use **prd-architect** to clarify requirements
2. Use **system-architect** to design approach
3. Use **backend-engineer** for API implementation
4. Use **frontend-engineer** for UI implementation
5. Use **test-architect** for test coverage

Coordinate between agents and ensure integration.
```

### Validation Command

```markdown
# Pre-Commit Check

Validate changes before commit.

Files: $ARGUMENTS (or all staged files if not specified)

Checklist:
- [ ] All tests pass
- [ ] No linting errors
- [ ] No type errors
- [ ] No console.log statements
- [ ] No TODO comments
- [ ] No hardcoded secrets

Return READY or BLOCKED with details.
```

---

## Command Categories

### Development Commands

| Command | Purpose |
|---------|---------|
| `/review` | Code review |
| `/test` | Run/write tests |
| `/debug` | Debug issues |
| `/refactor` | Improve code |

### Architecture Commands

| Command | Purpose |
|---------|---------|
| `/design` | System design |
| `/architecture-review` | Review architecture |
| `/tech-spec` | Write tech spec |

### Security Commands

| Command | Purpose |
|---------|---------|
| `/security-scan` | Security audit |
| `/secrets-check` | Find exposed secrets |
| `/dependency-audit` | Check dependencies |

### Operations Commands

| Command | Purpose |
|---------|---------|
| `/deploy` | Deployment workflow |
| `/rollback` | Rollback changes |
| `/incident` | Incident response |

---

## Naming Conventions

| Pattern | Example | Use For |
|---------|---------|---------|
| `{action}` | `/review` | Simple actions |
| `{action}-{target}` | `/security-scan` | Specific targets |
| `{domain}-{action}` | `/pm-strategy` | Domain-prefixed |
| `{tool}-{action}` | `/git-commit` | Tool-specific |

---

## Command vs Agent vs Skill

| Feature | Command | Agent | Skill |
|---------|---------|-------|-------|
| **Trigger** | User types `/command` | Claude decides | Claude loads |
| **Purpose** | Quick shortcuts | Complex work | Knowledge |
| **Statefulness** | Stateless | Maintains context | Reference only |
| **Length** | Short prompt | Full instructions | Detailed docs |

**Flow**: User → Command → Agent → Skill

---

## Best Practices

### DO

```markdown
# Good Command

Clear, specific instructions.

Target: $ARGUMENTS

1. First, analyze the target
2. Then, perform action X
3. Finally, output result Y

Expected output:
- Summary of findings
- Actionable recommendations
```

### DON'T

```markdown
# Bad Command

Do stuff with $ARGUMENTS.

Make it good.
```

---

## Advanced Patterns

### Conditional Logic

```markdown
# Smart Review

Review target: $ARGUMENTS

If target is a PR number (e.g., #123):
  - Fetch PR details with `gh pr view`
  - Review all changed files

If target is a file path:
  - Review that specific file

If target is a directory:
  - Review all files in directory
```

### Template with Options

```markdown
# Generate Tests

Generate tests for: $ARGUMENTS

Options (parsed from arguments):
- `--unit` - Unit tests only
- `--e2e` - E2E tests only
- `--coverage` - Include coverage report

Default: Generate both unit and E2E tests.
```

---

## Navigation

### Resources

- [resources/command-patterns.md](resources/command-patterns.md) — Common patterns
- [resources/command-examples.md](resources/command-examples.md) — Full examples
- [data/sources.json](data/sources.json) — Documentation links

### Related Skills

- [../claude-code-agents/SKILL.md](../claude-code-agents/SKILL.md) — Agent creation
- [../claude-code-skills/SKILL.md](../claude-code-skills/SKILL.md) — Skill creation
- [../claude-code-hooks/SKILL.md](../claude-code-hooks/SKILL.md) — Hook automation
