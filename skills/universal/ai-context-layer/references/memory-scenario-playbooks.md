# Memory Scenario Playbooks

Load this first when the scenario is known (personal assistant, support desk, coding agent, incident memory, and so on). Each playbook sets the stage defaults for the seven responsibilities (R1 admission, R2 encoding, R3 persistence, R4 maintenance, R5 retrieval, R6 post-retrieval, R7 materialisation) and links to the depth that already exists. When no scenario fits, or the system is being audited end to end, use [memory-responsibilities-audit](memory-responsibilities-audit.md) instead.

Every default below is practitioner synthesis unless a source is named. Research citations give the direction of an effect, not a magnitude; most were read at abstract level, so treat them as "reported, not replicated".

## Contents

- [Selector](#selector)
- [Cross-cutting rules](#cross-cutting-rules)
- [1. Personal assistant / end-user memory](#1-personal-assistant--end-user-memory)
- [2. Customer support / CRM, multi-tenant](#2-customer-support--crm-multi-tenant)
- [3. Coding-agent memory](#3-coding-agent-memory)
- [4. Multi-agent shared memory](#4-multi-agent-shared-memory)
- [5. Regulated enterprise knowledge base](#5-regulated-enterprise-knowledge-base)
- [6. Multi-repo code hub](#6-multi-repo-code-hub)
- [7. Incident / ops memory with point-in-time ownership](#7-incident--ops-memory-with-point-in-time-ownership)
- [8. Long-running agent with procedural memory](#8-long-running-agent-with-procedural-memory)
- [9. Voice / realtime](#9-voice--realtime)
- [10. Analytics over interaction history](#10-analytics-over-interaction-history)
- [11. On-device / privacy-first](#11-on-device--privacy-first)

## Selector

Representation runs text/notes → linked facts → typed entities; output runs broad context → selected context → synthesised or computed answer.

| # | Scenario | Workload | Coverage vs precision | Representation × output | First pattern |
|---|---|---|---|---|---|
| 1 | Personal assistant | Agent memory | Precision | Scoped facts + profile × selected | P2 (+P6) |
| 2 | Support / CRM | Agent memory over a system of record | Precision for account state, coverage for prior issues | Typed notes linked to CRM IDs × selected | P1 |
| 3 | Coding agent | Agent memory (project + procedural) | Precision | Files × broad index + on-demand topics | P10, P12 |
| 4 | Multi-agent shared | Coordination memory | Precision with provenance | Typed artifacts × role-scoped selected | P16 |
| 5 | Regulated KB | Search over a governed corpus | Both | Typed registry + passages × selected with citations | P22 (+P23, P24) |
| 6 | Multi-repo hub | Search + structured graph | Coverage for impact, precision for ownership | Typed graph + cards × computed + selected | P4, P12 |
| 7 | Incident / ops | Search + state | Recall at triage, precision for owner and fix | Typed records + episodes × computed (as-of) | P22, P4 |
| 8 | Procedural agent | Agent memory (skills) | Precision | Code or step files × selected skills | P15 |
| 9 | Voice / realtime | Agent memory under a latency budget | Precision with very small k | Compact profile × preloaded | RA13, P2 |
| 10 | Analytics | Analytics, not memory | Coverage (complete counts) | Event rows × computed (SQL) | Hand off to a warehouse |
| 11 | On-device | Agent memory, local | Precision, small store | Facts + episodes × selected | P10 |

## Cross-cutting rules

These hold in every scenario unless a playbook overrides them.

- **Keep raw episodes.** Derived facts, summaries, and observations must be rebuildable from an append-only episode log. Fact extraction that replaces the original text loses information; LongMemEval (arXiv 2410.10813) reports better recall when extracted facts expand the index keys and the original rounds stay as values.
- **Run two baselines.** Compare every memory design against a no-memory baseline and a full-context baseline on the same questions. Memory papers have reported full context matching or beating memory on accuracy when the history fits the window (the Mem0 authors' own table, arXiv 2504.19413), so a "memory wins" claim on a short benchmark is usually a cost and latency claim.
- **Consolidate into a new artifact, gated by eval.** Consolidation writes a new version (P14, P21), is diffed against the previous one, and is promoted only when the stage eval holds. Repeated in-place consolidation has been reported to raise utility at first and then degrade it, while an episodic-only control stays competitive (arXiv 2605.12978, abstract).
- **Store user statements as attributed claims.** "User said X" is a claim with the user as source, not a fact about the world. Saved claims have been reported to amplify sycophancy in later sessions (arXiv 2607.10526, abstract), and memory is not evidence for factual answers.
- **Derive scope from authenticated identity.** Tenant, user, and clearance come from the server-side principal bound at session start, never from a tool argument or a model-supplied ID. Platform session IDs are not authentication. Apply the scope inside each retrieval leg ([tenant-isolation-patterns](tenant-isolation-patterns.md)).
- **One vocabulary for time.** Valid time and transaction time follow P4 in [patterns-catalog](patterns-catalog.md#p4--temporal-knowledge-graph-with-bi-temporal-facts).
- **Eval method lives elsewhere.** Held-out sets, per-stage scoring, and regression gates are in [retrieval-and-memory-eval](../../ai-evals/references/retrieval-and-memory-eval.md), with state-maintenance scoring in [§4](../../ai-evals/references/retrieval-and-memory-eval.md#4-state-maintenance-scoring), cross-tenant canaries in [§5](../../ai-evals/references/retrieval-and-memory-eval.md#5-cross-tenant-leakage-slice), and learned or procedural memory in [§6](../../ai-evals/references/retrieval-and-memory-eval.md#6-learned-and-procedural-memory). Each playbook lists only the scenario-specific acceptance tests.

Row format used below: `R1–R7` gives one line per responsibility; links point at the existing depth instead of repeating it.

## 1. Personal assistant / end-user memory

"Our product must remember users across sessions." One end user, many sessions, consumer or prosumer.

- **Workload**: agent memory, personalisation. **Bias**: precision. An irrelevant or wrong personal fact does more harm than a missing one; over-personalisation and cross-domain leakage have been reported as common failures (OP-Bench arXiv 2601.13722, PersistBench arXiv 2602.01146, abstracts).
- **R1**: extract preferences, stable facts, and explicit "remember / forget" requests; skip what can be derived or is ephemeral; default-deny special-category data unless the user asks.
- **R2**: raw rounds as episodes; a small profile for stable attributes plus a collection of scoped facts, each with a domain label (work, travel, health) and evidence; user statements stored as claims.
- **R3**: one relational store, partitioned by user (P2, P6).
- **R4**: invalidate on update (P4); "forget X" deletes everywhere, including derived summaries; offline consolidation into a reviewable version (P14).
- **R5**: profile at session start, plus top-k scoped facts per turn.
- **R6**: a task-relevance gate that drops memories from another domain; never cite a stored claim as evidence.
- **R7**: a rarely-changing profile block may sit in the cached prefix; per-turn facts go after the cache breakpoint.
- **Default stack**: Postgres with a vector column and row-level security, or a managed memory service behind P13. **Upgrade trigger**: add a temporal graph (P4) only when questions ask about relationship history ("who was my manager when").
- **Maintenance**: newest valid time wins and the old fact stays invalidated; TTL on conversation summaries, not on explicit preferences; a user-visible "manage memories" view and a no-memory mode.
- **Acceptance tests**: knowledge-update and abstention probes ([§4](../../ai-evals/references/retrieval-and-memory-eval.md#4-state-maintenance-scoring)); cross-domain leakage probes; repetition and irrelevance probes; a rename and relationship-change slice; erasure reaches facts, vectors, summaries, and caches.
- **Top failures**: saved claims hardening into "facts" (A49); over-personalisation from self-extracted preferences (A26); persistent injected instructions (A19, A23); deleting a chat leaves memory derived from it (A11).
- **Depth**: [entity-and-memory-models](entity-and-memory-models.md), [managed-memory-boundaries](managed-memory-boundaries.md), [security-threat-model](security-threat-model.md).

## 2. Customer support / CRM, multi-tenant

"Customer support agent memory per customer, multi-tenant." Two tenancy layers: the operator (your SaaS customer) and their end customers.

- **Workload**: agent memory over a system of record. **Bias**: precision for account state, coverage for prior-issue recall.
- **R1**: never admit account state (plan, balance, entitlements) into memory; read it live (P1). Admit interaction summaries, stated preferences, and resolutions.
- **R2**: ticket-level records keyed by stable customer and ticket IDs; resolution notes typed as problem → steps → outcome.
- **R3**: tenant-partitioned relational store; per-customer scope inside the operator tenant.
- **R4**: retention from the support contract and law; invalidate a note when the CRM state it references changes.
- **R5**: structured lookup by customer ID first, then hybrid search over that customer's history, then similar resolved tickets inside the operator tenant only.
- **R6**: cite the ticket or record; abstain on any account fact not confirmed live.
- **R7**: a customer card of live CRM fields plus the last few interaction summaries and the open handoff note.
- **Default stack**: Postgres plus CRM API tools. **Upgrade trigger**: an outbox from the CRM into a search index when ticket volume outgrows the relational search; a graph only for account hierarchies.
- **Maintenance**: nightly reconciliation against the CRM; data-subject erasure cascades the customer ID through notes, vectors, summaries, and logs.
- **Acceptance tests**: prior-issue recall on held-out real tickets; cross-customer and cross-tenant canaries that must score zero ([§5](../../ai-evals/references/retrieval-and-memory-eval.md#5-cross-tenant-leakage-slice)); stale-state probes (plan changed after the note).
- **Top failures**: memory says "premium" after a downgrade (A2, A38); leakage through a shared semantic cache (A10, A30); a filter added after ANN that silently drops the customer's own history.
- **Depth**: the support/CRM recipe in [tenant-isolation-patterns](tenant-isolation-patterns.md#recipe-support--crm-memory), [semantic-caching](semantic-caching.md).

## 3. Coding-agent memory

A coding agent in one repo across developer sessions.

- **Split first**: instruction files (`AGENTS.md`, `CLAUDE.md`, path-scoped rules) are human-owned configuration and belong to [agents-memory](../../agents-memory/SKILL.md). This playbook covers learned notes: what the agent records about the project, gotchas, and user feedback. A learned note that keeps being right is promoted to an instruction file by a human; the note is never edited into instructions automatically.
- **Workload**: agent memory, project plus procedural. **Bias**: precision; a stale command breaks builds.
- **R1**: record only what the code cannot tell you: non-standard conventions, gotchas, feedback, external references.
- **R2**: Markdown with typed frontmatter (type, created, last-verified) and code-location citations; JSON for task lists.
- **R3**: files under version control (P10); one memory scope per subagent.
- **R4**: re-verify cited code locations at read time; expire notes that are not revalidated; periodic conflict audit between notes and instructions.
- **R5**: an always-loaded capped index plus topic files on demand (P12).
- **R6**: when a note conflicts with current code, the code wins and the note is flagged.
- **R7**: short; hard constraints go to hooks, not memory.
- **Default stack**: files plus git plus a progress log. **Upgrade trigger**: a local full-text index over the memory directory when the index outgrows its cap; a symbol graph when navigation, not recall, is the bottleneck ([dev-context-code-graph](../../dev-context-code-graph/SKILL.md)).
- **Acceptance tests**: task success and cost with and without the memory files on the same tasks (context files have been reported to add cost without improving success, arXiv 2602.11988, abstract); seeded false-memory tests ([§6](../../ai-evals/references/retrieval-and-memory-eval.md#6-learned-and-procedural-memory)); path portability (no absolute paths).
- **Top failures**: stale commands; premature "done" (A36); notes written from an untrusted repo file (A19); concurrent writers clobbering each other (A32).
- **Depth**: [filesystem-as-memory](filesystem-as-memory.md).

## 4. Multi-agent shared memory

Cooperating agents that must share findings and decisions.

- **Workload**: coordination memory (blackboard). **Bias**: precision with provenance; every reader must know who wrote what and whether it was verified.
- **R1**: every write carries writer agent, role, task ID, trust tier, and evidence; writes land in the writer's scratch scope.
- **R2**: typed artifacts (plan, finding, decision, open question) with references to large outputs stored outside the board.
- **R3**: one transactional store with optimistic concurrency (a content-hash precondition) and an append-only event log.
- **R4**: the orchestrator owns consolidation; agents propose, a gate promotes (P16 `promote`, P17); conflicts go to an arbiter, not last-write-wins.
- **R5**: by task and role scope; do not hand every agent the whole board.
- **R6**: label author and verification state; an unverified peer claim is a hint.
- **R7**: a role-specific briefing plus references; the plan stays pinned.
- **Default stack**: Postgres or a versioned KV store plus an object store for artifacts. **Upgrade trigger**: an event bus when agents must react to board changes rather than poll.
- **Acceptance tests**: audit inter-agent channels as well as final outputs (internal channels have been reported to leak more than outputs, arXiv 2602.11510, abstract); concurrent-write tests with a stale precondition that must be rejected; poisoned-peer test.
- **Top failures**: one agent's bad claim propagated as fact (A32); evaluator bias carried through stored trajectories (arXiv 2606.23195, abstract); role drift.
- **Depth**: P11, P16, RA12 in [reference-architectures](reference-architectures.md); parallel coding-agent races in [agents-memory](../../agents-memory/SKILL.md).

## 5. Regulated enterprise knowledge base

A governed policy or procedure corpus served to agents, often for several legal entities and clearance levels.

- **Workload**: search over a governed corpus with state questions ("which version applies"). **Bias**: both; a missed obligation and a superseded policy are both failures, so link current state to evidence (P22).
- **R1**: ingest only from the registry of record; record status, three-state approval with its basis, effective dates, supersession, sensitivity, and scope per section (P23).
- **R2**: convert to Markdown with tables preserved and section IDs kept; check conversion fidelity per format (the encoding gotchas in [memory-responsibilities-audit](memory-responsibilities-audit.md#2-encoding)).
- **R3**: a typed registry plus a per-scope full-text index; relation edges only with text evidence (A42).
- **R4**: supersession tombstones cascade to index, graph, and caches (A40); re-convert and re-index when parsers change; reject `superseded_by` self-pointers.
- **R5**: hybrid; scope, effective date, and clearance filters inside every leg before fusion (P24); clearance bound at server launch.
- **R6**: rerank, citation-support check, abstain on low coverage, flag draft or under-review hits.
- **R7**: quote with document ID, section, and effective date; never paraphrase an obligation without its source text.
- **Default stack**: SQLite FTS5 per scope or Postgres with RLS, served by a retrieval tool ([agents-mcp](../../agents-mcp/SKILL.md)). **Upgrade trigger**: add dense retrieval and a reranker when paraphrase or multilingual slices miss their floor ([ai-rag](../../ai-rag/SKILL.md)).
- **Acceptance tests**: an independent held-out question set written by non-builders; cross-scope and superseded-version hard negatives; point-in-time questions; sensitivity canaries; index fingerprint asserted (A41).
- **Top failures**: own-eval inflation; addendum leak across entities (A43); silent fallback to a weaker index (A41); personal data carried in converted documents.
- **Depth**: [policy-and-compliance-docs](policy-and-compliance-docs.md), RA11, [company-brain-assembly](company-brain-assembly.md).

## 6. Multi-repo code hub

A context hub over many repositories: services, APIs, queues, tables, owners.

- **Owner**: [dev-context-multi-repo](../../dev-context-multi-repo/SKILL.md) owns the scanners, graph, cards, freshness, and drift reports. This playbook adds only the memory-design checks.
- **Workload**: search plus structured graph queries. **Bias**: coverage for impact analysis, precision for ownership and contracts.
- **R1**: deterministic scanners only, with a base commit per repo; model-written prose tagged inferred and stamped with the commit it was generated from.
- **R2–R3**: typed graph tables (SQLite or Postgres) plus short repo cards; make the graph queryable through a tool, not a large file agents must read.
- **R4**: rescan on merge; expire nodes absent from the latest scan, keeping a history row; one generated home per count.
- **R5–R7**: graph query first, then full-text over cards, then just-in-time code reads (P12); show source commit and staleness age.
- **Upgrade trigger**: bitemporal edges (P4 vocabulary) once "what depended on X last quarter" questions appear.
- **Acceptance tests**: a question-level retrieval eval, not only structural checks; impact-analysis recall against known incidents; a freshness SLO on hand-written pages.
- **Top failures**: hand-written pages drift unstamped; stale nodes kept instead of forgotten; counts hand-copied into several files.
- **Depth**: RA10, [git-anchored-ingestion](git-anchored-ingestion.md), [composition-with-related-skills](composition-with-related-skills.md).

## 7. Incident / ops memory with point-in-time ownership

"Who owned the incident at 09:05?" and "have we seen this before?" over incident history and runbooks.

- **Workload**: state (owner, status, severity over time) plus search (similar past incidents). **Bias**: recall at triage, precision for owner and remediation; link state to evidence (P22).
- **R1**: incident and assignment events from the incident tool, applied idempotently by effective time (A39); closed postmortems admitted as verified; live-incident chat is a lower-trust tier and never becomes a root cause by itself.
- **R2**: typed records keyed by stable incident ID; ownership as an assignment row with valid time and a role (incident owner, task owner, and document owner are different fields); symptoms embedded; runbooks as procedures with verification steps.
- **R3**: SQL incident store with P4 columns, a vector column over symptoms, and links to the service graph (scenario 6).
- **R4**: re-validate runbooks when the service version changes; retire remediations for decommissioned components; a stale secondary source (chat topic, old index row) proposes, never overwrites (A38).
- **R5**: as-of questions go to SQL with `valid_from <= t AND (valid_to IS NULL OR t < valid_to)`; similarity search adds time decay and diversity across incident categories (RCACopilot, arXiv 2305.15778, reports recurring incidents clustering close in time).
- **R6**: compute the answer for state questions; for similar incidents show outcome, including fixes that failed.
- **R7**: a triage brief: current owner with its evidence span, top similar incidents with cause and fix, and the current change diff.
- **Default stack**: Postgres (P4 columns, vector, full-text) linked to the service graph. **Upgrade trigger**: a learned similarity model once enough labelled recurrence pairs exist.
- **Acceptance tests**: the "who owns X" exhibit as a regression slice: change at t, then a stale index row, a duplicate event, an out-of-order backfill, a stale secondary source, another object's owner, and a task-owner vs incident-owner question; as-of answers match a replayed event log (scoring in [§4](../../ai-evals/references/retrieval-and-memory-eval.md#4-state-maintenance-scoring)); false-similarity rate (same symptom, different cause).
- **Top failures**: arrival-order application (A39); stale secondary override (A38); role confusion between owner fields; top-k anchored on one category.
- **Depth**: [operational-brain-pattern](operational-brain-pattern.md), [evals-and-operations](evals-and-operations.md#state-maintenance-eval).

## 8. Long-running agent with procedural memory

An agent that learns skills, workflows, or playbooks across many tasks.

- **Workload**: procedural plus episodic memory. **Bias**: precision; a bad skill is reused everywhere.
- **R1**: verification-gated. Prefer an external success signal (tests, environment state) over self-judgement; papers report that removing verification hurts skill libraries and that false-positive self-tests write wrong lessons (Voyager arXiv 2305.16291, Reflexion arXiv 2303.11366).
- **R2**: skills as code or step files with a description for selection; example values abstracted out.
- **R3**: skill library in version control with tests per skill; trajectories in an append-only log.
- **R4**: scheduled, eval-gated consolidation into a new library version (P14, P18 deltas, never rewrites); deprecate skills that stop transferring.
- **R5**: top-k skills by task description plus recent episodes for the same task family.
- **R6**: run the skill's preconditions or tests before use; prefer verified over induced skills.
- **R7**: names and descriptions only; bodies load on demand (P12).
- **Default stack**: git repo of skills and tests, an episode log, and an index over descriptions. **Upgrade trigger**: offline consolidation with an A/B gate once the library changes faster than humans can review it.
- **Acceptance tests**: held-out tasks with and without the library, plus an episodic-only control; transfer across task families; a planted-bad-skill removal test that checks no copies survive ([§6](../../ai-evals/references/retrieval-and-memory-eval.md#6-learned-and-procedural-memory)).
- **Top failures**: self-poisoning and lessons hallucinated from reflections (A26, A31); context collapse from rewrites (A35); victory declaration (A36).
- **Depth**: P15, P18, RA5 in [reference-architectures](reference-architectures.md).

## 9. Voice / realtime

Memory for a spoken agent with a turn-latency budget.

- **Workload**: agent memory under a latency budget. **Bias**: precision with very small k; no room for long contexts or a model reranker on the hot path.
- **R1**: write asynchronously after the turn or after the call; ASR errors mean stored facts carry a confidence and, for anything consequential, a spoken confirmation.
- **R2**: short normalised facts and a compact profile; transcripts as episodes with ASR confidence.
- **R3**: a low-latency store near the media server plus an in-process cache; never cache operational truth (P1).
- **R4**: as scenario 1, plus a correction flow for misheard facts; consolidate after the call.
- **R5**: preload the hot set at session start; prefetch in the background for likely next turns.
- **R6**: precomputed relevance only; play an acknowledgement when a cold lookup is unavoidable.
- **R7**: a small, stable profile block that stays cacheable.
- **Default stack**: RA13 hot/cold split. **Upgrade trigger**: a background prefetch agent when cold lookups show up in turn latency.
- **Acceptance tests**: end-of-turn latency with memory on vs off; recall on spoken-fact probes with ASR noise; correction-flow tests.
- **Top failures**: synchronous chat-style retrieval on every turn (A34); misheard facts stored as true; a semantic cache shared across users.
- **Depth**: the voice memory section of [conversational-surfaces-cross-platform](conversational-surfaces-cross-platform.md#voice-and-realtime-memory), RA13, [ai-voice-bots](../../ai-voice-bots/SKILL.md) for the audio pipeline.

## 10. Analytics over interaction history

"How many users asked about X last month?" is an analytics question, not a memory question.

- **Workload**: analytics. **Bias**: coverage; an aggregate must count everything in scope, and vector top-k silently undercounts.
- **Hand-off**: land every interaction as an append-only event with pseudonymised IDs in a warehouse or event log; model-assigned labels are derived columns carrying the labeller version. The memory engine does not own this data.
- **R5–R6**: SQL over allowlisted views or a semantic layer through a read-only role; show the query and row counts; check aggregates against known totals. The structured leg rules are in [memory-responsibilities-audit](memory-responsibilities-audit.md#5-retrieval).
- **R7**: a result table plus the query and caveats; never raw rows in context.
- **Default stack**: warehouse plus semantic layer plus a text-to-SQL tool ([agents-mcp mcp-for-dwh](../../agents-mcp/references/mcp-for-dwh.md)). **Upgrade trigger**: certified metrics once the same question gets different numbers.
- **Acceptance tests**: text-to-SQL accuracy on your own schema; multi-turn follow-ups that depend on the previous query state; re-run on every model upgrade.
- **Top failures**: counting with vector search; a label-model change shifting trends with no version mark; injected SQL.

## 11. On-device / privacy-first

Memory that stays on the user's device.

- **Workload**: agent memory, local only. **Bias**: precision with a small store.
- **R1**: local by default; no server copy without explicit opt-in; redact before any cloud model call.
- **R2–R3**: compact facts plus episodes in SQLite with full-text and vector extensions and an on-device embedding model; encrypt the database file at rest (P10).
- **R4**: deletion is not erasure. Enable secure delete before deleting, rebuild or merge full-text segments, purge vector rows, and vacuum; destroy per-user keys for backups and sync copies (crypto-shredding).
- **R5–R7**: local hybrid search; send only the selected snippets to any cloud model.
- **Default stack**: [embedded-local-brain](../../ai-vector-brain/references/embedded-local-brain.md). **Upgrade trigger**: end-to-end-encrypted sync when users need the memory on a second device.
- **Acceptance tests**: forensic erasure check (search the database file and its write-ahead log for an erased string); recall at the store size you actually ship.
- **Top failures**: "deleted" text recoverable from free pages, logs, full-text segments, or soft-deleted vectors; unencrypted temp files.
