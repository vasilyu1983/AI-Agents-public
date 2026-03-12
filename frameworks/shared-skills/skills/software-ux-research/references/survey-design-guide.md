# Survey Design Guide — UX Research Methodology (Jan 2026)

Practical guide to designing, distributing, and analyzing surveys for UX research. Covers question types, bias prevention, sampling, statistical confidence, distribution channels, analysis methods, and platform comparison. Surveys are powerful at scale but fragile — bad questions produce bad data.

---

## When to Use Surveys

| Use Surveys When | Avoid Surveys When |
|-----------------|-------------------|
| You need quantitative data at scale (n > 50) | You need to understand "why" (use interviews) |
| Measuring satisfaction, preference, or attitudes | Exploring unknown problem spaces (use discovery research) |
| Benchmarking (NPS, SUS, CSAT) over time | Testing usability of specific flows (use usability tests) |
| Validating qualitative findings with larger sample | You have < 30 potential respondents |
| Segmenting users by behavior or preference | Questions require complex context or demonstration |
| Tracking trends over time (pulse surveys) | Sensitive topics requiring rapport (use interviews) |

---

## Question Types

### Closed-Ended Questions

| Type | Format | When to Use | Analysis |
|------|--------|-------------|----------|
| **Likert scale** | 5 or 7-point agreement scale | Attitudes, satisfaction, agreement | Mean, median, distribution |
| **NPS** | 0-10 likelihood to recommend | Loyalty benchmarking | NPS score (% promoters - % detractors) |
| **SUS** (System Usability Scale) | 10 standardized questions, 5-point scale | Usability benchmarking | SUS score (0-100) |
| **CSAT** | 1-5 satisfaction rating | Transaction-specific satisfaction | Mean, top-2-box % |
| **CES** (Customer Effort Score) | 1-7 effort scale | Task completion ease | Mean, low-effort % |
| **Multiple choice** | Select one from list | Demographics, preferences | Frequency, percentage |
| **Multi-select** | Select all that apply | Feature usage, pain points | Frequency per option |
| **Ranking** | Drag to order | Priority assessment | Rank distribution, average rank |
| **Matrix** | Multiple items on same scale | Batch similar questions efficiently | Mean per row item |
| **Semantic differential** | Scale between two opposite adjectives | Brand perception, UX qualities | Mean position on scale |

### Open-Ended Questions

| Type | Format | When to Use | Analysis |
|------|--------|-------------|----------|
| **Short text** | Single line | Specific factual response | Categorize, quantify themes |
| **Long text** | Multi-line textarea | Detailed feedback, explanations | Thematic analysis, sentiment |
| **Conditional open-end** | "Why?" after a closed question | Context for quantitative response | Pair with closed-end analysis |

### Standard Scales Reference

**Likert 5-Point (Agreement)**:
1. Strongly disagree
2. Disagree
3. Neither agree nor disagree
4. Agree
5. Strongly agree

**Likert 7-Point (Satisfaction)**:
1. Extremely dissatisfied
2. Moderately dissatisfied
3. Slightly dissatisfied
4. Neutral
5. Slightly satisfied
6. Moderately satisfied
7. Extremely satisfied

**NPS** (0-10):
- 0-6: Detractors
- 7-8: Passives
- 9-10: Promoters
- NPS = % Promoters - % Detractors (range: -100 to +100)

**SUS Score Interpretation**:

| SUS Score | Grade | Percentile | Adjective |
|-----------|-------|------------|-----------|
| > 80 | A | 90th+ | Excellent |
| 68-80 | B-C | 50-89th | Good to OK |
| 51-67 | D | 15-49th | Below average |
| < 51 | F | < 15th | Poor |

---

## Question Design: Avoiding Bias

### Common Biases and Fixes

| Bias | Bad Question | Fixed Question |
|------|-------------|---------------|
| **Leading** | "How much did you enjoy our new feature?" | "How would you describe your experience with the new feature?" |
| **Double-barreled** | "How satisfied are you with speed and reliability?" | Split into two questions: speed and reliability separately |
| **Assumption** | "What problems did you have with checkout?" (assumes problems) | "How was your checkout experience?" + conditional follow-up |
| **Social desirability** | "Do you care about accessibility?" (everyone says yes) | "How often do you use screen magnification or VoiceOver?" |
| **Acquiescence** | All statements phrased positively (people agree by default) | Mix positively and negatively worded statements |
| **Recency** | "How was your experience this year?" (they recall last week) | "Think about the last 30 days. How often did you..." |
| **Anchoring** | "On a scale of 1-100, most users rate us 85+. How would you rate us?" | Remove anchor: "On a scale of 1-100, how would you rate..." |

### Question Writing Checklist

- [ ] Single concept per question (no double-barreled)
- [ ] Neutral wording (not leading toward a particular answer)
- [ ] No assumptions about experience embedded in the question
- [ ] Clear timeframe specified ("in the last 30 days", "during your last visit")
- [ ] Answer options are mutually exclusive and collectively exhaustive
- [ ] "Other" or "Not applicable" option included where relevant
- [ ] Scale direction is consistent throughout survey (low → high)
- [ ] No jargon or internal terminology

---

## Survey Length and Completion Rate

### Length vs Completion Benchmarks

| Survey Length | Questions | Typical Completion Rate | Best Use |
|-------------|-----------|------------------------|----------|
| Micro (< 2 min) | 1-5 questions | 80-90% | In-app pulse, NPS, CSAT |
| Short (3-5 min) | 6-15 questions | 60-80% | Feature feedback, satisfaction |
| Medium (5-10 min) | 15-25 questions | 40-60% | Research survey, segmentation |
| Long (10-15 min) | 25-40 questions | 20-40% | Annual survey, comprehensive study |
| Extended (15+ min) | 40+ questions | < 20% | Avoid unless compensated |

### Completion Rate Optimization

| Technique | Impact | Implementation |
|-----------|--------|---------------|
| Progress bar | +10-15% completion | Show "X of Y" or percentage bar |
| Mobile-optimized | +20% on mobile respondents | Responsive layout, large tap targets |
| Save and continue | Prevents loss of partial responses | Email link to resume |
| Estimated time | Sets expectation, reduces abandonment | "This takes about 4 minutes" |
| Skip logic | Reduces irrelevant questions | Show questions based on prior answers |
| Incentives | +15-30% response rate | Gift card, charity donation, early access |
| Personalization | +5-10% open rate | "Hi [Name], we'd love your feedback on..." |

---

## Sampling Strategy

### Sampling Methods

| Method | How It Works | Best For | Risk |
|--------|-------------|----------|------|
| **Random** | Every user has equal probability of selection | Large user base, general insights | May under-represent small segments |
| **Stratified** | Random within defined segments | Ensuring segment representation | Requires known segment sizes |
| **Convenience** | Available users (in-app intercept, email list) | Quick feedback, iterative research | Selection bias (active users over-represented) |
| **Quota** | Recruit until segment quotas met | Balanced demographic representation | Can be expensive, slower |
| **Purposive** | Deliberately select specific users | Expert feedback, specific persona research | Not generalizable |
| **Snowball** | Participants refer others | Hard-to-reach populations | Homogeneity bias |

### Choosing a Strategy

```text
What do you need?
  ├─ General population insights
  │   └─ Random or stratified sampling
  ├─ Feedback from specific user types
  │   └─ Quota or purposive sampling
  ├─ Quick directional feedback
  │   └─ Convenience (in-app intercept)
  └─ Hard-to-reach users (churned, non-users)
      └─ Panel recruitment or snowball
```

---

## Sample Size Calculation

### Confidence Level Reference

| Confidence Level | Z-Score | Meaning |
|-----------------|---------|---------|
| 90% | 1.645 | 90% chance result reflects true population |
| 95% | 1.960 | Standard for most UX research |
| 99% | 2.576 | High-stakes research |

### Sample Size Table (95% confidence, 50% proportion)

| Margin of Error | Population 500 | Population 5,000 | Population 50,000 | Population 1,000,000+ |
|-----------------|---------------|------------------|-------------------|---------------------|
| ±10% | 81 | 94 | 96 | 97 |
| ±5% | 217 | 357 | 381 | 384 |
| ±3% | 340 | 879 | 1,045 | 1,067 |
| ±1% | 475 | 3,288 | 8,057 | 9,513 |

### Formula

```text
n = (Z² × p × (1 - p)) / E²

Where:
  n = required sample size
  Z = Z-score for confidence level (1.96 for 95%)
  p = estimated proportion (use 0.5 for maximum variability)
  E = margin of error (0.05 for ±5%)

Example: 95% confidence, ±5% margin
  n = (1.96² × 0.5 × 0.5) / 0.05²
  n = (3.8416 × 0.25) / 0.0025
  n = 384.16 → 385 respondents

Adjust for finite population:
  n_adjusted = n / (1 + (n - 1) / N)
  Where N = total population size
```

### Practical Rules of Thumb

| Analysis Type | Minimum n | Comfortable n | Notes |
|--------------|-----------|---------------|-------|
| Overall percentages | 100 | 300-400 | For ±5% margin |
| Segment comparison (2 groups) | 30 per group | 100 per group | Per group, not total |
| Correlation analysis | 50 | 200+ | More = more reliable |
| NPS tracking | 100 | 250+ | Per measurement period |
| SUS scoring | 12 | 40+ | SUS is surprisingly reliable at small n |

---

## Response Bias Types

| Bias | Description | Mitigation |
|------|-------------|------------|
| **Social desirability** | Respondents answer how they think they "should" | Anonymity assurance, indirect questioning |
| **Acquiescence** | Tendency to agree with any statement | Reverse-coded items, mix positive/negative framing |
| **Central tendency** | Avoiding extreme responses | Use 7-point scale (more range) or forced choice |
| **Extreme responding** | Always selecting highest/lowest | Randomize scale direction, include attention checks |
| **Primacy/recency** | First or last options selected more often | Randomize option order |
| **Non-response** | Certain populations don't respond | Compare respondent demographics to known population |
| **Survivorship** | Only active/happy users respond | Actively recruit churned users, add in-context prompts |
| **Demand characteristics** | Users guess what you want to hear | Blind the hypothesis, neutral framing |

### Attention Check Questions

Include 1-2 attention checks in surveys longer than 10 questions:

```text
"For quality purposes, please select 'Somewhat agree' for this question."

Or embedded:
"How often do you use our teleportation feature?"
(If the product has no teleportation feature, flag respondent)
```

Flag or exclude respondents who fail attention checks. Report exclusion rate.

---

## Distribution Channels

### Channel Comparison

| Channel | Response Rate | Bias Risk | Best For | Setup Effort |
|---------|-------------|-----------|----------|-------------|
| **In-app intercept** | 10-30% | Active user bias | Feature-specific feedback, NPS pulse | Medium (SDK/widget) |
| **Email** | 5-15% | Active/engaged user bias | Relationship surveys, annual benchmarks | Low |
| **Post-transaction** | 15-40% | Recent experience bias | CSAT, CES, transactional feedback | Medium |
| **Research panel** | 20-60% | Panel bias (professional respondents) | Specific demographics, non-users | High (cost + recruitment) |
| **Social media** | 1-5% | Self-selection bias | Brand perception, broad audience | Low |
| **SMS** | 15-25% | Mobile user bias | Quick pulse, high-urgency | Medium (opt-in required) |
| **QR code** | 2-10% | Physical location bias | Event feedback, physical product | Low |

### In-App Intercept Best Practices

```text
TIMING:
- After meaningful action (completed task, used feature)
- Not during active workflow (avoid interruption)
- Minimum 3 sessions before first survey
- Maximum frequency: once per 90 days per user

TARGETING:
- Segment by: user type, plan, feature usage, tenure
- Exclude: users who recently completed a survey
- Exclude: users in critical flows (checkout, onboarding)

FORMAT:
- 1-3 questions maximum for intercept
- Single question + optional follow-up is ideal
- Always provide "dismiss" option
- Mobile: bottom sheet format, not modal
```

---

## Analysis Methods

### Quantitative Analysis

| Method | Use Case | Tool |
|--------|----------|------|
| **Descriptive statistics** | Summarize responses (mean, median, mode, std dev) | Spreadsheet, R, Python |
| **Cross-tabulation** | Compare responses across segments | Spreadsheet pivot table, SPSS |
| **Chi-square test** | Test if segment differences are significant (categorical data) | R, Python scipy, SPSS |
| **t-test / ANOVA** | Compare means across groups (continuous data) | R, Python scipy, SPSS |
| **Correlation** | Identify relationships between variables | R, Python, spreadsheet |
| **Regression** | Predict outcome from multiple factors | R, Python statsmodels, SPSS |
| **NPS calculation** | % Promoters - % Detractors | Spreadsheet formula |
| **Top-2-box / Bottom-2-box** | Percentage selecting top or bottom 2 options | Spreadsheet formula |

### Qualitative Analysis (Open-Ended Responses)

| Method | Description | Best For |
|--------|-------------|----------|
| **Thematic coding** | Read responses, assign codes, group into themes | Identifying patterns in feedback |
| **Sentiment analysis** | Classify as positive/neutral/negative | Large volume quick-scan |
| **Word frequency** | Count most common terms | Identifying dominant topics |
| **Affinity mapping** | Group similar responses visually | Team-based analysis session |

### Reporting Template

```text
SURVEY RESULTS: [Survey Name]
Date: [Date range]
Respondents: [n] (response rate: [X]%)
Method: [Distribution channel]
Confidence: [Confidence level, margin of error]

KEY FINDINGS:
1. [Finding with metric]
2. [Finding with metric]
3. [Finding with metric]

SEGMENT DIFFERENCES:
- [Segment A] vs [Segment B]: [difference and significance]

OPEN-ENDED THEMES:
1. [Theme] (mentioned by X% of respondents)
2. [Theme] (mentioned by X% of respondents)

LIMITATIONS:
- [Response bias, sample limitations, etc.]

RECOMMENDATIONS:
1. [Action based on finding]
2. [Action based on finding]
```

---

## Common Survey Anti-Patterns

| Anti-Pattern | Why It Fails | Correct Approach |
|-------------|-------------|------------------|
| **40+ question survey** | Completion rate < 20%, data quality degrades | Max 15-20 questions; split into focused surveys |
| **Leading questions** | Data reflects your hypothesis, not user reality | Neutral wording, peer review questions |
| **No skip logic** | Users answer irrelevant questions, abandon | Show questions based on prior answers |
| **Surveying everyone** | Low signal, high noise | Target specific segments for specific questions |
| **No pilot test** | Ambiguous questions discovered after launch | Test with 5-10 people, iterate before full launch |
| **Asking for features** | Users describe solutions, not problems | Ask about problems, pain points, and outcomes |
| **No incentive for long surveys** | Low response rate, biased toward most engaged | Offer incentive proportional to time commitment |
| **Matrix questions spanning screen** | Respondents satisfice (same answer for all rows) | Max 5 rows per matrix; break up if needed |
| **"How likely are you to use..." without context** | Hypothetical intent ≠ actual behavior | Measure actual behavior where possible |
| **Annual survey only** | Findings stale by time they're acted on | Continuous pulse + annual deep-dive |

---

## Platform Comparison

| Platform | Best For | Strengths | Limitations | Pricing (2026) |
|----------|----------|-----------|-------------|----------------|
| **Typeform** | Beautiful conversational surveys | High completion rates, conversational format, branching | Limited analysis, expensive at scale | Free (10 resp/mo), $25-83/mo |
| **SurveyMonkey** | Established teams, enterprise | Templates, team features, benchmarking, compliance | UI dated, costly for advanced features | Free (basic), $25-75+/mo |
| **Qualtrics** | Academic/enterprise research | Advanced logic, conjoint analysis, stats, panels | Expensive, steep learning curve | Enterprise pricing ($$$$) |
| **Google Forms** | Zero budget, simple surveys | Free, simple, integrates with Sheets | No branching logic, basic analysis | Free |
| **Hotjar Surveys** | In-app feedback | Integrated with heatmaps/recordings, easy targeting | Limited question types, no advanced analysis | Free (basic), $32-171/mo |
| **Maze** | UX research integration | Surveys + usability tests in one tool, prototype testing | Smaller survey feature set | $0-99/mo |
| **Lyssna** | UX research focus | Surveys + card sorts + tree tests, participant panel | Niche, smaller community | $75-175/mo |
| **Prolific** | Participant recruitment | Academic-grade panel, demographic targeting | Platform for recruitment, not survey hosting | Pay per participant |

### Selection Decision

```text
What's your primary need?
  ├─ Quick, free, simple
  │   └─ Google Forms
  ├─ Beautiful surveys, high completion rate
  │   └─ Typeform
  ├─ In-app survey integrated with analytics
  │   └─ Hotjar
  ├─ UX research with surveys as one method
  │   └─ Maze or Lyssna
  ├─ Enterprise with compliance requirements
  │   └─ SurveyMonkey or Qualtrics
  ├─ Academic research with complex methodology
  │   └─ Qualtrics
  └─ Need participants, not just a survey tool
      └─ Prolific (recruit) + any survey tool (host)
```

---

## References

- [Dillman, Don A. Internet, Phone, Mail, and Mixed-Mode Surveys. Wiley, 2014.](https://www.wiley.com/en-us/Internet,+Phone,+Mail,+and+Mixed-Mode+Surveys-p-9781118456149)
- [Nielsen Norman Group — Survey Design](https://www.nngroup.com/articles/survey-design/)
- [Qualtrics — Survey Best Practices](https://www.qualtrics.com/experience-management/research/survey-design/)
- [SUS — System Usability Scale (Brooke, 1996)](https://digital.ahrq.gov/sites/default/files/docs/survey/systemusabilityscale%28sus%29_comp%5B1%5D.pdf)
- [SurveyMonkey — Sample Size Calculator](https://www.surveymonkey.com/mp/sample-size-calculator/)

---

## Cross-References

- [SKILL.md](../SKILL.md) — Parent skill overview, method selection table
- [ux-metrics-framework.md](ux-metrics-framework.md) — NPS, SUS, HEART metrics that surveys measure
- [ab-testing-implementation.md](ab-testing-implementation.md) — Sample size concepts shared with survey methodology
- [research-repository-management.md](research-repository-management.md) — Storing and reusing survey findings
- [demographic-research-methods.md](demographic-research-methods.md) — Inclusive survey design for diverse populations
