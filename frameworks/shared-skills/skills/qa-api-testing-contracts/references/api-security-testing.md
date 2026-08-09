# API Security Testing

Use this reference for the minimum security baseline that should accompany contract testing.

## Priority Areas

Map coverage to the OWASP API Security Top 10, then add protocol-specific checks for webhooks and async consumers.

Highest priority in most systems:

- Broken object or tenant authorization
- Broken function authorization
- Authentication weaknesses
- Unrestricted resource consumption
- Unsafe consumption of upstream APIs
- Security misconfiguration

## Minimum Baseline

### AuthN / AuthZ

- Missing, expired, malformed, and tampered credentials
- Under-scoped tokens and role mismatches
- Cross-tenant access attempts
- Admin-only or write-only actions attempted by unprivileged users

### Input Validation

- Missing required fields
- Invalid types, enum values, and malformed identifiers
- Oversized payloads and boundary values
- Injection attempts appropriate to the stack

### Error Contracts

- Do not leak secrets, stack traces, SQL, or internal topology
- Keep the error contract stable if clients parse it
- For HTTP APIs using problem responses, prefer RFC 9457 `application/problem+json`

### Rate Limits and Abuse

- 429 behavior
- Retry headers or equivalent client guidance
- Idempotency and duplicate submission handling
- Pagination and cursor abuse

## Webhook Security

Always test:

- Signature verification failure
- Timestamp skew
- Replay of a previously valid event
- Duplicate delivery handling
- Out-of-order deliveries
- Callback URL validation and secret rotation behavior

Webhook security belongs in the contract conversation because receivers often depend on signing and retry semantics as much as payload shape.

## Async / Event Security

Always test:

- Schema validation on consume
- Poison message behavior and DLQ routing
- Unauthorized publish/subscribe paths
- Correlation ID spoofing or reuse
- Replay and duplicate-event handling

## GraphQL-Specific Security

- Introspection policy
- Operation cost / complexity limits
- Persisted or known-operation enforcement if used
- Field-level authorization on sensitive subgraphs or resolvers

## gRPC-Specific Security

- mTLS or transport auth configuration
- Per-method authorization
- Input limits and streaming abuse
- Reflection exposure policy

## CI Guidance

- Keep fast negative/security cases in the normal contract pipeline.
- Keep deeper DAST or fuzzing runs separate unless the user explicitly wants a combined gate.
- Publish failing requests/messages with secrets redacted.
