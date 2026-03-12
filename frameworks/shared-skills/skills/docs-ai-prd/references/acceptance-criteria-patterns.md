# Acceptance Criteria Patterns

*Purpose: Operational guide for writing testable, unambiguous acceptance criteria (ACs) that map cleanly to automated tests, cover edge cases, and support AI-assisted development workflows.*

## Contents

- AC formats (Given/When/Then, checklist, rule-based)
- Mapping ACs to automated tests
- Edge case and negative test patterns
- Accessibility and performance templates
- Common mistakes and quick reference table

---

## Acceptance Criteria Formats

### 1. Given/When/Then (Behavioral)

**Use when:** The requirement describes a user interaction or system behavior with clear preconditions and outcomes.

```gherkin
Given a logged-in user with "editor" role
When the user clicks "Publish" on a draft article
Then the article status changes to "published"
And the article appears in the public feed within 5 seconds
```

**Rules:** One behavior per scenario. Given = precondition. When = trigger. Then = observable result. Avoid implementation details.

### 2. Checklist Format

**Use when:** Multiple independent conditions that must all be true.

- [ ] Password must be 8-128 characters
- [ ] Must contain uppercase, lowercase, and digit
- [ ] Must not match user's email or appear in breached-password dictionary
- [ ] Error message specifies which rule(s) failed

### 3. Rule-Based Format

**Use when:** Business logic with conditional branches.

- If cart total >= $100 AND member: apply 15% discount
- If cart total >= $100 AND non-member: apply 10% discount
- If cart total < $100: no discount
- Discount calculated before tax; cannot reduce price below $0

---

## Mapping ACs to Automated Tests

| AC Format | Test Type | Framework Examples |
|-----------|-----------|-------------------|
| Given/When/Then | Integration / E2E | Playwright, Cypress, pytest-bdd |
| Checklist | Unit tests (one test per checkbox) | Jest, pytest, Go testing |
| Rule-based | Parameterized / table-driven tests | pytest.mark.parametrize, Jest.each |

### Mapping Example

```text
AC: "Given expired subscription, When user accesses premium content, Then upgrade prompt shown"
-> Test: test_expired_user_sees_upgrade_prompt
-> Setup: create user with subscription_end < now()
-> Assert: response contains upgrade_prompt, status 403
```

**Rules:**
- Every AC must produce at least one test. If it cannot, the AC is untestable -- rewrite it.
- Name tests after the AC they verify. Store mappings in test docstrings or a traceability matrix.

---

## Edge Case Coverage Patterns

### Boundary Values

| Boundary | Test Cases |
|----------|------------|
| Minimum | At min, min - 1 |
| Maximum | At max, max + 1 |
| Zero / empty | 0, "", null, [] |
| Negative | -1 (if applicable) |

### State Transitions

- [ ] Every valid transition (draft -> published, published -> archived)
- [ ] Every invalid transition (archived -> draft should fail)
- [ ] Concurrent transitions (two users publish simultaneously)

### Input Combinations

- [ ] Each required field missing individually
- [ ] All optional fields omitted
- [ ] Maximum-length inputs for every text field
- [ ] Unicode, emoji, RTL text in string fields
- [ ] SQL injection and XSS payloads in free-text fields

---

## Negative Test Criteria

**Use when:** Specifying what the system must NOT do. Frequently missed in PRDs.

- [ ] Deleted user's data must NOT appear in search results
- [ ] API must NOT return other users' PII in error messages
- [ ] System must NOT process payment if cart total is $0
- [ ] Expired token must NOT grant access to any endpoint

**Pattern:** For every "system shall" AC, ask "what if someone abuses this?" and write the inverse.

---

## Accessibility and Performance Templates

### Accessibility Criteria

- [ ] All interactive elements reachable via keyboard (Tab / Shift+Tab)
- [ ] Screen reader announces form errors on submission
- [ ] Color contrast ratio >= 4.5:1 for body text (WCAG AA)
- [ ] Focus indicator visible on all interactive elements

### Performance Criteria

- [ ] Page load (LCP) < 2.5s on 4G connection
- [ ] API response time < 200ms at p95 under normal load
- [ ] Search returns results within 500ms for datasets up to 100k records
- [ ] No memory leak after 1 hour of continuous usage (heap growth < 5%)

**Rules:** Always specify measurement conditions (network, dataset size, concurrency). State the percentile (p95, p99) -- averages hide tail latency.

---

## Common Mistakes

AVOID: **Vague criteria** -- "System should be fast" or "User experience should be good."
FIX: Quantify. "API response < 200ms at p95" or "Task completion in < 3 clicks."

AVOID: **Untestable conditions** -- "System should be intuitive."
FIX: Replace with observable behavior. "New user completes onboarding in < 2 min (usability test, n=5)."

AVOID: **Implementation-specific ACs** -- "Use Redis for caching."
FIX: Describe the outcome. "Repeated queries return cached results within 50ms."

AVOID: **Missing negative cases** -- Only specifying happy-path behavior.
FIX: For every AC, write at least one "must NOT" or error-case AC.

AVOID: **Compound ACs** -- One criterion that tests three things.
FIX: Split into atomic criteria. Each AC should be independently verifiable.

---

## Quick Reference: AC Format by Requirement Type

| Requirement Type | Recommended Format | Example |
|------------------|--------------------|---------|
| User interaction / workflow | Given/When/Then | Login, checkout |
| Validation rules | Checklist | Password policy, forms |
| Business logic with branches | Rule-based | Pricing, discounts |
| Performance / SLA | Checklist with metrics | Load time, throughput |
| Accessibility | Checklist (WCAG-mapped) | Keyboard nav, reader |
| Security constraints | Negative test checklist | Auth bypass, injection |

---

## Related Resources

- [Requirements Checklists](requirements-checklists.md) -- PRD completeness validation
- [Stakeholder Alignment](stakeholder-alignment.md) -- Getting sign-off on ACs and specs
- [Gherkin Example Template](../assets/stories/gherkin-example-template.md) -- Copy-paste Gherkin scaffolds
