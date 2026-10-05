# Operational Testing Playbook

## Table of Contents

- [Navigation](#navigation)
- [Pattern: Test Shape Selection](#pattern-test-shape-selection)
- [Pattern: CI Test Gates](#pattern-ci-test-gates)
- [Coverage Goals](#coverage-goals)

Compact navigation hub for layered testing, CI gates, and ready-to-use templates. BDD, test-data management, framework selection, anti-patterns, the decision tree, the checklist and the generic test-pyramid ratios were cut from this file — they duplicated content that lives in the linked references and templates below, or restated what any current model produces unprompted; follow those links instead.

## Navigation

### Resources (Detailed Guides)

- [references/comprehensive-testing-guide.md](comprehensive-testing-guide.md) — redirect stub; content merged into this playbook and the linked references
- [references/component-testing-browser-mode.md](component-testing-browser-mode.md) — Real-browser component testing strategy for modern JS/TS UI apps
- [references/shift-left-testing.md](shift-left-testing.md) — Shift-left stage/check/blocks decision table and TDD workflow rules
- [references/schema-aware-api-fuzzing.md](schema-aware-api-fuzzing.md) — Schema-aware fuzzing for OpenAPI-driven APIs
- [references/test-automation-patterns.md](test-automation-patterns.md) — Retry rules, snapshot rules, and a flaky-test taxonomy (order-dependent, async, shared-resource, environment)
- [data/sources.json](../data/sources.json) — Curated external references for frameworks (Jest, Vitest, Playwright, k6, Cucumber), tools, and best practices

### Templates by Testing Type

**Unit Testing:**
- [assets/unit/template-jest-vitest.md](../assets/unit/template-jest-vitest.md) — Jest/Vitest unit test decisions table and AAA example

**Component Testing:**
- [assets/component/template-vitest-browser.md](../assets/component/template-vitest-browser.md) — Vitest Browser Mode component tests for real-browser UI behavior and accessibility smoke

**E2E Testing:**
- [assets/e2e/template-playwright.md](../assets/e2e/template-playwright.md) — redirect stub; see [../qa-testing-playwright/SKILL.md](../../qa-testing-playwright/SKILL.md) for the live Playwright templates

**Performance Testing:**
- [assets/performance/template-k6-load-testing.md](../assets/performance/template-k6-load-testing.md) — redirect stub; see [../qa-testing-performance/SKILL.md](../../qa-testing-performance/SKILL.md) for the live k6 templates

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

## Pattern: Test Shape Selection

The "test pyramid" is one model. Others exist and are better suited to specific architectures. Pick based on where bugs actually live in your system; the ratio between layers is an output of that choice, never an input.

| Shape | Description | Best For |
|-------|-------------|----------|
| **Pyramid** | Many unit → fewer integration → few E2E | Monoliths, logic-heavy backends, algorithmic code |
| **Trophy** (Kent C. Dodds) | Static analysis base, integration-heavy middle, few unit and few E2E | Frontend/full-stack JS/TS apps, API-driven services |
| **Honeycomb** (Spotify) | Integration at the center; unit tests minimized | Microservice architectures where bugs live at service boundaries |
| **Risk-based** (default recommendation) | Coverage allocated by defect probability and impact, not shape | Any architecture — start here when unsure |

**Decision rule**: ask "where do our production bugs actually come from?" and allocate coverage there. For microservices, integration tests are typically the highest-ROI layer. For domain-heavy monoliths, unit tests dominate. For frontend apps, integration tests on user-facing behavior (React Testing Library / component tests) outperform unit tests on implementation details.

Do not debate shapes as ideology. Pick the layer that can prove the behavior with the least cost. The shape emerges from that decision, not the other way around.

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
- A test that fails spuriously 5% of the time ejects about 5% of queue cycles; volume, not per-cycle probability, is what amplifies it (M × f ejections/day, each one re-running every merge group queued behind it).
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

## Coverage Goals

Line coverage is an execution map, not a quality bar. The only coverage gate this skill recommends is **no decrease on the PR diff**; repo-wide percentage targets are not set, because any fixed number becomes the thing teams optimise for (tests that execute a line and assert nothing).

Where a stronger bar is needed, scope it by risk and change the metric:

| Module class | Gate | Why |
|---|---|---|
| Critical paths (auth, payments, persistence, migrations, security-sensitive operations) | Mutation score on changed files, threshold calibrated per suite; every uncovered line in the diff needs a written reason | Line coverage on these modules is necessary but proves nothing about assertions |
| Domain rules and validators | Property or table-driven tests for the invariant, plus the no-decrease delta | Branch coverage misses value-space bugs a property test finds |
| Glue, adapters, UI rendering | No-decrease delta only | Cost of mutation testing exceeds the risk |

Pitfalls that make coverage numbers lie:

- Coverage from a test-impact-analysis or sharded run is not comparable to a full-suite baseline; compare full runs only.
- Coverage that rises while defect escape rate is flat means tests are executing code without asserting on it; check mutation score before celebrating.
- Coverage of generated, vendored or migration files inflates the repo average; exclude them so the delta gate measures the code the team writes.

The gate policy and threshold bands are in [Operationalising Mutation Coverage](quality-metrics-dashboard.md#operationalising-mutation-coverage).

---

