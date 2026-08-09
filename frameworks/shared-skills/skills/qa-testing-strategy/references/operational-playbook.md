# Operational Testing Playbook

## Table of Contents

- [Contents](#contents)
- [Core Testing Principles](#core-testing-principles)
- [Navigation](#navigation)
- [Pattern: Test Pyramid](#pattern-test-pyramid)
- [Pattern: Given–When–Then (BDD)](#pattern-givenwhenthen-bdd)
- [Pattern: Test Data Management](#pattern-test-data-management)
- [Pattern: CI Test Gates](#pattern-ci-test-gates)
- [Quick Reference: Framework Selection](#quick-reference-framework-selection-2026)
- [Coverage Goals](#coverage-goals)
- [Common Anti-Patterns to Avoid](#common-anti-patterns-to-avoid)
- [Testing Decision Tree](#testing-decision-tree)
- [External Resources](#external-resources)
- [Best Practices Checklist](#best-practices-checklist)
- [Getting Started](#getting-started)

Compact navigation hub for layered testing, CI gates, and ready-to-use templates.

## Contents

- Core Testing Principles
- Navigation
- Pattern: Test Pyramid
- Pattern: Test Shape Selection
- Pattern: Given–When–Then (BDD)
- Pattern: Test Data Management
- Pattern: CI Test Gates
- Quick Reference: Framework Selection
- Coverage Goals
- Common Anti-Patterns to Avoid
- Testing Decision Tree
- External Resources
- Best Practices Checklist

## Core Testing Principles

### Test Pyramid Distribution

```
       /\
      /E2E\         5-10% - End-to-end tests (critical paths)
     /------\
    /  API  \       15-25% - API/Integration tests
   /----------\
  / Component \     20-30% - Component tests
 /--------------\
/      Unit       \ 40-60% - Unit tests (fast, isolated)
```

These ratios describe a logic-heavy monolith and are a starting illustration, not a target to hit by adding tests. Treat them as one shape among several — see [Pattern: Test Shape Selection](#pattern-test-shape-selection) below, which is the actual decision rule: allocate coverage to where defects originate, then let the ratio fall out of that decision. A frontend-heavy app or a microservice mesh should land on a visibly different distribution, and that is correct, not a deviation to fix.

**Rationale:**
- **Unit tests**: Fast (ms), isolated, easy to debug, cheap to maintain
- **Component tests**: Balance speed + integration, good for business logic
- **Integration tests**: Test service interactions, catch integration issues
- **E2E tests**: Expensive but validate critical user journeys

### Core Themes

- Clarify what to test vs what to assume
- Use fast, deterministic unit tests for core logic
- Use integration tests for cross-service flows
- Use E2E tests only for critical user paths
- Keep flaky tests out of required gates; fix or quarantine them
- Mock external boundaries, use real implementations internally
- Test behavior, not implementation details

---

## Navigation

### Resources (Detailed Guides)

- [references/comprehensive-testing-guide.md](comprehensive-testing-guide.md) — Complete testing playbook across unit, integration, E2E, performance, and security layers with modern practices
- [references/component-testing-browser-mode.md](component-testing-browser-mode.md) — Real-browser component testing strategy for modern JS/TS UI apps
- [references/shift-left-testing.md](shift-left-testing.md) — Shift-left tactics, BDD in requirements, TDD workflow, preview environments, and continuous testing
- [references/schema-aware-api-fuzzing.md](schema-aware-api-fuzzing.md) — Schema-aware fuzzing for OpenAPI-driven APIs
- [references/test-automation-patterns.md](test-automation-patterns.md) — Patterns and anti-patterns: Page Object Model, test doubles, fixtures, contract testing, retry logic, and common pitfalls
- [data/sources.json](../data/sources.json) — Curated external references for frameworks (Jest, Vitest, Playwright, k6, Cucumber), tools, and best practices

### Templates by Testing Type

**Unit Testing:**
- [assets/unit/template-jest-vitest.md](../assets/unit/template-jest-vitest.md) — Jest/Vitest unit tests with AAA pattern, mocking, snapshot testing, test factories, async testing, and coverage

**Component Testing:**
- [assets/component/template-vitest-browser.md](../assets/component/template-vitest-browser.md) — Vitest Browser Mode component tests for real-browser UI behavior and accessibility smoke

**E2E Testing:**
- [assets/e2e/template-playwright.md](../assets/e2e/template-playwright.md) — Playwright cross-browser E2E tests with setup projects, traces on retry, accessibility smoke, and parallel execution

**Performance Testing:**
- [assets/performance/template-k6-load-testing.md](../assets/performance/template-k6-load-testing.md) — k6 load testing with realistic scenarios, spike testing, stress testing, soak testing, custom metrics, and CI/CD integration

**BDD (Behavior-Driven Development):**
- [assets/bdd/template-cucumber-gherkin.md](../assets/bdd/template-cucumber-gherkin.md) — Cucumber BDD with Gherkin syntax, scenario outlines, data tables, tags, step definitions, and best practices for declarative testing

**Strategy & Pipeline:**
- [assets/test-strategy-template.md](../assets/test-strategy-template.md) — Test strategy one-pager with quality goals, scope by layer, data handling, and ownership
- [assets/automation-pipeline-template.md](../assets/automation-pipeline-template.md) — CI/CD pipeline blueprint with stages, gates, parallelization, and rollback rules

### Related Skills

- [../software-backend/SKILL.md](../../software-backend/SKILL.md) — Backend testing with Node.js, Python, Java (language-specific unit/integration patterns)
- [../software-frontend/SKILL.md](../../software-frontend/SKILL.md) — Frontend component testing, React Testing Library, accessibility, and visual testing
- [../software-mobile/SKILL.md](../../software-mobile/SKILL.md) — Mobile testing with XCTest, Espresso, Detox, and Appium
- [../qa-resilience/SKILL.md](../../qa-resilience/SKILL.md) — Chaos engineering, resilience testing, and reliability validation
- [../ops-devops-platform/SKILL.md](../../ops-devops-platform/SKILL.md) — CI/CD pipelines, observability, and incident response integration
- [../software-security-appsec/SKILL.md](../../software-security-appsec/SKILL.md) — Security testing, OWASP ZAP, vulnerability scanning, and penetration testing

---

## Pattern: Test Pyramid

Use this pattern to balance test types for optimal speed, coverage, and maintainability.

**Structure:**

**Base: Unit tests (40-60%)**
- Many, fast, close to the code
- No network, filesystem, or external services
- AAA pattern (Arrange, Act, Assert)
- Test business logic in isolation

**Middle: Integration tests (30-40%)**
- Fewer, slower, validate interactions
- Test with real databases, queues, external services (or Docker containers)
- Verify cross-component contracts

**Top: E2E/system tests (5-10%)**
- Small number, slowest, cover critical user journeys
- Test complete workflows through UI
- Focus on happy paths and critical edge cases

**Checklist:**

- [ ] Most new logic has unit tests
- [ ] Cross-service flows have integration or E2E coverage
- [ ] Avoid over-relying on UI-only tests for backend behavior
- [ ] Flaky tests are quarantined and fixed, not ignored
- [ ] Tests run in parallel where possible

---

---

## Pattern: Test Shape Selection

The "test pyramid" is one model. Others exist and are better suited to specific architectures. Pick based on where bugs actually live in your system.

| Shape | Description | Best For |
|-------|-------------|----------|
| **Pyramid** | Many unit → fewer integration → few E2E | Monoliths, logic-heavy backends, algorithmic code |
| **Trophy** (Kent C. Dodds) | Static analysis base, integration-heavy middle, few unit and few E2E | Frontend/full-stack JS/TS apps, API-driven services |
| **Honeycomb** (Spotify) | Integration at the center; unit tests minimized | Microservice architectures where bugs live at service boundaries |
| **Risk-based** (default recommendation) | Coverage allocated by defect probability and impact, not shape | Any architecture — start here when unsure |

**Decision rule**: ask "where do our production bugs actually come from?" and allocate coverage there. For microservices, integration tests are typically the highest-ROI layer. For domain-heavy monoliths, unit tests dominate. For frontend apps, integration tests on user-facing behavior (React Testing Library / component tests) outperform unit tests on implementation details.

Do not debate shapes as ideology. Pick the layer that can prove the behavior with the least cost. The shape emerges from that decision, not the other way around.

---

## Pattern: Given–When–Then (BDD)

Use for tests that encode requirements clearly in natural language.

**Structure:**

- **Given**: Initial state and inputs (setup)
- **When**: Action under test (execution)
- **Then**: Expected observable outcomes (assertions)

**Example (Gherkin):**

```gherkin
Scenario: Successful login with valid credentials
  Given I am on the login page
  When I enter email "user@example.com"
  And I enter password "SecurePass123"
  And I click the "Login" button
  Then I should see my dashboard
  And I should see "Welcome back, John"
```

**Guidelines:**

- Use descriptive test names that capture Given/When/Then in plain language
- Keep each test focused on a single behavior
- Use fixtures or builders to set up complex state without hiding important details

See [assets/bdd/template-cucumber-gherkin.md](../assets/bdd/template-cucumber-gherkin.md) for full BDD implementation.

---

## Pattern: Test Data Management

Use when tests rely on non-trivial data.

**Strategies:**

**In-memory data:**
- Prefer for unit tests (fast, isolated)
- Use factories to generate test data
- Avoid global shared state

**Database tests:**
- Use transactions and rollbacks per test where possible
- Reset state between tests to avoid cross-test coupling
- Use Docker containers (Testcontainers) for integration tests

**Large datasets:**
- Use factories/builders to construct minimal required data
- Keep golden files small and understandable
- Regenerate intentionally, not automatically

**Example (Factory Pattern):**

```typescript
import { faker } from '@faker-js/faker'

export class UserFactory {
  static create(overrides = {}) {
    return {
      email: faker.internet.email(),
      name: faker.person.fullName(),
      age: faker.number.int({ min: 18, max: 80 }),
      role: 'user',
      ...overrides
    }
  }

  static createMany(count: number, overrides = {}) {
    return Array.from({ length: count }, () => this.create(overrides))
  }
}
```

See [references/test-automation-patterns.md](test-automation-patterns.md) for more data management patterns.

---

## Pattern: CI Test Gates

Use when wiring tests into CI/CD pipelines.

**Stages:**

**Fast linting and unit tests:**
- Run on every push and PR
- Fail fast on style or obvious logic errors
- Target: < 5 minutes

**Integration and E2E tests:**
- Run on main branch and release branches
- Gate deployments for critical services
- Target: < 15 minutes

**Performance and security tests:**
- Run nightly or on release branches
- Track trends over time
- Target: < 30 minutes

**Flaky tests:**
- Track flakiness explicitly (retry count, failure rate)
- Quarantine or stabilize them instead of ignoring failures
- Use tags (@flaky) to separate from required gates

**Merge queues (GitHub, GitLab, Trunk, Aviator):**
- Flaky tests that fail 5% per run can block the entire queue on every cycle — impact is amplified.
- Split checks into required (unit, lint, type-check, security scan) and informational (E2E, visual regression, performance); only required checks block the queue.
- Enable automatic quarantine in your queue tool: quarantined tests still run and log output but do not eject PRs.
- Use Nx `affected` or Jest `--findRelatedTests` to subset tests per queue batch and cut CI time.
- Never rely solely on retry counts to absorb flake — instrument flake rate trends and fix root causes.

**Flaky-test economics (worked example, illustrative assumptions):**

The reason a 5% flake rate is not "just noise" is that it compounds with queue volume. Model it explicitly rather than eyeballing it:

```text
Assumptions (replace with your own measured numbers):
  PRs merged per day via queue (M)         = 40
  Flaky test's failure rate per run (f)    = 5%   (0.05)
  CI minutes burned per requeue-and-rerun  = 12 min

Expected ejections/day  = M x f            = 40 x 0.05 = 2 ejections/day
Wasted CI minutes/day   = ejections x 12   = 2 x 12    = 24 CI-minutes/day
Wasted CI minutes/month = 24 x ~21 workdays = ~504 CI-minutes/month
```

At 2 ejections/day, every merge behind that flaky test in the queue also requeues — the cost is not the 24 CI-minutes alone, it is 2 unplanned interruptions per day for whichever engineers happen to be queued behind it. That is the argument for a hard rule: **a test above the flake-SLO threshold (>1% weekly, see Core Targets) gets quarantined with an owner and expiry within one business day, rather than left to keep taxing the queue while "someone gets to it."** Recompute this model with your own `M` and `f` before deciding whether a specific flaky test justifies emergency quarantine or can wait for the next sprint — the decision should follow the number, not a blanket policy.

**Checklist:**

- [ ] Unit tests run on every commit
- [ ] Integration tests run on PR and main branch
- [ ] E2E tests run on staging before production deploy
- [ ] Performance tests run nightly with trend analysis
- [ ] Security scans run on every PR (OWASP ZAP, Snyk)
- [ ] Flaky tests are tracked and fixed, not ignored
- [ ] Merge queue required checks separated from informational checks

See [assets/automation-pipeline-template.md](../assets/automation-pipeline-template.md) for CI/CD pipeline blueprint.

---

## Quick Reference: Framework Selection

### Unit Testing

**Jest** - Best for:
- React applications (built-in React Testing Library support)
- Zero-config setup preference
- Extensive mocking capabilities

**Vitest** - Best for:
- Vite-based projects (instant compatibility)
- Speed priority (native ESM, parallel execution)
- Modern tooling (watch mode, UI mode)

**Verdict:** Vitest for new Vite projects, Jest for React/established codebases.

### E2E Testing

**Playwright** - Best for:
- Cross-browser testing (Chromium, Firefox, WebKit)
- Parallel execution by default
- Network interception and API mocking
- Mobile device emulation

**Cypress** - Best for:
- Real-time reloading and time-travel debugging
- Easier learning curve
- Excellent developer experience

**Verdict:** Playwright for comprehensive cross-browser coverage, Cypress for developer ergonomics.

### Performance Testing

**k6** - Best for:
- Developer-centric (JavaScript DSL)
- Modern CI/CD integration
- Grafana Cloud integration
- Protocol Buffers/gRPC support

**JMeter** - Best for:
- Legacy systems
- GUI-based test creation
- Java ecosystem

**Verdict:** k6 for modern applications, JMeter for legacy/Java ecosystems.

See [data/sources.json](../data/sources.json) for complete framework references and official documentation.

---

## Coverage Goals

**Critical paths**: 100%
- Authentication, payment processing, data persistence
- Security-sensitive operations

**Business logic**: 90%+
- Service layer, domain models
- Validation, calculations, workflows

**Overall**: 80%+
- Repository-wide average

**UI components**: 70%+
- Component rendering, user interactions

**Note:** Coverage is a metric, not a goal. Quality > quantity. Test behavior, not lines.

**Reconciling with the coverage anti-pattern:** [references/quality-metrics-dashboard.md](quality-metrics-dashboard.md) flags "100% coverage mandate" as an anti-pattern because a repo-wide blanket target invites Goodhart's-Law gaming (tests that execute a line without asserting anything). The targets above are the opposite of that: they are risk-scoped to a small set of critical-path modules (auth, payments, persistence), not a repo-wide rule. Even on those modules, line coverage is necessary but not sufficient — pair the 100% target with a mutation-score gate (see [Operationalising Mutation Coverage](quality-metrics-dashboard.md#operationalising-mutation-coverage)) so the tests are proven to detect regressions, not just execute code.

---

## Common Anti-Patterns to Avoid

### BAD: Testing Implementation Details

```typescript
// Bad - Tests internal method
expect(service.internalHelper()).toBe(true)

// Good - Tests public behavior
expect(service.publicMethod()).toBe(expectedResult)
```

### BAD: Flaky Tests (Race Conditions)

```typescript
// Bad - Sleep (flaky)
await sleep(1000) // Hope data loads

// Good - Explicit wait
await expect(page.getByText('Loaded')).toBeVisible()
```

### BAD: Shared Mutable State

```typescript
// Bad - Shared across tests
let user: User
beforeAll(() => { user = createUser() })

// Good - Fresh for each test
beforeEach(() => { user = createUser() })
```

### BAD: Excessive Mocking

```typescript
// Bad - Mock everything
const db = { save: jest.fn(), find: jest.fn() }
const cache = { get: jest.fn(), set: jest.fn() }

// Good - Use real implementations for internal code
const db = new InMemoryDatabase() // Real logic
const emailService = mockEmailService() // Mock external
```

### BAD: Brittle Selectors

```typescript
// Bad - Implementation-coupled
await page.locator('.btn.btn-primary.submit-v2').click()

// Good - Semantic
await page.getByRole('button', { name: 'Submit' }).click()
await page.getByTestId('submit-button').click()
```

See [references/test-automation-patterns.md](test-automation-patterns.md) for complete anti-patterns guide.

---

## Testing Decision Tree

**What should I test?**

```
Is it a UI interaction?
├─ YES → E2E test (Playwright/Cypress)
└─ NO
   ├─ Is it business logic?
   │  └─ YES → Unit test (Jest/Vitest)
   └─ Is it API contract?
      └─ YES → Contract test (Pact) + Integration test
```

**Should I mock this?**

```
Is it an external service (API, payment gateway)?
├─ YES → Mock it
└─ NO
   ├─ Is it a database?
   │  ├─ Unit test → Use in-memory/mock
   │  └─ Integration test → Use real DB (Docker)
   └─ Is it internal code?
      └─ Use real implementation
```

---

## External Resources

See [data/sources.json](../data/sources.json) for curated references across 13 categories:

- Unit testing frameworks (Jest, Vitest, Pytest, JUnit, RSpec)
- E2E testing (Playwright, Cypress, Selenium, Puppeteer)
- API testing (Supertest, REST Assured, Pact, Postman)
- Performance testing (k6, JMeter, Gatling, Locust)
- BDD frameworks (Cucumber, SpecFlow, Behave)
- Mobile testing (Appium, XCTest, Espresso, Detox)
- Visual regression (Percy, Chromatic, BackstopJS)
- Test data (Faker.js, Factory Bot, Testcontainers)
- Security testing (OWASP ZAP, Snyk, Burp Suite)
- Accessibility (Axe Core, Pa11y, Lighthouse CI)
- CI/CD integration (GitHub Actions, GitLab CI, Jenkins)
- Coverage & quality (Istanbul, Codecov, SonarQube)
- Property/mutation testing (fast-check, Stryker)

---

## Best Practices Checklist

**Test Design:**
- [ ] Use AAA pattern (Arrange, Act, Assert)
- [ ] One assertion per test (or related group)
- [ ] Test behavior, not implementation details
- [ ] Keep tests independent (no shared state)
- [ ] Use descriptive test names

**Test Data:**
- [ ] Use factories for test data generation
- [ ] Avoid magic values (use constants or factories)
- [ ] Clean up after tests (beforeEach/afterEach)

**Test Coverage:**
- [ ] 100% coverage on critical paths
- [ ] 90%+ coverage on business logic
- [ ] 80%+ overall coverage
- [ ] Track coverage trends in CI

**Test Maintenance:**
- [ ] Run tests in parallel
- [ ] Fix or quarantine flaky tests immediately
- [ ] Refactor tests alongside code
- [ ] Review test failures in CI before merging

**CI/CD Integration:**
- [ ] Unit tests on every commit (< 5 min)
- [ ] Integration tests on PR (< 15 min)
- [ ] E2E tests on staging (< 30 min)
- [ ] Performance tests nightly
- [ ] Security scans on every PR

---

## Getting Started

1. **Choose your testing stack** based on project type:
   - **JavaScript/TypeScript**: Jest/Vitest + Playwright + k6
   - **Python**: Pytest + Playwright + Locust
   - **Java**: JUnit 5 + REST Assured + Gatling
   - **Ruby**: RSpec + Capybara + JMeter

2. **Pick a test shape from where defects originate** (see [Pattern: Test Shape Selection](#pattern-test-shape-selection)) rather than targeting a fixed ratio; the pyramid distribution above is a reasonable starting illustration for logic-heavy monoliths only

3. **Configure CI/CD** with test gates at each stage

4. **Implement test data factories** for consistent, reusable test data

5. **Add code coverage tracking** with thresholds (80%+ overall)

6. **Monitor test flakiness** and fix root causes

7. **Run tests in parallel** to reduce feedback time

See [references/comprehensive-testing-guide.md](comprehensive-testing-guide.md) for complete testing playbook and [references/shift-left-testing.md](shift-left-testing.md) for early testing practices.
