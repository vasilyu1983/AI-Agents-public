# PPTX Speaker Notes & Delivery - Presenter-Side Content

Deep-dive resource for speaker notes, rehearsal workflow, and delivery preparation with python-pptx and PptxGenJS.

---

## Contents

- [Adding Speaker Notes (Python)](#adding-speaker-notes-python)
- [Adding Speaker Notes (PptxGenJS)](#adding-speaker-notes-pptxgenjs)
- [Notes Structure Template](#notes-structure-template)
- [Speaker Notes Best Practices](#speaker-notes-best-practices)
- [Presenter View Setup](#presenter-view-setup)
- [Exporting Notes and Handouts](#exporting-notes-and-handouts)
- [Rehearsal and Timing](#rehearsal-and-timing)
- [Do / Avoid](#do--avoid)
- [Pre-Presentation Delivery Checklist](#pre-presentation-delivery-checklist)
- [Related Resources](#related-resources)

---

## Adding Speaker Notes (Python)

```python
from pptx import Presentation
from pptx.util import Pt

prs = Presentation()
slide = prs.slides.add_slide(prs.slide_layouts[1])
slide.shapes.title.text = "Q4 Results"
slide.placeholders[1].text = "Revenue grew 22% YoY"

# Add speaker notes
notes_slide = slide.notes_slide
notes_tf = notes_slide.notes_text_frame
notes_tf.text = "Opening: Remind audience of Q3 target.\nKey stat: $4.2M revenue.\nTransition: Move to regional breakdown."

prs.save('with_notes.pptx')
```

### Rich-Formatted Notes

```python
from pptx.util import Pt
from pptx.dml.color import RgbColor

notes_slide = slide.notes_slide
notes_tf = notes_slide.notes_text_frame

# Clear default paragraph and build formatted notes
notes_tf.clear()

p = notes_tf.paragraphs[0]
run = p.add_run()
run.text = "KEY POINT: "
run.font.bold = True
run.font.size = Pt(12)

run2 = p.add_run()
run2.text = "Revenue exceeded forecast by 8%."
run2.font.size = Pt(12)

# Add a second paragraph
p2 = notes_tf.add_paragraph()
p2.text = "If asked about margins, defer to slide 7."
p2.font.size = Pt(11)
p2.font.italic = True
```

### Batch-Add Notes from a Dictionary

```python
from pptx import Presentation

prs = Presentation('existing_deck.pptx')

# Map slide index to notes content
notes_map = {
    0: "Welcome the audience. Introduce yourself and the agenda.",
    1: "Key metric: 42% conversion rate. Compare to industry avg 28%.",
    2: "Transition: 'Now let's look at what's driving this growth.'",
    3: "Close with the ask: Series A terms on slide 5.",
}

for idx, notes_text in notes_map.items():
    slide = prs.slides[idx]
    notes_slide = slide.notes_slide
    notes_slide.notes_text_frame.text = notes_text

prs.save('deck_with_notes.pptx')
```

---

## Adding Speaker Notes (PptxGenJS)

```typescript
import pptxgen from 'pptxgenjs';

const pptx = new pptxgen();

const slide = pptx.addSlide();
slide.addText('Market Opportunity', { x: 1, y: 1, fontSize: 32 });

// Add speaker notes as a string
slide.addNotes('TAM is $12B. We target the mid-market segment ($2B SAM).\nPause here for questions.');

// Multi-slide notes pattern
const slidesData = [
  { title: 'Problem', notes: 'Start with the customer pain point story from Acme Corp.' },
  { title: 'Solution', notes: 'Demo video is 90 seconds. Cue it before advancing.' },
  { title: 'Traction', notes: 'Emphasize MoM growth. If asked about churn, see appendix.' },
];

for (const data of slidesData) {
  const s = pptx.addSlide();
  s.addText(data.title, { x: 1, y: 1, fontSize: 28 });
  s.addNotes(data.notes);
}

await pptx.writeFile({ fileName: 'deck_with_notes.pptx' });
```

---

## Notes Structure Template

Use a consistent structure for every slide's notes. This keeps delivery smooth and rehearsal predictable.

```text
[OPENING] — Hook or transition from previous slide
  "As we saw in the pipeline data..."

[KEY POINTS] — 2-3 bullets, not sentences
  • Revenue: $4.2M (+22% YoY)
  • Top driver: Enterprise segment
  • Risk: APAC slowdown in Q1

[DATA CUE] — Specific numbers to reference
  Exact figure: $4,217,000
  Comparison: Q3 was $3,460,000

[TRANSITION] — Bridge to next slide
  "Let's look at how this breaks down by region."

[TIME CHECK] — Target time at this point
  ⏱ Should be at ~4:00 of 15:00
```

---

## Speaker Notes Best Practices

### Write Key Points, Not Scripts

- Notes are a safety net, not a teleprompter
- 3-5 bullet points per slide maximum
- Include exact numbers you might forget under pressure
- Write transition phrases verbatim — these are the hardest to improvise

### Include Audience Cues

- "PAUSE for questions here"
- "Check room energy — if low, use the Acme story"
- "This slide is optional — skip if running over 12 min"
- "CLICK to advance build animation before speaking"

### Timing Markers

- Add cumulative time targets: "⏱ 5:00 / 20:00"
- Flag slides that tend to run long: "WARNING: This slide eats time. Stay under 2 min."
- Mark optional slides: "SKIP if under 5 min remaining"

---

## Presenter View Setup

Presenter View shows notes on the presenter's screen while the audience sees only slides.

### Enabling Presenter View

| Platform | How to Enable |
|---|---|
| PowerPoint (Windows) | Slide Show > Use Presenter View (check box) |
| PowerPoint (Mac) | Slide Show > Presenter View |
| Google Slides | Present > Presenter View (dropdown arrow) |
| Keynote | Play > Presenter Display > Customize |

### Presenter View Features

- Current slide and next slide preview
- Speaker notes panel (resizable)
- Elapsed time and clock
- Slide navigation thumbnails
- Zoom into current slide
- Black/white screen toggle (B or W key)

### Keyboard Shortcuts During Presentation

| Action | Key |
|---|---|
| Next slide | Right arrow, Space, Enter, N |
| Previous slide | Left arrow, Backspace, P |
| Go to slide N | Type number + Enter |
| Black screen | B |
| White screen | W |
| End show | Esc |
| Toggle pointer | Ctrl+P (Windows), Cmd+P (Mac) |

---

## Exporting Notes and Handouts

### Notes Pages (Python)

PowerPoint's "Notes Page" layout prints one slide per page with notes below. This is controlled via print settings, not python-pptx. To generate a notes-included PDF:

```bash
# macOS — use LibreOffice headless to export with notes
libreoffice --headless --convert-to pdf:"impress_pdf_Export:ExportNotesPages=true" deck.pptx
```

### Extract Notes to Text

```python
from pptx import Presentation

prs = Presentation('deck.pptx')

for idx, slide in enumerate(prs.slides):
    notes_slide = slide.notes_slide
    notes_text = notes_slide.notes_text_frame.text
    if notes_text.strip():
        print(f"--- Slide {idx + 1} ---")
        print(notes_text)
        print()
```

### Generate Speaker Script Markdown

```python
from pptx import Presentation

prs = Presentation('deck.pptx')
lines = ["# Speaker Script\n"]

for idx, slide in enumerate(prs.slides):
    title = slide.shapes.title.text if slide.shapes.title else f"Slide {idx + 1}"
    notes = slide.notes_slide.notes_text_frame.text.strip()
    lines.append(f"## Slide {idx + 1}: {title}\n")
    lines.append(f"{notes}\n" if notes else "_No notes._\n")

with open('speaker_script.md', 'w') as f:
    f.write('\n'.join(lines))
```

---

## Rehearsal and Timing

### Rehearsal Workflow

1. **First pass:** Read notes aloud, slide by slide. Record total time.
2. **Trim pass:** Cut any note that you naturally remember. Keep only what you forget.
3. **Timing pass:** Add time markers after measuring your natural pace.
4. **Dry run:** Present to a colleague using Presenter View. Get feedback on pacing.
5. **Final notes edit:** Update based on dry run. Remove anything you no longer need.

### Timing Rules of Thumb

| Content Type | Time per Slide |
|---|---|
| Title / section divider | 15-30 seconds |
| Key message with build | 1-2 minutes |
| Data-heavy chart | 2-3 minutes |
| Demo or video | Actual runtime + 30s buffer |
| Q&A prompt | 3-5 minutes |

### Programmatic Timing Validation

```python
# Estimate presentation duration from notes word count
from pptx import Presentation

prs = Presentation('deck.pptx')
total_words = 0
for slide in prs.slides:
    notes = slide.notes_slide.notes_text_frame.text
    total_words += len(notes.split())

# Average speaking pace: 130 words per minute
estimated_minutes = total_words / 130
print(f"Estimated speaking time: {estimated_minutes:.1f} minutes")
print(f"Slide count: {len(prs.slides)}")
print(f"Average words per slide: {total_words / len(prs.slides):.0f}")
```

---

## Do / Avoid

### Do

- Write notes as bullet points, not full paragraphs
- Include exact data points you need to cite verbally
- Add transition phrases between slides
- Put timing markers on every 3rd-4th slide
- Test Presenter View on the actual presentation hardware
- Export a speaker script for backup (phone or printout)

### Avoid

- Writing a word-for-word script (you will read it, and the audience will notice)
- Leaving notes empty on data slides where you need exact figures
- Assuming Presenter View will work without testing (dual monitor setup varies)
- Putting confidential information in notes (they export with handouts)
- Using notes as a dumping ground for cut slide content
- Skipping rehearsal because "I know this material"

---

## Pre-Presentation Delivery Checklist

- [ ] All slides have speaker notes (no blanks on data slides)
- [ ] Notes contain timing markers at regular intervals
- [ ] Total estimated time fits the allotted slot (with 10% buffer)
- [ ] Presenter View tested on target hardware
- [ ] Backup copy of notes exported as text or PDF
- [ ] Font rendering verified on presentation machine
- [ ] Slide clicker / remote tested
- [ ] Video and audio clips tested for playback
- [ ] Screen resolution matches slide aspect ratio (16:9 vs 4:3)
- [ ] Confidence monitor or podium screen confirmed with AV team

---

## Related Resources

- [pptx-layouts.md](pptx-layouts.md) - Master slides and themes
- [pptx-animations-transitions.md](pptx-animations-transitions.md) - Animations and transitions
- [../assets/pitch-deck.md](../assets/pitch-deck.md) - Complete pitch deck template
- [../assets/quarterly-review.md](../assets/quarterly-review.md) - Business review template
