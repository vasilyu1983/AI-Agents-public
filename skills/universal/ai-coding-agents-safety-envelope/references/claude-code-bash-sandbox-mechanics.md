# Claude Code Bash Sandbox Mechanics

Source kind: the vendor sandboxing doc (`code.claude.com/docs/en/sandboxing`). Look up the current doc before copying a key name, default, or version gate; these move with point releases.

## Table of Contents

- [Scope: Subprocess-Spawning Tools Only](#scope-subprocess-spawning-tools-only)
- [Two Independent Modes](#two-independent-modes)
- [Platform Backends](#platform-backends)
- [Default Read/Write Asymmetry](#default-readwrite-asymmetry)
- [Settings Controls](#settings-controls)
- [Credential Protection: Deny Vs Mask](#credential-protection-deny-vs-mask)
- [Network: Allowlist Without TLS Inspection](#network-allowlist-without-tls-inspection)
- [The Escape Hatch](#the-escape-hatch)
- [Known Compatibility Failures](#known-compatibility-failures)
- [Known Traps](#known-traps)

## Scope: Subprocess-Spawning Tools Only

The sandbox is not a runtime-wide isolation boundary. It restricts subprocesses spawned by command-running tools (Bash and the other shell or process-launching tools the runtime routes through it) and their children at the OS level. Enumerate which tool classes the target runtime sandboxes from its current doc; do not assume the list is Bash alone. Read, Edit, Write, WebFetch, MCP tools, and computer-use each go through the ordinary permission-rule system instead, and computer-use runs on the real desktop, not inside an isolation boundary. A design that assumes "sandboxed" implies protection for every tool call is wrong; audit each tool class separately.

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

## Settings Controls

All sandbox settings live under one `sandbox` object in the settings files. How values combine across scopes follows the settings layer's per-value-type precedence rule: scalars take the highest-precedence source, lists merge across sources, and a deny from any scope still applies. See [`../../ai-coding-agents-settings-policy/references/settings-precedence-table.md`](../../ai-coding-agents-settings-policy/references/settings-precedence-table.md#rules).

Look up the current key names in the vendor sandbox settings reference; do not generate them from memory. The control classes to find, and the durable rule for each:

- **Enable and fail-if-unavailable.** Set the fail-if-unavailable control from managed settings, so a missing backend dependency hard-fails startup instead of silently running unsandboxed.
- **Strict mode.** A switch that removes the retry-outside-sandbox escape hatch (see [The Escape Hatch](#the-escape-hatch)).
- **Excluded commands.** Every entry runs fully outside the sandbox; treat each one as a registered hole, not a convenience.
- **Filesystem lists.** Write widen/narrow lists and read deny/re-open lists; the read deny list is what closes the credential gap above.
- **Credential modes.** Per-file and per-env-var deny or mask (see below).
- **Network domain lists.** Allow and deny lists for the sandbox proxy; connectivity policy only (see below).
- **Managed-only lockdowns.** Controls, honored only from managed settings, that make non-managed domain or read-path entries ignored and block unlisted domains instead of prompting.
- **Weaker-isolation hatches.** Platform-specific switches (for example the macOS Apple Events switch) that each remove a named guarantee; see Known Traps.

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

- Assuming "sandboxed" covers every tool call — it covers subprocess-spawning tools only; enumerate which ones for the target runtime.
- Treating the read-access default as equivalent to the write-access default; they are not symmetric, and the gap leaks credential files unless explicitly closed.
- Enabling `allowAppleEvents` to fix a broken `open`/`osascript` call without registering that it removes code-execution isolation on macOS (sandboxed commands can then launch other unsandboxed applications and drive them via AppleScript, gated only by the OS's own automation-consent prompt).
- Allowing a Unix domain socket such as `/var/run/docker.sock` through `allowUnixSockets`, which is equivalent to granting host access through the Docker daemon.
- Believing a domain allowlist inspects content; without `tlsTerminate` it only checks the requested hostname.
