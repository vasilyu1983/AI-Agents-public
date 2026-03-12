# Multi-Step Forecasting Strategy Template

Define how to generate forecasts across multiple future steps.

---

## 1. Strategy Type

Choose one:

strategy: "<direct|recursive|seq2seq>"

---

## 2. Configurations

### Direct

direct:
horizons:

- 1
- 7
- 28

### Recursive

recursive:
max_horizon: <value>
refit: false

### Seq2Seq (NN)

seq2seq:
encoder_length: <value>
decoder_length: <value>

---

## 3. Checklist

- [ ] Strategy aligned with horizon length  
- [ ] Error propagation checked  
- [ ] Covariates aligned with forecast range  
