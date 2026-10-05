# Example Assessments

## Table of Contents

- [Pattern A: Intelligence System](#pattern-a-intelligence-system)
- [Pattern B: Personalization Runtime](#pattern-b-personalization-runtime)
- [Pattern C: Pure Vector RAG](#pattern-c-pure-vector-rag)
- [Pattern D: Living Knowledge Base For Agents](#pattern-d-living-knowledge-base-for-agents)
- [Pattern E: Personal AI Cross-Session Memory](#pattern-e-personal-ai-cross-session-memory)
- [Pattern F: Regulated Compliance-Aware Memory](#pattern-f-regulated-compliance-aware-memory)

## Pattern A: Intelligence System

Signals:

- org-scoped unified read model
- brand or domain analysis snapshots
- recommendation history with outcomes
- action graph or workflow loop

Assessment:

- close to a modern context layer if it still separates operational truth, memory, retrieval, and action feedback
- weaker if "graph" is only a label and no explicit relationship layer exists

## Pattern B: Personalization Runtime

Signals:

- shared profile builder
- deterministic signals across many surfaces
- scoped projection into LLM prompts
- policy and entitlement gating

Assessment:

- strong personalization runtime
- not yet a full app context layer unless it also adds durable memory, evidence-bearing retrieval, and optional relationship context

## Pattern C: Pure Vector RAG

Signals:

- embeddings everywhere
- little separation between live facts and retrieved text
- prompt stuffing replaces explicit context assembly

Assessment:

- useful retrieval subsystem
- weak overall app context architecture

## Pattern D: Living Knowledge Base For Agents

Corresponds to recipe RA1 in `reference-architectures.md`. The problem shape
a practitioner request for a reviewable living knowledge base described by name.

Signals:

- org- or tenant-scoped knowledge store that grows as sources arrive
- agents write into it, not only read from it
- supersession and contradictions are first-class events, not admin actions
- reviewers inspect, correct, and approve derived claims
- UI exposes graph, page, source trace, and confidence
- pages are human-readable markdown with wikilinks, not opaque vector blobs

Assessment:

- **strong** when: operational truth is separated from derived knowledge,
  every claim carries `source_episode_id`, bi-temporal validity and
  non-destructive invalidation wired end-to-end, and at least the minimum
  viable review surface ships (graph + page + source trace). Pattern IDs
  present: P7, P4, P2, P9. Anti-patterns blocked at minimum: A1, A4, A13,
  A14, A16, A17.
- **partial** when: the wiki exists and is reviewable but contradictions
  surface only at query time (A4 present) or confidence is a static number
  with no decay (A14 partial).
- **weak** when: the "wiki" is a vector index with a markdown skin — no
  extraction pipeline (A16), no ingest-time contradiction detection (A4),
  no traceable provenance (A13). The label is wiki; the architecture is
  Pattern C.

## Pattern E: Personal AI Cross-Session Memory

Corresponds to recipe RA2. Personal assistant, single user, long-lived.

Signals:

- bounded core memory block the agent edits itself
- structured preferences and declared facts separate from the agent's block
- personal corpus queried with citations
- calendar, tasks, health, and billing stay in tools, not in memory
- optional minimal "memory page" UI for the user to see and edit what the
  agent remembers

Assessment:

- **strong** when: P3 (self-editing block) + P2 (app-owned prefs the agent
  cannot silently overwrite) + P8 (corpus retrieval with evidence). Forget
  path exists (A11 blocked). Cross-session facts survive agent restart.
- **partial** when: memory exists but is raw chat turns (A1 present) or
  every recall re-runs retrieval with no extraction (A16 present).
- **weak** when: "memory" is the recent chat history, preferences live in
  prompt text, and the agent cannot survive a session boundary.

## Pattern F: Regulated Compliance-Aware Memory

Corresponds to recipe RA4. Financial advice, health, legal, or similar.

Signals:

- explicit audit log on every `remember / forget / improve` call
- bi-temporal tracking with both real-world validity and system knowledge time
- reviewer role gating on production writes (staging → approved → readable)
- distinct deletion path for DSAR / GDPR that preserves audit shape
- point-in-time queries are a first-class product feature, not a debugging tool

Assessment:

- **strong** when: RA4 recipe implemented end-to-end. Every fact carries
  `valid_from / valid_to / recorded_at / superseded_at / supersedes_id /
  consent_basis`. Review surface mandatory. Anti-patterns blocked: A3, A7,
  A10, A11, A13, A17.
- **partial** when: bi-temporal is present but deletion uses the same code
  path as normal forget (A7 risk), or the review surface is ops-only with
  no role gating.
- **weak** when: facts can be hard-deleted (A3, A7), no episode provenance
  (A13), no role-gated approval. This is a regulatory failure mode, not an
  architecture preference.
