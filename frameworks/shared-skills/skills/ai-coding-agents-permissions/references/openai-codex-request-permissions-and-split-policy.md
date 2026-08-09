# OpenAI Codex Request Permissions And Split Policy

Source snapshot: OpenAI Codex commit `7d47056ea42636271ac020b86347fbbef49490aa` (2026-05-22), especially `codex-rs/protocol/src/permissions.rs`, `codex-rs/core/src/tools/handlers/shell_spec.rs`, and `codex-rs/core/README.md`.

## Table Of Contents

- [Design Goal](#design-goal)
- [Split Filesystem Policy](#split-filesystem-policy)
- [Protected Metadata](#protected-metadata)
- [Permission Request Tool](#permission-request-tool)
- [Approval Policy Is Not Sandbox Policy](#approval-policy-is-not-sandbox-policy)
- [Test Matrix](#test-matrix)

## Design Goal

Use a capability policy that can express exact filesystem and network permissions, then route approval prompts through the host. Older `read-only` / `workspace-write` / `danger-full-access` modes are useful presets, but they are too coarse as the only internal model.

## Split Filesystem Policy

Codex models filesystem access as entries with:

- path: concrete path or special path such as root, project roots, temp directory, or platform defaults
- access: `read`, `write`, or `deny`
- kind: restricted, unrestricted, or external sandbox

This lets a runtime express cases that coarse sandbox modes cannot:

- writable project root with read-only or denied carveouts
- denied child under a writable parent
- writable child reopened under a denied parent
- restricted read roots on platforms that can enforce them

For new runtimes, normalize high-level presets into this lower-level model before execution.

## Protected Metadata

Codex protects top-level workspace metadata names under writable roots:

- `.git`
- `.agents`
- `.codex`

Use this as a default rule. A workspace-write sandbox should not imply that the agent can rewrite repository metadata, local agent definitions, or runtime policy files unless there is an explicit write grant for that metadata path.

## Permission Request Tool

Codex exposes a `request_permissions` tool that asks for a structured permission profile rather than forcing every command to request full escalation. Granted permissions can apply to later shell-like commands in the current turn or, if approved at session scope, for the rest of the session.

Copy the pattern:

- prefer requesting narrower filesystem or network permissions
- keep full unsandboxed escalation as the exception
- distinguish fresh requests from already preapproved sticky grants
- record whether a grant is turn-scoped or session-scoped

## Approval Policy Is Not Sandbox Policy

Codex keeps approval behavior and sandbox enforcement separate. An approval policy can suppress prompts, but it does not by itself create filesystem or network authority.

Design rule:

- approval policy answers "may the runtime ask or auto-decide?"
- sandbox policy answers "what can the process actually access?"
- permission grants are explicit changes to sandbox capability, not merely approval state

## Test Matrix

Codex's source and sandbox smoke tests point to the hostile cases worth copying:

- write inside workspace succeeds only when intended
- write outside workspace fails unless explicitly granted
- protected metadata remains read-only by default
- symlink and junction paths cannot bypass carveouts
- malformed deny globs fail closed
- network behavior follows network policy, not command text
- platform fallbacks fail closed when exact policy cannot be enforced

## Traps

- Treating `approval_policy = never` as permission to bypass sandboxing.
- Making `.git`, `.agents`, or `.codex` writable just because the repo root is writable.
- Falling back to a weaker sandbox silently when a split policy cannot be enforced.
- Asking for unsandboxed escalation when a narrower additional permission would work.
