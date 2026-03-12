# Backend Architecture Principles

## Service design goals
- Optimize for maintainability and correctness first, then performance.
- Keep use cases explicit and independently testable.
- Make invariants enforceable inside domain/application boundaries.

## Clean architecture application
- Presentation: protocol concerns (HTTP/messages), auth entry, request/response mapping.
- Application: orchestration of use cases, transaction scope coordination, domain policy calls.
- Domain: pure business rules and invariants.
- Infrastructure: database, messaging, external APIs, filesystem, cache implementations.

## Boundary contracts
- Define small interfaces at application boundary based on use-case needs.
- Return domain/app results that encode expected errors.
- Keep retry/timeouts out of domain logic; place them in infrastructure decorators.

## Maintainable service patterns
- Use one service/handler per use case with clear input/output model.
- Prefer composition over inheritance for workflow assembly.
- Keep branching shallow by extracting named private steps.
- Introduce decorators for cross-cutting policies (authorization, metrics, retries).
- For CQRS handlers, prefer MediatR + FluentResults with `Handle` boundary and `DoHandle` functional pipeline.

## Evolution rules
- Add new behavior by extending use cases, not by growing god services.
- Require architectural tests or review checks for forbidden dependencies.
- Refactor duplicated orchestration into reusable components only after repeated need.

## When to delegate
- For deep API controller and CQRS endpoint patterns, use `$csharp-api-cqrs`.
