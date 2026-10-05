# Test Automation Patterns

Page Object Model, data factories, fixtures, AAA, parameterised tests and tags are standard practice and are not repeated here. This file keeps the rules where teams most often get the pattern wrong: retries, snapshots, flake classification and mocking boundaries. Tool-specific mechanics live in the specialist skills ([qa-testing-playwright](../../qa-testing-playwright/SKILL.md), [qa-api-testing-contracts](../../qa-api-testing-contracts/SKILL.md)).

## Retry Rules

- Prefer web-first assertions and explicit conditions (`await expect(locator).toBeVisible()`) over sleeps or hand-rolled retry loops around assertions.
- CI-level retries are an evidence-collection tool, not a fix. Keep traces/screenshots from the failed attempt, and record every rerun-pass as flake debt against the test.
- Never retry a test that gates security, auth or payment correctness to green; a rerun-pass there is a failure until triaged.
- Retries in application code (idempotent client retries with backoff) are a product behaviour and must be tested as such, including the give-up path; see [qa-resilience](../../qa-resilience/SKILL.md).

## Snapshot Rules

- Use snapshots only for output that changes rarely and is reviewed as a diff (serialised config, generated schemas, stable rendering).
- Mask or matcher-replace dynamic fields (`expect.any(String)` for IDs and timestamps) so snapshot churn stays meaningful.
- A snapshot update is a reviewed change. Blanket `-u` in CI, or approving large snapshot diffs without reading them, turns the test into a recorder.
- Prefer explicit assertions when the property matters (a value, an invariant); a snapshot proves only "unchanged".

## Flaky-Test Taxonomy and Detection

| Class | Typical cause | How to detect | Fix direction |
|---|---|---|---|
| Order-dependent | Shared mutable state, test pollution | Randomise test order (`pytest-randomly`, Jest `--randomize`, JUnit random method order) as a periodic or PR check | Fresh state per test; remove global singletons |
| Async / timing | Races, fixed sleeps, animation, polling | History shows failures clustered on slow runners; trace diff (see [observability-driven-testing.md](observability-driven-testing.md)) | Wait on conditions, not time; control clocks |
| Shared resource | Ports, DB rows, files, rate-limited sandboxes | Failures correlate with parallelism level | Isolate per worker; unique data per test |
| Environment | Runner image, network, third-party sandbox | Same test fails across unrelated suites at the same time | Fix or pin the environment; do not quarantine the test |

Detection method: prefer history-based detection (same commit, different outcomes across runs over time) over rerun-based detection (retry immediately and see if it passes). Rerun-based detection misses order- and resource-dependent flakes that only appear under specific scheduling, and it hides environment incidents as "flaky tests".

## Mocking Boundary

- Mock at external boundaries you do not own (third-party APIs, payment gateways, email); use real implementations for internal code.
- For databases and queues, use the real engine in integration tests (containers); in-memory fakes only for unit-level logic.
- If a test needs more than a couple of mocks to reach the code under test, the design or the layer choice is wrong; move the test to the layer that can prove the behaviour.

## Related Resources

- [../SKILL.md](../SKILL.md) — layer decision rules
- [operational-playbook.md](operational-playbook.md) — CI gates, quarantine and merge-queue policy
- [shift-left-testing.md](shift-left-testing.md) — early testing practices
