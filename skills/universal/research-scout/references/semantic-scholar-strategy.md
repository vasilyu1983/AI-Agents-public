# Semantic Scholar Strategy

## Table of Contents

- [Discovery Path](#discovery-path)
- [Query Patterns](#query-patterns)
- [Citation-Velocity Thresholds](#citation-velocity-thresholds)
- [Credibility Signals](#credibility-signals)
- [Biases](#biases)
- [Rate Limits](#rate-limits)

## Discovery Path

Semantic Scholar's strength is the **citation graph** — finding what built on a paper, what's similar, and which papers are influential.

1. **Search**: `https://api.semanticscholar.org/graph/v1/paper/search?query={{query}}&limit=50`
2. **Paper details**: `https://api.semanticscholar.org/graph/v1/paper/{{paperId}}` (S2 ID, DOI, arXiv ID, etc.)
3. **Citations / references**: `.../paper/{{paperId}}/citations` and `.../paper/{{paperId}}/references`
4. **Recommendations**: `https://api.semanticscholar.org/recommendations/v1/papers/forpaper/{{paperId}}`
5. **Bulk via OpenAlex:** basic keyless access is available; register a free key for larger budgets. See [Rate Limits](#rate-limits) below for the lookup step.

## Query Patterns

```text
# Search recent influential papers on a topic
GET /graph/v1/paper/search
  ?query=retrieval+augmented+generation+evaluation
  &limit=50
  &fields=title,authors,year,citationCount,influentialCitationCount,externalIds,url

# Citations of a known paper (who built on it?)
GET /graph/v1/paper/{{S2_ID}}/citations
  ?fields=title,year,citationCount,intents,isInfluential
  &limit=100

# Paper recommendations
GET /recommendations/v1/papers/forpaper/{{S2_ID}}?limit=20
```

**Key fields:**
- `citationCount` — total citations
- `influentialCitationCount` — S2's filter for "meaningfully cited"; better signal than raw count
- `externalIds.ArXiv` — arXiv ID if applicable
- `intents` (on citations and references) — a list per citation, for example `["methodology"]`; the field is plural (`fields=intent` returns HTTP 400). Filter client-side; the value vocabulary is documented at https://www.semanticscholar.org/faq#citation-intent, and `isInfluential` is the per-citation boolean behind `influentialCitationCount`

## Citation-Velocity Thresholds

Prefer **citations-per-month-since-publication** over raw counts to avoid penalising recent papers.

The numbers below are starting heuristics, not evidence thresholds: they were not derived from a measured baseline. Before using them, sample a few methods you already consider mature and emerging in your field, compute the same rates, and move the cut-offs to match; citation rates differ by an order of magnitude between subfields.

| Temporal bucket | Starting heuristic (calibrate per field) |
| --- | --- |
| **Emerging** | First `influentialCitationCount` citations appear within 90 days of publication AND the monthly rate is accelerating (month-over-month increase ≥ 1 influential citation) |
| **Cresting** | > 10 influential citations in the last 60 days; mentions accelerating across arXiv, HF Papers, and curator sources |
| **Mature** | Stable influential-citation rate over 90d–365d; ≥ 2 independent implementations exist |
| **Declining** | Influential-citation rate falling for 2+ consecutive 30-day windows; investigate successor methods |

Use the `/paper/{{id}}/citations` endpoint with `fields=citingPaper.publicationDate,citingPaper.year,isInfluential,intents` and bin by `citingPaper.publicationDate` to compute the monthly rate. Citing-paper attributes are nested under `citingPaper` in each `data` item and must be requested with that prefix (the API docs: "Request fields nested within `citingPaper` the same way as fields like `contexts`"); a bare `year` or `publicationDate` in `fields` returns nothing to bin on. `publicationDate` can be null for some records; fall back to `citingPaper.year` for those. Raw `citationCount` is a lagging, gameable proxy — always prefer `influentialCitationCount` for velocity calculations.

## Credibility Signals

- **`influentialCitationCount` ≥ 3 within 12 months** (starting heuristic; calibrate against your field's baseline as above) — a sign that the method is being applied, not just cited politely.
- **Multi-institutional citing graph** — methods cited by multiple institutions are more transferable than methods cited only by the original lab.
- **Citing-paper recency** — sustained citations across 12-24 months > burst-then-die.
- **Methodology-intent citations** — a citation whose `intents` list contains `methodology` is the strongest steal signal (others use the method).

## Biases

- **CS / ML over-coverage**, classics like physics or biology under-coverage relative to topic.
- **Citation lag.** Recent papers (last 6 months) have artificially low citation counts.
- **English-language bias** in indexing.
- **Citation gaming** — high citation counts can reflect controversy as much as quality. Read the citing-paper intents to disambiguate.

## Rate Limits

Semantic Scholar's limits, key tiers, and key-eligibility rules change. Before a scan at scale:

1. Read the current unauthenticated limit, keyed limit, and key-eligibility rules at https://www.semanticscholar.org/product/api.
2. Treat the unauthenticated pool as best-effort: it is shared, so throughput is unpredictable.
3. Retry on HTTP 429 with exponential backoff and a capped wait; never treat a throttled empty page as "no results".
4. If you cannot get a key, plan around the shared pool or fall back to OpenAlex (check its current allowances at https://help.openalex.org/api/authentication/).
- Query generators emit URLs; they do not execute requests or enforce backoff. The fetching agent must apply current operator limits.
