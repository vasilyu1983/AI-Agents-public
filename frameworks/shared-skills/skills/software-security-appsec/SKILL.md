---
name: software-security-appsec
description: Modern application security patterns aligned with OWASP Top 10:2025 (final), OWASP API Security Top 10 (2023), NIST SSDF, zero trust (incl. NSA ZIGs 2026), supply chain security (SBOM), passkeys/WebAuthn, authentication, authorization, input validation, cryptography, plus security ROI, breach cost modeling, and compliance-driven enterprise sales.
---

# Software Security & AppSec — Quick Reference

Production-grade security patterns for building secure applications in Jan 2026. Covers OWASP Top 10:2025 (stable) https://owasp.org/Top10/2025/ plus OWASP API Security Top 10 (2023) https://owasp.org/API-Security/ and secure SDLC baselines (NIST SSDF) https://csrc.nist.gov/publications/detail/sp/800-218/final.

---

## When to Use This Skill

Activate this skill when:

- Implementing authentication or authorization systems
- Handling user input that could lead to injection attacks (SQL, XSS, command injection)
- Designing secure APIs or web applications
- Working with cryptographic operations or sensitive data storage
- Conducting security reviews, threat modeling, or vulnerability assessments
- Responding to security incidents or compliance audit requirements
- Building systems that must comply with OWASP, NIST, PCI DSS, GDPR, HIPAA, or SOC 2
- Integrating third-party dependencies (supply chain security review)
- Implementing zero trust architecture or modern cloud-native security patterns
- Establishing or improving secure SDLC gates (threat modeling, SAST/DAST, dependency scanning)

### When NOT to Use This Skill

- **General backend development** without security focus → use [software-backend](../software-backend/SKILL.md)
- **Infrastructure/cloud security** (IAM, network security, container hardening) → use [ops-devops-platform](../ops-devops-platform/SKILL.md)
- **Smart contract auditing** as primary focus → use [software-crypto-web3](../software-crypto-web3/SKILL.md)
- **ML model security** (adversarial attacks, data poisoning) → use [ai-mlops](../ai-mlops/SKILL.md)
- **Compliance-only questions** without implementation → consult compliance team directly

---

## Quick Reference Table

| Security Task | Tool/Pattern | Implementation | When to Use |
|---------------|--------------|----------------|-------------|
| **Primary Auth** | Passkeys/WebAuthn | `navigator.credentials.create()` | New apps (2026+), phishing-resistant, broad platform support |
| Password Storage | bcrypt/Argon2 | `bcrypt.hash(password, 12)` | Legacy auth fallback (never store plaintext) |
| Input Validation | Allowlist regex | `/^[a-zA-Z0-9_]{3,20}$/` | All user input (SQL, XSS, command injection prevention) |
| SQL Queries | Parameterized queries | `db.execute(query, [userId])` | All database operations (prevent SQL injection) |
| API Authentication | OAuth 2.1 + PKCE | `oauth.authorize({ code_challenge })` | Third-party auth, API access (deprecates implicit flow) |
| Token Auth | JWT (short-lived) | `jwt.sign(payload, secret, { expiresIn: '15m' })` | Stateless APIs (always validate, 15-30 min expiry) |
| Data Encryption | AES-256-GCM | `crypto.createCipheriv('aes-256-gcm')` | Sensitive data at rest (PII, financial, health) |
| HTTPS/TLS | TLS 1.3 | Force HTTPS redirects | All production traffic (data in transit) |
| Access Control | RBAC/ABAC | `requireRole('admin', 'moderator')` | Resource authorization (APIs, admin panels) |
| Rate Limiting | express-rate-limit | `limiter({ windowMs: 15min, max: 100 })` | Public APIs, auth endpoints (DoS prevention) |
| Security Requirements | OWASP ASVS | Choose L1/L2/L3 | Security requirements baseline + test scope |

## Authentication Decision Matrix (Jan 2026)

| Method | Use Case | Token Lifetime | Security Level | Notes |
|--------|----------|----------------|----------------|-------|
| **Passkeys/WebAuthn** | Primary auth (2026+) | N/A (cryptographic) | Highest | Phishing-resistant, broad platform support |
| OAuth 2.1 + PKCE | Third-party auth | 5-15 min access | High | Replaces implicit flow, mandatory PKCE |
| Session cookies | Traditional web apps | 30 min - 4 hrs | Medium-High | HttpOnly, Secure, SameSite=Strict |
| JWT stateless | APIs, microservices | 15-30 min | Medium | Always validate signature, short expiry |
| API keys | Machine-to-machine | Long-lived | Low-Medium | Rotate regularly, scope permissions |

**Jurisdiction notes (verify):** Authentication assurance requirements vary by country, industry, and buyer. Prefer passkeys/FIDO2; treat SMS OTP as recovery-only/low assurance unless you can justify it.

## OWASP Top 10:2025 Quick Checklist

| # | Risk | Key Controls | Test |
|---|------|--------------|------|
| A01 | Broken Access Control | RBAC/ABAC, deny by default, CORS allowlist | BOLA, BFLA, privilege escalation |
| A02 | Security Misconfiguration | Harden defaults, disable unused features, error handling | Default creds, stack traces, headers |
| A03 | **Supply Chain Failures** (NEW) | SBOM, dependency scanning, SLSA, code signing | Outdated deps, typosquatting, compromised packages |
| A04 | Cryptographic Failures | TLS 1.3, AES-256-GCM, key rotation, no MD5/SHA1 | Weak ciphers, exposed secrets, cert validation |
| A05 | Injection | Parameterized queries, input validation, output encoding | SQLi, XSS, command injection, LDAP injection |
| A06 | Insecure Design | Threat modeling, secure design patterns, abuse cases | Design flaws, missing controls, trust boundaries |
| A07 | Authentication Failures | MFA/passkeys, rate limiting, secure password storage | Credential stuffing, brute force, session fixation |
| A08 | Integrity Failures | Code signing, CI/CD pipeline security, SRI | Unsigned updates, pipeline poisoning, CDN tampering |
| A09 | Logging Failures | Structured JSON, SIEM integration, correlation IDs | Missing logs, PII in logs, no alerting |
| A10 | **Exceptional Conditions** (NEW) | Fail-safe defaults, complete error recovery, input validation | Error handling gaps, fail-open, resource exhaustion |

## Decision Tree: Security Implementation

```text
Security requirement: [Feature Type]
    ├─ User Authentication?
    │   ├─ Session-based? → Cookie sessions + CSRF tokens
    │   ├─ Token-based? → JWT with refresh tokens (references/authentication-authorization.md)
    │   └─ Third-party? → OAuth2/OIDC integration
    │
    ├─ User Input?
    │   ├─ Database query? → Parameterized queries (NEVER string concatenation)
    │   ├─ HTML output? → DOMPurify sanitization + CSP headers
    │   ├─ File upload? → Content validation, size limits, virus scanning
    │   └─ API parameters? → Allowlist validation (references/input-validation.md)
    │
    ├─ Sensitive Data?
    │   ├─ Passwords? → bcrypt/Argon2 (cost factor 12+)
    │   ├─ PII/financial? → AES-256-GCM encryption + key rotation
    │   ├─ API keys/tokens? → Environment variables + secrets manager
    │   └─ In transit? → TLS 1.3 only
    │
    ├─ Access Control?
    │   ├─ Simple roles? → RBAC (assets/web-application/template-authorization.md)
    │   ├─ Complex rules? → ABAC with policy engine
    │   └─ Relationship-based? → ReBAC (owner, collaborator, viewer)
    │
    └─ API Security?
        ├─ Public API? → Rate limiting + API keys
        ├─ CORS needed? → Strict origin allowlist (never *)
        └─ Headers? → Helmet.js (CSP, HSTS, X-Frame-Options)
```

---

## Security ROI & Business Value (Jan 2026)

Security investment justification and compliance-driven revenue. Full framework: [references/security-business-value.md](references/security-business-value.md)

### Quick Breach Cost Reference

Indicative figures (source: IBM Cost of a Data Breach 2024; refresh for current year): https://www.ibm.com/reports/data-breach

| Metric | Global Avg | US Avg | Impact |
|--------|------------|--------|--------|
| Avg breach cost | $4.88M | $9.36M | Budget justification baseline |
| Cost per record | $165 | $194 | Data classification priority |
| Detection time | 204 days | 191 days | SIEM/monitoring ROI |
| DevSecOps adoption | -$1.68M | -34% | Shift-left justification |
| IR team | -$2.26M | -46% | Highest ROI control |

### Compliance → Enterprise Sales

| Certification | Deals Unlocked | Sales Impact |
|---------------|----------------|--------------|
| SOC 2 Type II | $100K+ enterprise | Typically reduces security questionnaire friction |
| ISO 27001 | $250K+ EU enterprise | Preferred vendor status |
| HIPAA | Healthcare vertical | Market access |
| FedRAMP | $1M+ government | US gov market entry |

### ROI Formula (Quick Reference)

```text
Security ROI = (Risk Reduction - Investment) / Investment × 100

Risk Reduction = Breach Probability × Avg Cost × Control Effectiveness
Example: 15% × $4.88M × 46% = $337K/year risk reduction
```

---

## Incident Response Patterns (Jan 2026)

### Security Incident Playbook

| Phase | Actions |
|-------|---------|
| **Detect** | Alert fires, user report, automated scan |
| **Contain** | Isolate affected systems, revoke compromised credentials |
| **Investigate** | Collect logs, determine scope, identify root cause |
| **Remediate** | Patch vulnerability, rotate secrets, update defenses |
| **Recover** | Restore services, verify fixes, update monitoring |
| **Learn** | Post-mortem, update playbooks, share lessons |

### Security Logging Requirements

| What to Log | Format | Retention |
|-------------|--------|-----------|
| Authentication events | JSON with correlation ID | 90 days minimum |
| Authorization failures | JSON with user context | 90 days minimum |
| Data access (sensitive) | JSON with resource ID | 1 year minimum |
| Security scan results | SARIF format | 1 year minimum |

**Do:**

- Include correlation IDs across services
- Log to SIEM (Splunk, Datadog, ELK)
- Mask PII in logs

**Avoid:**

- Logging passwords, tokens, or keys
- Unstructured log formats
- Missing timestamps or context

### Common Security Mistakes

| FAIL Bad Practice | PASS Correct Approach | Risk |
| --------------- | ------------------- | ---- |
| `query = "SELECT * FROM users WHERE id=" + userId` | `db.execute("SELECT * FROM users WHERE id=?", [userId])` | SQL injection |
| Storing passwords in plaintext or MD5 | `bcrypt.hash(password, 12)` or Argon2 | Credential theft |
| `res.send(userInput)` without encoding | `res.send(DOMPurify.sanitize(userInput))` | XSS |
| Hardcoded API keys in source code | Environment variables + secrets manager | Secret exposure |
| `Access-Control-Allow-Origin: *` | Explicit origin allowlist | CORS bypass |
| JWT with no expiration | `expiresIn: '15m'` + refresh tokens | Token hijacking |
| Generic error messages to logs | Structured JSON with correlation IDs | Debugging blind spots |
| SMS OTP as primary factor | Passkeys/WebAuthn or TOTP (keep SMS for recovery-only) | Credential phishing |

---

### Optional: AI/Automation Extensions

> **Note**: Security considerations for AI systems. Skip if not building AI features.

#### LLM Security Patterns

| Threat | Mitigation |
|--------|------------|
| Prompt injection | Input validation, output filtering, sandboxed execution |
| Data exfiltration | Output scanning, PII detection |
| Model theft | API rate limiting, watermarking |
| Jailbreaking | Constitutional AI, guardrails |

#### AI-Assisted Security Tools

| Tool | Use Case |
|------|----------|
| Semgrep | Static analysis with AI rules |
| Snyk Code | AI-powered vulnerability detection |
| GitHub CodeQL | Semantic code analysis |

---

## .NET/EF Core Crypto Integration Security

For C#/.NET crypto/fintech services using Entity Framework Core, see:

- [references/dotnet-efcore-crypto-security.md](references/dotnet-efcore-crypto-security.md) — Security rules and C# patterns

**Key rules summary:**

- No secrets in code — use configuration/environment variables
- No sensitive data in logs (tokens, keys, PII)
- Use `decimal` for financial values, never `double`/`float`
- EF Core or parameterized queries only — no dynamic SQL
- Generic error messages to users, detailed logging server-side

## Navigation

### Core Resources (Updated 2024-2026)

#### Security Business Value & ROI

- [references/security-business-value.md](references/security-business-value.md) — Breach cost modeling, security ROI formulas, compliance → enterprise sales, investment justification templates

#### 2025 Updates & Modern Architecture

- [references/supply-chain-security.md](references/supply-chain-security.md) — Dependency, build, and artifact integrity (SLSA, provenance, signing)
- [references/zero-trust-architecture.md](references/zero-trust-architecture.md) — NIST SP 800-207, service identity, policy-based access
- [references/owasp-top-10.md](references/owasp-top-10.md) — OWASP Top 10:2025 (final) guide + 2021→2025 diffs
- [references/advanced-xss-techniques.md](references/advanced-xss-techniques.md) — 2024-2025 XSS: mutation XSS, polyglots, SVG attacks, context-aware encoding

#### Foundation Security Patterns

- [references/secure-design-principles.md](references/secure-design-principles.md) — Defense in depth, least privilege, secure defaults
- [references/authentication-authorization.md](references/authentication-authorization.md) — AuthN/AuthZ flows, OAuth 2.1, JWT best practices, RBAC/ABAC
- [references/input-validation.md](references/input-validation.md) — Allowlist validation, SQL injection, XSS, CSRF prevention, file upload security
- [references/cryptography-standards.md](references/cryptography-standards.md) — AES-256-GCM, Argon2, TLS 1.3, key management
- [references/common-vulnerabilities.md](references/common-vulnerabilities.md) — Path traversal, command injection, deserialization, SSRF

#### External References

- [data/sources.json](data/sources.json) — 70+ curated security resources (OWASP 2025, supply chain, zero trust, API security, compliance)
- Shared checklists: [../software-clean-code-standard/assets/checklists/secure-code-review-checklist.md](../software-clean-code-standard/assets/checklists/secure-code-review-checklist.md), [../software-clean-code-standard/assets/checklists/backend-api-review-checklist.md](../software-clean-code-standard/assets/checklists/backend-api-review-checklist.md)

### Templates by Domain

#### Web Application Security

- [assets/web-application/template-authentication.md](assets/web-application/template-authentication.md) — Secure authentication flows (JWT, OAuth2, sessions, MFA)
- [assets/web-application/template-authorization.md](assets/web-application/template-authorization.md) — RBAC/ABAC/ReBAC policy patterns

#### API Security

- [assets/api/template-secure-api.md](assets/api/template-secure-api.md) — Secure API gateway, rate limiting, CORS, security headers

#### Cloud-Native Security

- [assets/cloud-native/crypto-security.md](assets/cloud-native/crypto-security.md) — Cryptography usage, key management, HSM integration

#### Blockchain & Web3 Security

- [references/smart-contract-security-auditing.md](references/smart-contract-security-auditing.md) — **NEW**: Smart contract auditing, vulnerability patterns, formal verification, Solidity security

### Related Skills

#### Security Ecosystem

- [../software-backend/SKILL.md](../software-backend/SKILL.md) — API implementation patterns and error handling
- [../software-architecture-design/SKILL.md](../software-architecture-design/SKILL.md) — Secure system decomposition and dependency design
- [../ops-devops-platform/SKILL.md](../ops-devops-platform/SKILL.md) — DevSecOps pipelines, secrets management, infrastructure hardening
- [../software-crypto-web3/SKILL.md](../software-crypto-web3/SKILL.md) — Smart contract security, blockchain vulnerabilities, DeFi patterns
- [../qa-testing-strategy/SKILL.md](../qa-testing-strategy/SKILL.md) — Security testing, SAST/DAST integration, penetration testing

#### AI/LLM Security

- [../ai-llm/SKILL.md](../ai-llm/SKILL.md) — LLM security patterns including prompt injection prevention
- [../ai-mlops/SKILL.md](../ai-mlops/SKILL.md) — ML model security, adversarial attacks, privacy-preserving ML

#### Quality & Resilience

- [../qa-resilience/SKILL.md](../qa-resilience/SKILL.md) — Resilience, safeguards, failure handling, chaos engineering
- [../qa-refactoring/SKILL.md](../qa-refactoring/SKILL.md) — Security-focused refactoring patterns

---

## Trend Awareness Protocol

**IMPORTANT**: When users ask recommendation questions about application security, you MUST use WebSearch to check current trends before answering. If WebSearch is unavailable, use `data/sources.json` + web browsing and state what you verified vs assumed.

### Trigger Conditions

- "What's the best approach for [authentication/authorization]?"
- "What should I use for [secrets/encryption/API security]?"
- "What's the latest in application security?"
- "Current best practices for [OWASP/zero trust/supply chain]?"
- "Is [security approach] still recommended in 2026?"
- "What are the latest security vulnerabilities?"
- "Best auth solution for [use case]?"

### Required Searches

1. Search: `"application security best practices 2026"`
2. Search: `"OWASP Top 10 2025 2026"`
3. Search: `"[authentication/authorization] trends 2026"`
4. Search: `"supply chain security 2026"`

### What to Report

After searching, provide:

- **Current landscape**: What security approaches are standard NOW
- **Emerging threats**: New vulnerabilities or attack vectors
- **Deprecated/declining**: Approaches that are no longer secure
- **Recommendation**: Based on fresh data and current advisories

### Example Topics (verify with fresh search)

- OWASP Top 10 updates
- Passkeys and passwordless authentication
- AI security concerns (prompt injection, model poisoning)
- Supply chain security (SBOMs, dependency scanning)
- Zero trust architecture implementation
- API security (BOLA, broken auth)

---

## Operational Playbooks
- [references/operational-playbook.md](references/operational-playbook.md) — Core security principles, OWASP summaries, authentication patterns, and detailed code examples
