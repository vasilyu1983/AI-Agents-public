# Document Automation Pipelines

CI and batch automation around DOCX generation: pipeline shape, quality gates, failure handling. For docxtpl rendering rules, see [template-workflows.md](template-workflows.md).

## Quality Gates

Run on every generated file:

```bash
python3 scripts/docx_quality_gate.py output.docx --json            # exit 2 on any issue
python3 scripts/docx_quality_gate.py output.docx --check-libreoffice  # also fails if LibreOffice is absent
```

The gate checks the package, document XML and unresolved template tags in Word XML parts; it reports review markup separately. Run the template renderer first to catch missing variables that otherwise become blanks.

What the gate cannot see, and how to cover it:

| Blind spot | Cover it with |
|------------|---------------|
| Layout breakage (overflowing tables, orphaned headings, empty TOC) | Render a sample to PNG and look at it (SKILL.md Default Workflow, step 6) |
| Wrong data in the right place | Control totals or spot checks against the source records |
| Leaked metadata (`author="python-docx"`) | Reset `core_properties` in the renderer; check with `docx_extract.py` |

## Failure Handling

| Error | Cause | Fix |
|-------|-------|-----|
| `Render failed: Template variables missing from context` | Record lacks a field | Fix the data, or send `""` for an intentional blank. Never switch to `--allow-missing` in production. |
| `jinja2.exceptions.UndefinedError` | Nested attribute missing (`item.price`) under StrictUndefined | Fix the record shape; the top-level pre-check cannot see nested keys |
| `TemplateSyntaxError` | Mistyped or unbalanced tag in the Word template | Fix the template; check `{%tr %}`/`{%p %}` placement |
| Word repair prompt on open | Raw OXML post-processing in the wrong element order | See [docx-patterns.md](docx-patterns.md), Corruption Pitfalls |
| Review metadata lost | High-level library edited a document with revisions | Inspect OOXML first (`docx_inspect_ooxml.py`); route redlines to the official `docx` skill |
| Font substitution in PDF | CI image lacks the template's fonts | Install the fonts in the image; check with `pdffonts` |

Batch runs must exit non-zero if any record failed. Write a manifest (record id, output path, gate result) so a partial run is visible and can be resumed.

## Related Resources

- [template-workflows.md](template-workflows.md) - docxtpl tags, fail-closed rendering, batch rules
- [cross-platform-compatibility.md](cross-platform-compatibility.md) - Rendering and conversion
- [accessibility-compliance.md](accessibility-compliance.md) - Accessible output
- [../assets/docx-template-authoring-checklist.md](../assets/docx-template-authoring-checklist.md) - Template handoff checklist
