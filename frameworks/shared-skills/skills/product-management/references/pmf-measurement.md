# Product-Market Fit Measurement

Operational guide for measuring, tracking, and improving product-market fit.

---

## Sean Ellis Survey Design

### Core Question

"How would you feel if you could no longer use [product]?"
- Very disappointed
- Somewhat disappointed
- Not disappointed

**PMF signal**: >40% "Very disappointed" (benchmark from Superhuman, Slack, Notion early days).

### Extended Survey (Recommended)

Combine Sean Ellis with usage and open-ended questions:

1. **Sean Ellis question** (above)
2. **Primary use case**: "What is the main thing you use [product] for?"
3. **Key benefit**: "What is the primary benefit you get from [product]?"
4. **Alternative**: "What would you use instead if [product] didn't exist?"
5. **Improvement**: "What's the one thing we could do to make [product] better for you?"
6. **NPS**: "How likely are you to recommend [product] to a colleague?" (0-10)
7. **Usage frequency**: "How often do you use [product]?" (Daily / Several times a week / Weekly / Monthly / Rarely)

### Survey Administration

- **Who to survey**: Active users who have used the product at least 2x in the past 2 weeks
- **Minimum sample**: 40+ responses for statistical relevance
- **Frequency**: Quarterly (or after major product changes)
- **Segmentation**: Always analyze by ICP/segment, not just aggregate

See `assets/discovery/pmf-survey-template.md` for the ready-to-use survey.

---

## Retention Curve Analysis

### How to Build a Retention Curve

1. Define a cohort (users who signed up in week/month X)
2. Define "active" (what action counts as usage?)
3. Track % of cohort still active at week/month 1, 2, 3... N
4. Plot the curve

### Reading the Curve

```
100% ──┐
       │\
       │ \
       │  \──────────────── Flattening = PMF (users who stay, stay)
       │   \
       │    └──────── Declining = No PMF (even retained users leave)
       │
  0% ──┴──────────────────
       W1  W2  W4  W8  W12
```

**Flattening curve** = PMF signal. The earlier and higher it flattens, the stronger the PMF.
**Declining curve** = Problem. Even retained users are leaving — the product isn't sticky enough.
**S-curve (rises then flattens)** = Activation problem. Users who get past the initial hurdle stay.

### Benchmarks (Directional)

| Product Type | Good D7 Retention | Good D30 Retention |
|-------------|-------------------|-------------------|
| Consumer social | 25-30% | 15-20% |
| Consumer utility | 30-40% | 20-25% |
| B2B SaaS (SMB) | 40-50% | 30-40% |
| B2B SaaS (Enterprise) | 60-70% | 50-60% |

### Segmented Retention

Always segment retention by:
- Acquisition channel (organic vs paid vs referral)
- ICP match (target segment vs non-target)
- Activation status (completed onboarding vs didn't)
- Plan type (free vs paid)

You may have PMF in one segment but not another. This is common and useful — double down on the segment with PMF.

---

## Engagement Scoring

### Define Activation Precisely

Activation is NOT signup. It's the moment the user gets first value.

| Product | Activation Event | Window |
|---------|-----------------|--------|
| Project management tool | Created project + invited 1 team member | First 7 days |
| Analytics platform | Connected data source + viewed first report | First 14 days |
| CRM | Added 10 contacts + logged 1 activity | First 7 days |
| Developer tool | Completed integration + ran first job | First 3 days |

### Engagement Depth Tiers

| Tier | Definition | What It Means |
|------|-----------|---------------|
| Power users | Use core features daily, adopt new features | Product champions; source of referrals |
| Regular users | Use core features weekly | Retained but not deeply engaged |
| Casual users | Use occasionally, limited feature adoption | At risk of churn; activation problem |
| Dormant | Signed up but stopped using | Lost; re-engagement or churn |

### Leading vs Lagging Indicators

| Leading (Predict) | Lagging (Confirm) |
|-------------------|-------------------|
| Activation rate | Revenue retention (NRR) |
| Feature adoption depth | Churn rate |
| Session frequency | LTV |
| Time-to-value | Sean Ellis score |

---

## Feature Audit Methodology

### Usage-Based Feature Audit

1. Instrument all features with usage tracking (events, not page views)
2. Pull usage data for the past 90 days
3. Segment features into quadrants:

| | High Usage | Low Usage |
|---|-----------|-----------|
| **High Value** (users say it's important) | Core — invest, polish | Hidden gem — improve discovery |
| **Low Value** (users don't care) | Habit — maintain, don't expand | Dead weight — sunset candidate |

4. For each "dead weight" feature:
   - Check support cost (tickets, documentation, bugs)
   - Check maintenance cost (code complexity, dependencies)
   - If combined cost > value: sunset with 30-day notice

### Feature Removal Playbook

1. Identify candidate (low usage + low value + maintenance cost)
2. Notify users 30 days in advance (in-app + email)
3. Offer migration path or alternative
4. Monitor support tickets during sunset period
5. Remove and simplify codebase
6. Document the decision (what we learned, why we removed it)

---

## PMF Tracking Dashboard (Minimum Viable)

Track these metrics monthly (or weekly if pre-PMF):

| Metric | Formula | PMF Signal |
|--------|---------|------------|
| Sean Ellis % | % "Very disappointed" responses | >40% |
| Activation rate | Activated users / Signups | Increasing or stable |
| D30 retention | Active at D30 / Cohort size | Flattening curve |
| NRR | (Starting MRR + Expansion - Contraction - Churn) / Starting MRR | >100% |
| Time to value | Median time from signup to activation event | Decreasing |
| Feature adoption | % users using top 5 features | Broad adoption of core features |
