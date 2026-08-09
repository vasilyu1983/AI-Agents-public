# Authentication & Authorization Patterns

Application-layer guidance for authentication and authorization decisions as of March 2026.

Use this reference to choose between passkeys, sessions, tokens, delegated auth, and authorization models. Verify vendor-specific defaults and protocol revisions before final implementation.

---
## Table of Contents

- [Current Baseline](#current-baseline)
- [Decision Matrix](#decision-matrix)
- [Passkeys / WebAuthn](#passkeys-webauthn)
- [When to Prefer Them](#when-to-prefer-them)
- [Benefits](#benefits)
- [Operational Notes](#operational-notes)
- [Implementation Sketch](#implementation-sketch)
- [Recommended Libraries](#recommended-libraries)
- [Sessions vs Tokens](#sessions-vs-tokens)
- [Browser Apps: Prefer Sessions by Default](#browser-apps-prefer-sessions-by-default)
- [APIs: Use Short-Lived Access Tokens Deliberately](#apis-use-short-lived-access-tokens-deliberately)
- [Refresh Tokens](#refresh-tokens)
- [OAuth 2.1 / OIDC](#oauth-21-oidc)
- [Minimum Checks](#minimum-checks)
- [Avoid](#avoid)
- [Service-to-Service Authentication](#service-to-service-authentication)
- [Authorization Models](#authorization-models)
- [RBAC](#rbac)
- [ABAC](#abac)
- [ReBAC](#rebac)
- [General Rules](#general-rules)
- [Anti-Patterns](#anti-patterns)
- [Testing Checklist](#testing-checklist)
- [Sources to Verify Live](#sources-to-verify-live)


## Current Baseline

- Prefer passkeys / WebAuthn for new first-party user authentication when recovery and device support are viable.
- Prefer server-managed session cookies for browser apps unless you have a concrete reason to expose bearer tokens to the browser.
- Prefer OIDC / OAuth 2.1 style authorization code + PKCE for delegated login and API access.
- Prefer workload identity or mTLS over long-lived shared API keys for service-to-service traffic.
- Treat authorization as a separate design problem from authentication.

---

## Decision Matrix

| Problem | Default | Notes |
|---------|---------|-------|
| First-party browser login | Passkeys + session cookie | Best blend of phishing resistance and operational simplicity |
| Existing password app | Add passkey enrollment, keep strong password fallback | Migrate incrementally; do not break recovery |
| Third-party sign-in | OIDC / OAuth + PKCE | Validate issuer, audience, state, nonce, and redirect URI |
| Browser SPA needing backend APIs | BFF/session or tightly scoped token flow | Do not default to localStorage JWTs |
| Mobile/native app auth | OIDC + PKCE | Use platform secure storage and app-bound redirect URIs |
| Service-to-service auth | Workload identity / mTLS / short-lived credentials | Avoid static credentials when platform support exists |
| Coarse permissions | RBAC | Simple and auditable |
| Contextual access rules | ABAC | Use when attributes materially affect access decisions |
| Shared-resource collaboration | ReBAC | Needed for owner/editor/viewer style models |

---

## Passkeys / WebAuthn

### When to Prefer Them

- New applications without a legacy password constraint
- Sensitive consumer or workforce login flows
- Environments where phishing resistance matters more than maximum backward compatibility

### Benefits

- No shared secret for the server to leak
- Strong phishing resistance
- Lower credential-stuffing exposure
- Works with platform authenticators and hardware security keys

### Operational Notes

- Recovery must be explicit: secondary passkey, recovery code, verified help-desk process, or equivalent
- Treat enrollment, device replacement, and account recovery as core product work, not an afterthought
- Avoid “passwordless” claims unless you have proven recovery and cross-device behavior

### Implementation Sketch

```javascript
// Server: create options
const challenge = crypto.randomBytes(32);
await storeChallenge(userId, challenge);

return {
  challenge: challenge.toString("base64url"),
  rp: { name: "Your App", id: "example.com" },
  user: {
    id: Buffer.from(userId).toString("base64url"),
    name: userEmail,
    displayName: userDisplayName
  },
  pubKeyCredParams: [
    { alg: -7, type: "public-key" },
    { alg: -257, type: "public-key" }
  ],
  userVerification: "required",
  timeout: 60000,
  attestation: "none"
};
```

```javascript
// Browser
const credential = await navigator.credentials.create({
  publicKey: registrationOptions
});
```

```javascript
// Server-side verification must check:
// - challenge
// - origin / rpId
// - signature using stored public key
// - counter / device metadata as supported
```

### Recommended Libraries

| Platform | Library |
|----------|---------|
| Node.js | `@simplewebauthn/server` |
| Python | `py_webauthn` |
| Go | `github.com/go-webauthn/webauthn` |
| .NET | `Fido2NetLib` or current maintained FIDO2 library |

---

## Sessions vs Tokens

### Browser Apps: Prefer Sessions by Default

Use secure cookies unless a concrete architecture constraint points elsewhere.

```javascript
app.use(session({
  name: "__Host-session",
  secret: process.env.SESSION_SECRET,
  cookie: {
    httpOnly: true,
    secure: true,
    sameSite: "lax",
    path: "/"
  }
}));
```

Notes:

- Use `SameSite=Lax` or `Strict` intentionally; do not cargo-cult defaults
- Pair state-changing browser requests with CSRF protections where needed
- Rotate session identifiers on login and privilege change

### APIs: Use Short-Lived Access Tokens Deliberately

Use JWTs or opaque tokens when you need distributed validation, API delegation, or cross-service propagation.

```javascript
const accessToken = jwt.sign(
  {
    sub: user.id,
    aud: "your-api",
    iss: "https://auth.example.com",
    scope: "orders:read orders:write"
  },
  process.env.JWT_PRIVATE_KEY,
  {
    algorithm: "RS256",
    expiresIn: "15m",
    keyid: process.env.JWT_KID
  }
);
```

JWT guardrails:

- Keep access tokens short-lived
- Validate signature, issuer, audience, expiry, and algorithm
- Prefer asymmetric signing for multi-service verification
- Do not store browser bearer tokens in places that widen XSS impact
- If you need revocation-heavy behavior, prefer opaque tokens with introspection

### Refresh Tokens

- Rotate on use
- Bind to device/session context where practical
- Store hashed server-side if you persist them
- Revoke on logout, credential reset, suspicious activity, or inactivity thresholds

---

## OAuth 2.1 / OIDC

Prefer authorization code + PKCE for modern delegated auth.

### Minimum Checks

- Exact redirect URI matching
- `state` verification
- `nonce` where ID tokens are used
- Issuer and audience validation
- Scope minimization
- Token storage and refresh design reviewed explicitly

### Avoid

- Implicit flow
- Wildcard redirect URIs
- Treating ID tokens as API access tokens
- Over-broad long-lived scopes

---

## Service-to-Service Authentication

Prefer:

- Cloud workload identity
- SPIFFE / SPIRE style workload identity
- mTLS with short-lived certs
- OIDC federation for CI/CD and publishing workflows

Use API keys only when the integration surface is simple and low privilege. Scope, rotate, and monitor them.

---

## Authorization Models

### RBAC

Good for:

- Admin/operator separation
- Stable role sets
- Straightforward audit and UI permissioning

### ABAC

Good for:

- Tenant, region, data-classification, or device posture conditions
- Policies that depend on resource and subject attributes

### ReBAC

Good for:

- Collaboration models
- Shared content
- Resource owner/editor/viewer relationships

### General Rules

- Authorize on the server
- Check object ownership and tenancy on every resource access
- Deny by default
- Keep policy logic centralized enough to review and test

---

## Anti-Patterns

- Password-only auth as the “finished” state for new high-value apps
- SMS OTP as primary factor when phishing resistance is required
- Long-lived browser bearer tokens as the default web auth design
- Token contents trusted without signature and claim validation
- Authorization inferred from UI state
- “Admin” bypasses that skip normal object-level checks

---

## Testing Checklist

- Can one tenant access another tenant's data?
- Are refresh and logout flows actually revoking or rotating tokens?
- Can a replayed callback or stale state parameter succeed?
- Are passkey enrollment and recovery abuse cases covered?
- Do session fixation and CSRF tests exist for browser flows?
- Are privileged actions gated by fresh auth or step-up auth where needed?

---

## Sources to Verify Live

- NIST SP 800-63-4
- FIDO Alliance passkeys guidance
- WebAuthn Level 3 status
- OAuth 2.1 status and provider-specific support
- Vendor SDK behavior and deprecations
