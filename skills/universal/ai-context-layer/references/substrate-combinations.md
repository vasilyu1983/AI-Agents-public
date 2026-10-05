# Substrate Combinations: RAG, Files, Memory, Graph — When to Combine and Why

Cross-skill reference. The user-facing question is almost always *"RAG or
files? memory or vector? do we need a graph?"* — and the answer
is almost always **"both, with a clear seam between them."** This doc names
the combinations that produce real value, the combinations that look
clever but cost more than they return, and the gates each seam needs.

This doc is the operational complement to:

- `architectures-by-organization.md` (org tier × substrate matrix)
- `reference-architectures.md` (RA1–RA13 named recipes)
- `retrieve-vs-preload-vs-finetune.md` (RAG vs CAG vs fine-tune decision)
- [storage-paradigm-selection](../../software-database-design/references/storage-paradigm-selection.md)
  (canonical Relational vs Graph vs Vector)
- `../../ai-rag/SKILL.md` (retrieval theory and eval depth)
- `../../ai-vector-brain/SKILL.md` (paste-ready pgvector implementation)
- `../../agents-memory/SKILL.md` (file-based AGENTS.md / CLAUDE.md memory)

## Table of contents

1. [The five substrate primitives, restated](#the-five-substrate-primitives-restated)
2. [The "RAG vs files" question — answered](#the-rag-vs-files-question--answered)
3. [Five combinations that produce real value](#five-combinations-that-produce-real-value)
4. [Five combinations that look clever but cost more than they return](#five-combinations-that-look-clever-but-cost-more-than-they-return)
5. [Seam contracts: what every combination needs](#seam-contracts-what-every-combination-needs)
6. [Cross-skill ownership map](#cross-skill-ownership-map)
7. [Sources](#sources)

## The five substrate primitives, restated

| S | Primitive | Owns |
|---|-----------|------|
| **S1** | Files / git (Markdown, JSON, SQLite, filesystem) | Procedural memory (P15), policy docs, AGENTS.md/CLAUDE.md, solo-tier everything |
| **S2** | Relational + vector co-located (Postgres + pgvector, Supabase, MongoDB Atlas + vector) | Operational truth (P1) + derived memory (P2) + KB chunks (P8) in one substrate |
| **S3** | Dedicated vector DB (Pinecone, Weaviate, Qdrant, Vespa) | Large-scale semantic retrieval surface; per-tenant namespace isolation |
| **S4** | DWH + vector (Snowflake/BigQuery/Databricks + pgvector / external vector) | Compiled wiki (P7) from authoritative facts; SCD2 temporal (P4) |
| **S5** | Graph + vector (Neo4j/Memgraph + vector store) | Multi-hop traversal where relationships *change* the answer; control-framework graph (RA11) |

The substrate is not the architecture. The substrate is the *physical
storage*. The architecture is *which pattern P1–P25 runs on which
substrate, with which seam between them*.

## The "RAG vs files" question — answered

This is the most common confusion. They are not alternatives at the same
level — they answer different questions.

| Question | Substrate | Skill |
|----------|-----------|-------|
| "Where do **agent instructions** live across sessions?" | **Files** (AGENTS.md, CLAUDE.md, `.claude/rules/`, `/memories/`) | `agents-memory` |
| "Where do **learned facts about the user** live?" | **Memory** (typed rows in Postgres OR managed Mem0/Letta) | `ai-context-layer` (P2, P13) |
| "Where do **domain documents** live so the agent can cite them?" | **RAG** (chunks + embeddings + grounding evidence) | `ai-rag` + `ai-vector-brain` |
| "Where does **operational truth** (users, orgs, billing) live?" | **Tools / SQL / system of record** (P1) | `ai-context-layer` (P1) |
| "Where does **procedural memory** (skills, playbooks) live?" | **Files** (Anthropic Skills, P15) | `ai-context-layer` (P15) + `agents-memory` |

The right framing is **"files for what is durable and human-reviewable;
RAG for what is large and grounded; memory for what is learned and
typed; tools for what is operational truth."** A serious app uses all
four. The mistake is forcing one substrate to do another's job.

### Specific anti-patterns this framing prevents

- "We put policies in RAG" → policies need authority hierarchy + effective
  time + paragraph-precise citations (RA11). Vector cosine ranking does
  not respect normative weight. Use the authority-aware KB pattern, not
  raw RAG.
- "We put user preferences in RAG" → preferences are *facts*, not chunks.
  Embedding-similarity on "user prefers dark mode" returns the wrong
  precedent. Store as typed rows with provenance (P2).
- "We put AGENTS.md in a vector DB" → instructions are loaded *every
  turn*, not retrieved by similarity. Vector retrieval for the always-on
  layer adds latency and a similarity gate for content that should not
  be gated. Keep in files.
- "We put everything in files" → solo-tier-correct (T1), startup-fatal
  (T2+). The moment you have concurrent writers or >10⁶ rows of derived
  memory, file-based storage stops scaling on lock contention and search.

## Five combinations that produce real value

These are the combinations that show up repeatedly in production write-ups. Each has documented numbers and a clear seam.

### C1 — Files + Postgres (Tier 1 → Tier 2 graduation path)

```text
┌─────────────────────────────────────────────────────────────┐
│  Files (S1): AGENTS.md, CLAUDE.md, skills/*.md (procedural) │
│              + /memories/ (Anthropic memory tool)            │
│              ↑ read every turn, loaded into system prompt    │
└────────────────────────┬────────────────────────────────────┘
                         │ Agent reads files for HOW;
                         │ queries Postgres for WHAT
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  Postgres (S2): users (P1) + derived_memory (P2)             │
│                 + kb_chunks with pgvector (P8)               │
└─────────────────────────────────────────────────────────────┘
```

- **Seam**: files own *procedure* and *policy*; Postgres owns *state*
  and *retrieved facts*.
- **Real value**: human-readable git review of behavioral changes
  (files), ACID-correct state and retrieval (Postgres). The migration
  story from T1 → T2 keeps files intact and just adds the database.
- **When to use**: any single-tenant or low-tenant startup with
  procedural memory worth versioning.
- **When not to use**: when "files" become a dumping ground for what
  should be typed rows (user preferences in markdown is anti-pattern
  A1).
- **Citations**: `agents-memory` boundary; `references/filesystem-as-memory.md`.

### C2 — Postgres + pgvector co-located (the common startup default)

```text
┌─────────────────────────────────────────────────────────────┐
│  Postgres (single substrate, logical separation)             │
│  ┌──────────────────────────────────────────────────────┐    │
│  │ operational tables (P1)                              │    │
│  │ derived_memory (P2)  ← schema gate P17               │    │
│  │ kb_chunks (P8) WITH pgvector + tsvector              │    │
│  │ episodes / event log                                 │    │
│  └──────────────────────────────────────────────────────┘    │
│  Row-Level Security for per-user/per-org ACL                 │
└─────────────────────────────────────────────────────────────┘
```

- **Seam**: separate *tables* (not separate databases). Each table
  carries its own retention policy, ACL scope, write gate.
- **Real value**: one substrate, one backup, one ops burden. ACID
  joins between operational truth and retrieval results. RLS gives
  multi-tenant safety without a separate identity service. Vendor
  comparison write-ups (a Deeflect migration, a Groovyweb comparison)
  report pgvector cheaper than Pinecone below roughly 50M vectors;
  re-price at your own scale before relying on it.
- **When to use**: T2 default, T3 until tenant scale forces a split.
- **When not to use**: above ~50M vectors per node, or when sub-40ms
  p95 retrieval is non-negotiable.
- **Citations**: RA9 in `reference-architectures.md`; A8 anti-pattern
  is about *logical* convergence (one table for everything), not
  *physical* convergence on one substrate.

### C3 — Files-for-procedure + RAG-for-corpus + Memory-for-facts (three-layer canonical)

```text
┌────────────────────────────────────────────────────────────────┐
│  System prompt assembled from:                                 │
│  ├── Files (S1): AGENTS.md / skill bodies loaded by reference  │
│  ├── Memory (S2 typed rows): user.prefs + behavioral_summary   │
│  └── RAG (S2 or S3): top-k chunks from KB with grounding       │
└────────────────────────────────────────────────────────────────┘
                                ▲
                                │ P12 just-in-time loading
                                │ (only the IDs/refs land in
                                │  the prompt; bodies load on need)
```

- **Seam**: each layer answers a different question; the assembler is
  the contract.
- **Real value**: this is what the `ai-context-layer` skill calls a
  `ContextBundle`. Every layer has its own provenance, ACL, and
  retention. The bundle is what the LLM sees; the substrates are how
  it's stored.
- **When to use**: any agent with all three concerns (instructions,
  learned facts, large corpus). Most real apps.
- **When not to use**: prototypes with no real KB yet (don't build the
  KB layer until you have one).
- **Citations**: `references/context-assembly.md`,
  `references/just-in-time-context-loading.md`.

### C4 — Postgres (truth) + Pinecone/Weaviate (retrieval at scale) + Mem0/Letta (derived memory)

```text
┌─────────────────┐   ┌──────────────────────┐   ┌─────────────────┐
│ Postgres        │   │ Pinecone / Weaviate   │   │ Mem0 / Letta    │
│ - operational   │   │ - per-tenant          │   │ - episodic      │
│   truth (P1)    │   │   namespace           │   │ - profile       │
│ - audit log     │   │ - hybrid retrieval    │   │ - behavioral    │
│   (compliance)  │   │   over KB             │   │ - P13 boundary  │
└────────┬────────┘   └──────────┬───────────┘   └────────┬────────┘
         │                       │                         │
         └───────────────────────┴─────────────────────────┘
                                 │
                                 ▼
                       Assembler with ACL scope
                       (per-tenant token budget)
```

- **Seam**: Postgres = P1 source of truth (never violate this), vector
  store = P8 retrieval at scale, managed memory = P2 derived facts with
  a *P13 boundary contract* (you must be able to re-derive from raw
  episodes if vendor is lost).
- **Real value**: each substrate is best-of-class at its job; tenant
  isolation is enforceable per-substrate; managed-memory accelerates
  feature delivery without surrendering truth.
- **When to use**: T3 with real enterprise customers; T4 retrieval
  surfaces.
- **When not to use**: when nobody has named the P13 boundary explicitly
  (then the managed vendor becomes hard to leave — A28 risk).
- **Citations**: RA3 (multi-tenant), RA12 (multi-agent), Mem0 LOCOMO
  paper (91% p95 latency reduction, >90% token cost reduction, both relative to
  the full-context baseline).

### C5 — DWH + Vector + Wiki (RA1/RA11 mid-enterprise composition)

```text
┌──────────────────────────────────────────────────────────────────┐
│  DWH (Snowflake / BigQuery / Databricks)                          │
│  - SCD2 facts with effective_from/effective_to (P4)               │
│  - lineage to source documents                                    │
│  - retention per regulation                                        │
└────────┬──────────────────────────────────┬──────────────────────┘
         │ nightly P7 compilation           │ CDC reindex
         ▼                                  ▼
┌──────────────────────────┐    ┌──────────────────────────┐
│  Compiled markdown wiki  │    │  Vector store            │
│  (P7) — human-reviewable │───▶│  (pgvector or Pinecone)  │
│  (P9 review surface)     │    │  - hybrid retrieval P8   │
└──────────────────────────┘    └─────────┬────────────────┘
                                          │
                                          ▼
                                  Agent retrieval path
                                  (with paragraph-precise citation
                                   doc_id, version, clause_id,
                                   effective_at)
```

- **Seam**: DWH is *truth-at-rest*; wiki is *human-reviewable rendering*;
  vector store is *agent retrieval index*. All three project from the
  same surrogate key.
- **Real value**: every retrieval can quote (doc_id, version, clause_id,
  effective_at). Humans review the wiki before agents read it (P9).
  Audit story is automatic.
- **When to use**: T4 mid-enterprise with existing DWH; T5 for regulated
  / compliance / policy KBs (RA11).
- **When not to use**: when there is no DWH yet (don't introduce one
  for the context layer alone; cost-prohibitive).
- **Citations**: RA1, RA11; `references/policy-and-compliance-docs.md`;
  Pingcap split-stack pattern.

## Five combinations that look clever but cost more than they return

These are the failure modes you should explicitly reject during design
review. Each is named in the anti-patterns catalog.

### X1 — Vector-only "we put everything in Pinecone" (A8 logical convergence)

- **The pitch**: "Just embed everything — preferences, facts, policies,
  docs. One substrate, simple."
- **Why it fails**: cosine similarity does not respect authority weight
  (policies), does not respect freshness (preferences age), does not
  respect type (user.timezone is not a chunk). You lose ACID, you lose
  audit, you gain the worst search semantics for non-document data.
- **Substitute**: C2 (Postgres + pgvector co-located, separate tables).

### X2 — Graph-everywhere (A33 GraphRAG misapplied to single-hop)

- **The pitch**: "GraphRAG papers report multi-hop gains, let's use
  graph for everything."
- **Why it fails**: "When to use Graphs in RAG" (arXiv 2506.05690) reports
  that GraphRAG frequently underperforms vanilla RAG on many real-world tasks;
  GraphRAG-Bench (arXiv 2506.02404) shows the gains concentrate on multi-hop
  reasoning and states no point gain. Most questions are
  single-hop. The graph adds traversal latency and ingest cost to
  queries that would resolve in one vector hop.
- **Substitute**: route by query shape. Use graph only when the eval
  shows ≥5pt improvement on multi-hop and ≤2pt regression on
  single-hop.

### X3 — Hosted memory as canonical truth (A28)

- **The pitch**: "Mem0/Letta has profile + episodic + procedural,
  let's make it our source of truth."
- **Why it fails**: managed memory vendors are derived-memory stores
  with proprietary schemas. If the vendor changes terms, deprecates an
  API, or you decide to leave, you cannot reconstruct your business
  state. Operational truth must stay in your Postgres.
- **Substitute**: P13 boundary contract. Postgres holds truth; managed
  memory holds the derived projection; you can rebuild from raw
  episodes.

### X4 — DWH in the read path (A30 scope-free managed retrieval)

- **The pitch**: "The DWH has the freshest data, query it from the
  agent."
- **Why it fails**: DWH query latency (seconds) blows the bundle budget
  before you start reasoning. DWH is the *ingestion* path; the agent
  reads from a derived index (vector store or compiled wiki).
- **Substitute**: nightly P7 compilation + CDC reindex.

### X5 — Files-for-everything past T1 (A26 mode collapse via re-ingestion)

- **The pitch**: "Just keep dumping everything into the model's memory
  folder; it's simple."
- **Why it fails**: without P17 (schema-grounded write gate) and P14
  (sleep-time consolidation), the file store accumulates duplicates,
  contradictions, ghost references, "yesterday" baked into text. When
  the model re-reads its own outputs as new "preferences" it converges
  on a single style and rare-but-important strategies decay (A35
  context collapse).
- **Substitute**: any file-based memory at T2+ needs (a) a write
  schema (P17), (b) a consolidation job (P14), and (c) mode-collapse
  evals on a cadence.

## Seam contracts: what every combination needs

A combination is only as good as its seam. Every multi-substrate design
must answer these six questions explicitly:

| # | Seam concern | Concrete output |
|---|--------------|-----------------|
| 1 | **Source of truth (P1)** — which substrate wins when they disagree? | A named substrate per data class; documented in design doc |
| 2 | **Write path (P17)** — who can write to derived memory, with what schema? | Schema validation gate between extractor and store |
| 3 | **Consolidation (P14)** — what background job dedupes, supersedes, re-clusters? | Named job, cadence, eval gate (mode-collapse + context-collapse) |
| 4 | **Boundary (P13)** — what is the contract with each external service? | Required fields, retention, retrieval format, replacement path |
| 5 | **Grounding** — how does each retrieved piece carry provenance? | Per-row fields (source_id, version, valid_from, confidence, owner_scope) |
| 6 | **Failure handling** — what happens when one substrate is down? | Per-substrate graceful degradation policy; what features lose what gracefully |

Combinations C1–C5 above all assume these six contracts are in place.
Skipping any of them turns a clever architecture into the X1–X5 failure
modes above.

## Cross-skill ownership map

```text
USER QUESTION                                        SKILL THAT OWNS THE ANSWER
─────────────────────────────────────────────────    ──────────────────────────────────
"How should I lay out my system?"                    ai-context-layer (this skill)
"How should I chunk and retrieve documents?"         ai-rag
"What SQL/DDL do I need for pgvector?"               ai-vector-brain
"Where do AGENTS.md / CLAUDE.md rules go?"           agents-memory
"Relational, graph, or vector for this entity?"      software-database-design
"How do I expose this as a tool to the agent?"       agents-mcp / ai-agents
"How do I evaluate retrieval quality?"               ai-rag (eval section)
"How do I detect mode/context collapse?"             ai-context-layer (P14/P17/A26/A35)
"How do I keep KB fresh from a portfolio of repos?"  dev-context-multi-repo + ai-context-layer (RA10)
"How do I turn policies into authority-aware KB?"    ai-context-layer (RA11) + ai-rag
```

Two skills almost always compose: `ai-context-layer` (what architecture)
and one or more of `ai-rag` / `ai-vector-brain` / `agents-memory` (how
to implement a layer). The combination patterns C1–C5 above are
expressed in this skill because the *seam* is an architecture decision;
the *substrate detail* lives in the partner skill.

## Sources

Primary sources cited in this doc (all already present in
`data/sources.json`):

- Mem0, *State of AI Agent Memory 2026*
- Mem0, *Building Production-Ready AI Agents with Scalable Long-Term Memory*
  (arXiv:2504.19413)
- Atlan, *Top Vector Databases for Enterprise AI: 2026 Comparison*
- Pingcap, *Best Database for AI Agents (2026)*
- Groovyweb, *Pinecone vs pgvector vs Chroma vs Weaviate (2026)*
- Deeflect, *Supabase vs Pinecone migration write-up*
- Anthropic, *Context engineering: memory, compaction, tool clearing* (cookbook)
- GraphRAG-Bench — arXiv 2506.02404 (Xiao et al., Jun 2025)
- Zhang et al., *Agentic Context Engineering* (arXiv:2510.04618)

Internal cross-references:

- `architectures-by-organization.md` — the org-tier matrix this doc
  complements
- `reference-architectures.md` — RA1–RA13 named recipes
- `patterns-catalog.md` — P1–P25 pattern definitions
- `anti-patterns-catalog.md` — A1–A49 failure modes (X1–X5 above map
  to A8, A33, A28, A30, A26/A35 respectively)
- `vendor-landscape.md` — substrate-by-substrate decision matrix
- `retrieve-vs-preload-vs-finetune.md` — RAG vs CAG vs fine-tune
  decision rubric (orthogonal to substrate combinations)
