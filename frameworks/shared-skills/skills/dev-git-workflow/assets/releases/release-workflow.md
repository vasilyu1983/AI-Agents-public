# Release Workflow Template

Complete workflow for managing software releases with semantic versioning and automation.

---

## Overview

This template provides a production-ready release workflow combining:
- **Semantic Versioning (SemVer)** - MAJOR.MINOR.PATCH version scheme
- **Conventional Commits** - Automated version bumping from commit messages
- **Automated Releases** - CI/CD-driven release process
- **Release Notes** - Auto-generated changelogs

---

## Release Types & Version Bumping

### Semantic Versioning Format

```
MAJOR.MINOR.PATCH[-PRERELEASE][+BUILD]

Examples:
- 1.0.0        - Initial stable release
- 1.2.3        - Patch release
- 2.0.0        - Major release (breaking changes)
- 2.1.0-beta.1 - Pre-release version
- 2.1.0+20240115 - Build metadata
```

### Version Bump Rules

| Change Type | Commit Prefix | Version Impact | Example |
|-------------|--------------|----------------|---------|
| **Breaking change** | `feat!:` or `BREAKING CHANGE:` | MAJOR (1.0.0 -> 2.0.0) | API redesign |
| **New feature** | `feat:` | MINOR (1.0.0 -> 1.1.0) | Add user export |
| **Bug fix** | `fix:` | PATCH (1.0.0 -> 1.0.1) | Fix login issue |
| **Performance** | `perf:` | PATCH (1.0.0 -> 1.0.1) | Optimize queries |
| **Other** | `docs:`, `style:`, `refactor:`, `test:`, `chore:` | No version bump | Update README |

---

## Manual Release Workflow (GitFlow)

Use this workflow for scheduled releases with manual control.

### 1. Prepare Release Branch

```bash
# Create release branch from develop
git checkout develop
git pull origin develop
git checkout -b release/v2.1.0

# Bump version in package files
# package.json, pyproject.toml, Cargo.toml, etc.
npm version 2.1.0 --no-git-tag-version
# OR
# Edit version manually in package.json, setup.py, etc.

# Commit version bump
git commit -am "chore: bump version to 2.1.0"
```

### 2. Generate Changelog

```bash
# Option 1: Use standard-version (recommended)
npm install -g standard-version
npx standard-version --dry-run  # Preview changes
npx standard-version              # Generate CHANGELOG.md

# Option 2: Manual changelog
# Edit CHANGELOG.md with release notes
```

**CHANGELOG.md Format**:
```markdown
# Changelog

## [2.1.0] - 2024-11-20

### Added
- User profile export feature (#234)
- OAuth2 social login support (#456)

### Fixed
- Race condition in user registration (#789)
- Memory leak in WebSocket handler (#790)

### Changed
- Improved error messages for API validation (#567)

### Breaking Changes
- Removed deprecated /api/v1/users endpoint (use /api/v2/users)
```

### 3. Merge to Main and Tag

```bash
# Merge release to main
git checkout main
git merge --no-ff release/v2.1.0
git tag -a v2.1.0 -m "Release version 2.1.0"

# Push to remote
git push origin main --tags

# Merge back to develop
git checkout develop
git merge --no-ff release/v2.1.0
git push origin develop

# Delete release branch
git branch -d release/v2.1.0
git push origin --delete release/v2.1.0
```

### 4. Publish Release

```bash
# Publish to npm/PyPI/etc.
npm publish

# Or create GitHub/GitLab release
gh release create v2.1.0 \
  --title "Release v2.1.0" \
  --notes-file CHANGELOG.md
```

---

## Automated Release Workflow (Recommended)

Use **semantic-release** for fully automated version management.

### Setup semantic-release

**1. Install Dependencies**:
```bash
npm install --save-dev semantic-release \
  @semantic-release/changelog \
  @semantic-release/git \
  @semantic-release/github
```

**2. Configure `.releaserc.json`**:
```json
{
  "branches": ["main"],
  "plugins": [
    "@semantic-release/commit-analyzer",
    "@semantic-release/release-notes-generator",
    ["@semantic-release/changelog", {
      "changelogFile": "CHANGELOG.md"
    }],
    "@semantic-release/npm",
    ["@semantic-release/git", {
      "assets": ["CHANGELOG.md", "package.json"],
      "message": "chore(release): ${nextRelease.version} [skip ci]\n\n${nextRelease.notes}"
    }],
    "@semantic-release/github"
  ]
}
```

**3. GitHub Actions Workflow**:

Create `.github/workflows/release.yml`:
```yaml
name: Release

on:
  push:
    branches:
      - main

permissions:
  contents: write
  issues: write
  pull-requests: write

jobs:
  release:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: 'lts/*'

      - name: Install dependencies
        run: npm ci

      - name: Run tests
        run: npm test

      - name: Release
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          NPM_TOKEN: ${{ secrets.NPM_TOKEN }}
        run: npx semantic-release
```

**4. GitLab CI Configuration**:

Create `.gitlab-ci.yml`:
```yaml
release:
  stage: release
  image: node:lts
  only:
    - main
  script:
    - npm ci
    - npm test
    - npx semantic-release
  variables:
    GL_TOKEN: $CI_JOB_TOKEN
    NPM_TOKEN: $NPM_TOKEN
```

### How semantic-release Works

```
1. Analyze commits since last release
   ↓
2. Determine next version (MAJOR, MINOR, PATCH)
   ↓
3. Generate release notes from commits
   ↓
4. Update CHANGELOG.md
   ↓
5. Bump version in package.json
   ↓
6. Create Git tag
   ↓
7. Publish to npm/GitHub/etc.
   ↓
8. Post GitHub release with notes
```

**Example Commit History -> Version**:
```
feat: add user export          -> 1.0.0 -> 1.1.0
fix: resolve memory leak       -> 1.1.0 -> 1.1.1
feat!: redesign API            -> 1.1.1 -> 2.0.0
```

---

## Pre-release Workflow

### Create Alpha/Beta Releases

**Manual (GitFlow)**:
```bash
# Create pre-release branch
git checkout -b release/v2.0.0-beta.1 develop

# Bump version to pre-release
npm version 2.0.0-beta.1 --no-git-tag-version
git commit -am "chore: release v2.0.0-beta.1"

# Merge to main and tag
git checkout main
git merge --no-ff release/v2.0.0-beta.1
git tag v2.0.0-beta.1
git push origin main --tags

# Publish pre-release
npm publish --tag beta
```

**Automated (semantic-release)**:

Configure `.releaserc.json` for pre-releases:
```json
{
  "branches": [
    "main",
    {
      "name": "beta",
      "prerelease": true
    },
    {
      "name": "alpha",
      "prerelease": true
    }
  ]
}
```

Push to beta branch:
```bash
git checkout -b beta
git push origin beta
# Triggers release: 2.0.0-beta.1
```

---

## Hotfix Workflow

### GitFlow Hotfix

```bash
# Create hotfix branch from main
git checkout main
git checkout -b hotfix/v2.0.1

# Fix the issue
git commit -m "fix: resolve critical security vulnerability"

# Bump version
npm version patch --no-git-tag-version
git commit -am "chore: bump version to 2.0.1"

# Merge to main
git checkout main
git merge --no-ff hotfix/v2.0.1
git tag v2.0.1
git push origin main --tags

# Merge to develop
git checkout develop
git merge --no-ff hotfix/v2.0.1
git push origin develop

# Delete hotfix branch
git branch -d hotfix/v2.0.1
```

### Trunk-Based Hotfix

```bash
# Fix directly on main (or short-lived branch)
git checkout main
git checkout -b hotfix/security-patch

# Fix the issue
git commit -m "fix: resolve critical security vulnerability"

# Merge via PR with expedited review
# Automated release triggers from main
```

---

## Release Checklist

### Pre-Release Checklist

- [ ] All tests pass in CI/CD
- [ ] Code coverage meets threshold (e.g., 80%)
- [ ] All PRs merged and approved
- [ ] Documentation updated
- [ ] CHANGELOG.md reviewed (if manual)
- [ ] Version number follows SemVer
- [ ] Breaking changes documented
- [ ] Migration guide written (if breaking changes)
- [ ] Staging environment tested
- [ ] Performance benchmarks pass
- [ ] Security scan completed (no critical vulnerabilities)

### Release Execution Checklist

- [ ] Create release branch (GitFlow) or merge to main (Trunk-Based)
- [ ] Bump version number
- [ ] Generate/review changelog
- [ ] Create Git tag
- [ ] Push tag to remote
- [ ] Publish package (npm, PyPI, Docker, etc.)
- [ ] Create GitHub/GitLab release
- [ ] Update documentation site
- [ ] Notify stakeholders (Slack, email, etc.)

### Post-Release Checklist

- [ ] Monitor error tracking (Sentry, Rollbar, etc.)
- [ ] Check metrics dashboard
- [ ] Monitor user feedback
- [ ] Verify deployment to production
- [ ] Update project board/Jira
- [ ] Tweet/blog announcement (if public release)
- [ ] Merge release branch back to develop (GitFlow)

---

## Release Types

### Patch Release (1.0.0 -> 1.0.1)

**When**: Bug fixes, performance improvements, documentation updates

**Scope**: Backward-compatible changes only

**Timeline**: As needed (hotfixes can be immediate)

**Example Commits**:
```
fix: resolve null pointer exception in user service
perf: optimize database queries for user search
docs: update API authentication examples
```

### Minor Release (1.0.0 -> 1.1.0)

**When**: New features, backward-compatible API additions

**Scope**: Additive changes, no breaking changes

**Timeline**: Weekly, bi-weekly, or monthly

**Example Commits**:
```
feat: add user profile export to CSV
feat: implement OAuth2 social login
feat: add real-time notifications
```

### Major Release (1.0.0 -> 2.0.0)

**When**: Breaking changes, API redesigns, major refactors

**Scope**: Can include breaking changes

**Timeline**: Quarterly, bi-annually, or annually

**Example Commits**:
```
feat!: redesign REST API with new resource structure
BREAKING CHANGE: Remove deprecated /api/v1/* endpoints
feat!: migrate to new authentication system
```

**Migration Guide Template**:
```markdown
# Migration Guide: v1.x -> v2.0

## Breaking Changes

### 1. API Endpoint Changes

**Before (v1.x)**:
GET /api/v1/users

**After (v2.0)**:
GET /api/v2/users

### 2. Authentication Changes

**Before (v1.x)**:
Authorization: Token <token>

**After (v2.0)**:
Authorization: Bearer <token>

## Migration Steps

1. Update API base URL
2. Replace authentication headers
3. Update request/response formats
4. Run migration script: `npm run migrate:v2`

## Support Timeline

- v1.x: Supported until 2025-06-01
- v2.0: Current stable version
```

---

## Rollback Plan

### Rollback Strategies

**1. Revert Git Tag (Recommended)**:
```bash
# Revert to previous version
git revert v2.1.0..HEAD
git tag v2.1.1
git push origin main --tags

# Publish rollback version
npm publish
```

**2. Republish Previous Version**:
```bash
# Republish previous stable version
git checkout v2.0.0
npm publish

# Update latest tag
npm dist-tag add package-name@2.0.0 latest
```

**3. Hotfix Release**:
```bash
# Create hotfix on top of failed release
git checkout -b hotfix/v2.1.1 v2.1.0
# Fix critical issue
git commit -m "fix: resolve critical deployment issue"
npm version patch
git push origin hotfix/v2.1.1
```

### Rollback Checklist

- [ ] Identify root cause of failure
- [ ] Decide rollback strategy
- [ ] Notify stakeholders
- [ ] Execute rollback
- [ ] Verify rollback in staging
- [ ] Deploy rollback to production
- [ ] Monitor metrics post-rollback
- [ ] Document incident for postmortem

---

## Version Compatibility Matrix

Document version compatibility for multi-component systems.

```markdown
| API Version | Client Version | Database Schema | Supported Until |
|-------------|----------------|-----------------|-----------------|
| 2.1.x       | >= 2.0.0       | v5              | 2025-12-31      |
| 2.0.x       | >= 1.5.0       | v4              | 2025-06-01      |
| 1.x.x       | >= 1.0.0       | v3              | 2024-12-31      |
```

---

## Tools Comparison

| Tool | Use Case | Pros | Cons |
|------|----------|------|------|
| **semantic-release** | Fully automated | Zero-config, CI/CD native | Less control over process |
| **standard-version** | Manual trigger | More control, dry-run mode | Manual execution required |
| **release-it** | Interactive | User-friendly prompts | Not ideal for full automation |
| **Manual** | Full control | Complete flexibility | Error-prone, time-consuming |

---

## Advanced Configurations

### Monorepo Releases

Use **Lerna** or **semantic-release-monorepo**:

```json
{
  "plugins": [
    "@semantic-release/commit-analyzer",
    "@semantic-release/release-notes-generator",
    ["@semantic-release/npm", {
      "pkgRoot": "packages/core"
    }],
    ["@semantic-release/npm", {
      "pkgRoot": "packages/utils"
    }]
  ]
}
```

### Custom Release Notes

Customize release note template:

```json
{
  "plugins": [
    ["@semantic-release/release-notes-generator", {
      "preset": "angular",
      "writerOpts": {
        "headerPartial": "## {{version}} ({{date}})\n\n"
      }
    }]
  ]
}
```

---

## References

- **Semantic Versioning**: https://semver.org/
- **Conventional Commits**: https://www.conventionalcommits.org/
- **semantic-release**: https://semantic-release.gitbook.io/
- **standard-version**: https://github.com/conventional-changelog/standard-version
- **GitHub Releases**: https://docs.github.com/en/repositories/releasing-projects-on-github
- **GitLab Releases**: https://docs.gitlab.com/ee/user/project/releases/
