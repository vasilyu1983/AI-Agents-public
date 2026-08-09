# Prototype-to-Production Alignment

Operational checklist for closing the gap between design prototypes and shipped UI. Use when a team says "prototype is close, but the real page feels off."

**Last Updated**: March 2026

---

## Dashboard Lesson Pack

### 1) Desktop choreography before pixel tweaks

- Start with asymmetric columns (about 60/40), not strict mirrored rows.
- Keep independent vertical rhythm per column; align only intentional pairs.
- Prevent dead-right canvas by moving right-column cards up when left grows.

### 2) Compactness heuristics (web)

- Tighten module spacing to ~10-14px in related zones.
- Remove decorative section labels unless they add navigation value.
- Merge adjacent related blocks into one container if this reduces visual fragmentation.
- **Default to flat/compact, not expandable/accordion**: Use static inline content unless the user explicitly needs progressive disclosure. Expanding panels add interaction cost, layout shift, and complexity. Only use accordions/drawers when content volume genuinely exceeds viewport tolerance.

### 3) Control standardization

- One primary action per card context.
- One share style across dashboard; avoid duplicate share controls in one context.
- Replace oversized full-width disclosure controls with compact secondary pills/links.
- Keep day chips + "This Week" as one visual family with stable alignment.

### 4) De-duplication rules

- Do not repeat the same meaning in metadata, chips, and body hints.
- If context is shown under the hero title (date/moon/phase), remove duplicate decorative restatements.
- Remove duplicate guidance fragments across Signal/Tension and Do/Do not.

### 5) Banner governance

- Promotional/validation banners are contextual, not always-on.
- Dismissal must persist; route-level suppression is required for noisy cards.
- Passive banners should not look selected (no heavy "active" border unless stateful).

### 6) Loading-state quality bar

- Skeletons must map to final IA (shape/count/relative sizing).
- Keep header context visible while loading.
- Avoid disconnected full-page placeholder compositions that create "messy" perception.

### 7) i18n requirement in design handoff

- Every user-visible string (including aria labels/tooltips) must be key-based.
- Define EN keys as baseline in spec before implementation.
- Reject hardcoded strings in final QA.

### 8) Final QA pass sequence

1. Desktop rhythm and right-side void check (1440+).
2. Mobile chip size/contrast/alignment check.
3. Control consistency sweep (buttons, links, share, chips).
4. Expansion behavior check (no whitespace blowouts).
5. Loading state and feature-surfacing sanity check.

---

## Ops UI QA: Design-to-Ship Checks

Use this after implementing visual changes to prevent "looks good in Figma, broken in prod" outcomes.

### Fast QA Commands

```bash
# 1) Run build first (layout and import safety)
npm run build

# 2) Run accessibility smoke if available
npm run test:e2e -- --grep "@a11y"

# 3) Capture route screenshots for review set
# (replace with your project screenshot task)
npm run test:e2e -- --grep "@visual"
```

### Required Review Grid

Validate each critical screen for:
- desktop rhythm (1366+, 1440+, 1920),
- mobile spacing and tap targets (360-430 width),
- loading/empty/error state consistency,
- contrast and focus visibility,
- localization expansion (long strings, RTL if supported).

### Operational Rule

Do not sign off on visual changes without state coverage (loading, empty, error, success). Most production regressions hide outside the default happy state.
