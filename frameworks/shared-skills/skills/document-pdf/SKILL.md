---
name: document-pdf
description: Extract text/tables from PDFs, create formatted PDFs, merge/split/rotate, handle forms and metadata. Supports pdf-lib/pdfkit (Node.js) and pypdf/pdfplumber/ReportLab (Python).
---

# Document PDF Skill — Quick Reference

This skill enables PDF creation, extraction, manipulation, and analysis. Claude should apply these patterns when users need to generate invoices, reports, extract data from PDFs, merge documents, or work with PDF forms.

**Modern Best Practices (Jan 2026)**:
- PDF is a release artifact, not the editable source of truth.
- Validate export fidelity (fonts, images, links) and accessibility where required.
- Accessibility: if compliance matters, target a tagged/structured PDF workflow (often PDF/UA-aligned) and validate with tooling.
- EU distribution: EAA (June 2025) typically implies EN 301 549 expectations for customer-facing PDFs.
- Treat PDFs as sensitive: scrub metadata, ensure real redaction, and control distribution.

## Core Decision Rules (2026)

- First decide: born-digital PDF (selectable text) vs scanned PDF (images). Scanned PDFs usually require OCR; see `references/pdf-extraction-patterns.md`.
- If the user needs accessibility/compliance, prefer generating from a source format that supports structure (DOCX/HTML + proper export) rather than “post-fixing” an untagged PDF.
- For deterministic ops (merge/split/rotate/scrub), prefer `scripts/` helpers over re-implementing ad hoc.
- Never treat black rectangles or overlays as redaction; use real redaction and verify by copy/paste + search.

---

## Quick Reference

| Task | Tool/Library | Language | When to Use |
|------|--------------|----------|-------------|
| Create PDF | pdfkit | Node.js | Reports, invoices, certificates |
| Create PDF | ReportLab | Python | Complex layouts, tables |
| Create PDF | FPDF2 | Python | Simple PDFs with Unicode support |
| Create PDF | Borb | Python | Interactive elements, pure Python |
| Edit PDF | pdf-lib | Node.js | Modify existing PDFs, add pages |
| Extract text | pdfplumber | Python | OCR-free text extraction |
| OCR scanned PDF | PyMuPDF + Tesseract | Python | Scanned PDFs (no selectable text) |
| Extract tables | Camelot | Python | Tables with borders (Lattice mode) |
| Extract tables | Camelot/Tabula | Python | Tables without borders (Stream mode) |
| Parse/merge/split/rotate | pypdf | Python | Deterministic PDF manipulation |
| Fill forms | pdf-lib | Node.js | Form automation |
| HTML to PDF | Puppeteer/Playwright | Node.js | High-fidelity web page rendering |
| HTML to PDF | WeasyPrint | Python | CSS3-based, no browser needed |

## When to Use This Skill

Claude should invoke this skill when a user requests:

- Generate PDFs from data (invoices, reports, certificates)
- Extract text or tables from existing PDFs
- Merge multiple PDFs into one document
- Split PDFs into separate files
- Fill PDF forms programmatically
- Add watermarks, headers, footers
- Convert HTML/web pages to PDF

---

## Default Workflow

- Create: pick `pdfkit` (Node) or `ReportLab` (Python) and start from `assets/invoice-template.md` or `assets/report-template.md`; for advanced layouts use `references/pdf-generation-patterns.md`.
- Extract: use `references/pdf-extraction-patterns.md` (text/tables/images/metadata + OCR fallback).
- Ship: run `assets/pdf-release-checklist.md` (fidelity, links, accessibility baseline, privacy).

## Scripts (Deterministic Operations)

Scripts are optional helpers; they assume Python 3 plus the listed dependencies in each file.

- Merge: `python3 scripts/merge_pdfs.py merged.pdf a.pdf b.pdf`
- Split: `python3 scripts/split_pdf.py in.pdf out_dir --each-page`
- Rotate: `python3 scripts/rotate_pdf.py in.pdf out.pdf --degrees 90`
- Scrub metadata: `python3 scripts/scrub_metadata.py in.pdf out.pdf`

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
    │   ├─ Simple text/tables → pdfkit (Node) or ReportLab (Python)
    │   ├─ Complex layouts → ReportLab with Platypus
    │   └─ From HTML → Puppeteer or wkhtmltopdf
    │
    ├─ Extract from PDF?
    │   ├─ Text only → pdfplumber (Python)
    │   ├─ Tables → pdfplumber or camelot (Python)
    │   └─ Images → PyMuPDF/fitz (Python)
    │
    ├─ Modify existing PDF?
    │   ├─ Add text/images → pdf-lib (Node)
    │   ├─ Merge/split → pypdf or pdf-lib
    │   └─ Fill forms → pdf-lib
    │
    └─ Batch processing?
        └─ pypdf + pdfplumber pipeline
```

---

## Do / Avoid (Jan 2026)

### Do

- Keep a versioned source document (doc/slide/design file) alongside the PDF.
- Verify links and reading order for long documents.
- Use real redaction and test by copy/paste.

### Avoid

- Editing PDFs as the primary workflow when a source doc exists.
- Shipping PDFs with broken links or illegible charts.
- Including customer PII or secrets in PDFs without explicit approval.

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
- [data/sources.json](data/sources.json) — Library documentation links

**Templates**
- [assets/invoice-template.md](assets/invoice-template.md) — Invoice PDF generation
- [assets/report-template.md](assets/report-template.md) — Multi-page report structure
- [assets/pdf-release-checklist.md](assets/pdf-release-checklist.md) — Links, accessibility, export fidelity

**Related Skills**
- [../document-docx/SKILL.md](../document-docx/SKILL.md) — Word document generation
- [../document-xlsx/SKILL.md](../document-xlsx/SKILL.md) — Excel/spreadsheet workflows
- [../document-pptx/SKILL.md](../document-pptx/SKILL.md) — PowerPoint presentations
