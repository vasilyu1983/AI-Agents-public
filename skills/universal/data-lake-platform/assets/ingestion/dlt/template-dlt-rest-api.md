# dlt REST API Source Template

Use when extracting from an HTTP API with dlt's declarative `rest_api_source`. Pipeline identity and dispositions: [template-dlt-pipeline.md](template-dlt-pipeline.md). Cursor, merge and delete rules: [template-dlt-incremental.md](template-dlt-incremental.md).

## Skeleton: The Settings That Matter

```python
source = rest_api_source({
    "client": {
        "base_url": "https://api.example.com/",
        "auth": {"type": "bearer", "token": dlt.secrets["sources.example.token"]},
    },
    "resource_defaults": {"primary_key": "id", "write_disposition": "merge"},
    "resources": [
        {
            "name": "orders",
            "endpoint": {
                "path": "orders",
                "data_selector": "data",          # where the record list lives in the response
                "paginator": {"type": "cursor", "cursor_path": "next_cursor", "cursor_param": "cursor"},
                "params": {
                    "updated_since": {             # incremental bound to pipeline state
                        "type": "incremental",
                        "cursor_path": "updated_at",
                        "initial_value": "<history_start>",
                    },
                },
            },
        },
    ],
})
```

- Set `data_selector` explicitly. Auto-detection can pick the wrong list (for example an `errors` or `included` array), and the load succeeds with the wrong records.
- Set the paginator explicitly. Auto-detection that finds no next page loads only page one with no error.
- Put `primary_key` and `write_disposition` in `resource_defaults` so no endpoint silently falls back to `append`.

## Paginator Choice

| API offers | Paginator | Note |
|---|---|---|
| Opaque next token in body | `cursor` | Preferred: stable under concurrent inserts |
| Full next URL in body | `json_link` | Same stability as cursor |
| `Link` header (RFC 8288) | `header_link` | Same |
| `offset`/`limit` | `offset` | Rows inserted or deleted during the scan shift pages: rows are skipped or duplicated. Sort by a stable key and load with `merge` |
| Page numbers | `page_number` | Same risk as offset; needs `total_path` or a stop-on-empty-page rule |

For offset and page-number APIs, prefer narrowing each run by the incremental filter so the scanned set is small and changes little during the run.

## Incremental on APIs

- Use the API's server-side filter (`updated_since`, `modified_after`) through the `incremental` param. Without a server filter, dlt still de-duplicates by cursor but downloads every page each run.
- Check that the filter uses the same field and timezone as `cursor_path`. A filter on `created_at` with a cursor on `updated_at` never picks up updates.
- If the API returns rows ordered by the cursor, set the incremental's `row_order` to match so dlt stops paginating once rows leave the window. Set it only when the order is guaranteed; a wrong order stops the walk early and loses rows.

## Parent-Child Endpoints

Resolve child paths from a parent resource (`"type": "resolve", "resource": "customers", "field": "id"`). Each parent row costs one or more child requests, so:

- Filter the parent incrementally first, or the child fans out over every parent on every run.
- A child resource does not inherit the parent's cursor (see [parent-child rule](template-dlt-incremental.md#parent-child-resources)).

## Rate Limits, Retries, Errors

- dlt's HTTP client retries transient failures (429, 5xx, connection errors) with backoff. Tune retry count and backoff in the runtime config (see the dlt docs for the exact keys), not in paginator settings.
- Respect the provider's documented limit by lowering concurrency and page size before raising retries; aggressive retries against a 429 extend the ban.
- Use `response_actions` to handle known non-errors explicitly (for example `{"status_code": 404, "action": "ignore"}` for a deleted child). Do not wrap `pipeline.run` in a broad `except` that logs and continues: that hides partial loads.

## Auth

- Built-in types cover bearer, API key (header or query), HTTP basic, and OAuth2 client credentials. Use them instead of hand-built headers so tokens come from secrets and refresh correctly.
- Keep tokens in `.dlt/secrets.toml` or environment variables; never in the config dict.

## Verify

- [ ] Record count for a small window matches the API's own total or UI count (catches wrong `data_selector` and single-page pagination).
- [ ] The last page is reached: log page count and compare with `total`/`has_more`.
- [ ] A second run requests only the filtered window (check request params in the trace).
- [ ] No duplicate `primary_key` values in the destination after an offset-paginated load.
