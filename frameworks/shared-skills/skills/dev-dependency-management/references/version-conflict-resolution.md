# Version Conflict Resolution

> Operational reference for diagnosing and resolving dependency version conflicts across package managers. Covers diamond dependencies, peer mismatches, resolution algorithms, forced overrides, and prevention patterns.

**Freshness anchor:** June 2026 — verify current package-manager diagnostics and resolution behavior before recommending fixes.

---
## Table of Contents

- [Conflict Types Quick Reference](#conflict-types-quick-reference)
- [Diagnostic Commands](#diagnostic-commands)
- [npm](#npm)
- [View full dependency tree](#view-full-dependency-tree)
- [Find why a specific package is installed](#find-why-a-specific-package-is-installed)
- [Alias: npm why <package>](#alias-npm-why-package)
- [List duplicate packages](#list-duplicate-packages)
- [Check for peer dependency issues](#check-for-peer-dependency-issues)
- [View resolved versions](#view-resolved-versions)
- [Audit for conflicts during install](#audit-for-conflicts-during-install)
- [pnpm](#pnpm)
- [View dependency tree](#view-dependency-tree)
- [Why is a package installed](#why-is-a-package-installed)
- [List all versions of a package in the project](#list-all-versions-of-a-package-in-the-project)
- [Check for peer dependency issues](#check-for-peer-dependency-issues)
- [Yarn (v4 Berry)](#yarn-v4-berry)
- [View dependency tree](#view-dependency-tree)
- [Why is a package installed](#why-is-a-package-installed)
- [List duplicates](#list-duplicates)
- [Explain resolution](#explain-resolution)
- [pip](#pip)
- [Check for conflicts](#check-for-conflicts)
- [Show dependency tree (requires pipdeptree)](#show-dependency-tree-requires-pipdeptree)
- [Show reverse dependencies](#show-reverse-dependencies)
- [Verbose install to see resolution](#verbose-install-to-see-resolution)
- [Cargo (Rust)](#cargo-rust)
- [View dependency tree](#view-dependency-tree)
- [Find duplicates](#find-duplicates)
- [Why is a package included](#why-is-a-package-included)
- [View feature flags](#view-feature-flags)
- [Go Modules](#go-modules)
- [View module graph](#view-module-graph)
- [Why is a module required](#why-is-a-module-required)
- [Tidy unused dependencies](#tidy-unused-dependencies)
- [View effective versions](#view-effective-versions)
- [Resolution Algorithm Differences](#resolution-algorithm-differences)
- [Decision Tree: Choosing Resolution Strategy](#decision-tree-choosing-resolution-strategy)
- [Forced Resolution Strategies](#forced-resolution-strategies)
- [npm overrides](#npm-overrides)
- [pnpm overrides](#pnpm-overrides)
- [Yarn resolutions](#yarn-resolutions)
- [pip constraints](#pip-constraints)
- [constraints.txt](#constraintstxt)
- [Cargo patch](#cargo-patch)
- [Cargo.toml](#cargotoml)
- [Use a fixed fork](#use-a-fixed-fork)
- [Use local path during development](#use-local-path-during-development)
- [Go replace](#go-replace)
- [Diamond Dependency Resolution](#diamond-dependency-resolution)
- [Diagnosis Workflow](#diagnosis-workflow)
- [Singleton Libraries (Cannot Duplicate)](#singleton-libraries-cannot-duplicate)
- [Conflict Prevention Patterns](#conflict-prevention-patterns)
- [Proactive Measures](#proactive-measures)
- [Lockfile Hygiene](#lockfile-hygiene)
- [Monorepo-Specific Strategies](#monorepo-specific-strategies)
- [pnpm Catalogs (Monorepo Version Alignment)](#pnpm-catalogs-monorepo-version-alignment)
- [pnpm-workspace.yaml](#pnpm-workspaceyaml)
- [Debugging Workflow: Step-by-Step](#debugging-workflow-step-by-step)
- ["It works locally but not in CI"](#it-works-locally-but-not-in-ci)
- ["Package X breaks after updating Package Y"](#package-x-breaks-after-updating-package-y)
- [Anti-Patterns](#anti-patterns)
- [Cross-References](#cross-references)


## Conflict Types Quick Reference

| Conflict Type | Description | Severity | Example |
|---|---|---|---|
| Diamond dependency | A depends on C@1.x; B depends on C@2.x | High | `react-dom` needs `react@18`, plugin needs `react@17` |
| Peer dependency mismatch | Package declares peer dep not met by consumer | Medium | `eslint-plugin-react` requires `eslint@^8`, project has `eslint@9` |
| Version range incompatibility | Overlapping ranges have no intersection | High | `^1.2.0` vs `~1.1.5` with no shared version |
| Duplicate packages | Same package at different versions in tree | Low-Medium | Two copies of `lodash` bundled |
| Transitive conflict | Indirect deps create version collision | High | Sub-dependency of sub-dependency has conflict |
| Platform/engine mismatch | Package requires different Node/Python/OS | Medium | `engines: { node: ">=20" }` with Node 18 |

---

## Diagnostic Commands

### npm

```bash
# View full dependency tree
npm ls

# Find why a specific package is installed
npm explain <package>
# Alias: npm why <package>

# List duplicate packages
npm ls --all | grep "deduped"

# Check for peer dependency issues
npm ls 2>&1 | grep "ERESOLVE\|peer dep\|invalid"

# View resolved versions
npm ls <package> --all

# Audit for conflicts during install
npm install --dry-run 2>&1
```

### pnpm

```bash
# View dependency tree
pnpm ls --depth Infinity

# Why is a package installed
pnpm why <package>

# List all versions of a package in the project
pnpm ls <package> --depth Infinity

# Check for peer dependency issues
pnpm install --fix-lockfile 2>&1
```

### Yarn (v4 Berry)

```bash
# View dependency tree
yarn info --all --dependents

# Why is a package installed
yarn why <package>

# List duplicates
yarn dedupe --check

# Explain resolution
yarn explain peer-requirements
```

### pip

```bash
# Check for conflicts
pip check

# Show dependency tree (requires pipdeptree)
pipdeptree --warn fail

# Show reverse dependencies
pipdeptree --reverse --packages <package>

# Verbose install to see resolution
pip install --dry-run -v <package>
```

### Cargo (Rust)

```bash
# View dependency tree
cargo tree

# Find duplicates
cargo tree --duplicates

# Why is a package included
cargo tree --invert <package>

# View feature flags
cargo tree --edges features
```

### Go Modules

```bash
# View module graph
go mod graph

# Why is a module required
go mod why <module>

# Tidy unused dependencies
go mod tidy

# View effective versions
go list -m all
```

---

## Resolution Algorithm Differences

| Manager | Strategy | Hoisting | Lockfile | Peer Dep Handling |
|---|---|---|---|---|
| npm | Nested with hoisting | Yes (flat by default) | `package-lock.json` | Warning, auto-install in v7+ |
| pnpm | Content-addressable store + symlinks | No (strict by default) | `pnpm-lock.yaml` | Strict by default, error on mismatch |
| Yarn Berry | Plug'n'Play (no `node_modules`) or node_modules | Configurable | `yarn.lock` | Configurable strictness |
| pip | Latest compatible version, backtracking | N/A (flat install) | `requirements.txt` / `poetry.lock` | N/A |
| Cargo | SemVer-compatible unification | N/A | `Cargo.lock` | N/A (feature unification) |
| Go | Minimum version selection (MVS) | N/A | `go.sum` | N/A |

### Decision Tree: Choosing Resolution Strategy

```
What package manager are you using?
├── npm
│   └── Conflict on install?
│       ├── Peer dep warning → Check if compatible, use --legacy-peer-deps as last resort
│       └── ERESOLVE error → Use overrides in package.json
├── pnpm
│   └── Strict mode failing?
│       ├── Peer dep → Add to peerDependencyRules in .npmrc
│       └── Version conflict → Use pnpm.overrides
├── Yarn Berry
│   └── Use resolutions in package.json
├── pip
│   └── Use pip-compile with constraints file
├── Cargo
│   └── Use [patch] section in Cargo.toml
└── Go
    └── Use replace directive in go.mod
```

---

## Forced Resolution Strategies

### npm overrides

```json
{
  "overrides": {
    "lodash": "4.17.21",
    "react": "$react",
    "some-package": {
      "vulnerable-dep": "2.0.1"
    }
  }
}
```

- `"$react"` references the version declared in top-level `dependencies`
- Nested overrides target specific dependency paths
- Use sparingly — overrides bypass semver safety

### pnpm overrides

```json
{
  "pnpm": {
    "overrides": {
      "lodash": "4.17.21",
      "foo>bar": "2.0.0"
    },
    "peerDependencyRules": {
      "ignoreMissing": ["@babel/*"],
      "allowedVersions": {
        "react": "18"
      }
    }
  }
}
```

### Yarn resolutions

```json
{
  "resolutions": {
    "lodash": "4.17.21",
    "package-a/lodash": "4.17.21",
    "**/@types/node": "22.0.0"
  }
}
```

### pip constraints

```bash
# constraints.txt
cryptography==43.0.0
requests>=2.31.0,<3.0.0
```

```bash
pip install -c constraints.txt -r requirements.txt
```

### Cargo patch

```toml
# Cargo.toml
[patch.crates-io]
# Use a fixed fork
some-crate = { git = "https://github.com/user/some-crate", branch = "fix" }
# Use local path during development
some-crate = { path = "../some-crate" }
```

### Go replace

```go
// go.mod
replace (
    example.com/broken/module v1.0.0 => example.com/fixed/module v1.1.0
    example.com/local/module => ../local-module
)
```

---

## Diamond Dependency Resolution

### Diagnosis Workflow

```
Two or more packages require different versions of the same dependency
│
├── Step 1: Identify the conflicting versions
│   └── npm: `npm explain <package>`
│   └── pnpm: `pnpm why <package>`
│
├── Step 2: Check if ranges overlap
│   ├── YES (ranges overlap) → Deduplicate
│   │   └── npm: `npm dedupe`
│   │   └── Yarn: `yarn dedupe`
│   └── NO (ranges incompatible) → Continue
│
├── Step 3: Can either dependent package be updated?
│   ├── YES → Update to version with compatible range
│   └── NO → Continue
│
├── Step 4: Is the conflicting package side-effect-free?
│   ├── YES → Allow duplicate versions (npm does this by default)
│   └── NO (e.g., React, singleton libraries) → Continue
│
└── Step 5: Force resolution
    ├── Use overrides/resolutions to pin single version
    ├── Test thoroughly — forced version may break dependents
    └── Document override with reason and review date
```

### Singleton Libraries (Cannot Duplicate)

| Library | Why singleton | Symptom of duplication |
|---|---|---|
| React | Hooks require single instance | "Invalid hook call" error |
| Angular | DI container must be single | "Multiple platforms" error |
| Webpack | Plugin system assumes single | Build errors, duplicate modules |
| styled-components | Theme context must be single | Styles not applying |

---

## Conflict Prevention Patterns

### Proactive Measures

- [ ] Pin exact versions in production applications (`"lodash": "4.17.21"`)
- [ ] Use ranges in libraries (`"lodash": "^4.17.0"`)
- [ ] Run `npm ls` / `pnpm why` in CI to detect new duplicates
- [ ] Renovate/Dependabot configured with grouping for related packages
- [ ] Lockfile committed and reviewed in PRs
- [ ] `engines` field set in `package.json` to prevent Node.js mismatches
- [ ] `.npmrc` configured with `strict-peer-dependencies=true` (pnpm)
- [ ] Regular deduplication runs (`npm dedupe`, `yarn dedupe`)

### Lockfile Hygiene

| Action | When | Command |
|---|---|---|
| Regenerate lockfile | After major upgrades | Delete lockfile, run install |
| Deduplicate | After adding new deps | `npm dedupe` / `yarn dedupe` |
| Audit lockfile diff | Every PR | Review lockfile changes in code review |
| Verify integrity | CI pipeline | `npm ci` (fails if lockfile out of sync) |

### Monorepo-Specific Strategies

| Tool | Strategy | Config |
|---|---|---|
| npm workspaces | Hoisted shared deps | `workspaces` in root `package.json` |
| pnpm workspaces | Strict isolation with catalog | `pnpm-workspace.yaml` + `catalogs` |
| Yarn workspaces | PnP with shared deps | `workspaces` in root `package.json` |
| Nx / Turborepo | Single version policy | Root `package.json` manages all versions |

### pnpm Catalogs (Monorepo Version Alignment)

```yaml
# pnpm-workspace.yaml
packages:
  - "packages/*"

catalogs:
  default:
    react: ^18.3.0
    react-dom: ^18.3.0
    typescript: ^5.6.0
```

```json
// packages/app/package.json
{
  "dependencies": {
    "react": "catalog:default"
  }
}
```

---

## Debugging Workflow: Step-by-Step

### "It works locally but not in CI"

```
1. Compare lockfile: is CI using the same lockfile as local?
   └── CI must use `npm ci` (not `npm install`)

2. Compare Node.js/runtime version
   └── Pin in `.nvmrc`, `.node-version`, or `engines`

3. Compare registry: is CI using a private registry?
   └── Check `.npmrc` for registry overrides

4. Clean local state and reproduce
   └── rm -rf node_modules && npm ci
```

### "Package X breaks after updating Package Y"

```
1. Check if X and Y share a transitive dependency
   └── npm explain <shared-dep>

2. Compare resolved versions before and after
   └── git diff package-lock.json | grep <shared-dep>

3. Check if shared dep had a breaking change
   └── Review changelog of shared dep

4. Resolution:
   ├── Pin shared dep to previous working version via overrides
   ├── OR update X to version compatible with new shared dep
   └── OR open issue upstream
```

---

## Anti-Patterns

| Anti-Pattern | Problem | Fix |
|---|---|---|
| `--legacy-peer-deps` as default | Hides real conflicts, causes runtime errors | Fix peer deps properly, use as last resort |
| `--force` on every install | Bypasses all safety checks | Investigate and resolve the actual conflict |
| Not committing lockfiles | Non-reproducible builds | Always commit lockfiles for applications |
| Overrides without documentation | Future maintainers don't know why | Add comment with reason and review date |
| Ignoring duplicate warnings | Larger bundles, potential runtime bugs | Run dedupe, investigate singletons |
| Manual lockfile editing | Corruption, desync | Use CLI commands, never hand-edit lockfiles |
| Pinning everything in libraries | Prevents consumers from deduplicating | Use ranges in libraries, pin in applications |
| Updating all deps at once | Hard to isolate breakage | Update in small batches, test between each |
| No `engines` field | Works on dev's Node 22, breaks on CI's Node 18 | Declare minimum engine requirements |

---

## Cross-References

- `dev-dependency-management/references/container-dependency-patterns.md` — lockfiles in Docker builds
- `dev-dependency-management/references/license-compliance.md` — scanning resolved dependency trees
- `software-clean-code-standard/references/code-complexity-metrics.md` — dependency complexity as a metric
- `software-backend/references/nodejs-best-practices.md` — Node.js-specific dependency management
- `qa-refactoring/references/strangler-fig-migration.md` — managing deps during incremental migration
