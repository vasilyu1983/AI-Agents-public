# Excel Formatting Reference

Styling, conditional formatting, and visual presentation for spreadsheets.

---

## Cell Styling

### Font Properties

```python
# openpyxl
from openpyxl.styles import Font

cell.font = Font(
    name='Calibri',
    size=11,
    bold=True,
    italic=False,
    underline='single',  # 'single', 'double', 'singleAccounting', 'doubleAccounting'
    strike=False,
    color='FF0000'  # ARGB hex (no #)
)
```

```typescript
// ExcelJS
cell.font = {
  name: 'Calibri',
  size: 11,
  bold: true,
  italic: false,
  underline: true,
  strike: false,
  color: { argb: 'FFFF0000' }
};
```

### Fill (Background Color)

```python
# openpyxl
from openpyxl.styles import PatternFill

# Solid fill
cell.fill = PatternFill(
    start_color='4472C4',
    end_color='4472C4',
    fill_type='solid'
)

# Gradient fill
from openpyxl.styles import GradientFill
cell.fill = GradientFill(
    type='linear',
    degree=90,
    stop=['4472C4', 'FFFFFF']
)
```

```typescript
// ExcelJS
cell.fill = {
  type: 'pattern',
  pattern: 'solid',
  fgColor: { argb: 'FF4472C4' }
};

// Gradient
cell.fill = {
  type: 'gradient',
  gradient: 'angle',
  degree: 90,
  stops: [
    { position: 0, color: { argb: 'FF4472C4' } },
    { position: 1, color: { argb: 'FFFFFFFF' } }
  ]
};
```

### Borders

```python
# openpyxl
from openpyxl.styles import Border, Side

thin_border = Border(
    left=Side(style='thin', color='000000'),
    right=Side(style='thin', color='000000'),
    top=Side(style='thin', color='000000'),
    bottom=Side(style='thin', color='000000')
)
cell.border = thin_border

# Border styles: 'thin', 'medium', 'thick', 'double', 'dotted', 'dashed'
```

```typescript
// ExcelJS
cell.border = {
  top: { style: 'thin', color: { argb: 'FF000000' } },
  left: { style: 'thin', color: { argb: 'FF000000' } },
  bottom: { style: 'thin', color: { argb: 'FF000000' } },
  right: { style: 'thin', color: { argb: 'FF000000' } }
};
```

### Alignment

```python
# openpyxl
from openpyxl.styles import Alignment

cell.alignment = Alignment(
    horizontal='center',  # 'left', 'center', 'right', 'justify'
    vertical='center',    # 'top', 'center', 'bottom'
    wrap_text=True,
    shrink_to_fit=False,
    indent=0,
    text_rotation=0  # -90 to 90 degrees
)
```

```typescript
// ExcelJS
cell.alignment = {
  horizontal: 'center',
  vertical: 'middle',
  wrapText: true,
  shrinkToFit: false,
  indent: 0,
  textRotation: 0
};
```

---

## Number Formatting

### Common Formats

| Format Code | Example Output | Use Case |
|-------------|----------------|----------|
| `General` | 1234.5 | Default |
| `0` | 1235 | Integer |
| `0.00` | 1234.50 | 2 decimals |
| `#,##0` | 1,235 | Thousands separator |
| `#,##0.00` | 1,234.50 | Currency without symbol |
| `$#,##0.00` | $1,234.50 | USD currency |
| `0%` | 50% | Percentage |
| `0.00%` | 50.00% | Percentage with decimals |
| `yyyy-mm-dd` | 2024-01-15 | ISO date |
| `mm/dd/yyyy` | 01/15/2024 | US date |
| `dd-mmm-yyyy` | 15-Jan-2024 | Readable date |
| `hh:mm:ss` | 14:30:00 | Time |
| `0.00E+00` | 1.23E+03 | Scientific |

### Implementation

```python
# openpyxl
cell.number_format = '$#,##0.00'
cell.number_format = 'yyyy-mm-dd'
cell.number_format = '0.00%'

# Custom format with color
cell.number_format = '[Green]$#,##0.00;[Red]-$#,##0.00'
```

```typescript
// ExcelJS
cell.numFmt = '$#,##0.00';
cell.numFmt = 'yyyy-mm-dd';
cell.numFmt = '0.00%';
```

---

## Conditional Formatting

### Color Scales (Heatmaps)

```python
from openpyxl.formatting.rule import ColorScaleRule

# 2-color scale (red to green)
rule = ColorScaleRule(
    start_type='min', start_color='FF0000',
    end_type='max', end_color='00FF00'
)
ws.conditional_formatting.add('B2:B100', rule)

# 3-color scale
rule = ColorScaleRule(
    start_type='min', start_color='FF0000',
    mid_type='percentile', mid_value=50, mid_color='FFFF00',
    end_type='max', end_color='00FF00'
)
ws.conditional_formatting.add('C2:C100', rule)
```

```typescript
// ExcelJS
sheet.addConditionalFormatting({
  ref: 'B2:B100',
  rules: [{
    type: 'colorScale',
    cfvo: [
      { type: 'min' },
      { type: 'max' }
    ],
    color: [
      { argb: 'FFFF0000' },
      { argb: 'FF00FF00' }
    ]
  }]
});
```

### Data Bars

```python
from openpyxl.formatting.rule import DataBarRule

rule = DataBarRule(
    start_type='min',
    end_type='max',
    color='4472C4',
    showValue=True,
    minLength=None,
    maxLength=None
)
ws.conditional_formatting.add('D2:D100', rule)
```

### Icon Sets

```python
from openpyxl.formatting.rule import IconSetRule

# Traffic lights
rule = IconSetRule(
    icon_style='3TrafficLights1',
    type='percent',
    values=[0, 33, 67],
    showValue=True,
    reverse=False
)
ws.conditional_formatting.add('E2:E100', rule)

# Icon styles: '3Arrows', '3TrafficLights1', '4Rating', '5Quarters'
```

### Formula-Based Rules

```python
from openpyxl.formatting.rule import FormulaRule
from openpyxl.styles import PatternFill

# Highlight rows where status = "Overdue"
red_fill = PatternFill(start_color='FFCCCC', fill_type='solid')
rule = FormulaRule(
    formula=['$C2="Overdue"'],
    fill=red_fill
)
ws.conditional_formatting.add('A2:E100', rule)

# Highlight duplicates
rule = FormulaRule(
    formula=['COUNTIF($A:$A,A2)>1'],
    fill=PatternFill(start_color='FFFFCC', fill_type='solid')
)
ws.conditional_formatting.add('A2:A100', rule)
```

### Cell Value Rules

```python
from openpyxl.formatting.rule import CellIsRule

# Greater than
rule = CellIsRule(
    operator='greaterThan',
    formula=['100'],
    fill=PatternFill(start_color='C6EFCE', fill_type='solid')
)
ws.conditional_formatting.add('B2:B100', rule)

# Between
rule = CellIsRule(
    operator='between',
    formula=['50', '100'],
    fill=PatternFill(start_color='FFEB9C', fill_type='solid')
)
ws.conditional_formatting.add('B2:B100', rule)

# Operators: 'lessThan', 'lessThanOrEqual', 'greaterThan',
#            'greaterThanOrEqual', 'equal', 'notEqual', 'between'
```

---

## Row and Column Formatting

### Column Width

```python
# openpyxl
ws.column_dimensions['A'].width = 20
ws.column_dimensions['B'].width = 15

# Auto-fit (approximate)
for column in ws.columns:
    max_length = max(len(str(cell.value or '')) for cell in column)
    ws.column_dimensions[column[0].column_letter].width = max_length + 2
```

```typescript
// ExcelJS
sheet.getColumn('A').width = 20;

// Set via column definition
sheet.columns = [
  { header: 'Name', key: 'name', width: 20 },
  { header: 'Value', key: 'value', width: 15 }
];
```

### Row Height

```python
# openpyxl
ws.row_dimensions[1].height = 30  # Header row

# All rows
for row in range(1, 101):
    ws.row_dimensions[row].height = 20
```

```typescript
// ExcelJS
sheet.getRow(1).height = 30;
```

### Freeze Panes

```python
# openpyxl - Freeze first row
ws.freeze_panes = 'A2'

# Freeze first column
ws.freeze_panes = 'B1'

# Freeze both
ws.freeze_panes = 'B2'
```

```typescript
// ExcelJS
sheet.views = [{ state: 'frozen', xSplit: 1, ySplit: 1 }];
```

### Hide Rows/Columns

```python
# openpyxl
ws.column_dimensions['C'].hidden = True
ws.row_dimensions[5].hidden = True
```

```typescript
// ExcelJS
sheet.getColumn('C').hidden = true;
sheet.getRow(5).hidden = true;
```

---

## Merged Cells

```python
# openpyxl
ws.merge_cells('A1:D1')  # Merge range
ws['A1'] = 'Report Title'
ws['A1'].alignment = Alignment(horizontal='center')

# Unmerge
ws.unmerge_cells('A1:D1')
```

```typescript
// ExcelJS
sheet.mergeCells('A1:D1');
sheet.getCell('A1').value = 'Report Title';
sheet.getCell('A1').alignment = { horizontal: 'center' };

// Unmerge
sheet.unMergeCells('A1:D1');
```

---

## Named Styles

```python
from openpyxl.styles import NamedStyle, Font, Border, Side, PatternFill

# Create reusable style
header_style = NamedStyle(name='header')
header_style.font = Font(bold=True, color='FFFFFF', size=12)
header_style.fill = PatternFill(start_color='4472C4', fill_type='solid')
header_style.border = Border(
    bottom=Side(style='medium', color='000000')
)

# Register style
wb.add_named_style(header_style)

# Apply to cells
for cell in ws[1]:
    cell.style = 'header'
```

---

## Page Setup (Print)

```python
# openpyxl
ws.page_setup.orientation = 'landscape'
ws.page_setup.paperSize = ws.PAPERSIZE_A4
ws.page_setup.fitToPage = True
ws.page_setup.fitToWidth = 1
ws.page_setup.fitToHeight = 0  # Auto

# Print titles (repeat rows/columns)
ws.print_title_rows = '1:1'  # Repeat row 1
ws.print_title_cols = 'A:A'  # Repeat column A

# Print area
ws.print_area = 'A1:F50'

# Headers/footers
ws.oddHeader.center.text = 'Monthly Report'
ws.oddFooter.center.text = 'Page &P of &N'
```

---

## Style Presets

### Header Style

```python
def style_header_row(ws, row=1):
    """Apply professional header styling."""
    header_fill = PatternFill(start_color='4472C4', fill_type='solid')
    header_font = Font(bold=True, color='FFFFFF', size=11)
    header_border = Border(bottom=Side(style='medium', color='000000'))

    for cell in ws[row]:
        cell.fill = header_fill
        cell.font = header_font
        cell.border = header_border
        cell.alignment = Alignment(horizontal='center', vertical='center')
```

### Alternating Row Colors

```python
def style_alternating_rows(ws, start_row=2, end_row=100):
    """Apply zebra striping."""
    light_fill = PatternFill(start_color='F2F2F2', fill_type='solid')

    for row in range(start_row, end_row + 1):
        if row % 2 == 0:
            for cell in ws[row]:
                cell.fill = light_fill
```

### Currency Column

```python
def style_currency_column(ws, col, start_row=2, end_row=100):
    """Format column as currency with conditional colors."""
    for row in range(start_row, end_row + 1):
        cell = ws.cell(row=row, column=col)
        cell.number_format = '$#,##0.00'

        if cell.value and cell.value < 0:
            cell.font = Font(color='FF0000')
```

---

## Color Reference

### Excel Theme Colors

| Color Name | Hex Code | ARGB |
|------------|----------|------|
| Blue (Accent 1) | #4472C4 | FF4472C4 |
| Orange (Accent 2) | #ED7D31 | FFED7D31 |
| Gray (Accent 3) | #A5A5A5 | FFA5A5A5 |
| Yellow (Accent 4) | #FFC000 | FFFFC000 |
| Blue (Accent 5) | #5B9BD5 | FF5B9BD5 |
| Green (Accent 6) | #70AD47 | FF70AD47 |

### Status Colors

| Status | Hex | Usage |
|--------|-----|-------|
| Success | #C6EFCE | Light green background |
| Warning | #FFEB9C | Light yellow background |
| Error | #FFC7CE | Light red background |
| Info | #BDD7EE | Light blue background |
