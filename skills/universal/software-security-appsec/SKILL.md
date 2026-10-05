---
name: software-security-appsec
description: "Provides application security guidance for design and implementation. Use when reviewing auth, data handling, supply-chain controls, or AppSec architecture."
compatibility: Portable core. Works on Claude Code and Codex.
version: "1.2"
last_validated: 2026-07-11
---

# Software Security And AppSec

Use this skill for application-layer security: authentication, authorization, input and output handling, cryptography, supply-chain controls, API security, threat modeling, and security reviews. It is the AppSec decision layer, not general backend or infrastructure hardening.

## Quick Reference

| Task | Use |
|------|-----|
| Risk-category framing | [references/owasp-top-10.md](references/owasp-top-10.md) |
| Auth and authorization choices | [references/authentication-authorization.md](references/authentication-authorization.md), [assets/web-application/template-authentication.md](assets/web-application/template-authentication.md), [assets/web-application/template-authorization.md](assets/web-application/template-authorization.md) |
| Input handling, uploads, rendering, and common bugs | [references/input-validation.md](references/input-validation.md), [references/common-vulnerabilities.md](references/common-vulnerabilities.md) |
| Secure design and threat modeling | [references/secure-design-principles.md](references/secure-design-principles.md), [references/threat-modeling-guide.md](references/threat-modeling-guide.md) |
| API and supply-chain security | [references/api-security-patterns.md](references/api-security-patterns.md), [references/supply-chain-security.md](references/supply-chain-security.md), [assets/api/template-secure-api.md](assets/api/template-secure-api.md) |
| Crypto, password hashing, and transport choices | [references/cryptography-standards.md](references/cryptography-standards.md) |
| Agentic, LLM, and MCP application design | [references/agentic-llm-appsec.md](references/agentic-llm-appsec.md) (testing lives in qa-security-testing) |
| Mobile secure storage, pinning policy, attestation | [assets/mobile/template-mobile-security.md](assets/mobile/template-mobile-security.md) |
| Secret-storage selection | See "Secret-Storage Selection" below — choosing encrypted vs plaintext at the provider, and how to verify after storing |
| Incident response and security program framing | [references/incident-response-playbook.md](references/incident-response-playbook.md), [references/security-business-value.md](references/security-business-value.md), [references/operational-playbook.md](references/operational-playbook.md) |

## Secret-Storage Selection

Choose the provider's credential storage and verify who can read values; encryption at rest does not imply write-only access or complete read auditing.

| Provider | Credential storage | Check before use |
|---|---|---|
| Cloudflare Workers | `wrangler secret put` | Secret binding rather than a plain `vars` binding; see [Workers secrets](https://developers.cloudflare.com/workers/configuration/secrets/) |
| Vercel | Secret environment variable | Confirm the current write-only option and environment scope in [Vercel docs](https://vercel.com/docs/environment-variables/sensitive-environment-variables); a readable Config value may still be encrypted |
| GitHub Actions | Repository / Organization Secrets | Restrict workflow and environment access; keep credentials out of workflow `env:` literals and repository Variables |
| AWS | Secrets Manager or SSM `SecureString` | Restrict decrypt/read permissions; authorized clients can retrieve plaintext ([Secrets Manager retrieval](https://docs.aws.amazon.com/secretsmanager/latest/userguide/retrieving-secrets.html)) |
| Kubernetes | `Secret` with configured encryption at rest | Base64 alone is not encryption; restrict API and Pod-creation access ([Kubernetes Secrets](https://kubernetes.io/docs/concepts/configuration/secret/)) |

Use secret storage for API keys, signing keys, passwords and webhook secrets. Public identifiers belong in ordinary configuration. For multiline values, prefer a protected file or provider CLI input and verify exact bytes through an authorized test without printing the value; do not assume every dashboard corrupts newlines.

If a credential was exposed to unauthorized readers, revoke and rotate it at the issuer, remove exposed copies, and verify the replacement's scope. Storage in readable configuration warrants an exposure assessment; it does not by itself prove compromise.

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
- Smart-contract-specific audits: use [software-crypto-web3](../software-crypto-web3/SKILL.md) (owns the audit methodology in [references/smart-contract-security-auditing.md](references/smart-contract-security-auditing.md)).
- Security test tooling and coverage (SAST/DAST, LLM/agentic test suites): use [qa-security-testing](../qa-security-testing/SKILL.md).
- ML pipeline or model-ops governance: use [ai-mlops](../ai-mlops/SKILL.md).
- Compliance-only interpretation with no implementation choice: route to legal or compliance stakeholders.

## Defaults

- Use OWASP Top 10 for risk framing, ASVS for requirements depth, and NIST SSDF for SDLC baselines. At selection time, read the publishers' pages, record the edition and status applied, and distinguish a draft from a final standard: [OWASP Top 10](https://owasp.org/www-project-top-ten/), [ASVS](https://owasp.org/www-project-application-security-verification-standard/), [SSDF](https://csrc.nist.gov/Projects/ssdf), [SLSA](https://slsa.dev/spec/), [NIST digital identity](https://pages.nist.gov/800-63-4/), [WebAuthn](https://www.w3.org/TR/webauthn-3/), [OWASP GenAI](https://genai.owasp.org/). CRA applicability is covered in [supply-chain-security.md](references/supply-chain-security.md).
- Prefer passkeys where feasible and sessions for browser-first apps.
- Model trust boundaries before choosing controls.
- Treat tool calls, retrieved content, and long-term memory as untrusted input in agentic systems.

## Workflow

1. Identify the asset, trust boundary, attacker capability, and failure consequence.
2. Classify the problem: auth, authZ, untrusted input, API, supply chain, agentic flow, or secure-design issue.
3. Choose the control family from the relevant reference.
4. Apply the concrete safeguards and define verification depth.
5. Recheck volatile standards and provider behavior before final recommendations.

Scoping a self-audit with an AI reviewer: state that the team owns the code and the goal is remediation; review one module or trust boundary per pass; run static tools (SAST, dependency audit, secret scan) first and have the reviewer triage their output against the real code path; ask for fixes and safe reproductions, not exploit payloads. A whole-repository "find all vulnerabilities" prompt gives shallow, unverifiable findings and can trip provider safety filters.

## Auth Model Selection

| Situation | Choose | Avoid |
|-----------|--------|-------|
| Product with browser users, session state acceptable | Server sessions (cookie + server-side store) | JWTs for sessions — revocation is hard |
| Mobile/desktop app with device-native biometrics | Passkeys (WebAuthn) | SMS OTP — SIM-swap risk |
| Third-party sign-in or delegated access | OIDC for identity; OAuth authorization-code flow + PKCE for delegated access | Implicit flow; apply [RFC 9700](https://www.rfc-editor.org/rfc/rfc9700.html) security guidance |
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
- OIDC for sign-in; OAuth authorization-code flow plus PKCE for delegated access, following RFC 9700. Check [OAuth 2.1 status](https://oauth.net/2.1/) before presenting it as a final standard
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

Keep read-only and mutating capabilities separate and log intent, scope, and result. Never let one context combine untrusted content, private data, and an exfiltration or mutation channel. Threat-to-control design: [references/agentic-llm-appsec.md](references/agentic-llm-appsec.md).

**Metered or costly actions** (single-source design pattern): for any agent action that consumes a bounded quota, spends money, or is otherwise costly/irreversible, re-check current authorization and quota state immediately before that specific call, not from an earlier cached check. Apply the user-authorized budget and action scope; request fresh confirmation when a call would exceed them or when the authorization requires confirmation per call. On failure mid-run, resume from saved state rather than restarting, since restarting re-incurs the metered cost.

### Supply-Chain and Release Integrity

Use:
- lockfiles
- trusted publishing or provenance
- artifact integrity checks
- SBOM where relevant
- explicit review of transitive risk

## Verification Checklist

**Finding evidence gate.**

For each security finding, identify the attacker capability, reachable entry point, trust-boundary crossing, sink, and concrete impact. Separate confirmed exploit paths from defense-in-depth gaps and unverified hypotheses. Supply a safe reproduction or code-path trace plus the smallest viable remediation; severity follows exploitability and impact, not the presence of a risky-looking API alone.

Before finalizing any AppSec design or review output:

- [ ] Trust boundary drawn explicitly — every input crossing it is validated or rejected
- [ ] Authentication model chosen from Defaults (passkeys → server session → OIDC/PKCE → short-lived token)
- [ ] Authorization checked server-side; deny-by-default enforced at every privileged endpoint
- [ ] All sinks parameterized: SQL, shell, LDAP, XPath, XML, HTML rendering, redirect targets
- [ ] File uploads and rich content treated as active content: type validation, size limit, storage isolation
- [ ] Credentials use provider secret storage; verify read permissions, environment scope and encryption configuration
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
- Shipping a CSP with `'unsafe-inline'` or `'unsafe-eval'` as the default. Each one removes much of the XSS protection the policy exists for; treat any that a dependency forces as debt with an owner and a plan to move to nonces or hashes.

## Anti-Patterns

- Treating standards status as evergreen without checking.
- Using auth mechanisms that are more complex than the app needs.
- Trusting unvalidated input deep in the system.
- Leaving tool or MCP permissions broad by default.
- Bolting security onto a feature after implementation choices are locked.
- Conflating infrastructure posture with application security design.

## Navigation

- For control prioritization under uncertain attacker incentives, load [game-theory-applied.md](references/game-theory-applied.md); for availability tradeoffs, load [reliability-theory-applied.md](references/reliability-theory-applied.md).
- For lateral trust boundaries, load [zero-trust-architecture.md](references/zero-trust-architecture.md).
- For advanced browser payloads or .NET crypto integration, load [advanced-xss-techniques.md](references/advanced-xss-techniques.md) or [dotnet-efcore-crypto-security.md](references/dotnet-efcore-crypto-security.md).
- For contract-code risks, follow the software-crypto-web3 handoff above and use [assets/web3/crypto-security.md](assets/web3/crypto-security.md) for the vulnerability catalogue.
- When a claim needs source lookup, consult [data/sources.json](data/sources.json).

**Attribution**: the metered/costly-action authorization-check pattern under [Agentic and MCP Security](#agentic-and-mcp-security) is adapted from `regulatory-threat-model` by Ansvar Systems AB, in [davila7/claude-code-templates](https://github.com/davila7/claude-code-templates) at commit `22d8efa9e9afcf31b98b7e3952ec557694e72c13`, licensed CC-BY-4.0. Extracted 2026-08-09. This is a single-source pattern (medium confidence) extracted from one vendor-specific, proprietary-tool-bound skill — treat it as a named pattern to consider, not a widely-corroborated convention.

## Learnings Loop

When prior decisions or pitfalls are relevant, consult `learnings.consolidated.md` if present; use `learnings.md` only for needed history or as the available fallback. Otherwise skip both.

After applying it, if you encountered a pattern worth remembering, a mistake worth preventing, or a domain fact that surprised you, append one dated bullet to `learnings.md` via `agents-skills-feedback-loop/scripts/append_learning.py`. Do not modify `SKILL.md` itself.
