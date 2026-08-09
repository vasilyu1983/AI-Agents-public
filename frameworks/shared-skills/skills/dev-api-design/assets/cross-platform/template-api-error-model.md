# API Error Model Template (RFC 9457 Problem Details)

Use this template to standardize errors across services and make client behavior predictable.

---

## Core

### 1) Default Response Format

- Content-Type: `application/problem+json`
- Standard fields: `type`, `title`, `status`, `detail`, `instance`
- Extensions (recommended): `code`, `retryable`, `errors[]`, `trace_id`

Example:

```json
{
  "type": "https://api.example.com/problems/validation-error",
  "title": "Validation Error",
  "status": 422,
  "detail": "One or more fields failed validation",
  "instance": "/v1/users",
  "code": "validation_error",
  "retryable": false,
  "trace_id": "01JFDY9W9Q8Y2W7A9JY3VJQ3Z0",
  "errors": [
    { "field": "email", "code": "invalid_format", "message": "Email must be valid" }
  ]
}
```

### 2) Error Code Registry (Required)

Rules:

- `code` is stable (clients can switch on it).
- `type` is stable and documented (URI per error family).
- `title` is stable per error type (human-readable).
- `detail` is instance-specific and safe to expose.

Registry template:

| code | http_status | retryable | type | title | Client action |
|------|-------------|-----------|------|-------|---------------|
| `validation_error` | 422 | No | `/problems/validation-error` | Validation Error | Fix request and retry |
| `authentication_required` | 401 | No | `/problems/unauthorized` | Unauthorized | Re-authenticate |
| `permission_denied` | 403 | No | `/problems/forbidden` | Forbidden | Stop, request access |
| `resource_not_found` | 404 | No | `/problems/not-found` | Not Found | Stop or create |
| `conflict` | 409 | No | `/problems/conflict` | Conflict | Resolve state, retry |
| `rate_limited` | 429 | Yes | `/problems/rate-limited` | Too Many Requests | Backoff, respect Retry-After |
| `upstream_unavailable` | 503 | Yes | `/problems/unavailable` | Service Unavailable | Retry with backoff/jitter |

### 3) HTTP Header Requirements

- 401: `WWW-Authenticate` (Bearer realm and error details where applicable)
- 429: `Retry-After` when you can provide a meaningful retry time
- All responses: request correlation header (`traceparent` or `x-request-id`) should be returned

### 4) Validation Error Shape

Guidelines:

- Use `errors[]` only for field-level issues.
- `errors[].code` is stable; `errors[].message` is safe and user-facing.
- Prefer `422` for semantic validation errors; `400` for malformed syntax.

### 5) Security Requirements

- Do not include stack traces, SQL text, secrets, internal hostnames, or dependency credentials.
- Avoid user enumeration: keep auth errors generic where needed.
- Ensure tenant boundaries: do not leak cross-tenant existence via 404/403 mismatches.

### 6) Observability Requirements

- Always include a correlation identifier (`trace_id` and/or `traceparent`).
- Log the full error server-side with internal diagnostics keyed by `trace_id`.
- Emit metrics by `code` and route group to support alerting and SLOs.

---

## Do / Avoid

### Do

- Do document the `code` registry and treat it as API surface
- Do keep `detail` safe and actionable for clients
- Do mark retryability explicitly and keep it consistent with status codes

### Avoid

- Avoid inventing a different error shape per endpoint
- Avoid making clients parse human strings to decide behavior
- Avoid leaking sensitive internals in error responses

---

## Optional: AI/Automation

- Generate the first draft of `code` registry entries from existing logs (human-reviewed)
- Summarize incident spikes by `code` and propose top contributors (human-validated)
- Create contract tests from the registry table (human-owned acceptance)

### Bounded Claims

- Automation cannot decide which errors are safe to expose.
- Retryability must be validated against real dependency behavior and SLAs.
