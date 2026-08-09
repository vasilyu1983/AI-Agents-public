# Monitoring and Analytics Cost Guide

Operational reference for understanding and reducing monitoring, error tracking, and product analytics spend. Covers provider pricing, free tier maximization, common waste patterns, and open-source alternatives.

## Table of Contents

- [PostHog](#posthog)
- [Sentry](#sentry)
- [Datadog](#datadog)
- [LogRocket](#logrocket)
- [Mixpanel](#mixpanel)
- [Provider Comparison](#provider-comparison)
- [Free Tier Maximization](#free-tier-maximization)
- [Open-Source Alternatives](#open-source-alternatives)
- [Optimization Checklist](#optimization-checklist)

---

## PostHog

### Pricing

PostHog uses usage-based pricing with a generous free tier across each product:

| Product | Free Tier | Overage Pricing |
|---------|-----------|-----------------|
| Product Analytics | 1M events/month | $0.00031/event after |
| Session Replay | 5K recordings/month | $0.04/recording after |
| Feature Flags | 1M requests/month | $0.0001/request after |
| Surveys | 250 responses/month | $0.20/response after |
| Data Warehouse | 1M rows synced/month | Usage-based after |

Each product is billed independently. You can use analytics heavily and stay free on feature flags if volume is low.

### Common Waste

- **Tracking too many events.** Auto-capture is convenient but sends every click, input change, and page view. Most of these events are noise that no one queries.
- **Recording all sessions.** 100% session recording capture on a site with 50K daily visitors produces 1.5M recordings/month. Most are never watched.
- **Not sampling.** Sending every event and every recording when a 10-20% sample gives statistically valid insights.
- **Unused feature flag evaluations.** Client-side SDKs evaluating flags on every page load, including for flags that are fully rolled out or archived.

### Optimization

1. **Use event allowlists instead of auto-capture.** Define the 20-50 events that matter for your metrics. Disable or filter auto-capture for everything else.
2. **Sample session recordings.** Record 10-20% of sessions unless investigating a specific issue. PostHog supports sampling configuration in the SDK:
   ```js
   posthog.init('key', {
     session_recording: {
       sample_rate: 0.1, // 10% of sessions
     },
   });
   ```
3. **Aggregate client-side before sending.** For high-frequency events (scroll depth, time on page), compute aggregates client-side and send a single summary event instead of streaming raw data.
4. **Clean up stale feature flags.** Remove fully rolled out flags from the codebase and archive them in PostHog to stop evaluation requests.
5. **Use property filters on recordings.** Only record sessions where specific conditions are met (e.g., user hit an error state, used a specific feature).

---

## Sentry

### Pricing

| Plan | Price | Errors | Performance Transactions | Replays |
|------|-------|--------|--------------------------|---------|
| Developer (Free) | $0 | 5K/month | 10K/month | 50/month |
| Team | $26/month | 50K/month | 100K/month | 500/month |
| Business | $80/month | 100K/month | 1M/month | 5K/month |
| Enterprise | Custom | Custom | Custom | Custom |

Overage pricing applies when included quotas are exceeded. Costs scale with error volume and transaction sample rate.

### Common Waste

- **Noisy errors consuming quota.** CORS errors, network timeouts, browser extension interference, and ad blocker-related failures generate high volumes of errors that are not actionable.
- **High transaction sample rate.** Running performance monitoring at 100% sample rate when 5-10% provides sufficient visibility.
- **Duplicate errors.** The same error from the same source generating thousands of events because grouping rules are not configured.
- **Replays on every session.** Session replay at high capture rates burns through quota quickly without proportional debugging value.

### Optimization

1. **Filter known noisy errors.** Use Sentry inbound filters (Settings > Inbound Filters) to drop:
   - Browser extension errors
   - Known third-party script errors
   - Network errors (`TypeError: Failed to fetch`)
   - Legacy browser errors
2. **Reduce transaction sample rate.** Set `tracesSampleRate` to 0.05-0.1 (5-10%) for production. Increase temporarily when investigating specific performance issues:
   ```js
   Sentry.init({
     tracesSampleRate: 0.05,
   });
   ```
3. **Configure error grouping.** Use fingerprinting rules to group related errors into single issues instead of creating thousands of duplicate events.
4. **Use rate limiting.** Set per-key rate limits to cap the maximum events per minute from a single source.
5. **Set replay sample rates separately.** Use `replaysSessionSampleRate` (low, e.g., 0.01) for general sessions and `replaysOnErrorSampleRate` (higher, e.g., 0.5) to capture sessions that hit errors:
   ```js
   Sentry.init({
     replaysSessionSampleRate: 0.01,
     replaysOnErrorSampleRate: 0.5,
   });
   ```

---

## Datadog

### Pricing

Datadog has no free tier for most products. Pricing is per host, per million events, or per GB depending on the product:

| Product | Pricing |
|---------|---------|
| Infrastructure | $15/host/month (Pro), $23/host/month (Enterprise) |
| APM | $31/host/month (APM Pro), $40/host/month (APM Enterprise) |
| Log Management | $0.10/GB ingested/day (indexed), $1.70/million events (15-day retention) |
| RUM (Real User Monitoring) | $1.50/1K sessions |
| Synthetic Monitoring | $5/1K API tests, $12/1K browser tests |
| Custom Metrics | $0.05/custom metric/month (first 100 free with infrastructure) |

Costs compound quickly when multiple products are enabled across many hosts.

### Common Waste

- **Over-instrumented services.** Sending traces for every endpoint, including health checks, readiness probes, and internal service-to-service calls that do not need APM visibility.
- **Too many custom metrics.** Every unique metric name, tag combination, and host creates a billable custom metric. Teams generating thousands of custom metrics from careless tagging.
- **Log volume explosion.** Debug-level logging enabled in production. Logging full request/response bodies. Logging every database query. A single verbose service can generate terabytes of logs per month.
- **Unused product bundles.** Paying for APM + Logs + Infrastructure + RUM when only infrastructure monitoring is needed.

### Optimization

1. **Use only the products you need.** Evaluate whether you need APM, logs, and infrastructure monitoring or just one or two of these. For startups, a simpler stack (infrastructure monitoring + error tracking via Sentry) is often sufficient.
2. **Exclude health checks and internal routes from APM.** Configure trace filtering to drop traces for `/health`, `/ready`, `/metrics`, and similar endpoints.
3. **Control custom metric cardinality.** Avoid high-cardinality tags (user IDs, request IDs, timestamps) on custom metrics. Each unique tag combination creates a new metric.
4. **Reduce log volume at the source.** Set production log level to `warn` or `error`. Use structured logging and send only indexed fields to Datadog. Archive raw logs to S3/R2 for cheaper long-term storage.
5. **Use log pipelines and exclusion filters.** Drop known noisy log patterns before they are indexed. Use Datadog log pipelines to parse, filter, and route logs.
6. **Consider alternatives for startups.** Datadog's pricing model favors large organizations that can negotiate enterprise contracts. For teams under 20 engineers, the cost per engineer is often unjustifiable relative to alternatives.

---

## LogRocket

### Pricing

| Plan | Price | Sessions |
|------|-------|----------|
| Free | $0 | 1K sessions/month |
| Team | $99/month | 10K sessions/month |
| Professional | $249/month | 25K sessions/month |
| Enterprise | Custom | Custom |

Session replay is the core product. Additional sessions are billed at overage rates.

### Cost Considerations

- Session counts depend on how "session" is defined (typically a 30-minute window of activity). A single user can generate multiple sessions per day.
- LogRocket also offers product analytics and error tracking, but the primary cost driver is session volume.
- For teams only needing session replay, compare with PostHog (5K recordings free) or Sentry Replays before committing.

### Optimization

- Sample session recordings (record a percentage of users, not all).
- Use conditional recording: only record sessions where specific events occur (errors, rage clicks, specific page visits).
- Exclude internal users and bots from recording.

---

## Mixpanel

### Pricing

| Plan | Price | Events |
|------|-------|--------|
| Starter (Free) | $0 | 20M events/month |
| Growth | $28/month | 100M events/month |
| Enterprise | Custom | Custom |

Mixpanel's free tier is generous for event volume. Paid plans add advanced analytics features (group analytics, data modeling, SSO) rather than just increasing event limits.

### Cost Considerations

- 20M free events is sufficient for most early-stage products. You hit Growth pricing when you need group analytics, advanced behavioral reports, or data governance features.
- Mixpanel charges by tracked events, not by users. High-frequency events (page views, scrolls) inflate counts quickly.
- Unlike PostHog, Mixpanel does not include session replay, feature flags, or A/B testing. You need separate tools for those.

### Optimization

- Track meaningful user actions, not page views. Use a dedicated analytics tool (Plausible, Umami) for page-level traffic analytics.
- Use Mixpanel's Lexicon to enforce an event taxonomy and prevent event proliferation.
- Implement server-side tracking for critical events to avoid losing data to ad blockers.

---

## Provider Comparison

Decision table for selecting a monitoring and analytics stack.

| Capability | PostHog | Sentry | Datadog | LogRocket | Mixpanel |
|------------|---------|--------|---------|-----------|----------|
| Product Analytics | Strong (core product) | No | Limited (RUM) | Limited | Strong (core product) |
| Error Tracking | Basic | Strong (core product) | Yes (via APM) | Yes | No |
| Session Replay | Yes | Yes | Yes (RUM) | Strong (core product) | No |
| Performance Monitoring | No | Yes | Strong (core product) | Limited | No |
| Feature Flags | Yes | No | No | No | No |
| A/B Testing | Yes | No | No | No | No |
| Infrastructure Monitoring | No | No | Strong (core product) | No | No |
| Log Management | No | No | Strong (core product) | No | No |
| Free Tier | Generous | Moderate | None | Minimal | Generous |
| Self-Hostable | Yes (open-source) | Yes (open-source) | No | No | No |
| Best For | All-in-one product analytics | Error tracking + performance | Full-stack infrastructure | Session replay focus | Behavioral analytics |

### Recommended Stacks by Stage

**Early stage (pre-revenue, 0-5 engineers):**

- PostHog Free (analytics, session replay, feature flags) + Sentry Free (error tracking)
- Total cost: $0/month if within free tiers

**Growth stage (revenue, 5-20 engineers):**

- PostHog (analytics, flags, experiments) + Sentry Team (error tracking) + lightweight infrastructure monitoring (Uptime Kuma, self-hosted)
- Total cost: $26-100/month depending on volume

**Scale stage (20+ engineers, complex infrastructure):**

- Evaluate Datadog or Grafana Cloud for infrastructure monitoring
- Keep PostHog or Mixpanel for product analytics
- Keep Sentry for error tracking
- Total cost: varies significantly by host count and log volume

---

## Free Tier Maximization

Strategies to stay within free tiers as long as possible.

### PostHog

- Disable auto-capture. Track only the 20-50 events that appear in your dashboards and reports.
- Sample session recordings at 5-10%.
- Remove fully rolled-out feature flags from the codebase to stop evaluation requests.
- Use the `posthog-js` `opt_out_capturing` function for internal/test users.

### Sentry

- Enable all inbound filters (browser extensions, legacy browsers, known crawlers).
- Set `tracesSampleRate` to 0.01-0.05 in production.
- Use `beforeSend` to drop errors you cannot act on:
  ```js
  Sentry.init({
    beforeSend(event) {
      if (event.exception?.values?.[0]?.type === 'ChunkLoadError') return null;
      return event;
    },
  });
  ```
- Set `replaysSessionSampleRate` to 0 and only use `replaysOnErrorSampleRate`.

### Mixpanel

- Track server-side where possible to avoid double-counting from client retries.
- Use `mixpanel.set_config({ batch_size: 50 })` to reduce network overhead (does not reduce event count, but improves reliability).
- Avoid tracking page views in Mixpanel. Use a lightweight tool for that.

---

## Open-Source Alternatives

For teams that want to reduce vendor costs by self-hosting.

| Tool | Replaces | Self-Hosting Effort | Notes |
|------|----------|---------------------|-------|
| PostHog (self-hosted) | PostHog Cloud, Mixpanel, Amplitude | Medium-High (Kubernetes, ClickHouse) | Full feature parity. Requires ClickHouse and Kafka. Significant infrastructure overhead. |
| GlitchTip | Sentry | Low (single Docker container) | Sentry-compatible SDK. Covers error tracking only. No performance monitoring or replays. |
| Plausible | Google Analytics, simple analytics | Low (single Docker container) | Privacy-focused, lightweight. Page views and referrers only. No event funnels or cohorts. |
| Umami | Google Analytics, simple analytics | Low (Node.js + PostgreSQL) | Privacy-focused, lightweight. Slightly more features than Plausible (custom events, basic funnels). |
| Grafana + Loki + Prometheus | Datadog | Medium-High (multiple services) | Full observability stack. Requires managing Prometheus, Loki, and Grafana. No vendor lock-in. |
| Uptime Kuma | Pingdom, StatusPage | Low (single Docker container) | Uptime monitoring and status pages only. Not a replacement for APM. |

### Decision: Self-Host vs. SaaS

Self-host when:

- You have infrastructure engineering capacity to maintain the deployment
- Data residency requirements prohibit sending telemetry to third-party services
- You are at scale where SaaS pricing exceeds the cost of running your own infrastructure

Stay on SaaS when:

- Your team is under 10 engineers and infrastructure time is expensive
- You are within free tiers
- You need features that self-hosted versions lag on (PostHog Cloud ships features before self-hosted)

---

## Optimization Checklist

Apply in order of typical impact:

1. **Audit event volume.** List every event being tracked. Delete or stop tracking events that do not appear in any dashboard, report, or alert. For most products, 20-50 well-defined events cover 90% of analytical needs.

2. **Sample session recordings.** Set recording sample rate to 10-20% as a baseline. Use conditional recording (on error, on specific page) for targeted debugging. Never record 100% of sessions in production.

3. **Filter noisy errors.** Configure inbound filters and `beforeSend` hooks to drop browser extension errors, network timeouts, chunk load failures, and bot traffic before they consume quota.

4. **Reduce transaction/trace sample rates.** Set APM/performance sample rates to 5-10% in production. Higher rates are only justified during active performance investigations.

5. **Consolidate tools.** If you are paying for PostHog + Mixpanel + LogRocket + Sentry, evaluate whether PostHog alone covers analytics, session replay, and feature flags, reducing your stack to two tools (PostHog + Sentry).

6. **Control log volume.** Set production log level to `warn` or `error`. Remove request/response body logging. Archive verbose logs to cheap object storage instead of indexed log management.

7. **Clean up unused integrations.** Remove SDK initializations for tools you no longer actively use. Unused SDKs still send data and consume quotas.

8. **Review billing dashboards monthly.** Check usage against included allowances mid-cycle. Set budget alerts where available. Catch volume spikes before they become surprise invoices.

9. **Evaluate open-source alternatives.** For simple use cases (uptime monitoring, basic analytics, error tracking), self-hosted tools can eliminate recurring SaaS costs at the price of infrastructure maintenance.
