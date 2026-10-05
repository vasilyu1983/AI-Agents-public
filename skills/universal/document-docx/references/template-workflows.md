# docxtpl Template Workflows

Word-authored templates filled from data: contracts, letters, invoices, mail merge. This lane is unique to this skill; the official `docx` skill does not cover docxtpl.

## When To Use A Template

Use docxtpl when a non-developer (legal, ops, finance) owns the layout in Word and code only supplies data. Use python-docx when code decides the structure, such as a variable number of sections with different layouts. Hybrid: render the docxtpl template first, then post-process with python-docx through `doc.docx` (set only after `render()`) before saving.

## Tag Placement Rules

docxtpl runs Jinja2 over the document XML, so where a tag sits matters as much as its syntax.

| Tag | Scope | Rule |
|-----|-------|------|
| `{{ var }}` | Inline in a run | docxtpl strips run boundaries that Word inserts inside a tag. Apply formatting to the whole tag, not part of it. |
| `{%p if x %}` ... `{%p endif %}` | Whole paragraph | Each `{%p %}` tag must be the only content of its paragraph; the tag paragraph is removed on render. |
| `{%tr for r in rows %}` ... `{%tr endfor %}` | Table row | Put each tag in its own row. The rows holding the tags are removed, and the row between them repeats. |
| `{%tc %}` | Table cell | Column loops. Rarely needed; widths do not adjust automatically. |
| `{%r %}` | Run | Run-level control inside a paragraph. |

- A plain `{% for %}` that spans table rows produces broken XML. Use `{%tr %}`.
- A tag that survives rendering is almost always mistyped (`{ {` or `{{ var }`). `docx_quality_gate.py` flags it.

## Fail-Closed Rendering

docxtpl's defaults fail open. Both of these produce a file that opens fine and passes a tag scan:

1. **Missing variable renders as empty.** Jinja's default `Undefined` prints `""`. No `{{ }}` is left behind for a quality gate to catch, so the contract ships with a blank party name.
2. **XML metacharacters are inserted raw.** Without `autoescape=True`, a value such as `A & B <Ltd>` drops text or corrupts the part.

Use `scripts/docx_render_template.py`; it checks missing variables, renders with `StrictUndefined` and XML escaping, then returns a non-zero exit on failure. `--allow-missing` is only for drafts. Pass `""` for an intentional blank rather than `None`, which may render as text.

After rendering, run `scripts/docx_quality_gate.py` to catch tags that survived because they were mistyped. Then render to images and look at the pages (SKILL.md Default Workflow, step 6).

## Images, Rich Text, Subdocuments

- Build `InlineImage(doc, path, width=Mm(40))` with the same `DocxTemplate` instance that renders it, because the image is added to that document's package. Build a new one for each output.
- `RichText` carries its own formatting. Use `{{r var }}` in the template (note the `r`). A plain `{{ var }}` renders it as nothing, with no error.
- `Subdoc` (`doc.new_subdoc()`) inserts python-docx-built content, such as a variable-length clause list. Use `{{p var }}` for paragraph-level insertion.

## Batch Generation

- Create one `DocxTemplate` per output in batch code. Images and subdocs belong to the package of the instance that created them.
- Pre-validate every record with `get_undeclared_template_variables` before starting so a missing field stops the batch before outputs are written.
- Collect failures per record, and exit non-zero if any failed. A batch that logs errors but exits 0 is a silent partial run.
- Name outputs from a stable id field, never from free text (path traversal, duplicates).

Template authoring handoff: [../assets/docx-template-authoring-checklist.md](../assets/docx-template-authoring-checklist.md).

## Related Resources

- [SKILL.md](../SKILL.md) - Quick reference
- [document-automation-pipelines.md](document-automation-pipelines.md) - CI, quality gates, PDF conversion
- [docx-patterns.md](docx-patterns.md) - python-docx gotchas for post-processing
- [docxtpl documentation](https://docxtpl.readthedocs.io/)
