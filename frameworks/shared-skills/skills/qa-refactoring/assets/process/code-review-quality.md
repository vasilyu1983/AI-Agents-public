# Code Review Quality Checklist

Copy-paste checklist for reviewing code quality, maintainability, and technical debt.

---

## Quick Review (5 minutes)

Fast pass for obvious issues:

- [ ] **Linter passes** - no warnings
- [ ] **Tests pass** - all green
- [ ] **Builds successfully** - no errors
- [ ] **No debug code** - console.log, debugger, print statements removed
- [ ] **No commented-out code**
- [ ] **No TODOs** for critical functionality
- [ ] **Formatting consistent** - follows project style

---

## Comprehensive Review (30 minutes)

### Code Smells

#### Bloaters

- [ ] **No long methods** (>20 lines)
  - If found: Request Extract Method refactoring
- [ ] **No large classes** (>300 lines)
  - If found: Request Extract Class refactoring
- [ ] **No long parameter lists** (>3 parameters)
  - If found: Suggest Introduce Parameter Object
- [ ] **No primitive obsession** (string/number for domain concepts)
  - If found: Suggest value objects (Email, Money, etc.)
- [ ] **No data clumps** (same group of variables repeated)
  - If found: Suggest Extract Class

#### Object-Orientation Abusers

- [ ] **No switch statements on type codes**
  - If found: Suggest Replace Conditional with Polymorphism
- [ ] **No temporary fields** (fields only used sometimes)
  - If found: Suggest Extract Class or Remove Field
- [ ] **No refused bequest** (subclass not using parent's methods)
  - If found: Suggest Replace Inheritance with Delegation

#### Change Preventers

- [ ] **No divergent change** (class changed for many reasons)
  - If found: Violates Single Responsibility Principle
- [ ] **No shotgun surgery** (change requires updates in many classes)
  - If found: Suggest Move Method or Inline Class

#### Dispensables

- [ ] **No unnecessary comments** (code should be self-explanatory)
- [ ] **No duplicate code**
  - If found: Suggest Extract Method or Extract Class
- [ ] **No lazy classes** (classes doing too little)
  - If found: Suggest Inline Class or Remove Class
- [ ] **No dead code** (unused variables, methods, classes)
  - If found: Request removal
- [ ] **No speculative generality** ("in case we need it")
  - If found: Suggest YAGNI, remove unused abstractions

#### Couplers

- [ ] **No feature envy** (method uses more of another class)
  - If found: Suggest Move Method
- [ ] **No inappropriate intimacy** (classes too dependent)
  - If found: Suggest Extract Class or Hide Delegate
- [ ] **No message chains** (a.getB().getC().getD())
  - If found: Violates Law of Demeter, suggest Hide Delegate
- [ ] **No middle man** (class just delegates to another)
  - If found: Suggest Remove Middle Man or Inline Class

---

### Code Quality Metrics

#### Complexity

- [ ] **Cyclomatic complexity** < 10 per method
  - Tool: ESLint `complexity` rule, SonarQube
  - If >10: Request simplification
- [ ] **Cognitive complexity** < 15 per method
  - Measures understandability
  - If >15: Hard to understand, request refactoring
- [ ] **Nesting depth** < 3 levels
  - If deeper: Use guard clauses or Extract Method

#### Size Metrics

- [ ] **Method length** < 20 lines
  - If longer: Suggest Extract Method
- [ ] **Class length** < 300 lines
  - If longer: Suggest Extract Class
- [ ] **File length** < 500 lines
  - If longer: Consider splitting into modules
- [ ] **Line length** < 120 characters
  - If longer: Break into multiple lines

#### Maintainability

- [ ] **No magic numbers** - all constants named
  ```javascript
  // BAD: Bad
  if (age > 18) { /* ... */ }

  // GOOD: Good
  const LEGAL_ADULT_AGE = 18;
  if (age > LEGAL_ADULT_AGE) { /* ... */ }
  ```
- [ ] **Meaningful names** - variables, methods, classes
  ```javascript
  // BAD: Bad
  const x = users.filter(u => u.a > 18);

  // GOOD: Good
  const adultUsers = users.filter(user => user.age > 18);
  ```
- [ ] **No abbreviations** unless well-known (e.g., URL, HTTP)
- [ ] **Consistent naming** across codebase

---

### Design Principles

#### SOLID Principles

- [ ] **Single Responsibility Principle**
  - Each class/method has one reason to change
  - If violated: Class does too much, suggest splitting

- [ ] **Open/Closed Principle**
  - Open for extension, closed for modification
  - If violated: Suggest strategy pattern or inheritance

- [ ] **Liskov Substitution Principle**
  - Subtypes should be substitutable for base types
  - If violated: Check subclass overrides

- [ ] **Interface Segregation Principle**
  - Many specific interfaces > one general interface
  - If violated: Clients forced to depend on unused methods

- [ ] **Dependency Inversion Principle**
  - Depend on abstractions, not concretions
  - If violated: Hard-coded dependencies, suggest injection

#### DRY (Don't Repeat Yourself)

- [ ] **No duplicate code** in same file
- [ ] **No duplicate code** across files
- [ ] **No duplicate logic** with slight variations
  - If found: Extract shared logic, parameterize differences

#### YAGNI (You Aren't Gonna Need It)

- [ ] **No premature abstractions**
- [ ] **No unused parameters** "for future use"
- [ ] **No overly complex designs** for simple problems
- [ ] **No feature flags** for features not coming

#### KISS (Keep It Simple, Stupid)

- [ ] **Simplest solution** that works
- [ ] **No unnecessary complexity**
- [ ] **No over-engineering**

---

### Testing

#### Test Coverage

- [ ] **New code has tests**
  - [ ] Unit tests for business logic
  - [ ] Integration tests for external dependencies
  - [ ] E2E tests for critical user flows

- [ ] **Test coverage** > 80% for new code
  - Critical paths: 100%
  - Business logic: 90%+
  - Overall: 80%+

#### Test Quality

- [ ] **Tests are independent** - can run in any order
- [ ] **Tests are deterministic** - same result every time
- [ ] **Tests are fast** - unit tests < 1s each
- [ ] **Tests have clear names** - describe what they test
  ```javascript
  // BAD: Bad
  it('test1', () => { /* ... */ });

  // GOOD: Good
  it('should return 400 when email is invalid', () => { /* ... */ });
  ```
- [ ] **Tests use AAA pattern** - Arrange, Act, Assert
- [ ] **No test duplication** - use helper functions
- [ ] **Mocks used appropriately** - only for external dependencies

---

### Security

#### Common Vulnerabilities

- [ ] **No SQL injection** - use parameterized queries
  ```javascript
  // BAD: Bad
  db.query(`SELECT * FROM users WHERE id = ${userId}`);

  // GOOD: Good
  db.query('SELECT * FROM users WHERE id = ?', [userId]);
  ```

- [ ] **No XSS vulnerabilities** - escape user input
  ```javascript
  // BAD: Bad
  element.innerHTML = userInput;

  // GOOD: Good
  element.textContent = userInput;
  // or use DOMPurify for HTML
  ```

- [ ] **No command injection** - validate inputs
- [ ] **No hardcoded secrets** - use environment variables
- [ ] **No sensitive data in logs**
- [ ] **No weak crypto** - use industry standards (AES-256, bcrypt)
- [ ] **Input validation** on all user inputs
- [ ] **Authentication/authorization** implemented correctly

---

### Performance

#### Potential Issues

- [ ] **No N+1 queries** - use eager loading
  ```javascript
  // BAD: Bad
  const users = await User.findAll();
  for (const user of users) {
    user.orders = await Order.findByUserId(user.id); // N queries
  }

  // GOOD: Good
  const users = await User.findAll({ include: [Order] }); // 1 query
  ```

- [ ] **No unnecessary database calls** - cache if appropriate
- [ ] **No memory leaks** - clean up listeners, intervals
- [ ] **Efficient algorithms** - not O(n²) when O(n) possible
- [ ] **No blocking operations** in async code
- [ ] **Proper indexing** for database queries

---

### Error Handling

- [ ] **Errors handled appropriately**
  - Don't swallow errors silently
  - Log errors with context
  - Return meaningful error messages

- [ ] **No catch-all handlers** without re-throwing
  ```javascript
  // BAD: Bad
  try {
    await doSomething();
  } catch (error) {
    console.log(error); // Swallowed!
  }

  // GOOD: Good
  try {
    await doSomething();
  } catch (error) {
    logger.error('Failed to do something', { error });
    throw new ApplicationError('Operation failed', error);
  }
  ```

- [ ] **Specific error types** - not generic Error
- [ ] **Error messages are user-friendly** (for user-facing errors)
- [ ] **Stack traces preserved** when re-throwing

---

### Documentation

- [ ] **Public APIs documented** - JSDoc, TSDoc, etc.
  ```typescript
  /**
   * Calculates user's total order value.
   *
   * @param userId - The user's unique identifier
   * @param startDate - Filter orders from this date
   * @param endDate - Filter orders until this date
   * @returns Total order value in cents
   * @throws {UserNotFoundError} If user doesn't exist
   */
  async function calculateTotalOrders(
    userId: string,
    startDate: Date,
    endDate: Date
  ): Promise<number> {
    // ...
  }
  ```

- [ ] **Complex logic explained** - why, not what
  ```javascript
  // BAD: Bad
  // Multiply by 1.1
  const price = basePrice * 1.1;

  // GOOD: Good
  // Apply 10% VAT as required by EU regulations
  const VAT_RATE = 1.1;
  const price = basePrice * VAT_RATE;
  ```

- [ ] **README updated** if architecture changed
- [ ] **Breaking changes documented**

---

## Automated Checks

Use these tools to automate quality checks:

### Linters

- [ ] **ESLint** (JavaScript/TypeScript)
  ```json
  {
    "extends": ["eslint:recommended"],
    "rules": {
      "complexity": ["error", 10],
      "max-lines": ["error", 300],
      "max-lines-per-function": ["error", 20],
      "max-params": ["error", 3],
      "max-depth": ["error", 3]
    }
  }
  ```

- [ ] **Pylint** (Python)
- [ ] **RuboCop** (Ruby)
- [ ] **Clippy** (Rust)

### Code Quality Tools

- [ ] **SonarQube** - comprehensive analysis
- [ ] **CodeClimate** - maintainability metrics
- [ ] **Embold** - anti-pattern detection

### Security Scanners

- [ ] **npm audit** / **yarn audit** (JavaScript)
- [ ] **Snyk** - dependency vulnerabilities
- [ ] **OWASP Dependency-Check**

---

## Review Comments Template

### For Code Smells

```
**Code Smell: Long Method**

This method is 50 lines long, which makes it hard to understand and test.

Suggestion: Extract the validation logic into a separate `validateInput()` method and the calculation logic into `calculateTotal()`.

References:
- [Refactoring: Extract Method](https://refactoring.guru/extract-method)
- See references/refactoring-catalog.md
```

### For Complexity Issues

```
**High Complexity: 15**

This method has cyclomatic complexity of 15, which is above our threshold of 10.

Suggestion: Break down the nested conditionals using guard clauses, or use the Strategy pattern if this is polymorphic behavior.

Tool output:
```
eslint: complexity: Method 'processOrder' has complexity 15 (max 10)
```
```

### For Missing Tests

```
**Missing Test Coverage**

The new `PaymentProcessor` class has 0% test coverage.

Suggestion: Add unit tests covering:
- [ ] Happy path (successful payment)
- [ ] Error handling (failed payment)
- [ ] Edge cases (zero amount, negative amount)

Target coverage: 80%+
```

---

## Approval Criteria

Code is approved when ALL of these are true:

- [ ] **No critical issues** (security, bugs)
- [ ] **All automated checks pass** (linter, tests, build)
- [ ] **No major code smells** (God objects, high complexity)
- [ ] **Test coverage sufficient** (>80% for new code)
- [ ] **Documentation adequate**
- [ ] **Performance acceptable**
- [ ] **Follows team conventions**

---

## Technical Debt Assessment

If code has quality issues but must be merged:

### Document Technical Debt

```
**Technical Debt Created**

Issue: UserService class is 450 lines (>300 line limit)

Reason: Time-sensitive feature needed for demo

Impact: High (difficult to maintain)

Effort to fix: 1 day

Plan: Refactor in sprint 23 (TD-042)

Priority: P1 (high impact, low effort)
```

### Track in Debt Register

Add to technical debt register:
- ID: TD-XXX
- Description: Issue summary
- Type: Reckless/Prudent, Deliberate/Inadvertent
- Impact: High/Medium/Low
- Effort: Days to fix
- Priority: P1/P2/P3/P4
- Owner: Who will fix it
- Target sprint: When it will be addressed

---

## Summary Template

```
## Code Review Summary

**Overall**: [Approve / Request Changes / Reject]

**Positives**:
- [check] Good test coverage (85%)
- [check] Clean separation of concerns
- [check] Clear naming conventions

**Issues Found**:
- [FAIL] 3 methods exceed complexity threshold
- [WARNING] 1 missing error handler
- [WARNING] 2 minor code smells

**Action Items**:
1. Reduce complexity in `processOrder()` (Priority: High)
2. Add error handling in `validateInput()` (Priority: High)
3. Extract duplicated validation logic (Priority: Low)

**Technical Debt**:
- None created [check]

**Estimated Fix Time**: 2 hours
```
