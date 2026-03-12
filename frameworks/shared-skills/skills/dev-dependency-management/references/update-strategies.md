# Dependency Update Strategies

**When to Use**: Keeping dependencies up to date safely while minimizing breaking changes and security risks.

---

## Why Update Dependencies?

**Benefits:**
- Security patches for known vulnerabilities
- Bug fixes and stability improvements
- Performance improvements
- New features and capabilities
- Compatibility with newer ecosystems

**Risks if you DON'T update:**
- Accumulating technical debt
- Security vulnerabilities exploited
- Compatibility issues with new tools
- Harder to update later (breaking changes pile up)
- Loss of community support

---

## Update Strategies

### 1. Continuous Updates (Recommended for Libraries)

**What:** Update dependencies weekly or bi-weekly

**Best for:**
- Open source libraries
- npm packages
- Small teams with fast iteration

**Pros:**
- [OK] Small, manageable changes
- [OK] Catch breaking changes early
- [OK] Stay close to ecosystem
- [OK] Easier to debug issues

**Cons:**
- [FAIL] More frequent changes
- [FAIL] Requires good test coverage
- [FAIL] Can distract from feature work

**Setup:**

```yaml
# .github/dependabot.yml
version: 2
updates:
  - package-ecosystem: "npm"
    directory: "/"
    schedule:
      interval: "weekly"
      day: "monday"
      time: "09:00"
    open-pull-requests-limit: 10
    reviewers:
      - "dev-team"
```

### 2. Scheduled Updates (Recommended for Applications)

**What:** Update monthly or quarterly in dedicated sprints

**Best for:**
- Production applications
- Enterprise software
- Large teams with release cycles

**Pros:**
- [OK] Predictable change windows
- [OK] Batch updates together
- [OK] Thorough testing before deployment
- [OK] Coordinated with releases

**Cons:**
- [FAIL] Larger change sets
- [FAIL] More breaking changes at once
- [FAIL] Harder to isolate issues

**Setup:**

```yaml
# .github/dependabot.yml
version: 2
updates:
  - package-ecosystem: "npm"
    directory: "/"
    schedule:
      interval: "monthly"
      day: "monday"
    labels:
      - "dependencies"
      - "monthly-update"
```

**Update workflow:**

1. **Week 1**: Review available updates, plan batch
2. **Week 2**: Update dev dependencies, test
3. **Week 3**: Update production dependencies, test
4. **Week 4**: Deploy to staging, verify, deploy to prod

### 3. Security-Only Updates (Conservative)

**What:** Only update for security patches, skip feature updates

**Best for:**
- Legacy systems
- Risk-averse organizations
- Apps with limited test coverage

**Pros:**
- [OK] Minimal breaking changes
- [OK] Focuses on critical fixes
- [OK] Less testing overhead

**Cons:**
- [FAIL] Accumulates technical debt
- [FAIL] May miss important bug fixes
- [FAIL] Harder to update later

**Setup:**

```yaml
# .github/dependabot.yml
version: 2
updates:
  - package-ecosystem: "npm"
    directory: "/"
    schedule:
      interval: "weekly"
    open-pull-requests-limit: 5
    labels:
      - "security"
      - "priority-high"
    # Only open PRs for security updates
    assignees:
      - "security-team"
```

---

## Safe Update Workflow

### Step-by-Step Process

**1. Check for outdated dependencies:**

```bash
# Node.js
npm outdated
npm outdated --long  # Shows homepage, description

# Python
poetry show --outdated
pip list --outdated

# Rust
cargo outdated

# Go
go list -u -m all
```

**Example output:**

```bash
$ npm outdated
Package      Current  Wanted  Latest  Location
axios        0.27.2   0.27.2  1.6.0   node_modules/axios
typescript   4.9.5    4.9.5   5.3.2   node_modules/typescript
```

**2. Categorize updates by risk:**

| Update Type | Risk | Action |
|-------------|------|--------|
| Patch (1.0.0 → 1.0.1) | [GREEN] Low | Update immediately |
| Minor (1.0.0 → 1.1.0) | [YELLOW] Medium | Test thoroughly |
| Major (1.0.0 → 2.0.0) | [RED] High | Read CHANGELOG, plan migration |

**3. Update patch versions (safest):**

```bash
# Update to latest patch versions within constraints
npm update

# This respects your package.json constraints
# E.g., ^1.2.3 → updates to 1.2.x, not 1.3.0 or 2.0.0
```

**4. Update minor/major versions (carefully):**

```bash
# Update specific package to latest
npm install axios@latest

# Update to specific version
npm install typescript@5.3.2

# Update all to latest (DANGEROUS - use with caution)
npm install -g npm-check-updates
ncu -u
npm install
```

**5. Run tests:**

```bash
# Run full test suite
npm test

# Run E2E tests
npm run test:e2e

# Check for type errors (TypeScript)
npm run type-check

# Run linter
npm run lint
```

**6. Check for breaking changes:**

**Read changelogs:**

```bash
# View package changelog
npm info <package> homepage
# Click through to GitHub releases

# Search for breaking changes
npm info axios | grep -i "breaking"
```

**Common breaking change indicators:**

- Major version bump (1.x → 2.x)
- Removed APIs
- Changed function signatures
- New required parameters
- Dropped Node.js version support

**7. Test in staging:**

```bash
# Deploy to staging environment
npm run deploy:staging

# Run smoke tests
npm run test:smoke

# Manual QA on critical flows
```

**8. Commit with clear message:**

```bash
# Stage changes
git add package.json package-lock.json

# Descriptive commit message
git commit -m "chore(deps): update axios 0.27.2 → 1.6.0

- Fixes CVE-2023-45857
- Adds support for new timeout options
- BREAKING: Removed deprecated getUri method (not used in codebase)

Tested:
- All unit tests passing
- E2E tests verified
- Staging deployment successful"
```

**9. Monitor production:**

After deploying updates:

- Watch error tracking (Sentry, Rollbar)
- Monitor performance metrics
- Check logs for new errors
- Have rollback plan ready

---

## Automated Update Tools

### Dependabot (GitHub Native)

**Pros:**
- [OK] Free for GitHub repos
- [OK] Auto-creates PRs
- [OK] Security alerts integration
- [OK] Easy configuration

**Cons:**
- [FAIL] GitHub only
- [FAIL] Less configurable than Renovate
- [FAIL] Can create many PRs

**Configuration:**

```yaml
# .github/dependabot.yml
version: 2
updates:
  - package-ecosystem: "npm"
    directory: "/"
    schedule:
      interval: "weekly"
      day: "monday"
      time: "09:00"
    open-pull-requests-limit: 5
    reviewers:
      - "dev-team"
    assignees:
      - "lead-developer"
    labels:
      - "dependencies"
      - "auto-update"
    commit-message:
      prefix: "chore(deps)"
      include: "scope"
    # Grouping related updates
    groups:
      dev-dependencies:
        patterns:
          - "@types/*"
          - "eslint*"
          - "prettier"
```

### Renovate (Multi-Platform)

**Pros:**
- [OK] More configurable
- [OK] Supports all package managers
- [OK] Works with GitHub, GitLab, Bitbucket
- [OK] Automerge capabilities
- [OK] Smart grouping

**Cons:**
- [FAIL] More complex setup
- [FAIL] Requires separate service

**Configuration:**

```json
{
  "$schema": "https://docs.renovatebot.com/renovate-schema.json",
  "extends": ["config:base"],
  "schedule": ["after 9am on monday"],
  "packageRules": [
    {
      "matchUpdateTypes": ["patch"],
      "automerge": true,
      "automergeType": "branch"
    },
    {
      "matchUpdateTypes": ["minor"],
      "groupName": "minor updates",
      "automerge": false
    },
    {
      "matchUpdateTypes": ["major"],
      "enabled": false
    }
  ],
  "vulnerabilityAlerts": {
    "enabled": true,
    "labels": ["security"]
  }
}
```

### npm-check-updates (Manual)

**Pros:**
- [OK] Full control
- [OK] Interactive mode
- [OK] Works offline

**Cons:**
- [FAIL] Manual process
- [FAIL] No automation

**Usage:**

```bash
# Install globally
npm install -g npm-check-updates

# Check for updates
ncu

# Interactive update selection
ncu -i

# Update package.json (without installing)
ncu -u

# Update and install
ncu -u && npm install
```

---

## Update Strategies by Project Type

### Open Source Library

**Strategy:** Continuous updates

```yaml
# Aggressive update schedule
schedule:
  interval: "weekly"
automerge: true for patches
```

**Why:** Stay close to ecosystem, contributors expect modern dependencies

### Production SaaS Application

**Strategy:** Scheduled updates (monthly)

```yaml
# Conservative schedule
schedule:
  interval: "monthly"
automerge: false
```

**Why:** Stability critical, thorough testing required

### Enterprise Application

**Strategy:** Security-only + quarterly reviews

```yaml
# Security-focused
schedule:
  interval: "weekly"
vulnerabilityAlerts: true
open-pull-requests-limit: 3
```

**Why:** Risk-averse, extensive testing required

### Early-Stage Startup

**Strategy:** Continuous updates

```yaml
# Fast-paced updates
schedule:
  interval: "daily"
automerge: true for patches and minors
```

**Why:** Move fast, iterate quickly, smaller codebase

---

## Handling Breaking Changes

### Before Updating

**1. Read the CHANGELOG:**

```bash
# Find changelog
npm info <package> homepage
# Look for CHANGELOG.md, RELEASES.md, or GitHub releases
```

**2. Search for migration guides:**

```bash
# Google: "axios v1 migration guide"
# Check package docs: /docs/migration
# Look for "UPGRADING.md" or "MIGRATION.md"
```

**3. Check for codemods:**

Some libraries provide automated migration tools:

```bash
# Example: React 19 codemod
npx react-codemod update-react-imports
```

### After Updating

**1. Fix TypeScript errors:**

```bash
npm run type-check
# Fix type errors in your code
```

**2. Update deprecated API usage:**

```bash
# Find deprecated warnings
npm run build 2>&1 | grep -i "deprecated"

# Replace old APIs with new ones
```

**3. Run full test suite:**

```bash
npm test
npm run test:e2e
npm run test:integration
```

**4. Update documentation:**

```markdown
# Update README.md, CHANGELOG.md
## Dependencies Updated
- axios: 0.27.2 → 1.6.0 (BREAKING: removed getUri method)
```

---

## Rollback Plan

Always have a rollback strategy:

**1. Git rollback:**

```bash
# Revert commit
git revert HEAD

# Or reset to previous commit
git reset --hard HEAD~1

# Push rollback
git push --force-with-lease
```

**2. npm rollback:**

```bash
# Reinstall previous version
npm install axios@0.27.2

# Commit lockfile change
git add package-lock.json
git commit -m "chore(deps): rollback axios to 0.27.2"
```

**3. Docker rollback:**

```bash
# Deploy previous image tag
kubectl set image deployment/app app=myapp:v1.2.3

# Or rollback in Kubernetes
kubectl rollout undo deployment/app
```

---

## Best Practices

### DO:

- [OK] **Update frequently** - Small changes easier to manage
- [OK] **Read changelogs** - Understand what changed
- [OK] **Test thoroughly** - Especially E2E tests
- [OK] **Update in batches** - Group related dependencies
- [OK] **Monitor production** - Watch for errors after deploy
- [OK] **Document breaking changes** - Help future you
- [OK] **Use semantic versioning** - Understand what updates mean
- [OK] **Enable automated alerts** - Know when security issues arise

### DON'T:

- [FAIL] **Update all at once** - Risky, hard to debug
- [FAIL] **Skip reading changelogs** - May miss breaking changes
- [FAIL] **Blindly automerge** - At least for major updates
- [FAIL] **Ignore test failures** - Tests exist for a reason
- [FAIL] **Update without rollback plan** - Always have escape hatch
- [FAIL] **Use wildcards (`*`)** - Unpredictable updates
- [FAIL] **Skip staging deployment** - Test in production-like env first

---

## Checklist: Before Updating Dependencies

Use this checklist for EVERY dependency update:

**Preparation:**
- [ ] Check available updates (`npm outdated`)
- [ ] Categorize by risk (patch/minor/major)
- [ ] Read changelogs for major/minor updates
- [ ] Check for migration guides
- [ ] Review test coverage (>80%)

**Execution:**
- [ ] Update lockfile (`npm update` or `npm install <pkg>@latest`)
- [ ] Run full test suite
- [ ] Check for TypeScript errors
- [ ] Run linter
- [ ] Build project successfully

**Testing:**
- [ ] Deploy to staging
- [ ] Run smoke tests
- [ ] Manual QA on critical flows
- [ ] Check performance metrics
- [ ] Review error logs

**Deployment:**
- [ ] Commit with descriptive message
- [ ] Create PR with changelog summary
- [ ] Get code review
- [ ] Deploy to production
- [ ] Monitor error tracking
- [ ] Have rollback plan ready

---

## Summary

**The Update Workflow:**

```
Check updates → Categorize risk → Read changelogs → Update → Test → Stage → Deploy → Monitor
```

**Golden Rules:**

1. **Update frequently** - Small changes are manageable
2. **Test thoroughly** - Trust but verify
3. **Read changelogs** - Know what changed
4. **Have rollback plan** - Things go wrong
5. **Monitor production** - Catch issues early

**Remember:** Updates are essential for security and stability, but should be done deliberately, not automatically.
