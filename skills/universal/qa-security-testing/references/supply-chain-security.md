# Supply-Chain Security

Security-testing view of the supply chain: the **verification gates** that fail a pipeline when an
artifact's signature, provenance or SBOM is missing or does not match. SLSA levels, Sigstore
signing, in-toto and SBOM generation are owned by
[ops-devops-platform/references/supply-chain-security.md](../../ops-devops-platform/references/supply-chain-security.md).

## Contents

- [What to Gate On](#what-to-gate-on)
- [Verify Signatures and Attestations](#verify-signatures-and-attestations)
- [GitHub Artifact Attestations](#github-artifact-attestations)
- [npm and PyPI Provenance](#npm-and-pypi-provenance)
- [Gate Checklist](#gate-checklist)
- [Key Sources](#key-sources)

---

## What to Gate On

| Gate | Fails when | Where |
|------|-----------|-------|
| Signature | Image or blob has no valid Sigstore signature from the expected workflow identity | Deploy pipeline, admission controller |
| Provenance | No SLSA provenance, or its builder/source/ref does not match policy | Deploy pipeline |
| SBOM attestation | Release image has no signed SBOM | Release pipeline |
| Digest pinning | Manifest or workflow references a mutable tag | PR check |
| Scanner self-integrity | A security action is referenced by tag, not by commit SHA | PR check (see the Trivy incident in [container-iac-scanning.md](container-iac-scanning.md#tool-selection)) |

SLSA v1.2 (approved 2025-11-24, backward compatible with v1.1) is the current spec:
https://slsa.dev/spec/v1.2/. Test against the Build track level your policy names. The level
definitions are in the ops-devops-platform reference.

A verification test is only useful if it can fail. For each gate, keep one known-bad fixture (an
unsigned image, an attestation from another repository's workflow, a tag-referenced action) and
assert that the gate rejects it.

---

## Verify Signatures and Attestations

Cosign 2.x and later sign keylessly by default. `COSIGN_EXPERIMENTAL` is no longer needed. Always
pin the expected identity. A bare `cosign verify` without an identity check accepts any signer.

```bash
# Signature: fail unless signed by this repository's release workflow
cosign verify \
  --certificate-identity-regexp '^https://github\.com/ORG/REPO/\.github/workflows/release\.yml@' \
  --certificate-oidc-issuer 'https://token.actions.githubusercontent.com' \
  ghcr.io/ORG/IMAGE@sha256:DIGEST

# SBOM attestation (CycloneDX)
cosign verify-attestation --type cyclonedx \
  --certificate-identity-regexp '^https://github\.com/ORG/REPO/' \
  --certificate-oidc-issuer 'https://token.actions.githubusercontent.com' \
  ghcr.io/ORG/IMAGE@sha256:DIGEST > /dev/null
```

Negative test: run the same command against an image signed by a different repository. It must
exit non-zero.

---

## GitHub Artifact Attestations

Use [`actions/attest`](https://github.com/actions/attest) for new workflows. Since v4,
`actions/attest-build-provenance` is only a wrapper around it. With no `sbom-path` or predicate
inputs, `actions/attest` generates SLSA build provenance.

```yaml
permissions:
  id-token: write
  attestations: write
  artifact-metadata: write
  packages: write

# after the build step
      - name: Attest build provenance
        uses: actions/attest@1e69f48acb82d1966a394da916b4c1698aa569d6 # v4.2.2
        with:
          subject-name: ghcr.io/${{ github.repository }}
          subject-digest: ${{ steps.build.outputs.digest }}
          push-to-registry: true
```

Gate on it at deploy time:

```bash
gh attestation verify oci://ghcr.io/ORG/IMAGE@sha256:DIGEST --owner ORG
```

Artifact attestations work in public repositories on all current GitHub plans. Private and
internal repositories need GitHub Enterprise Cloud. GitHub Enterprise Server is not supported.

---

## npm and PyPI Provenance

**npm**: packages published from CI with `npm publish --provenance` carry a Sigstore provenance
statement. Consumers check registry signatures and provenance with:

```bash
npm audit signatures   # fails on invalid signatures; reports packages with verified attestations
```

**PyPI**: Trusted Publishing from GitHub Actions uploads PEP 740 attestations through
`pypa/gh-action-pypi-publish`. Verify a package against its source repository:

```bash
pip install pypi-attestations
pypi-attestations verify pypi --repository https://github.com/ORG/REPO \
  pypi:mypkg-1.0.0-py3-none-any.whl
```

---

## Gate Checklist

- [ ] Deploy pipelines run `cosign verify` or `gh attestation verify` with a pinned identity before
  `kubectl apply` or `helm upgrade`.
- [ ] Each gate has a known-bad fixture that the gate rejects in CI.
- [ ] Deployment manifests reference images by digest, not by tag.
- [ ] Every third-party action, and every security scanner action above all, is pinned to a full
  commit SHA.
- [ ] Release images carry a signed SBOM attestation.
- [ ] Dependency consumers run `npm audit signatures` or `pypi-attestations verify` where the
  ecosystem supports it.

---

## Key Sources

- SLSA v1.2 announcement: https://slsa.dev/blog/2025/11/announce-slsa-v1.2
- Cosign 2.0 release (keyless by default): https://blog.sigstore.dev/cosign-2-0-released/
- actions/attest: https://github.com/actions/attest
- npm provenance: https://docs.npmjs.com/generating-provenance-statements
- pypi-attestations CLI: https://github.com/trailofbits/pypi-attestations
