# Tool Integration for Coding Agents

How to wrap development tools for agent use. Covers linters, formatters, test runners, type checkers, build tools, and git operations. Includes team-aware patterns and guidance on when Bash is sufficient vs when to build an MCP tool.

---

## Table of Contents

- [1. Tool Wrapping Principles](#1-tool-wrapping-principles)
- [2. Linter Integration](#2-linter-integration)
- [3. Formatter Integration](#3-formatter-integration)
- [4. Test Runner Integration](#4-test-runner-integration)
- [5. Type Checker Integration](#5-type-checker-integration)
- [6. Build Tool Integration](#6-build-tool-integration)
- [7. Git Operations](#7-git-operations)
- [8. Team-Aware Tool Patterns](#8-team-aware-tool-patterns)
- [9. When Bash Is Enough vs MCP](#9-when-bash-is-enough-vs-mcp)

---

## 1. Tool Wrapping Principles

Agents work best with tools that produce predictable, parseable output. Follow these principles when integrating any dev tool.

### Deterministic Output

Use flags that produce structured output (JSON, machine-readable text). Avoid tools that produce colored, paginated, or interactive output.

```bash
# Good: JSON output, parseable
npx eslint --format json src/
# Bad: default human-readable output with colors
npx eslint src/
```

### Structured Results

Parse tool output into a consistent shape the agent can reason about:

```
file: src/api/users.ts
line: 42
column: 5
severity: error
message: 'userId' is possibly undefined
rule: @typescript-eslint/no-unsafe-member-access
```

### Timeout Handling

Set timeouts for all tool invocations. A test suite that hangs will consume the agent's entire turn budget.

```bash
# Set a timeout to prevent hanging
timeout 60 npx jest --json --outputFile=results.json
```

### Avoid Interactive Tools

Agents cannot respond to prompts, confirmations, or interactive menus. Use `--yes`, `--no-interactive`, or equivalent flags. If a tool has no non-interactive mode, wrap it in a script that provides default answers.

---

## 2. Linter Integration

### ESLint (JavaScript/TypeScript)

```bash
npx eslint --format json src/ 2>/dev/null
```

JSON output structure per file:
```json
{
  "filePath": "src/api/users.ts",
  "messages": [
    {
      "ruleId": "no-unused-vars",
      "severity": 2,
      "message": "'userId' is defined but never used",
      "line": 15,
      "column": 7
    }
  ]
}
```

Severity mapping: 1 = warning, 2 = error.

### Ruff (Python)

```bash
ruff check --output-format json src/
```

JSON output per finding:
```json
{
  "code": "F841",
  "message": "Local variable `result` is assigned to but never used",
  "filename": "src/api/users.py",
  "location": {"row": 23, "column": 5}
}
```

### Common Linter Pattern for Agents

1. Run linter with JSON output on changed files
2. Parse JSON for file, line, severity, message
3. Fix the issues (for edit agents) or report them (for review agents)
4. Re-run linter to verify fixes did not introduce new issues

```
Agent workflow:
  1. npx eslint --format json <changed-files> > lint-results.json
  2. Read lint-results.json, parse findings
  3. Edit files to fix findings
  4. npx eslint --format json <changed-files> -- verify clean
```

---

## 3. Formatter Integration

### Check Mode First

Always run formatters in check mode before applying. This tells the agent which files need formatting without modifying them.

### Prettier (JavaScript/TypeScript/CSS/HTML)

```bash
# Check which files need formatting (exit code 1 if any do)
npx prettier --check "src/**/*.ts"

# Format specific files (only when the agent decides to format)
npx prettier --write src/api/users.ts
```

### Black (Python)

```bash
# Check mode: shows what would change
black --check --diff src/

# Format specific files
black src/api/users.py
```

### gofmt (Go)

```bash
# Check: list files that differ from gofmt style
gofmt -l src/

# Format: write formatted output
gofmt -w src/api/users.go
```

### Agent Formatting Principle

Only format files the agent modified. Running a formatter on untouched files creates noise in diffs and can conflict with other agents' work.

```
Agent rule: "After editing a file, run the formatter on that file only.
Do not format files you did not modify."
```

---

## 4. Test Runner Integration

### Run Specific Tests, Not Full Suites

Full test suites can take minutes and produce output that exceeds the token budget. Run only the tests relevant to the agent's work.

### Jest (JavaScript/TypeScript)

```bash
# Run specific test file
npx jest src/auth/validate.test.ts --no-coverage

# Run tests related to changed files
npx jest --findRelatedTests src/auth/validate.ts --no-coverage

# JSON output for parsing
npx jest --json --outputFile=test-results.json src/auth/
```

JSON output includes pass/fail per test with error messages and file:line for failures.

### pytest (Python)

```bash
# Run specific test file, short traceback
pytest tests/test_validate.py -x --tb=short -q

# Run tests matching a pattern
pytest -k "test_validate" --tb=short -q
```

The `-x` flag stops on first failure (saves tokens). `--tb=short` gives concise tracebacks. `-q` reduces output noise.

### Vitest

```bash
# Run specific file
npx vitest run src/auth/validate.test.ts

# JSON output
npx vitest run --reporter=json src/auth/
```

### Go test

```bash
# Run specific package tests
go test ./src/auth/ -v -count=1

# Run with short output
go test ./src/auth/ -short
```

### Parsing Test Failures

For every test failure, extract:
- File path and line number
- Test name
- Error message (expected vs actual)
- Stack trace (first 5 lines only -- deeper trace rarely helps)

```
Agent parses:
  FAIL src/auth/validate.test.ts:42
  Test: "validateToken returns null for expired token"
  Expected: null
  Received: { claims: { exp: 1234 } }
```

---

## 5. Type Checker Integration

### TypeScript (tsc)

```bash
# Check types without emitting files
npx tsc --noEmit

# Check specific files (if tsconfig supports it)
npx tsc --noEmit --project tsconfig.json
```

Output: file:line:column + error message. Parse for the same file:line:message structure used by linters.

### mypy (Python)

```bash
# Check specific files
mypy src/auth/validate.py --no-error-summary

# Check with strict mode
mypy src/auth/ --strict --no-error-summary
```

### Pyright (Python)

```bash
# Check specific directory
pyright src/auth/
```

### Incremental Type Checking

When the agent modifies files, run the type checker only on those files (when the tool supports it). Full project type checking is expensive and most findings will be unrelated to the agent's changes.

```
Agent workflow after editing src/auth/validate.ts:
  1. npx tsc --noEmit  (checks entire project, but fast with incremental)
  2. Parse output, filter to only errors in files the agent modified
  3. Fix type errors in modified files
  4. Re-run to verify
```

---

## 6. Build Tool Integration

### Purpose

Run the build after changes to catch compilation errors, missing imports, and configuration issues that type checkers alone may miss.

### npm/yarn/pnpm

```bash
# Build the project
npm run build 2>&1 | head -50

# If the build script is known:
npx tsc --build
npx next build
npx vite build
```

Limit output with `head` to prevent large build logs from consuming the token budget.

### Cargo (Rust)

```bash
cargo build 2>&1 | head -50
cargo check  # faster than build, checks without producing binary
```

### Go

```bash
go build ./... 2>&1 | head -50
go vet ./...  # static analysis checks
```

### Build Error Parsing

Build errors follow the same file:line:message pattern. Parse and fix iteratively:

```
Agent workflow:
  1. npm run build
  2. If build fails: parse error for file:line:message
  3. Read the file at that line
  4. Fix the error
  5. Re-build to verify
  6. Max 3 fix cycles, then report remaining errors
```

---

## 7. Git Operations

### Safe Subset for Coding Agents

These git commands are safe for agents to run without human approval:

| Command | Purpose | Safe? |
|---------|---------|-------|
| `git status` | See changed files | Yes |
| `git diff` | See changes | Yes |
| `git diff --staged` | See staged changes | Yes |
| `git log --oneline -20` | See recent commits | Yes |
| `git show <commit>` | See a specific commit | Yes |
| `git add <specific-files>` | Stage specific files | Yes |
| `git commit -m "<message>"` | Commit staged changes | Yes |
| `git stash` | Temporarily save changes | Yes |
| `git stash pop` | Restore saved changes | Yes |

### Dangerous Operations

These require human approval or should be excluded from the agent's tool set:

| Command | Risk | Recommendation |
|---------|------|----------------|
| `git push` | Publishes changes to remote | Require human approval |
| `git push --force` | Overwrites remote history | Exclude from agent tools |
| `git reset --hard` | Discards all uncommitted changes | Exclude or require approval |
| `git checkout -- .` | Discards all unstaged changes | Exclude or require approval |
| `git clean -fd` | Deletes untracked files permanently | Exclude from agent tools |
| `git rebase` | Rewrites commit history | Require human approval |

### Agent Git Workflow

For agents that commit (migration agents, refactoring agents with checkpoint patterns):

```bash
# Stage only the files the agent modified
git add src/auth/validate.ts src/auth/helpers.ts

# Commit with a descriptive message
git commit -m "[refactor] Extract parseTokenClaims from validateToken

Moved shared parsing logic to helpers.ts. All 24 tests pass."
```

Rules:
- Stage specific files, never `git add .` or `git add -A`
- Include test results in commit messages
- Use conventional commit prefixes when the repo follows that convention

---

## 8. Team-Aware Tool Patterns

When multiple agents work on the same codebase simultaneously.

### owned_files Enforcement

Each agent in a multi-agent team should only edit files in its assigned set. Enforce this in the system prompt and verify after execution.

```
System prompt:
"Your owned_files are: src/auth/validate.ts, src/auth/helpers.ts
You must NOT modify any file outside this list.
Before completing, run: git diff --name-only
Verify every changed file is in your owned_files list."
```

Post-execution verification:

```bash
# Check that only owned files were modified
git diff --name-only | while read f; do
  if [[ "$f" != "src/auth/validate.ts" && "$f" != "src/auth/helpers.ts" ]]; then
    echo "ERROR: Modified file outside owned_files: $f"
  fi
done
```

### Worktree-Scoped Bash

When agents use git worktrees for isolation, all Bash commands must run within the agent's worktree, not the main tree.

```bash
# Agent's worktree is at /tmp/worktrees/agent-1
cd /tmp/worktrees/agent-1 && npm test
cd /tmp/worktrees/agent-1 && npx eslint --format json src/auth/
```

The agent should never run commands in the main repository directory. Its system prompt should specify the worktree path.

### Shared MCP Servers

When multiple agents need access to the same external service (database, API, deployment platform), use a shared MCP server rather than giving each agent direct access.

```
Use case: 3 agents need to query a staging database
Without MCP: each agent runs psql commands directly (connection conflicts, no access control)
With MCP: one MCP server handles all DB queries, enforces read-only access, manages connections
```

MCP is warranted here because:
- Connection pooling prevents conflicts
- Access control is centralized
- Query results can be structured and token-efficient

---

## 9. When Bash Is Enough vs MCP

Most development tools work fine as Bash commands. Do not build an MCP tool when Bash suffices.

### Bash Is Enough When

- The tool has a CLI with structured output (JSON, machine-readable text)
- The tool is stateless (each invocation is independent)
- The tool runs quickly (under 30 seconds)
- The tool does not need shared state between agents

**Examples where Bash is sufficient:**

| Tool | Bash Command | MCP Needed? |
|------|-------------|-------------|
| ESLint | `npx eslint --format json src/` | No |
| pytest | `pytest --tb=short -q tests/` | No |
| tsc | `npx tsc --noEmit` | No |
| git status | `git status` | No |
| npm audit | `npm audit --json` | No |
| prettier | `npx prettier --check src/` | No |

### Build an MCP Tool When

**Stateful sessions**: The tool needs to maintain state across multiple calls. Example: a database connection that stays open for multiple queries, or a browser session for E2E testing.

**Large structured data**: The tool returns data that benefits from a typed interface. Example: a code analysis tool that returns a dependency graph as a structured object rather than text output.

**Shared access**: Multiple agents need coordinated access to the same resource. Example: a deployment service where agents must not deploy simultaneously.

**Complex input**: The tool requires structured input that is awkward to express as command-line arguments. Example: a code transformation tool that takes an AST pattern as input.

**Examples where MCP is warranted:**

| Scenario | Why MCP |
|----------|---------|
| Database queries across multiple agents | Connection pooling, read-only enforcement |
| Browser automation for E2E verification | Stateful session management |
| External API with rate limits | Centralized rate limiting, shared auth |
| Code analysis returning graph structures | Typed interface, efficient data transfer |

### Decision Checklist

```
[ ] Can I get the output I need from a single CLI command? -> Bash
[ ] Does the tool need to maintain state between calls? -> MCP
[ ] Do multiple agents need coordinated access? -> MCP
[ ] Is the output small enough for conversation context? -> Bash
[ ] Does the tool have a non-interactive CLI mode? -> Bash
[ ] All boxes point to Bash? -> Use Bash. Do not over-engineer.
```
