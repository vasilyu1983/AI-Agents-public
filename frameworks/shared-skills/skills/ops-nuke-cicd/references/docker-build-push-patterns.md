# Docker Build Push Patterns

## Purpose
Build and publish container images with traceability and immutable deployment references.

## Image Count
- Do not hardcode image count assumptions in shared guidance.
- Some repositories publish one image, others multiple images.
- Pricing is only one example and currently publishes two image outputs (private API and migrator).

## Build Pattern
- Tag images with CI build identifier for traceability.
- Pass `COMMIT_HASH`, `BUILD_DATE`, and `BUILD_ID` as build args.
- Use `SetPull(true)` when base-image freshness matters.
- Use Dockerfiles when the repo needs custom package installs, non-default users, or multi-stage assembly logic.
- Consider SDK-native `dotnet publish /t:PublishContainer` when a repo can ship an image without a custom Dockerfile.

## Push + Digest Capture Pattern
1. Build image with mutable tag (`registry/image:{BuildId}`).
2. Push tagged image.
3. Prefer a structured digest output from the CI provider or action; parse push output only in raw Docker CLI flows.
4. Emit immutable deploy reference (`registry/image@sha256:...`).

## Example
```csharp
var imageTag = $"{DockerRegistry}/{DockerImagePrefix}/privateapi:{BuildId}";
DockerTasks.DockerBuild(s => s.SetTag(imageTag));
var outputs = DockerTasks.DockerImagePush(s => s.SetName(imageTag));
var digest = ReadDigits(outputs); // returns "sha256:..."
var deployRef = $"{DockerRegistry}/{DockerImagePrefix}/privateapi@{digest}";
```

## deploy.env Contract
Write exported deploy variables for downstream jobs (one variable per produced image):
```text
DOCKER_IMAGE_DEPLOY_SERVICE_A=<registry>/<repo>/service-a@sha256:...
DOCKER_IMAGE_DEPLOY_SERVICE_B=<registry>/<repo>/service-b@sha256:...
```

## SDK-Native PublishContainer: Chiseled Images and Non-Root Defaults

`dotnet publish /t:PublishContainer` produces images without a Dockerfile. Key properties for hardened images from a NUKE target:

- **Non-root is the default since .NET 8.** The container runs as UID 1654 (`app`) automatically — do not override to `root` unless explicitly required.
- **Default port is 8080** (not 80). Update load-balancer and health-check configs accordingly.
- **Chiseled base image** (Ubuntu Chiseled — minimal attack surface, no shell): set `ContainerFamily=jammy-chiseled` or `ContainerFamily=noble-chiseled`.
- **Override user** via `ContainerUser` MSBuild property when a specific UID is required.

NUKE target pattern — pass MSBuild properties via `DotNetPublish`:

```csharp
Target PublishContainerSdk => _ => _
    .DependsOn(Compile)
    .Executes(() =>
    {
        DotNetTasks.DotNetPublish(s => s
            .SetProject(ApiProject)
            .SetConfiguration(Configuration)
            .SetProperty("PublishProfile", "DefaultContainer")
            .SetProperty("ContainerRegistry", DockerRegistry)
            .SetProperty("ContainerRepository", $"{DockerImagePrefix}/privateapi")
            .SetProperty("ContainerImageTag", BuildId)
            // Chiseled Ubuntu image — minimal OS surface, no shell
            .SetProperty("ContainerFamily", "jammy-chiseled")
            // Non-root is the default (UID 1654 "app"); set explicitly only when overriding
            // .SetProperty("ContainerUser", "app")
        );
    });
```

Chiseled-image constraints:
- No shell inside the container — exec-form `ENTRYPOINT` only (SDK publishes this correctly by default).
- Health checks that shell out (`/bin/sh -c`) will fail — use TCP or HTTP probes instead.
- Verify base image tag availability; `jammy-chiseled` corresponds to Ubuntu 22.04. Use `noble-chiseled` for Ubuntu 24.04.

Source: https://learn.microsoft.com/en-us/dotnet/core/containers/sdk-publish

## Supply-Chain Metadata
- Keep digest as the deployment contract.
- Emit provenance and SBOM metadata when the workflow and registry support them.
- If the pipeline runs on GitHub Actions with `docker/build-push-action`, prefer the action's `digest` output and enable `provenance`/`sbom` explicitly when required.

## Reliability Checks
- Verify login target runs before push.
- Verify digest parsing handles push output format changes when structured outputs are unavailable.
- Verify env file is written even when only one image is produced.
- Verify cleanup targets (`docker rmi`) run only after all required outputs are captured.

## Failure Diagnostics
- Missing digest value: inspect push logs and parsing utility.
- Wrong tag source: verify `BuildId` and repository metadata at runtime.
- Deployment drift: use digest reference, not mutable tag, in downstream deploy steps.
