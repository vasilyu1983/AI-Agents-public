# Web Platform APIs Replacing JavaScript Libraries

Native browser APIs that eliminate common JavaScript dependencies. Before running `npm install`, verify whether modern browsers already provide the capability — native APIs cost 0 KB of bundle, run deep in the engine (often off-main-thread), and use optimizations unavailable to userland code.

**Freshness:** Browser support data shifts frequently — verify at use-time via [MDN Browser Compatibility](https://developer.mozilla.org/en-US/docs/MDN/Writing_guidelines/Page_structures/Compatibility_tables) or [caniuse.com](https://caniuse.com).

---

## Table of Contents

1. [Decision Framework](#decision-framework)
2. [Fetch API](#fetch-api)
3. [FormData API](#formdata-api)
4. [URL and URLSearchParams](#url-and-urlsearchparams)
5. [Popover API](#popover-api)
6. [Clipboard API](#clipboard-api)
7. [ResizeObserver](#resizeobserver)
8. [View Transitions API](#view-transitions-api)
9. [Dialog Element](#dialog-element)
10. [Temporal API](#temporal-api)
11. [Geolocation API](#geolocation-api)
12. [Upcoming APIs to Watch](#upcoming-apis-to-watch)
13. [Anti-Patterns](#anti-patterns)

---

## Decision Framework

### When to Prefer Native

- The API covers your use case without polyfills
- Bundle size or dependency count is a concern
- You need only the core capability, not the library's ecosystem (interceptors, plugins, middleware)

### When to Keep the Library

- Library provides superior DX for your specific workflow (validation, state management, animation physics)
- Browser support is incomplete and polyfill cost exceeds library cost
- You need the library's ecosystem (interceptors, retry logic, spring physics, etc.)
- The abstraction handles significant cross-browser edge cases

### Verification Checklist

Before replacing a library with a native API:

1. Check browser support on [caniuse.com](https://caniuse.com) against your support matrix
2. Audit all call sites — ensure the native API covers every usage pattern
3. Review edge cases the library handled (error normalization, retries, encoding quirks)
4. Test on your oldest supported browser

---

## Fetch API

**Replaces:** Axios, jQuery.ajax, request, got (browser builds)

**Browser support:** All modern browsers (since 2017). Universal.

### Minimal Example

```typescript
// GET with JSON parsing
const data = await fetch('/api/users').then(res => {
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
});

// POST with JSON body
const created = await fetch('/api/users', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ name: 'Ada' }),
  signal: AbortSignal.timeout(5000), // built-in timeout
}).then(res => {
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
});
```

### Key Differences from Axios

| Behavior | Fetch | Axios |
|----------|-------|-------|
| HTTP errors | Does NOT throw on 4xx/5xx — check `res.ok` | Throws on non-2xx |
| Request timeout | `AbortSignal.timeout()` | `timeout` config option |
| Interceptors | None — use wrapper function | Built-in request/response interceptors |
| JSON auto-parse | Manual `.json()` call | Automatic |
| Streaming | Native `ReadableStream` | Limited |

### When to Keep Axios

- Large app with centralized auth token injection and request/response transforms
- Need retry logic with exponential backoff (consider `fetch` + a tiny retry wrapper instead)
- Server-side Node.js where you need interceptors (though Node 18+ has native fetch)

---

## FormData API

**Replaces:** Manual form serialization, lightweight use of React Hook Form / Formik (when only serialization is needed)

**Browser support:** All major browsers (since 2015). Universal.

### Minimal Example

```typescript
// Extract all form fields in one line
const form = document.querySelector('form');
const data = new FormData(form);

// Send with fetch — headers set automatically for multipart/form-data
await fetch('/api/submit', { method: 'POST', body: data });

// Access individual values
const email = data.get('email');

// Append file programmatically
data.append('avatar', fileInput.files[0]);
```

### When to Keep Form Libraries

- Multi-step forms with cross-field validation
- Real-time validation feedback and error state management
- Conditional field rendering based on other field values
- Complex form state (dirty tracking, touched fields, submission state)

---

## URL and URLSearchParams

**Replaces:** URL.js, query-string, qs (for basic use cases)

**Browser support:** All major browsers; Node.js 10+. Universal.

### Minimal Example

```typescript
// Parse and inspect URL components
const url = new URL('https://example.com/search?q=web+apis&page=2#results');
url.hostname;    // 'example.com'
url.pathname;    // '/search'
url.hash;        // '#results'

// Read and manipulate query parameters (auto-decodes)
url.searchParams.get('q');        // 'web apis'
url.searchParams.set('page', '3');
url.searchParams.append('lang', 'en');
url.toString();  // full URL with updated params

// Build query strings from scratch
const params = new URLSearchParams({ q: 'hello world', limit: '10' });
params.toString(); // 'q=hello+world&limit=10'
```

### When to Keep a Library

- Need deeply nested object serialization (`qs` handles `a[b][c]=1` patterns)
- Require custom array format encoding (`brackets`, `indices`, `comma`)

---

## Popover API

**Replaces:** Tippy.js, @floating-ui/react (for basic popover/tooltip needs)

**Browser support:** Chrome 114+, Firefox 125+, Safari 17.4+. Reached Baseline Widely Available in April 2025 — treat as safe to use without a fallback for mainstream traffic as of mid-2026, but re-check caniuse.com if your support matrix includes older browser versions.

### Minimal Example

```html
<!-- HTML-only popover — no JavaScript required -->
<button popovertarget="menu">Open Menu</button>
<div id="menu" popover>
  <p>This renders in the top layer — no z-index issues.</p>
</div>
```

Built-in behaviors:
- **Top-layer rendering** — escapes all stacking contexts, solves z-index battles
- **Light dismiss** — closes on outside click or Escape key
- **Focus management** — traps and restores focus automatically

### Limitation

Does NOT handle positioning relative to the trigger element. The popover appears but you must position it yourself with CSS.

### When to Keep Floating UI

- Need intelligent positioning that avoids viewport edges (flip, shift, offset)
- Need arrow elements pointing to the trigger
- Need virtual element anchoring (e.g., right-click context menus)
- **Future:** Anchor Positioning API will close this gap once Safari ships support

---

## Clipboard API

**Replaces:** clipboard.js, copy-to-clipboard

**Browser support:** `writeText()` and `readText()` universally supported. HTTPS required.

### Minimal Example

```typescript
// Copy text — one async call
await navigator.clipboard.writeText('Copied!');

// Read text
const text = await navigator.clipboard.readText();
```

**Security model:** Requires HTTPS, page must be focused, browser manages permission prompts automatically.

### Limitation

Rich content (`write()` for HTML/images) has partial browser support. For plain text copy, the native API is a complete replacement.

---

## ResizeObserver

**Replaces:** element-resize-detector, react-resize-detector, throttled `getBoundingClientRect()` polling

**Browser support:** All major browsers (since July 2020). Universal.

### Minimal Example

```typescript
const observer = new ResizeObserver(entries => {
  for (const entry of entries) {
    const { width, height } = entry.contentRect;
    console.log(`Element resized: ${width}x${height}`);
  }
});

observer.observe(document.querySelector('.panel'));

// Cleanup
observer.disconnect();
```

**Key advantage:** Observes individual elements, not the viewport. Browser auto-batches and debounces callbacks — no manual throttling needed.

### Related: CSS Container Queries

For purely visual adaptation based on container size, prefer `@container` queries over JavaScript:

```css
.card-container { container-type: inline-size; }

@container (min-width: 400px) {
  .card { flex-direction: row; }
}
```

Use ResizeObserver when you need the dimensions in JavaScript (e.g., canvas sizing, dynamic layout calculations).

---

## View Transitions API

**Replaces:** Framer Motion and GSAP for page-level transitions only (not full animation replacement)

**Browser support:** Chrome 111+, Safari 18+, Firefox 144+ (same-page/SPA transitions reached Baseline in 2025). MPA/cross-document transitions: Chrome 126+, Safari 18.2+ — Firefox does not yet support cross-document transitions as of this writing, so treat MPA view transitions as a progressive enhancement, not a guaranteed cross-browser feature.

### Minimal Example

```typescript
// SPA: animate between DOM states
document.startViewTransition(() => {
  // Update the DOM — framework router or manual update
  updateContent(newPageHTML);
});
```

```css
/* Style the transition */
::view-transition-old(root) {
  animation: fade-out 0.3s ease-out;
}
::view-transition-new(root) {
  animation: fade-in 0.3s ease-in;
}
```

### Element Morphing

Assign `view-transition-name` to morph specific elements across state changes:

```css
.hero-image { view-transition-name: hero; }
```

The browser automatically animates the element's position, size, and opacity between old and new states.

### Coverage

Replaces ~80% of page transition use cases. Does NOT handle:

- Spring physics or gesture-driven animations
- Complex choreographed sequences
- Scroll-linked animations (use CSS Scroll-Driven Animations instead)

---

## Dialog Element

**Replaces:** react-modal, @headlessui/react dialog, custom modal implementations

**Browser support:** Chrome 37+, Firefox 98+, Safari 15.4+ (since March 2022). Universal.

### Minimal Example

```html
<dialog id="confirm-dialog">
  <h2>Confirm Action</h2>
  <p>Are you sure?</p>
  <form method="dialog">
    <button value="cancel">Cancel</button>
    <button value="confirm">Confirm</button>
  </form>
</dialog>

<button onclick="document.getElementById('confirm-dialog').showModal()">
  Open
</button>
```

```typescript
const dialog = document.querySelector('dialog');

// Modal (blocks interaction with page, shows backdrop)
dialog.showModal();

// Non-modal (page remains interactive)
dialog.show();

// Read which button closed it
dialog.addEventListener('close', () => {
  console.log(dialog.returnValue); // 'cancel' or 'confirm'
});
```

Built-in behaviors:
- **Top-layer rendering** — no z-index management
- **`::backdrop` pseudo-element** — style the overlay with CSS
- **Focus trap** — automatic in modal mode
- **Escape key** — closes modal automatically
- **Focus restoration** — returns focus to trigger on close

### Limitation

No built-in entrance/exit animations. Implementable with CSS transitions; native animation support is in development.

---

## Temporal API

**Replaces:** Moment.js, date-fns, Day.js, Luxon

**Status:** TC39 Stage 4 — advanced in the ECMAScript 2026 specification (this is a large jump from Stage 3; re-verify at TC39's proposal-temporal repo if this file is stale). Stage 4 means the spec is finished, but runtime support still lags. **Polyfill still required for production cross-browser reach.**

**Browser support:** Firefox 139+ (May 2025), Chrome 144+ (Jan 2026), Node.js 26+ (May 2026). Safari and Edge: not yet shipped as of this writing.

### Minimal Example

```typescript
// Immutable date arithmetic — original unchanged
const date = Temporal.PlainDate.from('2025-02-14');
const later = date.add({ months: 3 }); // 2025-05-14

// First-class timezone support
const meeting = Temporal.ZonedDateTime.from({
  timeZone: 'America/New_York',
  year: 2025, month: 6, day: 15,
  hour: 14, minute: 30,
});

// Type-safe distinctions
Temporal.PlainDate      // date only (no time, no timezone)
Temporal.PlainTime      // time only
Temporal.PlainDateTime  // date + time (no timezone)
Temporal.ZonedDateTime  // date + time + timezone
Temporal.Instant        // exact moment in time (like Unix timestamp)
```

### Current Recommendation

**Not production-ready without polyfill.** Until Safari ships support:

- Use `@js-temporal/polyfill` or `temporal-polyfill` if you want to adopt early
- Otherwise stick with **date-fns** (tree-shakeable) or **Day.js** (lightweight)
- Avoid Moment.js for new projects (deprecated, not tree-shakeable)

---

## Geolocation API

**Replaces:** IP geolocation services (ipapi.co, ip-api.com, MaxMind, IPinfo) for device-level location

**Browser support:** Universal. HTTPS required.

### Minimal Example

```typescript
// One-time position
navigator.geolocation.getCurrentPosition(
  (pos) => {
    const { latitude, longitude, accuracy } = pos.coords;
    console.log(`${latitude}, ${longitude} ±${accuracy}m`);
  },
  (err) => console.error(err.message),
  { enableHighAccuracy: true, timeout: 10000 }
);

// Continuous tracking
const watchId = navigator.geolocation.watchPosition(callback);
navigator.geolocation.clearWatch(watchId); // stop
```

**Key advantage:** GPS-level precision (meters) vs IP geolocation (city-level, VPN-affected).

**Privacy:** Browser shows a permission prompt — user explicitly grants access.

### When to Keep IP Geolocation

- Need approximate location without prompting the user (e.g., default currency, language)
- Server-side location detection where no browser API is available
- Analytics where you need location for all visitors, not just those who grant permission

---

## Upcoming APIs to Watch

| API | Status (verify at use-time) | Replaces |
|-----|---------------------|----------|
| **Anchor Positioning API** | Chrome 125+; Safari/Firefox in development | Floating UI positioning logic |
| **CSS Container Queries** | Baseline — stable in Chrome 130+, Safari 18+, Firefox 130+; container *style* queries (not just size) still landing across browsers | Many ResizeObserver viewport-adaptation patterns |
| **CSS Scroll-Driven Animations** | Chrome 115+, Firefox 110+; Safari partial | Scroll-linked animation libraries (ScrollMagic, GSAP ScrollTrigger) |
| **Navigation API** | Chrome 102+; Firefox/Safari not yet | Client-side router history management |

Note: `:has()` and CSS nesting (both referenced elsewhere in this skill's styling guidance) are no longer "upcoming" — both reached Baseline in 2023 and are safe to use without fallbacks.

---

## Anti-Patterns

| Anti-Pattern | Why It Fails |
|---|---|
| Dropping a library without checking browser support matrix | Breaks for users on older browsers within your support range |
| Using Temporal API without polyfill in production | Safari and Edge users get runtime errors |
| Replacing Framer Motion entirely with View Transitions | View Transitions covers page transitions only — not spring physics, gestures, or choreographed sequences |
| Replacing Floating UI with Popover API alone | Popover renders in top layer but does NOT position relative to the trigger |
| Removing `clipboard.js` on HTTP sites | Clipboard API requires HTTPS |
| Swapping `react-modal` for `<dialog>` without testing animations | `<dialog>` lacks built-in enter/exit transitions |
| Using native Geolocation as a drop-in for IP geolocation | Geolocation prompts the user — IP geolocation is silent; different use cases |
