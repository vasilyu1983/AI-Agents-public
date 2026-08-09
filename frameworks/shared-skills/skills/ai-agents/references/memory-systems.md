# Memory Systems — Agent-Side Quick Reference

## Table of Contents

- [Where the catalogs live](#where-the-catalogs-live)
- [Agent-loop routing](#agent-loop-routing)
- [Required anti-pattern sweep](#required-anti-pattern-sweep)
- [What this file adds does not duplicate](#what-this-file-adds-does-not-duplicate)
- [2025-2026 research notes complement not duplicate](#2025-2026-research-notes-complement-not-duplicate)

*Purpose: tell an agent designer **where to look** for memory architecture and
**which catalog entries** are load-bearing. The full pattern and anti-pattern
catalogs live in `ai-context-layer`; this file does not maintain a parallel
taxonomy.*

If you find yourself wanting to add a new pattern here, add it to
`ai-context-layer/references/patterns-catalog.md` instead and link to it.

## Where the catalogs live

| Concern | Source of truth |
|---------|-----------------|
| Named patterns (P1–P16) | [`../../ai-context-layer/references/patterns-catalog.md`](../../ai-context-layer/references/patterns-catalog.md) |
| Anti-patterns (A1–A34) | [`../../ai-context-layer/references/anti-patterns-catalog.md`](../../ai-context-layer/references/anti-patterns-catalog.md) |
| Reference architectures (RA1–RA13) | [`../../ai-context-layer/references/reference-architectures.md`](../../ai-context-layer/references/reference-architectures.md) |
| Runtime hygiene (F1–F4 failure modes) | [`../../ai-context-layer/references/context-hygiene.md`](../../ai-context-layer/references/context-hygiene.md) |
| External benchmarks (LongMemEval, LoCoMo, MemBench, GraphRAG-Bench, MemTier) | [`../../ai-context-layer/references/agent-memory-benchmarks.md`](../../ai-context-layer/references/agent-memory-benchmarks.md) |

## Agent-loop routing

| Question | Catalog entry |
|----------|---------------|
| Where does live state live? | **P1** Operational truth in tools/APIs/SQL — never in derived memory |
| App-orchestrated facts (preferences, settings) | **P2** Structured memory |
| Self-editing notes (Zettelkasten-style) | **P3** Self-editing memory |
| Time-aware facts that supersede | **P4** Temporal knowledge graph |
| Conversational episodic + semantic split | **P6** Episodic + semantic split |
| Compiled wiki pages for recurring queries | **P7** LLM Wiki |
| Evidence-bearing retrieval | **P8** Evidence-bearing retrieval |
| Just-in-time loading of large refs | **P12** Just-in-time context loading |
| Hosted memory boundaries | **P13** Managed-memory boundaries |
| Background dedup / contradiction resolution | **P14** Sleep-time consolidation |
| Procedural memory / skill library | **P15** Procedural memory |
| Multi-agent shared memory with isolation | **P16** Multi-agent barriers |

## Required anti-pattern sweep

Run before shipping any agent that writes memory:

| ID | What to block |
|----|---------------|
| A1  | Raw chat transcripts as memory |
| A11 | No forget path (DSAR / correction) |
| A13 | Provenance not stored with the fact |
| A14 | No confidence / no abstain |
| A26 | Mode-collapse loop (model output ingested as preference) |
| A31 | Sleep-time pollution from un-gated consolidation |
| A33 | GraphRAG misapplied to single-hop questions |

The full A1–A34 list with detection signals is in the catalog above.

## What this file *adds* (does not duplicate)

The agent loop has a few concerns that belong here, not in ai-context-layer:

- **Trigger placement.** Memory `recall()` runs in the *pre-LLM* assembly
  phase; `remember()` runs *post-response* as a background side-effect, never
  on the user's critical path.
- **Latency budget.** Voice agents get ≤300ms for the full bundle (see RA13);
  text agents get up to ~1s; batch agents are unbounded.
- **Tool-result projection.** Raw tool JSON should be `format`-ed into typed
  projections before it enters the window — this is one of the six runtime
  verbs (write/select/compress/isolate/order/format) and is where the agent
  loop differs most from generic context assembly.

If a memory question has *no* agent-loop angle (storage shape, retention,
provenance, retrieval), use the ai-context-layer catalogs directly and skip
this file.

## 2025–2026 research notes (complement, not duplicate)

The patterns here predate the 2026 catalog and remain useful as **named
research lineages** that map to current P-codes:

### A-MEM (Zettelkasten-inspired, 2025)

Atomic notes with bidirectional links, dynamic indexing, emergent structure.
Maps to **P3 self-editing memory** in the current catalog. Use the original
A-MEM paper as the lineage reference; use P3 for the operational pattern.

### Mem0 (production long-term memory, 2025)

ADD / UPDATE / DELETE / NOOP operations on a per-turn basis, RL-fine-tuned
operation selector. Maps to **P2 structured memory** plus **P14 sleep-time
consolidation** for the dedup loop. See vendor entry in
[`vendor-landscape-2026-04.md`](../../ai-context-layer/references/vendor-landscape-2026-04.md).

### Agentic Context Engineering / ACE (2025)

Context as an evolving playbook (generation → reflection → curation). Avoids
"context collapse" where iterative rewriting erodes detail. Maps to **P15
procedural memory** plus the **A26 mode-collapse** anti-pattern.

### Event-Centric Conversational Memory (2025)

Conversation history as event-like propositions (participants, temporal cue,
proposition, local context) instead of turn-based logs. Maps to **P6 episodic
+ semantic split** — the event projection is the episodic side; extracted
propositions feed the semantic side.

---

**This file is working if:** an agent designer arrives, picks the right
P-code in under a minute, and never has to choose between two competing
taxonomies.
