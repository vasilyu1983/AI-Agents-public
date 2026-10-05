# python-docx Patterns And Gotchas

The official Anthropic `docx` skill covers docx-js generation. This file is the python-docx lane: only the patterns where the obvious code is wrong or python-docx has no public API. Basic calls (`add_heading`, `add_table`, `add_picture`, section margins) are assumed knowledge.

## Contents

- Styles
- Tables
- Sections And Orientation
- Fields (PAGE, TOC)
- Hyperlinks
- Corruption Pitfalls And Round-Trip Fidelity

## Styles

- `doc.styles.add_style(name, ...)` raises `ValueError` if the name already exists. The default template already ships `Emphasis`, `Quote`, `Caption`, `List Bullet` and others, so guard before adding:

```python
from docx.enum.style import WD_STYLE_TYPE

name = "CustomEmphasis"
style = doc.styles[name] if name in doc.styles else doc.styles.add_style(name, WD_STYLE_TYPE.CHARACTER)
style.font.italic = True
```

- `add_paragraph(style="X")` / `add_run(style="X")` raise `KeyError` when the template lacks style `X`. A document built from a client template may not have `List Bullet` or `Caption`; check `doc.styles` first.
- A custom style's `base_style` is not validated. Point it at a style that does not exist and Word silently falls back to Normal.
- Prefer styles over per-run `run.font.*`. Direct formatting looks right but breaks TOC generation, accessibility tools and HTML/Markdown extraction, and is the usual reason a generated file fails brand review.

## Tables

- A cell's first paragraph has no runs until text is added. `cell.paragraphs[0].runs[0]` raises `IndexError` on an empty cell:

```python
p = cell.paragraphs[0]
run = p.runs[0] if p.runs else p.add_run()
```

- Cell shading has no public API. [Word treats `w:shd/@w:val` as required](https://learn.microsoft.com/en-us/openspecs/office_standards/ms-oe376/c7a6a5fd-538c-4a77-8cbb-0f447298dace). Reuse an existing `w:shd` so repeat calls do not create duplicate elements:

```python
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

def shade_cell(cell, hex_fill: str) -> None:
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = tc_pr.find(qn("w:shd"))
    if shd is None:
        shd = OxmlElement("w:shd")
        tc_pr.insert_element_before(
            shd, "w:noWrap", "w:tcMar", "w:textDirection", "w:tcFitText",
            "w:vAlign", "w:hideMark", "w:headers", "w:cellIns", "w:cellDel",
            "w:cellMerge", "w:tcPrChange",
        )
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:fill"), hex_fill)
```

- Column width: set `cell.width` on every cell in the column. `table.columns[i].width` only writes the grid, and Word generally lays the table out from the per-cell widths.
- `a.merge(b)` returns the merged cell and keeps both cells' paragraphs (`'A\nB'`). Clear the text first if you do not want the leftovers.
- Repeat a header row on each page (also an accessibility requirement): see `accessibility-compliance.md`.

## Sections And Orientation

Setting `section.orientation = WD_ORIENT.LANDSCAPE` does not rotate the page. You must also swap the dimensions:

```python
section.orientation = WD_ORIENT.LANDSCAPE
section.page_width, section.page_height = section.page_height, section.page_width
```

`doc.add_section(WD_SECTION.NEW_PAGE)` starts a new section that inherits the previous one's settings. Change orientation on the new section object, not on `doc.sections[0]`. Multi-column layout has no API: append `<w:cols w:num="2" w:space="720"/>` to `section._sectPr` (space is in twips).

## Fields (PAGE, TOC)

Fields are three-part structures: `fldChar begin`, `instrText`, `fldChar separate` (optional), `fldChar end`. python-docx has no field API. The field shows its cached result, or nothing, until Word or LibreOffice updates it.

```python
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

def add_field(paragraph, instr: str) -> None:
    run = paragraph.add_run()
    for kind, text in (("begin", None), (None, instr), ("separate", None), ("end", None)):
        if kind:
            el = OxmlElement("w:fldChar"); el.set(qn("w:fldCharType"), kind)
        else:
            el = OxmlElement("w:instrText"); el.set(qn("xml:space"), "preserve"); el.text = text
        run._r.append(el)

add_field(section.footer.paragraphs[0], "PAGE")
add_field(doc.add_paragraph(), 'TOC \\o "1-3" \\h \\z \\u')
```

- A TOC inserted this way is empty until fields are updated. In an unattended pipeline, render through LibreOffice headless and check in the rendered PDF that the TOC is populated. If it is not, the recipient must update fields in Word (F9). Never ship a TOC that shows nothing.
- To make Word refresh fields on open, add `<w:updateFields w:val="true"/>` to `word/settings.xml`. Word then shows a prompt on open, so warn the recipient.

## Hyperlinks

python-docx has no public hyperlink authoring API. The link needs an external relationship plus a `w:hyperlink` element. Use the `Hyperlink` character style so the link is styled semantically rather than with hardcoded colour:

```python
from docx.opc.constants import RELATIONSHIP_TYPE as RT

def add_hyperlink(paragraph, url: str, text: str):
    r_id = paragraph.part.relate_to(url, RT.HYPERLINK, is_external=True)
    link = OxmlElement("w:hyperlink"); link.set(qn("r:id"), r_id)
    run = OxmlElement("w:r"); rpr = OxmlElement("w:rPr")
    rstyle = OxmlElement("w:rStyle"); rstyle.set(qn("w:val"), "Hyperlink"); rpr.append(rstyle)
    t = OxmlElement("w:t"); t.text = text
    run.append(rpr); run.append(t); link.append(run)
    paragraph._p.append(link)
```

python-docx's default template has no `Hyperlink` style. Add one, or use a template that has it; otherwise the link works but renders unstyled. Link text must describe the destination, not "click here".

## Corruption Pitfalls And Round-Trip Fidelity

- **Element order is schema-enforced.** Children of `w:rPr`, `w:pPr`, `w:tcPr` and `w:trPr` must follow the schema sequence, not the order that is convenient in code. Appending in the wrong order is a leading cause of Word's "found a problem with some content" repair prompt. LibreOffice and python-docx open the same file without complaint, so they do not prove validity. If you appended raw OXML, validate with the official `docx` skill's validator.
- **Re-saving is not byte-for-byte.** python-docx round-trips the XML it does not model (custom XML parts, content controls, SmartArt), but do not assume a lossless round trip once you have touched those regions. Diff the part list before and after with `scripts/docx_inspect_ooxml.py --list-parts`.
- **Fields keep stale cached results** after you edit the surrounding text, until a user or a renderer updates them.
- **Core properties leak.** New documents carry `author="python-docx"`, a fixed creation date years in the past and `comments="generated by python-docx"`. Reset them before saving (SKILL.md Default Workflow, step 4).
- **Private attributes** (`_tc`, `_r`, `_p`, `_sectPr`, `_inline`) are implementation details. Re-verify them after upgrading python-docx, and use a public API whenever one exists.

## Related Resources

- [SKILL.md](../SKILL.md) - Quick reference
- [template-workflows.md](template-workflows.md) - docxtpl templates and batch generation
- [accessibility-compliance.md](accessibility-compliance.md) - Headings, alt text, table headers, language
- [python-docx documentation](https://python-docx.readthedocs.io/)
