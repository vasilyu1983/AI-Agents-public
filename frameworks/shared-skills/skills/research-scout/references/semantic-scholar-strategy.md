# Semantic Scholar Strategy

> **API-key restriction (2026):** New keys are no longer approved for free email domains (gmail, outlook, etc.). Existing keys are unaffected. If you only have a free-domain email, plan around the anonymous shared pool or use [OpenAlex](https://openalex.org/) as an alternative — note OpenAlex is **not** keyless either (a free key has been mandatory there since 2026-02-13), it just has no email-domain restriction. See [Rate Limits](#rate-limits-verified-jul-2026) for full detail.

## Table of Contents

- [Discovery Path](#discovery-path)
- [Query Patterns](#query-patterns)
- [Citation-Velocity Thresholds](#citation-velocity-thresholds)
- [Credibility Signals](#credibility-signals)
- [Biases](#biases)
- [Rate Limits](#rate-limits-verified-jul-2026)

## Discovery Path

Semantic Scholar's strength is the **citation graph** — finding what built on a paper, what's similar, and which papers are influential.

1. **Search**: `https://api.semanticscholar.org/graph/v1/paper/search?query={{query}}&limit=50`
2. **Paper details**: `https://api.semanticscholar.org/graph/v1/paper/{{paperId}}` (S2 ID, DOI, arXiv ID, etc.)
3. **Citations / references**: `.../paper/{{paperId}}/citations` and `.../paper/{{paperId}}/references`
4. **Recommendations**: `https://api.semanticscholar.org/recommendations/v1/papers/forpaper/{{paperId}}`
5. **Bulk via OpenAlex**: complementary catalog at https://openalex.org/ for cross-checking (free API key mandatory since 2026-02-13 — register at openalex.org/settings/api).

## Query Patterns

```text
# Search recent influential papers on a topic
GET /graph/v1/paper/search
  ?query=retrieval+augmented+generation+evaluation
  &limit=50
  &fields=title,authors,year,citationCount,influentialCitationCount,externalIds,url

# Citations of a known paper (who built on it?)
GET /graph/v1/paper/{{S2_ID}}/citations
  ?fields=title,year,citationCount,intent
  &limit=100

# Paper recommendations
GET /recommendations/v1/papers/forpaper/{{S2_ID}}?limit=20
```

**Key fields:**
- `citationCount` — total citations
- `influentialCitationCount` — S2's filter for "meaningfully cited"; better signal than raw count
- `externalIds.ArXiv` — arXiv ID if applicable
- `intent` (on citations) — `methodology`, `result`, `background`; use to filter by relevance

## Citation-Velocity Thresholds

Prefer **citations-per-month-since-publication** over raw counts to avoid penalising recent papers.

| Temporal bucket | Operational threshold |
| --- | --- |
| **Emerging** | First `influentialCitationCount` citations appear within 90 days of publication AND the monthly rate is accelerating (month-over-month increase ≥ 1 influential citation) |
| **Cresting** | > 10 influential citations in the last 60 days; mentions accelerating across arXiv, HF Papers, and curator sources |
| **Mature** | Stable influential-citation rate over 90d–365d; ≥ 2 independent implementations exist |
| **Declining** | Influential-citation rate falling for 2+ consecutive 30-day windows; investigate successor methods |

Use the `/paper/{{id}}/citations` endpoint with `fields=year,influentialCitationCount,intent` and bin by `publicationDate` to compute the monthly rate. Raw `citationCount` is a lagging, gameable proxy — always prefer `influentialCitationCount` for velocity calculations.

## Credibility Signals

- **`influentialCitationCount` ≥ 3 within 12 months** — strong corroboration that the method is being applied, not just cited politely.
- **Multi-institutional citing graph** — methods cited by multiple institutions are more transferable than methods cited only by the original lab.
- **Citing-paper recency** — sustained citations across 12-24 months > burst-then-die.
- **Methodology-intent citations** — `intent=methodology` is the strongest steal signal (others use the method).

## Biases

- **CS / ML over-coverage**, classics like physics or biology under-coverage relative to topic.
- **Citation lag.** Recent papers (last 6 months) have artificially low citation counts.
- **English-language bias** in indexing.
- **Citation gaming** — high citation counts can reflect controversy as much as quality. Read the citing-paper intents to disambiguate.

## Rate Limits (verified Jul 2026)

- Unauthenticated: a **shared** pool (~5,000 req / 5 min across *all* anonymous
  users) — effective throughput is unpredictable; treat as best-effort.
- Authenticated: **new keys are issued at 1 req/sec on all endpoints** (higher
  tiers only after manual review). The old "~10 req/sec with key" no longer holds.
- **Exponential backoff is now required**, not optional — the API returns 429s
  under shared-pool contention even below the documented limit. Scripts must
  retry with backoff, not fail hard.
- **Key requests from free email domains (gmail/outlook/etc.) are no longer
  approved** due to limited resources. Existing keys are unaffected. If you only
  have a free-domain email, plan around the anonymous shared pool, or fall back
  to **OpenAlex** (https://openalex.org/) which has no email-domain restriction
  — but still requires its own free API key for every request (mandatory since
  2026-02-13; register at openalex.org/settings/api). "No restriction" means no
  domain gate, not no key.
- Apply for a key at https://www.semanticscholar.org/product/api (institutional
  email) if scanning at scale.
- Scripts in this skill default to 1 req/sec + exponential backoff to stay under
  the public limit.
