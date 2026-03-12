# UX Metrics Framework

Comprehensive guide to measuring UX success through task metrics, satisfaction scores, behavioral analytics, and North Star metrics.

---

## UX Metrics Overview

### Behavioral vs Attitudinal Metrics

| Type | What It Measures | Examples | Collection Method |
|------|------------------|----------|-------------------|
| **Behavioral** | What users do | Task success, time-on-task, clicks | Analytics, observation |
| **Attitudinal** | What users think/feel | Satisfaction, NPS, perceived ease | Surveys, interviews |

### Leading vs Lagging Indicators

| Type | Definition | UX Examples | Action |
|------|------------|-------------|--------|
| **Leading** | Predicts future outcomes | Task success, activation rate | Improve before problems occur |
| **Lagging** | Reflects past performance | Churn, revenue, NPS | Diagnose after seeing results |

### HEART Framework (Google)

```text
HEART: Metrics Framework for UX

H - Happiness
    • User satisfaction
    • NPS, CSAT, SUS

E - Engagement
    • How much users use product
    • DAU/MAU, session duration, features used

A - Adoption
    • New users, feature uptake
    • Signups, activation, feature adoption rate

R - Retention
    • Users who keep coming back
    • Day 1/7/30 retention, churn rate

T - Task Success
    • Can users accomplish goals?
    • Task completion rate, time-on-task, error rate
```

### Goals-Signals-Metrics (GSM)

```text
For each HEART dimension:

1. GOAL: What are we trying to achieve?
2. SIGNAL: How will we know if we're succeeding?
3. METRIC: What will we measure?

Example (Task Success):
• Goal: Users can complete checkout quickly and easily
• Signal: Users finish checkout without abandoning
• Metric: Checkout completion rate, time to complete
```

---

## Task-Level Metrics

### Task Success Rate (TSR)

**Definition**: Percentage of users who successfully complete a task

**Formula**:
```text
TSR = (Successful completions / Total attempts) × 100

Binary Success:
• 1 = Completed task
• 0 = Failed or abandoned

Partial Success:
• 1.0 = Completed without assistance
• 0.5 = Completed with hints or difficulty
• 0 = Failed
```

**Benchmarks**:
| Context | Poor | Average | Good | Excellent |
|---------|------|---------|------|-----------|
| E-commerce checkout | <60% | 60-70% | 70-80% | >80% |
| SaaS core task | <70% | 70-80% | 80-90% | >90% |
| Mobile app flow | <65% | 65-75% | 75-85% | >85% |

### Time on Task (ToT)

**Definition**: Time elapsed from task start to completion or abandonment

**Measurement Tips**:
- Start: User begins task (first relevant action)
- End: User signals completion OR gives up
- Exclude: Think-aloud overhead in moderated tests

**Analysis**:
```text
Geometric mean is better than arithmetic mean for time data
(handles outliers better)

Geometric Mean = ⁿ√(T₁ × T₂ × ... × Tₙ)

Report:
• Median time (less sensitive to outliers)
• 75th percentile (captures slower users)
• Compare to optimal time (expert baseline)
```

**Benchmarks by Task Type**:
| Task Complexity | Expected Time | Warning Threshold |
|-----------------|---------------|-------------------|
| Simple (1-2 clicks) | <30 sec | >1 min |
| Medium (3-5 steps) | 1-3 min | >5 min |
| Complex (multi-step) | 3-10 min | >15 min |

### Error Rate

**Definition**: Mistakes made while attempting a task

**Error Types**:
| Type | Definition | Example |
|------|------------|---------|
| **Slip** | Unintended action (knew correct action) | Typo, misclick |
| **Mistake** | Wrong action (misunderstood interface) | Wrong menu, wrong button |
| **Recovery** | How user gets back on track | Back button, undo, start over |

**Error Rate Formula**:
```text
Error Rate = Total errors / Total opportunities for error

OR

Errors per Task = Total errors / Number of tasks attempted
```

**Analysis Questions**:
- Where do errors occur most?
- Can users recover?
- What causes confusion?

### Lostness Score

**Definition**: Measure of unnecessary navigation

**Formula**:
```text
Lostness = √[(N/S - 1)² + (R/N - 1)²]

Where:
N = Number of pages visited
S = Minimum pages required
R = Unique pages visited

Score Interpretation:
0.0 = Perfect navigation
<0.4 = Acceptable
0.4-0.5 = Problems likely
>0.5 = User clearly lost
```

---

## Study-Level Metrics

### System Usability Scale (SUS)

**Definition**: Industry-standard 10-question usability assessment

**Questionnaire**:
```text
Rate 1 (Strongly Disagree) to 5 (Strongly Agree):

1. I think that I would like to use this system frequently.
2. I found the system unnecessarily complex. (R)
3. I thought the system was easy to use.
4. I think that I would need the support of a technical person to use this system. (R)
5. I found the various functions in this system were well integrated.
6. I thought there was too much inconsistency in this system. (R)
7. I would imagine that most people would learn to use this system very quickly.
8. I found the system very cumbersome to use. (R)
9. I felt very confident using the system.
10. I needed to learn a lot of things before I could get going with this system. (R)

(R) = Reverse scored
```

**Scoring**:
```text
For items 1, 3, 5, 7, 9: Score = Response - 1
For items 2, 4, 6, 8, 10: Score = 5 - Response

SUS Score = (Sum of scores) × 2.5

Range: 0-100
```

**Interpretation**:
| Score | Grade | Percentile | Interpretation |
|-------|-------|------------|----------------|
| >80.3 | A | 90th | Excellent |
| 68-80.3 | B | 70th-89th | Good |
| 51-68 | C | 35th-69th | OK |
| 38-51 | D | 15th-34th | Poor |
| <38 | F | <15th | Awful |

**Industry Benchmark**: 68 is average (50th percentile)

### UMUX-Lite

**Definition**: 2-question version of SUS for quick assessment

**Questions**:
```text
1. [Product name]'s capabilities meet my requirements.
   1 (Strongly Disagree) to 7 (Strongly Agree)

2. [Product name] is easy to use.
   1 (Strongly Disagree) to 7 (Strongly Agree)
```

**Scoring**:
```text
UMUX-Lite = [(Response1 - 1) + (Response2 - 1)] / 12 × 100
```

### Single Ease Question (SEQ)

**Definition**: Task-level satisfaction question

```text
"Overall, how easy or difficult was this task?"

1 = Very Difficult
2
3
4 = Neither Easy nor Difficult
5
6
7 = Very Easy

Benchmark: 5.5+ is good
```

### After-Scenario Questionnaire (ASQ)

**Definition**: 3-question task satisfaction survey

```text
For each statement, rate 1 (Strongly Disagree) to 7 (Strongly Agree):

1. I am satisfied with the ease of completing this task.
2. I am satisfied with the amount of time it took to complete this task.
3. I am satisfied with the support information (help, messages, documentation).

ASQ Score = Average of 3 responses
Benchmark: 5.0+ is good
```

---

## Product-Level Metrics

### Net Promoter Score (NPS)

**Question**:
```text
"How likely are you to recommend [product] to a friend or colleague?"

0 (Not at all likely) ... 10 (Extremely likely)
```

**Calculation**:
```text
Promoters: 9-10
Passives: 7-8
Detractors: 0-6

NPS = % Promoters - % Detractors

Range: -100 to +100
```

**Benchmarks**:
| Score Range | Interpretation |
|-------------|----------------|
| <0 | Needs improvement |
| 0-30 | Good |
| 30-70 | Great |
| >70 | Excellent |

**Industry Benchmarks** (2025):
| Industry | Average NPS |
|----------|-------------|
| SaaS | 30-40 |
| E-commerce | 35-45 |
| Financial services | 25-35 |
| Consumer apps | 40-50 |

### Customer Satisfaction (CSAT)

**Question**:
```text
"How satisfied are you with [product/feature/experience]?"

1 = Very Unsatisfied
2 = Unsatisfied
3 = Neutral
4 = Satisfied
5 = Very Satisfied
```

**Calculation**:
```text
CSAT = (Satisfied + Very Satisfied) / Total Responses × 100

OR

CSAT = Average Score / 5 × 100
```

**Benchmarks**:
| Score | Interpretation |
|-------|----------------|
| <60% | Poor |
| 60-70% | Acceptable |
| 70-80% | Good |
| >80% | Excellent |

### Customer Effort Score (CES)

**Question**:
```text
"[Company] made it easy for me to [complete task]."

1 (Strongly Disagree) to 7 (Strongly Agree)
```

**Interpretation**:
- High effort = churn predictor
- Low effort = loyalty driver

**Benchmarks**:
| Score | Interpretation |
|-------|----------------|
| <4 | High effort (problem) |
| 4-5 | Moderate effort |
| >5 | Low effort (good) |
| >6 | Very easy (excellent) |

---

## Behavioral Metrics

### Engagement Metrics

| Metric | Definition | Formula |
|--------|------------|---------|
| **DAU** | Daily Active Users | Unique users per day |
| **MAU** | Monthly Active Users | Unique users per month |
| **Stickiness** | Daily engagement | DAU / MAU × 100 |
| **Session Duration** | Time spent per session | End time - Start time |
| **Sessions per User** | Frequency of use | Total sessions / Unique users |
| **Feature Usage** | Which features used | Actions per feature / Total users |

**Stickiness Benchmarks**:
| Stickiness | Interpretation |
|------------|----------------|
| <10% | Low engagement |
| 10-20% | Average |
| 20-30% | Good |
| >30% | Excellent |

### Retention Metrics

| Metric | Definition | Formula |
|--------|------------|---------|
| **Day 1 Retention** | Return next day | Users day 1 / Users day 0 × 100 |
| **Day 7 Retention** | Return after week | Users day 7 / Users day 0 × 100 |
| **Day 30 Retention** | Return after month | Users day 30 / Users day 0 × 100 |
| **Churn Rate** | Users who leave | Churned users / Total users × 100 |

**Retention Benchmarks** (Mobile Apps):
| Metric | Poor | Average | Good | Excellent |
|--------|------|---------|------|-----------|
| Day 1 | <20% | 20-30% | 30-40% | >40% |
| Day 7 | <10% | 10-15% | 15-25% | >25% |
| Day 30 | <5% | 5-10% | 10-15% | >15% |

### Conversion Metrics

| Metric | Definition |
|--------|------------|
| **Activation Rate** | Users who complete key action |
| **Conversion Rate** | Visitors who convert to goal |
| **Trial-to-Paid** | Free users who become paid |
| **Upgrade Rate** | Users who upgrade tier |

**Activation Rate Formula**:
```text
Activation Rate = Users who complete activation event / Total signups × 100

Example activation events:
• Completed onboarding
• Created first [item]
• Invited team member
• Integrated with tool
```

---

## North Star Metrics

### Concept

A single metric that best captures the core value your product delivers to customers.

### North Star Characteristics

- **Measures customer value**: Not just business value
- **Leading indicator**: Predicts long-term success
- **Actionable**: Teams can influence it
- **Understandable**: Everyone knows what it means

### Examples by Product Type

| Product Type | North Star Metric | Why |
|--------------|-------------------|-----|
| **E-commerce** | Weekly purchase rate | Directly ties to revenue and repeat value |
| **SaaS** | Weekly active users using core feature | Shows value realization |
| **Marketplace** | Transactions per week | Both sides getting value |
| **Social** | Daily messages sent | Core engagement activity |
| **Media** | Time spent consuming content | Shows content value |
| **Productivity** | Tasks completed per week | Core value delivery |

### Input Metrics Hierarchy

```text
NORTH STAR METRIC
"Weekly Active Users Who Complete Core Action"
         |
    +----+----+----+
    |         |         |
 Activation  Engagement  Retention
    |         |         |
 • Onboarding  • Feature   • Day 1
   completion    usage      return
 • First       • Session   • Day 7
   action       duration    return
```

### Metric Tree Construction

```text
Step 1: Define North Star
        "Users who find value weekly"

Step 2: Identify Input Metrics
        ├── Acquisition (new users)
        ├── Activation (first value)
        ├── Engagement (ongoing value)
        └── Retention (return for value)

Step 3: Define Actionable Metrics per Input
        Activation:
        ├── Onboarding start rate
        ├── Onboarding completion rate
        ├── Time to first action
        └── First action success rate
```

---

## Metrics Dashboard Design

### Key Metrics Selection

**Rule of 5-7**: Dashboard should show 5-7 key metrics

**Suggested Metrics**:
1. **North Star** (1 metric)
2. **Task Success** (1-2 metrics)
3. **User Satisfaction** (1 metric: SUS or NPS)
4. **Engagement** (1-2 metrics)
5. **Retention** (1 metric)

### Visualization Best Practices

| Metric Type | Best Visualization |
|-------------|-------------------|
| Single number | Big number with trend arrow |
| Over time | Line chart |
| Breakdown | Stacked bar or pie |
| Comparison | Bar chart |
| Progress | Progress bar or gauge |
| Distribution | Histogram |

### Alerting Thresholds

```text
ALERT LEVELS

Critical (immediate action):
• Task success <60%
• NPS <0
• Day 1 retention <15%
• Error rate >10%

Warning (investigate):
• Task success 60-70%
• NPS 0-20
• Day 1 retention 15-25%
• Error rate 5-10%

Healthy:
• Task success >70%
• NPS >30
• Day 1 retention >25%
• Error rate <5%
```

### Trend Analysis

```text
TREND INTERPRETATION

Week-over-Week Change:
• >10% increase: Strong positive trend (up)
• 5-10% increase: Moderate positive trend (up)
• -5% to +5%: Stable (flat)
• 5-10% decrease: Moderate negative trend (down)
• >10% decrease: Investigate immediately (down)

Consider:
• Seasonality (holidays, weekdays)
• Release correlation
• External factors (competitor launch, press)
```

---

## Metrics Selection Decision Tree

```text
What do you need to measure?
    |
    +-- Task performance?
    |   +-- Did they succeed? -> Task Success Rate
    |   +-- How long? -> Time on Task
    |   +-- What went wrong? -> Error Rate
    |   +-- How easy? -> SEQ (post-task)
    |
    +-- Overall satisfaction?
    |   +-- Quick pulse? -> UMUX-Lite (2 questions)
    |   +-- Comprehensive? -> SUS (10 questions)
    |   +-- Loyalty prediction? -> NPS
    |   +-- Effort assessment? -> CES
    |
    +-- User behavior?
    |   +-- How often they use? -> DAU/MAU, Stickiness
    |   +-- How deeply they use? -> Feature usage, Session duration
    |   +-- Do they come back? -> Retention (D1/D7/D30)
    |   +-- Do they convert? -> Conversion rate
    |
    +-- Product success?
        +-- Core value delivery -> North Star
        +-- Health check -> HEART framework
```

---

## Benchmarking Resources

### Industry Benchmark Sources

| Source | What They Provide | URL |
|--------|-------------------|-----|
| Baymard Institute | E-commerce UX benchmarks | baymard.com |
| MeasuringU | SUS percentiles, UX benchmarks | measuringu.com |
| Mixpanel Benchmarks | Mobile/web engagement | mixpanel.com/benchmarks |
| Amplitude | Product analytics benchmarks | amplitude.com |
| UserTesting | Industry NPS data | usertesting.com |

### Creating Internal Benchmarks

```text
BASELINE ESTABLISHMENT PROCESS

1. Measure current state (2-4 weeks of data)
2. Calculate baseline metrics
3. Set targets (realistic improvement)
4. Track weekly/monthly
5. Review and adjust quarterly

Target Setting:
• Aggressive: Top quartile of industry
• Moderate: Industry average
• Conservative: 10-20% improvement from baseline
```
