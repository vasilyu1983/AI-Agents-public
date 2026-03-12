# Excel Charts Reference

Chart creation and customization for data visualization in spreadsheets.

---

## Chart Types Overview

| Chart Type | Best For | openpyxl Class |
|------------|----------|----------------|
| Bar/Column | Comparisons | `BarChart` |
| Line | Trends over time | `LineChart` |
| Pie | Part of whole | `PieChart` |
| Area | Cumulative trends | `AreaChart` |
| Scatter | Correlations | `ScatterChart` |
| Doughnut | Part of whole (variant) | `DoughnutChart` |
| Radar | Multi-variable comparison | `RadarChart` |
| Bubble | 3-variable relationships | `BubbleChart` |
| Stock | OHLC financial data | `StockChart` |

---

## Bar/Column Charts

### Basic Bar Chart (Python)

```python
from openpyxl import Workbook
from openpyxl.chart import BarChart, Reference

wb = Workbook()
ws = wb.active

# Sample data
data = [
    ['Product', 'Sales'],
    ['Widget A', 1200],
    ['Widget B', 800],
    ['Widget C', 1500],
    ['Widget D', 950],
]
for row in data:
    ws.append(row)

# Create chart
chart = BarChart()
chart.type = 'col'  # 'col' for vertical, 'bar' for horizontal
chart.style = 10
chart.title = 'Product Sales'
chart.x_axis.title = 'Product'
chart.y_axis.title = 'Sales ($)'

# Data references
data_ref = Reference(ws, min_col=2, min_row=1, max_row=5, max_col=2)
categories = Reference(ws, min_col=1, min_row=2, max_row=5)

chart.add_data(data_ref, titles_from_data=True)
chart.set_categories(categories)
chart.shape = 4  # Rounded corners

# Position chart
ws.add_chart(chart, 'D2')
wb.save('bar_chart.xlsx')
```

### Stacked Bar Chart

```python
chart = BarChart()
chart.type = 'col'
chart.grouping = 'stacked'  # 'standard', 'stacked', 'percentStacked'

# Multiple data series
data_ref = Reference(ws, min_col=2, min_row=1, max_row=10, max_col=4)
chart.add_data(data_ref, titles_from_data=True)
```

### Clustered Bar with Custom Colors

```python
from openpyxl.chart.series import DataPoint
from openpyxl.drawing.fill import PatternFillProperties, ColorChoice

chart = BarChart()
chart.add_data(data_ref, titles_from_data=True)
chart.set_categories(categories)

# Custom series colors
colors = ['4472C4', 'ED7D31', '70AD47']
for i, series in enumerate(chart.series):
    series.graphicalProperties.solidFill = colors[i % len(colors)]
```

---

## Line Charts

### Basic Line Chart

```python
from openpyxl.chart import LineChart, Reference

chart = LineChart()
chart.style = 10
chart.title = 'Monthly Trend'
chart.x_axis.title = 'Month'
chart.y_axis.title = 'Value'

data_ref = Reference(ws, min_col=2, min_row=1, max_row=13, max_col=2)
categories = Reference(ws, min_col=1, min_row=2, max_row=13)

chart.add_data(data_ref, titles_from_data=True)
chart.set_categories(categories)

ws.add_chart(chart, 'D2')
```

### Multi-Series Line Chart

```python
chart = LineChart()
chart.title = 'Year over Year Comparison'

# Add multiple data columns
data_ref = Reference(ws, min_col=2, min_row=1, max_row=13, max_col=4)
chart.add_data(data_ref, titles_from_data=True)
chart.set_categories(categories)

# Customize line styles
for i, series in enumerate(chart.series):
    series.graphicalProperties.line.width = 25000  # EMUs (25000 = ~2pt)
    series.smooth = True  # Smooth lines
```

### Line with Markers

```python
from openpyxl.chart.marker import Marker

chart = LineChart()
chart.add_data(data_ref, titles_from_data=True)

for series in chart.series:
    series.marker = Marker(symbol='circle', size=7)
    series.graphicalProperties.line.width = 20000
```

---

## Pie Charts

### Basic Pie Chart

```python
from openpyxl.chart import PieChart, Reference

chart = PieChart()
chart.title = 'Market Share'

data_ref = Reference(ws, min_col=2, min_row=1, max_row=5)
labels = Reference(ws, min_col=1, min_row=2, max_row=5)

chart.add_data(data_ref, titles_from_data=True)
chart.set_categories(labels)

ws.add_chart(chart, 'D2')
```

### Pie Chart with Data Labels

```python
from openpyxl.chart.label import DataLabelList

chart = PieChart()
chart.add_data(data_ref, titles_from_data=True)
chart.set_categories(labels)

# Data labels
chart.dataLabels = DataLabelList()
chart.dataLabels.showCatName = True
chart.dataLabels.showPercent = True
chart.dataLabels.showVal = False
```

### Exploded Pie

```python
from openpyxl.chart.series import DataPoint

chart = PieChart()
chart.add_data(data_ref, titles_from_data=True)

# Explode first slice
slice = DataPoint(idx=0, explosion=10)  # 10% explosion
chart.series[0].data_points = [slice]
```

### Doughnut Chart

```python
from openpyxl.chart import DoughnutChart

chart = DoughnutChart()
chart.title = 'Budget Allocation'
chart.holeSize = 50  # Inner hole size (percentage)

chart.add_data(data_ref, titles_from_data=True)
chart.set_categories(labels)
```

---

## Area Charts

```python
from openpyxl.chart import AreaChart

chart = AreaChart()
chart.style = 10
chart.title = 'Cumulative Growth'
chart.grouping = 'stacked'  # 'standard', 'stacked', 'percentStacked'

data_ref = Reference(ws, min_col=2, min_row=1, max_row=13, max_col=4)
chart.add_data(data_ref, titles_from_data=True)
chart.set_categories(categories)

ws.add_chart(chart, 'D2')
```

---

## Scatter Charts

### Basic Scatter Plot

```python
from openpyxl.chart import ScatterChart, Reference, Series

chart = ScatterChart()
chart.style = 13
chart.title = 'Correlation Analysis'
chart.x_axis.title = 'Variable X'
chart.y_axis.title = 'Variable Y'

xvalues = Reference(ws, min_col=1, min_row=2, max_row=50)
yvalues = Reference(ws, min_col=2, min_row=2, max_row=50)

series = Series(yvalues, xvalues, title='Data Points')
chart.series.append(series)

ws.add_chart(chart, 'D2')
```

### Scatter with Trendline

```python
from openpyxl.chart.trendline import Trendline

chart = ScatterChart()
# ... add data ...

# Add linear trendline
trendline = Trendline(trendlineType='linear')
chart.series[0].trendline = trendline

# Other types: 'exp', 'log', 'poly', 'power', 'movingAvg'
```

---

## Combo Charts

### Column + Line Combination

```python
from openpyxl.chart import BarChart, LineChart, Reference

# Primary chart (columns)
bar_chart = BarChart()
bar_chart.type = 'col'
bar_data = Reference(ws, min_col=2, min_row=1, max_row=13)
bar_chart.add_data(bar_data, titles_from_data=True)
bar_chart.set_categories(categories)

# Secondary chart (line)
line_chart = LineChart()
line_data = Reference(ws, min_col=3, min_row=1, max_row=13)
line_chart.add_data(line_data, titles_from_data=True)

# Use secondary Y axis
line_chart.y_axis.axId = 200
line_chart.y_axis.crosses = 'max'

# Combine charts
bar_chart += line_chart

ws.add_chart(bar_chart, 'D2')
```

---

## Chart Customization

### Size and Position

```python
chart.width = 15  # Width in cm
chart.height = 10  # Height in cm

# Anchor position
ws.add_chart(chart, 'D2')  # Top-left cell

# Alternative: absolute positioning
from openpyxl.drawing.spreadsheet_drawing import AnchorMarker
chart.anchor = 'D2'  # Or use TwoCellAnchor for resizing with cells
```

### Legend Position

```python
from openpyxl.chart.legend import Legend

chart.legend = Legend()
chart.legend.position = 'b'  # 'b'=bottom, 't'=top, 'l'=left, 'r'=right, 'tr'=top-right
chart.legend.overlay = False

# Hide legend
chart.legend = None
```

### Axis Formatting

```python
# Number format
chart.y_axis.numFmt = '$#,##0'

# Axis bounds
chart.y_axis.scaling.min = 0
chart.y_axis.scaling.max = 10000

# Axis title
chart.x_axis.title = 'Quarter'
chart.y_axis.title = 'Revenue ($)'

# Hide axis
chart.x_axis.delete = True
```

### Gridlines

```python
from openpyxl.chart.axis import ChartLines

# Major gridlines
chart.y_axis.majorGridlines = ChartLines()

# Hide gridlines
chart.y_axis.majorGridlines = None
chart.y_axis.minorGridlines = None
```

### Title Formatting

```python
from openpyxl.chart.text import RichText
from openpyxl.drawing.text import Paragraph, ParagraphProperties, CharacterProperties

chart.title = 'Sales Report'

# Styled title
props = CharacterProperties(b=True, sz=1400)  # Bold, 14pt
para = Paragraph(pPr=ParagraphProperties(defRPr=props), r=[])
chart.title.tx.rich.p = [para]
```

---

## Chart Templates

### Dashboard KPI Chart

```python
def create_kpi_chart(ws, data_range, title, position):
    """Create a clean KPI column chart."""
    chart = BarChart()
    chart.type = 'col'
    chart.style = 10
    chart.title = title

    data = Reference(ws, **data_range)
    chart.add_data(data, titles_from_data=True)

    # Clean styling
    chart.legend = None
    chart.y_axis.majorGridlines = ChartLines()
    chart.y_axis.numFmt = '#,##0'

    # Color scheme
    chart.series[0].graphicalProperties.solidFill = '4472C4'

    chart.width = 10
    chart.height = 6

    ws.add_chart(chart, position)
    return chart
```

### Trend Analysis Chart

```python
def create_trend_chart(ws, data_range, categories_range, title, position):
    """Create line chart with trendline."""
    chart = LineChart()
    chart.style = 10
    chart.title = title

    data = Reference(ws, **data_range)
    cats = Reference(ws, **categories_range)

    chart.add_data(data, titles_from_data=True)
    chart.set_categories(cats)

    # Smooth lines with markers
    for series in chart.series:
        series.smooth = True
        series.marker = Marker(symbol='circle', size=5)

    # Add trendline
    chart.series[0].trendline = Trendline(trendlineType='linear')

    chart.width = 12
    chart.height = 7

    ws.add_chart(chart, position)
    return chart
```

### Comparison Pie Chart

```python
def create_comparison_pie(ws, data_range, labels_range, title, position):
    """Create pie chart with percentage labels."""
    chart = PieChart()
    chart.title = title

    data = Reference(ws, **data_range)
    labels = Reference(ws, **labels_range)

    chart.add_data(data, titles_from_data=True)
    chart.set_categories(labels)

    # Show percentages
    chart.dataLabels = DataLabelList()
    chart.dataLabels.showPercent = True
    chart.dataLabels.showCatName = True
    chart.dataLabels.showVal = False

    chart.width = 10
    chart.height = 8

    ws.add_chart(chart, position)
    return chart
```

---

## ExcelJS Charts (Node.js)

ExcelJS has limited native chart support. For complex charts, consider:

1. **Template approach**: Create chart in Excel, use as template
2. **Hybrid**: Generate data with ExcelJS, open in Excel for charts
3. **Alternative**: Use xlsx-chart or chart.js for image export

```typescript
// ExcelJS basic image embedding (for pre-rendered charts)
import ExcelJS from 'exceljs';

const workbook = new ExcelJS.Workbook();
const sheet = workbook.addWorksheet('Report');

// Add image (chart exported as PNG)
const imageId = workbook.addImage({
  filename: 'chart.png',
  extension: 'png',
});

sheet.addImage(imageId, {
  tl: { col: 4, row: 1 },
  ext: { width: 500, height: 300 }
});
```

---

## Chart Styles Reference

| Style # | Description |
|---------|-------------|
| 1 | Default colors |
| 2 | Outline style |
| 3 | Gradient fills |
| 10 | Clean, professional |
| 11 | Subtle colors |
| 12 | Bold colors |
| 13 | Two-tone |

Use `chart.style = N` to apply built-in Excel chart styles.
