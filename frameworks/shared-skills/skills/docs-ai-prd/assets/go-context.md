# Go CLAUDE.md Template

Copy and customize for Go projects.

---

```markdown
# [Project Name]

[One-line description of what this project does]

## Tech Stack

- **Go**: [1.21 / 1.22]
- **Framework**: [Standard library / Gin / Echo / Chi / Fiber]
- **Database**: [PostgreSQL / MySQL / SQLite] via [sqlx / pgx / GORM / ent]
- **Cache**: [Redis / go-cache / BigCache]
- **Message Queue**: [RabbitMQ / NATS / Kafka]
- **Testing**: [testify / gomock / mockery]

## Architecture

[2-3 sentences describing the overall design approach]

### Directory Structure

```
.
├── cmd/                      # Application entry points
│   └── server/
│       └── main.go           # Main entry point
├── internal/                 # Private application code
│   ├── api/                  # HTTP handlers
│   │   ├── handlers/         # Request handlers
│   │   ├── middleware/       # HTTP middleware
│   │   └── routes.go         # Route definitions
│   ├── service/              # Business logic
│   ├── repository/           # Data access layer
│   ├── model/                # Domain models
│   ├── dto/                  # Data transfer objects
│   └── config/               # Configuration
├── pkg/                      # Public reusable packages
│   ├── logger/               # Logging utilities
│   └── validator/            # Validation helpers
├── migrations/               # Database migrations
├── scripts/                  # Build/deploy scripts
├── docs/                     # Documentation
├── go.mod
├── go.sum
└── Makefile
```

### Key Patterns

- **Clean Architecture**: `handler → service → repository` layering
- **Dependency Injection**: Constructor injection, no frameworks
- **Interface-based**: Define interfaces where used, not implemented
- **Context propagation**: `context.Context` passed through all layers

### Data Flow

```
HTTP Request → Middleware → Handler → Service → Repository → Database
                                           ↓
HTTP Response ← Handler ← Service ← Repository ←──────────┘
```

## Conventions

### Naming

| Type | Convention | Example |
|------|------------|---------|
| Packages | lowercase, short | `user`, `auth` |
| Files | snake_case | `user_service.go` |
| Exported | PascalCase | `UserService`, `GetUser` |
| Unexported | camelCase | `userRepo`, `getByID` |
| Constants | PascalCase or SCREAMING_SNAKE | `MaxRetries`, `MAX_RETRIES` |
| Interfaces | -er suffix (single method) | `Reader`, `UserRepository` |
| Test files | `_test.go` suffix | `user_service_test.go` |

### File Organization

```go
// Order within a file:
// 1. Package declaration
// 2. Imports (stdlib, external, internal - goimports handles this)
// 3. Constants
// 4. Types (structs, interfaces)
// 5. Constructor functions (New*)
// 6. Methods (grouped by receiver)
// 7. Helper functions
```

### Interface Definition

```go
// Define interfaces where used, not where implemented
// Keep interfaces small (1-3 methods)

// In service/user.go
type userRepository interface {
    GetByID(ctx context.Context, id int64) (*model.User, error)
    Create(ctx context.Context, user *model.User) error
}

type UserService struct {
    repo userRepository
}
```

### Error Handling

```go
// Always handle errors explicitly
// Wrap errors with context
if err != nil {
    return fmt.Errorf("failed to get user %d: %w", id, err)
}

// Define domain errors
var (
    ErrUserNotFound = errors.New("user not found")
    ErrDuplicateEmail = errors.New("email already exists")
)
```

## Key Files

| Purpose | Location | Notes |
|---------|----------|-------|
| Entry point | `cmd/server/main.go` | Server bootstrap |
| Routes | `internal/api/routes.go` | Route registration |
| Config | `internal/config/config.go` | Configuration struct |
| Models | `internal/model/` | Domain entities |
| Handlers | `internal/api/handlers/` | HTTP handlers |
| Services | `internal/service/` | Business logic |
| Repositories | `internal/repository/` | Database access |

## Configuration

### Environment Variables

```bash
# .env
ENV=development
PORT=8080
DATABASE_URL=postgres://user:pass@localhost:5432/db?sslmode=disable
REDIS_URL=redis://localhost:6379
JWT_SECRET=your-secret-key
LOG_LEVEL=debug
```

### Config Struct Pattern

```go
// internal/config/config.go
type Config struct {
    Env         string `env:"ENV" envDefault:"development"`
    Port        int    `env:"PORT" envDefault:"8080"`
    DatabaseURL string `env:"DATABASE_URL,required"`
    JWTSecret   string `env:"JWT_SECRET,required"`
}

func Load() (*Config, error) {
    var cfg Config
    if err := env.Parse(&cfg); err != nil {
        return nil, err
    }
    return &cfg, nil
}
```

## Commands

```bash
# Development
make run                     # Run with hot reload (air)
go run ./cmd/server          # Run directly

# Build
make build                   # Build binary
go build -o bin/server ./cmd/server

# Database
make migrate-up              # Run migrations
make migrate-down            # Rollback migration
make migrate-create name=add_users  # Create migration

# Testing
make test                    # Run all tests
go test ./...                # Run all tests
go test -v ./internal/...    # Verbose
go test -cover ./...         # With coverage
go test -race ./...          # Race detection
make test-integration        # Integration tests

# Quality
make lint                    # golangci-lint
go fmt ./...                 # Format code
go vet ./...                 # Static analysis
make generate                # go generate ./...
```

## Important Context

### Technical Decisions

#### [Why Chi over Gin]
**Context**: Need lightweight HTTP router
**Decision**: Chi for stdlib compatibility and middleware chaining
**Trade-off**: Less batteries-included than Gin, but more idiomatic

#### [Why sqlx over GORM]
**Context**: Complex queries needed
**Decision**: sqlx for raw SQL with struct scanning
**Trade-off**: More boilerplate, but full control over queries

### Known Gotchas

- **nil slices vs empty slices**: `var s []int` (nil) vs `s := []int{}` (empty) - different JSON encoding
- **goroutine leaks**: Always handle context cancellation, use `errgroup`
- **defer in loops**: Deferred calls stack up, move to function
- **interface nil check**: Interface with nil concrete value is not nil
- **time.Time zero value**: Use `time.IsZero()`, not `== time.Time{}`

### Historical Context

- [Any migrations, refactors, or legacy patterns to know about]

## Testing

### Test Structure

```go
// internal/service/user_test.go
func TestUserService_GetByID(t *testing.T) {
    tests := []struct {
        name    string
        id      int64
        want    *model.User
        wantErr error
    }{
        {
            name: "existing user",
            id:   1,
            want: &model.User{ID: 1, Name: "Alice"},
        },
        {
            name:    "not found",
            id:      999,
            wantErr: ErrUserNotFound,
        },
    }

    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            // Arrange
            repo := &mockUserRepo{}
            svc := NewUserService(repo)

            // Act
            got, err := svc.GetByID(context.Background(), tt.id)

            // Assert
            if tt.wantErr != nil {
                require.ErrorIs(t, err, tt.wantErr)
                return
            }
            require.NoError(t, err)
            assert.Equal(t, tt.want, got)
        })
    }
}
```

### Mocking

```go
// Use mockery or manual mocks
// internal/service/mock_test.go
type mockUserRepo struct {
    mock.Mock
}

func (m *mockUserRepo) GetByID(ctx context.Context, id int64) (*model.User, error) {
    args := m.Called(ctx, id)
    if args.Get(0) == nil {
        return nil, args.Error(1)
    }
    return args.Get(0).(*model.User), args.Error(1)
}
```

## For AI Assistants

### When modifying this codebase:

- Follow existing patterns in similar files
- Add tests for new functionality
- Handle all errors explicitly
- Propagate context.Context through all functions
- Run `make lint && make test` before committing

### Patterns to follow:

- Constructor injection for dependencies
- Table-driven tests
- Wrap errors with context (`fmt.Errorf("...: %w", err)`)
- Small interfaces defined where used
- `internal/` for private packages

### Avoid:

- Global state and init() functions
- Naked returns (always name return values if using)
- Panic for expected errors
- Deep package nesting
- Circular dependencies between packages
```

---

## Quick Start Commands

Run these to gather context for a new Go project:

```bash
# Basic structure
tree -L 3 -I 'vendor|.git'

# Module info
cat go.mod | head -20

# Entry points
find . -name "main.go" -type f

# Find services/handlers
find . -name "*service*.go" -o -name "*handler*.go" | grep -v test

# Check for framework
grep -l "gin-gonic\|echo\|chi\|fiber" go.mod

# Database driver
grep -E "pgx|sqlx|gorm|ent" go.mod
```
