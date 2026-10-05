# Survey Design Guide — UX Research Methodology

Practical guide to designing, distributing, and analyzing surveys for UX research. Covers question types, bias prevention, sampling, statistical confidence, distribution channels, analysis methods, and platform comparison. Surveys are powerful at scale but fragile — bad questions produce bad data.

---
## Table of Contents

- [When to Use Surveys](#when-to-use-surveys)
- [Question Types](#question-types)
- [Closed-Ended Questions](#closed-ended-questions)
- [Open-Ended Questions](#open-ended-questions)
- [Standard Scales Reference](#standard-scales-reference)
- [Question Design: Avoiding Bias](#question-design-avoiding-bias)
- [Common Biases and Fixes](#common-biases-and-fixes)
- [Question Writing Checklist](#question-writing-checklist)
- [Construct Validity: Measuring What Cannot Be Measured Directly](#construct-validity-measuring-what-cannot-be-measured-directly)
- [Latent Constructs vs Direct Measures](#latent-constructs-vs-direct-measures)
- [The Validity Ladder](#the-validity-ladder)
- [A Construct That Failed Validity Testing](#a-construct-that-failed-validity-testing)
- [Bad-Question Failure Modes](#bad-question-failure-modes)
- [The Analysis Ladder](#the-analysis-ladder)
- [Survey Length and Completion Rate](#survey-length-and-completion-rate)
- [Length vs Completion Benchmarks](#length-vs-completion-benchmarks)
- [Completion Rate Optimization](#completion-rate-optimization)
- [Sampling Strategy](#sampling-strategy)
- [Sampling Methods](#sampling-methods)
- [Choosing a Strategy](#choosing-a-strategy)
- [Sample Size Calculation](#sample-size-calculation)
- [Confidence Level Reference](#confidence-level-reference)
- [Sample Size Table (95% confidence, 50% proportion)](#sample-size-table-95-confidence-50-proportion)
- [Formula](#formula)
- [Practical Rules of Thumb](#practical-rules-of-thumb)
- [Response Bias Types](#response-bias-types)
- [Attention Check Questions](#attention-check-questions)
- [Survey Integrity: Fraud, Bots, and Speeders](#survey-integrity-fraud-bots-and-speeders)
- [Distribution Channels](#distribution-channels)
- [Channel Comparison](#channel-comparison)
- [In-App Intercept Best Practices](#in-app-intercept-best-practices)
- [Analysis Methods](#analysis-methods)
- [Quantitative Analysis](#quantitative-analysis)
- [Qualitative Analysis (Open-Ended Responses)](#qualitative-analysis-open-ended-responses)
- [Reporting Template](#reporting-template)
- [Common Survey Anti-Patterns](#common-survey-anti-patterns)
- [Platform Comparison](#platform-comparison)
- [Selection Decision](#selection-decision)
- [References](#references)
- [Cross-References](#cross-references)


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

Sauro-Lewis curved grading scale (Sauro & Lewis, *Quantifying the User Experience*; [MeasuringU](https://measuringu.com/interpret-sus-score/)). The average SUS score (about 68) is a **C**, not a B.

| SUS Score | Grade | Percentile |
|-----------|-------|------------|
| 84.1-100 | A+ | 96-100 |
| 80.8-84.0 | A | 90-95 |
| 78.9-80.7 | A- | 85-89 |
| 77.2-78.8 | B+ | 80-84 |
| 74.1-77.1 | B | 70-79 |
| 72.6-74.0 | B- | 65-69 |
| 71.1-72.5 | C+ | 60-64 |
| 65.0-71.0 | C | 41-59 |
| 62.7-64.9 | C- | 35-40 |
| 51.7-62.6 | D | 15-34 |
| 0-51.6 | F | 0-14 |

Do not mix these grades with Bangor's adjective scale ("Excellent", "OK", "Poor"), which uses different cut-offs.

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

## Construct Validity: Measuring What Cannot Be Measured Directly

Some things can be measured directly — the response time of a page, the count of clicks. Attitudes, trust, perceived effort, and culture cannot. Those require a **latent construct**: several survey items (called *manifest variables*) that each capture one aspect of the underlying idea, combined into a single score. Source for the framing and the worked examples below: Forsgren, Humble & Kim, *Accelerate* (IT Revolution, 2018), Ch. 13 (printed pp. 183–196) and Ch. 12 (pp. 170–182).

### Latent Constructs vs Direct Measures

| Aspect | Direct measure | Latent construct |
| ------ | -------------- | ---------------- |
| Example | Page load time, task completion rate | Perceived usability, trust, team culture |
| Instrument | One measurement | Several items, averaged |
| Failure mode | Instrument breaks silently | One bad item is outvoted by the others |
| Analysis unit | The measure itself | The construct, never a single item |

The point of using several items is defensive. *Accelerate* names three benefits: constructs force you to define what you are measuring; they give several views into the same behavior so rogue data is visible; and they make it harder for a single bad respondent or misread item to skew the result. Note that "all measures are proxies" — this applies to system telemetry as much as to surveys. Response time is a proxy for performance whether or not you say so.

Asking "Is your culture good?" fails on both halves: the respondent picks their own definition of *culture*, and *good* is undefined. Define the construct first, then write one item per facet.

### The Validity Ladder

Run these before any correlation, regression, or segment comparison. Each rules out a specific way the instrument can be wrong.

| Test | Definition (verbatim, *Accelerate* Ch. 13) | What it rules out |
| ---- | ------------------------------------------ | ----------------- |
| **Discriminant validity** | "tests to make sure that items that are not supposed to be related are actually unrelated" | Your items are quietly measuring something else too — the construct is contaminated by an adjacent concept |
| **Convergent validity** | "tests to make sure that items that are supposed to be related are actually related" | Your items do not hang together — you have several small constructs, not one |
| **Reliability** (internal consistency) | "provides assurance that the items are read and interpreted similarly by those who take the survey" | Respondents are interpreting the same wording differently, so the average is noise |

Reliability is conventionally reported as **Cronbach's alpha** — the standard internal-consistency coefficient. Higher alpha means the items are answered more consistently as a set; it does *not* certify that the set measures the right thing, which is what the two validity tests are for. A construct can be highly reliable and still measure the wrong concept.

Together, validity and reliability "confirm our measures. They come before any analysis." Re-run them periodically, not once — *Accelerate* recommends reassessing "especially if you suspect a change in the system or environment."

### A Construct That Failed Validity Testing

*Accelerate* reports a **failure-notification** construct that did not survive testing (Ch. 13, printed pp. 193–194). The original five items were:

- We are primarily notified of failures by reports from customers.
- We are primarily notified of failures by the NOC.
- We get failure alerts from logging and monitoring systems.
- We monitor system health based on threshold warnings (ex. CPU exceeds 90%).
- We monitor system health based on rate-of-change warnings (ex. CPU usage has increased by 25% over the last 10 minutes).

In a pilot with about 20 technical professionals the items loaded together. On the full dataset they did not: "when we ran our statistical tests, they did not confirm a single construct, but instead revealed two constructs." The first two items measured "notifications that come from outside of automated processes"; the remaining three measured "notifications that come from systems" or "proactive failure notification." The single construct was dropped and replaced by the split.

Two lessons. First, a small pilot can pass an instrument that a full sample rejects — pilots check comprehension, not structure. Second, the split was the finding: only after separating them could the authors report that proactive failure notification "is a technical capability that is predictive of software delivery performance." A merged construct would have averaged the two apart.

*Accelerate* has a second example of the same discipline. Its delivery-performance construct was intended to combine four metrics — lead time, release frequency, time to restore service, and change fail rate — but "the four measures don't pass all of the statistical tests of validity and reliability." Only three formed a valid, reliable construct, and change fail rate was reported separately thereafter. When a measure you *want* in the construct will not load, drop it from the construct and report it on its own.

### Bad-Question Failure Modes

These break the construct before any statistic runs. The table in [Common Biases and Fixes](#common-biases-and-fixes) covers the same ground for individual questions; these are the four *Accelerate* names explicitly (Ch. 13, printed p. 185):

| Failure mode | Definition | Book's example |
| ------------ | ---------- | -------------- |
| **Leading** | Biases the respondent toward a direction | "Was Napoleon short?" — use "How would you describe Napoleon's height?" |
| **Loaded** | Forces an answer that isn't true for the respondent | "Where did you take your certification exam?" assumes they took one |
| **Multiple questions in one** (double-barreled) | Asks two things, so the answer is uninterpretable | "Are you notified of failures by your customers and the NOC?" — customers? the NOC? both? neither? |
| **Unclear language** | Terms the respondent does not share | Use language respondents are familiar with; clarify and give examples |

Note that the double-barreled example is the failure-notification construct's own subject matter, split correctly into separate items — that is what the two-item/three-item separation above is doing.

Push polls are the extreme case: questions "difficult to answer honestly unless you already agree with the 'researcher's' point of view." Internal surveys reach this by accident when the writer already knows the answer they want.

### The Analysis Ladder

Never analyze a single item as if it were a construct. *Accelerate* orders analysis by increasing complexity (Ch. 12, after Leek 2013): **descriptive → exploratory → inferential predictive → predictive → causal → mechanistic**. Their research covers only the first three, plus classification.

Practical rules for survey work:

1. **Validate before you analyze.** Discriminant validity, convergent validity, reliability — then correlations.
2. **Correlation is the exploratory stage, not the conclusion.** "Correlation looks at how closely two variables move together — or don't — but it doesn't tell us if one variable's movement predicts or causes the movement in another variable." Two variables can move together through a third variable or chance.
3. **Analyze the construct mean, not the items.** Average the item scores (e.g. 1–7) and analyze that. Report item-level distributions only as diagnostics.
4. **Single-item measures buy narrow conclusions only.** Quick surveys "can be useful if they are based on well-written and carefully understood questions. However, it is important that only narrow conclusions are drawn from these types of surveys." NPS is the well-studied exception — carefully developed, well-documented, and comparable across companies precisely because it is standardized; better multi-item satisfaction measures exist, but a single measure is easier to collect.
5. **Say "associated with," not "causes."** Causal analysis "generally requires randomized studies," which most survey work is not.

**Provenance caveat for any *Accelerate* figure.** The findings come from a self-reported, self-selected survey population across four annual collections in the mid-2010s. Direction-of-effect claims rest on an inferential-predictive design (theory-driven hypothesis, then test), which the authors distinguish from causal analysis. Quote magnitudes verbatim with their date, or hedge them — do not restate them as current industry constants.

**Ready-made validated construct.** The seven-item Westrum organizational-culture instrument — a worked example of a construct that *did* pass validity and reliability testing — is reproduced with its scoring and caveats in [`references/westrum-culture-measurement.md`](westrum-culture-measurement.md).

---

## Survey Length and Completion Rate

### Length vs Completion Benchmarks

The rates in this table are unsourced house heuristics for planning scenarios, not observed benchmarks. Pilot the actual instrument and report its denominator and measured completion rate.

| Survey Length | Questions | Typical Completion Rate | Best Use |
|-------------|-----------|------------------------|----------|
| Micro (< 2 min) | 1-5 questions | 80-90% | In-app pulse, NPS, CSAT |
| Short (3-5 min) | 6-15 questions | 60-80% | Feature feedback, satisfaction |
| Medium (5-10 min) | 15-25 questions | 40-60% | Research survey, segmentation |
| Long (10-15 min) | 25-40 questions | 20-40% | Annual survey, comprehensive study |
| Extended (15+ min) | 40+ questions | < 20% | Avoid unless compensated |

### Completion Rate Optimization

The impact bands below are unsourced house heuristics for hypothetical planning scenarios. They do not establish an expected uplift or whether the change helps; measure the effect in a controlled comparison before promising a number.

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

Confidence describes repeated-sample interval coverage under the sampling assumptions, not the probability that one survey is correct ([NIST definition](https://csrc.nist.gov/glossary/term/confidence_interval)).

| Confidence Level | Z-Score | Meaning |
|-----------------|---------|---------|
| 90% | 1.645 | About 90% of repeated-sample intervals cover the parameter |
| 95% | 1.960 | Standard for most UX research |
| 99% | 2.576 | High-stakes research |

### Sample Size Table (95% confidence, 50% proportion)

These calculations assume a simple random sample and address sampling error only. An opt-in panel's selection bias is not repaired by this sample size; ask the provider for its sample design before reporting a margin of error ([AAPOR report, Section 5](https://aapor.org/wp-content/uploads/2023/02/Task-Force-Report-FINAL.pdf)).

| Margin of Error | Population 500 | Population 5,000 | Population 50,000 | Population 1,000,000 |
|-----------------|---------------|------------------|-------------------|---------------------|
| ±10% | 81 | 95 | 96 | 97 |
| ±5% | 218 | 357 | 382 | 385 |
| ±3% | 341 | 880 | 1,045 | 1,066 |
| ±1% | 476 | 3,289 | 8,057 | 9,513 |

Cells apply the finite-population formula below and round up. Recalculate for the actual population rather than treating the last column as an unlimited population.

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

Flag failures for review under a predeclared exclusion rule. One failed check alone does not establish fraud.

### Survey Integrity: Fraud, Bots, and Speeders

- Before distribution, record the provider's recruitment, bot and duplicate controls, exclusions, and available quality fields. Prefer unique invitations for a known sample; verify controls are enabled and published. Bot scores can flag a response without blocking it, and missing or error-status scores are not proof of a human response ([Qualtrics Fraud Detection](https://www.qualtrics.com/support/survey-platform/survey-module/survey-checker/fraud-detection/)).
- Predeclare a speeder threshold from a pilot by questionnaire branch and respondent context; combine timing with attention failures, inconsistent eligibility answers, straightlining, and irrelevant or repeated open text. Neither speed nor articulate text alone establishes authenticity. Trap questions and speeding checks miss insincere respondents ([AAPOR report, Section 5](https://aapor.org/wp-content/uploads/2023/02/Task-Force-Report-FINAL.pdf)).
- Quarantine flagged cases for human review rather than deleting them. Check shared-device and assistive-technology explanations; retain reason codes and a privacy-appropriate audit trail. Inspect duplicate records across recruitment sources, while limiting collection of identifying data to what the consent and study require.
- Read the platform's current score semantics and timing rules before applying exclusions. Relative speeder flags may change as responses arrive; finish collection before finalizing them ([Qualtrics Response Quality](https://www.qualtrics.com/support/survey-platform/survey-module/survey-checker/response-quality/)). Report raw, flagged, excluded, and analyzed counts by source and compare key results with and without disputed cases.

---

## Distribution Channels

### Channel Comparison

Response-rate bands below are unsourced house heuristics, not vendor promises or population benchmarks. Budget from a pilot of the same channel, audience, invitation, and incentive; disclose who was eligible and what counts as a response.

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
| **40+ question survey** | Fatigue and abandonment may undermine data quality; no universal completion rate | Pilot duration and relevance; split into focused surveys when needed |
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

Verify each shortlisted platform's current branching, accessibility, fraud controls, exports, pricing, and plan limits in its official documentation before recommending it; the table is a shortlist, not a capability guarantee.

| Platform | Best For | Strengths | Limitations | Budget fit |
|----------|----------|-----------|-------------|------------|
| **Typeform** | Conversational surveys | Conversational format, branching | Verify analysis and scale costs | Medium |
| **SurveyMonkey** | Established teams, enterprise | Templates, team features, benchmarking, compliance | UI dated, costly for advanced features | Medium to high |
| **Qualtrics** | Academic/enterprise research | Advanced logic, conjoint analysis, stats, panels | Expensive, steep learning curve | Enterprise |
| **Google Forms** | Simple surveys | Simple, integrates with Sheets; section branching for multiple-choice/dropdown answers ([official help](https://support.google.com/docs/answer/141062?hl=en)) | Basic analysis; verify whether branching and fraud controls fit the study | Low |
| **Hotjar Surveys** | In-app feedback | Integrated with heatmaps and recordings, easy targeting | Limited question types, no advanced analysis | Low to medium |
| **Maze** | UX research integration | Surveys + usability tests in one tool, prototype testing | Smaller survey feature set | Low to medium |
| **Lyssna** | UX research focus | Surveys + card sorts + tree tests, participant panel | Niche, smaller community | Medium |
| **Prolific** | Participant recruitment | Academic-grade panel, demographic targeting | Platform for recruitment, not survey hosting | Variable |

### Selection Decision

```text
What's your primary need?
  ├─ Quick, free, simple
  │   └─ Google Forms
  ├─ Conversational survey presentation
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
- [SUS — System Usability Scale (Brooke, 1996)](https://www.usability.gov/how-to-and-tools/methods/system-usability-scale.html)
- [SurveyMonkey — Sample Size Calculator](https://www.surveymonkey.com/mp/sample-size-calculator/)

---

## Cross-References

- [SKILL.md](../SKILL.md) — Parent skill overview, method selection table
- [ux-metrics-framework.md](ux-metrics-framework.md) — NPS, SUS, HEART metrics that surveys measure
- [ab-testing-implementation.md](ab-testing-implementation.md) — Sample size concepts shared with survey methodology
- [research-repository-management.md](research-repository-management.md) — Storing and reusing survey findings
- [demographic-research-methods.md](demographic-research-methods.md) — Inclusive survey design for diverse populations
