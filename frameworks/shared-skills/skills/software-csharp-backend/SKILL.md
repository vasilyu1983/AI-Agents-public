---
name: software-csharp-backend
description: "Applies C# and .NET backend standards. Use when shaping API boundaries, data access, resilience, observability, or security defaults."
compatibility: Portable core. Works on Claude Code and Codex.
version: "1.1"
last_validated: 2026-07-11
---

# C# Backend Engineering

## Quick Reference

| Decision | Default | Notes |
|----------|---------|-------|
| Runtime | .NET 10 + C# 14 (LTS, GA Nov 2025, supported through ~Nov 2028) | .NET 8 LTS ends Nov 10, 2026 — verify current dates at [dotnet support policy](https://dotnet.microsoft.com/en-us/platform/support/policy/dotnet-core); treat continued .NET 8 targeting as a tracked migration, not a comfortable steady state |
| API style | Minimal API for new endpoints | Controllers for large CQRS surface with many filters/action results |
| Persistence (SQL, write-heavy) | EF Core | Use Dapper when query shapes are complex and hand-tuned SQL wins |
| Persistence (SQL, query-heavy) | Dapper | Pair with EF Core for write path if aggregates exist |
| Persistence (document) | MongoDB driver | Use when schema variability is genuine, not habitual |
| Background worker | `IHostedService` / `BackgroundService` | Add lease, graceful shutdown, and poison-message handling from day one |
| Resilience | `Microsoft.Extensions.Resilience` (Polly v8) | Standard pipeline: retry → circuit breaker → timeout |
| OpenAPI | Built-in ASP.NET Core OpenAPI (`Microsoft.AspNetCore.OpenApi`) | Do not add Swashbuckle unless repo already uses it |

Route other tasks:
- NUnit fixture design, WireMock/Testcontainers setup, or flake reduction → `$qa-testing-nunit`
- `nuke/Build.cs`, CI target sequencing, or artifact publication → `$ops-nuke-cicd`
- Legacy `ILogger` or Serilog rewrite automation → `$dev-structured-logs`

## When to Use This Skill

- Building or reviewing C# / .NET backend services
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
2. Choose runtime shape before implementation details.
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
Load `references/testing-practices.md`.
8. Add logs, traces, metrics, health probes, and operability defaults.
Load `references/observability-standards.md`, and for API/runtime deployment defaults load `references/runtime-ops-checklist.md`. If the service is distributed or cloud-native by design, also load `references/scenario-guides.md` for the Aspire-oriented profile.
9. Validate auth, validation, and secrets handling.
Load `references/security-baseline.md`.
10. Run feedback loop validation for changed behavior.
For NUKE-based repositories, run `BuildAll`, `LocalUnitTest`, `ApiTest` (when relevant), and `TestAll`; use `$ops-nuke-cicd` for pipeline-target edits.
11. Run final review against anti-pattern checklist.
Load `references/code-review-checklist.md`.

## ASCII Flow

```text
C# backend task
  -> Identify API, worker, data access, or service boundary
  -> Confirm .NET version, hosting model, DI, and persistence choices
  -> Design validation, auth, errors, retries, and observability
  -> Implement bounded slice with unit and integration tests
  -> Check EF, async, cancellation, and deployment traps
  -> Run focused verification and capture follow-up risks
```

## Decision Tree
- If the issue is naming, nullability, exception usage, or async flow, read `references/csharp-language-practices.md`.
- If the issue is project layout, DI, configuration, or layering, read `references/dotnet-coding-standards.md`.
- If the issue is service boundaries or clean architecture drift, read `references/backend-architecture-principles.md`.
- If the issue is module boundaries, composition hosts, or modular-monolith tradeoffs, read `references/modular-architecture-principles.md`.
- If the issue is API style, middleware ordering, ProblemDetails, OpenAPI, request timeouts, rate limiting, health/readiness, or graceful shutdown, read `references/aspnet-core-api-patterns.md`.
- If the issue is SQL/Mongo/EF access, pagination, transactions, idempotency, or N+1, read `references/data-access-patterns.md`.
- If EF Core is selected for relational persistence, also read `references/efcore-persistence-patterns.md`.
- If the issue is system profile specific (high-throughput API, event-driven worker, multi-tenant service, distributed/Aspire host), read `references/scenario-guides.md`.
- If the issue is retry/timeout/circuit behavior, cancellation propagation, standard resilience handler behavior, or worker reliability, read `references/reliability-and-resilience.md` and `references/resilience-policy-defaults.md`.
- If the issue is container/runtime readiness, startup config validation, HybridCache defaults, or deployment reliability gates, read `references/runtime-ops-checklist.md`.
- If the issue is target framework constraints, package/API compatibility, multi-targeting, or migration between `.NET Framework`/`netstandard2.0` and modern `.NET`, read `references/version-compatibility-notes.md`.
- If the issue is flaky tests, fake time control, or weak coverage strategy, read `references/testing-practices.md`.
- If the issue is logs/traces/metrics/health checks, read `references/observability-standards.md`.
- If the issue is input validation, auth boundaries, secret handling, or secure defaults, read `references/security-baseline.md`.
- If the task is reviewing a PR for backend quality risks, read `references/code-review-checklist.md`.
- If the task is designing or fixing build-test pipeline loop behavior, use `$ops-nuke-cicd`.
- If the task needs deep HTTP controller + CQRS error-contract design, keep it in this skill and align handler/result patterns to the repository's existing conventions rather than introducing new framework requirements by default.

## Do / Avoid

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
- Treating EF Core defaults as safe under load: lazy loading, implicit tracking, and missing query shaping frequently create hidden cost.
- Using retries around non-idempotent handlers, transaction scopes, or third-party calls without dedupe or timeout coordination.
- Shipping background workers without graceful shutdown, lease or lock ownership, or poison-message handling.
- Binding configuration directly into services without options validation, startup failure checks, or explicit secret handling.
- Choosing Native AOT for a service that depends on EF Core, reflection-based JSON, or dynamic plugin loading — EF Core is not fully AOT-compatible today, and unbounded reflection breaks at publish/trim time. Verify each dependency's AOT/trim compatibility before committing, or keep the service on the standard runtime.
- Instantiating `new HttpClient()` per call or per request instead of resolving it through `IHttpClientFactory`/`AddHttpClient<T>` — this exhausts sockets under load (`new HttpClient()` disposed per call) or goes DNS-stale (one long-lived static instance) if done by hand.
- Leaving Server GC (the ASP.NET Core default) unexamined in a memory-constrained or high-density container deployment — Server GC sizes heaps to the visible processor count, which can over-allocate memory on small/shared containers. Use `DOTNET_GCHeapHardLimit`/DATAS (Dynamic Adaptation to Application Sizes — opt-in on .NET 8, default-on from .NET 9) or switch to Workstation GC for high-density, low-CPU hosting; keep Server GC for dedicated, CPU-bound API pods.

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
- [Skill Sources](data/sources.json): curated primary sources (last verified 2026-07-11) plus modular-architecture supporting references.

### Templates
- [API Host Template](assets/api-host-template.cs)
- [Service Class Template](assets/service-class-template.cs)
- [Options Configuration Template](assets/options-configuration-template.cs)
- [Resilient HTTP Client Template](assets/resilient-http-client-template.cs)
- [Dapper Query Handler Template](assets/dapper-query-handler-template.cs)
- [Mongo Repository Template](assets/mongo-repository-template.cs)
- [Test Data Builder Template](assets/test-data-builder-template.cs)
- [Pull Request Checklist Template](assets/pull-request-checklist-template.md)

### Related Skills

- [software-backend](../software-backend/SKILL.md) → General backend patterns and multi-language guidance
- [software-architecture-design](../software-architecture-design/SKILL.md) → System-level design and decomposition
- [software-security-appsec](../software-security-appsec/SKILL.md) → Security audits and threat modeling
- [software-code-review](../software-code-review/SKILL.md) → Review workflow and judgment patterns
- [qa-testing-nunit](../qa-testing-nunit/SKILL.md) → NUnit fixture design and test infrastructure
- [ops-nuke-cicd](../ops-nuke-cicd/SKILL.md) → NUKE build pipeline and CI/CD targets
- `dev-structured-logs` → Structured logging migration

## Freshness Protocol

When users ask version-sensitive questions about .NET, C#, or ASP.NET Core, verify current information before answering.

### Trigger Conditions

- "What's the latest .NET LTS version?"
- "Should I use EF Core or Dapper?"
- "What's new in ASP.NET Core / C#?"
- "Is [pattern/library] still recommended for .NET?"

### How to Freshness-Check

1. Start from `data/sources.json` (official docs, release notes, support policies).
2. Run a targeted web search for the specific .NET component.
3. Prefer official Microsoft docs over blogs for versions and support windows.

### What to Report

- **Current landscape**: what is stable and widely used now
- **Emerging trends**: what is gaining traction (and why)
- **Deprecated/declining**: what is falling out of favor (and why)
- **Recommendation**: default choice + 1-2 alternatives, with trade-offs

## Fact-Checking

- Known bugs, regressions, framework/compiler/runtime footguns, and version-specific crash or workaround guidance must be verified against current primary web sources before being treated as current fact.
- Use web search/web fetch to verify current external facts, versions, pricing, deadlines, regulations, or platform behavior before final answers.
- Prefer primary sources; report source links and dates for volatile information.
- If web access is unavailable, state the limitation and mark guidance as unverified.

## Learnings Loop

Before applying this skill on a non-trivial task, read `learnings.consolidated.md` in this directory (and `learnings.md` if present).

After applying it, if you encountered a pattern worth remembering, a mistake worth preventing, or a domain fact that surprised you, append one dated bullet to `learnings.md` via `agents-skills-feedback-loop/scripts/append_learning.py`. Do not modify `SKILL.md` itself.

