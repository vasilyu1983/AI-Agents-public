# Web Vitals and Performance Budgets

## Table of Contents

- [Core Web Vitals Thresholds](#core-web-vitals-thresholds)
- [Performance Budget Templates](#performance-budget-templates)
- [k6 Load Testing Patterns](#k6-load-testing-patterns)
- [Lighthouse Usage Patterns](#lighthouse-usage-patterns)
- [autocannon Usage Patterns](#autocannon-usage-patterns)
- [Regression CI Gate Examples](#regression-ci-gate-examples)
- [Anti-Patterns and Failure Modes](#anti-patterns-and-failure-modes)

---

## Core Web Vitals Thresholds

Core Web Vitals are Google's field quality signals for user experience, used in search ranking and Lighthouse scoring. The three active metrics are LCP, INP, and CLS. FID was retired in March 2024 and replaced by INP.

### Current Thresholds

| Metric | Good | Needs Improvement | Poor | Source |
|--------|------|--------------------|------|--------|
| **LCP** (Largest Contentful Paint) | ≤ 2.5s | 2.5s – 4s | > 4s | Google Search Central |
| **INP** (Interaction to Next Paint) | ≤ 200ms | 200ms – 500ms | > 500ms | Google Search Central |
| **CLS** (Cumulative Layout Shift) | ≤ 0.1 | 0.1 – 0.25 | > 0.25 | Google Search Central |

These thresholds apply at the 75th percentile of page loads in field data (Chrome UX Report / CrUX). A page passes if 75% of real visits meet the "good" threshold. These headline thresholds are confirmed unchanged as of mid-2026; a 2026 methodology update tightened how INP is aggregated within a session (more weight on sustained/repeated slow interactions rather than a flat average) and expanded CrUX coverage of SPA soft navigations — the 200ms/500ms lines themselves did not move. Re-verify against web.dev/articles/vitals before quoting exact mechanics, since CWV measurement methodology is actively iterated even when thresholds hold steady.

### Metric Definitions

**LCP — Largest Contentful Paint**
Time until the largest image or text block visible in the viewport is fully rendered. Common LCP elements: hero images, above-fold `<img>`, `<video>` poster, large text blocks. Key factors: server response time (TTFB), render-blocking resources, image fetch time, client-side rendering delay.

**INP — Interaction to Next Paint** (replaced FID in March 2024)
Measures the latency of all user interactions (click, tap, key) throughout the page lifetime, not just the first one. The metric reports at the 98th percentile of all interactions in a session. Key factors: long JavaScript tasks blocking the main thread, layout thrash triggered by event handlers, excessive DOM size, unoptimized event delegation.

**CLS — Cumulative Layout Shift**
Sum of all unexpected layout shift scores during the page's lifetime. Each layout shift score is `impact fraction × distance fraction`. Key causes: images and embeds without explicit dimensions, dynamically injected content above existing content, web fonts causing FOIT/FOUT without font-display strategy.

### How INP Replaced FID

| Aspect | FID (retired) | INP (current) |
|--------|---------------|---------------|
| Scope | First input only | All interactions |
| Measurement | Input delay only | Full interaction latency (input + processing + presentation) |
| Threshold (good) | ≤ 100ms | ≤ 200ms |
| Retired | March 12, 2024 | Active |

Teams still citing FID in budgets or reports should update to INP. FID data in CrUX is historical.

### Field vs Lab Measurement

| | Field (RUM) | Lab (Lighthouse/WebPageTest) |
|--|-------------|------------------------------|
| LCP | CrUX, web-vitals.js | Lighthouse, WebPageTest |
| INP | CrUX, web-vitals.js | Lighthouse (TBT as proxy), PerformanceObserver |
| CLS | CrUX, web-vitals.js | Lighthouse, WebPageTest |

Lighthouse does not directly measure INP in lab; it uses Total Blocking Time (TBT ≤ 200ms) as a correlated proxy. Field and lab results frequently diverge. Budget gates on lab scores are necessary but field data from CrUX or RUM is the ground truth for search ranking.

---

## Performance Budget Templates

### Template 1 — Marketing / Content Page (`perf-budget-content.json`)

```json
{
  "page_type": "marketing-content",
  "description": "Public marketing and content pages; primarily SEO-facing",
  "budgets": {
    "lcp_ms": 2500,
    "inp_ms": 200,
    "cls": 0.1,
    "ttfb_ms": 800,
    "fcp_ms": 1800,
    "tbt_ms": 200,
    "js_bytes": 350000,
    "css_bytes": 75000,
    "image_bytes": 600000,
    "total_bytes": 1200000,
    "requests": 50,
    "lighthouse_performance_score": 90
  },
  "measurement": {
    "tool": "lighthouse-ci",
    "profile": "mobile-4g",
    "runs": 3,
    "aggregation": "median"
  }
}
```

### Template 2 — Web Application (`perf-budget-webapp.json`)

```json
{
  "page_type": "web-application",
  "description": "Authenticated app surfaces; user retention and INP are primary concerns",
  "budgets": {
    "lcp_ms": 2500,
    "inp_ms": 200,
    "cls": 0.1,
    "ttfb_ms": 600,
    "fcp_ms": 1500,
    "tbt_ms": 150,
    "js_bytes": 500000,
    "css_bytes": 100000,
    "image_bytes": 400000,
    "total_bytes": 1500000,
    "requests": 75,
    "lighthouse_performance_score": 85
  },
  "measurement": {
    "tool": "lighthouse-ci",
    "profile": "mobile-4g",
    "runs": 3,
    "aggregation": "median"
  }
}
```

### Template 3 — API Service (`perf-budget-api.json`)

```json
{
  "service": "api",
  "description": "HTTP API service; latency and throughput targets",
  "budgets": {
    "p50_ms": 100,
    "p95_ms": 300,
    "p99_ms": 800,
    "error_rate_pct": 0.5,
    "rps_target": 500,
    "startup_time_ms": 3000
  },
  "load_test": {
    "tool": "k6",
    "vus": 50,
    "duration_s": 60,
    "ramp_up_s": 10
  }
}
```

### Budget File Schema for `check_perf_budget.py`

```json
{
  "lcp_ms": 2500,
  "inp_ms": 200,
  "cls": 0.1,
  "tbt_ms": 200,
  "fcp_ms": 1800,
  "ttfb_ms": 800,
  "js_bytes": 350000,
  "css_bytes": 75000,
  "lighthouse_performance_score": 90
}
```

Values are upper bounds (fail if report value exceeds threshold), except `lighthouse_performance_score` which is a lower bound.

**On the `js_bytes` figures above:** 350-500kB gzipped (as used in the templates) is a lenient ceiling suitable for content-heavy or feature-dense apps; mobile-first teams increasingly target 150-300kB gzipped for the initial route. Treat any specific kB number as provisional and site-dependent — verify current guidance rather than copying these figures unchanged, and always budget per-route after code splitting rather than against total app size.

For the capacity-planning math behind concurrency, throughput, and connection-pool sizing (Little's Law) and the diminishing-returns math for adding workers (Amdahl's Law), see the parent [SKILL.md](../SKILL.md#capacity-and-concurrency-math-littles-law).

---

## k6 Load Testing Patterns

k6 is the default load testing tool for this skill. It uses JavaScript test scripts, supports TypeScript, and produces structured JSON output.

### Smoke Test — Correctness Check

```javascript
import http from 'k6/http';
import { check } from 'k6';

export const options = {
  vus: 2,
  duration: '30s',
  thresholds: {
    http_req_failed: ['rate<0.01'],
    http_req_duration: ['p(95)<500'],
  },
};

export default function () {
  const res = http.get('https://api.example.com/health');
  check(res, { 'status 200': (r) => r.status === 200 });
}
```

### Load Test — Expected Traffic

```javascript
export const options = {
  stages: [
    { duration: '1m', target: 50 },   // ramp up
    { duration: '3m', target: 50 },   // steady state
    { duration: '1m', target: 0 },    // ramp down
  ],
  thresholds: {
    http_req_duration: ['p(95)<300', 'p(99)<800'],
    http_req_failed: ['rate<0.005'],
  },
};
```

### Stress Test — Breaking Point

```javascript
export const options = {
  stages: [
    { duration: '2m', target: 100 },
    { duration: '5m', target: 100 },
    { duration: '2m', target: 200 },
    { duration: '5m', target: 200 },
    { duration: '2m', target: 300 },
    { duration: '5m', target: 300 },
    { duration: '2m', target: 0 },
  ],
  thresholds: {
    http_req_failed: ['rate<0.05'],
  },
};
```

**Rule:** define thresholds before running the test. A stress test with no thresholds produces data but not a pass/fail outcome usable in CI.

### Soak Test — Long-Duration Degradation

```javascript
export const options = {
  stages: [
    { duration: '5m', target: 50 },
    { duration: '4h', target: 50 },   // sustain
    { duration: '5m', target: 0 },
  ],
  thresholds: {
    http_req_duration: ['p(99)<1000'],
    http_req_failed: ['rate<0.01'],
  },
};
```

Soak tests reveal: memory leaks, connection pool exhaustion, log file rotation issues, and caching invalidation storms.

### Running k6 with JSON Output

```bash
k6 run --out json=results.json load-test.js
```

Use `k6 cloud` for distributed tests or when the load generator itself becomes a bottleneck (typically above 1000 VUs on a single machine).

---

## Lighthouse Usage Patterns

### CLI Usage

```bash
# Single run
lighthouse https://example.com --output json --output html --output-path ./lighthouse-report

# Headless CI run (mobile preset)
lighthouse https://example.com \
  --preset mobile \
  --chrome-flags="--headless --no-sandbox" \
  --output json \
  --output-path ./lh-mobile.json \
  --quiet
```

### lighthouse-ci (LHCI)

LHCI is the CI integration layer for Lighthouse. It collects multiple runs, computes statistics, and can assert against budget thresholds.

```yaml
# .lighthouserc.json
{
  "ci": {
    "collect": {
      "url": ["https://example.com/", "https://example.com/checkout"],
      "numberOfRuns": 3,
      "settings": {
        "preset": "desktop"
      }
    },
    "assert": {
      "preset": "lighthouse:no-pwa",
      "assertions": {
        "largest-contentful-paint": ["error", {"maxNumericValue": 2500}],
        "total-blocking-time": ["error", {"maxNumericValue": 200}],
        "cumulative-layout-shift": ["error", {"maxNumericValue": 0.1}],
        "categories:performance": ["warn", {"minScore": 0.9}]
      }
    },
    "upload": {
      "target": "temporary-public-storage"
    }
  }
}
```

### GitHub Actions Example

```yaml
- name: Run Lighthouse CI
  uses: treosh/lighthouse-ci-action@v12
  with:
    urls: |
      https://staging.example.com/
    configPath: .lighthouserc.json
    uploadArtifacts: true
    temporaryPublicStorage: true
```

**Caveat:** Lighthouse lab scores vary with machine load, network simulation accuracy, and Chrome version. Run at least 3 times and use the median. Do not gate on a single run.

---

## autocannon Usage Patterns

autocannon is a Node.js HTTP/1.1 benchmarking tool. Use it for quick server-level throughput checks where k6 overhead is unwanted.

### CLI Usage

```bash
# 10 connections, 10s duration
npx autocannon -c 10 -d 10 http://localhost:3000/api/endpoint

# With custom headers and body
npx autocannon \
  -c 20 -d 30 \
  -m POST \
  -H "content-type=application/json" \
  -b '{"query":"test"}' \
  http://localhost:3000/api/search

# JSON output for CI parsing
npx autocannon -c 10 -d 10 --json http://localhost:3000/ > bench.json
```

### Programmatic Usage (Node.js)

```javascript
import autocannon from 'autocannon';

const result = await autocannon({
  url: 'http://localhost:3000/api',
  connections: 20,
  duration: 30,
  pipelining: 1,
});

if (result.requests.p99 > 800) {
  console.error(`p99 ${result.requests.p99}ms exceeds 800ms budget`);
  process.exit(1);
}
```

**When to use autocannon vs k6:** autocannon is faster to set up for Node.js servers and needs no binary install. Use k6 when you need scripted scenarios, multi-step flows, staged load profiles, or structured threshold reporting.

---

## Regression CI Gate Examples

### Gate 1 — Lighthouse Score Regression (GitHub Actions)

```yaml
name: Performance Gate
on: [pull_request]

jobs:
  perf:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Build and serve
        run: npm run build && npx serve dist &

      - name: Lighthouse CI
        uses: treosh/lighthouse-ci-action@v12
        with:
          urls: http://localhost:3000
          budgetPath: ./perf-budget-content.json
          temporaryPublicStorage: true
```

### Gate 2 — Bundle Size Regression

```yaml
- name: Check bundle size
  run: |
    npm run build
    node scripts/check_perf_budget.py --report dist/stats.json --budget perf-budget-webapp.json
```

Or using `bundlesize` package:

```json
// package.json
{
  "bundlesize": [
    { "path": "./dist/static/js/main.*.js", "maxSize": "350 kB" },
    { "path": "./dist/static/css/main.*.css", "maxSize": "75 kB" }
  ]
}
```

### Gate 3 — k6 API Regression in CI

```yaml
- name: Start service
  run: docker compose up -d api && sleep 5

- name: k6 smoke test
  run: k6 run --out json=k6-results.json tests/smoke.js

- name: Check thresholds
  run: |
    python3 -c "
    import json, sys
    data = json.load(open('k6-results.json'))
    # k6 exits non-zero on threshold failure; this is a secondary check
    metrics = {m['metric']: m for m in data if 'metric' in m}
    print('k6 run complete')
    "
```

**Note:** k6 exits with code 99 when thresholds are breached. The `run` step will fail the CI job automatically if thresholds are configured in the test script. No extra parsing needed for pass/fail; JSON output is for artifact storage and dashboards.

### Gate 4 — Statistical Regression Check

Single benchmark runs produce noise. Use a minimum of 5 runs and compare distributions:

```bash
# Hyperfine for CLI tool benchmarks
hyperfine --warmup 3 --runs 10 --export-json before.json 'my-tool input.txt'
# After change:
hyperfine --warmup 3 --runs 10 --export-json after.json 'my-tool input.txt'

# Python comparison
python3 -c "
import json
before = json.load(open('before.json'))['results'][0]
after = json.load(open('after.json'))['results'][0]
delta_pct = (after['mean'] - before['mean']) / before['mean'] * 100
print(f'Delta: {delta_pct:.1f}%')
if delta_pct > 10:
    print('REGRESSION: mean time increased >10%')
    exit(1)
"
```

---

## Anti-Patterns and Failure Modes

| Anti-pattern | Why it fails |
|-------------|--------------|
| Gating on Lighthouse score alone | Score is a composite that can hide individual metric regressions; gate on individual metric thresholds instead |
| Running one benchmark pass | Single-pass results include warmup noise, GC pauses, and environmental variance; use median of at least 3 runs |
| Load-testing a non-production-like environment | Results are not predictive; database pool sizes, memory limits, and downstream stub latency must match production |
| Celebrating average latency improvements | p95 and p99 tails often worsen under optimization of the mean; always report both |
| Adding caches before measuring query behavior | Cache invalidation bugs and memory pressure may worsen the system; profile and fix the query first |
| Using TBT as a direct proxy for INP in field data | TBT correlates with INP in lab but field INP depends on actual user interaction patterns and device capabilities |
| Setting LCP budgets without distinguishing page types | LCP on a data-dense dashboard legitimately differs from a marketing page; use per-page-type budgets |
| Ignoring TTFB when debugging LCP | LCP cannot be under 2.5s if TTFB is 1.5s; fix TTFB first before client-side LCP optimizations |
