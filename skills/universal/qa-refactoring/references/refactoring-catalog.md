# Refactoring Catalog

This file previously restated Martin Fowler's refactoring catalog in full
(~1,390 lines) with toy examples per refactoring — content the base model
already knows well without a skill's help. It was trimmed 2026-09-23. For
the full catalog, use [refactoring.com/catalog](https://refactoring.com/catalog/)
or the *Refactoring* book itself.

What the base model tends to get wrong, and this skill's actual delta, is
narrower: **some named refactorings can silently change behavior**, even
though the catalog presents them as behavior-preserving. That risk list is
the content worth keeping here.

## Refactorings with hidden behavior-change risk

- **Replace Temp with Query** — inlining a cached local into a repeated
  method call changes *when* and *how often* the computation runs. If the
  query is non-idempotent (reads mutable state, has side effects, or is
  expensive/non-deterministic), this changes observable behavior or
  performance, not just structure. Verify the query is a pure read before
  applying this one automatically.

- **Pull Up Method / Pull Up Field** — moving a method or field to a
  superclass changes its visibility and initialization order relative to
  sibling subclasses. A field that was independently initialized per
  subclass can end up shared or initialized once, changing behavior for
  every subclass that relied on the old per-instance state.

- **Inline Variable** (and Inline Method) with side effects — inlining
  duplicates the expression at every call site. If the expression has a
  side effect (mutation, I/O, logging) or the original was evaluated once
  and reused, inlining changes it from "evaluated once" to "evaluated N
  times" — this is exactly the Replace Temp with Query risk, generalized.

- **Extract Method** across an exception boundary — moving code into a new
  method changes what a `try`/`catch`/`finally` around the call site
  actually wraps. A `finally` or `catch` that used to run inline may now
  run around a call that returns early, changing cleanup or error-recovery
  timing.

- **Replace Conditional with Polymorphism** — collapsing a `switch`/`if`
  chain into virtual dispatch changes evaluation order (a `switch` with
  fallthrough or a specific branch order is not automatically equivalent
  to dispatch-by-type) and can silently drop a default/else branch if no
  subclass claims it. Verify every original branch, including the default,
  has an explicit polymorphic equivalent.

- **Consolidating near-duplicate conditionals** (a common precursor to
  several catalog refactorings) — merging two conditions that look
  identical but differ at a boundary (`>` vs `>=`, inclusive vs exclusive
  ranges) silently changes which inputs take which branch. This is the
  single most common source of the "boundary drift" failure mode described
  in [SKILL.md's LLM-agent section](../SKILL.md#llm-agents-and-subtle-behavior-changes-during-refactors).

- **Move Method/Field across a serialization or wire boundary** — not a
  named Fowler refactoring by itself, but any of the above applied to a
  type that is serialized (JSON, protobuf, DB row) can change the wire
  shape even when the in-memory behavior is preserved. Add a golden-master
  or contract test on the serialized form before refactoring types that
  cross a boundary another system parses.

## How to use this list

Treat every refactoring on this list as **not** unconditionally
behavior-preserving. Before applying one:

1. State the specific precondition that makes it safe here (pure function,
   no fallthrough, no shared mutable state, not serialized externally).
2. Add or confirm a test that would fail if that precondition were false.
3. Apply the refactor, then re-run the test before moving to the next step.

This is the same discipline as [SKILL.md's Behavior-Preservation
Verification Strategies](../SKILL.md#behavior-preservation-verification-strategies) —
this file exists to name the specific catalog entries where "it's just a
refactor" is most likely to be wrong.
