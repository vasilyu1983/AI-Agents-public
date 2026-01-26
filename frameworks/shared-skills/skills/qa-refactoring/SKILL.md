---
name: qa-refactoring
description: "Safe refactoring for legacy or complex codebases: preserve behavior while improving structure, reducing technical debt, and tightening quality gates. Use for characterization tests, seams/adapters, incremental refactor loops, strangler migrations, refactor PR sizing, and CI guardrails (lint/type/contract tests)."
---

# QA Refactoring Safety

Use this skill to refactor safely: preserve behavior, reduce risk, and keep CI green while improving maintainability and delivery speed.

Defaults: baseline first, smallest safe step next, and proof via tests/contracts/observability instead of intuition.

## Quick Start (10 Minutes)

- Confirm baseline: `main` green; reproduce the behavior you must preserve.
- Choose a boundary: API surface, module boundary, DB boundary, or request handler.
- Add a safety net: characterization/contract/integration tests at that boundary.
- Refactor in micro-steps: one behavior-preserving change per commit/PR chunk.
- Prove: run the smallest relevant suite locally, then full CI; keep failures deterministic.

## Core QA (Default)

### Safe Refactor Loop (Behavior First)

- Establish baseline: get `main` green; reproduce the behavior you must preserve.
- Define invariants: inputs/outputs, error modes, permissions, data shape, performance budgets.
- Add a safety net: write characterization/contract/integration tests around the boundary you will touch.
- Create seams: introduce injection points/adapters to isolate side effects and external dependencies.
- Refactor in micro-steps: one behavior-preserving change at a time; keep diffs reviewable.
- Prove: run the smallest relevant suite locally, then full CI; keep failures debuggable and deterministic.
- Ship safely: use canary/dark launch/feature flags when refactors touch production-critical paths.

### Risk Levels (Choose Safety Net)

| Risk | Examples | Minimum required safety net |
|------|----------|-----------------------------|
| Low | rename, extract method, formatting-only | unit tests + lint/type checks |
| Medium | moving logic across modules, dependency inversion | unit + integration/contract tests at boundary |
| High | auth/permission paths, concurrency, migrations, money/data-loss paths | integration + contract tests, observability checks, canary + rollback plan |

### Test Strategy for Refactors

- Prefer contract and integration tests around boundaries to preserve behavior.
- Use snapshots/golden masters only when outputs are stable and reviewed (avoid "approve everything" loops).
- For invariants, consider property-based tests or table-driven cases (inputs, edge cases, error modes).
- Avoid making E2E/UI tests the primary safety net for refactors; keep most safety below the UI.
- For flaky areas: fix determinism first (seeds, time, ordering, network) before trusting results.

### CI Economics and Debugging Ergonomics

- Keep refactor PRs small and reviewable; avoid refactor + feature in one PR.
- Require failure artifacts for tests guarding refactors (logs, trace IDs, deterministic seeds, repro steps).
- Reduce diff noise: isolate formatting-only changes (or apply formatting repo-wide once with buy-in).
- Keep `git bisect` viable: avoid mixed "mechanical + semantic" changes unless necessary.

### Do / Avoid

Do:

- Add missing tests before refactoring high-risk areas.
- Add guardrails (linters, type checks, contract checks, static analysis/security checks) so refactors don't silently break interfaces.
- Prefer "branch by abstraction" / adapters when you need to swap implementations safely.

Avoid:

- Combining large structural refactors with behavior changes.
- Using flaky E2E as the primary safety net for refactors.

## Quick Reference

| Task | Tool/Pattern | Command/Approach | When to Use |
| ---- | ------------ | ---------------- | ----------- |
| Long method (>50 lines) | Extract Method | Split into smaller functions | Single method does too much |
| Large class (>300 lines) | Split Class | Create focused single-responsibility classes | God object doing too much |
| Duplicated code | Extract Function/Class | DRY principle | Same logic in multiple places |
| Complex conditionals | Replace Conditional with Polymorphism | Use inheritance/strategy pattern | Switch statements on type |
| Long parameter list | Introduce Parameter Object | Create DTO/config object | Functions with >3 parameters |
| Legacy code modernization | Characterization Tests + Strangler Fig | Write tests first, migrate incrementally | No tests, old codebase |
| Automated quality gates | ESLint, SonarQube, Prettier | `npm run lint`, CI/CD pipeline | Prevent quality regression |
| Technical debt tracking | SonarQube, CodeClimate | Track trends + hotspots | Prioritize refactoring work |

## Decision Tree: Refactoring Strategy

```text
Code issue: [Refactoring Scenario]
    ├─ Code Smells Detected?
    │   ├─ Duplicated code? → Extract method/function
    │   ├─ Long method (>50 lines)? → Extract smaller methods
    │   ├─ Large class (>300 lines)? → Split into focused classes
    │   ├─ Long parameter list? → Parameter object
    │   └─ Feature envy? → Move method closer to data
    │
    ├─ Legacy Code (No Tests)?
    │   ├─ High risk? → Write characterization tests first
    │   ├─ Large rewrite needed? → Strangler Fig (incremental migration)
    │   ├─ Unknown behavior? → Characterization tests + small refactors
    │   └─ Production system? → Canary deployments + monitoring
    │
    ├─ Quality Standards?
    │   ├─ New project? → Setup linter + formatter + quality gates
    │   ├─ Existing project? → Add pre-commit hooks + CI checks
    │   ├─ Complexity issues? → Set cyclomatic complexity limits (<10)
    │   └─ Technical debt? → Track in register, 20% sprint capacity
```

## Related Skills

- Debugging production issues: [qa-debugging](../qa-debugging/SKILL.md)
- Code review process and checklists: [software-code-review](../software-code-review/SKILL.md)
- New architecture design from scratch: [software-architecture-design](../software-architecture-design/SKILL.md)
- Test strategy and coverage planning: [qa-testing-strategy](../qa-testing-strategy/SKILL.md)

## Operational Deep Dives

### Shared Foundation

- [../software-clean-code-standard/references/clean-code-standard.md](../software-clean-code-standard/references/clean-code-standard.md) - Canonical clean code rules (`CC-*`) for citation
- Legacy playbook: [../software-clean-code-standard/references/code-quality-operational-playbook.md](../software-clean-code-standard/references/code-quality-operational-playbook.md) - `RULE-01`–`RULE-13`, decision trees, and operational procedures
- [../software-clean-code-standard/references/refactoring-operational-checklist.md](../software-clean-code-standard/references/refactoring-operational-checklist.md) - Refactoring smell-to-action mapping, safe refactoring guardrails
- [../software-clean-code-standard/references/working-effectively-with-legacy-code-operational-checklist.md](../software-clean-code-standard/references/working-effectively-with-legacy-code-operational-checklist.md) - Seams, characterization tests, incremental migration patterns

### Skill-Specific

See [references/operational-patterns.md](references/operational-patterns.md) for detailed refactoring catalogs, automated quality gates, technical debt playbooks, and legacy modernization steps.

## Templates

Use copy-paste templates in `assets/` for checklists and quality-gate configs:

- Refactoring: [assets/process/refactoring-checklist.md](assets/process/refactoring-checklist.md), [assets/process/code-review-quality.md](assets/process/code-review-quality.md)
- Technical debt: [assets/tracking/tech-debt-register.md](assets/tracking/tech-debt-register.md)
- Quality gates: [assets/quality-gates/javascript/eslint-config.js](assets/quality-gates/javascript/eslint-config.js), [assets/quality-gates/platform-agnostic/sonarqube-setup.md](assets/quality-gates/platform-agnostic/sonarqube-setup.md)

## Resources

Use deep-dive guides in `references/` (load only what you need):

- **Operational Patterns**: [references/operational-patterns.md](references/operational-patterns.md) - Core refactoring catalogs, quality gates, and legacy modernization
- **Refactoring Catalog**: [references/refactoring-catalog.md](references/refactoring-catalog.md)
- **Code Smells Guide**: [references/code-smells-guide.md](references/code-smells-guide.md)
- **Technical Debt Management**: [references/tech-debt-management.md](references/tech-debt-management.md)
- **Legacy Code Modernization**: [references/legacy-code-strategies.md](references/legacy-code-strategies.md)

## Optional: AI / Automation

Do:

- Use AI to propose mechanical refactors (rename/extract/move) only when you can prove behavior preservation via tests and contracts.
- Use AI to summarize diffs and risk hotspots; verify by running targeted characterization tests.
- Prefer tool-assisted refactors (IDE/compiler-aware, codemods) over freeform text edits when available.

Avoid:

- Accepting refactors that change behavior without an explicit requirement and regression tests.
- Letting AI "fix tests" by weakening assertions to make CI green.

See [data/sources.json](data/sources.json) for curated external references.
