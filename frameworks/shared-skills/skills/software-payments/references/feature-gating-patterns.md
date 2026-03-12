# Feature Gating Patterns

Detailed patterns for feature gating, entitlement architectures, fraud prevention, and typed gated responses in payment-integrated applications.

---

## Consumable vs. Binary Unlock Architecture

Two fundamental access models exist for paid features. Most apps need both.

### Binary Unlocks

Simple "has completed purchase or has active subscription at correct tier" check. Examples: Chart PDF export, Year Ahead Report, advanced house systems.

```typescript
// Binary unlock — simple tier check
export function hasBinaryAccess(
  tier: SubscriptionTier,
  feature: Feature,
  purchases: Purchase[]
): boolean {
  // Subscription grants access
  if (hasFeatureAccess(tier, feature)) return true;
  // One-time purchase grants access
  return purchases.some(p => p.feature === feature && p.status === 'completed');
}
```

### Consumables

Consumable features (e.g., Ask Pack credits, AI interpretation tokens) require an atomic decrement on a counter column with optimistic locking. Without atomicity, concurrent requests can overdraw the pool.

```sql
-- Atomic decrement with optimistic lock
UPDATE ask_cosmos_bonus_pool
SET remaining = remaining - 1
WHERE user_id = $1 AND remaining > 0
RETURNING remaining;
-- If 0 rows returned → pool exhausted, do NOT grant access
```

```typescript
// Application-level consumable check
async function consumeCredit(userId: string, pool: string): Promise<boolean> {
  const { data, error } = await supabase
    .rpc('decrement_pool', { p_user_id: userId, p_pool: pool });

  if (error || !data || data.length === 0) {
    // Pool exhausted or DB error — deny access
    return false;
  }

  return true; // Credit consumed, proceed with feature
}
```

PASS/FAIL:

```
FAIL: SELECT remaining, then UPDATE remaining - 1 in two queries → race condition, overdraw
PASS: Single UPDATE ... WHERE remaining > 0 RETURNING → atomic, no overdraw
FAIL: Caching consumable count client-side and decrementing locally → stale count
PASS: Server-side atomic decrement, return fresh count to client
```

---

## Spread-Then-Override Tier Filtering

When building gated API responses, the filtering strategy determines how safely new fields are handled over time.

### Spread-Then-Override (PASS: Forward-Compatible)

Start with the full response object, then override only the gated fields. New fields added to the response automatically pass through to paid users without code changes.

```typescript
// PASS: Forward-compatible — new fields automatically pass through
function buildGatedResponse(fullResponse: FullResponse, userTier: Tier): GatedResponse {
  return {
    ...fullResponse,
    // Override only gated fields
    transits: hasAccess(userTier, 'transits')
      ? fullResponse.transits
      : [],
    transitsGated: !hasAccess(userTier, 'transits'),
    transitTeaser: !hasAccess(userTier, 'transits')
      ? { count: fullResponse.transits.length, topTransit: fullResponse.transits[0]?.name }
      : undefined,
  };
}
```

### Allowlist (FAIL: Brittle)

Explicitly listing allowed fields means every new field must be added to the allowlist. Forgetting silently drops data for all users.

```typescript
// FAIL: Allowlist — silently drops newly added fields
function buildGatedResponse(data: FullResponse): GatedResponse {
  return {
    sunSign: data.sunSign,
    moonSign: data.moonSign,
    // Forgot to add risingSign when it was added last sprint → invisible bug
  };
}
```

---

## Fraud Prevention Patterns

### 1. Cross-Account Intro Pricing Detection

Prevent users from creating new accounts to repeatedly claim introductory pricing.

```typescript
// Before granting intro discount, check Stripe for prior customers with same email
async function isEligibleForIntroPricing(email: string): Promise<boolean> {
  const existingCustomers = await stripe.customers.list({
    email: email.toLowerCase(),
    limit: 1,
  });

  // If any prior customer record exists, they've had an account before
  if (existingCustomers.data.length > 0) {
    return false; // Not eligible for intro pricing
  }

  return true;
}
```

### 2. Refund-and-Revoke

When a charge is refunded (either voluntarily or via dispute), revoke access and zero out consumable pools.

```typescript
// charge.refunded webhook handler
async function handleChargeRefunded(charge: Stripe.Charge) {
  const customerId = charge.customer as string;
  const user = await getUserByStripeCustomerId(customerId);
  if (!user) return;

  // Revoke subscription access
  await db.subscriptions.update({
    tier: 'free',
    status: 'canceled',
    updated_at: new Date(),
  }).where({ user_id: user.id });

  // Zero out consumable pools
  await db.askCosmosBonusPool.update({
    remaining: 0,
    updated_at: new Date(),
  }).where({ user_id: user.id });

  // Clear feature cache
  await invalidateFeatureCache(user.id);
}
```

### 3. Stale Feature Cache Invalidation

When subscription state changes (cancellation, downgrade, refund), immediately clear any cached feature entitlements. Stale caches let users retain access after they should have lost it.

```typescript
// Call on: subscription.deleted, subscription.updated (downgrade), charge.refunded
async function invalidateFeatureCache(userId: string): Promise<void> {
  await redis.del(`user_features:${userId}`);
  // If using in-memory cache, also publish invalidation event
  await redis.publish('feature_cache_invalidate', userId);
}
```

### 4. Rate Limiting LLM-Costly Features

Features that invoke LLMs or expensive compute need per-user rate limits independent of subscription tier to prevent abuse.

| Feature | Limit | Window | Rationale |
|---------|-------|--------|-----------|
| `write:ask-cosmos` | 20 | per hour | LLM inference cost |
| `write:dreams` | 20 | per day | LLM interpretation cost |
| `write:chart-pdf` | 10 | per hour | PDF rendering + compute |
| `read:compatibility` | 50 | per hour | Prevent scraping |

```typescript
// Rate limit check before expensive operation
const key = `ratelimit:${feature}:${userId}`;
const current = await redis.incr(key);
if (current === 1) {
  await redis.expire(key, windowSeconds);
}
if (current > limit) {
  return Response.json(
    { error: 'rate_limited', retryAfter: await redis.ttl(key) },
    { status: 429 }
  );
}
```

---

## Discriminated Union for Gated Fields

A type-safe pattern for API responses where fields can be either fully available or gated with a teaser.

### Type Definition

```typescript
type GatedField<T> =
  | { gated: false; data: T }
  | { gated: true; teaser: { count: number; preview: string } };
```

### API Response Usage

```typescript
type ChartResponse = {
  sunSign: string;          // Always available (free tier)
  moonSign: string;         // Always available (free tier)
  transits: GatedField<Transit[]>;
  houseSystems: GatedField<HouseSystem[]>;
  yearAhead: GatedField<YearAheadReport>;
};

function buildChartResponse(data: FullChartData, tier: Tier): ChartResponse {
  return {
    sunSign: data.sunSign,
    moonSign: data.moonSign,
    transits: hasAccess(tier, 'transits')
      ? { gated: false, data: data.transits }
      : { gated: true, teaser: { count: data.transits.length, preview: data.transits[0]?.summary ?? '' } },
    houseSystems: hasAccess(tier, 'house_systems')
      ? { gated: false, data: data.houseSystems }
      : { gated: true, teaser: { count: data.houseSystems.length, preview: 'Placidus, Whole Sign, ...' } },
    yearAhead: hasAccess(tier, 'year_ahead')
      ? { gated: false, data: data.yearAhead }
      : { gated: true, teaser: { count: 12, preview: 'Your year begins with a powerful...' } },
  };
}
```

### React Component with Render Props

```tsx
type GatedFieldProps<T> = {
  field: GatedField<T>;
  feature: Feature;
  children: (data: T) => React.ReactNode;
  fallback?: (teaser: { count: number; preview: string }) => React.ReactNode;
};

function GatedFieldView<T>({ field, feature, children, fallback }: GatedFieldProps<T>) {
  if (!field.gated) {
    return <>{children(field.data)}</>;
  }

  if (fallback) {
    return <>{fallback(field.teaser)}</>;
  }

  return <UpgradePrompt feature={feature} teaser={field.teaser} />;
}

// Usage
<GatedFieldView field={response.transits} feature="transits">
  {(transits) => <TransitList transits={transits} />}
</GatedFieldView>
```

### Why Discriminated Union over Optional Fields

| Approach | Pros | Cons |
|----------|------|------|
| `data?: T` (optional) | Simple | No teaser, no way to distinguish "empty" from "gated" |
| `data: T \| GatedTeaser` (union, no discriminant) | Compact | Requires `Array.isArray()` or `instanceof` checks; easy to forget |
| `GatedField<T>` (discriminated union) | Type-safe, exhaustive switch, teaser included | Slightly more verbose response |

The discriminated union forces the client to handle both branches. TypeScript narrows the type after checking `field.gated`, so accessing `field.data` on a gated field is a compile error.

```typescript
// TypeScript enforces exhaustive handling
function renderTransits(field: GatedField<Transit[]>) {
  if (field.gated) {
    // field.teaser is available, field.data is NOT
    return showUpgrade(field.teaser);
  }
  // field.data is available, field.teaser is NOT
  return renderList(field.data);
}
```
