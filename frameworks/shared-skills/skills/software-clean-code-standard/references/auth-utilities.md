# Authentication Utilities

Centralized patterns for password hashing, JWT, and OAuth 2.1. Updated December 2025.

---

## Quick Reference

| Task | Library | Version | Notes |
|------|---------|---------|-------|
| Password hashing | argon2 / @node-rs/argon2 | 2.x | Recommended over bcrypt |
| JWT (TypeScript) | jose | 5.x | Standards-compliant, no native deps |
| JWT (Python) | PyJWT | 2.9+ | Or python-jose for JWE |
| JWT (Go) | golang-jwt/jwt | v5 | Current standard |
| OAuth 2.1 | openid-client | 6.x | PKCE required |

---

## File Structure

```text
src/
├── utils/
│   └── auth.ts          # JWT, password utilities
├── middleware/
│   └── auth.ts          # Auth middleware (uses utils/auth)
└── types/
    └── auth.ts          # Shared types
```

---

## TypeScript/Node.js

### Types (`src/types/auth.ts`)

```typescript
export interface TokenPayload {
  userId: string;
  email: string;
  role: 'user' | 'admin';
  iat?: number;
  exp?: number;
}

export interface AuthUser {
  id: string;
  email: string;
  role: string;
}

export interface TokenPair {
  accessToken: string;
  refreshToken: string;
}
```

### Utilities (`src/utils/auth.ts`)

```typescript
import { hash, verify } from '@node-rs/argon2';
import { SignJWT, jwtVerify, type JWTPayload } from 'jose';
import { config } from '@/config';
import type { TokenPayload, TokenPair } from '@/types/auth';

// ============================================
// PASSWORD HASHING (Argon2id - recommended)
// ============================================

// Argon2id with OWASP-recommended parameters
const ARGON2_OPTIONS = {
  memoryCost: 65536,      // 64 MiB
  timeCost: 3,            // 3 iterations
  parallelism: 4,         // 4 threads
};

export const hashPassword = async (password: string): Promise<string> => {
  return hash(password, ARGON2_OPTIONS);
};

export const verifyPassword = async (
  password: string,
  hashedPassword: string
): Promise<boolean> => {
  try {
    return await verify(hashedPassword, password);
  } catch {
    return false;
  }
};

// ============================================
// JWT TOKENS (jose library)
// ============================================

const ACCESS_SECRET = new TextEncoder().encode(config.JWT_SECRET);
const REFRESH_SECRET = new TextEncoder().encode(config.JWT_REFRESH_SECRET);

export const generateAccessToken = async (
  payload: Omit<TokenPayload, 'iat' | 'exp'>
): Promise<string> => {
  return new SignJWT({ ...payload } as JWTPayload)
    .setProtectedHeader({ alg: 'HS256' })
    .setIssuedAt()
    .setExpirationTime(config.JWT_ACCESS_EXPIRE || '15m')
    .sign(ACCESS_SECRET);
};

export const generateRefreshToken = async (
  payload: Pick<TokenPayload, 'userId'>
): Promise<string> => {
  return new SignJWT({ userId: payload.userId } as JWTPayload)
    .setProtectedHeader({ alg: 'HS256' })
    .setIssuedAt()
    .setExpirationTime(config.JWT_REFRESH_EXPIRE || '7d')
    .sign(REFRESH_SECRET);
};

export const generateTokenPair = async (
  payload: Omit<TokenPayload, 'iat' | 'exp'>
): Promise<TokenPair> => {
  const [accessToken, refreshToken] = await Promise.all([
    generateAccessToken(payload),
    generateRefreshToken({ userId: payload.userId }),
  ]);
  return { accessToken, refreshToken };
};

export const verifyAccessToken = async (token: string): Promise<TokenPayload> => {
  const { payload } = await jwtVerify(token, ACCESS_SECRET);
  return payload as unknown as TokenPayload;
};

export const verifyRefreshToken = async (
  token: string
): Promise<Pick<TokenPayload, 'userId'>> => {
  const { payload } = await jwtVerify(token, REFRESH_SECRET);
  return { userId: payload.userId as string };
};

// ============================================
// TOKEN EXTRACTION
// ============================================

export const extractBearerToken = (header: string | undefined): string | null => {
  if (!header?.startsWith('Bearer ')) return null;
  return header.slice(7);
};
```

### Middleware (`src/middleware/auth.ts`)

```typescript
import type { Request, Response, NextFunction } from 'express';
import { verifyAccessToken, extractBearerToken } from '@/utils/auth';
import { UnauthorizedError, ForbiddenError } from '@/utils/errors';
import type { AuthUser } from '@/types/auth';

declare global {
  namespace Express {
    interface Request {
      user?: AuthUser;
    }
  }
}

export const authenticate = async (
  req: Request,
  _res: Response,
  next: NextFunction
): Promise<void> => {
  const token = extractBearerToken(req.headers.authorization);

  if (!token) {
    return next(new UnauthorizedError('Missing authorization token'));
  }

  try {
    const payload = await verifyAccessToken(token);
    req.user = {
      id: payload.userId,
      email: payload.email,
      role: payload.role,
    };
    next();
  } catch {
    next(new UnauthorizedError('Invalid or expired token'));
  }
};

export const requireRole = (...roles: string[]) => {
  return (req: Request, _res: Response, next: NextFunction): void => {
    if (!req.user) {
      return next(new UnauthorizedError('Not authenticated'));
    }
    if (!roles.includes(req.user.role)) {
      return next(new ForbiddenError('Insufficient permissions'));
    }
    next();
  };
};
```

---

## Python (FastAPI)

### Utilities (`src/utils/auth.py`)

```python
from datetime import datetime, timedelta, timezone
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
import jwt
from src.config import settings

# Argon2id with OWASP-recommended parameters
ph = PasswordHasher(
    time_cost=3,
    memory_cost=65536,
    parallelism=4,
)

# ============================================
# PASSWORD HASHING (Argon2id)
# ============================================

def hash_password(password: str) -> str:
    """Hash password using Argon2id."""
    return ph.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash. Returns False on mismatch."""
    try:
        ph.verify(hashed_password, plain_password)
        return True
    except VerifyMismatchError:
        return False

def needs_rehash(hashed_password: str) -> bool:
    """Check if password hash needs updating to current parameters."""
    return ph.check_needs_rehash(hashed_password)

# ============================================
# JWT TOKENS
# ============================================

def create_access_token(user_id: int, email: str, role: str) -> str:
    """Create short-lived access token (15 min default)."""
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.JWT_ACCESS_EXPIRE_MINUTES
    )
    payload = {
        "sub": str(user_id),
        "email": email,
        "role": role,
        "exp": expire,
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm="HS256")

def create_refresh_token(user_id: int) -> str:
    """Create long-lived refresh token (7 days default)."""
    expire = datetime.now(timezone.utc) + timedelta(
        days=settings.JWT_REFRESH_EXPIRE_DAYS
    )
    payload = {
        "sub": str(user_id),
        "exp": expire,
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, settings.JWT_REFRESH_SECRET, algorithm="HS256")

def create_token_pair(user_id: int, email: str, role: str) -> dict[str, str]:
    """Create both access and refresh tokens."""
    return {
        "access_token": create_access_token(user_id, email, role),
        "refresh_token": create_refresh_token(user_id),
    }

def decode_access_token(token: str) -> dict:
    """Decode and validate access token."""
    return jwt.decode(token, settings.JWT_SECRET, algorithms=["HS256"])

def decode_refresh_token(token: str) -> dict:
    """Decode and validate refresh token."""
    return jwt.decode(token, settings.JWT_REFRESH_SECRET, algorithms=["HS256"])
```

### Dependencies (`src/dependencies/auth.py`)

```python
from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from jwt.exceptions import InvalidTokenError
from src.utils.auth import decode_access_token, verify_password, needs_rehash
from src.database import get_db
from src.repositories.user import UserRepository

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Extract and validate user from JWT token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_access_token(token)
        user_id = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except InvalidTokenError:
        raise credentials_exception

    user = await UserRepository(db).get_by_id(int(user_id))
    if user is None:
        raise credentials_exception
    return user

def require_role(*roles: str):
    """Dependency factory for role-based access control."""
    async def role_checker(user=Depends(get_current_user)):
        if user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )
        return user
    return role_checker
```

---

## Go (Fiber)

### Utilities (`internal/utils/auth.go`)

```go
package utils

import (
	"errors"
	"time"

	"github.com/alexedwards/argon2id"
	"github.com/golang-jwt/jwt/v5"
)

// Argon2id params (OWASP recommended)
var argon2Params = &argon2id.Params{
	Memory:      64 * 1024, // 64 MiB
	Iterations:  3,
	Parallelism: 4,
	SaltLength:  16,
	KeyLength:   32,
}

// ============================================
// PASSWORD HASHING (Argon2id)
// ============================================

func HashPassword(password string) (string, error) {
	return argon2id.CreateHash(password, argon2Params)
}

func VerifyPassword(password, hash string) (bool, error) {
	return argon2id.ComparePasswordAndHash(password, hash)
}

// ============================================
// JWT TOKENS
// ============================================

type TokenClaims struct {
	UserID string `json:"user_id"`
	Email  string `json:"email"`
	Role   string `json:"role"`
	jwt.RegisteredClaims
}

type TokenPair struct {
	AccessToken  string `json:"access_token"`
	RefreshToken string `json:"refresh_token"`
}

func GenerateAccessToken(userID, email, role, secret string, expiry time.Duration) (string, error) {
	claims := TokenClaims{
		UserID: userID,
		Email:  email,
		Role:   role,
		RegisteredClaims: jwt.RegisteredClaims{
			ExpiresAt: jwt.NewNumericDate(time.Now().Add(expiry)),
			IssuedAt:  jwt.NewNumericDate(time.Now()),
		},
	}
	token := jwt.NewWithClaims(jwt.SigningMethodHS256, claims)
	return token.SignedString([]byte(secret))
}

func GenerateRefreshToken(userID, secret string, expiry time.Duration) (string, error) {
	claims := jwt.RegisteredClaims{
		Subject:   userID,
		ExpiresAt: jwt.NewNumericDate(time.Now().Add(expiry)),
		IssuedAt:  jwt.NewNumericDate(time.Now()),
	}
	token := jwt.NewWithClaims(jwt.SigningMethodHS256, claims)
	return token.SignedString([]byte(secret))
}

func GenerateTokenPair(userID, email, role, accessSecret, refreshSecret string) (*TokenPair, error) {
	accessToken, err := GenerateAccessToken(userID, email, role, accessSecret, 15*time.Minute)
	if err != nil {
		return nil, err
	}

	refreshToken, err := GenerateRefreshToken(userID, refreshSecret, 7*24*time.Hour)
	if err != nil {
		return nil, err
	}

	return &TokenPair{
		AccessToken:  accessToken,
		RefreshToken: refreshToken,
	}, nil
}

func VerifyAccessToken(tokenString, secret string) (*TokenClaims, error) {
	token, err := jwt.ParseWithClaims(tokenString, &TokenClaims{}, func(t *jwt.Token) (interface{}, error) {
		if _, ok := t.Method.(*jwt.SigningMethodHMAC); !ok {
			return nil, errors.New("unexpected signing method")
		}
		return []byte(secret), nil
	})
	if err != nil {
		return nil, err
	}
	if claims, ok := token.Claims.(*TokenClaims); ok && token.Valid {
		return claims, nil
	}
	return nil, errors.New("invalid token")
}
```

### Middleware (`internal/middleware/auth.go`)

```go
package middleware

import (
	"strings"

	"github.com/gofiber/fiber/v2"
	"myapp/internal/config"
	"myapp/internal/utils"
)

func Authenticate(cfg *config.Config) fiber.Handler {
	return func(c *fiber.Ctx) error {
		auth := c.Get("Authorization")
		if auth == "" {
			return c.Status(401).JSON(fiber.Map{"error": "Missing authorization header"})
		}

		parts := strings.Split(auth, " ")
		if len(parts) != 2 || parts[0] != "Bearer" {
			return c.Status(401).JSON(fiber.Map{"error": "Invalid authorization format"})
		}

		claims, err := utils.VerifyAccessToken(parts[1], cfg.JWTSecret)
		if err != nil {
			return c.Status(401).JSON(fiber.Map{"error": "Invalid or expired token"})
		}

		c.Locals("user_id", claims.UserID)
		c.Locals("email", claims.Email)
		c.Locals("role", claims.Role)
		return c.Next()
	}
}

func RequireRole(roles ...string) fiber.Handler {
	return func(c *fiber.Ctx) error {
		userRole, ok := c.Locals("role").(string)
		if !ok {
			return c.Status(401).JSON(fiber.Map{"error": "Not authenticated"})
		}
		for _, role := range roles {
			if userRole == role {
				return c.Next()
			}
		}
		return c.Status(403).JSON(fiber.Map{"error": "Insufficient permissions"})
	}
}
```

---

## OAuth 2.1 / PKCE (TypeScript)

OAuth 2.1 requires PKCE for all clients. Use `openid-client` for standards-compliant implementation.

### PKCE Utilities (`src/utils/oauth.ts`)

```typescript
import { randomBytes, createHash } from 'node:crypto';

export const generateCodeVerifier = (): string => {
  return randomBytes(32).toString('base64url');
};

export const generateCodeChallenge = (verifier: string): string => {
  return createHash('sha256').update(verifier).digest('base64url');
};

export interface PKCEPair {
  codeVerifier: string;
  codeChallenge: string;
}

export const generatePKCE = (): PKCEPair => {
  const codeVerifier = generateCodeVerifier();
  const codeChallenge = generateCodeChallenge(codeVerifier);
  return { codeVerifier, codeChallenge };
};
```

### OAuth Client Setup

```typescript
import { Issuer, generators } from 'openid-client';

export const setupOAuthClient = async () => {
  const issuer = await Issuer.discover('https://accounts.google.com');

  const client = new issuer.Client({
    client_id: process.env.GOOGLE_CLIENT_ID!,
    client_secret: process.env.GOOGLE_CLIENT_SECRET!,
    redirect_uris: ['http://localhost:3000/auth/callback'],
    response_types: ['code'],
  });

  return client;
};

export const getAuthorizationUrl = async (client: any) => {
  const codeVerifier = generators.codeVerifier();
  const codeChallenge = generators.codeChallenge(codeVerifier);

  const url = client.authorizationUrl({
    scope: 'openid email profile',
    code_challenge: codeChallenge,
    code_challenge_method: 'S256',
    state: generators.state(),
  });

  return { url, codeVerifier };
};
```

---

## Usage Examples

### TypeScript Service

```typescript
// src/services/user.service.ts
import { hashPassword, verifyPassword, generateTokenPair } from '@/utils/auth';
import { UnauthorizedError } from '@/utils/errors';

export const createUser = async (email: string, password: string) => {
  const hashedPassword = await hashPassword(password);
  return db.user.create({ data: { email, password: hashedPassword } });
};

export const loginUser = async (email: string, password: string) => {
  const user = await db.user.findUnique({ where: { email } });
  if (!user || !(await verifyPassword(password, user.password))) {
    throw new UnauthorizedError('Invalid credentials');
  }
  return generateTokenPair({
    userId: user.id,
    email: user.email,
    role: user.role,
  });
};
```

### Python Router

```python
# src/routers/auth.py
from src.utils.auth import hash_password, verify_password, create_token_pair

@router.post("/register")
async def register(data: RegisterRequest, db: AsyncSession = Depends(get_db)):
    hashed = hash_password(data.password)
    user = await UserRepository(db).create(email=data.email, password=hashed)
    return {"id": user.id}

@router.post("/login")
async def login(data: LoginRequest, db: AsyncSession = Depends(get_db)):
    user = await UserRepository(db).get_by_email(data.email)
    if not user or not verify_password(data.password, user.password):
        raise HTTPException(401, "Invalid credentials")
    return create_token_pair(user.id, user.email, user.role)
```

---

## Migration Guide: bcrypt → Argon2

### Gradual Migration Pattern

```typescript
// Support both during migration
export const verifyPasswordWithMigration = async (
  password: string,
  hash: string,
  userId: string
): Promise<boolean> => {
  // Check if it's an Argon2 hash (starts with $argon2)
  if (hash.startsWith('$argon2')) {
    return verifyPassword(password, hash);
  }

  // Legacy bcrypt hash (starts with $2a, $2b, or $2y)
  const bcrypt = await import('bcrypt');
  const isValid = await bcrypt.compare(password, hash);

  if (isValid) {
    // Rehash with Argon2 on successful login
    const newHash = await hashPassword(password);
    await db.user.update({
      where: { id: userId },
      data: { password: newHash },
    });
  }

  return isValid;
};
```

---

## Anti-Patterns

```typescript
// BAD: Using bcrypt with low cost
const hash = await bcrypt.hash(password, 10);

// BAD: Using jsonwebtoken (legacy)
import jwt from 'jsonwebtoken';
const token = jwt.sign(payload, secret);

// BAD: Duplicated auth code
// user.service.ts
const hashPwd = async (p: string) => bcrypt.hash(p, 10);
// admin.service.ts
const hashPwd = async (p: string) => bcrypt.hash(p, 10);

// GOOD: Argon2 with OWASP params
const hash = await hashPassword(password);

// GOOD: jose library for JWT
const token = await generateAccessToken(payload);

// GOOD: Import from centralized utility
import { hashPassword, generateAccessToken } from '@/utils/auth';
```

---

## Dependencies

### TypeScript/Node.js

```json
{
  "@node-rs/argon2": "^2.0.0",
  "jose": "^5.9.0",
  "openid-client": "^6.1.0"
}
```

### Python

```txt
argon2-cffi>=23.1.0
PyJWT>=2.9.0
```

### Go

```bash
go get github.com/alexedwards/argon2id
go get github.com/golang-jwt/jwt/v5
```
