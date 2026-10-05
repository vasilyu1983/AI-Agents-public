# Security Regression Testing Guide

Writing targeted test cases that prevent reintroduction of fixed vulnerabilities. Covers auth boundary tests, input validation, IDOR prevention, and security header verification.

## Table of Contents

- [Purpose](#purpose)
- [Auth Boundary Tests](#auth-boundary-tests)
- [IDOR (Insecure Direct Object Reference) Prevention](#idor-insecure-direct-object-reference-prevention)
- [test_auth_boundaries.py](#testauthboundariespy)
- [Privilege Escalation Prevention](#privilege-escalation-prevention)
- [Input Validation Tests](#input-validation-tests)
- [SQL Injection Prevention](#sql-injection-prevention)
- [XSS Prevention](#xss-prevention)
- [Path Traversal Prevention](#path-traversal-prevention)
- [Security Header Verification](#security-header-verification)
- [Test Organization](#test-organization)
- [Structure](#structure)
- [Naming Convention](#naming-convention)
- [Running in CI](#running-in-ci)
- [No separate security test job needed](#no-separate-security-test-job-needed)
- [Writing New Regression Tests](#writing-new-regression-tests)

## Purpose

Every confirmed vulnerability should produce a regression test. These tests:

- Prevent the same vulnerability from being reintroduced.
- Document the exact attack vector for future developers.
- Run in the standard test suite on every PR (not a separate security run).
- Serve as living documentation of past security issues.

## Auth Boundary Tests

### IDOR (Insecure Direct Object Reference) Prevention

```python
# test_auth_boundaries.py
import pytest

class TestIDORPrevention:
    """Verify users cannot access other users' resources."""

    def test_user_cannot_access_other_user_profile(self, client, user_a_token, user_b):
        """Regression: CVE-INTERNAL-2025-042 - profile endpoint IDOR."""
        response = client.get(
            f"/api/users/{user_b.id}/profile",
            headers={"Authorization": f"Bearer {user_a_token}"}
        )
        assert response.status_code == 403

    def test_user_cannot_list_other_org_resources(self, client, user_a_token, org_b):
        """Regression: VULN-2025-088 - org resource enumeration."""
        response = client.get(
            f"/api/orgs/{org_b.id}/documents",
            headers={"Authorization": f"Bearer {user_a_token}"}
        )
        assert response.status_code == 403

    def test_sequential_id_enumeration_blocked(self, client, user_a_token):
        """Verify sequential ID guessing does not leak data."""
        for resource_id in range(1, 20):
            response = client.get(
                f"/api/documents/{resource_id}",
                headers={"Authorization": f"Bearer {user_a_token}"}
            )
            assert response.status_code in (403, 404)
```

### Privilege Escalation Prevention

```python
class TestPrivilegeEscalation:
    """Verify role boundaries are enforced."""

    def test_standard_user_cannot_access_admin_endpoint(self, client, user_token):
        response = client.get(
            "/api/admin/users",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        assert response.status_code == 403

    def test_standard_user_cannot_modify_roles(self, client, user_token, user_id):
        response = client.patch(
            f"/api/users/{user_id}",
            json={"role": "admin"},
            headers={"Authorization": f"Bearer {user_token}"}
        )
        assert response.status_code == 403

    def test_unauthenticated_access_blocked(self, client):
        """All protected endpoints return 401 without auth."""
        protected_endpoints = [
            "/api/users/me",
            "/api/documents",
            "/api/admin/settings",
        ]
        for endpoint in protected_endpoints:
            response = client.get(endpoint)
            assert response.status_code == 401, f"{endpoint} accessible without auth"
```

## Input Validation Tests

### SQL Injection Prevention

```python
class TestSQLInjectionPrevention:
    """Verify parameterized queries prevent injection."""

    @pytest.mark.parametrize("payload", [
        "'; DROP TABLE users; --",
        "' OR '1'='1",
        "' UNION SELECT * FROM credentials --",
        "1; WAITFOR DELAY '0:0:5' --",
    ])
    def test_search_endpoint_resists_sqli(self, client, auth_headers, payload):
        response = client.get(
            f"/api/search?q={payload}",
            headers=auth_headers
        )
        assert response.status_code in (200, 400)
        # Verify no data leakage in response
        assert "credentials" not in response.text.lower()
```

### XSS Prevention

```python
class TestXSSPrevention:
    """Verify output encoding prevents XSS."""

    @pytest.mark.parametrize("payload", [
        '<script>alert("xss")</script>',
        '<img src=x onerror=alert(1)>',
        '"><svg onload=alert(1)>',
        "javascript:alert(1)",
    ])
    def test_user_input_is_encoded_in_response(self, client, auth_headers, payload):
        # Submit payload as user input
        client.post(
            "/api/comments",
            json={"body": payload},
            headers=auth_headers
        )
        # Retrieve and verify encoding
        response = client.get("/api/comments", headers=auth_headers)
        assert "<script>" not in response.text
        assert "onerror=" not in response.text
```

### Path Traversal Prevention

```python
class TestPathTraversalPrevention:
    """Verify file access is constrained to allowed directories."""

    @pytest.mark.parametrize("payload", [
        "../../../etc/passwd",
        "..\\..\\..\\windows\\system32\\config\\sam",
        "%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd",
        "....//....//....//etc/passwd",
    ])
    def test_file_download_resists_traversal(self, client, auth_headers, payload):
        response = client.get(
            f"/api/files/{payload}",
            headers=auth_headers
        )
        assert response.status_code in (400, 404)
```

## Security Header Verification

```python
class TestSecurityHeaders:
    """Verify security headers are present on all responses."""

    def test_security_headers_present(self, client):
        response = client.get("/")
        headers = response.headers

        # Content Security Policy
        assert "content-security-policy" in headers
        csp = headers["content-security-policy"]
        assert "default-src" in csp

        # Other security headers
        assert headers.get("x-content-type-options") == "nosniff"
        assert headers.get("x-frame-options") in ("DENY", "SAMEORIGIN")
        assert "strict-transport-security" in headers
        assert headers.get("referrer-policy") is not None
        assert headers.get("permissions-policy") is not None

    def test_cors_not_wildcard(self, client):
        """CORS should never be wildcard in production."""
        response = client.options(
            "/api/data",
            headers={"Origin": "https://evil.example.com"}
        )
        cors_origin = response.headers.get("access-control-allow-origin", "")
        assert cors_origin != "*"
        assert "evil.example.com" not in cors_origin

    def test_cookies_have_security_flags(self, client):
        response = client.post("/api/auth/login", json={
            "username": "test", "password": "test"
        })
        for cookie in response.headers.getlist("set-cookie"):
            cookie_lower = cookie.lower()
            assert "httponly" in cookie_lower
            assert "secure" in cookie_lower
            assert "samesite" in cookie_lower
```

## Test Organization

### Structure

```
tests/
  security/
    test_auth_boundaries.py      # IDOR, privilege escalation
    test_input_validation.py     # SQLi, XSS, path traversal
    test_security_headers.py     # CSP, CORS, HSTS, cookies
    test_rate_limiting.py        # Brute force protection
    test_business_logic.py       # Logic abuse cases
    conftest.py                  # Auth fixtures, test users
```

### Naming Convention

- Prefix with `test_` for pytest discovery.
- Include vulnerability reference in docstring: `"""Regression: VULN-2025-042"""`.
- Group by attack category, not by endpoint.

### Running in CI

Security regression tests should run in the standard test suite:

```yaml
# No separate security test job needed
- name: Run tests
  run: pytest tests/ -v --tb=short
  # Security tests in tests/security/ run alongside all other tests
```

## Writing New Regression Tests

When a vulnerability is confirmed and fixed:

1. **Document the attack vector**: exact request, parameters, and expected vulnerable behavior.
2. **Write the test**: reproduce the attack and assert it is blocked.
3. **Include context**: vulnerability ID, date, and brief description in docstring.
4. **Verify the test fails without the fix**: check out the pre-fix code and confirm the test catches it.
5. **Add to standard suite**: no special flags or separate runs needed.
