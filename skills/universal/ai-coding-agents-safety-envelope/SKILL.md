---
name: ai-coding-agents-safety-envelope
description: "Designs approval and sandbox policy for local coding agents: permission modes, isolation, network and destructive-command guards. Use when setting approvals. Not cloud sandboxes."
compatibility: Portable core. Works on Claude Code and Codex.
version: "2.0"
last_validated: 2026-09-29
---

# AI Coding Agents Safety Envelope

Use this skill to design or review the two layers that bound what a coding agent may do: the **approval system** (who decides: permission modes, rule sources, plan-mode transitions, prompt routing, leader-worker handoff) and the **execution sandbox** (what is reachable: process isolation, filesystem mounts, network policy, environment exposure, destructive-command controls).

Approval policy decides who decides; the sandbox decides what is reachable. Neither substitutes for the other, and both are defined here so their interaction (auto-allow inside the boundary, escalation at its edge, worker envelopes) is designed once.

This skill does not own remote execution or managed cloud sandboxes (`ai-coding-agents-cloud-sandboxes`), hook automation ([`../agents-hooks/SKILL.md`](../agents-hooks/SKILL.md)), full settings-source layering and managed policy ([`../ai-coding-agents-settings-policy/SKILL.md`](../ai-coding-agents-settings-policy/SKILL.md)), plugin trust ([`../ai-coding-agents-plugins/SKILL.md`](../ai-coding-agents-plugins/SKILL.md)), or the tool execution pipeline ([`../ai-coding-agents-runtime-core/SKILL.md`](../ai-coding-agents-runtime-core/SKILL.md)).

## Quick Reference

| Question | Read | Outcome |
|----------|------|---------|
| How should permission state live in the runtime? | [references/permission-runtime-model.md](references/permission-runtime-model.md) | Central permission context, mode handling, plan-mode restore, host-owned rules |
| How do local, remote, and worker approvals differ? | [references/permission-routing-local-remote-and-worker.md](references/permission-routing-local-remote-and-worker.md) | Approval flows for REPL, remote sessions, and leader-worker teams |
| Which vendor modes, rule syntax, and precedence traps does an audit check first? | [references/reference-runtime-permission-modes-and-rule-syntax.md](references/reference-runtime-permission-modes-and-rule-syntax.md) | Mode ladder, protected paths, deny > ask > allow, path anchors, symlinks, hook limits |
| How does OpenAI Codex model split filesystem policy and `request_permissions`? | [references/openai-codex-request-permissions-and-split-policy.md](references/openai-codex-request-permissions-and-split-policy.md) | Read/write/deny entries, protected metadata, scoped grants |
| How does OpenAI Codex structure exec policy and network egress? | [references/openai-codex-execpolicy-and-network-proxy.md](references/openai-codex-execpolicy-and-network-proxy.md) | Prefix rules, strictest-decision wins, network deny precedence |
| How should process, filesystem, and workspace isolation work? | [references/sandbox-process-and-filesystem-model.md](references/sandbox-process-and-filesystem-model.md) | Execution modes, mounts, working directories, write boundaries |
| How should network, approvals, and destructive actions be controlled? | [references/network-approval-and-destructive-action-guards.md](references/network-approval-and-destructive-action-guards.md) | Outbound policy, command classes, escalation triggers |
| What sandbox mode names and backend split does Codex use? | [references/openai-codex-sandbox-guardrails-may-2026.md](references/openai-codex-sandbox-guardrails-may-2026.md) | Mode names, platform backends, fail-closed translation, telemetry |
| What does a shipping subprocess sandbox enforce, and where does its scope end? | [references/claude-code-bash-sandbox-mechanics.md](references/claude-code-bash-sandbox-mechanics.md) | Read/write asymmetry, credential deny-vs-mask, TLS-blind allowlists, tool-scope limits |
| What is the canonical sandbox policy format? | [references/sandbox-policy-format.md](references/sandbox-policy-format.md) | Runtime-agnostic policy fields, traps, translation notes |
| How do I verify the permission boundary and sandbox before shipping? | [references/hostile-path-test-checklist.md](references/hostile-path-test-checklist.md), [references/escape-path-test-matrix.md](references/escape-path-test-matrix.md) | Path, symlink, interpreter-wrapper, env-injection, package-manager escape tests |
| Identity-aware or ACP-bridged approvals, build-time gates, distro allowlists? | [references/goose-approval-and-distribution-layer-patterns.md](references/goose-approval-and-distribution-layer-patterns.md) | Cross-platform patterns beyond the local REPL |

A JSON schema for the permission context is in [assets/templates/permission-context.schema.json](assets/templates/permission-context.schema.json).

## When To Use

- Design a permission model, approval prompts, ask/allow/deny rules, or sandbox escalation
- Model plan-mode entry and exit as a permission transition
- Route worker or remote approvals through a lead agent or bridge; decide what background agents auto-deny
- Define execution modes, mounts, network policy, env-var exposure, or destructive-command classes
- Review how worker or teammate sandboxes inherit or narrow the launcher's envelope
- Audit an over-permissive local setup, or verify a sandbox holds before shipping it

## Use Other Skills

| Need | Use Instead |
|------|-------------|
| Managed sandbox providers, ephemeral cloud workspaces, egress across a network boundary, cost per task | `ai-coding-agents-cloud-sandboxes` |
| Hook automation and lifecycle callbacks | [`../agents-hooks/SKILL.md`](../agents-hooks/SKILL.md) |
| Plugin trust and install-time capability boundaries | [`../ai-coding-agents-plugins/SKILL.md`](../ai-coding-agents-plugins/SKILL.md) |
| Settings-source precedence, managed policy layering, env controls | [`../ai-coding-agents-settings-policy/SKILL.md`](../ai-coding-agents-settings-policy/SKILL.md) |
| Remote bridge transport and local-UI remote execution | [`../ai-coding-agents-surfaces/SKILL.md`](../ai-coding-agents-surfaces/SKILL.md) |
| Tool contract and execution pipeline | [`../ai-coding-agents-runtime-core/SKILL.md`](../ai-coding-agents-runtime-core/SKILL.md) |
| Multi-agent worker coordination | [`../agents-swarm-orchestration/SKILL.md`](../agents-swarm-orchestration/SKILL.md) |
| Prompt-budget metrics | [`../ai-coding-agents-observability-evals/SKILL.md`](../ai-coding-agents-observability-evals/SKILL.md) |

## Approval Policy vs Sandbox

Sandbox mode is not approval mode: they are related but not identical, and each needs its own enum.

- Look up the current approval values in the vendor config reference before writing config; a retired value can prevent startup. Write explicit current values, never branch code on a backward-compatible alias as if it were its own policy, and never invent a parallel enum.
- A per-category (granular) approval setting may auto-reject a category rather than prompt for it; check what each category does when it is not enabled.
- An approval prompt is not isolation; a sandbox is not consent. Keep a prompt from being read as a boundary and a boundary from being read as authorization.
- Move a command class that is over prompt budget into the sandbox (auto-allow inside the boundary) instead of widening allow rules.

## Approval Workflow

1. **Model permission as runtime state.** One host-owned permission context with mode, rule sources, and special-case flags, not scattered booleans.
2. **Separate policy layers:** always-allow, always-deny, always-ask, org policy, session-local overrides. Preserve source class through evaluation; shared and personal sources may need different sanitization.
3. **Define promptability.** Background workers, headless sessions, and remote viewers need auto-deny or delegated approval instead of local dialogs. Auto-deny only when no controller exists; otherwise surface the request in the parent session, labeled with the subagent.
4. **Treat plan mode as a reversible permission transition** that preserves the prior mode.
5. **Route approvals by topology** (local REPL, remote, swarm worker, ACP-delegated) with shared semantics but separate transport.
6. **Keep pending approvals as first-class objects** with prompt ID, tool-use ID, cancellation state, and exactly one terminal outcome (approved, denied, cancelled, expired). "Prompt shown" is not an outcome.
7. **Bridge unknown remote tools** into local renderables (synthetic messages or stubs) so the user can still see what is being approved. Tools describe requests; the host decides enforcement and persistence.
8. **Lint and scrub persisted rules.** Detect unreachable or shadowed allows, refuse over-broad shell prefixes, and reject any rule that matches a secret shape (an "always allow" click can persist auth headers); rotate any token found in a rules file.
9. **Preserve authorization scope.** Bind a decision to the concrete action, target, actor, and session or policy scope. An agent-to-agent message is not consent, and do not discard still-applicable user authorization merely because time passed unless policy defines expiry.
10. **Budget prompts.** Track prompts per session and the share approved within seconds; prompt fatigue drives users to bypass modes.
11. **Audit the mode before the rules.** In a bypass mode the allow, ask, and deny lists may enforce nothing, and a blanket allow that matches before classification switches the classifier off for that surface. Deny beats allow at every scope; see the rule-syntax reference.

## Sandbox Workflow

1. **Define execution modes** (read-only, workspace-write, unrestricted, remote-bridged, worker-reduced) with trust levels.
2. **Set the mount model:** readable, writable, hidden, remapped. Canonical path and symlink resolution are part of the boundary; permission-rule path semantics and substrate mount semantics are separate resolvers.
3. **Control process spawning** with allowlists enforced by a mechanism that can see paths (an LSM such as Landlock, AppArmor, or Seatbelt, seccomp user-notify, ptrace, or a `noexec` mount plus one executable bin root). Plain seccomp filters cannot allowlist executables by path.
4. **Separate network policy** from filesystem policy. A hostname allowlist is connectivity policy, not content inspection, unless the proxy terminates TLS; otherwise domain fronting is an exfiltration path.
5. **Make environment and secret exposure opt-in.** A sandbox that restricts only writes and still reads `~/.ssh` or cloud credentials is not a secrets boundary.
6. **Classify destructive actions** (delete, reset, force-push, privileged) with stricter rules, evaluated against the subprocess tree, not the top-level command.
7. **Protect privileged config surfaces** (settings, policy, skill directories, repository metadata) even when the workspace is writable.
8. **Compute the worker envelope:** intersect the launcher envelope, worker policy, runtime defaults, mounted roots, network policy, and any fresh approval. A narrower worker definition does not by itself narrow child capability; compare with the launcher's envelope before dispatch and block or surface any widening.
9. **Scope the sandbox to the tool classes it covers.** Shipping subprocess sandboxes restrict subprocess execution but leave file-edit, fetch, and computer-use calls to the permission system; "the agent is sandboxed" is a category error unless it names the tool surface.
10. **A declared policy is not an enforced policy.** Record which component enforces each field (kernel backend, proxy, or nothing) and keep a fail-closed test that proves the backend applied it. Domain rules with no active proxy, or a missing backend dependency that falls back to unsandboxed execution, are the same failure.
11. **Test escape paths:** symlinks, traversal, shell expansion, wrapper binaries, env indirection, package-manager helpers.

## Host Rules

- The host owns allow, deny, ask, and persistence policy; one canonical permission context per session.
- Apply policy before execution, not after output returns; the boundary must exist in the execution substrate, not in prompts.
- Filesystem, network, and environment are separate control planes. Default to a conservative sandbox and escalate only when justified.
- Prompts need stable request IDs and explicit cancellation. Record why a request was allowed, denied, or never prompted. Remote and worker flows return structured results, not implicit UI side effects.
- Non-interactive actors never hang waiting for a prompt they cannot answer.
- Await automated checks (classifier, hook output) before showing dialogs when coordinator workers depend on them.
- A deny from any scope blocks the action; do not assume "higher scope wins" applies to allow-versus-deny conflicts.
- Registering a compatibility escape hatch (Apple Events, a weaker-isolation flag, an unelevated backend) must record what guarantee it removes for every later command in the session. A Unix domain socket exception such as a container runtime control socket can equal full host access.

## Unfamiliar Repositories

- A headless `claude -p` run shows neither the workspace-trust dialog nor the approval prompt for a project's `.mcp.json` servers (Claude Code security docs, "Trust verification"). Read the repository's committed config and `.mcp.json` before the first headless run, or pass `--strict-mcp-config` with your own `--mcp-config` so only servers you named load.
- `--bare` skips auto-discovery of hooks and MCP servers, so it removes your own guard hooks along with the repository's. Do not use it as a trust measure unless the guard lives somewhere the flag does not skip.
- For a repository you do not trust, run the agent in a container with no network and only that repository mounted. A host mount of anything else, or a container runtime socket, defeats the boundary.

Source idea: ECC `the-security-guide.md` (MIT), adapted.

## Build Order

1. One canonical permission context; modes and rule sources explicit.
2. Request IDs, approval results, cancellation and expiry semantics.
3. Execution modes, canonical path resolution, and mount policy.
4. Process and interpreter allowlists; network policy and exceptions; env and secret filtering.
5. Protected config surfaces and destructive-command classification with escalation hooks.
6. Approval routing by topology; worker-envelope computation.
7. Persistence or session-local memory for approved rules, with sanitization, shadow detection, and source-aware handling.
8. Escape-path and hostile-path tests before shipping.

## Core Invariants

- Tools describe requests; the host decides. Every prompt ends in exactly one terminal outcome.
- Plan mode is a reversible transition, not a separate permission system.
- No persisted rule contains a credential; persisted rules are linted for reachability and breadth before activation.
- Worker capability is the computed effective envelope; inheritance defaults are runtime-specific and must be verified.
- Destructive capability is never implied by tool name or user intent alone.
- Privileged config surfaces stay protected even when ordinary workspace edits are allowed.

## Failure Modes

- Prompt IDs that cannot be matched to cancellations or late results; workers blocking on a prompt they cannot answer; plan-mode exit not restoring prior state.
- Remote approvals for unknown tools that become unrenderable; approval state inferred independently by runtime, UI, and stored policy.
- Persisted shell rules broader than intended; allow rules shadowed by an earlier ask or deny.
- Symlink or traversal writes escaping the workspace; wrapper tools or package-manager helpers bypassing interpreter and network policy.
- Child workers silently inheriting a parent's unrestricted mode; secrets leaking through inherited environments.
- Workspace-write modes that allow mutation of policy or skill roots; approval prompts treated as the sandbox.
- Package installs, build tools, and test runners writing outside obvious workspace paths because mounts and temp policy were not explicit.
- Tools or plugins owning their own approval policy and bypassing central auditability.

## Minimal Viable Version

- One session-owned permission context with explicit ask, allow, and deny modes; stable IDs; auto-deny for non-interactive workers.
- One conservative default sandbox mode with canonical readable and writable roots, one subprocess allowlist, one network policy, one protected-config list.
- One lint pass over persisted rules and one escalation path for destructive or restricted actions, with approval metadata that explains outcomes.

## What Strong Implementations Add

- Policy layering across org, repo, session, and ephemeral overrides; source-aware shared-versus-personal handling.
- Worker-specific narrowed envelopes, host-specific mount remapping and temp-space policy.
- Automated checks before prompting; synthetic rendering for remote prompts; cancellation, expiry, and retry-safe bookkeeping.
- Auditable destructive-command classes with justifications; package-manager exception handling.
- Escape-path tests for symlinks, shell expansion, wrapper binaries, and env indirection; identity-aware approvals for external side effects.

## Navigation

### References

All files under [`references/`](references/) are listed in the Quick Reference table above.

### Templates

- [assets/templates/permission-context.schema.json](assets/templates/permission-context.schema.json) — Permission context schema

### Data

- [`data/sources.json`](data/sources.json) — Primary documentation and source references for approval and sandbox design

### Related Skills

- [`../agents-hooks/SKILL.md`](../agents-hooks/SKILL.md)
- [`../agents-swarm-orchestration/SKILL.md`](../agents-swarm-orchestration/SKILL.md)
- [`../ai-coding-agents-plugins/SKILL.md`](../ai-coding-agents-plugins/SKILL.md)
- [`../ai-coding-agents-surfaces/SKILL.md`](../ai-coding-agents-surfaces/SKILL.md)
- [`../ai-coding-agents-runtime-core/SKILL.md`](../ai-coding-agents-runtime-core/SKILL.md)

## Learnings Loop

When prior decisions or pitfalls are relevant, consult `learnings.consolidated.md` if present; use `learnings.md` only for needed history or as the available fallback. Otherwise skip both.

After applying it, if you encountered a pattern worth remembering, a mistake worth preventing, or a domain fact that surprised you, append one dated bullet to `learnings.md` via `agents-skills-feedback-loop/scripts/append_learning.py`. Do not modify `SKILL.md` itself.
