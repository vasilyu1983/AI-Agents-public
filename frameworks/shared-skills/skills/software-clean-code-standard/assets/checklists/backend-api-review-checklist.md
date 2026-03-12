# Backend API Review Checklist

**PR**: [Link]
**Reviewer**: [Name]
**Date**: YYYY-MM-DD

---

## Standards (Core)

- Clean code standard (single source of truth): [../../references/clean-code-standard.md](../../references/clean-code-standard.md)
- Review comments: if feedback is primarily about clean code, cite `CC-*` IDs; do not restate the standard.

## Core Review (All PRs)

### Correctness

- [ ] Request/response schemas match documentation
- [ ] Business logic handles edge cases (null, empty, max values)
- [ ] Error responses use consistent format (prefer RFC 9457 Problem Details) https://www.rfc-editor.org/rfc/rfc9457
- [ ] Database transactions have proper boundaries

### API Design

- [ ] RESTful conventions followed (verbs, resources, status codes)
- [ ] Idempotency key supported for mutating operations
- [ ] Pagination implemented for list endpoints
- [ ] Versioning strategy consistent with existing APIs

### Security

- Baseline `CC-*` to apply (cite IDs if violated): `CC-SEC-01`, `CC-SEC-02`, `CC-SEC-03`, `CC-SEC-05`, `CC-SEC-08`, `CC-ERR-02`, `CC-OBS-02`
- [ ] Rate limiting configured
- [ ] API threats considered (OWASP API Security Top 10) https://owasp.org/API-Security/

### Performance

- Baseline `CC-*` to apply (cite IDs if violated): `CC-PERF-01`, `CC-PERF-02`, `CC-PERF-03`
- [ ] Database queries are efficient (no N+1)
- [ ] Indexes exist for filtered/sorted fields
- [ ] Response payload size is reasonable
- [ ] Caching considered for read-heavy endpoints

### Testing

- Baseline `CC-*` to apply (cite IDs if violated): `CC-TST-01`, `CC-TST-02`, `CC-TST-03`, `CC-TST-04`
- [ ] Unit tests cover business logic
- [ ] Integration tests verify API contracts
- [ ] Error cases tested (400, 401, 403, 404, 500)
- [ ] Performance/load tests for critical paths

### Observability

- Baseline `CC-*` to apply (cite IDs if violated): `CC-OBS-01`, `CC-OBS-02`, `CC-OBS-03`
- [ ] Request logging with correlation ID
- [ ] Metrics for latency, throughput, errors
- [ ] Health check endpoints (liveness, readiness)
- [ ] Tracing/metrics aligned with OpenTelemetry where applicable https://opentelemetry.io/docs/

---

## Decision

- [ ] **APPROVE**: All checks pass
- [ ] **REQUEST CHANGES**: Issues listed below
- [ ] **BLOCK**: Critical security/correctness issue

### Issues Found

| Severity | Issue | Line(s) |
|----------|-------|---------|
| P0/P1/P2/P3 | Description | #L1-L5 |

---

## Optional: AI/Automation Section

> Include only when using AI features or adding automation gates.

- [ ] Automation (linters/SAST/SCA) results reviewed and mapped to `CC-*` IDs where possible
- [ ] If any AI-generated code is included, validate APIs exist and match project conventions
- [ ] LLM integrations have explicit timeouts, cancellation, and safe fallbacks
