# Performance UX Vitals

Practical guide to the intersection of web performance and user experience. Covers Core Web Vitals, perceived performance techniques, image and font optimization, SPA navigation patterns, performance budgets, mobile considerations, and measurement tools. Performance is a UX feature -- every 100ms of latency costs measurable engagement and conversion.

**Last Updated**: March 2026

---
## Table of Contents

- [Core Web Vitals](#core-web-vitals)
- [Metric Overview](#metric-overview)
- [LCP: What Counts as "Largest"](#lcp-what-counts-as-largest)
- [LCP Optimization](#lcp-optimization)
- [INP Optimization](#inp-optimization)
- [CLS Optimization](#cls-optimization)
- [Perceived Performance Patterns](#perceived-performance-patterns)
- [Skeleton Screens](#skeleton-screens)
- [Optimistic UI](#optimistic-ui)
- [Progressive Loading](#progressive-loading)
- [Image Optimization for UX](#image-optimization-for-ux)
- [Responsive Images](#responsive-images)
- [Image Loading Strategies](#image-loading-strategies)
- [Blur-Up Placeholder Pattern](#blur-up-placeholder-pattern)
- [Format Comparison](#format-comparison)
- [Font Loading Impact on UX](#font-loading-impact-on-ux)
- [CLS from Font Swap](#cls-from-font-swap)
- [Font Loading Performance Checklist](#font-loading-performance-checklist)
- [SPA Navigation UX](#spa-navigation-ux)
- [Route Transition Patterns](#route-transition-patterns)
- [Loading Indicators by Duration](#loading-indicators-by-duration)
- [Route Transition Implementation](#route-transition-implementation)
- [Focus Management on Navigation](#focus-management-on-navigation)
- [Performance Budgets](#performance-budgets)
- [Setting Budgets](#setting-budgets)
- [Budget Enforcement](#budget-enforcement)
- [UX Implications of Budget Violations](#ux-implications-of-budget-violations)
- [Mobile Performance Considerations](#mobile-performance-considerations)
- [Network-Aware Loading](#network-aware-loading)
- [Reduced Data Mode](#reduced-data-mode)
- [Mobile-Specific Performance Priorities](#mobile-specific-performance-priorities)
- [Reduced Motion](#reduced-motion)
- [Measuring UX Performance](#measuring-ux-performance)
- [Real User Monitoring (RUM)](#real-user-monitoring-rum)
- [Web Vitals API](#web-vitals-api)
- [Lighthouse](#lighthouse)
- [Lighthouse CLI in CI](#lighthouse-cli-in-ci)
- [Performance Testing in CI](#performance-testing-in-ci)
- [GitHub Actions: Lighthouse CI](#github-actions-lighthouse-ci)
- [Metric Correlation with UX Outcomes](#metric-correlation-with-ux-outcomes)
- [Performance UX Checklist](#performance-ux-checklist)
- [References](#references)
- [Cross-References](#cross-references)


## Core Web Vitals

Google's Core Web Vitals are the primary metrics for measuring real-user experience. They capture loading, interactivity, and visual stability.

### Metric Overview

| Metric | Full Name | What It Measures | Good | Needs Improvement | Poor |
|--------|-----------|-----------------|------|-------------------|------|
| **LCP** | Largest Contentful Paint | Loading -- when the largest visible element renders | <= 2.5s | 2.5-4.0s | > 4.0s |
| **INP** | Interaction to Next Paint | Responsiveness -- delay between user action and visual response | <= 200ms | 200-500ms | > 500ms |
| **CLS** | Cumulative Layout Shift | Visual stability -- how much content shifts unexpectedly | <= 0.1 | 0.1-0.25 | > 0.25 |

### LCP: What Counts as "Largest"

| Element Type | Counts for LCP | Notes |
|-------------|---------------|-------|
| `<img>` elements | Yes | Including `<img>` inside `<picture>` |
| `<image>` inside `<svg>` | Yes | SVG raster images |
| `<video>` poster image | Yes | Poster frame, not video playback |
| Block-level element with background image via CSS | Yes | `background-image: url(...)` |
| Text block elements | Yes | `<p>`, `<h1>`, etc. with significant text |

### LCP Optimization

| Cause | Fix | Impact |
|-------|-----|--------|
| Slow server response (TTFB > 800ms) | CDN, edge caching, server optimization | High |
| Render-blocking CSS/JS | Inline critical CSS, defer non-critical JS | High |
| Hero image not preloaded | `<link rel="preload" as="image" href="hero.webp">` | High |
| Client-side rendering delay | SSR or SSG for above-the-fold content | High |
| Large unoptimized images | Responsive images, WebP/AVIF, compression | Medium |
| Web font blocking text render | `font-display: swap` + preload | Medium |

### INP Optimization

| Cause | Fix | Impact |
|-------|-----|--------|
| Long JavaScript tasks (> 50ms) | Break into smaller tasks with `requestIdleCallback` or `scheduler.yield()` | High |
| Heavy event handlers | Debounce input, use `requestAnimationFrame` for visual updates | High |
| Layout thrashing | Batch DOM reads/writes, use `ResizeObserver` instead of polling | Medium |
| Third-party scripts | Lazy-load non-critical third-party code | Medium |
| Expensive re-renders (React) | `useMemo`, `React.memo`, virtualized lists | Medium |

```javascript
// Breaking long tasks for better INP
async function processLargeList(items) {
  const CHUNK_SIZE = 50;
  for (let i = 0; i < items.length; i += CHUNK_SIZE) {
    const chunk = items.slice(i, i + CHUNK_SIZE);
    processChunk(chunk);

    // Yield to browser between chunks
    await scheduler.yield();  // Modern API
    // Fallback: await new Promise(resolve => setTimeout(resolve, 0));
  }
}
```

### CLS Optimization

| Cause | Fix | Impact |
|-------|-----|--------|
| Images without dimensions | Always set `width` and `height` attributes | High |
| Ads/embeds without reserved space | Use `aspect-ratio` or `min-height` placeholder | High |
| Font swap causing text reflow | Size-adjusted fallback font (`ascent-override`, `size-adjust`) | High |
| Dynamically injected content | Reserve space or insert below the viewport | Medium |
| Late-loading CSS | Inline critical CSS in `<head>` | Medium |

```html
<!-- Prevent CLS: always declare image dimensions -->
<img
  src="hero.webp"
  alt="Product hero"
  width="1200"
  height="630"
  loading="eager"
  fetchpriority="high"
  decoding="async"
/>

<!-- Prevent CLS: aspect-ratio for responsive containers -->
<style>
  .video-embed {
    aspect-ratio: 16 / 9;
    width: 100%;
    background: var(--color-surface-secondary);
  }
</style>
```

---

## Perceived Performance Patterns

Perceived performance is how fast users *feel* the interface is, independent of actual load time. A 2-second load with good perceived performance feels faster than a 1-second load with a blank screen.

### Skeleton Screens

| Guideline | Rationale |
|-----------|-----------|
| Match the layout of the actual content | Reduces visual shift when content arrives |
| Use subtle animation (pulse or wave) | Signals loading; static gray blocks look broken |
| Show skeletons for above-the-fold content only | Below-fold can lazy-load without skeletons |
| Remove skeletons progressively as content loads | Do not wait for all content before showing any |

```css
/* Skeleton pulse animation */
.skeleton {
  background: linear-gradient(
    90deg,
    var(--color-surface-secondary) 25%,
    var(--color-surface-primary) 50%,
    var(--color-surface-secondary) 75%
  );
  background-size: 200% 100%;
  animation: skeleton-pulse 1.5s ease-in-out infinite;
  border-radius: 4px;
}

@keyframes skeleton-pulse {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

/* Skeleton layout elements */
.skeleton-text { height: 1rem; width: 80%; margin-bottom: 0.5rem; }
.skeleton-heading { height: 1.5rem; width: 60%; margin-bottom: 1rem; }
.skeleton-image { aspect-ratio: 16 / 9; width: 100%; }
```

```jsx
// React skeleton component pattern
function ArticleSkeleton() {
  return (
    <div aria-busy="true" aria-label="Loading article">
      <div className="skeleton skeleton-image" />
      <div className="skeleton skeleton-heading" />
      <div className="skeleton skeleton-text" />
      <div className="skeleton skeleton-text" />
      <div className="skeleton skeleton-text" style={{ width: '45%' }} />
    </div>
  );
}
```

### Optimistic UI

Show the expected result of a user action immediately, before the server confirms it.

| Action | Optimistic Response | Rollback on Failure |
|--------|-------------------|-------------------|
| Like/favorite | Immediately toggle icon and increment count | Revert icon and count, show toast error |
| Send message | Append message to thread with "sending" indicator | Show "failed to send" with retry option |
| Delete item | Remove from list with undo toast | Re-insert item if undo or server fails |
| Form submit | Navigate to success state | Return to form with error, pre-fill data |

```javascript
// Optimistic update pattern
async function toggleLike(postId) {
  // Optimistic: update UI immediately
  setLiked(prev => !prev);
  setCount(prev => liked ? prev - 1 : prev + 1);

  try {
    await api.toggleLike(postId);
  } catch (error) {
    // Rollback on failure
    setLiked(prev => !prev);
    setCount(prev => liked ? prev + 1 : prev - 1);
    showToast('Could not update. Please try again.');
  }
}
```

### Progressive Loading

| Pattern | Implementation | Best For |
|---------|---------------|----------|
| **Above-the-fold first** | SSR critical content, lazy-load rest | Landing pages, articles |
| **Infinite scroll** | Load next batch when near bottom (`IntersectionObserver`) | Feeds, search results |
| **Pagination** | Discrete pages with explicit navigation | Data tables, product listings |
| **Staggered reveal** | Components appear as they load, top to bottom | Dashboards with multiple data sources |

---

## Image Optimization for UX

### Responsive Images

```html
<!-- Responsive image with format fallback -->
<picture>
  <source
    type="image/avif"
    srcset="photo-400.avif 400w, photo-800.avif 800w, photo-1200.avif 1200w"
    sizes="(max-width: 640px) 100vw, (max-width: 1024px) 50vw, 33vw"
  />
  <source
    type="image/webp"
    srcset="photo-400.webp 400w, photo-800.webp 800w, photo-1200.webp 1200w"
    sizes="(max-width: 640px) 100vw, (max-width: 1024px) 50vw, 33vw"
  />
  <img
    src="photo-800.jpg"
    alt="Product photograph"
    width="800"
    height="600"
    loading="lazy"
    decoding="async"
  />
</picture>
```

### Image Loading Strategies

| Strategy | Attribute / API | When to Use |
|----------|----------------|-------------|
| **Eager loading** | `loading="eager"` + `fetchpriority="high"` | Above-the-fold hero/LCP image |
| **Lazy loading** | `loading="lazy"` | Below-the-fold images |
| **Progressive JPEG** | Encoder setting (e.g., `mozjpeg --progressive`) | Large photos -- renders blurry then sharpens |
| **Blur-up placeholder** | Base64 inline tiny image (20-40 bytes LQIP) | Image-heavy pages, e-commerce |
| **Dominant color placeholder** | CSS `background-color` matching image | Cards, thumbnails |

### Blur-Up Placeholder Pattern

```jsx
function BlurUpImage({ src, placeholder, alt, width, height }) {
  const [loaded, setLoaded] = useState(false);

  return (
    <div className="blur-up-container" style={{ aspectRatio: `${width}/${height}` }}>
      {/* Tiny base64 placeholder */}
      <img
        src={placeholder}
        alt=""
        aria-hidden="true"
        className={`blur-up-placeholder ${loaded ? 'blur-up-hidden' : ''}`}
      />
      {/* Full image */}
      <img
        src={src}
        alt={alt}
        width={width}
        height={height}
        loading="lazy"
        onLoad={() => setLoaded(true)}
        className={`blur-up-full ${loaded ? 'blur-up-visible' : ''}`}
      />
    </div>
  );
}
```

```css
.blur-up-container {
  position: relative;
  overflow: hidden;
  background: var(--color-surface-secondary);
}
.blur-up-placeholder {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
  filter: blur(20px);
  transform: scale(1.1);
  transition: opacity 0.3s ease;
}
.blur-up-hidden { opacity: 0; }
.blur-up-full {
  width: 100%;
  height: 100%;
  object-fit: cover;
  opacity: 0;
  transition: opacity 0.3s ease;
}
.blur-up-visible { opacity: 1; }
```

### Format Comparison

| Format | Compression | Browser Support (2026) | Best For |
|--------|------------|----------------------|----------|
| **AVIF** | Best (50% smaller than JPEG) | Chrome, Firefox, Safari 16.4+ | Photos, all modern browsers |
| **WebP** | Very good (25-35% smaller than JPEG) | Universal | Safe default, broad support |
| **JPEG** | Baseline | Universal | Fallback only |
| **PNG** | Lossless | Universal | Screenshots, images with text, transparency |
| **SVG** | N/A (vector) | Universal | Icons, logos, illustrations |

---

## Font Loading Impact on UX

### CLS from Font Swap

When a web font loads and replaces the fallback font, text can reflow, causing layout shift (CLS).

| Impact | Magnitude | Mitigation |
|--------|-----------|------------|
| Line height change | High CLS | Match fallback line height via `ascent-override`, `descent-override` |
| Character width change | Medium CLS | Use `size-adjust` to match fallback metrics |
| Weight difference | Low CLS | Choose fallback with similar stroke width |

```css
/* Size-adjusted fallback font to minimize CLS */
@font-face {
  font-family: 'Inter Fallback';
  src: local('Arial');
  ascent-override: 90.49%;
  descent-override: 22.56%;
  line-gap-override: 0%;
  size-adjust: 107.64%;
}

body {
  font-family: 'Inter', 'Inter Fallback', sans-serif;
}
```

### Font Loading Performance Checklist

- [ ] Critical fonts preloaded with `<link rel="preload">`
- [ ] `font-display: swap` on body fonts, `optional` on decorative fonts
- [ ] Variable font used (single file, all weights)
- [ ] Font files subset to required character ranges
- [ ] Size-adjusted fallback defined to minimize CLS
- [ ] Fonts self-hosted (avoid third-party font CDN round trips)
- [ ] WOFF2 format used (best compression)
- [ ] Total font payload under 100 KB

---

## SPA Navigation UX

### Route Transition Patterns

| Pattern | Implementation | User Experience |
|---------|---------------|-----------------|
| **Instant swap** | Replace content immediately | Fast but disorienting without transition |
| **Fade transition** | Fade out old, fade in new (150-250ms) | Smooth, signals change |
| **Slide transition** | Slide old content out, new in | Directional navigation (forward/back) |
| **Skeleton on navigate** | Show skeleton of target page immediately | Feels fast, structure previewed |
| **Keep old content + progress bar** | NProgress or similar bar at top of viewport | User sees progress, no blank state |

### Loading Indicators by Duration

| Expected Duration | Pattern | Implementation |
|------------------|---------|---------------|
| < 300ms | No indicator needed | Instant swap or short fade |
| 300ms - 1s | Subtle progress bar | Thin bar at top of viewport |
| 1s - 5s | Skeleton screen | Layout placeholder for target page |
| 5s - 30s | Progress with explanation | "Loading dashboard data..." with progress % |
| > 30s | Background processing | "We'll email you when ready" or polling |

### Route Transition Implementation

```jsx
// React Router + NProgress pattern
import NProgress from 'nprogress';
import { useNavigation } from 'react-router-dom';
import { useEffect } from 'react';

function NavigationProgress() {
  const navigation = useNavigation();

  useEffect(() => {
    if (navigation.state === 'loading') {
      NProgress.start();
    } else {
      NProgress.done();
    }
  }, [navigation.state]);

  return null;
}
```

```css
/* NProgress styling */
#nprogress .bar {
  background: var(--color-interactive);
  position: fixed;
  z-index: 1031;
  top: 0;
  left: 0;
  width: 100%;
  height: 3px;
}
```

### Focus Management on Navigation

| Event | Focus Target | Why |
|-------|-------------|-----|
| Route change | `<h1>` of new page or skip-link target | Screen readers need to know the page changed |
| Modal open | First focusable element in modal | Trap focus inside modal |
| Modal close | Element that triggered the modal | Return to context |
| Accordion expand | Content area of expanded section | Direct attention to revealed content |

```javascript
// Focus management on SPA route change
useEffect(() => {
  const heading = document.querySelector('h1');
  if (heading) {
    heading.setAttribute('tabindex', '-1');
    heading.focus({ preventScroll: false });
  }
  // Announce page change to screen readers
  document.title = `${pageTitle} | My App`;
}, [location.pathname]);
```

### Focus management in complex flows

**Multi-step wizards**: move focus to the first input in the new step on every step change. Announce step progress via `aria-live` so screen reader users know where they are without having to read the whole page.

```jsx
// Step change: focus first input, announce progress
useEffect(() => {
  const firstInput = stepRef.current?.querySelector('input, select, textarea, [tabindex]:not([tabindex="-1"])');
  firstInput?.focus();
}, [currentStep]);

// Separate live region for step announcements
<div aria-live="polite" aria-atomic="true" className="sr-only">
  Step {currentStep} of {totalSteps}: {stepTitle}
</div>
```

**Async DOM replacement**: store the target element's `id` before triggering the update. After the DOM settles, attempt to restore focus to that element; if it is gone, walk up to the nearest stable parent.

```javascript
function focusAfterUpdate(savedId) {
  const exact = document.getElementById(savedId);
  if (exact) {
    exact.focus();
    return;
  }
  // Nearest stable ancestor
  const parent = document.querySelector('[data-stable-focus]');
  if (parent) parent.focus();
}
```

**Optimistic deletion**: after removing an item, focus the next sibling in the list; if the deleted item was the last, focus the previous sibling. Never let focus fall to `document.body`.

```javascript
function deleteItem(index, listRef) {
  const items = Array.from(listRef.current.querySelectorAll('[data-list-item]'));
  const nextTarget = items[index + 1] ?? items[index - 1];
  // Remove item from DOM, then restore focus
  requestAnimationFrame(() => nextTarget?.focus());
}
```

**Nested drawers and modals**:

| Event | Focus behavior |
|-------|---------------|
| Inner drawer/modal opens | Focus traps inside the innermost layer |
| `Esc` pressed | Closes innermost layer only; focus returns to the element that opened it |
| Outer modal closes (programmatic) | Focus restores in stack order — inner first, then outer trigger |

Maintain a focus stack as a simple array. Push the trigger element on open; pop and `.focus()` on close.

```javascript
const focusStack = [];

function openModal(triggerEl) {
  focusStack.push(triggerEl);
  // ... open modal, move focus to first focusable inside
}

function closeModal() {
  const returnTarget = focusStack.pop();
  returnTarget?.focus();
}
```

**Skip links**: the first focusable element on every page must be a visually hidden "Skip to main content" link that becomes visible on focus. This is a WCAG 2.4.1 (Level A) requirement, not optional.

```html
<a href="#main-content" class="skip-link">Skip to main content</a>
<!-- ... nav ... -->
<main id="main-content" tabindex="-1">...</main>
```

```css
.skip-link {
  position: absolute;
  top: -100%;
  left: var(--spacing-2);
  z-index: 9999;
  background: var(--color-interactive);
  color: var(--color-on-interactive);
  padding: var(--spacing-1) var(--spacing-2);
  border-radius: var(--radius-md);
  font-weight: 600;
  text-decoration: none;
}
.skip-link:focus { top: var(--spacing-2); }
```

**Route changes in SPAs**: focus must go to the `<h1>` or the `<main>` landmark — not `document.body`. Body focus is invisible to screen readers and does not announce the new page context.

**Avoid**:

| Anti-pattern | Why it fails |
|---|---|
| Focus to invisible / `display:none` element | Focus disappears; screen reader announces nothing |
| Focus trap that blocks `Esc` | WCAG 2.1.2 failure; users cannot exit the layer |
| `autofocus` on page-load inputs | Steals focus from users navigating via keyboard before they reach the input intentionally |
| Focus to `document.body` after route change | Screen reader does not announce the new page; user must manually navigate to find where they are |

---

## Performance Budgets

### Setting Budgets

| Budget Type | Metric | Recommended Threshold | Rationale |
|------------|--------|----------------------|-----------|
| **Size** | Total page weight | < 500 KB compressed | Mobile 3G loads in ~5s |
| **Size** | JavaScript payload | < 200 KB compressed | Parse/compile time on mobile |
| **Size** | Image payload | < 300 KB per viewport | LCP impact |
| **Size** | Font payload | < 100 KB | CLS and render-blocking |
| **Timing** | LCP | < 2.5s | Core Web Vital threshold |
| **Timing** | INP | < 200ms | Core Web Vital threshold |
| **Timing** | Time to Interactive | < 3.8s | Mobile usability benchmark |
| **Count** | HTTP requests | < 50 per page | Connection overhead on mobile |
| **Score** | Lighthouse Performance | >= 90 | Composite quality score |

### Budget Enforcement

```json
{
  "budgets": [
    {
      "path": "/*",
      "resourceSizes": [
        { "resourceType": "script", "budget": 200 },
        { "resourceType": "image", "budget": 300 },
        { "resourceType": "font", "budget": 100 },
        { "resourceType": "total", "budget": 500 }
      ],
      "resourceCounts": [
        { "resourceType": "script", "budget": 15 },
        { "resourceType": "third-party", "budget": 5 }
      ]
    }
  ]
}
```

### UX Implications of Budget Violations

| Violation | UX Impact | User Behavior |
|-----------|-----------|--------------|
| JS > 300 KB | Delayed interactivity, frozen UI on tap | Users tap repeatedly, leave |
| Images > 500 KB viewport | Slow LCP, blank hero section for seconds | Users bounce before content appears |
| Total > 1 MB | 10+ second load on 3G | 53% of mobile users leave after 3s |
| CLS > 0.25 | Buttons shift, misclicks | Users accidentally tap wrong element, lose trust |

---

## Mobile Performance Considerations

### Network-Aware Loading

```javascript
// Adapt content quality to network conditions
function getNetworkQuality() {
  const conn = navigator.connection;
  if (!conn) return 'unknown';

  if (conn.saveData) return 'save-data';
  if (conn.effectiveType === '2g' || conn.effectiveType === 'slow-2g') return 'low';
  if (conn.effectiveType === '3g') return 'medium';
  return 'high';
}

// Adapt image quality
function getImageSrc(basePath) {
  const quality = getNetworkQuality();
  switch (quality) {
    case 'save-data':
    case 'low':
      return `${basePath}-low.webp`;     // 30 KB
    case 'medium':
      return `${basePath}-medium.webp`;  // 80 KB
    case 'high':
    default:
      return `${basePath}-high.webp`;    // 200 KB
  }
}
```

### Reduced Data Mode

```css
/* Respect user's data-saving preference */
@media (prefers-reduced-data: reduce) {
  .hero-video { display: none; }
  .hero-image-fallback { display: block; }

  /* Replace background images with solid colors */
  .decorative-bg {
    background-image: none;
    background-color: var(--color-surface-secondary);
  }
}
```

### Mobile-Specific Performance Priorities

| Priority | Desktop | Mobile | Reason |
|----------|---------|--------|--------|
| JavaScript budget | 300 KB | 150 KB | Mobile CPUs are 4-6x slower at parsing JS |
| Image format | WebP/AVIF | WebP (wider support) | Older mobile browsers may lack AVIF |
| Font loading | `swap` | `optional` (consider) | Reduce layout shift on slow connections |
| Third-party scripts | Acceptable cost | Defer or remove | Each third-party = DNS + connect + download |
| Animation | GPU-accelerated OK | Reduce or respect `prefers-reduced-motion` | Battery and CPU impact |

### Reduced Motion

```css
/* Respect user preference for reduced motion */
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;
  }
}
```

---

## Measuring UX Performance

### Real User Monitoring (RUM)

| Tool | Type | Key Features |
|------|------|-------------|
| **Web Vitals (npm)** | Library | Lightweight, Core Web Vitals collection |
| **Google Analytics 4** | Service | Built-in Web Vitals reporting |
| **Vercel Analytics** | Service | Per-route Web Vitals, zero config for Next.js |
| **SpeedCurve** | Service | RUM + synthetic, filmstrip, competitive comparison |
| **Sentry Performance** | Service | Error tracking + Web Vitals, transaction tracing |

### Web Vitals API

```javascript
import { onLCP, onINP, onCLS } from 'web-vitals';

function sendToAnalytics(metric) {
  const body = JSON.stringify({
    name: metric.name,
    value: metric.value,
    rating: metric.rating,  // 'good', 'needs-improvement', 'poor'
    id: metric.id,
    navigationType: metric.navigationType,
    url: window.location.href,
  });

  // Use sendBeacon for reliability (works during page unload)
  if (navigator.sendBeacon) {
    navigator.sendBeacon('/analytics', body);
  } else {
    fetch('/analytics', { body, method: 'POST', keepalive: true });
  }
}

onLCP(sendToAnalytics);
onINP(sendToAnalytics);
onCLS(sendToAnalytics);
```

### Lighthouse

| Mode | When to Use | Limitations |
|------|------------|-------------|
| **Navigation** (default) | CI/CD pipeline, pre-deploy checks | Simulated throttling, not real devices |
| **Timespan** | Measure interactions (click, scroll, navigate) | Requires manual scripting |
| **Snapshot** | Audit a specific state (modal open, after interaction) | No loading metrics |

```bash
# Lighthouse CLI in CI
npx lighthouse https://example.com \
  --output=json \
  --output-path=./lighthouse-report.json \
  --chrome-flags="--headless --no-sandbox" \
  --budget-path=./budget.json
```

### Performance Testing in CI

```yaml
# GitHub Actions: Lighthouse CI
name: Performance Audit
on: [pull_request]

jobs:
  lighthouse:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
      - run: npm ci && npm run build

      - name: Run Lighthouse
        uses: treosh/lighthouse-ci-action@v12
        with:
          urls: |
            http://localhost:3000/
            http://localhost:3000/dashboard
          budgetPath: ./budget.json
          uploadArtifacts: true
```

### Metric Correlation with UX Outcomes

| Metric Improvement | Expected UX Outcome | Evidence |
|-------------------|---------------------|----------|
| LCP -1s | +7-13% conversion rate | Google/Deloitte studies |
| INP < 200ms | Users perceive app as "instant" | Human perception threshold |
| CLS < 0.1 | Near-zero rage clicks from layout shifts | FullStory/LogRocket analysis |
| Total page weight -50% | +15-25% engagement on 3G networks | Akamai/Google research |

---

## Modern CSS Surfaces (2026)

Three CSS features now affect interaction and layout *design* decisions, not just implementation. Spec these explicitly in the handoff because they change which problems need JavaScript and which don't.

### View Transitions API

- **What**: native crossfade and morph animations between page or state changes.
- **Status (April 2026)**: same-document API shipped in Chrome, Firefox, Safari (Interop 2025 score 90.8%). Cross-document transitions shipped Safari 18.2; Interop 2026 target.
- **Design decision**: same-document transitions for SPA route or state changes; cross-document for MPA navigation. Replace bespoke JS animation libraries for these cases.
- **Trap**: must specify `view-transition-name` per element pair; without it the transition is a single-element crossfade. Always specify `prefers-reduced-motion` fallback (set transition duration to 0 or disable `view-transition-name`).
- Source: [Chrome Developers — View Transitions in 2025](https://developer.chrome.com/blog/view-transitions-in-2025).

### CSS Anchor Positioning

- **What**: position a popover, tooltip, or dropdown relative to an anchor element without JS.
- **Status (April 2026)**: production in Chromium and WebKit; Firefox in progress. Use `@position-try` for fallback placement when the preferred anchor side overflows.
- **Design decision**: tooltips, popovers, menus, autocompletes, and tour overlays no longer require Floating UI / Popper. Specify anchor element + preferred side + fallback sides in the handoff.
- **Trap**: still needs JS-positioning fallback for older browsers; budget for both code paths until Firefox ships.
- Source: [WebKit — Interop 2026](https://webkit.org/blog/17818/announcing-interop-2026/).

### Scroll-Driven Animations

- **What**: animate properties as a function of scroll position (`animation-timeline: scroll()` or `view()`), no JS.
- **Status (April 2026)**: Chromium production; Safari 26+ rolling out (Interop 2026 focus); Firefox needs fallback.
- **Design decision**: parallax, scroll-linked progress bars, scroll-triggered reveals, and sticky-header transforms can now be CSS-only.
- **Trap (accessibility)**: scroll-driven animations are *invisible* to users with `prefers-reduced-motion: reduce` if not explicitly handled. Wrap any scroll-driven animation in `@media (prefers-reduced-motion: no-preference)` and provide a static fallback that still communicates the visual relationship.
- Source: [MDN — CSS scroll-driven animations](https://developer.mozilla.org/en-US/docs/Web/CSS/Guides/Scroll-driven_animations).

---

## Performance UX Checklist

- [ ] LCP <= 2.5s (lab and field)
- [ ] INP <= 200ms
- [ ] CLS <= 0.1
- [ ] Hero/LCP image preloaded with `fetchpriority="high"`
- [ ] All images have explicit `width` and `height`
- [ ] Below-fold images use `loading="lazy"`
- [ ] JavaScript budget enforced (< 200 KB compressed)
- [ ] Skeleton screens shown for async content
- [ ] Optimistic UI used for user-initiated mutations
- [ ] `font-display: swap` on all font faces
- [ ] Size-adjusted fallback fonts to prevent CLS
- [ ] SPA route transitions have loading indicators
- [ ] Focus managed on route change (a11y)
- [ ] `prefers-reduced-motion` respected
- [ ] `prefers-reduced-data` respected where possible
- [ ] Performance budgets defined and enforced in CI
- [ ] RUM data collected and reviewed regularly

---

## References

- [Web.dev — Core Web Vitals](https://web.dev/articles/vitals)
- [Web.dev — Optimize LCP](https://web.dev/articles/optimize-lcp)
- [Web.dev — Optimize INP](https://web.dev/articles/optimize-inp)
- [Web.dev — Optimize CLS](https://web.dev/articles/optimize-cls)
- [Google — Web Vitals npm Library](https://github.com/GoogleChrome/web-vitals)
- [Lighthouse Documentation](https://developer.chrome.com/docs/lighthouse/)
- [Nielsen, Jakob. "Response Time Limits." Nielsen Norman Group, 1993 (updated).](https://www.nngroup.com/articles/response-times-3-important-limits/)
- [Akamai — The State of Online Retail Performance](https://www.akamai.com/resources)
- [MDN — Network Information API](https://developer.mozilla.org/en-US/docs/Web/API/Network_Information_API)

---

## Cross-References

- [SKILL.md](../SKILL.md) — Parent skill overview and interaction checklist
- [typography-systems.md](typography-systems.md) — Font loading strategies and CLS from fonts
- [mobile-ux-patterns.md](mobile-ux-patterns.md) — Mobile performance expectations and patterns
- [wcag-accessibility.md](wcag-accessibility.md) — Reduced motion and prefers-reduced-data
- [dark-mode-theming.md](dark-mode-theming.md) — Theme-specific image loading considerations
- [data-visualization-ux.md](data-visualization-ux.md) — Lazy loading charts and dashboard performance
