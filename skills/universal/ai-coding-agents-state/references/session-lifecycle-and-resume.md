# Session Lifecycle And Resume

## Table Of Contents

- [Design Goal](#design-goal)
- [Session Identity](#session-identity)
- [Resume Entry Modes](#resume-entry-modes)
- [Cache Handling](#cache-handling)
- [Picker And Search Behavior](#picker-and-search-behavior)
- [Store Schema And Retention](#store-schema-and-retention)
- [Reference Implementation: Claude Code (verify against current docs)](#reference-implementation-claude-code-verify-against-current-docs)

## Design Goal

Coding-agent CLIs should treat resume as a controlled state transition, not a best-effort convenience command. Session identity, picker flows, stale-cache clearing, and search aliases are all part of the runtime contract.

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

The reference CLI clears stale session caches before resuming so file and skill discovery are fresh.

That is a critical rule:

- transcript and session identity may be trusted from storage
- discovery caches should not be trusted across resume

Resume should restore persisted state, then rebuild the environment-dependent parts.

## Picker And Search Behavior

The reference resume flow also shows two useful UI rules:

- exclude the current session and sidechain-only logs from the picker
- same-repo worktrees can resume directly, while other-project sessions should produce an explicit resume command instead of silently teleporting the user

That boundary is worth copying because it keeps resume predictable and reviewable.

## Store Schema And Retention

The session store holds transcripts, indexes, checkpoints, and metadata. It outlives any one binary, so version it separately from the app.

- **Stamp a schema version in the store.** Use one version per store, or one per file for append-only transcripts. Read it before any read or write.
- **Migrate forward only.** Each migration moves the store from version N to N+1 and is idempotent, so re-running it after a crash is safe. Record completion before you move the version stamp. Write no down-migrations: rollback means restoring the backup.
- **Back up before migrating.** Snapshot the store, or the files the migration touches, and confirm the snapshot is readable before the first write. If the migration fails, restore the snapshot and start on the old version; never leave a half-migrated store. Keep the snapshot until the rollback window closes.
- **Prefer additive changes**, such as new optional fields or new files, so older clients can still read the store. Bump the major schema version only for a change that an older reader would misread.
- **An older client must never write to a newer store.** It may open the store read-only when the schema promises that older readers can ignore additions. Otherwise it refuses with a message that names both versions and tells the user to upgrade. A store that fails to parse is quarantined, never repaired, downgraded, or truncated.
- **Bound growth with a documented retention policy.** Transcripts, checkpoints, and debug logs grow without limit unless a policy caps them by age and total size. Prune at startup or on a schedule, not mid-session. Never prune a session that holds a live lease or that the user pinned. Give debug logs their own, shorter retention class than transcripts. Document the policy and the setting that changes it.

## Reference Implementation: Claude Code (verify against current docs)

These patterns from one shipped CLI sharpen the abstract rules above. Paths, flags, keys and scoping change between releases; check the runtime's sessions docs before quoting them.

- **Storage format is internal:** transcripts are per-project, per-session JSONL files whose entry format the vendor documents as internal and version-fragile. Build against export or the scripting interfaces (JSON output mode, the hook transcript path, the Agent SDK), not by parsing the JSONL directly.
- **Resume-by-ID scope is a decision, not an accident:** decide whether ID lookup covers only the current project and its worktrees or every project. If out-of-scope IDs are rejected, fail with a clean "not found"; if they resolve, make the directory switch explicit (show or copy the command) rather than silently teleporting the user. Scope has changed across releases of the reference CLI, so check its docs before copying either behaviour.
- **Picker default scope and widen actions:** the picker defaults to the current worktree plus explicitly added directories, with separate actions to widen to all worktrees of the repo, to every project, or to filter by branch. Exposing scope as an explicit, reversible widen action (rather than showing everything by default) is the reusable pattern.
- **Name resolution is exact-or-explicit:** `claude --resume <name>` and `/resume <name>` only match names the user set (`/rename`, `-n` at startup, or accepting a plan). An ambiguous name either opens the picker pre-filled with the name as a search term (CLI form) or reports an error and asks the user to run the bare picker command (in-session form) — never silently guesses.
- **Cross-project selection in the picker copies a command, it does not jump:** selecting a session from an unrelated project in the widened picker copies a `cd`-and-resume command to the clipboard instead of switching the working directory underneath the user. This is the concrete implementation of "cross-project resume must be explicit."
- **PR-linked resume exists as a first-class entrypoint:** a resume-from-PR option resumes the session tied to a given pull request, and pasting a PR/MR URL into picker search finds the session that created it. Worth modeling as a named resume path alongside ID and title lookup, not bolted on as a search hack.
