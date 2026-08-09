# Tracked Changes In DOCX (OOXML)

Use this when the request is specifically about insertions/deletions/moves as revision history rather than comments.

## Decision Guide

- If you need a human-friendly redline, create the revised `.docx` and use Microsoft Word Compare.
- If you need review notes rather than revisions, use comments instead. See [review-comments-workflows.md](review-comments-workflows.md).
- If you need to inspect whether a document already contains revisions, inspect the OOXML before editing.
- If you must author tracked changes programmatically, move to OOXML-specialized tooling such as Open XML SDK, docx4j, or a commercial library.

## What Common Libraries Can And Cannot Do

- `python-docx`: good for structure, styles, and comments; not a tracked-changes authoring library.
- `docx` (Node.js): good for document generation; not a tracked-changes workflow tool.
- `mammoth`: extraction/conversion tool only; not revision-preserving.

## OOXML Signals To Look For

Tracked revisions in `word/document.xml` typically appear as:
- `<w:ins ...>` for inserted content
- `<w:del ...>` for deleted content
- `<w:moveFrom ...>` / `<w:moveTo ...>` for moved content

Review-related companion files may include:
- `word/comments.xml`
- `word/commentsExtended.xml`
- `word/people.xml`

## Quick Inspection

```bash
python3 scripts/docx_inspect_ooxml.py input.docx --json
```

Use the counts to decide whether to:
- Avoid editing with high-level libraries, or
- Promote the task to an OOXML-level workflow.

## Safety Notes

- Treat `.docx` as a zip archive and keep a clean original copy.
- Do not do blind string replacement inside `document.xml`.
- Inspect first if the document is review-heavy or legal/editorial in nature.

## Related Resources

- [review-comments-workflows.md](review-comments-workflows.md) - Comments and Word Compare workflows
- [llm-extraction-workflows.md](llm-extraction-workflows.md) - Extraction limits when review metadata exists
- [SKILL.md](../SKILL.md) - Parent DOCX skill
