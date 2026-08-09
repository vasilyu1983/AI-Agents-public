---
name: document-docx
description: "Create/edit .docx files with styles, templates, comments, and extraction workflows. Use when asked to generate Word reports, contracts, proposals, or convert Word content."
allowed-tools: Bash, Read, Write, Glob, Grep
compatibility: Claude Code + Codex. Uses runtime-specific allowed-tools / argument-hint fields.
version: "1.1"
last_validated: 2026-07-11
---

# Document DOCX Skill - Quick Reference

This skill covers creation, editing, review, extraction, and release workflows for `.docx` documents.

Modern best practices (Jul 2026):
- Treat `.docx` as the editable source and PDF as a release artifact.
- Prefer templates and built-in styles over manual formatting.
- Use comments for review notes; use Word Compare for true redlines.
- For LLM/RAG extraction, optimize for structure, trust level, and sanitization rather than visual fidelity.
- Treat macro-enabled Office files (`.docm`, `.dotm`) as untrusted by default.
- Before promising a feature (comments, alt text, tracked changes), check the installed library version — several of these APIs are recent additions and silently absent on older pins. See "Version-Gate Before Promising A Feature" below.

## Core Decision Rules (2026)

- If non-developers need to own layout/design, prefer `docxtpl` with a Word-authored template.
- If the stack is Python and edits are structural, prefer `python-docx`.
- If the stack is TypeScript/Node and the output is generated server-side, prefer `docx`.
- If you need semantic HTML from a trusted document, prefer `mammoth`, then sanitize before rendering or storing the output.
- If you need Markdown/JSON for search, indexing, or RAG, prefer `MarkItDown` or `Docling`.
- If the user asks for tracked changes, do not promise high-level library support. Generate a revised `.docx` and use Word Compare, or switch to OOXML-specialized tooling.
- If the user asks for PDF output, prefer Word automation for highest fidelity and LibreOffice headless for cross-platform batch workflows.
- If the input is `.doc`, convert to `.docx` first. If it is `.docm` or `.dotm`, do not trust embedded macros.

## Quick Reference

| Task | Tool/Library | Language | When to Use |
|------|--------------|----------|-------------|
| Create/edit DOCX | `python-docx` | Python | Structural edits, reports, contracts, section/table/image work |
| Create/edit DOCX | `docx` | Node.js | Server-side generation in TypeScript-heavy stacks |
| Template fill | `docxtpl` | Python | Word-authored templates, mail merge, batch documents |
| Add/access comments | `python-docx` + Word review workflow | Python / Word | Review notes without tracked revisions |
| Convert DOCX to HTML | `mammoth` | Node.js | Semantic HTML from trusted documents |
| Convert DOCX to Markdown | `MarkItDown` | Python | LLM/RAG ingestion where Markdown is preferred |
| Convert DOCX to Markdown/HTML/JSON | `Docling` | Python / CLI | Multi-format ingestion, structured extraction, batch conversion |
| Parse text/tables/metadata | `python-docx` + OOXML inspection | Python | Extraction, audits, migration tooling |
| Parse tracked changes/comments | OOXML, Open XML SDK, docx4j, Aspose.Words | Python / .NET / Java | Revision-heavy workflows and interoperability edge cases |
| Convert DOCX to PDF | Word automation / LibreOffice headless | OS tooling | Release artifacts and cross-platform smoke checks |

## Selection Guide

- Prefer `docxtpl` when a legal, ops, or business user needs to maintain the template in Word.
- Prefer `python-docx` for moderate formatting complexity where you control the document structure in code.
- Prefer `docx` when the surrounding service and tests already live in Node.js.
- Prefer `mammoth` for trusted, text-first conversion to HTML; it is not a fidelity-preserving renderer.
- Prefer `MarkItDown` for simple DOCX-to-Markdown pipelines.
- Prefer `Docling` when DOCX is only one input among many formats or you need HTML/JSON/Markdown/text output from a unified pipeline.

## ASCII Flow

```text
DOCX request
  |
  v
Classify file + trust level
  |-- .docx / .dotx -----> normal OOXML workflow
  |-- .doc -------------> convert to .docx first
  |-- .docm / .dotm ----> treat macros as untrusted
  |
  v
Choose lane
  |-- Word-owned template ------> docxtpl
  |-- Python structural edit ---> python-docx
  |-- Node service generation --> docx
  |-- trusted HTML conversion --> mammoth + sanitizer
  |-- Markdown / JSON ingest ---> MarkItDown or Docling
  |-- tracked-change review ----> revised DOCX + Word Compare
  |
  v
Generate, edit, or extract
  |
  v
Quality gate
  |-- parseability + unresolved tags ---> scripts/docx_quality_gate.py
  |-- comments / revisions / OOXML ----> scripts/docx_inspect_ooxml.py
  |
  v
Viewer, accessibility, and release checks
```

## Format And Safety Caveats

- `.docx` and `.dotx` are Office Open XML packages; `.doc` is legacy binary and needs conversion first.
- `.docm` and `.dotm` are macro-enabled; do not treat them as safe content inputs.
- `python-docx` can add and read comments in the main document body, but not threaded replies/resolved states, and not comment anchors in headers/footers.
- `python-docx` does not provide reliable tracked-change authoring.
- `mammoth` performs no sanitization of generated HTML or links from untrusted source documents.
- Tables of contents and many Word fields are placeholders until updated in Word.

## Version-Gate Before Promising A Feature

Do not assume the environment has a current library. This is the single most common way this skill causes a confident-but-wrong answer:

- `Document.add_comment()` only exists from `python-docx` 1.2.0 onward. On an older pinned version it raises `AttributeError`, not a graceful fallback. Check first: `python -c "import docx; print(docx.__version__)"`.
- python-docx still has no public high-level property for image alt text (no `.alt_text` on `InlineShape`) as of the current 1.x line — `InlineShape` only documents `height`, `width`, and `type`. The OOXML workaround in `references/accessibility-compliance.md` reaches into the private `_inline` attribute; treat that as an implementation detail that can move between releases, re-verify after any python-docx upgrade, and prefer `python-docx`'s own comment/style APIs wherever a public one exists instead of private attributes.
- If a user asks for a feature this skill flags as unsupported (tracked-change authoring, threaded comment replies, resolved-state comments), say so plainly rather than approximating it with formatting hacks — a document that merely *looks* right (e.g., colored/struck-through text standing in for `<w:ins>`/`<w:del>`) will fail any real redline/legal review because it carries no revision metadata.

## Default Workflow

1. Identify the file type and trust level: `.docx`/`.dotx` vs `.docm`/`.dotm` vs legacy `.doc`.
2. Pick the lane:
   - Template generation -> `docxtpl`
   - Programmatic structure edits -> `python-docx` or `docx`
   - Review/comments -> comments or Word Compare
   - LLM extraction -> `MarkItDown`, `Docling`, or `mammoth`
3. Generate or modify the document.
4. Run `scripts/docx_quality_gate.py` and, when needed, `scripts/docx_inspect_ooxml.py`.
5. If shipping externally, validate rendering in Word plus at least one secondary viewer and apply accessibility hygiene.

## Core Operations

### Create A Document (Python - `python-docx`)

```python
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Inches

doc = Document()

title = doc.add_heading("Quarterly Review", 0)
title.alignment = WD_ALIGN_PARAGRAPH.CENTER

doc.add_paragraph("Executive summary goes here.")

table = doc.add_table(rows=2, cols=2)
table.style = "Table Grid"
table.rows[0].cells[0].text = "Metric"
table.rows[0].cells[1].text = "Value"
table.rows[1].cells[0].text = "Revenue"
table.rows[1].cells[1].text = "$1.2M"

doc.add_picture("chart.png", width=Inches(4.5))
doc.save("quarterly-review.docx")
```

### Add A Review Comment (Python - `python-docx`)

```python
from docx import Document

doc = Document()
paragraph = doc.add_paragraph("This clause needs legal review.")

comment = doc.add_comment(
    runs=paragraph.runs,
    text="Clarify whether this applies to renewals as well.",
    author="Legal",
    initials="LG",
)

comment.paragraphs[0].add_run(" Add the renewal edge case explicitly.").bold = True
doc.save("reviewable.docx")
```

### Fill A Template (Python - `docxtpl`)

```python
from docxtpl import DocxTemplate

doc = DocxTemplate("template.docx")
context = {
    "company_name": "Acme Corp",
    "contract_date": "2026-03-13",
    "items": [
        {"name": "Widget A", "price": 100},
        {"name": "Widget B", "price": 200},
    ],
}
doc.render(context)
doc.save("filled-template.docx")
```

### Convert Trusted DOCX To HTML (Script)

```bash
node scripts/docx_to_html.mjs input.docx output.html --style-map custom-style-map.txt --extract-images-dir output-assets/
```

### Extract Structure For Automation (Script)

```bash
python3 scripts/docx_extract.py input.docx --include headers footers hyperlinks comments images --out extracted.json
```

## Output Quality Checklist

- Structure: heading hierarchy, list styles, and tables are intentional and consistent.
- Reviewability: comments or Word Compare are used for feedback-heavy workflows instead of ad hoc formatting hacks.
- Safety: macro-enabled files are treated as untrusted; HTML generated from DOCX is sanitized before use.
- Portability: fonts, numbering, tables, and images are checked in at least one non-Word viewer when documents are distributed.
- Accessibility hygiene: headings, descriptive links, table headers, document language, and alt text are present where needed.
- Release quality: run `scripts/docx_quality_gate.py` before shipping or batch-publishing.

## Optional: AI / Automation

Use only when explicitly requested and policy-compliant.

- Convert trusted DOCX content into Markdown/HTML/JSON for search or RAG.
- Summarize meeting notes into a Word template, but keep humans accountable for factual accuracy.
- Generate first-pass reports/contracts from structured data, then route through human review.

## Navigation

**Resources**
- [references/docx-patterns.md](references/docx-patterns.md) - Styles, headers/footers, tables, sections, TOC
- [references/template-workflows.md](references/template-workflows.md) - Template authoring, mail merge, batch rendering
- [references/review-comments-workflows.md](references/review-comments-workflows.md) - Comments, review notes, Word Compare, comment limits
- [references/tracked-changes.md](references/tracked-changes.md) - What is and is not feasible for tracked revisions
- [references/llm-extraction-workflows.md](references/llm-extraction-workflows.md) - Mammoth, MarkItDown, Docling, HTML/Markdown/JSON extraction
- [references/accessibility-compliance.md](references/accessibility-compliance.md) - Word accessibility, EN 301 549 context, manual checks
- [references/cross-platform-compatibility.md](references/cross-platform-compatibility.md) - Word, Google Docs, LibreOffice, PDF conversion
- [references/document-automation-pipelines.md](references/document-automation-pipelines.md) - CI/CD, batch generation, quality gates
- [data/sources.json](data/sources.json) - Current external documentation links

**Scripts**
- `scripts/docx_inspect_ooxml.py` - Dependency-free OOXML inspection for tracked changes and comments
- `scripts/docx_extract.py` - Extract text, tables, metadata, and optional headers/footers/hyperlinks/comments/images to JSON
- `scripts/docx_render_template.py` - Render a `docxtpl` template from JSON
- `scripts/docx_to_html.mjs` - Convert trusted `.docx` to HTML with style maps and optional image extraction
- `scripts/docx_quality_gate.py` - Validate parseability, unresolved template tags, tracked-change/comment signals, and optional LibreOffice conversion

**Templates**
- [assets/report-template.md](assets/report-template.md) - Standard report structure
- [assets/contract-template.md](assets/contract-template.md) - Legal document structure
- [assets/doc-template-pack.md](assets/doc-template-pack.md) - Decision log, meeting notes, changelog templates
- [assets/docx-template-authoring-checklist.md](assets/docx-template-authoring-checklist.md) - Template authoring and handoff checklist

**Related Skills**
- [../document-pdf/SKILL.md](../document-pdf/SKILL.md) - PDF generation and release workflows
- [../document-xlsx/SKILL.md](../document-xlsx/SKILL.md) - Spreadsheet generation and exports
- [../document-pptx/SKILL.md](../document-pptx/SKILL.md) - Presentation generation
- [../docs-codebase/SKILL.md](../docs-codebase/SKILL.md) - Technical writing patterns

## Fact-Checking

- Use `data/sources.json` as the starting set of primary sources.
- Use web search/web fetch to verify current external facts, versions, release behavior, regulations, and platform quirks before final answers.
- Prefer primary documentation, package pages, release pages, and official standards pages.
- If web access is unavailable, state the limitation and mark volatile guidance as unverified.

## Learnings Loop

Before applying this skill on a non-trivial task, read `learnings.consolidated.md` in this directory (and `learnings.md` if present).

After applying it, if you encountered a pattern worth remembering, a mistake worth preventing, or a domain fact that surprised you, append one dated bullet to `learnings.md` via `agents-skills-feedback-loop/scripts/append_learning.py`. Do not modify `SKILL.md` itself.

