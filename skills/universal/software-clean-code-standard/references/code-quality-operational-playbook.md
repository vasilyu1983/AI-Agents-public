# Code Quality Operational Playbook

Canonical, cross-language rules and procedures for writing, reviewing, refactoring, and maintaining production-grade code. Designed for deterministic execution by downstream skills.

Note: The canonical clean code rule catalog lives in [clean-code-standard.md](clean-code-standard.md) with `CC-*` rule IDs. The legacy `RULE-01`–`RULE-13` IDs are retired; § 1 maps each to its `CC-*` replacement.

---
## Table of Contents

- [1. Canonical Coding Principles (RULE-01–RULE-13 retired)](#1-canonical-coding-principles-rule-01rule-13-retired)
- [2. The Operational Coding Playbook](#2-the-operational-coding-playbook)
- [2.1 Writing New Code](#21-writing-new-code)
- [2.2 Refactoring Existing Code](#22-refactoring-existing-code)
- [2.3 Reviewing Code](#23-reviewing-code)
- [2.4 Designing and Documenting Systems](#24-designing-and-documenting-systems)
- [2.5 Reducing Complexity](#25-reducing-complexity)
- [2.6 Handling Legacy Systems](#26-handling-legacy-systems)
- [3. Code Review Execution Protocol](#3-code-review-execution-protocol)
- [4. Refactoring Decision Trees](#4-refactoring-decision-trees)
- [5. Legacy Code Survival Kit](#5-legacy-code-survival-kit)
- [6. Design Patterns & Application Rules](#6-design-patterns--application-rules)
- [6.1 General Rules](#61-general-rules)
- [6.2 Strategy](#62-strategy)
- [6.3 Adapter and Facade](#63-adapter-and-facade)
- [6.4 Repository / Data Access Layer](#64-repository--data-access-layer)
- [6.5 Observer / Eventing](#65-observer--eventing)
- [6.6 Command / Query Separation](#66-command--query-separation)
- [7. Anti-Patterns & Correction Routines](#7-anti-patterns--correction-routines)
- [8. Agent-Executable Checklists](#8-agent-executable-checklists)
- [8.1 Before Committing New Code](#81-before-committing-new-code)
- [8.2 Before Approving a Review](#82-before-approving-a-review)
- [8.3 After Refactoring](#83-after-refactoring)
- [8.4 Working with Legacy Code](#84-working-with-legacy-code)
- [9. Cross-Book Concordance Table](#9-cross-book-concordance-table)
- [10. Operational Heuristics Library](#10-operational-heuristics-library)
- [10.1 Pull Request Hygiene (review sources)](#101-pull-request-hygiene-review-sources)
- [10.2 High-Signal Defect Scan (Code Complete, Pragmatic, Practice of Programming)](#102-high-signal-defect-scan-code-complete-pragmatic-practice-of-programming)
- [10.3 Function and API Shape (Clean Code, Art of Clean Code, Clean Coder)](#103-function-and-api-shape-clean-code-art-of-clean-code-clean-coder)
- [10.4 Refactor Recipes (Refactoring)](#104-refactor-recipes-refactoring)
- [10.5 Legacy Change Patterns (Working Effectively with Legacy Code)](#105-legacy-change-patterns-working-effectively-with-legacy-code)
- [10.6 Design Decision Triggers (Design Patterns, Pragmatic)](#106-design-decision-triggers-design-patterns-pragmatic)
- [10.7 Testing and Deployment Safety (Clean Coder, Pragmatic, Practice of Programming)](#107-testing-and-deployment-safety-clean-coder-pragmatic-practice-of-programming)
- [10.8 Peer Review Controls (Cisco/SmartBear peer-review research)](#108-peer-review-controls-ciscosmartbear-peer-review-research)
- [11. LLM-Generated Code Review Protocol](#11-llm-generated-code-review-protocol)
- [11.1 Why LLM Code Needs Special Review](#111-why-llm-code-needs-special-review)
- [11.2 Pre-Commit Checklist for LLM Code](#112-pre-commit-checklist-for-llm-code)
- [11.3 Hallucination Detection Checklist](#113-hallucination-detection-checklist)
- [11.4 Version and Deprecation Verification](#114-version-and-deprecation-verification)
- [11.5 Codebase Consistency Checks](#115-codebase-consistency-checks)
- [11.6 Security Review for LLM Code](#116-security-review-for-llm-code)
- [11.7 Test Coverage for LLM Code](#117-test-coverage-for-llm-code)
- [11.8 Review Protocol: Step-by-Step](#118-review-protocol-step-by-step)
- [11.9 Agent-Executable LLM Code Review Checklist](#119-agent-executable-llm-code-review-checklist)
- [11.10 Common LLM Mistakes by Language](#1110-common-llm-mistakes-by-language)
- [11.11 Prompt Engineering for Better LLM Code](#1111-prompt-engineering-for-better-llm-code)
- [11.12 Metrics for LLM Code Quality](#1112-metrics-for-llm-code-quality)
- [12. Complexity Management](#12-complexity-management)
- [12.1 Complexity Metrics](#121-complexity-metrics)
- [12.2 Complexity Tracking Workflow](#122-complexity-tracking-workflow)
- [12.3 Complexity Reduction Techniques](#123-complexity-reduction-techniques)
- [12.4 CI Integration](#124-ci-integration)
- [12.5 Agent-Executable Complexity Checklist](#125-agent-executable-complexity-checklist)
- [13. Technical Debt Register](#13-technical-debt-register)
- [14. Judgment Over Dogma](#14-judgment-over-dogma)
- [14.1 The Clean Code vs. "A Philosophy of Software Design" Debate](#141-the-clean-code-vs-a-philosophy-of-software-design-debate)
- [14.2 DRY Absolutism vs. AHA/WET](#142-dry-absolutism-vs-ahawet)
- [14.3 When NOT to Refactor](#143-when-not-to-refactor)
- [14.4 Hard Caps Are Tooling Defaults, Not Physical Law](#144-hard-caps-are-tooling-defaults-not-physical-law)
- [14.5 Reviewing AI-Generated Code in 2026](#145-reviewing-ai-generated-code-in-2026)


## 1. Canonical Coding Principles (RULE-01–RULE-13 retired)

The legacy `RULE-01`–`RULE-13` principle IDs are retired. Cite the `CC-*` IDs in [clean-code-standard.md](clean-code-standard.md) instead. Old citations map as follows:

| Retired ID | Principle | Cite instead |
|---|---|---|
| RULE-01 | Correctness first | P1 correctness finding + `CC-TST-01` |
| RULE-02 | Clarity over cleverness | `CC-NAM-01`, `CC-FLOW-01`, `CC-FLOW-02` |
| RULE-03 | Single responsibility | `CC-FUN-01` |
| RULE-04 | High cohesion, low coupling | `CC-TYP-03` |
| RULE-05 | Encapsulate volatility | `CC-TYP-03` |
| RULE-06 | Local reasoning | `CC-FUN-02`, `CC-FLOW-03` |
| RULE-07 | Small, focused units | `CC-FUN-01` (the old "extract helpers until small" mandate is dropped; see § 14.1 and § 14.4) |
| RULE-08 | Explicit contracts | `CC-DOC-01`, `CC-TYP-01` |
| RULE-09 | Fail safely | `CC-ERR-01`, `CC-ERR-02`, `CC-SEC-01` |
| RULE-10 | Testability | `CC-FUN-04`, `CC-TST-01` |
| RULE-11 | Simple first, general later | `CC-FUN-06` |
| RULE-12 | Continuous improvement | No `CC-*` rule (process, not a code property); see § 14.3 and [qa-refactoring](../../qa-refactoring/SKILL.md) |
| RULE-13 | Operational observability | `CC-OBS-03` |

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
   - Split responsibilities into units that satisfy CC-FUN-01 and CC-TYP-03.
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
   - Re-run the area against the `CC-*` catalog.

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
   - Evaluate responsibilities, dependencies, and abstractions against CC-FUN-01 and CC-TYP-03.
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

Retired (duplicated the owning skill). Review execution, severity rubric, and approval rules live in [software-code-review/references/operational-playbook.md](../../software-code-review/references/operational-playbook.md); complexity-focused review lives in [software-code-review/references/complexity-only-review-pass.md](../../software-code-review/references/complexity-only-review-pass.md). Cite `CC-*` IDs from [clean-code-standard.md](clean-code-standard.md) in comments.

## 4. Refactoring Decision Trees

Retired (duplicated the owning skill). When to refactor, refactor-vs-rewrite, scope, and operation choice live in [qa-refactoring](../../qa-refactoring/SKILL.md) ([references/operational-patterns.md](../../qa-refactoring/references/operational-patterns.md), [references/refactoring-catalog.md](../../qa-refactoring/references/refactoring-catalog.md)). The "when NOT to refactor" judgment stays in § 14.3 below.

## 5. Legacy Code Survival Kit

Retired (duplicated the owning skill). Stabilize-first characterization tests, seams, incremental change, and retirement live in [qa-refactoring/references/legacy-code-strategies.md](../../qa-refactoring/references/legacy-code-strategies.md) and [working-effectively-with-legacy-code-operational-checklist.md](working-effectively-with-legacy-code-operational-checklist.md).

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

Retired (duplicated the owning skill). Smell catalog and correction routines (god object, long method, primitive obsession, shotgun surgery, feature envy, global mutable state, commented-out code) live in [qa-refactoring/references/code-smells-guide.md](../../qa-refactoring/references/code-smells-guide.md) and [qa-refactoring/references/refactoring-catalog.md](../../qa-refactoring/references/refactoring-catalog.md). Cite the matching `CC-*` rule (e.g. `CC-FUN-01`, `CC-TYP-02`, `CC-FLOW-03`, `CC-DOC-04`) when flagging them in review.

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
- [ ] Design respects existing architecture and the `CC-*` catalog.
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
| CC-TST-*, CC-FUN-04 | Correctness, testing, verification | Code Complete; The Pragmatic Programmer; The Practice of Programming; The Clean Coder |
| CC-NAM-*, CC-FLOW-*, CC-FUN-01 | Clarity, small functions, readability | Clean Code; Refactoring; The Art of Clean Code |
| CC-FUN-01, CC-TYP-03 | Responsibilities, coupling, cohesion | Clean Code; Design Patterns; Code Complete |
| CC-TYP-03, CC-SEC-05 | Encapsulation of volatility, dependency management | Design Patterns; Working Effectively with Legacy Code; Refactoring |
| CC-FUN-02, CC-FLOW-03 | Local reasoning, incremental improvement | The Pragmatic Programmer; Code Complete; Working Effectively with Legacy Code |
| CC-ERR-*, CC-OBS-* | Error handling, observability | The Pragmatic Programmer; The Practice of Programming; modern clean-code practice literature |
| § 2.2, qa-refactoring | Safe refactoring, small steps | Refactoring; Working Effectively with Legacy Code |
| § 10.8, software-code-review | Structured code reviews | Best Kept Secrets of Peer Code Review; Implementing Effective Code Reviews; Looks Good To Me |
| qa-refactoring legacy strategies | Legacy system strategies | Working Effectively with Legacy Code; Refactoring; The Pragmatic Programmer |

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

### 10.8 Peer Review Controls (Cisco/SmartBear peer-review research)

The specific numbers below trace to Jason Cohen's Cisco Systems code-review study (published as *Best Kept Secrets of Peer Code Review*, SmartBear, 2006). It is one company's data set, not a universal law — treat it as a well-evidenced starting point and recalibrate against your own team's defect data over time.

- Headline numbers: Review under 200 LOC, never over 400; under 60 minutes per session, never over 90; best detection below ~300 LOC/h (under 500 still acceptable); top advice 100–300 LOC in 30–60 minutes.
- Size limits: these are the chapter's recommendations, not observed averages. Split larger changes; reject or rescope anything that cannot be reviewed in one focused sitting.
- Pace: the chapter also reports that reviewers slower than ~400 LOC/hour found above-average defect density, and that above ~450 LOC/hour defect density was below average in 87% of cases. Treat pace as a signal, not a hard cutoff.
- Timebox: past ~60 minutes reviewer fatigue sets in; break up longer reviews rather than pushing through in one sitting.
- Author preparation: the study found author-side annotation and self-review before sending measurably lowered defect density — cheap, high-leverage practice.
- Tooling guardrails: flag reviews with implausibly short durations or high LOC/hour rates as likely "rubber-stamp" approvals and prompt for a second look — treat the exact cutoff as a team-tunable heuristic, not a number from the source study.
- Metrics: track defect density per review; use size and pace outliers as a signal to coach smaller PRs and slower pace, not to game counts.

Source: Cohen, *Best Kept Secrets of Peer Code Review*, SmartBear 2006, Cisco chapter ([PDF](https://static1.smartbear.co/support/media/resources/cc/book/code-review-cisco-case-study.pdf), conclusions); [Smart Bear, Cisco, and the Largest Study on Code Review Ever](https://mikeconley.ca/blog/2009/09/14/smart-bear-cisco-and-the-largest-study-on-code-review-ever/) (secondary summary); [SmartBear — Best Practices for Peer Code Review](https://smartbear.com/learn/code-review/best-practices-for-peer-code-review/).

---

## 11. LLM-Generated Code Review Protocol

### 11.1 Why LLM Code Needs Special Review

LLM-generated code introduces distinct failure modes not covered by traditional code review:

- **Hallucinated APIs**: Non-existent methods, incorrect signatures, deprecated functions
- **Outdated patterns**: Any model's knowledge has some cutoff and can lag current library/framework guidance by an unpredictable amount — verify against current docs rather than assuming a fixed lag window
- **Plausible-looking bugs**: Code that appears correct but has subtle logic errors
- **Context blindness**: Ignores existing codebase patterns, introduces inconsistencies

By 2026, "review AI-generated code like human code, but verify harder" is the working consensus — the review load has shifted from spotting typos to verifying imports/APIs actually exist and that style matches the surrounding codebase, not an abstract style guide. Don't pin these checks to a specific model or vendor; the failure modes below are common across current-generation coding assistants and change as models improve.
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
- Replacing an established component pattern with a different one without a requested migration
- Wrong async/await patterns
- Deprecated Express middleware

**Python**:
- Returning a plausible default from an error path and hiding the failed operation
- Weakening or deleting an assertion until a failing test passes
- `requests` without timeout
- Adding a duplicate helper beside an existing one
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
- Target language and toolchain versions, copied from the project's lockfile/manifest (not from memory). Note that major compiler lines can split: a new major (for example a native-port TypeScript compiler) may ship before its programmatic API, so tools that embed the compiler keep running the previous major side by side. Check the release notes and name the version the code must compile under.
- Framework versions, again from the lockfile
- Existing patterns ("Match our existing error handling in src/utils/errors.ts")
- Security requirements ("Use parameterized queries only")
- Test requirements ("Include unit tests with edge cases")

**Request Verification**:
- "List all external packages this code requires"
- "Confirm all imported APIs exist in [package version]"
- "Identify potential security concerns"
- "What edge cases should be tested?"

### 11.12 Metrics for LLM Code Quality

Track metrics like these to improve LLM code quality over time. The targets below are illustrative starting points, not published benchmarks — no independently verified industry-wide figures for "acceptable hallucination rate" exist as of this writing. Set your own baseline from your team's first month of data, then tighten it.

| Metric | Illustrative Starting Target | Action if Exceeded |
|--------|--------|-------------------|
| Hallucination rate (PRs with a non-existent API/import) | Baseline from your own data, then drive down | Improve prompts, add verification |
| Type errors per PR | 0 | Run type check in CI before review |
| Security issues per PR | 0 | Add security scanning to pipeline |
| Test failure rate | Baseline from your own data | Require tests pass before merge |
| Pattern violations | Baseline from your own data | Document patterns, improve prompts |

**Tracking Command**:

```bash
# Log LLM code issues for analysis
echo "$(date -Iseconds),hallucination,import,express" >> llm-code-issues.csv
```

---

## 12. Complexity Management

Systematic approaches to measuring, monitoring, and reducing codebase complexity.

### 12.1 Complexity Metrics

Only the first two thresholds have a named source: cyclomatic complexity 10 is McCabe's limit as documented in NIST SP 500-235 (which also notes limits up to 15 used successfully), and cognitive complexity 15 is SonarSource's tool default. Every other number below is an illustrative team default with no study behind it — calibrate against your own codebase and change-failure data, and see § 14.4 before gating merges on any of them.

| Metric | Threshold | Basis | Tool | Action |
|--------|-----------|-------|------|--------|
| Cyclomatic Complexity | >10 per function | McCabe / NIST SP 500-235 | eslint `complexity` rule, radon | Refactor or split function |
| Cognitive Complexity | >15 per function | SonarSource default | SonarQube, codeclimate | Simplify control flow |
| Lines per Function | >50 lines (illustrative) | Team default | eslint, pylint | Consider extracting helpers if the function mixes concerns |
| Parameters per Function | >4 parameters (illustrative) | Team default | eslint, pylint | Consider a parameter object (CC-FUN-03) |
| Nesting Depth | >3 levels (illustrative) | Team default | eslint, pylint | Use guard clauses, early returns |
| File Length | >400 lines (illustrative) | Team default | custom script | Review whether the module has one cohesive purpose |
| Dependencies per Module | >7 imports (illustrative) | Team default | madge, import-graph | Review module boundaries |

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
- [ ] Functions above the team's parameter-count default (illustrative: 4) justified or grouped (CC-FUN-03)
- [ ] Nesting above the team's depth default (illustrative: 3) justified or flattened
- [ ] Complex conditionals extracted to well-named functions
- [ ] Guard clauses used for early validation
- [ ] Complex calculations isolated in pure functions

---

## 13. Technical Debt Register

Retired (duplicated the owning skills). Debt classification, register templates, tracking workflow, and debt metrics live in [product-management/references/technical-debt-management.md](../../product-management/references/technical-debt-management.md) and [qa-refactoring/references/tech-debt-management.md](../../qa-refactoring/references/tech-debt-management.md). The agent-introduced shortcut marker convention stays here as `CC-DOC-05` in [clean-code-standard.md](clean-code-standard.md).

---

## 14. Judgment Over Dogma

Clean-code guidance is durable where it encodes coupling/cohesion, naming, and interface design; it becomes cargo cult when specific numeric rules (function length, comment bans, DRY-at-all-costs) are applied as universal law regardless of context. This section makes that distinction explicit so agents apply the CC-* catalog with judgment, not by rote.

### 14.1 The Clean Code vs. "A Philosophy of Software Design" Debate

Robert C. Martin's *Clean Code* (2nd ed., 2025, Addison-Wesley) and John Ousterhout's *A Philosophy of Software Design* hold different, both well-argued positions on function size, comments, and decomposition. In late 2024–early 2025 the two authors held a public, recorded debate and published a written discussion of where their books agree and disagree (see [johnousterhout/aposd-vs-clean-code](https://github.com/johnousterhout/aposd-vs-clean-code)). Key tension points relevant to this standard:

- **Function length**: Martin favors very short functions (a handful of lines); Ousterhout argues that splitting logic purely to hit a line-count target can fragment a single cohesive idea across many "shallow" functions, each adding interface overhead without reducing real complexity — his heuristic is deep modules (small interface, large functionality) over many shallow ones.
- **Comments**: Martin treats most comments as a failure to make code self-explanatory; Ousterhout argues well-placed comments capture design intent and non-obvious rationale that naming alone cannot carry, especially at module boundaries.
- **Practical takeaway for this skill**: apply CC-FUN-01 (one dominant responsibility) and CC-DOC-02 (comments explain "why") as the durable rules. Do not treat "function must be under N lines" or "comments are a code smell" as absolute — judge by whether the split, or the comment, makes the code easier to change safely.

### 14.2 DRY Absolutism vs. AHA/WET

Strict DRY (Don't Repeat Yourself, from *The Pragmatic Programmer*) is durable when duplication represents one true rule that must change consistently (CC-FUN-05). It becomes a trap when two call sites look similar today but represent independent business rules that will diverge — premature abstraction over that duplication (a shared helper serving unrelated concerns) creates hidden coupling that is harder to undo than the original duplication. The community counter-heuristics worth citing explicitly:

- **WET** ("Write Everything Twice" / "Waste Everyone's Time" as its critics call it) — informally, tolerate duplication until a third occurrence proves it is really the same rule (the "rule of three").
- **AHA** ("Avoid Hasty Abstraction," coined by Kent C. Dodds) — prefer duplication over the wrong abstraction; extract only once the abstraction is obvious from real, repeated need.
- **Practical takeaway**: treat CC-FUN-05 as "eliminate duplication that is bug-prone or certain to diverge together," not "never write similar-looking code twice"; cite CC-FUN-06 for the premature-abstraction side.

### 14.3 When NOT to Refactor

Refactoring is a cost with a payoff, not a default good. Skip or defer refactoring when:

- The code is stable, low-change-frequency, and correct — improving its internals produces review risk with no user-visible benefit (refactor-timing guidance: [qa-refactoring](../../qa-refactoring/SKILL.md)).
- A release deadline makes a large behavior-preserving refactor itself the riskiest change in the diff — prefer the smallest change that satisfies the request and log the cleanup as debt (`CC-DOC-05` marker; process in [product-management/references/technical-debt-management.md](../../product-management/references/technical-debt-management.md)) instead.
- Test coverage is too weak to safely validate that behavior is preserved, and adding characterization tests is out of scope for the current change — refactor only after coverage exists ([qa-refactoring/references/legacy-code-strategies.md](../../qa-refactoring/references/legacy-code-strategies.md)).
- The only justification is a metric threshold (§ 12) with no evidence of real defect risk or change friction — refactoring to satisfy a dashboard, not a problem, is itself an anti-pattern (§ 12 Anti-Patterns).
- The surrounding code is scheduled for removal or replacement — polishing code that will be deleted wastes review effort.

### 14.4 Hard Caps Are Tooling Defaults, Not Physical Law

Numeric thresholds in this playbook and in [code-complexity-metrics.md](code-complexity-metrics.md) (cyclomatic complexity 10, cognitive complexity 15, function length 20–50 lines, nesting depth 3) come from a mix of real research (McCabe's cyclomatic complexity threshold of 10 is supported by NIST Special Publication 500-235) and tool defaults (SonarSource's cognitive-complexity default of 15). They are useful starting points for CI gates, not proof that code above the threshold is wrong or code below it is safe. Utility/parsing/serialization code legitimately runs higher on these metrics without being poorly designed; apply judgment per the Anti-Patterns table in that reference rather than blocking merges on the number alone.

### 14.5 Reviewing AI-Generated Code in 2026

The review bottleneck has moved. A few years ago the scarce resource was writing code; now it is verifying code that was generated quickly and reads as plausible. The durable adjustments, independent of which vendor or model produced the code:

- Verify imports, APIs, and library versions actually exist and match the project's dependency versions before trusting the logic (§ 11.2–11.4).
- Check consistency with the existing codebase's actual patterns (error handling, logging, naming) over any abstract external style guide (§ 11.5) — a generated PR that is individually "clean" but inconsistent with its neighbors increases long-run maintenance cost.
- Do not pin review checklists to a specific model name or version; hallucination and staleness patterns are common across current-generation coding assistants and shift as models change, so keep the checks behavior-based (does the import resolve? does the type check pass?) rather than tied to one vendor's release.
