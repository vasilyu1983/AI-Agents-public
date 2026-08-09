# OpenAI Codex Unified Exec And Tool Contracts

Source snapshot: OpenAI Codex commit `9f42c89c0112771dc29100a6f3fc904049b2655f` (2026-05-24), especially `codex-rs/core/src/tools/handlers/shell_spec.rs` and `codex-rs/core/src/tools/handlers`.

Web sources checked 2026-05-25:

- OpenAI, "How OpenAI uses Codex" PDF, May 2026: https://cdn.openai.com/pdf/6a2631dc-783e-479b-b1a4-af0cfbd38630/how-openai-uses-codex.pdf
- Codex use cases, "Create a CLI Codex can use": https://developers.openai.com/codex/use-cases

## Table Of Contents

- [Design Goal](#design-goal)
- [Unified Exec Contract](#unified-exec-contract)
- [Permission-Aware Tool Parameters](#permission-aware-tool-parameters)
- [Output Budgeting](#output-budgeting)
- [Composable CLIs As Tools](#composable-clis-as-tools)
- [Known Traps](#known-traps)

## Design Goal

Treat shell execution as a real tool contract, not a string escape hatch. Codex's current tool surface makes command execution explicit enough for UI rendering, approval routing, PTY sessions, output truncation, and remote environments.

## Unified Exec Contract

A strong exec tool contract includes:

- command text
- optional working directory
- optional shell
- optional login-shell behavior
- TTY allocation flag
- output yield timeout
- maximum output tokens
- session ID for ongoing interactive processes
- separate stdin-writing tool for already-running sessions

This split lets the runtime distinguish one-shot commands from long-lived terminal sessions.

## Permission-Aware Tool Parameters

Codex adds approval fields to shell-like tools rather than hiding escalation in natural language:

- sandbox permission mode
- justification for unsandboxed escalation
- suggested future approval prefix
- optional additional permission profile when fine-grained permission approvals are enabled

Best practice:

- request the narrowest extra permission that can complete the command
- keep unsandboxed execution as the exceptional path
- make the approval prompt carry command, reason, and scope

## Output Budgeting

Codex exposes `max_output_tokens` and `yield_time_ms` in the tool contract. Copy that pattern for every high-volume tool:

- cap output at the tool boundary
- report that truncation happened
- let the model poll long-running commands instead of blocking the whole turn
- preserve enough metadata to resume or cancel the running process

## Composable CLIs As Tools

OpenAI's May 2026 use cases explicitly call out creating CLIs that Codex can use. The runtime lesson is simple: the best agent tool is often a small, typed command-line wrapper around an existing API, log source, export, or team script.

For runtime builders:

- prefer deterministic CLI wrappers over broad browser automation when an API exists
- keep output structured and compact
- provide dry-run or read-only modes
- document auth and environment variables outside the prompt body

## Known Traps

- Using shell commands as an untyped universal tool and losing approval context.
- Returning unlimited logs to the model.
- Blocking a turn on an interactive process that should have become a session.
- Asking for full escalation when a turn-scoped read, write, or network grant would work.
- Building a plugin when a small CLI plus a stable output schema would be enough.
