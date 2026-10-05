# Data Dashboard Notes

Non-obvious gotchas for building KPI/dashboard workbooks with `openpyxl`. Base
mechanics (styling, `PatternFill`, merging cells, `BarChart`/`LineChart`/`PieChart`
construction) are covered in `../references/excel-formatting.md` and `../references/excel-charts.md` — this
file only covers dashboard-layout-specific pitfalls not obvious from those refs.

---

## KPI Card Grid Layout

Laying out repeated KPI "cards" across columns (name / value / vs-target) is a
common dashboard pattern. Two openpyxl behaviours bite people:

- **Write only to the anchor (top-left) cell of a merged range.** Writing to any
  other cell in the range raises `AttributeError: 'MergedCell' object attribute
  'value' is read-only`. Merging a range that already holds values keeps only the
  anchor's value; the others are dropped without a warning.
- **Merge first, then style every cell in the block.** `merge_cells()` also
  drops the styles already set on the non-anchor cells, so a fill applied
  before the merge survives only on the anchor. Apply the card fill (and
  borders) after merging, to every cell in the card's bounding box.

```python
kpi_start_col = 1
for i, kpi in enumerate(data['kpis']):
    col = kpi_start_col + (i * 3)  # 3-column-wide cards
    ws.merge_cells(start_row=row, start_column=col, end_row=row, end_column=col + 2)
    ws.cell(row=row, column=col).value = kpi['name']  # write to the anchor only
    for r in range(row, row + 4):  # style after merging, or the fill is lost
        for c in range(col, col + 3):
            ws.cell(row=r, column=c).fill = card_fill
```

## Embedding a Chart Next to Hand-Placed Cells

`ws.add_chart(chart, "E8")` anchors the chart's top-left corner at a cell but
does not reserve that space — if KPI cards or tables are written to
overlapping rows/columns after the chart is added, they render *underneath*
the chart in Excel (both exist; the chart just draws on top). Lay out the
non-chart content first, compute the chart's anchor from the known row/column
extent of what's already written, then add the chart last.

## Hiding Raw Data Columns Behind a Dashboard View

A common ask is "show only the dashboard, not the raw numbers backing the
charts." `ws.column_dimensions['A'].hidden = True` hides the column from view
but the data — and any formula referencing it — is still fully present and
readable by anyone who unhides it or opens the raw XML. Hidden columns are a
presentation choice, not a security boundary; do not use them to withhold
sensitive figures from the person receiving the workbook (see
`../references/excel-security-protection.md`).

## Chart Data Source Row Bookkeeping

Dashboard code typically writes staging data for a chart (e.g. a 12-row
monthly trend table) into the same worksheet the dashboard cards live on, then
tracks the row where that data starts to build `Reference()` ranges. Off-by-one
errors here are common because `Reference(min_row=..., max_row=...)` is
inclusive on both ends — if the trend table's header is at `trend_data_row`
and data starts at `trend_data_row + 1`, the category reference must start at
`trend_data_row + 1` and the data reference (with `titles_from_data=True`)
must start at `trend_data_row` to include the header as the series title.
