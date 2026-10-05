# Competitive UX Analysis

Method and templates for benchmarking your product's UX against competitors: selecting competitors, comparing patterns and task performance, and turning gaps into prioritised recommendations. Mining competitors' reviews belongs to `research-review-mining`; design critique of a single UI belongs to [software-ui-ux-design](../../software-ui-ux-design/SKILL.md).

All numbers in the templates below are placeholders showing the format, not benchmarks.

---
## Table of Contents

- [Competitor Selection Framework](#competitor-selection-framework)
- [UX Pattern Analysis](#ux-pattern-analysis)
- [Feature Comparison Matrix](#feature-comparison-matrix)
- [External Benchmarks](#external-benchmarks)
- [Benchmarking Metrics](#benchmarking-metrics)
- [Competitive Report Structure](#competitive-report-structure)
- [Competitive Analysis Checklist](#competitive-analysis-checklist)
- [Researching Competitor Flows](#researching-competitor-flows)


## Competitor Selection Framework

### Competitor Types

| Type | Definition | Why Analyze |
|------|------------|-------------|
| **Direct** | Same product, same market | Feature parity, differentiation |
| **Indirect** | Different product, same need | Alternative solutions, JTBD |
| **Aspirational** | Best-in-class, any industry | UX patterns, inspiration |
| **Emerging** | New entrants, startups | Disruption signals, innovation |

### Selection Matrix

```text
COMPETITOR SELECTION GUIDE

Must Include (2-3):
├── Top direct competitor
├── Fastest-growing competitor
└── Current user's alternative

Should Include (1-2):
├── Aspirational best-in-class
└── Adjacent market leader

Consider (1):
└── Disruptive newcomer

Total: 4-6 competitors maximum
```

### Competitor Research Sources

| Source | What You'll Learn |
|--------|-------------------|
| Their product (trial/demo) | Actual UX experience |
| App Store / Play Store | User complaints, praised features |
| G2, Capterra reviews | Feature gaps, satisfaction drivers |
| Customer interviews | Why they chose/left competitor |
| Job postings | Their priorities and investment areas |
| Crunchbase, LinkedIn | Size, growth, team composition |

---

## UX Pattern Analysis

### Navigation Patterns Comparison

| Pattern | Your Product | Competitor A | Competitor B | Best Practice |
|---------|--------------|--------------|--------------|---------------|
| Primary nav style | Sidebar | Top bar | Sidebar | Context-dependent |
| Mobile nav | Hamburger | Bottom tabs | Hamburger | Bottom tabs for frequent use |
| Search placement | Top right | Top center | Top left | Prominent, consistent |
| Breadcrumbs | None | Full path | Abbreviated | Full path for deep hierarchy |
| Back behavior | Browser | In-app stack | Both | In-app + browser support |

### Onboarding Flow Analysis

| Element | Your Product | Competitor A | Competitor B | Best Practice |
|---------|--------------|--------------|--------------|---------------|
| Steps to signup | 5 | 3 | 4 | 3-4 maximum |
| Social login | No | Yes | Yes | Offer multiple options |
| Email verification | Before use | After value | Before use | After first value |
| First-run tutorial | 8 screens | 3 tips | Progressive | Progressive in context |
| Time to value | 10 min | 2 min | 5 min | < 5 minutes |
| Skip option | No | Yes | Partial | Allow skip |

### Error Handling Comparison

| Element | Your Product | Competitor A | Competitor B | Best Practice |
|---------|--------------|--------------|--------------|---------------|
| Error visibility | Red text below | Inline + icon | Toast notification | Inline + prominent |
| Error message clarity | Technical code | Plain language | Plain + solution | Plain + specific solution |
| Prevention | Minimal | Confirmations | Smart defaults | Both confirmation + prevention |
| Recovery assistance | "Try again" | Specific steps | Auto-retry | Context-specific guidance |

### Mobile Experience Benchmarking

| Element | Your Product | Competitor A | Competitor B | Best Practice |
|---------|--------------|--------------|--------------|---------------|
| Touch targets | 32px | 44px | 48px | 44-48px minimum |
| Gesture support | Tap only | Swipe actions | Full gesture | Common gestures supported |
| Offline capability | None | Partial read | Full sync | Graceful degradation |
| Performance (LCP) | 3.2s | 1.8s | 2.4s | < 2.5s |
| PWA/native | Responsive web | PWA | Native app | Match user expectations |

---

## Feature Comparison Matrix

### Feature Parity Analysis

```text
FEATURE COMPARISON MATRIX

| Feature Category | Feature | Ours | Comp A | Comp B | Comp C | Priority |
|------------------|---------|------|--------|--------|--------|----------|
| Core | Basic function | Yes | Yes | Yes | Yes | Table stakes |
| Core | Advanced function | No | Yes | Yes | No | Gap to close |
| Differentiation | Unique feature | Yes | No | No | No | Maintain lead |
| Nice-to-have | Extra feature | No | Yes | No | Yes | Evaluate need |

LEGEND:
Yes = Available and good quality
Partial = Available but limited
No = Not available
Best = Best-in-class implementation
```

### UX Quality Scoring

Score each feature's UX implementation (1-5):

```text
| Feature | Ours | Comp A | Comp B | Notes |
|---------|------|--------|--------|-------|
| Search | 3 | 5 | 4 | A has autocomplete + filters |
| Dashboard | 4 | 3 | 4 | Ours is cleaner |
| Settings | 2 | 4 | 3 | Ours is scattered |
| Mobile | 2 | 4 | 5 | B is native app |
| Onboarding | 3 | 5 | 4 | A has best first-run |

SCORING CRITERIA:
1 = Major usability issues, frustrating
2 = Usable but clunky, workarounds needed
3 = Acceptable, meets basic expectations
4 = Good, pleasant to use
5 = Excellent, delightful, sets standard
```

---

## External Benchmarks

Published cross-industry benchmarks are rare and easy to misquote. Baymard Institute publishes the average documented cart-abandonment rate (about 70%, averaged across many studies) and checkout form-field counts (an average of about 15 fields against an achievable 7-8). Most other "industry standard" bands that circulate (signup completion, activation, trial conversion, retention, bounce, NPS tiers) have no traceable source.

Rules:
- Quote an external number only with its publisher, study scope and date, and look up the current edition before using it.
- Prefer your own baseline and a head-to-head competitor measurement (below) over industry bands.
- For app quality metrics (crash-free rate, cold start, store rating), use the platform vendor's own guidance and your category peers, not a generic table.

---

## Benchmarking Metrics

### Task Completion Comparison

```text
TASK: [Create new project]

| Step | Ours (time) | Comp A (time) | Comp B (time) |
|------|-------------|---------------|---------------|
| Find action | 5s | 2s | 3s |
| Fill form | 45s | 30s | 20s |
| Submit | 3s | 2s | 2s |
| Confirmation | 2s | 5s | 1s |
| TOTAL | 55s | 39s | 26s |

Gap Analysis:
• Fill form: Our 45s vs B's 20s (-25s)
• Root cause: Too many required fields
• Recommendation: Reduce to essential fields, smart defaults
```

### User Satisfaction Benchmarks

```text
| Metric | Ours | Comp A | Comp B | Target |
|--------|------|--------|--------|--------|
| SUS Score | 62 | 78 | 72 | 75+ |
| NPS | +12 | +45 | +32 | +40 |
| Task satisfaction | 3.2 | 4.1 | 3.8 | 4.0 |
| Effort score | 3.8 | 2.4 | 2.9 | <3.0 |

Biggest Gap: NPS (+12 vs +45 for Comp A)
Investigation: Deep dive into promoter/detractor reasons
```

---

## Competitive Report Structure

```text
COMPETITIVE UX ANALYSIS: [Scope]
Date, products analysed, method (task walkthroughs, heuristic scoring, benchmark measurement)

KEY FINDINGS
1. [Top competitive gap]  2. [Secondary gap]  3. [Our strength to keep]

PER FEATURE AREA (repeat)
Ours:          [how it works today]
Competitor A:  [how it works]      Competitor B: [how it works]
Gap:           must close (table stakes) / should close / opportunity
Evidence:      screenshots, task times, review quotes, dated

PATTERNS
Adopt:  [pattern] from [competitor], because [user need it serves]
Avoid:  [pattern] from [competitor], because [observed problem]

RECOMMENDATIONS
| Improvement | Gap closed | Effort (S/M/L/XL) | Impact | Horizon (now / next / strategic) |
```

Rank recommendations by user impact and effort, not by how many competitors have the feature: parity with a weak pattern is not a goal. Validate "adopt" patterns with your own users before committing.

---

## Competitive Analysis Checklist

### Before Analysis

- [ ] Define analysis objectives
- [ ] Select 4-6 competitors (mixed types)
- [ ] Get access to competitor products
- [ ] Prepare evaluation framework
- [ ] Align stakeholders on scope

### During Analysis

- [ ] Complete each competitor signup/onboarding
- [ ] Execute core task scenarios
- [ ] Document with screenshots/recordings
- [ ] Score using consistent criteria
- [ ] Note standout patterns (good and bad)

### After Analysis

- [ ] Synthesize findings by theme
- [ ] Create comparison matrices
- [ ] Calculate gap severity
- [ ] Prioritize recommendations
- [ ] Present to stakeholders
- [ ] Define action items with owners

---

## Researching Competitor Flows

1. Pick the flow closest to what you are building (checkout, onboarding, KYC, money transfer, booking, API docs).
2. Collect current evidence: walk the flow yourself with a trial account, and use pattern libraries (Mobbin, Page Flows) and public teardowns. Record the date; competitor flows change often.
3. Compare 2-3 leaders, note the patterns they share, and separate regulatory requirements (identity checks, consent, disclosures) from design choices.
4. Adapt, do not copy: map each pattern to your users' needs, find one or two differentiation opportunities, and validate with usability testing.

Search starting points:

```text
"[company] [flow type] UX walkthrough"
site:mobbin.com [company] [flow]
site:pageflows.com [company]
"[company] UX teardown"
"[company] vs [competitor] UX comparison"
```
