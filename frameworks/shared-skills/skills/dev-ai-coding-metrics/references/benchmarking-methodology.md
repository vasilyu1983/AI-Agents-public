# Benchmarking Methodology for AI Coding Impact

Study designs, statistical methods, confound management, and reporting structures for measuring AI coding tool impact with rigor.

---

## A/B Team Comparison

The strongest causal design when you have enough teams. Two comparable groups: one uses AI tools (treatment), one does not (control).

### Team Selection Criteria

Match teams on these dimensions:

| Dimension | How to Match | Tolerance |
|-----------|-------------|-----------|
| Team size | Same +/- 1 person | Strict |
| Avg seniority | Within 1 year of experience | Moderate |
| Tech stack | Same primary language and framework | Strict |
| Project type | Same lifecycle stage (greenfield, growth, maintenance) | Strict |
| Historical velocity | Within 20% of each other (past 3 months) | Moderate |
| Code complexity | Similar cyclomatic complexity per repo | Moderate |
| Team tenure | How long they've worked together | Moderate |

### Assignment

- **Random assignment** is ideal but rarely practical. At minimum, do not let teams self-select.
- **Stratified assignment**: If you have 6+ teams, stratify by project type and randomly assign within strata.
- **Avoid**: Assigning the "best" team to treatment (guarantees confounded results).

### Duration

| Phase | Duration | Purpose |
|-------|----------|---------|
| Pre-measurement baseline | 4 weeks minimum | Establish comparable starting metrics |
| Phase 1 (treatment) | 8 weeks minimum | Treatment team uses AI tools; control does not |
| Washout (optional) | 2 weeks | Both teams pause AI usage |
| Phase 2 (crossover) | 8 weeks | Teams swap: former control gets AI tools |

Total: 20-24 weeks for a crossover design.

**Why 8 weeks minimum**: Weeks 1-3 are adoption ramp (noise). Weeks 4-8 represent stabilized usage. Shorter studies measure novelty, not impact.

### Crossover Design

Each team serves as its own control, which dramatically increases statistical power.

```
          Week 1-8         Week 9-10       Week 11-18
Team A:   AI tools         Washout         No AI tools
Team B:   No AI tools      Washout         AI tools

Analysis: Compare each team's AI period to its non-AI period.
          Also compare Team A's AI period to Team B's non-AI period.
```

Advantages:
- Controls for team-level confounds (skill, culture, codebase)
- Requires fewer teams for same statistical power
- More palatable than permanently denying tools to a group

Disadvantages:
- Learning effects (Team A may retain AI skills during non-AI period)
- Longer total study duration
- Cannot fully "un-learn" AI-assisted patterns

### Metrics to Collect

Collect all of these for both teams in both periods:

**Primary metrics** (must have):
- Cycle time (commit to deploy)
- Throughput (story points or tasks completed per sprint)
- Defect rate (bugs per 100 commits or per feature)
- Code review turnaround time

**Secondary metrics** (should have):
- Lines of code (context only, not as a productivity measure)
- Test coverage delta
- PR size and frequency
- Developer satisfaction survey (pre and post each phase)

**Tertiary metrics** (nice to have):
- Cognitive load assessment
- Context switch frequency
- Time spent on specific task categories

### Statistical Analysis

- **Primary test**: Mixed-effects model with team as random effect and treatment as fixed effect
- **Simpler alternative**: Paired t-test on team-period averages (if crossover design)
- **Report**: Effect size (Cohen's d), 95% confidence interval, p-value
- **Minimum detectable effect**: Calculate before starting (see Statistical Rigor section)

---

## Before/After Study Design

When you cannot withhold AI tools from any team. Compare the same team's performance before and after AI tool adoption.

### Baseline Establishment

```
BASELINE PERIOD:
  Minimum: 8 weeks
  Recommended: 12 weeks
  Purpose: Establish stable pre-AI metrics

REQUIREMENTS:
  - No major process changes during baseline
  - No team composition changes
  - Normal project work (not a release crunch or lull)
  - Collect the same metrics you'll measure post-intervention
```

**Common mistake**: Starting baseline measurement the week you announce AI tools are coming. Anticipation effects distort the baseline.

### Intervention Period

| Phase | Duration | Notes |
|-------|----------|-------|
| Rollout and training | 2-4 weeks | Not counted in post-measurement |
| Ramp-up | 4-6 weeks | Usage stabilizing, some measurement |
| Stabilized usage | 8+ weeks | Primary measurement period |

Do not compare baseline to ramp-up period. Compare baseline to stabilized period only.

### Interrupted Time Series Analysis

The gold standard for before/after designs. Requires frequent metric observations (weekly minimum).

```
APPROACH:
1. Plot weekly metric values for entire study period
2. Mark the intervention point (AI tool rollout)
3. Fit a regression model:
   Y = β0 + β1(time) + β2(intervention) + β3(time × intervention) + ε

INTERPRETATION:
  β1: Pre-existing trend (was the metric already improving?)
  β2: Immediate effect of intervention (level change)
  β3: Change in trend after intervention (slope change)
```

If β1 shows the metric was already improving before AI tools, the post-intervention improvement may not be attributable to AI tools.

### Controlling for Seasonal Effects

Software teams have predictable rhythms:

- **Sprint boundaries**: Velocity spikes at sprint end
- **Quarter-end**: Release pressure distorts metrics
- **Holidays**: Reduced capacity
- **Annual planning**: Strategy work displaces coding
- **Hiring cycles**: New team members reduce velocity temporarily

**Mitigation**: Compare same calendar period year-over-year if possible, or use seasonal adjustment in time series models.

### Multiple Baseline Design

Stagger AI tool rollout across teams:

```
           Month 1-2    Month 3-4    Month 5-6    Month 7-8
Team A:    Baseline     AI tools →   AI tools     AI tools
Team B:    Baseline     Baseline     AI tools →   AI tools
Team C:    Baseline     Baseline     Baseline     AI tools →

If all teams improve at their specific rollout point (not before),
the effect is more likely causal than coincidental.
```

This is the most rigorous before/after design available without a control group.

---

## Shadow Team Experiments

The most rigorous but most expensive approach: two teams independently complete the same task.

Cross-reference: `dev-context-engineering/references/team-transformation-patterns.md` for the Shadow Team Experiment framework, including setup, evaluation criteria, and documented case studies.

### Design

```
SETUP:
1. Select a meaningful feature or task
   - Not trivial (would take traditional team 2-4 weeks)
   - Not mission-critical (results used for learning, not shipping)
   - Well-defined acceptance criteria

2. Assign two teams:
   - AI-Equipped Team: Full access to AI coding tools
   - Traditional Team: Standard tooling only
   - Teams should NOT know each other's assignment

3. Identical success criteria:
   - Feature completeness (checklist)
   - Test coverage minimums
   - Code quality thresholds (linting, review)
   - Documentation requirements
```

### Blind Evaluation

After both teams deliver:

1. **Strip identifying information**: Remove author names, commit messages that mention tools
2. **Independent reviewers**: 3+ senior engineers who were not on either team
3. **Evaluation rubric**:

| Dimension | Weight | Scale |
|-----------|--------|-------|
| Functional correctness | 25% | 1-5 |
| Code quality and maintainability | 25% | 1-5 |
| Test coverage and quality | 20% | 1-5 |
| Architecture decisions | 15% | 1-5 |
| Documentation | 15% | 1-5 |

4. **Record evaluation time**: How long reviewers spend understanding each codebase (proxy for maintainability)

### Time and Cost Comparison

| Metric | AI-Equipped | Traditional | Difference |
|--------|-------------|-------------|------------|
| Calendar time to completion | X days | Y days | Y - X |
| Total person-hours | A hours | B hours | B - A |
| Fully-loaded cost | $C | $D | $D - $C |
| Tool costs | $E | $0 | -$E |
| Net cost difference | | | ($D - $C) - $E |

### Limitations

- **Expensive**: Duplicating work is a hard sell to leadership
- **Artificial**: Developers know it is an experiment (Hawthorne effect)
- **Small sample**: Usually only 1-2 comparisons feasible (low statistical power)
- **Task-dependent**: Results from one task may not generalize

**When it is worth it**: Major investment decisions (enterprise-wide rollout), or when before/after data is unconvincing.

---

## Statistical Rigor

### Sample Size Calculations

Before running any study, determine how many data points you need.

```
SAMPLE SIZE FORMULA (simplified for two-group comparison):

  n per group = 2 × ((z_α/2 + z_β) / d)²

  Where:
    z_α/2 = 1.96 (for 95% confidence)
    z_β   = 0.84 (for 80% power)
    d     = expected effect size (Cohen's d)

PRACTICAL MINIMUMS:
  Large effect (d = 0.8):   ~26 observations per group
  Medium effect (d = 0.5):  ~64 observations per group
  Small effect (d = 0.2):   ~394 observations per group
```

For team-level comparisons, "observations" = team-sprints. For individual metrics, "observations" = developer-tasks.

**Reality check**: Most organizations cannot get 394 developer-task observations per condition. This means small effects will not be detectable. Plan for detecting medium-to-large effects only.

### Effect Size Estimation

| Metric | Plausible Effect Size | Cohen's d Category |
|--------|----------------------|-------------------|
| Code generation speed | Large (d = 0.8-1.2) | Large |
| Overall sprint velocity | Small-Medium (d = 0.2-0.5) | Small-Medium |
| Bug rate change | Small (d = 0.1-0.3) | Small |
| Developer satisfaction | Medium (d = 0.4-0.7) | Medium |
| Code review time | Medium (d = 0.3-0.6) | Medium |

Use pilot data to estimate effect sizes for your organization. Vendor claims often correspond to d > 1.5, which is implausibly large.

### Confidence Intervals

Report 95% confidence intervals for every metric. A point estimate without a confidence interval is useless.

```
EXAMPLE:
  "AI-assisted developers completed tasks 22% faster
   (95% CI: 12% to 32%, p = 0.003)"

NOT:
  "AI-assisted developers completed tasks 22% faster"
```

Wide confidence intervals (e.g., -5% to 49%) indicate insufficient data. Do not claim an effect exists when the CI includes zero.

### Multiple Comparison Corrections

When testing many metrics simultaneously, some will appear significant by chance.

| Number of Metrics Tested | Expected False Positives (p < 0.05) |
|--------------------------|--------------------------------------|
| 5 | 0.25 (1 in 4 studies) |
| 10 | 0.50 (1 in 2 studies) |
| 20 | 1.0 (expect at least 1) |

**Bonferroni correction**: Divide significance threshold by number of tests. If testing 10 metrics, use p < 0.005 instead of p < 0.05.

**Better approach**: Pre-register 2-3 primary metrics. Report others as exploratory.

### Power Analysis

```
MINIMUM STANDARD: β = 0.80 (80% power)

Interpretation: If the effect is real, you have an 80% chance of
detecting it. 20% chance of a false negative.

For high-stakes decisions: β = 0.90 (90% power)

PRACTICAL IMPACT:
  At 80% power, 1 in 5 real effects go undetected.
  At 90% power, 1 in 10 real effects go undetected.
  At 50% power (common in underpowered studies), HALF of real
  effects go undetected.
```

Run power analysis before the study to determine if you have enough data. If not, either extend the study or accept that you can only detect large effects.

### Practical vs Statistical Significance

A result can be statistically significant but practically meaningless (and vice versa).

```
EXAMPLE OF STATISTICALLY SIGNIFICANT BUT PRACTICALLY MEANINGLESS:
  "AI tools reduced cycle time by 12 minutes per task
   (95% CI: 3-21 minutes, p = 0.01)"

  If tasks take 8 hours on average, 12 minutes is a 2.5% improvement.
  Statistically real, but not worth the investment.

EXAMPLE OF PRACTICALLY SIGNIFICANT BUT STATISTICALLY UNCERTAIN:
  "AI tools reduced cycle time by 2 hours per task
   (95% CI: -0.5 to 4.5 hours, p = 0.11)"

  Potentially large effect, but insufficient data to confirm.
  Gather more data before deciding.
```

Define practical significance thresholds before the study: "We need at least X% improvement to justify the investment."

---

## Confounding Variable Management

### Developer Skill Level

The most common confound. Higher-skill developers adopt AI tools faster and are more productive regardless.

**Controls**:
- **Stratified analysis**: Report results separately for junior, mid, senior
- **Matched pairs**: Compare each developer to their own baseline (before/after)
- **Covariate adjustment**: Include years of experience in statistical models
- **Random assignment**: If possible, randomly assign developers to conditions within skill strata

### Task Complexity

AI tools excel at routine tasks and struggle with complex ones. If AI-equipped teams get easier tasks, results are confounded.

**Standardized task classification**:

| Complexity Level | Characteristics | Example |
|-----------------|-----------------|---------|
| C1: Routine | Well-defined, repetitive, boilerplate | CRUD endpoint, unit tests |
| C2: Standard | Some judgment required, established patterns | Feature implementation with clear spec |
| C3: Complex | Architecture decisions, multiple systems | API redesign, performance optimization |
| C4: Novel | No precedent, research required | New algorithm, unfamiliar domain |

Report results by complexity level. If AI shows gains only at C1-C2, that is an honest and useful finding.

### Project Lifecycle Stage

| Stage | AI Impact Profile |
|-------|------------------|
| Greenfield | Highest AI leverage; scaffolding, boilerplate, rapid prototyping |
| Active growth | High leverage; feature development, test generation |
| Mature/maintenance | Moderate leverage; bug fixes, refactoring, documentation |
| Legacy rescue | Low leverage; AI lacks context, outdated patterns |

Compare AI impact only within the same lifecycle stage. Greenfield-vs-maintenance comparisons are meaningless.

### Team Dynamics and Collaboration

- **Pair programming teams** may see different AI impact than solo developers
- **Code review culture** affects whether AI-generated bugs are caught
- **Communication overhead** varies with team size and distribution
- **Psychological safety** affects willingness to experiment with new tools

**Control**: Include team dynamics measures in your analysis. At minimum, track team size, co-location, and existing collaboration patterns.

### External Factors

| Factor | How It Confounds | Mitigation |
|--------|-----------------|------------|
| Market pressure / deadline | Teams work harder during crunch | Exclude crunch periods from analysis |
| Org restructuring | Disrupts teams regardless of AI | Note and control for in analysis |
| Major incidents / outages | Divert attention from feature work | Exclude affected sprints |
| New team members | Onboarding reduces velocity | Track team composition stability |
| Tech debt paydown | Planned maintenance skews metrics | Tag and separate from feature work |

### Tool Version Changes

AI tools update frequently. A mid-study tool update can:
- Improve results (making the tool look better than baseline)
- Degrade results (introducing new bugs or changing UX)
- Invalidate comparisons (before and after are measuring different tools)

**Mitigation**: Lock tool versions during study periods if possible. If not, document version changes and note them in the analysis.

---

## Reporting Structure

### Executive Summary

```
TEMPLATE (1 page):

STUDY: [Name/description]
PERIOD: [Start] to [End]
DESIGN: [A/B comparison | Before/after | Shadow team]
TEAMS: [N teams, N developers]

KEY FINDING:
[One sentence: what did we learn?]

PRIMARY METRICS:
| Metric           | Treatment | Control | Difference | 95% CI        |
|------------------|-----------|---------|------------|---------------|
| [Primary 1]      | X         | Y       | +Z%        | [low, high]   |
| [Primary 2]      | X         | Y       | +Z%        | [low, high]   |

RECOMMENDATION: [Continue / Expand / Modify / Pause]
CONFIDENCE: [High / Medium / Low] based on [rationale]
```

### Detailed Methodology Section

Include enough detail for replication:

1. **Study design** with justification for chosen approach
2. **Team/participant selection** criteria and process
3. **Timeline** with phases and durations
4. **Metrics** collected, data sources, collection frequency
5. **Statistical methods** used, software/tools, pre-registration status
6. **Deviations** from original plan and why

### Results with Confidence Intervals

Every metric reported must include:
- Point estimate
- 95% confidence interval
- Sample size
- Effect size (Cohen's d or equivalent)
- p-value (but emphasize CI over p-value)

Present results in tables with consistent formatting. Include visualizations (before/after trend lines, forest plots for multiple metrics).

### Limitations and Threats to Validity

Be explicit. Credibility comes from honesty about limitations.

| Threat | Severity | Mitigation Applied | Residual Risk |
|--------|----------|-------------------|---------------|
| Selection bias | High/Med/Low | [What you did] | [What remains] |
| Hawthorne effect | High/Med/Low | [What you did] | [What remains] |
| Small sample size | High/Med/Low | [What you did] | [What remains] |
| Confounding variables | High/Med/Low | [What you did] | [What remains] |

### Recommendations with Evidence Strength

Rate each recommendation by evidence quality:

| Strength | Meaning | Basis |
|----------|---------|-------|
| **Strong** | High confidence, act on this | Multiple metrics, large effect, narrow CI |
| **Moderate** | Likely true, proceed with monitoring | Consistent direction, moderate CI width |
| **Preliminary** | Suggestive, needs more data | Trend in expected direction, wide CI |
| **Insufficient** | Cannot conclude | Conflicting results, very wide CI, too few observations |

### Replication Guidelines

Enable others to repeat the study:

- Exact tool versions and configurations used
- Survey instruments (full question text)
- Data collection scripts or procedures
- Analysis code or statistical procedures
- Raw data (anonymized) if organizational policy allows
- Known limitations that affect reproducibility

```
REPLICATION CHECKLIST:
[ ] Study design documented with decision rationale
[ ] Team selection criteria and process recorded
[ ] All metrics defined with precise measurement methods
[ ] Data collection timeline and tools specified
[ ] Statistical analysis plan documented before data collection
[ ] Deviations from plan recorded with justification
[ ] Raw data preserved (anonymized) for re-analysis
[ ] Analysis code/procedures documented for reproducibility
```
