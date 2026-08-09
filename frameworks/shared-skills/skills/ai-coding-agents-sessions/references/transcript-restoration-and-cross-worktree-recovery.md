# Transcript Restoration And Cross-Worktree Recovery

## Table Of Contents

- [Design Goal](#design-goal)
- [Transcript vs Summary State](#transcript-vs-summary-state)
- [Cross-Worktree Recovery](#cross-worktree-recovery)
- [Failure Handling](#failure-handling)

## Design Goal

Long-lived coding-agent sessions need more than raw message replay. They need a recovery model for:

- visible REPL history
- transcript side data
- summary or collapse stores
- worktree-aware session selection

The `claude_code` comments around `query.ts`, `resume.tsx`, and `main.tsx` show this separation clearly.

## Transcript vs Summary State

The source indicates that not all conversation state lives in the visible REPL array:

- some summary or collapse information persists outside the immediate message list
- some session fields are persisted specifically because resume needs to read them back

That yields a strong rule:

- keep the user-visible transcript separate from compressed or support-state stores
- resume should restore both where needed, but not confuse them as one data structure

## Cross-Worktree Recovery

The picker flow distinguishes:

- same-directory sessions
- same-repo worktree sessions
- different-project sessions

Same-repo worktrees can often be resumed directly. Different-project sessions should usually return an explicit command so the user changes context intentionally.

This avoids unsafe implicit cwd switches and makes recovery auditable.

Useful restore sequence from the source behavior:

1. resolve the target session by stable ID when possible
2. if enriched picker data misses the session, try direct log lookup
3. load the full conversation payload
4. restore transcript and session metadata
5. restore agent mode, worktree state, and cost state
6. rebuild environment-dependent caches and agent definitions
7. only then hand control back to the live REPL

## Failure Handling

Model these failure paths explicitly:

- session not found
- multiple matches for a title
- stale or missing worktree path
- failed full-log load for lite logs
- resume partially starts but cannot finish

The runtime should return a clear error or fallback picker state instead of silently dropping into a mismatched session.

## Edge Cases And Workarounds

Additional cases worth documenting for a real clone:

- picker data is partial
  - support progressive loading rather than blocking on global history hydration
- current session appears in results
  - exclude it so resume does not loop back into the active session
- sidechain-only or support-only logs appear
  - keep them out of normal operator-facing resume flows
- same-repo worktree resume
  - allow direct recovery when the workspace relationship is still valid
- cross-project resume
  - show an explicit next command rather than silently teleporting cwd
- transcript collapse or summary state exists outside the visible message list
  - restore it explicitly; do not assume replaying messages is enough

Practical tip:

- separate "can identify the session" from "can safely restore the runtime context"
- many resume bugs come from treating those as the same operation
