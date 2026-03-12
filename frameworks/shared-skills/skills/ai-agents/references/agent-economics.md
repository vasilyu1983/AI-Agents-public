# Agent Economics & ROI Framework

**Purpose**: Business-focused decision framework for agent investments — token costs, ROI calculation, hallucination impact, and when to kill an agent project.

No theory. No narrative. Only what you can calculate and decide.

---

## Token Economics (January 2026 Pricing)

### Cost Per Model (USD per 1M tokens)

| Model | Input | Output | Cached Input | Notes |
|-------|-------|--------|--------------|-------|
| **GPT-4o** | $2.50 | $10.00 | $1.25 | Best cost/quality balance |
| **GPT-4o-mini** | $0.15 | $0.60 | $0.075 | High-volume, simple tasks |
| **Claude 3.5 Sonnet** | $3.00 | $15.00 | $0.30 | Best for coding/reasoning |
| **Claude 3.5 Haiku** | $0.80 | $4.00 | $0.08 | Fast, cheap classification |
| **Gemini 1.5 Pro** | $1.25 | $5.00 | $0.315 | Long context (2M tokens) |
| **Gemini 1.5 Flash** | $0.075 | $0.30 | $0.01875 | Cheapest for simple tasks |

### Agent Task Cost Estimates

| Agent Type | Avg Tokens/Task | Cost/Task (GPT-4o) | Cost/Task (Haiku) |
|------------|-----------------|-------------------|-------------------|
| Simple Q&A | 2K in + 500 out | $0.01 | $0.004 |
| RAG Query | 8K in + 1K out | $0.03 | $0.01 |
| Tool-Using (3 calls) | 15K in + 3K out | $0.07 | $0.02 |
| Code Generation | 10K in + 2K out | $0.045 | $0.015 |
| Multi-Agent (5 steps) | 50K in + 10K out | $0.225 | $0.06 |
| Agentic Coding Session | 200K in + 50K out | $1.00 | $0.26 |

### Monthly Cost Projections

| Volume | Simple Agent | RAG Agent | Tool Agent | Multi-Agent |
|--------|--------------|-----------|------------|-------------|
| 1K tasks/day | $300/mo | $900/mo | $2,100/mo | $6,750/mo |
| 10K tasks/day | $3,000/mo | $9,000/mo | $21,000/mo | $67,500/mo |
| 100K tasks/day | $30,000/mo | $90,000/mo | $210,000/mo | $675,000/mo |

---

## Agent ROI Framework

### ROI Calculation Formula

```text
Agent ROI = (Value Created - Total Cost) / Total Cost × 100%

Where:
- Value Created = (Tasks Automated × Human Cost/Task) + Revenue Impact
- Total Cost = Development + Infrastructure + LLM Costs + Maintenance + Error Costs
```

### Cost Categories (Annual)

| Category | Components | Typical Range |
|----------|------------|---------------|
| **Development** | Engineering time, testing, iteration | $50K - $500K |
| **Infrastructure** | Compute, vector DB, monitoring | $12K - $120K |
| **LLM API Costs** | Token usage (see above) | $3.6K - $800K |
| **Maintenance** | Prompt tuning, bug fixes, updates | 20-40% of dev cost |
| **Error/Hallucination** | Human review, corrections, customer impact | 5-30% of LLM cost |

### Value Categories (Annual)

| Value Type | Measurement | Example |
|------------|-------------|---------|
| **Labor Savings** | Hours saved × hourly cost | 10K hrs × $50 = $500K |
| **Speed Premium** | Faster delivery × value | 50% faster × $200K = $100K |
| **Scale Enablement** | Tasks impossible without agent | 100K queries × $5 value = $500K |
| **Quality Improvement** | Error reduction × error cost | 50% fewer errors × $100K = $50K |
| **Revenue Lift** | Conversion improvement × revenue | 2% lift × $5M = $100K |

### ROI Tiers

| ROI | Assessment | Action |
|-----|------------|--------|
| **<0%** | Negative ROI | Kill or pivot immediately |
| **0-50%** | Marginal | Optimize costs or scope |
| **50-200%** | Healthy | Scale and maintain |
| **200-500%** | Strong | Expand use cases |
| **>500%** | Exceptional | Productize or license |

---

## Hallucination Cost Framework

### Hallucination Impact Categories

| Category | Description | Cost Multiplier |
|----------|-------------|-----------------|
| **Benign** | User notices, asks for correction | 1.5x task cost |
| **Annoying** | User loses trust, abandons task | 3x task cost + churn risk |
| **Costly** | Wrong action taken, needs reversal | 10-100x task cost |
| **Dangerous** | Legal, safety, or compliance violation | $10K - $10M per incident |

### Hallucination Rate Benchmarks (2026)

| Agent Type | Baseline Rate | With Guardrails | Best Achievable |
|------------|---------------|-----------------|-----------------|
| Simple Q&A | 5-10% | 2-5% | <1% |
| RAG (good retrieval) | 3-8% | 1-3% | <0.5% |
| Tool-Using | 8-15% | 3-8% | 1-3% |
| Code Generation | 10-20% | 5-10% | 2-5% |
| Multi-Agent | 15-25% | 8-15% | 3-8% |

### Hallucination Cost Calculator

```text
Monthly Hallucination Cost =
  Tasks × Hallucination Rate × Avg Impact Cost

Example (10K RAG queries/day, 3% rate, $5 avg impact):
  300,000 × 0.03 × $5 = $45,000/month
```

### Mitigation Investment Framework

| Mitigation | Implementation Cost | Hallucination Reduction | ROI Threshold |
|------------|--------------------|-----------------------|---------------|
| Better prompts | $5-10K | 20-40% | >$2K/mo hallucination cost |
| RAG grounding | $20-50K | 40-60% | >$10K/mo hallucination cost |
| Multi-layer guardrails | $30-80K | 50-70% | >$20K/mo hallucination cost |
| Human-in-the-loop | $50-150K | 80-95% | >$50K/mo hallucination cost |
| Fine-tuning | $100-500K | 60-80% | >$100K/mo hallucination cost |

---

## Agent Investment Decision Matrix

### Quick Filters (Kill Early)

**Do NOT build an agent if:**

| Red Flag | Reason | Alternative |
|----------|--------|-------------|
| <100 tasks/month | ROI never positive | Manual process or simple automation |
| >$100/task human cost acceptable | Agent won't beat human quality | Keep humans |
| Hallucination cost >$1K/incident | Risk too high without massive guardrails | Human-in-the-loop only |
| No clear success metric | Can't prove value | Define metrics first |
| Data quality <80% | Garbage in, garbage out | Fix data first |
| Regulatory requires 100% accuracy | Agents can't guarantee this | Human review required |

### Investment Decision Tree

```text
Should you build an agent?
│
├─ Task volume >1000/month?
│   ├─ No → Don't build (manual is cheaper)
│   └─ Yes → Continue
│       │
│       ├─ Human cost >$10/task?
│       │   ├─ No → Don't build (agent likely more expensive)
│       │   └─ Yes → Continue
│       │       │
│       │       ├─ Hallucination cost <$50/incident?
│       │       │   ├─ No → Build with heavy guardrails + HITL
│       │       │   └─ Yes → Continue
│       │       │       │
│       │       │       ├─ Task is structured/repeatable?
│       │       │       │   ├─ No → Consider simpler automation
│       │       │       │   └─ Yes → BUILD AGENT
│       │       │       │
│       │       │       └─ Projected ROI >100%?
│       │       │           ├─ No → Optimize scope first
│       │       │           └─ Yes → BUILD AGENT
```

---

## When to Kill an Agent Project

### Kill Signals (Any One = Stop)

| Signal | Threshold | Measurement |
|--------|-----------|-------------|
| Negative ROI after 3 months | <0% | Monthly cost vs value |
| Hallucination rate not improving | >10% after 2 iterations | Error tracking |
| User adoption <20% | After 1 month post-launch | Active users / eligible users |
| LLM costs >2x projection | For 2 consecutive months | API billing |
| Maintenance >50% of dev time | Sustained over 1 month | Engineering hours |
| Compliance/legal concerns raised | Any | Legal review |

### Pivot vs Kill Decision

| Situation | Action | Criteria |
|-----------|--------|----------|
| High value, high cost | Optimize | Value >2x cost, clear optimization path |
| High value, quality issues | Invest in guardrails | Users want it, hallucinations fixable |
| Low value, low cost | Maintain minimally | <$1K/mo, no active complaints |
| Low value, high cost | **KILL** | Sunk cost fallacy - stop now |
| High risk, any ROI | **KILL or heavy HITL** | Legal/safety risks not worth it |

---

## ROI Tracking Dashboard

### Metrics to Track Weekly

| Metric | Formula | Target |
|--------|---------|--------|
| **Cost per Task** | Total LLM cost / completed tasks | Decreasing |
| **Error Rate** | Failed tasks / total tasks | <5% |
| **Hallucination Rate** | Human-flagged errors / total tasks | <3% |
| **Automation Rate** | Agent-completed / total eligible | >80% |
| **User Satisfaction** | CSAT or NPS | >4.0/5 or >30 NPS |
| **Time Saved** | Avg human time × tasks automated | Increasing |

### Monthly ROI Report Template

```markdown
## Agent ROI Report - [Month]

### Summary
- **Total Tasks**: X
- **Total Cost**: $X (LLM: $X, Infra: $X, Maintenance: $X)
- **Value Created**: $X (Labor: $X, Speed: $X, Quality: $X)
- **Net ROI**: X%

### Quality Metrics
- Hallucination Rate: X% (target: <3%)
- Error Rate: X% (target: <5%)
- Human Escalation Rate: X%

### Cost Breakdown
- Cost per Task: $X (vs $X human cost)
- LLM Efficiency: X tokens/task (vs X last month)

### Recommendation
[ ] Scale  [ ] Maintain  [ ] Optimize  [ ] Kill
```

---

## Quick Reference: Economics Formulas

```text
# Break-even volume
Break-even = Fixed Costs / (Human Cost/Task - Agent Cost/Task)

# Payback period (months)
Payback = Development Cost / (Monthly Value - Monthly Operating Cost)

# Hallucination budget
Max Hallucination Rate = Acceptable Error Cost / (Tasks × Avg Impact Cost)

# Token efficiency target
Target Tokens/Task = Budget / (Tasks × Cost/Token)

# Scaling threshold
Scale when: ROI >200% AND Error Rate <5% AND Adoption >80%
```

---

## Related References

- [Agent Maturity & Governance](agent-maturity-governance.md) — Capability levels and rollout risk
- [Evaluation & Observability](evaluation-and-observability.md) — Metrics and monitoring
- [Deployment, CI/CD & Safety](deployment-ci-cd-and-safety.md) — Production guardrails
