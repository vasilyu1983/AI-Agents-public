# LLM-Based Forecasting & Generative TS Patterns

Operational patterns for using foundation models (Chronos-2, TimesFM 2.5, Lag-Llama) and generative TS systems.

**Modern Best Practices (January 2026)**:

- **Chronos-2** (Oct 2025): Universal forecasting with multivariate/covariate support — best accuracy on benchmarks
- **Chronos-Bolt** (Nov 2024): 250x faster inference, 20x memory efficient — production-ready univariate
- **TimesFM 2.5**: XReg covariate support for regression tasks
- Zero-shot foundation models often match or outperform trained-from-scratch Transformers

---

## Model Comparison (January 2026)

| Model | Multivariate | Covariates | Speed | Memory | Best For |
|-------|--------------|------------|-------|--------|----------|
| Chronos-2 | PASS | PASS | Medium | Medium | Best accuracy, universal forecasting |
| Chronos-Bolt | FAIL | FAIL | Fastest (250x) | Lowest (20x) | Production univariate, latency-critical |
| TimesFM 2.5 | PASS | PASS (XReg) | Fast | Medium | Google ecosystem, covariate-heavy |
| Lag-Llama | FAIL | FAIL | Medium | High | Open source, research |
| Time-MoE | PASS | PASS | Fast | Medium | Mixture-of-experts efficiency |

**Benchmark Performance (GIFT-Eval, Chronos Benchmark II)**:
- Chronos-2 > TimesFM-2.5 > TiRex on most benchmarks
- Zero-shot TSFMs often match trained Transformers with no tuning

---

## 1. When to Use TS-LLM

Use for:

- Long horizon forecasts  
- Multi-modal distributions  
- Simulation of scenarios  
- Extremely irregular or non-linear patterns  
- Zero or limited domain features  

---

## 2. Tokenization & Value Discretization

LLM TS models require discrete tokens.

### Options

- Quantize numeric values → buckets  
- Scale → round → tokenize  
- Diffusion-style embeddings  

**Checklist**

- [ ] Values discretized consistently  
- [ ] Resolution high enough for accuracy  
- [ ] No leakage from future values  

---

## 3. TS-LLM Inference Workflow

### Steps

1. Provide past N values  
2. Model auto-regressively generates next H tokens  
3. Convert tokens back to continuous values  
4. Optionally run multiple samples for probabilistic outputs  

---

## 4. Scenario Simulation Pattern

Use multiple model samples:

- 20–100 stochastic trajectories  
- Compute percentiles (P10/P50/P90)  
- Use for risk-aware planning  

---

## 5. Hybrid TS Pattern (Classical + TS-LLM)

Combine:

- Statistical + ML forecast  
- LLM for long-horizon adjustment  
- Weighted or rule-based fusion  

Example:
final_forecast = 0.7 *ml_model + 0.3* llm_model

---

## 6. Evaluation Pattern for TS-LLMs

Evaluate:

- MASE  
- Pinball loss  
- Horizon-by-horizon accuracy  
- Drift tolerance  
- Scenario coverage  

---

## 7. TS-LLM Checklist

- [ ] Discretization validated  
- [ ] Long horizon stable  
- [ ] No leakage  
- [ ] Backtested against baselines  
- [ ] Scenario coverage documented  
