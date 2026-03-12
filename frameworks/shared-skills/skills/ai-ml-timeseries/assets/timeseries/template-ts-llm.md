# TS-LLM Template (Chronos, Time-LLM, Generative TS)

A template for building LLM-based forecasting pipelines.

---

## 1. Tokenization / Discretization

discretization:
method: "quantize" # quantize | bucketize | round
num_bins: 500
normalize: true

---

## 2. Input Structure

inputs:
past_values: <list>
exogenous_features: <optional>
context_length: 128

---

## 3. Generation Settings

generation:
max_horizon: <N>
num_samples: 20
temperature: 0.8
top_p: 0.9

---

## 4. Output Reconstruction

reconstruction:
method: "dequantize"

---

## 5. Scenario Simulation

Calculate P10/P50/P90:

quantiles: [0.1, 0.5, 0.9]

---

## 6. Checklist

- [ ] Values discretized  
- [ ] No leakage  
- [ ] Multiple trajectories aggregated  
- [ ] Evaluated vs baseline  
