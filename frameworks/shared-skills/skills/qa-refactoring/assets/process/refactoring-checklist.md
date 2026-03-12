# Refactor Safety Checklist (Characterization + Incremental Steps)

Copy-paste checklist for safe refactoring that preserves behavior and reduces regression risk.

## Core

## Pre-Refactoring Checklist

Before starting any refactoring:

- [ ] **Safety net exists** for code being refactored
  - [ ] If tests already exist: identify which tests guard the behavior
  - [ ] If tests are missing: add characterization tests for current behavior (Feathers: https://michaelfeathers.silvrback.com/characterization-testing)
  - [ ] Flaky tests addressed (fix or quarantine with owner + expiry)
- [ ] **Version control** is up to date
  - [ ] All changes committed
  - [ ] Working on feature branch
  - [ ] Branch is up to date with main
- [ ] **Baseline metrics** recorded
  - [ ] Current lines of code
  - [ ] Cyclomatic complexity
  - [ ] Code coverage percentage
  - [ ] SonarQube debt ratio (if available)
- [ ] **Refactoring scope** is defined
  - [ ] Specific files/classes identified
  - [ ] Clear goal stated (e.g., "reduce complexity")
  - [ ] Time-boxed (e.g., "2 hours max")
- [ ] **PR plan** is safe
  - [ ] Refactor-only PR (no feature changes mixed in)
  - [ ] Rollback strategy defined (revertable commits)
- [ ] **Stakeholders informed**
  - [ ] Team aware of refactoring session
  - [ ] No conflicting work on same files

---

## During Refactoring Checklist

### Every 15-30 Minutes

- [ ] **Run tests** after each small change
- [ ] **Commit** working code with descriptive message
- [ ] **Verify** behavior hasn't changed
  - [ ] No new failing tests
  - [ ] No performance degradation
  - [ ] Same output for same input

### Code Quality Checks

#### Method-Level Refactoring

- [ ] **Method length** < 20 lines
- [ ] **Method complexity** < 10 (cyclomatic)
- [ ] **Single responsibility** - method does one thing
- [ ] **Meaningful name** - describes what it does
- [ ] **Parameters** < 4 (use parameter objects if more)
- [ ] **No side effects** unless clearly named (e.g., `saveAndNotify`)
- [ ] **Comments removed** if code is self-explanatory
- [ ] **Magic numbers** extracted to named constants

#### Class-Level Refactoring

- [ ] **Class length** < 300 lines
- [ ] **Single responsibility** - one reason to change
- [ ] **Low coupling** - minimal dependencies on other classes
- [ ] **High cohesion** - related functionality grouped
- [ ] **Meaningful name** - describes purpose
- [ ] **No God objects** - not doing too much
- [ ] **Fields encapsulated** - private with getters/setters if needed
- [ ] **No duplicate code** within class

#### Code Smell Removal

- [ ] **Duplicate code** extracted to shared method
- [ ] **Long parameter lists** replaced with parameter objects
- [ ] **Large classes** split into focused classes
- [ ] **Switch statements** replaced with polymorphism (if appropriate)
- [ ] **Primitive obsession** replaced with value objects
- [ ] **Feature envy** fixed by moving method to proper class
- [ ] **Temporary fields** eliminated
- [ ] **Dead code** removed

---

## Post-Refactoring Checklist

### Verification

- [ ] **All tests pass**
  - [ ] Unit tests: [check]
  - [ ] Integration tests: [check]
  - [ ] E2E tests: [check]
- [ ] **Code coverage maintained or improved**
  - [ ] Before: ____%
  - [ ] After: ____%
- [ ] **Performance unchanged or improved**
  - [ ] Run performance benchmarks
  - [ ] Check memory usage
  - [ ] Verify response times
- [ ] **Linter passes** with no new warnings
- [ ] **Type checker passes** (if applicable)

### Metrics Improvement

- [ ] **Complexity reduced**
  - [ ] Before: _____
  - [ ] After: _____
- [ ] **Lines of code** (should decrease or stay same)
  - [ ] Before: _____
  - [ ] After: _____
- [ ] **Code duplication** reduced
  - [ ] Before: ____%
  - [ ] After: ____%
- [ ] **Technical debt** reduced (SonarQube)
  - [ ] Before: _____
  - [ ] After: _____

### Documentation

- [ ] **Commit message** describes refactoring
  - Example: "Refactor UserService: extract validation logic, reduce complexity from 25 to 8"
- [ ] **PR description** explains changes
  - Why refactoring was needed
  - What changed
  - Metrics before/after
- [ ] **Code comments** updated if needed
- [ ] **README** updated if architecture changed
- [ ] **Technical debt register** updated

### Code Review Preparation

- [ ] **Self-review** completed
  - [ ] Check diff for unintended changes
  - [ ] Verify no debug code left
  - [ ] Ensure consistent formatting
- [ ] **Tests demonstrate** refactoring didn't break functionality
- [ ] **Screenshots/metrics** show improvement
- [ ] **Reviewers assigned**

---

## Specific Refactoring Patterns

### Extract Method

- [ ] Identified code block that can be grouped
- [ ] Created method with descriptive name
- [ ] Moved code to new method
- [ ] Replaced original code with method call
- [ ] Verified tests still pass
- [ ] No duplicate code created

### Rename Variable/Method/Class

- [ ] New name is more descriptive
- [ ] New name follows naming conventions
- [ ] All references updated
- [ ] Tests still pass
- [ ] Documentation updated

### Extract Class

- [ ] Identified cohesive group of methods/fields
- [ ] Created new class with clear responsibility
- [ ] Moved methods/fields to new class
- [ ] Updated original class to use new class
- [ ] Tests still pass
- [ ] Both classes have single responsibility

### Replace Conditional with Polymorphism

- [ ] Identified type-based conditional logic
- [ ] Created interface or abstract class
- [ ] Created concrete subclasses for each type
- [ ] Moved type-specific logic to subclasses
- [ ] Replaced conditional with polymorphic call
- [ ] Tests still pass

### Introduce Parameter Object

- [ ] Identified related parameters (3+)
- [ ] Created parameter object class
- [ ] Updated method signature
- [ ] Updated all call sites
- [ ] Tests still pass
- [ ] Code is more readable

---

## Emergency Rollback Checklist

If refactoring causes issues:

- [ ] **Stop immediately** - don't add more changes
- [ ] **Identify issue**
  - Which test is failing?
  - What behavior changed?
- [ ] **Options**:
  - [ ] Quick fix (< 15 minutes)
  - [ ] Revert last commit
  - [ ] Revert entire refactoring branch
- [ ] **After rollback**:
  - [ ] Understand what went wrong
  - [ ] Plan safer approach
  - [ ] Add more tests before trying again

---

## Boy Scout Rule Checklist

When touching existing code (not dedicated refactoring session):

- [ ] Leave code **better than you found it**
- [ ] Fix at least **one code smell**
- [ ] Add at least **one test** if missing
- [ ] Improve at least **one variable name**
- [ ] Extract at least **one magic number** to constant
- [ ] Remove at least **one comment** by making code self-explanatory
- [ ] Changes are **small and safe**
- [ ] Changes **don't delay** feature delivery

---

## Optional: AI / Automation

Do:
- Use AI to propose mechanical refactors (rename/extract/move) and lint fixes; verify behavior with tests and contracts.
- Use AI to summarize diffs and highlight risky areas; validate by running characterization and integration tests.

Avoid:
- Accepting AI refactors that change behavior without explicit requirements and regression tests.
- Letting AI "fix CI" by weakening assertions or deleting tests.

## Team Refactoring Session Checklist

For organized team refactoring days:

### Before Session

- [ ] **Goal identified** (e.g., "reduce UserService complexity")
- [ ] **Time allocated** (e.g., "4-hour session")
- [ ] **Team available** - no meetings scheduled
- [ ] **Branch created** for refactoring
- [ ] **Baseline metrics** captured
- [ ] **Areas prioritized** by impact

### During Session

- [ ] **Pair/mob programming** - not solo refactoring
- [ ] **Small commits** every 15-30 minutes
- [ ] **Tests run** after each commit
- [ ] **Progress tracked** on board
- [ ] **Breaks taken** every 90 minutes

### After Session

- [ ] **Metrics compared** to baseline
- [ ] **PR created** with before/after stats
- [ ] **Team demo** of improvements
- [ ] **Retrospective** - what worked, what didn't
- [ ] **Next session planned** if needed

---

## Refactoring Safety Levels

Use this to assess risk:

### Level 1: Safe (No Tests Required)

- Rename variable (IDE refactoring)
- Extract constant
- Reorder method parameters (with IDE)
- Format code

### Level 2: Low Risk (Basic Tests)

- Extract method
- Inline variable
- Rename method/class (with IDE)
- Add parameter

### Level 3: Medium Risk (Good Test Coverage)

- Move method to another class
- Extract class
- Split conditional
- Replace conditional with polymorphism

### Level 4: High Risk (Extensive Tests Required)

- Change class hierarchy
- Modify algorithm
- Change data structure
- Refactor across multiple files

**Rule**: Never attempt Level 3-4 refactoring without 80%+ test coverage.

---

## Quick Refactoring Wins Checklist

15-minute improvements anyone can do:

- [ ] Remove unused imports
- [ ] Remove commented-out code
- [ ] Fix spelling in variable names
- [ ] Extract magic numbers to constants
- [ ] Add missing braces to single-line conditionals
- [ ] Break long lines (>120 characters)
- [ ] Add whitespace for readability
- [ ] Remove unnecessary else after return
- [ ] Replace var with const/let (JavaScript)
- [ ] Add missing error handling

---

## Summary Checklist

Before marking refactoring as complete:

- [ ] All tests pass [check]
- [ ] Code coverage maintained/improved [check]
- [ ] Metrics improved [check]
- [ ] Code is more readable [check]
- [ ] No new bugs introduced [check]
- [ ] Team reviewed and approved [check]
- [ ] Documentation updated [check]
- [ ] Committed and pushed [check]

**Time spent**: _____ hours
**Value delivered**: [Improved maintainability / Reduced complexity / Enabled feature X]

---

## Template for Refactoring Commit Message

```
Refactor [Component]: [Brief description]

What changed:
- [Change 1]
- [Change 2]
- [Change 3]

Why:
- [Reason 1]
- [Reason 2]

Metrics:
- Complexity: [Before] → [After]
- Lines of code: [Before] → [After]
- Test coverage: [Before] → [After]

Tests: All passing [check]
```

Example:
```
Refactor UserService: Extract validation and reduce complexity

What changed:
- Extracted email validation to EmailValidator class
- Extracted password validation to PasswordValidator class
- Split UserService into UserService and UserRepository
- Reduced method lengths from 50+ to < 20 lines

Why:
- UserService was 800 lines (God object)
- Cyclomatic complexity was 35 (very high risk)
- Mixed concerns (validation, persistence, business logic)

Metrics:
- Complexity: 35 → 8
- Lines of code: 800 → 250
- Test coverage: 45% → 82%

Tests: All passing [check]
```
