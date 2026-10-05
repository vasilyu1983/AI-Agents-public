# ai-coding-agents-surfaces — Learnings

Merged from ai-coding-agents-surfaces and ai-coding-agents-surfaces on 2026-09-29; entries carried unchanged.

## Patterns That Work


## Mistakes to Avoid

- [2026-07-11] Prior draft invented keybindings (Shift+Up/Down teammate nav, per-task K/F/D). Verify every key against code.claude.com/docs/en/keybindings before asserting it exists.

## Domain Knowledge

- [2026-07-11] Agent Teams default display mode is in-process (v2.1.178+); split-pane needs tmux or iTerm2+it2 and never works in VS Code terminal, Windows Terminal, or Ghostty.

## Open Questions


## Consolidated Principles


## Carried Raw Entries

- [2026-07-11] July 2026 audit found the skill's remote-runtime patterns had drifted from being grounded only in source reading to now having live, citable shipped products: Claude Code's `remote-control` feature (`claude remote-control`/`--remote-control`/`/remote-control`, outbound-HTTPS-only with no inbound ports, short-lived scoped credentials, session URL + QR from `claude.ai/code`) is architecturally distinct from the Desktop app's SSH-to-remote-host feature (execution genuinely moves to the remote host) and from Claude Code on the web / Routines (cloud VM, no local machine involved at all). Also corrected a stale claim (flagged in `openai/codex` issue #25552) that top-level `codex remote-control` manages daemon bootstrap — it actually runs a foreground app-server for one invocation; daemon lifecycle is under explicit `codex remote-control start/stop/restart` subcommands. (The claim recorded here that pairing is mediated only by the desktop app was found stale in the 2026-09 audit; check current CLI help.) Added a "no-inbound-ports relay" transport shape to `transport-selection.md` since the existing WebSocket/SSE/HTTP-POST/ACP tree had no entry for NAT'd, roaming, or otherwise untrusted-network executing machines.
