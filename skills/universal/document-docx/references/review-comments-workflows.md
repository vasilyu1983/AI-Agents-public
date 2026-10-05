# Review And Comments Workflows For DOCX

Use this when the task is document review rather than generation.

## Decision Guide

| Need | Workflow | Why |
|------|----------|-----|
| Reviewer notes on specific text | Comments (python-docx `add_comment`, or the official `docx` skill's comment tooling) | Lightweight and readable |
| Redline between two versions (human with Word) | Word Compare | Best interactive UX; cannot run headless |
| Tracked-change authoring in code | Official `docx` skill: `<w:ins>`/`<w:del>` plus `validate.py --original --author` | High-level libraries cannot do it |
| Inspect existing review markup | `docx_inspect_ooxml.py` plus `docx_extract.py --include comments` | Avoids flattening review metadata |

Comments are annotations; tracked changes are revision history. Legal and editorial reviewers who ask for "changes" usually mean real redlines. Ask before substituting comments.

## python-docx Comments

`Document.add_comment()` is a recent python-docx addition. On an older pinned install it raises `AttributeError` rather than degrading. Check before promising comment support:

```python
import docx
assert hasattr(docx.document.Document, "add_comment"), "python-docx too old for comments; upgrade or use the official docx skill"
```

Limits:
- A comment anchors to whole runs (`runs=[...]`), not to a character offset inside a run. Split the run first if the target is a phrase inside it.
- Main document body only. No anchors in headers or footers.
- No threaded replies and no resolved state.
- Not a substitute for tracked changes.

```python
p = doc.add_paragraph("This clause needs legal review.")
doc.add_comment(runs=p.runs, text="Does this apply to renewals?", author="Legal", initials="LG")
```

## Before Editing A Reviewed Document

```bash
python3 scripts/docx_inspect_ooxml.py input.docx --json
python3 scripts/docx_extract.py input.docx --include comments hyperlinks --out extracted.json
```

Existing comments or revisions change the strategy. High-level libraries can flatten revision-heavy documents. Keep the original and the revised file separate, and never overwrite the baseline before comparison.

## Related Resources

- [tracked-changes.md](tracked-changes.md) - Tracked revisions: signals and routing
- [llm-extraction-workflows.md](llm-extraction-workflows.md) - Extraction when review metadata exists
- [SKILL.md](../SKILL.md) - Parent DOCX skill
