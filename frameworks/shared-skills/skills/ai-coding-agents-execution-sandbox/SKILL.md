---
name: ai-coding-agents-execution-sandbox
description: "Designs execution sandboxes for coding agents. Use when modeling process isolation, filesystem policy, network controls, workspace mounts, or destructive-command boundaries."
compatibility: Portable core. Works on Claude Code and Codex.
version: "1.1"
last_validated: 2026-07-11
---

# AI Coding Agents Execution Sandbox

Use this skill to design or review the execution substrate for a coding-agent runtime: process isolation, filesystem mounts, network policy, workspace boundaries, environment exposure, and destructive-command controls.

This skill covers where and how code runs. It complements permission routing by defining the actual isolation and policy envelope around execution.

## ASCII Flow

```text
requested execution
  |
  v
classify action
  read | write | network | process | destructive | secret-bearing
  |
  v
sandbox policy
  filesystem roots + workspace mounts + env exposure + network policy
  |
  v
decision
  allow in sandbox | ask permission | deny | require safer workspace
  |
  v
run process with bounded cwd, mounts, env, network, and cleanup rules
```

## Quick Reference

| Question | Read | Outcome |
|----------|------|---------|
| How should process, filesystem, and workspace isolation work? | [`references/sandbox-process-and-filesystem-model.md`](references/sandbox-process-and-filesystem-model.md) | Execution modes, mounts, working directories, and write boundaries |
| How should network, approvals, and destructive actions be controlled? | [`references/network-approval-and-destructive-action-guards.md`](references/network-approval-and-destructive-action-guards.md) | Outbound policy, command classes, escalation triggers, and guardrails |
| What sandbox mode names and backend split should runtime builders copy from Codex? | [`references/openai-codex-sandbox-guardrails-may-2026.md`](references/openai-codex-sandbox-guardrails-may-2026.md) | `read-only`/`workspace-write`/`danger-full-access` modes, platform backends, fail-closed policy translation, security telemetry |
| What does a shipping Bash sandbox actually enforce, and where does its scope end? | [`references/claude-code-bash-sandbox-mechanics.md`](references/claude-code-bash-sandbox-mechanics.md) | Read/write asymmetry, credential deny-vs-mask, TLS-blind allowlists, tool-scope limits, known compatibility failures |
| What is the canonical policy format for interpreter allowlists and filesystem/network rules? | [`references/sandbox-policy-format.md`](references/sandbox-policy-format.md) | Runtime-agnostic policy fields, common traps, and translation notes |
| How do I verify a sandbox actually holds before shipping it? | [`references/escape-path-test-matrix.md`](references/escape-path-test-matrix.md) | Symlink, interpreter-wrapper, env-injection, and package-manager escape tests with pass criteria |

## When To Use

- Design execution modes for local or remote coding agents
- Define filesystem write boundaries and workspace mount rules
- Add network restrictions, env-var policy, or secret exposure controls
- Review how destructive commands should be blocked or escalated
- Model how worker or teammate sandboxes should inherit or narrow permissions

## Use Other Skills

| Need | Use Instead |
|------|-------------|
| Approval routing and permission prompts | [`../ai-coding-agents-permissions/SKILL.md`](../ai-coding-agents-permissions/SKILL.md) |
| Remote bridge and local or remote execution model | [`../ai-coding-agents-remote-runtime/SKILL.md`](../ai-coding-agents-remote-runtime/SKILL.md) |
| Tool contract and execution pipeline | [`../ai-coding-agents-tools/SKILL.md`](../ai-coding-agents-tools/SKILL.md) |
| Broader coding-agent architecture | [`../ai-coding-agents/SKILL.md`](../ai-coding-agents/SKILL.md) |

## Default Workflow

1. **Define execution modes.** For example: read-only, workspace-write, unrestricted, remote-bridged, or worker-reduced.
2. **Set the mount model.** Decide which directories are readable, writable, hidden, or remapped.
3. **Control process spawning.** Define which shells, interpreters, and subprocess classes are allowed by default.
4. **Separate network policy.** Outbound access, host allowlists, and package-manager exceptions should be explicit.
5. **Constrain environment exposure.** Make secret inheritance opt-in and scoped to the minimum execution surface.
6. **Classify destructive actions.** Delete, reset, force-push, and privileged commands need stricter rules than normal edits.
7. **Protect privileged config surfaces.** Settings files, policy files, and skill directories should usually be non-writable even when the workspace is otherwise writable.
8. **Narrow worker inheritance.** Child tasks and teammates should inherit the minimum effective envelope, not the widest parent one.
9. **Test escape paths.** Validate symlink tricks, path traversal, shell expansion, and tool-wrapper bypass attempts.

## Host Rules

- Keep sandbox mode distinct from approval mode; they are related but not identical.
- Apply policy before execution, not after output returns.
- Treat path resolution and symlink resolution as part of the security boundary.
- Model network access independently from filesystem access.
- Make the default sandbox conservative and escalate only when justified.
- Ensure worker tasks never gain more power than the actor that launched them unless a fresh approval path exists.
- Distinguish path semantics for permission rules from path semantics for substrate mounts if the runtime supports both; do not assume one resolver is correct for both layers.
- Scope the sandbox explicitly to the tool classes it covers. Both shipping references this skill tracks (Claude Code's Bash sandbox, Codex's exec sandbox) restrict subprocess execution but leave file-edit, fetch, and computer-use tool calls to a separate permission system — "the agent is sandboxed" is a category error unless you name which tool surface that applies to.
- Do not let default read policy stay broad while write policy is locked down and call the result a secrets boundary; a sandbox that can still read `~/.ssh` or `~/.aws/credentials` because only writes were restricted is a common, easy-to-miss gap.
- Treat a hostname-based network allowlist as connectivity policy, not content inspection, unless the proxy actually terminates and inspects TLS — otherwise domain fronting through an allowed host is a viable exfiltration path.

## Build Order

1. Define execution modes and their trust levels.
2. Implement canonical path resolution and mount policy.
3. Add process and interpreter allowlists.
4. Add network policy and host exceptions.
5. Add env-var exposure rules and secret filtering.
6. Protect settings, policy, and skill directories as privileged config surfaces.
7. Add destructive-command classification and escalation hooks.

## Core Invariants

- The sandbox boundary must exist in the execution substrate, not only in prompts.
- Filesystem, network, and environment policy are separate control planes.
- Canonical path resolution is part of the security boundary.
- Child workers inherit the minimum effective envelope by default.
- Destructive capability must never be implied by tool name or user intent alone.
- Privileged config surfaces should remain protected even when ordinary workspace edits are allowed.

## Failure Modes

- Symlink or path-traversal writes escaping the allowed workspace.
- Wrapper tools bypassing interpreter or command allowlists.
- Network-denied commands succeeding through unclassified package-manager helpers.
- Child workers inheriting parent unrestricted mode silently.
- Secrets leaking through inherited environments into commands that did not need them.
- Workspace-write modes that accidentally allow mutation of policy or skill roots.

## Minimal Viable Version

- One conservative default sandbox mode.
- Canonical readable and writable root enforcement.
- One subprocess allowlist and one deny path for privileged classes.
- One explicit network policy.
- One protected-config-surface list.
- One escalation path for destructive or restricted actions.

## What Strong Implementations Add

- Worker-specific narrowed envelopes.
- Host-specific mount remapping and temp-space policies.
- Auditable destructive-command classes and explicit justifications.
- Network host allowlists and package-manager exception handling.
- Separate path resolvers or canonicalization rules for permission matching versus substrate mount enforcement.
- Escape-path tests for symlinks, shell expansion, wrapper binaries, and env indirection.

## Known Traps

- Assuming path-prefix checks are sufficient while symlinks, wrapper binaries, env indirection, or shell expansion bypass the intended boundary.
- Treating approval prompts as if they enforce isolation when the substrate itself still allows broad process, filesystem, or network access.
- Reusing the parent worker’s envelope for convenience and accidentally granting broader write or network privileges to delegated tasks.
- Forgetting that package-manager installs, build tools, and test runners often write outside obvious workspace paths unless mounts and temp policies are explicit.
- Classifying a top-level command as safe without evaluating the actual subprocess tree it can spawn.
- Enabling a compatibility escape hatch (macOS Apple Events, a MITM-friendly weaker-isolation flag, an unelevated Windows backend chosen for convenience) to fix one broken tool without registering what isolation guarantee that escape hatch removes for every command that follows it in the same session.
- Allowing a Unix domain socket such as a container runtime's control socket through the sandbox; a single such exception can be equivalent to full host access even when every filesystem and network rule looks tight.

## Common Anti-Patterns

- Treating approval prompts as if they were the sandbox.
- Assuming workspace-write is safe without canonical path checks.
- Allowing arbitrary interpreters because the top-level tool looked harmless.
- Reusing the parent worker’s full envelope for convenience.
- Treating settings and policy files as ordinary editable workspace content.
- Trusting wrapper commands without classifying what they actually execute.

## Cross-Platform Patterns (Goose)

Goose is now maintained under the Agentic AI Foundation (AAIF) at the Linux Foundation (founding contributors Block, Anthropic, OpenAI; transferred April 7, 2026). Repository: `aaif-goose/goose`; documentation: `goose-docs.ai`. Goose 2.0 (April 2026) ships a TypeScript TUI and is migrating the desktop app from Electron to Tauri; both surfaces communicate with a shared ACP daemon rather than separate runtimes. For cloud-hosted devbox execution, the isolation substrate is microVM/Firecracker-style (matching the pattern used for Codex cloud tasks).

Goose's sandbox posture adds two patterns the core skill does not model directly: build-time supply-chain gates, and distribution-layer allowlist baking.

### Build-time supply-chain gates (`deny.toml`, recipe-scanner)

Sandboxing stops code from misbehaving at runtime. It does not stop a compromised dependency from shipping. Goose uses `deny.toml` (cargo-deny) to gate licenses, advisories, and source allowlists at build, and `recipe-scanner/` to validate YAML recipes before they enter the shipping artifact.

- **Pattern:** pair every runtime substrate control with a build-time gate. If a tool or extension should not be allowed at runtime, it also should not appear in the shipping artifact. The sandbox is the runtime enforcement; build-time gates are the artifact enforcement.
- **Anti-pattern:** relying solely on runtime sandboxing to contain shipped-but-disallowed code. An attacker who compromises the build pipeline bypasses the runtime check entirely.
- **Recipe:** include `deny.toml`-equivalent gates (license, advisory, source allowlist) for every language ecosystem your agent uses. Statically scan shipped YAML recipes and plugin manifests for declared tools that exceed the distribution's allowlist.

### Custom-distro preconfigured allowlists

Custom distributions (see `ai-coding-agents-release-distribution`) ship with a narrowed extension/tool/provider allowlist *baked into the binary*. The runtime sandbox then enforces a tighter envelope than the open-source stable.

- **Pattern:** treat distribution-layer allowlists as a sandbox policy layer above the user's own settings. Users cannot broaden beyond what the distro allows; they can only narrow within it.
- **Anti-pattern:** ship the open-source binary to enterprise customers with a "policy file" they must install separately. Separation between binary and policy creates drift, stale-policy risk, and bypass-by-rename attacks.
- **Recipe:** add `distro_envelope: Option<ExtensionAllowlist>` as an immutable field in the merged settings source. The sandbox enforces it at execution time; the settings layer shows it as a read-only source (see `ai-coding-agents-settings-policy`).

## Navigation

### References

- [`references/sandbox-process-and-filesystem-model.md`](references/sandbox-process-and-filesystem-model.md) — Execution modes, process isolation, mounts, and write boundaries
- [`references/network-approval-and-destructive-action-guards.md`](references/network-approval-and-destructive-action-guards.md) — Network policy, escalation triggers, and destructive-command controls
- [`references/openai-codex-sandbox-guardrails-may-2026.md`](references/openai-codex-sandbox-guardrails-may-2026.md) — OpenAI Codex sandbox guardrails: mode names, backend matrix, fail-closed translation, and telemetry (re-verified 2026-07-11)
- [`references/claude-code-bash-sandbox-mechanics.md`](references/claude-code-bash-sandbox-mechanics.md) — Claude Code's shipping Bash sandbox: settings keys, read/write asymmetry, credential deny-vs-mask, TLS-blind allowlists, tool-scope limits
- [`references/sandbox-policy-format.md`](references/sandbox-policy-format.md) — Runtime-agnostic canonical policy format for interpreter allowlists and filesystem/network rules
- [`references/escape-path-test-matrix.md`](references/escape-path-test-matrix.md) — Escape-attack checklist to run before shipping any sandbox configuration

### Data

- [`data/sources.json`](data/sources.json) — Primary docs and implementation references for coding-agent sandbox design

### Related Skills

- [`../ai-coding-agents-permissions/SKILL.md`](../ai-coding-agents-permissions/SKILL.md)
- [`../ai-coding-agents-remote-runtime/SKILL.md`](../ai-coding-agents-remote-runtime/SKILL.md)
- [`../ai-coding-agents-tools/SKILL.md`](../ai-coding-agents-tools/SKILL.md)

## Fact-Checking

- Known bugs, regressions, framework/compiler/runtime footguns, and version-specific crash or workaround guidance must be verified against current primary web sources before being treated as current fact.
- Sandbox details are highly product-specific and may depend on host OS, terminal model, and packaging strategy. Preserve the security model, but verify exact enforcement points in the target runtime.
- Do not infer real safety from prompt instructions alone; the boundary must exist in the execution substrate.

## Learnings Loop

Before applying this skill on a non-trivial task, read `learnings.consolidated.md` in this directory (and `learnings.md` if present).

After applying it, if you encountered a pattern worth remembering, a mistake worth preventing, or a domain fact that surprised you, append one dated bullet to `learnings.md` via `agents-skills-feedback-loop/scripts/append_learning.py`. Do not modify `SKILL.md` itself.
