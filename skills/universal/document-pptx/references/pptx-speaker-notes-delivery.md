# PPTX Speaker Notes & Delivery

Notes API reference for python-pptx and PptxGenJS, plus the delivery gotchas that don't fit the accessibility or troubleshooting references.

---

## Contents

- [Adding Speaker Notes (Python)](#adding-speaker-notes-python)
- [Adding Speaker Notes (PptxGenJS)](#adding-speaker-notes-pptxgenjs)
- [Extracting and Exporting Notes](#extracting-and-exporting-notes)
- [Delivery Gotchas](#delivery-gotchas)
- [Related Resources](#related-resources)

---

## Adding Speaker Notes (Python)

```python
from pptx import Presentation

prs = Presentation()
slide = prs.slides.add_slide(prs.slide_layouts[1])
slide.shapes.title.text = "Q4 Results"

notes_slide = slide.notes_slide
notes_tf = notes_slide.notes_text_frame
notes_tf.text = "Opening: Remind audience of Q3 target.\nKey stat: $4.2M revenue."

prs.save('with_notes.pptx')
```

Batch-setting notes across an existing deck:

```python
notes_map = {0: "Welcome...", 1: "Key metric: 42% conversion..."}
for idx, notes_text in notes_map.items():
    prs.slides[idx].notes_slide.notes_text_frame.text = notes_text
```

To extract notes back out (e.g. for a printed script), use `scripts/pptx_extract_notes.py` rather than re-implementing the read loop.

## Adding Speaker Notes (PptxGenJS)

```typescript
const slide = pptx.addSlide();
slide.addText('Market Opportunity', { x: 1, y: 1, fontSize: 32 });
slide.addNotes('TAM is $12B. We target the mid-market segment ($2B SAM).');
```

---

## Extracting and Exporting Notes

### Notes Pages PDF

PowerPoint's "Notes Page" layout (one slide per page, notes below) is an export setting, not something python-pptx controls. LibreOffice's Impress PDF export has an `ExportNotesPages` option; check the LibreOffice PDF export filter-options docs for the exact `--convert-to` syntax your installed version accepts, for example:

```bash
libreoffice --headless --convert-to pdf:"impress_pdf_Export:ExportNotesPages=true" deck.pptx
```

### Extract Notes to Text

Use [`scripts/pptx_extract_notes.py`](../scripts/pptx_extract_notes.py) rather than reimplementing extraction — it already handles empty notes slides and non-existent notes gracefully.

### Generate Speaker Script Markdown

```python
from pptx import Presentation

prs = Presentation('deck.pptx')
lines = ["# Speaker Script\n"]

for idx, slide in enumerate(prs.slides):
    title = slide.shapes.title.text if slide.shapes.title else f"Slide {idx + 1}"
    # has_notes_slide guard: reading slide.notes_slide creates an empty notes slide if none exists
    notes = slide.notes_slide.notes_text_frame.text.strip() if slide.has_notes_slide else ""
    lines.append(f"## Slide {idx + 1}: {title}\n")
    lines.append(f"{notes}\n" if notes else "_No notes._\n")

with open('speaker_script.md', 'w') as f:
    f.write('\n'.join(lines))
```

---

## Delivery Gotchas

- Estimate speaking time from notes word count divided by the presenter's own measured pace (time one rehearsed slide): `total_words = sum(len(s.notes_slide.notes_text_frame.text.split()) for s in prs.slides if s.has_notes_slide)`, then `total_words / words_per_minute`. It is a sanity check before rehearsal, not a substitute for it.
- Notes travel with the file and can be exported to PDF or handouts — never put confidential figures or negotiation floors in notes of a deck that will be shared.
- Presenter View's dual-monitor behavior varies by OS, app version and hardware; test on the actual presentation hardware, not just the authoring machine.
- Keep notes as bullet points and exact figures to cite, not a verbatim script — a script gets read aloud and the audience notices.

---

## Related Resources

- [pptx-layouts.md](pptx-layouts.md) - Master slides and themes
- [pptx-animations-transitions.md](pptx-animations-transitions.md) - Animations and transitions
- [pptx-accessibility-compliance.md](pptx-accessibility-compliance.md) - Accessibility checks and delivery context
- [../scripts/pptx_extract_notes.py](../scripts/pptx_extract_notes.py) - Notes extraction script
