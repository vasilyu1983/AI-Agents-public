# Loading and Layers

## Table of Contents

- [Claude Code](#claude-code)
- [AGENTS.md in Claude Code (lookup step)](#agentsmd-in-claude-code-lookup-step)
- [Personal Layer Shared by Claude Code and Codex](#personal-layer-shared-by-claude-code-and-codex)
- [Other Runtimes (lookup step)](#other-runtimes-lookup-step)
- [Codex](#codex)
- [Codex Memories (Auto-Memory Layer)](#codex-memories-auto-memory-layer)
- [Codex config.toml (Complementary Layer)](#codex-configtoml-complementary-layer)

## Claude Code

- `CLAUDE.md` loads from the current working directory upward, so parent directories can provide shared guidance.
- Nested `CLAUDE.md` files load when Claude works inside those subtrees.
- `.claude/rules/*.md` lets you split topic-specific or path-scoped rules out of the main file.
- Local settings can exclude discovered `CLAUDE.md` files with `claudeMdExcludes`.
- Auto memory is a separate local layer for accumulated notes; use it for machine-local reminders, not as the main project contract.
- **Loaded layers concatenate. None of them overrides or replaces another.** Managed, user, project, local, rules, and nested files all end up in context together. When two of them conflict, the model sees both and may follow either. Fix conflicts by editing the files; do not rely on load order to settle them.
- Loading is asymmetric with Codex: Claude Code walks *up* from cwd at startup and lazily adds subdirectory files when it reads files there; Codex builds one chain from the project root *down* to cwd and reads nothing below cwd.
- Run `/context` and read the **Memory files** list to see which files actually loaded in a session; `/memory` lists locations and opens files for editing, including files that do not exist yet. Trust the `/context` list over any table, including the ones in this skill.

## AGENTS.md in Claude Code (lookup step)

Claude Code may read a repo's `AGENTS.md` directly, without a `CLAUDE.md` import or symlink, depending on version, provider, and configuration. Those conditions change between releases, so treat support as a lookup, never as a yes/no fact to memorize or state in a skill.

Durable rules:

- **A `CLAUDE.md`-family file can suppress `AGENTS.md`.** In the default mode, a `CLAUDE.md`, `.claude/CLAUDE.md`, or `CLAUDE.local.md` at or above cwd makes Claude Code read that file *instead of* `AGENTS.md`. The trap: one developer's gitignored `CLAUDE.local.md` silently drops the team's `AGENTS.md` for that developer only.
- **Native reading is not universal.** Some providers, configurations, and sessions fall back to `CLAUDE.md` only. Teams that mix providers (for example a cloud-platform deployment next to direct API use) need a bridge that works everywhere.
- **The loading mode is a user- or managed-level setting.** Project-level settings files may not be honoured for it, so a repo cannot force the mode on its contributors.
- **Claude Code does not read Codex-only files** such as `AGENTS.override.md`, `AGENTS.local.md`, or anything under `.agents/`. It does read `.claude/AGENTS.md` alongside a root `AGENTS.md`.
- **Hooks that fire on instruction loading may not fire for natively read `AGENTS.md`.** Check before building automation on them.

Before recommending "delete the symlink/import and rely on native reading", check the Claude Code memory docs and changelog (<https://code.claude.com/docs/en/memory>) for: the minimum version, which files suppress `AGENTS.md`, which providers and sessions are excluded, the setting name and its allowed values, and where that setting may live. Then confirm with `/memory` in a real session on each provider the team uses.

Decision: if every contributor runs a version and provider where native reading works and nobody keeps a `CLAUDE.md`-family file, native reading is enough. Otherwise keep the `@AGENTS.md` import (or symlink) as the portable bridge; it works whatever the native mode is.

## Personal Layer Shared by Claude Code and Codex

One person who uses both runtimes needs one personal file, not two. Keep the layers global to local:

| Layer | File | Holds |
|---|---|---|
| Personal, both runtimes | `~/.codex/AGENTS.md` (canonical) | How the agent works and writes for you in every repo: reply rules, git habits, verification habits |
| Personal, Claude Code entry | `~/.claude/CLAUDE.md` | One line, `@~/.codex/AGENTS.md`, plus a note to edit the canonical file |
| Project | repo `AGENTS.md` (and nested ones) | Project facts: layout, commands, conventions, boundaries, and lessons specific to this repo |

Setup:

1. Write the personal rules in `~/.codex/AGENTS.md`. Codex reads that path globally. Do not rely on Codex expanding `@` imports; check the Codex docs before you assume it does.
2. Create `~/.claude/CLAUDE.md` with the import line. A symlink from one path to the other also works; the import keeps a visible pointer.
3. Verify both runtimes. In Claude Code, `/memory` or `/context` lists the imported file; a headless check is `claude -p "Quote the first rule of my personal instructions"`. In Codex, `codex --show-context` (or the current equivalent) lists the personal file.

Rules for the repo layer:

- **Never copy personal rules into a repo file.** Loaded layers concatenate, so a copy spends the instruction budget twice, and the copies drift apart. A repo file may say "personal rules load from the user layer" in one line, but it needs no summary of them.
- **Keep repo-specific lessons local.** A lesson that names this repo's deploy split, sibling repos, or the user's shorthand in this project goes at the end of the repo `AGENTS.md`. A lesson that applies everywhere goes to the personal file.
- **A team rule is not a personal rule.** If teammates must follow it, put it in the repo file as a project rule; teammates do not load your personal file.

Traps:

- **The user-scope file does not suppress a repo `AGENTS.md`.** The suppression trap in the previous section concerns `CLAUDE.md`-family files at or above cwd. A repo that has its own `CLAUDE.md` without an `@AGENTS.md` import still hides its `AGENTS.md` from Claude Code; the personal layer loads either way. Fix the repo with the import, or set the loading mode at user level (look up the setting name).
- **Approval prompts for imports can differ by scope.** Imports of files outside the project may ask for approval in project files. Check the current memory docs, then confirm with `/memory` that the import loaded.
- **Audit with the loaded list, not the file list.** After setup, open one session per runtime in a repo that has its own `CLAUDE.md` and in one that does not. Confirm which files loaded.

For the reply-writing rules that usually fill the personal layer, see [reply-clarity-ste.md](reply-clarity-ste.md).

## Other Runtimes (lookup step)

Whether an agent runtime reads `AGENTS.md`, which file it treats as primary, and how it scopes nested or path-specific rules all change often. Do not keep a yes/no support table in memory or in this skill. For each runtime the team actually uses, check its own docs (and the list at <https://agents.md>) for:

1. Does it read `AGENTS.md` natively, only through configuration (some tools need an explicit "read this file" setting), or not at all?
2. What is its primary instruction file, and does a tool-specific file suppress or merge with `AGENTS.md`?
3. How does it scope rules: nested directory files, glob or `applyTo`-style path rules, or frontmatter activation?
4. Does it cap instruction-file size, and what happens past the cap (truncation or skipping)?

Durable rules that hold whatever the answers:

- Keep `AGENTS.md` the single source for cross-tool rules. Tool-specific files hold only what that tool alone needs, plus a pointer or import back to `AGENTS.md`.
- Never hand-maintain the same rule in two tool files. Bridge with an import, symlink, or generated copy, and lint for drift.
- For a runtime that cannot read `AGENTS.md`, generate its file from `AGENTS.md` rather than editing it by hand.
- Re-check the answers when a runtime ships a major release or the team adds a tool.

## Codex

- `AGENTS.md` is the primary project-memory file for Codex.
- Keep one concise file per directory that needs local context instead of relying on undocumented import chains.
- Codex also supports personal/global memory via `~/.codex/AGENTS.md`.
- At each global or project directory level, `AGENTS.override.md` takes precedence over `AGENTS.md`; Codex loads at most one instruction file per directory. An override can be developer-local or checked-in scoped guidance—its defining behavior is precedence, not Git status.
- Advanced Codex config can change discovery behavior with `project_doc_fallback_filenames` and `project_doc_max_bytes`. The byte cap applies to the combined chain: once it is reached Codex stops adding files, so a large root file silently starves the nested ones. Check the Codex config reference for the current default before a root file grows large.
- `codex` exposes an `/init` command that generates a starter `AGENTS.md` project-instructions scaffold — the Codex analog of bootstrapping `CLAUDE.md`.

## Codex Memories (Auto-Memory Layer)

Codex has an accumulated-recall layer (the Codex analog of Claude Code auto-memory). It is **separate from `AGENTS.md`** and must not be treated as the source of truth for rules that always apply. Official guidance: keep required team guidance in `AGENTS.md` or checked-in docs; treat memories as a helpful local recall layer.

- **Enable** in `~/.codex/config.toml` (or the Codex app settings):

  ```toml
  [features]
  memories = true
  ```

- **Storage**: under the Codex home directory, default `~/.codex/memories/` — machine-local, not committed.
- **Default**: off unless enabled (per the Codex config reference; re-check on a major release). Do not assume a teammate or fresh runner has the same recall layer you do.
- **Key sub-settings** (all under the `memories` table; verify names against the current Codex config reference before copying):

  | Key | Effect |
  |-----|--------|
  | `memories.generate_memories` | Whether new threads can be stored as memory-generation input |
  | `memories.use_memories` | Whether Codex injects existing memories into future sessions |
  | `memories.disable_on_external_context` | When `true`, keeps threads that used MCP tools, web search, or tool search out of memory generation |
  | `memories.min_rate_limit_remaining_percent` | Halts memory generation below this quota threshold |
  | `memories.extract_model` / `memories.consolidation_model` | Override the model used for per-thread extraction / global consolidation |

**Layer discipline (mirrors the Claude `CLAUDE.md` vs auto-memory split):** durable, must-always-apply rules → `AGENTS.md` (committed); evolving machine-local recall → Codex memories. If a "memory" is something every teammate must follow, it belongs in `AGENTS.md`, not the recall layer.

## Codex config.toml (Complementary Layer)

`config.toml` is the durable configuration layer that complements `AGENTS.md`. It handles operational infrastructure while `AGENTS.md` encodes team workflow guidance.

If the task is specifically about OpenClaw runtime setup, `openclaw.json`, workspace topology, or sandboxing, use `agents-openclaw-ops` instead of stretching this skill beyond project memory.

If the task is about session transcripts, resume flows, rewind, or cross-worktree recovery, use [../../ai-coding-agents-state/SKILL.md](../../ai-coding-agents-state/SKILL.md). Those are runtime session concerns, not durable project memory.

**Layering, highest precedence first**: CLI flags and `--config`; trusted project `.codex/config.toml` files from root to current directory (closest wins); a selected profile; user `~/.codex/config.toml`; system config; built-in defaults. Managed `requirements.toml` can constrain security-sensitive choices across those layers. Untrusted projects do not load project-scoped config, hooks, or rules. Route detailed precedence questions to `ai-coding-agents-settings-policy` so this memory skill does not duplicate the full policy model.

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

### Approval review is configuration, not project memory

Keep approval mechanics out of `AGENTS.md`. Put them in `config.toml`, a trusted project-scoped `.codex/config.toml`, an executable policy rule, or a temporary CLI/session override. `AGENTS.md` may state the team's workflow boundary (for example, "ask before deploying production"), but it does not grant filesystem or network authority and should not be used as an approval allowlist.

For automatic review without removing the workspace sandbox, use:

```toml
approval_policy = "on-request"
sandbox_mode = "workspace-write"
approvals_reviewer = "auto_review"
```

- `approvals_reviewer = "auto_review"` routes eligible approval prompts to the reviewer subagent; it does not widen the sandbox or change actions that are already allowed inside it.
- Keep `approval_policy = "on-request"` when prompts may still be needed. `approval_policy = "never"` suppresses prompts but does not grant missing filesystem or network capabilities.
- Use `/permissions` to adjust the active permission profile during a session. If automatic review denies an action that the user has checked and intends to allow, `/approve` retries one recent denial.
- Persist narrow command-prefix rules only for stable, reviewed commands. A rule allowing a mutable repository wrapper script also trusts future changes to that script, so prefer the smallest useful subcommand prefix and keep destructive primitives denied.

Note: `config.toml` is shared across Codex CLI, IDE extension, and Codex app.
