---
name: software-csharp-backend
description: "Applies C# and .NET backend standards to ASP.NET Core APIs, EF Core, Dapper, and workers. Use when shaping API boundaries, data access, resilience, or observability."
compatibility: Portable core. Works on Claude Code and Codex.
version: "1.1"
last_validated: 2026-07-11
---

# C# Backend Engineering

## Quick Reference

| Decision | Default | Notes |
|----------|---------|-------|
| Runtime | Current .NET LTS and its C# version | Look up the current LTS and its end date on the [dotnet support policy](https://dotnet.microsoft.com/en-us/platform/support/policy/dotnet-core) page before naming a version. Treat any target within a year of end of support as a tracked migration, not a steady state. Choose the current LTS by default; choose a newer STS only if the team upgrades every year |
| API style | Minimal API for new endpoints | Controllers for large CQRS surface with many filters/action results |
| Persistence (SQL, write-heavy) | EF Core | Use Dapper when query shapes are complex and hand-tuned SQL wins |
| Persistence (SQL, query-heavy) | Dapper | Pair with EF Core for write path if aggregates exist |
| Persistence (document) | MongoDB driver | Use when schema variability is genuine, not habitual |
| Background worker | `IHostedService` / `BackgroundService` | Add lease, graceful shutdown, and poison-message handling from day one |
| Resilience | `Microsoft.Extensions.Resilience` (Polly v8) | `AddStandardResilienceHandler()` runs five strategies, outermost first: rate limiter → total timeout → retry → circuit breaker → attempt timeout. It retries **all** HTTP methods by default. Override the defaults for unsafe methods and for tight deadlines. Retry at one layer only: a handler added to a client that `ConfigureHttpClientDefaults` (for example, service defaults) already wraps, or an app-level retry around a retrying client or EF execution strategy, multiplies attempts. See `references/resilience-policy-defaults.md` |
| OpenAPI | Built-in ASP.NET Core OpenAPI (`Microsoft.AspNetCore.OpenApi`) | Do not add Swashbuckle unless repo already uses it |

Route other tasks:
- NUnit fixture design, WireMock/Testcontainers setup, or flake reduction → `$qa-testing-nunit`
- `nuke/Build.cs`, CI target sequencing, or artifact publication → `$ops-nuke-cicd`
- Legacy `ILogger` or Serilog rewrite automation → `$dev-structured-logs`

## When to Use This Skill

- Building or reviewing C# / .NET backend services (this skill is the library's C#/.NET owner; `software-backend` routes .NET work here)
- Choosing between ASP.NET Core API styles (controller, minimal API, background worker)
- Implementing data access with EF Core, Dapper, or MongoDB
- Adding resilience, observability, or security baselines to .NET services
- Refactoring .NET backend code or detecting common anti-patterns

## When NOT to Use This Skill

- **General backend patterns (Node.js, Python, Go, Rust)** → [software-backend](../software-backend/SKILL.md)
- **NUnit fixture design and test infrastructure** → [qa-testing-nunit](../qa-testing-nunit/SKILL.md)
- **NUKE pipeline targets and CI/CD** → [ops-nuke-cicd](../ops-nuke-cicd/SKILL.md)
- **ILogger/Serilog migration automation** → `dev-structured-logs`
- **System architecture beyond a single service** → [software-architecture-design](../software-architecture-design/SKILL.md)
- **Security audits and threat modeling** → [software-security-appsec](../software-security-appsec/SKILL.md)

## Workflow
1. Classify the requested change (new feature, refactor, bug fix, review).
2. Choose runtime shape before implementation details. For target-framework constraints, multi-targeting, or legacy migrations, load `references/version-compatibility-notes.md`.
Load `references/scenario-guides.md` and, for HTTP services, `references/aspnet-core-api-patterns.md`.
3. Apply language and coding standards.
Load `references/csharp-language-practices.md` and `references/dotnet-coding-standards.md`.
4. Confirm architecture and boundaries before editing internals.
Load `references/backend-architecture-principles.md` and `references/modular-architecture-principles.md`.
5. Choose persistence and consistency strategy from query/write shape.
Load `references/data-access-patterns.md`; if EF Core is selected, load `references/efcore-persistence-patterns.md`.
6. Add resilience behavior for outbound I/O and long-running work.
Load `references/reliability-and-resilience.md` and `references/resilience-policy-defaults.md`.
7. Define tests by risk and boundary.
Load `references/testing-practices.md`; for a new NUnit component-test fixture, start from `assets/test-fixture-template-nunit.cs`.
8. Add logs, traces, metrics, health probes, and operability defaults.
Load `references/observability-standards.md`, and for API/runtime deployment defaults load `references/runtime-ops-checklist.md`. If the service is distributed or cloud-native by design, also load `references/scenario-guides.md` for the Aspire-oriented profile.
9. Validate auth, validation, and secrets handling.
Load `references/security-baseline.md`.
10. Run feedback loop validation for changed behavior.
Run the repository's own build, unit-test and API-test targets (for a NUKE-based repository, the build targets it defines); use `$ops-nuke-cicd` for pipeline-target edits.
11. Run final review against anti-pattern checklist.
Load `references/code-review-checklist.md`.

## Do / Avoid

**Cancellation and deadline contract.**

Accept `CancellationToken` at every cancellable request and worker boundary and propagate it through database, HTTP, queue, and delay calls. Derive child timeouts from the remaining parent deadline when one exists; for queue and scheduled work, define an operation deadline and combine it with host-shutdown cancellation. Document dependencies that cannot honor cancellation. Do not convert client disconnects or deadline expiry into generic 500s. In tests, cancel during an external call and verify work stops without committing a partial mutation or leaking a background task.

Rule: `rules/dotnet/csharp.md` loads this invariant when Claude edits a matching file.

| Do | Avoid |
|----|-------|
| Keep application services small and explicit about dependencies | Coupling domain logic directly to HTTP, DB driver types, or framework-specific classes |
| Return deterministic domain/application results for expected failures | Swallowing exceptions or replacing root causes with vague error messages |
| Pass `CancellationToken` through every async layer and external call | Letting cancellation stop at the controller while downstream calls continue |
| Model options with `IOptions<T>` validation; fail fast on invalid startup config | Binding configuration directly into services without options validation |
| Choose API style intentionally; keep middleware ordering explicit | Mixing minimal APIs, controllers, and bespoke endpoint frameworks without a clear error-shape policy |
| Use built-in ASP.NET Core OpenAPI and ProblemDetails before adding third-party wrappers | Adding Swashbuckle or MediatR when built-in plumbing is sufficient |
| Keep persistence choices aligned to use-case shape, not team habit | Using retries without timeout and idempotency guarantees |
| Make telemetry and security checks part of definition of done | Shipping endpoints without structured logs, traces, metrics, and health signals |
| Write tests at unit and integration seams separately | Mixing unit and integration concerns in the same test fixture |
| — | Using `async void` outside event handlers |
| — | Sharing one `DbContext` instance across concurrent operations/threads |
| — | Captive dependencies (singleton depending on scoped service) |

## Known Traps

- Mixing minimal APIs, controllers, and bespoke endpoint frameworks without a clear contract strategy or error-shape policy.
- Letting cancellation stop at the controller boundary while downstream HTTP, EF Core, queue, or cache calls continue running.
- Treating EF Core defaults as safe under load: lazy loading, implicit tracking, and missing query shaping frequently create hidden cost. Two or more collection `Include`s in one query multiply rows (cartesian explosion); see `references/efcore-persistence-patterns.md`.
- Using retries around non-idempotent handlers, transaction scopes, or third-party calls without dedupe or timeout coordination.
- Shipping background workers without graceful shutdown, lease or lock ownership, or poison-message handling.
- Binding configuration directly into services without options validation, startup failure checks, or explicit secret handling.
- Choosing Native AOT before checking the target EF Core version's [NativeAOT support and restrictions](https://learn.microsoft.com/en-us/ef/core/performance/nativeaot-and-precompiled-queries), serializer metadata, and dynamic loading requirements. Plain Dapper is not AOT-safe because it uses runtime reflection and IL emit; under AOT use raw ADO.NET or [Dapper.AOT](https://aot.dapperlib.dev/). Verify each dependency's trim/AOT support with an actual publish and fail the publish on IL2xxx/IL3xxx trim/AOT warnings; otherwise retain the standard runtime.
- Creating and disposing an owning `HttpClient`/handler per request can exhaust ports. Default to short-lived factory clients; a long-lived client with `SocketsHttpHandler.PooledConnectionLifetime` configured for expected DNS changes is also valid. For cookie-dependent sessions, check handler pooling and cookie isolation before using the factory ([Microsoft lifetime guidance](https://learn.microsoft.com/en-us/dotnet/fundamentals/networking/http/httpclient-guidelines)).
- Leaving GC mode unexamined for the deployment shape. On net8, Server GC (the ASP.NET Core default) sizes heaps to the visible processor count and can over-allocate on small or shared containers. There, consider opting into DATAS (Dynamic Adaptation to Application Sizes), `DOTNET_GCHeapHardLimit`, or Workstation GC. On net9+, DATAS is already on by default. For dedicated, throughput-bound pods, measure first and disable DATAS only if the data supports it; check the DATAS docs page for the target framework's current behavior.

## Common Anti-Patterns

- Building `clean architecture` layers that are mostly pass-through wrappers with no boundary or policy value.
- Returning exceptions for expected domain outcomes instead of explicit result or error contracts.
- Sharing repository abstractions everywhere even when the real need is a focused query handler or aggregate persistence boundary.
- Hiding cross-cutting behavior inside ad hoc helpers instead of using middleware, filters, options, or resilience handlers deliberately.
- Using integration tests as the only safety net while unit seams, fake time, and deterministic failure cases stay untested.

## Navigation

### References
- [C# Language Practices](references/csharp-language-practices.md)
- [Dotnet Coding Standards](references/dotnet-coding-standards.md)
- [Backend Architecture Principles](references/backend-architecture-principles.md)
- [Modular Architecture Principles](references/modular-architecture-principles.md)
- [ASP.NET Core API Patterns](references/aspnet-core-api-patterns.md)
- [Data Access Patterns](references/data-access-patterns.md)
- [EF Core Persistence Patterns](references/efcore-persistence-patterns.md)
- [Scenario Guides](references/scenario-guides.md)
- [Reliability and Resilience](references/reliability-and-resilience.md)
- [Resilience Policy Defaults](references/resilience-policy-defaults.md)
- [Testing Practices](references/testing-practices.md)
- [Observability Standards](references/observability-standards.md)
- [Runtime Ops Checklist](references/runtime-ops-checklist.md)
- [Version Compatibility Notes](references/version-compatibility-notes.md)
- [Security Baseline](references/security-baseline.md)
- [Code Review Checklist](references/code-review-checklist.md)
- [Skill Sources](data/sources.json): curated primary sources plus modular-architecture supporting references.

### Templates
- [API Host Template](assets/api-host-template.cs)
- [Service Class Template](assets/service-class-template.cs)
- [Options Configuration Template](assets/options-configuration-template.cs)
- [Resilient HTTP Client Template](assets/resilient-http-client-template.cs)
- [Dapper Query Handler Template](assets/dapper-query-handler-template.cs)
- [Mongo Repository Template](assets/mongo-repository-template.cs)
- [Test Data Builder Template](assets/test-data-builder-template.cs)
- [NUnit Test Fixture Template](assets/test-fixture-template-nunit.cs)
- [Pull Request Checklist Template](assets/pull-request-checklist-template.md)

### Related Skills

- [software-backend](../software-backend/SKILL.md) → General backend patterns and multi-language guidance
- [software-architecture-design](../software-architecture-design/SKILL.md) → System-level design and decomposition
- [software-security-appsec](../software-security-appsec/SKILL.md) → Security audits and threat modeling
- [software-code-review](../software-code-review/SKILL.md) → Review workflow and judgment patterns
- [qa-testing-nunit](../qa-testing-nunit/SKILL.md) → NUnit fixture design and test infrastructure
- [ops-nuke-cicd](../ops-nuke-cicd/SKILL.md) → NUKE build pipeline and CI/CD targets
- `dev-structured-logs` → Structured logging migration

Known bugs, regressions, framework/compiler/runtime footguns, and version-specific crash or workaround guidance must be verified against current primary web sources before being treated as current fact. Start from `data/sources.json`, and prefer official Microsoft docs over blogs for versions and support windows.

## Learnings Loop

When prior decisions or pitfalls are relevant, consult `learnings.consolidated.md` if present; use `learnings.md` only for needed history or as the available fallback. Otherwise skip both.

After applying it, if you encountered a pattern worth remembering, a mistake worth preventing, or a domain fact that surprised you, append one dated bullet to `learnings.md` via `agents-skills-feedback-loop/scripts/append_learning.py`. Do not modify `SKILL.md` itself.
