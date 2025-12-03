---
name: claude-code-hooks
description: Create event-driven hooks for Claude Code automation. Configure PreToolUse, PostToolUse, Stop, and other hook events with bash scripts, environment variables, matchers, and exit codes.
---

# Claude Code Hooks — Meta Reference

This skill provides the definitive reference for creating Claude Code hooks. Use this when building automation that triggers on Claude Code events.

---

## When to Use This Skill

- Building event-driven automation for Claude Code
- Creating PreToolUse guards to block dangerous commands
- Implementing PostToolUse formatters, linters, or auditors
- Adding Stop hooks for testing or notifications
- Setting up SessionStart/SessionEnd for environment management
- Integrating Claude Code with CI/CD pipelines (headless mode)

---

## Quick Reference

| Event | Trigger | Use Case |
|-------|---------|----------|
| `PreToolUse` | Before tool execution | Validate, block dangerous commands |
| `PostToolUse` | After tool execution | Format, audit, notify |
| `Stop` | When Claude finishes | Run tests, summarize |
| `Notification` | On notifications | Alert integrations |
| `SessionStart` | Session begins | Initialize environment |
| `SessionEnd` | Session ends | Cleanup, save state |
| `UserPromptSubmit` | User sends message | Preprocessing |

## Hook Structure

```text
.claude/hooks/
├── pre-tool-validate.sh
├── post-tool-format.sh
├── post-tool-audit.sh
├── stop-run-tests.sh
└── session-start-init.sh
```

---

## Configuration

### settings.json

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/post-tool-format.sh"
          }
        ]
      }
    ],
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/pre-tool-validate.sh"
          }
        ]
      }
    ],
    "Stop": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/stop-run-tests.sh"
          }
        ]
      }
    ]
  }
}
```

---

## Environment Variables

| Variable | Description | Available In |
|----------|-------------|--------------|
| `CLAUDE_PROJECT_DIR` | Project root path | All hooks |
| `CLAUDE_TOOL_NAME` | Current tool name | Pre/PostToolUse |
| `CLAUDE_TOOL_INPUT` | Tool input (JSON) | PreToolUse |
| `CLAUDE_TOOL_OUTPUT` | Tool output | PostToolUse |
| `CLAUDE_FILE_PATHS` | Affected files | PostToolUse |
| `CLAUDE_SESSION_ID` | Session identifier | All hooks |

---

## Exit Codes

| Code | Meaning | Effect |
|------|---------|--------|
| `0` | Success | Continue execution |
| `1` | Error | Report error, continue |
| `2` | Block | Block tool execution (PreToolUse only) |

---

## Hook Templates

### Pre-Tool Validation

```bash
#!/bin/bash
set -euo pipefail

# Block dangerous commands
if [[ "$CLAUDE_TOOL_NAME" == "Bash" ]]; then
  INPUT="$CLAUDE_TOOL_INPUT"

  # Block rm -rf /
  if echo "$INPUT" | grep -qE 'rm\s+-rf\s+/'; then
    echo "BLOCKED: Dangerous rm command detected"
    exit 2
  fi

  # Block force push to main
  if echo "$INPUT" | grep -qE 'git\s+push.*--force.*(main|master)'; then
    echo "BLOCKED: Force push to main/master not allowed"
    exit 2
  fi

  # Block credential exposure
  if echo "$INPUT" | grep -qE '(password|secret|api_key)\s*='; then
    echo "WARNING: Possible credential exposure"
  fi
fi

exit 0
```

### Post-Tool Formatting

```bash
#!/bin/bash
set -euo pipefail

# Auto-format modified files
if [[ "$CLAUDE_TOOL_NAME" =~ ^(Edit|Write)$ ]]; then
  FILES="$CLAUDE_FILE_PATHS"

  for file in $FILES; do
    if [[ -f "$file" ]]; then
      case "$file" in
        *.js|*.ts|*.jsx|*.tsx|*.json|*.md)
          npx prettier --write "$file" 2>/dev/null || true
          ;;
        *.py)
          ruff format "$file" 2>/dev/null || true
          ;;
        *.go)
          gofmt -w "$file" 2>/dev/null || true
          ;;
        *.rs)
          rustfmt "$file" 2>/dev/null || true
          ;;
      esac
    fi
  done
fi

exit 0
```

### Post-Tool Security Audit

```bash
#!/bin/bash
set -euo pipefail

# Audit file changes for security issues
if [[ "$CLAUDE_TOOL_NAME" =~ ^(Edit|Write)$ ]]; then
  FILES="$CLAUDE_FILE_PATHS"

  for file in $FILES; do
    if [[ -f "$file" ]]; then
      # Check for hardcoded secrets
      if grep -qE '(password|secret|api_key|token)\s*[:=]\s*["\x27][^"\x27]+["\x27]' "$file"; then
        echo "WARNING: Possible hardcoded secret in $file"
      fi

      # Check for console.log in production code
      if [[ "$file" =~ \.(ts|js|tsx|jsx)$ ]] && grep -q 'console.log' "$file"; then
        echo "NOTE: console.log found in $file"
      fi
    fi
  done
fi

exit 0
```

### Stop Hook (Run Tests)

```bash
#!/bin/bash
set -euo pipefail

# Run tests after Claude finishes
cd "$CLAUDE_PROJECT_DIR"

# Detect test framework
if [[ -f "package.json" ]]; then
  if grep -q '"vitest"' package.json; then
    npm run test 2>&1 | head -50
  elif grep -q '"jest"' package.json; then
    npm test 2>&1 | head -50
  fi
elif [[ -f "pytest.ini" ]] || [[ -f "pyproject.toml" ]]; then
  pytest --tb=short 2>&1 | head -50
fi

exit 0
```

### Session Start

```bash
#!/bin/bash
set -euo pipefail

cd "$CLAUDE_PROJECT_DIR"

# Check git status
echo "=== Git Status ==="
git status --short

# Check for uncommitted changes
if ! git diff --quiet; then
  echo "WARNING: Uncommitted changes detected"
fi

# Verify dependencies
if [[ -f "package.json" ]]; then
  if [[ ! -d "node_modules" ]]; then
    echo "NOTE: node_modules missing, run npm install"
  fi
fi

exit 0
```

---

## Matchers

Matchers filter which tool triggers the hook:

| Matcher | Matches |
|---------|---------|
| `""` (empty) | All tools |
| `"Bash"` | Bash tool only |
| `"Edit\|Write"` | Edit OR Write |
| `"Edit.*"` | Edit and variants (regex) |

---

## Security Best Practices

```text
HOOK SECURITY CHECKLIST

[ ] Validate all inputs with regex
[ ] Quote all variables: "$VAR" not $VAR
[ ] Use absolute paths
[ ] No eval with untrusted input
[ ] Set -euo pipefail at top
[ ] Keep hooks fast (<1 second)
[ ] Log actions for audit
[ ] Test manually before deploying
```

---

## Hook Composition

### Multiple Hooks on Same Event

```json
{
  "PostToolUse": [
    {
      "matcher": "Edit|Write",
      "hooks": [
        { "type": "command", "command": ".claude/hooks/format.sh" },
        { "type": "command", "command": ".claude/hooks/audit.sh" },
        { "type": "command", "command": ".claude/hooks/notify.sh" }
      ]
    }
  ]
}
```

Hooks execute in order. If one fails, subsequent hooks may not run.

---

## Debugging Hooks

```bash
# Test hook manually
CLAUDE_TOOL_NAME="Edit" \
CLAUDE_FILE_PATHS="src/app.ts" \
CLAUDE_PROJECT_DIR="$(pwd)" \
bash .claude/hooks/post-tool-format.sh

# Check exit code
echo $?
```

---

## Navigation

### Resources

- [resources/hook-patterns.md](resources/hook-patterns.md) — Common patterns
- [resources/hook-security.md](resources/hook-security.md) — Security guide
- [data/sources.json](data/sources.json) — Documentation links

### Related Skills

- [../claude-code-commands/SKILL.md](../claude-code-commands/SKILL.md) — Command creation
- [../claude-code-agents/SKILL.md](../claude-code-agents/SKILL.md) — Agent creation
- [../ops-devops-platform/SKILL.md](../ops-devops-platform/SKILL.md) — CI/CD integration
