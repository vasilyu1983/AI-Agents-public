---
name: agents-hooks
description: Configures Claude Code hooks and Codex hooks.json/notify. Use when adding PreToolUse guards, Stop hooks, managed hooks, format-on-save, preflight, audits, or worktree/budget hooks.
compatibility: Claude Code + Codex. Claude Code hooks plus Codex notifications — runtime-specific invocation in both.
version: "1.6"
last_validated: 2026-09-24
---

# Claude Code Hooks + Codex Notifications

Use this skill when hook behavior is the main concern: Claude lifecycle hooks, runtime preflight, guardrails, async verification, worktree lifecycle checks, subagent coordination, or Codex notification callbacks.

Claude and Codex are not equivalent here. Claude has a broad, stable hook system. Codex has two surfaces: the long-stable notification surface (`notify` + `tui.notifications`), and a lifecycle-hooks system (`hooks.json`; see [developers.openai.com/codex/hooks](https://developers.openai.com/codex/hooks)) whose events, handler types, and trust rules change between releases and have had firing-reliability gaps. Both event sets grow, so look up the current list in each runtime's hooks reference instead of trusting a count. This skill owns the Codex hook facts as lookup steps in [`references/hook-templates.md`](references/hook-templates.md) §Codex. Prefer `notify` for anything that must be dependable, and confirm a Codex hook fires on your runtime before relying on it.

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
| subagent design or delegation boundaries | [../agents-subagents/SKILL.md](../agents-subagents/SKILL.md) |
| multi-agent orchestration | [../agents-swarm-orchestration/SKILL.md](../agents-swarm-orchestration/SKILL.md) |
| permission modes and approval routing for coding agents | [../ai-coding-agents-safety-envelope/SKILL.md](../ai-coding-agents-safety-envelope/SKILL.md) |

## Capability Boundary

| Capability | Claude Code | Codex |
|-----------|-------------|-------|
| broad lifecycle hooks | yes (stable; look up the current event table) | yes via `hooks.json` (smaller event set, reliability gaps; look up the matcher table) |
| command or decision control | yes | yes (`PreToolUse` deny; `Stop`/`SubagentStop` block-and-continue); check which handler types execute and which are parsed but skipped |
| payload mutation on supported events | yes (`updatedInput`, `updatedToolOutput`) | check whether `PreToolUse` accepts `updatedInput` on your version |
| external callback program | yes | `notify` (dependable) + `hooks.json` hooks (verify-first; a trust review can silently skip a changed hook) |
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
| Measure which skills actually trigger across sessions | `PreToolUse` (matcher `Skill`) + `UserPromptExpansion` (`/skillname` path) | `command` | patterns §15 |
| Desktop alert / hand off "turn complete" to a local process (Codex) | `notify` + `tui.notifications` | external program | patterns §12 |

## Workflow

1. Confirm whether the task is Claude hooks, Codex notifications, or mixed setup.
2. Choose the minimum event surface that satisfies the requirement.
3. Prefer deterministic command hooks for enforcement.
4. Keep synchronous hooks fast; move heavy work into async or background paths.
5. Validate event support and payload assumptions against current docs before final advice.
6. Declare the timeout and error posture for the exact runtime, event, and handler type. In current Claude Code, an explicit `PreToolUse` deny or exit `2` blocks the tool call, while a timed-out `command`, `http`, or `mcp_tool` handler returns the call to normal permission evaluation; an Agent SDK callback timeout blocks it. A policy that must remain closed on handler failure needs a separate deny rule or enforcement in the execution substrate. Test timeout, malformed output, and duplicate delivery separately from the happy path.

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

## Event Surface (Claude Code)

Source: [code.claude.com/docs/en/hooks](https://code.claude.com/docs/en/hooks). The tables below group the events by purpose; they are a map, not the authoritative list. New events arrive between releases, so before wiring an event confirm it in the reference's event table and read its blocking column.

Two rules hold across the table:

- **Context-only events cannot block.** For `SessionStart`, `SubagentStart`, and any event the reference marks "no blocking", exit `2` only shows stderr to the user as a hook-error notice; Claude never sees it. Send anything the model must know as `hookSpecificOutput.additionalContext` on exit `0`.
- **Blocking stop hooks need a loop guard.** `Stop` and `SubagentStop` payloads carry `stop_hook_active`; exit `0` without blocking when it is `true`. The hooks reference documents a cap on consecutive stop-hook continuations and the environment variable that raises it; a gate that needs its own limit should count in a session-keyed state file rather than lean on the runtime cap.

**Session lifecycle**

| Event | Fires when | Can block? |
|-------|-----------|-----------|
| `SessionStart` | session begins or resumes | no (context only; see rule above) |
| `Setup` | `claude --init-only`, or `--init` / `--maintenance` in `-p` mode; one-time preparation for CI or scripts (matcher `init` / `maintenance`) | no |
| `SessionEnd` | session terminates | no (runs under a short default timeout; look up the default, the maximum, and the override variable before putting cleanup work here) |

**Per-turn**

| Event | Fires when | Can block? |
|-------|-----------|-----------|
| `UserPromptSubmit` | user submits prompt, before Claude sees it | yes |
| `UserPromptExpansion` | user-typed command expands into a prompt | yes |
| `Stop` | Claude finishes responding | yes (check `stop_hook_active`) |
| `StopFailure` | turn ends due to API error | no |
| `MessageDisplay` | assistant text is displayed (display-only, does not alter transcript) | no |
| `PreModelSwitch` | before the session switches model | yes |
| `PostModelSwitch` | after a model switch completes | no (context only) |

**Tool execution**

| Event | Fires when | Can block? |
|-------|-----------|-----------|
| `PreToolUse` | before any tool call | yes |
| `PermissionRequest` | permission dialog appears | via `hookSpecificOutput.decision` only; exit 2 is not honored |
| `PermissionDenied` | tool denied by auto-mode classifier | no |
| `PostToolUse` | after tool call succeeds | no |
| `PostToolUseFailure` | after tool call fails | no |
| `PostToolBatch` | after full batch of parallel tool calls resolves | yes |
| `Elicitation` | MCP server requests user input | yes |
| `ElicitationResult` | user responds to MCP elicitation | yes |

**Subagent / team**

| Event | Fires when | Can block? |
|-------|-----------|-----------|
| `SubagentStart` | subagent spawned | no (context only, via `hookSpecificOutput.additionalContext`) |
| `SubagentStop` | subagent finishes | yes (check `stop_hook_active`; read `agent_transcript_path`, not `transcript_path`) |
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
| `DirectoryAdded` | a directory is added to the session workspace | no |
| `FileChanged` | watched file changes on disk | no |
| `WorktreeCreate` | worktree being created | yes (any non-zero exit); read the requested `name` from the payload |
| `WorktreeRemove` | worktree being removed | check the reference's blocking column before using it as a gate |

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
| `command` | usually lowest latency; measure | script bug, wrong exit code, missing binary | deterministic checks — the default choice |
| `http` | network round-trip | endpoint down, timeout, no local fallback | audit must leave the box immediately (SIEM, webhook) |
| `mcp_tool` | depends on server | server not connected, tool schema drift | policy lives on a connected MCP server already |
| `prompt` | one extra LLM call | non-determinism, model-dependent token cost | a single-turn semantic judgment is enough (no tool use needed) |
| `agent` (experimental) | usually higher latency and usage; measure | cost/latency creep if used on hot paths | multi-step semantic verification (e.g. "did this satisfy acceptance criteria") |

Escalate down this list only when the simpler type cannot express the check; compare observed latency and usage before making a cost claim — see [`references/hook-patterns.md`](references/hook-patterns.md) §3 for the command-vs-agent decision in practice.

## Execution Model And Precedence

- **Parallel, not sequential.** When multiple registered hooks match the same event, Claude Code runs all of them in parallel. Do not assume one hook's output is visible to another, and do not rely on registration order to break ties. Identical `command` hooks are deduplicated by command string + `args`; identical `http` hooks by URL — near-duplicate hooks (different flags, same intent) are not deduplicated and will double-fire.
- **Conflicting decisions use restrictive precedence.** Current Claude Code resolves `deny` before `defer`, `ask`, and `allow`. Still avoid overlapping hooks that disagree: narrow matchers so the effective rule is reviewable, and test the merged configuration rather than relying on one hook in isolation.
- **Settings precedence** (per [code.claude.com/docs/en/settings](https://code.claude.com/docs/en/settings); re-check there when a hook's scope matters): managed (org) policy > CLI flags > project `.claude/settings.local.json` > project `.claude/settings.json` > user `~/.claude/settings.json`. This corrects an earlier version of this skill, which put `.claude/settings.local.json` last — it actually overrides both project and user settings, not the reverse. Two more hook-bearing scopes exist beyond these four: plugin `hooks/hooks.json` (active whenever the plugin is enabled) and skill/agent frontmatter (a skill's hooks stay registered for the rest of the session once the skill is invoked; a subagent's only while it runs). Hooks from every scope merge and run together rather than override each other — a broader-scoped hook does not silently replace a narrower one — so this ordering mainly governs `disableAllHooks` and single-value settings conflicts, not whether a given hook fires.
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

`SubagentStart` does not inject plain stdout. Context reaches the subagent only through `hookSpecificOutput.additionalContext` in the JSON output; `systemMessage` is a top-level field shown to the user. `SubagentStop` can block the subagent from reporting back (exit `0` with `decision: "block"`); check `stop_hook_active` first and read `agent_transcript_path`, which is the subagent's transcript.

### Codex

- use `notify` for external callbacks (long-stable, dependable)
- use `tui.notifications` for terminal notification policy
- for lifecycle automation, use `hooks.json` after running the lookup steps in [`references/hook-templates.md`](references/hook-templates.md) §Codex (events, handler types, async, `updatedInput`, managed policy and trust review, open firing bugs). Verify it fires on the target runtime; fall back to `notify` if dependability matters.
- before substituting `Stop` for end-of-session capture, check the Codex matcher table for a session-end event; `Stop` may fire per turn, so dedupe if you need once-per-session semantics.
- do not assume Claude-style lifecycle parity for any event you have not found in the Codex reference

### Community Recipes

Third-party hooks worth knowing about, treat as community-sourced (verify provenance and review code before installing on production sessions):

- **`monitoring/context-timeline`** ([aitmpl.com](https://www.aitmpl.com/component/hook/monitoring/context-timeline), via Daniel San, 2026-04-26 [thread](https://x.com/dani_avila7/status/2048486242321662189)) — distributed through the `claude-code-templates` npm package. Do not run it as `npx claude-code-templates@latest`: a moving `@latest` executes whatever the registry serves at that moment with your user permissions. Either review one published version and pin it exactly (`npx claude-code-templates@<reviewed-version> --hook monitoring/context-timeline`), or vendor the hook script into `.claude/hooks/` after reading it. Shows a live timeline of the main agent's context window plus every subagent running in parallel, including the context each subagent returns when it finishes. Useful when debugging multi-worker fan-out or forked subagents (whether fork mode needs an opt-in depends on version and surface; see [`../agents-subagents/SKILL.md`](../agents-subagents/SKILL.md) §"Forking Parent Context Into Subagents"). Treat as observability, not policy enforcement — and audit the hook source before adding to a session that touches secrets.

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
  Resolution: Check the Capability Boundary table above before wiring any hook. Codex has two separate surfaces, `notify`/`tui.notifications` and the `hooks.json` lifecycle system, and neither matches Claude's event set. Look up the Codex matcher table and test on the actual runtime before deploying.

- Putting slow network calls, broad test suites, or repo-wide scans in always-on hooks.
  Resolution: Measure hook latency on your own runtime (no official budget is published) and move anything that visibly stalls the loop into the documented `async: true` path. A bare background job (`&`) loses output delivery and timeout handling. Reserve synchronous hooks for fast, narrow checks.

- Mutating files or config in a hook without leaving a reviewable diff or audit trail.
  Resolution: Write mutations through the normal git-tracked file path. Log every mutation to an append-only audit file (e.g. `/tmp/claude-hook-audit.log`). See `references/scenario-preflight-chain.md` for a working example.

- Reloading plugin hooks non-atomically and leaving stale handlers active beside new ones.
  Resolution: Clear all handlers first, then register the new set. Never add new handlers before removing old ones. Use a lock file or atomic swap (write to a temp path, then `mv`) if the registration sequence can be interrupted.

- Trusting payload shape, cwd, or path values without canonicalization and boundary checks.
  Resolution: Always call `realpath -m` (or equivalent) on any path from the payload before using it. Validate that the resolved path is within the expected root before acting. Treat stdin JSON as untrusted input regardless of hook type.

- Assuming two hooks on the same event run in order.
  Resolution: Claude Code runs all matching hooks in parallel and resolves conflicting decisions by the restrictive precedence in Execution Model above (`deny` first; check the hooks reference for the exact order on events with their own decision set). Still narrow matchers so hooks on the same event rarely disagree; a reviewed merged config is easier to reason about than arbitration.

- Writing a `Stop` or `SubagentStop` gate that blocks without checking `stop_hook_active`.
  Resolution: Exit `0` when `stop_hook_active` is `true`. Without the guard, a persistent failure condition forces extra turns until the runtime's block cap stops it.

- Reading a payload field by the name you expect rather than the name the reference documents.
  Resolution: Build dry-run payloads from the documented field names and test the input the guard must block. A wrong key reads as empty, so the guard prints nothing and exits `0`, which looks like a pass. `scripts/test_hook_templates.py` does this for the templates.

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
- [scripts/test_hook_templates.py](scripts/test_hook_templates.py) — runs each template against doc-shaped payloads; run after editing a template
- [data/sources.json](data/sources.json)

**Related Skills**

- [../agents-subagents/SKILL.md](../agents-subagents/SKILL.md)
- [../agents-mcp/SKILL.md](../agents-mcp/SKILL.md)
- [../agents-memory/SKILL.md](../agents-memory/SKILL.md)
- [../agents-skills/SKILL.md](../agents-skills/SKILL.md)
- [../agents-swarm-orchestration/SKILL.md](../agents-swarm-orchestration/SKILL.md)
- [../ai-coding-agents-safety-envelope/SKILL.md](../ai-coding-agents-safety-envelope/SKILL.md)
- [../ops-devops-platform/SKILL.md](../ops-devops-platform/SKILL.md)

## Learnings Loop

When prior decisions or pitfalls are relevant, consult `learnings.consolidated.md` if present; use `learnings.md` only for needed history or as the available fallback. Otherwise skip both.

After applying it, if you encountered a pattern worth remembering, a mistake worth preventing, or a domain fact that surprised you, append one dated bullet to `learnings.md` via `agents-skills-feedback-loop/scripts/append_learning.py`. Do not modify `SKILL.md` itself.
