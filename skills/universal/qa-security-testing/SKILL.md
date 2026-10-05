---
name: qa-security-testing
description: "Builds automated security testing pipelines for SAST, DAST, SCA, secret scanning, and containers. Use when integrating scanners into CI or managing security regression gates."
compatibility: Portable core. Works on Claude Code and Codex.
version: "1.3"
last_validated: 2026-07-11
---

# QA Security Testing

Automated security testing pipelines that integrate scanners into CI/CD, enforce vulnerability gates, and drive findings through remediation. This skill covers the testing automation side of security; for secure design, threat modeling, and architecture review, use [software-security-appsec](../software-security-appsec/SKILL.md).

## Quick Start

1. Identify the authorized targets, allowed scan modes, and attack surfaces from the threat model.
2. Select tools per category (SAST, SCA, DAST, secrets, container/IaC).
3. Integrate into CI with clear gate policies per stage.
4. Establish a triage workflow: confirm, classify, assign, track.
5. Define vulnerability SLAs as a starting policy, then tune them to exploitability, business impact, and compliance obligations.
6. Add security regression tests for every confirmed vulnerability.

## Inputs to Gather

- Application type: web app, API, mobile, CLI, infrastructure.
- Languages, frameworks, and build toolchain.
- Deployment model: containers, serverless, VMs, PaaS.
- Current security tooling and CI platform.
- Compliance requirements: SOC 2, PCI DSS, HIPAA, ISO 27001 if applicable.
- Existing vulnerability management process and acceptable risk thresholds.
- Code hosting platform: GitHub, GitLab, Bitbucket (affects native tool availability).

## Security Testing Categories

### 1. SAST (Static Application Security Testing)

Analyze source code for vulnerabilities without executing it.

- **Recommended tools**: Semgrep (customizable rules), CodeQL (deep dataflow analysis, GitHub-native), Snyk Code.
- **CI pattern**: run on every PR; a common starter is block merge on high/critical findings, then tune to your risk policy.
- **Key practices**: maintain custom rules for your codebase patterns, manage suppressions with documented reasons, use baseline files to avoid noise from pre-existing findings.
- **Reference**: [references/sast-integration.md](references/sast-integration.md)

### 2. SCA / Dependency Scanning

Detect known vulnerabilities in direct and transitive dependencies.

- **Recommended tools**: Dependabot alerts (enable for the repository; default-branch monitoring), Snyk Open Source, Renovate + `npm audit` / `pip-audit`, Trivy fs mode.
- **Vulnerability SLAs**: the bundled tracker has an example policy, not a compliance standard. Set due dates from the approved policy and exploitability, asset value, and compensating controls.
- **Key practices**: use dependency review or a lockfile audit for PR changes; Dependabot alerts monitor the default branch ([GitHub docs](https://docs.github.com/en/code-security/concepts/supply-chain-security/dependabot-alerts)). Generate SBOMs (CycloneDX or SPDX) and track transitive risk.
- **Reference**: [references/dependency-scanning.md](references/dependency-scanning.md)

### 3. DAST (Dynamic Application Security Testing)

Test the running application for vulnerabilities by sending crafted requests.

- **Recommended tools**: ZAP (open source, automation framework), Nuclei (template-based, fast), Burp Suite (manual + CI plugin).
- **CI pattern**: use a bounded passive baseline on PR previews when available ([ZAP baseline docs](https://www.zaproxy.org/docs/docker/baseline-scan/)); run authenticated active scans against approved staging targets with a time budget. Schedule broader scans by release risk.
- **Key practices**: configure authenticated scanning, maintain baselines for known findings, scan APIs with OpenAPI specs.
- **Reference**: [references/dast-automation.md](references/dast-automation.md)

### 4. Secret Scanning

Detect credentials, tokens, and keys committed to source code.

- **Recommended tools**: gitleaks (pre-commit + CI), TruffleHog (entropy + regex), GitHub secret scanning (push protection).
- **CI pattern**: hard fail on any active credential or secret material. False positives and documented test fixtures still need an explicit suppression workflow.
- **Key practices**: install pre-commit hooks to catch secrets before push, scan full git history for historical leaks, rotate exposed secrets immediately (removal from code is not sufficient).
- **Reference**: [references/secret-scanning.md](references/secret-scanning.md)

### 5. Container and IaC Scanning

Scan container images and infrastructure-as-code for misconfigurations and CVEs.

- **Recommended tools**: Trivy (containers + IaC + SBOM, single tool), Checkov (Terraform, CloudFormation, Kubernetes). Before selecting a scanner, check its official support matrix and maintenance guidance in [data/sources.json](data/sources.json) for the target formats and migration requirements.
- **CI pattern**: scan on image build; a common starter is block on critical CVEs. Scan IaC on every PR with thresholds matched to environment risk.
- **Key practices**: enforce base image policy (approved images only), scan registry images on schedule, use multi-stage builds to reduce attack surface.
- **Reference**: [references/container-iac-scanning.md](references/container-iac-scanning.md)

### 6. Security Regression Testing

Write test cases that prevent reintroduction of fixed vulnerabilities.

- **Key areas**: auth boundary tests (IDOR, privilege escalation), input validation suites, CORS/CSP/security header verification, business logic abuse cases.
- **CI pattern**: include in standard test suites, run on every PR like functional tests.
- **Reference**: [references/security-regression-testing.md](references/security-regression-testing.md)

## Quick Reference

Treat gate thresholds as organization policy, not universal defaults. Severity alone is not enough; combine scanner severity with exploitability, reachability, asset sensitivity, and business impact.

| Stage | Tools | Gate Policy |
|-------|-------|-------------|
| Pre-merge (every PR) | SAST + secret scanning + dependency audit | Common starter: block on high/critical SAST, active secrets, and critical/high exploitable CVEs |
| Pre-deploy (staging) | DAST on staging + container scan | Common starter: block on high/critical confirmed DAST findings and critical container CVEs |
| Scheduled (weekly) | Full DAST scan, dependency review, registry scan | Findings feed into triage backlog |
| Release | All gates green + SLA compliance check | Block release when open findings violate the org's release policy or SLA commitments |

## Vulnerability Management Workflow

1. **Triage**: confirm finding is real, classify severity **and exploitability**. Severity (CVSS)
   alone is not triage. A CISA KEV listing (confirmed exploitation) overrides the CVSS band; EPSS
   is only a 30-day exploitation probability; reachability says whether your build can hit the
   path. Read the CVE record and current [NVD enrichment status](https://nvd.nist.gov/general/news)
   when selecting CVSS provenance; missing NVD enrichment does not mean no vulnerability. See
   [references/owasp-top-10-coverage.md § Triage: Severity vs. Exploitability vs.
   Reachability](references/owasp-top-10-coverage.md#triage-severity-vs-exploitability-vs-reachability)
   for the full model and worked rules of thumb.
2. **Track**: record in issue tracker with severity, KEV/EPSS/reachability context, SLA deadline, and remediation plan.
3. **Remediate**: keep `scanner finding`, `triaged vulnerability`, `local remediation`, and `verified deployed fix` as separate states. Apply the organization's closure policy to the finding class. Where a safe, stable behavioral oracle exists, show it failing on the vulnerable revision or fixture and passing on the fix. For dependency, configuration, or secret findings, fixed inventory, effective configuration, or rotation/revocation evidence plus a clean scoped rescan can verify local remediation; record any coverage limits. When deployment is relevant, track it separately by proving the affected artifact or environment contains the fix, unless policy explicitly makes deployment a closure requirement.
4. **Suppress**: if false positive, document reason and reviewer. Review suppressions quarterly — see
   [references/owasp-top-10-coverage.md § False-Positive Economics](references/owasp-top-10-coverage.md#false-positive-economics)
   for why unmanaged false positives cost more than the noise itself.
5. **Measure**: track mean time to remediate, open vulnerability count by severity, scan coverage percentage. Preserve scanner version/ruleset, artifact digest or commit, target environment, test case, and suppression reviewer; a clean rescan alone can miss changed reachability or an unscanned deployed artifact.
6. **Escalate to human testing when scanners cannot see the risk**: business-logic abuse, exploit
   chains across multiple low-severity findings, and freshly re-architected surfaces need a pen-test
   or red-team engagement, not another scanner run — see [references/owasp-top-10-coverage.md § When
   Pen-Testing Beats Scanning](references/owasp-top-10-coverage.md#when-pen-testing-beats-scanning).

## Decision Tree

```text
Starting security testing pipeline:
    │
    ├─ New project, no security tooling?
    │   └─ Start with: SAST (Semgrep) + secret scanning (gitleaks) + SCA (Dependabot)
    │
    ├─ Have SAST/SCA, need runtime testing?
    │   └─ Add DAST: ZAP on staging + Nuclei for targeted templates
    │
    ├─ Running containers?
    │   └─ Add Trivy for image scanning + base image policy
    │
    ├─ Using Terraform/CloudFormation/Kubernetes?
    │   └─ Add Checkov or Trivy IaC scanning on every PR
    │
    ├─ Compliance requirement (SOC 2, PCI, HIPAA)?
    │   └─ Full pipeline + SBOM generation + evidence retention + SLA tracking
    │
    └─ Past security incidents?
        └─ Write regression tests for each, add to standard test suite
```

## Scripts

| Script | Purpose |
|--------|---------|
| [scripts/vuln_tracker.py](scripts/vuln_tracker.py) | Vulnerability tracker and illustrative posture scorer |
| [scripts/test_vuln_tracker.py](scripts/test_vuln_tracker.py) | Offline regression tests for malformed exports and absent coverage |

Run from the `qa-security-testing/` directory. Inputs must explicitly list `vulnerabilities`; each finding needs a unique nonempty `id`, `title`, lowercase severity (`critical`, `high`, `medium`, `low`) and status (`open`, `in_progress`, `resolved`). Open findings require a `due_date` in `YYYY-MM-DD` format. Malformed statuses, numeric triage values, and scanner mappings exit nonzero before producing results. Coverage requires a scanner inventory plus at least one named surface, with boolean flags keyed by registered scanners. An empty scanner inventory represents coverage gaps.

Report recommendations use each finding's recorded due date rather than substituting bundled SLA defaults. Posture scores are illustrative policy arithmetic, not evidence of security effectiveness. `status` and reports without `--coverage` label the score unavailable; declared scanner assignments do not prove the scanner ran or detected a risk.

```bash
# Counts by severity, SLA rate and overdue items; score unavailable without coverage
python scripts/vuln_tracker.py status --input data/sample-vulnerabilities.json
```

```bash
# SLA compliance check: list overdue items with days overdue
python scripts/vuln_tracker.py sla --input data/sample-vulnerabilities.json
# Fix order: KEV > EPSS >= 0.7 (+reachable) > CVSS; unreachable is tracked, never auto-closed
python scripts/vuln_tracker.py triage --input data/sample-vulnerabilities.json
```

```bash
# Scanner coverage across attack surfaces: flag gaps
python scripts/vuln_tracker.py coverage --input data/sample-scan-coverage.json
```

```bash
# Full Markdown security testing report
python scripts/vuln_tracker.py report \
  --input data/sample-vulnerabilities.json \
  --coverage data/sample-scan-coverage.json \
  --output report.md
```

Run offline checks with `python3 -m unittest discover -s scripts -p "test_vuln_tracker.py"`. To test an alternate tracker revision, set `VULN_TRACKER_SCRIPT` to its path; pytest discovery uses the same selector.

## Resources

| Resource | Purpose |
|----------|---------|
| [references/sast-integration.md](references/sast-integration.md) | Semgrep and CodeQL setup, custom rules, CI integration |
| [references/dast-automation.md](references/dast-automation.md) | ZAP (by Checkmarx) and Nuclei automation, authenticated scanning |
| [references/dependency-scanning.md](references/dependency-scanning.md) | SCA tools, vulnerability SLAs, SBOM generation |
| [references/secret-scanning.md](references/secret-scanning.md) | gitleaks setup, pre-commit hooks, remediation workflow |
| [references/container-iac-scanning.md](references/container-iac-scanning.md) | Trivy and Checkov for containers and IaC |
| [references/security-regression-testing.md](references/security-regression-testing.md) | Writing security test cases for past vulnerabilities |
| [references/supply-chain-security.md](references/supply-chain-security.md) | Supply-chain verification gates: signature, provenance and SBOM checks, `actions/attest`, npm/PyPI provenance (SLSA/signing setup lives in ops-devops-platform) |
| [references/owasp-top-10-coverage.md](references/owasp-top-10-coverage.md) | CI scanner mapping for OWASP API Top 10 (2023), OWASP LLM Top 10 v2 (2025), OWASP Top 10 for Agentic Applications (2026, ASI01-10), and OWASP Top 10:2025; notes on ASVS 5.0; plus the severity/exploitability/reachability triage model, keep-vs-downgrade rules for code findings, pen-test-vs-scanning judgment, and false-positive economics |
| [data/sources.json](data/sources.json) | Curated external sources and documentation links |
| [data/sample-vulnerabilities.json](data/sample-vulnerabilities.json) | Sample B2B SaaS vulnerability list for vuln_tracker.py |
| [data/sample-scan-coverage.json](data/sample-scan-coverage.json) | Sample scanner coverage map for vuln_tracker.py |

## Templates

| Template | Purpose |
|----------|---------|
| [assets/template-security-test-plan.md](assets/template-security-test-plan.md) | Security testing scope, tool selection, and gate policy |
| [assets/template-security-gate-checklist.md](assets/template-security-gate-checklist.md) | Pre-merge, pre-deploy, and release gate checklist |
| [assets/template-vulnerability-sla.md](assets/template-vulnerability-sla.md) | Severity-based SLA table with escalation paths |

## Navigation

Load scanner references from the relevant testing category. Load [references/game-theory-applied.md](references/game-theory-applied.md) when choosing scan schedules, fuzz seeds, or repeated adversarial tests.

## Related Skills

| Skill | Purpose |
|-------|---------|
| [software-security-appsec](../software-security-appsec/SKILL.md) | Secure design, threat modeling, and security review |
| [qa-testing-strategy](../qa-testing-strategy/SKILL.md) | Risk-based test strategy |
| [qa-api-testing-contracts](../qa-api-testing-contracts/SKILL.md) | API contract and security testing |
| [ops-devops-platform](../ops-devops-platform/SKILL.md) | CI/CD pipeline design |
| [dev-dependency-management](../dev-dependency-management/SKILL.md) | Dependency management and update policy |
| [qa-resilience](../qa-resilience/SKILL.md) | Failure mode testing |

## Learnings Loop

When prior decisions or pitfalls are relevant, consult `learnings.consolidated.md` if present; use `learnings.md` only for needed history or as the available fallback. Otherwise skip both.

After applying it, if you encountered a pattern worth remembering, a mistake worth preventing, or a domain fact that surprised you, append one dated bullet to `learnings.md` via `agents-skills-feedback-loop/scripts/append_learning.py`. Do not modify `SKILL.md` itself.
