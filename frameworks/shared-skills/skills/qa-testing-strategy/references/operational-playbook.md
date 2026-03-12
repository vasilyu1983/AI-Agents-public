# Operational Testing Playbook (2026)

Compact navigation hub for layered testing, CI gates, and ready-to-use templates.

## Contents

- Core Testing Principles
- Navigation
- Pattern: Test Pyramid
- Pattern: Given–When–Then (BDD)
- Pattern: Test Data Management
- Pattern: CI Test Gates
- Quick Reference: Framework Selection (2026)
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

- [references/comprehensive-testing-guide.md](comprehensive-testing-guide.md) — Complete testing playbook across unit, integration, E2E, performance, and security layers with modern 2026 practices
- [references/shift-left-testing.md](shift-left-testing.md) — Shift-left tactics, BDD in requirements, TDD workflow, preview environments, and continuous testing
- [references/test-automation-patterns.md](test-automation-patterns.md) — Patterns and anti-patterns: Page Object Model, test doubles, fixtures, contract testing, retry logic, and common pitfalls
- [data/sources.json](../data/sources.json) — Curated external references for frameworks (Jest, Vitest, Playwright, k6, Cucumber), tools, and best practices

### Templates by Testing Type

**Unit Testing:**
- [assets/unit/template-jest-vitest.md](../assets/unit/template-jest-vitest.md) — Jest/Vitest unit tests with AAA pattern, mocking, snapshot testing, test factories, async testing, and coverage

**E2E Testing:**
- [assets/e2e/template-playwright.md](../assets/e2e/template-playwright.md) — Playwright cross-browser E2E tests with Page Object Model, authentication state reuse, API mocking, mobile testing, visual regression, and parallel execution

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

**Checklist:**

- [ ] Unit tests run on every commit
- [ ] Integration tests run on PR and main branch
- [ ] E2E tests run on staging before production deploy
- [ ] Performance tests run nightly with trend analysis
- [ ] Security scans run on every PR (OWASP ZAP, Snyk)
- [ ] Flaky tests are tracked and fixed, not ignored

See [assets/automation-pipeline-template.md](../assets/automation-pipeline-template.md) for CI/CD pipeline blueprint.

---

## Quick Reference: Framework Selection (2026)

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

2. **Set up test pyramid** with proper ratios (60% unit, 30% integration, 10% E2E)

3. **Configure CI/CD** with test gates at each stage

4. **Implement test data factories** for consistent, reusable test data

5. **Add code coverage tracking** with thresholds (80%+ overall)

6. **Monitor test flakiness** and fix root causes

7. **Run tests in parallel** to reduce feedback time

See [references/comprehensive-testing-guide.md](comprehensive-testing-guide.md) for complete testing playbook and [references/shift-left-testing.md](shift-left-testing.md) for early testing practices.
