# Memory Architecture Ceilings

When flat `AGENTS.md` / `CLAUDE.md` / auto-memory stops being enough, and what replaces it.

Last verified: 2026-04-21. Sources inline with dates — treat as moving targets.

## Table of Contents

- [When to read this](#when-to-read-this)
- [The four ceilings](#the-four-ceilings)
- [Compiled-truth + timeline file schema](#compiled-truth--timeline-file-schema)
- [Tiered entity enrichment](#tiered-entity-enrichment)
- [Thin harness, fat skills](#thin-harness-fat-skills)
- [Graph-vector hybrid memory](#graph-vector-hybrid-memory)
- [Fail-improve loops](#fail-improve-loops)
- [Memory taxonomy vocabulary](#memory-taxonomy-vocabulary)
- [Decision rule](#decision-rule)

## When to read this

Read this reference when any of these is true:

- The repo's `AGENTS.md` or auto-memory has grown past ~150 hot lines and pruning is no longer enough.
- The agent needs to answer **multi-hop questions** ("was Alice's project affected by Tuesday's outage?") that cross entities.
- The team accumulates people, companies, projects, or incidents that must stay linked across months.
- Keyword grep across memory returns empty while the fact is clearly on disk (synonym / paraphrase failure).
- You are considering a separate memory service and want to know the shape before shopping.

If none apply, stay on flat `AGENTS.md` + scoped `.claude/rules/*.md`. The ceiling patterns below add cost and infrastructure.

## The four ceilings

Progression of memory substrates and where each breaks. Pattern documented by Akshay Pachaar (2026-04-13, [thread](https://x.com/akshay_pachaar/status/2043745099792953508)).

| Layer | Substrate | Breaks when |
|---|---|---|
| L1 — In-memory | Python list / conversation array | Process restart or context window fills (~200 turns); no persistence, no prioritization. |
| L2 — Flat files | `AGENTS.md`, `CLAUDE.md`, markdown vault | Corpus > ~1,000 facts; keyword search misses synonyms and paraphrases. |
| L3 — Vector | Embeddings + cosine similarity | Multi-hop queries where the **bridge fact** contains neither query term. |
| L4 — Graph-vector hybrid | Graph edges + embeddings on every node | Requires entity extraction, dedup, and edge-weighting infra — weeks of work if built from scratch. |

"Lost in the middle" effect: accuracy drops >30% when relevant info sits mid-context even with 128K+ windows. Throwing more context at L1/L2 does not substitute for structure.

On hosted runtimes (Claude Managed Agents), the L2 "flat files" rung is satisfied by **memory stores mounted at `/mnt/memory/<store-name>/`** rather than local disk. Same substrate, different mount. See [`../../agents-subagents/references/runtime-surfaces.md`](../../agents-subagents/references/runtime-surfaces.md) §"Memory stores" and [`../../ai-context-layer/references/filesystem-as-memory.md`](../../ai-context-layer/references/filesystem-as-memory.md) for the design rationale and the Pokémon longitudinal case showing capable models organize file-based memory better than specialized memory APIs.

## Compiled-truth + timeline file schema

Durable schema for memory entries that accumulate evidence over time without losing the current-best-understanding view. Pattern from GBrain (Garry Tan, 2026-04-10, [repo](https://github.com/garrytan/gbrain)).

```markdown
---
type: concept
title: Do Things That Don't Scale
tags: [startups, growth, pg-essay]
---
Paul Graham's argument that startups should do unscalable things early on.
The key insight: unscalable effort teaches you what users actually want.

---
- 2013-07-01: Published on paulgraham.com
- 2024-11-15: Referenced in batch W25 kickoff talk
- 2026-03-04: Cited in YC investor memo — reframed as "the customer interview substitute"
```

Above the `---` divider: **compiled truth**. The current best understanding. Rewritten when new evidence changes the picture.

Below the divider: **timeline**. Append-only evidence trail. Never edited, only extended.

Use this shape for person/company/project/idea pages. Use it especially when a durable fact will accumulate evidence across months — the compiled-truth section stays stable while the timeline grows.

## Tiered entity enrichment

Policy for when to turn a mentioned entity into a full memory page. Prevents pollution from one-off mentions while ensuring recurring entities become first-class. Pattern from GBrain.

| Tier | Trigger | Content |
|---|---|---|
| 3 — Stub | First mention | Name + source + one-line context |
| 2 — Enriched | ≥3 mentions across different sources | Web + social lookup, canonical attributes |
| 1 — Full | Meeting/interaction OR ≥8 mentions | Full enrichment pipeline, bidirectional links |

The key is that enrichment is **automatic based on mention count**, not manual tagging. Adapt the thresholds to the corpus — a high-noise feed may need higher tier-2 cutoff.

## Thin harness, fat skills

Architectural split that governs what goes in code vs. in model-interpreted markdown. Pattern from GBrain (labelled "Thin Harness, Fat Skills").

| Concern | Goes where | Why |
|---|---|---|
| Deterministic ops (search, embed, import, sync) | Executable code (TS/Python) | Must be reliable, testable, cheap |
| Judgment-dependent ops (consolidation, classification, entity linking) | Markdown skill files | Model reads the skill and executes |
| Operation contract | **One shared interface** covering CLI + MCP (e.g. `src/core/operations.ts`) | No drift between surfaces |

Implication for project memory: if a procedure can be expressed as a deterministic script, extract it to a hook or CI step rather than leaving it as model-interpreted prose in `AGENTS.md`. If it requires judgment, keep it as a skill with a clear trigger — not as always-loaded memory. This mirrors your existing `agents-memory` guidance ("memory ≠ skill").

**Reliability caveat**: model-interpreted features scale with model quality. GBrain documents Claude Opus 4.6 and GPT-5.4 "Thinking" as working configurations; weaker models produce unpredictable results on instruction-dependent features. Do not promote a procedure to a skill if the reliability matters and the target model is below that bar — keep it as a hook.

## Graph-vector hybrid memory

When flat files + vector search stop being enough, the next step is a three-store architecture. Pattern formalized by Cognee (open-source, 2026-04-13, [GitHub](https://github.com/topoteretes/cognee)).

| Store | Captures | Default backend | Production backend |
|---|---|---|---|
| Relational | Provenance: where data came from, when, who has access | SQLite | Postgres |
| Vector | Semantics: what content means, similarity | LanceDB | Qdrant / pgvector / Pinecone |
| Graph | Relationships: how entities connect, causality, hierarchy | Kuzu (embedded) | Neo4j / FalkorDB / Neptune |

The load-bearing trick: **every graph node has a corresponding embedding**. Enter through vectors (semantic match) and exit through the graph (follow relationships), or the reverse. This is what makes multi-hop queries work without losing semantic recall.

Four-call API shape (framework-agnostic worth copying even without Cognee):

```python
add(document)       # Ingest anything
cognify()           # Build graph + embeddings (classification, chunk, extract, dedup, index)
memify()            # Self-improve: strengthen useful paths, prune stale nodes, tune edge weights
search(query)       # Retrieve with intent-aware reasoning
```

Alternatives in the same space: **Mem0**, **Zep**, **Letta**, **Graphiti**. Evaluate against your query shape (does it cross entities?) and your ingest rate.

## Fail-improve loops

Self-improving memory layer that promotes model-interpreted paths to deterministic ones over time. Pattern from GBrain (`fail-improve.ts`).

```text
LLM fallback fires → log fallback (input, output, timing)
                  → periodically mine logs for regex / rule candidates
                  → promote stable patterns to deterministic handlers
                  → track trajectory (e.g. "intent classifier: 87% deterministic, up from 40% in week 1")
```

The point: the memory system gets cheaper and more reliable the longer it runs, because the things the model used to do get replaced by code. Add a `doctor` command (or equivalent) that surfaces the trajectory so you can see the promotion is actually happening.

## Memory taxonomy vocabulary

Use these terms when describing memory design so the scope of each layer is unambiguous. Taxonomy from Lilian Weng (2023) via cognitive-science mapping.

| Term | What it holds | Memory home |
|---|---|---|
| Sensory | Raw perceptual input, milliseconds | Tool call results before the model reads them |
| Working | Active thinking, ~7±2 items | Current context window |
| Long-term — Episodic | Specific past events ("on Tuesday, the cluster went down") | Per-session logs, timeline sections |
| Long-term — Semantic | Facts and concepts ("PostgreSQL is a relational DB") | Compiled-truth sections, knowledge base |
| Long-term — Procedural | Skills and workflows ("when refund request, first check date") | Skill files, hooks, runbooks |

**Consolidation** is the bridge: repeated episodic events distilling into semantic rules. An agent that notices "users consistently prefer executive summaries" across dozens of interactions should turn that into a reusable rule rather than replaying each event. Consolidation is usually model-interpreted today — treat it as a manual review pass or a scheduled `memify`-style job, not a silent background promotion.

## Decision rule

Use this to decide whether a project needs to climb the ladder:

1. **L1 in-memory** — prototypes only.
2. **L2 flat files** — default for all repos. Stay here unless a specific query failure forces you up.
3. **L3 vector** — add when keyword search in L2 starts missing the fact you know is on disk.
4. **L4 graph-vector** — add when a real user query needs two or more entities connected through a bridge fact.

Do not preemptively climb. Every rung adds infra, cost, and a frontier-model reliance (GBrain's documented requirement: Opus 4.6 or GPT-5.4 Thinking; weaker models degrade). The exception-file test from [../SKILL.md](../SKILL.md) §Exception-File Test still applies — if most of your memory is inferable from the repo, no store architecture fixes that.

## Attribution

- Cognee architecture and four-call API: Akshay Pachaar, "Build Agents that never forget" (2026-04-13).
- GBrain patterns (compiled-truth + timeline, tiered enrichment, thin-harness/fat-skills, fail-improve): AlphaSignal AI summary of Garry Tan's GBrain (2026-04-15).
- Lilian Weng memory taxonomy: widely cited 2023 formulation, re-popularized in the Pachaar thread.
- OpenAI Agents SDK "control when memories are created and where they're stored": @OpenAIDevs (2026-04-15). Reinforces the existing opt-in `memory:` field guidance in [`../../agents-subagents/references/agent-tools.md`](../../agents-subagents/references/agent-tools.md).
