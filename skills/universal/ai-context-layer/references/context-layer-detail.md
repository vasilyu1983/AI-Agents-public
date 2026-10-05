# Context Layer — Architecture, Contracts, Workflow, Defaults, Traps

## Table of Contents

- [Architecture Model](#architecture-model)
- [Default Choice Framework](#default-choice-framework)
- [Canonical Contracts](#canonical-contracts)
- [Review Workflow](#review-workflow)
- [Operational Defaults](#operational-defaults)
- [Known Traps](#known-traps)
- [Common Anti-Patterns](#common-anti-patterns)


## Architecture Model

```text
App Context Layer
  ├─ Entity/Profile Layer
  │   └─ user, org, brand, account, product, domain entities
  ├─ Memory Layer
  │   └─ preferences, learned facts, action history, outcomes
  ├─ Retrieval/Grounding Layer
  │   └─ docs, sites, KBs, search indexes, file search
  ├─ Relationship/Graph Layer
  │   └─ entity links, ownership, dependencies, influence paths
  ├─ Context Assembly Layer
  │   ├─ per-surface bundles, latency budgets, allowlists
  │   └─ emotional context: mood signals, tone modulation, emotional framing
  ├─ Cross-Surface Signal Flow
  │   └─ mood/energy from journaling → chat, decisions from dashboard → ask, feedback → memory confidence
  ├─ Feedback Layer
  │   ├─ corrections, execution results, reuse scoring, drift checks
  │   └─ inline reactions tied to context bundle IDs
  └─ Review & Inspection Layer (mandatory when KB is user-visible)
      ├─ graph view, page view, source trace
      ├─ contradiction queue (attribution / temporal / stale)
      ├─ confidence / provenance view
      └─ editorial approval workflow with staging
```

See `references/inspection-and-review-surfaces.md` for surface details and
`references/patterns-catalog.md` for the P9 composition.

## Default Choice Framework

Keyed on *problem shape*, not "need". Pattern IDs map to
`references/patterns-catalog.md`.

| Problem shape | Pattern pick | Use when | Avoid when |
|---------------|--------------|----------|------------|
| Live user / org / billing state | P1 Operational-truth-first | Facts must be current and scoped | Data is prose corpora |
| Durable learned preferences | P2 Structured memory classes | Facts persist across sessions and need audit | One-turn ephemeral state is enough |
| Long-running agent with own memory | P3 Self-editing memory blocks | Agent must maintain persona and facts across many sessions | Memory is app-orchestrated, not agent-owned |
| Relationships change over time | P4 Temporal knowledge graph | Bi-temporal validity, non-destructive invalidation, contradiction tracking | SQL joins or retrieval already solve it |
| Heterogeneous data, one API | P5 Ontology-grounded poly-store | Typed entities across graph + vector + relational | You need only one store type |
| User-scoped conversational memory | P6 Episodic + semantic dual-store | Extract atomic facts from dialogue per user | Facts are app-declared, not dialogue-derived |
| Human-reviewable compiled knowledge | P7 LLM Wiki / knowledge compilation | Product needs a wiki humans read and review | Consumer is an LLM only |
| Corpus retrieval with citations | P8 Evidence-bearing hybrid retrieval | Prose corpus, changes independently of OLTP | Answer depends on live billing / entitlement |
| Inspectable living KB | P9 Composed review surface (P4+P7+UI) | KB is user-visible, contradictions matter, reviewers act | Internal-only, single consumer, no audit need |
| Sovereign / offline memory | P10 Self-hosted local-first memory | Data gravity or sovereignty blocks managed services | Managed services are acceptable |
| Long-horizon sub-task inflates parent window | P11 Sub-agent context isolation | Bounded sub-task needs its own context (search, synthesis, analysis) | Sub-task fits in parent window without distraction risk |
| Surface-specific personalization | Context assembly bundles | Web, email, dashboard, chat need different slices | One monolithic prompt is sufficient |
| Outcome learning | Feedback and outcome store | Actions and recommendations should improve over time | No learning loop is required |

Compose multiple rows when the problem shape spans layers (e.g., P1+P4+P7+P9
for a living enterprise KB — see `reference-architectures.md` RA1).

## Canonical Contracts

Model your design around these contracts:

- `EntityProfile`
  Stable entity record for a user, customer, org, brand, or domain object.
- `LearnedMemory`
  Derived fact or preference with `source`, `confidence`, `ttl`, `updated_at`, and owner scope.
- `KnowledgeSource`
  Registry entry for a live API, database table, site crawl, document set, or index.
- `RetrievalResult`
  Evidence-bearing result with chunk/page IDs, source refs, freshness, and ACL metadata.
- `ContextAssemblyRequest`
  Input that names `surface`, `actor`, `org`, `task`, `latency_budget`, and required trust level.
- `ContextBundle`
  Output slices such as `live_facts`, `memory`, `domain_evidence`, `relationship_context`, and `guardrails`.
- `FeedbackOutcome`
  Correction or execution result that can update derived memory or reuse scoring.

### Memory Lifecycle Verbs

Name the lifecycle explicitly with four verbs, each with its own contract and owner:

- `remember(input)` — ingest raw episode → extract → write derived facts with `source_episode_id`, confidence, and validity window
- `recall(query)` — retrieve from any layer (live, memory, retrieval, graph) with evidence IDs intact
- `forget(target)` — **invalidate** (close `valid_to`, set `superseded_at`) rather than hard-delete; delete only for compliance/GDPR paths
- `improve(feedback)` — drive `FeedbackOutcome` back into confidence, reuse scoring, and contradiction resolution

Forgetting is a first-class verb, not an admin operation. Without it, the memory layer either accumulates contradictions or deletes history.

<!-- Source: github.com/topoteretes/cognee@961c3ca4784686390d89d7c45cef63ed2e8da6a1 (Apache-2.0), extracted 2026-04-15 -->

See the templates in `assets/contracts/`.

## Review Workflow

1. Identify the primary entities and source-of-truth systems.
2. Separate operational truth from derived memory.
3. Classify each knowledge source: tool/API, SQL, retrieval corpus, graph, or cache.
4. **Select named patterns** from `references/patterns-catalog.md` (P1–P25) or a
   composed recipe from `references/reference-architectures.md` (RA1–RA13). The
   design must cite pattern IDs; ad-hoc designs are not complete.
5. Check whether graph usage is justified or just fashionable.
6. Inspect context assembly per surface:
   - what is always present
   - what is retrieved on demand
   - what is excluded by policy
7. **Run the context-hygiene check (F1–F5)** against each surface bundle —
   poisoning, distraction, clash, confusion (F1–F4, Breunig canonical), plus
   proactive interference (F5). Each failure mode must have a documented
   defense. See `references/context-hygiene.md`.
8. Inspect grounding:
   - provenance
   - freshness
   - ACL/tenant scope
   - evidence IDs
   - refusal behavior on missing evidence
9. **Inspect contradiction handling** — name the category for each contradiction
   path:
   - **attribution** (same claim, different sources)
   - **temporal** (new value invalidates the old)
   - **stale** (fact is past its validity window)
   Each category must have an ingest-time detection path and a visible
   resolution action.
10. **Check sub-agent isolation (P11)** — does any long-horizon sub-task
    (search, synthesis, deep analysis) run in the parent's context window when
    it would double the parent's budget? If yes, split into a sub-agent with a
    defined handoff contract. See `references/context-hygiene.md` §Sub-agent
    isolation recipe.
11. Inspect the learning loop:
    - corrections
    - action outcomes
    - inline reactions tied to context bundle IDs
    - reuse scoring
    - stale-memory invalidation
12. **Inspect the Review & Inspection Layer** when the KB is user-visible:
    graph view, page view, source trace, contradiction queue, confidence view,
    editorial approval. See `references/inspection-and-review-surfaces.md`.
13. Inspect emotional context:
    - does the system capture mood/emotional state?
    - does tone modulate based on user state?
    - is context metadata presented as warm narrative or raw metrics?
    - do signals flow across surfaces (e.g., journaling mood → chat)?
14. **Run the anti-pattern sweep** from `references/anti-patterns-catalog.md`.
    Every applicable anti-pattern must be either `BLOCKED by <pattern ID>` or
    `NOT BLOCKED (accepted: <justification>)`. The sweep includes A1–A49.
15. **Run the security threat-model review** — indirect prompt injection,
    memory poisoning, tool-description injection, cross-tenant leakage, PII
    paths, feedback-loop abuse, exfiltration via tool output. See
    `references/security-threat-model.md`.
16. Score the system against the context-layer scorecard in
    `assets/eval/context-layer-scorecard.md`.

## Operational Defaults

**Do**

- Keep user and org state in operational stores and fetch it live.
- Make memory explicit, structured, and auditable.
- Treat retrieval as an evidence system, not as hidden prompt stuffing.
- Add graph only when entity relationships materially change the answer.
- Use per-surface context bundles with strict allowlists and bounded budgets.
- Run retrieval and answer quality evals separately.
- Track stale context, missing evidence, and tenant leakage as first-class failures.
- Capture emotional state as an explicit context signal, not an afterthought.
- Present context metadata as warm narrative for end users; collapse raw metrics for power users.
- Design inline feedback that ties to context bundle IDs, not general satisfaction ratings.
- Enable cross-surface signal flow so that state captured on one surface enriches others.
- **Name the pattern(s)** used, from `references/patterns-catalog.md`, and
  record the anti-patterns explicitly blocked from `references/anti-patterns-catalog.md`.
  A design without pattern IDs and a sweep is not complete.

**Avoid**

- Copying operational truth into embeddings and then treating the index as the system of record.
- Treating raw chat history as durable memory.
- Assuming personalization and retrieval are the same subsystem.
- Building GraphRAG without proving that graph traversal beats SQL or hybrid retrieval.
- Sending the full internal state into an LLM when a smaller derived projection will do.
- Exposing raw context metrics (trust levels, coverage scores) to end users — use emotional framing instead.
- Treating AI tone as static brand voice when the system has mood/energy signals available.
- Showing feedback buttons on every surface from day one — start with the highest-value surface and expand after validating.

## Known Traps

- operational truth copied into memory or retrieval caches and later trusted more than the source system
- context bundles assembled without surface-specific budgets, ACL filters, or freshness checks
- derived signals flowing across surfaces with no confidence model, deletion path, or owner
- emotional context treated as durable fact rather than a bounded presentation or interaction signal
- graph, vector, and memory layers all added at once so failures cannot be localized

## Common Anti-Patterns

Top seven. Full catalog with detection signals and replacement pattern IDs in
`references/anti-patterns-catalog.md` (A1–A49). The sweep in step 14 of the
Review Workflow is mandatory.

**Storage-layer top of mind:**

- **A8** — one monolithic personalization store for profile, memory, retrieval, and feedback
- **A2** — vector search used to answer structured entity or SQL questions
- **A1** — transcript logging mistaken for a usable memory layer
- **A17** — cross-surface personalization with no inspection or correction UI
- **A5** — context assembly that cannot explain why a fact appeared in the bundle

**Runtime / security top of mind:**

- **A19** — context poisoning: wrong facts compound across turns
- **A23** — indirect prompt injection via retrieved or remembered content
