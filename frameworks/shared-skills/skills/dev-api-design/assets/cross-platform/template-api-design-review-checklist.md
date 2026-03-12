# API Design Review Checklist (Production)

Use this checklist for PRDs, RFCs, and PR reviews to keep APIs consistent, secure, and operable.

---

## Core

### 1) Scope and Consumers

- [ ] Audience: public / partner / internal
- [ ] Use case(s) and non-goals listed
- [ ] Backward compatibility expectations documented
- [ ] Data classification (PII/PHI/PCI) documented

### 2) Resource Model and Semantics

- [ ] Resource names are nouns; actions are minimized and justified
- [ ] HTTP method semantics match intent (GET safe, PUT/DELETE idempotent)
- [ ] Idempotency defined for create/mutation flows (idempotency key or natural key)
- [ ] Pagination is mandatory for list endpoints (cursor preferred for large/real-time lists)
- [ ] Filtering and sorting are explicit, indexed, and bounded (no unbounded scans)
- [ ] Partial responses and field selection strategy decided (if needed for cost control)

### 3) Versioning and Deprecation

- [ ] Versioning strategy is explicit (URL/header/content negotiation) and consistently applied
- [ ] Deprecation policy exists (notice period, sunset date, comms plan)
- [ ] Breaking-change rules documented (what counts as breaking)
- [ ] Compatibility tests (or contract checks) defined for stable endpoints

### 4) Error Model (Consistency + Retryability)

- [ ] RFC 9457 Problem Details is the default response format for errors
- [ ] Stable `code` registry exists (machine-readable, documented)
- [ ] `retryable` is defined per error code and consistent with HTTP semantics
- [ ] 401 uses `WWW-Authenticate` where relevant; 429 uses `Retry-After` where applicable
- [ ] Errors do not leak secrets, stack traces, internal hostnames, or SQL text

Template: [template-api-error-model.md](template-api-error-model.md)

### 5) AuthN/AuthZ and Multi-Tenancy

- [ ] AuthN mechanism is explicit (OAuth2/OIDC, JWT, mTLS, API keys)
- [ ] AuthZ model is explicit (RBAC/ABAC) with least privilege
- [ ] Tenant boundaries are enforced server-side (never trust tenant ID from client)
- [ ] Audit logging requirements are defined for sensitive operations

### 6) Rate Limits, Quotas, and Abuse Controls

- [ ] Rate limits are defined per actor (user/org/token) and per route group
- [ ] Limits are observable (rate limit headers, dashboards, alert thresholds)
- [ ] Abuse prevention: replay protection, bot mitigation where needed
- [ ] Traffic shaping plan exists for batch/backfill endpoints

### 7) Reliability and Operations

- [ ] Timeouts and retries are defined per dependency (client and server)
- [ ] Request IDs and trace propagation are implemented (logs + traces)
- [ ] Metrics defined: latency (p95/p99), error rate, saturation, queue depth
- [ ] Runbook exists for top failure modes (dependency outage, auth outage, overload)
- [ ] Safe deploy plan: canary/gradual rollout, rollback strategy, feature flags if needed

### 8) Data and Performance

- [ ] N+1 risk addressed (batch endpoints, joins, caching, DataLoader for GraphQL)
- [ ] Queries are bounded and indexed for hot paths
- [ ] Bulk endpoints have throttles and async patterns (202 + job status) if needed
- [ ] Caching strategy is explicit (ETag/If-None-Match, Cache-Control) where appropriate

---

## Do / Avoid

### Do

- Do define a stable error code taxonomy before the first external client ships
- Do treat rate limits as part of the contract (document and test them)
- Do design for operability: logs/metrics/traces and runbooks are required
- Do require pagination and bounded filters to control cost and reliability

### Avoid

- Avoid action endpoints for everything (`/doThing`); start with resources + verbs
- Avoid breaking changes without an explicit deprecation and migration path
- Avoid returning raw internal errors to clients (leaks + unstable contracts)
- Avoid unbounded list endpoints and expensive filters without quotas

---

## Optional: AI/Automation

> Use only as a productivity layer; humans own the contract.

- Automated OpenAPI linting (Spectral/Redocly) and diff checks (oasdiff)
- Drafting endpoint tables and examples from an approved design doc
- Generating initial SDK stubs and contract-test scaffolding (human-reviewed)

### Bounded Claims

- Generated specs and examples require human review for security and semantics.
- Automation cannot infer business-acceptable risk, quotas, or deprecation timelines.
