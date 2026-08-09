# Performance Budgets and CI Integration

Define explicit performance budgets, integrate them into CI pipelines, and detect regressions automatically.

## Table of Contents

- [Defining Performance Budgets](#defining-performance-budgets)
- [API Performance Budgets](#api-performance-budgets)
- [Frontend Performance Budgets](#frontend-performance-budgets)
- [k6 Threshold Integration](#k6-threshold-integration)
- [k6 in CI (GitHub Actions Example)](#k6-in-ci-github-actions-example)
- [.github/workflows/performance.yml](#githubworkflowsperformanceyml)
- [Lighthouse CI Integration](#lighthouse-ci-integration)
- [Configuration](#configuration)
- [Lighthouse CI in GitHub Actions](#lighthouse-ci-in-github-actions)
- [.github/workflows/lighthouse.yml](#githubworkflowslighthouseyml)
- [Bundle Size Tracking](#bundle-size-tracking)
- [size-limit Configuration](#size-limit-configuration)
- [In CI](#in-ci)
- [Baseline Management](#baseline-management)
- [Storing Baselines](#storing-baselines)
- [After a known-good run](#after-a-known-good-run)
- [In CI, compare current run against baseline](#in-ci-compare-current-run-against-baseline)
- [Lighthouse CI server stores historical results and compares automatically](#lighthouse-ci-server-stores-historical-results-and-compares-automatically)
- [Regression Detection](#regression-detection)
- [Handling Flaky Performance Tests](#handling-flaky-performance-tests)
- [Pipeline Tier Design](#pipeline-tier-design)
- [Artifact Collection](#artifact-collection)
- [GitHub Actions — always upload artifacts](#github-actions-—-always-upload-artifacts)
- [Alerting on Degradation](#alerting-on-degradation)

## Defining Performance Budgets

A performance budget is a quantified threshold that blocks a merge or deploy when exceeded. Budgets should be tied to SLOs, not arbitrary numbers.

### API Performance Budgets

| Metric | Budget Example | Rationale |
|--------|---------------|-----------|
| p50 latency | < 100ms | Typical user experience |
| p95 latency | < 500ms | Worst case for most users |
| p99 latency | < 1000ms | Tail latency ceiling |
| Error rate | < 0.1% | Reliability floor |
| Throughput | >= 500 rps | Minimum capacity |

### Frontend Performance Budgets

| Metric | Budget | Source |
|--------|--------|--------|
| LCP | < 2.5s | Core Web Vitals "Good" threshold |
| INP | < 200ms | Core Web Vitals "Good" threshold |
| CLS | < 0.1 | Core Web Vitals "Good" threshold |
| Total bundle size (JS) | < 200KB gzipped | Performance engineering baseline |
| Per-route bundle | < 50KB gzipped | Code splitting target |
| First Byte (TTFB) | < 800ms | Server response budget |

## k6 Threshold Integration

k6 thresholds fail the test (non-zero exit code) when a budget is breached — perfect for CI gates.

```javascript
// k6 — performance budgets as thresholds
export const options = {
  stages: [
    { duration: '30s', target: 20 },
    { duration: '1m', target: 20 },
    { duration: '10s', target: 0 },
  ],
  thresholds: {
    // Global latency budgets
    http_req_duration: [
      'p(50)<100',   // p50 under 100ms
      'p(95)<500',   // p95 under 500ms
      'p(99)<1000',  // p99 under 1s
    ],
    // Error rate budget
    http_req_failed: ['rate<0.001'],  // < 0.1% errors

    // Per-endpoint budgets using tags
    'http_req_duration{name:search}': ['p(95)<300'],
    'http_req_duration{name:checkout}': ['p(95)<800'],

    // Throughput minimum
    http_reqs: ['rate>100'],  // > 100 rps
  },
};
```

### k6 in CI (GitHub Actions Example)

```yaml
# .github/workflows/performance.yml
name: Performance Gate
on:
  pull_request:
    paths: ['src/**', 'api/**']

jobs:
  smoke-load-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: grafana/setup-k6-action@v1
      - uses: grafana/run-k6-action@v1
        with:
          path: tests/performance/smoke.js
          flags: --out json=results.json
      - uses: actions/upload-artifact@v4
        if: always()
        with:
          name: k6-results
          path: results.json
```

## Lighthouse CI Integration

### Configuration

```json
// lighthouserc.json
{
  "ci": {
    "collect": {
      "url": ["http://localhost:3000/", "http://localhost:3000/products"],
      "numberOfRuns": 3,
      "settings": {
        "preset": "desktop"
      }
    },
    "assert": {
      "assertions": {
        "categories:performance": ["error", { "minScore": 0.9 }],
        "first-contentful-paint": ["warn", { "maxNumericValue": 2000 }],
        "largest-contentful-paint": ["error", { "maxNumericValue": 2500 }],
        "interactive": ["error", { "maxNumericValue": 3500 }],
        "cumulative-layout-shift": ["error", { "maxNumericValue": 0.1 }],
        "total-byte-weight": ["warn", { "maxNumericValue": 500000 }]
      }
    },
    "upload": {
      "target": "temporary-public-storage"
    }
  }
}
```

### Lighthouse CI in GitHub Actions

```yaml
# .github/workflows/lighthouse.yml
name: Lighthouse CI
on: pull_request

jobs:
  lighthouse:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 24  # Active LTS as of 2026-07; re-check https://endoflife.date/nodejs before pinning
      - run: npm ci && npm run build
      - run: npm start &
      - name: Wait for server
        run: npx wait-on http://localhost:3000
      - name: Run Lighthouse CI
        run: npx @lhci/cli@latest autorun
```

## Bundle Size Tracking

### size-limit Configuration

```json
// package.json
{
  "size-limit": [
    { "path": "dist/index.js", "limit": "50 KB" },
    { "path": "dist/vendor.js", "limit": "150 KB" },
    { "path": "dist/**/*.css", "limit": "30 KB" }
  ]
}
```

```yaml
# In CI
- run: npx size-limit
```

## Baseline Management

### Storing Baselines

Store baseline results as CI artifacts or in a dedicated baseline branch/file. Compare each run against the baseline, not against absolute numbers alone.

**Approach 1: File-based baseline**
```bash
# After a known-good run
cp results.json baselines/api-performance-baseline.json
# In CI, compare current run against baseline
```

**Approach 2: Lighthouse CI Server**
```bash
# Lighthouse CI server stores historical results and compares automatically
npx @lhci/cli@latest server --storage.storageMethod=sql \
  --storage.sqlDialect=sqlite \
  --storage.sqlDatabasePath=./lhci.db
```

### Regression Detection

A regression is when a metric exceeds the budget OR degrades more than a threshold compared to baseline.

Rules of thumb:
- p95 latency increased > 15% from baseline → warn
- p95 latency increased > 30% from baseline → fail
- Error rate increased > 0.05% absolute → fail
- Bundle size increased > 5KB → warn, > 20KB → fail

### Handling Flaky Performance Tests

Performance tests have inherent variance. Reduce flakiness:
- Run multiple iterations (3-5) and use the median
- Use warm-up periods before measuring
- Pin the test environment (same instance size, same region, no shared resources)
- Use statistical comparison (confidence intervals) rather than single-value thresholds
- Set budgets with headroom — if your SLO is 500ms p95, set the CI budget at 400ms

## Pipeline Tier Design

| Tier | Trigger | Duration | Scenarios | Action on Failure |
|------|---------|----------|-----------|-------------------|
| Smoke | Every PR | 1-2 min | Lightweight: 10 VUs, 30s hold | Block merge |
| Full load | Nightly | 15-30 min | Full scenario suite, realistic VUs | Alert team, ticket |
| Soak | Weekly | 2-4 hours | Sustained moderate load | Alert team, ticket |
| Capacity | Pre-release | 30-60 min | Stress + spike | Block release |

## Artifact Collection

Always collect and store these artifacts regardless of pass/fail:
- Raw results (JSON/CSV)
- Summary report (HTML or Markdown)
- Flamegraphs (if profiling was active)
- Comparison against baseline (delta report)
- Grafana dashboard snapshot (link or export)
- Lighthouse HTML report (for frontend)

```yaml
# GitHub Actions — always upload artifacts
- uses: actions/upload-artifact@v4
  if: always()
  with:
    name: performance-results-${{ github.sha }}
    path: |
      results/
      *.html
    retention-days: 30
```

## Alerting on Degradation

For nightly/weekly runs that are not PR gates, send alerts on degradation:
- Slack/Teams notification with summary and trend chart
- Auto-create a ticket when a budget is breached for 2+ consecutive runs
- Include a diff against the last passing run

Avoid alert fatigue: only alert on confirmed regressions (multiple runs), not single-run variance.
