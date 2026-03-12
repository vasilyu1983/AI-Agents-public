# Resilience Utilities

Centralized patterns for retry, circuit breaker, timeout, rate limiting, and observability.

**Updated**: December 2025
**Node.js**: 24 LTS | **Python**: 3.14+ | **Go**: 1.25+

---

## File Structure

```
src/
└── utils/
    └── resilience.ts    # All resilience utilities
```

---

## TypeScript/Node.js

### Dependencies

```bash
npm install p-retry@^6 opossum@^8 @opentelemetry/api@^1.9
```

### Complete Resilience Module (`src/utils/resilience.ts`)

```typescript
import pRetry, { AbortError } from 'p-retry';
import CircuitBreaker from 'opossum';
import { trace, SpanStatusCode, context, propagation } from '@opentelemetry/api';
import { logger } from '@/utils/logger';

const tracer = trace.getTracer('resilience');

// ============================================
// RETRY WITH EXPONENTIAL BACKOFF (p-retry v6)
// ============================================

export interface RetryOptions {
  retries?: number;
  minTimeout?: number;
  maxTimeout?: number;
  factor?: number;
  onRetry?: (error: Error, attempt: number) => void;
  signal?: AbortSignal;  // p-retry v6: AbortController support
}

const defaultRetryOptions: Required<Omit<RetryOptions, 'onRetry' | 'signal'>> = {
  retries: 3,
  minTimeout: 1000,
  maxTimeout: 30000,
  factor: 2,
};

export const withRetry = async <T>(
  fn: (attemptCount: number) => Promise<T>,  // p-retry v6: attempt count passed
  options: RetryOptions = {}
): Promise<T> => {
  const opts = { ...defaultRetryOptions, ...options };

  return tracer.startActiveSpan('retry', async (span) => {
    try {
      const result = await pRetry(fn, {
        retries: opts.retries,
        minTimeout: opts.minTimeout,
        maxTimeout: opts.maxTimeout,
        factor: opts.factor,
        randomize: true,
        signal: opts.signal,
        onFailedAttempt: (error) => {
          span.addEvent('retry_attempt', {
            attempt: error.attemptNumber,
            retriesLeft: error.retriesLeft,
            error: error.message,
          });

          logger.warn({
            attempt: error.attemptNumber,
            retriesLeft: error.retriesLeft,
            error: error.message,
          }, 'Retry attempt failed');

          options.onRetry?.(error, error.attemptNumber);
        },
      });

      span.setStatus({ code: SpanStatusCode.OK });
      return result;
    } catch (error) {
      span.setStatus({ code: SpanStatusCode.ERROR, message: String(error) });
      throw error;
    } finally {
      span.end();
    }
  });
};

// Abort retry on non-retryable errors
export const abortRetry = (error: Error): never => {
  throw new AbortError(error.message);
};

// ============================================
// CIRCUIT BREAKER (opossum v8 + OpenTelemetry)
// ============================================

export interface CircuitBreakerOptions {
  timeout?: number;           // Request timeout in ms
  errorThreshold?: number;    // % of failures to open circuit
  resetTimeout?: number;      // Time before half-open (ms)
  volumeThreshold?: number;   // Min requests before opening
}

const defaultBreakerOptions: Required<CircuitBreakerOptions> = {
  timeout: 3000,
  errorThreshold: 50,
  resetTimeout: 30000,
  volumeThreshold: 10,
};

export const createCircuitBreaker = <T extends (...args: any[]) => Promise<any>>(
  fn: T,
  name: string,
  options: CircuitBreakerOptions = {}
): CircuitBreaker<Parameters<T>, Awaited<ReturnType<T>>> => {
  const opts = { ...defaultBreakerOptions, ...options };

  // Wrap function with OpenTelemetry span
  const wrappedFn = async (...args: Parameters<T>): Promise<Awaited<ReturnType<T>>> => {
    return tracer.startActiveSpan(`circuit_breaker.${name}`, async (span) => {
      try {
        const result = await fn(...args);
        span.setStatus({ code: SpanStatusCode.OK });
        return result;
      } catch (error) {
        span.setStatus({ code: SpanStatusCode.ERROR, message: String(error) });
        throw error;
      } finally {
        span.end();
      }
    });
  };

  const breaker = new CircuitBreaker(wrappedFn, {
    timeout: opts.timeout,
    errorThresholdPercentage: opts.errorThreshold,
    resetTimeout: opts.resetTimeout,
    volumeThreshold: opts.volumeThreshold,
    name,
  });

  // Logging with OpenTelemetry events
  breaker.on('open', () => {
    const span = trace.getActiveSpan();
    span?.addEvent('circuit_opened', { circuit: name });
    logger.warn({ circuit: name }, 'Circuit breaker opened');
  });

  breaker.on('halfOpen', () => {
    const span = trace.getActiveSpan();
    span?.addEvent('circuit_half_open', { circuit: name });
    logger.info({ circuit: name }, 'Circuit breaker half-open');
  });

  breaker.on('close', () => {
    const span = trace.getActiveSpan();
    span?.addEvent('circuit_closed', { circuit: name });
    logger.info({ circuit: name }, 'Circuit breaker closed');
  });

  breaker.on('fallback', () => {
    const span = trace.getActiveSpan();
    span?.addEvent('circuit_fallback', { circuit: name });
    logger.warn({ circuit: name }, 'Circuit breaker fallback triggered');
  });

  return breaker;
};

// ============================================
// TIMEOUT WRAPPER
// ============================================

export class TimeoutError extends Error {
  constructor(ms: number) {
    super(`Operation timed out after ${ms}ms`);
    this.name = 'TimeoutError';
  }
}

export const withTimeout = <T>(
  promise: Promise<T>,
  ms: number,
  signal?: AbortSignal
): Promise<T> => {
  return tracer.startActiveSpan('timeout', async (span) => {
    span.setAttribute('timeout_ms', ms);

    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), ms);

    // Link to external abort signal if provided
    signal?.addEventListener('abort', () => controller.abort());

    try {
      const result = await Promise.race([
        promise,
        new Promise<never>((_, reject) => {
          controller.signal.addEventListener('abort', () => {
            reject(new TimeoutError(ms));
          });
        }),
      ]);

      span.setStatus({ code: SpanStatusCode.OK });
      return result;
    } catch (error) {
      if (error instanceof TimeoutError) {
        span.setStatus({ code: SpanStatusCode.ERROR, message: 'timeout' });
      }
      throw error;
    } finally {
      clearTimeout(timeoutId);
      span.end();
    }
  });
};

// ============================================
// RATE LIMITER (Token Bucket with Sliding Window)
// ============================================

export interface RateLimiterOptions {
  windowMs: number;
  maxRequests: number;
}

export class RateLimiter {
  private requests: Map<string, number[]> = new Map();
  private readonly windowMs: number;
  private readonly maxRequests: number;

  constructor(options: RateLimiterOptions) {
    this.windowMs = options.windowMs;
    this.maxRequests = options.maxRequests;
  }

  isAllowed(key: string): boolean {
    const now = Date.now();
    const windowStart = now - this.windowMs;

    // Get existing timestamps for this key
    let timestamps = this.requests.get(key) || [];

    // Filter to only include timestamps within the window
    timestamps = timestamps.filter((ts) => ts > windowStart);

    // Check if under limit
    if (timestamps.length >= this.maxRequests) {
      return false;
    }

    // Add current request
    timestamps.push(now);
    this.requests.set(key, timestamps);

    return true;
  }

  getRemainingRequests(key: string): number {
    const now = Date.now();
    const windowStart = now - this.windowMs;
    const timestamps = this.requests.get(key) || [];
    const validTimestamps = timestamps.filter((ts) => ts > windowStart);
    return Math.max(0, this.maxRequests - validTimestamps.length);
  }

  getResetTime(key: string): number {
    const timestamps = this.requests.get(key) || [];
    if (timestamps.length === 0) return 0;
    const oldest = Math.min(...timestamps);
    return oldest + this.windowMs;
  }
}

// ============================================
// BULKHEAD (Concurrency Limiter)
// ============================================

export class Bulkhead {
  private running = 0;
  private queue: Array<() => void> = [];
  private readonly name: string;

  constructor(
    private readonly maxConcurrent: number,
    name = 'default'
  ) {
    this.name = name;
  }

  async execute<T>(fn: () => Promise<T>): Promise<T> {
    return tracer.startActiveSpan(`bulkhead.${this.name}`, async (span) => {
      span.setAttribute('max_concurrent', this.maxConcurrent);
      span.setAttribute('current_running', this.running);
      span.setAttribute('queue_size', this.queue.length);

      await this.acquire();
      try {
        const result = await fn();
        span.setStatus({ code: SpanStatusCode.OK });
        return result;
      } catch (error) {
        span.setStatus({ code: SpanStatusCode.ERROR, message: String(error) });
        throw error;
      } finally {
        this.release();
        span.end();
      }
    });
  }

  private acquire(): Promise<void> {
    if (this.running < this.maxConcurrent) {
      this.running++;
      return Promise.resolve();
    }

    return new Promise((resolve) => {
      this.queue.push(() => {
        this.running++;
        resolve();
      });
    });
  }

  private release(): void {
    this.running--;
    const next = this.queue.shift();
    if (next) next();
  }

  get stats() {
    return {
      running: this.running,
      queued: this.queue.length,
      available: this.maxConcurrent - this.running,
    };
  }
}

// ============================================
// HEDGED REQUESTS (Parallel with First Response)
// ============================================

export const withHedging = async <T>(
  fn: () => Promise<T>,
  hedgeDelayMs: number,
  maxHedges = 2
): Promise<T> => {
  return tracer.startActiveSpan('hedged_request', async (span) => {
    span.setAttribute('hedge_delay_ms', hedgeDelayMs);
    span.setAttribute('max_hedges', maxHedges);

    const controller = new AbortController();
    const promises: Promise<T>[] = [];

    // Primary request
    promises.push(fn());

    // Schedule hedged requests
    for (let i = 1; i < maxHedges; i++) {
      promises.push(
        new Promise((resolve, reject) => {
          const timeoutId = setTimeout(async () => {
            if (controller.signal.aborted) return;
            try {
              span.addEvent('hedge_started', { hedge_number: i });
              resolve(await fn());
            } catch (error) {
              reject(error);
            }
          }, hedgeDelayMs * i);

          controller.signal.addEventListener('abort', () => {
            clearTimeout(timeoutId);
          });
        })
      );
    }

    try {
      const result = await Promise.race(promises);
      controller.abort(); // Cancel pending hedges
      span.setStatus({ code: SpanStatusCode.OK });
      return result;
    } catch (error) {
      span.setStatus({ code: SpanStatusCode.ERROR, message: String(error) });
      throw error;
    } finally {
      span.end();
    }
  });
};
```

---

## Usage Examples

### Retry with AbortController (p-retry v6)

```typescript
import { withRetry, abortRetry } from '@/utils/resilience';

// With AbortController (new in p-retry v6)
const controller = new AbortController();
setTimeout(() => controller.abort(), 10000); // Cancel after 10s

const data = await withRetry(
  async (attemptCount) => {
    console.log(`Attempt ${attemptCount}`);
    const response = await fetch('/api/data');

    if (response.status === 429) {
      abortRetry(new Error('Rate limited'));  // Don't retry
    }
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);  // Will retry
    }

    return response.json();
  },
  { retries: 5, minTimeout: 2000, signal: controller.signal }
);
```

### Circuit Breaker with Fallback

```typescript
import { createCircuitBreaker } from '@/utils/resilience';

const paymentAPI = async (data: PaymentData) => {
  const response = await fetch('https://payments.example.com/charge', {
    method: 'POST',
    body: JSON.stringify(data),
  });
  if (!response.ok) throw new Error('Payment failed');
  return response.json();
};

const paymentBreaker = createCircuitBreaker(paymentAPI, 'payment-api', {
  timeout: 5000,
  errorThreshold: 30,
  resetTimeout: 60000,
});

// With fallback
paymentBreaker.fallback(async (data: PaymentData) => {
  await queuePaymentForLater(data);
  return { status: 'queued', message: 'Payment queued for processing' };
});

// Use
const result = await paymentBreaker.fire(paymentData);
```

### Timeout with Abort Signal

```typescript
import { withTimeout, TimeoutError } from '@/utils/resilience';

try {
  const data = await withTimeout(
    fetch('/api/slow-endpoint').then((r) => r.json()),
    5000  // 5 second timeout
  );
} catch (error) {
  if (error instanceof TimeoutError) {
    console.log('Request timed out');
  }
}
```

### Rate Limiter Middleware

```typescript
import { RateLimiter } from '@/utils/resilience';

const limiter = new RateLimiter({
  windowMs: 60000,   // 1 minute
  maxRequests: 100,  // 100 requests per minute
});

// Express middleware
app.use((req, res, next) => {
  const key = req.ip;

  if (!limiter.isAllowed(key)) {
    res.setHeader('X-RateLimit-Reset', limiter.getResetTime(key));
    return res.status(429).json({ error: 'Too many requests' });
  }

  res.setHeader('X-RateLimit-Remaining', limiter.getRemainingRequests(key));
  next();
});
```

### Bulkhead for Database Operations

```typescript
import { Bulkhead } from '@/utils/resilience';

// Limit to 5 concurrent database operations
const dbBulkhead = new Bulkhead(5, 'database');

// All calls go through bulkhead
const results = await Promise.all(
  userIds.map((id) =>
    dbBulkhead.execute(() => db.user.findUnique({ where: { id } }))
  )
);

// Check stats
console.log(dbBulkhead.stats);
// { running: 3, queued: 10, available: 2 }
```

### Hedged Requests for Latency-Sensitive Operations

```typescript
import { withHedging } from '@/utils/resilience';

// Send parallel requests, use first response
const data = await withHedging(
  () => fetch('/api/critical-data').then((r) => r.json()),
  100,  // Start hedge after 100ms
  3     // Max 3 parallel requests
);
```

---

## Python (tenacity 9.x)

### Dependencies

```bash
pip install tenacity>=9.0 pybreaker>=1.2 opentelemetry-api>=1.29
```

### Resilience Module (`src/utils/resilience.py`)

```python
import asyncio
from collections.abc import Callable
from functools import wraps
from typing import ParamSpec, TypeVar

import pybreaker
from opentelemetry import trace
from opentelemetry.trace import SpanKind, Status, StatusCode
from tenacity import (
    AsyncRetrying,
    RetryError,
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential_jitter,
)

from src.utils.logger import logger

T = TypeVar("T")
P = ParamSpec("P")

tracer = trace.get_tracer("resilience")


# ============================================
# RETRY WITH EXPONENTIAL BACKOFF (tenacity 9.x)
# ============================================


def with_retry(
    retries: int = 3,
    min_seconds: float = 1,
    max_seconds: float = 30,
    retry_exceptions: tuple[type[Exception], ...] = (Exception,),
):
    """Decorator for retry with exponential backoff and jitter (tenacity 9.x)."""

    def decorator(func: Callable[P, T]) -> Callable[P, T]:
        @wraps(func)
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            with tracer.start_as_current_span("retry", kind=SpanKind.INTERNAL) as span:
                try:
                    async for attempt in AsyncRetrying(
                        stop=stop_after_attempt(retries),
                        wait=wait_exponential_jitter(
                            initial=min_seconds,
                            max=max_seconds,
                            jitter=min_seconds,  # Add jitter
                        ),
                        retry=retry_if_exception_type(retry_exceptions),
                        reraise=True,
                    ):
                        with attempt:
                            span.add_event(
                                "retry_attempt",
                                {"attempt": attempt.retry_state.attempt_number},
                            )
                            result = await func(*args, **kwargs)
                            span.set_status(Status(StatusCode.OK))
                            return result
                except RetryError as e:
                    span.set_status(Status(StatusCode.ERROR, str(e)))
                    raise

        return wrapper

    return decorator


# ============================================
# CIRCUIT BREAKER (pybreaker with OTel)
# ============================================


class TracingCircuitBreakerListener(pybreaker.CircuitBreakerListener):
    """Listener that emits OpenTelemetry events."""

    def __init__(self, name: str):
        self.name = name

    def state_change(
        self, cb: pybreaker.CircuitBreaker, old_state: str, new_state: str
    ):
        span = trace.get_current_span()
        span.add_event(
            "circuit_state_change",
            {"circuit": self.name, "old_state": old_state, "new_state": new_state},
        )
        logger.info(f"Circuit {self.name}: {old_state} -> {new_state}")


def create_circuit_breaker(
    name: str,
    fail_max: int = 5,
    reset_timeout: int = 30,
) -> pybreaker.CircuitBreaker:
    """Create a circuit breaker with OpenTelemetry integration."""
    return pybreaker.CircuitBreaker(
        name=name,
        fail_max=fail_max,
        reset_timeout=reset_timeout,
        listeners=[TracingCircuitBreakerListener(name)],
    )


# ============================================
# TIMEOUT
# ============================================


class TimeoutError(Exception):
    pass


async def with_timeout(coro, seconds: float):
    """Run coroutine with timeout and OTel span."""
    with tracer.start_as_current_span("timeout", kind=SpanKind.INTERNAL) as span:
        span.set_attribute("timeout_seconds", seconds)
        try:
            result = await asyncio.wait_for(coro, timeout=seconds)
            span.set_status(Status(StatusCode.OK))
            return result
        except asyncio.TimeoutError:
            span.set_status(Status(StatusCode.ERROR, "timeout"))
            raise TimeoutError(f"Operation timed out after {seconds}s")


# ============================================
# BULKHEAD (Semaphore-based)
# ============================================


class Bulkhead:
    """Concurrency limiter using asyncio.Semaphore."""

    def __init__(self, max_concurrent: int, name: str = "default"):
        self._semaphore = asyncio.Semaphore(max_concurrent)
        self._max = max_concurrent
        self._name = name

    async def execute(self, coro):
        with tracer.start_as_current_span(
            f"bulkhead.{self._name}", kind=SpanKind.INTERNAL
        ) as span:
            span.set_attribute("max_concurrent", self._max)

            async with self._semaphore:
                try:
                    result = await coro
                    span.set_status(Status(StatusCode.OK))
                    return result
                except Exception as e:
                    span.set_status(Status(StatusCode.ERROR, str(e)))
                    raise
```

### Usage

```python
from src.utils.resilience import (
    with_retry,
    create_circuit_breaker,
    with_timeout,
    Bulkhead,
)


# Retry decorator
@with_retry(retries=3, min_seconds=1, max_seconds=10)
async def fetch_data(url: str) -> dict:
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        response.raise_for_status()
        return response.json()


# Circuit breaker
payment_breaker = create_circuit_breaker("payment-api", fail_max=5, reset_timeout=60)


@payment_breaker
async def process_payment(data: dict) -> dict:
    # Payment logic
    pass


# Timeout
result = await with_timeout(fetch_data("https://api.example.com"), seconds=5.0)


# Bulkhead
db_bulkhead = Bulkhead(max_concurrent=5, name="database")
results = await asyncio.gather(
    *[db_bulkhead.execute(db.get_user(id)) for id in user_ids]
)
```

---

## Go 1.25+

### Dependencies

```bash
go get github.com/cenkalti/backoff/v5
go get github.com/sony/gobreaker/v2
go get go.opentelemetry.io/otel
```

### Resilience Package (`internal/utils/resilience.go`)

```go
package utils

import (
	"context"
	"errors"
	"sync"
	"time"

	"github.com/cenkalti/backoff/v5"
	"github.com/sony/gobreaker/v2"
	"go.opentelemetry.io/otel"
	"go.opentelemetry.io/otel/attribute"
	"go.opentelemetry.io/otel/codes"
	"go.opentelemetry.io/otel/trace"
)

var tracer = otel.Tracer("resilience")

// ============================================
// RETRY WITH EXPONENTIAL BACKOFF
// ============================================

type RetryOptions struct {
	MaxAttempts     int
	InitialInterval time.Duration
	MaxInterval     time.Duration
	Multiplier      float64
}

func DefaultRetryOptions() RetryOptions {
	return RetryOptions{
		MaxAttempts:     3,
		InitialInterval: time.Second,
		MaxInterval:     30 * time.Second,
		Multiplier:      2.0,
	}
}

func WithRetry[T any](ctx context.Context, fn func() (T, error), opts RetryOptions) (T, error) {
	ctx, span := tracer.Start(ctx, "retry")
	defer span.End()

	var result T
	var attempt int

	b := backoff.NewExponentialBackOff(
		backoff.WithInitialInterval(opts.InitialInterval),
		backoff.WithMaxInterval(opts.MaxInterval),
		backoff.WithMultiplier(opts.Multiplier),
	)

	operation := func() (T, error) {
		attempt++
		span.AddEvent("retry_attempt", trace.WithAttributes(
			attribute.Int("attempt", attempt),
		))

		return fn()
	}

	result, err := backoff.RetryWithData(operation, backoff.WithContext(backoff.WithMaxRetries(b, uint64(opts.MaxAttempts-1)), ctx))
	if err != nil {
		span.SetStatus(codes.Error, err.Error())
		return result, err
	}

	span.SetStatus(codes.Ok, "")
	return result, nil
}

// ============================================
// CIRCUIT BREAKER (gobreaker v2)
// ============================================

type CircuitBreakerConfig struct {
	Name          string
	MaxRequests   uint32        // Max requests in half-open state
	Interval      time.Duration // Cyclic period for clearing counts
	Timeout       time.Duration // Period of open state
	ReadyToTrip   func(counts gobreaker.Counts) bool
}

func DefaultCircuitBreakerConfig(name string) CircuitBreakerConfig {
	return CircuitBreakerConfig{
		Name:        name,
		MaxRequests: 1,
		Interval:    0,
		Timeout:     30 * time.Second,
		ReadyToTrip: func(counts gobreaker.Counts) bool {
			failureRatio := float64(counts.TotalFailures) / float64(counts.Requests)
			return counts.Requests >= 10 && failureRatio >= 0.5
		},
	}
}

func NewCircuitBreaker[T any](cfg CircuitBreakerConfig) *gobreaker.CircuitBreaker[T] {
	return gobreaker.NewCircuitBreaker[T](gobreaker.Settings{
		Name:        cfg.Name,
		MaxRequests: cfg.MaxRequests,
		Interval:    cfg.Interval,
		Timeout:     cfg.Timeout,
		ReadyToTrip: cfg.ReadyToTrip,
		OnStateChange: func(name string, from, to gobreaker.State) {
			span := trace.SpanFromContext(context.Background())
			span.AddEvent("circuit_state_change", trace.WithAttributes(
				attribute.String("circuit", name),
				attribute.String("from", from.String()),
				attribute.String("to", to.String()),
			))
		},
	})
}

var ErrCircuitOpen = errors.New("circuit breaker is open")

// ============================================
// TIMEOUT
// ============================================

type TimeoutError struct {
	Duration time.Duration
}

func (e TimeoutError) Error() string {
	return "operation timed out after " + e.Duration.String()
}

func WithTimeout[T any](ctx context.Context, fn func(context.Context) (T, error), timeout time.Duration) (T, error) {
	ctx, span := tracer.Start(ctx, "timeout")
	defer span.End()

	span.SetAttributes(attribute.Int64("timeout_ms", timeout.Milliseconds()))

	ctx, cancel := context.WithTimeout(ctx, timeout)
	defer cancel()

	resultCh := make(chan T, 1)
	errCh := make(chan error, 1)

	go func() {
		result, err := fn(ctx)
		if err != nil {
			errCh <- err
			return
		}
		resultCh <- result
	}()

	select {
	case result := <-resultCh:
		span.SetStatus(codes.Ok, "")
		return result, nil
	case err := <-errCh:
		span.SetStatus(codes.Error, err.Error())
		var zero T
		return zero, err
	case <-ctx.Done():
		span.SetStatus(codes.Error, "timeout")
		var zero T
		return zero, TimeoutError{Duration: timeout}
	}
}

// ============================================
// BULKHEAD (Semaphore)
// ============================================

type Bulkhead struct {
	sem  chan struct{}
	name string
}

func NewBulkhead(maxConcurrent int, name string) *Bulkhead {
	return &Bulkhead{
		sem:  make(chan struct{}, maxConcurrent),
		name: name,
	}
}

func (b *Bulkhead) Execute(ctx context.Context, fn func() error) error {
	ctx, span := tracer.Start(ctx, "bulkhead."+b.name)
	defer span.End()

	span.SetAttributes(
		attribute.Int("max_concurrent", cap(b.sem)),
		attribute.Int("current_running", len(b.sem)),
	)

	select {
	case b.sem <- struct{}{}:
		defer func() { <-b.sem }()
		if err := fn(); err != nil {
			span.SetStatus(codes.Error, err.Error())
			return err
		}
		span.SetStatus(codes.Ok, "")
		return nil
	case <-ctx.Done():
		span.SetStatus(codes.Error, "context cancelled")
		return ctx.Err()
	}
}
```

### Usage

```go
package main

import (
	"context"
	"myapp/internal/utils"
	"time"
)

func main() {
	ctx := context.Background()

	// Retry
	result, err := utils.WithRetry(ctx, func() (string, error) {
		return fetchData()
	}, utils.DefaultRetryOptions())

	// Circuit breaker
	cb := utils.NewCircuitBreaker[string](utils.DefaultCircuitBreakerConfig("payment-api"))
	result, err = cb.Execute(func() (string, error) {
		return processPayment()
	})

	// Timeout
	result, err = utils.WithTimeout(ctx, func(ctx context.Context) (string, error) {
		return slowOperation(ctx)
	}, 5*time.Second)

	// Bulkhead
	bulkhead := utils.NewBulkhead(5, "database")
	err = bulkhead.Execute(ctx, func() error {
		return dbOperation()
	})
}
```

---

## Anti-Pattern: Inline Retry Logic

```typescript
// BAD: Duplicated retry logic
const fetchData = async () => {
  let attempts = 0;
  while (attempts < 3) {
    try {
      return await fetch('/api/data');
    } catch (e) {
      attempts++;
      await new Promise(r => setTimeout(r, 1000 * attempts));
    }
  }
};

// GOOD: Use centralized utility with OTel
import { withRetry } from '@/utils/resilience';
const data = await withRetry(() => fetch('/api/data'));
```

---

## References

- [p-retry v6 Documentation](https://github.com/sindresorhus/p-retry)
- [opossum Circuit Breaker](https://nodeshift.dev/opossum/)
- [tenacity 9.x Documentation](https://tenacity.readthedocs.io)
- [gobreaker v2](https://github.com/sony/gobreaker)
- [OpenTelemetry Tracing](https://opentelemetry.io/docs/concepts/signals/traces/)
