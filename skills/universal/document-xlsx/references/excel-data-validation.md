# Excel Data Validation Reference

Patterns for enforcing input constraints in generated spreadsheets, and the defaults that silently leave them unenforced.

## Contents

- [Enforcement Is Off By Default](#enforcement-is-off-by-default)
- [openpyxl Examples](#openpyxl-examples)
- [Named Ranges for Validation Lists](#named-ranges-for-validation-lists)
- [Cascading Dropdowns](#cascading-dropdowns)
- [Combining Validation with Sheet Protection](#combining-validation-with-sheet-protection)
- [Verify](#verify)
- [Common Pitfalls](#common-pitfalls)

## Enforcement Is Off By Default

openpyxl's `DataValidation` defaults to `showErrorMessage=False` and `showInputMessage=False`. With the error alert off, Excel **accepts any typed value**. The dropdown appears, but the rule is not enforced. Setting `dv.error = "..."` does not switch the alert on. Always pass both flags:

```python
DataValidation(..., showErrorMessage=True, showInputMessage=True)
```

`errorStyle` then selects the behaviour: `stop` rejects the entry, `warning` allows an override, `information` only informs. Use `stop` for keys and codes that downstream code depends on.

## openpyxl Examples

```python
from openpyxl.worksheet.datavalidation import DataValidation

strict = dict(showErrorMessage=True, showInputMessage=True, errorStyle="stop")

dv = DataValidation(type="list", formula1='"Open,In Progress,Closed"', allow_blank=True, **strict)
dv.error, dv.prompt = "Pick a valid status.", "Select a status from the list."
ws.add_data_validation(dv); dv.add("B2:B500")

dv_num = DataValidation(type="whole", operator="between", formula1="1", formula2="100", **strict)
dv_num.error = "Enter a whole number between 1 and 100."
ws.add_data_validation(dv_num); dv_num.add("C2:C500")

# Custom rule: no leading "=" (openpyxl writes formula1 verbatim)
dv_uniq = DataValidation(type="custom", formula1="COUNTIF($D$2:$D$500,D2)<=1", **strict)
dv_uniq.error = "Duplicate value."
ws.add_data_validation(dv_uniq); dv_uniq.add("D2:D500")
```

- Inline lists need the inner double quotes: `formula1='"A,B,C"'`.
- Custom formulas are relative to the top-left cell of the range, as with conditional formatting.
- ExcelJS sets `dataValidation` per cell, so loop over the range, and set `showErrorMessage: true` there too.

## Named Ranges for Validation Lists

The file format caps an inline list at 255 characters, and inline lists are hard to maintain. Put longer lists on a lists sheet and reference them by name:

```python
from openpyxl.workbook.defined_name import DefinedName

lists = wb.create_sheet("Lists")
for i, val in enumerate(["Open", "In Progress", "Closed", "Blocked"], start=1):
    lists.cell(row=i, column=1, value=val)
lists.sheet_state = "hidden"
wb.defined_names.add(DefinedName("StatusList", attr_text="Lists!$A$1:$A$4"))

dv = DataValidation(type="list", formula1="StatusList", showErrorMessage=True)
ws.add_data_validation(dv); dv.add("B2:B500")
```

Blank cells inside the source range appear as blank dropdown entries. Size the range exactly, or point it at a Table column.

## Cascading Dropdowns

Dependent validation (Country to City) uses `INDIRECT` with one named range per parent value:

```python
dv_city = DataValidation(type="list", formula1="INDIRECT(A2)", showErrorMessage=True)
```

`INDIRECT` is volatile, and the named ranges must match the parent values exactly (no spaces). Support outside Excel is inconsistent, so if the file will be used in LibreOffice or Google Sheets, use a flat list plus a custom check instead.

## Combining Validation with Sheet Protection

Validation does not stop paste-over: pasting a value replaces the cell's rule along with its value. Protect the sheet and unlock only the input cells:

```python
from openpyxl.styles import Protection

for row in ws.iter_rows(min_row=2, max_row=500, min_col=2, max_col=2):
    for cell in row:
        cell.protection = Protection(locked=False)
ws.protection.sheet = True
```

Sheet protection is a guard against accidents, not a security control. See [excel-security-protection.md](excel-security-protection.md).

## Verify

After saving, reload the file and assert the rules are live:

```python
from openpyxl import load_workbook
dvs = load_workbook(path).active.data_validations.dataValidation
assert dvs and all(d.showErrorMessage for d in dvs), "validation present but not enforced"
```

Then type an invalid value in Excel once. Only a real application proves the rule rejects it.

## Common Pitfalls

| Pitfall | Detail |
|---------|--------|
| Rule not enforced | `showErrorMessage` left at openpyxl's default of `False` |
| Leading `=` in `formula1` | Written verbatim; Excel may flag the file for repair |
| Copy-paste bypasses validation | Pasting replaces the cell's rule; use protection |
| Whole-column ranges (`A:A`) | Slow and bloats the file; use bounded ranges |
| One rule per cell | Excel caps the rule count per sheet; add one rule over a range instead |
| Validation invisible to pandas | `read_excel` ignores it; re-validate the data in code before trusting it |

## Related Resources

- [excel-security-protection.md](excel-security-protection.md) - Protection limits
- [excel-tables-structured-references.md](excel-tables-structured-references.md) - Table columns as list sources
- [../SKILL.md](../SKILL.md) - Parent skill
