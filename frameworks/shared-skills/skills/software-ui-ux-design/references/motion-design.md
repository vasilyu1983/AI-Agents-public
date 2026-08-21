# Motion Design

Practical guidance for specifying and implementing interface motion. Pairs with the Craft Bar's Motion row ("functional, not decorative") in `../SKILL.md` and the visual-language guidance in [frontend-aesthetics.md](frontend-aesthetics.md).

## Library Landscape (verified 2026-08-13)

| Tool | Use when | Notes |
|------|----------|-------|
| CSS transitions/animations | single-property state changes, hover, focus, simple reveals | zero JS cost; first choice for anything a transition can express |
| CSS scroll-driven animations | progress bars, simple scroll reveals | needs `prefers-reduced-motion` guard *and* graceful no-support fallback |
| **Motion** (motion.dev) | React/Vue/vanilla apps needing springs, layout animation, gestures, exit animations | formerly Framer Motion; independent since mid-2025; npm package `motion`, React import `motion/react`; ~12KB core; v13.x current — the legacy `framer-motion` npm package still installs but new work should not use it |
| GSAP | timeline choreography, SVG/canvas, scroll-scrubbed narratives | free since the Webflow acquisition; heavier mental model, strongest sequencing control |
| React Spring | physics-first React animation | overlaps Motion; prefer one, not both, in a codebase (Rule: don't blend two animation conventions) |
| Rive / Lottie | designer-authored vector animation assets | asset pipeline, not interaction logic; require reduced-motion and fallback plan |

Do not specify "Framer Motion" in new briefs or specs — the name now points at a legacy package. Write "Motion (motion.dev)".

## Motion Defaults Worth Encoding in Specs

- **Springs for physical properties** (`x`, `y`, `scale`, `rotate`): interruptible and velocity-preserving, so mid-animation redirects feel natural. **Tweens/easing for visual properties** (`opacity`, `color`): physics on opacity reads as lag, not life.
- **Layout animation over manual FLIP**: Motion's `layout` prop animates size/position/reorder changes via transforms automatically. Specify "list reorder animates with layout animation" instead of describing translate math.
- **Exit animations are part of the state model**: removal without exit animation reads as data loss. `AnimatePresence` (React) or equivalent covers unmount transitions — but keep exits *faster* than entrances (roughly 2:3), because the user has already decided to leave.
- **Scroll-*triggered* vs scroll-*linked* are different patterns with different risk**:
  - *Triggered* (`whileInView`): fires once when entering viewport. Low motion-sickness risk; fine almost everywhere.
  - *Linked* (`useScroll` + motion values — parallax, scrubbed progress): continuously tied to scroll position. This is the category that harms vestibular-disorder users; always behind a reduced-motion check, and never carrying information that isn't available statically.
- **Duration bands**: micro-feedback 50–150ms; state transitions 200–300ms; navigation/spatial transitions 300–500ms. Anything over ~500ms on a repeated interaction is a tax, not a delight.

## Reduced Motion — Implementation, Not Just a Checkbox

The Verification Checklist requires a `prefers-reduced-motion` fallback. The implementation pattern, in order of preference:

1. **App-wide switch (React/Motion):**

   ```jsx
   import { MotionConfig } from 'motion/react'

   <MotionConfig reducedMotion="user">
     <App />
   </MotionConfig>
   ```

   With `reducedMotion="user"`, Motion honors the OS-level Reduced Motion setting automatically: transform and layout animations are disabled while opacity and color transitions are preserved — which matches the correct design intent (reduce *movement*, keep *state communication*).

2. **Per-component logic** where the fallback needs design intent, not just suppression:

   ```jsx
   import { useReducedMotion } from 'motion/react'

   const shouldReduce = useReducedMotion()
   // swap transform-based entrance for opacity fade,
   // disable parallax / autoplaying video / scroll-linked values
   ```

3. **CSS-only surfaces:**

   ```css
   @media (prefers-reduced-motion: reduce) {
     *, *::before, *::after { animation-duration: 0.01ms !important; transition-duration: 0.01ms !important; }
   }
   ```

   The blanket kill-switch is a floor, not a design: it also removes opacity transitions that reduced-motion users generally tolerate. Prefer targeted overrides on the offending transforms.

**Reduced motion is not "no motion".** The setting signals vestibular sensitivity to *movement* — parallax, zoom, spin, large translations. Crossfades, color changes, and instant state swaps remain fine and are usually *necessary* so state changes stay perceivable.

## Motion Spec Checklist (add to handoffs)

- [ ] Every specified animation names its *function*: orientation (where did this come from), feedback (did my action land), or state change (what is different)
- [ ] Purely decorative motion is limited to first-run delight and primary commit moments (Craft Bar rows)
- [ ] Springs vs tweens assigned per property type; durations within bands above
- [ ] Exit animations specified for every entrance
- [ ] Scroll-linked motion listed explicitly, each with its reduced-motion replacement
- [ ] `MotionConfig reducedMotion="user"` (or platform equivalent) present in the implementation plan
- [ ] Animations run on compositor-friendly properties (`transform`, `opacity`) — no animated `top/left/width/height` unless layout animation handles it
- [ ] Library choice stated once for the codebase; no mixing Motion + React Spring + GSAP on one surface

## Known Traps

- Specifying motion by adjective ("smooth", "snappy", "delightful") instead of by property, duration, and trigger — AI-generated implementations will guess, and guesses skew decorative.
- Copying `framer-motion` imports from pre-2025 tutorials into a `motion` codebase: both packages install without error and their APIs drift apart silently.
- Scroll-linked hero animations that carry the only statement of what the product does — reduced-motion users and crawlers get a blank hero.
- Treating Motion+ paid examples/AI-kit output as MIT-by-default for redistribution: the *library* is MIT; Motion+ content has its own license.
