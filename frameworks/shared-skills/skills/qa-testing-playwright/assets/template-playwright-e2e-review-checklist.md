# Playwright E2E Review Checklist (Selectors, Parallelization, Flake Rules)

Use this checklist in PR review and when triaging flaky E2E suites.

## Core

### Scope and ROI

- [ ] Test protects a critical user journey or high-risk integration (not "nice to have").
- [ ] Lower-layer alternatives considered (unit/integration/contract).
- [ ] Test name states user intent and expected outcome.

### Selector Strategy (Stability)

- [ ] Uses `getByRole` / `getByLabel` / `getByText` by default (Playwright locators: https://playwright.dev/docs/locators).
- [ ] Uses `data-testid` only when semantic selectors are not feasible.
- [ ] Avoids brittle CSS/XPath selectors.

### Assertions and Waiting

- [ ] Uses web-first assertions (`expect(...)`) and Playwright auto-wait (https://playwright.dev/docs/best-practices).
- [ ] No `sleep` / time-based waits.
- [ ] Timeouts are scoped (per action/assert) rather than global increases.

### Test Isolation and Data

- [ ] Test is independent (can run alone, in parallel, in any order).
- [ ] Data setup is explicit (fixtures/factories) and cleanup is deterministic.
- [ ] No reliance on shared accounts, shared carts, or global state unless isolated by tenant.

### Network and Dependencies

- [ ] Third-party dependencies are mocked at the boundary (route interception) unless explicitly required.
- [ ] Test validates your integration contract, not a third-party UI.

### Flake Control

- [ ] Retries configured intentionally; rerun-pass tests are treated as flakes (https://playwright.dev/docs/test-retries).
- [ ] Trace/screenshot/video captured on failure and attached to CI artifacts (trace viewer: https://playwright.dev/docs/trace-viewer).

### Parallelization and Sharding (CI Economics)

- [ ] Suite is safe to run with multiple workers (no shared mutable state).
- [ ] Sharding plan exists for large suites (https://playwright.dev/docs/test-sharding).
- [ ] PR gate is a smoke subset; full regression runs on schedule or per-release.

### Visual Testing (If Used)

- [ ] Visual checks are limited to stable screens/components with a review workflow.
- [ ] Snapshots are not used as a substitute for functional assertions.

## Optional: AI / Automation

Do:
- Use AI to scaffold tests and page objects, then apply this checklist to harden selectors, assertions, and data isolation.
- Use AI to summarize trace artifacts and propose hypotheses; verify with evidence and stable assertions.

Avoid:
- Auto-healing by weakening assertions or switching to brittle selectors.
