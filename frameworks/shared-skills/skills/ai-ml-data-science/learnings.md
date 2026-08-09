# ai-ml-data-science — Learnings

## Patterns That Work

## Mistakes to Avoid

- [2026-07-11] SHAP >=0.45.0 returns shap_values() as an ndarray, not a per-class list; shap_values[1] on binary classifiers now indexes sample 1, not the positive class. Use explainer(X) Explanation objects.
## Domain Knowledge

- [2026-07-11] 2026-07 versions: Optuna 4.9.x (v4 removed suggest_uniform family), scikit-learn 1.9.0, imbalanced-learn 0.14.x, LightGBM 4.6.x, XGBoost 3.2. Verify before citing.
## Open Questions

## Consolidated Principles

