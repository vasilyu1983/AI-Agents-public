# Claude Managed Agents — Memory Stores

Operational notes on the filesystem-backed memory system shipped with Claude Managed Agents on the Claude Platform. Files persist across sessions; the agent organizes them itself with standard file tools. Launched public beta 2026-04-23.

Sources: @RLanceMartin, 2026-04-24 — <https://x.com/RLanceMartin/status/2047720067107033525>; Anthropic blog — <https://claude.com/blog/claude-managed-agents-memory> (2026-04-23); API docs — <https://platform.claude.com/docs/en/managed-agents/memory>

Cross-links: [`memory-architecture-ceilings.md`](memory-architecture-ceilings.md), [`platform-and-scale.md`](platform-and-scale.md).

## Table of Contents

- [Why Filesystem, Not a Specialized Tool](#why-filesystem-not-a-specialized-tool)
- [Memory Store Mount Point](#memory-store-mount-point)
- [Multi-Agent Sync](#multi-agent-sync)
- [Export API](#export-api)
- [Session Log vs Memory Store](#session-log-vs-memory-store)
- [Empirical Behavior Across Models](#empirical-behavior-across-models)

## Why Filesystem, Not a Specialized Tool

Earlier work (CoALA, MemGPT) modeled memory after cognitive science / OS abstractions. The Claude Plays Pokémon experiment showed a simpler result: with general file tools, **later models learn to organize memory better than specialized memory tools**. Letta independently confirmed filesystem memory can outperform specialized memory APIs.

Implication: give Claude general tools (read/write files), let it manage organization. Don't pre-impose a schema.

## Memory Store Mount Point

When you attach a memory store to a session, it mounts inside the agent container at:

```text
/mnt/memory/<store-name>/
```

A short note about the mount is **automatically injected into the system prompt** so Claude knows the directory is there. Memory stores are workspace-scoped collections of text documents that **outlive any single session**.

## Multi-Agent Sync

- Multiple agents can have the same memory store mounted simultaneously.
- The platform syncs memories in real time — an edit by one agent is reflected in the filesystem of all agents that have the store mounted.
- The platform handles **concurrency**: multiple agents can work concurrently against the same store without overwriting each other.
- Mount access can be scoped: `read_only` mounts reject writes; `read_write` mounts produce memory versions attributed to the session.

This is the operational model for shared team-wide memory across a fleet of agents.

## Version History and Audit

All changes are tracked: every write to a memory store creates an immutable memory version with attribution (which agent, which session). You can roll back to an earlier version or redact content from history. Updates also appear as session events in the Claude Console.

## Export API

Memories are interpretable and shareable — files, not opaque blobs. Export via the SDK:

```python
client.beta.memory_stores.memories.list(store_id, view="full")
```

Useful for: auditing what an agent has learned, sharing memory state across teams, debugging a regression by replaying a known memory snapshot. Updates also surface as session events in the Claude Console for traceability.

## Session Log vs Memory Store

Two distinct surfaces for context in Managed Agents:

| Surface | Lifetime | Purpose |
|---|---|---|
| Session log | per session, lives outside the context window | record of work; can be fetched and transformed during a task |
| Memory store | persistent across sessions | what Claude chooses to remember long-term |

Claude can fetch and transform session context over the course of a task; it can write files to the memory store when something needs to survive the session.

## Empirical Behavior Across Models

From Claude Plays Pokémon, same step count (≈14K steps):

- **Sonnet 3.5**: treated memory as a transcript — wrote down NPC dialog rather than what mattered. 31 memory files, stuck in second town.
- **Opus 4.6**: 10 files organized into directories, three gym badges earned, plus a `learnings.md` distilled from its own failures (e.g., move-set warnings, tile-maze chaining notes, confirmed-solid wall coordinates).

The skill (knowing *what* to write and *how* to organize) scales with model capability when the tool stays general. Operational takeaway: prefer general file tools and let the model show its memory discipline; revisit if it doesn't.
