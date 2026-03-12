# Changelog Generation Guide

Generating changelogs from commit history using Conventional Commits. Covers tooling, configuration, output format, CI integration, manual overrides, and versioning automation.

---

## Table of Contents

1. [Tools Overview](#tools-overview)
2. [Setup: conventional-changelog](#setup-conventional-changelog)
3. [Setup: standard-version](#setup-standard-version)
4. [Setup: semantic-release](#setup-semantic-release)
5. [Setup: changesets](#setup-changesets)
6. [Output Format: Keep a Changelog](#output-format-keep-a-changelog)
7. [Customization](#customization)
8. [CI Integration](#ci-integration)
9. [Manual Overrides](#manual-overrides)
10. [Versioning Integration](#versioning-integration)
11. [Example Workflow](#example-workflow)
12. [Do / Avoid](#do--avoid)
13. [Checklist: Changelog Release](#checklist-changelog-release)

---

## Tools Overview

| Tool | Auto Version Bump | Auto Changelog | Auto Publish | Monorepo Support | Human Approval Step |
|------|-------------------|----------------|-------------|------------------|---------------------|
| conventional-changelog | No | Yes | No | Via `--commit-path` | N/A (generate only) |
| standard-version | Yes | Yes | No | Limited | Yes (review before push) |
| semantic-release | Yes | Yes | Yes | Via plugins | No (fully automated) |
| changesets | Yes | Yes | Yes | Built-in | Yes (changeset files) |

**Choosing a tool:**
- Need full automation with no human gate? Use **semantic-release**.
- Want to review changelog before release? Use **standard-version** or **changesets**.
- Need per-package changelogs in a monorepo? Use **changesets**.
- Only need changelog generation (no versioning)? Use **conventional-changelog** directly.

---

## Setup: conventional-changelog

The lowest-level tool. Generates a changelog from commit history without touching versions.

```bash
npm install --save-dev conventional-changelog-cli
```

Add to `package.json`:

```json
{
  "scripts": {
    "changelog": "conventional-changelog -p conventionalcommits -i CHANGELOG.md -s",
    "changelog:all": "conventional-changelog -p conventionalcommits -i CHANGELOG.md -s -r 0"
  }
}
```

- `-p conventionalcommits` selects the Conventional Commits preset
- `-i CHANGELOG.md` reads from and appends to the existing changelog
- `-s` writes output to the same file as input
- `-r 0` regenerates the entire changelog from all commits (not just since last tag)

### Per-Package Changelog (Monorepo)

```bash
conventional-changelog -p conventionalcommits -i packages/auth/CHANGELOG.md -s \
  --commit-path packages/auth
```

---

## Setup: standard-version

Handles version bumping + changelog generation + git tagging. Does not publish.

```bash
npm install --save-dev standard-version
```

```json
{
  "scripts": {
    "release": "standard-version",
    "release:minor": "standard-version --release-as minor",
    "release:major": "standard-version --release-as major",
    "release:dry": "standard-version --dry-run"
  }
}
```

Configuration via `.versionrc` or `.versionrc.json`:

```json
{
  "types": [
    { "type": "feat", "section": "Features" },
    { "type": "fix", "section": "Bug Fixes" },
    { "type": "perf", "section": "Performance" },
    { "type": "refactor", "section": "Refactoring", "hidden": true },
    { "type": "docs", "section": "Documentation", "hidden": true },
    { "type": "style", "hidden": true },
    { "type": "chore", "hidden": true },
    { "type": "test", "hidden": true },
    { "type": "ci", "hidden": true },
    { "type": "build", "hidden": true }
  ],
  "commitUrlFormat": "https://github.com/org/repo/commit/{{hash}}",
  "compareUrlFormat": "https://github.com/org/repo/compare/{{previousTag}}...{{currentTag}}"
}
```

Note: `standard-version` is in maintenance mode. The maintainers recommend migrating to `release-please` or `semantic-release` for new projects.

---

## Setup: semantic-release

Fully automated: analyzes commits, determines version, generates changelog, publishes, creates GitHub release.

```bash
npm install --save-dev semantic-release @semantic-release/changelog @semantic-release/git
```

`release.config.js`:

```js
module.exports = {
  branches: ['main'],
  plugins: [
    ['@semantic-release/commit-analyzer', {
      preset: 'conventionalcommits',
      releaseRules: [
        { type: 'feat', release: 'minor' },
        { type: 'fix', release: 'patch' },
        { type: 'perf', release: 'patch' },
        { type: 'revert', release: 'patch' },
        { breaking: true, release: 'major' },
      ],
    }],
    ['@semantic-release/release-notes-generator', {
      preset: 'conventionalcommits',
      presetConfig: {
        types: [
          { type: 'feat', section: 'Features' },
          { type: 'fix', section: 'Bug Fixes' },
          { type: 'perf', section: 'Performance' },
        ],
      },
    }],
    ['@semantic-release/changelog', { changelogFile: 'CHANGELOG.md' }],
    ['@semantic-release/git', {
      assets: ['CHANGELOG.md', 'package.json', 'package-lock.json'],
      message: 'chore(release): ${nextRelease.version} [skip ci]',
    }],
    '@semantic-release/github',
  ],
};
```

---

## Setup: changesets

Human-in-the-loop approach. Developers create changeset files describing their changes; the release process consumes them.

```bash
npx changeset init
```

### Creating a Changeset

```bash
npx changeset
# Prompts: which packages? major/minor/patch? summary?
```

This creates a markdown file in `.changeset/`:

```markdown
---
"@acme/auth": minor
"@acme/api": patch
---

Add OAuth2 PKCE flow to auth package. API package updated to
accept new token format.
```

### Consuming Changesets on Release

```bash
npx changeset version   # Bumps versions, writes CHANGELOGs, deletes consumed changesets
npx changeset publish   # Publishes to npm
```

---

## Output Format: Keep a Changelog

The [Keep a Changelog](https://keepachangelog.com/) format is the de facto standard. All major tools can produce it.

```markdown
# Changelog

## [2.1.0] - 2026-02-10

### Features

- **auth**: add OAuth2 PKCE flow ([#234](https://github.com/org/repo/pull/234))
- **search**: add full-text product search

### Bug Fixes

- **cart**: prevent negative quantity on item update ([#567](https://github.com/org/repo/issues/567))
- **checkout**: correct address validation for PO boxes

### Performance

- **images**: implement progressive JPEG loading

### BREAKING CHANGES

- **auth**: session-based tokens removed; migrate to JWT ([migration guide](./docs/migration-2.1.md))

## [2.0.1] - 2026-01-15

### Bug Fixes

- **api**: correct pagination offset calculation
```

### Standard Sections

| Section | Maps From | SemVer Impact |
|---------|-----------|---------------|
| Features | `feat` commits | Minor bump |
| Bug Fixes | `fix` commits | Patch bump |
| Performance | `perf` commits | Patch bump |
| BREAKING CHANGES | `!` or `BREAKING CHANGE` footer | Major bump |
| Documentation | `docs` commits | No bump (usually hidden) |
| Refactoring | `refactor` commits | No bump (usually hidden) |

---

## Customization

### Grouping by Type

Control which types appear and under what heading using `.versionrc` (standard-version) or `presetConfig` (semantic-release):

```json
{
  "types": [
    { "type": "feat", "section": "New Features" },
    { "type": "fix", "section": "Fixes" },
    { "type": "perf", "section": "Performance Improvements" },
    { "type": "refactor", "section": "Internal Changes", "hidden": false },
    { "type": "chore", "hidden": true },
    { "type": "docs", "hidden": true }
  ]
}
```

### Filtering by Scope

Hide internal-only changes from the public changelog:

```js
// release.config.js — custom transform
['@semantic-release/release-notes-generator', {
  preset: 'conventionalcommits',
  writerOpts: {
    transform: (commit, context) => {
      // Hide internal scopes from public changelog
      const internalScopes = ['deps', 'ci', 'infra', 'internal'];
      if (internalScopes.includes(commit.scope)) return;
      return commit;
    },
  },
}],
```

### Adding PR Links

Most tools support linking commits to PRs or issues:

```json
{
  "issueUrlFormat": "https://github.com/org/repo/issues/{{id}}",
  "commitUrlFormat": "https://github.com/org/repo/commit/{{hash}}",
  "userUrlFormat": "https://github.com/{{user}}"
}
```

---

## CI Integration

### Auto-Generate Changelog on Release

```yaml
# GitHub Actions: release on push to main
name: Release
on:
  push:
    branches: [main]
jobs:
  release:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
          persist-credentials: false
      - uses: actions/setup-node@v4
        with:
          node-version: 20
      - run: npm ci
      - name: Release
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          NPM_TOKEN: ${{ secrets.NPM_TOKEN }}
        run: npx semantic-release
```

### Changesets Bot (for PR-Based Workflow)

```yaml
# GitHub Actions: check for changeset in PRs
name: Changeset Check
on: pull_request
jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - uses: changesets/action@v1
        with:
          publish: npx changeset publish
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

---

## Manual Overrides

### Editing Generated Changelogs

After running `standard-version --dry-run` or `changeset version`:

1. Review the generated `CHANGELOG.md`
2. Edit entries for clarity, grammar, or context
3. Add migration notes under a `### Migration` subsection
4. Remove noise entries (internal refactors that leaked into public changelog)
5. Commit the edited changelog as part of the release commit

### Adding Migration Notes

```markdown
## [3.0.0] - 2026-02-10

### BREAKING CHANGES

- **auth**: replace API key auth with OAuth2 tokens

### Migration

To migrate from v2.x to v3.0:

1. Register your application at https://dashboard.example.com/oauth
2. Replace `X-API-Key` header with `Authorization: Bearer <token>`
3. Update SDK: `npm install @acme/sdk@3`

See [full migration guide](./docs/migration-v3.md).
```

### Overriding Version Bumps

When auto-detection gets it wrong:

```bash
# Force a specific version with standard-version
npx standard-version --release-as 2.0.0

# Force with semantic-release (via commit)
# Add a commit with BREAKING CHANGE footer to trigger major bump

# Force with changesets (edit the changeset file)
# Change "minor" to "major" in the changeset markdown frontmatter
```

---

## Versioning Integration

### How Commit Types Map to Version Bumps

```text
BREAKING CHANGE (in footer or !)  ->  MAJOR (3.0.0 -> 4.0.0)
feat                              ->  MINOR (3.0.0 -> 3.1.0)
fix, perf, revert                 ->  PATCH (3.0.0 -> 3.0.1)
docs, style, refactor, test,
chore, ci, build                  ->  No release (unless configured)
```

### Pre-release Versions

```bash
# standard-version
npx standard-version --prerelease alpha   # 1.0.0 -> 1.0.1-alpha.0

# semantic-release (branch-based)
# release.config.js
branches: [
  'main',
  { name: 'beta', prerelease: true },
  { name: 'alpha', prerelease: true },
]
```

---

## Example Workflow

End-to-end flow from commit to GitHub release:

```text
1. Developer commits:
   feat(auth): add OAuth2 PKCE flow
   fix(cart): prevent negative quantity

2. PR merged to main

3. CI triggers semantic-release:
   a. Analyze commits since last tag (v2.0.3)
   b. Determine bump: feat -> MINOR -> v2.1.0
   c. Generate changelog entries
   d. Update CHANGELOG.md
   e. Bump package.json to 2.1.0
   f. Create git tag v2.1.0
   g. Commit changelog + version files
   h. Create GitHub release with changelog body
   i. Publish to npm (if configured)

4. Result:
   - Git tag: v2.1.0
   - CHANGELOG.md updated with Features + Bug Fixes sections
   - GitHub release created with formatted notes
   - npm package published (optional)
```

---

## Do / Avoid

### Do

- Use Conventional Commits consistently so tooling can parse history
- Hide internal types (`chore`, `ci`, `style`) from public changelogs
- Review generated changelogs before publishing (even with automation)
- Include migration notes for breaking changes
- Link entries to PRs or issues for traceability
- Use `--dry-run` before actual releases to preview output
- Configure `fetch-depth: 0` in CI so the tool can read full git history

### Avoid

- Manually writing changelogs from scratch when commit history is conventional (let tools generate the first draft)
- Publishing changelogs that include internal noise (`chore(deps): bump lodash`)
- Running changelog generation without tags (tools need tags to determine ranges)
- Mixing changelog tools in the same repo (pick one and commit to it)
- Skipping the `BREAKING CHANGE` footer for breaking changes (tools miss the major bump)
- Using `[skip ci]` on release commits without understanding the downstream effects

---

## Checklist: Changelog Release

- [ ] All commits since last tag follow Conventional Commits format
- [ ] `git fetch --tags` run before generation (tags are up to date)
- [ ] Dry run reviewed: `npx standard-version --dry-run` or equivalent
- [ ] Generated entries are accurate and human-readable
- [ ] Internal changes (`chore`, `ci`, `docs`) hidden from public changelog
- [ ] Breaking changes have migration notes
- [ ] PR/issue links are present in entries
- [ ] Version bump is correct (major/minor/patch matches changes)
- [ ] Release commit does not trigger another CI release cycle (`[skip ci]` or conditional)
- [ ] GitHub release created with changelog body

---

## Cross-References

- [conventional-commits-guide.md](conventional-commits-guide.md) -- Format spec that changelog tools depend on
- [commit-message-antipatterns.md](commit-message-antipatterns.md) -- Anti-patterns that break changelog generation
- [monorepo-commit-conventions.md](monorepo-commit-conventions.md) -- Per-package changelog strategies for monorepos
