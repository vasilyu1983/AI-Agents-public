---
name: software-testing-automation
description: Test strategy, QA patterns, and automation practices across unit, integration, E2E, performance, BDD, and security testing with modern frameworks (Jest, Vitest, Playwright, k6, Cucumber).
---

# Software Testing & Automation Skill — Quick Reference

Use this skill when the primary focus is how to test software effectively rather than how to implement features. This skill provides execution-ready patterns for building reliable, maintainable test suites across all testing layers.

---

## When to Use This Skill

Invoke when users ask for:

- Test strategy for a new service or feature
- Unit testing with Jest or Vitest
- Integration testing with databases, APIs, external services
- E2E testing with Playwright or Cypress
- Performance and load testing with k6
- BDD with Cucumber and Gherkin
- API contract testing with Pact
- Visual regression testing
- Test automation CI/CD integration
- Test data management and fixtures
- Security and accessibility testing

---

## Quick Reference Table

| Test Type | Framework | Command | When to Use |
|-----------|-----------|---------|-------------|
| Unit Tests | Vitest | `vitest run` | Pure functions, business logic (40-60% of tests) |
| Component Tests | React Testing Library | `vitest --ui` | React components, user interactions (20-30%) |
| Integration Tests | Supertest + Docker | `vitest run integration.test.ts` | API endpoints, database operations (15-25%) |
| E2E Tests | Playwright | `playwright test` | Critical user journeys, cross-browser (5-10%) |
| Performance Tests | k6 | `k6 run load-test.js` | Load testing, stress testing (nightly/pre-release) |
| API Contract Tests | Pact | `pact test` | Microservices, consumer-provider contracts |
| Visual Regression | Percy/Chromatic | `percy snapshot` | UI consistency, design system validation |
| Security Tests | OWASP ZAP | `zap-baseline.py` | Vulnerability scanning (every PR) |

## Decision Tree: Test Strategy

```text
Need to test: [Feature Type]
    ├─ Pure business logic?
    │   └─ Unit tests (Jest/Vitest) — Fast, isolated, AAA pattern
    │
    ├─ UI Component?
    │   ├─ Isolated component? → Component tests (React Testing Library)
    │   └─ User journey? → E2E tests (Playwright)
    │
    ├─ API Endpoint?
    │   ├─ Single service? → Integration tests (Supertest + test DB)
    │   └─ Microservices? → Contract tests (Pact) + integration tests
    │
    ├─ Performance-critical?
    │   ├─ Load capacity? → k6 load testing (ramp-up, stress, spike)
    │   └─ Response time? → k6 performance benchmarks (SLO validation)
    │
    └─ External dependency?
        ├─ Mock it (unit tests) → Use test doubles
        └─ Real implementation (integration) → Docker containers (Testcontainers)
```

---

## Operational Playbooks
- [resources/operational-playbook.md](resources/operational-playbook.md) — Testing pyramid guidance, BDD/test data patterns, CI gates, and anti-patterns
- [resources/playwright-webapp-testing.md](resources/playwright-webapp-testing.md) — Playwright decision tree, server lifecycle helper, and recon-first scripting pattern

## Navigation

**Resources**
- [resources/operational-playbook.md](resources/operational-playbook.md)
- [resources/playwright-webapp-testing.md](resources/playwright-webapp-testing.md)
- [resources/comprehensive-testing-guide.md](resources/comprehensive-testing-guide.md)
- [resources/test-automation-patterns.md](resources/test-automation-patterns.md)
- [resources/shift-left-testing.md](resources/shift-left-testing.md)

**Templates**
- [templates/test-strategy-template.md](templates/test-strategy-template.md) — Test strategy starter
- [templates/automation-pipeline-template.md](templates/automation-pipeline-template.md) — CI/CD automation pattern
- [templates/unit/template-jest-vitest.md](templates/unit/template-jest-vitest.md) — Unit testing
- [templates/integration/template-api-integration.md](templates/integration/template-api-integration.md) — Integration/API testing
- [templates/e2e/template-playwright.md](templates/e2e/template-playwright.md) — Playwright E2E
- [templates/bdd/template-cucumber-gherkin.md](templates/bdd/template-cucumber-gherkin.md) — BDD/Gherkin
- [templates/performance/template-k6-load-testing.md](templates/performance/template-k6-load-testing.md) — k6 performance
- [templates/visual-regression/template-visual-testing.md](templates/visual-regression/template-visual-testing.md) — Visual regression

**Data**
- [data/sources.json](data/sources.json) — Curated external references
