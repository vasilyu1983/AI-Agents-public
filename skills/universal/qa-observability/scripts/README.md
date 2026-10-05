# observability_scorer.py — Quick Start

Stdlib-only Python CLI for scoring observability maturity and calculating SLO error budget status.
No pip dependencies — runs on Python 3.9+.

## Requirements

Python 3.9+. No pip dependencies.

## Commands

### `maturity` — Observability maturity score and per-dimension breakdown

```bash
python scripts/observability_scorer.py maturity \
  --input data/sample-observability-profile.json
```

Outputs:
- Total score (0–100) and maturity level
- Per-dimension scores with visual bar and rating (COMPLETE / PARTIAL / MISSING)
- Summary of MISSING and PARTIAL dimensions

**Maturity levels:**

| Level | Score Range | Meaning |
|---|---|---|
| ADVANCED | ≥ 85 | Highest bundled self-assessment band |
| PROFICIENT | 65–84 | Upper-middle bundled self-assessment band |
| DEVELOPING | 40–64 | Lower-middle bundled self-assessment band |
| FOUNDATIONAL | < 40 | Lowest bundled self-assessment band |

**Signal dimensions and weights:**

| Dimension | Max Score | What it measures |
|---|---|---|
| structured_logs | 20 | JSON logs, correlation IDs in logs, PII redaction |
| metrics | 20 | Golden signals, histograms, exemplars |
| distributed_tracing | 20 | Auto-instrumentation, manual spans, propagation |
| slo_sli | 15 | SLI/SLO definitions and error budget policy |
| alerting | 15 | Burn-rate alerts, alert fatigue management |
| correlation_ids | 10 | Request ID propagation within and across services |

### `slo` — SLO error budget status

```bash
python scripts/observability_scorer.py slo \
  --input data/sample-slo-data.json
```

Outputs a table of each SLO with:
- Target and actual availability
- Current burn rate (`(1 − actual) / (1 − target)`)
- Budget consumed percentage
- Status flag

Inputs must represent the complete declared SLO window. Counts, when supplied, determine actual availability; otherwise an explicit percentage is required. This calculation cannot forecast exhaustion or evaluate short-window paging rules.

**Status flags (bundled policy heuristics):**

| Status | Condition | Action |
|---|---|---|
| HEALTHY | Complete-window budget consumption ≤ 20% | Interpret with current user impact and recent burn |
| AT_RISK | Consumption > 20% and < 100% | Review against the service policy |
| BUDGET_EXHAUSTED | Consumption ≥ 100% | Apply the service error-budget policy; assess current impact before paging |

Percentage-only input cannot establish remaining budget events; these are reported as unknown. The previous CRITICAL branch had no elapsed-window evidence and is removed.

### `report` — Full observability readiness report

```bash
# Print to stdout
python scripts/observability_scorer.py report \
  --input data/sample-observability-profile.json \
  --slos  data/sample-slo-data.json

# Write to file
python scripts/observability_scorer.py report \
  --input data/sample-observability-profile.json \
  --slos  data/sample-slo-data.json \
  --output report.md

# Maturity only (no SLO section)
python scripts/observability_scorer.py report \
  --input data/sample-observability-profile.json
```

Produces a Markdown report with:
1. Executive summary (score, level, SLO health counts)
2. Maturity scorecard table per dimension
3. SLO error budget status table (if `--slos` provided)
4. Prioritised improvement plan (MISSING → PARTIAL → COMPLETE)
5. SLO remediation actions for non-healthy SLOs

## Scoring Model

Six signal dimensions, each scored 0–max and summed to a total out of 100:

| Dimension | Max | Checked fields |
|---|---|---|
| structured_logs | 20 | `has`, `json_format`, `correlation_id`, `pii_redacted`, `score` |
| metrics | 20 | `has`, `golden_signals_covered`, `histograms`, `exemplars`, `score` |
| distributed_tracing | 20 | `has`, `auto_instrumented`, `manual_spans`, `propagation_verified`, `score` |
| slo_sli | 15 | `defined`, `error_budget_policy`, `score` |
| alerting | 15 | `burn_rate_alerts`, `no_alert_fatigue`, `score` |
| correlation_ids | 10 | `request_id`, `across_services`, `score` |

The `score` field in the input JSON is the authoritative value used for scoring.
Boolean fields are informational and support the maturity report narrative. Scores are a self-assessment, not observed runtime readiness. Supplied scores must be integers within each dimension’s range; unknown dimensions and malformed entries are errors. An omitted dimension contributes zero.

## Input Format

### Observability profile (`--input`)

See `data/sample-observability-profile.json` for the full schema. Key fields:

```json
{
  "service_name": "checkout-service",
  "stack": "Node.js / TypeScript",
  "environment": "production",
  "notes": "Free-text context for the report",
  "signals": {
    "structured_logs": {
      "has": true,
      "json_format": true,
      "correlation_id": true,
      "pii_redacted": false,
      "score": 14
    },
    "metrics": { "has": true, "golden_signals_covered": true, "histograms": true, "exemplars": false, "score": 16 },
    "distributed_tracing": { "has": true, "auto_instrumented": true, "manual_spans": false, "propagation_verified": true, "score": 13 },
    "slo_sli": { "defined": true, "error_budget_policy": false, "score": 8 },
    "alerting": { "burn_rate_alerts": false, "no_alert_fatigue": false, "score": 5 },
    "correlation_ids": { "request_id": true, "across_services": false, "score": 5 }
  }
}
```

### SLO data (`--slos`)

See `data/sample-slo-data.json` for the full schema. Key fields:

```json
[
  {
    "name": "checkout-availability",
    "service": "checkout-service",
    "metric_type": "availability",
    "target_pct": 99.9,
    "window_days": 30,
    "current_availability_pct": 99.85,
    "good_events": 2156340,
    "total_events": 2157780
  }
]
```

Profiles require a nonempty `service_name` and a `signals` object. SLO input requires a nonempty array, nonempty name/service, a target strictly between 0 and 100, and a positive integer `window_days`. Supply either both integer event counts (`0 <= good_events <= total_events`, total positive) or an explicit availability percentage from 0 through 100. Numbers must be finite and cannot be booleans or strings. Malformed input exits nonzero before a result is produced.

Run offline regressions with `python3 -m pytest scripts/test_observability_scorer.py -q`. Set `OBSERVABILITY_SCORER_SCRIPT` to a saved script path to compare implementations.

## Help

```bash
python scripts/observability_scorer.py --help
python scripts/observability_scorer.py maturity --help
python scripts/observability_scorer.py slo --help
python scripts/observability_scorer.py report --help
```
