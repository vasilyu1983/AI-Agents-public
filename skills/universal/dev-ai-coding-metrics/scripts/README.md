# roi_calculator.py

Stdlib-only Python CLI for AI coding metrics analysis. No external dependencies — runs with any Python 3.9+ installation.

## Purpose

Gives engineering leaders and productivity teams fast, reproducible answers to three core questions:

1. **ROI** — How much time and money is the program saving? What is the modeled capacity value and annualized ROI?
2. **Score** — How is each of the 6 metric families rated? There is deliberately no composite grade: a blended score hides a weak Quality family behind strong Adoption.
3. **Report** — A full Markdown dashboard combining per-family ratings, ROI, and per-family signal details.

Missing inputs fail closed: any subcommand exits `2` and names the missing keys instead of scoring zeros.

## Quick Start

Run from the `dev-ai-coding-metrics/` directory:

```bash
# ROI: time saved, cost saved, tool-cost-equivalent weeks, annualized ROI %
python scripts/roi_calculator.py roi --input data/sample-ai-metrics.json

# Scorecard: 6-family scores and Strong/Developing/Weak ratings (no composite)
python scripts/roi_calculator.py score --input data/sample-ai-metrics.json

# Scorecard with all key signals printed per family
python scripts/roi_calculator.py score --input data/sample-ai-metrics.json --signals

# Full Markdown report (prints to stdout)
python scripts/roi_calculator.py report --input data/sample-ai-metrics.json

# Full Markdown report written to file
python scripts/roi_calculator.py report --input data/sample-ai-metrics.json --output /tmp/ai-metrics-report.md
```

## JSON Input Format

All subcommands read from a structured JSON file. Required fields:

```json
{
  "team_name": "Platform Engineering",
  "team_size": 20,
  "measurement_period_weeks": 12,
  "ai_tooling_monthly_cost": 1200,
  "avg_dev_hourly_rate": 95,
  "hours_saved_per_dev_per_week": 3.5,
  "review_hours_per_dev_per_week": 1.0,
  "rework_hours_per_dev_per_week": 0.5,
  "notes": "12-week pilot. Baseline established from prior 12-week period.",
  "metric_families": {
    "adoption":        { "score": 72, "signals": ["..."] },
    "delivery":        { "score": 61, "signals": ["..."] },
    "quality":         { "score": 54, "signals": ["..."] },
    "economics":       { "score": 78, "signals": ["..."] },
    "experience":      { "score": 66, "signals": ["..."] },
    "agent_execution": { "score": 49, "signals": ["..."] }
  }
}
```

| Field | Used by | Notes |
|---|---|---|
| `team_size` | roi | Number of developers in the program |
| `ai_tooling_monthly_cost` | roi | Total monthly spend on AI coding tools ($) |
| `avg_dev_hourly_rate` | roi | Fully-loaded hourly rate per developer ($) |
| `hours_saved_per_dev_per_week` | roi | Self-reported time saved per developer per week |
| `review_hours_per_dev_per_week` | roi (optional) | Extra review time AI output costs per developer per week |
| `rework_hours_per_dev_per_week` | roi (optional) | Time spent fixing AI-assisted changes per developer per week |
| `measurement_period_weeks` | roi, score, report | Positive integer duration of the measurement window; required for ROI |
| `team_name` | all | Display label in output headers |
| `notes` | report | Free-text context shown in report header |
| `metric_families` | score, report | Object with per-family `score` (0-100) and `signals` array; all 6 families are required |

The five `roi` fields and all six `metric_families.<family>.score` values are required for their respective commands; missing or invalid values exit `2`. Numeric inputs must be finite nonnegative numbers, not booleans or numeric strings; team size and observation period must be positive integers. Family scores must be integers from 0 to 100, and signals must be arrays of strings. ROI carries a "not decision-grade" caveat until both burden terms are supplied; use explicit zero only when measured absent.

See `data/sample-ai-metrics.json` for a complete example with realistic values for a 20-person team.

## Subcommand Reference

```
python scripts/roi_calculator.py roi    --help
python scripts/roi_calculator.py score  --help
python scripts/roi_calculator.py report --help
```

## Scoring: Rating Bands

These are illustrative local rubric bands, not validated constructs.

| Rating | Score Range | Interpretation |
|---|---|---|
| Strong | 80–100 | Healthy signal; sustain and expand |
| Developing | 60–79 | Progress visible; gaps remain |
| Weak | 0–59 | Requires focused intervention |

## Exit Codes

| Code | Meaning |
|---|---|
| 0 | Output produced |
| 2 | Insufficient data or invalid input; stderr names the problem and nothing is scored |

Tests: `python3 -m unittest discover -s scripts -p 'test_*.py'`

## ROI Calculation Notes

The ROI subcommand uses:

- **Weekly hours saved** = `team_size × (hours_saved_per_dev_per_week − review_hours_per_dev_per_week − rework_hours_per_dev_per_week)`
- **Annual value** = weekly hours saved × 52 × `avg_dev_hourly_rate`
- **Annual net savings** = annual value − (`ai_tooling_monthly_cost` × 12)
- **Tool-cost-equivalent weeks** = monthly tool cost ÷ weekly value of time saved; this is not investment payback
- **Annualized ROI %** = (annual net savings ÷ annual tool cost) × 100; undefined (`N/A`) when tooling cost is zero

Hours-saved inputs are estimates of capacity value, not realized cash savings. Calibrate assumptions against observed delivery, review burden, rework, and quality outcomes before presenting to leadership.
