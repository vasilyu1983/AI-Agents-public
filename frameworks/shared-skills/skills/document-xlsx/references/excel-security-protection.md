# Excel Security and Protection Reference

Sheet protection, cell locking, and injection prevention for generated spreadsheets.

---

## Contents

- Sheet protection (openpyxl, ExcelJS) and workbook structure protection
- Cell locking patterns and password limitations
- Formula injection prevention and hidden sheets
- Do / Avoid and pre-distribution checklist

---

## Sheet Protection

### openpyxl

```python
from openpyxl.worksheet.protection import SheetProtection

ws.protection = SheetProtection(
    sheet=True, password="review2025",
    formatCells=False, insertRows=False, deleteRows=False,
    sort=True, autoFilter=True,
    selectLockedCells=True, selectUnlockedCells=True
)
```

### ExcelJS

```typescript
await worksheet.protect('review2025', {
  selectLockedCells: true, selectUnlockedCells: true,
  formatCells: false, insertRows: false, deleteRows: false,
  sort: true, autoFilter: true
});
```

---

## Workbook Protection

Prevents adding, deleting, renaming, or reordering sheets. Does not protect cell contents.

```python
wb.security.workbookPassword = "struct2025"
wb.security.lockStructure = True
```

ExcelJS has no native workbook protection API. Use a pre-protected template.

---

## Cell Locking Patterns

All cells default to "locked" in Excel, but locking activates only when the sheet is protected.

```python
from openpyxl.styles import Protection

# Unlock input cells
for row in ws.iter_rows(min_row=2, max_row=200, min_col=2, max_col=4):
    for cell in row:
        cell.protection = Protection(locked=False)

# Lock and hide formula cells (hidden=True hides from formula bar)
for row in ws.iter_rows(min_row=2, max_row=200, min_col=5, max_col=8):
    for cell in row:
        cell.protection = Protection(locked=True, hidden=True)

ws.protection.sheet = True
ws.protection.password = "edit2025"
```

```typescript
// ExcelJS equivalent
for (let r = 2; r <= 200; r++) {
  for (let c = 2; c <= 4; c++)
    worksheet.getCell(r, c).protection = { locked: false };
  for (let c = 5; c <= 8; c++)
    worksheet.getCell(r, c).protection = { locked: true, hidden: true };
}
await worksheet.protect('edit2025');
```

---

## Password Limitations

Sheet/workbook protection passwords are **not encryption**. They are a UI deterrent only.

| Fact | Detail |
|------|--------|
| Hash algorithm | Legacy CRC / SHA-based hash in XML |
| Crack time | Seconds with freely available tools |
| Bypass | Unzip .xlsx, edit XML, remove password hash |
| Real encryption | AES-128/256 via `msoffcrypto-tool` or OS-level controls |

```python
import msoffcrypto
with open("report.xlsx", "rb") as f:
    file = msoffcrypto.OfficeFile(f)
    file.load_key(password="Str0ngP@ss!")
    with open("report_encrypted.xlsx", "wb") as out:
        file.encrypt("Str0ngP@ss!", out)
```

---

## Formula Injection Prevention

User-supplied strings can trigger formula execution when written to cells.

### Dangerous Prefixes

`=`, `+`, `-`, `@`, `\t` (tab), `\r` (carriage return)

### Sanitization

```python
DANGEROUS_PREFIXES = ("=", "+", "-", "@", "\t", "\r", "\n")

def sanitize_cell_value(value):
    if isinstance(value, str) and value.startswith(DANGEROUS_PREFIXES):
        return "'" + value   # leading quote forces text interpretation
    return value
```

```typescript
const DANGEROUS = /^[=+\-@\t\r\n]/;
function sanitize(v: unknown): unknown {
  return typeof v === 'string' && DANGEROUS.test(v) ? "'" + v : v;
}
```

The leading single quote is not displayed in the cell.

---

## Hidden Sheets for Audit Trails

```python
ws_meta = wb.create_sheet("_Audit")
ws_meta.sheet_state = "veryHidden"  # only accessible via VBA editor
ws_meta["A1"], ws_meta["B1"] = "Generated", datetime.now().isoformat()
ws_meta["A2"], ws_meta["B2"] = "Source Hash", data_hash
```

`hidden` = users can unhide via right-click. `veryHidden` = requires VBA or XML editing.

## Do / Avoid

**Do:** sanitize all user-supplied strings before cell writes. Use file-level AES encryption for sensitive data. Unlock only specific input ranges. Hide formulas in protected sheets. Document editable cells on an Instructions sheet.

**Avoid:** relying on sheet protection passwords as a security boundary. Writing raw user input without injection checks. Protecting sheets without setting locked/unlocked patterns first. Storing secrets or PII in cells, even on hidden sheets.

---

## Checklist: Pre-Distribution Security Review

- [ ] User-supplied values pass through injection sanitization
- [ ] Input cells unlocked; all others locked; sheet protection enabled
- [ ] Formula cells have `hidden=True` if logic is confidential
- [ ] Workbook structure protection is on
- [ ] File-level encryption applied if data is sensitive or regulated
- [ ] Hidden sheets contain no credentials or tokens
- [ ] Tested in Excel, LibreOffice, and Google Sheets
