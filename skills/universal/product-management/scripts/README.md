# product_scorer.py — Quick Start

Stdlib-only Python CLI for product prioritization (RICE) and a pre-PMF opportunity score. No pip install needed.

Inputs reject duplicate JSON keys, nonfinite numbers, malformed records and booleans in numeric fields before writing scored output. Validation errors exit nonzero; the documented field ranges below are enforced. Run `python3 scripts/test_product_scorer.py` for offline CLI regressions.

```bash
python scripts/product_scorer.py <subcommand> --help
```

---

## Subcommands

### `rice` — RICE Prioritization

Scores each feature as `RICE = (Reach × Impact × Confidence) / Effort` and ranks descending.

**Input fields** (per feature in `data/sample-features.json`):

| Field | Type | Values |
|-------|------|--------|
| `reach` | int | users/quarter, 0–10000 |
| `impact` | float | 0.25, 0.5, 1, 2, 3 |
| `confidence` | float | 0.5, 0.8, 1.0 |
| `effort_weeks` | float | person-weeks, 0.5–26 |
| `theme` | string | growth, retention, monetization, infra |

```bash
# Full backlog ranked
python scripts/product_scorer.py rice \
  --input data/sample-features.json

# Filter to retention theme, show top 3
python scripts/product_scorer.py rice \
  --input data/sample-features.json \
  --theme retention \
  --top 3

# Write ranked JSON output
python scripts/product_scorer.py rice \
  --input data/sample-features.json \
  --output /tmp/ranked-features.json
```

---

### `pmf` — Pre-PMF Opportunity Score

Scores five judgment dimensions (problem, solution, timing, team, economics) and returns a verdict band. **This is a pre-PMF opportunity score, not a PMF measurement:** it takes no retention input, so it cannot show product-market fit. For a PMF verdict, score retention and the other evidence in [`../assets/pmf-scorecard-b2b.yaml`](../assets/pmf-scorecard-b2b.yaml) or [`../assets/pmf-scorecard-b2c.yaml`](../assets/pmf-scorecard-b2c.yaml).

**Dimension weights:**

| Dimension | Weight |
|-----------|-------:|
| Solution Quality | 30% |
| Problem Severity | 25% |
| Economic Viability | 15% |
| Market Timing | 20% |
| Team–Market Fit | 10% |

**Heuristic verdict thresholds** (valid inputs produce a 5–25 score):

| Verdict | Range |
|---------|-------|
| STRONG | ≥ 20 |
| SIGNALS | 14 ≤ score < 20 |
| WEAK | 8 ≤ score < 14 |
| NO_SIGNAL | < 8 |

```bash
# Score a pre-PMF opportunity assessment
python scripts/product_scorer.py pmf \
  --input data/sample-pmf-data.json
```

---

### `report` — Full Product Health Report

Combines RICE backlog prioritization and the pre-PMF opportunity assessment into a Markdown report.

```bash
# Print report to stdout
python scripts/product_scorer.py report \
  --input data/sample-features.json \
  --pmf data/sample-pmf-data.json

# Write report to file
python scripts/product_scorer.py report \
  --input data/sample-features.json \
  --pmf data/sample-pmf-data.json \
  --output report.md
```

---

## Sample Data

| File | Description |
|------|-------------|
| `data/sample-features.json` | 10 product features with RICE inputs and themes |
| `data/sample-pmf-data.json` | Synthetic opportunity assessment with five dimension scores and evidence |

---

## Schema Reference

### Feature object (`sample-features.json`)

```json
{
  "id": "F01",
  "name": "Onboarding Checklist",
  "description": "Guided onboarding checklist for new users.",
  "reach": 8500,
  "impact": 3,
  "confidence": 1.0,
  "effort_weeks": 3,
  "theme": "retention"
}
```

### Pre-PMF opportunity assessment (`sample-pmf-data.json`)

```json
{
  "product_name": "Clearpath",
  "assessment_date": "2026-03-21",
  "segment": "SMB operations teams",
  "dimensions": {
    "problem_severity": { "score": 4, "evidence": "..." },
    "solution_quality": { "score": 3, "evidence": "..." },
    "market_timing":    { "score": 4, "evidence": "..." },
    "team_market_fit":  { "score": 3, "evidence": "..." },
    "economic_viability": { "score": 2, "evidence": "..." }
  }
}
```
