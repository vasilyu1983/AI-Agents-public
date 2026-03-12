# Reports in Metabase API (Cards)

In Metabase, the UI "Question" is a `card` in the API.

## Contents

- Core endpoints (most common)
- Card payload shape (practical subset)
- Query types
- Native SQL card example
- Editing workflow (recommended)
- Query Builder (MBQL) card example
- Parameters and safe query templating
- ID discovery cheatsheet
- Executing queries and exporting results

## Core endpoints (most common)

- Create a card: `POST /api/card`
- Update a card: `PUT /api/card/:id`
- Read a card: `GET /api/card/:id`

Dashboards are separate objects:

- Create a dashboard: `POST /api/dashboard`
- Read/update a dashboard: `GET|PUT /api/dashboard/:id`

Note: Exact endpoints and response shapes can vary by Metabase version. Prefer to confirm on your instance by exporting an existing card via `GET /api/card/:id` and editing that JSON.

## Card payload shape (practical subset)

When creating/updating a card, these fields cover most automation cases:

- `name` (string, REQUIRED)
- `description` (string, optional)
- `collection_id` (int, where to store the card)
- `display` (string, chart type; examples: `table`, `bar`, `line`, `pie`)
- `visualization_settings` (object; see `references/charts-settings.md`)
- `dataset_query` (object, REQUIRED)

## Query types

Metabase supports two query types in `dataset_query`:

| Type                 | `type` value | Best for                            |
|----------------------|--------------|-------------------------------------|
| Native SQL           | `"native"`   | Full SQL control, stable automation |
| Query Builder (MBQL) | `"query"`    | Replicating UI-built questions      |

---

## Native SQL card example

This is the most stable automation pattern: you control SQL directly.

`dataset_query` skeleton:

```json
{
  "database": 2,
  "type": "native",
  "native": {
    "query": "select date_trunc('day', created_at) as day, count(*) as signups from users group by 1 order by 1"
  }
}
```

Minimal create payload:

```json
{
  "name": "Daily signups",
  "collection_id": 10,
  "display": "line",
  "dataset_query": {
    "database": 2,
    "type": "native",
    "native": {
      "query": "select date_trunc('day', created_at) as day, count(*) as signups from users group by 1 order by 1"
    }
  },
  "visualization_settings": {}
}
```

## Editing workflow (recommended)

1. Build a report in the Metabase UI until it looks correct.
2. Export it via `GET /api/card/:id`.
3. Treat that JSON as the source-of-truth template.
4. Apply small, targeted edits:
   - SQL text
   - `collection_id`
   - `display`
   - `visualization_settings`
5. PUT the updated JSON back to `PUT /api/card/:id`.

This approach avoids guessing version-specific defaults and visualization keys.

---

## Query Builder (MBQL) card example

For questions created via the UI query builder, Metabase uses MBQL (Metabase Query Language), a JSON-based format.

`dataset_query` skeleton for MBQL:

```json
{
  "database": 2,
  "type": "query",
  "query": {
    "source-table": 5,
    "aggregation": [["count"]],
    "breakout": [["field", 12, {"temporal-unit": "day"}]]
  }
}
```

Minimal create payload (MBQL):

```json
{
  "name": "Daily order count",
  "collection_id": 10,
  "display": "line",
  "dataset_query": {
    "database": 2,
    "type": "query",
    "query": {
      "source-table": 5,
      "aggregation": [["count"]],
      "breakout": [["field", 12, {"temporal-unit": "day"}]]
    }
  },
  "visualization_settings": {}
}
```

**Tip:** Build a question in the Metabase UI, then use browser DevTools (Network tab) to inspect the request payload. This shows the exact MBQL structure for your query.

### Converting MBQL to native SQL

Use `POST /api/dataset/native` to convert an MBQL query to native SQL:

```bash
curl -X POST "$METABASE_URL/api/dataset/native" \
  -H "X-API-KEY: $METABASE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query": {"source-table": 5, "aggregation": [["count"]]}}'
```

---

## Parameters and safe query templating

Avoid string-interpolating untrusted input into SQL. If you need runtime parameters:

1. Build the question in the Metabase UI with filters/variables.
2. Export the card JSON (`GET /api/card/:id`).
3. Reuse the exported `dataset_query` (including any parameter/template-tag structures) as your template.

Metabase query templating shapes vary by version and by whether the question is SQL vs MBQL. Export-first is the most reliable way to keep parameters compatible with your instance.

## ID discovery cheatsheet

Prefer discovery over hardcoding numeric IDs across environments.

Common endpoints (version/edition dependent):

- Collections: `GET /api/collection`, `GET /api/collection/tree`
- Databases: `GET /api/database`
- Tables and fields: `GET /api/database/:id/metadata`, `GET /api/table`, `GET /api/field`

Tip: When in doubt, use browser DevTools (Network tab) while saving a question in the UI to see the exact payload and IDs your instance uses.

## Executing queries and exporting results

Use `POST /api/dataset` to run a query and get results:

```bash
curl -X POST "$METABASE_URL/api/dataset" \
  -H "X-API-KEY: $METABASE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "database": 2,
    "type": "native",
    "native": {"query": "SELECT COUNT(*) FROM orders"}
  }'
```

Export formats via `POST /api/card/:id/query/:format`:

| Format | Endpoint suffix |
|--------|-----------------|
| JSON   | `/json`         |
| CSV    | `/csv`          |
| XLSX   | `/xlsx`         |
