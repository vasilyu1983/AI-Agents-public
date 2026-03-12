# API Documentation Validation

Systematic approaches to validating API documentation accuracy against live endpoints, detecting spec drift, and enforcing documentation-code sync in CI.

## Contents

- [OpenAPI and AsyncAPI Spec Linting](#openapi-and-asyncapi-spec-linting)
- [Spec-to-Implementation Drift Detection](#spec-to-implementation-drift-detection)
- [Example Validation with Mock Servers](#example-validation-with-mock-servers)
- [Request/Response Sample Testing](#requestresponse-sample-testing)
- [Schema Accuracy Verification](#schema-accuracy-verification)
- [Endpoint Coverage Audit](#endpoint-coverage-audit)
- [Automated CI Checks for Doc Drift](#automated-ci-checks-for-doc-drift)
- [Documentation-Code Sync Strategies](#documentation-code-sync-strategies)
- [Tools Comparison](#tools-comparison)
- [Related Resources](#related-resources)

---

## OpenAPI and AsyncAPI Spec Linting

Linting catches structural errors, naming inconsistencies, and missing descriptions before specs reach consumers.

### Spectral (Stoplight)

Spectral is the most widely adopted OpenAPI/AsyncAPI linter. It supports custom rulesets and integrates with CI.

```bash
# Install Spectral
npm install -g @stoplight/spectral-cli

# Lint an OpenAPI spec
spectral lint openapi.yaml

# Lint with a custom ruleset
spectral lint openapi.yaml --ruleset .spectral.yaml

# Lint AsyncAPI spec
spectral lint asyncapi.yaml --ruleset spectral-asyncapi
```

**Custom ruleset example** (`.spectral.yaml`):

```yaml
extends:
  - spectral:oas

rules:
  operation-description:
    description: Every operation must have a description
    given: "$.paths[*][get,post,put,patch,delete]"
    then:
      field: description
      function: truthy
    severity: error

  operation-tags:
    description: Every operation must have at least one tag
    given: "$.paths[*][get,post,put,patch,delete]"
    then:
      field: tags
      function: length
      functionOptions:
        min: 1
    severity: warn

  schema-description:
    description: All schema properties should have descriptions
    given: "$.components.schemas[*].properties[*]"
    then:
      field: description
      function: truthy
    severity: info

  no-empty-examples:
    description: Response examples must not be empty
    given: "$.paths[*][*].responses[*].content[*].examples[*]"
    then:
      function: truthy
    severity: warn
```

### Redocly CLI

Redocly provides stricter validation and can bundle multi-file specs.

```bash
# Install Redocly CLI
npm install -g @redocly/cli

# Lint with built-in recommended rules
redocly lint openapi.yaml

# Lint with custom config
redocly lint openapi.yaml --config redocly.yaml

# Bundle multi-file spec into single file
redocly bundle openapi.yaml -o bundled.yaml

# Preview docs locally
redocly preview-docs openapi.yaml
```

**Redocly config** (`redocly.yaml`):

```yaml
extends:
  - recommended

rules:
  no-empty-servers: error
  operation-operationId-unique: error
  no-path-trailing-slash: error
  path-declaration-must-exist: error
  operation-summary: warn
  tag-description: warn
  no-unused-components: warn
```

### Linting Checklist

- [ ] All endpoints have `operationId`, `summary`, and `description`
- [ ] All request/response schemas reference `$ref` components (no inline)
- [ ] All parameters have `description` and `example`
- [ ] Error responses (4xx, 5xx) are documented with schemas
- [ ] Authentication schemes are declared in `securitySchemes`
- [ ] No unused components in `components/schemas`
- [ ] Server URLs are valid and environment-appropriate

---

## Spec-to-Implementation Drift Detection

Drift occurs when the API implementation diverges from the documented spec. Detection strategies range from runtime traffic comparison to static code analysis.

### Traffic-Based Drift Detection

Capture real API traffic and compare against the spec.

```python
"""
Compare live API responses against OpenAPI spec.
Uses openapi-core for validation.
"""
import requests
import json
from openapi_core import OpenAPI

# Load spec
api = OpenAPI.from_file_path("openapi.yaml")

# Make a real request
response = requests.get("https://api.example.com/users/123")

# Validate response against spec
result = api.validate_response(
    request_method="GET",
    request_path="/users/123",
    response_status=response.status_code,
    response_headers=dict(response.headers),
    response_data=response.json(),
)

if result.errors:
    print("DRIFT DETECTED:")
    for error in result.errors:
        print(f"  - {error}")
else:
    print("Response matches spec")
```

### Code-Annotation Drift Detection

For frameworks that generate specs from code annotations, compare the generated spec to the committed spec.

```bash
#!/bin/bash
# drift-check.sh: Detect drift between generated and committed OpenAPI specs

# Generate spec from code annotations
npx tsoa spec-and-routes  # or: ./gradlew generateOpenApiDocs

# Compare generated vs committed
diff <(yq eval -P generated/openapi.yaml) <(yq eval -P docs/openapi.yaml) > drift.diff

if [ -s drift.diff ]; then
    echo "DRIFT DETECTED between generated spec and committed spec:"
    cat drift.diff
    exit 1
else
    echo "No drift detected"
    exit 0
fi
```

### Drift Detection Strategies

| Strategy | How It Works | Best For |
|----------|-------------|----------|
| Traffic capture | Record prod traffic, validate against spec | Runtime accuracy |
| Code-gen comparison | Generate spec from code, diff against committed spec | Annotation-based APIs |
| Contract testing | Consumer-driven contracts validate provider | Microservices |
| Integration tests | Hit live endpoints, validate response schema | Pre-deploy validation |
| Proxy validation | API gateway validates traffic against spec | Real-time enforcement |

---

## Example Validation with Mock Servers

Mock servers like Prism validate that your documented examples actually conform to your schemas.

### Prism (Stoplight)

```bash
# Install Prism
npm install -g @stoplight/prism-cli

# Start mock server from spec
prism mock openapi.yaml

# Start with validation mode (strict)
prism mock openapi.yaml --errors

# Proxy mode: validate real traffic against spec
prism proxy openapi.yaml https://api.example.com --errors
```

**Proxy validation workflow:**

```bash
# Start Prism in proxy mode
prism proxy openapi.yaml https://api.staging.example.com --errors &

# Run test suite against proxy
API_BASE_URL=http://localhost:4010 pytest tests/api/

# Prism will flag any response that doesn't match the spec
```

### Validating Inline Examples

```yaml
# openapi.yaml snippet with inline examples
paths:
  /users/{id}:
    get:
      responses:
        "200":
          content:
            application/json:
              schema:
                $ref: "#/components/schemas/User"
              examples:
                standard-user:
                  summary: A standard active user
                  value:
                    id: 123
                    name: "Jane Doe"
                    email: "jane@example.com"
                    status: "active"
                    created_at: "2025-01-15T10:30:00Z"
```

```bash
# Validate that all examples conform to their schemas
npx @schemathesis/cli validate openapi.yaml --check-examples
```

---

## Request/Response Sample Testing

Test documented request/response pairs against the live API to verify accuracy.

```python
"""
Automated sample testing: extract examples from OpenAPI spec
and execute them against a live or staging API.
"""
import yaml
import requests
import jsonschema

def load_spec(path: str) -> dict:
    with open(path) as f:
        return yaml.safe_load(f)

def extract_examples(spec: dict) -> list:
    """Extract all request/response example pairs from spec."""
    examples = []
    for path, methods in spec.get("paths", {}).items():
        for method, operation in methods.items():
            if method not in ("get", "post", "put", "patch", "delete"):
                continue
            for status_code, response in operation.get("responses", {}).items():
                content = response.get("content", {})
                for media_type, media in content.items():
                    for name, example in media.get("examples", {}).items():
                        examples.append({
                            "path": path,
                            "method": method,
                            "status_code": status_code,
                            "example_name": name,
                            "example_value": example.get("value"),
                            "schema": media.get("schema"),
                        })
    return examples

def validate_examples(spec_path: str, base_url: str):
    spec = load_spec(spec_path)
    examples = extract_examples(spec)
    results = []

    for ex in examples:
        # Validate example against its own schema
        try:
            resolver = jsonschema.RefResolver.from_schema(spec)
            jsonschema.validate(ex["example_value"], ex["schema"], resolver=resolver)
            results.append({"example": ex["example_name"], "status": "PASS"})
        except jsonschema.ValidationError as e:
            results.append({
                "example": ex["example_name"],
                "status": "FAIL",
                "error": str(e.message),
            })

    return results

# Run validation
results = validate_examples("openapi.yaml", "https://api.staging.example.com")
for r in results:
    print(f"[{r['status']}] {r['example']}")
```

---

## Schema Accuracy Verification

Ensure that documented schemas match the actual shape of API responses.

### Schema Diff Script

```python
"""
Compare documented schema against actual API response shape.
Detects: missing fields, extra undocumented fields, type mismatches.
"""
import requests
import yaml

def get_response_shape(url: str) -> dict:
    """Get the actual response and infer its shape."""
    resp = requests.get(url)
    return infer_schema(resp.json())

def infer_schema(data, path="$") -> dict:
    """Recursively infer JSON Schema from a response."""
    if isinstance(data, dict):
        return {
            "type": "object",
            "properties": {
                k: infer_schema(v, f"{path}.{k}") for k, v in data.items()
            },
        }
    elif isinstance(data, list):
        if data:
            return {"type": "array", "items": infer_schema(data[0], f"{path}[0]")}
        return {"type": "array"}
    elif isinstance(data, bool):
        return {"type": "boolean"}
    elif isinstance(data, int):
        return {"type": "integer"}
    elif isinstance(data, float):
        return {"type": "number"}
    elif isinstance(data, str):
        return {"type": "string"}
    return {"type": "null"}

def compare_schemas(documented: dict, actual: dict, path: str = "$") -> list:
    """Compare documented schema vs actual response schema."""
    issues = []
    doc_props = documented.get("properties", {})
    act_props = actual.get("properties", {})

    # Fields in actual but not documented
    for field in set(act_props.keys()) - set(doc_props.keys()):
        issues.append(f"UNDOCUMENTED field: {path}.{field}")

    # Fields documented but not in actual
    for field in set(doc_props.keys()) - set(act_props.keys()):
        issues.append(f"MISSING field: {path}.{field} (documented but not returned)")

    # Type mismatches
    for field in set(doc_props.keys()) & set(act_props.keys()):
        doc_type = doc_props[field].get("type")
        act_type = act_props[field].get("type")
        if doc_type != act_type:
            issues.append(
                f"TYPE MISMATCH: {path}.{field} "
                f"documented={doc_type}, actual={act_type}"
            )
        if doc_type == "object":
            issues.extend(
                compare_schemas(doc_props[field], act_props[field], f"{path}.{field}")
            )
    return issues
```

### Common Schema Accuracy Problems

| Problem | Detection | Fix |
|---------|-----------|-----|
| Undocumented fields returned | Response diff against schema | Add fields to spec |
| Documented fields missing | Schema validation fails | Remove from spec or fix API |
| Type mismatch (string vs integer) | Type comparison | Correct spec or API |
| Nullable not declared | Non-null constraint fails | Add `nullable: true` to spec |
| Enum value not listed | Enum validation fails | Expand enum in spec |
| Date format inconsistency | Format validation | Standardize on ISO 8601 |

---

## Endpoint Coverage Audit

Measure which endpoints are documented vs discovered through code analysis or traffic.

### Coverage Matrix

```bash
#!/bin/bash
# endpoint-coverage-audit.sh
# Compare discovered routes against documented endpoints

echo "=== Endpoint Coverage Audit ==="

# Extract routes from code (Express.js example)
echo "Discovering routes from code..."
grep -rn "router\.\(get\|post\|put\|patch\|delete\)" src/routes/ \
  | sed 's/.*router\.\(.*\)(\s*["'"'"']\(.*\)["'"'"'].*/\U\1 \2/' \
  | sort > /tmp/code-routes.txt

# Extract documented endpoints from OpenAPI spec
echo "Extracting documented endpoints..."
yq eval '.paths | keys[]' openapi.yaml | while read path; do
  yq eval ".paths[\"$path\"] | keys[]" openapi.yaml | while read method; do
    if [[ "$method" != "parameters" && "$method" != "summary" ]]; then
      echo "${method^^} $path"
    fi
  done
done | sort > /tmp/spec-routes.txt

# Compare
echo ""
echo "--- Documented but not in code (stale?) ---"
comm -23 /tmp/spec-routes.txt /tmp/code-routes.txt

echo ""
echo "--- In code but not documented (gap!) ---"
comm -13 /tmp/spec-routes.txt /tmp/code-routes.txt

echo ""
TOTAL_CODE=$(wc -l < /tmp/code-routes.txt)
TOTAL_SPEC=$(wc -l < /tmp/spec-routes.txt)
DOCUMENTED=$(comm -12 /tmp/spec-routes.txt /tmp/code-routes.txt | wc -l)
echo "Coverage: $DOCUMENTED / $TOTAL_CODE endpoints documented ($(( DOCUMENTED * 100 / TOTAL_CODE ))%)"
```

### Coverage Targets by Service Tier

| Service Tier | Endpoint Coverage | Schema Coverage | Example Coverage |
|-------------|-------------------|-----------------|------------------|
| Tier 1 (public API) | 100% | 100% | 100% with test validation |
| Tier 2 (internal API) | 95% | 90% | 80% |
| Tier 3 (admin/debug) | 80% | 70% | 50% |
| Tier 4 (deprecated) | Track only | -- | -- |

---

## Automated CI Checks for Doc Drift

Integrate documentation validation into your CI pipeline to prevent drift.

### GitHub Actions Workflow

```yaml
# .github/workflows/api-docs-validation.yaml
name: API Documentation Validation

on:
  pull_request:
    paths:
      - "src/routes/**"
      - "src/controllers/**"
      - "docs/openapi.yaml"
      - "docs/asyncapi.yaml"

jobs:
  lint-spec:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Lint OpenAPI spec
        uses: stoplightio/spectral-action@latest
        with:
          file_glob: "docs/openapi.yaml"
          spectral_ruleset: ".spectral.yaml"

  validate-examples:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 20

      - name: Install Prism
        run: npm install -g @stoplight/prism-cli

      - name: Start mock server and validate
        run: |
          prism mock docs/openapi.yaml --errors --port 4010 &
          sleep 3
          # Hit every documented endpoint and verify 2xx
          npx @schemathesis/cli run docs/openapi.yaml \
            --base-url http://localhost:4010 \
            --validate-schema true

  drift-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Generate spec from code
        run: npm run generate-spec

      - name: Check for drift
        run: |
          diff <(yq eval -P generated/openapi.yaml) \
               <(yq eval -P docs/openapi.yaml)
          if [ $? -ne 0 ]; then
            echo "::error::API spec drift detected. Regenerate docs."
            exit 1
          fi
```

### CI Validation Checklist

- [ ] Spectral lint passes with zero errors
- [ ] All documented examples validate against their schemas
- [ ] No spec drift between code-generated and committed specs
- [ ] Endpoint coverage does not decrease (ratchet)
- [ ] Breaking changes flagged (removed endpoints, changed schemas)
- [ ] Changelog entry required when spec changes

---

## Documentation-Code Sync Strategies

| Strategy | Description | Pros | Cons |
|----------|-------------|------|------|
| **Code-first** | Generate spec from code annotations (tsoa, springdoc, FastAPI) | Always in sync, single source of truth | Spec quality depends on annotation discipline |
| **Spec-first** | Write spec manually, generate code stubs | Better API design, contract-driven | Drift risk if implementation diverges |
| **Hybrid** | Spec-first for design, code-first for validation | Best of both worlds | More complex pipeline |
| **Traffic-based** | Generate spec from recorded API traffic | Captures actual behavior | Misses edge cases, no intent |

### Code-First Best Practices

```typescript
// FastAPI example: code annotations generate spec automatically
// This IS the documentation

from fastapi import FastAPI, Path, Query
from pydantic import BaseModel, Field
from datetime import datetime

class User(BaseModel):
    """A registered user in the system."""
    id: int = Field(..., description="Unique user identifier", example=123)
    name: str = Field(..., description="Full display name", example="Jane Doe")
    email: str = Field(..., description="Primary email address", example="jane@example.com")
    status: str = Field(..., description="Account status", example="active", enum=["active", "suspended", "deleted"])
    created_at: datetime = Field(..., description="Account creation timestamp")

@app.get(
    "/users/{user_id}",
    response_model=User,
    summary="Get user by ID",
    description="Retrieve a single user by their unique identifier.",
    responses={
        404: {"description": "User not found"},
        403: {"description": "Insufficient permissions"},
    },
)
async def get_user(
    user_id: int = Path(..., description="The user ID to retrieve", ge=1),
):
    ...
```

### Spec-First Best Practices

- Store the canonical spec in `docs/openapi.yaml`
- Generate server stubs with `openapi-generator`
- Generate client SDKs from the same spec
- Validate implementation against spec in integration tests
- Require spec review before merging code changes

---

## Tools Comparison

| Tool | Type | OpenAPI | AsyncAPI | CI Integration | Custom Rules | Pricing |
|------|------|---------|----------|----------------|--------------|---------|
| **Spectral** | Linter | 2.x, 3.x | 2.x | GitHub Action, npm | YAML rulesets | Free/OSS |
| **Redocly CLI** | Linter + Bundler | 2.x, 3.x | -- | GitHub Action, npm | YAML config | Free tier + paid |
| **Prism** | Mock + Proxy | 2.x, 3.x | -- | npm | -- | Free/OSS |
| **Schemathesis** | Fuzz tester | 2.x, 3.x | -- | Docker, pip | Python hooks | Free/OSS |
| **Optic** | Diff + Drift | 3.x | -- | GitHub Action | Custom checks | Free tier + paid |
| **openapi-diff** | Breaking change | 2.x, 3.x | -- | npm, Docker | -- | Free/OSS |
| **Swagger Coverage** | Coverage audit | 2.x | -- | Maven, Gradle | -- | Free/OSS |

---

## Related Resources

- [Discovery Patterns](./discovery-patterns.md) - Finding undocumented components
- [Freshness Tracking](./freshness-tracking.md) - Detecting stale documentation
- [CI/CD Integration](./cicd-integration.md) - Automation pipeline patterns
- [Documentation Quality Metrics](./documentation-quality-metrics.md) - Measuring doc health KPIs
- [Runbook Testing](./runbook-testing.md) - Validating operational runbooks
- [SKILL.md](../SKILL.md) - Parent skill overview
