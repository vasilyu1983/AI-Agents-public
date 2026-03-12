# PPTX Animations & Transitions - Motion in Presentations

Deep-dive resource for slide transitions and build animations across python-pptx, PptxGenJS, and PPTX-Automizer.

---

## Contents

- [Library Support Matrix](#library-support-matrix)
- [Slide Transitions](#slide-transitions)
- [PptxGenJS Transition Examples](#pptxgenjs-transition-examples)
- [Build Animations](#build-animations)
- [python-pptx XML Approach for Animations](#python-pptx-xml-approach-for-animations)
- [PPTX-Automizer: Preserving Existing Animations](#pptx-automizer-preserving-existing-animations)
- [When to Use Animations](#when-to-use-animations)
- [Accessibility Concerns](#accessibility-concerns)
- [Do / Avoid](#do--avoid)
- [Related Resources](#related-resources)

---

## Library Support Matrix

| Capability | python-pptx | PptxGenJS | PPTX-Automizer |
|---|---|---|---|
| Slide transitions | No native API; XML manipulation required | Native `transition` option on slides | Preserves transitions from source slides |
| Build animations (appear, fade) | No API; raw OOXML only | Not supported | Preserves existing animations on copied slides |
| Custom motion paths | Raw OOXML only | Not supported | Preserves if present in template |
| Timing / auto-advance | XML manipulation | `advanceAfter` option | Preserves source timing |

**Key takeaway:** PptxGenJS is the simplest path for transitions. For build animations, design them in PowerPoint first and use PPTX-Automizer to inject data while keeping animations intact. python-pptx requires direct XML work.

---

## Slide Transitions

### Transition Types (OOXML)

| Transition | OOXML Element | Notes |
|---|---|---|
| Fade | `<p:fade>` | Smooth, safe default |
| Push | `<p:push dir="l">` | Directional (l, r, u, d) |
| Wipe | `<p:wipe dir="d">` | Directional reveal |
| Cover / Uncover | `<p:cover>` / `<p:uncover>` | Overlay motion |
| Split | `<p:split orient="horz">` | Horizontal or vertical |
| Cut | `<p:cut>` | Instant, no animation |
| None | omit `<p:transition>` | Default behavior |

### Timing Options

```xml
<!-- Auto-advance after 3 seconds, 500ms transition duration -->
<p:transition spd="med" advTm="3000">
  <p:fade />
</p:transition>
```

- `spd`: `slow` (1000ms), `med` (750ms), `fast` (500ms)
- `advTm`: auto-advance in milliseconds (omit for click-to-advance)
- `advClick`: set to `0` to disable click advance when using auto-advance

---

## PptxGenJS Transition Examples

```typescript
import pptxgen from 'pptxgenjs';

const pptx = new pptxgen();

// Slide with fade transition
const slide1 = pptx.addSlide();
slide1.addText('Introduction', { x: 1, y: 1, fontSize: 32 });
slide1.transition = {
  type: 'fade',
  speed: 1.0,       // seconds
  advanceAfter: 5000 // auto-advance after 5s (omit for manual)
};

// Slide with push transition
const slide2 = pptx.addSlide();
slide2.addText('Key Findings', { x: 1, y: 1, fontSize: 32 });
slide2.transition = {
  type: 'push',
  speed: 0.5,
  dir: 'l'  // push from left
};

// Kiosk-style auto-advancing deck
const kioskSlide = pptx.addSlide();
kioskSlide.addText('Auto-play slide', { x: 1, y: 2, fontSize: 24 });
kioskSlide.transition = {
  type: 'fade',
  speed: 0.75,
  advanceAfter: 4000
};

await pptx.writeFile({ fileName: 'transitions.pptx' });
```

### Available PptxGenJS Transition Types

`fade`, `push`, `wipe`, `zoom`, `split`, `cover`, `uncover`, `cut`, `random`, `none`

---

## Build Animations

Build animations reveal slide elements sequentially (bullet points appearing one at a time, chart series fading in). PowerPoint uses the `<p:timing>` tree inside each slide's XML.

### Animation Types

| Effect | OOXML Preset | Use Case |
|---|---|---|
| Appear | `anim_appear` | Instant reveal, no motion |
| Fade | `anim_fade` | Subtle entrance |
| Fly In | `anim_flyIn` | Directional entrance (from bottom, left, etc.) |
| Wipe | `anim_wipe` | Progressive reveal for charts |
| Grow & Turn | `anim_growTurn` | Emphasis on icons or callouts |

### Animation Sequence Concepts

```text
Slide Timing Tree
├── Build sequence 1 (on click)
│   ├── Shape A → Fade In (duration 500ms)
│   └── Shape B → Fade In (delay 200ms after A)
├── Build sequence 2 (on click)
│   └── Chart → Wipe by series
└── Exit sequence (on click)
    └── Shape A → Fade Out
```

---

## python-pptx XML Approach for Animations

python-pptx has no animation API. Manipulate the slide's `<p:timing>` element directly.

```python
from pptx import Presentation
from pptx.oxml.ns import qn
from lxml import etree

prs = Presentation()
slide = prs.slides.add_slide(prs.slide_layouts[1])

# Add a text shape that we want to animate
title = slide.shapes.title
title.text = "Animated Title"
body = slide.placeholders[1]
body.text = "This appears on click"

# Get the shape's spTree ID for targeting
body_sp = body._element
shape_id = body_sp.attrib.get('id', body_sp.find(qn('p:nvSpPr')).find(qn('p:cNvPr')).attrib['id'])

# Build the timing XML for a fade-in animation
timing_xml = f'''
<p:timing xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"
          xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">
  <p:tnLst>
    <p:par>
      <p:cTn id="1" dur="indefinite" restart="never" nodeType="tmRoot">
        <p:childTnLst>
          <p:seq concurrent="1" nextAc="seek">
            <p:cTn id="2" dur="indefinite" nodeType="mainSeq">
              <p:childTnLst>
                <p:par>
                  <p:cTn id="3" fill="hold">
                    <p:stCondLst>
                      <p:cond delay="0"/>
                    </p:stCondLst>
                    <p:childTnLst>
                      <p:par>
                        <p:cTn id="4" fill="hold">
                          <p:stCondLst>
                            <p:cond delay="0"/>
                          </p:stCondLst>
                          <p:childTnLst>
                            <p:set>
                              <p:cBhvr>
                                <p:cTn id="5" dur="1" fill="hold">
                                  <p:stCondLst>
                                    <p:cond delay="0"/>
                                  </p:stCondLst>
                                </p:cTn>
                                <p:tgtEl>
                                  <p:spTgt spid="{shape_id}"/>
                                </p:tgtEl>
                                <p:attrNameLst>
                                  <p:attrName>style.visibility</p:attrName>
                                </p:attrNameLst>
                              </p:cBhvr>
                              <p:to><p:strVal val="visible"/></p:to>
                            </p:set>
                          </p:childTnLst>
                        </p:cTn>
                      </p:par>
                    </p:childTnLst>
                  </p:cTn>
                </p:par>
              </p:childTnLst>
            </p:cTn>
            <p:prevCondLst>
              <p:cond evt="onPrev" delay="0">
                <p:tgtEl><p:sldTgt/></p:tgtEl>
              </p:cond>
            </p:prevCondLst>
            <p:nextCondLst>
              <p:cond evt="onClick" delay="0">
                <p:tgtEl><p:sldTgt/></p:tgtEl>
              </p:cond>
            </p:nextCondLst>
          </p:seq>
        </p:childTnLst>
      </p:cTn>
    </p:par>
  </p:tnLst>
</p:timing>
'''

timing_element = etree.fromstring(timing_xml)
slide._element.append(timing_element)

prs.save('animated.pptx')
```

**Warning:** This XML is fragile. Test output in PowerPoint after every change. Consider designing animations in PowerPoint and using PPTX-Automizer to merge content instead.

---

## PPTX-Automizer: Preserving Existing Animations

PPTX-Automizer copies slides from template files, keeping all animations and transitions intact.

```typescript
import Automizer from 'pptx-automizer';

const automizer = new Automizer({
  templateDir: './templates',
  outputDir: './output',
});

const pptx = automizer
  .loadRoot('base.pptx')
  .load('animated-template.pptx', 'animated');

// Copy slide 2 from animated template — all animations are preserved
pptx.addSlide('animated', 2, (slide) => {
  slide.modifyElement('TitlePlaceholder', { text: 'Updated Title' });
  slide.modifyElement('DataTable', { replaceTable: updatedTableData });
});

await pptx.write('output.pptx');
```

**Workflow:** Design animations in PowerPoint, save as template, use Automizer to swap data. Animations stay intact.

---

## When to Use Animations

### Good Uses

- **Progressive disclosure:** Reveal complex diagrams step by step so the audience follows your logic
- **Data storytelling:** Animate chart series to show growth over time
- **Agenda navigation:** Highlight the current section in a recurring agenda slide
- **Before/after reveals:** Show the "after" state on click for impact

### When to Skip

- **Dense data slides:** Animations slow down comprehension when the audience needs to scan
- **Printed or exported decks:** Animations are invisible in PDF exports
- **Kiosk / self-service:** Auto-play timing is hard to calibrate for varied reading speeds
- **Accessibility-first contexts:** Screen readers and reduced-motion users get no benefit

---

## Accessibility Concerns

- **Reduced motion:** Users with vestibular disorders rely on OS-level "reduce motion" preferences. PPTX files do not honor `prefers-reduced-motion`. Provide a static version of any animated deck.
- **Screen readers:** Animations are invisible to screen readers. Ensure all content makes sense without animation sequence.
- **Flashing content:** Avoid rapid flashing (3+ flashes per second). This can trigger photosensitive seizures. WCAG 2.3.1 applies.
- **Auto-advance timing:** If using auto-advance, set generous timing (5s+ per bullet point) or provide manual override instructions.
- **Alt text:** Animated elements still need alt text. Animations do not replace descriptive text.

---

## Do / Avoid

### Do

- Use fade for most transitions — it is unobtrusive and professional
- Apply consistent transition type across the entire deck
- Build bullet points one at a time for persuasive presentations
- Design animations in PowerPoint, then inject data with Automizer
- Test the final file in PowerPoint (not just a viewer) to verify timing
- Provide a non-animated PDF export for distribution

### Avoid

- Mixing multiple transition types on adjacent slides
- Using fly-in, bounce, or spin effects in business presentations
- Adding animations purely for decoration
- Relying on auto-advance without a manual fallback
- Using python-pptx XML animation hacks in production without thorough QA
- Assuming animations work in Google Slides or Keynote imports

---

## Related Resources

- [pptx-layouts.md](pptx-layouts.md) - Master slides and themes
- [pptx-charts.md](pptx-charts.md) - Chart styling and data binding
- [../assets/pitch-deck.md](../assets/pitch-deck.md) - Complete pitch deck template
