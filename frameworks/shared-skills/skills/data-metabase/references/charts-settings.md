# Charts and Visualization Settings (Metabase)

Metabase stores chart configuration on the card:

- `display`: the visualization type (table/line/bar/pie/etc.)
- `visualization_settings`: an object with visualization-specific keys

## Quick Reference

| Display | Best for | What to preserve |
|---------|----------|------------------|
| `table` | Raw detail and exports | column formatting and visibility |
| `line` | Trends over time | axis, series, and formatting settings |
| `bar` | Category comparisons | stacking, orientation, labels |
| `scalar` | KPI cards | goal/formatting and threshold colors |
| `pie` | Share of total | legend and slice labels |
| `boxplot` | Distribution analysis | export-first is safest |

## Recommended approach: copy, then edit

Metabase visualization keys change over time and depend on chart type. The most reliable way to automate chart settings is:

1. Create the chart in the UI.
2. Export the card JSON (`GET /api/card/:id`).
3. Reuse and modify the exported `display` and `visualization_settings` as your template.

## Practical patterns

### Pattern: enforce consistent naming and formatting

- Keep `name` consistent (stable identifiers help cross-environment diffs).
- Keep `display` explicit (do not rely on defaults).
- Keep `visualization_settings` minimal (only keys you need).

### Pattern: keep stable examples by chart family

- `table` for operational exports and QA checks
- `line` or `bar` for most time-series/category dashboards
- `scalar` for KPI tiles; scalar charts support conditional coloring; verify against your instance
- `boxplot` for distribution analysis when the instance supports it

### Pattern: keep a "golden card" per chart type

Create one card per visualization type (line/bar/table/pie) configured exactly as desired.
Export each as a template and reuse its `visualization_settings` for future cards.

### Pattern: export after UI edits

If a chart was edited in the UI, immediately re-export it and diff the JSON. Visualization payloads change faster than the surrounding card schema.
