# Time-Series Foundation Model Patterns

Operational patterns for using time-series foundation models (TSFMs) in May 2026.

Keep this file focused on **forecasting foundation models**, not generic LLM workflow advice.

## Table of Contents

- [What Changed By 2026](#what-changed-by-2026)
- [When To Use A TSFM](#when-to-use-a-tsfm)
- [Practical Model Roles](#practical-model-roles)
- [Default Evaluation Flow](#default-evaluation-flow)
- [Zero-Shot Benchmark Pattern](#zero-shot-benchmark-pattern)
- [Covariate-Aware Pattern](#covariate-aware-pattern)
- [Hybrid Pattern](#hybrid-pattern)
- [Sampling And Scenario Use](#sampling-and-scenario-use)
- [Anti-Patterns](#anti-patterns)
- [TSFM Checklist](#tsfm-checklist)
- [Cross-References](#cross-references)

## What Changed By 2026

- TSFMs are now credible **zero-shot or light-adaptation baselines**, not just research curiosities.
- The practical question is no longer "LLM or not?" but "does the TSFM beat seasonal-naive and a strong feature-based global model on this task?"
- Current model capabilities move fast, so always verify the official docs or official repositories before making a final recommendation.
- **Benchmarking standard (2025–2026):** fev-bench has emerged as a realistic evaluation framework — 100 forecasting tasks across 7 domains built from 96 datasets, point and probabilistic metrics, covariate-inclusive tasks (30 known-covariate, 24 past-covariate, 19 static-covariate), bootstrapped confidence intervals. Paper: arxiv.org/abs/2509.26468. Leaderboard: https://huggingface.co/spaces/autogluon/fev-bench. Use in place of informal ablation comparisons when assessing TSFM claims.
- **Chronos-2 fev-bench result:** the Chronos-2 paper (arxiv.org/abs/2510.15821) reports a 90.7% win rate and 47.3% skill score on fev-bench, ahead of the next-best pretrained model, TiRex, at 80.8% / 42.6%. Treat these as the published anchor figures as of the Oct 2025 paper, not a permanent ranking — re-check the live leaderboard before quoting them, since new TSFM releases reshuffle it every few months.
- **Leaderboard churn is the norm, not the exception.** TimesFM 2.5 briefly topped GIFT-Eval on release (Sept 2025) before Chronos-2 and Salesforce's Moirai 2.0 displaced it. Do not present any single "best TSFM" claim as durable; state the date of the benchmark snapshot alongside the claim.

## Decision Branch: TSFM Approach Selection

Use this branch when a TSFM is under consideration:

```
Data has ≤50 series with rich known-future covariates?
└── Feature-based supervised global model (e.g., LightGBM with MLForecast)
    Better covariate exploitation; cheaper at inference time

Data has many series, limited feature-engineering time?
├── Zero-shot TSFM → benchmark first (seasonal-naive is the floor)
│   ├── Latency / cost is the binding constraint → Chronos-Bolt (250x faster than original)
│   ├── Strong zero-shot quality needed → Chronos-2 or TimesFM 2.5
│   └── Observability metrics / multivariate → Toto 2.0
│
└── Zero-shot TSFM falls short on your eval?
    ├── LoRA fine-tune on your domain (TimesFM 2.5 via HF PEFT; Chronos fine-tune path)
    └── Escalate to supervised global model with lag/rolling features
```

Verify any specific TSFM capability (covariate API, fine-tuning path, max horizon) against the official repository or model card before relying on it.

## When To Use A TSFM

Use a TSFM when:

- you need a strong zero-shot baseline quickly
- feature engineering time is limited
- the horizon is long enough that handcrafted features may be brittle
- the problem has many related series but limited bespoke modelling time
- you want a benchmark before investing in supervised tuning

Do not default to a TSFM when:

- a simple seasonal-naive baseline already meets the need
- rich known-future covariates dominate the problem and a feature-based model can exploit them better
- the deployment needs strict interpretability or very tight, cheap latency

### Judgment Call: Where TSFMs Actually Win In Practice

The honest 2026 picture, distilled from fev-bench and GIFT-Eval results: TSFMs win by the largest margins on **covariate-informed and multivariate tasks with limited history per series** — new products, thin long-tail SKUs, or cold-start series where a feature-based model has too little data per `unique_id` to learn stable coefficients but the TSFM can transfer cross-series structure zero-shot. They also win when the team genuinely does not have time to build and maintain a feature pipeline, or when a fast, defensible baseline is needed before committing to a supervised build.

TSFMs tend to **lose** to a well-built feature-based global model (LightGBM/XGBoost + MLForecast or skforecast) when: the series have long, clean history; promotions, pricing, and holiday calendars are known-future and exploitable; the business needs per-forecast explainability (SHAP, feature importance) for planning conversations; or per-forecast inference cost at high volume matters more than zero-shot convenience. In these conditions a tuned boosting model with good features still tends to out-earn a zero-shot TSFM on fev-bench-style covariate tasks — the "TSFM wins the covariate story" narrative is about beating other TSFMs on those tasks, not about beating a strong bespoke model.

A pragmatic default: run the TSFM zero-shot benchmark cheaply and early regardless of which side of that line you expect to land on. It costs little, sets a credible floor/ceiling, and prevents both "we didn't need six weeks of feature engineering" and "the LLM benchmark was rigged against our features" arguments later.

## Practical Model Roles

| Model Family | Best Role | Watchouts |
|-------------|-----------|-----------|
| Chronos-2 (Amazon, released Oct 2025) / Chronos-Bolt (Amazon, released Nov 2024) | Strong zero-shot baseline; Chronos-2 adds multivariate + covariate support and leads fev-bench (90.7% win rate); Chronos-Bolt is up to 250x faster and ~20x more memory-efficient than original Chronos, but is the older, univariate-only member of the family | Chronos-Bolt predates Chronos-2 by about a year — do not describe them as same-generation siblings. Verify covariate API and current model card at https://github.com/amazon-science/chronos-forecasting |
| Original Chronos family | Backward-compatible univariate zero-shot baseline | Prefer Chronos-2 or Chronos-Bolt for new projects; original maintained for compatibility |
| TimesFM 2.5 (Google, 200M params, released Sept 2025) | 200M-parameter zero-shot TSFM; 16,384-step context (up from 2.0's 2,048); point forecasts plus an optional ~30M-param quantile head giving continuous quantile forecasts up to a 1,000-step horizon. Briefly led GIFT-Eval on release. LoRA fine-tuning via HuggingFace PEFT is documented in the repo's finetuning examples. Repo: https://github.com/google-research/timesfm | Chronos-2 and Moirai 2.0 have since passed it on GIFT-Eval — verify the current leaderboard before calling it best-in-class. `ForecastConfig` defaults (e.g. `max_context=1024`, `max_horizon=256`) are configurable, not hard model limits — don't undersell the model's real 16K/1000 ceiling by quoting the default config values as capability limits |
| TimesFM 2.0 (Google, 500M params) | Larger predecessor checkpoint; 2,048-step context; covariate support via XReg | Superseded by 2.5 on both size and context for new projects; retained for compatibility or when its XReg covariate path is specifically needed |
| Toto / Toto 2.0 (Datadog, published to Hugging Face May 2026) | Observability-metric forecasting; multivariate zero-shot with quantile-based uncertainty; 4M-2.5B param family using u-µP scaling so hyperparameters tuned on the 4M model transfer to the 2.5B checkpoint; leads BOOM, GIFT-Eval, and the contamination-resistant TIME benchmark | Built and validated primarily on observability/metrics data; verify general-domain (retail, demand, finance) fit before treating GIFT-Eval rank as proof it wins your task. Repo: https://github.com/DataDog/toto |
| TiRex / TiRex-2 (NX-AI) | 35M-parameter xLSTM zero-shot forecaster; strong on GIFT-Eval; second-best pretrained model on fev-bench behind Chronos-2 (80.8% win rate / 42.6% skill score). TiRex-2 (2026) adds multivariate, covariate-aware, streaming forecasting from a single checkpoint | Much smaller than the Chronos/TimesFM/Toto families — a good low-cost zero-shot candidate to benchmark alongside them, not just a hedge entry. Repo: https://github.com/NX-AI/tirex |
| AutoGluon TimeSeries TSFM integrations | Rapid benchmark stack across local, global, and TSFM candidates | Good for comparison, but still validate deployment fit |

## Default Evaluation Flow

Always benchmark a TSFM against:

1. naive baseline
2. seasonal-naive baseline
3. strong feature-based global model if covariates exist

Minimum evaluation outputs:

- MAE / MASE / WAPE by horizon
- probabilistic score if intervals or samples are available
- slice analysis by series family, volume band, or geography
- latency and cost notes if the model is a production candidate

## Zero-Shot Benchmark Pattern

Use when:

- you need an answer quickly
- you are deciding whether additional modelling work is justified

Workflow:

1. prepare clean history windows with explicit cutoff timestamps
2. run seasonal-naive baseline
3. run TSFM zero-shot forecast
4. compare horizon-wise accuracy
5. decide whether to stop, tune, or escalate to supervised global forecasting

This is the default entry point for TSFMs.

## Covariate-Aware Pattern

Use when:

- official docs confirm the current model version supports covariates or known-future regressors
- promotions, holidays, or other future-known drivers matter

Rules:

- only pass covariates that are truly known at forecast time
- keep a pure zero-shot benchmark alongside the covariate-aware run
- document whether scenario inputs or deterministic future values were used

## Hybrid Pattern

Reasonable hybrid uses:

- TSFM as the initial benchmark, supervised global model as the production default
- ensemble or stacked comparison where a TSFM and feature-based model make complementary errors
- TSFM for cold-start benchmarking, feature-based model for tuned production rollout

Avoid vague "LLM adjustment" steps that have no validation design.

## Sampling And Scenario Use

Use stochastic trajectories only when they map to a real decision:

- demand risk planning
- inventory buffers
- scenario comparison

If the model produces samples:

- aggregate them into quantiles
- score them with CRPS or pinball loss when possible
- compare coverage and sharpness, not just the visual spread

## Anti-Patterns

| Anti-Pattern | Why It Fails | Fix |
|---|---|---|
| Treating TSFMs as automatic winners | Good zero-shot does not guarantee best deployed model | Benchmark against strong baselines |
| Using TSFM outputs without horizon-wise review | Long-horizon wins can hide near-term misses | Report by horizon |
| Passing unknown future covariates | Creates fake deployment assumptions | Use only known-future inputs or explicit scenarios |
| Using "LLM" language as a proxy for capability | The relevant question is forecasting behavior, not branding | Evaluate the actual TSFM interface and outputs |
| Copying stale capability tables | TSFM APIs change quickly | Verify current official docs before final recommendation |

## TSFM Checklist

- [ ] Seasonal-naive baseline included
- [ ] Zero-shot benchmark recorded
- [ ] Horizon-wise metrics reported
- [ ] Slice analysis included
- [ ] Covariate support verified against current docs if used
- [ ] Cost and latency noted if production is under consideration
- [ ] Probabilistic outputs scored if available
- [ ] Final recommendation compared against a feature-based global model

## Cross-References

- [model-selection-guide.md](model-selection-guide.md) - when to use TSFMs vs other families
- [backtesting-patterns.md](backtesting-patterns.md) - rolling-origin evaluation
- [probabilistic-forecasting.md](probabilistic-forecasting.md) - interval and sample evaluation
