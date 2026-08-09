# Session Lifecycle And Resume

## Table Of Contents

- [Design Goal](#design-goal)
- [Session Identity](#session-identity)
- [Resume Entry Modes](#resume-entry-modes)
- [Cache Handling](#cache-handling)
- [Picker And Search Behavior](#picker-and-search-behavior)
- [Confirmed Storage And Scoping (Claude Code)](#confirmed-storage-and-scoping-claude-code)

## Design Goal

Coding-agent CLIs should treat resume as a controlled state transition, not a best-effort convenience command. Claude Code's public docs (re-verified 2026-07-11 against `code.claude.com/docs/en/sessions`) confirm that session identity, picker flows, stale-cache clearing, and search aliases are all part of the runtime contract.

## Session Identity

The resume flow uses a stable session ID as the primary identity, then layers convenience lookup on top:

- UUID session ID
- custom title search
- interactive session picker

That is the right order:

- stable ID for correctness
- titles and search for human usability
- picker fallback when the input is ambiguous

## Resume Entry Modes

The source supports several resume entry shapes:

- explicit session ID
- interactive picker when no argument is provided
- exact custom-title match
- search-term fallback when the title is ambiguous
- filtered entrypoints such as PR-related resume paths

Use the same idea in new runtimes: one resume command can support multiple operator entry modes without changing the underlying restore contract.

## Cache Handling

`main.tsx` clears stale session caches before resuming so file and skill discovery are fresh.

That is a critical rule:

- transcript and session identity may be trusted from storage
- discovery caches should not be trusted across resume

Resume should restore persisted state, then rebuild the environment-dependent parts.

## Picker And Search Behavior

`resume.tsx` also shows two useful UI rules:

- exclude the current session and sidechain-only logs from the picker
- same-repo worktrees can resume directly, while other-project sessions should produce an explicit resume command instead of silently teleporting the user

That boundary is worth copying because it keeps resume predictable and reviewable.

## Confirmed Storage And Scoping (Claude Code)

The following details were re-verified against public docs on 2026-07-11 and sharpen the abstract rules above into concrete behavior worth copying:

- **Storage path:** transcripts default to `~/.claude/projects/<project>/<session-id>.jsonl`, where `<project>` is the working-directory path with non-alphanumeric characters replaced by `-`. Anthropic documents this entry format as internal and version-fragile — build against `/export` or the scripting interfaces (`claude -p --output-format json`, hook `transcript_path`, Agent SDK), not by parsing the JSONL directly.
- **Scoping is strict, not best-effort:** session-ID lookup for `claude --resume <id>` is scoped to the current project directory and its git worktrees. A session created elsewhere returns a clean "No conversation found" error rather than a silent cross-project resume — copy this fail-closed default.
- **Picker default scope and widen keys:** the picker defaults to the current worktree plus any directory added via `/add-dir`. `Ctrl+W` widens to all worktrees of the current repo; `Ctrl+A` widens to every project on the machine; `Ctrl+B` filters to the current git branch. Exposing scope as an explicit, reversible widen action (rather than showing everything by default) is the reusable pattern.
- **Name resolution is exact-or-explicit:** `claude --resume <name>` and `/resume <name>` only match names the user set (`/rename`, `-n` at startup, or accepting a plan). An ambiguous name either opens the picker pre-filled with the name as a search term (CLI form) or reports an error and asks the user to run the bare picker command (in-session form) — never silently guesses.
- **Cross-project selection in the picker copies a command, it does not jump:** selecting a session from an unrelated project in the widened picker copies a `cd`-and-resume command to the clipboard instead of switching the working directory underneath the user. This is the concrete implementation of "cross-project resume must be explicit."
- **PR-linked resume exists as a first-class entrypoint:** `claude --from-pr <number>` resumes the session tied to a given pull request, and pasting a PR/MR URL into picker search finds the session that created it. Worth modeling as a named resume path alongside ID and title lookup, not bolted on as a search hack.
