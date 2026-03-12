# Configuration Validation Utilities

Centralized patterns for environment variable loading with schema validation and secrets management.

**Updated**: December 2025
**Node.js**: 24 LTS | **Python**: 3.14+ | **TypeScript**: 5.7+

---

## File Structure

```
src/
├── config/
│   ├── index.ts         # Main config export
│   ├── schema.ts        # Validation schema (Zod or Valibot)
│   └── secrets.ts       # Secrets loader (optional)
└── types/
    └── config.ts        # Config types (if not inferred)
```

---

## TypeScript: Zod 3.24+

### Dependencies

```bash
npm install zod@^3.24 dotenv
```

### Schema (`src/config/schema.ts`)

```typescript
import { z } from 'zod';

// ============================================
// ZOD 3.24+ FEATURES
// ============================================

// 1. z.pipe() for transform chains
const portSchema = z.string()
  .pipe(z.coerce.number().int().min(1).max(65535));

// 2. z.string().url() with protocol validation
const urlSchema = z.string().url().refine(
  (url) => url.startsWith('https://') || url.startsWith('postgresql://'),
  { message: 'Must use HTTPS or postgresql://' }
);

// 3. z.string().datetime() for ISO 8601
const timestampSchema = z.string().datetime({ offset: true });

// ============================================
// ENVIRONMENT SCHEMA
// ============================================

export const envSchema = z.object({
  // Server
  NODE_ENV: z.enum(['development', 'production', 'test']).default('development'),
  PORT: z.string().pipe(z.coerce.number().int().min(1).max(65535)).default('3000'),
  HOST: z.string().default('0.0.0.0'),

  // Database
  DATABASE_URL: z.string().url(),

  // Authentication (secrets - see Secrets Management section)
  JWT_SECRET: z.string().min(32, 'JWT_SECRET must be at least 32 characters'),
  JWT_ACCESS_EXPIRE: z.string().default('15m'),
  JWT_REFRESH_SECRET: z.string().min(32).optional(),
  JWT_REFRESH_EXPIRE: z.string().default('7d'),

  // Redis (optional)
  REDIS_URL: z.string().url().optional(),

  // CORS - transform to array
  CORS_ORIGINS: z.string()
    .default('http://localhost:3000')
    .transform((s) => s.split(',').map((o) => o.trim())),

  // Rate limiting
  RATE_LIMIT_WINDOW_MS: z.string().pipe(z.coerce.number().int().positive()).default('60000'),
  RATE_LIMIT_MAX_REQUESTS: z.string().pipe(z.coerce.number().int().positive()).default('100'),

  // Logging
  LOG_LEVEL: z.enum(['debug', 'info', 'warn', 'error']).default('info'),

  // Feature flags (Zod 3.24+ branded types)
  FEATURE_NEW_DASHBOARD: z.string()
    .transform((s) => s.toLowerCase() === 'true')
    .default('false'),
});

export type EnvConfig = z.infer<typeof envSchema>;
```

### Config Export (`src/config/index.ts`)

```typescript
import 'dotenv/config';
import { envSchema, type EnvConfig } from './schema';

// Fail fast at startup
const parseResult = envSchema.safeParse(process.env);

if (!parseResult.success) {
  const errors = parseResult.error.flatten().fieldErrors;
  console.error('ERROR: Invalid environment variables:');

  for (const [field, messages] of Object.entries(errors)) {
    console.error(`  ${field}: ${messages?.join(', ')}`);
  }

  process.exit(1);
}

export const config: EnvConfig = parseResult.data;

// Computed values
export const isDevelopment = config.NODE_ENV === 'development';
export const isProduction = config.NODE_ENV === 'production';
export const isTest = config.NODE_ENV === 'test';

// CORS_ORIGINS already transformed to array by schema
export const corsOrigins = config.CORS_ORIGINS;
```

---

## TypeScript: Valibot (Lightweight Alternative)

Valibot is a smaller alternative to Zod (~1KB vs ~12KB minified).

### Dependencies

```bash
npm install valibot@^1.0 dotenv
```

### Schema (`src/config/schema.ts`)

```typescript
import * as v from 'valibot';

// ============================================
// VALIBOT SCHEMA
// ============================================

export const envSchema = v.object({
  // Server
  NODE_ENV: v.optional(
    v.picklist(['development', 'production', 'test']),
    'development'
  ),
  PORT: v.pipe(
    v.optional(v.string(), '3000'),
    v.transform((s) => parseInt(s, 10)),
    v.number(),
    v.integer(),
    v.minValue(1),
    v.maxValue(65535)
  ),
  HOST: v.optional(v.string(), '0.0.0.0'),

  // Database
  DATABASE_URL: v.pipe(v.string(), v.url()),

  // Authentication
  JWT_SECRET: v.pipe(
    v.string(),
    v.minLength(32, 'JWT_SECRET must be at least 32 characters')
  ),
  JWT_ACCESS_EXPIRE: v.optional(v.string(), '15m'),
  JWT_REFRESH_SECRET: v.optional(
    v.pipe(v.string(), v.minLength(32))
  ),
  JWT_REFRESH_EXPIRE: v.optional(v.string(), '7d'),

  // CORS - transform to array
  CORS_ORIGINS: v.pipe(
    v.optional(v.string(), 'http://localhost:3000'),
    v.transform((s) => s.split(',').map((o) => o.trim()))
  ),

  // Logging
  LOG_LEVEL: v.optional(
    v.picklist(['debug', 'info', 'warn', 'error']),
    'info'
  ),
});

export type EnvConfig = v.InferOutput<typeof envSchema>;
```

### Config Export (`src/config/index.ts`)

```typescript
import 'dotenv/config';
import * as v from 'valibot';
import { envSchema, type EnvConfig } from './schema';

const parseResult = v.safeParse(envSchema, process.env);

if (!parseResult.success) {
  console.error('ERROR: Invalid environment variables:');

  for (const issue of parseResult.issues) {
    const path = issue.path?.map((p) => p.key).join('.') || 'unknown';
    console.error(`  ${path}: ${issue.message}`);
  }

  process.exit(1);
}

export const config: EnvConfig = parseResult.output;

export const isDevelopment = config.NODE_ENV === 'development';
export const isProduction = config.NODE_ENV === 'production';
export const isTest = config.NODE_ENV === 'test';
```

### Zod vs Valibot Comparison

| Feature | Zod 3.24+ | Valibot 1.x |
|---------|-----------|-------------|
| Bundle size | ~12KB | ~1KB |
| API style | Method chaining | Function composition |
| TypeScript | Excellent | Excellent |
| Transforms | `.transform()` | `v.transform()` in pipe |
| Defaults | `.default()` | `v.optional(schema, default)` |
| Ecosystem | Larger | Growing |

**Recommendation**: Use Zod for complex validation, Valibot for size-sensitive apps.

---

## Python: Pydantic 2.x

### Dependencies

```bash
pip install pydantic>=2.10 pydantic-settings>=2.7
```

### Settings (`src/config/settings.py`)

```python
from functools import lru_cache
from typing import Annotated

from pydantic import (
    AnyHttpUrl,
    Field,
    PostgresDsn,
    field_validator,
    model_validator,
)
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",  # Ignore unknown env vars
    )

    # Server
    app_env: str = Field(default="development", alias="APP_ENV")
    app_host: str = Field(default="0.0.0.0", alias="APP_HOST")
    app_port: Annotated[int, Field(ge=1, le=65535)] = Field(
        default=8000, alias="APP_PORT"
    )

    # Database
    database_url: PostgresDsn = Field(alias="DATABASE_URL")

    # Authentication
    jwt_secret: Annotated[str, Field(min_length=32)] = Field(alias="JWT_SECRET")
    jwt_access_expire_minutes: int = Field(default=15, alias="JWT_ACCESS_EXPIRE_MINUTES")
    jwt_refresh_secret: str | None = Field(default=None, alias="JWT_REFRESH_SECRET")
    jwt_refresh_expire_days: int = Field(default=7, alias="JWT_REFRESH_EXPIRE_DAYS")

    # Redis (optional)
    redis_url: AnyHttpUrl | None = Field(default=None, alias="REDIS_URL")

    # CORS
    cors_origins: str = Field(
        default="http://localhost:3000", alias="CORS_ORIGINS"
    )

    # Logging
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        allowed = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        upper = v.upper()
        if upper not in allowed:
            raise ValueError(f"log_level must be one of {allowed}")
        return upper

    @model_validator(mode="after")
    def validate_refresh_secret(self) -> "Settings":
        """Ensure refresh secret is set in production."""
        if self.app_env == "production" and not self.jwt_refresh_secret:
            raise ValueError("JWT_REFRESH_SECRET required in production")
        return self

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",")]

    @property
    def is_development(self) -> bool:
        return self.app_env == "development"

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
```

### Usage

```python
from src.config.settings import settings

print(settings.app_port)              # int, validated
print(settings.database_url)          # PostgresDsn, validated
print(settings.is_production)         # bool
print(settings.cors_origins_list)     # list[str]
```

---

## Go 1.25+

### Dependencies

```bash
go get github.com/caarlos0/env/v11
go get github.com/go-playground/validator/v10
```

### Config (`internal/config/config.go`)

```go
package config

import (
	"fmt"
	"strings"
	"time"

	"github.com/caarlos0/env/v11"
	"github.com/go-playground/validator/v10"
)

type Config struct {
	// Server
	Env  string `env:"APP_ENV" envDefault:"development" validate:"oneof=development production test"`
	Host string `env:"HOST" envDefault:"0.0.0.0"`
	Port int    `env:"PORT" envDefault:"3000" validate:"min=1,max=65535"`

	// Database
	DatabaseURL string `env:"DATABASE_URL,required" validate:"required,url"`

	// JWT
	JWTSecret        string        `env:"JWT_SECRET,required" validate:"required,min=32"`
	JWTAccessExpire  time.Duration `env:"JWT_ACCESS_EXPIRE" envDefault:"15m"`
	JWTRefreshSecret string        `env:"JWT_REFRESH_SECRET"`
	JWTRefreshExpire time.Duration `env:"JWT_REFRESH_EXPIRE" envDefault:"168h"` // 7 days

	// Redis
	RedisURL string `env:"REDIS_URL"`

	// CORS (comma-separated in env, parsed to slice)
	CORSOriginsRaw string   `env:"CORS_ORIGINS" envDefault:"http://localhost:3000"`
	CORSOrigins    []string `env:"-"` // Computed field

	// Logging
	LogLevel string `env:"LOG_LEVEL" envDefault:"info" validate:"oneof=debug info warn error"`
}

func Load() (*Config, error) {
	cfg := &Config{}

	// Parse environment variables
	if err := env.Parse(cfg); err != nil {
		return nil, fmt.Errorf("failed to parse env: %w", err)
	}

	// Transform CORS origins
	cfg.CORSOrigins = parseCORSOrigins(cfg.CORSOriginsRaw)

	// Validate struct
	validate := validator.New()
	if err := validate.Struct(cfg); err != nil {
		return nil, fmt.Errorf("config validation failed: %w", err)
	}

	// Production-specific validation
	if cfg.Env == "production" && cfg.JWTRefreshSecret == "" {
		return nil, fmt.Errorf("JWT_REFRESH_SECRET required in production")
	}

	return cfg, nil
}

func parseCORSOrigins(raw string) []string {
	parts := strings.Split(raw, ",")
	origins := make([]string, 0, len(parts))
	for _, part := range parts {
		if trimmed := strings.TrimSpace(part); trimmed != "" {
			origins = append(origins, trimmed)
		}
	}
	return origins
}

func (c *Config) IsDevelopment() bool { return c.Env == "development" }
func (c *Config) IsProduction() bool  { return c.Env == "production" }
func (c *Config) IsTest() bool        { return c.Env == "test" }
```

### Usage

```go
package main

import (
	"log"

	"myapp/internal/config"
)

func main() {
	cfg, err := config.Load()
	if err != nil {
		log.Fatalf("Config error: %v", err)
	}

	log.Printf("Server: %s:%d (%s)", cfg.Host, cfg.Port, cfg.Env)
}
```

---

## Secrets Management

**NEVER commit secrets to git.** Use external secret managers for production.

### 1Password CLI (Recommended for Teams)

```bash
# Install 1Password CLI
brew install 1password-cli

# Authenticate
op signin

# Load secrets at runtime
export JWT_SECRET=$(op read "op://Vault/MyApp/JWT_SECRET")
export DATABASE_URL=$(op read "op://Vault/MyApp/DATABASE_URL")

# Or use op run for full env injection
op run --env-file=.env.1p -- npm start
```

**.env.1p** (template for 1Password):
```bash
JWT_SECRET=op://Vault/MyApp/JWT_SECRET
DATABASE_URL=op://Vault/MyApp/DATABASE_URL
JWT_REFRESH_SECRET=op://Vault/MyApp/JWT_REFRESH_SECRET
```

### Doppler (Cloud-Native)

```bash
# Install Doppler CLI
brew install dopplerhq/cli/doppler

# Setup project
doppler setup

# Run with injected secrets
doppler run -- npm start

# Or export to .env (for local dev only)
doppler secrets download --no-file --format env > .env
```

### AWS Secrets Manager

```typescript
import { SecretsManagerClient, GetSecretValueCommand } from '@aws-sdk/client-secrets-manager';

const client = new SecretsManagerClient({ region: 'us-east-1' });

export const loadSecrets = async (secretId: string): Promise<Record<string, string>> => {
  const command = new GetSecretValueCommand({ SecretId: secretId });
  const response = await client.send(command);

  if (response.SecretString) {
    return JSON.parse(response.SecretString);
  }

  throw new Error('Secret not found');
};

// Usage at startup
const secrets = await loadSecrets('myapp/production');
process.env.JWT_SECRET = secrets.JWT_SECRET;
process.env.DATABASE_URL = secrets.DATABASE_URL;
```

### HashiCorp Vault

```typescript
import Vault from 'node-vault';

const vault = Vault({
  endpoint: process.env.VAULT_ADDR,
  token: process.env.VAULT_TOKEN,
});

export const loadVaultSecrets = async (path: string): Promise<Record<string, string>> => {
  const result = await vault.read(path);
  return result.data.data;
};
```

### Secret Rotation Pattern

```typescript
// Auto-refresh secrets every hour
let cachedSecrets: Record<string, string> | null = null;
let lastRefresh = 0;
const REFRESH_INTERVAL = 60 * 60 * 1000; // 1 hour

export const getSecret = async (key: string): Promise<string> => {
  const now = Date.now();

  if (!cachedSecrets || now - lastRefresh > REFRESH_INTERVAL) {
    cachedSecrets = await loadSecrets('myapp/production');
    lastRefresh = now;
  }

  const value = cachedSecrets[key];
  if (!value) {
    throw new Error(`Secret ${key} not found`);
  }

  return value;
};
```

---

## Environment File Template

### `.env.example`

```bash
# Server
NODE_ENV=development
PORT=3000
HOST=0.0.0.0

# Database (required)
DATABASE_URL=postgresql://user:password@localhost:5432/mydb

# Authentication (required)
# Generate: openssl rand -base64 32
JWT_SECRET=your-super-secret-key-at-least-32-chars
JWT_ACCESS_EXPIRE=15m
JWT_REFRESH_SECRET=another-secret-key-at-least-32-chars
JWT_REFRESH_EXPIRE=7d

# Redis (optional)
REDIS_URL=redis://localhost:6379

# CORS (comma-separated)
CORS_ORIGINS=http://localhost:3000,http://localhost:5173

# Rate limiting
RATE_LIMIT_WINDOW_MS=60000
RATE_LIMIT_MAX_REQUESTS=100

# Logging
LOG_LEVEL=debug

# Feature flags
FEATURE_NEW_DASHBOARD=false
```

### `.gitignore`

```gitignore
# Environment files
.env
.env.local
.env.*.local
!.env.example
!.env.test
```

---

## Anti-Patterns

### Non-Null Assertions on Environment Variables

**This is the #1 cause of production crashes from missing config.**

```typescript
// BAD: Non-null assertion crashes at runtime if missing
const apiKey = process.env.OPENAI_API_KEY!;  // Runtime crash if undefined
const dbUrl = process.env.DATABASE_URL!;     // TypeScript trusts you, runtime doesn't

// BAD: Trusting environment without validation
const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!;
const supabaseKey = process.env.SUPABASE_SERVICE_ROLE_KEY!;
// If either is missing, your app crashes with unhelpful error

// GOOD: Fail fast with clear message
function getRequiredEnv(key: string): string {
  const value = process.env[key];
  if (!value) {
    throw new Error(`Missing required environment variable: ${key}`);
  }
  return value;
}

const apiKey = getRequiredEnv('OPENAI_API_KEY');
const dbUrl = getRequiredEnv('DATABASE_URL');

// BETTER: Zod validation at startup (recommended)
import { z } from 'zod';

const envSchema = z.object({
  OPENAI_API_KEY: z.string().min(1, 'OPENAI_API_KEY is required'),
  DATABASE_URL: z.string().url('DATABASE_URL must be a valid URL'),
  NODE_ENV: z.enum(['development', 'production', 'test']).default('development'),
  // Optional with sensible default
  LOG_LEVEL: z.enum(['debug', 'info', 'warn', 'error']).default('info'),
});

// Validate once at startup, export typed config
const parseResult = envSchema.safeParse(process.env);
if (!parseResult.success) {
  console.error('ERROR: Environment validation failed:');
  console.error(parseResult.error.flatten().fieldErrors);
  process.exit(1);
}

export const env = parseResult.data;
// Now env.OPENAI_API_KEY is guaranteed to exist and is typed as string
```

**Why Non-Null Assertions Are Dangerous:**

| Pattern | Behavior | Problem |
|---------|----------|---------|
| `process.env.VAR!` | TypeScript trusts you | Crashes at runtime if missing |
| `process.env.VAR \|\| ''` | Silent empty string | App runs with broken config |
| `getRequiredEnv('VAR')` | Throws with clear message | Good, but manual |
| Zod validation | Validates all at startup | Best - catches all issues early |

### Scattered Config Access

```typescript
// BAD: Raw process.env everywhere
const port = parseInt(process.env.PORT || '3000');  // No validation
const secret = process.env.JWT_SECRET;               // Could be undefined

// GOOD: Centralized, validated config
import { config } from '@/config';
const port = config.PORT;         // Already number, validated
const secret = config.JWT_SECRET; // Guaranteed to exist
```

### Secrets in Code

```typescript
// BAD: Hardcoded secrets
const JWT_SECRET = 'my-super-secret-key-123';

// BAD: Secrets in .env committed to git
// (in .env file committed to repo)

// GOOD: External secret manager
const JWT_SECRET = await getSecret('JWT_SECRET');

// GOOD: Environment variable from CI/CD
const JWT_SECRET = process.env.JWT_SECRET;
```

### No Startup Validation

```typescript
// BAD: Fails at runtime when config is used
app.listen(process.env.PORT); // Could be undefined

// GOOD: Fails at startup with clear error
const parseResult = envSchema.safeParse(process.env);
if (!parseResult.success) {
  console.error('Invalid config:', parseResult.error.flatten());
  process.exit(1);
}
```

---

## Security Checklist

- [ ] **No secrets in git** - Use .env.example, not .env
- [ ] **Minimum 32 chars** for JWT secrets
- [ ] **HTTPS only** in production URLs
- [ ] **Fail fast** at startup on invalid config
- [ ] **External secret manager** for production (1Password, Doppler, Vault)
- [ ] **Rotate secrets** periodically (at least quarterly)
- [ ] **Different secrets** per environment (dev/staging/prod)
- [ ] **Audit secret access** in production

---

## References

- [Zod 3.24 Documentation](https://zod.dev)
- [Valibot Documentation](https://valibot.dev)
- [Pydantic Settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)
- [1Password CLI](https://developer.1password.com/docs/cli/)
- [Doppler Documentation](https://docs.doppler.com)
- [AWS Secrets Manager](https://docs.aws.amazon.com/secretsmanager/)
