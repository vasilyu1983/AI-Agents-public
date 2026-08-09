# Fine-Tuning ROI Calculator

**Purpose**: Determine whether fine-tuning investment is justified for your use case.

---

## ROI Framework

### Core Formula

```
Net ROI = (Annual Benefits - Total Investment) / Total Investment × 100

Where:
- Annual Benefits = Cost Savings + Quality Value Improvement
- Total Investment = Data + Compute + Engineering + Maintenance
```

---

## 1. Current State Assessment

### Baseline Metrics

| Metric | Current Value | Measurement Method |
|--------|---------------|-------------------|
| Requests per month | ___ | Logs/monitoring |
| Cost per request | $___ | Token tracking |
| Monthly LLM spend | $___ | Billing |
| Quality score (0-100) | ___ | Eval suite |
| Latency p95 | ___ms | Monitoring |
| Prompt length (tokens) | ___ | Token counting |

### Baseline Calculations

```
Annual LLM Cost = Monthly Spend × 12 = $_______

Quality Gap = Target Quality - Current Quality = ____%
```

---

## 2. Fine-Tuning Investment Estimate

### One-Time Costs

| Component | Low Estimate | High Estimate | Your Estimate |
|-----------|-------------|---------------|---------------|
| **Data preparation** | | | |
| - Collection/generation | $2,000 | $20,000 | $_____ |
| - Labeling/annotation | $1,000 | $30,000 | $_____ |
| - Cleaning/validation | $500 | $5,000 | $_____ |
| **Compute (training)** | | | |
| - PEFT/LoRA training | $100 | $1,000 | $_____ |
| - Full fine-tuning | $500 | $10,000 | $_____ |
| **Evaluation** | | | |
| - Golden set creation | $500 | $5,000 | $_____ |
| - Human evaluation | $1,000 | $10,000 | $_____ |
| - A/B test infrastructure | $500 | $5,000 | $_____ |
| **Engineering time** | | | |
| - Integration (2-4 weeks) | $5,000 | $20,000 | $_____ |
| - Testing (1-2 weeks) | $2,500 | $10,000 | $_____ |
| **Subtotal one-time** | $12,100 | $116,000 | $_____ |

### Ongoing Costs (Annual)

| Component | Low Estimate | High Estimate | Your Estimate |
|-----------|-------------|---------------|---------------|
| Drift monitoring | $2,000 | $10,000 | $_____ |
| Periodic retraining | $5,000 | $30,000 | $_____ |
| Evaluation suite maintenance | $1,000 | $5,000 | $_____ |
| **Subtotal annual** | $8,000 | $45,000 | $_____ |

### Total Investment

```
Year 1 Total = One-Time + Annual = $_______
Year 2+ Total = Annual Only = $_______
```

---

## 3. Expected Benefits

### Cost Reduction Benefits

| Improvement | Mechanism | Estimated Savings |
|-------------|-----------|-------------------|
| Shorter prompts | Remove examples from prompt | 20-40% input tokens |
| Smaller model possible | Quality maintained with cheaper model | 50-80% per token |
| Reduced retries | Higher first-pass success | 10-30% fewer requests |
| Lower latency | Shorter prompts, simpler processing | Indirect cost savings |

### Calculate Annual Cost Savings

```
Current Annual Cost: $_______

After Fine-Tuning:
- Token reduction: ____% → New input cost: $_______
- Model tier change: From $___/1M to $___/1M
- Retry reduction: ____% → Request reduction: ____

New Annual Cost: $_______

Annual Cost Savings: Current - New = $_______
```

### Quality Improvement Value

| Quality Improvement | Business Impact | Estimated Value |
|--------------------|-----------------|-----------------|
| Higher accuracy (+5%) | Fewer escalations | $___/year |
| Better consistency | Brand/UX improvement | $___/year |
| Faster responses | User satisfaction | $___/year |
| Specialized behavior | Competitive advantage | $___/year |
| **Total Quality Value** | | $___/year |

---

## 4. ROI Calculation

### Summary Table

| Item | Year 1 | Year 2 | Year 3 |
|------|--------|--------|--------|
| **Benefits** | | | |
| Cost savings | $_____ | $_____ | $_____ |
| Quality value | $_____ | $_____ | $_____ |
| Total benefits | $_____ | $_____ | $_____ |
| **Investment** | | | |
| One-time costs | $_____ | $0 | $0 |
| Ongoing costs | $_____ | $_____ | $_____ |
| Total investment | $_____ | $_____ | $_____ |
| **Net benefit** | $_____ | $_____ | $_____ |

### ROI Metrics

```
Break-Even Point = One-Time Investment / Monthly Net Benefit = ___ months

Year 1 ROI = (Year 1 Benefits - Year 1 Investment) / Year 1 Investment = ____%

3-Year ROI = (3-Year Benefits - 3-Year Investment) / 3-Year Investment = ____%

NPV (10% discount) = Σ (Annual Net Benefit / (1.10)^n) - Initial Investment = $_______
```

---

## 5. Decision Framework

### Go / No-Go Criteria

| Criterion | Threshold | Your Value | Pass? |
|-----------|-----------|------------|-------|
| Break-even period | <12 months | ___ months | ☐ |
| Year 1 ROI | >25% | ___% | ☐ |
| 3-Year ROI | >100% | ___% | ☐ |
| Available training data | >1,000 examples | ___ examples | ☐ |
| Domain stability | >6 months unchanged | ___ months | ☐ |
| Request volume | >10k/month | ___/month | ☐ |

### Decision Tree

```
Have >1,000 quality examples?
├─ No → Use prompt engineering (collect data first)
│
└─ Yes → Request volume >10k/month?
    ├─ No → Calculate: Is quality improvement worth $15-50k?
    │   ├─ Yes → Fine-tune (quality-driven)
    │   └─ No → Use prompt engineering
    │
    └─ Yes → Break-even <12 months?
        ├─ Yes → PASS Fine-tune (cost-driven)
        └─ No → Is quality improvement critical?
            ├─ Yes → Fine-tune (quality-driven)
            └─ No → Use prompt engineering + optimize
```

---

## 6. Risk Assessment

### Risk Factors

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Training data insufficient | Medium | High | Start with prompt engineering, collect data |
| Quality regression | Medium | High | Maintain eval suite, A/B test |
| Domain drift | Low-Medium | Medium | Monitor performance, retrain schedule |
| Model deprecation | Low | High | Portable adapter approach |
| Overfitting | Medium | Medium | Validation set, regularization |

### Risk-Adjusted ROI

```
Risk Factor = Σ(Probability × Impact) = ____

Risk-Adjusted ROI = Base ROI × (1 - Risk Factor) = ____%
```

---

## 7. Recommendation Template

### Executive Summary

**Recommendation**: [ ] Proceed with Fine-Tuning [ ] Defer [ ] Alternative Approach

**Rationale**:
1. ____________________
2. ____________________
3. ____________________

**Key Metrics**:
- Expected break-even: ___ months
- Year 1 ROI: ___%
- 3-Year NPV: $______

**Risks and Mitigations**:
- Risk 1: ____________________
- Mitigation: ____________________

**Next Steps**:
1. ____________________
2. ____________________
3. ____________________

---

## Example Calculation

### Scenario: Customer Support Chatbot

**Current State**:
- 50,000 requests/month
- $0.05/request (Claude Sonnet with long prompts)
- 82% quality score (target: 90%)
- Annual cost: $30,000

**Fine-Tuning Investment**:
- Data preparation: $15,000
- Training (PEFT): $500
- Evaluation: $5,000
- Engineering: $10,000
- **Total one-time**: $30,500
- **Annual maintenance**: $12,000

**Expected Benefits**:
- Shorter prompts (40% reduction): $12,000/year savings
- Smaller model possible: $0.02/request → $6,000/year savings
- Total cost savings: $18,000/year
- Quality improvement (82%→90%): Worth $25,000/year (fewer escalations)
- **Total annual benefits**: $43,000

**ROI Calculation**:
- Year 1 net: $43,000 - $42,500 = $500 (break-even)
- Year 2 net: $43,000 - $12,000 = $31,000
- 3-Year ROI: ($97,500 - $66,500) / $66,500 = 47%

**Decision**: Proceed - modest Year 1, strong Years 2-3

---

## Related Resources

- **[Cost Economics](../../references/cost-economics.md)** - Cost modeling fundamentals
- **[Fine-Tuning Recipes](../../references/fine-tuning-recipes.md)** - Implementation patterns
- **[Model Selection Matrix](model-selection-matrix.md)** - Model comparison
- **[Decision Matrices](../../references/decision-matrices.md)** - Technology selection

---
