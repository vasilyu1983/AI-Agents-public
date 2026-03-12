# API Documentation Standards

Comprehensive guide for documenting REST, GraphQL, and gRPC APIs with modern standards and tools.

## Modern API Documentation Standards (January 2026)

**Key Standards**:
- **OpenAPI 3.2.0** (latest, Sept 2025) - Streaming support, hierarchical tags, self-identifying documents
- **OpenAPI 3.1.0** (stable) - JSON Schema compatibility, webhooks support
- **AsyncAPI 3.0** - Event-driven and message-driven APIs
- **GraphQL Schema** - Self-documenting with introspection
- **gRPC Protocol Buffers** - Type-safe service definitions

**Modern Tools**:
- **Interactive docs**: Swagger UI, Redoc, Stoplight, RapiDoc
- **AI-assisted**: Mintlify, Readme.com (AI-powered search), Apidog (multi-protocol)
- **Testing**: Postman, Insomnia, Thunder Client
- **Code generation**: OpenAPI Generator, GraphQL Code Generator

---

## OpenAPI 3.2.0 Features (September 2025)

OpenAPI 3.2.0 introduces significant improvements for streaming APIs and modern web patterns.

### Streaming Support

**New streaming capabilities**:
- **itemSchema**: Define schema for individual items in streaming responses
- **prefixEncoding**: Specify encoding for streamed content prefixes
- **Sequential media types**: First-class support for SSE, JSON Lines, multipart feeds

**Example - Server-Sent Events (SSE)**:

```yaml
openapi: 3.2.0
paths:
  /events/stream:
    get:
      summary: Subscribe to real-time events
      responses:
        '200':
          description: Event stream
          content:
            text/event-stream:
              schema:
                type: array
                itemSchema:
                  $ref: '#/components/schemas/Event'
              encoding:
                prefixEncoding: "data: "
```

**Example - JSON Lines (NDJSON)**:

```yaml
paths:
  /logs/stream:
    get:
      summary: Stream log entries
      responses:
        '200':
          description: Log stream
          content:
            application/x-ndjson:
              schema:
                type: array
                itemSchema:
                  $ref: '#/components/schemas/LogEntry'
```

### Tag Metadata (Replaces Vendor Extensions)

**New standardized tag fields**:
- **summary**: Brief description for navigation
- **parent**: Hierarchical tag organization
- **kind**: Tag category (resource, operation, domain)

```yaml
tags:
  - name: users
    summary: User management
    kind: resource
    description: Operations for creating, reading, updating, and deleting users
  - name: users-admin
    summary: Admin user operations
    parent: users
    kind: operation
```

### Query Operations

**New query-related features**:
- **additionalOperations**: Define custom operations beyond CRUD
- **querystring parameter location**: Explicit querystring handling

```yaml
paths:
  /search:
    query:
      summary: Search across all resources
      parameters:
        - name: q
          in: querystring
          required: true
          schema:
            type: string
      additionalOperations:
        - facets
        - suggest
```

### Migration Notes

**Upgrading from 3.1.x**:
- Old vendor extensions (`x-summary`, `x-parent`) still work but are deprecated
- Check linters and gateways for 3.2.0 compatibility
- Streaming payloads may require schema updates
- Test with Swagger UI 5.x+ or Redoc 2.x+ for full 3.2.0 support

## Essential API Documentation Elements

Every API documentation should include:

1. **Base URL** - API endpoint base
2. **Authentication** - How to authenticate (Bearer, API key, OAuth)
3. **Endpoints** - All available endpoints with:
   - HTTP method and path
   - Request parameters
   - Request body schema
   - Response format with examples
   - Status codes
   - cURL/code examples
4. **Error Responses** - Standard error format
5. **Rate Limiting** - Limits and rate limit headers
6. **Pagination** - Cursor-based or offset-based
7. **Webhooks** (if applicable) - Event types and payloads
8. **SDKs/Libraries** - Client libraries for different languages
9. **Changelog** - API version history

## REST API Documentation

### Authentication Section

**Purpose**: Explain how to authenticate API requests.

**Common methods**:
- Bearer tokens (JWT)
- API keys
- OAuth 2.0
- Basic authentication (not recommended for production)

**Example**:

```markdown
## Authentication

All API requests require authentication using a Bearer token.

### Getting a Token

**Request**:
```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "your-password"
}
```

**Response**:
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "expiresIn": 3600
}
```

### Using the Token

Include the token in the `Authorization` header:

```http
GET /api/v1/users
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### Token Expiration

- Tokens expire after 1 hour (3600 seconds)
- Refresh tokens valid for 7 days
- Use `/auth/refresh` endpoint to renew tokens
```

### Endpoint Documentation Template

**For each endpoint, document**:

```markdown
### GET /api/v1/users/:id

Get a user by ID.

**Path Parameters**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | string (UUID) | Yes | User unique identifier |

**Query Parameters**:

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `include` | string | No | - | Comma-separated related resources (e.g., `orders,payments`) |
| `fields` | string | No | All fields | Comma-separated fields to return (e.g., `email,name`) |

**Request Headers**:

```http
GET /api/v1/users/123e4567-e89b-12d3-a456-426614174000?include=orders
Authorization: Bearer YOUR_ACCESS_TOKEN
Accept: application/json
```

**Response (200 OK)**:

```json
{
  "data": {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "email": "user@example.com",
    "name": "John Doe",
    "createdAt": "2025-11-22T10:30:00Z",
    "orders": [
      {
        "id": "order-001",
        "total": 99.99,
        "status": "completed"
      }
    ]
  }
}
```

**Error Responses**:

| Status Code | Description | Response |
|-------------|-------------|----------|
| 400 Bad Request | Invalid UUID format | `{"error": {"code": "INVALID_ID", "message": "Invalid user ID format"}}` |
| 401 Unauthorized | Missing or invalid token | `{"error": {"code": "UNAUTHORIZED", "message": "Invalid authentication token"}}` |
| 404 Not Found | User not found | `{"error": {"code": "NOT_FOUND", "message": "User not found"}}` |
| 429 Too Many Requests | Rate limit exceeded | `{"error": {"code": "RATE_LIMIT", "message": "Too many requests"}}` |

**Rate Limit**: 1000 requests per hour per user

**Example cURL**:

```bash
curl -X GET \
  https://api.example.com/v1/users/123e4567-e89b-12d3-a456-426614174000 \
  -H 'Authorization: Bearer YOUR_ACCESS_TOKEN' \
  -H 'Accept: application/json'
```

**Example JavaScript**:

```javascript
const response = await fetch('https://api.example.com/v1/users/123e4567-e89b-12d3-a456-426614174000', {
  headers: {
    'Authorization': `Bearer ${token}`,
    'Accept': 'application/json'
  }
});

const user = await response.json();
console.log(user.data);
```

**Example Python**:

```python
import requests

headers = {
    'Authorization': f'Bearer {token}',
    'Accept': 'application/json'
}

response = requests.get(
    'https://api.example.com/v1/users/123e4567-e89b-12d3-a456-426614174000',
    headers=headers
)

user = response.json()
print(user['data'])
```
```

### Error Response Format (RFC 7807)

**Standard error format**:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Request validation failed",
    "details": [
      {
        "field": "email",
        "message": "Invalid email format",
        "value": "not-an-email"
      }
    ],
    "requestId": "req_abc123xyz",
    "timestamp": "2025-11-22T10:30:00Z"
  }
}
```

**Error code standards**:
- `VALIDATION_ERROR` - Request validation failed
- `AUTHENTICATION_ERROR` - Authentication failed
- `AUTHORIZATION_ERROR` - Insufficient permissions
- `NOT_FOUND` - Resource not found
- `CONFLICT` - Resource conflict (duplicate)
- `RATE_LIMIT_EXCEEDED` - Too many requests
- `INTERNAL_ERROR` - Server error

### Rate Limiting

**Document**:
- Limit (requests per time period)
- Time window
- Rate limit headers
- Behavior when limit exceeded

**Example**:

```markdown
## Rate Limiting

All endpoints are rate-limited to prevent abuse.

**Limits**:
- **Authenticated users**: 1000 requests per hour
- **Unauthenticated users**: 100 requests per hour

**Rate Limit Headers**:

Every response includes rate limit information:

```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 987
X-RateLimit-Reset: 1700654400
```

| Header | Description |
|--------|-------------|
| `X-RateLimit-Limit` | Total requests allowed per hour |
| `X-RateLimit-Remaining` | Requests remaining in current window |
| `X-RateLimit-Reset` | Unix timestamp when limit resets |

**Rate Limit Exceeded (429)**:

```json
{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Rate limit exceeded. Try again in 300 seconds.",
    "retryAfter": 300
  }
}
```

**Best Practices**:
- Monitor `X-RateLimit-Remaining` header
- Implement exponential backoff when rate limited
- Cache responses when possible to reduce API calls
```

### Pagination

**Cursor-based pagination (recommended)**:

```markdown
## Pagination

All list endpoints support cursor-based pagination for consistent results.

**Query Parameters**:

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `cursor` | string | - | Pagination cursor from previous response |
| `limit` | integer | 20 | Items per page (max: 100) |

**Request**:

```http
GET /api/v1/users?limit=20
```

**Response**:

```json
{
  "data": [
    { "id": "user-1", "name": "John" },
    { "id": "user-2", "name": "Jane" }
  ],
  "pagination": {
    "cursor": "eyJpZCI6InVzZXItMjAifQ==",
    "hasMore": true,
    "total": 150
  }
}
```

**Next Page**:

```http
GET /api/v1/users?cursor=eyJpZCI6InVzZXItMjAifQ==&limit=20
```

**Benefits**:
- Consistent results (no missing/duplicate items)
- Works with real-time data
- Better performance than offset pagination
```

**Offset-based pagination (simpler but less reliable)**:

```markdown
## Pagination

**Query Parameters**:

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `page` | integer | 1 | Page number (1-indexed) |
| `perPage` | integer | 20 | Items per page (max: 100) |

**Response**:

```json
{
  "data": [...],
  "meta": {
    "page": 1,
    "perPage": 20,
    "total": 150,
    "totalPages": 8
  }
}
```
```

### Webhooks

**Document webhook events and payloads**:

```markdown
## Webhooks

Subscribe to events by configuring webhook endpoints in your account settings.

**Supported Events**:

| Event | Description | Payload |
|-------|-------------|---------|
| `user.created` | New user registered | `User` object |
| `order.completed` | Order completed | `Order` object |
| `payment.succeeded` | Payment successful | `Payment` object |
| `payment.failed` | Payment failed | `Payment` object with error |

**Webhook Payload Format**:

```json
{
  "event": "order.completed",
  "timestamp": "2025-11-22T10:30:00Z",
  "data": {
    "id": "order-123",
    "userId": "user-456",
    "total": 99.99,
    "status": "completed"
  },
  "webhookId": "wh_abc123"
}
```

**Webhook Signature Verification**:

All webhooks include an `X-Webhook-Signature` header for verification:

```javascript
const crypto = require('crypto');

function verifyWebhook(payload, signature, secret) {
  const expectedSignature = crypto
    .createHmac('sha256', secret)
    .update(payload)
    .digest('hex');

  return signature === expectedSignature;
}
```

**Retry Policy**:
- Failed webhooks retry with exponential backoff
- Retries: immediately, 5 min, 1 hour, 6 hours, 24 hours
- After 5 failures, webhook is disabled
```

## GraphQL API Documentation

**GraphQL benefits**: Self-documenting through introspection.

**Example documentation**:

```markdown
# GraphQL API

**Endpoint**: `https://api.example.com/graphql`

## Authentication

Include Bearer token in Authorization header:

```http
POST /graphql
Authorization: Bearer YOUR_ACCESS_TOKEN
Content-Type: application/json
```

## Schema Introspection

Explore the full schema using GraphQL Playground or GraphiQL:

- **GraphQL Playground**: https://api.example.com/graphql
- **Schema docs**: Auto-generated from schema

## Example Queries

### Get User

```graphql
query GetUser($id: ID!) {
  user(id: $id) {
    id
    email
    name
    orders {
      id
      total
      status
    }
  }
}
```

**Variables**:

```json
{
  "id": "user-123"
}
```

**Response**:

```json
{
  "data": {
    "user": {
      "id": "user-123",
      "email": "user@example.com",
      "name": "John Doe",
      "orders": [...]
    }
  }
}
```

### Create Order (Mutation)

```graphql
mutation CreateOrder($input: CreateOrderInput!) {
  createOrder(input: $input) {
    id
    total
    status
  }
}
```

**Variables**:

```json
{
  "input": {
    "userId": "user-123",
    "items": [
      { "productId": "prod-456", "quantity": 2 }
    ]
  }
}
```

## Error Handling

GraphQL returns errors in `errors` array:

```json
{
  "errors": [
    {
      "message": "User not found",
      "extensions": {
        "code": "NOT_FOUND",
        "userId": "user-999"
      }
    }
  ],
  "data": null
}
```
```

## gRPC API Documentation

**gRPC**: Define services in Protocol Buffers (.proto files).

**Example documentation**:

```markdown
# gRPC API

**Server**: `api.example.com:50051`

## Protocol Buffers Definition

```protobuf
syntax = "proto3";

package user.v1;

service UserService {
  rpc GetUser (GetUserRequest) returns (User) {}
  rpc ListUsers (ListUsersRequest) returns (ListUsersResponse) {}
  rpc CreateUser (CreateUserRequest) returns (User) {}
}

message User {
  string id = 1;
  string email = 2;
  string name = 3;
  int64 created_at = 4;
}

message GetUserRequest {
  string id = 1;
}

message ListUsersRequest {
  int32 page_size = 1;
  string page_token = 2;
}

message ListUsersResponse {
  repeated User users = 1;
  string next_page_token = 2;
}
```

## Authentication

Use gRPC metadata to pass authentication:

```javascript
const metadata = new grpc.Metadata();
metadata.add('authorization', `Bearer ${token}`);

client.getUser({ id: 'user-123' }, metadata, callback);
```

## Example Calls

### Get User (Go)

```go
import (
  pb "path/to/proto/user/v1"
  "google.golang.org/grpc"
)

conn, _ := grpc.Dial("api.example.com:50051", grpc.WithInsecure())
client := pb.NewUserServiceClient(conn)

user, err := client.GetUser(ctx, &pb.GetUserRequest{
  Id: "user-123",
})
```
```

## OpenAPI 3.1 Specification

**Use OpenAPI for REST APIs**:

```yaml
openapi: 3.1.0
info:
  title: Example API
  version: 1.0.0
  description: API for managing users and orders

servers:
  - url: https://api.example.com/v1
    description: Production server

security:
  - bearerAuth: []

paths:
  /users/{id}:
    get:
      summary: Get user by ID
      parameters:
        - name: id
          in: path
          required: true
          schema:
            type: string
            format: uuid
      responses:
        '200':
          description: User found
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/User'
        '404':
          description: User not found

components:
  securitySchemes:
    bearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT

  schemas:
    User:
      type: object
      properties:
        id:
          type: string
          format: uuid
        email:
          type: string
          format: email
        name:
          type: string
```

**Generate interactive docs**:

```bash
# Swagger UI
npx @redocly/cli preview-docs openapi.yaml

# Redoc
npx @redocly/cli build-docs openapi.yaml
```

## API Documentation Checklist

**Before publishing API docs**:

- [ ] All endpoints documented
- [ ] Authentication explained with examples
- [ ] Request/response schemas complete
- [ ] Error responses documented
- [ ] Rate limiting explained
- [ ] Pagination documented
- [ ] Code examples in 2-3 languages
- [ ] cURL examples for all endpoints
- [ ] Webhooks documented (if applicable)
- [ ] Changelog included
- [ ] Interactive docs available (Swagger/Redoc)
- [ ] SDKs listed with links
- [ ] Versioning strategy explained
- [ ] Deprecation notices added
- [ ] Contact/support information included

## API Documentation Success Criteria

**Great API documentation enables developers to**:

1. [OK] Authenticate successfully in < 5 minutes
2. [OK] Make first API call in < 10 minutes
3. [OK] Find all endpoints and parameters
4. [OK] Understand error responses
5. [OK] Copy-paste working code examples
6. [OK] Handle rate limits appropriately
7. [OK] Implement webhooks correctly

**Quality metrics**:
- Time to first successful API call: < 10 minutes
- Support questions about authentication: < 5%
- Completeness: All endpoints documented
- Code examples: 3+ languages
- Error clarity: All status codes explained
