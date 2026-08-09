# A/B Testing Implementation Guide

Comprehensive guide to designing, running, and analyzing A/B tests.

**References**: [Google Experimentation](https://research.google/), [Netflix Experimentation](https://netflixtechblog.com/), [Statsig Documentation](https://docs.statsig.com/)

---
## Table of Contents

- [A/B Testing Fundamentals](#ab-testing-fundamentals)
- [When to A/B Test](#when-to-ab-test)
- [A/B Test Types](#ab-test-types)
- [Test Design](#test-design)
- [Hypothesis Framework](#hypothesis-framework)
- [Sample Size Calculation](#sample-size-calculation)
- [Runtime Calculation](#runtime-calculation)
- [Implementation](#implementation)
- [Technical Setup](#technical-setup)
- [Randomization Requirements](#randomization-requirements)
- [Experiment Configuration](#experiment-configuration)
- [Experiment config example](#experiment-config-example)
- [Analysis](#analysis)
- [Statistical Methods](#statistical-methods)
- [Metric Calculations](#metric-calculations)
- [Result Interpretation](#result-interpretation)
- [Common Pitfalls](#common-pitfalls)
- [Peeking Problem](#peeking-problem)
- [Multiple Comparisons](#multiple-comparisons)
- [Simpson's Paradox](#simpsons-paradox)
- [Sample Ratio Mismatch (SRM)](#sample-ratio-mismatch-srm)
- [Novelty/Primacy Effects](#noveltyprimacy-effects)
- [Experimentation Maturity](#experimentation-maturity)
- [Level 1: Ad-hoc Testing](#level-1-ad-hoc-testing)
- [Level 2: Standardized Process](#level-2-standardized-process)
- [Level 3: Automated Platform](#level-3-automated-platform)
- [Level 4: Culture of Experimentation](#level-4-culture-of-experimentation)
- [Tools & Platforms](#tools-&-platforms)
- [Experimentation Platforms](#experimentation-platforms)
- [DIY Components](#diy-components)
- [Templates](#templates)
- [Experiment Plan Template](#experiment-plan-template)
- [Experiment: [Name]](#experiment-name)
- [Hypothesis](#hypothesis)
- [Design](#design)
- [Metrics](#metrics)
- [Sample Size](#sample-size)
- [Targeting](#targeting)
- [Timeline](#timeline)
- [Success Criteria](#success-criteria)
- [Risks](#risks)
- [Results Report Template](#results-report-template)
- [Results: [Experiment Name]](#results-experiment-name)
- [Summary](#summary)
- [Key Findings](#key-findings)
- [Segment Analysis](#segment-analysis)
- [Secondary Metrics](#secondary-metrics)
- [Guardrails](#guardrails)
- [Decision](#decision)
- [Learnings](#learnings)
- [Related Resources](#related-resources)


## A/B Testing Fundamentals

### When to A/B Test

```
GOOD CANDIDATES:
- Clear, measurable primary metric
- Sufficient traffic (see sample size)
- Isolated change (not part of larger release)
- Reversible change
- Adequate runtime possible (7+ days)

POOR CANDIDATES:
- Major redesigns (too many variables)
- Legal/compliance changes (must ship)
- Bug fixes (obvious improvement)
- Low-traffic pages (<1000/week)
- Already optimal (marginal gains)
```

### A/B Test Types

| Type | Description | Use Case |
|------|-------------|----------|
| A/B | Control vs. single variant | Simple hypothesis |
| A/B/n | Control vs. multiple variants | Compare alternatives |
| MVT | Multiple variables tested | Complex interactions |
| Bandit | Dynamic allocation | Quick optimization |
| Split URL | Different URLs | Backend changes |

---

## Test Design

### Hypothesis Framework

```
STRUCTURE:
[Observation]
leads us to believe that
[Change]
will cause
[Effect]
for
[Segment]
measured by
[Metric].

EXAMPLE:
We observed that 35% of users abandon checkout at shipping step
leads us to believe that
showing estimated delivery dates on product pages
will cause
increased checkout completion
for
mobile users
measured by
checkout completion rate (+5% MDE).
```

### Sample Size Calculation

**Key Variables**
| Variable | Description | Typical Value |
|----------|-------------|---------------|
| α (alpha) | False positive rate | 0.05 (95% confidence) |
| β (beta) | False negative rate | 0.20 (80% power) |
| MDE | Minimum Detectable Effect | 5-20% relative |
| Baseline | Current conversion rate | Varies |

**Sample Size Formula (per variant)**
```
n = 2 × (Zα + Zβ)² × p(1-p) / (MDE × p)²

Where:
- Zα = 1.96 (for 95% confidence)
- Zβ = 0.84 (for 80% power)
- p = baseline conversion rate
- MDE = minimum detectable effect (as decimal)
```

**Quick Reference Table** (re-derived from the formula above: n = 2×(1.96+0.84)²×p(1−p)/(MDE×p)², rounded up)

| Baseline CR | MDE 10% | MDE 15% | MDE 20% |
|-------------|---------|---------|---------|
| 1% | 155,300 | 69,000 | 38,800 |
| 2% | 76,800 | 34,100 | 19,200 |
| 3% | 50,700 | 22,500 | 12,700 |
| 5% | 29,800 | 13,200 | 7,400 |
| 10% | 14,100 | 6,300 | 3,500 |
| 20% | 6,300 | 2,800 | 1,600 |
| 30% | 3,700 | 1,600 | 900 |

*Per variant, 95% confidence, 80% power. These numbers roughly double the widely-copied "quick reference" figures that circulate in blog posts — verify against a calculator (Evan Miller's, Statsig's, or your own script) before committing traffic; MDE and baseline assumptions swing sample size by 10x across this table.*

### Runtime Calculation

```
Minimum Runtime = Sample Size / Daily Traffic per Variant

Additional Requirements:
- Minimum 7 days (weekly cycle)
- Minimum 2 weeks (recommended)
- Capture full business cycle
- Avoid holidays/anomalies
```

---

## Implementation

### Technical Setup

**Assignment Logic**
```javascript
// Deterministic user assignment
function getVariant(userId, experimentId, variants) {
  const hash = md5(`${userId}:${experimentId}`);
  const bucket = parseInt(hash.substring(0, 8), 16) % 100;

  let cumulative = 0;
  for (const variant of variants) {
    cumulative += variant.percentage;
    if (bucket < cumulative) {
      return variant.name;
    }
  }
  return variants[0].name; // fallback
}
```

**Event Tracking**
```javascript
// Track experiment exposure
trackEvent('experiment_viewed', {
  experiment_id: 'checkout_v2',
  variant: 'treatment',
  user_id: userId,
  session_id: sessionId,
  timestamp: Date.now()
});

// Track conversion
trackEvent('purchase_completed', {
  experiment_id: 'checkout_v2',
  variant: 'treatment',
  user_id: userId,
  order_value: 99.99,
  timestamp: Date.now()
});
```

### Randomization Requirements

```
CRITICAL:
- User sees SAME variant on return
- Assignment before exposure
- Independent of other experiments
- Even distribution verification

CHECKS:
- Sample ratio mismatch (SRM) test
- Pre-experiment metrics balance
- No systematic bias
```

### Experiment Configuration

```yaml
# Experiment config example
experiment:
  id: checkout_v2_delivery_date
  name: Delivery Date on Product Page
  hypothesis: |
    Showing delivery dates on product pages
    will increase checkout completion by 5%

  traffic_allocation: 100%
  variants:
    - name: control
      percentage: 50
    - name: treatment
      percentage: 50

  targeting:
    platform: [web, mobile_web]
    country: [US, CA, UK]
    user_segment: [new_users, returning_users]

  metrics:
    primary: checkout_completion_rate
    secondary:
      - add_to_cart_rate
      - revenue_per_visitor
    guardrail:
      - page_load_time
      - error_rate

  runtime:
    min_days: 7
    max_days: 28
    sample_size_per_variant: 15000

  rollout:
    auto_stop_on_harm: true
    harm_threshold: -5%
```

---

## Analysis

### Statistical Methods

**Frequentist (Traditional)**
```
Hypothesis Test:
- H0: Treatment = Control
- H1: Treatment ≠ Control

Result:
- p-value < 0.05 → Reject H0 (significant)
- p-value ≥ 0.05 → Fail to reject H0

Confidence Interval:
- 95% CI for effect size
- If CI excludes 0 → significant
```

**Bayesian**
```
Output:
- Probability that treatment > control
- Expected effect size distribution
- Risk assessment

Advantages:
- More intuitive interpretation
- Better for low-traffic tests
- Continuous monitoring OK
```

**Variance Reduction (CUPED)**

CUPED — Controlled-experiment Using Pre-Experiment Data — is the standard variance-reduction technique. By regressing the outcome metric on each user's pre-experiment value of the same (or correlated) metric, CUPED removes systematic between-user variation and shrinks the variance of the estimated treatment effect.

```
Y_adjusted = Y - θ × (X_pre - mean(X_pre))
where θ = Cov(Y, X_pre) / Var(X_pre)
```

- **Effect**: commonly cited variance/sample-size reductions are in the 20–50% range for typical metrics (Microsoft's original CUPED work, Deng et al. 2013, reported up to 40–50% for some metrics); reductions above that are possible for highly auto-correlated metrics like spend but are workload-specific — treat any single number as directional and re-measure on your own metric's autocorrelation rather than assuming a fixed percentage.
- **When**: every product experiment with a continuous or count-based primary metric, where pre-experiment data exists for assigned users.
- **Where it lives**: built into Statsig, Eppo, GrowthBook by default; available in Microsoft's internal experimentation platform; implementable manually in Python/R. Verify current vendor feature sets before recommending a specific platform for this capability.
- **Trap**: do not use post-randomisation covariates — that biases the estimate. Pre-experiment window only.

**Sequential testing / mSPRT**

Used for continuous monitoring without inflating false positives. See Common Pitfalls → Peeking Problem below for the design rationale.

### Metric Calculations

**Conversion Rate**
```
CR = Conversions / Visitors

CR_lift = (CR_treatment - CR_control) / CR_control

Standard Error = sqrt(p(1-p) × (1/n_control + 1/n_treatment))
```

**Revenue Per Visitor**
```
RPV = Total Revenue / Visitors

RPV_lift = (RPV_treatment - RPV_control) / RPV_control
```

### Result Interpretation

| Scenario | Interpretation | Action |
|----------|----------------|--------|
| p < 0.05, positive | Significant win | Ship treatment |
| p < 0.05, negative | Significant loss | Keep control |
| p > 0.05, positive trend | Inconclusive | Extend or iterate |
| p > 0.05, negative trend | Inconclusive | Keep control |
| p > 0.05, flat | No effect | Keep simpler option |

---

## Common Pitfalls

### Peeking Problem

```
PROBLEM:
Checking results multiple times inflates false positive rate

EXAMPLE:
- Check at day 3: 14% false positive rate
- Check at day 7: 19% false positive rate
- Check at day 14: 25% false positive rate

SOLUTIONS:
1. Pre-set runtime, don't peek
2. Use sequential testing (SPRT)
3. Use Bayesian methods
4. Apply alpha spending (Pocock, O'Brien-Fleming)
```

### Multiple Comparisons

```
PROBLEM:
Testing multiple metrics increases false positives

EXAMPLE:
- 20 metrics tested
- Expected false positives: 1 (at α=0.05)

SOLUTIONS:
1. Declare ONE primary metric
2. Bonferroni correction: α/n
3. False Discovery Rate (FDR) control
4. Pre-register metrics
```

### Simpson's Paradox

```
PROBLEM:
Overall results hide segment-level reversal

EXAMPLE:
- Overall: Treatment +2%
- Mobile: Treatment -5%
- Desktop: Treatment +8%
- Mobile users increased → masked loss

SOLUTION:
Always segment analysis by device, user type, etc.
```

### Sample Ratio Mismatch (SRM)

```
PROBLEM:
Uneven split indicates implementation bug

CHECK:
- Expected: 50/50
- Actual: 52/48
- Chi-square test: p < 0.001 → SRM detected

CAUSES:
- Bot filtering differences
- Assignment bugs
- Redirect issues
- Caching problems

ACTION:
Invalidate test, fix bug, restart
```

### Novelty/Primacy Effects

```
PROBLEM:
Initial lift fades over time (novelty)
or users need time to adapt (primacy)

DETECTION:
Plot conversion over time by variant
Look for converging/diverging trends

SOLUTION:
Run tests long enough (2+ weeks)
Segment by new vs. returning users
```

---

## Experimentation Maturity

### Level 1: Ad-hoc Testing

```
CHARACTERISTICS:
- One-off tests
- Manual analysis
- No documentation
- Results often ignored

IMPROVEMENTS:
- Test documentation template
- Centralized results tracking
- Basic statistical training
```

### Level 2: Standardized Process

```
CHARACTERISTICS:
- Consistent methodology
- Proper sample sizes
- Pre/post analysis
- Results shared

IMPROVEMENTS:
- Experiment review process
- Central experiment catalog
- Automated statistical checks
```

### Level 3: Automated Platform

```
CHARACTERISTICS:
- Dedicated experimentation tool
- Real-time dashboards
- Automatic significance
- Feature flags integrated

IMPROVEMENTS:
- Sequential testing
- Automated guardrails
- Machine learning for targeting
```

### Level 4: Culture of Experimentation

```
CHARACTERISTICS:
- Most changes tested
- Data-driven decisions
- Rapid iteration
- Learning documented

IMPROVEMENTS:
- Meta-analysis
- Causal inference
- Long-term holdouts
```

---

## Tools & Platforms

### Experimentation Platforms

| Tool | Type | Best For |
|------|------|----------|
| Statsig | Full platform; CUPED, sequential testing built in | Modern product teams; good free tier |
| Eppo | Warehouse-native experimentation; CUPED, CUPAC | Data-team-led experimentation on Snowflake/BigQuery/Databricks |
| GrowthBook | Open source; warehouse-native; CUPED, sequential | Self-hosted, data-team ownership |
| LaunchDarkly | Feature flags + experiments | DevOps-heavy teams; release gating doubles as experimentation |
| Optimizely | Full platform | Enterprise, visual editor |
| VWO | Full platform | Non-technical users |
| Amplitude Experiment | Analytics + experiments | Teams already on Amplitude product analytics |

Note: Google Optimize was sunset in September 2023 and is no longer a viable option. Adobe Target remains a market option but is not listed because it primarily serves Adobe Experience Cloud customers.

### DIY Components

| Component | Tools |
|-----------|-------|
| Assignment | Feature flags, hash-based |
| Tracking | Segment, Mixpanel, GA4 |
| Analysis | Python (scipy, statsmodels), R |
| Visualization | Looker, Tableau, custom |

---

## Templates

### Experiment Plan Template

```markdown
## Experiment: [Name]

### Hypothesis
[Observation] leads us to believe [Change] will cause [Effect]
for [Segment] measured by [Metric].

### Design
- Type: A/B
- Traffic: 100%
- Split: 50/50
- Variants:
  - Control: [Description]
  - Treatment: [Description]

### Metrics
- Primary: [Metric] (MDE: [X]%)
- Secondary: [Metrics]
- Guardrail: [Metrics]

### Sample Size
- Required per variant: [N]
- Daily traffic: [N]
- Minimum runtime: [N] days

### Targeting
- Platform: [All/Web/Mobile]
- User segment: [All/New/Returning]
- Geography: [Countries]

### Timeline
- Start: [Date]
- Decision: [Date]
- Maximum runtime: [Date]

### Success Criteria
- Primary metric +[X]% with p < 0.05
- No guardrail degradation > [X]%

### Risks
- [Risk 1]
- [Risk 2]
```

### Results Report Template

```markdown
## Results: [Experiment Name]

### Summary
- Result: [WIN/LOSS/INCONCLUSIVE]
- Primary metric: [+X%] (p=[X], 95% CI: [X, Y])
- Runtime: [X] days, [N] users

### Key Findings
1. [Finding 1]
2. [Finding 2]

### Segment Analysis
| Segment | Control | Treatment | Lift | Significant |
|---------|---------|-----------|------|-------------|
| All | X% | Y% | +Z% | Yes |
| Mobile | X% | Y% | +Z% | Yes |
| Desktop | X% | Y% | +Z% | No |

### Secondary Metrics
| Metric | Lift | Significant |
|--------|------|-------------|
| [Metric 1] | +X% | Yes |
| [Metric 2] | +X% | No |

### Guardrails
| Metric | Change | Status |
|--------|--------|--------|
| Page load | +50ms | OK |
| Error rate | +0.1% | OK |

### Decision
[Ship treatment / Keep control / Iterate]

### Learnings
[What did we learn? What's next?]
```

---

## ITT vs Per-Protocol Analysis

**Intent-to-Treat (ITT)**: analyze users by assigned variant, regardless of whether they actually received the treatment. Default for confirmatory experiments — preserves the integrity of randomization.

**Per-Protocol (PP)**: analyze only users who received the treatment as designed. Useful diagnostic, but biased for inference.

**Why ITT is the default in consumer products**: caching, network failures, partial exposure, and opt-out features all mean many assigned users never see the change. Filtering them out creates selection bias — the users who consistently received the treatment are not a random sample.

**When PP is informative**:
- Pre-launch readiness: "does the feature work when users actually see it?"
- Feature-engagement subgroup analysis, clearly labeled as exploratory

**Anti-pattern**: shipping decisions on PP results because PP shows a bigger lift. Bigger lift, lower validity. The gap between ITT and PP is usually a signal about product reliability, not about effect size.

---

## SUTVA / Network Interference / Switchback Testing

**SUTVA assumption (Stable Unit Treatment Value Assumption)**: one user's treatment does not affect another user's outcome. Standard user-level A/B testing requires this.

**Where it breaks**:
- Marketplaces (Airbnb, DoorDash): treating one side of the market changes supply/demand for both
- Social products (Spotify shared listening, LinkedIn feed): a treated user's behavior changes what control users see
- Shared resources: ad auction, search ranking, inventory — one variant cannibalizes from the other
- Feed-ranking experiments where impressions are zero-sum

**Detection**: A/A test with cluster-level aggregation; compare pre-period to in-period variance in control; look for correlated outcomes in nominally independent control users.

**Solutions**:
- **Cluster randomization**: randomize by city, metro area, friend-graph component, or ad-set rather than by user
- **Switchback testing**: alternate global treatment assignment by time window (used heavily by DoorDash, Uber, Airbnb for operations experiments). Requires autocorrelation correction in analysis.
- **Synthetic control**: treat one geo, construct a synthetic counterfactual from similar untreated geos
- **Long holdouts**: maintain a small percentage of users who never see any new feature; measure aggregate lift over months to detect diluted effects

**Anti-pattern**: running standard user-level A/B in a marketplace and reporting the result as causal. Network interference typically biases estimated effects by 30–50%, in either direction.

---

## Practical vs Statistical Significance

**Statistical significance**: confidence that the measured effect is non-zero (i.e., not attributable to sampling variance).

**Practical significance**: whether the effect is large enough to justify shipping, maintenance cost, and tech debt.

The **MDE (Minimum Detectable Effect)** is set at the practical floor — the smallest effect that would be worth acting on — not at the smallest effect the statistics can detect. Setting MDE too low produces underpowered-in-practice experiments that detect effects too small to matter.

A statistically significant 0.2% lift at p=0.03 is usually noise wearing a confidence-interval costume. A non-significant 3% lift in the right direction on a high-stakes metric is a reason to iterate, not declare failure.

**Anti-pattern**: declaring a p<0.05 win and shipping without checking whether the effect size clears the cost of ongoing engineering and maintenance. Statistics cannot determine whether a result is worth acting on — business judgment does.

---

## Related Resources

- [CRO Framework](../../software-ui-ux-design/references/cro-framework.md) - Conversion optimization
- [UX Metrics Framework](ux-metrics-framework.md) - Metric selection
- [Research Frameworks](research-frameworks.md) - Qualitative methods
