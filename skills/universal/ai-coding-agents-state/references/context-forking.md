# Context Forking In Subagent Sessions

Subagents in coding-agent runtimes have two distinct context-startup modes. Each implies different session-lifecycle, cost, and isolation behavior. This file owns the **session-layer** view; the **subagent-design** view lives in [`../../agents-subagents/SKILL.md`](../../agents-subagents/SKILL.md) §"Forking Parent Context Into Subagents".

Source: officially documented at [`code.claude.com/docs/en/sub-agents`](https://code.claude.com/docs/en/sub-agents) §"Fork the current conversation" . Fork behaviour is staged and fast-moving; check the sub-agents docs for the build in use before relying on any command, variable or default below.

## Two startup modes

| Mode | Startup context | Cache behavior | Tool-call visibility |
|---|---|---|---|
| Blank (named subagent) | Fresh conversation history; startup instructions, memory, preloaded skills, tools, and permissions follow the named-agent and runtime rules | Separate prompt-cache lineage from the parent; calculate cost from returned usage rather than assuming every input token is uncached | Tool calls stay in subagent; only final result returns to parent |
| Fork (Claude Code) | Inherits the documented parent conversation, system prompt, tools, and model at spawn time | Shares the parent's prompt-cache prefix on its first request; the billed cache-read rate is model-specific and total task cost still depends on writes, misses, output, tools, and retries | Tool calls stay isolated; only the fork's final result returns to the main conversation |

Both modes return only the final result to the parent/main session — that part is identical. The difference is what the subagent starts with, and a fork drops the input-isolation property subagents otherwise provide.

## Activation surfaces

- **Commands and variables are version-gated and have been renamed.** The slash command that starts a forked subagent, and whether `/fork` means a forked subagent or a separate session, has changed across releases and depends on whether agent view is on. An environment variable can disable fork mode everywhere; check its current values in the docs rather than copying them.
- **Fork is requested explicitly.** The model must ask for the fork subagent type; omitting a type selects the default named agent.
- **Assume spawns may default to background.** Background-versus-foreground defaults for subagent spawns have changed across releases; design the session layer so background surfaces are first-class, and check the docs for the current default and the opt-out.
- A fork can optionally be given `isolation: "worktree"` so its file edits land in a separate git worktree instead of the main checkout.

## Session-lifecycle implications

- **Resume after fork** — a forked subagent's transcript is logically a sidechain of the parent. Resume should treat the parent transcript as primary; the fork's transcript is a sidechain artifact, not a separate session, unless the runtime explicitly promotes it.
- **Cache accounting** — Claude Code documents a shared prompt-cache prefix for the fork's first request. Do not turn that into a guaranteed task-level saving: inspect cache-read, cache-write, uncached input, output, tool, and retry usage, and apply the selected model's current rates.
- **Isolation guarantee** — forked tool calls do not pollute the parent transcript. The parent sees only the summary returned at fork completion. Persist enough sidechain telemetry that a fork failure can be debugged without rerunning.
- **Cross-worktree** — if the parent moves worktrees mid-fork, the fork keeps operating against the snapshot it received (or its own `isolation: "worktree"` copy). Treat moved-worktree resume as a special case for forks, separate from same-repo worktree adoption.
- **Nested behavior is version-specific** — current fork documentation forbids a fork from spawning another fork. Whether a subagent can spawn named subagents has changed across releases, so check whether the `Agent` tool is actually present and enforce the runtime's advertised depth rather than copying a universal number.
- **Not the same as session branching.** `/subtask` inherits context into a *subagent* that reports back into the same session; `/branch` (or `--fork-session`) mints a whole new *independent session* the user switches into. On current agent-view releases, `/fork` is another session-branching surface rather than the normal forked-subagent command. Do not conflate these paths in documentation or UI — see the parent SKILL.md §"Rewind vs Git vs Session Branching".

## When to fork vs stay blank

Fork only when you can answer **both** questions:

1. What understanding has the parent built that the subagent needs?
2. Why is recomputing it more expensive than inheriting parent context (with its cache penalty risk and noise)?

If you can name a specific build-up the subagent would otherwise re-derive (read the same 30 files, rerun the same grep sweep, re-establish the same architectural mental model), forking earns its keep. If not, stay blank — fresh context still wins for reviewers, verifiers, and bounded scoped research, where parent transcripts contain noise the worker should not see.

Per [`../../agents-subagents/SKILL.md`](../../agents-subagents/SKILL.md) §"Current Runtime Model", **fresh context per worker is the default**. Forking is the documented exception.

## Anti-patterns

- **Forking by default for every subagent.** Inherits parent's noise (failed tool calls, dead-end exploration) and re-introduces context rot the subagent boundary was meant to prevent.
- **Forking review and verification roles.** A reviewer who inherits the implementer's reasoning is no longer an independent check; the value of review collapses.
- **Forking a coordinator-role subagent.** A forked coordinator inherits the parent's "delegate work" system prompt and starts orchestrating instead of executing — the two modes cannot share a session's role definition cleanly.
- **Treating fork as free or always cheaper.** Shared-prefix cache reads can reduce input cost, but inherited noise, output, tool use, cache writes or misses, and retries can erase the saving. Compare returned usage for the actual task shape.
- **Forking when the parent has touched secrets.** The fork inherits the parent transcript, including any accidentally surfaced secrets, tokens, or PII. Audit before enabling for sensitive sessions.
- **Assuming `/subtask`, `/fork`, and `/branch` are stable synonyms.** Current `/subtask` creates the forked subagent; current `/fork` behavior depends on agent-view state, and `/branch` creates a new independent session. Version-gate runbooks and verify the active UI mode.

## Cross-references

- [`../../agents-subagents/SKILL.md`](../../agents-subagents/SKILL.md) §"Forking Parent Context Into Subagents" — design-side rules and decision matrix.
- [`../../ai-coding-agents-runtime-core/references/command-dispatch-forking-and-remote-safety.md`](../../ai-coding-agents-runtime-core/references/command-dispatch-forking-and-remote-safety.md) — fork model for prompt commands.
- [`context-lifecycle-and-branching.md`](context-lifecycle-and-branching.md) — per-turn branching (continue / rewind / clear / compact / subagent) at the parent thread level.
- [`session-lifecycle-and-resume.md`](session-lifecycle-and-resume.md) — session identity and resume semantics that govern parent-and-fork session pairs.
- Parent SKILL.md §"Rewind vs Git vs Session Branching" — how `/subtask` (forked subagent) differs from `/branch`/`--fork-session` (session-level), including the current agent-view-dependent meaning of `/fork`.
