---
name: qa-testing-strategy
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
- Test coverage analysis and improvement
- Flaky test diagnosis and fixes
- Mobile app testing (iOS/Android)

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
| Accessibility Tests | axe-core | `vitest run a11y.test.ts` | WCAG compliance (every component) |
| Mutation Tests | Stryker | `stryker run` | Test quality validation (weekly) |

---

## Decision Tree: Test Strategy

```text
Need to test: [Feature Type]
    │
    ├─ Pure business logic?
    │   └─ Unit tests (Jest/Vitest) — Fast, isolated, AAA pattern
    │       ├─ Has dependencies? → Mock them
    │       ├─ Complex calculations? → Property-based testing (fast-check)
    │       └─ State machine? → State transition tests
    │
    ├─ UI Component?
    │   ├─ Isolated component?
    │   │   └─ Component tests (React Testing Library)
    │   │       ├─ User interactions → fireEvent/userEvent
    │   │       └─ Accessibility → axe-core integration
    │   │
    │   └─ User journey?
    │       └─ E2E tests (Playwright)
    │           ├─ Critical path → Always test
    │           ├─ Edge cases → Selective E2E
    │           └─ Visual → Percy/Chromatic
    │
    ├─ API Endpoint?
    │   ├─ Single service?
    │   │   └─ Integration tests (Supertest + test DB)
    │   │       ├─ CRUD operations → Test all verbs
    │   │       ├─ Auth/permissions → Test unauthorized paths
    │   │       └─ Error handling → Test error responses
    │   │
    │   └─ Microservices?
    │       └─ Contract tests (Pact) + integration tests
    │           ├─ Consumer defines expectations
    │           └─ Provider verifies contracts
    │
    ├─ Performance-critical?
    │   ├─ Load capacity?
    │   │   └─ k6 load testing (ramp-up, stress, spike)
    │   │
    │   └─ Response time?
    │       └─ k6 performance benchmarks (SLO validation)
    │
    └─ External dependency?
        ├─ Mock it (unit tests) → Use test doubles
        └─ Real implementation (integration) → Docker containers (Testcontainers)
```

## Decision Tree: Choosing Test Framework

```text
What are you testing?
    │
    ├─ JavaScript/TypeScript?
    │   ├─ New project? → Vitest (faster, modern)
    │   ├─ Existing Jest project? → Keep Jest
    │   └─ Browser-specific? → Playwright component testing
    │
    ├─ Python?
    │   ├─ General testing? → pytest
    │   ├─ Django? → pytest-django
    │   └─ FastAPI? → pytest + httpx
    │
    ├─ Go?
    │   ├─ Unit tests? → testing package
    │   ├─ Mocking? → gomock or testify
    │   └─ Integration? → testcontainers-go
    │
    ├─ Rust?
    │   ├─ Unit tests? → Built-in #[test]
    │   └─ Property-based? → proptest
    │
    └─ E2E (any language)?
        ├─ Web app? → Playwright (recommended)
        ├─ API only? → k6 or Postman/Newman
        └─ Mobile? → Detox (RN), XCUITest (iOS), Espresso (Android)
```

## Decision Tree: Flaky Test Diagnosis

```text
Test is flaky?
    │
    ├─ Timing-related?
    │   ├─ Race condition? → Add proper waits (not sleep)
    │   ├─ Animation? → Disable animations in test mode
    │   └─ Network timeout? → Increase timeout, add retry
    │
    ├─ Data-related?
    │   ├─ Shared state? → Isolate test data
    │   ├─ Random data? → Use seeded random
    │   └─ Order-dependent? → Fix test isolation
    │
    ├─ Environment-related?
    │   ├─ CI-only failures? → Check resource constraints
    │   ├─ Timezone issues? → Use UTC in tests
    │   └─ Locale issues? → Set consistent locale
    │
    └─ External dependency?
        ├─ Third-party API? → Mock it
        └─ Database? → Use test containers
```

---

## Test Pyramid

```text
                    /\
                   /  \
                  / E2E \         5-10% - Critical user journeys
                 /--------\       - Slow, expensive, high confidence
                /Integration\     15-25% - API, database, services
               /--------------\   - Medium speed, good coverage
              /     Unit       \  40-60% - Functions, components
             /------------------\ - Fast, cheap, foundation
```

**Target coverage by layer:**

| Layer | Coverage | Speed | Confidence |
|-------|----------|-------|------------|
| Unit | 80%+ | ~1000/sec | Low (isolated) |
| Integration | 70%+ | ~10/sec | Medium |
| E2E | Critical paths | ~1/sec | High |

---

## Core Capabilities

### Unit Testing

- **Frameworks**: Vitest, Jest, pytest, Go testing
- **Patterns**: AAA (Arrange-Act-Assert), Given-When-Then
- **Mocking**: Dependency injection, test doubles
- **Coverage**: Line, branch, function coverage

### Integration Testing

- **Database**: Testcontainers, in-memory DBs
- **API**: Supertest, httpx, REST-assured
- **Services**: Docker Compose, localstack
- **Fixtures**: Factory patterns, seeders

### E2E Testing

- **Web**: Playwright, Cypress
- **Mobile**: Detox, XCUITest, Espresso
- **API**: k6, Postman/Newman
- **Patterns**: Page Object Model, test locators

### Performance Testing

- **Load**: k6, Locust, Gatling
- **Profiling**: Browser DevTools, Lighthouse
- **Monitoring**: Real User Monitoring (RUM)
- **Benchmarks**: Response time, throughput, error rate

---

## Common Patterns

### AAA Pattern (Arrange-Act-Assert)

```javascript
describe('calculateDiscount', () => {
  it('should apply 10% discount for orders over $100', () => {
    // Arrange
    const order = { total: 150, customerId: 'user-1' };

    // Act
    const result = calculateDiscount(order);

    // Assert
    expect(result.discount).toBe(15);
    expect(result.finalTotal).toBe(135);
  });
});
```

### Page Object Model (E2E)

```typescript
// pages/login.page.ts
class LoginPage {
  async login(email: string, password: string) {
    await this.page.fill('[data-testid="email"]', email);
    await this.page.fill('[data-testid="password"]', password);
    await this.page.click('[data-testid="submit"]');
  }

  async expectLoggedIn() {
    await expect(this.page.locator('[data-testid="dashboard"]')).toBeVisible();
  }
}

// tests/login.spec.ts
test('user can login with valid credentials', async ({ page }) => {
  const loginPage = new LoginPage(page);
  await loginPage.login('user@example.com', 'password');
  await loginPage.expectLoggedIn();
});
```

### Test Data Factory

```typescript
// factories/user.factory.ts
export const createUser = (overrides = {}) => ({
  id: faker.string.uuid(),
  email: faker.internet.email(),
  name: faker.person.fullName(),
  createdAt: new Date(),
  ...overrides,
});

// Usage in tests
const admin = createUser({ role: 'admin' });
const guest = createUser({ role: 'guest', email: 'guest@test.com' });
```

---

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Test Suite
on: [push, pull_request]

jobs:
  unit-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
      - run: npm ci
      - run: npm run test:unit -- --coverage
      - uses: codecov/codecov-action@v3

  integration-tests:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: test
    steps:
      - uses: actions/checkout@v4
      - run: npm ci
      - run: npm run test:integration

  e2e-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: npm ci
      - run: npx playwright install --with-deps
      - run: npm run test:e2e
```

### Quality Gates

| Gate | Threshold | Action on Failure |
|------|-----------|-------------------|
| Unit test coverage | 80% | Block merge |
| All tests pass | 100% | Block merge |
| No new critical bugs | 0 | Block merge |
| Performance regression | <10% | Warning |
| Security vulnerabilities | 0 critical | Block deploy |

---

## Anti-Patterns to Avoid

| Anti-Pattern | Problem | Solution |
|--------------|---------|----------|
| Testing implementation | Breaks on refactor | Test behavior, not internals |
| Shared mutable state | Flaky tests | Isolate test data |
| sleep() in tests | Slow, unreliable | Use proper waits/assertions |
| Testing everything E2E | Slow, expensive | Use test pyramid |
| No test data cleanup | Test pollution | Reset state between tests |
| Ignoring flaky tests | False confidence | Fix or quarantine immediately |
| Copy-paste tests | Hard to maintain | Use factories and helpers |
| Testing third-party code | Wasted effort | Trust libraries, test integration |

---

## AI-Assisted Testing (2025 Trend)

72% of teams are exploring AI-driven testing workflows. Key patterns:

| Tool | Use Case | Example |
|------|----------|---------|
| **GitHub Copilot** | Generate unit tests | "Write tests for this function" in editor |
| **Playwright + MCP** | AI-generated E2E | Model Context Protocol enables AI agents to create/execute tests |
| **Visual AI** | Smart visual regression | Applitools, Percy AI ignore irrelevant changes |
| **Test Generation** | Edge case discovery | AI analyzes code paths for missing coverage |

**When to use AI testing:**

- Generating boilerplate test scaffolding
- Suggesting edge cases from code analysis
- Visual regression with intelligent diffing
- Test data generation from schemas

**When NOT to use AI testing:**

- Critical business logic (review manually)
- Security-sensitive assertions
- Performance benchmarks (needs human baseline)

---

## Navigation

### Resources

- [resources/operational-playbook.md](resources/operational-playbook.md) — Testing pyramid guidance, BDD/test data patterns, CI gates, and anti-patterns
- [resources/playwright-webapp-testing.md](resources/playwright-webapp-testing.md) — Playwright decision tree, server lifecycle helper, and recon-first scripting pattern
- [resources/comprehensive-testing-guide.md](resources/comprehensive-testing-guide.md) — Full testing methodology reference
- [resources/test-automation-patterns.md](resources/test-automation-patterns.md) — Automation patterns and best practices
- [resources/shift-left-testing.md](resources/shift-left-testing.md) — Early testing strategies

### Templates

- [templates/test-strategy-template.md](templates/test-strategy-template.md) — Test strategy starter
- [templates/automation-pipeline-template.md](templates/automation-pipeline-template.md) — CI/CD automation pattern
- [templates/unit/template-jest-vitest.md](templates/unit/template-jest-vitest.md) — Unit testing
- [templates/integration/template-api-integration.md](templates/integration/template-api-integration.md) — Integration/API testing
- [templates/e2e/template-playwright.md](templates/e2e/template-playwright.md) — Playwright E2E
- [templates/bdd/template-cucumber-gherkin.md](templates/bdd/template-cucumber-gherkin.md) — BDD/Gherkin
- [templates/performance/template-k6-load-testing.md](templates/performance/template-k6-load-testing.md) — k6 performance
- [templates/visual-regression/template-visual-testing.md](templates/visual-regression/template-visual-testing.md) — Visual regression

### Data

- [data/sources.json](data/sources.json) — Curated external references

---

## Related Skills

- [../software-backend/SKILL.md](../software-backend/SKILL.md) — API design and backend patterns to test
- [../software-frontend/SKILL.md](../software-frontend/SKILL.md) — Frontend components and UI patterns
- [../ops-devops-platform/SKILL.md](../ops-devops-platform/SKILL.md) — CI/CD pipelines and infrastructure
- [../qa-debugging/SKILL.md](../qa-debugging/SKILL.md) — Debugging failing tests
- [../software-security-appsec/SKILL.md](../software-security-appsec/SKILL.md) — Security testing patterns
