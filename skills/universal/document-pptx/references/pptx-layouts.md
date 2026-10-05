# PPTX Layouts - Master Slides, Themes & Templates

Gotchas for PowerPoint layout customization with python-pptx and pptxgenjs. Full branding/theme workflow lives in [pptx-template-branding.md](pptx-template-branding.md).

---

## Gotchas

- **Default layout indices are not portable.** `prs.slide_layouts[N]` on a blank `Presentation()` maps to Office's default master (0=Title Slide, 1=Title and Content, 2=Section Header, 3=Two Content, 4=Comparison, 5=Title Only, 6=Blank, 7=Content with Caption, 8=Picture with Caption) — but a loaded `.pptx`/`.potx` template can reorder or rename these. Always resolve layouts by name:

```python
def get_layout_by_name(prs, wanted: str):
    for layout in prs.slide_master.slide_layouts:
        if layout.name == wanted:
            return layout
    available = [l.name for l in prs.slide_master.slide_layouts]
    raise ValueError(f"Layout '{wanted}' not found. Available: {available}")
```

- **python-pptx has no theme-color API** (see [pptx-template-branding.md](pptx-template-branding.md#theme-colors-via-xml) for the XML workaround and the `theme_part` attribute error to avoid).
- **python-pptx has no native gradient-fill API.** `slide.background.fill.solid()` works; gradients require direct XML manipulation.
- **Default slide sizes differ by library.** python-pptx's default template is 10 × 7.5 in (4:3); pptxgenjs defaults to 10 × 5.625 in (16:9). Positions copied from one to the other clip or leave dead space, so set the size explicitly (python-pptx: `prs.slide_width = Inches(10)`, `prs.slide_height = Inches(5.625)` for 16:9). Changing `prs.slide_width`/`prs.slide_height` after adding slides does not reflow existing shape positions — set size before adding content, or reposition shapes afterward. Common alternates: 16:9 at 13.333 × 7.5 in (pptxgenjs `LAYOUT_WIDE`, PowerPoint's Widescreen size); A4 portrait for print is `Inches(8.27), Inches(11.69)`.
- **pptxgenjs uses named layout presets** (`pptx.layout = 'LAYOUT_16x9' | 'LAYOUT_4x3' | 'LAYOUT_16x10' | 'LAYOUT_WIDE'`); for any other size, register one with `pptx.defineLayout({ name, width, height })` (inches) and assign its name. Set this before adding slides.
- **pptxgenjs master `objects` render in array order** — a background `rect` must precede a logo `image` entry in the array or the logo renders underneath it.

---

## Related Resources

- [pptx-charts.md](pptx-charts.md) - Chart styling and data binding
- [../assets/pitch-deck.md](../assets/pitch-deck.md) - Complete pitch deck
- [../assets/quarterly-review.md](../assets/quarterly-review.md) - Business review template
