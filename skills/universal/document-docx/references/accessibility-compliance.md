# DOCX Accessibility Compliance

Use this when the document is customer-facing, procurement-sensitive, or will be exported to PDF or published. Accessibility set in the DOCX carries into a tagged PDF export; remediating the PDF afterwards costs far more.

## Structure

Screen readers navigate by Word structure, not by visual formatting.

- Use built-in heading styles (`add_heading`), never bold Normal text, and keep levels sequential (no H1 to H3 jump).
- Use real list styles, not typed dashes or numbers.
- Use tables for data only. No layout tables, no nested tables, no blank spacer cells, and avoid merged cells when a simple grid works.
- Set the document title (`core_properties.title`). Word and PDF exports surface it to assistive tech.

## Alt Text

python-docx has no public alt-text property: `InlineShape` documents only `height`, `width` and `type`. Set it through OOXML:

```python
from docx.oxml.ns import qn

shape = doc.add_paragraph().add_run().add_picture("chart.png", width=Inches(4))
doc_pr = shape._inline.find(qn("wp:docPr"))
doc_pr.set("descr", "Bar chart: revenue rose each quarter, Q4 highest")
```

- `_inline` is private. Re-verify it after any python-docx upgrade.
- Informative images say what the image shows and why it matters. For a key chart, also state the conclusion in nearby text.
- Decorative images: mark them decorative in Word (Alt Text pane, "Mark as decorative"). An empty `descr` alone is not the same signal.

## Table Header Rows

Mark the header row so it is announced and repeats across pages:

```python
from docx.oxml import OxmlElement
tr_pr = table.rows[0]._tr.get_or_add_trPr()
tr_pr.append(OxmlElement("w:tblHeader"))
```

## Language

Set the document language, or screen readers use the wrong pronunciation. python-docx's default template says `en-US`; a client template may have no `w:lang` at all, so create it when missing:

```python
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

r_pr = doc.styles.element.find(qn("w:docDefaults")).find(qn("w:rPrDefault")).find(qn("w:rPr"))
lang = r_pr.find(qn("w:lang"))
if lang is None:
    lang = OxmlElement("w:lang"); r_pr.append(lang)
lang.set(qn("w:val"), "en-GB")
```

Mark passages in another language at run level (`w:lang` in that run's `rPr`).

## Links, Colour, Contrast

- Link text must describe the destination, never "click here" or a bare URL.
- Do not use colour alone to convey meaning; add a text label or symbol as well.
- Check text contrast against WCAG AA. Grey-on-white body text is the usual failure.

## Word Accessibility Checker

A baseline, not an audit. Run it from the Review tab, then review manually.

| It often catches | It often misses |
|------------------|-----------------|
| Missing alt text | Weak or useless alt text |
| Missing table header rows | Reading order in complex layouts |
| Missing title | Real contrast failures in some cases |
| Some list and table issues | Whether nearby text explains key charts |

## EU / EN 301 549 Context

- The European Accessibility Act (EAA) applies to in-scope products and services. Whether a given DOCX is in scope depends on the product or service context, not on the file format.
- EN 301 549 is the European ICT accessibility standard that maps to WCAG. Presumption of conformity comes only from the EN 301 549 revision that the European Commission has cited in the Official Journal. That revision can lag the newest ETSI publication.
- **Lookup step before any conformance statement:** find (a) the newest ETSI EN 301 549 deliverable and the WCAG version and level it maps to, and (b) the revision cited in the Official Journal on the date of the statement. Build to the newer WCAG level. Cite the OJ-cited revision in the conformance statement. Never state either version from memory.
- For legal or compliance claims, confirm the jurisdiction and distribution context first. Enforce accessibility in the template and review loop, not at the end.

## Checklist

```text
[ ] Real, sequential heading hierarchy
[ ] Lists use Word list styles
[ ] Informative images have meaningful alt text; decorative ones are marked decorative
[ ] Tables have a marked header row and a simple structure
[ ] Document title and language are set
[ ] Links are descriptive; colour is never the only signal; contrast meets AA
[ ] Accessibility Checker run, plus manual review of reading order and charts
[ ] Compliance claims checked against the OJ-cited EN 301 549 revision for the actual context
```

## Related Resources

- [cross-platform-compatibility.md](cross-platform-compatibility.md) - Viewer drift and PDF conversion
- [SKILL.md](../SKILL.md) - Parent DOCX skill
- [WCAG 2.2](https://www.w3.org/TR/WCAG22/)
- [W3C WAI - European Union policies](https://www.w3.org/WAI/policies/european-union/)
