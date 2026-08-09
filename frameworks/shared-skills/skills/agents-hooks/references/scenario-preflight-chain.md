# Scenario: Preflight Chain — PreToolUse + PostToolUse + PreCompact

A self-contained end-to-end example showing three hooks composed together. Copy these snippets into your `.claude/settings.json` hooks block, then run any write-file or bash command to observe the chain in action.

## Table of Contents

- [What This Scenario Does](#what-this-scenario-does)
- [Directory Layout](#directory-layout)
- [lib.sh — Shared Helpers](#libsh--shared-helpers)
- [preflight-guard.sh — PreToolUse](#preflight-guardsh--pretooluse)
- [post-audit.sh — PostToolUse](#post-auditsh--posttooluse)
- [pre-compact-state.sh — PreCompact](#pre-compact-statesh--precompact)
- [settings.json — Hook Wiring](#settingsjson--hook-wiring)
- [Expected Behavior](#expected-behavior)
- [Verification](#verification)
- [Composition Notes](#composition-notes)

## What This Scenario Does

1. **PreToolUse** — blocks writes to `/etc` and prompts approval for any `bash` that contains `rm -rf`.
2. **PostToolUse** — logs the tool name and exit code to `/tmp/claude-hook-audit.log` after every tool call.
3. **PreCompact** — injects a terse state note into the context before the transcript is compacted.

All three hooks run from the same shell script library at `~/.claude/hooks/lib.sh` to avoid duplication.

---

## Directory Layout

```
~/.claude/
  hooks/
    lib.sh                  # shared helpers
    preflight-guard.sh      # PreToolUse handler
    post-audit.sh           # PostToolUse handler
    pre-compact-state.sh    # PreCompact handler
  settings.json             # wires hooks to events
```

---

## lib.sh — Shared Helpers

```bash
#!/usr/bin/env bash
# ~/.claude/hooks/lib.sh
# Shared helpers for all hooks. Source this file; do not execute directly.

log_audit() {
  local msg="$1"
  printf '%s %s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$msg" >> /tmp/claude-hook-audit.log
}

# Read and validate stdin JSON payload.
# Usage: payload=$(read_payload) || exit 1
read_payload() {
  local raw
  raw=$(cat)
  if [ -z "$raw" ]; then
    echo "ERROR: empty payload" >&2
    return 1
  fi
  printf '%s' "$raw"
}
```

---

## preflight-guard.sh — PreToolUse

```bash
#!/usr/bin/env bash
# ~/.claude/hooks/preflight-guard.sh
# PreToolUse: block writes to /etc, require approval for dangerous rm -rf.

set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/lib.sh"

payload=$(read_payload) || exit 0   # if no payload, pass through

tool_name=$(printf '%s' "$payload" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('tool_name',''))" 2>/dev/null || true)
tool_input=$(printf '%s' "$payload" | python3 -c "import sys,json; d=json.load(sys.stdin); print(json.dumps(d.get('tool_input',{})))" 2>/dev/null || true)

case "$tool_name" in
  Write|Edit)
    # Block any write whose path starts with /etc
    file_path=$(printf '%s' "$tool_input" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('file_path','') or d.get('path',''))" 2>/dev/null || true)
    real_path=$(realpath -m "$file_path" 2>/dev/null || printf '%s' "$file_path")
    if [[ "$real_path" == /etc/* ]]; then
      log_audit "BLOCKED $tool_name path=$real_path"
      # Exit code 2 = hard block; emit human-readable reason to stderr
      echo "PreToolUse guard: writes to /etc are not allowed." >&2
      exit 2
    fi
    ;;
  Bash)
    command_str=$(printf '%s' "$tool_input" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('command',''))" 2>/dev/null || true)
    if printf '%s' "$command_str" | grep -qE 'rm[[:space:]]+-[a-zA-Z]*r[a-zA-Z]*f|rm[[:space:]]+-[a-zA-Z]*f[a-zA-Z]*r'; then
      log_audit "PAUSED Bash rm-rf pattern detected"
      # Exit 0 + JSON permissionDecision=ask surfaces an approval prompt to the user
      jq -cn '{hookSpecificOutput: {hookEventName: "PreToolUse", permissionDecision: "ask", permissionDecisionReason: "rm -rf detected — awaiting operator approval."}}'
      exit 0
    fi
    ;;
esac

log_audit "PASS $tool_name"
exit 0
```

---

## post-audit.sh — PostToolUse

```bash
#!/usr/bin/env bash
# ~/.claude/hooks/post-audit.sh
# PostToolUse: append every tool result to the audit log.

set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/lib.sh"

payload=$(read_payload) || exit 0

tool_name=$(printf '%s' "$payload" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('tool_name','UNKNOWN'))" 2>/dev/null || true)
exit_code=$(printf '%s' "$payload" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('exit_code','?'))" 2>/dev/null || true)

log_audit "DONE tool=$tool_name exit=$exit_code"
exit 0
```

---

## pre-compact-state.sh — PreCompact

```bash
#!/usr/bin/env bash
# ~/.claude/hooks/pre-compact-state.sh
# PreCompact: write a terse state note to stdout so Claude injects it before compaction.

set -euo pipefail

# This output is injected into the compaction context as a system note.
# Keep it under 200 tokens — compaction already has budget pressure.
printf 'STATE NOTE (pre-compact): last audit log at /tmp/claude-hook-audit.log. '
printf 'Hook chain: preflight-guard (PreToolUse) + post-audit (PostToolUse) + this (PreCompact). '
printf 'If resuming, re-check audit log for any BLOCKED or PAUSED entries before continuing.\n'
exit 0
```

---

## settings.json — Hook Wiring

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "bash ~/.claude/hooks/preflight-guard.sh"
          }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "bash ~/.claude/hooks/post-audit.sh"
          }
        ]
      }
    ],
    "PreCompact": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "bash ~/.claude/hooks/pre-compact-state.sh"
          }
        ]
      }
    ]
  }
}
```

---

## Expected Behavior

| Action | Hook Fired | Expected Outcome |
|--------|-----------|-----------------|
| Claude writes a file to `/tmp/foo.txt` | PreToolUse | PASS logged; write proceeds |
| Claude writes a file to `/etc/hosts` | PreToolUse | BLOCKED logged; write rejected with error message |
| Claude runs `bash rm -rf /tmp/scratch` | PreToolUse | PAUSED logged; user prompted for approval (via JSON `permissionDecision: "ask"`) |
| Any tool completes | PostToolUse | `DONE tool=X exit=0` appended to audit log |
| Context nears compaction | PreCompact | State note injected; log path carried forward |

---

## Verification

After installing the hooks:

```bash
# 1. Confirm hook files are executable
chmod +x ~/.claude/hooks/preflight-guard.sh
chmod +x ~/.claude/hooks/post-audit.sh
chmod +x ~/.claude/hooks/pre-compact-state.sh

# 2. Dry-run PreToolUse manually
echo '{"tool_name":"Write","tool_input":{"file_path":"/etc/test"}}' \
  | bash ~/.claude/hooks/preflight-guard.sh
# Expect: exit 2 + "writes to /etc are not allowed" on stderr

# 3. Check audit log after any Claude session
cat /tmp/claude-hook-audit.log
```

---

## Composition Notes

- **PreToolUse exit codes** (re-verified 2026-07-11 against [code.claude.com/docs/en/hooks](https://code.claude.com/docs/en/hooks)): `0` = success, parse stdout for JSON output (use `permissionDecision` in JSON to allow/deny/ask/defer); `2` = hard block, stderr fed to Claude, JSON output ignored; other non-zero = non-blocking error logged. To request approval, exit `0` with JSON `{"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "ask", ...}}`.
- **PostToolUse** runs after the tool result is already committed; it cannot cancel the action but can flag it.
- **PreCompact** output replaces or supplements the default compaction summary. Keep it terse.
- All three hooks read stdin JSON — never skip the `read_payload` call even if you only need one field.
- Run `shellcheck ~/.claude/hooks/*.sh` before deploying to production sessions.
