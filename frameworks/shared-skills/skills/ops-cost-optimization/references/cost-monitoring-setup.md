# Cost Monitoring Setup

Cross-platform guide for setting up budget alerts, usage dashboards, and review cadence.

## Table of Contents

- [Budget Alerts by Platform](#budget-alerts-by-platform)
- [Monthly Review Cadence](#monthly-review-cadence)
- [Annual Cost Calendar](#annual-cost-calendar)
- [Dashboard Setup](#dashboard-setup)
- [Negotiation Timing](#negotiation-timing)
- [Cost Attribution](#cost-attribution)
- [FOCUS: Multi-Vendor Cost Normalization](#focus-multi-vendor-cost-normalization)

---

## Budget Alerts by Platform

| Platform | Alert Mechanism | How to Set Up |
|----------|----------------|---------------|
| Vercel | Spend Management | Settings → Billing → Spend Management → set monthly cap |
| Supabase | Usage alerts | Organization Settings → Billing → set usage alerts per metric |
| Stripe | Billing alerts | Dashboard → Settings → configure revenue/dispute alerts |
| Cloudflare | Billing notifications | Account → Billing → Notifications |
| Anthropic | Usage limits | Console → Settings → Spending limits (hard and soft limits) |
| OpenAI | Usage limits | Platform → Settings → Limits → set monthly budget cap |
| GitHub | Spending limits | Settings → Billing → Actions/Packages/Codespaces spending limits |
| PostHog | Billing limits | Organization → Billing → set event/recording limits |
| Sentry | Spend allocation | Settings → Subscription → configure per-category spend allocation |
| Resend | No built-in alerts | Monitor via API usage endpoint or build custom tracking |

### Alert Thresholds

Set two alert levels for each service:

- **Warning (70% of budget):** review usage trends, check for anomalies
- **Critical (90% of budget):** investigate immediately, consider emergency optimizations

For services without built-in alerts, set up calendar reminders to check usage at mid-cycle.

---

## Monthly Review Cadence

### Week 1 of billing cycle
- Check previous cycle's final bill for each service
- Compare to budget — flag any service that exceeded expectations
- Note any new services added

### Mid-cycle check
- Review usage dashboards for top 3 services by cost
- Check if any usage-based metric is trending toward overage
- Verify no unexpected spikes (bot traffic, retry storms, misconfigured cron)

### End of cycle
- Compile total infrastructure spend
- Calculate month-over-month change
- Update the cost inventory spreadsheet

### Quarterly deep review
- Review all subscriptions — cancel unused ones
- Check if any service should change tiers (up or down)
- Evaluate annual vs monthly billing for stable services
- Run the full optimization checklist from SKILL.md
- Negotiate rates where volume justifies it

---

## Annual Cost Calendar

| Month | Action |
|-------|--------|
| January | Annual cost audit — review all services and subscriptions |
| February | Domain renewal audit — cancel unused domains before renewal |
| March | Review annual billing — renew or cancel annual subscriptions expiring in Q2 |
| April | Q1 cost review — compare actual vs budget |
| June | Mid-year review — adjust budgets based on growth |
| July | Q2 cost review |
| September | Plan annual renewals for Q4 — negotiate before auto-renewal |
| October | Q3 cost review |
| November | Black Friday / annual deal season — lock in annual plans at discount |
| December | Year-end cost summary — total spend, per-service breakdown, YoY comparison |

---

## Dashboard Setup

### Minimum viable cost dashboard

Track these metrics monthly for each service:

| Metric | Purpose |
|--------|---------|
| Monthly spend | Total cost per service |
| Month-over-month change | Trend direction |
| Spend vs budget | Are you on track? |
| Top cost driver | Where the money goes |
| Usage vs plan limit | How close to overage or tier change |

### Implementation options

1. **Spreadsheet (simplest):** Google Sheet with one row per service per month. Update manually after each billing cycle. Good for < 10 services.

2. **Notion/Linear tracker:** Create a cost tracking database. Good for team visibility.

3. **Custom dashboard:** Pull from billing APIs (Stripe, Vercel, Supabase all have billing APIs) into a simple dashboard. Worth building only if you track > 15 services or need automated alerting.

---

## Negotiation Timing

| Trigger | Action |
|---------|--------|
| Approaching volume tier boundary | Contact sales before crossing — negotiate rate for commitment |
| Annual renewal coming up | Negotiate 30 days before renewal — leverage competitor quotes |
| Significant usage increase | Request volume discount — show growth trajectory |
| New competitor launched | Use competitive pressure in negotiation |
| Contract anniversary | Many providers review pricing annually — initiate the conversation |

### Negotiation prep

Before contacting sales:
1. Know your current monthly spend with the provider
2. Know your growth trajectory (3-6 month forecast)
3. Have a competitor quote or benchmark ready
4. Know your walk-away point — what would you switch to?
5. Ask for interchange-plus (Stripe), committed-use discounts (cloud), or volume tiers (SaaS)

---

## Cost Attribution

For teams or multi-product setups, attribute costs to projects or products:

### Per-project attribution

- **Vercel:** usage dashboard shows per-project bandwidth and function usage
- **Supabase:** separate projects per product — costs are naturally isolated
- **Stripe:** use metadata or product IDs to attribute revenue and fees per product
- **AI APIs:** tag requests with project/feature identifiers, track cost per feature
- **GitHub:** Actions usage is per-repo in billing

### Attribution rule

If a service doesn't support per-project billing, estimate by usage ratio. Example: if Project A uses 80% of Vercel bandwidth, attribute 80% of Vercel infrastructure cost to Project A.

Track attribution quarterly — it changes as products grow or shrink.

---

## FOCUS: Multi-Vendor Cost Normalization

When aggregating cost data across Vercel, Supabase, AI APIs, and GitHub into a single dashboard, each vendor uses different column names, date formats, and cost categories. This schema mismatch makes multi-vendor rollups error-prone.

**FOCUS** (FinOps Open Cost and Usage Specification) is the vendor-neutral standard for normalizing billing exports. It defines a common schema so cost data from different providers can be merged without manual per-vendor mapping.

**Current version:** FOCUS 1.4, ratified June 4, 2026 (verify at the spec URL below — re-check periodically as the spec revises every 6-12 months).
FOCUS 1.2 (May 29, 2025) added SaaS/PaaS normalization — directly relevant for the SaaS-heavy stacks this skill covers.
**Specification:** https://focus.finops.org/focus-specification/

### When to adopt FOCUS

| Situation | Recommendation |
|-----------|---------------|
| Single vendor or 2-3 vendors, manual review | Skip — a simple spreadsheet is sufficient |
| 4+ vendors, automated aggregation needed | Map billing exports to FOCUS schema for stable cross-vendor joins |
| Building a cost dashboard or BI pipeline | Target FOCUS columns from the start; avoid vendor-specific schemas |
| Vendors emit native FOCUS exports | Drop them in directly — no mapping needed |

### Practical adoption

1. Export billing data from each vendor (most offer CSV or API exports).
2. For vendors with native FOCUS exports, use them directly.
3. For vendors without FOCUS exports, write a one-time column mapping to the FOCUS schema and version-control it.
4. Aggregate the normalized data and compute unit metrics (cost per customer, cost per request) against the unified dataset.

See [unit-economics-guide.md](unit-economics-guide.md) for the full FOCUS context and how it connects to unit economic tracking.
