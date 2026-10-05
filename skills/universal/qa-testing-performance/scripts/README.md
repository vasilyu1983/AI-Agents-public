# perf_budget_checker.py

Stdlib-only Python CLI for performance budget validation and CI test planning. No external dependencies — runs with any Python 3.10+ installation.

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

For LCP, INP and CLS, the supplied budget is authoritative: `actual <= budget` passes; exceeding it fails. Google bands appear only as context in the output and cannot override the budget. Check current field-assessment guidance at [web.dev](https://web.dev/articles/vitals) when interpreting results; this checker does not establish field data coverage.

### API and Load Metrics

These are bundled policy heuristics. WARN permits a budget breach and exits successfully; it is not strict SLO enforcement.

| Metric | PASS | WARN | FAIL |
|--------|------|------|------|
| API p95 latency | <= budget | up to +25% over budget | > +25% over budget |
| API p99 / p99.9 latency | <= budget | up to +15% over budget | > +15% over budget |
| Throughput | >= minimum | within 10% below minimum | > 10% below minimum |
| Error rate | <= budget | up to 1.5x budget | > 1.5x budget |
| Bundle size | <= budget | up to +15% over budget | > +15% over budget |

## CI Tier Rules

| Scenario Characteristics | Assigned Tier |
|--------------------------|---------------|
| Load test, <= 2 min, <= 10 VUs | PR_gate |
| Other load tests | nightly |
| Soak test (any duration) | nightly |
| Spike test, <= 300 VUs | nightly |
| Stress or capacity test (any) | pre_release |
| Spike test, > 300 VUs | pre_release |

These tiers are bundled scheduling heuristics, not measured runtime or cost guarantees.

**Tier definitions:**

- **PR_gate** — runs on every pull request; set a runtime budget for the actual environment
- **nightly** — scheduled overnight; full suite with baseline comparison
- **pre_release** — manual trigger before release; capacity, stress, spike testing

## Exit Codes

The `check` and `report` subcommands return CI-friendly exit codes. A failed report is still written before exit 1:

| Exit code | Meaning |
|-----------|---------|
| `0` | All metrics PASS or WARN (CI allows merge) |
| `1` | One or more metrics FAIL (CI blocks merge) |
| `2` | Malformed or unreadable input |

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
| `budgets.*` | Nonempty object of supported metric keys; unknown keys are errors |
| `results.*` | Every budget requires a finite, nonnegative numeric measurement; missing values are errors |
| `test_scenarios[].type` | `load` / `stress` / `soak` / `spike` / `capacity` |
| `test_scenarios[].duration_minutes` | Positive finite number |
| `test_scenarios[].virtual_users` | Positive integer |

Budget and measurement values must be JSON numbers, not booleans or strings. Latency (API), throughput and bundle budgets must be positive; error-rate values are percentages from 0 through 100. Scenario names must be nonempty. `plan` requires a nonempty scenario list; `report` may omit it or use an empty list. Any supplied rows must be valid. Duplicate JSON keys are rejected; input/output errors return 2.

The regression suite requires Node.js for mocked k6 template checks. Run offline regression tests with `python3 -m unittest discover -s scripts -p "test_perf_budget_checker.py"`.

## Subcommand Reference

```bash
python scripts/perf_budget_checker.py check  --help
python scripts/perf_budget_checker.py plan   --help
python scripts/perf_budget_checker.py report --help
```
