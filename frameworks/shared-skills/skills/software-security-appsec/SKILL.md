---
name: software-security-appsec
description: "Provides application security guidance for design and implementation. Use when reviewing auth, data handling, supply-chain controls, or AppSec architecture."
compatibility: Portable core. Works on Claude Code and Codex.
version: "1.1"
last_validated: 2026-07-11
---

# Software Security And AppSec

Use this skill for application-layer security: authentication, authorization, input and output handling, cryptography, supply-chain controls, API security, threat modeling, and security reviews. It is the AppSec decision layer, not general backend or infrastructure hardening.

## Quick Reference

| Task | Use |
|------|-----|
| Auth and authorization choices | [references/authentication-authorization.md](references/authentication-authorization.md), [assets/web-application/template-authentication.md](assets/web-application/template-authentication.md), [assets/web-application/template-authorization.md](assets/web-application/template-authorization.md) |
| Input handling, uploads, rendering, and common bugs | [references/input-validation.md](references/input-validation.md), [references/common-vulnerabilities.md](references/common-vulnerabilities.md) |
| Secure design and threat modeling | [references/secure-design-principles.md](references/secure-design-principles.md), [references/threat-modeling-guide.md](references/threat-modeling-guide.md) |
| API and supply-chain security | [references/api-security-patterns.md](references/api-security-patterns.md), [references/supply-chain-security.md](references/supply-chain-security.md), [assets/api/template-secure-api.md](assets/api/template-secure-api.md) |
| Crypto and transport choices | [references/cryptography-standards.md](references/cryptography-standards.md) |
| Secret-storage selection | See "Secret-Storage Selection" below — choosing encrypted vs plaintext at the provider, and how to verify after storing |
| Incident response and security program framing | [references/incident-response-playbook.md](references/incident-response-playbook.md), [references/security-business-value.md](references/security-business-value.md), [references/operational-playbook.md](references/operational-playbook.md) |

## Secret-Storage Selection

Every major cloud provider has two surface-similar storage classes: one encrypted-at-rest with no readback, one plaintext-visible in the dashboard. Picking the wrong one is silent — the app still works — and the audit log for *who-read-what* exists only on the encrypted form. Plaintext reads are invisible.

| Provider | Yes Encrypted, never-readable | No Plaintext, dashboard-visible |
|---|---|---|
| Cloudflare Workers | `wrangler secret put` (API type: `secret_text`) | `[vars]` in `wrangler.toml`, Workers > Variables tab |
| Vercel | Environment Variables marked "Sensitive" | Standard Environment Variables |
| GitHub Actions | Repository / Organization Secrets | `env:` in workflow YAML, repository Variables |
| AWS | Secrets Manager, SSM Parameter Store `SecureString` | SSM `String`, plain Lambda env vars |
| Kubernetes | `Secret` + KMS envelope (SOPS, Sealed Secrets) | `ConfigMap`, plain env vars |

**Rules:**

- If the provider distinguishes "Secret" from "Variable" (or "Sensitive" from "Standard"), **always** use the encrypted form for: API keys, OAuth client secrets, JWT signing keys, database passwords, webhook secrets, push certificates.
- Identifiers that already appear in client builds (bundle IDs, Team IDs, KV namespace IDs, project IDs) are **not** secrets and belong in the plaintext config — putting them in the secret store both clutters and signals false risk.
- **Verify after storing.** `wrangler secret list` returns `type: secret_text` when encrypted. If you see `plain_text` or the value appears under `[vars]`, the credential is plaintext — treat as compromised and rotate.
- **PEM and other multi-line secrets must use CLI redirect, never dashboard paste.** Dashboards silently mangle newlines: `wrangler secret put APNS_AUTH_KEY --name worker < AuthKey_XXX.p8`.

**If you suspect a secret was stored as plaintext:** treat it as compromised. Revoke at the issuer, generate a new credential, store correctly, then verify. Deleting the visible plaintext copy does not invalidate any cached or scraped value. Rotation is a no-regret action; the cost is one credential refresh, the alternative is undetectable use.

## When to Use

- Review or design auth, session, token, or authorization flows.
- Validate input handling, uploads, rendering, and untrusted-data boundaries.
- Secure APIs, webhooks, browser apps, and admin surfaces.
- Threat-model a feature or AppSec architecture choice.
- Harden dependency, build, artifact, and release paths.
- Review agentic or MCP-connected applications from an AppSec angle.

## Route Elsewhere

- General backend engineering without a security focus: use [software-backend](../software-backend/SKILL.md).
- Infrastructure hardening, IAM, cluster policy, or cloud posture: use [ops-devops-platform](../ops-devops-platform/SKILL.md).
- Smart-contract-specific audits: use [software-crypto-web3](../software-crypto-web3/SKILL.md).
- ML pipeline or model-ops governance: use [ai-mlops](../ai-mlops/SKILL.md).
- Compliance-only interpretation with no implementation choice: route to legal or compliance stakeholders.

## Defaults

- Use OWASP Top 10:2025 for risk framing (released January 2026, replaces 2021 edition), ASVS for requirements depth, and SSDF for SDLC baselines.
- Treat standards, browser behavior, and current exploit trends as volatile until rechecked.
- Prefer passkeys where feasible and sessions for browser-first apps.
- Model trust boundaries before choosing controls.
- Treat tool calls, retrieved content, and long-term memory as untrusted input in agentic systems.

## Workflow

1. Identify the asset, trust boundary, attacker capability, and failure consequence.
2. Classify the problem: auth, authZ, untrusted input, API, supply chain, agentic flow, or secure-design issue.
3. Choose the control family from the relevant reference.
4. Apply the concrete safeguards and define verification depth.
5. Recheck volatile standards and provider behavior before final recommendations.

## ASCII Flow

```text
AppSec task
  -> Identify asset, trust boundary, attacker, and consequence
  -> Classify auth, authZ, input, API, supply chain, agentic, or design risk
  -> Choose control family and verification depth
  -> Implement concrete safeguards at the boundary
  -> Test exploit paths, regression cases, and logging
  -> Recheck volatile standards and document residual risk
```

## Auth Model Selection

| Situation | Choose | Avoid |
|-----------|--------|-------|
| Product with browser users, session state acceptable | Server sessions (cookie + server-side store) | JWTs for sessions — revocation is hard |
| Mobile/desktop app with device-native biometrics | Passkeys (WebAuthn) | SMS OTP — SIM-swap risk |
| Third-party sign-in or delegated access | OIDC / OAuth 2.1 + PKCE | Implicit flow (deprecated in OAuth 2.1) |
| API-to-API, no user context | mTLS or short-lived signed tokens | Long-lived API keys |
| Intra-service auth in a trusted cluster | Service accounts + mTLS | Shared secrets or user tokens |

## Input Control Selection

| Sink / operation | Required control |
|-----------------|-----------------|
| SQL query construction | Parameterized query or ORM binding; never string concatenation |
| Shell / process execution | Allowlist args; avoid shell=True / exec with user input |
| HTML rendering | Context-aware output encoding; CSP header |
| File upload destination path | Canonicalize; reject path traversal sequences; store outside webroot |
| Redirect target | Allowlist known origins; reject open redirect patterns |
| LDAP / XPath / XML | Library-level escaping or schema validation before query construction |
| LLM / agent tool call input | Treat as untrusted; validate schema before execution; log intent + scope |

## Core Decisions

### Authentication and Sessions

Default choices:
- passkeys when product and recovery flows support them
- server sessions for browser apps
- OIDC or OAuth 2.1 plus PKCE for delegated or third-party sign-in
- short-lived tokens only when true statelessness is required

Choose the simplest safe model that matches the app shape.

### Authorization and Input Boundaries

Minimum rules:
- deny by default
- check authorization on the server
- validate at boundaries
- parameterize dangerous sinks
- treat rich content and file uploads as active content until proven otherwise

### Secure Design and Threat Modeling

Threat-model before implementing:
- storage of sensitive data
- privileged actions
- external callbacks
- file uploads
- rich rendering
- agent or tool flows

Retroactive hardening is slower and weaker than secure-by-default design.

### Agentic and MCP Security

Model explicitly:
- prompt injection
- tool misuse
- memory poisoning
- cross-tenant leakage
- over-broad server capabilities
- unsafe approval flows

Keep read-only and mutating capabilities separate and log intent, scope, and result.

**Metered or costly actions** (medium confidence, single-source pattern — see [Fact-Checking](#fact-checking)): for any agent action that consumes a bounded quota, spends money, or is otherwise costly/irreversible, re-check current authorization and quota state immediately before that specific call, not from an earlier cached check. The original task assignment ("do X") is not standing consent to spend a metered resource — treat each metered call as needing its own fresh confirmation. On failure mid-run, resume from saved state rather than restarting, since restarting re-incurs the metered cost.

### Supply-Chain and Release Integrity

Use:
- lockfiles
- trusted publishing or provenance
- artifact integrity checks
- SBOM where relevant
- explicit review of transitive risk

## Verification Checklist

Before finalizing any AppSec design or review output:

- [ ] Trust boundary drawn explicitly — every input crossing it is validated or rejected
- [ ] Authentication model chosen from Defaults (passkeys → server session → OIDC/PKCE → short-lived token)
- [ ] Authorization checked server-side; deny-by-default enforced at every privileged endpoint
- [ ] All sinks parameterized: SQL, shell, LDAP, XPath, XML, HTML rendering, redirect targets
- [ ] File uploads and rich content treated as active content: type validation, size limit, storage isolation
- [ ] Secrets stored in encrypted provider form (see Secret-Storage Selection table); verify with provider CLI
- [ ] Supply-chain controls in place: lockfile, dependency scanning, artifact integrity, SBOM if required
- [ ] Agentic flows threat-modeled for prompt injection, tool misuse, cross-tenant leakage, and over-broad scopes
- [ ] Residual risks documented with mitigating controls and owner
- [ ] Standards and browser-behavior claims verified against current sources before final output

## Output Modes

Default to one of these:

- Security design brief:
  threats, control choices, and verification scope.
- Security review:
  findings, risks, and implementation priorities.
- Auth or API hardening plan:
  recommended model, pitfalls, and validation steps.
- Agentic AppSec review:
  threat model, capability boundaries, and approval controls.

## Known Traps

- Starting security review after architecture and product flows are already fixed, which turns foundational design issues into expensive compensating controls.
- Conflating authentication with authorization and assuming a valid identity token answers the permission question.
- Treating file uploads, rich text, markdown, or retrieved tool content as passive data instead of active attacker-controlled input.
- Reusing one permission surface for both read-only and mutating tool or MCP actions.
- Assuming infrastructure posture or a managed platform compensates for weak application-level control design.

## Anti-Patterns

- Treating standards status as evergreen without checking.
- Using auth mechanisms that are more complex than the app needs.
- Trusting unvalidated input deep in the system.
- Leaving tool or MCP permissions broad by default.
- Bolting security onto a feature after implementation choices are locked.
- Conflating infrastructure posture with application security design.

## Navigation

- Core references: [references/owasp-top-10.md](references/owasp-top-10.md), [references/authentication-authorization.md](references/authentication-authorization.md), [references/input-validation.md](references/input-validation.md), [references/cryptography-standards.md](references/cryptography-standards.md), [references/common-vulnerabilities.md](references/common-vulnerabilities.md)
- SDLC and architecture: [references/secure-design-principles.md](references/secure-design-principles.md), [references/threat-modeling-guide.md](references/threat-modeling-guide.md), [references/supply-chain-security.md](references/supply-chain-security.md), [references/zero-trust-architecture.md](references/zero-trust-architecture.md), [references/api-security-patterns.md](references/api-security-patterns.md)
- Operational references: [references/incident-response-playbook.md](references/incident-response-playbook.md), [references/security-business-value.md](references/security-business-value.md), [references/operational-playbook.md](references/operational-playbook.md)
- Templates and adjacent assets: [assets/web-application/template-authentication.md](assets/web-application/template-authentication.md), [assets/web-application/template-authorization.md](assets/web-application/template-authorization.md), [assets/api/template-secure-api.md](assets/api/template-secure-api.md), [data/sources.json](data/sources.json)
- Game theory (defender design — investment allocation, honeypots, patch decisions): [references/game-theory-applied.md](references/game-theory-applied.md)
- [references/reliability-theory-applied.md](references/reliability-theory-applied.md) — Reliability primitives (MTBF/MTTR, availability, FMEA, error budgets) applied to application security and resilience.
- Specialized deep-dives: [references/advanced-xss-techniques.md](references/advanced-xss-techniques.md) — advanced XSS vectors and comprehensive defense; [references/dotnet-efcore-crypto-security.md](references/dotnet-efcore-crypto-security.md) — .NET/EF Core crypto integration security; [references/smart-contract-security-auditing.md](references/smart-contract-security-auditing.md) — smart-contract (web3) security auditing methodology

## Fact-Checking

- Known bugs, regressions, framework/compiler/runtime footguns, and version-specific crash or workaround guidance must be verified against current primary web sources before being treated as current fact.
- Use [data/sources.json](data/sources.json) as the primary source map.
- Standards revisions, vendor defaults, and active agentic or MCP security guidance are time-sensitive and should be verified before being presented as current fact.
- Mark anything inferred or not rechecked as provisional.
- **Attribution**: the metered/costly-action re-consent pattern under [Agentic and MCP Security](#agentic-and-mcp-security) is adapted from `regulatory-threat-model` by Ansvar Systems AB, in [davila7/claude-code-templates](https://github.com/davila7/claude-code-templates) at commit `22d8efa9e9afcf31b98b7e3952ec557694e72c13`, licensed CC-BY-4.0. Extracted 2026-08-09. This is a single-source pattern (medium confidence) extracted from one vendor-specific, proprietary-tool-bound skill — treat it as a named pattern to consider, not a widely-corroborated convention.

## Learnings Loop

Before applying this skill on a non-trivial task, read `learnings.consolidated.md` in this directory (and `learnings.md` if present).

After applying it, if you encountered a pattern worth remembering, a mistake worth preventing, or a domain fact that surprised you, append one dated bullet to `learnings.md` via `agents-skills-feedback-loop/scripts/append_learning.py`. Do not modify `SKILL.md` itself.

