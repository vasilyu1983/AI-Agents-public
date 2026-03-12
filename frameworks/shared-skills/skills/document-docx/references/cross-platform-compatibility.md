# Cross-Platform DOCX Compatibility

Rendering differences across Microsoft Word, Google Docs, and LibreOffice. Safe features, risky features, font handling, conversion strategies, and testing workflow.

## Contents

- Rendering Differences
- Safe Features
- Risky Features
- Font Handling
- Testing Strategy
- Conversion Best Practices
- Do / Avoid
- Related Resources

---

## Rendering Differences

| Area | Word | Google Docs | LibreOffice |
|------|------|-------------|-------------|
| Headings, bold/italic | Exact | Correct (minor spacing drift) | Correct (font substitution common) |
| Simple tables | Exact | Cell padding may shift | Border rendering varies |
| Merged / nested tables | Full support | Merged cells break; nesting lost | Nested tables misaligned |
| Inline images | Exact | Exact | Exact |
| Floating images | Full support | Converted to inline or lost | Position may shift |
| SmartArt | Full support | Flattened to image or missing | Not rendered |
| Macros (VBA) | Executes | Stripped | Not supported |
| Multi-level numbering | Full support | May flatten to simple list | Restart rules can break |
| Content controls / form fields | Full support | Not interactive | Partial rendering |

---

## Safe Features

These render consistently across all three platforms:

```text
  - Headings (levels 1-6, built-in styles)
  - Bold, italic, underline, strikethrough
  - Font name and size (if font available)
  - Paragraph alignment (left, center, right, justify)
  - Simple tables (no merges, no nesting)
  - Inline images (PNG, JPEG)
  - Single-level bulleted and numbered lists
  - Page breaks
  - Basic headers/footers (text + page numbers)
  - Hyperlinks
```

---

## Risky Features

| Feature | Risk | Failure Mode |
|---------|------|--------------|
| Merged table cells | Medium | Content shifts in Google Docs |
| Nested tables | High | Layout breaks in LibreOffice |
| SmartArt | High | Missing or flattened |
| Floating images | Medium | Repositioned or inlined |
| Embedded objects (Excel, PDF) | High | Not rendered outside Word |
| Macros / VBA | High | Stripped or blocked |
| Multi-level numbering | Medium | Indentation and restart rules break |
| Text effects (glow, 3D) | Medium | Stripped in Docs and LibreOffice |

---

## Font Handling

When a font is missing, the platform substitutes a fallback, changing line breaks and page count.

```text
Strategies:
  1. Use universally available fonts: Arial, Times New Roman, Courier New
  2. Embed fonts: Word > Options > Save > "Embed fonts" (adds 500KB-2MB)
     Google Docs ignores embedded fonts. LibreOffice reads them.
  3. Convert to PDF for guaranteed fidelity when recipients only need to read
```

```python
from docx.shared import Pt

run = doc.add_paragraph().add_run('Cross-platform safe text')
run.font.name = 'Arial'   # Widely available
run.font.size = Pt(11)
```

---

## Testing Strategy

```text
Per-template testing workflow:
  1. Open in Microsoft Word (desktop) — baseline reference
  2. Open in Google Docs — check tables, images, numbering, fonts
  3. Open in LibreOffice Writer — check layout, fonts, headers
  4. Compare page count — if different, font substitution is changing line breaks
  Re-test after any structural template change.
```

CI smoke test — verify LibreOffice can open and convert:

```python
import subprocess, os

def validate_docx_opens(path: str) -> bool:
    result = subprocess.run(
        ['libreoffice', '--headless', '--convert-to', 'pdf', path,
         '--outdir', '/tmp/docx-check'], capture_output=True, timeout=30)
    pdf = f"/tmp/docx-check/{os.path.basename(path).replace('.docx', '.pdf')}"
    return result.returncode == 0 and os.path.exists(pdf)
```

---

## Conversion Best Practices

| Method | Fidelity | Platform | Notes |
|--------|----------|----------|-------|
| Word COM/VBA | Highest | Windows only | Best for Word-specific features |
| LibreOffice headless | Good | Cross-platform | Minor layout drift on complex docs |
| docx2pdf (Python) | High | Windows/macOS | Wraps Word or LibreOffice |
| mammoth (DOCX → HTML) | Text only | Cross-platform | Loses layout; good for content extraction |

```python
from docx2pdf import convert
convert("report.docx", "report.pdf")   # Single file
convert("reports/", "pdfs/")           # Batch directory
```

---

## Do / Avoid

| Do | Avoid |
|----|-------|
| Use built-in heading and list styles | Custom XML formatting only Word understands |
| Stick to Arial, Times New Roman | Calibri without fallback for non-Windows users |
| Use simple tables (no merges, no nesting) | Nested or complex merged-cell tables |
| Test in Word, Google Docs, and LibreOffice | Assuming Word rendering is universal |
| Convert to PDF when editing is not needed | Distributing DOCX with SmartArt or macros |
| Use inline images (PNG/JPEG) | Floating images for cross-platform documents |

---

## Related Resources

- [docx-patterns.md](docx-patterns.md) - Advanced formatting and styles
- [accessibility-compliance.md](accessibility-compliance.md) - DOCX accessibility patterns
- [template-workflows.md](template-workflows.md) - Template-based generation
- [SKILL.md](../SKILL.md) - Parent DOCX skill
- [mammoth.js](https://github.com/mwilliamson/mammoth.js)
- [docx2pdf](https://github.com/AlJohri/docx2pdf)
