# CI Output Contracts and Provenance

## Table of Contents

- [Purpose](#purpose)
- [Contract Principles](#contract-principles)
- [Core Outputs](#core-outputs)
- [Provider-Native Exports](#provider-native-exports)
- [Provenance and SBOM](#provenance-and-sbom)
- [deploy.env Behavior](#deployenv-behavior)
- [Change Management Rules](#change-management-rules)

## Purpose
Define stable outputs that downstream jobs can consume while using provider-native output channels when they are available.

## Contract Principles
- Keep artifact locations deterministic and filenames stable across local and CI contexts.
- Treat output contracts as public interfaces of the pipeline.
- Prefer CI-native environment or step-output files when the pipeline is provider-specific.
- Keep `deploy.env` as a portable repository contract, not the only output mechanism.

## Core Outputs
- `artifacts/coverage-report/**/coverage.cobertura.xml`
- `artifacts/coverage-report/index.html` (or equivalent HTML summary)
- `artifacts/*-unit-test-result.xml`
- `artifacts/*-api-test-result.xml`
- `artifacts/*-db-test-result.xml`
- `deploy.env` when downstream deployment expects repository-emitted variables

## Provider-Native Exports
- GitHub Actions: write shared env values to `$GITHUB_ENV` and step outputs to `$GITHUB_OUTPUT`.
- Azure Pipelines or other CI systems: use their native output primitives first, then mirror into `deploy.env` only when downstream jobs need a file contract.
- Avoid parsing console logs to recover values that the CI system already exposes structurally.

## Provenance and SBOM

- Keep image digest as the immutable deployment identifier.
- Emit provenance and SBOM metadata when registry and CI support them.
- If the workflow uses `docker/build-push-action`, prefer its structured `digest` output over parsing push logs.

### SBOM Generation from a NUKE Target

Generate an SBOM as a first-class pipeline artifact. Two tool options:

**Option A — Microsoft sbom-tool** (https://github.com/microsoft/sbom-tool):

```csharp
Target GenerateSbom => _ => _
    .DependsOn(Publish)
    .Executes(() =>
    {
        // sbom-tool must be on PATH or installed as a global .NET tool
        ProcessTasks.StartProcess(
            "sbom-tool",
            $"generate -b {ArtifactsDirectory} -bc {RootDirectory} -pn {ProductName} -pv {GitVersion.NuGetVersion} -ps YourOrg -nsb https://your-org.example/sbom",
            workingDirectory: RootDirectory
        ).AssertZeroExitCode();
    });
```

**Option B — CycloneDX .NET tool** (`dotnet-CycloneDX`):

```csharp
Target GenerateSbom => _ => _
    .DependsOn(Restore)
    .Executes(() =>
    {
        ProcessTasks.StartProcess(
            ToolPathResolver.GetPathExecutable("dotnet"),
            $"CycloneDX {SolutionFile} -o {ArtifactsDirectory / "sbom"} --json",
            workingDirectory: RootDirectory
        ).AssertZeroExitCode();
    });
```

Emit the SBOM file as a CI artifact alongside coverage and test results.

### GitHub Artifact Attestations (SLSA Build Provenance)

Use GitHub's `attest-build-provenance` action to sign NuGet packages and container images with SLSA L2 provenance. Wire the attestation step after push so the digest is resolved. Source: https://docs.github.com/en/actions/concepts/security/artifact-attestations

In the NUKE-driven GitHub Actions workflow:

```yaml
- name: Attest container image
  uses: actions/attest-build-provenance@v2
  with:
    subject-name: ${{ env.DOCKER_REGISTRY }}/${{ env.IMAGE_NAME }}
    subject-digest: ${{ env.IMAGE_DIGEST }}   # sha256:... written to GITHUB_ENV by NUKE target

- name: Attest NuGet package
  uses: actions/attest-build-provenance@v2
  with:
    subject-path: artifacts/packages/*.nupkg
```

NUKE target responsibility: write the resolved image digest to `$GITHUB_ENV` (key `IMAGE_DIGEST`) before the attestation step runs.

### NuGet Lockfiles for Reproducible Restores

Enable lockfile-pinned restores to prevent silent dependency drift between local and CI:

```csharp
Target Restore => _ => _
    .Executes(() =>
    {
        DotNetTasks.DotNetRestore(s => s
            .SetProjectFile(Solution)
            // Enforce locked-mode in CI; omit locally to allow updates
            .When(IsServerBuild, x => x.SetProperty("RestoreLockedMode", "true"))
        );
    });
```

Commit `packages.lock.json` files generated after setting `RestorePackagesWithLockFile=true` in project files or `Directory.Build.props`. CI restore will fail fast if any dependency deviates from the lock.

## deploy.env Behavior
- Local run: commonly write to repo root `./deploy.env`.
- CI run: commonly write to `${CiProjectDirectory}/deploy.env`.
- Include only variables with known values; avoid placeholder keys.

## Change Management Rules
- If output names or locations change, update all CI collectors, attestation steps, and deploy consumers in the same change.
- Keep one source of truth for artifact directory variables.
- Add guard checks when contract files or digests are mandatory for downstream targets.
