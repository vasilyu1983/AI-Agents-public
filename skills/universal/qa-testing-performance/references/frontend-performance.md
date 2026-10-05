# Frontend Performance

Core Web Vitals measurement, Lighthouse CI integration, bundle size tracking, and rendering performance optimization.

## Table of Contents

- [Core Web Vitals](#core-web-vitals)
- [LCP (Largest Contentful Paint)](#lcp-largest-contentful-paint)
- [INP (Interaction to Next Paint)](#inp-interaction-to-next-paint)
- [CLS (Cumulative Layout Shift)](#cls-cumulative-layout-shift)
- [Lighthouse CI](#lighthouse-ci)
- [Setup](#setup)
- [Assertions Configuration](#assertions-configuration)
- [Lighthouse CI Server](#lighthouse-ci-server)
- [Start Lighthouse CI server](#start-lighthouse-ci-server)
- [Configure upload target in lighthouserc.json](#configure-upload-target-in-lighthousercjson)
- [Byte and Request-Count Budgets](#byte-and-request-count-budgets)
- [Bundle Size Tracking](#bundle-size-tracking)
- [size-limit](#size-limit)
- [Bundle Analysis](#bundle-analysis)
- [CI Integration for Bundle Size](#ci-integration-for-bundle-size)
- [Resource Loading Optimization](#resource-loading-optimization)
- [Synthetic vs RUM Monitoring](#synthetic-vs-rum-monitoring)
- [Implementing RUM with web-vitals](#implementing-rum-with-web-vitals)
- [Performance Testing with Playwright](#performance-testing-with-playwright)
- [Rendering Performance](#rendering-performance)
- [Frontend Diagnosis Traps](#frontend-diagnosis-traps)

## Core Web Vitals

Google's Core Web Vitals are the primary frontend performance metrics. They represent real user experience.

### LCP (Largest Contentful Paint)

Measures loading performance — when the largest visible content element finishes rendering.

| Rating | Threshold |
|--------|-----------|
| Good | <= 2.5s |
| Needs improvement | 2.5s - 4.0s |
| Poor | > 4.0s |

**Note:** Take the LCP threshold from `developers.google.com/search/docs/appearance/core-web-vitals`, not from SEO publications, which have reported unconfirmed threshold changes. Check the source before adjusting CI budgets.

**Common LCP issues and fixes:**
- Slow server response → optimize TTFB, use CDN, cache HTML
- Render-blocking resources → defer non-critical CSS/JS, inline critical CSS
- Slow resource load → preload LCP image, use modern formats (WebP/AVIF), responsive images
- Client-side rendering → SSR/SSG for critical content, streaming HTML

### INP (Interaction to Next Paint)

Measures responsiveness — the latency between user interaction and the next visual update. Replaced FID.

| Rating | Threshold |
|--------|-----------|
| Good | <= 200ms |
| Needs improvement | 200ms - 500ms |
| Poor | > 500ms |

**Common INP issues and fixes:**
- Long tasks blocking main thread → break into smaller tasks, use `scheduler.yield()`
- Heavy event handlers → debounce, defer non-visual work, use web workers
- Layout thrashing → batch DOM reads/writes, use `requestAnimationFrame`
- Hydration blocking → progressive hydration, islands architecture, partial hydration

### CLS (Cumulative Layout Shift)

Measures visual stability — how much visible content shifts unexpectedly during the page lifecycle.

| Rating | Threshold |
|--------|-----------|
| Good | <= 0.1 |
| Needs improvement | 0.1 - 0.25 |
| Poor | > 0.25 |

**Common CLS issues and fixes:**
- Images without dimensions → always set width/height or aspect-ratio
- Dynamically injected content → reserve space with min-height or skeleton loaders
- Web fonts causing FOUT → `font-display: swap` with size-adjusted fallback, preload fonts
- Ads/embeds without reserved space → set explicit container dimensions

## Lighthouse CI

### Setup

```bash
npm install -g @lhci/cli
lhci autorun  # uses lighthouserc.json
```

### Assertions Configuration

```json
{
  "ci": {
    "collect": {
      "url": [
        "http://localhost:3000/",
        "http://localhost:3000/products",
        "http://localhost:3000/checkout"
      ],
      "numberOfRuns": 5,
      "settings": {
        "chromeFlags": "--no-sandbox",
        "throttling": {
          "cpuSlowdownMultiplier": 4,
          "downloadThroughputKbps": 1600,
          "uploadThroughputKbps": 750,
          "rttMs": 150
        }
      }
    },
    "assert": {
      "assertions": {
        "categories:performance": ["error", { "minScore": 0.9 }],
        "largest-contentful-paint": ["error", { "maxNumericValue": 2500 }],
        "cumulative-layout-shift": ["error", { "maxNumericValue": 0.1 }],
        "total-blocking-time": ["warn", { "maxNumericValue": 300 }],
        "total-byte-weight": ["warn", { "maxNumericValue": 500000 }],
        "image-delivery-insight": ["warn", { "minScore": 1 }]
      }
    }
  }
}
```

**Audit compatibility:** read the audit IDs in the Lighthouse version bundled by your reviewed `@lhci/cli` dependency. Legacy audits can move to Insights or disappear; confirm each assertion ID and score/numeric semantics in the actual report before it becomes a gate. Navigation runs use TBT as a lab proxy, not a field-INP measurement.

### Lighthouse CI Server

For historical tracking and comparison:

```bash
# Start Lighthouse CI server
npx --no-install lhci server --storage.storageMethod=sql \
  --storage.sqlDialect=sqlite \
  --storage.sqlDatabasePath=./lhci.db

# Configure upload target in lighthouserc.json
{
  "ci": {
    "upload": {
      "target": "lhci",
      "serverBaseUrl": "http://lhci-server.internal:9001"
    }
  }
}
```

## Byte and Request-Count Budgets

LHCI can gate on total transfer size and request count per resource type, not just Lighthouse category scores:

```json
{
  "ci": {
    "assert": {
      "assertions": {
        "resource-summary:script:size": ["error", { "maxNumericValue": 300000 }],
        "resource-summary:image:size": ["warn", { "maxNumericValue": 500000 }],
        "resource-summary:third-party:count": ["warn", { "maxNumericValue": 10 }]
      }
    }
  }
}
```

Note: `budgetsFile` (the separate Lighthouse budgets.json format) cannot be combined with other `assert.assertions` options in the same LHCI config — pick one mechanism per project rather than mixing them.

## Bundle Size Tracking

### size-limit

```json
// package.json
{
  "size-limit": [
    { "path": "dist/index.js", "limit": "45 KB", "gzip": true },
    { "path": "dist/vendor.js", "limit": "120 KB", "gzip": true },
    { "path": "dist/**/*.css", "limit": "25 KB", "gzip": true }
  ]
}
```

```bash
npx size-limit  # check sizes, fail if over limit
npx size-limit --why  # show what contributes to bundle size
```

### Bundle Analysis

```bash
# Webpack
npx webpack-bundle-analyzer stats.json

# Vite / Rollup
npx vite-bundle-visualizer

# Next.js
ANALYZE=true next build  # requires @next/bundle-analyzer
```

### CI Integration for Bundle Size

```yaml
# GitHub Actions — size-limit with PR comment
- uses: andresz1/size-limit-action@v1
  with:
    github_token: ${{ secrets.GITHUB_TOKEN }}
    build_script: build
```

## Resource Loading Optimization

Resource-loading fixes (priority hints, image formats, code splitting) are optimization advice, not testing, and are owned by [software-frontend performance-optimization](../../software-frontend/references/performance-optimization.md). This skill's job is to measure whether a change helped: gate on the CWV/bundle budgets above, and see [Frontend Diagnosis Traps](#frontend-diagnosis-traps) for the one optimization-adjacent trap worth knowing before you interpret a `fetchpriority="high"` experiment (avoid assigning high priority indiscriminately).

## Synthetic vs RUM Monitoring

| Aspect | Synthetic (Lab) | RUM (Field) |
|--------|----------------|-------------|
| Use for | CI gates, trend tracking, debugging | Real user experience, geographic/device insights |
| Data source | Controlled test runs | Real user browsers |
| Consistency | High (same conditions) | Variable (real-world conditions) |
| Coverage | Configured URLs only | All pages visited by real users |
| Tools | Lighthouse, WebPageTest, SpeedCurve | CrUX, web-vitals library, Sentry, Datadog RUM |
| CI integration | Yes (primary use) | No (production only) |

### Implementing RUM with web-vitals

```javascript
import { onLCP, onINP, onCLS } from 'web-vitals';

function sendToAnalytics(metric) {
  const body = JSON.stringify({
    name: metric.name,
    value: metric.value,
    rating: metric.rating,  // "good", "needs-improvement", "poor"
    delta: metric.delta,
    id: metric.id,
    navigationType: metric.navigationType,
  });
  navigator.sendBeacon('/api/vitals', body);
}

onLCP(sendToAnalytics);
onINP(sendToAnalytics);
onCLS(sendToAnalytics);
```

## Performance Testing with Playwright

Use an explicit page readiness marker and a bounded collection interval; fail the test if the expected LCP element or metric is absent. Observe buffered LCP candidates and retain the latest candidate through that interval, disconnect the observer on completion, and label the result a lab observation. The first observer callback is not necessarily final LCP, and `networkidle` does not establish application readiness. Confirm field p75 separately.

## Rendering Performance

Rendering-level fixes (layout thrashing, CSS containment, list virtualization, compositor-only animations) are implementation guidance owned by [software-frontend performance-optimization](../../software-frontend/references/performance-optimization.md), not testing. The one item worth keeping here: **monitor Long Animation Frames (LoAF)**, a frame-level complement to Long Tasks — it attributes *what* caused a slow frame, which is what makes an INP regression in a load/RUM test actionable instead of just a number.

## Frontend Diagnosis Traps

- **FID vs INP** — FID (First Input Delay) is retired as a Core Web Vital; do not report it alongside INP as if they measure the same thing. FID only captured the first interaction's delay; INP evaluates the interaction distribution across the page lifecycle, discarding outliers for pages with many interactions; check the current calculation at [web.dev/inp](https://web.dev/articles/inp).
- **`fetchpriority="high"` is a relative hint** — prioritize the confirmed LCP resource and avoid raising unrelated resources indiscriminately; it is not restricted by the API to a single element.
- **`font-display: optional`** — the browser may skip the web font entirely on a slow connection rather than show it late; this trades CLS/FOUT risk for a guaranteed-fast first render, and is a deliberate choice, not a bug.
- **TTFB and FCP are diagnostic, not CWV metrics** — they are useful for narrowing down *why* LCP is slow and may have explicit diagnostic budgets, but do not treat them as substitutes for CWV or claim a navigation audit measures field INP.
- **Budgets should differ per page type** — a marketing landing page and an authenticated dashboard have different realistic LCP/bundle budgets; a single global budget either fails the heavy page constantly or hides regressions on the light one.
- **INP methodology has changed across Chrome versions** — verify the current INP calculation and reporting window against `web.dev/articles/inp` before citing a specific percentile methodology as current.
