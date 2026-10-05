# Performance UX Vitals

The design side of performance: how fast the interface *feels*, what users see while they wait, and where focus goes when content changes. Metric engineering lives elsewhere:

- Core Web Vitals targets, LCP/INP/CLS fixes, images, fonts, bundles and third-party scripts: [software-frontend/references/performance-optimization.md](../../software-frontend/references/performance-optimization.md)
- Lab and field measurement, budgets and CI gates: [qa-testing-performance/references/frontend-performance.md](../../qa-testing-performance/references/frontend-performance.md)
- Profiling and system-level performance: [software-performance](../../software-performance/SKILL.md)

Font-swap layout shift as a type decision is covered in [typography-systems.md](typography-systems.md).

## Table of Contents

- [Perceived Performance](#perceived-performance)
- [Loading Indicators by Duration](#loading-indicators-by-duration)
- [Route Transition Patterns](#route-transition-patterns)
- [Focus Management When Content Changes](#focus-management-when-content-changes)
- [Modern CSS Surfaces](#modern-css-surfaces)
- [Design Checklist](#design-checklist)

---

## Perceived Performance

Perceived performance is how fast users *feel* the interface is, independent of measured load time. A screen that shows structure immediately and fills in progressively usually feels faster than a blank screen that finishes sooner.

### Skeleton Screens

| Guideline | Rationale |
|-----------|-----------|
| Match the layout of the actual content | Reduces visual shift when content arrives; users recognise the final layout |
| Use a subtle pulse or wave | Signals loading; static grey blocks look broken |
| Skeleton above-the-fold content only | Below-fold content can lazy-load without placeholders |
| Replace skeletons progressively | Do not wait for all content before showing any |
| Mark the region `aria-busy="true"` and stop the animation under `prefers-reduced-motion` | Assistive tech and motion-sensitive users get the same state without the shimmer |

A skeleton whose composition does not match the loaded screen is a usability defect, not cosmetic debt.

### Optimistic UI

Show the expected result of a user action immediately, before the server confirms it, and design the rollback at the same time.

| Action | Optimistic Response | Rollback on Failure |
|--------|-------------------|-------------------|
| Like/favorite | Immediately toggle icon and increment count | Revert icon and count, show toast error |
| Send message | Append message to thread with "sending" indicator | Show "failed to send" with retry option |
| Delete item | Remove from list with undo toast | Re-insert item if undo or server fails |
| Form submit | Navigate to success state | Return to form with error, pre-fill data |

Do not use optimistic UI for payments, irreversible actions, or anything where a silent rollback would mislead the user.

### Progressive Loading

| Pattern | Implementation | Best For |
|---------|---------------|----------|
| **Above-the-fold first** | Server-render critical content, lazy-load the rest | Landing pages, articles |
| **Infinite scroll** | Load next batch near the bottom (`IntersectionObserver`); keep a reachable footer and restore scroll position on back | Feeds, search results |
| **Pagination** | Discrete pages with explicit navigation | Data tables, product listings, anything users need to reference or share |
| **Staggered reveal** | Components appear as they load, top to bottom, in reserved space | Dashboards with multiple data sources |

## Loading Indicators by Duration

Rules of thumb, anchored on the classic response-time limits (about 0.1 s feels instant, about 1 s keeps flow, about 10 s is the limit of attention; [NN/g](https://www.nngroup.com/articles/response-times-3-important-limits/)):

| Expected Duration | Pattern |
|------------------|---------|
| Under ~300 ms | No indicator; an instant swap or short fade |
| ~300 ms to 1 s | Subtle progress bar at the top of the viewport |
| ~1 to 5 s | Skeleton of the target screen |
| ~5 to 30 s | Progress with explanation ("Loading dashboard data…"), determinate if you can measure it |
| Over ~30 s | Background processing with notification when ready, and a way to leave the screen |

Delay showing a spinner by a few hundred milliseconds so fast responses do not flash one.

## Route Transition Patterns

| Pattern | User Experience |
|---------|-----------------|
| **Instant swap** | Fast but can disorient without a cue |
| **Fade** (about 150-250 ms) | Smooth, signals change |
| **Slide** | Directional; match direction to forward/back navigation |
| **Skeleton on navigate** | Feels fast, previews structure |
| **Keep old content + progress bar** | No blank state; users see progress |

Every transition needs a reduced-motion path (instant swap or plain fade).

## Focus Management When Content Changes

| Event | Focus Target | Why |
|-------|-------------|-----|
| SPA route change | The new page's `<h1>` (with `tabindex="-1"`) or the `<main>` landmark, plus an updated `document.title` | Screen readers must learn the page changed; focus left on `body` announces nothing |
| Modal or drawer opens | First focusable element inside; trap focus in the innermost layer | Keeps keyboard users in context |
| `Esc` or close | Closes the innermost layer only; focus returns to the element that opened it | Return to context |
| Nested layers | Keep a focus stack: push the trigger on open, pop and focus on close | Restores focus in the right order |
| Wizard step change | First input of the new step; announce "Step n of m: title" in a polite live region | Users know where they are without re-reading the page |
| Async DOM replacement | Save the focused element's id before the update and restore it after; fall back to the nearest stable parent | Focus never drops to `document.body` |
| Optimistic delete | Next sibling in the list, or the previous one if the last item was removed | Keeps the keyboard position |
| Accordion expand | Leave focus on the trigger; the content follows in reading order | Avoids surprise jumps |

Bypass blocks (WCAG 2.4.1, Level A) can be met with a "Skip to main content" link, with landmarks, or with headings; a skip link is the most robust choice for keyboard-only users but not the only conforming one. Avoid focusing hidden elements, traps that block `Esc` (2.1.2), and `autofocus` on page-load inputs. Code-level focus and ARIA fixes: [software-accessibility](../../software-accessibility/SKILL.md).

## Modern CSS Surfaces

Three CSS features change which interaction problems need JavaScript, so spec them in the handoff. Browser support moves quickly: check [MDN](https://developer.mozilla.org/) or caniuse for each feature and budget a fallback for any engine that lacks it.

### View Transitions API

- **What**: native crossfade and morph animations between page or state changes; same-document for SPA state and route changes, cross-document for multi-page navigation.
- **Design decision**: replaces bespoke JS animation libraries for route and state transitions.
- **Trap**: give each element pair a `view-transition-name`, or the transition is a single whole-page crossfade. Provide a `prefers-reduced-motion` fallback (zero duration or no transition names).

### CSS Anchor Positioning

- **What**: position a popover, tooltip or dropdown relative to an anchor element without JS, with `@position-try` fallbacks when the preferred side overflows.
- **Design decision**: specify anchor element, preferred side and fallback sides in the handoff; tooltips, menus, autocompletes and tour overlays may not need a positioning library.
- **Trap**: keep a JS-positioning fallback until every target engine supports it.

### Scroll-Driven Animations

- **What**: animate properties as a function of scroll position (`animation-timeline: scroll()` or `view()`), no JS.
- **Design decision**: parallax, scroll progress bars, reveals and sticky-header transforms can be CSS-only.
- **Trap (accessibility)**: wrap scroll-driven animation in `@media (prefers-reduced-motion: no-preference)` and give a static fallback that still communicates the relationship.

## Design Checklist

- [ ] Every async surface has a loading, empty, error and success state designed
- [ ] Skeletons match the loaded layout and respect reduced motion
- [ ] Optimistic actions have a designed rollback and are not used for irreversible actions
- [ ] Loading indicator chosen by expected duration, with a delay before spinners
- [ ] Route transitions have a reduced-motion path
- [ ] Focus target defined for route change, modal open/close, wizard steps and deletes
- [ ] Space reserved for late-loading content (no layout shift)
- [ ] Metric targets and budgets handed to the performance references above
