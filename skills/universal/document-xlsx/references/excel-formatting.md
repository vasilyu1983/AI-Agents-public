# Excel Formatting Reference

Decision rules and failure modes for number formats, conditional formatting and layout. The basic openpyxl/ExcelJS styling API (fonts, fills, borders, alignment) is covered by the library docs and the official `xlsx` skill.

## Contents

- [Types Before Formats](#types-before-formats)
- [Number Formats](#number-formats)
- [Conditional Formatting](#conditional-formatting)
- [Layout](#layout)
- [Styles At Scale](#styles-at-scale)
- [Print Setup](#print-setup)

## Types Before Formats

A number format only applies to a cell of the right type. A string that looks like a date or a number stays text: it sorts wrong, sums to zero and ignores the format.

- Write dates as `datetime.date`/`datetime` objects. openpyxl stores them as type `d` and applies `yyyy-mm-dd` by default. A date passed as an ISO string is stored as type `s` (text).
- Write numbers as `int`/`float`/`Decimal`, never as pre-formatted strings such as `"1,234.50"` or `"12%"`.
- Keep full precision in the cell and round with the format. Round the value itself only where the business rule says so (for example invoice lines).

## Number Formats

- Format codes are stored in the file in the invariant (en-US) form: `.` for decimals, `,` for thousands. Excel localises the display. Do not write locale-specific separators into the code.
- `[Green]#,##0.00;[Red]-#,##0.00` uses sections: positive;negative;zero;text.
- Currency symbols in the code are literals. For a multi-currency sheet, put the currency code in its own column rather than baking one symbol into a shared format.
- Percentages: store `0.125` and format `0.0%`. Storing `12.5` with a `%` format shows `1250.0%`.

## Conditional Formatting

- **Formula rules** are written relative to the top-left cell of the applied range. Range `A2:E100` with formula `$C2="Overdue"` highlights whole rows: the `$` pins the column, while the row floats.
- Write the formula **without a leading `=`**. openpyxl writes the text verbatim into `<formula>`, and Excel may then flag the file for repair.
- Functions that need `_xlfn.` in cells need it inside rule formulas too (see [excel-formulas.md](excel-formulas.md#newer-functions-need-_xlfn)).
- Avoid whole-column references such as `COUNTIF($A:$A,A2)` on large ranges. Every visible cell re-evaluates them. Bound the range.
- Rules evaluate in priority order. Set `stopIfTrue` when a later rule must not override an earlier one. Keep rules few: overlapping rules from repeated generation runs are a common source of slow, confusing files.
- Colour must not be the only signal. Pair a colour scale or fill with a status column or an icon set (see [excel-accessibility-compliance.md](excel-accessibility-compliance.md)).
- Rule classes: `CellIsRule` (thresholds), `FormulaRule` (row logic), `ColorScaleRule`, `DataBarRule`, `IconSetRule`, all in `openpyxl.formatting.rule`.

## Layout

- **Column width:** openpyxl cannot auto-fit. The width is in character units. Estimate it from the longest rendered value plus padding, and cap it (about 50) so one long note does not produce a huge column.
- **Freeze panes:** `ws.freeze_panes = "B2"` freezes everything above and to the left of B2. Freeze the header row on any table longer than one screen.
- **Merged cells:** they break sorting, filtering, copy-paste and screen-reader navigation. For a title across columns use `Alignment(horizontal="centerContinuous")` (Center Across Selection). Never merge inside a data table.
- **Hidden rows and columns:** a reader will not find them, and hidden data still ships in the file. Do not hide confidential data (see [excel-security-protection.md](excel-security-protection.md)).

## Styles At Scale

- Register a `NamedStyle` once per workbook. A second `wb.add_named_style()` with the same name raises `ValueError`. Guard with `if name not in wb.named_styles`.
- On large sheets, a named style or a column-level pattern is cheaper than building new `Font`/`PatternFill` objects per cell.
- Prefer table styles (`TableStyleInfo(showRowStripes=True)`) to hand-painted zebra fills. They survive sorting and row inserts.
- When editing a client template, reuse its existing styles and theme colours. Do not introduce a parallel palette.

## Print Setup

```python
ws.page_setup.orientation = "landscape"
ws.page_setup.fitToWidth, ws.page_setup.fitToHeight = 1, 0   # 1 page wide, any height
ws.page_setup.fitToPage = True                               # writes <pageSetUpPr fitToPage="1"/>
ws.print_title_rows = "1:1"                                  # repeat header row
ws.oddFooter.center.text = "Page &P of &N"
```

`fitToWidth`/`fitToHeight` are ignored unless `fitToPage` is set. Without it Excel prints at the `scale` value.

## Related Resources

- [excel-charts.md](excel-charts.md) - Chart rules
- [excel-tables-structured-references.md](excel-tables-structured-references.md) - Table styles
- [../SKILL.md](../SKILL.md) - Parent skill
