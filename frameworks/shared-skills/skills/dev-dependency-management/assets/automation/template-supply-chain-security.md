# Supply Chain Security & SBOM Guide

Production-grade dependency security covering SBOM generation, provenance, signatures, and vulnerability management.

---

## Software Bill of Materials (SBOM)

### SBOM Generation Checklist

- [ ] SBOM format selected (CycloneDX or SPDX)
- [ ] SBOM generation integrated in CI/CD
- [ ] SBOM stored with release artifacts
- [ ] SBOM includes transitive dependencies
- [ ] SBOM versioned with each release
- [ ] SBOM accessible for security audits

### SBOM Formats Comparison

| Format | Best For | Ecosystem | Spec |
|--------|----------|-----------|------|
| **CycloneDX** | Security, vulnerability tracking | OWASP | 1.5+ |
| **SPDX** | License compliance, legal | Linux Foundation | 2.3+ |

### SBOM Generation Commands

```bash
# Node.js (CycloneDX)
npx @cyclonedx/cyclonedx-npm --output-file sbom.json

# Python (CycloneDX)
pip install cyclonedx-bom
cyclonedx-py environment -o sbom.json

# Rust (CycloneDX)
cargo install cargo-cyclonedx
cargo cyclonedx -f json > sbom.json

# Go (CycloneDX)
go install github.com/CycloneDX/cyclonedx-gomod/cmd/cyclonedx-gomod@latest
cyclonedx-gomod mod -json -output sbom.json

# Universal (Syft - supports all ecosystems)
syft . -o cyclonedx-json > sbom.json
syft . -o spdx-json > sbom.spdx.json
```

### SBOM CI/CD Integration (GitHub Actions)

```yaml
name: Generate SBOM
on:
  release:
    types: [published]

jobs:
  sbom:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Generate SBOM with Syft
        uses: anchore/sbom-action@v0
        with:
          format: cyclonedx-json
          output-file: sbom.json

      - name: Upload SBOM to release
        uses: softprops/action-gh-release@v1
        with:
          files: sbom.json

      - name: Attest SBOM provenance
        uses: actions/attest-sbom@v1
        with:
          subject-path: ./dist/*
          sbom-path: sbom.json
```

---

## Provenance & Attestation

### SLSA Framework Levels

| Level | Requirements | Trust |
|-------|--------------|-------|
| **SLSA 1** | Documented build process | Low |
| **SLSA 2** | Version-controlled, hosted build | Medium |
| **SLSA 3** | Hardened build platform, signed provenance | High |
| **SLSA 4** | Hermetic, reproducible builds | Highest |

### Provenance Attestation (Sigstore)

```bash
# Sign artifact with Sigstore (keyless)
cosign sign-blob --yes artifact.tar.gz > artifact.sig

# Verify signature
cosign verify-blob --signature artifact.sig artifact.tar.gz

# Generate SLSA provenance
slsa-provenance generate \
  --artifact-path artifact.tar.gz \
  --output-path provenance.json
```

### npm Provenance (Native)

```bash
# Enable npm provenance (requires npm 9.5+)
npm publish --provenance

# Verify provenance
npm audit signatures
```

### GitHub Artifact Attestations

```yaml
- name: Generate artifact attestation
  uses: actions/attest-build-provenance@v1
  with:
    subject-path: ./dist/my-artifact.tar.gz
```

---

## Vulnerability Management

### Vulnerability Triage Checklist

- [ ] CVSS score assessed
- [ ] Exploitability determined (PoC exists?)
- [ ] Exposure assessed (public-facing? internal?)
- [ ] Fix available? What version?
- [ ] Breaking changes in fix version?
- [ ] Workaround available?
- [ ] Risk acceptance documented (if not fixing)

### Severity Response SLA

| Severity | CVSS | Response Time | Fix Deadline |
|----------|------|---------------|--------------|
| **Critical** | 9.0-10.0 | < 4 hours | < 24 hours |
| **High** | 7.0-8.9 | < 24 hours | < 7 days |
| **Medium** | 4.0-6.9 | < 72 hours | < 30 days |
| **Low** | 0.1-3.9 | Next sprint | < 90 days |

### Vulnerability Scanning Commands

```bash
# Node.js
npm audit
npm audit fix
npm audit --audit-level=high  # CI gate

# Python
pip-audit
pip-audit --fix

# Rust
cargo audit
cargo audit fix

# Go
govulncheck ./...

# Universal (Trivy)
trivy fs .
trivy image myapp:latest

# Grype (alternative to Trivy)
grype dir:.
grype myapp:latest
```

### CI/CD Vulnerability Gate

```yaml
name: Security Scan
on: [push, pull_request]

jobs:
  audit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Trivy vulnerability scan
        uses: aquasecurity/trivy-action@master
        with:
          scan-type: fs
          exit-code: 1
          severity: CRITICAL,HIGH

      - name: npm audit
        run: npm audit --audit-level=high
```

---

## Upgrade Playbook

### Upgrade Workflow

```text
1. Identify outdated packages
   └─ npm outdated / poetry show --outdated / cargo outdated

2. Categorize by risk
   ├─ Patch: Low risk, batch weekly
   ├─ Minor: Medium risk, test in staging
   └─ Major: High risk, dedicated sprint

3. Create upgrade branch
   └─ git checkout -b deps/upgrade-[package]-[version]

4. Update lockfile
   └─ npm install [package]@[version]

5. Run full test suite
   └─ npm test && npm run e2e

6. Deploy to staging (canary)
   └─ Monitor for 24h

7. Deploy to production
   └─ Staged rollout if critical path

8. Document in changelog
```

### Batching Strategy

| Update Type | Batch Size | Frequency | Review |
|-------------|------------|-----------|--------|
| Security patches | All | Immediate | Automated |
| Patch versions | Up to 10 | Weekly | Quick review |
| Minor versions | Up to 5 | Bi-weekly | Full review |
| Major versions | 1 at a time | Quarterly | Deep review |

### Rollback Procedure

```bash
# Git: Revert lockfile
git checkout HEAD~1 -- package-lock.json
npm ci

# Or: Pin to previous version
npm install [package]@[previous-version] --save-exact
```

---

## Pinning & Reproducibility

### Lockfile Requirements

| Ecosystem | Lockfile | Commit? | CI Command |
|-----------|----------|---------|------------|
| npm | `package-lock.json` | [OK] Yes | `npm ci` |
| pnpm | `pnpm-lock.yaml` | [OK] Yes | `pnpm install --frozen-lockfile` |
| Yarn | `yarn.lock` | [OK] Yes | `yarn install --immutable` |
| pip | `requirements.txt` + hashes | [OK] Yes | `pip install -r requirements.txt --require-hashes` |
| Poetry | `poetry.lock` | [OK] Yes | `poetry install --no-root` |
| Cargo | `Cargo.lock` | Apps: [OK], Libs: [FAIL] | `cargo build --locked` |
| Go | `go.sum` | [OK] Yes | `go build` (auto-verifies) |

### Hash Pinning (Python)

```txt
# requirements.txt with hashes
requests==2.31.0 \
    --hash=sha256:58cd2187c01e70e6e26505bca751777aa9f2ee0b7f4300988b709f44e013003f \
    --hash=sha256:942c5a758f98d790eaed1a29cb6eefc7ffb0d1cf7af05c3d2791656dbd6ad1e1
```

Generate hashes:
```bash
pip-compile --generate-hashes requirements.in
```

### Version Constraints Best Practices

```json
// package.json - Good
{
  "dependencies": {
    "express": "^4.18.2",        // Caret: patches + minors
    "lodash": "~4.17.21",        // Tilde: patches only
    "critical-lib": "1.2.3"      // Exact: no updates without review
  }
}

// Bad: Never use
{
  "dependencies": {
    "anything": "*",             // BAD: Wildcard
    "risky": ">=1.0.0",         // BAD: Unbounded
    "legacy": "latest"          // BAD: Floating tag
  }
}
```

---

## Do / Avoid

### GOOD: Do

- Generate SBOM for every release
- Sign release artifacts (Sigstore/cosign)
- Run vulnerability scans in CI/CD
- Fix critical vulnerabilities within 24 hours
- Document risk acceptance for deferred fixes
- Use lockfiles for reproducible builds
- Batch non-security updates by risk level
- Verify npm package provenance

### BAD: Avoid

- Publishing without SBOM
- Using unsigned packages in production
- Ignoring vulnerability scanner output
- Updating all dependencies at once
- Using wildcard version ranges
- Committing without updating lockfile
- Bypassing security gates "just this once"
- Trusting packages without provenance

---

## Anti-Patterns

| Anti-Pattern | Problem | Fix |
|--------------|---------|-----|
| **No SBOM** | Can't respond to supply chain attacks | Generate SBOM in CI/CD |
| **Unsigned artifacts** | Tampering undetectable | Sign with Sigstore |
| **Audit ignored** | Vulnerabilities ship to prod | Gate deployments on audit |
| **Floating versions** | Build not reproducible | Use lockfiles + exact versions |
| **All-at-once updates** | Hard to bisect regressions | Batch by risk level |
| **npm install in CI** | Non-deterministic | Use `npm ci` |

---

## Optional: AI/Automation

> **Note**: AI tools assist but require human judgment for security decisions.

### Automated Triage

- CVSS enrichment with exploitability context
- Auto-categorization of vulnerability severity
- PR description generation for security updates

### AI-Assisted Analysis

- Dependency changelog summarization
- Breaking change detection in major updates
- Risk scoring for transitive dependencies

### Bounded Claims

- AI cannot determine business risk acceptance
- Automated fixes require security team review
- Vulnerability severity context needs human validation

---

## Compliance Checklist

### For Regulated Industries

- [ ] SBOM meets NTIA minimum elements
- [ ] Vulnerability disclosure process documented
- [ ] Third-party risk assessment performed
- [ ] License compliance verified (SPDX)
- [ ] Supply chain security policy documented
- [ ] Incident response plan includes supply chain

### Regulatory References

- **US Executive Order 14028**: Requires SBOM for federal software
- **EU Cyber Resilience Act**: Mandates vulnerability handling
- **PCI DSS 4.0**: Third-party component inventory
- **NIST SP 800-218**: Secure software development

---

## Related Templates

- [audit-checklist.md](audit-checklist.md) — Security audit workflow
- [dependabot-config.yml](dependabot-config.yml) — Automated update PRs
- [renovate-config.json](renovate-config.json) — Renovate Bot setup

---

**Last Updated**: December 2025

---

## Sources

- [SLSA Framework](https://slsa.dev/) — Supply chain security levels
- [Sigstore](https://www.sigstore.dev/) — Keyless signing
- [CycloneDX](https://cyclonedx.org/) — SBOM standard
- [SPDX](https://spdx.dev/) — Software package data exchange
- [npm Provenance](https://docs.npmjs.com/generating-provenance-statements)
- [OpenSSF Scorecard](https://securityscorecards.dev/)
