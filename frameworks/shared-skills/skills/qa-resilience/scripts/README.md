# resilience_checker.py — Quick Start

Stdlib-only Python CLI that scores resilience pattern coverage for a microservice and surfaces actionable gaps.

## Requirements

Python 3.9+. No pip dependencies.

## Commands

### `assess` — Score resilience pattern coverage

```bash
# Score the sample service profile (prints weighted score and tier)
python scripts/resilience_checker.py assess \
  --input data/sample-service-profile.json
```

```bash
# Score your own service profile
python scripts/resilience_checker.py assess \
  --input path/to/my-service-profile.json
```

### `gaps` — List missing or misconfigured patterns with remediation

```bash
# Show all gaps with failure mode and recommended fix
python scripts/resilience_checker.py gaps \
  --input data/sample-service-profile.json
```

### `report` — Full Markdown resilience assessment report

```bash
# Print report to stdout
python scripts/resilience_checker.py report \
  --input data/sample-service-profile.json
```

```bash
# Write report to file
python scripts/resilience_checker.py report \
  --input data/sample-service-profile.json \
  --output resilience-report.md
```

## Scoring Model

Nine patterns, weighted by failure-mode priority:

| Pattern | Weight | Full credit | Half credit | No credit |
|---------|--------|-------------|-------------|-----------|
| timeouts | 20% | present + correctly configured | present but misconfigured | absent |
| retries | 15% | present + correctly configured | present but misconfigured | absent |
| circuit_breaker | 15% | present + correctly configured | present but misconfigured | absent |
| bulkheads | 15% | present + correctly configured | present but misconfigured | absent |
| graceful_degradation | 15% | present + correctly configured | present but misconfigured | absent |
| health_checks | 10% | present + correctly configured | present but misconfigured | absent |
| retry_budget | 5% | present + correctly configured | present but misconfigured | absent |
| hedging | 3% | present + correctly configured OR explicitly N/A | present but misconfigured | absent |
| chaos_testing | 2% | present + correctly configured | present but misconfigured | absent |

## Resilience Tiers

| Tier | Score |
|------|-------|
| HARDENED | ≥ 80 |
| ADEQUATE | 60–79 |
| AT_RISK | 40–59 |
| VULNERABLE | < 40 |

## Input Format

See `data/sample-service-profile.json` for the full schema. Key fields:

```json
{
  "service_name": "checkout-service",
  "team": "platform-payments",
  "language": "Go",
  "deployment": "Kubernetes",
  "assessed_date": "2026-03-21",
  "dependencies": [
    {
      "name": "payment-gateway",
      "type": "external",
      "criticality": "high",
      "notes": "..."
    }
  ],
  "patterns": {
    "timeouts": {
      "has_it": true,
      "configured_correctly": false,
      "notes": "HTTP client timeout set to 30s globally. No per-dependency tuning..."
    },
    "retries": { "has_it": true, "configured_correctly": false, "notes": "..." },
    "retry_budget": { "has_it": false, "configured_correctly": false, "notes": "..." },
    "hedging": { "has_it": false, "configured_correctly": false, "notes": "..." },
    "circuit_breaker": { "has_it": true, "configured_correctly": false, "notes": "..." },
    "bulkheads": { "has_it": false, "configured_correctly": false, "notes": "..." },
    "graceful_degradation": { "has_it": true, "configured_correctly": true, "notes": "..." },
    "health_checks": { "has_it": true, "configured_correctly": false, "notes": "..." },
    "chaos_testing": { "has_it": false, "configured_correctly": false, "notes": "..." }
  },
  "observability": {
    "has_tracing": true,
    "has_alerts": true,
    "slo_defined": true,
    "slo_target": "99.5% success rate, p99 < 800ms",
    "notes": "..."
  }
}
```

## Help

```bash
python scripts/resilience_checker.py --help
python scripts/resilience_checker.py assess --help
python scripts/resilience_checker.py gaps --help
python scripts/resilience_checker.py report --help
```
