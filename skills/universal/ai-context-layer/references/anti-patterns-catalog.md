# Anti-Patterns Catalog

## Table of Contents

- [How to use this catalog](#how-to-use-this-catalog)
- [Anti-pattern index](#anti-pattern-index)
- [A1 — Chat transcripts as memory](#a1--chat-transcripts-as-memory)
- [A2 — Vector DB as system of record](#a2--vector-db-as-system-of-record)
- [A3 — Destructive overwrite without supersession](#a3--destructive-overwrite-without-supersession)
- [A4 — Query-time contradiction detection](#a4--query-time-contradiction-detection)
- [A5 — Prompt stuffing instead of context assembly](#a5--prompt-stuffing-instead-of-context-assembly)
- [A6 — Untyped `(subject, predicate, object)` triples at scale](#a6--untyped-subject-predicate-object-triples-at-scale)
- [A7 — Hard delete instead of invalidation](#a7--hard-delete-instead-of-invalidation)
- [A8 — Monolithic personalization store](#a8--monolithic-personalization-store)
- [A9 — Graph added without proof](#a9--graph-added-without-proof)
- [A10 — No ACL / tenant scope on memory](#a10--no-acl--tenant-scope-on-memory)
- [A11 — No lifecycle verbs / no forget path](#a11--no-lifecycle-verbs--no-forget-path)
- [A12 — Cross-surface signals with no owner](#a12--cross-surface-signals-with-no-owner)
- [A13 — Provenance as optional metadata](#a13--provenance-as-optional-metadata)
- [A14 — No confidence model](#a14--no-confidence-model)
- [A15 — RAG re-run per turn instead of compiled knowledge](#a15--rag-re-run-per-turn-instead-of-compiled-knowledge)
- [A16 — Ingest without extraction pipeline](#a16--ingest-without-extraction-pipeline)
- [A17 — Review surface treated as optional for user-visible KB](#a17--review-surface-treated-as-optional-for-user-visible-kb)
- [A18 — Raw embeddings without evidence or reranking](#a18--raw-embeddings-without-evidence-or-reranking)
- [A19 — Context poisoning](#a19--context-poisoning)
- [A20 — Context distraction](#a20--context-distraction)
- [A21 — Context clash](#a21--context-clash)
- [A22 — Context confusion](#a22--context-confusion)
- [A23 — Indirect prompt injection via retrieved or remembered content](#a23--indirect-prompt-injection-via-retrieved-or-remembered-content)
- [A24 — No tool-result compaction / clearing](#a24--no-tool-result-compaction--clearing)
- [A25 — Persistent state stored in the system prompt](#a25--persistent-state-stored-in-the-system-prompt)
- [A26 — Mode-collapse loop from self-extracted "preferences"](#a26--mode-collapse-loop-from-self-extracted-preferences)
- [A27 — Eager prefetch masquerading as retrieval](#a27--eager-prefetch-masquerading-as-retrieval)
- [A28 — Hosted memory treated as canonical truth](#a28--hosted-memory-treated-as-canonical-truth)
- [A29 — Artifact payload stuffing](#a29--artifact-payload-stuffing)
- [A30 — Scope-free managed retrieval](#a30--scope-free-managed-retrieval)
- [A31 — Sleep-time pollution](#a31--sleep-time-pollution)
- [A32 — Uncoordinated multi-agent writes](#a32--uncoordinated-multi-agent-writes)
- [A33 — GraphRAG misapplied to single-hop lookups](#a33--graphrag-misapplied-to-single-hop-lookups)
- [A34 — Voice-tier memory miss](#a34--voice-tier-memory-miss)
- [A35 — Context collapse from wholesale rewrites](#a35--context-collapse-from-wholesale-rewrites)
- [A36 — Victory declaration bias](#a36--victory-declaration-bias)
- [A37 — Eager compaction](#a37--eager-compaction)
- [A38 — Stale secondary signal overrides authoritative state](#a38--stale-secondary-signal-overrides-authoritative-state)
- [A39 — Events applied by arrival time](#a39--events-applied-by-arrival-time)
- [A40 — Tombstone that does not cascade](#a40--tombstone-that-does-not-cascade)
- [A41 — Silent fallback to a weaker retrieval path](#a41--silent-fallback-to-a-weaker-retrieval-path)
- [A42 — Relation edges asserted without text evidence](#a42--relation-edges-asserted-without-text-evidence)
- [A43 — Document-level scope on mixed-scope documents](#a43--document-level-scope-on-mixed-scope-documents)
- [A44 — Missing-key collapse on upsert](#a44--missing-key-collapse-on-upsert)
- [A45 — Silent partial aggregate](#a45--silent-partial-aggregate)
- [A46 — Extraction descriptions edited without regression tests](#a46--extraction-descriptions-edited-without-regression-tests)
- [A47 — Consolidation that discards raw episodes](#a47--consolidation-that-discards-raw-episodes)
- [A48 — Memory evaluated without both baselines](#a48--memory-evaluated-without-both-baselines)
- [A49 — User claims stored as facts](#a49--user-claims-stored-as-facts)
- [Anti-pattern sweep output format](#anti-pattern-sweep-output-format)

**Purpose.** Named, numbered catalog of knowledge-base failure modes with detection
signals and replacement patterns. Every design this skill produces must pass an
explicit sweep against this list. Use alongside `patterns-catalog.md`
(for replacements) and `assets/eval/context-layer-scorecard.md` (for scoring).

## How to use this catalog

1. Read the target design (code, diagram, or prose description).
2. For each anti-pattern below, check the **signal** against the design.
3. If the signal is present, record the anti-pattern ID in the review output and
   cite the replacement pattern ID.
4. Only call a design complete when every applicable anti-pattern is either blocked
   or explicitly accepted with a written justification.

## Anti-pattern index

| ID | Name | Replacement |
|----|------|-------------|
| A1 | Chat transcripts as memory | P2 / P5 / P6 |
| A2 | Vector DB as system of record | P1 |
| A3 | Destructive overwrite without supersession | P4 |
| A4 | Query-time contradiction detection | P4 / P7 |
| A5 | Prompt stuffing instead of context assembly | Context Assembly Layer |
| A6 | Untyped `(subject, predicate, object)` triples at scale | P4 / P5 |
| A7 | Hard delete instead of invalidation | P4 |
| A8 | Monolithic personalization store | P1+P2+P8 separation |
| A9 | Graph added without proof | Remove until earned |
| A10 | No ACL / tenant scope on memory | Canonical contract + tenant isolation |
| A11 | No lifecycle verbs / no forget path | P5 four-verb API |
| A12 | Cross-surface signals with no owner | Signal-flow contract + TTL |
| A13 | Provenance as optional metadata | Episode provenance chain |
| A14 | No confidence model | P7 confidence decay |
| A15 | RAG re-run per turn instead of compiled knowledge | P7 |
| A16 | Ingest without extraction pipeline | P5 / P7 extract-then-store |
| A17 | Review surface treated as optional for user-visible KB | P9 review surface |
| A18 | Raw embeddings without evidence or reranking | P8 evidence-bearing retrieval |
| A19 | Context poisoning (errors accumulate and compound) | P4 invalidation + A13 provenance + A14 confidence |
| A20 | Context distraction (long history drowns the task) | Compaction + P11 sub-agent isolation |
| A21 | Context clash (contradictory tools / memories / instructions) | P4 ingest-time detection + per-surface allowlists |
| A22 | Context confusion (too many tools / facts) | Per-surface tool allowlists + just-in-time selection |
| A23 | Indirect prompt injection via retrieved or remembered content | Token-origin tagging + tool allowlists + refusal on missing evidence |
| A24 | No tool-result compaction / clearing | `write` runtime verb + tool-result summary recipe |
| A25 | Persistent state stored in the system prompt | `write` to memory store; reload on session start |
| A26 | Mode-collapse loop from self-extracted "preferences" | Confidence + provenance separation; never extract from assistant turns |
| A27 | Eager prefetch masquerading as retrieval | P12 pointer-first loading |
| A28 | Hosted memory treated as canonical truth | P13 managed boundary + P1 truth |
| A29 | Artifact payload stuffing | P12 typed artifact projections |
| A30 | Scope-free managed retrieval | P13 + storage-layer scope enforcement |
| A31 | Sleep-time pollution | P14 with strict consolidation rules; `inferred_by_model` flag; no confidence raise |
| A32 | Uncoordinated multi-agent writes | P16 provenance-per-write; per-agent scratch namespaces; validation gate at promotion |
| A33 | GraphRAG misapplied to single-hop lookups | P5 / P8 with a router; LazyGraphRAG as cost-conscious default |
| A34 | Voice-tier memory miss | RA13 / VoiceAgentRAG Fast Talker + Slow Thinker split; latency budget as first-class input |
| A35 | Context collapse from wholesale rewrites | P18 ACE delta-updates (Curator emits patches, not full rewrites) |
| A36 | Victory declaration bias | Verification gate at harness layer before completion-status row passes P17 schema gate |
| A37 | Eager compaction | P20 Anchored Iterative Summarization; provider-default trigger plus clear-vs-keep rule; explicit anchoring instructions |
| A38 | Stale secondary signal overrides authoritative state | P22 precedence: authority, then effective time, then arrival |
| A39 | Events applied by arrival time | Idempotency key + effective-time ordering; backfill writes history only |
| A40 | Tombstone that does not cascade | Derived-artifact lineage + cascade job + post-cascade check |
| A41 | Silent fallback to a weaker retrieval path | Index fingerprint check that fails loud; eval asserts the path used |
| A42 | Relation edges asserted without text evidence | Candidate vs asserted edges; asserted edges need an evidence span |
| A43 | Document-level scope on mixed-scope documents | P23 section-level `applies_to` |
| A44 | Missing-key collapse on upsert | Reject writes with a missing or empty key; P25 acceptance check |
| A45 | Silent partial aggregate | Aggregates report coverage and missing records (P25 read path) |
| A46 | Extraction descriptions edited without regression tests | Descriptions as versioned code with a golden extraction suite (P25, P17) |
| A47 | Consolidation that discards raw episodes | Append-only episode log; derived memory rebuildable and evidence-linked (P21, P14) |
| A48 | Memory evaluated without both baselines | No-memory and full-context baselines on the same questions (`agent-memory-benchmarks.md`) |
| A49 | User claims stored as facts | Attributed claims with speaker, time, and status; verification before promotion |

Catalog entries A19–A30 cover the **runtime / context-window** axis; A31–A37 cover sleep-time, multi-agent, retrieval-routing, and compaction failure modes; A38–A43 cover state maintenance, deletion cascade, index freshness, edge evidence, and scope; A44–A46 cover typed-memory writes, reads, and extraction drift; A47–A49 cover consolidation, evaluation, and attributed claims (audit them stage by stage with `memory-responsibilities-audit.md`). See
`references/context-hygiene.md` for the full failure taxonomy and
`references/security-threat-model.md` for the injection threat model.

---

## A1 — Chat transcripts as memory

- **Signal**: the "memory" store is a table of raw conversation turns. Retrieval is
  semantic search over turn text.
- **Why it fails**: raw turns carry noise, meta-talk, self-correction, and duplicated
  facts. Recall quality degrades as the store grows; contradictions accumulate;
  there is no stable identifier to point at a single durable fact.
- **Replacement**: P2 / P5 / P6 — extract typed facts from each episode at write time
  and store the extracted facts, not the raw turns. Keep the episode log separately
  for audit.

## A2 — Vector DB as system of record

- **Signal**: entity state (user profile, billing, org membership) is read from the
  vector index or from a cache that was populated from embeddings.
- **Why it fails**: embeddings are lossy and stale. Any drift between the operational
  store and the index produces silent wrong answers that survive until reindex.
- **Replacement**: P1 — operational truth in tools/APIs/SQL; the index holds only
  prose or derived summaries that carry a source pointer back to P1.

## A3 — Destructive overwrite without supersession

- **Signal**: memory updates look like `UPDATE fact SET value = ... WHERE id = ...`
  with no history row.
- **Why it fails**: contradictions cannot be traced, point-in-time queries are
  impossible, and reviewers cannot answer "when did we first believe X?".
- **Replacement**: P4 non-destructive invalidation — close the old row's validity
  window and insert a new row linked by `supersedes_id`.

## A4 — Query-time contradiction detection

- **Signal**: conflicts surface only when a user asks a question that happens to
  touch two contradicting facts; there is no ingest-time check.
- **Why it fails**: the knowledge layer silently accumulates contradictions until a
  query stumbles on one; the user sees inconsistent answers with no explanation.
- **Replacement**: P4 or P7 ingest-time detection using the MemPalace categories —
  **attribution** (same claim, different sources), **temporal** (new value
  invalidates the old), **stale** (fact is past its validity window).

<!-- Source: github.com/MemPalace/mempalace@6614b9b4e71e67da2236493b036b7bf42ba2d55f (MIT), cross-routed 2026-04-15 -->

## A5 — Prompt stuffing instead of context assembly

- **Signal**: a single monolithic system prompt carries every possible piece of
  context; there is no per-surface bundle, no budget, no allowlist.
- **Why it fails**: token budget blows up, latency suffers, model attention drifts,
  irrelevant facts poison answers, and you cannot explain why a given fact ended up
  in the prompt.
- **Replacement**: Context Assembly Layer with `ContextAssemblyRequest` →
  `ContextBundle`, per-surface budgets, strict allowlists, bundle IDs tied to
  feedback. See `references/context-assembly.md`.

## A6 — Untyped `(subject, predicate, object)` triples at scale

- **Signal**: graph layer is a table of freeform triples; query logic does
  string-compare on predicate names.
- **Why it fails**: renames and schema drift break queries silently; no validation
  on edge fields; no type-aware traversal; reviewer cannot trust the graph shape.
- **Replacement**: P4 / P5 typed ontology as code — entities and edges declared as
  classes with required fields, validators, and types. Extraction returns typed
  instances.

## A7 — Hard delete instead of invalidation

- **Signal**: `DELETE FROM edges WHERE ...` is the forget path. GDPR and "fix this
  fact" use the same code path.
- **Why it fails**: audit trail destroyed; as-of queries impossible; superseded
  facts look identical to facts that never existed; legitimate deletion (GDPR)
  indistinguishable from correction.
- **Replacement**: P4 — close the validity window and set `superseded_at`; reserve
  hard delete for compliance paths with a separate audited code path.

## A8 — Monolithic personalization store

- **Signal**: one table or service for profile + learned memory + retrieved docs
  + feedback events.
- **Why it fails**: operational truth mixes with derived memory and retrieval results;
  ACL enforcement is ambiguous; failures are hard to localize; migrations become
  all-or-nothing.
- **Replacement**: P1 + P2 + P8 + separate `FeedbackOutcome` store; each layer owned
  by one subsystem with a clear contract.

## A9 — Graph added without proof

- **Signal**: graph store exists in the stack; ablation (remove graph, re-run evals)
  shows no measurable change in answer quality or action quality.
- **Why it fails**: graph carries operational and maintenance cost (ingestion,
  schema drift, ACL plumbing, visualization) that no business outcome justifies.
- **Replacement**: remove the graph layer until a concrete query class is shown to
  improve with traversal versus SQL or hybrid retrieval. Add back as P4 with a
  documented ablation result.

## A10 — No ACL / tenant scope on memory

- **Signal**: `LearnedMemory` rows have no `owner_scope` field; memory is retrieved
  by entity ID alone.
- **Why it fails**: cross-tenant leakage risk; privacy incidents; compliance
  failures. For multi-tenant SaaS this is a ship-blocker.
- **Replacement**: make `owner_scope` a required canonical-contract field;
  enforce at the storage layer, not just the query layer; see
  `references/tenant-isolation-patterns.md`.

## A11 — No lifecycle verbs / no forget path

- **Signal**: memory can be added and read, but there is no `forget` and no
  `improve` path. Every historical belief accumulates.
- **Why it fails**: contradictions compound; corrections cannot be applied without
  hand-surgery on the store; reviewers cannot trust any historical fact.
- **Replacement**: P5 four-verb API — `remember / recall / forget / improve`.
  `forget` is first-class and non-destructive.

<!-- Source: github.com/topoteretes/cognee@961c3ca4784686390d89d7c45cef63ed2e8da6a1 (Apache-2.0), extracted 2026-04-15 -->

## A12 — Cross-surface signals with no owner

- **Signal**: mood, intent, or preference signals flow from one surface to another
  without a documented owner, TTL, or deletion path.
- **Why it fails**: signals go stale and are trusted anyway; privacy surface area
  grows silently; no-one can answer "why did the chat surface know I was sad?".
- **Replacement**: a Cross-Surface Signal Flow contract with explicit owner, TTL,
  confidence, and `superseded_at`. See `references/context-assembly.md` §Cross-surface
  signal flow.

## A13 — Provenance as optional metadata

- **Signal**: facts have no `source_episode_id`. "Why do you believe this?" cannot
  be answered without re-running the pipeline (and sometimes not even then).
- **Why it fails**: reviewers cannot trust facts; contradiction resolution cannot
  reach the raw evidence; re-chunking breaks every citation.
- **Replacement**: episode provenance chain — every derived fact carries the
  `source_episode_id` of the raw input it came from; the episode store holds the
  raw input verbatim.

<!-- Source: github.com/getzep/graphiti@98d8344d531aa74160f2e33b8db84c5bdc9954ba (Apache-2.0), extracted 2026-04-15 -->

## A14 — No confidence model

- **Signal**: every memory or wiki claim is treated as equally true; no decay, no
  reinforcement, no threshold for refusal.
- **Why it fails**: a six-month-old one-source observation is given the same weight
  as a recent multi-source confirmation; the model cannot self-limit.
- **Replacement**: P7 confidence model — Ebbinghaus-style decay, reset by reuse
  or new source confirmation; threshold below which the system refuses to cite.

## A15 — RAG re-run per turn instead of compiled knowledge

- **Signal**: every user question runs the same retrieve-chunk-embed loop; nothing
  accumulates; synthesis work is thrown away at the end of each turn.
- **Why it fails**: expensive (latency and cost), fragile (retrieval quality dominates
  answer quality), and wasteful when the same questions are asked repeatedly.
- **Replacement**: P7 knowledge compilation — when the consumer needs a reviewable
  or reusable asset, compile synthesis pages into the wiki; future questions hit
  the compiled page first, falling back to retrieval only for gaps.

## A16 — Ingest without extraction pipeline

- **Signal**: source documents are chunked and embedded directly into an index
  with no entity/relation/fact extraction step.
- **Why it fails**: the index only supports prose recall; typed facts stay implicit
  inside blobs; graph overlays and contradiction detection are impossible.
- **Replacement**: P5 or P7 extraction pipeline — parse source, extract typed
  entities and relations, reconcile against existing state, then index the
  derived facts alongside the prose.

## A17 — Review surface treated as optional for user-visible KB

- **Signal**: the product exposes the knowledge base to end users or operators, but
  there is no graph view, no page-level source trace, no contradiction queue, no
  way to approve/reject/supersede a fact.
- **Why it fails**: users cannot trust what they cannot inspect; operators cannot
  correct mistakes; regulated contexts fail audit; the knowledge base becomes a
  black box at exactly the moment transparency matters.
- **Replacement**: P9 mandatory Review & Inspection Layer. See
  `references/inspection-and-review-surfaces.md`.

## A18 — Raw embeddings without evidence or reranking

- **Signal**: retrieval returns top-k chunks by cosine similarity, with no source
  pointer, no freshness timestamp, no reranker, and no citation granularity.
- **Why it fails**: hallucinations cannot be traced; refusal on missing evidence is
  impossible; relevance degrades as the corpus grows because lexical precision is
  missing.
- **Replacement**: P8 — hybrid retrieval (BM25 + dense), reranker, evidence IDs,
  freshness metadata, and citation handles stable across re-indexing.

## A19 — Context poisoning

- **Signal**: multi-turn traces show the model citing facts the source of truth does
  not contain; stored memory carries statements no user or tool ever provided;
  unreinforced facts do not decay.
- **Why it fails**: a single hallucinated or wrong fact enters the window and is
  referenced on subsequent turns, compounding into a false reality the model
  treats as ground truth.
- **Replacement**: P4 non-destructive invalidation + A13 provenance + A14
  confidence. Facts carry `source_episode_id`; confidence decays without
  reinforcement; contradictions are detected at ingest, not replayed into the
  next prompt. See `references/context-hygiene.md` §F1.

## A20 — Context distraction

- **Signal**: the model repeats prior actions from history rather than synthesizing
  novel plans; long-horizon agents loop on failed tool calls; responses drift as
  session length grows.
- **Why it fails**: as context grows large, the model over-attends to stored
  history and under-attends to its training and the current task. Pokemon-playing
  Gemini observed repetition over planning past ~100K tokens. n²-attention
  dilution is the mechanism.
- **Replacement**: token-budget caps per surface + history compaction at a
  threshold + P11 sub-agent isolation for long-horizon sub-tasks. See
  `references/context-hygiene.md` §F2.

## A21 — Context clash

- **Signal**: identical-looking inputs produce oscillating behaviors; new MCP or
  tool integrations cause regressions in unrelated tasks; two memory rows disagree
  on the same fact and both appear in the bundle.
- **Why it fails**: the model is forced to reconcile contradictions at generation
  time. It often silently blends them or picks the most recent.
- **Replacement**: P4 ingest-time contradiction detection + per-surface tool
  allowlists + deterministic context ordering (stable → volatile for KV-cache).
  Vet new tool descriptions on registration. See `references/context-hygiene.md`
  §F3.

## A22 — Context confusion

- **Signal**: model picks the wrong tool when many are available; irrelevant
  memories or retrieval results crowd the bundle; small models fail past ~30
  tools (Llama-3.1-8B: 46 tools fail, 19 tools succeed).
- **Why it fails**: too many options or too many irrelevant facts dilute the
  signal. The model cannot identify what is load-bearing.
- **Replacement**: per-surface tool allowlists tuned to the surface's real jobs +
  just-in-time selection (not prompt-stuffing, A5) + retrieval reranking before
  injection (not A18). See `references/context-hygiene.md` §F4.

## A23 — Indirect prompt injection via retrieved or remembered content

- **Signal**: the system prompt does not distinguish instruction tokens from data
  tokens; retrieved chunks are concatenated into the prompt without origin tags;
  tool descriptions from external MCP servers are trusted the same as the app's
  own system prompt; no adversarial corpus runs in evals.
- **Why it fails**: an attacker who reaches any ingest path (public docs, ticket
  bodies, product reviews, webhook payloads, MCP descriptions) can embed an
  instruction the model will follow. PoisonedRAG (arXiv 2402.07867) reports that a few
  injected texts per target question usually steer the answer in the authors' setup; the 2024 ChatGPT "spAIware" disclosure showed
  memory-persisted exploits across sessions.
- **Replacement**: token-origin tagging in the system prompt + per-surface tool
  allowlists + refusal on missing evidence + classifier-based sanitization on
  high-risk ingest paths + adversarial corpus in evals. Destructive operations
  re-prompt from P1 operational truth, not from memory or retrieval. See
  `references/security-threat-model.md`.

## A24 — No tool-result compaction / clearing

- **Signal**: tool outputs remain in the window for the rest of the session at
  full size; token budget grows monotonically with every tool call; an agent with
  five tool calls of 5K tokens each carries 25K of tool output into every later
  turn.
- **Why it fails**: tool results are the most common driver of window bloat in
  agent loops. Most of a tool result is irrelevant after the agent has acted on
  it. Keeping it inflates cost, latency, and F2 distraction risk.
- **Replacement**: the `write` runtime verb — replace a consumed tool result with
  a short model-written summary (or a structured projection of the fields used)
  and keep the full result in the episode log for re-fetch. Cap tool-result
  payload size at the tool boundary. See `references/context-hygiene.md` §Tool-result
  pressure.

## A25 — Persistent state stored in the system prompt

- **Signal**: durable facts the agent must "remember across sessions" (user
  preferences, last topic, project state, prior decisions) live in the system
  prompt or in a hand-edited preamble. Resetting the session loses them; growing
  them eats context budget every turn.
- **Why it fails**: the system prompt is a fixed cost paid on every turn and a
  hard ceiling on the model's working memory. State stored there cannot be
  invalidated, scoped per surface, audited, or forgotten — it is just text the
  user cannot see and the agent cannot edit. As the prompt grows, F2 distraction
  and context rot arrive sooner.
- **Replacement**: the `write` runtime verb plus the storage layer. Persist
  durable state in the memory store (P2/P5/P6) with provenance and lifecycle
  verbs; on session start, `select` only the slice the surface needs. The system
  prompt holds *role and policy*, not *state*.

<!-- Source: paxrel.com/blog-ai-agent-prompts (2026), intuitionlabs.ai/articles/what-is-context-engineering -->

## A26 — Mode-collapse loop from self-extracted "preferences"

- **Signal**: the memory layer extracts "user preferences" from any turn,
  including the assistant's own outputs. Over time, near-duplicate preferences
  accumulate ("user likes concise answers", "user prefers brief responses", "user
  wants short replies"), and the agent's responses converge on a single style
  regardless of input.
- **Why it fails**: extracting from the assistant's own outputs creates a
  feedback loop — the model's habits become the user's "preferences" become the
  model's next prompt. Diversity collapses, real user signal is drowned by
  inferred signal, and corrections get acknowledged then silently re-violated.
- **Replacement**: distinguish *user-stated* from *model-inferred* preferences at
  storage time using A13 provenance and A14 confidence. Never extract memories
  from assistant turns unless the user explicitly confirmed them in the next
  turn. Decay unreinforced inferred preferences faster than user-stated ones.
  Sample the memory store periodically for self-similarity (`inspection-and-review-surfaces.md`).
- **Maps to.** `context-hygiene.md` §Mode collapse.

## A27 — Eager prefetch masquerading as retrieval

- **Signal**: the runtime loads every candidate document, file, screenshot, or
  tool payload into the bundle "just in case", then calls that retrieval.
- **Why it fails**: bundle size and latency grow with corpus size, not task
  need. The surface loses determinism, F2 distraction arrives sooner, and the
  system cannot explain why a given artifact entered the window.
- **Replacement**: P12 pointer-first loading — keep refs in the request, resolve
  only the refs the current surface needs, and load artifacts only after
  selection.

## A28 — Hosted memory treated as canonical truth

- **Signal**: a managed memory product stores account, entitlement, or profile
  state and the app reads it back as if it were the system of record.
- **Why it fails**: provider state may lag, reshape, or delete differently from
  the product systems that actually own the truth. Audits and DSAR/delete paths
  become unclear, and provider outages become truth outages.
- **Replacement**: P13 managed boundary + P1. Hosted memory may accelerate
  retrieval or recall, but operational truth remains app-owned and live.

## A29 — Artifact payload stuffing

- **Signal**: raw PDFs, screenshots, OCR dumps, HTML pages, or large tool
  results are injected into the bundle wholesale, often with base64 or verbose
  JSON still attached.
- **Why it fails**: cost and distraction spike, raw payloads crowd out signal,
  and provenance often gets lost during ad hoc truncation. Multimodal tasks turn
  into prompt-stuffing under a different name.
- **Replacement**: P12 typed projections over `LoadedArtifact` — keep refs,
  project text excerpts and metadata, and preserve `source_ref_id` /
  `evidence_id`.

## A30 — Scope-free managed retrieval

- **Signal**: the app queries a managed retrieval or memory service without
  tenant/user scope in the request, then filters results after they come back.
- **Why it fails**: the provider has already done work on a broader population,
  leakage becomes a configuration accident, and audit logs no longer prove scope
  was enforced at the retrieval boundary.
- **Replacement**: P13 boundary discipline — owner scope is required before the
  managed request is issued, and app-side audit logs record the scoped request.

## A31 — Sleep-time pollution

- **Signal**: the consolidation pass (P14) merges, rewrites, or invents
  memory rows from the agent's own outputs without provenance, raising
  confidence of self-asserted "preferences" the user never stated.
- **Why it fails**: this is A26 (mode collapse) on a schedule. Each
  consolidation run flattens nuance and reinforces stylistic regression;
  user-stated facts and model-inferred facts blur in the same rows.
- **Replacement**: P14 with strict rules — consolidation reads, never
  fabricates; merges require ≥2 source episodes; `inferred_by_model` flag
  preserved; confidence cannot be raised by consolidation, only lowered
  (decay) or held. Re-run `mode_collapse` evals after each consolidation
  cadence change. When consolidation derives a cross-episode pattern, write
  it as a P21 evidence-linked observation, not a free-floating rewritten
  note.

## A32 — Uncoordinated multi-agent writes

- **Signal**: multiple agents share a memory/blackboard layer, each writes
  freely, and downstream agents read the result as ground truth without
  knowing which agent wrote it or why. One agent's hallucinated claim
  propagates to the rest of the team.
- **Why it fails**: shared memory without provenance is a global confused
  deputy. The error becomes indistinguishable from validated knowledge;
  blame-assignment is impossible after the fact.
- **Replacement**: P16 boundary discipline — provenance per write
  (`writer_agent`, `role`, `source_episode_id`, `confidence`); per-agent
  scratch namespaces with a `promote` gate to shared namespaces; validation
  sweep at promotion (schema, contradiction, confidence floor).

## A33 — GraphRAG misapplied to single-hop lookups

- **Signal**: every retrieval path goes through the knowledge graph,
  including questions a vector or BM25 lookup would answer in one hop.
  Latency and cost balloon; recall on simple lookups *drops* compared to
  plain RAG.
- **Why it fails**: the GraphRAG-Bench result (arXiv 2506.02404) is public —
  graph retrieval tends to help on multi-hop, cross-document questions and
  not on single-hop lookups (direction only: the paper states no point gain,
  and arXiv 2506.05690 reports GraphRAG frequently underperforming vanilla RAG
  on real-world tasks). Forcing graph traversal where embeddings already
  match wastes tokens and adds failure surface.
- **Replacement**: P5 / P8 with a router — entity-recognition step decides
  whether the question needs traversal (multi-hop, cross-reference) or
  flat retrieval (single-hop). LazyGraphRAG (deferred community
  summarization, which its authors report as far cheaper to index than full GraphRAG) is the cost-
  conscious default when graph indexing cost matters; reserve full
  GraphRAG for narrative/multi-hop paths.

## A34 — Voice-tier memory miss

- **Signal**: a voice agent runs the same memory + retrieval path as a
  chat agent — synchronous embedding lookup on every turn — and overshoots
  the 200–300ms human-conversation latency window. Users perceive lag,
  drop-off climbs, the surface feels broken.
- **Why it fails**: voice has a hard latency budget that chat does not.
  Memory architecture optimized for recall depth is fatal for voice.
- **Replacement**: voice-tier memory split (RA13 / VoiceAgentRAG pattern).
  Foreground "Fast Talker" with sub-millisecond cache lookups and a tight
  per-user memory hot set; background "Slow Thinker" pre-fetches and
  consolidates predictively. Latency budget is a first-class input to
  bundle assembly, not an afterthought.

## A35 — Context collapse from wholesale rewrites

- **Signal**: an evolving playbook, memory store, or instruction context
  starts rich and detailed but, after N consolidation or compaction cycles,
  converges to terse generic summaries. Rare-but-important strategies that
  helped on edge cases disappear. New trajectories regress on those edge
  cases without an obvious code change.
- **Why it fails**: every consolidation step regenerates the whole context
  instead of emitting a delta. Each regeneration is a lossy compression of
  the previous regeneration. Detail decays geometrically. Distinct from A26
  (mode collapse of *output* distribution) — A35 is collapse of the *stored
  context* distribution.
- **Replacement**: P18 ACE — the Curator emits **delta updates** (new
  bullets, edits to existing bullets, supersession of stale ones), never
  whole-context rewrites. Every emission is a small patch the playbook can
  accept, reject, or supersede. Source: Zhang et al. arXiv:2510.04618 (the
  paper names this exact failure mode and the delta-update defense).

## A36 — Victory declaration bias

- **Signal**: an agent marks a task complete, writes a "done" memory row, or
  closes a todo without producing or referencing verification evidence.
  Downstream readers (humans, follow-up agents) trust the "done" status; the
  underlying work was never actually verified. Failures surface much later,
  often as an angry user or a regression test that catches what the agent
  should have.
- **Why it fails**: this is a harness-level failure (P19 column 2:
  verification loops), but it leaks into the context layer because the
  "done" status gets persisted to memory and contaminates future retrievals
  with false-positive completion claims.
- **Replacement**: verification gate at the harness layer (cite an artifact,
  pass a test, link to a passing CI run) *before* a completion-status row
  passes the P17 schema gate into derived memory. If verification evidence
  is absent, downgrade `status: complete` to `status: claimed_complete`
  with `confidence < 0.5` and route to a review queue. Source: Faros AI
  harness-engineering 2026 deep dive; coding-behavior rule 12 (Fail loud).

## A37 — Eager compaction

- **Signal**: an agent compacts its context aggressively (low trigger
  threshold, short summary target, no anchoring) "to save tokens". Token
  cost drops but task quality drops harder — the summary loses open-thread
  references, decision IDs, or file paths that the next step needed.
  Downstream re-asks for context that should have survived compaction.
- **Why it fails**: compaction is lossy by definition; aggressive compaction
  with no anchoring rule destroys the references downstream steps depend on.
  The trigger fires before the conversation has accumulated enough signal
  to compress well. The "summary" is shorter than the things being
  summarized, but more important things are missing than present.
- **Replacement**: P20 Anchored Iterative Summarization — every summary line
  carries durable IDs (file paths, decision IDs, todo IDs, ticket numbers)
  so the next step can re-resolve any artifact. Start the trigger at
  the provider's documented default (look it up; do not use the minimum)
  unless you have measured a reason to compact earlier, and apply the
  clear-vs-keep rule in [context-hygiene.md](context-hygiene.md#context-mutation-economics)
  plus the recall probe in [Compaction verification](context-hygiene.md#compaction-verification). Override the default `instructions` to enforce
  anchoring explicitly. Source: Anthropic *context engineering* cookbook;
  Jason Liu *Two Experiments on Agent Compaction* (2025).

## A38 — Stale secondary signal overrides authoritative state

- **Signal**: state is last-writer-wins across sources. A chat channel topic,
  a cached summary, or a stale index row rewrites "owner" or "limit" after
  the system of record already changed it.
- **Why it fails**: arrival time is not authority. The most recently
  processed source is often the least authoritative one (a summary written
  from yesterday's state, a backfilled snapshot).
- **Replacement**: P22 precedence — authority rank, then effective time,
  then arrival. A lower-authority source only creates a candidate change
  that is verified against the system of record or routed to review. The
  source-trust hierarchy lives in `entity-and-memory-models.md`.

## A39 — Events applied by arrival time

- **Signal**: the state reducer applies events in consumption order with no
  idempotency key. A redelivered event applies twice; a historical snapshot
  backfilled after the fact overwrites the current value.
- **Why it fails**: at-least-once delivery and backfills are normal, so the
  final state depends on queue timing. As-of answers become irreproducible.
- **Replacement**: dedupe on `event_id` (or `content_hash`); order by effective
  time (`valid_from`); a backfill closes and inserts history intervals and
  never replaces a value with a later `valid_from`. Check: replaying the
  stream shuffled and with duplicates yields identical final and as-of state
  (`builds/evals/suites/state_maintenance`).

## A40 — Tombstone that does not cascade

- **Signal**: a source is deleted or superseded and its registry row is
  tombstoned, but the full-text index, vector index, graph nodes and edges,
  compiled pages, or P21 observations still serve it. Related symptoms:
  `superseded_by` pointing at itself, or supersession cycles.
- **Why it fails**: each derived store has its own rebuild cadence, so a
  retired document keeps answering questions until the slowest one rebuilds.
- **Replacement**: every derived artifact records the source IDs it came
  from; a cascade job invalidates dependants on tombstone; a post-cascade
  check fails when any live derived artifact references a tombstoned source;
  a lint rejects self-pointers and cycles in supersession chains.

## A41 — Silent fallback to a weaker retrieval path

- **Signal**: when the index is missing or its fingerprint no longer matches
  (schema, tokenizer, or query-code change), the retriever quietly falls back
  to an in-memory, lexical-only, or brute-force path. Evals keep passing on a
  path production does not use, or production degrades with no alert.
- **Why it fails**: in one in-house knowledge base, editing the query code
  changed the index fingerprint and the eval silently ran on the fallback
  path, so the scores described a different system.
- **Replacement**: a fingerprint check that fails loud (or returns an
  explicit `degraded` flag in every result); the eval report records and
  asserts the path used; a freshness gate before serving.

## A42 — Relation edges asserted without text evidence

- **Signal**: graph edges (`implements`, `depends_on`, `owns`) are created
  from co-mention, title similarity, or an unverified model guess and then
  counted and traversed as fact.
- **Why it fails**: edge counts and coverage reports overstate the real
  relationships, and traversal answers inherit the guess.
- **Replacement**: two tiers. `candidate_*` edges carry `basis`, `mentions`,
  and `confidence` and are excluded from answers and counts by default;
  asserted edges require an evidence span (P22 provenance fields) or a
  structural source (code import, registry field, human approval). Check:
  every asserted edge resolves a live evidence span.

## A43 — Document-level scope on mixed-scope documents

- **Signal**: `applies_to` or entity scope is tagged once per document, and
  the document contains per-entity addenda, schedules, or annexes.
- **Why it fails**: one entity's addendum (a different limit, a local
  exception) is served as if it applied to every entity the document
  covers. The text is retrieved correctly; the scope is wrong, so the answer
  is confidently wrong.
- **Replacement**: P23 section-level scope, plus cross-scope hard negatives in
  the eval.

## A44 — Missing-key collapse on upsert

- **Signal**: a typed store upserts on a natural key (name, email, external
  ID) and the extractor may leave the key empty. Distinct people or orders
  end up as one record whose fields flip with each write.
- **Why it fails**: an empty key matches every other empty key, so repeated
  writes collapse onto the same record and overwrite it. At least one
  schema-first engine documents this behaviour. The output looks valid; only
  the record count gives it away.
- **Replacement**: reject or quarantine any write whose key fields are
  missing or empty; never default a key to an empty string; use a surrogate
  ID plus a candidate-match step when the natural key is unknown. Check (P25):
  two writes missing the key never merge.

## A45 — Silent partial aggregate

- **Signal**: "how many", "total", or "which is largest" is answered from a
  scoped or filtered read, and the answer carries no coverage information.
- **Why it fails**: the aggregate is computed over what the read found. When
  records are out of scope, unextracted, or still in the async queue, the
  number is wrong and nothing in the response says so. One schema-first
  engine documents exactly this for scoped reads.
- **Replacement**: every aggregate returns its coverage (records included,
  records expected or excluded, and why); the agent states partial coverage
  in its answer; the P25 acceptance check plants a missing record and
  expects a flag.

## A46 — Extraction descriptions edited without regression tests

- **Signal**: field descriptions, extraction prompts, or schema docstrings
  are edited in place (often in a dashboard) with no versioning and no
  extraction test run.
- **Why it fails**: in schema-first memory the description is the extraction
  policy. A wording change shifts what gets stored for every later write, and
  the regression shows up weeks later as a retrieval bug. The same drift
  happens when the extraction model changes under an unchanged description.
- **Replacement**: descriptions live in version control beside the schema; a
  golden set of input-to-record cases runs on every description, schema, or
  model change; the diff of extracted records is reviewed like a code diff
  (P25, P17).

## A47 — Consolidation that discards raw episodes

- **Signal**: a consolidation, summarisation, or dream pass replaces the
  episodes it read, and nothing can regenerate memory from the original
  inputs.
- **Why it fails**: each rewrite loses detail, and errors compound across
  cycles. A study of iterative consolidation (arXiv 2605.12978) reports
  utility rising, then falling below the no-memory baseline, while an
  episodic-only control stays competitive. Erasure, audit, and re-extraction
  with a better model all need the originals. This is not A1 in reverse: the
  episodes are the rebuild source and provenance, not the retrieval
  interface.
- **Replacement**: an append-only episode log with retention set by policy;
  every derived fact, summary, or observation links its source episodes
  (P21); consolidation writes new versions instead of overwriting (P14); a
  drift eval reruns after N cycles.

## A48 — Memory evaluated without both baselines

- **Signal**: a memory layer is reported as an improvement with no
  no-memory baseline, no full-context baseline, or neither.
- **Why it fails**: without the no-memory baseline you cannot tell whether
  memory helps; without full context you cannot tell whether the layer beats
  simply sending the history. Memory papers have reported full context at or
  above memory on accuracy when the history fits the window, which makes
  the real win cost and latency.
- **Replacement**: run both baselines on the same questions with the same
  answering model and judge; report accuracy with intervals, plus cost and
  latency; rerun after model upgrades
  ([agent-memory-benchmarks](agent-memory-benchmarks.md#rules-before-you-trust-a-memory-number)).

## A49 — User claims stored as facts

- **Signal**: "I'm the account owner", "my doctor said X", or "the deadline
  moved to Friday" is stored as `fact: X` with no speaker, time, or status.
  Later sessions treat it as ground truth.
- **Why it fails**: persisted claims amplify sycophancy: the agent agrees with
  what it was told and then cites its own memory as confirmation.
  Personalisation-risk benchmarks (PASB, arXiv 2607.10526; PersistBench,
  arXiv 2602.01146) report this direction, and PASB reports agents rewriting
  claims as stable facts during consolidation. Claims about identity or
  authority also become an escalation path (T4, T8).
- **Replacement**: store a claim as `{speaker, claimed_at, statement,
  status: asserted | verified | contradicted, verified_by}`; render it as
  "the user said ..." in context; promote to fact only through a verifying
  tool or authoritative source (P22); consolidation must preserve
  attribution; never derive permissions from a claim.

## Anti-pattern sweep output format

When this catalog is applied to a design, emit a block like:

```text
ANTI-PATTERN SWEEP:
- A1 Chat transcripts as memory — BLOCKED by P2 extraction at ingest
- A4 Query-time contradiction detection — BLOCKED by P4 ingest-time check
- A17 Review surface optional — NOT BLOCKED (accepted: internal-only, 1 user)
- A14 No confidence model — BLOCKED by P7 confidence decay
```

Every applicable anti-pattern must be either `BLOCKED by <pattern ID>` or
`NOT BLOCKED (accepted: <written justification>)`. Silent omissions are not allowed.
