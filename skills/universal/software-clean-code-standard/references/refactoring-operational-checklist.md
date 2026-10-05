# Refactoring Operational Checklist

Field-ready guardrails and recipes distilled from Martin Fowler’s Refactoring.

## Preconditions
- Establish tests that pin current behavior (characterization tests if coverage is weak); tests must fail when behavior changes.
- Choose a small scope with clear intent; avoid mixing feature changes with refactors in the same commit unless clearly separated.
- Baseline green tests before starting; keep version control checkpoints small and reversible.

## Safe Move Patterns
- Extract Function / Extract Method: name by intent; move one logical step at a time; inline temp variables that obscure meaning.
- Extract Class / Module: split responsibilities; move fields and methods together to preserve cohesion.
- Introduce Parameter Object: replace long parameter lists or data clumps with a typed object that owns validation.
- Move Method/Field: relocate behavior to the data owner (cures feature envy); update callers in small steps.
- Replace Conditional with Polymorphism/Strategy when variants are stable and tested; otherwise keep conditionals simple and well-named.
- Encapsulate Collection / Encapsulate Variable: hide representation, expose behaviors (add/remove) not raw collections.
- Replace Magic Number with Constant; rename for units and intent.

## Step Discipline
- One transformation at a time; run tests after each cluster of small moves.
- Keep behavior stable until refactor is complete; avoid simultaneous structural and behavioral changes.
- Use guard clauses to flatten deeply nested code; extract predicates into named helpers for clarity.

## Working with Legacy Code
- Create seams (wrappers, adapters) to inject fakes and isolate risky dependencies.
- Sprout Method/Class to add new behavior without altering existing code paths; route callers incrementally.
- Strangle: build new implementation alongside old and switch traffic via config/flags; delete dead paths after verification.

## Smells → Actions (selected)
- Long Function, Deep Nesting → Extract functions, introduce guard clauses, split phases.
- Long Parameter List, Boolean Flags, Data Clumps → Introduce Parameter Object or value objects; remove flags by splitting functions.
- Divergent Change / Shotgun Surgery → Reorganize by responsibility; extract modules; centralize shared logic.
- Feature Envy → Move method/behavior to the data owner; expose behavior not getters.
- Primitive Obsession → Create value objects with invariants; push validation inside them.
- Temporary Field / Incomplete Library Class → Extract class or introduce adapter to keep optional state constrained.
- Comments explaining “what” → Refactor for clarity; keep comments for “why,” constraints, and non-obvious decisions.

## Verification and Closure
- Rerun full tests; ensure public behavior unchanged (unless intentionally changed in a separate feature commit).
- Remove dead code after switching call sites; simplify interfaces to match new structure.
- Update names and documentation to reflect the new design; keep commits labeled as refactor-only for traceability.
