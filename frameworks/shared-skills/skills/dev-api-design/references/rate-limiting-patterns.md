# Rate Limiting & Throttling Patterns

This guide provides production-ready patterns for implementing rate limiting and throttling to protect APIs from abuse and ensure fair usage.

---

## Why Rate Limiting?

**Goals:**
- Prevent abuse and DDoS attacks
- Ensure fair resource allocation
- Protect backend services from overload
- Monetize API access (tiered pricing)
- Comply with SLAs

---

## Rate Limiting Algorithms

### Algorithm 1: Token Bucket (Recommended)

**Best for:** Most use cases, allows bursts

**How it works:**
- Bucket holds N tokens
- Each request consumes 1 token
- Tokens refill at fixed rate R per second
- Request allowed if tokens available

**Characteristics:**
- [OK] Allows traffic bursts (within bucket size)
- [OK] Smooth rate limiting
- [OK] Simple to implement

**Example:**
```
Bucket size: 100 tokens
Refill rate: 10 tokens/second

User makes 50 requests instantly → Allowed (50 tokens consumed)
User makes 60 more requests instantly → 10 allowed, 50 rejected (bucket empty)
After 5 seconds → 50 tokens refilled
```

---

### Algorithm 2: Fixed Window

**Best for:** Simple rate limits, less precise

**How it works:**
- Count requests in fixed time window (e.g., per minute)
- Reset counter at window boundary

**Characteristics:**
- [OK] Simple to implement
- [FAIL] Boundary issue: 2x limit at window edge
- [FAIL] Bursty traffic spikes

**Example:**
```
Limit: 100 requests/minute
Window: 12:00:00 - 12:01:00

At 12:00:50 → User sends 100 requests (allowed)
At 12:01:01 → Counter resets, user sends 100 more requests (allowed)
Total in 11 seconds: 200 requests (exceeds spirit of limit)
```

---

### Algorithm 3: Sliding Window

**Best for:** More accurate rate limiting, prevents boundary issues

**How it works:**
- Track requests with timestamps
- Count requests in rolling window (last N seconds)

**Characteristics:**
- [OK] No boundary issues
- [OK] Accurate rate limiting
- [FAIL] More memory (store timestamps)

**Example:**
```
Limit: 100 requests/minute
Current time: 12:01:30

Count requests from 12:00:30 to 12:01:30
If count < 100 → Allow
Else → Reject
```

---

### Algorithm 4: Leaky Bucket

**Best for:** Smoothing bursty traffic, message queues

**How it works:**
- Requests added to queue (bucket)
- Processed at fixed rate (leak rate)
- Queue overflow = reject

**Characteristics:**
- [OK] Smooth output rate
- [FAIL] Adds latency (queuing)
- Best for background jobs, not synchronous APIs

---

## Rate Limit Headers

**Standard headers** (de facto standard):

```http
X-RateLimit-Limit: 1000        # Max requests per window
X-RateLimit-Remaining: 987     # Requests left in current window
X-RateLimit-Reset: 1640000000  # Unix timestamp when window resets
```

**When limit exceeded:**

```http
HTTP/1.1 429 Too Many Requests
Retry-After: 60                 # Seconds until retry
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1640000060

{
  "type": "https://api.example.com/errors/rate-limit-exceeded",
  "title": "Too Many Requests",
  "status": 429,
  "detail": "Rate limit exceeded. Try again in 60 seconds.",
  "retryAfter": 60
}
```

---

## Tiered Rate Limits

**Use when:** Monetizing API access or different user types.

**Example tiers:**

```
Free tier:        100 requests/hour
Paid tier:      1,000 requests/hour
Premium tier:  10,000 requests/hour
Enterprise:    No limit (or very high)
```

**Implementation:**

```python
RATE_LIMITS = {
    "free": {"limit": 100, "window": 3600},      # 100/hour
    "paid": {"limit": 1000, "window": 3600},     # 1000/hour
    "premium": {"limit": 10000, "window": 3600}, # 10000/hour
    "enterprise": None  # No limit
}

def get_rate_limit(user):
    tier = user.subscription_tier
    return RATE_LIMITS.get(tier, RATE_LIMITS["free"])
```

---

## Implementation Examples

### Redis + Token Bucket

**Why Redis?**
- Fast in-memory storage
- Built-in TTL (automatic cleanup)
- Atomic operations
- Distributed (works across servers)

**Implementation (Python + FastAPI):**

```python
import redis
import time
from fastapi import FastAPI, HTTPException, Request

redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)

def check_rate_limit(key: str, limit: int, window: int) -> tuple[bool, dict]:
    """
    Token bucket rate limiting using Redis.

    Args:
        key: Unique identifier (e.g., user_id or api_key)
        limit: Max requests per window
        window: Time window in seconds

    Returns:
        (allowed, headers) tuple
    """
    now = time.time()
    bucket_key = f"rate_limit:{key}"

    # Get current bucket state
    bucket = redis_client.get(bucket_key)

    if bucket is None:
        # First request - initialize bucket
        tokens = limit - 1
        redis_client.setex(bucket_key, window, tokens)
        reset_time = int(now + window)
    else:
        tokens = int(bucket)
        ttl = redis_client.ttl(bucket_key)
        reset_time = int(now + ttl)

        if tokens > 0:
            # Consume token
            redis_client.decr(bucket_key)
            tokens -= 1
        else:
            # No tokens left
            headers = {
                "X-RateLimit-Limit": str(limit),
                "X-RateLimit-Remaining": "0",
                "X-RateLimit-Reset": str(reset_time),
                "Retry-After": str(ttl)
            }
            return False, headers

    headers = {
        "X-RateLimit-Limit": str(limit),
        "X-RateLimit-Remaining": str(tokens),
        "X-RateLimit-Reset": str(reset_time)
    }
    return True, headers

@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    # Get user or API key
    user_id = request.state.user.id if hasattr(request.state, 'user') else None
    api_key = request.headers.get("X-API-Key")

    key = user_id or api_key or request.client.host

    # Get tier-specific limits
    limit = 100  # requests per hour
    window = 3600  # 1 hour

    allowed, headers = check_rate_limit(key, limit, window)

    if not allowed:
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded",
            headers=headers
        )

    response = await call_next(request)

    # Add rate limit headers to response
    for header, value in headers.items():
        response.headers[header] = value

    return response
```

---

### Redis + Sliding Window Log

**Implementation (Python):**

```python
import redis
import time

redis_client = redis.Redis(host='localhost', port=6379)

def check_rate_limit_sliding_window(key: str, limit: int, window: int) -> bool:
    """
    Sliding window log using Redis sorted sets.

    Args:
        key: Unique identifier
        limit: Max requests per window
        window: Time window in seconds
    """
    now = time.time()
    window_start = now - window
    bucket_key = f"rate_limit:{key}"

    # Remove old requests outside window
    redis_client.zremrangebyscore(bucket_key, 0, window_start)

    # Count requests in window
    request_count = redis_client.zcard(bucket_key)

    if request_count >= limit:
        return False

    # Add current request
    redis_client.zadd(bucket_key, {str(now): now})
    redis_client.expire(bucket_key, window)

    return True
```

---

### Express.js + express-rate-limit

**Installation:**
```bash
npm install express-rate-limit redis
```

**Implementation (TypeScript):**

```typescript
import express from 'express';
import rateLimit from 'express-rate-limit';
import RedisStore from 'rate-limit-redis';
import { createClient } from 'redis';

const redisClient = createClient({ url: 'redis://localhost:6379' });
await redisClient.connect();

// Create rate limiter
const limiter = rateLimit({
  store: new RedisStore({
    client: redisClient,
    prefix: 'rate_limit:',
  }),
  windowMs: 60 * 60 * 1000, // 1 hour
  max: 100, // 100 requests per hour
  message: {
    type: 'https://api.example.com/errors/rate-limit-exceeded',
    title: 'Too Many Requests',
    status: 429,
    detail: 'Rate limit exceeded. Try again later.',
  },
  standardHeaders: true, // Return rate limit info in headers
  legacyHeaders: false,
  handler: (req, res) => {
    res.status(429).json({
      type: 'https://api.example.com/errors/rate-limit-exceeded',
      title: 'Too Many Requests',
      status: 429,
      detail: 'Rate limit exceeded. Try again later.',
      retryAfter: Math.ceil(req.rateLimit.resetTime / 1000),
    });
  },
});

// Apply globally
app.use('/api/', limiter);

// Per-route limits
const strictLimiter = rateLimit({
  store: new RedisStore({ client: redisClient }),
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 10, // 10 requests per 15 minutes
});

app.post('/api/v1/auth/login', strictLimiter, (req, res) => {
  // Login endpoint with stricter limit
});
```

---

## Per-Endpoint Rate Limits

**Use when:** Different endpoints have different usage patterns.

**Example:**

```python
ENDPOINT_LIMITS = {
    "POST /api/v1/auth/login": {"limit": 5, "window": 900},       # 5/15min
    "POST /api/v1/users": {"limit": 10, "window": 3600},          # 10/hour
    "GET /api/v1/users": {"limit": 1000, "window": 3600},         # 1000/hour
    "DELETE /api/v1/users/:id": {"limit": 10, "window": 3600},    # 10/hour
}

@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    endpoint = f"{request.method} {request.url.path}"
    limits = ENDPOINT_LIMITS.get(endpoint, {"limit": 100, "window": 3600})

    allowed, headers = check_rate_limit(
        key=f"{request.state.user.id}:{endpoint}",
        limit=limits["limit"],
        window=limits["window"]
    )

    if not allowed:
        raise HTTPException(429, "Rate limit exceeded", headers=headers)

    response = await call_next(request)
    for header, value in headers.items():
        response.headers[header] = value
    return response
```

---

## Rate Limiting Strategies

### Per User/API Key

```python
key = f"user:{user.id}"
# or
key = f"api_key:{api_key}"
```

**Best for:** Authenticated APIs, per-account limits.

---

### Per IP Address

```python
key = f"ip:{request.client.host}"
```

**Best for:** Public APIs, preventing DDoS.

**Warning:** Multiple users behind NAT share same IP.

---

### Per User + Endpoint

```python
key = f"user:{user.id}:endpoint:{endpoint}"
```

**Best for:** Granular control, sensitive endpoints.

---

## Best Practices Checklist

- [ ] **Rate limits documented** (in API docs, terms of service)
- [ ] **Rate limit headers included** (`X-RateLimit-*`)
- [ ] **429 status code** for violations
- [ ] **Retry-After header** provided
- [ ] **Per-user or per-API-key limits** (not just per-IP)
- [ ] **Burst allowance** for spiky traffic (use token bucket)
- [ ] **Tiered limits** for different subscription levels
- [ ] **Graceful degradation** (queue or throttle instead of hard reject)
- [ ] **Monitoring & alerting** on rate limit violations
- [ ] **Redis for distributed rate limiting** (if multi-server)

---

## Common Anti-Patterns

### BAD: No Rate Limiting

```
# Bad - No protection against abuse
GET /api/v1/users
```

**Fix:** Always implement rate limiting.

---

### BAD: Per-IP Only (Not Per-User)

```python
# Bad - Users behind NAT blocked together
key = f"ip:{request.client.host}"
```

**Fix:** Use per-user or per-API-key limits:

```python
key = f"user:{user.id}"
```

---

### BAD: Missing Retry-After Header

```http
HTTP/1.1 429 Too Many Requests

{
  "error": "Rate limit exceeded"
}
```

**Fix:** Include Retry-After:

```http
HTTP/1.1 429 Too Many Requests
Retry-After: 60
```

---

### BAD: No Burst Allowance

Using fixed window with no burst allowance punishes legitimate spiky traffic.

**Fix:** Use token bucket algorithm.

---

## Advanced Patterns

### Adaptive Rate Limiting

Adjust limits based on system load:

```python
def get_dynamic_limit():
    cpu_usage = get_cpu_usage()
    if cpu_usage > 80:
        return 50  # Reduce limit under load
    elif cpu_usage < 50:
        return 200  # Increase limit when idle
    else:
        return 100  # Normal limit
```

---

### Rate Limit Bypass for Trusted Clients

```python
TRUSTED_IPS = ["10.0.0.0/8", "192.168.0.0/16"]

if request.client.host in TRUSTED_IPS:
    # Skip rate limiting
    pass
```

---

### Cost-Based Rate Limiting

Different endpoints consume different "costs":

```python
ENDPOINT_COSTS = {
    "GET /api/v1/users": 1,           # Cheap
    "POST /api/v1/users": 5,          # Moderate
    "POST /api/v1/reports/generate": 50  # Expensive
}

# Consume tokens based on cost
cost = ENDPOINT_COSTS.get(endpoint, 1)
check_rate_limit(key, limit, window, cost)
```

---

## Monitoring & Observability

**Metrics to track:**

- **Rate limit violations** (by user, endpoint)
- **95th percentile usage** (approaching limits?)
- **Burst patterns** (legitimate or abuse?)
- **Endpoint popularity** (adjust limits accordingly)

**Example metrics:**

```python
from prometheus_client import Counter, Histogram

rate_limit_violations = Counter(
    'api_rate_limit_violations_total',
    'Total rate limit violations',
    ['user_id', 'endpoint']
)

rate_limit_usage = Histogram(
    'api_rate_limit_usage_percent',
    'Rate limit usage percentage',
    ['user_id', 'tier']
)
```

---

## Decision Matrix

| Use Case | Algorithm | Storage |
|----------|-----------|---------|
| Simple API, single server | Fixed Window | In-memory |
| Distributed API, multiple servers | Token Bucket | Redis |
| Prevent abuse, allow bursts | Token Bucket | Redis |
| Accurate rate limiting | Sliding Window | Redis |
| Background jobs, queuing | Leaky Bucket | Redis |
| High-traffic API | Token Bucket | Redis Cluster |

---

## Related Resources

- **[authentication-patterns.md](authentication-patterns.md)** - Rate limiting per API key/user
- **[error-handling-patterns.md](error-handling-patterns.md)** - 429 error responses
- **[api-security-checklist.md](api-security-checklist.md)** - Security best practices
- **[restful-design-patterns.md](restful-design-patterns.md)** - HTTP status codes
- **[openapi-guide.md](openapi-guide.md)** - Documenting rate limits
