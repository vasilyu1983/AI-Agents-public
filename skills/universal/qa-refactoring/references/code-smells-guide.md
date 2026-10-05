# Code Smells Guide

Compressed reference of code-smell names, detection cues, and standard fixes,
based on Martin Fowler's catalog and Refactoring.Guru. This file previously
restated the full Fowler/Refactoring.Guru catalog with worked examples per
smell (~1,450 lines) — content the base model already knows. It was trimmed
2026-09-23 to a name-level index; the filename and heading structure are
kept because [software-code-review/references/complexity-only-review-pass.md](../../software-code-review/references/complexity-only-review-pass.md)
cites this file by name for its Dead Code, Speculative Generality, Lazy
Class, and Bloaters/Dispensables categories, which are retained below.

## Contents

- [Bloaters](#bloaters)
- [Object-Orientation Abusers](#object-orientation-abusers)
- [Change Preventers](#change-preventers)
- [Dispensables](#dispensables)
- [Couplers](#couplers)
- [Modern Code Smells](#modern-code-smells)
- [Detection Tools](#detection-tools)

Code smells are surface indications of a deeper design problem — not bugs,
and not always worth fixing. They are context-dependent: judge cost of the
smell against cost of the fix before refactoring, per [SKILL.md's "When NOT
to Refactor"](../SKILL.md#when-not-to-refactor).

## Bloaters

Smells that grow over time until a unit is too large to reason about.

- **Long Method** — a method that keeps absorbing logic. Fix: Extract Method at natural sub-steps.
- **Large Class** — a class doing too much. Fix: Extract Class / Extract Module along a responsibility seam.
- **Primitive Obsession** — using primitives (strings, ints) where a small value type would encode invariants. Fix: Replace Primitive with Object/value type.
- **Long Parameter List** — more than ~3-4 parameters. Fix: Introduce Parameter Object, or replace a parameter with a method call the callee can make itself.
- **Data Clumps** — the same group of fields/parameters traveling together everywhere. Fix: Extract a class or struct for the clump.

## Object-Orientation Abusers

Smells from incomplete or misapplied OO design.

- **Switch Statements** — repeated type-based branching. Fix: Replace Conditional with Polymorphism, or a lookup table, when the branch set is closed and behavior-bearing.
- **Temporary Field** — a field only set/used in some code paths. Fix: Extract Class for the sometimes-used state, or use a local variable/parameter instead.
- **Refused Bequest** — a subclass that overrides most of what it inherits to reject it. Fix: replace inheritance with delegation/composition.
- **Alternative Classes with Different Interfaces** — two classes that do the same job with different method names. Fix: unify the interface.

## Change Preventers

Smells where one conceptual change forces edits across many places.

- **Divergent Change** — one class is edited for many unrelated reasons. Fix: split along the reasons for change (Extract Class).
- **Shotgun Surgery** — one conceptual change requires touching many classes. Fix: Move Method/Field to consolidate the related logic.
- **Parallel Inheritance Hierarchies** — subclassing one hierarchy always forces subclassing another in lockstep. Fix: merge the hierarchies or replace one with composition.

## Dispensables

Smells that are pure overhead — safe to remove once verified unused.

- **Comments** — comments compensating for unclear code, not explaining intent/rationale. Fix: rename/extract until the comment is unnecessary; keep comments that explain *why*, not *what*.
- **Duplicate Code** — the same logic in more than one place. Fix: Extract Function/Method/Class; for cross-cutting duplication, consider a shared utility only after the third occurrence (rule of three).
- **Lazy Class** — a class or module too small to justify its own existence. Fix: inline it into its one caller, or merge with a closely related class.
- **Dead Code** — unreachable or never-called code. Verify with usage search and `git blame` (Chesterton's Fence — see [SKILL.md](../SKILL.md#characterization-test-first-discipline)) before deleting.
- **Speculative Generality** — abstraction (interface, hook, parameter) built for a future need with no current caller. Fix: delete it now; add it when a real second caller appears (YAGNI).

### Dead-Code Removal Tiers

An unused-code report (knip, vulture, `deadcode`, or zero-import grep) is a candidate list, not a deletion list. Tier each finding by how far its callers can hide from static search:

| Tier | Typical items | Evidence needed before deletion |
|------|---------------|---------------------------------|
| Safe | Private helpers, internal functions, test utilities with no references | Zero references in the repo, green suite before and after, one item per commit |
| Caution | Components, route handlers, middleware, plugins, exported symbols | Also: no dynamic import or reflection by name, no string reference in config, routing, or DI registration, not part of a published package API |
| Danger | Entry points, config files, public type definitions, migrations, anything a deployed artifact or another repo loads | Also: owner sign-off, consumer or traffic evidence (logs, usage metrics, dependents list), and a deprecation step before removal |

Delete Safe items in a loop: baseline green, remove one, re-run, revert that one item if anything fails. Never batch Caution or Danger items with Safe ones; a failure then cannot be traced to one deletion.

## Couplers

Smells where objects know too much about each other's internals.

- **Feature Envy** — a method that mostly manipulates another object's data. Fix: Move Method to the object it envies.
- **Inappropriate Intimacy** — two classes reaching into each other's internals. Fix: tighten encapsulation; move shared behavior to one owner.
- **Message Chains** — `a.getB().getC().getD()`. Fix: Hide Delegate, or move the calling logic closer to the data.
- **Middle Man** — a class that only forwards calls to another class. Fix: remove the middle man and call the delegate directly, unless the indirection is deliberate (e.g. a stable seam for testing).

## Modern Code Smells

Smells more specific to async/event-driven and component-based code.

- **Callback Hell** — deeply nested callbacks obscuring control flow. Fix: `async`/`await`, promise chaining, or a state machine for complex flows.
- **Prop Drilling (React/component frameworks)** — passing a prop through many intermediate components that don't use it. Fix: context/provider pattern, or composition (pass the component, not the data, down).
- **God Object** — one object/module that knows or does nearly everything. Fix: same remedies as Large Class/Divergent Change, applied at architecture scale.

## Detection Tools

### Static Analysis Tools

- **SonarQube** — detects code smells, bugs, vulnerabilities (see [../assets/quality-gates/platform-agnostic/sonarqube-setup.md](../assets/quality-gates/platform-agnostic/sonarqube-setup.md) for gate configuration — gates are server-side, not scanner properties).
- **ESLint** — JavaScript/TypeScript code quality (see [../assets/quality-gates/javascript/eslint-config.js](../assets/quality-gates/javascript/eslint-config.js)).
- **Pylint**, **RuboCop**, **ReSharper**, and IDE built-in inspections (IntelliJ, VS/Rider) cover Python, Ruby, and .NET respectively.

### AI-Assisted Detection

- Editor/agent copilots can suggest local cleanups and summarize likely hotspots, but verify their suggestions against this catalog — an agent will sometimes name a smell that doesn't apply or miss the actual root cause.
- Static analysis platforms and IDE inspections remain the more reliable signal for maintainability/security issues at scale; use AI summaries to triage, not to replace the scan.

## References

- Martin Fowler, *Refactoring: Improving the Design of Existing Code*
- https://refactoring.guru/refactoring/smells
- https://luzkan.github.io/smells/
