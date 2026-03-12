# PPTX Template & Branding - Corporate Identity Management

Deep-dive resource for slide masters, theme configuration, branded templates, and multi-brand workflows with python-pptx, PptxGenJS, and PPTX-Automizer.

---

## Contents

- [Slide Master and Layout Architecture](#slide-master-and-layout-architecture)
- [Theme Elements](#theme-elements)
- [Creating Reusable Templates (Python)](#creating-reusable-templates-python)
- [Branded Master Slides (PptxGenJS)](#branded-master-slides-pptxgenjs)
- [PPTX-Automizer for Branded Templates](#pptx-automizer-for-branded-templates)
- [Template Versioning and Distribution](#template-versioning-and-distribution)
- [Multi-Brand Support](#multi-brand-support)
- [Brand Consistency Checklist](#brand-consistency-checklist)
- [Common Pitfalls](#common-pitfalls)
- [Do / Avoid](#do--avoid)
- [Related Resources](#related-resources)

---

## Slide Master and Layout Architecture

```text
Presentation (.pptx)
├── Slide Master (slideMaster1.xml)
│   ├── Theme (theme1.xml) — colors, fonts, effects
│   ├── Slide Layout: Title Slide
│   ├── Slide Layout: Title and Content
│   ├── Slide Layout: Section Header
│   ├── Slide Layout: Two Content
│   ├── Slide Layout: Blank
│   └── Slide Layout: Custom Layout ...
└── Slides
    └── Each slide references one layout
```

**Inheritance chain:** Theme → Slide Master → Slide Layout → Individual Slide. Properties set lower in the chain override those set higher. A color defined on the slide master is inherited by all layouts unless explicitly overridden.

### Layout Placeholders

Each layout defines placeholder positions, sizes, and types. When you add a slide from a layout, you get that layout's placeholders.

```python
from pptx import Presentation

prs = Presentation('company_template.pptx')
for idx, layout in enumerate(prs.slide_master.slide_layouts):
    print(f"Layout {idx}: {layout.name}")
    for ph in layout.placeholders:
        print(f"  Placeholder {ph.placeholder_format.idx}: {ph.name} ({ph.placeholder_format.type})")
```

---

## Theme Elements

A PPTX theme (`theme1.xml`) controls three categories:

### Color Scheme

| Slot | Purpose | Typical Mapping |
|---|---|---|
| dk1 | Dark 1 | Primary text (black/dark gray) |
| lt1 | Light 1 | Background (white) |
| dk2 | Dark 2 | Secondary text |
| lt2 | Light 2 | Secondary background |
| accent1-6 | Accent colors | Brand palette, chart colors |
| hlink | Hyperlink | Link color |
| folHlink | Followed hyperlink | Visited link color |

### Font Scheme

```xml
<a:fontScheme name="Corporate">
  <a:majorFont>
    <a:latin typeface="Inter"/>    <!-- Headings -->
  </a:majorFont>
  <a:minorFont>
    <a:latin typeface="Inter"/>    <!-- Body text -->
  </a:minorFont>
</a:fontScheme>
```

### Effect Scheme

Effects (shadows, reflections, 3D) are defined at the theme level. Keep them minimal for corporate use.

---

## Creating Reusable Templates (Python)

### Start from an Existing Template

```python
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RgbColor
from pptx.enum.text import PP_ALIGN

# Load a designed template with correct masters
prs = Presentation('brand_template.pptx')

# Verify available layouts
for idx, layout in enumerate(prs.slide_master.slide_layouts):
    print(f"{idx}: {layout.name}")

# Use branded layouts
title_slide = prs.slides.add_slide(prs.slide_layouts[0])
title_slide.shapes.title.text = "Q4 Business Review"
title_slide.placeholders[1].text = "December 2025"

content_slide = prs.slides.add_slide(prs.slide_layouts[1])
content_slide.shapes.title.text = "Revenue Summary"
body = content_slide.placeholders[1]
body.text = "Total revenue: $4.2M"

prs.save('branded_output.pptx')
```

### Set Theme Colors via XML

python-pptx does not expose theme color modification through its API. Use XML manipulation:

```python
from pptx import Presentation
from lxml import etree
from pptx.oxml.ns import qn

prs = Presentation()
theme = prs.slide_master.element.find(qn('p:cSld')).getparent()

# Access the theme XML (stored in the theme part)
theme_part = prs.slide_master.part.slide_master.theme_part
theme_element = theme_part._element

# Find the color scheme
clrScheme = theme_element.find('.//' + qn('a:clrScheme'))

# Update accent1 to brand blue
accent1 = clrScheme.find(qn('a:accent1'))
srgbClr = accent1.find(qn('a:srgbClr'))
if srgbClr is not None:
    srgbClr.set('val', '0066CC')

prs.save('themed.pptx')
```

### Set Default Font Sizes

```python
from pptx import Presentation
from pptx.util import Pt

prs = Presentation('brand_template.pptx')
slide = prs.slides.add_slide(prs.slide_layouts[1])

# Title formatting
title = slide.shapes.title
title.text = "Section Title"
for paragraph in title.text_frame.paragraphs:
    paragraph.font.size = Pt(28)
    paragraph.font.bold = True
    paragraph.font.color.rgb = RgbColor(0x1A, 0x1A, 0x2E)

# Body formatting
body = slide.placeholders[1]
for paragraph in body.text_frame.paragraphs:
    paragraph.font.size = Pt(16)
    paragraph.font.color.rgb = RgbColor(0x33, 0x33, 0x33)
```

---

## Branded Master Slides (PptxGenJS)

```typescript
import pptxgen from 'pptxgenjs';

const pptx = new pptxgen();

// Define brand master with logo, header bar, and footer
pptx.defineSlideMaster({
  title: 'BRAND_STANDARD',
  background: { color: 'FFFFFF' },
  objects: [
    // Top brand bar
    { rect: { x: 0, y: 0, w: '100%', h: 0.6, fill: { color: '1A1A2E' } } },
    // Logo
    { image: { x: 0.3, y: 0.08, w: 1.2, h: 0.44, path: './assets/logo-white.png' } },
    // Bottom rule
    { rect: { x: 0, y: 5.35, w: '100%', h: 0.02, fill: { color: '0066CC' } } },
    // Footer text
    { text: {
      text: 'Confidential | Company Inc.',
      options: { x: 0.3, y: 5.4, w: 5, h: 0.25, fontSize: 8, color: '999999' }
    }},
    // Slide number
    { text: {
      text: '{slideNumber}',
      options: { x: 9.2, y: 5.4, w: 0.5, h: 0.25, fontSize: 8, color: '999999', align: 'right' }
    }},
  ],
});

// Section divider master
pptx.defineSlideMaster({
  title: 'SECTION_DIVIDER',
  background: { color: '1A1A2E' },
  objects: [
    { image: { x: 0.3, y: 0.3, w: 1.5, h: 0.55, path: './assets/logo-white.png' } },
    { rect: { x: 2, y: 2.7, w: 6, h: 0.03, fill: { color: '0066CC' } } },
  ],
});

// Use masters
const slide1 = pptx.addSlide({ masterName: 'SECTION_DIVIDER' });
slide1.addText('Market Analysis', { x: 2, y: 2, w: 6, fontSize: 36, color: 'FFFFFF' });

const slide2 = pptx.addSlide({ masterName: 'BRAND_STANDARD' });
slide2.addText('TAM: $12B', { x: 1, y: 1.2, w: 8, fontSize: 24, bold: true });

await pptx.writeFile({ fileName: 'branded.pptx' });
```

---

## PPTX-Automizer for Branded Templates

PPTX-Automizer copies slides from branded template files while preserving all master/layout references.

```typescript
import Automizer from 'pptx-automizer';

const automizer = new Automizer({
  templateDir: './templates',
  outputDir: './output',
});

const pptx = automizer
  .loadRoot('branded-base.pptx')          // Contains master slides and theme
  .load('data-slides.pptx', 'data');      // Contains content slides

// Slides inherit the branded-base.pptx masters
pptx.addSlide('data', 1, (slide) => {
  slide.modifyElement('RevenueChart', {
    replaceChart: updatedChartData,
  });
  slide.modifyElement('QuarterLabel', { text: 'Q4 2025' });
});

pptx.addSlide('data', 2, (slide) => {
  slide.modifyElement('MetricsTable', { replaceTable: metricsData });
});

await pptx.write('quarterly_report.pptx');
```

**Key advantage:** Designers maintain the template in PowerPoint. Engineers inject data with Automizer. Branding stays pixel-perfect.

---

## Template Versioning and Distribution

### Version Control Strategy

```text
templates/
├── v2.1/
│   ├── brand-standard.pptx      ← Current production template
│   ├── brand-standard.potx      ← PowerPoint template format
│   └── CHANGELOG.md
├── v2.0/
│   └── brand-standard.pptx      ← Previous version (archived)
└── assets/
    ├── logo-dark.png
    ├── logo-white.png
    └── brand-colors.json
```

### Distribution Approaches

| Method | Pros | Cons |
|---|---|---|
| Shared drive / cloud folder | Simple, accessible | No version enforcement |
| Git LFS | Versioned, auditable | Requires dev tooling |
| Template server API | Programmatic access, always current | Requires infrastructure |
| PowerPoint custom template path | Native Office integration | Manual installation per machine |

### brand-colors.json for Automation

```json
{
  "version": "2.1",
  "colors": {
    "primary": "1A1A2E",
    "secondary": "0066CC",
    "accent": "FF6600",
    "text_dark": "333333",
    "text_light": "FFFFFF",
    "background": "FFFFFF",
    "surface": "F5F5F5"
  },
  "fonts": {
    "heading": "Inter",
    "body": "Inter",
    "mono": "JetBrains Mono"
  }
}
```

---

## Multi-Brand Support

When supporting sub-brands or white-label variants:

```python
import json
from pptx import Presentation
from pptx.dml.color import RgbColor
from pptx.util import Pt

def load_brand(brand_name: str) -> dict:
    with open(f'brands/{brand_name}/brand-colors.json') as f:
        return json.load(f)

def apply_brand(prs: Presentation, brand: dict):
    """Apply brand colors to all slides in the presentation."""
    primary = brand['colors']['primary']
    for slide in prs.slides:
        if slide.shapes.title:
            for p in slide.shapes.title.text_frame.paragraphs:
                p.font.color.rgb = RgbColor(
                    int(primary[0:2], 16),
                    int(primary[2:4], 16),
                    int(primary[4:6], 16)
                )

# Usage
brand = load_brand('subsidiary-a')
prs = Presentation(f'brands/subsidiary-a/template.pptx')
apply_brand(prs, brand)
prs.save('output.pptx')
```

### Multi-Brand File Structure

```text
brands/
├── parent-co/
│   ├── template.pptx
│   ├── brand-colors.json
│   └── assets/
│       ├── logo-dark.png
│       └── logo-white.png
├── subsidiary-a/
│   ├── template.pptx       ← Inherits parent layout, different colors/logo
│   ├── brand-colors.json
│   └── assets/
└── white-label/
    ├── template.pptx       ← Neutral template, no branding
    └── brand-colors.json
```

---

## Brand Consistency Checklist

- [ ] Logo placement is identical on every non-title slide (position, size)
- [ ] Color palette uses only defined brand colors (no ad-hoc hex values)
- [ ] Heading font and body font match the brand font scheme
- [ ] Font sizes follow the hierarchy: title (28-36pt), subtitle (18-24pt), body (14-18pt), caption (10-12pt)
- [ ] Footer contains required legal text (confidential, copyright)
- [ ] Slide numbers are present and consistently positioned
- [ ] Chart colors map to the accent palette in the correct order
- [ ] Background color or gradient matches the brand specification
- [ ] No orphaned layouts from previous template versions
- [ ] Template version is documented in the file properties or a hidden slide

---

## Common Pitfalls

### Layout Index Assumptions

Layout indices vary between templates. Never hardcode layout index numbers.

```python
# BAD — breaks if template changes
layout = prs.slide_layouts[1]

# GOOD — look up by name
def get_layout(prs, name):
    for layout in prs.slide_master.slide_layouts:
        if layout.name == name:
            return layout
    raise ValueError(f"Layout '{name}' not found. Available: "
                     f"{[l.name for l in prs.slide_master.slide_layouts]}")

layout = get_layout(prs, 'Title and Content')
```

### Missing Placeholders

Templates may have fewer placeholders than expected. Always check before accessing.

```python
slide = prs.slides.add_slide(layout)

# BAD — KeyError if placeholder 1 does not exist
body = slide.placeholders[1]

# GOOD — safe access
if 1 in slide.placeholders:
    body = slide.placeholders[1]
    body.text = "Content here"
else:
    # Fall back to adding a text box
    from pptx.util import Inches
    txBox = slide.shapes.add_textbox(Inches(1), Inches(1.5), Inches(8), Inches(4))
    txBox.text_frame.text = "Content here"
```

### Font Substitution

If the brand font is not installed on the rendering machine, PowerPoint substitutes a default font. This breaks spacing and alignment.

**Mitigations:**

- Embed fonts in the PPTX (File > Options > Save > Embed fonts)
- Use widely available fonts (Inter, Open Sans, Roboto) as fallbacks
- Test on the target machine before the presentation
- For PDF export, fonts must be present at export time

### Theme Corruption

Editing `theme1.xml` incorrectly can corrupt the file. Always:

1. Back up the original template before XML edits
2. Validate the output opens cleanly in PowerPoint
3. Check that all 12 theme color slots are populated

---

## Do / Avoid

### Do

- Look up layouts by name, not by index
- Store brand configuration in a JSON file alongside templates
- Version your templates with clear changelogs
- Test generated files in PowerPoint on the target OS
- Use PPTX-Automizer when designers own the template and engineers own the data
- Validate placeholder existence before accessing
- Keep one canonical template per brand, not per-project copies

### Avoid

- Hardcoding layout indices (`slide_layouts[1]`)
- Defining colors as raw hex strings scattered through code (use a palette class or JSON)
- Editing slide master XML without a backup
- Assuming fonts are available on all machines
- Creating new layouts programmatically when a template layout already exists
- Mixing elements from different template versions in one deck
- Ignoring the theme color scheme and using only direct RGB overrides

---

## Related Resources

- [pptx-layouts.md](pptx-layouts.md) - Master slides, themes, and backgrounds
- [pptx-charts.md](pptx-charts.md) - Chart styling with brand colors
- [pptx-animations-transitions.md](pptx-animations-transitions.md) - Transitions and motion
- [../assets/pitch-deck.md](../assets/pitch-deck.md) - Complete pitch deck template
