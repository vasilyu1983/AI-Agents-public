# roi_calculator.py

Stdlib-only Python CLI for AI coding metrics analysis. No external dependencies — runs with any Python 3.9+ installation.

## Purpose

Gives engineering leaders and productivity teams fast, reproducible answers to three core questions:

1. **ROI** — How much time and money is the program saving? What is the payback period and annualized ROI?
2. **Score** — How healthy is adoption across all 6 metric families? What is the composite grade?
3. **Report** — A full Markdown dashboard combining scorecard, ROI, and per-family signal details.

## Quick Start

Run from the `dev-ai-coding-metrics/` directory:

```bash
# ROI: time saved, cost saved, payback period, annualized ROI %
python scripts/roi_calculator.py roi --input data/sample-ai-metrics.json

# Scorecard: 6-family scores, Strong/Developing/Weak ratings, health grade
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
  "adoption_pct": 72,
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
| `measurement_period_weeks` | score, report | Duration of the measurement window |
| `team_name` | all | Display label in output headers |
| `notes` | report | Free-text context shown in report header |
| `metric_families` | score, report | Object with per-family `score` (0-100) and `signals` array |

See `data/sample-ai-metrics.json` for a complete example with realistic values for a 20-person team.

## Subcommand Reference

```
python scripts/roi_calculator.py roi    --help
python scripts/roi_calculator.py score  --help
python scripts/roi_calculator.py report --help
```

## Scoring: Rating Bands

| Rating | Score Range | Interpretation |
|---|---|---|
| Strong | 80–100 | Healthy signal; sustain and expand |
| Developing | 60–79 | Progress visible; gaps remain |
| Weak | 0–59 | Requires focused intervention |

## Health Grade Scale

| Grade | Composite Score | Interpretation |
|---|---|---|
| A | 90–100 | Excellent across all families |
| B | 80–89 | Strong program with minor gaps |
| C | 70–79 | Mixed results; address weak families |
| D | 60–69 | Below threshold; reassess design |
| F | 0–59 | Program underperforming; consider reset |

## ROI Calculation Notes

The ROI subcommand uses:

- **Weekly hours saved** = `team_size × hours_saved_per_dev_per_week`
- **Annual value** = weekly hours saved × 52 × `avg_dev_hourly_rate`
- **Annual net savings** = annual value − (`ai_tooling_monthly_cost` × 12)
- **Payback period** = monthly tool cost ÷ weekly value of time saved
- **Annualized ROI %** = (annual net savings ÷ annual tool cost) × 100

Hours-saved inputs are self-reported estimates. Apply a conservative discount (50% is a reasonable starting point) before presenting to leadership. Triangulate with delivery and quality metrics from the scorecard.
