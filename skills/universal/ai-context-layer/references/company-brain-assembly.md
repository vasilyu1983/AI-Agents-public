# Company Brain Assembly

> Purpose: End-to-end composition recipe for assembling a regulated, multi-source company brain — a P7 LLM Wiki fed by lawful collectors, backed by a pseudonymised warehouse, queryable via MCP, with agent/LLM access governed at every seam. Composes six shared skills into one orchestration. Vendor-neutral; org-specific values (vendor names, jurisdictions, retention windows, vault keys) stay in the project repo.

## Table of Contents

- [When to use this assembly](#when-to-use-this-assembly)
- [The 5-layer stack](#the-5-layer-stack)
- [Phase 1 — Collectors](#phase-1--collectors)
- [Phase 2 — DWH staging and PII vault](#phase-2--dwh-staging-and-pii-vault)
- [Phase 3 — Wiki ingestion pipeline](#phase-3--wiki-ingestion-pipeline)
- [Phase 4 — Risk and signal packs (optional)](#phase-4--risk-and-signal-packs-optional)
- [Phase 5 — MCP query surface](#phase-5--mcp-query-surface)
- [Phase 6 — Agent and answer layer](#phase-6--agent-and-answer-layer)
- [Seam anti-patterns](#seam-anti-patterns)
- [Phase-to-phase gates](#phase-to-phase-gates)
- [Composition with other patterns](#composition-with-other-patterns)
- [Check](#check)

## When to use this assembly

Use when ALL hold:

- The org needs a knowledge surface fed by ≥2 source systems (code platform, ticket platform, chat, meeting, email, calendar, audit logs).
- The same surface must serve **humans** (reviewers reading wiki pages) **and** **agents** (LLM-grounded answers with citations).
- The org carries data-protection obligations (employee, customer, or counterparty data).
- Decisions read from the surface must be auditable (claim → wiki page → source event → raw audit row).

Do NOT use when:

- A single team needs a single-source product brain → use [`operational-brain-pattern.md`](operational-brain-pattern.md) directly.
- The corpus is documents only, no entity graph → standard hybrid RAG patterns.
- The org has no PII vaulting capability yet → build that first (Phase 2 is a hard prerequisite; skipping it is not optional).

## The 5-layer stack

```text
┌─ Layer 5: Agent / answer surface ───────────────────────────────┐
│  LLM with MCP. Reads wiki + DWH metrics. Never sees raw PII.    │
│  Owns: routing, citation, supersede transparency.               │
├─ Layer 4: MCP query surface ────────────────────────────────────┤
│  Read-only role-scoped MCP. Audit log per call. Per-purpose     │
│  isolation. PII boundary enforced at the DB.                    │
├─ Layer 3: LLM Wiki (P7) + Signal packs ─────────────────────────┤
│  Entity / concept / synthesis / source / index / log pages.     │
│  Supersede records. Optional triage packs feed Cases.           │
├─ Layer 2: DWH staging + PII vault ──────────────────────────────┤
│  Fact tables per source. Pseudonyms in marts. Direct identifiers│
│  vaulted. Role-based unmask views audited.                      │
├─ Layer 1: Collectors ───────────────────────────────────────────┤
│  Admin-API pulls + bot-as-participant for meetings. No endpoint │
│  capture. Replayable. Idempotent.                               │
└─────────────────────────────────────────────────────────────────┘
```

Each phase below builds one layer. Phases gate on the layer below being verified.

## Phase 1 — Collectors

**Owns:** turning source systems into idempotent, replayable event streams landing in object storage.

**Pre-requisite:** Lawful basis declared per source (LIA / DPIA / consultation as required for your jurisdiction; this assembly does not specify the jurisdiction).

**Primary skill ref:** none in the shared library. Choose per source among admin-API export, bot-as-participant, and endpoint collectors by lawful basis, coverage, and failure mode, and record the choice. Use a project-scoped collector reference if your project has one; the shared library does not name client skills.

**Steps:**

1. Pick Pattern A (admin-API) for code/ticket/chat/email/calendar platforms; Pattern B (bot-as-participant) for cross-vendor meeting capture; reject Pattern C (endpoint) for centralised collection.
2. For each source: scoped service account + admin scopes minimal-necessary + audit-trail location identified.
3. One collector per source — no shared credentials, no shared purpose.
4. Output contract: append-only events to object storage with `source_episode_id` (stable across re-pulls), `source_system`, `pulled_at`, `payload`. Replay = re-fetch by `source_episode_id` range.
5. Per-source dead-letter queue + polling budget + exponential backoff.
6. Per-source purpose tag travels with every event (used at Phase 5 enforcement).

**Phase gate:** for every source, prove (a) replay produces identical staging output, (b) credentials are vaulted not file-resident, (c) audit trail in the source platform shows the collector's reads.

## Phase 2 — DWH staging and PII vault

**Owns:** turning event streams into governed analytical tables with direct identifiers vaulted and pseudonyms in marts.

**Pre-requisite:** Phase 1 events landing in staging. Column-classification schema agreed (direct / quasi / sensitive / non-sensitive).

**Primary skill ref:** [`../../data-analytics-engineering/references/pii-vault-and-pseudonymisation.md`](../../data-analytics-engineering/references/pii-vault-and-pseudonymisation.md) — column classification, tokenisation choice tree, role-based unmask, LLM-context PII boundary.

**Steps:**

1. Stand up `vault.person` (and `vault.account`, `vault.customer` as needed) with `canonical_id`, `pseud` (HMAC), `source_system_ids` JSON for identity bridging, `direct_identifiers` encrypted/separate.
2. Stage models per source (`stg_<source>__events`); raw direct identifiers land in vault only, never in stage tables consumed by marts.
3. dbt contracts on every model with `meta: {pii: direct | quasi | sensitive | none}`; CI test enforces no `pii: direct` outside `models/sensitive/`.
4. Mart layer (`mart.fact_*`) joins on `pseud`, never `email` or `user_id`.
5. Role matrix: `analyst_pseud` (default), `analyst_unmask` (audited unmask view), `llm_agent` (pseud-only, no unmask grants). Application-layer masking is not sufficient — enforce at DB.
6. Erasure mechanic wired: `vault.person.erasure_requested_at` → crypto-shred direct identifiers, pseud retained for mart integrity, audit log row.

**Phase gate:** (a) `llm_agent` role provably cannot return a direct identifier under any query, (b) erasure test passes (request → vault row null → marts still functional, no person-path), (c) backup re-erasure documented.

## Phase 3 — Wiki ingestion pipeline

**Owns:** turning per-source events into idempotent edits on a P7 LLM Wiki with provenance and supersede records.

**Pre-requisite:** Phase 2 marts and vault operational; canonical entity IDs available via vault.

**Primary skill refs:**
- Page model + supersede + provenance: [`knowledge-compilation-and-wiki-pattern.md`](knowledge-compilation-and-wiki-pattern.md)
- The pipeline shape: [`multi-source-wiki-ingestion.md`](multi-source-wiki-ingestion.md)
- Single-product brain primitives (entity/relation/synthesis/log): [`operational-brain-pattern.md`](operational-brain-pattern.md)

**Steps:**

1. Define entity types for the org (person, project, repo, team, customer, decision — pick what matches your reality, not what looks complete).
2. Per source: extractor (event → typed entities + facts + `source_episode_id`), entity resolver (stable-id lookup against vault), reconciler (NEW / UPDATE / SUPERSEDE / CONTRADICTION decision).
3. Page writer is atomic per page, emits markdown diff + structured supersede sidecar, updates page header with `last_updated`, `last_source_event_id`, `contradiction_flag`.
4. Append-only run-log page per ingest (`run_id`, sources, extracted/reconciled/superseded counts, contradictions, duration).
5. Contradiction queue is a wiki page; resolver decisions become supersede records with rationale.
6. **Pseudonymise at extractor stage** — entity pages carry pseud + role + signal summaries, not direct identifiers. De-pseudonymisation is a Phase 5 concern, not a wiki concern.

**Phase gate:** (a) re-running ingestion of any source window produces identical wiki state modulo `pulled_at`, (b) every entity page claim traces to a `source_episode_id`, (c) one synthetic contradiction is resolved end-to-end via the queue.

## Phase 4 — Risk and signal packs (optional)

**Owns:** turning multi-source events into governed Case envelopes for convergent-signal review (fincrime, IT insider risk, employee comms, ops anomaly, compliance controls).

**Pre-requisite:** Phases 1–3 operational. Lawful basis per pack purpose distinct from collector purpose tags.

**Primary skill ref:** a project-scoped governed triage engine (engine contract plus pack router), if your project has one; without one, stop at Phase 3. Pick exactly one pack per entity type; do not blend.

**Steps:**

1. Pick the pack(s) that match the entity types defined in Phase 3.
2. Wire the pack's detector to read from Phase 2 marts (NOT directly from collectors — never bypass the vault).
3. Case envelopes emit to a `case` table that is itself a Phase 3 source for the wiki (Cases become a page type with their own provenance).
4. Severity tier outputs route to the pack's disposition lifecycle; consequential dispositions require human review per the engine's governance gate.
5. Purpose tag on Case envelope MUST match the LIA for the pack — purpose-creep across packs is the most common breach mode.

**Phase gate:** for one pack end-to-end, prove (a) a Case envelope generates from real Phase 2 marts, (b) governance gate refuses `Review` without LIA presence, (c) Case appears on the wiki via Phase 3 with provenance.

## Phase 5 — MCP query surface

**Owns:** giving agents read access to the wiki + DWH with read-only roles, pseudonym enforcement, query budgets, and an audit log per call.

**Pre-requisite:** Phases 2 and 3 operational (Phase 4 optional). Per-purpose roles defined in the DWH.

**Primary skill ref:** [`../../agents-mcp/references/mcp-for-dwh.md`](../../agents-mcp/references/mcp-for-dwh.md) — three MCP shapes (managed-BI / DB-driver / custom-thin), the seven enforcement layers, audit log contract.

**Steps:**

1. Pick the MCP shape per use case: Shape A (managed BI) if a semantic layer fronts the warehouse; Shape B (DB-driver) for exploratory analyst-style agent use; Shape C (custom thin) for high-stakes domains where every query class must be pre-reviewed.
2. One MCP server per purpose. Per-purpose role in the DB (`agent_fincrime`, `agent_comms`, `agent_kpi`, `agent_brain_reader`). Roles are read-only at the DB layer — not by trusting the LLM.
3. Wiki access is a separate MCP tool (`fetch_wiki_page(slug)`, `list_entities_of_type(...)`) — do not expose wiki pages via the warehouse MCP. Different access patterns, different audit needs.
4. Append-only audit table `mcp_audit` not readable by any MCP role.
5. Query budgets: statement timeout, max rows, max bytes scanned, max cost per session.
6. Pseudonym boundary enforced at the connection: `llm_agent`-class roles have grants only on pseud columns/views.

**Phase gate:** (a) MCP role provably cannot execute non-SELECT or return direct identifiers under adversarial prompt, (b) every MCP call appears in `mcp_audit`, (c) per-purpose isolation verified (`agent_fincrime` cannot read `mart.fact_meeting` etc.).

## Phase 6 — Agent and answer layer

**Owns:** the LLM-served answer surface — wiki-grounded reads, citation discipline, supersede transparency, missing-entity handling.

**Pre-requisite:** Phase 5 MCP operational.

**Primary skill ref:** [`../../ai-rag/references/wiki-grounded-retrieval.md`](../../ai-rag/references/wiki-grounded-retrieval.md) — entity-first → synthesis → vector routing, citation tuple, supersede-aware reads, 5-class eval.

**Steps:**

1. Implement the routing rule: extract named entities from the query → direct entity-page fetch (via Phase 5 MCP) → synthesis-page fallback → vector fallback over source pages only.
2. Citation tuple `(wiki_page_slug, page_version_id, retrieved_at)` on every claim. Tuple must let a reviewer reproduce the read.
3. Missing-entity handler: never hallucinate; return "not in wiki, stub-draft offer" and log a `missing_entity` event (high-value wiki maintenance backlog).
4. Supersede-aware reads: when a fetched fact has a recent supersede record, the response carries a one-line note.
5. Eval set with 5 classes: named-entity-factual, named-entity-multi-hop, synthesis, vector-fallback, supersede-transparency. Continuous regression in CI.
6. Per-purpose agent identity: agent calling the MCP carries its purpose tag; cross-purpose queries refused at MCP layer (Phase 5).

**Phase gate:** (a) eval set passes thresholds, (b) one adversarial prompt asking for raw email/identifier is refused at the MCP boundary, (c) one recently-superseded fact in a response carries the change note.

## Seam anti-patterns

Most failures happen at the seams between phases. Watch for:

| Seam | Anti-pattern | Consequence | Corrective |
|---|---|---|---|
| 1→2 | Direct identifiers land in stage tables before vault | PII spread; erasure broken | Vault is the first writer on every identifier column |
| 2→3 | Wiki extractor reads vault unmask view | LLM-readable pages contain direct identifiers | Extractor reads pseud columns only |
| 3→4 | Pack reads collectors directly, bypassing vault | Pack-private pipeline of raw PII | Packs read from Phase 2 marts only |
| 4→3 | Case envelope written direct to wiki without provenance | Cases not auditable as wiki claims | Cases enter wiki as a source like any other |
| 2→5 | MCP role created with `SELECT *` on a schema | PII exposed via wildcard query | Column grants only; deny direct identifiers at role |
| 3→5 | Wiki pages exposed via the warehouse MCP | Audit-pattern mismatch; wiki contradictions invisible | Separate MCP tools for wiki vs warehouse |
| 5→6 | Agent reconstructs identifiers from pseuds via prompt | LLM as PII reversal channel | Pseud unmask is a separate MCP tool with separate role + audit |
| 6→3 | Vector retrieval indexes entity/synthesis pages | Circular hits, derived-content retrieval | Vector scope = source pages only |
| 1↔all | Single collector serves multiple purposes (e.g. one Slack pull for fincrime AND productivity) | Purpose-limitation breach | Per-purpose collectors + per-purpose audit tags |

## Phase-to-phase gates

A phase is NOT done until its gate passes. The next phase imports failures otherwise. Order matters: 1 → 2 → 3 → (4) → 5 → 6.

| Phase | Gate condition | If gate fails |
|---|---|---|
| 1 | Replay produces identical staging | Fix extractor non-determinism before any vault work |
| 2 | LLM role cannot return direct identifiers | Do NOT proceed to wiki ingestion |
| 3 | Re-ingest produces identical wiki state | Fix idempotency before opening to live writes |
| 4 | Pack governance gate refuses Review without LIA | Engine misconfigured; pack not production-ready |
| 5 | MCP audit log captures every call; per-purpose isolation holds | Do NOT expose to agents |
| 6 | Eval set passes; adversarial-prompt PII extraction refused | Do NOT expose to humans |

## Composition with other patterns

| Pattern from this skill | Role in the assembly |
|---|---|
| [`operational-brain-pattern.md`](operational-brain-pattern.md) | The single-product brain primitive Phase 3 extends to multi-source / multi-team |
| [`knowledge-compilation-and-wiki-pattern.md`](knowledge-compilation-and-wiki-pattern.md) | P7 page model that Phase 3 writes to |
| [`multi-source-wiki-ingestion.md`](multi-source-wiki-ingestion.md) | The pipeline contract Phase 3 implements |
| [`inspection-and-review-surfaces.md`](inspection-and-review-surfaces.md) | The human review UI for Phase 3 contradictions + Phase 4 cases |
| [`reference-architectures.md`](reference-architectures.md) | Higher-level RA1–RA13 catalog; this assembly maps closest to a multi-source RA |
| [`composition-with-related-skills.md`](composition-with-related-skills.md) | General composition guidance; this file is one concrete composition |

## Check

The assembly is right if all hold:

- Every wiki claim traces: claim → wiki page → `source_episode_id` → raw source audit row. A reviewer can click through.
- No direct identifier exists outside `vault.*` tables. The LLM role provably cannot return one.
- Every MCP call appears in `mcp_audit`; per-purpose roles are isolated.
- Re-running any phase from its replay point produces identical downstream state.
- Supersede records exist and the agent layer surfaces recent changes.
- Cases (Phase 4) appear on the wiki with provenance, not as a side-channel pipeline.
- One adversarial prompt asking for `email_for(p_xxxx)` is refused at the MCP layer, not by a prompt instruction.
- Adding a new source = new collector + new extractor + new entity-resolver mapping, zero changes to Phases 4–6.
