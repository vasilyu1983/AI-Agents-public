# Dependency Selection Guide

**Freshness anchor:** June 2026. Dependency selection should optimize for necessity, maintenance quality, graph size, and supply-chain posture rather than vanity metrics.

## Table of Contents

- [First Question: Do You Need A New Dependency?](#first-question-do-you-need-a-new-dependency)
- [Evaluation Criteria](#evaluation-criteria)
- [1. Necessity](#1-necessity)
- [2. Maintenance Quality](#2-maintenance-quality)
- [3. Graph Complexity](#3-graph-complexity)
- [Node.js](#nodejs)
- [Python](#python)
- [Rust](#rust)
- [4. Security And Supply Chain](#4-security-and-supply-chain)
- [Node.js](#nodejs)
- [Python](#python)
- [Rust](#rust)
- [5. Size And Runtime Cost](#5-size-and-runtime-cost)
- [Comparison Template](#comparison-template)
- [Ecosystem Examples](#ecosystem-examples)
- [Node.js](#nodejs)
- [Python](#python)
- [Java / .NET / PHP](#java-net-php)
- [AI-Suggested Dependencies](#ai-suggested-dependencies)
- [Red Flags](#red-flags)
- [Decision Rule](#decision-rule)

## First Question: Do You Need A New Dependency?

Ask in order:

1. Can the requirement be solved with the standard library?
2. Can the existing repo dependencies already solve it?
3. Is this actually a small utility that would be clearer in local code?
4. If a dependency is still justified, which option has the lowest long-term maintenance cost?

## Evaluation Criteria

### 1. Necessity

Strong reasons to add a dependency:

- protocol or file-format implementation that is difficult to recreate safely
- framework integration where ecosystem conventions matter
- well-maintained tooling that replaces substantial custom build or release code

Weak reasons:

- one-line helpers
- APIs already covered by modern runtime features
- "AI suggested it" without a concrete capability gap

### 2. Maintenance Quality

Prefer packages with:

- recent releases, not just recent commits
- active maintainers or an organization rather than a single abandoned repo
- clear changelogs and upgrade notes
- security policy or disclosure path
- reproducible release process or signed provenance where available

Avoid packages where:

- the release cadence has obviously stalled for the ecosystem they serve
- unresolved security issues are piling up
- transitive dependency count is unexpectedly large for the problem being solved
- ownership or maintainer changes look suspicious

### 3. Graph Complexity

Inspect the graph before adopting:

```bash
# Node.js
npm ls <package>
pnpm why <package>
yarn why <package>

# Python
pipdeptree -p <package>

# Rust
cargo tree -p <crate>
```

Prefer the package that:

- solves the problem with fewer transitive dependencies
- does not add conflicting peer or optional runtime requirements
- does not introduce risky install/build scripts without a good reason

### 4. Security And Supply Chain

Review:

- vulnerability history
- package provenance and signatures if the ecosystem supports them
- use of lifecycle scripts, plugins, or postinstall hooks
- registry reputation and typosquatting risk

Minimum review:

```bash
# Node.js
npm audit --audit-level=high

# Python
pip-audit

# Rust
cargo audit
```

### 5. Size And Runtime Cost

For frontend or serverless-sensitive code paths, check:

- bundle size
- tree-shakeability
- cold-start cost
- native module or toolchain requirements

Use Bundlephobia or the repo's own bundle analysis when evaluating browser-facing packages, but do not let downloads or stars override technical fit.

## Comparison Template

Use a small comparison table before adding a non-trivial dependency.

| Criterion | Package A | Package B | Notes |
|-----------|-----------|-----------|-------|
| Capability fit | | | |
| Maintenance quality | | | |
| Dependency graph size | | | |
| Security posture | | | |
| Bundle/runtime cost | | | |
| Migration cost | | | |

## Ecosystem Examples

### Node.js

Prefer runtime-native options first:

- `fetch` before `axios` when the use case is simple
- `URL` / `URLSearchParams` before query-string helpers
- `crypto.randomUUID()` before small UUID helpers when compatibility allows

### Python

Prefer:

- standard-library modules where they are adequate
- one packaging workflow per repo instead of layering uv, Poetry, pip-tools, and raw pip together without policy

### Java / .NET / PHP

Prefer libraries with:

- strong ecosystem adoption
- current wrapper/plugin compatibility
- a clear long-term maintenance story from a reputable maintainer

## AI-Suggested Dependencies

Do not accept an AI-suggested package until you verify:

- it exists on the real registry
- it is spelled correctly
- it is current for the repo's actual ecosystem
- it survives the same technical and security review as human-suggested packages

## Red Flags

- install scripts for a package that should not need them
- a tiny utility with a surprisingly large dependency tree
- no release notes, no security policy, no maintainers responding
- package names that resemble a popular package but differ slightly
- recommendation based only on speed claims or popularity charts

## Decision Rule

Choose the dependency only if it is:

- clearly necessary
- lower risk than the alternatives
- maintainable by the team
- compatible with the repo's existing dependency policy
