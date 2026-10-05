# Research Plan

**Research question**: <!-- one-line statement of the falsifiable question -->
**Requested output shape**: <!-- comparison matrix / brief / memo / dossier / source ledger only -->
**Plan created**: <!-- YYYY-MM-DD -->
**Planner**: <!-- human / agent-id -->

---

## Usage

Complete this plan before starting any search or tool call. The planner does not search — it only plans.

Rules:
- Sub-questions must be independently answerable (parallelizable).
- Each query branch has a freshness class — use it to reject out-of-window sources.
- The stop criterion must be defined before the loop starts.
- Share this plan with the searcher, not with the verifier.

---

## Research Question

### Falsifiability Check

State what evidence would change the conclusion:

<!-- e.g., "If vendor X lacks feature Y in official docs dated 2025+, the comparison row for Y will be 'not supported'." -->

### Sub-Questions

1.
2.
3.

---

## Source Targets

| Priority | Source type | Specific targets |
|----------|------------|-----------------|
| 1 | Primary | Official docs, specs, filings, release notes |
| 2 | Secondary | Analyst reports, established press |
| 3 | Secondary | Technical blogs with named authors |
| Excluded | — | AI-generated content farms, SEO aggregators |

---

## Query Branches

### Branch 1: <!-- branch name -->

**Freshness class**: stable / volatile / unknown
**Freshness window** (if volatile): <!-- e.g., "sources must be dated 2025-01-01 or later" -->

Queries:
1.
2.
3.

### Branch 2: <!-- branch name -->

**Freshness class**: stable / volatile / unknown
**Freshness window** (if volatile):

Queries:
1.
2.
3.

<!-- Add branches as needed -->

---

## Stop Criterion

| Field | Value |
|-------|-------|
| **Type** | saturation / hard_cap / coverage_threshold |
| **Saturation window** (if saturation) | <!-- N consecutive iterations with no novel primary sources --> |
| **Max queries** (if hard_cap) | |
| **Min primary sources per branch** (if coverage_threshold) | |
| **Max total queries** | |

---

## Evidence Tier Requirements

| Tier | Required? | Notes |
|------|-----------|-------|
| Primary | Yes | Minimum K per sub-question |
| Secondary | Optional | Supporting context only |
| Model-working-notes | Never as citation | Working use only |

---

## Verifier Scope

Claims to verify (fill after searcher phase):

1.
2.
3.

<!-- The verifier receives this list + the closed SourceLedger only. It does not see this plan. -->

---

## Output Constraints

| Constraint | Value |
|-----------|-------|
| Output shape | comparison matrix / brief / memo / dossier |
| Max synthesis length | |
| Citation style | inline [LEDGER-ID] |
| Date stamps required on volatile claims | yes |
| [UNVERIFIED] markers for unsupported claims | yes |
