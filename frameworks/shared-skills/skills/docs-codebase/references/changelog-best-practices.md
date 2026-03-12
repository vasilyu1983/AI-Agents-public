# Changelog Best Practices

Comprehensive guide for maintaining changelogs using the "Keep a Changelog" format and semantic versioning.

## What Is a Changelog?

A **changelog** is a file documenting all notable changes made to a project in chronological order.

**Purpose**:
- Help users understand what changed between versions
- Communicate breaking changes clearly
- Show project activity and maintenance status
- Enable informed upgrade decisions

**Standard**: [Keep a Changelog](https://keepachangelog.com/) v1.1.0

## Keep a Changelog Format

### Basic Structure

```markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- New features that are not yet released

## [1.2.0] - 2025-11-22

### Added
- Feature descriptions

### Changed
- Changes to existing functionality

### Deprecated
- Features marked for removal in future versions

### Removed
- Features removed in this version

### Fixed
- Bug fixes

### Security
- Security vulnerability patches

## [1.1.0] - 2025-10-15
...

[Unreleased]: https://github.com/user/repo/compare/v1.2.0...HEAD
[1.2.0]: https://github.com/user/repo/compare/v1.1.0...v1.2.0
[1.1.0]: https://github.com/user/repo/compare/v1.0.0...v1.1.0
```

## Change Categories

### Added

**Purpose**: New features or capabilities.

**Examples**:
```markdown
### Added
- OAuth2 authentication with Google and GitHub providers
- Rate limiting with Redis (100 requests per minute per user)
- Webhook support for order completion events
- Export functionality for user reports (CSV and JSON formats)
- Dark mode toggle in user settings
```

**Best practices**:
- Start with verb (passive voice acceptable)
- Be specific about what was added
- Include relevant details (providers, formats, limits)

### Changed

**Purpose**: Changes to existing functionality.

**Examples**:
```markdown
### Changed
- Improved search performance by 60% using Elasticsearch
- Updated Node.js requirement from 16+ to 18+
- Changed default pagination limit from 10 to 20 items
- Refactored authentication flow for better security
- Updated UI design to match new brand guidelines
```

**Best practices**:
- Explain the change clearly
- Include performance improvements with metrics
- Mention requirement changes
- Note visual/UX changes

### Deprecated

**Purpose**: Features that will be removed in future versions.

**Examples**:
```markdown
### Deprecated
- Legacy API v1 endpoints (will be removed in v2.0.0)
  - Use API v2 endpoints instead: `/api/v2/users`
- `getUserData()` function (use `fetchUserProfile()` instead)
- XML response format (JSON is now the standard)
- Support for Node.js 14 (end-of-life 2023-04-30)
```

**Best practices**:
- State removal timeline
- Provide migration path/alternative
- Explain reason for deprecation

### Removed

**Purpose**: Features removed in this version.

**Examples**:
```markdown
### Removed
- API v1 endpoints (deprecated in v1.5.0)
- Internet Explorer 11 support
- Legacy authentication using session cookies
- `/legacy-api/*` routes
- Deprecated `config.old.json` format
```

**Best practices**:
- Reference when it was deprecated
- Keep brief (removal was communicated in deprecation)
- List breaking changes prominently

### Fixed

**Purpose**: Bug fixes.

**Examples**:
```markdown
### Fixed
- Memory leak in WebSocket connections (#456)
- Race condition in order processing queue (#789)
- Incorrect timezone handling in date picker (#321)
- XSS vulnerability in comment rendering (CVE-2025-12345)
- 404 error when navigating to user profiles with special characters
```

**Best practices**:
- Link to issue numbers
- Describe the bug clearly
- Include CVE numbers for security fixes
- Mention user-facing impact

### Security

**Purpose**: Security vulnerability patches.

**Examples**:
```markdown
### Security
- Updated jsonwebtoken to 9.0.0 (CVE-2022-23529)
- Fixed SQL injection vulnerability in search endpoint (CVSS 8.1)
- Patched XSS vulnerability in markdown renderer (CVE-2025-1234)
- Upgraded axios to 1.6.0 to fix SSRF vulnerability
- Added rate limiting to prevent brute-force attacks on login
```

**Best practices**:
- **Always list security fixes** in a dedicated section
- Include CVE numbers if assigned
- Include CVSS scores for severity
- Link to security advisories
- Don't expose exploit details

## Version Numbering (Semantic Versioning)

**Format**: `MAJOR.MINOR.PATCH`

### MAJOR (Breaking Changes)

Increment when making incompatible API changes.

**Examples**:
- Removing deprecated endpoints
- Changing function signatures
- Changing response formats
- Removing configuration options
- Requiring new dependencies

**Changelog entry**:
```markdown
## [2.0.0] - 2025-11-22

### Removed
- API v1 endpoints (use v2 instead)

### Changed
- `createUser()` now returns Promise instead of callback
- Changed response format from XML to JSON
```

### MINOR (New Features)

Increment when adding functionality in a backward-compatible manner.

**Examples**:
- Adding new endpoints
- Adding optional parameters
- Adding new features
- Extending functionality

**Changelog entry**:
```markdown
## [1.3.0] - 2025-11-22

### Added
- OAuth2 authentication support
- Export to PDF functionality
- GraphQL API endpoint
```

### PATCH (Bug Fixes)

Increment when making backward-compatible bug fixes.

**Examples**:
- Fixing bugs
- Security patches
- Performance improvements
- Documentation updates

**Changelog entry**:
```markdown
## [1.2.1] - 2025-11-22

### Fixed
- Memory leak in connection pooling (#234)
- Incorrect date formatting in exports

### Security
- Updated dependencies to patch vulnerabilities
```

## Complete Changelog Example

```markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Bulk user import from CSV files
- Email notifications for order status changes

### Changed
- Improved dashboard loading time by 40%

## [1.2.0] - 2025-11-22

### Added
- OAuth2 authentication with Google and GitHub (#123)
- Rate limiting with Redis: 100 requests per minute per user (#145)
- Webhook support for `order.completed` and `user.created` events (#167)
- Export user reports in CSV and JSON formats (#189)
- Dark mode toggle in user settings (#201)

### Changed
- Improved search performance by 60% using Elasticsearch instead of PostgreSQL full-text search (#134)
- Updated minimum Node.js version from 16.x to 18.x (#156)
- Changed default pagination limit from 10 to 20 items per page (#178)
- Refactored authentication flow to use JWT instead of sessions (#192)

### Deprecated
- Legacy API v1 endpoints under `/api/v1/*` (will be removed in v2.0.0)
  - Migrate to `/api/v2/*` endpoints
  - See migration guide: [MIGRATION.md](MIGRATION.md)

### Fixed
- Memory leak in WebSocket connections after 24 hours of runtime (#456)
- Race condition in order processing queue causing duplicate charges (#489)
- Incorrect timezone handling in date picker component (#321)
- 404 error when navigating to user profiles with special characters (#367)

### Security
- Updated jsonwebtoken from 8.5.1 to 9.0.0 (CVE-2022-23529, CVSS 7.5)
- Fixed SQL injection vulnerability in search endpoint (CVE-2025-1234, CVSS 8.1)
- Patched XSS vulnerability in markdown renderer (CVE-2025-5678)
- Upgraded axios to 1.6.0 to fix SSRF vulnerability

## [1.1.0] - 2025-10-15

### Added
- Two-factor authentication (2FA) with TOTP (#98)
- User profile customization options (#112)
- Admin dashboard for user management (#134)

### Changed
- Migrated from JavaScript to TypeScript (#87)
- Updated UI design to match new brand guidelines (#101)

### Fixed
- Email verification links expiring too quickly (#76)
- Pagination breaking on last page (#89)

## [1.0.0] - 2025-09-01

### Added
- Initial release
- User authentication and registration
- Product catalog with search
- Shopping cart functionality
- Stripe payment integration
- Order management system
- Admin panel
- Email notifications

[Unreleased]: https://github.com/user/repo/compare/v1.2.0...HEAD
[1.2.0]: https://github.com/user/repo/compare/v1.1.0...v1.2.0
[1.1.0]: https://github.com/user/repo/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/user/repo/releases/tag/v1.0.0
```

## Unreleased Section

**Purpose**: Track upcoming changes before release.

**Usage**:
```markdown
## [Unreleased]

### Added
- Feature X that will be in next release

### Fixed
- Bug Y that will be in next release
```

**When releasing**:
1. Create new version section
2. Move Unreleased items to version section
3. Add release date
4. Clear Unreleased section

**Example transformation**:

**Before release**:
```markdown
## [Unreleased]

### Added
- Dark mode support
```

**After 1.3.0 release**:
```markdown
## [Unreleased]

## [1.3.0] - 2025-11-22

### Added
- Dark mode support
```

## Linking to Commits

**At the bottom of CHANGELOG.md**:

```markdown
[Unreleased]: https://github.com/user/repo/compare/v1.2.0...HEAD
[1.2.0]: https://github.com/user/repo/compare/v1.1.0...v1.2.0
[1.1.0]: https://github.com/user/repo/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/user/repo/releases/tag/v1.0.0
```

**Benefits**:
- Click version to see all changes on GitHub
- Visual diff between versions
- Traceability to commits

## Changelog Anti-Patterns

**BAD: Avoid**:

**Commit dumps**:
```markdown
### Changed
- Fixed typo
- Updated package.json
- Refactored code
- Fixed bug
- Updated README
```

Instead, group related changes:
```markdown
### Changed
- Improved user authentication security
  - Implemented rate limiting
  - Added 2FA support
  - Fixed session timeout bug
```

**Vague entries**:
```markdown
### Fixed
- Fixed bugs
- Performance improvements
- Various updates
```

Instead, be specific:
```markdown
### Fixed
- Memory leak in WebSocket connections (#456)
- Search performance improved by 60%
```

**No dates**:
```markdown
## [1.2.0]  ← Missing date
```

Instead:
```markdown
## [1.2.0] - 2025-11-22
```

**Missing links**:
```markdown
[1.2.0]: Missing
```

Instead:
```markdown
[1.2.0]: https://github.com/user/repo/compare/v1.1.0...v1.2.0
```

## Automated Changelog Generation

### semantic-release

**Installation**:
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
    "@semantic-release/github",
    "@semantic-release/git"
  ]
}
```

**Commit format** (Conventional Commits):
```
feat: add OAuth2 authentication
fix: resolve memory leak in WebSocket
docs: update API documentation
chore: upgrade dependencies
```

### standard-version

**Installation**:
```bash
npm install --save-dev standard-version
```

**Usage**:
```bash
npm run release
```

**What it does**:
1. Bumps version in `package.json`
2. Generates/updates `CHANGELOG.md`
3. Creates git tag
4. Commits changes

## Writing Style Guidelines

### Audience

Write for:
- Users upgrading to new version
- Developers integrating your library
- Product managers tracking features

### Tone

- **Clear and concise** - No marketing fluff
- **Technical but accessible** - Avoid jargon when possible
- **Action-oriented** - Start with verbs
- **User-focused** - Explain impact on users

### Format

**Good**:
```markdown
### Added
- OAuth2 authentication with Google and GitHub providers
- Rate limiting: 100 requests per minute per user (configurable)
```

**Bad**:
```markdown
### Added
- We've added the amazing new feature of OAuth2! Now you can log in with Google or GitHub!
```

### Breaking Changes

**Always highlight breaking changes prominently**:

```markdown
## [2.0.0] - 2025-11-22 - BREAKING CHANGES

### Removed
- [WARNING] **BREAKING**: API v1 endpoints removed (use v2 instead)
- [WARNING] **BREAKING**: Node.js 14 support dropped (requires 18+)

### Changed
- [WARNING] **BREAKING**: `createUser()` signature changed
  - **Old**: `createUser(name, email, callback)`
  - **New**: `createUser({ name, email }): Promise<User>`
```

## Changelog Maintenance Checklist

**When releasing**:

- [ ] Move Unreleased items to new version section
- [ ] Add release date in YYYY-MM-DD format
- [ ] Update version number (semantic versioning)
- [ ] Add comparison link at bottom
- [ ] Update Unreleased link
- [ ] Verify all issue/PR links work
- [ ] Check for typos and formatting
- [ ] Highlight breaking changes
- [ ] Include migration guide link if needed
- [ ] Tag release in Git

## Tools for Changelog Management

**Generators**:
- `semantic-release` - Automated versioning and changelog
- `standard-version` - Conventional Commits to changelog
- `auto-changelog` - Generate from Git history
- `conventional-changelog` - Changelog from commits

**Validators**:
- `changelogithub` - Validate changelog format
- Custom CI scripts to enforce format

**Example CI check**:
```bash
# Verify CHANGELOG.md was updated
git diff --name-only HEAD~1 | grep CHANGELOG.md || {
  echo "Error: CHANGELOG.md not updated"
  exit 1
}
```

## Examples of Great Changelogs

**Open Source Projects**:
- **Rust**: https://github.com/rust-lang/rust/blob/master/RELEASES.md
- **React**: https://github.com/facebook/react/blob/main/CHANGELOG.md
- **Next.js**: https://github.com/vercel/next.js/releases
- **fastify**: https://github.com/fastify/fastify/blob/main/CHANGELOG.md

## Changelog Success Criteria

**A great changelog enables readers to**:

1. [OK] Understand what changed in 30 seconds
2. [OK] Identify breaking changes immediately
3. [OK] Find relevant issues/PRs for more context
4. [OK] Decide whether to upgrade
5. [OK] Plan migration for breaking changes
6. [OK] Trust the project is actively maintained

**Quality metrics**:
- Completeness: All notable changes documented
- Clarity: Changes easy to understand
- Consistency: Follows Keep a Changelog format
- Traceability: Links to issues/commits
- Timeliness: Updated with every release
