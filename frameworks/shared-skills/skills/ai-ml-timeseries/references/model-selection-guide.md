# Model Selection Guide for Forecasting

Operational decision rules for selecting forecasting models based on data patterns and constraints.

---

## 1. First Principles

### Always

- Start with baseline forecasts  
- Document naive performance  
- Choose model by data behavior, not hype  

---

## 2. Baseline Models (Required)

- Naive (y[t] = y[t-1])  
- Seasonal naive (y[t] = y[t-7])  
- Moving average  

**Checklist**

- [ ] Baseline implemented  
- [ ] Candidate model must outperform baseline  

---

## 3. Model Family Decision Rules

### A. Classical Statistical Models

Use when:

- Strong linear trend  
- Regular seasonality  
- Few covariates  
- Daily/hourly data  

Models:

- ARIMA / SARIMA  
- ETS  
- TBATS  
- Prophet  

---

### B. Machine Learning Models

Use when:

- Many covariates  
- Complex interactions  
- Intermittent demand  
- Non-linear patterns  

Models:

- XGBoost  
- LightGBM  
- Random Forest  
- Gradient-boosted trees  

---

### C. Deep Learning Models

Use when:

- Large dataset  
- Multiple related series  
- Long horizon forecasting  
- Complex sequences  

Models:

- LSTM / GRU  
- DeepAR  
- N-BEATS  
- Temporal Fusion Transformer (TFT)  

---

### D. Generative Models (LLM-based TS)

Use when:

- Need scenario simulation  
- Multi-modal distributions  
- Irregular patterns  
- Very long horizons  

Models:

- Chronos  
- Time-LLM  
- Diffusion-based TS models  

---

## 4. Model Constraints

### Consider

- Training time  
- Inference latency  
- Explainability requirements  
- Hardware constraints  
- Availability of covariates  

---

## 5. Model Selection Checklist

- [ ] Baseline compared  
- [ ] Model matched to data patterns  
- [ ] Hardware constraints respected  
- [ ] Horizon requirements satisfied  
- [ ] Evaluation metrics defined ahead of time  
