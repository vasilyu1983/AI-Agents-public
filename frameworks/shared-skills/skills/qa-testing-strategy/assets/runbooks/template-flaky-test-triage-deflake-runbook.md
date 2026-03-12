# Flaky Test Triage & Deflake Runbook

Use this runbook to reduce CI noise, prevent silent regressions, and restore confidence.

## Core

### Definitions

- Flaky test: fails without product change and passes on rerun.
- “Rerun-pass” is a defect signal, not a success.

### Flake SLOs (Example Targets)

- Suite flake rate <= 1% weekly.
- Time-to-deflake: p50 <= 2 business days, p95 <= 7 business days.
- Mainline health: >= 99% green builds/day.

### Intake Checklist (First 5 Minutes)

- Identify the failing test(s): name/path, suite, owner.
- Collect context:
  - Build URL, commit SHA, branch, runner type (self-hosted vs hosted)
  - Timestamp, region, parallel shard/worker ID
  - Retry count and whether it passed on retry
  - Correlation IDs (request/trace IDs) and artifacts (logs/screenshots/traces)

### Triage Flow (Reproduce → Classify → Fix → Prevent)

Reproduce:
- Run the single test N times (example: 20) on the same runner profile.
- If CI-only: reproduce in a container/runner that matches CI resources.

Classify (pick the dominant class):

| Class | Signals | Typical fixes |
|------|---------|--------------|
| Timing/race | “Sometimes element not ready”, async hazards | event-based waits, remove sleeps, await network/state |
| Data/state | ordering dependency, shared accounts, leaked DB rows | isolate data, reset state, unique IDs, cleanup |
| Environment | low CPU/memory, timezone/locale, throttling | pin locale/tz, increase resources, remove env assumptions |
| Dependency | third-party API, unstable backend | mock boundary, contract tests, test doubles |
| Test design | brittle selectors/assertions | assert user intent, stable selectors, stronger oracles |
| Product bug | genuine race in product | fix race; add regression at lowest layer |

Fix:
- Prefer product fixes for real races over test-only band-aids.
- Add/upgrade observability for the failing path (logs/traces) to catch it next time.

Prevent:
- Add a pre-merge check that would have caught the issue earlier (unit/integration/contract).

### Quarantine Policy (If You Must)

Quarantine is a temporary safety valve, not a solution.

REQUIRED fields:
- Owner: ______________________
- Ticket: _____________________
- Reason: _____________________
- Expiry date: ________________
- Impact: blocks PRs? yes/no

Rules:
- No quarantines without expiry and an assigned owner.
- Quarantined tests must still run and report; they just don’t block merges.
- If a quarantined test starts failing consistently, escalate as a product defect.

### CI Economics (Contain Blast Radius)

- Split suites by layer and cost: fast PR gate vs slow scheduled suites.
- Shard long-running suites; keep PR feedback under a fixed budget.

### Anti-Patterns (Deflake Smells)

- Adding sleeps to “stabilize” without proving the race.
- Increasing timeouts globally instead of fixing the slow step.
- Weakening assertions so failures disappear.
- Marking rerun-pass as success without tracking flake rate.

## Optional: AI / Automation

Do:
- Use AI to cluster failures across builds and summarize common signatures, but require evidence links (logs/traces/stack traces).
- Use AI to propose candidate root causes; validate via targeted instrumentation and reproduction.

Avoid:
- Letting AI auto-edit tests to “heal” flakes by reducing assertions or switching to brittle selectors.
