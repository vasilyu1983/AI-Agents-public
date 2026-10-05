# Publishing And Support

Use this file when the request is about releasing or maintaining a developer-facing product.

## Release Hygiene

- Ship changelogs and migration notes with every notable release.
- Test install-from-registry, not just workspace usage.
- Sign or attest packages when the ecosystem supports it.
- Monitor package size, transitive dependencies, and install time.

## Support Signals

- Track time-to-first-success in quickstarts.
- Mine issues and support tickets for recurring friction.
- Keep deprecation policy explicit: timeline, replacement, and compatibility notes.

## Pre-Publish Checklist

- [ ] Tests pass from a clean disposable checkout (`npm ci && npm test`)
- [ ] Build output is current and committed (or generated in CI)
- [ ] `package.json` fields verified: `main`, `types`, `exports`, `files`
- [ ] Bundle size checked with `size-limit` or the actual tarball produced by [`npm pack`](https://docs.npmjs.com/cli/v11/commands/npm-pack/) (packing prints the filename, not the archive bytes)
- [ ] Install tested from tarball: `npm pack && npm install ./pkg.tgz` in a fresh project
- [ ] Every published entry point loads without error: `import` (and `require()` from CJS on your Node floor) for ESM-only; both CJS and ESM entry points for dual builds
- [ ] `CHANGELOG.md` updated; migration guide written for any breaking change
- [ ] Provenance attestation enabled — prefer npm trusted publishing (OIDC, CI `id-token: write` permission, no static token in CI) over the manual `--provenance` flag path
- [ ] Publish credentials scoped and short-lived: no long-lived npm/PyPI tokens sitting in CI secrets if trusted publishing is available for the registry; 2FA enforced on maintainer accounts

## Publisher Supply-Chain Hardening

- Prefer trusted publishing over static publish tokens; restrict the trust configuration to the intended repository, workflow and release environment. Verify provider support and attestation eligibility at [npm’s official docs](https://docs.npmjs.com/trusted-publishers/).
- Keep release credentials least-privileged and short-lived; isolate dependency installation from publish authority and do not expose cloud or registry credentials to unrelated build steps.
- Review the packed artifact’s lifecycle scripts and bundled files; reject unexpected scripts or secret-bearing files before publication.
- Protect release workflows and signing identities; rehearse token/key revocation and publish-channel containment.
- For consuming packages or editor extensions, installation-script policy, provenance review and upgrade controls belong to [dev-dependency-management](../../dev-dependency-management/SKILL.md) and [software-security-appsec](../../software-security-appsec/SKILL.md).

## Installers and Self-Update

Use this checklist when a CLI ships its own installer or self-updater instead of relying on a package registry.

- **Verify a signature, not only a checksum.** Check the archive against a public key or signing identity pinned out of band: carried in the running binary, embedded in the install script, or held in a package-manager keyring. A checksum file fetched from the same origin as the archive only proves the download is complete. Anyone who can replace the archive can replace the checksum too. On a missing or failed signature, refuse to install, and offer no "continue anyway" default.
- **Rotate signing keys as a release event.** Sign the next key with the current one, or announce it through a channel separate from the download host, before you sign releases with it.
- **Keep the previous binary until the new one passes a self-check.** Stage the new binary beside the old one. Run a post-install self-check: it reports its version, loads config, and runs a no-op command. Then swap with an atomic rename, not an in-place overwrite. If the self-check fails, keep or restore the previous binary and say why. Remove the old binary only after the rollback window closes.
- **Ship one install script per platform family: `sh` and `ps1`.** Commit both to the repo and serve them from stable URLs. Each script must:
  - detect OS and architecture before it downloads anything;
  - take an explicit channel or version argument;
  - verify the signature as above;
  - offer a non-interactive mode for CI and fleet installs, with no prompts and a non-zero exit on any failure;
  - offer a dry run that plans the install without writing anything;
  - stop on the first error (`set -eu`, plus `pipefail` where the shell supports it; `$ErrorActionPreference = 'Stop'` in PowerShell);
  - in `sh`, wrap the body in a function called on the last line, to reduce partial-download execution risk; prefer downloading and verifying the complete file before execution;
  - document how to download, inspect, and then run the script, as an alternative to piping it into a shell.
- **Set halt criteria before exposure.**
  - As a publisher: before the first cohort, name the halt metrics (crash rate, self-check failures, plugin-load or session-resume failures), their thresholds, and who can halt the rollout.
  - Halt the publisher’s rollout on signing-identity surprises, failed self-checks, rollback events or compromised release channels; resume after a verified canary.

## DX Metrics

The numeric targets below are **heuristic — unsourced**, not benchmarks. Replace them with product-specific budgets and baselines before treating them as release gates.

| Metric | Target | Signal when off |
|--------|--------|-----------------|
| Local feedback-loop time (save → test result / reload) | < 2 seconds for unit tests, < 1 second for HMR | Slow inner loop kills iteration speed faster than any CI metric |
| Time-to-first-API-call | < 5 minutes from `npm install` | Onboarding friction; simplify the quickstart |
| Onboarding drop-off rate | Track per step in the guide | High drop-off at a specific step → missing example or broken link |
| SDK version adoption (latest major) | Rising adoption vs your previous major's baseline (no fixed benchmark) | Breaking-change pain or missing migration docs |
| Error rate by method | < 1% for common operations | Fix SDK error messages and docs; don't just add FAQ entries |
| Support ticket clustering | Track top-3 recurring topics | Recurring questions → undiscoverable API surface |
| Developer NPS / satisfaction | Quarterly pulse; structured interviews | Quantitative metrics miss the "this feels bad" signals |
