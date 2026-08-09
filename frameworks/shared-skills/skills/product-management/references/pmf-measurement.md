# Product-Market Fit Measurement

Operational guide for measuring, tracking, and improving product-market fit.

---
## Table of Contents

- [Sean Ellis Survey Design](#sean-ellis-survey-design)
- [Core Question](#core-question)
- [Extended Survey (Recommended)](#extended-survey-recommended)
- [Survey Administration](#survey-administration)
- [Retention Curve Analysis](#retention-curve-analysis)
- [How to Build a Retention Curve](#how-to-build-a-retention-curve)
- [Reading the Curve](#reading-the-curve)
- [Benchmarks (Directional)](#benchmarks-directional)
- [Mobile Consumer Retention Benchmarks](#mobile-consumer-retention-benchmarks)
- [Segmented Retention](#segmented-retention)
- [Usage-Based & AI-Native PMF Signals](#usage-based--ai-native-pmf-signals)
- [Engagement Scoring](#engagement-scoring)
- [Define Activation Precisely](#define-activation-precisely)
- [Engagement Depth Tiers](#engagement-depth-tiers)
- [Leading vs Lagging Indicators](#leading-vs-lagging-indicators)
- [Feature Audit Methodology](#feature-audit-methodology)
- [Usage-Based Feature Audit](#usage-based-feature-audit)
- [Feature Removal Playbook](#feature-removal-playbook)
- [PMF Tracking Dashboard (Minimum Viable)](#pmf-tracking-dashboard-minimum-viable)


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

**CAUTION: web/desktop SaaS and mobile consumer benchmarks are not comparable and must not be blended.** A mobile PM comparing against the web/B2B rows below will misread health by 3-4x. Use the platform-matched table.

#### Web / Desktop / B2B SaaS

| Product Type | Good D7 Retention | Good D30 Retention |
|-------------|-------------------|-------------------|
| Consumer social (web/desktop) | 25-30% | 15-20% |
| Consumer utility (web/desktop) | 30-40% | 20-25% |
| B2B SaaS (SMB) | 40-50% | 30-40% |
| B2B SaaS (Enterprise) | 60-70% | 50-60% |

#### Mobile Consumer Retention Benchmarks

Mobile apps face structurally lower retention due to app-switching friction, notification competition, and lower switching cost. Use these rows for native iOS/Android consumer apps only.

| Tier | Good D1 Retention | Good D7 Retention | Good D30 Retention |
|------|-------------------|-------------------|--------------------|
| Average consumer app | 25-35% | 10-15% | 3-6% |
| Top-quartile consumer social | 35-40% | 15-20% | 10-15% |
| Top-quartile consumer utility | 30-40% | 12-18% | 6-10% |

Sources: Plotline/OneSignal/Pushwoosh mobile retention industry benchmarks (2025-2026). D30 averages of 3-6% are normal; do not benchmark a mobile app against the web/B2B rows above.

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

## Usage-Based & AI-Native PMF Signals

Usage-based pricing (UBP) and consumption/token/outcome models are now the dominant monetization pattern for AI-native products. Seat-based PMF assumptions misdiagnose consumption products — run these signals in addition to or instead of the standard dashboard when the value metric is a consumable (tokens, API calls, runs, outcomes) rather than a seat.

### How UBP Remaps Standard PMF Signals

| Standard Signal | Seat-Based Reading | UBP / Consumption Reading |
|----------------|-------------------|--------------------------|
| NRR | Expansion = more seats | Expansion = more spend per account (dollar/consumption growth) |
| Churn | Account cancels | Usage cliff: consumption decay precedes cancellation by weeks |
| CAC payback | MRR / (blended CAC / gross margin) | Payback based on consumption ARR growth trajectory, not fixed MRR |
| Value-metric alignment | Seat count correlates with value | Consumption unit (tokens/calls/runs) correlates with value delivered |

### Leading Indicators for UBP Products

| Indicator | What to Measure | PMF Signal |
|-----------|----------------|------------|
| Per-account consumption growth | Tokens / API calls / runs MoM per account | Sustained growth with no cliff = product embedding in workflow |
| Usage-to-seat ratio | Consumption units per licensed seat | Rising ratio = deeper per-user engagement |
| Consumption-based NRR | Dollar expansion from consumption growth per cohort | Target >100%; compute by cohort, not blended |
| Usage cliff detection | Accounts with >30% consumption drop over 60 days | Leading churn signal; trigger at-risk intervention |
| Price-tier retention | NRR segmented by price point | See AI retention cliff below |

### AI-Native Retention Cliff by Price Point

AI-native tools show a structural retention cliff at low price points driven by experimental adoption, commodity perception, and willingness-to-pay misalignment:

| Monthly Price Band | Approximate NRR Range |
|--------------------|-----------------------|
| <$20/mo | ~20-25% |
| $20-$100/mo | ~40-50% |
| >$100/mo | ~80-90% |

Implication: a 99% NRR target is appropriate for flat-rate SMB SaaS but is not meaningful as a standalone signal for usage-based products — a UBP account can retain at 99% NRR while usage stagnates if the subscription floor is fixed. Diagnose by consumption cohort, not by subscription status. If NRR is strong but consumption per account is flat or declining, you are measuring billing retention, not product PMF.

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
