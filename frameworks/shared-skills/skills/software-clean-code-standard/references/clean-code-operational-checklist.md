# Clean Code Operational Checklist

Actionable rules distilled from Clean Code for day-to-day coding, reviews, and refactors.

## Naming
- Use intention-revealing names; avoid noise words and misleading terms.
- Prefer pronounceable, searchable names; avoid encodings or Hungarian notation.
- Commands are verbs, queries are nouns; keep consistent terminology across modules.

## Functions
- Keep functions small and do one thing; stay at one abstraction level per function.
- Limit parameters to three; avoid boolean flags and long parameter lists—extract objects when needed.
- Prefer clear control flow with guard clauses over deep nesting; avoid hidden side effects.
- Separate commands from queries; return data instead of mutating unexpectedly.

## Comments
- Explain intent, warnings, or legal notes only; delete redundant or outdated comments.
- Remove commented-out code; version control preserves history.

## Formatting and Structure
- Group related code vertically; keep closely related lines together and separate concepts with blank lines.
- Keep line length reasonable and indentation simple; one statement per line.
- Order dependencies: high-level context first, details later; minimize interleaving concerns.

## Objects, Data, and Classes
- Apply Single Responsibility: one reason to change per class/module.
- Keep instance variables few and coherent; constructors establish invariants.
- Hide representation; expose behavior over data. For DTOs, keep them simple and behavior-free.
- Respect the Law of Demeter: talk to friends, not strangers; avoid train-wreck calls.

## Error Handling
- Use exceptions, not error codes; avoid returning null—use exceptions, Option/Maybe, or Null Object.
- Keep try/catch blocks narrow; translate low-level exceptions to domain-specific ones.
- Do not mix error handling with normal logic; handle once, close resources deterministically.

## Boundaries and External Code
- Wrap third-party APIs behind adapters; centralize translation, validation, and error mapping.
- Write contract tests against boundaries; keep external details out of domain logic.

## Tests
- Apply FIRST: Fast, Independent, Repeatable, Self-validating, Timely.
- One assertion concept per test; use descriptive names and clear Arrange-Act-Assert structure.
- Tests should read like documentation and never share hidden state.

## Emergent Design Rules
- A design is clean when: all tests pass, no duplication, clear intent, and minimal classes/methods.
- Refactor whenever adding behavior to preserve these properties.

## Concurrency (Clean Code guidance)
- Separate concurrency concerns from business logic; isolate shared state and prefer immutability.
- Keep critical sections small; minimize locking scope and shared data.
- Use producer/consumer queues or message passing to reduce contention; test with stress and race detectors.

## Smells → Refactor Triggers (selected)
- Long function, long parameter list, flag arguments, or deep nesting → extract helpers/objects and flatten control flow.
- Divergent change or shotgun surgery → split responsibilities and introduce stable abstractions.
- Feature envy or data clumps → move behavior to the data owner and create value objects.
- Dead code and duplicated code → delete or consolidate; keep single sources of truth.
