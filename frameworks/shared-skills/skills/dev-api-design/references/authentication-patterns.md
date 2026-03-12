# Authentication & Authorization Patterns

This guide provides production-ready patterns for securing API endpoints with authentication and authorization.

---

## Overview

**Authentication** - Verifying who the user is (identity)
**Authorization** - Verifying what the user can do (permissions)

Both are critical for API security and must work together.

---

## Authentication Strategies

### Strategy 1: JWT (JSON Web Tokens)

**Best for:** Stateless authentication, microservices, mobile/web apps

**Pros:**
- Stateless (no server-side session storage)
- Self-contained (carries user claims)
- Works across services
- Easy to scale horizontally

**Cons:**
- Can't revoke before expiration (use short TTLs + refresh tokens)
- Token size larger than session IDs
- Sensitive to XSS (store securely)

---

### JWT Authentication Flow

**1. Login Request**

```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "********"
}
```

**2. Login Response**

```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "accessToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refreshToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "expiresIn": 3600,
  "tokenType": "Bearer"
}
```

**3. Authenticated Request**

```http
GET /api/v1/users/me
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**4. Refresh Token Flow**

```http
POST /api/v1/auth/refresh
Content-Type: application/json

{
  "refreshToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response:**
```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "accessToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "expiresIn": 3600
}
```

---

### JWT Structure

**Header:**
```json
{
  "alg": "HS256",
  "typ": "JWT"
}
```

**Payload (Claims):**
```json
{
  "sub": "user-123",
  "email": "user@example.com",
  "role": "admin",
  "iat": 1640000000,
  "exp": 1640003600
}
```

**Signature:**
```
HMACSHA256(
  base64UrlEncode(header) + "." + base64UrlEncode(payload),
  secret
)
```

---

### JWT Best Practices

**1. Short Access Token TTL**
```
Access Token: 15-60 minutes
Refresh Token: 7-30 days
```

**2. Refresh Token Rotation**

Each refresh returns a NEW refresh token, invalidating the old one:

```python
# On refresh
new_access_token = generate_access_token(user)
new_refresh_token = generate_refresh_token(user)

# Invalidate old refresh token
db.delete_refresh_token(old_refresh_token)
db.save_refresh_token(new_refresh_token, user_id)

return {
    "accessToken": new_access_token,
    "refreshToken": new_refresh_token
}
```

**3. Store Refresh Tokens Securely**

- Database: Store hashed refresh tokens
- HttpOnly cookies (for web apps): Prevent XSS
- Secure storage (for mobile apps): Keychain/Keystore

**4. Include Essential Claims Only**

```json
{
  "sub": "user-123",
  "role": "admin",
  "iat": 1640000000,
  "exp": 1640003600
}
```

Don't include sensitive data (passwords, credit cards) in JWTs.

---

### Strategy 2: OAuth2 Authorization Code Flow

**Best for:** Third-party integrations, social login (Google, GitHub)

**Pros:**
- Industry standard
- Delegated authorization
- Scoped permissions
- Supports single sign-on

**Cons:**
- More complex than JWT
- Requires redirect flow
- Not suitable for server-to-server

---

### OAuth2 Flow

**1. Redirect to Authorization Server**

```
GET https://auth.example.com/oauth/authorize
  ?response_type=code
  &client_id=YOUR_CLIENT_ID
  &redirect_uri=https://yourapp.com/callback
  &scope=read:users write:orders
  &state=random_state_token
```

**2. User Grants Permission → Redirect Back**

```
GET https://yourapp.com/callback
  ?code=AUTH_CODE_HERE
  &state=random_state_token
```

**3. Exchange Authorization Code for Token**

```http
POST https://auth.example.com/oauth/token
Content-Type: application/x-www-form-urlencoded

grant_type=authorization_code
&code=AUTH_CODE_HERE
&client_id=YOUR_CLIENT_ID
&client_secret=YOUR_CLIENT_SECRET
&redirect_uri=https://yourapp.com/callback
```

**Response:**
```json
{
  "access_token": "eyJhbGc...",
  "token_type": "Bearer",
  "expires_in": 3600,
  "refresh_token": "eyJhbGc...",
  "scope": "read:users write:orders"
}
```

**4. Use Access Token**

```http
GET /api/v1/users/me
Authorization: Bearer eyJhbGc...
```

---

### Strategy 3: API Key Authentication

**Best for:** Server-to-server APIs, webhooks, public APIs with rate limits

**Pros:**
- Simple to implement
- Easy to rotate
- Per-key rate limiting
- Good for service accounts

**Cons:**
- No user context
- Must be stored securely
- All-or-nothing permissions

---

### API Key Patterns

**1. Header-based (Recommended)**

```http
GET /api/v1/users
X-API-Key: sk_live_abc123def456
```

**2. Query Parameter (Less secure)**

```
GET /api/v1/users?api_key=sk_live_abc123def456
```

**3. Basic Auth**

```http
GET /api/v1/users
Authorization: Basic YXBpX2tleV9oZXJlOg==
```

Base64 encode: `api_key_here:`

---

### API Key Best Practices

**1. Prefix Keys by Environment**

```
sk_live_abc123def456    # Production
sk_test_abc123def456    # Testing
```

**2. Store Hashed Keys in Database**

```python
import hashlib

def hash_api_key(key: str) -> str:
    return hashlib.sha256(key.encode()).hexdigest()

# Save hashed version
db.save(hash_api_key(api_key))

# Validate
if hash_api_key(provided_key) == stored_hash:
    # Valid
```

**3. Allow Key Rotation**

```http
POST /api/v1/api-keys/rotate
Authorization: Bearer <user_token>

{
  "keyId": "key_123"
}
```

Response:
```json
{
  "newKey": "sk_live_xyz789uvw456",
  "oldKey": "sk_live_abc123def456",
  "expiresAt": "2025-02-01T00:00:00Z"
}
```

**4. Rate Limit Per Key**

```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 987
X-RateLimit-Reset: 1640000000
```

---

## Authorization Patterns

### Pattern 1: RBAC (Role-Based Access Control)

**Best for:** Simple permission models, hierarchical roles

**Concept:** Users have roles; roles have permissions.

**Example Roles:**
- `guest` - Read public content
- `user` - Read/write own content
- `moderator` - Moderate content
- `admin` - Full access

**Implementation:**

```python
def require_role(required_role: str):
    def decorator(func):
        async def wrapper(request, *args, **kwargs):
            user = request.state.user
            if user.role != required_role and user.role != 'admin':
                raise HTTPException(403, "Insufficient permissions")
            return await func(request, *args, **kwargs)
        return wrapper
    return decorator

@app.delete("/api/v1/users/:id")
@require_role("admin")
async def delete_user(request, user_id):
    # Only admins can delete users
    pass
```

---

### Pattern 2: ABAC (Attribute-Based Access Control)

**Best for:** Complex policies based on attributes (department, location, time)

**Concept:** Policies evaluate attributes of user, resource, and environment.

**Example Policy:**

```python
def can_access_order(user, order):
    # Users can access their own orders
    if order.user_id == user.id:
        return True

    # Managers can access orders in their department
    if user.role == 'manager' and order.department == user.department:
        return True

    # Admins can access all orders
    if user.role == 'admin':
        return True

    return False
```

**Usage:**

```python
@app.get("/api/v1/orders/:id")
async def get_order(request, order_id):
    user = request.state.user
    order = await db.get_order(order_id)

    if not can_access_order(user, order):
        raise HTTPException(403, "Access denied")

    return order
```

---

### Pattern 3: Resource-Based Authorization

**Best for:** User-owned resources (posts, profiles, files)

**Concept:** Users can only modify resources they own.

**Implementation:**

```python
@app.patch("/api/v1/posts/:id")
async def update_post(request, post_id):
    user = request.state.user
    post = await db.get_post(post_id)

    if post.author_id != user.id and user.role != 'admin':
        raise HTTPException(403, "You can only edit your own posts")

    # Update post
    pass
```

---

## Security Best Practices Checklist

### HTTPS & Transport Security

- [ ] **HTTPS enforced** for all endpoints (redirect HTTP → HTTPS)
- [ ] **TLS 1.3** or TLS 1.2 minimum
- [ ] **HSTS header** (`Strict-Transport-Security: max-age=31536000`)
- [ ] **Secure cookies** (`Secure; HttpOnly; SameSite=Strict`)

### Token Security

- [ ] **Access tokens expire** (15-60 minutes)
- [ ] **Refresh tokens expire** (7-30 days)
- [ ] **Refresh token rotation** (invalidate old on refresh)
- [ ] **Tokens stored securely** (HttpOnly cookies or secure storage)
- [ ] **JWTs signed** with strong secret (HS256 or RS256)
- [ ] **Token blacklist** for logout (if needed)

### API Key Security

- [ ] **Keys hashed in database** (SHA-256 or bcrypt)
- [ ] **Keys rotatable** by users
- [ ] **Keys prefixed** by environment (`sk_live_`, `sk_test_`)
- [ ] **Rate limiting per key**
- [ ] **Keys revocable** immediately

### Authorization Security

- [ ] **Authorize on every endpoint** (never trust client)
- [ ] **Check resource ownership** before mutations
- [ ] **Role/permission checks** before sensitive operations
- [ ] **Fail securely** (deny by default)
- [ ] **Log access attempts** (successful and failed)

### Password Security

- [ ] **Hash passwords** with bcrypt, scrypt, or Argon2
- [ ] **Enforce password complexity** (min 8 chars, uppercase, numbers)
- [ ] **Rate limit login attempts** (prevent brute force)
- [ ] **Account lockout** after N failed attempts
- [ ] **Password reset flow** with time-limited tokens

---

## Common Anti-Patterns

### BAD: Storing Passwords in Plain Text

```python
# Bad
user.password = "plaintext_password"
```

```python
# Good
from passlib.hash import bcrypt

user.password_hash = bcrypt.hash("plaintext_password")

# Verify
if bcrypt.verify(provided_password, user.password_hash):
    # Valid
```

---

### BAD: Long-Lived Access Tokens

```json
{
  "accessToken": "...",
  "expiresIn": 2592000  # 30 days - TOO LONG
}
```

**Fix:** Use short-lived access tokens + refresh tokens.

---

### BAD: No HTTPS

```
http://api.example.com/login  # Credentials sent in clear text
```

**Fix:** Always use HTTPS.

---

### BAD: Trusting Client-Side Authorization

```javascript
// Bad - Client decides if user is admin
if (user.role === 'admin') {
  // Show admin panel
}
```

**Fix:** Always authorize on server:

```python
@app.delete("/api/v1/users/:id")
async def delete_user(request, user_id):
    user = request.state.user
    if user.role != 'admin':
        raise HTTPException(403, "Admin only")
    # Delete user
```

---

## Implementation Examples

### FastAPI (Python) - JWT Auth

```python
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from passlib.hash import bcrypt
from datetime import datetime, timedelta

SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

security = HTTPBearer()

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(401, "Invalid token")
        user = await db.get_user(user_id)
        return user
    except JWTError:
        raise HTTPException(401, "Invalid token")

@app.post("/api/v1/auth/login")
async def login(email: str, password: str):
    user = await db.get_user_by_email(email)
    if not user or not bcrypt.verify(password, user.password_hash):
        raise HTTPException(401, "Invalid credentials")

    access_token = create_access_token({"sub": user.id, "role": user.role})
    return {"accessToken": access_token, "expiresIn": ACCESS_TOKEN_EXPIRE_MINUTES * 60}

@app.get("/api/v1/users/me")
async def get_me(user = Depends(get_current_user)):
    return user
```

---

### Express.js (TypeScript) - JWT Auth

```typescript
import express from 'express';
import jwt from 'jsonwebtoken';
import bcrypt from 'bcrypt';

const SECRET_KEY = 'your-secret-key';
const ACCESS_TOKEN_EXPIRE = '30m';

const createAccessToken = (userId: string, role: string) => {
  return jwt.sign({ sub: userId, role }, SECRET_KEY, { expiresIn: ACCESS_TOKEN_EXPIRE });
};

const authenticate = (req, res, next) => {
  const authHeader = req.headers.authorization;
  if (!authHeader || !authHeader.startsWith('Bearer ')) {
    return res.status(401).json({ error: 'Missing or invalid token' });
  }

  const token = authHeader.substring(7);
  try {
    const payload = jwt.verify(token, SECRET_KEY);
    req.user = payload;
    next();
  } catch (err) {
    return res.status(401).json({ error: 'Invalid token' });
  }
};

app.post('/api/v1/auth/login', async (req, res) => {
  const { email, password } = req.body;
  const user = await db.getUserByEmail(email);

  if (!user || !(await bcrypt.compare(password, user.passwordHash))) {
    return res.status(401).json({ error: 'Invalid credentials' });
  }

  const accessToken = createAccessToken(user.id, user.role);
  res.json({ accessToken, expiresIn: 1800 });
});

app.get('/api/v1/users/me', authenticate, (req, res) => {
  res.json(req.user);
});
```

---

## Related Resources

- **[api-security-checklist.md](api-security-checklist.md)** - Comprehensive security checklist
- **[error-handling-patterns.md](error-handling-patterns.md)** - 401/403 error responses
- **[rate-limiting-patterns.md](rate-limiting-patterns.md)** - Rate limiting per user/key
- **[restful-design-patterns.md](restful-design-patterns.md)** - HTTP status codes
- **[openapi-guide.md](openapi-guide.md)** - Documenting security schemes
