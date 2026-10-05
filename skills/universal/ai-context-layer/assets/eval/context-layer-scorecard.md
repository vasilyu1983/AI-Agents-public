# Context Layer Scorecard

Score each item `0`, `1`, or `2`.

## Operational Truth

- Live user/customer facts fetched from source-of-truth systems
- Tenant and ACL boundaries explicit

## Memory

- Structured memory exists
- Memory has provenance, confidence, and expiry

## Retrieval

- Retrieval has evidence IDs and freshness
- Retrieval and answer quality are evaluated separately

## Graph

- Graph use is justified by the problem
- Inferred edges are separated from operational edges
- Temporal validity and fact expiry are defined for graph edges

## Context Assembly

- Per-surface bundles are explicit
- Model projection is bounded and allowlisted
- Context compression and token budget management are explicit
- Pointer-first refs used for large or tool-rich surfaces before loading payloads
- Managed memory or hosted retrieval boundaries are explicit (truth, audit, delete)
- Multimodal artifacts use typed projections rather than raw payload stuffing

## Emotional Context

- Emotional/mood signals captured and passed to context assembly
- AI responses modulate tone based on user state (not just static brand voice)
- Context metadata presented as warm narrative (emotional frame), not raw metrics
- Cross-surface signal flow exists (e.g., journaling mood → chat context)

## Feedback

- Corrections and outcomes are captured
- Learning loop improves derived context without overwriting truth
- Inline reactions tied to context bundle IDs (not just general satisfaction)
- Feedback fatigue managed (limited surfaces, one-shot per response)

## Pattern Selection And Sweep

- Design cites named pattern IDs from `references/patterns-catalog.md` (P1–P25)
- Anti-pattern sweep run against `references/anti-patterns-catalog.md` (A1–A49)
- Each applicable anti-pattern marked `BLOCKED by <pattern>` or `NOT BLOCKED (accepted: ...)`
- Contradictions categorized as attribution / temporal / stale with ingest-time detection

## Knowledge Compilation (P7 designs only)

- Extract → reconcile → supersede pipeline runs at ingest, not at query time
- Every claim tagged `extracted | inferred | ambiguous` with `source_episode_id`
- Confidence decays with time and strengthens with reinforcement
- Recurring queries hit compiled synthesis pages, not re-run retrieval end-to-end

## Review & Inspection Surface

- Every fact can be traced to a raw source episode in ≤3 actions
- Per-fact confidence is visible to operators
- Contradictions appear in a queue grouped by category, not only as page flags
- Approve / reject / supersede workflow exists (staging → production) when the KB is user-visible
- Ingest-time contradiction detection confirmed (not query-time)
- Forget path is non-destructive (closes validity window; hard delete reserved for compliance)

## Context Window Hygiene

- F1 context poisoning has a documented defense (provenance + confidence + invalidation)
- F2 context distraction has a documented defense (token-budget cap + history compaction)
- F3 context clash has a documented defense (ingest-time contradiction detection + per-surface tool allowlist)
- F4 context confusion has a documented defense (just-in-time selection + surface-tuned tool allowlist)
- Runtime verbs `write / select / compress / isolate` are explicitly assigned to an assembly-layer component
- Runtime refs resolve only on demand and preserve provenance after expansion
- Tool-result compaction recipe wired into the agent loop (A24 blocked)

## Sub-Agent Isolation

- Long-horizon sub-tasks use P11 sub-agents rather than the parent window
- Sub-agent handoff contract defined (task brief, tool allowlist, output schema, token budget)
- Sub-agent summary preserves citations or episode IDs so the parent can re-fetch detail

## Security

- Token-origin tagging in the system prompt distinguishes instructions from data (A23 blocked)
- Tool allowlists are per-surface, not global
- Adversarial / injection corpus runs in evals and gates release
- PII scrubbing runs before embed and before log
- Destructive or external-effect tools require explicit confirmation
- Cross-tenant smoke tests pass at storage layer, not only at query layer

## State Maintenance

- Current state rows link to supporting evidence spans (P22)
- Section-level scope and sensitivity filters apply inside each retrieval leg before fusion (P23, P24)
- Tombstones cascade to derived indexes, graph, and observations (A40 blocked)
- State-maintenance eval covers update, rename, relationship change, deletion, supersession, as-of, duplicate and out-of-order events, stale secondary sources, role confusion, and scope leakage

## Interpretation

Total items: 57. Max score: 114.

- `0-29`: fragmented context system
- `30-49`: solid partial context layer
- `50-73`: strong context-layer architecture with named patterns, basic hygiene, and feedback
- `74-114`: complete context layer — storage patterns, runtime hygiene, pointer-first loading, managed-memory boundaries, sub-agent isolation, security threat model, state maintenance, and full review surface
