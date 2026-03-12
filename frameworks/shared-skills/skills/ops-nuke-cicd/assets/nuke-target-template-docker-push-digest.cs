using System.IO;
using Nuke.Common;
using Nuke.Common.Tools.Docker;

// Copy this pair for each produced image. Repositories may output one or many images.
string? ServiceTag;
string? ServiceDigestTag;

Target BuildServiceImage => definition => definition
    .DependsOn(PublishService)
    .Executes(() =>
    {
        var commitSha = CommitSha != string.Empty ? CommitSha : Repository.Commit;
        ServiceTag = $"{DockerRegistry}/{DockerImagePrefix}/service:{BuildId}";

        DockerTasks.DockerBuild(s => s
            .SetPath("publish/service")
            .SetFile("docker-files/service.Dockerfile")
            .SetPull(true)
            .SetTag(ServiceTag)
            .SetBuildArg(
                $"COMMIT_HASH={commitSha}",
                $"BUILD_DATE={BuildDate}",
                $"BUILD_ID={BuildId}",
                $"CI={!IsLocalBuild}"));
    });

Target PushServiceImage => definition => definition
    .DependsOn(BuildServiceImage)
    .DependsOn(DockerLogin)
    .Executes(() =>
    {
        var outputs = DockerTasks.DockerImagePush(s => s.SetName(ServiceTag));
        var digest = ReadDigits(outputs); // expected format: sha256:<digest>
        ServiceDigestTag = $"{DockerRegistry}/{DockerImagePrefix}/service@{digest}";
    });

Target OutputImages => definition => definition
    .After(PushServiceImage)
    .Executes(() =>
    {
        var outputFilePath = IsLocalBuild
            ? Path.Combine(".", "deploy.env")
            : Path.Combine(CiProjectDirectory, "deploy.env");

        using var outputFile = new StreamWriter(outputFilePath);

        if (ServiceDigestTag is not null)
        {
            outputFile.WriteLine($"DOCKER_IMAGE_DEPLOY_SERVICE={ServiceDigestTag}");
        }
    });
