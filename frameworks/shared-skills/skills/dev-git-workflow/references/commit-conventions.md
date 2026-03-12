# Conventional Commits & Semantic Versioning

Comprehensive guide to commit message conventions and automated versioning.

## Contents

- Conventional Commits Specification
- Commit Types
- Examples
- Scopes
- Writing Good Commit Messages
- Semantic Versioning (SemVer)
- Automation Tools
- Changelog Generation
- Best Practices
- Enforcement Strategies
- Team Adoption
- Common Mistakes
- Quick Reference

---

## Conventional Commits Specification

### Format

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

### Components

**Type** (required): Category of change
**Scope** (optional): Area affected (module, component, package)
**Description** (required): Brief summary in imperative mood
**Body** (optional): Detailed explanation of what and why
**Footer** (optional): Breaking changes, issue references

---

## Commit Types

### Standard Types

| Type | Purpose | SemVer Impact | Changelog Section |
|------|---------|---------------|-------------------|
| `feat` | New feature | MINOR (0.1.0) | Features |
| `fix` | Bug fix | PATCH (0.0.1) | Bug Fixes |
| `docs` | Documentation only | None | Documentation |
| `style` | Code style (formatting, whitespace) | None | - |
| `refactor` | Code refactoring | None | - |
| `perf` | Performance improvement | PATCH | Performance |
| `test` | Tests only | None | - |
| `build` | Build system, dependencies | None | Build System |
| `ci` | CI configuration | None | - |
| `chore` | Maintenance tasks | None | - |
| `revert` | Revert previous commit | Depends | - |

### Breaking Changes

| Marker | SemVer Impact | Example |
|--------|---------------|---------|
| `BREAKING CHANGE:` in footer | MAJOR (1.0.0) | See below |
| Exclamation mark after type/scope | MAJOR (1.0.0) | feat!: remove API v1 |

---

## Examples

### Feature (MINOR version bump)

**Simple Feature**:
```bash
git commit -m "feat: add user profile page"
```

**With Scope**:
```bash
git commit -m "feat(auth): add OAuth2 social login"
```

**With Body**:
```bash
git commit -m "feat(api): add pagination to user list endpoint

Add limit and offset query parameters for paginating users.
Default limit is 20, maximum is 100.

Returns total count in response headers for client pagination UI."
```

**With Issue Reference**:
```bash
git commit -m "feat(dashboard): add metrics visualization

Closes #234"
```

### Bug Fix (PATCH version bump)

**Simple Fix**:
```bash
git commit -m "fix: resolve null pointer in login"
```

**With Root Cause**:
```bash
git commit -m "fix(auth): prevent duplicate user creation on concurrent requests

Race condition occurred when multiple requests tried to create
the same user simultaneously. Added database unique constraint
and transaction handling to prevent duplicates.

Fixes #456"
```

**With Testing Notes**:
```bash
git commit -m "fix(api): handle 404 errors for deleted resources

Previously returned 500 error when resource was deleted.
Now returns proper 404 with error message.

Added integration tests to verify error handling."
```

### Breaking Change (MAJOR version bump)

**With Footer**:
```bash
git commit -m "feat(api): migrate to REST API v2

Remove support for all v1 endpoints and migrate to new
response format with consistent error handling.

BREAKING CHANGE: All v1 endpoints removed. Clients must upgrade
to v2 API. See migration guide: docs/api-v2-migration.md"
```

**With ! Marker**:
```bash
git commit -m "feat(auth)!: change JWT payload structure

BREAKING CHANGE: JWT payload now uses 'userId' instead of 'id'.
Existing tokens will be invalidated. Users must re-login."
```

**Multiple Breaking Changes**:
```bash
git commit -m "refactor!: restructure database schema

BREAKING CHANGE: User table renamed to 'users' (was 'user')
BREAKING CHANGE: Deleted 'legacy_auth' table, use 'auth_tokens' instead
BREAKING CHANGE: Changed 'created_at' to timestamp (was string)

Migration required: npm run migrate:v2"
```

### Documentation

```bash
git commit -m "docs: update API authentication guide

Add examples for OAuth2 flow and refresh tokens."
```

```bash
git commit -m "docs(readme): add installation instructions for Windows"
```

### Refactoring

```bash
git commit -m "refactor: extract auth logic to separate service"
```

```bash
git commit -m "refactor(api): simplify error handling middleware

Consolidate duplicate error handling code into single middleware.
No functional changes."
```

### Performance

```bash
git commit -m "perf: optimize database queries with indexes

Add indexes on user.email and post.created_at columns.
Reduces query time from 500ms to 50ms for user search."
```

```bash
git commit -m "perf(frontend): lazy load dashboard components

Reduce initial bundle size by 200KB by lazy loading charts."
```

### Tests

```bash
git commit -m "test: add integration tests for auth flow"
```

```bash
git commit -m "test(api): increase coverage for error handling

Add tests for edge cases: network failures, timeouts,
invalid responses. Coverage increased from 75% to 92%."
```

### Build & Dependencies

```bash
git commit -m "build: upgrade to Node.js 20"
```

```bash
git commit -m "build(deps): bump axios from 1.4.0 to 1.6.0

Security fix for CVE-2023-12345"
```

### CI/CD

```bash
git commit -m "ci: add code coverage reporting to GitHub Actions"
```

```bash
git commit -m "ci: enable auto-merge for dependabot PRs

Auto-merge dependency updates if all tests pass."
```

### Chore

```bash
git commit -m "chore: update .gitignore for IDE files"
```

```bash
git commit -m "chore: clean up unused dependencies"
```

### Revert

```bash
git commit -m "revert: feat(api): add pagination

This reverts commit abc123def456.

Pagination caused performance issues in production."
```

---

## Scopes

### Common Scopes by Project Type

**Backend API**:
- `auth` - Authentication/authorization
- `api` - API endpoints
- `db` - Database, migrations
- `middleware` - Express/Koa middleware
- `service` - Business logic services
- `utils` - Utility functions

**Frontend**:
- `ui` - UI components
- `pages` - Page components
- `store` - State management
- `hooks` - React hooks
- `styles` - CSS, styling
- `routes` - Routing

**Mobile**:
- `ios` - iOS specific code
- `android` - Android specific code
- `navigation` - Navigation
- `screens` - Screen components

**Infrastructure**:
- `infra` - Infrastructure code
- `deploy` - Deployment scripts
- `monitoring` - Monitoring setup
- `security` - Security config

**Monorepo**:
- `packages/auth` - Auth package
- `apps/web` - Web application
- `apps/mobile` - Mobile application

---

## Writing Good Commit Messages

### Imperative Mood

**Use imperative mood** in description (like giving a command).

**Good** (imperative):
```bash
feat: add user authentication
fix: resolve memory leak
docs: update installation guide
```

**Bad** (past tense):
```bash
feat: added user authentication
fix: resolved memory leak
docs: updated installation guide
```

**Rule**: The commit should complete the sentence:
"If applied, this commit will _[your commit message]_"

### Be Specific

**Good** (specific):
```bash
fix(auth): prevent race condition in token refresh

Add mutex lock to prevent concurrent token refresh requests
from creating duplicate tokens.
```

**Bad** (vague):
```bash
fix: fix bug
```

### Explain Why, Not What

The diff shows **what** changed. The message should explain **why**.

**Good** (explains why):
```bash
perf(api): add Redis caching for user profile endpoint

User profile is fetched on every request but changes infrequently.
Caching reduces database load by 80% and improves response time
from 200ms to 20ms.
```

**Bad** (just what):
```bash
perf: add caching
```

### Use Body for Context

**When to use body**:
- Complex changes that need explanation
- Non-obvious solutions or trade-offs
- Multiple related changes
- Breaking changes

**Example**:
```bash
feat(search): implement fuzzy search with Elasticsearch

Replace PostgreSQL full-text search with Elasticsearch to support:
- Fuzzy matching (handle typos)
- Faceted search (filters)
- Relevance scoring
- Real-time indexing

Considered alternatives:
- Algolia: too expensive for our scale
- Meilisearch: lacks advanced features we need

Performance improvement: 100ms -> 20ms avg query time

Closes #789
```

---

## Semantic Versioning (SemVer)

### Version Format

```
MAJOR.MINOR.PATCH
```

**Example**: `2.3.1`

### Version Increments

| Change Type | Increment | Example | Description |
|-------------|-----------|---------|-------------|
| **Breaking change** | MAJOR | 2.3.1 -> 3.0.0 | Incompatible API changes |
| **New feature** | MINOR | 2.3.1 -> 2.4.0 | Backward-compatible functionality |
| **Bug fix** | PATCH | 2.3.1 -> 2.3.2 | Backward-compatible fixes |

### Pre-release Versions

```
1.0.0-alpha.1      # Alpha version (early testing)
1.0.0-beta.2       # Beta version (feature complete, bugs expected)
1.0.0-rc.1         # Release candidate (production ready, final testing)
```

### How Conventional Commits Map to SemVer

**Automatic Version Bumping**:

```
feat: add feature A     ->  1.0.0 -> 1.1.0 (MINOR)
feat: add feature B     ->  1.1.0 -> 1.2.0 (MINOR)
fix: resolve bug X      ->  1.2.0 -> 1.2.1 (PATCH)
fix: resolve bug Y      ->  1.2.1 -> 1.2.2 (PATCH)
feat!: breaking change  ->  1.2.2 -> 2.0.0 (MAJOR)
```

---

## Automation Tools

### 1. Commitlint

**Enforce commit conventions** in git hooks or CI/CD.

**Install**:
```bash
npm install --save-dev @commitlint/cli @commitlint/config-conventional

# Create config
echo "export default {extends: ['@commitlint/config-conventional']};" > commitlint.config.js
```

**Husky Hook** (validate commits locally):
```bash
npm install --save-dev husky

# Add hook
npx husky add .husky/commit-msg 'npx commitlint --edit $1'
```

**CI/CD** (GitHub Actions):
```yaml
- name: Validate PR title
  uses: amannn/action-semantic-pull-request@v5
  env:
    GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

### 2. Standard-Version

**Automate changelog and version bumps** (manual trigger).

**Install**:
```bash
npm install --save-dev standard-version
```

**Usage**:
```bash
# Generate changelog and bump version
npm run release

# First release
npm run release -- --first-release

# Pre-release
npm run release -- --prerelease alpha
```

**What it does**:
1. Analyzes commits since last tag
2. Determines next version (SemVer)
3. Updates CHANGELOG.md
4. Bumps version in package.json
5. Creates git tag

### 3. Semantic-Release

**Fully automated** version management (triggers on CI/CD).

**Install**:
```bash
npm install --save-dev semantic-release
```

**Configuration** (`.releaserc.json`):
```json
{
  "branches": ["main"],
  "plugins": [
    "@semantic-release/commit-analyzer",
    "@semantic-release/release-notes-generator",
    "@semantic-release/changelog",
    "@semantic-release/npm",
    "@semantic-release/git",
    "@semantic-release/github"
  ]
}
```

**GitHub Actions**:
```yaml
name: Release

on:
  push:
    branches: [main]

jobs:
  release:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
      - run: npm ci
      - run: npx semantic-release
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          NPM_TOKEN: ${{ secrets.NPM_TOKEN }}
```

**What it does**:
1. Analyzes commits on main branch
2. Determines next version
3. Generates release notes
4. Updates CHANGELOG.md
5. Publishes to npm
6. Creates GitHub release
7. Commits version bump

---

## Changelog Generation

### Automatic Changelog from Commits

**Example CHANGELOG.md**:

```markdown
# Changelog

All notable changes to this project will be documented in this file.

## [2.1.0] - 2024-03-15

### Features

- **auth**: add OAuth2 social login ([abc123](https://github.com/user/repo/commit/abc123))
- **dashboard**: add metrics visualization ([def456](https://github.com/user/repo/commit/def456))

### Bug Fixes

- **api**: handle 404 errors for deleted resources ([ghi789](https://github.com/user/repo/commit/ghi789))
- **auth**: prevent duplicate user creation ([jkl012](https://github.com/user/repo/commit/jkl012))

### Performance

- **api**: add Redis caching for user profiles ([mno345](https://github.com/user/repo/commit/mno345))

## [2.0.0] - 2024-02-01

### BREAKING CHANGES

- **api**: migrate to REST API v2 ([pqr678](https://github.com/user/repo/commit/pqr678))
  - Remove all v1 endpoints
  - New response format
  - Migration guide: docs/api-v2-migration.md

### Features

- **api**: add pagination to all list endpoints ([stu901](https://github.com/user/repo/commit/stu901))
```

---

## Best Practices

### Atomic Commits

Each commit should be a **single logical change**.

**Good** (atomic):
```bash
git commit -m "feat: add user authentication"
git commit -m "test: add auth integration tests"
git commit -m "docs: document auth API"
```

**Bad** (mixing changes):
```bash
git commit -m "Add auth, fix bug, update docs"
```

### Commit Frequency

**Commit often**, but keep commits meaningful.

**Good rhythm**:
- Implement feature -> commit
- Write tests -> commit
- Fix discovered bug -> commit
- Update docs -> commit

**Too frequent** (bad):
```bash
git commit -m "WIP"
git commit -m "fix typo"
git commit -m "fix another typo"
git commit -m "actually fix it now"
```

**Solution**: Use `git commit --amend` or interactive rebase to clean up before pushing.

### Squashing Before Merge

Clean up messy commit history before merging:

```bash
# Interactive rebase to squash commits
git rebase -i HEAD~5

# Or use --autosquash workflow
git commit -m "feat: add feature"
git commit -m "fixup! feat: add feature"  # Auto-squashes
git rebase -i --autosquash main
```

---

## Enforcement Strategies

### Local Enforcement (Git Hooks)

**Pre-commit hook** (format check):
```bash
#!/bin/bash
# .git/hooks/pre-commit

npm run lint
npm run test:quick
```

**Commit-msg hook** (commitlint):
```bash
#!/bin/bash
# .git/hooks/commit-msg

npx commitlint --edit $1
```

### CI/CD Enforcement

**GitHub Actions**:
```yaml
name: Commit Checks

on:
  pull_request:

jobs:
  commitlint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Validate commits
        uses: wagoid/commitlint-github-action@v5
```

**GitLab CI**:
```yaml
commitlint:
  stage: test
  script:
    - npm install @commitlint/cli @commitlint/config-conventional
    - echo "module.exports = {extends: ['@commitlint/config-conventional']};" > commitlint.config.js
    - npx commitlint --from $CI_MERGE_REQUEST_DIFF_BASE_SHA --to HEAD
  rules:
    - if: '$CI_PIPELINE_SOURCE == "merge_request_event"'
```

---

## Team Adoption

### Gradual Rollout

**Phase 1: Education** (Week 1-2)
- Share commit convention guide
- Demo tools (commitlint, semantic-release)
- Show benefits (automated changelogs)

**Phase 2: Soft Enforcement** (Week 3-4)
- Add commitlint warnings (not blocking)
- Encourage conventional commits in PRs
- Team reviews examples together

**Phase 3: Hard Enforcement** (Week 5+)
- Enable commitlint in CI/CD (blocking)
- Require conventional commits for all PRs
- Reject non-conforming commits

### Commit Message Templates

**Create git template**:
```bash
# ~/.gitmessage
# <type>[optional scope]: <description>
#
# [optional body]
#
# [optional footer(s)]
#
# Types: feat, fix, docs, style, refactor, perf, test, build, ci, chore, revert

git config --global commit.template ~/.gitmessage
```

Now `git commit` opens editor with template filled in.

---

## Common Mistakes

### Mistake 1: Vague Types

**Bad**:
```bash
git commit -m "chore: update stuff"
```

**Good**:
```bash
git commit -m "build(deps): upgrade React from 17 to 18"
```

### Mistake 2: Missing Scope

**Bad**:
```bash
git commit -m "feat: add feature"
```

**Good**:
```bash
git commit -m "feat(auth): add OAuth2 social login"
```

### Mistake 3: Past Tense

**Bad**:
```bash
git commit -m "fixed bug in login"
```

**Good**:
```bash
git commit -m "fix(auth): resolve race condition in login"
```

### Mistake 4: No Context

**Bad**:
```bash
git commit -m "fix: bug"
```

**Good**:
```bash
git commit -m "fix(api): prevent null pointer when user not found

Return 404 error instead of 500 when user ID doesn't exist.
Added validation middleware to check resource existence.

Fixes #456"
```

---

## Quick Reference

### Commit Message Checklist

- [ ] Type is valid (feat, fix, docs, etc.)
- [ ] Scope is appropriate (if used)
- [ ] Description is imperative mood ("add" not "added")
- [ ] Description is specific and clear
- [ ] Body explains why (if complex)
- [ ] Footer references issues (if applicable)
- [ ] Breaking changes marked with exclamation mark or BREAKING CHANGE footer

### Common Commands

```bash
# Amend last commit
git commit --amend

# Rewrite commit message
git commit --amend -m "new message"

# Interactive rebase (clean up history)
git rebase -i HEAD~3

# Auto-squash fixup commits
git commit -m "fixup! previous commit message"
git rebase -i --autosquash main

# Sign commits
git commit -S -m "commit message"
```

### Resources

- **Conventional Commits Spec**: https://www.conventionalcommits.org
- **Semantic Versioning**: https://semver.org
- **Commitlint**: https://commitlint.js.org
- **Standard-Version**: https://github.com/conventional-changelog/standard-version
- **Semantic-Release**: https://semantic-release.gitbook.io
