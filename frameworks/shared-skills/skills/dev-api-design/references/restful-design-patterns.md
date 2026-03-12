# RESTful API Design Patterns

This guide provides production-ready patterns for designing RESTful APIs with proper HTTP semantics.

---

## Core Principles

**Use when:** Building resource-based APIs with HTTP semantics.

### The Five RESTful Principles

1. **Resources over actions**: Use nouns, not verbs (`/users` not `/getUsers`)
2. **HTTP methods**: GET (read), POST (create), PUT (replace), PATCH (update), DELETE (remove)
3. **Proper status codes**: 200 (OK), 201 (Created), 204 (No Content), 400 (Bad Request), 401 (Unauthorized), 403 (Forbidden), 404 (Not Found), 409 (Conflict), 422 (Validation Error), 500 (Server Error)
4. **Idempotency**: GET, PUT, DELETE are idempotent; POST is not
5. **Stateless**: Each request contains all necessary information

---

## URL Structure Best Practices

### Collection Endpoints

```
# List all resources (with pagination)
GET    /api/v1/users

# Create a new resource
POST   /api/v1/users
```

### Resource Endpoints

```
# Get a specific resource
GET    /api/v1/users/:id

# Replace entire resource (full update)
PUT    /api/v1/users/:id

# Update specific fields (partial update)
PATCH  /api/v1/users/:id

# Delete a resource
DELETE /api/v1/users/:id
```

### Nested Resources

**Rule**: Keep nesting max 2 levels deep for readability.

```
# User's orders (belongs-to relationship)
GET    /api/v1/users/:id/orders
POST   /api/v1/users/:id/orders

# Order items (nested collection)
GET    /api/v1/orders/:id/items
```

**When nesting gets too deep:**

```
# BAD: Bad - Too deeply nested
GET /api/v1/users/:userId/orders/:orderId/items/:itemId/reviews

# GOOD: Good - Flatten with query parameters
GET /api/v1/reviews?itemId=123
GET /api/v1/items/:itemId/reviews
```

### Action Endpoints (Non-CRUD Operations)

**Use when:** The resource model doesn't fit standard CRUD operations.

```
POST   /api/v1/users/:id/activate      # Activate user account
POST   /api/v1/users/:id/deactivate    # Deactivate user
POST   /api/v1/orders/:id/cancel       # Cancel order
POST   /api/v1/orders/:id/ship         # Ship order
POST   /api/v1/payments/:id/refund     # Refund payment
```

**Action endpoint criteria:**
- Use POST method (actions change state)
- Action name should be a verb (activate, cancel, ship)
- Only when standard CRUD doesn't fit the business logic
- Document side effects clearly

---

## HTTP Method Semantics

### GET - Read Resources

**Characteristics:**
- **Idempotent**: Multiple identical requests have same effect
- **Safe**: No side effects, doesn't change server state
- **Cacheable**: Responses can be cached by default

**Examples:**
```
GET /api/v1/users              # List users
GET /api/v1/users/:id          # Get specific user
GET /api/v1/users/:id/orders   # Get user's orders
```

**Response:**
```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "data": {
    "id": "123",
    "email": "user@example.com"
  }
}
```

---

### POST - Create Resources

**Characteristics:**
- **Not idempotent**: Multiple requests create multiple resources
- **Not safe**: Changes server state
- **Not cacheable**: Fresh data needed

**Examples:**
```
POST /api/v1/users             # Create new user
POST /api/v1/orders            # Create new order
```

**Request:**
```http
POST /api/v1/users
Content-Type: application/json

{
  "email": "newuser@example.com",
  "name": "John Doe"
}
```

**Response:**
```http
HTTP/1.1 201 Created
Location: /api/v1/users/456
Content-Type: application/json

{
  "data": {
    "id": "456",
    "email": "newuser@example.com",
    "name": "John Doe",
    "createdAt": "2025-01-15T10:30:00Z"
  }
}
```

**Best practices:**
- Return `201 Created` status
- Include `Location` header with new resource URI
- Return created resource in response body

---

### PUT - Replace Resource

**Characteristics:**
- **Idempotent**: Multiple identical requests have same effect
- **Replaces entire resource**: All fields must be provided

**Examples:**
```
PUT /api/v1/users/:id          # Replace entire user
```

**Request:**
```http
PUT /api/v1/users/123
Content-Type: application/json

{
  "email": "updated@example.com",
  "name": "Jane Doe",
  "bio": "Updated bio"
}
```

**Response:**
```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "data": {
    "id": "123",
    "email": "updated@example.com",
    "name": "Jane Doe",
    "bio": "Updated bio",
    "updatedAt": "2025-01-15T11:00:00Z"
  }
}
```

**When to use PUT vs PATCH:**
- **PUT**: When client sends complete resource representation
- **PATCH**: When client sends only changed fields

---

### PATCH - Partial Update

**Characteristics:**
- **Idempotent**: Multiple identical requests have same effect
- **Updates specific fields**: Only changed fields provided

**Examples:**
```
PATCH /api/v1/users/:id        # Update specific user fields
```

**Request:**
```http
PATCH /api/v1/users/123
Content-Type: application/json

{
  "name": "Updated Name"
}
```

**Response:**
```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "data": {
    "id": "123",
    "email": "user@example.com",
    "name": "Updated Name",
    "bio": "Existing bio remains unchanged",
    "updatedAt": "2025-01-15T11:30:00Z"
  }
}
```

---

### DELETE - Remove Resource

**Characteristics:**
- **Idempotent**: Multiple deletes have same effect (resource stays deleted)
- **Returns 204 or 200**: Depending on whether response body is included

**Examples:**
```
DELETE /api/v1/users/:id       # Delete user
```

**Response (no body):**
```http
HTTP/1.1 204 No Content
```

**Response (with body):**
```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "message": "User deleted successfully",
  "deletedAt": "2025-01-15T12:00:00Z"
}
```

**Soft delete pattern:**
```
# Mark as deleted instead of removing from database
PATCH /api/v1/users/:id
{
  "status": "deleted"
}
```

---

## HTTP Status Codes Reference

### Success Codes (2xx)

| Code | Meaning | Use Case |
|------|---------|----------|
| `200 OK` | Successful request | GET, PUT, PATCH with response body |
| `201 Created` | Resource created | POST successful creation |
| `202 Accepted` | Request accepted for processing | Async operations, queued jobs |
| `204 No Content` | Successful, no body to return | DELETE, POST/PUT without response |

### Client Error Codes (4xx)

| Code | Meaning | Use Case |
|------|---------|----------|
| `400 Bad Request` | Malformed syntax | Invalid JSON, missing required headers |
| `401 Unauthorized` | Authentication required | Missing or invalid credentials |
| `403 Forbidden` | Authenticated but insufficient permissions | User lacks role/permission |
| `404 Not Found` | Resource doesn't exist | Invalid resource ID |
| `405 Method Not Allowed` | HTTP method not supported | POST to read-only endpoint |
| `409 Conflict` | Resource state conflict | Duplicate email, version mismatch |
| `422 Unprocessable Entity` | Validation error | Invalid email format, out-of-range values |
| `429 Too Many Requests` | Rate limit exceeded | Client exceeded quota |

### Server Error Codes (5xx)

| Code | Meaning | Use Case |
|------|---------|----------|
| `500 Internal Server Error` | Unexpected server error | Unhandled exception |
| `502 Bad Gateway` | Invalid upstream response | Downstream service error |
| `503 Service Unavailable` | Temporary unavailability | Maintenance, overloaded |
| `504 Gateway Timeout` | Upstream timeout | Downstream service timeout |

---

## Idempotency Guarantees

### Idempotent Methods

**GET, PUT, DELETE, HEAD, OPTIONS** - Multiple identical requests have the same effect as a single request.

**Example - DELETE:**
```
DELETE /api/v1/users/123  # First call: deletes user, returns 204
DELETE /api/v1/users/123  # Second call: user already gone, returns 404 (or 204)
```

### Non-Idempotent Methods

**POST** - Each request creates a new resource.

**Example:**
```
POST /api/v1/orders
{ "productId": "abc", "quantity": 1 }

# Calling twice creates TWO orders
```

**Idempotency key pattern for POST:**

Use idempotency keys to make POST idempotent:

```http
POST /api/v1/orders
Idempotency-Key: unique-client-generated-uuid
Content-Type: application/json

{
  "productId": "abc",
  "quantity": 1
}
```

Server stores idempotency key and returns cached response for duplicate requests.

---

## Stateless Design

**Principle:** Each request must contain all information needed to process it.

**BAD: Bad (Stateful):**
```
# Server stores "current user" in session
GET /api/v1/current-user/orders
```

**GOOD: Good (Stateless):**
```
GET /api/v1/users/:userId/orders
Authorization: Bearer <token>
```

**Benefits of stateless APIs:**
- Horizontal scalability (any server can handle any request)
- Simpler caching
- Better fault tolerance
- Easier load balancing

---

## Design Checklist

Use this checklist when designing RESTful APIs:

- [ ] **Consistent naming**: Plural nouns for collections (`/users`, `/orders`)
- [ ] **HTTP methods match semantic intent**: GET for reads, POST for creates, etc.
- [ ] **Proper status codes**: 200 for success, 404 for not found, 422 for validation, etc.
- [ ] **Idempotent operations**: GET, PUT, DELETE designed correctly
- [ ] **Nested resources max 2 levels**: Avoid `/users/:id/orders/:id/items/:id`
- [ ] **Actions only when needed**: Use POST `/resource/:id/action` sparingly
- [ ] **Stateless design**: All context in request (auth token, parameters)
- [ ] **Version in URL**: `/api/v1/resource` for clear versioning
- [ ] **Pagination implemented**: Never return unbounded lists
- [ ] **Filtering & sorting**: Query parameters for list endpoints
- [ ] **Consistent error format**: Standardized error responses
- [ ] **Documentation**: OpenAPI spec with examples

---

## Common Anti-Patterns

### BAD: Verbs in URLs

```
# Bad
GET  /api/v1/getUsers
POST /api/v1/createUser
POST /api/v1/deleteUser
```

```
# Good
GET    /api/v1/users
POST   /api/v1/users
DELETE /api/v1/users/:id
```

---

### BAD: Using GET for Mutations

```
# Bad - GET changes state
GET /api/v1/users/:id/delete
GET /api/v1/orders/:id/cancel
```

```
# Good - POST for state changes
DELETE /api/v1/users/:id
POST   /api/v1/orders/:id/cancel
```

---

### BAD: Inconsistent Plurality

```
# Bad - Mixed singular/plural
GET /api/v1/user
GET /api/v1/orders
```

```
# Good - Always plural for collections
GET /api/v1/users
GET /api/v1/orders
```

---

### BAD: Deep Nesting

```
# Bad - Too deep
GET /api/v1/users/:userId/orders/:orderId/items/:itemId/reviews/:reviewId
```

```
# Good - Flatten with query params
GET /api/v1/reviews/:reviewId
GET /api/v1/reviews?itemId=123
```

---

## Related Resources

- **[api-design-best-practices.md](api-design-best-practices.md)** - Comprehensive design principles
- **[versioning-strategies.md](versioning-strategies.md)** - API versioning approaches
- **[error-handling-patterns.md](error-handling-patterns.md)** - Error response standards
- **[authentication-patterns.md](authentication-patterns.md)** - Auth flows and security
- **[openapi-guide.md](openapi-guide.md)** - Documentation with OpenAPI 3.1
