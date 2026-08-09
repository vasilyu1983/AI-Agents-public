---
source_snapshot: openai/codex main branch (verified 2026-05-25)
anchors:
  - codex-rs/cli/src/main.rs — Resume, Fork, Cloud subcommand variants
  - codex-rs/external-agent-sessions/ — SQLite-backed session index (ledger.rs, records.rs, detect.rs)
  - codex-rs/config/src/config_toml.rs — config.toml path, sqlite_home, CODEX_HOME
---

# OpenAI Codex Session Persistence

## Table of Contents

- [When To Use](#when-to-use)
- [What It Covers](#what-it-covers)
- [Storage Architecture](#storage-architecture)
- [Session Resume](#session-resume)
- [Session Forking](#session-forking)
- [Cloud Task Resume](#cloud-task-resume)
- [Contrast With JSONL / Transcript Model](#contrast-with-jsonl--transcript-model)
- [Design Rules](#design-rules)
- [Anti-Patterns](#anti-patterns)

## When To Use

Use this reference when designing session resume, fork, or cloud-task-apply flows in a Codex-class coding-agent runtime, or when reviewing how Codex persists and queries session state.

## What It Covers

- SQLite-backed session index: crate structure, storage paths
- `codex resume` — UUID lookup and picker flow
- `codex fork` — branch semantics
- `codex cloud` — cloud task resume surface
- Contrast with JSONL/rollout transcript model (covered in `openai-codex-rollout-doctor-telemetry.md`)

## Storage Architecture

Codex uses two parallel persistence layers for sessions. Understanding the boundary prevents architectural confusion:

| Layer | Format | Purpose | Canonical? |
|-------|--------|---------|------------|
| Rollout JSONL | Append-only JSONL files | Durable transcript — prompts, tool calls, compaction markers, token counts | Yes — source of truth |
| SQLite index | `codex-rs/external-agent-sessions` | Fast lookup by session ID, title, recency; rebuildable from JSONL | No — rebuildable cache |

The SQLite index is managed by the `codex-rs/external-agent-sessions` crate:

- `ledger.rs` — session ledger: insert, update, query session records
- `records.rs` — record shapes: session metadata, thread IDs, timestamps
- `detect.rs` — detection helpers: find existing sessions by path or identity
- `export.rs` — export session metadata for external consumers

### Storage Path

Config file: `~/.codex/config.toml` (constant `CONFIG_TOML_FILE = "config.toml"`)

Storage paths default to `$CODEX_HOME` (e.g. `~/.codex/`):
- SQLite DB: `$CODEX_HOME` (or `$CODEX_SQLITE_HOME` if set)
- Logs: `$CODEX_HOME/log/`

## Session Resume

CLI subcommand: `codex resume`

> "Resume a previous interactive session (picker by default; use --last)"

Behavior:
- Default: opens an interactive picker over the SQLite session index, ordered by recency
- `--last`: bypasses the picker and resumes the most recent session directly
- With UUID: performs a direct lookup in the SQLite index; falls back to scanning JSONL if the index misses

Design implications:
- The SQLite index is the fast path; it must be kept consistent with rollout JSONL
- A session that exists in JSONL but not in the index should still be resumable via fallback scan — do not gate recoverability on index freshness
- Resume must clear stale derived caches (tool registry, config cache) before rebuilding live state from persisted transcript

## Session Forking

CLI subcommand: `codex fork`

> "Fork a previous interactive session (picker by default; use --last)"

Fork semantics:
- Creates a new session that starts with the transcript and context of the source session
- The source session remains unchanged; the fork is an independent branch
- Useful for exploring an alternative approach without losing the original thread

Contrast with resume: `resume` continues the same session in-place; `fork` branches off a copy. They share the same picker UI (session ID, recency ordering) but diverge after selection.

Design implication for storage: forked sessions need an ancestry reference (`forked_from: Option<SessionId>`) so developers can trace decision trees. This is different from how Claude Code tracks subagent context inheritance.

## Cloud Task Resume

CLI subcommand: `codex cloud` (alias: `cloud-tasks`)

> "[EXPERIMENTAL] Browse tasks from Codex Cloud and apply changes locally"

This surface connects local Codex invocations to Codex Cloud task history. The flow:
1. Fetch task metadata from Codex Cloud
2. Present task list (analogous to the local session picker)
3. User selects a cloud task
4. Codex downloads the task artifact and applies the diff locally

This is a different resume surface from `codex resume`:

| Surface | Source | What resumes |
|---------|--------|-------------|
| `codex resume` | Local SQLite + JSONL | Full interactive session with transcript |
| `codex cloud` | Codex Cloud API | Task artifacts (diffs, results); interactive session re-seed is separate |

## Contrast With JSONL / Transcript Model

The transcript model (documented in `openai-codex-rollout-doctor-telemetry.md`) is the canonical session record. This file covers the *index* and *lookup* layer on top of it.

Rule: treat SQLite as a rebuildable cache over the JSONL canonical record. If they diverge, JSONL wins.

The `external-agent-sessions` crate's `detect.rs` implements logic for detecting whether an existing session matches by path or identity — this is the entry point for both `resume` and `fork` picker flows.

## Design Rules

- Persist the SQLite index as a fast lookup cache; design the resume path to fall back to JSONL scan when the index is stale or missing.
- `fork` requires an `forked_from` ancestry field so session branching is traceable — do not treat it as just another new session.
- Cloud task resume and local session resume are different flows with different artifacts; do not conflate them in the UI.
- Storage paths should respect `$CODEX_HOME` and `$CODEX_SQLITE_HOME` so enterprise deployments can relocate them without patching config.
- Clear stale discovery caches (tool registry, config, MCP) before rebuilding live state after any resume.

## Anti-Patterns

- Treating SQLite as the source of truth and making sessions unrecoverable when the index is corrupt or missing.
- Implementing `fork` as a shallow copy that shares mutable state with the source session.
- Gating `codex cloud` task apply on the same code path as `codex resume` — they have different authentication, transport, and artifact shapes.
- Using human-readable session titles as the primary identity key for either resume or fork lookup.
