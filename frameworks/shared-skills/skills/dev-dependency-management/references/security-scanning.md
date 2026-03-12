# Dependency Security Scanning

Comprehensive guide to scanning dependencies for vulnerabilities and securing your software supply chain.

## Table of Contents

- [Why Security Scanning Matters](#why-security-scanning-matters)
- [Native Package Manager Audits](#native-package-manager-audits)
- [Automated Security Tools](#automated-security-tools)
- [CI/CD Integration](#cicd-integration)
- [Supply Chain Security](#supply-chain-security)
- [Incident Response](#incident-response)
- [Best Practices](#best-practices)

---

## Why Security Scanning Matters

**Real-world supply chain attacks:**
- **event-stream (2018):** Compromised npm package with 2M weekly downloads, injected code to steal Bitcoin wallets
- **ua-parser-js (2021):** Maintainer's account hijacked, malicious version published with cryptominer
- **Log4Shell (2021):** Critical RCE vulnerability affecting millions of Java applications
- **colors.js/faker.js (2022):** Maintainer intentionally sabotaged packages in protest
- **PyTorch (2023):** Malicious dependency uploaded to PyPI targeting Linux systems

**Impact:**
- Data breaches and credential theft
- Cryptominers and ransomware
- Remote code execution (RCE)
- Supply chain compromise
- Reputational damage

**Statistics:**
- 245,000+ malicious packages found on npm (2018-2024)
- 88% of organizations have at least one vulnerable dependency
- Average time to patch: 85 days

---

## Native Package Manager Audits

### npm audit

**Basic usage:**
```bash
# Run security audit
npm audit

# Show JSON output
npm audit --json

# Only show production dependencies
npm audit --production

# Set minimum severity level
npm audit --audit-level=moderate
```

**Output format:**
```
found 3 vulnerabilities (1 moderate, 2 high)
  run `npm audit fix` to fix 2 of them

  1 moderate severity vulnerability
  in lodash <4.17.21
  Dependency of: express
  Path: express > body-parser > lodash
  More info: https://github.com/advisories/GHSA-xxxx
```

**Auto-fixing vulnerabilities:**
```bash
# Fix vulnerabilities (safe updates only)
npm audit fix

# Force fix (may include breaking changes)
npm audit fix --force

# Dry run (preview changes without applying)
npm audit fix --dry-run
```

**Audit levels:**
- `info` - All vulnerabilities
- `low` - Low, moderate, high, critical
- `moderate` - Moderate, high, critical (recommended)
- `high` - High and critical only
- `critical` - Only critical vulnerabilities

**CI/CD integration:**
```bash
# Fail build if vulnerabilities found
npm audit --audit-level=moderate || exit 1
```

### pip-audit (Python)

**Installation:**
```bash
pip install pip-audit
```

**Usage:**
```bash
# Audit installed packages
pip-audit

# Audit requirements.txt
pip-audit -r requirements.txt

# Output as JSON
pip-audit --format=json

# Fix vulnerabilities
pip-audit --fix

# Set vulnerability database
pip-audit --vulnerability-service=osv
```

### cargo audit (Rust)

**Installation:**
```bash
cargo install cargo-audit
```

**Usage:**
```bash
# Audit dependencies
cargo audit

# Ignore specific advisories
cargo audit --ignore RUSTSEC-2020-0071

# JSON output
cargo audit --json

# Database update
cargo audit --update
```

### yarn audit

**Usage:**
```bash
# Run audit
yarn audit

# JSON format
yarn audit --json

# Set severity level
yarn audit --level moderate
```

---

## Automated Security Tools

### Dependabot (GitHub)

**Features:**
- Automated security updates via pull requests
- Version updates for dependencies
- Supports 15+ package ecosystems
- Native GitHub integration

**Configuration (`.github/dependabot.yml`):**
```yaml
version: 2
updates:
  - package-ecosystem: "npm"
    directory: "/"
    schedule:
      interval: "weekly"
    open-pull-requests-limit: 5
    labels:
      - "dependencies"
      - "security"
    reviewers:
      - "security-team"
    # Security updates only
    ignore:
      - dependency-name: "*"
        update-types: ["version-update:semver-major"]
```

**Enable Dependabot alerts:**
1. Go to repository Settings → Security & analysis
2. Enable "Dependabot alerts"
3. Enable "Dependabot security updates"

### Snyk

**Features:**
- Continuous security monitoring
- Fix pull requests
- License compliance
- Container vulnerability scanning
- IaC security scanning

**Installation:**
```bash
npm install -g snyk
snyk auth
```

**Usage:**
```bash
# Test project for vulnerabilities
snyk test

# Monitor project (continuous monitoring)
snyk monitor

# Fix vulnerabilities
snyk wizard

# Test container images
snyk container test node:18-alpine

# Test Kubernetes manifests
snyk iac test kubernetes.yaml
```

**CI/CD integration (GitHub Actions):**
```yaml
name: Snyk Security Scan

on: [push, pull_request]

jobs:
  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: snyk/actions/node@master
        env:
          SNYK_TOKEN: ${{ secrets.SNYK_TOKEN }}
        with:
          args: --severity-threshold=high
```

### GitHub Advanced Security

**Features:**
- Dependency graph
- Security advisories
- Code scanning (CodeQL)
- Secret scanning

**Enable:**
1. Settings → Security & analysis
2. Enable "Dependency graph"
3. Enable "Dependabot alerts"
4. Enable "Code scanning" (requires GitHub Advanced Security)

**CodeQL configuration (`.github/workflows/codeql.yml`):**
```yaml
name: CodeQL

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  analyze:
    runs-on: ubuntu-latest
    permissions:
      security-events: write
    steps:
      - uses: actions/checkout@v3
      - uses: github/codeql-action/init@v2
        with:
          languages: javascript
      - uses: github/codeql-action/autobuild@v2
      - uses: github/codeql-action/analyze@v2
```

### Socket.dev

**Features:**
- Supply chain attack detection
- Malicious package detection
- Real-time alerts
- Risk scoring

**Installation:**
```bash
npx socket-cli@latest
```

**Usage:**
```bash
# Analyze package.json
npx socket-cli report create --view

# CI integration
npx socket-cli report create --strict
```

### OWASP Dependency-Check

**Features:**
- Software composition analysis (SCA)
- CVE database scanning
- Supports Java, .NET, Ruby, Python, JavaScript

**Installation:**
```bash
# macOS
brew install dependency-check

# Manual download
wget https://github.com/jeremylong/DependencyCheck/releases/download/v8.0.0/dependency-check-8.0.0-release.zip
```

**Usage:**
```bash
# Scan project
dependency-check --project "My Project" --scan ./

# Generate HTML report
dependency-check --project "My Project" --scan ./ --format HTML

# Set suppression file
dependency-check --project "My Project" --scan ./ --suppression suppression.xml
```

---

## CI/CD Integration

### GitHub Actions

**Basic security workflow:**
```yaml
name: Security Audit

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]
  schedule:
    # Run weekly on Mondays at 9 AM
    - cron: '0 9 * * 1'

jobs:
  audit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - uses: actions/setup-node@v3
        with:
          node-version: '18'

      - name: Install dependencies
        run: npm ci

      - name: Run npm audit
        run: npm audit --audit-level=moderate

      - name: Check for outdated packages
        run: npm outdated || true

      - name: Generate SBOM
        run: npx @cyclonedx/cyclonedx-npm --output-file sbom.json

      - name: Upload SBOM
        uses: actions/upload-artifact@v3
        with:
          name: sbom
          path: sbom.json
```

**Advanced workflow with multiple tools:**
```yaml
name: Comprehensive Security Scan

on: [push, pull_request]

jobs:
  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3

      - name: Install dependencies
        run: npm ci

      # npm audit
      - name: npm audit
        run: npm audit --audit-level=moderate
        continue-on-error: true

      # Snyk
      - name: Snyk test
        uses: snyk/actions/node@master
        env:
          SNYK_TOKEN: ${{ secrets.SNYK_TOKEN }}
        with:
          args: --severity-threshold=high
        continue-on-error: true

      # Socket.dev
      - name: Socket.dev scan
        run: npx socket-cli@latest report create --strict
        continue-on-error: true

      # License compliance
      - name: License check
        run: npx license-checker --production --onlyAllow "MIT;Apache-2.0;BSD-2-Clause;BSD-3-Clause;ISC"

      # Upload results
      - name: Upload security reports
        uses: actions/upload-artifact@v3
        with:
          name: security-reports
          path: |
            npm-audit.json
            snyk-report.json
```

### GitLab CI

```yaml
security:
  stage: test
  image: node:18
  script:
    - npm ci
    - npm audit --audit-level=moderate
  allow_failure: false
```

### Jenkins

```groovy
pipeline {
  agent any
  stages {
    stage('Security Audit') {
      steps {
        sh 'npm ci'
        sh 'npm audit --audit-level=moderate'
      }
    }
  }
}
```

---

## Supply Chain Security

### SLSA Framework

**SLSA (Supply-chain Levels for Software Artifacts)** - Security framework for build integrity.

**SLSA Levels:**
- **Level 1:** Source provenance (basic)
- **Level 2:** Build service (tamper-proof build)
- **Level 3:** Hardened build platform
- **Level 4:** Two-party review (highest security)

**Implementing SLSA Level 1:**
```yaml
# GitHub Actions with SLSA provenance
name: Build with SLSA

on: push

jobs:
  build:
    permissions:
      id-token: write
      contents: write
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
      - run: npm ci
      - run: npm run build

      - uses: slsa-framework/slsa-github-generator@v1.6.0
        with:
          artifact-path: dist/
          provenance-name: provenance.intoto.jsonl
```

### SBOM (Software Bill of Materials)

**Generate SBOM:**
```bash
# CycloneDX (OWASP standard)
npx @cyclonedx/cyclonedx-npm --output-file sbom.json

# SPDX format
npm sbom --sbom-format=spdx

# Syft (multi-language)
syft packages . -o spdx-json > sbom.json
```

**SBOM formats:**
- **CycloneDX:** OWASP standard, JSON/XML
- **SPDX:** ISO/IEC standard, JSON/RDF/YAML
- **SWID:** ISO/IEC 19770-2

### npm Provenance

**Enable npm provenance:**
```bash
# Publish with provenance
npm publish --provenance
```

**Verify provenance:**
```bash
npm audit signatures
```

### Package Signing

**Verify package integrity:**
```bash
# npm (experimental)
npm audit signatures

# Sigstore (Rust, Python, containers)
cosign verify <image>
```

---

## Incident Response

### When a Vulnerability is Discovered

**1. Assess severity:**
- **Critical:** RCE, arbitrary code execution, data breach
- **High:** Privilege escalation, authentication bypass
- **Moderate:** XSS, CSRF, information disclosure
- **Low:** Denial of service, minor information leaks

**2. Check if vulnerability is exploitable:**
```bash
# Is the vulnerable function actually used?
grep -r "vulnerableFunction" src/

# Is the vulnerable dependency in production?
npm ls <vulnerable-package>
```

**3. Find a fix:**
```bash
# Check if patch exists
npm audit fix --dry-run

# Check for alternative packages
npm info <alternative-package>
```

**4. Apply fix:**
```bash
# Option 1: Automated fix
npm audit fix

# Option 2: Manual update
npm install <package>@latest

# Option 3: Use override/resolution
# package.json
{
  "overrides": {
    "lodash": "4.17.21"
  }
}
```

**5. Verify fix:**
```bash
npm audit
npm test
```

**6. Document:**
- Update CHANGELOG.md
- Security advisory (if public package)
- Internal incident report

### Vulnerability Disclosure Process

**If you discover a vulnerability:**

1. **Do NOT** open a public GitHub issue
2. Use GitHub Security Advisories
3. Contact maintainer privately
4. Allow 90 days for fix before public disclosure
5. Coordinate disclosure with maintainer

---

## Best Practices

### 1. Run Audits Regularly

```bash
# Weekly automated scans
npm audit --audit-level=moderate

# Before releases
npm audit --production
```

### 2. Enable Automated Tools

- [OK] Dependabot (free for GitHub)
- [OK] Snyk (free tier available)
- [OK] GitHub Advanced Security (if available)

### 3. Set Audit Thresholds

```json
// package.json
{
  "scripts": {
    "audit": "npm audit --audit-level=moderate",
    "audit:production": "npm audit --production --audit-level=high"
  }
}
```

### 4. Monitor Advisories

- Subscribe to GitHub Security Advisories
- Monitor CVE databases
- Follow security mailing lists

### 5. Use Lock Files

```bash
# Commit lockfiles to ensure reproducibility
git add package-lock.json
git commit -m "chore: update dependencies"
```

### 6. Minimize Dependencies

```bash
# Remove unused dependencies
npx depcheck

# Check bundle size impact
npx bundlephobia <package>
```

### 7. Vet New Dependencies

Before adding a dependency:
- Check weekly downloads
- Review GitHub activity
- Check security audit history
- Review open issues
- Check license compatibility

### 8. Use Private Registry for Internal Packages

```bash
# .npmrc
@myorg:registry=https://npm.pkg.github.com/
//npm.pkg.github.com/:_authToken=${GITHUB_TOKEN}
```

### 9. Implement Least Privilege

```bash
# Don't run npm install as root
# Use specific Node.js versions
nvm use 18
```

### 10. Generate and Store SBOMs

```bash
# Generate SBOM
npx @cyclonedx/cyclonedx-npm --output-file sbom.json

# Store with release artifacts
gh release create v1.0.0 dist/* sbom.json
```

---

## Severity Level Guidelines

| Severity | CVSS Score | Action | Timeline |
|----------|------------|--------|----------|
| **Critical** | 9.0-10.0 | Immediate patch | <24 hours |
| **High** | 7.0-8.9 | Prioritize fix | <1 week |
| **Moderate** | 4.0-6.9 | Schedule fix | <1 month |
| **Low** | 0.1-3.9 | Monitor | Next release |

---

## Resources

- [npm audit documentation](https://docs.npmjs.com/cli/v10/commands/npm-audit)
- [Snyk](https://snyk.io/)
- [Dependabot](https://github.com/dependabot)
- [OWASP Dependency-Check](https://owasp.org/www-project-dependency-check/)
- [SLSA Framework](https://slsa.dev/)
- [CycloneDX SBOM](https://cyclonedx.org/)
- [GitHub Security Advisories](https://docs.github.com/en/code-security/security-advisories)
- [CVE database](https://cve.mitre.org/)
- [National Vulnerability Database (NVD)](https://nvd.nist.gov/)