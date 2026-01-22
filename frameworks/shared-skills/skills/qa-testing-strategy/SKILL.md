---
name: qa-testing-strategy
description: Risk-based quality engineering test strategy across unit, integration, contract, E2E, performance, and security testing with shift-left gates, flake control, CI economics, and observability-first debugging.
---

# QA Testing Strategy (Dec 2025) — Quick Reference

Use this skill when the primary focus is how to test software effectively (risk-first, automation-first, observable systems) rather than how to implement features.

---

Core references: SLO/error budgets and troubleshooting patterns from the Google SRE Book ([Service Level Objectives](https://sre.google/sre-book/service-level-objectives/), [Effective Troubleshooting](https://sre.google/sre-book/effective-troubleshooting/)); contract-driven API documentation via OpenAPI ([OAS](https://spec.openapis.org/oas/latest.html)); and E2E ergonomics/practices via Playwright docs ([Best Practices](https://playwright.dev/docs/best-practices)).

## Core QA (Default)

### Outcomes (Definition of Done)

- Strategy is risk-based: critical user journeys + likely failure modes are explicit.
- Test portfolio is layered: fastest checks catch most defects; slow checks are minimal and high-signal.
- CI is economical: fast pre-merge gates; heavy suites are scheduled or scoped.
- Failures are diagnosable: every failure yields actionable artifacts (logs/trace/screenshots/crash reports).
- Flakes are managed as reliability debt with an SLO and a deflake runbook.

### Quality Model: Risk, Journeys, Failure Modes

- Model risk as `impact x likelihood x detectability` per journey.
- Write failure modes per journey: auth/session, permissions, data integrity, dependency failure, latency, offline/degraded UX, concurrency/races.
- Define oracles per test: business rule oracle, contract/schema oracle, security oracle, accessibility oracle, performance oracle.

### Test Portfolio (Modern Equivalent of the Pyramid)

- Prefer unit + component + contract + integration as the default safety net; keep E2E for thin, critical journeys.
- Add exploratory testing for discovery and usability; convert findings into automated checks when ROI is positive.
- Use the smallest scope that detects the bug class:
  - Bug in business logic: unit/property-based.
  - Bug in service wiring/data: integration/contract.
  - Bug in cross-service compatibility: contract + a small number of integration scenarios.
  - Bug in user journey: E2E (critical path only).

### Shift-Left Gates (Pre-Merge by Default)

- Contracts: OpenAPI/AsyncAPI/JSON Schema validation where applicable ([OpenAPI](https://spec.openapis.org/oas/latest.html), [AsyncAPI](https://www.asyncapi.com/docs/reference/specification/v3.0.0), [JSON Schema](https://json-schema.org/)).
- Static checks: lint, typecheck, dependency scanning, secret scanning.
- Fast tests: unit + key integration checks; avoid full E2E as a PR gate unless the product is E2E-only.

### Coverage Model (Explicitly Separate)

- Code coverage answers: “What code executed?” (useful as a smoke signal).
- Risk coverage answers: “What user/business risk is reduced?” (the real target).
- REQUIRED: every critical journey has at least one automated check at the lowest effective layer.

### CI Economics (Budgets and Levers)

- Budgets [Inference]:
  - PR gate: p50 <= 10 min, p95 <= 20 min.
  - Mainline health: >= 99% green builds per day.
- Levers:
  - Parallelize by layer and shard long-running suites (Playwright supports sharding in CI: [Sharding](https://playwright.dev/docs/test-sharding)).
  - Cache dependencies and test artifacts where your CI supports it.
  - Run “full regression” on schedule (nightly) and “risk-scoped regression” on PRs.

### Flake Management (SLO + Runbook)

- Define flake: test fails without product change and passes on rerun.
- Track flake rate as: `rerun_pass / (rerun_pass + rerun_fail)` for a suite.
- SLO examples [Inference]:
  - Suite flake rate <= 1% weekly.
  - Time-to-deflake: p50 <= 2 business days, p95 <= 7 business days.
- REQUIRED: quarantine policy and deflake playbook: `assets/runbooks/template-flaky-test-triage-deflake-runbook.md`.
- For rate-limited endpoints, run serially, reuse tokens, and add backoff for 429s; isolate 429 tests to avoid poisoning other suites.

### Debugging Ergonomics (Make Failures Cheap)

- Always capture first failure context: request IDs, trace IDs, build URL, seed, test data IDs.
- Standardize artifacts per layer:
  - Unit/integration: structured logs + minimal repro input.
  - E2E: trace + screenshot/video on failure (Playwright tooling: [Trace Viewer](https://playwright.dev/docs/trace-viewer)).
  - Mobile: `xcresult` bundles + screenshots + device logs.

### Do / Avoid

Do:
- Write tests against stable contracts and user-visible behavior.
- Treat flaky tests as P1 reliability work; quarantine only with an owner and expiry.
- Make “how to debug this failure” part of every suite’s definition of done.

Avoid:
- “Everything E2E” as a default (slow, expensive, low-signal).
- Sleeps/time-based waits (prefer assertions and event-based waits).
- Using coverage % as the primary quality KPI (use risk coverage + defect escape rate).

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

## Optional: AI / Automation

Use AI assistance only as an accelerator for low-risk work; validate outputs with objective checks and evidence.

### AI-Assisted Test Generation (2026 Patterns)

| Use Case | AI Role | Human Role | Tools |
|----------|---------|------------|-------|
| Test scaffolding | Generate file structure, boilerplate | Review, customize assertions | Copilot, Cursor, Claude |
| Edge case discovery | Propose boundary conditions | Validate relevance, add oracles | promptfoo, DeepEval |
| Test data creation | Generate realistic fixtures | Verify data constraints | Faker + AI |
| Flake analysis | Cluster similar failures | Determine root cause | Observability + AI |
| Coverage gap analysis | Identify untested paths | Prioritize by risk model | Coverage tools + AI |

**Guardrails for AI-Generated Tests:**

1. **Never trust assertions blindly** - AI may generate confident but incorrect oracles
2. **Require human review for security tests** - AI may miss subtle vulnerabilities
3. **Version control AI prompts** - Reproducibility requires prompt versioning
4. **Track AI vs human test ratio** - Monitor over-reliance on generated tests
5. **Validate against ground truth** - Use golden datasets for regression

**Emerging Tools (verify with web search):**

- **Codium AI** - AI test generation with coverage analysis
- **Diffblue Cover** - Java unit test generation
- **Meticulous** - Automated E2E test recording
- **Octomind** - AI-driven E2E test maintenance

Do:
- Generate scaffolding (test file skeletons, fixtures) and then harden manually.
- Use AI to propose edge cases, then select based on your risk model and add explicit oracles.
- Use AI to summarize flaky-test clusters, but base actions on logs/traces and rerun evidence.

Avoid:
- Accepting generated assertions without validating the oracle (risk: confident nonsense).
- Letting AI "heal" tests by weakening assertions (risk: silent regressions).

Safety references (optional):
- OWASP Top 10 for LLM Applications: https://owasp.org/www-project-top-10-for-large-language-model-applications/
- NIST AI Risk Management Framework: https://www.nist.gov/itl/ai-risk-management-framework

---

## Chaos Engineering & Resilience Testing (2026)

Proactive reliability validation through controlled failure injection. See [references/chaos-resilience-testing.md](references/chaos-resilience-testing.md) for full guide.

### When to Use Chaos Engineering

- Before major releases (validate failover, auto-scaling)
- Compliance audits (DORA, SOC 2 resilience requirements)
- After infrastructure changes (new regions, database migrations)
- Quarterly game days (scheduled resilience exercises)

### Core Experiments

| Category | Experiment | Validates |
|----------|------------|-----------|
| Infrastructure | Instance termination | Auto-scaling, failover |
| Infrastructure | Zone failure | Multi-AZ deployment |
| Network | Latency injection | Timeout handling, SLOs |
| Network | Packet loss | Retry logic, circuit breakers |
| Application | Dependency failure | Fallbacks, graceful degradation |
| Application | Resource exhaustion | Connection pooling, limits |

### Tools (2026)

| Tool | Best For | Open Source |
|------|----------|-------------|
| **LitmusChaos** | Kubernetes-native | Yes |
| **Gremlin** | Enterprise, multi-cloud | No (SaaS) |
| **AWS FIS** | AWS workloads | No (AWS) |
| **Steadybit** | SRE workflows | No (SaaS) |
| **Chaos Toolkit** | Extensible, CI/CD | Yes |

### Blast Radius Control

```text
Development → Full chaos (no approval)
Staging     → Targeted (team lead approval)
Production  → 1-5% canary (SRE + eng lead approval)
```

---

## Observability-Driven Testing (2026)

Use production telemetry (traces, metrics, logs) as the foundation for test design. OpenTelemetry is the 2026 de facto standard. See [references/observability-driven-testing.md](references/observability-driven-testing.md) for full guide.

### Core Workflow

```text
1. Instrument code with OpenTelemetry spans
2. Ship with traces, metrics, structured logs
3. Observe production behavior
4. Convert production traces to test cases
5. Assert on trace attributes, not just responses
```

### Trace-Based Testing (Tracetest)

```yaml
# Assert on distributed trace, not just HTTP response
specs:
  - selector: span[name="payment.process"]
    assertions:
      - attr:payment.status = "success"
      - attr:tracetest.span.duration < 500ms

  - selector: span[name="db.orders.insert"]
    assertions:
      - attr:db.operation = "INSERT"
```

### Benefits

- **Debug flaky tests** with trace context (not just logs)
- **Convert incidents to tests** automatically
- **Validate distributed behavior** across services
- **Coverage = behaviors observed** (not just lines executed)

---

## Synthetic Test Data (2026)

Ephemeral, privacy-safe test data is replacing static datasets. 60% of AI/analytics data is now synthetic.

### Why Synthetic Data

| Static Data | Synthetic Data |
|-------------|----------------|
| Privacy risks (PII) | GDPR-compliant |
| Stale, outdated | Generated on demand |
| Storage costs | Ephemeral, disposable |
| Limited edge cases | Unlimited variations |

### Synthetic Data Tools (2026)

| Tool | Best For | Features |
|------|----------|----------|
| **K2view** | Enterprise TDM | Subsetting, masking, synthetic |
| **MOSTLY AI** | Privacy-first synthetic | GDPR compliance, ML-based |
| **Synthesized** | CI/CD integration | API-first, ephemeral |
| **YData** | Data science teams | Profiling, quality scoring |
| **Faker.js** | Simple fixtures | Deterministic, lightweight |

### CI/CD Integration Pattern

```yaml
# Generate fresh synthetic data per test run
jobs:
  test:
    steps:
      - name: Generate Test Data
        run: |
          synthesized generate \
            --schema ./schemas/users.json \
            --count 1000 \
            --output ./fixtures/users.json

      - name: Run Tests
        run: npm test

      - name: Cleanup
        run: rm -rf ./fixtures  # Ephemeral, no storage
```

### Best Practices

- Generate data per test run (not shared datasets)
- Use seeded random for reproducibility
- Match production distributions (realistic edge cases)
- Dispose after test completion (ephemeral)

---

## Contract Testing (2026 Expanded)

### Approaches Comparison

| Approach | Tool | When to Use |
|----------|------|-------------|
| **Consumer-Driven (CDC)** | Pact | Consumer knows what it needs |
| **Contract-Driven (CDD)** | Specmatic | OpenAPI as single source of truth |
| **Bi-Directional (BDCT)** | Pactflow | Both sides define expectations |
| **Unified API Testing** | Karate | API, contract, and performance in one |

### Specmatic (Contract-Driven)

OpenAPI spec becomes the executable contract—no separate contract files.

```bash
# Validate API implementation against OpenAPI spec
specmatic test --contract openapi.yaml --host localhost:8080

# Generate stubs from OpenAPI for consumer testing
specmatic stub --contract openapi.yaml --port 9000
```

### Pact vs Specmatic Decision

```text
Use Pact when:
├── Consumer team owns contract definition
├── Multiple consumers with different needs
└── Gradual migration from no contracts

Use Specmatic when:
├── OpenAPI is already the source of truth
├── Strict contract-first development
└── Both provider and consumer use same spec
```

### Karate (Unified)

Single DSL for API, contract, and performance testing.

```gherkin
Feature: Order API

Scenario: Create order
  Given url 'http://localhost:8080/orders'
  And request { userId: 'user-1', productId: 'prod-1' }
  When method POST
  Then status 201
  And match response contains { orderId: '#string' }
```

---

## Navigation

### Resources

- [references/operational-playbook.md](references/operational-playbook.md) — Testing pyramid guidance, BDD/test data patterns, CI gates, and anti-patterns
- [references/playwright-webapp-testing.md](references/playwright-webapp-testing.md) — Playwright decision tree, server lifecycle helper, and recon-first scripting pattern
- [references/comprehensive-testing-guide.md](references/comprehensive-testing-guide.md) — Full testing methodology reference
- [references/test-automation-patterns.md](references/test-automation-patterns.md) — Automation patterns and best practices
- [references/shift-left-testing.md](references/shift-left-testing.md) — Early testing strategies
- [references/chaos-resilience-testing.md](references/chaos-resilience-testing.md) — Chaos engineering, resilience testing, DORA compliance
- [references/observability-driven-testing.md](references/observability-driven-testing.md) — OpenTelemetry, trace-based testing, ODD patterns

### Templates

- [assets/test-strategy-template.md](assets/test-strategy-template.md) — Risk-based test strategy one-pager
- [assets/template-test-case-design.md](assets/template-test-case-design.md) — Test case design (Given/When/Then + oracles)
- [assets/runbooks/template-flaky-test-triage-deflake-runbook.md](assets/runbooks/template-flaky-test-triage-deflake-runbook.md) — Flake triage + deflake runbook
- [assets/automation-pipeline-template.md](assets/automation-pipeline-template.md) — CI/CD automation pattern
- [assets/unit/template-jest-vitest.md](assets/unit/template-jest-vitest.md) — Unit testing
- [assets/integration/template-api-integration.md](assets/integration/template-api-integration.md) — Integration/API testing
- [assets/e2e/template-playwright.md](assets/e2e/template-playwright.md) — Playwright E2E
- [assets/bdd/template-cucumber-gherkin.md](assets/bdd/template-cucumber-gherkin.md) — BDD/Gherkin
- [assets/performance/template-k6-load-testing.md](assets/performance/template-k6-load-testing.md) — k6 performance
- [assets/visual-regression/template-visual-testing.md](assets/visual-regression/template-visual-testing.md) — Visual regression

### Data

- [data/sources.json](data/sources.json) — Curated external references

---

## Related Skills

- [../software-backend/SKILL.md](../software-backend/SKILL.md) — API design and backend patterns to test
- [../software-frontend/SKILL.md](../software-frontend/SKILL.md) — Frontend components and UI patterns
- [../ops-devops-platform/SKILL.md](../ops-devops-platform/SKILL.md) — CI/CD pipelines and infrastructure
- [../qa-debugging/SKILL.md](../qa-debugging/SKILL.md) — Debugging failing tests
- [../software-security-appsec/SKILL.md](../software-security-appsec/SKILL.md) — Security testing patterns

---

## Trend Awareness Protocol

**IMPORTANT**: When users ask recommendation questions about testing frameworks, strategies, or tools, you MUST use WebSearch to check current trends before answering.

### Trigger Conditions

- "What's the best testing framework for [language/use case]?"
- "What should I use for [unit/integration/E2E testing]?"
- "What's the latest in testing strategies?"
- "Current best practices for [test automation/CI testing]?"
- "Is [Playwright/Cypress/Jest] still relevant in 2026?"
- "[Vitest] vs [Jest]?" or "[Playwright] vs [Cypress]?"
- "Best E2E testing framework?"

### Required Searches

1. Search: `"testing best practices 2026"`
2. Search: `"[specific framework] vs alternatives 2026"`
3. Search: `"testing trends January 2026"`
4. Search: `"[E2E/unit/integration] testing frameworks 2026"`

### What to Report

After searching, provide:

- **Current landscape**: What testing tools/frameworks are popular NOW
- **Emerging trends**: New frameworks, patterns, or approaches gaining traction
- **Deprecated/declining**: Tools/approaches losing relevance or support
- **Recommendation**: Based on fresh data, not just static knowledge

### Example Topics (verify with fresh search)

- E2E frameworks (Playwright, Cypress, WebdriverIO)
- Unit testing (Vitest, Jest, pytest)
- API testing (Supertest, Postman/Newman, k6)
- Contract testing (Pact, Specmatic)
- Visual regression (Percy, Chromatic, Playwright)
- Test runners and CI integration
- AI-assisted test generation
