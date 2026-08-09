# Loading and Layers

## Table of Contents

- [Claude Code](#claude-code)
- [Codex](#codex)
- [Codex Memories (Auto-Memory Layer)](#codex-memories-auto-memory-layer)
- [Codex config.toml (Complementary Layer)](#codex-configtoml-complementary-layer)

## Claude Code

- `CLAUDE.md` loads from the current working directory upward, so parent directories can provide shared guidance.
- Nested `CLAUDE.md` files load when Claude works inside those subtrees.
- `.claude/rules/*.md` lets you split topic-specific or path-scoped rules out of the main file.
- Local settings can exclude discovered `CLAUDE.md` files with `claudeMdExcludes`.
- Auto memory is a separate local layer for accumulated notes; use it for machine-local reminders, not as the main project contract.

## Codex

- `AGENTS.md` is the primary project-memory file for Codex.
- Keep one concise file per directory that needs local context instead of relying on undocumented import chains.
- Codex also supports personal/global memory via `~/.codex/AGENTS.md`.
- Use `AGENTS.override.md` only for local developer overrides that should not be committed as the shared contract.
- Advanced Codex config can change discovery behavior with `project_doc_fallback_filenames` and `project_doc_max_bytes`.
- `codex` exposes an `/init` command that generates a starter `AGENTS.md` project-instructions scaffold — the Codex analog of bootstrapping `CLAUDE.md`.

## Codex Memories (Auto-Memory Layer)

Codex now ships an accumulated-recall layer (the Codex analog of Claude Code auto-memory). It is **separate from `AGENTS.md`** and must not be treated as the source of truth for rules that always apply. Official guidance: keep required team guidance in `AGENTS.md` or checked-in docs; treat memories as a helpful local recall layer.

- **Enable** in `~/.codex/config.toml` (or the Codex app settings):

  ```toml
  [features]
  memories = true
  ```

- **Storage**: under the Codex home directory, default `~/.codex/memories/` — machine-local, not committed.
- **Default-off jurisdictions**: memories are **off by default in the EEA, the UK, and Switzerland** until explicitly enabled. Do not assume a teammate in those regions has the same recall layer you do.
- **Key sub-settings** (all under the `memories` table):

  | Key | Effect |
  |-----|--------|
  | `memories.generate_memories` | Whether new threads can be stored as memory-generation input |
  | `memories.use_memories` | Whether Codex injects existing memories into future sessions |
  | `memories.disable_on_external_context` | When `true`, keeps threads that used MCP tools, web search, or tool search out of memory generation (default `false`) |
  | `memories.min_rate_limit_remaining_percent` | Halts memory generation below this quota threshold |
  | `memories.extract_model` / `memories.consolidation_model` | Override the model used for per-thread extraction / global consolidation |

**Layer discipline (mirrors the Claude `CLAUDE.md` vs auto-memory split):** durable, must-always-apply rules → `AGENTS.md` (committed); evolving machine-local recall → Codex memories. If a "memory" is something every teammate must follow, it belongs in `AGENTS.md`, not the recall layer.

## Codex config.toml (Complementary Layer)

`config.toml` is the durable configuration layer that complements `AGENTS.md`. It handles operational infrastructure while `AGENTS.md` encodes team workflow guidance.

If the task is specifically about OpenClaw runtime setup, `openclaw.json`, workspace topology, or sandboxing, use `agents-openclaw-ops` instead of stretching this skill beyond project memory.

If the task is about session transcripts, resume flows, rewind, or cross-worktree recovery, use [../../ai-coding-agents-sessions/SKILL.md](../../ai-coding-agents-sessions/SKILL.md). Those are runtime session concerns, not durable project memory.

**Layering**: `~/.codex/config.toml` (personal) → `.codex/config.toml` (repo) → CLI overrides.

| What goes where | config.toml | AGENTS.md |
|----------------|-------------|-----------|
| Model defaults, reasoning effort | ✓ | |
| Sandbox and approval policies | ✓ | |
| MCP server connections | ✓ | |
| Multi-agent limits, experimental features | ✓ | |
| Repo layout, key directories | | ✓ |
| Build, test, lint commands | | ✓ |
| Engineering conventions, PR standards | | ✓ |
| Constraints and prohibitions | | ✓ |
| Verification methods | | ✓ |

Note: `config.toml` is shared across Codex CLI, IDE extension, and Codex app.
