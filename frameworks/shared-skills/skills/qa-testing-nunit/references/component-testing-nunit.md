# Component Testing with NUnit

## Purpose
Use this guide for in-process tests that validate collaboration between multiple components.

## Boundaries
- Include real composition root for the targeted module.
- Replace only out-of-process dependencies when needed.
- Keep database/message broker real when behavior depends on integration semantics.

## Pattern
1. Build service provider with test configuration.
2. Seed state using deterministic builders.
3. Execute use case through public component API.
4. Assert output plus state transitions.

## API-Component Hybrid Pattern
- Use this when tests run through HTTP but still verify database and message side effects.
- Keep web app host real and infrastructure production-like for owned dependencies.
- Use WireMock for external services and Testcontainers for owned stateful services.
- Keep per-test fixture object as orchestration layer for Given/When helper methods.
- Keep fixture scope aligned to one controller/test family for migration and parallel execution.

## Controller-Focused Migration Rule
- When migrating from feature-file grouping, move to controller-focused files and fixtures.
- Keep one fixture per controller/test family and avoid shared global setup fixture for all controllers.

## Guidance
- Prefer component tests for handler + repository + mapper behavior.
- Keep each test focused on one end-to-end component scenario.
- Avoid asserting private implementation details.

## Exit Criteria
- Component tests catch wiring issues that unit tests miss.
- Test runtime remains acceptable by limiting permutations.
