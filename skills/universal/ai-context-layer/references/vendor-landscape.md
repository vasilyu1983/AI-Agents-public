# Vendor Landscape

## Table of Contents

- [Agent-memory engines by representation and output](#agent-memory-engines-by-representation-and-output)
- [Choose, avoid, and the gotcha to test first](#choose-avoid-and-the-gotcha-to-test-first)
- [Engine notes](#engine-notes)
- [Platform memory](#platform-memory)
- [Other frameworks](#other-frameworks)
- [Storage substrates databases agents are built on](#storage-substrates-databases-agents-are-built-on)
- [Reading vendor memory benchmarks](#reading-vendor-memory-benchmarks)
- [What to take from the matrix](#what-to-take-from-the-matrix)
- [Routing rules by problem shape](#routing-rules-by-problem-shape)
- [Before citing a row](#before-citing-a-row)

<!-- as_of: 2026-10-02 (engine, platform and substrate-caveat rows re-verified against primary sources; "Other frameworks" rows not re-verified) -->
<!-- review_cadence: 30d -->

**Purpose.** Decision matrix for the engines, platform memory services, and
databases in the agent-memory space. It holds judgment, not release news:
licences, plans, limits, and retention windows live in `data/sources.json`
with a `last_verified` date. Patterns are in `patterns-catalog.md`; the
stage-by-stage audit is [memory-responsibilities-audit](memory-responsibilities-audit.md).

## Agent-memory engines by representation and output

Position an engine on two axes before comparing features. **Representation**:
text, notes, or episodes → linked facts → typed entities and relations.
**Output**: broad context → selected context → synthesised answers. The
responsibility numbers are the stages in the audit (1 admission, 2 encoding,
3 persistence, 4 maintenance, 5 retrieval, 6 post-retrieval, 7
materialisation). A number is listed only when the vendor's own docs, repo,
or paper describe it; a missing number is unverified, not absent. "Left to
you" names what the docs leave to your configuration or do not document.

| Engine | Representation × output | Native (documented) | Left to you | Time model | Provenance |
|---|---|---|---|---|---|
| Hindsight | Episodes + facts + entities, plus observation and mental-model memories × selected (`recall`) or synthesised (`reflect`) | 1 2 3 4 5 6 | Output shape; TTL not documented (deleting a memory cascades to the observations derived from it) | Temporal data extracted; an explicit valid-time model is not documented | Each observation points at supporting memories with quotes and a proof count (P21) |
| Honcho | Messages per peer and session + derived conclusions × synthesised answers, optionally schema-shaped | 1 2 5 6 7 | Storage engine; contradiction, forgetting, and consolidation rules | Not documented | Chat returns the evidence it consulted; conclusion-to-message links not documented |
| xmemory | Typed objects and relations from a declared schema × structured rows or objects, or a synthesised answer; generated SQL inspectable | 1 2 3 4 5 6 7 | Time and history, contradiction policy, TTL and decay, record-to-source provenance, fuzzy recall | No history or as-of read; model time in the schema | Field-level diff on every write; a source link exists only if you model it |
| Supermemory | Linked facts per entity + document chunks × profile block plus hybrid search results | 1 2 3 4 5 | Reranking and structured output not documented; source linkage | Temporary facts expire and conflicts resolve toward the newer fact | Not stated |
| Claude-Mem | Tool-use observations + model-written summaries × selected context by progressive disclosure (index → timeline → fetch by ID) | 1 2 3 5 | Reconciliation, decay, reranking | None | Observation IDs; summaries are model-written |
| LangMem | Text memories in semantic and episodic collections over a LangGraph store × selected (similarity) | 1 2 3 4 5 | Extraction schemas, consolidation rules, assembly | None | Not documented |
| Letta | Memory as a git-backed file tree (MemFS) pinned to the prompt + archival history × broad context plus retrieval tools | 1 3 4 5 | Encoding and reconciliation rules (background "dreaming" subagents run the passes; what they reconcile is prompt-defined) | None | Edit history only: every memory edit is a git commit; no per-fact evidence pointers documented |
| Mem0 | Linked facts + entity store (graph memory on the managed platform) × selected ranked memories, no synthesis | 1 2 3 5 6 7 | Context assembly; forgetting; graph features in the open-source build | Temporal scoring; no validity intervals | Not documented |
| Zep | Typed entities and relations + episodes (managed temporal graph) × curated context block, plus low-level graph search | 1 2 4 5 7 | Storage and residency are the vendor's; source-authority policy | Validity windows; invalidation time stored on the edge | Source episodes for each fact |
| Graphiti | Typed entities and relations + episodes, prescribed or learned ontology × selected facts and entities | 1 2 3 4 5 6 | Consolidation, context assembly, source-authority policy | Bi-temporal: valid time and ingestion time; invalidate, never delete (P4) | Every entity and edge traces to episodes |
| Cognee | Typed graph + chunks over graph, vector, and relational stores × rows from retrieval modes or text from completion modes | 1 2 3 5 6 7 | Contradiction handling, forgetting, decay | A temporal search mode; valid-time facts not documented | Not documented |
| Microsoft GraphRAG | Text units + entities + community reports × synthesised answers from graph context | 2 5 6 | Admission (batch indexing only), reconciliation, forgetting | None | Community-report source links not documented |

How to use it:

- **Pick the output first.** A machine consumer that needs fields and evidence
  wants selected context or structured rows. A synthesised answer moves
  interpretation inside the engine, so you then need a citation-support check.
- **Check maintenance on your own data** with the categories in
  [evals-and-operations](evals-and-operations.md#state-maintenance-eval)
  before trusting a vendor claim. Free-floating rewrites (A31, A35) and
  arrival-order updates (A39) are the common gaps.
- **Your domain configuration stays yours**: source precedence (P22), section
  scope (P23), sensitivity filtering (P24), the schema and its descriptions
  (P25), and the acceptance tests. Confirm the engine enforces scope at
  retrieval time, not after it.

## Choose, avoid, and the gotcha to test first

"Documented" gotchas come from the vendor's docs, repo, or paper. "Inferred"
ones follow from what the docs leave out; test them before adoption.

| Engine | Choose when | Avoid when | Gotcha to test first |
|---|---|---|---|
| Hindsight | Self-hosted memory where consolidated beliefs must stay auditable against their evidence | TTL guarantees are a launch requirement, or erasure must be proven beyond the documented cascade and you cannot test it | Documented: deleting a memory cascades to derived observations and re-queues their other sources. Inferred: check mental models, exports, and backups too; plant and erase a sentinel fact |
| Honcho | Modelling users or agents as peers and asking questions about them | You need exact state, typed fields, or aggregates | Inferred: conclusions are derived in the background, so a fact from the last few turns may not be there yet; keep the transcript in context |
| xmemory | Exact, aggregative, or stateful questions over a domain you can enumerate | Open-ended recall, paraphrase-heavy or multilingual search, native as-of history required, or regulated data without published residency and subprocessor terms | Documented: writes that omit primary-key values collapse onto one record (A44); scoped aggregates silently skip missing records (A45) |
| Supermemory | User-profile memory plus document RAG behind one API, with source connectors | You must explain why a fact changed | Inferred: "the newer fact wins" breaks when an old document is backfilled (A39) |
| Claude-Mem | Zero-config session memory for one developer's coding agent | Team-shared truth or a state store | Documented: hooks capture tool observations automatically, and anything not wrapped in its private-exclusion tag is stored. Inferred: no reconciliation of stale observations is documented |
| LangMem | You already run LangGraph and want primitives | You want documented reconciliation out of the box | Documented by LangGraph: a single profile document becomes error-prone as it grows; collections raise recall but models over-insert or over-update |
| Letta | A stateful agent runtime whose agent and background dreaming subagents edit a git-versioned memory tree ([crosswalk](memory-stack-crosswalk.md)) | The model's tool calling is weak, or writes need provenance | Documented in the MemGPT paper (arXiv 2310.08560): performance degraded with a weaker function-calling model; inferred: self-edited memory writes inherit that weakness |
| Mem0 | Simple add-and-search fact memory across user, session, and agent scopes | You need synthesis, validity intervals, or platform-only features in the open-source build | Documented in its own paper (arXiv 2504.19413): in the authors' LoCoMo setup the full-context baseline scored highest; the memory win was latency and tokens |
| Zep | A managed temporal graph that returns ready-to-inject context | You must own storage, residency, or the extraction prompts | Documented in its paper (arXiv 2501.13956): invalidation favours the most recently ingested information, and assistant-side recall regressed against full context in the authors' setup |
| Graphiti | A self-hosted bi-temporal graph with episode provenance | Workloads are single-hop lookups (A33) | Same ingestion-order invalidation as Zep; the repo marks the Kuzu backend deprecated |
| Cognee | A document-to-graph pipeline with many search modes | You need documented contradiction or forgetting behaviour | Inferred: completion modes return LLM text; use a retrieval-only mode when a machine consumer needs rows and evidence |
| Microsoft GraphRAG | Static-corpus global or theme questions | An agent-memory write and maintain loop | Documented: the repo states maintenance mode; HippoRAG 2 (arXiv 2502.14802) reports structure-augmented methods, GraphRAG among them, below standard RAG on simple factual QA |

## Engine notes

**xmemory (schema-first typed memory).** The developer declares a schema of
typed objects and relations; field descriptions are the extraction policy
(vocabulary, what to exclude, how to normalise). An LLM pipeline extracts
natural-language writes into those types; deterministic mutations bypass the
model; scoped writes either reject or drop-and-report out-of-scope changes;
every write returns a field-level diff. Reads translate a question to SQL over
the instance's tables, and composite questions share one snapshot; log the
generated SQL, because a wrong join (task owner vs incident owner) is visible
only there. No vector path is documented, so paraphrase relies on SQL
generation alone. Time is something you model: the API reference documents no
history, version list, or as-of read, and no event-time guard, so an older
fact written later overwrites the newer one unless the schema carries an
effective date and the description forbids the overwrite. The API reference
also lists no backfill of new fields and no migration rollback; a blog post
claims both, so treat the reference as authoritative. Maturity: closed
engine with open clients, beta-stage, deployment and compliance terms
recorded in `data/sources.json`. The pattern itself (P25) is reproducible
on your own Postgres with the acceptance checks listed there.

**Zep and Graphiti: ingestion order is a policy, not a law.** Their
invalidation sets the old edge's end to the new edge's start and favours the
new information (documented, arXiv 2501.13956). Inferred, not documented: when
you backfill historical documents, an imported old fact may close a newer one.
Test it first by planting an out-of-order backfill on the installed version. Reconcile by valid time or source authority
(P22), and include an out-of-order backfill case in the state-maintenance
eval.

**Mem0: run the full-context baseline.** Its paper's own table puts
full-context above Mem0 on LoCoMo; the memory's advantage was latency and
cost. That is the general rule for every engine: report accuracy against a
no-memory and a full-context baseline, plus cost and latency, before calling
memory a win ([agent-memory-benchmarks](agent-memory-benchmarks.md)).

## Platform memory

Every platform separates short-term memory (thread, session, events) from
long-term memory (store, records, bank). Two facts hold everywhere: the caller
supplies the scope, and managed extraction runs asynchronously, so a fact from
the last few turns may not be retrievable yet. Retention windows and size
limits are in `data/sources.json`.

| Platform | Write path | Scope | Consolidation | Expiry and erasure surface | Gotcha |
|---|---|---|---|---|---|
| Anthropic memory tool | Model tool calls (view, create, str_replace, insert, delete, rename) that your handler executes | None built in; you map paths per user or tenant | None; the model self-curates | Yours: TTL, delete, audit | Path traversal is documented; canonicalise and check containment. Boundary rules: [managed-memory-boundaries](managed-memory-boundaries.md) Case 2 |
| Claude Managed Agents memory stores | Agent file writes to a mounted directory, plus REST | Workspace store; a store per user; read-only mounts enforced at the filesystem | Dreams write a new, reorganised store; the input is never modified | Immutable versions kept for a fixed window; a redact endpoint | The docs warn that a successful injection can write content later sessions read as trusted memory |
| OpenAI Agents SDK sessions | The runner appends items to a session after each run; transcript memory, not extracted facts | A session ID string only | Optional compaction wrapper that rewrites history | `clear_session`, `pop_item`; TTL through the encrypted or Dapr session | The docs: a session ID does not authenticate a user; the SQLite backend does not detect external edits or replay |
| OpenAI Conversations API | Server-managed conversation objects, usable as a session backend | Conversation ID | Not verified | Not verified | Read the conversation-state guide before designing erasure around it |
| ChatGPT memory | Consumer feature; no developer API found | Per account | Not verified | User-facing delete | Out of scope for app architecture |
| LangGraph store | Hot path (a tool or node) or background job | Namespace tuple plus key; prefix search | You define it (profile patch vs collection) | `delete`; TTL through the hosted server config, or the open-source `AsyncPostgresStore(ttl=…)` with its TTL sweeper | Profile vs collection is the decision; see the LangMem row |
| AWS Bedrock AgentCore Memory | App `CreateEvent` (immutable events); async strategies extract long-term records | `actorId` / `sessionId` plus hierarchical namespaces; IAM namespace condition keys | Built-in semantic, summary, preference, and episodic strategies, overridable or self-managed | Event expiry covers short-term events only; long-term records need explicit deletion | End namespaces with a trailing slash; the docs say it prevents tenant prefix collisions |
| Vertex AI Memory Bank | Managed extraction from events, or direct create and update | Scope dict, exact match; IAM conditions on scope | Merge on write: created, updated, or deleted when contradicted | Configurable TTL; immutable revisions with rollback, which have their own retention | The docs: assume some sensitive or personal information may still be stored |

## Other frameworks

Not re-verified in the 2026-10-02 review; check the repo before relying on a row.

| Framework | Primary | Storage | Best fit |
|---|---|---|---|
| MemPalace | P4 + P10 | SQLite | Sovereign, local-first deployments |
| Redis agent memory server | P2 + P6 | Redis | The open-source server now sits in an unmaintained directory and the repo points at a managed product; use Redis for TTL-bound session state, not as the only durable store |
| LlamaIndex Property Graph | P4 (partial) | Graph + vector | Graph-backed retrieval inside LlamaIndex apps |
| llm-wiki-agent | P7 | Markdown files + graph | Open-source LLM Wiki reference |
| obsidian-wiki | P7 | Obsidian vault + graph overlay | Obsidian-native LLM Wiki |
| Cloudflare Agent Memory | P2 + P13 | Durable Objects | MCP-native memory profiles shared across agents; check release status first |

## Storage substrates (databases agents are built on)

Picking the substrate is often the more durable decision than picking the
framework. The caveat column is what breaks memory workloads specifically;
performance claims are not kept here.

| Substrate | Primary | Memory fit | Memory caveat |
|---|---|---|---|
| Postgres + pgvector | P1/P2/P8 | All layers in one ACID store | Under HNSW, filters apply after the ANN scan, so a selective tenant filter can return few or no rows; use iterative scans, partial indexes, or partitioning. Postgres full-text ranking uses no corpus-wide statistics, so it is not BM25 |
| Supabase | P1/P2/P8 | Postgres memory with RLS | Table owners skip RLS unless it is forced; superusers and `BYPASSRLS` roles always skip it. Connect the agent as a non-owner role with neither attribute |
| MongoDB Atlas | P2/P8 | Documents + vector + checkpointer | In-database embedding ties the model to the index ([managed-memory-boundaries](managed-memory-boundaries.md) Case 1) |
| Redis | P2 (short-term) + P6 | Session state, caches | Treat a semantic cache as a cross-user channel unless its key includes tenant, user, and permission scope; its similarity threshold needs tuning per workload |
| Neo4j / FalkorDB | P4 | Graphiti backends | FalkorDB is SSPL-licensed; Kuzu is archived, so do not start new work on it |
| Qdrant | P8 | Collections with payload filters | Use the tenant payload index for multi-tenancy; corpus statistics are shared across tenants unless configured |
| Weaviate / Milvus / Pinecone / Vespa | P8 | Large vector corpora | Not re-verified for memory use; check tenant isolation and hard-delete semantics before adoption |
| LanceDB | P8 + P10 | Local-first and multimodal | Dataset versioning is storage versioning, not valid time |
| turbopuffer | P8 (cost tier) | Many cold namespaces | Eventually consistent reads can be stale, which is wrong for read-your-writes memory; namespaces are the tenancy unit |
| SQLite FTS5 + sqlite-vec | P10 | Local or per-user memory | sqlite-vec is pre-v1 and brute-force; FTS5 deletes leave index entries until a merge unless secure-delete is on ([erasure](managed-memory-boundaries.md#erasure-across-derived-stores)) |
| Convex / Firestore | P1/P2 | App backends with memory beside them | Firestore splits vector search into a separate service |
| DuckDB + VSS | P8 | Offline eval and reranking | Not a live memory store |
| AWS Bedrock Knowledge Bases | P8 + P13 | Managed corpus retrieval, not agent memory | See [aws-bedrock-knowledge-bases](../../ai-rag/references/aws-bedrock-knowledge-bases.md) |

## Reading vendor memory benchmarks

A vendor chart is a claim about the vendor's configuration on the vendor's
questions. Before citing one, apply the rules in
[agent-memory-benchmarks](agent-memory-benchmarks.md#rules-before-you-trust-a-memory-number):
both baselines, configuration parity, n and intervals, a public runner, and a
re-run on your own workload. Benchmark scores are never recorded in this file.

## What to take from the matrix

1. **Bi-temporal is rare.** Graphiti and Zep document it. Elsewhere you model
   time in the schema (P25) or on Postgres columns (P4).
2. **Invalidation is not erasure.** Engines that "invalidate, never delete"
   keep the old fact on purpose. A deletion request still needs a physical
   purge across every derived store
   ([managed-memory-boundaries](managed-memory-boundaries.md#erasure-across-derived-stores)).
3. **Evidence-linked consolidation is rarer than consolidation.** Hindsight
   documents observations that point at their evidence; most others rewrite
   or merge without links (A31, A35, A47).
4. **Review UIs are shallow.** Graph viewers exist; none ships a
   contradiction queue or editorial approval workflow
   (`inspection-and-review-surfaces.md`).
5. **Managed services split into merge-on-write and offline rewrite.**
   Merge-on-write (Memory Bank, AgentCore) is auditable only through revision
   logs; an offline rewrite into a new store (dreams) can be diffed and
   rolled back.
6. **In-database embedding is a boundary decision.** It trades convenience for
   lock-in on the model; treat it as P13 with a documented migration plan.

## Routing rules by problem shape

- **Reviewable enterprise knowledge base** → Graphiti or Zep (P4) + a P7
  compiler + a custom review surface. No single vendor ships it. Substrate:
  Postgres or Neo4j.
- **Personal AI memory** → Mem0, Letta, Supermemory, or Honcho. Pick by write
  path: app-assembled facts (Mem0), self-edited blocks (Letta, P3), or
  reasoning about the user (Honcho). Substrate: Postgres, or SQLite for
  local-first.
- **Exact state and aggregates over a known domain** → schema-first typed
  memory (P25): xmemory, or the same pattern on Postgres.
- **Grounded retrieval for a corpus** → a managed P8 service or Anthropic
  Citations, by hosting preference.
- **Sovereign or offline memory** → MemPalace, SQLite FTS5 + sqlite-vec, or
  self-hosted Cognee or Graphiti.
- **Long-running coding agent** → files plus git (P10), Claude-Mem for
  single-developer session recall, Letta for P3; see RA5.
- **Multi-tenant customer KB** → managed P8 + per-tenant namespaces; see RA3
  and `tenant-isolation-patterns.md`.
- **Hosted memory boundary with you owning the bytes** → the Anthropic memory
  tool on your own storage.

Decision questions:

1. Do I need bi-temporal facts? → Graphiti or Zep, or Postgres with P4 columns.
2. Are the questions exact, aggregative, or stateful? → P25, with the
   generated query logged.
3. Do I have hard tenant isolation? → Postgres + forced RLS, or per-tenant
   namespaces; never a shared index with a caller-supplied filter (A10, A30).
4. Do I need erasure that survives audit? → any engine plus your own erasure
   runbook and sentinel test; none documents it end to end.
5. Am I locked into a model vendor? → avoid in-database embedding unless the
   migration path is documented.

## Before citing a row

Look up the engine's entry in `data/sources.json` and re-check, at the
primary URL, the four things that change fastest: licence and hosting
options, any maintenance or deprecation notice, whether a history or as-of
read exists, and the deletion semantics (soft or hard, revisions retained).
If the entry's `last_verified` is older than the review cadence above, say
so in the answer.
