# A/B Testing Implementation Guide

Comprehensive guide to designing, running, and analyzing A/B tests.

**Last Updated**: January 2026
**References**: [Google Experimentation](https://research.google/), [Netflix Experimentation](https://netflixtechblog.com/), [Statsig Documentation](https://docs.statsig.com/)

---

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

**Quick Reference Table**

| Baseline CR | MDE 10% | MDE 15% | MDE 20% |
|-------------|---------|---------|---------|
| 1% | 78,000 | 34,700 | 19,500 |
| 2% | 38,500 | 17,100 | 9,600 |
| 3% | 25,400 | 11,300 | 6,400 |
| 5% | 15,000 | 6,700 | 3,800 |
| 10% | 7,200 | 3,200 | 1,800 |
| 20% | 3,400 | 1,500 | 850 |
| 30% | 2,100 | 950 | 530 |

*Per variant, 95% confidence, 80% power*

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
| Statsig | Full platform | Modern teams, good free tier |
| LaunchDarkly | Feature flags + experiments | DevOps-heavy teams |
| Optimizely | Full platform | Enterprise, visual editor |
| VWO | Full platform | Non-technical users |
| GrowthBook | Open source | Data teams, warehouse-native |
| Google Optimize | Free (sunset) | Small teams (deprecated) |
| Amplitude | Analytics + experiments | Product analytics users |

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

## Related Resources

- [CRO Framework](../../software-ui-ux-design/references/cro-framework.md) - Conversion optimization
- [UX Metrics Framework](ux-metrics-framework.md) - Metric selection
- [Research Frameworks](research-frameworks.md) - Qualitative methods
