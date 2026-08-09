# Source Ledger

**Research question**: <!-- one-line statement of the falsifiable question being researched -->
**Plan reference**: <!-- path to research-plan.json -->
**Research start**: <!-- YYYY-MM-DD -->
**Ledger status**: <!-- open | closed (closed after stop criterion is met) -->

---

## Usage

This ledger is the primary artifact of any research task. Synthesis is produced only after this ledger is closed (stop criterion met) and verified.

Rules:
- Add rows immediately on retrieval — do not batch at end of session.
- Every row must have: `id`, `url`, `title`, `date_accessed`, `evidence_tier`.
- Never place model-generated summaries in `evidence_tier: primary`.
- Close the ledger explicitly before starting synthesis.

The JSONL version (`source-ledger.jsonl`) is the machine-readable canonical form. This markdown template is for human review.

---

## Evidence Tier Key

| Tier | Description | Examples |
|------|-------------|---------|
| `primary` | Original document; no intermediary | Official docs, filings, specs, release notes, primary research papers |
| `secondary` | Commentary, summary, or interpretation of a primary | Blog posts, news articles, analyst reports |
| `model-working-notes` | LLM-generated summaries or extracted text | Notes from this session; never cite as source |

---

## Ledger Entries

### L001

| Field | Value |
|-------|-------|
| **ID** | L001 |
| **URL** | |
| **Title** | |
| **Author** | |
| **Date published** | |
| **Date accessed** | |
| **Evidence tier** | primary / secondary / model-working-notes |
| **Freshness class** | stable / volatile / unknown |
| **Branch** | <!-- query branch from the research plan --> |
| **Supporting quote** | <!-- exact extracted text, max 3–4 sentences --> |
| **Confidence** | high / medium / low |
| **Hostile source flags** | <!-- empty, or list of detected signals --> |
| **Notes** | |

---

<!-- Duplicate the L001 block for each additional source -->

---

## Stop Criterion Check

| Check | Status |
|-------|--------|
| Stop criterion type | saturation / hard_cap / coverage_threshold |
| Criterion met? | yes / no |
| Date closed | |
| Total sources | |
| Primary sources | |
| Secondary sources | |
| Flagged / quarantined | |

---

## Open Questions and Confidence Gaps

<!-- List claims that could not be verified, areas with insufficient primary sources, and topics requiring follow-up. -->

1.
2.
3.
