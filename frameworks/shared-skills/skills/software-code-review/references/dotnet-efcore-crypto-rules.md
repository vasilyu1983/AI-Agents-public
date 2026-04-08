# .NET/EF Core Crypto Integration Review Rules

Review rules for **C#/.NET crypto/fintech services** using **Entity Framework Core**. Practical, minimal rules focused on correctness, security, readability, and maintainability.

---

## 0. Review Scope Rule

- Review **only new or modified code** in the merge request, not the entire repository
- Feedback must be limited to changes in the diff unless new code directly interacts with existing components where consistency is important
- Do not comment on untouched legacy code

---

## 1. Correctness

- All conditional branches are handled — no missing scenarios
- Input parameters are validated at a basic level (null/empty, format, ranges)
- Methods do not return `null` when a proper result or explicit failure is expected
- No silent-fail paths — deviations lead to explicit outcomes
- No unreachable or dead code
- Calculations use `decimal` for financial values, with proper comparisons and rounding
- All dates and times use UTC
- Status transitions are valid and do not skip intermediate states
- DTO → model → database mappings are consistent and do not lose data
- Edge cases are handled: empty collections, missing data, zero values

---

## 2. Security

- No secrets in code: API keys, tokens, connection strings must come from configuration or environment variables
- Logs must not contain sensitive data: tokens, passwords, private keys
- External inputs are validated at a basic level before use
- SQL queries are not constructed manually — ORM or parameterized queries must be used
- Error messages do not expose internal technical details (stack traces, configuration values)

---

## 3. Error Handling

- Errors are handled explicitly — no silent failures
- Exceptions are not swallowed; if caught, they must be logged
- No unhandled exceptions leaking into higher layers
- External errors (DB, HTTP, API) are minimally handled: return a failure or meaningful result
- Error messages are clear but do not reveal sensitive or internal details
- Methods returning `Result` or `Result<T>` follow a consistent Success/Fail pattern

---

## 4. Async / I/O

- Async methods are used for I/O operations
- No blocking calls (`.Result`, `.Wait()`)
- No missing `await` inside async methods
- `CancellationToken` is passed when supported
- No heavy CPU work inside async methods unless intentional
- No unintended fire-and-forget calls

---

## 5. Database (EF Core)

- Database queries are simple and predictable — no dynamic SQL
- No queries inside loops leading to repeated DB calls (N+1 patterns)
- Only necessary data is loaded — avoid overusing `.Include`
- Use `AsNoTracking` for read-only scenarios
- LINQ queries remain readable and not overly complex
- Absence of data is handled explicitly — no silent null returns

---

## 6. External API

- External API calls are encapsulated in dedicated clients or services
- API responses are checked for success
- API errors result in clear failure handling
- No empty `catch` blocks
- Response data is validated before use (null checks, required fields)
- All external calls are async and respect `CancellationToken` when possible

---

## 7. Readability & Maintainability

- Names of classes, methods, and variables clearly reflect their purpose
- No dead or commented-out code
- TODO comments are acceptable if brief and relevant
- Methods perform a single, clear responsibility
- Repeated logic is extracted into helpers or shared methods
- Prefer early returns over deep nesting
- Formatting follows project conventions (`editorconfig`, style rules)

---

## 8. Unit & API Tests

- Updated logic is covered by at least one type of test: unit tests or API tests
- Minimum coverage: one success scenario
- Tests are readable and not overly complex
- Mocks are used only when necessary; simple logic is tested directly
- Tests do not depend on external services or the network
- Test names reflect expected behavior
- Key input arguments are explicitly asserted — avoid `It.IsAny<T>()` when specific values matter

---

## 9. Behavioral Infrastructure Changes

When a change alters runtime semantics (consumer commit behavior, retry/DLQ routing, failure handling, shutdown flow):

- Does this change alter commit, retry, or DLQ semantics? If yes, is the new behavior explicitly opt-in?
- Are legacy extension points (shared subscriptions, custom `IMessageSubscription`, fan-out consumers) still exercised by tests?
- Is `OperationCanceledException` kept outside the normal failure path? Cancellation must exit the processing loop before failure routing kicks in
- Are failure-routing failures (e.g., failed DLQ publish) isolated to the affected partition, not killing the whole consumer task?
- For high-risk behavioral work, use the review-first fix loop: implement → review → isolate highest-risk gap → fix only the risky slice → revalidate. This is not cleanup — it is how behavioral infrastructure work becomes safe

---

## 10. Merge Requests

- MR contains logically related changes — feature, bugfix, or refactor
- If refactoring is included, it is separated from functional changes (structurally or via commits)
- No temporary, debug, or commented-out code
- MR size remains reasonable and easy to review
- All CI checks pass
- Commit messages and branch names reflect the purpose of the change
