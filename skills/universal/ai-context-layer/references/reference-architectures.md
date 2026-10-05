# Reference Architectures

## Table of Contents

- [Recipe index](#recipe-index)
- [RA1 — Living enterprise knowledge base for agents](#ra1--living-enterprise-knowledge-base-for-agents)
- [RA2 — Personal AI with cross-session memory](#ra2--personal-ai-with-cross-session-memory)
- [RA3 — Multi-tenant customer knowledge layer](#ra3--multi-tenant-customer-knowledge-layer)
- [RA4 — Regulated / compliance-aware memory](#ra4--regulated--compliance-aware-memory)
- [RA5 — Agent memory for long-running task execution](#ra5--agent-memory-for-long-running-task-execution)
- [RA6 — Conversational bot with persistent knowledge](#ra6--conversational-bot-with-persistent-knowledge)
- [RA7 — Managed-runtime agent with hosted memory and retrieval](#ra7--managed-runtime-agent-with-hosted-memory-and-retrieval)
- [RA8 — Multimodal workspace context layer](#ra8--multimodal-workspace-context-layer)
- [RA9 — Converged datastore (single-substrate memory + retrieval + ops)](#ra9--converged-datastore-single-substrate-memory--retrieval--ops)
- [RA10 — Multi-repo knowledge base for AI agents](#ra10--multi-repo-knowledge-base-for-ai-agents)
- [RA11 — Policy, compliance & operational-doc context](#ra11--policy-compliance--operational-doc-context)
- [RA12 — Multi-agent team with shared memory](#ra12--multi-agent-team-with-shared-memory)
- [RA13 — Real-time voice agent with sub-300ms memory](#ra13--real-time-voice-agent-with-sub-300ms-memory)
- [Choosing between recipes](#choosing-between-recipes)

**Purpose.** Composed recipes combining patterns from `patterns-catalog.md` against
common problem shapes. Each recipe lists the pattern IDs, non-negotiable
anti-patterns to block, contracts touched, review-surface requirement, and the
verification approach. Use this reference as the starting point when a caller
asks "how should I design X?" — pick the matching recipe, adapt, then run the
anti-pattern sweep.

## Recipe index

| ID | Name | Primary patterns | Review UI |
|----|------|------------------|-----------|
| RA1 | Living enterprise knowledge base for agents | P7 + P4 + P2 | Mandatory |
| RA2 | Personal AI with cross-session memory | P3 + P2 + P8 | Optional |
| RA3 | Multi-tenant customer knowledge layer | P1 + P4 + P8 | Ops-only |
| RA4 | Regulated / compliance-aware memory | P1 + P4 + audit contracts | Mandatory |
| RA5 | Agent memory for long-running task execution | P3 + P4 + FeedbackOutcome | Optional |
| RA6 | Conversational bot with persistent knowledge | P1 + P2/P6 + P8 | Optional |
| RA7 | Managed-runtime agent with hosted memory and retrieval | P1 + P8 + P12 + P13 | Ops-only |
| RA8 | Multimodal workspace context layer | P1 + P8 + P12 + P11 | Optional |
| RA9 | Converged datastore (single-substrate stack) | P1 + P2 + P8 (+ optional P13 for autoEmbed) | Optional |
| RA10 | Multi-repo knowledge base for AI agents | P1 + P4 + P7 + P8 + P10 + P12 | Mandatory if regulated, else Ops-only |
| RA11 | Policy, compliance & operational-doc context | P1 + P4 + P5 + P7 + P8 + P12 | Mandatory |
| RA12 | Multi-agent team with shared memory | P1 + P2 + P11 + P14 + P16 | Ops-only |
| RA13 | Real-time voice agent with sub-300ms memory | P1 + P2 + P12 + cache tier | Optional |

---

## RA1 — Living enterprise knowledge base for agents

**Problem shape.** An organization runs multiple agents that produce and consume
knowledge. Sources arrive over time. Reviewers need to explore the graph,
inspect contradictions, trace facts to sources, and correct mistakes.

**Pattern composition.**

- **P1** as the base — operational truth stays in tools, APIs, and SQL.
  Knowledge extracted from operational state carries a pointer back, not a copy.
- **P7** as the knowledge-compilation layer — pages are compiled from sources
  via the ingest → extract → reconcile → supersede pipeline.
- **P4** as the factual substrate — temporal facts with bi-temporal validity
  windows and non-destructive invalidation; pages cite graph facts by
  `source_episode_id`.
- **P2** as the cross-session memory — user-specific preferences and settings
  live in structured memory, not in wiki pages.
- **P9** as the composition label — because the review surface is mandatory.

**Contracts touched.**

- `KnowledgeSource` — every ingest source registered.
- `LearnedMemory` — all derived facts carry `source_episode_id`, confidence,
  validity window, owner scope.
- `ContextAssemblyRequest` / `ContextBundle` — agents request slices by surface
  and task.
- `FeedbackOutcome` — reviewer decisions and reuse metrics flow back to
  confidence and to the compile queue.

**Review surface.** Mandatory. Full surface: graph view, page view, source
trace, confidence view, contradiction queue (attribution / temporal / stale),
editorial approval with staging. See `inspection-and-review-surfaces.md`.

**Anti-patterns to block.**

- **A1** — no raw chat logs in the wiki; extract first.
- **A4** — contradictions detected at ingest, not at query.
- **A13** — every claim carries `source_episode_id`.
- **A14** — confidence model with decay and reinforcement.
- **A15** — recurring queries compile to synthesis pages.
- **A16** — extraction pipeline runs on every ingest.
- **A17** — review surface ships in the minimum viable form at launch.

**Vendors that fit.** Cognee (P5 variant gives you P7-ready ontology), Graphiti/Zep
(P4 substrate), Letta (if agents are long-running with self-editing memory).
Open-source references: SamurAIGPT/llm-wiki-agent, Ar9av/obsidian-wiki.

**Verification.**

- Reviewer can trace any wiki claim to a source episode in ≤3 clicks.
- Ingesting a contradicting source surfaces a queue item within one pipeline
  run.
- A superseded fact is reachable via as-of query.
- Confidence decays visibly when not reinforced.
- Recurring queries (measured via reuse metrics) have compiled synthesis pages.

---

## RA2 — Personal AI with cross-session memory

**Problem shape.** A personal assistant serves one user across many sessions.
Memory must persist and evolve; preferences must survive model switches;
retrieval runs over a personal document corpus.

**Pattern composition.**

- **P3** self-editing memory blocks — the agent maintains persona, current
  state, and working facts in bounded core memory.
- **P2** structured memory classes — durable, application-owned preferences and
  declared facts the agent cannot silently overwrite.
- **P8** evidence-bearing retrieval — personal corpus (notes, emails, docs)
  queried with citations.
- **P1** operational truth — calendar, tasks, health — stays in tools, not in
  the agent's memory block.

**Contracts touched.** `EntityProfile` (single-user), `LearnedMemory`,
`RetrievalResult`, `ContextBundle` (tight per-surface budgets given personal use).

**Review surface.** Optional. A minimal inspection CLI is enough for the engineer;
consumer products may add a small "memory" page that shows what the agent
remembers. No contradiction queue, no editorial workflow.

**Anti-patterns to block.**

- **A1** — extract facts from dialogue; do not store raw turns as memory.
- **A5** — per-surface bundles; no monolithic system prompt.
- **A11** — forget path exists (user deletes a memory, the block is invalidated).
- **A13** — every recalled fact is citable.

**Vendors that fit.** Letta (P3 native), Mem0 (P2 + episodic), LangGraph Store
(application-owned memory). For self-hosted document ingest into the personal
corpus: **paperless-ngx** (REST API at `/api/documents/`, consume-folder ingest,
built-in OCR) is a lightweight adapter that feeds the P8 retrieval layer without
requiring a cloud document store. Pair with a P8 hybrid index on the same
Postgres/SQLite substrate.

**Verification.** Agent's core block stays under its size ceiling across long
sessions; user-initiated deletion removes facts from `recall` but preserves
audit history; cross-session preferences survive agent restarts.

---

## RA3 — Multi-tenant customer knowledge layer

**Problem shape.** B2B SaaS with many customer tenants. Each tenant has its own
knowledge (configs, docs, conversations, decisions). No cross-tenant leakage is
acceptable. Ops team needs visibility; end users see only their own tenant.

**Pattern composition.**

- **P1** operational truth — tenant state stays in the OLTP store, always
  fetched live with tenant ID as a non-optional filter.
- **P4** temporal facts — per-tenant graph (or tenant-partitioned shared graph)
  with bi-temporal validity.
- **P8** evidence-bearing retrieval — per-tenant index, never a shared index
  with tenant metadata as the only guard.
- **Tenant isolation layer** — enforced at the storage layer, not just the query
  layer. See `references/tenant-isolation-patterns.md`.

**Contracts touched.** `EntityProfile.owner_scope`, `LearnedMemory.owner_scope`,
`RetrievalResult` ACL metadata, `ContextBundle` includes tenant in the
`actor.scope`.

**Review surface.** Ops-only. Engineers and customer success use the review
surface to inspect a specific tenant's knowledge. End users see their own
tenant's KB via the product UI, not via the ops surface.

**Anti-patterns to block.**

- **A10/A30** — no shared vector index across tenants.
- **A8** — separate stores per layer; no monolithic personalization table.
- **A10** — owner_scope enforced at storage; query-layer filters are belt AND
  braces.
- **A13** — every claim carries source + tenant + episode.

**Verification.** A penetration test attempting cross-tenant reads fails at
the storage layer, not just at the query layer. Ops review surface can switch
tenant context without leaking previously-loaded state.

---

## RA4 — Regulated / compliance-aware memory

**Problem shape.** Domain is financial advice, health, legal, or similar. Every
recommendation must be explainable, every fact must be traceable, corrections
must be auditable, and data subject deletion requests must be honored without
breaking audit history.

**Pattern composition.**

- **P1** operational truth — live state from regulated systems of record;
  never cached into derived memory as the canonical value.
- **P4** temporal facts with **mandatory** bi-temporal tracking — separate
  real-world validity time from system knowledge time.
- **Audit-log contract** — every `remember / forget / improve` call writes an
  immutable audit row; reviewer decisions recorded with role and rationale.
- **Deletion-path contract** — GDPR / DSAR deletion uses a distinct code path
  from the normal `forget`. Deletion removes content but preserves the shape of
  history (tombstoned rows rather than vacant).

**Contracts touched.** `LearnedMemory` with `consent_basis`, `valid_from`,
`valid_to`, `recorded_at`, `superseded_at`, `supersedes_id`. Every field
mandatory, none optional.

**Review surface.** Mandatory. Full editorial approval workflow with role
gating. Approved facts leave staging; rejected facts are retained for audit.
Every reviewer action logs role, user, timestamp, rationale.

**Anti-patterns to block.**

- **A3** — no destructive overwrites. Ever.
- **A7** — no hard deletes in the normal path; deletion is a distinct contract.
- **A10** — owner_scope is the core data model axis.
- **A11** — forget is first-class and audited.
- **A13** — every claim traceable to the raw source episode.
- **A17** — review surface is a ship blocker.

**Verification.** DSAR simulation succeeds without breaking audit queries for
unrelated users. Point-in-time queries return the state the system believed on
a given date. Reviewer decisions are reconstructable from the audit log alone.

---

## RA5 — Agent memory for long-running task execution

**Problem shape.** An agent executes a long-running task (multi-step research,
autonomous coding, ongoing campaign). It needs to remember what it tried, what
worked, and what it learned from each step, without losing the thread across
pauses and resumes.

**Pattern composition.**

- **P3** self-editing memory blocks for working state and running conclusions.
- **P4** temporal facts for recorded decisions and their validity over the
  task lifetime; a decision reversed later still has a record of when it was
  believed.
- **FeedbackOutcome contract** — every action in the task has a tied outcome
  row (success / failure / partial / deferred) keyed on the action ID. The
  outcome feeds back into confidence and reuse scoring.

**Contracts touched.** `LearnedMemory` for task-scoped facts, `FeedbackOutcome`
for action results, `ContextBundle` for per-step resume context.

**Review surface.** Optional for internal agents; engineer-only CLI is enough.
Consumer-facing long-running agents may add a small run-log view.

**Anti-patterns to block.**

- **A11** — the agent must be able to forget and supersede its own conclusions.
- **A14** — confidence for decisions decays; a belief held three hours ago
  should not be treated equally with current state unless reinforced.
- **A15** — recurring sub-tasks should hit compiled pages, not re-run full
  exploration.

**Verification.** Pausing and resuming the agent after ≥1 hour preserves core
memory and context; a decision that turns out wrong can be superseded without
destroying the record that it was once believed; action outcomes visibly shape
future decisions.

## RA6 — Conversational bot with persistent knowledge

**Problem shape.** A conversational bot (support, sales, knowledge, or domain-specific)
needs persistent memory that survives across sessions and evolves as the user
interacts. The bot must personalize, remember preferences, track temporal
changes, and explain why it believes a fact — without storing raw chat turns
as "memory."

**Pattern composition.**

- **P1** operational truth — account state, billing, CRM, ticketing stay
  behind tool calls. The bot never copies operational facts into memory.
- **P2 or P6** structured or episodic-semantic memory — atomic facts
  extracted from each conversation at `remember()` time. User-scoped,
  with confidence and validity windows.
- **P4** temporal knowledge graph (when facts change over time) — deal
  intent, customer preferences, config decisions tracked with validity
  windows. Stale facts invalidated, not deleted.
- **P8** evidence-bearing retrieval — KB docs, help articles, product docs
  queried with citations. Grounding layer for the bot's answers.
- **P7** knowledge compilation (optional, for knowledge bots) — recurring
  queries compile into synthesis pages; future turns hit the compiled page
  first, retrieval falls back for gaps. Blocks A15.

**The remember / recall loop.** Memory wires into the conversation turn cycle:

```text
user message → recall(user_id) → assemble ContextBundle
  → generate response → compliance filter → deliver
  → remember(episode, extracted_facts) [background]
```

`remember()` runs after response delivery (background, non-blocking).
`recall()` runs before generation (foreground, latency-critical).

**Contracts touched.** `LearnedMemory` (per-user facts), `ContextBundle`
(per-turn assembly with token budget), `FeedbackOutcome` (user corrections
feed back into memory confidence), `RetrievalResult` (KB grounding with
evidence IDs).

**Review surface.** Optional for most bots. Recommended when the bot is
customer-facing in a regulated domain (RA4 applies) or when the knowledge
layer is user-visible (RA1 applies). A minimal "what the bot remembers about
you" page may be sufficient for consumer products.

**Anti-patterns to block.**

- **A1** — no raw chat transcripts stored as memory. Extract facts first.
- **A2** — operational truth in tools, not in memory or embeddings.
- **A5** — per-surface context bundles, not prompt stuffing.
- **A10** — owner_scope (user_id / tenant_id) on every memory row.
- **A11** — forget path wired to the bot's command handler.
- **A13** — every recalled fact carries source_episode_id.

**Framework fit.**

- **LangGraph** — complex support/sales flows with checkpoints and human
  handoff. Memory as graph state + recall/remember nodes.
- **Claude Agent SDK** — simpler tool-using bots. Memory as
  `recall_user_memory` / `remember_fact` tools.
- **Plain async Python** — linear bots where LangGraph is overhead.
  Memory as service calls in the turn handler.

**Vendors that fit.** Mem0 (P2+P6, support bots), Zep/Graphiti (P4, sales
bots), Cognee (P5+P7, knowledge bots), Letta (P3, self-editing agent memory),
LangGraph Store (P2, application-owned). See
`vendor-landscape.md`.

**Verification.** A returning user gets personalized context without
re-stating preferences; the bot can cite *when* it learned a fact; a user
saying "forget X" removes it from future recall; contradictions between old
and new statements are handled at `remember()` time, not surfaced as
inconsistent answers; `recall()` adds <50ms P95 latency to the turn.

Full wiring guide: `ai-bot-builder/references/bot-memory-integration.md`.

## RA7 — Managed-runtime agent with hosted memory and retrieval

**Problem shape.** Teams want fast adoption on a managed agent/runtime stack
without losing product-owned truth, tenant scope, or deletion/audit control.

**Pattern composition.**

- **P1** operational truth — live user, org, entitlement, and workflow state
  stays in tools, APIs, or SQL.
- **P8** hosted retrieval — corpus grounding and evidence come from a managed
  retrieval layer with stable source IDs.
- **P12** pointer-first loading — refs and handles move through the runtime;
  large payloads load only when the surface needs them.
- **P13** managed-memory boundary — hosted memory is allowed, but it is never
  the canonical profile or account store.

**Contracts touched.** `ContextAssemblyRequest` with refs and owner scope,
`ContextBundle` with typed artifact projections, `LearnedMemory` only for the
 app-owned slice that survives provider changes, and `FeedbackOutcome` for
 local audit and invalidation.

**Review surface.** Ops-only by default. Customer-visible review surfaces still
 need P9.

**Anti-patterns to block.**

- **A2** — provider retrieval or memory must not answer structured account-state
  questions.
- **A28** — hosted memory cannot become the source of truth.
- **A30** — tenant scope must be applied before provider retrieval or memory
  calls.
- **A24** — tool and provider payloads must be compacted before they persist in
  the window.

**Verification.**

- Cutting off the managed-memory provider leaves app-owned truth intact.
- Wrong-scope refs are rejected before retrieval/memory expansion.
- Rebuild from source systems plus local audit logs is documented and tested.
- DSAR/delete semantics are defined in the app layer, not hand-waved to the
  provider.

## RA8 — Multimodal workspace context layer

**Problem shape.** The assistant works across files, screenshots, dashboards,
 notes, docs, and tool outputs. The hard problem is not storage alone; it is
 loading the right artifacts without stuffing the whole workspace into the
 model window.

**Pattern composition.**

- **P1** operational truth — workspace state, permissions, and live metadata
  stay behind tools.
- **P8** evidence-bearing retrieval — docs, notes, and page text still need
  citations.
- **P12** pointer-first loading — the request carries refs, not raw files.
- **P11** sub-agent isolation — deep search or heavy artifact inspection runs
  in a separate window when it would distract the parent.

**Contracts touched.** `ContextRef`, `ArtifactRef`, `LoadedArtifact`,
`ContextAssemblyRequest`, `ContextBundle`.

**Review surface.** Optional for internal tools; mandatory when multimodal
 evidence is user-visible in regulated settings.

**Anti-patterns to block.**

- **A5** — no prompt stuffing of full file payloads.
- **A27** — no eager loading of every artifact in the workspace.
- **A29** — raw file payloads do not enter the bundle; only typed projections.
- **A23** — OCR text, doc text, and tool outputs are tagged as data, not
  instructions.

**Verification.**

- A small surface request loads only the artifacts it references.
- Artifact projections preserve source ref IDs and evidence IDs after
  compression.
- Multimodal bundles stay under budget while preserving enough typed detail to
  explain the answer.
- Deep artifact analysis can be delegated to a sub-agent without inflating the
  parent bundle.

## RA9 — Converged datastore (single-substrate memory + retrieval + ops)

**Problem shape.** One small team. One substrate already in production. The
operational documents, agent memory, conversation checkpoints, and chunk
retrieval should live in one cluster with one backup, one ACL story, and one
migration story — not three. Vendor pitches for all-in-one
document/Postgres stores codify this. RA9 is the "yes, this is legitimate" answer
*with explicit guardrails*, distinguishing it from anti-pattern A8 (monolithic
personalization table).

**When RA9 wins.**

- Operational data already lives in the chosen substrate; pulling agent memory
  out doubles the ops surface.
- Team size is small enough that one team owns the full stack; the cost of
  *separation* (separate failure domain, separate connection pool, separate
  on-call) is paid daily, the cost of *convergence* (vendor lock, embedding
  coupling) is paid only on a vendor change.
- Vector workload fits one cluster's vector-index tier (typical ceiling
  ~10–100M vectors per cluster on Atlas M30+; ~10–50M with pgvector HNSW on
  Supabase / Aurora).

**When RA9 loses.**

- Bi-temporal facts are needed (P4) — RA1 / RA4 dominate.
- Hard tenant isolation (regulated, multi-customer SaaS) — RA3 dominates.
- Workload exceeds single-cluster vector capacity — split retrieval onto a
  dedicated vector DB and keep RA9 only for memory.
- Embedding model switching is on the roadmap and `autoEmbed` would lock you in.

**Pattern composition.**

- **P1** operational truth — already-modeled documents/rows are the source of
  truth. RA9 keeps them physically near memory but logically distinct.
- **P2** structured memory in *separate collections / tables* — never the same
  collection as operational documents, even when convenient.
- **P8** evidence-bearing retrieval — chunks live in their own collection /
  table. Vector index scoped to that collection only.
- **P13** managed-memory boundary — applies if `autoEmbed` (MongoDB) or
  `pg_net`-backed embedding triggers (Supabase) are used. The vendor owns the
  embedding model; you own the source text and the migration plan.

**Substrate options.**

- **MongoDB Atlas 8.3+** — operational docs, `learned_memory`, `knowledge_chunk`
  with `autoEmbed` (Voyage 4), LangGraph MongoDB checkpointer for short-term
  memory. See `builds/cookbooks/mongodb_atlas.md`.
- **Supabase / Postgres + pgvector 0.8+** — `app_*` tables for operational truth,
  `learned_memory`, `knowledge_chunk` with HNSW or IVFFlat, RLS for tenant
  isolation, edge functions for embedding generation. See
  `builds/cookbooks/pgvector.md`.
- **Convex** — operational state, vector search, scheduled jobs in one TS
  backend. Fits when the whole stack is already TypeScript-only and reactivity
  matters.

**Contracts touched.** All four core contracts in one cluster: `EntityProfile`,
`LearnedMemory`, `RetrievalResult`, `ContextAssemblyRequest` / `ContextBundle`,
plus checkpointer documents for short-term thread state.

**Review surface.** Optional. RA9 is engineering-economics-driven, not
review-driven. If a review surface is required, RA9 is *not* the right recipe —
promote to RA1 or RA4.

**Anti-patterns to block.**

- **A10/A30** — even with everything in one cluster, the vector index is per
  collection; no single shared vector index across tenants or memory layers.
- **A8** — operational truth, memory, and chunks remain in *separate
  collections / tables*. The convergence is physical, not logical.
- **A10** — `owner_scope` enforced on every read; per-tenant collection or
  prefix discipline at scale.
- **A11** — forget path wired (non-destructive flag, never `deleteOne`).
- **A13** — every memory row carries `source_episode_id`.
- **A28** — even on a converged stack, derived memory is never the canonical
  answer to operational questions.
- **A30** — scope enforced before any vector query, especially before
  `autoEmbed`-backed retrieval.

**Guardrails specific to convergence.**

1. **Logical separation is non-negotiable.** Memory and operational docs share a
   cluster, never a collection or a table.
2. **`autoEmbed` is only for chunks**, never for memory. Memory rows where
   embeddings are part of an audit chain need explicit, app-controlled
   embedding.
3. **Document the split-out path.** What does it take to move chunk retrieval
   onto Qdrant or Milvus when scale demands? If that question is unanswered,
   you have not earned convergence — you have postponed a decision.
4. **Vendor migration plan is a P13 deliverable.** Source text retained, model
   choice abstracted in code, re-embed cost estimated.

**Verification.**

- A penetration test attempting to read another tenant's memory via vector
  search returns zero rows (scope filter applied before vector pre-filter).
- Switching the autoEmbed model is exercised on a representative collection
  (drop index → new model → backfill → verify recall) before production.
- A dry-run "split-out chunk retrieval to dedicated vector DB" plan exists in
  the architecture doc, with realistic time and cost.
- Provider-side outage of the embedding endpoint degrades retrieval but does
  not corrupt memory or operational truth.

**Vendors that fit.** MongoDB Atlas 8.3+ (`mongodb_atlas.md` cookbook),
Supabase, Postgres + pgvector 0.8+ (`pgvector.md` cookbook), Convex. See
`vendor-landscape.md`.

---

## RA10 — Multi-repo knowledge base for AI agents

**Problem shape.** A team has dozens-to-hundreds of git repositories
(microservices, infra, docs, coordination/hub repo) and wants AI agents to
reason over the *current* state of that portfolio. Knowledge lives in markdown
(ADRs, runbooks, design notes, AML/compliance memos), in code, in CI configs,
and in the coordination repo's domain-by-lifecycle folders. The portfolio
changes every day; the KB must stay fresh without re-embedding the world.

This is the `requirements-hub`-shaped case: 100+ repos, coordination
repo with `business/cards/crypto/payments/` × `as-is/assessment/initiatives/`
folders, FCA EMI-regulated, hundreds of markdown files, multiple agents
consuming the layer.

**When RA10 wins.**

- The corpus is git-anchored — every fact has a commit, a path, a blob hash.
- Many sources, many readers, many agents — a single KB layer beats per-agent
  retrieval rebuilds.
- Freshness matters more than peak recall — agents must not cite a doc that
  was deleted last Tuesday.
- A regulated overlay applies (RA4 composes on top) — every recalled fact must
  trace to `(repo, path, commit_sha)`.

**When RA10 loses.**

- Single-repo or few-repo cases — RA1 (enterprise wiki) or plain RAG is enough.
- The corpus is non-git (Confluence, SharePoint, Notion) — keep RA1; the
  freshness pattern transfers but the commit-anchoring does not.
- The team needs full-text search only, no embeddings — Sourcegraph or
  ripgrep-on-a-cron is the cheaper answer.

**Pattern composition.**

- **P1** operational truth — repo metadata (default branch, owner, lifecycle
  stage) lives in the portfolio catalog, not in derived memory.
- **P4** temporal facts — every chunk row carries `valid_from_commit` and
  optional `valid_to_commit`. Bi-temporal queries answer "what did we believe
  on date X." Required for regulated overlay (RA4).
- **P7** knowledge compilation — recurring agent queries compile into wiki-shaped
  synthesis pages stored back into the coordination repo, reviewable in PRs.
- **P8** evidence-bearing retrieval — every recall returns
  `(repo, path, commit_sha, anchor)` so agents and humans can open the source.
- **P10** filesystem-as-memory — git is the canonical store; the vector index
  is a derived projection that can always be rebuilt from `git log`.
- **P12** just-in-time loading — agents receive `ContextRef` pointers
  (`repo://<name>@<sha>:<path>#<anchor>`); raw file content loads only when the
  agent calls `load_artifact`.
- **P13** if a managed embedding service is used (Voyage, OpenAI, Cohere) —
  the model owns embeddings only; `(repo, path, commit_sha, source_text)` is
  always app-owned.

**Substrate decision.**

- **Regulated (RA4 composes)** → Postgres + pgvector with RLS, audit log
  table, tombstoned deletes. *Not MongoDB autoEmbed* — the embedding model
  becoming an index property breaks audit chains.
- **Non-regulated, small team** → RA9 substrate (MongoDB Atlas, Supabase,
  Convex) is fine; chunks collection with autoEmbed, memory collection with
  app-controlled embedding.
- **Hyper-scale (>10M chunks)** → split retrieval onto Qdrant or Vespa, keep
  bi-temporal facts in Postgres.

**Contracts touched.**

- `KnowledgeSource` — one row per (repo, branch); registers the ingest source.
- `LearnedMemory` extended with: `source_repo`, `source_path`,
  `source_commit_sha`, `content_hash`, `valid_from_commit`, `valid_to_commit`,
  `chunk_anchor` (heading path or line range).
- `ContextRef` — pointers, not payloads, in `ContextBundle`.
- `FeedbackOutcome` — agent citations and reviewer corrections feed back to
  confidence and to the compile queue.

**Ingest pipeline.**

```text
git event (push / nightly poll / webhook)
  → diff(previous_indexed_sha, current_sha)
  → for each changed markdown file:
      emit_chunks(file, commit_sha)         # heading-aware split
      content_hash = blake3(chunk_text)
      if content_hash unchanged: skip       # idempotency
      else: embed → upsert(chunk_id, …, valid_from_commit=current_sha)
  → for each deleted file:
      mark valid_to_commit=current_sha      # tombstone, not delete
  → write ingest_run row (repo, sha, started_at, finished_at, stats)
```

Worked example, schema, and webhook plumbing in
`builds/cookbooks/git_repo_ingest.md`. Diff-emission and idempotency rules in
`references/git-anchored-ingestion.md`. Heading-aware chunking rules in
`references/markdown-chunking-patterns.md`.

**Hub / catalog layer.** A coordination repo (e.g. `requirements-hub`) carries
the portfolio catalog (`profiles/<repo>.json` or richer domain × lifecycle
folders). The catalog answers "what repos are in scope, who owns them, what
lifecycle phase are they in." The vector index references catalog repo IDs.
See partner skill `dev-context-multi-repo` for the catalog and freshness
tooling — RA10 consumes its `discover_repos.py`, `report_drift.py`, and
`check_hub_freshness.sh` outputs.

**Review surface.**

- **Mandatory** when a regulated overlay applies (RA4): editorial workflow,
  source trace, contradiction queue.
- **Ops-only** otherwise: an internal page that shows last ingest run per
  repo, freshness lag, contradiction count, and a search-with-citations view.

**Anti-patterns to block.**

- **A1** — chunk markdown into atomic facts; do not store raw chat or PR
  threads as memory.
- **A10/A30** — vector index per tenant or per portfolio. A single shared index
  across customer portfolios with `tenant_id` as a metadata filter is forbidden
  (storage-layer enforcement, not query-layer).
- **A4** — contradictions detected at ingest, not at query. Two repos
  disagreeing about an AML threshold surfaces a queue item.
- **A11** — repo deletion or file deletion sets `valid_to_commit`; a recall
  with `as_of=<past_sha>` still returns the old fact.
- **A13** — every recall row carries `(repo, path, commit_sha)`.
- **A15** — recurring queries (measured) compile to synthesis pages in the
  hub repo; agents hit the page first, fall back to retrieval for gaps.
- **A28** — derived memory never answers "what is the canonical owner of repo
  X" — that question hits the catalog, not the vector index.
- **A30** — tenant scope and repo allowlist applied *before* the vector
  search, never as a post-filter.

**Vendors that fit.**

- **Postgres + pgvector 0.8+** (regulated default) — RLS, iterative scans,
  tombstones, `pg_cron` for nightly polls.
- **MongoDB Atlas 8.3+** (non-regulated converged) — autoEmbed for chunks,
  app-controlled embedding for memory.
- **Qdrant / Weaviate / Milvus** (hyper-scale retrieval split-out) — when
  chunk count exceeds single-cluster vector tier.
- **GitHub Actions / GitLab CI / `pg_cron`** for the ingest scheduler;
  webhooks for low-latency.

See `vendor-landscape.md` and `builds/cookbooks/{pgvector,mongodb_atlas}.md`.

**Verification.**

- A file deleted in commit `Y` returns no results from `recall(as_of=now)`
  but still returns from `recall(as_of=X)` where `X < Y`.
- A force-pushed branch is detected and re-embedded (commit ancestry check).
- Re-running the ingest pipeline against an unchanged repo embeds zero
  chunks (`content_hash` idempotency).
- Every recall result is openable as `repo://<name>@<sha>:<path>#<anchor>`.
- Freshness lag (max time since last successful ingest run, per repo) is on
  a dashboard with an SLO; staleness > N days raises an alert.
- DSAR simulation: deleting all rows for one tenant succeeds without breaking
  audit reconstruction for other tenants (regulated overlay).
- A representative agent query that *should* miss returns "no evidence" with
  a clean empty result, not a hallucinated answer.

---

## RA11 — Policy, compliance & operational-doc context

**Problem shape.** A regulated firm holds dozens to hundreds of policies,
standards, procedures, runbooks, regulator letters, and internal guides.
Some live in git markdown, some in Confluence/SharePoint/Notion, some are
PDFs from regulators, some are exported Word docs from legal. AI agents
(compliance copilot, AML reviewer, change-risk advisor, customer-facing
chatbot) must answer policy-anchored questions with paragraph-level
citations: *"Per AML Policy v3.4 §4.2(a), effective 2026-02-01, the
threshold is …"*. The KB must distinguish a binding regulator rule from an
internal guideline, must show the chain from regulation → policy → standard
→ runbook → code, and must never quote a policy that was superseded last
quarter.

This composes on top of RA10 (when policies live in git) and on top of RA4
(regulated overlay). It dominates RA1 (enterprise wiki) for any compliance-
or audit-bearing use.

**When RA11 wins.**

- Citations must be paragraph- or clause-precise (regulators, auditors,
  legal disputes, FCA/PRA/EBA-style supervision).
- Authority matters: an answer must say *which* policy, *what version*, *as
  of when*, with normative weight (mandatory / recommended / informational).
- Multiple agents need the same compliance grounding: a chatbot answering a
  customer, a code-review agent flagging non-compliant changes, an AML
  alerts triager — all must agree on what the policy says today.
- Cross-references matter: "this internal standard implements ISO 27001
  A.5.7 and PSD2 RTS Article 18, operationalized by runbook RB-PAY-014"
  is a graph traversal, not a search query.

**When RA11 loses.**

- A handful of static FAQ docs — RA6 (conversational bot) with plain RAG
  is enough.
- All "policies" are internal soft guidelines with no audit pressure — RA1
  is enough.
- Policies and code live in the same git repo and never change formats —
  RA10 alone covers it; RA11's added authority/effective-date contracts
  are overkill.

**Pattern composition.**

- **P1** operational truth — policy registry (which docs exist, who owns
  them, current version, effective date, supersession chain) is a system of
  record, *not* a derived index. Hosted in a dedicated `policy_registry`
  table or service, queried live by tools.
- **P4** temporal facts — every chunk and every cross-reference carries an
  *effective-time* window (`effective_from`, `effective_to`,
  `superseded_by`), separate from system-time / commit-time. A regulator
  asks "what was your policy on 2025-09-12?" — the answer must use
  effective-time, not ingest-time.
- **P5** ontology / graph — policy → standard → procedure → runbook → code
  links are first-class edges, not implicit. So are control-framework
  mappings (ISO 27001 control ID, NIST SP 800-53 control, PSD2 RTS article).
  Graph traversal answers "what runbooks operationalize PCI-DSS Req 8.3?"
  in ways pure embedding similarity cannot.
- **P7** knowledge compilation with **mandatory** editorial review — every
  policy chunk is reviewer-approved before it joins the live KB. New
  versions go to staging; reviewer approves the version cutover. Old
  version stays queryable via effective-time.
- **P8** evidence-bearing retrieval with paragraph-precise anchors —
  citation contract extends to `(doc_id, version, clause_id,
  effective_at)`, not just chunk hash.
- **P12** just-in-time loading — agents receive `ContextRef` pointers like
  `policy://aml-policy@v3.4#§4.2.a`; raw clause text loads only when the
  agent calls `load_artifact`. Saves window space and gives the audit log a
  precise "what did the agent see" record.

**Authority hierarchy.** Every chunk row carries a `normative_weight` enum.
Without it, a model treats a draft guideline and a regulator's binding rule
as equivalent evidence. A workable hierarchy:

| Weight | Examples | Override behavior |
|--------|----------|-------------------|
| `regulation` | FCA Handbook, EBA RTS, PSD2 SCA | Cannot be relaxed by lower weights; conflict surfaces as a queue item |
| `policy` | Internal AML Policy, Information Security Policy | Implements regulations; binding internally |
| `standard` | Encryption Standard, Logging Standard; external standards such as ISO/IEC 27001 are voluntary until a contract or regulator adopts them, then they inherit that weight | Implements policy; testable |
| `procedure` | "How to onboard a corporate customer" | Implements standards; auditable |
| `runbook` | Incident response playbook | Operational; cited but not normative |
| `guideline` | Style guide, README, ADR-as-guidance | Informational; never cited as compliance evidence |

Conflicts between weights are resolved upward (regulation wins). Conflicts
within the same weight are reviewer-resolved.

**Source heterogeneity.** Policies do not all live in git. Build a
**polyglot ingest layer** that normalizes to a single chunk schema:

| Source | Adapter | Notes |
|--------|---------|-------|
| Git markdown | RA10 ingestion (commit-anchored) | Default for engineered orgs |
| Confluence | REST API + page-version webhooks | Page-version-as-time; heading-aware extraction |
| SharePoint / Word `.docx` | python-docx + heading walker | Track-changes preserved as superseded chunks |
| Regulator PDFs | OCR + clause-tree extractor (e.g., Marker, Docling, LayoutLMv3-class) | Preserve numbered clauses, footnotes |
| Notion | Notion API + block-level versioning | Block IDs survive renames |
| Email/letter ingest | Manual upload + register row in `policy_registry` | Regulator letters are first-class evidence |

Each adapter emits the same `PolicyChunk` shape: `(doc_id, version,
clause_id, normative_weight, effective_from, effective_to, source_uri,
content_hash, text, owner_scope)`. Heading-aware chunking rules from
`markdown-chunking-patterns.md` apply to any source that has structure;
PDFs use clause numbering as the anchor.

**Cross-reference graph.** Build edges at ingest time, not at query time:

```text
(:Policy {id, version})-[:IMPLEMENTS]->(:Regulation {id, clause})
(:Standard)-[:IMPLEMENTS]->(:Policy)
(:Procedure)-[:IMPLEMENTS]->(:Standard)
(:Runbook)-[:OPERATIONALIZES]->(:Procedure)
(:CodeArtifact {repo, path})-[:ENFORCES]->(:Standard)        // from RA10
(:Policy)-[:SUPERSEDED_BY]->(:Policy)
(:Policy)-[:CITES]->(:Regulation {id, clause})
(:Control {framework, id})<-[:MAPS_TO]-(:Policy)             // ISO/NIST/PCI
```

Substrate options: Neo4j + Graphiti for bi-temporal graph; Postgres with a
`policy_edge` table for simpler stacks; MongoDB Atlas with `$graphLookup`
when you are already on the converged stack (RA9). The graph is small (~10⁴
nodes, ~10⁵ edges for a mid-size firm) — even a serialized JSON graph fits
in memory if scale is small.

**Compliance retrieval pattern.** When an agent asks a policy-anchored
question, the assembly path is:

```text
question → entity recognition (regulation IDs, control IDs, policy names)
        → graph traversal (resolve to live policy versions, follow IMPLEMENTS edges)
        → P8 retrieval over the resolved chunk set, weighted by authority
        → ContextBundle with: citation block (doc, version, clause, effective_at),
          conflict warnings (if multiple normative weights disagree),
          related runbooks, related code artifacts (RA10 join)
```

This is the layered pattern: graph picks the *right* documents, retrieval
picks the *right paragraphs*, the bundle carries the citation contract.

**Contracts touched.**

- `KnowledgeSource` extended: `source_type` (regulation / policy / standard
  / procedure / runbook / guideline), `authority_owner` (legal / compliance
  / security / engineering), `next_review_at`.
- `LearnedMemory` / `policy_chunk` extended: `doc_id`, `version`,
  `clause_id`, `normative_weight`, `effective_from`, `effective_to`,
  `superseded_by`, `control_mappings` (array of `{framework, control_id}`).
- `ContextBundle` carries a `citations` block typed for compliance:
  `{doc_id, version, clause_id, effective_at, normative_weight,
  source_uri}`. Agents must surface this verbatim — no paraphrasing.
- `FeedbackOutcome` — when a reviewer corrects a citation or flags a stale
  policy, the correction feeds back into confidence and triggers a
  re-extraction.

**Review surface.** **Mandatory.** This is non-negotiable in regulated
contexts. Required surfaces:

- **Policy registry view** — every doc, current version, effective date,
  next review date, owner. Stale-policy SLO dashboard.
- **Version diff view** — clause-level diff between two policy versions,
  reviewer-approvable.
- **Citation trace** — for any agent answer in production, click through to
  the exact clause the agent cited; verify it matches the policy version
  that was effective at the time of the query.
- **Control-mapping matrix** — show which policies / standards / runbooks
  cover each external control (ISO 27001, NIST 800-53, PCI-DSS, PSD2 RTS).
  Gaps light up red.
- **Contradiction queue** — when ingest detects two policies disagreeing,
  or a policy contradicting a regulation, route to legal/compliance.

See `inspection-and-review-surfaces.md` for the editorial workflow.

**Anti-patterns to block.**

- **A1** — never embed raw regulator PDFs as one chunk. Extract clause
  structure first.
- **A10/A30** — never share a policy index across tenants in a multi-tenant SaaS;
  one tenant's bespoke policies must not surface for another.
- **A3** / **A11** — old policy versions are tombstoned via
  `effective_to` + `superseded_by`, never deleted; audit reconstruction
  depends on this.
- **A4** — contradictions between authority levels surface at ingest time,
  not when an agent answers a customer question with conflicting policy
  text.
- **A13** — every recall row carries `(doc_id, version, clause_id,
  effective_at)`. A claim without a clause anchor is rejected at write
  time.
- **A14** — confidence on policy chunks is bounded by *authority*: a
  regulation chunk starts at confidence 1.0 and never decays; an internal
  guideline can decay; a runbook decays faster.
- **A15** — recurring compliance questions ("is this transaction reportable
  under MLR 2017?") compile to synthesis pages with reviewer approval, not
  re-RAGged each time.
- **A23** — policy text is data, not instructions. A regulator quoting "you
  must…" inside an ingested doc is *content*, not a system instruction the
  model should follow.
- **A28** — derived policy chunks never become the canonical "what is the
  current version of Policy X" — that question hits `policy_registry`
  (P1), not the vector index.

**Vendors that fit.**

- **Postgres + pgvector + Neo4j** (regulated default) — pgvector for chunk
  retrieval, Neo4j for the cross-reference graph, RLS on both for tenant
  isolation. Optionally Graphiti on Neo4j for bi-temporal graph.
- **MongoDB Atlas 8.3+** with `$graphLookup` — converged stack when graph
  size is small and team is already on Atlas (RA9 substrate).
- **Cognee** for ontology-bearing retrieval (P5+P7) when the team prefers a
  framework over rolling its own graph + retrieval composition.
- **Document ingest helpers**: `unstructured.io` for heterogeneous parsing,
  Marker / Docling for PDF clause extraction, Confluence / Notion /
  SharePoint REST adapters for live-source ingestion.

See `vendor-landscape.md` and the policy-doc deep dive in
`references/policy-and-compliance-docs.md`.

**Verification.**

- A regulator-style query — *"What was your AML threshold on 2025-09-12?"* —
  returns the clause that was effective on that date with paragraph-precise
  citation, even if the policy has since been superseded twice.
- A control-mapping audit query — *"Show every internal artifact that
  covers ISO 27001 A.5.7"* — returns policy + standards + runbooks +
  related code artifacts (RA10 join), with normative weights ranked.
- Two policies disagreeing produces a contradiction-queue item within one
  ingest run; the agent refuses to answer with conflicting text and surfaces
  the conflict.
- A policy past its `next_review_at` lights up red in the registry; agents
  citing it surface a "stale policy" warning in the bundle.
- DSAR / regulator-deletion path tombstones one tenant's policies without
  breaking the cross-reference graph for other tenants.
- A retired policy is not retrievable in `recall(as_of=now)` but *is*
  retrievable via `recall(as_of=<past>)`.

---

## RA12 — Multi-agent team with shared memory

**Problem shape.** An orchestrator agent coordinates several task agents
on a shared objective (deep research, multi-step incident response,
compliance review with parallel sub-investigations). They must coordinate
— hand off intermediate findings, agree on decisions, avoid duplicating
work — but one agent's hallucinated claim must not silently corrupt the
others. P11 isolation alone kills coordination; a global blackboard
without barriers propagates errors.

**When RA12 wins.**

- ≥2 cooperating agents with overlapping tasks; pure handoff messaging
  doesn't carry enough state.
- Long-horizon work where re-deriving context is expensive.
- The team is small enough that named role namespaces are tractable
  (orchestrator, researchers, validators, summarizer).

**When RA12 loses.**

- One agent is enough — RA5 covers it.
- Fully independent sub-tasks — P11 isolation alone, no shared memory.
- A swarm of >50 agents — graduate to a job queue / event bus pattern;
  shared memory at that scale becomes a global garbage bin.

**Pattern composition.**

- **P1** operational truth — system-of-record state stays in tools.
  Shared memory is for *agent-team artifacts* (decisions, claims,
  blackboard entries), never for billing or entitlement.
- **P2** structured user-scoped memory remains app-owned and *not*
  shared cross-agent. A team writing user preferences into a shared
  blackboard is breaking P2.
- **P11** sub-agent isolation — long-horizon sub-tasks still get their
  own window; only validated, promoted artifacts cross the boundary.
- **P14** sleep-time consolidation runs *per namespace* — orchestrator
  scratch, task-agent scratch, shared decisions all consolidate
  independently.
- **P16** the load-bearing pattern — provenance per write, per-agent
  scratch namespaces, validation gate at `promote`, role-keyed
  namespaces.

**Boundary diagram.**

```
                ┌─────────────────────────────────────┐
                │  shared.decisions  (read-many)      │
                │  shared.facts      (read-many)      │   ← validation gate
                └────────────────▲────────────────────┘     (P16 promote)
                                 │ promote()
   ┌────────────────────┬────────┴────────┬────────────────┐
   │ scratch.orchestr.  │ scratch.task_a  │ scratch.task_b │ ...
   │ (writer = orch)    │ (writer = a)    │ (writer = b)   │
   └────────────────────┴─────────────────┴────────────────┘
```

**Contracts touched.** `LearnedMemory` extended with `writer_agent`,
`role`, `namespace`, `promotion_status`. `FeedbackOutcome` keyed on
`writer_agent` so blame-assignment works after the fact.
`ContextBundle` filters by allowed namespaces per agent role.

**Substrate options.**

- **LangGraph Store** — namespace-keyed, native fit; the usual
  default for agent teams already on LangGraph.
- **Postgres** — `namespace` + `writer_agent` columns with row-level
  filters; works at small/medium scale.
- **Hindsight MCP / shared memory layer** — when agents span apps and
  need cross-app continuity.
- **Redis Agent Memory Server** — for hot scratch namespaces with
  TTL-based eviction; durable layer behind it.

**Review surface.** Ops-only. Engineers need a "who wrote what" view
across namespaces; consumer-facing surfaces don't expose it.

**Anti-patterns to block.**

- **A2** / **A10** — namespace ACL at storage; agents see only their
  scratch + the shared layer they have read access to.
- **A13** — every shared row carries `writer_agent + source_episode_id`.
- **A26** / **A31** — consolidation runs per namespace; no cross-
  namespace promotion via "merging."
- **A32** — the load-bearing block; promotion gate enforces validation.
- **A11** — `forget` is wired per namespace; consolidating dead
  scratch namespaces is part of the lifecycle.

**Vendors that fit.** LangGraph Store (default if already on LangGraph), Hindsight MCP
multi-agent shared memory, Mem0 with multi-agent extension, Supermemory
(cross-agent continuity). See `vendor-landscape.md`.

**Verification.**

- Promoting a claim from `scratch.task_a` runs the validation sweep
  (schema, contradiction, confidence floor); a failing claim stays in
  scratch with a recorded reason.
- A penetration test where one agent attempts to write to another's
  scratch namespace is rejected at storage.
- Killing one task agent mid-run does not corrupt shared state; its
  scratch namespace is consolidated or discarded by P14.
- Blame-assignment query "who introduced claim X" returns
  `writer_agent` + `source_episode_id` deterministically.

---

## RA13 — Real-time voice agent with sub-300ms memory

**Problem shape.** A voice agent (customer support, in-car assistant,
voice-first companion) must hold the 200–300ms human-conversation
response window end-to-end. The standard chat memory path —
synchronous embedding lookup on every turn — overshoots the budget by
itself. The recipe is *not* "use less memory"; it is "split memory by
latency tier."

The Salesforce VoiceAgentRAG paper describes the dual-agent
memory router pattern: foreground "Fast Talker" handles cache-hot
recall, background "Slow Thinker" pre-fetches and consolidates. The paper
reports a 75% cache hit rate and a 316× retrieval speedup vs direct
vector lookup (self-reported; verify on your own traffic).

**When RA13 wins.**

- Real-time voice or video where every additional 100ms of memory
  latency is user-perceivable.
- The corpus has predictable per-user hot sets (customer profile,
  recent transactions, last conversation summary).

**When RA13 loses.**

- Asynchronous voice (transcription + delayed response) — chat
  recipes apply.
- The corpus is large and unpredictable on every turn — accept
  retrieval latency, hide it with a brief acknowledgment turn.

**Pattern composition.**

- **P1** operational truth — live tool calls (account, order status)
  go through normal APIs; do not put them in the cache path. Voice
  surfaces tend to *want* to cache operational truth and that is the
  exact thing that breaks: a stale account balance read aloud.
- **P2** structured memory with *two* tiers — a hot tier (per-user
  cache, ≤100 rows, sub-ms read) and a cold tier (full memory store
  on the standard substrate).
- **P12** pointer-first loading — most turns hit refs; only the
  ~25% cache miss touches cold storage.
- **Cache tier as a first-class architectural element** — Redis /
  in-process LRU / sub-ms KV. The cache *is* the memory at request
  time; the cold tier is the source.

**Latency budget.**

```
turn budget                                ~250ms target
  ├─ ASR (speech → text)                    ~80ms
  ├─ memory recall                          ≤10ms   ← Fast Talker
  ├─ LLM generation (streaming)             ~80ms TTFT
  ├─ TTS (text → speech, streaming)         ~70ms TTFT
  └─ network + buffering                    ~10ms
```

The memory budget is hard: ≤10ms. Anything more eats into the LLM
budget and breaks streaming TTS prosody.

**Architecture.**

```
turn ──▶ Fast Talker
          ├─ hot-set lookup (user_id → recent memories)   ~1ms
          ├─ if hit  → assemble bundle, return
          └─ if miss → return minimal bundle, mark "needs hydration"
                                  │
                                  ▼ async
                       Slow Thinker (background)
                         ├─ vector recall over cold tier
                         ├─ pre-fetch likely next-turn memories
                         ├─ update hot set for this user
                         └─ run P14 consolidation off-peak
```

**Contracts touched.** `ContextBundle` carries a `tier` indicator
(`hot` / `cold` / `degraded`); the agent's response style adapts
slightly when in `degraded` mode. `LearnedMemory` extended with
`hot_set_eligible: bool` and `last_promoted_at`.

**Review surface.** Optional. Voice products usually expose a "what
the agent remembers about you" page asynchronously, not at request
time.

**Anti-patterns to block.**

- **A34** — the load-bearing block; memory architecture matches the
  latency tier of the surface.
- **A28** — never cache operational truth (P1) in the hot tier;
  cache learned memories only.
- **A8** — hot set per user, not a global table.
- **A24** — tool-result compaction is critical; voice cannot afford
  raw tool payloads in the window.
- **A11** — `forget` invalidates both hot and cold tiers atomically;
  a deleted memory must not survive in cache.

**Vendors that fit.** Redis Agent Memory Server (hot tier);
Mem0 voice profile; Supermemory voice cookbook;
LiveKit / Pipecat / Vapi as the voice runtime — memory plugs in via
their context-pre-call hook. See `vendor-landscape.md`.

**Verification.**

- P95 memory-recall latency on cache hits ≤ 10ms; on misses, agent
  emits a brief acknowledgment turn rather than blocking.
- Forget propagates to hot tier within one TTL window.
- Operational-truth queries (account balance) bypass the cache and
  hit the live tool path; an inserted "stale balance" test row in
  cache is never read aloud.
- Cache hit rate dashboard exists; an SLO threshold (e.g., ≥60% hit)
  triggers alerts when it drops.

---

## Choosing between recipes

- Start with the **consumer**: human reader → RA1 or RA4. LLM only → RA2 or RA5.
  Multi-customer SaaS → RA3. Conversational bot → RA6. Managed agent runtime →
  RA7. Multimodal workspace assistant → RA8. **One small team, one substrate,
  ops simplicity dominates → RA9. Many git repos, KB feeds many agents → RA10.
  Policies / regulator docs / control frameworks as agent context → RA11.
  Multi-agent team coordinating on a shared objective → RA12. Real-time
  voice / sub-300ms surface → RA13.**
- Then check **regulatory exposure**: if yes, RA4 absorbs whichever other recipe
  would have applied.
- Then check **review surface requirement**: if yes, promote the composition
  label to P9.
- Then run the **anti-pattern sweep** from `anti-patterns-catalog.md`.
- Only then begin implementation.
