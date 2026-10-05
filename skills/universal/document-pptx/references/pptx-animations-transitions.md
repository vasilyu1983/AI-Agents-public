# PPTX Animations & Transitions - Motion in Presentations

Deep-dive resource for slide transitions and build animations across python-pptx, PptxGenJS, and PPTX-Automizer.

---

## Contents

- [Library Support Matrix](#library-support-matrix)
- [Slide Transitions](#slide-transitions)
- [python-pptx XML Approach for Slide Transitions](#python-pptx-xml-approach-for-slide-transitions)
- [Build Animations](#build-animations)
- [PPTX-Automizer: Best-Effort Animation Retention](#pptx-automizer-best-effort-animation-retention)
- [Accessibility Concerns](#accessibility-concerns)
- [Do / Avoid](#do--avoid)
- [Related Resources](#related-resources)

---

## Library Support Matrix

| Capability | python-pptx | PptxGenJS | PPTX-Automizer |
|---|---|---|---|
| Slide transitions | No native API; XML manipulation required | **No transition API** — its published types (`types/index.d.ts`) have no `slide.transition` property; re-check the current types before relying on this | Can keep source-slide transitions when slides are copied unchanged |
| Build animations (appear, fade) | No API; raw OOXML only | Not supported | No animation API; copied slides may retain existing animations, but edits can break them |
| Custom motion paths | Raw OOXML only | Not supported | Best-effort retention only when the animated shapes remain structurally unchanged |
| Timing / auto-advance | XML manipulation | Not supported (no `advanceAfter` option) | Best-effort retention from the source slide |

**Key takeaway:** none of these three libraries has a native transition or animation-authoring API (check each library's current type definitions if in doubt). Do not generate code that sets `slide.transition` or `advanceAfter` — pptxgenjs silently ignores unknown properties rather than erroring, so the deck ships with no transition applied. The only reliable way to set a transition or build animation in a generated deck is direct OOXML manipulation (below), or designing the motion in PowerPoint and preserving it through PPTX-Automizer's best-effort retention when copying slides unchanged.

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

```xml
<!-- Medium-speed fade, auto-advance after 3 seconds -->
<p:transition spd="med" advTm="3000">
  <p:fade />
</p:transition>
```

- `spd`: `slow`, `med` or `fast`; the rendering app maps these to durations
- `advTm`: auto-advance in milliseconds (omit for click-to-advance)
- `advClick`: set to `0` to disable click advance when using auto-advance

---

## python-pptx XML Approach for Slide Transitions

Neither python-pptx nor pptxgenjs exposes a transition API; write the OOXML directly after the slide exists.

```python
from pptx import Presentation
from pptx.oxml.ns import qn
from lxml import etree

prs = Presentation()
slide = prs.slides.add_slide(prs.slide_layouts[1])
slide.shapes.title.text = "Introduction"

# Schema order inside <p:sld>: cSld, clrMapOvr, transition, timing, extLst.
# Insert after clrMapOvr (or cSld) so a template slide that already has
# <p:timing> or <p:extLst> stays valid; appending at the end would not.
sld = slide._element
transition = etree.Element(qn('p:transition'))
transition.set('spd', 'med')     # slow | med | fast
transition.set('advTm', '5000')  # auto-advance ms; omit for click-to-advance
etree.SubElement(transition, qn('p:fade'))
anchor = sld.find(qn('p:clrMapOvr'))
if anchor is None:
    anchor = sld.find(qn('p:cSld'))
anchor.addnext(transition)

prs.save('transitions.pptx')
```

Valid transition elements: `p:fade`, `p:push` (with `dir="l|r|u|d"`), `p:wipe` (with `dir`), `p:cover`, `p:uncover`, `p:split` (with `orient="horz|vert"`), `p:cut`. If PowerPoint shows a repair prompt, check element order — `<p:transition>` must come before any `<p:timing>` or `<p:extLst>` sibling.

---

## Build Animations

Build animations (bullets appearing one at a time, chart series fading in) require direct manipulation of the slide's `<p:timing>` tree — no library in this stack has an animation API, and the tree is deeply nested and fragile to hand-write from the OOXML spec. Prefer designing the build sequence in PowerPoint directly; if it must be scripted, extract the `<p:timing>` XML from a hand-built example deck and reuse it as a template (swap the `spTgt` shape ids) rather than constructing it from scratch. Test output in PowerPoint after every change.

---

## PPTX-Automizer: Best-Effort Animation Retention

PPTX-Automizer can preserve transitions and animations when it copies source slides, but animations are still outside its core editing model. If you replace or remove a shape that participates in the timing tree, the slide can lose motion or even become fragile.

`modifyElement(selector, callback | callback[])` takes a callback, not a plain options object like `{ text: ... }`. Build callbacks with the helper exports (`ModifyTextHelper.setText`, `ModifyTableHelper.setTable`, `ModifyChartHelper.setChartData`, or the `modify.*` shorthands); check the installed version's `index.d.ts` for the current list:

```typescript
import Automizer, { ModifyTextHelper, ModifyTableHelper } from 'pptx-automizer';

const automizer = new Automizer({
  templateDir: './templates',
  outputDir: './output',
});

const pptx = automizer
  .loadRoot('base.pptx')
  .load('animated-template.pptx', 'animated');

// Copy slide 2 from the animated template.
// Keep edits small if the slide contains animations tied to specific shape ids.
pptx.addSlide('animated', 2, (slide) => {
  slide.modifyElement('TitlePlaceholder', ModifyTextHelper.setText('Updated Title'));
  slide.modifyElement('DataTable', ModifyTableHelper.setTable(updatedTableData));
});

await pptx.write('output.pptx');
```

**Workflow:** Design animations in PowerPoint, save as template, use Automizer only for conservative text/image/table/chart replacement via its callback API, then test the final file in desktop PowerPoint. Assume motion is best-effort, not guaranteed.

---

## Accessibility Concerns

- **Reduced motion:** PPTX files do not honor `prefers-reduced-motion`. Provide a static version of any animated deck.
- **Screen readers:** Animations are invisible to screen readers; all content must make sense without the animation sequence.
- **Flashing content:** Nothing should flash more than three times in any one-second period — WCAG 2.3.1.
- **Auto-advance timing:** Time auto-advance against a slow reader, not the author, and provide a manual override (WCAG 2.2.1 Timing Adjustable).

---

## Do / Avoid

### Do

- Design animations and transitions in PowerPoint directly; treat scripted XML as a last resort
- Keep template edits to animated slides conservative — text/table/chart data only
- Test the final file in PowerPoint (not just a viewer) to verify timing

### Avoid

- Generating PptxGenJS code that sets `slide.transition` or `advanceAfter` — neither exists in the API
- Calling `modifyElement(selector, { text: ... })` on pptx-automizer — pass a callback, not an options object
- Assuming animations survive a Google Slides or Keynote import

---

## Related Resources

- [pptx-layouts.md](pptx-layouts.md) - Master slides and themes
- [pptx-charts.md](pptx-charts.md) - Chart styling and data binding
- [../assets/pitch-deck.md](../assets/pitch-deck.md) - Complete pitch deck template
