---
name: qa-testing-playwright
description: "Use when writing E2E web tests, debugging flaky tests, or setting up Playwright CI. Covers: stable selectors (getByRole), parallelization/sharding, flake control, network mocking, visual testing, MCP/AI automation, and CI/CD integration."
---

# QA Testing (Playwright)

High-signal, cost-aware E2E testing for web applications.

Core docs:
- https://playwright.dev/docs/best-practices
- https://playwright.dev/docs/locators
- https://playwright.dev/docs/test-retries
- https://playwright.dev/docs/trace-viewer
- https://playwright.dev/docs/test-sharding
- https://playwright.dev/docs/ci

## Defaults (2026)

- Keep E2E thin: protect critical user journeys only; push coverage down (unit/integration/contract).
- Locator priority: `getByRole` → `getByLabel`/`getByText` → `getByTestId` (fallback).
- Waiting: rely on Playwright auto-wait + web-first assertions; no sleeps/time-based waits.
- Isolation: tests must run alone, in parallel, and in any order; eliminate shared mutable state.
- Flake posture: retries are a debugging tool; treat rerun-pass as a failure signal and fix root cause.
- CI posture: smoke gate on PRs; shard/parallelize regression on schedule; always keep artifacts (trace/video/screenshot).

## Quick Start

| Command | Purpose |
|---------|---------|
| `npm init playwright@latest` | Initialize Playwright |
| `npx playwright test` | Run all tests |
| `npx playwright test --grep @smoke` | Run smoke tests |
| `npx playwright test --project=chromium` | Run a single project |
| `npx playwright test --ui` | Debug with UI mode |
| `npx playwright test --debug` | Step through a test |
| `npx playwright show-trace trace.zip` | Inspect trace artifacts |
| `npx playwright show-report` | Inspect HTML report |

## When to Use

- E2E tests for web applications
- Test user authentication flows
- Verify form submissions
- Test responsive designs
- Automate browser interactions
- Set up Playwright in CI/CD

## When NOT to Use

| Scenario | Use Instead |
|----------|-------------|
| Unit testing | Jest, Vitest, pytest |
| API contracts | [qa-api-testing-contracts](../qa-api-testing-contracts/SKILL.md) |
| Load testing | k6, Locust, Artillery |
| Mobile native | Appium |

## Authoring Rules

### Locator Strategy

```typescript
// 1. Role locators (preferred)
await page.getByRole('button', { name: 'Sign in' }).click();

// 2. Label/text locators
await page.getByLabel('Email').fill('user@example.com');

// 3. Test IDs (fallback)
await page.getByTestId('user-avatar').click();
```

### Flake Control

- Avoid sleeps; use Playwright auto-wait
- Use retries as signal, not a crutch
- Capture trace/screenshot/video on failure
- Prefer user-like interactions; avoid `force: true`

## Workflow

- Write the smallest test that proves the user outcome (intent + oracle).
- Stabilize locators and assertions before adding more steps.
- Make state explicit: seed per test/worker, clean up deterministically, mock third-party boundaries.
- In CI: shard/parallelize, capture artifacts, and fail fast on rerun-pass flakes.

## Debugging Checklist

If something is flaky:
- Open trace first; identify whether it is selector ambiguity, missing wait, or state leakage.
- Replace brittle selectors with semantic locators; replace sleeps with `expect(...)` or a targeted wait.
- Reduce global timeouts; add scoped timeouts only when the product truly needs it.
- If it only fails in CI, look for concurrency, cold-start, CPU starvation, and environment differences.

## Do / Avoid

- Make tests independent and deterministic
- Use network mocking for third-party deps
- Run smoke E2E on PRs; full regression on schedule

- "Test everything E2E" as default
- Weakening assertions to "fix" flakes
- Auto-healing that weakens assertions

## Execution Preflight (High ROI)

Run this preflight before expensive E2E runs to prevent avoidable failures.

### Preflight Checklist

1. Repository shape:
- Confirm working directory and expected app root exist.
- Verify spec paths before execution (`rg --files tests/e2e | rg <target>`).

2. Port/process hygiene:
- Check and clear stale dev server port before run (example: `lsof -i :3001`).
- Avoid parallel local servers colliding with Playwright `webServer`.

3. Command validity:
- Validate CLI flags for current tool versions before batch runs.
- Prefer exact spec paths or `--grep` over broad globs during triage.

4. Artifact expectations:
- Confirm result artifact paths exist before reading (`test -f <error-context.md>`).
- If artifact path missing, inspect latest `test-results` index first.

### Triage Sequence (Fastest Signal)

1. Reproduce one failing test with `--workers=1`.
2. Capture trace/video/screenshot for that single failure.
3. Fix determinism root cause.
4. Re-run targeted suite.
5. Only then run broad regression.

### Failure Patterns to Treat as Environment, Not Product Bugs

- `EADDRINUSE` on Playwright web server port
- Missing spec/result paths from stale assumptions
- Shell glob expansion failures for bracketed route segments


## Resources

| Resource | Purpose |
|----------|---------|
| [references/playwright-mcp.md](references/playwright-mcp.md) | MCP & AI testing |
| [references/playwright-patterns.md](references/playwright-patterns.md) | Advanced patterns |
| [references/playwright-ci.md](references/playwright-ci.md) | CI configurations |
| [references/playwright-authentication.md](references/playwright-authentication.md) | Auth patterns and session management |
| [references/visual-regression-testing.md](references/visual-regression-testing.md) | Visual regression strategies |
| [references/api-testing-playwright.md](references/api-testing-playwright.md) | API testing with APIRequestContext |
| [data/sources.json](data/sources.json) | Documentation links |

## Templates

| Template | Purpose |
|----------|---------|
| [assets/template-playwright-e2e-review-checklist.md](assets/template-playwright-e2e-review-checklist.md) | E2E review checklist |
| [assets/template-playwright-fail-on-flaky-reporter.js](assets/template-playwright-fail-on-flaky-reporter.js) | Fail CI on rerun-pass flakes |

## Related Skills

| Skill | Purpose |
|-------|---------|
| [qa-testing-strategy](../qa-testing-strategy/SKILL.md) | Overall test strategy |
| [software-frontend](../software-frontend/SKILL.md) | Frontend development |
| [ops-devops-platform](../ops-devops-platform/SKILL.md) | CI/CD integration |
