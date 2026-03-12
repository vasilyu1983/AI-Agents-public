# Operational Patterns and Standards

## Contents

- [Pattern: Classic Refactoring Catalog](#pattern-classic-refactoring-catalog)
- [Pattern: Code Smells Detection](#pattern-code-smells-detection)
- [Pattern: Technical Debt Management](#pattern-technical-debt-management)
- [Pattern: Automated Quality Gates](#pattern-automated-quality-gates)
- [Pattern: Legacy Code Modernization](#pattern-legacy-code-modernization)
- [Enterprise-Grade AI Refactoring Platforms](#enterprise-grade-ai-refactoring-platforms)
- [Popular Developer Tools](#popular-developer-tools)
- [AI Capabilities in Modern Refactoring](#ai-capabilities-in-modern-refactoring)
- [Quality & Testing](#quality--testing)
- [Code Review & Security](#code-review--security)
- [Architecture & Design](#architecture--design)
- [Frontend & Backend Development](#frontend--backend-development)
- [DevOps & Data](#devops--data)
- [Common Workflows](#common-workflows)

## Pattern: Classic Refactoring Catalog

**Use when:** Improving code structure without changing behavior.

**Extract Method:**
```javascript
// Before: Long method with mixed concerns
function processOrder(order) {
  // Validate
  if (!order.items || order.items.length === 0) {
    throw new Error('Empty order');
  }

  // Calculate total
  let total = 0;
  for (const item of order.items) {
    total += item.price * item.quantity;
  }

  // Apply discount
  if (order.coupon) {
    const discount = total * order.coupon.percentage;
    total -= discount;
  }

  // Save
  db.orders.insert({ ...order, total });
}

// After: Extracted methods
function processOrder(order) {
  validateOrder(order);
  const total = calculateTotal(order);
  saveOrder(order, total);
}

function validateOrder(order) {
  if (!order.items || order.items.length === 0) {
    throw new Error('Empty order');
  }
}

function calculateTotal(order) {
  const subtotal = order.items.reduce(
    (sum, item) => sum + item.price * item.quantity,
    0
  );
  return applyDiscount(subtotal, order.coupon);
}

function applyDiscount(amount, coupon) {
  if (!coupon) return amount;
  return amount * (1 - coupon.percentage);
}

function saveOrder(order, total) {
  db.orders.insert({ ...order, total });
}
```

**Replace Conditional with Polymorphism:**
```typescript
// Before: Type-checking with conditionals
class Bird {
  type: string;

  getSpeed(): number {
    switch (this.type) {
      case 'european':
        return this.getBaseSpeed();
      case 'african':
        return this.getBaseSpeed() - this.getLoadFactor();
      case 'norwegian-blue':
        return this.isNailed ? 0 : this.getBaseSpeed();
      default:
        throw new Error('Unknown bird type');
    }
  }
}

// After: Polymorphic classes
abstract class Bird {
  abstract getSpeed(): number;
  protected abstract getBaseSpeed(): number;
}

class EuropeanBird extends Bird {
  getSpeed(): number {
    return this.getBaseSpeed();
  }

  protected getBaseSpeed(): number {
    return 35;
  }
}

class AfricanBird extends Bird {
  constructor(private numberOfCoconuts: number) {
    super();
  }

  getSpeed(): number {
    return this.getBaseSpeed() - this.getLoadFactor();
  }

  private getLoadFactor(): number {
    return this.numberOfCoconuts * 2;
  }

  protected getBaseSpeed(): number {
    return 40;
  }
}

class NorwegianBlueBird extends Bird {
  constructor(private isNailed: boolean) {
    super();
  }

  getSpeed(): number {
    return this.isNailed ? 0 : this.getBaseSpeed();
  }

  protected getBaseSpeed(): number {
    return 32;
  }
}
```

**Introduce Parameter Object:**
```typescript
// Before: Long parameter list
function createUser(
  firstName: string,
  lastName: string,
  email: string,
  phone: string,
  address: string,
  city: string,
  state: string,
  zip: string
) {
  // ...
}

// After: Parameter object
interface UserData {
  firstName: string;
  lastName: string;
  email: string;
  phone: string;
  address: Address;
}

interface Address {
  street: string;
  city: string;
  state: string;
  zip: string;
}

function createUser(userData: UserData) {
  // ...
}
```

---

## Pattern: Code Smells Detection

**Use when:** Identifying areas needing refactoring.

**Common Code Smells:**

**1. Duplicated Code:**
```javascript
// Smell: Same logic in multiple places
function calculateEmployeeBonus(employee) {
  if (employee.department === 'sales') {
    return employee.salary * 0.15;
  }
  return employee.salary * 0.10;
}

function calculateManagerBonus(manager) {
  if (manager.department === 'sales') {
    return manager.salary * 0.15 + 5000;
  }
  return manager.salary * 0.10 + 5000;
}

// Fix: Extract common logic
const BONUS_RATES = {
  sales: 0.15,
  default: 0.10,
};

function getBonusRate(department) {
  return BONUS_RATES[department] || BONUS_RATES.default;
}

function calculateEmployeeBonus(employee) {
  return employee.salary * getBonusRate(employee.department);
}

function calculateManagerBonus(manager) {
  return calculateEmployeeBonus(manager) + 5000;
}
```

**2. Long Method (>20 lines):**
- Extract smaller methods
- Apply Single Responsibility Principle
- Use Extract Method refactoring

**3. Large Class (>300 lines or >10 methods):**
```typescript
// Smell: God class doing too much
class UserManager {
  createUser() {}
  deleteUser() {}
  authenticateUser() {}
  sendEmail() {}
  generateReport() {}
  processPayment() {}
}

// Fix: Split into focused classes
class UserService {
  createUser() {}
  deleteUser() {}
}

class AuthenticationService {
  authenticateUser() {}
}

class EmailService {
  sendEmail() {}
}

class ReportingService {
  generateReport() {}
}

class PaymentService {
  processPayment() {}
}
```

**4. Long Parameter List (>3 parameters):**
- Use parameter objects
- Builder pattern for complex objects

**5. Feature Envy:**
```javascript
// Smell: Method uses more features of another class
class Order {
  getTotal() {
    let total = 0;
    for (const item of this.items) {
      total += item.product.price * item.quantity;
      total -= item.product.discount;
    }
    return total;
  }
}

// Fix: Move logic closer to data
class OrderItem {
  getPrice() {
    return this.product.getDiscountedPrice() * this.quantity;
  }
}

class Product {
  getDiscountedPrice() {
    return this.price - this.discount;
  }
}

class Order {
  getTotal() {
    return this.items.reduce((sum, item) => sum + item.getPrice(), 0);
  }
}
```

**6. Primitive Obsession:**
```typescript
// Smell: Using primitives instead of small objects
function validateEmail(email: string): boolean {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}

// Fix: Create value object
class Email {
  constructor(private value: string) {
    if (!Email.isValid(value)) {
      throw new Error('Invalid email');
    }
  }

  static isValid(email: string): boolean {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
  }

  toString(): string {
    return this.value;
  }
}

// Usage
const userEmail = new Email('user@example.com'); // Validates automatically
```

**Checklist:**
- [ ] No duplicated code blocks (DRY principle)
- [ ] Methods < 20 lines (extract if longer)
- [ ] Classes < 300 lines (split if larger)
- [ ] Functions have < 4 parameters (use objects for more)
- [ ] No "God objects" doing too much
- [ ] Value objects for primitives with validation rules
- [ ] Logic lives close to the data it operates on

---

## Pattern: Technical Debt Management

**Use when:** Prioritizing and tracking code improvements.

**Technical Debt Quadrant:**

```
     High Impact
         │
 Reckless│Prudent
─────────┼─────────── Deliberate
 Reckless│Prudent
         │
     Low Impact

Inadvertent
```

**Debt Types:**
1. **Reckless Deliberate**: "We don't have time for design" (avoid)
2. **Prudent Deliberate**: "We must ship now, deal with consequences" (acceptable short-term)
3. **Reckless Inadvertent**: "What's layering?" (fix through training)
4. **Prudent Inadvertent**: "Now we know how we should have done it" (normal learning)

**Technical Debt Register:**

```markdown
| ID | Description | Type | Impact | Effort | Priority | Created | Owner |
|----|-------------|------|--------|--------|----------|---------|-------|
| TD-001 | Refactor UserService (600 lines) | Prudent Deliberate | High | 2 days | P1 | 2025-10-01 | Alice |
| TD-002 | Add tests for PaymentProcessor | Reckless Inadvertent | Medium | 3 days | P2 | 2025-09-15 | Bob |
| TD-003 | Extract shared validation logic | Prudent Inadvertent | Low | 1 day | P3 | 2025-11-01 | Charlie |
```

**Quantifying Technical Debt (SonarQube Metrics):**

```
Technical Debt Ratio = (Remediation Cost / Development Cost) * 100

Example:
Remediation Cost: 50 hours (to fix all issues)
Development Cost: 500 hours (total project time)
Debt Ratio: 10%

Thresholds:
< 5%: Excellent
5-10%: Good
10-20%: Needs attention
> 20%: Critical
```

**Boy Scout Rule:**
```
Leave the code better than you found it.

When touching a file:
- [ ] Fix at least one code smell
- [ ] Add missing tests
- [ ] Improve naming
- [ ] Extract duplicated code
- [ ] Add documentation
```

**Checklist:**
- [ ] Technical debt tracked in backlog
- [ ] Debt prioritized by impact and effort
- [ ] 20% of sprint capacity for debt reduction
- [ ] Code quality metrics monitored (SonarQube, CodeClimate)
- [ ] Debt discussed in retrospectives
- [ ] Boy Scout Rule enforced in code reviews

---

## Pattern: Automated Quality Gates

**Use when:** Preventing quality regression in CI/CD.

**ESLint Configuration (.eslintrc.js):**

```javascript
module.exports = {
  extends: ['eslint:recommended', 'plugin:@typescript-eslint/recommended'],
  rules: {
    'complexity': ['error', 10],  // Max cyclomatic complexity
    'max-lines': ['error', 300],   // Max lines per file
    'max-lines-per-function': ['error', 50],  // Max lines per function
    'max-params': ['error', 3],    // Max parameters
    'max-depth': ['error', 3],     // Max nesting depth
    'no-duplicate-code': 'error',  // Detect duplicates
    '@typescript-eslint/no-unused-vars': 'error',
    '@typescript-eslint/explicit-function-return-type': 'warn',
  },
};
```

**SonarQube Quality Gate:**

```yaml
# sonar-project.properties
sonar.projectKey=my-project
sonar.organization=my-org

# Quality Gate thresholds
sonar.qualitygate.wait=true
sonar.coverage.threshold=80
sonar.duplications.threshold=3
sonar.complexity.threshold=10
sonar.maintainability.rating=A
sonar.reliability.rating=A
sonar.security.rating=A
```

**Pre-commit Hooks (Husky + lint-staged):**

```json
{
  "husky": {
    "hooks": {
      "pre-commit": "lint-staged"
    }
  },
  "lint-staged": {
    "*.{js,ts}": [
      "eslint --fix",
      "prettier --write"
    ],
    "*.{js,ts,tsx}": [
      "jest --bail --findRelatedTests"
    ]
  }
}
```

**GitHub Actions Quality Check:**

```yaml
name: qa-refactoring

on: [pull_request]

jobs:
  quality:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Run ESLint
        run: npm run lint

      - name: Check code coverage
        run: npm run test:coverage

      - name: SonarQube Scan
        uses: sonarsource/sonarqube-scan-action@master
        env:
          SONAR_TOKEN: ${{ secrets.SONAR_TOKEN }}

      - name: Quality Gate Check
        run: |
          # Fail if quality gate fails
          if [ $SONAR_QUALITY_GATE == "ERROR" ]; then
            exit 1
          fi
```

**Checklist:**
- [ ] Linter configured (ESLint, Pylint, RuboCop)
- [ ] Formatter enforced (Prettier, Black, gofmt)
- [ ] Complexity limits set (cyclomatic complexity < 10)
- [ ] File size limits enforced (< 300 lines)
- [ ] Function length limits (< 50 lines)
- [ ] Test coverage threshold (> 80%)
- [ ] Pre-commit hooks run linter + formatter
- [ ] CI pipeline fails on quality gate violations

---

## Pattern: Legacy Code Modernization

**Use when:** Refactoring old codebases without tests.

**Strangler Fig Pattern:**

```
1. Identify seam (boundary between old and new)
2. Build new implementation alongside old
3. Redirect traffic to new implementation
4. Remove old implementation when confident

Example:
Old: Monolithic UserService
New: Microservice UserAPI

Phase 1: Proxy pattern (route 10% to new)
Phase 2: Increase to 50%
Phase 3: Full migration (100% new)
Phase 4: Remove old code
```

**Characterization Tests (Before Refactoring):**

```javascript
// 1. Write tests that describe current behavior (even if buggy)
describe('LegacyUserService', () => {
  it('returns user with uppercased name (weird, but current behavior)', () => {
    const user = legacyService.getUser(123);
    expect(user.name).toBe('JOHN DOE'); // Captures current behavior
  });
});

// 2. Refactor with confidence
function getUser(id) {
  const user = db.users.findById(id);
  return { ...user, name: user.name }; // Fix: removed toUpperCase()
}

// 3. Update tests to reflect correct behavior
it('returns user with original name casing', () => {
  const user = userService.getUser(123);
  expect(user.name).toBe('John Doe');
});
```

**Incremental Refactoring Steps:**

```
Week 1: Add characterization tests (no code changes)
Week 2: Extract methods, improve naming
Week 3: Split large classes
Week 4: Add proper error handling
Week 5: Modernize dependencies
Week 6: Remove dead code
Week 7: Performance optimization
Week 8: Final cleanup + documentation
```

**Checklist:**
- [ ] Characterization tests written before refactoring
- [ ] Refactor in small, safe steps (1 pattern at a time)
- [ ] Run full test suite after each change
- [ ] Use Strangler Fig for large rewrites
- [ ] Avoid "big bang" refactors (incremental > rewrite)
- [ ] Monitor performance metrics during migration
- [ ] Keep old code running until new is proven

---

# Modern AI-Assisted Tools (2025)

## Enterprise-Grade AI Refactoring Platforms

**Qodo (formerly CodiumAI)**:
- AI-driven code integrity platform with multi-agent architecture
- Supports 56+ programming languages for comprehensive refactoring
- Test-driven refactoring with autogenerated unit tests
- Designed for teams managing multi-million-line repositories with compliance requirements
- 4x better ROI when prioritizing high-impact legacy components

**Augment Code**:
- 200k-token context handling for deep codebase understanding
- Enterprise-grade security (ISO/IEC 42001 certified)
- Excels at multi-repository refactoring with dependency analysis
- Cross-language refactoring capabilities
- Systematic testing protocols reduce post-deployment issues by 70%

**Cursor AI**:
- AI-first code editor built on VS Code
- Deep codebase understanding with semantic analysis
- Context-aware refactoring recommendations
- Acts as personal coding assistant that understands your entire codebase

## Popular Developer Tools

**GitHub Copilot**:
- Real-time refactoring suggestions as you code
- Suggests Extract Method, Rename Variable, Simplify Conditional
- Works in VS Code, JetBrains IDEs, Neovim
- 20-30% faster refactoring according to 2025 studies

**Tabnine**:
- Intelligent code completion with error detection
- Refactoring assistance and automatic code documentation
- Excellent guidance for code improvement
- Multi-language support with team learning

**ReSharper (JetBrains)**:
- AI-driven .NET refactoring automation
- Deep refactor suggestions with context awareness
- Real-time code quality checks
- Automated method extraction and class decomposition

**IntelliJ IDEA AI Assistant**:
- Intelligent code insight for Java, Kotlin, and more
- Automates method extraction, variable renaming, class decomposition
- Flags architectural smells early
- Context-aware refactoring recommendations

**Embold**:
- Preventive refactoring by identifying anti-patterns
- Code smell detection before they snowball
- Visual scorecard of code health
- Complexity hotspot identification

## AI Capabilities in Modern Refactoring

**Semantic Understanding**:
- Parse code structure and understand variable scope
- Maintain consistency across function calls and imports
- Enhanced semantic analysis with larger context windows
- Understand relationships between distant code sections

**Strategic Approach**:
- Incremental implementation preferred over big-bang refactors
- Human oversight remains crucial for quality assurance
- Systematic measurement of code quality improvements
- Continuous refactoring as part of regular development

**Best Practices**:
- Treat refactoring as ongoing practice, not one-time project
- Continuously identify opportunities during feature development
- Apply AI-assisted techniques incrementally
- Measure impact: complexity reduction, maintainability improvement

**Impact**: Teams using AI-assisted refactoring see 20-30% faster refactoring cycles, 70% fewer post-deployment issues with proper testing protocols, and 4x better ROI when focusing on high-impact components.

---

# Related Skills

This skill works together with other quality and development skills. Use cross-skill combinations for comprehensive code improvement workflows.

## Quality & Testing

- [qa-testing-strategy](../../qa-testing-strategy/SKILL.md) - Test strategies to support safe refactoring; essential before attempting Level 3-4 refactorings
- [qa-debugging](../../qa-debugging/SKILL.md) - Debugging techniques for complex refactoring; use when refactoring introduces unexpected behavior
- [qa-observability](../../qa-observability/SKILL.md) - Monitoring code quality improvements and performance impact of refactoring
- [qa-resilience](../../qa-resilience/SKILL.md) - Building resilient systems during refactoring; error handling and fault tolerance patterns

## Code Review & Security

- [software-code-review](../../software-code-review/SKILL.md) - Review practices for refactored code; use for post-refactoring quality checks
- [software-security-appsec](../../software-security-appsec/SKILL.md) - Security considerations during refactoring; prevent introducing vulnerabilities

## Architecture & Design

- [software-architecture-design](../../software-architecture-design/SKILL.md) - Architectural patterns for large-scale refactoring; use for Extract Class, Move Method patterns
- [software-ui-ux-design](../../software-ui-ux-design/SKILL.md) - UI/UX considerations during frontend refactoring; maintain user experience during UI code improvements

## Frontend & Backend Development

- [software-frontend](../../software-frontend/SKILL.md) - Frontend-specific refactoring patterns; React hooks, component extraction, state management
- [software-backend](../../software-backend/SKILL.md) - Backend refactoring patterns; service decomposition, API versioning, database schema changes

## DevOps & Data

- [ops-devops-platform](../../ops-devops-platform/SKILL.md) - CI/CD integration for quality gates; automate refactoring checks in pipelines
- [data-sql-optimization](../../data-sql-optimization/SKILL.md) - Database refactoring patterns; schema evolution, query optimization, migration strategies

## Common Workflows

**Refactoring Legacy Code (High Risk)**:
1. Use [qa-refactoring](../SKILL.md) for characterization tests strategy
2. Use [qa-testing-strategy](../../qa-testing-strategy/SKILL.md) to build test coverage
3. Use [qa-debugging](../../qa-debugging/SKILL.md) if issues arise
4. Use [software-code-review](../../software-code-review/SKILL.md) for post-refactoring validation

**Establishing Quality Standards (New Project)**:
1. Use [qa-refactoring](../SKILL.md) for linting and quality gate setup
2. Use [ops-devops-platform](../../ops-devops-platform/SKILL.md) for CI/CD integration
3. Use [software-code-review](../../software-code-review/SKILL.md) for review checklists
4. Use [qa-testing-strategy](../../qa-testing-strategy/SKILL.md) for test pyramid

**Performance Optimization Refactoring**:
1. Use [qa-observability](../../qa-observability/SKILL.md) to identify bottlenecks
2. Use [qa-refactoring](../SKILL.md) to apply refactoring patterns
3. Use [qa-testing-strategy](../../qa-testing-strategy/SKILL.md) to add performance tests
4. Use [data-sql-optimization](../../data-sql-optimization/SKILL.md) if database queries are involved

---

# External Resources

See [data/sources.json](../data/sources.json) for:
- Refactoring books (Martin Fowler, Michael Feathers)
- Code quality tools (SonarQube, CodeClimate, ESLint)
- Modern AI-assisted tools (GitHub Copilot, ReSharper, IntelliJ IDEA)
- Refactoring patterns and techniques
- Legacy code rescue strategies
- 2025 industry best practices

---

# Quick Decision Matrix

| Scenario | Recommendation |
|----------|----------------|
| Long method (>50 lines) | Extract Method refactoring |
| Large class (>300 lines) | Split into smaller focused classes |
| Duplicated code | Extract to shared function/class |
| Complex conditionals | Replace Conditional with Polymorphism |
| Long parameter list | Introduce Parameter Object |
| Legacy code without tests | Write Characterization Tests first |
| Large rewrite needed | Strangler Fig Pattern (incremental) |
| Setting quality standards | Automated quality gates in CI/CD |

---

# Anti-Patterns to Avoid

- **Big bang refactors** - High risk, prefer incremental
- **Refactoring without tests** - Breaks things silently
- **Premature optimization** - Refactor for clarity first, performance second
- **Over-engineering** - Keep it simple (YAGNI)
- **Ignoring technical debt** - Compounds over time
- **No quality gates** - Quality degrades without enforcement
- **Rewriting from scratch** - Usually fails, prefer strangler fig

---

> **Success Criteria:** Code is maintainable, readable, testable, and follows established quality standards. Technical debt is tracked, prioritized, and actively reduced. Automated quality gates prevent regression.
