# OpenAI Codex Rollout Doctor Telemetry

Source snapshot: OpenAI Codex commit `7d47056ea42636271ac020b86347fbbef49490aa` (2026-05-22), especially `codex-rs/state/src/lib.rs`, `codex-rs/cli/src/doctor.rs`, `codex-rs/otel`, and session/task telemetry code under `codex-rs/core/src`.

## Table Of Contents

- [Design Goal](#design-goal)
- [Rollout As Replay Artifact](#rollout-as-replay-artifact)
- [SQLite Mirror](#sqlite-mirror)
- [Doctor Reports](#doctor-reports)
- [Trace And Metric Hooks](#trace-and-metric-hooks)

## Design Goal

Observability for a coding-agent runtime should support both debugging a single user session and measuring aggregate runtime health. Codex does this by combining rollout JSONL, SQLite-derived indexes, structured doctor checks, trace IDs, and metrics.

## Rollout As Replay Artifact

Codex stores rich rollout items that can be replayed or mined later. The runtime can reconstruct history, seed token usage, and recover metadata from rollout items.

Copy this rule:

- the human transcript is not enough
- persist event messages, response items, compaction markers, token counts, and task boundaries
- make rollout flush behavior explicit around abort/interruption paths

## SQLite Mirror

Codex mirrors rollout metadata into local SQLite databases for fast query and lifecycle state. The state crate separates:

- raw rollout extraction
- thread metadata
- logs
- goals
- backfill state
- telemetry around DB init, fallback, and backfill

This is the right shape for long-running agent CLIs: append-only session artifacts remain canonical, while SQLite is an index/cache that can be rebuilt.

## Doctor Reports

Codex's `doctor` command emits both human-readable output and a redacted JSON report. Each check has:

- stable ID
- category
- status: ok, warning, or fail
- summary
- details
- structured issues
- remediation
- duration

Reuse that schema for support tooling. A good doctor report should be machine-readable first, then rendered for humans.

## Trace And Metric Hooks

Codex carries W3C trace context on submissions and emits trace IDs on turn start. It also records metrics for token usage, tool calls, skill rendering, DB initialization, and runtime events.

For new runtimes:

- propagate `traceparent` and `tracestate` through async queues
- include trace IDs in start events so UI and logs can correlate
- tag token metrics by token type, not just total
- measure skill/tool truncation and deferred loading because prompt budget affects behavior

## Traps

- Treating SQLite as canonical session storage instead of a rebuildable index.
- Emitting doctor output only as pretty terminal text.
- Losing trace context at UI -> core queue boundaries.
- Recording token totals without input/output/reasoning/cache breakdowns.
