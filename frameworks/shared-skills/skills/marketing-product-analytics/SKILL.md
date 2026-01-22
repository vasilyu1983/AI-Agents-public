---
name: marketing-product-analytics
description: Product analytics instrumentation and strategy covering event taxonomy design, tracking plans, user behavior analysis, activation/retention metrics, and marketing attribution. PostHog-first with multi-platform support (Pendo, Amplitude, Mixpanel, Heap).
---

# PRODUCT ANALYTICS — INSTRUMENTATION & MEASUREMENT OS (OPERATIONAL)

Built as a **no-fluff execution skill** for product analytics instrumentation, event design, and marketing measurement.

**Structure**: Core analytics fundamentals first. Platform-specific implementation in dedicated sections. PostHog is the primary reference platform with cross-platform patterns for Pendo, Amplitude, Mixpanel, and Heap.

---

## Modern Best Practices (January 2026)

**Primary Sources**:
- PostHog Docs: https://posthog.com/docs/product-analytics/best-practices
- Amplitude Taxonomy Guide: https://amplitude.com/blog/event-taxonomy
- Segment Tracking Plan: https://segment.com/docs/protocols/tracking-plan/create/

### 2026 Product Analytics Landscape

| Trend | Impact | Action |
|-------|--------|--------|
| **AI agent analytics** | New event category for LLM interactions | Track prompts, completions, latency, outcomes |
| **Privacy-first tracking** | Cookie deprecation, consent requirements | Server-side events, first-party data, consent-aware capture |
| **Revenue attribution** | Connect product usage to business outcomes | Event → activation → revenue pipeline |
| **Hybrid attribution models** | 80% of companies combining models by 2026 | First-party data + probabilistic models |
| **Autocapture evolution** | Reduce instrumentation burden | Combine autocapture with strategic custom events |

### Key Metrics (2026 Benchmarks)

| Metric | Median | Top Quartile | Source |
|--------|--------|--------------|--------|
| **Day 7 retention** | 4% | 7%+ | Amplitude 2025 Report |
| **Month 1 retention** | 39% | 50%+ | Pendo 2025 Report |
| **Activation rate** | 25% | 40%+ | Industry benchmark |
| **NRR (B2B SaaS)** | 106% | 120%+ | SaaS benchmark |
| **GRR (B2B SaaS)** | 90% | 95%+ | SaaS benchmark |

---

## When to Use This Skill

- **Event taxonomy design**: Naming conventions, event hierarchy, property structure
- **Tracking plan creation**: What to track, where, and why
- **Marketing attribution**: UTM capture, campaign tracking, source attribution
- **Activation metrics**: Defining and measuring user activation
- **Retention analysis**: Cohort analysis, churn prediction, engagement scoring
- **Platform setup**: PostHog, Pendo, Amplitude, Mixpanel, Heap configuration
- **Data quality**: Event validation, debugging, governance

---

## Core: The Three-Layer Framework

Before instrumenting anything, define your three measurement layers. Keep them stable.

```text
┌─────────────────────────────────────────────────────────────────┐
│  ACQUISITION          ACTIVATION           RETENTION            │
│  How users arrive     First value moment   Repeated value       │
│                                                                 │
│  page_viewed          [your_activation]    [your_engagement]    │
│  campaign_landed      feature_first_used   user_returned        │
│  signup_completed     onboarding_done      streak_achieved      │
└─────────────────────────────────────────────────────────────────┘
```

### Minimum Viable Analytics (MVA)

**Start with 5-15 events, not 200.** You can always add more, but cleaning up noise is painful.

| Layer | Required Events | Optional (add after 1 week) |
|-------|-----------------|----------------------------|
| **Acquisition** | `page_viewed`, `signup_completed` | `campaign_landed`, `referral_clicked` |
| **Activation** | Your activation event (1-2 max) | `onboarding_step_completed` |
| **Engagement** | Your engagement signal (1-2 max) | `feature_used`, `content_engaged` |
| **Conversion** | `purchase_completed` or `subscription_started` | `checkout_started`, `upgrade_clicked` |

### Example: Content App MVA

```text
Activation = reading_generated (content delivered)
Engagement = reading_engaged (scroll_60 OR dwell_15s)
Conversion = subscription_started

That's 3 custom events + autocaptured pageviews. Start there.
```

### Example: SaaS App MVA

```text
Activation = project_created OR team_member_invited
Engagement = feature_used (with feature_name property)
Conversion = checkout_completed

That's 3 custom events. Add more only when you have questions the data can't answer.
```

---

## Core: North Star Activation Event (VITAL)

**Every product must have ONE canonical activation event.**

This is the single event that means: "The user received real value."

### Why This Matters

Without a North Star event:
- Funnels fragment across multiple "success" definitions
- Retention becomes meaningless (returning to do what?)
- SEO/marketing analysis becomes noisy
- A/B experiments cannot be evaluated correctly

All analytics must ladder up to this one event.

### Defining Your North Star

| Product Type | North Star Event | When It Fires |
|--------------|------------------|---------------|
| **Content/Media** | `content_consumed` | Reading/video fully loaded and visible |
| **SaaS Tool** | `workflow_completed` | User completes core workflow |
| **E-commerce** | `purchase_completed` | Transaction successful |
| **Social** | `content_published` | User posts content |
| **Developer Tool** | `integration_working` | First successful API call/deploy |

### Example: Astrology App

```javascript
// North Star: User received astrology value
posthog.capture('generated_reading', {
  reading_type: 'compatibility',  // daily | chart | horoscope | compatibility
  // source: 'email',             // optional override; prefer session-level traffic_source
});

// Engagement: User engaged with the value
posthog.capture('reading_engaged', {
  reading_type: 'compatibility',
  engagement_type: 'scroll_60',   // scroll_60 | expand_section | dwell_15s
});
```

**Attribution note:** Prefer session-level `traffic_source` captured once per session. Only set `source` on an event when you intentionally override attribution (e.g., email or push).

### The North Star Rule

**Every feature event should collapse into one activation event with properties.**

```javascript
// ❌ WRONG: Multiple fragmented events
'daily_digest_viewed'
'chart_viewed'
'horoscope_viewed'
'compatibility_viewed'

// ✅ CORRECT: One event, differentiated by property
'generated_reading' { reading_type: 'compatibility' }
'generated_reading' { reading_type: 'chart' }
'generated_reading' { reading_type: 'horoscope' }
```

This mirrors subscription event patterns. Apply the same discipline to product features.

---

## Core: Event Quality Rules (Anti-Patterns)

### Anti-Pattern 1: Excessive `*_viewed` Events

**Problem**: Tracking UI states, not outcomes.

```javascript
// ❌ Analytics smell: These are UI states, not value delivery
'settings_viewed'
'dashboard_viewed'
'profile_viewed'
'modal_viewed'

// ✅ Better: Track outcomes only
'settings_changed' { setting_name: 'notifications' }
'report_generated' { report_type: 'weekly' }
```

**Rule**: If an event fires before the user receives value, question whether you need it.

### Anti-Pattern 2: Mixed Lifecycle Layers

**Problem**: Mixing authentication, onboarding, features, and subscriptions in one flat list.

Each event must answer **one clear question**:

| Question | Event Examples |
|----------|----------------|
| Did the user advance a lifecycle stage? | `signup_completed`, `onboarding_finished` |
| Did the user receive value? | `generated_reading`, `report_created` |
| Did the user show intent? | `checkout_started`, `upgrade_clicked` |
| Did the system change state? | `subscription_started`, `payment_failed` |

**If an event answers none of these, remove it.**

### Anti-Pattern 3: Manual Tracking of Derived Metrics

**Problem**: Manually tracking things PostHog should derive.

```javascript
// ❌ WRONG: Don't manually track these
'user_retained'
'user_returned'
'active_user'
'engaged_user'
'session_started'  // PostHog does this automatically

// ✅ CORRECT: Let PostHog derive from your activation/engagement events
'generated_reading'  // PostHog calculates retention from this
'reading_engaged'    // PostHog calculates engagement from this
```

PostHog is strongest when outcomes are **derived**, not explicitly tracked. You already apply this principle for `trial_converted`. Extend it consistently.

### Anti-Pattern 4: PII in Identify Calls

**Problem**: Storing email and personal data creates GDPR/compliance risk.

```javascript
// ❌ RISKY: Email is PII, creates data governance burden
posthog.identify(userId, {
  email: user.email,
  name: user.name,
  phone: user.phone
});

// ✅ SAFER: State-based identification, no PII
posthog.identify(userId, {
  subscription_tier: 'pro',
  onboarding_completed: true,
  signup_source: 'google'
});
```

Only store email if there is a strict operational reason AND you have proper consent.

### Anti-Pattern 5: Event Spam from Component Mounts

**Problem**: Events fire multiple times due to React re-renders.

```javascript
// ❌ WRONG: Fires on every mount/re-render
useEffect(() => {
  posthog.capture('dashboard_viewed');
}, []);

// ✅ CORRECT: Guard against spam
const track = useCallback(
  (event: string, properties?: Record<string, unknown>) => {
    if (!isPostHogReady()) return;
    posthog.capture(event, properties);
  },
  []
);
```

### Anti-Pattern 6: Incomplete Readiness Guard

**Problem**: `posthog` being defined does not mean it is initialized. Your guard can silently drop early events.

```typescript
// ❌ WRONG: Incomplete guard
if (!posthog?.__loaded) return;  // __loaded may not exist or be reliable

// ❌ WRONG: Truthy check is insufficient
if (!posthog) return;  // posthog object exists before init completes

// ✅ CORRECT: Stricter readiness check
function isPostHogReady(): boolean {
  return (
    typeof window !== 'undefined' &&
    !!posthog &&
    typeof posthog.capture === 'function'
  );
}

// Usage
const track = useCallback(
  (event: string, properties?: Record<string, unknown>) => {
    if (!isPostHogReady()) return;
    posthog.capture(event, properties);
  },
  []
);
```

**Why this matters**: Events fired before PostHog initializes are silently dropped. This causes:

- Missing early funnel events
- Incorrect activation counts
- Attribution data loss for fast users

---

## Core: Production Hardening Patterns

### Pattern 1: Session Context Registration (VITAL)

Register standard context once per session using `posthog.register()`. This attaches properties to ALL subsequent events without per-event duplication.

```typescript
export type TrafficSource = 'seo' | 'direct' | 'referral' | 'social' | 'internal' | 'paid' | 'email' | 'push';

// Register on first page load (before any events)
export function registerSessionContext() {
  if (!isPostHogReady()) return;

  const url = new URL(window.location.href);
  const params = url.searchParams;

  // Compute referrer domain safely
  let referrer_domain: string | null = null;
  try {
    if (document.referrer) referrer_domain = new URL(document.referrer).hostname;
  } catch {
    referrer_domain = null;
  }

  // UTM capture
  const utm_source = params.get('utm_source') ?? undefined;
  const utm_medium = params.get('utm_medium') ?? undefined;
  const utm_campaign = params.get('utm_campaign') ?? undefined;
  const utm_term = params.get('utm_term') ?? undefined;
  const utm_content = params.get('utm_content') ?? undefined;

  // Traffic source classification (simple, stable)
  const traffic_source: TrafficSource =
    utm_medium === 'cpc' || utm_medium === 'paid' ? 'paid'
    : referrer_domain ? (
        referrer_domain.includes('google.') || referrer_domain.includes('bing.') ? 'seo'
        : referrer_domain.includes('facebook.') || referrer_domain.includes('instagram.') || referrer_domain.includes('tiktok.') ? 'social'
        : 'referral'
      )
    : 'direct';

  // Landing path should be first page in the session
  const landing_path = window.location.pathname;

  posthog!.register({
    app_env: process.env.NEXT_PUBLIC_APP_ENV ?? 'prod',
    platform: 'web',
    landing_path,
    referrer_domain,
    traffic_source,
    utm_source,
    utm_medium,
    utm_campaign,
    utm_term,
    utm_content,
  });
}
```

**Call this once** on app initialization (e.g., in `_app.tsx` or your root layout). All subsequent `posthog.capture()` calls automatically include these properties.

**Why this matters**: Without session context, funnels and cohorts require per-event property duplication or become unusable for SEO/marketing analysis.

### Pattern 2: Source as Enum (Override Only)

**Problem**: Free text `source` properties drift into garbage: `'SEO'`, `'seo '`, `'organic'`, `'google'`.

```typescript
// ✅ CORRECT: Define source as a strict enum
export type TrafficSource = 'seo' | 'direct' | 'referral' | 'social' | 'internal' | 'paid' | 'email' | 'push';

// Usage: rely on session-level traffic_source by default
function trackReading(readingType: string, sourceOverride?: TrafficSource) {
  const props: Record<string, unknown> = { reading_type: readingType };
  if (sourceOverride) props.source = sourceOverride; // override only when needed
  posthog.capture('generated_reading', props);
}

// ❌ WRONG: Free text allows inconsistency
posthog.capture('generated_reading', { reading_type: 'horoscope', source: 'SEO' });      // Capital
posthog.capture('generated_reading', { reading_type: 'horoscope', source: 'organic' });  // Different word
posthog.capture('generated_reading', { reading_type: 'horoscope', source: 'seo ' });     // Trailing space
```

### Pattern 3: Event Idempotency (Prevent Double-Firing) (VITAL)

**Problem**: In React/Next, effects can run twice in dev and sometimes in prod due to re-renders. Without idempotency, you inflate activation counts.

**Solution**: Enforce dedupe inside the tracking function—not optional, not external.

```typescript
// Dedupe helper: returns false if already fired this session
function dedupeOncePerSession(key: string): boolean {
  try {
    const storageKey = `ph_dedupe_${key}`;
    if (sessionStorage.getItem(storageKey)) return false;
    sessionStorage.setItem(storageKey, '1');
    return true;
  } catch {
    // If sessionStorage is blocked, allow capture rather than lose signal
    return true;
  }
}

// Apply dedupe INSIDE trackReading (not optional)
const trackReading = useCallback(
  (
    readingType: ReadingType,
    properties?: {
      reading_id?: string;
      [key: string]: unknown;
    }
  ) => {
    if (!isPostHogReady()) return;

    const readingId =
      properties?.reading_id ??
      generateReadingId(readingType, posthog!.get_distinct_id?.() ?? undefined);

    // Dedupe: once per session per readingId
    if (!dedupeOncePerSession(`generated_reading_${readingId}`)) return;

    posthog!.capture('generated_reading', {
      reading_type: readingType,
      reading_id: readingId,
      ...properties,
    });
  },
  []
);
```

### Pattern 3a: Reading ID Generation (Critical)

**Rule**: `reading_id` must represent one distinct "value delivered" unit.

Using only `date` can undercount if a user generates multiple readings of the same type on the same day. Add a **variant key** based on your product:

```typescript
// Generate stable reading ID with variant key
function generateReadingId(
  readingType: ReadingType,
  userId: string | undefined,
  variantKey?: string  // Product-specific differentiator
): string {
  const date = new Date().toISOString().split('T')[0];  // YYYY-MM-DD
  const userPart = userId ?? 'anon';

  // Include variant key to distinguish multiple readings of same type
  if (variantKey) {
    return `${readingType}_${userPart}_${date}_${variantKey}`;
  }
  return `${readingType}_${userPart}_${date}`;
}

// Examples by product feature:
// Compatibility reading: normalize if symmetric (A-B == B-A)
const variant = isSymmetric
  ? [sign1, sign2].sort().join('_')
  : `${sign1}_${sign2}`;
generateReadingId('compatibility', userId, variant);

// Ask Cosmos: variant = question_id (hash of question text)
generateReadingId('ask_cosmos', userId, questionId);

// Birth chart: variant = chart_id (hash of birth data)
generateReadingId('chart', userId, chartId);

// Daily horoscope: no variant needed (one per day is correct)
generateReadingId('daily', userId);
```

**Why variant keys matter**: Without them, a user who generates 3 different compatibility readings on the same day counts as 1 activation instead of 3.

### Pattern 3b: Activation vs Paywall Separation (Critical)

If the user sees a limited/locked result, **do not** fire activation. Emit a paywall event with a reason and return early.

```typescript
if (isLimited) {
  posthog.capture('paywall_shown', {
    feature: 'feature_name',
    required_tier: 'pro',
    reason: 'limited_report', // limited_report | quota_reached | trial_expired
  });
  return;
}

posthog.capture('generated_reading', {
  reading_type: 'content',
});
```

### Pattern 3c: Cache vs Fresh (Recommended)

Add a `cached` (or `delivery_type`) flag so repeat views are separable from fresh value delivery.

```typescript
posthog.capture('generated_reading', {
  reading_type: 'content',
  cached: true, // or delivery_type: 'cached' | 'fresh'
});
```

### Pattern 3d: Dwell Engagement Visibility Guard

Only count dwell engagement when the tab is visible, and always clear the timer on unmount.

```typescript
const timer = setTimeout(() => {
  if (document.visibilityState !== 'visible') return;
  posthog.capture('reading_engaged', {
    reading_type: 'content',
    engagement_type: 'dwell_15s',
  });
}, 15000);

return () => clearTimeout(timer);
```

### Pattern 4: Deprecation Strategy

**Problem**: Keeping deprecated events in the type union is fine, but continuing to emit them causes double-counting.

**Rules**:

1. **Do not emit deprecated events in new code** — Comment them as deprecated
2. **Set a cutoff date** — Remove after 14-30 days once dashboards migrate
3. **Never emit both old and new events** — Pick one source of truth

```typescript
// Type union can keep deprecated for backwards compatibility
type AnalyticsEvent =
  | 'generated_reading'           // ✅ Current
  | 'reading_engaged'             // ✅ Current
  // DEPRECATED: Remove after 2026-02-15
  // | 'horoscope_viewed'         // ❌ Replaced by generated_reading
  // | 'chart_viewed'             // ❌ Replaced by generated_reading
  ;

// ❌ WRONG: Emitting both old and new
posthog.capture('generated_reading', { reading_type: 'horoscope' });
posthog.capture('horoscope_viewed');  // Double-counting!

// ✅ CORRECT: Only emit the canonical event
posthog.capture('generated_reading', { reading_type: 'horoscope' });
```

### Pattern 5: Revenue Event Schema

When monetizing, you need ONE canonical revenue event with complete properties.

```typescript
// Canonical revenue event
posthog.capture('purchase_completed', {
  // Required for revenue analytics
  product_id: 'pro_annual',
  plan: 'pro',
  amount: 99.00,
  currency: 'USD',
  billing_period: 'annual',  // 'monthly' | 'annual' | 'lifetime'

  // Attribution
  is_trial_conversion: true,
  trial_duration_days: 7,
  upgrade_source: 'paywall',  // 'paywall' | 'settings' | 'email' | 'limit_reached'

  // Context (from registered session)
  // utm_source, landing_path, etc. auto-attached
});
```

**Do not rely only on `trial_converted`** for revenue. The revenue event needs complete transaction data.

### Pattern 6: Property Naming Consistency

Use `snake_case` for ALL event properties. Never mix conventions.

```typescript
// ✅ CORRECT: Consistent snake_case
{
  reading_type: 'compatibility',
  engagement_type: 'scroll_60',
  required_tier: 'pro',
  step_name: 'onboarding_welcome',
  is_first_use: true,
}

// ❌ WRONG: Mixed conventions
{
  readingType: 'compatibility',    // camelCase
  'step-name': 'welcome',          // kebab-case
  stepName: 'onboarding_welcome',  // camelCase
}
```

---

## Core: Implementation Checklist

Before shipping any activation event, verify:

```markdown
## Activation Event Checklist

### Event Correctness
- [ ] `generated_reading` fires only when reading is **visible** (not on mount)
- [ ] `generated_reading` includes `reading_type`, `reading_id`
- [ ] `reading_id` includes **variant key** for multi-reading scenarios
- [ ] Symmetric variants are **normalized** (e.g., sort pairs) to avoid split cohorts
- [ ] `generated_reading` is **not** fired for limited/locked results
- [ ] `paywall_shown` fires with a `reason` (e.g., `limited_report`, `quota_reached`)
- [ ] `cached` (or `delivery_type`) property distinguishes fresh vs cached reads
- [ ] `dedupeOncePerSession()` is called **inside** the tracking function (mandatory)
- [ ] Event fires in **exactly one place** per feature surface

### Session Context
- [ ] `registerSessionContext()` called on app initialization with:
  - [ ] `app_env` (prod/staging)
  - [ ] `platform` (web)
  - [ ] `landing_path`
  - [ ] `traffic_source` (derived from UTM/referrer)
  - [ ] UTM fields (when present)
  - [ ] `referrer_domain`
- [ ] Traffic source classification is **derived**, not passed manually

### Type Safety
- [ ] `TrafficSource` uses TypeScript enum, not free string
- [ ] All properties use `snake_case`
- [ ] TypeScript types match actual event payloads

### Dedupe Verification
- [ ] Fire event twice in browser console → only one event in PostHog
- [ ] Refresh page → dedupe resets (new session)
- [ ] Different `reading_id` → both events fire

### Engagement
- [ ] Dwell timers check `document.visibilityState === 'visible'`
- [ ] Engagement timers cleared on unmount

### Deprecation
- [ ] Deprecated `*_viewed` events not emitted in new code
- [ ] Cutoff date documented for deprecated event removal

### Privacy
- [ ] Person properties contain **no PII** by default
- [ ] Email only stored with explicit consent + operational need
```

---

## Core: Event Taxonomy Design

A consistent event taxonomy is the foundation of useful analytics. Get this wrong and your data becomes unusable.

### Naming Convention Standards

**Recommended: Object-Action Format**

```text
[object]_[action]

Examples:
- user_signed_up
- project_created
- invite_sent
- subscription_upgraded
- feature_used
```

**For Complex Apps: Category:Object_Action**

```text
[category]:[object]_[action]

Examples:
- onboarding:welcome_modal_viewed
- settings:password_changed
- checkout:payment_submitted
- dashboard:report_exported
```

### Naming Rules (Non-Negotiable)

| Rule | Correct | Incorrect |
|------|---------|-----------|
| **Lowercase only** | `user_signed_up` | `User_Signed_Up` |
| **Snake_case** | `button_clicked` | `button-clicked`, `buttonClicked` |
| **Present tense verbs** | `create`, `submit`, `view` | `created`, `submitted`, `viewed` |
| **User perspective** | `message_sent` (user sent) | Ambiguous: who sent? |
| **No abbreviations** | `subscription_canceled` | `sub_cncld` |

### Property Naming

| Pattern | Example | Use For |
|---------|---------|---------|
| `object_adjective` | `user_id`, `item_price`, `plan_name` | All properties |
| `is_` prefix | `is_subscribed`, `is_trial` | Booleans |
| `has_` prefix | `has_seen_upsell`, `has_completed_onboarding` | Boolean states |
| `_count` suffix | `item_count`, `retry_count` | Integers |
| `_at` / `_date` suffix | `created_at`, `trial_end_date` | Timestamps |
| `_amount` / `_value` suffix | `order_amount`, `discount_value` | Currency |

### Standard Verb Library

Pick from this list and don't deviate:

| Category | Verbs |
|----------|-------|
| **View/Read** | `viewed`, `opened`, `loaded`, `displayed` |
| **Create** | `created`, `added`, `submitted`, `uploaded` |
| **Update** | `updated`, `edited`, `changed`, `modified` |
| **Delete** | `deleted`, `removed`, `canceled`, `archived` |
| **Interact** | `clicked`, `tapped`, `selected`, `toggled` |
| **Convert** | `signed_up`, `subscribed`, `purchased`, `upgraded` |
| **Engage** | `shared`, `invited`, `commented`, `rated` |

---

## Core: Event Categories

Every event should belong to one category. This enables filtering and analysis.

### Marketing Events (Attribution & Acquisition)

| Event | Properties | When to Fire |
|-------|------------|--------------|
| `page_viewed` | `page_url`, `page_title`, `referrer`, `utm_*` | Every page load |
| `campaign_landed` | `utm_source`, `utm_medium`, `utm_campaign`, `utm_content`, `utm_term` | First pageview with UTM |
| `signup_started` | `source`, `referrer`, `landing_page` | Form displayed |
| `signup_completed` | `method` (email/google/github), `source`, `referrer` | Account created |
| `trial_started` | `plan_name`, `source`, `referrer` | Trial begins |
| `demo_requested` | `source`, `company_size`, `use_case` | Demo form submitted |

### Activation Events (Time-to-Value)

| Event | Properties | When to Fire |
|-------|------------|--------------|
| `onboarding_started` | `user_id`, `signup_source` | First login after signup |
| `onboarding_step_completed` | `step_name`, `step_number`, `time_spent` | Each step done |
| `onboarding_completed` | `total_time`, `steps_completed`, `steps_skipped` | All required steps done |
| `feature_first_used` | `feature_name`, `time_since_signup` | First use of key feature |
| `activation_achieved` | `activation_criteria`, `days_since_signup` | User hits activation metric |

### Engagement Events (Product Usage)

| Event | Properties | When to Fire |
|-------|------------|--------------|
| `feature_used` | `feature_name`, `context`, `outcome` | Any feature interaction |
| `session_started` | `session_id`, `return_interval_days` | New session begins |
| `search_performed` | `query`, `results_count`, `filters_applied` | User searches |
| `content_created` | `content_type`, `content_length`, `has_media` | User creates content |
| `collaboration_action` | `action_type`, `collaborator_count` | Team features used |
| `content_engaged` | `content_id`, `engagement_type`, `depth` | User engages with content |

### Engagement Signal Patterns

Pick ONE engagement signal and implement it well. Options:

#### Scroll Depth

```javascript
// Fire when user scrolls past threshold
let hasFiredEngagement = false;

window.addEventListener('scroll', () => {
  if (hasFiredEngagement) return;

  const scrollPercent = (window.scrollY / (document.body.scrollHeight - window.innerHeight)) * 100;

  if (scrollPercent >= 60) {
    posthog.capture('content_engaged', {
      content_id: currentContentId,
      engagement_type: 'scroll_60',
      scroll_depth: Math.round(scrollPercent)
    });
    hasFiredEngagement = true;
  }
});
```

#### Dwell Time

```javascript
// Fire after 15 seconds on page
let hasFiredEngagement = false;
const DWELL_THRESHOLD_MS = 15000;

setTimeout(() => {
  if (!hasFiredEngagement && document.visibilityState === 'visible') {
    posthog.capture('content_engaged', {
      content_id: currentContentId,
      engagement_type: 'dwell_15s',
      time_on_page_seconds: 15
    });
    hasFiredEngagement = true;
  }
}, DWELL_THRESHOLD_MS);
```

#### Section Expand

```javascript
// Fire when user expands a section (accordion, details)
function onSectionExpand(sectionName) {
  posthog.capture('content_engaged', {
    content_id: currentContentId,
    engagement_type: 'expand_section',
    section_name: sectionName
  });
}
```

#### Choose Based on Content Type

| Content Type | Best Engagement Signal |
|--------------|------------------------|
| Long-form articles | Scroll depth (60-80%) |
| Interactive tools | Feature completion |
| Video content | Watch time (50%+) |
| Dashboard/app | Session duration + actions |

### Conversion Events (Revenue)

| Event | Properties | When to Fire |
|-------|------------|--------------|
| `checkout_started` | `plan_name`, `billing_cycle`, `price` | Checkout page loaded |
| `checkout_completed` | `plan_name`, `price`, `payment_method`, `currency` | Payment successful |
| `subscription_upgraded` | `from_plan`, `to_plan`, `price_change` | Plan upgrade |
| `subscription_downgraded` | `from_plan`, `to_plan`, `reason` | Plan downgrade |
| `subscription_canceled` | `plan_name`, `tenure_days`, `reason` | Cancellation |
| `refund_requested` | `order_id`, `amount`, `reason` | Refund initiated |

### Retention Events (Engagement Quality)

| Event | Properties | When to Fire |
|-------|------------|--------------|
| `user_returned` | `days_since_last_visit`, `return_source` | Returning user session |
| `streak_achieved` | `streak_length`, `streak_type` | Usage milestone |
| `notification_clicked` | `notification_type`, `channel` | User returns via notification |
| `churn_risk_signal` | `risk_score`, `days_inactive`, `last_feature_used` | Server-side risk detection |

---

## Core: Tracking Plan Template

Use this structure for your tracking plan document.

### Tracking Plan Structure

```markdown
## Event: [event_name]

**Category**: Marketing | Activation | Engagement | Conversion | Retention
**Priority**: Critical | High | Medium | Low
**Source**: Frontend | Backend | Both
**Owner**: [team/person]

### Description
[One sentence: what action does this represent?]

### When to Fire
[Exact trigger condition]

### Properties

| Property | Type | Required | Description | Example |
|----------|------|----------|-------------|---------|
| user_id | string | Yes | Unique user identifier | "usr_abc123" |
| ... | ... | ... | ... | ... |

### Implementation Notes
[Any special considerations, edge cases, or dependencies]

### Version History
- v1.0 (2026-01-15): Initial implementation
```

### Sample Tracking Plan (SaaS)

See [assets/tracking-plan-saas.md](assets/tracking-plan-saas.md) for a complete SaaS tracking plan template.

---

## Core: Marketing Attribution Setup

### UTM Parameter Standards

| Parameter | Purpose | Example Values |
|-----------|---------|----------------|
| `utm_source` | Traffic source | `google`, `linkedin`, `newsletter`, `partner_acme` |
| `utm_medium` | Marketing medium | `cpc`, `email`, `social`, `referral`, `organic` |
| `utm_campaign` | Campaign name | `spring_launch_2026`, `black_friday`, `product_webinar` |
| `utm_content` | Content variant | `hero_cta`, `sidebar_banner`, `email_header` |
| `utm_term` | Paid keywords | `product_analytics`, `posthog_alternative` |

### UTM Naming Rules

| Rule | Correct | Incorrect |
|------|---------|-----------|
| **Lowercase only** | `utm_source=google` | `utm_source=Google` |
| **Underscores for spaces** | `spring_launch_2026` | `spring-launch-2026`, `spring launch` |
| **No special characters** | `partner_acme` | `partner:acme`, `partner/acme` |
| **Consistent vocabulary** | Always `cpc` for paid | Mixing `cpc`, `paid`, `ppc` |

**Critical**: Inconsistent UTM parameters cause 35% data loss in attribution (Bitly 2024 study).

### First-Touch Attribution Capture

Capture UTM parameters on first visit and persist through signup:

```javascript
// PostHog: Capture UTMs on first pageview
posthog.capture('page_viewed', {
  utm_source: getUrlParam('utm_source'),
  utm_medium: getUrlParam('utm_medium'),
  utm_campaign: getUrlParam('utm_campaign'),
  utm_content: getUrlParam('utm_content'),
  utm_term: getUrlParam('utm_term'),
  referrer: document.referrer,
  landing_page: window.location.pathname
});

// Persist to user properties for attribution
posthog.people.set_once({
  initial_utm_source: getUrlParam('utm_source'),
  initial_utm_medium: getUrlParam('utm_medium'),
  initial_utm_campaign: getUrlParam('utm_campaign'),
  initial_referrer: document.referrer,
  initial_landing_page: window.location.pathname
});
```

### Attribution Models

| Model | Credit Distribution | Best For |
|-------|---------------------|----------|
| **First-touch** | 100% to first interaction | Understanding awareness sources |
| **Last-touch** | 100% to final interaction | Short sales cycles, direct response |
| **Linear** | Equal across all touches | Simple multi-touch view |
| **Time-decay** | More to recent touches | Long sales cycles |
| **Position-based (U-shape)** | 40% first, 40% last, 20% middle | Balanced view |
| **Data-driven** | ML-optimized weights | High volume, sophisticated teams |
| **Probabilistic** | Statistical inference from patterns | Privacy-first, post-cookie |

> **2026 Attribution Reality**: Third-party cookies are dead. Last-click attribution is obsolete. Modern attribution requires: first-party data + probabilistic models + server-side tracking (Meta Conversions API, Google Enhanced Conversions).

### Privacy Sandbox APIs (Post-Cookie Attribution)

> **2026 Reality**: Google has **retired** several Privacy Sandbox technologies—including Attribution Reporting API, IP Protection, and On-Device Personalization—due to low adoption (announced late 2024). The interoperable Attribution standard is being developed through web standards process. CHIPS and FedCM remain supported.

Chrome's Privacy Sandbox introduced replacement technologies, but adoption was limited:

| API | Status (2026) | Notes |
|-----|---------------|-------|
| **Attribution Reporting API** | ❌ Deprecated | Retired due to low adoption |
| **Topics API** | ⚠️ Limited | Broad categories, minimal adoption |
| **Protected Audience API** | ⚠️ Limited | On-device auctions, limited signals |
| **CHIPS** | ✅ Active | Partitioned cookies, broad browser support |
| **FedCM** | ✅ Active | Federated identity, supported cross-browser |

**Practical impact**: Privacy Sandbox did not deliver the cookieless attribution solution originally promised. Plan for:
- **First-party data collection** as primary signal (62% of marketers prioritizing this)
- **Server-side tracking** for critical conversions (Meta CAPI, Google Enhanced Conversions)
- **Probabilistic modeling** to fill gaps
- **Data clean rooms** for cross-channel analysis (e.g., Google Ads Data Hub)
- **User choice reality**: Chrome prompts users with "Privacy Choice"—most opt out, making third-party cookies opt-in for a small audience

> **Note**: For B2B pipeline-focused attribution (MQL/SQL context, lead routing), see [marketing-leads-generation](../marketing-leads-generation/SKILL.md). This section focuses on **technical instrumentation** of attribution data.

### Do (Attribution)

- Capture UTMs server-side (more reliable than client-side)
- Store first-touch AND last-touch attribution
- Ask "How did you hear about us?" in signup (self-reported complements tracked)
- Set up conversion events that tie to revenue

### Avoid (Attribution)

- Inconsistent UTM naming (fragments your data)
- Trusting any single model as "truth"
- Ignoring dark social (word-of-mouth, private shares)
- Not tracking offline touchpoints (events, sales calls)

---

## Core: Activation Metrics Framework

### What Is Activation?

Activation = the moment a user experiences your product's core value for the first time.

**Good activation metrics**:
- Correlate strongly with retention
- Are achievable within first session or week
- Reflect genuine value, not vanity actions

### Defining Your Activation Metric

**Step 1: List candidate actions**

```text
Examples for a project management SaaS:
- Created first project
- Added first task
- Invited first team member
- Completed first task
- Connected first integration
```

**Step 2: Correlate with retention**

For each action, measure: "Do users who complete this action retain better at 30/60/90 days?"

```sql
-- PostHog SQL: Retention correlation
SELECT
  has_created_project,
  COUNT(DISTINCT user_id) as users,
  COUNT(DISTINCT CASE WHEN returned_day_30 THEN user_id END) as retained_30,
  ROUND(100.0 * COUNT(DISTINCT CASE WHEN returned_day_30 THEN user_id END) / COUNT(DISTINCT user_id), 1) as retention_rate
FROM user_activation_analysis
GROUP BY has_created_project
```

**Step 3: Choose the action with highest retention correlation**

| Action | Users | 30-Day Retention | Correlation |
|--------|-------|------------------|-------------|
| Created project | 1,000 | 45% | High |
| Added task | 800 | 52% | Higher |
| Invited team member | 300 | 68% | **Highest** |

→ "Invited first team member" is likely your activation metric.

### Activation Metric Examples by Product Type

| Product Type | Typical Activation Metric |
|--------------|---------------------------|
| **SaaS (B2B)** | Invited team member, completed key workflow |
| **E-commerce** | Made first purchase, added to wishlist |
| **Social/Community** | Made first post, followed 5 users |
| **Content/Media** | Consumed 3 pieces of content, subscribed |
| **Developer tools** | Deployed first project, made first API call |
| **Analytics** | Created first dashboard, shared first insight |

### Measuring Time-to-Activation

```text
Metric: Time from signup to activation event
Target: Reduce by 20% quarter-over-quarter

Breakdown:
- Median time to activation: 2.5 days
- Top 25% activate within: 4 hours
- Bottom 25% activate after: 7+ days (at-risk)
```

---

## Core: Retention Analysis

### Cohort Retention Table

The foundational view for understanding retention:

```text
              Week 0   Week 1   Week 2   Week 3   Week 4
Cohort A      100%     45%      32%      28%      25%
Cohort B      100%     48%      35%      30%      27%
Cohort C      100%     52%      40%      35%      32%
```

### Retention Curve Health

| Pattern | Diagnosis | Action |
|---------|-----------|--------|
| **Flattens after Week 2** | Healthy: Core users found | Focus on acquisition |
| **Keeps declining** | Product/market fit issue | Improve activation, core value |
| **Uptick at Week 4** | Re-engagement working | Double down on win-back |
| **Flat from Day 1** | Wrong users or weak activation | Fix acquisition targeting |

### Retention Benchmarks (2025)

| Timeframe | Median | Good | Great |
|-----------|--------|------|-------|
| **Day 1** | 25% | 35% | 45%+ |
| **Day 7** | 15% | 20% | 30%+ |
| **Day 30** | 8% | 12% | 20%+ |
| **Day 90** | 4% | 7% | 12%+ |

Source: Amplitude Product Benchmark Report 2025

### Stickiness Ratio (DAU/MAU)

Measures how often monthly users return daily:

| Ratio | Interpretation |
|-------|----------------|
| 5-10% | Low engagement (monthly tools) |
| 10-20% | Moderate (weekly workflows) |
| 20-30% | Good (regular use) |
| 30%+ | Excellent (daily habit) |

---

## Platform: PostHog Setup

PostHog is an open-source, all-in-one product analytics platform. Recommended for technical teams who want control and cost efficiency.

### Core Setup

```javascript
// Initialize PostHog
posthog.init('YOUR_PROJECT_API_KEY', {
  // Cloud default is `https://us.i.posthog.com` (set explicitly for EU/self-hosted/proxy)
  api_host: 'https://us.i.posthog.com', // e.g. `https://eu.i.posthog.com` (EU) or your proxy/self-hosted URL
  autocapture: true,
  capture_pageview: true,
  capture_pageleave: true,
  persistence: 'localStorage+cookie',
  loaded: function(posthog) {
    // Identify user when logged in
    if (currentUser) {
      posthog.identify(currentUser.id, {
        // Prefer non-PII, state-based properties
        plan: currentUser.plan,
        signup_date: currentUser.createdAt,
        onboarding_completed: currentUser.onboardingCompleted === true
      });
    }
  }
});
```

### Autocapture vs Custom Events

| Use Autocapture For | Use Custom Events For |
|---------------------|----------------------|
| General click patterns | Key conversion moments |
| Exploring user behavior | Revenue events |
| Finding unknown friction | Activation metrics |
| Early discovery phase | Business-critical tracking |

### PostHog Custom Event Example

```javascript
// Track activation event
posthog.capture('activation_achieved', {
  activation_criteria: 'invited_team_member',
  days_since_signup: 2,
  team_size: 3,
  plan: 'trial'
});

// Track conversion with revenue
posthog.capture('subscription_started', {
  plan_name: 'pro',
  billing_cycle: 'annual',
  price: 199,
  currency: 'USD',
  payment_method: 'stripe'
});
```

### PostHog Actions (Combining Events)

Group autocaptured events into meaningful actions:

```text
Action: "Started Checkout"
Matches:
- pageview where URL contains "/checkout"
- OR autocapture where element text = "Start checkout"
- OR custom event "checkout_started"
```

### PostHog Feature Flags + Analytics

```javascript
// Check flag and track exposure
if (posthog.isFeatureEnabled('new_onboarding_flow')) {
  posthog.capture('feature_flag_exposure', {
    flag_name: 'new_onboarding_flow',
    variant: posthog.getFeatureFlag('new_onboarding_flow')
  });
  showNewOnboarding();
} else {
  showOldOnboarding();
}
```

### PostHog Session Replay Integration

Session replay automatically connects to your events:

- Filter recordings by event (show me sessions with "checkout_abandoned")
- Jump to moment when event fired
- Identify rage clicks and friction patterns

### PostHog Revenue Analytics (Beta)

```javascript
// Track revenue for lifetime value analysis
posthog.capture('purchase_completed', {
  revenue: 99.00,
  currency: 'USD',
  item_count: 1,
  order_id: 'ord_123'
});
```

For complete PostHog setup, see [references/posthog-implementation.md](references/posthog-implementation.md).

### PostHog: Core Artifacts to Build

Once events flow in, build these artifacts in PostHog:

#### Must-Have Funnels

```text
Funnel 1: Acquisition → Activation
Steps: $pageview → [your_activation_event]
Purpose: What % of visitors activate?

Funnel 2: Activation → Engagement
Steps: [your_activation_event] → [your_engagement_event]
Purpose: Do activated users engage?

Funnel 3: Engagement → Conversion (if applicable)
Steps: [your_engagement_event] → checkout_completed
Purpose: Does engagement lead to revenue?
```

#### Must-Have Retention Report

```text
Retention: Weekly for activated users
Cohort: Users who did [your_activation_event]
Return event: Any event OR [your_engagement_event]
Time period: Weekly, 8 weeks

What to look for:
- Week 1 retention > 30% = healthy
- Curve flattens by Week 3-4 = core users exist
- Keeps declining = product/market fit issue
```

#### Must-Have Cohort

```text
Cohort: "Activated but not engaged"
Definition: Did [activation_event] AND NOT [engagement_event] within 7 days
Purpose: Target for re-engagement campaigns
```

#### Dashboard: SEO to Value (4-6 cards max)

| Card | Metric | Purpose |
|------|--------|---------|
| Visitors | Unique $pageview by day | Acquisition volume |
| Activation Rate | [activation] / $pageview | Value delivery |
| Engagement Rate | [engagement] / [activation] | Stickiness |
| Top Landing Pages | $pageview breakdown by page | SEO performance |
| Source Breakdown | $pageview by utm_source | Channel performance |
| Week-over-Week Retention | Retention % | Product health |

---

## Platform: Pendo Setup

Pendo excels at combining analytics with in-app guidance. Best for product teams who also need user onboarding tools.

### Key Pendo Concepts

| Concept | Description |
|---------|-------------|
| **Features** | Clickable elements on pages (auto-tagged or manual) |
| **Pages** | URL patterns for page-level analytics |
| **Guides** | In-app tooltips, walkthroughs, announcements |
| **Segments** | User groups based on metadata or behavior |

### Pendo Track Events

```javascript
// Custom track event
pendo.track('feature_used', {
  feature_name: 'bulk_export',
  export_format: 'csv',
  row_count: 1500
});
```

### Pendo AI Agent Analytics (2026)

```javascript
// Track AI agent interactions
pendo.track('ai_agent_prompt', {
  agent_name: 'support_assistant',
  prompt_text: 'How do I reset my password?',
  response_time_ms: 1200,
  was_helpful: true,
  escalated_to_human: false
});
```

### Pendo Predict (2025)

Use Pendo Predict for:
- Churn prediction models
- Expansion opportunity scoring
- Health scoring based on usage

For Pendo setup, see [references/pendo-implementation.md](references/pendo-implementation.md).

---

## Platform: Amplitude Setup

Amplitude is the enterprise standard for product analytics. Best for teams needing advanced behavioral analytics and experimentation.

### Amplitude Event Structure

```javascript
// Track event with Amplitude SDK
amplitude.track('subscription_started', {
  plan_name: 'pro',
  billing_cycle: 'annual',
  price: 199,
  currency: 'USD'
});
```

### Amplitude User Properties

```javascript
// Set user properties
amplitude.identify(
  new amplitude.Identify()
    .set('plan', 'pro')
    .set('company_size', '50-100')
    .setOnce('initial_source', 'google_ads')
);
```

### Amplitude Taxonomy (Data Planning)

Amplitude's Data Planning features:
- **Blueprint**: Central source of truth for event definitions
- **Categories**: Group events by type
- **Validation**: Ensure events match schema

For Amplitude setup, see [references/amplitude-implementation.md](references/amplitude-implementation.md).

---

## Platform: Mixpanel Setup

Mixpanel offers powerful funnel and retention analysis with a user-friendly interface.

### Mixpanel Event Structure

```javascript
// Track event
mixpanel.track('feature_used', {
  feature_name: 'dashboard_export',
  export_format: 'pdf',
  time_on_page: 45
});
```

### Mixpanel User Profiles

```javascript
// Set user properties
mixpanel.people.set({
  '$email': 'user@example.com',
  '$name': 'Jane Doe',
  'plan': 'enterprise',
  'company': 'Acme Inc'
});

// Set once (first-touch attribution)
mixpanel.people.set_once({
  'initial_source': 'product_hunt',
  'initial_campaign': 'launch_2026'
});
```

For Mixpanel setup, see [references/mixpanel-implementation.md](references/mixpanel-implementation.md).

---

## Platform: Heap Setup

Heap's autocapture captures everything automatically, reducing instrumentation burden.

### Heap Philosophy

- **Capture everything, analyze later**: No need to define events upfront
- **Retroactive analysis**: Ask questions about past behavior
- **Virtual events**: Define events after the fact from captured data

### When Heap Makes Sense

| Scenario | Heap Fit |
|----------|----------|
| Early-stage, exploring what to track | Excellent |
| Resource-constrained team | Good |
| Need retroactive analysis | Excellent |
| Strict event governance required | Poor |
| High event volume cost concerns | Poor |

For Heap setup, see [references/heap-implementation.md](references/heap-implementation.md).

---

## Platform: LLM Analytics (2025-2026)

Track AI/LLM features as part of product analytics. This is distinct from QA testing harnesses — focus here is on **product metrics for AI-native features**.

### When to Use LLM Analytics

- Tracking AI feature usage (tokens, latency, model versions)
- Measuring AI feature value delivery (completion quality, user satisfaction)
- Cost attribution for AI features
- A/B testing AI model versions

### Core LLM Metrics

| Metric | Description | Target | Why |
|--------|-------------|--------|-----|
| `prompt_tokens` | Input token count | Monitor for cost | Token costs scale linearly |
| `completion_tokens` | Output token count | Monitor for cost | Often 2-3x prompt cost |
| `latency_ms` | Time to first token / total | p95 < 3000ms | UX threshold |
| `model_version` | Model used | Track for regression | Model changes affect quality |
| `success` | Did completion succeed | >99% | Reliability signal |
| `user_rating` | Thumbs up/down if collected | >80% positive | Quality signal |

### PostHog LLM Event Example

```javascript
// Track AI feature completion
posthog.capture('ai_feature_completed', {
  feature_name: 'ai_writing_assistant',
  model: 'gpt-4o',
  prompt_tokens: 150,
  completion_tokens: 400,
  latency_ms: 1200,
  success: true,
  conversation_id: 'conv_abc123',
  user_rating: 'positive'  // if collected
});

// Track AI feature error
posthog.capture('ai_feature_failed', {
  feature_name: 'ai_writing_assistant',
  model: 'gpt-4o',
  error_type: 'rate_limit',  // rate_limit | timeout | invalid_response | context_length
  latency_ms: 30000,
  retry_count: 3
});
```

### LLM Cost Tracking Pattern

```javascript
// Calculate and track cost per interaction
const COST_PER_1K = { 'gpt-4o': { input: 0.005, output: 0.015 } };

function trackLLMCompletion(model, promptTokens, completionTokens, latencyMs, success) {
  const cost = (promptTokens / 1000) * COST_PER_1K[model].input +
               (completionTokens / 1000) * COST_PER_1K[model].output;

  posthog.capture('ai_feature_completed', {
    model,
    prompt_tokens: promptTokens,
    completion_tokens: completionTokens,
    total_tokens: promptTokens + completionTokens,
    estimated_cost_usd: Math.round(cost * 10000) / 10000,  // 4 decimal places
    latency_ms: latencyMs,
    success
  });
}
```

### LLM Dashboard Cards

| Card | Metric | Purpose |
|------|--------|---------|
| AI Feature Usage | Count of `ai_feature_completed` | Adoption |
| Token Consumption | Sum of `total_tokens` by day | Cost monitoring |
| Latency p95 | 95th percentile `latency_ms` | Performance |
| Success Rate | `success=true` / total | Reliability |
| User Satisfaction | `user_rating=positive` % | Quality |
| Cost per User | `estimated_cost_usd` / unique users | Unit economics |

### LLM Observability Platforms (Advanced)

For production AI features, consider dedicated LLM observability alongside product analytics:

| Platform | Strength | Integration |
|----------|----------|-------------|
| **Datadog LLM Observability** | Enterprise, full APM integration | SDK + agent |
| **Langfuse** | Open-source, detailed traces | SDK |
| **Arize** | ML-focused, drift detection | SDK |
| **Braintrust** | Eval-focused, cost analytics | SDK |

These complement PostHog by providing deeper LLM-specific traces (prompt/completion inspection, chain visualization). Use product analytics for business metrics, LLM observability for debugging.

**Note**: For LLM agent QA testing and evaluation harnesses, see [qa-agent-testing](../qa-agent-testing/SKILL.md).

---

## Quick Reference

| Task | Template | Location |
|------|----------|----------|
| Event naming | Naming conventions | See Core: Event Taxonomy Design |
| Tracking plan | Full tracking plan | `assets/tracking-plan-saas.md` |
| Marketing events | Event library | `assets/marketing-event-library.md` |
| UTM standards | UTM naming guide | `assets/utm-naming-standards.md` |
| Activation setup | Activation metrics | `assets/activation-metrics-template.md` |
| PostHog config | Implementation guide | `references/posthog-implementation.md` |
| Data quality | QA checklist | `assets/analytics-qa-checklist.md` |

---

## Decision Tree (Analytics Triage)

```text
### Not seeing expected events?
├─ Are PostHog default events visible? (e.g. $pageview, autocapture)
│   ├─ Yes → SDK works → likely a custom-event firing bug
│   │   ├─ Trace the render path (route → component) and confirm the event is instrumented in the component actually used
│   │   ├─ Check gating conditions (loading/error/data) + `isPostHogReady()` guard (event may be skipped silently)
│   │   ├─ Next.js App Router: ensure tracking runs in a Client Component (`"use client"`)
│   │   └─ Check dedupe (sessionStorage). New Incognito / clear `ph_dedupe_*` keys to re-fire
│   └─ No → SDK not sending → config/transport issue
│       ├─ Check env vars are set in the deployed environment (Next.js bakes them at build time)
│       ├─ Check DNT/consent/opt-out settings (respect_dnt can disable capture)
│       └─ Check ad blockers / tracking prevention → reverse proxy or server-side tracking
├─ Check implementation
│   └─ Use browser DevTools Network tab to verify `/e/` ingest calls and payload
├─ Check PostHog UI visibility
│   └─ Use PostHog **Live Events**; widen time range; disable “Filter out internal and test users” while debugging
├─ Check event naming
│   └─ Case sensitivity matters: "User_Signup" ≠ "user_signup"
└─ Check user identification
    └─ Ensure posthog.identify() called after login

### Too many events / noisy data?
├─ Autocapture too broad
│   └─ Add ph-no-capture class to irrelevant elements
├─ Internal traffic included
│   └─ Filter by internal email domains or IP ranges
├─ Bot traffic
│   └─ Filter known bot user agents
└─ Duplicate events
    └─ Check for both frontend + backend firing same event

### Can't answer business questions?
├─ Missing events
│   └─ Add custom events for key moments
├─ Missing properties
│   └─ Enrich events with context (user plan, feature name)
├─ No user identification
│   └─ Implement proper identify() calls
└─ Attribution gaps
    └─ Capture UTMs on first touch, persist through signup

### Low activation rate?
├─ Activation metric wrong
│   └─ Validate correlation with retention
├─ Onboarding friction
│   └─ Use session replay to identify drop-off points
├─ Time-to-value too long
│   └─ Streamline path to activation event
└─ Wrong users
    └─ Check acquisition channels for ICP fit
```

---

## Operational SOPs

### Weekly Analytics Review (30 minutes)

1. **Check data quality**
   - Any spike/drop in event volume? (instrumentation issue?)
   - Any new "unknown" events appearing?

2. **Review key metrics**
   - Signup → Activation conversion rate
   - Week-over-week retention
   - Top acquisition sources

3. **Identify anomalies**
   - Unusual patterns in funnels
   - New friction points

### Monthly Analytics Audit (2 hours)

1. **Event coverage review**
   - Are all critical user journeys instrumented?
   - Any new features missing tracking?

2. **Data quality check**
   - Sample 20 events, verify properties are correct
   - Check for duplicate or inconsistent events

3. **Tracking plan update**
   - Document any new events added
   - Deprecate unused events
   - Update event descriptions

4. **Attribution review**
   - Check UTM consistency across campaigns
   - Review channel performance

### Quarterly Taxonomy Review

Bring together PMs, engineers, and analysts to:
- Surface edge cases and naming drift
- Align on new event categories
- Update documentation
- Plan instrumentation for next quarter's features

---

## Data Quality Checklist

Before shipping any analytics implementation:

- [ ] **Event names follow convention** (lowercase, snake_case, present tense)
- [ ] **Required properties present** (user_id, timestamp, event-specific props)
- [ ] **Property types correct** (strings vs numbers vs booleans)
- [ ] **User identification working** (anonymous → identified linking)
- [ ] **UTM capture tested** (all 5 parameters)
- [ ] **First-touch attribution persisted** (survives page refresh)
- [ ] **Internal users filtered** (test accounts, employee traffic)
- [ ] **Ad blockers handled** (reverse proxy or server-side)
- [ ] **Events fire once** (no duplicate counting)
- [ ] **Sensitive data excluded** (no PII in event properties)

---

## Validation Workflow

Never trust charts until you pass these checks.

### Manual Validation (Before Deploy)

1. **Event appears in PostHog Live Events** within seconds of action (Explore/Activity can lag)
2. **Properties are present** and correctly typed
3. **Event volume matches reality** (spot-check counts)
4. **Funnel behaves sensibly**:
   - `$pageview` → `activation_event` should NOT be 0%
   - It should NOT be ~100% either
   - Expect 5-40% depending on your product

### CI Regression Guard

Add automated checks to catch instrumentation breakage:

```yaml
# .github/workflows/analytics-check.yml
name: Analytics Regression Check

on:
  schedule:
    - cron: '0 9 * * *'  # Daily at 9am

jobs:
  check-events:
    runs-on: ubuntu-latest
    steps:
	      - name: Check critical events exist
	        run: |
	          # Query PostHog API for yesterday's events
	          YESTERDAY=$(date -d 'yesterday' +%Y-%m-%d)
	          POSTHOG_UI_HOST=${POSTHOG_UI_HOST:-https://us.posthog.com} # e.g. https://eu.posthog.com

	          # Check activation events > 0
	          ACTIVATION_COUNT=$(curl -s -H "Authorization: Bearer $POSTHOG_PERSONAL_API_KEY" \
	            "$POSTHOG_UI_HOST/api/projects/$POSTHOG_PROJECT_ID/events?event=your_activation_event&after=$YESTERDAY" \
	            | jq '.results | length')

          if [ "$ACTIVATION_COUNT" -eq 0 ]; then
            echo "ALERT: No activation events yesterday!"
            exit 1
          fi

          echo "Activation events: $ACTIVATION_COUNT"
	        env:
	          POSTHOG_PERSONAL_API_KEY: ${{ secrets.POSTHOG_PERSONAL_API_KEY }} # PostHog Personal API key (not the Project API key)
	          POSTHOG_PROJECT_ID: ${{ secrets.POSTHOG_PROJECT_ID }}
	          POSTHOG_UI_HOST: ${{ secrets.POSTHOG_UI_HOST }} # optional: https://eu.posthog.com
```

### Alert Conditions

| Condition | Severity | Action |
|-----------|----------|--------|
| Critical event count = 0 | High | Immediate investigation |
| Event count drops >50% day-over-day | Medium | Review recent deploys |
| New unknown event appears | Low | Check for typos, add to tracking plan |
| Funnel conversion drops >20% | Medium | Check for broken flows |

---

## Session Replay Workflow

Session replay is your qualitative complement to quantitative data.

### Weekly Session Review (30 minutes)

**Watch 20 sessions of activated users and document 5 issues.**

#### How to Filter Sessions

In PostHog Session Recordings:

1. Filter by: `activation_event` performed = true
2. Sort by: Most recent
3. Watch 20 recordings, take notes

#### What to Look For

| Signal | What It Means | Action |
|--------|---------------|--------|
| Rage clicks | User frustrated, element not responding | Fix interaction or feedback |
| Dead clicks | User expects clickable, nothing happens | Add interactivity or visual cue |
| Backtracking | User lost, went back multiple times | Improve navigation or copy |
| Long pauses | User confused or distracted | Simplify flow or add guidance |
| Form abandonment | Friction in conversion | Reduce fields or add progress |

#### Session Review Template

```markdown
## Session Review - [Date]

### Sessions Watched: 20
### Activation Rate in Sample: X%

### Issues Found:

1. **Issue**: [Description]
   - **Sessions affected**: 3/20
   - **Severity**: High/Medium/Low
   - **Recommendation**: [Fix]

2. **Issue**: [Description]
   ...

### Patterns Observed:
- Most users [behavior]
- Drop-off commonly at [step]
- Successful users tend to [behavior]

### Action Items:
- [ ] Fix issue #1 (owner: @name)
- [ ] Investigate issue #2
```

### Connecting Replays to Events

Use events to find specific moments:

```text
"Show me sessions where checkout_abandoned happened"
"Show me sessions where activation_achieved took > 7 days"
"Show me sessions with rage_click events"
```

---

## Anti-Patterns Summary

| Anti-Pattern | Why It Fails | Instead |
|--------------|--------------|---------|
| **No North Star event** | Funnels fragment, retention meaningless | Define ONE canonical activation event |
| **Excessive `*_viewed` events** | Tracks UI states, not outcomes | Collapse into one event with properties |
| **Mixed lifecycle layers** | Dashboards become confusing | Separate auth/onboarding/features/subscription |
| **Manual derived metrics** | Redundant, error-prone | Let PostHog derive retention/engagement |
| **PII in identify()** | GDPR risk, compliance burden | State-based identification, no email/name |
| **Event spam from re-renders** | Inflated counts, bad data | Use `isPostHogReady()` guard + dedupe |
| **Incomplete readiness guard** | Silently drops early events | Check `typeof posthog.capture === 'function'` |
| **No session context** | Funnels unusable for SEO analysis | Use `registerSessionContext()` on first load |
| **Free text source** | Values drift: 'SEO', 'seo ', 'organic' | Use TypeScript enum for `TrafficSource` |
| **Optional dedupe** | Dedupe not enforced, counts inflate | Enforce `dedupeOncePerSession()` inside track fn |
| **Date-only reading_id** | Undercounts multi-reading days | Add variant key to reading_id |
| **Emitting deprecated events** | Double-counting in dashboards | Stop emitting, set 14-30 day cutoff |
| **Mixed property naming** | `stepName` vs `step_name` fragments | Use `snake_case` for ALL properties |
| **Tracking everything** | Data noise, high costs, analysis paralysis | Focus on 5-15 key events (MVA) |
| **Inconsistent naming** | "signup_completed" vs "Signup_Complete" | Enforce naming convention strictly |
| **No tracking plan** | Random instrumentation, duplicate events | Document before implementing |
| **Frontend-only tracking** | Ad blockers block 20-40% of events | Use server-side for critical events |
| **UTM chaos** | Attribution data is useless | Enforce UTM naming standards |
| **Tracking in unused component** | Refactors silently drop key events | Trace route → component, instrument where it renders |

See **Core: Event Quality Rules** and **Core: Production Hardening Patterns** sections above for detailed examples and fixes.

---

## Templates

| Template | Purpose |
|----------|---------|
| [tracking-plan-saas.md](assets/tracking-plan-saas.md) | Complete SaaS tracking plan |
| [marketing-event-library.md](assets/marketing-event-library.md) | Marketing attribution events |
| [utm-naming-standards.md](assets/utm-naming-standards.md) | UTM parameter guide |
| [activation-metrics-template.md](assets/activation-metrics-template.md) | Activation metric definition |
| [analytics-qa-checklist.md](assets/analytics-qa-checklist.md) | Data quality checklist |
| [cohort-retention-template.md](assets/cohort-retention-template.md) | Retention analysis template |

---

## References

| Resource | Purpose |
|----------|---------|
| [posthog-implementation.md](references/posthog-implementation.md) | PostHog setup and configuration |
| [pendo-implementation.md](references/pendo-implementation.md) | Pendo setup guide |
| [amplitude-implementation.md](references/amplitude-implementation.md) | Amplitude configuration |
| [mixpanel-implementation.md](references/mixpanel-implementation.md) | Mixpanel setup |
| [heap-implementation.md](references/heap-implementation.md) | Heap autocapture guide |
| [server-side-tracking.md](references/server-side-tracking.md) | Backend event implementation |
| [privacy-compliance.md](references/privacy-compliance.md) | GDPR/CCPA tracking compliance |

---

## Data Sources

See [data/sources.json](data/sources.json) for official documentation links.

---

## Related Skills

- [marketing-cro](../marketing-cro/SKILL.md) — A/B testing and conversion optimization (uses analytics data)
- [marketing-leads-generation](../marketing-leads-generation/SKILL.md) — Lead funnel tracking and B2B attribution context
- [qa-agent-testing](../qa-agent-testing/SKILL.md) — LLM agent QA harnesses, scoring rubrics, regression testing (complements AI feature analytics)
- [data-sql-optimization](../data-sql-optimization/SKILL.md) — SQL for analytics queries
- [ops-devops-platform](../ops-devops-platform/SKILL.md) — Reverse proxy setup for tracking reliability
- [software-frontend](../software-frontend/SKILL.md) — Frontend SDK implementation

---

## Usage Notes (Claude)

- **Always ask for the North Star event first** — Before designing any tracking plan, identify the ONE canonical activation event
- Stay operational: return event schemas, tracking plans, implementation code
- Default to PostHog examples but provide platform-agnostic patterns
- Always include property types and examples
- Emphasize naming conventions—inconsistency is the #1 analytics killer
- **Challenge excessive `*_viewed` events** — Recommend collapsing into one event with properties
- **Warn against PII in identify()** — Recommend state-based identification
- Include server-side tracking recommendation for critical events
- Reference 2025-2026 benchmarks when discussing metrics
- Do not invent specific benchmark numbers; use ranges or cite sources
