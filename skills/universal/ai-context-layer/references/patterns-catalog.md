# Patterns Catalog

## Table of Contents

- [How to use this catalog](#how-to-use-this-catalog)
- [Pattern index](#pattern-index)
- [P14 — Sleep-time memory consolidation](#p14--sleep-time-memory-consolidation)
- [P15 — Procedural memory / skill library](#p15--procedural-memory--skill-library)
- [P16 — Multi-agent shared memory with isolation barriers](#p16--multi-agent-shared-memory-with-isolation-barriers)
- [P1 — Operational-truth-first](#p1--operational-truth-first)
- [P2 — Structured memory classes](#p2--structured-memory-classes)
- [P3 — Self-editing memory blocks](#p3--self-editing-memory-blocks)
- [P4 — Temporal knowledge graph with bi-temporal facts](#p4--temporal-knowledge-graph-with-bi-temporal-facts)
- [P5 — Ontology-grounded poly-store](#p5--ontology-grounded-poly-store)
- [P6 — Episodic + semantic dual-store](#p6--episodic--semantic-dual-store)
- [P7 — LLM Wiki / knowledge compilation](#p7--llm-wiki--knowledge-compilation)
- [P8 — Evidence-bearing hybrid retrieval](#p8--evidence-bearing-hybrid-retrieval)
- [P9 — Composed review surface (Wiki + TKG + Inspection UI)](#p9--composed-review-surface-wiki--tkg--inspection-ui)
- [P10 — Self-hosted / local-first memory](#p10--self-hosted--local-first-memory)
- [P11 — Sub-agent context isolation](#p11--sub-agent-context-isolation)
- [P12 — Pointer-first just-in-time context loading](#p12--pointer-first-just-in-time-context-loading)
- [P13 — Managed memory boundary](#p13--managed-memory-boundary)
- [P17 — Schema-grounded write path](#p17--schema-grounded-write-path)
- [P18 — Agentic Context Engineering (ACE) playbook loop](#p18--agentic-context-engineering-ace-playbook-loop)
- [P19 — Harness Engineering (Agent = Model + Harness)](#p19--harness-engineering-agent--model--harness)
- [P20 — Anchored Iterative Summarization (AIS)](#p20--anchored-iterative-summarization-ais)
- [P21 — Evidence-linked consolidated observation](#p21--evidence-linked-consolidated-observation)
- [P22 — Current state linked to supporting evidence](#p22--current-state-linked-to-supporting-evidence)
- [P23 — Section-level scope](#p23--section-level-scope)
- [P24 — Sensitivity filter before retrieval](#p24--sensitivity-filter-before-retrieval)
- [P25 — Schema-first typed memory](#p25--schema-first-typed-memory)
- [Composition rules of thumb](#composition-rules-of-thumb)

**Purpose.** Named, numbered catalog of the durable patterns for AI context
and knowledge-base design. Every design this skill produces should cite one or more
pattern IDs from this catalog. Pair with `anti-patterns-catalog.md` for the sweep and
`reference-architectures.md` for composed recipes.

## How to use this catalog

1. Describe the problem shape (who asks, what surface, what data, what freshness).
2. Pick the minimum set of patterns that covers the problem shape.
3. For each pick, confirm the non-negotiables can be met in the target stack.
4. Run the anti-pattern sweep (`anti-patterns-catalog.md`).
5. Wire the canonical contracts in `assets/contracts/`.

## Pattern index

| ID | Name | Primary role |
|----|------|--------------|
| P1 | Operational-truth-first | Live entity state |
| P2 | Structured memory classes | Durable, app-orchestrated memory |
| P3 | Self-editing memory blocks | Agent-orchestrated core memory |
| P4 | Temporal knowledge graph | Bi-temporal facts with invalidation |
| P5 | Ontology-grounded poly-store | Typed entities + four-verb lifecycle |
| P6 | Episodic + semantic dual-store | User-scoped atomic facts |
| P7 | LLM Wiki / knowledge compilation | Human-reviewable derived KB |
| P8 | Evidence-bearing hybrid retrieval | Corpus grounding with citations |
| P9 | Composed review surface | Wiki + TKG + inspection UI |
| P10 | Self-hosted / local-first memory | Sovereign, on-disk store |
| P11 | Sub-agent context isolation | Bounded task gets its own window |
| P12 | Pointer-first just-in-time context loading | Resolve heavy context only when the surface needs it |
| P13 | Managed memory boundary | Hosted memory without surrendering app-owned truth |
| P14 | Sleep-time memory consolidation | Background dedup, reconciliation, and re-indexing off the request path |
| P15 | Procedural memory / skill library | Reusable, versioned workflows the agent selects |
| P16 | Multi-agent shared memory with isolation barriers | Provenance and a promotion gate for shared writes |
| P17 | Schema-grounded write path | Validation gate on every memory write to block poisoning, drift, and self-ingestion |
| P18 | ACE playbook loop | Generator, reflector, curator emitting delta updates |
| P19 | Harness engineering | Names the control plane this skill is one column of |
| P20 | Anchored iterative summarization | Compression that keeps the IDs it summarises |
| P21 | Evidence-linked consolidated observation | Derived patterns that cite every supporting instance |
| P22 | Current state linked to supporting evidence | Precise state answers that stay auditable |
| P23 | Section-level scope | `applies_to` per section, so addenda do not leak |
| P24 | Sensitivity filter before retrieval | Clearance bound at launch, enforced in every leg before fusion |
| P25 | Schema-first typed memory | Versioned field descriptions, write diffs, scoped writes, logged queries |

---

## P1 — Operational-truth-first

- **Problem shape**: answers depend on live user, org, billing, entitlement, product, or
  transactional state.
- **Non-negotiables**: source of truth stays in operational stores (SQL, APIs, tools);
  never copied into memory or embeddings as the canonical value.
- **Storage pick**: OLTP database, service APIs, or MCP tool endpoints.
- **Lifecycle verbs**: `recall` reads live; `remember` writes only derived summaries,
  never operational facts; `forget` is out of scope.
- **Composition partners**: every other pattern. P1 is the base of any context layer.
- **Failure modes**: vector index mistaken for source of truth (A2); stale cached
  reads (A2 variant); missing ACL scope on tool calls (A10).
- **Reference**: `references/architecture-patterns.md` §Entity Layer; `sources.json`
  → OpenAI MCP, Vercel Agent Resources.

## P2 — Structured memory classes

- **Problem shape**: durable learned facts or preferences that persist across sessions
  but must stay app-orchestrated and auditable.
- **Non-negotiables**: three classes present — profile (declared), behavioral (observed),
  outcome (measured). Every fact carries the `LearnedMemory` contract fields.
- **Storage pick**: typed table or document store keyed by `entity_id` + `memory_type`. AWS-native option: DynamoDB single-table design with `(entity_id, memory_type)` as the composite key and a TTL attribute for ephemeral sessions; pairs with Postgres for heavier relational joins.
- **Lifecycle verbs**: full coverage — `remember` with confidence + source; `recall`
  by entity+type; `forget` closes `valid_to`; `improve` updates confidence from feedback.
- **Composition partners**: P1 (source of truth), P4 (when facts have time validity),
  P8 (grounding fetched separately).
- **Failure modes**: raw chat logs stored as memory (A1); confidence field missing (A14);
  no forget path (A11).
- **Reference**: `references/entity-and-memory-models.md`;
  `assets/contracts/entity-memory-contract.md`; `sources.json` → Mem0 Memory Types,
  LangChain Long-Term Memory.

## P3 — Self-editing memory blocks

- **Problem shape**: long-running agent, same user across many sessions, memory must
  evolve without external orchestration.
- **Non-negotiables**: bounded core block always in context; archival store paged by
  tool calls; edit-auditing so the model cannot silently overwrite critical facts.
- **Storage pick**: fixed-size core block (profile + persona + facts) + larger archival
  KV or vector store.
- **Lifecycle verbs**: `remember` and `forget` are agent actions; `recall` is paging;
  `improve` is edit history.
- **Composition partners**: P2 (for application-owned durable facts the agent cannot
  overwrite), P4 (when block facts need validity windows).
- **Failure modes**: silent overwrite of critical facts (no edit audit); unbounded
  block growth; leaking cross-user core blocks.
- **Reference**: `references/entity-and-memory-models.md` §Self-Editing Memory;
  `sources.json` → Letta Memory Blocks, Letta Context Hierarchy (now legacy V1 pages;
  current Letta stores memory as a git-versioned file tree, see
  [memory-stack-crosswalk](memory-stack-crosswalk.md)).

<!-- Source: github.com/letta-ai/letta@bb52a8900a79cf1378e6e9cdecf244b673a13a72 (Apache-2.0), extracted 2026-04-15 -->

## P4 — Temporal knowledge graph with bi-temporal facts

- **Problem shape**: relationships change over time, answers depend on *when* a fact
  was true, contradictions must be inspectable not silently dropped.
- **Non-negotiables**: every edge or state row carries both timelines below;
  invalidation is non-destructive; as-of queries are first-class; the
  episode-provenance chain is preserved.
- **Canonical vocabulary** (the one this skill uses everywhere; other files
  link here):

  | Timeline | Columns | Meaning |
  |---|---|---|
  | Valid time (when it was true in the world) | `valid_from`, `valid_to` | Half-open `[valid_from, valid_to)`; `valid_to IS NULL` means current |
  | Transaction time (when the system knew it) | `recorded_at`, `superseded_at` | Append-only; `superseded_at IS NULL` means the row is the system's current belief |

  "True at t": `valid_from <= t AND (valid_to IS NULL OR t < valid_to)`. "As
  known at k": add `recorded_at <= k AND (superseded_at IS NULL OR k <
  superseded_at)`. A contradiction closes `valid_to` on the old fact (world
  change) or sets `superseded_at` (the system was wrong); it never deletes.
  An out-of-order backfill writes history without touching current state.
- **Name mapping** (names in code stay as they are; map them at the adapter):

  | Source | Valid time | Transaction time |
  |---|---|---|
  | This skill | `valid_from` / `valid_to` | `recorded_at` / `superseded_at` |
  | Graphiti / Zep edges | `valid_at` / `invalid_at` | `created_at` / `expired_at` |
  | Multi-repo hub graph ([dev-context-multi-repo](../../dev-context-multi-repo/SKILL.md)) | `valid_at` / `valid_until` | `ingested_at` / `ingested_until` |
  | This skill's reference app (`builds/reference_app/contracts/memory.py` `LearnedMemory`, adapters, migrations) and cookbooks | `valid_from` / `valid_to` | `created_at` / `invalidated_at` (read as `recorded_at` / `superseded_at`) |

  Postgres DDL for this shape (exclusion constraint against overlapping
  current rows, as-of queries): [Bitemporal State Facts](../../ai-vector-brain/references/postgres-pgvector-default.md#bitemporal-state-facts)
  in ai-vector-brain. Link it; do not restate the DDL here.
- **Storage pick**: graph DB (Neo4j, FalkorDB; Kuzu is archived) or hybrid graph+vector; SQLite-backed
  variant for smaller footprints.
- **Lifecycle verbs**: `remember` writes typed edges with episode IDs; `recall` supports
  current and point-in-time queries; `forget` closes validity windows (hard delete
  reserved for GDPR); `improve` resolves contradictions by category.
- **Composition partners**: P2 (structured facts feed into the graph), P5 (when
  ontology is typed in code), P7 (wiki pages cite graph facts), P9 (review surface
  visualizes the graph).
- **Failure modes**: untyped `(subject, predicate, object)` triples (A6); hard delete
  instead of invalidation (A7); query-time contradiction detection (A4).
- **Reference**: `references/graph-and-relationship-layer.md`; `sources.json` →
  Zep Graphiti, MemPalace cross-routed.

<!-- Source: github.com/getzep/graphiti@98d8344d531aa74160f2e33b8db84c5bdc9954ba (Apache-2.0), github.com/MemPalace/mempalace@6614b9b4e71e67da2236493b036b7bf42ba2d55f (MIT), extracted 2026-04-15 -->

## P5 — Ontology-grounded poly-store

- **Problem shape**: heterogeneous data (prose, events, relational rows) must land in a
  single knowledge layer with typed entities and a single API surface.
- **Non-negotiables**: typed ontology as code (Pydantic or schema-first); poly-store
  (graph + vector + relational) under one driver; `remember / recall / forget / improve`
  as the public verbs.
- **Storage pick**: graph (entities + edges) + vector (embeddings on typed nodes) +
  relational (audit, metadata, job state).
- **Lifecycle verbs**: full four-verb coverage by design.
- **Composition partners**: P4 (when bi-temporal facts matter), P7 (wiki view over
  the same ontology), P8 (retrieval against node+chunk hybrid).
- **Failure modes**: ontology drift (schema changes not enforced as code); graph and
  vector diverge because updates are not transactional; poly-store complexity without
  composition payoff.
- **Reference**: `sources.json` → Cognee.

<!-- Source: github.com/topoteretes/cognee@961c3ca4784686390d89d7c45cef63ed2e8da6a1 (Apache-2.0), extracted 2026-04-15 -->

## P6 — Episodic + semantic dual-store

- **Problem shape**: conversational agent needs short atomic facts extracted from
  dialogue, indexed by user/session, with optional graph overlay for relationships.
- **Non-negotiables**: extraction pipeline converts episodes → atomic facts; each fact
  scoped to `user_id / session_id / agent_id`; episodic layer (what happened) kept
  separate from semantic layer (what we learned).
- **Storage pick**: vector store for semantic facts + time-ordered episode log; optional
  graph overlay (e.g., Mem0g).
- **Lifecycle verbs**: `remember` with extraction; `recall` with user scoping;
  `forget` invalidates semantic facts while episode log is retained for audit;
  `improve` promotes reinforced facts.
- **Composition partners**: P1 (for operational facts the agent should not guess at),
  P8 (prose corpus retrieval alongside user memory).
- **Failure modes**: chat log stored as memory without extraction (A1, A16);
  cross-user leakage (A10); no confidence model (A14).
- **Reference**: `sources.json` → Mem0 Memory Types, Mem0 Graph Memory.

## P7 — LLM Wiki / knowledge compilation

- **Problem shape**: product needs a **human-reviewable, accumulating** knowledge
  asset — not a retrieval index. Sources arrive over time, knowledge must be updated,
  linked, challenged, and reused by both people and agents.
- **Non-negotiables**: ingest → extract → reconcile → supersede pipeline; page types
  (entity / concept / synthesis / source summary / index / log); every claim tagged as
  extracted / inferred / ambiguous with `source_episode_id`; contradictions flagged at
  ingest, not at query time; confidence decays with time and strengthens with
  reinforcement.
- **Storage pick**: file-based markdown wiki with a graph overlay (wikilinks or KG);
  may sit on top of P4 or P5 for facts.
- **Lifecycle verbs**: `remember` runs the ingest pipeline; `recall` reads pages or
  graph queries; `forget` supersedes pages and closes validity on facts; `improve`
  incorporates reviewer corrections and reinforcement.
- **Composition partners**: P4 (temporal facts), P2 (structured memory), P9 (review
  surface is mandatory for user-visible wikis).
- **Failure modes**: query-time contradiction detection (A4); raw embeddings without
  extraction (A16, A18); no review surface when the wiki is user-visible (A17); no
  confidence model (A14).
- **Reference**: `references/knowledge-compilation-and-wiki-pattern.md`;
  `sources.json` → Karpathy LLM Wiki post, SamurAIGPT/llm-wiki-agent,
  Ar9av/obsidian-wiki.

## P8 — Evidence-bearing hybrid retrieval

- **Problem shape**: corpus of prose (docs, site crawl, reports, emails) that changes
  independently of the operational DB and must be queried with citations.
- **Non-negotiables**: every result carries `source_id`, chunk/page ID, freshness
  timestamp, ACL scope, confidence or rank; refuse or downgrade when evidence is
  missing; retrieval eval separated from answer eval.
- **Storage pick**: hybrid index (BM25 + dense) with reranker; citation handles
  stable across re-indexing (episode IDs). On AWS, the default embedding pick is
  **Amazon Nova 2 Multimodal Embeddings** (Bedrock) — supersedes Titan v2.
- **Lifecycle verbs**: `recall` with evidence IDs; `remember` is index ingest (use
  P5/P7 if extraction should produce typed facts); `forget` is index eviction on
  source delete; `improve` is relevance feedback.
- **Composition partners**: P1 (live state stays in tools), P2 (learned prefs scope
  retrieval), P7 (when the corpus must become a reviewable wiki, not just an index).
- **Failure modes**: vector DB as system of record (A2); raw embeddings without
  reranker or evidence (A18); prompt stuffing instead of assembly (A5).
- **Reference**: `references/retrieval-and-grounding.md`; cross-link to
  [ai-rag](../../ai-rag/SKILL.md); `sources.json` → Azure AI Search RAG, Vertex
  Grounding, OpenAI Retrieval.

## P9 — Composed review surface (Wiki + TKG + Inspection UI)

- **Problem shape**: the knowledge layer is **user-visible** — operators, reviewers, or
  customers need to explore, inspect, trace, and correct facts. Practitioner
  write-ups ask for this composition by name.
- **Non-negotiables**: P4 + P7 + an inspection/review surface (graph view, page view,
  contradiction queue by category, source trace, confidence view, editorial approval);
  every fact traceable to `source_episode_id`; contradictions categorized
  (attribution / temporal / stale).
- **Storage pick**: poly-store (P5) or file-based wiki (P7) over a temporal KG (P4);
  review surface is a separate frontend that reads the same store.
- **Lifecycle verbs**: full four-verb lifecycle with reviewer-in-the-loop for
  high-risk pages.
- **Composition partners**: P4, P7, P2, plus the Review & Inspection Layer described
  in `inspection-and-review-surfaces.md`.
- **Failure modes**: review surface treated as optional (A17); no per-fact confidence
  exposure (A14); provenance as optional metadata (A13); contradictions surfaced only
  at query time (A4).
- **Reference**: `references/inspection-and-review-surfaces.md`;
  `references/knowledge-compilation-and-wiki-pattern.md`.

## P10 — Self-hosted / local-first memory

- **Problem shape**: data sovereignty, gravity, offline, or tenant isolation blocks
  managed services; still need the memory properties above.
- **Non-negotiables**: zero managed-service dependencies for the core path;
  single-process, on-disk store (SQLite, embedded graph) acceptable; bi-temporal and
  lifecycle verbs still required.
- **Storage pick**: SQLite + local embeddings; optional lightweight graph;
  MemPalace-style zero-dep setup.
- **Lifecycle verbs**: full four-verb coverage; `forget` closes validity windows
  locally.
- **Composition partners**: any of P1–P8; often combined with P2 and P4 for a minimal
  sovereign stack.
- **Failure modes**: vendor shortcuts reintroduced as "just one managed call"; no
  backup/export path; no ACL because "it's local".
- **Reference**: `sources.json` → MemPalace cross-routed.

<!-- Source: github.com/MemPalace/mempalace@6614b9b4e71e67da2236493b036b7bf42ba2d55f (MIT), cross-routed 2026-04-15 -->

## P11 — Sub-agent context isolation

- **Problem shape**: a bounded sub-task (deep search, report synthesis, file
  analysis) would need substantial context — docs, tools, history — that the
  parent agent does not need once the sub-task returns. Running the sub-task in
  the parent's window inflates the parent toward F2 distraction and F4 confusion.
- **Non-negotiables**: explicit handoff contract — the sub-agent receives a
  task statement, acceptance criteria, tool allowlist, output schema, and token
  budget; returns a compact summary plus citations/episode IDs; the parent never
  sees the sub-agent's internal reasoning, intermediate tool results, or
  conversation turns.
- **Storage pick**: no dedicated storage. P11 is a *runtime* pattern. The
  sub-agent may itself use any of P1–P10 inside its window.
- **Lifecycle verbs**: this is an assembly-layer pattern. The runtime verb set
  (`write / select / compress / isolate` — see `context-hygiene.md`) governs it;
  `isolate` is the verb P11 instantiates.
- **Composition partners**: P3 (the parent is often a long-running agent with
  self-editing memory), P7 (sub-agents compile synthesis pages rather than
  polluting the parent with raw sources), P8 (a search sub-agent is a common
  shape), and the FeedbackOutcome contract when sub-agent results feed
  reinforcement.
- **Failure modes**: sub-agent used as a black box with no output schema (the
  returned summary causes F1 poisoning or F3 clash in the parent); over-eager
  splitting when the task fits in the parent window; summary loses provenance
  so the parent cannot re-fetch detail.
- **Reference**: `references/context-hygiene.md` §Sub-agent isolation recipe;
  Anthropic multi-agent research architecture (90.2% over a single-agent
  baseline on Anthropic's internal research eval, at roughly 15× the tokens of
  a chat interaction — the uplift is bought with budget).

## P12 — Pointer-first just-in-time context loading

- **Problem shape**: large files, tool-rich tasks, or multimodal workspaces
  where preloading every document, screenshot, or tool result would blow the
  bundle budget or destabilize tool choice.
- **Non-negotiables**: the request carries stable refs first (`ContextRef`,
  `ArtifactRef`); only the refs the current surface needs are resolved; loaded
  artifacts keep provenance, freshness, and owner scope; formatting drops raw
  payloads in favor of typed projections.
- **Storage pick**: whatever stores the underlying artifact or tool result.
  P12 is a runtime/assembly pattern, not a storage backend.
- **Lifecycle verbs**: adjacent to `select` and `format`. The request carries
  refs, a resolver maps refs to typed projections or `ArtifactRef`s, then the
  loader expands only the chosen artifacts.
- **Composition partners**: P1 (live truth still comes from tools), P8
  (retrieval returns evidence + refs), P11 (sub-agents often receive refs, not
  full payloads), P10 (local-first apps still benefit from pointer-first
  expansion).
- **Failure modes**: eager prefetch disguised as retrieval (A27), artifact
  payload stuffing (A29), stale refs that lost provenance after expansion, and
  per-surface tool allowlists bypassed by a generic "load anything" tool.
- **Reference**: `references/just-in-time-context-loading.md`;
  `references/multimodal-context-assembly.md`; `sources.json` → OpenAI MCP,
  OpenAI Retrieval, Anthropic context engineering.

## P13 — Managed memory boundary

- **Problem shape**: a team wants to use hosted memory or retrieval because it
  accelerates delivery, but still needs product-owned truth, audit semantics,
  tenant scope, and deletion/export controls.
- **Non-negotiables**: hosted memory is never the canonical store for billing,
  entitlement, profile, or org state; scope is explicit before provider calls;
  invalidation and DSAR/delete semantics are documented in the app layer; export
  or rebuild from source systems remains possible.
- **Storage pick**: managed store or hosted retrieval index paired with app-owned
  operational systems and audit records.
- **Lifecycle verbs**: the provider may support `remember` and `recall`; the
  app still owns the authoritative `forget` / invalidate mapping and the policy
  around what may be remembered at all.
- **Composition partners**: P1, P2, P8, P12. P13 is a boundary pattern, not a
  replacement for those layers.
- **Failure modes**: hosted memory treated as profile truth (A28), scope-free
  managed retrieval (A30), undocumented provider delete behavior, and no local
  replay path when vendors or models change.
- **Reference**: `references/managed-memory-boundaries.md`;
  `sources.json` → Google Agent Engine Memory Bank, OpenAI Retrieval,
  LangChain Long-Term Memory.

## P14 — Sleep-time memory consolidation

Background, asynchronous pass over the memory store that runs off the
request's critical path: between sessions, or during one on a step-count or
debounce trigger (Letta dreaming, LangMem `ReflectionExecutor`). Distills, dedupes, resolves contradictions,
converts relative dates to absolute, prunes superseded rows, and re-indexes.
Anthropic ships a between-session consolidation feature ("dreaming") for
Claude Managed Agents (see the managed-memory-boundaries.md Case list; check
the platform docs for current release status before relying on it); same shape implemented as `dream-skill` in the
wider community and discussed in OpenAI / LinkedIn / Supermemory write-ups.

- **Why this is its own pattern.** A `remember`-only loop accumulates rot:
  contradictory entries, ghost references to deleted artifacts, "yesterday"
  baked into stored text. A foreground `improve` cannot fix it without
  burning user-visible latency. P14 names the *background* job that does it.
- **What runs in the consolidation pass.** Deduplication of near-identical
  rows; contradiction resolution by P4 supersession; relative→absolute date
  rewrites (`"yesterday"` → ISO date at write-time of the original); orphan
  cleanup (rows whose `source_episode_id` is gone); stale row demotion via
  confidence decay (A14); re-clustering / re-summarization for P7 pages.
- **What it must not do.** Touch operational truth (P1). Re-ingest the
  model's own outputs as new "preferences" (A26). Run synchronously in the
  request path (A24-style window pollution).
- **Storage pick.** Whatever already holds memory; the pass is a job, not a
  store. Schedule via `pg_cron`, Mongo Triggers, Cloudflare Queues, GitHub
  Actions, or your existing job runner.
- **Lifecycle verbs.** Reads the full memory layer; writes via `improve`,
  `forget`, and *new* `compress`-equivalent rows that supersede merged
  originals.
- **Composition partners.** P2 / P3 / P4 / P7 (the layers that rot without
  consolidation). P11 if the consolidation runs as a sub-agent.
- **Failure modes.** A26 (mode collapse if consolidation re-ingests model
  outputs), A31 (sleep-time pollution — see anti-patterns), A14 violation
  if confidence is rewritten without bounds.
- **Reference.** "Auto Dream" (Anthropic Claude Code pattern); `dream-skill`;
  Supermemory / Mem0 consolidation docs. See
  `references/agent-memory-benchmarks.md` for the LongMemEval
  "knowledge-updates" axis that catches silent consolidation regressions.

## P15 — Procedural memory / skill library

A third memory tier alongside episodic (events) and semantic (facts):
*procedural* memory — reusable workflows, recipes, and tool-binding
templates the agent can select and follow rather than reinvent. Recent
literature (LEGOMem, SkillFoundry, the techrxiv "Agent Skills from the
Perspective of Procedural Memory" survey, Anthropic Skills) treats
skills/playbooks as first-class memory, not as system-prompt configuration.

- **Why this is its own pattern.** A model regenerating "how do we onboard
  a corporate customer" from weights every turn is wasteful and unsafe.
  Encoding the workflow as a discoverable, version-controlled artifact lets
  the model *select* a procedure and *follow* it — verifiable, auditable,
  composable. This is the representational shift skills make explicit.
- **Shape of a skill row.** `(skill_id, version, name, description,
  trigger_signature, tool_bindings, steps, environment_assumptions,
  provenance, tests, owner_scope)`. The description + trigger_signature
  carry into the agent's selection prompt; the steps load just-in-time
  (P12).
- **Multi-agent variant (LEGOMem).** Modular procedural memory keyed by
  *role* (orchestrator vs task agent), distilled from successful
  trajectories, reused across tasks. The skill catalog itself becomes a
  graph: which orchestrator skills compose with which task-agent skills.
- **Storage pick.** Filesystem-as-memory (P10) is the dominant substrate
  — markdown files in a directory with frontmatter — because it composes
  with git, code review, and editorial workflows. A skill registry table
  alongside `learned_memory` works when skills are a product feature.
- **Lifecycle verbs.** `remember` writes a skill version (typically via PR
  review, not silent extraction); `recall` is *selection* by name + trigger;
  `improve` updates from execution traces and post-hoc reflection; `forget`
  retires a skill via supersession.
- **Composition partners.** P2 (declared facts the skill depends on), P7
  (skill catalog as compiled wiki), P10 (filesystem-as-memory), P12
  (just-in-time loading — only names + descriptions enter the window by
  default).
- **Failure modes.** Skill drift (skills referencing tools that no longer
  exist); silent re-extraction of skills from runs without review (A26
  variant); over-fitting a skill to one customer / one tenant.
- **Reference.** LEGOMem (Oct 2025 / May 2026 review), SkillFoundry, the
  techrxiv procedural-memory survey, Anthropic's Skills feature,
  Hierarchical Procedural Memory for LLM Agents (arXiv 2512.18950).

## P16 — Multi-agent shared memory with isolation barriers

A bounded *shared* memory layer for a team of cooperating agents
(orchestrator + task agents, or a swarm). Distinct from P11 (sub-agent
isolation) — P16 is what you reach for when agents *must* coordinate, not
when they must stay apart. Distinct from P2 — P16 carries cross-agent
artifacts (decisions, claims, blackboard entries), not user-scoped facts.

- **Why this is its own pattern.** Multi-agent stacks in production
  surfaced a new failure: one agent writes an unvalidated claim into shared
  memory; downstream agents treat it as ground truth and propagate the
  error. Pure isolation (P11) prevents the error but kills coordination;
  pure global memory propagates it. P16 names the barriers that make
  sharing safe.
- **Boundary rules.** (1) **Provenance per write** — every shared row
  carries `(writer_agent, role, source_episode_id, confidence)`; readers
  see who wrote it. (2) **Validation gate before promotion** — claims start
  in a per-agent scratch namespace; promotion to the shared namespace
  requires a check (schema, contradiction sweep against existing shared
  rows, confidence floor). (3) **Role-keyed namespaces** — orchestrator
  scratch, task-agent scratch, shared decisions, shared facts; agents read
  what they need, write only to what they own. (4) **Memory boundary
  matches the collaboration boundary** — if two agent groups don't truly
  share a task, they don't share memory.
- **Storage pick.** Postgres / pgvector with row-level scope by `namespace`
  + `writer_agent`. LangGraph Store works; Redis / Mongo / Hindsight MCP
  for cross-app continuity. Never a single shared blob with no ACL.
- **Lifecycle verbs.** Standard four, plus `promote` (scratch → shared)
  which is the chokepoint where the validation gate runs.
- **Composition partners.** P2 (per-user facts stay app-scoped, not
  cross-agent), P4 (shared decisions get bi-temporal validity so reversals
  are auditable), P11 (orthogonal — long-horizon sub-tasks still get
  isolated windows), P14 (consolidation runs over each namespace
  independently).
- **Failure modes.** A32 (uncoordinated multi-agent writes — see
  anti-patterns), shared blackboard with no ACL becoming a global garbage
  bin, role drift (an agent writes outside its role).
- **Reference.** Hindsight multi-agent shared memory guide (April 2026);
  Shared Recurrent Memory Transformer (SRMT, OpenReview); LEGOMem
  multi-agent procedural memory; Supermemory / Mem0 multi-agent docs.

## P17 — Schema-grounded write path

A validation gate placed between the agent's extraction step and the memory
persistence write. Every `remember()` call passes through the gate before
anything hits the store. This is the primary architectural defense against
memory poisoning (F1), unbounded drift, and mode-collapse amplification (A26,
A31).

- **Why this is its own pattern.** The four lifecycle verbs (`remember /
  recall / forget / improve`) describe what memory does; P17 describes how
  writes are disciplined. Without a gate, extraction quality becomes the
  only defense — and extraction is not reliable enough. The gate is the
  chokepoint where provenance, type safety, and contradiction checks all
  run before any row lands in the store.
- **Gate checks (in order).** (1) **Schema validation** — required fields
  present and typed: `source_episode_id`, `confidence`, `owner_scope`,
  `valid_from`, `memory_type`. (2) **Range and enum constraints** — confidence
  in [0, 1]; `memory_type` is one of `{profile, behavioral, outcome, claim}`.
  (3) **Contradiction check** — query existing rows for the same `(entity_id,
  memory_key)`; if a conflict exists, invoke the supersession path (P4) rather
  than silently overwriting. (4) **Normalization** — raw model output is
  converted to the typed schema; model inference output is never written as a
  declared `profile` fact without a confidence signal and the correct
  `memory_type`. (5) **Self-ingestion block** — if the source of the write is
  the model's own prior output (not a user turn or a tool result), the write is
  rejected or downgraded to `behavioral` with confidence < 0.5 to prevent A26.
- **Decision node.** Write request → gate → (pass) store → (fail) route to
  contradiction queue (if conflict) or rejection log (if schema fails). Do not
  swallow rejections silently — each rejection is a signal the extraction step
  needs improvement.
- **Storage pick.** Any store that runs the gate. Postgres `BEFORE INSERT`
  trigger, application middleware, or a pre-write validator function in your
  memory adapter. The gate must run before the store, not after.
- **Lifecycle verbs.** Wraps `remember` and `improve`. `recall` and `forget`
  do not pass through the write gate but must still respect `owner_scope`.
- **Composition partners.** P2 (the schema the gate enforces), P4 (the
  supersession path the gate routes conflicts to), P14 (sleep-time
  consolidation still needs its own gate pass for every row it writes).
- **Failure modes.** Silent gate bypass (agent writes directly to the store,
  skipping the gate — enforce at the adapter level, not just the application
  layer); gate too strict (legitimate writes rejected, agent cannot accumulate
  useful memory — tune with observed rejection rates); gate too loose (no
  self-ingestion check, A31 fires during P14 consolidation).
- **Reference.** Anti-patterns A13 (missing provenance), A26 (mode-collapse
  self-ingestion), A31 (sleep-time pollution) — all prevented by P17.
  Validated write-path design also appears in P16's `promote` verb.

## P18 — Agentic Context Engineering (ACE) playbook loop

A self-improving context system that treats the agent's working context as an
**evolving playbook** rather than a fixed prompt. Three components run a tight
loop that mirrors how humans learn — attempt, reflect, consolidate — and emit
**delta updates** (small, additive bullets) instead of rewriting the whole
context. Source: Zhang et al., *Agentic Context Engineering: Evolving Contexts
for Self-Improving Language Models* (arXiv:2510.04618, Oct 2025; Stanford +
SambaNova + UC Berkeley; OSS at github.com/ace-agent/ace). The abstract reports
"+10.6% on agents and +8.6% on finance" over strong baselines, with no
fine-tune; the paper also reports matching the top-ranked production agent on
AppWorld. This is the one place the skill states these figures; other files
point here.

- **Why this is its own pattern.** P14 (sleep-time consolidation) describes a
  *background* job that cleans a memory store. P15 (procedural memory) names
  the skill-library substrate. P18 names the *foreground learning loop* that
  produces the playbook P15 stores — and the discipline (delta updates,
  reflection step) that prevents A35 context collapse. Without P18, P14 is
  unconstrained rewriting and P15 has no source-of-improvement.
- **The three components.**
  1. **Generator** — produces the response or trajectory for a task using the
     current playbook. Outputs the attempt and a structured trace of which
     playbook bullets it used.
  2. **Reflector** — evaluates the trace against the outcome (success, failure,
     partial). Emits structured signals: which bullets helped, which misled,
     which gap caused the failure. This step is the *gradient signal*.
  3. **Curator** — converts reflector signals into a compact **delta update**:
     new bullets, edits to existing bullets, supersession of stale ones. Writes
     to the playbook via the P17 schema-grounded gate.
- **Delta updates, not rewrites.** The load-bearing mechanic. Every curator
  emission is a small, additive patch — like a git diff against the playbook.
  Wholesale rewrites are forbidden because they cause A35 context collapse
  (rare-but-important strategies disappear after N consolidation cycles).
- **Storage pick.** Any P15 substrate (filesystem-as-memory + git is dominant;
  Postgres rows with `superseded_by` works). The playbook must be diff-able and
  reviewable by humans.
- **Lifecycle verbs.** `remember` (delta append) + `improve` (Reflector →
  Curator → gate). `recall` is just playbook lookup. `forget` happens via
  supersession, never silent overwrite.
- **Composition partners.** P15 (procedural-memory substrate the playbook lives
  on), P17 (every delta passes the schema gate), P14 (sleep-time job can run
  the Reflector → Curator pass between sessions for offline distillation).
- **Failure modes.** Curator emits rewrites instead of deltas → A35 context
  collapse. Reflector runs on the model's own output without an external
  outcome signal → A26 mode collapse. Playbook grows unboundedly because the
  curator never supersedes → A1 chat-transcripts-as-memory variant.
- **When NOT to use.** Single-turn classification, deterministic transforms,
  any task where a plain rule already knows the answer (echoes coding-behavior
  rule 5). ACE earns its complexity in multi-step agent loops; do not bolt it
  onto every prompt.
- **Reference.** Paper: arXiv:2510.04618. OSS: ace-agent/ace. Independent
  coverage: VentureBeat (Oct 2025), MarkTechPost (Oct 2025), DEV Community
  walkthrough (2026). Anti-pattern blocked: A35.

## P19 — Harness Engineering (Agent = Model + Harness)

The discipline of designing the **control plane around the model**: tools,
guardrails, verification loops, observability, and context delivery. Coined
by Mitchell Hashimoto as the formula `Agent = Model + Harness`; named the
top next priority by several speakers at a 2026 AI engineering conference.
P19 is not a substitute for the context layer — it is the
*parent discipline* in which `ai-context-layer` is one of five columns.

- **Why this is its own pattern.** The skill historically described context
  delivery in isolation. Practitioners have converged on a five-column
  harness model. Naming the parent makes the boundaries explicit: this skill
  owns column 3 (Context & Memory); `ai-agents` owns columns 1, 2, 4
  (Tools, Verification, Guardrails); `qa-observability` owns column 5.
- **The five columns of a harness.**
  1. **Tool orchestration** — selection, chaining, error recovery (→ `ai-agents`).
  2. **Verification loops** — self-critique, tests, judge models (→ `ai-evals`,
     `ai-agents`).
  3. **Context & memory** — *this skill*: P1–P18 above.
  4. **Guardrails** — sandboxes, budget ceilings, HITL approvals (→ `ai-agents`,
     `software-security-appsec`).
  5. **Observability** — traces, audit logs, regression detection
     (→ `qa-observability`).
- **Why this matters for context-layer design.** Decisions about *what to
  load* (P12 JIT) only make sense once the *harness budget* is fixed. A
  per-surface 8K token cap is a harness decision, not a context-layer one.
  When reviewing a context layer, surface the harness assumptions explicitly.
- **Lifecycle verbs.** Spans all six runtime verbs (write / select / compress
  / isolate / order / format) — but the *budget* each verb operates against
  is a harness parameter.
- **Composition partners.** Every pattern in this skill runs inside a harness.
  Reference architectures RA1–RA13 are context-layer recipes; the harness
  composes them with tools, guardrails, and observability.
- **Failure modes.** Designing the context layer without naming the harness →
  context-layer choices that look fine in isolation but violate budget,
  guardrail, or observability requirements at integration. **A36 Victory
  declaration bias** (agents mark tasks complete without verification) is a
  harness-level failure that the context layer cannot fix alone.
- **Reference.** Hashimoto 2026 formulation; Faros AI 2026 deep dive; Atlan
  2026 guide; LangChain's March 2026 Terminal Bench 2.0 improvement
  attributed to harness optimization without changing the model.

## P20 — Anchored Iterative Summarization (AIS)

The canonical `compress` recipe: summarize a long context by **anchoring the
summary to durable identifiers** — file paths, decision IDs, todo IDs, ticket
numbers — so the summary never silently loses references that downstream
steps depend on. Source: Cognition Labs / Walden Yan ↔ Jason Liu conversation
(2025); Anthropic Claude Cookbook *context engineering: memory, compaction,
tool clearing*. A provider-side compaction API, where offered, is the runtime
primitive; look up its current name and contract.

- **Why this is its own pattern.** P14 says "consolidate"; the six runtime
  verbs say "compress"; both are silent on *how to compress without losing
  references*. AIS names the discipline: every summary carries the IDs of the
  artifacts it summarizes, so a later step can re-resolve any artifact by ID.
- **The anchoring rule.** A summary line that says "agreed to switch the
  retry policy" is unanchored and lossy. A summary line that says
  `[decision:D-2026-05-12 file:src/retry.py todo:T-148] switched retry
  policy from exponential to fixed-30s` is anchored — every downstream step
  can re-resolve the original artifacts.
- **Trigger and budget.** Look up the provider's compaction primitive, its
  default trigger, and whether custom summarization instructions and a
  pause-for-review option exist; use them to enforce anchoring and human
  review. Decide when to compact with `context-hygiene.md` §Context mutation
  economics and verify with §Compaction verification (must-survive probe).
- **Composition partners.** P12 (JIT loading uses the anchors to re-fetch);
  P10 (filesystem-as-memory holds the original artifacts that anchors point
  at); P14 (sleep-time job runs AIS on long episodes); P17 (anchored summary
  rows pass the schema gate; non-anchored rejected).
- **Failure modes.** Summary rewrites without anchors → references decay, P12
  JIT can no longer re-resolve. Aggressive compaction without preserving
  open-thread anchors → A37 eager compaction. Summary text contains relative
  dates ("yesterday", "earlier this week") → temporal drift; P14 must rewrite
  to absolute dates.
- **Reference.** Anthropic *context engineering* cookbook (compaction API
  contract); Jason Liu *Two Experiments We Need to Run on AI Agent
  Compaction* (2025); LangChain Deep Agents summarization fallback. Anti-
  patterns blocked: A37, partially A31.

## P21 — Evidence-linked consolidated observation

The consolidation output of P14 when the result is a pattern across many
episodes ("rollback resolved the incident in 3 cases"). The observation is a
derived row that points at each instance it summarises; it is never a
free-floating rewritten note.

- **Problem shape**: agents reuse lessons across incidents, tickets, or
  sessions, and a reviewer must be able to check, recount, or retract them.
- **Non-negotiables**: the row carries `supporting_ids` (episode or fact IDs,
  one per instance) and optional `counter_ids`; the count shown ("in N cases")
  is computed from live links, never stored as free text; `inferred=true`;
  confidence is bounded by the evidence and consolidation cannot raise it
  (A31); when any supporting row is invalidated or tombstoned, the
  observation is recounted or re-queued (A40).
- **Contrast**: a self-edited note such as "rollback usually works" (the
  P3 / background-rewrite shape) cannot be recounted when one incident is
  reclassified, cannot be audited, and drifts under repeated rewrites (A35).
- **Lifecycle verbs**: written only by the consolidation job through the P17
  gate; `recall` returns the observation with its links so the agent can open
  the instances; `forget` on a supporting row triggers recount.
- **Acceptance checks**: every link resolves; invalidating one supporting
  instance changes the count or status within one consolidation cycle; an
  observation with zero live supports is not served.
- **Composition partners**: P14 (the job), P17 (the gate), P22 (state rows
  can cite observations as secondary evidence, never as authority).
- **Reference**: vendor support differs; see the engine axes table in
  `vendor-landscape.md`.

## P22 — Current state linked to supporting evidence

The default when a workload needs both precision (identity, updates, time,
scope) and coverage (the text behind the answer). Answer state from a typed
record; return the evidence pointers with it.

- **Problem shape**: "who owns X now", "which limit applies to entity Y",
  "what was true at time t" over a changing corpus or event stream, where a
  retrieved paragraph alone is ambiguous and a bare value is unauditable.
- **Record shape**: `entity_id` (stable ID, never a display name),
  `attribute`, `value`, `valid_from` / `valid_to` (valid time), `recorded_at` /
  `superseded_at` (transaction time; vocabulary in P4), `authority` (source class and precedence
  rank), `status`, `derived_by` (`rule | extractor | human`), and
  `evidence[]`.
- **Span-level provenance (each `evidence[]` item)**: `source_id`,
  `source_version` or `content_hash`, `section_anchor` (heading path or
  clause ID), `span_start` / `span_end` (character offsets in the converted
  text; page plus box for PDFs), and `quote_hash` for re-anchoring. On
  re-conversion, re-anchor by quote hash; if the quote is gone, mark the
  evidence `orphaned` and flag the state row for review rather than keeping
  it silently.
- **Precedence**: authority rank first, then effective time, then arrival
  order last. A secondary source (chat topic, summary, stale index row)
  proposes a candidate change; it never overwrites a higher-authority value
  (A38). Events are applied idempotently by effective time (A39).
- **Read path**: state questions hit the record (structured lookup or SQL
  with the P4 "true at t" predicate); coverage questions go to P8 retrieval;
  the answer carries both the value and the spans.
- **Acceptance checks**: every served value has at least one live evidence
  span from a source whose authority is at least the record's; as-of answers
  match a replayed event log; the state-maintenance eval in
  `evals-and-operations.md` passes per category.
- **Composition partners**: P1 (the system of record stays the top
  authority), P4 (bi-temporal storage), P8 (evidence retrieval), P17 (gate).
- **Failure modes**: A2, A13, A38, A39, A40.

## P23 — Section-level scope

- **Problem shape**: one document mixes scopes — a group policy with
  per-entity addenda, a contract with per-region schedules, a runbook with
  per-environment sections.
- **Non-negotiables**: `applies_to` (entity, jurisdiction, product, or
  environment set) is assigned per section and inherited by its chunks; the
  document-level value is only a default for sections without an override;
  addendum, annex, schedule, and appendix headings are detected at
  conversion and must carry an explicit scope or fail ingest; retrieval
  filters on chunk-level `applies_to`; the citation names the section.
- **Acceptance checks**: cross-scope hard negatives in the eval (asking about
  entity A never surfaces entity B's addendum, even when the text matches
  better); a lint that counts sections inheriting a scope from a document
  that contains addendum-type headings.
- **Failure mode**: A43 (addendum leak).
- **Reference**: `policy-and-compliance-docs.md` (`PolicyChunk.owner_scope`
  is where the per-section value lives).

## P24 — Sensitivity filter before retrieval

- **Problem shape**: one corpus holds mixed sensitivity labels (public,
  internal, confidential, restricted) and is served to callers with
  different clearance, inside one tenant.
- **Non-negotiables**: every chunk carries `sensitivity`, inherited from its
  source and overridable per section; an unknown label defaults to the most
  restrictive (fail closed); derived artifacts (summaries, P21 observations,
  graph nodes) inherit the highest label among their evidence; the serving
  process's clearance is bound at launch (deployment config or service
  identity), never a tool argument the caller or model can set; the filter
  runs inside each retrieval leg before ranking and fusion, so result
  counts, snippets, and fused ranks never reveal that an above-clearance
  document exists; output is fenced and scrubbed.
- **Acceptance checks**: canary documents with unique tokens at each label
  never appear, or change counts, at a lower clearance, including through
  graph expansion and derived summaries; a request that tries to pass a
  clearance argument is rejected.
- **Named deviation**: inside one trust boundary with an escalation path, a
  launch flag may expose a single withheld count so the agent can say
  "evidence exists above your clearance". Off by default, never per call,
  and off for multi-tenant or customer-facing callers; the canary check then
  allows that one counter to move. Details in
  [agents-mcp](../../agents-mcp/references/mcp-knowledge-serving.md).
- **Relationship to tenant isolation**: same rule as `owner_scope` at
  candidate generation (`tenant-isolation-patterns.md`); sensitivity is a
  second axis within a tenant. Use both.
- **Failure modes**: post-fusion filtering; clearance supplied per call; a
  summary that drops the label of its evidence (A30 is the managed-service
  form).
- **Reference**: MCP serving of a filtered retrieve tool belongs to
  [agents-mcp](../../agents-mcp/SKILL.md).

## P25 — Schema-first typed memory

The whole write and read path for memory whose questions are exact,
aggregative, or stateful ("how many", "who owns it now", "which limit
applies") over a domain you can enumerate. P17 is the gate inside this path;
P25 is the path around it.

- **Problem shape**: wrong-but-plausible answers are costly and must be
  checkable against stored rows.
- **Write path**:
  1. **Field descriptions are versioned code.** Each field's description
     states vocabulary, extraction policy, and inference limits (canonical ID
     format, "exclude scheduled changes"). Review and regression-test a
     description change like a code change.
  2. **Staged extraction with per-field validation**: detect objects, then
     fields, then values; validate each field and retry only the failing one.
     Escalate only flagged records to a slower extractor.
  3. **Deterministic mutations bypass the model.** Known-structure updates
     (an API event, a status change) write directly; the model extracts only
     from unstructured input.
  4. **Every write returns a diff** (created, updated, deleted, with old and
     new values) and appends it to a change log.
  5. **Scoped writes.** A write declares which records it may touch. Choose
     per write path between reject (the whole write fails) and
     drop-and-report (out-of-scope fields are skipped and listed); never
     silently apply them.
  6. Time is modelled in the schema with P4 columns, not inferred at read.
- **Read path**: fixed query templates for known question types first;
  model-generated queries as a fallback over a read-only role; the generated
  query is always logged and replayable; composite questions run against one
  consistent snapshot; scoped aggregates report any record they could not
  include.
- **Store split**: a tight typed store for lookups and a broad text store
  (episodes, chunks) for "explain X" questions, linked by evidence IDs
  (P22). Do not force one representation to answer both.
- **Schema-gap capture**: log reads the schema could not answer, turn them
  into schema-change proposals, and have a human decide and apply them.
- **When not to use**: open-ended conversational recall, preferences with no
  known ontology, paraphrase-heavy or multilingual free-text search, or
  entities you cannot define in advance (use P6 or P8).
- **Acceptance checks**: update returns the new value and its diff; field
  clearance ("X no longer has a deadline") nulls the field; a never-written
  fact returns "unknown"; two writes missing the key never merge silently;
  a write scoped to A that mentions B leaves B unchanged and reports the
  skip; a scoped aggregate with a missing record flags it; task-owner and
  incident-owner fields are never confused; every read's query is logged.
  Run them on every schema or description change.
- **Composition partners**: P2 (memory classes), P4 (time), P17 (the gate),
  P22 (state linked to evidence).
- **Failure modes**: A6 (untyped triples), A13, A38.

## Composition rules of thumb

- **Every design starts with P1**. Operational truth is the base. If it's missing, no
  other pattern will save the design.
- **P2 + P8 is the minimum for a personalized RAG app** — structured memory for user,
  hybrid retrieval for corpus.
- **P4 + P7 is the minimum for a living wiki** — temporal facts plus human-readable
  compiled pages.
- **P9 is P4 + P7 + the review surface**. It is not a new pattern; it is the
  composition the skill must be able to name when a caller asks for an inspectable
  knowledge base.
- **P3 replaces external memory orchestration, it does not replace P1**. The agent
  can edit its memory blocks; it cannot be trusted as the source of truth for billing
  or entitlement.
- **Never compose without naming the anti-patterns blocked**. Every composed
  architecture must pass the sweep in `anti-patterns-catalog.md`.
- **P11 is orthogonal**. Sub-agent isolation applies to any long-horizon
  composition — RA5 (long-running agent), RA1 (reviewers invoking synthesis
  sub-agents), deep-research workflows. Add P11 whenever a sub-task would
  otherwise double the parent's context.
- **P12 is the runtime default once artifacts get large**. Prefer refs in the
  request and typed projections in the bundle over inlining whole documents,
  screenshots, or tool payloads.
- **P13 is a boundary, not an architecture**. Managed memory can accelerate
  delivery, but it never removes the need for P1 truth, explicit scope, or a
  local audit/deletion story.
- **P22 is the answer to "coverage or precision?"** When a workload needs
  both, link current state to its evidence instead of choosing one; add P23
  and P24 as soon as one corpus serves more than one scope or clearance.
