# Session Storage: Background Sessions, Checkpointing, and Compaction

Moved from the former sessions skill. The main SKILL.md carries the rules; this file carries the detail behind background-agent sessions, checkpoint and rewind design, the rewind-versus-git-versus-branch comparison, and the compaction contract.

## Background Agent Sessions

Some runtimes run agent sessions under a supervisor process that outlives the terminal, with a roster of jobs the user can re-attach to. Commands, storage paths, idle timeouts, retention defaults and settings names change between releases: read the runtime's current agent-view (or equivalent) and settings docs before quoting any of them.

Durable rules:

- **Session state must survive a supervisor restart.** Flush state at each checkpoint. In-flight children (shell commands, subagents, scheduled tasks) are handed off across the restart or marked "outcome unknown"; never silently dropped or re-run.
- **The roster is a rebuildable cache**, not the source of truth. Pickers may read it, but a crashed supervisor must be recoverable from per-job state.
- **Each background session edits in its own worktree**, and merging results back is an explicit action. Auto-commit, push or draft-PR from an isolated worktree is an explicit policy setting, never a default to copy.
- **A managed setting may remove the whole feature**, not just its UI. Never assume background sessions exist.
- **A session misread as empty on restart is quarantined, not discarded.** Rename or set it aside so it stays recoverable.
- **One retention policy covers transcripts, finished jobs and their worktrees.** Document it; do not let worktrees outlive their job silently.

Resume path for a background session: **re-attach by exact job ID is the default**; the roster picker is the fallback when the ID is unknown; if the feature is disabled, fall back to ordinary resume by ID. CI polls the roster's machine-readable output for completion before collecting results. In [`references/resume-path-decision-tree.md`](resume-path-decision-tree.md) this path sits between exact-ID resume and picker search.

## Checkpointing and Rewind

Claude Code creates a new checkpoint on every user prompt, capturing the code state before that prompt's edits begin. Checkpoints track **only file changes made through the agent's own file-editing tools**. They do not capture files touched by shell commands (`rm`, `mv`, `cp`, etc.) or by any process outside the session. That is a load-bearing limitation, not an edge case: any runtime cloning this pattern must decide explicitly whether to widen tracked-change scope beyond editor-tool calls, and must not imply broader coverage than it has.

Mode rules (the entry keys and menu layout are UI detail; check the runtime's checkpointing docs):

- **Restore modes discard state:** restore code, restore conversation, or both, back to the chosen point.
- **Summarize modes are non-destructive:** "summarize from here" or "up to here" collapses one side of a chosen point into a summary, keeps the other side verbatim, and keeps the original messages in the transcript.
- **`/clear` starts a new, resumable session.** It does not destroy the previous session's checkpoints; the old session stays independently resumable and rewindable.

### Design Implications for Session Storage

- Checkpoints are runtime state, not project memory — they live in the session layer alongside transcripts
- Checkpoints persist across session resume, so a user can close the terminal and still rewind later
- Checkpoint storage should be cheap per operation (copy-on-write or incremental diff) to avoid blocking the agent loop
- The rewind menu should clearly distinguish restore modes (conversation vs code vs both) from the two non-destructive summarize modes, since only the restore modes actually discard state
- Document the bash-command blind spot explicitly in any user-facing rewind UI — silently implying full coverage is the most common trust-breaking bug in this feature class

### Rewind vs Git vs Session Branching

Checkpointing is not a replacement for git, and it is not the same primitive as branching a session. Three distinct mechanisms solve three distinct problems — conflating them is a common design mistake:

| Mechanism | Scope | What survives | Use when |
|---|---|---|---|
| Rewind / checkpoint (`/rewind`) | Same session, same conversation | Files reverted via copy-on-write/diff; conversation truncated or summarized in place | Undo the agent's own recent edits or steer the current thread without starting over |
| Session branch (`/branch`, or `claude --continue`/`--resume <id> --fork-session`) | New, independent session — a full copy of the conversation so far | Original session is untouched and stays resumable; the new session diverges from that point forward | Try a different top-level approach while preserving the path you were on; A/B test prompting or implementation strategy from the same loaded context |
| Git commit | Durable, cross-session, cross-tool | Whatever you committed, forever | Permanent history and collaboration |

Rewind and `/branch`/`--fork-session` are easy to confuse because both "go back to an earlier point," but rewind mutates the current session in place while branching spins up a second, independent session ID that shows up grouped under the root session in the picker. Whether session-scoped approvals carry into a branch differs by runtime and release; do not document either answer as fixed. Design the branch to re-derive grants from current policy (see Rules and Traps) and check the runtime's docs for its actual behaviour. Users should still commit to git regularly — rewind and branching are for fast in-session experimentation, not long-term version control.

### Integration With Compaction

Checkpoints interact with compaction: "Summarize from here" and "Summarize up to here" let the user choose a point to compact around, keeping the side that matters intact while compressing the rest. This is a more targeted alternative to auto-compaction at the context limit, which always summarizes the entire history.

### Compaction Contract

Treat compaction as a state transition with a written contract, not a best-effort summary:

- **Name what is re-injected after the summary** (for example recently read files, loaded instructions and memory, invoked skills, plan or task state) and **give each item its own bound**, so re-injection cannot refill the window.
- **Name what is lost.** Tool outputs and files not re-injected must be re-read on demand; the summary must say so rather than imply full recall.
- **Record the boundary** in the transcript (a compaction marker with what was kept) so rewind, resume and debugging can see where detail ends.
- **Check the runtime's docs for its current re-injection set and limits** before depending on a specific item surviving compaction.

