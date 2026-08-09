---
name: agents-hooks
description: Configures Claude Code hooks and Codex hooks.json/notify callbacks. Use when adding guardrails, preflight, audit trails, worktree automation, or budget enforcement.
compatibility: Claude Code + Codex. Claude Code hooks plus Codex notifications — runtime-specific invocation in both.
version: "1.5"
last_validated: 2026-07-11
---

# Claude Code Hooks + Codex Notifications

Use this skill when hook behavior is the main concern: Claude lifecycle hooks, runtime preflight, guardrails, async verification, worktree lifecycle checks, subagent coordination, or Codex notification callbacks.

Claude and Codex are not equivalent here. Claude has a broad, stable hook system (30 events, re-verified against official docs 2026-07-11). Codex has two surfaces: the long-stable notification surface (`notify` + `tui.notifications`), and a newer lifecycle-hooks system (`hooks.json` with events including `SessionStart`, `UserPromptSubmit`, `SubagentStop`, `Stop`, `PreCompact`/`PostCompact` — see [developers.openai.com/codex/hooks](https://developers.openai.com/codex/hooks)). The Codex hooks system is less mature than Claude's and has known firing-reliability gaps (e.g. [codex#17532](https://github.com/openai/codex/issues/17532): repo-local `.codex/config.toml` hooks may not fire in interactive sessions). Prefer `notify` for anything that must be dependable; treat Codex `hooks.json` as usable-but-verify and confirm it fires on your runtime before relying on it.

## Quick Reference

| Need | Event / Approach |
|------|---------|
| enforce pre-tool policy or guardrails | `PreToolUse` command hook |
| fast runtime checks at session start | `SessionStart` or `Setup` |
| react to user prompt before Claude sees it | `UserPromptSubmit` |
| run checks after edits (non-blocking) | `PostToolUse` (async/background) |
| catch tool failures separately | `PostToolUseFailure` |
| check after a full batch of parallel tool calls | `PostToolBatch` |
| inject context into or coordinate subagents | `SubagentStart` / `SubagentStop` |
| transform what the user sees (not the transcript) | `MessageDisplay` |
| persist compact durable state before compaction | `PreCompact` |
| react after compaction completes | `PostCompact` |
| handle worktree setup and teardown | `WorktreeCreate` / `WorktreeRemove` |
| react to `cd` or watched file changes | `CwdChanged` / `FileChanged` |
| keep agent team from going idle | `TeammateIdle` |
| handle API errors at turn end | `StopFailure` |
| reload plugin hooks safely | atomic clear-then-register swap |
| add Codex callback behavior | `notify` external program plus `tui.notifications` |
| enforce budgets, iteration caps, stagnation, kill-switches | [`references/budget-and-loop-hooks.md`](references/budget-and-loop-hooks.md) |

## When To Use This Skill

Use this skill when the task is:

- building Claude hook automation
- adding command guardrails or approval logic
- wiring verification or audit hooks
- managing hook-scoped repo hygiene
- configuring Codex notifications or callback programs

Route elsewhere when the main concern is:

| Need | Use Instead |
|------|-------------|
| durable project memory or compaction content | [../agents-memory/SKILL.md](../agents-memory/SKILL.md) |
| MCP design or server integration | [../agents-mcp/SKILL.md](../agents-mcp/SKILL.md) |
| subagent design or delegation boundaries | `agents-subagents` |
| multi-agent orchestration | [../agents-swarm-orchestration/SKILL.md](../agents-swarm-orchestration/SKILL.md) |
| permission modes and approval routing for coding agents | [../ai-coding-agents-permissions/SKILL.md](../ai-coding-agents-permissions/SKILL.md) |

## Capability Boundary

| Capability | Claude Code | Codex |
|-----------|-------------|-------|
| broad lifecycle hooks | yes (stable, 30 events) | yes via `hooks.json` (newer, fewer events, reliability gaps) |
| command or decision control | yes | yes (`PreToolUse` deny; `Stop`/`SubagentStop` block-and-continue) — `command` handlers only, verify per runtime |
| payload mutation on supported events | yes | not documented |
| external callback program | yes | `notify` (dependable) + `hooks.json` command hooks (verify-first) |
| best use | policy, verification, hygiene | dependable: `notify` alerts/logging; experimental: lifecycle automation via `hooks.json` |

## Typical Scenarios

Real situations mapped to the smallest event + recipe that solves them. Pick the narrowest row that matches.

| Scenario | Event(s) | Handler | Recipe |
|----------|----------|---------|--------|
| Block `rm -rf`, `git push --force`, `git add .` before they run | `PreToolUse` (matcher `Bash`) | `command` | [`references/hook-templates.md`](references/hook-templates.md), patterns §8/§11 |
| Auto-format and smoke-check after every edit, without slowing the agent | `PostToolUse` (matcher `Edit\|Write`, `async: true`) | `command` | patterns §1 |
| Require approval for production/destructive tools instead of hard-denying | `PreToolUse` → `permissionDecision: ask`, `PermissionRequest` | `command` | patterns §8 |
| Inject repo state (branch, task id, top commands) at session start | `SessionStart` / `Setup` | `command` | [`references/runtime-preflight-hooks.md`](references/runtime-preflight-hooks.md), patterns §6 |
| Preserve critical state across context compaction | `PreCompact` (checkpoint) + `SessionStart` (restore) | `command` | [`hook-templates.md`](references/hook-templates.md), patterns §5 |
| Gate the next model call after a parallel tool burst | `PostToolBatch` | `command`/`agent` | [`hook-templates.md`](references/hook-templates.md), patterns §1 |
| Pass context into subagents and validate their output before they report back | `SubagentStart` (inject) + `SubagentStop` (block) | `command` | [`hook-templates.md`](references/hook-templates.md), SKILL.md §Subagent coordination |
| Keep an agent team from going idle prematurely | `TeammateIdle` | `command` | Quick Reference |
| Per-worktree setup/teardown (caches, env files, indexes) | `WorktreeCreate` / `WorktreeRemove` | `command` | [`hook-templates.md`](references/hook-templates.md), patterns §7 |
| Ship audit events off-box to a SIEM/webhook immediately | `PostToolUse` / `Notification` | `http` | patterns §2 |
| Semantic "are acceptance criteria met?" gate, not a syntactic one | `Stop` / `SubagentStop` | `agent` | patterns §3 |
| Enforce a token/iteration/stagnation budget or kill-switch on an autonomous loop | `Stop` / `PostToolBatch` / `UserPromptSubmit` | `command` | [`references/budget-and-loop-hooks.md`](references/budget-and-loop-hooks.md) |
| Audit edits to hook/approval/sandbox policy itself | `ConfigChange` | `command` | [`hook-templates.md`](references/hook-templates.md), patterns §4 |
| Reload `.envrc`/local config when the directory changes | `CwdChanged` / `FileChanged` | `command` | patterns §6 |
| Measure which skills actually trigger across sessions | `PreToolUse` (matcher `Read`) | `command` | patterns §15 |
| Desktop alert / hand off "turn complete" to a local process (Codex) | `notify` + `tui.notifications` | external program | patterns §12 |

## Workflow

1. Confirm whether the task is Claude hooks, Codex notifications, or mixed setup.
2. Choose the minimum event surface that satisfies the requirement.
3. Prefer deterministic command hooks for enforcement.
4. Keep synchronous hooks fast; move heavy work into async or background paths.
5. Validate event support and payload assumptions against current docs before final advice.

**Validate and install checklist**

```bash
# 1. Lint every hook script before deployment
shellcheck ~/.claude/hooks/*.sh

# 2. Dry-run a hook by piping a sample payload
echo '{"tool_name":"Bash","tool_input":{"command":"rm -rf /"}}' \
  | bash ~/.claude/hooks/preflight-guard.sh

# 3. Confirm hook files are executable
chmod +x ~/.claude/hooks/*.sh

# 4. Check audit log after a test session
cat /tmp/claude-hook-audit.log

# 5. Disable all hooks for emergency bypass
# Set "disableAllHooks": true in ~/.claude/settings.json
```

## ASCII Flow

```text
Hook request
  -> Identify runtime
     +-- Claude Code -> choose lifecycle event -> keep sync hook fast -> async heavy checks
     +-- Codex       -> configure notify/tui.notifications -> avoid lifecycle parity claims
  -> Validate payload, paths, and secrets boundary
  -> Test on the target runtime
  -> Document event, command, failure mode, and rollback path
```

## Event Surface (Claude Code, verified 2026-07-11)

Source: [code.claude.com/docs/en/hooks](https://code.claude.com/docs/en/hooks)

**Session lifecycle**

| Event | Fires when | Can block? |
|-------|-----------|-----------|
| `SessionStart` | session begins or resumes | no |
| `Setup` | one-time init (`--init`, `--maintenance`) | no |
| `SessionEnd` | session terminates | no |

**Per-turn**

| Event | Fires when | Can block? |
|-------|-----------|-----------|
| `UserPromptSubmit` | user submits prompt, before Claude sees it | yes |
| `UserPromptExpansion` | user-typed command expands into a prompt | yes |
| `Stop` | Claude finishes responding | yes |
| `StopFailure` | turn ends due to API error | no |
| `MessageDisplay` | assistant text is displayed (display-only, does not alter transcript) | no |

**Tool execution**

| Event | Fires when | Can block? |
|-------|-----------|-----------|
| `PreToolUse` | before any tool call | yes |
| `PermissionRequest` | permission dialog appears | yes |
| `PermissionDenied` | tool denied by auto-mode classifier | no |
| `PostToolUse` | after tool call succeeds | no |
| `PostToolUseFailure` | after tool call fails | no |
| `PostToolBatch` | after full batch of parallel tool calls resolves | yes |
| `Elicitation` | MCP server requests user input | yes |
| `ElicitationResult` | user responds to MCP elicitation | yes |

**Subagent / team**

| Event | Fires when | Can block? |
|-------|-----------|-----------|
| `SubagentStart` | subagent spawned | no |
| `SubagentStop` | subagent finishes | yes |
| `TeammateIdle` | agent-team teammate about to go idle | yes |

**Task**

| Event | Fires when | Can block? |
|-------|-----------|-----------|
| `TaskCreated` | task being created via `TaskCreate` | yes |
| `TaskCompleted` | task being marked complete | yes |

**Config / filesystem**

| Event | Fires when | Can block? |
|-------|-----------|-----------|
| `ConfigChange` | config file changes during session | yes (except `policy_settings`) |
| `InstructionsLoaded` | instruction files load (CLAUDE.md, includes, glob/path matches, on compact) | no (observability; exit code ignored) |
| `CwdChanged` | working directory changes (`cd`) | no |
| `FileChanged` | watched file changes on disk | no |
| `WorktreeCreate` | worktree being created | yes (any non-zero exit) |
| `WorktreeRemove` | worktree being removed | no |

**Compaction / display**

| Event | Fires when | Can block? |
|-------|-----------|-----------|
| `PreCompact` | before context compaction | yes |
| `PostCompact` | after compaction completes | no |
| `Notification` | Claude Code sends a notification | no |

## Hook Configuration Snippet

Minimal `settings.json` wiring (copy into `~/.claude/settings.json` or `.claude/settings.json`):

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
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
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "bash ~/.claude/hooks/post-audit.sh",
            "async": true
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

**Matcher rules**: empty string or `"*"` = match all; `|`-separated words = exact list (e.g. `"Edit|Write"`); any string with other characters = JavaScript regex (e.g. `"mcp__memory__.*"`).

**Hook types**: `command` (shell script), `http` (POST to URL), `mcp_tool` (call MCP server tool), `prompt` (single-turn LLM), `agent` (spawns subagent, experimental).

**Exit codes**: `0` = success, parse stdout for JSON; `2` = hard block, stderr fed to Claude; other non-zero = non-blocking error logged.

**Payload mutation** (exit `0` with JSON `hookSpecificOutput`): `PreToolUse` can set `permissionDecision` to `allow` / `deny` / `ask` / `defer`; `PostToolUse` can replace the tool result with `updatedToolOutput`; `MessageDisplay` can rewrite on-screen text with `displayContent` (screen only — transcript and Claude's view are unchanged). Always set `hookEventName` in the output to the firing event.

**Exec vs. shell form**: add `"args": [...]` to avoid shell and support cross-platform use. Omit `args` to use `sh -c` with pipes and `&&`.

**Disable all hooks**: set `"disableAllHooks": true` in settings for emergency bypass.

## Choosing A Hook Type

| Type | Latency | Failure mode | Use when |
|------|---------|--------------|----------|
| `command` | fastest (local process) | script bug, wrong exit code, missing binary | deterministic checks — the default choice |
| `http` | network round-trip | endpoint down, timeout, no local fallback | audit must leave the box immediately (SIEM, webhook) |
| `mcp_tool` | depends on server | server not connected, tool schema drift | policy lives on a connected MCP server already |
| `prompt` | one extra LLM call | non-determinism, added token cost | a single-turn semantic judgment is enough (no tool use needed) |
| `agent` (experimental) | slowest, most tokens | cost/latency creep if used on hot paths | multi-step semantic verification (e.g. "did this satisfy acceptance criteria") |

Escalate down this list only when the cheaper type can't express the check — see [`references/hook-patterns.md`](references/hook-patterns.md) §3 for the command-vs-agent decision in practice.

## Execution Model And Precedence

- **Parallel, not sequential.** When multiple registered hooks match the same event, Claude Code runs all of them in parallel. Do not assume one hook's output is visible to another, and do not rely on registration order to break ties. Identical `command` hooks are deduplicated by command string + `args`; identical `http` hooks by URL — near-duplicate hooks (different flags, same intent) are not deduplicated and will double-fire.
- **Conflicting decisions are not spec'd as "deny wins."** The docs do not officially guarantee a resolution order when one matching hook returns `allow` and another returns `deny` on the same event. Design as if any single `deny` should be treated as authoritative (fail-closed), and avoid registering two hooks with overlapping matchers that can disagree — narrow the matchers instead.
- **Settings precedence** (per [code.claude.com/docs/en/settings](https://code.claude.com/docs/en/settings), re-verified 2026-07-11): managed (org) policy > CLI flags > project `.claude/settings.local.json` > project `.claude/settings.json` > user `~/.claude/settings.json`. This corrects an earlier version of this skill, which put `.claude/settings.local.json` last — it actually overrides both project and user settings, not the reverse. Two more hook-bearing scopes exist beyond these four: plugin `hooks/hooks.json` (active whenever the plugin is enabled) and skill/agent frontmatter (active only while that component is active). Hooks from every scope merge and run together rather than override each other — a broader-scoped hook does not silently replace a narrower one — so this ordering mainly governs `disableAllHooks` and single-value settings conflicts, not whether a given hook fires.
- **`allowManagedHooksOnly`**: an enterprise admin can set this in managed settings to block all user/project/plugin hooks except those bundled with plugins force-enabled via managed `enabledPlugins`. If a hook you registered mysteriously stops firing in a managed environment, check this first before debugging the hook script.
- **Scoping a hook without a shell condition**: tool-event hooks (`PreToolUse` etc.) accept an `if` field — a permission-rule string like `"if": "Bash(git *)"` — to narrow when a handler fires beyond what `matcher` alone expresses. Prefer this over duplicating the same logic inside the script.

## Recommended Patterns

### Claude

- `SessionStart` or `Setup` for runtime preflight
- `UserPromptSubmit` to intercept or enrich prompts before Claude processes them
- `PreToolUse` for narrow allow, deny, or ask guardrails
- `PostToolUse` for formatting and smoke checks; `PostToolUseFailure` for failure-specific handling
- `PostToolBatch` to gate the next model call after a parallel tool batch
- `SubagentStart` to inject context into spawned subagents; `SubagentStop` to validate their output
- `PreCompact` for terse state reinjection; `PostCompact` for post-compaction orientation
- `CwdChanged` to reload `.envrc` or local configs when directory changes
- `ConfigChange` for auditing hook-policy edits
- `WorktreeCreate` and `WorktreeRemove` for worktree hygiene
- clear and re-register plugin hooks atomically during reloads so stale handlers never coexist with new ones

### Subagent coordination

Inject context into spawned subagents via `SubagentStart` and validate their output via `SubagentStop`:

```json
{
  "hooks": {
    "SubagentStart": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "bash ~/.claude/hooks/subagent-context.sh"
          }
        ]
      }
    ],
    "SubagentStop": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "bash ~/.claude/hooks/subagent-validate.sh"
          }
        ]
      }
    ]
  }
}
```

`SubagentStart` command stdout is injected as `systemMessage` context for the subagent. `SubagentStop` can block the subagent from reporting back (exit `0` with `decision: "block"`).

### Codex

- use `notify` for external callbacks (long-stable, dependable)
- use `tui.notifications` for terminal notification policy
- for lifecycle automation, Codex now has `hooks.json` (events incl. `SessionStart`, `UserPromptSubmit`, `SubagentStop`, `Stop`, `PreCompact`/`PostCompact`; [docs](https://developers.openai.com/codex/hooks)) — but it is newer and has firing-reliability gaps ([codex#17532](https://github.com/openai/codex/issues/17532)). Verify it fires on the target runtime before depending on it; fall back to `notify` if dependability matters.
- Codex has no Claude-style `SessionEnd`; use `Stop` for end-of-turn capture, and note `Stop` may fire per turn (dedupe if you need once-per-session semantics).
- do not assume full Claude-style lifecycle parity

### Community Recipes

Third-party hooks worth knowing about, treat as community-sourced (verify provenance and review code before installing on production sessions):

- **`monitoring/context-timeline`** ([aitmpl.com](https://www.aitmpl.com/component/hook/monitoring/context-timeline), via Daniel San, 2026-04-26 [thread](https://x.com/dani_avila7/status/2048486242321662189)) — installs with `npx claude-code-templates@latest --hook monitoring/context-timeline`. Shows a live timeline of the main agent's context window plus every subagent running in parallel, including the context each subagent returns when it finishes. Useful when debugging multi-worker fan-out under Opus 4.7 or after enabling `CLAUDE_CODE_FORK_SUBAGENT=1` (see `agents-subagents` §"Forking Parent Context Into Subagents"). Treat as observability, not policy enforcement — and audit the hook source before adding to a session that touches secrets.

## Security Rules

- treat stdin JSON as untrusted input
- validate fields before use
- prefer canonical path checks over filename regex
- quote shell variables and avoid `eval`
- keep secrets out of logs and checked-in config
- keep blocking hooks narrow and auditable
- run ShellCheck on non-trivial shell hooks

## Known Traps

- Assuming Claude lifecycle events and Codex notification surfaces are interchangeable.
  Resolution: Check the Capability Boundary table above before wiring any hook. Claude has broad lifecycle events; Codex exposes only `notify` and `tui.notifications`. Test on the actual runtime before deploying.

- Putting slow network calls, broad test suites, or repo-wide scans in always-on hooks.
  Resolution: Move anything over ~200ms into an async or background path. Use `PostToolUse` with a background job (`&`) rather than blocking the tool call. Reserve synchronous hooks for fast, narrow checks.

- Mutating files or config in a hook without leaving a reviewable diff or audit trail.
  Resolution: Write mutations through the normal git-tracked file path. Log every mutation to an append-only audit file (e.g. `/tmp/claude-hook-audit.log`). See `references/scenario-preflight-chain.md` for a working example.

- Reloading plugin hooks non-atomically and leaving stale handlers active beside new ones.
  Resolution: Clear all handlers first, then register the new set. Never add new handlers before removing old ones. Use a lock file or atomic swap (write to a temp path, then `mv`) if the registration sequence can be interrupted.

- Trusting payload shape, cwd, or path values without canonicalization and boundary checks.
  Resolution: Always call `realpath -m` (or equivalent) on any path from the payload before using it. Validate that the resolved path is within the expected root before acting. Treat stdin JSON as untrusted input regardless of hook type.

- Assuming two hooks on the same event run in order, or that "deny" is guaranteed to beat "allow" when they disagree.
  Resolution: Claude Code runs all matching hooks in parallel with no documented tie-break rule. Narrow matchers so hooks on the same event cannot disagree, and treat any single `deny` as authoritative in your own hook logic rather than depending on runtime arbitration.

- A hook silently stops firing after it worked fine in dev, and the script itself looks correct.
  Resolution: Check settings precedence and `allowManagedHooksOnly` before debugging the script — an org-level managed policy can suppress user/project/plugin hooks entirely in a way that looks identical to a broken hook.

## Anti-Patterns

- heavy synchronous test suites in every hook
- undocumented assumptions about Codex event parity
- regex-only path validation
- raw payload or environment logging without redaction
- silent dangerous rewrites that are not reviewable

## Navigation

**Resources**

- [references/hook-templates.md](references/hook-templates.md)
- [references/hook-patterns.md](references/hook-patterns.md)
- [references/hook-security.md](references/hook-security.md)
- [references/runtime-preflight-hooks.md](references/runtime-preflight-hooks.md)
- [references/scenario-preflight-chain.md](references/scenario-preflight-chain.md) — end-to-end runnable scenario: PreToolUse + PostToolUse + PreCompact composed
- [references/budget-and-loop-hooks.md](references/budget-and-loop-hooks.md) — budget, iteration cap, stagnation, kill-switch hooks for autonomous loops, triggered runs, and always-on bots
- [assets/template-preflight-runtime-hook.sh](assets/template-preflight-runtime-hook.sh)
- [data/sources.json](data/sources.json)

**Related Skills**

- `agents-subagents`
- [../agents-mcp/SKILL.md](../agents-mcp/SKILL.md)
- [../agents-memory/SKILL.md](../agents-memory/SKILL.md)
- [../agents-skills/SKILL.md](../agents-skills/SKILL.md)
- [../agents-swarm-orchestration/SKILL.md](../agents-swarm-orchestration/SKILL.md)
- [../ai-coding-agents-permissions/SKILL.md](../ai-coding-agents-permissions/SKILL.md)
- [../ops-devops-platform/SKILL.md](../ops-devops-platform/SKILL.md)

## Fact-Checking

- Known bugs, regressions, framework/compiler/runtime footguns, and version-specific crash or workaround guidance must be verified against current primary web sources before being treated as current fact.
- Verify current hook behavior, event support, JSON schema, and Codex notification capabilities against official docs before operational guidance.
- Prefer official Claude and OpenAI sources over community posts.
- If live verification is unavailable, mark hook-surface claims as unverified.

## Learnings Loop

Before applying this skill on a non-trivial task, read `learnings.consolidated.md` in this directory (and `learnings.md` if present).

After applying it, if you encountered a pattern worth remembering, a mistake worth preventing, or a domain fact that surprised you, append one dated bullet to `learnings.md` via `agents-skills-feedback-loop/scripts/append_learning.py`. Do not modify `SKILL.md` itself.

