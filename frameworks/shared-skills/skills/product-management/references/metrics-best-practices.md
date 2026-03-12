# Metrics Best Practices  

*Operational guide for defining, selecting, and executing product metrics.*

This file contains ONLY:

- Patterns  
- Templates  
- Checklists  
- Decision trees  
- Zero theory  

---

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

## 5.1 Retention Curve Template

Cohort:
Day 0 value:
Week 1 retention:
Month 1 retention:
Month 3 retention:

## 5.2 Healthy Retention Indicators

- Flat tail after week/month 4  
- Downward slope < 10% per period  
- Active use of key feature  

---

# 6. Experimentation Metrics

## 6.1 For A/B Tests

- Primary metric (1)  
- Secondary metrics (2–3)  
- Guardrails  
- Required sample size  
- Min detectable effect (MDE)  

## 6.2 Experiment Metric Template

Experiment:
Hypothesis:
Primary metric:
Secondary metrics:
Guardrails:
MDE:
Success criteria:

## 6.3 Common A/B Mistakes (Avoid)

- AVOID: Multiple primary metrics  
- AVOID: Short experiment duration  
- AVOID: Changing metrics mid-test  
- AVOID: Insufficient sample size  

---

# 7. AI & LLM Product Metrics

## 7.1 Accuracy / Quality Metrics

- Factuality (%)  
- Hallucination rate  
- Agreement-with-human score  
- Relevance@K (RAG)  

## 7.2 Performance Metrics

- Latency (ms)  
- Cost per 1K tokens / inference  
- Task success rate (agents)  
- Step efficiency  

## 7.3 Risk Metrics

- Safety violation rate  
- Bias / unfairness indicators  
- Drift (distribution shift)  

---

# 8. Monetization Metrics (Operational)

## 8.1 Revenue Components

Revenue = Acquisition × Price × Retention × Expansion

## 8.2 Pricing Metrics

- ARPU  
- Discount rate  
- Paid conversion rate  

## 8.3 Expansion Metrics

- % of users upgrading  
- Add-on attach rate  
- Expansion revenue per user  

---

# 9. Decision Trees

## 9.1 Is This a Good Metric?

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

## 9.2 Should This Be a Primary Metric?

Does it measure value delivered to user?
├─ No → Secondary
└─ Yes
↓
Does it create perverse incentives?
├─ Yes → Redesign
└─ No → Primary metric

---

# 10. Anti-Patterns

- AVOID: Tracking everything  
- AVOID: Vanity metrics (downloads, pageviews)  
- AVOID: Metrics without ownership  
- AVOID: Metrics without baselines  
- AVOID: Metrics without guardrails  
- AVOID: Sharing metrics without context  

---

# 11. Metric Hygiene (Weekly)

Checklist:

- [ ] All metrics refreshed  
- [ ] Investigate significant deltas  
- [ ] Validate data integrity  
- [ ] Update dashboard commentary  
- [ ] Reconnect metrics to roadmap bets  

---

# 12. Definition of Done (Metrics)

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
