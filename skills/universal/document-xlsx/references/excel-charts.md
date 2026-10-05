# Excel Charts Reference

Rules for native Excel charts generated from code: choosing the chart, wiring references, and the openpyxl behaviours that produce broken or misleading charts. Class-by-class API tutorials are in the openpyxl and XlsxWriter docs.

## Contents

- [Choose The Chart](#choose-the-chart)
- [Native Chart Or Image](#native-chart-or-image)
- [Wiring References](#wiring-references)
- [openpyxl Gotchas](#openpyxl-gotchas)
- [Verification](#verification)

## Choose The Chart

| Question the reader asks | Chart | openpyxl class | Avoid |
|--------------------------|-------|----------------|-------|
| How do categories compare? | Column/bar, sorted | `BarChart` (`type="col"`/`"bar"`) | 3-D bars, unsorted categories |
| How did it change over time? | Line | `LineChart` | Pie; column charts with more than about 12 periods |
| What is the share of a whole? | Stacked bar, or pie with 5 slices or fewer | `BarChart(grouping="stacked", overlap=100)`, `PieChart` | Pie with many slices, exploded or 3-D pies |
| Are two measures related? | Scatter | `ScatterChart` | Line charts for unordered x values |
| Two measures, different units | Column plus line on a secondary axis | `BarChart` + `LineChart` | Dual axes whose scales imply a false correlation |

Rules: start value axes at zero for bars, label the axes with units, and keep one message per chart. The chart title should state the conclusion ("Q4 revenue up 12%"), not only the topic.

## Native Chart Or Image

- **Native chart** (openpyxl/XlsxWriter): it stays linked to cells, updates on recalculation and remains editable. It is the default for workbooks that people will reuse.
- **Image** (a matplotlib PNG inserted with `ws.add_image`): exact visuals, but it goes stale when the data changes, has no alt text by default and cannot be edited. Use it only for chart types Excel lacks, or for frozen snapshots.
- ExcelJS has no chart-authoring API. From Node, either fill a template that already contains the chart and write only the data cells, or insert an image.

## Wiring References

```python
from openpyxl.chart import BarChart, Reference

data = Reference(ws, min_col=2, max_col=3, min_row=1, max_row=13)   # include the header row
cats = Reference(ws, min_col=1, min_row=2, max_row=13)              # exclude the header row
chart = BarChart()
chart.add_data(data, titles_from_data=True)   # row 1 becomes the series names
chart.set_categories(cats)
```

- With `titles_from_data=True` the data reference must **include** the header row and the category reference must **exclude** it. An off-by-one shifts every label by a period, and nothing errors.
- The reference points to a fixed range. Rows appended later are not charted. For growing data, size the range to the data at write time, or regenerate the chart.
- Chart the cells the reader can see, not a hidden helper sheet, unless the helper is documented.

## openpyxl Gotchas

- **Axes may be missing in Excel.** openpyxl omits `<c:delete>` on axes by default, and some Excel builds then hide them. Set `chart.x_axis.delete = False` and `chart.y_axis.delete = False` explicitly. This writes `<delete val="0"/>`.
- **Secondary axis:** the second chart needs a distinct axis id and must cross at the max, or both series share one scale:

```python
line.y_axis.axId = 200
line.y_axis.crosses = "max"
bar += line
```

- **Stacked bars** need `overlap = 100` as well as `grouping = "stacked"`, or the segments render side by side.
- **Size** is `chart.width`/`chart.height` in centimetres. The anchor cell sets only the top-left corner, so a chart can cover data to its right. Leave empty columns, or anchor the chart below the table.
- `chart.style = N` selects one of Excel's built-in style presets. The rendering varies by Excel build, so do not promise a specific look.

## Verification

1. Open the file in Excel (or render it with LibreOffice to PDF or PNG) and look at every chart. openpyxl writes invalid combinations without error.
2. Check that the series names, category labels and first and last values match the source cells.
3. Check that the axes are visible and titled with units, and that the legend does not hide data.
4. Add alt text or a nearby text summary for each chart (see [excel-accessibility-compliance.md](excel-accessibility-compliance.md)).

## Related Resources

- [excel-formatting.md](excel-formatting.md) - Conditional formatting as an alternative to charts
- [excel-pivot-tables.md](excel-pivot-tables.md) - Summaries that feed charts
- [../SKILL.md](../SKILL.md) - Parent skill
