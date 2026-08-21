# Code Complexity Metrics

Practical guide to measuring code complexity, choosing the right metrics, setting thresholds, and using metrics to trigger refactoring. Covers cyclomatic complexity, cognitive complexity, Halstead metrics, function length, nesting depth, and tooling.

## Table of Contents

- [Cyclomatic Complexity](#cyclomatic-complexity)
- [Trajectory Metrics for Repeated AI Edits](#trajectory-metrics-for-repeated-ai-edits)
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

The "10" cutoff traces to Thomas McCabe's original research and is explicitly endorsed as a starting point (not an absolute ceiling) by [NIST Special Publication 500-235](https://www.nist.gov/publications/structured-testing-testing-methodology-using-cyclomatic-complexity-metric), which also notes that teams with strong testing/design practices have used limits up to 15 successfully. Treat the table below as a well-evidenced heuristic, not a hard physical law — a flat switch statement (see Limitations below) can have high CC and still be easy to read.

| CC Range | Risk Level | Action |
|----------|-----------|--------|
| 1-5 | Low | Simple, easy to test |
| 6-10 | Moderate | Acceptable; consider simplification if growing |
| 11-20 | High | Refactor: extract methods, use strategy pattern |
| 21-50 | Very High | Must refactor; function is doing too much |
| 50+ | Critical | Emergency refactor; untestable, unmaintainable |

### Per-Language Tools

| Language | Tooling | Notes |
|----------|---------|-------|
| TypeScript/JS | ESLint v9 flat config, Biome, Oxlint | Tool choice depends on rule coverage, speed, and formatter consolidation needs |
| Python | Ruff, `ty`, `radon` | Ruff for lint/format, `ty`/mypy for typing, `radon` for explicit complexity reports |
| Go | golangci-lint, Staticcheck, `gocyclo` | Use golangci-lint as aggregator; add `gocyclo` when explicit complexity budgets matter |
| Rust | Clippy, `rust-code-analysis` | Clippy for idioms/hygiene; `rust-code-analysis` for explicit metrics reports |
| Java/Kotlin | SonarQube, Detekt, Checkstyle | SonarQube remains the common source for cognitive complexity gates |

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

## Trajectory Metrics for Repeated AI Edits

Use these research-derived signals when the same codebase is repeatedly extended by a coding agent. They complement ordinary per-snapshot metrics: mean CC can dilute a few increasingly overloaded functions, while maximum CC shows only the worst callable and not how much of the codebase's complexity has concentrated there.

### Structural Erosion

[SlopCodeBench v1](https://arxiv.org/abs/2603.24755v1) defines a callable's complexity mass as:

```text
mass(f) = CC(f) * sqrt(SLOC(f))

erosion = sum(mass(f) where CC(f) > 10) / sum(mass(f) for all callables)
```

The square root keeps size relevant without allowing raw line count to dominate cyclomatic complexity. Track erosion at every checkpoint and inspect its direction or slope: a rise means a growing share of decision-path mass is accumulating in already-complex functions, even if mean CC looks stable.

The paper used `CC > 10` for its Python experiments. Treat that cutoff and any slope threshold as an advisory research lens, not a universal quality gate or proof of incorrectness. Calibrate language tooling, generated code, parsers, and repository conventions before operational use. This signal applies the existing **CC-FUN-01** and **CC-FLOW-01** intents; it creates no new rule ID.

### Verbosity

For a local repository and language, define a reviewed set of redundant-code patterns and a clone detector, then calculate:

```text
verbosity = count(flagged-pattern lines UNION clone lines) / LOC
```

Count each line once when both detectors flag it. The pattern set must be locally defined and versioned: SlopCodeBench used its own Python-oriented rules, which are not a universal catalog. Track the metric across checkpoints to detect redundant scaffolding or duplication accumulating faster than useful behavior. Interpret it through **CC-FUN-05** (duplication) and, when redundant code obscures cohesion, **CC-FUN-01**.

Neither erosion nor verbosity predicts correctness by itself. Pair both with behavioral and regression tests, review evidence, and change context. Their value is longitudinal: they reveal deterioration that a green test suite or a single end-state snapshot can miss.

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

The 15 cutoff is [SonarSource's built-in default](https://www.sonarsource.com/resources/cognitive-complexity/) for its cognitive-complexity rule, not an independent empirical finding — teams commonly tune this per-project. Use it as a sensible out-of-the-box default rather than a claim that 16 is objectively "too complex."

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

There is no strong independent empirical study establishing an optimal function-length number — the figures below are community convention and tool defaults (ESLint's `max-lines-per-function`, popular style guides), not a measured productivity or defect-rate finding. Treat them as a default lint setting to tune, not proof that a 51-line function is defective. John Ousterhout's *A Philosophy of Software Design* explicitly argues against optimizing for short functions as a goal in itself: splitting a cohesive piece of logic purely to hit a line count can increase the number of "shallow" interfaces a reader must hold in mind, trading one kind of complexity for another. Prefer CC-FUN-01 ("one dominant responsibility") as the actual test; use the line count as a cheap proxy that flags candidates for review, not a rule to satisfy mechanically.

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

**Note**: split "complexity metrics" from "general code-quality tooling" in recommendations. Many modern tools are excellent general linters/formatters, but only some expose explicit cyclomatic/cognitive complexity metrics.

### JavaScript / TypeScript

#### ESLint v9 Flat Config Complexity Rules

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

ESLint is still the most flexible option when you need mature custom rule ecosystems or framework-specific plugins.

#### Biome / Oxlint

```text
Biome and Oxlint are useful when speed and simplified setup matter.

- Biome can consolidate formatting + linting, but complexity-specific rule coverage is narrower than ESLint/SonarQube.
- Oxlint is well-suited for fast CI feedback and broad built-in rule coverage.
- Use SonarQube or a dedicated metrics tool if you need cognitive complexity gates, trend charts, or portfolio-level governance.
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
| ESLint v9 | Cyclomatic, depth, params, lines | JS/TS | Free | Editor, CI |
| Biome | Limited complexity-related rules; strong lint/format DX | JS/TS | Free | Editor, CI |
| Oxlint | Broad lint coverage; fast CI feedback | JS/TS | Free | Editor, CI |
| SonarQube | Cognitive, cyclomatic, duplication | 30+ languages | Free (Community) / Paid | CI, PR |
| Ruff | Lint + format; not a dedicated complexity dashboard | Python | Free | Editor, CI |
| `ty` / mypy | Type-system pressure that often reduces hidden complexity | Python | Free | Editor, CI |
| Radon | Cyclomatic, Halstead, maintainability | Python | Free | CI |
| golangci-lint + Staticcheck | Hygiene and bug-risk aggregation; pair with `gocyclo` for explicit complexity limits | Go | Free | CI |
| Clippy | Idioms and bug-risk hygiene; pair with metrics tooling for explicit complexity reporting | Rust | Free | Editor, CI |
| rust-code-analysis | Cyclomatic, cognitive, Halstead | Rust, C++, JS | Free | CI |

### CI Integration Example

```yaml
# GitHub Actions: fail if complexity exceeds threshold
- name: Check complexity
  run: |
    npx eslint src/ --rule 'complexity: [error, 15]'
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
| High cyclomatic complexity | Extract method, replace conditional with polymorphism | CC-FUN-01, CC-FLOW-01 |
| Deep nesting | Guard clauses, extract helper, invert conditions | CC-FLOW-01 |
| Long function | Extract method, split by responsibility | CC-FUN-01, CC-FUN-04 |
| Many parameters | Introduce parameter object, builder pattern | CC-FUN-03 |
| High cognitive complexity | Flatten conditions, extract named predicates | CC-FLOW-01, CC-FLOW-02 |
| Large file | Split into modules, move related functions | CC-FUN-01, CC-TYP-03 |

---

## CC-Rule Mapping

| Metric | CC Rule | Application |
|--------|---------|-------------|
| Cyclomatic complexity | **CC-FUN-01**, **CC-FLOW-01** | Functions should be cohesive and control flow should stay shallow |
| Cognitive complexity | **CC-FUN-01**, **CC-FLOW-01**, **CC-FLOW-02** | Functions should be easy to understand |
| Nesting depth | **CC-FLOW-01** | Reduce nesting with guard clauses |
| Function length | **CC-FUN-01**, **CC-FUN-04** | Extract when function exceeds 30-50 lines |
| Parameter count | **CC-FUN-03** | Group related parameters |
| File length | **CC-FUN-01**, **CC-TYP-03** | Keep module boundaries clear and responsibilities cohesive |
| Duplication | **CC-FUN-05** | Extract shared logic to avoid divergence |
| Structural erosion trajectory | **CC-FUN-01**, **CC-FLOW-01** | Detect complexity mass concentrating in already-complex functions across repeated edits |
| Verbosity trajectory | **CC-FUN-05**, **CC-FUN-01** | Detect locally defined redundant patterns and clone lines accumulating across repeated edits |
| Halstead effort | **CC-FUN-01**, **CC-TYP-03** | High effort indicates refactoring need |

### Using Metrics in Code Review

```text
PR review comment template:

> **CC-FLOW-01 violation**: `processOrder()` has cognitive complexity 22
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
| Treating trajectory signals as correctness gates | Erosion and verbosity can rise or fall independently of behavior | Pair them with tests and review; calibrate thresholds locally |

---

## Cross-References

- [clean-code-standard.md](clean-code-standard.md) — CC-FUN, CC-FLOW, CC-TYP rule definitions
- [functional-programming-patterns.md](functional-programming-patterns.md) — FP patterns that reduce complexity
- [refactoring-operational-checklist.md](refactoring-operational-checklist.md) — Refactoring techniques and triggers
- [design-patterns-operational-checklist.md](design-patterns-operational-checklist.md) — When to use patterns to reduce complexity
- [../../software-code-review/SKILL.md](../../software-code-review/SKILL.md) — Code review practices with complexity references
- [../../qa-refactoring/SKILL.md](../../qa-refactoring/SKILL.md) — Refactoring execution patterns
