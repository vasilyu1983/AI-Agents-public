# PPTX Template & Branding - Corporate Identity Management

Rules for filling designer-owned templates: inspect before you write, address layouts and placeholders by name and idx, edit the theme rather than overriding colours per shape, and use PPTX-Automizer when the template must stay pixel-perfect. Building a deck from scratch with PptxGenJS is covered by the official `pptx` skill.

## Contents

- [Slide Master and Layout Architecture](#slide-master-and-layout-architecture)
- [Inspect The Template First](#inspect-the-template-first)
- [Layouts And Placeholders](#layouts-and-placeholders)
- [Theme Colors via XML](#theme-colors-via-xml)
- [PPTX-Automizer for Branded Templates](#pptx-automizer-for-branded-templates)
- [Multi-Brand Support](#multi-brand-support)
- [Font Substitution](#font-substitution)
- [Brand Consistency Checklist](#brand-consistency-checklist)
- [Do / Avoid](#do--avoid)

## Slide Master and Layout Architecture

```text
Presentation (.pptx)
├── Slide Master (slideMaster1.xml) ── Theme (theme1.xml): colours, fonts, effects
│   ├── Slide Layout: Title Slide
│   ├── Slide Layout: Title and Content
│   └── Slide Layout: ... (template-specific)
└── Slides: each references one layout
```

**Inheritance chain:** Theme → Slide Master → Slide Layout → Slide. A property set lower in the chain overrides one set higher. A colour set as a theme slot (`accent1`) follows a theme change; a direct RGB on a shape does not. That is why brand work belongs in the theme and the master, not in per-shape overrides.

Theme colour slots: `dk1`/`lt1` (primary text and background), `dk2`/`lt2`, `accent1`-`accent6` (brand palette, and the order in which charts use colours), `hlink`, `folHlink`. The font scheme sets `majorFont` (headings) and `minorFont` (body).

## Inspect The Template First

```bash
python3 scripts/pptx_inventory.py template.pptx --json      # layouts, placeholders, shape names
python3 scripts/pptx_ooxml_inspect.py template.pptx --json  # masters, media, notes, parts
```

Record each layout's name and each placeholder's `idx` and type before writing any fill code. Placeholder idx values and layout order are template-specific.

## Layouts And Placeholders

```python
def get_layout(prs, name):
    for layout in prs.slide_master.slide_layouts:
        if layout.name == name:
            return layout
    raise ValueError(f"Layout {name!r} not found. Available: "
                     f"{[l.name for l in prs.slide_master.slide_layouts]}")

slide = prs.slides.add_slide(get_layout(prs, "Title and Content"))
idxs = {ph.placeholder_format.idx for ph in slide.placeholders}
if 1 not in idxs:
    raise ValueError(f"Layout has no body placeholder idx 1; available: {sorted(idxs)}")
slide.placeholders[1].text = "Content here"
```

- **Never hard-code layout indices** (`prs.slide_layouts[1]`). The order differs between templates and changes when a designer edits the master.
- **`1 in slide.placeholders` is always `False`.** The membership test compares against the shapes, not their idx values, so a guard written that way always takes the fallback branch. That leaves an empty "Click to add text" placeholder on the slide next to a new text box. Test membership against the set of `placeholder_format.idx` values, as above.
- Fill the layout's placeholders rather than adding free text boxes. Placeholders carry the template's position, fonts and reading order.
- An unused placeholder still shows its prompt text in edit mode, and screen readers may announce it. Remove it (`ph.element.getparent().remove(ph.element)`) or fill it.

## Theme Colors via XML

python-pptx has no API for changing the theme. Edit the theme part directly:

```python
from pptx.opc.constants import RELATIONSHIP_TYPE as RT
from pptx.oxml.ns import qn
from lxml import etree

# `slide_master.part.slide_master` does not exist (AttributeError); the theme is a
# separate OPC part related to the slide master part by the RT.THEME relationship.
theme_part = prs.slide_master.part.part_related_by(RT.THEME)
theme = etree.fromstring(theme_part.blob)

accent1 = theme.find(".//" + qn("a:clrScheme")).find(qn("a:accent1"))
srgb = accent1.find(qn("a:srgbClr"))
if srgb is None:  # e.g. the slot uses <a:sysClr>; fail loudly instead of saving unchanged
    raise ValueError("accent1 is not an srgbClr; replace the child element instead")
srgb.set("val", "0066CC")

# python-pptx loads the theme as a plain Part (not an XmlPart): write the edited XML back to its
# private _blob, or the change is silently lost on save.
theme_part._blob = etree.tostring(theme, xml_declaration=True, encoding="UTF-8", standalone=True)
```

- `_blob` is private. Re-verify it after a python-pptx upgrade by reopening the saved file and reading the slot back.
- Keep all 12 colour slots populated, and back up the template before editing XML. Open the result in PowerPoint to confirm there is no repair prompt.

## PPTX-Automizer for Branded Templates

PPTX-Automizer is strongest when a designer owns the template and automation only replaces named elements, leaving the slide structure stable. Master and layout references usually survive; animation timing and embedded media need a retest.

```typescript
import Automizer, { ModifyChartHelper, ModifyTextHelper, ModifyTableHelper } from 'pptx-automizer';

const automizer = new Automizer({ templateDir: './templates', outputDir: './output' });
const pptx = automizer
  .loadRoot('branded-base.pptx')          // masters and theme
  .load('data-slides.pptx', 'data');      // content slides

// modifyElement(selector, callback | callback[]) takes modification callbacks,
// not a plain options object like { replaceChart: ... }.
pptx.addSlide('data', 1, (slide) => {
  slide.modifyElement('RevenueChart', ModifyChartHelper.setChartData(updatedChartData));
  slide.modifyElement('PeriodLabel', ModifyTextHelper.setText(periodLabel));
});
pptx.addSlide('data', 2, (slide) => {
  slide.modifyElement('MetricsTable', ModifyTableHelper.setTable(metricsData));
});

await pptx.write('quarterly_report.pptx');
```

- Selectors are **shape names** from the Selection Pane. Agree stable names with the designer (`RevenueChart`, not `Chart 7`) and check them with `pptx_inventory.py` before each run.
- A selector that matches nothing is a template-drift error. Verify the output (see the verification loop in `SKILL.md`) rather than assuming every modification applied.

## Multi-Brand Support

- Keep one canonical template per brand. Its theme carries the colours and fonts, and its master carries the logo, footer and slide number. Generation code picks the template; it never recolours shapes.
- Recolouring titles shape by shape (`font.color.rgb = ...` in a loop) creates exactly the direct overrides that stop a later theme change from applying. Change the theme slots instead.
- Store the brand metadata the code needs (template path, legal footer, logo variant) next to each template, and version the templates. Never mix layouts from two template versions in one deck.

## Font Substitution

If the brand font is not installed on the rendering machine, PowerPoint and LibreOffice substitute another font. Line breaks, overflow and alignment then change.
- Embed fonts in the template (PowerPoint: Options, Save, Embed fonts), or choose fonts available on every target machine.
- For PDF export, the fonts must be installed on the machine that exports.
- Render on the target platform before sign-off.

## Brand Consistency Checklist

- [ ] Logo position and size are identical on every non-title slide (they come from the master)
- [ ] Colours come from theme slots; no ad hoc hex values on shapes
- [ ] Heading and body fonts match the theme font scheme, and fonts are embedded or installed
- [ ] The footer carries the required legal text; slide numbers are present and consistent
- [ ] Chart series follow accent order
- [ ] No orphaned layouts from earlier template versions
- [ ] No empty placeholders left with prompt text

## Do / Avoid

**Do:** look up layouts by name, check placeholder idx values before filling, use PPTX-Automizer when designers own the template, keep one canonical template per brand, and test the generated file in PowerPoint on the target OS.

**Avoid:** hard-coded layout indices, `in slide.placeholders` membership tests, direct RGB overrides where a theme slot exists, editing master XML without a backup, creating new layouts in code when the template has one, and replacing animated or media-heavy shapes without a retest.

## Related Resources

- [pptx-layouts.md](pptx-layouts.md) - Layout choice
- [pptx-charts.md](pptx-charts.md) - Chart styling with the theme palette
- [pptx-animations-transitions.md](pptx-animations-transitions.md) - Transitions and motion
- [../assets/pitch-deck.md](../assets/pitch-deck.md) - Pitch deck structure
