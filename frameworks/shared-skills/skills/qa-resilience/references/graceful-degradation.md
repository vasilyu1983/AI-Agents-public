# Graceful Degradation Patterns

Maintaining partial functionality during failures with strategic fallback mechanisms.

---
## Table of Contents

- [Pattern: Graceful Degradation](#pattern-graceful-degradation)
- [Expert Judgment: What to Shed First](#expert-judgment-what-to-shed-first)
- [Degradation Strategy 1: Cached Fallback](#degradation-strategy-1-cached-fallback)
- [Degradation Strategy 2: Default Values](#degradation-strategy-2-default-values)
- [Degradation Strategy 3: Feature Toggles](#degradation-strategy-3-feature-toggles)
- [Degradation Strategy 4: Reduced Functionality](#degradation-strategy-4-reduced-functionality)
- [Degradation Strategy 5: Partial Responses](#degradation-strategy-5-partial-responses)
- [Degradation Strategy 6: Queue-Based Async Processing](#degradation-strategy-6-queue-based-async-processing)
- [User Experience for Degraded Mode](#user-experience-for-degraded-mode)
- [Monitoring Degraded State](#monitoring-degraded-state)
- [Alert when running in degraded mode for > 10 min](#alert-when-running-in-degraded-mode-for-10-min)
- [Checklist](#checklist)
- [Related Resources](#related-resources)


## Pattern: Graceful Degradation

**Use when:** Maintaining partial functionality during failures.

**Core Principle:** Critical path succeeds even when non-critical dependencies fail.

---

## Expert Judgment: What to Shed First

Engineering can build every strategy in this file and still make the outage worse, because "what degrades first" is a product and revenue decision that engineering cannot make alone — it requires the same input a pricing or trust decision would. Decide this **before** an incident, with product/business sign-off, not during one under pressure. A workable order-of-shedding framework:

1. **Rank features by (a) revenue/trust impact if broken and (b) resource cost to keep running**, not by how easy they are to degrade. The easiest thing to turn off (e.g., a recommendations widget) is often also low-impact, which is why it is usually the correct first thing to shed — but verify this with data (conversion impact, support-ticket volume) rather than assuming code-level "non-critical" tags are still accurate; they rot as products change.
2. **Protect the transaction-completion path last.** Whatever lets a user finish the action they came to do — checkout, message send, booking confirmation — should be the last thing degraded, even if it means shedding everything else first (search relevance, personalization, analytics beacons, non-essential third-party calls, image/video transcoding quality).
3. **Protect anything with a regulatory, safety, or contractual floor before protecting anything to do with vanity metrics or engagement optimization.** A feature that exists to satisfy an SLA, an accessibility requirement, or a compliance obligation is not a "nice to have" even if it looks low-traffic.
4. **Prefer shedding write amplification before shedding reads**, when both are contributing to overload: a failed read usually degrades UX; a failed or duplicated write can corrupt state or double-charge a customer. Load-shed queue producers and background writers before serving-path reads where possible.
5. **Make the shed list explicit and pre-approved**, e.g. a tiered list in the runbook: Tier 3 (shed immediately under load) → Tier 2 (shed if Tier 3 shedding is insufficient) → Tier 1 (never shed without an incident commander's explicit decision, logged). Without this, the person paged at 3 a.m. is forced to invent a prioritization scheme live, under time pressure, without the business context to get it right — this is how outages turn "just the recommendations widget was down" into "checkout was down" because someone shed the wrong thing first, or shed nothing until it was too late.
6. **Revisit the ranking on a schedule** (e.g., quarterly, or after any feature launch that changes revenue mix) — a shed-priority list calibrated for last year's product is exactly the kind of stale artifact that fails silently until the next incident proves it wrong.

This ranking exercise is the direct product-decision analogue of the priority-tier request shedding described in [load-shedding-backpressure.md](load-shedding-backpressure.md) — that file's tiers describe *how* to shed at the request layer; this section is about *which business capabilities* those tiers should map to.

---

## Degradation Strategy 1: Cached Fallback

**Use when:** Stale data is better than no data.

```javascript
async function getUserProfile(userId) {
  try {
    // Try primary source
    const user = await api.getUser(userId);

    // Update cache on success
    await cache.set(`user:${userId}`, user, 3600); // 1 hour TTL

    return user;
  } catch (error) {
    // Fall back to cache
    const cached = await cache.get(`user:${userId}`);
    if (cached) {
      logger.warn('Using cached user profile', { userId, error });
      return { ...cached, _degraded: true, _cached: true };
    }

    throw error;
  }
}
```

**Cache-Aside Pattern with Graceful Degradation:**

```javascript
async function getProductDetails(productId) {
  // 1. Try cache first
  const cached = await cache.get(`product:${productId}`);
  if (cached && !cached._expired) {
    return cached;
  }

  // 2. Try database
  try {
    const product = await db.query('SELECT * FROM products WHERE id = $1', [productId]);

    if (!product) {
      throw new Error('Product not found');
    }

    // Update cache
    await cache.set(`product:${productId}`, product, 3600);

    return product;
  } catch (error) {
    // 3. Fall back to stale cache if database fails
    if (cached) {
      logger.warn('Database failed, using stale cache', { productId, error });
      return { ...cached, _degraded: true, _stale: true };
    }

    throw error;
  }
}
```

---

## Degradation Strategy 2: Default Values

**Use when:** Sensible defaults maintain functionality.

```javascript
async function getRecommendations(userId) {
  try {
    return await mlService.getRecommendations(userId);
  } catch (error) {
    logger.error('ML service failed, falling back to popular items', { error });

    // Fall back to popular items
    return {
      items: await getPopularItems(),
      _degraded: true,
      _reason: 'ML service unavailable',
      _fallback: 'popular_items',
    };
  }
}

async function getPopularItems() {
  // Return cached popular items (updated daily)
  return await cache.get('popular_items') || DEFAULT_POPULAR_ITEMS;
}

const DEFAULT_POPULAR_ITEMS = [
  { id: 1, name: 'Product A', score: 0.95 },
  { id: 2, name: 'Product B', score: 0.90 },
  { id: 3, name: 'Product C', score: 0.85 },
];
```

---

## Degradation Strategy 3: Feature Toggles

**Use when:** Non-critical features can be disabled during failures.

```javascript
async function processOrder(order) {
  // Critical: save order
  const result = await saveOrder(order);

  // Non-critical: send confirmation email
  if (featureFlags.isEnabled('email-notifications')) {
    try {
      await sendConfirmationEmail(order);
    } catch (error) {
      // Log but don't fail order
      logger.error('Email failed', { error, orderId: order.id });
      metrics.increment('email.send.failed');
    }
  }

  // Non-critical: update analytics
  if (featureFlags.isEnabled('analytics')) {
    try {
      await analytics.trackPurchase(order);
    } catch (error) {
      // Log but don't fail order
      logger.error('Analytics failed', { error, orderId: order.id });
    }
  }

  return result;
}
```

**Dynamic Feature Flags with Circuit Breaker:**

```javascript
class FeatureToggle {
  constructor() {
    this.features = new Map();
    this.circuitBreakers = new Map();
  }

  isEnabled(featureName) {
    // Check if feature manually disabled
    if (!this.features.get(featureName)?.enabled) {
      return false;
    }

    // Check if circuit breaker is open
    const breaker = this.circuitBreakers.get(featureName);
    return !breaker || breaker.state !== 'OPEN';
  }

  async executeIfEnabled(featureName, fn, fallback = null) {
    if (!this.isEnabled(featureName)) {
      return fallback;
    }

    try {
      return await fn();
    } catch (error) {
      logger.error(`Feature ${featureName} failed`, { error });

      // Open circuit if too many failures
      const breaker = this.circuitBreakers.get(featureName);
      if (breaker) {
        breaker.recordFailure();
      }

      return fallback;
    }
  }
}

// Usage
const featureFlags = new FeatureToggle();

async function processOrder(order) {
  const result = await saveOrder(order);

  // Execute non-critical features with fallback
  await featureFlags.executeIfEnabled(
    'email-notifications',
    () => sendConfirmationEmail(order),
    null
  );

  return result;
}
```

---

## Degradation Strategy 4: Reduced Functionality

**Use when:** Simpler fallback provides core value.

```javascript
async function search(query) {
  try {
    // Try full-text search with advanced features
    return await elasticsearchService.search(query, {
      fuzzyMatch: true,
      synonyms: true,
      facets: true,
      personalization: true,
    });
  } catch (error) {
    logger.warn('Elasticsearch down, using SQL fallback', { error });

    // Fall back to basic SQL LIKE search
    const results = await db.query(
      'SELECT * FROM products WHERE name ILIKE $1 LIMIT 20',
      [`%${query}%`]
    );

    return {
      results,
      _degraded: true,
      _fallback: 'sql_search',
      _features_disabled: ['fuzzy_match', 'synonyms', 'facets', 'personalization'],
    };
  }
}
```

---

## Degradation Strategy 5: Partial Responses

**Use when:** Some data is better than complete failure.

```javascript
async function getUserDashboard(userId) {
  const results = await Promise.allSettled([
    getProfile(userId),
    getRecentOrders(userId),
    getRecommendations(userId),
    getNotifications(userId),
  ]);

  const [profile, orders, recommendations, notifications] = results;

  return {
    profile: profile.status === 'fulfilled' ? profile.value : null,
    orders: orders.status === 'fulfilled' ? orders.value : [],
    recommendations: recommendations.status === 'fulfilled' ? recommendations.value : [],
    notifications: notifications.status === 'fulfilled' ? notifications.value : [],
    _partial: results.some(r => r.status === 'rejected'),
    _errors: results
      .filter(r => r.status === 'rejected')
      .map((r, i) => ({ section: ['profile', 'orders', 'recommendations', 'notifications'][i], error: r.reason })),
  };
}
```

---

## Degradation Strategy 6: Queue-Based Async Processing

**Use when:** Operation can be deferred.

```javascript
async function createOrder(orderData) {
  // Critical: save order to database
  const order = await db.insert('orders', orderData);

  // Non-critical: enqueue async operations
  try {
    await queue.enqueue('send-confirmation-email', { orderId: order.id });
    await queue.enqueue('update-inventory', { orderId: order.id });
    await queue.enqueue('notify-analytics', { orderId: order.id });
  } catch (error) {
    // If queue fails, log but don't block order creation
    logger.error('Failed to enqueue async tasks', { error, orderId: order.id });
  }

  return order;
}

// Background worker processes queue
async function processQueue() {
  const job = await queue.dequeue();

  try {
    await processJob(job);
  } catch (error) {
    // Retry with exponential backoff
    await queue.enqueue(job.type, job.data, {
      delay: calculateBackoff(job.attempts),
      maxAttempts: 5,
    });
  }
}
```

---

## User Experience for Degraded Mode

**Indicate Degraded State:**

```javascript
// API response
{
  "data": { /* partial data */ },
  "status": {
    "degraded": true,
    "message": "Some features temporarily unavailable",
    "missing": ["recommendations", "personalization"],
    "eta": "2025-11-22T15:30:00Z"
  }
}
```

**Frontend Handling:**

```javascript
function DashboardComponent({ userId }) {
  const { data, status } = useDashboard(userId);

  return (
    <div>
      {status.degraded && (
        <Alert severity="warning">
          Some features are temporarily unavailable. We're working on it!
        </Alert>
      )}

      {data.profile ? (
        <UserProfile profile={data.profile} />
      ) : (
        <Skeleton variant="rectangular" />
      )}

      {data.recommendations.length > 0 ? (
        <Recommendations items={data.recommendations} />
      ) : (
        <div>Recommendations currently unavailable</div>
      )}
    </div>
  );
}
```

---

## Monitoring Degraded State

**Metrics to Track:**

```javascript
// Track degradation rate
metrics.gauge('service.degraded', isDegraded ? 1 : 0);
metrics.increment('service.degradation.event', { reason: 'elasticsearch_down' });

// Track which features are degraded
metrics.gauge('feature.email.degraded', emailServiceDown ? 1 : 0);
metrics.gauge('feature.search.degraded', searchServiceDown ? 1 : 0);

// Track fallback usage
metrics.increment('fallback.cache.used', { service: 'user-profile' });
metrics.increment('fallback.default.used', { service: 'recommendations' });
```

**Alerts:**

```yaml
# Alert when running in degraded mode for > 10 min
- alert: ServiceDegraded
  expr: service_degraded == 1
  for: 10m
  annotations:
    summary: "Service running in degraded mode"
    description: "{{ $labels.service }} has been degraded for > 10 min"
```

---

## Checklist

- [ ] Critical path vs non-critical operations identified
- [ ] Fallback behavior defined for each dependency
- [ ] Degraded mode clearly indicated to users
- [ ] Cache strategies in place for common data
- [ ] Feature flags control non-essential features
- [ ] Degradation metrics tracked
- [ ] Alerts when running in degraded mode
- [ ] Default values configured for ML/recommendations
- [ ] Partial responses acceptable (Promise.allSettled)
- [ ] Queue-based processing for non-critical operations

---

## Related Resources

- [circuit-breaker-patterns.md](circuit-breaker-patterns.md) - Trigger degradation when circuit opens
- [retry-patterns.md](retry-patterns.md) - Retry before degrading
- [timeout-policies.md](timeout-policies.md) - Timeout triggers degradation
- [resilience-checklists.md](resilience-checklists.md) - Comprehensive fallback strategies
