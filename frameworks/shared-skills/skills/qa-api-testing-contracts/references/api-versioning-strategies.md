# API Versioning Strategies

Patterns for versioning APIs, detecting breaking changes, and automating backward compatibility verification across release cycles.

---

## Contents

- [Versioning Schemes](#versioning-schemes)
- [Semantic Versioning for APIs](#semantic-versioning-for-apis)
- [Breaking vs Non-Breaking Changes](#breaking-vs-non-breaking-changes)
- [Backward Compatibility Verification](#backward-compatibility-verification)
- [Deprecation Policy Design](#deprecation-policy-design)
- [Sunset Header Implementation](#sunset-header-implementation)
- [Consumer Notification Workflows](#consumer-notification-workflows)
- [Migration Testing Patterns](#migration-testing-patterns)
- [Version Matrix Testing](#version-matrix-testing)
- [OpenAPI Diff Tooling](#openapi-diff-tooling)
- [Versioning Checklist](#versioning-checklist)
- [Related Resources](#related-resources)

---

## Versioning Schemes

### Scheme Comparison

| Scheme | Format | Pros | Cons | Best For |
|--------|--------|------|------|----------|
| URL path | `/v1/users` | Explicit, cacheable, easy to route | URL pollution, hard to sunset | Public APIs |
| Header | `Accept: application/vnd.api.v1+json` | Clean URLs, flexible | Hidden from browser, harder to test | Internal APIs |
| Query param | `/users?version=1` | Easy to add, backward compatible | Caching issues, easy to forget | Legacy migration |
| Content negotiation | `Accept: application/json; version=1` | Standards-compliant | Complex client implementation | Hypermedia APIs |
| No versioning | `/users` (evolve in place) | Simple | Risky, requires strict compatibility | Additive-only APIs |

### URL Path Versioning (Recommended for Public APIs)

```python
# FastAPI example
from fastapi import FastAPI, APIRouter

app = FastAPI()

# Version 1
v1_router = APIRouter(prefix="/v1")

@v1_router.get("/users/{user_id}")
async def get_user_v1(user_id: int):
    return {"id": user_id, "name": "Alice", "email": "alice@example.com"}

# Version 2 - added 'role' field, restructured 'name'
v2_router = APIRouter(prefix="/v2")

@v2_router.get("/users/{user_id}")
async def get_user_v2(user_id: int):
    return {
        "id": user_id,
        "name": {"first": "Alice", "last": "Smith"},
        "email": "alice@example.com",
        "role": "admin",
    }

app.include_router(v1_router)
app.include_router(v2_router)
```

### Header-Based Versioning

```python
from fastapi import FastAPI, Header, HTTPException

app = FastAPI()

@app.get("/users/{user_id}")
async def get_user(
    user_id: int,
    accept: str = Header(default="application/vnd.myapi.v2+json"),
):
    if "v1" in accept:
        return {"id": user_id, "name": "Alice"}
    elif "v2" in accept:
        return {"id": user_id, "name": {"first": "Alice", "last": "Smith"}}
    else:
        raise HTTPException(406, "Unsupported API version")
```

```bash
# Client usage
curl -H "Accept: application/vnd.myapi.v1+json" https://api.example.com/users/42
curl -H "Accept: application/vnd.myapi.v2+json" https://api.example.com/users/42
```

---

## Semantic Versioning for APIs

### SemVer Applied to APIs

```text
MAJOR.MINOR.PATCH

MAJOR (v1 → v2): Breaking changes
  - Removed endpoints or fields
  - Changed field types
  - Changed authentication scheme
  - Restructured response shape

MINOR (v1.1 → v1.2): New features, backward compatible
  - Added new endpoints
  - Added optional fields to responses
  - Added optional query parameters
  - New enum values in responses

PATCH (v1.1.0 → v1.1.1): Bug fixes, no API changes
  - Fixed incorrect status codes
  - Fixed validation logic
  - Performance improvements
  - Documentation corrections
```

### Version Lifecycle

```text
┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
│  Alpha   │───▶│   Beta   │───▶│  Stable  │───▶│  Sunset  │───▶ Removed
│ (v3-alpha)│   │(v3-beta) │    │   (v3)   │    │  (v3)    │
└──────────┘    └──────────┘    └──────────┘    └──────────┘
                                     │
                                     │  v4 released
                                     ▼
                                ┌──────────┐
                                │Deprecated│
                                │   (v3)   │
                                └──────────┘
```

---

## Breaking vs Non-Breaking Changes

### Breaking Changes Catalog

| Change | Breaking? | Example |
|--------|-----------|---------|
| Remove endpoint | Yes | `DELETE /v1/legacy-endpoint` |
| Remove response field | Yes | Remove `user.email` from response |
| Rename response field | Yes | `user_name` to `username` |
| Change field type | Yes | `"age": "25"` to `"age": 25` |
| Change required params | Yes | Make optional param required |
| Narrow enum values | Yes | Remove valid enum option |
| Change error format | Yes | Different error response structure |
| Change auth scheme | Yes | API key to OAuth2 |
| Tighten validation | Yes | Reduce max length from 255 to 100 |
| Add required request field | Yes | New mandatory field in POST body |
| Add optional response field | No | New field with default |
| Add optional query param | No | New filter parameter |
| Widen enum values | No | Add new enum option |
| Add new endpoint | No | New resource route |
| Loosen validation | No | Increase max length |
| Add new HTTP method to existing route | No | Add PATCH to existing resource |

### Automated Breaking Change Detection

```python
def detect_breaking_changes(old_spec: dict, new_spec: dict) -> list[dict]:
    """Detect breaking changes between two OpenAPI specs."""
    breaking = []

    # Check removed endpoints
    old_paths = set(old_spec.get("paths", {}).keys())
    new_paths = set(new_spec.get("paths", {}).keys())
    for removed in old_paths - new_paths:
        breaking.append({
            "type": "endpoint_removed",
            "path": removed,
            "severity": "critical",
        })

    # Check each shared endpoint
    for path in old_paths & new_paths:
        old_methods = set(old_spec["paths"][path].keys())
        new_methods = set(new_spec["paths"][path].keys())

        for removed_method in old_methods - new_methods:
            breaking.append({
                "type": "method_removed",
                "path": path,
                "method": removed_method,
                "severity": "critical",
            })

        for method in old_methods & new_methods:
            # Check response schema changes
            changes = compare_response_schemas(
                old_spec["paths"][path][method],
                new_spec["paths"][path][method],
            )
            breaking.extend(changes)

    return breaking
```

---

## Backward Compatibility Verification

### Contract Test Suite

```python
import pytest
import requests

BASE_V1 = "https://api.example.com/v1"
BASE_V2 = "https://api.example.com/v2"

class TestBackwardCompatibility:
    """Verify v2 does not break v1 consumers."""

    def test_v1_response_fields_still_present(self):
        """All v1 response fields must still exist in v1 endpoint."""
        response = requests.get(f"{BASE_V1}/users/1")
        data = response.json()
        # These fields must always be present in v1
        assert "id" in data
        assert "name" in data
        assert "email" in data
        assert isinstance(data["name"], str)  # v1 uses flat string

    def test_v1_status_codes_unchanged(self):
        """v1 must return same status codes for same scenarios."""
        # Existing resource
        r = requests.get(f"{BASE_V1}/users/1")
        assert r.status_code == 200

        # Missing resource
        r = requests.get(f"{BASE_V1}/users/999999")
        assert r.status_code == 404

        # Invalid input
        r = requests.get(f"{BASE_V1}/users/abc")
        assert r.status_code in (400, 422)

    def test_v1_pagination_contract_preserved(self):
        """Pagination structure must not change in v1."""
        r = requests.get(f"{BASE_V1}/users?page=1&per_page=10")
        data = r.json()
        assert "data" in data
        assert "meta" in data
        assert "total" in data["meta"]
        assert "page" in data["meta"]
```

### Compatibility Test Matrix

```bash
#!/bin/bash
# run_compat_matrix.sh - Test all supported version combinations

VERSIONS=("v1" "v2" "v3")
RESULTS=()

for version in "${VERSIONS[@]}"; do
    echo "Testing $version compatibility..."
    pytest tests/compatibility/ \
        --api-version="$version" \
        --junitxml="reports/compat_${version}.xml" \
        2>&1

    if [ $? -eq 0 ]; then
        RESULTS+=("$version: PASS")
    else
        RESULTS+=("$version: FAIL")
    fi
done

echo ""
echo "=== Compatibility Matrix Results ==="
for result in "${RESULTS[@]}"; do
    echo "  $result"
done
```

---

## Deprecation Policy Design

### Deprecation Timeline Template

```text
Phase 1: Announce (Month 0)
  - Add Deprecation header to responses
  - Update API documentation
  - Notify consumers via email/changelog
  - Provide migration guide

Phase 2: Warning Period (Months 1-3)
  - Log usage of deprecated endpoints
  - Send targeted notifications to active consumers
  - Add Sunset header with target date

Phase 3: Soft Sunset (Month 4-5)
  - Return warning in response body
  - Throttle deprecated endpoint (optional)
  - Final migration reminders

Phase 4: Hard Sunset (Month 6)
  - Return 410 Gone status
  - Include migration URL in response body
  - Remove from documentation
```

### Deprecation Headers

```http
HTTP/1.1 200 OK
Deprecation: true
Sunset: Sat, 01 Mar 2026 00:00:00 GMT
Link: <https://api.example.com/v2/users>; rel="successor-version"

{
  "data": { ... },
  "_deprecation": {
    "message": "This endpoint is deprecated. Use /v2/users instead.",
    "sunset_date": "2026-03-01",
    "migration_guide": "https://docs.example.com/migration/v1-to-v2"
  }
}
```

---

## Sunset Header Implementation

```python
from fastapi import FastAPI, Response
from datetime import datetime

app = FastAPI()

SUNSET_DATES = {
    "v1": datetime(2026, 3, 1),
    "v2": None,  # Current version, no sunset
}

def add_deprecation_headers(response: Response, version: str):
    """Add standard deprecation and sunset headers."""
    sunset = SUNSET_DATES.get(version)
    if sunset:
        response.headers["Deprecation"] = "true"
        response.headers["Sunset"] = sunset.strftime("%a, %d %b %Y %H:%M:%S GMT")
        response.headers["Link"] = (
            f'<https://api.example.com/v{int(version[1:])+1}/users>; '
            f'rel="successor-version"'
        )

@app.get("/v1/users/{user_id}")
async def get_user_v1(user_id: int, response: Response):
    add_deprecation_headers(response, "v1")
    return {"id": user_id, "name": "Alice"}
```

---

## Consumer Notification Workflows

| Event | Channel | Audience | Timing |
|-------|---------|----------|--------|
| New version released | Changelog, email, developer portal | All consumers | Immediate |
| Version deprecated | Email, in-API header, dashboard alert | Active consumers of old version | Day 0 of deprecation |
| 30 days to sunset | Email, webhook notification | Active consumers of deprecated version | 30 days before |
| 7 days to sunset | Email, SMS/Slack for high-volume consumers | Still-active consumers | 7 days before |
| Version sunset | 410 Gone response, email confirmation | Remaining consumers | Sunset day |

### Consumer Usage Tracking

```python
def track_version_usage(version: str, consumer_id: str):
    """Track which consumers are using which versions."""
    redis_client.hincrby(f"api_usage:{version}", consumer_id, 1)
    redis_client.sadd(f"active_consumers:{version}", consumer_id)
    redis_client.expire(f"active_consumers:{version}", 86400 * 30)

def get_consumers_needing_migration(deprecated_version: str) -> set:
    """Find consumers still using a deprecated version."""
    return redis_client.smembers(f"active_consumers:{deprecated_version}")
```

---

## Migration Testing Patterns

### Response Shape Migration Test

```python
def test_v1_to_v2_migration_path(api_client):
    """Verify consumers can migrate from v1 to v2."""
    # Get v1 response
    v1_response = api_client.get("/v1/users/1").json()

    # Get v2 response
    v2_response = api_client.get("/v2/users/1").json()

    # All v1 data must be derivable from v2
    assert v2_response["id"] == v1_response["id"]
    assert v2_response["email"] == v1_response["email"]

    # v1 'name' (string) maps to v2 'name.first' + 'name.last'
    full_name = f"{v2_response['name']['first']} {v2_response['name']['last']}"
    assert full_name == v1_response["name"]

def test_v1_to_v2_request_compatibility(api_client):
    """Verify v1 request format works or returns helpful error in v2."""
    v1_payload = {"name": "Alice Smith", "email": "alice@example.com"}

    response = api_client.post("/v2/users", json=v1_payload)

    # v2 should either accept the old format or return actionable error
    if response.status_code == 422:
        error = response.json()
        assert "migration" in str(error).lower() or "name.first" in str(error)
```

---

## Version Matrix Testing

### Multi-Version CI Pipeline

```yaml
# .github/workflows/version-compat.yml
name: API Version Compatibility

on:
  push:
    paths: ['src/api/**']

jobs:
  compatibility:
    strategy:
      matrix:
        api_version: [v1, v2, v3]
        client_version: [v1, v2, v3]
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Start API server
        run: docker compose up -d api
      - name: Run compatibility tests
        run: |
          pytest tests/compatibility/ \
            --server-version=${{ matrix.api_version }} \
            --client-version=${{ matrix.client_version }} \
            --junitxml=reports/${{ matrix.api_version }}_${{ matrix.client_version }}.xml
      - name: Upload results
        uses: actions/upload-artifact@v4
        with:
          name: compat-${{ matrix.api_version }}-${{ matrix.client_version }}
          path: reports/
```

### Compatibility Matrix Visualization

```text
           Server Version
           v1      v2      v3
Client v1  PASS    PASS    FAIL*
Client v2  N/A     PASS    PASS
Client v3  N/A     N/A     PASS

* v1 client + v3 server: Expected failure (v1 sunset)
```

---

## OpenAPI Diff Tooling

### oasdiff (Recommended)

```bash
# Install
go install github.com/tufin/oasdiff@latest

# Detect breaking changes
oasdiff breaking old-api.yaml new-api.yaml

# Full changelog diff
oasdiff changelog old-api.yaml new-api.yaml

# Output as JSON for CI
oasdiff breaking old-api.yaml new-api.yaml --format json

# Fail CI on breaking changes
oasdiff breaking old-api.yaml new-api.yaml --fail-on ERR
```

### Optic

```bash
# Install
npm install -g @useoptic/optic

# Compare specs
optic diff old-api.yaml new-api.yaml

# CI integration - check for breaking changes
optic diff old-api.yaml new-api.yaml --check
```

### CI Integration Example

```bash
#!/bin/bash
# check_api_compat.sh - Run in CI before merge

set -euo pipefail

OLD_SPEC="main:openapi/spec.yaml"
NEW_SPEC="openapi/spec.yaml"

echo "Checking for breaking changes..."
BREAKING=$(oasdiff breaking "$OLD_SPEC" "$NEW_SPEC" --format json 2>&1)

if [ "$(echo "$BREAKING" | jq length)" -gt 0 ]; then
    echo "BREAKING CHANGES DETECTED:"
    echo "$BREAKING" | jq -r '.[].message'
    echo ""
    echo "If intentional, bump the major version and update migration guide."
    exit 1
fi

echo "No breaking changes detected. Safe to merge."
```

---

## Versioning Checklist

- [ ] Versioning scheme selected and documented
- [ ] Breaking change detection automated in CI (oasdiff or optic)
- [ ] Backward compatibility test suite covers all supported versions
- [ ] Deprecation policy written with clear timelines
- [ ] Sunset headers implemented for deprecated versions
- [ ] Consumer usage tracking in place
- [ ] Migration guide published for each major version bump
- [ ] Version matrix testing runs in CI
- [ ] Notification workflow configured for deprecation events
- [ ] 410 Gone responses configured for sunset versions
- [ ] OpenAPI spec versioned alongside code

---

## Related Resources

- **[contract-testing-patterns.md](contract-testing-patterns.md)** - Consumer-driven contract testing
- **[schema-driven-testing.md](schema-driven-testing.md)** - Schema-based test generation
- **[ai-contract-testing.md](ai-contract-testing.md)** - AI-specific contract testing
- **[SKILL.md](../SKILL.md)** - QA API Testing & Contracts skill overview
