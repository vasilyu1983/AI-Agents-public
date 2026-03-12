# Contract Testing (2026 Expanded)

Contract testing validates API compatibility between services before integration, catching issues early in development.

## Contents

- Approaches Comparison
- Specmatic (Contract-Driven)
- Pact (Consumer-Driven)
- Pact vs Specmatic Decision Tree
- Karate (Unified DSL)
- Bi-Directional Contract Testing (BDCT)
- Contract Testing in CI/CD
- Common Pitfalls

## Approaches Comparison

| Approach | Tool | When to Use |
| -------- | ---- | ----------- |
| **Consumer-Driven (CDC)** | Pact | Consumer knows what it needs |
| **Contract-Driven (CDD)** | Specmatic | OpenAPI as single source of truth |
| **Bi-Directional (BDCT)** | Pactflow | Both sides define expectations |
| **Unified API Testing** | Karate | API, contract, and performance in one |

## Specmatic (Contract-Driven)

OpenAPI spec becomes the executable contract—no separate contract files.

```bash
# Validate API implementation against OpenAPI spec
specmatic test --contract openapi.yaml --host localhost:8080

# Generate stubs from OpenAPI for consumer testing
specmatic stub --contract openapi.yaml --port 9000
```

### Specmatic CI Integration

```yaml
# GitHub Actions
- name: Contract Test
  run: |
    specmatic test \
      --contract ./api/openapi.yaml \
      --host localhost:8080 \
      --report junit

- name: Upload Results
  uses: actions/upload-artifact@v4
  with:
    name: contract-test-results
    path: build/reports/specmatic/
```

## Pact (Consumer-Driven)

Consumer defines expectations, provider verifies.

```typescript
// Consumer test (generates contract)
const provider = new PactV4({
  consumer: 'OrderService',
  provider: 'InventoryService',
});

await provider.executeTest(async (mockServer) => {
  const response = await fetch(`${mockServer.url}/inventory/item-1`);
  expect(response.status).toBe(200);
});
```

```typescript
// Provider verification
const verifier = new Verifier({
  providerBaseUrl: 'http://localhost:3000',
  pactUrls: ['./pacts/orderservice-inventoryservice.json'],
});

await verifier.verifyProvider();
```

## Pact vs Specmatic Decision Tree

```text
Use Pact when:
├── Consumer team owns contract definition
├── Multiple consumers with different needs
├── Gradual migration from no contracts
└── Need Pact Broker for contract sharing

Use Specmatic when:
├── OpenAPI is already the source of truth
├── Strict contract-first development
├── Both provider and consumer use same spec
└── Want to avoid dual maintenance (OpenAPI + Pact JSON)
```

## Karate (Unified DSL)

Single DSL for API, contract, and performance testing.

```gherkin
Feature: Order API

Scenario: Create order
  Given url 'http://localhost:8080/orders'
  And request { userId: 'user-1', productId: 'prod-1' }
  When method POST
  Then status 201
  And match response contains { orderId: '#string' }

Scenario: Get order
  Given url 'http://localhost:8080/orders/order-1'
  When method GET
  Then status 200
  And match response == { orderId: 'order-1', status: '#string' }
```

### Karate Performance Testing

```gherkin
Feature: Order API Performance

Scenario: Load test create order
  * configure driver = { type: 'chrome' }
  * def result = karate.callSingle('create-order.feature')
  * print 'Response time:', result.responseTime

Background:
  * configure readTimeout = 30000
```

## Bi-Directional Contract Testing (BDCT)

Pactflow enables both consumer and provider to contribute to contract definition.

```text
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  Consumer   │────▶│  Pactflow   │◀────│  Provider   │
│  (Pact)     │     │  Broker     │     │  (OpenAPI)  │
└─────────────┘     └─────────────┘     └─────────────┘
        │                  │                    │
        └──────────────────┼────────────────────┘
                           ▼
                   Contract Merge +
                   Compatibility Check
```

## Contract Testing in CI/CD

```yaml
# Recommended pipeline stages
stages:
  - unit-tests
  - contract-tests  # Before integration
  - integration-tests
  - e2e-tests

contract-tests:
  stage: contract-tests
  script:
    # Consumer: Generate contracts
    - npm run test:contract:consumer
    # Publish to broker
    - pact-broker publish ./pacts --broker-base-url $PACT_BROKER_URL
    # Provider: Verify contracts
    - npm run test:contract:provider
  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
```

## Common Pitfalls

| Pitfall | Solution |
| ------- | -------- |
| Testing implementation details | Test behavior (inputs/outputs), not internals |
| Overly specific contracts | Use loose matchers (`#string`, `#number`) |
| Ignoring breaking changes | Use can-i-deploy check before release |
| Missing edge cases | Include error responses in contracts |
| Stale contracts | Automate contract generation in CI |
