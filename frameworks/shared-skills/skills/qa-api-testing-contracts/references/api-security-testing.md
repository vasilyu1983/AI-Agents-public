# API Security Testing

Systematic API security testing aligned with the OWASP API Security Top 10 (2023), covering authentication, authorization, injection, and automated scanning patterns.

---

## Contents

- [OWASP API Security Top 10 Overview](#owasp-api-security-top-10-overview)
- [BOLA Testing (Broken Object Level Authorization)](#bola-testing)
- [BFLA Testing (Broken Function Level Authorization)](#bfla-testing)
- [Authentication Testing](#authentication-testing)
- [Rate Limiting Verification](#rate-limiting-verification)
- [Injection Testing](#injection-testing)
- [Mass Assignment Testing](#mass-assignment-testing)
- [SSRF Prevention Testing](#ssrf-prevention-testing)
- [Security Headers Validation](#security-headers-validation)
- [API Key Management Testing](#api-key-management-testing)
- [Automated Security Scanning](#automated-security-scanning)
- [Security Testing Checklist](#security-testing-checklist)
- [Related Resources](#related-resources)

---

## OWASP API Security Top 10 Overview

| # | Risk | Test Priority | Automated? |
|---|------|--------------|------------|
| API1 | Broken Object Level Authorization (BOLA) | P0 | Partial |
| API2 | Broken Authentication | P0 | Yes |
| API3 | Broken Object Property Level Authorization | P0 | Partial |
| API4 | Unrestricted Resource Consumption | P1 | Yes |
| API5 | Broken Function Level Authorization (BFLA) | P0 | Partial |
| API6 | Unrestricted Access to Sensitive Business Flows | P1 | Partial |
| API7 | Server Side Request Forgery (SSRF) | P1 | Yes |
| API8 | Security Misconfiguration | P1 | Yes |
| API9 | Improper Inventory Management | P2 | Partial |
| API10 | Unsafe Consumption of APIs | P2 | No |

---

## BOLA Testing

Broken Object Level Authorization: accessing another user's resources by changing the object ID.

### Test Patterns

```python
import pytest
import requests

class TestBOLA:
    """Test that users cannot access other users' resources."""

    def setup_method(self):
        self.user_a_token = get_token("user_a@example.com")
        self.user_b_token = get_token("user_b@example.com")

        # Create a resource owned by user_a
        r = requests.post(
            f"{BASE_URL}/orders",
            json={"item": "widget", "quantity": 1},
            headers={"Authorization": f"Bearer {self.user_a_token}"},
        )
        self.user_a_order_id = r.json()["id"]

    def test_cannot_read_other_users_order(self):
        """User B must not access User A's order."""
        r = requests.get(
            f"{BASE_URL}/orders/{self.user_a_order_id}",
            headers={"Authorization": f"Bearer {self.user_b_token}"},
        )
        assert r.status_code == 403 or r.status_code == 404

    def test_cannot_update_other_users_order(self):
        """User B must not modify User A's order."""
        r = requests.patch(
            f"{BASE_URL}/orders/{self.user_a_order_id}",
            json={"quantity": 999},
            headers={"Authorization": f"Bearer {self.user_b_token}"},
        )
        assert r.status_code in (403, 404)

    def test_cannot_delete_other_users_order(self):
        """User B must not delete User A's order."""
        r = requests.delete(
            f"{BASE_URL}/orders/{self.user_a_order_id}",
            headers={"Authorization": f"Bearer {self.user_b_token}"},
        )
        assert r.status_code in (403, 404)

    def test_id_enumeration_does_not_leak_data(self):
        """Sequential ID enumeration must not reveal other users' data."""
        for offset in range(-5, 6):
            test_id = self.user_a_order_id + offset
            r = requests.get(
                f"{BASE_URL}/orders/{test_id}",
                headers={"Authorization": f"Bearer {self.user_b_token}"},
            )
            if r.status_code == 200:
                # If accessible, it must belong to user_b
                assert r.json()["owner_id"] == "user_b"
```

### BOLA Test Matrix

| Resource | GET | PUT/PATCH | DELETE | List/Filter |
|----------|-----|-----------|--------|-------------|
| /users/{id} | Test cross-user access | Test cross-user update | Test cross-user delete | Test listing shows only own |
| /orders/{id} | Same | Same | Same | Same |
| /documents/{id} | Same | Same | Same | Same |
| /payments/{id} | Same | Same | N/A | Same |

---

## BFLA Testing

Broken Function Level Authorization: accessing admin or privileged endpoints as a regular user.

```python
class TestBFLA:
    """Test that role-based access control is enforced."""

    def setup_method(self):
        self.admin_token = get_token("admin@example.com")
        self.user_token = get_token("user@example.com")
        self.readonly_token = get_token("viewer@example.com")

    ADMIN_ENDPOINTS = [
        ("GET", "/admin/users"),
        ("POST", "/admin/users"),
        ("DELETE", "/admin/users/1"),
        ("POST", "/admin/settings"),
        ("GET", "/admin/audit-logs"),
        ("POST", "/admin/export"),
    ]

    @pytest.mark.parametrize("method,path", ADMIN_ENDPOINTS)
    def test_regular_user_cannot_access_admin(self, method, path):
        """Regular users must be denied access to admin endpoints."""
        r = requests.request(
            method, f"{BASE_URL}{path}",
            headers={"Authorization": f"Bearer {self.user_token}"},
            json={} if method in ("POST", "PUT") else None,
        )
        assert r.status_code in (401, 403), (
            f"User accessed admin endpoint: {method} {path} -> {r.status_code}"
        )

    WRITE_ENDPOINTS = [
        ("POST", "/orders"),
        ("PATCH", "/orders/1"),
        ("DELETE", "/orders/1"),
        ("POST", "/documents"),
    ]

    @pytest.mark.parametrize("method,path", WRITE_ENDPOINTS)
    def test_readonly_cannot_write(self, method, path):
        """Read-only users must be denied write operations."""
        r = requests.request(
            method, f"{BASE_URL}{path}",
            headers={"Authorization": f"Bearer {self.readonly_token}"},
            json={} if method in ("POST", "PUT", "PATCH") else None,
        )
        assert r.status_code in (401, 403)

    def test_privilege_escalation_via_body(self):
        """Users cannot escalate their own role via request body."""
        r = requests.patch(
            f"{BASE_URL}/users/me",
            json={"role": "admin"},
            headers={"Authorization": f"Bearer {self.user_token}"},
        )
        # Either rejected or role field ignored
        if r.status_code == 200:
            assert r.json()["role"] != "admin"
```

---

## Authentication Testing

### JWT Validation Tests

```python
import jwt
import time

class TestJWTAuthentication:

    def test_expired_token_rejected(self):
        """Expired JWTs must be rejected."""
        expired_token = jwt.encode(
            {"sub": "user_1", "exp": int(time.time()) - 3600},
            SECRET_KEY, algorithm="HS256",
        )
        r = requests.get(
            f"{BASE_URL}/users/me",
            headers={"Authorization": f"Bearer {expired_token}"},
        )
        assert r.status_code == 401

    def test_tampered_token_rejected(self):
        """Tokens signed with wrong key must be rejected."""
        bad_token = jwt.encode(
            {"sub": "user_1", "exp": int(time.time()) + 3600},
            "wrong_secret_key", algorithm="HS256",
        )
        r = requests.get(
            f"{BASE_URL}/users/me",
            headers={"Authorization": f"Bearer {bad_token}"},
        )
        assert r.status_code == 401

    def test_none_algorithm_rejected(self):
        """JWT 'none' algorithm attack must be rejected."""
        header = {"alg": "none", "typ": "JWT"}
        payload = {"sub": "admin", "exp": int(time.time()) + 3600}
        # Manually construct unsigned token
        import base64, json
        h = base64.urlsafe_b64encode(json.dumps(header).encode()).rstrip(b"=")
        p = base64.urlsafe_b64encode(json.dumps(payload).encode()).rstrip(b"=")
        none_token = f"{h.decode()}.{p.decode()}."

        r = requests.get(
            f"{BASE_URL}/users/me",
            headers={"Authorization": f"Bearer {none_token}"},
        )
        assert r.status_code == 401

    def test_missing_token_returns_401(self):
        """Requests without auth token must return 401."""
        r = requests.get(f"{BASE_URL}/users/me")
        assert r.status_code == 401

    def test_refresh_token_rotation(self):
        """Used refresh tokens must be invalidated after rotation."""
        # Get initial token pair
        r = requests.post(f"{BASE_URL}/auth/login", json={
            "email": "user@example.com", "password": "password123"
        })
        refresh_token = r.json()["refresh_token"]

        # Use refresh token
        r = requests.post(f"{BASE_URL}/auth/refresh", json={
            "refresh_token": refresh_token
        })
        assert r.status_code == 200

        # Reuse same refresh token (must fail)
        r = requests.post(f"{BASE_URL}/auth/refresh", json={
            "refresh_token": refresh_token
        })
        assert r.status_code == 401
```

---

## Rate Limiting Verification

```python
import time
from concurrent.futures import ThreadPoolExecutor

class TestRateLimiting:

    def test_rate_limit_enforced(self):
        """Verify rate limit headers and enforcement."""
        responses = []
        for _ in range(110):  # Exceed 100/min limit
            r = requests.get(
                f"{BASE_URL}/users",
                headers={"Authorization": f"Bearer {self.token}"},
            )
            responses.append(r)

        # Verify headers present
        assert "X-RateLimit-Limit" in responses[0].headers
        assert "X-RateLimit-Remaining" in responses[0].headers

        # Some requests should be rate-limited
        status_codes = [r.status_code for r in responses]
        assert 429 in status_codes, "Rate limit was never triggered"

        # 429 response must include Retry-After
        limited = [r for r in responses if r.status_code == 429]
        assert "Retry-After" in limited[0].headers

    def test_rate_limit_per_user_not_global(self):
        """Rate limiting one user must not affect another."""
        # Exhaust user_a's limit
        for _ in range(110):
            requests.get(
                f"{BASE_URL}/users",
                headers={"Authorization": f"Bearer {self.user_a_token}"},
            )

        # User_b should still have quota
        r = requests.get(
            f"{BASE_URL}/users",
            headers={"Authorization": f"Bearer {self.user_b_token}"},
        )
        assert r.status_code == 200

    def test_brute_force_login_protection(self):
        """Login endpoint must have strict rate limiting."""
        for i in range(20):
            r = requests.post(f"{BASE_URL}/auth/login", json={
                "email": "target@example.com",
                "password": f"wrong_password_{i}",
            })

        # Should be rate-limited or locked
        assert r.status_code in (429, 423)
```

---

## Injection Testing

### SQL Injection

```python
SQL_INJECTION_PAYLOADS = [
    "' OR '1'='1",
    "'; DROP TABLE users; --",
    "1 UNION SELECT username, password FROM users--",
    "admin'--",
    "1; WAITFOR DELAY '0:0:5'--",
]

@pytest.mark.parametrize("payload", SQL_INJECTION_PAYLOADS)
def test_sql_injection_blocked(api_client, payload):
    """SQL injection payloads must not alter query behavior."""
    r = api_client.get(f"/users?search={payload}")
    assert r.status_code in (200, 400, 422)  # Never 500
    # Verify no unexpected data returned
    if r.status_code == 200:
        data = r.json()
        # Should not return all users (injection success indicator)
        assert len(data.get("data", [])) <= 10
```

### NoSQL Injection

```python
NOSQL_INJECTION_PAYLOADS = [
    {"email": {"$gt": ""}, "password": {"$gt": ""}},
    {"email": {"$ne": "nonexistent"}, "password": {"$ne": "wrong"}},
    {"email": {"$regex": ".*"}, "password": {"$regex": ".*"}},
    {"$where": "this.email == this.email"},
]

@pytest.mark.parametrize("payload", NOSQL_INJECTION_PAYLOADS)
def test_nosql_injection_blocked(api_client, payload):
    """NoSQL injection payloads must be rejected."""
    r = api_client.post("/auth/login", json=payload)
    assert r.status_code != 200, "NoSQL injection may have succeeded"
```

### Command Injection

```python
COMMAND_INJECTION_PAYLOADS = [
    "; ls -la",
    "| cat /etc/passwd",
    "$(whoami)",
    "`id`",
    "& ping -c 10 127.0.0.1",
]

@pytest.mark.parametrize("payload", COMMAND_INJECTION_PAYLOADS)
def test_command_injection_blocked(api_client, payload):
    """Command injection via API parameters must be blocked."""
    r = api_client.post("/tools/convert", json={"filename": payload})
    assert r.status_code in (400, 422)
    # Verify no command execution indicators in response
    assert "/root" not in r.text
    assert "uid=" not in r.text
```

---

## Mass Assignment Testing

```python
class TestMassAssignment:
    """Test that APIs reject unexpected fields that could modify protected attributes."""

    def test_cannot_set_admin_via_registration(self):
        """Registration must ignore role/admin fields."""
        r = requests.post(f"{BASE_URL}/auth/register", json={
            "email": "newuser@example.com",
            "password": "SecureP@ss123",
            "name": "New User",
            "role": "admin",             # Mass assignment attempt
            "is_admin": True,            # Mass assignment attempt
            "subscription": "enterprise", # Mass assignment attempt
        })
        if r.status_code == 201:
            user = r.json()
            assert user.get("role") != "admin"
            assert user.get("is_admin") is not True
            assert user.get("subscription") != "enterprise"

    def test_cannot_modify_protected_fields_via_update(self):
        """Profile update must ignore protected fields."""
        r = requests.patch(
            f"{BASE_URL}/users/me",
            json={
                "name": "Updated Name",
                "id": 1,                    # Cannot change own ID
                "created_at": "2020-01-01", # Cannot backdate
                "email_verified": True,      # Cannot self-verify
            },
            headers={"Authorization": f"Bearer {self.user_token}"},
        )
        if r.status_code == 200:
            user = r.json()
            assert user["id"] != 1 or user["id"] == self.original_user_id
            assert user.get("email_verified") != True  # noqa
```

---

## SSRF Prevention Testing

```python
SSRF_PAYLOADS = [
    "http://127.0.0.1/admin",
    "http://localhost/admin",
    "http://0.0.0.0/",
    "http://169.254.169.254/latest/meta-data/",  # AWS metadata
    "http://[::1]/admin",
    "http://metadata.google.internal/",           # GCP metadata
    "http://100.100.100.200/latest/meta-data/",   # Alibaba metadata
    "file:///etc/passwd",
    "gopher://127.0.0.1:6379/_INFO",
]

@pytest.mark.parametrize("url", SSRF_PAYLOADS)
def test_ssrf_blocked(api_client, url):
    """Server must not fetch internal/metadata URLs."""
    r = api_client.post("/tools/fetch-url", json={"url": url})
    assert r.status_code in (400, 403, 422), (
        f"SSRF may have succeeded for {url}: status={r.status_code}"
    )
    # Verify no internal data leaked
    assert "ami-id" not in r.text        # AWS metadata indicator
    assert "root:" not in r.text         # /etc/passwd indicator
    assert "instance-id" not in r.text   # Cloud metadata indicator
```

---

## Security Headers Validation

```python
def test_security_headers_present(api_client):
    """Verify required security headers on all API responses."""
    r = api_client.get("/users")
    headers = r.headers

    # Required headers
    assert headers.get("X-Content-Type-Options") == "nosniff"
    assert headers.get("X-Frame-Options") in ("DENY", "SAMEORIGIN")
    assert "strict-transport-security" in {k.lower() for k in headers}
    assert headers.get("Cache-Control") in (
        "no-store", "no-cache, no-store, must-revalidate"
    )

    # Must NOT expose
    assert "Server" not in headers or headers["Server"] == ""
    assert "X-Powered-By" not in headers
    assert "X-AspNet-Version" not in headers

    # CORS headers (if applicable)
    assert headers.get("Access-Control-Allow-Origin") != "*" or \
        "authenticated endpoint should not use wildcard CORS"
```

### Security Headers Reference

| Header | Required Value | Purpose |
|--------|---------------|---------|
| `X-Content-Type-Options` | `nosniff` | Prevent MIME sniffing |
| `X-Frame-Options` | `DENY` | Prevent clickjacking |
| `Strict-Transport-Security` | `max-age=31536000; includeSubDomains` | Force HTTPS |
| `Cache-Control` | `no-store` | Prevent caching sensitive responses |
| `Content-Security-Policy` | Appropriate policy | Prevent XSS |
| `X-XSS-Protection` | `0` (rely on CSP) | Legacy XSS filter |

---

## API Key Management Testing

```python
class TestAPIKeyManagement:

    def test_key_in_url_rejected(self):
        """API keys in URL query params should be rejected (log exposure risk)."""
        r = requests.get(f"{BASE_URL}/users?api_key=test_key_123")
        assert r.status_code in (400, 401), \
            "API key in URL should be rejected"

    def test_revoked_key_rejected(self):
        """Revoked API keys must be immediately rejected."""
        # Create and revoke a key
        key = create_api_key("test_user")
        revoke_api_key(key)

        r = requests.get(
            f"{BASE_URL}/users",
            headers={"X-API-Key": key},
        )
        assert r.status_code == 401

    def test_key_scoping_enforced(self):
        """API keys must only access their permitted scopes."""
        readonly_key = create_api_key("test_user", scopes=["read"])

        # Read should work
        r = requests.get(
            f"{BASE_URL}/users",
            headers={"X-API-Key": readonly_key},
        )
        assert r.status_code == 200

        # Write should be rejected
        r = requests.post(
            f"{BASE_URL}/users",
            json={"name": "test"},
            headers={"X-API-Key": readonly_key},
        )
        assert r.status_code == 403

    def test_key_not_leaked_in_error_responses(self):
        """API key must never appear in error response bodies."""
        key = "sk_test_secret_key_12345"
        r = requests.get(
            f"{BASE_URL}/nonexistent",
            headers={"X-API-Key": key},
        )
        assert key not in r.text
```

---

## Automated Security Scanning

### OWASP ZAP Integration

```bash
# Pull ZAP Docker image
docker pull zaproxy/zap-stable

# API scan using OpenAPI spec
docker run --rm -v $(pwd):/zap/wrk zaproxy/zap-stable \
    zap-api-scan.py \
    -t http://host.docker.internal:8000/openapi.json \
    -f openapi \
    -r /zap/wrk/reports/zap-report.html \
    -J /zap/wrk/reports/zap-report.json \
    -c /zap/wrk/zap-config.conf

# Baseline scan (passive only)
docker run --rm -v $(pwd):/zap/wrk zaproxy/zap-stable \
    zap-baseline.py \
    -t http://host.docker.internal:8000 \
    -r /zap/wrk/reports/baseline.html
```

### CI Pipeline Integration

```yaml
# .github/workflows/security-scan.yml
name: API Security Scan

on:
  push:
    branches: [main]
  schedule:
    - cron: '0 2 * * 1'  # Weekly Monday 2AM

jobs:
  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Start API
        run: docker compose up -d api
      - name: Wait for API
        run: |
          for i in {1..30}; do
            curl -s http://localhost:8000/health && break
            sleep 2
          done
      - name: Run OWASP ZAP
        run: |
          docker run --rm --network host \
            -v ${{ github.workspace }}:/zap/wrk \
            zaproxy/zap-stable \
            zap-api-scan.py \
            -t http://localhost:8000/openapi.json \
            -f openapi \
            -J /zap/wrk/zap-results.json
      - name: Check for high severity findings
        run: |
          HIGH=$(jq '[.site[].alerts[] | select(.riskcode >= 3)] | length' zap-results.json)
          if [ "$HIGH" -gt 0 ]; then
            echo "HIGH/CRITICAL findings detected: $HIGH"
            jq '.site[].alerts[] | select(.riskcode >= 3) | .name' zap-results.json
            exit 1
          fi
```

---

## Security Testing Checklist

- [ ] BOLA: Cross-user access tested for all resource endpoints
- [ ] BFLA: Admin endpoints blocked for regular users
- [ ] BFLA: Write endpoints blocked for read-only users
- [ ] JWT: Expired, tampered, and none-algorithm tokens rejected
- [ ] JWT: Refresh token rotation and reuse detection verified
- [ ] Rate limiting: Enforced per-user on all endpoints
- [ ] Rate limiting: Login endpoint has strict limits
- [ ] SQL injection: Parameterized queries verified, payloads tested
- [ ] NoSQL injection: Operator injection payloads rejected
- [ ] Command injection: Payloads in all user-controlled parameters tested
- [ ] Mass assignment: Protected fields not modifiable via API
- [ ] SSRF: Internal and cloud metadata URLs blocked
- [ ] Security headers: All required headers present
- [ ] API keys: Not accepted in URL params, revocation works
- [ ] Automated scan: OWASP ZAP or Burp Suite run in CI
- [ ] No sensitive data in error responses
- [ ] HTTPS enforced, no HTTP fallback

---

## Related Resources

- **[contract-testing-patterns.md](contract-testing-patterns.md)** - Contract testing fundamentals
- **[schema-driven-testing.md](schema-driven-testing.md)** - Schema-based fuzzing and validation
- **[api-versioning-strategies.md](api-versioning-strategies.md)** - Versioning and deprecation
- **[SKILL.md](../SKILL.md)** - QA API Testing & Contracts skill overview
