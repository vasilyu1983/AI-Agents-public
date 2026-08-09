# Agentic Research Loop Architecture

Reference for the planner / searcher / verifier / synthesizer subagent split. Use this when building a custom research pipeline that must be auditable, repeatable, or integrated into a product workflow.

## Table of Contents

- [Subagent Roles](#subagent-roles)
- [Canonical Contracts](#canonical-contracts)
- [Loop Flow Diagram](#loop-flow-diagram)
- [Session-State Persistence Pattern](#session-state-persistence-pattern)
- [Anti-Patterns This Architecture Blocks](#anti-patterns-this-architecture-blocks)

---

## Subagent Roles

### Planner

**Responsibility**: convert the research question into a structured `ResearchPlan` before any search begins.

**Inputs**: research question, freshness requirements, source preferences, output format.

**Outputs**:
```json
{
  "question": "string",
  "sub_questions": ["string"],
  "query_branches": [
    {"branch": "string", "queries": ["string"], "freshness_class": "stable|volatile|unknown"}
  ],
  "source_targets": ["domain or source type"],
  "stop_criterion": {
    "type": "saturation|hard_cap|coverage_threshold",
    "saturation_window": 3,
    "max_queries": 30,
    "min_primary_sources_per_branch": 2
  },
  "evidence_tiers_required": ["primary", "secondary"]
}
```

**Key rule**: the planner does not search. It only plans. This separation prevents early search results from framing the plan.

---

### Searcher

**Responsibility**: execute the query branches from the plan; record every source in the ledger before any synthesis.

**Inputs**: `ResearchPlan` from the planner.

**Outputs**: appended rows to the `SourceLedger` (see contract below).

**Key rules**:
- Write to the ledger immediately on each retrieval — do not batch.
- Tag every entry with `evidence_tier` (`primary` / `secondary` / `model-working-notes`).
- Flag suspicious sources rather than silently discarding them (P9).
- Check the stop criterion after each iteration.
- Do not synthesize or summarize findings — working notes in the ledger are the most the searcher emits.

**Multiple searchers**: in a swarm (P3), multiple searcher agents run in parallel, each writing to the same shared ledger. The planner assigns non-overlapping query branches to prevent duplicate work.

---

### Verifier

**Responsibility**: independently check that each claim in the draft synthesis is supported by a specific ledger entry.

**Context isolation rule (critical)**: the verifier must not have access to the search session, browser history, searcher scratchpad, or planner context. It receives:
1. The finalized `SourceLedger` JSONL.
2. The list of claims to verify (extracted from the draft synthesis).

**Outputs**: a `VerifierReport` per claim:
```json
{
  "claim": "string",
  "verdict": "supported|unsupported|inconclusive",
  "ledger_id": "string or null",
  "supporting_quote": "string or null",
  "notes": "string"
}
```

**Unsupported claims**: surface to the synthesizer as `[UNVERIFIED]`; do not silently drop or auto-correct.

---

### Synthesizer

**Responsibility**: produce the final output artifact from the finalized, verified ledger.

**Inputs**: finalized `SourceLedger`, `VerifierReport`, requested output shape.

**Key rules**:
- Only synthesize after the research loop has reached its stop criterion (P10).
- Every factual sentence carries a `[LEDGER-ID]` citation back-pointer (P7).
- Claims marked `[UNVERIFIED]` by the verifier are either dropped or explicitly flagged in the output.
- Keep working notes, ledger, and final synthesis as separate artifacts (P1, P12).

---

## Canonical Contracts

### SourceLedger Row (JSONL)

```json
{
  "id": "L001",
  "url": "https://...",
  "title": "string",
  "author": "string or null",
  "date_published": "YYYY-MM-DD or null",
  "date_accessed": "YYYY-MM-DD",
  "evidence_tier": "primary|secondary|model-working-notes",
  "freshness_class": "stable|volatile|unknown",
  "branch": "branch name from plan",
  "supporting_quote": "exact extracted text",
  "confidence": "high|medium|low",
  "hostile_source_flags": [],
  "notes": "string"
}
```

### ResearchPlan (JSON)

See planner outputs section above.

### VerifierReport (JSONL)

See verifier outputs section above.

### SynthesisArtifact (Markdown)

Prose synthesis with:
- Section headers matching sub-questions from the plan.
- Inline `[LEDGER-ID]` citations on every factual claim.
- Explicit `[UNVERIFIED]` markers from the verifier report.
- Trailing section: "Open Questions and Confidence Gaps."
- Trailing section: "Evidence Freshness Summary" with date anchors per volatile claim.

---

## Loop Flow Diagram

```
User question
    │
    ▼
Planner → ResearchPlan (written to disk)
    │
    ▼
Searcher(s) → SourceLedger rows (appended after each retrieval)
    │
    ├── Stop criterion met? No → next iteration
    │
    └── Yes
    │
    ▼
Verifier (reads only SourceLedger + claim list)
    │
    ▼
Synthesizer (reads SourceLedger + VerifierReport)
    │
    ▼
SynthesisArtifact + archived SourceLedger
```

---

## Session-State Persistence Pattern

Agentic research loops are interrupted by context resets, model switches, and API timeouts. Resilience rule: **every subagent persists its output to disk before yielding control**.

- Planner writes `research-plan.json` before starting the searcher.
- Searcher appends to `source-ledger.jsonl` after each tool call — not at the end of the session.
- Verifier writes `verifier-report.jsonl` before returning.
- Synthesizer writes `synthesis-draft.md` before requesting review.

On resume: reload from the last persisted artifact, not from conversation context. This prevents the S2S session-state loss trap described in the Known Traps section of SKILL.md.

---

## Anti-Patterns This Architecture Blocks

| Anti-pattern | Where blocked |
|-------------|---------------|
| A1 Pre-synthesizing the answer | Planner/Searcher phase separation |
| A2 Single-pass search | Iterative loop with stop criterion |
| A5 Unbounded loop | Stop criterion defined in ResearchPlan |
| A7 Verifier-with-same-context | Verifier context isolation rule |
| A10 Retrofitting citations | Ledger written before synthesis |
| A12 Storing evidence with synthesis | Separate artifact rule |
