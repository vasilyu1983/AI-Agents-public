---
source_snapshot: openai/codex main branch (verified 2026-05-25)
anchors:
  - codex-rs/cli/src/main.rs — Resume, Fork, Cloud subcommand variants
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

- Session index layer: its role as a rebuildable cache, storage paths
- `codex resume` — UUID lookup and picker flow
- `codex fork` — branch semantics
- `codex cloud` — cloud task resume surface
- Contrast with JSONL/rollout transcript model (covered in the observability-evals rollout reference)

## Storage Architecture

Codex uses two parallel persistence layers for sessions. Understanding the boundary prevents architectural confusion:

| Layer | Format | Purpose | Canonical? |
|-------|--------|---------|------------|
| Rollout JSONL | Append-only JSONL files | Durable transcript — prompts, tool calls, compaction markers, token counts | Yes — source of truth |
| Session index | Local database (check current source for the module) | Fast lookup by session ID, title, recency; rebuildable from JSONL | No — rebuildable cache |

Do not attribute the index to `codex-rs/external-agent-sessions`: a verification pass found that crate is not the session index. Check the current `openai/codex` source before citing a module or file name. The design rule does not depend on it: the index is a rebuildable lookup cache over the rollout log.

### Storage Path

Config file: `~/.codex/config.toml` (constant `CONFIG_TOML_FILE = "config.toml"`)

Storage paths default to `$CODEX_HOME` (e.g. `~/.codex/`):
- Index database: under `$CODEX_HOME` (a separate home override exists; check current config docs)
- Logs: `$CODEX_HOME/log/`

## Session Resume

CLI subcommand: `codex resume`

> "Resume a previous interactive session (picker by default; use --last)"

Behavior:
- Default: opens an interactive picker over the session index, ordered by recency
- `--last`: bypasses the picker and resumes the most recent session directly
- With UUID: direct lookup by ID. Design the lookup to fall back to the rollout log if the index misses

Design implications:
- The index is the fast path; it must be kept consistent with rollout JSONL
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
| `codex resume` | Local index + rollout JSONL | Full interactive session with transcript |
| `codex cloud` | Codex Cloud API | Task artifacts (diffs, results); interactive session re-seed is separate |

## Contrast With JSONL / Transcript Model

The transcript model (documented in [`openai-codex-rollout-doctor-telemetry.md`](../../ai-coding-agents-observability-evals/references/openai-codex-rollout-doctor-telemetry.md)) is the canonical session record. This file covers the *index* and *lookup* layer on top of it.

Rule: treat the index as a rebuildable cache over the JSONL canonical record. If they diverge, JSONL wins. `resume` and `fork` share one picker and lookup path; keep session matching by path or identity in one place.

## Design Rules

- Persist the index as a fast lookup cache; design the resume path to fall back to JSONL scan when the index is stale or missing.
- `fork` requires an `forked_from` ancestry field so session branching is traceable — do not treat it as just another new session.
- Cloud task resume and local session resume are different flows with different artifacts; do not conflate them in the UI.
- Storage paths should respect the home-directory overrides so enterprise deployments can relocate them without patching config.
- Clear stale discovery caches (tool registry, config, MCP) before rebuilding live state after any resume.

## Anti-Patterns

- Treating the index as the source of truth and making sessions unrecoverable when the index is corrupt or missing.
- Implementing `fork` as a shallow copy that shares mutable state with the source session.
- Gating `codex cloud` task apply on the same code path as `codex resume` — they have different authentication, transport, and artifact shapes.
- Using human-readable session titles as the primary identity key for either resume or fork lookup.
