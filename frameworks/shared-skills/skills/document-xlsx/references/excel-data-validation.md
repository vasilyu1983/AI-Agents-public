# Excel Data Validation Reference

Patterns for enforcing input constraints in generated spreadsheets.

---

## Contents

- Validation types overview
- openpyxl and ExcelJS code examples
- Named ranges for maintainable lists
- Cascading (dependent) dropdowns
- Error/input messages and protection
- Do / Avoid and common pitfalls

---

## Validation Types

| Type | Use Case | openpyxl `type` value |
|------|----------|-----------------------|
| List (dropdown) | Constrain to predefined options | `list` |
| Whole number | Integer within range | `whole` |
| Decimal | Float within range | `decimal` |
| Date | Date within range | `date` |
| Text length | Min/max character count | `textLength` |
| Custom formula | Any boolean expression | `custom` |

---

## openpyxl Examples

```python
from openpyxl.worksheet.datavalidation import DataValidation

# Dropdown list
dv = DataValidation(type="list", formula1='"Open,In Progress,Closed"', allow_blank=True)
dv.error = "Pick a valid status."
dv.prompt = "Select a status from the list."
ws.add_data_validation(dv)
dv.add("B2:B500")

# Whole number range
dv_num = DataValidation(type="whole", operator="between", formula1=1, formula2=100)
dv_num.error = "Enter a number between 1 and 100."
ws.add_data_validation(dv_num)
dv_num.add("C2:C500")

# Custom formula (unique values only)
dv_uniq = DataValidation(type="custom", formula1="=COUNTIF($D:$D,D2)<=1")
dv_uniq.error = "Duplicate value."
ws.add_data_validation(dv_uniq)
dv_uniq.add("D2:D500")
```

## ExcelJS Example

```typescript
worksheet.getCell('B2').dataValidation = {
  type: 'list',
  allowBlank: true,
  formulae: ['"Open,In Progress,Closed"'],
  showErrorMessage: true,
  error: 'Pick a valid status.',
  showInputMessage: true,
  prompt: 'Select a status from the list.'
};
```

ExcelJS requires setting `dataValidation` per-cell or looping over a range; there is no range-based add method.

---

## Named Ranges for Validation Lists

Hardcoded comma-separated strings break when lists exceed ~255 characters. Use named ranges instead.

```python
from openpyxl.workbook.defined_name import DefinedName

ws_lists = wb.create_sheet("Lists")
statuses = ["Open", "In Progress", "Closed", "Blocked"]
for i, val in enumerate(statuses, start=1):
    ws_lists.cell(row=i, column=1, value=val)
ws_lists.sheet_state = "hidden"

ref = f"Lists!$A$1:$A${len(statuses)}"
defn = DefinedName("StatusList", attr_text=ref)
wb.defined_names.add(defn)

dv = DataValidation(type="list", formula1="StatusList")
ws.add_data_validation(dv)
dv.add("B2:B500")
```

---

## Cascading Dropdowns

Dependent validation (Country -> City) uses INDIRECT with named ranges per parent value.

```python
# Named ranges: "USA" -> Lists!$B$1:$B$3, "UK" -> Lists!$C$1:$C$2

dv_country = DataValidation(type="list", formula1='"USA,UK"')
ws.add_data_validation(dv_country)
dv_country.add("A2:A100")

dv_city = DataValidation(type="list", formula1="=INDIRECT(A2)")
ws.add_data_validation(dv_city)
dv_city.add("B2:B100")
```

Limitation: INDIRECT is volatile and only resolves in Excel. LibreOffice and Google Sheets have inconsistent support.

---

## Error Messages and Input Messages

| Property | Purpose |
|----------|---------|
| `prompt` / `promptTitle` | Tooltip when cell is selected |
| `error` / `errorTitle` | Dialog shown on invalid entry |
| `errorStyle` | `stop` (reject), `warning` (allow override), `information` (info only) |

Set `errorStyle` to `warning` when soft guidance is acceptable.

## Combining Validation with Sheet Protection

Validation alone does not prevent paste-over. Combine with protection:

```python
from openpyxl.styles import Protection

for row in ws.iter_rows(min_row=2, max_row=500, min_col=2, max_col=2):
    for cell in row:
        cell.protection = Protection(locked=False)  # unlock input cells

ws.protection.sheet = True
ws.protection.password = "edit123"
```

---

## Do / Avoid

**Do:**
- Use named ranges on a hidden sheet for lists longer than 5 items
- Set both `prompt` and `error` messages for every validation rule
- Combine validation with sheet protection on template workbooks
- Test generated files in Excel, LibreOffice, and Google Sheets

**Avoid:**
- Comma-separated strings over ~200 characters (Excel truncates at 255)
- More than 65,534 validation objects per sheet (Excel hard limit)
- INDIRECT-based cascading dropdowns if the file will be consumed outside Excel
- Validating entire columns (`A:A`) -- use bounded ranges (`A2:A5000`)

---

## Common Pitfalls

| Pitfall | Detail |
|---------|--------|
| Hidden rows break list source | Filtered/hidden source rows cause blank dropdown entries |
| Copy-paste bypasses validation | Users can paste invalid data; sheet protection mitigates |
| Formula1 quoting | openpyxl lists need inner double quotes: `formula1='"A,B,C"'` |
| Validation invisible to pandas | `read_excel` ignores validation; it is UI metadata only |
| Max 255 chars in formula1 | Use a named range referencing cells instead of inline strings |
