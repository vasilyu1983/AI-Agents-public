# Test Data Management

Rules for the data a test suite depends on: who creates it, how it is isolated, when production-shaped data is justified, and how to keep real customer data out of non-production systems. Tool boilerplate (fixture libraries, faker calls, masking products) is not repeated here; the choices are.

## Ownership and Isolation

| Rule | Default | Deviate when |
|---|---|---|
| Who creates the data | The test, through a factory, immediately before use | Read-only reference data (countries, currencies, plans) that no test mutates may be seeded once per environment |
| Identity | Every created entity carries a unique identifier (UUID or run-id prefix) so parallel workers and reruns never collide | Never; shared accounts and fixed emails are the most common cause of order-dependent and shared-resource flakes |
| Cleanup | Per-test teardown or a per-worker schema dropped after the run | Ephemeral environments torn down after the run make explicit cleanup optional |
| Shared fixtures | Not used for anything a test mutates | Never |
| Seeding | Fixed seed per run, printed in the failure output so a case can be replayed | Property-based runners manage their own seed and replay index |

A test that needs data another test created is an integration of two tests, not a test; merge them or make the second one create its own state.

## Synthetic vs Production-Derived Data

| Need | Use | Condition |
|---|---|---|
| Unit, component, contract, most integration and E2E | Synthetic, generated per test | Default |
| Boundary and rare-path coverage | Synthetic, explicitly enumerated (empty, maximum length, unicode, negative, timezone edge, concurrent) | Generators produce typical values unless told otherwise; list the edges |
| Reproducing a production defect | A masked copy of the specific records involved | Masking rules reviewed by the data owner; copy deleted when the fix merges |
| Performance and capacity testing | Production-shaped volume and distribution | Generated to match measured cardinality and skew, or a masked subset; distribution matters more than row count |
| ML or ranking behaviour | Masked production sample | Synthetic data does not reproduce real distributions; state the residual risk |

Synthetic data misleads in two ways worth naming in the strategy: it lacks the referential tangles of real data (orphans, duplicates, legacy encodings), and it is usually uniformly distributed while production is skewed. Integration tests that pass on synthetic data and fail on the first real import are a data-shape gap, not a flake.

## Masking Production Data

When production-derived data is justified:

- Masking is irreversible (hashing with a secret, tokenisation, format-preserving replacement), not reversible pseudonymisation that a key can undo.
- Referential integrity is preserved: the same source value maps to the same masked value across tables, or joins break and the copy tests nothing.
- Free-text fields are dropped or replaced entirely; they hide identifiers that column-level rules miss.
- The masking rule set has an owner, a version and a review date, and the masked copy has a deletion date.
- Legal basis and retention are decided by whoever owns data protection for the product; this file does not make data "compliant" with any regulation. Route those questions to the organisation's privacy owner.

## CI Pattern

```yaml
jobs:
  test:
    steps:
      - name: Generate seed
        run: echo "TEST_SEED=${TEST_SEED:-$GITHUB_RUN_ID}" >> "$GITHUB_ENV"
      - name: Run tests
        run: npm test   # factories read TEST_SEED; failures print it for replay
      - name: Cleanup
        if: always()
        run: npm run test:teardown   # drops the per-run schema or bucket
```

```typescript
import { faker } from '@faker-js/faker';

const seed = Number(process.env.TEST_SEED ?? Date.now());
faker.seed(seed);
console.log(`test seed: ${seed}`);

export const createTestUser = (overrides: Partial<User> = {}): User => ({
  id: faker.string.uuid(),
  email: `u-${faker.string.alphanumeric(8)}@example.test`,
  name: faker.person.fullName(),
  createdAt: faker.date.past(),
  ...overrides,
});
```

Reserved test domains (`example.test`, `example.com`) keep generated addresses from ever reaching a real mailbox.

## Related

- [test-environment-management.md](test-environment-management.md): which environments hold which data class
- [test-automation-patterns.md](test-automation-patterns.md): flaky-test taxonomy, where shared data shows up as order-dependent flakes
- [property-based-testing.md](property-based-testing.md): generated inputs with seed and replay
