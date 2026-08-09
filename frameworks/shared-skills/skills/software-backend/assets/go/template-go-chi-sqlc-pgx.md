# Backend Engineering - Go + chi + sqlc + pgx Template

*Purpose: Auditable SQL-first Go backend for teams that want explicit queries, lean HTTP routing, and predictable production behavior.*

---

# When to Use

Use this template when building:

- Go REST APIs with PostgreSQL
- fintech, ops, or compliance-sensitive services
- low-abstraction services where SQL should stay visible in review
- systems that need simple deployment and efficient concurrency

Prefer this over GORM when query control and schema review matter more than ORM convenience.

---

# TEMPLATE STARTS HERE

# 1. Project Overview

**Tech Stack:**
- [ ] Go 1.24+ (or org-approved stable)
- [ ] chi router
- [ ] sqlc
- [ ] pgxpool
- [ ] PostgreSQL
- [ ] Testify

**Project Name:** `{{project_name}}`

---

# 2. Project Structure

```text
project-root/
|-- cmd/api/main.go
|-- internal/
|   |-- config/config.go
|   |-- db/
|   |   |-- pool.go
|   |   |-- query.sql
|   |   `-- queries.sql.go
|   |-- http/
|   |   |-- router.go
|   |   |-- users.go
|   |   `-- health.go
|   `-- problem/problem.go
|-- sql/schema.sql
|-- sqlc.yaml
|-- go.mod
`-- .env.example
```

---

# 3. Configuration

## .env.example

```env
APP_PORT=8080
DATABASE_URL=postgres://postgres:postgres@localhost:5432/app?sslmode=disable
```

## internal/config/config.go

```go
package config

import (
	"errors"
	"os"
)

type Config struct {
	AppPort     string
	DatabaseURL string
}

func Load() (Config, error) {
	cfg := Config{
		AppPort:     getEnv("APP_PORT", "8080"),
		DatabaseURL: os.Getenv("DATABASE_URL"),
	}

	if cfg.DatabaseURL == "" {
		return Config{}, errors.New("DATABASE_URL is required")
	}

	return cfg, nil
}

func getEnv(key, fallback string) string {
	if value := os.Getenv(key); value != "" {
		return value
	}
	return fallback
}
```

---

# 4. Database Layer

## sql/schema.sql

```sql
CREATE TABLE IF NOT EXISTS users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email TEXT NOT NULL UNIQUE,
  full_name TEXT NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

## internal/db/query.sql

```sql
-- name: ListUsers :many
SELECT id, email, full_name, created_at
FROM users
ORDER BY created_at DESC;

-- name: GetUserByEmail :one
SELECT id, email, full_name, created_at
FROM users
WHERE email = $1;

-- name: CreateUser :one
INSERT INTO users (email, full_name)
VALUES ($1, $2)
RETURNING id, email, full_name, created_at;
```

## sqlc.yaml

```yaml
version: "2"
sql:
  - engine: "postgresql"
    schema: "sql/schema.sql"
    queries: "internal/db/query.sql"
    gen:
      go:
        package: "db"
        out: "internal/db"
        sql_package: "pgx/v5"
```

## internal/db/pool.go

```go
package db

import (
	"context"

	"github.com/jackc/pgx/v5/pgxpool"
)

func NewPool(ctx context.Context, databaseURL string) (*pgxpool.Pool, error) {
	cfg, err := pgxpool.ParseConfig(databaseURL)
	if err != nil {
		return nil, err
	}

	cfg.MaxConns = 20
	cfg.MinConns = 2
	cfg.MaxConnIdleTime = 30_000_000_000

	return pgxpool.NewWithConfig(ctx, cfg)
}
```

---

# 5. HTTP Layer

## internal/problem/problem.go

```go
package problem

import (
	"encoding/json"
	"net/http"
)

type Details struct {
	Type     string `json:"type"`
	Title    string `json:"title"`
	Status   int    `json:"status"`
	Detail   string `json:"detail"`
	Instance string `json:"instance"`
}

func Write(w http.ResponseWriter, r *http.Request, status int, typ, title, detail string) {
	w.Header().Set("Content-Type", "application/problem+json")
	w.WriteHeader(status)
	_ = json.NewEncoder(w).Encode(Details{
		Type:     typ,
		Title:    title,
		Status:   status,
		Detail:   detail,
		Instance: r.URL.Path,
	})
}
```

## internal/http/users.go

```go
package http

import (
	"encoding/json"
	"net/http"

	"your-api/internal/db"
	"your-api/internal/problem"
)

type UsersHandler struct {
	queries *db.Queries
}

type createUserRequest struct {
	Email    string `json:"email"`
	FullName string `json:"fullName"`
}

func NewUsersHandler(queries *db.Queries) *UsersHandler {
	return &UsersHandler{queries: queries}
}

func (h *UsersHandler) List(w http.ResponseWriter, r *http.Request) {
	users, err := h.queries.ListUsers(r.Context())
	if err != nil {
		problem.Write(w, r, http.StatusInternalServerError, "https://api.example.com/problems/internal", "Internal Server Error", "Failed to load users.")
		return
	}

	w.Header().Set("Content-Type", "application/json")
	_ = json.NewEncoder(w).Encode(users)
}

func (h *UsersHandler) Create(w http.ResponseWriter, r *http.Request) {
	var input createUserRequest
	if err := json.NewDecoder(r.Body).Decode(&input); err != nil {
		problem.Write(w, r, http.StatusBadRequest, "https://api.example.com/problems/invalid-json", "Bad Request", "Invalid JSON body.")
		return
	}

	user, err := h.queries.CreateUser(r.Context(), db.CreateUserParams{
		Email:    input.Email,
		FullName: input.FullName,
	})
	if err != nil {
		problem.Write(w, r, http.StatusConflict, "https://api.example.com/problems/email-conflict", "Conflict", "A user with this email already exists.")
		return
	}

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusCreated)
	_ = json.NewEncoder(w).Encode(user)
}
```

## internal/http/router.go

```go
package http

import (
	"net/http"
	"time"

	"github.com/go-chi/chi/v5"
	"github.com/go-chi/chi/v5/middleware"
	"your-api/internal/db"
)

func NewRouter(queries *db.Queries) http.Handler {
	r := chi.NewRouter()
	r.Use(middleware.RequestID)
	r.Use(middleware.RealIP)
	r.Use(middleware.Logger)
	r.Use(middleware.Timeout(30 * time.Second))

	users := NewUsersHandler(queries)

	r.Get("/health/live", func(w http.ResponseWriter, _ *http.Request) {
		w.WriteHeader(http.StatusOK)
		_, _ = w.Write([]byte(`{"status":"ok"}`))
	})

	r.Get("/users", users.List)
	r.Post("/users", users.Create)
	return r
}
```

## cmd/api/main.go

```go
package main

import (
	"context"
	"log"
	"net/http"

	"your-api/internal/config"
	"your-api/internal/db"
	apphttp "your-api/internal/http"
)

func main() {
	ctx := context.Background()

	cfg, err := config.Load()
	if err != nil {
		log.Fatal(err)
	}

	pool, err := db.NewPool(ctx, cfg.DatabaseURL)
	if err != nil {
		log.Fatal(err)
	}
	defer pool.Close()

	queries := db.New(pool)
	router := apphttp.NewRouter(queries)

	log.Fatal(http.ListenAndServe(":"+cfg.AppPort, router))
}
```

---

# 6. Testing

```go
package http_test

import (
	"net/http"
	"net/http/httptest"
	"testing"

	"github.com/stretchr/testify/require"
)

func TestHealth(t *testing.T) {
	req := httptest.NewRequest(http.MethodGet, "/health/live", nil)
	rec := httptest.NewRecorder()

	router := buildTestRouter(t)
	router.ServeHTTP(rec, req)

	require.Equal(t, http.StatusOK, rec.Code)
}
```

---

# 7. Operational Notes

- Keep SQL reviewed in `query.sql` rather than scattered through handlers.
- Use pgx pool metrics and query latency logging from the first production deployment.
- Keep request deadlines and DB statement timeouts aligned.
- Prefer explicit transactions around multi-step writes.

---

# END

**Next Steps**
1. Run `go generate` or `sqlc generate`.
2. Apply `sql/schema.sql` to Postgres.
3. Start the service with `go run ./cmd/api`.
4. Add auth, rate limiting, and OpenTelemetry before production.
