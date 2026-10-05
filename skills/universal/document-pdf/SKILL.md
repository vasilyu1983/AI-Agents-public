---
name: document-pdf
description: Handles PDF/UA accessibility, real redaction, metadata scrubbing, signing, and extraction. Use when redacting or signing PDFs; for plain create/merge prefer the official pdf skill.
allowed-tools: Bash, Read, Write, Glob, Grep
compatibility: Claude Code + Codex. Uses runtime-specific allowed-tools / argument-hint fields.
version: "1.2"
last_validated: 2026-07-11
---

# Document PDF Skill — Quick Reference

**Boundary:** when the official Anthropic `pdf` skill is available, prefer it for plain create, merge/split, form fill, and CLI (qpdf/pdftotext) work. Use this skill for its unique lanes: accessibility (PDF/UA-1/UA-2, EAA), real redaction and its evidence gate, metadata scrubbing, pyHanko signing, OCR/table extraction discipline, and PyMuPDF/pdf-lib licensing and maintenance risk.

- EU compliance: scope the product/service and national implementation before applying the EAA to a PDF. Verify that any cited harmonised standard supports the specific applicable legislation in the Official Journal; an EN 301 549 citation under another directive is insufficient. Load [references/pdf-accessibility-compliance.md](references/pdf-accessibility-compliance.md#eu-eaa-and-en-301-549) for that scoping step.
- Metadata exists in multiple layers: PDF Info/XMP, filesystem dates, and OS extended attributes. Scrubbing one layer leaves the others available.

## Core Decision Rules

- First decide: born-digital PDF (selectable text) vs scanned PDF (images). Scanned PDFs usually require OCR; see `references/pdf-extraction-patterns.md`.
- If the user needs accessibility/compliance, prefer generating from a source format that supports structure (DOCX/HTML + proper export) rather than “post-fixing” an untagged PDF.
- For deterministic ops (merge/split/rotate/scrub), prefer `scripts/` helpers over re-implementing ad hoc.
- Never treat black rectangles or overlays as redaction. Real redaction removes the content bytes: PyMuPDF `page.add_redact_annot(rect)` then `page.apply_redactions()` per page, then save. Prove it with the [redaction evidence gate](#redaction-evidence-gate).
- Password protection: pypdf `writer.encrypt(..., algorithm='AES-256')` (security handler R6). Omitting `algorithm` writes RC4-128, so always pass it; use `AES-256-R5` only for a named legacy reader. Permission flags are advisory, not security. See [references/pdf-security-redaction.md](references/pdf-security-redaction.md).
- Table extraction is probabilistic, not deterministic: run `pdfplumber` first and spot-check output against the source page; escalate to `Camelot` only when columns/rows are visibly wrong, and always inspect Camelot's per-table `accuracy` score rather than trusting output blindly.
- `PyMuPDF`/`fitz` (used by `scrub_metadata.py` and most redaction/OCR-prep code below) is dual-licensed **AGPL-3.0 / commercial**. Flag this before shipping it inside a closed-source product or SaaS backend — AGPL's network-use clause can trigger a source-disclosure obligation; get a commercial license from Artifex or substitute `pypdf`/`pdfplumber` where the required functionality overlaps.
- `pdf-lib` (Node): check the upstream package's release activity before depending on it. If it is stale and you need ongoing fixes, evaluate a maintained fork before committing, and pin the dependency either way.

---

## Quick Reference

| Task | Tool/Library | Language | When to Use |
|------|--------------|----------|-------------|
| Create PDF | pdfkit | Node.js | Reports, invoices, certificates |
| Create PDF | ReportLab | Python | Complex layouts, tables |
| Create PDF | FPDF2 | Python | Simple PDFs with Unicode support |
| Edit PDF | pdf-lib | Node.js | Modify existing PDFs, add pages (check upstream release activity first) |
| Parse/merge/split/rotate | pypdf | Python | Deterministic PDF manipulation |
| Extract text | pdfplumber | Python | OCR-free text extraction |
| OCR scanned PDF | OCRmyPDF | Python/CLI | Searchable text layer for scanned PDFs |
| Custom OCR pipeline | PyMuPDF (fitz) + Tesseract | Python | Page-level OCR or image-heavy extraction — **PyMuPDF is AGPL-3.0/commercial dual-licensed** |
| Extract tables | pdfplumber | Python | Default table extraction; verify visually before trusting |
| Extract hard tables | Camelot (camelot-py) | Python | Lattice/stream edge cases; check the installed release's backends and inspect `table.accuracy` either way |
| Fill forms | pypdf (`update_page_form_field_values`) / pdf-lib | Python / Node.js | Form automation; see `references/pdf-forms-interactive.md` |
| Sign PDFs | pyHanko | Python/CLI | Digital signatures and validation |
| HTML to PDF | Playwright | Node.js | Browser-faithful web page rendering |
| HTML to tagged PDF | WeasyPrint | Python | Semantic HTML, PDF/A or PDF/UA-oriented export |
| Validate PDF/A | veraPDF | CLI/GUI | Archival conformance checks |
| Validate PDF accessibility | veraPDF (PDF/UA-1, PDF/UA-2 profiles) + PAC / Acrobat Checker | CLI/GUI | Machine-checkable PDF/UA rules in CI, then manual checks |
| Inspect/edit file metadata | exiftool | CLI | Audit or rewrite internal dates, XMP, EXIF, ICC across PDF/image files |
| Normalise filesystem dates | touch / SetFile | CLI (macOS) | Set timestamps to the release/build date; never backdate records |

## Default Workflow

- Create: use `Playwright` for browser-faithful HTML/CSS, `WeasyPrint` for semantic/tagged HTML exports, `ReportLab` for Python-heavy layouts, or `pdfkit` for Node-first custom layout.
- Extract: first classify the file as born-digital vs scanned; run `OCRmyPDF` before downstream extraction on scanned PDFs, then use `references/pdf-extraction-patterns.md`.
- Ship: run `assets/pdf-release-checklist.md`; add `PAC` / Acrobat checks for accessibility-sensitive PDFs and `veraPDF` when archival conformance matters.

## Scripts And Exit Codes

Each script needs Python 3 plus the dependency named in its `--help`.

```bash
python3 scripts/merge_pdfs.py merged.pdf a.pdf b.pdf
python3 scripts/split_pdf.py in.pdf out_dir --each-page
python3 scripts/rotate_pdf.py in.pdf out.pdf --degrees 90
python3 scripts/scrub_metadata.py in.pdf out.pdf
python3 scripts/scrub_metadata.py in.pdf out.pdf --filesystem-date <publication-date> --strip-xattrs
python3 scripts/test_scrub_metadata.py
```

- Input errors exit nonzero; argparse usage errors exit 2. `scrub_metadata.py` exits 1 on scrub or requested filesystem-operation failure, with an error on stderr. It stages output beside the destination and replaces it only after all requested operations succeed, preserving an existing destination on failure. Input and output must differ. On macOS `--strip-xattrs` clears all output attributes using `xattr`; `--filesystem-date` also requires `SetFile` for creation time. Other platforms support access/modification times only and reject `--strip-xattrs`.
- `scrub_metadata.py` removes Info/XMP metadata, attachments, JavaScript and thumbnails, and **keeps OCR text layers and links by default**. PyMuPDF's own `scrub()` deletes both; the script does so only with `--remove-hidden-text` / `--remove-links`. Stripping the OCR layer makes a scanned PDF unsearchable and inaccessible.
- `--strip-xattrs` checks for residual attributes after clearing them. macOS may retain protected provenance attributes despite command success; the helper then rejects publication. Resolve the applicable host policy and verify the released file separately instead of assuming all traces were removed.

## Do / Avoid

### Do

- Keep a versioned source document (doc/slide/design file) alongside the PDF.
- Verify links and reading order for long documents.
- Use real redaction and test by copy/paste.
- Use `OCRmyPDF` for scanned PDFs before text extraction.
- Scrub all metadata layers before distribution (PDF-internal, filesystem dates, macOS xattrs).
- Verify with `exiftool -all -G1` after scrubbing — check for residual usernames, paths, tool stamps, and dates you did not intend to publish.
- Confirm PyMuPDF's AGPL/commercial licensing fits the deployment before relying on it in closed-source or SaaS code paths.

### Avoid

- Editing PDFs as the primary workflow when a source doc exists.
- Defaulting to `wkhtmltopdf` in new workflows.
- Shipping PDFs with broken links or illegible charts.
- Including customer PII or secrets in PDFs without explicit approval.
- Scrubbing only PDF-internal metadata while ignoring filesystem dates and OS-level xattrs.
- Backdating file or metadata dates to misrepresent when a record was created (falsification); normalise to the real publication date instead.
- Trusting `Camelot`/`pdfplumber` table output on financial or legal documents without a visual spot-check or accuracy-score review — misaligned columns fail silently.
- Bundling PyMuPDF into a proprietary product without checking AGPL obligations or budgeting for a commercial license.

For export QA, render every page with `pdftoppm -png -r 80 out.pdf page` (Poppler) and inspect the `page-*.png` files alongside `assets/pdf-release-checklist.md`.

## Redaction Evidence Gate

Prove redaction against every representation that can disclose the value: extracted text, search results, copy/paste, page rendering, annotations, form fields, attachments, and metadata. Reopen the final saved file in a second parser or viewer and search for the sensitive tokens plus normalized variants; inspect the redacted region at high zoom to catch overlays, shifted text, and partial glyphs. Record the token set or synthetic stand-ins used for verification without reproducing sensitive values in logs. If OCR was involved, test both the visible image and hidden text layer. A black box, empty search result in one viewer, or metadata scrub alone is not sufficient evidence that content was removed.

## Navigation

**Resources**
- [references/pdf-generation-patterns.md](references/pdf-generation-patterns.md) — Complex layouts, multi-page docs
- [references/pdf-extraction-patterns.md](references/pdf-extraction-patterns.md) — Text, table, image extraction
- [references/extraction-stack.md](references/extraction-stack.md) — Load when picking an extraction tool (native parse vs Docling vs OCR) for a new LLM/RAG pipeline
- [references/pdf-accessibility-compliance.md](references/pdf-accessibility-compliance.md) — Tagged PDFs, PDF/UA, EAA compliance
- [references/pdf-forms-interactive.md](references/pdf-forms-interactive.md) — AcroForms, form filling, digital signatures
- [references/pdf-security-redaction.md](references/pdf-security-redaction.md) — Encryption, permissions, real redaction
- [data/sources.json](data/sources.json) — Library documentation links

**Scripts**
- `scripts/merge_pdfs.py` — Merge PDFs in order
- `scripts/split_pdf.py` — Split one-per-page or by range
- `scripts/rotate_pdf.py` — Rotate all pages by 90/180/270 degrees
- `scripts/scrub_metadata.py` — Scrub Info/XMP metadata, attachments, JavaScript, and thumbnails (keeps OCR text and links by default)

**Templates**
- [assets/invoice-template.md](assets/invoice-template.md) — Invoice PDF generation
- [assets/report-template.md](assets/report-template.md) — Multi-page report structure
- [assets/pdf-release-checklist.md](assets/pdf-release-checklist.md) — Links, accessibility, export fidelity

**Related Skills**
- [../document-docx/SKILL.md](../document-docx/SKILL.md) — Word document generation
- [../document-xlsx/SKILL.md](../document-xlsx/SKILL.md) — Excel/spreadsheet workflows
- [../document-pptx/SKILL.md](../document-pptx/SKILL.md) — PowerPoint presentations

## Learnings Loop

When prior decisions or pitfalls are relevant, consult `learnings.consolidated.md` if present; use `learnings.md` only for needed history or as the available fallback. Otherwise skip both.

After applying it, if you encountered a pattern worth remembering, a mistake worth preventing, or a domain fact that surprised you, append one dated bullet to `learnings.md` via `agents-skills-feedback-loop/scripts/append_learning.py`. Do not modify `SKILL.md` itself.
