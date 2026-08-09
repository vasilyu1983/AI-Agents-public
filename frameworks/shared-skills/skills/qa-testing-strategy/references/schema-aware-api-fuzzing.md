# Schema-Aware API Fuzzing

Use this reference when contract validation is necessary but not sufficient. Schema-aware fuzzing explores valid and invalid inputs derived from the API schema, which helps catch parser, coercion, validation, and error-handling drift.

## When to add fuzzing

- Public or partner-facing APIs with many parameters
- High-risk validation logic: auth, payments, pricing, search, filtering
- Teams already using OpenAPI and wanting stronger edge-case coverage
- Bugs keep escaping because hand-written examples miss weird combinations

## Suggested stack

- Contract tests: compatibility and breaking-change detection
- Schema fuzzing: generated edge cases from the contract
- Integration smoke: real persistence, auth, and dependency behavior

## Decision rules

```text
Need to prove API quality?
    │
    ├─ Only compatibility between producer and consumer
    │   └─ Contract test
    │
    ├─ Validation, coercion, parser, and error-shape risk
    │   └─ Contract test + schema-aware fuzzing
    │
    └─ Real side effects, persistence, idempotency, or auth flow
        └─ Add integration tests
```

## Good targets

- Required vs optional fields
- Boundary values and format violations
- Enum drift and unknown values
- Nested objects and array constraints
- Error status codes and error-body stability

## Avoid

- Running unbounded fuzzing in every PR gate
- Treating fuzzing as a replacement for contract or integration tests
- Using random data without reproducible seeds or saved failing cases
