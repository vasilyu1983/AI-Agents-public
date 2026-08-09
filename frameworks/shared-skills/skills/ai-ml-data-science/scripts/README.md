# ml_toolkit.py

Stdlib-only Python CLI for ML model quality checks. No external dependencies — runs with any Python 3.9+ installation.

## Purpose

Gives data scientists and ML engineers fast, reproducible answers to three core questions:

1. **card** — What does this model do, how does it perform, and what are its risks? (Markdown model card)
2. **leakage** — Does this model spec pass temporal discipline and leakage checks? (PASS/WARN/FAIL per check)
3. **report** — A full Markdown quality report combining card + leakage analysis.

## Quick Start

Run from the `ai-ml-data-science/` directory:

```bash
# Generate a model card (prints to stdout)
python scripts/ml_toolkit.py card --input data/sample-model-spec.json

# Generate a model card and write to file
python scripts/ml_toolkit.py card --input data/sample-model-spec.json --output /tmp/model-card.md

# Run the leakage checklist (console output with PASS/WARN/FAIL per check)
python scripts/ml_toolkit.py leakage --input data/sample-model-spec.json

# Run leakage checklist and write a Markdown report to file
python scripts/ml_toolkit.py leakage --input data/sample-model-spec.json --output /tmp/leakage-report.md

# Full quality report combining card + leakage (prints to stdout)
python scripts/ml_toolkit.py report --input data/sample-model-spec.json

# Full quality report written to file
python scripts/ml_toolkit.py report --input data/sample-model-spec.json --output report.md
```

## JSON Input Format

All subcommands read from `--input <json_file>`. The sample spec at `data/sample-model-spec.json` documents all supported fields.

### Minimum viable spec

```json
{
  "model_name": "my-model",
  "version": "1.0.0",
  "model_type": "classification",
  "task_description": "Predict X given Y.",
  "intended_use": "Trigger action Z when score >= 0.5.",
  "training_data": {
    "source": "warehouse.feature_mart",
    "date_range": {"start": "2024-01-01", "end": "2025-06-30"},
    "row_count": 100000,
    "feature_count": 20,
    "target_variable": "outcome_flag",
    "temporal_column": "snapshot_date",
    "data_collection_date": "2025-07-10"
  },
  "features": [
    {"name": "days_since_last_event", "type": "numeric", "description": "Days since last recorded event"},
    {"name": "account_age_days",      "type": "numeric", "description": "Age of the account in days"}
  ],
  "performance_metrics": [
    {"metric": "ROC-AUC", "value": 0.82, "benchmark": 0.75, "split": "temporal-holdout"}
  ],
  "limitations": ["Model not validated on accounts < 30 days old."],
  "ethical_considerations": ["Do not use scores to deny service."],
  "prediction_timestamp_defined": true,
  "prediction_timestamp_field": "snapshot_date",
  "label_timestamp_field": "outcome_event_date",
  "train_val_test_split_method": "temporal",
  "split_config": {
    "train_end": "2025-03-31",
    "val_end": "2025-05-31",
    "test_end": "2025-06-30"
  }
}
```

## Leakage Checks Reference

| Check | What it looks for | FAIL condition | WARN condition |
|---|---|---|---|
| Prediction timestamp defined | `prediction_timestamp_defined` and `prediction_timestamp_field` present; distinct from `label_timestamp_field` | Missing or same field for pred/label | `label_timestamp_field` not set |
| No future-leaking features | Feature names containing `future_`, `next_`, `post_`, `after_label` | — | Any feature name matches a keyword |
| Temporal split discipline | `train_val_test_split_method` is temporal; `split_config` dates in ascending order | Random split with a temporal column, or dates out of order | Unknown split method |
| Target leakage | Feature names containing target-derived patterns or the target variable name | — | Any feature name matches |
| Data collection date | `training_data.data_collection_date` is present | Missing field | — |

## Subcommand Reference

```
python scripts/ml_toolkit.py card    --help
python scripts/ml_toolkit.py leakage --help
python scripts/ml_toolkit.py report  --help
```

## Model Card Sections

The `card` and `report` subcommands produce a Markdown model card with these sections:

| Section | Content |
|---|---|
| Model Overview | Task description and model type |
| Intended Use | Approved uses and explicit exclusions |
| Training Data | Source, date range, row/feature count, target, temporal column |
| Performance Metrics | Table: metric, value, benchmark, gap, split |
| Known Limitations | Bulleted list of documented failure conditions |
| Ethical Considerations | Bulleted list of fairness and misuse risks |
| Versioning and Lineage | Split config, timestamps, experiment/artifact IDs |
