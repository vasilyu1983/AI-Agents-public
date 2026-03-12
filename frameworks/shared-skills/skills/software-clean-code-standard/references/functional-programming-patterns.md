# Functional Programming Patterns for Clean Code

Practical guide to functional programming patterns that improve code quality, testability, and error handling. Covers Result/Either types, pipe/compose, immutability, pure functions, algebraic data types, and railway-oriented programming. Maps patterns to CC-* clean code rules.

## Contents

- [Result/Either Types](#resulteither-types)
- [Pipe and Compose](#pipe-and-compose)
- [Immutability Disciplines](#immutability-disciplines)
- [Pure Functions and Referential Transparency](#pure-functions-and-referential-transparency)
- [Algebraic Data Types and Pattern Matching](#algebraic-data-types-and-pattern-matching)
- [Railway-Oriented Programming](#railway-oriented-programming)
- [When FP Hurts Readability](#when-fp-hurts-readability)
- [CC-Rule Mapping](#cc-rule-mapping)
- [Cross-References](#cross-references)

---

## Result/Either Types

### The Problem with Exceptions

```typescript
// Exception-based: control flow is invisible
function getUser(id: string): User {
  const user = db.findUser(id);
  if (!user) throw new NotFoundError('User not found');  // invisible exit
  if (!user.active) throw new ForbiddenError('User inactive');  // invisible exit
  return user;
}

// Caller has no idea what can go wrong without reading the implementation
try {
  const user = getUser(id);
  // use user...
} catch (e) {
  // What errors are possible here? 🤷
}
```

### TypeScript Result Type

```typescript
// Make errors explicit in the type signature
type Result<T, E = Error> =
  | { ok: true; value: T }
  | { ok: false; error: E };

// Constructor helpers
function Ok<T>(value: T): Result<T, never> {
  return { ok: true, value };
}

function Err<E>(error: E): Result<never, E> {
  return { ok: false, error };
}

// Usage: errors are visible in the return type
type UserError = 'NOT_FOUND' | 'INACTIVE' | 'SUSPENDED';

function getUser(id: string): Result<User, UserError> {
  const user = db.findUser(id);
  if (!user) return Err('NOT_FOUND');
  if (!user.active) return Err('INACTIVE');
  if (user.suspended) return Err('SUSPENDED');
  return Ok(user);
}

// Caller MUST handle the error — the type system enforces it
const result = getUser('user-123');
if (!result.ok) {
  switch (result.error) {
    case 'NOT_FOUND': return res.status(404).json({ error: 'User not found' });
    case 'INACTIVE': return res.status(403).json({ error: 'User inactive' });
    case 'SUSPENDED': return res.status(403).json({ error: 'Account suspended' });
  }
}
const user = result.value;  // TypeScript knows this is User
```

### Go Error Handling (Idiomatic Result)

```go
// Go's multiple return values are a built-in Result type
type UserError string

const (
    ErrNotFound  UserError = "not_found"
    ErrInactive  UserError = "inactive"
    ErrSuspended UserError = "suspended"
)

func (e UserError) Error() string { return string(e) }

func GetUser(id string) (*User, error) {
    user, err := db.FindUser(id)
    if err != nil {
        return nil, fmt.Errorf("find user %s: %w", id, err)
    }
    if user == nil {
        return nil, ErrNotFound
    }
    if !user.Active {
        return nil, ErrInactive
    }
    return user, nil
}

// Caller checks error explicitly
user, err := GetUser("user-123")
if err != nil {
    if errors.Is(err, ErrNotFound) {
        // handle not found
    }
    return fmt.Errorf("get user: %w", err)
}
```

### Rust Result Type (Native)

```rust
use thiserror::Error;

#[derive(Error, Debug)]
enum UserError {
    #[error("user not found")]
    NotFound,
    #[error("user inactive")]
    Inactive,
    #[error("database error: {0}")]
    Database(#[from] sqlx::Error),
}

fn get_user(id: &str) -> Result<User, UserError> {
    let user = db::find_user(id)
        .map_err(UserError::Database)?;  // ? operator for early return

    match user {
        None => Err(UserError::NotFound),
        Some(u) if !u.active => Err(UserError::Inactive),
        Some(u) => Ok(u),
    }
}

// Caller MUST handle (compiler-enforced)
match get_user("user-123") {
    Ok(user) => println!("Found: {}", user.name),
    Err(UserError::NotFound) => println!("Not found"),
    Err(UserError::Inactive) => println!("Inactive"),
    Err(UserError::Database(e)) => eprintln!("DB error: {}", e),
}
```

---

## Pipe and Compose

### Pipeline Pattern for Data Transformation

```typescript
// Pipe: left-to-right function composition
function pipe<T>(...fns: Array<(arg: T) => T>): (arg: T) => T {
  return (arg: T) => fns.reduce((result, fn) => fn(result), arg);
}

// Transform user data through a pipeline
const sanitizeUser = pipe(
  trimWhitespace,
  normalizeEmail,
  validateAge,
  assignDefaultRole,
);

const cleanUser = sanitizeUser(rawInput);
```

```typescript
// Async pipe for operations that return Promises
async function asyncPipe<T>(
  input: T,
  ...fns: Array<(arg: T) => T | Promise<T>>
): Promise<T> {
  let result = input;
  for (const fn of fns) {
    result = await fn(result);
  }
  return result;
}

// Example: order processing pipeline
const processedOrder = await asyncPipe(
  rawOrder,
  validateOrderInput,
  enrichWithCustomerData,
  calculateTaxes,
  applyDiscounts,
  persistOrder,
);
```

### Compose: Right-to-Left (Mathematical Convention)

```typescript
// Compose: right-to-left (f . g = f(g(x)))
function compose<T>(...fns: Array<(arg: T) => T>): (arg: T) => T {
  return (arg: T) => fns.reduceRight((result, fn) => fn(result), arg);
}

// Read bottom-up: first normalize, then validate, then format
const prepareOutput = compose(
  formatResponse,     // 3. Format for API response
  validateOutput,     // 2. Ensure output is valid
  normalizeData,      // 1. Normalize raw data
);
```

### When to Use Pipe vs Compose

| Use Pipe | Use Compose |
|----------|-------------|
| Data processing pipelines | Mathematical function composition |
| Step-by-step transformations | Middleware chains |
| When reading order = execution order | When aligning with function notation |
| Most business logic | Decorator patterns |

**Recommendation:** Prefer pipe (left-to-right) for most code. It reads more naturally for non-mathematicians.

---

## Immutability Disciplines

### TypeScript Immutability

```typescript
// 1. readonly properties
interface User {
  readonly id: string;
  readonly email: string;
  readonly name: string;
}

// 2. Readonly utility type (deep immutable)
type ImmutableUser = Readonly<User>;

// 3. as const for literal types
const CONFIG = {
  maxRetries: 3,
  timeout: 5000,
  features: ['auth', 'logging'],
} as const;
// CONFIG.maxRetries = 5;  // Error: Cannot assign to 'maxRetries'
// CONFIG.features.push('new');  // Error: Property 'push' does not exist

// 4. Object.freeze (runtime enforcement)
const frozenConfig = Object.freeze({
  maxRetries: 3,
  timeout: 5000,
});
// frozenConfig.maxRetries = 5;  // Silently fails (or throws in strict mode)

// 5. Immutable updates (spread operator)
function updateUser(user: User, updates: Partial<Omit<User, 'id'>>): User {
  return { ...user, ...updates };  // New object, original unchanged
}

const original = { id: '1', email: 'a@b.com', name: 'Alice' };
const updated = updateUser(original, { name: 'Bob' });
// original.name === 'Alice' (unchanged)
// updated.name === 'Bob' (new object)
```

### Immutable Collections

```typescript
// For complex state, use immutable update patterns
// Simple: spread operator
const addItem = (items: readonly string[], item: string): readonly string[] =>
  [...items, item];

const removeItem = (items: readonly string[], index: number): readonly string[] =>
  [...items.slice(0, index), ...items.slice(index + 1)];

const updateItem = (items: readonly string[], index: number, value: string): readonly string[] =>
  items.map((item, i) => i === index ? value : item);

// For deep nested updates, consider libraries:
// - Immer (produces immutable state with mutable API)
// - Immutable.js (persistent data structures)
```

### Go Immutability

```go
// Go approach: unexported fields + methods that return new values
type Money struct {
    amount   int64  // unexported = immutable from outside
    currency string
}

func NewMoney(amount int64, currency string) Money {
    return Money{amount: amount, currency: currency}
}

func (m Money) Add(other Money) (Money, error) {
    if m.currency != other.currency {
        return Money{}, errors.New("currency mismatch")
    }
    return Money{amount: m.amount + other.amount, currency: m.currency}, nil
}

// m is unchanged after Add — new Money returned
```

### When Mutability Is Acceptable

| Mutable OK | Immutable Preferred |
|-----------|-------------------|
| Loop accumulators (local scope) | Shared state across goroutines/async |
| Performance-critical inner loops | Domain objects, value objects |
| Builder pattern during construction | Configuration after initialization |
| Stream/buffer processing | Function arguments and return values |

---

## Pure Functions and Referential Transparency

### What Makes a Function Pure

```typescript
// Pure: same input → same output, no side effects
function calculateTotal(items: readonly Item[]): number {
  return items.reduce((sum, item) => sum + item.price * item.quantity, 0);
}

// Impure: depends on external state
let taxRate = 0.08;
function calculateTotalWithTax(items: Item[]): number {
  return items.reduce((sum, item) => sum + item.price * item.quantity, 0) * (1 + taxRate);
  //                                                                         ↑ external state
}

// Fix: make dependency explicit
function calculateTotalWithTax(items: readonly Item[], taxRate: number): number {
  return items.reduce((sum, item) => sum + item.price * item.quantity, 0) * (1 + taxRate);
}
```

### Isolating Side Effects

```text
Architecture principle: Push side effects to the boundary

  ┌─────────────────────────────────────┐
  │          Pure Business Logic        │  ← No I/O, no DB, no network
  │  (calculateTotal, validateOrder,    │     Testable without mocks
  │   applyDiscount, formatInvoice)     │
  └──────────────┬──────────────────────┘
                 │
  ┌──────────────▼──────────────────────┐
  │        Impure Shell / Boundary      │  ← Reads DB, calls APIs
  │  (fetchOrder, saveOrder, sendEmail) │     Orchestrates pure functions
  └─────────────────────────────────────┘
```

```typescript
// Pure: business logic (easily testable)
function applyDiscount(order: Order, discount: Discount): Order {
  const discountedItems = order.items.map(item => ({
    ...item,
    price: item.price * (1 - discount.percentage),
  }));
  return { ...order, items: discountedItems };
}

// Impure: orchestration (tested with integration tests)
async function processOrder(orderId: string): Promise<void> {
  const order = await db.getOrder(orderId);           // side effect
  const discount = await discountService.get(order);   // side effect
  const discounted = applyDiscount(order, discount);   // pure
  await db.saveOrder(discounted);                      // side effect
  await emailService.sendConfirmation(discounted);     // side effect
}
```

### Testing Pure Functions

```typescript
// Pure functions need no mocks, no setup, no teardown
describe('applyDiscount', () => {
  it('applies percentage discount to all items', () => {
    const order: Order = {
      items: [
        { name: 'Widget', price: 100, quantity: 2 },
        { name: 'Gadget', price: 50, quantity: 1 },
      ],
    };
    const discount: Discount = { percentage: 0.1 };

    const result = applyDiscount(order, discount);

    expect(result.items[0].price).toBe(90);
    expect(result.items[1].price).toBe(45);
    expect(order.items[0].price).toBe(100);  // Original unchanged
  });
});
```

---

## Algebraic Data Types and Pattern Matching

### Discriminated Unions (TypeScript)

```typescript
// Model domain states as a union of tagged types
type PaymentState =
  | { status: 'pending'; orderId: string }
  | { status: 'processing'; orderId: string; transactionId: string }
  | { status: 'completed'; orderId: string; transactionId: string; amount: number }
  | { status: 'failed'; orderId: string; error: string; retryable: boolean }
  | { status: 'refunded'; orderId: string; refundId: string };

// Exhaustive pattern matching
function getPaymentMessage(payment: PaymentState): string {
  switch (payment.status) {
    case 'pending':
      return `Order ${payment.orderId} awaiting payment`;
    case 'processing':
      return `Processing transaction ${payment.transactionId}`;
    case 'completed':
      return `Payment of $${payment.amount} completed`;
    case 'failed':
      return payment.retryable
        ? `Payment failed: ${payment.error}. Retrying...`
        : `Payment failed permanently: ${payment.error}`;
    case 'refunded':
      return `Refund ${payment.refundId} issued`;
    // TypeScript will error if we miss a case (with --strict and never check)
  }
}

// Exhaustiveness check helper
function assertNever(x: never): never {
  throw new Error(`Unexpected value: ${JSON.stringify(x)}`);
}
```

### Rust Enums (True ADTs)

```rust
enum Shape {
    Circle { radius: f64 },
    Rectangle { width: f64, height: f64 },
    Triangle { base: f64, height: f64 },
}

fn area(shape: &Shape) -> f64 {
    match shape {
        Shape::Circle { radius } => std::f64::consts::PI * radius * radius,
        Shape::Rectangle { width, height } => width * height,
        Shape::Triangle { base, height } => 0.5 * base * height,
        // Compiler error if a variant is missing
    }
}

// Option and Result are ADTs
fn find_user(id: &str) -> Option<User> {
    // Returns Some(user) or None — no null, no exceptions
    users.iter().find(|u| u.id == id).cloned()
}
```

### When to Use ADTs

| Pattern | Use When | Example |
|---------|----------|---------|
| Discriminated union | Fixed set of states with different data | Payment status, request state |
| Option/Maybe | Value may or may not exist | User lookup, config value |
| Result/Either | Operation can succeed or fail with typed error | API call, validation |
| Enum with data | Variants carry different payloads | AST nodes, protocol messages |

---

## Railway-Oriented Programming

### Concept

Chain operations that can fail, short-circuiting on the first error.

```text
Happy path (Ok track):
  Input → [Validate] → [Enrich] → [Save] → [Notify] → Output

Error path (Err track):
  Input → [Validate] ─X→ Error
          [Enrich]  ─X→ Error
          [Save]    ─X→ Error
          [Notify]  ─X→ Error

Each step either continues on the Ok track or diverts to the Error track.
```

### TypeScript Implementation

```typescript
type Result<T, E> = { ok: true; value: T } | { ok: false; error: E };

// Chain Result-returning functions
function chain<T, U, E>(
  result: Result<T, E>,
  fn: (value: T) => Result<U, E>,
): Result<U, E> {
  if (!result.ok) return result;
  return fn(result.value);
}

// Map over the success value
function map<T, U, E>(
  result: Result<T, E>,
  fn: (value: T) => U,
): Result<U, E> {
  if (!result.ok) return result;
  return Ok(fn(result.value));
}

// Railway-oriented order processing
type OrderError =
  | { code: 'INVALID_INPUT'; message: string }
  | { code: 'INSUFFICIENT_STOCK'; item: string }
  | { code: 'PAYMENT_FAILED'; reason: string }
  | { code: 'DB_ERROR'; message: string };

function processOrder(input: RawOrderInput): Result<Order, OrderError> {
  let result: Result<any, OrderError> = validateInput(input);
  result = chain(result, checkInventory);
  result = chain(result, calculatePricing);
  result = chain(result, processPayment);
  result = chain(result, saveOrder);
  return result;
}

// Each function returns Result — chain short-circuits on first Err
function validateInput(input: RawOrderInput): Result<ValidatedOrder, OrderError> {
  if (!input.items?.length) {
    return Err({ code: 'INVALID_INPUT', message: 'No items in order' });
  }
  return Ok({ items: input.items, customerId: input.customerId });
}
```

### Async Railway

```typescript
async function chainAsync<T, U, E>(
  result: Result<T, E>,
  fn: (value: T) => Promise<Result<U, E>>,
): Promise<Result<U, E>> {
  if (!result.ok) return result;
  return fn(result.value);
}

async function processOrderAsync(input: RawOrderInput): Promise<Result<Order, OrderError>> {
  let result: Result<any, OrderError> = validateInput(input);
  result = await chainAsync(result, checkInventoryAsync);
  result = await chainAsync(result, processPaymentAsync);
  result = await chainAsync(result, saveOrderAsync);
  return result;
}
```

---

## When FP Hurts Readability

### Over-Abstraction Pitfalls

| Anti-Pattern | Problem | Fix |
|-------------|---------|-----|
| Pointfree everything | Unreadable: `compose(map(prop('name')), filter(propEq('active', true)))` | Use named intermediate variables |
| Monad transformers | Deep nesting: `TaskEither<ReaderT<...>>` | Keep monad stack shallow (<3 levels) |
| Category theory naming | `bifunctor`, `applicative` — obscure to most teams | Use domain names: `mapBoth`, `applyAll` |
| Currying everything | `f(a)(b)(c)` less clear than `f(a, b, c)` | Curry only when partial application is useful |
| FP-maximalism | Forcing FP where imperative is clearer | Loops are fine for simple iteration |

### When to Use FP vs Imperative

| FP Patterns | Imperative/OOP |
|-------------|---------------|
| Data transformation pipelines | Complex stateful workflows |
| Error handling (Result types) | Simple try/catch at boundaries |
| Immutable domain objects | Performance-critical mutation |
| Pure business logic | I/O orchestration |
| Small, composable functions | Complex class hierarchies with identity |

### Readability Test

Before using an FP pattern, ask:

1. Can a mid-level developer on the team understand this in 30 seconds?
2. Does the FP version communicate intent better than the imperative version?
3. Is the abstraction reused in at least 3 places?

If any answer is "no," use the simpler version.

---

## CC-Rule Mapping

| FP Pattern | CC Rule | How It Applies |
|-----------|---------|---------------|
| Result/Either types | **CC-ERR** (Error Handling) | Make errors explicit in signatures; no hidden throws |
| Pure functions | **CC-FUNC** (Function Design) | Small, single-purpose, testable without mocks |
| Immutability | **CC-FUNC**, **CC-MOD** | Reduce shared mutable state; safer concurrency |
| Pipe/Compose | **CC-FUNC** | Composable functions with clear data flow |
| Discriminated unions | **CC-TYPE** (Type Safety) | Model domain states precisely; exhaustive handling |
| Railway programming | **CC-ERR** | Structured error propagation; no silent failures |
| Side effect isolation | **CC-MOD** (Module Design) | Pure core, impure shell; testable architecture |

### Applying FP Incrementally

```text
Adoption path (least to most FP):

1. Start with Result types for error handling (CC-ERR)
   → Biggest readability and safety win for lowest cost

2. Add immutability for domain objects (CC-FUNC, CC-MOD)
   → Prevents mutation bugs in shared state

3. Use pipe/compose for data transformation (CC-FUNC)
   → Cleaner than nested function calls

4. Add discriminated unions for state modeling (CC-TYPE)
   → Compiler-enforced exhaustive handling

5. Railway-oriented programming for complex flows (CC-ERR)
   → Only when multiple sequential fallible operations
```

---

## Cross-References

- [clean-code-standard.md](clean-code-standard.md) — CC-* rule definitions (CC-ERR, CC-FUNC, CC-MOD, CC-TYPE)
- [error-handling.md](error-handling.md) — Effect Result types, correlation IDs
- [code-complexity-metrics.md](code-complexity-metrics.md) — Measuring when FP reduces complexity
- [design-patterns-operational-checklist.md](design-patterns-operational-checklist.md) — Strategy, Command, and other patterns with FP equivalents
- [../../software-backend/references/nodejs-best-practices.md](../../software-backend/references/nodejs-best-practices.md) — Async patterns, error handling in Node.js
- [../../software-backend/references/rust-best-practices.md](../../software-backend/references/rust-best-practices.md) — Rust's native Result/Option types
- [../../software-backend/references/go-best-practices.md](../../software-backend/references/go-best-practices.md) — Go's error handling patterns
