# Local UI, Remote Execution Model

## Table Of Contents

- [Design Goal](#design-goal)
- [Execution Split](#execution-split)
- [Remote Modes](#remote-modes)
- [Command And Tool Surface](#command-and-tool-surface)
- [Two Different "Remote" Products — Don't Conflate Them](#two-different-remote-products--dont-conflate-them)
- [SSH-Like Sessions](#ssh-like-sessions)

## Design Goal

Remote coding-agent runtimes should keep user interaction local while allowing the agent loop and tools to run elsewhere. As of July 2026 this is a shipped pattern, not just an internal prototype: Claude Code's `remote-control` feature (verified against `code.claude.com/docs/en/remote-control`) and its Desktop app's SSH-host connection are two independently real, differently-architected instances of the same design goal — see below for why they are not interchangeable.

## Execution Split

The runtime split should be explicit:

- local client renders the REPL or viewer
- remote runtime owns the agent loop and tool execution
- messages flow back over a typed transport
- control actions such as approval or interrupt are routed separately

This avoids pretending the local CLI is executing tools it does not control.

## Remote Modes

A local-first coding-agent CLI exposes several different remote-oriented modes. Claude Code's shipped `remote-control` surface (verified 2026-07-11) is a concrete, citable instance of this taxonomy:

- **server mode** — `claude remote-control` runs in the foreground and serves multiple concurrent sessions (`--spawn same-dir|worktree|session`, `--capacity N`); it prints a session URL and (on spacebar) a QR code
- **interactive-with-remote-control** — `claude --remote-control` (alias `--rc`) starts one normal interactive session that is simultaneously drivable from another device
- **attach-from-existing-session** — the `/remote-control` (alias `/rc`) slash command promotes an already-running local session to remotely steerable, carrying over conversation history
- **viewer/controller from claude.ai/code or the mobile app** — the remote client is not a peer session, it is a window into the one local session; some commands (e.g. `/plugin`, `/resume`) are deliberately local-only

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
