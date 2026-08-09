# Claude Code Bash Sandbox Mechanics

Source: `code.claude.com/docs/en/sandboxing`, checked 2026-07-11. Version-gated features are marked with the Claude Code release that introduced them; verify against the live doc before treating a gate as current, since these move with point releases.

## Table of Contents

- [Scope: Bash Only](#scope-bash-only)
- [Two Independent Modes](#two-independent-modes)
- [Platform Backends](#platform-backends)
- [Default Read/Write Asymmetry](#default-readwrite-asymmetry)
- [Settings Keys](#settings-keys)
- [Credential Protection: Deny Vs Mask](#credential-protection-deny-vs-mask)
- [Network: Allowlist Without TLS Inspection](#network-allowlist-without-tls-inspection)
- [The Escape Hatch](#the-escape-hatch)
- [Known Compatibility Failures](#known-compatibility-failures)
- [Known Traps](#known-traps)

## Scope: Bash Only

The sandbox is not a runtime-wide isolation boundary. It restricts Bash subprocesses (and their children) at the OS level. Read, Edit, Write, WebFetch, MCP tools, and computer-use each go through the ordinary permission-rule system instead, and computer-use runs on the real desktop, not inside an isolation boundary. A design that assumes "sandboxed" implies protection for every tool call is wrong; audit each tool class separately.

Subagents run in the same process as the parent session and inherit its sandbox configuration — a subagent cannot have a wider Bash sandbox than its parent.

## Two Independent Modes

`/sandbox` exposes a mode axis (auto-allow vs. regular permissions) that is deliberately separate from permission modes (default, auto, `--dangerously-skip-permissions`):

- **Auto-allow**: sandboxed Bash commands run without a prompt because the OS boundary contains them. Explicit deny rules, `rm`/`rmdir` against `/` or the home directory, and content-scoped ask rules (e.g. `Bash(git push *)`) still force a prompt even in auto-allow.
- **Regular permissions**: every Bash command still goes through the normal prompt flow even though it also runs sandboxed.

Do not conflate this with the model's own "auto mode," which uses a classifier to decide whether to prompt at all — the two axes compose independently.

## Platform Backends

- **macOS**: Seatbelt, built in, nothing to install.
- **Linux and WSL2**: bubblewrap (filesystem isolation) plus socat (network relay to the sandbox proxy); both must be installed by the user. An optional seccomp filter (installed via `npm install -g @anthropic-ai/sandbox-runtime`) adds Unix-domain-socket blocking.
- **WSL1 and native Windows**: unsupported. Windows users must run inside a WSL2 distribution.
- Ubuntu 24.04+ ships an AppArmor policy that blocks bubblewrap's unprivileged user-namespace creation; a dedicated `bwrap` AppArmor profile is required as a workaround (see the live doc for the exact profile).

## Default Read/Write Asymmetry

Write access defaults to narrow (current working directory plus the session temp directory). Read access defaults to broad (the entire filesystem except a denylist) — and that default still permits reading `~/.aws/credentials` and `~/.ssh/`. A sandbox with locked-down writes but stock read defaults is not a secrets boundary; it must be paired with `sandbox.credentials` or explicit `denyRead` entries to actually protect credential files.

## Settings Keys

All keys live under the `sandbox` object in `settings.json` (merged across managed/project/local/user scopes; project wins on conflict for scalars, arrays merge):

| Key | Purpose |
|---|---|
| `sandbox.enabled` | Turn the sandbox on for the scope |
| `sandbox.failIfUnavailable` | Hard-fail startup instead of silently running unsandboxed when a dependency is missing (use in managed settings) |
| `sandbox.allowUnsandboxedCommands` | Set `false` for "strict sandbox mode" — disables the retry-outside-sandbox escape hatch entirely |
| `sandbox.excludedCommands` | Commands that always run outside the sandbox (e.g. `docker *`) |
| `sandbox.filesystem.allowWrite` / `denyWrite` | Widen or narrow writable paths beyond cwd + temp |
| `sandbox.filesystem.denyRead` / `allowRead` | Narrow readable paths, then re-open specific paths within a denied region |
| `sandbox.credentials.files[].mode` | `"deny"` — block reads of a credential file inside the sandbox |
| `sandbox.credentials.envVars[].mode` | `"deny"` (unset) or `"mask"` (sentinel substitution, see below) |
| `sandbox.network.allowedDomains` / `deniedDomains` | Domain allowlist/denylist for the sandbox network proxy |
| `sandbox.network.allowManagedDomainsOnly` | Managed-settings-only lockdown: non-managed `allowedDomains` entries are ignored, unlisted domains are blocked instead of prompted |
| `sandbox.network.tlsTerminate` | Experimental: proxy terminates TLS itself; required for `mask` credential substitution |
| `sandbox.allowManagedReadPathsOnly` | Managed-settings-only lockdown for `allowRead` |
| `sandbox.allowAppleEvents` | macOS only; lifts the Apple Events block but removes code-execution isolation (see Known Traps) |

Settings files themselves (`settings.json` at every scope, plus the managed settings directory) are always write-denied inside the sandbox — a sandboxed command cannot rewrite its own policy.

## Credential Protection: Deny Vs Mask

`deny` removes a credential entirely from the sandboxed process — simplest, but breaks tools that need the value (`gh`, `npm`). `mask` substitutes a per-session sentinel; the real value is injected only when a request leaves the sandbox for a host listed in `injectHosts`, and only if `network.tlsTerminate` is configured (otherwise the sentinel reaches the server unchanged and auth fails — Claude Code reports this at startup rather than failing silently). `mask` entries, `tlsTerminate`, and `credentials.allowPlaintextInject` are honored only from user/managed/CLI settings — a repo's own `.claude/settings.json` cannot enable credential injection for itself.

## Network: Allowlist Without TLS Inspection

By default the sandbox's built-in proxy makes its allow/deny decision from the client-supplied hostname (SNI/Host header) and does not terminate or inspect TLS. Allowing a broad domain such as `github.com` can therefore be defeated by domain fronting or similar techniques that reach a different host behind the same front. Treat a domain allowlist as connectivity policy, not as a content-inspection boundary, unless `network.tlsTerminate` plus a custom inspecting proxy is in place.

## The Escape Hatch

When a sandboxed command fails because of the sandbox boundary, Claude Code can retry it with `dangerouslyDisableSandbox`, which routes the retry through the ordinary permission prompt instead of failing the task. This is a deliberate escalation path, not a silent fallback — but it does mean "the sandbox blocked it" is not the end of the story unless `allowUnsandboxedCommands: false` is set.

## Known Compatibility Failures

- `jest` hangs under the sandbox when `watchman` is present — run with `--no-watchman`.
- `docker` is fully incompatible — exclude it rather than trying to make it work inside the sandbox.
- Go-based CLIs (`gh`, `gcloud`, `terraform`) can fail TLS verification under macOS Seatbelt — exclude them or address it via `enableWeakerNetworkIsolation` only if a MITM proxy with a custom CA is already in play.
- On WSL2, the sandbox blocks calls out to Windows binaries (`cmd.exe`, `powershell.exe`, `/mnt/c/...`) because WSL hands them off over a Unix socket the sandbox blocks; add them to `excludedCommands` if a workflow genuinely needs them.
- `open`/`osascript`/browser-based auth flows fail with macOS error `-600` because Apple Events are blocked by default.

## Known Traps

- Assuming "sandboxed" covers every tool call — it covers Bash only.
- Treating the read-access default as equivalent to the write-access default; they are not symmetric, and the gap leaks credential files unless explicitly closed.
- Enabling `allowAppleEvents` to fix a broken `open`/`osascript` call without registering that it removes code-execution isolation on macOS (sandboxed commands can then launch other unsandboxed applications and drive them via AppleScript, gated only by the OS's own automation-consent prompt).
- Allowing a Unix domain socket such as `/var/run/docker.sock` through `allowUnixSockets`, which is equivalent to granting host access through the Docker daemon.
- Believing a domain allowlist inspects content; without `tlsTerminate` it only checks the requested hostname.
