# Supply-Chain Security

*Use when:* Designing artifact provenance, signing, SBOM generation, or promotion checks in CI/CD, or assessing a builder against SLSA.

## SLSA Build Track

Choose an approved specification at [SLSA](https://slsa.dev/spec/) and record its version and track in the assessment. The following summarizes the [v1.2 Build requirements](https://slsa.dev/spec/v1.2/build-requirements) as a named specification, not a claim about the latest release.

| Level | Required guarantee | Evidence to inspect |
|-------|--------------------|---------------------|
| Build L1 | Provenance identifies the artifact and how it was built; it may be unsigned | Output digest and distributed provenance |
| Build L2 | Hosted platform generates authentic provenance | Platform trust boundary and consumer authenticity verification |
| Build L3 | L2 plus unforgeable provenance and isolation between builds | Signing material inaccessible to build steps, trusted generation, ephemeral environments and cache isolation |

Hermeticity is distinct from isolation and is not a Build L3 requirement. A tool name, signed image, or provenance action alone does not establish a level. Assess producer and platform controls, including the consumer's verification policy. Source-track requirements are separate.

Use authenticated provenance as the initial delivery control; raise the target level when the threat model or an identified contract requires stronger build isolation. Do not infer procurement or regulatory requirements from an industry label. See [Build track basics](https://slsa.dev/spec/v1.2/build-track-basics).

## Signing and Verification

[Cosign](https://docs.sigstore.dev/cosign/signing/signing_with_containers/) supports OIDC-based keyless signing as well as key-backed signing. For CI with a supported OIDC issuer, prefer keyless signing and bind verification to the expected workflow identity, issuer, and immutable artifact digest. When OIDC is unavailable or the trust model requires controlled keys, choose a managed key service and define rotation and revocation.

Fulcio issues a short-lived identity certificate; Rekor provides transparency logging in the public Sigstore flow. Check the selected deployment's trust roots, logging behavior, and offline bundle support before relying on them. Certificate expiry alone does not invalidate a signature made within its validity period when the verification evidence establishes that time.

Promotion must reject missing or invalid required signatures and attestations. Successful cryptographic verification establishes origin and integrity; separately check whether the builder, source revision, predicate, and artifact meet release policy.

## SBOM and Attestations

Use in-toto statements to bind provenance, SBOMs, and other evidence to artifact digests. Choose SPDX or CycloneDX according to the consumer's required schema; emitting both is useful only when consumers need both.

Capture dependencies during the build and generate an SBOM for the final artifact. Artifact scanning also supports retrospective inventories, but neither method guarantees all components are visible. Record generator version, scope, omissions, and subject digest. An SBOM's existence is not a vulnerability verdict.

[Syft](https://github.com/anchore/syft) produces SBOMs; [GUAC](https://github.com/guacsec/guac) correlates SBOMs, provenance, and vulnerability evidence across artifacts. Add GUAC when cross-repository dependency queries justify operating another service.

## CI Integration

1. Read the selected CI provider's supported attestation workflow and repository/plan availability. For GitHub, start with [artifact attestations](https://docs.github.com/en/actions/concepts/security/artifact-attestations) and follow its linked generation guide. Check action inputs and supported release references in the action repository before writing YAML.
2. Build and push the artifact once, capture the resulting digest, then generate provenance and the SBOM for that same digest. Grant OIDC and registry write permissions only to the jobs that need them.
3. Pin ordinary actions to reviewed commit SHAs. For reusable workflows, obey the provider's reference rules and call them at `jobs.<job_id>.uses`, with `needs` and declared inputs; they are not step actions. See [GitHub reusable workflows](https://docs.github.com/en/actions/how-tos/reuse-automations/reuse-workflows).
4. For an existing `slsa-github-generator` integration, consult its [container generator instructions](https://github.com/slsa-framework/slsa-github-generator/blob/main/internal/builders/container/README.md) for exact tag and permission requirements. Check maintenance status before selecting it for new work; do not substitute a floating major tag or claim L3 merely because the filename contains `slsa3`.
5. Configure verification before promotion to validate the digest, expected signer/issuer, trusted builder and source, and required attestation predicates. Test rejection for absent, mismatched, and invalid evidence.
6. In Kubernetes admission, enforce the same policy for workload images, including init containers and applicable ephemeral containers. Read the target policy engine's image-verification documentation and deployed API support before producing policy YAML.

## Failure Traps

- Mutable tags break the binding between a promoted image and its evidence; verify and deploy by digest.
- A signature from any trusted issuer is too broad; constrain the expected workflow identity and builder.
- A valid SBOM attestation can describe a different artifact; check its subject digest and expected predicate.
- A self-hosted runner can sit outside the assessed builder's trust boundary; document that boundary and isolation evidence before assigning a level.
- Public transparency logs can reveal repository or identity metadata; check the selected service's behavior before attesting private builds.

Sources: [SLSA](https://slsa.dev/spec/) · [Sigstore](https://docs.sigstore.dev/) · [in-toto](https://in-toto.io/) · [GitHub attestations](https://docs.github.com/en/actions/concepts/security/artifact-attestations)
