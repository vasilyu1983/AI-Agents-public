# Quality Metrics and Dashboards

Quality metrics collection, reporting, trend analysis, and team dashboards -- from core quality indicators through executive reporting and anti-pattern avoidance.

## Contents

- Core Quality Metrics
- Test Suite Health Metrics
- Metric Collection Pipelines
- Dashboard Tools and Setup
- Dashboard Views by Audience
- Trend Analysis and Forecasting
- Quality Gates as Metrics
- Release Readiness Scoring
- Metric Anti-Patterns
- Alerting on Quality Regressions
- Implementation Checklist
- Related Resources

---

## Core Quality Metrics

### Primary Quality Indicators

| Metric | Formula | Target | Collection Source |
|--------|---------|--------|-------------------|
| **Defect Escape Rate** | Prod bugs / total bugs found | <10% | Defect tracker (Jira, Linear) |
| **Mean Time to Detect (MTTD)** | Avg time from defect introduction to detection | <24 hours | Git blame + bug report timestamps |
| **Test Pass Rate** | Passing tests / total tests | >98% | CI test reporters |
| **Flake Rate** | Flaky runs / total runs | <3% | CI analytics |
| **Code Coverage (delta)** | Coverage change on PR | +/- 0% (no decrease) | Coverage tools (Istanbul, JaCoCo) |
| **Coverage Trend** | Coverage over time | Increasing or stable | Coverage history |

### Defect Escape Rate Calculation

```python
def defect_escape_rate(
    bugs_in_prod: int,
    bugs_in_staging: int,
    bugs_in_dev: int,
    bugs_in_code_review: int
) -> dict:
    """Calculate defect escape rate and detection distribution."""
    total = bugs_in_prod + bugs_in_staging + bugs_in_dev + bugs_in_code_review
    if total == 0:
        return {"escape_rate": 0, "distribution": {}}

    return {
        "escape_rate": f"{(bugs_in_prod / total) * 100:.1f}%",
        "distribution": {
            "code_review": f"{(bugs_in_code_review / total) * 100:.1f}%",
            "development": f"{(bugs_in_dev / total) * 100:.1f}%",
            "staging": f"{(bugs_in_staging / total) * 100:.1f}%",
            "production": f"{(bugs_in_prod / total) * 100:.1f}%",
        },
        "total_bugs": total,
        "assessment": "GOOD" if bugs_in_prod / total < 0.10 else "NEEDS_IMPROVEMENT",
    }

# Example
result = defect_escape_rate(
    bugs_in_prod=3,
    bugs_in_staging=12,
    bugs_in_dev=25,
    bugs_in_code_review=10
)
# escape_rate: 6.0%, assessment: GOOD
```

### Mean Time to Detect

```python
from datetime import datetime, timedelta

def calculate_mttd(defects: list[dict]) -> timedelta:
    """Calculate mean time to detect from defect records.

    Each defect has:
      - introduced_at: datetime (commit timestamp)
      - detected_at: datetime (bug report / test failure timestamp)
    """
    detection_times = []
    for defect in defects:
        introduced = datetime.fromisoformat(defect["introduced_at"])
        detected = datetime.fromisoformat(defect["detected_at"])
        detection_times.append(detected - introduced)

    if not detection_times:
        return timedelta(0)

    total_seconds = sum(dt.total_seconds() for dt in detection_times)
    avg_seconds = total_seconds / len(detection_times)
    return timedelta(seconds=avg_seconds)
```

---

## Test Suite Health Metrics

| Metric | Formula | Target | Why It Matters |
|--------|---------|--------|----------------|
| **Suite Execution Time** | Wall-clock time for full suite | <15 min (E2E), <5 min (unit) | Developer feedback speed |
| **Suite Stability** | Runs with 0 flakes / total runs | >95% | Trust in CI signal |
| **Test Count Trend** | Tests added vs removed per sprint | Net positive | Coverage growth |
| **Slowest Tests (P95)** | 95th percentile test duration | <30s (E2E), <1s (unit) | CI pipeline bottlenecks |
| **Quarantined Test Count** | Tests in quarantine | Decreasing trend | Tech debt indicator |
| **Disabled Test Count** | Skipped / disabled tests | <5% of total | Hidden coverage gaps |

### Suite Health Report Script

```typescript
// scripts/suite-health-report.ts
import { execSync } from 'child_process';

interface TestResult {
  name: string;
  duration: number;
  status: 'passed' | 'failed' | 'skipped' | 'flaky';
}

function generateReport(results: TestResult[]) {
  const total = results.length;
  const passed = results.filter(r => r.status === 'passed').length;
  const failed = results.filter(r => r.status === 'failed').length;
  const flaky = results.filter(r => r.status === 'flaky').length;
  const skipped = results.filter(r => r.status === 'skipped').length;

  const durations = results.map(r => r.duration).sort((a, b) => a - b);
  const p50 = durations[Math.floor(durations.length * 0.5)];
  const p95 = durations[Math.floor(durations.length * 0.95)];
  const totalDuration = durations.reduce((sum, d) => sum + d, 0);

  return {
    summary: {
      total,
      passed,
      failed,
      flaky,
      skipped,
      passRate: `${((passed / total) * 100).toFixed(1)}%`,
      flakeRate: `${((flaky / total) * 100).toFixed(1)}%`,
    },
    timing: {
      totalDuration: `${(totalDuration / 1000).toFixed(1)}s`,
      p50: `${(p50 / 1000).toFixed(2)}s`,
      p95: `${(p95 / 1000).toFixed(2)}s`,
    },
    slowest: results
      .sort((a, b) => b.duration - a.duration)
      .slice(0, 10)
      .map(r => ({ name: r.name, duration: `${(r.duration / 1000).toFixed(2)}s` })),
  };
}
```

---

## Metric Collection Pipelines

### Architecture

```text
┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│  CI Pipeline │    │ Test Reporter │    │  Data Store  │    │  Dashboard   │
│  (GitHub/GL) │───>│  (JUnit XML) │───>│ (Postgres /  │───>│  (Grafana /  │
│              │    │  (JSON/CSV)  │    │  InfluxDB)   │    │  Datadog)    │
└──────────────┘    └──────────────┘    └──────────────┘    └──────────────┘
                           │
                    ┌──────┴──────┐
                    │ Bug Tracker │
                    │ (Jira API)  │
                    └─────────────┘
```

### JUnit XML Reporter (CI Standard)

```typescript
// playwright.config.ts
export default defineConfig({
  reporter: [
    ['junit', { outputFile: 'results/junit.xml' }],
    ['json', { outputFile: 'results/results.json' }],
    ['html', { open: 'never' }],
  ],
});
```

### Custom Metrics Collector

```python
#!/usr/bin/env python3
"""Collect test metrics from CI and push to metrics store."""
import json
import xml.etree.ElementTree as ET
from datetime import datetime
import requests

def parse_junit(xml_path: str) -> dict:
    """Parse JUnit XML into metrics."""
    tree = ET.parse(xml_path)
    root = tree.getroot()

    suites = root.findall('.//testsuite')
    total = sum(int(s.get('tests', 0)) for s in suites)
    failures = sum(int(s.get('failures', 0)) for s in suites)
    errors = sum(int(s.get('errors', 0)) for s in suites)
    skipped = sum(int(s.get('skipped', 0)) for s in suites)
    time_s = sum(float(s.get('time', 0)) for s in suites)

    return {
        "timestamp": datetime.utcnow().isoformat(),
        "total_tests": total,
        "passed": total - failures - errors - skipped,
        "failed": failures + errors,
        "skipped": skipped,
        "duration_seconds": round(time_s, 2),
        "pass_rate": round((total - failures - errors - skipped) / total * 100, 1) if total > 0 else 0,
    }

def push_to_datadog(metrics: dict):
    """Push metrics to Datadog."""
    series = []
    for key, value in metrics.items():
        if isinstance(value, (int, float)):
            series.append({
                "metric": f"qa.test_suite.{key}",
                "type": "gauge",
                "points": [[int(datetime.utcnow().timestamp()), value]],
                "tags": ["env:ci", f"branch:{os.getenv('BRANCH', 'main')}"],
            })

    requests.post(
        "https://api.datadoghq.com/api/v1/series",
        headers={"DD-API-KEY": os.getenv("DD_API_KEY")},
        json={"series": series},
    )

if __name__ == "__main__":
    metrics = parse_junit("results/junit.xml")
    push_to_datadog(metrics)
    print(json.dumps(metrics, indent=2))
```

### GitHub Actions: Metrics Collection Step

```yaml
- name: Collect and push test metrics
  if: always()
  env:
    DD_API_KEY: ${{ secrets.DD_API_KEY }}
    BRANCH: ${{ github.ref_name }}
  run: python scripts/collect-metrics.py results/junit.xml
```

---

## Dashboard Tools and Setup

### Grafana + PostgreSQL

```sql
-- Grafana query: test pass rate over time
SELECT
  date_trunc('day', created_at) AS time,
  AVG(pass_rate) AS avg_pass_rate,
  AVG(flake_rate) AS avg_flake_rate,
  AVG(duration_seconds) AS avg_duration
FROM test_runs
WHERE created_at > NOW() - INTERVAL '30 days'
  AND branch = 'main'
GROUP BY 1
ORDER BY 1;
```

### Datadog Dashboard

```python
# Datadog dashboard definition (Terraform)
resource "datadog_dashboard" "quality_metrics" {
  title       = "QA Quality Metrics"
  description = "Test suite health, defect metrics, and release readiness"
  layout_type = "ordered"

  widget {
    timeseries_definition {
      title = "Test Pass Rate"
      request {
        q          = "avg:qa.test_suite.pass_rate{branch:main}"
        display_type = "line"
      }
      yaxis { min = "90", max = "100" }
    }
  }

  widget {
    query_value_definition {
      title = "Current Flake Rate"
      request {
        q          = "avg:qa.test_suite.flake_rate{branch:main}.rollup(avg, 86400)"
        aggregator = "last"
      }
      precision = 1
    }
  }
}
```

### Lightweight: Markdown Report (No Infrastructure)

```python
def generate_markdown_report(metrics_history: list[dict]) -> str:
    """Generate a markdown quality report for PR comments or Slack."""
    latest = metrics_history[-1]
    previous = metrics_history[-2] if len(metrics_history) > 1 else latest

    def trend(current, prev):
        diff = current - prev
        if diff > 0: return f"+{diff:.1f} :arrow_up:"
        if diff < 0: return f"{diff:.1f} :arrow_down:"
        return "0 :left_right_arrow:"

    return f"""## Quality Metrics Report
| Metric | Current | Trend |
|--------|---------|-------|
| Pass Rate | {latest['pass_rate']}% | {trend(latest['pass_rate'], previous['pass_rate'])} |
| Flake Rate | {latest['flake_rate']}% | {trend(latest['flake_rate'], previous['flake_rate'])} |
| Suite Duration | {latest['duration_seconds']}s | {trend(latest['duration_seconds'], previous['duration_seconds'])} |
| Total Tests | {latest['total_tests']} | {trend(latest['total_tests'], previous['total_tests'])} |
| Defect Escape Rate | {latest.get('escape_rate', 'N/A')} | -- |
"""
```

---

## Dashboard Views by Audience

### Executive View

Focus on outcomes and trends, not technical details.

| Metric | Visualization | Update Frequency |
|--------|---------------|------------------|
| Defect Escape Rate (monthly) | Single number + trend line | Weekly |
| Release Cadence | Bar chart (releases/month) | Weekly |
| Deployment Success Rate | Percentage gauge | Daily |
| Mean Time to Recovery (MTTR) | Single number | Weekly |
| Customer-Reported Bugs | Trend line | Weekly |

### Team Lead View

Focus on team health and process effectiveness.

| Metric | Visualization | Update Frequency |
|--------|---------------|------------------|
| Test Pass Rate by suite | Stacked bar chart | Daily |
| Flake Rate trend | Line chart (7-day rolling) | Daily |
| CI Pipeline Duration | Line chart | Daily |
| Quarantined Test Count | Single number + trend | Daily |
| Coverage by module | Heatmap | Weekly |
| PR Review-to-Merge Time | Histogram | Weekly |

### Individual Contributor View

Focus on actionable signals.

| Metric | Visualization | Update Frequency |
|--------|---------------|------------------|
| My recent test failures | List with links | Real-time |
| My flaky tests | Table with flake % | Daily |
| My PR coverage delta | Inline in PR | Per-PR |
| Slowest tests I own | Ranked list | Weekly |

---

## Trend Analysis and Forecasting

### Rolling Averages

```python
import pandas as pd

def calculate_trends(metrics_df: pd.DataFrame) -> pd.DataFrame:
    """Calculate 7-day and 30-day rolling averages."""
    df = metrics_df.sort_values('date')

    df['pass_rate_7d'] = df['pass_rate'].rolling(window=7).mean()
    df['pass_rate_30d'] = df['pass_rate'].rolling(window=30).mean()
    df['flake_rate_7d'] = df['flake_rate'].rolling(window=7).mean()
    df['duration_7d'] = df['duration_seconds'].rolling(window=7).mean()

    return df

def detect_regression(df: pd.DataFrame, metric: str, window: int = 7, threshold: float = 0.1) -> list:
    """Detect metric regressions using rolling window comparison."""
    rolling = df[metric].rolling(window=window)
    mean = rolling.mean()
    std = rolling.std()

    regressions = []
    for i in range(window, len(df)):
        current = df[metric].iloc[i]
        expected_mean = mean.iloc[i - 1]
        expected_std = std.iloc[i - 1]

        if expected_std > 0:
            z_score = (current - expected_mean) / expected_std
            if abs(z_score) > 2:  # 2 sigma = significant change
                regressions.append({
                    "date": df['date'].iloc[i],
                    "metric": metric,
                    "value": current,
                    "expected": round(expected_mean, 2),
                    "z_score": round(z_score, 2),
                })

    return regressions
```

---

## Quality Gates as Metrics

### Gate Definition

```yaml
# quality-gates.yml
gates:
  merge:
    - metric: test_pass_rate
      operator: ">="
      threshold: 100
      description: "All tests must pass"
    - metric: coverage_delta
      operator: ">="
      threshold: 0
      description: "Coverage must not decrease"
    - metric: lint_errors
      operator: "=="
      threshold: 0
      description: "No lint errors"

  deploy_staging:
    - metric: e2e_pass_rate
      operator: ">="
      threshold: 98
      description: "E2E suite pass rate"
    - metric: smoke_tests
      operator: "=="
      threshold: "all_passed"
      description: "Smoke tests pass"

  deploy_production:
    - metric: staging_soak_hours
      operator: ">="
      threshold: 4
      description: "4 hours soak time in staging"
    - metric: performance_regression
      operator: "=="
      threshold: false
      description: "No performance regressions"
    - metric: security_scan
      operator: "=="
      threshold: "clean"
      description: "No critical vulnerabilities"
```

### Gate Evaluation

```python
def evaluate_gates(gate_name: str, metrics: dict, gates_config: dict) -> dict:
    """Evaluate quality gates and return pass/fail with details."""
    gates = gates_config["gates"][gate_name]
    results = []

    for gate in gates:
        actual = metrics.get(gate["metric"])
        threshold = gate["threshold"]
        op = gate["operator"]

        passed = {
            ">=": actual >= threshold,
            "<=": actual <= threshold,
            "==": actual == threshold,
            ">": actual > threshold,
            "<": actual < threshold,
        }.get(op, False) if actual is not None else False

        results.append({
            "metric": gate["metric"],
            "description": gate["description"],
            "threshold": threshold,
            "actual": actual,
            "passed": passed,
        })

    all_passed = all(r["passed"] for r in results)
    return {"gate": gate_name, "passed": all_passed, "results": results}
```

---

## Release Readiness Scoring

### Weighted Readiness Score

```python
def release_readiness_score(metrics: dict) -> dict:
    """Calculate weighted release readiness score (0-100)."""
    weights = {
        "test_pass_rate": 0.25,
        "e2e_pass_rate": 0.20,
        "flake_rate_inverse": 0.10,  # 100 - flake_rate
        "coverage": 0.10,
        "security_clean": 0.15,
        "performance_pass": 0.10,
        "staging_soak": 0.10,
    }

    scores = {
        "test_pass_rate": min(metrics.get("test_pass_rate", 0), 100),
        "e2e_pass_rate": min(metrics.get("e2e_pass_rate", 0), 100),
        "flake_rate_inverse": max(100 - metrics.get("flake_rate", 100), 0),
        "coverage": min(metrics.get("coverage", 0), 100),
        "security_clean": 100 if metrics.get("security_clean", False) else 0,
        "performance_pass": 100 if metrics.get("performance_pass", False) else 0,
        "staging_soak": min(metrics.get("staging_soak_hours", 0) / 4 * 100, 100),
    }

    total = sum(scores[k] * weights[k] for k in weights)

    return {
        "overall_score": round(total, 1),
        "ready": total >= 85,
        "component_scores": {k: round(v, 1) for k, v in scores.items()},
        "recommendation": "SHIP" if total >= 85 else "HOLD" if total >= 70 else "BLOCK",
    }
```

### Readiness Thresholds

| Score | Recommendation | Action |
|-------|---------------|--------|
| 85-100 | SHIP | Clear to deploy |
| 70-84 | HOLD | Review failing components, decide |
| <70 | BLOCK | Do not deploy; fix blocking issues |

---

## Metric Anti-Patterns

| Anti-Pattern | Problem | Better Approach |
|-------------|---------|-----------------|
| **Vanity metrics** (total test count) | More tests does not equal more quality | Track defect escape rate, not test count |
| **Goodhart's Law** (gaming coverage) | Writing tests to hit % target, not to find bugs | Measure mutation score or defect escape rate |
| **Averaging flake rate** | Hides badly flaky individual tests | Track per-test flake rate, fix top offenders |
| **100% coverage mandate** | Diminishing returns past 80-85% | Risk-weighted coverage targets by module |
| **Test count as productivity** | Incentivizes trivial tests | Track bugs found per test, not tests written |
| **Monthly reporting only** | Too slow for actionable feedback | Daily automated dashboards + weekly review |
| **Ignoring test duration** | Slow feedback loops reduce developer velocity | Track and budget suite execution time |

### Goodhart's Law in Practice

```text
BAD: "Our coverage is 95%!"
  → But 30% of tests assert nothing meaningful
  → Mutation testing reveals only 60% mutation kill rate
  → Defects still escape to production

GOOD: "Our mutation kill rate is 78% on critical paths"
  → Tests actually catch real bugs
  → Coverage is a secondary indicator
  → Defect escape rate is primary measure
```

---

## Alerting on Quality Regressions

### Alert Rules

```yaml
# alerting-rules.yml
alerts:
  - name: flake_rate_spike
    metric: qa.test_suite.flake_rate
    condition: "> 5%"
    window: "24h"
    severity: warning
    channel: "#qa-alerts"
    message: "Flake rate exceeded 5% in the last 24 hours"

  - name: test_pass_rate_drop
    metric: qa.test_suite.pass_rate
    condition: "< 95%"
    window: "1h"
    severity: critical
    channel: "#engineering-alerts"
    message: "Test pass rate dropped below 95%"

  - name: suite_duration_increase
    metric: qa.test_suite.duration_seconds
    condition: "> 120% of 7-day average"
    window: "24h"
    severity: warning
    channel: "#qa-alerts"
    message: "Suite duration increased >20% vs 7-day average"

  - name: defect_escape
    metric: qa.defects.production_new
    condition: "> 0"
    window: "24h"
    severity: info
    channel: "#qa-alerts"
    message: "New production defect reported -- review for test gap"
```

### Slack/Teams Integration

```python
def send_quality_alert(alert: dict, webhook_url: str):
    """Send quality regression alert to Slack."""
    color = {"critical": "#FF0000", "warning": "#FFA500", "info": "#0000FF"}
    requests.post(webhook_url, json={
        "attachments": [{
            "color": color.get(alert["severity"], "#808080"),
            "title": f"Quality Alert: {alert['name']}",
            "text": alert["message"],
            "fields": [
                {"title": "Metric", "value": alert["metric"], "short": True},
                {"title": "Current Value", "value": str(alert["current_value"]), "short": True},
                {"title": "Threshold", "value": alert["condition"], "short": True},
                {"title": "Severity", "value": alert["severity"].upper(), "short": True},
            ],
        }],
    })
```

---

## Implementation Checklist

### Phase 1: Foundation (Week 1-2)

- [ ] Configure JUnit/JSON test reporters in CI
- [ ] Store test results in database or metrics service
- [ ] Track: pass rate, flake rate, suite duration
- [ ] Create basic Grafana/Datadog dashboard

### Phase 2: Enrichment (Week 3-4)

- [ ] Add defect tracking integration (Jira/Linear API)
- [ ] Calculate defect escape rate
- [ ] Add coverage trend tracking
- [ ] Set up quality gate automation

### Phase 3: Actionability (Week 5-6)

- [ ] Configure regression alerts (Slack/Teams)
- [ ] Build release readiness scorecard
- [ ] Create audience-specific dashboard views
- [ ] Establish weekly quality review cadence

---

## Related Resources

- [operational-playbook.md](./operational-playbook.md) -- CI/CD pipeline quality gates
- [shift-left-testing.md](./shift-left-testing.md) -- metrics for shift-left effectiveness
- [test-environment-management.md](./test-environment-management.md) -- environment health monitoring
- [SKILL.md](../SKILL.md) -- parent testing strategy skill
- [DORA Metrics](https://dora.dev/guides/dora-metrics-four-keys/)
- [Grafana Dashboards](https://grafana.com/docs/grafana/latest/dashboards/)
- [Datadog APM](https://docs.datadoghq.com/tracing/)
