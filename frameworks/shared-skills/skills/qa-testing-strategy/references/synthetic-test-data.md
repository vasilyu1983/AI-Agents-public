# Synthetic Test Data (2026)

Ephemeral, privacy-safe test data reduces reliance on static datasets and helps avoid using real customer data in CI and staging.

## Why Synthetic Data

| Static Data | Synthetic Data |
| ----------- | -------------- |
| Privacy risks (PII) | GDPR-compliant |
| Stale, outdated | Generated on demand |
| Storage costs | Ephemeral, disposable |
| Limited edge cases | Unlimited variations |

## Synthetic Data Tools (2026)

| Tool | Best For | Features |
| ---- | -------- | -------- |
| **K2view** | Enterprise TDM | Subsetting, masking, synthetic |
| **MOSTLY AI** | Privacy-first synthetic | GDPR compliance, ML-based |
| **Synthesized** | CI/CD integration | API-first, ephemeral |
| **YData** | Data science teams | Profiling, quality scoring |
| **Faker.js** | Simple fixtures | Deterministic, lightweight |

## CI/CD Integration Pattern

```yaml
# Generate fresh synthetic data per test run
jobs:
  test:
    steps:
      - name: Generate Test Data
        run: |
          synthesized generate \
            --schema ./schemas/users.json \
            --count 1000 \
            --output ./fixtures/users.json

      - name: Run Tests
        run: npm test

      - name: Cleanup
        run: rm -rf ./fixtures  # Ephemeral, no storage
```

## Best Practices

- Generate data per test run (not shared datasets)
- Use seeded random for reproducibility
- Match production distributions (realistic edge cases)
- Dispose after test completion (ephemeral)

## Seeded Random Example

```typescript
// Reproducible test data with seed
import { faker } from '@faker-js/faker';

faker.seed(12345); // Same seed = same data

export const createTestUser = () => ({
  id: faker.string.uuid(),
  email: faker.internet.email(),
  name: faker.person.fullName(),
  createdAt: faker.date.past(),
});

// In tests
beforeEach(() => {
  faker.seed(12345); // Reset seed for reproducibility
});
```

## Privacy Compliance

| Requirement | Solution |
| ----------- | -------- |
| GDPR Right to Erasure | Ephemeral data (auto-deleted) |
| Data Minimization | Generate only needed fields |
| Pseudonymization | Synthetic replaces real PII |
| Cross-border Transfer | No real data leaves region |

## When to Use Synthetic vs Real Data

```text
Use Synthetic when:
├── PII involved (names, emails, addresses)
├── Edge cases needed (boundary values, rare scenarios)
├── Scale testing (10K+ records)
└── CI/CD pipelines (fresh data per run)

Use Real (Anonymized) when:
├── Production bug reproduction
├── Data distribution matters (ML training)
├── Regulatory audit requirements
└── Integration with live systems
```
