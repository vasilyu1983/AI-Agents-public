# Supply-Chain Security

Covers SLSA build levels, Sigstore/Cosign keyless signing, in-toto attestations, SBOM signing,
GitHub provenance attestations, and registry integrations for npm and PyPI.

## Contents

- [SLSA Framework](#slsa-framework)
- [Sigstore / Cosign](#sigstore--cosign)
- [in-toto Attestations](#in-toto-attestations)
- [SBOM Signing](#sbom-signing)
- [GitHub Provenance Attestations](#github-provenance-attestations)
- [npm and PyPI Sigstore Integration](#npm-and-pypi-sigstore-integration)
- [CI Integration Checklist](#ci-integration-checklist)
- [Key Sources](#key-sources)

---

## SLSA Framework

**SLSA** (Supply-chain Levels for Software Artifacts — https://slsa.dev) is a graduated framework
for hardening build provenance and artifact integrity. Each level builds on the previous.

| Level | Requirement | What it prevents |
|-------|-------------|-----------------|
| SLSA Build L1 | Build provenance exists (unsigned, informational) | No tampering visibility baseline |
| SLSA Build L2 | Signed provenance from a hosted build service | Third-party builds masquerading as CI output |
| SLSA Build L3 | Isolated, hardened build environment; source tracked | Compromised build system injecting code |

SLSA v1.0 (released 2023) replaced the earlier four-level model with a three-level Build track
(`Build L1`–`Build L3`) plus separate `Source` and `Dependencies` tracks under development.
SLSA v1.1 was released April 2025 (current approved spec). SLSA v1.2 RC2 was under review in
late 2025. The table above uses the current v1.x level names. Legacy four-level numbering (L1–L4)
still appears in some tooling documentation; map L4 → Build L3 when you encounter it.

**Key artifacts**: a SLSA provenance document records builder identity, source reference, build
invocation parameters, and output digest. Verifiers check the provenance before consuming an
artifact.

---

## Sigstore / Cosign

**Sigstore** (https://sigstore.dev) is a free, open, Linux Foundation project providing
transparency-log-backed signing for software artifacts without long-lived key management.

### Keyless OIDC signing

Instead of storing a signing key, cosign uses short-lived certificates bound to an OIDC identity
(e.g. a GitHub Actions workflow). The certificate and signature are recorded in the **Rekor**
transparency log. Verification checks the log, not a stored key.

```
identity → OIDC token → Fulcio CA issues short-lived cert → cosign signs image → Rekor records entry
```

### Verify a signed image

```bash
cosign verify \
  --certificate-identity-regexp "https://github.com/ORG/REPO/.github/workflows/release.yml" \
  --certificate-oidc-issuer "https://token.actions.githubusercontent.com" \
  ghcr.io/ORG/IMAGE@sha256:DIGEST
```

### CI snippet — sign a container image with GHA OIDC

```yaml
# .github/workflows/release.yml
name: Build and Sign

on:
  push:
    tags: ["v*"]

permissions:
  contents: read
  id-token: write      # Required for keyless OIDC signing
  packages: write

jobs:
  build-sign:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Build and push image
        id: build
        uses: docker/build-push-action@v6
        with:
          push: true
          tags: ghcr.io/${{ github.repository }}:${{ github.ref_name }}

      - name: Install cosign
        uses: sigstore/cosign-installer@v3   # pins to latest stable

      - name: Sign image (keyless)
        env:
          COSIGN_EXPERIMENTAL: "1"           # enables keyless mode
        run: |
          cosign sign --yes \
            ghcr.io/${{ github.repository }}@${{ steps.build.outputs.digest }}
```

The `id-token: write` permission lets the workflow exchange its OIDC token for a short-lived
Fulcio certificate. No secrets or key files are stored or rotated.

---

## in-toto Attestations

**in-toto** (https://in-toto.io) is a framework for recording and verifying each step in a
software supply chain. An attestation is a signed statement: *"step X produced artifact Y from
input Z under policy P."*

### Predicate types commonly used with SLSA

| Predicate type | URI | Purpose |
|----------------|-----|---------|
| `slsaprovenance/v1` | `https://slsa.dev/provenance/v1` | Build provenance (builder, source, params) |
| `sbom/cyclonedx` | `https://cyclonedx.org/bom` | Software bill of materials |
| `vuln` | `https://openvex.dev/ns/v0.2.0` | Vulnerability disclosure (VEX) |
| `test-results` | `https://slsa.dev/testresults/v1` | CI test result attestation |

### Attaching an in-toto SLSA attestation with cosign

```bash
cosign attest --yes \
  --predicate provenance.json \
  --type slsaprovenance \
  ghcr.io/ORG/IMAGE@sha256:DIGEST
```

### Verifying

```bash
cosign verify-attestation \
  --type slsaprovenance \
  --certificate-identity-regexp "https://github.com/ORG/REPO/.*" \
  --certificate-oidc-issuer "https://token.actions.githubusercontent.com" \
  ghcr.io/ORG/IMAGE@sha256:DIGEST
```

---

## SBOM Signing

Generate an SBOM, then sign it as a cosign attestation so consumers can verify both content and
provenance.

```bash
# 1. Generate SBOM with Trivy
trivy image --format cyclonedx --output sbom.json ghcr.io/ORG/IMAGE:tag

# 2. Attach signed SBOM attestation
cosign attest --yes \
  --predicate sbom.json \
  --type cyclonedx \
  ghcr.io/ORG/IMAGE@sha256:DIGEST

# 3. Verify SBOM attestation
cosign verify-attestation \
  --type cyclonedx \
  --certificate-identity-regexp "https://github.com/ORG/REPO/.*" \
  --certificate-oidc-issuer "https://token.actions.githubusercontent.com" \
  ghcr.io/ORG/IMAGE@sha256:DIGEST | jq .payload | base64 -d | jq .
```

---

## GitHub Provenance Attestations

GitHub Actions provides first-party SLSA L2 provenance via the
[`actions/attest-build-provenance`](https://github.com/actions/attest-build-provenance) action.
The attestation is stored in the GitHub trust root and verifiable with the `gh` CLI.

```yaml
# Add after your build step in the workflow above
      - name: Attest build provenance
        uses: actions/attest-build-provenance@v2
        with:
          subject-name: ghcr.io/${{ github.repository }}
          subject-digest: ${{ steps.build.outputs.digest }}
          push-to-registry: true
```

Verify with:

```bash
gh attestation verify oci://ghcr.io/ORG/IMAGE@sha256:DIGEST \
  --owner ORG
```

The attestation includes the workflow ref, runner environment, source commit SHA, and trigger
event — satisfying SLSA Build L2 requirements without any additional tooling.

---

## npm and PyPI Sigstore Integration

### npm (Provenance)

npm supports SLSA provenance attestations for packages published from GitHub Actions (npm ≥ 9.5).

```bash
# Publish with provenance from GHA (requires id-token: write)
npm publish --provenance --access public
```

Consumers verify with:

```bash
npm audit signatures
```

### PyPI (Trusted Publishers + Attestations)

PyPI Trusted Publishers (OIDC-based) replaced API tokens for GHA publishing. Since 2024, PyPI
also records Sigstore attestations for packages published via trusted publisher workflows.

```yaml
# pypi-publish step in GHA
      - name: Publish to PyPI
        uses: pypa/gh-action-pypi-publish@v1
        with:
          attestations: true   # generates and uploads Sigstore attestations
```

Consumers verify PyPI attestations:

```bash
pip install pypi-attestations
python -m pypi_attestations verify dist/mypkg-1.0.0-py3-none-any.whl
```

---

## CI Integration Checklist

- [ ] Sign all release images with `cosign sign` using GHA OIDC (keyless).
- [ ] Attach SLSA provenance attestation via `actions/attest-build-provenance`.
- [ ] Generate and sign SBOM for every published image (CycloneDX or SPDX).
- [ ] Add `cosign verify` step in deployment pipelines before `kubectl apply` or `helm upgrade`.
- [ ] Set `COSIGN_EXPERIMENTAL=1` only when targeting the public Sigstore instance; omit for
  private Fulcio/Rekor deployments.
- [ ] For npm packages: add `--provenance` flag to `npm publish` in release workflows.
- [ ] For PyPI packages: enable Trusted Publishers and set `attestations: true`.
- [ ] Store image digests (not tags) in deployment manifests to prevent tag mutation attacks.

---

## Key Sources

- SLSA framework: https://slsa.dev
- Sigstore project: https://sigstore.dev
- in-toto specification: https://in-toto.io
- GitHub provenance actions: https://github.com/actions/attest-build-provenance
- npm provenance docs: https://docs.npmjs.com/generating-provenance-statements
- PyPI attestations: https://docs.pypi.org/attestations/
