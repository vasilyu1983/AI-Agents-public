# Local UI, Remote Execution Model

## Table Of Contents

- [Design Goal](#design-goal)
- [Execution Split](#execution-split)
- [Remote Modes](#remote-modes)
- [Command And Tool Surface](#command-and-tool-surface)
- [Two Different "Remote" Products — Don't Conflate Them](#two-different-remote-products--dont-conflate-them)
- [SSH-Like Sessions](#ssh-like-sessions)
- [Client and Daemon Version Skew](#client-and-daemon-version-skew)

## Design Goal

Remote coding-agent runtimes should keep user interaction local while allowing the agent loop and tools to run elsewhere. This is a shipped pattern, not just a prototype: cross-device remote control of a local session and a desktop app's SSH-host connection are two differently-architected instances of the same design goal — see below for why they are not interchangeable.

## Execution Split

The runtime split should be explicit:

- local client renders the REPL or viewer
- remote runtime owns the agent loop and tool execution
- messages flow back over a typed transport
- control actions such as approval or interrupt are routed separately

This avoids pretending the local CLI is executing tools it does not control.

## Remote Modes

A local-first coding-agent CLI exposes several different remote-oriented modes. Claude Code's remote-control surface is one concrete instance of this taxonomy (check its current docs for exact commands and flags):

- **server mode** — a foreground process serves multiple concurrent remotely-steerable sessions, with a choice of where each spawned session runs (same directory, a new worktree) and a capacity limit; it prints a session URL or QR code for pairing
- **interactive-with-remote-control** — one normal interactive session that is simultaneously drivable from another device
- **attach-from-existing-session** — an in-session command promotes an already-running local session to remotely steerable, carrying over conversation history
- **viewer/controller from a web or mobile client** — the remote client is not a peer session, it is a window into the one local session; some commands (for example plugin management or session resume) are deliberately local-only

Treat those as distinct runtime modes, not feature flags on one generic session object — each has a different default network posture (foreground-blocking vs multiplexed) and a different set of commands it forwards.

## Command And Tool Surface

Remote mode also filters commands and starts with a narrower local tool surface. That is the right pattern:

- do not expose every local-only command in remote mode
- do not assume the local client has every remote tool available
- preserve a single semantic session, but narrow the operational UI appropriately

## Two Different "Remote" Products — Don't Conflate Them

Two shipped Claude Code features both answer "how do I use Claude Code away from my desk," and they are architecturally opposite. Picking the wrong one as your mental model produces the wrong design:

| | Desktop app → remote SSH host | `remote-control` |
|---|---|---|
| Where does the agent loop run? | On the remote SSH host (Claude Code is auto-installed there on first connect) | On the machine you started it on — never moves |
| Where does the REPL/UI live? | Desktop app, tunneled over the SSH connection | Any device (phone, browser, VS Code) via `claude.ai/code` or the mobile app |
| Network shape | Outbound SSH connection you already have working (`ssh user@host`) | Outbound-only HTTPS from the local machine; **no inbound port is ever opened**; the client and local machine rendezvous through the Anthropic API |
| Session history | Siloed per surface — desktop app, remote CLI, and remote VS Code each keep separate session lists | One session, mirrored; renaming from the phone updates the local title too |
| Right mental model | Classic "SSH-like" remote-execution devbox: filesystem, cwd, and process all genuinely live remotely | Cross-device **steering/mirroring** of a session whose filesystem and tools never leave the original machine |

Both are real and both matter, but they solve different problems:

- Use the **remote-execution devbox** model when the point is to run tools against a filesystem and environment that only exists on another machine (a build server, a GPU box, a long-lived dev container).
- Use the **outbound-poll mirroring** model when the point is to keep working from a different physical device on the *same* environment, without exposing that machine to inbound connections.

## SSH-Like Sessions

The reusable pattern behind the remote-execution devbox model:

- the REPL/UI stays on the connecting client
- tools, filesystem, and process state execute on the remote host
- auth and cwd state are remote-aware, and first-connect auto-installs the agent binary if it is missing
- treat each remote host as its own session-history namespace — do not assume a session created on the SSH host is visible from a different local surface

That is a reusable pattern for coding-agent runtimes that need remote execution without fully turning the UI into a web client. It is a different pattern from outbound-poll mirroring (above) even though both are commonly described as "remote."

## Client and Daemon Version Skew

The UI client and the daemon or server upgrade on different schedules. A desktop app auto-updates while a remote host keeps an old daemon, or an editor plugin lags behind both. Design for skew; do not assume the two move in lockstep.

- **Negotiate at connect.** The client's first message states the protocol version range and the capabilities it supports. The daemon replies with the chosen protocol version, its build identity, and the capability set both sides will use. Gate features on the negotiated capabilities, never on a comparison of product version strings.
- **Refuse explicitly when the ranges do not overlap.** The daemon returns a typed incompatibility error that names both versions, the supported range, and which side must upgrade. The client shows the error and stops. It does not try a best-effort session or silently drop messages it cannot parse. Inside the range, an unknown method or capability still gets a structured unsupported error.
- **Upgrade the daemon first.** Each daemon release accepts at least the previous client protocol version, so clients can upgrade after it. To retire a protocol version, first stop clients from sending it, then remove it from the daemon a release later. Never require a simultaneous upgrade, because that takes away independent rollback of the UI.
- **Roll back the UI alone.** Because the daemon still accepts the older client protocol, reverting the UI fixes a UI regression without touching the daemon.
- **Drain before a daemon restart.** Stop accepting new sessions, let in-flight turns finish or checkpoint, then restart. Clients reconnect and negotiate again, because the capability set may have changed.
- **Test the skew matrix.** Cover a new client with an old daemon, an old client with a new daemon, and a pair with no overlapping range, which must reach the refusal path.
