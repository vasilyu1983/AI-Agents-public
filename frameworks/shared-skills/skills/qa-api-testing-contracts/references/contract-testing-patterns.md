# Contract Testing Patterns

## Breaking vs Non-Breaking Changes

### Breaking Changes (Require Version Bump)

| Change Type | Example | Risk |
| --- | --- | --- |
| Remove field | `user.email` deleted | Consumers crash |
| Remove endpoint | DELETE `/v1/users` | 404 errors |
| Change field type | `age: string` → `age: number` | Parse failures |
| Required field added | `email` now required | 400 errors |
| Rename enum | `ACTIVE` → `ENABLED` | Validation fails |
| Change default | `limit: 10` → `limit: 50` | Behavior change |
| Narrow allowed values | Remove enum option | Validation fails |
| Tighten validation | `maxLength: 100` → `maxLength: 20` | Previously valid input rejected |
| Change error model | `{"error": ...}` → RFC 7807 `problem+json` | Client parsing/UX breaks |

### Non-Breaking Changes (Safe to Release)

| Change Type | Example | Notes |
| --- | --- | --- |
| Add optional field | `user.nickname` added | Ignored by old consumers |
| Add endpoint | POST `/v1/users/bulk` | New capability |
| Add enum value | `STATUS: ARCHIVED` | Extend options |
| Deprecate field | `@deprecated email` | Migration period |
| Widen allowed values | Add enum option | More permissive |
| Loosen validation | Allow larger `maxLength` | More permissive |

## GraphQL Change Safety (SDL)

### Breaking Changes

- Remove a field/type/enum value used by consumers.
- Change a field return type or input type incompatibly.
- Tighten nullability (`String` → `String!`) or list nullability in a way that can change runtime results.
- Add a required argument to an existing field.
- Change a directive or federation composition in a way that breaks query planning.

### Non-Breaking Changes

- Add a field (clients ignore what they do not request).
- Add an optional argument.
- Add an enum value (as long as consumers handle unknowns defensively).
- Deprecate fields with a published sunset policy.

## gRPC / Protobuf Change Safety (Proto3)

### Breaking Changes

- Reuse or renumber field numbers (wire incompatibility).
- Change a field type incompatibly (for example, `int32` → `string`).
- Change request/response shapes in a way that breaks existing clients (for example, moving fields between messages without compatibility rules).
- Remove an RPC or change streaming semantics.
- Rename packages/services without aliases (client generation and routing break).

### Non-Breaking Changes

- Add a new field with a new field number.
- Add a new RPC.
- Add an enum value (clients should handle unknown values).
- Remove a field only if you reserve the field number and name and keep behavior compatible.

**Rule of thumb:** never reuse field numbers; use `reserved` for removed numbers/names; run `buf breaking` in CI.

## Consumer-Driven Contract Testing

### Traditional CDC Workflow

```text
Consumer                    Broker                    Provider
   │                          │                          │
   ├── Generate contract ────►│                          │
   │   (Pact file)            │                          │
   │                          │◄── Fetch contracts ──────┤
   │                          │                          │
   │                          │    Verify against        │
   │                          │    provider ────────────►│
   │                          │                          │
   │◄── Results ──────────────┤◄── Publish results ──────┤
```

### Bi-Directional Contract Testing (2026)

New paradigm that combines consumer contracts with provider specifications.

```text
Consumer ─── Pact Contract ───┐
                              ├──► Broker ◄──► Comparison Engine
Provider ─── OpenAPI Spec ────┘
```

**When to Use Bi-Directional:**

| Scenario | Recommended Approach |
| --- | --- |
| Greenfield microservices | Traditional CDC |
| Provider already has OpenAPI | Bi-Directional |
| External/third-party APIs | Bi-Directional |
| Provider team won't run Pact | Bi-Directional |
| Legacy system integration | Bi-Directional |

**Setup Example:**

```yaml
# pactflow.yml
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

**Benefits:**

- Provider doesn't need to run Pact verification
- Works with existing OpenAPI specs
- Faster adoption for teams new to contract testing
- Supports provider-driven development

### Consumer Test Example (Pact)

```javascript
// consumer.pact.spec.js
const { Pact } = require('@pact-foundation/pact');

describe('User API Consumer', () => {
  const provider = new Pact({
    consumer: 'WebApp',
    provider: 'UserService',
  });

  it('fetches a user by ID', async () => {
    await provider.addInteraction({
      state: 'user 123 exists',
      uponReceiving: 'a request for user 123',
      withRequest: {
        method: 'GET',
        path: '/users/123',
      },
      willRespondWith: {
        status: 200,
        body: {
          id: '123',
          name: Matchers.string('John'),
          email: Matchers.email(),
        },
      },
    });

    const user = await userClient.getUser('123');
    expect(user.id).toBe('123');
  });
});
```

### Provider Verification Example

```javascript
// provider.pact.spec.js
const { Verifier } = require('@pact-foundation/pact');

describe('User API Provider', () => {
  it('validates consumer contracts', async () => {
    await new Verifier({
      providerBaseUrl: 'http://localhost:3000',
      pactBrokerUrl: process.env.PACT_BROKER_URL,
      provider: 'UserService',
      publishVerificationResult: true,
      stateHandlers: {
        'user 123 exists': async () => {
          await seedUser({ id: '123', name: 'John' });
        },
      },
    }).verifyProvider();
  });
});
```

## Schema Validation Patterns

### Four Levels of Validation

| Level | Focus | Tools | Stage |
| --- | --- | --- | --- |
| 1. Syntax | Valid YAML/JSON | yamllint, jsonlint | Pre-commit |
| 2. Schema | Spec compliance | Spectral, buf | Pre-commit |
| 3. Semantic | Logical correctness | Custom rules | PR |
| 4. Design | Best practices | Zally, Spectral | PR |

### Property-Based Testing (Schemathesis)

```bash
# Run property-based tests against OpenAPI spec
schemathesis run https://api.example.com/openapi.yaml \
  --checks all \
  --hypothesis-max-examples=100 \
  --base-url https://staging.api.example.com
```

Schemathesis automatically generates test cases to find:

- 500 errors from edge case inputs
- Schema violations in responses
- Security issues (auth bypass, injection)

## CI Integration Patterns

### Pre-merge Gates

```yaml
# .github/workflows/api-contracts.yml
name: API Contract Validation

on: [pull_request]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Lint OpenAPI
        run: npx @stoplight/spectral-cli lint specs/*.yaml

      - name: Check breaking changes
        run: |
          git show "origin/${{ github.base_ref }}:specs/api.yaml" > /tmp/api.base.yaml
          oasdiff breaking /tmp/api.base.yaml specs/api.yaml

  contract-test:
    runs-on: ubuntu-latest
    steps:
      - name: Run consumer contract tests
        run: npm run test:pact

      - name: Publish contracts to broker
        run: npx pact-broker publish ./pacts \
          --consumer-app-version=${{ github.sha }} \
          --broker-base-url=${{ secrets.PACT_BROKER_URL }}
```

### Post-merge Provider Verification

```yaml
# Run after provider changes merge
verify-contracts:
  runs-on: ubuntu-latest
  steps:
    - name: Start provider
      run: docker compose up -d api

    - name: Verify all consumer contracts
      run: |
        npx pact-verifier \
          --provider-base-url=http://localhost:3000 \
          --pact-broker-url=${{ secrets.PACT_BROKER_URL }} \
          --provider=UserService \
          --publish-verification-results
```

### Deployment Gate (Pact Broker)

Run a deploy gate (separate from tests) so you only deploy versions proven compatible:

```bash
# In the deploy pipeline (example: staging)
npx pact-broker can-i-deploy \
  --pacticipant "UserService" \
  --version "$GITHUB_SHA" \
  --to-environment "staging" \
  --broker-base-url "$PACT_BROKER_URL"

# After a successful deploy
npx pact-broker record-deployment \
  --pacticipant "UserService" \
  --version "$GITHUB_SHA" \
  --environment "staging" \
  --broker-base-url "$PACT_BROKER_URL"
```

## Mock Strategies

### Schema-Based Mocks (Prism)

```bash
# Generate mock server from OpenAPI spec
npx @stoplight/prism-cli mock specs/api.yaml --port 4010

# Responses match schema with realistic fake data
curl http://localhost:4010/users/123
# {"id": "abc123", "name": "John Doe", "email": "john@example.com"}
```

### Contract-Based Mocks (Pact Stub)

```bash
# Start stub server from Pact contracts
npx pact-stub-server --pact-dir ./pacts --port 4011

# Only returns interactions defined in contracts
curl http://localhost:4011/users/123
```

### When to Use Each

| Mock Type | Use When | Pros | Cons |
| --- | --- | --- | --- |
| Schema (Prism) | Early development | Full API surface | May not match real behavior |
| Contract (Pact) | Integration testing | Verified behavior | Limited to defined interactions |
| Record/replay | Legacy APIs | Real responses | Brittle, needs refresh |

## Versioning Strategies

### URL Versioning

```http
GET /v1/users/123
GET /v2/users/123
```

- Clear version visibility
- Easy routing
- URL pollution over time

### Header Versioning

```http
GET /users/123
Accept: application/vnd.api+json; version=2
```

- Clean URLs
- Harder to test/debug
- Proxy complexity

### Contract Testing with Versions

```javascript
// Test multiple versions simultaneously
const versions = ['v1', 'v2'];

versions.forEach(version => {
  describe(`User API ${version}`, () => {
    it('maintains backward compatibility', async () => {
      const response = await fetch(`/${version}/users/123`);
      expect(response.status).toBe(200);
      // v1 and v2 should both return user data
    });
  });
});
```

## Contract Versioning Best Practices (2026)

### Semantic Versioning for Contracts

Apply SemVer principles to API contracts:

| Change Type | Version Bump | Example |
| --- | --- | --- |
| Breaking change | Major (v1 → v2) | Remove field, change type |
| New feature | Minor (v1.0 → v1.1) | Add optional field |
| Bug fix | Patch (v1.0.0 → v1.0.1) | Fix response format |

### Contract Version in Pact

```javascript
// Include version in consumer contract
const provider = new Pact({
  consumer: 'WebApp',
  provider: 'UserService',
  pactfileWriteMode: 'update',
});

// Publish with version
await pactBroker.publishPacts({
  pactFilesOrDirs: ['./pacts'],
  consumerVersion: process.env.GIT_COMMIT,
  tags: ['main', 'v2'],
});
```

### Deprecation Strategy

```yaml
# OpenAPI deprecation example
paths:
  /v1/users/{id}:
    get:
      deprecated: true
      x-deprecation-date: "2026-06-01"
      x-sunset-date: "2026-12-01"
      description: |
        DEPRECATED: Use /v2/users/{id} instead.
        Will be removed on 2026-12-01.
```

### Multi-Version Contract Matrix

```text
Consumer v1.0 ──► Provider v1.x ✓
Consumer v1.0 ──► Provider v2.x ✓ (backward compatible)
Consumer v2.0 ──► Provider v1.x ✗ (requires v2 features)
Consumer v2.0 ──► Provider v2.x ✓
```

## Related Resources

- See `ai-contract-testing.md` for AI-powered test generation
- See `../assets/contract-change-checklist.md` for release validation
