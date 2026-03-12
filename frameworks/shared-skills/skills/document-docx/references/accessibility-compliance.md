# DOCX Accessibility Compliance

Patterns for producing accessible DOCX files that work with screen readers and meet WCAG 2.2 AA / EN 301 549 requirements.

## Contents

- Heading Hierarchy
- Alt Text for Images
- Accessible Tables
- Color Contrast and Font Sizing
- Document Language
- WCAG 2.2 AA Checklist
- Word Accessibility Checker
- EU EAA / EN 301 549
- Do / Avoid

---

## Heading Hierarchy

Screen readers build a navigation tree from heading levels. Skipping levels (H1 to H3 with no H2) breaks that tree.

```python
from docx import Document

doc = Document()
doc.add_heading('Annual Report', level=1)       # One H1 per document
doc.add_heading('Financial Summary', level=2)
doc.add_paragraph('Revenue grew 12% year-over-year.')
doc.add_heading('Regional Breakdown', level=3)  # Sequential: 1 → 2 → 3
doc.add_heading('Operational Highlights', level=2)
```

Rules: one Heading 1 per document (document title). Never skip levels. Do not use bold normal text as a fake heading.

---

## Alt Text for Images

python-docx has no high-level alt text API. Set it via OOXML:

```python
from docx.shared import Inches
from docx.oxml.ns import qn

inline_shape = doc.add_paragraph().add_run().add_picture('chart.png', width=Inches(4))
docPr = inline_shape._inline.find(qn('wp:docPr'))
docPr.set('descr', 'Bar chart showing Q1-Q4 revenue growth')  # Alt text
docPr.set('title', 'Revenue Chart')

# Decorative image: empty description signals "skip this"
# docPr.set('descr', '')
```

---

## Accessible Tables

Mark the first row as a header so screen readers announce column names and the row repeats on page breaks:

```python
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

table = doc.add_table(rows=3, cols=3)
table.style = 'Table Grid'
trPr = table.rows[0]._tr.get_or_add_trPr()
trPr.append(OxmlElement('w:tblHeader'))

for i, text in enumerate(['Name', 'Role', 'Department']):
    table.rows[0].cells[i].text = text
```

Avoid merged cells, nested tables, and tables used for page layout.

---

## Color Contrast and Font Sizing

| Requirement | WCAG 2.2 AA Threshold |
|-------------|----------------------|
| Normal text contrast | 4.5:1 minimum |
| Large text (>= 18pt or 14pt bold) | 3:1 minimum |
| Non-text elements (charts, icons) | 3:1 against background |

```python
from docx.shared import Pt, RGBColor

run = doc.add_paragraph().add_run('Accessible body text')
run.font.size = Pt(11)
run.font.color.rgb = RGBColor(0x1A, 0x1A, 0x1A)  # Near-black
run.font.name = 'Arial'
```

Never rely on color alone to convey meaning. Add text labels ("Warning:") alongside color cues.

---

## Document Language

Set language so screen readers pick the correct speech synthesizer:

```python
from docx.oxml.ns import qn

styles_el = doc.styles.element
rPr = styles_el.find(qn('w:docDefaults')).find(qn('w:rPrDefault')).find(qn('w:rPr'))
lang = rPr.find(qn('w:lang'))
if lang is not None:
    lang.set(qn('w:val'), 'en-US')
```

---

## WCAG 2.2 AA Checklist

```text
  [ ] Heading hierarchy is sequential (no skipped levels)
  [ ] Every informative image has alt text
  [ ] Decorative images marked decorative (empty descr)
  [ ] Tables have header rows (w:tblHeader)
  [ ] No nested or layout tables
  [ ] Color contrast meets 4.5:1 for body text
  [ ] Font size 11pt+ for body text
  [ ] Color is not sole means of conveying information
  [ ] Document language is set
  [ ] Hyperlinks have descriptive text (not "click here")
  [ ] Lists use List Bullet / List Number styles (not manual dashes)
```

---

## Word Accessibility Checker: Catches vs Misses

| Catches | Misses |
|---------|--------|
| Missing alt text | Poor-quality alt text ("image1.png") |
| Missing table header rows | Complex merged-cell reading order |
| Blank table cells | Color contrast failures (no ratio check) |
| Missing document title | Logical reading order in multi-column layouts |

Run: Review tab > Check Accessibility. Treat as minimum bar, not a full audit.

---

## EU EAA / EN 301 549 Relevance

The European Accessibility Act (effective June 2025) requires EN 301 549 compliance. Section 10 applies WCAG success criteria to non-web documents: structure, alt text, contrast, language, reading order. Documents published on websites or sent as part of a service fall in scope. Enforce accessibility at the template level, not through post-hoc remediation.

---

## Do / Avoid

| Do | Avoid |
|----|-------|
| Use built-in heading styles | Bold normal text as fake headings |
| Write descriptive alt text (what + why) | Filename as alt text |
| Mark header rows on every table | Layout tables for positioning |
| Set document language at the template level | Leaving language unset |
| Test with Accessibility Checker + manual review | Relying solely on automated checks |
| Use 11pt+ body text, high-contrast colors | Light gray text, decorative fonts below 10pt |

---

## Related Resources

- [docx-patterns.md](docx-patterns.md) - Advanced formatting and styles
- [template-workflows.md](template-workflows.md) - Template-based generation
- [SKILL.md](../SKILL.md) - Parent DOCX skill
- [WCAG 2.2](https://www.w3.org/TR/WCAG22/) / [EN 301 549](https://www.etsi.org/deliver/etsi_en/301500_301599/301549/)
