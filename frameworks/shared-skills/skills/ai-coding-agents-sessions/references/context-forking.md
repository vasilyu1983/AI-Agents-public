# Context Forking In Subagent Sessions

Subagents in coding-agent runtimes have two distinct context-startup modes. Each implies different session-lifecycle, cost, and isolation behavior. This file owns the **session-layer** view; the **subagent-design** view lives in `agents-subagents` §"Forking Parent Context Into Subagents".

Source: officially documented at [`code.claude.com/docs/en/sub-agents`](https://code.claude.com/docs/en/sub-agents) §"Fork the current conversation" (re-verified 2026-07-11). This was community-reported before it shipped in official docs; it is no longer an unverified surface, but it is still a fast-moving one — the docs themselves flag Claude-initiated forking as an experimental, staged rollout that may change.

## Two startup modes

| Mode | Startup context | Cache behavior | Tool-call visibility |
|---|---|---|---|
| Blank (named subagent) | Fresh, isolated context; own system prompt, own tool access, no parent history, skills, or already-read files | No shared prefix with parent; every spawn pays full input-token cost on its first request | Tool calls stay in subagent; only final summary returns to parent |
| Fork | Inherits the entire parent conversation so far — same system prompt, tools, model, and message history | First request reuses the parent's prompt-cache prefix, making it cheaper than a fresh spawn needing the same context; effective price on cache-hit tokens is roughly cache-read rate (~10% of normal input price on Sonnet tiers) | Tool calls stay isolated; only the fork's final result returns to the main conversation |

Both modes return only the final result to the parent/main session — that part is identical. The difference is what the subagent starts with, and a fork drops the input-isolation property subagents otherwise provide.

## Version gate and activation surfaces

- **Minimum version:** forked subagents require Claude Code **v2.1.117 or later** — the fork path existed in source before that but was compiled out of public releases.
- **`/fork <directive>`** — starts a fork directly, named from the first words of the directive. As of **v2.1.161, `/fork` is enabled by default**; on earlier versions it requires the env var below set to `1`.
- **`CLAUDE_CODE_FORK_SUBAGENT`** — set to `1` to force-enable fork mode (including letting Claude itself decide to spawn a fork instead of a fresh subagent when no `subagent_type` is specified), or `0` to force-disable it everywhere, including any server-side default rollout. Honored in interactive mode, the SDK, and `claude -p`.
- Once fork mode is enabled, **every** subagent spawn — fork or named — runs in the background by default (a panel below the prompt shows running forks/subagents; `Enter` opens a transcript, `x` dismisses or stops one). Set `CLAUDE_CODE_DISABLE_BACKGROUND_TASKS=1` to force spawns back to synchronous.
- A fork can optionally be given `isolation: "worktree"` so its file edits land in a separate git worktree instead of the main checkout.

## Session-lifecycle implications

- **Resume after fork** — a forked subagent's transcript is logically a sidechain of the parent. Resume should treat the parent transcript as primary; the fork's transcript is a sidechain artifact, not a separate session, unless the runtime explicitly promotes it.
- **Cache invalidation** — the fork shares prompt-cache prefix with the parent. If the parent's earlier turns are evicted from cache, the fork loses its discount and pays full input-token cost. Plan budget assuming eviction is possible during long sessions.
- **Isolation guarantee** — forked tool calls do not pollute the parent transcript. The parent sees only the summary returned at fork completion. Persist enough sidechain telemetry that a fork failure can be debugged without rerunning.
- **Cross-worktree** — if the parent moves worktrees mid-fork, the fork keeps operating against the snapshot it received (or its own `isolation: "worktree"` copy). Treat moved-worktree resume as a special case for forks, separate from same-repo worktree adoption.
- **No nested forks** — a fork cannot spawn another fork, though it can spawn other (non-fork) subagent types, which count toward any depth limit. Design resume/audit tooling assuming fork depth is always exactly one level from a real (non-fork) session.
- **Not the same as session branching.** `/fork` inherits context into a *subagent* that reports back into the same session; `/branch` (or `--fork-session`) mints a whole new *independent session* the user switches into. Do not conflate the two in documentation or UI — see the parent SKILL.md §"Rewind vs Git vs Session Branching".

## When to fork vs stay blank

Fork only when you can answer **both** questions:

1. What understanding has the parent built that the subagent needs?
2. Why is recomputing it more expensive than inheriting parent context (with its cache penalty risk and noise)?

If you can name a specific build-up the subagent would otherwise re-derive (read the same 30 files, rerun the same grep sweep, re-establish the same architectural mental model), forking earns its keep. If not, stay blank — fresh context still wins for reviewers, verifiers, and bounded scoped research, where parent transcripts contain noise the worker should not see.

Per `agents-subagents` §"Current Runtime Model", **fresh context per worker is the default**. Forking is the documented exception.

## Anti-patterns

- **Forking by default for every subagent.** Inherits parent's noise (failed tool calls, dead-end exploration) and re-introduces context rot the subagent boundary was meant to prevent.
- **Forking review and verification roles.** A reviewer who inherits the implementer's reasoning is no longer an independent check; the value of review collapses.
- **Forking a coordinator-role subagent.** A forked coordinator inherits the parent's "delegate work" system prompt and starts orchestrating instead of executing — the two modes cannot share a session's role definition cleanly.
- **Treating fork as free.** The cache-discount only applies once the parent prefix is cache-warm; the first fork of a session still pays full cost, and any cache eviction wipes the discount for later forks too.
- **Forking when the parent has touched secrets.** The fork inherits the parent transcript, including any accidentally surfaced secrets, tokens, or PII. Audit before enabling for sensitive sessions.
- **Assuming `/fork` and `/branch` are interchangeable.** They solve different problems (in-session delegation vs. new independent session) and confusing them in a runbook or UI copy causes users to lose track of which session is "real."

## Cross-references

- `agents-subagents` §"Forking Parent Context Into Subagents" — design-side rules and decision matrix.
- [`../../ai-coding-agents-command-runtime/references/command-dispatch-forking-and-remote-safety.md`](../../ai-coding-agents-command-runtime/references/command-dispatch-forking-and-remote-safety.md) — fork model for prompt commands.
- [`context-lifecycle-and-branching.md`](context-lifecycle-and-branching.md) — per-turn branching (continue / rewind / clear / compact / subagent) at the parent thread level.
- [`session-lifecycle-and-resume.md`](session-lifecycle-and-resume.md) — session identity and resume semantics that govern parent-and-fork session pairs.
- Parent SKILL.md §"Rewind vs Git vs Session Branching" — how `/fork` (subagent-level) differs from `/branch`/`--fork-session` (session-level).
