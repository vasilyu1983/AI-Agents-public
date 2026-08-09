# Security Baseline

## Input and boundary validation
- Validate and normalize all external inputs at entry boundaries.
- Reject invalid payloads early with explicit error responses.
- Enforce allow-lists for enum-like user inputs.
- Guard against over-posting by mapping explicit request models.

## Authentication and authorization boundaries
- Authenticate at transport edge.
- Authorize per use case, not only per endpoint path.
- Re-check authorization in background processing where user context is replayed.
- Deny by default when policy resolution is ambiguous.

## Secret and configuration hygiene
- Store secrets in managed secret stores/environment, never in source control.
- Rotate secrets and support zero-downtime reload where possible.
- Keep security-sensitive options separate from functional configuration.

## Secure defaults
- Use TLS for all networked communication.
- Disable debug/developer endpoints and verbose errors in production.
- Minimize privilege for service identities and database users.
- Set conservative defaults for CORS, headers, and cookie/token handling.

## Dependency and data protection
- Keep dependencies patched and monitor advisories.
- Hash passwords with modern adaptive algorithms.
- Encrypt sensitive data at rest and in transit.
- Redact sensitive fields in logs, traces, and exceptions.

## Security review checklist
- Can untrusted input reach dynamic query/path construction unsafely?
- Are authz checks close to business action boundaries?
- Are secrets and tokens fully excluded from telemetry?
