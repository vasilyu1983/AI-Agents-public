# C# Language Practices

## Naming and readability
- Use domain terms in class and method names; avoid transport terms inside domain/application layers.
- Prefer explicit types when inferred type hides intent; use `var` only when the right side is obvious.
- Keep methods focused: one behavior, one reason to change.
- Replace boolean flag arguments with explicit methods or options types.

## Immutability and state control
- Prefer immutable request/response models (`record` with `init` or constructor-only properties).
- Make mutable state private and minimal; expose behavior, not setters.
- Use readonly collections for outputs from domain and query handlers.

## Nullability discipline
- Enable nullable reference types and treat warnings as real defects.
- Validate boundary inputs immediately; keep internal code mostly null-free.
- Use guard clauses for required values and fail with precise argument messages.
- Avoid pervasive `!`; fix source nullability contracts instead.

## Exceptions and failure modeling
- Throw exceptions for unexpected/technical faults, not normal domain outcomes.
- Use typed/domain error results for validation and business-rule failures.
- Preserve stack trace (`throw;`) when rethrowing.
- Add context once at boundary logs; do not log-and-rethrow repeatedly.

## Async/await and cancellation
- Pass `CancellationToken` to every async dependency supporting cancellation.
- Never block on async (`.Result`, `.Wait()`); keep call chains async end-to-end.
- Use `Task.WhenAll` for independent I/O operations.
- Configure explicit timeouts for network and external dependencies.
- Avoid fire-and-forget in request paths; route background work through durable workers.

## Practical checks
- Are all public async methods cancellation-aware?
- Are expected failures represented without exceptions?
- Can a new engineer infer behavior from names alone?
