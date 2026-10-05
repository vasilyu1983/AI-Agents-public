# Tracked Changes In DOCX (OOXML)

Use this when the request is about insertions, deletions and moves as revision history, not comments.

## Decision Guide

- **Authoring redlines:** use the official `docx` skill's OOXML redlining workflow. It authors `<w:ins>`/`<w:del>` with `w:author`/`w:date`, then runs `validate.py --original --author` to prove every edit is tracked. An agent cannot run Word Compare headless. "Use Word Compare" is only useful to a human who has Word.
- **Review notes, not revisions:** use comments. See [review-comments-workflows.md](review-comments-workflows.md).
- **Existing document that may contain revisions:** inspect before editing (below). python-docx, the `docx` npm package and mammoth have no tracked-change authoring. Editing a revision-heavy file through them can silently flatten or mix the revision history.
- **Never fake a redline** with coloured or struck-through text. It carries no revision metadata and fails any real legal or editorial review.

## OOXML Signals

- In `word/document.xml`: `<w:ins>`, `<w:del>` (deleted text sits in `<w:delText>`), and `<w:moveFrom>`/`<w:moveTo>`.
- `<w:trackRevisions/>` in `word/settings.xml` means track changes is switched on. Any edit a human makes next will be tracked.
- Review companions: `word/comments.xml`, `word/commentsExtended.xml`, `word/people.xml`.

## Quick Inspection

```bash
python3 scripts/docx_inspect_ooxml.py input.docx --json
```

Non-zero `w:ins`/`w:del`/`w:moveFrom` counts: do not edit with a high-level library. Route the task to the OOXML workflow. Keep a clean original, and never string-replace inside `document.xml`.

## Related Resources

- [review-comments-workflows.md](review-comments-workflows.md) - Comments and redline routing
- [llm-extraction-workflows.md](llm-extraction-workflows.md) - What extraction does with revisions
- [SKILL.md](../SKILL.md) - Parent DOCX skill
