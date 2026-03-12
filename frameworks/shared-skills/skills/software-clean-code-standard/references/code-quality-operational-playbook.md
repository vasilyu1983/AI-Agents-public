# Code Quality Operational Playbook

Canonical, cross-language rules and procedures for writing, reviewing, refactoring, and maintaining production-grade code. Designed for deterministic execution by downstream skills.

Note: The canonical clean code rule catalog now lives in [clean-code-standard.md](clean-code-standard.md) with `CC-*` rule IDs. This document retains `RULE-01`–`RULE-13` as legacy principle IDs for backwards compatibility during migration.

---

## 1. Canonical Coding Principles

- [RULE-01 Correctness First] Code MUST produce correct results before any optimization, stylistic change, or deadline-driven shortcut. Agents MUST block or downgrade any change that knowingly introduces incorrect behavior.
- [RULE-02 Clarity Over Cleverness] Code MUST be understandable by a competent peer in one focused reading. Agents MUST prefer explicit control flow, descriptive names, and straightforward logic over terse or clever constructs.
- [RULE-03 Single Responsibility] Each function/class/module MUST have one dominant reason to change. When a unit spans multiple business concerns, agents MUST split it into smaller units with clearer responsibilities.
- [RULE-04 High Cohesion, Low Coupling] Related behavior and data MUST be grouped; unrelated concerns MUST be separated. Agents SHOULD design modules that do one thing well and know as little as possible about other modules’ internals.
- [RULE-05 Encapsulate Volatility] Code that depends on unstable details (APIs, IO, frameworks, configuration) MUST be wrapped behind stable interfaces. Callers MUST depend on abstractions rather than concrete, volatile details.
- [RULE-06 Local Reasoning] Behavior SHOULD be understandable by examining a small, contiguous region of code. Agents MUST minimize hidden global state, implicit side effects, and cross-module surprises that break local reasoning.
- [RULE-07 Small, Focused Units] Functions and methods MUST be small enough to describe in one short sentence. If a function contains multiple phases or decision clusters, agents MUST extract helpers until each unit is clearly focused.
- [RULE-08 Explicit Contracts] Public interfaces MUST define their preconditions, postconditions, side effects, error modes, and performance expectations. Agents SHOULD enforce contracts with types, validation, and assertions where practical.
- [RULE-09 Fail Safely] Code MUST handle invalid inputs, partial failures, and external errors predictably. Agents MUST choose safe defaults, never silently ignore critical errors, and surface actionable diagnostics.
- [RULE-10 Testability] Code MUST be structured so critical behavior can be verified automatically. Agents SHOULD factor out pure logic, inject dependencies, and avoid hard-coded external resources whenever possible.
- [RULE-11 Simple First, General Later] Agents MUST implement the simplest design that satisfies current requirements and observed variation. Abstractions SHOULD only be introduced when repeated duplication or real variation justifies them.
- [RULE-12 Continuous Improvement] Whenever touching a file, agents SHOULD leave code slightly better (naming, structure, tests) without uncontrolled scope creep. Safe, incremental refactors are preferred over large rewrites.
- [RULE-13 Operational Observability] Critical paths MUST be observable in production via logs, metrics, or traces. Agents MUST ensure that important decisions, failures, and slow operations are visible and debuggable.

---

## 2. The Operational Coding Playbook

### 2.1 Writing New Code

1. DEFINE intent:
   - MUST document goal, inputs, outputs, constraints, and failure modes in plain language or comments.
   - IF requirements are ambiguous, THEN block implementation and request clarification.
2. CHOOSE boundaries:
   - Identify affected modules and required new interfaces.
   - MUST isolate external dependencies (DB, APIs, file systems) behind interfaces or adapters.
3. SKETCH design:
   - Outline data flow and major steps without code.
   - Split responsibilities into units that satisfy RULE-03, RULE-04, and RULE-07.
4. IMPLEMENT outside-in:
   - Start from public API or entrypoints; define signatures and expected behaviors.
   - Write tests that describe desired behavior for the new API.
   - Implement internal helpers to satisfy tests.
5. EMBED safety:
   - Add validation for inputs and configuration.
   - Implement explicit error handling and logging for critical decisions and external calls.
6. VERIFY behavior:
   - Add tests for normal cases, edge cases, and failure scenarios.
   - Run all relevant tests and static checks; MUST fix failures before merge.

### 2.2 Refactoring Existing Code

1. STABILIZE behavior:
   - Confirm existing automated tests cover the area.
   - IF coverage is weak, THEN add characterization tests that capture current behavior (including quirks).
2. IDENTIFY pain points:
   - Look for duplication, long functions, unclear names, deep nesting, scattered responsibilities, and unstable dependencies.
3. PLAN safe steps:
   - Sequence small, behavior-preserving transformations (extract function, rename, move, introduce parameter object).
   - Ensure each step can be reverted independently.
4. EXECUTE incrementally:
   - Apply one logical transformation at a time.
   - Run tests after each chunk; revert if behavior changes unexpectedly.
5. CLEAN up:
   - Remove dead code and obsolete comments.
   - Re-run the area against RULE-01–RULE-13.

### 2.3 Reviewing Code

1. READ context:
   - MUST read change description, linked issue/ticket, and any design notes.
   - Determine risk level (data loss, security, money movement, availability).
2. SCAN design:
   - Verify that overall approach fits existing architecture and boundaries.
   - Check that scope is minimal and focused on the stated goal.
3. PASS 1 – Correctness:
   - Trace main flows and edge cases.
   - Confirm invariants, data validation, and transaction boundaries.
4. PASS 2 – Design:
   - Evaluate responsibilities, dependencies, and abstractions against RULE-03–RULE-05.
   - Flag any unnecessary coupling or cross-cutting concerns.
5. PASS 3 – Readability:
   - Assess names, control flow, comments, and documentation updates.
   - Request renames or extra structure where understanding is slow.
6. PASS 4 – Tests and Safety:
   - Verify presence and quality of tests for new behavior and bug fixes.
   - Check for security, performance, and operational risks.
7. DECIDE:
   - APPROVE when all MUST issues are resolved and tests pass.
   - REQUEST CHANGES with prioritized, actionable items when standards are not met.
   - ESCALATE or BLOCK when critical safety or architectural violations remain.

### 2.4 Designing and Documenting Systems

1. DEFINE responsibilities:
   - List core capabilities and domain concepts.
   - Group them into cohesive modules or services with single responsibilities.
2. SPECIFY contracts:
   - For each module, define public operations, inputs, outputs, error semantics, and performance expectations.
3. MAP dependencies:
   - Identify all external systems and internal dependencies.
   - Enforce directionality: high-level policy MUST NOT directly depend on low-level implementation details.
4. SELECT minimal patterns:
   - Choose the simplest patterns that satisfy requirements (for example, Strategy or Adapter).
   - AVOID patterns that add indirection without clear benefit.
5. DOCUMENT:
   - Capture data flow, sequence diagrams, and failure handling in short, focused documents near the code.
   - Update documentation whenever contracts or behavior change.

### 2.5 Reducing Complexity

1. LOCATE complex regions:
   - Identify functions with deep nesting, long length, or multiple logical phases.
   - Flag modules with many responsibilities or mixed concerns.
2. FLATTEN control flow:
   - Introduce guard clauses and early returns to reduce nesting.
   - Extract branching logic into well-named helper functions.
3. SPLIT responsibilities:
   - Separate orchestration from computation.
   - Separate IO from business logic.
   - Separate validation from core behavior.
4. CLARIFY data structures:
   - Replace ad-hoc dictionaries/arrays of primitives with descriptive types or objects.
   - Remove unused fields, flags, or legacy parameters.
5. RECHECK:
   - Ensure simplified code is easier to explain and test.
   - Confirm tests still pass and behavior is unchanged.

### 2.6 Handling Legacy Systems

1. ASSESS risk:
   - Identify critical flows, high-defect areas, and modules that change frequently.
   - Determine operational constraints (uptime, rollback flexibility).
2. CREATE seams:
   - Introduce wrapper functions, facades, or adapters to create testable entrypoints.
   - AVOID deep modifications without seams and tests.
3. CHARACTERIZE behavior:
   - Write tests around current behavior at seams, including edge cases and known bugs (label clearly).
4. CHANGE incrementally:
   - Prefer small, reversible refactors.
   - Use feature flags or configuration switches to control rollout.
5. CAPTURE knowledge:
   - Document domain rules, invariants, and surprising behavior discovered during work.
   - Convert important observations into tests.

---

## 3. Code Review Execution Protocol

1. PRE-REVIEW CHECKS:
   - Confirm CI and baseline tests have run.
   - Reject or pause review if the branch is red due to relevant failures.
2. SCOPE VALIDATION:
   - Compare change summary with actual diff.
   - MUST flag unrelated changes (formatting, renames, dead code removal) that are not clearly labeled and scoped.
3. ARCHITECTURE ALIGNMENT:
   - Validate that new code respects existing boundaries and dependency directions.
   - Ensure high-level modules do not depend on low-level details directly.
4. CORRECTNESS REVIEW:
   - For each new or modified entrypoint, walk through:
     - happy path
     - error paths
     - edge cases (null, empty, limits, unusual inputs)
   - Confirm invariants and state transitions are explicit and safe.
5. SAFETY & RISK REVIEW:
   - Inspect user input handling, authentication, authorization, data privacy, and resource management.
   - For calls that delete, update, or move data, require extra validation and logging.
6. TEST REVIEW:
   - Verify new tests exist for new behavior and bug fixes.
   - Ensure tests would fail if the bug reappeared or the feature regressed.
   - Reject changes that significantly alter behavior with no corresponding test updates.
7. READABILITY REVIEW:
   - Confirm names communicate intent, functions are small and focused, and comments explain “why” rather than restating “what”.
   - Ensure documentation and inline examples are updated where relevant.
8. PERFORMANCE & SCALABILITY REVIEW:
   - Spot obvious inefficiencies (N+1 queries, unnecessary loops, unbounded data structures).
   - For performance-sensitive areas, request measurements or guardrails (timeouts, rate limits, batching).
9. DECISION & FEEDBACK:
   - APPROVE when:
     - all MUST issues are resolved
     - tests pass
     - code adheres to RULE-01–RULE-13.
   - REQUEST CHANGES when:
     - correctness, safety, or clarity issues remain
     - tests are missing or weak
     - architecture is misaligned.
   - BLOCK and ESCALATE when:
     - security, compliance, or data-loss risks are present
     - major architectural regressions are introduced.

---

## 4. Refactoring Decision Trees

### 4.1 When to Refactor

- IF the same logic must be modified in multiple places for one change, THEN:
  - Extract the shared logic into a single function/module (RULE-03, RULE-04).
- IF a function is hard to explain in one short sentence, THEN:
  - Split it into smaller functions, each handling one phase of the work (RULE-07).
- IF a module changes frequently for unrelated reasons, THEN:
  - Separate those reasons into different modules/classes with clearer boundaries (Single Responsibility).
- IF adding a feature requires touching many unrelated modules, THEN:
  - Revisit domain boundaries and introduce abstractions that localize change.

### 4.2 Refactor vs Rewrite

- IF behavior is poorly understood AND tests are weak AND the system is critical, THEN:
  - Prefer incremental refactoring with characterization tests.
- IF the code is small, isolated, and well specified, THEN:
  - A clean rewrite MAY be acceptable provided tests are written first and behavior is preserved.
- IF deadlines are tight AND refactor risk is high, THEN:
  - Minimize scope:
    - Only refactor code necessary for the requested change.
    - Defer broad cleanups to dedicated refactor work.

### 4.3 Refactor Scope

- IF structure can be improved without changing observable behavior, THEN:
  - Treat as pure refactor; keep commits behavior-preserving.
- IF refactor and feature change are mixed, THEN:
  - Split into clearly labeled commits:
    - Commit A: refactor only, with tests proving no behavior change.
    - Commit B: feature change relying on the refactor.

### 4.4 Choosing Refactor Operations

- IF duplication is present, THEN:
  - Use Extract Function / Extract Module.
- IF names are misleading or vague, THEN:
  - Use Rename to clarify intentions (functions, variables, classes, and files).
- IF a function has many parameters or configuration flags, THEN:
  - Introduce a Parameter Object or configuration type.
- IF a class has unrelated methods or data, THEN:
  - Extract Class to group related behavior and state.

---

## 5. Legacy Code Survival Kit

### 5.1 Stabilize First

- MUST identify:
  - critical business flows
  - high-defect modules
  - areas with frequent changes.
- Add characterization tests at boundaries before modifying behavior.

### 5.2 Work at Seams

- Introduce seams (wrappers, facades, adapters) where none exist.
- Route new features and refactors through these seams.
- AVOID deep edits scattered across legacy internals without seams and tests.

### 5.3 Incremental Change

- Prefer many small, reversible changes over large rewrites.
- Use feature flags, configuration toggles, or routing switches to control rollout.
- Design each step so it can be reverted without complex data migrations.

### 5.4 Knowledge Capture

- Convert tribal knowledge into:
  - tests that encode invariants and edge cases
  - comments explaining surprising behaviors and domain rules.
- Keep documentation adjacent to the code being described.

### 5.5 Dependency De-risking

- Isolate external dependencies (database, file system, APIs, queues) behind interfaces.
- Implement:
  - timeouts
  - retries with backoff for transient errors
  - clear failure modes and fallbacks for non-critical operations.

### 5.6 Retirement and Cleanup

- Track usage of legacy endpoints and code paths using logs or metrics.
- Remove dead code once usage is confirmed zero and tests validate removal.
- Simplify interfaces after removal to avoid carrying historical baggage.

---

## 6. Design Patterns & Application Rules

### 6.1 General Rules

- Patterns MUST reduce duplication, clarify responsibilities, or improve safety; they MUST NOT be added solely for perceived sophistication.
- Composition SHOULD be preferred over inheritance unless a stable “is-a” relationship and shared contract clearly exist.

### 6.2 Strategy

- Use WHEN:
  - multiple algorithms share the same input/output shape
  - the algorithm must be chosen at runtime.
- Requirements:
  - define a simple, stable interface
  - implement each algorithm as a separate strategy
  - test each strategy independently.
- AVOID WHEN:
  - only one algorithm exists
  - variation is speculative and unsupported by real requirements.

### 6.3 Adapter and Facade

- Adapter:
  - Use WHEN integrating external APIs or legacy code with awkward interfaces.
  - Wrap the external interface in a local shape that fits your domain.
- Facade:
  - Use WHEN exposing a simpler API over a complex subsystem.
  - Provide a limited, stable set of operations that hide internal details.
- Rules:
  - Application code MUST depend only on adapters/facades, not on raw external clients.
  - Adapters MUST handle translation, validation, and error mapping.

### 6.4 Repository / Data Access Layer

- Use WHEN:
  - domain logic should be isolated from persistence details.
- Rules:
  - Domain services MUST depend on repository interfaces, not concrete ORM/driver classes.
  - Repositories MUST encapsulate queries, transactions, and mapping between domain and storage models.
  - Tests for domain logic SHOULD use in-memory or fake repository implementations.

### 6.5 Observer / Eventing

- Use WHEN:
  - many components need to react to a specific event without tight coupling to the origin.
- Rules:
  - Define clear event contracts (names, payloads, delivery guarantees).
  - Guard against unbounded fan-out and cascading failures (timeouts, dead-letter queues).
  - Log event publishing and processing for debugging.

### 6.6 Command / Query Separation

- Use WHEN:
  - reads and writes have different constraints or scaling profiles.
- Rules:
  - Separate operations that change state (commands) from those that only read (queries).
  - Commands MUST have clear side effects and error handling.
  - Queries MUST avoid unnecessary coupling to write models.

---

## 7. Anti-Patterns & Correction Routines

### 7.1 God Object / God Service

- Signals:
  - huge class or module with many unrelated methods and fields
  - frequent changes for different reasons
  - many dependencies injected into one place.
- Correction Routine:
  - Identify distinct domains or workflows.
  - Extract separate modules/services for each domain.
  - Move fields and methods into the new units and update callers.

### 7.2 Long Method

- Signals:
  - deep nesting, many branches
  - comments that divide the method into sections
  - difficult to summarize in one sentence.
- Correction Routine:
  - Extract helper functions for each logical phase.
  - Introduce early returns and guard clauses.
  - Rename functions to describe their intent clearly.

### 7.3 Primitive Obsession

- Signals:
  - many raw strings/ints/booleans representing domain concepts
  - repeated tuples or parameter groups.
- Correction Routine:
  - Create value objects or types that represent domain concepts.
  - Move validation and invariants into these types.
  - Replace primitive clusters with the new types in interfaces.

### 7.4 Shotgun Surgery

- Signals:
  - small change requires editing many scattered files
  - repeated similar edits across modules.
- Correction Routine:
  - Introduce abstractions that centralize related behavior.
  - Route callers through the new abstraction.
  - Gradually remove duplicated logic.

### 7.5 Feature Envy

- Signals:
  - a method uses more data from another object than from its own
  - large groups of getters followed by external computation.
- Correction Routine:
  - Move behavior to the object that owns the data.
  - Expose operations rather than raw data where appropriate.

### 7.6 Global Mutable State

- Signals:
  - global variables or singletons mutated from many places
  - tests that are order-dependent or flaky.
- Correction Routine:
  - Encapsulate state in objects with clear ownership.
  - Inject dependencies rather than reading globals directly.
  - Minimize mutation and provide explicit state transition methods.

### 7.7 Commented-Out Code and Redundant Comments

- Signals:
  - large blocks of disabled code
  - comments that restate obvious behavior.
- Correction Routine:
  - Delete dead code; rely on version control for history.
  - Keep comments that explain intent, constraints, or trade-offs only.

---

## 8. Agent-Executable Checklists

### 8.1 Before Committing New Code

- [ ] All new behavior is covered by tests (normal, edge, and failure cases).
- [ ] Functions and modules have single responsibilities and descriptive names.
- [ ] Shared logic is extracted; no obvious duplication was introduced.
- [ ] Inputs, configuration, and external calls are validated and handled safely.
- [ ] Public interfaces and significant changes are documented.

### 8.2 Before Approving a Review

- [ ] Change scope matches description; unrelated changes are called out or removed.
- [ ] Design respects existing architecture and RULE-01–RULE-13.
- [ ] Tests exist for new behavior and regressions; all relevant tests pass.
- [ ] Code is readable, consistent with surrounding style, and free from obvious smells.
- [ ] Security, performance, and operational impacts are considered and acceptable.

### 8.3 After Refactoring

- [ ] All tests that passed before still pass.
- [ ] Public APIs and observable behavior are unchanged unless explicitly intended.
- [ ] Complexity is reduced (shorter functions, clearer responsibilities, fewer dependencies).
- [ ] Names and comments are updated to reflect current behavior.
- [ ] Dead or unused code was removed in modified areas.

### 8.4 Working with Legacy Code

- [ ] Characterization tests cover modified behavior where feasible.
- [ ] Changes are localized behind seams or adapters.
- [ ] Domain rules and surprising behavior are documented.
- [ ] Rollback or disable strategy exists (feature flag, config, or revert plan).

---

## 9. Cross-Book Concordance Table

High-level mapping of rules to major sources. This mapping is approximate and intended for traceability only; all content here is rewritten and operationalized.

| Rule ID / Cluster | Primary Themes | Representative Sources |
|-------------------|----------------|------------------------|
| RULE-01, RULE-10  | Correctness, testing, verification | Code Complete; The Pragmatic Programmer; The Practice of Programming; The Clean Coder |
| RULE-02, RULE-07  | Clarity, small functions, readability | Clean Code; Refactoring; The Art of Clean Code |
| RULE-03, RULE-04  | Responsibilities, coupling, cohesion | Clean Code; Design Patterns; Code Complete |
| RULE-05, KIT-05   | Encapsulation of volatility, dependency management | Design Patterns; Working Effectively with Legacy Code; Refactoring |
| RULE-06, RULE-12  | Local reasoning, incremental improvement | The Pragmatic Programmer; Code Complete; Working Effectively with Legacy Code |
| RULE-09, RULE-13  | Error handling, observability | The Pragmatic Programmer; The Practice of Programming; modern clean-code practice literature |
| PLAYBOOK-02, TREE-4.x | Safe refactoring, small steps | Refactoring; Working Effectively with Legacy Code |
| PROTOCOL-CR, Section 3 | Structured code reviews | Best Kept Secrets of Peer Code Review; Implementing Effective Code Reviews; Looks Good To Me |
| KIT-01–KIT-06     | Legacy system strategies | Working Effectively with Legacy Code; Refactoring; The Pragmatic Programmer |

---

## 10. Operational Heuristics Library

Ready-to-run checklists distilled from Clean Code, The Art of Clean Code, Code Complete, Refactoring, Working Effectively with Legacy Code, Design Patterns, The Pragmatic Programmer, The Practice of Programming, The Clean Coder, Best Kept Secrets of Peer Code Review, Implementing Effective Code Reviews, and Looks Good To Me.

### 10.1 Pull Request Hygiene (review sources)

- Keep PRs small and single-purpose; avoid mixed refactor + feature unless separated and labeled.
- Include intent, scope, non-goals, risk level, rollout/rollback, and a test plan in the description.
- Provide reviewer aids: reproduction steps, screenshots/logs, data shape examples, migration notes.
- Remove noise (drive-by formatting, commented code); squash or group commits by logical steps.

### 10.2 High-Signal Defect Scan (Code Complete, Pragmatic, Practice of Programming)

- Inputs/outputs: validate null/empty, length/limits, encoding/time zones, units, index bounds.
- State and concurrency: ensure invariants, immutability or locking, no shared mutable defaults.
- Resources and IO: timeouts, retries with backoff, idempotency, close/cleanup paths, transactional boundaries.
- Data correctness: check sortedness/uniqueness assumptions, off-by-one loops, integer overflow, precision/rounding.
- Error flow: never swallow exceptions; surface actionable context; ensure logs/metrics exist for critical failures.

### 10.3 Function and API Shape (Clean Code, Art of Clean Code, Clean Coder)

- Names state effect or value; commands are verbs, queries are nouns; avoid mixed command/query functions.
- Parameter discipline: prefer ≤3 params, avoid boolean flags, group related params into objects with validation.
- Keep one abstraction level per function; use guard clauses to flatten nesting; isolate side effects at edges.
- Avoid hidden outputs or implicit mutation; prefer explicit return values and well-defined pre/postconditions.

### 10.4 Refactor Recipes (Refactoring)

- Safe operations to prioritize: Extract Function/Class/Module, Introduce Parameter Object, Move Method/Field, Inline Temp, Replace Conditional with Polymorphism when variants are stable.
- Sequence: add/verify tests → refactor in tiny steps → run tests after each cluster → revert on unexpected behavior change.
- Break dependencies with interfaces or constructor injection before moving logic; delete dead code after behavior is proven stable.

### 10.5 Legacy Change Patterns (Working Effectively with Legacy Code)

- Find seams and wrap them (facade/adapter); add characterization tests at seams before edits.
- Sprout Method/Class for new behavior; route callers gradually; avoid editing deep internals until coverage exists.
- Strangle pattern: build a new implementation alongside old, switch traffic via config/flags, retire old path once parity is verified.
- Document discovered invariants and keep a rollback switch for each risky change.

### 10.6 Design Decision Triggers (Design Patterns, Pragmatic)

- Adapter/Facade when external or legacy interfaces do not match domain shapes; Strategy when runtime algorithm choice is needed; Template/Hook only when steps are fixed but one slice varies.
- Repository/Data access layer to isolate persistence; CQRS when read/write constraints diverge.
- Prefer composition over inheritance; decline patterns when only one variant exists or indirection adds no safety.

### 10.7 Testing and Deployment Safety (Clean Coder, Pragmatic, Practice of Programming)

- Write tests for new behavior and for fixed bugs that fail before the fix; cover happy path, edge, and failure cases.
- Keep tests deterministic and fast: isolate time, randomness, and IO behind fakes; use Arrange-Act-Assert structure.
- Pre-merge: all relevant tests green, feature flags/config toggles in place, monitoring/logging ready for new paths.
- Post-merge: stage/roll out gradually when risk is high; capture metrics to confirm expected behavior and detect regressions.

### 10.8 Peer Review Controls (Best Kept Secrets of Peer Code Review)

- Size limits: keep reviews ≤200–250 LOC; if a change exceeds that, split it. Reject or rescope anything >2000 LOC or that cannot be reviewed in a focused sitting.
- Pace: aim for ≤400 LOC/hour; slower is better for defect discovery. If throughput rises above that, pause and reschedule in smaller batches.
- Timebox: stop or break at ~60 minutes; reviewers fatigue after that and miss defects. Avoid marathon sessions.
- Author preparation: require authors to annotate diffs (what to read first, risky areas, rationale) and run self-checks before sending; this materially lowers defect counts in the review.
- Tooling guardrails: flag "pass-through" reviews (durations <30 seconds or rates >1500 LOC/hour) as invalid; enforce size/time warnings and require explicit acknowledgement to proceed.
- Metrics: track defect density per review size; expect defect yield to drop sharply above ~200 LOC—use this signal to enforce smaller PRs and slower pace, not to game counts.

---

## 11. LLM-Generated Code Review Protocol

### 11.1 Why LLM Code Needs Special Review

LLM-generated code introduces distinct failure modes not covered by traditional code review:

- **Hallucinated APIs**: Non-existent methods, incorrect signatures, deprecated functions
- **Outdated patterns**: Training data lag (6-18 months behind current best practices)
- **Plausible-looking bugs**: Code that appears correct but has subtle logic errors
- **Context blindness**: Ignores existing codebase patterns, introduces inconsistencies
- **Security assumptions**: May generate vulnerable code that "looks right"

### 11.2 Pre-Commit Checklist for LLM Code

Before committing ANY LLM-generated code:

- [ ] **API verification**: Confirm all imported modules, functions, and methods exist
- [ ] **Version check**: Verify library versions match project dependencies
- [ ] **Signature validation**: Check function signatures against official documentation
- [ ] **Type correctness**: Run type checker (tsc, mypy, pyright) with strict mode
- [ ] **Test execution**: Run existing tests; add tests for new functionality
- [ ] **Security scan**: Run static analysis (semgrep, bandit, eslint-plugin-security)
- [ ] **Pattern alignment**: Compare with existing codebase conventions

### 11.3 Hallucination Detection Checklist

| Signal | Check | Action |
|--------|-------|--------|
| Import fails | Module not found | Search npm/PyPI for correct package name |
| Method undefined | `.nonExistentMethod()` | Check library docs for actual API |
| Wrong signature | Type errors on call | Verify parameter order and types |
| Deprecated warning | Using old API | Find current replacement |
| Unfamiliar syntax | Language feature unknown | Verify feature exists in target version |
| Magic constants | Unexplained numbers/strings | Request source or verify correctness |

### 11.4 Version and Deprecation Verification

```bash
# TypeScript/JavaScript - Check if package/version exists
npm info package-name versions

# Python - Check if package exists and version
pip index versions package-name

# Verify imports resolve
# TypeScript
npx tsc --noEmit src/file.ts

# Python
python -c "from module import function"
```

**Common hallucination patterns**:

```typescript
// BAD: Hallucinated - No such import in Express 5
import { validateBody } from 'express';

// GOOD: Correct - Use express-validator or manual
import { body, validationResult } from 'express-validator';
```

```python
# BAD: Hallucinated - pandas method doesn't exist
df.autoClean()

# GOOD: Correct - Use actual pandas API
df.dropna().drop_duplicates()
```

### 11.5 Codebase Consistency Checks

LLM code must match existing patterns:

| Area | Check | If Mismatch |
|------|-------|-------------|
| Error handling | Compare with existing error classes | Refactor to use project's error patterns |
| Logging | Match existing logger usage | Use project's logger instance |
| Naming | Check conventions (camelCase vs snake_case) | Rename to match |
| File structure | Compare with similar features | Reorganize to match patterns |
| Dependencies | Check if already in project | Use existing package, not new one |
| Testing style | Match existing test patterns | Rewrite tests to match conventions |

### 11.6 Security Review for LLM Code

LLM models may generate code with security vulnerabilities:

**High-Risk Patterns to Flag**:

```typescript
// BAD: SQL Injection - LLMs often generate string interpolation
const query = `SELECT * FROM users WHERE id = ${userId}`;

// GOOD: Parameterized query
const query = 'SELECT * FROM users WHERE id = $1';
await db.query(query, [userId]);
```

```typescript
// BAD: Command injection - Common LLM mistake
exec(`ls ${userInput}`);

// GOOD: Use array form
execFile('ls', [userInput]);
```

```typescript
// BAD: XSS - innerHTML with user data
element.innerHTML = userContent;

// GOOD: Use textContent or sanitize
element.textContent = userContent;
```

**Security Checklist for LLM Code**:

- [ ] No string concatenation in SQL/commands
- [ ] No `eval()`, `exec()`, or dynamic code execution with user input
- [ ] No hardcoded credentials or API keys
- [ ] Input validation on all external data
- [ ] Output encoding for HTML/JSON contexts
- [ ] Proper authentication/authorization checks
- [ ] No sensitive data in logs or error messages

### 11.7 Test Coverage for LLM Code

LLM-generated code requires higher test scrutiny:

**Minimum Test Requirements**:

```typescript
// For ANY new function, require:
describe('llmGeneratedFunction', () => {
  // 1. Happy path
  it('handles valid input correctly', () => {});

  // 2. Edge cases - LLMs often miss these
  it('handles empty input', () => {});
  it('handles null/undefined', () => {});
  it('handles boundary values', () => {});

  // 3. Error cases - LLMs often generate optimistic code
  it('throws on invalid input', () => {});
  it('handles API failures gracefully', () => {});

  // 4. Integration sanity
  it('integrates with existing system', () => {});
});
```

**Test Verification**:

- [ ] Tests actually run (not just syntactically correct)
- [ ] Tests fail when implementation is broken
- [ ] Tests cover documented behavior
- [ ] Tests match project's testing patterns

### 11.8 Review Protocol: Step-by-Step

**Phase 1: Automated Checks (Before Human Review)**

```bash
# 1. Type check
npm run typecheck  # or: tsc --noEmit

# 2. Lint
npm run lint

# 3. Security scan
npx semgrep --config auto src/

# 4. Test
npm test

# 5. Build
npm run build
```

**Phase 2: Human Review Focus Areas**

1. **Import verification** (5 min): Check every import against package.json and official docs
2. **Logic trace** (10 min): Walk through main code paths mentally
3. **Edge case analysis** (5 min): What happens with null, empty, max values?
4. **Pattern comparison** (5 min): Compare with similar existing code
5. **Security scan** (5 min): Look for injection, auth, data exposure risks

**Phase 3: Documentation and Context**

- [ ] Comments explain non-obvious logic
- [ ] Any "magic" values are documented
- [ ] Error messages are actionable
- [ ] README/docs updated if behavior changes

### 11.9 Agent-Executable LLM Code Review Checklist

```markdown
## LLM Code Review Checklist

### Verification (Blocking)
- [ ] All imports resolve without error
- [ ] All external APIs verified against documentation
- [ ] Type checker passes with zero errors
- [ ] No deprecated APIs used
- [ ] Security scan passes

### Quality (Required)
- [ ] Code matches existing codebase patterns
- [ ] Tests exist and pass
- [ ] No hardcoded values without explanation
- [ ] Error handling is explicit and safe
- [ ] Logging follows project conventions

### Documentation (Expected)
- [ ] Complex logic has comments
- [ ] Public APIs are documented
- [ ] Breaking changes noted in commit message

### Decision
- APPROVE: All blocking checks pass, quality checks pass
- REQUEST CHANGES: Any blocking or quality issues remain
- REJECT: Security vulnerabilities or hallucinated APIs detected
```

### 11.10 Common LLM Mistakes by Language

**TypeScript/JavaScript**:
- Mixing CommonJS (`require`) and ESM (`import`) incorrectly
- Using `any` type excessively
- Generating React class components (outdated)
- Wrong async/await patterns
- Deprecated Express middleware

**Python**:
- Python 2 syntax (`print "hello"`)
- Deprecated `typing` imports (use built-in generics in 3.9+)
- `requests` without timeout
- Missing `__init__.py` for packages
- Blocking calls in async functions

**Go**:
- Not handling errors (assigning to `_`)
- Deprecated `ioutil` package
- Missing context propagation
- Incorrect mutex usage
- Race conditions in goroutines

### 11.11 Prompt Engineering for Better LLM Code

When requesting code from LLMs:

**Include in Prompt**:
- Target language version (e.g., "Python 3.14", "TypeScript 5.7")
- Framework versions (e.g., "Next.js 16", "Express 5")
- Existing patterns ("Match our existing error handling in src/utils/errors.ts")
- Security requirements ("Use parameterized queries only")
- Test requirements ("Include unit tests with edge cases")

**Request Verification**:
- "List all external packages this code requires"
- "Confirm all imported APIs exist in [package version]"
- "Identify potential security concerns"
- "What edge cases should be tested?"

### 11.12 Metrics for LLM Code Quality

Track these metrics to improve LLM code quality over time:

| Metric | Target | Action if Exceeded |
|--------|--------|-------------------|
| Hallucination rate | <5% of PRs | Improve prompts, add verification |
| Type errors per PR | 0 | Run type check in CI before review |
| Security issues per PR | 0 | Add security scanning to pipeline |
| Test failure rate | <10% | Require tests pass before merge |
| Pattern violations | <3 per PR | Document patterns, improve prompts |

**Tracking Command**:

```bash
# Log LLM code issues for analysis
echo "$(date -Iseconds),hallucination,import,express" >> llm-code-issues.csv
```

---

## 12. Complexity Management (Dec 2025)

Systematic approaches to measuring, monitoring, and reducing codebase complexity.

### 12.1 Complexity Metrics

| Metric | Threshold | Tool | Action |
|--------|-----------|------|--------|
| Cyclomatic Complexity | >10 per function | eslint-plugin-complexity, radon | Refactor or split function |
| Cognitive Complexity | >15 per function | SonarQube, codeclimate | Simplify control flow |
| Lines per Function | >50 lines | eslint, pylint | Extract helper functions |
| Parameters per Function | >4 parameters | eslint, mypy | Introduce parameter object |
| Nesting Depth | >3 levels | eslint, pylint | Use guard clauses, early returns |
| File Length | >400 lines | custom script | Split into modules |
| Dependencies per Module | >7 imports | madge, import-graph | Review module boundaries |

### 12.2 Complexity Tracking Workflow

1. **BASELINE**:
   - Run complexity analysis on entire codebase
   - Record metrics per module/file
   - Identify top 10 most complex areas

2. **GATE**:
   - Add complexity checks to CI pipeline
   - Block PRs that exceed thresholds
   - Allow exception with documented justification

3. **TREND**:
   - Track complexity over time
   - Alert on trend increases
   - Schedule complexity reduction sprints

### 12.3 Complexity Reduction Techniques

**Guard Clauses Pattern**:

```typescript
// Before: Nested complexity
function processOrder(order: Order): Result {
  if (order) {
    if (order.items.length > 0) {
      if (order.status === 'pending') {
        // Process logic here
        return { success: true };
      }
    }
  }
  return { success: false };
}

// After: Guard clauses
function processOrder(order: Order): Result {
  if (!order) return { success: false };
  if (order.items.length === 0) return { success: false };
  if (order.status !== 'pending') return { success: false };

  // Process logic here
  return { success: true };
}
```

**Extract Method Pattern**:

```typescript
// Before: Long method with phases
function processCheckout(cart: Cart): Invoice {
  // Phase 1: Validate (20 lines)
  // Phase 2: Calculate totals (15 lines)
  // Phase 3: Apply discounts (25 lines)
  // Phase 4: Generate invoice (20 lines)
}

// After: Extracted methods
function processCheckout(cart: Cart): Invoice {
  const validated = validateCart(cart);
  const totals = calculateTotals(validated);
  const discounted = applyDiscounts(totals);
  return generateInvoice(discounted);
}
```

**Strategy Pattern for Conditionals**:

```typescript
// Before: Complex switch
function calculateShipping(type: string, weight: number): number {
  switch (type) {
    case 'standard': return weight * 1.5;
    case 'express': return weight * 3.0 + 10;
    case 'overnight': return weight * 5.0 + 25;
    // More cases...
  }
}

// After: Strategy pattern
const shippingStrategies: Record<string, ShippingStrategy> = {
  standard: new StandardShipping(),
  express: new ExpressShipping(),
  overnight: new OvernightShipping(),
};

function calculateShipping(type: string, weight: number): number {
  return shippingStrategies[type].calculate(weight);
}
```

### 12.4 CI Integration

```yaml
# GitHub Actions complexity gate
complexity-check:
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v4
    - name: Check complexity
      run: |
        npx eslint --rule 'complexity: ["error", 10]' src/
        # Or for Python
        # radon cc src/ --min C --show-complexity
```

### 12.5 Agent-Executable Complexity Checklist

- [ ] No function exceeds cyclomatic complexity of 10
- [ ] No function exceeds cognitive complexity of 15
- [ ] No function has more than 4 parameters
- [ ] No nesting deeper than 3 levels
- [ ] Complex conditionals extracted to well-named functions
- [ ] Guard clauses used for early validation
- [ ] Complex calculations isolated in pure functions

---

## 13. Technical Debt Register (Dec 2025)

Systematic tracking and management of technical debt to prevent accumulation and ensure prioritized resolution.

### 13.1 Debt Classification

| Category | Impact | Examples | SLA |
|----------|--------|----------|-----|
| **Critical** | Blocks features, causes incidents | Security vulnerabilities, data corruption risks | Fix within 1 sprint |
| **High** | Slows development significantly | Missing tests for critical paths, tight coupling | Fix within 3 sprints |
| **Medium** | Causes friction | Outdated dependencies, code duplication | Fix within quarter |
| **Low** | Minor inconvenience | Style inconsistencies, missing docs | Opportunistic |

### 13.2 Debt Entry Template

```markdown
## TD-[NUMBER]: [Brief Title]

**Category**: Critical | High | Medium | Low
**Area**: [Module/Feature affected]
**Introduced**: [Date or PR/Commit]
**Reporter**: [Name]

### Description
[What is the debt and why does it exist?]

### Impact
[How does this affect development, performance, or reliability?]

### Remediation
[Steps to fix, estimated effort, dependencies]

### Cost of Delay
[What happens if not fixed? Compound effects?]

### Related
- Issue: #[number]
- PRs: #[number]
- Related debt: TD-[number]
```

### 13.3 Debt Register Example

| ID | Title | Category | Area | Impact | Effort | Priority |
|----|-------|----------|------|--------|--------|----------|
| TD-001 | Missing auth service tests | High | auth/ | Cannot safely refactor | 3d | P1 |
| TD-002 | Deprecated axios version | Medium | api/ | Security warnings | 1d | P2 |
| TD-003 | Duplicate validation logic | Medium | forms/ | Bug fix requires 3 edits | 2d | P2 |
| TD-004 | Hardcoded config values | Low | config/ | Deploy friction | 0.5d | P3 |

### 13.4 Debt Tracking Workflow

1. **CAPTURE**:
   - Record debt when discovered (PR comments, incidents, planning)
   - Use standardized template
   - Link to related issues/PRs

2. **CLASSIFY**:
   - Assign category based on impact
   - Estimate remediation effort
   - Identify dependencies

3. **PRIORITIZE**:
   - Review debt register weekly/bi-weekly
   - Stack rank by impact-to-effort ratio
   - Allocate capacity (recommend 15-20% of sprint)

4. **RESOLVE**:
   - Create explicit tickets for debt work
   - Include debt fixes in PRs when adjacent
   - Update register when resolved

5. **REPORT**:
   - Track debt trends over time
   - Report debt velocity (added vs resolved)
   - Alert on critical debt age

### 13.5 Debt Prevention Strategies

**Code Review Gate**:

- [ ] New debt documented if introduced
- [ ] Adjacent debt addressed in PR (boy scout rule)
- [ ] No new critical/high debt without exception approval

**Architecture Review**:

- [ ] Quarterly debt audit
- [ ] Identify systemic debt patterns
- [ ] Plan strategic debt reduction initiatives

**Definition of Done**:

- [ ] No known bugs shipped
- [ ] Tests cover new functionality
- [ ] No increase in complexity metrics
- [ ] Debt register updated if applicable

### 13.6 Debt Metrics Dashboard

| Metric | Target | Current | Trend |
|--------|--------|---------|-------|
| Total debt items | <50 | [count] | [trend] |
| Critical debt age | <7 days | [max age] | [trend] |
| High debt age | <30 days | [max age] | [trend] |
| Debt added/sprint | <5 | [count] | [trend] |
| Debt resolved/sprint | >3 | [count] | [trend] |
| Debt ratio | <15% of backlog | [%] | [trend] |

### 13.7 Agent-Executable Debt Management Checklist

- [ ] All known debt recorded in register
- [ ] Critical debt has remediation timeline
- [ ] High debt reviewed in sprint planning
- [ ] Debt older than SLA escalated
- [ ] New PRs include debt impact assessment
- [ ] Quarterly debt audit scheduled
- [ ] Debt velocity trending downward
