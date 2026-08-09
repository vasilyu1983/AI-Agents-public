---
name: document-pdf
description: Extracts, creates, and transforms PDF documents. Use when parsing text or tables, generating files, merging pages, or handling PDF forms.
allowed-tools: Bash, Read, Write, Glob, Grep
compatibility: Claude Code + Codex. Uses runtime-specific allowed-tools / argument-hint fields.
version: "1.1"
last_validated: 2026-07-11
---

# Document PDF Skill — Quick Reference

This skill enables PDF creation, extraction, manipulation, and analysis. Apply these patterns when users need to generate invoices, reports, extract data from PDFs, merge documents, or work with PDF forms.

**Modern Best Practices (Jul 2026)**:
- PDF is a release artifact, not the editable source of truth.
- Validate export fidelity (fonts, images, links) and accessibility where required.
- Accessibility: if compliance matters, target a tagged/structured PDF workflow (often PDF/UA-aligned) and validate with tooling.
- EU distribution: EAA (June 2025) typically implies EN 301 549 expectations for customer-facing PDFs.
- Treat PDFs as sensitive: scrub metadata at all layers (PDF-internal, filesystem, OS xattrs), ensure real redaction, and control distribution.
- Metadata exists in multiple layers: PDF Info/XMP (internal), filesystem dates (OS), and extended attributes (macOS quarantine, provenance). Scrubbing one layer while ignoring others leaves traces.

## Core Decision Rules (2026)

- First decide: born-digital PDF (selectable text) vs scanned PDF (images). Scanned PDFs usually require OCR; see `references/pdf-extraction-patterns.md`.
- If the user needs accessibility/compliance, prefer generating from a source format that supports structure (DOCX/HTML + proper export) rather than “post-fixing” an untagged PDF.
- For deterministic ops (merge/split/rotate/scrub), prefer `scripts/` helpers over re-implementing ad hoc.
- Never treat black rectangles or overlays as redaction; use real redaction and verify by copy/paste + search.
- Table extraction is probabilistic, not deterministic: run `pdfplumber` first and spot-check output against the source page; escalate to `Camelot` only when columns/rows are visibly wrong, and always inspect Camelot's per-table `accuracy` score rather than trusting output blindly.
- `PyMuPDF`/`fitz` (used by `scrub_metadata.py` and most redaction/OCR-prep code below) is dual-licensed **AGPL-3.0 / commercial**. Flag this before shipping it inside a closed-source product or SaaS backend — AGPL's network-use clause can trigger a source-disclosure obligation; get a commercial license from Artifex or substitute `pypdf`/`pdfplumber` where the required functionality overlaps.
- `pdf-lib` (Node) has had no active upstream releases for an extended period as of mid-2026; for new Node projects needing ongoing fixes, evaluate a maintained fork (e.g. `@cantoo/pdf-lib`) before committing, and pin the dependency either way.

---

## Quick Reference

| Task | Tool/Library | Language | When to Use |
|------|--------------|----------|-------------|
| Create PDF | pdfkit | Node.js | Reports, invoices, certificates |
| Create PDF | ReportLab | Python | Complex layouts, tables |
| Create PDF | FPDF2 | Python | Simple PDFs with Unicode support |
| Edit PDF | pdf-lib | Node.js | Modify existing PDFs, add pages (upstream low-activity — consider a maintained fork) |
| Parse/merge/split/rotate | pypdf | Python | Deterministic PDF manipulation |
| Extract text | pdfplumber | Python | OCR-free text extraction |
| OCR scanned PDF | OCRmyPDF | Python/CLI | Searchable text layer for scanned PDFs |
| Custom OCR pipeline | PyMuPDF (fitz) + Tesseract | Python | Page-level OCR or image-heavy extraction — **PyMuPDF is AGPL-3.0/commercial dual-licensed** |
| Extract tables | pdfplumber | Python | Default table extraction; verify visually before trusting |
| Extract hard tables | Camelot (camelot-py) | Python | Lattice/stream edge cases; 2026 releases add an optional neural backend — check `table.accuracy` either way |
| Fill forms | pdf-lib | Node.js | Form automation |
| Sign PDFs | pyHanko | Python/CLI | Digital signatures and validation |
| HTML to PDF | Playwright | Node.js | Browser-faithful web page rendering |
| HTML to tagged PDF | WeasyPrint | Python | Semantic HTML, PDF/A or PDF/UA-oriented export |
| Validate PDF/A | veraPDF | CLI/GUI | Archival conformance checks |
| Validate PDF accessibility | PAC / Acrobat Checker | GUI | PDF/UA and accessibility checks |
| Inspect/edit file metadata | exiftool | CLI | Audit or rewrite internal dates, XMP, EXIF, ICC across PDF/image files |
| Set filesystem dates | touch / SetFile | CLI (macOS) | Correct creation/modification timestamps at OS level |

## When to Use This Skill

Use this skill when a user requests:

- Generate PDFs from data (invoices, reports, certificates)
- Extract text or tables from existing PDFs
- Merge multiple PDFs into one document
- Split PDFs into separate files
- Fill PDF forms programmatically
- Add watermarks, headers, footers
- Convert HTML/web pages to PDF

---

## Default Workflow

- Create: use `Playwright` for browser-faithful HTML/CSS, `WeasyPrint` for semantic/tagged HTML exports, `ReportLab` for Python-heavy layouts, or `pdfkit` for Node-first custom layout.
- Extract: first classify the file as born-digital vs scanned; run `OCRmyPDF` before downstream extraction on scanned PDFs, then use `references/pdf-extraction-patterns.md`.
- Ship: run `assets/pdf-release-checklist.md`; add `PAC` / Acrobat checks for accessibility-sensitive PDFs and `veraPDF` when archival conformance matters.

## ASCII Flow

```text
PDF request
  |
  v
Classify task
  |-- create new PDF
  |-- extract text / tables / images
  |-- modify existing PDF
  |-- fill / sign forms
  |-- merge / split / rotate / scrub
  |
  v
Classify source and risk
  |-- born-digital ----> extract directly
  |-- scanned ---------> OCR first
  |-- sensitive -------> real redaction + metadata scrub
  |-- compliance ------> tagged / structured source workflow
  |
  v
Select tool or script
  |-- HTML/CSS --------> Playwright or WeasyPrint
  |-- Python layout ---> ReportLab / FPDF2
  |-- deterministic ---> scripts/ + pypdf
  |-- extraction ------> pdfplumber / OCRmyPDF / Camelot
  |
  v
Verify fidelity, accessibility, metadata, and redaction
```

## Scripts (Deterministic Operations)

Scripts are optional helpers; they assume Python 3 plus the listed dependencies in each file.

- Merge: `python3 scripts/merge_pdfs.py merged.pdf a.pdf b.pdf`
- Split: `python3 scripts/split_pdf.py in.pdf out_dir --each-page`
- Rotate: `python3 scripts/rotate_pdf.py in.pdf out.pdf --degrees 90`
- Scrub metadata and active content: `python3 scripts/scrub_metadata.py in.pdf out.pdf`
- Scrub with filesystem + xattr cleanup: `python3 scripts/scrub_metadata.py in.pdf out.pdf --filesystem-date 2025-09-20 --strip-xattrs`

## PDF Structure Patterns

### Invoice Template

```text
INVOICE STRUCTURE
├── Header (logo, company info, invoice #)
├── Bill To / Ship To blocks
├── Line items table
│   ├── Description | Qty | Unit Price | Total
│   └── Subtotal, Tax, Total
├── Payment terms
└── Footer (contact, thank you)
```

### Report Template

```text
REPORT PDF STRUCTURE
├── Cover page (title, author, date)
├── Table of contents
├── Body sections with page numbers
├── Charts/images with captions
├── Appendices
└── Running header/footer
```

---

## Decision Tree

```text
PDF Task: [What do you need?]
    ├─ Create new PDF?
    │   ├─ Browser-faithful HTML/CSS → Playwright
    │   ├─ Semantic HTML / tagged export → WeasyPrint
    │   ├─ Node-first custom layout → pdfkit
    │   └─ Python complex layout → ReportLab / FPDF2
    │
    ├─ Extract from PDF?
    │   ├─ Born-digital text → pdfplumber (Python)
    │   ├─ Scanned pages → OCRmyPDF, then pdfplumber
    │   ├─ Tables → pdfplumber first, Camelot for hard cases
    │   └─ Images / raster work → PyMuPDF/fitz
    │
    ├─ Modify existing PDF?
    │   ├─ Add text/images → pdf-lib (Node)
    │   ├─ Merge/split/rotate/scrub → pypdf + scripts
    │   ├─ Fill forms → pdf-lib
    │   └─ Sign → pyHanko
    │
    └─ Batch processing?
        └─ OCRmyPDF / pypdf / pdfplumber pipeline
```

---

## Do / Avoid (Jul 2026)

### Do

- Keep a versioned source document (doc/slide/design file) alongside the PDF.
- Verify links and reading order for long documents.
- Use real redaction and test by copy/paste.
- Use `OCRmyPDF` for scanned PDFs before text extraction.
- Scrub all metadata layers before distribution (PDF-internal, filesystem dates, macOS xattrs).
- Verify with `exiftool -all -G1` after scrubbing — check for tool fingerprints (XMP Toolkit) and residual dates.
- Confirm PyMuPDF's AGPL/commercial licensing fits the deployment before relying on it in closed-source or SaaS code paths.

### Avoid

- Editing PDFs as the primary workflow when a source doc exists.
- Defaulting to `wkhtmltopdf` in new 2026 workflows.
- Shipping PDFs with broken links or illegible charts.
- Including customer PII or secrets in PDFs without explicit approval.
- Scrubbing only PDF-internal metadata while ignoring filesystem dates and OS-level xattrs.
- Using exiftool to modify PDF XMP without overwriting its `XMP Toolkit` fingerprint.
- Trusting `Camelot`/`pdfplumber` table output on financial or legal documents without a visual spot-check or accuracy-score review — misaligned columns fail silently.
- Bundling PyMuPDF into a proprietary product without checking AGPL obligations or budgeting for a commercial license.

## What Good Looks Like

- Fidelity: export is reproducible from a versioned source file (doc/slide/design) and looks identical across viewers.
- Accessibility: tags/reading order are correct; links work; scanned docs are OCRed when appropriate.
- Release hygiene: file naming includes version/date; metadata is clean; no “PDF as source of truth”.
- Security: redaction is verified (copy/paste test) and sensitive data is minimized.
- QA: release checklist completed using `assets/pdf-release-checklist.md`.

## Optional: AI / Automation

Use only when explicitly requested and policy-compliant.

- Generate a release checklist run; humans verify the final PDF manually.

## Navigation

**Resources**
- [references/pdf-generation-patterns.md](references/pdf-generation-patterns.md) — Complex layouts, multi-page docs
- [references/pdf-extraction-patterns.md](references/pdf-extraction-patterns.md) — Text, table, image extraction
- [references/pdf-accessibility-compliance.md](references/pdf-accessibility-compliance.md) — Tagged PDFs, PDF/UA, EAA compliance
- [references/pdf-forms-interactive.md](references/pdf-forms-interactive.md) — AcroForms, form filling, digital signatures
- [references/pdf-security-redaction.md](references/pdf-security-redaction.md) — Encryption, permissions, real redaction
- [data/sources.json](data/sources.json) — Library documentation links

**Scripts**
- `scripts/merge_pdfs.py` — Merge PDFs in order
- `scripts/split_pdf.py` — Split one-per-page or by range
- `scripts/rotate_pdf.py` — Rotate all pages by 90/180/270 degrees
- `scripts/scrub_metadata.py` — Scrub Info/XMP metadata, attachments, JavaScript, and thumbnails

**Templates**
- [assets/invoice-template.md](assets/invoice-template.md) — Invoice PDF generation
- [assets/report-template.md](assets/report-template.md) — Multi-page report structure
- [assets/pdf-release-checklist.md](assets/pdf-release-checklist.md) — Links, accessibility, export fidelity

**Related Skills**
- [../document-docx/SKILL.md](../document-docx/SKILL.md) — Word document generation
- [../document-xlsx/SKILL.md](../document-xlsx/SKILL.md) — Excel/spreadsheet workflows
- [../document-pptx/SKILL.md](../document-pptx/SKILL.md) — PowerPoint presentations

## Fact-Checking

- Use web search/web fetch to verify current external facts, versions, pricing, deadlines, regulations, or platform behavior before final answers.
- Prefer primary sources; report source links and dates for volatile information.
- If web access is unavailable, state the limitation and mark guidance as unverified.

## Learnings Loop

Before applying this skill on a non-trivial task, read `learnings.consolidated.md` in this directory (and `learnings.md` if present).

After applying it, if you encountered a pattern worth remembering, a mistake worth preventing, or a domain fact that surprised you, append one dated bullet to `learnings.md` via `agents-skills-feedback-loop/scripts/append_learning.py`. Do not modify `SKILL.md` itself.

