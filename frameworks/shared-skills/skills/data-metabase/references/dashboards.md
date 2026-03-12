# Dashboards in Metabase API

Create and manage dashboards programmatically, including card placement and layout.

## Contents

- Core endpoints
- Create a dashboard
- Add a card to a dashboard
- Update card positions
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

Use `PUT /api/dashboard/:id/cards` with an array of card updates:

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
2. Extract card IDs and layout from `dashcards` array
3. Create cards in target (or use serialization for Pro/Enterprise)
4. Create dashboard in target: `POST /api/dashboard`
5. Add cards with same layout: `POST /api/dashboard/:id/cards`

**Pro/Enterprise:** Use [serialization](https://www.metabase.com/docs/latest/installation-and-operation/serialization) for full dashboard export/import with Entity IDs.
