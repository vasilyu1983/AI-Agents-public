# Shift-Left Testing Strategy

Shift-left means moving the cheapest effective check to the earliest point where it can run: acceptance criteria and contracts before code, unit and static checks before merge, and preview environments before main. The generic practices (TDD, BDD feature files, OpenAPI-first, static analysis, staged pipelines) are well known; this file keeps only the decision rules.

## Decision Rules

| Stage | Check that belongs here | Blocks |
|---|---|---|
| Requirements | Acceptance criteria written as observable outcomes; each critical risk named with an oracle (see [../assets/template-test-case-design.md](../assets/template-test-case-design.md)) | Story ready |
| Design | API contract (OpenAPI/AsyncAPI/Protobuf) and its breaking-change check; test strategy line in the ADR for new boundaries | Implementation start |
| Development | Unit/property tests for domain rules; lint, types, secret scan in pre-commit or PR | Merge |
| PR | Contract checks, component/integration smoke, changed-file mutation score for AI-authored tests | Merge |
| Preview environment | Thin E2E smoke against the PR's own deployment | Merge (for UI-critical changes) |
| Main / deploy | Full suite, deploy-gate replay, performance budgets | Deploy |

Rules:

- A check moves left only if it stays fast and deterministic at the earlier stage; a flaky early check is worse than a reliable late one.
- Write the regression test for a production defect at the lowest layer that reproduces it, and confirm it fails on the pre-fix build.
- Shift-left does not replace shift-right: production signals decide which new tests to add (see [production-testing-and-shift-right.md](production-testing-and-shift-right.md)).
- Treat shift-left ROI as an investment decision: start where risk is highest (auth, payments, data loss, distributed workflows), measure defect escape rate, lead time and CI duration, and prune suites that cost more than they catch.

## Metrics

- **Early detection rate** = defects found before main / all defects found. Track the trend; a fixed target (often quoted as "80% before QA") is a practitioner heuristic, not a benchmark.
- **Defect escape rate** and **lead time for changes**: see [quality-metrics-dashboard.md](quality-metrics-dashboard.md) and DORA metrics.

## Related

- [operational-playbook.md](operational-playbook.md) — CI gates and merge-queue policy
- [test-environment-management.md](test-environment-management.md) — preview and ephemeral environments
- [../assets/bdd/template-cucumber-gherkin.md](../assets/bdd/template-cucumber-gherkin.md) — when Gherkin earns its cost
