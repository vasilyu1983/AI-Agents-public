# Performance Budgets and Core Web Vitals

## Table of Contents

- [Core Web Vitals Thresholds](#core-web-vitals-thresholds)
- [Lighthouse CI Budget JSON](#lighthouse-ci-budget-json)
- [k6 Load Patterns](#k6-load-patterns)
- [Native Profiling Tools](#native-profiling-tools)
- [Production Traps](#production-traps)
- [Neutral Is a Revert](#neutral-is-a-revert)

---

## Core Web Vitals Thresholds

Google's ranking signals (source: web.dev/vitals; verify current thresholds):

| Metric | Good | Needs Improvement | Poor | Measures |
|--------|------|-------------------|------|---------|
| LCP (Largest Contentful Paint) | ≤ 2.5 s | 2.5–4.0 s | > 4.0 s | Loading speed of main content |
| INP (Interaction to Next Paint) | ≤ 200 ms | 200–500 ms | > 500 ms | Responsiveness (replaced FID in March 2024) |
| CLS (Cumulative Layout Shift) | ≤ 0.1 | 0.1–0.25 | > 0.25 | Visual stability |

These three headline thresholds are confirmed unchanged as of mid-2026. A 2026 CWV update tightened how INP is *measured* rather than the threshold itself: field-data weighting now leans more toward sustained/repeated slow interactions in a session rather than treating all interactions as equally averaged, CrUX expanded soft-navigation (SPA route-change) coverage, and TTFB became a more prominent diagnostic surface in PageSpeed Insights. Practical effect: a borderline-good page can slip to "needs improvement" from the methodology change alone, with no code change on your side — don't treat that shift as a regression to chase blindly. Re-verify against web.dev/articles/vitals before quoting exact mechanics, since CWV methodology is actively iterated.

**INP replaces FID:** FID was retired from CWV in March 2024. Any budget or tooling referencing FID as a CWV signal is outdated.

**TTFB and FCP** are diagnostic metrics, not ranking signals, but remain useful budget indicators:

| Metric | Good |
|--------|------|
| TTFB | ≤ 800 ms |
| FCP | ≤ 1.8 s |

---

## Lighthouse CI Budget JSON

Place `lighthouserc.json` at repo root. CI exits non-zero when any budget is breached.

```json
{
  "ci": {
    "collect": {
      "url": ["https://staging.example.com/"],
      "numberOfRuns": 3
    },
    "assert": {
      "budgets": [
        {
          "path": "/*",
          "timings": [
            { "metric": "largest-contentful-paint",  "budget": 2500 },
            { "metric": "interaction-to-next-paint",  "budget": 200  },
            { "metric": "cumulative-layout-shift",    "budget": 0.1  },
            { "metric": "first-contentful-paint",     "budget": 1800 },
            { "metric": "time-to-first-byte",         "budget": 800  },
            { "metric": "total-blocking-time",        "budget": 200  }
          ],
          "resourceSizes": [
            { "resourceType": "script",  "budget": 300 },
            { "resourceType": "image",   "budget": 500 },
            { "resourceType": "total",   "budget": 1500 }
          ],
          "resourceCounts": [
            { "resourceType": "third-party", "budget": 10 }
          ]
        }
      ],
      "assertions": {
        "categories:performance": ["warn", { "minScore": 0.85 }]
      }
    },
    "upload": {
      "target": "temporary-public-storage"
    }
  }
}
```

Run in CI: `npx lhci autorun`

---

## k6 Load Patterns

### Smoke test (baseline)

```js
// smoke.js — verify p95 < 500 ms at low load
import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  vus: 5,
  duration: '30s',
  thresholds: {
    http_req_duration: ['p(95)<500'],
    http_req_failed:   ['rate<0.01'],
  },
};

export default function () {
  const res = http.get('https://api.example.com/health');
  check(res, { 'status 200': (r) => r.status === 200 });
  sleep(1);
}
```

### Ramp-up / stress test

```js
export const options = {
  stages: [
    { duration: '2m', target: 50  },   // ramp up
    { duration: '5m', target: 50  },   // hold
    { duration: '2m', target: 200 },   // stress
    { duration: '5m', target: 200 },   // hold at stress
    { duration: '2m', target: 0   },   // ramp down
  ],
  thresholds: {
    http_req_duration: ['p(99)<2000'],
    http_req_failed:   ['rate<0.05'],
  },
};
```

### Soak test skeleton

```js
export const options = {
  stages: [
    { duration: '5m',  target: 100 },
    { duration: '60m', target: 100 },  // hold; watch memory leak signals
    { duration: '5m',  target: 0   },
  ],
};
```

k6 docs: https://grafana.com/docs/k6/ (verify current version)

---

## Native Profiling Tools

| Ecosystem | Tool | Primary Use |
|-----------|------|-------------|
| Go | `pprof` | CPU, heap, goroutine, mutex profiles via `net/http/pprof` |
| .NET | `dotnet-counters` | Live runtime counters; `dotnet-trace` for flamegraphs |
| JVM | async-profiler | CPU/allocation flamegraphs without safepoint bias; v4.x adds native pthread mutex/rwlock contention detection (`--nativelock`) — use it before assuming a JVM pause is GC |
| Node.js | `--prof` + `node --prof-process` | V8 tick-based CPU profile |
| Python | `py-spy` (sampling) or `cProfile` | Production-safe CPU profiling |
| iOS/macOS | Instruments (Time Profiler, Allocations) | Xcode-integrated; use Xctrace for CLI |
| Rust | `cargo flamegraph` (via perf/dtrace) | Zero-overhead sampling |

### pprof quick start (Go)

```go
import _ "net/http/pprof"
// Exposes /debug/pprof/ on your HTTP server
```

```bash
go tool pprof -http=:6060 http://localhost:8080/debug/pprof/profile?seconds=30
```

### dotnet-counters quick start

```bash
dotnet-counters monitor --process-id <PID> \
  System.Runtime Microsoft.AspNetCore.Hosting
```

---

## Production Traps

- **INP ≠ FID in monitoring dashboards:** CrUX data from before March 2024 uses FID; post-March 2024 field data uses INP. Mixing the two in trend charts gives false readings.
- **LCP image fetchpriority:** Chrome respects `fetchpriority="high"` on `<img>` (and preload links) for the LCP candidate; images default to low priority until layout, which is exactly when a hero image needs to already be fetching. Real-world reports of adding this one attribute to an above-the-fold hero image commonly show LCP drops in the several-hundred-ms to ~1s range — the exact number is site- and connection-dependent, so measure before/after rather than quoting a fixed delta. Only mark one element per page `fetchpriority="high"`; marking several defeats the hint.
- **CLS from font-swap:** `font-display: optional` eliminates layout shift at the cost of invisible text on slow connections. Prefer `font-display: swap` with explicit `size-adjust`.
- **k6 is now on a formal stability track:** k6 reached v1.0 in 2025 and follows semantic versioning with documented stability guarantees — breaking changes to the stable/documented API are now reserved for major-version bumps, not silent minor-release changes. Experimental APIs (anything not explicitly covered in k6's versioning-and-stability-guarantees doc) can still change across minor versions, so pin a major version in CI and read the release notes before upgrading, especially for `http.batch()` usage that relies on array-vs-object return shape.
- **CLI flag drift across profiler/CI tool versions:** Flags on fast-moving CLIs (`lhci`, `dotnet-counters`, `dotnet-trace`, etc.) do change names between releases. Do not hardcode a remembered flag name into a long-lived CI script without pinning the tool version; run `--help` against the pinned version when writing the script. As of this writing, `lhci`'s current documented flag for pointing at a config file is `--config` (not `--config-path`) — verify against the tool's own `--help` output before shipping, since this is exactly the kind of detail that silently drifts.

---

## Neutral Is a Revert

> Source: [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills), `skills/performance-optimization/SKILL.md`, commit `7676817`, MIT License. Extracted 2026-08-09.

A benchmark-variance rule for judging "did this change actually help," referenced from [SKILL.md's "When NOT to Optimize"](../SKILL.md#when-not-to-optimize).

- Re-measure a performance change under the same conditions as the baseline: same environment, same load shape, same tool, same number of runs.
- Compare the result to the baseline's measured noise band (run-to-run variance), not to a single baseline number.
- If the result falls inside the noise band, the change is reverted. It is not kept as "harmless" or "probably fine" — a result that cannot be distinguished from noise has not been proven to help, and shipped complexity without a proven win is a net cost.
- "Neutral" and "no regression" are not the same as "improvement." Only a delta that clears the noise band counts as a win worth keeping.

### Idea Ledger

Log every attempted optimization — including reverted ones — in a table with this shape:

| Idea | Baseline → Result | Verdict | Why |
|------|--------------------|---------|-----|
| Add Redis cache in front of `/orders` read path | p95 142ms → 138ms (noise band ±8ms) | Reverted | Delta inside measurement noise; added cache-invalidation complexity for no proven gain |
| Batch N+1 queries in `OrderService.list()` | p95 142ms → 61ms (noise band ±8ms) | Kept | Delta clears noise band by >9x; re-measured 3x to confirm |

- Log the entry at the same time as the revert, not after the fact from memory — a reverted attempt with no record is indistinguishable from an attempt nobody thought of yet.
- Before starting a new optimization, check the ledger for the same idea. A previously reverted attempt is not automatically wrong to retry (baseline conditions can change), but retrying it silently — without checking whether the earlier revert's "why" still applies — re-burns the same investigation.
- The ledger's job is narrow: stop re-litigating a dead optimization, not replace the CHANGES MADE / POTENTIAL CONCERNS reporting this repo already uses after a change.
