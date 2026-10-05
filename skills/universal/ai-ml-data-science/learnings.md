# ai-ml-data-science — Learnings

## Patterns That Work

## Mistakes to Avoid

- [2026-07-11] SHAP >=0.45.0 returns shap_values() as an ndarray, not a per-class list; shap_values[1] on binary classifiers now indexes sample 1, not the positive class. Use explainer(X) Explanation objects.
## Domain Knowledge

- [2026-07-11] (corrected 2026-09-29) The former package-version snapshot is unverified. Check installed releases against official docs. Optuna 4.0 documents the suggest_uniform family as deprecated rather than removed; prefer suggest_float and check the release-specific migration guidance ([Optuna 4.0 Trial docs](https://optuna.readthedocs.io/en/v4.0.0/reference/generated/optuna.trial.Trial.html)).
## Open Questions

## Consolidated Principles

