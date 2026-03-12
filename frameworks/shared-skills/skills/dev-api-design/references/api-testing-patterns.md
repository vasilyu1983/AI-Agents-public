# API Testing Patterns

> Operational reference for testing APIs across the pyramid — contract tests, integration tests, load tests, and mocking strategies. Covers tooling, CI/CD integration, and consumer-driven workflows.

**Freshness anchor:** January 2026 — aligned with Pact v5, Schemathesis 3.x, k6 v0.52, MSW v2.x, WireMock 3.x, and OpenAPI 3.1.

---

## API Test Pyramid

```
         ┌─────────────────┐
         │   E2E / Smoke    │  ← Few: critical flows only
         ├─────────────────┤
         │  Integration     │  ← Medium: real HTTP, test DB
         ├─────────────────┤
         │  Contract        │  ← Medium: schema + consumer pacts
         ├─────────────────┤
         │  Unit (handlers) │  ← Many: logic without HTTP layer
         └─────────────────┘
```

| Layer | Scope | Speed | Fidelity | Run in CI |
|---|---|---|---|---|
| Unit | Handler logic, validators, transformers | <1ms per test | Low | Every commit |
| Contract | Request/response schemas, consumer pacts | <100ms per test | Medium | Every commit |
| Integration | Full HTTP stack, test database | <5s per test | High | Every PR |
| E2E / Smoke | Critical paths against staging | <30s per test | Highest | Pre-deploy |
| Load | Performance under traffic | Minutes | Performance-specific | Scheduled / pre-release |

---

## Contract Testing

### Decision Tree: Which Contract Testing Approach

```
Do you control both provider and consumer?
├── YES (internal services)
│   ├── Schema-based testing (Schemathesis, openapi-diff)
│   └── Consumer-driven contracts (Pact) if >3 consumers
└── NO (external API / third-party)
    ├── You are PROVIDER → Publish OpenAPI spec, run Schemathesis
    └── You are CONSUMER → Record + replay contract (Pact, MSW)
```

### Pact (Consumer-Driven Contracts)

**Use when:** Multiple consumers depend on your API and you need to verify changes won't break them.

**Setup checklist:**

- [ ] Consumer writes Pact test defining expected interactions
- [ ] Pact file (JSON contract) published to Pact Broker
- [ ] Provider runs verification against all published pacts
- [ ] CI gates prevent deploy if verification fails
- [ ] Pact Broker tracks compatibility matrix across versions

**Consumer-side test (JavaScript):**

```javascript
import { PactV4 } from "@pact-foundation/pact";

const provider = new PactV4({ consumer: "OrderUI", provider: "OrderAPI" });

it("fetches an order", async () => {
  await provider
    .addInteraction()
    .given("order 123 exists")
    .uponReceiving("a request for order 123")
    .withRequest("GET", "/orders/123")
    .willRespondWith(200, {
      body: { id: "123", status: "pending", total: 5000 }
    })
    .executeTest(async (mockServer) => {
      const response = await fetch(`${mockServer.url}/orders/123`);
      expect(response.status).toBe(200);
    });
});
```

**Provider-side verification:**

```javascript
const { Verifier } = require("@pact-foundation/pact");

new Verifier({
  providerBaseUrl: "http://localhost:3000",
  pactBrokerUrl: "https://pact-broker.internal",
  provider: "OrderAPI",
  providerVersion: process.env.GIT_SHA,
  publishVerificationResult: true
}).verifyProvider();
```

### Schemathesis (Property-Based API Testing)

**Use when:** You have an OpenAPI/GraphQL schema and want automated edge-case discovery.

```bash
# Basic run against OpenAPI spec
schemathesis run https://api.example.com/openapi.json --checks all

# Target specific endpoints
schemathesis run spec.yaml --endpoint "/users/{id}" --method GET

# CI-friendly with JUnit output
schemathesis run spec.yaml --checks all --report junit --output results.xml

# Stateful testing (link operations together)
schemathesis run spec.yaml --stateful=links
```

**Checks Schemathesis runs:**

- Response status codes match spec
- Response body validates against schema
- Content-Type headers are correct
- No server errors (5xx) on valid requests
- Negative testing (invalid inputs produce 4xx, not 5xx)

---

## Integration Testing Patterns

### HTTP Integration Test Checklist

- [ ] Tests use real HTTP calls (not mocked transport)
- [ ] Test database is isolated (per-test or per-suite reset)
- [ ] Authentication handled via test tokens (not production credentials)
- [ ] Tests cover happy path, validation errors, 404s, and auth failures
- [ ] Response body AND headers AND status codes are asserted
- [ ] Cleanup runs even when tests fail (afterEach / finally blocks)

### Test Database Strategies

| Strategy | Speed | Isolation | Use when |
|---|---|---|---|
| Transaction rollback | Fast | Per-test | Single DB, no cross-service calls |
| Truncate tables | Medium | Per-suite | Need committed data for reads |
| Docker container per suite | Slow | Complete | Need fresh schema per run |
| In-memory DB (SQLite) | Fast | Per-test | Simple schemas, no DB-specific features |

### Integration Test Structure

```python
# Arrange
user = create_test_user(role="admin")
token = generate_test_token(user)

# Act
response = client.get(
    "/api/v1/orders",
    headers={"Authorization": f"Bearer {token}"}
)

# Assert
assert response.status_code == 200
assert len(response.json()["data"]) > 0
assert response.headers["X-Total-Count"] == "42"
```

---

## API Mocking

### Tool Selection Decision Tree

```
What are you mocking?
├── Browser-side API calls (frontend tests)
│   └── MSW (Mock Service Worker)
├── Backend service dependencies (integration tests)
│   ├── WireMock (Java ecosystem, Docker available)
│   └── Prism (OpenAPI-first mock server)
├── Quick prototyping / design-first
│   └── Prism (auto-generates from OpenAPI spec)
└── E2E tests (Playwright, Cypress)
    └── MSW or built-in route interception
```

### MSW (Mock Service Worker) v2

**Use when:** Frontend tests, Node.js integration tests, or intercepting browser fetch/XHR.

```typescript
// handlers.ts
import { http, HttpResponse } from "msw";

export const handlers = [
  http.get("/api/users/:id", ({ params }) => {
    return HttpResponse.json({
      id: params.id,
      name: "Test User",
      email: "test@example.com"
    });
  }),

  http.post("/api/orders", async ({ request }) => {
    const body = await request.json();
    if (!body.items?.length) {
      return HttpResponse.json(
        { error: "Items required" },
        { status: 400 }
      );
    }
    return HttpResponse.json({ id: "ord_123" }, { status: 201 });
  })
];
```

### WireMock

**Use when:** Java ecosystem or Docker-based service virtualization.

```json
{
  "request": {
    "method": "GET",
    "urlPathPattern": "/api/users/[0-9]+"
  },
  "response": {
    "status": 200,
    "headers": { "Content-Type": "application/json" },
    "jsonBody": {
      "id": 1,
      "name": "Test User"
    }
  }
}
```

```bash
# Run WireMock in Docker
docker run -d --name wiremock -p 8080:8080 \
  -v ./stubs:/home/wiremock/mappings \
  wiremock/wiremock:3.9.1
```

### Prism (OpenAPI Mock Server)

**Use when:** You have an OpenAPI spec and want auto-generated mocks.

```bash
# Start mock server from OpenAPI spec
prism mock openapi.yaml --port 4010

# Validation proxy mode (validate real API against spec)
prism proxy openapi.yaml https://api.staging.example.com --port 4010
```

---

## Load Testing

### Tool Comparison

| Tool | Language | Protocol | Best for |
|---|---|---|---|
| k6 | JavaScript | HTTP, gRPC, WS | Developer-friendly, CI integration |
| Artillery | YAML + JS | HTTP, WS, Socket.io | Config-driven, scenario-based |
| Locust | Python | HTTP | Python teams, custom load shapes |
| Gatling | Scala/Java | HTTP | JVM teams, detailed reports |

### k6 Load Test Template

```javascript
import http from "k6/http";
import { check, sleep } from "k6";

export const options = {
  stages: [
    { duration: "2m", target: 50 },   // ramp up
    { duration: "5m", target: 50 },   // steady state
    { duration: "2m", target: 200 },  // spike
    { duration: "5m", target: 200 },  // sustained spike
    { duration: "2m", target: 0 },    // ramp down
  ],
  thresholds: {
    http_req_duration: ["p(95)<500", "p(99)<1000"],
    http_req_failed: ["rate<0.01"],
  },
};

export default function () {
  const res = http.get("https://api.staging.example.com/v1/products");

  check(res, {
    "status is 200": (r) => r.status === 200,
    "response time < 500ms": (r) => r.timings.duration < 500,
    "has products": (r) => r.json().data.length > 0,
  });

  sleep(1);
}
```

### Load Test Checklist

- [ ] Run against staging, never production (unless canary)
- [ ] Baseline test first (current traffic levels)
- [ ] Test with realistic data distribution (not all same endpoint)
- [ ] Include authentication in test scenarios
- [ ] Monitor backend resources during test (CPU, memory, DB connections)
- [ ] Define pass/fail thresholds before running
- [ ] Store results for trend comparison across releases

---

## Snapshot Testing for API Responses

### When to Use Snapshots

- **Use when:** API response structure is complex and changes infrequently
- **Avoid when:** Responses contain timestamps, random IDs, or volatile data

### Snapshot Strategy

```javascript
it("returns product detail response", async () => {
  const response = await request(app).get("/api/products/stable-123");

  // Sanitize volatile fields before snapshot
  const sanitized = {
    ...response.body,
    createdAt: "[TIMESTAMP]",
    id: "[UUID]"
  };

  expect(sanitized).toMatchSnapshot();
});
```

### Snapshot Maintenance Rules

- [ ] Review snapshot diffs in every PR (don't blindly update)
- [ ] Sanitize timestamps, UUIDs, and random values before snapshotting
- [ ] Keep snapshot files alongside test files (not in a separate tree)
- [ ] Delete orphaned snapshots when tests are removed

---

## CI/CD Integration

### Pipeline Stage Mapping

| Stage | Tests Run | Gate |
|---|---|---|
| Pre-commit (local) | Unit, linting | Optional |
| PR / commit | Unit + contract + integration | Required pass |
| Pre-merge | Full suite including E2E smoke | Required pass |
| Post-deploy (staging) | E2E + smoke against staging | Required pass |
| Scheduled (nightly) | Load tests, Schemathesis fuzzing | Alert on failure |

### CI Configuration Checklist

- [ ] Test database provisioned as CI service (Postgres, Redis containers)
- [ ] API spec linting runs before contract tests (`spectral lint openapi.yaml`)
- [ ] Contract verification publishes results to Pact Broker
- [ ] Test reports published as CI artifacts (JUnit XML, HTML)
- [ ] Flaky test quarantine process defined
- [ ] Load test results compared against baseline thresholds

---

## Anti-Patterns

| Anti-Pattern | Problem | Fix |
|---|---|---|
| Testing only happy paths | Misses validation, auth, and error handling | Cover 4xx and 5xx scenarios explicitly |
| Mocking everything in integration tests | Tests pass but real integration fails | Use real HTTP + test DB for integration layer |
| No contract tests for microservices | Breaking changes discovered in production | Implement consumer-driven contracts (Pact) |
| Load testing production without warning | Outage risk, alert noise | Use staging; if production, coordinate with ops |
| Snapshot tests with volatile data | Tests break on every run | Sanitize timestamps, IDs, random values |
| Single large E2E suite as only tests | Slow, flaky, hard to debug | Follow pyramid: many unit, fewer integration, few E2E |
| Hardcoded test data in assertions | Brittle when seed data changes | Use factories or builders, assert structure not values |
| Skipping authentication in tests | Auth bugs found in production | Include auth in integration and E2E tests |
| No schema validation in CI | Drift between spec and implementation | Run `spectral lint` + Schemathesis on every PR |

---

## Cross-References

- `dev-api-design/references/webhook-patterns.md` — testing webhook delivery and consumers
- `dev-api-design/references/real-time-api-patterns.md` — testing WebSocket and SSE connections
- `qa-api-testing-contracts/SKILL.md` — comprehensive contract testing skill
- `qa-testing-playwright/references/api-testing-playwright.md` — API testing within Playwright
- `software-backend/references/nodejs-best-practices.md` — Node.js-specific testing patterns
