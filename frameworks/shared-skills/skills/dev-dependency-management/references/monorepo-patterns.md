# Monorepo Dependency Patterns

**Freshness anchor:** June 2026. Monorepo advice should be workspace-first, lockfile-aware, and explicit about polyglot boundaries.

## Table of Contents

- [When a Monorepo Fits](#when-a-monorepo-fits)
- [Default JS/TS Pattern](#default-jsts-pattern)
- [Recommended baseline](#recommended-baseline)
- [Example root files](#example-root-files)
- [Useful commands](#useful-commands)
- [pnpm-Specific Safety Features](#pnpm-specific-safety-features)
- [Yarn 4 Pattern](#yarn-4-pattern)
- [Polyglot Monorepos](#polyglot-monorepos)
- [Recommended structure](#recommended-structure)
- [Rules](#rules)
- [Version Governance](#version-governance)
- [Update Strategy In Monorepos](#update-strategy-in-monorepos)
- [Review Checklist](#review-checklist)
- [Anti-Patterns](#anti-patterns)

## When a Monorepo Fits

Good fit:

- multiple deployables share libraries, tooling, or release cadence
- changes regularly span packages together
- the team wants one dependency policy and one CI control plane

Bad fit:

- unrelated products with independent release and ownership models
- teams that only want repo colocation with no shared graph or workflow
- ecosystems that should remain isolated for compliance or operational reasons

## Default JS/TS Pattern

### Recommended baseline

- **pnpm workspaces** for package management
- **one root lockfile** per JS/TS workspace
- **pinned `packageManager`** in root `package.json`
- **Nx or Turborepo** only when task graph caching is worth the added surface area

### Example root files

```json
{
  "name": "acme-monorepo",
  "private": true,
  "packageManager": "pnpm@<current-major>",  // pin to current major from https://pnpm.io/
  "workspaces": [
    "apps/*",
    "packages/*"
  ]
}
```

```yaml
packages:
  - "apps/*"
  - "packages/*"
```

### Useful commands

```bash
pnpm install --frozen-lockfile
pnpm -r test
pnpm --filter @acme/web build
pnpm --filter "...[origin/main]" test
```

## pnpm-Specific Safety Features

Use when the repo has a stronger supply-chain posture:

```yaml
minimumReleaseAge: 1440
onlyBuiltDependencies:
  - esbuild
  - sharp
```

Operational notes:

- `minimumReleaseAge` delays adoption of freshly published packages
- `approve-builds` helps populate build-script allowlists
- keep allowlists short and reviewed

## Yarn 4 Pattern

Use Yarn 4 workspaces when the repo already depends on:

- Plug'n'Play
- constraints
- zero-installs

Core rule:

```bash
yarn install --immutable
```

Do not write new generic monorepo guidance using Yarn Classic terminology.

## Polyglot Monorepos

### Recommended structure

- keep one lockfile per ecosystem root
- keep package-manager boundaries obvious
- keep shared CI conventions, not forced shared package-manager semantics

Example:

```text
repo/
├── apps/
│   ├── web/              # pnpm workspace member
│   └── api/              # pnpm workspace member
├── services/
│   └── billing/          # Python root with uv.lock or poetry.lock
├── crates/
│   └── worker/           # Rust root with Cargo.toml
└── infra/
    └── terraform/
```

### Rules

- do not try to collapse Python, Rust, and Node into one fake lockfile model
- do centralize review policy, CI gating, and vulnerability triage
- do separate ecosystem-specific updates unless the deployment unit truly requires one grouped change

## Version Governance

Use centralization where the ecosystem supports it:

- npm/pnpm/Yarn workspace root dev tooling
- Maven BOMs
- Gradle version catalogs
- NuGet `Directory.Packages.props`

Use it to reduce drift, not to force every package to move in lockstep when that would increase blast radius.

## Update Strategy In Monorepos

- group low-risk dev-tool updates
- isolate major framework migrations
- keep runtime dependency changes small for high-traffic apps
- regenerate only the lockfiles that actually belong to the changed ecosystem root

## Review Checklist

- Is the change scoped to the correct workspace or ecosystem root?
- Did the update modify only the expected lockfile?
- Did any new install/build scripts appear?
- Does the task runner cache remain valid after the dependency change?
- Does the PR mix package-manager migration with regular upgrades?

## Anti-Patterns

- global `npm install -g pnpm` as the only bootstrap story for every repo
- one PR that upgrades every workspace and every ecosystem at once
- multiple active Node lockfiles in one workspace root
- forcing a monorepo when the teams do not share code or release motion
