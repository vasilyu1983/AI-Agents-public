# Technical Debt Register

Track and prioritize technical debt items. Copy this template to your project.

---

## Active Technical Debt

| ID | Description | Type | Impact | Effort | Priority | Created | Owner | Target | Status |
|----|-------------|------|--------|--------|----------|---------|-------|--------|--------|
| TD-001 | Refactor UserService (600+ lines, complexity 25) | Prudent Deliberate | High | 2d | P1 | 2025-11-01 | Alice | Sprint 24 | In Progress |
| TD-002 | Add tests for PaymentProcessor (0% coverage) | Reckless Inadvertent | High | 3d | P1 | 2025-10-15 | Bob | Sprint 24 | Backlog |
| TD-003 | Extract shared validation logic (duplicated 5x) | Prudent Inadvertent | Medium | 1d | P2 | 2025-11-10 | Charlie | Sprint 25 | Backlog |
| TD-004 | Update deprecated API endpoints (3 remaining) | Prudent Deliberate | Medium | 2d | P2 | 2025-09-01 | Dave | Sprint 26 | Backlog |
| TD-005 | Reduce OrderProcessor complexity (18) | Reckless Inadvertent | Low | 4h | P3 | 2025-11-15 | Eve | Sprint 27 | Backlog |

---

## Debt Classification

### Type (Technical Debt Quadrant)

**Reckless Deliberate**: "We don't have time for design"
- Most dangerous, avoid creating
- Example: Copy-pasting code to ship fast

**Prudent Deliberate**: "We must ship now and deal with consequences"
- Acceptable short-term
- Example: Shipping MVP with known limitations

**Reckless Inadvertent**: "What's layering?"
- Due to lack of knowledge
- Example: Not using design patterns

**Prudent Inadvertent**: "Now we know how we should have done it"
- Normal learning process
- Example: Realizing better architecture after implementation

---

## Prioritization

### Priority Matrix

```
          High Impact
              │
    P1 = Do Now │ P2 = Plan
    ─────────────┼─────────────
    P3 = Maybe  │ P4 = Skip
              │
          Low Impact
        Low Effort → High Effort
```

**P1**: High impact, low effort → Address immediately
**P2**: High impact, high effort → Plan and schedule
**P3**: Low impact, low effort → Fix if time available
**P4**: Low impact, high effort → Defer or reconsider

### Impact Assessment

**High Impact**:
- Blocks new features
- Causes frequent bugs
- Slows team velocity
- Security risk

**Medium Impact**:
- Makes changes difficult
- Reduces code quality
- Increases maintenance time

**Low Impact**:
- Minor inconvenience
- Aesthetic issue
- Minimal effect on development

### Effort Estimation

**Days** or **hours** to fix:
- Include time for testing
- Include time for documentation
- Include time for review

---

## Template for New Debt Items

```markdown
## TD-XXX: [Brief Description]

**Created**: YYYY-MM-DD
**Owner**: [Name]
**Status**: Backlog

### Description

[Detailed explanation of the technical debt]

### Type

[Reckless/Prudent] [Deliberate/Inadvertent]

### Why It Was Created

[Context: Why did we take this shortcut?]

### Impact

**Level**: High / Medium / Low

**Effects**:
- [Effect 1]
- [Effect 2]

**Business Impact**:
- [How does this affect business? Slower features? More bugs?]

### Effort to Fix

**Estimated**: X days / hours

**Tasks**:
- [ ] Task 1
- [ ] Task 2
- [ ] Task 3

### Priority

**Priority**: P1 / P2 / P3 / P4

**Reasoning**:
[Why this priority? Impact vs. effort trade-off]

### Target

**Sprint**: Sprint XX
**Deadline**: YYYY-MM-DD (if applicable)

### Related Items

- Related to TD-XXX
- Blocks Feature-YYY
- Depends on TD-ZZZ

### Metrics

**Before**:
- Lines of code: XXX
- Complexity: YY
- Test coverage: ZZ%
- Debt ratio: AA%

**After (Expected)**:
- Lines of code: XXX
- Complexity: YY
- Test coverage: ZZ%
- Debt ratio: AA%

### Notes

[Additional context, links to discussions, etc.]
```

---

## Example: Complete Debt Item

```markdown
## TD-001: Refactor UserService

**Created**: 2025-11-01
**Owner**: Alice
**Status**: In Progress

### Description

UserService class has grown to 600+ lines with cyclomatic complexity of 25. It handles authentication, validation, database operations, and email notifications—violating Single Responsibility Principle.

### Type

Prudent Deliberate

### Why It Was Created

Started as simple user CRUD. Features added incrementally over 2 years without refactoring. Shipped quickly to meet deadlines.

### Impact

**Level**: High

**Effects**:
- 3 bugs in last month due to complexity
- New features take 2x longer (must understand entire class)
- Difficult to test (mocking 5+ dependencies)
- Onboarding new developers takes extra 2 days

**Business Impact**:
- Slower feature delivery (estimated 15% velocity reduction)
- Higher bug rate (3 production incidents in Q4)
- Increased hiring friction (candidates mention code quality in interviews)

### Effort to Fix

**Estimated**: 2 days

**Tasks**:
- [x] Extract AuthenticationService
- [ ] Extract ValidationService
- [ ] Extract UserRepository
- [ ] Extract EmailService
- [ ] Add unit tests (target: 85% coverage)
- [ ] Update integration tests
- [ ] Update documentation

### Priority

**Priority**: P1 (Do Now)

**Reasoning**:
- High impact (blocks features, causes bugs)
- Relatively low effort (2 days)
- Quick win for team morale

### Target

**Sprint**: Sprint 24
**Deadline**: 2025-11-30

### Related Items

- Related to TD-003 (validation logic duplication)
- Blocks Feature-045 (OAuth integration)
- Mentioned in SEC-12 (security audit finding)

### Metrics

**Before**:
- Lines of code: 600
- Complexity: 25
- Test coverage: 45%
- Debt ratio: 18%

**After (Expected)**:
- Lines of code: ~250
- Complexity: <10
- Test coverage: 85%
- Debt ratio: 12%

### Notes

- Discussed in retrospective 2025-10-28
- Stakeholders aware: Will delay Feature-046 by 2 days
- SonarQube report: [link]
- Refactoring plan: [link to design doc]
```

---

## Tracking Metrics

### Overall Debt Metrics

**Current State** (updated weekly):

```
Total Debt Items: 12
├── P1 (Critical): 2
├── P2 (High): 4
├── P3 (Medium): 5
└── P4 (Low): 1

By Status:
├── In Progress: 2
├── Backlog: 8
├── Blocked: 1
└── Completed this quarter: 6

Technical Debt Ratio: 14% (SonarQube)
Target: <10%

Estimated Total Effort: 24 days
Sprint Capacity for Debt: 2 days/sprint (20%)
```

### Trend Chart

```
Debt Ratio Over Time:

Q1 2025: 22% ████████████████████████ ↓
Q2 2025: 18% ████████████████████     ↓
Q3 2025: 14% ████████████████         ↓
Q4 2025: 12% █████████████           (target: <10%)
```

---

## Sprint Planning

### Debt Allocation

**Rule**: Allocate 20% of sprint capacity to debt reduction

**Example** (2-week sprint):
- Total capacity: 10 days
- Feature work: 8 days (80%)
- Debt reduction: 2 days (20%)

### Sprint N Planning

**Debt Items for Sprint N**:
- [ ] TD-001: UserService refactoring (2d) - P1
- [ ] TD-005: OrderProcessor complexity (4h) - P3

**Total Debt Work**: 2.5 days (25% of sprint)

**Rationale**: Catching up on P1 items, will return to 20% next sprint

---

## Completed Debt (Archive)

| ID | Description | Priority | Completed | Time Spent | Owner |
|----|-------------|----------|-----------|------------|-------|
| TD-010 | Remove deprecated API v1 | P2 | 2025-10-15 | 1d | Dave |
| TD-011 | Add tests for AuthService | P1 | 2025-10-10 | 2d | Bob |
| TD-012 | Extract payment logic | P2 | 2025-09-20 | 3d | Alice |

---

## Prevention Strategies

### Code Review Checklist

When reviewing PRs, check for new debt:
- [ ] No methods >20 lines
- [ ] No classes >300 lines
- [ ] No complexity >10
- [ ] Test coverage >80%
- [ ] No duplicate code

If debt found:
1. **Option 1**: Fix before merge (preferred)
2. **Option 2**: Create debt item, get approval, merge with plan

### Quality Gates (CI/CD)

Prevent debt with automated checks:
- Linter: Max complexity 10
- SonarQube: Quality gate must pass
- Test coverage: Must be >80%
- Build fails if debt exceeds thresholds

---

## Communication

### To Team

**Weekly Update** (standup):
- "We reduced debt ratio from 14% to 12% this week"
- "Completed TD-001, UserService is now maintainable"
- "3 P1 items remaining, focusing on those next sprint"

### To Stakeholders

**Monthly Report**:

```
Technical Debt Update - November 2025

Progress:
[check] Completed 3 debt items (TD-001, TD-005, TD-008)
[check] Debt ratio reduced: 18% → 14%
[check] Team velocity increased: 15 → 17 story points/sprint

Impact:
[check] Bug rate decreased: 8 bugs/month → 4 bugs/month
[check] Feature delivery faster: -20% time for new features
[check] Developer satisfaction improved: 3.2 → 4.1 (out of 5)

Investment:
[check] 6 days spent on debt this month (20% of capacity)
[check] ROI: 4 hours/week saved in maintenance

Next Month:
→ Target debt ratio: 12%
→ Focus on P1/P2 items (4 remaining)
→ Continue 20% allocation
```

---

## Retrospective Questions

Include in sprint retrospectives:

1. **What new debt did we create this sprint?**
   - Was it intentional (Prudent Deliberate)?
   - Did we document it?

2. **Did we meet our 20% debt reduction target?**
   - If not, why?
   - What blocked us?

3. **Which debt items caused problems this sprint?**
   - Did lack of tests slow us down?
   - Did complexity cause bugs?

4. **Are we preventing new debt effectively?**
   - Are quality gates working?
   - Are code reviews catching issues?

---

## ROI Calculator

Use this to justify debt reduction to stakeholders:

```
Cost of Debt (per week):
- Bug fixes: 8 hours × $100/hour = $800
- Slow feature delivery: 10 hours × $100/hour = $1000
- Developer frustration: -10% productivity = $500
Total weekly cost: $2300

Investment to Fix:
- 2 days refactoring × $800/day = $1600

ROI:
- Payback period: 0.7 weeks
- Annual savings: $119,600
- ROI: 7475%

Break-even: Less than 1 week!
```

---

## Tools Integration

### Jira

Create "Technical Debt" issue type:
- Fields: ID, Type, Impact, Effort, Priority
- Labels: debt, P1, P2, P3, P4
- Dashboard: Debt burndown chart

### GitHub

Use labels for tracking:
- `technical-debt`
- `debt-p1`, `debt-p2`, `debt-p3`
- `debt-security`, `debt-performance`

### SonarQube

Link debt items to SonarQube issues:
- Export debt metrics
- Track debt ratio over time
- Set quality gates

---

## References

- Technical Debt Quadrant: https://martinfowler.com/bliki/TechnicalDebtQuadrant.html
- Managing Technical Debt: references/tech-debt-management.md
