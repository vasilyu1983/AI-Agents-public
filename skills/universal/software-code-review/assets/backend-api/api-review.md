# Backend/API Code Review Checklist

Use this template when reviewing backend services and REST/GraphQL APIs.

## Core

### Standards

- Clean code standard (cite `CC-*` IDs): [../../../software-clean-code-standard/references/clean-code-standard.md](../../../software-clean-code-standard/references/clean-code-standard.md)
- Shared backend API checklist (product-agnostic): [../../../software-clean-code-standard/assets/checklists/backend-api-review-checklist.md](../../../software-clean-code-standard/assets/checklists/backend-api-review-checklist.md)
- Shared secure code review checklist (baseline): [../../../software-clean-code-standard/assets/checklists/secure-code-review-checklist.md](../../../software-clean-code-standard/assets/checklists/secure-code-review-checklist.md)

### Intent & Scope

- [ ] PR description states what/why/scope; risk and rollback plan are present.
- [ ] Diff matches intent; unrelated refactors are split or explicitly justified.

### API Contract

- [ ] Contract is explicit (OpenAPI/GraphQL schema) and versioning is consistent.
- [ ] Errors use a consistent model (e.g., RFC 9457 Problem Details) https://www.rfc-editor.org/rfc/rfc9457
- [ ] Idempotency and pagination are defined where needed.

### Security & Privacy

- [ ] Trust boundaries are clear; authorization is enforced for every sensitive operation (cite `CC-SEC-02`).
- [ ] Untrusted inputs are validated and not interpolated into interpreters (cite `CC-SEC-01`, `CC-SEC-08`).
- [ ] Secrets/PII are not logged or exposed via errors (cite `CC-SEC-03`, `CC-OBS-02`, `CC-ERR-02`).
- [ ] Dependency posture is acceptable for the change risk (cite `CC-SEC-05`).

### Reliability & Failure Modes

- [ ] Failure behavior is explicit and actionable (cite `CC-ERR-01`, `CC-ERR-02`).
- [ ] Retries are bounded and safe for idempotency/duplication (cite `CC-ERR-03`).
- [ ] I/O has timeouts and cancellation where supported (cite `CC-ERR-04`).
- [ ] External integrations have backoff/circuit-breaking where needed.

### Data & Consistency

- [ ] Transaction boundaries are correct; invariants preserved under concurrency.
- [ ] Queries are safe and efficient (no N+1; indexes for hot predicates).
- [ ] Migrations are safe, tested, and have rollback/forward-only strategy documented.

### Performance

- [ ] Work is bounded for untrusted/large inputs (cite `CC-PERF-01`).
- [ ] Obvious hazards avoided (N+1, O(n²) growth paths) (cite `CC-PERF-02`).
- [ ] Material perf changes are measured or justified in the target environment (cite `CC-PERF-03`).

### Observability

- [ ] Logs are structured and include correlation identifiers where relevant (cite `CC-OBS-01`).
- [ ] Critical paths are observable (logs/metrics/traces) (cite `CC-OBS-03`).
- [ ] No sensitive data in logs (cite `CC-OBS-02`).

### Tests

- [ ] New behavior is covered; bug fixes include regression tests (cite `CC-TST-01`).
- [ ] Tests are deterministic and isolate external dependencies (cite `CC-TST-02`).
- [ ] Risky changes have integration/contract tests where appropriate.

## Optional: AI / Automation

- [ ] CI status checks are green and enforceable (branch protection, required checks).
- [ ] SAST/SCA/secret scanning findings reviewed; map findings to `CC-*` IDs when possible.
- [ ] If AI-generated code is included, validate APIs exist, align with conventions, and add tests for generated changes.
- [ ] For LLM features: explicit timeouts, cancellation, rate limits, and safe fallbacks are implemented.
