# Secure Code Review Checklist

**PR**: [Link]
**Reviewer**: [Name]
**Date**: YYYY-MM-DD

---

## Standards (Core)

- Clean code standard (single source of truth): [../../references/clean-code-standard.md](../../references/clean-code-standard.md)
- Review comments: if feedback is primarily about clean code, cite `CC-*` IDs; do not restate the standard.

## Authentication (Core)

- Baseline `CC-*` to apply (cite IDs if violated): `CC-SEC-06`, `CC-SEC-07`
- [ ] Token lifetime and rotation aligned to OAuth security BCP (short-lived access tokens + rotation) https://www.rfc-editor.org/rfc/rfc9700
- [ ] Logout invalidates all sessions/tokens

## Authorization (Core)

- Baseline `CC-*` to apply (cite IDs if violated): `CC-SEC-02`
- [ ] RBAC/ABAC policies enforced consistently
- [ ] No direct object references without ownership check
- [ ] Admin actions require elevated confirmation

## Input Validation (Core)

- Baseline `CC-*` to apply (cite IDs if violated): `CC-SEC-01`, `CC-SEC-08`
- [ ] File uploads validated (type, size, content)
- [ ] Path traversal prevented (no user input in file paths)

## Output Encoding (Core, Conditional: Web)

- Baseline `CC-*` to apply (cite IDs if violated): `CC-SEC-08`
- [ ] CSP headers configured (no 'unsafe-inline')
- [ ] CORS restricted to known origins

## Cryptography (Core)

- Baseline `CC-*` to apply (cite IDs if violated): `CC-SEC-04`, `CC-SEC-03`
- [ ] TLS configured per modern guidance (prefer TLS 1.3; no legacy ciphers) [Inference]
- [ ] Encryption at rest uses organization-approved algorithms and libraries (avoid bespoke crypto) [Inference]

## Logging & Monitoring (Core)

- Baseline `CC-*` to apply (cite IDs if violated): `CC-OBS-01`, `CC-OBS-02`, `CC-OBS-03`
- [ ] Authentication events logged
- [ ] Authorization failures logged
- [ ] Correlation IDs for request tracing

## Dependency Security (Core)

- Baseline `CC-*` to apply (cite IDs if violated): `CC-SEC-05`
- [ ] Dependencies from trusted sources
- [ ] Supply chain controls in place (SBOM/provenance expectations) https://slsa.dev/spec/v1.0/

---

## Decision

- [ ] **APPROVE**: No security issues found
- [ ] **REQUEST CHANGES**: Security issues listed below
- [ ] **BLOCK**: Critical vulnerability detected

### Security Issues Found

| Severity | Issue | CWE | Line(s) |
|----------|-------|-----|---------|
| Critical/High/Medium/Low | Description | CWE-XXX | #L1-L5 |

---

## Optional: AI/Automation Section

> Include only for AI/LLM features.

- [ ] Prompt injection mitigated (input sanitization)
- [ ] LLM output sanitized before display
- [ ] PII not sent to external LLM APIs
- [ ] Rate limiting on AI endpoints
- [ ] Fallback behavior when AI service unavailable
