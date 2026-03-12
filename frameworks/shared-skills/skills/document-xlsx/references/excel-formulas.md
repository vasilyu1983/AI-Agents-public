# Excel Formulas Reference

Comprehensive formula patterns for spreadsheet generation with openpyxl and ExcelJS.

---

## Basic Formulas

| Category | Formula | Example | Description |
|----------|---------|---------|-------------|
| Sum | `=SUM(range)` | `=SUM(A1:A100)` | Total of range |
| Average | `=AVERAGE(range)` | `=AVERAGE(B2:B50)` | Mean value |
| Count | `=COUNT(range)` | `=COUNT(C:C)` | Count numbers |
| CountA | `=COUNTA(range)` | `=COUNTA(D:D)` | Count non-empty |
| Min/Max | `=MIN(range)` / `=MAX(range)` | `=MAX(E1:E100)` | Extremes |

---

## Conditional Formulas

### SUMIF / SUMIFS

```python
# openpyxl - Single condition
ws['F1'] = '=SUMIF(A:A,"Product A",B:B)'

# Multiple conditions
ws['F2'] = '=SUMIFS(C:C,A:A,"Region1",B:B,">100")'
```

```typescript
// ExcelJS
sheet.getCell('F1').value = { formula: 'SUMIF(A:A,"Product A",B:B)' };
```

### COUNTIF / COUNTIFS

| Pattern | Formula | Use Case |
|---------|---------|----------|
| Single condition | `=COUNTIF(A:A,"Completed")` | Count status |
| Date range | `=COUNTIFS(A:A,">=2024-01-01",A:A,"<=2024-12-31")` | Count by period |
| Multiple criteria | `=COUNTIFS(A:A,"Active",B:B,">1000")` | Filtered count |

### AVERAGEIF

```python
# Average sales for specific product
ws['G1'] = '=AVERAGEIF(A:A,"Widget",C:C)'
```

---

## Lookup Formulas

### VLOOKUP

```python
# Syntax: VLOOKUP(lookup_value, table_array, col_index, [range_lookup])
ws['D2'] = '=VLOOKUP(A2,Products!A:C,3,FALSE)'
```

**Parameters:**
- `lookup_value`: Value to find
- `table_array`: Range containing data
- `col_index`: Column number to return (1-based)
- `range_lookup`: FALSE for exact match

### XLOOKUP (Excel 365+)

```python
# More flexible than VLOOKUP
ws['D2'] = '=XLOOKUP(A2,Products!A:A,Products!C:C,"Not Found")'
```

### INDEX/MATCH (Most Flexible)

```python
# Syntax: INDEX(return_range, MATCH(lookup_value, lookup_range, 0))
ws['D2'] = '=INDEX(C:C,MATCH(A2,A:A,0))'
```

**Advantages over VLOOKUP:**
- Can look left (not just right)
- More performant on large datasets
- Column insertions don't break formula

---

## Date Formulas

| Formula | Example | Result |
|---------|---------|--------|
| `=TODAY()` | `=TODAY()` | Current date |
| `=NOW()` | `=NOW()` | Current date+time |
| `=YEAR(date)` | `=YEAR(A1)` | Extract year |
| `=MONTH(date)` | `=MONTH(A1)` | Extract month (1-12) |
| `=EOMONTH(date,months)` | `=EOMONTH(A1,0)` | End of month |
| `=NETWORKDAYS(start,end)` | `=NETWORKDAYS(A1,B1)` | Business days |
| `=DATEDIF(start,end,"Y")` | `=DATEDIF(A1,B1,"Y")` | Years between |

### Date Calculations

```python
# Days until deadline
ws['C2'] = '=B2-TODAY()'

# Age calculation
ws['D2'] = '=DATEDIF(A2,TODAY(),"Y")'

# Next month same day
ws['E2'] = '=EDATE(A2,1)'
```

---

## Text Formulas

| Formula | Example | Result |
|---------|---------|--------|
| `=CONCATENATE()` | `=A1&" "&B1` | Join text |
| `=LEFT(text,n)` | `=LEFT(A1,3)` | First n chars |
| `=RIGHT(text,n)` | `=RIGHT(A1,4)` | Last n chars |
| `=MID(text,start,n)` | `=MID(A1,2,5)` | Substring |
| `=TRIM(text)` | `=TRIM(A1)` | Remove spaces |
| `=UPPER/LOWER` | `=UPPER(A1)` | Case change |
| `=LEN(text)` | `=LEN(A1)` | Character count |

### Text Extraction

```python
# Extract domain from email
ws['B2'] = '=MID(A2,FIND("@",A2)+1,100)'

# First name from full name
ws['C2'] = '=LEFT(A2,FIND(" ",A2)-1)'
```

---

## Logical Formulas

### IF Statements

```python
# Simple IF
ws['C2'] = '=IF(B2>100,"High","Low")'

# Nested IF
ws['C2'] = '=IF(B2>100,"High",IF(B2>50,"Medium","Low"))'

# IFS (Excel 365+)
ws['C2'] = '=IFS(B2>100,"High",B2>50,"Medium",TRUE,"Low")'
```

### AND / OR

```python
# Multiple conditions
ws['D2'] = '=IF(AND(B2>100,C2="Active"),"Priority","Normal")'
ws['E2'] = '=IF(OR(B2>1000,C2="VIP"),"Premium","Standard")'
```

### IFERROR

```python
# Handle division by zero, lookup failures
ws['F2'] = '=IFERROR(A2/B2,0)'
ws['G2'] = '=IFERROR(VLOOKUP(A2,Data!A:B,2,FALSE),"Not Found")'
```

---

## Financial Formulas

| Formula | Purpose | Example |
|---------|---------|---------|
| `=PMT(rate,nper,pv)` | Loan payment | `=PMT(0.05/12,360,-250000)` |
| `=FV(rate,nper,pmt,pv)` | Future value | `=FV(0.07,10,-1000,0)` |
| `=PV(rate,nper,pmt)` | Present value | `=PV(0.05,5,-1000)` |
| `=NPV(rate,values)` | Net present value | `=NPV(0.1,B2:B10)` |
| `=IRR(values)` | Internal return | `=IRR(A1:A10)` |

---

## Array Formulas (Dynamic Arrays)

### FILTER

```python
# Filter rows where column B > 100
ws['E1'] = '=FILTER(A:C,B:B>100,"No results")'
```

### UNIQUE

```python
# Get unique values
ws['F1'] = '=UNIQUE(A:A)'
```

### SORT

```python
# Sort by column, descending
ws['G1'] = '=SORT(A1:C100,2,-1)'
```

### SEQUENCE

```python
# Generate number sequence
ws['A1'] = '=SEQUENCE(10,1,1,1)'  # 1 to 10
```

---

## Implementation Patterns

### openpyxl (Python)

```python
from openpyxl import Workbook

wb = Workbook()
ws = wb.active

# Add formula
ws['C2'] = '=A2*B2'

# Named ranges in formulas
wb.defined_names.add('SalesData', 'Sheet1!$A$1:$C$100')
ws['D1'] = '=SUM(SalesData)'

# Array formula (legacy)
ws['E1'] = '=SUM(A1:A10*B1:B10)'
ws['E1'].data_type = 'a'  # Mark as array formula
```

### ExcelJS (Node.js)

```typescript
import ExcelJS from 'exceljs';

const workbook = new ExcelJS.Workbook();
const sheet = workbook.addWorksheet('Data');

// Simple formula
sheet.getCell('C2').value = { formula: 'A2*B2' };

// Formula with result hint
sheet.getCell('D2').value = {
  formula: 'SUM(A:A)',
  result: 1000  // Optional: cached result
};

// Shared formula (efficient for repeated formulas)
sheet.getCell('C2').value = { sharedFormula: 'A2*B2' };
for (let row = 3; row <= 100; row++) {
  sheet.getCell(`C${row}`).value = { sharedFormula: 'C2' };
}
```

---

## Common Pitfalls

| Issue | Cause | Solution |
|-------|-------|----------|
| `#REF!` | Deleted reference | Use named ranges |
| `#VALUE!` | Type mismatch | Check data types |
| `#DIV/0!` | Division by zero | Wrap in IFERROR |
| `#N/A` | Lookup not found | IFERROR or IFNA |
| Circular reference | Self-referencing | Break the loop |
| Formula as text | Leading quote/space | Remove prefix |

---

## Performance Tips

1. **Avoid volatile functions** in large sheets: `NOW()`, `TODAY()`, `RAND()`, `INDIRECT()`
2. **Use structured references** with Tables instead of A1 notation
3. **Prefer XLOOKUP/INDEX-MATCH** over VLOOKUP for large datasets
4. **Limit whole-column references** (`A:A`) when possible
5. **Use helper columns** instead of complex nested formulas
