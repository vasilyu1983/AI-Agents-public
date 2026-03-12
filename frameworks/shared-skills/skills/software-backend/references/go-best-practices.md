# Go Backend Best Practices

Comprehensive guide for building production-grade backend services with Go.

## Contents

- [Core Go Principles](#core-go-principles)
- [Concurrency Patterns](#concurrency-patterns)
- [Error Handling](#error-handling)
- [HTTP Server Best Practices](#http-server-best-practices)
- [Database Patterns](#database-patterns)
- [Performance Optimization](#performance-optimization)
- [Testing Best Practices](#testing-best-practices)
- [Logging Best Practices](#logging-best-practices)
- [Configuration Management](#configuration-management)
- [Security Best Practices](#security-best-practices)
- [Deployment Patterns](#deployment-patterns)
- [Common Pitfalls](#common-pitfalls)
- [Resources](#resources)

---

## Core Go Principles

### Effective Go Idioms

**Simplicity over Cleverness**
```go
// Good: Clear and straightforward
func isValid(user *User) bool {
    return user != nil && user.Email != ""
}

// Avoid: Overly clever one-liners
func isValid(user *User) bool {
    return !(user == nil || user.Email == "")
}
```

**Accept Interfaces, Return Structs**
```go
// Good: Interface parameter for flexibility
type Storage interface {
    Save(data []byte) error
}

func ProcessData(s Storage, data []byte) error {
    // Process and save
    return s.Save(data)
}

// Avoid: Concrete parameter limits testability
func ProcessData(db *PostgresDB, data []byte) error {
    return db.Save(data)
}
```

**Error Handling**
```go
// Good: Check errors immediately
result, err := doSomething()
if err != nil {
    return fmt.Errorf("do something: %w", err) // Wrap errors
}

// Good: Custom error types for domain logic
type ValidationError struct {
    Field string
    Msg   string
}

func (e *ValidationError) Error() string {
    return fmt.Sprintf("%s: %s", e.Field, e.Msg)
}
```

---

## Concurrency Patterns

### Goroutine Management

**Worker Pool Pattern**
```go
type Job struct {
    ID   int
    Data string
}

func worker(id int, jobs <-chan Job, results chan<- int) {
    for job := range jobs {
        fmt.Printf("Worker %d processing job %d\n", id, job.ID)
        // Process job
        results <- job.ID
    }
}

func main() {
    numWorkers := 5
    jobs := make(chan Job, 100)
    results := make(chan int, 100)

    // Start workers
    for w := 1; w <= numWorkers; w++ {
        go worker(w, jobs, results)
    }

    // Send jobs
    for j := 1; j <= 100; j++ {
        jobs <- Job{ID: j, Data: fmt.Sprintf("data-%d", j)}
    }
    close(jobs)

    // Collect results
    for a := 1; a <= 100; a++ {
        <-results
    }
}
```

**Context for Cancellation**
```go
func fetchData(ctx context.Context, url string) ([]byte, error) {
    req, err := http.NewRequestWithContext(ctx, "GET", url, nil)
    if err != nil {
        return nil, err
    }

    resp, err := http.DefaultClient.Do(req)
    if err != nil {
        return nil, err
    }
    defer resp.Body.Close()

    return io.ReadAll(resp.Body)
}

// Usage with timeout
ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
defer cancel()

data, err := fetchData(ctx, "https://api.example.com/data")
```

**Fan-Out, Fan-In Pattern**
```go
func fanOut(input <-chan int, workers int) []<-chan int {
    channels := make([]<-chan int, workers)
    for i := 0; i < workers; i++ {
        channels[i] = worker(input)
    }
    return channels
}

func fanIn(channels ...<-chan int) <-chan int {
    out := make(chan int)
    var wg sync.WaitGroup

    for _, c := range channels {
        wg.Add(1)
        go func(ch <-chan int) {
            defer wg.Done()
            for n := range ch {
                out <- n
            }
        }(c)
    }

    go func() {
        wg.Wait()
        close(out)
    }()

    return out
}
```

### Synchronization

**Use sync.WaitGroup for Goroutine Coordination**
```go
func processItems(items []string) {
    var wg sync.WaitGroup

    for _, item := range items {
        wg.Add(1)
        go func(i string) {
            defer wg.Done()
            process(i)
        }(item) // Pass item to avoid closure issues
    }

    wg.Wait() // Wait for all goroutines to finish
}
```

**Use sync.Once for One-Time Initialization**
```go
var (
    instance *Database
    once     sync.Once
)

func GetDatabase() *Database {
    once.Do(func() {
        instance = &Database{
            // Initialize database connection
        }
    })
    return instance
}
```

---

## Error Handling

### Error Wrapping

```go
// Good: Preserve error context
func GetUser(id int) (*User, error) {
    user, err := db.FindUser(id)
    if err != nil {
        return nil, fmt.Errorf("get user %d: %w", id, err)
    }
    return user, nil
}

// Usage: Check for specific errors
user, err := GetUser(123)
if errors.Is(err, sql.ErrNoRows) {
    return fmt.Errorf("user not found: %w", err)
}
```

### Custom Error Types

```go
type AppError struct {
    Code    int
    Message string
    Err     error
}

func (e *AppError) Error() string {
    if e.Err != nil {
        return fmt.Sprintf("%s: %v", e.Message, e.Err)
    }
    return e.Message
}

func (e *AppError) Unwrap() error {
    return e.Err
}

// Usage
func validateInput(input string) error {
    if input == "" {
        return &AppError{
            Code:    400,
            Message: "input cannot be empty",
        }
    }
    return nil
}
```

### Error Group Pattern

```go
import "golang.org/x/sync/errgroup"

func fetchMultiple(urls []string) error {
    g := new(errgroup.Group)

    for _, url := range urls {
        url := url // https://golang.org/doc/faq#closures_and_goroutines
        g.Go(func() error {
            return fetch(url)
        })
    }

    return g.Wait() // Returns first error encountered
}
```

---

## HTTP Server Best Practices

### Middleware Pattern

```go
type Middleware func(http.Handler) http.Handler

func Logger(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        start := time.Now()
        next.ServeHTTP(w, r)
        log.Printf("%s %s %v", r.Method, r.URL.Path, time.Since(start))
    })
}

func Recovery(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        defer func() {
            if err := recover(); err != nil {
                log.Printf("panic: %v", err)
                http.Error(w, "Internal Server Error", 500)
            }
        }()
        next.ServeHTTP(w, r)
    })
}

// Chain middlewares
handler = Logger(Recovery(handler))
```

### Graceful Shutdown

```go
func main() {
    srv := &http.Server{
        Addr:         ":8080",
        Handler:      router,
        ReadTimeout:  5 * time.Second,
        WriteTimeout: 10 * time.Second,
        IdleTimeout:  120 * time.Second,
    }

    go func() {
        if err := srv.ListenAndServe(); err != nil && err != http.ErrServerClosed {
            log.Fatalf("listen: %s\n", err)
        }
    }()

    // Wait for interrupt signal
    quit := make(chan os.Signal, 1)
    signal.Notify(quit, syscall.SIGINT, syscall.SIGTERM)
    <-quit

    log.Println("Shutting down server...")

    ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
    defer cancel()

    if err := srv.Shutdown(ctx); err != nil {
        log.Fatal("Server forced to shutdown:", err)
    }

    log.Println("Server exiting")
}
```

---

## Database Patterns

### Connection Pooling

```go
import "database/sql"

func NewDB(dataSourceName string) (*sql.DB, error) {
    db, err := sql.Open("postgres", dataSourceName)
    if err != nil {
        return nil, err
    }

    // Configure connection pool
    db.SetMaxOpenConns(25)          // Maximum connections
    db.SetMaxIdleConns(5)           // Idle connections to keep
    db.SetConnMaxLifetime(5 * time.Minute) // Max connection lifetime

    // Verify connection
    ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
    defer cancel()

    if err := db.PingContext(ctx); err != nil {
        return nil, err
    }

    return db, nil
}
```

### Transaction Pattern

```go
func TransferFunds(db *sql.DB, fromID, toID int, amount float64) error {
    tx, err := db.BeginTx(context.Background(), nil)
    if err != nil {
        return err
    }
    defer tx.Rollback() // Rollback if not committed

    // Withdraw from source
    if err := withdraw(tx, fromID, amount); err != nil {
        return fmt.Errorf("withdraw: %w", err)
    }

    // Deposit to destination
    if err := deposit(tx, toID, amount); err != nil {
        return fmt.Errorf("deposit: %w", err)
    }

    return tx.Commit()
}

func withdraw(tx *sql.Tx, accountID int, amount float64) error {
    _, err := tx.Exec("UPDATE accounts SET balance = balance - $1 WHERE id = $2", amount, accountID)
    return err
}
```

### Repository Pattern with GORM

```go
type UserRepository interface {
    Create(user *User) error
    FindByID(id uint) (*User, error)
    FindByEmail(email string) (*User, error)
    Update(user *User) error
    Delete(id uint) error
}

type gormUserRepository struct {
    db *gorm.DB
}

func NewUserRepository(db *gorm.DB) UserRepository {
    return &gormUserRepository{db: db}
}

func (r *gormUserRepository) FindByID(id uint) (*User, error) {
    var user User
    err := r.db.First(&user, id).Error
    if err != nil {
        if errors.Is(err, gorm.ErrRecordNotFound) {
            return nil, fmt.Errorf("user not found: %w", err)
        }
        return nil, err
    }
    return &user, nil
}
```

---

## Performance Optimization

### Memory Efficiency

**Use Pointers for Large Structs**
```go
// Good: Pass pointer to avoid copying
func ProcessUser(user *User) {
    // Process user
}

// Avoid: Copying large struct
func ProcessUser(user User) {
    // Process user
}
```

**Preallocate Slices**
```go
// Good: Preallocate when size is known
users := make([]User, 0, 100)
for i := 0; i < 100; i++ {
    users = append(users, User{ID: i})
}

// Avoid: Dynamic growth causes reallocations
var users []User
for i := 0; i < 100; i++ {
    users = append(users, User{ID: i})
}
```

**Use sync.Pool for Frequent Allocations**
```go
var bufferPool = sync.Pool{
    New: func() interface{} {
        return new(bytes.Buffer)
    },
}

func processData(data []byte) {
    buf := bufferPool.Get().(*bytes.Buffer)
    defer bufferPool.Put(buf)
    buf.Reset()

    buf.Write(data)
    // Process buffer
}
```

### Profiling

```go
import _ "net/http/pprof"

func main() {
    go func() {
        log.Println(http.ListenAndServe("localhost:6060", nil))
    }()

    // Your application code
}

// Access profiling endpoints:
// http://localhost:6060/debug/pprof/
// http://localhost:6060/debug/pprof/heap
// http://localhost:6060/debug/pprof/goroutine

// Generate CPU profile:
// go tool pprof http://localhost:6060/debug/pprof/profile?seconds=30
```

---

## Testing Best Practices

### Table-Driven Tests

```go
func TestValidateEmail(t *testing.T) {
    tests := []struct {
        name    string
        email   string
        wantErr bool
    }{
        {"valid email", "test@example.com", false},
        {"missing @", "testexample.com", true},
        {"empty string", "", true},
        {"no domain", "test@", true},
    }

    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            err := ValidateEmail(tt.email)
            if (err != nil) != tt.wantErr {
                t.Errorf("ValidateEmail() error = %v, wantErr %v", err, tt.wantErr)
            }
        })
    }
}
```

### Mocking with Interfaces

```go
type EmailSender interface {
    Send(to, subject, body string) error
}

type mockEmailSender struct {
    sendFunc func(to, subject, body string) error
}

func (m *mockEmailSender) Send(to, subject, body string) error {
    if m.sendFunc != nil {
        return m.sendFunc(to, subject, body)
    }
    return nil
}

func TestUserService(t *testing.T) {
    mock := &mockEmailSender{
        sendFunc: func(to, subject, body string) error {
            if to != "test@example.com" {
                t.Errorf("unexpected recipient: %s", to)
            }
            return nil
        },
    }

    service := NewUserService(mock)
    service.RegisterUser("test@example.com", "password")
}
```

### Benchmark Tests

```go
func BenchmarkProcessData(b *testing.B) {
    data := generateTestData(1000)

    b.ResetTimer()
    for i := 0; i < b.N; i++ {
        ProcessData(data)
    }
}

// Run: go test -bench=. -benchmem
```

---

## Logging Best Practices

### Structured Logging

```go
import "go.uber.org/zap"

func main() {
    logger, _ := zap.NewProduction()
    defer logger.Sync()

    logger.Info("server started",
        zap.String("addr", ":8080"),
        zap.Int("pid", os.Getpid()),
    )

    logger.Error("failed to fetch user",
        zap.Error(err),
        zap.Int("user_id", userID),
        zap.Duration("elapsed", elapsed),
    )
}
```

### Context-Based Logging

```go
type contextKey string

const requestIDKey contextKey = "request_id"

func WithRequestID(ctx context.Context, requestID string) context.Context {
    return context.WithValue(ctx, requestIDKey, requestID)
}

func LogFromContext(ctx context.Context, msg string) {
    requestID, _ := ctx.Value(requestIDKey).(string)
    log.Printf("[%s] %s", requestID, msg)
}
```

---

## Configuration Management

### Environment Variables

```go
import "github.com/kelseyhightower/envconfig"

type Config struct {
    DatabaseURL string        `envconfig:"DATABASE_URL" required:"true"`
    Port        int           `envconfig:"PORT" default:"8080"`
    LogLevel    string        `envconfig:"LOG_LEVEL" default:"info"`
    Timeout     time.Duration `envconfig:"TIMEOUT" default:"30s"`
}

func LoadConfig() (*Config, error) {
    var cfg Config
    err := envconfig.Process("", &cfg)
    if err != nil {
        return nil, fmt.Errorf("load config: %w", err)
    }
    return &cfg, nil
}
```

---

## Security Best Practices

### Password Hashing

```go
import "golang.org/x/crypto/bcrypt"

const bcryptCost = 12

func HashPassword(password string) (string, error) {
    hash, err := bcrypt.GenerateFromPassword([]byte(password), bcryptCost)
    if err != nil {
        return "", err
    }
    return string(hash), nil
}

func VerifyPassword(hashedPassword, password string) error {
    return bcrypt.CompareHashAndPassword([]byte(hashedPassword), []byte(password))
}
```

### Input Validation

```go
import "github.com/go-playground/validator/v10"

type CreateUserRequest struct {
    Email    string `json:"email" validate:"required,email"`
    Password string `json:"password" validate:"required,min=8,max=100"`
    Name     string `json:"name" validate:"required,min=2,max=50"`
}

var validate = validator.New()

func ValidateRequest(req interface{}) error {
    return validate.Struct(req)
}
```

---

## Deployment Patterns

### Docker Multi-Stage Build

```dockerfile
# Build stage
FROM golang:1.21-alpine AS builder

WORKDIR /app
COPY go.mod go.sum ./
RUN go mod download

COPY . .
RUN CGO_ENABLED=0 GOOS=linux go build -a -installsuffix cgo -ldflags '-extldflags "-static"' -o main ./cmd/api

# Final stage
FROM scratch
COPY --from=builder /etc/ssl/certs/ca-certificates.crt /etc/ssl/certs/
COPY --from=builder /app/main /main
EXPOSE 8080
ENTRYPOINT ["/main"]
```

### Health Checks

```go
func healthHandler(w http.ResponseWriter, r *http.Request) {
    // Check database connectivity
    if err := db.Ping(); err != nil {
        w.WriteHeader(http.StatusServiceUnavailable)
        json.NewEncoder(w).Encode(map[string]string{
            "status": "unhealthy",
            "error":  err.Error(),
        })
        return
    }

    // Check Redis connectivity
    if err := redisClient.Ping(r.Context()).Err(); err != nil {
        w.WriteHeader(http.StatusServiceUnavailable)
        json.NewEncoder(w).Encode(map[string]string{
            "status": "unhealthy",
            "error":  err.Error(),
        })
        return
    }

    w.WriteHeader(http.StatusOK)
    json.NewEncoder(w).Encode(map[string]string{
        "status": "healthy",
    })
}
```

---

## Common Pitfalls

### Goroutine Leaks

```go
// Bad: Goroutine leak if channel never closes
func processItems(items []string) {
    ch := make(chan string)
    go func() {
        for item := range ch {
            process(item)
        }
    }()
    // ch is never closed - goroutine leaks
}

// Good: Ensure goroutines can exit
func processItems(items []string) {
    ch := make(chan string)
    done := make(chan struct{})

    go func() {
        defer close(done)
        for item := range ch {
            process(item)
        }
    }()

    for _, item := range items {
        ch <- item
    }
    close(ch) // Signal completion
    <-done    // Wait for goroutine to finish
}
```

### Closure Loop Variables

```go
// Bad: All goroutines reference same variable
for _, item := range items {
    go func() {
        process(item) // Bug: item is the loop variable
    }()
}

// Good: Pass variable to goroutine
for _, item := range items {
    go func(i string) {
        process(i)
    }(item)
}
```

### Nil Pointer Dereference

```go
// Bad: No nil check
func GetUserName(user *User) string {
    return user.Name // Panic if user is nil
}

// Good: Defensive programming
func GetUserName(user *User) string {
    if user == nil {
        return ""
    }
    return user.Name
}
```

---

## Resources

- [Effective Go](https://go.dev/doc/effective_go)
- [Go Code Review Comments](https://github.com/golang/go/wiki/CodeReviewComments)
- [Uber Go Style Guide](https://github.com/uber-go/guide/blob/master/style.md)
- [Go Proverbs](https://go-proverbs.github.io/)
- [Go by Example](https://gobyexample.com/)
