---
name: software-code-review
description: Patterns, checklists, and templates for systematic code review with a focus on correctness, security, readability, performance, and maintainability.
---

# Code Reviewing Skill — Quick Reference

This skill provides operational checklists and prompts for structured code review across languages and stacks. Use it when the primary task is reviewing existing code rather than designing new systems.

---

## Quick Reference

| Review Type | Focus Areas | Key Checklist | When to Use |
|-------------|-------------|---------------|-------------|
| Security Review | Auth, input validation, secrets, OWASP Top 10 | [software-security-appsec](../software-security-appsec/SKILL.md) | Security-critical code, API endpoints |
| Performance Review | N+1 queries, algorithms, caching, hot paths | DB queries, loops, memory allocation | High-traffic features, bottlenecks |
| Correctness Review | Logic, edge cases, error handling, tests | Boundary conditions, null checks, retries | Business logic, data transformations |
| Maintainability Review | Naming, complexity, duplication, readability | Function length, naming clarity, DRY | Complex modules, shared code |
| Test Review | Coverage, edge cases, flakiness, assertions | Test quality, missing scenarios | New features, refactors |
| Frontend Review | Accessibility, responsive design, performance | [frontend-review.md](templates/web-frontend/frontend-review.md) | UI/UX changes |
| Backend Review | API design, error handling, database patterns | [api-review.md](templates/backend-api/api-review.md) | API endpoints, services |
| Blockchain Review | Reentrancy, access control, gas optimization | [crypto-review.md](templates/blockchain/crypto-review.md) | Smart contracts, DeFi protocols |

---

## .NET/EF Core Crypto Integration

For C#/.NET crypto/fintech services using Entity Framework Core, see:

- [resources/dotnet-efcore-crypto-rules.md](resources/dotnet-efcore-crypto-rules.md) — Complete review rules (correctness, security, async, EF Core, tests, MRs)

**Key rules summary:**

- Review only new/modified code in the MR
- Use `decimal` for financial values, UTC for dates
- No secrets in code, no sensitive data in logs
- Async for I/O, pass `CancellationToken`, no `.Result`/`.Wait()`
- EF Core: `AsNoTracking` for reads, avoid N+1, no dynamic SQL
- `Result<T>` pattern for explicit success/fail

---

## When to Use This Skill

Invoke this skill when the user asks to:

- Review a pull request or diff for issues
- Audit code for security vulnerabilities or injection risks
- Improve readability, structure, and maintainability
- Suggest targeted refactors without changing behavior
- Validate tests and edge-case coverage

## Decision Tree: Selecting Review Mode

```text
Code review task: [What to Focus On?]
    ├─ Security-critical changes?
    │   ├─ Auth/access control → Security Review (OWASP, auth patterns)
    │   ├─ User input handling → Input validation, XSS, SQL injection
    │   └─ Smart contracts → Blockchain Review (reentrancy, access control)
    │
    ├─ Performance concerns?
    │   ├─ Database queries → Check for N+1, missing indexes
    │   ├─ Loops/algorithms → Complexity analysis, caching
    │   └─ API response times → Profiling, lazy loading
    │
    ├─ Correctness issues?
    │   ├─ Business logic → Edge cases, error handling, tests
    │   ├─ Data transformations → Boundary conditions, null checks
    │   └─ Integration points → Retry logic, timeouts, fallbacks
    │
    ├─ Maintainability problems?
    │   ├─ Complex code → Naming, function length, duplication
    │   ├─ Hard to understand → Comments, abstractions, clarity
    │   └─ Technical debt → Refactoring suggestions
    │
    ├─ Test coverage gaps?
    │   ├─ New features → Happy path + error cases
    │   ├─ Refactors → Regression tests
    │   └─ Bug fixes → Reproduction tests
    │
    └─ Stack-specific review?
        ├─ Frontend → [frontend-review.md](templates/web-frontend/frontend-review.md)
        ├─ Backend → [api-review.md](templates/backend-api/api-review.md)
        ├─ Mobile → [mobile-review.md](templates/mobile/mobile-review.md)
        ├─ Infrastructure → [infrastructure-review.md](templates/infrastructure/infrastructure-review.md)
        └─ Blockchain → [crypto-review.md](templates/blockchain/crypto-review.md)
```

**Multi-Mode Reviews:**

For complex PRs, apply multiple review modes sequentially:

1. **Security first** (P0/P1 issues)
2. **Correctness** (logic, edge cases)
3. **Performance** (if applicable)
4. **Maintainability** (P2/P3 suggestions)

---

## Simplicity and Complexity Control

- Prefer existing, battle-tested libraries over bespoke implementations when behavior is identical.
- Flag avoidable complexity early: remove dead/commented-out code, collapse duplication, and extract single-responsibility helpers.
- Call out premature optimization; favor clarity and measured, evidence-based tuning.
- Encourage incremental refactors alongside reviews to keep modules small, predictable, and aligned to standards.

---

## Operational Playbooks

**Shared Foundation**

- [../../_shared/resources/code-quality-operational-playbook.md](../../_shared/resources/code-quality-operational-playbook.md) — Canonical coding rules (RULE-01 to RULE-13), refactoring decision trees, design patterns, and LLM-generated code review protocol

**Code Review Specific**

- [resources/operational-playbook.md](resources/operational-playbook.md) — Review scope rules, severity ratings (P0-P3), checklists, modes, and PR workflow patterns

## Navigation

**Resources**
- [resources/operational-playbook.md](resources/operational-playbook.md)
- [resources/review-checklist-comprehensive.md](resources/review-checklist-comprehensive.md)
- [resources/automation-tools.md](resources/automation-tools.md)
- [resources/dotnet-efcore-crypto-rules.md](resources/dotnet-efcore-crypto-rules.md)
- [resources/psychological-safety-guide.md](resources/psychological-safety-guide.md)

**Templates**
- [templates/backend-api/api-review.md](templates/backend-api/api-review.md)
- [templates/web-frontend/frontend-review.md](templates/web-frontend/frontend-review.md)
- [templates/mobile/mobile-review.md](templates/mobile/mobile-review.md)
- [templates/infrastructure/infrastructure-review.md](templates/infrastructure/infrastructure-review.md)
- [templates/blockchain/crypto-review.md](templates/blockchain/crypto-review.md)
- [templates/data-ml/data-pipeline-review.md](templates/data-ml/data-pipeline-review.md)
- [templates/data-ml/experiment-tracking-review.md](templates/data-ml/experiment-tracking-review.md)
- [templates/data-ml/ml-model-review.md](templates/data-ml/ml-model-review.md)
- [templates/data-ml/ml-deployment-review.md](templates/data-ml/ml-deployment-review.md)

**Data**
- [data/sources.json](data/sources.json) — Curated external references
