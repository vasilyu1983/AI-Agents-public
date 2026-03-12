# Dependency Management Anti-Patterns

**When to Use**: Learn what NOT to do when managing dependencies to avoid common pitfalls.

---

## Overview

Anti-patterns are common practices that seem helpful but actually cause problems. This guide covers the most damaging dependency management anti-patterns and how to avoid them.

---

## Critical Anti-Patterns (NEVER Do These)

### 1. Not Committing Lockfiles

**BAD: Anti-Pattern:**

```bash
# .gitignore
package-lock.json  # BAD: DON'T IGNORE
pnpm-lock.yaml     # BAD: DON'T IGNORE
poetry.lock        # BAD: DON'T IGNORE
Cargo.lock         # BAD: DON'T IGNORE (for apps)
```

**Why it's bad:**
- Breaks reproducibility - different versions installed on different machines
- "Works on my machine" syndrome
- CI/production may get different versions than dev
- Hidden bugs from version mismatches
- Security vulnerabilities may appear unpredictably

**Real-world disaster:**

```
Developer: Uses axios@1.5.0 (no vulnerabilities)
CI: Installs axios@1.6.0 (has breaking change)
Production: Installs axios@1.4.0 (has CVE-2023-xxxxx)

Result: Production is vulnerable, CI tests don't catch it
```

**GOOD: Correct Approach:**

```bash
# Commit lockfiles
git add package-lock.json pnpm-lock.yaml poetry.lock Cargo.lock go.sum
git commit -m "chore: add lockfiles for reproducibility"
```

**Exception:** Don't commit `Cargo.lock` for Rust libraries (only for applications).

---

### 2. Using Wildcards (`*`) for Version Ranges

**BAD: Anti-Pattern:**

```json
{
  "dependencies": {
    "express": "*",
    "react": "*"
  }
}
```

**Why it's bad:**
- Completely unpredictable versions
- Breaking changes appear randomly
- No reproducibility even with lockfiles
- Production can break on any deploy
- Impossible to debug version-related issues

**Real-world disaster:**

```
Week 1: express@4.17.0 installed (works fine)
Week 2: express@5.0.0 released (breaking changes)
Week 3: New deploy pulls express@5.0.0
Result: Production crashes, team scrambles to fix
```

**GOOD: Correct Approach:**

```json
{
  "dependencies": {
    "express": "^4.18.0",  // Allows patches and minors, not majors
    "react": "~18.2.0"     // Allows only patches
  }
}
```

**When to use exact versions:**

```json
{
  "dependencies": {
    "critical-payment-lib": "1.2.3"  // Exact version for mission-critical
  }
}
```

---

### 3. Manual Lockfile Editing

**BAD: Anti-Pattern:**

```bash
# Manually editing package-lock.json
vim package-lock.json
# Change version numbers by hand
```

**Why it's bad:**
- Lockfile integrity broken
- Checksums won't match
- Installation will fail or reinstall wrong versions
- Package manager will overwrite your changes
- Corrupts dependency tree

**GOOD: Correct Approach:**

```bash
# Use package manager commands
npm install <package>@<version>
npm update
npm dedupe

# Let the package manager manage the lockfile
```

---

### 4. Ignoring Security Audits

**BAD: Anti-Pattern:**

```bash
$ npm audit
found 23 vulnerabilities (5 high, 18 moderate)

# Developer: "I'll fix it later"
# (Never fixes it)
```

**Why it's bad:**
- Known vulnerabilities exploited in production
- Data breaches, security incidents
- Compliance violations (SOC2, PCI-DSS)
- Legal liability
- Reputation damage

**Real-world disaster:**

```
Equifax breach (2017):
- Known vulnerability in Apache Struts
- Patch available for 2 months
- Never applied
- Result: 147 million records stolen, $700M+ in costs
```

**GOOD: Correct Approach:**

```bash
# Run audit regularly
npm audit

# Fix automatically (safe)
npm audit fix

# Review and fix manually (risky fixes)
npm audit fix --force

# Set up automated alerts
# Use Dependabot, Snyk, or GitHub Advanced Security
```

---

### 5. Adding Dependencies Without Review

**BAD: Anti-Pattern:**

```bash
# Developer sees a cool package on Twitter
npm install left-pad is-odd uppercase

# No review, no research, no questions
```

**Why it's bad:**
- Supply chain attacks (malicious packages)
- Dependency bloat (hundreds of transitive deps)
- Bundle size explosion
- Security vulnerabilities
- Unmaintained packages
- License violations

**Real-world disasters:**

```
event-stream (2018):
- Popular npm package compromised
- Malicious code injected by new maintainer
- Stole Bitcoin wallet credentials
- Downloaded 8M times per week

left-pad (2016):
- 11-line package unpublished
- Broke thousands of projects
- Highlighted fragility of npm ecosystem
```

**GOOD: Correct Approach:**

```bash
# Before adding ANY dependency:
1. Check last update (within 6 months?)
2. Check weekly downloads (>10k?)
3. Check GitHub issues (responsive maintainers?)
4. Check bundle size (bundlephobia.com)
5. Check dependency tree (npm ls <package>)
6. Check security (npm audit <package>)
7. Check license compatibility
8. Ask: Can I implement this in <100 LOC?

# Document decision
# Add to ADR (Architecture Decision Record)
```

---

## Dangerous Anti-Patterns (Avoid These)

### 6. Never Updating Dependencies

**BAD: Anti-Pattern:**

```bash
# Package.json from 2019
{
  "dependencies": {
    "express": "4.16.0",  // 5 years old
    "lodash": "4.17.11",  // Known vulnerabilities
    "moment": "2.24.0"    // Deprecated library
  }
}
```

**Why it's bad:**
- Technical debt accumulates
- Security vulnerabilities pile up
- Breaking changes pile up (harder to update later)
- Incompatibility with modern tools
- Loss of community support

**GOOD: Correct Approach:**

```bash
# Update regularly (monthly or quarterly)
npm outdated
npm update

# Or use automated tools
# Dependabot, Renovate
```

---

### 7. Using Deprecated Packages

**BAD: Anti-Pattern:**

```json
{
  "dependencies": {
    "request": "^2.88.0",      // Deprecated since 2020
    "moment": "^2.29.0",        // Maintenance mode
    "gulp": "^3.9.0",           // Use Gulp 4+
    "node-sass": "^4.14.0"      // Deprecated (use sass)
  }
}
```

**Why it's bad:**
- No security patches
- Incompatible with newer Node versions
- No bug fixes
- Community moves on
- Harder to hire developers familiar with old tools

**GOOD: Correct Approach:**

```json
{
  "dependencies": {
    "axios": "^1.6.0",           // Instead of request
    "date-fns": "^2.30.0",       // Instead of moment
    "gulp": "^4.0.2",            // Gulp 4+
    "sass": "^1.69.0"            // Instead of node-sass
  }
}
```

**Check deprecation status:**

```bash
npm outdated
npm view <package>
# Look for "DEPRECATED" warning
```

---

### 8. Mixing Package Managers

**BAD: Anti-Pattern:**

```bash
# Project has both
package-lock.json  # From npm
yarn.lock          # From yarn
pnpm-lock.yaml     # From pnpm

# Team uses different package managers
# Lockfiles conflict
```

**Why it's bad:**
- Conflicting lockfiles
- Inconsistent dependency resolution
- Different versions on different machines
- Merge conflicts in lockfiles
- Confusion for new team members

**GOOD: Correct Approach:**

```bash
# Choose ONE package manager
# Document in README.md
# Add to package.json

{
  "packageManager": "pnpm@8.0.0",
  "engines": {
    "npm": "please-use-pnpm",
    "yarn": "please-use-pnpm"
  }
}
```

---

### 9. Using `--force` or `--legacy-peer-deps` Without Understanding

**BAD: Anti-Pattern:**

```bash
# Error during npm install
$ npm install
npm ERR! peer dep missing: react@^18.0.0

# Developer: "I'll just force it"
$ npm install --force
# or
$ npm install --legacy-peer-deps
```

**Why it's bad:**
- Hides real problems
- May install incompatible versions
- Runtime errors in production
- Hard to debug later
- Breaks assumptions of libraries

**GOOD: Correct Approach:**

```bash
# Understand WHY the error occurred
npm ls react

# Fix the root cause
# Option 1: Update the dependency
npm update package-with-peer-dep

# Option 2: Install missing peer dependency
npm install react@^18.0.0

# Option 3: Use overrides (if necessary)
{
  "overrides": {
    "react": "18.2.0"
  }
}

# Document why (if using --legacy-peer-deps)
```

---

### 10. Not Using Virtual Environments (Python)

**BAD: Anti-Pattern:**

```bash
# Installing globally (Python)
sudo pip install flask
sudo pip install django

# System Python polluted
# Conflicts between projects
```

**Why it's bad:**
- Different projects need different versions
- System Python gets corrupted
- Permission issues
- Can't reproduce environments
- Hard to deploy

**GOOD: Correct Approach:**

```bash
# Use virtual environments
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Or use poetry
poetry install
```

---

## Moderate Anti-Patterns (Be Careful)

### 11. Overusing Overrides

**BAD: Anti-Pattern:**

```json
{
  "overrides": {
    "axios": "1.6.0",
    "lodash": "4.17.21",
    "express": "4.18.0",
    "react": "18.2.0",
    "typescript": "5.0.0",
    "webpack": "5.88.0",
    "...": "50 more overrides"
  }
}
```

**Why it's bad:**
- Hides real dependency issues
- May break packages that expect specific versions
- Hard to maintain
- Masks incompatibilities
- Makes debugging harder

**GOOD: Correct Approach:**

```json
{
  "overrides": {
    "axios": "1.6.0"  // Only 1-2 critical overrides
  }
}

// Document WHY in README:
// - axios override: CVE-2023-xxxxx fix
```

---

### 12. Ignoring Peer Dependency Warnings

**BAD: Anti-Pattern:**

```bash
$ npm install
npm WARN react-dom@18.2.0 requires a peer of react@^18.0.0
npm WARN react@17.0.0 is installed

# Developer: "It's just a warning, ignore it"
```

**Why it's bad:**
- Runtime errors in production
- Incompatible API usage
- Subtle bugs
- Undefined behavior

**GOOD: Correct Approach:**

```bash
# Install the correct peer dependency
npm install react@^18.0.0

# Or check if library supports your version
npm info react-dom peerDependencies
```

---

### 13. Committing `node_modules/`

**BAD: Anti-Pattern:**

```bash
# .gitignore missing node_modules/
git add node_modules/
git commit -m "add dependencies"
```

**Why it's bad:**
- Massive repo size (100MB+)
- Slow git operations
- Platform-specific binaries break
- Conflicts on every change
- Defeats purpose of package.json

**GOOD: Correct Approach:**

```bash
# .gitignore
node_modules/
venv/
__pycache__/
target/  # Rust
vendor/  # Go (usually)

# Commit lockfiles instead
git add package-lock.json
```

---

### 14. Using Development Dependencies in Production

**BAD: Anti-Pattern:**

```json
{
  "dependencies": {
    "express": "^4.18.0",
    "jest": "^29.0.0",        // BAD: Should be devDependency
    "eslint": "^8.0.0",       // BAD: Should be devDependency
    "typescript": "^5.0.0"    // BAD: Should be devDependency
  }
}
```

**Why it's bad:**
- Bloated production bundles
- Slower deployments
- Higher memory usage
- Security surface area increased

**GOOD: Correct Approach:**

```json
{
  "dependencies": {
    "express": "^4.18.0"
  },
  "devDependencies": {
    "jest": "^29.0.0",
    "eslint": "^8.0.0",
    "typescript": "^5.0.0"
  }
}
```

**Install production-only:**

```bash
npm install --production
# or
npm ci --production
```

---

## Checklist: Avoiding Anti-Patterns

**Before every dependency change:**

- [ ] [OK] Commit lockfiles
- [ ] [OK] Use semantic versioning (not wildcards)
- [ ] [OK] Use package manager commands (not manual edits)
- [ ] [OK] Run security audit
- [ ] [OK] Review dependency before adding
- [ ] [OK] Update dependencies regularly
- [ ] [OK] Avoid deprecated packages
- [ ] [OK] Use one package manager
- [ ] [OK] Understand `--force` before using
- [ ] [OK] Use virtual environments (Python)
- [ ] [OK] Minimize overrides
- [ ] [OK] Fix peer dependency warnings
- [ ] [OK] Never commit `node_modules/`
- [ ] [OK] Separate dev and prod dependencies

---

## Summary

**The Top 5 Most Damaging Anti-Patterns:**

1. **Not committing lockfiles** - Breaks reproducibility
2. **Using wildcards (`*`)** - Unpredictable versions
3. **Ignoring security audits** - Exploitable vulnerabilities
4. **Adding deps without review** - Supply chain attacks
5. **Never updating** - Technical debt accumulates

**Remember:** Dependency management requires discipline. Shortcuts today become disasters tomorrow.

---

## Quick Reference: What NOT To Do

| [FAIL] DON'T | [OK] DO |
|---------|-------|
| Ignore lockfiles | Commit lockfiles to git |
| Use wildcards (`*`) | Use semver ranges (`^`, `~`) |
| Edit lockfiles manually | Use package manager commands |
| Ignore `npm audit` | Fix vulnerabilities immediately |
| Add deps without review | Check bundle size, security, maintenance |
| Never update | Update monthly/quarterly |
| Use deprecated packages | Migrate to maintained alternatives |
| Mix package managers | Choose one, document in README |
| Use `--force` blindly | Understand and fix root cause |
| Skip virtual envs (Python) | Always use venv/poetry |
| Overuse overrides | Only 1-2 critical overrides |
| Ignore peer dep warnings | Install correct versions |
| Commit `node_modules/` | Add to `.gitignore` |
| Mix dev/prod deps | Separate into correct categories |

---

**Final Advice:** When in doubt, follow the principle of least surprise. If something seems hacky or fragile, it probably is. Do it the right way the first time.
