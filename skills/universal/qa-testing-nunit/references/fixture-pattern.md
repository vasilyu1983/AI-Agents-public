# Fixture Pattern

## Purpose
Use this guide when building reusable setup for NUnit API/component/integration tests.

## Fixture Boundaries
- Keep fixture scope equal to resource lifetime.
- Avoid one global fixture for unrelated scenarios.
- Share only immutable configuration and expensive dependencies.
- Keep default fixture focused on one handler/use case or one controller/test family.

## Per-Controller/Test-Family Model (API Suites)
- Use one fixture per controller/test family.
- Each fixture owns required runtime dependencies:
  - database container and migrations,
  - HTTP stub servers (for example WireMock),
  - web application factory,
  - HTTP/typed clients.
- Reset mutable state in `[SetUp]`.
- Dispose all owned dependencies in `[OneTimeTearDown]`.
- Do not introduce a single global shared setup fixture across unrelated controllers.

## Recommended Pattern
1. Start with one fixture per use case or per controller/test family.
2. Build resource factory methods and `Given...` scenario setup methods in fixture class.
3. Start dependencies in `[OneTimeSetUp]` only when reuse is safe.
4. Reset mutable state in `[SetUp]` before each test.
5. Dispose resources in `[OneTimeTearDown]` with defensive cleanup.

## Fixture and Test Class Pairing
- Pair each fixture with the test class that uses it, and name them as a pair.
- Keep fixture fluent and scenario-oriented:
  - `GivenCommand(...)`
  - `GivenUpstreamSucceeds()`
  - `GivenValidationPassed()`
  - `Send(...)`
- Return fixture instance from setup methods to keep Arrange phase linear.

## API Full-Cycle Fixture Pattern
- For API-to-database tests, use one base fixture per controller/test family that:
  - wraps API client calls,
  - manages DB verification helpers,
  - keeps scenario setup close to test intent.
- Create fixture inside `[SetUp]` and dispose in `[TearDown]` to avoid state leakage.
- Keep expensive infra (containers, network, wiremock host, web app factory) at controller fixture scope, not repository-global scope.
- Keep builder helpers (`GivenRequest()`, `GivenEntity()`) in fixture or dedicated builder files.

## Composition Rules
- Prefer small fixtures combined by helper methods.
- Keep test data builders outside fixture lifecycle logic.
- Hide infrastructure wiring behind clear fixture API.
- When scenario count becomes large, split fixture into partial files by scenario family while keeping one shared base fixture file.

## Failure Hygiene
- Capture startup logs when fixture init fails.
- Fail fast on missing ports/connection strings.
- Never swallow teardown exceptions silently.
