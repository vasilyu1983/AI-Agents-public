# OpenAPI 3.1 Specification Guide

Complete guide to documenting REST APIs using OpenAPI 3.1 (formerly Swagger).

---

## What is OpenAPI?

OpenAPI Specification (OAS) is a **machine-readable format** for describing REST APIs. It enables:

- [BOOK] **Auto-generated documentation** (Swagger UI, Redoc)
- [TOOL] **Client SDK generation** (50+ languages)
- [OK] **API contract testing** (Dredd, Pact)
- [TEST] **Mock servers** (Prism, MockServer)
- [SEARCH] **API linting** (Spectral)

**Version History:**
- OpenAPI 3.1 (2021) - Latest, JSON Schema compatible
- OpenAPI 3.0 (2017) - Major rewrite
- Swagger 2.0 (2014) - Legacy (avoid for new APIs)

---

## Basic Structure

```yaml
openapi: 3.1.0                    # Required: OAS version
info:                              # Required: API metadata
  title: My API
  version: 1.0.0
  description: API description
servers:                           # Optional: API servers
  - url: https://api.example.com/v1
paths:                             # Required: API endpoints
  /users:
    get:
      summary: List users
      responses:
        '200':
          description: Success
components:                        # Optional: Reusable schemas
  schemas:
    User:
      type: object
```

---

## Complete Example

```yaml
openapi: 3.1.0
info:
  title: User Management API
  version: 1.0.0
  description: |
    RESTful API for managing users with authentication, pagination, and filtering.
  contact:
    name: API Support
    email: api@example.com
    url: https://example.com/support
  license:
    name: MIT
    url: https://opensource.org/licenses/MIT

servers:
  - url: https://api.example.com/v1
    description: Production
  - url: https://staging.api.example.com/v1
    description: Staging

tags:
  - name: users
    description: User management operations
  - name: auth
    description: Authentication endpoints

paths:
  /users:
    get:
      summary: List users
      description: Returns paginated list of users with optional filtering
      operationId: listUsers
      tags:
        - users
      parameters:
        - $ref: '#/components/parameters/LimitParam'
        - $ref: '#/components/parameters/OffsetParam'
        - name: status
          in: query
          description: Filter by user status
          schema:
            type: string
            enum: [active, inactive, suspended]
        - name: sort
          in: query
          description: Sort field (prefix with - for descending)
          schema:
            type: string
            default: created_at
            example: -created_at
      responses:
        '200':
          description: Successful response
          content:
            application/json:
              schema:
                type: object
                properties:
                  data:
                    type: array
                    items:
                      $ref: '#/components/schemas/User'
                  meta:
                    $ref: '#/components/schemas/PaginationMeta'
              examples:
                success:
                  summary: Successful user list
                  value:
                    data:
                      - id: "550e8400-e29b-41d4-a716-446655440000"
                        email: "user@example.com"
                        name: "John Doe"
                        status: "active"
                        created_at: "2025-01-15T10:30:00Z"
                    meta:
                      total: 1500
                      limit: 20
                      offset: 0
        '401':
          $ref: '#/components/responses/UnauthorizedError'
        '429':
          $ref: '#/components/responses/RateLimitError'
      security:
        - bearerAuth: []

    post:
      summary: Create user
      description: Creates a new user account
      operationId: createUser
      tags:
        - users
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/CreateUserRequest'
            examples:
              basic:
                summary: Basic user creation
                value:
                  email: "newuser@example.com"
                  name: "Jane Smith"
                  password: "SecureP@ssw0rd"
      responses:
        '201':
          description: User created successfully
          headers:
            Location:
              description: URL of created resource
              schema:
                type: string
                format: uri
                example: /api/v1/users/550e8400-e29b-41d4-a716-446655440000
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/User'
        '400':
          $ref: '#/components/responses/BadRequestError'
        '422':
          $ref: '#/components/responses/ValidationError'
      security:
        - bearerAuth: []

  /users/{userId}:
    parameters:
      - $ref: '#/components/parameters/UserIdParam'

    get:
      summary: Get user
      description: Returns a single user by ID
      operationId: getUser
      tags:
        - users
      responses:
        '200':
          description: Successful response
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/User'
        '404':
          $ref: '#/components/responses/NotFoundError'
      security:
        - bearerAuth: []

    patch:
      summary: Update user
      description: Partially updates user fields
      operationId: updateUser
      tags:
        - users
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/UpdateUserRequest'
      responses:
        '200':
          description: User updated
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/User'
        '404':
          $ref: '#/components/responses/NotFoundError'
        '422':
          $ref: '#/components/responses/ValidationError'
      security:
        - bearerAuth: []

    delete:
      summary: Delete user
      description: Permanently deletes a user
      operationId: deleteUser
      tags:
        - users
      responses:
        '204':
          description: User deleted successfully
        '404':
          $ref: '#/components/responses/NotFoundError'
      security:
        - bearerAuth: []

  /auth/login:
    post:
      summary: Login
      description: Authenticate user and return JWT tokens
      operationId: login
      tags:
        - auth
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              required:
                - email
                - password
              properties:
                email:
                  type: string
                  format: email
                password:
                  type: string
                  format: password
      responses:
        '200':
          description: Login successful
          content:
            application/json:
              schema:
                type: object
                properties:
                  accessToken:
                    type: string
                    description: JWT access token (expires in 15 min)
                  refreshToken:
                    type: string
                    description: JWT refresh token (expires in 7 days)
                  expiresIn:
                    type: integer
                    description: Access token expiration in seconds
                    example: 900
        '401':
          $ref: '#/components/responses/UnauthorizedError'

components:
  schemas:
    User:
      type: object
      required:
        - id
        - email
        - name
        - status
        - created_at
      properties:
        id:
          type: string
          format: uuid
          description: Unique user identifier
          example: "550e8400-e29b-41d4-a716-446655440000"
        email:
          type: string
          format: email
          description: User email address
          example: "user@example.com"
        name:
          type: string
          minLength: 1
          maxLength: 100
          description: User full name
          example: "John Doe"
        status:
          type: string
          enum: [active, inactive, suspended]
          description: User account status
          example: "active"
        created_at:
          type: string
          format: date-time
          description: Account creation timestamp (ISO 8601)
          example: "2025-01-15T10:30:00Z"
        updated_at:
          type: string
          format: date-time
          description: Last update timestamp (ISO 8601)
          example: "2025-01-20T14:25:00Z"

    CreateUserRequest:
      type: object
      required:
        - email
        - name
        - password
      properties:
        email:
          type: string
          format: email
          example: "newuser@example.com"
        name:
          type: string
          minLength: 1
          maxLength: 100
          example: "Jane Smith"
        password:
          type: string
          format: password
          minLength: 12
          description: Must contain uppercase, lowercase, number, and special character
          example: "SecureP@ssw0rd"

    UpdateUserRequest:
      type: object
      properties:
        name:
          type: string
          minLength: 1
          maxLength: 100
        email:
          type: string
          format: email
        status:
          type: string
          enum: [active, inactive, suspended]

    PaginationMeta:
      type: object
      properties:
        total:
          type: integer
          description: Total number of items
          example: 1500
        limit:
          type: integer
          description: Items per page
          example: 20
        offset:
          type: integer
          description: Number of items skipped
          example: 0
        hasMore:
          type: boolean
          description: Whether more items exist
          example: true

    Error:
      type: object
      required:
        - status
        - message
      properties:
        type:
          type: string
          format: uri
          description: Error type reference
          example: "https://api.example.com/errors/validation-error"
        title:
          type: string
          description: Human-readable error title
          example: "Validation Error"
        status:
          type: integer
          description: HTTP status code
          example: 422
        detail:
          type: string
          description: Detailed error message
          example: "Email address is already registered"
        instance:
          type: string
          description: Request path
          example: "/api/v1/users"
        errors:
          type: array
          description: Field-level errors
          items:
            type: object
            properties:
              field:
                type: string
                example: "email"
              code:
                type: string
                example: "DUPLICATE_EMAIL"
              message:
                type: string
                example: "Email address is already registered"
        traceId:
          type: string
          description: Request trace ID for debugging
          example: "abc123-def456"

  parameters:
    UserIdParam:
      name: userId
      in: path
      required: true
      description: User UUID
      schema:
        type: string
        format: uuid
      example: "550e8400-e29b-41d4-a716-446655440000"

    LimitParam:
      name: limit
      in: query
      description: Maximum number of items to return
      schema:
        type: integer
        minimum: 1
        maximum: 100
        default: 20
      example: 20

    OffsetParam:
      name: offset
      in: query
      description: Number of items to skip
      schema:
        type: integer
        minimum: 0
        default: 0
      example: 0

  responses:
    BadRequestError:
      description: Bad request (malformed syntax)
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/Error'
          example:
            status: 400
            message: "Invalid JSON syntax"

    UnauthorizedError:
      description: Unauthorized (authentication required)
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/Error'
          example:
            status: 401
            message: "Authentication required"

    NotFoundError:
      description: Resource not found
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/Error'
          example:
            status: 404
            message: "User not found"

    ValidationError:
      description: Validation error (semantically incorrect)
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/Error'
          example:
            type: "https://api.example.com/errors/validation-error"
            title: "Validation Error"
            status: 422
            detail: "Email address is already registered"
            errors:
              - field: "email"
                code: "DUPLICATE_EMAIL"
                message: "Email address is already registered"

    RateLimitError:
      description: Rate limit exceeded
      headers:
        X-RateLimit-Limit:
          description: Requests per window
          schema:
            type: integer
            example: 1000
        X-RateLimit-Remaining:
          description: Requests remaining
          schema:
            type: integer
            example: 0
        X-RateLimit-Reset:
          description: Window reset time (Unix timestamp)
          schema:
            type: integer
            example: 1640000060
        Retry-After:
          description: Seconds until retry allowed
          schema:
            type: integer
            example: 60
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/Error'
          example:
            status: 429
            message: "Rate limit exceeded. Try again in 60 seconds."

  securitySchemes:
    bearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT
      description: JWT access token obtained from /auth/login endpoint
```

---

## Key Concepts

### 1. Reusable Components

**Benefits:**
- DRY (Don't Repeat Yourself)
- Consistent schemas across endpoints
- Easier maintenance

**Usage:**
```yaml
components:
  schemas:
    User:
      type: object
      properties:
        id: { type: string }
        name: { type: string }

paths:
  /users/{id}:
    get:
      responses:
        '200':
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/User'
```

### 2. Request Bodies

```yaml
requestBody:
  required: true
  content:
    application/json:            # Content type
      schema:
        type: object
        required:
          - email
        properties:
          email:
            type: string
            format: email
      examples:                  # Multiple examples
        basic:
          value: { email: "user@example.com" }
        admin:
          value: { email: "admin@example.com", role: "admin" }
```

### 3. Response Examples

```yaml
responses:
  '200':
    description: Success
    content:
      application/json:
        schema:
          $ref: '#/components/schemas/User'
        examples:
          success:
            summary: Successful response
            value:
              id: "123"
              name: "John Doe"
```

### 4. Security Schemes

**Bearer Token (JWT):**
```yaml
components:
  securitySchemes:
    bearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT

paths:
  /users:
    get:
      security:
        - bearerAuth: []      # Requires auth
```

**API Key:**
```yaml
components:
  securitySchemes:
    apiKey:
      type: apiKey
      in: header
      name: X-API-Key
```

**OAuth2:**
```yaml
components:
  securitySchemes:
    oauth2:
      type: oauth2
      flows:
        authorizationCode:
          authorizationUrl: https://example.com/oauth/authorize
          tokenUrl: https://example.com/oauth/token
          scopes:
            read:users: Read user data
            write:users: Modify user data
```

---

## Best Practices

### 1. Use Descriptive Operation IDs

```yaml
paths:
  /users:
    get:
      operationId: listUsers      # GOOD: Used for SDK method names
```

Generates SDK code:
```javascript
// JavaScript SDK
api.listUsers({ limit: 20 });

// Python SDK
api.list_users(limit=20)
```

### 2. Include Examples

```yaml
schema:
  type: string
  format: email
  example: "user@example.com"    # GOOD: Shows expected format
```

### 3. Document Error Responses

```yaml
responses:
  '422':
    description: Validation error
    content:
      application/json:
        schema:
          $ref: '#/components/schemas/Error'
        example:                    # GOOD: Show error format
          status: 422
          message: "Invalid email"
```

### 4. Use Tags for Organization

```yaml
tags:
  - name: users
    description: User management
  - name: orders
    description: Order management

paths:
  /users:
    get:
      tags:
        - users                     # GOOD: Groups endpoints in docs
```

### 5. Document Deprecations

```yaml
paths:
  /legacy-endpoint:
    get:
      deprecated: true              # GOOD: Marks as deprecated
      description: |
        **DEPRECATED:** Use /v2/endpoint instead.
        This endpoint will be removed on 2025-06-01.
```

---

## Validation & Linting

### Spectral (OpenAPI Linter)

```bash
# Install
npm install -g @stoplight/spectral-cli

# Lint spec
spectral lint openapi.yaml
```

**Common Rules:**
- operation-operationId: Every operation must have operationId
- operation-description: Every operation must have description
- operation-tags: Every operation must have tags
- operation-success-response: Must have 2xx response
- no-$ref-siblings: Don't mix $ref with other properties

**Custom Rules (.spectral.yaml):**
```yaml
rules:
  operation-2xx-response:
    description: Every operation must have at least one 2xx response
    given: $.paths[*][*].responses
    then:
      field: '@key'
      function: pattern
      functionOptions:
        match: '^2'
```

### OpenAPI Validator

```bash
# Swagger Editor
docker run -p 8080:8080 swaggerapi/swagger-editor

# Visit http://localhost:8080
```

---

## Generating Documentation

### Swagger UI

```html
<!DOCTYPE html>
<html>
<head>
  <title>API Docs</title>
  <link rel="stylesheet" href="https://unpkg.com/swagger-ui-dist/swagger-ui.css">
</head>
<body>
  <div id="swagger-ui"></div>
  <script src="https://unpkg.com/swagger-ui-dist/swagger-ui-bundle.js"></script>
  <script>
    SwaggerUIBundle({
      url: '/openapi.yaml',
      dom_id: '#swagger-ui'
    });
  </script>
</body>
</html>
```

### Redoc

```html
<!DOCTYPE html>
<html>
<head>
  <title>API Docs</title>
</head>
<body>
  <redoc spec-url='/openapi.yaml'></redoc>
  <script src="https://cdn.jsdelivr.net/npm/redoc/bundles/redoc.standalone.js"></script>
</body>
</html>
```

---

## Generating Client SDKs

```bash
# OpenAPI Generator
openapi-generator generate \
  -i openapi.yaml \
  -g typescript-axios \
  -o ./sdk/typescript

# Supported generators: typescript-axios, python, java, go, ruby, php, etc.
```

---

## Tools & Resources

**Editors:**
- [Swagger Editor](https://editor.swagger.io/)
- [Stoplight Studio](https://stoplight.io/studio)

**Documentation:**
- [Swagger UI](https://swagger.io/tools/swagger-ui/)
- [Redoc](https://redocly.com/redoc)

**Validation:**
- [Spectral](https://stoplight.io/open-source/spectral)
- [OpenAPI Validator](https://github.com/IBM/openapi-validator)

**Code Generation:**
- [OpenAPI Generator](https://openapi-generator.tech/)
- [Swagger Codegen](https://github.com/swagger-api/swagger-codegen)

**Official Spec:**
- [OpenAPI 3.1 Specification](https://spec.openapis.org/oas/latest.html)
