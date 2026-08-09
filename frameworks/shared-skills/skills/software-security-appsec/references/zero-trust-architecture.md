# Zero Trust Architecture

Application-facing zero-trust guidance for modern systems as of March 2026.

Use this reference when the user needs application, service, or workload-level trust-boundary design. For infrastructure implementation details, pair with [../../ops-devops-platform/SKILL.md](../../ops-devops-platform/SKILL.md).

---
## Table of Contents

- [Stable Baseline](#stable-baseline)
- [Zero Trust in AppSec Terms](#zero-trust-in-appsec-terms)
- [Key Design Questions](#key-design-questions)
- [Core Building Blocks](#core-building-blocks)
- [Identity](#identity)
- [Policy](#policy)
- [Transport](#transport)
- [Observability](#observability)
- [Example: Policy-Based Authorization](#example-policy-based-authorization)
- [Service-to-Service Patterns](#service-to-service-patterns)
- [Common Mistakes](#common-mistakes)
- [Testing Questions](#testing-questions)
- [Sources to Verify Live](#sources-to-verify-live)


## Stable Baseline

Anchor recommendations on:

- NIST SP 800-207
- CISA Zero Trust Maturity Model 2.0
- workload identity patterns such as SPIFFE / SPIRE
- policy-based authorization systems such as OPA

Avoid unsourced maturity claims, “X% fewer breaches” statistics, or speculative future-roadmap statements.

---

## Zero Trust in AppSec Terms

For application security, zero trust means:

- no implicit trust from network location alone
- per-request identity and authorization
- explicit trust boundaries between users, services, tools, and data stores
- short-lived credentials
- policy-driven access decisions
- auditability of privileged actions

It does **not** mean “put MFA everywhere and call it done.”

---

## Key Design Questions

- What is the principal for this request: user, device, workload, or automation?
- What resource is being accessed and under what tenant or policy boundary?
- What evidence is required before granting access?
- How is access revoked or expired?
- What logs prove the decision and the action taken?

---

## Core Building Blocks

### Identity

- User identity via OIDC / workforce SSO / passkeys
- Workload identity via mTLS, SPIFFE, cloud workload identity, or equivalent
- Device posture only where it actually changes authorization decisions

### Policy

- Centralize policy enough to review and test it
- Keep policy inputs explicit: subject, action, resource, tenant, environment
- Default to deny

### Transport

- Encrypt east-west and north-south traffic
- Prefer authenticated service-to-service channels
- Treat private networks as hostile enough to require identity and policy

### Observability

- Log the decision inputs and outcome
- Preserve enough context for incident response
- Distinguish authentication failure from authorization denial

---

## Example: Policy-Based Authorization

```rego
package httpapi.authz

default allow = false

allow if {
  input.subject.tenant_id == input.resource.tenant_id
  input.action == "read"
}

allow if {
  input.subject.role == "admin"
  input.action == "write"
  input.resource.classification != "break-glass-only"
}
```

This is valuable only if the input model is trustworthy and consistently enforced.

---

## Service-to-Service Patterns

Prefer:

- mTLS with short-lived certs
- federated OIDC for CI/CD and cloud workload auth
- SPIFFE / SPIRE for workload identity in service environments
- narrowly scoped service accounts

Avoid:

- shared long-lived secrets across many services
- “internal network” as the primary trust mechanism
- authorization based purely on source IP or subnet

---

## Common Mistakes

- Mixing identity, device posture, and authorization into one opaque check
- Building exceptions that bypass normal policy evaluation
- Trusting headers inserted by upstream systems without boundary validation
- Relying on static service tokens that never expire
- Logging too little to explain who did what, or too much sensitive data

---

## Testing Questions

- Can an internal service call another service without a legitimate identity?
- Can one tenant access another tenant's data through internal APIs?
- Do degraded auth services fail closed or fail open?
- Are break-glass paths logged, bounded, and reviewed?
- Can you revoke a compromised service identity quickly?

---

## Sources to Verify Live

- NIST SP 800-207
- CISA Zero Trust Maturity Model
- current workload identity and mesh documentation
- cloud-provider identity federation behavior
