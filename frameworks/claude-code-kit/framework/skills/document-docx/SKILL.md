---
name: document-docx
description: Create, edit, and analyze Microsoft Word documents with tracked changes, formatting, styles, tables, headers/footers, and template-based generation. Supports .docx format using python-docx, mammoth.js, and docx libraries for Node.js and Python workflows.
---

# Document DOCX Skill — Quick Reference

This skill enables creation, editing, and analysis of Word documents programmatically. Claude should apply these patterns when users need to generate reports, contracts, proposals, documentation, or any structured Word documents from data or templates.

---

## Quick Reference

| Task | Tool/Library | Language | When to Use |
|------|--------------|----------|-------------|
| Create DOCX | python-docx | Python | Reports, contracts, proposals |
| Create DOCX | docx | Node.js | Server-side document generation |
| Convert to HTML | mammoth.js | Node.js | Web display, content extraction |
| Parse DOCX | python-docx | Python | Extract text, tables, metadata |
| Template fill | docxtpl | Python | Mail merge, template-based generation |
| Track changes | python-docx | Python | Review workflows, redlining |

## When to Use This Skill

Claude should invoke this skill when a user requests:

- Generate Word documents from data or templates
- Create formatted reports with tables, headers, styles
- Extract content from existing DOCX files
- Convert DOCX to HTML or other formats
- Implement mail merge or template filling
- Add tracked changes or comments
- Create document automation workflows

---

## Core Operations

### Create Document (Python)

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

### Create Document (Node.js)

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

### Template-Based Generation (Python)

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

### Extract Content

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

---

## Document Structure Patterns

### Report Template

```text
REPORT STRUCTURE
├── Title Page (heading level 0, centered)
├── Table of Contents (auto-generated)
├── Executive Summary (heading level 1)
├── Body Sections (heading levels 1-3)
│   ├── Introduction
│   ├── Findings (with tables, charts)
│   └── Recommendations
├── Appendices
└── Footer (page numbers, date)
```

### Contract Template

```text
CONTRACT STRUCTURE
├── Header (parties, date)
├── Recitals (WHEREAS clauses)
├── Definitions
├── Terms and Conditions (numbered sections)
├── Signatures Block
└── Exhibits/Schedules
```

---

## Styling Reference

| Element | Python Method | Node.js Class |
|---------|---------------|---------------|
| Heading 1 | `add_heading(text, 1)` | `HeadingLevel.HEADING_1` |
| Bold | `run.bold = True` | `TextRun({ bold: true })` |
| Italic | `run.italic = True` | `TextRun({ italics: true })` |
| Font size | `run.font.size = Pt(12)` | `TextRun({ size: 24 })` (half-points) |
| Alignment | `WD_ALIGN_PARAGRAPH.CENTER` | `AlignmentType.CENTER` |
| Page break | `doc.add_page_break()` | `new PageBreak()` |

---

## Navigation

**Resources**
- [resources/docx-patterns.md](resources/docx-patterns.md) — Advanced formatting, styles, headers/footers
- [resources/template-workflows.md](resources/template-workflows.md) — Mail merge, batch generation
- [data/sources.json](data/sources.json) — Library documentation links

**Templates**
- [templates/report-template.md](templates/report-template.md) — Standard report structure
- [templates/contract-template.md](templates/contract-template.md) — Legal document structure

**Related Skills**
- [../document-pdf/SKILL.md](../document-pdf/SKILL.md) — PDF generation and conversion
- [../document-docx/SKILL.md](../document-docx/SKILL.md) — Document workflow automation
- [../docs-codebase/SKILL.md](../docs-codebase/SKILL.md) — Technical writing patterns
