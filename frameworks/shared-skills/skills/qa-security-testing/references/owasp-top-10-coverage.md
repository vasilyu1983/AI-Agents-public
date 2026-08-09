# OWASP Top 10 Coverage Maps

> Verify OWASP edition currency at owasp.org before citing.

Maps CI scanner tooling to three OWASP Top 10 lists. Each entry: risk description + the scanner
or test type that catches it. Use as a gap-analysis checklist when configuring a security pipeline.

**How to use this file**

1. Pick the list(s) relevant to your application type (REST/GraphQL APIs → API Top 10;
   LLM-integrated apps → LLM Top 10; general web apps → Top 10 2025).
2. For each item, confirm you have the listed scanner or test type in CI.
3. Items flagged "manual / pen-test" in the gap table cannot be automated — schedule them as
   periodic red-team or architecture review activities.
4. Cross-reference with [supply-chain-security.md](supply-chain-security.md) for A03:2025 /
   A08:2025 and LLM03:2025 supply-chain coverage details.

## Contents

- [OWASP API Top 10 (2023)](#owasp-api-top-10-2023)
- [OWASP LLM Top 10 (v2 2025)](#owasp-llm-top-10-v2--2025-edition)
- [OWASP Top 10 for Agentic Applications (2026)](#owasp-top-10-for-agentic-applications-2026)
- [OWASP Top 10 (2025)](#owasp-top-10-2025)
- [Coverage Gap Analysis](#coverage-gap-analysis)
- [Scanner Setup Notes](#scanner-setup-notes)
- [Triage: Severity vs. Exploitability vs. Reachability](#triage-severity-vs-exploitability-vs-reachability)
- [When Pen-Testing Beats Scanning](#when-pen-testing-beats-scanning)
- [False-Positive Economics](#false-positive-economics)

---

## OWASP API Top 10 (2023)

Source: https://owasp.org/API-Security (API2023 edition, OWASP considers this the current release)

| ID | Risk | Scanner / Test |
|----|------|----------------|
| API1:2023 | **Broken Object Level Authorization** — API returns objects owned by other users when the requester supplies a different resource ID | DAST (ZAP active scan, Nuclei BOLA templates); integration tests with cross-tenant requests |
| API2:2023 | **Broken Authentication** — Weak tokens, missing expiry, or credential stuffing not rate-limited | DAST (ZAP authentication scan); Semgrep rules for JWT `alg:none` and hardcoded secrets |
| API3:2023 | **Broken Object Property Level Authorization** — Over-exposed fields; mass assignment allows writing fields the caller should not control | SAST (Semgrep mass-assignment rules); API contract tests checking response schema |
| API4:2023 | **Unrestricted Resource Consumption** — No rate limits or query depth limits enable DoS or cost escalation | DAST (ZAP rate-limit probe, Nuclei); load tests; API gateway policy review |
| API5:2023 | **Broken Function Level Authorization** — Admin or privileged endpoints accessible to lower-privilege roles | DAST (authenticated scanning with low-privilege token); Semgrep `@admin` route pattern checks; regression tests |
| API6:2023 | **Unrestricted Access to Sensitive Business Flows** — Business logic flows (bulk account creation, promo abuse) can be automated without detection | Manual pen-test; Nuclei business logic templates; rate-limit regression tests |
| API7:2023 | **Server-Side Request Forgery** — Attacker causes server to make requests to internal or external URLs | SAST (Semgrep SSRF rules, CodeQL taint tracking); DAST (ZAP SSRF active scan) |
| API8:2023 | **Security Misconfiguration** — Default credentials, verbose errors, permissive CORS, missing headers | DAST (ZAP passive scan, Nuclei misconfig templates); IaC scan (Checkov, Trivy) |
| API9:2023 | **Improper Inventory Management** — Outdated or shadow API versions remain accessible | DAST against all known API versions; OpenAPI spec diff in CI; Nuclei version-detection templates |
| API10:2023 | **Unsafe Consumption of APIs** — Third-party API data trusted without validation enables injection or logic bypass | SAST (Semgrep input-validation rules); dependency scanning (Trivy, Snyk) for third-party SDK CVEs |

---

## OWASP LLM Top 10 (v2 — 2025 edition)

Source: https://owasp.org/www-project-top-10-for-large-language-model-applications

Note: OWASP also released a **separate** Top 10 for Agentic Applications (2026 edition, see below)
covering autonomous multi-step agents. If your application uses autonomous agents with tool access,
consult both lists — an agent built on an LLM is exposed to both sets of risks simultaneously.

| ID | Risk | Scanner / Test |
|----|------|----------------|
| LLM01:2025 | **Prompt Injection** — Malicious content in user or retrieved input overrides system instructions | SAST (Semgrep rules for unsanitized prompt concatenation); adversarial prompt regression tests; red-team eval harness |
| LLM02:2025 | **Sensitive Information Disclosure** — Model leaks PII, credentials, or proprietary training data in output | Output validation tests asserting no PII patterns; secret scanning on logged completions; DAST probes sending extraction prompts |
| LLM03:2025 | **Supply Chain Vulnerabilities** — Compromised model weights, training data, or fine-tuning pipeline | SCA (Snyk/Trivy) on ML dependency stack; model provenance checks (SLSA attestations); `cosign verify` on model container images |
| LLM04:2025 | **Data and Model Poisoning** — Malicious training or RAG data biases model behavior | Data pipeline integrity checks; input validation on RAG corpus ingestion; audit log review |
| LLM05:2025 | **Improper Output Handling** — LLM output passed unsanitized to downstream systems causes XSS, SQLi, or command injection | SAST (Semgrep injection rules on output-handling code); integration tests asserting output sanitization |
| LLM06:2025 | **Excessive Agency** — Autonomous agent granted more permissions than needed escalates blast radius of prompt injection | Code review of tool permission scopes; regression tests verifying least-privilege tool grants; SAST for over-broad API scope |
| LLM07:2025 | **System Prompt Leakage** — System prompt extractable via crafted user inputs, exposing business logic | Regression tests asserting system prompt not echoed; DAST extraction probes |
| LLM08:2025 | **Vector and Embedding Weaknesses** — Manipulated vector store entries influence retrieval, poisoning RAG responses | Integrity checks on vector store upserts; input validation on documents before embedding; monitoring for anomalous retrieval patterns |
| LLM09:2025 | **Misinformation** — Model generates confidently wrong factual claims leading to harmful decisions | Factual evaluation harness (compare against ground truth); output confidence calibration tests |
| LLM10:2025 | **Unbounded Consumption** — Unlimited token, query, or compute consumption enables DoS or runaway cost | Rate limiting at the API gateway level; DAST probe for missing limits; cost anomaly monitoring; load tests |

---

## OWASP Top 10 for Agentic Applications (2026)

Source: https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/ — announced
2025-12-09 (OWASP GenAI Security Project, Black Hat Europe / OWASP Agentic Security Summit) and
officially released; current edition as of 2026-07. Uses the **ASI** ID prefix (Agentic Security
Issues) rather than a plain number, distinguishing it from the LLM Top 10's **LLM** prefix. This
list targets risks that only exist once an LLM is wired to tools, memory, and other agents —
`LLM06 Excessive Agency` is the bridge risk shared with the LLM Top 10.

| ID | Risk | Scanner / Test |
|----|------|----------------|
| ASI01:2026 | **Planning and Goal Manipulation** — Attacker-influenced task decomposition or planning steps redirect the agent toward unintended goals | Adversarial regression suite injecting goal-altering content mid-plan; assertions on final-goal invariants; red-team eval harness |
| ASI02:2026 | **Tool Misuse** — Agent invokes a legitimate tool with attacker-influenced or unvalidated arguments (SSRF via a fetch tool, destructive calls via a shell/DB tool) | SAST/schema validation on tool-argument construction; integration tests with adversarial tool-call payloads; tool allowlisting review |
| ASI03:2026 | **Identity and Delegated Trust** — Agent acts under a human's or another agent's identity with broader scope than the delegator intended | Regression tests asserting delegated-token scope narrowing; code review of impersonation/on-behalf-of flows |
| ASI04:2026 | **Agentic Supply Chain** — Compromised tool/plugin registries, sub-agent packages, or third-party agent frameworks | SCA on agent framework and tool-plugin dependencies; provenance/signature checks on installed tools and sub-agent packages (SLSA/cosign) |
| ASI05:2026 | **Code Execution** — Agent executes attacker-influenced code (generated scripts, sandboxed code-interpreter tools) escaping intended sandbox boundaries | Sandbox escape regression tests; SAST on code-execution tool wrappers; container/seccomp policy review for the execution sandbox |
| ASI06:2026 | **Memory Poisoning** — Persistent agent memory (long-term store, vector memory, session state) is poisoned to influence future sessions | Integrity checks on memory writes; regression tests asserting untrusted content cannot alter stored memory without review; periodic memory audit |
| ASI07:2026 | **Inter-Agent Communication Abuse** — Malicious or compromised peer agent sends crafted messages that a receiving agent trusts implicitly | Message-schema validation between agents; tests asserting agent-to-agent messages are treated as untrusted input, not instructions |
| ASI08:2026 | **Cascading Failures** — A single compromised or malfunctioning agent's output propagates uncorrected through a multi-agent pipeline | Circuit-breaker / bulkhead tests between agent stages; chaos tests injecting bad output at each pipeline stage and asserting downstream containment |
| ASI09:2026 | **Human-Agent Trust Exploitation** — Agent's persuasive or authoritative framing induces a human operator to approve an unsafe action without real scrutiny | UX review of approval prompts (rubber-stamp risk); regression tests asserting high-risk actions require explicit, specific confirmation, not blanket approval |
| ASI10:2026 | **Rogue Agents** — An agent (or sub-agent it spawned) continues acting autonomously outside its intended scope or after its task should have ended | Tests asserting hard termination/kill-switch paths; monitoring for agent activity after task-completion signal; spawn-depth and lifetime limits |

Gap note: ASI01, ASI03, ASI08, ASI09, and ASI10 are largely **not** catchable by conventional
SAST/DAST/SCA — they require adversarial multi-turn simulation, chaos testing of agent pipelines,
and human-factors review of approval UX. Budget for this as its own testing category, not an
extension of existing scanner coverage.

---

## OWASP Top 10 (2025)

Source: https://owasp.org/Top10/2025/ (OWASP Top 10:2025 is the current full release: announced at
OWASP Global AppSec Washington D.C. in November 2025, with final published text released January
2026; supersedes the 2021 edition)

Changes from 2021 that affect this map: **A03:2025 Software Supply Chain Failures** is a new,
broader category that absorbs 2021's *Vulnerable and Outdated Components*; **A10:2025 Mishandling
of Exceptional Conditions** is new; **SSRF** (2021 A10) is consolidated into **A01:2025 Broken
Access Control**; *Security Misconfiguration* rises to **A02:2025**; *Cryptographic Failures*
moves to **A04:2025**; A09 is renamed *Security Logging and **Alerting** Failures*. Scanner/test
mappings below are unchanged in substance — only the category IDs are remapped. If your scanner
still emits 2021 tags (many do, pending rule-pack updates), treat the 2021 ID as an alias.

| ID | Risk | Scanner / Test |
|----|------|----------------|
| A01:2025 | **Broken Access Control** — Users act outside intended permissions; now includes SSRF (server fetches attacker-supplied URL → internal network access) | DAST (ZAP access-control + SSRF active scan, Nuclei); SAST (Semgrep auth-bypass + SSRF rules, CodeQL); integration tests asserting authorization boundaries and outbound-URL allowlists |
| A02:2025 | **Security Misconfiguration** — Insecure defaults, unnecessary features, verbose errors, permissive CORS, missing headers | DAST passive scan; IaC scan (Checkov, Trivy); CIS Benchmark scan; automated header checks (Mozilla Observatory) |
| A03:2025 | **Software Supply Chain Failures** — Compromised dependencies, build pipeline, or distribution; known CVEs in components or runtime | SCA (Dependabot, Trivy, Snyk); container image scan (Trivy); `npm audit` / `pip-audit`; SLSA provenance + SBOM attestations; `cosign verify` on artifacts |
| A04:2025 | **Cryptographic Failures** — Sensitive data exposed due to weak or missing encryption | SAST (Semgrep crypto rules, CodeQL taint for HTTP vs HTTPS); Trivy secrets scan; TLS configuration scan (testssl.sh) |
| A05:2025 | **Injection** — Untrusted data sent to an interpreter (SQL, OS, LDAP, XSS) | SAST (Semgrep, CodeQL injection queries); DAST (ZAP active scan); parameterized query enforcement in code review |
| A06:2025 | **Insecure Design** — Missing threat model, security controls absent by design | Threat modeling (STRIDE); architecture review; SAST rules for design-level anti-patterns (hardcoded secrets, no input bounds) |
| A07:2025 | **Authentication Failures** — Credential stuffing, weak passwords, missing MFA, weak session management | DAST (ZAP auth scan); Semgrep rules for session management anti-patterns; regression tests on login rate limiting |
| A08:2025 | **Software or Data Integrity Failures** — Unsigned updates, insecure deserialization, CI/CD pipeline compromise | Supply-chain checks: `cosign verify`, SLSA provenance, SBOM attestations; SAST deserialization rules (Semgrep, CodeQL) |
| A09:2025 | **Security Logging and Alerting Failures** — Insufficient logging/alerting prevents breach detection and timely response | Code review for log coverage on auth events; integration tests asserting audit log entries; SIEM/alert coverage review |
| A10:2025 | **Mishandling of Exceptional Conditions** — Swallowed exceptions, fail-open error paths, improper error handling leak state or bypass controls | SAST rules for empty/over-broad catch blocks and fail-open patterns (Semgrep, CodeQL); code review of error/exception paths; tests asserting fail-closed behavior on forced faults |

---

## Coverage Gap Analysis

Use this table to identify which scanner categories cover each OWASP list:

| Scanner category | API Top 10 | LLM Top 10 | Top 10 (2025) |
|-----------------|:----------:|:----------:|:-------------:|
| SAST (Semgrep / CodeQL) | API1,7,8 | LLM1,3,5,6,7 | A01,04,05,06,08,10 |
| DAST (ZAP / Nuclei) | API1–6,8,9 | LLM2,7,10 | A01,02,05,07 |
| SCA (Dependabot / Trivy / Snyk) | API10 | LLM3 | A03 |
| IaC scan (Checkov / Trivy) | API8 | — | A02 |
| Supply-chain (cosign / SLSA) | — | LLM3,4,8 | A03,08 |
| Regression / integration tests | API1,4,5,6 | LLM1,2,6,7,8,10 | A01,04,07,09,10 |
| Manual / pen-test | API6 | LLM4,9 | A06,09 |

Gaps not covered by automated tooling (API6 business logic, LLM4 data poisoning, A06:2025
insecure design) MUST be addressed through threat modeling, manual red-teaming, and architecture
review.

---

## Scanner Setup Notes

### SAST — Semgrep and CodeQL

- Semgrep registry includes OWASP-tagged rule packs (`p/owasp-top-ten`, `p/owasp-api-top-10`).
  Enable them with `semgrep --config p/owasp-top-ten` or add to `semgrep.yml` in CI.
- CodeQL ships built-in query suites for injection (A05:2025), authentication failures
  (A07:2025), SSRF (now under A01:2025), and path traversal; run with
  `--suite security-extended` for broadest OWASP coverage.

### DAST — OWASP ZAP

- Use the ZAP Automation Framework (`automation.yaml`) with the `activeScan` job targeting your
  staging environment. The built-in scan policy maps to OWASP Top 10 categories.
- For API coverage use the `openapi` context plan so ZAP exercises all API1–API10 endpoints.
- Run ZAP after every staging deploy, not on every PR (full scan: 10–40 min for average APIs).

### SCA — Dependabot / Trivy / Snyk

- All three tools report against CVE databases with CVSS scores. Map severity thresholds:
  CVSS ≥ 9.0 = Critical (A06 block); 7.0–8.9 = High (warning or block per policy).
- Generate SBOMs with `trivy image --format cyclonedx` so you can audit A03:2025 supply-chain
  and A08:2025 integrity at the component level.

### LLM-specific Testing

- Prompt injection regression tests: maintain a fixture file of known injection payloads; assert
  the model does not execute them. Run in CI on every PR that touches prompt templates.
- For LLM10 (unbounded consumption): instrument token usage in tests and assert a hard ceiling.
  Fail the test if a single request exceeds the configured max-tokens budget.

### Tooling Version Pins

Pin scanner versions in CI to avoid silent behavior changes breaking your gate baselines. For
container-based actions, prefer SHA pinning over tag pinning — the March 2026 Trivy supply chain
compromise (76 tags force-pushed with credential-stealing malware) demonstrated that even a
widely-trusted scanner's mutable tags can be hijacked. Verify pinned actions with
`gh attestation verify` where attestations are available.

```yaml
# Example version pins in GHA — use SHA where supply-chain trust is critical
uses: semgrep/semgrep-action@v1                  # or pin to @sha256:...
uses: aquasecurity/trivy-action@0.35.0           # pin to a release SHA, not just a tag — see container-iac-scanning.md incident note; do NOT use @main or @latest
uses: zaproxy/action-full-scan@v0.12.0
uses: gitleaks/gitleaks-action@v2
```

Review and update pins quarterly or when a scanner publishes a security advisory for itself. After
any scanner supply-chain incident: rotate all secrets that were accessible to workflows running the
compromised version during the exposure window before resuming normal operations.

### OWASP ASVS 5.0

OWASP ASVS 5.0.0 was released May 30, 2025 (first major release since 4.0 in 2019). It contains
~350 requirements across 17 chapters, with action-oriented language, expanded coverage for APIs,
SPAs, and microservices, and alignment with NIST SP 800-63B v4 on passwords. ASVS 5.0 supersedes
ASVS 4.0.3 for new assessments.

Key change for testing: ASVS 5.0 explicitly states that meaningful verification requires internal
artifact access — black-box testing alone is insufficient for most controls. ~60–70% of
requirements can be automated with SAST, SCA, and configuration review. Future CWE/OWASP
cross-mappings will route through the OWASP Common Requirement Enumeration (CRE) project rather
than direct ASVS anchors.

Source: https://owasp.org/www-project-application-security-verification-standard/

---

## Triage: Severity vs. Exploitability vs. Reachability

A scanner's severity rating (CVSS) answers one question — "how bad is this if triggered?" It does
not answer "how likely is this to be triggered?" or "can an attacker even reach this code path in
our deployment?" Treating CVSS alone as the triage signal is the single most common cause of both
wasted remediation effort (fixing unreachable criticals) and missed risk (ignoring a "medium" that
is being actively exploited). Combine three independent signals before setting an SLA clock:

| Signal | What it tells you | Source | Failure mode if ignored |
|--------|-------------------|--------|--------------------------|
| **Severity** (CVSS) | Technical impact if the vulnerable path executes | Scanner-reported CVSS 3.1 or 4.0 vector | Over-indexing on a 9.8 that lives in a dev-only tool nobody exposes |
| **Exploitability-in-the-wild** (EPSS) | Probability this specific CVE is exploited in the next 30 days, given real attacker activity | [FIRST.org EPSS](https://www.first.org/epss/) score (0-1); current model EPSS v4 (2025.03.14) | Missing a CVSS 6.5 with a 0.94 EPSS score (mass-exploited) while burning a sprint on an unreachable 9.1 |
| **Reachability** | Whether your specific build actually calls the vulnerable function/path | SCA reachability analysis (Snyk, Semgrep Supply Chain), manual code-path tracing, or architecture review | Auto-closing every dependency finding as "not applicable" without verifying, which quietly reintroduces risk when the code path changes later |

**Working triage rule of thumb** (tune to your risk appetite, do not copy blindly):

- High CVSS + high EPSS + reachable → treat as Critical regardless of scanner label; page now.
- High CVSS + low EPSS + not reachable → track normally at standard SLA; do not let raw CVSS panic
  a P1 response for code that cannot execute.
- Any CVSS + high EPSS (roughly EPSS > 0.5, i.e. mass-exploited in the wild) + reachable → escalate
  even if CVSS lands in the "Medium" band; EPSS is telling you attackers do not care about your
  CVSS math.
- Low CVSS + low EPSS + unknown reachability → default SLA tier, revisit if reachability analysis
  becomes cheap enough to run at scale (most orgs cannot reachability-check every finding, so spend
  that budget on the highest CVSS×EPSS products first).

**CVSS version note**: as of 2026, NVD publishes both CVSS 3.1 and 4.0 for new CVEs; historical
CVEs keep their 3.1 score only. The numeric severity bands are the same (Critical 9.0-10, High
7.0-8.9, Medium 4.0-6.9, Low 0.1-3.9) but the two versions compute the score from the vector
differently (v4.0 adds Safety/Automatable metrics and drops the old impact-subscore formula). Do
not assume a v3.1 "7.5" and a v4.0 "7.5" reflect identical underlying risk reasoning — check which
version produced the score before comparing across a mixed-vintage vulnerability backlog.

## When Pen-Testing Beats Scanning

Scanners (SAST/DAST/SCA) are necessary but structurally blind to a specific class of risk: anything
that requires understanding your business logic, chaining multiple low-severity findings into a
high-impact path, or reasoning about intent rather than pattern-matching syntax. Reach for a human
pen-test or red-team engagement — not another scanner — when:

- The risk is a **business-logic abuse case** (promo-code stacking, price manipulation via
  parallel requests, workflow-state bypass) — no scanner has a rule for "this violates our
  intended business flow," because the flow is bespoke to your product.
- You need to validate an **exploit chain**, not a single finding — e.g., a low-severity
  information leak combined with a medium-severity auth weakness combined with a low-severity
  IDOR that together produce full account takeover. Scanners report findings independently; only
  a human (or a scenario-driven BAS run) tests the chain.
- The target is **freshly re-architected** (new auth model, new multi-tenancy boundary, new
  payment flow) — scanner rule packs lag novel architectures by months; a focused pen-test before
  GA catches what rules have not been written for yet.
- You have a **compliance requirement for independent, human-attested testing** (PCI DSS
  penetration testing requirement, SOC 2 customer requests, cyber-insurance underwriting) — a
  scanner report does not satisfy these; they require a named tester's attestation.
- Your automated coverage has **plateaued** (new findings per PR trending near zero for months) —
  this can mean the codebase is clean, or it can mean your rule packs have stopped finding
  anything novel. A pen-test is the cheapest way to tell the two apart.

Scanners win on cadence, cost, and regression prevention (they run on every PR forever); pen-tests
win on judgment, chaining, and novel-architecture coverage. Run both — scanners continuously,
pen-tests/red-team at major release boundaries and on a fixed minimum cadence (annually is a
compliance floor, not a security target; align cadence to how fast your architecture changes).

## False-Positive Economics

Every suppressed or ignored finding has a cost on both sides of the ledger, and teams that only
count one side make bad tuning decisions:

- **Cost of a false positive left unfixed in a blocking gate**: developer time lost re-triaging the
  same non-issue on every PR, and — the larger cost — erosion of trust in the gate itself. Once
  engineers learn "the scanner cries wolf," they start reflexively dismissing real findings too.
  A false-positive rate above roughly 30% is the empirical point (see
  [references/sast-integration.md](sast-integration.md) Metrics) where teams start requesting the
  gate be turned off entirely, which is a worse outcome than the false positives themselves.
- **Cost of a false negative (missed true positive)**: the vulnerability ships. This cost is
  usually invisible until an incident makes it visible, which is exactly why teams under-weight it
  relative to the very visible, very annoying false-positive cost.
- **The tuning lever**: every rule/policy change trades one cost for the other. Loosening a rule
  to cut false positives raises false-negative risk; tightening raises developer friction. There is
  no zero-cost setting — treat rule tuning as an explicit risk-appetite decision made by security
  and engineering leads together, not as a unilateral "just turn off the noisy rule" ticket.
- **Cheapest lever, in order**: (1) exclude known-safe patterns with documented suppressions before
  (2) lowering severity thresholds before (3) disabling a rule/category outright. Disabling loses
  all future detections in that category, not just the noisy historical ones.
