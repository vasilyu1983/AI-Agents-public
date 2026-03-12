# Error Handling Utilities

Centralized patterns for error classes, middleware, RFC 9457 Problem Details responses (obsoletes RFC 7807), and correlation IDs. Updated January 2026.

---

## Quick Reference

| Task | Library | Version | Notes |
|------|---------|---------|-------|
| Error classes | Native + Effect | effect 3.x | Typed errors with branded types |
| Validation | Zod | 3.24+ | Schema-based validation |
| RFC 9457 | Native | - | Problem Details for HTTP APIs (obsoletes RFC 7807) |
| Correlation IDs | cls-hooked / AsyncLocalStorage | - | Request tracing |

---

## File Structure

```text
src/
├── utils/
│   ├── errors.ts        # Error classes
│   └── correlation.ts   # Correlation ID utilities
├── middleware/
│   └── error-handler.ts # Error middleware
└── types/
    └── errors.ts        # Error types
```

---

## TypeScript/Node.js

### Error Classes (`src/utils/errors.ts`)

```typescript
/**
 * Base error class for all application errors.
 * NEVER expose stack traces to clients - log them server-side only.
 */
export class AppError extends Error {
  public readonly statusCode: number;
  public readonly code: string;
  public readonly isOperational: boolean;
  public readonly correlationId?: string;

  constructor(
    statusCode: number,
    message: string,
    code?: string,
    isOperational = true
  ) {
    super(message);
    this.statusCode = statusCode;
    this.code = code || this.constructor.name.toUpperCase();
    this.isOperational = isOperational;
    Error.captureStackTrace(this, this.constructor);
  }

  /**
   * Convert to RFC 9457 response format (Problem Details).
   * NEVER includes stack trace.
   */
  toJSON(instance?: string): ErrorResponse {
    return {
      type: `https://api.example.com/errors/${this.code.toLowerCase()}`,
      title: this.code.replace(/_/g, ' '),
      status: this.statusCode,
      detail: this.message,
      instance,
      correlationId: this.correlationId,
    };
  }
}

// 400 Bad Request
export class BadRequestError extends AppError {
  constructor(message = 'Bad request') {
    super(400, message, 'BAD_REQUEST');
  }
}

// 401 Unauthorized
export class UnauthorizedError extends AppError {
  constructor(message = 'Unauthorized') {
    super(401, message, 'UNAUTHORIZED');
  }
}

// 403 Forbidden
export class ForbiddenError extends AppError {
  constructor(message = 'Forbidden') {
    super(403, message, 'FORBIDDEN');
  }
}

// 404 Not Found
export class NotFoundError extends AppError {
  constructor(resource = 'Resource') {
    super(404, `${resource} not found`, 'NOT_FOUND');
  }
}

// 409 Conflict
export class ConflictError extends AppError {
  constructor(message = 'Resource already exists') {
    super(409, message, 'CONFLICT');
  }
}

// 422 Validation Error
export class ValidationError extends AppError {
  public readonly errors: Record<string, string[]>;

  constructor(message = 'Validation failed', errors: Record<string, string[]> = {}) {
    super(422, message, 'VALIDATION_ERROR');
    this.errors = errors;
  }

  override toJSON(instance?: string): ErrorResponse {
    return {
      ...super.toJSON(instance),
      errors: this.errors,
    };
  }
}

// 429 Rate Limit
export class RateLimitError extends AppError {
  public readonly retryAfter?: number;

  constructor(message = 'Too many requests', retryAfter?: number) {
    super(429, message, 'RATE_LIMIT_EXCEEDED');
    this.retryAfter = retryAfter;
  }
}

// 500 Internal Server Error
export class InternalError extends AppError {
  constructor(message = 'Internal server error') {
    super(500, message, 'INTERNAL_ERROR', false);
  }
}

// 503 Service Unavailable
export class ServiceUnavailableError extends AppError {
  constructor(message = 'Service temporarily unavailable') {
    super(503, message, 'SERVICE_UNAVAILABLE');
  }
}
```

### RFC 9457 Problem Details Type

```typescript
// src/types/errors.ts
export interface ErrorResponse {
  type: string;
  title: string;
  status: number;
  detail: string;
  instance?: string;
  correlationId?: string;
  errors?: Record<string, string[]>;
}
```

### Correlation ID Utilities (`src/utils/correlation.ts`)

```typescript
import { AsyncLocalStorage } from 'node:async_hooks';
import { randomUUID } from 'node:crypto';

interface RequestContext {
  correlationId: string;
  startTime: number;
}

export const asyncLocalStorage = new AsyncLocalStorage<RequestContext>();

export const getCorrelationId = (): string | undefined => {
  return asyncLocalStorage.getStore()?.correlationId;
};

export const generateCorrelationId = (): string => {
  return randomUUID();
};

/**
 * Middleware to initialize correlation ID for each request.
 * Checks X-Correlation-ID header first, generates if missing.
 */
export const correlationMiddleware = (
  req: Request,
  _res: Response,
  next: NextFunction
): void => {
  const correlationId =
    (req.headers['x-correlation-id'] as string) || generateCorrelationId();

  asyncLocalStorage.run(
    { correlationId, startTime: Date.now() },
    () => {
      next();
    }
  );
};
```

### Error Handler Middleware (`src/middleware/error-handler.ts`)

```typescript
import type { Request, Response, NextFunction } from 'express';
import { ZodError } from 'zod';
import { AppError, ValidationError, InternalError } from '@/utils/errors';
import { getCorrelationId } from '@/utils/correlation';
import { logger } from '@/utils/logger';
import type { ErrorResponse } from '@/types/errors';

/**
 * Central error handler middleware.
 * CRITICAL: Never expose stack traces or internal details to clients.
 */
export const errorHandler = (
  err: Error,
  req: Request,
  res: Response,
  _next: NextFunction
): void => {
  const correlationId = getCorrelationId();

  // Always log full error details server-side
  logger.error({
    correlationId,
    error: err.message,
    stack: err.stack, // Log stack server-side only
    method: req.method,
    path: req.path,
    statusCode: err instanceof AppError ? err.statusCode : 500,
  });

  // Handle Zod validation errors
  if (err instanceof ZodError) {
    const errors: Record<string, string[]> = {};
    err.errors.forEach((e) => {
      const path = e.path.join('.');
      if (!errors[path]) errors[path] = [];
      errors[path].push(e.message);
    });

    const response: ErrorResponse = {
      type: 'https://api.example.com/errors/validation',
      title: 'Validation Error',
      status: 422,
      detail: 'Request validation failed',
      instance: req.path,
      correlationId,
      errors,
    };
    res.status(422).json(response);
    return;
  }

  // Handle AppError instances
  if (err instanceof AppError) {
    const response = err.toJSON(req.path);
    response.correlationId = correlationId;

    if (err instanceof ValidationError && Object.keys(err.errors).length > 0) {
      response.errors = err.errors;
    }

    res.status(err.statusCode).json(response);
    return;
  }

  // Handle unknown errors - NEVER expose details
  const response: ErrorResponse = {
    type: 'https://api.example.com/errors/internal',
    title: 'Internal Server Error',
    status: 500,
    detail: 'An unexpected error occurred', // Generic message always
    instance: req.path,
    correlationId,
  };

  res.status(500).json(response);
};

// 404 handler for undefined routes
export const notFoundHandler = (req: Request, res: Response): void => {
  const correlationId = getCorrelationId();

  const response: ErrorResponse = {
    type: 'https://api.example.com/errors/not-found',
    title: 'Not Found',
    status: 404,
    detail: `Route ${req.method} ${req.path} not found`,
    instance: req.path,
    correlationId,
  };
  res.status(404).json(response);
};
```

### Express App Setup

```typescript
// src/app.ts
import express from 'express';
import { correlationMiddleware } from '@/utils/correlation';
import { errorHandler, notFoundHandler } from '@/middleware/error-handler';

const app = express();

// Correlation ID middleware (must be first)
app.use(correlationMiddleware);

// Routes
app.use('/api/users', userRouter);
app.use('/api/orders', orderRouter);

// Error handlers (must be last)
app.use(notFoundHandler);
app.use(errorHandler);

export { app };
```

---

## Effect Library Pattern (TypeScript)

For typed error handling with compile-time guarantees, use Effect:

```typescript
import { Effect, Either, pipe } from 'effect';

// Define branded error types
class UserNotFoundError {
  readonly _tag = 'UserNotFoundError';
  constructor(readonly userId: string) {}
}

class ValidationError {
  readonly _tag = 'ValidationError';
  constructor(readonly errors: Record<string, string[]>) {}
}

class DatabaseError {
  readonly _tag = 'DatabaseError';
  constructor(readonly cause: unknown) {}
}

// Service with typed errors
const getUser = (
  userId: string
): Effect.Effect<User, UserNotFoundError | DatabaseError> =>
  pipe(
    Effect.tryPromise({
      try: () => db.user.findUnique({ where: { id: userId } }),
      catch: (error) => new DatabaseError(error),
    }),
    Effect.flatMap((user) =>
      user
        ? Effect.succeed(user)
        : Effect.fail(new UserNotFoundError(userId))
    )
  );

// Handle errors explicitly
const getUserHandler = (userId: string) =>
  pipe(
    getUser(userId),
    Effect.catchTags({
      UserNotFoundError: (err) =>
        Effect.succeed({ status: 404, body: { error: `User ${err.userId} not found` } }),
      DatabaseError: () =>
        Effect.succeed({ status: 500, body: { error: 'Database error' } }),
    })
  );

// Run the effect
const result = await Effect.runPromise(getUserHandler('123'));
```

### Effect Error Mapping to HTTP

```typescript
import { Effect, Match } from 'effect';

type AppErrors = UserNotFoundError | ValidationError | DatabaseError;

const errorToResponse = (error: AppErrors): ErrorResponse =>
  Match.value(error).pipe(
    Match.tag('UserNotFoundError', (e) => ({
      type: 'https://api.example.com/errors/not-found',
      title: 'Not Found',
      status: 404,
      detail: `User ${e.userId} not found`,
    })),
    Match.tag('ValidationError', (e) => ({
      type: 'https://api.example.com/errors/validation',
      title: 'Validation Error',
      status: 422,
      detail: 'Validation failed',
      errors: e.errors,
    })),
    Match.tag('DatabaseError', () => ({
      type: 'https://api.example.com/errors/internal',
      title: 'Internal Server Error',
      status: 500,
      detail: 'An unexpected error occurred',
    })),
    Match.exhaustive
  );
```

---

## Python (FastAPI)

### Error Classes (`src/utils/errors.py`)

```python
from typing import Any
from contextvars import ContextVar

# Correlation ID context variable
correlation_id_var: ContextVar[str | None] = ContextVar("correlation_id", default=None)

def get_correlation_id() -> str | None:
    return correlation_id_var.get()

class AppError(Exception):
    """Base error class. Never expose stack traces to clients."""

    def __init__(
        self,
        status_code: int,
        message: str,
        code: str | None = None,
        errors: dict[str, list[str]] | None = None,
    ):
        self.status_code = status_code
        self.message = message
        self.code = code or self.__class__.__name__.upper()
        self.errors = errors or {}
        super().__init__(message)

    def to_dict(self, instance: str | None = None) -> dict[str, Any]:
        """Convert to RFC 9457 format (Problem Details). Never includes stack trace."""
        response = {
            "type": f"https://api.example.com/errors/{self.code.lower()}",
            "title": self.code.replace("_", " ").title(),
            "status": self.status_code,
            "detail": self.message,
        }
        if instance:
            response["instance"] = instance
        if correlation_id := get_correlation_id():
            response["correlationId"] = correlation_id
        if self.errors:
            response["errors"] = self.errors
        return response


class BadRequestError(AppError):
    def __init__(self, message: str = "Bad request"):
        super().__init__(400, message, "BAD_REQUEST")


class UnauthorizedError(AppError):
    def __init__(self, message: str = "Unauthorized"):
        super().__init__(401, message, "UNAUTHORIZED")


class ForbiddenError(AppError):
    def __init__(self, message: str = "Forbidden"):
        super().__init__(403, message, "FORBIDDEN")


class NotFoundError(AppError):
    def __init__(self, resource: str = "Resource"):
        super().__init__(404, f"{resource} not found", "NOT_FOUND")


class ConflictError(AppError):
    def __init__(self, message: str = "Resource already exists"):
        super().__init__(409, message, "CONFLICT")


class ValidationError(AppError):
    def __init__(
        self,
        message: str = "Validation failed",
        errors: dict[str, list[str]] | None = None,
    ):
        super().__init__(422, message, "VALIDATION_ERROR", errors)


class RateLimitError(AppError):
    def __init__(self, message: str = "Too many requests", retry_after: int | None = None):
        super().__init__(429, message, "RATE_LIMIT_EXCEEDED")
        self.retry_after = retry_after


class ServiceUnavailableError(AppError):
    def __init__(self, message: str = "Service temporarily unavailable"):
        super().__init__(503, message, "SERVICE_UNAVAILABLE")
```

### Correlation ID Middleware (`src/middleware/correlation.py`)

```python
import uuid
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from src.utils.errors import correlation_id_var

class CorrelationIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Get from header or generate new
        correlation_id = request.headers.get("X-Correlation-ID") or str(uuid.uuid4())

        # Set in context variable
        token = correlation_id_var.set(correlation_id)

        try:
            response = await call_next(request)
            # Add to response headers
            response.headers["X-Correlation-ID"] = correlation_id
            return response
        finally:
            correlation_id_var.reset(token)
```

### Exception Handlers (`src/middleware/error_handler.py`)

```python
import traceback
from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from src.utils.errors import AppError, get_correlation_id
from src.utils.logger import logger

async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    """Handle AppError instances. Never expose stack traces."""
    correlation_id = get_correlation_id()

    # Log full details server-side
    logger.error(
        f"{exc.code}: {exc.message}",
        extra={
            "correlation_id": correlation_id,
            "path": str(request.url.path),
            "status_code": exc.status_code,
        },
    )

    return JSONResponse(
        status_code=exc.status_code,
        content=exc.to_dict(str(request.url.path)),
    )


async def validation_error_handler(
    request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    """Handle Pydantic validation errors."""
    correlation_id = get_correlation_id()

    errors: dict[str, list[str]] = {}
    for error in exc.errors():
        field = ".".join(str(loc) for loc in error["loc"][1:])
        if field not in errors:
            errors[field] = []
        errors[field].append(error["msg"])

    logger.warning(
        "Validation error",
        extra={
            "correlation_id": correlation_id,
            "path": str(request.url.path),
            "errors": errors,
        },
    )

    response = {
        "type": "https://api.example.com/errors/validation",
        "title": "Validation Error",
        "status": 422,
        "detail": "Request validation failed",
        "instance": str(request.url.path),
        "correlationId": correlation_id,
        "errors": errors,
    }

    return JSONResponse(status_code=422, content=response)


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle unexpected errors. NEVER expose stack traces."""
    correlation_id = get_correlation_id()

    # Log full stack trace server-side only
    logger.exception(
        "Unhandled exception",
        extra={
            "correlation_id": correlation_id,
            "path": str(request.url.path),
        },
    )

    # Generic response - no details exposed
    response = {
        "type": "https://api.example.com/errors/internal",
        "title": "Internal Server Error",
        "status": 500,
        "detail": "An unexpected error occurred",
        "instance": str(request.url.path),
        "correlationId": correlation_id,
    }

    return JSONResponse(status_code=500, content=response)
```

### FastAPI App Setup

```python
# src/main.py
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from src.utils.errors import AppError
from src.middleware.correlation import CorrelationIdMiddleware
from src.middleware.error_handler import (
    app_error_handler,
    validation_error_handler,
    unhandled_exception_handler,
)

app = FastAPI()

# Middleware (order matters)
app.add_middleware(CorrelationIdMiddleware)

# Exception handlers
app.add_exception_handler(AppError, app_error_handler)
app.add_exception_handler(RequestValidationError, validation_error_handler)
app.add_exception_handler(Exception, unhandled_exception_handler)
```

---

## Go (Fiber)

### Error Types with Correlation (`internal/utils/errors.go`)

```go
package utils

import (
	"context"
	"fmt"
)

type correlationKey struct{}

func WithCorrelationID(ctx context.Context, id string) context.Context {
	return context.WithValue(ctx, correlationKey{}, id)
}

func GetCorrelationID(ctx context.Context) string {
	if id, ok := ctx.Value(correlationKey{}).(string); ok {
		return id
	}
	return ""
}

type AppError struct {
	StatusCode    int               `json:"-"`
	Code          string            `json:"code"`
	Message       string            `json:"message"`
	Errors        map[string]string `json:"errors,omitempty"`
	CorrelationID string            `json:"correlationId,omitempty"`
}

func (e *AppError) Error() string {
	return e.Message
}

func (e *AppError) WithCorrelationID(id string) *AppError {
	e.CorrelationID = id
	return e
}

func NewBadRequestError(message string) *AppError {
	return &AppError{StatusCode: 400, Code: "BAD_REQUEST", Message: message}
}

func NewUnauthorizedError(message string) *AppError {
	return &AppError{StatusCode: 401, Code: "UNAUTHORIZED", Message: message}
}

func NewForbiddenError(message string) *AppError {
	return &AppError{StatusCode: 403, Code: "FORBIDDEN", Message: message}
}

func NewNotFoundError(resource string) *AppError {
	return &AppError{StatusCode: 404, Code: "NOT_FOUND", Message: fmt.Sprintf("%s not found", resource)}
}

func NewConflictError(message string) *AppError {
	return &AppError{StatusCode: 409, Code: "CONFLICT", Message: message}
}

func NewValidationError(message string, errors map[string]string) *AppError {
	return &AppError{StatusCode: 422, Code: "VALIDATION_ERROR", Message: message, Errors: errors}
}

func NewInternalError() *AppError {
	return &AppError{StatusCode: 500, Code: "INTERNAL_ERROR", Message: "An unexpected error occurred"}
}
```

### Error Handler with Correlation (`internal/middleware/error_handler.go`)

```go
package middleware

import (
	"fmt"
	"strings"

	"github.com/gofiber/fiber/v2"
	"github.com/google/uuid"
	"myapp/internal/utils"
	"myapp/internal/logger"
)

type ErrorResponse struct {
	Type          string            `json:"type"`
	Title         string            `json:"title"`
	Status        int               `json:"status"`
	Detail        string            `json:"detail"`
	Instance      string            `json:"instance"`
	CorrelationID string            `json:"correlationId,omitempty"`
	Errors        map[string]string `json:"errors,omitempty"`
}

// CorrelationMiddleware adds correlation ID to each request
func CorrelationMiddleware() fiber.Handler {
	return func(c *fiber.Ctx) error {
		correlationID := c.Get("X-Correlation-ID")
		if correlationID == "" {
			correlationID = uuid.New().String()
		}
		c.Locals("correlationId", correlationID)
		c.Set("X-Correlation-ID", correlationID)
		return c.Next()
	}
}

// ErrorHandler handles all errors. Never exposes stack traces.
func ErrorHandler(c *fiber.Ctx, err error) error {
	correlationID, _ := c.Locals("correlationId").(string)

	// Log full error server-side
	logger.Error("Request error",
		"correlationId", correlationID,
		"path", c.Path(),
		"error", err.Error(),
	)

	if appErr, ok := err.(*utils.AppError); ok {
		response := ErrorResponse{
			Type:          fmt.Sprintf("https://api.example.com/errors/%s", strings.ToLower(appErr.Code)),
			Title:         strings.ReplaceAll(appErr.Code, "_", " "),
			Status:        appErr.StatusCode,
			Detail:        appErr.Message,
			Instance:      c.Path(),
			CorrelationID: correlationID,
			Errors:        appErr.Errors,
		}
		return c.Status(appErr.StatusCode).JSON(response)
	}

	// Handle Fiber errors
	if fiberErr, ok := err.(*fiber.Error); ok {
		response := ErrorResponse{
			Type:          "https://api.example.com/errors/http",
			Title:         "HTTP Error",
			Status:        fiberErr.Code,
			Detail:        fiberErr.Message,
			Instance:      c.Path(),
			CorrelationID: correlationID,
		}
		return c.Status(fiberErr.Code).JSON(response)
	}

	// Unknown error - generic response, no details
	response := ErrorResponse{
		Type:          "https://api.example.com/errors/internal",
		Title:         "Internal Server Error",
		Status:        500,
		Detail:        "An unexpected error occurred",
		Instance:      c.Path(),
		CorrelationID: correlationID,
	}
	return c.Status(500).JSON(response)
}
```

---

## Usage Examples

### Throwing Errors with Correlation

```typescript
// TypeScript
import { NotFoundError, ValidationError } from '@/utils/errors';
import { getCorrelationId } from '@/utils/correlation';

const getUser = async (id: string) => {
  const user = await db.user.findUnique({ where: { id } });
  if (!user) {
    const error = new NotFoundError('User');
    error.correlationId = getCorrelationId();
    throw error;
  }
  return user;
};
```

```python
# Python
from src.utils.errors import NotFoundError, ConflictError

async def get_user(user_id: int) -> User:
    user = await repo.get_by_id(user_id)
    if not user:
        raise NotFoundError("User")  # Correlation ID added by middleware
    return user
```

---

## RFC 9457 Problem Details Response Format

All errors follow [RFC 9457](https://www.rfc-editor.org/rfc/rfc9457) (obsoletes RFC 7807) with correlation ID:

```json
{
  "type": "https://api.example.com/errors/not-found",
  "title": "Not Found",
  "status": 404,
  "detail": "User not found",
  "instance": "/api/users/123",
  "correlationId": "550e8400-e29b-41d4-a716-446655440000",
  "errors": {}
}
```

---

## Security Checklist

- [ ] **Never** expose stack traces in API responses (any environment)
- [ ] **Never** expose internal error messages for 500 errors
- [ ] **Always** log full error details server-side with correlation ID
- [ ] **Always** use generic messages for unexpected errors
- [ ] **Always** include correlation ID in error responses for debugging
- [ ] **Validate** all user input before processing
- [ ] **Sanitize** error messages to prevent information disclosure

---

## Anti-Patterns

```typescript
// BAD: Exposing stack traces
const response = {
  error: err.message,
  stack: err.stack, // NEVER DO THIS
};

// BAD: Exposing internal details in non-production
detail: process.env.NODE_ENV === 'production'
  ? 'An error occurred'
  : err.message,  // Still exposes details in dev/staging

// BAD: No correlation ID
logger.error(err.message); // Can't trace across services

// GOOD: Generic message, logged details
logger.error({ correlationId, error: err.message, stack: err.stack });
res.json({ detail: 'An unexpected error occurred', correlationId });

// GOOD: Effect for typed errors
const result = Effect.runPromise(
  pipe(getUser(id), Effect.catchAll(errorToResponse))
);
```

---

## Dependencies

### TypeScript/Node.js

```json
{
  "zod": "^3.24.0",
  "effect": "^3.10.0"
}
```

### Python

```txt
fastapi>=0.115.0
pydantic>=2.10.0
```

### Go

```bash
go get github.com/gofiber/fiber/v2
go get github.com/google/uuid
```
