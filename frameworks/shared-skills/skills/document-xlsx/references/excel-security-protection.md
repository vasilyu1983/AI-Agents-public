# Excel Security and Protection Reference

## Table of Contents

- [Contents](#contents)
- [Sheet Protection](#sheet-protection)
- [Workbook Protection](#workbook-protection)
- [Cell Locking Patterns](#cell-locking-patterns)
- [Password Limitations](#password-limitations)
- [Formula Injection Prevention](#formula-injection-prevention)
- [Hyperlinks And External Links](#hyperlinks-and-external-links)
- [Hidden Sheets for Audit Trails](#hidden-sheets-for-audit-trails)
- [Do / Avoid](#do--avoid)
- [Checklist: Pre-Distribution Security Review](#checklist-pre-distribution-security-review)

Sheet protection, cell locking, external-link handling, and injection prevention for generated spreadsheets.

---

## Contents

- Sheet protection (openpyxl, ExcelJS) and workbook structure protection
- Cell locking patterns and password limitations
- Formula injection, hyperlinks, external links, and hidden sheets
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

## Hyperlinks And External Links

Hyperlinks and workbook external links need separate review.

### Hyperlink Review

- Reject or rewrite untrusted protocols such as `javascript:`
- Prefer readable hyperlink labels over raw tracking URLs
- Audit links before distribution when the workbook will leave the authoring team

### openpyxl Workbook Loading

When ingesting an untrusted workbook, do not preserve external links by default unless the workflow explicitly requires them.

```python
from openpyxl import load_workbook

wb = load_workbook("input.xlsx", keep_vba=False, keep_links=False)
```

### Strip External Links During Packaging

- Remove `xl/externalLinks/` parts and their relationships if the workbook should be self-contained
- Document intentional external links on an Instructions or Summary sheet
- Re-test formulas after link removal because some models expect external workbooks

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

**Do:** sanitize all user-supplied strings before cell writes. Review hyperlinks and external links before distribution. Use file-level AES encryption for sensitive data. Unlock only specific input ranges. Hide formulas in protected sheets. Document editable cells and intentional links on an Instructions sheet.

**Avoid:** relying on sheet protection passwords as a security boundary. Writing raw user input without injection checks. Preserving external links on untrusted ingest without a reason. Protecting sheets without setting locked/unlocked patterns first. Storing secrets or PII in cells, even on hidden sheets.

---

## Checklist: Pre-Distribution Security Review

- [ ] User-supplied values pass through injection sanitization
- [ ] Hyperlinks have been reviewed and unsafe protocols removed or rewritten
- [ ] Input cells unlocked; all others locked; sheet protection enabled
- [ ] Formula cells have `hidden=True` if logic is confidential
- [ ] Workbook structure protection is on
- [ ] External links are removed, documented, or explicitly approved
- [ ] File-level encryption applied if data is sensitive or regulated
- [ ] Hidden sheets contain no credentials or tokens
- [ ] Tested in Excel, LibreOffice, and Google Sheets
