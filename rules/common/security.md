---
description: Secret, injection, and authorisation invariants for every coding session.
owner: skills/universal/software-clean-code-standard/SKILL.md
---
- Never hardcode, commit, or log secrets, credentials, or sensitive personal data (CC-SEC-03, CC-OBS-02).
- Never interpolate untrusted input into SQL, shell, or HTML; use parameterised queries, escaping, and safe APIs (CC-SEC-08).
- Enforce authorisation on every sensitive operation, with no bypass path (CC-SEC-02).
- Derive the tenant from the authenticated principal, never from a client-supplied field.
Why and procedure: skills/universal/software-clean-code-standard/references/clean-code-standard.md#security-hygiene-cc-sec
