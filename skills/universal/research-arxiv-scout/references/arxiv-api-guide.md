# arXiv API Integration Guide

Use this as a quick reference when querying arXiv for paper metadata.

## Table of Contents

- [Endpoint](#endpoint)
- [Common parameters](#common-parameters)
- [Field prefixes](#field-prefixes)
- [Boolean operators](#boolean-operators)
- [Output format](#output-format)
- [Rate limiting](#rate-limiting)
- [GET and POST](#get-and-post)
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
- `max_results`: results per page; read the current API manual for its cap before a large scan
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

## Rate limiting

Before execution, read the current [arXiv API terms](https://info.arxiv.org/help/api/tou.html) for the request gap and connection limit. Apply them across all machines under your control. Practical rules:

- Set the delay from the terms you just read; the query generator's runtime estimate uses a checked constant and is a planning estimate, not permission to exceed a newer limit.
- On **HTTP 429 (Too Many Requests)**, stop and back off exponentially with a capped wait; do not retry tight. A burst of parallel queries is the fastest way to get throttled.
- Narrow an overbroad query before paginating far into the result set.
- Identify your client with a descriptive `User-Agent`.

## GET and POST

The [arXiv API user manual](https://info.arxiv.org/help/api/user-manual.html#311-query-interface) supports both GET and POST; it suggests POST when parameters are unusually long. Neither method changes the request-rate limit. Do not change methods or vary queries solely to bypass caching.

## Date-range filtering

Use the `submittedDate` field to restrict results to a calendar window:

```text
search_query=cat:cs.AI AND submittedDate:[YYYYMMDD0000 TO YYYYMMDD2359]
```

The range is `[YYYYMMDDTTTT TO YYYYMMDDTTTT]`, with `TTTT` the 24-hour time to the minute in GMT (arXiv API user manual: https://info.arxiv.org/help/api/user-manual.html). Put the window in the query this way so a 30-day and a 365-day scan return different result sets; sorting by date alone does not apply a window.

- **`submittedDate`** — date the first version was submitted. Use this for fresh-paper scouting; it excludes revisions of older papers.
- **`lastUpdatedDate`** — date of the most recent version. Use this to catch major rewrites of existing papers, but be aware that `sortBy=lastUpdatedDate` will surface old papers that received minor revisions as if they were new.
- When scouting a date window, always filter on `submittedDate` unless you specifically want revision activity.

## RSS & daily-digest workflow

arXiv publishes per-category RSS feeds tied to its [announcement schedule](https://info.arxiv.org/help/availability.html). Check that page before interpreting a quiet feed:

- Announcement and mailing days differ. A quiet feed may reflect the schedule, deferrals, or publication lag.

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
GET https://api.openalex.org/works?filter=cites:W2741809807&sort=cited_by_count:desc&per-page=25
```

(OpenAlex answers basic queries without a key; add `&api_key=YOUR_KEY` when you need a larger daily budget.)

Both providers change their access terms. Before a citation chase at scale, look up:

- **Semantic Scholar:** the current unauthenticated pool, keyed rate, and key-eligibility rules at https://www.semanticscholar.org/product/api and its API release notes (https://github.com/allenai/s2-folks/blob/main/API_RELEASE_NOTES.md). The unauthenticated pool is shared across callers, so throughput is unpredictable.
- **OpenAlex:** the current keyless and keyed daily budgets at https://help.openalex.org/api/authentication/. It returns 429 when the budget or the rate limit is exceeded.
- On 429 from either, back off exponentially with a capped wait.

## Rate-limit-safe pagination

Pseudocode for windowed pagination that respects the current request gap and reports coverage. `query` already carries the `submittedDate` range. Check the current [API manual](https://info.arxiv.org/help/api/user-manual.html#3112-start-and-max_results-paging) for page and result-set caps.

```python
start, page_size, max_pages = 0, 50, 4  # illustrative scan budget
required_gap = read_current_api_terms()
fetched, total = 0, None
for _ in range(max_pages):
    response = get(
        "https://export.arxiv.org/api/query",
        params={
            "search_query": query,
            "start": start,
            "max_results": page_size,
            "sortBy": "submittedDate",
            "sortOrder": "descending",
        },
        headers={"User-Agent": "my-scout/1.0 (contact@example.com)"},
    )
    feed = parse_atom(response)
    if total is None:
        total = feed.total_results          # opensearch:totalResults
    if not feed.entries:
        break
    process(feed.entries)
    fetched += len(feed.entries)
    start += page_size
    if fetched >= total:
        break
    sleep(required_gap)
report_coverage(fetched, total)             # always "fetched/total", e.g. 200/1460
if total > fetched:
    narrow_query_and_rerun()                # never call the first pages "the top of the window"
```

For field scans, keep entries whose `arxiv:primary_category` is in the requested categories and label the rest cross-lists.

OAI-PMH curl example for bulk harvesting a date window:

```bash
curl -s "https://export.arxiv.org/oai2?verb=ListRecords&metadataPrefix=arXiv&set=cs&from=YYYY-MM-DD&until=YYYY-MM-DD"
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
