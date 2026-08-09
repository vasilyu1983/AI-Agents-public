---
name: ai-ml-data-science
description: "ML and data science workflows - EDA, feature engineering, modelling, evaluation, and production handoff. Use when exploring data or building models."
compatibility: Portable core. Works on Claude Code and Codex.
version: "1.1"
last_validated: 2026-07-11
---

# Data Science Engineering Suite

Use this skill for reproducible data-science work from problem framing through evaluation and handoff. The center of gravity is not "pick the fanciest model." It is framing the decision, building train-serve-safe features, and producing decision-ready evidence.

## ASCII Flow

```text
data question
  |
  v
problem framing
  target + unit of analysis + leakage risks + decision/use case
  |
  v
data work
  source checks + EDA + feature logic + split strategy + baseline
  |
  v
model/evidence
  train or analyze + validate + interpret + quantify uncertainty
  |
  v
handoff
  report, notebook, model candidate, or production path to MLOps
```

## Quick Reference

| Need | Default Direction |
|------|-------------------|
| reproducible Python workflow | `uv` plus scripts or git-friendly notebooks (marimo for reactive/diffable notebooks) |
| fast local analysis | DuckDB plus Polars (v1.x stable API as of 2026; pre-1.0 API-churn concerns no longer apply) |
| data contracts | Pandera or GX Core at dataset boundaries |
| tabular baseline | linear or logistic model plus tree-based candidate |
| feature engineering | explicit train-serve-safe transforms |
| tuning | Optuna only after the baseline is stable |
| evaluation | slices, threshold, calibration, uncertainty |
| handoff | model card, evaluation report, failure modes, monitoring expectations |

## When To Use This Skill

- exploring datasets and checking modelling feasibility
- designing feature pipelines and leakage controls
- choosing and comparing model families
- building reproducible experiment workflows
- producing evaluation reports, model cards, and handoff artifacts
- reviewing whether an experiment is genuinely ready for production handoff

## Route Elsewhere

- serving, retraining automation, monitoring, or incident response -> [ai-mlops](../ai-mlops/SKILL.md)
- forecasting and temporal validation -> [ai-ml-timeseries](../ai-ml-timeseries/SKILL.md)
- lakehouse, ingestion, or streaming infrastructure -> [data-lake-platform](../data-lake-platform/SKILL.md)
- prompting, fine-tuning, or LLM-system design -> [ai-llm](../ai-llm/SKILL.md) or [ai-rag](../ai-rag/SKILL.md)

---

## Workflow

1. Frame the decision, target, baseline, and prediction timestamp before touching models.
2. Validate the dataset shape, ownership, and leakage risks.
3. Build the simplest viable baseline first.
4. Design point-in-time-correct features and compare stronger candidates only after the baseline is trustworthy.
5. Evaluate with the same split strategy, same metric definitions, and same compute budget.
6. Produce handoff artifacts with thresholds, calibration state, failure modes, and reproducibility notes.

---

## Core Rules

- write down the prediction timestamp explicitly
- do not trust random splits where time or entity leakage is plausible
- compare at least one simple baseline against one stronger candidate
- treat thresholding, calibration, and uncertainty as part of the decision
- keep data version, feature version, seed, and split logic reproducible
- hand off deployment-heavy questions early instead of rebuilding MLOps inside a notebook

## Known Traps

- Using random train/test splits when time, entity, household, account, or session leakage is plausible.
- Building features with information that is only available after the prediction point, then calling the result "production ready."
- Tuning models before the baseline and metric definitions are stable.
- Reporting only AUC or one aggregate score while ignoring threshold choice, calibration, slice behavior, and operational tradeoffs.
- Letting notebook state become the real pipeline logic. Hidden ordering and cached state break reproducibility fast.
- A single feature with near-perfect standalone separation, or a metric a domain expert would find implausibly good — treat as a leakage bug report first, a discovery second (see `references/eda-best-practices.md` Expert Instincts).
- A correct time-based split with no group/entity split alongside it, when the same user/account/household recurs across time periods — time discipline alone does not stop entity leakage.
- Citing a library version, benchmark number, or API pattern from memory or an older tutorial without checking it against the currently installed version — tabular-ML tooling (Optuna, SHAP, scikit-learn, boosted-tree libraries) crosses breaking major versions inside a single year.

## Common Anti-Patterns

- Treating a more complex model as progress when the baseline is not yet well understood.
- Optimizing benchmark metrics without checking train-serve parity for feature computation.
- Using global preprocessing shortcuts that leak label or split information across folds.
- Handing off a model without a model card, failure modes, threshold rationale, and monitoring expectations.

## Pattern Chooser

| Problem Shape | Direction |
|---------------|-----------|
| tabular or relational | baseline plus tree-based comparison |
| time-ordered forecasting | route to [ai-ml-timeseries](../ai-ml-timeseries/SKILL.md) |
| classical text or embeddings plus classifier | stay here |
| LLM workflow, prompting, or RAG | route to [ai-llm](../ai-llm/SKILL.md) or [ai-rag](../ai-rag/SKILL.md) |
| deployment, monitoring, retraining | route to [ai-mlops](../ai-mlops/SKILL.md) |
| ingestion or lakehouse architecture | route to [data-lake-platform](../data-lake-platform/SKILL.md) |

---

## Core Patterns

### End-to-end DS lifecycle

- problem framing and baseline
- dataset scan and contracts
- EDA and leakage review
- feature plan
- baseline versus candidate comparison
- evaluation with slices and thresholds
- production handoff package

### Reproducible workspace

- `uv` and explicit dependencies
- script-first or git-friendly notebook entrypoints — for reactive, git-diffable notebooks consider [marimo](https://docs.marimo.io/) as an alternative to Jupyter; marimo is reactive (dependent cells auto-rerun), stores notebooks as plain Python scripts, and eliminates hidden-state ordering issues
- fixed seeds and explicit split logic
- logged dataset and feature assumptions

### Feature engineering and contracts

- numeric, categorical, text, and time-based transforms
- point-in-time availability checks
- reusable encoders and documented freshness assumptions

### Evaluation and decision readiness

- primary metric plus guardrails
- threshold strategy
- calibration and uncertainty handling
- slice analysis and qualitative error review

### Autonomous experimentation

Use agent-driven experiment loops only when the metric is explicit, the search space is bounded, and each run is cheap enough to keep or revert automatically.

---

## Templates

- [assets/project/template-standard.md](assets/project/template-standard.md)
- [assets/project/template-quick.md](assets/project/template-quick.md)
- [assets/features/template-feature-engineering.md](assets/features/template-feature-engineering.md)
- [assets/eda/template-eda.md](assets/eda/template-eda.md)
- [assets/evaluation/template-evaluation-report.md](assets/evaluation/template-evaluation-report.md)
- [assets/evaluation/template-model-card.md](assets/evaluation/template-model-card.md)
- [assets/review/experiment-review-template.md](assets/review/experiment-review-template.md)

## Scripts

| Script | Purpose |
|--------|---------|
| [scripts/ml_toolkit.py](scripts/ml_toolkit.py) | Generates model cards, leakage checks, and model-quality reports from a model-spec JSON |
| [scripts/leakage_scan.py](scripts/leakage_scan.py) | Static leakage scanner for ML feature/target column specs (JSON/JSONL). Flags time-leakage, target-leakage, and ID-leakage anti-patterns from column metadata. Exit code 1 if issues found. |

Typical usage:

```bash
python scripts/ml_toolkit.py card --input data/sample-model-spec.json
python scripts/ml_toolkit.py leakage --input data/sample-model-spec.json
python scripts/ml_toolkit.py report --input data/sample-model-spec.json --output report.md
```

See [scripts/README.md](scripts/README.md) for the input format and leakage-check logic.

## Navigation

### Core references

- [references/eda-best-practices.md](references/eda-best-practices.md)
- [references/feature-engineering-patterns.md](references/feature-engineering-patterns.md)
- [references/data-contracts-lineage.md](references/data-contracts-lineage.md)
- [references/modelling-patterns.md](references/modelling-patterns.md)
- [references/evaluation-patterns.md](references/evaluation-patterns.md)
- [references/class-imbalance-patterns.md](references/class-imbalance-patterns.md)
- [references/hyperparameter-optimization.md](references/hyperparameter-optimization.md)
- [references/interpretability-explainability.md](references/interpretability-explainability.md)
- [references/reproducibility-checklist.md](references/reproducibility-checklist.md)
- [references/llm-data-pipeline.md](references/llm-data-pipeline.md) — LLM-from-scratch data pipelines (dedup, quality filtering, synthetic mixing, decontamination); route here first for corpus curation work
- [references/ml-diagrams.md](references/ml-diagrams.md) — Mermaid diagram catalog for classical ML (k-means, logistic regression, decision trees, collaborative filtering) and neural net architectures (MLP, RNN, CNN, Transformer); for embedding in docs, READMEs, PR descriptions

### Data and external references

- [data/sources.json](data/sources.json)
- [data/sample-model-spec.json](data/sample-model-spec.json)

## Related Skills

- [ai-architecture-advisor](../ai-architecture-advisor/SKILL.md) — when to use trees vs deep learning vs LLM (decide before building)
- [ai-mlops](../ai-mlops/SKILL.md)
- [ai-ml-timeseries](../ai-ml-timeseries/SKILL.md)
- [data-lake-platform](../data-lake-platform/SKILL.md)
- [ai-llm](../ai-llm/SKILL.md)
- [ai-rag](../ai-rag/SKILL.md)
- huggingface-datasets — now in the external `huggingface-skills:` plugin

## Fact-Checking

- Known bugs, regressions, framework/compiler/runtime footguns, and version-specific crash or workaround guidance must be verified against current primary web sources before being treated as current fact.
- Verify current library capabilities, version-sensitive tooling advice, and benchmark claims before final answers.
- Prefer official docs for fast-moving tools and model libraries.
- If web access is unavailable, keep tool recommendations marked as unverified where freshness matters.

## Learnings Loop

Before applying this skill on a non-trivial task, read `learnings.consolidated.md` in this directory (and `learnings.md` if present).

After applying it, if you encountered a pattern worth remembering, a mistake worth preventing, or a domain fact that surprised you, append one dated bullet to `learnings.md` via `agents-skills-feedback-loop/scripts/append_learning.py`. Do not modify `SKILL.md` itself.

