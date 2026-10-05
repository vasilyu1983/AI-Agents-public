using System.Linq;
using Nuke.Common;
using Nuke.Common.IO;
using Nuke.Common.Tools.DotNet;

// Target names, category names, and project paths are illustrative; replace them with the repo's own.
// Keep category names in this one place and build every filter from it.
static class TestCategories
{
    public const string Api = "Api";
    public const string Db = "Db";
    public const string Component = "Component";
    public static readonly string[] NonUnit = [Api, Db, Component];
}

static string ExcludeCategories(params string[] categories) =>
    string.Join("&", categories.Select(c => $"TestCategory!={c}"));

AbsolutePath[] UnitTestProjects =
[
    RootDirectory / "tests/unit/Your.Project.Tests/Your.Project.Tests.csproj"
];

AbsolutePath[] ApiTestProjects =
[
    RootDirectory / "tests/api/Your.Project.Tests.Api/Your.Project.Tests.Api.csproj"
];

AbsolutePath[] DbTestProjects =
[
    RootDirectory / "tests/db/Your.Project.Tests.Db/Your.Project.Tests.Db.csproj"
];

// This template assumes a VSTest-compatible `dotnet test` flow.
// If the repo uses Microsoft.Testing.Platform, align logger and coverage arguments first.
string NormalizePath(AbsolutePath path) => path.ToString().Replace("\\", "/");
string CoverageResultsDirectory => NormalizePath(ArtifactsDirectory / "coverage-report");
string JUnitLogger(string suffix) =>
    $"junit;LogFilePath={NormalizePath(ArtifactsDirectory / $"{{assembly}}-{suffix}.xml")};MethodFormat=Class;FailureBodyFormat=Verbose";

Target UnitTest => definition => definition
    .DependsOn(BuildAll)
    .OnlyWhenDynamic(IsBuildRequired)
    .Executes(() =>
    {
        foreach (var project in UnitTestProjects)
        {
            DotNetTasks.DotNetTest(s => s
                .SetProjectFile(project)
                .EnableNoRestore()
                .EnableNoBuild()
                .SetVerbosity(DotNetVerbosity.minimal)
                .SetConfiguration(Configuration)
                .SetFilter(ExcludeCategories(TestCategories.NonUnit))
                .AddLoggers(JUnitLogger("unit-test-result"))
                .SetTestAdapterPath(".")
                .SetDataCollector("XPlat Code Coverage;Format=cobertura")
                .SetResultsDirectory(CoverageResultsDirectory));
        }
    });

Target ApiTest => definition => definition
    .DependsOn(BuildAll)
    .After(UnitTest)
    .OnlyWhenDynamic(IsBuildRequired)
    .Executes(() =>
    {
        foreach (var project in ApiTestProjects)
        {
            DotNetTasks.DotNetTest(s => s
                .SetProjectFile(project)
                .EnableNoRestore()
                .EnableNoBuild()
                .SetVerbosity(DotNetVerbosity.minimal)
                .SetConfiguration(Configuration)
                .SetFilter($"TestCategory={TestCategories.Api}")
                .SetDataCollector("XPlat Code Coverage;Format=cobertura")
                .SetResultsDirectory(CoverageResultsDirectory)
                .AddLoggers(JUnitLogger("api-test-result"))
                .SetTestAdapterPath("."));
        }
    });

Target DbTest => definition => definition
    .DependsOn(BuildAll)
    .After(UnitTest)
    .OnlyWhenDynamic(IsBuildRequired)
    .Executes(() =>
    {
        foreach (var project in DbTestProjects)
        {
            DotNetTasks.DotNetTest(s => s
                .SetProjectFile(project)
                .EnableNoRestore()
                .EnableNoBuild()
                .SetVerbosity(DotNetVerbosity.minimal)
                .SetConfiguration(Configuration)
                .SetFilter($"TestCategory={TestCategories.Db}")
                .SetDataCollector("XPlat Code Coverage;Format=cobertura")
                .SetResultsDirectory(CoverageResultsDirectory)
                .AddLoggers(JUnitLogger("db-test-result")));
        }
    });

Target TestAll => definition => definition
    .Triggers(BuildAll, UnitTest, ApiTest, DbTest, MergeCodeCoverageReports);
