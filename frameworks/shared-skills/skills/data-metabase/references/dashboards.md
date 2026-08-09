# Dashboards in Metabase API

## Table of Contents

- [Contents](#contents)
- [Core endpoints](#core-endpoints)
- [Create a dashboard](#create-a-dashboard)
- [Add a card to a dashboard](#add-a-card-to-a-dashboard)
- [Update card positions](#update-card-positions)
- [Tabs and filters](#tabs-and-filters)
- [Add a text card](#add-a-text-card)
- [Common layout patterns](#common-layout-patterns)
- [Workflow: replicate dashboards across environments](#workflow-replicate-dashboards-across-environments)

Create and manage dashboards programmatically, including card placement and layout.

## Contents

- Core endpoints
- Create a dashboard
- Add a card to a dashboard
- Update card positions
- Tabs and filters
- Add a text card
- Common layout patterns
- Workflow: replicate dashboards across environments

## Core endpoints

| Action           | Method | Endpoint                            |
|------------------|--------|-------------------------------------|
| Create dashboard | POST   | `/api/dashboard`                    |
| Read dashboard   | GET    | `/api/dashboard/:id`                |
| Update dashboard | PUT    | `/api/dashboard/:id`                |
| Delete dashboard | DELETE | `/api/dashboard/:id`                |
| Add card         | POST   | `/api/dashboard/:id/cards`          |
| Update cards     | PUT    | `/api/dashboard/:id/cards`          |
| Remove card      | DELETE | `/api/dashboard/:id/cards/:card_id` |

For simple layout changes, the `/cards` endpoints are convenient. For dashboards with tabs, filters, or richer state, prefer export-first and consider updating the full dashboard payload via `PUT /api/dashboard/:id`.

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

Use `POST /api/dashboard/:id/cards` with placement properties:

```bash
curl -X POST "$METABASE_URL/api/dashboard/5/cards" \
  -H "X-API-KEY: $METABASE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "cardId": 123,
    "row": 0,
    "col": 0,
    "sizeX": 6,
    "sizeY": 4
  }'
```

### Card placement properties

| Property | Type | Description                                      |
|----------|------|--------------------------------------------------|
| `cardId` | int  | ID of the saved question (card) to add           |
| `row`    | int  | Vertical position (0 = top)                      |
| `col`    | int  | Horizontal position (0 = left, max typically 17) |
| `sizeX`  | int  | Width in grid units (min 2, typical max 18)      |
| `sizeY`  | int  | Height in grid units (min 2)                     |

**Grid system:** Metabase uses an 18-column grid. Cards have minimum dimensions (typically 2x2 or 3x3 depending on version).

## Update card positions

Use `PUT /api/dashboard/:id/cards` with an array of card updates for compatibility and small changes:

```bash
curl -X PUT "$METABASE_URL/api/dashboard/5/cards" \
  -H "X-API-KEY: $METABASE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "cards": [
      {"id": 101, "row": 0, "col": 0, "sizeX": 9, "sizeY": 4},
      {"id": 102, "row": 0, "col": 9, "sizeX": 9, "sizeY": 4},
      {"id": 103, "row": 4, "col": 0, "sizeX": 18, "sizeY": 6}
    ]
  }'
```

**Note:** The `id` in the cards array is the `dashcard_id` (dashboard-card relationship ID), not the card/question ID. Get this from the dashboard GET response.

### Full-dashboard update pattern

If the dashboard includes tabs, dashboard filters, or other exported state, use:

1. `GET /api/dashboard/:id`
2. Edit the exported JSON carefully
3. `PUT /api/dashboard/:id` with the updated payload

This is the safer path for modern dashboards because it preserves tab/filter mappings that are easy to lose when rebuilding layout by hand.

## Tabs and filters

- Current dashboards may include `tabs`, dashboard-level filters, and dashcard filter mappings
- Export-first is strongly recommended before changing dashboards that already exist
- If a dashboard uses tabs, preserve both `tabs` and `dashcards` from the exported payload
- When cloning dashboards across environments, map cards first, then restore layout and filter mappings second

## Add a text card

Text cards have `cardId: null` and use `visualization_settings` for content:

```bash
curl -X POST "$METABASE_URL/api/dashboard/5/cards" \
  -H "X-API-KEY: $METABASE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "cardId": null,
    "row": 0,
    "col": 0,
    "sizeX": 18,
    "sizeY": 2,
    "visualization_settings": {
      "text": "## Sales Dashboard\nUpdated daily at 6am UTC",
      "virtual_card": {"display": "text"}
    }
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
  "cards": [
    {"id": 101, "row": 0, "col": 0, "sizeX": 9, "sizeY": 4},
    {"id": 102, "row": 0, "col": 9, "sizeX": 9, "sizeY": 4},
    {"id": 103, "row": 4, "col": 0, "sizeX": 18, "sizeY": 6}
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
5. Restore layout with `POST /api/dashboard/:id/cards` or a full `PUT /api/dashboard/:id`

**Preferred:** Use Remote Sync or [serialization](https://www.metabase.com/docs/latest/installation-and-operation/serialization) for reviewable, cross-environment promotion. Use raw dashboard API for incremental edits and runtime automation.
