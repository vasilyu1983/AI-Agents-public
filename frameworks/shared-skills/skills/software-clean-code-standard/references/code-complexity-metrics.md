# Code Complexity Metrics

Practical guide to measuring code complexity, choosing the right metrics, setting thresholds, and using metrics to trigger refactoring. Covers cyclomatic complexity, cognitive complexity, Halstead metrics, function length, nesting depth, and tooling.

## Contents

- [Cyclomatic Complexity](#cyclomatic-complexity)
- [Cognitive Complexity](#cognitive-complexity)
- [Halstead Metrics](#halstead-metrics)
- [Function Length and Size Metrics](#function-length-and-size-metrics)
- [Nesting Depth](#nesting-depth)
- [Tooling](#tooling)
- [Refactoring Decision Framework](#refactoring-decision-framework)
- [CC-Rule Mapping](#cc-rule-mapping)
- [Anti-Patterns](#anti-patterns)
- [Cross-References](#cross-references)

---

## Cyclomatic Complexity

### Definition

Cyclomatic complexity (CC) measures the number of linearly independent paths through a function. Each decision point (if, else, for, while, case, catch, &&, ||, ?:) adds 1 to the count.

```text
CC = number_of_decision_points + 1
```

### Calculation Example

```typescript
function processOrder(order: Order): string {
  // CC starts at 1
  if (!order.items.length) {          // +1 → CC = 2
    return 'empty';
  }

  if (order.total > 1000) {           // +1 → CC = 3
    if (order.customer.isPremium) {    // +1 → CC = 4
      return 'premium-high-value';
    }
    return 'high-value';
  }

  for (const item of order.items) {   // +1 → CC = 5
    if (item.quantity > 100) {         // +1 → CC = 6
      return 'bulk';
    }
  }

  return order.customer.isPremium     // +1 (ternary) → CC = 7
    ? 'premium-standard'
    : 'standard';
}
// Final CC = 7
```

### Thresholds

| CC Range | Risk Level | Action |
|----------|-----------|--------|
| 1-5 | Low | Simple, easy to test |
| 6-10 | Moderate | Acceptable; consider simplification if growing |
| 11-20 | High | Refactor: extract methods, use strategy pattern |
| 21-50 | Very High | Must refactor; function is doing too much |
| 50+ | Critical | Emergency refactor; untestable, unmaintainable |

### Per-Language Tools

| Language | Tool | Command |
|----------|------|---------|
| TypeScript/JS | ESLint `complexity` rule | `"complexity": ["warn", 10]` |
| TypeScript/JS | `ts-complexity` | `npx ts-complexity src/` |
| Python | `radon` | `radon cc src/ -a -s` |
| Go | `gocyclo` | `gocyclo -over 10 ./...` |
| Rust | `rust-code-analysis` | `rust-code-analysis -m ./src` |
| Java/Kotlin | SonarQube, Checkstyle | Via CI integration |

### Limitations of Cyclomatic Complexity

```typescript
// CC = 11 but actually easy to read (flat switch)
function getStatusLabel(status: OrderStatus): string {
  switch (status) {
    case 'pending': return 'Pending';
    case 'confirmed': return 'Confirmed';
    case 'processing': return 'Processing';
    case 'shipped': return 'Shipped';
    case 'delivered': return 'Delivered';
    case 'cancelled': return 'Cancelled';
    case 'refunded': return 'Refunded';
    case 'disputed': return 'Disputed';
    case 'returned': return 'Returned';
    case 'archived': return 'Archived';
    default: return 'Unknown';
  }
}
// High CC, but low cognitive load — this is a known limitation
// Cognitive complexity handles this case better
```

---

## Cognitive Complexity

### Why Cognitive Complexity Is Better for Readability

Cognitive complexity (developed by SonarSource) measures how hard code is for a human to understand, not just how many paths exist. Key differences from cyclomatic:

| Feature | Cyclomatic | Cognitive |
|---------|-----------|-----------|
| Flat switch/case | Each case adds 1 | Adds 1 total (not per case) |
| Nested conditions | Same weight as flat | Nesting adds extra penalty |
| Shorthand syntax (`?.`, `??`) | Counts as branch | Reduced weight (less cognitive load) |
| Linear sequence of if/else | Counts each branch | Lower weight for sequential logic |
| Break in control flow | Not counted | Penalized (goto, break, continue) |

### Calculation Rules

```text
1. Increment for each:
   - if, else if, else
   - for, while, do-while
   - catch
   - switch
   - Logical operators in conditions (sequences of && or ||)
   - goto, break to label, continue to label
   - Recursion

2. Nesting penalty: +1 for each level of nesting when incrementing

3. No increment for:
   - Individual case labels in a switch
   - Multiple sequential if/else (no nesting penalty for linear flow)
```

### Calculation Example

```typescript
function processPayment(payment: Payment): Result {
  if (payment.amount <= 0) {                    // +1 (if)
    return Err('invalid amount');
  }

  if (payment.method === 'card') {              // +1 (if)
    if (payment.card.expired) {                  // +2 (if + nesting)
      return Err('expired card');
    }
    if (payment.amount > 10000                   // +2 (if + nesting)
        && !payment.customer.verified) {         // +1 (logical operator)
      return Err('verification required');
    }
    return chargeCard(payment);
  } else if (payment.method === 'bank') {       // +1 (else if)
    return processBankTransfer(payment);
  } else {                                       // +1 (else)
    return Err('unsupported method');
  }
}
// Cognitive complexity = 9
// Cyclomatic complexity would be 7
// The nested conditions make this harder to read than CC suggests
```

### Thresholds

| Cognitive Complexity | Assessment | Action |
|---------------------|------------|--------|
| 0-5 | Excellent | Easy to understand and test |
| 6-10 | Good | Acceptable for most functions |
| 11-15 | Concerning | Consider refactoring |
| 16-25 | High | Should refactor; extract nested logic |
| 25+ | Critical | Must refactor; too complex for reliable review |

### Reducing Cognitive Complexity

```typescript
// Before: cognitive complexity = 12
function handleRequest(req: Request): Response {
  if (req.authenticated) {
    if (req.method === 'GET') {
      if (req.path.startsWith('/admin')) {
        if (req.user.isAdmin) {
          return handleAdminGet(req);
        } else {
          return forbidden();
        }
      } else {
        return handleUserGet(req);
      }
    } else if (req.method === 'POST') {
      if (req.body) {
        return handlePost(req);
      } else {
        return badRequest('Missing body');
      }
    }
  }
  return unauthorized();
}

// After: cognitive complexity = 5 (guard clauses + extraction)
function handleRequest(req: Request): Response {
  if (!req.authenticated) return unauthorized();
  if (req.method === 'GET') return handleGet(req);
  if (req.method === 'POST') return handlePost(req);
  return methodNotAllowed();
}

function handleGet(req: Request): Response {
  if (!req.path.startsWith('/admin')) return handleUserGet(req);
  if (!req.user.isAdmin) return forbidden();
  return handleAdminGet(req);
}

function handlePost(req: Request): Response {
  if (!req.body) return badRequest('Missing body');
  return processPost(req);
}
```

---

## Halstead Metrics

### Overview

Halstead metrics measure code complexity based on operators and operands. Less commonly used than cyclomatic/cognitive, but useful for comparing implementations of the same algorithm.

| Metric | Formula | Measures |
|--------|---------|----------|
| Vocabulary (n) | n1 + n2 | Unique operators + operands |
| Length (N) | N1 + N2 | Total operators + operands |
| Volume (V) | N * log2(n) | Information content |
| Difficulty (D) | (n1/2) * (N2/n2) | Error proneness |
| Effort (E) | D * V | Mental effort to understand |
| Bugs (B) | V / 3000 | Estimated bugs (rough) |

### When Halstead Metrics Are Useful

| Use Case | Why |
|----------|-----|
| Comparing two implementations of same algorithm | Volume shows which is more concise |
| Estimating bug density | Effort correlates with defect probability |
| Benchmarking code generators | Measure output complexity |

**For day-to-day code review, prefer cyclomatic + cognitive complexity.** Halstead is more academic and harder to act on.

---

## Function Length and Size Metrics

### Guidelines by Language

| Language | Recommended Max Lines | Hard Limit | Source |
|----------|----------------------|------------|--------|
| TypeScript/JS | 20-30 lines | 50 lines | Community consensus |
| Python | 20-30 lines | 50 lines | PEP style guides |
| Go | 30-40 lines | 60 lines | Go community (slightly longer due to error handling) |
| Rust | 30-40 lines | 60 lines | Match arms can inflate length |
| Java/Kotlin | 20-30 lines | 50 lines | Clean Code (Robert Martin) |

### Parameter Count

| Count | Assessment | Action |
|-------|------------|--------|
| 0-2 | Ideal | Easy to understand and test |
| 3 | Acceptable | Consider if all params are necessary |
| 4-5 | Concerning | Group into object/struct |
| 6+ | Too many | Must refactor; extract parameter object |

```typescript
// Too many parameters
function createUser(
  name: string, email: string, age: number,
  role: string, department: string, manager: string
): User { /* ... */ }

// Refactored: parameter object
interface CreateUserInput {
  name: string;
  email: string;
  age: number;
  role: string;
  department: string;
  manager: string;
}

function createUser(input: CreateUserInput): User { /* ... */ }
```

### File Length

| Lines | Assessment | Action |
|-------|------------|--------|
| 0-200 | Good | Single responsibility, easy to navigate |
| 200-400 | Acceptable | Check for hidden concerns |
| 400-600 | Concerning | Look for extraction opportunities |
| 600+ | Too large | Must split; multiple responsibilities likely |

---

## Nesting Depth

### Why Nesting Matters

Each level of nesting requires the reader to maintain mental context. Beyond 3 levels, comprehension drops rapidly.

```text
Nesting depth and cognitive load:

Depth 0: // ← Easy
Depth 1:   if (...) {  // ← Fine
Depth 2:     for (...) {  // ← Acceptable
Depth 3:       if (...) {  // ← Reader starts struggling
Depth 4:         if (...) {  // ← Very hard to follow
Depth 5:           // ← Unacceptable
```

### Reducing Nesting

**Technique 1: Early returns (guard clauses)**

```typescript
// Before: depth 4
function process(user: User) {
  if (user) {
    if (user.active) {
      if (user.permissions.includes('write')) {
        return doWork(user);
      }
    }
  }
  return null;
}

// After: depth 1
function process(user: User) {
  if (!user) return null;
  if (!user.active) return null;
  if (!user.permissions.includes('write')) return null;
  return doWork(user);
}
```

**Technique 2: Extract helper functions**

```typescript
// Before: deep nesting in loop
for (const order of orders) {
  if (order.status === 'pending') {
    for (const item of order.items) {
      if (item.inStock) {
        // process...
      }
    }
  }
}

// After: extracted
const pendingOrders = orders.filter(o => o.status === 'pending');
for (const order of pendingOrders) {
  processInStockItems(order.items);
}
```

### Thresholds

| Max Nesting | Assessment |
|-------------|------------|
| 1-2 | Excellent |
| 3 | Acceptable |
| 4 | Must refactor |
| 5+ | Emergency refactor |

---

## Tooling

### ESLint Complexity Rules

```json
{
  "rules": {
    "complexity": ["warn", 10],
    "max-depth": ["warn", 3],
    "max-nested-callbacks": ["warn", 3],
    "max-params": ["warn", 4],
    "max-lines-per-function": ["warn", { "max": 50, "skipBlankLines": true, "skipComments": true }],
    "max-lines": ["warn", { "max": 400, "skipBlankLines": true, "skipComments": true }]
  }
}
```

### SonarQube (Cognitive Complexity)

```text
SonarQube provides:
  - Cognitive complexity per function (default threshold: 15)
  - File-level complexity
  - Complexity distribution charts
  - Trend analysis over time

Integration: CI pipeline → SonarQube → quality gate
Quality gate example: No new code with cognitive complexity > 15
```

### CodeClimate

```text
CodeClimate provides:
  - Maintainability rating (A-F) per file
  - Cognitive complexity
  - Duplication detection
  - Technical debt estimation in time units

Integration: GitHub PR checks → CodeClimate → inline comments
```

### Tool Comparison

| Tool | Metrics | Languages | Cost | Integration |
|------|---------|-----------|------|-------------|
| ESLint (complexity) | Cyclomatic, depth, params, lines | JS/TS | Free | Editor, CI |
| SonarQube | Cognitive, cyclomatic, duplication | 30+ languages | Free (Community) / Paid | CI, PR |
| CodeClimate | Cognitive, duplication, maintainability | 15+ languages | Free (open source) / Paid | GitHub PR |
| Radon | Cyclomatic, Halstead, maintainability | Python | Free | CI |
| gocyclo | Cyclomatic | Go | Free | CI |
| rust-code-analysis | Cyclomatic, cognitive, Halstead | Rust, C++, JS | Free | CI |
| Biome | Limited complexity rules | JS/TS | Free | Editor, CI |

### CI Integration Example

```yaml
# GitHub Actions: fail if complexity exceeds threshold
- name: Check complexity
  run: |
    npx eslint src/ --rule 'complexity: [error, 15]' --no-eslintrc
    if [ $? -ne 0 ]; then
      echo "::error::Functions exceed complexity threshold of 15"
      exit 1
    fi
```

---

## Refactoring Decision Framework

### When to Refactor Based on Metrics

```text
Refactoring trigger decision:

1. Is the function's cyclomatic complexity > 10?
   └─ Yes → Refactor: extract sub-functions, use strategy pattern

2. Is the cognitive complexity > 15?
   └─ Yes → Refactor: reduce nesting, add guard clauses, extract helpers

3. Is the nesting depth > 3?
   └─ Yes → Refactor: early returns, extract inner logic

4. Is the function longer than 50 lines?
   └─ Yes → Refactor: extract cohesive blocks into named functions

5. Does the function have > 4 parameters?
   └─ Yes → Refactor: introduce parameter object or builder

6. Is the file longer than 400 lines?
   └─ Yes → Refactor: split into modules by responsibility
```

### Refactoring Priority Matrix

| Metric Violation | Change Frequency | Priority |
|-----------------|------------------|----------|
| High complexity + frequently changed | Must fix NOW | P0 — Immediate |
| High complexity + rarely changed | Fix opportunistically | P2 — Next sprint |
| Moderate complexity + frequently changed | Fix soon | P1 — This sprint |
| Moderate complexity + rarely changed | Monitor | P3 — Backlog |

### Refactoring Techniques by Metric

| Metric Problem | Technique | CC Rule |
|---------------|-----------|---------|
| High cyclomatic complexity | Extract method, replace conditional with polymorphism | CC-FUNC |
| Deep nesting | Guard clauses, extract helper, invert conditions | CC-FUNC |
| Long function | Extract method, split by responsibility | CC-FUNC, CC-MOD |
| Many parameters | Introduce parameter object, builder pattern | CC-FUNC |
| High cognitive complexity | Flatten conditions, extract named predicates | CC-FUNC |
| Large file | Split into modules, move related functions | CC-MOD |

---

## CC-Rule Mapping

| Metric | CC Rule | Application |
|--------|---------|-------------|
| Cyclomatic complexity | **CC-FUNC** | Functions should be small and single-purpose |
| Cognitive complexity | **CC-FUNC** | Functions should be easy to understand |
| Nesting depth | **CC-FUNC** | Reduce nesting with guard clauses |
| Function length | **CC-FUNC** | Extract when function exceeds 30-50 lines |
| Parameter count | **CC-FUNC** | Group related parameters |
| File length | **CC-MOD** | One responsibility per module |
| Duplication | **CC-REF** | DRY principle; extract shared logic |
| Halstead effort | **CC-FUNC**, **CC-MOD** | High effort indicates refactoring need |

### Using Metrics in Code Review

```text
PR review comment template:

> **CC-FUNC violation**: `processOrder()` has cognitive complexity 22
> (threshold: 15). The nested `if` at line 45 adds +3 due to nesting level.
>
> Suggested fix: Extract the discount calculation into a pure function
> `calculateDiscount()` and use guard clauses for validation.
>
> Reference: [code-complexity-metrics.md] § Reducing Cognitive Complexity
```

---

## Anti-Patterns

| Anti-Pattern | Problem | Fix |
|-------------|---------|-----|
| Metric-driven refactoring only | Refactoring code that works fine just to hit numbers | Metrics inform decisions; judgment matters |
| Ignoring metrics entirely | Complexity creeps up, bugs increase | Set CI quality gates; review periodically |
| One threshold for all code | Utility vs business logic have different needs | Allow higher thresholds for serialization, parsing |
| Measuring but not acting | Dashboards exist but no one looks at them | Tie metrics to PR checks; block on violations |
| Splitting to game metrics | Tiny functions that are harder to follow together | Functions should be cohesive; splitting must improve readability |

---

## Cross-References

- [clean-code-standard.md](clean-code-standard.md) — CC-FUNC, CC-MOD, CC-REF rule definitions
- [functional-programming-patterns.md](functional-programming-patterns.md) — FP patterns that reduce complexity
- [refactoring-operational-checklist.md](refactoring-operational-checklist.md) — Refactoring techniques and triggers
- [design-patterns-operational-checklist.md](design-patterns-operational-checklist.md) — When to use patterns to reduce complexity
- [../../software-code-review/SKILL.md](../../software-code-review/SKILL.md) — Code review practices with complexity references
- [../../qa-refactoring/SKILL.md](../../qa-refactoring/SKILL.md) — Refactoring execution patterns
