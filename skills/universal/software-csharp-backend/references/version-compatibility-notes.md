# Version Compatibility Notes

## Scope and intent
- Use this guide when framework compatibility materially affects design decisions.
- Prefer compatibility-safe defaults first, then adopt newer features where targets allow.
- Treat `.NET Framework 4.8` and `netstandard2.0` as maintenance/interoperability paths; prefer modern `.NET` for new services.

## Target matrix
| Target | Support posture | Language ceiling (practical) | Primary use | Risk notes | Fallback strategy |
| --- | --- | --- | --- | --- | --- |
| `.NET Framework 4.8` (`net48`) | Legacy maintenance | C# 7.3 typical | Existing enterprise apps/libraries | Older BCL and package constraints | Keep adapters thin, isolate modern APIs behind interfaces, multi-target where feasible |
| `netstandard2.0` | Compatibility contract | Feature set constrained by consumer runtimes | Shared libraries consumed by mixed runtimes | Limited API surface vs modern .NET | Keep core abstractions here, add runtime-specific implementations in `net8.0+` targets |
| `.NET 8` (`net8.0`) | LTS at or near end of support — check the support policy page for the date | C# 12+ | Existing fleets mid-migration; not a comfortable long-term target anymore | No security patches after end of support; feature drift vs current docs and templates | Plan the `net10.0` move now — treat "still on net8.0" as a tracked migration item, not steady state |
| `.NET 9` (`net9.0`) | STS — from .NET 9, STS support is 24 months, so .NET 9 ends support on the same day as .NET 8; check the support policy page for the date | C# 13+ | Short-horizon validation only | Offers no extra runway over `net8.0` | Move directly to `net10.0`; don't treat `net9.0` as a safe intermediate stop given the shared support cliff |
| `.NET 10` (`net10.0`) | LTS; the greenfield baseline only while it is the newest LTS — confirm the current LTS and end-of-support date on the support policy page | C# 14 | New services that want this release's built-in ASP.NET Core/runtime defaults | Team/environment may still lag SDK/runtime rollout | Provide `net8.0` fallbacks only when compatibility requirements are real |
| `.NET 11` (`net11.0`) | STS (24-month support window, which ends close to .NET 10's LTS end); check the support policy page for release status and dates | Newer C# version (check the C# language-versioning docs) | Teams that upgrade yearly and want the newest runtime | Do not target a pre-GA release in production; RC go-live support windows are short | Stay on `net10.0` (LTS) unless the team commits to a yearly upgrade cadence |

## Language feature gates
- Treat C# 12/13/14 features as optional unless all targets support them.
- Keep shared-domain models compatible with lower targets when libraries are multi-targeted.
- Avoid introducing syntax/features that force unnecessary target upgrades.
- Prefer behavior-preserving fallback patterns when down-targeting:
  - Primary constructors -> explicit constructors
  - Newest collection/syntax sugar -> standard object/collection initialization
  - TFM-specific APIs -> interface abstraction + target-specific implementation

## ASP.NET Core feature compatibility
- `.NET 10` is the preferred baseline for new ASP.NET Core hosts; `.NET 8` remains the common fallback where upgrade timing or platform policy lags.
- `netstandard2.0` is not a host target; use it for shared abstractions and helpers only.
- For API projects, keep middleware and endpoint design stable across targets:
  - deterministic error contracts,
  - explicit health/readiness behavior,
  - explicit authentication/authorization and rate-limiting configuration.
- `.NET 10` favors built-in OpenAPI (`AddOpenApi`, `MapOpenApi`) and central exception handling (`AddProblemDetails`, `IExceptionHandler`).
- Treat `.WithOpenApi()` as deprecated and verify diagnostic behavior changes when upgrading exception handling middleware.
- When using framework features newer than the lowest supported host target, ensure endpoints still compile/run under the lowest supported host target.

## net8 → net10 upgrade traps
Check these behavior changes during the host upgrade, not after:
- EF10 requires the .NET 10 runtime. You cannot upgrade EF ahead of the host.
- EF10 changes the default translation of parameterized collections (padded per-value parameters instead of `OPENJSON`), which changes query plans. See `references/efcore-persistence-patterns.md`.
- EF10 on SQL Server compatibility level 170+/Azure SQL migrates `nvarchar` JSON columns to `json` in the first migration.
- Built-in OpenAPI documents default to OpenAPI 3.1.
- Cookie-authenticated API endpoints now return 401/403 instead of redirecting to login or access-denied pages.
- `IExceptionHandler` diagnostics suppression (`SuppressDiagnosticsCallback`) changes which handled exceptions still emit diagnostics.
- `.WithOpenApi()` is deprecated.
- Minimal APIs gain built-in validation (`AddValidation()`). Decide whether it replaces or coexists with existing validators.

## Data access compatibility
- EF Core version must match the host runtime and provider support matrix.
- Dapper is broadly compatible and useful for cross-target SQL access. It is not Native AOT-safe; use Dapper.AOT or ADO.NET for AOT hosts.
- MongoDB driver support can vary by runtime generation; verify package/runtime matrix before upgrades.
- Keep repository interfaces target-agnostic; isolate provider/runtime-specific APIs in infrastructure implementations.

## Resilience and observability package compatibility
- `Microsoft.Extensions.*` and modern resilience packages vary by target; pin versions explicitly.
- Prefer policy abstractions in application code and framework/package-specific wiring in composition root.
- Keep telemetry contracts stable (log properties, metric names, trace tags) regardless of target runtime.
- If a modern package is unavailable for a lower target, provide a minimal fallback policy with explicit limitations.
- `TimeProvider` should replace `ISystemClock`-style abstractions for modern hosts and new test code.
- `HybridCache` is a modern host-level option, but shared libraries should not depend on it unless the library is intentionally runtime-specific.

## Multi-targeting patterns
- Use multi-targeting for reusable libraries that need broad compatibility.
- Typical library examples:
  - `TargetFrameworks: netstandard2.0;net8.0`
  - `TargetFrameworks: net48;netstandard2.0`
  - `TargetFrameworks: net48;net8.0;net10.0`
- Use conditional compilation only for target-specific behavior, not core business logic:
  - `#if NETSTANDARD2_0`
  - `#if NET48`
  - `#if NET8_0_OR_GREATER`

## Migration guidance
- Prefer staged migration over big-bang upgrades:
  1. Stabilize test coverage and public contracts.
  2. Multi-target shared libraries (`netstandard2.0` + modern TFM).
  3. Move hosts to modern .NET runtime.
  4. Remove legacy-only compatibility code once consumers are migrated.
- Validate package compatibility and runtime behavior at each stage.
- Keep deployment rollback-compatible across mixed-version windows.
- Validate OpenAPI generation, ProblemDetails behavior, and resilience policy semantics during host upgrades, not just compile success.

## Compatibility review checklist
- Are required targets explicitly documented for this component?
- Does new code compile and test on every declared target?
- Are framework-specific APIs isolated from shared abstractions?
- Is there a fallback path for the lowest supported target?
- Are package versions pinned to a known compatible range per target?
