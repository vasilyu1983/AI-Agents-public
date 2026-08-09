# Unit Economics Guide

Operational reference for tracking cost at the unit level — per customer, per feature, per request — and connecting infrastructure spend to revenue. Anchored in the FinOps Foundation's "Unit Economics" capability under the Quantify Business Value domain (https://www.finops.org/framework/domains/).

## Table of Contents

- [Why Unit Economics](#why-unit-economics)
- [Core Unit Metrics](#core-unit-metrics)
  - [Cost Per Customer](#cost-per-customer)
  - [Cost Per Feature](#cost-per-feature)
  - [Cost Per Request](#cost-per-request)
- [Tagging and Attribution](#tagging-and-attribution)
- [Tracking Cost Against ARPC](#tracking-cost-against-arpc)
- [Profitable Growth vs Destructive Growth](#profitable-growth-vs-destructive-growth)
- [FOCUS: Vendor-Neutral Cost Normalization](#focus-vendor-neutral-cost-normalization)
- [Implementation Checklist](#implementation-checklist)

---

## Why Unit Economics

Aggregate infrastructure spend is a vanity metric. A $5,000/month bill is fine for a business with 2,000 paying customers and destructive for a pre-revenue side project. Unit economics tie spend to a denominator that has business meaning: customers, requests, features, or revenue.

Without unit metrics:
- Cost increases caused by growth are indistinguishable from cost increases caused by waste.
- You cannot know whether adding customers is profitable or loss-making.
- FinOps reviews devolve into "find things to cut" rather than "understand what we are buying."

With unit metrics:
- Every optimization decision can be evaluated against business impact.
- You can distinguish "expensive because we are growing" from "expensive because we are inefficient."
- Growth conversations are grounded in cost-per-unit, not total spend.

---

## Core Unit Metrics

### Cost Per Customer

**Definition:** Total monthly infrastructure cost divided by the number of active customers (paying or meaningfully engaged, depending on your business model).

**Formula:**

```
cost_per_customer = total_monthly_infra_spend / active_customers
```

**Target:** Cost per customer should be well below your average revenue per customer (ARPC) to leave gross margin for SG&A, product, and profit. A common SaaS target is infrastructure COGS at 15-25% of ARPC, though this varies widely by product type.

**Tracking frequency:** Monthly. Compare month-over-month — if cost per customer is rising while customer count is flat, you have an efficiency problem.

**Common drivers of high cost per customer:**
- Shared infrastructure not shared proportionally (each customer gets a dedicated database or worker)
- Overprovisioned compute relative to actual per-customer usage
- Runaway AI API costs per user session
- Storage accumulating without lifecycle policies

### Cost Per Feature

**Definition:** The infrastructure cost attributable to a specific product feature, expressed per unit of use (per invocation, per active user of that feature, per month).

**Why track it:** Not all features carry the same cost. A real-time sync feature might cost 10x per active user compared to a static dashboard. Unit cost by feature reveals which capabilities are expensive to run and helps prioritize optimization effort.

**How to calculate:**
1. Tag all compute, storage, bandwidth, and API calls with a feature identifier (see [Tagging and Attribution](#tagging-and-attribution)).
2. Sum tagged costs per feature per month.
3. Divide by the active user count or invocation count for that feature.

**Use case:** When evaluating whether to deprecate, sunset, or redesign a feature, cost per feature is an input. A feature used by 5% of customers but consuming 30% of infra cost is a candidate for architectural rework.

### Cost Per Request

**Definition:** The average infrastructure cost to serve one request, API call, or unit of work.

**Formula:**

```
cost_per_request = total_monthly_infra_spend / total_requests_served
```

**Useful for:**
- Benchmarking optimization progress — if cost per request drops, you are getting more efficient.
- Estimating infrastructure cost for projected load at scale.
- Comparing architecture approaches (server-side rendering vs edge vs static).

**Segment by request type.** A homepage load, a complex AI-assisted query, and a background job have vastly different costs per invocation. Aggregate cost per request is a starting point; segment by workload type for actionable data.

---

## Tagging and Attribution

Unit economics require attributing infrastructure spend to business units. This is a tagging and labeling problem.

### Tag taxonomy

Define a consistent set of tags before you start spending at scale. Retrofitting tags is painful.

| Tag Key | Example Values | Purpose |
|---------|---------------|---------|
| `feature` | `onboarding`, `dashboard`, `export`, `ai-chat` | Attribute cost to product features |
| `customer_tier` | `free`, `starter`, `pro`, `enterprise` | Break cost down by revenue tier |
| `customer_id` | UUID or slug | Per-customer attribution (only if compliance permits) |
| `environment` | `production`, `staging`, `dev` | Separate production cost from non-production waste |
| `team` | `backend`, `ml`, `data` | Internal team accountability |

### Tagging by platform

- **Vercel:** Per-project cost is native. Use multiple Vercel projects to isolate major features or products.
- **Supabase:** Separate projects per major product boundary. Within a project, tag usage via application logic (e.g., log which feature triggered each Edge Function invocation).
- **AI APIs:** Pass a `metadata` or `user` field on every request with feature and user-tier identifiers. Aggregate from API usage logs or a tool like Langfuse, Helicone, or Portkey (see [ai-api-cost-guide.md](ai-api-cost-guide.md) — LLM Cost Attribution section).
- **GitHub Actions:** Usage is per-repo in billing. Use matrix strategies and conditional jobs to tag workflow runs by environment.

### Attribution when tagging is incomplete

If native tagging is not available, estimate by usage ratio:

1. Measure the proportion of total load attributable to each feature or customer tier (requests, storage reads, active sessions).
2. Multiply total cost by that proportion.
3. Reassess quarterly — usage ratios shift as products grow.

This is approximate but far better than treating all spend as undivided overhead.

---

## Tracking Cost Against ARPC

**ARPC (Average Revenue Per Customer):** Total monthly recurring revenue divided by paying customer count.

**Infrastructure gross margin:**

```
infra_gross_margin = 1 - (cost_per_customer / ARPC)
```

A product with ARPC of $30 and cost per customer of $6 has 80% infrastructure gross margin — the remaining 20% of revenue is consumed by infrastructure COGS before any other expense.

### Target ranges (indicative, not guaranteed)

These are practitioner-reported norms for SaaS. Your numbers will vary based on product type, AI usage, and data intensity.

| Infrastructure Gross Margin | Signal |
|-----------------------------|--------|
| > 80% | Healthy — infrastructure is well-managed relative to revenue |
| 60-80% | Acceptable — watch for cost creep as scale increases |
| 40-60% | Needs attention — identify top cost drivers and optimize |
| < 40% | Unsustainable at current ARPC — re-architect or reprice |

**AI-heavy products** may see lower margins because model inference costs are high relative to subscription ARPC. In these cases, track cost per AI session or cost per AI query separately, and set per-session cost targets.

### Monthly cost-to-revenue tracking

Add a column to your cost inventory for ARPC and compute the ratio monthly:

| Month | Total Infra Cost | Active Customers | Cost/Customer | ARPC | Infra Margin |
|-------|-----------------|-----------------|---------------|------|-------------|
| Jan   | $4,200          | 350             | $12.00        | $45  | 73%         |
| Feb   | $4,800          | 380             | $12.63        | $45  | 72%         |

A rising cost/customer with flat ARPC is the early signal that infrastructure is becoming a margin problem.

---

## Profitable Growth vs Destructive Growth

Not all growth improves the business. Unit economics reveal whether growth is increasing or decreasing efficiency.

### Profitable growth signals

- Cost per customer is flat or declining as customer count grows (economies of scale working).
- Infrastructure gross margin is stable or improving.
- New features added without proportional cost increases (shared infrastructure absorbing load).
- Optimization work outpacing usage growth (cost per request declining).

### Destructive growth signals

- Cost per customer is rising as customer count grows (diseconomies of scale — architecture not designed for shared load).
- AI API cost per user is growing faster than ARPC (each user session consumes more tokens over time without corresponding revenue increase).
- Infrastructure cost growing faster than customer count (onboarding each new customer costs more than the last).
- Large non-production spend growing in proportion to production (staging and dev environments not cleaned up as team grows).

### Diagnostic questions

When growth looks expensive, ask:

1. Is this cost driven by customer growth (expected) or by waste (fixable)?
2. Is the new marginal customer profitable at current cost per customer?
3. Which single cost line is growing fastest, and is it necessary?
4. If we doubled customers tomorrow, would infrastructure cost double, grow slower, or grow faster — and why?

---

## FOCUS: Vendor-Neutral Cost Normalization

When tracking unit economics across multiple cloud or SaaS providers, inconsistent billing schemas make aggregation difficult. FOCUS (FinOps Open Cost and Usage Specification) is the vendor-neutral standard for normalizing cost and usage data across providers.

**Current version:** FOCUS 1.4, ratified June 4, 2026 (verify at the spec URL below — the spec revises roughly every 6-12 months). FOCUS 1.4 added Invoice Detail and Billing Period datasets and expanded the Contract Commitment dataset from 13 to 30 columns, making commitment structures (Savings Plans, RIs, CUDs) comparable across providers from one schema — directly relevant if you are also tracking cloud commitment purchases (see [cloud-commitment-and-k8s-cost-guide.md](cloud-commitment-and-k8s-cost-guide.md)).
**Key milestone:** FOCUS 1.2 (May 29, 2025) added SaaS/PaaS normalization, making it relevant for the multi-vendor stacks this skill covers.
**Specification:** https://focus.finops.org/focus-specification/

FOCUS defines a common schema for billing exports — standardized column names, date formats, and cost categories — so you can merge AWS, GCP, Azure, and SaaS billing data without manual mapping.

### When FOCUS matters for this skill

For indie and scale-up teams running Vercel + Supabase + Anthropic + GitHub:

- FOCUS is most valuable when you want a single cost dashboard that aggregates all vendor bills without per-vendor ETL logic.
- If you export billing data from each vendor and join it in a spreadsheet or BI tool, FOCUS column names give you a stable schema to target.
- Providers that emit FOCUS-compliant exports can be dropped into a unified pipeline without schema translation.

### Practical adoption path

1. Check whether your vendors export FOCUS-compliant billing data (major cloud providers do; SaaS providers are adopting progressively).
2. For vendors without FOCUS exports, map their billing columns to FOCUS schema manually — do this once and version-control the mapping.
3. Aggregate into a unified cost dataset and compute unit metrics (cost per customer, cost per request) against the normalized data.
4. Do not wait for full vendor FOCUS compliance before starting unit economics tracking — approximate normalization beats no normalization.

---

## Implementation Checklist

Apply in order of impact:

1. Define your primary unit denominator: active customers, requests, or both.
2. Pull current monthly infrastructure spend from each platform.
3. Calculate current cost per customer and cost per request as a baseline.
4. Compare cost per customer to ARPC — compute infrastructure gross margin.
5. Set up a monthly cost-to-revenue tracking table (spreadsheet or Notion).
6. Implement feature/tier tagging in your top 2-3 cost services.
7. Add a unit economics row to your monthly cost review cadence.
8. Set a target infrastructure gross margin and alert when the metric falls below threshold.
9. Review unit trends quarterly alongside the standard cost review.
