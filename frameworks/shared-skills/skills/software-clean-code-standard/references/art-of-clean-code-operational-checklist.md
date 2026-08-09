# The Art of Clean Code Operational Checklist

Actionable guidance focused on readability, intent, and humane codebases.

## Intent and Storytelling
- Lead with intent: each module/function starts from “what it does and why,” not how.
- Keep one narrative thread per function; avoid mixing setup, business rules, and orchestration in a single block.
- Prefer expressive names that match domain language; keep naming consistent across files and layers.

## Simplicity and Structure
- Make the happy path straight-line; push error/edge cases to guard clauses.
- Keep functions small and single-purpose; align all statements to one abstraction level.
- Remove incidental complexity: collapse redundant layers, delete unused parameters/flags, and simplify conditionals.
- Choose the simplest data structure that fits; wrap domain concepts in value objects to encode rules once.

## Clarity Over Cleverness
- Avoid “smart” tricks (implicit mutation, overloading semantics, condensed boolean logic) when a clearer version exists.
- Replace boolean soups with named predicates; extract readability helpers for compound conditions.
- Prefer composition and plain data over inheritance and global state; keep dependency graphs shallow.

## Error Handling and Safety
- Validate inputs early; fail fast with actionable messages.
- Isolate external calls; standardize timeouts, retries, and error mapping in one place.
- Log decisions and failures at boundaries; include key identifiers and outcomes, not raw data dumps.

## Comments and Documentation
- Comment intent, constraints, and trade-offs; delete comments that restate code.
- Co-locate short “why” notes near non-obvious decisions; keep longer rationale in adjacent docs when necessary.
- Remove dead/commented-out code promptly.

## Testing for Confidence
- Tests must read like examples: clear Arrange-Act-Assert with domain-meaningful names.
- Cover happy path, edges, and failure modes; ensure tests fail without the code under test.
- Keep tests isolated and deterministic; control time, randomness, and IO with fakes.

## Incremental Improvement
- When touching code, rename for clarity, split long functions, and remove duplication—avoid scope creep beyond the touched area.
- Prefer small, reversible commits; keep refactors behavior-preserving and separately labeled from features.
