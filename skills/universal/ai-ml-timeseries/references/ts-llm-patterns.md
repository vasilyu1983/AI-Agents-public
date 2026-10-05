# Time-Series Foundation Model Patterns

Operational patterns for using time-series foundation models (TSFMs).

Keep this file focused on **forecasting foundation models**, not generic LLM workflow advice.

## Table of Contents

- [Ground Rules](#ground-rules)
- [TSFM Trust Gate](#tsfm-trust-gate)
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

## Ground Rules

- TSFMs are credible **zero-shot or light-adaptation baselines**. The question is not "LLM or not?" but "does the TSFM beat seasonal-naive and a strong feature-based global model on this task, at this horizon?"
- Use a public benchmark with many tasks, covariate-inclusive tasks and confidence intervals (for example fev-bench or GIFT-Eval) in place of informal ablations when assessing a TSFM claim. The Chronos-2 paper (arXiv 2510.15821, 2025) reported the family leading fev-bench at publication; treat that as a dated citation, not a ranking.
- Leaderboards reshuffle with each release. Never present a "best TSFM" as durable: quote a rank only with the benchmark name and the snapshot date you read it on.

## TSFM Trust Gate

Pass all three before a zero-shot win changes a decision:

1. **Weight licence.** Read the licence on the exact checkpoint before benchmarking; some TSFM releases ship non-commercial weights, which rules them out for production regardless of accuracy.
2. **Contamination.** Public benchmark datasets may sit in the pretraining corpus. Validate on private data, or on data dated after the model's training cutoff, before trusting a zero-shot margin.
3. **Same backtest.** Score the TSFM in your own rolling-origin backtest, against seasonal-naive and a feature-based global model, by horizon; a leaderboard rank is not a backtest.

## Decision Branch: TSFM Approach Selection

Use this branch when a TSFM is under consideration:

```
Data has rich known-future covariates and enough history to fit a supervised model?
└── Feature-based supervised global model (e.g., LightGBM with MLForecast)
    Default supervised comparator; measure accuracy and inference cost against the TSFM

Data has many series, limited feature-engineering time?
├── Zero-shot TSFM → benchmark first (seasonal-naive is the floor)
│   ├── Latency / cost is the binding constraint → smallest checkpoint that clears the baseline
│   ├── Known-future or multivariate covariates → a model whose card documents covariate input
│   └── Domain-specific data (e.g. observability metrics) → a model pretrained on that domain, then check general-domain fit
│
└── Zero-shot TSFM falls short on your eval?
    ├── Fine-tune (e.g. LoRA) if the model card documents a fine-tuning path
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

### Judgment Call: Benchmark The Claimed Advantage

The [Chronos-2 paper](https://arxiv.org/html/2510.15821v1) reports its largest gains on covariate-informed tasks in its benchmark setup. That result does not establish where every TSFM wins, a minimum history threshold, or a universal advantage for tuned boosting. Compare a covariate-capable TSFM and a feature-based global model on the same origins, available covariates and tuning budget; measure inference cost on the target hardware. Cold-start performance and explanations needed by planners are separate acceptance criteria.

## Practical Model Roles

Choose a candidate by role, then look up which current checkpoints fill it. Do not copy a model-role table from a past snapshot.

| Criterion | What to check | Decision it feeds |
|-----------|---------------|-------------------|
| Univariate vs covariates | Model card: past, known-future and static covariate inputs; multivariate support | Whether the TSFM can use the drivers a feature model would exploit |
| Size and latency | Parameter count, inference time per series on your hardware | Batch vs online use; cost at your series count |
| Domain match | Pretraining data domains named in the paper or card | Trust in zero-shot on your domain (see the trust gate) |
| Weight licence | Licence on the exact checkpoint | Whether it can ship at all |
| Horizon and context | Maximum context and horizon the model supports (not the default config values) | Whether your horizon needs chunking or a different model |
| Uncertainty output | Quantiles, samples, or point only | Whether pinball/CRPS scoring and decision quantiles are possible |

**Lookup step:** for each shortlisted family, read the official model card or repository and a live snapshot of a multi-task leaderboard (fev-bench, GIFT-Eval). Record the snapshot date next to any rank you quote. Families commonly shortlisted include Chronos, TimesFM, Moirai, TiRex and Toto. AutoGluon TimeSeries wraps the Chronos family (original, Bolt, Chronos-2) in the same backtest as statistical and tree models; check the installed release's model list before assuming it covers other families.

Capability, licence and covariate support differ by generation within one family (for example, one Toto generation keeps fine-tuning and exogenous support that the next does not yet have). Record family, generation and exact checkpoint ID with every result, and never transfer a capability claim across generations.

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
| Copying stale capability tables | TSFM APIs and rankings change with each release | Look up the model card and a dated leaderboard snapshot |
| Trusting a zero-shot win on public data | The data may be in the pretraining set | Validate on private or post-cutoff data (trust gate) |

## TSFM Checklist

- [ ] Weight licence read for the exact checkpoint
- [ ] Zero-shot win confirmed on private or post-cutoff data
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
