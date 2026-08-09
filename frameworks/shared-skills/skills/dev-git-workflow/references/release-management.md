# Release Management & Versioning

## Table of Contents

- [Contents](#contents)
- [Semantic Versioning (SemVer)](#semantic-versioning-semver)
- [Manual Release Workflow (GitFlow)](#manual-release-workflow-gitflow)
- [[2.1.0] - YYYY-MM-DD](#210---yyyy-mm-dd)
- [Controlled Release Workflow (release-it / release-please)](#controlled-release-workflow-release-it--release-please)
- [Automated Release Workflow (semantic-release)](#automated-release-workflow-semantic-release)
- [Hotfix Workflow](#hotfix-workflow)
- [Release Checklist](#release-checklist)
- [Versioning Strategies by Project Type](#versioning-strategies-by-project-type)
- [Changelog Best Practices](#changelog-best-practices)
- [[Unreleased]](#unreleased)
- [[2.1.0] - YYYY-MM-DD](#210---yyyy-mm-dd)
- [[2.0.0] - YYYY-MM-DD](#200---yyyy-mm-dd)
- [Release Notification Templates](#release-notification-templates)
- [Related Resources](#related-resources)

Version releases, generate changelogs, and manage deployment workflows using semantic versioning and automation.

## Contents

- Semantic Versioning (SemVer)
- Manual Release Workflow (GitFlow)
- Controlled Release Workflow (release-it / release-please)
- Automated Release Workflow (semantic-release)
- Hotfix Workflow
- Release Checklist
- Versioning Strategies by Project Type
- Changelog Best Practices
- Release Notification Templates
- Related Resources

---

## Semantic Versioning (SemVer)

### Version Format

**Format**: `MAJOR.MINOR.PATCH` (e.g., `2.3.1`)

- **MAJOR** - Breaking changes (2.0.0 -> 3.0.0)
  - Breaking API changes
  - Removed features
  - Major architecture changes

- **MINOR** - New features, backward-compatible (2.0.0 -> 2.1.0)
  - New features
  - New API endpoints
  - Deprecated (but not removed) features

- **PATCH** - Bug fixes, backward-compatible (2.0.0 -> 2.0.1)
  - Bug fixes
  - Security patches
  - Performance improvements
  - Documentation updates

### Pre-release Versions

**Format**: `MAJOR.MINOR.PATCH-<pre-release>.<number>`

**Examples**:
- `1.0.0-alpha.1` - Early development
- `1.0.0-beta.2` - Feature complete, testing
- `1.0.0-rc.1` - Release candidate

**Precedence**:
```
1.0.0-alpha < 1.0.0-alpha.1 < 1.0.0-beta < 1.0.0-rc.1 < 1.0.0
```

---

## Manual Release Workflow (GitFlow)

### 1. Prepare Release Branch

```bash
# Create release branch from develop
git checkout develop
git pull origin develop
git checkout -b release/v2.1.0

# Bump version in package files
npm version minor  # Updates package.json
# Or manually edit: package.json, pyproject.toml, Cargo.toml, etc.

# Update version references
# - README.md
# - API documentation
# - Migration guides
```

### 2. Generate Changelog

**Recommended for controlled/manual releases**:

```bash
npm install --save-dev release-it

# Preview the release without tagging or publishing
npx release-it --dry-run

# Run the release interactively
npx release-it
```

**GitHub-first alternative**: use `release-please` to open a version PR, review the generated notes, and publish after merge.

**Legacy note**: `standard-version` is in maintenance mode and should not be the default choice for new projects.

**Manual changelog format**:

```markdown
# Changelog

## [2.1.0] - YYYY-MM-DD

### Added
- New OAuth2 social login providers (Google, GitHub)
- User profile API endpoints
- Real-time notifications via WebSocket

### Changed
- Improved database query performance (30% faster)
- Updated UI component library to v5.2

### Fixed
- SQL injection vulnerability in search endpoint
- Race condition in user registration
- Memory leak in background job processor

### Deprecated
- Legacy `/api/v1/auth` endpoints (use `/api/v2/auth`)

### Removed
- Support for Node.js 14 (EOL)

### Security
- Patched CVE-2025-1234 in dependency XYZ
```

### 3. Test Release

```bash
# Deploy to staging environment
git push origin release/v2.1.0

# Run full test suite
npm test
npm run test:e2e

# Manual QA testing
# - Smoke tests
# - Regression tests
# - Migration dry-run
```

### 4. Merge to Main and Develop

```bash
# Merge to main (production)
git checkout main
git merge --no-ff release/v2.1.0
git tag -a v2.1.0 -m "Release version 2.1.0"
git push origin main --tags

# Merge back to develop
git checkout develop
git merge --no-ff release/v2.1.0
git push origin develop

# Delete release branch
git branch -d release/v2.1.0
git push origin --delete release/v2.1.0
```

---

## Controlled Release Workflow (release-it / release-please)

Use this when you want reviewed version bumps and generated notes, but do not want fully autonomous publishing on every merge.

### release-it

```bash
npm install --save-dev release-it
npx release-it --dry-run
```

### release-please

- Best fit for GitHub repositories that want version PRs, human review, and conventional-commit-based notes
- Runs as GitHub automation rather than a local CLI-first workflow
- Good default for teams that want strong review gates around releases

---

## Automated Release Workflow (semantic-release)

### Setup

**Installation**:

```bash
npm install --save-dev semantic-release
npm install --save-dev @semantic-release/changelog
npm install --save-dev @semantic-release/git
npm install --save-dev @semantic-release/github
```

**Configuration** (`.releaserc.json`):

```json
{
  "branches": ["main"],
  "plugins": [
    "@semantic-release/commit-analyzer",
    "@semantic-release/release-notes-generator",
    [
      "@semantic-release/changelog",
      {
        "changelogFile": "CHANGELOG.md"
      }
    ],
    "@semantic-release/npm",
    [
      "@semantic-release/git",
      {
        "assets": ["package.json", "CHANGELOG.md"],
        "message": "chore(release): ${nextRelease.version} [skip ci]\n\n${nextRelease.notes}"
      }
    ],
    [
      "@semantic-release/github",
      {
        "assets": [
          {"path": "dist/**", "label": "Distribution"}
        ]
      }
    ]
  ]
}
```

### GitHub Actions Workflow

**File**: `.github/workflows/release.yml`

```yaml
name: Release

on:
  push:
    branches:
      - main

jobs:
  release:
    name: Release
    runs-on: ubuntu-latest
    permissions:
      contents: write
      issues: write
      pull-requests: write
    steps:
      - name: Checkout
        uses: actions/checkout@v4
        with:
          fetch-depth: 0
          persist-credentials: false

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'

      - name: Install dependencies
        run: npm ci

      - name: Build
        run: npm run build

      - name: Run tests
        run: npm test

      - name: Release
        env:
          GITHUB_TOKEN: ${{ secrets.GH_TOKEN }}
          NPM_TOKEN: ${{ secrets.NPM_TOKEN }}
        run: npx semantic-release
```

### How It Works

**On merge to main**:

1. **Analyze commits** - Determines version bump from conventional commits
   - `fix:` -> PATCH (0.0.1)
   - `feat:` -> MINOR (0.1.0)
   - `BREAKING CHANGE:` -> MAJOR (1.0.0)

2. **Generate release notes** - Creates release notes from commits

3. **Update CHANGELOG.md** - Appends new version to changelog

4. **Bump version** - Updates `package.json`

5. **Create Git tag** - Tags commit with version number

6. **Publish to npm** - Publishes package (if configured)

7. **Create GitHub release** - Creates release with notes and artifacts

---

## Hotfix Workflow

### When to Use

**Hotfix required for**:
- Critical production bugs
- Security vulnerabilities
- Data loss prevention
- Service outages

### GitFlow Hotfix Process

```bash
# Create hotfix branch from main
git checkout main
git pull origin main
git checkout -b hotfix/v2.0.1

# Fix the bug
git add .
git commit -m "fix: patch SQL injection vulnerability (CVE-2025-1234)"

# Bump patch version
npm version patch

# Test thoroughly
npm test
npm run test:e2e

# Merge to main
git checkout main
git merge --no-ff hotfix/v2.0.1
git tag -a v2.0.1 -m "Hotfix: Security patch"
git push origin main --tags

# Merge to develop
git checkout develop
git merge --no-ff hotfix/v2.0.1
git push origin develop

# Delete hotfix branch
git branch -d hotfix/v2.0.1
```

### Fast-Track Hotfix (GitHub Flow)

```bash
# Create hotfix branch from main
git checkout -b hotfix/security-patch main

# Fix and test
git commit -m "fix: patch SQL injection (CVE-2025-1234)"

# Create PR with [HOTFIX] label
gh pr create --title "[HOTFIX] Security patch" --base main

# Fast-track review and merge
# After merge, tag immediately
git tag -a v2.0.1 -m "Hotfix: Security patch"
git push origin v2.0.1
```

---

## Release Checklist

### Pre-Release

- [ ] All features merged and tested in staging
- [ ] Version number follows SemVer
- [ ] CHANGELOG.md updated with all changes
- [ ] Breaking changes documented with migration guide
- [ ] API documentation updated
- [ ] Database migration scripts tested
- [ ] Rollback plan documented
- [ ] Performance benchmarks pass
- [ ] Security scan clean

### Release Day

- [ ] Notify stakeholders (schedule downtime if needed)
- [ ] Create release branch (GitFlow) or tag (GitHub Flow)
- [ ] Run full test suite
- [ ] Deploy to staging for final QA
- [ ] Backup production database
- [ ] Deploy to production
- [ ] Run smoke tests
- [ ] Monitor error logs for 1 hour
- [ ] Send release announcement

### Post-Release

- [ ] Monitor error rates and performance
- [ ] Verify all features working in production
- [ ] Update documentation site
- [ ] Close related issues and PRs
- [ ] Merge release branch back to develop (GitFlow)
- [ ] Plan next release cycle

---

## Versioning Strategies by Project Type

### Library/Package

**Follow strict SemVer**:
- Breaking changes = MAJOR bump
- New features = MINOR bump
- Bug fixes = PATCH bump
- Use pre-release versions for testing (`1.0.0-beta.1`)

### Web Application

**Calendar versioning or SemVer**:
- SemVer for APIs and SDKs
- CalVer for user-facing apps (`YYYY.MM.PATCH`)
- Consider date-based releases for continuous deployment

### Mobile App

**Platform-specific versioning**:
- **iOS**: `CFBundleShortVersionString` (user-facing, e.g., 2.1.0)
- **iOS**: `CFBundleVersion` (build number, incrementing, e.g., 145)
- **Android**: `versionName` (user-facing, e.g., 2.1.0)
- **Android**: `versionCode` (build number, incrementing, e.g., 145)

---

## Changelog Best Practices

### Keep a Changelog Format

**Structure**:

```markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added
- Feature X for users to do Y

## [2.1.0] - YYYY-MM-DD

### Added
- OAuth2 social login
- Real-time notifications

### Fixed
- SQL injection in search endpoint (#234)

## [2.0.0] - YYYY-MM-DD

### Changed
- **BREAKING**: Migrated to REST API v2

### Removed
- **BREAKING**: Removed deprecated v1 endpoints

[Unreleased]: https://github.com/user/repo/compare/v2.1.0...HEAD
[2.1.0]: https://github.com/user/repo/compare/v2.0.0...v2.1.0
[2.0.0]: https://github.com/user/repo/releases/tag/v2.0.0
```

### Auto-Generated from Commits

**Tools**:
- `semantic-release` - Fully automated changelog + release
- `release-please` - Reviewable version PRs and release notes
- `release-it` - Controlled manual or interactive releases
- `conventional-changelog` - Manual trigger changelog generation

---

## Release Notification Templates

### Release Announcement (Slack/Email)

```markdown
**[LAUNCH] Version 2.1.0 Released**

**What's New:**
- OAuth2 social login (Google, GitHub)
- Real-time notifications via WebSocket
- User profile API endpoints

**Improvements:**
- 30% faster database queries
- Updated UI component library

**Bug Fixes:**
- Fixed SQL injection vulnerability (#234)
- Resolved race condition in user registration

**Breaking Changes:**
- None

**Migration Guide:** https://docs.example.com/migration/v2.1.0

**Full Changelog:** https://github.com/user/repo/releases/tag/v2.1.0
```

### Hotfix Announcement

```markdown
**[SECURE] Security Hotfix: Version 2.0.1**

**Critical security patch released**

**Fixed:**
- Patched SQL injection vulnerability (CVE-2025-1234)

**Action Required:**
- All users must upgrade immediately
- No breaking changes

**Upgrade:** `npm install package@2.0.1`

**Details:** https://github.com/user/repo/security/advisories/GHSA-xxxx
```

---

## Related Resources

- [Conventional Commits Standard](commit-conventions.md) - Commit formats for automated releases
- [Branching Strategies Comparison](branching-strategies.md) - Release workflows by strategy
- [Automated Quality Gates](automated-quality-gates.md) - CI/CD for releases
