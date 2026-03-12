# API Documentation

Base URL: `https://api.example.com/v1`

Version: 1.0.0

Last Updated: 2025-01-15

## Table of Contents

- [Authentication](#authentication)
- [Rate Limiting](#rate-limiting)
- [Error Handling](#error-handling)
- [Pagination](#pagination)
- [Endpoints](#endpoints)
  - [Users](#users)
  - [Posts](#posts)
  - [Comments](#comments)

## Authentication

All API requests require authentication via Bearer token.

### Obtaining an Access Token

```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**Response:**

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "Bearer",
  "expires_in": 3600,
  "refresh_token": "dGhpcyBpcyBhIHJlZnJlc2ggdG9rZW4..."
}
```

### Using the Access Token

Include the token in the `Authorization` header:

```http
GET /api/v1/users
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### Token Expiration

- Access tokens expire after 1 hour
- Use the refresh token to obtain a new access token without re-authenticating

```http
POST /api/v1/auth/refresh
Content-Type: application/json

{
  "refresh_token": "dGhpcyBpcyBhIHJlZnJlc2ggdG9rZW4..."
}
```

## Rate Limiting

API requests are rate-limited to prevent abuse.

**Limits:**
- Authenticated users: 1000 requests per hour
- Unauthenticated requests: 100 requests per hour

**Headers:**

```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 995
X-RateLimit-Reset: 1642521600
```

**Rate Limit Exceeded Response:**

```http
HTTP/1.1 429 Too Many Requests
Content-Type: application/json

{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Rate limit exceeded. Please try again later.",
    "retry_after": 3600
  }
}
```

## Error Handling

The API uses standard HTTP status codes and returns errors in RFC 7807 Problem Details format.

### Error Response Format

```json
{
  "type": "https://api.example.com/errors/validation-error",
  "title": "Validation Error",
  "status": 422,
  "detail": "The request body contains invalid data",
  "instance": "/api/v1/users",
  "errors": [
    {
      "field": "email",
      "code": "INVALID_FORMAT",
      "message": "Email address is not valid"
    },
    {
      "field": "age",
      "code": "OUT_OF_RANGE",
      "message": "Age must be between 18 and 120"
    }
  ]
}
```

### Status Codes

| Code | Meaning | Description |
|------|---------|-------------|
| 200 | OK | Request succeeded |
| 201 | Created | Resource created successfully |
| 204 | No Content | Request succeeded, no response body |
| 400 | Bad Request | Invalid request format |
| 401 | Unauthorized | Missing or invalid authentication |
| 403 | Forbidden | Authenticated but not authorized |
| 404 | Not Found | Resource does not exist |
| 422 | Unprocessable Entity | Validation error |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Server error |
| 503 | Service Unavailable | Temporary unavailability |

## Pagination

List endpoints support cursor-based pagination.

### Request

```http
GET /api/v1/users?limit=20&cursor=eyJpZCI6MTIzfQ
```

**Query Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `limit` | integer | No | Number of items (1-100, default: 20) |
| `cursor` | string | No | Pagination cursor from previous response |

### Response

```json
{
  "data": [
    { "id": 1, "name": "John Doe", ... },
    { "id": 2, "name": "Jane Smith", ... }
  ],
  "pagination": {
    "next_cursor": "eyJpZCI6MjB9",
    "has_more": true,
    "total": 150
  }
}
```

## Endpoints

---

## Users

### List Users

Retrieve a paginated list of users.

```http
GET /api/v1/users
```

**Query Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `limit` | integer | No | Number of items (default: 20, max: 100) |
| `cursor` | string | No | Pagination cursor |
| `sort` | string | No | Sort field (`name`, `-created_at`) |
| `status` | string | No | Filter by status (`active`, `inactive`) |
| `search` | string | No | Search by name or email |

**Example Request:**

```bash
curl -X GET "https://api.example.com/v1/users?limit=10&sort=-created_at&status=active" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Response:**

```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "data": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "email": "john.doe@example.com",
      "name": "John Doe",
      "avatar_url": "https://cdn.example.com/avatars/john.jpg",
      "status": "active",
      "created_at": "2025-01-15T10:30:00Z",
      "updated_at": "2025-01-15T10:30:00Z"
    }
  ],
  "pagination": {
    "next_cursor": "eyJpZCI6MTB9",
    "has_more": true,
    "total": 150
  }
}
```

---

### Get User by ID

Retrieve a specific user by ID.

```http
GET /api/v1/users/:id
```

**Path Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `id` | UUID | User ID |

**Example Request:**

```bash
curl -X GET "https://api.example.com/v1/users/550e8400-e29b-41d4-a716-446655440000" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Response:**

```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "john.doe@example.com",
  "name": "John Doe",
  "bio": "Software engineer and open source enthusiast",
  "avatar_url": "https://cdn.example.com/avatars/john.jpg",
  "location": "San Francisco, CA",
  "website": "https://johndoe.com",
  "status": "active",
  "created_at": "2025-01-15T10:30:00Z",
  "updated_at": "2025-01-15T10:30:00Z"
}
```

**Error Responses:**

```http
HTTP/1.1 404 Not Found
Content-Type: application/json

{
  "error": {
    "code": "USER_NOT_FOUND",
    "message": "User with ID 550e8400-e29b-41d4-a716-446655440000 not found"
  }
}
```

---

### Create User

Create a new user.

```http
POST /api/v1/users
```

**Request Body:**

```json
{
  "email": "newuser@example.com",
  "name": "New User",
  "password": "SecurePassword123!",
  "bio": "Optional bio text",
  "location": "New York, NY"
}
```

**Required Fields:**

| Field | Type | Constraints |
|-------|------|-------------|
| `email` | string | Valid email address, unique |
| `name` | string | 1-100 characters |
| `password` | string | Minimum 8 characters, must include uppercase, lowercase, number, special char |

**Optional Fields:**

| Field | Type | Constraints |
|-------|------|-------------|
| `bio` | string | Maximum 500 characters |
| `location` | string | Maximum 100 characters |
| `website` | string | Valid URL |

**Example Request:**

```bash
curl -X POST "https://api.example.com/v1/users" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "newuser@example.com",
    "name": "New User",
    "password": "SecurePassword123!"
  }'
```

**Response:**

```http
HTTP/1.1 201 Created
Content-Type: application/json
Location: /api/v1/users/660e8400-e29b-41d4-a716-446655440000

{
  "id": "660e8400-e29b-41d4-a716-446655440000",
  "email": "newuser@example.com",
  "name": "New User",
  "status": "active",
  "created_at": "2025-01-20T14:30:00Z",
  "updated_at": "2025-01-20T14:30:00Z"
}
```

**Error Responses:**

```http
HTTP/1.1 422 Unprocessable Entity
Content-Type: application/json

{
  "type": "https://api.example.com/errors/validation-error",
  "title": "Validation Error",
  "status": 422,
  "errors": [
    {
      "field": "email",
      "code": "DUPLICATE_EMAIL",
      "message": "Email address is already registered"
    },
    {
      "field": "password",
      "code": "WEAK_PASSWORD",
      "message": "Password must include at least one uppercase letter"
    }
  ]
}
```

---

### Update User

Update an existing user.

```http
PUT /api/v1/users/:id
```

**Path Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `id` | UUID | User ID |

**Request Body:**

```json
{
  "name": "Updated Name",
  "bio": "Updated bio text",
  "location": "Los Angeles, CA",
  "website": "https://updated-website.com"
}
```

All fields are optional. Only provided fields will be updated.

**Example Request:**

```bash
curl -X PUT "https://api.example.com/v1/users/550e8400-e29b-41d4-a716-446655440000" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John D.",
    "bio": "Updated bio"
  }'
```

**Response:**

```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "john.doe@example.com",
  "name": "John D.",
  "bio": "Updated bio",
  "status": "active",
  "updated_at": "2025-01-20T15:00:00Z"
}
```

---

### Delete User

Delete a user permanently.

```http
DELETE /api/v1/users/:id
```

**Path Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `id` | UUID | User ID |

**Example Request:**

```bash
curl -X DELETE "https://api.example.com/v1/users/550e8400-e29b-41d4-a716-446655440000" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Response:**

```http
HTTP/1.1 204 No Content
```

**Error Responses:**

```http
HTTP/1.1 403 Forbidden
Content-Type: application/json

{
  "error": {
    "code": "FORBIDDEN",
    "message": "You do not have permission to delete this user"
  }
}
```

---

## Webhooks

Subscribe to events via webhooks.

### Webhook Events

| Event | Description |
|-------|-------------|
| `user.created` | New user registered |
| `user.updated` | User profile updated |
| `user.deleted` | User deleted |
| `post.created` | New post published |

### Webhook Payload

```json
{
  "event": "user.created",
  "timestamp": "2025-01-20T14:30:00Z",
  "data": {
    "id": "660e8400-e29b-41d4-a716-446655440000",
    "email": "newuser@example.com",
    "name": "New User"
  }
}
```

### Webhook Signature

All webhook requests include an `X-Signature` header with HMAC-SHA256 signature.

**Verify signature:**

```javascript
const crypto = require('crypto');

function verifyWebhook(payload, signature, secret) {
  const expectedSignature = crypto
    .createHmac('sha256', secret)
    .update(payload)
    .digest('hex');

  return crypto.timingSafeEqual(
    Buffer.from(signature),
    Buffer.from(expectedSignature)
  );
}
```

---

## SDKs and Libraries

Official SDKs are available for:

- [JavaScript/TypeScript](https://github.com/example/sdk-js)
- [Python](https://github.com/example/sdk-python)
- [Go](https://github.com/example/sdk-go)
- [Ruby](https://github.com/example/sdk-ruby)

---

## Support

- Documentation: https://docs.example.com
- API Status: https://status.example.com
- Support Email: api-support@example.com
- Discord: https://discord.gg/example-api

---

## Changelog

See [API Changelog](https://docs.example.com/changelog) for version history and breaking changes.
