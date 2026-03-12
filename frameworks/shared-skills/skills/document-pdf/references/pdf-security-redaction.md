# PDF Security, Encryption, and Redaction

Patterns for protecting PDF content, controlling permissions, and performing verified redaction.

---

## Contents

- [Encryption Types](#encryption-types)
- [Password Protection](#password-protection)
- [Setting Permissions](#setting-permissions)
- [Real vs Fake Redaction](#real-vs-fake-redaction)
- [Redaction Workflow](#redaction-workflow)
- [Metadata Scrubbing](#metadata-scrubbing)
- [Do / Avoid](#do--avoid)
- [Checklist: Pre-Distribution Security Review](#checklist-pre-distribution-security-review)

---

## Encryption Types

| Algorithm | Key | Status |
|-----------|-----|--------|
| RC4 40-bit | Broken | Crackable in seconds. Never use. |
| RC4 128-bit | Weak | Not recommended for new documents. |
| AES 128-bit | Acceptable | PDF 1.6+. |
| AES 256-bit | Recommended | PDF 2.0. Use for all new work. |

PDF uses two passwords: **user** (to open) and **owner** (to change permissions). Permission flags are viewer-enforced, not cryptographic. Encryption prevents content access; permissions are advisory.

---

## Password Protection

### pypdf

```python
from pypdf import PdfReader, PdfWriter

reader = PdfReader('report.pdf')
writer = PdfWriter()
for page in reader.pages:
    writer.add_page(page)
writer.encrypt(user_password='viewpass', owner_password='adminpass', algorithm='AES-256')
with open('encrypted.pdf', 'wb') as f:
    writer.write(f)
```

### pdf-lib

```typescript
const pdfDoc = await PDFDocument.load(fs.readFileSync('report.pdf'));
const bytes = await pdfDoc.save({
  userPassword: 'viewpass', ownerPassword: 'adminpass',
  permissions: { printing: 'highResolution', modifying: false, copying: false,
    fillingForms: true, contentAccessibility: true },
});
```

---

## Setting Permissions

```python
from pypdf.constants import UserAccessPermissions

permissions = UserAccessPermissions.PRINT | UserAccessPermissions.PRINT_TO_REPRESENTATION
writer.encrypt(user_password='', owner_password='adminpass',
               algorithm='AES-256', permissions_flag=permissions)
```

Common flags: `PRINT`, `MODIFY`, `EXTRACT`, `FILL_FORM`, `PRINT_TO_REPRESENTATION`.

---

## Real vs Fake Redaction

**Fake**: black rectangles, background-coloured text, overlaid shapes. All leave original text in the content stream. Anyone can copy or extract it. This is the most common PDF data breach source.

**Real**: permanently removes content bytes. After real redaction, original text no longer exists in the file.

---

## Redaction Workflow

Three phases: **mark, apply, verify**.

```python
import fitz  # PyMuPDF

# 1. MARK
doc = fitz.open('sensitive.pdf')
for page in doc:
    for pattern in ['SSN: \\d{3}-\\d{2}-\\d{4}', 'CONFIDENTIAL']:
        for inst in page.search_for(pattern):
            page.add_redact_annot(inst, fill=(0, 0, 0), text='[REDACTED]')

# 2. APPLY — permanently destroys content
for page in doc:
    page.apply_redactions()
doc.save('redacted.pdf', garbage=4, deflate=True)
```

Save with `garbage=4` to clean orphaned objects. Then verify:

```python
import pdfplumber

with pdfplumber.open('redacted.pdf') as pdf:
    for i, page in enumerate(pdf.pages):
        text = page.extract_text() or ''
        for term in ['123-45-6789', 'CONFIDENTIAL']:
            assert term.lower() not in text.lower(), f"Page {i+1}: '{term}' remains"
```

Manual checks: select/copy in redacted areas, search in viewer, `pdftotext redacted.pdf - | grep -i "secret"`.

---

## Metadata Scrubbing

```bash
python3 scripts/scrub_metadata.py input.pdf cleaned.pdf
```

See `scripts/scrub_metadata.py` for implementation. For deeper scrubbing (XMP, embedded files, JS), use PyMuPDF's `doc.scrub(metadata=True, javascript=True, embedded_files=True, xml_metadata=True)` and save with `garbage=4`.

---

## Do / Avoid

### Do

- Use AES-256 for all password-protected PDFs.
- Use real redaction (`apply_redactions()`) that removes content bytes.
- Verify redaction with extraction and copy/paste tests.
- Scrub metadata before external distribution.

### Avoid

- RC4 encryption (40 or 128-bit).
- Black rectangles as "redaction" (content remains extractable).
- Assuming permission flags stop a determined attacker.
- Skipping verification after redaction.

---

## Checklist: Pre-Distribution Security Review

- [ ] Encryption uses AES-256; owner password differs from user password
- [ ] Permission flags match intended restrictions
- [ ] Sensitive content uses real redaction, not overlays
- [ ] Redaction verified: extraction and copy/paste yield nothing
- [ ] Metadata scrubbed (author, creator, producer, timestamps)
- [ ] No embedded files, JavaScript, or hidden layers remain
- [ ] Saved with `garbage=4` to remove orphaned objects

---

## Related

- [pdf-forms-interactive.md](pdf-forms-interactive.md) — Form creation and filling
- [pdf-generation-patterns.md](pdf-generation-patterns.md) — Layout and generation code
- [pdf-accessibility-compliance.md](pdf-accessibility-compliance.md) — Tags and compliance
- [../scripts/scrub_metadata.py](../scripts/scrub_metadata.py) — Metadata scrubbing helper
