# Context Lifecycle and Per-Turn Branching

## Table of Contents

- [What Is in the Context Window](#what-is-in-the-context-window)
- [Context Rot](#context-rot)
- [The Five Options at Every Turn](#the-five-options-at-every-turn)
- [Rewind > Correction](#rewind--correction)
- [Compact vs Clear](#compact-vs-clear)
- [Subagents as Context Management](#subagents-as-context-management)
- [When to Start a New Session](#when-to-start-a-new-session)
- [Decision Flow Between Turns](#decision-flow-between-turns)
- [Design Implications for Coding-Agent Runtimes](#design-implications-for-coding-agent-runtimes)
- [See Also](#see-also)

When a session has a large context window (Claude Code's is 1M tokens), session management shifts from "avoid running out" to **deciding what belongs in the window at every turn**. This reference covers the decision points between turns and the behaviour of the four context-management tools: continue, rewind, clear, and compact — plus subagents as a fifth escape.

For the runtime storage layer (session identity, resume, transcript persistence), see [`session-lifecycle-and-resume.md`](session-lifecycle-and-resume.md) and the Checkpointing and Rewind section in the parent SKILL.

## What Is in the Context Window

Every turn, the model sees all of:

- System prompt (loaded memory, repo instructions)
- Full conversation so far (user + assistant messages)
- Every tool call request and its full output
- Every file that has been read

This is why tool-heavy turns and file-read turns balloon context much faster than pure-chat turns. A single `grep` across a large repo can cost more than 20 back-and-forth messages.

## Context Rot

Model performance degrades as the window grows — attention thins across more tokens and older irrelevant content starts distracting from the current task. On Claude Code's 1M model, rot becomes **noticeable around ~300–400k tokens**, but it is highly task-dependent and not a fast rule. Complex reasoning degrades first, instruction following next.

Consequence: the model is at its **least intelligent point exactly when the context is largest** — which is exactly when compaction has to run. This is why bad compacts happen (see below).

## The Five Options at Every Turn

When Claude finishes a turn, five actions are available. "Continue" is the natural choice, but the other four exist specifically to manage context.

| Option | Shortcut | What happens | When it's right |
|---|---|---|---|
| **Continue** | just reply | Keep everything, add next turn | Current context is still relevant and below rot zone |
| **Rewind** | `Esc Esc` or `/rewind` | Drop messages after a chosen point; re-prompt from there | Claude tried an approach and it didn't work — you know why it failed |
| **Clear** | `/clear` | New session, zero carryover | New task, or context is no longer useful and you can summarise what matters yourself |
| **Compact** | `/compact` | Model summarises history, replaces it with the summary | Current work must continue but context has grown too large |
| **Subagent** | `Agent` tool / explicit request | Delegate to a fresh-context agent; only the result returns | Next chunk of work will produce noise you don't need later |

## Rewind > Correction

The single habit that signals good context management: **rewind instead of correcting**.

Anti-pattern:
```
Claude reads 5 files, tries approach A, fails.
User: "That didn't work, try B instead."
```
All 5 file reads + the failed approach A are still in context. Every subsequent turn pays for them.

Better:
```
Esc Esc → jump back to just after the file reads
User: "Don't use approach A — the foo module doesn't expose that. Go straight to B."
```
Failed attempt is gone. File reads are preserved (they were useful). Claude re-enters the fork with what you learned.

**Summarise from here** is the extended form: before rewinding, ask Claude to write a handoff message summarising what it tried and what it learned. Then rewind and paste that as the next prompt — a note from the previous iteration of Claude to its future self.

## Compact vs Clear

Both shed weight; they behave very differently.

| | Compact (`/compact`) | Clear (`/clear`) |
|---|---|---|
| Who decides what matters | The model | You |
| Effort | Low | Higher — you write the handoff |
| Lossiness | Lossy; Claude might drop something load-bearing | Deterministic; only what you typed survives |
| Thoroughness | Can include files/decisions you would have forgotten | Only as thorough as your handoff brief |
| Best for | Related continuation inside the same task | New task, or when you know exactly what's relevant |

**Steering compaction:** pass instructions to `/compact` so the summary focuses on the right axis:
```
/compact focus on the auth refactor, drop the test debugging
```

### What Causes a Bad Compact

Bad compacts happen when **the model can't predict the direction of your next work**. Example:

```
Long debugging session on foo.ts → auto-compact fires → summary
focuses on the foo.ts investigation.
User: "Now fix that other warning we saw in bar.ts."
```

The bar.ts warning was a throwaway observation during debugging. The summariser dropped it because the session was clearly about foo.ts. Claude now has no memory of the warning.

Amplifier: context rot means the model is at peak token load, which is the point of lowest intelligence, when it has to summarise. The lossier the call, the more this matters.

**Mitigation — proactive compact with steering.** Because the 1M window gives you more time before auto-compact fires, compact **deliberately at a known transition point**, with explicit instructions about what comes next:

```
/compact I'm about to switch from the foo.ts fix to the bar.ts warning.
Keep both contexts — don't drop the warning observation from earlier.
```

Never let auto-compact run during a task pivot.

## Subagents as Context Management

Subagents are not only a parallelism tool — they are **the right primitive when the next chunk of work will produce intermediate output you won't need again**.

The mental test:
> Will I need this **tool output** again, or only the **conclusion**?

If only the conclusion, spawn a subagent. It runs in a fresh context, produces its summary, and the parent window only absorbs the final report — not the 30 file reads or 20 tool calls that produced it.

Claude Code auto-dispatches subagents in some cases, but explicit requests produce more predictable behaviour:

```
Spin up a subagent to verify the result of this work against {spec file}.

Spin up a subagent to read {other repo} and summarise how it implements
the auth flow; I'll implement it here in the same style afterwards.

Spin up a subagent to write docs for this feature based on my git changes.
```

**Rule of thumb for coding-agent runtimes:** any sub-task whose output is a *report* (verification result, summary, review) belongs in a subagent. Any sub-task whose output is *integrated code changes* belongs in the parent.

## When to Start a New Session

Rule: **new task = new session.** Carrying context from a DB refactor into a frontend redesign produces confused, conflicting code.

Grey zone: related tasks where *some* prior context helps but not all. Example: writing documentation for a feature you just implemented.
- New session = Claude re-reads the files you just touched (slower, more expensive, but clean).
- Same session = extra context lingers but doc generation is not highly intelligence-sensitive, so the efficiency gain usually wins.

Decision: if the next task is **intelligence-sensitive** (architecture, tricky debugging, security-sensitive code), prefer a fresh session. If it's **formatting, docs, repetitive translation**, keeping context is fine.

## Decision Flow Between Turns

```
After Claude finishes a turn:

 ├─ Is the next work the same task?
 │   ├─ No → /clear (write a handoff first if the task was long)
 │   └─ Yes ↓
 │
 ├─ Did the last attempt fail in an instructive way?
 │   └─ Yes → Esc Esc (rewind to before the failed approach,
 │            re-prompt with what you learned)
 │
 ├─ Is the next chunk going to produce noise you don't need later?
 │   └─ Yes → explicit subagent
 │
 ├─ Is the context approaching rot zone (300–400k) or clearly bloated?
 │   ├─ Yes and I can write a handoff → /clear with handoff
 │   └─ Yes and I can't → /compact with steering instructions
 │
 └─ Otherwise → continue
```

## Design Implications for Coding-Agent Runtimes

- **Expose all five options visibly.** Users default to "continue" unless the alternatives are one keystroke away.
- **Surface token counts at every turn.** Users can't decide between compact and continue without knowing context weight relative to the rot zone.
- **Make rewind atomic.** Rewinding to a specific message must cleanly drop everything after it — partial drops produce worse context than not rewinding.
- **Steerable auto-compact.** When auto-compact must fire, prompt the user for an optional steering instruction ("what are you about to work on next?") — this alone prevents the most common bad-compact cause.
- **Distinguish rewind from clear in UI.** Both drop context but rewind preserves session identity and transcripts; clear starts a new session.
- **Surface subagent results distinctly** from parent tool calls so users can audit which chunk of context came back as a summary vs. verbatim.

## See Also

- Parent SKILL.md §Checkpointing and Rewind — the concrete key bindings and restore modes
- [`session-lifecycle-and-resume.md`](session-lifecycle-and-resume.md) — storage and identity for the sessions this file's decisions operate on
- [`../../ai-context-layer/references/context-hygiene.md`](../../ai-context-layer/references/context-hygiene.md) — the four context failure modes (poisoning, distraction, clash, confusion) and context rot as a system-design concern
- [`../../agents-swarm-orchestration/SKILL.md`](../../agents-swarm-orchestration/SKILL.md) — when subagent dispatch becomes multi-agent orchestration
