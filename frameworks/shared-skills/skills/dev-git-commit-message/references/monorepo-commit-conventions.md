# Monorepo Commit Conventions

Commit message conventions for monorepo and multi-package repositories. Covers scope strategy, changelog generation per package, affected-package detection, and CI integration.

---

## Table of Contents

1. [Scope Strategy](#scope-strategy)
2. [Scope Granularity Decision Table](#scope-granularity-decision-table)
3. [Examples by Repo Structure](#examples-by-repo-structure)
4. [Changelog Generation per Package](#changelog-generation-per-package)
5. [Affected Package Detection](#affected-package-detection)
6. [Breaking Changes Across Packages](#breaking-changes-across-packages)
7. [CI Integration](#ci-integration)
8. [Common Monorepo Tools](#common-monorepo-tools)
9. [Do / Avoid](#do--avoid)
10. [Checklist: Monorepo Commit Review](#checklist-monorepo-commit-review)

---

## Scope Strategy

Monorepo commits must encode *where* the change happened so that tooling can route changelogs, trigger builds, and filter CI to the affected packages.

### Three Scope Levels

| Level | Format | When to Use |
|-------|--------|-------------|
| Package-level | `feat(packages/auth): ...` | Distinct publishable packages |
| Directory-level | `fix(apps/web): ...` | Apps or services within the repo |
| Feature-level | `feat(payments): ...` | Cross-cutting features spanning packages |

### Choosing a Scope Level

Use **package-level** scopes when:
- Packages are independently versioned and published
- Changelogs are generated per package
- CI pipelines run per package

Use **directory-level** scopes when:
- Repo has `apps/`, `packages/`, `services/` top-level directories
- Each directory maps to a deployable unit
- Teams own specific directories

Use **feature-level** scopes when:
- Changes span multiple packages but belong to one feature
- The repo does not publish packages independently
- Scopes map to product areas rather than file paths

---

## Scope Granularity Decision Table

| Repo Structure | Recommended Scope | Example |
|---|---|---|
| `packages/auth`, `packages/ui`, `packages/api` | Package name | `feat(auth): add OAuth2 flow` |
| `apps/web`, `apps/mobile`, `apps/admin` | App name | `fix(web): correct routing on 404` |
| `services/billing`, `services/notifications` | Service name | `perf(billing): cache invoice queries` |
| `libs/shared`, `libs/utils` | Lib name | `refactor(shared): extract date helpers` |
| Flat structure (no clear packages) | Feature area | `feat(search): add autocomplete` |
| `packages/` + `apps/` hybrid | Full path prefix | `fix(apps/web): correct CSP header` |

### Scope Naming Rules

- Lowercase, kebab-case: `feat(auth-service)` not `feat(AuthService)`
- Match directory names exactly when using path-based scopes
- Keep scope stable across the project lifetime (renaming scopes breaks changelog history)
- Document the scope map in the repo's contributing guide or commitlint config

---

## Examples by Repo Structure

### Turborepo / pnpm Workspaces

```text
feat(packages/auth): add OAuth2 PKCE flow
fix(packages/ui): correct button focus ring on Safari
chore(packages/config): update ESLint shared config
test(apps/web): add integration tests for checkout
ci(root): update GitHub Actions to Node 20
docs(packages/api): add OpenAPI schema for v2 endpoints
```

### Nx Workspace

```text
feat(libs/feature-dashboard): add analytics widget
fix(apps/admin): correct permission check on user list
refactor(libs/data-access-auth): simplify token refresh logic
build(workspace): update Nx to 17.x
```

### Lerna Monorepo

```text
feat(@acme/auth): add MFA enrollment endpoint
fix(@acme/ui): correct modal z-index stacking
chore(@acme/cli): bump commander to v12
```

When packages are npm-scoped (`@org/package`), the scope in the commit can use the short name without the org prefix: `feat(auth)` instead of `feat(@acme/auth)`, as long as the commitlint config maps `auth` to `@acme/auth`.

---

## Changelog Generation per Package

### Changesets (Recommended for Multi-Package)

```bash
npx changeset init

# After making changes, create a changeset
npx changeset
# Interactive prompt: select affected packages, bump type, summary

# On release branch
npx changeset version   # Updates package.json versions + CHANGELOG.md per package
npx changeset publish   # Publishes to npm
```

Changeset files live in `.changeset/` and describe the change independently from commit messages. This decouples changelog content from commit history.

### semantic-release with monorepo plugins

```js
// release.config.js (per package or root)
module.exports = {
  branches: ['main'],
  plugins: [
    ['@semantic-release/commit-analyzer', {
      preset: 'conventionalcommits',
      releaseRules: [
        { type: 'feat', release: 'minor' },
        { type: 'fix', release: 'patch' },
        { type: 'perf', release: 'patch' },
        { breaking: true, release: 'major' },
      ],
    }],
    ['@semantic-release/release-notes-generator', {
      preset: 'conventionalcommits',
    }],
    '@semantic-release/changelog',
    '@semantic-release/npm',
    '@semantic-release/github',
  ],
};
```

For monorepo support, use `semantic-release-monorepo` or `multi-semantic-release`:

```bash
npx multi-semantic-release
```

### lerna-changelog

```bash
npx lerna-changelog --from=v1.0.0 --to=v2.0.0
```

Generates a changelog grouped by PR labels. Works best with Lerna but requires GitHub PR labels to classify changes.

### Conventional Changelog (per package)

```bash
# Generate changelog for a specific package directory
npx conventional-changelog -p conventionalcommits -i packages/auth/CHANGELOG.md -s \
  --commit-path packages/auth
```

The `--commit-path` flag filters commits to those that touched the specified directory.

---

## Affected Package Detection

### From Commit Scope

Tools parse the commit scope to determine which packages were affected:

```text
feat(auth): add OAuth2 flow       -> packages/auth
fix(apps/web): correct routing    -> apps/web
chore(root): update tsconfig      -> root (all packages)
```

### From Changed Files

When scope is absent or insufficient, tools fall back to file path analysis:

```bash
# Nx: detect affected projects from git diff
npx nx affected:apps --base=main --head=HEAD
npx nx affected:libs --base=main --head=HEAD

# Turborepo: filter by changed packages
npx turbo run build --filter='...[HEAD^1]'

# pnpm: list changed packages
pnpm -r --filter '...[HEAD~1]' exec pwd
```

### Combining Scope and File Detection

The most reliable approach uses both:

1. Parse commit scope for explicit package targeting
2. Cross-reference with `git diff --name-only` for validation
3. Flag mismatches (scope says `auth` but files changed in `billing`)

---

## Breaking Changes Across Packages

### Single-Package Breaking Change

```text
feat(auth)!: replace session tokens with JWT

BREAKING CHANGE: All consumers of @acme/auth must update their
token validation logic. Session-based auth is removed.
```

### Cross-Package Breaking Change

When a breaking change in one package forces changes in dependent packages:

```text
feat(auth)!: change TokenPayload interface

BREAKING CHANGE: TokenPayload.userId is now a UUID string instead of
a number. Affected packages: @acme/api, @acme/admin, @acme/mobile.

Migration: Replace `user.id` (number) with `user.uuid` (string) in
all token consumers.
```

### Documenting Impact Scope

For cross-package breaks, list all affected packages in the commit body. This gives release tooling and human readers a clear blast radius.

```text
Affected packages:
- @acme/auth (source of change)
- @acme/api (consumes TokenPayload)
- @acme/admin (consumes TokenPayload)
- @acme/shared-types (type definition updated)
```

---

## CI Integration

### Run Tests Only for Affected Packages

```yaml
# GitHub Actions with Nx
- name: Determine affected packages
  run: echo "AFFECTED=$(npx nx show projects --affected --base=origin/main)" >> $GITHUB_ENV

- name: Test affected
  run: npx nx affected -t test --base=origin/main
```

```yaml
# GitHub Actions with Turborepo
- name: Test changed packages
  run: npx turbo run test --filter='...[origin/main]'
```

### Scope-Based Pipeline Routing

```yaml
# GitHub Actions: trigger package-specific workflows based on paths
on:
  push:
    paths:
      - 'packages/auth/**'
jobs:
  test-auth:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: cd packages/auth && npm test
```

### Commit Scope Validation in CI

```yaml
# Validate that the commit scope matches a known package
- name: Validate commit scope
  run: |
    SCOPE=$(echo "${{ github.event.head_commit.message }}" | grep -oP '\(\K[^)]+')
    KNOWN_SCOPES="auth ui api config apps/web apps/admin root"
    if [[ ! " $KNOWN_SCOPES " =~ " $SCOPE " ]]; then
      echo "Unknown scope: $SCOPE"
      exit 1
    fi
```

---

## Common Monorepo Tools

| Tool | Scope Detection | Affected Packages | Changelog Per Package | Package Publishing |
|------|----------------|-------------------|-----------------------|-------------------|
| Nx | File paths + project graph | `nx affected` | Via plugins | Via plugins |
| Turborepo | File paths + `turbo.json` | `--filter='...[ref]'` | Via changesets | Manual or changesets |
| Lerna | Package directories | `lerna changed` | `lerna-changelog` | `lerna publish` |
| pnpm workspaces | Workspace protocol | `--filter` with git ranges | Via changesets | `pnpm -r publish` |
| Changesets | Explicit declaration | Changeset files | Built-in per package | `changeset publish` |
| Rush | Rush project config | `rush change` | `rush publish` | `rush publish` |

---

## Do / Avoid

### Do

- Define a scope map and enforce it with commitlint
- Use package-level scopes for independently published packages
- Generate changelogs per package using `--commit-path` or changesets
- Include affected package lists in cross-package breaking changes
- Validate commit scopes against known packages in CI
- Use `root` or `workspace` scope for changes that affect the entire repo (CI configs, root tsconfig, tooling)

### Avoid

- Omitting scope entirely in monorepo commits (breaks per-package filtering)
- Using inconsistent scope formats (`auth` vs `packages/auth` vs `@acme/auth` in the same repo)
- Committing cross-package changes without listing the impact scope
- Nesting scopes (`feat(packages/auth/middleware)`) -- keep scopes to one level
- Changing scope names after release tooling depends on them
- Using feature-level scopes in repos that need per-package changelogs

---

## Checklist: Monorepo Commit Review

- [ ] Commit scope matches a package, app, or service directory name
- [ ] Scope is documented in the project's commitlint config or contributing guide
- [ ] Cross-package breaking changes list all affected packages in the body
- [ ] One logical change per commit (not mixing changes across unrelated packages)
- [ ] Changelog tooling can parse the scope to route entries to the correct package
- [ ] CI is configured to use scope or file paths for affected-package detection
- [ ] Root/workspace changes use a `root` or `workspace` scope

---

## Cross-References

- [conventional-commits-guide.md](conventional-commits-guide.md) -- Base format spec, type definitions, scope guidelines
- [commit-message-antipatterns.md](commit-message-antipatterns.md) -- Generic messages and mixed-concern anti-patterns
- [changelog-generation-guide.md](changelog-generation-guide.md) -- Changelog tools, configuration, and CI integration
