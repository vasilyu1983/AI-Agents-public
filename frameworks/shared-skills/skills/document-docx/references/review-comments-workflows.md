# Review And Comments Workflows For DOCX

Use this when the task is document review rather than pure document generation.

## Decision Guide

| Need | Preferred Workflow | Why |
|------|--------------------|-----|
| Reviewer notes on specific text | Word comments / `python-docx` comments | Lightweight and readable |
| Human-friendly redline between versions | Microsoft Word Compare | Best tracked-change output for review |
| Programmatic inspection of existing review markup | OOXML inspection + extraction | Avoids flattening review metadata |
| True tracked-change authoring in code | OOXML-specialized tooling | High-level libraries are not built for this |

## Comments vs Tracked Changes

Use comments when:
- The reviewer is giving notes or questions
- You do not need redline semantics
- The document will stay in a collaborative review loop

Use tracked changes / Word Compare when:
- The reviewer needs visible insertions/deletions
- Legal or editorial review expects real redlines
- Two versions of the document already exist

Do not confuse the two:
- Comments are annotations
- Tracked changes are revision history

## `python-docx` Comment Support

`python-docx` supports adding and reading comments in the main document body from version 1.2.0 onward, which is enough for many review-note workflows.

Known limits:
- Not a substitute for tracked changes
- Not suitable for comment anchors in headers/footers
- Not a threaded review system with reply/resolve semantics
- A comment can only be anchored on an even run boundary — the referenced text must be a whole number of consecutive runs, not an arbitrary character offset inside one

Before relying on `add_comment`, confirm the version: `python -c "import docx; print(docx.__version__)"`. On an older pinned install (pre-1.2.0) the method does not exist and raises `AttributeError` rather than degrading gracefully — do not promise comment support to the user without checking first.

Example:

```python
from docx import Document

doc = Document()
paragraph = doc.add_paragraph("This paragraph needs review.")
doc.add_comment(
    runs=paragraph.runs,
    text="Clarify the customer obligation here.",
    author="Legal",
    initials="LG",
)
doc.save("reviewable.docx")
```

## Parse Existing Comments And Revision Signals

Inspect the document before editing if review metadata may matter.

```bash
python3 scripts/docx_inspect_ooxml.py input.docx --json
python3 scripts/docx_extract.py input.docx --include comments hyperlinks --out extracted.json
```

Why inspect first:
- High-level libraries can flatten or normalize revision-heavy documents.
- Existing comments/tracked changes may change the editing strategy.

## Word Compare Workflow

Recommended workflow for true redlines:

1. Generate or edit the revised `.docx`.
2. Keep the original `.docx` unchanged.
3. Open both in Word and run Compare.
4. Save the compared document as the review artifact.

This is still the most reliable route for human-readable tracked changes.

## Practical Do / Avoid

| Do | Avoid |
|----|-------|
| Use comments for notes/questions | Pretending comments are tracked changes |
| Inspect revision-heavy DOCX before editing | Blindly editing review-heavy files with high-level libraries |
| Use Word Compare for real redlines | Trying to synthesize tracked changes with string replacement |
| Keep original and revised files separate | Overwriting the baseline before comparison |

## Related Resources

- [tracked-changes.md](tracked-changes.md) - What is feasible for tracked revisions
- [llm-extraction-workflows.md](llm-extraction-workflows.md) - Extraction workflows when review metadata exists
- [cross-platform-compatibility.md](cross-platform-compatibility.md) - Viewer behavior outside Word
- [SKILL.md](../SKILL.md) - Parent DOCX skill
