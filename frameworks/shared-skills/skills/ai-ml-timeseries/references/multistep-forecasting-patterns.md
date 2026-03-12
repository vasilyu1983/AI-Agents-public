# Multi-Step Forecasting Patterns

Operational patterns for forecasting multiple time steps ahead.

---

## Overview

Multi-step forecasting predicts multiple future time points. Three main strategies exist:

1. **Direct Strategy** - Train separate models for each horizon
2. **Recursive Strategy** - Predict one step, feed back as input
3. **Sequence-to-Sequence** - Generate entire horizon at once

---

## Pattern 1: Direct Strategy

### When to Use
- Short horizons (1-7 steps)
- Need independent predictions per horizon
- Have sufficient data per horizon

### Implementation

Train one model per horizon step:

```python
# Example: Direct strategy for 7-day forecast
models = {}
for h in range(1, 8):
    X_train = create_features(df, lag_window=28)
    y_train = df['target'].shift(-h)  # Target at h steps ahead

    models[h] = LGBMRegressor().fit(X_train, y_train)
```

### Pros
- No error propagation
- Different features per horizon
- Easier to interpret

### Cons
- Multiple models to maintain
- More training time
- Features must be aligned carefully

---

## Pattern 2: Recursive Strategy

### When to Use
- Medium horizons (1-30 steps)
- Sequential dependencies matter
- Prefer single model simplicity

### Implementation

```python
# Recursive forecasting
model = LGBMRegressor().fit(X_train, y_train)

predictions = []
current_features = X_test[0].copy()

for h in range(1, forecast_horizon + 1):
    pred = model.predict([current_features])[0]
    predictions.append(pred)

    # Update features with prediction
    current_features = update_features(current_features, pred)
```

### Pros
- Single model
- Captures sequential dependencies
- Memory efficient

### Cons
- Error compounds over horizon
- Slower inference (sequential)
- Harder to parallelize

---

## Pattern 3: Sequence-to-Sequence (Deep Learning)

### When to Use
- Long horizons (30-180 steps)
- Complex temporal patterns
- Have sufficient data for DL

### Frameworks
- **Transformers**: TimesFM, Chronos (for long dependencies)
- **RNNs/LSTMs**: Good for sequential data
- **TFT**: Temporal Fusion Transformers
- **N-BEATS**: Neural Basis Expansion
- **DeepAR**: Probabilistic forecasting

### Implementation Example

```python
from pytorch_forecasting import TemporalFusionTransformer

model = TemporalFusionTransformer(
    max_prediction_length=30,  # Forecast horizon
    max_encoder_length=60,     # Historical window
    # ... other config
)

predictions = model.predict(data)  # Full horizon at once
```

### Pros
- Outputs full horizon
- Captures complex patterns
- Probabilistic forecasts

### Cons
- Needs more data
- Harder to debug
- Computationally expensive

---

## Choosing the Right Strategy

| Horizon Length | Best Strategy | Reasoning |
|----------------|---------------|-----------|
| 1-7 steps | Direct or Recursive | Simple, fast, accurate |
| 7-30 steps | Recursive or Seq2Seq | Balance complexity/performance |
| 30-180 steps | Seq2Seq (Transformers, N-BEATS) | Handles long dependencies |
| 180+ steps | Prophet, TBATS, Seq2Seq | Seasonal decomposition helps |

### Additional Considerations

**Data characteristics:**
- High noise → Direct (less error propagation)
- Strong autocorrelation → Recursive or Seq2Seq
- Multiple seasonalities → Seq2Seq or Prophet

**Computational constraints:**
- Limited resources → Direct or Recursive
- Need real-time predictions → Direct (parallelizable)
- Batch predictions → Any strategy

**Explainability:**
- Need interpretability → Direct with LightGBM
- Black box acceptable → Seq2Seq deep learning

---

## Hybrid Approaches

### Direct-Recursive Hybrid

```python
# Use direct for near-term (1-7), recursive for long-term
short_term_models = {h: train_direct_model(h) for h in range(1, 8)}
long_term_model = train_recursive_model()

# Combine predictions
predictions = []
predictions.extend([short_term_models[h].predict(X) for h in range(1, 8)])
predictions.extend(recursive_forecast(long_term_model, X, horizon=23))
```

### Ensemble Approach

```python
# Combine multiple strategies
direct_preds = direct_forecast(X, horizon)
recursive_preds = recursive_forecast(X, horizon)
seq2seq_preds = seq2seq_forecast(X, horizon)

# Weighted average
final_preds = 0.4 * direct_preds + 0.3 * recursive_preds + 0.3 * seq2seq_preds
```

---

## Error Analysis by Strategy

### Horizon-Specific Metrics

Track performance at each forecast step:

```python
# Evaluate each horizon separately
for h in range(1, horizon + 1):
    y_true_h = actuals[:, h-1]
    y_pred_h = predictions[:, h-1]

    mae_h = mean_absolute_error(y_true_h, y_pred_h)
    print(f"Horizon {h}: MAE = {mae_h:.2f}")
```

### Error Propagation Monitoring

For recursive strategy, monitor cumulative error:

```python
# Track error growth over horizon
errors = []
for h in range(1, horizon + 1):
    error_h = np.abs(actuals[:, h-1] - predictions[:, h-1]).mean()
    errors.append(error_h)

# Plot error growth
plt.plot(range(1, horizon + 1), errors)
plt.xlabel("Forecast Horizon")
plt.ylabel("MAE")
plt.title("Error Propagation Over Horizon")
```

---

## Checklist: Multi-Step Strategy Implementation

### Planning
- [ ] Forecast horizon defined (H-step)
- [ ] Strategy chosen based on horizon length
- [ ] Data characteristics analyzed
- [ ] Computational constraints documented

### Direct Strategy
- [ ] Separate models trained for each horizon
- [ ] Features aligned correctly for each target
- [ ] Models saved with horizon identifier
- [ ] Parallel prediction implemented

### Recursive Strategy
- [ ] Feature update logic implemented
- [ ] Error propagation monitored
- [ ] Stopping criteria defined
- [ ] Fallback for divergence cases

### Seq2Seq Strategy
- [ ] Encoder/decoder architecture chosen
- [ ] Historical window size optimized
- [ ] Attention mechanisms configured
- [ ] Probabilistic outputs enabled (if needed)

### Evaluation
- [ ] Horizon-wise metrics computed
- [ ] Error growth analyzed
- [ ] Baseline comparison done
- [ ] Segment-level performance checked

---

## References

See also:
- [Backtesting Patterns](backtesting-patterns.md) - Temporal validation strategies
- [Model Selection Guide](model-selection-guide.md) - Choosing forecasting models
- [TS-LLM Patterns](ts-llm-patterns.md) - Deep learning approaches
