# Dashboards in Metabase API

## Table of Contents

- [Core endpoints](#core-endpoints)
- [Create a dashboard](#create-a-dashboard)
- [Add a card to a dashboard](#add-a-card-to-a-dashboard)
- [Update card positions](#update-card-positions)
- [Tabs and filters](#tabs-and-filters)
- [Add a text card](#add-a-text-card)
- [Common layout patterns](#common-layout-patterns)
- [Workflow: replicate dashboards across environments](#workflow-replicate-dashboards-across-environments)

## Core endpoints

| Action           | Method | Endpoint                            |
|------------------|--------|-------------------------------------|
| Create dashboard | POST   | `/api/dashboard`                    |
| Read dashboard   | GET    | `/api/dashboard/:id`                |
| Update dashboard | PUT    | `/api/dashboard/:id`                |
| Delete dashboard | DELETE | `/api/dashboard/:id`                |

Dashcards (the card placements on a dashboard) are edited through `PUT /api/dashboard/:id` with a `dashcards` array (and `tabs` when editing dashboard tabs). The legacy `/cards` routes were removed or deprecated: [Metabase 48's API changes](https://www.metabase.com/releases/metabase-48) list removal of `PUT /api/dashboard/:id/cards`, while [issue #35577](https://github.com/metabase/metabase/issues/35577) records the replacement endpoint. Confirm writable fields in your instance's `/api/docs`.

**`dashcards` is the full desired set, not a patch.** The server diffs it against the stored dashcards:

| In the submitted `dashcards` | Result |
|------------------------------|--------|
| Existing dashcard `id` | Updated |
| Negative `id` (e.g. `-1`, `-2`) | Created as a new dashcard |
| Existing dashcard left out | **Deleted** |

So every edit is read-modify-write: `GET /api/dashboard/:id`, change the `dashcards` list, `PUT` the writable placement fields back. `scripts/metabase_api.py` rejects missing or malformed fetched lists and duplicate or invalid ids before writing; `update-dashcards` refuses to drop existing placements unless you pass `--replace`.

## Create a dashboard

```bash
curl -X POST "$METABASE_URL/api/dashboard" \
  -H "X-API-KEY: $METABASE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Sales Overview",
    "description": "Key sales metrics",
    "collection_id": 10
  }'
```

Response includes the new dashboard `id`.

## Add a card to a dashboard

Fetch the current dashcards, append the new one with a negative `id`, and PUT the whole list:

```bash
# 1. current dashcards (keep them, or they will be deleted)
curl -s "$METABASE_URL/api/dashboard/5" -H "X-API-KEY: $METABASE_API_KEY" > dash5.json

# 2. PUT existing dashcards + the new one (id -1 => create)
curl -X PUT "$METABASE_URL/api/dashboard/5" \
  -H "X-API-KEY: $METABASE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "dashcards": [
      {"id": 101, "card_id": 120, "row": 0, "col": 0, "size_x": 9, "size_y": 4},
      {"id": -1,  "card_id": 123, "row": 4, "col": 0, "size_x": 6,  "size_y": 4}
    ]
  }'
```

Or: `python3 scripts/metabase_api.py add-dashcard --dashboard-id 5 --spec dashcard.json` with `{"card_id": 123, "row": 4, "col": 0, "size_x": 6, "size_y": 4}`.

### Dashcard properties

| Property | Type | Description |
|----------|------|-------------|
| `id` | int | Dashcard id (the dashboard-card link, **not** the question id); negative = create |
| `card_id` | int or null | Saved question (card) id; `null` for text/heading cards |
| `row` | int | Vertical position (0 = top) |
| `col` | int | Horizontal position (0 = left) |
| `size_x` | int | Width in grid units (required) |
| `size_y` | int | Height in grid units (required) |
| `dashboard_tab_id` | int | Tab the dashcard belongs to, when the dashboard has tabs |
| `parameter_mappings` | array | Dashboard-filter wiring for this dashcard |
| `visualization_settings` | object | Per-dashcard overrides; text content for text cards |
| `series` | array | `[{"id": <card_id>}]` for combined series |

Older docs and payloads use camelCase `cardId`/`sizeX`/`sizeY`; the current schema uses snake_case. **Grid system:** do not assume a column count from older docs; read `col`/`size_x` values from an exported dashboard on your version and lay out new dashcards on the same grid.

## Update card positions

Send every dashcard you want to keep, with new positions:

```bash
curl -X PUT "$METABASE_URL/api/dashboard/5" \
  -H "X-API-KEY: $METABASE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "dashcards": [
      {"id": 101, "card_id": 120, "row": 0, "col": 0, "size_x": 9,  "size_y": 4},
      {"id": 102, "card_id": 121, "row": 0, "col": 9, "size_x": 9,  "size_y": 4},
      {"id": 103, "card_id": 122, "row": 4, "col": 0, "size_x": 18, "size_y": 6}
    ]
  }'
```

**Note:** The `id` in the `dashcards` array is the dashcard id (dashboard-card relationship ID), not the card/question ID. Get it from the dashboard GET response.

### Full-dashboard update pattern

If the dashboard includes tabs, dashboard filters, or other exported state, use:

1. `GET /api/dashboard/:id`
2. Build a write payload from the exported state using the instance's documented writable fields; the full read response is not a replayable write payload.
3. `PUT /api/dashboard/:id` with the changed fields, preserving dashcard filter mappings and including `tabs` when editing them.

This is the safer path for modern dashboards because it preserves tab/filter mappings that are easy to lose when rebuilding layout by hand.

## Tabs and filters

- Current dashboards may include `tabs`, dashboard-level filters, and dashcard filter mappings
- Export-first is strongly recommended before changing dashboards that already exist
- If a dashboard uses tabs, preserve both `tabs` and `dashcards` from the exported payload
- When cloning dashboards across environments, map cards first, then restore layout and filter mappings second

## Add a text card

Text cards have `card_id: null` and carry their content in `visualization_settings`. Add one as a new dashcard (negative `id`) alongside the existing dashcards:

```bash
curl -X PUT "$METABASE_URL/api/dashboard/5" \
  -H "X-API-KEY: $METABASE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "dashcards": [
      {"id": 101, "card_id": 120, "row": 2, "col": 0, "size_x": 9, "size_y": 4},
      {
        "id": -1,
        "card_id": null,
        "row": 0,
        "col": 0,
        "size_x": 18,
        "size_y": 2,
        "visualization_settings": {
          "text": "## Sales Dashboard\nUpdated daily at 6am UTC",
          "virtual_card": {"display": "text"}
        }
      }
    ]
  }'
```

## Common layout patterns

### Two-column layout

```text
+------------------+------------------+
|   Card A (9x4)   |   Card B (9x4)   |   row 0
+------------------+------------------+
|           Card C (18x6)             |   row 4
+-------------------------------------+
```

JSON for this layout:

```json
{
  "dashcards": [
    {"id": 101, "row": 0, "col": 0, "size_x": 9, "size_y": 4},
    {"id": 102, "row": 0, "col": 9, "size_x": 9, "size_y": 4},
    {"id": 103, "row": 4, "col": 0, "size_x": 18, "size_y": 6}
  ]
}
```

### Header + KPIs + chart

```text
+-------------------------------------+
|        Text Header (18x2)           |   row 0
+--------+--------+--------+----------+
| KPI 1  | KPI 2  | KPI 3  | KPI 4    |   row 2
+--------+--------+--------+----------+
|           Main Chart (18x8)         |   row 6
+-------------------------------------+
```

## Workflow: replicate dashboards across environments

1. Export source dashboard: `GET /api/dashboard/:id`
2. Extract card IDs, tabs, filters, and layout from `dashcards`
3. Create cards in target or use serialization / Remote Sync when available
4. Create dashboard in target: `POST /api/dashboard`
5. Restore layout with `PUT /api/dashboard/:id` (`dashcards` with negative ids for new placements, plus `tabs`)

Numeric card and dashcard ids differ between instances. Before step 5, map each source `card_id` to the target card, by `entity_id` (kept stable by serialization) or by an agreed lookup key such as collection plus name; never copy numeric ids across instances. `scripts/metabase_api.py` matches dashcards by numeric id only, so use it for edits within one instance.

Card query shape: newer Metabase versions serialize `dataset_query` in the stages-based MBQL 5 shape. Check your version's API docs before parsing or rewriting card queries, and do not mix legacy and MBQL 5 shapes in one payload.

**Preferred:** Use Remote Sync or [serialization](https://www.metabase.com/docs/latest/installation-and-operation/serialization) for reviewable, cross-environment promotion. Use raw dashboard API for incremental edits and runtime automation.
