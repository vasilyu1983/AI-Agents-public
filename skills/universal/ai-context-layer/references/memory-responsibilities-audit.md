# Memory Responsibilities Audit

Build or audit checklist for a knowledge-base or agent-memory system, end to end. Load it when the request is "audit our memory system", "build a KB for agents", or "compare memory engines" and the design is not yet decomposed. For one known failure, go straight to the pattern or anti-pattern instead. When the scenario is known (support desk, coding agent, incident memory), take its stage defaults from [memory-scenario-playbooks](memory-scenario-playbooks.md) and use this file to audit the deviations.

The lens: every memory system does seven jobs, from admission to materialisation. Engines bundle them differently and the jobs overlap, so audit each one separately. For each stage, record the decision, the default you picked or why you deviated, the acceptance checks you ran, and the evidence level.

## Contents

- [Step 0 — Workload first](#step-0--workload-first)
- [1. Admission](#1-admission)
- [2. Encoding](#2-encoding)
- [3. Persistence](#3-persistence)
- [4. Maintenance](#4-maintenance)
- [5. Retrieval](#5-retrieval)
- [6. Post-retrieval](#6-post-retrieval)
- [7. Materialisation](#7-materialisation)
- [Across stages](#across-stages)
- [Audit record format](#audit-record-format)

## Step 0 — Workload first

Classify the dominant question before picking any engine:

| Workload | Question it answers | Optimise for | Usual home |
|---|---|---|---|
| Analytics | What happened across history? | Complete, aggregable events | Warehouse or SQL over an event log, not a memory engine (hand-off below) |
| Agent memory | What must stay true and useful while the agent acts? | **Precision**: identity, updates, time, scope, validation | Typed state records (P2, P4, P22) |
| Search | Which evidence is relevant? | **Coverage**: broad recall with citations | Hybrid retrieval (P8) |

- Default: name one dominant workload and let it set the stage defaults below.
- Deviate when the workload needs both precision and coverage (the usual case for a policy KB or an incident memory). Then link current state to its supporting evidence (P22) instead of choosing one side.
- Analytics hand-off: land every interaction as an append-only event (pseudonymised IDs, model-assigned labels as derived columns with the labeller version) in a warehouse or event log, and answer from SQL. Do not route counts or trends through a memory engine; vector top-k silently undercounts. Scenario detail: [memory-scenario-playbooks](memory-scenario-playbooks.md#10-analytics-over-interaction-history).
- Check: write five real questions per workload and confirm which store answers each. A question no store owns is a gap; a question two stores answer differently is an A21 clash.

## 1. Admission

Decision: what is worth remembering, and who decides. The write paths are application writes (API calls, rules, event subscriptions), agent writes (tool calls, selection prompts), and a background worker (hooks, queues, model extraction).

- Default: application or event writes for system-of-record changes; background extraction for conversational facts; agent writes only through the P17 gate.
- Deviate to agent-selected writes when facts appear only in the agent's own reasoning. Accept that selection misses facts, and measure how many.
- Trade-off: rules need upkeep; agent selection misses facts; background writes cut request latency, but the memory arrives later.
- Acceptance checks:
  - every admitted item carries source class, owner scope, provenance, and time (SKILL.md Context Admission Gate);
  - admission recall probe: seed known facts into test episodes and count how many are captured, per write path;
  - background lag is measured (event to queryable), and a read inside the lag window reports `pending` instead of the stale value;
  - rejected writes are logged with a reason.
- Covered by: P2, P17, A1, A26, A32.

## 2. Encoding

Decision: text and episodes, atomic facts, or typed objects.

- Default: always keep raw episodes. Extract atomic facts with entity resolution to stable IDs (never display names) and time resolution (`valid_from` per P4, relative dates made absolute). Use typed objects (domain schema, Pydantic or a DSL) once state questions dominate.
- Deviate to text-only when the workload is search and no question asks for state.
- Trade-off: text needs interpretation at read time; typed objects need domain configuration up front.
- Acceptance checks:
  - rename test: rename an entity; the old name still resolves and no duplicate entity appears;
  - extraction output passes schema validation, and the failure rate is tracked;
  - conversion fidelity per source format: count tables in the raw XML against the extracted ones; look for dropped tracked insertions and image-only tables; check file type by magic bytes and title-body overlap, because filenames and extensions lie.
- Gotcha: `python-docx` `Document.tables` skips tables nested in content controls (`w:sdtContent`). In one in-house corpus this hit a large share of DOCX files with no error. Walk the body element tree instead.
- Covered by: P2, P5, P17, A6, A16; `markdown-chunking-patterns.md`, `multi-source-wiki-ingestion.md`.

## 3. Persistence

Decision: files (Markdown, JSONL), relational (Postgres or SQLite, with pgvector or FTS), graph, or a vector DB.

- Default: one relational store that holds typed records, episodes, a full-text index, and a vector column. Add a graph only when traversal changes answers (A9). Every derived row stores its source episode IDs.
- Deviate to files plus SQLite for local-first, single-writer agents (P10).
- Trade-off: every extra index adds consistency and recovery work (A40, A41).
- Acceptance checks:
  - rebuild from episodes reproduces identical state (idempotency);
  - every derived row joins back to an episode;
  - each index records a fingerprint (schema, tokenizer, embedding model, code hash) that the reader verifies.
- Covered by: P1, P4, P10, A2, A9, A13; `substrate-combinations.md`.

## 4. Maintenance

Decision: how memory stays correct over time. Three jobs:

- **Reconciliation**: contradiction checks with source and time precedence.
- **Forgetting**: TTL, decay, and cascading deletion.
- **Consolidation**: merging duplicates, connecting facts, extracting patterns, refreshing summaries.

- Default: reconcile at ingest (A4) with precedence authority, then effective time, then arrival (A38, A39). Forget by invalidation plus cascade (A7, A40). Run consolidation as a scheduled job that writes P21 evidence-linked observations, never free-floating rewrites (A31, A35).
- Deviate by skipping consolidation when reads return evidence only and volume is small; decay still applies.
- Trade-off: less read-time work, more compute, and derived updates that arrive late.
- Acceptance checks:
  - the state-maintenance eval passes per category ([evals-and-operations](evals-and-operations.md#state-maintenance-eval));
  - the post-cascade check finds no live derived artifact citing a tombstoned source;
  - every observation link resolves;
  - consolidation never raises confidence;
  - running dedup twice changes nothing;
  - stale derived nodes are invalidated rather than kept.
- Covered by: P4, P14, P21, P22, A3, A4, A7, A31, A35, A38, A39, A40.

## 5. Retrieval

Decision: which legs, how they are fused, and where filters apply. Legs are semantic (vectors, HNSW), lexical (BM25 plus exact identifier match), relational (graph traversal), and structured (SQL or a DSL, text-to-SQL).

- Default: lexical plus semantic, fused with RRF. Apply tenant, sensitivity, section-scope, and validity filters inside each leg before fusion (P23, P24). Send state questions to the structured lookup, and use the graph only for multi-hop questions (A33).
- Structured leg (state, count, and as-of questions):
  - fixed query templates for known question types first; a model-generated query (text-to-SQL) only as the fallback;
  - every query runs under a read-only database role with a statement timeout, over allowlisted views or a semantic layer, parsed and validated before execution; these defences hold only in combination (P2SQL, ICSE 2025);
  - the generated query is always logged and replayable with the answer (P25);
  - a scoped aggregate checks completeness and reports any in-scope record it could not include, instead of returning a silent partial count;
  - multi-turn follow-ups ("and last month?") keep the previous query state as working memory; stateless multi-turn text-to-SQL has been reported to collapse within a few turns (EnterpriseMem-Bench, arXiv 2605.26394, abstract);
  - BI-shaped access (semantic layer, certified metrics, warehouse tools over MCP) belongs to [mcp-for-dwh](../../agents-mcp/references/mcp-for-dwh.md).
- Deviate to lexical-only for a small corpus queried by exact terms, but measure paraphrase and multilingual recall before claiming coverage; lexical-only was weak on both in one in-house build.
- Trade-off: broad retrieval finds more; strict filters miss evidence.
- Acceptance checks:
  - an independent held-out question set, written by people who did not build the KB, with per-slice floors (the builders' own set inflates scores);
  - hard negatives, including cross-scope ones;
  - the retrieval path used is recorded and asserted (A41);
  - sensitivity canaries pass.
- Covered by: P8, P12, P23, P24, P25, A18, A30, A33, A41; method in [ai-rag](../../ai-rag/SKILL.md).

## 6. Post-retrieval

Decision: select evidence (dedup, cross-encoder rerank), compute a result (SQL joins, aggregates, temporal predicates), or synthesise (model answer, iterative retrieval).

- Default: compute for state, aggregate, and as-of questions; for "who owned X at t", use the P4 predicate `valid_from <= t AND (valid_to IS NULL OR t < valid_to)`, adding the `recorded_at` / `superseded_at` predicate for "as known at" questions (engine-native names are mapped in P4). Select evidence for search. Synthesise only behind a citation-support check, and abstain when coverage is insufficient.
- Trade-off: returning evidence leaves interpretation to the agent; synthesis can lose detail or introduce errors.
- Acceptance checks:
  - as-of questions match a replayed event log;
  - citation-support rate is tracked: each cited span actually supports its claim;
  - abstain rate on unanswerable questions is tracked;
  - synthesis faithfulness is measured against the selected evidence.
- Covered by: P4, P8, P20, P22.

## 7. Materialisation

Decision: what shape leaves the memory system — text, JSON, or rows.

- Default: machine consumers get structured, validated output (`value`, `as_of`, `evidence[]`, `confidence`, `status`); human-facing text is rendered from that record.
- Deviate to text when the only consumer is a model prompt with no field-level monitoring. Even then, keep the evidence IDs.
- Acceptance checks:
  - schema validation rate is monitored per field;
  - field-level drift alerts exist;
  - output is fenced and scrubbed;
  - the same memory rendered as text and as JSON carries the same values.
- Covered by: P12 typed projections, A29; `context-assembly.md`.

## Across stages

- Evaluate each stage on its own and end to end. A good end-to-end score can hide one stage compensating for another.
- Choose the model per stage on cost: extraction, consolidation, rerank, and synthesis rarely need the same model.
- Re-run the stage evals on every model or prompt update. Treat it as a standing workstream, not a launch task ([ai-evals](../../ai-evals/SKILL.md) owns the method).
- Adopt an engine for persistence and retrieval when one fits ([vendor-landscape](vendor-landscape.md#agent-memory-engines-by-representation-and-output)); own the domain configuration (schema, precedence, scope model) and the acceptance tests yourself.
- Code and doc hubs drift the same way: hand-written pages need a `generated_from` stamp and a freshness lint, and counts copied by hand into several files should be generated from one source.

## Audit record format

```text
MEMORY AUDIT: <system>
Workload: agent memory (precision) + search (coverage) -> P22
1 Admission    | default: event writes + background extraction | checks: recall probe per write path, lag measured | evidence: loaded
2 Encoding     | deviation: text-only for runbooks (search-only)  | checks: rename test FAIL -> fix | evidence: static
...
7 Materialise  | default: JSON record + rendered text            | checks: per-field validation | evidence: evaluated
Open: <stage>: <gap>, owner, next bounded step
```

The anti-pattern sweep (`anti-patterns-catalog.md`) still runs after this audit; the audit decides the design, the sweep confirms what it blocks.
