# perf_budget_checker.py

Stdlib-only Python CLI for performance budget validation and CI test planning. No external dependencies — runs with any Python 3.9+ installation.

## Purpose

Gives performance and QA engineers fast, reproducible answers to three core questions:

1. **Check** — Do the measured results pass performance budgets? Which metrics are failing or in warning? Should CI block this build?
2. **Plan** — Which CI tier (PR gate, nightly, or pre-release) should each test scenario run in?
3. **Report** — A full Markdown performance test report combining budget results and the test execution matrix.

## Quick Start

Run from the `qa-testing-performance/` directory:

```bash
# Budget check — PASS/WARN/FAIL per metric, CI gate verdict
python scripts/perf_budget_checker.py check --input data/sample-perf-results.json

# CI test tier assignment — execution matrix for all scenarios
python scripts/perf_budget_checker.py plan --input data/sample-perf-results.json

# Full Markdown report to stdout
python scripts/perf_budget_checker.py report --input data/sample-perf-results.json

# Full Markdown report written to file
python scripts/perf_budget_checker.py report \
  --input data/sample-perf-results.json \
  --output report.md
```

## Budget Thresholds

### Core Web Vitals

| Metric | PASS | WARN | FAIL |
|--------|------|------|------|
| LCP | < budget (2500ms) | 2500–4000ms | > 4000ms |
| INP | < budget (200ms) | 200–500ms | > 500ms |
| CLS | < budget (0.1) | 0.1–0.25 | > 0.25 |

### API and Load Metrics

| Metric | PASS | WARN | FAIL |
|--------|------|------|------|
| API p95 latency | <= budget | up to +25% over budget | > +25% over budget |
| Throughput | >= minimum | within 10% below minimum | > 10% below minimum |
| Error rate | <= budget | up to 1.5x budget | > 1.5x budget |
| Bundle size | <= budget | up to +15% over budget | > +15% over budget |

## CI Tier Rules

| Scenario Characteristics | Assigned Tier |
|--------------------------|---------------|
| Load test, <= 2 min, <= 10 VUs | PR_gate |
| Load test, > 10 min or > 50 VUs | nightly |
| Soak test (any duration) | nightly |
| Spike test, <= 300 VUs | nightly |
| Stress test (any) | pre_release |
| Spike test, > 300 VUs | pre_release |

**Tier definitions:**

- **PR_gate** — runs on every pull request; must complete in under 5 minutes
- **nightly** — scheduled overnight; full suite with baseline comparison
- **pre_release** — manual trigger before release; capacity, stress, spike testing

## Exit Codes

The `check` subcommand returns a CI-friendly exit code:

| Exit code | Meaning |
|-----------|---------|
| `0` | All metrics PASS or WARN (CI allows merge) |
| `1` | One or more metrics FAIL (CI blocks merge) |

Use in CI pipelines:

```bash
python scripts/perf_budget_checker.py check --input data/sample-perf-results.json || exit 1
```

## Input File Format (`data/sample-perf-results.json`)

```json
{
  "service_name": "My SaaS App",
  "test_date": "2026-03-21",
  "environment": "staging-prod-parity",
  "budgets": {
    "lcp_ms": 2500,
    "inp_ms": 200,
    "cls": 0.1,
    "api_p95_ms": 400,
    "api_throughput_rps": 150,
    "error_rate_pct": 1.0,
    "bundle_size_kb": 350
  },
  "results": {
    "lcp_ms": 2810,
    "inp_ms": 185,
    "cls": 0.06,
    "api_p95_ms": 387,
    "api_throughput_rps": 162,
    "error_rate_pct": 0.4,
    "bundle_size_kb": 412
  },
  "test_scenarios": [
    {
      "name": "smoke_login_dashboard",
      "type": "load",
      "duration_minutes": 1,
      "virtual_users": 5,
      "description": "Smoke check for PR gate."
    }
  ]
}
```

| Field | Notes |
|-------|-------|
| `budgets.*` | All keys are optional; only present keys are checked |
| `results.*` | Must match the same keys in `budgets` to be evaluated |
| `test_scenarios[].type` | `load` / `stress` / `soak` / `spike` |
| `test_scenarios[].duration_minutes` | Used for tier assignment |
| `test_scenarios[].virtual_users` | Used for tier assignment |

## Subcommand Reference

```bash
python scripts/perf_budget_checker.py check  --help
python scripts/perf_budget_checker.py plan   --help
python scripts/perf_budget_checker.py report --help
```
