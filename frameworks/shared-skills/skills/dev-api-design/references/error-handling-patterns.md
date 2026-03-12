# Error Response Standardization

This guide provides production-ready patterns for implementing consistent, informative error responses in RESTful APIs.

---

## RFC 9457 Problem Details Standard (Obsoletes RFC 7807)

**Use when:** Ensuring consistent error handling across all API endpoints.

RFC 9457 defines a "problem detail" format for HTTP API errors, providing a standardized structure that's both machine-readable and human-friendly.

### Standard Error Format

```json
{
  "type": "https://api.example.com/errors/validation-error",
  "title": "Validation Error",
  "status": 422,
  "detail": "Email address is already registered",
  "instance": "/api/v1/users",
  "code": "DUPLICATE_EMAIL",
  "retryable": false,
  "errors": [
    {
      "field": "email",
      "code": "DUPLICATE_EMAIL",
      "message": "Email address is already registered"
    }
  ],
  "traceId": "abc123def456"
}
```

### Field Descriptions

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `type` | URI | Yes | URI identifying the error type (for documentation) |
| `title` | string | Yes | Human-readable error title (consistent per type) |
| `status` | integer | Yes | HTTP status code |
| `detail` | string | No | Human-readable explanation (specific to this occurrence) |
| `instance` | URI | No | URI of the request that caused the error |
| `code` | string | No | Stable, application-specific error code (for client handling) |
| `retryable` | boolean | No | Whether retry could succeed without changing the request |
| `errors` | array | No | Field-level validation errors |
| `traceId` | string | No | Unique identifier for debugging |

---

## HTTP Status Code Reference

### Success Codes (2xx)

| Code | Name | Use When |
|------|------|----------|
| `200 OK` | Standard success | GET, PUT, PATCH with response body |
| `201 Created` | Resource created | POST successfully creates resource |
| `202 Accepted` | Async processing | Request accepted, processing later |
| `204 No Content` | Success, no body | DELETE, POST/PUT with no response |

### Client Error Codes (4xx)

| Code | Name | Use When |
|------|------|----------|
| `400 Bad Request` | Malformed request | Invalid JSON syntax, missing headers |
| `401 Unauthorized` | Auth required | Missing/invalid credentials |
| `403 Forbidden` | Insufficient permissions | Valid auth, but lacks permission |
| `404 Not Found` | Resource not found | Invalid resource ID |
| `405 Method Not Allowed` | HTTP method unsupported | POST to read-only endpoint |
| `406 Not Acceptable` | Content type unsupported | Client can't accept response format |
| `409 Conflict` | Resource conflict | Duplicate resource, optimistic lock |
| `410 Gone` | Permanently deleted | Resource existed, now deleted |
| `415 Unsupported Media Type` | Invalid Content-Type | Server can't parse request format |
| `422 Unprocessable Entity` | Validation error | Valid syntax, invalid semantics |
| `429 Too Many Requests` | Rate limit exceeded | Client exceeded quota |

### Server Error Codes (5xx)

| Code | Name | Use When |
|------|------|----------|
| `500 Internal Server Error` | Unexpected error | Unhandled exception |
| `502 Bad Gateway` | Upstream error | Invalid response from upstream |
| `503 Service Unavailable` | Temporary unavailability | Maintenance, overload |
| `504 Gateway Timeout` | Upstream timeout | Upstream service timeout |

---

## Error Response Examples

### 400 Bad Request - Malformed JSON

```http
HTTP/1.1 400 Bad Request
Content-Type: application/problem+json

{
  "type": "https://api.example.com/errors/bad-request",
  "title": "Bad Request",
  "status": 400,
  "detail": "Invalid JSON syntax in request body",
  "instance": "/api/v1/users",
  "traceId": "a1b2c3d4"
}
```

---

### 401 Unauthorized - Missing Token

```http
HTTP/1.1 401 Unauthorized
Content-Type: application/problem+json
WWW-Authenticate: Bearer realm="api"

{
  "type": "https://api.example.com/errors/unauthorized",
  "title": "Unauthorized",
  "status": 401,
  "detail": "Authentication required. Provide a valid Bearer token.",
  "instance": "/api/v1/users",
  "traceId": "e5f6g7h8"
}
```

---

### 403 Forbidden - Insufficient Permissions

```http
HTTP/1.1 403 Forbidden
Content-Type: application/problem+json

{
  "type": "https://api.example.com/errors/forbidden",
  "title": "Forbidden",
  "status": 403,
  "detail": "You do not have permission to access this resource. Required role: admin.",
  "instance": "/api/v1/admin/users",
  "traceId": "i9j0k1l2"
}
```

---

### 404 Not Found - Resource Missing

```http
HTTP/1.1 404 Not Found
Content-Type: application/problem+json

{
  "type": "https://api.example.com/errors/not-found",
  "title": "Not Found",
  "status": 404,
  "detail": "User with ID '12345' not found",
  "instance": "/api/v1/users/12345",
  "traceId": "m3n4o5p6"
}
```

---

### 409 Conflict - Duplicate Resource

```http
HTTP/1.1 409 Conflict
Content-Type: application/problem+json

{
  "type": "https://api.example.com/errors/conflict",
  "title": "Conflict",
  "status": 409,
  "detail": "A user with this email already exists",
  "instance": "/api/v1/users",
  "errors": [
    {
      "field": "email",
      "code": "DUPLICATE_EMAIL",
      "message": "Email address 'user@example.com' is already registered"
    }
  ],
  "traceId": "q7r8s9t0"
}
```

---

### 422 Unprocessable Entity - Validation Errors

```http
HTTP/1.1 422 Unprocessable Entity
Content-Type: application/problem+json

{
  "type": "https://api.example.com/errors/validation-error",
  "title": "Validation Error",
  "status": 422,
  "detail": "One or more validation errors occurred",
  "instance": "/api/v1/users",
  "errors": [
    {
      "field": "email",
      "code": "INVALID_FORMAT",
      "message": "Email address must be a valid email format"
    },
    {
      "field": "password",
      "code": "TOO_SHORT",
      "message": "Password must be at least 8 characters long"
    },
    {
      "field": "age",
      "code": "OUT_OF_RANGE",
      "message": "Age must be between 18 and 120"
    }
  ],
  "traceId": "u1v2w3x4"
}
```

---

### 429 Too Many Requests - Rate Limit

```http
HTTP/1.1 429 Too Many Requests
Content-Type: application/problem+json
Retry-After: 60
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1640000060

{
  "type": "https://api.example.com/errors/rate-limit-exceeded",
  "title": "Too Many Requests",
  "status": 429,
  "detail": "Rate limit exceeded. Try again in 60 seconds.",
  "instance": "/api/v1/users",
  "retryAfter": 60,
  "traceId": "y5z6a7b8"
}
```

---

### 500 Internal Server Error

```http
HTTP/1.1 500 Internal Server Error
Content-Type: application/problem+json

{
  "type": "https://api.example.com/errors/internal-error",
  "title": "Internal Server Error",
  "status": 500,
  "detail": "An unexpected error occurred. Please try again later.",
  "instance": "/api/v1/users",
  "traceId": "c9d0e1f2"
}
```

**Security note:** Never expose stack traces or internal error details in production.

---

## Validation Error Patterns

### Field-Level Errors

```json
{
  "errors": [
    {
      "field": "email",
      "code": "INVALID_FORMAT",
      "message": "Email address must be valid"
    },
    {
      "field": "password",
      "code": "TOO_SHORT",
      "message": "Password must be at least 8 characters"
    }
  ]
}
```

### Nested Field Errors

```json
{
  "errors": [
    {
      "field": "address.zipCode",
      "code": "INVALID_FORMAT",
      "message": "ZIP code must be 5 digits"
    },
    {
      "field": "items[0].quantity",
      "code": "OUT_OF_RANGE",
      "message": "Quantity must be at least 1"
    }
  ]
}
```

### Error Codes Convention

Use SCREAMING_SNAKE_CASE for machine-readable error codes:

```
REQUIRED_FIELD
INVALID_FORMAT
TOO_SHORT
TOO_LONG
OUT_OF_RANGE
DUPLICATE_VALUE
NOT_FOUND
EXPIRED
INVALID_STATE
```

---

## Implementation Examples

### FastAPI (Python)

```python
from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional
import uuid

class ErrorDetail(BaseModel):
    field: str
    code: str
    message: str

class ProblemDetail(BaseModel):
    type: str
    title: str
    status: int
    detail: str
    instance: str
    errors: Optional[List[ErrorDetail]] = None
    traceId: str

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    errors = []
    for error in exc.errors():
        field = ".".join(str(loc) for loc in error["loc"][1:])
        errors.append({
            "field": field,
            "code": error["type"].upper().replace(".", "_"),
            "message": error["msg"]
        })

    problem = ProblemDetail(
        type="https://api.example.com/errors/validation-error",
        title="Validation Error",
        status=422,
        detail="One or more validation errors occurred",
        instance=str(request.url.path),
        errors=errors,
        traceId=str(uuid.uuid4())
    )

    return JSONResponse(
        status_code=422,
        content=problem.dict(exclude_none=True)
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    problem = ProblemDetail(
        type=f"https://api.example.com/errors/{exc.status_code}",
        title=exc.detail,
        status=exc.status_code,
        detail=exc.detail,
        instance=str(request.url.path),
        traceId=str(uuid.uuid4())
    )

    return JSONResponse(
        status_code=exc.status_code,
        content=problem.dict(exclude_none=True)
    )
```

---

### Express.js (TypeScript)

```typescript
import express, { Request, Response, NextFunction } from 'express';
import { v4 as uuidv4 } from 'uuid';

interface ErrorDetail {
  field: string;
  code: string;
  message: string;
}

interface ProblemDetail {
  type: string;
  title: string;
  status: number;
  detail: string;
  instance: string;
  errors?: ErrorDetail[];
  traceId: string;
}

class ApiError extends Error {
  constructor(
    public status: number,
    public title: string,
    public detail: string,
    public errors?: ErrorDetail[]
  ) {
    super(detail);
  }
}

// Global error handler
app.use((err: Error, req: Request, res: Response, next: NextFunction) => {
  const traceId = uuidv4();

  if (err instanceof ApiError) {
    const problem: ProblemDetail = {
      type: `https://api.example.com/errors/${err.status}`,
      title: err.title,
      status: err.status,
      detail: err.detail,
      instance: req.path,
      errors: err.errors,
      traceId
    };

    return res.status(err.status).json(problem);
  }

  // Unhandled error
  const problem: ProblemDetail = {
    type: 'https://api.example.com/errors/internal-error',
    title: 'Internal Server Error',
    status: 500,
    detail: 'An unexpected error occurred',
    instance: req.path,
    traceId
  };

  console.error('[Error]', traceId, err);
  res.status(500).json(problem);
});

// Usage
app.post('/users', (req, res, next) => {
  const errors: ErrorDetail[] = [];

  if (!req.body.email) {
    errors.push({
      field: 'email',
      code: 'REQUIRED_FIELD',
      message: 'Email is required'
    });
  }

  if (errors.length > 0) {
    throw new ApiError(422, 'Validation Error', 'One or more validation errors occurred', errors);
  }

  // ... create user
});
```

---

## Best Practices Checklist

- [ ] **Consistent error format** across all endpoints
- [ ] **Machine-readable error codes** (e.g., `DUPLICATE_EMAIL`)
- [ ] **Human-readable messages** for client display
- [ ] **Field-level validation errors** with specific field names
- [ ] **Trace IDs for debugging** (UUID or correlation ID)
- [ ] **No sensitive data** in error responses (no stack traces, internal paths)
- [ ] **Proper Content-Type** (`application/problem+json` or `application/json`)
- [ ] **HTTP status code matches error type**
- [ ] **Error type URI** for documentation reference
- [ ] **Instance URI** to identify failing request

---

## Common Anti-Patterns

### BAD: Inconsistent Error Format

```json
// Endpoint 1
{ "error": "User not found" }

// Endpoint 2
{ "message": "Invalid input", "code": 400 }

// Endpoint 3
{ "errors": [{ "msg": "Email required" }] }
```

**Fix:** Use RFC 9457 format everywhere (and document your `type` + `code` catalog).

---

### BAD: Generic Error Messages

```json
{
  "error": "Bad request"
}
```

**Fix:** Provide specific, actionable details:

```json
{
  "type": "https://api.example.com/errors/validation-error",
  "title": "Validation Error",
  "status": 422,
  "detail": "Email address is required",
  "errors": [
    {
      "field": "email",
      "code": "REQUIRED_FIELD",
      "message": "Email address is required"
    }
  ]
}
```

---

### BAD: Exposing Internal Errors

```json
{
  "error": "PostgreSQL connection failed: role 'dbuser' does not exist"
}
```

**Fix:** Sanitize internal errors in production:

```json
{
  "type": "https://api.example.com/errors/internal-error",
  "title": "Internal Server Error",
  "status": 500,
  "detail": "An unexpected error occurred. Please try again later.",
  "traceId": "abc123"
}
```

---

### BAD: No Trace ID

Hard to debug production issues without correlation ID.

**Fix:** Always include trace ID:

```json
{
  "traceId": "a1b2c3d4-e5f6-7890-g1h2-i3j4k5l6m7n8"
}
```

---

## Error Response Decision Matrix

| Scenario | Status Code | Error Type |
|----------|-------------|------------|
| Missing required field | 422 | Validation Error |
| Invalid email format | 422 | Validation Error |
| Duplicate resource (email exists) | 409 | Conflict |
| Resource not found | 404 | Not Found |
| Missing auth token | 401 | Unauthorized |
| Invalid auth token | 401 | Unauthorized |
| Valid token, insufficient permissions | 403 | Forbidden |
| Rate limit exceeded | 429 | Too Many Requests |
| Malformed JSON | 400 | Bad Request |
| Unsupported Content-Type | 415 | Unsupported Media Type |
| Unhandled exception | 500 | Internal Server Error |
| Upstream service error | 502 | Bad Gateway |
| Upstream timeout | 504 | Gateway Timeout |

---

## Related Resources

- **[restful-design-patterns.md](restful-design-patterns.md)** - HTTP status code semantics
- **[authentication-patterns.md](authentication-patterns.md)** - 401/403 error handling
- **[rate-limiting-patterns.md](rate-limiting-patterns.md)** - 429 rate limit responses
- **[api-design-best-practices.md](api-design-best-practices.md)** - Overall API design
- **[openapi-guide.md](openapi-guide.md)** - Documenting error responses in OpenAPI
