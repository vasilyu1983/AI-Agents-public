# Time Series Anomaly Detection Patterns

> Operational guide for detecting anomalies in time series data. Covers point, contextual, and collective anomaly types. Methods span statistical baselines through deep learning. Focus on production alerting, threshold tuning, and false positive management.

**Freshness anchor:** January 2026 — scikit-learn 1.5+, PyOD 1.1+, STUMPY 1.13+, Prophet 1.1+

---

## Decision Tree: Choosing a Detection Method

```
START
│
├─ Anomaly type?
│   ├─ Point (single unexpected value)
│   │   ├─ Univariate?
│   │   │   ├─ YES → Z-score / IQR baseline, then Isolation Forest
│   │   │   └─ NO  → Isolation Forest or LOF on multivariate
│   │   └─ Stationary series?
│   │       ├─ YES → Statistical methods sufficient
│   │       └─ NO  → Decompose first (STL), detect on residuals
│   │
│   ├─ Contextual (normal value in wrong context)
│   │   └─ Time-of-day / seasonality matters?
│   │       ├─ YES → Prophet / STL decomposition → residual detection
│   │       └─ NO  → Rolling window z-score with adaptive threshold
│   │
│   └─ Collective (sequence of points form anomaly)
│       ├─ Known pattern length?
│       │   ├─ YES → Matrix Profile (STUMPY) with fixed window
│       │   └─ NO  → Autoencoder on sliding windows
│       └─ Subsequence anomaly?
│           └─ Matrix Profile → Discord discovery
│
├─ Labeled anomaly data available?
│   ├─ YES (>100 labeled anomalies) → Supervised (XGBoost on features)
│   ├─ PARTIAL (<100 labels) → Semi-supervised (tune threshold on labels)
│   └─ NO → Unsupervised (statistical or isolation-based)
│
└─ Latency requirement?
    ├─ Real-time (< 1 sec) → Z-score, EWM, simple thresholds
    ├─ Near real-time (< 1 min) → Isolation Forest, LOF (pre-trained)
    └─ Batch (hourly+) → Autoencoder, Matrix Profile, full pipeline
```

---

## Quick Reference: Methods Comparison

| Method | Type | Training | Latency | Handles Seasonality | Multivariate |
|--------|------|----------|---------|---------------------|--------------|
| Z-score | Statistical | None | < 1ms | No (needs detrend) | No |
| IQR | Statistical | None | < 1ms | No (needs detrend) | No |
| Grubbs test | Statistical | None | < 1ms | No | No |
| Rolling z-score | Statistical | None | < 5ms | Partial (via window) | No |
| STL + residual | Decomposition | Fit | ~100ms | Yes | No |
| Prophet residuals | Decomposition | Fit (slow) | ~500ms | Yes | No |
| Isolation Forest | ML | Fit | < 10ms | No (feature it) | Yes |
| LOF | ML | Fit | < 50ms | No (feature it) | Yes |
| One-Class SVM | ML | Fit | < 10ms | No | Yes |
| Matrix Profile | Pattern | Compute | ~1s/10k pts | Captures patterns | No (per series) |
| Autoencoder | Deep | Train | < 50ms | If trained with | Yes |
| VAE | Deep | Train | < 50ms | If trained with | Yes |

---

## Operational Patterns

### Pattern 1: Statistical Baseline (Start Here)

- **Use when:** First pass on any time series, establishing baseline
- **Implementation:**

```python
import numpy as np
import pandas as pd

def zscore_detector(series, window=168, threshold=3.0):
    """Rolling z-score anomaly detection.

    Args:
        series: pd.Series with datetime index
        window: rolling window size (168 = 1 week hourly)
        threshold: z-score threshold
    """
    rolling_mean = series.rolling(window=window, min_periods=window//2).mean()
    rolling_std = series.rolling(window=window, min_periods=window//2).std()
    zscore = (series - rolling_mean) / (rolling_std + 1e-8)
    anomalies = zscore.abs() > threshold
    return anomalies, zscore

def iqr_detector(series, window=168, k=1.5):
    """Rolling IQR anomaly detection."""
    q1 = series.rolling(window).quantile(0.25)
    q3 = series.rolling(window).quantile(0.75)
    iqr = q3 - q1
    lower = q1 - k * iqr
    upper = q3 + k * iqr
    anomalies = (series < lower) | (series > upper)
    return anomalies
```

- **Threshold tuning guide:**

| Z-score | Expected FP rate | Use case |
|---------|-----------------|----------|
| 2.0 | ~5% | Sensitive detection (medical) |
| 2.5 | ~1.2% | General monitoring |
| 3.0 | ~0.3% | Conservative (reduce alert fatigue) |
| 3.5 | ~0.05% | Very conservative (critical systems) |

### Pattern 2: STL Decomposition + Residual Detection

- **Use when:** Series has clear seasonality and trend
- **Implementation:**

```python
from statsmodels.tsa.seasonal import STL

def stl_anomaly_detector(series, period=24, threshold=3.0):
    """Decompose, then detect anomalies in residuals."""
    stl = STL(series, period=period, robust=True)
    result = stl.fit()

    residuals = result.resid
    resid_mean = residuals.mean()
    resid_std = residuals.std()

    zscore = (residuals - resid_mean) / (resid_std + 1e-8)
    anomalies = zscore.abs() > threshold

    return anomalies, result

# For multiple seasonality: use MSTL
from statsmodels.tsa.seasonal import MSTL
mstl = MSTL(series, periods=[24, 168])  # daily + weekly
```

- **Key rule:** Always use `robust=True` to prevent anomalies from distorting the decomposition

### Pattern 3: Isolation Forest for Multivariate

- **Use when:** Multiple correlated features, unknown anomaly structure
- **Implementation:**

```python
from sklearn.ensemble import IsolationForest

def build_features(df, target_col, lags=[1, 2, 3, 24], windows=[6, 24]):
    """Build time series features for anomaly detection."""
    features = pd.DataFrame(index=df.index)
    for lag in lags:
        features[f'lag_{lag}'] = df[target_col].shift(lag)
    for w in windows:
        features[f'rolling_mean_{w}'] = df[target_col].rolling(w).mean()
        features[f'rolling_std_{w}'] = df[target_col].rolling(w).std()
    features['hour'] = df.index.hour
    features['dayofweek'] = df.index.dayofweek
    return features.dropna()

features = build_features(df, 'value')

iforest = IsolationForest(
    n_estimators=300,
    contamination=0.01,    # expected anomaly rate
    max_samples='auto',
    random_state=42,
    n_jobs=-1,
)
iforest.fit(features)

scores = iforest.decision_function(features)  # lower = more anomalous
anomalies = iforest.predict(features) == -1
```

- **Contamination tuning:** Start at 0.01 (1%), adjust based on domain knowledge
- **Feature engineering is critical** — raw values alone are insufficient

### Pattern 4: Matrix Profile for Subsequence Anomalies

- **Use when:** Looking for unusual patterns (not just unusual values)
- **Implementation:**

```python
import stumpy

# Compute matrix profile
window_size = 24  # pattern length to search for
mp = stumpy.stump(series.values, m=window_size)

# Discord (most unusual subsequence)
discord_idx = mp[:, 0].argmax()
discord_distance = mp[discord_idx, 0]

# Top-k anomalous subsequences
k = 10
top_k_idx = np.argsort(mp[:, 0])[-k:][::-1]

# Threshold: discords with distance > mean + 3*std of all distances
threshold = mp[:, 0].mean() + 3 * mp[:, 0].std()
anomalous_subsequences = np.where(mp[:, 0] > threshold)[0]
```

- **Window size selection:**
  - Known period (e.g., daily cycle = 24 hourly points) → use period
  - Unknown → try multiple window sizes, look for consistent discords

### Pattern 5: Autoencoder for Complex Patterns

- **Use when:** High-dimensional, non-linear patterns, sufficient training data
- **Implementation:**

```python
import torch
import torch.nn as nn

class TSAutoencoder(nn.Module):
    def __init__(self, input_dim, latent_dim=16):
        super().__init__()
        self.encoder = nn.Sequential(
            nn.Linear(input_dim, 64), nn.ReLU(),
            nn.Linear(64, 32), nn.ReLU(),
            nn.Linear(32, latent_dim),
        )
        self.decoder = nn.Sequential(
            nn.Linear(latent_dim, 32), nn.ReLU(),
            nn.Linear(32, 64), nn.ReLU(),
            nn.Linear(64, input_dim),
        )

    def forward(self, x):
        z = self.encoder(x)
        return self.decoder(z)

# Train on normal data only
# Anomaly = high reconstruction error
recon = model(X_test)
errors = ((X_test - recon) ** 2).mean(dim=1)
threshold = errors.quantile(0.99)  # calibrate on validation set
anomalies = errors > threshold
```

- **Training rule:** Train ONLY on clean/normal data — if anomalies are in training set, autoencoder learns to reconstruct them

---

## Production Alerting Configuration

### Alert Fatigue Management

| Strategy | Implementation | Impact |
|----------|---------------|--------|
| Cooldown window | Suppress alerts within N minutes of last alert | Reduces burst noise |
| Severity tiers | threshold=3 (warn), threshold=4 (critical) | Prioritizes response |
| Minimum duration | Require N consecutive anomalous points | Filters transient spikes |
| Business hours filter | Suppress low-severity during off-hours | Reduces fatigue |
| Rolling false positive rate | Track FP rate per detector, disable if >50% | Self-correcting |

### Threshold Calibration Workflow

```
1. Deploy detector with logging only (no alerts) — 2 weeks
2. Review flagged anomalies with domain expert
3. Calculate precision at current threshold
4. Adjust threshold to target precision > 70%
5. Enable alerts, track weekly precision
6. Re-calibrate monthly or after distribution shifts
```

---

## Anti-Patterns

| Anti-Pattern | Why It Fails | Fix |
|---|---|---|
| Fixed threshold on non-stationary series | Drift makes threshold meaningless over time | Use rolling/adaptive thresholds |
| Z-score on seasonal data without decomposition | Normal seasonal peaks flagged as anomalies | Decompose first (STL), detect on residuals |
| Training autoencoder on data with anomalies | Model learns to reconstruct anomalies | Filter training data or use robust training |
| Single-point alerts without cooldown | Alert storm from one event | Add cooldown window (15–60 min) |
| Using contamination=0.05 as default | Too many false positives | Start at 0.01, calibrate with labels |
| Matrix profile without window size analysis | Wrong window misses or mischaracterizes anomalies | Test multiple window sizes |
| Ignoring concept drift | Detector degrades as normal behavior changes | Retrain detectors monthly or on drift signal |
| Alerting on raw anomaly score | Scores aren't interpretable across methods | Convert to severity levels with calibrated thresholds |
| Only using one detection method | Each has blind spots | Ensemble 2–3 methods, alert on agreement |
| No feedback loop from operators | Can't improve without ground truth | Log operator dismiss/confirm actions |

---

## Validation Checklist

- [ ] Statistical baseline (z-score/IQR) established first
- [ ] Seasonality handled (decomposition or feature engineering)
- [ ] Contamination rate estimated from domain knowledge
- [ ] Threshold calibrated on labeled validation data (if available)
- [ ] Alert cooldown and severity tiers configured
- [ ] False positive rate tracked in production
- [ ] Detector retrained on schedule (monthly minimum)
- [ ] Feedback loop from operators to anomaly labels
- [ ] Multiple detection methods compared before production
- [ ] Edge cases tested: missing data, zero-variance periods, holidays

---

## Cross-References

- `ai-ml-timeseries/references/probabilistic-forecasting.md` — prediction intervals as anomaly bounds
- `ai-ml-timeseries/references/hierarchical-forecasting.md` — detecting anomalies across hierarchy levels
- `ai-mlops/references/automated-retraining-patterns.md` — drift detection triggering retraining
- `ai-mlops/references/experiment-tracking-patterns.md` — logging detector performance metrics
