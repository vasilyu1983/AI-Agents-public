# Performance Budget: [Project/Service Name]

**Owner:** [Team/Person]
**Last Updated:** [YYYY-MM-DD]
**Review Cadence:** [Monthly/Quarterly]

## API Performance Budgets

### Global Defaults

| Metric | Budget | Severity | Notes |
|--------|--------|----------|-------|
| p50 latency | < 100ms | Warn | Typical user experience |
| p95 latency | < 500ms | Fail | Most users' worst case |
| p99 latency | < 1000ms | Fail | Tail latency ceiling |
| Error rate (5xx) | < 0.1% | Fail | Reliability floor |
| Error rate (4xx) | < 5% | Warn | Indicates client-side issues at scale |
| Throughput | >= [X] rps | Fail | Minimum viable capacity |

### Per-Endpoint Overrides

| Endpoint | p95 Budget | Throughput Min | Notes |
|----------|-----------|----------------|-------|
| GET /api/search | < 300ms | >= 200 rps | Search is latency-sensitive |
| POST /api/checkout | < 800ms | >= 50 rps | Higher tolerance, lower volume |
| GET /api/feed | < 200ms | >= 500 rps | High traffic, must be fast |
| POST /api/upload | < 5000ms | >= 10 rps | Large payloads expected |

## Frontend Performance Budgets

### Core Web Vitals

| Metric | Budget | Source |
|--------|--------|--------|
| LCP (Largest Contentful Paint) | < 2.5s | Google "Good" threshold |
| INP (Interaction to Next Paint) | < 200ms | Google "Good" threshold |
| CLS (Cumulative Layout Shift) | < 0.1 | Google "Good" threshold |
| TTFB (Time to First Byte) | < 800ms | Server response budget |
| FCP (First Contentful Paint) | < 1.8s | Lighthouse recommendation |

### Bundle Size

| Asset | Budget (gzipped) | Notes |
|-------|-------------------|-------|
| Main JS bundle | < 50 KB | Entry point only |
| Vendor JS bundle | < 150 KB | Third-party dependencies |
| Total JS (all routes) | < 300 KB | Entire application |
| CSS (total) | < 30 KB | All stylesheets |
| Largest image | < 200 KB | Hero/LCP image |
| Total page weight | < 1 MB | Initial page load |

### Lighthouse Scores

| Category | Minimum Score | Notes |
|----------|---------------|-------|
| Performance | >= 90 | Desktop; >= 75 for mobile |
| Accessibility | >= 90 | All pages |
| Best Practices | >= 90 | All pages |

## Database Performance Budgets

| Metric | Budget | Notes |
|--------|--------|-------|
| Query p95 | < 50ms | Critical path queries |
| Query p99 | < 200ms | All queries |
| Connection pool wait p95 | < 10ms | Pool should not be a bottleneck |
| Connection pool utilization | < 80% | Headroom for spikes |
| Slow query rate (> 1s) | < 0.01% | Flag for optimization |

## Infrastructure Budgets

| Metric | Budget | Notes |
|--------|--------|-------|
| CPU utilization (sustained) | < 70% | Headroom for spikes |
| Memory utilization | < 80% | Headroom for GC and spikes |
| Disk I/O utilization | < 60% | Prevents I/O wait bottlenecks |
| Network throughput | < 70% of capacity | |

## CI Gate Configuration

### PR Gate (Smoke — every PR)

| Check | Tool | Fail Criteria |
|-------|------|---------------|
| Bundle size | size-limit | Any budget exceeded |
| Lighthouse audit | Lighthouse CI | Performance score < 90 or LCP > 2.5s |
| API smoke load | k6 (30s, 10 VUs) | p95 > budget or error rate > 1% |

### Nightly Gate (Full Load)

| Check | Tool | Fail Criteria |
|-------|------|---------------|
| Full load test | k6 (10 min, realistic VUs) | Any threshold breached |
| Soak test | k6 (2 hours) | Memory growth trend detected |
| Baseline comparison | k6 + custom script | p95 regression > 15% from baseline |

### Pre-Release Gate (Capacity)

| Check | Tool | Fail Criteria |
|-------|------|---------------|
| Stress test | k6 (find ceiling) | Ceiling < required capacity * 1.3 |
| Spike test | k6 (burst pattern) | Error rate > 5% during spike |
| Database under load | Query benchmarks | Any query > 2x baseline |

## Budget Review Process

1. Review budgets [monthly/quarterly] against production telemetry.
2. Tighten budgets when the system consistently meets them with margin.
3. Relax budgets only with explicit justification and stakeholder approval.
4. When a budget is breached in production, create an incident ticket and root-cause analysis.
5. When adding new endpoints or pages, define budgets before launch.

## Revision History

| Date | Change | Author |
|------|--------|--------|
| [YYYY-MM-DD] | Initial budget definition | [Name] |
