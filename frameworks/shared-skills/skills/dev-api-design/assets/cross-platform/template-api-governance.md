# API Governance & Design Review Checklist

Production-grade API governance covering deprecation, compatibility, multi-tenancy, and SDK guidelines.

---

## API Design Review Checklist

### Before Implementation

- [ ] API scope and purpose documented
- [ ] Resource naming follows conventions (nouns, plural)
- [ ] HTTP methods semantically correct (GET=read, POST=create, etc.)
- [ ] Request/response schemas defined in OpenAPI
- [ ] Authentication method specified
- [ ] Rate limits defined
- [ ] Error codes and messages documented
- [ ] Breaking change assessment completed

### Resource Design

| Check | Pass | Notes |
|-------|------|-------|
| Resource names are nouns (not verbs) | [ ] | |
| Collection endpoints use plural | [ ] | |
| Nested resources max 2 levels deep | [ ] | |
| IDs are opaque (no business meaning) | [ ] | |
| URL paths are lowercase with hyphens | [ ] | |
| Query params documented with types | [ ] | |

### Request/Response Design

| Check | Pass | Notes |
|-------|------|-------|
| Request body schema defined | [ ] | |
| Response envelope consistent | [ ] | |
| Pagination implemented for lists | [ ] | |
| Timestamps use ISO 8601 | [ ] | |
| Null handling explicit | [ ] | |
| Field casing consistent (camelCase) | [ ] | |

---

## Deprecation Policy

### Deprecation Timeline

| Phase | Duration | Actions |
|-------|----------|---------|
| **Announce** | T-90 days | Add `Deprecation` header, update docs |
| **Warn** | T-60 days | Log warnings for deprecated endpoint usage |
| **Migrate** | T-30 days | Direct outreach to heavy users |
| **Sunset** | T-0 | Return 410 Gone (not 404) |

### Deprecation Headers

```http
HTTP/1.1 200 OK
Deprecation: Sun, 01 Dec 2025 00:00:00 GMT
Sunset: Sun, 01 Mar 2026 00:00:00 GMT
Link: <https://api.example.com/v2/users>; rel="successor-version"
```

### Deprecation Announcement Template

```markdown
## API Deprecation Notice: [Endpoint/Version]

**Deprecated**: [Date]
**Sunset Date**: [Date + 90 days minimum]
**Replacement**: [New endpoint or version]

### What's Changing
[Description of deprecated functionality]

### Migration Guide
1. [Step 1]
2. [Step 2]
3. [Step 3]

### Timeline
- [ ] 90 days: Deprecation announced
- [ ] 60 days: Warning logs enabled
- [ ] 30 days: Direct migration outreach
- [ ] 0 days: Endpoint returns 410 Gone

### Support
Contact api-support@example.com for migration assistance.
```

---

## Backward Compatibility Rules

### Breaking Changes (Require Major Version)

- Removing an endpoint
- Removing a field from response
- Changing field type (string → number)
- Changing field meaning
- Adding required request field
- Changing authentication method
- Changing error code meanings

### Non-Breaking Changes (Safe)

- Adding new endpoint
- Adding optional request field
- Adding response field
- Adding new error codes
- Adding enum values (if client handles unknown gracefully)
- Adding new HTTP methods to existing resource

### Compatibility Checklist

- [ ] No fields removed from response
- [ ] No required fields added to request
- [ ] No field types changed
- [ ] Existing error codes unchanged
- [ ] Authentication backward compatible
- [ ] Rate limits not made stricter

### Schema Evolution Strategy

```yaml
# Good: Additive change (non-breaking)
User:
  properties:
    id: string
    name: string
    email: string
    phone: string  # NEW - optional

# Bad: Breaking change
User:
  properties:
    id: string
    fullName: string  # RENAMED from 'name' - BREAKING
    emailAddress: string  # RENAMED from 'email' - BREAKING
```

---

## Multi-Tenant API Patterns

### Tenant Isolation Checklist

- [ ] Tenant ID in all database queries
- [ ] Row-level security enabled
- [ ] Cross-tenant data access impossible
- [ ] Tenant context propagated in headers
- [ ] Audit logs include tenant ID
- [ ] Rate limits per tenant

### Tenant Identification Methods

| Method | Use When | Example |
|--------|----------|---------|
| **Subdomain** | B2B SaaS | `acme.api.example.com` |
| **Path prefix** | Multi-tenant APIs | `/tenants/{tenant_id}/users` |
| **Header** | Internal services | `X-Tenant-ID: acme` |
| **JWT claim** | Auth-integrated | `tenant_id` in token payload |

### Multi-Tenant Request Template

```http
GET /api/v1/users HTTP/1.1
Host: api.example.com
Authorization: Bearer <jwt_with_tenant_claim>
X-Tenant-ID: acme  # Redundant with JWT, but explicit

# Response scoped to tenant
{
  "data": [
    {"id": "user_123", "tenant_id": "acme", "name": "Alice"}
  ],
  "meta": {
    "tenant_id": "acme",
    "total": 1
  }
}
```

### Tenant Data Isolation Patterns

| Pattern | Security | Complexity | Use When |
|---------|----------|------------|----------|
| **Shared tables + tenant_id** | Medium | Low | Most SaaS apps |
| **Schema per tenant** | High | Medium | Compliance requirements |
| **Database per tenant** | Highest | High | Enterprise, regulated |

---

## Error Model Template

### Standard Error Response (RFC 9457, obsoletes RFC 7807)

```json
{
  "type": "https://api.example.com/errors/validation-error",
  "title": "Validation Error",
  "status": 422,
  "detail": "One or more fields failed validation",
  "instance": "/api/v1/users/123",
  "code": "validation_error",
  "retryable": false,
  "trace_id": "abc123def456",
  "errors": [
    {
      "field": "email",
      "code": "invalid_format",
      "message": "Email must be a valid email address"
    },
    {
      "field": "age",
      "code": "out_of_range",
      "message": "Age must be between 0 and 150"
    }
  ]
}
```

### Error Code Registry

| Code | HTTP Status | Retryable | Description |
|------|-------------|-----------|-------------|
| `invalid_request` | 400 | No | Malformed request syntax |
| `validation_error` | 422 | No | Field validation failed |
| `authentication_required` | 401 | No | Missing or invalid auth |
| `permission_denied` | 403 | No | Insufficient permissions |
| `resource_not_found` | 404 | No | Resource does not exist |
| `conflict` | 409 | No | Resource state conflict |
| `rate_limited` | 429 | Yes | Too many requests |
| `internal_error` | 500 | Yes | Server error (with backoff) |
| `service_unavailable` | 503 | Yes | Temporary overload |

### Retryability Header

```http
HTTP/1.1 429 Too Many Requests
Retry-After: 60
X-RateLimit-Reset: 1701388800
```

---

## SDK Guidelines

### SDK Generation Checklist

- [ ] OpenAPI spec is complete and accurate
- [ ] All endpoints have examples
- [ ] Error responses documented
- [ ] Authentication flows documented
- [ ] Pagination handling documented
- [ ] Rate limit handling documented

### SDK Feature Requirements

| Feature | Priority | Notes |
|---------|----------|-------|
| Type safety | Required | Generated types from OpenAPI |
| Authentication | Required | Handle token refresh |
| Retry logic | Required | Exponential backoff |
| Rate limit handling | Required | Respect Retry-After |
| Pagination helpers | Recommended | Iterator patterns |
| Request/response logging | Recommended | Debug mode |
| Timeout configuration | Recommended | Client-side timeouts |

### SDK Error Handling Pattern

```typescript
// Good SDK error handling
try {
  const user = await client.users.get("user_123");
} catch (error) {
  if (error instanceof ApiError) {
    switch (error.code) {
      case "resource_not_found":
        // Handle 404
        break;
      case "rate_limited":
        // Retry with backoff (SDK should handle)
        break;
      case "authentication_required":
        // Refresh token and retry
        break;
      default:
        // Unknown error
        throw error;
    }
  }
}
```

---

## Do / Avoid

### GOOD: Do

- Version all APIs from day one
- Document deprecation policy before first deprecation
- Use semantic versioning for API versions
- Provide migration guides for breaking changes
- Include trace IDs in all error responses
- Test SDK generated code before release
- Monitor API usage before deprecating endpoints

### BAD: Avoid

- Removing fields without deprecation period
- Changing field types in existing versions
- Making auth more restrictive without notice
- Deprecating without providing alternatives
- Mixing tenant data without explicit isolation
- Hardcoding error messages (use codes)
- Returning 500 for client errors

---

## Anti-Patterns

| Anti-Pattern | Problem | Fix |
|--------------|---------|-----|
| **Instant deprecation** | Breaks existing clients | 90-day minimum sunset |
| **Silent breaking changes** | Client failures in production | Versioning + changelog |
| **Tenant ID in URL only** | Forgery risk | Validate against auth token |
| **Generic error messages** | Poor developer experience | Specific error codes |
| **No rate limit headers** | Clients can't back off properly | Include X-RateLimit-* |
| **Version in request body** | Hard to route, debug | Version in URL or header |

---

## Optional: AI/Automation

> **Note**: These enhance governance but require human oversight.

### Automated Governance

- OpenAPI linting in CI/CD (Spectral, Redocly)
- Breaking change detection (oasdiff)
- SDK generation on spec changes
- Contract testing automation (Pact, Dredd)

### AI-Assisted Review

- API design suggestions (must be validated)
- Documentation generation (review for accuracy)
- Error message improvement suggestions

### Bounded Claims

- AI-generated OpenAPI specs require human review
- Automated deprecation detection needs manual confirmation
- SDK generation requires type verification

---

## Related Templates

- [api-patterns-universal.md](api-patterns-universal.md) — Cross-framework patterns
- [../error-handling-patterns.md](../../references/error-handling-patterns.md) — Error model deep dive
- [../versioning-strategies.md](../../references/versioning-strategies.md) — Version comparison

---

**Last Updated**: December 2025
