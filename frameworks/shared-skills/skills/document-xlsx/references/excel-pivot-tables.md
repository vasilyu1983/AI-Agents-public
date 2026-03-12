# Excel Pivot Tables and Summary Data Reference

Patterns for generating pivot-style summaries using Python and Node.js libraries.

---

## Contents

- Library limitations for native pivot tables
- pandas pivot_table to Excel workflow
- xlwings native pivot table creation
- Summary table patterns (cross-tab, running totals, YoY)
- Structuring data for pivot-readiness
- Do / Avoid

---

## Library Limitations

| Library | Native Pivot Support | Notes |
|---------|---------------------|-------|
| openpyxl | No | Can read existing pivots, cannot create |
| XlsxWriter | No | Cannot create or modify pivot tables |
| ExcelJS / SheetJS | No / Read-only | No creation API |
| xlwings | Yes | Requires Excel installed on the machine |
| win32com | Yes | Windows + Excel only |

If the runtime has no Excel installation, generate pre-computed summary tables instead.

---

## pandas pivot_table to Excel

```python
import pandas as pd

df = pd.DataFrame({
    "Region": ["East", "East", "West", "West", "East", "West"],
    "Product": ["A", "B", "A", "B", "A", "B"],
    "Revenue": [100, 200, 150, 250, 120, 180],
    "Units": [10, 20, 15, 25, 12, 18],
})

# Single aggregation with grand totals
summary = pd.pivot_table(
    df, values="Revenue", index="Region", columns="Product",
    aggfunc="sum", margins=True, margins_name="Total"
)

# Multiple aggregations
detail = pd.pivot_table(
    df, values=["Revenue", "Units"], index="Region", columns="Product",
    aggfunc={"Revenue": "sum", "Units": "mean"}, fill_value=0
)

with pd.ExcelWriter("report.xlsx", engine="openpyxl") as writer:
    summary.to_excel(writer, sheet_name="Summary")
    detail.to_excel(writer, sheet_name="Detail")
    df.to_excel(writer, sheet_name="Raw Data", index=False)
```

---

## xlwings Native Pivot (Requires Excel)

```python
import xlwings as xw

app = xw.App(visible=False)
wb = app.books.open("data.xlsx")
ws_data = wb.sheets["Raw Data"]
ws_pivot = wb.sheets.add("PivotReport")

src = ws_data.range("A1").expand()
pt = wb.api.PivotCaches().Create(
    SourceType=1, SourceData=src.api
).CreatePivotTable(
    TableDestination=ws_pivot.range("A3").api, TableName="SalesPivot"
)
pt.PivotFields("Region").Orientation = 1   # xlRowField
pt.PivotFields("Product").Orientation = 2  # xlColumnField
pt.AddDataField(pt.PivotFields("Revenue"), "Sum of Revenue", -4157)

wb.save("report_with_pivot.xlsx")
wb.close()
app.quit()
```

Not suitable for headless Linux CI -- COM/AppleScript bridge required.

---

## Summary Table Patterns

```python
# Cross-tab
cross = pd.crosstab(df["Region"], df["Product"],
                     values=df["Revenue"], aggfunc="sum", margins=True)

# Running totals
monthly = df.groupby("Month")["Revenue"].sum().reset_index()
monthly["Cumulative"] = monthly["Revenue"].cumsum()

# Year-over-year comparison
yoy = df.pivot_table(values="Revenue", index="Month", columns="Year", aggfunc="sum")
yoy["YoY Change"] = yoy[2025] - yoy[2024]
yoy["YoY %"] = ((yoy[2025] - yoy[2024]) / yoy[2024] * 100).round(1)
```

---

## Structuring Data for Pivot-Readiness

Pivots require tidy, flat data. Verify these properties before generating:

1. One header row -- no merged cells in the header
2. Every column has a unique, non-empty name
3. No blank rows or columns within the data block
4. Consistent types per column (no mixed text/numbers)
5. Dates stored as date objects, not strings
6. No subtotals or totals mixed into data rows

```python
df.columns = df.columns.str.strip()
df = df.dropna(how="all")
df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce").fillna(0)
```

---

## When Native Pivots vs Pre-Computed

| Scenario | Recommendation |
|----------|---------------|
| Recipients need interactive slice/filter | Native pivot (xlwings) |
| Read-only report or email attachment | Pre-computed summary |
| Headless Linux CI | Pre-computed summary |
| File must open in Google Sheets / LibreOffice | Pre-computed summary |
| Strict audit trail required | Pre-computed (frozen values) |

---

## Do / Avoid

**Do:**
- Include a "Raw Data" sheet so recipients can build their own pivots
- Use `margins=True` in pandas to add Grand Total rows/columns
- Format summary output with openpyxl styles after writing
- Name the data range as an Excel Table for self-expanding pivot sources
- Validate aggregation results against source totals before saving

**Avoid:**
- Merged cells in pivot source data (breaks field detection)
- Multi-level column headers from pandas MultiIndex without flattening
- Assuming openpyxl or XlsxWriter can create native pivot tables
- Leaving `NaN` in numeric columns (use `fill_value=0`)
- Running xlwings in CI without a licensed Excel installation
