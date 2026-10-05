# Dependency Management by Ecosystem

Verify CLI flags and feature support against official docs before giving "best tool" recommendations.

## Table of Contents

- [Node.js](#nodejs)
- [Package Manager Selection](#package-manager-selection)
- [Defaults](#defaults)
- [Operational rules](#operational-rules)
- [Pin package manager in package.json](#pin-package-manager-in-packagejson)
- [CI installs](#ci-installs)
- [Security-specific notes](#security-specific-notes)
- [Recommendation boundaries](#recommendation-boundaries)
- [Python](#python)
- [Tool Selection](#tool-selection)
- [Defaults](#defaults)
- [Operational rules](#operational-rules)
- [uv](#uv)
- [Poetry](#poetry)
- [pip-tools](#pip-tools)
- [Packaging guidance](#packaging-guidance)
- [Rust](#rust)
- [Defaults](#defaults)
- [Useful commands](#useful-commands)
- [Notes](#notes)
- [Go](#go)
- [Defaults](#defaults)
- [Useful commands](#useful-commands)
- [Notes](#notes)
- [Java](#java)
- [Maven](#maven)
- [Gradle](#gradle)
- [Notes](#notes)
- [.NET](#net)
- [Defaults](#defaults)
- [Useful commands](#useful-commands)
- [PHP](#php)
- [Defaults](#defaults)
- [Useful commands](#useful-commands)
- [Cross-Ecosystem Rules](#cross-ecosystem-rules)
- [1. Pin the toolchain](#1-pin-the-toolchain)
- [2. Install from lock state in CI](#2-install-from-lock-state-in-ci)
- [3. Keep one source of truth](#3-keep-one-source-of-truth)
- [4. Separate dependency work by risk](#4-separate-dependency-work-by-risk)
- [Anti-Patterns To Avoid](#anti-patterns-to-avoid)

## Node.js

### Package Manager Selection

| Tool | Prefer it when | Lockfile | CI install | Main watchouts |
|------|----------------|----------|------------|----------------|
| **pnpm** | New repos, workspaces, strict dependency isolation | `pnpm-lock.yaml` | `pnpm install --frozen-lockfile` | Majors change runtime requirements and workspace settings (pnpm 11 replaced `onlyBuiltDependencies` with `allowBuilds`; pnpm 12 rejects or warns on unrecognized workspace settings); read the release notes of the major you adopt and verify CI compatibility |
| **npm** | Compatibility-first repos and tooling expectations | `package-lock.json` | `npm ci` | Before upgrading, read the target major's [configuration docs](https://docs.npmjs.com/cli/using-npm/config) and [release notes](https://github.com/npm/cli/releases) for lifecycle-script approvals and git/remote dependency defaults; test required native builds and sources in CI |
| **Yarn 4** | Existing Berry/PnP/constraints/zero-install repos | `yarn.lock` | `yarn install --immutable` | Avoid mixing Berry guidance with Yarn Classic docs |
| **Bun** | Bun-first runtime or validated Bun toolchains | `bun.lock` | `bun ci` | Node.js compatibility is incomplete — verify the specific APIs your repo depends on before migrating |

### Defaults

- Default new repo: **pnpm**; look up its release channels with `npm view pnpm dist-tags`, because a new major can ship on a non-default tag before it becomes the default install
- Pin the manager with `packageManager` in `package.json`
- Prefer **Corepack-managed** package-manager versions over ad-hoc global installs
- Keep exactly one lockfile for the active Node package manager
- pnpm 11+ security defaults are tighter out of the box; migrate `onlyBuiltDependencies`/`ignoredBuiltDependencies` to the `allowBuilds` map and review `approve-builds` behavior after upgrading
- For npm upgrades, check the target version's script-approval and dependency-source settings in the primary docs linked above. Review each required approval and test it in CI rather than enabling all scripts.

### Operational rules

```bash
# Pin package manager in package.json
{
  "packageManager": "pnpm@<major.minor.patch>"  # pin the exact version the team has validated
}

# CI installs
npm ci
pnpm install --frozen-lockfile
yarn install --immutable
bun ci
```

### Security-specific notes

- `npm audit` checks known vulnerabilities; registry-signature and provenance verification is the separate `npm audit signatures` command — run both, and do not treat either as your only control
- `npm sbom` can generate an SPDX SBOM directly from the npm graph
- pnpm adds useful supply-chain controls in workspace settings, especially `minimumReleaseAge`, `allowBuilds`, and `approve-builds`
- Bun has `bun audit`; use it if the repo is already on Bun instead of shelling out to npm just for auditing

### Recommendation boundaries

- Choose **pnpm** when the question is "what should we start with?"
- Choose **npm** when the question is "what minimizes migration risk?"
- Keep **Yarn 4** when the repo already depends on Berry features
- Choose **Bun** only when the runtime choice and package-manager choice are intentionally coupled

## Python

### Tool Selection

| Tool | Prefer it when | Lockfile | CI install | Main watchouts |
|------|----------------|----------|------------|----------------|
| **uv** | New apps, tools, CI speed, unified workflow | `uv.lock` | `uv sync --frozen` | Verify any missing workflow-specific plugin features before migration |
| **Poetry** | Established Poetry repo with team familiarity | `poetry.lock` | `poetry sync` | Avoid older docs that still describe sync as an install-time flag instead of a dedicated command |
| **pip-tools** | Conservative environments that want text lockfiles | compiled `requirements.txt` | `pip-sync` | Requires separate compile/sync flow |
| **conda / conda-lock** | Data science and binary-heavy stacks | `conda-lock.yml` or platform locks | environment-specific | Keep app and notebook workflows separate where possible |

### Defaults

- Default new repo: **uv**; check its release notes for whether it is still on 0.x versioning, and pin the uv version in CI because 0.x minor releases may change behavior
- Keep **Poetry** when the repo already uses Poetry well and migration value is unclear
- Prefer standardized metadata in `pyproject.toml`
- Use PyPA **Dependency Groups** where cross-tool interoperability matters
- Export or adopt **`pylock.toml`** when a standardized lock format is useful across tools

### Operational rules

```bash
# uv
uv lock
uv sync --frozen

# Poetry
poetry lock
poetry sync

# pip-tools
pip-compile pyproject.toml -o requirements.txt
pip-sync requirements.txt
```

### Packaging guidance

- Prefer `[project]` metadata over tool-only metadata when starting fresh
- Keep optional runtime extras separate from development/test groups
- Treat `requirements.txt` as a compiled artifact, not the hand-edited source of truth, when using pip-tools

## Rust

### Defaults

- Commit `Cargo.lock` for applications
- Use `cargo build --locked` in CI, release, and reproducibility-sensitive workflows
- Use `cargo update -p <crate>` for targeted updates

### Useful commands

```bash
cargo build --locked
cargo tree
cargo audit
```

### Notes

- Libraries often omit `Cargo.lock`, but follow repo policy rather than cargo folklore if the project standard differs
- Be cautious with feature unification and default features during upgrades

## Go

### Defaults

- Treat `go.mod` and `go.sum` as canonical
- Run `go mod tidy` after dependency edits
- Use `govulncheck ./...` for vulnerability scanning

### Useful commands

```bash
go mod tidy
go list -m all
govulncheck ./...
```

### Notes

- Use vendoring only when your build or compliance environment requires it
- Keep generated code and module updates separate in review when possible

## Java

### Maven

- Use the **Maven wrapper** (`./mvnw`) rather than assuming a global installation
- Centralize versions with dependency management and BOMs
- Inspect the graph with `./mvnw dependency:tree`

### Gradle

- Use the **Gradle wrapper** (`./gradlew`)
- Prefer version catalogs and dependency locking where appropriate
- Inspect the graph with `./gradlew dependencies`

### Notes

- For both Maven and Gradle, treat wrapper updates as supply-chain events and review them explicitly
- Do not mix generated lock-state changes with broad plugin upgrades in one PR

## .NET

### Defaults

- Prefer `PackageReference`
- Use `dotnet restore` and `dotnet list package --outdated` / `--vulnerable`
- Commit lock files only when repo policy requires deterministic restore lock mode

### Useful commands

```bash
dotnet restore
dotnet list package --outdated
dotnet list package --vulnerable --include-transitive
```

## PHP

### Defaults

- Commit `composer.lock` for applications
- Use `composer install --no-interaction --prefer-dist` in CI
- Audit plugins and scripts before allowing them in CI

### Useful commands

```bash
composer install --no-interaction --prefer-dist
composer update vendor/package
composer audit
```

## Cross-Ecosystem Rules

### 1. Pin the toolchain

- Pin package-manager and wrapper versions
- Prefer repo-local wrappers or toolchain files over "install latest" shell snippets

### 2. Install from lock state in CI

- Do not use mutable install commands in CI when an exact install command exists

### 3. Keep one source of truth

- One active package manager
- One lockfile per package graph
- One documented update policy

### 4. Separate dependency work by risk

- Patch and dev-tool updates together
- Security-sensitive runtime changes separately
- Major upgrades one family at a time

## Anti-Patterns To Avoid

- Recommending a package manager purely because it is "fastest"
- Using Yarn Classic docs to explain Yarn 4 behavior
- Recommending `npm install -g pnpm` as the default bootstrap path for every repo
- Treating `poetry install` and `poetry sync` as interchangeable in reproducibility-sensitive flows
- Assuming every ecosystem has npm-style lockfile semantics
