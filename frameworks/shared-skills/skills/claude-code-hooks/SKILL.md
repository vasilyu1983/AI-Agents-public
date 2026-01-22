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
| `PermissionRequest` | Permission dialog shown | Auto-allow/deny permissions |
| `Stop` | When Claude finishes | Run tests, summarize |
| `SubagentStop` | Subagent finishes | Verify subagent completion |
| `Notification` | On notifications | Alert integrations |
| `SessionStart` | Session begins | Initialize environment |
| `SessionEnd` | Session ends | Cleanup, save state |
| `UserPromptSubmit` | User sends message | Preprocessing |
| `PreCompact` | Before context compaction | Preserve critical context |

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
| `2` | Block | Block tool execution (PreToolUse/SubagentStop) |

---

## Input Modification (v2.0.10+)

PreToolUse hooks can modify tool inputs instead of blocking. This enables transparent corrections without error messages or retries.

### Hook Output Schema

```json
{
  "decision": "approve",
  "updatedInput": { "command": "echo 'modified'" },
  "additionalContext": "Hook added safety check"
}
```

| Field | Description |
|-------|-------------|
| `decision` | "approve", "block", or "ask" |
| `updatedInput` | Modified tool input JSON |
| `additionalContext` | Context returned to model (Jan 2026) |

### Example: Redirect Sensitive File Edits

```bash
#!/bin/bash
set -euo pipefail

INPUT=$(cat)
FILE=$(echo "$INPUT" | jq -r '.tool_input.file_path // empty')

# Redirect package-lock.json edits to /dev/null
if [[ "$FILE" == *"package-lock.json" ]]; then
  MODIFIED=$(echo "$INPUT" | jq '.tool_input.file_path = "/dev/null"')
  echo "{\"decision\": \"approve\", \"updatedInput\": $MODIFIED}"
  exit 0
fi

echo '{"decision": "approve"}'
```

### Example: Strip Sensitive Files from Git Add

```bash
#!/bin/bash
set -euo pipefail

INPUT=$(cat)
TOOL=$(echo "$INPUT" | jq -r '.tool_name')
CMD=$(echo "$INPUT" | jq -r '.tool_input.command // empty')

if [[ "$TOOL" == "Bash" && "$CMD" =~ ^git\ add ]]; then
  # Remove .env files from staging
  SAFE_CMD=$(echo "$CMD" | sed 's/\.env[^ ]*//g')
  if [[ "$SAFE_CMD" != "$CMD" ]]; then
    MODIFIED=$(echo "$INPUT" | jq --arg cmd "$SAFE_CMD" '.tool_input.command = $cmd')
    echo "{\"decision\": \"approve\", \"updatedInput\": $MODIFIED}"
    exit 0
  fi
fi

echo '{"decision": "approve"}'
```

---

## Prompt-Based Hooks

For complex decisions, use LLM-evaluated hooks (`type: "prompt"`) instead of bash scripts.

### Supported Events

| Event | Prompt Hooks | Use Case |
|-------|--------------|----------|
| `Stop` | ✅ | Verify task completion |
| `SubagentStop` | ✅ | Validate subagent work |
| `PreToolUse` | ❌ | Use command hooks |
| `PostToolUse` | ❌ | Use command hooks |

### Configuration

```json
{
  "hooks": {
    "Stop": [
      {
        "hooks": [
          {
            "type": "prompt",
            "prompt": "Check if all user tasks are complete. Return approve if done, block if work remains.",
            "timeout": 30
          }
        ]
      }
    ]
  }
}
```

### Response Fields

| Field | Description |
|-------|-------------|
| `decision` | "approve" or "block" |
| `reason` | Explanation for decision |
| `stopReason` | Custom stop message |
| `systemMessage` | Warning shown to user |
| `continue` | Set false to stop Claude entirely |

### Combining Command and Prompt Hooks

Use command hooks for fast, deterministic checks. Use prompt hooks for nuanced decisions:

```json
{
  "Stop": [
    {
      "hooks": [
        { "type": "command", "command": ".claude/hooks/quick-check.sh" },
        { "type": "prompt", "prompt": "Verify code quality meets standards" }
      ]
    }
  ]
}
```

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

- [references/hook-patterns.md](references/hook-patterns.md) — Common patterns
- [references/hook-security.md](references/hook-security.md) — Security guide
- [data/sources.json](data/sources.json) — Documentation links

### Related Skills

- [../claude-code-commands/SKILL.md](../claude-code-commands/SKILL.md) — Command creation
- [../claude-code-agents/SKILL.md](../claude-code-agents/SKILL.md) — Agent creation
- [../ops-devops-platform/SKILL.md](../ops-devops-platform/SKILL.md) — CI/CD integration
