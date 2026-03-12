# Tracked Changes in DOCX (OOXML)

## Decision Guide

- If you need a human-friendly redline: generate the revised `.docx` and use Microsoft Word "Compare" to create tracked changes.
- If you need review notes: add comments or highlight runs instead of trying to generate tracked changes.
- If you need to parse tracked changes in an existing `.docx`: inspect OOXML (`word/document.xml`) for tracked-revision tags.
- If you must generate true tracked changes programmatically: prefer dedicated OOXML tooling (docx4j, Open XML SDK) or a commercial library (Aspose.Words).

## What Is Feasible with Common Libraries

- `python-docx`: strong for structure and styling; does not provide a first-class API for tracked changes and may flatten them when editing.
- `docx` (Node.js): good for generation; not designed for tracked changes workflows.
- `mammoth`: best-effort text-first extraction/HTML conversion; not a revision-preserving tool.

## OOXML Markers to Look For

- Tracked revisions in `word/document.xml`:
  - `<w:ins ...>` inserted content
  - `<w:del ...>` deleted content
  - `<w:moveFrom ...>` / `<w:moveTo ...>` moved content
- Comments:
  - Definitions in `word/comments.xml`
  - References in `word/document.xml` via comment range and reference tags

## Quick Inspection (No Dependencies)

- Run: `python scripts/docx_inspect_ooxml.py input.docx --json`
- Use the counts to decide whether to:
  - Avoid editing with high-level libraries, or
  - Move to an OOXML-level approach for this document.

## Safety Notes

- Treat `.docx` as a zip archive; always work on a copy when editing OOXML directly.
- Avoid "string replace" edits in `document.xml` unless you also validate the resulting XML well-formedness.
