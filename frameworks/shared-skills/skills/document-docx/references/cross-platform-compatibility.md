# Cross-Platform DOCX Compatibility

## Table of Contents

- [Contents](#contents)
- [Rendering Differences](#rendering-differences)
- [Safe Features](#safe-features)
- [Risky Features](#risky-features)
- [Fonts And Numbering](#fonts-and-numbering)
- [Testing Strategy](#testing-strategy)
- [Conversion Best Practices](#conversion-best-practices)
- [Do / Avoid](#do--avoid)
- [Related Resources](#related-resources)

Rendering differences across Microsoft Word, Google Docs, and LibreOffice. Use this when the document must survive handoff across viewers, office suites, or PDF conversion pipelines.

## Contents

- Rendering Differences
- Safe Features
- Risky Features
- Fonts And Numbering
- Testing Strategy
- Conversion Best Practices
- Do / Avoid

---

## Rendering Differences

| Area | Word | Google Docs | LibreOffice |
|------|------|-------------|-------------|
| Headings, bold/italic | Baseline reference | Usually correct, minor spacing drift | Usually correct, font substitution is common |
| Simple tables | Exact | Cell padding and page breaks can shift | Borders and widths can vary |
| Merged / nested tables | Full support | Merged cells can drift; nested tables are fragile | Nested tables often misalign |
| Inline images | Exact | Usually correct | Usually correct |
| Floating images | Full support | Often converted to inline or repositioned | Position may shift |
| SmartArt / advanced drawing objects | Full support | Flattened or missing | Often not rendered faithfully |
| Multi-level numbering | Full support | Can flatten or restart incorrectly | Restart rules often drift |
| Content controls / structured document tags | Full support | Usually flattened to plain content | Partial support |
| Comments / tracked-review metadata | Full support | Review semantics may flatten | Review semantics may flatten |
| Macros / VBA | Supported, subject to Trust Center settings | Removed or ignored | Not supported |

---

## Safe Features

These are the lowest-risk features when a DOCX must remain editable outside Word:

```text
  - Built-in heading styles
  - Bold / italic / underline
  - Paragraph alignment
  - Simple tables with no merges or nesting
  - Inline PNG/JPEG images
  - Simple headers/footers with text and page numbers
  - Descriptive hyperlinks
  - Single-level bullet and numbered lists
  - Page breaks
```

---

## Risky Features

| Feature | Risk | Failure Mode |
|---------|------|--------------|
| Merged table cells | Medium | Alignment drift in Docs/LibreOffice |
| Nested tables | High | Layout breaks or reflows unpredictably |
| Floating images / text wrapping | Medium | Repositioned, inlined, or lost |
| SmartArt / charts with advanced styling | High | Flattened or partially missing |
| Embedded objects (Excel, PDF, Visio) | High | Not interactive or not rendered |
| Content controls / form fields | High | Flattened to plain text or partially lost |
| Macros / VBA | High | Blocked, removed, or unsafe to open |
| Review metadata dependencies | Medium | Comments/tracked changes may not round-trip cleanly |

---

## Fonts And Numbering

Missing fonts change line wraps, page counts, and sometimes list indentation.

```text
Practical rules:
  1. Use widely available fonts such as Arial, Times New Roman, or Calibri only when you control the target environment.
  2. Keep numbering styles simple; multi-level custom numbering is fragile outside Word.
  3. If recipients only need to read the document, export a PDF from Word or LibreOffice and keep the DOCX as the editable source.
```

```python
from docx.shared import Pt

run = doc.add_paragraph().add_run("Cross-platform safe text")
run.font.name = "Arial"
run.font.size = Pt(11)
```

---

## Testing Strategy

```text
Per-template workflow:
  1. Open in Microsoft Word desktop - baseline reference.
  2. Open in Google Docs - check tables, numbering, comments, and image placement.
  3. Open in LibreOffice Writer - check fonts, headers/footers, and page count drift.
  4. If exporting PDF, compare the PDF against the Word baseline.
  Re-test after any structural template or style change.
```

CI smoke test - verify LibreOffice can open and convert:

```python
import os
import subprocess

def validate_docx_opens(path: str) -> bool:
    result = subprocess.run(
        [
            "libreoffice",
            "--headless",
            "--convert-to",
            "pdf",
            path,
            "--outdir",
            "/tmp/docx-check",
        ],
        capture_output=True,
        timeout=30,
    )
    pdf = f"/tmp/docx-check/{os.path.basename(path).replace('.docx', '.pdf')}"
    return result.returncode == 0 and os.path.exists(pdf)
```

---

## Conversion Best Practices

| Method | Fidelity | Platform | Notes |
|--------|----------|----------|-------|
| Word automation (COM/JXA/AppleScript) | Highest | Windows / macOS | Best for Word-specific features and final release PDFs |
| `docx2pdf` | High | Windows / macOS | Wraps Microsoft Word; not a LibreOffice wrapper |
| LibreOffice headless | Good | Cross-platform | Best general-purpose batch conversion outside Word; expect some layout drift |
| `mammoth` (DOCX -> HTML) | Text-first only | Cross-platform | Good for semantic extraction, not layout fidelity |

```python
from docx2pdf import convert

convert("report.docx", "report.pdf")
convert("reports/", "pdfs/")
```

Use `docx2pdf` only where Microsoft Word is installed. Use LibreOffice headless when you need Linux support or CI batch conversion.

---

## Do / Avoid

| Do | Avoid |
|----|-------|
| Use built-in styles and simple numbering | Depending on Word-only XML quirks |
| Keep tables simple and structural | Using nested/layout tables for positioning |
| Keep images inline for portability | Relying on floating positioning across viewers |
| Test in Word plus one secondary viewer | Assuming Word rendering is universal |
| Convert to PDF when recipients only need to read | Sending feature-heavy DOCX files to uncontrolled environments |
| Treat `.docm` / `.dotm` as untrusted | Opening macro-enabled files casually in automation pipelines |

---

## Related Resources

- [docx-patterns.md](docx-patterns.md) - Advanced formatting and styles
- [review-comments-workflows.md](review-comments-workflows.md) - Comments, review workflows, and Word Compare
- [accessibility-compliance.md](accessibility-compliance.md) - DOCX accessibility patterns
- [document-automation-pipelines.md](document-automation-pipelines.md) - Batch generation and quality gates
- [SKILL.md](../SKILL.md) - Parent DOCX skill
