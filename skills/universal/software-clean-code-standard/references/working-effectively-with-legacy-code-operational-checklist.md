# Working Effectively with Legacy Code Operational Checklist

Practical moves from Feathers for changing legacy systems safely.

## Assess and Stabilize
- Identify critical flows and high-risk modules; map dependencies and hidden globals.
- Add characterization tests at seams to pin current behavior; tests must fail if behavior changes.
- Keep changes behind toggles/flags when risk is high; plan rollback paths.

## Create Seams
- Introduce adapters/facades to wrap external calls and hard dependencies; inject collaborators instead of constructing internally.
- Break hidden dependencies: pass in environment/config/IO instead of reading globals/singletons.
- Use dependency-breaking techniques: parameterize constructors, extract interfaces, replace constructors with factories.

## Change Patterns
- Sprout Method/Class: add new behavior in a new function/class and route callers incrementally.
- Wrap/Strangle: build a parallel implementation; route traffic via configuration; remove old paths after parity is proven.
- Expand-Contract: widen interfaces to support new behavior, migrate callers, then contract the old shape.

## Safe Refactors
- Work in small, reversible steps; run tests after each step.
- Extract to clarify responsibilities (functions/classes/modules); move behavior to data owners.
- Guard side effects: isolate IO; introduce guard clauses to simplify control flow.

## Testing Strategies
- Prefer tests at seams (public APIs, service boundaries); use fakes/adapters to control collaborators.
- When behavior is unclear, log and assert observed invariants; promote them to tests.
- Keep tests deterministic: control time, randomness, and external resources.

## Risk Controls
- Avoid wide edits; localize changes behind seams or flags.
- Instrument changes: logs/metrics around new paths for observability during rollout.
- Remove dead code promptly after migration; simplify interfaces to match the new shape.
