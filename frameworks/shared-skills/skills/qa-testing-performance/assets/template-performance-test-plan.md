# Performance Test Plan: [Project/Service Name]

**Author:** [Name]
**Date:** [YYYY-MM-DD]
**Version:** 1.0
**Status:** Draft | In Review | Approved

## 1. Objective

[What this performance test is intended to prove or measure. Be specific.]

Example: Validate that the Orders API can sustain 500 rps at p95 < 200ms and < 0.1% error rate under expected peak traffic, and identify the capacity ceiling.

## 2. Scope

### In Scope

- [ ] [Service/endpoint/journey 1]
- [ ] [Service/endpoint/journey 2]
- [ ] [Service/endpoint/journey 3]

### Out of Scope

- [ ] [What is explicitly excluded and why]

## 3. Success Criteria

| Metric | Target | Measurement |
|--------|--------|-------------|
| p50 latency | < [X]ms | k6 / APM |
| p95 latency | < [X]ms | k6 / APM |
| p99 latency | < [X]ms | k6 / APM |
| Throughput | >= [X] rps | k6 |
| Error rate | < [X]% | k6 / APM |
| CPU utilization | < [X]% at target load | Infrastructure monitoring |
| Memory utilization | < [X]% at target load | Infrastructure monitoring |
| Zero memory growth trend | Stable over [X] hour soak | Heap snapshots |

## 4. Test Scenarios

### Scenario 1: [Name — e.g., Standard Load]

- **Type:** Load / Stress / Soak / Spike / Capacity
- **VU profile:** Ramp from [X] to [Y] over [Z] minutes, hold for [A] minutes
- **Think time:** [X-Y] seconds between actions
- **Data:** [Parameterization approach — CSV, generated, API seeded]
- **Duration:** [Total duration]

### Scenario 2: [Name]

- **Type:** [Type]
- **VU profile:** [Profile]
- **Think time:** [Think time]
- **Data:** [Data approach]
- **Duration:** [Duration]

### Scenario 3: [Name]

- **Type:** [Type]
- **VU profile:** [Profile]
- **Think time:** [Think time]
- **Data:** [Data approach]
- **Duration:** [Duration]

## 5. User Journeys and Traffic Mix

| Journey | Weight | Steps |
|---------|--------|-------|
| [Journey 1] | [X]% | [Step 1 → Step 2 → Step 3] |
| [Journey 2] | [X]% | [Step 1 → Step 2] |
| [Journey 3] | [X]% | [Step 1 → Step 2 → Step 3 → Step 4] |

## 6. Test Environment

| Component | Configuration |
|-----------|---------------|
| Application | [Version, instance count, instance size] |
| Database | [Type, size, configuration] |
| Cache | [Type, size] |
| Load balancer | [Type, configuration] |
| CDN | [Enabled/Disabled] |
| Region | [Region/zone] |
| Environment parity | [How close to production] |

**Differences from production:** [List any known differences that could affect results]

## 7. Test Data

- **Volume:** [Number of records per table/collection]
- **Source:** [Production snapshot / generated / seeded via API]
- **Parameterization:** [How test data is varied across VUs]
- **Cleanup:** [How test data is cleaned up after tests]

## 8. Monitoring and Observability

| Signal | Tool | Dashboard Link |
|--------|------|----------------|
| Application metrics | [APM tool] | [Link] |
| Infrastructure metrics | [Monitoring tool] | [Link] |
| Database metrics | [Tool] | [Link] |
| Load test results | [k6 / Locust / Artillery] | [Link] |
| Traces | [Tracing tool] | [Link] |
| Logs | [Log aggregator] | [Link] |

## 9. Schedule

| Activity | Date | Owner |
|----------|------|-------|
| Test plan review | [Date] | [Name] |
| Environment preparation | [Date] | [Name] |
| Test data setup | [Date] | [Name] |
| Smoke run | [Date] | [Name] |
| Full test execution | [Date] | [Name] |
| Results analysis | [Date] | [Name] |
| Report and recommendations | [Date] | [Name] |

## 10. Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Environment not representative | Misleading results | [Mitigation] |
| Test data insufficient | Unrealistic cache hit rates | [Mitigation] |
| Shared environment interference | Noisy neighbor effects | [Mitigation] |
| Load generator bottleneck | Understated server capacity | [Mitigation] |

## 11. Stakeholder Sign-Off

| Role | Name | Approval |
|------|------|----------|
| Engineering Lead | [Name] | [ ] |
| SRE / Platform | [Name] | [ ] |
| Product Owner | [Name] | [ ] |

## 12. Results Summary

_Fill in after test execution._

| Metric | Target | Actual | Pass/Fail |
|--------|--------|--------|-----------|
| p95 latency | | | |
| Throughput | | | |
| Error rate | | | |

**Bottleneck identified:** [Description]
**Recommendations:** [Next steps]
**Artifacts:** [Links to results, flamegraphs, dashboards]
