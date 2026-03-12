```markdown
# Load & Performance Testing Template (DevOps)

*Purpose: A template for designing, running, and analyzing load, stress, and performance tests for applications and infrastructure.*

---

# 1. Overview

**Service / Endpoint:**  
[name or URL]

**Environment:**  
- [ ] perf  
- [ ] staging  
- [ ] prod-like  

**Test Type:**  
- [ ] Load test  
- [ ] Stress test  
- [ ] Soak test  
- [ ] Spike test  

**Tooling:**  
- [ ] k6  
- [ ] JMeter  
- [ ] Locust  
- [ ] Gatling  
- [ ] Custom  

---

# 2. Test Objectives

- [ ] Validate SLOs under expected load  
- [ ] Identify bottlenecks  
- [ ] Validate autoscaling behavior  
- [ ] Validate DB/queue limits  
- [ ] Test caching efficacy  

**Success Criteria:**  
[Explicit metrics & thresholds]

---

# 3. Workload Model

## 3.1 Traffic Profile

- RPS: [e.g., 500 RPS average, 1000 RPS peak]  
- Concurrency: [users or VUs]  
- Test duration: [e.g., 30m / 2h / 24h]  
- Ramp-up/down strategy:  

---

## 3.2 Scenario Definitions

Describe each user flow:

| Scenario | Description | Weight | Notes |
|----------|-------------|--------|-------|
| Browse | GET /catalog | 60% | |
| View Item | GET /item/{id} | 30% | |
| Checkout | POST /checkout | 10% | |

---

# 4. Test Configuration

### Example (k6)

```js
import http from 'k6/http';
import { sleep } from 'k6';

export let options = {
  stages: [
    { duration: '5m', target: 100 },
    { duration: '10m', target: 500 },
    { duration: '5m', target: 0 }
  ],
  thresholds: {
    http_req_duration: ['p(95)<400'],
    http_req_failed: ['rate<0.01']
  }
};

export default function () {
  http.get('https://staging.example.com/catalog');
  sleep(1);
}
```

Checklist:

- [ ] Throttling / simulated think time included  
- [ ] Target env isolated (not shared with other tests)  
- [ ] Test data strategy defined  

---

# 5. Observability During Test

Monitor:

- Latency (p50/p95/p99)  
- Error rate  
- CPU & memory  
- DB connections and queries  
- Cache hit ratio  
- Queue length  
- Autoscaling events  

Checklist:

- [ ] Dedicated dashboards per test  
- [ ] Logs sampled and analyzed  
- [ ] Traces captured for slow outliers  

---

# 6. Execution Plan

Steps:

1. Announce test window  
2. Ensure monitoring and alerts ready  
3. Warm up environment  
4. Start test at low load  
5. Increase load gradually  
6. Observe autoscaling and resource usage  
7. Stop test and cool down  
8. Save logs and metrics  

---

# 7. Results & Analysis

## 7.1 Key Metrics

| Metric | Target | Observed |
|--------|--------|----------|
| p95 latency | < 400ms | |
| Error rate | < 1% | |
| Max RPS | | |
| CPU usage | | |
| DB CPU | | |
| Cache hit ratio | | |

---

## 7.2 Findings

- Bottlenecks:  
- Saturation points:  
- Autoscaling behavior:  
- Resource over/under-provisioning:  

---

## 7.3 Recommendations

- Increase CPU/memory for X  
- Add DB index on Y  
- Tweak autoscaling policies  
- Add cache for expensive queries  
- Optimize code paths  

---

# 8. Regression Strategy

- [ ] CI nightly load tests at smaller scale  
- [ ] Pre-release load test for major versions  
- [ ] Baseline comparison across versions  

---

# 9. Completed Example

**Service:** Checkout API  
**Test:** Load test, 15m ramp, 45m steady  
**Peak:** 800RPS  
**Results:**  

- p95 latency ~350ms (OK)  
- p99 latency ~600ms (marginal)  
- DB CPU 80% (acceptable)  

**Actions:**  

- Optimize DB queries  
- Add caching layer  

---

# END

```
