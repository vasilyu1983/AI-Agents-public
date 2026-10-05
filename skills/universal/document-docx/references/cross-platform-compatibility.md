# Cross-Platform DOCX Compatibility

Use this when a DOCX must survive handoff across Word, Google Docs and LibreOffice, or through a PDF conversion pipeline.

## Rendering Differences

Use Word desktop as the reference when a file has complex layout or review markup. In the recipient's editor, inspect tables, floating images, numbering, content controls, comments and tracked changes; these can render or round-trip differently. Do not use a conversion through another editor as the sole copy of the reviewed original.

**Portable subset** for files that must stay editable outside Word: built-in heading styles, simple tables without merges or nesting, inline images, text-and-page-number headers and footers, single-level lists, explicit page breaks, descriptive hyperlinks.

## Fonts And Numbering

- A missing font changes line wraps, page count and sometimes list indentation. Before promising page-exact output, confirm the fonts are installed on every renderer, including the CI image. `pdffonts out.pdf` shows what was actually embedded or substituted.
- Keep numbering simple. Custom multi-level numbering is the most fragile feature outside Word.
- If recipients only read, send PDF and keep the DOCX as the editable source.

## Testing Strategy

1. Word desktop is the baseline.
2. Open the file in the recipient's secondary viewer (Google Docs or LibreOffice). Check tables, numbering, comments, image placement and page count.
3. For PDF output, compare the PDF against the Word baseline page by page, as rendered images rather than extracted text.
4. Re-test after any structural template or style change.

Headless smoke test for CI: `docx_quality_gate.py --check-libreoffice`. It fails when LibreOffice is absent rather than skipping silently. A successful conversion proves the file opens; it does not prove layout fidelity.

## Conversion

| Method | Fidelity | Platform | Notes |
|--------|----------|----------|-------|
| Word automation (COM / AppleScript) | Highest | Windows / macOS with Word | Use for final release PDFs of Word-specific layouts |
| `docx2pdf` | High | Windows / macOS with Word | Wraps Word; does not work on Linux |
| LibreOffice headless (`soffice --headless --convert-to pdf`) | Good | Cross-platform | Default for CI and batch. Expect some layout drift. |
| `mammoth` (DOCX to HTML) | Text-first | Cross-platform | Semantic extraction, not layout |

LibreOffice headless serialises on a shared user profile. For parallel batch conversion, give each worker its own `-env:UserInstallation=file:///tmp/lo-<n>`, or run the conversions sequentially.

## Related Resources

- [docx-patterns.md](docx-patterns.md) - python-docx gotchas
- [review-comments-workflows.md](review-comments-workflows.md) - Comments and redline routing
- [accessibility-compliance.md](accessibility-compliance.md) - DOCX accessibility
- [document-automation-pipelines.md](document-automation-pipelines.md) - Batch generation and quality gates
