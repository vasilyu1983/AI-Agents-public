# Filesystem-as-Memory Pattern

The thesis: **give a capable model general file tools and minimal scaffolding, and it will organize its own memory better than a specialized memory tool will**. Specialized memory APIs (CoALA-style structured stores, memGPT-style tiered context) buy you predictability and lookup latency, but they also constrain how the model can compress and retrieve. With strong models, the constraint costs more than it earns.

Source: Lance Martin (Anthropic), 2026-04-24 ([thread](https://x.com/RLanceMartin/status/2047720067107033525)), referencing David Hershey's "Claude Plays Pokémon" longitudinal experiment and an independent Letta finding that filesystem-backed memory outperformed specialized memory tools on their evals.

## The Pokémon longitudinal case

Same harness, different models, same task (navigate the game and persist learnings to a folder). The artifact quality diverged sharply.

| Model | At ~14k steps | What memory looked like |
|---|---|---|
| Sonnet 3.5 | 31 memory files, stuck in town 2, no progress | Treated memory as a transcript: wrote down what NPCs said rather than what mattered. Example file logged Caterpie/Weedle trivia as "crucial information." |
| Opus 4.6 | 10 files in directories, 3 gym badges, distilled `learnings.md` | Used the filesystem as an organizational substrate. Wrote terse, action-oriented entries: combat heuristics, item-bag limits, dungeon wall coordinates verified at specific step counts. |

The difference is not that Opus was given a better memory tool. The tool was identical. Opus was better at deciding **what to save and how to organize it** — capabilities that scale with the underlying model rather than with the memory schema.

## Pattern: general tools beat specialized memory APIs (when the model is strong)

Operational rules:

- **Provide read/write/list file tools**, a mount point, and a one-line note in the system prompt that the directory exists. Do not prescribe a schema, file naming convention, or retrieval method up front. Let the agent develop its own organization.
- **Persist files between sessions** through a workspace-scoped store — the Anthropic memory tool (`memory_20250818`) uses a client-controlled `/memories` directory by convention — rather than a specialized memory database. The mount path is application-defined; `/mnt/memory/<store-name>/` is a community convention seen in some earlier Claude Code harnesses, not the official Anthropic API shape.
- **Make memory contents human-readable and exportable**. Plain text directories can be downloaded, diffed, and audited. Specialized memory APIs hide this layer.
- **Allow multi-agent attach** with platform-level concurrency handling — multiple agents collaborating on the same memory directory should not silently overwrite each other.

## Anti-pattern: transcript-style memory

The Sonnet 3.5 failure mode is the most common memory anti-pattern in production agents:

- Writes everything notable into memory regardless of whether it changes future behavior.
- Files accumulate without distillation — 31 files of trivia, no `learnings.md` distilled from failures.
- Treats memory as session log rather than as a teaching corpus for the next session.

Detection: file count grows linearly with session count, but task progress does not. If a memory directory has hundreds of small files and the agent is not measurably better at the task, it is logging, not learning.

Mitigation prompts that have been observed to help weaker models:

- "Before writing a memory file, ask whether reading this file in a future session would change what you do next. If not, do not write it."
- "Maintain one `learnings.md` distilled from your own failures. Update it when a failure pattern repeats. Do not let it grow past N entries — compress older entries."

## When specialized memory still wins

This pattern is not universal. Reach for a specialized memory tool (vector store, graph store, structured episodic/semantic/procedural separation) when:

- **The model is small or weak.** Smaller models do not develop file organization on their own. Give them a constrained API.
- **Lookup latency dominates.** Filesystem listing is O(n) over file count. If the agent needs sub-100ms recall over thousands of memories, vector similarity wins.
- **Auditability requires structured fields.** Compliance, retention windows, and DSAR/delete operations are easier against typed records than free-form markdown.
- **Multi-tenant scope enforcement is needed.** Tenant isolation, ACLs, and per-user retention are harder to express through a filesystem mount than through a query layer that attaches scope before retrieval.
- **Cross-entity reasoning matters.** When the bridge fact connecting two queries is not in either query's text, vector or graph retrieval finds it; filesystem listing does not.

Per [`managed-memory-boundaries.md`](managed-memory-boundaries.md), even when filesystem-as-memory is the right choice, **operational truth still does not live in the memory directory** — entitlements, billing, account state, and audit logs stay in app-owned systems regardless of how the agent's memory is stored.

## Compose, do not pick

The strongest production designs combine both:

- Filesystem-as-memory for **agent-authored learnings** (what the agent figured out about itself, the user, or the task).
- Specialized retrieval for **app-authored knowledge** (corpus docs, knowledge base, structured user state).

The two layers do not compete. They answer different questions: "what have I learned?" vs. "what does the system know?" Use the file mount for the first, retrieval for the second.

## Cross-references

- [`managed-memory-boundaries.md`](managed-memory-boundaries.md) — what hosted memory must NOT own.
- [`patterns-catalog.md`](patterns-catalog.md) — P1–P25 named patterns including memory architectures.
- [`entity-and-memory-models.md`](entity-and-memory-models.md) — episodic / semantic / procedural taxonomy.
- [`../../agents-memory/references/memory-architecture-ceilings.md`](../../agents-memory/references/memory-architecture-ceilings.md) — when flat files break and the next rung is needed.
- [`../../agents-subagents/references/runtime-surfaces.md`](../../agents-subagents/references/runtime-surfaces.md) §"Memory stores" — Claude Managed Agents implementation of this pattern.

## Source notes

- Lance Martin thread, 2026-04-24, links David Hershey's Pokémon experiment, the CoALA paper (Ted Sumers), and memGPT (Sarah Wooders, Charles Packer).
- Letta independently found that filesystem-backed memory outperformed specialized memory tools on their evaluations; cited inside the same thread without a separate paper link.
- Anthropic memory tool: a client-side tool type that gives agents read/write/list/delete access to a memory directory whose mount path is application-defined. Look up the current tool type and semantics at `platform.claude.com/docs/en/agents-and-tools/tool-use/memory-tool` before wiring it.
