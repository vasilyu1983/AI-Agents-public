# Agent Tools Reference

Complete reference for tools available to Claude Code agents.

## Contents

- [Tool Categories](#tool-categories)
- [Read-Only Tools](#read-only-tools)
- [Code Modification Tools](#code-modification-tools)
- [Execution Tools](#execution-tools)
- [Web Tools](#web-tools)
- [Delegation Tools](#delegation-tools)
- [Tool Permission Patterns](#tool-permission-patterns)
- [Security Best Practices](#security-best-practices)
- [Tool Selection Checklist](#tool-selection-checklist)
- [Related](#related)

---

## Tool Categories

| Category | Tools | Use Case |
|----------|-------|----------|
| **Read-Only** | Read, Grep, Glob | Analysis, review, research |
| **Code Modification** | Edit, Write | Implementation, refactoring |
| **Execution** | Bash | Build, test, git, scripts |
| **Web** | WebFetch, WebSearch | Documentation, research |
| **Delegation** | Task | Spawn subagents |

---

## Read-Only Tools

### Read

**Purpose**: Read file contents.

```yaml
tools: Read
```

**Capabilities**:
- Read any file in workspace
- View images (PNG, JPG)
- Parse PDFs (text + visual)
- Read Jupyter notebooks

**Example Usage**:
```
Read src/auth/login.ts to understand authentication flow
```

**Always Include**: Yes, nearly all agents need this.

---

### Grep

**Purpose**: Search file contents using regex.

```yaml
tools: Grep
```

**Capabilities**:
- Regex pattern matching
- Filter by file type (`--type js`)
- Filter by glob (`--glob "*.tsx"`)
- Show context lines (`-A`, `-B`, `-C`)

**Example Usage**:
```
Search for "TODO|FIXME" in all TypeScript files
```

**Include When**: Code analysis, finding patterns, auditing.

---

### Glob

**Purpose**: Find files by name pattern.

```yaml
tools: Glob
```

**Capabilities**:
- Match file paths (`**/*.ts`)
- Sort by modification time
- Fast even in large codebases

**Example Usage**:
```
Find all test files: **/*.test.ts
```

**Include When**: File discovery, structure analysis.

---

## Code Modification Tools

### Edit

**Purpose**: Modify existing files with precise replacements.

```yaml
tools: Edit
```

**Capabilities**:
- Exact string replacement
- Preserve indentation
- `replace_all` for bulk changes

**Security Note**: Only grant to agents that need to modify code.

**Example Usage**:
```
Replace deprecated API call with new version
```

---

### Write

**Purpose**: Create new files or overwrite existing.

```yaml
tools: Write
```

**Capabilities**:
- Create new files
- Overwrite existing files
- Any file type

**Security Note**: Can overwrite critical files. Use sparingly.

**Example Usage**:
```
Create new component file src/components/Button.tsx
```

---

## Execution Tools

### Bash

**Purpose**: Run shell commands.

```yaml
tools: Bash
```

**Capabilities**:
- Run any shell command
- Build projects (`npm run build`)
- Run tests (`pytest`, `jest`)
- Git operations
- Package management

**Security Notes**:
- Runs with user permissions
- Can execute destructive commands
- Use sandbox mode when possible

**Common Commands**:
```bash
# Build
npm run build
cargo build

# Test
npm test
pytest

# Git
git status
git diff

# Lint
eslint src/
prettier --check .
```

**Include When**: Build, test, git, package management needed.

---

## Web Tools

### WebFetch

**Purpose**: Fetch and read web page content.

```yaml
tools: WebFetch
```

**Capabilities**:
- Fetch URL content
- Convert HTML to markdown
- Process with AI model
- 15-minute cache

**Example Usage**:
```
Fetch React documentation to understand hooks API
```

**Include When**: Need to read specific documentation pages.

---

### WebSearch

**Purpose**: Search the web.

```yaml
tools: WebSearch
```

**Capabilities**:
- Web search with query
- Domain filtering (allow/block)
- Returns search results with URLs

**Example Usage**:
```
Search for "TypeScript 5.0 new features"
```

**Include When**: Research, finding current information.

---

## Delegation Tools

### Task

**Purpose**: Spawn subagents for complex work.

```yaml
tools: Task
```

**Capabilities**:
- Launch specialized agents
- Pass prompts to subagents
- Receive results back
- Run multiple agents in parallel

**Example Usage**:
```
Delegate security review to security-auditor agent
Delegate API design to backend-engineer agent
```

**Include When**: Orchestrator agents that coordinate work.

---

## Tool Permission Patterns

### Read-Only Agent (Reviewers, Auditors)

```yaml
tools: Read, Grep, Glob
```

- Cannot modify code
- Cannot execute commands
- Safe for sensitive codebases

### Research Agent

```yaml
tools: Read, Grep, Glob, WebFetch, WebSearch
```

- Read-only code access
- Web access for documentation
- Cannot modify anything

### Implementation Agent

```yaml
tools: Read, Grep, Glob, Edit, Write, Bash
```

- Full code modification
- Can run builds and tests
- Use for trusted development tasks

### Orchestrator Agent

```yaml
tools: Read, Grep, Glob, Task
```

- Can spawn subagents
- Limited direct actions
- Delegates implementation

### Full-Access Agent (Use Sparingly)

```yaml
tools: Read, Grep, Glob, Edit, Write, Bash, WebFetch, WebSearch, Task
```

- All capabilities
- Only for trusted, complex workflows
- Consider splitting into specialized agents

---

## Security Best Practices

### Principle of Least Privilege

```yaml
# GOOD: Only what's needed
name: code-reviewer
tools: Read, Grep, Glob

# BAD: Everything "just in case"
name: code-reviewer
tools: Read, Write, Edit, Bash, WebSearch, Task
```

### Dangerous Command Awareness

Commands that should require confirmation:
- `rm -rf` — Recursive delete
- `git push --force` — Overwrite history
- `sudo` — Elevated permissions
- `DROP TABLE` — Database destruction
- Infrastructure changes

### Sandbox Mode

When possible, run in sandbox mode:
- Restricted filesystem access
- Network limitations
- Safer for untrusted operations

---

## Tool Selection Checklist

```text
TOOL SELECTION CHECKLIST

[ ] Does agent need to read files? → Read
[ ] Does agent need to search content? → Grep
[ ] Does agent need to find files? → Glob
[ ] Does agent need to modify code? → Edit
[ ] Does agent need to create files? → Write
[ ] Does agent need to run commands? → Bash
[ ] Does agent need web documentation? → WebFetch
[ ] Does agent need to search web? → WebSearch
[ ] Does agent need to delegate work? → Task

Start minimal, add tools only when needed.
```

---

## Related

- [agent-patterns.md](agent-patterns.md) — Agent design patterns
- [../SKILL.md](../SKILL.md) — Agent quick reference
