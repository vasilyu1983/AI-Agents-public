# OpenAI Codex App Server Remote Control

Source snapshot: OpenAI Codex commit `9f42c89c0112771dc29100a6f3fc904049b2655f` (2026-05-24), especially `codex-rs/app-server-daemon/README.md`, `codex-rs/app-server-protocol`, `codex-rs/app-server-transport`, and `codex-rs/cli/src/remote_control_cmd.rs`.

Web sources checked 2026-05-25:

- OpenAI, "Codex for (almost) everything", Apr 16, 2026: https://openai.com/index/codex-for-almost-everything/
- Codex use cases: https://developers.openai.com/codex/use-cases

Later sources that correct the daemon README (see the CLI remote-control section below):

- `openai/codex` issue #25552 (app-server-daemon README describes stale top-level `codex remote-control` behavior)
- `openai/codex` discussion #21935 (intended direction for the `codex remote-control` entrypoint, v0.130.0+)
- Codex CLI v0.130 release notes (`codex remote-control` top-level command)

## Table Of Contents

- [Design Goal](#design-goal)
- [Daemon Lifecycle](#daemon-lifecycle)
- [Machine-Readable Control](#machine-readable-control)
- [Remote Host Bootstrap](#remote-host-bootstrap)
- [Long-Running Work](#long-running-work)
- [Known Traps](#known-traps)

## Design Goal

Model remote runtime as local UI clients talking to a durable app-server process, not as a UI that owns every session directly. Codex uses app-server and daemon commands so desktop, mobile, SSH, and CLI surfaces can attach to a managed backend.

## Daemon Lifecycle

Codex daemon operations include:

- start
- restart
- enable remote control
- disable remote control
- stop
- version
- bootstrap with remote control

Mutating lifecycle operations are serialized per `CODEX_HOME`. Copy this invariant so concurrent start/restart/enable operations cannot corrupt daemon state.

## Machine-Readable Control

Codex daemon commands write exactly one JSON object on success. Consumers should parse JSON, not terminal prose.

For remote runtimes:

- keep lifecycle output stable and typed
- include socket path, backend, local CLI version, and running server version
- keep human rendering outside the protocol layer

## CLI remote-control: user entry point vs plumbing

Codex maintainers flagged (`openai/codex` issue #25552) that the `app-server-daemon` README's description of top-level `codex remote-control` was stale. The durable lessons:

- A foreground "enable remote control for this invocation" mode and daemon lifecycle management (start/stop/restart/enable/disable) are different jobs; keep them as distinct, explicit subcommands rather than one command that silently does both.
- Which surface owns device pairing (CLI, desktop app, or both) varies by product and changes between releases. Check the current CLI help and remote-control docs before stating where a pairing code or QR flow comes from.
- Two products' "remote-control" commands need not play the same role just because the name matches; one may be the primary user-facing entry point and the other plumbing that other surfaces build on.

Design rule: when documenting or building a CLI `remote-control`-style command, be explicit about whether it is a user-facing steering entry point or low-level daemon plumbing for other surfaces to build on. Conflating the two produces wrong integration guides.

## Remote Host Bootstrap

The Codex bootstrap pattern assumes a managed standalone install under `CODEX_HOME`, records daemon settings, starts app-server as a detached process, and launches an updater loop.

Design rule:

- bootstrap should be idempotent
- bootstrap should leave a clear state directory
- update behavior should be explicit, not a side effect of every start

## Long-Running Work

Long-running remote work — scheduled runs, reused threads, remote devboxes, multiple terminals, work carried forward across days — needs re-attach, durable thread IDs, and explicit enablement. A remote runtime must therefore support:

- re-attach after UI disconnect
- durable thread IDs
- explicit remote-control enablement
- safe access to local credentials and files on the connected host
- clear ownership of who can start, stop, or update the daemon

## Known Traps

- Binding session lifetime to a GUI window or SSH pipe.
- Printing human text where remote clients expect one JSON object.
- Updating the daemon binary before restarting the app-server that depends on it.
- Letting concurrent lifecycle commands race in the same runtime home.
- Treating mobile/desktop remote control as just another transport, without credential and host-ownership rules.
