using Nuke.Common;
using Nuke.Common.IO;
using Nuke.Common.Tools.DotNet;

AbsolutePath[] ApiTestProjects =
[
    RootDirectory / "tests/api/Your.Project.Tests.Api/Your.Project.Tests.Api.csproj"
];

Target UnitTest => definition => definition
    .DependsOn(BuildAll)
    .OnlyWhenDynamic(IsBuildRequired)
    .Executes(() =>
    {
        DotNetTasks.DotNetTest(s => s
            .EnableNoRestore()
            .EnableNoBuild()
            .SetVerbosity(DotNetVerbosity.minimal)
            .SetConfiguration(Configuration)
            .SetFilter("TestCategory!=ComponentTests&TestCategory!=ApiTest")
            .AddLoggers($"junit;LogFilePath={ArtifactsDirectory}\\{{assembly}}-unit-test-result.xml;MethodFormat=Class;FailureBodyFormat=Verbose")
            .SetTestAdapterPath(".")
            .SetNoBuild(IsLocalBuild)
            .SetDataCollector("Code Coverage;Format=cobertura")
            .SetResultsDirectory($"{ArtifactsDirectory}/coverage-report")
        );
    });

Target ApiTest => definition => definition
    .After(UnitTest)
    .OnlyWhenDynamic(IsBuildRequired)
    .Executes(() =>
    {
        DotNetTasks.DotNetTest(s => s
            .EnableNoRestore()
            .EnableNoBuild()
            .SetVerbosity(DotNetVerbosity.minimal)
            .SetConfiguration(Configuration)
            .SetFilter("TestCategory=ApiTest")
            .SetDataCollector("Code Coverage;Format=cobertura")
            .SetResultsDirectory($"{ArtifactsDirectory}/coverage-report")
            .AddLoggers($"junit;LogFilePath={ArtifactsDirectory}\\{{assembly}}-api-test-result.xml;MethodFormat=Class;FailureBodyFormat=Verbose")
            .SetTestAdapterPath(".")
            .SetNoBuild(IsLocalBuild)
        );
    });

Target DbTest => definition => definition
    .After(UnitTest)
    .OnlyWhenDynamic(IsBuildRequired)
    .Executes(() =>
    {
        DotNetTasks.DotNetTest(s => s
            .EnableNoRestore()
            .EnableNoBuild()
            .SetConfiguration(Configuration)
            .SetFilter("TestCategory=DbTests")
            .SetDataCollector("XPlat Code Coverage;Format=cobertura")
            .SetResultsDirectory($"{ArtifactsDirectory}/coverage-report")
            .AddLoggers($"junit;LogFilePath={ArtifactsDirectory}/{{assembly}}-db-test-result.xml;MethodFormat=Class;FailureBodyFormat=Verbose")
            .SetNoBuild(IsLocalBuild));
    });

Target TestAll => definition => definition
    .Triggers(BuildAll, UnitTest, ApiTest, DbTest, MergeCodeCoverageReports);
