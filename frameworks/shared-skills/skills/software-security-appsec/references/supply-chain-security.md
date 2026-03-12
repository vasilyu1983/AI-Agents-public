# Supply Chain Security — Modern Best Practices (Jan 2026)

Comprehensive guide to software supply chain security focusing on dependency management, SBOM, trusted publishing, and protection against supply chain attacks.

---

## Overview

Supply chain risk is the risk that code you did not author (dependencies, build tooling, CI/CD, registries, container base images, artifact storage, CDNs) is compromised.

**OWASP Top 10:2025 (FINAL)** includes **A03: Software Supply Chain Failures** as a first-class category (elevated from "Vulnerable and Outdated Components").

---

## 2026 Updates

### CISA 2025 SBOM Minimum Elements

CISA released updated guidance on Software Bill of Materials (December 2025):

**Required SBOM Fields:**
- Supplier name
- Component name and version
- Unique identifier (PURL, CPE)
- Dependency relationship
- Author of SBOM data
- Timestamp

**Key Changes from 2021:**
- Machine-readable format required (SPDX 2.3+ or CycloneDX 1.4+)
- Vulnerability correlation (link to VEX)
- Continuous updates (not one-time deliverable)

### EU CRA (Cyber Resilience Act)

The EU CRA became law in 2025, making SBOMs mandatory for products sold in EU:
- Required for all products with digital elements
- Must be updated throughout product lifecycle
- Penalties for non-compliance

### AI-BOM (AI Bill of Materials)

For AI-native systems, traditional SBOMs don't capture full risk. AI-BOM includes:
- Models and model versions
- Training datasets and data provenance
- Embeddings and vector stores
- AI service dependencies (OpenAI, Anthropic, etc.)
- Orchestration frameworks (LangChain, LlamaIndex)

**EU AI Act** (effective August 2, 2025) requires transparency for GPAI models.

### Industry Adoption Status

- **48% of organizations** falling behind on SBOM requirements (Lineaje 2025 survey)
- Leading ecosystems integrating SBOMs natively into build tools
- SBOM now a cornerstone of modern software security

---

## OWASP Top 10:2025 - A03: Software Supply Chain Failures

**First-class category in 2025** (expanded from "Vulnerable and Outdated Components"):
- Dependency confusion attacks
- Malicious package injection
- Compromised maintainer accounts
- Build pipeline tampering
- Unsigned artifacts
- **Unknown vulnerabilities** from third-parties (new scope)

---

## Common Attack Vectors

- Typosquatting / brandjacking in package registries
- Dependency confusion (private package name collision)
- Compromised maintainer accounts and malicious releases
- Build pipeline compromise (CI tokens, runners, scripts)
- Artifact substitution (unsigned or unverified binaries/images)
- Compromised CDN/script injection
- Compromised transitive dependencies and postinstall scripts

### Reference Incidents (for training)

- CISA alert on the npm “Shai-Hulud” worm (2025-09-23): https://www.cisa.gov/news-events/alerts/2025/09/23/widespread-supply-chain-compromise-impacting-npm-ecosystem
- xz-utils backdoor disclosure (oss-security, 2024-03-29): https://www.openwall.com/lists/oss-security/2024/03/29/4

---

## Defense-in-Depth Strategy

### 1. Dependency Management

**Lock File Integrity**

```bash
# Generate lockfiles with integrity hashes
npm install --package-lock-only

# Verify lockfile hasn't been tampered with
npm ci --audit

# pnpm v10.16+ minimum release age protection
# pnpm-workspace.yaml
minReleaseAge: 1440  # 24 hours in minutes
```

**Dependency Pinning**

```json
{
  "dependencies": {
    "express": "4.18.2",        // Exact version, not ^4.18.2
    "lodash": "4.17.21",
    "react": "18.2.0"
  }
}
```

**Why pin versions:**
- Prevents automatic upgrades to compromised versions
- Allows time for community to detect malicious updates
- Enables controlled upgrade process with security review

**Automated Dependency Updates**

```yaml
# .github/dependabot.yml
version: 2
updates:
  - package-ecosystem: "npm"
    directory: "/"
    schedule:
      interval: "weekly"
    open-pull-requests-limit: 10
    reviewers:
      - "security-team"
    labels:
      - "dependencies"
      - "security"
    # Allow time for community vetting
    pull-request-branch-name:
      separator: "/"
```

---

### 2. Software Bill of Materials (SBOM)

**Generate SBOM**

```bash
# Using CycloneDX
npm install -g @cyclonedx/cyclonedx-npm
cyclonedx-npm --output-file sbom.json

# Using Syft
syft packages dir:. -o json > sbom.json

# Using npm native (npm 8+)
npm sbom --sbom-format=cyclonedx > sbom.json
```

**SBOM Benefits:**
- Complete inventory of dependencies
- Vulnerability tracking across supply chain
- License compliance validation
- Incident response acceleration

**Track SBOM Changes**

```bash
# Store SBOMs in version control
git add sbom.json

# Compare SBOMs between versions
diff sbom-v1.json sbom-v2.json
```

---

### 3. Trusted Publishing

**GitHub Actions + npm Trusted Publishing (July 2025)**

```yaml
# .github/workflows/publish.yml
name: Publish to npm
on:
  release:
    types: [published]

jobs:
  publish:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      id-token: write  # Required for trusted publishing
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
          registry-url: 'https://registry.npmjs.org'
      - run: npm ci
      - run: npm test
      - run: npm publish --provenance --access public
        env:
          NODE_AUTH_TOKEN: ${{ secrets.NPM_TOKEN }}
```

**Benefits:**
- No long-lived tokens in secrets
- Cryptographic proof of build origin
- Build transparency via SLSA provenance

**Verify Package Provenance**

```bash
# Check if package has provenance
npm view express dist.attestations

# Verify provenance
npm audit signatures
```

---

### 4. Authentication Security

**Phishing-Resistant MFA (Required by GitHub 2025)**

```bash
# Enable hardware security key (WebAuthn)
# GitHub Account Settings → Security → Two-factor authentication
# → Register new security key

# Backup codes
# Store in password manager or secure location
```

**Best Practices:**
- Use hardware security keys (YubiKey, Titan Key)
- Enable MFA on all developer accounts
- Avoid SMS-based 2FA (vulnerable to SIM swapping)
- Implement organization-wide MFA policies

---

### 5. Software Composition Analysis (SCA)

**Continuous Vulnerability Scanning**

```bash
# npm audit (built-in)
npm audit --audit-level=moderate

# Snyk
npm install -g snyk
snyk auth
snyk test
snyk monitor

# Trivy
trivy fs .

# Grype
grype dir:.
```

**CI/CD Integration**

```yaml
# GitHub Actions
- name: Run Snyk security scan
  uses: snyk/actions/node@master
  env:
    SNYK_TOKEN: ${{ secrets.SNYK_TOKEN }}
  with:
    command: test
    args: --severity-threshold=high
```

**Automated PR Blocking**

```yaml
# Block PRs with high/critical vulnerabilities
- name: Check vulnerabilities
  run: |
    npm audit --audit-level=high
    if [ $? -ne 0 ]; then
      echo "High/critical vulnerabilities found"
      exit 1
    fi
```

---

### 6. SLSA Framework

**Supply-chain Levels for Software Artifacts**

**SLSA Level 1**: Documentation of build process
**SLSA Level 2**: Tamper-resistant build service
**SLSA Level 3**: Hardened build platform with provenance
**SLSA Level 4**: Two-party review + hermetic builds

**Implement SLSA Level 3**

```yaml
# Use GitHub-hosted runners (trusted build environment)
jobs:
  build:
    runs-on: ubuntu-latest  # Isolated, ephemeral environment
    permissions:
      id-token: write       # Generate provenance
      contents: read
    steps:
      - uses: actions/checkout@v4
      - run: npm ci --ignore-scripts  # Prevent malicious install scripts
      - run: npm run build
      - uses: actions/attest-build-provenance@v1
        with:
          subject-path: 'dist/**'
```

---

### 7. Artifact Signing

**Sigstore - Keyless Signing**

```bash
# Install cosign
brew install cosign

# Sign artifact (keyless with OIDC)
cosign sign-blob --yes artifact.tar.gz > artifact.sig

# Verify signature
cosign verify-blob \
  --signature artifact.sig \
  --certificate-identity your-email@domain.com \
  --certificate-oidc-issuer https://github.com/login/oauth \
  artifact.tar.gz
```

**Docker Image Signing**

```bash
# Sign container image
cosign sign ghcr.io/org/image:v1.0.0

# Verify before deployment
cosign verify \
  --certificate-identity your-email@domain.com \
  --certificate-oidc-issuer https://github.com/login/oauth \
  ghcr.io/org/image:v1.0.0
```

---

### 8. Secure CI/CD Pipeline

**Principle: Least Privilege**

```yaml
# Minimal permissions
permissions:
  contents: read
  pull-requests: write

jobs:
  test:
    runs-on: ubuntu-latest
    # No write access to secrets or packages
    steps:
      - uses: actions/checkout@v4
      - run: npm ci
      - run: npm test
```

**Secrets Management**

```yaml
# Use environment-specific secrets
jobs:
  deploy:
    environment: production
    steps:
      - uses: actions/checkout@v4
      - run: |
          # Secrets scoped to environment
          echo "Deploying with ${{ secrets.PROD_API_KEY }}"
```

**Prevent Script Injection**

```bash
# Bad: Command injection vulnerability
git commit -m "${{ github.event.issue.title }}"

# Good: Use environment variables
export TITLE="${{ github.event.issue.title }}"
git commit -m "$TITLE"
```

---

### 9. Dependency Confusion Prevention

**Use Scoped Packages**

```json
{
  "name": "@myorg/my-package",
  "private": true
}
```

**Namespace Protection**

```bash
# Reserve namespace on public registry
npm org create myorg
```

**Private Registry Configuration**

```ini
# .npmrc
@myorg:registry=https://npm.internal.company.com/
//npm.internal.company.com/:_authToken=${NPM_TOKEN}

# Public packages still from public registry
registry=https://registry.npmjs.org/
```

---

### 10. Incident Response

**Detection**

```bash
# Check for compromised dependencies
npm audit

# Verify package integrity
npm ls --depth=0
npm ls --all | grep -i "suspicious"

# Check for unexpected network calls
strace -e trace=network npm install
```

**Response Playbook**

1. **Isolate**: Stop deployments, quarantine affected systems
2. **Identify**: Determine scope of compromise
3. **Remediate**: Remove malicious dependencies, rotate credentials
4. **Recover**: Deploy clean versions, verify integrity
5. **Report**: Notify stakeholders, report to npm/GitHub security

**SBOM-Driven Response**

```bash
# Check if your project uses compromised package
jq '.components[] | select(.name == "compromised-package")' sbom.json

# Find all affected projects
find . -name sbom.json -exec grep -l "compromised-package" {} \;
```

---

## Best Practices Checklist

**Authentication & Access**
- [ ] Phishing-resistant MFA enabled on all developer accounts
- [ ] Hardware security keys for critical accounts
- [ ] Organization-wide MFA policy enforced
- [ ] Periodic access reviews and key rotation

**Dependency Management**
- [ ] Exact version pinning (no semver ranges)
- [ ] pnpm minimumReleaseAge or equivalent delay
- [ ] Automated dependency updates with security review
- [ ] Regular `npm audit` and SCA scans

**Build Security**
- [ ] Trusted publishing implemented (npm, PyPI, RubyGems)
- [ ] SLSA Level 2+ provenance generation
- [ ] Artifact signing with Sigstore
- [ ] Hermetic builds with locked dependencies

**Monitoring & Detection**
- [ ] SBOM generation and tracking
- [ ] Continuous vulnerability scanning
- [ ] Real-time dependency monitoring
- [ ] Alerting on new vulnerabilities

**Incident Response**
- [ ] Documented supply chain incident response plan
- [ ] SBOM-driven impact analysis process
- [ ] Communication plan for stakeholders
- [ ] Regular incident response drills

---

## Tools Comparison

| Tool | Focus | Best For |
|------|-------|----------|
| **Dependabot** | Automated updates | GitHub native integration |
| **Snyk** | Vulnerability scanning | Developer-first workflows |
| **Trivy** | Container + code scanning | Multi-artifact scanning |
| **Grype** | Vulnerability detection | CLI-first, fast scanning |
| **Syft** | SBOM generation | Comprehensive inventory |
| **Sigstore** | Artifact signing | Keyless signing |
| **SLSA** | Build provenance | End-to-end attestation |

---

## References

- [OWASP Top 10:2025 - A03: Software Supply Chain Failures](https://owasp.org/Top10/2025/A03/)
- [GitHub's Plan for a More Secure npm Supply Chain](https://github.blog/security/supply-chain-security/our-plan-for-a-more-secure-npm-supply-chain/)
- [SLSA Framework](https://slsa.dev/)
- [Sigstore Documentation](https://docs.sigstore.dev/)
- [OpenSSF Best Practices](https://openssf.org/references/guides/)
- [CISA Supply Chain Compromise Alerts](https://www.cisa.gov/topics/supply-chain-security)
- [npm Security Best Practices](https://docs.npmjs.com/about-security-and-npm)
