# Circuit Breaker Patterns

Production-ready circuit breaker implementations for preventing cascading failures.

---

## Pattern: Circuit Breaker (Classic)

**Use when:** Preventing cascading failures from external dependencies.

**Circuit Breaker States:**

```text
CLOSED → requests flow normally
   ↓ (failure threshold reached)
OPEN → requests fail immediately, no calls to dependency
   ↓ (timeout period expires)
HALF-OPEN → test request allowed
   ↓ (success) → CLOSED | (failure) → OPEN
```

**Node.js Implementation (opossum library):**

```javascript
const CircuitBreaker = require('opossum');

// Wrap external service call
async function callExternalAPI(data) {
  const response = await fetch('https://api.example.com/data', {
    method: 'POST',
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    throw new Error(`API error: ${response.status}`);
  }

  return response.json();
}

// Circuit breaker configuration
const options = {
  timeout: 3000,              // Timeout after 3s
  errorThresholdPercentage: 50, // Open after 50% errors
  resetTimeout: 30000,         // Try again after 30s
  volumeThreshold: 10,         // Min 10 requests before opening
};

const breaker = new CircuitBreaker(callExternalAPI, options);

// Fallback when circuit is open
breaker.fallback(() => {
  return { status: 'degraded', data: getCachedData() };
});

// Event listeners
breaker.on('open', () => console.log('Circuit opened'));
breaker.on('halfOpen', () => console.log('Circuit half-open'));
breaker.on('close', () => console.log('Circuit closed'));

// Usage
try {
  const result = await breaker.fire(requestData);
  console.log(result);
} catch (error) {
  console.error('Request failed:', error);
}
```

**Python Implementation (pybreaker-style):**

```python
import pybreaker
import requests

# Configure circuit breaker
breaker = pybreaker.CircuitBreaker(
    fail_max=5,        # Open after 5 failures
    reset_timeout=30,  # Try again after 30s
)

@breaker
def call_external_api(data):
    response = requests.post(
        'https://api.example.com/data',
        json=data,
        timeout=3,
    )
    response.raise_for_status()
    return response.json()

# Fallback function
def fallback_handler():
    return {'status': 'degraded', 'data': get_cached_data()}

# Usage with fallback
try:
    result = call_external_api(request_data)
except Exception as e:
    if breaker.current_state == 'open':
        result = fallback_handler()
    else:
        raise
```

**Checklist:**

- Circuit breaker wraps external dependencies (not business logic).
- Failure thresholds and windows are tuned to traffic volume + error budget.
- Reset timeout is set (30-60s typical) and half-open probes are bounded.
- Fallback behavior is explicit (cache, stale reads, partial response, or hard fail).
- Circuit state changes are emitted as metrics/logs and alertable.

---

## Pattern: Adaptive Circuit Breaker (2024-2025)

**Use when:** Static thresholds cause false positives during traffic spikes or miss real issues during low traffic.

**Evolution from Static to Adaptive:**

Traditional circuit breakers use fixed thresholds (e.g., "open after 50% errors"). Adaptive circuit breakers use real-time data to adjust behavior based on context:

- **Traffic-aware thresholds:** Different thresholds for peak hours vs low traffic
- **Baseline learning:** ML models learn normal failure rates over time
- **Anomaly detection:** Detect unusual patterns (sudden spike vs gradual degradation)
- **Dynamic timeouts:** Adjust based on observed latency percentiles

**Conceptual Implementation (Node.js with adaptive logic):**

```javascript
class AdaptiveCircuitBreaker {
  constructor(service) {
    this.service = service;
    this.window = []; // Rolling window of results
    this.baselineFailureRate = 0.05; // Learned over time
    this.state = 'CLOSED';
    this.consecutiveSuccesses = 0;
  }

  async call(fn, context) {
    if (this.state === 'OPEN') {
      if (this.shouldAttemptReset()) {
        this.state = 'HALF-OPEN';
      } else {
        throw new Error('Circuit breaker is OPEN');
      }
    }

    try {
      const result = await fn();
      this.recordSuccess();
      return result;
    } catch (error) {
      this.recordFailure();

      // Adaptive threshold based on current traffic volume
      const currentVolume = this.getRequestVolume();
      const adaptiveThreshold = this.calculateAdaptiveThreshold(currentVolume);

      if (this.currentFailureRate() > adaptiveThreshold) {
        this.state = 'OPEN';
        this.openedAt = Date.now();
      }

      throw error;
    }
  }

  calculateAdaptiveThreshold(volume) {
    // Higher threshold during low traffic (more tolerance)
    // Lower threshold during high traffic (strict)
    const baseThreshold = 0.5;

    if (volume < 10) {
      return 0.7; // 70% for low volume (avoid false positives)
    } else if (volume < 100) {
      return baseThreshold; // 50% for medium volume
    } else {
      // High volume: use anomaly detection
      const currentRate = this.currentFailureRate();
      const isAnomaly = currentRate > (this.baselineFailureRate * 3);
      return isAnomaly ? 0.3 : baseThreshold; // Stricter when anomaly detected
    }
  }

  updateBaseline() {
    // Update baseline from historical data (run periodically)
    const recentWindow = this.window.slice(-1000);
    const failures = recentWindow.filter(r => !r.success).length;
    this.baselineFailureRate = failures / recentWindow.length;
  }

  currentFailureRate() {
    const recent = this.window.slice(-100);
    if (recent.length === 0) return 0;
    const failures = recent.filter(r => !r.success).length;
    return failures / recent.length;
  }

  getRequestVolume() {
    const oneMinuteAgo = Date.now() - 60000;
    return this.window.filter(r => r.timestamp > oneMinuteAgo).length;
  }

  // ... other methods
}
```

**Key Adaptive Strategies:**

1. **Volume-Based Thresholds:**
   - Low traffic (<10 req/min): Higher tolerance (70% threshold) to avoid false positives
   - High traffic (>100 req/min): Anomaly detection vs learned baseline

2. **Baseline Learning:**
   - Track historical failure rates (e.g., last 1000 requests)
   - Update baseline during stable periods
   - Compare current rate to 3x baseline for anomaly detection

3. **Context-Aware Decisions:**
   - Time-of-day patterns (weekday vs weekend)
   - Seasonal traffic variations
   - Deployment events (expect higher errors post-deploy)

4. **Dynamic Timeout Adjustment:**

   ```javascript
   function calculateAdaptiveTimeout(service) {
     const p95Latency = getP95Latency(service); // From metrics
     const baseTimeout = p95Latency * 2; // 2x P95 as baseline

     // Add buffer during traffic spikes
     const currentLoad = getCurrentLoad();
     const loadMultiplier = currentLoad > 0.8 ? 1.5 : 1.0;

     return baseTimeout * loadMultiplier;
   }
   ```

**Checklist:**

- [ ] Collect baseline metrics before enabling adaptive logic
- [ ] Track P95/P99 latency for dynamic timeouts
- [ ] Implement traffic volume detection (requests per minute)
- [ ] Define anomaly threshold (e.g., 3x baseline)
- [ ] Add observability for threshold changes
- [ ] Test with production-like traffic patterns
- [ ] Monitor false positive rate (circuits opened unnecessarily)
- [ ] Review and retrain baseline monthly

**When NOT to Use Adaptive Patterns:**

- **Low-traffic services:** Static thresholds simpler and sufficient
- **Predictable failure modes:** If failures are binary (works/doesn't work), no need for ML
- **Early-stage systems:** Need stable baseline data first (6-12 months)
- **Regulatory constraints:** Some industries require fixed, auditable thresholds

**Production Example (Conceptual):**

```javascript
// Combine with observability
const adaptiveBreaker = new AdaptiveCircuitBreaker('payment-api');

// Update baseline nightly
cron.schedule('0 3 * * *', () => {
  adaptiveBreaker.updateBaseline();
  metrics.gauge('circuit_breaker.baseline_failure_rate',
    adaptiveBreaker.baselineFailureRate);
});

// Use in application
app.post('/checkout', async (req, res) => {
  try {
    const result = await adaptiveBreaker.call(async () => {
      return await paymentAPI.charge(req.body);
    });
    res.json(result);
  } catch (error) {
    // Circuit open or payment failed
    res.status(503).json({ error: 'Service temporarily unavailable' });
  }
});
```

**Further Reading:**

- https://martinfowler.com/bliki/CircuitBreaker.html
- https://learn.microsoft.com/en-us/azure/architecture/patterns/circuit-breaker
- https://docs.aws.amazon.com/wellarchitected/latest/reliability-pillar/welcome.html

---

## Related Resources

- [retry-patterns.md](retry-patterns.md) - Combine circuit breakers with retry logic
- [timeout-policies.md](timeout-policies.md) - Configure timeouts for circuit breakers
- [resilience-checklists.md](resilience-checklists.md) - Comprehensive dependency hardening
