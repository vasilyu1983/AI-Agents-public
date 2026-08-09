# Agent Economics & ROI Framework

**Purpose**: Business-focused decision framework for agent investments — token costs, ROI calculation, hallucination impact, and when to kill an agent project.

No theory. No narrative. Only what you can calculate and decide.

---
## Table of Contents

- [Token Economics (July 2026 Pricing)](#token-economics-july-2026-pricing)
- [Cost Per Model (USD per 1M tokens)](#cost-per-model-usd-per-1m-tokens)
- [Agent Task Cost Estimates](#agent-task-cost-estimates)
- [Monthly Cost Projections](#monthly-cost-projections)
- [Agent ROI Framework](#agent-roi-framework)
- [ROI Calculation Formula](#roi-calculation-formula)
- [Cost Categories (Annual)](#cost-categories-annual)
- [Value Categories (Annual)](#value-categories-annual)
- [ROI Tiers](#roi-tiers)
- [Hallucination Cost Framework](#hallucination-cost-framework)
- [Hallucination Impact Categories](#hallucination-impact-categories)
- [Hallucination Rate Benchmarks (2026)](#hallucination-rate-benchmarks-2026)
- [Hallucination Cost Calculator](#hallucination-cost-calculator)
- [Mitigation Investment Framework](#mitigation-investment-framework)
- [Agent Investment Decision Matrix](#agent-investment-decision-matrix)
- [Quick Filters (Kill Early)](#quick-filters-kill-early)
- [Investment Decision Tree](#investment-decision-tree)
- [When to Kill an Agent Project](#when-to-kill-an-agent-project)
- [Kill Signals (Any One = Stop)](#kill-signals-any-one-=-stop)
- [Pivot vs Kill Decision](#pivot-vs-kill-decision)
- [ROI Tracking Dashboard](#roi-tracking-dashboard)
- [Metrics to Track Weekly](#metrics-to-track-weekly)
- [Monthly ROI Report Template](#monthly-roi-report-template)
- [Agent ROI Report - [Month]](#agent-roi-report-month)
- [Summary](#summary)
- [Quality Metrics](#quality-metrics)
- [Cost Breakdown](#cost-breakdown)
- [Recommendation](#recommendation)
- [Quick Reference: Economics Formulas](#quick-reference-economics-formulas)
- [Break-even volume](#break-even-volume)
- [Payback period (months)](#payback-period-months)
- [Hallucination budget](#hallucination-budget)
- [Token efficiency target](#token-efficiency-target)
- [Scaling threshold](#scaling-threshold)
- [Related References](#related-references)


## Token Economics (July 2026 Pricing)

Prices move quarterly; treat this table as decision-scale anchors and verify against provider pricing docs before quoting in a deliverable.

### Cost Per Model (USD per 1M tokens)

| Model | Input | Output | Cached Input | Notes |
|-------|-------|--------|--------------|-------|
| **GPT-5.5** | $5.00 | $30.00 | $0.50 | Flagship, 1M context |
| **GPT-5.4** | $2.50 | $15.00 | $0.25 | Mid-tier workhorse |
| **GPT-5.4 mini** | $0.75 | $4.50 | ~0.1x input | High-volume, simple tasks |
| **Claude Opus 4.8** | $5.00 | $25.00 | $0.50 | Flagship coding/agents |
| **Claude Sonnet 4.6** | $3.00 | $15.00 | $0.30 | Coding/reasoning workhorse |
| **Claude Haiku 4.5** | $1.00 | $5.00 | $0.10 | Fast, cheap classification |
| **Gemini 3.1 Pro** | $2.00 | $12.00 | see docs | Value flagship (<=200K prompt tier) |
| **Gemini 3.5 Flash** | $1.50 | $9.00 | see docs | Fast mid-tier |
| **Gemini 3.1 Flash-Lite** | $0.25 | $1.50 | see docs | Cheapest for simple tasks |

Batch APIs run ~50% off list at all three providers; prompt caching cuts cached input ~90% (Anthropic/OpenAI).

### Agent Task Cost Estimates

| Agent Type | Avg Tokens/Task | Cost/Task (GPT-5.4) | Cost/Task (Haiku 4.5) |
|------------|-----------------|---------------------|------------------------|
| Simple Q&A | 2K in + 500 out | $0.013 | $0.005 |
| RAG Query | 8K in + 1K out | $0.035 | $0.013 |
| Tool-Using (3 calls) | 15K in + 3K out | $0.08 | $0.03 |
| Code Generation | 10K in + 2K out | $0.055 | $0.02 |
| Multi-Agent (5 steps) | 50K in + 10K out | $0.28 | $0.10 |
| Agentic Coding Session | 200K in + 50K out | $1.25 | $0.45 |

### Monthly Cost Projections

Mid-tier model (GPT-5.4 / Sonnet-class) without caching; caching and batch typically cut these 40-70%.

| Volume | Simple Agent | RAG Agent | Tool Agent | Multi-Agent |
|--------|--------------|-----------|------------|-------------|
| 1K tasks/day | $375/mo | $1,050/mo | $2,475/mo | $8,250/mo |
| 10K tasks/day | $3,750/mo | $10,500/mo | $24,750/mo | $82,500/mo |
| 100K tasks/day | $37,500/mo | $105,000/mo | $247,500/mo | $825,000/mo |

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

> **Actual cost data**: To feed real token and cost numbers into this dashboard from Claude Code or Codex CLI sessions, see [`coding-agent-usage-tracking.md`](coding-agent-usage-tracking.md).

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
- [Coding Agent Usage Tracking](coding-agent-usage-tracking.md) — Measure actual CLI token spend with ccusage
