# Frontend Performance Optimization

Actionable patterns for optimizing Core Web Vitals (LCP, INP, CLS), bundle size, images, fonts, React rendering, Server Components, and third-party scripts. Includes measurement tooling and decision frameworks.

---

## Table of Contents

1. [Core Web Vitals Optimization](#core-web-vitals-optimization)
2. [Bundle Analysis and Code Splitting](#bundle-analysis-and-code-splitting)
3. [Image Optimization](#image-optimization)
4. [Font Optimization](#font-optimization)
5. [React Performance](#react-performance)
6. [Server Components Performance](#server-components-performance)
7. [Third-Party Script Management](#third-party-script-management)
8. [Measurement and Tooling](#measurement-and-tooling)
9. [Anti-Patterns](#anti-patterns)

---

## Core Web Vitals Optimization

### Targets

| Metric | Good | Needs Improvement | Poor |
|--------|------|-------------------|------|
| LCP (Largest Contentful Paint) | <= 2.5s | 2.5-4.0s | > 4.0s |
| INP (Interaction to Next Paint) | <= 200ms | 200-500ms | > 500ms |
| CLS (Cumulative Layout Shift) | <= 0.1 | 0.1-0.25 | > 0.25 |
| TTFB (Time to First Byte) | < 600ms | 600-1000ms | > 1000ms |

### LCP Optimization

The LCP element is typically the largest image or text block in the viewport.

```text
LCP Optimization Checklist:
  1. Identify the LCP element (use Lighthouse or Web Vitals extension)
  2. Preload the LCP resource (image, font, or critical CSS)
  3. Eliminate render-blocking resources before LCP
  4. Optimize server response time (TTFB)
  5. Avoid client-side rendering for above-the-fold content
```

```typescript
// Preload LCP image in Next.js
import Image from 'next/image';

// priority={true} adds <link rel="preload"> for the image
export default function HeroSection() {
  return (
    <Image
      src="/hero-image.webp"
      alt="Hero"
      width={1200}
      height={600}
      priority  // Preloads the image, disables lazy loading
      sizes="100vw"
    />
  );
}
```

```html
<!-- Manual preload for critical resources -->
<head>
  <!-- Preload LCP image -->
  <link rel="preload" as="image" href="/hero.webp" fetchpriority="high" />

  <!-- Preload critical font -->
  <link rel="preload" as="font" type="font/woff2"
        href="/fonts/Inter-var.woff2" crossorigin />

  <!-- Preconnect to external origins -->
  <link rel="preconnect" href="https://cdn.example.com" />
  <link rel="dns-prefetch" href="https://analytics.example.com" />
</head>
```

### INP Optimization

INP measures the responsiveness of all user interactions (clicks, taps, keyboard).

```typescript
// PROBLEM: Long task blocks the main thread
function handleClick() {
  // 500ms of synchronous work = poor INP
  const result = expensiveCalculation(largeDataset);
  setResult(result);
}

// FIX 1: Break up long tasks with yield
function handleClick() {
  // Process in chunks, yielding to the browser between chunks
  requestIdleCallback(() => {
    const chunk1 = processChunk(data, 0, 100);
    requestIdleCallback(() => {
      const chunk2 = processChunk(data, 100, 200);
      setResult([...chunk1, ...chunk2]);
    });
  });
}

// FIX 2: Move heavy work to Web Worker
// worker.ts
self.onmessage = (event) => {
  const result = expensiveCalculation(event.data);
  self.postMessage(result);
};

// component.tsx
const worker = new Worker(new URL('./worker.ts', import.meta.url));
function handleClick() {
  worker.postMessage(largeDataset);
  worker.onmessage = (event) => setResult(event.data);
}

// FIX 3: Use startTransition for non-urgent updates
import { startTransition } from 'react';

function handleInput(value: string) {
  // Urgent: update the input field immediately
  setInputValue(value);

  // Non-urgent: update the filtered list (can be interrupted)
  startTransition(() => {
    setFilteredItems(items.filter(item => item.name.includes(value)));
  });
}
```

### CLS Optimization

CLS measures visual stability -- elements shifting unexpectedly during page load.

```typescript
// PROBLEM: Image without dimensions causes layout shift
<img src="/photo.jpg" alt="Photo" />
// Image loads -> pushes content down -> CLS

// FIX: Always set width and height (or aspect-ratio)
<img src="/photo.jpg" alt="Photo" width={800} height={600} />

// Next.js Image handles this automatically
<Image src="/photo.jpg" alt="Photo" width={800} height={600} />
```

Common CLS causes and fixes:

| Cause | Fix |
|-------|-----|
| Images without dimensions | Set `width` and `height` or `aspect-ratio` |
| Ads/embeds without reserved space | Use placeholder with fixed dimensions |
| Web fonts causing FOIT/FOUT | Use `font-display: swap` + `size-adjust` |
| Dynamic content inserted above viewport | Insert below the fold or use transform animations |
| Late-loading CSS changing layout | Inline critical CSS, defer non-critical |

---

## Bundle Analysis and Code Splitting

### Bundle Analysis

```bash
# Next.js bundle analyzer
npm install @next/bundle-analyzer

# Run build with analysis
ANALYZE=true npm run build
```

```typescript
// next.config.ts
import withBundleAnalyzer from '@next/bundle-analyzer';

const config = withBundleAnalyzer({
  enabled: process.env.ANALYZE === 'true',
})({
  // ... next config
});

export default config;
```

### Code Splitting Strategies

```typescript
// 1. Route-based splitting (automatic in Next.js App Router)
// Each page in app/ is automatically code-split

// 2. Component-level splitting with dynamic import
import dynamic from 'next/dynamic';

const HeavyChart = dynamic(() => import('@/components/Chart'), {
  loading: () => <div className="h-64 animate-pulse bg-muted" />,
  ssr: false,  // Skip server-side rendering for client-only components
});

// 3. Library-level splitting
const DatePicker = dynamic(
  () => import('react-datepicker').then(mod => mod.default),
  { ssr: false }
);
```

### Dynamic Imports for Heavy Libraries

```typescript
// WRONG: Import at the top level (included in main bundle)
import { format, parseISO, differenceInDays } from 'date-fns';

// RIGHT: Dynamic import when needed
async function formatDate(date: string) {
  const { format, parseISO } = await import('date-fns');
  return format(parseISO(date), 'MMM d, yyyy');
}

// RIGHT: Conditional dynamic import
async function processCSV(file: File) {
  const Papa = (await import('papaparse')).default;
  return Papa.parse(file, { header: true });
}
```

### Tree Shaking Verification

```typescript
// BAD: Import entire library
import _ from 'lodash';
const sorted = _.sortBy(items, 'name');
// Includes ALL of lodash in bundle (~70KB)

// GOOD: Import specific function
import sortBy from 'lodash/sortBy';
const sorted = sortBy(items, 'name');
// Only includes sortBy (~2KB)

// BETTER: Use native methods or lodash-es
import { sortBy } from 'lodash-es';  // ES modules, tree-shakeable
```

### Bundle Size Budgets

| Category | Budget | Check |
|----------|--------|-------|
| First Load JS (shared) | < 100KB gzipped | `next build` output |
| Per-page JS | < 50KB gzipped | `next build` output |
| Total page weight | < 500KB | Lighthouse |
| Largest dependency | < 50KB gzipped | Bundle analyzer |

---

## Image Optimization

### Next.js Image Component

```typescript
import Image from 'next/image';

// Responsive image with automatic optimization
<Image
  src="/products/shoe.jpg"
  alt="Running shoe"
  width={800}
  height={600}
  sizes="(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 33vw"
  placeholder="blur"
  blurDataURL={shimmerDataUrl}  // Low-quality placeholder
/>

// Fill mode for unknown dimensions (parent must be positioned)
<div className="relative h-64 w-full">
  <Image
    src="/banner.jpg"
    alt="Banner"
    fill
    className="object-cover"
    sizes="100vw"
  />
</div>
```

### Format Selection

| Format | Use Case | Browser Support | Size vs JPEG |
|--------|----------|-----------------|-------------|
| AVIF | Best compression, photos | Chrome, Firefox, Safari 16+ | 50-70% smaller |
| WebP | Good compression, wide support | All modern browsers | 25-35% smaller |
| JPEG | Fallback for old browsers | Universal | Baseline |
| PNG | Transparency needed | Universal | Larger for photos |
| SVG | Icons, logos, illustrations | Universal | Scalable, tiny for simple graphics |

```typescript
// Next.js automatically serves AVIF/WebP with fallback
// Configure in next.config.ts:
const nextConfig = {
  images: {
    formats: ['image/avif', 'image/webp'],
    deviceSizes: [640, 750, 828, 1080, 1200, 1920],
    imageSizes: [16, 32, 48, 64, 96, 128, 256],
  },
};
```

### Lazy Loading

```typescript
// Default: Images below the fold are lazy-loaded automatically
<Image src="/photo.jpg" alt="Photo" width={400} height={300} />
// loading="lazy" is the default

// LCP image: disable lazy loading
<Image src="/hero.jpg" alt="Hero" width={1200} height={600} priority />
// priority adds loading="eager" and preload link

// Native HTML lazy loading
<img src="/photo.jpg" alt="Photo" loading="lazy" width="400" height="300" />
```

### Image Optimization Checklist

- [ ] LCP image has `priority` prop (or `fetchpriority="high"`)
- [ ] All images have explicit `width` and `height` (prevents CLS)
- [ ] `sizes` attribute matches actual rendered size (prevents over-fetching)
- [ ] AVIF/WebP formats configured
- [ ] Below-fold images use lazy loading (default in Next.js)
- [ ] Placeholder (blur or shimmer) for large images
- [ ] SVG for icons and logos (not raster images)

---

## Font Optimization

### Next.js Font Optimization

```typescript
// app/layout.tsx
import { Inter, JetBrains_Mono } from 'next/font/google';

const inter = Inter({
  subsets: ['latin'],
  display: 'swap',           // Prevents FOIT
  variable: '--font-inter',  // CSS variable for Tailwind
});

const jetbrainsMono = JetBrains_Mono({
  subsets: ['latin'],
  display: 'swap',
  variable: '--font-mono',
});

export default function RootLayout({ children }) {
  return (
    <html className={`${inter.variable} ${jetbrainsMono.variable}`}>
      <body className="font-sans">{children}</body>
    </html>
  );
}
```

### Font Loading Strategy

| Strategy | `font-display` | Behavior | Best For |
|----------|---------------|----------|----------|
| Swap | `swap` | Show fallback, swap when loaded | Body text |
| Optional | `optional` | Show fallback, use font only if cached | Non-critical text |
| Fallback | `fallback` | Brief blank, then fallback, then swap | Headings |
| Block | `block` | Invisible text until font loads | Icon fonts (avoid these) |

### Variable Fonts

```css
/* Variable fonts: one file, all weights */
@font-face {
  font-family: 'Inter';
  src: url('/fonts/Inter-var.woff2') format('woff2');
  font-weight: 100 900;  /* Full weight range */
  font-display: swap;
  font-style: normal;
}

/* vs static fonts: one file per weight */
/* Inter-Regular.woff2, Inter-Bold.woff2, Inter-SemiBold.woff2 */
/* 3 files = 3 requests = more bytes */
```

### Preloading Critical Fonts

```html
<!-- Preload the most critical font file -->
<link
  rel="preload"
  href="/fonts/Inter-var.woff2"
  as="font"
  type="font/woff2"
  crossorigin
/>
```

### Font Subsetting

```bash
# Reduce font file size by including only needed characters
# Use fonttools/pyftsubset
pyftsubset Inter-var.woff2 \
  --unicodes="U+0000-007F,U+00A0-00FF" \
  --layout-features="kern,liga" \
  --flavor=woff2 \
  --output-file=Inter-var-latin.woff2
```

---

## React Performance

### memo, useMemo, useCallback

```typescript
// React.memo: skip re-render if props haven't changed
const ExpensiveList = React.memo(function ExpensiveList({
  items
}: {
  items: Item[]
}) {
  return (
    <ul>
      {items.map(item => (
        <ExpensiveItem key={item.id} item={item} />
      ))}
    </ul>
  );
});

// useMemo: memoize expensive computation
function Dashboard({ data }: { data: DataPoint[] }) {
  const aggregated = useMemo(() => {
    return data.reduce((acc, point) => {
      // Expensive aggregation
      return computeAggregate(acc, point);
    }, initialValue);
  }, [data]);

  return <Chart data={aggregated} />;
}

// useCallback: stable function reference for child props
function ParentComponent() {
  const [filter, setFilter] = useState('');

  const handleSelect = useCallback((id: string) => {
    // Only recreated when filter changes
    applyFilter(id, filter);
  }, [filter]);

  return <MemoizedChild onSelect={handleSelect} />;
}
```

### React Compiler (Next.js 16+)

```typescript
// next.config.ts
const nextConfig: NextConfig = {
  experimental: {
    reactCompiler: true,
  },
};

// With React Compiler enabled:
// - memo, useMemo, useCallback are automatically inserted
// - Manual memoization is usually unnecessary
// - Components are automatically optimized for minimal re-renders

// Before (manual optimization):
const MemoizedComponent = React.memo(({ data }) => {
  const processed = useMemo(() => transform(data), [data]);
  return <div>{processed}</div>;
});

// After (React Compiler handles it):
function Component({ data }) {
  const processed = transform(data);
  return <div>{processed}</div>;
}
```

### Virtualization for Long Lists

```typescript
// Use @tanstack/react-virtual for large lists
import { useVirtualizer } from '@tanstack/react-virtual';

function VirtualList({ items }: { items: Item[] }) {
  const parentRef = useRef<HTMLDivElement>(null);

  const virtualizer = useVirtualizer({
    count: items.length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => 50,  // Estimated row height
    overscan: 5,             // Render 5 extra items above/below
  });

  return (
    <div ref={parentRef} className="h-[600px] overflow-auto">
      <div
        style={{
          height: `${virtualizer.getTotalSize()}px`,
          position: 'relative',
        }}
      >
        {virtualizer.getVirtualItems().map((virtualItem) => (
          <div
            key={virtualItem.key}
            style={{
              position: 'absolute',
              top: 0,
              transform: `translateY(${virtualItem.start}px)`,
              height: `${virtualItem.size}px`,
              width: '100%',
            }}
          >
            <ItemRow item={items[virtualItem.index]} />
          </div>
        ))}
      </div>
    </div>
  );
}
```

---

## Server Components Performance

### Benefits

```text
Server Components eliminate:
  - Component JS from the client bundle
  - Data fetching waterfalls (fetch on server, stream HTML)
  - Hydration cost for static content

Example impact:
  Before (Client Components): 150KB JS, 3 API waterfall requests
  After (Server Components):   40KB JS, 0 client requests
```

### Patterns for Optimal Performance

```typescript
// Pattern 1: Data fetching at the page level (server)
// app/products/page.tsx
export default async function ProductsPage() {
  // Fetch on server -- no API call from client
  const products = await db.product.findMany();

  return (
    <div>
      <h1>Products</h1>
      {/* Static list rendered on server */}
      <ProductList products={products} />
      {/* Interactive search is a Client Component */}
      <ProductSearch />
    </div>
  );
}

// Pattern 2: Streaming with Suspense
export default async function Dashboard() {
  return (
    <div>
      {/* Fast: renders immediately */}
      <DashboardHeader />

      {/* Slow: streams in when ready */}
      <Suspense fallback={<ChartSkeleton />}>
        <ExpensiveChart />
      </Suspense>

      <Suspense fallback={<TableSkeleton />}>
        <DataTable />
      </Suspense>
    </div>
  );
}

// Pattern 3: Parallel data fetching
async function Dashboard() {
  // Fetch in parallel, not sequentially
  const [users, posts, metrics] = await Promise.all([
    fetchUsers(),
    fetchPosts(),
    fetchMetrics(),
  ]);

  return (
    <div>
      <UserSummary users={users} />
      <RecentPosts posts={posts} />
      <MetricsChart metrics={metrics} />
    </div>
  );
}
```

### Client Component Boundaries

```text
Minimize the "use client" surface area:
  Page (Server)
    +-- Header (Server)
    +-- Sidebar (Server)
    +-- Content (Server)
    |   +-- DataTable (Server) -- fetches data
    |       +-- SortButton (Client) -- needs onClick
    |       +-- FilterDropdown (Client) -- needs state
    +-- Footer (Server)

Push "use client" as deep as possible in the component tree.
```

---

## Third-Party Script Management

### Loading Strategies

| Strategy | When to Use | Impact |
|----------|-------------|--------|
| `afterInteractive` (default) | Analytics, chat widgets | Loads after hydration |
| `lazyOnload` | Non-essential scripts | Loads during idle time |
| `beforeInteractive` | Critical polyfills | Blocks hydration (use sparingly) |
| `worker` (Partytown) | Analytics, ads | Runs in Web Worker |

```typescript
// Next.js Script component
import Script from 'next/script';

// Analytics: load after page is interactive
<Script
  src="https://analytics.example.com/script.js"
  strategy="afterInteractive"
/>

// Chat widget: load when browser is idle
<Script
  src="https://chat.example.com/widget.js"
  strategy="lazyOnload"
/>

// Move analytics to Web Worker (zero main-thread impact)
<Script
  src="https://analytics.example.com/script.js"
  strategy="worker"  // Requires Partytown setup
/>
```

### Partytown (Web Worker for Third-Party Scripts)

```typescript
// next.config.ts
const nextConfig = {
  experimental: {
    nextScriptWorkers: true,
  },
};

// Install Partytown
// npm install @builder.io/partytown

// Scripts with strategy="worker" run in a Web Worker
// Zero main-thread impact for analytics, ads, etc.
```

### Third-Party Script Audit

| Question | Red Flag | Action |
|----------|----------|--------|
| Does it block rendering? | Synchronous `<script>` in `<head>` | Move to `afterInteractive` or `lazyOnload` |
| How large is it? | > 50KB | Evaluate alternatives or defer loading |
| Does it load more scripts? | Chain-loads multiple resources | Consider removing or using Partytown |
| Is it on the critical path? | Blocks LCP or INP | Defer or load in Web Worker |
| Can it be self-hosted? | External CDN with variable latency | Self-host and cache |

---

## Measurement and Tooling

### Lighthouse

```bash
# CLI Lighthouse audit
npx lighthouse https://example.com \
  --output=json \
  --output-path=lighthouse-report.json \
  --chrome-flags="--headless"

# Performance budget enforcement
npx lighthouse https://example.com \
  --budget-path=budget.json
```

```json
// budget.json
[
  {
    "resourceSizes": [
      { "resourceType": "script", "budget": 200 },
      { "resourceType": "image", "budget": 300 },
      { "resourceType": "total", "budget": 500 }
    ],
    "resourceCounts": [
      { "resourceType": "third-party", "budget": 5 }
    ]
  }
]
```

### Web Vitals Measurement

```typescript
// app/components/WebVitals.tsx
'use client';

import { useReportWebVitals } from 'next/web-vitals';

export function WebVitals() {
  useReportWebVitals((metric) => {
    // Send to your analytics
    console.log(metric.name, metric.value);

    // Or send to an endpoint
    fetch('/api/vitals', {
      method: 'POST',
      body: JSON.stringify({
        name: metric.name,     // CLS, FCP, INP, LCP, TTFB
        value: metric.value,
        rating: metric.rating, // good, needs-improvement, poor
        id: metric.id,
      }),
    });
  });

  return null;
}
```

### Performance Testing in CI

```yaml
# .github/workflows/performance.yml
name: Performance

on: [pull_request]

jobs:
  lighthouse:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
      - run: npm ci && npm run build
      - name: Lighthouse CI
        uses: treosh/lighthouse-ci-action@v12
        with:
          urls: |
            http://localhost:3000/
            http://localhost:3000/products
          budgetPath: ./budget.json
          uploadArtifacts: true
```

---

## Anti-Patterns

### 1. Premature Optimization

**Problem**: Optimizing before measuring. Adding memoization everywhere "just in case."

**Fix**: Measure first with Lighthouse, React DevTools Profiler, and Web Vitals. Optimize the measured bottleneck.

### 2. Over-Bundling

**Problem**: Importing large libraries at the top level when only used on one page.

**Fix**: Dynamic imports for route-specific or interaction-triggered libraries.

### 3. Ignoring TTFB

**Problem**: Focusing on client-side optimization while server response takes 2 seconds.

**Fix**: Optimize server response (caching, CDN, database queries) before client optimizations.

### 4. Layout Thrashing

**Problem**: Reading then writing DOM properties in a loop, forcing synchronous reflows.

**Fix**: Batch reads and writes. Use `requestAnimationFrame` for DOM mutations.

### 5. Unoptimized Images

**Problem**: Serving 5MB PNG images to mobile users.

**Fix**: Use `next/image` with proper `sizes`, AVIF/WebP format, and responsive breakpoints.

---

## Cross-References

- [state-management-patterns.md](state-management-patterns.md) -- Render optimization via selective subscriptions
- [testing-frontend-patterns.md](testing-frontend-patterns.md) -- Performance testing strategies
- [fullstack-patterns.md](fullstack-patterns.md) -- Server Component data fetching patterns
- [../../software-clean-code-standard/assets/checklists/frontend-performance-a11y-checklist.md](../../software-clean-code-standard/assets/checklists/frontend-performance-a11y-checklist.md) -- Release gate checklist
