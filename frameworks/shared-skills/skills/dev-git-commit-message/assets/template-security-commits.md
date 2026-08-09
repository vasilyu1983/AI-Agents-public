# Security-Sensitive Commit Message Guide

Use this file when the commit itself is security-relevant and the subject line alone is not enough.

This is a commit-message aid, not a full incident-response runbook.

---

## Default Form

Prefer standard Conventional Commit types with a `security` scope:

```text
fix(security): patch reflected XSS in comment preview
chore(security): rotate staging webhook credentials
feat(security): add brute-force rate limiting to login flow
```

Use a top-level `security:` type only if the repository already supports that custom type in linting and release tooling.

---

## When To Add A Body

Add a body when:

- the vulnerability or control change is not obvious from the subject
- reviewers need deployment or rollback notes
- the change introduces a breaking security behavior
- the repo requires audit or incident context

Template:

```text
fix(security): patch reflected XSS in comment preview

Why:
- Unescaped HTML in preview mode allowed script injection

What:
- Escape rendered preview content before display
- Add regression coverage for encoded and malformed payloads

Notes:
- Tests: added regression coverage for preview sanitization
- Risks/rollback: revert preview escaping only after compensating control exists
```

---

## Good Patterns

### Vulnerability Fix

```text
fix(security): reject unsigned webhook payloads

Why:
- Unsigned requests could bypass provider authenticity checks

What:
- Require HMAC verification before processing webhook events

Notes:
- Tests: added valid and invalid signature cases
```

### Credential Rotation

```text
chore(security): rotate sandbox payment webhook secret

Why:
- Previous secret was exposed to an internal test channel

What:
- Replace sandbox secret and update deployment configuration

Notes:
- Tests: validated webhook delivery after rotation
- Risks/rollback: old secret remains revoked
```

### Hardening Change

```text
feat(security): add rate limiting to password reset endpoint

Why:
- Reduce credential-stuffing and reset abuse risk

What:
- Enforce per-IP and per-account rate limits with audit logging
```

### Breaking Security Change

```text
fix(auth)!: require signed session tokens

BREAKING CHANGE: Unsigned legacy tokens are no longer accepted.
Clients must re-authenticate before the next deploy window.
```

---

## Avoid

- Vague subjects such as `fix security` or `security update`
- Assistant or tool attribution in the message body or trailers
- Promising impact you did not verify in the diff
- Copying live secrets, indicators, or sensitive internal URLs into the commit message
- Treating a leaked secret as "fixed" without rotation

---

## Minimal Incident Note

If the commit removes or rotates an exposed secret:

1. Rotate or revoke the secret first.
2. Then clean history only if repository policy requires it.
3. Keep the commit message factual and non-sensitive.

Good:

```text
chore(security): revoke exposed staging API key
```

Bad:

```text
chore(security): revoke key sk_live_123456 exposed in Slack
```

---

## Related References

- [template-commit-message.md](template-commit-message.md)
- [../references/conventional-commits-guide.md](../references/conventional-commits-guide.md)
- [../references/commit-message-antipatterns.md](../references/commit-message-antipatterns.md)
- [../data/sources.json](../data/sources.json)
