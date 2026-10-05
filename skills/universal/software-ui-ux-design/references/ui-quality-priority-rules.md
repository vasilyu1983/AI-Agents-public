# UI Quality Priority Rules

Priority-ordered rule categories for building or reviewing UI, plus frequently-missed professional-polish rules. Adapted from [nextlevelbuilder/ui-ux-pro-max-skill](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill) (MIT). Use top-down: a screen failing priority 1–3 rules is not ready regardless of how well it scores below.

Detailed do/don't rows with code examples are queryable: see [design-database-search.md](design-database-search.md) (`--domain ux`, `--domain web`).

## Table of Contents

- [Priority Categories](#priority-categories)
- [Professional Polish Rules](#professional-polish-rules)
- [App Pre-Delivery Checklist](#app-pre-delivery-checklist)

## Priority Categories

| Priority | Category | Impact | Key Checks (Must Have) | Anti-Patterns (Avoid) |
|----------|----------|--------|------------------------|------------------------|
| 1 | Accessibility | CRITICAL | text contrast 4.5:1 (3:1 only for large text and non-text UI), alt text, keyboard nav, aria-labels, reduced-motion, Dynamic Type | removed focus rings, icon-only buttons without labels |
| 2 | Touch & interaction | CRITICAL | targets ≥24×24 CSS px (WCAG 2.2 AA, SC 2.5.8) and at the platform size (44pt iOS / 48dp Android) for primary controls, ≥8px gap, press feedback perceptibly immediate, loading-state buttons | hover-only affordances, instant 0ms state changes, gesture-only critical actions |
| 3 | Performance | HIGH | WebP/AVIF + lazy load, reserved space (CLS <0.1), virtualize long lists, skeletons >1s | layout thrashing, blocking spinners, unbounded third-party scripts |
| 4 | Style selection | HIGH | style matched to product type, one icon family, SVG icons (never emoji), consistent elevation scale | mixing flat and skeuomorphic, emoji as icons, random shadow values |
| 5 | Layout & responsive | HIGH | mobile-first breakpoints, viewport meta with zoom enabled, 4/8pt spacing rhythm, dvh over vh | horizontal scroll on mobile, fixed px containers, disabled zoom |
| 6 | Typography & color | MEDIUM | 16px base body, line-height 1.5–1.75, semantic color tokens, tabular figures for data | body text <12px, gray-on-gray, raw hex in components, inverted-color dark mode |
| 7 | Animation | MEDIUM | 150–300ms micro-interactions, transform/opacity only, exit shorter than enter, interruptible | decorative-only motion, animating width/height, >500ms transitions, no reduced-motion path |
| 8 | Forms & feedback | MEDIUM | visible labels, error below field with recovery path, validate on blur, focus first invalid field | placeholder-only labels, errors only at top, overwhelming upfront options |
| 9 | Navigation | HIGH | predictable back with state restore, bottom nav ≤5 labeled items, deep links to key screens | mixed nav patterns at one level, silent stack resets, modal-as-navigation |
| 10 | Charts & data | LOW | legend + tooltips, table fallback for screen readers, color + pattern (never color alone) | pie with >5 categories, gridlines competing with data, hover-only tooltips |

## Professional Polish Rules

Frequently-overlooked issues that make UI read as amateur. Scope: app UI (iOS/Android/React Native/Flutter); most rows generalize to web.

### Icons and visual elements

- Vector icons only (Phosphor, Heroicons, Lucide, platform vector sets) — never emoji for navigation, settings, or system controls; never raster PNGs that blur.
- One icon family, one stroke width (e.g. 1.5px or 2px), one fill-vs-outline style per hierarchy level.
- Icon sizes as design tokens (icon-sm/md/lg), aligned to text baseline, contrast ≥3:1 against adjacent colours (WCAG 1.4.11 non-text); icons that carry text-like meaning at small sizes are safer at 4.5:1.
- Official brand assets with correct proportions and clear space — never recolored or guessed.
- Press states change color/opacity/elevation without shifting layout bounds.

### Light/dark mode contrast

- All text ≥4.5:1 in **both** themes, secondary and caption text included (WCAG 1.4.3 allows 3:1 only for large text: at least 18pt, or 14pt bold); icons, borders and state indicators ≥3:1 (1.4.11); test dark mode separately, never inferred from light.
- Borders, dividers, and interaction states must remain distinguishable in both themes.
- Theme via semantic tokens mapped per mode — no hardcoded per-screen hex values.
- Modal scrim strong enough to isolate the foreground and keep the dialog's own text and controls at their contrast ratios; measure against the scrimmed surface, not the base canvas.

### Layout and spacing

- Respect safe areas for all fixed headers, tab bars, and CTA bars; never collide with OS chrome or the gesture bar.
- 4/8pt spacing rhythm with explicit vertical-rhythm tiers (e.g. 16/24/32/48) by hierarchy.
- Add content insets so scroll content is not hidden behind fixed/sticky bars.
- Adapt gutters by breakpoint and orientation; cap long-form text measure on large devices.

## App Pre-Delivery Checklist

Run before delivering app UI code; pairs with the web-oriented Verification Checklist in `SKILL.md`.

- [ ] No emoji icons; single consistent icon family and style
- [ ] Every tappable element has pressed feedback (ripple/opacity/elevation) without layout shift
- [ ] Touch targets ≥24×24 CSS px everywhere (WCAG 2.2 AA, SC 2.5.8; 44×44 is the AAA SC 2.5.5 size) and at the platform size for primary controls (44×44pt iOS HIG / 48×48dp Material); hit areas expanded for small icons
- [ ] Micro-interactions 150–300ms with platform-native easing; animations interruptible and non-blocking
- [ ] Both themes tested: all text ≥4.5:1 (large text and non-text UI ≥3:1), states distinguishable in light and dark
- [ ] Safe areas respected; scroll content not obscured by fixed bars
- [ ] Verified at small-phone width (375px) and landscape; gutters adapt by size
- [ ] Reduced motion and largest Dynamic Type size verified without layout breakage
- [ ] Screen reader focus order matches visual order; roles/states (selected, disabled, expanded) announced
- [ ] Color never the only indicator; form fields have labels, hints, and recovery-path errors
