# Excel Tables and Structured References

Use Excel Tables as the default container for exported data blocks. Tables give stable ranges that expand with the data, built-in filters, totals rows, auditable structured formulas and explicit headers for assistive tech. Charts and pivots built on a table follow appended rows.

## Contents

- [Range Arithmetic](#range-arithmetic)
- [XlsxWriter](#xlsxwriter)
- [openpyxl](#openpyxl)
- [ExcelJS and Office Scripts](#exceljs-and-office-scripts)
- [Structured Formula Patterns](#structured-formula-patterns)
- [Do / Avoid](#do--avoid)

## Range Arithmetic

The table range must cover the header row, every data row and, if enabled, the totals row. With the header in 0-based row `h` and `n` data rows:

| Part | Rows (0-based) |
|------|----------------|
| Header | `h` |
| Data | `h+1` … `h+n` |
| Totals (when `total_row`) | `h+n+1` |

An off-by-one does not error. If `last_row` is one short, **the totals row overwrites the last data row**: the value is silently replaced by `SUBTOTAL(...)`, and the total then excludes it.

## XlsxWriter

```python
with pd.ExcelWriter("table_report.xlsx", engine="xlsxwriter") as writer:
    df.to_excel(writer, sheet_name="Raw Data", index=False)       # header row 0
    ws = writer.sheets["Raw Data"]
    ws.add_table(0, 0, len(df) + 1, len(df.columns) - 1, {        # +1 for the totals row
        "name": "SalesTable",
        "style": "Table Style Medium 2",
        "total_row": True,
        "columns": [{"header": c, **({"total_function": "sum"} if c == "revenue" else {})}
                    for c in df.columns],
    })
    ws.freeze_panes(1, 0)
```

- A table brings its own autofilter. Calling `worksheet.autofilter()` over the same range raises `OverlappingRange`.
- The `columns` headers override what `to_excel` wrote. Keep them identical to `df.columns`.
- XlsxWriter cannot edit an existing file. To add a table to an existing workbook, use openpyxl.

## openpyxl

```python
from openpyxl.worksheet.table import Table, TableStyleInfo

table = Table(displayName="SalesTable", ref=f"A1:C{ws.max_row}")
table.tableStyleInfo = TableStyleInfo(name="TableStyleMedium2", showRowStripes=True)
ws.add_table(table)
```

- `displayName` must be unique in the workbook, must start with a letter or underscore, and cannot contain spaces.
- Header cells must be non-empty, unique strings. For numeric or duplicate headers openpyxl only emits a `UserWarning` ("File may not be readable") and saves anyway; Excel then repairs the table. Treat that warning as an error.
- openpyxl does not add a totals row for you. Write the totals formulas yourself and include that row in `ref`.

## ExcelJS and Office Scripts

- ExcelJS `worksheet.addTable({ name, ref: "A1", headerRow: true, totalsRow: true, columns, rows })` writes the rows itself. Do not also write the same cells with `addRows`, or the data is duplicated.
- Office Scripts: `ws.addTable(ws.getUsedRange(), true)` then `table.setName(...)` and `table.setShowTotals(true)`. Use this for workbooks that already live in Microsoft 365.

## Structured Formula Patterns

| Goal | Formula |
|------|---------|
| Sum a column | `=SUM(SalesTable[revenue])` |
| Current row math (inside the table) | `=[@qty]*[@price]` |
| Visible-rows total (respects filters) | `=SUBTOTAL(109,SalesTable[revenue])` |

Use structured references in workbooks that humans will review. They are longer than A1 references, but they survive inserted rows and read as intent.

## Do / Avoid

**Do:** one header row, a descriptive and stable table name, a frozen header row, and charts and pivots built from the table rather than from guessed ranges.

**Avoid:** merged header cells, blank columns inside the table, duplicate header names, and hand-written footer formulas below the table that drift away from the data.

## Related Resources

- [excel-pivot-tables.md](excel-pivot-tables.md) - Tables as pivot sources
- [excel-formulas.md](excel-formulas.md) - Formula rules
- [../SKILL.md](../SKILL.md) - Parent skill
