# Dependency Security Scanning

Dependency security scanning covers vulnerability feeds, provenance and signature verification, build-script controls, and SBOM generation.

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
- [Vulnerability Triage](#vulnerability-triage)
- [EU Cyber Resilience Act Lookup](#eu-cyber-resilience-act-lookup)
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
- Before upgrading npm, read the target major's [configuration docs](https://docs.npmjs.com/cli/using-npm/config) and [release notes](https://github.com/npm/cli/releases) for lifecycle-script approvals and git/remote dependency defaults. Check required native builds and sources in CI; review each approval rather than enabling all scripts.
- pnpm 11+ controls dependency build scripts with the `allowBuilds` map (plus `strictDepBuilds`, default `true`) and `pnpm approve-builds`; `onlyBuiltDependencies`, `ignoredBuiltDependencies`, and `ignoreDepScripts` were removed in pnpm 11, and pnpm 12 errors or warns on unrecognized workspace settings
- Bun has a native audit workflow; do not assume npm is required just because the project is JavaScript

### Python

```bash
pip-audit
uv export --format cyclonedx1.5 > sbom.json
poetry run pip-audit
```

Notes:

- `pip-audit` is the default Python vulnerability scanner for resolved package graphs
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

The CISA 2025 draft of the SBOM minimum elements proposed fields beyond the 2021 NTIA baseline:
- **component hash** (cryptographic fingerprint)
- **license information**
- **tool name** (generator)
- **generation context** (how, when, by whom)
- "supplier name" replaced by "software producer" with "unknown provenance" fallback

Lookup step: before claiming SBOM compliance for a federal or regulated customer, check CISA's SBOM minimum-elements publication for whether that draft is final and which fields are required, and check the customer contract for the format it names. Generating these fields is cheap either way; the lookup decides whether a missing field blocks a release.

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
- Include the minimum-element fields your customer or regulator requires (see the lookup step above)
- Use the SBOM to answer "where is this vulnerable package actually deployed?"

## Provenance And Signatures

### Current practical controls

- verify npm registry signatures and provenance where available
- prefer trusted publishing and signed artifacts for releases
- treat wrapper updates, installer scripts, and plugin additions as supply-chain events
- review dependency install/build scripts before enabling them in CI
- valid provenance is not proof of safety: it attests *where and how* a package was built, not that the source or workflow was benign. Mini Shai-Hulud (May 2026) and Miasma (Jun 2026) packages carried cryptographically valid SLSA provenance / npm attestations because attackers published through the legitimate CI/OIDC workflow (slsa.dev blog 2026-05-15; Microsoft 2026-06-02). Use provenance to detect packages published *outside* the expected repo/workflow, and layer it with release-age delays, script allowlists, and lockfile review

### Node-focused controls

- pin the active package manager with `packageManager`
- use pnpm `minimumReleaseAge` when you want to avoid immediately consuming just-published packages
- use pnpm `approve-builds` and the `allowBuilds` map (pnpm 11+) to restrict lifecycle scripts

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

## Vulnerability Triage

Scanner output is a list of candidates, not a work queue. Rank by whether the vulnerable code can run in your product and whether anyone is exploiting it; severity comes after that.

When a vulnerability alert lands:

1. **Confirm presence.** Map the package and version to the deployed build or image using the lockfile or the release SBOM. Not shipped to production (dev-only, test-only, build tool not in the artifact) → lower priority, but still fix build tools that run with publish credentials.
2. **Check reachability.** Is the vulnerable function or configuration actually called or enabled? Use a reachability-aware scanner (for example `govulncheck`, which separates vulnerabilities in functions your code calls from those in packages it merely imports) or trace call sites by hand for the affected API. Unknown reachability counts as reachable.
3. **Check exploitation evidence.**
   - Listed in CISA's Known Exploited Vulnerabilities (KEV) catalog → exploitation is confirmed; treat as the top tier regardless of CVSS.
   - EPSS gives the estimated probability of exploitation activity in the near term. Use it to order the non-KEV backlog. It is a likelihood signal, not a severity: a low EPSS on a reachable, internet-facing path is still worth fixing, and a high EPSS on an unreachable path is not urgent.
   - CVSS describes technical severity, not your risk. Use it to break ties and to size impact once reachability and exploitation are known.
4. **Decide.** Upgrade, pin or override temporarily (with an owner and expiry), mitigate operationally, or accept with an expiry and an approver.
5. **Record "not affected" as a VEX statement.** When the component is present but you are not affected, publish a VEX (Vulnerability Exploitability eXchange) statement — OpenVEX, CSAF VEX, or CycloneDX VEX, whichever your SBOM toolchain consumes — with status `not_affected` and a justification (for example: vulnerable code not present, vulnerable code not in execute path, inline mitigations already exist). Scanners that read VEX suppress the finding; without it, every rescan and every customer scan reopens the same ticket. A "not affected" claim without a stated justification is a risk acceptance, not a VEX.
6. **Validate** with tests, an exact-install rebuild, and a rescan of the rebuilt artifact. Update the VEX status if a later change makes the code reachable.

Default ordering: KEV-listed and reachable → reachable with high EPSS or public exploit → reachable, remaining by CVSS → unreachable or not shipped (VEX `not_affected` with justification, or batch upgrade).

## EU Cyber Resilience Act Lookup

The EU Cyber Resilience Act (Regulation (EU) 2024/2847) sets vulnerability-handling and reporting obligations for manufacturers of products with digital elements placed on the EU market, including duties that cover the third-party components they ship. Its obligations phase in on different dates, and open-source stewards and different product classes are treated differently.

Lookup step: if you place software or connected products on the EU market, check the regulation text and the European Commission's CRA pages for which obligations apply to your role (manufacturer, importer, distributor, open-source steward), which already apply, and the reporting channel and deadlines for actively exploited vulnerabilities and severe incidents. Confirm the answer with counsel before relying on it. The decision it feeds: whether your triage workflow needs a regulator-reporting branch with its own clock, and whether your SBOM and VEX records must be retained as conformity evidence.

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
- one documented SLA keyed to the triage tiers above (KEV-listed and reachable first), not to CVSS alone
- one place to publish VEX statements for `not_affected` findings

## Incident Patterns (Historical, 2025-2026)

Historical record of the attack vectors; use it for the vector → control mapping, not as a current threat feed.

| Incident | Date | Vector | Mitigation demonstrated |
|----------|------|--------|------------------------|
| Shai-Hulud worm | Sep 2025 | Self-replicating worm stole publish tokens, spread to 500+ packages | minimumReleaseAge, token rotation, CISA alert |
| Shai-Hulud 2.0 | Nov 2025 | Wider scope: 25k+ malicious GitHub repos | Registry monitoring, token revocation; provenance helps only to flag publishes from an unexpected repo/workflow |
| Axios compromise | Mar 2026 | Compromised publish credentials; 2 malicious versions live <3h | Exact-version pinning, minimumReleaseAge |
| Mini Shai-Hulud | May 2026 | ~170 npm and PyPI packages in one coordinated cross-registry campaign | Cross-registry audit, SBOM correlation |
| Dependency confusion | Recurring class | Public packages that mimic internal package names win resolution | Scope allowlists, private registry enforcement |
| Miasma | Jun 2026 | Compromised `@redhat-cloud-services` npm namespace (32 packages), returned within days via a "Phantom Gyp" technique to hit 57 more packages in a 2-hour window | Namespace-scope monitoring, rapid-response revocation |

Operational takeaways:
- The fast-publish-to-exploit window is under 3 hours; a release-age delay (`minimumReleaseAge`, 1440 minutes by default in pnpm 11+) is one layer, not a complete mitigation — combine it with install-script denial, lockfile review, and token hygiene, and note that valid provenance did not stop Mini Shai-Hulud or Miasma
- Cross-registry attacks now span npm and PyPI simultaneously; audit both in polyglot repos
- Dependency confusion targets org-scoped packages; configure private registry priority and scope allowlists
- Install-script and dependency-source policy is version-specific. Use the npm lookup above when designing CI controls; do not infer the target version's defaults from incident coverage.

## Anti-Patterns

- using only a bot and calling the problem solved
- generating SBOMs but never linking them to real artifacts
- ignoring install scripts and plugin execution risk
- triaging based only on CVSS without reachability and exploitation evidence (KEV, EPSS)
- closing "not affected" findings without a VEX statement and justification, so every rescan reopens them
- keeping security updates bundled with unrelated refactors
