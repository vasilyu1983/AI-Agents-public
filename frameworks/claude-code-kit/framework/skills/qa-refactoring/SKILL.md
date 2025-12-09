---
name: qa-refactoring
description: Systematic refactoring patterns, code smell detection, technical debt management, automated code quality gates, and legacy code modernization strategies for maintainable codebases.
---

# Code Quality & Refactoring — Quick Reference

This skill provides execution-ready patterns for improving code quality, refactoring legacy systems, managing technical debt, and establishing automated quality gates. Claude should apply these patterns when users need to improve code maintainability, reduce complexity, or modernize legacy code.

**Modern Best Practices (2025)**: AI-assisted refactoring tools (GitHub Copilot, ReSharper AI, IntelliJ IDEA AI Assistant), automated code smell detection with deep learning (Embold, CodiumAI), technical debt quantification (SonarQube metrics), incremental refactoring strategies (Strangler Fig pattern), and quality gates in CI/CD pipelines.

---

## Quick Reference

| Task | Tool/Pattern | Command/Approach | When to Use |
|------|--------------|------------------|-------------|
| Long method (>50 lines) | Extract Method | Split into smaller functions | Single method does too much |
| Large class (>300 lines) | Split Class | Create focused single-responsibility classes | God object doing too much |
| Duplicated code | Extract Function/Class | DRY principle | Same logic in multiple places |
| Complex conditionals | Replace Conditional with Polymorphism | Use inheritance/strategy pattern | Switch statements on type |
| Long parameter list | Introduce Parameter Object | Create DTO/config object | Functions with >3 parameters |
| Legacy code modernization | Characterization Tests + Strangler Fig | Write tests first, migrate incrementally | No tests, old codebase |
| Automated quality gates | ESLint, SonarQube, Prettier | `npm run lint`, CI/CD pipeline | Prevent quality regression |
| Technical debt tracking | SonarQube, CodeClimate | Debt ratio < 10% target | Prioritize refactoring work |

---

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
    │
    └─ AI-Assisted Refactoring?
        ├─ Enterprise (multi-million LOC)? → Qodo, Augment Code
        ├─ .NET codebase? → ReSharper AI
        ├─ Java/Kotlin? → IntelliJ IDEA AI Assistant
        └─ General purpose? → GitHub Copilot, Cursor AI
```

---

# When to Use This Skill

Claude should invoke this skill when a user requests:

- Refactoring code to improve readability/maintainability
- Identifying and fixing code smells
- Managing technical debt
- Establishing code quality standards
- Setting up automated quality gates (linters, formatters)
- Modernizing legacy codebases
- Reducing code complexity
- Improving test coverage
- Code review automation
- Establishing refactoring strategies

---

# Operational Deep Dives

**Shared Foundation**

- [../../_shared/resources/code-quality-operational-playbook.md](../../_shared/resources/code-quality-operational-playbook.md) — Canonical coding rules (RULE-01 to RULE-13), refactoring decision trees, anti-patterns & correction routines
- [../../_shared/resources/refactoring-operational-checklist.md](../../_shared/resources/refactoring-operational-checklist.md) — Refactoring smell-to-action mapping, safe refactoring guardrails
- [../../_shared/resources/working-effectively-with-legacy-code-operational-checklist.md](../../_shared/resources/working-effectively-with-legacy-code-operational-checklist.md) — Seams, characterization tests, incremental migration patterns

**Skill-Specific**

See [resources/operational-patterns.md](resources/operational-patterns.md) for detailed refactoring catalogs, automated quality gates, technical debt playbooks, legacy modernization steps, and modern AI tooling guidance.

---

# Templates

See [templates/](templates/) for copy-paste ready examples organized by domain:
```

## Refactoring Process

Checklists and workflows for systematic code improvement:

- [Refactoring Checklist](templates/process/refactoring-checklist.md) - Systematic refactoring session checklist with pre/during/post steps
- [Code Review Quality Checklist](templates/process/code-review-quality.md) - Quality-focused code review guide with SOLID principles

## Technical Debt Tracking

Tools for managing and prioritizing technical debt:

- [Technical Debt Register](templates/tracking/tech-debt-register.md) - Track and prioritize technical debt with impact/effort matrix

## Quality Gates Configuration

Automated quality enforcement by tech stack:

### JavaScript/TypeScript
- [ESLint Configuration](templates/quality-gates/javascript/eslint-config.js) - Comprehensive linting setup with complexity rules, code smell prevention

### Platform-Agnostic
- [SonarQube Setup](templates/quality-gates/platform-agnostic/sonarqube-setup.md) - Static analysis and quality gates for 20+ languages (Docker, Cloud, Server)

---

# Resources

See [resources/](resources/) for deep-dive guides:
- **Operational Patterns**: [resources/operational-patterns.md](resources/operational-patterns.md) - Core refactoring catalogs, quality gates, legacy modernization, and AI tooling
- **Refactoring Catalog**: [resources/refactoring-catalog.md](resources/refactoring-catalog.md)
- **Code Smells Guide**: [resources/code-smells-guide.md](resources/code-smells-guide.md)
- **Technical Debt Management**: [resources/tech-debt-management.md](resources/tech-debt-management.md)
- **Legacy Code Modernization**: [resources/legacy-code-strategies.md](resources/legacy-code-strategies.md)

---

## Navigation

**Resources**
- [resources/operational-patterns.md](resources/operational-patterns.md)
- [resources/refactoring-catalog.md](resources/refactoring-catalog.md)
- [resources/code-smells-guide.md](resources/code-smells-guide.md)
- [resources/tech-debt-management.md](resources/tech-debt-management.md)
- [resources/legacy-code-strategies.md](resources/legacy-code-strategies.md)

**Templates**
- [templates/README.md](templates/README.md)
- [templates/process/refactoring-checklist.md](templates/process/refactoring-checklist.md)
- [templates/process/code-review-quality.md](templates/process/code-review-quality.md)
- [templates/process/README.md](templates/process/README.md)
- [templates/tracking/tech-debt-register.md](templates/tracking/tech-debt-register.md)
- [templates/tracking/README.md](templates/tracking/README.md)
- [templates/quality-gates/README.md](templates/quality-gates/README.md)
- [templates/quality-gates/javascript/eslint-config.js](templates/quality-gates/javascript/eslint-config.js)
- [templates/quality-gates/platform-agnostic/sonarqube-setup.md](templates/quality-gates/platform-agnostic/sonarqube-setup.md)

**Data**
- [data/sources.json](data/sources.json) — Curated external references

---
