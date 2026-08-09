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
| AES 256-bit (`AES-256-R5`) | Recommended | PDF 2.0. pypdf's own docs recommend `AES-256-R5` over the plain `AES-256` revision — pass `algorithm='AES-256-R5'` for new work. |

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
writer.encrypt(user_password='viewpass', owner_password='adminpass', algorithm='AES-256-R5')
with open('encrypted.pdf', 'wb') as f:
    writer.write(f)
```

Valid `algorithm` values in current `pypdf` are `RC4-40`, `RC4-128`, `AES-128`, `AES-256-R5`, and `AES-256`; pypdf's own documentation recommends `AES-256-R5`. Omitting `algorithm` falls back to RC4 for backward compatibility — always pass it explicitly. Keep encryption guidance tied to verified tools: use `pypdf` for Python-side password protection and verify any alternative library against its current primary documentation before treating it as encryption-capable.

---

## Setting Permissions

```python
from pypdf.constants import UserAccessPermissions

permissions = UserAccessPermissions.PRINT | UserAccessPermissions.PRINT_TO_REPRESENTATION
writer.encrypt(user_password='', owner_password='adminpass',
               algorithm='AES-256-R5', permissions_flag=permissions)
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

PDF metadata exists in **three independent layers**. Scrubbing only one leaves traces in the others.

### Layer 1: PDF-Internal (Info dict + XMP)

```bash
python3 scripts/scrub_metadata.py input.pdf cleaned.pdf
```

The shipped helper uses PyMuPDF's `Document.scrub()` plus `garbage=4` to remove document-info metadata, XMP metadata, attachments, embedded files, JavaScript, and thumbnails.

**Caveat — tool fingerprinting**: tools that modify PDF metadata stamp themselves. For example, `exiftool` writes `XMP Toolkit: Image::ExifTool <version>` into the XMP, which reveals the file was post-processed. Either overwrite this field or use PyMuPDF which doesn't add an external toolkit stamp.

### Layer 2: Filesystem Dates

Filesystem creation/modification/access dates are independent of PDF-internal dates. After scrubbing internal metadata, reset filesystem dates:

```bash
# Set modification + access dates (macOS/Linux)
touch -t YYYYMMDDhhmm.ss file.pdf

# Set creation date (macOS only, requires Xcode CLI tools)
SetFile -d "MM/DD/YYYY HH:MM:SS" file.pdf
```

**Note**: `File Inode Change Date` is kernel-managed and resets on any file operation. It cannot be faked and is normal — Spotlight indexing, backups, and antivirus all update it.

### Layer 3: macOS Extended Attributes (xattrs)

macOS silently attaches metadata that leaks provenance and timestamps:

| Attribute | What it reveals |
|---|---|
| `com.apple.quarantine` | Hex timestamp of download + source app (e.g., Safari, Mail, Preview) |
| `com.apple.lastuseddate#PS` | Last time the file was opened |
| `com.apple.metadata:kMDItemIsScreenCapture` | File originated as a macOS screenshot |
| `com.apple.metadata:kMDItemScreenCaptureGlobalRect` | Screen region of the capture |
| `kMDItemDateAdded` | When file was added to the current folder |

Strip with:

```bash
xattr -d com.apple.quarantine file.pdf
xattr -d com.apple.lastuseddate#PS file.pdf
# List all: xattr -l file.pdf
```

Remaining harmless attributes: `com.apple.macl` (access control, no dates), `com.apple.provenance` (empty sandbox marker).

### Full Scrub Workflow

```bash
# 1. Scrub PDF internals
python3 scripts/scrub_metadata.py input.pdf cleaned.pdf

# 2. Strip macOS xattrs
xattr -d com.apple.quarantine cleaned.pdf 2>/dev/null
xattr -d com.apple.lastuseddate#PS cleaned.pdf 2>/dev/null

# 3. Set filesystem dates
touch -t 202509201200.00 cleaned.pdf
SetFile -d "09/20/2025 12:00:00" cleaned.pdf  # macOS only

# 4. Verify with exiftool
exiftool -all -G1 cleaned.pdf
```

### Verification with exiftool

`exiftool` is the most thorough way to audit all metadata layers:

```bash
# Full dump — check for any remaining dates, toolkit stamps, or provenance
exiftool -all -G1 file.pdf

# Filter for date fields only
exiftool -time:all -G1 file.pdf

# Check for tool fingerprints
exiftool -XMPToolkit -Producer -Creator -G1 file.pdf
```

---

## Do / Avoid

### Do

- Use AES-256 (ideally `AES-256-R5`) for all password-protected PDFs.
- Use real redaction (`apply_redactions()`) that removes content bytes.
- Verify redaction with extraction and copy/paste tests.
- Scrub metadata before external distribution.
- Confirm PyMuPDF's AGPL-3.0/commercial dual license fits before shipping the redaction pipeline inside closed-source or SaaS code.

### Avoid

- RC4 encryption (40 or 128-bit).
- Black rectangles as "redaction" (content remains extractable).
- Assuming permission flags stop a determined attacker.
- Skipping verification after redaction.
- Distributing PyMuPDF-based redaction tooling inside a proprietary product without checking AGPL obligations.

---

## Checklist: Pre-Distribution Security Review

- [ ] Encryption uses AES-256 (`AES-256-R5` preferred); owner password differs from user password
- [ ] Permission flags match intended restrictions
- [ ] Sensitive content uses real redaction, not overlays
- [ ] Redaction verified: extraction and copy/paste yield nothing
- [ ] PDF-internal metadata scrubbed (Info dict + XMP: author, creator, producer, timestamps)
- [ ] No tool fingerprints remain (check XMP Toolkit field)
- [ ] No embedded files, JavaScript, or hidden layers remain
- [ ] Saved with `garbage=4` to remove orphaned objects
- [ ] macOS xattrs stripped (quarantine, lastuseddate, screenshot markers)
- [ ] Filesystem dates (creation, modification) set appropriately
- [ ] Final verification with `exiftool -all -G1` shows no unwanted traces

---

## Related

- [pdf-forms-interactive.md](pdf-forms-interactive.md) — Form creation and filling
- [pdf-generation-patterns.md](pdf-generation-patterns.md) — Layout and generation code
- [pdf-accessibility-compliance.md](pdf-accessibility-compliance.md) — Tags and compliance
- [../scripts/scrub_metadata.py](../scripts/scrub_metadata.py) — Metadata scrubbing helper
