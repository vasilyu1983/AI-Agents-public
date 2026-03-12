# LightGBM for Time Series Forecasting - Best Practices

Operational patterns for using LightGBM in time series forecasting (2024-2025 best practices).

---

## Why LightGBM for Time Series

**Key Advantages:**
- Majority of M5 Competition winners used LightGBM
- Handles missing data well
- Fast training and prediction speed
- Works efficiently with large datasets
- Supports custom loss functions
- Competes with and outperforms XGBoost, AdaBoost, CatBoost

**When to Use LightGBM:**
- Lots of data available (high frequency, decent volume)
- Want to include many external features (weather, holidays, events)
- Need fast training and prediction
- Require computational efficiency
- Have strong seasonality patterns
- Multiple covariates involved

---

## Critical Limitation

**LightGBM doesn't natively understand time** - you must manually create time-based features to teach it temporal awareness.

---

## Essential Feature Engineering

### 1. Lag Features

Represent past values of the series:

```python
# Daily data
df['lag_1'] = df['target'].shift(1)
df['lag_7'] = df['target'].shift(7)
df['lag_28'] = df['target'].shift(28)

# Hourly data
df['lag_24'] = df['target'].shift(24)
df['lag_48'] = df['target'].shift(48)
```

### 2. Rolling Statistics

Moving averages and windows:

```python
# Rolling means
df['rolling_mean_7'] = df['target'].rolling(window=7).mean()
df['rolling_mean_30'] = df['target'].rolling(window=30).mean()

# Rolling std
df['rolling_std_7'] = df['target'].rolling(window=7).std()

# Exponentially weighted means
df['ewm_7'] = df['target'].ewm(span=7).mean()
```

### 3. Prophet-Derived Features

Extract features from Prophet model:

```python
# Train Prophet model
prophet_model.fit(train_data)

# Extract features
predictions = prophet_model.predict(df)
df['prophet_pred'] = predictions['yhat']
df['prophet_lower'] = predictions['yhat_lower']
df['prophet_upper'] = predictions['yhat_upper']
df['prophet_daily_seasonality'] = predictions['daily']
df['prophet_weekly_seasonality'] = predictions['weekly']
df['prophet_trend'] = predictions['trend']
```

### 4. Calendar Features

```python
df['dayofweek'] = df['date'].dt.dayofweek
df['day'] = df['date'].dt.day
df['month'] = df['date'].dt.month
df['quarter'] = df['date'].dt.quarter
df['year'] = df['date'].dt.year
df['weekofyear'] = df['date'].dt.weekofyear

# Cyclical encoding
df['month_sin'] = np.sin(2 * np.pi * df['month']/12)
df['month_cos'] = np.cos(2 * np.pi * df['month']/12)
```

### 5. External Variables

Weather data can improve performance by 42% (MAE reduction):

```python
# Weather features
df['temperature']
df['precipitation']
df['wind_speed']

# Holiday indicators
df['is_holiday']
df['is_weekend']

# Event flags
df['black_friday']
df['end_of_quarter']
```

---

## Hyperparameter Optimization

### Approach

Use **Grid Search + Repeated K-Fold Cross Validation** with manual tuning.

### Key Parameters

```python
params = {
    'objective': 'regression',
    'metric': 'mae',  # or 'rmse'
    'boosting_type': 'gbdt',
    'num_leaves': 31,
    'learning_rate': 0.05,
    'feature_fraction': 0.9,
    'bagging_fraction': 0.8,
    'bagging_freq': 5,
    'verbose': 0
}
```

### Grid Search Example

```python
from sklearn.model_selection import GridSearchCV
import lightgbm as lgb

param_grid = {
    'num_leaves': [15, 31, 63],
    'learning_rate': [0.01, 0.05, 0.1],
    'n_estimators': [100, 500, 1000],
    'max_depth': [-1, 5, 10]
}

model = lgb.LGBMRegressor()
grid_search = GridSearchCV(
    estimator=model,
    param_grid=param_grid,
    cv=5,
    scoring='neg_mean_absolute_error',
    n_jobs=-1
)
```

---

## Multi-Step Forecasting Strategy

### Challenge

LightGBM does not support multi-output models - you need to predict one step at a time.

### Solutions

**1. Direct Strategy:**
Train one model per horizon step:

```python
# Train model for h=1
model_h1.fit(X_train, y_train_h1)

# Train model for h=7
model_h7.fit(X_train, y_train_h7)

# Each model predicts its specific horizon
```

**2. Recursive Strategy:**
Predict one step, feed it back, predict next step:

```python
predictions = []
for h in range(1, horizon+1):
    pred = model.predict(X_current)
    predictions.append(pred)
    # Update features with new prediction
    X_current = update_features(X_current, pred)
```

---

## Handling Seasonality

### Short-Term Seasonality

LightGBM handles well with lag features (daily, weekly).

### Long-Term Seasonality

Does not handle as well as traditional models (SARIMA, Prophet).

**Solution:** Combine approaches:
- Use Prophet for trend and long-term seasonality
- Use LightGBM to model residuals and short-term patterns

---

## Production Best Practices

### 1. Feature Consistency

Ensure training and serving use identical feature engineering:

```python
class FeatureEngineer:
    def fit(self, train_data):
        # Store parameters for transform
        self.rolling_params = {...}
        return self

    def transform(self, data):
        # Apply same transformations
        return engineered_data

# Use in both training and serving
engineer.fit(train_data)
train_features = engineer.transform(train_data)
serve_features = engineer.transform(new_data)
```

### 2. Avoid Data Leakage

```python
# WRONG - uses future data
df['rolling_mean'] = df['target'].rolling(window=7).mean()

# CORRECT - only uses past data
df['rolling_mean'] = df['target'].shift(1).rolling(window=7).mean()
```

### 3. Temporal Cross-Validation

```python
from sklearn.model_selection import TimeSeriesSplit

tscv = TimeSeriesSplit(n_splits=5)
for train_index, test_index in tscv.split(X):
    X_train, X_test = X[train_index], X[test_index]
    y_train, y_test = y[train_index], y[test_index]
    # Train and evaluate
```

---

## Hybrid Approaches (2024-2025)

### LazyProphet Pattern

Combines Prophet feature extraction with LightGBM modeling:

**Steps:**
1. Train Prophet model
2. Extract Prophet features (trend, seasonality, predictions)
3. Add Prophet features to LightGBM feature set
4. Train LightGBM on combined features

**Benefits:**
- Prophet captures long-term patterns
- LightGBM captures complex interactions
- Often outperforms either model alone

---

## Evaluation Checklist

- [ ] Temporal split (no random shuffle)
- [ ] No data leakage in features
- [ ] Rolling window validation performed
- [ ] Baseline comparison (naive, seasonal naive)
- [ ] Metrics: MAE, RMSE, MAPE, MASE
- [ ] Horizon-wise error analysis
- [ ] External variable impact measured
- [ ] Feature importance reviewed
- [ ] Model explainability documented

---

## Common Pitfalls

### 1. Forgetting Time Direction

Features must only use past data:

```python
# WRONG
df['future_mean'] = df['target'].rolling(window=7, center=True).mean()

# CORRECT
df['lag_mean'] = df['target'].shift(1).rolling(window=7).mean()
```

### 2. Not Encoding Cyclical Features

Month, day of week should be cyclical:

```python
# BETTER than raw month=1,2,3...12
df['month_sin'] = np.sin(2 * np.pi * df['month']/12)
df['month_cos'] = np.cos(2 * np.pi * df['month']/12)
```

### 3. Ignoring Feature Scaling

While LightGBM doesn't require scaling, some external features benefit:

```python
from sklearn.preprocessing import StandardScaler

# Scale weather features
scaler = StandardScaler()
df[['temp', 'humidity', 'pressure']] = scaler.fit_transform(
    df[['temp', 'humidity', 'pressure']]
)
```

---

## Performance Benchmarks (2024)

**M5 Competition Results:**
- Majority of winners used LightGBM
- Typical MAE improvement: 15-30% over baselines
- With weather data: 42% MAE reduction

**Computational Efficiency:**
- 2-5x faster than XGBoost
- Scales well to millions of rows
- Memory efficient

---

## References

- [M5 Competition Winners](https://phdinds-aim.github.io/time_series_handbook/08_WinningestMethods/lightgbm_m5_forecasting.html)
- [LightGBM Time Series Guide](https://cienciadedatos.net/documentos/py58-forecasting-time-series-with-lightgbm.html)
- [LazyProphet Approach](https://towardsdatascience.com/lazyprophet-time-series-forecasting-with-lightgbm-3745bafe5ce5)
