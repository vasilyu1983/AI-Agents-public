---
name: document-docx
description: "Builds docxtpl templates, DOCX extraction for RAG, and EAA accessibility checks. Use when templating Word or extracting tables; plain edits and redlines: official docx skill."
allowed-tools: Bash, Read, Write, Glob, Grep
compatibility: Claude Code + Codex. Uses runtime-specific allowed-tools / argument-hint fields.
version: "1.2"
last_validated: 2026-07-11
---

# Document DOCX Skill - Quick Reference

This skill covers the specialist `.docx` lanes: docxtpl template pipelines, python-docx structural edits and extraction, LLM/RAG ingestion, and accessibility/EAA compliance.

**Boundary:** when the official Anthropic `docx` skill is available, prefer it for plain create/edit (docx-js), tracked-change (redline) authoring via `<w:ins>`/`<w:del>` with `validate.py`, and comment authoring. When the user asks for "a document" without naming a format and a document connector or artifact type is available, prefer that over generating a `.docx`.

## Core Decision Rules

- Non-developers own the layout in Word, and code supplies data: `docxtpl`. Code decides the structure: `python-docx` (Python) or `docx` (Node).
- Render templates fail-closed. docxtpl's defaults render a missing variable as blank and insert `&`/`<` unescaped, so the file opens fine and passes a tag scan. Use `scripts/docx_render_template.py` (StrictUndefined + autoescape); see [references/template-workflows.md](references/template-workflows.md).
- Tracked changes: never promise high-level library support, and never fake redlines with colour or strikethrough. Route authoring to the official `docx` skill's OOXML workflow. See [references/tracked-changes.md](references/tracked-changes.md).
- Semantic HTML from a trusted file: `mammoth`, then sanitise (it does no sanitisation). Markdown/JSON for RAG: a Markdown converter or `scripts/docx_extract.py`; see [references/llm-extraction-workflows.md](references/llm-extraction-workflows.md).
- DOCX feeding a KB or index: tables inside content controls are silently missing from `Document.tables`, tables pasted as images have no text, tracked changes need an explicit accept/original policy, and filenames can lie. Run the table-count detection check in [references/docx-extraction-failure-modes.md](references/docx-extraction-failure-modes.md) before indexing any file (load it whenever DOCX is ingestion input).
- PDF output: Word automation for the highest fidelity; LibreOffice headless for CI and batch.
- `.doc`: convert to `.docx` first. `.docm`/`.dotm`: treat the macros as untrusted and never execute them.
- `.docx` is the editable source; PDF is the release artifact.

## Quick Reference

| Task | Tool | When |
|------|------|------|
| Template fill, mail merge | `docxtpl` + `scripts/docx_render_template.py` | Word-authored templates, batch documents |
| Structural edits in Python | `python-docx` ([references/docx-patterns.md](references/docx-patterns.md)) | Styles, tables, sections, fields, hyperlinks |
| Comments | `python-docx` `add_comment` (version-gated) or the official `docx` skill | Review notes without revisions |
| DOCX to HTML | `mammoth` via `scripts/docx_to_html.mjs` | Trusted documents, semantic HTML |
| DOCX to JSON/Markdown | `scripts/docx_extract.py`, Markdown converters | Automation, RAG ingestion |
| Inspect revisions/comments | `scripts/docx_inspect_ooxml.py` | Before editing any reviewed document |
| Release gate | `scripts/docx_quality_gate.py` | Every generated or edited file |
| DOCX to PDF | Word automation / LibreOffice headless | Release artifacts, CI smoke tests |

## Format And Safety Caveats

- python-docx comments: main body only, no anchors in headers or footers, no threaded replies or resolved state, and anchors are whole runs.
- python-docx has no tracked-change authoring, no alt-text property, no field API and no public hyperlink authoring API. The workarounds in the references use private attributes; re-verify them after upgrades.
- A TOC and other Word fields stay empty or stale until updated in Word or rendered by LibreOffice.
- New python-docx documents can inherit author, date and comments from the default template. Inspect core properties before distribution.

## Version-Gate Before Promising A Feature

Do not assume the environment has a current library:

- `Document.add_comment()` is a recent python-docx addition and raises `AttributeError` on older pins. Check `hasattr(docx.document.Document, "add_comment")` before promising comment support.
- If a user asks for something flagged unsupported here (tracked-change authoring in python-docx, threaded replies, resolved comments), say so plainly and route to the official `docx` skill. Do not approximate it with formatting.

## Default Workflow

1. Identify the file type and trust level: `.docx`/`.dotx`, `.docm`/`.dotm`, or legacy `.doc`.
2. If the document may carry review metadata, run `scripts/docx_inspect_ooxml.py --json` first.
3. Generate or modify: docxtpl through `docx_render_template.py`, or python-docx/docx for structure.
4. For a newly generated output, set `doc.core_properties` to the intended author, clear template comments, and set `created`/`modified` to `datetime.now(timezone.utc).replace(tzinfo=None)` (python-docx expects naive UTC). For edits to an existing file, preserve provenance unless the user requested a metadata reset.
5. Run `scripts/docx_quality_gate.py`. It exits 2 on any issue, including a requested `--check-libreoffice` that could not run.
6. Render to images and look at every page before shipping: `soffice --headless --convert-to pdf out.docx && pdftoppm -png -r 80 out.pdf page`, then open the `page-*.png` files. For external distribution, also check in Word and apply the accessibility checklist.

```bash
python3 scripts/docx_render_template.py template.docx context.json out.docx   # exit 2 on missing vars
python3 scripts/docx_quality_gate.py out.docx --json                          # exit 2 on any issue
python3 scripts/docx_extract.py in.docx --include headers footers comments --out extracted.json
node scripts/docx_to_html.mjs in.docx out.html --style-map map.txt --extract-images-dir assets/
```

## Round-Trip Release Proof

- Capture the expected counts of sections, tables, images, hyperlinks, comments and tracked changes before the final save.
- Reopen the saved DOCX and compare the counts.
- Render a copy and inspect page breaks, numbering, table overflow, missing fonts and unresolved tags.

A successful OOXML parse or text extraction does not prove layout fidelity. A visually correct PDF does not prove that comments, hyperlinks, fields or accessibility metadata survived in the editable DOCX. Record which viewer did the primary review and which secondary viewer was checked.

## Navigation

**Resources**
- [references/docx-patterns.md](references/docx-patterns.md) - python-docx gotchas: styles, tables, sections, fields, hyperlinks, corruption pitfalls
- [references/template-workflows.md](references/template-workflows.md) - docxtpl tag placement, fail-closed rendering, batch rules
- [references/review-comments-workflows.md](references/review-comments-workflows.md) - Comments, review notes, programmatic redline routing, comment limits
- [references/tracked-changes.md](references/tracked-changes.md) - What is and is not feasible for tracked revisions
- [references/llm-extraction-workflows.md](references/llm-extraction-workflows.md) - Mammoth, MarkItDown, Docling, HTML/Markdown/JSON extraction; includes [Extraction Stack](references/llm-extraction-workflows.md#extraction-stack) tool candidates by job (native parse, structured converter, OCR)
- [references/docx-extraction-failure-modes.md](references/docx-extraction-failure-modes.md) - Silent-loss modes for KB/RAG ingestion (content-control tables, image tables, revisions, lying filenames) and the table-count detection check
- [references/accessibility-compliance.md](references/accessibility-compliance.md) - Word accessibility, EN 301 549 context, manual checks
- [references/cross-platform-compatibility.md](references/cross-platform-compatibility.md) - Word, Google Docs, LibreOffice, PDF conversion
- [references/document-automation-pipelines.md](references/document-automation-pipelines.md) - CI/CD, batch generation, quality gates
- [data/sources.json](data/sources.json) - External documentation links

**Scripts**
- `scripts/docx_inspect_ooxml.py` - Dependency-free OOXML inspection for tracked changes and comments
- `scripts/docx_extract.py` - Extract text, tables, metadata, and optional headers/footers/hyperlinks/comments/images to JSON
- `scripts/docx_render_template.py` - Render a `docxtpl` template from JSON, failing on missing variables (`--allow-missing` for drafts)
- `scripts/docx_to_html.mjs` - Convert trusted `.docx` to HTML with style maps and optional image extraction
- `scripts/docx_quality_gate.py` - Validate parseability, unresolved template tags, tracked-change/comment signals, and optional LibreOffice conversion; exits 2 on any issue

**Templates**
- [assets/docx-template-authoring-checklist.md](assets/docx-template-authoring-checklist.md) - Template authoring and handoff checklist

**Related Skills**
- [../document-pdf/SKILL.md](../document-pdf/SKILL.md) - PDF generation and release workflows
- [../document-xlsx/SKILL.md](../document-xlsx/SKILL.md) - Spreadsheet generation and exports
- [../document-pptx/SKILL.md](../document-pptx/SKILL.md) - Presentation generation
- [../docs-codebase/SKILL.md](../docs-codebase/SKILL.md) - Technical writing patterns

## Learnings Loop

When prior decisions or pitfalls are relevant, consult `learnings.consolidated.md` if present; use `learnings.md` only for needed history or as the available fallback. Otherwise skip both.

After applying it, if you encountered a pattern worth remembering, a mistake worth preventing, or a domain fact that surprised you, append one dated bullet to `learnings.md` via `agents-skills-feedback-loop/scripts/append_learning.py`. Do not modify `SKILL.md` itself.
