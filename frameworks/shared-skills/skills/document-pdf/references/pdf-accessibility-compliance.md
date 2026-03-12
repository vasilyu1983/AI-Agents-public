# PDF Accessibility and Compliance

Patterns for producing accessible, standards-compliant PDF documents.

---

## Contents

- [Tagged vs Untagged PDFs](#tagged-vs-untagged-pdfs)
- [PDF/UA Standard (ISO 14289)](#pdfua-standard-iso-14289)
- [Creating Tagged PDFs](#creating-tagged-pdfs)
- [Reading Order and Alt Text](#reading-order-and-alt-text)
- [EU EAA and EN 301 549](#eu-eaa-and-en-301-549)
- [Validation Tools](#validation-tools)
- [Decision Guide: When to Invest](#decision-guide-when-to-invest)
- [Checklist: PDF Accessibility Review](#checklist-pdf-accessibility-review)

---

## Tagged vs Untagged PDFs

A tagged PDF contains a logical structure tree mapping visual elements to semantic roles (headings, paragraphs, tables, figures). Screen readers depend on this tree. Without tags, assistive technology guesses reading order from character positions, which fails on multi-column layouts, tables, and sidebars.

Untagged PDFs cannot be reliably fixed after the fact. Retroactively tagging a complex document is manual, error-prone, and typically more expensive than regenerating from a structured source. Budget 30-60 minutes per page for manual remediation.

---

## PDF/UA Standard (ISO 14289)

Key requirements: every content element tagged or marked as artifact; tag tree reflects logical reading order; all images have alt text; tables use TH/TD with scope; document language declared; fonts embedded with Unicode mappings; no reliance on colour alone. Compliance with PDF/UA generally satisfies EN 301 549 and Section 508 for PDF content.

---

## Creating Tagged PDFs

Generate from structured source. Do not post-fix untagged PDFs.

### WeasyPrint (Python) — HTML+CSS to Tagged PDF

```python
from weasyprint import HTML

html = """
<!DOCTYPE html>
<html lang="en">
<head><meta charset="utf-8">
<style>
  body { font-family: sans-serif; font-size: 12pt; }
  table { border-collapse: collapse; width: 100%; }
  th, td { border: 1px solid #333; padding: 6px; }
</style></head>
<body>
  <h1>Quarterly Report</h1>
  <p>Summary of Q4 metrics.</p>
  <table>
    <thead><tr><th>Metric</th><th>Value</th></tr></thead>
    <tbody><tr><td>Revenue</td><td>$1.2M</td></tr></tbody>
  </table>
  <img src="chart.png" alt="Bar chart showing quarterly revenue growth">
</body></html>
"""

HTML(string=html).write_pdf('report.pdf', presentational_hints=True)
```

The tag tree mirrors HTML semantics: `<h1>` becomes Heading, `<table>` maps to Table/TR/TH/TD, `<img alt="...">` becomes Figure with alt text. DOCX export also works: use built-in heading styles, alt text on images, table header rows, then export with "Tagged PDF" enabled.

---

## Reading Order and Alt Text

**Reading order** must match logical content flow. Common failures: multi-column text read across columns, headers injected mid-body, footnotes before referencing paragraphs. Prevention: generate from single-flow HTML or style-based DOCX authoring.

**Alt text**: describe what the image communicates, not what it looks like. Charts: state the trend ("Revenue grew 23% YoY"). Logos: company name. Keep under 150 characters. Mark decorative images as artifacts.

---

## EU EAA and EN 301 549

The European Accessibility Act (EAA, effective June 2025) requires products and services sold in the EU to meet accessibility standards. EN 301 549 clause 10 covers non-web documents and points to WCAG 2.1 AA plus PDF/UA. Customer-facing PDFs (invoices, contracts, statements, product docs) distributed in the EU should be tagged and meet PDF/UA. Internal-only documents have lower regulatory exposure.

---

## Validation Tools

| Tool | Platform | Scope |
|------|----------|-------|
| PAC (PDF Accessibility Checker) | Windows (free) | Full PDF/UA validation |
| Adobe Acrobat Accessibility Checker | Win/macOS | Tags, reading order, alt text |
| axe-pdf (Deque) | CLI/CI | Automated pipeline integration |
| VoiceOver / NVDA | macOS / Windows | Manual screen reader testing |

```bash
# Quick tag presence check (Poppler)
pdfinfo report.pdf | grep Tagged
# "Tagged: yes" means tags exist — not that they are correct.
```

Always pair automated checks with at least one manual screen reader pass.

---

## Decision Guide: When to Invest

| Scenario | Level |
|----------|-------|
| Customer-facing PDFs in EU | Full PDF/UA compliance |
| Public marketing / docs | Tagged PDF + alt text + reading order |
| Internal reports, sighted team | Selectable text, bookmarks, clean metadata |
| Archival / legal hold | PDF/A; add tags if public-facing |
| One-off personal exports | No accessibility work needed |

---

## Checklist: PDF Accessibility Review

- [ ] Document language declared (`/Lang` entry)
- [ ] PDF is tagged (`/MarkInfo` with `Marked: true`)
- [ ] Heading hierarchy correct (H1 > H2 > H3, no skipped levels)
- [ ] All meaningful images have alt text
- [ ] Decorative images marked as artifacts
- [ ] Tables use TH for headers with scope
- [ ] Reading order matches logical flow (screen reader test)
- [ ] Links have descriptive text (not raw URLs)
- [ ] Fonts embedded with Unicode mappings
- [ ] PAC or Acrobat accessibility check passes with zero errors

---

## Do / Avoid

### Do

- Generate tagged PDFs from semantic HTML (WeasyPrint) or styled DOCX.
- Set document language at the root level.
- Test with a real screen reader at least once per template.
- Automate validation in CI for recurring document types.

### Avoid

- Manually tagging complex untagged PDFs — regenerate from source instead.
- Using text boxes or absolute positioning in Word for layout.
- Assuming "it looks fine" means it is accessible.
- Treating accessibility as a post-release patch.

---

## Related

- [pdf-generation-patterns.md](pdf-generation-patterns.md) — Layout and generation code
- [pdf-extraction-patterns.md](pdf-extraction-patterns.md) — Text and table extraction
- [../assets/pdf-release-checklist.md](../assets/pdf-release-checklist.md) — Pre-distribution quality gate
