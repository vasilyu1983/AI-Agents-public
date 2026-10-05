---
name: dev-dependency-management
description: "Guides dependency audits and upgrades. Use when auditing dependencies, upgrading vulnerable packages, managing lockfiles or package managers, SBOMs, or update and monorepo policy."
compatibility: Portable core. Works on Claude Code and Codex.
version: "1.4"
last_validated: 2026-07-11
---

# Dependency Management

## Quick Reference

| Task | Use |
|------|-----|
| Ecosystem defaults and package-manager choice | [references/ecosystem-guides.md](references/ecosystem-guides.md) |
| Lockfiles and CI install policy | [references/lockfile-management.md](references/lockfile-management.md) |
| Security scanning, SBOMs, and provenance | [references/security-scanning.md](references/security-scanning.md), [assets/automation/template-supply-chain-security.md](assets/automation/template-supply-chain-security.md), [assets/automation/template-sbom-vuln-triage-checklist.md](assets/automation/template-sbom-vuln-triage-checklist.md) |
| Monorepos and workspace policy | [references/monorepo-patterns.md](references/monorepo-patterns.md), [assets/nodejs/pnpm-workspace-template.yaml](assets/nodejs/pnpm-workspace-template.yaml) |
| Update strategy and rollback | [references/update-strategies.md](references/update-strategies.md), [assets/automation/template-dependency-upgrade-playbook.md](assets/automation/template-dependency-upgrade-playbook.md) |
| Add-or-avoid dependency decision | [references/dependency-selection-guide.md](references/dependency-selection-guide.md), [references/transitive-dependencies.md](references/transitive-dependencies.md) |
| Vulnerability detection | The ecosystem's native audit tool (`npm audit`, `pnpm audit`, `pip-audit`, `cargo audit`, `govulncheck`, `composer audit`) or `osv-scanner`; see [references/security-scanning.md](references/security-scanning.md#native-ecosystem-commands) |
| Vulnerability triage, VEX, EU CRA lookup | [references/security-scanning.md](references/security-scanning.md#vulnerability-triage) |
| Policy-manifest scorer (not a vulnerability scanner: no advisory database, refuses real manifests, exits 2 on unchecked input) | `python3 scripts/dep_auditor.py --help`, limits in [scripts/README.md](scripts/README.md) |

## Route Elsewhere

- Framework-specific frontend or backend implementation: use the relevant software skill.
- AppSec architecture beyond the dependency layer: use [software-security-appsec](../software-security-appsec/SKILL.md).
- CI/CD platform design: use [ops-devops-platform](../ops-devops-platform/SKILL.md).

## Workflow

1. Identify ecosystem, package manager, lockfile, and wrapper conventions already present.
2. Decide the smallest safe change: add, remove, pin, update, audit, or migrate.
3. Load only the guidance needed for lockfiles, security, monorepo policy, or update strategy.
4. Before migrating Node tooling, check the target major's release notes and its script-approval settings using the lookups below; compare them with CI's runtime and required native builds.
5. Finish with reproducibility checks, rollback notes, and any audit or SBOM follow-up.

### Upgrade proof and rollback bundle

Treat the manifest and lockfile as one change unit. Before the upgrade, capture the resolved version, integrity/source metadata, transitive dependency delta, install-script delta, and the exact build/test/runtime probes that protect the affected path. Review newly introduced packages and lifecycle scripts even when the requested direct dependency looks harmless.

A rollback instruction must restore both manifest and lockfile to a known pair and state whether caches, generated clients, database state, or persisted wire formats make code rollback insufficient. For a stateful or protocol-changing upgrade, require a forward-compatible migration or a tested downgrade path before rollout. “Revert the dependency bump” is not a complete rollback plan when the new version has already written data or changed an external contract.

## Core Decisions

### Package-Manager Defaults

| Ecosystem | Default for new repos | Version lookup | Key constraint |
|-----------|----------------------|----------------|----------------|
| Node | pnpm unless compat pressure favors npm | `npm view pnpm dist-tags` (a new major may ship on a non-default tag) | pnpm 11 removed `onlyBuiltDependencies` in favour of `allowBuilds`; check the target major's [release notes](https://pnpm.io/blog) for its runtime and install path, and [build settings](https://pnpm.io/settings/build) for script approvals before setting CI policy |
| Python | uv | uv release notes | Check whether uv is still on 0.x versioning before promising API stability |
| Rust | Cargo | pinned `rust-toolchain.toml` | commit Cargo.lock for apps |
| Go | go modules | `go` / `toolchain` lines in go.mod | go.mod + go.sum canonical |
| Java | Maven wrapper or Gradle wrapper | wrapper properties | wrappers plus BOMs or version catalogs |
| .NET | PackageReference | `global.json` SDK pin | PackageReference over packages.config |
| PHP | Composer | composer.json `config.platform` | commit composer.lock for apps |

Keep repo-local consistency more important than theoretical ecosystem purity.

### Lockfile and Toolchain Policy

Minimum rules:
- commit application lockfiles
- use exact lockfile installs in CI
- avoid hand-editing lockfiles
- do not carry multiple lockfiles for one package graph
- prefer repo-local wrappers or toolchain files over unpinned global installs

Rule: `rules/deps/lockfiles.md` loads this invariant when Claude edits a matching file.

### Update Strategy

Default cadence:
- patch: small and frequent
- minor: batched and tested
- major: isolated with release-note review and rollback plan
- security: prioritize by reachability and exploitation evidence (KEV listing first, EPSS as a likelihood signal, CVSS as severity only), and record `not_affected` findings as VEX statements with a justification; see [Vulnerability Triage](references/security-scanning.md#vulnerability-triage)

### Supply-Chain Controls

Use:
- official registries where possible
- provenance or signature verification where supported
- SBOM generation for release artifacts, with the minimum-element fields your customer or regulator requires (lookup step in [references/security-scanning.md](references/security-scanning.md#sboms))
- explicit review of install or build scripts
- a build-time static gate on every shipped artifact, not only source code. The gate covers the package or binary and everything bundled into it: vendored and statically linked dependencies, plugins, extension or recipe manifests, and templates. Before publish it checks licenses against an allowlist, known advisories, and allowed sources (no git or path dependencies that bypass the lockfile), and it schema-validates bundled manifests. An artifact that fails does not reach a release channel. A policy file such as cargo-deny's `deny.toml` is one way to express this
- expiration on overrides, resolutions, and temporary pins
- a release-age delay (pnpm `minimumReleaseAge`, Renovate `minimumReleaseAge`, Dependabot `cooldown`) to avoid consuming just-published packages; it is one layer, not a fix, because several historical npm compromises were live for only hours before removal (see the incident patterns in [references/security-scanning.md](references/security-scanning.md))
- dependency confusion mitigations: scope all internal packages, audit all org-scoped packages before use
- EU market: if you ship products with digital elements in the EU, look up which Cyber Resilience Act (Regulation (EU) 2024/2847) vulnerability-reporting obligations apply to you before designing the triage workflow; see [EU Cyber Resilience Act Lookup](references/security-scanning.md#eu-cyber-resilience-act-lookup)
- Before adopting an npm major, read its [versioned configuration docs](https://docs.npmjs.com/cli/using-npm/config) and [changelog](https://github.com/npm/cli/releases) for dependency lifecycle-script approvals and git/remote dependency defaults. Check required native builds and sources in CI, and review each approval rather than enabling all scripts.

### AI-Generated Dependency Risk

Before accepting an AI-suggested package:
- verify it exists
- check for typosquatting risk
- check maintenance and release cadence
- prefer standard library or existing dependencies if feasible
- run the same audit and review workflow as for any other new package

Rule: `rules/common/dependencies.md` loads this invariant in every coding session.

## Output Modes

Default to one of these:

- Dependency policy brief:
  manager choice, lockfile rules, update cadence, and security controls.
- Upgrade plan:
  scope, batching, testing, rollback, and audit follow-up.
- Dependency audit:
  health risks, unmaintained packages, graph complexity, and remediation order.
- Monorepo dependency strategy:
  workspace model, shared policy, and update automation rules.

## Known Traps

- Upgrading transitive or security-sensitive packages without checking whether the fix actually lands in the production artifact path.
- Mixing wrapper, lockfile, and package-manager upgrades in one move, which makes rollback and blame assignment much harder.
- Assuming monorepo hoisting or workspace dedupe is harmless when postinstall scripts, peer deps, or native builds are involved.
- Accepting temporary pins or overrides without a removal owner, expiry, and retest trigger.
- Treating SBOM generation as complete supply-chain control while provenance, install scripts, and release process remain unreviewed.

- Treating a clean `dep_auditor.py` run as an audit: it reads self-declared flags only. Its input requires an explicit dependency list (use `[]` for a dependency-free ecosystem), boolean policy flags, non-negative integer ages when provided, and a scan date that is not in the future; malformed declarations exit 2.

## References

| File | What it covers |
|------|---------------|
| [references/ecosystem-guides.md](references/ecosystem-guides.md) | Per-ecosystem package-manager defaults, CI install commands, and watchouts for Node, Python, Rust, Go, Java, .NET, PHP |
| [references/lockfile-management.md](references/lockfile-management.md) | Lockfile matrix, golden rules, per-ecosystem exact-install commands, CI rules, and drift recovery |
| [references/security-scanning.md](references/security-scanning.md) | Native audit commands, SBOM generation, provenance controls, Dependabot/Renovate usage, and triage workflow |
| [references/monorepo-patterns.md](references/monorepo-patterns.md) | JS/TS workspace defaults, pnpm supply-chain settings, polyglot structure, and version governance |
| [references/dependency-selection-guide.md](references/dependency-selection-guide.md) | Add-or-avoid decision criteria, graph inspection commands, AI-suggested package checklist |
| [references/update-strategies.md](references/update-strategies.md) | Update cadence table, batch-by-risk workflow, bot policy, and rollback rule |
| [references/transitive-dependencies.md](references/transitive-dependencies.md) | Tree inspection, override patterns, deduplication, and resolution decision tree |
| [references/license-compliance.md](references/license-compliance.md) | License risk table, GPL decision tree, automated tooling, CI integration, and SBOM generation commands |
| [references/version-conflict-resolution.md](references/version-conflict-resolution.md) | Conflict types, per-manager diagnostic commands, forced resolution syntax, and pnpm catalogs |
| [references/container-dependency-patterns.md](references/container-dependency-patterns.md) | Multi-stage build patterns, layer caching, vulnerability scanning (Trivy/Grype), and reproducible base image pinning |
| [references/semver-guide.md](references/semver-guide.md) | SemVer constraint syntax for npm, Python, and Cargo with common pitfalls |
| [references/anti-patterns.md](references/anti-patterns.md) | Critical and moderate anti-patterns with corrective examples |

Curated source links live in [data/sources.json](data/sources.json).

## Navigation

- Assets: [assets/nodejs/package-json-template.json](assets/nodejs/package-json-template.json), [assets/nodejs/npmrc-template.txt](assets/nodejs/npmrc-template.txt), [assets/nodejs/pnpm-workspace-template.yaml](assets/nodejs/pnpm-workspace-template.yaml), [assets/python/pyproject-toml-template.toml](assets/python/pyproject-toml-template.toml), [assets/automation/dependabot-config.yml](assets/automation/dependabot-config.yml), [assets/automation/renovate-config.json](assets/automation/renovate-config.json), [assets/automation/audit-checklist.md](assets/automation/audit-checklist.md), [assets/automation/template-dependency-upgrade-playbook.md](assets/automation/template-dependency-upgrade-playbook.md), [assets/automation/template-supply-chain-security.md](assets/automation/template-supply-chain-security.md), [assets/automation/template-sbom-vuln-triage-checklist.md](assets/automation/template-sbom-vuln-triage-checklist.md)
- Scripts and samples: `scripts/dep_auditor.py`, `scripts/README.md`, [data/sample-dependency-manifest.example.json](data/sample-dependency-manifest.example.json)

## Learnings Loop

When prior decisions or pitfalls are relevant, consult `learnings.consolidated.md` if present; use `learnings.md` only for needed history or as the available fallback. Otherwise skip both.

After applying it, if you encountered a pattern worth remembering, a mistake worth preventing, or a domain fact that surprised you, append one dated bullet to `learnings.md` via `agents-skills-feedback-loop/scripts/append_learning.py`. Do not modify `SKILL.md` itself.
