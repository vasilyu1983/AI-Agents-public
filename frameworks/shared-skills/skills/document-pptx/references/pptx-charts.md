# PPTX Charts - Data Visualization in PowerPoint

Deep-dive resource for charts, graphs, and data visualization with python-pptx and pptxgenjs.

---

## Contents

- [Chart Type Reference](#chart-type-reference)
- [Column Chart (Python)](#column-chart-python)
- [Line Chart with Markers](#line-chart-with-markers)
- [Pie Chart](#pie-chart)
- [Combo Chart (Column + Line)](#combo-chart-column--line)
- [Charts in Node.js (pptxgenjs)](#charts-in-nodejs-pptxgenjs)
- [Chart Styling Best Practices](#chart-styling-best-practices)
- [Dynamic Data from DataFrame](#dynamic-data-from-dataframe)
- [Chart from Database Query](#chart-from-database-query)
- [Related Resources](#related-resources)

---

## Chart Type Reference

| Chart Type | Constant (python-pptx) | Use Case |
|------------|------------------------|----------|
| Column (Clustered) | `XL_CHART_TYPE.COLUMN_CLUSTERED` | Compare categories |
| Column (Stacked) | `XL_CHART_TYPE.COLUMN_STACKED` | Part-to-whole by category |
| Bar (Clustered) | `XL_CHART_TYPE.BAR_CLUSTERED` | Horizontal comparison |
| Line | `XL_CHART_TYPE.LINE` | Trends over time |
| Line (Markers) | `XL_CHART_TYPE.LINE_MARKERS` | Trends with data points |
| Pie | `XL_CHART_TYPE.PIE` | Proportions (single series) |
| Doughnut | `XL_CHART_TYPE.DOUGHNUT` | Proportions with center |
| Area | `XL_CHART_TYPE.AREA` | Cumulative trends |
| Scatter | `XL_CHART_TYPE.XY_SCATTER` | Correlation analysis |
| Bubble | `XL_CHART_TYPE.BUBBLE` | Three-variable comparison |
| Radar | `XL_CHART_TYPE.RADAR` | Multi-axis comparison |

---

## Column Chart (Python)

```python
from pptx import Presentation
from pptx.chart.data import CategoryChartData
from pptx.enum.chart import XL_CHART_TYPE
from pptx.util import Inches, Pt
from pptx.dml.color import RgbColor

prs = Presentation()
slide = prs.slides.add_slide(prs.slide_layouts[5])  # Title Only

# Chart data
chart_data = CategoryChartData()
chart_data.categories = ['Q1', 'Q2', 'Q3', 'Q4']
chart_data.add_series('2024', (120, 145, 160, 185))
chart_data.add_series('2025', (150, 175, 195, 225))

# Add chart
x, y, cx, cy = Inches(0.5), Inches(1.5), Inches(9), Inches(5)
chart = slide.shapes.add_chart(
    XL_CHART_TYPE.COLUMN_CLUSTERED,
    x, y, cx, cy,
    chart_data
).chart

# Style the chart
chart.has_legend = True
chart.legend.include_in_layout = False

# Style series colors
series_colors = [
    RgbColor(0x00, 0x66, 0xCC),  # Blue
    RgbColor(0x00, 0x99, 0xFF),  # Light blue
]
for idx, series in enumerate(chart.series):
    series.format.fill.solid()
    series.format.fill.fore_color.rgb = series_colors[idx]

prs.save('column_chart.pptx')
```

---

## Line Chart with Markers

```python
# Assumes you already imported `CategoryChartData` and `Inches`, and have a `slide` reference.
from pptx.enum.chart import XL_CHART_TYPE, XL_MARKER_STYLE

chart_data = CategoryChartData()
chart_data.categories = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
chart_data.add_series('Revenue', (100, 110, 125, 140, 155, 180))
chart_data.add_series('Target', (100, 115, 130, 145, 160, 175))

chart = slide.shapes.add_chart(
    XL_CHART_TYPE.LINE_MARKERS,
    Inches(0.5), Inches(1.5), Inches(9), Inches(5),
    chart_data
).chart

# Configure markers
for series in chart.series:
    series.marker.style = XL_MARKER_STYLE.CIRCLE
    series.marker.size = 8
```

---

## Pie Chart

```python
from pptx.chart.data import CategoryChartData
from pptx.enum.chart import XL_CHART_TYPE

chart_data = CategoryChartData()
chart_data.categories = ['Product A', 'Product B', 'Product C', 'Other']
chart_data.add_series('Market Share', (35, 28, 22, 15))

chart = slide.shapes.add_chart(
    XL_CHART_TYPE.PIE,
    Inches(2), Inches(1.5), Inches(6), Inches(5),
    chart_data
).chart

# Add data labels
plot = chart.plots[0]
plot.has_data_labels = True
data_labels = plot.data_labels
data_labels.show_percentage = True
data_labels.show_category_name = True
data_labels.show_value = False
```

---

## Combo Chart (Column + Line)

```python
from pptx.chart.data import CategoryChartData
from pptx.enum.chart import XL_CHART_TYPE

# Create column chart first
chart_data = CategoryChartData()
chart_data.categories = ['Q1', 'Q2', 'Q3', 'Q4']
chart_data.add_series('Revenue', (100, 150, 180, 225))
chart_data.add_series('Growth %', (10, 15, 12, 25))

chart = slide.shapes.add_chart(
    XL_CHART_TYPE.COLUMN_CLUSTERED,
    Inches(0.5), Inches(1.5), Inches(9), Inches(5),
    chart_data
).chart

# Change second series to line (requires XML manipulation)
# python-pptx doesn't natively support combo charts
# Consider pptxgenjs for native combo chart support
```

---

## Charts in Node.js (pptxgenjs)

```typescript
import pptxgen from 'pptxgenjs';

async function main() {
  const pptx = new pptxgen();

  // Bar chart
  let slide = pptx.addSlide();
  slide.addChart(pptx.ChartType.bar, [
    { name: 'Q1', labels: ['Sales', 'Costs', 'Profit'], values: [100, 70, 30] },
    { name: 'Q2', labels: ['Sales', 'Costs', 'Profit'], values: [120, 75, 45] },
    { name: 'Q3', labels: ['Sales', 'Costs', 'Profit'], values: [140, 80, 60] },
    { name: 'Q4', labels: ['Sales', 'Costs', 'Profit'], values: [180, 90, 90] },
  ], {
    x: 0.5, y: 1.5, w: 9, h: 5,
    showLegend: true,
    legendPos: 'b',
    showTitle: true,
    title: 'Quarterly Performance',
    barDir: 'bar',  // horizontal bars
    barGrouping: 'clustered',
  });

  // Line chart
  slide = pptx.addSlide();
  slide.addChart(pptx.ChartType.line, [
    { name: 'Actual', labels: ['Jan','Feb','Mar','Apr','May','Jun'], values: [10,20,30,40,50,60] },
    { name: 'Target', labels: ['Jan','Feb','Mar','Apr','May','Jun'], values: [15,25,35,45,55,65] },
  ], {
    x: 0.5, y: 1.5, w: 9, h: 5,
    showLegend: true,
    lineDataSymbol: 'circle',
    lineDataSymbolSize: 8,
  });

  // Pie chart
  slide = pptx.addSlide();
  slide.addChart(pptx.ChartType.pie, [
    { name: 'Market Share', labels: ['Product A','Product B','Product C'], values: [40, 35, 25] },
  ], {
    x: 2, y: 1.5, w: 6, h: 5,
    showLegend: true,
    showPercent: true,
    showValue: false,
  });

  // "Combo-like" chart: column series plus line styling options (see PptxGenJS docs for true combos)
  slide = pptx.addSlide();
  slide.addChart(pptx.ChartType.bar, [
    { name: 'Revenue', labels: ['Q1','Q2','Q3','Q4'], values: [100,150,180,225] },
  ], {
    x: 0.5, y: 1.5, w: 9, h: 5,
    chartColors: ['0066CC'],
    catAxisTitle: 'Quarter',
    valAxisTitle: 'Revenue ($K)',
    showValue: true,
    lineDataSymbol: 'none',
  });

  await pptx.writeFile({ fileName: 'charts.pptx' });
}

main();
```

---

## Chart Styling Best Practices

### Colors
```python
# Use brand colors consistently
from pptx.dml.color import RgbColor

CHART_COLORS = [
    RgbColor(0x00, 0x66, 0xCC),  # Primary
    RgbColor(0x00, 0x99, 0xFF),  # Secondary
    RgbColor(0xFF, 0x66, 0x00),  # Accent
    RgbColor(0x66, 0x66, 0x66),  # Neutral
]
```

### Data Labels
```python
plot = chart.plots[0]
plot.has_data_labels = True
data_labels = plot.data_labels
data_labels.font.size = Pt(10)
data_labels.font.color.rgb = RgbColor(0x33, 0x33, 0x33)
data_labels.number_format = '#,##0'  # Thousands separator
```

### Axis Formatting
```python
# Value axis
value_axis = chart.value_axis
value_axis.has_major_gridlines = True
value_axis.major_gridlines.format.line.color.rgb = RgbColor(0xE0, 0xE0, 0xE0)
value_axis.tick_labels.font.size = Pt(10)
value_axis.tick_labels.number_format = '$#,##0K'

# Category axis
category_axis = chart.category_axis
category_axis.tick_labels.font.size = Pt(10)
category_axis.tick_labels.font.bold = False
```

---

## Dynamic Data from DataFrame

```python
import pandas as pd
from pptx.chart.data import CategoryChartData

# Sample DataFrame
df = pd.DataFrame({
    'Quarter': ['Q1', 'Q2', 'Q3', 'Q4'],
    'Revenue': [100, 150, 180, 225],
    'Costs': [70, 85, 95, 110],
    'Profit': [30, 65, 85, 115]
})

# Build chart data from DataFrame
chart_data = CategoryChartData()
chart_data.categories = df['Quarter'].tolist()

for col in ['Revenue', 'Costs', 'Profit']:
    chart_data.add_series(col, df[col].tolist())

# Add to slide
chart = slide.shapes.add_chart(
    XL_CHART_TYPE.COLUMN_CLUSTERED,
    Inches(0.5), Inches(1.5), Inches(9), Inches(5),
    chart_data
).chart
```

---

## Chart from Database Query

```python
import sqlite3
from pptx.chart.data import CategoryChartData

# Query database
conn = sqlite3.connect('sales.db')
cursor = conn.execute('''
    SELECT quarter, SUM(revenue), SUM(costs)
    FROM sales
    WHERE year = 2025
    GROUP BY quarter
    ORDER BY quarter
''')
rows = cursor.fetchall()
conn.close()

# Build chart
chart_data = CategoryChartData()
chart_data.categories = [row[0] for row in rows]
chart_data.add_series('Revenue', [row[1] for row in rows])
chart_data.add_series('Costs', [row[2] for row in rows])
```

---

## Related Resources

- [pptx-layouts.md](pptx-layouts.md) - Master slides and themes
- [../assets/pitch-deck.md](../assets/pitch-deck.md) - Charts in pitch context
- [../assets/quarterly-review.md](../assets/quarterly-review.md) - Business charts
