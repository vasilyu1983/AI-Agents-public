# Dotnet Coding Standards

## Project structure
- Organize by capability and layer, not by technical type only.
- Keep API/presentation thin; place use-case logic in application layer.
- Keep infrastructure adapters isolated behind interfaces.

## Dependency boundaries
- Enforce inward dependency direction: presentation -> application -> domain.
- Prevent domain from referencing infrastructure packages.
- Avoid static service locators and hidden global dependencies.

## Dependency injection
- Register dependencies by role and lifetime:
  - `Singleton` for stateless/shared expensive resources.
  - `Scoped` for request-bound services and data sessions.
  - `Transient` for lightweight stateless components.
- Validate container at startup when possible.
- Prefer constructor injection; avoid method/property injection except narrow framework cases.

## Configuration and options
- Bind strongly typed options per bounded context.
- Validate options on startup (`ValidateOnStart`) for critical settings.
- Keep secrets outside source control and outside plain config files.
- Separate runtime policies (timeouts, retry counts, limits) into options.

## Layering rules
- Keep transport DTOs and persistence documents outside core domain models.
- Map data at boundaries; do not leak ORM/driver entities into domain/application.
- Keep cross-cutting concerns (logging, metrics, auth) in decorators/middleware where possible.

## Implementation checklist
- Does each project have one clear responsibility?
- Does each dependency point inward?
- Are options typed, validated, and environment-safe?
