# Test Categories and Filters

## Purpose
Control test scope with predictable category filters so local and CI runs execute the intended suites.

## Category Strategy
- Treat the repo's category set as a local contract, not a NUKE default. Read it from the test code before changing any filter.
- Keep the category names in one place (for example a constants class shared by tests and `Build.cs`) and build every filter from it.
- Use one naming style for every category (all singular or all plural). Mixed forms such as `Db` next to `Components` invite typos that silently drop suites.
- Keep category assignment explicit in test attributes.
- Map each category to exactly one target and one filter. The unit target excludes every non-unit category.

## Filter Patterns
Category names below (`Api`, `Db`, `Component`) are illustrative; substitute the repo's own set.
- Unit-only exclusion pattern:
```text
TestCategory!=Component&TestCategory!=Db&TestCategory!=Api
```
- Single-category pattern:
```text
TestCategory=Api
```

## Target Mapping Example
```csharp
// One place for category names; tests use the same constants in [Category(...)].
static class TestCategories
{
    public const string Api = "Api";
    public const string Db = "Db";
    public const string Component = "Component";
    public static readonly string[] NonUnit = [Api, Db, Component];
}

static string Exclude(params string[] categories) =>
    string.Join("&", categories.Select(c => $"TestCategory!={c}"));

Target UnitTest => _ => _
    .Executes(() => DotNetTasks.DotNetTest(s => s
        .SetFilter(Exclude(TestCategories.NonUnit))));

Target ApiTest => _ => _
    .Executes(() => DotNetTasks.DotNetTest(s => s
        .SetFilter($"TestCategory={TestCategories.Api}")));

Target DbTest => _ => _
    .Executes(() => DotNetTasks.DotNetTest(s => s
        .SetFilter($"TestCategory={TestCategories.Db}")));
```

## Composition Rules
- Keep one composed CI target (for example `TestAll`) that triggers the build, every category target, and the coverage merge.
- When a new category is added, add its constant, its target, and its entry in the unit exclusion list in the same change.
- When a legacy test orchestration path is replaced, remove its targets and environment plumbing from the graph instead of leaving them dormant.

## Validation Checks
- Verify each category has at least one test.
- Verify unit target excludes integration categories.
- Verify CI composed target includes all mandatory categories.
- Verify filter strings are identical between local and CI paths when scope should match.

## Common Failure Modes
- Category typo causes tests to silently skip.
- Broad exclusion filters hide suites that should run.
- Project-level test target mismatch (wrong `.csproj`) drops expected tests.
- Running parallel `dotnet test` on the same project output causes intermittent file-lock/MSBuild failures.
