# Resume Path Decision Tree

Use this reference when deciding which session-resume mechanism to use. Apply at design time (choosing an architecture) and at runtime (code that dispatches to the right resume path).

## Table of Contents

- [Decision Tree](#decision-tree)
- [Path Comparison](#path-comparison)
- [Invariants](#invariants)
- [Prompt-cache economics in subagent spawning](#prompt-cache-economics-in-subagent-spawning)
- [Anti-patterns](#anti-patterns)
- [Related](#related)

## Decision Tree

```
Start: Why does the session need to resume?
│
├── User explicitly named a session ID (flag, env var, deep link)
│   └── → Session-ID direct resume
│       - Validate ID format before lookup
│       - Clear stale discovery caches
│       - Fail hard with a clean error if not found (no silent fallback to picker)
│
├── User ran `--continue` or `/continue` without naming a session
│   └── → Most-recent-session shortcut
│       - Resolve from session index, sorted by last-active timestamp
│       - If only one session exists: resume directly
│       - If multiple sessions exist: show picker (see picker path below)
│
├── User is looking for a session by keyword, title, or description
│   └── → Interactive picker / fuzzy search
│       - Exclude: current session, sidechain-only artifacts, corrupted entries
│       - Rank by: last-active, then title match score
│       - If exactly one match: offer direct resume with confirm
│       - If zero matches: fall through to direct-log fallback
│
├── Session is in a different git worktree on the same repo
│   └── → Same-repo worktree adoption
│       - Check: does the session's stored worktree path still resolve?
│         ├── YES → resume with worktree relocation note in the REPL
│         └── NO  → offer to re-attach to current worktree (user confirms)
│       - Never silently adopt a session from a different project
│
├── Session was started by an editor (Zed, JetBrains, etc.) via ACP stdio
│   └── → ACP session re-attach
│       - Client sends `session/resume` with `session_id` on new stdin pipe
│       - Agent looks up session from daemon-side store (not from transcript file)
│       - If found: replay catch-up messages (seq > last_seq), re-attach sender
│       - If not found: return `session_not_found`; editor starts new session
│       - Process restart does NOT lose session state if daemon-owned store is used
│
├── User wants to try an alternative approach without losing the current thread (not a recovery case — a branch case)
│   └── → Session branch, not resume
│       - In-session: `/branch [name]` — copies the conversation so far into a new session and switches into it
│       - From the shell: `claude --continue --fork-session` or `claude --resume <id> --fork-session`
│       - The source session is untouched and stays in the picker; the new branch is grouped under it
│       - Permissions granted with "allow for this session" do NOT carry over to the branch — re-grant explicitly
│       - Do not route this through the resume paths below; it creates a new session ID rather than recovering an existing one
│
├── Session was spawned from a Goose-style recipe
│   └── → Recipe re-seed
│       - Two resume modes (show both in UI):
│         1. "Replay transcript" — high fidelity, large artifact
│         2. "Re-run from recipe + last checkpoint" — deterministic, small
│       - Prefer recipe re-seed when transcript references tools no longer in scope
│       - Fall back to transcript replay if no `seed_ref` is stored in session metadata
│
└── No session found through any of the above paths
    └── → Direct-log / transcript fallback
        - Scan session storage directory for transcript files matching the session ID
        - Do not use enriched index as the only lookup; it may be stale
        - If transcript found: rebuild session metadata from raw log, then resume
        - If nothing found: declare session unrecoverable, offer to start fresh
```

## Path Comparison

| Path | Trigger | Requires | Fails when |
|------|---------|----------|-----------|
| Session-ID direct | Explicit flag or deep link | Valid ID in session store | ID not found (no fallback) |
| Most-recent shortcut | `--continue` with no ID | Session index with timestamps | Index corrupted or empty |
| Interactive picker | `--continue` + multiple candidates, or `/resume` | Active terminal; session index | Headless mode; all sessions excluded by filter |
| Worktree adoption | Same repo, different worktree | Repo-root match; user confirmation | Different project root |
| Session branch | `/branch` or `--fork-session` | An existing session to copy from | N/A — always succeeds by creating a new session; not a recovery path |
| ACP re-attach | Editor reconnects over stdio | Daemon-owned session store | Process restarted without persistent store |
| Recipe re-seed | Session has `seed_ref` in metadata | Recipe version still resolvable | Recipe version gone; extension set changed |
| Direct-log fallback | All above failed | Transcript files on disk | Storage wiped; encrypted storage without key |

## Invariants

- Session identity must use a stable UUID, not the human-readable title.
- Picker flows must exclude the current active session and sidechain-only artifacts.
- Same-repo worktree and cross-project sessions must follow different code paths. Never conflate them.
- Stale discovery caches (file index, skill index, config) must be cleared before any resume path rebuilds live state.
- ACP re-attach must be daemon-side (process-outliving) state; binding session lifetime to a file descriptor is the canonical anti-pattern.
- Recipe re-seed must offer transcript replay as an alternative; never silently re-run the recipe without showing the user which mode was chosen.
- Branching is not resume: it always succeeds (it copies rather than recovers) and always produces a new session ID. Keep it out of the failure-driven decision tree above except as the explicit "don't route here" leaf — conflating the two makes users lose track of which session is authoritative.

## Prompt-cache economics in subagent spawning

Session resume decisions interact with prompt-cache prefix sharing. When a subagent is spawned from a lead session:

- A **blank subagent** starts fresh — no cache overlap with the lead. Use when the subagent task is entirely independent and tool sets differ significantly.
- A **forked subagent** (`CLAUDE_CODE_FORK_SUBAGENT=1` or `/fork`) copies the lead's context prefix and maximizes prompt-cache hits. Use when the subagent needs most of the same system prompt, tool list, and project instructions. See [`../ai-coding-agents-sessions/references/context-forking.md`](context-forking.md) for economics.

Resume path interacts with fork: resuming a forked subagent from transcript is safe; resuming via recipe re-seed requires re-pinning the extension list to the parent's envelope, not the recipe's original envelope.

For full prompt-cache economics in subagent spawning, see [`../../ai-coding-agents-sessions/SKILL.md`](../SKILL.md) and [`context-forking.md`](context-forking.md).

## Anti-patterns

- Using title as primary session identity and silently resolving to a wrong session when titles collide.
- Declaring a session unrecoverable without checking direct-log fallback.
- Treating enriched session indexes as the only source of truth (they lag behind, can be corrupted, and may not exist in fresh environments).
- Adopting a cross-project session silently — always require explicit user confirmation.
- Binding ACP session lifetime to the editor process PID; the editor may restart without the agent restarting.

## Related

- [`session-lifecycle-and-resume.md`](session-lifecycle-and-resume.md) — Session identity, picker flows, cache clearing, and resume entrypoints
- [`context-forking.md`](context-forking.md) — Blank vs. forked subagent startup and cache-prefix economics
- [`../../ai-coding-agents-remote-runtime/references/recipe-reconnect-with-sequence.md`](../../ai-coding-agents-remote-runtime/references/recipe-reconnect-with-sequence.md) — ACP reconnect with sequence numbers
