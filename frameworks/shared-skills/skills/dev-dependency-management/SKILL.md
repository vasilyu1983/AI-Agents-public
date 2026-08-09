---
name: dev-dependency-management
description: "Guides dependency management across languages and ecosystems. Use when choosing package managers, lockfiles, update policy, security scanning, SBOMs, or monorepo patterns."
compatibility: Portable core. Works on Claude Code and Codex.
version: "1.2"
last_validated: 2026-07-11
---

# Dependency Management

Use this skill for package-manager choice, lockfile policy, update strategy, supply-chain controls, and dependency hygiene across common ecosystems. It owns reproducibility and security defaults, not framework-specific app architecture.

## Quick Reference

| Task | Use |
|------|-----|
| Ecosystem defaults and package-manager choice | [references/ecosystem-guides.md](references/ecosystem-guides.md) |
| Lockfiles and CI install policy | [references/lockfile-management.md](references/lockfile-management.md) |
| Security scanning, SBOMs, and provenance | [references/security-scanning.md](references/security-scanning.md), [assets/automation/template-supply-chain-security.md](assets/automation/template-supply-chain-security.md), [assets/automation/template-sbom-vuln-triage-checklist.md](assets/automation/template-sbom-vuln-triage-checklist.md) |
| Monorepos and workspace policy | [references/monorepo-patterns.md](references/monorepo-patterns.md), [assets/nodejs/pnpm-workspace-template.yaml](assets/nodejs/pnpm-workspace-template.yaml) |
| Update strategy and rollback | [references/update-strategies.md](references/update-strategies.md), [assets/automation/template-dependency-upgrade-playbook.md](assets/automation/template-dependency-upgrade-playbook.md) |
| Add-or-avoid dependency decision | [references/dependency-selection-guide.md](references/dependency-selection-guide.md), [references/transitive-dependencies.md](references/transitive-dependencies.md) |
| Audit script | `python3 scripts/dep_auditor.py --help` |

## When to Use

- Choose or migrate a package manager.
- Define lockfile, wrapper, or toolchain pinning policy.
- Add, remove, pin, or upgrade dependencies safely.
- Resolve dependency conflicts or transitive-risk issues.
- Set up audits, SBOM generation, provenance checks, or update automation.
- Define dependency policy for monorepos or polyglot repos.

## Route Elsewhere

- Framework-specific frontend or backend implementation: use the relevant software skill.
- AppSec architecture beyond the dependency layer: use [software-security-appsec](../software-security-appsec/SKILL.md).
- CI/CD platform design: use [ops-devops-platform](../ops-devops-platform/SKILL.md).

## Defaults

- Lockfile-first installs.
- Pinned package manager or wrapper where the ecosystem supports it.
- Smallest safe dependency change first.
- Patch updates often, majors in isolation.
- SBOM and audit workflow for release artifacts.
- AI-suggested packages are untrusted until verified.

## Workflow

1. Identify ecosystem, package manager, lockfile, and wrapper conventions already present.
2. Decide the smallest safe change: add, remove, pin, update, audit, or migrate.
3. Load only the guidance needed for lockfiles, security, monorepo policy, or update strategy.
4. Verify volatile tool behavior and security claims against official sources before recommending migrations.
5. Finish with reproducibility checks, rollback notes, and any audit or SBOM follow-up.

## ASCII Flow

```text
dependency management request
  -> identify ecosystem, package manager, lockfile, wrapper, and workspace shape
  -> classify change: add, remove, pin, update, audit, migrate, or policy
  -> choose smallest safe dependency move
  -> check security, provenance, license, transitive risk, and AI package risk
  -> update lockfile or policy according to repo conventions
  -> run reproducibility, test, audit, and SBOM checks where available
  -> document rollback, owner, expiry, and follow-up
```

## Core Decisions

### Package-Manager Defaults

| Ecosystem | Default for new repos | Current stable | Key constraint |
|-----------|----------------------|----------------|----------------|
| Node | pnpm unless compat pressure favors npm | pnpm 12 (Rust-native, requires Node 22) | pnpm 11+ is pure ESM, SQLite store; pnpm 12 is a native Rust port via `pnpm self-update`; verify CI Node version |
| Python | uv | uv 0.11.x (0.x but production-stable) | Still on 0.x versioning; core APIs stable |
| Rust | Cargo | stable toolchain | commit Cargo.lock for apps |
| Go | go modules | current go toolchain | go.mod + go.sum canonical |
| Java | Maven wrapper or Gradle wrapper | see upstream | wrappers plus BOMs or version catalogs |
| .NET | PackageReference | current .NET SDK | PackageReference over packages.config |
| PHP | Composer | current stable | commit composer.lock for apps |

Keep repo-local consistency more important than theoretical ecosystem purity.

### Lockfile and Toolchain Policy

Minimum rules:
- commit application lockfiles
- use exact lockfile installs in CI
- avoid hand-editing lockfiles
- do not carry multiple lockfiles for one package graph
- prefer repo-local wrappers or toolchain files over global latest installs

### Update Strategy

Default cadence:
- patch: small and frequent
- minor: batched and tested
- major: isolated with release-note review and rollback plan
- security: prioritize by exploitability and exposure, not CVSS alone

### Supply-Chain Controls

Use:
- official registries where possible
- provenance or signature verification where supported
- SBOM generation for release artifacts (CISA 2025 draft adds mandatory component hash, license, tool name, and generation context fields)
- explicit review of install or build scripts
- expiration on overrides, resolutions, and temporary pins
- pnpm `minimumReleaseAge` or Renovate `minimumReleaseAge` to avoid consuming just-published packages (Shai-Hulud, Axios, and Miasma npm compromises 2025-2026 repeatedly show a fast-publish-to-attack window under three hours)
- dependency confusion mitigations: scope all internal packages, audit all org-scoped packages before use
- npm v12 (shipping July 2026) disables install scripts, git dependencies, and remote-URL dependencies by default; plan the CI migration before it lands, and treat any repo still relying on install scripts as a review item, not a blocker to skip

### AI-Generated Dependency Risk

Before accepting an AI-suggested package:
- verify it exists
- check for typosquatting risk
- check maintenance and release cadence
- prefer standard library or existing dependencies if feasible
- run the same audit and review workflow as for any other new package

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

## Anti-Patterns

- Mixing package managers or lockfiles casually.
- Installing without the lockfile in CI.
- Migrating ecosystems for novelty instead of clear value.
- Treating AI-suggested packages as trusted by default.
- Leaving temporary overrides in place without owners or expiry.
- Chasing vulnerability counts without considering exploitability and production exposure.

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

## Navigation

- Assets: [assets/nodejs/package-json-template.json](assets/nodejs/package-json-template.json), [assets/nodejs/npmrc-template.txt](assets/nodejs/npmrc-template.txt), [assets/nodejs/pnpm-workspace-template.yaml](assets/nodejs/pnpm-workspace-template.yaml), [assets/python/pyproject-toml-template.toml](assets/python/pyproject-toml-template.toml), [assets/automation/dependabot-config.yml](assets/automation/dependabot-config.yml), [assets/automation/renovate-config.json](assets/automation/renovate-config.json), [assets/automation/audit-checklist.md](assets/automation/audit-checklist.md), [assets/automation/template-dependency-upgrade-playbook.md](assets/automation/template-dependency-upgrade-playbook.md), [assets/automation/template-supply-chain-security.md](assets/automation/template-supply-chain-security.md), [assets/automation/template-sbom-vuln-triage-checklist.md](assets/automation/template-sbom-vuln-triage-checklist.md)
- Scripts and samples: `scripts/dep_auditor.py`, `scripts/README.md`, [data/sample-dependency-manifest.example.json](data/sample-dependency-manifest.example.json)

## Fact-Checking

- Known bugs, regressions, framework/compiler/runtime footguns, and version-specific crash or workaround guidance must be verified against current primary web sources before being treated as current fact.
- Curated source links live in [data/sources.json](data/sources.json).
- Package-manager defaults, CLI flags, provenance behavior, and SBOM guidance are volatile and should be verified against current official docs before giving definitive recommendations.
- Prefer official package-manager, standards, and security-advisory sources over secondary blogs.

## Learnings Loop

Before applying this skill on a non-trivial task, read `learnings.consolidated.md` in this directory (and `learnings.md` if present).

After applying it, if you encountered a pattern worth remembering, a mistake worth preventing, or a domain fact that surprised you, append one dated bullet to `learnings.md` via `agents-skills-feedback-loop/scripts/append_learning.py`. Do not modify `SKILL.md` itself.
