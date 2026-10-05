# OpenAI Codex Sandbox Guardrails

Source kind: the vendor sandboxing concept doc and the sandbox crate READMEs in the Codex repository (`codex-rs/core`, `codex-rs/linux-sandbox`, `codex-rs/windows-sandbox-rs`). Check them before copying mode names or backend claims; both move with releases.

Web sources:

- OpenAI, "Building a safe, effective sandbox to enable Codex on Windows", May 13, 2026: https://openai.com/index/building-codex-windows-sandbox/
- OpenAI, "Running Codex safely at OpenAI": https://openai.com/index/running-codex-safely/
- OpenAI, Codex sandboxing concept doc: https://developers.openai.com/codex/concepts/sandboxing

## Table Of Contents

- [Sandbox Modes](#sandbox-modes)
- [Design Goal](#design-goal)
- [Default Useful Sandbox](#default-useful-sandbox)
- [Platform Backends](#platform-backends)
- [Fail-Closed Policy Translation](#fail-closed-policy-translation)
- [Security Telemetry](#security-telemetry)
- [Known Traps](#known-traps)

## Sandbox Modes

Codex names three modes explicitly — copy these names when mapping a runtime's own modes onto the Codex model, since "sandbox mode" and "approval policy" are separate axes here too:

- **`read-only`**: inspect files; no writes, no command execution without approval.
- **`workspace-write`** (default): read broadly, write only inside the workspace, run routine commands inside that boundary.
- **`danger-full-access`**: no filesystem or network restriction — treat as equivalent to disabling the sandbox, not as a stronger permission tier.

Sandbox mode and approval policy are separate axes; look up the current approval values before writing config (see [`../SKILL.md`](../SKILL.md)). The same sandbox mode with a never-prompt approval policy is a materially different posture than with a prompt-on-request policy, so audit both axes, not just the sandbox mode name.

## Design Goal

The sandbox should be useful enough that developers do not disable it, while still enforcing real process, filesystem, and network boundaries. OpenAI's Windows sandbox write-up frames the bad alternatives clearly: approving nearly every command is too slow, while full access removes the boundary.

## Default Useful Sandbox

Codex's public sandbox framing is a practical default:

- read broadly enough to inspect code and dependencies
- write only inside the workspace
- deny internet access unless explicitly enabled
- propagate constraints down the process tree

Copy the product principle, not only the implementation: a default sandbox must let normal build/test/edit loops work without training users to reach for full access.

## Platform Backends

Codex uses different enforcement backends per platform:

- macOS: Seatbelt via `sandbox-exec`; workspace-write policy keeps `.git` and `.codex` read-only even inside writable roots.
- Linux and WSL2: bubblewrap (`bwrap`) is the primary backend — Codex prefers the first `bwrap` found on `PATH`, with a bundled fallback helper; Landlock remains for legacy-compatible policies. WSL1 is rejected outright (bubblewrap needs kernel features WSL1 lacks).
- Windows: two backends, not one — an **elevated** backend supporting split filesystem policies (needs system read roots such as `C:\Windows` to run at all) and an **unelevated, restricted-token** backend for simpler/legacy configurations. Native Windows in PowerShell uses the Windows-native backend; running Codex inside WSL2 uses the Linux backend instead.

Keep a backend capability matrix. Do not assume a policy that works on macOS can be enforced the same way on Windows or Linux, and do not assume "Windows" is a single backend — elevated and unelevated Windows sandboxes have different capabilities.

## Fail-Closed Policy Translation

Codex keeps legacy sandbox modes but translates newer split filesystem policies only when semantics are preserved. Policies that cannot be enforced directly or round-trip safely should fail closed.

Required tests:

- writable root with read-only child
- denied parent with writable reopened descendant
- symlink and junction traversal
- protected metadata under writable roots
- missing helper binary fallback
- unsupported Windows/WSL backend behavior

## Security Telemetry

OpenAI's safety post emphasizes agent-native telemetry: user prompt, approval decisions, tool results, MCP usage, and network proxy decisions. Sandbox denials should be observable as first-class security events, not just stderr text.

Design implication:

- emit structured sandbox denial events
- include network allow/deny/prompt decisions
- keep enough context for a security triage agent to distinguish expected behavior, benign mistakes, and suspicious activity

## Known Traps

- Treating "sandboxed" as a single boolean.
- Silently weakening a policy when a platform backend cannot enforce it.
- Making the sandbox so restrictive that users switch to full access for ordinary work.
- Logging process execution without the prompt, approval, or network-policy context that explains why it happened.
- Forgetting descendant processes: a sandbox that does not propagate is not a coding-agent sandbox.
