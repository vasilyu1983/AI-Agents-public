# Excel Formulas Reference

Rules for writing formulas from code so they open without `#NAME?`, recalculate, and read back correctly. Function syntax itself (SUMIFS, INDEX/MATCH, date and text functions) is standard Excel and is not repeated here.

## Contents

- [Newer Functions Need `_xlfn.`](#newer-functions-need-_xlfn)
- [Spilling Functions](#spilling-functions)
- [Legacy Array Formulas](#legacy-array-formulas)
- [Reading Values Back](#reading-values-back)
- [Common Pitfalls](#common-pitfalls)
- [Performance Tips](#performance-tips)

## Newer Functions Need `_xlfn.`

Use the exact spelling listed in [XlsxWriter's future-function reference](https://xlsxwriter.readthedocs.io/working_with_formulas.html#formulas-added-in-excel-2010-and-later), including `_xlfn._xlws.` where required. Some listed functions use no `_xlfn.` prefix, so do not infer it from a function's age or absence from `openpyxl.utils.FORMULAE`. Check support in the recipient's Excel build separately.

| Writer | Behaviour | What to do |
|--------|-----------|------------|
| openpyxl | Writes formula text verbatim; its function list does not establish target-engine support | Look up the required spelling, e.g. `'=_xlfn.XLOOKUP(A2,Products!A:A,Products!C:C,"Not Found")'` |
| XlsxWriter | Prefixes dynamic-array functions (XLOOKUP, FILTER, ...) automatically, but not other newer functions (IFS, TEXTJOIN) | Create the workbook with `{'use_future_functions': True}`, or prefix by hand |
| ExcelJS | Writes formula text verbatim | Look up the required spelling as with openpyxl |

XlsxWriter skips automatic expansion when any `_xlfn.` prefix is already present in a formula. Use unprefixed input with `use_future_functions`, or spell every required prefix explicitly; do not mix the two.

When the recipient's Excel build is unknown, prefer functions every build supports: `INDEX/MATCH` over XLOOKUP, nested `IF` over IFS. LibreOffice cannot evaluate some newer functions, so a LibreOffice recalc pass may report errors that Excel would not. Treat those cells as "unverified", not as "passing".

## Spilling Functions

**Do not write spilling functions (`FILTER`, `UNIQUE`, `SORT`, `SORTBY`, `SEQUENCE`) with openpyxl.** openpyxl writes no dynamic-array (spill) metadata. Excel then treats the formula as a legacy implicit-intersection formula (often displayed with `@`) or shows `#NAME?`. LibreOffice recalculation cannot be relied on for these either. Choose one of:

- Compute the filtered, sorted or unique result in Python and write it as a plain table that the reader can trace, with the source data alongside.
- Write the spill formula with XlsxWriter, which adds the `_xlfn.`/`_xlfn._xlws.` prefixes and the spill metadata:

```python
import xlsxwriter

wb = xlsxwriter.Workbook("dyn.xlsx")
ws = wb.add_worksheet()
# ... write data in A1:C100 ...
ws.write_dynamic_array_formula("E1", "=FILTER(A1:C100,B1:B100>100,\"No results\")")
ws.write_dynamic_array_formula("G1", "=SORT(A1:C100,2,-1)")
ws.write_dynamic_array_formula("K1", "=UNIQUE(A1:A100)")
wb.close()
```

Spilling functions need a dynamic-array build of Excel. Builds without dynamic arrays show `#NAME?`. Confirm the recipient's build before relying on them.

## Legacy Array Formulas

Setting `cell.data_type = 'a'` does **not** create an array formula in openpyxl. It writes the text as a literal cell value. Use `ArrayFormula`, which emits `<f t="array">`:

```python
from openpyxl.worksheet.formula import ArrayFormula
ws["F1"] = ArrayFormula("F1", "=SUM(A1:A10*B1:B10)")
```

## Reading Values Back

- `load_workbook(data_only=True)` returns the stored cache, not a fresh calculation. openpyxl does not evaluate formulas and newly saved formula cells generally have empty caches. [XlsxWriter stores `0` by default](https://xlsxwriter.readthedocs.io/working_with_formulas.html#formula-results), requests recalculation, and accepts an explicitly supplied result. Neither an empty cache nor a placeholder zero verifies the formula.
- Recalculate headless (LibreOffice) or in Excel before reading values back. If a downstream step needs the number immediately, compute it separately in code for that step. Never replace the formula in the deliverable with a literal.
- Loading with `data_only=True` and then saving **destroys the formulas**. Keep two handles if you need both.

## Common Pitfalls

| Issue | Cause | Fix |
|-------|-------|-----|
| `#NAME?` on XLOOKUP/IFS/TEXTJOIN | Incorrect stored spelling or an unsupported recipient build | Check the future-function spelling and target support; use `use_future_functions` in XlsxWriter where appropriate |
| `#NAME?` or `@` on FILTER/UNIQUE/SORT | Written by openpyxl without spill metadata, or opened in a non-dynamic-array build | XlsxWriter `write_dynamic_array_formula`, or compute in Python |
| Formula cell reads `None` or a placeholder `0` | Missing or unevaluated cached result | Recalculate first; keep the formula and compare control totals |
| Formula shows as text | Leading apostrophe/space, or cell stored as a string | Write the string starting with `=`; check `cell.data_type == 'f'` |
| Array formula appears as literal text | `data_type = 'a'` used instead of `ArrayFormula` | Use `ArrayFormula` |
| `#REF!` after a template edit | Hard-coded ranges broke when rows or columns moved | Named ranges or structured table references |
| Circular reference | Self-referencing formula | Break the loop; do not enable iterative calculation to hide it |

## Performance Tips

1. Avoid volatile functions (`NOW`, `TODAY`, `RAND`, `OFFSET`, `INDIRECT`) in large sheets. They recalculate on every change.
2. Limit whole-column references (`A:A`) in lookups and SUMPRODUCT. Prefer table structured references.
3. Prefer helper columns to deeply nested formulas. They are faster and auditable.
4. For large openpyxl exports, install `lxml` and use `Workbook(write_only=True)` / `load_workbook(read_only=True)`. Both stream rows instead of building a full in-memory tree. A write-only workbook can be saved exactly once.

## Related Resources

- [excel-tables-structured-references.md](excel-tables-structured-references.md) - Structured references
- [../SKILL.md](../SKILL.md) - Parent skill
