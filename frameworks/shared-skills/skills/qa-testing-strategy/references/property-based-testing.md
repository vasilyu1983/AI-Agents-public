# Property-Based Testing

## Table of Contents

- [Concept](#concept)
- [When to Use](#when-to-use)
- [Tool Landscape](#tool-landscape)
- [fast-check (JavaScript / TypeScript)](#fast-check-javascript--typescript)
- [Hypothesis (Python)](#hypothesis-python)
- [JQwik / QuickTheories (Java)](#jqwik--quicktheories-java)
- [Generating Domain-Valid Inputs](#generating-domain-valid-inputs)
- [CI Integration](#ci-integration)
- [Property-Based Testing for AI-Generated Code](#property-based-testing-for-ai-generated-code)
- [Anti-Patterns](#anti-patterns)
- [Related Resources](#related-resources)

Property-based testing (PBT) replaces hand-crafted example inputs with a generator that produces many random inputs satisfying declared constraints. When a failure is found, the framework shrinks the failing case to the minimal reproducible counterexample. PBT is a high-signal complement to example-based tests: it exercises edge cases and boundary conditions that humans routinely miss.

---

## Concept

```text
Example-based test:
  Given price = 9.99, quantity = 3
  Then total = 29.97

Property-based test:
  For all price in [0.01, 999.99] and quantity in [1, 100]
  total == price * quantity (within floating-point tolerance)
  AND total >= price
  AND total >= quantity
```

The generator runs hundreds of inputs automatically. On failure, shrinking produces the smallest failing case.

---

## When to Use

| Scenario | Benefit |
|----------|---------|
| Pure functions with numeric or string inputs | Discover boundary, overflow, and encoding edge cases |
| Serialization / deserialization round-trips | Verify `deserialize(serialize(x)) == x` for all valid `x` |
| State machine / workflow invariants | Verify invariants hold across all reachable states |
| API input validation | Discover parser edge cases that hand-crafted fuzz inputs miss |
| Algebraic properties (commutativity, associativity, idempotence) | Encode mathematical contracts as tests |
| AI-generated code review | Blind-spot detection: PBT finds the edge cases LLMs routinely skip |

PBT is **not** a replacement for example-based tests. Keep example tests for readability and regression coverage; add PBT for properties that should hold universally.

---

## Tool Landscape

| Tool | Languages | Notes |
|------|-----------|-------|
| **fast-check** | JavaScript, TypeScript | Most complete JS PBT library; excellent shrinking; Vitest and Jest compatible |
| **Hypothesis** | Python | Mature; integrates with pytest; stateful testing via `RuleBasedStateMachine` |
| **jqwik** | Java | JUnit 5-native; richer than QuickCheck ports; property-level annotations |
| **QuickTheories** | Java | Simpler than jqwik; good for teams already on JUnit 5 |
| **PropEr / Eqwalizer** | Erlang/Elixir | Strong for protocol and state-machine testing |
| **FsCheck** | F# / C# | Well-integrated with xUnit and NUnit |

---

## fast-check (JavaScript / TypeScript)

```bash
npm install --save-dev fast-check
```

### Round-trip property

```typescript
import fc from 'fast-check';

test('JSON round-trip: all serializable values survive serialize/deserialize', () => {
  fc.assert(
    fc.property(fc.jsonValue(), (value) => {
      expect(JSON.parse(JSON.stringify(value))).toEqual(value);
    })
  );
});
```

### Numeric invariant

```typescript
test('total is always >= unit price and >= quantity', () => {
  fc.assert(
    fc.property(
      fc.float({ min: 0.01, max: 999.99, noNaN: true }),
      fc.integer({ min: 1, max: 100 }),
      (price, quantity) => {
        const total = computeTotal(price, quantity);
        expect(total).toBeGreaterThanOrEqual(price);
        expect(total).toBeGreaterThanOrEqual(quantity);
      }
    )
  );
});
```

### State machine property (user session)

```typescript
test('user session: authenticated state never reached from initial without valid login', () => {
  fc.assert(
    fc.property(
      fc.array(fc.oneof(
        fc.record({ type: fc.constant('login'), password: fc.string() }),
        fc.record({ type: fc.constant('logout') }),
        fc.record({ type: fc.constant('access'), resource: fc.string() }),
      )),
      (commands) => {
        const session = new UserSession();
        for (const cmd of commands) {
          session.apply(cmd);
          if (session.isAuthenticated()) {
            // Authenticated state only reachable via valid login
            expect(session.hasValidLogin()).toBe(true);
          }
        }
      }
    )
  );
});
```

### Vitest configuration

```typescript
// vitest.config.ts — no special config needed; fast-check works in any test runner
// Increase default runs for nightly / pre-release jobs:
fc.configureGlobal({ numRuns: 1000 });  // default 100; increase for thorough sweeps
```

---

## Hypothesis (Python)

```bash
pip install hypothesis pytest
```

### Basic property

```python
from hypothesis import given, settings
from hypothesis import strategies as st

@given(price=st.floats(min_value=0.01, max_value=999.99, allow_nan=False),
       quantity=st.integers(min_value=1, max_value=100))
def test_total_non_negative(price: float, quantity: int) -> None:
    total = compute_total(price, quantity)
    assert total >= 0
    assert total >= price
```

### Stateful testing (rule-based)

```python
from hypothesis.stateful import RuleBasedStateMachine, rule, initialize

class CartMachine(RuleBasedStateMachine):
    @initialize()
    def setup(self) -> None:
        self.cart = Cart()

    @rule(item=st.from_regex(r'[A-Z]{3}-\d{4}'))
    def add_item(self, item: str) -> None:
        self.cart.add(item)
        assert item in self.cart.items()

    @rule()
    def checkout(self) -> None:
        count = len(self.cart.items())
        self.cart.checkout()
        assert self.cart.total() >= 0

TestCart = CartMachine.TestCase
```

### CI settings for Hypothesis

```python
# conftest.py
from hypothesis import settings, HealthCheck

settings.register_profile("ci", max_examples=200, suppress_health_check=[HealthCheck.too_slow])
settings.register_profile("nightly", max_examples=2000)
settings.load_profile("ci")  # override with HY_PROFILE=nightly for thorough runs
```

---

## JQwik / QuickTheories (Java)

```java
// jqwik
@Property
void totalAlwaysGtePrice(@ForAll @Positive @FloatRange(max = 999.99f) float price,
                          @ForAll @IntRange(min = 1, max = 100) int quantity) {
    float total = computeTotal(price, quantity);
    Assertions.assertThat(total).isGreaterThanOrEqualTo(price);
}
```

---

## Generating Domain-Valid Inputs

Use constrained generators to avoid "unrealistic data" failures that waste debugging time.

```typescript
// Constrained: only valid email-like strings
const emailArb = fc.emailAddress();

// Custom: product SKU matching format ABC-1234
const skuArb = fc.stringMatching(/^[A-Z]{3}-\d{4}$/);

// Composing domain objects
const orderArb = fc.record({
  sku: skuArb,
  quantity: fc.integer({ min: 1, max: 50 }),
  price: fc.float({ min: 0.01, max: 999.99, noNaN: true }),
});
```

Avoid overly permissive generators (e.g., `fc.string()` for email fields). They produce inputs your code will never receive in practice, wasting test cycles on irrelevant failures.

---

## CI Integration

PBT runs are deterministic when a failing seed is logged. fast-check and Hypothesis both print the seed on failure; re-run with that seed to reproduce.

**Default CI strategy**: keep `numRuns` / `max_examples` low (100-200) in the standard PR gate. Run high-count sweeps (1000+) nightly or pre-release.

```yaml
# GitHub Actions: nightly deep PBT run
- name: Property-based tests (thorough)
  env:
    HY_PROFILE: nightly         # Hypothesis: 2000 examples
    FC_NUM_RUNS: "1000"         # fast-check: read in conftest or test setup
  run: npx vitest run --reporter=verbose tests/property/
```

**Reproducing failures**: fast-check prints the failing seed in the error message. Pass it explicitly:

```typescript
fc.assert(fc.property(...), { seed: 1234567890, path: '0' });
```

---

## Property-Based Testing for AI-Generated Code

AI-generated code tends to pass example-based tests while failing on edge cases the prompt never specified. Common failure modes:

- Off-by-one errors in bounds checks
- Missing null/undefined guards
- Incorrect handling of empty collections
- Floating-point edge cases (NaN, Infinity, negative zero)
- String encoding edge cases (Unicode, empty, whitespace-only)

PBT is the highest-ROI complement to mutation testing for AI-authored code:

1. Write PBT for any function where the AI authored the implementation.
2. Run with at least 500 examples before merging.
3. If PBT finds a failure, do not simply fix the example — update the generator to reliably produce that class of input, then fix the code.

Pair with mutation testing (see [quality-metrics-dashboard.md](./quality-metrics-dashboard.md)): mutation score measures assertion depth, PBT measures input coverage.

---

## Anti-Patterns

| Anti-Pattern | Problem | Better Approach |
|-------------|---------|-----------------|
| Over-permissive generators | Tests fail on inputs your code will never see | Constrain generators to domain-valid inputs |
| PBT replacing all example tests | Hard to read; harder to debug specific known regressions | Keep examples for known cases; PBT for universal properties |
| Not logging failing seeds | Failures not reproducible | fast-check and Hypothesis log seeds automatically; capture in CI artifacts |
| `numRuns = 10000` in every PR gate | Slow feedback loop | Use 100-200 in PR gates; run 1000+ nightly |
| Testing multiple independent properties in one `fc.assert` | Hard to diagnose failures | One property per `fc.assert` call |

---

## Related Resources

- [quality-metrics-dashboard.md](./quality-metrics-dashboard.md) -- mutation testing to pair with PBT
- [schema-aware-api-fuzzing.md](./schema-aware-api-fuzzing.md) -- schema-driven fuzzing for API contracts
- [shift-left-testing.md](./shift-left-testing.md) -- shifting quality checks earlier
- [fast-check documentation](https://fast-check.dev/)
- [Hypothesis documentation](https://hypothesis.readthedocs.io/)
- [jqwik user guide](https://jqwik.net/docs/current/user-guide.html)
