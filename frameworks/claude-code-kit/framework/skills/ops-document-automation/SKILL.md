---
name: ops-document-automation
description: Creation, editing, redlining, and processing of DOCX, PDF, PPTX, and XLSX with repeatable workflows, conversions, and QA checks.
---

# Document Automation — Office Formats

Use this multi-format skill when a task involves Office files: drafting/redlining Word docs, converting or templating PowerPoint, extracting or filling PDFs, and building/recalculating Excel models.

---

## When to Use This Skill

- Create or revise DOCX (tracked changes, comments, formatting)
- Convert content to PPTX or generate slides from HTML while preserving layout
- Extract, merge, split, or fill PDFs (text/tables/forms)
- Build or adjust XLSX models with correct color-coding and live formulas
- Recalculate spreadsheets without breaking formulas
- Decide which toolchain to run for a given format
- Automate document generation pipelines (templates + data merge)
- Validate document structure and content quality
- Convert between formats while preserving fidelity

---

## Quick Reference

| Task | Format | Tooling | When to Use |
|------|--------|---------|-------------|
| Draft/review doc | DOCX | pandoc (read), OOXML unpack/pack, docx-js (new docs) | Redlines, comments, legal/academic edits |
| Generate slides | PPTX | html2pptx flow, OOXML unpack | Build decks from HTML or adjust layouts/notes |
| Extract text | PDF | pypdf, pdfplumber | Text extraction, search indexing |
| Extract tables | PDF | pdfplumber, tabula-py | Structured data extraction from PDFs |
| Merge/split PDFs | PDF | pypdf | Combine or separate PDF files |
| Fill forms | PDF | pdf form workflows | AcroForm filling and output validation |
| Recalc/cleanup | XLSX | LibreOffice `recalc.py` | Refresh formulas, clear errors, preserve formats |
| Build models | XLSX | openpyxl/xlsxwriter (formulas), color rules | Dynamic financial/ops models with standards |
| Convert MD to DOCX | DOCX | pandoc | Markdown documentation to Word |
| Convert DOCX to PDF | PDF | LibreOffice headless, pandoc | Final document distribution |

---

## Decision Tree: Picking a Workflow

```text
What do you need to do?
    │
    ├─ Read/Extract only?
    │   ├─ DOCX → pandoc -t plain/markdown
    │   ├─ PPTX → markitdown or html2pptx preview
    │   ├─ PDF → pdfplumber (text/tables)
    │   └─ XLSX → pandas read_excel or openpyxl
    │
    ├─ Create new document?
    │   ├─ DOCX → docx-js (Python: python-docx)
    │   ├─ PPTX → html2pptx pipeline or python-pptx
    │   ├─ PDF → Generate from HTML (weasyprint) or DOCX conversion
    │   └─ XLSX → openpyxl or xlsxwriter with formulas
    │
    ├─ Edit existing document?
    │   ├─ DOCX with tracked changes → OOXML unpack/pack workflow
    │   ├─ PPTX modify slides → OOXML unpack or python-pptx
    │   ├─ PDF fill forms → pypdf or pdftk
    │   └─ XLSX preserve formulas → openpyxl (data_only=False)
    │
    ├─ Convert between formats?
    │   ├─ DOCX → PDF → LibreOffice headless or pandoc
    │   ├─ MD → DOCX → pandoc with reference doc
    │   ├─ HTML → PPTX → html2pptx
    │   └─ XLSX → CSV → pandas to_csv
    │
    └─ Merge/combine documents?
        ├─ PDFs → pypdf PdfMerger
        ├─ DOCX sections → python-docx composer
        └─ XLSX sheets → openpyxl copy_worksheet
```

## Decision Tree: PDF Processing

```text
PDF task?
    │
    ├─ Extract text only?
    │   ├─ Simple layout → pypdf extract_text()
    │   └─ Complex layout → pdfplumber with char analysis
    │
    ├─ Extract tables?
    │   ├─ Clear borders → pdfplumber find_tables()
    │   ├─ Borderless tables → tabula-py with lattice=False
    │   └─ Scanned PDF → OCR first (tesseract), then extract
    │
    ├─ Fill form fields?
    │   ├─ AcroForms → pypdf with form field names
    │   └─ Flatten after fill → pypdf or pdftk
    │
    ├─ Merge multiple PDFs?
    │   └─ pypdf PdfMerger.append() for each file
    │
    ├─ Split PDF?
    │   └─ pypdf PdfWriter with page ranges
    │
    └─ Add watermark/overlay?
        └─ pypdf merge_page() with watermark PDF
```

## Decision Tree: Excel Processing

```text
Excel task?
    │
    ├─ Read data only?
    │   ├─ Small file → pandas read_excel()
    │   └─ Large file → openpyxl read_only=True, iter_rows()
    │
    ├─ Write new workbook?
    │   ├─ Simple data → pandas to_excel()
    │   ├─ With formulas → openpyxl (write formula strings)
    │   └─ High performance → xlsxwriter (write-only)
    │
    ├─ Modify existing workbook?
    │   ├─ Preserve formulas → openpyxl (data_only=False)
    │   ├─ Update values only → openpyxl load + save
    │   └─ Recalculate → LibreOffice headless recalc
    │
    ├─ Format cells?
    │   ├─ Colors/fonts → openpyxl PatternFill, Font
    │   ├─ Conditional formatting → openpyxl ColorScaleRule
    │   └─ Number formats → openpyxl number_format
    │
    └─ Multiple sheets?
        ├─ Copy sheet → openpyxl copy_worksheet()
        └─ Merge workbooks → openpyxl load each, copy sheets
```

---

## Core Capabilities

### DOCX Processing

- **Read**: Extract text, paragraphs, tables, images
- **Write**: Create documents with styles, headers, footers
- **Edit**: Track changes, comments, accept/reject revisions
- **Convert**: MD/HTML to DOCX, DOCX to PDF

### PPTX Processing

- **Read**: Extract text, speaker notes, slide layouts
- **Write**: Generate slides from templates, add charts/images
- **Edit**: Modify existing presentations, update placeholders
- **Convert**: HTML to PPTX, PPTX to PDF

### PDF Processing

- **Read**: Extract text, tables, metadata, form fields
- **Write**: Generate from HTML/DOCX, create from scratch
- **Edit**: Fill forms, add annotations, watermarks
- **Manipulate**: Merge, split, rotate, encrypt/decrypt

### XLSX Processing

- **Read**: Extract data, formulas, named ranges
- **Write**: Create workbooks with formulas, charts, pivot tables
- **Edit**: Update cells while preserving formatting
- **Calculate**: Recalculate formulas, validate results

---

## Common Patterns

### Template-Based Document Generation

```text
1. Create master template (DOCX/XLSX/PPTX)
   - Define placeholder syntax: {{field_name}}
   - Set up styles and formatting
   - Include conditional sections

2. Prepare data source
   - JSON/CSV with field values
   - Database query results
   - API response data

3. Merge template + data
   - Replace placeholders with values
   - Handle lists/repeating sections
   - Apply conditional logic

4. Generate output
   - Save as original format
   - Convert to PDF for distribution
   - Validate output quality
```

### Batch Document Processing

```text
1. Input validation
   - Check file formats
   - Verify file integrity
   - Log processing start

2. Process each document
   - Extract/transform as needed
   - Apply consistent formatting
   - Generate outputs

3. Output validation
   - Verify file created
   - Check file size > 0
   - Validate content structure

4. Cleanup
   - Archive originals
   - Log completion
   - Report errors
```

### PDF Table Extraction Pipeline

```text
1. Analyze PDF structure
   - Check page count
   - Identify table locations
   - Detect table borders

2. Extract tables
   - Use pdfplumber find_tables()
   - Handle multi-page tables
   - Clean extracted data

3. Post-process data
   - Fix header rows
   - Handle merged cells
   - Convert data types

4. Export results
   - Save to CSV/XLSX
   - Validate row counts
   - Log extraction quality
```

---

## Quality Assurance Checklist

### Pre-Processing

- [ ] Backup original files
- [ ] Validate input file formats
- [ ] Check file permissions
- [ ] Set up temp directory for processing

### During Processing

- [ ] Preserve original formatting where possible
- [ ] Handle encoding issues (UTF-8)
- [ ] Log each operation step
- [ ] Validate intermediate results

### Post-Processing

- [ ] Verify output file exists
- [ ] Check output file size > 0
- [ ] Visual spot-check (for critical documents)
- [ ] Validate formulas calculate correctly (XLSX)
- [ ] Verify form fields filled (PDF)
- [ ] Clean up temp files

---

## Navigation: Core Workflows

- **DOCX workflows** — [resources/docx-workflows.md](resources/docx-workflows.md)
  Extraction, redlining batches, unpack/pack tips, docx-js creation guidance.

- **PPTX workflows** — [resources/pptx-workflows.md](resources/pptx-workflows.md)
  Markdown/HTML conversion, layout analysis, unpack for notes/themes.

- **PDF workflows** — [resources/pdf-workflows.md](resources/pdf-workflows.md)
  pypdf merges/splits, pdfplumber tables, form filling, metadata checks.

- **XLSX workflows** — [resources/xlsx-workflows.md](resources/xlsx-workflows.md)
  Formula-first modeling, color coding, recalc with LibreOffice, QA steps.

---

## Anti-Patterns to Avoid

| Anti-Pattern | Problem | Solution |
|--------------|---------|----------|
| Hardcoding paths | Breaks on different machines | Use relative paths or config |
| Ignoring encoding | Garbled characters in output | Always specify UTF-8 |
| No backup | Lost original on error | Copy original before processing |
| Silent failures | Processing errors go unnoticed | Log and validate each step |
| Formula overwrite | XLSX formulas replaced with values | Use data_only=False |
| Large file in memory | Memory exhaustion | Use streaming/iterative processing |

---

## Related Skills

- [../foundation-documentation/SKILL.md](../foundation-documentation/SKILL.md) — Docs strategy, templates, writing patterns
- [../software-frontend/SKILL.md](../software-frontend/SKILL.md) — HTML/CSS/React sources for slide or PDF generation
- [../software-testing-automation/SKILL.md](../software-testing-automation/SKILL.md) — Automated QA and regression checks for outputs
- [../ops-devops-platform/SKILL.md](../ops-devops-platform/SKILL.md) — CI pipelines for document generation and validation

---

## Usage Notes

- Keep SKILL.md lean; load the specific resource file before acting.
- Prefer resource toolchains over ad-hoc scripts to avoid breaking formats.
- Preserve originals; run conversions in temp paths; verify outputs (visual check for DOCX/PPTX/PDF, zero formula errors for XLSX).
- For legal/business docs, default to tracked changes and minimal edits.
- Always test document processing with representative sample files before batch operations.
