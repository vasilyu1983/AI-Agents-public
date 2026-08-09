# Code Complete Operational Checklist

Pragmatic construction rules distilled from Code Complete for authors and reviewers.

## Design and Decomposition
- Define responsibilities before coding; split by cohesion/coupling—high cohesion inside modules, low coupling across.
- Favor information hiding: expose minimal interfaces, keep volatile details behind stable abstractions.
- Separate policy from implementation; isolate IO/integration behind adapters to keep core logic testable.
- Choose simple designs that satisfy current requirements; avoid speculative generality.

## API and Routine Design
- Write short, focused routines with single, clear purposes; keep a consistent abstraction level.
- Prefer clear parameter lists: ≤3–4 params; avoid control booleans—use enums or parameter objects.
- Make side effects explicit; separate queries (no state change) from commands (clear state change).
- Use assertions and pre/postconditions at boundaries; fail fast on invalid inputs.

## Naming and Readability
- Names express intent and units; avoid abbreviations and noise words.
- Keep related code close; use vertical spacing to separate concepts; one statement per line.
- Replace magic numbers/strings with named constants; document units and ranges.

## Defensive Programming
- Validate external inputs and configuration; sanitize before use.
- Handle errors once per layer; translate low-level exceptions into domain errors.
- Use guard clauses to handle error cases early; keep normal flow straight-line.
- Prefer immutable data or minimal mutation; encapsulate shared state.

## Control Flow and Complexity
- Reduce nesting with early returns; avoid deeply nested conditionals/loops.
- Simplify conditionals: extract predicates into named helpers; avoid compound boolean soup.
- Break large loops or condition clusters into smaller routines; limit local variables per scope.

## Data Structures
- Choose structures for clarity and operations (lookup, order, uniqueness); wrap raw collections in intention-revealing types when behavior matters.
- Avoid primitive obsession: create value objects with validation/invariants for domain concepts.

## Comments and Documentation
- Comment “why” and constraints, not “what”; keep comments current or delete.
- Eliminate dead/commented-out code; keep docs near the code they describe.

## Testing and Quality Gates
- Unit tests cover normal, boundary, and error cases; isolate external dependencies with fakes.
- Use systematic test checklists: null/empty, limits, ordering, concurrency, resource cleanup, locale/time.
- Measure and prevent defects early: code reading and static checks before tests catch many issues.

## Construction Practices
- Build in increments; integrate frequently to shrink defect-finding latency.
- Refactor continuously: remove duplication, tighten names, simplify logic as you touch code.
- Prefer clarity over micro-optimizations; profile before tuning and after changes.

## Code Tuning (when justified)
- Optimize last, guided by measurements; focus on hotspots, not entire modules.
- Preserve correctness and readability while tuning; re-run tests after each change.
