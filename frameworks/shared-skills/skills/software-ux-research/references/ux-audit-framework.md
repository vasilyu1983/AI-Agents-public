# UX Audit Framework

Comprehensive methodology for systematic UX evaluation, including extended heuristics, cognitive walkthrough, severity rating, and prioritization.

---

## Audit Overview

### What is a UX Audit?

A systematic evaluation of a product's user experience to identify usability issues, accessibility gaps, and improvement opportunities.

### Audit Types

| Type | Focus | Best For | Duration |
|------|-------|----------|----------|
| **Heuristic Evaluation** | Expert review against principles | Quick assessment, limited budget | 2-5 days |
| **Cognitive Walkthrough** | Task-based step analysis | Critical user flows | 1-3 days |
| **Accessibility Audit** | WCAG compliance | Legal requirements, inclusivity | 3-7 days |
| **Competitive Audit** | Comparison to competitors | Market positioning | 1-2 weeks |
| **Full UX Audit** | All of the above | Major redesign planning | 2-4 weeks |

### When to Audit

- Before major redesign (baseline)
- After launch (validation)
- Quarterly/annually (maintenance)
- When metrics decline (diagnosis)
- Before acquisition/investment (due diligence)

---

## Extended Heuristic Evaluation

### Nielsen's 10 Usability Heuristics

| # | Heuristic | What to Check |
|---|-----------|---------------|
| 1 | **Visibility of System Status** | Loading indicators, progress bars, state feedback |
| 2 | **Match with Real World** | Familiar language, logical order, real-world conventions |
| 3 | **User Control & Freedom** | Undo/redo, cancel, back navigation, exit points |
| 4 | **Consistency & Standards** | UI patterns, terminology, behavior consistency |
| 5 | **Error Prevention** | Confirmation dialogs, constraints, smart defaults |
| 6 | **Recognition over Recall** | Visible options, contextual help, persistent info |
| 7 | **Flexibility & Efficiency** | Shortcuts, customization, accelerators |
| 8 | **Aesthetic & Minimalist** | Essential info only, visual hierarchy, whitespace |
| 9 | **Error Recovery** | Clear error messages, constructive solutions |
| 10 | **Help & Documentation** | Searchable help, contextual guidance, tutorials |

### Gerhardt-Powals Cognitive Principles

Extend Nielsen with cognitive load considerations:

| # | Principle | Evaluation Questions |
|---|-----------|---------------------|
| 1 | **Automate Unwanted Workload** | Are repetitive tasks automated? Can users batch actions? |
| 2 | **Reduce Uncertainty** | Is next step always clear? Are outcomes predictable? |
| 3 | **Fuse Data** | Is related information grouped? Can users see connections? |
| 4 | **Present New Info with Aids** | Are complex concepts explained? Is progressive disclosure used? |
| 5 | **Use Names that Match Concepts** | Does terminology match user mental models? |
| 6 | **Group Data Meaningfully** | Is information chunked logically? (Miller's 7±2) |
| 7 | **Limit Data-Driven Tasks** | Is calculation offloaded to system? Are comparisons facilitated? |
| 8 | **Present Only Needed Info** | Is there information overload? Can users filter? |
| 9 | **Provide Multiple Coding** | Text + icons? Color + shape? Redundant cues? |
| 10 | **Practice Judicious Redundancy** | Are critical actions confirmed? Multiple access paths? |

### Weinschenk & Barker Categories

20 heuristics grouped by psychological principle:

**User Control**:
- Provide flexible interaction
- Support keyboard navigation
- Enable customization

**Human Limitations**:
- Respect memory limits
- Support recognition over recall
- Allow error recovery

**Perceptual**:
- Make actions visible
- Use consistent interface
- Provide feedback

**Learning**:
- Support novice and expert
- Enable exploration
- Provide help

### Evaluation Matrix Template

```text
| Heuristic | Screen/Flow | Issue Description | Severity | Evidence |
|-----------|-------------|-------------------|----------|----------|
| Visibility | Checkout | No loading indicator | 3-Major | [screenshot] |
| Control | Profile | No undo for delete | 2-Critical | [screenshot] |
```

---

## Cognitive Walkthrough Protocol

### Core Concept

Evaluate interface by stepping through tasks as a user would, assessing learnability at each step.

### Four Questions per Step

For each action in a task, answer:

1. **Will users try to achieve the right effect?**
   - Do users understand what they need to do?
   - Is the goal of this step clear?

2. **Will users notice the correct action is available?**
   - Is the action visible?
   - Is it labeled clearly?

3. **Will users associate the action with the desired effect?**
   - Does the label/icon match user expectations?
   - Is the affordance clear?

4. **Will users interpret feedback correctly?**
   - Does the system indicate success/failure?
   - Is it clear what to do next?

### Walkthrough Process

**Step 1: Define Inputs**
- User profile (experience level, goals)
- Task scenarios (realistic, specific)
- Interface version to evaluate

**Step 2: Walk Through Each Task**
- Break task into discrete actions
- Answer 4 questions for each action
- Document issues found

**Step 3: Synthesize Findings**
- Group issues by type
- Assign severity
- Prioritize fixes

### Walkthrough Documentation Template

```text
Task: [Create new project]
User: [First-time user, technical background]
Goal: [Set up project with basic settings]

| Step | User Action | Q1 Goal | Q2 Visible | Q3 Association | Q4 Feedback | Issues |
|------|-------------|---------|------------|----------------|-------------|--------|
| 1 | Click "New" button | Yes | Yes | Yes | Partial - modal opens but purpose unclear | Minor |
| 2 | Enter project name | Yes | Yes | Yes | No - no character limit shown | Major |
| 3 | Select template | No - unclear this is required | Yes | Partial | Yes | Critical |
```

---

## Accessibility Audit Component

### Quick WCAG 2.2 Checklist

#### Level A (Minimum)

**Perceivable**:
- [ ] All images have alt text
- [ ] Videos have captions
- [ ] Color isn't only means of conveying info
- [ ] Content can be presented without losing meaning

**Operable**:
- [ ] All functionality available via keyboard
- [ ] No keyboard traps
- [ ] No content flashes more than 3 times/second
- [ ] Skip navigation link available

**Understandable**:
- [ ] Page language is identified
- [ ] Focus doesn't change context unexpectedly
- [ ] Form inputs have labels
- [ ] Error messages identify the problem

**Robust**:
- [ ] HTML validates
- [ ] Name, role, value available for custom controls

#### Level AA (Standard)

- [ ] 4.5:1 contrast for normal text
- [ ] 3:1 contrast for large text
- [ ] Text can be resized 200% without loss
- [ ] Multiple ways to find pages
- [ ] Headings and labels are descriptive
- [ ] Focus visible
- [ ] Consistent navigation
- [ ] Consistent identification
- [ ] Error suggestions provided
- [ ] Error prevention for legal/financial

### Accessibility Testing Tools

| Tool | Type | Best For |
|------|------|----------|
| axe DevTools | Browser extension | Automated scanning |
| WAVE | Browser extension | Visual feedback |
| Lighthouse | Chrome DevTools | Performance + a11y |
| NVDA/VoiceOver | Screen reader | Manual testing |
| Colour Contrast Analyser | Desktop app | Color checking |

### Automated vs Manual Testing

**Automated catches (~30%)**:
- Missing alt text
- Color contrast
- Missing labels
- Heading structure

**Manual required (~70%)**:
- Alt text quality
- Keyboard navigation flow
- Screen reader experience
- Focus management
- Error message helpfulness

---

## Severity Rating System

### 5-Level Severity Scale

| Level | Name | Definition | Example | Fix Timeline |
|-------|------|------------|---------|--------------|
| **0** | Not a problem | No usability issue | Preference-based feedback | Backlog |
| **1** | Cosmetic | Minor visual issue, doesn't affect task | Inconsistent icon size | Next quarter |
| **2** | Minor | Causes slight delay, workaround exists | Extra click required | Next sprint |
| **3** | Major | Significant difficulty, some users blocked | Confusing navigation | This sprint |
| **4** | Critical | Task failure, data loss, or security | Can't complete purchase | Immediate |

### Severity Decision Matrix

```text
                    High Frequency
                         |
                         |
    Minor (2)            |           Critical (4)
    Affects many,        |           Blocks many,
    mild impact          |           severe impact
                         |
    -----------------+---+----------------------
                         |
    Cosmetic (1)         |           Major (3)
    Affects few,         |           Blocks few,
    mild impact          |           severe impact
                         |
                         |
                    Low Frequency

    Low Impact <-------------------------> High Impact
```

### Frequency x Impact Scoring

```text
Severity Score = Frequency Score + Impact Score

Frequency:
- Affects <10% users = 1
- Affects 10-50% users = 2
- Affects >50% users = 3

Impact:
- Annoyance, no task impact = 1
- Task delayed, workaround exists = 2
- Task blocked, no workaround = 3

Total:
- 2-3 = Cosmetic/Minor
- 4 = Major
- 5-6 = Critical
```

---

## Gap Analysis Patterns

### Current vs. Expected State

```text
| Area | Current State | Expected State | Gap | Priority |
|------|---------------|----------------|-----|----------|
| Onboarding | 5 steps, 40% completion | 3 steps, 80% completion | -3 steps, +40% | High |
| Search | Basic text search | Filters + autocomplete | Filters, suggestions | Medium |
| Mobile | Responsive but slow | Native-like performance | Performance optimization | High |
```

### Pain Point Clustering

Group issues by theme:

```text
Navigation Issues (8 findings)
├── Can't find settings (Critical)
├── Breadcrumbs missing (Major)
├── Menu labels unclear (Minor)
└── ...

Form Issues (12 findings)
├── Validation errors unclear (Critical)
├── Required fields not marked (Major)
├── Date picker unusable on mobile (Major)
└── ...

Feedback Issues (5 findings)
├── No loading indicators (Major)
├── Success messages disappear too fast (Minor)
└── ...
```

### Root Cause Analysis

For each major issue, identify root cause:

```text
Issue: Users can't complete checkout (Critical)

Why? → Error message doesn't explain problem
Why? → Backend returns generic error code
Why? → No error message mapping implemented
Why? → Rushed launch, error handling deprioritized

Root Cause: Technical debt + launch pressure
Solution: Error message system + process change
```

---

## Prioritization Framework

### Effort vs Impact Matrix

```text
                    High Impact
                         |
    QUICK WINS           |           BIG BETS
    Do First             |           Plan & Resource
    Low effort,          |           High effort,
    high return          |           high return
                         |
    -----------------+---+----------------------
                         |
    FILL-INS             |           MONEY PITS
    Do If Time           |           Avoid/Defer
    Low effort,          |           High effort,
    low return           |           low return
                         |
                         |
                    Low Impact

    Low Effort <-------------------------> High Effort
```

### Prioritization Scoring

```text
Priority Score = (Impact × 3) + (Frequency × 2) - (Effort × 1)

Impact (1-5): Business/user value
Frequency (1-5): How often encountered
Effort (1-5): Implementation complexity

Example:
- Checkout error messages: (5 × 3) + (4 × 2) - (2 × 1) = 21 → HIGH
- Icon consistency: (2 × 3) + (3 × 2) - (3 × 1) = 9 → LOW
```

### Phased Improvement Roadmap

```text
Phase 1: Quick Wins (Week 1-2)
├── Fix critical checkout errors
├── Add loading indicators
└── Improve error messages

Phase 2: Core Issues (Month 1)
├── Redesign navigation
├── Implement search filters
└── Mobile performance optimization

Phase 3: Enhancement (Quarter 1)
├── Advanced personalization
├── Accessibility improvements (AA)
└── Design system consistency

Phase 4: Innovation (Quarter 2+)
├── Optional: automation-powered features
├── New user flows
└── Platform expansion
```

---

## Audit Report Structure

### Executive Summary (1 page)

```text
UX AUDIT EXECUTIVE SUMMARY
Product: [Name]
Date: [Date]
Auditor: [Name/Team]

OVERALL UX HEALTH SCORE: 62/100

KEY FINDINGS:
• 4 Critical issues blocking core tasks
• 12 Major issues causing significant friction
• 23 Minor issues affecting experience
• 8 Cosmetic issues noted

TOP 3 PRIORITIES:
1. Checkout completion rate (47% → 75% potential)
2. Mobile performance (3.2s → 1.5s target)
3. Error message clarity (reduce support tickets 30%)

ESTIMATED IMPACT:
• Revenue: +$X potential from checkout fixes
• Support: -30% tickets from error clarity
• Engagement: +15% session duration

RECOMMENDED INVESTMENT: [X weeks/months, Y resources]
```

### Detailed Findings (Main Report)

For each finding:

```text
FINDING #[X]: [Title]

SEVERITY: [Critical/Major/Minor/Cosmetic]
LOCATION: [Screen/Flow name]
HEURISTIC: [Which principle violated]

DESCRIPTION:
[What the issue is]

EVIDENCE:
[Screenshot/recording link]

USER IMPACT:
[How this affects users]

BUSINESS IMPACT:
[Revenue, support, retention effect]

RECOMMENDATION:
[Specific fix suggestion]

EFFORT ESTIMATE: [T-shirt size: S/M/L/XL]
```

### Appendix

- Full findings log
- Screenshots and recordings
- Test methodology
- Participant profiles (if applicable)
- Competitive context
- Tool outputs (Lighthouse, axe, etc.)

---

## Audit Checklist by Product Type

### E-commerce

- [ ] Product discovery (search, filters, browse)
- [ ] Product detail page (images, info, reviews)
- [ ] Cart management (add, edit, remove)
- [ ] Checkout flow (guest option, payment, confirmation)
- [ ] Account management (orders, returns, settings)
- [ ] Mobile purchasing experience

### SaaS Application

- [ ] Onboarding (signup, first value, activation)
- [ ] Core workflow (main task completion)
- [ ] Navigation (find features, context switching)
- [ ] Collaboration (sharing, permissions, comments)
- [ ] Settings and configuration
- [ ] Upgrade/billing flow

### Mobile App

- [ ] App store presence (screenshots, description)
- [ ] Onboarding (permissions, account creation)
- [ ] Navigation (tab bar, gestures, back behavior)
- [ ] Offline functionality
- [ ] Notifications (relevance, frequency, actions)
- [ ] Performance (load time, responsiveness)

### Content Website

- [ ] Information architecture (findability)
- [ ] Content readability (typography, length)
- [ ] Navigation (menus, search, breadcrumbs)
- [ ] Mobile reading experience
- [ ] Page load performance
- [ ] Accessibility for diverse audiences
