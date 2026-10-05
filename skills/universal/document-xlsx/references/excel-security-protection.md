# Excel Security and Protection Reference

Sheet protection, cell locking, file encryption, external-link handling and injection prevention for generated spreadsheets. The core rule: **protection is a guard against accidents; only encryption protects confidentiality.**

## Contents

- [Protection Is Not Security](#protection-is-not-security)
- [Cell Locking Patterns](#cell-locking-patterns)
- [File Encryption](#file-encryption)
- [Formula Injection Prevention](#formula-injection-prevention)
- [Hyperlinks And External Links](#hyperlinks-and-external-links)
- [Hidden And Very Hidden Sheets](#hidden-and-very-hidden-sheets)
- [Checklist: Pre-Distribution Security Review](#checklist-pre-distribution-security-review)

## Protection Is Not Security

| Mechanism | What it does | What it does not do |
|-----------|--------------|---------------------|
| Sheet protection | Blocks edits to locked cells in the Excel UI | Hide or encrypt data. The password hash sits in the XML, and anyone can unzip the file and delete the element |
| Workbook structure protection (`wb.security.lockStructure`) | Blocks adding, deleting, renaming or unhiding sheets | Protect cell contents |
| `hidden=True` on a cell | Hides the formula from the formula bar on a protected sheet | Hide the formula from anyone who reads the XML |
| File encryption | Encrypts the whole package; nothing opens without the password | Allow selective editing |

Never put a real password in source code. Read it from the environment or a secret store, and never reuse a sheet-protection password for anything that matters.

## Cell Locking Patterns

Every cell is locked by default, but locking only takes effect once the sheet is protected. Unlock the input ranges first, then protect:

```python
import os
from openpyxl.styles import Protection
from openpyxl.worksheet.protection import SheetProtection

for row in ws.iter_rows(min_row=2, max_row=200, min_col=2, max_col=4):
    for cell in row:
        cell.protection = Protection(locked=False)          # inputs
for row in ws.iter_rows(min_row=2, max_row=200, min_col=5, max_col=8):
    for cell in row:
        cell.protection = Protection(locked=True, hidden=True)  # formulas

ws.protection = SheetProtection(sheet=True, password=os.environ["SHEET_PW"],
                                sort=True, autoFilter=True,
                                selectLockedCells=True, selectUnlockedCells=True)
```

- Protecting before unlocking the inputs produces a sheet that nobody can use.
- Sort and filter only work on a protected sheet when those options are allowed, and even then sorting can fail when the range contains locked cells. Test in Excel.
- ExcelJS: `worksheet.protect(password, options)`. It has no workbook-structure protection, so start from a pre-protected template.

## File Encryption

Use file-level encryption for confidential or regulated data:

```python
import msoffcrypto, os

with open("report.xlsx", "rb") as f, open("report_encrypted.xlsx", "wb") as out:
    msoffcrypto.OfficeFile(f).encrypt(os.environ["FILE_PW"], out)
```

- An encrypted file is no longer a zip. openpyxl, pandas and the audit script cannot read it until it is decrypted (`OfficeFile.load_key(...)` then `.decrypt(...)`).
- Send the password through a different channel from the file.
- Where the platform offers it (sensitivity labels, access-controlled shares), platform access control is usually better than a shared password.

## Formula Injection Prevention

The risk is **CSV/export injection**. A string that starts with `=`, `+`, `-`, `@`, a tab, CR or LF becomes a live formula when the data is exported to CSV, or pasted, and then opened in a spreadsheet. An XLSX string cell does not execute because of its prefix, since its type is string, so the boundary to guard is the export and the paste, not the workbook itself.

```python
DANGEROUS_PREFIXES = ("=", "+", "-", "@", "\t", "\r", "\n")

def sanitize_for_csv(value):
    if isinstance(value, str) and value.startswith(DANGEROUS_PREFIXES):
        return "'" + value
    return value
```

- In a CSV, the leading apostrophe is the accepted neutraliser.
- Inside an XLSX, a literal apostrophe becomes a **visible character** in Excel, LibreOffice and Google Sheets. Excel's own convention is the `quotePrefix` cell-style attribute, which hides the quote. `scripts/xlsx_sanitize.py` writes the literal apostrophe (a documented limitation in the script). Use it for files headed to CSV or to untrusted re-export, and tell the recipient the quote is visible.
- Blindly prefixing `-` corrupts negative numbers stored as text. Convert numeric strings to numbers first.

## Hyperlinks And External Links

- Reject or rewrite untrusted protocols (`javascript:`, `file:`, `data:`). Label links readably instead of showing raw tracking URLs.
- Load untrusted workbooks with `load_workbook(path, keep_vba=False, keep_links=False)`.
- External workbook links live in `xl/externalLinks/` plus their relationships and content types. `xlsx_sanitize.py --strip-external-links` removes all three. Formulas that referenced them then return errors or stale cached values, so re-check them afterwards.
- Document any intentional external link on an Instructions sheet.

## Hidden And Very Hidden Sheets

- `hidden`: users unhide it from the sheet-tab menu. `veryHidden`: only VBA or XML editing reveals it. Both ship in the file, in plain XML.
- A very hidden sheet suits generator metadata (timestamp, source hash). It is never a place for secrets, PII or anything the recipient must not see. Remove such data instead.
- `scripts/xlsx_audit.py` reports hidden and very hidden sheets. Review them before sending.

## Checklist: Pre-Distribution Security Review

- [ ] Exported and user-supplied strings pass through injection sanitisation at the CSV or paste boundary
- [ ] Hyperlinks reviewed; unsafe protocols removed or rewritten
- [ ] Input cells unlocked, everything else locked, sheet protection on, and tested in Excel
- [ ] External links removed, documented or approved; formulas re-checked afterwards
- [ ] File-level encryption, or platform access control, for sensitive or regulated data
- [ ] Hidden and very hidden sheets contain no credentials, tokens or PII
- [ ] `scripts/xlsx_audit.py` exits 0 (no blocking findings)

## Related Resources

- [excel-data-validation.md](excel-data-validation.md) - Validation plus protection
- [../SKILL.md](../SKILL.md) - Parent skill
