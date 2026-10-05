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
| AES 256-bit | Recommended | Two security-handler revisions. pypdf `algorithm='AES-256'` writes **R6**, the revision PDF 2.0 (ISO 32000-2) defines: use it by default. `algorithm='AES-256-R5'` writes **R5** (Adobe Extension Level 3 to PDF 1.7), which PDF 2.0 deprecates: use it only when a named legacy reader cannot open R6. |

PDF uses two passwords: **user** (to open) and **owner** (to change permissions). Permission flags are viewer-enforced, not cryptographic. Encryption prevents content access; permissions are advisory.

---

## Password Protection

### pypdf

```python
import os
from pypdf import PdfReader, PdfWriter

reader = PdfReader('report.pdf')
writer = PdfWriter()
for page in reader.pages:
    writer.add_page(page)
writer.encrypt(user_password=os.environ['PDF_USER_PW'],
               owner_password=os.environ['PDF_OWNER_PW'], algorithm='AES-256')  # R6
with open('encrypted.pdf', 'wb') as f:
    writer.write(f)
```

pypdf accepts `RC4-40`, `RC4-128`, `AES-128`, `AES-256-R5` and `AES-256`. **Omitting `algorithm` writes RC4-128 (R3)**, so always pass it explicitly. Verify what was written by reopening the file: `PdfReader(path).trailer['/Encrypt']['/R']` should be `6` (or `5` for the legacy case). Never put real passwords in source code; read them from the environment or a secret store. Verify any alternative library against its primary documentation before treating it as encryption-capable.

---

## Setting Permissions

```python
from pypdf.constants import UserAccessPermissions

permissions = UserAccessPermissions.PRINT | UserAccessPermissions.PRINT_TO_REPRESENTATION
writer.encrypt(user_password='', owner_password=os.environ['PDF_OWNER_PW'],
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
import re
import pymupdf  # PyMuPDF (AGPL/commercial)

# page.search_for() matches LITERAL strings only; a regex passed to it finds nothing.
# For patterns, match on words (or lines) with `re`, then redact the matched rectangles.
PATTERNS = [re.compile(r"\b\d{3}-\d{2}-\d{4}\b")]   # e.g. US SSN
LITERALS = ["CONFIDENTIAL"]

# 1. MARK
doc = pymupdf.open('sensitive.pdf')
for page in doc:
    for x0, y0, x1, y1, word, *_ in page.get_text("words"):
        if any(p.search(word) for p in PATTERNS):
            page.add_redact_annot(pymupdf.Rect(x0, y0, x1, y1), fill=(0, 0, 0))
    for term in LITERALS:
        for rect in page.search_for(term):
            page.add_redact_annot(rect, fill=(0, 0, 0))

# 2. APPLY — permanently removes the covered text (and, by default, overlapping image pixels)
for page in doc:
    page.apply_redactions()
doc.save('redacted.pdf', garbage=4, deflate=True)  # full rewrite, never incremental
```

Word-level matching misses patterns that span several words (e.g. "SSN: 123 45 6789"); for those, match per line from `page.get_text("dict")` spans, or search for each literal hit returned by a regex over `page.get_text()`.

Save with `garbage=4` and without `incremental=True`: an incremental save appends changes and leaves the original, unredacted objects recoverable in the file. Then verify:

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

**Caveat — tool stamps**: tools that modify PDF metadata add their own. For example, `exiftool` writes `XMP Toolkit: Image::ExifTool <version>` into the XMP. If the goal is to avoid leaking internal tooling or usernames, prefer PyMuPDF's `scrub()` (which removes XMP entirely) over editing XMP fields with exiftool. The purpose is privacy hygiene, not hiding that a file was processed.

**Content is preserved by default**: `scrub_metadata.py` keeps invisible text (the searchable OCR layer on scanned PDFs) and hyperlinks. PyMuPDF's `scrub()` deletes both unless told otherwise; the script only does so with the explicit `--remove-hidden-text` / `--remove-links` flags.

### Layer 2: Filesystem Dates

Filesystem creation/modification/access dates are independent of PDF-internal dates. They mostly do not travel with a file sent by email or HTTP, but they do travel inside archives and synced folders. Legitimate reasons to set them:

- Normalising timestamps to the release or build date for reproducible builds or archive packaging.
- Removing a timestamp that reveals when an individual worked on a file (privacy), by setting it to the publication date.

**Do not use timestamps to misrepresent when a document was created or signed.** Backdating contracts, evidence, audit records, or regulated records is falsification and can be fraud or obstruction. If a record's true creation date matters, keep it.

```bash
# Set modification + access dates (macOS/Linux) to the publication date
touch -t YYYYMMDDhhmm.ss file.pdf

# Set creation date (macOS only, requires Xcode CLI tools)
SetFile -d "MM/DD/YYYY HH:MM:SS" file.pdf
```

**Note**: `File Inode Change Date` (ctime) is kernel-managed and updates on any file operation (Spotlight indexing, backups, antivirus). That is normal and cannot be set from user space.

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

# 3. Optional: normalise filesystem dates to the publication date (never to a false past date)
touch -t "$(date +%Y%m%d%H%M.%S)" cleaned.pdf

# 4. Verify with exiftool
exiftool -all -G1 cleaned.pdf
```

### Verification with exiftool

`exiftool` is the most thorough way to audit all metadata layers:

```bash
# Full dump — check for remaining dates, tool stamps, usernames, or paths
exiftool -all -G1 file.pdf

# Filter for date fields only
exiftool -time:all -G1 file.pdf

# Check which tools stamped the file
exiftool -XMPToolkit -Producer -Creator -G1 file.pdf
```

---

## Do / Avoid

### Do

- Use AES-256 for all password-protected PDFs: pypdf `AES-256` (R6) by default, `AES-256-R5` only for a named legacy reader.
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

- [ ] Encryption uses AES-256 (`/R` 6, or 5 for a named legacy reader; never RC4); owner password differs from user password
- [ ] Permission flags match intended restrictions
- [ ] Sensitive content uses real redaction, not overlays
- [ ] Redaction verified: extraction and copy/paste yield nothing
- [ ] PDF-internal metadata scrubbed (Info dict + XMP: author, creator, producer, timestamps)
- [ ] No internal usernames, paths, or tool stamps remain that you did not intend to publish (check Producer/Creator/XMP Toolkit)
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
