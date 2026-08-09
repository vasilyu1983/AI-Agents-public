# Supply Chain Security

Application-security guidance for dependencies, builds, artifacts, registries, and release workflows as of July 2026.

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
npm ci
npm audit
```

### 2. Publishing and Release Identity

Prefer OIDC trusted publishing over long-lived registry tokens.

```yaml
name: publish
on:
  release:
    types: [published]

jobs:
  publish:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      id-token: write
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 22
          registry-url: https://registry.npmjs.org
      - run: npm ci
      - run: npm test
      - run: npm publish
```

Notes:

- npm trusted publishing (OIDC-based, no long-lived tokens, automatic provenance) reached general availability on July 31, 2025. Treat it as the default for any package publishable through npm's registry, not an experimental option.
- Remove unused automation tokens after migration
- Restrict who can trigger release workflows

### 3. Provenance and Artifact Integrity

- Generate provenance where the ecosystem supports it
- Verify signatures or provenance before consuming internal artifacts
- Use SLSA and Sigstore as reference frameworks and tooling
- Sign tags, releases, and important artifacts where practical

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
- Manufacturer reporting duties (actively exploited vulnerability and severe incident notification to ENISA/CSIRT) apply from 11 September 2026 — this is imminent as of mid-2026 and should be treated as a near-term compliance deadline, not a distant one.
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
- Is provenance generated and visible?
- Are SBOMs release-specific and refreshable?
- Are dependency exceptions documented and time-bounded?
- Is there a process for KEV/high-severity dependency response?

---

## Sources to Verify Live

- CISA SBOM pages
- npm trusted publishing and provenance docs
- SLSA and Sigstore docs
- EU CRA text and implementation dates
- OWASP SPVS status
