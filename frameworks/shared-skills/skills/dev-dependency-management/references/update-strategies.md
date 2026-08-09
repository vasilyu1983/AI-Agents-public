# Dependency Update Strategies

**Freshness anchor:** June 2026. Safe update policy is about batch size, reviewability, and rollback, not just how often a bot opens PRs.

## Table of Contents

- [Default Cadence](#default-cadence)
- [Strategy Options](#strategy-options)
- [Continuous](#continuous)
- [Scheduled](#scheduled)
- [Security-first](#security-first)
- [Practical Workflow](#practical-workflow)
- [1. Discover available updates](#1-discover-available-updates)
- [Node.js](#nodejs)
- [Python](#python)
- [Rust / Go / .NET / PHP](#rust-go-net-php)
- [2. Batch by risk](#2-batch-by-risk)
- [3. Review release notes](#3-review-release-notes)
- [4. Rebuild from exact lock state](#4-rebuild-from-exact-lock-state)
- [5. Validate and ship](#5-validate-and-ship)
- [Bot Policy](#bot-policy)
- [Dependabot](#dependabot)
- [Renovate](#renovate)
- [Rollback Rule](#rollback-rule)
- [Anti-Patterns](#anti-patterns)

## Default Cadence

| Update type | Default cadence | Handling |
|-------------|-----------------|----------|
| Critical security | Same day when exploitable in production | Isolate, patch, verify, deploy |
| High security | Within SLA, usually within a week | Isolate or group narrowly |
| Patch | Weekly or bi-weekly | Group by ecosystem or dependency family |
| Minor | Monthly | Batch carefully, test thoroughly |
| Major | Planned work | One family at a time with rollback path |

## Strategy Options

### Continuous

Best for:

- libraries
- platform teams with strong CI
- repos that already keep PRs small

Tradeoff:

- lower drift, more frequent review

### Scheduled

Best for:

- applications with staged releases
- teams that want predictable dependency windows

Tradeoff:

- larger batches, clearer planning

### Security-first

Best for:

- high-risk or under-tested systems
- legacy systems where broad upgrades are too risky

Tradeoff:

- less noise now, more migration debt later

## Practical Workflow

### 1. Discover available updates

```bash
# Node.js
npm outdated
pnpm outdated -r
yarn outdated
bun outdated

# Python
uv tree --outdated
poetry show --latest

# Rust / Go / .NET / PHP
cargo outdated
go list -u -m all
dotnet list package --outdated
composer outdated
```

### 2. Batch by risk

Low risk:

- patch updates
- internal packages
- dev tooling

Medium risk:

- runtime library minor updates
- framework-adjacent tooling

High risk:

- major versions
- auth, crypto, database drivers, ORMs
- build tooling or package-manager migrations

### 3. Review release notes

Always review release notes or migration docs for:

- major updates
- framework families
- security-related fixes that change defaults
- dependencies with install/build scripts

### 4. Rebuild from exact lock state

Use the exact install command for the ecosystem before testing:

- `npm ci`
- `pnpm install --frozen-lockfile`
- `yarn install --immutable`
- `bun ci`
- `uv sync --frozen`
- `poetry sync`
- `cargo build --locked`

### 5. Validate and ship

- run tests and type checks
- verify startup/runtime behavior
- regenerate SBOM if the release artifact changes
- keep the rollback path explicit

## Bot Policy

### Dependabot

Use for:

- security updates
- grouped patch/minor dependency families
- cross-ecosystem groupings only where the deployment unit truly spans those ecosystems

### Renovate

Use for:

- finer package rules
- automerge of low-risk changes with guardrails
- lockfile maintenance windows
- package age policies like `minimumReleaseAge`

## Rollback Rule

Every dependency PR should have a simple rollback:

- revert the PR or commit
- restore the previous lock state
- redeploy the last known good artifact if needed

## Anti-Patterns

- updating everything to latest in one PR
- treating all security alerts as equally urgent without environment context
- mixing package-manager migration with ordinary version updates
- accepting broad lockfile churn without inspecting the transitive graph
