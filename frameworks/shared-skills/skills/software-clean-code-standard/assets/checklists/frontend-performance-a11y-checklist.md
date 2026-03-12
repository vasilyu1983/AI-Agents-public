# Frontend Performance & Accessibility Checklist

**Page/Component**: [Name]
**Reviewer**: [Name]
**Date**: YYYY-MM-DD

---

## Performance (Core)

### Core Web Vitals

- [ ] LCP (Largest Contentful Paint) <= 2.5s
- [ ] INP (Interaction to Next Paint) <= 200ms
- [ ] CLS (Cumulative Layout Shift) <= 0.1

### Bundle Size

- [ ] Performance budgets defined and tracked (JS/CSS/images/fonts) [Inference]
- [ ] Route-level code splitting used where applicable
- [ ] Images optimized (WebP/AVIF, lazy loading)
- [ ] Fonts subset and preloaded

### Rendering and Runtime

- [ ] Main-thread long tasks minimized (avoid synchronous heavy work on input) [Inference]
- [ ] Critical rendering path avoids unnecessary blocking requests [Inference]
- [ ] Error boundaries or equivalent fault isolation for UI crashes

### Framework-Specific (React/Next.js)

- [ ] Server Components used where they reduce client JS [Inference]
- [ ] Client Components are minimal and explicitly marked (`"use client"`)
- [ ] Suspense boundaries used for async data and streaming
- [ ] Error boundaries used for fault isolation

---

## Accessibility (Core)

### WCAG 2.2 AA Compliance

- [ ] Color contrast ratio >= 4.5:1 (text), >= 3:1 (large text)
- [ ] Focus visible on all interactive elements
- [ ] Keyboard navigation works (Tab, Enter, Escape)
- [ ] Touch targets meet WCAG 2.2 SC 2.5.8 target size (24x24 CSS px; exceptions apply) https://www.w3.org/TR/WCAG22/#target-size-minimum
- [ ] Touch targets follow platform guidance where relevant (e.g., 44x44 on iOS) https://developer.apple.com/design/human-interface-guidelines/

### Semantic HTML

- [ ] Proper heading hierarchy (h1, h2, h3)
- [ ] Landmarks used (main, nav, aside, footer)
- [ ] Form inputs have associated labels
- [ ] Images have alt text (or alt="" for decorative)

### Screen Reader

- [ ] ARIA labels where semantic HTML insufficient
- [ ] Live regions for dynamic content
- [ ] Focus management for modals/dialogs
- [ ] Skip links for navigation

---

## Testing

- [ ] Core Web Vitals measured (field + lab) with no regressions https://web.dev/vitals/
- [ ] Lighthouse budgets set with no regressions [Inference]
- [ ] axe DevTools: 0 critical/serious issues [Inference]
- [ ] Manual keyboard navigation test
- [ ] Screen reader test (VoiceOver/NVDA)

---

## Optional: AI/Automation Section

> Include only for AI design tools or AI features.

- [ ] AI-generated components reviewed for accessibility
- [ ] AI chat interfaces have ARIA live regions
- [ ] Loading states visible during AI processing
- [ ] Error handling for AI service failures
