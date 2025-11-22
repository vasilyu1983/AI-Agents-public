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

---

## Quick Reference

| Task | Format | Tooling | When to Use |
|------|--------|---------|-------------|
| Draft/review doc | DOCX | pandoc (read), OOXML unpack/pack, docx-js (new docs) | Redlines, comments, legal/academic edits |
| Generate slides | PPTX | html2pptx flow, OOXML unpack | Build decks from HTML or adjust layouts/notes |
| Extract/transform | PDF | pypdf, pdfplumber | Text/table extraction, merges/splits, metadata |
| Fill forms | PDF | pdf form workflows | AcroForm filling and output validation |
| Recalc/cleanup | XLSX | LibreOffice `recalc.py` | Refresh formulas, clear errors, preserve formats |
| Build models | XLSX | openpyxl/xlsxwriter (formulas), color rules | Dynamic financial/ops models with standards |

---

## Decision Tree: Picking a Workflow

Need to read only? → Use format-specific extraction (pandoc for DOCX, markitdown/html2pptx preview for PPTX, pdfplumber for PDF, pandas for XLSX).  
Need tracked edits? → DOCX redlining workflow (unpack, minimal `<w:ins>/<w:del>`, pack).  
Need new doc/deck? → Use docx-js for DOCX creation; html2pptx pipeline for PPTX.  
Need tables from PDF? → pdfplumber with page iteration; export to CSV/XLSX.  
Need formulas preserved? → Write Excel formulas, avoid hardcoding; run recalc script.  
Unsure? → Start with Quick Reference, then open the matching resource below.

---

## Navigation: Core Workflows

- **DOCX workflows** — [`resources/docx-workflows.md`](resources/docx-workflows.md)  
  Extraction, redlining batches, unpack/pack tips, docx-js creation guidance.

- **PPTX workflows** — [`resources/pptx-workflows.md`](resources/pptx-workflows.md)  
  Markdown/HTML conversion, layout analysis, unpack for notes/themes.

- **PDF workflows** — [`resources/pdf-workflows.md`](resources/pdf-workflows.md)  
  pypdf merges/splits, pdfplumber tables, form filling, metadata checks.

- **XLSX workflows** — [`resources/xlsx-workflows.md`](resources/xlsx-workflows.md)  
  Formula-first modeling, color coding, recalc with LibreOffice, QA steps.

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
