# Branching Strategies - Comprehensive Comparison

Deep dive into modern Git branching strategies with decision frameworks, migration paths, and real-world examples.

## Contents

- Strategy Comparison Matrix
- GitHub Flow - Detailed Guide
- Trunk-Based Development - Detailed Guide
- GitFlow - Detailed Guide
- Migration Paths
- Team Size Recommendations
- Branching Strategy Checklist
- Anti-Patterns to Avoid
- Real-World Examples

---

## Strategy Comparison Matrix

### Feature Comparison

| Feature | GitHub Flow | Trunk-Based | GitFlow |
|---------|-------------|-------------|---------|
| **Complexity** | Low | Low-Medium | High |
| **Learning Curve** | Easy | Medium | Steep |
| **Branch Count** | 2-5 | 1-3 | 5-10+ |
| **Merge Frequency** | Multiple/day | Continuous | Weekly/release |
| **Release Process** | Tag main | Tag main | Release branches |
| **Hotfix Process** | Branch from main | Branch from main | Dedicated hotfix/* |
| **CI/CD Fit** | Excellent | Excellent | Poor |
| **Team Size** | 1-15 | 5-50+ | Any |
| **Best For** | Startups, SaaS | Enterprises, CI/CD | Versioned software |

---

## GitHub Flow - Detailed Guide

### Philosophy

"Deploy from main, always. Main is always production-ready."

### Full Workflow

**1. Create Feature Branch**:
```bash
# Always branch from latest main
git checkout main
git pull origin main
git checkout -b feature/user-dashboard

# Naming conventions
feature/user-authentication
feature/payment-integration
bugfix/login-error
hotfix/security-patch
docs/api-documentation
```

**2. Develop with Frequent Commits**:
```bash
# Make incremental progress
git commit -m "feat: add dashboard layout component"
git commit -m "feat: add metrics cards to dashboard"
git commit -m "test: add dashboard component tests"
git commit -m "docs: document dashboard props"

# Push frequently for backup
git push origin feature/user-dashboard
```

**3. Open Pull Request Early**:
```markdown
# Draft PR for early feedback
Title: [WIP] User Dashboard

## What
Building user dashboard with metrics and activity feed

## Progress
- [x] Layout component
- [x] Metrics cards
- [ ] Activity feed
- [ ] Responsive design
- [ ] E2E tests

## Questions
- Should we show real-time metrics or daily aggregates?
- Any design feedback on the layout?
```

**4. Review & Iterate**:
```bash
# Address review comments
git commit -m "refactor: extract metrics calculation logic"
git commit -m "fix: handle missing data in metrics cards"
git push origin feature/user-dashboard

# Rebase to keep history clean (optional)
git fetch origin
git rebase origin/main
git push --force-with-lease origin feature/user-dashboard
```

**5. Merge & Deploy**:
```bash
# After approval, merge via GitHub/GitLab UI
# Or locally:
git checkout main
git pull origin main
git merge --no-ff feature/user-dashboard
git push origin main

# Automated deployment triggers
# Tag if needed
git tag -a v1.2.0 -m "Release: User Dashboard"
git push origin v1.2.0

# Clean up
git branch -d feature/user-dashboard
git push origin --delete feature/user-dashboard
```

### GitHub Flow with Feature Flags

For large features that can't ship atomically:

```javascript
// Use feature flags to hide incomplete work
import { featureFlags } from './config';

function Dashboard() {
  if (!featureFlags.userDashboard) {
    return <LegacyDashboard />;
  }
  return <NewDashboard />;
}

// Merge to main even if incomplete
// Enable flag when ready
```

**Advantages**:
- Deploy incomplete code safely
- Test in production with limited users
- Gradual rollout capability

---

## Trunk-Based Development - Detailed Guide

### Philosophy

"Integrate continuously, release confidently. Branches live hours, not days."

### Core Principles

1. **Short-Lived Branches**: < 24 hours from creation to merge
2. **Small Commits**: < 400 lines of code per commit
3. **Feature Flags**: Hide incomplete features
4. **High Test Coverage**: > 80% to catch integration issues
5. **Continuous Integration**: Every commit tested automatically

### Full Workflow

**1. Create Micro-Branch**:
```bash
# Branch for single, focused change
git checkout -b feat/add-user-filter main

# Commit 1: Implementation
git commit -m "feat: add user filter dropdown component"

# Commit 2: Tests
git commit -m "test: add user filter component tests"

# Commit 3: Integration
git commit -m "feat: integrate user filter with table"

# Total time: 2-4 hours
```

**2. Use Feature Flags for Large Features**:
```python
# Feature flag in code
from feature_flags import is_enabled

def process_payment(order):
    if is_enabled('new_payment_processor'):
        return new_payment_flow(order)
    else:
        return legacy_payment_flow(order)

# Deploy to main even if new flow not ready
# Enable flag after testing
```

**3. Merge Rapidly**:
```bash
# Push and create PR immediately
git push origin feat/add-user-filter

# Request quick review (< 2 hours)
# Small PRs get reviewed faster

# Merge within same day
git checkout main
git pull origin main
git merge feat/add-user-filter
git push origin main

# Delete branch immediately
git branch -d feat/add-user-filter
git push origin --delete feat/add-user-filter
```

**4. Continuous Deployment**:
```yaml
# .github/workflows/main.yml
name: CI/CD

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run tests
        run: npm test
      - name: Deploy to production
        if: success()
        run: npm run deploy
```

### Trunk-Based with Release Branches (Scaled)

For teams releasing on schedule:

```bash
# Development on main
git checkout main
git commit -m "feat: new feature"
git push origin main

# Weekly release branch
git checkout -b release/2024-w47 main
git push origin release/2024-w47

# Continue development on main
git checkout main
git commit -m "feat: another feature"

# Hotfix on release branch
git checkout release/2024-w47
git cherry-pick <commit-hash>
git push origin release/2024-w47
```

---

## GitFlow - Detailed Guide

### Philosophy

"Structured releases with parallel development and maintenance."

### Branch Structure

```
main (production)
  ├─ release/v2.1.0 (release prep)
  └─ develop (integration)
      ├─ feature/user-auth
      ├─ feature/payment
      └─ feature/notifications

hotfix/security-patch (from main)
```

### Full Workflow

**1. Feature Development**:
```bash
# Create feature branch from develop
git checkout develop
git pull origin develop
git checkout -b feature/user-authentication

# Develop feature
git commit -m "feat: add JWT authentication"
git commit -m "feat: add refresh token logic"
git commit -m "test: add auth integration tests"

# Keep up-to-date with develop
git fetch origin
git rebase origin/develop

# Merge back to develop
git checkout develop
git merge --no-ff feature/user-authentication
git push origin develop

# Delete feature branch
git branch -d feature/user-authentication
```

**2. Release Preparation**:
```bash
# Create release branch from develop
git checkout develop
git pull origin develop
git checkout -b release/v2.1.0

# Version bump and final fixes
npm version minor
git commit -am "chore: bump version to 2.1.0"

# Bug fixes only on release branch
git commit -m "fix: resolve edge case in auth"

# Merge to main
git checkout main
git merge --no-ff release/v2.1.0
git tag -a v2.1.0 -m "Release 2.1.0"
git push origin main --tags

# Merge back to develop
git checkout develop
git merge --no-ff release/v2.1.0
git push origin develop

# Delete release branch
git branch -d release/v2.1.0
```

**3. Hotfix Process**:
```bash
# Critical bug in production
git checkout main
git pull origin main
git checkout -b hotfix/security-patch

# Fix and test
git commit -m "fix: patch SQL injection vulnerability"
npm version patch  # 2.1.0 -> 2.1.1

# Merge to main
git checkout main
git merge --no-ff hotfix/security-patch
git tag -a v2.1.1 -m "Hotfix: Security patch"
git push origin main --tags

# Merge to develop
git checkout develop
git merge --no-ff hotfix/security-patch
git push origin develop

# Delete hotfix branch
git branch -d hotfix/security-patch
```

---

## Migration Paths

### From GitFlow to GitHub Flow

**Why Migrate**: Faster releases, simpler workflow, better CI/CD fit

**Step 1: Simplify Branches**:
```bash
# Merge all open features to develop
git checkout develop
git merge feature/auth
git merge feature/payments

# Final release from develop
git checkout main
git merge develop
git tag v3.0.0

# Delete develop branch
git branch -D develop
git push origin --delete develop
```

**Step 2: Adopt GitHub Flow**:
```bash
# New workflow: feature branches from main
git checkout main
git checkout -b feature/new-feature
# ... develop, PR, merge to main
```

**Step 3: Update CI/CD**:
```yaml
# Before (GitFlow)
on:
  push:
    branches: [develop]

# After (GitHub Flow)
on:
  push:
    branches: [main]
```

### From GitHub Flow to Trunk-Based

**Why Migrate**: Scale to larger teams, reduce merge conflicts

**Step 1: Add Feature Flags**:
```javascript
// Install feature flag library
npm install @openfeature/server-sdk

// Wrap new features
if (featureFlags.isEnabled('new-search')) {
  return <NewSearch />;
}
```

**Step 2: Enforce Short-Lived Branches**:
```yaml
# .github/workflows/pr-checks.yml
- name: Check branch age
  run: |
    DAYS_OLD=$(git log --since="2 days ago" --oneline | wc -l)
    if [ "$DAYS_OLD" -eq 0 ]; then
      echo "Branch is > 2 days old. Please merge or rebase."
      exit 1
    fi
```

**Step 3: Increase Merge Frequency**:
```bash
# Before: Merge when feature complete
# After: Merge daily with feature flags

git commit -m "feat: add search UI (behind flag)"
git push
# Merge same day, even if incomplete
```

---

## Team Size Recommendations

### Small Teams (1-5 developers)

**Recommendation**: **GitHub Flow**

**Why**:
- Minimal overhead
- Fast iteration
- Easy to understand
- No coordination needed

**Setup**:
```bash
# Branch protection on main
Protected branches: main
Require PR before merge: Yes
Require approvals: 1
Require status checks: Yes (CI)
```

### Medium Teams (5-15 developers)

**Recommendation**: **GitHub Flow** or **Trunk-Based**

**Why**:
- Enough developers for merge conflicts
- Need faster integration (trunk-based)
- Or keep simple with GitHub Flow + feature flags

**Setup**:
```bash
# Trunk-based setup
Protected branches: main
Require PR before merge: Yes
Require approvals: 2
Branch age limit: 24 hours (automated check)
Feature flags: Required for large features
```

### Large Teams (15+ developers)

**Recommendation**: **Trunk-Based Development**

**Why**:
- Reduces merge conflicts through rapid integration
- Scales to hundreds of developers
- Requires mature CI/CD and testing

**Setup**:
```bash
# Enterprise trunk-based
Protected branches: main, release/*
Require PR before merge: Yes
Require approvals: 2
Automated tests: Required
Code coverage: > 80%
Feature flags: Mandatory
Deployment: Automated to staging, manual to prod
```

### Versioned Software Teams

**Recommendation**: **GitFlow**

**Why**:
- Support multiple versions (e.g., 2.x and 3.x)
- Scheduled releases (monthly, quarterly)
- Need structured release process

**Setup**:
```bash
# GitFlow setup
Protected branches: main, develop
Feature branches: feature/*
Release branches: release/*
Hotfix branches: hotfix/*
Require PR for all merges: Yes
Version tags: Required on main
```

---

## Branching Strategy Checklist

### GitHub Flow Readiness

- [ ] Can deploy multiple times per day
- [ ] Have automated CI/CD pipeline
- [ ] Test coverage > 70%
- [ ] Team < 15 developers
- [ ] Single production version
- [ ] Fast review culture (< 4 hours)

### Trunk-Based Readiness

- [ ] Can deploy daily
- [ ] Have feature flag system
- [ ] Test coverage > 80%
- [ ] Automated quality gates
- [ ] Fast CI/CD (< 10 minutes)
- [ ] Team trained on short-lived branches

### GitFlow Readiness

- [ ] Release on schedule (weekly, monthly)
- [ ] Support multiple versions
- [ ] Need QA phase before release
- [ ] Regulated industry (finance, healthcare)
- [ ] Comfortable with complexity
- [ ] Have release manager role

---

## Anti-Patterns to Avoid

### Long-Lived Feature Branches

**Problem**: Feature branch open for weeks, massive merge conflicts

**Fix**: Use stacked diffs or feature flags
```bash
# Bad
git checkout -b feature/rewrite-everything
# ... 3 weeks later, 5000 line diff

# Good
git checkout -b feat/extract-service-layer (400 lines)
git checkout -b feat/add-new-api (300 lines)
git checkout -b feat/migrate-clients (200 lines)
```

### Branching from Branches

**Problem**: Pyramid of branches, unclear base

**Fix**: Always branch from main or develop
```bash
# Bad
feature/A -> feature/B -> feature/C

# Good
main -> feature/A (merge)
main -> feature/B (merge)
main -> feature/C (merge)
```

### No Branch Protection

**Problem**: Accidental direct commits to main

**Fix**: Enable branch protection
```yaml
# GitHub branch protection
main:
  require_pull_request: true
  required_approvals: 2
  dismiss_stale_reviews: true
  require_status_checks: true
  checks:
    - CI/CD Pipeline
    - Code Coverage
    - Security Scan
```

---

## Real-World Examples

### Example 1: SaaS Startup (GitHub Flow)

**Team**: 5 developers
**Deployment**: 10x/day to production
**Workflow**:

```bash
# Developer workflow
git checkout main
git pull
git checkout -b feature/add-export
git commit -m "feat: add CSV export"
git push origin feature/add-export
# Create PR, review, merge
# Deployment happens automatically
```

**Results**:
- Features ship in hours, not days
- Minimal process overhead
- High deployment frequency

### Example 2: Fintech Company (Trunk-Based)

**Team**: 30 developers
**Deployment**: Daily to staging, weekly to prod
**Workflow**:

```bash
# Developer workflow with feature flags
git checkout main
git pull
git checkout -b feat/fraud-detection
git commit -m "feat: add fraud detection (behind flag FRAUD_V2)"
git push origin feat/fraud-detection
# PR reviewed within 2 hours, merged same day
# Feature flag enabled after validation
```

**Results**:
- Reduced merge conflicts by 70%
- Faster integration
- Safe production testing with flags

### Example 3: Enterprise Software (GitFlow)

**Team**: 50 developers
**Deployment**: Quarterly releases
**Workflow**:

```bash
# Feature development
git checkout develop
git checkout -b feature/sso-integration
# ... 2 weeks of development
git checkout develop
git merge feature/sso-integration

# Release preparation
git checkout -b release/v4.0.0 develop
# ... QA testing for 2 weeks
git checkout main
git merge release/v4.0.0
git tag v4.0.0
```

**Results**:
- Structured release process
- Support for multiple versions
- Predictable release schedule
