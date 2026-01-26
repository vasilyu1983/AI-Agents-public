---
name: qa-testing-strategy
description: Risk-based quality engineering test strategy for software delivery. Use when defining or updating test strategy, selecting unit/integration/contract/E2E/performance/security coverage, setting CI quality gates and suite budgets, managing flaky tests and test data, and operationalizing observability-first debugging and release criteria.
---

# QA Testing Strategy (Jan 2026)

Risk-based quality engineering strategy for modern software delivery.

**Core references**: curated links in `data/sources.json` (SLOs/error budgets, contracts, E2E, OpenTelemetry). Start with `references/operational-playbook.md` for a compact, navigable overview.

## Scope

- Create or update a risk-based test strategy (what to test, where, and why)
- Define quality gates and release criteria (merge vs deploy)
- Select the smallest effective layer (unit → integration → contract → E2E)
- Make failures diagnosable (artifacts, logs/traces, ownership)
- Operationalize reliability (flake SLO, quarantines, suite budgets)

## Use Instead

| Need | Skill |
|------|-------|
| Debug failing tests or incidents | [qa-debugging](../qa-debugging/SKILL.md) |
| Test LLM agents/personas | [qa-agent-testing](../qa-agent-testing/SKILL.md) |
| Perform security audit/threat model | [software-security-appsec](../software-security-appsec/SKILL.md) |
| Design CI/CD pipelines and infra | [ops-devops-platform](../ops-devops-platform/SKILL.md) |

## Quick Reference

| Test Type | Goal | Typical Use |
|-----------|------|-------------|
| Unit | Prove logic and invariants fast | Pure functions, core business rules |
| Component | Validate UI behavior in isolation | UI components and state transitions |
| Integration | Validate boundaries with real deps | API + DB, queues, external adapters |
| Contract | Prevent breaking changes cross-team | OpenAPI/AsyncAPI/JSON Schema/Protobuf |
| E2E | Validate critical user journeys | 1–2 “money paths” per product area |
| Performance | Enforce budgets and capacity | Load, stress, soak, regression trends |
| Visual | Catch UI regressions | Layout/visual diffs on stable pages |
| Accessibility | Automate WCAG checks | axe smoke + targeted manual audits |
| Security | Catch common web vulns early | DAST smoke + critical checks in CI |

## Default Workflow

1. Clarify scope and risk: critical journeys, failure modes, and non-functional risks (latency, data loss, auth).
2. Define quality signals: SLOs/error budgets, contract/schema checks, and what blocks merge vs blocks deploy.
3. Choose the smallest effective layer (unit → integration → contract → E2E).
4. Make failures diagnosable: artifacts + correlation IDs (logs/traces/screenshots), clear ownership, deflake runbook.
5. Operationalize: flake SLO, quarantine with expiry, suite budgets (PR gate vs scheduled), dashboards.

## Test Pyramid

```text
           /\
          /E2E\          5-10% - Critical journeys
         /------\
        /Integr. \       15-25% - API, DB, queues
       /----------\
      /Component \       20-30% - UI modules
     /------------\
    /   Unit      \      40-60% - Logic and invariants
   /--------------\
```

## Decision Tree: Test Strategy

```text
Need to test: [Feature Type]
    │
    ├─ Pure business logic/invariants? → Unit tests (mock boundaries)
    │
    ├─ UI component/state transitions? → Component tests
    │   └─ Cross-page user journey? → E2E tests
    │
    ├─ API Endpoint?
    │   ├─ Single service boundary? → Integration tests (real DB/deps)
    │   └─ Cross-service compatibility? → Contract tests (schema/versioning)
    │
    ├─ Event-driven/API schema evolution? → Contract + backward-compat tests
    │
    └─ Performance-critical? → k6 load testing
```

## Core QA Principles

### Definition of Done

- Strategy is risk-based: critical journeys + failure modes explicit
- Test portfolio is layered: fast checks catch most defects
- CI is economical: fast pre-merge gates, heavy suites scheduled
- Failures are diagnosable: actionable artifacts (logs/trace/screenshots)
- Flakes managed with SLO and deflake runbook

### Shift-Left Gates (Pre-Merge)

- Contracts: OpenAPI/AsyncAPI/JSON Schema validation
- Static checks: lint, typecheck, secret scanning
- Fast tests: unit + key integration (avoid full E2E as PR gate)

### Shift-Right (Post-Deploy)

- Synthetic checks for critical paths (monitoring-as-tests)
- Canary analysis: compare SLO signals and key metrics before ramping
- Feature flags for safe rollouts and fast rollback
- Convert incidents into regression tests (prefer lower layers first)

### CI Economics

| Budget | Target |
|--------|--------|
| PR gate | p50 ≤ 10 min, p95 ≤ 20 min |
| Mainline health | ≥ 99% green builds/day |

### Flake Management

- Define: test fails without product change, passes on rerun
- Track weekly: `flaky_failures / total_test_executions` (where `flaky_failure = fail_then_pass_on_rerun`)
- SLO: Suite flake rate ≤ 1% weekly
- Quarantine policy with owner and expiry
- Use the deflake runbook: [template-flaky-test-triage-deflake-runbook.md](assets/runbooks/template-flaky-test-triage-deflake-runbook.md)

## Common Patterns

### AAA Pattern

```javascript
it('should apply discount', () => {
  // Arrange
  const order = { total: 150 };
  // Act
  const result = calculateDiscount(order);
  // Assert
  expect(result.discount).toBe(15);
});
```

### Page Object Model (E2E)

```typescript
class LoginPage {
  async login(email: string, password: string) {
    await this.page.fill('[data-testid="email"]', email);
    await this.page.fill('[data-testid="password"]', password);
    await this.page.click('[data-testid="submit"]');
  }
}
```

## Anti-Patterns

| Anti-Pattern | Problem | Solution |
|--------------|---------|----------|
| Testing implementation | Breaks on refactor | Test behavior |
| Shared mutable state | Flaky tests | Isolate test data |
| sleep() in tests | Slow, unreliable | Use proper waits |
| Everything E2E | Slow, expensive | Use test pyramid |
| Ignoring flaky tests | False confidence | Fix or quarantine |

## Do / Avoid

### Do

- Write tests against stable contracts and user-visible behavior
- Treat flaky tests as P1 reliability work
- Make "how to debug this failure" part of every suite

### Avoid

- "Everything E2E" as default
- Sleeps/time-based waits (use event-based)
- Coverage % as primary quality KPI

## Resources

| Resource | Purpose |
|----------|---------|
| [comprehensive-testing-guide.md](references/comprehensive-testing-guide.md) | End-to-end playbook across layers |
| [operational-playbook.md](references/operational-playbook.md) | Testing pyramid, BDD, CI gates |
| [shift-left-testing.md](references/shift-left-testing.md) | Contract-first, BDD, continuous testing |
| [test-automation-patterns.md](references/test-automation-patterns.md) | Reliable patterns and anti-patterns |
| [playwright-webapp-testing.md](references/playwright-webapp-testing.md) | Playwright patterns |
| [chaos-resilience-testing.md](references/chaos-resilience-testing.md) | Chaos engineering |
| [observability-driven-testing.md](references/observability-driven-testing.md) | OpenTelemetry, trace-based |
| [contract-testing-2026.md](references/contract-testing-2026.md) | Pact, Specmatic |
| [synthetic-test-data.md](references/synthetic-test-data.md) | Privacy-safe, ephemeral test data |

## Templates

| Template | Purpose |
|----------|---------|
| [template-test-case-design.md](assets/template-test-case-design.md) | Given/When/Then and test oracles |
| [test-strategy-template.md](assets/test-strategy-template.md) | Risk-based strategy |
| [template-flaky-test-triage.md](assets/runbooks/template-flaky-test-triage-deflake-runbook.md) | Flake triage runbook |
| [template-jest-vitest.md](assets/unit/template-jest-vitest.md) | Unit test patterns |
| [template-api-integration.md](assets/integration/template-api-integration.md) | API + DB integration tests |
| [template-playwright.md](assets/e2e/template-playwright.md) | Playwright E2E |
| [template-visual-testing.md](assets/visual-regression/template-visual-testing.md) | Visual regression testing |
| [template-k6-load-testing.md](assets/performance/template-k6-load-testing.md) | k6 performance |
| [automation-pipeline-template.md](assets/automation-pipeline-template.md) | CI stages, budgets, gates |
| [template-cucumber-gherkin.md](assets/bdd/template-cucumber-gherkin.md) | BDD feature files and steps |

## Data

| File | Purpose |
|------|---------|
| [sources.json](data/sources.json) | External references |

## Related Skills

- [qa-debugging](../qa-debugging/SKILL.md) — Debugging failing tests
- [qa-agent-testing](../qa-agent-testing/SKILL.md) — Testing AI agents
- [software-backend](../software-backend/SKILL.md) — API patterns to test
- [ops-devops-platform](../ops-devops-platform/SKILL.md) — CI/CD pipelines
