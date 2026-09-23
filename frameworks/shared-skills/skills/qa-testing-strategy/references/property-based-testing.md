# Property-Based Testing

## Table of Contents

- [Concept](#concept)
- [Runnable Contract Workflow](#runnable-contract-workflow)
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

Property-based testing (PBT) supplements hand-crafted examples with generators over a declared input domain. Mature frameworks such as Hypothesis also try to shrink generated failures. Preserve a concrete failing example in the test source when it must remain a permanent regression case; a library's internal failure database or replay blob can change across versions.

---

## Concept

```text
Example-based test:
  Given price = 9.99, quantity = 3
  Then total = 29.97

Property-based test:
  For all price in [0.01, 999.99] and quantity in [1, 100]
  total == price * quantity (exactly for Decimal/integer minor units;
                             within a specified tolerance for binary floats)
  AND total >= price
```

`total >= quantity` is not a valid invariant when price can be below `1`: `0.25 * 2 = 0.50`, which is less than the unit count `2`. Compare quantities only when they have the same unit. `total >= price` is valid here because quantity is constrained to a positive integer.

---

## Runnable Contract Workflow

Use the standard-library runner when a project has no property-testing dependency or when you need a portable contract demonstration. It tests any Python adapter that supplies generated cases, property checks, follow-up transformations, and metamorphic relation checks.

Select it for deterministic calculators, parsers, serializers, and equivalent configuration representations. For stateful systems or larger input spaces, translate the same domains and oracles to Hypothesis, fast-check, or jqwik so you gain their generation and shrinking support.

Required adapter inputs:

| Member | Contract |
|---|---|
| `ORACLES` | Non-empty mapping from every emitted check name to the author's independent-oracle rationale |
| `generate(rng)` | Return one finite JSON-serializable case from the valid input domain; depend only on the supplied RNG |
| `evaluate(case)` | Invoke the system under test and return an observable result that supports defensive copying |
| `check_properties(case, result)` | Return one or more `{name, ok, detail}` mappings |
| `transformations(case)` | Return one or more `{name, case}` valid follow-ups |
| `check_relation(...)` | Return named checks comparing source and follow-up results |
| `configure_mutation(name)` | Optional negative-control hook used only with `--mutation` |

Start from [the example adapter](../assets/property_contract_example.py). It uses exact decimal arithmetic and covers config parsing plus JSON serialization. Review the adapter first: `--contract` imports and executes local Python code, and this runner does not provide a sandbox. Pass the actual trusted adapter path; the result repeats its resolved path for auditability.

Run from the `qa-testing-strategy` skill directory (an equivalent absolute path works from any directory):

```bash
python3 scripts/property_contract_runner.py \
  --contract assets/property_contract_example.py \
  --seed 20260908 --cases 120 --json
```

Interpret exit `0` as all sampled checks passing, exit `1` as a reproducible contract failure, and exit `2` as an invalid adapter or command. A pass covers only the generated domain, sampled cases, named properties, and named transformations. It does not prove correctness outside them.

The runner snapshots each case and result before later callbacks, and gives `evaluate`, property checks, transformations, and relation checks separate defensive copies. A target or callback may mutate its copy without rewriting the oracle input or failure artifact. Adapter-level global state is outside that isolation: deterministic case-index replay requires generation and evaluation to avoid cross-case state that changes later outcomes. `ORACLES` records the author's justification; the runner checks that a declaration exists, not that it is logically independent or correct.

On failure, copy the printed `replay_command`; with the same adapter and Python behavior, it regenerates the same case from `seed` and `case_index`. The failure payload also contains the generated case. Promote important counterexamples into fixed unit tests instead of treating pseudorandom replay as a permanent artifact. Verify that the suite can fail by running the documented mutations:

```bash
python3 scripts/property_contract_runner.py \
  --contract assets/property_contract_example.py \
  --seed 20260908 --cases 120 --mutation calculator-add-unit --json
python3 scripts/test_property_contract_runner.py
```

The regression test proves the known-correct adapter passes and deliberate calculator, parser, and serialization faults exit `1` and replay identically. The `parser-space-sensitive` mutation passes its source-case property and fails only after the equivalent-representation transformation, so it is a negative control for the metamorphic relation itself. Replace the example adapter with a thin adapter around the user's code; do not copy its example oracles unless they are true business or protocol requirements for that system.

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
test('total equals unit price times quantity and is at least unit price', () => {
  fc.assert(
    fc.property(
      fc.float({ min: 0.01, max: 999.99, noNaN: true }),
      fc.integer({ min: 1, max: 100 }),
      (price, quantity) => {
        const total = computeTotal(price, quantity);
        expect(total).toBeCloseTo(price * quantity);
        expect(total).toBeGreaterThanOrEqual(price);
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

Capture the tool version, generator code, and replay data with a generated failure. Seeds and internal replay blobs may not reproduce across library or test changes. Keep important counterexamples as explicit examples in source; Hypothesis recommends this rather than relying on its example database or version-specific replay blob for correctness.

**Default CI strategy**: keep `numRuns` / `max_examples` low (100-200) in the standard PR gate. Run high-count sweeps (1000+) nightly or pre-release.

```yaml
# GitHub Actions: nightly deep PBT run
- name: Property-based tests (thorough)
  env:
    HY_PROFILE: nightly         # Hypothesis: 2000 examples
    FC_NUM_RUNS: "1000"         # fast-check: read in conftest or test setup
  run: npx vitest run --reporter=verbose tests/property/
```

**Reproducing failures**: capture the framework's replay information in CI. For fast-check, pass the reported seed and path explicitly:

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

PBT and mutation testing answer different questions for AI-authored code:

1. Add PBT where the implementation has a meaningful universal property or broad structured input domain.
2. Choose the run count from execution cost and risk; keep the seed, version, and failing example in the evidence.
3. If PBT finds a failure, do not simply fix the example — update the generator to reliably produce that class of input, then fix the code.

Pair with mutation testing (see [quality-metrics-dashboard.md](./quality-metrics-dashboard.md)): mutation score measures assertion depth, PBT measures input coverage.

---

## Anti-Patterns

| Anti-Pattern | Problem | Better Approach |
|-------------|---------|-----------------|
| Over-permissive generators | Tests fail on inputs your code will never see | Constrain generators to domain-valid inputs |
| PBT replacing all example tests | Hard to read; harder to debug specific known regressions | Keep examples for known cases; PBT for universal properties |
| Relying only on transient replay state | A library upgrade or cache loss can remove the regression | Capture replay data, then promote important failures into explicit examples |
| A dimensionally invalid invariant | The test rejects correct behavior, such as comparing money total to an item count | Compare like units and prove the property's preconditions |
| `numRuns = 10000` in every PR gate | Slow feedback loop | Use 100-200 in PR gates; run 1000+ nightly |
| Testing multiple independent properties in one `fc.assert` | Hard to diagnose failures | One property per `fc.assert` call |

---

## Related Resources

- [quality-metrics-dashboard.md](./quality-metrics-dashboard.md) -- mutation testing to pair with PBT
- [schema-aware-api-fuzzing.md](./schema-aware-api-fuzzing.md) -- schema-driven fuzzing for API contracts
- [shift-left-testing.md](./shift-left-testing.md) -- shifting quality checks earlier
- [fast-check documentation](https://fast-check.dev/)
- [Hypothesis documentation](https://hypothesis.readthedocs.io/)
- [original metamorphic-testing report](https://www.cse.ust.hk/~scc/publ/CS98-01-metamorphictesting.pdf)
- [jqwik user guide](https://jqwik.net/docs/current/user-guide.html)
