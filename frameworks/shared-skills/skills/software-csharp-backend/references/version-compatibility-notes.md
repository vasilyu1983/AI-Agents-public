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
| `.NET 8` (`net8.0`) | LTS ending — verify current date, was Nov 10, 2026 as of mid-2026 | C# 12+ | Existing fleets mid-migration; not a comfortable long-term target anymore | No security patches after end of support; feature drift vs current docs and templates | Plan the `net10.0` move now — treat "still on net8.0" as a tracked migration item, not steady state |
| `.NET 9` (`net9.0`) | STS — Microsoft extended STS support from 18 to 24 months starting with .NET 9, so its end-of-support date lands the same day as .NET 8's (Nov 10, 2026 as of mid-2026); verify current date | C# 13+ | Short-horizon validation only | Offers no extra runway over `net8.0` once you account for the extended STS window — weigh that before treating it as a stepping stone | Move directly to `net10.0`; don't treat `net9.0` as a safe intermediate stop given the shared support cliff |
| `.NET 10` (`net10.0`) | Recommended greenfield baseline — LTS, GA Nov 2025, supported through ~Nov 2028 (verify current date) | C# 14 | New services and latest built-in ASP.NET Core/runtime defaults | Team/environment may still lag SDK/runtime rollout | Provide `net8.0` fallbacks only when compatibility requirements are real |

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
- When using latest framework features, ensure endpoints still compile/run under the lowest supported host target.

## Data access compatibility
- EF Core version must match the host runtime and provider support matrix.
- Dapper is broadly compatible and useful for cross-target SQL access.
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
