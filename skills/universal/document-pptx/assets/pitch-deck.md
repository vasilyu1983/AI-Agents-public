# Pitch Deck — Non-Obvious Patterns

A pitch deck is standard python-pptx `add_textbox`/`add_chart` work; see [../references/pptx-layouts.md](../references/pptx-layouts.md) and [../references/pptx-charts.md](../references/pptx-charts.md) for the API. This file covers only the patterns that aren't obvious from the API docs.

## Slide Order

A common order: Problem → Solution → Market (TAM/SAM/SOM) → Business Model → Traction → Team → Competition → Financials → Ask. Putting Traction before Team leads with evidence rather than credentials. Give your strongest quantified proof (ARR, growth, retention) its own metrics slide instead of burying it in a bulleted list.

## Metric Row Layout Math

Set the slide size explicitly: `prs.slide_width = Inches(10)` and `prs.slide_height = Inches(5.625)` for 16:9. python-pptx's default template is 4:3 (10×7.5 in).

For N metrics laid out as equal-width columns on a 10"-wide slide:

```python
box_width = 9 / num_metrics  # 9" usable width, 0.5" margin each side
for i, (value, label) in enumerate(metrics):
    x = Inches(0.5 + i * box_width)
```

Keep each metric's value and label in separate text boxes at the same `x`, not one multi-line box. Independent boxes let you recolor a single metric (for example a red churn number) without touching the others. Columns narrow quickly as N grows; wrap to a second metrics slide rather than shrinking the font to fit.

## Financial Projection Chart

A single-series `COLUMN_CLUSTERED` chart with `chart.has_legend = False` reads cleaner than one with a legend; a legend only adds value with 2+ series. On a 16:9 slide (5.625" tall), keep `y + h` at or below about 5.1" (for example `y=1.3, h=3.8`) so the chart clears the bottom edge; see the geometry note in [pptx-charts.md](../references/pptx-charts.md).

## PDF Export

`unoconv` is deprecated; call LibreOffice headless directly:

```bash
soffice --headless --convert-to pdf pitch_deck.pptx
```

## Related Resources

- [../references/pptx-layouts.md](../references/pptx-layouts.md) — layout gotchas
- [../references/pptx-charts.md](../references/pptx-charts.md) — chart API and geometry
- [quarterly-review.md](quarterly-review.md) — business review template
