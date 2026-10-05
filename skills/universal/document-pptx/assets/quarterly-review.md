# Quarterly Review — Non-Obvious Patterns

An 8-slide QBR deck (Title → Executive Summary → Revenue → Product → Customers → Challenges → Next Quarter → Q&A) is standard python-pptx work; see [../references/pptx-charts.md](../references/pptx-charts.md) and [../references/pptx-layouts.md](../references/pptx-layouts.md) for the API. This file covers only what isn't obvious from the API docs.

## KPI Dashboard Status Color Mapping

Map each KPI's status to a color once, in a lookup, not inline per metric. The red/amber/green semantics then stay consistent when a later slide (for example a summary table) needs the same mapping, and readers recognize the same "at risk" color across decks:

```python
from pptx.dml.color import RGBColor

STATUS_COLOR = {
    "success": RGBColor(0x28, 0xA7, 0x45),  # green
    "warning": RGBColor(0xFF, 0xC1, 0x07),  # amber
    "danger":  RGBColor(0xDC, 0x35, 0x45),  # red
}
color = STATUS_COLOR[kpi["status"]]  # KeyError on an unknown status, not a silent default
```

Do not rely on color alone; pair it with a text label or symbol (see [../references/pptx-accessibility-compliance.md](../references/pptx-accessibility-compliance.md)).

## Challenges Slide

Include a separate "Challenges & Learnings" slide before "Next Quarter Goals" rather than folding it into the goals slide. A review that shows only wins reads as filtered; naming two or three real challenges, with what is being done about each, makes the traction numbers more credible.

## Data Source Traceability

Every number on a QBR slide should trace to a query or dashboard the audience can check, not a hand-typed config dict. Put whatever populates `monthly_revenue`/`kpis` (SQL query, API call, CSV) in a named, swappable function at the top of the script. QBR decks get regenerated each period with new data, and the slide-layout code should not need to change.

## Related Resources

- [../references/pptx-charts.md](../references/pptx-charts.md) — chart styling and geometry
- [../references/pptx-layouts.md](../references/pptx-layouts.md) — layout gotchas
- [pitch-deck.md](pitch-deck.md) — external presentation format
