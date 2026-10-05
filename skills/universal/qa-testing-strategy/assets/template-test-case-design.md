# Test Case Design Template (Given/When/Then + Oracles)

Use this template for any test layer (unit/integration/contract/E2E) by filling only what applies.

## Core

### Metadata

- ID: __________________________
- Title: _______________________
- Owner: _______________________
- Layer: unit / component / contract / integration / E2E / exploratory
- Priority: P0 / P1 / P2 / P3
- Risk addressed: journey + failure mode(s)

### Goal (What This Test Proves)

- Hypothesis: _______________________________________________
- Why now: _________________________________________________

### Preconditions

- Environment: local / CI / staging
- Feature flags/config: _____________________________________
- Auth/user roles: __________________________________________

### Test Data

- Data setup method: fixtures / factories / seed / API setup
- Data identifiers (IDs/keys): _______________________________
- Cleanup/reset plan: _______________________________________

### Steps (Given / When / Then)

Given:
- ___________________________________________________________

When:
- ___________________________________________________________

Then:
- ___________________________________________________________

### Oracles (How You Know It’s Correct)

Functional oracles:
- Expected state/output: _____________________________________
- Contract/schema: __________________________________________

Quality oracles (if applicable):
- Security: authz/authn, sensitive data not exposed
- Accessibility: roles/labels, focus order, keyboard paths
- Performance: budget (p95/p99) and no significant regression

Negative oracles:
- What must NOT happen: _____________________________________

### Observability (Debugging Ergonomics)

- Correlation IDs captured: request ID / trace ID / build URL
- Failure artifacts expected:
  - Logs
  - Traces
  - Screenshots/video (UI)
  - Crash reports/core dumps (if relevant)

### Flake Control (Determinism)

- Time control: timezone/locale/frozen time? ________________
- Network control: mocked/stubbed boundaries? _______________
- Retries policy: ___________________________________________
- Timeout budget: ___________________________________________

### Automation Notes

- What to mock vs keep real: ________________________________
- Lowest layer alternative: can this be tested lower? ________
- CI execution: PR gate / nightly / release _________________

### Pass/Fail Criteria

- Pass criteria: ____________________________________________
- Fail criteria: ____________________________________________

## Optional: AI / Automation

Do:
- Use AI to propose edge cases and variations (boundaries, auth roles, locales).
- Use AI to draft Given/When/Then steps and candidate oracles, then validate manually.

Avoid:
- Copying AI-generated assertions without verifying the oracle and failure mode.
- Generating large combinatorial suites without a risk-based selection.
