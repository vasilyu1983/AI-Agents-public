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
- [Bundle Size Tracking](#bundle-size-tracking)
- [size-limit](#size-limit)
- [Bundle Analysis](#bundle-analysis)
- [Webpack](#webpack)
- [Vite / Rollup](#vite-rollup)
- [Next.js](#nextjs)
- [CI Integration for Bundle Size](#ci-integration-for-bundle-size)
- [GitHub Actions — size-limit with PR comment](#github-actions-—-size-limit-with-pr-comment)
- [Resource Loading Optimization](#resource-loading-optimization)
- [Priority Hints](#priority-hints)
- [Image Optimization](#image-optimization)
- [Code Splitting](#code-splitting)
- [Synthetic vs RUM Monitoring](#synthetic-vs-rum-monitoring)
- [Implementing RUM with web-vitals](#implementing-rum-with-web-vitals)
- [Performance Testing with Playwright](#performance-testing-with-playwright)
- [Rendering Performance](#rendering-performance)

## Core Web Vitals

Google's Core Web Vitals are the primary frontend performance metrics. They represent real user experience.

### LCP (Largest Contentful Paint)

Measures loading performance — when the largest visible content element finishes rendering.

| Rating | Threshold |
|--------|-----------|
| Good | <= 2.5s |
| Needs improvement | 2.5s - 4.0s |
| Poor | > 4.0s |

**Note (verified 2026-07-11):** The official Google threshold remains 2.5s per `developers.google.com/search/docs/appearance/core-web-vitals`. Several SEO publications claim Google tightened LCP to 2.0s in a March 2026 core update; this has not been confirmed in official Google documentation. Verify at the source before adjusting CI budgets.

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
        "uses-responsive-images": ["warn", { "minScore": 1 }],
        "uses-text-compression": ["error", { "minScore": 1 }]
      }
    }
  }
}
```

### Lighthouse CI Server

For historical tracking and comparison:

```bash
# Start Lighthouse CI server
npx @lhci/cli@latest server --storage.storageMethod=sql \
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

### Priority Hints

```html
<!-- Preload LCP image -->
<link rel="preload" as="image" href="/hero.webp" fetchpriority="high">

<!-- Defer non-critical scripts -->
<script src="/analytics.js" defer fetchpriority="low"></script>

<!-- Preconnect to critical origins -->
<link rel="preconnect" href="https://api.example.com">
```

### Image Optimization

- Use modern formats: WebP (95%+ browser support), AVIF (growing support)
- Responsive images with `srcset` and `sizes`
- Lazy-load below-the-fold images: `loading="lazy"`
- Explicit dimensions to prevent CLS

### Code Splitting

- Route-based splitting (default in Next.js, Nuxt, Remix)
- Component-based lazy loading: `React.lazy()`, Vue `defineAsyncComponent()`
- Dynamic imports for heavy libraries: `const chart = await import('chart.js')`

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

```javascript
// Playwright — measure Core Web Vitals in E2E tests
const { test, expect } = require('@playwright/test');

test('homepage meets performance budget', async ({ page }) => {
  await page.goto('/', { waitUntil: 'networkidle' });

  // Measure LCP via PerformanceObserver
  const lcp = await page.evaluate(() => {
    return new Promise((resolve) => {
      new PerformanceObserver((list) => {
        const entries = list.getEntries();
        resolve(entries[entries.length - 1].startTime);
      }).observe({ type: 'largest-contentful-paint', buffered: true });
    });
  });

  expect(lcp).toBeLessThan(2500);
});
```

## Rendering Performance

- **Avoid layout thrashing** — batch DOM reads before DOM writes.
- **Use CSS containment** — `contain: layout style paint` to isolate rendering.
- **Virtualize long lists** — render only visible items (TanStack Virtual, react-window).
- **Optimize animations** — use `transform` and `opacity` only (compositor-only properties), prefer CSS animations over JS.
- **Monitor Long Animation Frames (LoAF)** — the successor to Long Tasks, provides attribution for what caused slow frames.
