# Regional Pricing and Multi-Currency Guide

Strategies for implementing Purchasing Power Parity (PPP) pricing, multi-currency support, tax compliance, fraud prevention, and revenue analytics for global SaaS products.

---
## Table of Contents

- [Overview](#overview)
- [Purchasing Power Parity (PPP)](#purchasing-power-parity-ppp)
- [What PPP Is](#what-ppp-is)
- [PPP Data Sources](#ppp-data-sources)
- [PPP Discount Tiers](#ppp-discount-tiers)
- [Implementation Strategy](#implementation-strategy)
- [Multi-Currency with Stripe](#multi-currency-with-stripe)
- [Price Objects Per Currency](#price-objects-per-currency)
- [Stripe Auto-Conversion vs Explicit Prices](#stripe-auto-conversion-vs-explicit-prices)
- [Country Detection](#country-detection)
- [Detection Methods](#detection-methods)
- [Implementation](#implementation)
- [Tax Implications](#tax-implications)
- [Tax by Region](#tax-by-region)
- [Tax Handling Options](#tax-handling-options)
- [Currency Display and Formatting](#currency-display-and-formatting)
- [Locale-Aware Currency Formatting](#locale-aware-currency-formatting)
- [Display Examples](#display-examples)
- [Fraud Prevention for Regional Pricing](#fraud-prevention-for-regional-pricing)
- [Common Abuse Vectors](#common-abuse-vectors)
- [Mitigation Strategies](#mitigation-strategies)
- [Prevention Checklist](#prevention-checklist)
- [A/B Testing Pricing Across Regions](#ab-testing-pricing-across-regions)
- [Testing Framework](#testing-framework)
- [Metrics to Track](#metrics-to-track)
- [Statistical Significance](#statistical-significance)
- [Revenue Analytics with Multi-Currency](#revenue-analytics-with-multi-currency)
- [Normalisation Strategy](#normalisation-strategy)
- [Dashboard Considerations](#dashboard-considerations)
- [Anti-Patterns](#anti-patterns)
- [See Also](#see-also)


## Overview

Regional pricing adjusts what customers pay based on their location and local purchasing power. A customer in India should not pay the same absolute price as a customer in the US for the same digital product. Implementing this correctly increases total revenue by expanding addressable markets while maintaining willingness-to-pay in high-income markets.

---

## Purchasing Power Parity (PPP)

### What PPP Is

PPP measures how much a basket of goods costs in different countries relative to a base currency. A product priced at $10/month in the US might have a PPP-equivalent of $3/month in India.

### PPP Data Sources

| Source | Data Type | Update Frequency | Access |
|--------|-----------|-----------------|--------|
| **World Bank ICP** | Official PPP conversion factors | Annual | Free API |
| **OECD PPP** | PPP for GDP and consumption | Annual | Free |
| **Big Mac Index** | Informal PPP indicator | Semi-annual | Free (The Economist) |
| **Numbeo** | Cost of living index | Continuous | API (paid) |
| **Purchasing Power Parity API** | Developer-focused PPP data | Continuous | Free tier available |

### PPP Discount Tiers

```typescript
// Tier-based PPP pricing (recommended over continuous PPP)
export const PPP_TIERS = {
  TIER_0: {
    name: 'Full Price',
    discount: 0,
    countries: ['US', 'CA', 'GB', 'DE', 'FR', 'AU', 'JP', 'CH', 'NO', 'SE', 'DK', 'NL', 'AT', 'BE', 'FI', 'IE', 'SG', 'NZ'],
  },
  TIER_1: {
    name: 'Moderate Discount',
    discount: 0.30, // 30% off
    countries: ['ES', 'IT', 'PT', 'KR', 'CZ', 'PL', 'CL', 'CR', 'UY'],
  },
  TIER_2: {
    name: 'Significant Discount',
    discount: 0.50, // 50% off
    countries: ['BR', 'MX', 'CO', 'AR', 'TH', 'MY', 'ZA', 'RO', 'BG', 'HU'],
  },
  TIER_3: {
    name: 'Emerging Market',
    discount: 0.65, // 65% off
    countries: ['IN', 'ID', 'PH', 'VN', 'EG', 'NG', 'PK', 'BD', 'KE', 'ET', 'GH', 'TZ'],
  },
} as const;

export function getPPPTier(countryCode: string): typeof PPP_TIERS[keyof typeof PPP_TIERS] {
  for (const tier of Object.values(PPP_TIERS)) {
    if (tier.countries.includes(countryCode)) return tier;
  }
  return PPP_TIERS.TIER_0; // Default: full price
}
```

### Implementation Strategy

```text
Two approaches:

1. Multiple Stripe Price Objects (recommended)
   - Create separate Price objects for each tier
   - pros: Clean reporting, no coupon complexity
   - cons: More Price objects to manage

2. Single Price + Automatic Discount
   - One base price, apply PPP coupon at checkout
   - pros: Fewer objects to manage
   - cons: Revenue reporting requires coupon filtering
```

---

## Multi-Currency with Stripe

### Price Objects Per Currency

```typescript
// Create Stripe prices for each currency/tier combination
const PRICE_CONFIG: Record<string, Record<string, { amount: number; currency: string }>> = {
  starter_monthly: {
    default:  { amount: 999,  currency: 'usd' },
    eur:      { amount: 899,  currency: 'eur' },
    gbp:      { amount: 799,  currency: 'gbp' },
    inr:      { amount: 29900, currency: 'inr' }, // ~$3.59
    brl:      { amount: 2990, currency: 'brl' },  // ~$4.99
  },
  pro_monthly: {
    default:  { amount: 2999, currency: 'usd' },
    eur:      { amount: 2699, currency: 'eur' },
    gbp:      { amount: 2399, currency: 'gbp' },
    inr:      { amount: 89900, currency: 'inr' }, // ~$10.79
    brl:      { amount: 8990, currency: 'brl' },  // ~$14.99
  },
};

// Resolve price ID based on country
export function resolvePriceId(
  tier: PaidTier,
  interval: BillingInterval,
  countryCode: string,
): string {
  const pppTier = getPPPTier(countryCode);
  const currencyOverride = COUNTRY_CURRENCY_MAP[countryCode];
  const key = `${tier}_${interval}`;

  // Look up the appropriate pre-created Stripe Price ID
  return STRIPE_PRICE_IDS[key][pppTier.name] || STRIPE_PRICE_IDS[key]['default'];
}
```

### Stripe Auto-Conversion vs Explicit Prices

| Approach | How | Pros | Cons |
|----------|-----|------|------|
| **Explicit prices** | Create Price per currency | Precise control, round numbers | More objects to manage |
| **Stripe auto-conversion** | Single USD price, Stripe converts | Simple setup | Odd amounts ($9.99 → $13.27 AUD), exchange rate fluctuation |
| **Hybrid** | Explicit for top markets, auto for rest | Balance control vs effort | Two systems to maintain |

**Recommendation**: Use explicit prices for your top 5-10 markets, auto-conversion for the rest.

---

## Country Detection

### Detection Methods

| Method | Accuracy | Latency | VPN-Resistant | Implementation |
|--------|----------|---------|---------------|---------------|
| **Vercel headers** | High | 0ms | Moderate | `x-vercel-ip-country` |
| **Cloudflare headers** | High | 0ms | Moderate | `CF-IPCountry` |
| **GeoIP service** | High | 10-50ms | Moderate | MaxMind, IP2Location |
| **User preference** | Perfect | 0ms | Yes | User selects country |
| **Billing address** | Perfect | N/A | Yes | From payment method |
| **Accept-Language** | Low | 0ms | Yes | Browser header (infers, not detects) |

### Implementation

```typescript
// Server-side country detection with fallback chain
export function detectCountry(request: NextRequest): string {
  // 1. User override (stored preference)
  const userCountry = request.cookies.get('user_country')?.value;
  if (userCountry && isValidCountryCode(userCountry)) return userCountry;

  // 2. CDN header (Vercel)
  const vercelCountry = request.headers.get('x-vercel-ip-country');
  if (vercelCountry && isValidCountryCode(vercelCountry)) return vercelCountry;

  // 3. Cloudflare header
  const cfCountry = request.headers.get('cf-ipcountry');
  if (cfCountry && isValidCountryCode(cfCountry)) return cfCountry;

  // 4. Default
  return 'US';
}

// Let users override detected country
export function PricingPage() {
  const [country, setCountry] = useState(detectedCountry);

  return (
    <div>
      <CountrySelector
        value={country}
        onChange={(code) => {
          setCountry(code);
          setCookie('user_country', code, { maxAge: 365 * 24 * 60 * 60 });
        }}
      />
      <PricingTable country={country} />
    </div>
  );
}
```

---

## Tax Implications

### Tax by Region

| Region | Tax Type | Rate Range | Who Collects |
|--------|----------|-----------|--------------|
| **US** | Sales tax | 0-10.25% | Varies by state (nexus rules) |
| **EU** | VAT | 17-27% | Seller (or MoR) |
| **UK** | VAT | 20% | Seller (or MoR) |
| **Canada** | GST/HST/PST | 5-15% | Seller |
| **Australia** | GST | 10% | Seller |
| **India** | GST | 18% | Seller |
| **Japan** | Consumption tax | 10% | Seller |

### Tax Handling Options

| Option | Complexity | Cost | Best For |
|--------|-----------|------|----------|
| **Stripe Tax** | Low | 0.5% per transaction | Self-managed Stripe |
| **Merchant of Record** (Paddle/LemonSqueezy) | Lowest | 5% + 50c (includes tax) | Indie/small SaaS |
| **Tax calculation service** (TaxJar, Avalara) | Medium | Subscription-based | Complex tax needs |
| **Manual** | Highest | Accounting costs | Not recommended |

```typescript
// Stripe Tax integration
const session = await stripe.checkout.sessions.create({
  mode: 'subscription',
  line_items: [{ price: priceId, quantity: 1 }],
  automatic_tax: { enabled: true }, // Stripe calculates and collects tax
  customer_update: {
    address: 'auto', // Update customer address from checkout
  },
  // ...
});
```

---

## Currency Display and Formatting

### Locale-Aware Currency Formatting

```typescript
// Always use Intl.NumberFormat for currency display
export function formatPrice(
  amount: number,       // In smallest currency unit (cents)
  currency: string,     // ISO 4217 code
  locale?: string,      // BCP 47 locale
): string {
  const displayAmount = getDisplayAmount(amount, currency);

  return new Intl.NumberFormat(locale || 'en-US', {
    style: 'currency',
    currency: currency.toUpperCase(),
    minimumFractionDigits: isZeroDecimalCurrency(currency) ? 0 : 2,
    maximumFractionDigits: isZeroDecimalCurrency(currency) ? 0 : 2,
  }).format(displayAmount);
}

function getDisplayAmount(amount: number, currency: string): number {
  return isZeroDecimalCurrency(currency) ? amount : amount / 100;
}

// Stripe zero-decimal currencies
const ZERO_DECIMAL_CURRENCIES = new Set([
  'bif', 'clp', 'djf', 'gnf', 'jpy', 'kmf', 'krw', 'mga',
  'pyg', 'rwf', 'ugx', 'vnd', 'vuv', 'xaf', 'xof', 'xpf',
]);

function isZeroDecimalCurrency(currency: string): boolean {
  return ZERO_DECIMAL_CURRENCIES.has(currency.toLowerCase());
}
```

### Display Examples

| Locale | Currency | Amount (cents) | Display |
|--------|----------|---------------|---------|
| en-US | USD | 999 | $9.99 |
| de-DE | EUR | 899 | 8,99 EUR |
| ja-JP | JPY | 1500 | 1,500 JPY |
| pt-BR | BRL | 2990 | R$ 29,90 |
| hi-IN | INR | 29900 | 29,900.00 INR |
| ar-SA | SAR | 3750 | 37.50 SAR |

---

## Fraud Prevention for Regional Pricing

### Common Abuse Vectors

| Vector | Description | Detection |
|--------|-------------|-----------|
| **VPN abuse** | User in US uses Indian VPN for lower price | IP vs billing address mismatch |
| **Address spoofing** | Fake billing address in low-tier country | Billing address vs card BIN country |
| **Account sharing** | One PPP subscription shared in high-income country | Usage patterns, concurrent sessions |
| **Coupon stacking** | PPP discount + promotional coupon | Enforce mutual exclusivity |

### Mitigation Strategies

```typescript
// Validate billing country matches pricing country
async function validatePricingEligibility(
  session: Stripe.Checkout.Session,
): Promise<boolean> {
  const pricingCountry = session.metadata?.pricing_country;
  const billingCountry = session.customer_details?.address?.country;
  const cardCountry = session.payment_intent
    ? await getCardCountry(session.payment_intent as string)
    : null;

  // Flag if card country doesn't match pricing country
  if (cardCountry && pricingCountry && cardCountry !== pricingCountry) {
    await flagForReview(session.id, {
      reason: 'country_mismatch',
      pricingCountry,
      billingCountry,
      cardCountry,
    });
    return false; // Block or flag for review
  }

  return true;
}

// Get card issuing country from payment method
async function getCardCountry(paymentIntentId: string): Promise<string | null> {
  const pi = await stripe.paymentIntents.retrieve(paymentIntentId, {
    expand: ['payment_method'],
  });

  const pm = pi.payment_method as Stripe.PaymentMethod;
  return pm?.card?.country || null;
}
```

### Prevention Checklist

```text
Required:
  - Compare card BIN country with pricing tier country
  - Store pricing country in subscription metadata
  - Block coupon stacking with PPP pricing

Recommended:
  - Log IP country at checkout for audit trail
  - Require billing address that matches pricing country
  - Rate limit pricing lookups per IP

Optional:
  - Use IP reputation service (MaxMind, IPQualityScore)
  - Require phone verification for high-discount tiers
  - Manual review for cards from different country than pricing
```

---

## A/B Testing Pricing Across Regions

### Testing Framework

```typescript
// Assign users to pricing experiments by country
interface PricingExperiment {
  id: string;
  name: string;
  countries: string[];
  variants: {
    control: { priceId: string; amount: number };
    treatment: { priceId: string; amount: number };
  };
  allocation: number; // 0-1, percentage in treatment
}

function getPricingVariant(
  experiment: PricingExperiment,
  userId: string,
): 'control' | 'treatment' {
  // Deterministic assignment based on user ID
  const hash = hashString(`${experiment.id}:${userId}`);
  const bucket = (hash % 100) / 100;
  return bucket < experiment.allocation ? 'treatment' : 'control';
}
```

### Metrics to Track

| Metric | Formula | What It Tells You |
|--------|---------|-------------------|
| **Conversion rate** | Signups / Visitors | Does the price point convert? |
| **Revenue per visitor** | Total revenue / Visitors | Net revenue impact |
| **ARPU** | Revenue / Paying users | Average yield per user |
| **LTV** | ARPU x Average lifespan | Long-term value at this price |
| **Churn rate** | Churned / Total | Does price affect retention? |

### Statistical Significance

```text
Pricing A/B tests require larger sample sizes than feature tests
because conversion rate differences are small.

Recommended:
  - Minimum 1,000 visitors per variant per country
  - Run for at least 2 full billing cycles (2 months)
  - Track LTV, not just initial conversion
  - Segment by new vs returning visitors
```

---

## Revenue Analytics with Multi-Currency

### Normalisation Strategy

```typescript
// Always normalise to a base currency for reporting
export async function normaliseRevenue(
  amount: number,
  currency: string,
  targetCurrency: string = 'USD',
): Promise<number> {
  if (currency.toUpperCase() === targetCurrency.toUpperCase()) return amount;

  const rate = await getExchangeRate(currency, targetCurrency);
  return Math.round(amount * rate);
}

// Monthly revenue report
interface RevenueReport {
  period: string;
  totalRevenueUSD: number;
  byCountry: Record<string, {
    revenue: number;
    currency: string;
    revenueUSD: number;
    subscribers: number;
    arpu: number;
  }>;
  byTier: Record<string, {
    subscribers: number;
    mrrUSD: number;
  }>;
}
```

### Dashboard Considerations

| Metric | Display | Notes |
|--------|---------|-------|
| MRR | Always in base currency (USD) | Normalise at time of transaction |
| ARPU by country | Local currency + USD equivalent | Show both for context |
| Conversion by tier | Separate by PPP tier | Don't mix high/low price cohorts |
| Revenue growth | USD-normalised | Exchange rate fluctuation can mask real growth |
| Churn rate | Segment by PPP tier | Different retention patterns by market |

---

## Anti-Patterns

| Anti-Pattern | Problem | Fix |
|-------------|---------|-----|
| Continuous PPP (per-country price) | 200+ prices to manage | Use 3-4 PPP tiers |
| No fraud prevention | Users VPN to get low prices | Validate card BIN vs pricing country |
| Auto-conversion only | Odd price amounts ($13.27) | Use explicit prices for top markets |
| Ignoring zero-decimal currencies | JPY 999 displayed as $9.99 | Check Stripe zero-decimal currency list |
| Same tax treatment everywhere | Non-compliant in many jurisdictions | Use Stripe Tax or MoR |
| Not tracking PPP tier in analytics | Cannot segment revenue by market | Store pricing_country in metadata |
| A/B testing prices for too short | Unreliable results | Run for 2+ billing cycles |

---

---

## App Store Connect + Google Play PPP-Pricing Implementation Mechanics

> Source mechanics derived from [github.com/iosdevmax/ppp-pricing](https://github.com/iosdevmax/ppp-pricing) (MIT).  
> Apple and Google store APIs and the 8x–12x pricing band below are **undocumented / volatile** — verify against current App Store Connect and Play Developer API docs before building.  
> For PPP **strategy** (coefficient tiers, country groupings, business model framing) see [../../startup-business-models/references/ppp-regional-pricing.md](../../startup-business-models/references/ppp-regional-pricing.md).

These mechanics are for teams applying PPP discounts directly through the platform stores rather than through a web paywall. The stores have their own price-point catalogs, versioning requirements, and constraints that are completely separate from Stripe.

---

### iOS / App Store Connect

#### Fetch the Price-Point Catalog Once per Currency

Apple's Subscriptions API exposes the full set of discrete price points per storefront (territory). Many territories share the same currency. The efficient pattern:

1. Fetch the price-point catalog **once per currency**, not once per territory.
2. Build a map of `currency -> [pricePoint]` sorted ascending.
3. For sister territories that share a currency (e.g. most Eurozone countries all use EUR), synthesize their price-point IDs from the same cached list — avoids N redundant API calls.

```text
fetch_price_points(currency='EUR')         # one call for all EUR territories
cache: { EUR: [{id, amount}, ...] }
apply to: DE, FR, IT, ES, NL, AT, BE, FI, PT, ... (all EUR territories)
```

#### The 8x–12x Weekly-to-Yearly Band (Key Undocumented Constraint)

Apple enforces a relationship between your subscription tier prices across billing intervals. Specifically: **a yearly subscription price must fall between 8× and 12× the weekly price** for the same product.

When you apply a PPP coefficient to scale down a yearly price, the naive result may violate this band. Apple's API will reject the price point with a validation error.

**Safe pattern — naive scale → band check → binary-search recovery:**

```text
1. naive_yearly = base_yearly_price * ppp_coefficient
2. lower_bound  = weekly_price * 8
3. upper_bound  = weekly_price * 12

4. if lower_bound <= naive_yearly <= upper_bound:
       use naive_yearly (find nearest price-point in catalog)
   else:
       # Binary-search the sorted price-point catalog
       # for the closest valid price-point within [lower_bound, upper_bound]
       clamped = clamp(naive_yearly, lower_bound, upper_bound)
       price_point = binary_search(catalog, target=clamped)
       use price_point
```

The binary search operates over Apple's **discrete price-point ladder** (the catalog fetched above). You cannot set an arbitrary amount — you must land on an existing price-point ID. The binary-search-to-nearest ensures you stay within the band while picking the closest discrete step.

This band is undocumented in Apple's public docs as of mid-2026. Verify the exact multipliers (8× and 12×) against current App Store Connect API responses before implementing.

#### Snapshot Before Applying

Before writing any price-point changes to App Store Connect:

1. Read the current territory → price-point mapping for all affected territories.
2. Persist it as a snapshot (JSON file or DB row) keyed by timestamp and product ID.
3. Apply the new prices.
4. If a subsequent diff step detects unexpected outcomes, the snapshot is the rollback artifact.

```text
snapshot: { territory: 'IN', product_id: 'pro_yearly', price_point_id: 'ppXXXX', amount_usd_micros: 9990000 }
```

---

### Android / Google Play

#### Get Canonical Currency per Region First

Google Play exposes `convertRegionPrices` (Monetization API) which returns Google's canonical currency assignment per region. Always call this first — do not assume currencies from external sources. Then apply the PPP coefficient to each region's canonical currency amount.

```text
1. convertRegionPrices(base_price)
   -> { 'IN': { currency: 'INR', amount: ... }, 'BR': { currency: 'BRL', amount: ... }, ... }
2. scaled_price[region] = canonical_amount * ppp_coefficient[region]
```

#### Patch `regionalConfigs` Wholesale

A critical implementation constraint: you must patch the entire `regionalConfigs` array in a single write, not update individual regions incrementally. Partial patching is rejected by the API.

Additionally, **you must pass the current `regionsVersion`** (fetched from the subscription resource before the write). Submitting a stale or missing `regionsVersion` causes the patch to be rejected — this is Play's optimistic-locking mechanism for concurrent price edits.

```text
1. GET subscription resource -> capture current regionsVersion
2. Build the full updated regionalConfigs array (all regions, not just changed ones)
3. PATCH with { regionalConfigs: [...all...], regionsVersion: <captured> }
```

#### Snapshot Before Applying

Same principle as iOS: capture the full `regionalConfigs` array from the current subscription resource before making any changes. Store it with timestamp and subscription ID so you have a clean rollback target.

---

### Cross-Platform Operational Pattern

Regardless of platform, apply this sequence before any bulk pricing change:

```text
snapshot  ->  dry-run diff  ->  apply  ->  verify
```

1. **Snapshot**: capture current prices from the live API (not from your local config files — they may be stale).
2. **Dry-run diff**: compute the before/after delta without writing. Log every territory that would change, the old price-point, and the new price-point. The reference repo ships `diff_ios_prices.py` and `diff_android_prices.py` for this step.
3. **Apply**: write the changes to the store API.
4. **Verify**: re-read prices from the API and confirm they match the expected post-change state.

Never skip the diff step on bulk PPP reruns (e.g. after annual coefficient updates). Store APIs occasionally reject individual territories silently — the verify step catches partial failures.

---

## See Also

- [subscription-lifecycle.md](subscription-lifecycle.md) — Subscription states, upgrades, dunning
- [stripe-patterns.md](stripe-patterns.md) — Checkout session creation, price ID resolution
- [webhook-reliability-patterns.md](webhook-reliability-patterns.md) — Webhook handling for payment events
- [testing-patterns.md](testing-patterns.md) — Testing regional pricing flows
- [platform-comparison.md](platform-comparison.md) — MoR platforms that handle tax automatically
- [storekit2-native-patterns.md](storekit2-native-patterns.md) — StoreKit 2 subscription and purchase flows
- [../../startup-business-models/references/ppp-regional-pricing.md](../../startup-business-models/references/ppp-regional-pricing.md) — PPP strategy: coefficient tiers, country groupings, business model framing
