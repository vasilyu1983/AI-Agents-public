# Dependency Security Scanning

**Freshness anchor:** July 2026. Security scanning now includes vulnerability feeds, provenance and signature verification, build-script controls, and SBOM generation.

## Table of Contents

- [Security Layers](#security-layers)
- [Native Ecosystem Commands](#native-ecosystem-commands)
- [Node.js](#nodejs)
- [npm](#npm)
- [pnpm](#pnpm)
- [Yarn 4](#yarn-4)
- [Bun](#bun)
- [Python](#python)
- [Rust, Go, PHP, .NET](#rust-go-php-net)
- [SBOMs](#sboms)
- [Generation options](#generation-options)
- [npm](#npm)
- [uv](#uv)
- [generic / polyglot / container](#generic-polyglot-container)
- [Rules](#rules)
- [Provenance And Signatures](#provenance-and-signatures)
- [Current practical controls](#current-practical-controls)
- [Node-focused controls](#node-focused-controls)
- [Automated Update Tooling](#automated-update-tooling)
- [Dependabot](#dependabot)
- [Renovate](#renovate)
- [Triage Workflow](#triage-workflow)
- [Review Checklist](#review-checklist)
- [Recommended Baseline](#recommended-baseline)
- [Anti-Patterns](#anti-patterns)

## Security Layers

Use more than one layer:

1. native ecosystem audit commands
2. automated update tooling
3. provenance and signature checks
4. SBOM generation and correlation
5. incident response workflow tied to actual deployed artifacts

## Native Ecosystem Commands

### Node.js

```bash
# npm
npm audit --audit-level=high
npm sbom --sbom-format=spdx

# pnpm
pnpm audit

# Yarn 4
yarn npm audit

# Bun
bun audit
```

Notes:

- registry-signature verification is a separate subcommand, `npm audit signatures` — plain `npm audit` checks known vulnerabilities only; run both, and do not conflate them
- npm 12 (shipping July 2026) disables install scripts, git dependencies, and remote-URL dependencies by default; this is a bigger default-security shift than audit tooling alone and needs an explicit CI migration plan before upgrading
- pnpm can reduce script risk with `onlyBuiltDependencies`, `ignoredBuiltDependencies`, and `approve-builds`
- Bun has a native audit workflow; do not assume npm is required just because the project is JavaScript

### Python

```bash
pip-audit
uv export --format cyclonedx1.5 > sbom.json
poetry run pip-audit
```

Notes:

- `pip-audit` remains the simplest current Python vulnerability scanner for package graphs
- when using uv or Poetry, audit the resolved environment, not only the manifest

### Rust, Go, PHP, .NET

```bash
cargo audit
govulncheck ./...
composer audit
dotnet list package --vulnerable --include-transitive
```

## SBOMs

Prefer **SPDX** or **CycloneDX**.

CISA 2025 draft minimum elements (public comment closed Oct 2025; as of July 2026 the draft has not been finalized — treat it as directional, not yet binding) adds mandatory fields beyond the 2021 NTIA baseline:
- **component hash** (cryptographic fingerprint)
- **license information**
- **tool name** (generator)
- **generation context** (how, when, by whom)
- "supplier name" replaced by "software producer" with "unknown provenance" fallback

### Generation options

```bash
# npm
npm sbom --sbom-format=spdx

# uv
uv export --format cyclonedx1.5 > sbom.json

# generic / polyglot / container
syft . -o cyclonedx-json > sbom.json
```

### Rules

- Generate SBOMs for release artifacts, not just source trees
- Store the SBOM with the build ID, commit SHA, and artifact digest
- Include all CISA 2025 mandatory fields when targeting federal or regulated environments
- Use the SBOM to answer "where is this vulnerable package actually deployed?"

## Provenance And Signatures

### Current practical controls

- verify npm registry signatures and provenance where available
- prefer trusted publishing and signed artifacts for releases
- treat wrapper updates, installer scripts, and plugin additions as supply-chain events
- review dependency install/build scripts before enabling them in CI

### Node-focused controls

- pin the active package manager with `packageManager`
- use pnpm `minimumReleaseAge` when you want to avoid immediately consuming just-published packages
- use pnpm `approve-builds` and `onlyBuiltDependencies` to restrict lifecycle scripts

## Automated Update Tooling

### Dependabot

Use it for:

- security updates
- grouped patch/minor updates
- multi-ecosystem grouping when repo topology makes sense

Current guidance:

- use `groups` to reduce PR noise
- use `multi-ecosystem-groups` only when the deployment unit truly spans those ecosystems
- keep security updates separate from broad version refreshes

### Renovate

Use it for:

- finer grouping and automerge policy
- dependency dashboards
- lockfile maintenance windows
- package-specific policies like `minimumReleaseAge`

## Triage Workflow

When a vulnerability alert lands:

1. confirm the affected package and version
2. map the finding to the deployed build or image using lock state or SBOM
3. determine exploitability in your environment
4. choose one of: upgrade, pin/override temporarily, mitigate operationally, or accept risk with expiry
5. validate with tests and exact-install rebuilds

## Review Checklist

- Is the finding on a runtime path or dev-only path?
- Is the vulnerable package actually present in production artifacts?
- Does the fix introduce a major version jump?
- Is there a safer transitive override than a broad upgrade?
- Did the update change install/build script behavior?
- Was the SBOM refreshed after the fix?

## Recommended Baseline

- one native audit command in CI for the ecosystem
- one automated update bot
- one SBOM generation step per release
- one provenance/signature review path for published artifacts
- one documented SLA for critical and high-risk dependency issues

## Notable 2025-2026 npm Incidents (Pattern Reference)

| Incident | Date | Vector | Mitigation demonstrated |
|----------|------|--------|------------------------|
| Shai-Hulud worm | Sep 2025 | Self-replicating worm stole publish tokens, spread to 500+ packages | minimumReleaseAge, token rotation, CISA alert |
| Shai-Hulud 2.0 | Nov 2025 | Wider scope: 25k+ malicious GitHub repos | Signed provenance, registry monitoring |
| Axios compromise | Mar 2026 | Compromised publish credentials; 2 malicious versions live <3h | Exact-version pinning, minimumReleaseAge |
| Mini Shai-Hulud | May 2026 | 170+ npm + 2 PyPI packages; first cross-registry coordinated attack | Cross-registry audit, SBOM correlation |
| Dependency confusion | May 2026 | Malicious packages in org scopes mimicking internal names | Scope allowlists, private registry enforcement |
| Miasma | Jun 2026 | Compromised `@redhat-cloud-services` npm namespace (32 packages), returned within days via a "Phantom Gyp" technique to hit 57 more packages in a 2-hour window | Namespace-scope monitoring, rapid-response revocation; directly accelerated npm's v12 default-deny release |

Operational takeaways:
- The fast-publish-to-exploit window is under 3 hours; `minimumReleaseAge: 1440` (minutes) is the primary mitigation
- Cross-registry attacks now span npm and PyPI simultaneously; audit both in polyglot repos
- Dependency confusion targets org-scoped packages; configure private registry priority and scope allowlists
- Repeated namespace-takeover incidents (Miasma) are why npm 12 disables install scripts, git dependencies, and remote-URL dependencies by default; expect the ecosystem norm to shift from "allow unless flagged" to "deny unless reviewed"

## Anti-Patterns

- using only a bot and calling the problem solved
- generating SBOMs but never linking them to real artifacts
- ignoring install scripts and plugin execution risk
- triaging based only on CVSS without environment context
- keeping security updates bundled with unrelated refactors
