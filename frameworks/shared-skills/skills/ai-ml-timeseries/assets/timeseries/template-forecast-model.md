# Forecast Model Template

Define forecasting model configuration and training logic.

---

## 1. Model Overview

model_type: "<sarima|prophet|xgboost|lightgbm|lstm|tft|nbeats>"
version: <vX.Y>
description: "<short text>"

---

## 2. Training Config

training:
target: "<column>"
features: "<list_of_features>"
train_start: "<date>"
train_end: "<date>"

---

## 3. Hyperparameters

params:
learning_rate: <value>
max_depth: <value>
num_leaves: <value>
seasonal_period: <value>

(Use appropriate params for model family.)

---

## 4. Validation Strategy

validation:
split_type: "temporal"
horizon_days: <H>
backtest_windows: <N>

---

## 5. Output

outputs:
model_artifact: "<path>"
metrics_report: "<path>"
feature_importance: true/false

---

## 6. Checklist

- [ ] Baseline compared  
- [ ] No leakage  
- [ ] Validation horizon correct  
- [ ] Metrics stable  
