# QA Test Strategy One-Pager (Risk-Based)

Use this template to define a minimal, high-signal quality plan that balances risk coverage, CI economics, and debuggability.

## Core

### Context

- Product/area: ________________________________
- What is changing (scope): _____________________
- Release cadence: ______________________________
- Environments: local / CI / staging / prod
- Key dependencies: _____________________________

### Quality Goals (Measurable)

- Reliability: SLIs/SLOs (latency/error/availability) and error budget policy
- Performance: budgets (p95/p99), frontend budgets (if applicable)
- Security: required checks (SAST/DAST/dependency scanning)
- Accessibility: target level and automation scope

### Risk Model (Journeys x Failure Modes)

List top user journeys and likely failure modes.

| Journey | Failure modes | Impact | Likelihood | Primary tests | Owner |
|--------|---------------|--------|------------|---------------|-------|
| Login | auth outage, session bugs | High | Med | E2E smoke + contract | ___ |
| Checkout | payment timeout, idempotency | High | Med | integration + resilience | ___ |

### Test Portfolio (Layered)

Define what runs where, and why.

- Unit: business logic, validators, pure functions
- Component: UI logic and accessibility checks
- Contract: OpenAPI/AsyncAPI/JSON schema validations
- Integration: API + DB + key dependencies (mock third parties)
- E2E: thin, critical user journeys only
- Exploratory: discovery and usability; convert high-ROI findings to automation
- Performance/resilience: scheduled or canary-gated, not every PR

### Shift-Left (Pre-Merge Gates)

- Required: lint, typecheck, unit tests, contract validation
- Conditional: integration smoke for affected areas
- Avoid: full E2E as a default PR gate (unless E2E-only product)

### CI/CD Stages (Economics)

- PR gate: ________________________________
- Post-merge: _____________________________
- Nightly: ________________________________
- Release: ________________________________
- Budgets (example targets):
  - PR gate p50 <= 10 min, p95 <= 20 min
  - Mainline health >= 99% green builds/day

### Flake Management

- Flake definition: fails without product change and passes on rerun.
- SLO examples (example targets):
  - Suite flake rate <= 1% weekly
  - Time-to-deflake p50 <= 2 business days, p95 <= 7 business days
- Quarantine rules: owner + ticket + expiry; never “ignore forever”.
- Runbook: `runbooks/template-flaky-test-triage-deflake-runbook.md`

### Observability for QA (Debugging Ergonomics)

- Required correlation IDs: request ID, trace ID
- Failure artifacts: logs, traces, screenshots/videos (UI), crash reports
- Where artifacts live: __________________________

### Owners and Cadence

- Suite owners: _________________________________
- Review cadence: _______________________________
- Deprecation policy for low-value tests: ________

## Optional: AI / Automation

Do:
- Use AI to draft the initial risk register and candidate test ideas; validate against domain knowledge and telemetry.
- Use AI to summarize test failures (log/trace clustering) while retaining evidence links.

Avoid:
- Accepting generated assertions/oracles without validation.
- Using AI to “heal” tests by weakening assertions.
