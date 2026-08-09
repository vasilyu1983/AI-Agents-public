# arXiv API Integration Guide

Use this as a quick reference when querying arXiv for paper metadata.

## Table of Contents

- [Endpoint](#endpoint)
- [Common parameters](#common-parameters)
- [Field prefixes](#field-prefixes)
- [Boolean operators](#boolean-operators)
- [Output format](#output-format)
- [Rate limiting (enforced as of 2026)](#rate-limiting-enforced-as-of-2026)
- [CDN cache footgun (GET vs POST)](#cdn-cache-footgun-get-vs-post)
- [Date-range filtering](#date-range-filtering)
- [RSS & daily-digest workflow](#rss-daily-digest-workflow)
- [Version deduplication](#version-deduplication)
- [Citation chasing](#citation-chasing)
- [Rate-limit-safe pagination](#rate-limit-safe-pagination)
- [Bulk / full-corpus harvesting — use OAI-PMH, not the search API](#bulk-full-corpus-harvesting-use-oai-pmh-not-the-search-api)

## Endpoint

Base URL:

```text
https://export.arxiv.org/api/query
```

## Common parameters

- `search_query`: arXiv query string (supports boolean operators and field prefixes)
- `start`: pagination start index (default 0)
- `max_results`: results per page (use 50 for scouting)
- `sortBy`: `relevance`, `lastUpdatedDate`, `submittedDate`
- `sortOrder`: `ascending`, `descending`

## Field prefixes

- `ti:` title
- `au:` author
- `abs:` abstract
- `cat:` category
- `all:` all fields

Examples:

```text
cat:cs.AI AND (agents OR planning)
cat:cs.CL AND abs:"in-context learning"
cat:cs.IR AND ("retrieval augmented" OR RAG)
```

## Boolean operators

- `AND`, `OR`, `ANDNOT`
- Parentheses for grouping

Example:

```text
cat:cs.AI AND (agents OR "tool use") ANDNOT withdrawn
```

## Output format

The API returns an Atom XML feed. For each entry you typically need:

- arXiv ID / URL (`/abs/...`)
- title
- authors
- summary (abstract)
- published (submission date)
- updated (latest version date)
- categories (primary + additional)

## Rate limiting (enforced as of 2026)

The arXiv API rate limiting tightened in early 2026 — it is no longer purely best-effort. Practical rules:

- Keep **≥3 seconds between requests** (the long-standing politeness floor; arXiv now enforces, not just requests, this).
- On **HTTP 429 (Too Many Requests)**, stop and back off exponentially (e.g. 30s → 60s → 120s); do not retry tight. A burst of parallel queries is the fastest way to get throttled.
- Prefer fewer wide queries (`max_results=50`+, paginate) over many narrow ones.
- Identify your client with a descriptive `User-Agent`; anonymous high-volume traffic is throttled harder.

## CDN cache footgun (GET vs POST)

Responses are served through a CDN (Fastly). Consequences:

- **Identical GET queries may return a cached, slightly stale response.** For day-fresh scouting this is usually fine; if you need the absolute latest, expect up to a short cache window of lag rather than assuming real-time.
- **Do not switch to POST to "force freshness."** The arXiv API is GET-oriented; POST is not a supported freshness lever and bypassing the cache by mangling queries just increases your 429 risk. Accept brief cache lag or use the bulk channel below.

## Date-range filtering

Use the `submittedDate` field to restrict results to a calendar window:

```text
search_query=cat:cs.AI AND submittedDate:[20260101 TO 20260610]
```

- **`submittedDate`** — date the first version was submitted. Use this for fresh-paper scouting; it excludes revisions of older papers.
- **`lastUpdatedDate`** — date of the most recent version. Use this to catch major rewrites of existing papers, but be aware that `sortBy=lastUpdatedDate` will surface old papers that received minor revisions as if they were new.
- When scouting a date window, always filter on `submittedDate` unless you specifically want revision activity.

## RSS & daily-digest workflow

arXiv publishes per-category RSS feeds tied to the official announcement schedule (confirmed against `info.arxiv.org/help/availability.html`, checked 2026-07-11):

- Announcements run **Sunday-Thursday at 20:00 ET**. There are **no new-paper announcements Friday or Saturday** — a quiet RSS feed on those two days is expected, not a sign of an outage or a stale pull.
- Submission cutoff is 14:00 ET; the window closing Thu 14:00-Fri 14:00 rolls into the Sunday 20:00 ET batch (the long weekend gap), so Monday's feed is typically the largest of the week.
- arXiv periodically shifts this schedule for holidays (see arXiv blog "Attention Authors" posts each Nov/Dec and around mid-year breaks) — re-check `info.arxiv.org/help/availability.html` if a scan around a holiday looks abnormally thin.

```text
https://rss.arxiv.org/rss/cs.AI
https://rss.arxiv.org/rss/cs.LG
https://rss.arxiv.org/rss/cs.CL
```

The matching new-listing HTML pages (useful for visual review):

```text
https://arxiv.org/list/cs.AI/new
https://arxiv.org/list/cs.LG/new
```

Recommended daily workflow:

1. **RSS pull** — ingest the day's new submissions for the target categories.
2. **Social-signal pre-filter** — cross-reference titles/IDs against HF Papers (`huggingface.co/papers`), alphaXiv (`alphaxiv.org`), and Emergent Mind (`emergentmind.com`) to identify papers already attracting community attention.
3. **Atom API deep triage** — for the surviving candidates, fetch full metadata via `export.arxiv.org/api/query` using exact arXiv IDs.

This keeps API call volume low (step 3 only runs on pre-filtered candidates) and avoids missing papers that are not yet ranked by the search index.

## Version deduplication

The Atom feed exposes two date fields per entry:

- `published` — first-version submission date.
- `updated` — most recent version date.

When `updated` ≠ `published`, the paper is a revision of an older submission.

**For fresh-paper scouting:** filter on `published` within the target window; papers where only `updated` falls in the window are revisions, not new work.

**Footgun:** `sortBy=lastUpdatedDate` returns old papers with minor revisions mixed in with new submissions. Use `sortBy=submittedDate` for recency scouting.

## Citation chasing

Two free APIs for forward and backward citation traversal:

**Semantic Scholar** (forward citations, by arXiv ID):

```text
GET https://api.semanticscholar.org/graph/v1/paper/arXiv:2501.00001/citations?fields=title,year,authors,externalIds&limit=50
```

**OpenAlex** (forward citations, by OpenAlex work ID):

```text
GET https://api.openalex.org/works?filter=cites:W2741809807&sort=cited_by_count:desc&per-page=25&api_key=YOUR_KEY
```

Rate-limit and access notes (verify at the linked docs before relying on exact numbers — both providers have changed terms within the last two years):

- **Semantic Scholar**: unauthenticated requests share a pool of **5,000 requests / 5 min across all unauthenticated users** (per `allenai/s2-folks` API release notes) — this is a shared, not per-caller, budget, so throughput degrades unpredictably under global load. A personal API key gets 1 request/s. Since **August 2024**, Semantic Scholar no longer approves new API keys for free/personal email domains or for third-party apps; keys idle ~60 days are auto-pruned. Verify at `https://github.com/allenai/s2-folks/blob/main/API_RELEASE_NOTES.md`.
- **OpenAlex**: since **13 Feb 2026**, every API request requires a (free) API key — create one at `openalex.org/settings/api`. The old email-based "polite pool" (`mailto=` parameter) is gone. Pricing is now usage-based: each key gets **$1/day of free usage**; single-work/ID lookups are free, and search/filter calls cost roughly **$1 per 1,000 calls** — for scouting-scale volumes this stays within the free daily allowance, but do not assume the old 100k-requests/day unauthenticated ceiling still applies. Verify at `https://developers.openalex.org/guides/authentication` before a high-volume pull.

## Rate-limit-safe pagination

Pseudocode operationalizing the 3-second rule with windowed pagination:

```python
start = 0
max_results = 50
while True:
    response = get(
        "https://export.arxiv.org/api/query",
        params={
            "search_query": query,
            "start": start,
            "max_results": max_results,
            "sortBy": "submittedDate",
            "sortOrder": "descending",
        },
        headers={"User-Agent": "my-scout/1.0 (contact@example.com)"},
    )
    entries = parse_atom(response)
    if not entries:
        break
    process(entries)
    start += max_results
    sleep(3)  # mandatory politeness floor
```

OAI-PMH curl example for bulk harvesting a date window:

```bash
curl -s "https://export.arxiv.org/oai2?verb=ListRecords&metadataPrefix=arXiv&set=cs&from=2026-06-01&until=2026-06-10"
```

Use the `<resumptionToken>` value from each response to fetch the next page; honour any `503 Retry-After` header before retrying.

## Bulk / full-corpus harvesting — use OAI-PMH, not the search API

For large-scale or repeated full-metadata pulls, the search API is the wrong tool (you will be throttled). Use the OAI-PMH endpoint:

```text
https://export.arxiv.org/oai2?verb=ListRecords&metadataPrefix=arXiv&set=cs
```

- Supports `from`/`until` date windows and `resumptionToken` pagination.
- `metadataPrefix=arXiv` (arXiv-native) or `oai_dc` (Dublin Core).
- Use a longer politeness delay between resumption-token pages; honour any `503 Retry-After`.
- This is the correct channel for "scan everything in cs.AI since date X" workloads; the Atom search API is for targeted scouting only.
