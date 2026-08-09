# Excel Tables and Structured References

Use Excel Tables as the default container for exported data blocks. Tables improve filtering, totals, formulas, readability, and downstream pivot/chart behavior.

---
## Table of Contents

- [Why Tables First](#why-tables-first)
- [XlsxWriter](#xlsxwriter)
- [openpyxl](#openpyxl)
- [ExcelJS](#exceljs)
- [Office Scripts](#office-scripts)
- [Structured Formula Patterns](#structured-formula-patterns)
- [Do / Avoid](#do-avoid)


## Why Tables First

| Benefit | Why it matters |
|---------|----------------|
| Stable ranges | Formulas, charts, and pivots expand with the table |
| Structured formulas | `=SUM(SalesTable[Revenue])` is easier to audit than `=SUM(D2:D5000)` |
| Built-in filters | Users get filters without ad hoc range guessing |
| Totals rows | Common aggregates can be exposed without hand-written footer formulas |
| Accessibility | Explicit headers and bounded data regions are easier to navigate |

---

## XlsxWriter

```python
import pandas as pd

df = pd.DataFrame(
    [
        {"region": "East", "product": "A", "revenue": 100},
        {"region": "West", "product": "B", "revenue": 150},
    ]
)

with pd.ExcelWriter("table_report.xlsx", engine="xlsxwriter") as writer:
    df.to_excel(writer, sheet_name="Raw Data", index=False, startrow=0)
    workbook = writer.book
    worksheet = writer.sheets["Raw Data"]

    worksheet.add_table(
        0,
        0,
        len(df),
        len(df.columns) - 1,
        {
            "name": "SalesTable",
            "style": "Table Style Medium 2",
            "total_row": True,
            "columns": [
                {"header": "region"},
                {"header": "product"},
                {"header": "revenue", "total_function": "sum"},
            ],
        },
    )
    worksheet.freeze_panes(1, 0)
```

---

## openpyxl

```python
from openpyxl import Workbook
from openpyxl.worksheet.table import Table, TableStyleInfo

wb = Workbook()
ws = wb.active
ws.title = "Raw Data"
ws.append(["region", "product", "revenue"])
ws.append(["East", "A", 100])
ws.append(["West", "B", 150])

table = Table(displayName="SalesTable", ref="A1:C3")
table.tableStyleInfo = TableStyleInfo(
    name="TableStyleMedium2",
    showFirstColumn=False,
    showLastColumn=False,
    showRowStripes=True,
    showColumnStripes=False,
)
ws.add_table(table)
wb.save("table_report.xlsx")
```

---

## ExcelJS

```typescript
import ExcelJS from "exceljs";

const workbook = new ExcelJS.Workbook();
const worksheet = workbook.addWorksheet("Raw Data");

worksheet.columns = [
  { header: "region", key: "region", width: 12 },
  { header: "product", key: "product", width: 12 },
  { header: "revenue", key: "revenue", width: 14 },
];

worksheet.addRows([
  { region: "East", product: "A", revenue: 100 },
  { region: "West", product: "B", revenue: 150 },
]);

worksheet.addTable({
  name: "SalesTable",
  ref: "A1",
  headerRow: true,
  totalsRow: true,
  style: { theme: "TableStyleMedium2", showRowStripes: true },
  columns: [
    { name: "region" },
    { name: "product" },
    { name: "revenue", totalsRowFunction: "sum" },
  ],
  rows: [
    ["East", "A", 100],
    ["West", "B", 150],
  ],
});

await workbook.xlsx.writeFile("table_report.xlsx");
```

---

## Office Scripts

```typescript
function main(workbook: ExcelScript.Workbook) {
  const ws = workbook.getWorksheet("Raw Data");
  const range = ws.getUsedRange();
  const table = ws.addTable(range, true);
  table.setName("SalesTable");
  table.setShowTotals(true);
}
```

---

## Structured Formula Patterns

| Goal | Formula |
|------|---------|
| Sum a column | `=SUM(SalesTable[Revenue])` |
| Current row math | `=[@qty]*[@price]` |
| Count non-empty items | `=COUNTA(SalesTable[product])` |
| Average by table column | `=AVERAGE(SalesTable[margin])` |

Use structured references for workbook models that will be reviewed by humans. They are more verbose than cell references, but far easier to audit.

---

## Do / Avoid

**Do:**
- Use one header row at the top of the table
- Give each table a descriptive, stable name
- Freeze the header row and keep totals rows explicit
- Build charts and pivots from tables instead of guessed ranges

**Avoid:**
- Merged cells in the header row
- Blank columns inside the table block
- Duplicate header names
- Hardcoded footer formulas that drift away from the data block
