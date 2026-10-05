# PPTX Charts - Data Visualization in PowerPoint

Rules for native, editable charts in generated decks: slide geometry, filling template charts, library limits and verification. Chart-type tutorials are in the python-pptx and PptxGenJS docs.

## Contents

- [Choose The Chart](#choose-the-chart)
- [Slide Geometry](#slide-geometry)
- [python-pptx](#python-pptx)
- [Charts in Node.js (pptxgenjs)](#charts-in-nodejs-pptxgenjs)
- [Data Plumbing](#data-plumbing)
- [Verification](#verification)

## Choose The Chart

| Message | Chart | python-pptx constant |
|---------|-------|----------------------|
| Compare categories | Clustered column/bar, sorted | `COLUMN_CLUSTERED`, `BAR_CLUSTERED` |
| Trend over time | Line | `LINE`, `LINE_MARKERS` |
| Part of a whole | Stacked column, or pie with 5 slices or fewer | `COLUMN_STACKED`, `PIE` |
| Relationship | Scatter | `XY_SCATTER` |

One message per chart, stated in the slide title ("Q4 revenue beat target by 12%"). Label units on the axis. Avoid 3-D, and avoid pies with many slices.

## Slide Geometry

**pptxgenjs's default layout (`LAYOUT_16x9`) is 10 × 5.625 in, while python-pptx's default template is 10 × 7.5 in (4:3).** Positions copied from a python-pptx example (`y=1.5, h=5`, bottom edge 6.5 in) run 0.875 in off a pptxgenjs slide.

- Check `y + h <= slide height` and `x + w <= slide width` for every chart. For a 16:9 slide, `x: 0.5, y: 1.2, w: 9, h: 3.8` (bottom edge 5.0 in) leaves room for a title above and a footer below.
- Read the real size from the template (`prs.slide_width`, `prs.slide_height` in EMU, where 914,400 EMU = 1 in) or set `pptx.layout` explicitly. Never assume one.
- Nothing warns when a chart runs off the slide. Only a bounds check or a render catches it.

## python-pptx

- **Filling a template chart:** find it by shape name and call `chart.replace_data(chart_data)`. This keeps the designer's formatting, colours and embedded workbook, and it handles a different number of categories. Building a new chart and copying the style over is fragile.
- **Colours:** leave series colours to the theme's accent order where possible (see [pptx-template-branding.md](pptx-template-branding.md)). A per-series `fill.fore_color.rgb` pins colours that a later theme change will not update.
- **Number formats:** setting `data_labels.number_format` or `tick_labels.number_format` also sets `number_format_is_linked = False`, so the format applies. Quote literal text in format codes: `'$#,##0"K"'`, not `'$#,##0K'`.
- **Combo charts (column plus line) are not supported** by the python-pptx API. Use a template chart that already is a combo and fill it with `replace_data`, generate it with pptxgenjs, or edit the chart XML.
- Each chart embeds its data as an `.xlsx` part (`ppt/embeddings/`). That makes the chart editable in PowerPoint, and it ships the data to the recipient. Do not chart figures the recipient must not see at a finer grain than shown.

```python
chart_shape = next(s for s in slide.shapes if s.has_chart and s.name == "RevenueChart")
data = CategoryChartData()
data.categories = df["period"].tolist()
for col in ("Revenue", "Costs"):
    data.add_series(col, df[col].tolist(), number_format="#,##0")
chart_shape.chart.replace_data(data)
```

## Charts in Node.js (pptxgenjs)

```typescript
slide.addChart(pptx.ChartType.bar, [
  { name: 'Revenue', labels: ['Q1', 'Q2', 'Q3', 'Q4'], values: [100, 150, 180, 225] },
], {
  x: 0.5, y: 1.2, w: 9, h: 3.8, // default layout is 10x5.625in; y+h=5.0 leaves room for title/footer
  barDir: 'col', showLegend: false, valAxisTitle: 'Revenue ($K)', showValAxisTitle: true,
});
```

- True combo charts take an **array of chart-type definitions** as the first argument (one entry per type, with a secondary axis on the line series). Check the PptxGenJS docs for the option names in your installed version. A single bar chart with line-style options is not a combo.
- `chartColors` takes hex strings without `#`.
- In a designer-owned template, fill the existing chart with PPTX-Automizer (`ModifyChartHelper.setChartData`) instead of drawing a new one.

## Data Plumbing

- Build series from the source data in one place (a DataFrame or query result). Never type numbers into chart code.
- Derive period labels from the data (`df["period"]`). Do not hard-code years or quarters in code or SQL. Pass the period as a parameter: `WHERE period = ?`.
- `None` in a series renders as a gap. Decide explicitly between gap, zero and interpolation, and say which in a footnote when it matters.
- Keep a reconciliation: the chart total should equal the table or appendix total on another slide.

## Verification

1. Run a bounds check on every chart shape (`left + width <= prs.slide_width`, `top + height <= prs.slide_height`).
2. Render the deck (LibreOffice to PDF, then to images) and look at each chart slide. Check the labels, the legend, overlap with the title or footer, and that the axis does not start misleadingly above zero on bars.
3. Check that the series names and first and last values match the source.
4. Add alt text, or a nearby text summary, stating the chart's conclusion (see [pptx-accessibility-compliance.md](pptx-accessibility-compliance.md)).

## Related Resources

- [pptx-template-branding.md](pptx-template-branding.md) - Theme palette and Automizer chart fills
- [pptx-layouts.md](pptx-layouts.md) - Layout choice
- [../assets/quarterly-review.md](../assets/quarterly-review.md) - Business review charts
