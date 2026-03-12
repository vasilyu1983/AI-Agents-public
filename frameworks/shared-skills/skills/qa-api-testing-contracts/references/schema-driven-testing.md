# Schema-Driven Testing

Property-based and schema-driven API testing using OpenAPI specifications as the source of truth for automated test generation, fuzzing, and validation.

---

## Contents

- [Schema-Driven Testing Principles](#schema-driven-testing-principles)
- [Schemathesis for OpenAPI Fuzzing](#schemathesis-for-openapi-fuzzing)
- [Property-Based Testing with Hypothesis](#property-based-testing-with-hypothesis)
- [Property-Based Testing with fast-check](#property-based-testing-with-fast-check)
- [Negative Test Generation from Schemas](#negative-test-generation-from-schemas)
- [Boundary Value Analysis](#boundary-value-analysis)
- [Stateful Testing](#stateful-testing)
- [Response Schema Validation](#response-schema-validation)
- [Schema Evolution Testing](#schema-evolution-testing)
- [Custom Strategies for Domain Types](#custom-strategies-for-domain-types)
- [Schema Testing Checklist](#schema-testing-checklist)
- [Related Resources](#related-resources)

---

## Schema-Driven Testing Principles

| Principle | Description | Benefit |
|-----------|-------------|---------|
| Schema as contract | OpenAPI spec is the single source of truth | Tests always match API design |
| Generative testing | Generate inputs from schema constraints | Discover edge cases humans miss |
| Property verification | Assert invariants rather than specific values | Broader coverage per test |
| Negative testing | Intentionally violate schema to test validation | Verify error handling |
| Stateful sequences | Test multi-step workflows with dependencies | Find interaction bugs |

```text
Schema ──▶ Test Generator ──▶ Requests ──▶ API ──▶ Response Validator
  │                                                        │
  └─── Constraints (types, ranges, patterns) ──────────────┘
                    Validates against schema
```

---

## Schemathesis for OpenAPI Fuzzing

Schemathesis generates test cases automatically from OpenAPI/GraphQL specifications.

### Installation and Basic Usage

```bash
# Install
pip install schemathesis

# Run against a live API
schemathesis run https://api.example.com/openapi.json

# Run against a local spec file
schemathesis run ./openapi.yaml --base-url http://localhost:8000

# Target specific endpoints
schemathesis run ./openapi.yaml \
    --base-url http://localhost:8000 \
    --endpoint "/users" \
    --method POST

# Set authentication
schemathesis run ./openapi.yaml \
    --base-url http://localhost:8000 \
    --header "Authorization: Bearer $TOKEN"
```

### Advanced Schemathesis Configuration

```bash
# Increase test cases per endpoint
schemathesis run ./openapi.yaml \
    --base-url http://localhost:8000 \
    --hypothesis-max-examples=500

# Enable stateful testing (link-based)
schemathesis run ./openapi.yaml \
    --base-url http://localhost:8000 \
    --stateful=links

# Output as JUnit XML for CI
schemathesis run ./openapi.yaml \
    --base-url http://localhost:8000 \
    --junit-xml=reports/schemathesis.xml

# Reproduce a specific failure
schemathesis replay ./cassette.yaml
```

### Schemathesis in Python Tests

```python
import schemathesis

schema = schemathesis.from_uri("http://localhost:8000/openapi.json")

@schema.parametrize()
def test_api(case):
    """Schemathesis generates and runs test cases from schema."""
    response = case.call()
    case.validate_response(response)

@schema.parametrize(endpoint="/users", method="POST")
def test_create_user(case):
    """Test user creation with generated payloads."""
    response = case.call()
    case.validate_response(response)
    # Custom assertions
    if response.status_code == 201:
        data = response.json()
        assert "id" in data
        assert isinstance(data["id"], int)

# Add custom checks
@schema.parametrize()
def test_no_server_errors(case):
    """API must never return 500."""
    response = case.call()
    assert response.status_code < 500, (
        f"Server error on {case.method} {case.path}: {response.text}"
    )
```

---

## Property-Based Testing with Hypothesis

Hypothesis generates random inputs satisfying constraints and finds minimal failing examples.

### Basic API Property Tests

```python
from hypothesis import given, settings, strategies as st
import requests

@given(
    name=st.text(min_size=1, max_size=100, alphabet=st.characters(
        whitelist_categories=("L", "N", "Zs")
    )),
    email=st.emails(),
    age=st.integers(min_value=0, max_value=150),
)
@settings(max_examples=200)
def test_create_user_properties(name, email, age):
    """
    Property: Creating a user with valid data always succeeds
    and returns the same data back.
    """
    payload = {"name": name, "email": email, "age": age}
    response = requests.post("http://localhost:8000/v1/users", json=payload)

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == name
    assert data["email"] == email
    assert data["age"] == age
    assert "id" in data

@given(
    page=st.integers(min_value=1, max_value=1000),
    per_page=st.integers(min_value=1, max_value=100),
)
def test_pagination_properties(page, per_page):
    """
    Properties:
    - Response always contains 'data' array
    - Array length <= per_page
    - Meta includes correct page number
    """
    r = requests.get(
        f"http://localhost:8000/v1/users?page={page}&per_page={per_page}"
    )
    assert r.status_code == 200
    body = r.json()
    assert isinstance(body["data"], list)
    assert len(body["data"]) <= per_page
    assert body["meta"]["page"] == page
```

### Strategies from OpenAPI Schema

```python
from hypothesis import strategies as st
import json

def strategy_from_json_schema(schema: dict) -> st.SearchStrategy:
    """Generate Hypothesis strategy from JSON Schema definition."""
    schema_type = schema.get("type")

    if schema_type == "string":
        min_len = schema.get("minLength", 0)
        max_len = schema.get("maxLength", 256)
        pattern = schema.get("pattern")
        enum = schema.get("enum")

        if enum:
            return st.sampled_from(enum)
        if schema.get("format") == "email":
            return st.emails()
        if schema.get("format") == "date":
            return st.dates().map(str)
        if schema.get("format") == "uuid":
            return st.uuids().map(str)
        if pattern:
            return st.from_regex(pattern, fullmatch=True)
        return st.text(min_size=min_len, max_size=max_len)

    elif schema_type == "integer":
        minimum = schema.get("minimum", -2**31)
        maximum = schema.get("maximum", 2**31)
        return st.integers(min_value=minimum, max_value=maximum)

    elif schema_type == "number":
        minimum = schema.get("minimum", -1e10)
        maximum = schema.get("maximum", 1e10)
        return st.floats(
            min_value=minimum, max_value=maximum,
            allow_nan=False, allow_infinity=False,
        )

    elif schema_type == "boolean":
        return st.booleans()

    elif schema_type == "array":
        items_strategy = strategy_from_json_schema(schema.get("items", {}))
        min_items = schema.get("minItems", 0)
        max_items = schema.get("maxItems", 10)
        return st.lists(items_strategy, min_size=min_items, max_size=max_items)

    elif schema_type == "object":
        properties = schema.get("properties", {})
        required = set(schema.get("required", []))
        fixed = {
            k: strategy_from_json_schema(v)
            for k, v in properties.items()
            if k in required
        }
        optional = {
            k: strategy_from_json_schema(v)
            for k, v in properties.items()
            if k not in required
        }
        return st.fixed_dictionaries(fixed, optional=optional)

    return st.none()
```

---

## Property-Based Testing with fast-check

### JavaScript/TypeScript API Testing

```typescript
import fc from 'fast-check';
import axios from 'axios';

const BASE_URL = 'http://localhost:8000/v1';

describe('User API Properties', () => {
  it('creating a user with valid data returns 201', async () => {
    await fc.assert(
      fc.asyncProperty(
        fc.record({
          name: fc.string({ minLength: 1, maxLength: 100 }),
          email: fc.emailAddress(),
          age: fc.integer({ min: 0, max: 150 }),
        }),
        async (user) => {
          const res = await axios.post(`${BASE_URL}/users`, user, {
            validateStatus: () => true,
          });
          expect(res.status).toBe(201);
          expect(res.data.name).toBe(user.name);
          expect(res.data.email).toBe(user.email);
        },
      ),
      { numRuns: 100 },
    );
  });

  it('GET /users always returns valid pagination', async () => {
    await fc.assert(
      fc.asyncProperty(
        fc.integer({ min: 1, max: 100 }),
        fc.integer({ min: 1, max: 50 }),
        async (page, perPage) => {
          const res = await axios.get(
            `${BASE_URL}/users?page=${page}&per_page=${perPage}`,
          );
          expect(res.status).toBe(200);
          expect(Array.isArray(res.data.data)).toBe(true);
          expect(res.data.data.length).toBeLessThanOrEqual(perPage);
        },
      ),
    );
  });

  it('invalid input always returns 4xx, never 5xx', async () => {
    await fc.assert(
      fc.asyncProperty(
        fc.anything(),
        async (randomPayload) => {
          const res = await axios.post(`${BASE_URL}/users`, randomPayload, {
            validateStatus: () => true,
          });
          // Server must never crash on random input
          expect(res.status).toBeLessThan(500);
        },
      ),
      { numRuns: 200 },
    );
  });
});
```

---

## Negative Test Generation from Schemas

### Systematic Invalid Input Generation

```python
def generate_negative_cases(schema: dict) -> list[dict]:
    """Generate invalid inputs that should trigger validation errors."""
    negative = []
    properties = schema.get("properties", {})
    required = schema.get("required", [])

    # Missing required fields
    for field in required:
        case = {k: generate_valid(v) for k, v in properties.items() if k != field}
        negative.append({
            "payload": case,
            "description": f"Missing required field: {field}",
            "expected_status": 422,
        })

    # Wrong types for each field
    for field, field_schema in properties.items():
        wrong_type_values = get_wrong_type_values(field_schema["type"])
        for wrong_val in wrong_type_values:
            case = {k: generate_valid(v) for k, v in properties.items()}
            case[field] = wrong_val
            negative.append({
                "payload": case,
                "description": f"Wrong type for {field}: {type(wrong_val).__name__}",
                "expected_status": 422,
            })

    # Boundary violations
    for field, field_schema in properties.items():
        if "maxLength" in field_schema:
            case = {k: generate_valid(v) for k, v in properties.items()}
            case[field] = "x" * (field_schema["maxLength"] + 1)
            negative.append({
                "payload": case,
                "description": f"Exceeds maxLength for {field}",
                "expected_status": 422,
            })
        if "minimum" in field_schema:
            case = {k: generate_valid(v) for k, v in properties.items()}
            case[field] = field_schema["minimum"] - 1
            negative.append({
                "payload": case,
                "description": f"Below minimum for {field}",
                "expected_status": 422,
            })

    return negative

def get_wrong_type_values(expected_type: str) -> list:
    """Return values of incorrect types."""
    all_types = {
        "string": [123, True, None, [], {}],
        "integer": ["abc", True, None, [], {}, 3.14],
        "number": ["abc", True, None, [], {}],
        "boolean": ["abc", 0, None, [], {}],
        "array": ["abc", 123, None, {}],
        "object": ["abc", 123, None, []],
    }
    return all_types.get(expected_type, [None])
```

### Running Negative Tests

```python
@pytest.mark.parametrize(
    "case",
    generate_negative_cases(USER_SCHEMA),
    ids=lambda c: c["description"],
)
def test_validation_rejects_invalid_input(api_client, case):
    """API must reject all invalid inputs with proper error response."""
    response = api_client.post("/v1/users", json=case["payload"])
    assert response.status_code == case["expected_status"], (
        f"Expected {case['expected_status']} for: {case['description']}, "
        f"got {response.status_code}"
    )
    # Error response should include field-level detail
    error = response.json()
    assert "detail" in error or "errors" in error
```

---

## Boundary Value Analysis

### Boundary Matrix from Schema

| Field | Type | Constraint | Boundary Values to Test |
|-------|------|-----------|------------------------|
| name | string | minLength: 1, maxLength: 100 | `""`, `"a"`, `"a"*100`, `"a"*101` |
| age | integer | minimum: 0, maximum: 150 | `-1`, `0`, `1`, `149`, `150`, `151` |
| price | number | minimum: 0.01, maximum: 99999.99 | `0`, `0.01`, `0.02`, `99999.98`, `99999.99`, `100000` |
| tags | array | minItems: 0, maxItems: 10 | `[]`, `["a"]`, `["a"]*10`, `["a"]*11` |
| email | string | format: email | `"a@b.c"`, `"@b.com"`, `"a@.com"`, 256-char email |

### Automated Boundary Testing

```python
def generate_boundary_values(schema: dict) -> list[tuple]:
    """Generate boundary test values from schema constraints."""
    boundaries = []

    for field, props in schema.get("properties", {}).items():
        if props["type"] == "integer":
            lo = props.get("minimum")
            hi = props.get("maximum")
            if lo is not None:
                boundaries.extend([
                    (field, lo - 1, "below_minimum", 422),
                    (field, lo, "at_minimum", 200),
                    (field, lo + 1, "above_minimum", 200),
                ])
            if hi is not None:
                boundaries.extend([
                    (field, hi - 1, "below_maximum", 200),
                    (field, hi, "at_maximum", 200),
                    (field, hi + 1, "above_maximum", 422),
                ])

        elif props["type"] == "string":
            min_len = props.get("minLength", 0)
            max_len = props.get("maxLength")
            if min_len > 0:
                boundaries.extend([
                    (field, "x" * (min_len - 1), "below_minLength", 422),
                    (field, "x" * min_len, "at_minLength", 200),
                ])
            if max_len:
                boundaries.extend([
                    (field, "x" * max_len, "at_maxLength", 200),
                    (field, "x" * (max_len + 1), "above_maxLength", 422),
                ])

    return boundaries
```

---

## Stateful Testing

### Link-Based Stateful Testing (Schemathesis)

```bash
# Schemathesis follows OpenAPI links to test multi-step workflows
# e.g., POST /users → GET /users/{id} → PATCH /users/{id} → DELETE /users/{id}
schemathesis run ./openapi.yaml \
    --base-url http://localhost:8000 \
    --stateful=links \
    --hypothesis-max-examples=100
```

### Custom State Machine Testing

```python
import hypothesis.stateful as stateful
from hypothesis import strategies as st

class APIStateMachine(stateful.RuleBasedStateMachine):
    """Test API through stateful sequences of operations."""

    created_user_ids = stateful.Bundle("user_ids")

    @stateful.rule(
        target=created_user_ids,
        name=st.text(min_size=1, max_size=50),
        email=st.emails(),
    )
    def create_user(self, name, email):
        r = requests.post(BASE_URL + "/users", json={
            "name": name, "email": email
        })
        assert r.status_code == 201
        user_id = r.json()["id"]
        return user_id

    @stateful.rule(user_id=created_user_ids)
    def get_user(self, user_id):
        r = requests.get(f"{BASE_URL}/users/{user_id}")
        assert r.status_code == 200
        assert r.json()["id"] == user_id

    @stateful.rule(
        user_id=created_user_ids,
        new_name=st.text(min_size=1, max_size=50),
    )
    def update_user(self, user_id, new_name):
        r = requests.patch(
            f"{BASE_URL}/users/{user_id}",
            json={"name": new_name},
        )
        assert r.status_code == 200
        assert r.json()["name"] == new_name

    @stateful.rule(user_id=stateful.consumes(created_user_ids))
    def delete_user(self, user_id):
        r = requests.delete(f"{BASE_URL}/users/{user_id}")
        assert r.status_code == 204

        # Verify deletion
        r = requests.get(f"{BASE_URL}/users/{user_id}")
        assert r.status_code == 404

TestAPIStateMachine = APIStateMachine.TestCase
```

---

## Response Schema Validation

### Runtime Response Validation

```python
import jsonschema

def validate_response_against_schema(
    response_data: dict,
    openapi_spec: dict,
    path: str,
    method: str,
    status_code: int,
) -> list[str]:
    """Validate API response matches OpenAPI schema."""
    errors = []

    try:
        response_schema = (
            openapi_spec["paths"][path][method]["responses"]
            [str(status_code)]["content"]["application/json"]["schema"]
        )
    except KeyError:
        errors.append(f"No schema defined for {method.upper()} {path} {status_code}")
        return errors

    # Resolve $ref if present
    response_schema = resolve_refs(response_schema, openapi_spec)

    validator = jsonschema.Draft7Validator(response_schema)
    for error in validator.iter_errors(response_data):
        errors.append(f"{error.json_path}: {error.message}")

    return errors
```

### Middleware Validation (Python)

```python
from fastapi import FastAPI, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import json

class SchemaValidationMiddleware(BaseHTTPMiddleware):
    """Validate all responses match OpenAPI schema in dev/test."""

    def __init__(self, app, openapi_spec: dict):
        super().__init__(app)
        self.spec = openapi_spec

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)

        if request.url.path.startswith("/api/"):
            body = b""
            async for chunk in response.body_iterator:
                body += chunk

            errors = validate_response_against_schema(
                response_data=json.loads(body),
                openapi_spec=self.spec,
                path=request.url.path,
                method=request.method.lower(),
                status_code=response.status_code,
            )

            if errors:
                # Log schema violations (do not block in prod)
                logger.warning(f"Schema violation: {errors}")

            return Response(
                content=body,
                status_code=response.status_code,
                headers=dict(response.headers),
            )
        return response
```

---

## Schema Evolution Testing

### Track Schema Changes Over Time

```python
def test_schema_evolution_is_backward_compatible(
    current_schema: dict,
    previous_schema: dict,
):
    """Verify schema changes are backward compatible."""
    current_required = set(current_schema.get("required", []))
    previous_required = set(previous_schema.get("required", []))

    # New required fields = breaking change
    new_required = current_required - previous_required
    assert not new_required, (
        f"New required fields break backward compatibility: {new_required}"
    )

    # Removed fields = breaking change
    previous_fields = set(previous_schema.get("properties", {}).keys())
    current_fields = set(current_schema.get("properties", {}).keys())
    removed_fields = previous_fields - current_fields
    assert not removed_fields, (
        f"Removed fields break backward compatibility: {removed_fields}"
    )

    # Type changes = breaking change
    for field in previous_fields & current_fields:
        prev_type = previous_schema["properties"][field].get("type")
        curr_type = current_schema["properties"][field].get("type")
        assert prev_type == curr_type, (
            f"Type change for '{field}': {prev_type} -> {curr_type}"
        )
```

---

## Custom Strategies for Domain Types

### Building Domain-Specific Generators

```python
from hypothesis import strategies as st

# Currency amount: positive, 2 decimal places
currency = st.decimals(
    min_value="0.01", max_value="999999.99", places=2
).map(float)

# Phone number: E.164 format
phone_number = st.from_regex(r"\+[1-9]\d{6,14}", fullmatch=True)

# ISO country code
country_code = st.sampled_from(["US", "GB", "DE", "FR", "JP", "AU", "CA"])

# Slug (URL-safe string)
slug = st.from_regex(r"[a-z0-9]+(-[a-z0-9]+)*", fullmatch=True).filter(
    lambda s: 3 <= len(s) <= 60
)

# Composite domain object
order_strategy = st.fixed_dictionaries({
    "customer_id": st.uuids().map(str),
    "items": st.lists(
        st.fixed_dictionaries({
            "sku": st.from_regex(r"[A-Z]{3}-\d{4}", fullmatch=True),
            "quantity": st.integers(min_value=1, max_value=100),
            "unit_price": currency,
        }),
        min_size=1,
        max_size=20,
    ),
    "currency": st.sampled_from(["USD", "EUR", "GBP"]),
    "shipping_country": country_code,
})
```

---

## Schema Testing Checklist

- [ ] OpenAPI spec is the single source of truth for all tests
- [ ] Schemathesis runs against all endpoints in CI
- [ ] Property-based tests cover core creation/read/update/delete flows
- [ ] Negative tests generated from schema for all required fields
- [ ] Boundary values tested for all constrained fields
- [ ] Stateful testing validates multi-step workflows
- [ ] Response schema validation runs in test/dev environments
- [ ] Schema evolution checked for backward compatibility
- [ ] Custom strategies built for domain-specific types
- [ ] Failing examples are minimized and saved for regression
- [ ] CI gates on server errors (5xx) from fuzzed input

---

## Related Resources

- **[contract-testing-patterns.md](contract-testing-patterns.md)** - Consumer-driven contract testing
- **[api-versioning-strategies.md](api-versioning-strategies.md)** - Versioning and compatibility
- **[api-security-testing.md](api-security-testing.md)** - Security-focused API testing
- **[SKILL.md](../SKILL.md)** - QA API Testing & Contracts skill overview
