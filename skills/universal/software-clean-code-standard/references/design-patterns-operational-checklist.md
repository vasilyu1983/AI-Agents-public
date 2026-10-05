# Design Patterns Operational Checklist

Practical triggers and guardrails for applying GoF patterns without over-engineering.

## Creational Patterns
- Factory Method: use when callers need instances without binding to concrete classes; keep factory small and colocated with variants; enforce invariant validation in factory.
- Abstract Factory: use when a family of related products must vary together; return interfaces, not concretes; ensure products stay compatible; avoid if only one family exists.
- Builder: use when constructing complex objects with many optional steps/validations; keep immutable end result; reset builders after use to prevent reuse bugs.
- Prototype: use when cloning configured instances is cheaper than re-constructing; implement deep copies deliberately; document ownership of mutable internals.
- Singleton: avoid by default; if unavoidable (process-wide resource), keep it stateless or immutable, inject where possible, and expose teardown for tests.

## Structural Patterns
- Adapter: use to reconcile mismatched interfaces (third-party, legacy); map types, handle errors, and normalize contracts in one place; do not leak foreign types to domain.
- Facade: use to present a narrow API over a complex subsystem; keep orchestration here, not business logic; log key operations for operability.
- Composite: use for tree-like data with uniform operations; keep parent/child ownership clear; make operations iterative where recursion depth is a risk.
- Decorator: use to add cross-cutting behavior (caching, metrics, validation) without modifying core; ensure transparency—identity and semantics unchanged; avoid stacking conflicting decorators.
- Proxy: use to interpose access (lazy load, remote access, permissions); surface failures explicitly; define timeout/retry/authorization policies in the proxy.
- Bridge: use to vary abstractions and implementations independently (e.g., renderers vs. shapes); keep cross-product explosion controlled; prefer composition over inheritance.

## Behavioral Patterns
- Strategy: use for interchangeable algorithms with same IO shape; inject at construction; keep strategies stateless or clearly stateful; test each strategy independently.
- Template Method: use when algorithm steps are fixed but one slice varies; keep hooks minimal; prefer composition/strategy if subclassing grows.
- Observer: use when multiple listeners react to an event; define payload schema and delivery guarantees; prevent unbounded fan-out and handle failures (dead-letter/metrics).
- Command: use to package actions with undo/redo/logging; ensure idempotence if retried; separate command creation from execution; validate inputs at creation.
- Chain of Responsibility: use when multiple handlers may process a request; stop rules must be explicit; log fall-throughs; avoid hidden global chains.
- State: use when behavior truly depends on a finite, explicit state machine; encapsulate transitions; guard invalid transitions; instrument transitions for debugging.
- Mediator: use to decouple many-to-many interactions; keep mediator lean; avoid turning it into a god object.

## Usage Heuristics
- Start simple: reach for a pattern only after duplication or clear variation appears; document the trigger.
- Prefer composition over inheritance; most patterns have composition-friendly variants—choose those first.
- Keep pattern code small and intent-revealing; rename types after domain concepts, not pattern names.
- Tests: add contract tests per interface (strategies, adapters, commands) and integration tests for orchestrating patterns (facade, mediator, chain).
- Remove patterns when variation disappears; refactor back to simpler structures to avoid accidental complexity.
