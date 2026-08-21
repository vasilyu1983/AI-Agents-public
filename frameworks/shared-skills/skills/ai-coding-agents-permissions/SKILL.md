---
name: ai-coding-agents-permissions
description: "Designs approval and permission systems for coding-agent runtimes. Use when modeling tool approvals, plan-mode transitions, sandbox prompts, or worker permission handoffs."
compatibility: Portable core. Works on Claude Code and Codex.
version: "1.1"
last_validated: 2026-07-11
---

# AI Coding Agents Permissions

Use this skill to design or review the approval system for a coding-agent runtime: tool permission modes, plan-mode entry and exit, sandbox escalation, background-agent auto-deny behavior, and leader-worker permission routing.

This skill owns approval architecture for coding agents. For general hooks or callback automation, use [`../agents-hooks/SKILL.md`](../agents-hooks/SKILL.md).

## ASCII Flow

```text
tool/action request
  |
  v
permission context
  mode + actor + sandbox + tool + path + remote/local + worker role
  |
  v
policy route
  allowlist | ask rule | deny rule | managed policy | plan-mode gate
  |
  v
decision
  allow -> execute
  ask   -> prompt owner or lead session
  deny  -> return structured refusal
  log   -> trace permission reason
```

## Quick Reference

| Question | Read | Outcome |
|----------|------|---------|
| How should permission state live in the runtime? | [`references/permission-runtime-model.md`](references/permission-runtime-model.md) | Central permission context, mode handling, and host-owned rules |
| How do local, remote, and swarm approvals differ? | [`references/permission-routing-local-remote-and-worker.md`](references/permission-routing-local-remote-and-worker.md) | Approval flows for REPL, remote sessions, and leader-worker teams |
| How does OpenAI Codex model split filesystem policy and `request_permissions`? | [`references/openai-codex-request-permissions-and-split-policy.md`](references/openai-codex-request-permissions-and-split-policy.md) | Read/write/deny entries, protected metadata, scoped permission grants, and sandbox-vs-approval separation |
| How does OpenAI Codex structure executable policy and network egress policy? | [`references/openai-codex-execpolicy-and-network-proxy.md`](references/openai-codex-execpolicy-and-network-proxy.md) | Prefix-rule evaluation, strictest-decision wins, structured justifications, network deny precedence, and local binding controls |

## When To Use

- Design a permission model for a coding-agent CLI or runtime
- Add tool approval prompts, ask/allow/deny rules, or sandbox escalation
- Model plan-mode entry and exit as part of the permission system
- Route worker approvals through a lead agent or remote bridge
- Decide what background agents should auto-deny instead of prompting for

## Use Other Skills

| Need | Use Instead |
|------|-------------|
| Hook automation and lifecycle callbacks | [`../agents-hooks/SKILL.md`](../agents-hooks/SKILL.md) |
| Plugin trust and install-time capability boundaries | [`../ai-coding-agents-plugins/SKILL.md`](../ai-coding-agents-plugins/SKILL.md) |
| Session resume and transcript recovery | [`../ai-coding-agents-sessions/SKILL.md`](../ai-coding-agents-sessions/SKILL.md) |
| Multi-agent worker coordination | [`../agents-swarm-orchestration/SKILL.md`](../agents-swarm-orchestration/SKILL.md) |
| Full settings-source precedence, managed policy layering, env controls | [`../ai-coding-agents-settings-policy/SKILL.md`](../ai-coding-agents-settings-policy/SKILL.md) |

## Default Workflow

1. **Model permission as runtime state, not scattered booleans.** Keep a single host-owned permission context with mode, rule sources, and special-case flags.
2. **Separate policy layers.** Distinguish always-allow, always-deny, always-ask, org policy, and session-local overrides.
3. **Define promptability.** Background workers, headless sessions, or remote viewers may need auto-deny or delegated approval instead of local dialogs.
4. **Treat plan mode as a permission transition.** Entering or exiting plan mode should preserve the prior mode so the runtime can safely restore it.
5. **Route approvals by execution topology.** Local REPL, remote session, and swarm worker flows should share semantics but not transport.
6. **Keep pending approvals as first-class runtime objects.** Prompt IDs, tool-use IDs, cancellation state, and approval outcomes should be tracked explicitly so remote cancellation and reconnect behavior cannot desynchronize the UI.
7. **Bridge remote requests into local renderables.** Remote approval prompts may reference tools unknown to the local client; normalize them through synthetic assistant messages or tool stubs so the UI can still explain what is being approved.
8. **Keep tool-specific rendering separate from host policy.** A tool can explain its request, but the host decides how approval is enforced and remembered.
9. **Lint persisted rules.** Detect unreachable or shadowed allow rules before they enter the active policy set.
10. **Test hostile paths.** Verify denied prompts, cancelled prompts, remote unknown-tool approvals, worker poll timeouts, bypass-mode restrictions, and over-broad shell rules.

## Host Rules

- Keep one canonical permission context for the session.
- Let tools contribute request detail, not the final allow/deny policy.
- Background agents that cannot show UI should auto-deny or escalate to a controller instead of hanging.
- Await automated checks before showing dialogs when coordinator workers depend on classifier or hook output.
- Remote and worker approval flows should return structured approval results, not implicit UI side effects.
- Permission prompts should have stable request IDs and explicit cancellation behavior.
- Unknown remote tools should still be approvable through synthetic local rendering paths rather than becoming unrenderable errors.
- Over-broad persisted shell rules should be sanitized or refused before they are admitted into the active permission context.
- Record enough metadata to explain why a request was allowed, denied, or never prompted.
- Shared policy sources and personal policy sources may need different sanitization or auto-allow behavior. Preserve source class through evaluation.

## Build Order

1. Define one canonical permission context for the host runtime.
2. Model permission modes and rule sources explicitly.
3. Implement request IDs, approval results, and cancellation semantics.
4. Route approval by topology: local, remote, worker, or non-interactive.
5. Add persistence or session-local memory for approved rules.
6. Add sanitization and shadowed-rule detection for dangerous or over-broad rule proposals.
7. Add source-aware handling for shared versus personal policy layers.

## Core Invariants

- The host owns allow, deny, ask, and persistence policy.
- Tools describe requests; they do not decide approval policy.
- Non-interactive actors must never hang waiting for a prompt they cannot answer.
- Every prompt must end in exactly one terminal outcome: approved, denied, cancelled, or expired.
- Plan mode is a reversible permission transition, not a separate permission system.
- Persisted rules must be linted for reachability and dangerous breadth before activation.

## Failure Modes

- Prompt IDs that cannot be matched to cancellations or late results.
- Remote approvals that reference unknown tools and therefore become unrenderable.
- Persisted shell rules that silently become broader than intended.
- Workers blocking forever while waiting for interactive approval.
- Plan-mode exit failing to restore the preexisting permission state.
- Lower-precedence allow rules that are unreachable because an earlier ask or deny rule shadows them.

## Minimal Viable Version

- One session-owned permission context.
- Explicit ask, allow, and deny modes.
- Stable IDs for prompts and approval results.
- Auto-deny for non-interactive workers.
- One sanitization or lint pass over persisted rules before activation.
- Approval metadata that explains why a request was allowed or denied.

## What Strong Implementations Add

- Policy layering across org, repo, session, and ephemeral overrides.
- Automated checks before prompting the user.
- Synthetic local rendering for remote approval prompts.
- Cancellation, expiry, and retry-safe bookkeeping.
- Rule sanitization and explainability for persisted approvals.
- Shadowed-rule detection and source-aware behavior differences for shared versus personal policy layers.

## Known Traps

- Letting multiple subsystems infer approval state independently and then diverge between the runtime, UI, and stored policy.
- Persisting shell-prefix approvals without enough narrowing to prevent future privilege creep.
- Treating remote approval as a rendering problem instead of a durable runtime object with expiry, cancellation, and retry semantics.
- Recording “prompt shown” as if it were equivalent to a valid approval outcome.
- Allowing tools or plugins to own their own approval policy and bypass central auditability.

## Common Anti-Patterns

- Storing approval mode as scattered booleans instead of one context object.
- Letting tools persist their own approval policy.
- Treating remote approval as a UI problem instead of a runtime-routing problem.
- Persisting arbitrary shell prefixes without narrowing or review.
- Assuming every stored allow rule is reachable and therefore useful.
- Assuming a prompt that was shown always receives a valid response.

## Claude Code: Permission Modes Quick Reference (2026)

Six named modes are the complete enumeration. All are set via `--permission-mode <mode>`, the `defaultMode` settings key, or `permissionMode` in subagent frontmatter. As of v2.1.200, `default` is labeled **Manual** in the CLI, `--help`, and the VS Code/JetBrains extensions, and `manual`/`"manual"` is accepted as an alias for `default` everywhere the mode is configured — treat `default` and `manual` as the same mode when writing tooling against it.

| Mode | What runs without prompting | Key notes |
|------|----------------------------|-----------|
| `default` (aka Manual, v2.1.200+) | Reads only | Starting mode; Shift+Tab cycles default → acceptEdits → plan |
| `acceptEdits` | Reads, file edits, common filesystem commands | Auto-approves edits in working directory only; never auto-approves [protected-path](#protected-paths) writes |
| `plan` | Reads only | Research without writing; exit via Shift+Tab or plan approval |
| `auto` | Everything except protected-path writes, with background classifier checks | v2.1.83+ required; protected-path writes route to the classifier, not auto-approval; see below |
| `dontAsk` | Only pre-approved tools (allow-list only) | Named headless auto-deny mode; for CI/locked environments; never appears in Shift+Tab cycle; protected-path writes are denied outright |
| `bypassPermissions` | Everything, no classifier, including protected-path writes | Isolated containers/VMs only; never appears in default cycle; explicit `ask` rules and `rm -rf /` / `rm -rf ~` still prompt as a circuit breaker |

**Shift+Tab cycle**: default → acceptEdits → plan. Optional modes slot in after plan: `bypassPermissions` first (if started with `--permission-mode bypassPermissions` or `--allow-dangerously-skip-permissions`), then `auto` last (if eligible). `dontAsk` never appears in the cycle.

### Protected paths

A small set of paths (`.git`, `.config/git`, `.vscode`, `.idea`, `.husky`, `.cargo`, `.devcontainer`, `.yarn`, `.mvn`, `.claude` except `.claude/worktrees`, plus files like `.gitconfig`, shell rc files, and package-manager rc files) are never auto-approved in any mode except `bypassPermissions`, and the check runs *before* `permissions.allow` rules are evaluated — an `Edit(.claude/**)` allow rule does not change this. This is the pattern to copy for any runtime: repository metadata and the agent's own config directory should have a hard-coded carveout that ordinary allow rules cannot reach, independent of mode.

**`auto` mode** — model-classifier approval system:
- A server-configured classifier model (independent of the session's `/model` selection) evaluates each action before execution; do not hard-pin a specific classifier model name in downstream tooling — it can change without a version bump to the mode's behavior.
- Two-stage: fast single-token filter, then chain-of-thought on flagged actions
- Classifier sees user messages, tool calls, and CLAUDE.md content; tool *results* are stripped and separately scanned for injected instructions
- Decision order: allow/deny rules resolve first (except protected-path writes, which always route to the classifier) → read-only/in-directory edits auto-approve → everything else hits the classifier
- On entering `auto`, broad allow rules (`Bash(*)`, `PowerShell(*)`, wildcarded interpreters, package-manager run commands, `Agent` allow rules) are dropped and restored on exit; narrow rules like `Bash(npm test)` carry over
- If the classifier blocks 3 consecutive times or 20 total times, auto mode pauses and prompting resumes; in non-interactive (`-p`) mode there is no user to prompt, so the run aborts instead
- Eligibility (plan tier, minimum model, provider) is gated per-provider and changes over time — verify current gating in `/en/permission-modes` at ship time rather than trusting a cached list
- **Trap:** `defaultMode: "auto"` set in `.claude/settings.json` or `.claude/settings.local.json` is silently ignored (v2.1.142+) so a repository cannot grant itself auto mode; it must be set in user (`~/.claude/settings.json`) or managed settings
- `permissionMode: auto` in subagent frontmatter is ignored when the parent is in auto mode — the parent's auto mode applies to all subagent actions, checked at three points: before spawn (task description), during execution (each action), and after completion (a full-history review that can prepend a security warning to the result, v2.1.178+)
- Plugin subagents cannot set `permissionMode`
- `disableAutoMode: "disable"` in managed settings removes auto from the Shift+Tab cycle and rejects `--permission-mode auto`
- Source: `code.claude.com/docs/en/permission-modes` and `anthropic.com/engineering/claude-code-auto-mode`

**`dontAsk` mode** — named headless auto-deny: every tool call that would normally prompt is auto-denied; only `allow`-rule-matched tools and read-only Bash commands execute, and an MCP tool marked `requiresUserInteraction` is denied even when an allow rule matches it (its consent card needs an answer this mode never collects). This is the correct mode for CI scripts that must not hang waiting for approval.

**Background subagents and the "auto-deny vs. escalate" judgment call**: prior to v2.1.186, a background subagent that hit a tool call requiring approval was auto-denied outright, because the main session had no way to interrupt it — subagents got stuck in silent denial loops. Since v2.1.186, the denied-by-default call instead surfaces as a prompt in the parent/main session, labeled with the subagent's name; the parent can approve or deny that single call without stopping the subagent. Treat this as the reference pattern for this skill's own "promptability" principle: **auto-deny is the correct answer only when no controller exists to escalate to.** When a background or worker context has any reachable parent/leader session, route the pending approval there as a first-class object (see [Permission Runtime Model](references/permission-runtime-model.md)) rather than defaulting to silent denial.

**Inheritance rules**: a parent session in `auto` overrides any `permissionMode` set in subagent frontmatter. Plugin-shipped agents are additionally restricted: `hooks`, `mcpServers`, and `permissionMode` fields in plugin agent definitions are silently ignored by the runtime.

### Rule syntax an expert checks first

- **Evaluation order is fixed, not precedence-weighted**: deny, then ask, then allow — first match wins regardless of specificity. A broad `Bash(aws *)` deny still blocks a narrower `Bash(aws s3 ls)` allow; there is no allowlist-exception mechanism inside a deny rule.
- **Parameter-matching rules** (`Tool(param:value)`, v2.1.178+) let deny/ask rules gate on any top-level scalar input field, e.g. `Agent(model:opus)` or `Agent(isolation:worktree)` or `Bash(run_in_background:true)`. This is distinct from — and composes with — the older `Agent(AgentName)` subagent-identity rule. Fields a tool already canonicalizes (`command` for Bash, `file_path` for Read/Edit/Write) are excluded from this path and must use the tool's own specifier syntax; a `Bash(command:rm *)` rule is silently ignored with a startup warning because it would be bypassable by a compound command.
- **Path-anchor bugs are the most common review finding**: `//path` is filesystem-absolute; `/path` is relative to *the settings file that defines the rule*, not the project root or the CLI's cwd. A `Read(/secrets/**)` deny written into `~/.claude/settings.json` blocks `~/.claude/secrets/**`, not a project's `secrets/` directory — reviewers should flag every single-leading-slash path rule in user settings as a likely mistake.
- **Symlinks split allow/deny asymmetrically**: allow rules require both the symlink path *and* its resolved target to match (otherwise it falls back to prompting); deny rules fire if *either* the symlink path or the target matches. A symlink into an allowed directory pointing outside it is not auto-approved by that fact alone.
- **Hooks are best-effort, not enforcement**: a `PreToolUse` hook's `if` field scopes it with permission-rule syntax (e.g. `if: "Bash(rm *)"`), but the filter fails open — if the Bash command can't be parsed, the hook runs anyway. Deny/ask permission rules are evaluated independently of what a hook returns, so a hook cannot be the sole enforcement point for a hard boundary; it can add checks, not replace deny/ask rules. See [`../agents-hooks/SKILL.md`](../agents-hooks/SKILL.md) for hook event and matcher design.

### Settings precedence, briefly (permission-audit nuance only)

Full precedence chain — **managed settings > CLI arguments > local project (`.claude/settings.local.json`) > shared project (`.claude/settings.json`) > user (`~/.claude/settings.json`)** — is [`../ai-coding-agents-settings-policy/SKILL.md`](../ai-coding-agents-settings-policy/SKILL.md)'s territory; use it for full source layering and managed-policy design.

The one nuance load-bearing for a *permission* audit: that precedence order governs plain settings (e.g. `spinnerTipsEnabled`), but permission rules do not simply follow "higher scope wins." **A deny rule from any scope blocks the action regardless of scope precedence** — a user-level deny blocks a project-level allow and a project-level deny blocks a user-level allow, because deny is evaluated before allow at every scope and rules merge across scopes rather than one file overriding another wholesale. Do not assume "project settings win over user settings" applies to allow-vs-deny conflicts — check which rule is a deny before applying the file-precedence mental model.

## OpenAI Codex: `AskForApproval` Policy Enum

Source: live `codex-rs/protocol/src/protocol.rs` (`main` branch, re-verified July 2026) — re-check before shipping, since Codex's config surface has changed shape twice within a few months.

TOML key: `approval_policy` (type `Option<AskForApproval>`, in the top-level `[config]` section of `~/.codex/config.toml`)

| Variant | TOML value | Behavior |
|---------|-----------|---------|
| `UnlessTrusted` | `"untrusted"` | Auto-approves only commands `is_safe_command()` judges "known safe" and read-only; asks for everything else |
| `OnRequest` | `"on-request"` (also accepts legacy `"on-failure"` as a deserialization alias) | **Default.** The model decides when to ask for approval |
| `Granular(GranularApprovalConfig)` | `"granular"` + sub-keys | Fine-grained per-category control: `sandbox_approval`, `rules` (execpolicy `prompt` rules), `skill_approval`, `request_permissions`, `mcp_elicitations` |
| `Never` | `"never"` | Never submits commands for approval; failures returned immediately to the model |

**Correction from an earlier snapshot of this skill:** a prior pinned-commit source (2026-05-22) showed `UnlessTrusted` serializing as `"unless-trusted"` and a separate deprecated `OnFailure` variant ("all commands auto-approved, rely on the sandbox"). The live source now serializes `UnlessTrusted` as `"untrusted"`, and `OnFailure` is gone as a distinct variant — `"on-failure"` is now only a backward-compatible TOML alias that deserializes into `OnRequest`, so a config still carrying `approval_policy = "on-failure"` gets `OnRequest` behavior, not the old always-auto-approve behavior. Treat this as a general lesson, not just a one-time fix: **pinned-commit citations for a fast-moving CLI's config surface expire faster than the rest of this skill; re-fetch the live source (or current config-reference docs) before trusting an enum-value table, and prefer `on-request`/`never` explicitly over relying on the `on-failure` alias.**

`GranularApprovalConfig` lets operators selectively enable or suppress approval prompts per action class, allowing a policy like "always ask for MCP tool calls, never ask for skill-script approval."

Design rule: treat `AskForApproval` as the canonical approval-mode type when implementing Codex-compatible runtimes — do not invent a parallel enum. Do not write new code that branches on a standalone `on-failure` semantic; it is an alias, not a policy.

## Cross-Platform Patterns (Goose)

Goose exposes two approval surfaces the current skill does not model: **identity-aware approvals via an OIDC proxy**, and **ACP-bridged approvals** where approvals must round-trip across a stdio boundary to a delegating agent.

### Identity-aware approvals (OIDC proxy)

Goose ships an `oidc-proxy/` crate that bridges agent calls to external providers through an OIDC-authenticated proxy. Approvals tied to external side-effects (deploy, merge, paid API use) can be gated on the authenticated identity, not just on "the user accepted a local prompt."

- **Pattern:** treat user identity as a permission-context field alongside mode and rule sources. Certain rule classes (destructive-on-prod, financial, third-party) can require fresh auth proof, not just a prior local allow.
- **Anti-pattern:** assuming the OS user running the CLI is the authorization principal for remote/side-effecting approvals. Shared dev machines, CI agents, and teammate-session handoff all break that assumption.
- **Recipe:** add an optional `auth_proof` field to the permission context; rules can declare `require_fresh_auth: true`. For those, every N minutes or per-call, the host demands re-authentication via OIDC proxy. Record the identity with the approval outcome for audit.

### ACP-bridged approvals

When a session delegates work to an external ACP agent (see `ai-coding-agents-remote-runtime` agent-delegating mode, and `ai-coding-agents-provider-runtime` agent-as-provider), tool approvals requested by the delegated agent must round-trip back to the orchestrator's local UI. The skill's current worker-routing model assumes same-process workers.

- **Pattern:** approvals raised by an ACP-delegated agent travel back through the ACP control channel, are materialized as a pending approval object in the orchestrator, rendered in the orchestrator's UI, resolved locally, and the outcome is sent back through ACP to the delegated agent. Stable request IDs are required end-to-end.
- **Anti-pattern:** auto-approving everything from a "trusted" delegated agent. ACP does not bound the delegated agent's tool use; without round-trip approval, the orchestrator loses audit and policy.
- **Recipe:** add a third routing leg in the permission-routing reference: **orchestrator ↔ ACP-delegated agent**. The delegated agent's approval requests are first-class runtime objects in the orchestrator's permission context, with stable IDs, cancellation support, and cross-process cancellation on session death.

## Navigation

### References

- [`references/permission-runtime-model.md`](references/permission-runtime-model.md) — Central permission context, plan-mode restore, and host-owned rule layers
- [`references/permission-routing-local-remote-and-worker.md`](references/permission-routing-local-remote-and-worker.md) — Approval flows for REPL, remote sessions, and swarm workers
- [`references/openai-codex-request-permissions-and-split-policy.md`](references/openai-codex-request-permissions-and-split-policy.md) — OpenAI Codex split filesystem policy, protected metadata, `request_permissions`, and hostile-case tests
- [`references/openai-codex-execpolicy-and-network-proxy.md`](references/openai-codex-execpolicy-and-network-proxy.md) — OpenAI Codex executable policy engine and network proxy boundary patterns
- [`references/hostile-path-test-checklist.md`](references/hostile-path-test-checklist.md) — Adversarial path, symlink, and containment cases for permission-boundary tests

### Data

- [`data/sources.json`](data/sources.json) — Primary documentation and source references for approval-system design

### Related Skills

- [`../agents-hooks/SKILL.md`](../agents-hooks/SKILL.md)
- [`../agents-swarm-orchestration/SKILL.md`](../agents-swarm-orchestration/SKILL.md)
- [`../ai-coding-agents-plugins/SKILL.md`](../ai-coding-agents-plugins/SKILL.md)

## Fact-Checking

- Known bugs, regressions, framework/compiler/runtime footguns, and version-specific crash or workaround guidance must be verified against current primary web sources before being treated as current fact.
- The patterns here are grounded in a local April 2026 `claude_code` source snapshot. Verify current permission field names, event names, and remote control schemas before shipping.
- Approval UX and sandbox semantics are runtime-specific. Preserve the architecture patterns, but re-check exact prompt behavior for the target client.

## Learnings Loop

Before applying this skill on a non-trivial task, read `learnings.consolidated.md` in this directory (and `learnings.md` if present).

After applying it, if you encountered a pattern worth remembering, a mistake worth preventing, or a domain fact that surprised you, append one dated bullet to `learnings.md` via `agents-skills-feedback-loop/scripts/append_learning.py`. Do not modify `SKILL.md` itself.
