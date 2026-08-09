# API Documentation Standards

Comprehensive guide for documenting REST, AsyncAPI, GraphQL, gRPC, and API workflow specs with modern standards and tools.

## Table of Contents

- [Modern API Documentation Standards (March 2026)](#modern-api-documentation-standards-march-2026)
- [OpenAPI 3.2.0 Features (September 2025)](#openapi-320-features-september-2025)
- [Streaming Support](#streaming-support)
- [Tag Metadata (Replaces Vendor Extensions)](#tag-metadata-replaces-vendor-extensions)
- [Query Operations](#query-operations)
- [Migration Notes](#migration-notes)
- [Essential API Documentation Elements](#essential-api-documentation-elements)
- [REST API Documentation](#rest-api-documentation)
- [Authentication Section](#authentication-section)
- [Authentication](#authentication)
- [Getting a Token](#getting-a-token)
- [Using the Token](#using-the-token)
- [Token Expiration](#token-expiration)
- [Endpoint Documentation Template](#endpoint-documentation-template)
- [GET /api/v1/users/:id](#get-apiv1usersid)
- [Error Response Format (RFC 9457 Problem Details)](#error-response-format-rfc-9457-problem-details)
- [Rate Limiting](#rate-limiting)
- [Rate Limiting](#rate-limiting)
- [Pagination](#pagination)
- [Pagination](#pagination)
- [Pagination](#pagination)
- [Webhooks](#webhooks)
- [Webhooks](#webhooks)
- [GraphQL API Documentation](#graphql-api-documentation)
- [GraphQL API](#graphql-api)
- [Authentication](#authentication)
- [Schema Introspection](#schema-introspection)
- [Example Queries](#example-queries)
- [Get User](#get-user)
- [Create Order (Mutation)](#create-order-mutation)
- [Error Handling](#error-handling)
- [gRPC API Documentation](#grpc-api-documentation)
- [gRPC API](#grpc-api)
- [Protocol Buffers Definition](#protocol-buffers-definition)
- [Authentication](#authentication)
- [Example Calls](#example-calls)
- [Get User (Go)](#get-user-go)
- [OpenAPI 3.1 Specification](#openapi-31-specification)
- [Swagger UI](#swagger-ui)
- [Redoc](#redoc)
- [API Documentation Checklist](#api-documentation-checklist)
- [API Documentation Success Criteria](#api-documentation-success-criteria)

## Modern API Documentation Standards (March 2026)

**Key Standards**:
- **OpenAPI 3.2.0** (latest published OAS version) - Sequential media types, richer tag metadata, query and path improvements
- **OpenAPI 3.1.x** (widest current tooling support) - JSON Schema alignment, webhooks support
- **AsyncAPI 3.1.0** - Event-driven, streaming, and message-driven APIs
- **Arazzo 1.x** - Multi-step API workflows and task-oriented API guides
- **RFC 9457 Problem Details** - Current standard error model for HTTP APIs
- **GraphQL Schema** - Self-documenting with introspection
- **gRPC Protocol Buffers** - Type-safe service definitions

**Modern Tools**:
- **Interactive docs**: Swagger UI, Redoc, Stoplight, RapiDoc
- **Governance**: Redocly CLI, OpenAPI Generator, GraphQL Code Generator
- **AI-readable delivery**: Mintlify, ReadMe, VitePress, Starlight
- **Testing**: Postman, Insomnia, Thunder Client

---

## OpenAPI 3.2.0 Features (September 2025)

OpenAPI 3.2.0 adds useful improvements for streaming APIs and modern documentation workflows, but many teams should still publish 3.1.x until their renderer, linter, gateway, and SDK toolchain support 3.2.0 cleanly.

### Streaming Support

**New streaming capabilities**:
- **itemSchema**: Define schema for each item in sequential responses
- **itemEncoding**: Describe per-item encoding for sequential or multipart content
- **Sequential media types**: First-class support for formats such as `application/jsonl`, `application/json-seq`, and multipart streams

**Example - JSON Lines (`application/jsonl`)**:

```yaml
openapi: 3.2.0
paths:
  /logs/stream:
    get:
      summary: Stream log entries
      responses:
        '200':
          description: Log stream
          content:
            application/jsonl:
              itemSchema:
                $ref: '#/components/schemas/LogEntry'
```

**Example - item encoding for sequential payloads**:

```yaml
paths:
  /events/stream:
    get:
      summary: Stream events
      responses:
        '200':
          description: Event stream
          content:
            application/json-seq:
              itemSchema:
                $ref: '#/components/schemas/Event'
              itemEncoding:
                prefix: "\u001e"
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
- **additionalOperations**: Define custom operations beyond the standard HTTP method slots
- **querystring parameter location**: Explicitly document whole-querystring serialization when it matters

```yaml
paths:
  /search:
    query:
      summary: Search across all resources
      parameters:
        - name: q
          in: query
          required: true
          schema:
            type: string
    additionalOperations:
      SUGGEST:
        summary: Return query suggestions
        responses:
          '200':
            description: Suggestion list
```

### Migration Notes

**Upgrading from 3.1.x**:
- Old vendor extensions (`x-summary`, `x-parent`) may still exist in downstream tooling, but prefer standard fields where 3.2.0 is supported
- Verify renderer, linter, gateway, and SDK support before switching production specs to 3.2.0
- Keep 3.1.x as the default publish target when 3.2.0 features are not materially needed
- Streaming payloads and custom operations usually need the most compatibility testing

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
| 400 Bad Request | Invalid UUID format | `{"type":"https://api.example.com/problems/invalid-id","title":"Invalid ID","status":400,"detail":"Invalid user ID format"}` |
| 401 Unauthorized | Missing or invalid token | `{"type":"https://api.example.com/problems/unauthorized","title":"Unauthorized","status":401,"detail":"Invalid authentication token"}` |
| 404 Not Found | User not found | `{"type":"https://api.example.com/problems/not-found","title":"Not found","status":404,"detail":"User not found"}` |
| 429 Too Many Requests | Rate limit exceeded | `{"type":"https://api.example.com/problems/rate-limit-exceeded","title":"Rate limit exceeded","status":429,"detail":"Too many requests"}` |

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

### Error Response Format (RFC 9457 Problem Details)

**Standard error format**:

```json
{
  "type": "https://api.example.com/problems/validation-error",
  "title": "Validation error",
  "status": 422,
  "detail": "Request validation failed",
  "instance": "/api/v1/users",
  "request_id": "req_abc123xyz",
  "timestamp": "2026-03-13T10:30:00Z",
  "errors": [
    {
      "field": "email",
      "message": "Invalid email format",
      "value": "not-an-email"
    }
  ]
}
```

Use the standard Problem Details members (`type`, `title`, `status`, `detail`, `instance`) and add extension members only where they materially help clients, for example `errors`, `request_id`, or `timestamp`.

**Common problem types**:
- `validation-error` - Request validation failed
- `authentication-error` - Authentication failed
- `authorization-error` - Insufficient permissions
- `not-found` - Resource not found
- `conflict` - Resource conflict (duplicate)
- `rate-limit-exceeded` - Too many requests
- `internal-error` - Server error

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
  "type": "https://api.example.com/problems/rate-limit-exceeded",
  "title": "Rate limit exceeded",
  "status": 429,
  "detail": "Rate limit exceeded. Try again in 300 seconds.",
  "retry_after": 300
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
