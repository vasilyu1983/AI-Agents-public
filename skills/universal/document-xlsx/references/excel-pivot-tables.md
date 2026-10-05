# Excel Pivot Tables and Summary Data Reference

Choosing between native pivots and pre-computed summaries, and making the data pivot-ready.

## Contents

- [Runtime Support Matrix](#runtime-support-matrix)
- [When Native Pivots vs Pre-Computed](#when-native-pivots-vs-pre-computed)
- [Pre-Computed Summaries With pandas](#pre-computed-summaries-with-pandas)
- [Office Scripts Native Pivot (Microsoft 365)](#office-scripts-native-pivot-microsoft-365)
- [xlwings Native Pivot (Requires Excel)](#xlwings-native-pivot-requires-excel)
- [Structuring Data for Pivot-Readiness](#structuring-data-for-pivot-readiness)
- [Do / Avoid](#do--avoid)

## Runtime Support Matrix

| Library | Native pivot creation | Notes |
|---------|-----------------------|-------|
| openpyxl | No | Preserves existing pivots on load/save in simple cases; cannot create them |
| XlsxWriter | No | Write-only; no pivots |
| ExcelJS | Partial in some releases | Check the project's docs for your installed version and open the result in Excel before relying on it |
| SheetJS | No | Ingestion and transformation only |
| Office Scripts | Yes | Excel on the web, for workbooks in OneDrive or SharePoint |
| xlwings / win32com | Yes | Needs a licensed desktop Excel on the machine |

If the runtime has neither a desktop Excel installation nor a Microsoft 365 workbook context, generate pre-computed summary tables.

## When Native Pivots vs Pre-Computed

| Scenario | Recommendation |
|----------|---------------|
| Recipients need interactive slicing in Microsoft 365 | Native pivot (Office Scripts) |
| Recipients need interactive slicing in desktop Excel | Native pivot (xlwings) |
| Read-only report or email attachment | Pre-computed summary |
| Headless Linux CI | Pre-computed summary |
| File must open in Google Sheets or LibreOffice | Pre-computed summary |
| Strict audit trail required | Pre-computed summary (frozen values plus the raw data) |

## Pre-Computed Summaries With pandas

```python
summary = pd.pivot_table(df, values="Revenue", index="Region", columns="Product",
                         aggfunc="sum", margins=True, margins_name="Total")

# Period-over-period without hard-coded years
by_year = df.pivot_table(values="Revenue", index="Month", columns="Year", aggfunc="sum")
cur, prev = by_year.columns[-1], by_year.columns[-2]
by_year["Change"] = by_year[cur] - by_year[prev]
by_year["Change %"] = (by_year["Change"] / by_year[prev]).round(3)   # format as 0.0%
```

- Flatten a MultiIndex before writing (`df.columns = [" ".join(map(str, c)).strip() for c in df.columns]`). Otherwise the sheet gets stacked header rows that break filters and table conversion.
- Reconcile before saving: the grand total of the summary must equal the sum of the source column. Fail the build if they differ.
- Write the raw data to its own sheet, as an Excel Table, so recipients can build their own pivots.

## Office Scripts Native Pivot (Microsoft 365)

```typescript
function main(workbook: ExcelScript.Workbook) {
  const raw = workbook.getWorksheet("Raw Data");
  const sourceTable = raw.addTable(raw.getUsedRange(), true);
  sourceTable.setName("SalesTable");

  const pivotSheet = workbook.addWorksheet("Pivot");
  const pivot = workbook.addPivotTable("SalesPivot", sourceTable, pivotSheet.getRange("A1"));
  pivot.addRowHierarchy(pivot.getHierarchy("Region"));
  pivot.addColumnHierarchy(pivot.getHierarchy("Product"));
  pivot.addDataHierarchy(pivot.getHierarchy("Revenue"));
}
```

Using a Table as the source makes the pivot follow appended rows after a refresh.

## xlwings Native Pivot (Requires Excel)

```python
import xlwings as xw

app = xw.App(visible=False)
try:
    wb = app.books.open("data.xlsx")
    src = wb.sheets["Raw Data"].range("A1").expand()
    dest = wb.sheets.add("PivotReport")
    pt = wb.api.PivotCaches().Create(SourceType=1, SourceData=src.api).CreatePivotTable(
        TableDestination=dest.range("A3").api, TableName="SalesPivot")
    pt.PivotFields("Region").Orientation = 1   # xlRowField
    pt.PivotFields("Product").Orientation = 2  # xlColumnField
    pt.AddDataField(pt.PivotFields("Revenue"), "Sum of Revenue", -4157)  # xlSum
    wb.save("report_with_pivot.xlsx")
finally:
    app.quit()   # a crashed script otherwise leaves a hidden Excel process
```

This is the Windows COM object model. On macOS the `.api` calls go through AppleScript and differ. It is not usable in headless Linux CI.

## Structuring Data for Pivot-Readiness

1. One header row, with no merged cells in it.
2. Every column has a unique, non-empty name.
3. No blank rows or columns inside the data block.
4. One type per column (no text mixed with numbers).
5. Dates stored as dates, not strings.
6. No subtotal or total rows mixed into the data.

```python
df.columns = df.columns.str.strip()
df = df.dropna(how="all")
df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce")
bad = df[df["Date"].isna() | df["Amount"].isna()]
if len(bad):
    raise ValueError(f"{len(bad)} rows have unparseable Date/Amount; fix the source or report them")
```

Do not `fillna(0)` a coerced column. It turns unreadable values into real-looking zeros, and the totals silently go wrong.

## Do / Avoid

**Do:**
- Include a raw-data sheet stored as a Table.
- Reconcile the summary totals against the source before saving.
- Use `fill_value=0` only where "no rows" really means zero. Otherwise leave the cell blank.

**Avoid:**
- Merged cells in pivot source data, which break field detection.
- Assuming openpyxl or XlsxWriter can create native pivots.
- Assuming every viewer (Google Sheets, LibreOffice, mobile) preserves native pivots.
- Running xlwings in CI without a licensed Excel installation.

## Related Resources

- [excel-tables-structured-references.md](excel-tables-structured-references.md) - Tables as pivot sources
- [excel-cloud-automation.md](excel-cloud-automation.md) - Office Scripts and Graph
- [../SKILL.md](../SKILL.md) - Parent skill
