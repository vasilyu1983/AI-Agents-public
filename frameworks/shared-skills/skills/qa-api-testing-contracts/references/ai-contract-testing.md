# AI-Powered Contract Testing (2026)

## Overview

AI-powered tools now automate contract test generation, maintenance, and validation. This guide covers the leading approaches and when to use each.

## Guardrails

- Keep deterministic gates (schema lint + breaking diff + contract verification) as the source of truth; AI suggestions must pass them.
- Treat generated tests as a starting point; tighten matchers to avoid flaky or overfitted contracts.
- Sanitize payloads/logs before sharing with third-party tools; never include credentials or PII.

## Tool Comparison

| Tool | Approach | Best For | Setup Effort |
| --- | --- | --- | --- |
| PactFlow AI | Code review + generation | Teams already using Pact | Low |
| Keploy | Traffic capture → tests | Existing APIs with traffic | Very low |
| Postman Postbot | Request/response analysis | Manual API exploration | Low |
| Specmatic | Schema → executable contracts | OpenAPI/GraphQL-first teams | Low |

## PactFlow AI Code Review

PactFlow's AI inspects Pact tests and suggests improvements.

### What It Checks

- Contract completeness (missing scenarios)
- Matcher usage (overly strict vs too loose)
- State handler coverage
- Best practice violations

### Setup

```javascript
// Enable AI review in PactFlow settings
// Runs automatically on contract publish

// Example: AI detects overly strict matcher
// Before (flagged)
willRespondWith: {
  body: { id: "123", name: "John" }  // Exact match
}

// After (AI suggestion)
willRespondWith: {
  body: {
    id: Matchers.string("123"),
    name: Matchers.string("John")
  }
}
```

### Notes

- Feature availability, pricing, and supported languages change frequently; confirm current capabilities in vendor docs.
- Treat AI output as untrusted until it passes contract verification and your own review.
- Avoid uploading sensitive payloads or credentials; sanitize examples and logs.

## Bi-Directional Contract Testing

New paradigm combining provider-driven and consumer-driven approaches.

### Traditional CDC Flow

```text
Consumer → Contract → Broker → Provider Verification
```

### Bi-Directional Flow

```text
Consumer → Contract ─┐
                     ├─► Broker ◄─► Comparison
Provider → OpenAPI ──┘
```

### When to Use

| Scenario | Approach |
| --- | --- |
| Greenfield microservices | Traditional CDC |
| Provider already has OpenAPI | Bi-Directional |
| External/third-party APIs | Bi-Directional |
| Legacy system integration | Bi-Directional |

### Setup Example

```yaml
# pact-config.yml for bi-directional
provider:
  name: UserService
  specification:
    type: openapi
    path: ./specs/user-api.yaml

consumer:
  name: WebApp
  contracts:
    - path: ./pacts/webapp-userservice.json
```

## Keploy: Traffic-Based Test Generation

Keploy captures live API traffic and generates tests automatically.

### How It Works

```text
1. Attach to running service
2. Capture real requests/responses
3. Generate test cases with assertions
4. Replay in CI without test environment
```

### Setup

```bash
# Install Keploy
curl -O https://raw.githubusercontent.com/keploy/keploy/main/keploy.sh
chmod +x keploy.sh

# Record tests from running app
keploy record -c "npm start"

# Replay in CI
keploy test -c "npm start" --delay 10
```

### Generated Test Example

```yaml
# keploy/tests/test-1.yaml (auto-generated)
version: api.keploy.io/v1beta2
kind: Http
name: test-1
spec:
  request:
    method: GET
    url: /api/users/123
    headers:
      Authorization: Bearer ***
  response:
    status_code: 200
    body: |
      {"id": "123", "name": "John", "email": "john@example.com"}
  assertions:
    - type: status_code
      expected: 200
    - type: body_contains
      expected: '"id": "123"'
```

### Best Use Cases

- Legacy APIs with no existing tests
- Complex integration flows
- Rapid test coverage bootstrap
- Regression test generation

## Postman Postbot

AI assistant for test generation within Postman.

### Capabilities

- Analyze request/response and generate assertions
- Suggest edge cases and negative scenarios
- Auto-generate documentation
- Debug failing requests

### Example Workflow

```javascript
// 1. Send request in Postman
// 2. Postbot analyzes response
// 3. Suggests tests:

pm.test("Status is 200", () => {
  pm.response.to.have.status(200);
});

pm.test("Response has required fields", () => {
  const json = pm.response.json();
  pm.expect(json).to.have.property("id");
  pm.expect(json).to.have.property("name");
  pm.expect(json).to.have.property("email");
});

pm.test("Email format is valid", () => {
  const json = pm.response.json();
  pm.expect(json.email).to.match(/^[^\s@]+@[^\s@]+\.[^\s@]+$/);
});

// Postbot also suggests edge cases:
// - What if user ID doesn't exist? (404)
// - What if ID is malformed? (400)
// - What if auth token is expired? (401)
```

## Specmatic: Schema-Driven Contracts

Converts OpenAPI/GraphQL specs into executable contracts.

### Key Features

- No code required for basic contract tests
- Intelligent service virtualisation
- Backward compatibility checking
- Works with OpenAPI 3.x and GraphQL SDL

### Setup

```bash
# Install
npm install -g specmatic

# Run contract tests from OpenAPI
specmatic test --contract specs/user-api.yaml --host localhost --port 3000

# Generate stub server
specmatic stub --contract specs/user-api.yaml --port 9000
```

### CI Integration

```yaml
# .github/workflows/contracts.yml
- name: Contract Test
  run: |
    specmatic test \
      --contract specs/api.yaml \
      --host ${{ env.API_HOST }}

- name: Backward Compatibility
  run: |
    specmatic compatible \
      --older origin/main:specs/api.yaml \
      --newer specs/api.yaml
```

## Decision Matrix: When to Use What

| Situation | Recommended Tool |
| --- | --- |
| Starting new microservices | Pact + PactFlow AI |
| Have OpenAPI, need tests fast | Specmatic |
| Legacy API, no specs | Keploy (traffic capture) |
| Manual testing workflow | Postman + Postbot |
| Provider won't run Pact | Bi-Directional + OpenAPI |
| Need regression coverage fast | Keploy |

## AI vs Manual Contract Tests

### Use AI When

- Bootstrapping test coverage
- Generating boilerplate assertions
- Catching obvious missing scenarios
- Maintaining large test suites

### Use Manual When

- Complex business logic validation
- Security-critical flows
- Custom matcher requirements
- Semantic contract rules

## CI Integration Patterns

### Combined AI + Traditional Pipeline

```yaml
# .github/workflows/api-contracts.yml
jobs:
  ai-generated:
    steps:
      - name: Run Keploy tests
        run: keploy test -c "npm start"

  pact-contracts:
    steps:
      - name: Run consumer contracts
        run: npm run test:pact

      - name: Publish to PactFlow
        run: |
          pact-broker publish ./pacts \
            --consumer-app-version=${{ github.sha }}

  ai-review:
    needs: pact-contracts
    steps:
      - name: PactFlow AI Review
        run: |
          # Triggered automatically on publish
          # Review results in PactFlow dashboard
```

## Metrics to Track

| Metric | Target | Tool |
| --- | --- | --- |
| Contract coverage | >80% of endpoints | PactFlow dashboard |
| AI-generated test accuracy | >95% pass rate | Keploy metrics |
| Time to first test | <5 minutes | Specmatic/Keploy |
| False positive rate | <5% | All tools |
