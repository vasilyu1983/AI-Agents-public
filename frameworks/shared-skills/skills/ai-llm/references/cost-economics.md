# LLM Cost Economics & Decision Frameworks

Production cost modeling, unit economics, and decision frameworks for LLM systems.

---

## Modern Best Practices (2026)

**Cost optimization is now table stakes**:
- Usage-based inference (tokens/requests) is often the largest variable cost driver
- Model selection directly impacts unit economics
- Cost-quality tradeoffs determine product viability

**Key Insight**: Measure cost per successful outcome, not cost per token

**Authoritative Sources**:
- [Anthropic Prompt Caching](https://docs.anthropic.com/en/docs/build-with-claude/prompt-caching) - Provider-specific caching semantics and discounts
- [OpenAI Pricing](https://openai.com/api/pricing/) - Current model pricing
- [a16z: Emerging Architectures for LLM Applications](https://a16z.com/emerging-architectures-for-llm-applications/) - TCO and architecture patterns

---

## Cost Model Fundamentals

### Unit Economics Formula

```
Cost per Request = (Input Tokens × Input Price) + (Output Tokens × Output Price)

Cost per Successful Outcome = Total LLM Spend / Successful Completions

Gross Margin = (Revenue per Request - Cost per Request) / Revenue per Request
```

### Pricing Snapshot Policy (Always Verify)

Avoid hard-coding prices or benchmark numbers in design docs. Instead:

1. Pull current prices from official pricing pages (or internal procurement sheets).
2. Store prices in configuration (versioned) and include the price version/date in every cost report.
3. Treat prices as inputs to the formulas below.

### Prompt Caching Economics (Provider-Specific)

Caching semantics, eligibility, TTLs, and discounts differ across providers and can change. Use current provider docs and model your ROI with observed hit rates.

**When Caching Pays Off**:
- Repeated system prompts > 1024 tokens
- RAG with stable context
- Multi-turn conversations with history

```python
# Caching ROI calculation
base_cost = input_tokens * base_price
cached_cost = (input_tokens * base_price * (1 - cache_hit_discount)) + cache_write_cost_if_miss

# Break-even: 2 requests with same prefix
# 3+ requests: significant savings
```

---

## Cost-Quality Tradeoff Framework

### The Cost-Quality Curve

```
Quality ▲
    100% │              ┌─ Premium tier ($$$$$)
         │         ┌────┘
         │    ┌────┘ ← Balanced tier ($$$)
         │ ┌──┘ ← Balanced/value boundary ($$)
    90%  │─┘ ← Value tier ($)
         │
    80%  │ ← Value tier ($)
         │
         └─────────────────────► Cost
           $0.01   $0.10   $1.00
```

### Decision Matrix: Model Selection by Use Case

| Use Case | Quality Need | Volume | Recommended Tier | Cost Target |
|----------|-------------|--------|------------------|-------------|
| Content moderation | High precision | 100k+/day | Value tier | Tight budget |
| Customer support | High CSAT | 10k/day | Balanced tier | Medium budget |
| Code generation | High correctness | 1k/day | Balanced/Premium | Medium budget |
| Complex reasoning | Maximum | <1k/day | Premium tier | Loose budget |
| Document analysis | 85%+ | Variable | Balanced + caching | Medium budget |

### Tiered Model Strategy (Cascade Pattern)

```python
# Route by complexity to optimize cost/quality
def select_model(request):
    complexity = estimate_complexity(request)

    if complexity < 0.3:  # Simple
        return "tier:value"
    elif complexity < 0.7:  # Medium
        return "tier:balanced"
    else:  # Complex
        return "tier:premium"

# Expected savings: 40-60% vs always using top model
```

### Quality-Cost Scoring Template

| Candidate | Quality Score (0-10) | Cost/1K Requests | Quality/$ Ratio |
|-----------|---------------------|------------------|-----------------|
| Model A | 9.5 | $50.00 | 0.19 |
| Model B | 8.5 | $5.00 | 1.70 |
| Model C | 7.0 | $0.50 | 14.00 |

**Decision rule**: Maximize Quality/$ ratio subject to minimum quality threshold

---

## Total Cost of Ownership (TCO)

### LLM TCO Components

| Component | Typical driver | Optimization Lever |
|-----------|----------|-------------------|
| **Inference usage** | Often largest variable cost | Model selection, prompt optimization, caching, routing |
| **Infrastructure** | Serving + retrieval infra | Right-sizing, batching, autoscaling |
| **Engineering** | Iteration/debugging overhead | Automation, observability, evals |
| **Embeddings** | RAG ingestion/query costs | Batching, reuse, self-hosted when justified |
| **Vector DB** | Storage + query cost | Data lifecycle, tier selection |

### TCO Calculation Template

```yaml
Monthly TCO Analysis:
  token_costs:
    llm_input: volume_requests × avg_input_tokens × input_price
    llm_output: volume_requests × avg_output_tokens × output_price
    embeddings: documents × embedding_price
    subtotal: $X

  infrastructure:
    compute: gpu_hours × hourly_rate  # Or managed API markup
    vector_db: vectors × storage_price + queries × query_price
    logging: log_volume × log_price
    subtotal: $Y

  engineering:
    monitoring: platform_costs
    on_call: hours × rate
    subtotal: $Z

  total_tco: X + Y + Z
  cost_per_request: total_tco / total_requests
  gross_margin: (revenue - total_tco) / revenue
```

### Self-Hosted vs API TCO

| Factor | API (Managed) | Self-Hosted |
|--------|---------------|-------------|
| Upfront cost | Low | Medium-high (GPUs + ops) |
| Marginal cost | Usage-based | Lower at sufficient scale |
| Engineering | Low | High |
| Break-even | N/A | Compute with your workload + utilization |
| Flexibility | Model swaps easy | Hardware locked |

**Rule of thumb**: Consider self-hosting when spend is high AND requirements are stable enough to amortize infra + ops.

---

## Fine-Tuning ROI Framework

### When Fine-Tuning Pays Off

```
ROI = (Quality Improvement Value + Cost Reduction) - Fine-Tuning Investment
                              ─────────────────────────────────────────────
                                      Fine-Tuning Investment
```

### Fine-Tuning Cost Components

| Component | Typical Cost | Notes |
|-----------|-------------|-------|
| **Data preparation** | $5k-50k | Labeling, cleaning, validation |
| **Compute (training)** | $100-10k | Depends on model size, method |
| **Evaluation** | $1k-5k | Golden set, human eval, A/B test |
| **Iteration** | 2-5 cycles | Multiply by 2-5x |
| **Maintenance** | Ongoing | Drift detection, retraining |

**Total typical investment**: $15k-100k for production fine-tune

### Fine-Tuning Decision Matrix

| Signal | Fine-Tune | Prompt Engineer | RAG |
|--------|-----------|----------------|-----|
| Need consistent style/tone | PASS | WARNING: | FAIL |
| Domain-specific terminology | PASS | WARNING: | PASS |
| Current/changing knowledge | FAIL | FAIL | PASS |
| <1000 examples available | FAIL | PASS | WARNING: |
| Latency budget <200ms | PASS | WARNING: | FAIL |
| Cost reduction needed | PASS (long-term) | WARNING: | FAIL |
| Rapid iteration required | FAIL | PASS | WARNING: |

### Fine-Tuning Break-Even Analysis

```python
# Calculate break-even point for fine-tuning investment
def fine_tuning_break_even(
    fine_tuning_cost: float,      # Total investment ($)
    current_cost_per_req: float,  # $/request with prompting
    tuned_cost_per_req: float,    # $/request after fine-tuning
    requests_per_month: int       # Request volume
) -> dict:

    savings_per_req = current_cost_per_req - tuned_cost_per_req
    monthly_savings = savings_per_req * requests_per_month
    break_even_months = fine_tuning_cost / monthly_savings

    return {
        "break_even_months": break_even_months,
        "annual_savings": monthly_savings * 12,
        "roi_1yr": (monthly_savings * 12 - fine_tuning_cost) / fine_tuning_cost
    }

# Example: $50k fine-tuning, 100k req/month
# Current: $0.05/req, Tuned (smaller model): $0.01/req
# Savings: $4k/month → Break-even: 12.5 months
```

### Fine-Tuning vs Prompting Cost Comparison

| Approach | Upfront | Per Request | Break-Even Point |
|----------|---------|-------------|-----------------|
| **Prompt only** | $0 | $0.05 (longer prompts) | Immediate |
| **Fine-tuned** | $50k | $0.01 (shorter prompts) | ~1M requests |
| **Hybrid** | $20k | $0.02 | ~500k requests |

**Decision rule**: Fine-tune when request volume justifies investment AND domain is stable

---

## Prompt Optimization for Cost

### Token Reduction Techniques

| Technique | Token Savings | Quality Impact |
|-----------|--------------|----------------|
| System prompt compression | 20-40% | Minimal |
| Example pruning | 30-50% | Test carefully |
| Output length limits | Variable | Depends on use case |
| Caching static context | 90% (cache hit) | None |
| Structured output (JSON) | 10-20% | Often improves |

### Prompt Cost Audit Checklist

- [ ] Remove redundant instructions
- [ ] Compress few-shot examples to minimal effective set
- [ ] Use structured output to reduce output tokens
- [ ] Implement prompt caching for repeated context
- [ ] Set appropriate max_tokens limits
- [ ] Consider token-efficient formatting (no unnecessary whitespace)

### Example: Prompt Optimization

**Before** (2500 tokens):
```
You are a helpful assistant that helps users with customer support.
[... 20 detailed instructions ...]
[... 5 full conversation examples ...]
```

**After** (800 tokens):
```
Role: Customer support agent
Rules: [compressed bullet points]
Examples: [1 minimal example]
Output: JSON {response, sentiment, escalate}
```

**Impact**: 68% token reduction, quality maintained

---

## Cost Monitoring & Alerting

### Essential Metrics

| Metric | Target | Alert Threshold |
|--------|--------|-----------------|
| Cost per request (p50) | <$0.05 | >$0.10 |
| Cost per request (p95) | <$0.20 | >$0.50 |
| Daily spend | Budget | 80% of budget |
| Token efficiency | >80% useful | <60% useful |
| Cache hit rate | >50% | <30% |

### Cost Dashboard Components

```yaml
dashboards:
  real_time:
    - current_spend_vs_budget
    - cost_per_request_p50_p95
    - model_tier_distribution
    - cache_hit_rate

  daily:
    - cost_by_feature
    - cost_by_model
    - token_usage_breakdown
    - anomaly_detection

  weekly:
    - trend_analysis
    - cost_optimization_opportunities
    - roi_by_use_case
```

### Budget Guardrails

```python
# Implement hard limits to prevent cost runaway
class CostGuardrails:
    def __init__(self):
        self.daily_limit = 1000  # $
        self.request_limit = 2.00  # $ per request
        self.token_limit = 50000  # per request

    def check_request(self, estimated_cost, tokens):
        if estimated_cost > self.request_limit:
            return False, "Request too expensive"
        if tokens > self.token_limit:
            return False, "Token limit exceeded"
        if self.daily_spend + estimated_cost > self.daily_limit:
            return False, "Daily budget exceeded"
        return True, None
```

---

## Cost Optimization Playbook

### Quick Wins (Week 1)

1. **Enable prompt caching** for repeated system prompts
2. **Implement max_tokens** limits on all requests
3. **Add cost logging** to every LLM call
4. **Review model selection** for each use case

### Medium-Term (Month 1)

1. **Implement model tiering** (cascade pattern)
2. **Optimize prompts** for token efficiency
3. **Add cost-based routing** logic
4. **Build cost dashboards**

### Strategic (Quarter 1)

1. **Evaluate fine-tuning ROI** for high-volume use cases
2. **Consider self-hosting** for predictable workloads
3. **Implement A/B testing** for cost/quality tradeoffs
4. **Build cost attribution** by feature/team

---

## Related Resources

- **[Decision Matrices](decision-matrices.md)** - Model selection and technology choices
- **[Project Planning Patterns](project-planning-patterns.md)** - Performance budgeting
- **[Fine-Tuning Recipes](fine-tuning-recipes.md)** - When and how to fine-tune
- **[LLMOps Best Practices](llmops-best-practices.md)** - Production operations

---
