# Backend Engineering - Go + Fiber + GORM Template

*Purpose: High-performance, concurrent backend services with Go's native concurrency primitives*

---

# When to Use

Use this template when building:
- High-performance APIs requiring low latency (<10ms)
- Microservices with intensive concurrent operations
- Real-time systems (WebSocket servers, streaming APIs)
- Services processing millions of requests/day
- Systems requiring predictable memory usage and minimal GC pauses

**Go Advantages:**
- Native goroutines for lightweight concurrency (100k+ concurrent connections)
- Static compilation (single binary deployment, no runtime dependencies)
- Fast startup times (critical for serverless/containers)
- Built-in race detector and profiling tools
- Excellent standard library (HTTP, JSON, crypto)

---

# TEMPLATE STARTS HERE

# 1. Project Overview

**Tech Stack:**
- [ ] Go 1.22+ (prefer latest stable)
- [ ] Fiber v2 (Express-inspired framework, 10x faster than Express.js)
- [ ] GORM 1.25+ (ORM with hooks, transactions, migrations)
- [ ] PostgreSQL 14+ (or org standard)
- [ ] Redis (caching, session store)
- [ ] github.com/golang-jwt/jwt/v5 (authentication)
- [ ] Testify (testing assertions)
- [ ] Air (hot reload for development)

**Project Name:** `{{project_name}}`

**Team:**
- Backend: {{team_size}} developers
- DevOps: {{devops_team}}

---

# 2. Project Structure

```
project-root/
|-- cmd/
|   `-- api/
|       `-- main.go                 # Application entry point
|-- internal/
|   |-- api/
|   |   |-- handlers/               # HTTP handlers
|   |   |-- middleware/             # Custom middleware
|   |   |-- routes/                 # Route definitions
|   |   `-- validators/             # Request validation
|   |-- domain/
|   |   |-- models/                 # Domain models (GORM structs)
|   |   |-- repositories/           # Data access interfaces
|   |   `-- services/               # Business logic
|   |-- infrastructure/
|   |   |-- database/               # Database connection, migrations
|   |   |-- cache/                  # Redis client
|   |   `-- config/                 # Configuration loader
|   `-- pkg/
|       |-- auth/                   # JWT utilities
|       |-- errors/                 # Custom error types
|       |-- logger/                 # Structured logging
|       `-- utils/                  # Shared utilities
|-- migrations/                     # SQL migration files
|-- tests/
|   |-- integration/
|   `-- unit/
|-- scripts/
|   |-- migrate.sh
|   `-- seed.sh
|-- .air.toml                       # Hot reload config
|-- .env.example
|-- Dockerfile
|-- docker-compose.yml
|-- go.mod
|-- go.sum
|-- Makefile
`-- README.md
```

**Key Principles:**
- `cmd/` for executable entry points
- `internal/` for private application code (not importable by external packages)
- `pkg/` for reusable utilities
- Clear separation: handlers -> services -> repositories -> database

---

## Centralization Guide

> **Important**: The code patterns in this template should be extracted to shared utility packages. **Do not duplicate** these utilities across services.

| Utility | Extract To | Reference |
|---------|------------|-----------|
| Config loading (`getEnv`, `getEnvInt`) | `internal/pkg/config/` | [config-validation.md](../../../software-clean-code-standard/utilities/config-validation.md) |
| JWT (`JWTManager`, `Generate`, `Verify`) | `internal/pkg/auth/` | [auth-utilities.md](../../../software-clean-code-standard/utilities/auth-utilities.md) |
| Password (`HashPassword`, `VerifyPassword`) | `internal/pkg/auth/` | [auth-utilities.md](../../../software-clean-code-standard/utilities/auth-utilities.md) |
| Errors (`AppError`, `errorHandler`) | `internal/pkg/errors/` | [error-handling.md](../../../software-clean-code-standard/utilities/error-handling.md) |
| Logging (zap setup) | `internal/pkg/logger/` | [logging-utilities.md](../../../software-clean-code-standard/utilities/logging-utilities.md) |

**Pattern**: Create utilities once in `internal/pkg/`, import everywhere via:

```go
import "myapp/internal/pkg/auth"
import "myapp/internal/pkg/errors"
```

---

# 3. Environment Configuration

## .env.example

```env
# Server
APP_ENV=development
APP_PORT=8080
APP_NAME=your-api
APP_VERSION=1.0.0

# Database
DATABASE_URL=postgres://user:password@localhost:5432/dbname?sslmode=disable
DB_MAX_OPEN_CONNS=25
DB_MAX_IDLE_CONNS=5
DB_CONN_MAX_LIFETIME=5m

# Redis
REDIS_URL=redis://localhost:6379/0
REDIS_PASSWORD=
REDIS_DB=0

# JWT
JWT_SECRET=your-super-secret-key-min-32-chars
JWT_EXPIRATION=168h # 7 days
JWT_REFRESH_EXPIRATION=720h # 30 days

# CORS
CORS_ALLOWED_ORIGINS=http://localhost:3000,https://yourapp.com
CORS_ALLOWED_METHODS=GET,POST,PUT,PATCH,DELETE
CORS_ALLOWED_HEADERS=Content-Type,Authorization

# Rate Limiting
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=1m

# Logging
LOG_LEVEL=info
LOG_FORMAT=json
```

## internal/infrastructure/config/config.go

```go
package config

import (
    "fmt"
    "os"
    "strconv"
    "time"

    "github.com/joho/godotenv"
)

type Config struct {
    App      AppConfig
    Database DatabaseConfig
    Redis    RedisConfig
    JWT      JWTConfig
    CORS     CORSConfig
    RateLimit RateLimitConfig
    Logger   LoggerConfig
}

type AppConfig struct {
    Env     string
    Port    string
    Name    string
    Version string
}

type DatabaseConfig struct {
    URL             string
    MaxOpenConns    int
    MaxIdleConns    int
    ConnMaxLifetime time.Duration
}

type RedisConfig struct {
    URL      string
    Password string
    DB       int
}

type JWTConfig struct {
    Secret             string
    Expiration         time.Duration
    RefreshExpiration  time.Duration
}

type CORSConfig struct {
    AllowedOrigins []string
    AllowedMethods []string
    AllowedHeaders []string
}

type RateLimitConfig struct {
    Requests int
    Window   time.Duration
}

type LoggerConfig struct {
    Level  string
    Format string
}

func Load() (*Config, error) {
    // Load .env file in development
    if os.Getenv("APP_ENV") != "production" {
        if err := godotenv.Load(); err != nil {
            return nil, fmt.Errorf("error loading .env file: %w", err)
        }
    }

    cfg := &Config{
        App: AppConfig{
            Env:     getEnv("APP_ENV", "development"),
            Port:    getEnv("APP_PORT", "8080"),
            Name:    getEnv("APP_NAME", "api"),
            Version: getEnv("APP_VERSION", "1.0.0"),
        },
        Database: DatabaseConfig{
            URL:             getEnv("DATABASE_URL", ""),
            MaxOpenConns:    getEnvInt("DB_MAX_OPEN_CONNS", 25),
            MaxIdleConns:    getEnvInt("DB_MAX_IDLE_CONNS", 5),
            ConnMaxLifetime: getEnvDuration("DB_CONN_MAX_LIFETIME", 5*time.Minute),
        },
        Redis: RedisConfig{
            URL:      getEnv("REDIS_URL", "redis://localhost:6379/0"),
            Password: getEnv("REDIS_PASSWORD", ""),
            DB:       getEnvInt("REDIS_DB", 0),
        },
        JWT: JWTConfig{
            Secret:            getEnv("JWT_SECRET", ""),
            Expiration:        getEnvDuration("JWT_EXPIRATION", 168*time.Hour),
            RefreshExpiration: getEnvDuration("JWT_REFRESH_EXPIRATION", 720*time.Hour),
        },
        RateLimit: RateLimitConfig{
            Requests: getEnvInt("RATE_LIMIT_REQUESTS", 100),
            Window:   getEnvDuration("RATE_LIMIT_WINDOW", 1*time.Minute),
        },
        Logger: LoggerConfig{
            Level:  getEnv("LOG_LEVEL", "info"),
            Format: getEnv("LOG_FORMAT", "json"),
        },
    }

    if err := cfg.Validate(); err != nil {
        return nil, fmt.Errorf("config validation failed: %w", err)
    }

    return cfg, nil
}

func (c *Config) Validate() error {
    if c.Database.URL == "" {
        return fmt.Errorf("DATABASE_URL is required")
    }
    if c.JWT.Secret == "" || len(c.JWT.Secret) < 32 {
        return fmt.Errorf("JWT_SECRET must be at least 32 characters")
    }
    return nil
}

func getEnv(key, defaultValue string) string {
    if value := os.Getenv(key); value != "" {
        return value
    }
    return defaultValue
}

func getEnvInt(key string, defaultValue int) int {
    if value := os.Getenv(key); value != "" {
        if intVal, err := strconv.Atoi(value); err == nil {
            return intVal
        }
    }
    return defaultValue
}

func getEnvDuration(key string, defaultValue time.Duration) time.Duration {
    if value := os.Getenv(key); value != "" {
        if duration, err := time.ParseDuration(value); err == nil {
            return duration
        }
    }
    return defaultValue
}
```

---

# 4. Database Setup

## internal/infrastructure/database/postgres.go

```go
package database

import (
    "context"
    "fmt"
    "log"
    "time"

    "gorm.io/driver/postgres"
    "gorm.io/gorm"
    "gorm.io/gorm/logger"

    "{{module_path}}/internal/domain/models"
    "{{module_path}}/internal/infrastructure/config"
)

type Database struct {
    *gorm.DB
}

func NewDatabase(cfg *config.DatabaseConfig) (*Database, error) {
    logLevel := logger.Info
    if cfg.LogLevel == "silent" {
        logLevel = logger.Silent
    }

    db, err := gorm.Open(postgres.Open(cfg.URL), &gorm.Config{
        Logger: logger.Default.LogMode(logLevel),
        NowFunc: func() time.Time {
            return time.Now().UTC()
        },
        PrepareStmt: true, // Prepared statement cache
    })
    if err != nil {
        return nil, fmt.Errorf("failed to connect to database: %w", err)
    }

    sqlDB, err := db.DB()
    if err != nil {
        return nil, fmt.Errorf("failed to get database instance: %w", err)
    }

    // Connection pool settings
    sqlDB.SetMaxOpenConns(cfg.MaxOpenConns)
    sqlDB.SetMaxIdleConns(cfg.MaxIdleConns)
    sqlDB.SetConnMaxLifetime(cfg.ConnMaxLifetime)

    // Verify connection
    ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
    defer cancel()

    if err := sqlDB.PingContext(ctx); err != nil {
        return nil, fmt.Errorf("failed to ping database: %w", err)
    }

    log.Println("Database connection established")
    return &Database{db}, nil
}

func (db *Database) AutoMigrate() error {
    return db.DB.AutoMigrate(
        &models.User{},
        &models.Post{},
        &models.Comment{},
        // Add more models here
    )
}

func (db *Database) Close() error {
    sqlDB, err := db.DB.DB()
    if err != nil {
        return err
    }
    return sqlDB.Close()
}
```

## internal/domain/models/user.go

```go
package models

import (
    "time"

    "gorm.io/gorm"
)

type User struct {
    ID        uint           `gorm:"primaryKey" json:"id"`
    Email     string         `gorm:"uniqueIndex;not null" json:"email"`
    Password  string         `gorm:"not null" json:"-"` // Never serialize password
    Name      string         `gorm:"not null" json:"name"`
    Role      string         `gorm:"type:varchar(20);default:'user'" json:"role"`
    IsActive  bool           `gorm:"default:true" json:"is_active"`
    Posts     []Post         `gorm:"foreignKey:UserID" json:"posts,omitempty"`
    CreatedAt time.Time      `json:"created_at"`
    UpdatedAt time.Time      `json:"updated_at"`
    DeletedAt gorm.DeletedAt `gorm:"index" json:"-"` // Soft delete
}

type Post struct {
    ID        uint           `gorm:"primaryKey" json:"id"`
    Title     string         `gorm:"not null" json:"title"`
    Content   string         `gorm:"type:text" json:"content"`
    Published bool           `gorm:"default:false" json:"published"`
    UserID    uint           `gorm:"not null;index" json:"user_id"`
    User      *User          `json:"user,omitempty"`
    Comments  []Comment      `gorm:"foreignKey:PostID" json:"comments,omitempty"`
    CreatedAt time.Time      `json:"created_at"`
    UpdatedAt time.Time      `json:"updated_at"`
    DeletedAt gorm.DeletedAt `gorm:"index" json:"-"`
}

type Comment struct {
    ID        uint           `gorm:"primaryKey" json:"id"`
    Content   string         `gorm:"type:text;not null" json:"content"`
    PostID    uint           `gorm:"not null;index" json:"post_id"`
    UserID    uint           `gorm:"not null;index" json:"user_id"`
    User      *User          `json:"user,omitempty"`
    CreatedAt time.Time      `json:"created_at"`
    UpdatedAt time.Time      `json:"updated_at"`
    DeletedAt gorm.DeletedAt `gorm:"index" json:"-"`
}

// BeforeCreate hook example
func (u *User) BeforeCreate(tx *gorm.DB) error {
    // Add validation or pre-processing here
    return nil
}
```

---

# 5. Application Setup

## cmd/api/main.go

```go
package main

import (
    "context"
    "fmt"
    "log"
    "os"
    "os/signal"
    "syscall"
    "time"

    "github.com/gofiber/fiber/v2"
    "github.com/gofiber/fiber/v2/middleware/compress"
    "github.com/gofiber/fiber/v2/middleware/cors"
    "github.com/gofiber/fiber/v2/middleware/helmet"
    "github.com/gofiber/fiber/v2/middleware/limiter"
    "github.com/gofiber/fiber/v2/middleware/recover"
    "github.com/gofiber/fiber/v2/middleware/requestid"

    "{{module_path}}/internal/api/routes"
    "{{module_path}}/internal/infrastructure/cache"
    "{{module_path}}/internal/infrastructure/config"
    "{{module_path}}/internal/infrastructure/database"
    "{{module_path}}/internal/pkg/logger"
)

func main() {
    // Load configuration
    cfg, err := config.Load()
    if err != nil {
        log.Fatalf("Failed to load config: %v", err)
    }

    // Initialize logger
    log := logger.NewLogger(cfg.Logger)
    log.Info("Starting application", "env", cfg.App.Env, "version", cfg.App.Version)

    // Connect to database
    db, err := database.NewDatabase(&cfg.Database)
    if err != nil {
        log.Fatal("Failed to connect to database", "error", err)
    }
    defer db.Close()

    // Run migrations
    if err := db.AutoMigrate(); err != nil {
        log.Fatal("Failed to run migrations", "error", err)
    }

    // Connect to Redis
    redis := cache.NewRedisClient(&cfg.Redis)
    defer redis.Close()

    // Initialize Fiber app
    app := fiber.New(fiber.Config{
        AppName:      cfg.App.Name,
        ReadTimeout:  10 * time.Second,
        WriteTimeout: 10 * time.Second,
        IdleTimeout:  120 * time.Second,
        ErrorHandler: errorHandler,
    })

    // Global middleware
    app.Use(recover.New())                   // Panic recovery
    app.Use(requestid.New())                 // Request ID tracking
    app.Use(helmet.New())                    // Security headers
    app.Use(compress.New())                  // Response compression
    app.Use(cors.New(cors.Config{
        AllowOrigins:     cfg.CORS.AllowedOrigins[0], // Join with comma
        AllowMethods:     cfg.CORS.AllowedMethods[0],
        AllowHeaders:     cfg.CORS.AllowedHeaders[0],
        AllowCredentials: true,
    }))
    app.Use(limiter.New(limiter.Config{
        Max:        cfg.RateLimit.Requests,
        Expiration: cfg.RateLimit.Window,
    }))

    // Health check
    app.Get("/health", func(c *fiber.Ctx) error {
        return c.JSON(fiber.Map{
            "status": "ok",
            "time":   time.Now().UTC(),
        })
    })

    // Setup routes
    routes.Setup(app, db, redis, cfg, log)

    // Graceful shutdown
    go func() {
        if err := app.Listen(":" + cfg.App.Port); err != nil {
            log.Fatal("Failed to start server", "error", err)
        }
    }()

    log.Info("Server started", "port", cfg.App.Port)

    // Wait for interrupt signal
    quit := make(chan os.Signal, 1)
    signal.Notify(quit, os.Interrupt, syscall.SIGTERM)
    <-quit

    log.Info("Shutting down server...")

    ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
    defer cancel()

    if err := app.ShutdownWithContext(ctx); err != nil {
        log.Error("Server forced to shutdown", "error", err)
    }

    log.Info("Server exited")
}

func errorHandler(c *fiber.Ctx, err error) error {
    code := fiber.StatusInternalServerError
    message := "Internal Server Error"

    if e, ok := err.(*fiber.Error); ok {
        code = e.Code
        message = e.Message
    }

    return c.Status(code).JSON(fiber.Map{
        "error": fiber.Map{
            "code":    code,
            "message": message,
        },
    })
}
```

---

# 6. Authentication Implementation

## internal/pkg/auth/jwt.go

```go
package auth

import (
    "errors"
    "fmt"
    "time"

    "github.com/golang-jwt/jwt/v5"
)

type JWTManager struct {
    secret     string
    expiration time.Duration
}

type Claims struct {
    UserID uint   `json:"user_id"`
    Email  string `json:"email"`
    Role   string `json:"role"`
    jwt.RegisteredClaims
}

func NewJWTManager(secret string, expiration time.Duration) *JWTManager {
    return &JWTManager{
        secret:     secret,
        expiration: expiration,
    }
}

func (jm *JWTManager) Generate(userID uint, email, role string) (string, error) {
    claims := Claims{
        UserID: userID,
        Email:  email,
        Role:   role,
        RegisteredClaims: jwt.RegisteredClaims{
            ExpiresAt: jwt.NewNumericDate(time.Now().Add(jm.expiration)),
            IssuedAt:  jwt.NewNumericDate(time.Now()),
            NotBefore: jwt.NewNumericDate(time.Now()),
        },
    }

    token := jwt.NewWithClaims(jwt.SigningMethodHS256, claims)
    return token.SignedString([]byte(jm.secret))
}

func (jm *JWTManager) Verify(tokenString string) (*Claims, error) {
    token, err := jwt.ParseWithClaims(tokenString, &Claims{}, func(token *jwt.Token) (interface{}, error) {
        if _, ok := token.Method.(*jwt.SigningMethodHMAC); !ok {
            return nil, fmt.Errorf("unexpected signing method: %v", token.Header["alg"])
        }
        return []byte(jm.secret), nil
    })

    if err != nil {
        return nil, err
    }

    claims, ok := token.Claims.(*Claims)
    if !ok || !token.Valid {
        return nil, errors.New("invalid token")
    }

    return claims, nil
}
```

## internal/pkg/auth/password.go

```go
package auth

import (
    "errors"

    "golang.org/x/crypto/bcrypt"
)

const bcryptCost = 12

func HashPassword(password string) (string, error) {
    if len(password) < 8 {
        return "", errors.New("password must be at least 8 characters")
    }

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

## internal/api/middleware/auth.go

```go
package middleware

import (
    "strings"

    "github.com/gofiber/fiber/v2"

    "{{module_path}}/internal/pkg/auth"
)

type AuthMiddleware struct {
    jwtManager *auth.JWTManager
}

func NewAuthMiddleware(jwtManager *auth.JWTManager) *AuthMiddleware {
    return &AuthMiddleware{jwtManager: jwtManager}
}

func (am *AuthMiddleware) Protected() fiber.Handler {
    return func(c *fiber.Ctx) error {
        authHeader := c.Get("Authorization")
        if authHeader == "" {
            return c.Status(fiber.StatusUnauthorized).JSON(fiber.Map{
                "error": "Missing authorization header",
            })
        }

        parts := strings.Split(authHeader, " ")
        if len(parts) != 2 || parts[0] != "Bearer" {
            return c.Status(fiber.StatusUnauthorized).JSON(fiber.Map{
                "error": "Invalid authorization header format",
            })
        }

        claims, err := am.jwtManager.Verify(parts[1])
        if err != nil {
            return c.Status(fiber.StatusUnauthorized).JSON(fiber.Map{
                "error": "Invalid or expired token",
            })
        }

        // Store user info in context
        c.Locals("user_id", claims.UserID)
        c.Locals("email", claims.Email)
        c.Locals("role", claims.Role)

        return c.Next()
    }
}

func (am *AuthMiddleware) RequireRole(role string) fiber.Handler {
    return func(c *fiber.Ctx) error {
        userRole := c.Locals("role").(string)
        if userRole != role {
            return c.Status(fiber.StatusForbidden).JSON(fiber.Map{
                "error": "Insufficient permissions",
            })
        }
        return c.Next()
    }
}
```

---

# 7. API Routes & Handlers

## internal/api/routes/routes.go

```go
package routes

import (
    "github.com/gofiber/fiber/v2"

    "{{module_path}}/internal/api/handlers"
    "{{module_path}}/internal/api/middleware"
    "{{module_path}}/internal/domain/repositories"
    "{{module_path}}/internal/domain/services"
    "{{module_path}}/internal/infrastructure/cache"
    "{{module_path}}/internal/infrastructure/config"
    "{{module_path}}/internal/infrastructure/database"
    "{{module_path}}/internal/pkg/auth"
    "{{module_path}}/internal/pkg/logger"
)

func Setup(
    app *fiber.App,
    db *database.Database,
    redis *cache.RedisClient,
    cfg *config.Config,
    log *logger.Logger,
) {
    // Initialize dependencies
    jwtManager := auth.NewJWTManager(cfg.JWT.Secret, cfg.JWT.Expiration)
    authMiddleware := middleware.NewAuthMiddleware(jwtManager)

    // Repositories
    userRepo := repositories.NewUserRepository(db)
    postRepo := repositories.NewPostRepository(db)

    // Services
    userService := services.NewUserService(userRepo, jwtManager)
    postService := services.NewPostService(postRepo, userRepo)

    // Handlers
    authHandler := handlers.NewAuthHandler(userService, log)
    userHandler := handlers.NewUserHandler(userService, log)
    postHandler := handlers.NewPostHandler(postService, log)

    // API v1 routes
    api := app.Group("/api/v1")

    // Public routes
    api.Post("/auth/register", authHandler.Register)
    api.Post("/auth/login", authHandler.Login)

    // Protected routes
    users := api.Group("/users", authMiddleware.Protected())
    users.Get("/me", userHandler.GetProfile)
    users.Put("/me", userHandler.UpdateProfile)
    users.Delete("/me", userHandler.DeleteAccount)

    // Admin only
    users.Get("/", authMiddleware.Protected(), authMiddleware.RequireRole("admin"), userHandler.ListUsers)

    // Posts (protected)
    posts := api.Group("/posts", authMiddleware.Protected())
    posts.Get("/", postHandler.List)
    posts.Get("/:id", postHandler.Get)
    posts.Post("/", postHandler.Create)
    posts.Put("/:id", postHandler.Update)
    posts.Delete("/:id", postHandler.Delete)
}
```

## internal/api/handlers/auth_handler.go

```go
package handlers

import (
    "github.com/gofiber/fiber/v2"

    "{{module_path}}/internal/domain/services"
    "{{module_path}}/internal/pkg/logger"
)

type AuthHandler struct {
    userService *services.UserService
    log         *logger.Logger
}

func NewAuthHandler(userService *services.UserService, log *logger.Logger) *AuthHandler {
    return &AuthHandler{
        userService: userService,
        log:         log,
    }
}

type RegisterRequest struct {
    Email    string `json:"email" validate:"required,email"`
    Password string `json:"password" validate:"required,min=8"`
    Name     string `json:"name" validate:"required,min=2,max=50"`
}

type LoginRequest struct {
    Email    string `json:"email" validate:"required,email"`
    Password string `json:"password" validate:"required"`
}

func (h *AuthHandler) Register(c *fiber.Ctx) error {
    var req RegisterRequest
    if err := c.BodyParser(&req); err != nil {
        return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{
            "error": "Invalid request body",
        })
    }

    // Validate request (use validator library in production)
    if req.Email == "" || req.Password == "" || req.Name == "" {
        return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{
            "error": "Missing required fields",
        })
    }

    user, token, err := h.userService.Register(req.Email, req.Password, req.Name)
    if err != nil {
        h.log.Error("Registration failed", "error", err, "email", req.Email)
        return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{
            "error": err.Error(),
        })
    }

    h.log.Info("User registered", "user_id", user.ID, "email", user.Email)

    return c.Status(fiber.StatusCreated).JSON(fiber.Map{
        "user":  user,
        "token": token,
    })
}

func (h *AuthHandler) Login(c *fiber.Ctx) error {
    var req LoginRequest
    if err := c.BodyParser(&req); err != nil {
        return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{
            "error": "Invalid request body",
        })
    }

    user, token, err := h.userService.Login(req.Email, req.Password)
    if err != nil {
        h.log.Warn("Login failed", "error", err, "email", req.Email)
        return c.Status(fiber.StatusUnauthorized).JSON(fiber.Map{
            "error": "Invalid email or password",
        })
    }

    h.log.Info("User logged in", "user_id", user.ID, "email", user.Email)

    return c.JSON(fiber.Map{
        "user":  user,
        "token": token,
    })
}
```

---

# 8. Repository Pattern / Data Access

## internal/domain/repositories/user_repository.go

```go
package repositories

import (
    "errors"

    "gorm.io/gorm"

    "{{module_path}}/internal/domain/models"
    "{{module_path}}/internal/infrastructure/database"
)

type UserRepository interface {
    Create(user *models.User) error
    FindByID(id uint) (*models.User, error)
    FindByEmail(email string) (*models.User, error)
    Update(user *models.User) error
    Delete(id uint) error
    List(offset, limit int) ([]models.User, int64, error)
}

type userRepository struct {
    db *database.Database
}

func NewUserRepository(db *database.Database) UserRepository {
    return &userRepository{db: db}
}

func (r *userRepository) Create(user *models.User) error {
    return r.db.Create(user).Error
}

func (r *userRepository) FindByID(id uint) (*models.User, error) {
    var user models.User
    err := r.db.First(&user, id).Error
    if err != nil {
        if errors.Is(err, gorm.ErrRecordNotFound) {
            return nil, errors.New("user not found")
        }
        return nil, err
    }
    return &user, nil
}

func (r *userRepository) FindByEmail(email string) (*models.User, error) {
    var user models.User
    err := r.db.Where("email = ?", email).First(&user).Error
    if err != nil {
        if errors.Is(err, gorm.ErrRecordNotFound) {
            return nil, errors.New("user not found")
        }
        return nil, err
    }
    return &user, nil
}

func (r *userRepository) Update(user *models.User) error {
    return r.db.Save(user).Error
}

func (r *userRepository) Delete(id uint) error {
    // Soft delete
    return r.db.Delete(&models.User{}, id).Error
}

func (r *userRepository) List(offset, limit int) ([]models.User, int64, error) {
    var users []models.User
    var total int64

    if err := r.db.Model(&models.User{}).Count(&total).Error; err != nil {
        return nil, 0, err
    }

    err := r.db.Offset(offset).Limit(limit).Order("created_at DESC").Find(&users).Error
    return users, total, err
}
```

## internal/domain/services/user_service.go

```go
package services

import (
    "errors"

    "{{module_path}}/internal/domain/models"
    "{{module_path}}/internal/domain/repositories"
    "{{module_path}}/internal/pkg/auth"
)

type UserService struct {
    repo       repositories.UserRepository
    jwtManager *auth.JWTManager
}

func NewUserService(repo repositories.UserRepository, jwtManager *auth.JWTManager) *UserService {
    return &UserService{
        repo:       repo,
        jwtManager: jwtManager,
    }
}

func (s *UserService) Register(email, password, name string) (*models.User, string, error) {
    // Check if user already exists
    existing, _ := s.repo.FindByEmail(email)
    if existing != nil {
        return nil, "", errors.New("email already in use")
    }

    // Hash password
    hashedPassword, err := auth.HashPassword(password)
    if err != nil {
        return nil, "", err
    }

    // Create user
    user := &models.User{
        Email:    email,
        Password: hashedPassword,
        Name:     name,
        Role:     "user",
        IsActive: true,
    }

    if err := s.repo.Create(user); err != nil {
        return nil, "", err
    }

    // Generate JWT
    token, err := s.jwtManager.Generate(user.ID, user.Email, user.Role)
    if err != nil {
        return nil, "", err
    }

    return user, token, nil
}

func (s *UserService) Login(email, password string) (*models.User, string, error) {
    user, err := s.repo.FindByEmail(email)
    if err != nil {
        return nil, "", errors.New("invalid credentials")
    }

    if err := auth.VerifyPassword(user.Password, password); err != nil {
        return nil, "", errors.New("invalid credentials")
    }

    if !user.IsActive {
        return nil, "", errors.New("account is deactivated")
    }

    token, err := s.jwtManager.Generate(user.ID, user.Email, user.Role)
    if err != nil {
        return nil, "", err
    }

    return user, token, nil
}
```

---

# 9. Testing

## tests/unit/services/user_service_test.go

```go
package services_test

import (
    "errors"
    "testing"
    "time"

    "github.com/stretchr/testify/assert"
    "github.com/stretchr/testify/mock"

    "{{module_path}}/internal/domain/models"
    "{{module_path}}/internal/domain/services"
    "{{module_path}}/internal/pkg/auth"
)

// Mock repository
type MockUserRepository struct {
    mock.Mock
}

func (m *MockUserRepository) Create(user *models.User) error {
    args := m.Called(user)
    return args.Error(0)
}

func (m *MockUserRepository) FindByEmail(email string) (*models.User, error) {
    args := m.Called(email)
    if args.Get(0) == nil {
        return nil, args.Error(1)
    }
    return args.Get(0).(*models.User), args.Error(1)
}

// More mock methods...

func TestUserService_Register(t *testing.T) {
    mockRepo := new(MockUserRepository)
    jwtManager := auth.NewJWTManager("test-secret-key-min-32-characters", 24*time.Hour)
    service := services.NewUserService(mockRepo, jwtManager)

    t.Run("successful registration", func(t *testing.T) {
        mockRepo.On("FindByEmail", "test@example.com").Return(nil, errors.New("not found"))
        mockRepo.On("Create", mock.AnythingOfType("*models.User")).Return(nil)

        user, token, err := service.Register("test@example.com", "password123", "Test User")

        assert.NoError(t, err)
        assert.NotNil(t, user)
        assert.NotEmpty(t, token)
        assert.Equal(t, "test@example.com", user.Email)
        mockRepo.AssertExpectations(t)
    })

    t.Run("duplicate email", func(t *testing.T) {
        existingUser := &models.User{Email: "test@example.com"}
        mockRepo.On("FindByEmail", "test@example.com").Return(existingUser, nil)

        user, token, err := service.Register("test@example.com", "password123", "Test User")

        assert.Error(t, err)
        assert.Nil(t, user)
        assert.Empty(t, token)
        assert.Contains(t, err.Error(), "already in use")
    })
}
```

## tests/integration/api/auth_test.go

```go
package api_test

import (
    "bytes"
    "encoding/json"
    "net/http"
    "net/http/httptest"
    "testing"

    "github.com/gofiber/fiber/v2"
    "github.com/stretchr/testify/assert"

    "{{module_path}}/internal/api/handlers"
    "{{module_path}}/internal/domain/repositories"
    "{{module_path}}/internal/domain/services"
    "{{module_path}}/internal/infrastructure/database"
    "{{module_path}}/internal/pkg/auth"
    "{{module_path}}/internal/pkg/logger"
)

func setupTestApp(t *testing.T) *fiber.App {
    // Setup test database
    db := setupTestDatabase(t)

    // Initialize dependencies
    jwtManager := auth.NewJWTManager("test-secret", time.Hour)
    userRepo := repositories.NewUserRepository(db)
    userService := services.NewUserService(userRepo, jwtManager)
    log := logger.NewLogger(logger.Config{Level: "error"})

    authHandler := handlers.NewAuthHandler(userService, log)

    app := fiber.New()
    app.Post("/register", authHandler.Register)
    app.Post("/login", authHandler.Login)

    return app
}

func TestAuthAPI_Register(t *testing.T) {
    app := setupTestApp(t)

    payload := map[string]string{
        "email":    "test@example.com",
        "password": "password123",
        "name":     "Test User",
    }
    body, _ := json.Marshal(payload)

    req := httptest.NewRequest(http.MethodPost, "/register", bytes.NewReader(body))
    req.Header.Set("Content-Type", "application/json")

    resp, err := app.Test(req)
    assert.NoError(t, err)
    assert.Equal(t, fiber.StatusCreated, resp.StatusCode)

    var result map[string]interface{}
    json.NewDecoder(resp.Body).Decode(&result)

    assert.NotNil(t, result["user"])
    assert.NotEmpty(t, result["token"])
}
```

---

# 10. Docker Setup

## Dockerfile (Multi-stage)

```dockerfile
# Build stage
FROM golang:1.25-alpine AS builder

WORKDIR /app

# Install dependencies
RUN apk add --no-cache git ca-certificates tzdata

# Copy go mod files
COPY go.mod go.sum ./
RUN go mod download

# Copy source code
COPY . .

# Build binary
RUN CGO_ENABLED=0 GOOS=linux go build -a -installsuffix cgo -ldflags '-extldflags "-static"' -o main ./cmd/api

# Final stage
FROM scratch

# Copy CA certificates and timezone data
COPY --from=builder /etc/ssl/certs/ca-certificates.crt /etc/ssl/certs/
COPY --from=builder /usr/share/zoneinfo /usr/share/zoneinfo

# Copy binary
COPY --from=builder /app/main /main

# Expose port
EXPOSE 8080

# Run
ENTRYPOINT ["/main"]
```

## docker-compose.yml

```yaml
version: '3.9'

services:
  api:
    build: .
    ports:
      - "8080:8080"
    environment:
      - APP_ENV=development
      - DATABASE_URL=postgres://postgres:postgres@postgres:5432/myapp?sslmode=disable
      - REDIS_URL=redis://redis:6379/0
      - JWT_SECRET=your-super-secret-jwt-key-min-32-chars
    depends_on:
      - postgres
      - redis
    volumes:
      - .:/app
    restart: unless-stopped

  postgres:
    image: postgres:18-alpine
    ports:
      - "5432:5432"
    environment:
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=postgres
      - POSTGRES_DB=myapp
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    command: redis-server --appendonly yes

volumes:
  postgres_data:
  redis_data:
```

## Makefile

```makefile
.PHONY: run build test migrate-up migrate-down docker-up docker-down

run:
	go run cmd/api/main.go

build:
	go build -o bin/main cmd/api/main.go

test:
	go test -v -race -coverprofile=coverage.out ./...

test-coverage:
	go test -v -race -coverprofile=coverage.out ./...
	go tool cover -html=coverage.out

migrate-create:
	migrate create -ext sql -dir migrations -seq $(name)

migrate-up:
	migrate -path migrations -database "$(DATABASE_URL)" up

migrate-down:
	migrate -path migrations -database "$(DATABASE_URL)" down

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

docker-build:
	docker-compose build

lint:
	golangci-lint run

fmt:
	go fmt ./...

tidy:
	go mod tidy

air:
	air
```

---

# 11. Production Checklist

## Security [OK]
- [ ] JWT secret is strong (min 32 chars) and stored in secret manager
- [ ] HTTPS enforced (TLS 1.2+ only)
- [ ] Rate limiting configured per endpoint
- [ ] CORS restricted to specific origins
- [ ] SQL injection prevention (GORM parameterized queries)
- [ ] Password hashing with bcrypt (cost 12+)
- [ ] Input validation on all endpoints
- [ ] Security headers (Helmet middleware)
- [ ] Dependency vulnerability scanning (go mod audit)
- [ ] API key rotation policy

## Performance [OK]
- [ ] Database connection pooling configured
- [ ] Redis caching for read-heavy operations
- [ ] Cursor-based pagination for large datasets
- [ ] Database indexes on foreign keys and query columns
- [ ] Response compression enabled
- [ ] Goroutine pool limits set
- [ ] Profiling enabled (pprof endpoints)
- [ ] Load testing completed (k6, vegeta)

## Observability [OK]
- [ ] Structured logging (JSON format)
- [ ] Request ID tracking
- [ ] Error tracking (Sentry, Rollbar)
- [ ] APM integration (New Relic, Datadog)
- [ ] Health check endpoint
- [ ] Metrics exposed (Prometheus format)
- [ ] Distributed tracing (OpenTelemetry)

## Deployment [OK]
- [ ] Multi-stage Docker build
- [ ] Container security scanning
- [ ] Environment variables validated
- [ ] Database migrations automated
- [ ] Graceful shutdown implemented
- [ ] Zero-downtime deployment strategy
- [ ] Rollback plan documented
- [ ] CI/CD pipeline configured

## Reliability [OK]
- [ ] Database backups automated
- [ ] Redis persistence configured
- [ ] Circuit breaker for external services
- [ ] Retry logic with exponential backoff
- [ ] Timeout configured for all operations
- [ ] Panic recovery middleware
- [ ] Dead letter queue for failed jobs

---

# 12. API Documentation

## Swagger/OpenAPI Setup

```go
// Install: go get -u github.com/swaggo/swag/cmd/swag
// Install: go get -u github.com/gofiber/swagger

package main

import (
    "github.com/gofiber/fiber/v2"
    "github.com/gofiber/swagger"

    _ "{{module_path}}/docs" // Generated by swag
)

// @title           Your API
// @version         1.0
// @description     API documentation for your backend service
// @termsOfService  http://swagger.io/terms/

// @contact.name   API Support
// @contact.url    http://www.example.com/support
// @contact.email  support@example.com

// @license.name  MIT
// @license.url   https://opensource.org/licenses/MIT

// @host      localhost:8080
// @BasePath  /api/v1

// @securityDefinitions.apikey Bearer
// @in header
// @name Authorization
// @description Type "Bearer" followed by a space and JWT token.

func main() {
    app := fiber.New()

    // Swagger route
    app.Get("/swagger/*", swagger.HandlerDefault)

    // Your routes...
}

// Generate docs: swag init -g cmd/api/main.go
```

## Example Documented Endpoint

```go
// Register godoc
// @Summary      Register a new user
// @Description  Create a new user account
// @Tags         auth
// @Accept       json
// @Produce      json
// @Param        request body RegisterRequest true "User registration details"
// @Success      201  {object}  map[string]interface{}
// @Failure      400  {object}  map[string]interface{}
// @Router       /auth/register [post]
func (h *AuthHandler) Register(c *fiber.Ctx) error {
    // Implementation...
}
```

---

# END

**Congratulations!** You now have a production-grade Go backend with Fiber, GORM, and PostgreSQL.

**Next Steps:**
1. Run `go mod tidy` to install dependencies
2. Copy `.env.example` to `.env` and configure
3. Start services with `docker-compose up -d`
4. Run migrations with `make migrate-up`
5. Start development server with `make run` or `make air` (hot reload)
6. Access Swagger docs at `http://localhost:8080/swagger/index.html`

**Go-Specific Best Practices:**
- Use goroutines for concurrent operations (with proper sync/error handling)
- Leverage Go's context for timeouts and cancellation
- Profile with pprof (`import _ "net/http/pprof"`)
- Use `errgroup` for coordinated goroutine error handling
- Implement graceful shutdown with signal handling
- Use `sync.Pool` for reusing expensive objects
- Benchmark performance-critical code with `go test -bench`
