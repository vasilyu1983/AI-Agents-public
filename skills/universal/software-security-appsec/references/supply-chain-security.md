# Supply Chain Security

Application-security guidance for dependencies, builds, artifacts, registries, and release workflows.

Use this reference for application-layer supply-chain decisions. For infrastructure hardening around runners, registries, and clusters, pair with [../../ops-devops-platform/SKILL.md](../../ops-devops-platform/SKILL.md).

---
## Table of Contents

- [Current Baseline](#current-baseline)
- [What to Protect](#what-to-protect)
- [Common Failure Modes](#common-failure-modes)
- [Practical Control Stack](#practical-control-stack)
- [1. Dependency Governance](#1-dependency-governance)
- [2. Publishing and Release Identity](#2-publishing-and-release-identity)
- [3. Provenance and Artifact Integrity](#3-provenance-and-artifact-integrity)
- [ML Model and Data Artifacts](#ml-model-and-data-artifacts)
- [4. SBOM and VEX](#4-sbom-and-vex)
- [5. Pipeline Verification](#5-pipeline-verification)
- [Regulatory Notes](#regulatory-notes)
- [CISA SBOM Guidance](#cisa-sbom-guidance)
- [EU Cyber Resilience Act](#eu-cyber-resilience-act)
- [Reference Incidents](#reference-incidents)
- [Review Checklist](#review-checklist)
- [Sources to Verify Live](#sources-to-verify-live)


## Current Baseline

- OWASP Top 10:2025 treats supply chain failures as a first-class application-security concern under A03.
- SBOMs are useful, but they are not a magic compliance checkbox and they do not replace release integrity controls.
- In the United States, CISA's 2025 SBOM minimum-elements document was published for public comment in August 2025. Treat it as draft guidance unless a final update is published.
- In the EU, the Cyber Resilience Act is real law, but obligations are phased. Do not summarize it as “SBOMs are mandatory now” without checking the product category and the applicable date.

---

## What to Protect

- Dependency selection and update process
- Lockfiles and dependency metadata
- CI/CD identities, tokens, and workflow boundaries
- Build environment integrity
- Artifact signing, provenance, and verification
- Registry publish permissions
- Runtime package and image provenance

---

## Common Failure Modes

- Typosquatting or dependency confusion
- Compromised maintainer or publish token
- Tampered CI workflow or release job
- Unpinned or weakly governed build inputs
- Unsigned artifacts or unverifiable provenance
- Blind trust in transitive dependencies
- SBOMs generated once and never refreshed

---

## Practical Control Stack

### 1. Dependency Governance

- Commit lockfiles
- Review new direct dependencies intentionally
- Prefer trusted registries and clear namespace controls
- Use age, maintenance, provenance, and advisory history as selection signals
- For application dependencies, exact pinning of direct production dependencies is often reasonable; for libraries, compatibility ranges may be necessary, but lockfile and release controls still matter

```bash
npm ci --ignore-scripts
npm audit
```

### Install Scripts and Release Cooldowns

- Disable dependency lifecycle scripts during dependency acquisition (`npm ci --ignore-scripts`). Explicit `npm run` / `npm test` commands still execute their requested script; this flag is not a sandbox. See [npm configuration](https://docs.npmjs.com/cli/using-npm/config/).
- If a dependency requires a native build or generated assets, review the resolved package and script, then run only the approved build in a disposable environment without publishing credentials or production secrets. Check the installed package manager's supported script-approval settings; do not silently enable every lifecycle script to make installation pass.
- Apply a release-age cooldown to routine updates, including transitive resolutions. Look up the installed manager's age filter and units before configuring it ([npm configuration](https://docs.npmjs.com/cli/using-npm/config/), [pnpm settings](https://pnpm.io/settings#minimumreleaseage)); unsupported settings must fail the policy check. Select the window from the team's threat and update policy, rather than claiming a universal safe duration.
- A cooldown does not prove safety and can delay a vulnerability fix. Review urgent security-update exceptions, record the exact package/version, owner and rationale, and expire the exception; avoid wildcard exclusions. Verify the resolved lockfile and installation behavior in an isolated fixture before admitting the update.

### 2. Publishing and Release Identity

Prefer OIDC trusted publishing where the registry supports the selected CI provider and runner. Before configuring it, read [npm trusted publishing](https://docs.npmjs.com/trusted-publishers/) for provider support, CLI prerequisites and the exact repository/workflow/environment identity. Restrict `id-token: write` to the publish job and pin third-party CI actions to reviewed immutable commits; select a supported Node runtime from the consuming project's toolchain policy.

Install dependencies with scripts disabled, run reviewed build/tests without registry credentials, then publish through the configured identity. Remove unused automation tokens after migration and restrict who can trigger releases.

Trusted publishing and provenance are distinct: npm automatic provenance depends on the supported CI path and public repository/package conditions. Verify the attestation on the released artifact; do not assume OIDC alone supplies it.

### 3. Provenance and Artifact Integrity

- Generate provenance where the ecosystem supports it
- Verify signatures or provenance before consuming internal artifacts
- Choose and record the applicable SLSA spec/track from its publisher and use Sigstore as reference frameworks and tooling; signing and provenance mechanics live in [qa-security-testing](../../qa-security-testing/SKILL.md)
- Sign tags, releases, and important artifacts where practical

### ML Model and Data Artifacts

Model weights, checkpoints, tokenizers and vector-index snapshots are build inputs with the same risks as packages, plus one more: some weight formats execute code on load.

- Pin each model and index snapshot by content hash or digest, record it in the SBOM or release manifest, and verify it before load or restore.
- Prefer non-executable weight formats (for example safetensors) over pickle-based formats, which can run arbitrary code when deserialized. Do not enable remote-code loading for third-party models without review.
- Load untrusted or newly downloaded models in an isolated environment: no production data, no outbound network, bounded resources.
- Treat GPU driver and CUDA/runtime versions as pinned inputs: allowlist them and record the versions per deployment so a silent host update is visible.

### 4. SBOM and VEX

- Generate an SBOM for each release, not once per repository
- Refresh it when dependencies or build composition changes
- Pair SBOM data with VEX or equivalent vulnerability-status workflows when you need actionable downstream triage

```bash
npm sbom --sbom-format=cyclonedx > sbom.json
```

### 5. Pipeline Verification

Use SSDF for process expectations and SPVS when the user specifically needs a pipeline-security verification framework.

Key review questions:

- Who can change release workflows?
- Who can mint publish credentials?
- Can builds be reproduced or independently verified?
- Is artifact provenance visible to consumers?
- Can a compromised dependency or workflow reach production unchecked?

---

## Regulatory Notes

### CISA SBOM Guidance

- The 2025 CISA minimum-elements document was released as draft guidance for public comment in August 2025.
- The document is useful for current expectations around richer SBOM content and operationalization.
- Do not present it as final federal law or final mandatory CISA policy unless you verify a newer update.

### EU Cyber Resilience Act

- Regulation (EU) 2024/2847 entered into force on 10 December 2024.
- Key obligations are phased.
- Manufacturer reporting duties (actively exploited vulnerability and severe incident notification to ENISA/CSIRT) apply from 11 September 2026. Clocks: 24h early warning, 72h notification, then a final report (14 days after a fix is available for an actively exploited vulnerability; 1 month after the 72h notification for a severe incident), submitted through ENISA's Single Reporting Platform. Open-source stewards follow from 11 December 2027. Source: https://digital-strategy.ec.europa.eu/en/policies/cra-reporting.
- Most other CRA obligations (conformity assessment, CE marking, full technical documentation) apply from 11 December 2027.

Use official EUR-Lex text for dates and scope. Avoid blanket claims such as “all products need an SBOM now.”

---

## Reference Incidents

Use concrete incidents to explain why controls matter:

- `xz` backdoor
- registry token compromise
- malicious package releases
- CDN or third-party script compromise
- tampered workflow or build step
- Shai-Hulud npm worm (first wave September 2025; a more sophisticated second wave, "Shai-Hulud 2.0," in November 2025) — self-propagating malware that harvested credentials via TruffleHog-style secret scanning from postinstall/preinstall scripts and used stolen tokens to republish itself into further packages. Treat it as the reference case for why short-lived, scoped publish credentials and postinstall-script restrictions matter, not just token hygiene in the abstract.

Use incident examples for training, not as a substitute for formal controls.

---

## Review Checklist

- Are release identities short-lived and scoped?
- Is trusted publishing enabled where supported?
- Are lockfiles committed and enforced in CI?
- Are lifecycle scripts disabled or explicitly reviewed in an isolated build?
- Does the manager enforce the release-age policy, with narrow, recorded security-fix exceptions?
- Is provenance generated and visible?
- Are SBOMs release-specific and refreshable?
- Are dependency exceptions documented and time-bounded?
- Is there a process for KEV/high-severity dependency response?
- Are model weights and index snapshots hash-pinned, verified before load, and in a non-executable format?

---

## Sources to Verify Live

- CISA SBOM pages
- npm trusted publishing and provenance docs
- SLSA and Sigstore docs
- EU CRA text and implementation dates
- OWASP SPVS status
