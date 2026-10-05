# data-analytics-engineering scripts

Stdlib-only Python tools for validating, linting, and reporting on analytics metric dictionaries.
No pip dependencies required. Python 3.8+.

## Scripts

| Script | Purpose |
|--------|---------|
| `analytics_linter.py` | Validate, lint, and health-score a metric dictionary JSON file |

## Quick start

Run all examples from the skill root directory:

```bash
# Validate required fields, duplicate names, and undefined data sources
python scripts/analytics_linter.py validate --input data/valid-metric-dictionary.json
```

```bash
# Lint metric quality: missing owners, undocumented dimensions, naming conventions, SLAs
python scripts/analytics_linter.py lint --input data/valid-metric-dictionary.json
```

```bash
# Generate a full Markdown health report (stdout or file)
python scripts/analytics_linter.py report \
  --input data/sample-metric-dictionary.json \
  --output metric-health-report.md
```

## Input format

`analytics_linter.py` expects a JSON object with the following top-level keys:

```json
{
  "company_name": "Acme Corp",
  "last_updated": "2026-03-21",
  "metrics": [...]
}
```

Each metric object supports these fields:

| Field | Required | Points |
|-------|:--------:|-------:|
| `name` | yes | — |
| `category` | no | — |
| `description` | yes | +20 |
| `formula` | yes | +20 |
| `owner` | yes | +20 |
| `data_source` | yes | +15 |
| `refresh_cadence` | yes | +10 |
| `dimensions` | no | +10 |
| `example_value` | no | +5 |

Use `data/valid-metric-dictionary.json` for passing smoke tests and quickstart
commands. Use `data/sample-metric-dictionary.json` when you need an intentional
failure fixture with incomplete metrics.

## Scoring tiers

| Tier | Score |
|------|-------|
| PRODUCTION_READY | ≥ 85 |
| NEEDS_WORK | 60 – 84 |
| CRITICAL_GAPS | < 60 |

The overall dictionary health score is the average quality score across all metrics.

## Options

```
--no-color    Disable ANSI color output (useful for CI logs or piping to files)
```

Example without color:

```bash
python scripts/analytics_linter.py --no-color lint --input data/valid-metric-dictionary.json
```
