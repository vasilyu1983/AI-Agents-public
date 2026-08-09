# Model Selection Guide for Forecasting

Operational decision rules for choosing a forecasting model family in May 2026.

Start with **problem shape**, not package hype.

## Table of Contents

- [First Principles](#first-principles)
- [Required Baselines](#required-baselines)
- [Decision Axes](#decision-axes)
- [Model Family Matrix](#model-family-matrix)
- [Practical Selection Rules](#practical-selection-rules)
- [1. Start Local Only When The Problem Is Truly Local](#1-start-local-only-when-the-problem-is-truly-local)
- [2. Default To Feature-Based Global Forecasting For Many Related Series](#2-default-to-feature-based-global-forecasting-for-many-related-series)
- [3. Use Deep Forecasting When Shared Dynamics Matter More Than Hand-Crafted Features](#3-use-deep-forecasting-when-shared-dynamics-matter-more-than-hand-crafted-features)
- [4. Use TS Foundation Models As Baselines Or When Feature Engineering Is Weak](#4-use-ts-foundation-models-as-baselines-or-when-feature-engineering-is-weak)
- [5. Add Hierarchical Reconciliation When Forecasts Must Be Coherent](#5-add-hierarchical-reconciliation-when-forecasts-must-be-coherent)
- [What To De-Emphasize In 2026](#what-to-de-emphasize-in-2026)
- [Selection Checklist](#selection-checklist)
- [Cross-References](#cross-references)

## First Principles

- Start with naive and seasonal-naive baselines.
- Define the prediction cutoff and horizon before choosing a model.
- Pick the simplest family that fits the data shape, covariates, and operating constraints.
- Compare models under the same rolling-origin validation scheme.

## Required Baselines

Use at least two of:

- Naive: `y[t] = y[t-1]`
- Seasonal naive: `y[t] = y[t-s]`
- Moving average or drift baseline
- ETS or SARIMAX when a local statistical baseline is appropriate

Candidate models do not earn deployment if they do not beat these baselines in a stable way.

## Decision Axes

Choose the model family using these axes:

1. Single series vs many related series
2. Few covariates vs rich known-future covariates
3. Point forecast only vs probabilistic forecast required
4. Short horizon vs long horizon
5. Interpretability/latency constraints vs raw accuracy focus

## Model Family Matrix

| Family | Best For | Strengths | Limits | Good Defaults |
|--------|----------|-----------|--------|---------------|
| Local classical models | Single series, low covariates, interpretable baselines | Fast, explainable, low maintenance | Weak on rich cross-series sharing | Naive, seasonal naive, ETS, SARIMAX |
| Feature-based global models | Many related series, covariate-rich forecasting | Strong accuracy/cost tradeoff, scalable, explainable enough | Need careful feature design and cutoff safety | LightGBM/XGBoost with MLForecast or skforecast |
| Deep sequence models | Large panels, complex dynamics, longer horizons | Learns shared temporal structure, native probabilistic heads | Higher training complexity, harder debugging | TFT, DeepAR, N-BEATS, modern seq2seq stacks |
| Time-series foundation models | Zero-shot baselines, low-feature setups, long-horizon benchmarking | Strong zero-shot baseline, fast benchmarking, low feature-engineering burden | Not always cheapest or most interpretable; current capability changes quickly | Chronos-2 / Chronos-Bolt (Amazon, 2025), TimesFM, Toto (Datadog, observability), AutoGluon TimeSeries TSFMs; verify current releases before recommending |
| Hierarchical reconciliation layer | Forecasts must add up across levels | Coherence across hierarchy, decision-ready rollups | Requires hierarchy design and residual/error tracking | HierarchicalForecast on top of base forecasts |

## Practical Selection Rules

### 1. Start Local Only When The Problem Is Truly Local

Use local statistical models when:

- you have a single important series or a small portfolio
- covariates are minimal
- interpretability matters more than extracting cross-series signal
- you need a strong baseline before escalating complexity

Prefer ETS/SARIMAX over niche legacy tools unless a specific seasonality pattern clearly justifies something else.

### 2. Default To Feature-Based Global Forecasting For Many Related Series

Use feature-based boosting when:

- you have many related series
- promotions, prices, holidays, or weather matter
- you need a practical accuracy/latency/maintenance balance
- you want explainability via feature importance or SHAP

This is the default practical choice for many production retail, demand, traffic, and operations forecasts.

### 3. Use Deep Forecasting When Shared Dynamics Matter More Than Hand-Crafted Features

Use deep sequence models when:

- the panel is large enough to justify representation learning
- long or variable horizons matter
- complex nonlinear temporal dependencies exist
- you need native probabilistic outputs and are prepared for higher training cost

### 4. Use TS Foundation Models As Baselines Or When Feature Engineering Is Weak

Use TSFMs when:

- you need a strong zero-shot benchmark quickly
- you have limited time for feature engineering
- long-horizon or sparse-feature settings make handcrafted features fragile
- you need a realistic benchmark before investing in supervised modelling

Do not assume a TSFM wins automatically. Benchmark it against seasonal-naive and feature-based global models.

### 5. Add Hierarchical Reconciliation When Forecasts Must Be Coherent

Use hierarchical reconciliation when:

- forecasts must add up across product, region, channel, or time aggregation levels
- planning or finance workflows depend on coherent rollups
- errors at one level create operational confusion upstream or downstream

## What To De-Emphasize In 2026

- Prophet is a niche option, not a default answer.
- TBATS is specialized, not a first-line recommendation.
- RNN-first thinking is usually weaker than modern global boosting, TSFMs, or stronger sequence models.
- Static "best model" rankings age badly; validate against current official docs and actual task constraints.
- When comparing TSFMs, prefer fev-bench results over informal ablations (https://huggingface.co/spaces/autogluon/fev-bench) — it covers 100 tasks, point and probabilistic metrics, and covariate-inclusive settings.

## Selection Checklist

- [ ] Prediction cutoff and horizon defined
- [ ] Naive and seasonal-naive baselines compared
- [ ] Model family chosen from data shape, not hype
- [ ] Known-future covariates separated from future-unknown covariates
- [ ] Validation scheme matches deployment reality
- [ ] Horizon-wise and slice-wise metrics defined ahead of tuning
- [ ] Probabilistic need decided explicitly
- [ ] Hierarchical coherence requirement checked
- [ ] Latency, interpretability, and maintenance costs documented

## Cross-References

- [global-panel-forecasting-patterns.md](global-panel-forecasting-patterns.md) - shared models and panel schemas
- [lightgbm-ts-patterns.md](lightgbm-ts-patterns.md) - feature-based/global boosting patterns
- [probabilistic-forecasting.md](probabilistic-forecasting.md) - intervals, quantiles, and calibration
- [ts-llm-patterns.md](ts-llm-patterns.md) - TS foundation model selection and zero-shot benchmarking
