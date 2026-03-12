# Dependency Audit Checklist

Use this checklist when auditing project dependencies for security, maintainability, and optimization.

## Pre-Audit Information Gathering

- [ ] **Document current state**
  ```bash
  # Node.js
  npm ls --depth=0 > dependencies-snapshot.txt
  npm outdated > outdated.txt
  npm audit > audit-report.txt

  # Python
  pip list > requirements-current.txt
  poetry show --outdated > outdated.txt
  pip-audit > audit-report.txt

  # Rust
  cargo tree --depth=1 > dependencies-snapshot.txt
  cargo outdated > outdated.txt
  cargo audit > audit-report.txt
  ```

- [ ] **Identify direct vs transitive dependencies**
  - Direct: Listed in package.json/pyproject.toml/Cargo.toml
  - Transitive: Dependencies of dependencies

- [ ] **Check lockfile status**
  - [ ] Lockfile exists and committed to git
  - [ ] Lockfile is in sync with package manifest
  - [ ] No merge conflicts in lockfile

## Security Audit

### Vulnerability Scanning

- [ ] **Run automated security audit**
  ```bash
  # Node.js
  npm audit --audit-level=moderate

  # Python
  pip-audit
  # or
  safety check

  # Rust
  cargo audit
  ```

- [ ] **Review vulnerability report**
  - [ ] Note severity levels (critical, high, moderate, low)
  - [ ] Identify affected dependencies
  - [ ] Check if fixes are available
  - [ ] Document any accepted risks

- [ ] **Check for known supply chain attacks**
  - [ ] Review package maintainer changes
  - [ ] Check for suspicious package names (typosquatting)
  - [ ] Verify package integrity (checksums, signatures)

### Automated Security Tools

- [ ] **Enable Dependabot/Renovate**
  - [ ] Configure `.github/dependabot.yml`
  - [ ] Set up auto-merge for patch updates (optional)
  - [ ] Configure security alerts

- [ ] **Snyk integration** (if applicable)
  - [ ] Connect repository to Snyk
  - [ ] Review Snyk security reports
  - [ ] Set up CI integration

- [ ] **GitHub Advanced Security** (if available)
  - [ ] Enable dependency graph
  - [ ] Enable Dependabot alerts
  - [ ] Enable code scanning

## Maintenance Audit

### Dependency Health

- [ ] **Check last update dates**
  ```bash
  # Node.js
  npm info <package> time

  # Python
  poetry show <package>

  # Rust
  cargo search <package>
  ```

- [ ] **Evaluate maintenance status**
  - [ ] Last commit within 6 months? ([OK] Active)
  - [ ] Last commit 6-12 months ago? ([WARNING] Slow)
  - [ ] Last commit 12+ months ago? ([FAIL] Stale)

- [ ] **Check issue/PR activity**
  - [ ] Open issues being addressed?
  - [ ] Pull requests being reviewed?
  - [ ] Responsive maintainers?

- [ ] **Evaluate popularity**
  - [ ] Weekly downloads >10k? ([OK] Widely used)
  - [ ] Weekly downloads 1k-10k? ([WARNING] Moderate)
  - [ ] Weekly downloads <1k? ([FAIL] Low adoption)

### Dependency Tree Analysis

- [ ] **Identify large dependency trees**
  ```bash
  # Node.js
  npm ls <package>

  # Python
  pipdeptree -p <package>

  # Rust
  cargo tree -p <package>
  ```

- [ ] **Look for duplicate dependencies**
  ```bash
  # Node.js
  npm dedupe

  # Check for multiple versions
  npm ls <package> --depth=999
  ```

- [ ] **Check for circular dependencies**

### License Compliance

- [ ] **Review licenses**
  ```bash
  # Node.js
  npm install -g license-checker
  license-checker --summary

  # Python
  pip install pip-licenses
  pip-licenses

  # Rust
  cargo install cargo-license
  cargo license
  ```

- [ ] **Verify license compatibility**
  - [ ] MIT, Apache 2.0, BSD: [OK] Permissive
  - [ ] GPL, AGPL: [WARNING] Copyleft (check if compatible)
  - [ ] Proprietary: [FAIL] Review terms carefully

## Optimization Audit

### Bundle Size Analysis (Frontend)

- [ ] **Measure bundle impact**
  ```bash
  # Check individual package size
  # Visit: https://bundlephobia.com/package/<package>@<version>

  # Or use CLI
  npm install -g bundlephobia
  bundlephobia <package>
  ```

- [ ] **Identify heavy dependencies**
  - [ ] Note packages >100kb
  - [ ] Check if tree-shaking is supported
  - [ ] Consider lighter alternatives

### Unused Dependencies

- [ ] **Find unused dependencies**
  ```bash
  # Node.js
  npm install -g depcheck
  depcheck

  # Python
  pip install pipreqs
  pipreqs --print
  ```

- [ ] **Remove unused dependencies**
  ```bash
  # Node.js
  npm uninstall <package>

  # Python
  poetry remove <package>

  # Rust
  cargo remove <package>
  ```

### Version Constraint Review

- [ ] **Review version constraints**
  - [ ] Too loose (`*`, `>=1.0.0`): [FAIL] Unpredictable
  - [ ] Caret (`^1.2.3`): [OK] Recommended
  - [ ] Tilde (`~1.2.3`): [OK] Conservative
  - [ ] Exact (`1.2.3`): [WARNING] Use for critical deps only

## Update Strategy

### Safe Update Process

- [ ] **Update patch versions first**
  ```bash
  # Node.js
  npm update

  # Python
  poetry update

  # Rust
  cargo update
  ```

- [ ] **Test after updates**
  - [ ] Run test suite
  - [ ] Manual smoke testing
  - [ ] Check for deprecation warnings

- [ ] **Update minor versions**
  ```bash
  # Node.js (interactive)
  npm install -g npm-check-updates
  ncu -i --target minor

  # Python
  poetry update --with dev
  ```

- [ ] **Update major versions cautiously**
  - [ ] Read CHANGELOG and migration guides
  - [ ] Update one major dependency at a time
  - [ ] Test thoroughly
  - [ ] Create rollback plan

### Update Documentation

- [ ] **Document changes**
  - [ ] Update CHANGELOG.md
  - [ ] Note breaking changes
  - [ ] Document any required code changes

- [ ] **Commit with clear message**
  ```bash
  git add package.json package-lock.json
  git commit -m "chore: update dependencies (axios 0.27 -> 1.0)"
  ```

## Monorepo-Specific Checks

### Workspace Dependencies

- [ ] **Check workspace dependency versions**
  - [ ] Ensure consistent versions across workspaces
  - [ ] Hoist shared dependencies to root
  - [ ] Use workspace protocol for internal packages

- [ ] **Review workspace configuration**
  ```bash
  # pnpm
  cat pnpm-workspace.yaml

  # npm
  cat package.json | jq '.workspaces'

  # yarn
  cat package.json | jq '.workspaces'
  ```

## Final Review

### Summary Report

- [ ] **Create audit summary**
  - Total dependencies (direct + transitive)
  - Critical vulnerabilities found and status
  - Outdated dependencies count
  - Unused dependencies removed
  - Bundle size changes (if applicable)
  - Recommended actions

- [ ] **Prioritize actions**
  - [RED] Critical: Security vulnerabilities, broken dependencies
  - [YELLOW] Important: Outdated deps, maintenance issues
  - [GREEN] Nice-to-have: Bundle size optimization, minor updates

### Next Steps

- [ ] **Schedule regular audits**
  - [ ] Monthly for production apps
  - [ ] Quarterly for internal tools
  - [ ] Before major releases

- [ ] **Set up automation**
  - [ ] Enable Dependabot/Renovate
  - [ ] Add audit script to CI/CD
  - [ ] Configure automated security alerts

---

## Quick Commands Reference

### Node.js (npm)
```bash
npm audit                 # Security audit
npm audit fix            # Auto-fix vulnerabilities
npm outdated             # Check outdated packages
npm ls --depth=0         # List direct dependencies
npm update               # Update to latest within constraints
```

### Python (Poetry)
```bash
poetry show --outdated   # Check outdated packages
poetry update            # Update dependencies
pip-audit                # Security audit
pipdeptree               # Show dependency tree
```

### Rust (Cargo)
```bash
cargo audit              # Security audit
cargo outdated           # Check outdated packages
cargo update             # Update dependencies
cargo tree               # Show dependency tree
```

---

**Audit Frequency Recommendations:**
- **Production apps**: Monthly
- **Internal tools**: Quarterly
- **Libraries**: Before each release
- **Security patches**: Immediately when notified
