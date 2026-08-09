# DOCX Accessibility Compliance

## Table of Contents

- [Contents](#contents)
- [Structure First](#structure-first)
- [Alt Text For Images](#alt-text-for-images)
- [Accessible Tables](#accessible-tables)
- [Links, Language, And Contrast](#links-language-and-contrast)
- [Word Accessibility Checker](#word-accessibility-checker)
- [EU / EN 301 549 Context](#eu--en-301-549-context)
- [Practical Checklist](#practical-checklist)
- [Related Resources](#related-resources)

Patterns for producing accessible Word documents. Use this when the document is customer-facing, procurement-sensitive, or likely to be exported to PDF or published online.

## Contents

- Structure First
- Alt Text For Images
- Accessible Tables
- Links, Language, And Contrast
- Word Accessibility Checker
- EU / EN 301 549 Context
- Practical Checklist

---

## Structure First

Screen readers rely on Word structure, not visual bolding.

```python
from docx import Document

doc = Document()
doc.add_heading("Annual Report", level=1)
doc.add_heading("Financial Summary", level=2)
doc.add_paragraph("Revenue grew 12% year-over-year.")
doc.add_heading("Regional Breakdown", level=3)
doc.add_heading("Operational Highlights", level=2)
```

Practical rules:
- Use built-in heading styles instead of fake headings made from bold text.
- Keep heading levels sequential.
- Use real list styles rather than manual dashes or typed numbers.
- Keep tables for data, not layout.

---

## Alt Text For Images

`python-docx`'s `InlineShape` only documents `height`, `width`, and `type` — there is still no public `.alt_text`/`.descr` property, so set it through OOXML when needed:

```python
from docx.shared import Inches
from docx.oxml.ns import qn

inline_shape = doc.add_paragraph().add_run().add_picture("chart.png", width=Inches(4))
doc_pr = inline_shape._inline.find(qn("wp:docPr"))
doc_pr.set("descr", "Bar chart showing Q1 to Q4 revenue growth")
doc_pr.set("title", "Revenue chart")
```

`inline_shape._inline` is a private attribute (python-docx's own constructor names it that way), not a documented public API. It has been stable for years, but treat it as an implementation detail: re-verify against the installed `python-docx` version after any upgrade, and prefer a public API (e.g. `add_comment`, style objects) over reaching into `_`-prefixed attributes whenever one exists for the task at hand.

Practical rules:
- Every informative image should explain what it shows and why it matters.
- Decorative images should not add noise; use an empty description when appropriate.
- If a chart is critical, also summarize its conclusion in text nearby.

---

## Accessible Tables

Mark the first row as a header and keep the structure simple:

```python
from docx.oxml import OxmlElement

table = doc.add_table(rows=3, cols=3)
table.style = "Table Grid"

tr_pr = table.rows[0]._tr.get_or_add_trPr()
tr_pr.append(OxmlElement("w:tblHeader"))

for i, text in enumerate(["Name", "Role", "Department"]):
    table.rows[0].cells[i].text = text
```

Avoid:
- Nested tables
- Merged cells when a simple layout would work
- Blank cells used only for spacing
- Tables used for page layout

---

## Links, Language, And Contrast

Use descriptive link text and declare the document language.

```python
from docx.oxml.ns import qn

styles_el = doc.styles.element
r_pr = styles_el.find(qn("w:docDefaults")).find(qn("w:rPrDefault")).find(qn("w:rPr"))
lang = r_pr.find(qn("w:lang"))
if lang is not None:
    lang.set(qn("w:val"), "en-US")
```

```python
from docx.shared import Pt, RGBColor

run = doc.add_paragraph().add_run("Accessible body text")
run.font.size = Pt(11)
run.font.color.rgb = RGBColor(0x1A, 0x1A, 0x1A)
```

Practical rules:
- Use descriptive links, not "click here".
- Set document language in the template where possible.
- Do not rely on color alone to convey meaning.
- Prefer body text around 11pt or larger unless the template has a strong reason not to.

---

## Word Accessibility Checker

Word's built-in checker is a baseline, not a full audit.

| It Often Catches | It Often Misses |
|------------------|-----------------|
| Missing alt text | Weak or useless alt text |
| Missing table header rows | Reading-order problems in complex layouts |
| Missing title/document properties | Real contrast failures |
| Some list/table issues | Whether nearby text explains important charts |

Run it from the Review tab before release, then do a manual pass for reading order, link wording, charts, and template drift.

---

## EU / EN 301 549 Context

Do not treat accessibility law as a one-line universal rule.

As of July 2026:
- The European Accessibility Act has been enforceable since June 28, 2025, but whether a given DOCX is in scope still depends on the product/service context, not the file format alone.
- EN 301 549 is the practical European baseline used in many procurement and compliance contexts. The current published version (V3.2.1) still references WCAG 2.1 Level AA; a revision (V4.1.1) aligning it with WCAG 2.2 Level AA is expected but was not yet in force at last check.
- Do not state a specific EN 301 549 version or WCAG level as settled fact for a live compliance decision — confirm the currently in-force revision at the time of the engagement, since this is actively moving.

Practical guidance:
- For real-world authoring, target clean structure and checks that would comfortably satisfy a WCAG 2.2-style review now, ahead of the standard catching up.
- For legal/compliance claims, verify the user's jurisdiction, distribution context, and the current EN 301 549 revision before making definitive statements.
- For customer-facing EU document workflows, enforce accessibility in the template and review process rather than relying on remediation at the end.

---

## Practical Checklist

```text
  [ ] Heading hierarchy is real and sequential
  [ ] Lists use Word list styles
  [ ] Every informative image has meaningful alt text
  [ ] Tables use a header row and simple structure
  [ ] Document language is set
  [ ] Hyperlinks are descriptive
  [ ] Body text and contrast are readable
  [ ] Accessibility Checker was run
  [ ] Manual review covered reading order, charts, and template drift
  [ ] Legal/compliance claims were verified for the actual distribution context
```

---

## Related Resources

- [review-comments-workflows.md](review-comments-workflows.md) - Review-oriented workflows before release
- [cross-platform-compatibility.md](cross-platform-compatibility.md) - Viewer drift and PDF conversion
- [llm-extraction-workflows.md](llm-extraction-workflows.md) - Extraction workflows when DOCX is reused downstream
- [SKILL.md](../SKILL.md) - Parent DOCX skill
- [WCAG 2.2](https://www.w3.org/TR/WCAG22/)
- [W3C WAI - European Union](https://www.w3.org/WAI/policies/european-union/)
