# Technical Debt Management

> Operational reference for identifying, categorizing, tracking, prioritizing, and systematically reducing technical debt. Covers the debt quadrant model, detection patterns, sprint allocation strategies, and stakeholder communication.

**Freshness anchor:** January 2026 — aligned with current SonarQube 10.x metrics, CodeClimate, and industry technical debt management practices.

---

## Technical Debt Quadrant

| | Deliberate | Accidental |
|---|---|---|
| **Reckless** | "We don't have time for design" — shipping knowingly bad code under pressure | "What's a design pattern?" — shipping bad code due to lack of knowledge |
| **Prudent** | "We must ship now and deal with consequences" — conscious tradeoff with payback plan | "Now we know how we should have done it" — learning-driven debt discovered after implementation |

### Quadrant Decision Guide

```
Was the debt introduced knowingly?
├── YES (Deliberate)
│   ├── Was there a payback plan?
│   │   ├── YES → Prudent Deliberate (acceptable, track and schedule payback)
│   │   └── NO → Reckless Deliberate (escalate, requires immediate planning)
│   └── Document the tradeoff in ADR
└── NO (Accidental)
    ├── Was the team skilled?
    │   ├── YES → Prudent Accidental (learning-driven, normal, refactor when revisiting)
    │   └── NO → Reckless Accidental (invest in training, pair programming)
    └── Document the discovery and remediation approach
```

---

## Debt Identification Patterns

### Code-Level Indicators

| Signal | Detection Method | Tool |
|---|---|---|
| High cyclomatic complexity | Static analysis | SonarQube, CodeClimate, ESLint (complexity rule) |
| Large files / long methods | Line count thresholds | `wc -l`, IDE warnings, custom linting |
| Code duplication | Duplicate detection | SonarQube, jscpd, PMD CPD |
| Outdated dependencies | Dependency age analysis | Renovate dashboard, `npm outdated`, Dependabot |
| Low test coverage | Coverage reporting | Istanbul/c8, pytest-cov, JaCoCo |
| TODO/FIXME/HACK comments | Pattern search | `rg "TODO\|FIXME\|HACK\|XXX"` |
| Inconsistent error handling | Code review, linting | Custom ESLint/Clippy rules |
| Dead code | Coverage + static analysis | Knip (JS), vulture (Python), dead_code_checker |

### Architecture-Level Indicators

| Signal | How to detect |
|---|---|
| Circular dependencies | Dependency graph analysis (Madge, deptrac) |
| God services / modules | Fan-in/fan-out metrics, module size |
| Shared mutable state | Code review, race condition reports |
| Tight coupling | Change coupling analysis (which files always change together) |
| Missing abstractions | Same logic duplicated across services |
| Schema debt | Migration count, workaround columns, JSON blob columns |

### Process-Level Indicators

| Signal | Metric |
|---|---|
| Increasing deploy time | Track CI/CD pipeline duration over time |
| Rising bug rate | Bug count per sprint trending up |
| Onboarding difficulty | Time for new dev to first meaningful PR |
| Fear of change | Team avoids touching certain areas |
| Incident repeat rate | Same root cause appearing in multiple incidents |

### Automated Detection Checklist

- [ ] SonarQube / CodeClimate configured with quality gate
- [ ] Dependency freshness dashboard (Renovate, Dependabot)
- [ ] Test coverage tracked and trending visible
- [ ] CI pipeline duration tracked weekly
- [ ] Code complexity metrics in PR checks
- [ ] Knip / tree-shaking for dead code detection
- [ ] Architecture fitness functions (dependency rules) in CI

---

## Tracking Systems

### Tagging Approach

```
Label: tech-debt
Sub-labels:
  - tech-debt/code-quality
  - tech-debt/dependencies
  - tech-debt/testing
  - tech-debt/architecture
  - tech-debt/infrastructure
  - tech-debt/documentation

Priority:
  - P1: Actively causing bugs or incidents
  - P2: Slowing down feature development measurably
  - P3: Will become P2 within 2-3 months
  - P4: Improvement opportunity, no urgency
```

### Tech Debt Ticket Template

```markdown
## Tech Debt: [Title]

**Category:** [code-quality | dependencies | testing | architecture | infrastructure]
**Quadrant:** [Prudent Deliberate | Reckless Deliberate | Prudent Accidental | Reckless Accidental]
**Priority:** [P1 | P2 | P3 | P4]

### Current State
- What exists today and why it's a problem

### Impact
- How this debt affects velocity / quality / reliability
- Quantify if possible (e.g., "adds 10 min to every deploy")

### Proposed Solution
- What the fix looks like
- Estimated effort: [S | M | L | XL]

### Acceptance Criteria
- [ ] [Specific measurable outcome]
- [ ] [Tests passing, metrics improved, etc.]

### Context
- When was this debt introduced and why
- Link to original ADR/PR if available
- Review date: [date to re-evaluate priority]
```

### ADR (Architecture Decision Record) for Debt

```markdown
# ADR-NNN: [Decision that creates known debt]

**Status:** Accepted
**Date:** 2026-01-15
**Deciders:** [names]

## Context
[Why we're making this tradeoff]

## Decision
[What we decided to do, knowing it creates debt]

## Debt Created
- [Specific debt item 1]
- [Specific debt item 2]

## Payback Plan
- [When and how we'll address each item]
- Review date: [specific date, max 3 months out]

## Consequences
- Positive: [immediate benefit]
- Negative: [ongoing cost until addressed]
```

---

## Sprint Allocation Strategies

### Strategy Comparison

| Strategy | How it works | Best for | Risk |
|---|---|---|---|
| 20% Rule | Reserve 20% of sprint capacity for debt | Steady-state teams | Debt work gets deprioritized when under pressure |
| Debt Sprints | Dedicate entire sprint to debt every N sprints | Teams with accumulated large debt | Stakeholders resist "no feature" sprints |
| Boy Scout Rule | Leave code better than you found it | Ongoing, organic improvement | Only fixes debt in actively-changed areas |
| Tech Debt Thursday | One day per week dedicated to debt | Small teams, predictable schedule | Fragmented work, hard to tackle large items |
| Interleaving | Alternate: 1 debt story per 3 feature stories | Balanced teams | Requires discipline in story selection |
| Debt Budget | Quarterly hours budget allocated to debt | Enterprise, measurable | Budget may be cut first during crunch |

### Decision Tree: Choosing a Strategy

```
How much debt has accumulated?
├── CRITICAL (causing incidents, blocking features)
│   └── Debt Sprint(s) — dedicate full capacity until stable
├── HIGH (measurably slowing velocity)
│   └── 30% allocation until under control, then drop to 20%
├── MODERATE (noticeable but manageable)
│   └── 20% Rule + Boy Scout Rule
└── LOW (well-maintained codebase)
    └── Boy Scout Rule + occasional debt stories
```

### Making the 20% Rule Work

- [ ] Tech debt stories are estimated and planned like feature stories
- [ ] Sprint planning explicitly allocates debt capacity
- [ ] Debt stories have acceptance criteria (not "clean up X")
- [ ] Debt work counts toward velocity (same estimation system)
- [ ] Track debt resolution rate alongside feature delivery
- [ ] If debt allocation is skipped, carry forward (don't lose it)

---

## Prioritization Framework

### Impact-Effort Matrix for Tech Debt

```
           High Impact
               │
    ┌──────────┼──────────┐
    │  DO NEXT │ DO FIRST │
    │  (Plan)  │ (Sprint) │
    │          │          │
────┼──────────┼──────────┼────
    │          │          │
    │ CONSIDER │ QUICK WIN│
    │(Backlog) │  (Now)   │
    │          │          │
    └──────────┼──────────┘
               │
           Low Impact
    High Effort          Low Effort
```

### Prioritization Scoring

| Factor | Weight | Score (1-5) | Calculation |
|---|---|---|---|
| Incident frequency caused by this debt | 3x | [1-5] | weight × score |
| Developer time wasted per week | 3x | [1-5] | weight × score |
| Number of teams/services affected | 2x | [1-5] | weight × score |
| Risk of worsening if left untreated | 2x | [1-5] | weight × score |
| Effort to fix | 1x (inverse) | [1-5] | weight × (6 - score) |
| **Total** | | | Sum = priority score |

### Urgency Signals (Promote to P1)

- Debt item was root cause in last 2 incidents
- Team velocity dropped >20% and debt is a contributing factor
- Security vulnerability in the debt area
- Regulatory compliance at risk
- Key team member leaving who understands the debt area

---

## Stakeholder Communication

### Framing Tech Debt for Non-Technical Stakeholders

| Instead of... | Say... |
|---|---|
| "We need to refactor the codebase" | "We need to reduce the time it takes to ship new features" |
| "Our code quality is bad" | "Each new feature is taking 30% longer than it should" |
| "We have technical debt" | "We've been making speed-over-quality tradeoffs that are now slowing us down" |
| "We need a debt sprint" | "We need to invest one sprint in reliability to prevent the incidents we've been having" |
| "The architecture is wrong" | "Our current design limits us to X; changing it enables Y" |

### Debt Health Dashboard

| Metric | Target | Current | Trend |
|---|---|---|---|
| Dependency age (avg) | <6 months | [value] | [arrow] |
| Test coverage | >80% | [value]% | [arrow] |
| CI pipeline duration | <10 min | [value] min | [arrow] |
| Bug rate per sprint | <3 | [value] | [arrow] |
| Code complexity (avg) | <10 | [value] | [arrow] |
| Tech debt story throughput | ≥20% of velocity | [value]% | [arrow] |
| Incidents with debt root cause | 0 | [value] | [arrow] |

### Reporting Cadence

| Audience | Frequency | Content |
|---|---|---|
| Engineering team | Every retro | Debt items resolved, new debt discovered |
| Engineering manager | Biweekly | Debt health metrics, allocation adherence |
| Product manager | Sprint planning | Debt items competing for capacity, impact framing |
| Leadership / CTO | Monthly / quarterly | Debt health dashboard, trend analysis, investment request |

---

## Prevention Patterns

### Preventing New Debt Accumulation

- [ ] Definition of Done includes code review, tests, and documentation
- [ ] PR template asks: "Does this introduce known technical debt? If yes, link the tracking ticket."
- [ ] Architecture Decision Records (ADRs) required for significant design choices
- [ ] Complexity limits enforced in CI (fail PR if cyclomatic complexity >15)
- [ ] Dependency update automation (Renovate/Dependabot) with auto-merge for patches
- [ ] Quarterly architecture review to catch drift early
- [ ] "Debt introduced" label added to PRs that knowingly add debt

### Code Review Debt Gates

```
During code review, check:
├── New TODO/FIXME comments → Must link to a tracking ticket
├── Copied/pasted code blocks → Must extract to shared module or justify
├── Skipped tests with reason "will add later" → Must link to ticket with due date
├── Workaround for upstream bug → Must link to upstream issue
└── "Quick fix" in incident response → Must link to follow-up cleanup ticket
```

---

## Anti-Patterns

| Anti-Pattern | Problem | Fix |
|---|---|---|
| "We'll fix it later" without tracking | Debt is forgotten, accumulates silently | Every "later" gets a ticket, no exceptions |
| Big-bang rewrite | High risk, long freeze, often fails | Incremental refactoring, strangler fig pattern |
| Debt sprint every quarter | Too infrequent, debt piles up between | Continuous allocation (20% rule) |
| Only addressing code-level debt | Architecture and process debt ignored | Categorize all debt types, include in tracking |
| No stakeholder visibility | Debt budget cut first during crunch | Regular reporting with business impact framing |
| Treating all debt as equal priority | High-impact debt waits behind trivial items | Use prioritization scoring, not FIFO |
| Perfectionism disguised as debt reduction | Gold-plating instead of pragmatic fixes | Define acceptance criteria, scope the fix |
| Measuring only coverage numbers | Coverage without meaningful assertions | Track mutation testing score, not just line coverage |
| Individual heroics to fix debt | Unsustainable, burns out contributors | Systematic allocation, team responsibility |

---

## Cross-References

- `dev-workflow-planning/references/agile-ceremony-patterns.md` — allocating debt in sprint planning
- `dev-workflow-planning/references/remote-async-workflows.md` — async debt tracking and RFC process
- `software-clean-code-standard/references/code-complexity-metrics.md` — measuring code quality
- `qa-refactoring/SKILL.md` — refactoring strategies for debt reduction
- `qa-refactoring/references/characterization-testing.md` — testing legacy code before refactoring
- `software-architecture-design/SKILL.md` — architecture-level debt decisions
