---
name: qa-testing-playwright
description: "Builds and debugs Playwright E2E suites. Use when authoring browser tests, fixing flakes, or hardening Playwright CI and locator strategy."
compatibility: Portable core. Works on Claude Code and Codex.
version: "1.3"
last_validated: 2026-07-11
---

# QA Testing (Playwright)

Core docs:
- https://playwright.dev/docs/best-practices
- https://playwright.dev/docs/locators
- https://playwright.dev/docs/auth
- https://playwright.dev/docs/api-testing
- https://playwright.dev/docs/test-retries
- https://playwright.dev/docs/test-snapshots
- https://playwright.dev/docs/trace-viewer
- https://playwright.dev/docs/test-sharding
- https://playwright.dev/docs/ci
- https://playwright.dev/docs/pom
- https://playwright.dev/docs/test-agents
- https://playwright.dev/docs/clock
- https://playwright.dev/docs/getting-started-cli
- https://playwright.dev/docs/test-components
- https://playwright.dev/docs/test-parallel#test-locks
- https://playwright.dev/docs/release-notes (check the current version before pinning)

## Quick Reference

| Need | Go to |
|------|-------|
| Run the Playwright workflow | `## Workflow` |
| Apply defaults and authoring rules | `## Defaults` and `## Authoring Rules` |
| Debug flaky or blocked runs | `## Debugging Checklist` and `## Execution Preflight` |
| Decide tool fit, selectors, flake triage order, sharding cost | `## Expert Judgment` |
| Load templates and references | `## Resources` and `## Templates` |

## Defaults

- Keep E2E thin: protect critical user journeys only; push coverage down (unit/integration/contract).
- Locator priority: `getByRole` → `getByLabel`/`getByText` → `getByTestId` (fallback).
- Waiting: rely on Playwright auto-wait + web-first assertions; no sleeps/time-based waits.
- Isolation: tests must run alone, in parallel, and in any order; eliminate shared mutable state. When a shared resource cannot be isolated (external service, global account setting), declare a named test lock (1.63+: `test(title, { lock: 'user-settings' }, fn)`) instead of `workers: 1` or `describe.serial` for the whole file.
- Local execution posture: choose one server topology first (shared dev stack or Playwright-managed `webServer`), then triage with an exact spec or named batch plus `--workers=1`.
- Flake posture: retries are a debugging tool; treat rerun-pass as a failure signal and fix root cause.
- CI flakes: prefer built-in `failOnFlakyTests` (1.52+); the custom reporter template is legacy, for pre-1.52 pins only.
- CI posture: smoke gate on PRs; shard/parallelize regression on schedule; always keep artifacts (trace/video/screenshot).
- Oracle posture: assert the user outcome; do not wait on incidental network requests when the visible result can be verified directly.
- AI posture: use Playwright codegen / test agents / MCP for scaffolding and exploration, then harden assertions and fixtures manually.
- Component tests: use the built-in stories/gallery `mount('components/X/Story')` fixture from `@playwright/test` (1.62+). The `@playwright/experimental-ct-*` packages were frozen in 1.63 and the docs now say they are removed; stay on 1.62 until migrated. See `references/playwright-patterns.md#component-testing`.
- Visual regression: native `toHaveScreenshot` when one OS/browser baseline set in Docker is enough; a hosted service when designers review diffs or the browser/OS matrix makes committed baselines unmanageable. See `references/visual-regression-testing.md`.
- Browser MCP: Playwright MCP for test generation + accessibility; Chrome DevTools MCP for performance / network / console debugging. See `references/playwright-mcp.md`.
- CLI posture: for high-throughput coding agents, prefer the Playwright CLI (`npx playwright cli`; shell commands) over Playwright MCP — it avoids the MCP protocol's per-call token overhead. Check `npx playwright cli --version` / release notes for your installed version before relying on it, since CLI availability and flags vary by release. The official docs call it token-efficient without a number; treat any specific token-count figure (e.g. a "tokens/task" comparison) as a claim to verify against your own measurement, not a quotable fact. Use MCP (`npx playwright mcp`) when persistent browser state and rich introspection are needed.
- Local iteration posture: use `npx playwright test --only-changed=main` to run only tests affected by uncommitted/branch changes during authoring; it is a heuristic over the import graph, so always run the full suite (or the deploy-gate replay) before merging — never treat `--only-changed` green as release-ready signal.

## Quick Start

| Command | Purpose |
|---------|---------|
| `npm init playwright@latest` | Initialize Playwright |
| `npx playwright test` | Run all tests |
| `npx playwright test --grep @smoke` | Run smoke tests |
| `npx playwright test --project=chromium` | Run a single project |
| `npx playwright test --ui` | Debug with UI mode |
| `npx playwright test --debug` | Step through a test |
| `npx playwright codegen` | Record a flow and bootstrap a test |
| `npx playwright init-agents --loop=claude` | Initialize test agents for Claude Code (`--loop=codex`, `vscode`, `opencode` also exist) |
| `npx playwright test --debug=cli` | Let a coding agent attach and debug a test via `playwright-cli` (1.59+) |
| `npx playwright test --last-failed` | Rerun only the tests that failed in the last run |
| `npx playwright test --fail-on-flaky-tests` | Fail CI if any test is flaky |
| `npx playwright show-trace trace.zip` | Inspect trace artifacts |
| `npx playwright show-report` | Inspect HTML report |
| `npx playwright trace open <trace.zip>` | Open a trace for CLI analysis; then `trace actions`, `trace action <n>`, `trace snapshot <n> --name after`, `trace close` (1.59+) |
| `npx playwright test --only-changed=main` | Run only tests affected by changes since `main` (heuristic — always follow with a full run before release) |

## Local Execution Topology

Use this order by default:

1. Start one shared local dev stack if the repo already provides it; prefer reusing it with `--no-server` over spawning a fresh app per rerun.
2. Prove which build handles the request: record source revision or build ID, base URL, server process/start command, environment, and service-worker or CDN cache state. A listening port can serve stale code; if identity is unavailable, label the result `runtime observed, build identity unverified`.
3. Reproduce with one exact spec or one named batch and `--workers=1`.
4. Fix and rerun the smallest affected scope.
5. Run the deploy-gate replay only after the targeted scope is green.

Default suite tiers:

- Smoke: PR gate and fastest signal.
- Targeted batch/spec: local triage and deflake work.
- Deploy-gate replay: dependency-chain or critical-journey replay for release confidence.

Avoid local full-suite reruns as the first move unless the job is explicitly “prove deploy readiness now.”

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
| Pure business-logic or data-transform correctness | Unit tests — a browser adds latency and flake with zero extra confidence |
| Cross-team API contract drift | Consumer-driven contract tests, not a UI click-path proxy |
| Component-level visual/interaction isolation at scale | Playwright stories/gallery component tests (1.62+, stable) if you already run Playwright; Storybook + Chromatic/Percy if the team reviews visual diffs in a hosted UI (see Defaults) |
| Thousands of input-combination fuzzing | Property-based testing at the unit layer; E2E cannot afford the runtime |

## Expert Judgment

### When Playwright Is the Wrong Tool

Playwright (or any browser E2E tool) is the wrong choice when a faster, cheaper layer already proves the same risk:
- If the bug class can be caught by a type system, unit test, or schema/contract check, push it down — E2E is the most expensive test layer per assertion (browser boot, network, rendering).
- If the "user journey" is actually an internal API call with no meaningful UI branching, test the API directly (`request` fixture or a dedicated API-testing skill) and skip the browser.
- If you are testing a third-party surface you do not control (payment provider hosted page, OAuth consent screen), do not chase it with E2E; mock the boundary and test your own integration contract instead — third-party UI changes make these tests flaky by design, not by mistake.
- If the same risk is already covered by a component test or visual snapshot at a fraction of the cost, do not duplicate it in E2E "just to be safe" — duplicate coverage without duplicate risk is waste, not thoroughness.

### Selector-Strategy Decision Rule

Pick the locator in this order, and stop at the first one that resolves unambiguously to exactly one element:
1. `getByRole` with an accessible name — this is what a screen reader and a real user both key off, so it survives markup refactors.
2. `getByLabel` / `getByText` — use when there is no meaningful role (plain text, decorative containers) but the visible copy is stable.
3. `getByTestId` — use only when the element has no stable role/label (e.g., a canvas, a drag handle, a duplicate-name list item) or when semantic locators would force asserting on implementation detail (raw CSS class, generated ID).
Never fall back to raw CSS or XPath as a first resort — they are a signal that the markup itself may need an accessibility fix, not just a test workaround.

### Flakiness Triage Order (Fastest Signal First)

Before touching a single assertion, classify the failure in this order — each step is strictly cheaper than the next, so do not skip ahead:
1. **Selector ambiguity** — trace shows the locator resolved to 0 or 2+ elements. Fix the locator, not the wait.
2. **Missing wait / race** — trace shows the action fired before the element was actionable. Replace with a web-first assertion; never add a fixed sleep.
3. **State leakage** — failure only reproduces after other tests ran (parallel workers, shared fixtures, undropped test data). Fix isolation before touching this test's own code. If the shared resource cannot be isolated, put a named `lock` on exactly the tests that touch it (1.63+) rather than serializing the suite.
4. **Environment** — only fails in CI, not locally; look at concurrency, cold start, CPU starvation, and container resource limits before assuming a product bug.
5. **Stateful-app classes** — for auth-heavy or backend-driven apps, also classify `auth-state`, `state-sync`, `optional-network`, and `degraded-mode` (see `### Stateful App Failure Classes`) before assuming a product bug.
6. **Product regression** — only after 1-5 are ruled out with trace evidence, treat the failure as reflecting the app under test and file/fix accordingly.
Retries mask all of these; use `retries` to gather evidence (trace/video) on the first CI run, but treat "passed on retry" as an unresolved defect, not a pass (`failOnFlakyTests: true`).

Flake forensics tooling (check availability against your pinned version):
- `retryStrategy: 'isolated'` (1.62+) runs all retries at the end, one by one in a single worker. A test that fails in-suite but passes isolated points to interference (step 3); one that still fails isolated points to steps 1, 2 or 6.
- `trace: 'retain-on-failure-and-retries'` (1.59+; a `video` mode since 1.61) keeps both the failing and the passing attempt, so you can diff them side by side.
- `--repeat-each=N` on the single suspect test proves a fix; `--last-failed` reruns only the previous failures.
- Quarantine: tag `@flaky` with an owner and an exit date, and exclude it from the gate with `--grep-invert @flaky` or a `Reporter.preprocess()` skip list (1.62+). A quarantined test with no owner is a deleted test.

### CI Parallelism Economics (Worked Example)

Sharding trades machine-cost for wall-clock time; the math to decide is straightforward. Given a suite that takes `T` minutes single-threaded and `N` shards each with `M` machine-minutes of fixed overhead (checkout, install, browser download):
- Wall-clock per shard ≈ `T/N + M`.
- Total machine-minutes billed ≈ `N × (T/N + M) = T + N×M`.

Example: `T = 60` min, `M = 3` min fixed overhead per shard/job.
- 1 shard: wall-clock = 63 min, billed = 63 machine-minutes.
- 4 shards: wall-clock = 60/4 + 3 = 18 min, billed = 4 × 18 = 72 machine-minutes.
- 12 shards: wall-clock = 60/12 + 3 = 8 min, billed = 12 × 8 = 96 machine-minutes.

Sharding always costs more total machine-minutes (because fixed overhead is paid N times) — the return is faster PR feedback, not lower spend. The judgment call: shard the PR-gate smoke suite (wall-clock matters, suite is small so `N×M` stays small) and run the full regression unsharded or lightly sharded on a schedule (spend matters more than latency there). Re-derive this ratio with your own `T` and `M` before picking a shard count — do not copy `N=4` by convention.

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
- Prefer built-in `failOnFlakyTests` in CI
- Capture trace/screenshot/video on failure
- Prefer user-like interactions; avoid `force: true`

## Workflow

- Write the smallest test that proves the user outcome (intent + oracle).
- Make execution topology explicit before triage: shared dev stack vs Playwright `webServer`, plus exact start/stop commands.
- Reproduce with one exact spec or named batch before expanding scope.
- Stabilize locators and assertions before adding more steps.
- Make state explicit: seed per test/worker, clean up deterministically, and verify auth/subscription/test-data reset paths for stateful apps.
- Mock or isolate third-party boundaries where they are not part of the user-facing oracle.
- In CI: shard/parallelize, capture artifacts, and fail fast on rerun-pass flakes.

## Debugging Checklist

If something is flaky:
- Open trace and error artifacts first; identify whether the failure is selector ambiguity, missing wait, state leakage, or the wrong server topology.
- If the trace lands on login or an unexpected redirect, classify `auth-state` before changing assertions.
- If browser logs show `429` or `Retry-After` on side endpoints, decide whether that request is part of the oracle or only noise.
- Replace brittle selectors with semantic locators; replace sleeps with `expect(...)`, an auth-aware navigation helper, or a targeted readiness assertion.
- Remove waits on incidental requests; assert the visible route, action, or content outcome instead.
- Reduce global timeouts; add scoped timeouts only when the product truly needs it — prefer a per-action timeout or `test.step(name, fn, { timeout })` over raising `timeout` in `playwright.config.ts`.
- If it only fails in CI, look for concurrency, cold-start, CPU starvation, and environment differences.

## Execution Preflight

Before expensive E2E runs, run the preflight in [references/playwright-preflight-sandbox.md](references/playwright-preflight-sandbox.md) (spec paths, port/host binding, one server topology, build locks, per-test timeout budget, `EPERM`/`EACCES` escalation) and record the answers with [assets/template-playwright-preflight-checklist.md](assets/template-playwright-preflight-checklist.md). Treat `EADDRINUSE`, missing spec/result paths and shell-glob failures on bracketed route segments as environment failures, not product bugs.

### Stateful App Failure Classes

- `auth-state`: protected route unexpectedly redirects to login or loses storage/session state.
- `state-sync`: backend reset or webhook succeeded, but UI has not converged yet.
- `optional-network`: a side request failed, but the user-visible oracle may still be correct.
- `degraded-mode`: rate limits or fallback UX activated and should be asserted intentionally.

## Resources

| Resource | Purpose |
|----------|---------|
| [references/playwright-mcp.md](references/playwright-mcp.md) | MCP & AI testing |
| [references/playwright-patterns.md](references/playwright-patterns.md) | Advanced patterns |
| [references/playwright-ci.md](references/playwright-ci.md) | CI configurations |
| [references/playwright-authentication.md](references/playwright-authentication.md) | Auth patterns and session management |
| [references/visual-regression-testing.md](references/visual-regression-testing.md) | Visual regression (library canonical): native vs hosted, baselines, thresholds |
| [references/api-testing-playwright.md](references/api-testing-playwright.md) | `request` fixture for UI+API hybrid tests (contract/schema work lives in qa-api-testing-contracts) |
| [references/playwright-preflight-sandbox.md](references/playwright-preflight-sandbox.md) | Sandbox/port preflight and escalation decisions |
| [data/sources.json](data/sources.json) | Documentation links |

## Templates

| Template | Purpose |
|----------|---------|
| [assets/template-playwright-e2e-review-checklist.md](assets/template-playwright-e2e-review-checklist.md) | E2E review checklist |
| [assets/template-playwright-fail-on-flaky-reporter.js](assets/template-playwright-fail-on-flaky-reporter.js) | Legacy: fail CI on rerun-pass flakes for Playwright < 1.52 only; use `failOnFlakyTests` otherwise |
| [assets/test-fail-on-flaky-reporter.test.js](assets/test-fail-on-flaky-reporter.test.js) | `node --test` checks for the legacy flaky reporter |
| [assets/template-playwright-preflight-checklist.md](assets/template-playwright-preflight-checklist.md) | Preflight checklist for port/sandbox/timeouts |

## Navigation

Use Quick Reference to select the workflow, debugging path, or resource.

## Related Skills

| Skill | Purpose |
|-------|---------|
| [qa-testing-strategy](../qa-testing-strategy/SKILL.md) | Overall test strategy |
| [software-frontend](../software-frontend/SKILL.md) | Frontend development |
| [ops-devops-platform](../ops-devops-platform/SKILL.md) | CI/CD integration |

## Verification Gate

Before delivering, check:

- [ ] If a Playwright project exists, provide the exact test command to run and execute it when the environment is available; otherwise mark execution as unverified.
- [ ] Generated selectors follow the stated locator priority unless the page makes that impossible.
- [ ] The output avoids sleep-based waits and names the readiness assertion or trace/debug artifact to inspect.
- [ ] Every referenced test file, config file, and command path exists in the repo or is explicitly marked as proposed.

## Learnings Loop

When prior decisions or pitfalls are relevant, consult `learnings.consolidated.md` if present; use `learnings.md` only for needed history or as the available fallback. Otherwise skip both.

After applying it, if you encountered a pattern worth remembering, a mistake worth preventing, or a domain fact that surprised you, append one dated bullet to `learnings.md` via `agents-skills-feedback-loop/scripts/append_learning.py`. Do not modify `SKILL.md` itself.
