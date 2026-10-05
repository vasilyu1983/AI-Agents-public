# Agent Economics & ROI Framework

**Purpose**: Business-focused decision framework for agent investments — token costs, ROI calculation, hallucination impact, and when to kill an agent project.

No theory. No narrative. Only what you can calculate and decide.

---
## Table of Contents

- [Token Economics](#token-economics)
- [Look Up Rates, Then Compute](#look-up-rates-then-compute)
- [Agent Task Token Profiles](#agent-task-token-profiles)
- [Monthly Cost Projections](#monthly-cost-projections)
- [Agent ROI Framework](#agent-roi-framework)
- [ROI Calculation Formula](#roi-calculation-formula)
- [Cost Categories (Annual)](#cost-categories-annual)
- [Value Categories (Annual)](#value-categories-annual)
- [ROI Tiers](#roi-tiers)
- [Hallucination Cost Framework](#hallucination-cost-framework)
- [Hallucination Impact Categories](#hallucination-impact-categories)
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


## Token Economics

Token cost is a formula over rates you look up on the day you decide. Do not carry a remembered price into a budget: provider rates and tier names change within weeks.

### Look Up Rates, Then Compute

1. Read the current per-1M-token rates for each candidate model on the provider's pricing page (Anthropic: https://claude.com/pricing; OpenAI: https://developers.openai.com/api/docs/pricing; Google: https://ai.google.dev/gemini-api/docs/pricing). Record input, output, cached-input, and any batch discount, with the date you read them.
2. Plug them into the formulas below. The decision the numbers feed is model-tier choice per task type and whether the agent clears the ROI bar in the next section.

```text
Cost/task  = input_tokens × input_rate / 1M + output_tokens × output_rate / 1M
             (cached prefix tokens at the cached-input rate instead of input_rate)
Cost/month = Cost/task × tasks/day × 30
```

Durable relationships that hold across price changes: output tokens cost several times input tokens at every major provider, so output-heavy agents are the expensive ones; prompt caching bills repeated prefixes at a fraction of the input rate; batch APIs trade latency for a discount. Check the size of each on the pricing page before relying on it.

### Agent Task Token Profiles

| Agent Type | Avg Tokens/Task |
|------------|-----------------|
| Simple Q&A | 2K in + 500 out |
| RAG Query | 8K in + 1K out |
| Tool-Using (3 calls) | 15K in + 3K out |
| Code Generation | 10K in + 2K out |
| Multi-Agent (5 steps) | 50K in + 10K out |
| Agentic Coding Session | 200K in + 50K out |

Measure your own profile from traces before budgeting; these are starting assumptions.

### Monthly Cost Projections

Worked example with hypothetical rates (not any provider's price): input $2 per 1M, output $10 per 1M, no caching.

```text
RAG query: 8,000 × $2/1M + 1,000 × $10/1M = $0.016 + $0.010 = $0.026/task
10K tasks/day × 30 days × $0.026 = $7,800/month
```

Scale is linear in volume, so compute one row per agent type with your looked-up rates, then apply your measured cache-hit rate and any batch share.

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

Development (engineering time, testing, iteration), infrastructure (compute, vector DB, monitoring), LLM API spend (the formula above with current rates), maintenance (prompt tuning, fixes, updates; a recurring share of development cost), and error or hallucination handling (human review, corrections, customer impact). Take every figure from your own quotes, payroll, and billing; no planning range is given here because none would be sourced.

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

Ordered by cost, cheapest first: **benign** (user notices and asks for a correction), **annoying** (user loses trust and abandons the task; churn risk), **costly** (a wrong action is taken and must be reversed), **dangerous** (legal, safety, or compliance violation). Price each tier from your own incident and support data; the tiers order the risk, they do not size it.

### Hallucination Cost Calculator

```text
Monthly Hallucination Cost =
  Tasks × Hallucination Rate × Avg Impact Cost

Example (10K RAG queries/day, 3% rate, $5 avg impact):
  300,000 × 0.03 × $5 = $45,000/month
```

### Mitigation Investment Framework

Apply levers in cost order and stop when the measured hallucination cost falls under the next lever's cost: better prompts → RAG grounding → multi-layer guardrails → human-in-the-loop → fine-tuning. A lever is justified only when the monthly hallucination cost from the calculator above exceeds what the lever costs to build and run, and the only defensible reduction figure is the one you measure on your own eval set before and after the change.

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
