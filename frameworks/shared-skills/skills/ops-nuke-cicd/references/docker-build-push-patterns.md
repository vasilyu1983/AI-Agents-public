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

## Push + Digest Capture Pattern
1. Build image with mutable tag (`registry/image:{BuildId}`).
2. Push tagged image.
3. Parse push output for digest (`sha256:...`).
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

## Reliability Checks
- Verify login target runs before push.
- Verify digest parsing handles push output format changes.
- Verify env file is written even when only one image is produced.
- Verify cleanup targets (`docker rmi`) run only after all required outputs are captured.

## Failure Diagnostics
- Missing digest value: inspect push logs and parsing utility.
- Wrong tag source: verify `BuildId` and repository metadata at runtime.
- Deployment drift: use digest reference, not mutable tag, in downstream deploy steps.
