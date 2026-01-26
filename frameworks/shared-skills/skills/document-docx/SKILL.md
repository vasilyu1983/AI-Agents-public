---
name: document-docx
description: Create, edit, and analyze Microsoft Word .docx files (reports, contracts, proposals) with styles, tables, headers/footers, template filling, content extraction, and conversion to HTML; support review workflows (comments/highlights) and inspect tracked changes via OOXML when needed using Python/Node.js (python-docx, docxtpl, mammoth.js, docx).
---

# Document DOCX Skill - Quick Reference

This skill enables creation, editing, and analysis of `.docx` files for reports, contracts, proposals, documentation, and template-driven outputs.

Modern best practices (2026):
- Prefer templates + styles over manual formatting.
- Treat `.docx` as the editable source; treat PDF as a release artifact.
- If distributing externally, include basic accessibility hygiene (headings, table headers, alt text).

## Quick Reference

| Task | Tool/Library | Language | When to Use |
|------|--------------|----------|-------------|
| Create DOCX | python-docx | Python | Reports, contracts, proposals |
| Create DOCX | docx | Node.js | Server-side document generation |
| Convert to HTML | mammoth.js | Node.js | Web display, content extraction |
| Parse DOCX | python-docx | Python | Extract text, tables, metadata |
| Template fill | docxtpl | Python | Mail merge, template-based generation |
| Review workflow | Word compare, comments/highlights | Any | Human review without OOXML surgery |
| Tracked changes | OOXML inspection, docx4j/OpenXML SDK/Aspose | Any | True redlines or parsing tracked changes |

## Tool Selection

- Prefer `docxtpl` when non-developers must edit layout/design in Word.
- Prefer `python-docx` for structural edits (paragraphs/tables/headers/footers) when formatting complexity is moderate.
- Prefer `docx` (Node.js) for server-side generation in TypeScript-heavy stacks.
- Prefer `mammoth` for text-first extraction or DOCX-to-HTML (best effort; may drop some layout fidelity).

## Known Limits (Plan Around These)

- `.doc` (legacy) is not supported by these libraries; convert to `.docx` first (e.g., LibreOffice).
- `python-docx` cannot reliably create true tracked changes; use Word compare or specialized OOXML tooling.
- Tables of Contents and many fields are placeholders until opened/updated in Word.

## Core Operations

### Create Document (Python - python-docx)

```python
from docx import Document
from docx.shared import Inches, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH

doc = Document()

# Title
title = doc.add_heading('Document Title', 0)
title.alignment = WD_ALIGN_PARAGRAPH.CENTER

# Paragraph with formatting
para = doc.add_paragraph()
run = para.add_run('Bold and ')
run.bold = True
run = para.add_run('italic text.')
run.italic = True

# Table
table = doc.add_table(rows=3, cols=3)
table.style = 'Table Grid'
for i, row in enumerate(table.rows):
    for j, cell in enumerate(row.cells):
        cell.text = f'Row {i+1}, Col {j+1}'

# Image
doc.add_picture('image.png', width=Inches(4))

# Save
doc.save('output.docx')
```

### Create Document (Node.js - docx)

```typescript
import { Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell } from 'docx';
import * as fs from 'fs';

const doc = new Document({
  sections: [{
    properties: {},
    children: [
      new Paragraph({
        children: [
          new TextRun({ text: 'Bold text', bold: true }),
          new TextRun({ text: ' and normal text.' }),
        ],
      }),
      new Table({
        rows: [
          new TableRow({
            children: [
              new TableCell({ children: [new Paragraph('Cell 1')] }),
              new TableCell({ children: [new Paragraph('Cell 2')] }),
            ],
          }),
        ],
      }),
    ],
  }],
});

Packer.toBuffer(doc).then((buffer) => {
  fs.writeFileSync('output.docx', buffer);
});
```

### Template-Based Generation (Python - docxtpl)

```python
from docxtpl import DocxTemplate

doc = DocxTemplate('template.docx')
context = {
    'company_name': 'Acme Corp',
    'date': '2025-01-15',
    'items': [
        {'name': 'Widget A', 'price': 100},
        {'name': 'Widget B', 'price': 200},
    ]
}
doc.render(context)
doc.save('filled_template.docx')
```

### Extract Content (Python - python-docx)

```python
from docx import Document

doc = Document('input.docx')

# Extract all text
full_text = []
for para in doc.paragraphs:
    full_text.append(para.text)

# Extract tables
for table in doc.tables:
    for row in table.rows:
        row_data = [cell.text for cell in row.cells]
        print(row_data)
```

## Styling Reference

| Element | Python Method | Node.js Class |
|---------|---------------|---------------|
| Heading 1 | `add_heading(text, 1)` | `HeadingLevel.HEADING_1` |
| Bold | `run.bold = True` | `TextRun({ bold: true })` |
| Italic | `run.italic = True` | `TextRun({ italics: true })` |
| Font size | `run.font.size = Pt(12)` | `TextRun({ size: 24 })` (half-points) |
| Alignment | `WD_ALIGN_PARAGRAPH.CENTER` | `AlignmentType.CENTER` |
| Page break | `doc.add_page_break()` | `new PageBreak()` |

## Do / Avoid (Dec 2025)

### Do

- Use consistent heading levels and a table of contents for long docs.
- Capture decisions and action items with owners and due dates.
- Store docs in a versioned, searchable system.

### Avoid

- Manual formatting instead of styles (breaks consistency).
- Docs with no owner or review cadence (stale quickly).
- Copy/pasting without updating definitions and links.

## Output Quality Checklist

- Structure: consistent heading hierarchy, styles, and (when needed) an auto-generated table of contents.
- Decisions: decisions/actions captured with owner + due date (not buried in prose).
- Versioning: doc ID + version + change summary; review cadence defined.
- Accessibility hygiene: headings/reading order are correct; table headers are marked; alt text for non-decorative images.
- Reuse: use `assets/doc-template-pack.md` for decision logs and recurring doc types.

## Optional: AI / Automation

Use only when explicitly requested and policy-compliant.

- Summarize meeting notes into decisions/actions; humans verify accuracy.
- Draft first-pass docs from outlines; do not invent facts or quotes.

## Navigation

**Resources**
- [references/docx-patterns.md](references/docx-patterns.md) - Advanced formatting, styles, headers/footers
- [references/template-workflows.md](references/template-workflows.md) - Mail merge, batch generation
- [references/tracked-changes.md](references/tracked-changes.md) - Tracked changes: what is feasible, and what is not
- [data/sources.json](data/sources.json) - Library documentation links

**Scripts**
- `scripts/docx_inspect_ooxml.py` - Dependency-free OOXML inspection (including tracked changes signals)
- `scripts/docx_extract.py` - Extract text/tables to JSON (requires `python-docx`)
- `scripts/docx_render_template.py` - Render a `docxtpl` template (requires `docxtpl`)
- `scripts/docx_to_html.mjs` - Convert `.docx` to HTML (requires `mammoth`)

**Templates**
- [assets/report-template.md](assets/report-template.md) - Standard report structure
- [assets/contract-template.md](assets/contract-template.md) - Legal document structure
- [assets/doc-template-pack.md](assets/doc-template-pack.md) - Decision log, meeting notes, changelog templates

**Related Skills**
- [../document-pdf/SKILL.md](../document-pdf/SKILL.md) - PDF generation and conversion
- [../docs-codebase/SKILL.md](../docs-codebase/SKILL.md) - Technical writing patterns
