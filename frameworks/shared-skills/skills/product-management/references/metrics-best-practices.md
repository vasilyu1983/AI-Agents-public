# Metrics Best Practices  

*Operational guide for defining, selecting, and executing product metrics.*

This file contains ONLY:

- Patterns  
- Templates  
- Checklists  
- Decision trees  
- Zero theory  

---
## Table of Contents

- [1.1 Metric Tree Checklist](#11-metric-tree-checklist)
- [2. Metric Types (Operational Categorization)](#2-metric-types-operational-categorization)
- [2.1 Leading Metrics (predict outcomes)](#21-leading-metrics-predict-outcomes)
- [2.2 Lagging Metrics (business results)](#22-lagging-metrics-business-results)
- [2.3 Guardrail Metrics (prevent regressions)](#23-guardrail-metrics-prevent-regressions)
- [3. Success Metric Templates](#3-success-metric-templates)
- [3.1 Product Outcome Metric Template](#31-product-outcome-metric-template)
- [3.2 Input Metric Template](#32-input-metric-template)
- [4. Activation Metrics (Operational)](#4-activation-metrics-operational)
- [5. Product-Led Growth Metrics](#5-product-led-growth-metrics)
- [5.1 Core PLG Metrics](#51-core-plg-metrics)
- [5.2 Habit Moment Framework](#52-habit-moment-framework)
- [5.3 PLG Funnel Template](#53-plg-funnel-template)
- [5.4 PLG Anti-Patterns](#54-plg-anti-patterns)
- [6. Retention Metrics](#6-retention-metrics)
- [6.1 Retention Curve Template](#61-retention-curve-template)
- [6.2 Healthy Retention Indicators](#62-healthy-retention-indicators)
- [7. Experimentation Metrics](#7-experimentation-metrics)
- [7.1 For A/B Tests](#71-for-ab-tests)
- [7.2 Experiment Metric Template](#72-experiment-metric-template)
- [7.3 Common A/B Mistakes (Avoid)](#73-common-ab-mistakes-avoid)
- [8. AI & LLM Product Metrics](#8-ai--llm-product-metrics)
- [8.1 Accuracy / Quality Metrics](#81-accuracy--quality-metrics)
- [8.2 Performance Metrics](#82-performance-metrics)
- [8.3 Risk Metrics](#83-risk-metrics)
- [9. Monetization Metrics (Operational)](#9-monetization-metrics-operational)
- [9.1 Revenue Components](#91-revenue-components)
- [9.2 Pricing Metrics](#92-pricing-metrics)
- [9.3 Expansion Metrics](#93-expansion-metrics)
- [10. Decision Trees](#10-decision-trees)
- [10.1 Is This a Good Metric?](#101-is-this-a-good-metric)
- [10.2 Should This Be a Primary Metric?](#102-should-this-be-a-primary-metric)
- [11. Anti-Patterns](#11-anti-patterns)
- [12. Metric Hygiene (Weekly)](#12-metric-hygiene-weekly)
- [13. Definition of Done (Metrics)](#13-definition-of-done-metrics)


# 1. Metric Tree Pattern

Use this to connect company → product → team metrics.

North Star Metric (NSM)
↳ Product Outcomes (3–5)
↳ Team Input Metrics (3–5 per team)

## 1.1 Metric Tree Checklist

- [ ] NSM reflects user value delivered  
- [ ] Product outcomes are **leading indicators** of NSM  
- [ ] Inputs are controllable by a single team  
- [ ] No vanity metrics  
- [ ] No more than 3 layers deep  
- [ ] Each metric has an owner  

---

# 2. Metric Types (Operational Categorization)

## 2.1 Leading Metrics (predict outcomes)

- Activation rate  
- Feature adoption  
- Frequency of key action  
- Time-to-value  
- Successful task completion  

## 2.2 Lagging Metrics (business results)

- Revenue  
- Retention  
- LTV  
- Churn rate  
- Expansion revenue  

## 2.3 Guardrail Metrics (prevent regressions)

- Reliability (latency, uptime)  
- Support tickets  
- Error rates  
- Cost-to-serve  

Checklist:

- [ ] Each outcome has 1–2 guardrails  
- [ ] Guardrails are monitored continuously  

---

# 3. Success Metric Templates

## 3.1 Product Outcome Metric Template

Outcome Name:
What it measures:
Formula:
Target (numeric):
Owner:
How often reviewed:
Related risks:

## 3.2 Input Metric Template

Input metric:
Why this team influences it:
Baseline:
Target:
Levers (3–5 actions):
Dependencies:

---

# 4. Activation Metrics (Operational)

Use these when improving onboarding or early value.

**Activation Funnel Template**
Visitors → Signups → Qualified signups → Activation → Habit loop

**Checklist**

- [ ] Activation defined as a meaningful action (not signup)  
- [ ] Each step of funnel is measured  
- [ ] Time window defined (e.g., Day 1, Day 7)  

---

# 5. Product-Led Growth Metrics

Use these when implementing PLG motion or measuring self-serve success.

## 5.1 Core PLG Metrics

| Metric | Definition | Benchmark |
|--------|------------|-----------|
| **Activation Rate** | % users completing key value action | 20-40% typical |
| **Time-to-Value (TTV)** | Time from signup to first "aha" moment | <5 min ideal |
| **Product-Qualified Leads (PQLs)** | Users demonstrating buying signals via product usage | Varies by product |
| **Viral Coefficient** | Users acquired via product-driven referrals | >1.0 = viral growth |
| **Net Revenue Retention (NRR)** | Revenue retained + expansion from existing customers | >100% healthy |

## 5.2 Habit Moment Framework

```text
Setup → Aha → Habit
```

- **Setup**: Account created, basic configuration complete
- **Aha**: First value delivery (product-specific milestone)
- **Habit**: Repeated usage pattern established (correlates with long-term retention)

**B2B Consideration**: Team-based activation > individual user activation. Account-level metrics matter more than individual user metrics for enterprise products.

## 5.3 PLG Funnel Template

```text
Visitors → Signups → Activated → PQL → Paying → Expanded
```

**Checklist**

- [ ] Each stage has conversion rate tracked
- [ ] Activation defined as meaningful action (not just signup)
- [ ] PQL scoring based on usage patterns
- [ ] Self-serve expansion paths identified
- [ ] Time-based cohort analysis enabled

## 5.4 PLG Anti-Patterns

- AVOID: Treating signup as activation
- AVOID: Individual user metrics for B2B products
- AVOID: Ignoring time-to-value
- AVOID: No self-serve upgrade path
- AVOID: Gating features behind sales calls only

---

# 6. Retention Metrics

## 6.1 Retention Curve Template

Cohort:
Day 0 value:
Week 1 retention:
Month 1 retention:
Month 3 retention:

## 6.2 Healthy Retention Indicators

- Flat tail after week/month 4  
- Downward slope < 10% per period  
- Active use of key feature  

---

# 7. Experimentation Metrics

## 7.1 For A/B Tests

- Primary metric (1)  
- Secondary metrics (2–3)  
- Guardrails  
- Required sample size  
- Min detectable effect (MDE)  

## 7.2 Experiment Metric Template

Experiment:
Hypothesis:
Primary metric:
Secondary metrics:
Guardrails:
MDE:
Success criteria:

## 7.3 Common A/B Mistakes (Avoid)

- AVOID: Multiple primary metrics  
- AVOID: Short experiment duration  
- AVOID: Changing metrics mid-test  
- AVOID: Insufficient sample size  

**Test duration and sample size**: Do not start a test without computing required sample size. Required sample depends on your baseline conversion rate and the minimum detectable effect (MDE) you care about — smaller MDE requires larger sample. Target 80% statistical power (β = 0.2) at p < 0.05. Do not stop a test early based on interim results (peeking inflates false-positive rate). Run until the pre-computed sample is reached or a full business cycle completes, whichever is longer. See [marketing-product-analytics](../../marketing-product-analytics/references/experimentation-framework.md) for sample-size formula, SRM checks, and sequential testing.

---

# 8. AI & LLM Product Metrics

## 8.1 Accuracy / Quality Metrics

- Factuality (%)  
- Hallucination rate  
- Agreement-with-human score  
- Relevance@K (RAG)  

## 8.2 Performance Metrics

- Latency (ms)  
- Cost per 1K tokens / inference  
- Task success rate (agents)  
- Step efficiency  

## 8.3 Risk Metrics

- Safety violation rate  
- Bias / unfairness indicators  
- Drift (distribution shift)  

---

# 9. Monetization Metrics (Operational)

## 9.1 Revenue Components

Revenue = Acquisition × Price × Retention × Expansion

## 9.2 Pricing Metrics

- ARPU  
- Discount rate  
- Paid conversion rate  

## 9.3 Expansion Metrics

- % of users upgrading  
- Add-on attach rate  
- Expansion revenue per user  

---

# 10. Decision Trees

## 10.1 Is This a Good Metric?

Is the metric measurable?
├─ No → Redesign
└─ Yes
↓
Is the metric controllable by the team?
├─ No → Move to product-level
└─ Yes
↓
Does it align with a product outcome?
├─ No → Remove
└─ Yes → Keep

---

## 10.2 Should This Be a Primary Metric?

Does it measure value delivered to user?
├─ No → Secondary
└─ Yes
↓
Does it create perverse incentives?
├─ Yes → Redesign
└─ No → Primary metric

---

# 11. Anti-Patterns

- AVOID: Tracking everything  
- AVOID: Vanity metrics (downloads, pageviews)  
- AVOID: Metrics without ownership  
- AVOID: Metrics without baselines  
- AVOID: Metrics without guardrails  
- AVOID: Sharing metrics without context  

---

# 12. Metric Hygiene (Weekly)

Checklist:

- [ ] All metrics refreshed  
- [ ] Investigate significant deltas  
- [ ] Validate data integrity  
- [ ] Update dashboard commentary  
- [ ] Reconnect metrics to roadmap bets  

---

# 13. Definition of Done (Metrics)

A metric set is **ready** when:

- [ ] There is one NSM  
- [ ] 3–5 product outcomes  
- [ ] 1–3 input metrics per team  
- [ ] All metrics have owners  
- [ ] Targets defined  
- [ ] Guardrails identified  
- [ ] Dashboard exists  
- [ ] Reviewed weekly  

---

**End of file.**
