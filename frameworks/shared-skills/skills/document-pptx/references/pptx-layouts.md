# PPTX Layouts - Master Slides, Themes & Templates

Deep-dive resource for PowerPoint layout customization with python-pptx and pptxgenjs.

---

## Contents

- [Master Slide Architecture](#master-slide-architecture)
- [Access Slide Masters (Python)](#access-slide-masters-python)
- [Custom Theme Colors](#custom-theme-colors)
- [Brand Color Palette Pattern](#brand-color-palette-pattern)
- [Use Existing Template](#use-existing-template)
- [Custom Placeholder Positions](#custom-placeholder-positions)
- [Node.js Theme Configuration](#nodejs-theme-configuration)
- [Slide Size Presets](#slide-size-presets)
- [Background Patterns](#background-patterns)
- [Related Resources](#related-resources)

---

## Master Slide Architecture

PowerPoint uses a three-level hierarchy:

```text
Slide Master (top level)
├── Slide Layouts (mid level) - Title, Content, Blank, etc.
└── Individual Slides (bottom level) - Your actual content
```

Changes to the Slide Master cascade down to all layouts and slides.

---

## Access Slide Masters (Python)

```python
from pptx import Presentation

prs = Presentation()

# Access the first slide master
slide_master = prs.slide_master

# List all available layouts
for idx, layout in enumerate(slide_master.slide_layouts):
    print(f"{idx}: {layout.name}")
```

**Default Layout Names:**
| Index | Name | Placeholders |
|-------|------|--------------|
| 0 | Title Slide | title, subtitle |
| 1 | Title and Content | title, body |
| 2 | Section Header | title, subtitle |
| 3 | Two Content | title, body (left), body (right) |
| 4 | Comparison | title, body x4 |
| 5 | Title Only | title |
| 6 | Blank | none |
| 7 | Content with Caption | body, title, text |
| 8 | Picture with Caption | picture, title, text |

---

## Custom Theme Colors

```python
from pptx import Presentation
from pptx.dml.color import RgbColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.util import Inches, Pt

prs = Presentation()
slide = prs.slides.add_slide(prs.slide_layouts[6])  # Blank

# Access theme colors via shape formatting (fill/line)
shape = slide.shapes.add_shape(
    MSO_SHAPE.RECTANGLE,
    Inches(1), Inches(1), Inches(2), Inches(1)
)

# Set fill color
fill = shape.fill
fill.solid()
fill.fore_color.rgb = RgbColor(0x00, 0x66, 0xCC)  # Brand blue

# Set line color
line = shape.line
line.color.rgb = RgbColor(0x00, 0x33, 0x66)
line.width = Pt(2)
```

---

## Brand Color Palette Pattern

```python
from pptx.dml.color import RgbColor

class BrandColors:
    PRIMARY = RgbColor(0x00, 0x66, 0xCC)      # #0066CC
    SECONDARY = RgbColor(0x00, 0x99, 0xFF)    # #0099FF
    ACCENT = RgbColor(0xFF, 0x66, 0x00)       # #FF6600
    DARK = RgbColor(0x33, 0x33, 0x33)         # #333333
    LIGHT = RgbColor(0xF5, 0xF5, 0xF5)        # #F5F5F5
    SUCCESS = RgbColor(0x28, 0xA7, 0x45)      # #28A745
    WARNING = RgbColor(0xFF, 0xC1, 0x07)      # #FFC107
    DANGER = RgbColor(0xDC, 0x35, 0x45)       # #DC3545
```

---

## Use Existing Template

```python
from pptx import Presentation

# Load template with custom master slides
prs = Presentation('company_template.pptx')

# Use template's layouts
title_layout = prs.slide_layouts[0]
content_layout = prs.slide_layouts[1]

# Add slides using template layouts
slide = prs.slides.add_slide(title_layout)
slide.shapes.title.text = "Uses Template Styling"

prs.save('branded_presentation.pptx')
```

---

## Custom Placeholder Positions

```python
from pptx import Presentation
from pptx.util import Inches, Pt

prs = Presentation()

# Blank layout for full control
blank_layout = prs.slide_layouts[6]
slide = prs.slides.add_slide(blank_layout)

# Custom title position
title_box = slide.shapes.add_textbox(
    Inches(0.5), Inches(0.3),  # x, y
    Inches(9), Inches(0.8)     # width, height
)
title_frame = title_box.text_frame
title_frame.paragraphs[0].text = "Custom Positioned Title"
title_frame.paragraphs[0].font.size = Pt(36)
title_frame.paragraphs[0].font.bold = True

# Custom content area
content_box = slide.shapes.add_textbox(
    Inches(0.5), Inches(1.5),
    Inches(9), Inches(5)
)
```

---

## Node.js Theme Configuration

```typescript
import pptxgen from 'pptxgenjs';

const pptx = new pptxgen();

// Set presentation metadata
pptx.author = 'Company Name';
pptx.company = 'Company Name';
pptx.subject = 'Quarterly Report';
pptx.title = 'Q4 2025 Business Review';

// Define master slide
pptx.defineSlideMaster({
  title: 'BRANDED_SLIDE',
  background: { color: 'FFFFFF' },
  objects: [
    // Header bar
    { rect: { x: 0, y: 0, w: '100%', h: 0.75, fill: { color: '0066CC' } } },
    // Logo placeholder
    { image: { x: 0.3, y: 0.1, w: 1.5, h: 0.5, path: 'logo.png' } },
    // Footer
    { text: {
      text: 'Confidential',
      options: { x: 0.3, y: 5.2, w: 2, h: 0.3, fontSize: 8, color: '666666' }
    }},
    // Page number
    { text: {
      text: 'Slide {slideNumber}',
      options: { x: 8.5, y: 5.2, w: 1, h: 0.3, fontSize: 8, color: '666666' }
    }},
  ],
  slideNumber: { x: 9.0, y: 5.2, fontSize: 8, color: '666666' },
});

// Use custom master
const slide = pptx.addSlide({ masterName: 'BRANDED_SLIDE' });
```

---

## Slide Size Presets

```python
from pptx.util import Inches

# Standard 16:9 (default)
# Width: 10 inches, Height: 5.625 inches

# Standard 4:3
prs.slide_width = Inches(10)
prs.slide_height = Inches(7.5)

# Widescreen 16:10
prs.slide_width = Inches(10)
prs.slide_height = Inches(6.25)

# A4 Portrait (for print)
prs.slide_width = Inches(8.27)
prs.slide_height = Inches(11.69)
```

```typescript
// pptxgenjs
const pptx = new pptxgen();
pptx.layout = 'LAYOUT_16x9';  // or 'LAYOUT_4x3', 'LAYOUT_16x10', 'LAYOUT_WIDE'
```

---

## Background Patterns

```python
from pptx import Presentation
from pptx.dml.color import RgbColor

# Solid color background
prs = Presentation()
slide = prs.slides.add_slide(prs.slide_layouts[6])
background = slide.background
fill = background.fill
fill.solid()
fill.fore_color.rgb = RgbColor(0xF0, 0xF0, 0xF0)

# Gradient backgrounds require XML manipulation (python-pptx doesn't have native gradient support).
```

```typescript
// pptxgenjs gradient background
slide.background = {
  color: '0066CC',
  // or gradient
  // fill: { type: 'solid', color: '0066CC' }
};
```

---

## Related Resources

- [pptx-charts.md](pptx-charts.md) - Chart styling and data binding
- [../assets/pitch-deck.md](../assets/pitch-deck.md) - Complete pitch deck
- [../assets/quarterly-review.md](../assets/quarterly-review.md) - Business review template
