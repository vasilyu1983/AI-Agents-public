# Vercel Cost Guide

Operational reference for understanding and reducing Vercel infrastructure spend. Covers billing mechanics, cost drivers ranked by typical impact, and a repeatable optimization checklist.

## Table of Contents

- [Plan Tiers](#plan-tiers)
- [Billing Model](#billing-model)
- [Cost Drivers](#cost-drivers)
  - [Fast Origin Transfer](#fast-origin-transfer)
  - [ISR Writes and Reads](#isr-writes-and-reads)
  - [Function Invocations and Duration](#function-invocations-and-duration)
  - [Fluid Active CPU and Provisioned Memory](#fluid-active-cpu-and-provisioned-memory)
  - [Edge Middleware Invocations](#edge-middleware-invocations)
  - [Image Optimization](#image-optimization)
  - [Build Minutes](#build-minutes)
- [Per-Project Analysis](#per-project-analysis)
- [Common Optimization Checklist](#common-optimization-checklist)
- [Monitoring](#monitoring)
- [When to Consider Alternatives](#when-to-consider-alternatives)

---

## Plan Tiers

### Hobby (Free)

- 100 GB bandwidth per month
- 100 GB-hours serverless function execution
- 6,000 build minutes per month
- No commercial usage permitted
- Single team member only

### Pro ($20/month per member)

- Includes a $20 infrastructure usage credit per billing cycle (applied to usage-based charges, not subscription fees)
- 1 TB bandwidth included
- 1,000 GB-hours serverless function execution included
- 24,000 build minutes per month
- Preview deployments, password protection, and advanced analytics
- Overages billed at published per-unit rates

### Enterprise

- Custom pricing, custom SLAs, and dedicated support
- Negotiable bandwidth, function, and build allocations
- SSO, audit logs, and advanced compliance features

### Decision: Hobby vs. Pro

Upgrade to Pro when any of these apply:

- The project is used for commercial purposes (Hobby TOS prohibits this)
- You need more than one team member
- You consistently exceed Hobby bandwidth or function limits
- You need preview deployment protection or analytics

Stay on Hobby for personal projects, prototypes, and non-commercial experiments that fit within the free limits.

---

## Billing Model

Vercel bills two separate charge types each cycle:

1. **Subscription (flat)** -- the per-member Pro seat fee ($20/member/month). This is a fixed cost regardless of usage.
2. **Infrastructure (usage-based)** -- charges for bandwidth, function invocations, ISR operations, image optimizations, and other metered resources. Billed based on actual consumption above included allowances.

Key details:

- The $20 Pro infrastructure credit applies only to infrastructure usage charges. It does not offset subscription seat fees.
- Billing cycles are calendar-monthly. Usage resets at the start of each cycle.
- Overages are calculated per unit (e.g., per GB of bandwidth, per 1M function invocations) at published rates once included allowances are exhausted.
- Multiple projects on one team share a single pool of included allowances. One high-traffic project can consume the entire team allocation.

---

## Cost Drivers

Ordered by typical impact from highest to lowest. Actual ranking varies by application architecture.

### Fast Origin Transfer

**What it is:** Data transferred from the Vercel CDN edge back to Vercel Compute (the origin). This occurs on every cache miss, every SSR request, and every API route invocation.

**Typical cost:** ~$0.06/GB after the included Pro allowance (1 TB).

**Common waste patterns:**

- Large unoptimized assets (images, fonts, videos) served through Vercel without CDN caching
- Pages rendered via SSR that could be statically generated
- API routes returning large JSON payloads without compression
- Missing or weak `Cache-Control` headers causing repeated origin fetches

**Optimization:**

- Use SSG (`getStaticProps` or static exports) for pages that do not require per-request data
- Set explicit `Cache-Control` headers on API responses: `s-maxage=60, stale-while-revalidate=300`
- Enable Next.js Image Optimization to serve properly sized, compressed images
- Compress API response payloads (Vercel applies gzip/brotli automatically, but reduce payload size at the application level)
- Serve large static assets (videos, downloads) from an external CDN or object storage (e.g., Cloudflare R2, S3 + CloudFront)

### ISR Writes and Reads

**What they are:** Incremental Static Regeneration cache operations. An ISR Write occurs when a page is regenerated and the new HTML is written to the cache. An ISR Read occurs when a cached page is served.

**Typical cost:** ISR Writes are significantly more expensive per operation than ISR Reads. Writes involve compute (re-rendering the page) plus cache storage. Reads are low-cost cache lookups.

**Common waste patterns:**

- Aggressive `revalidate` intervals (e.g., `revalidate: 10` on pages that change daily) -- this triggers frequent unnecessary re-renders
- ISR applied to pages with very low traffic where the regeneration cost exceeds the benefit of caching
- Large numbers of ISR paths across many locales or slug combinations, each regenerating on its own timer

**Optimization:**

- Switch from time-based ISR to on-demand ISR revalidation (`revalidatePath` / `revalidateTag`). Trigger regeneration only when data actually changes (e.g., via a CMS webhook).
- For time-based ISR, increase `revalidate` intervals to match actual data freshness requirements. If content changes hourly, `revalidate: 3600` is sufficient -- not `revalidate: 60`.
- Use plain SSG (no `revalidate`) for truly static content (marketing pages, docs, blog posts that rarely change).
- Audit the number of ISR paths. Reduce combinatorial explosion from locales and dynamic segments.

### Function Invocations and Duration

**What they are:** Every API route, server component render (App Router), and middleware execution counts as a serverless function invocation. Duration measures how long the function runs, billed per GB-hour (memory allocation multiplied by execution time).

**Typical cost:** Per-invocation fee (per 1M invocations) plus per-GB-hour duration charge. Duration cost dominates for long-running functions; invocation count dominates for high-throughput, fast functions.

**Common waste patterns:**

- API routes that perform work that could be cached or done client-side
- Functions with 1024 MB memory allocation when 256 MB would suffice
- No response caching, causing identical requests to re-execute functions
- Synchronous waterfall calls inside functions (fetch A, then B, then C) instead of parallel execution

**Optimization:**

- Cache function responses with `Cache-Control` headers or Next.js `unstable_cache` / `fetch` cache
- Use Edge Functions for simple logic (auth checks, redirects, header manipulation) -- they are cheaper and faster than Node.js serverless functions
- Right-size function memory allocation. Start at 256 MB and increase only if OOM errors occur.
- Batch external API calls with `Promise.all` to reduce duration
- Move heavy computation to background jobs (e.g., Vercel Cron + a queue) rather than synchronous request handlers

### Fluid Active CPU and Provisioned Memory

**What they are:** Compute resources allocated to serverless functions. Fluid Active CPU charges for CPU time during execution. Provisioned Memory charges for the memory reserved for each function instance, including during cold starts.

**Optimization:**

- Right-size function memory. Smaller memory allocation reduces both provisioned memory cost and CPU allocation (Vercel scales CPU proportionally to memory).
- Reduce cold starts by keeping function bundles small. Tree-shake unused dependencies. Avoid importing large libraries for small operations.
- Use Edge Functions for lightweight operations -- they have near-zero cold start and lower memory overhead.
- Consolidate multiple small API routes into fewer route handlers when the logic is closely related.

### Edge Middleware Invocations

**What they are:** Middleware functions that run at the CDN edge before the request reaches the origin. They execute on every matching request, including requests for static assets.

**Common waste patterns:**

- Middleware configured without a `matcher`, causing it to run on every request including `_next/static/*`, `_next/image/*`, and `favicon.ico`
- Complex logic in middleware (database queries, heavy computation) that should be in a serverless function

**Optimization:**

- Always configure `matcher` patterns in `middleware.ts` to exclude static assets:
  ```ts
  export const config = {
    matcher: ['/((?!_next/static|_next/image|favicon.ico).*)'],
  };
  ```
- Keep middleware logic minimal: auth token validation, redirects, header rewrites, geolocation routing
- Move any logic requiring database access or heavy computation to API routes or server components

### Image Optimization

**What it is:** Vercel's built-in image optimization pipeline (`next/image`). Source Transformations resize and convert the original image. Subsequent requests are served from cache (Cache Reads/Writes).

**Typical cost:** Source Transformations are the expensive operation. Cached serves are cheap.

**Optimization:**

- Use modern formats (WebP, AVIF) -- they produce smaller files, reducing both transformation cost and bandwidth
- Set `minimumCacheTTL` in `next.config.js` to keep optimized images cached longer (default is 60 seconds, which is too short for most use cases):
  ```js
  images: {
    minimumCacheTTL: 2592000, // 30 days
  }
  ```
- Pre-optimize images at build time or upload time (e.g., via a CI pipeline with `sharp`) to avoid runtime transformations entirely
- Use `sizes` prop correctly on `<Image>` to avoid generating unnecessary size variants
- For images served from a CDN that already handles optimization (e.g., Cloudflare Images, Imgix), use `unoptimized` prop or a custom loader to bypass Vercel optimization

### Build Minutes

**What they are:** Time spent building and deploying your application. Included in Pro (24,000 min/month). Overage charged per additional minute.

**Optimization:**

- Cache dependencies aggressively (Next.js caches by default; verify with build logs)
- Use Turborepo for monorepos to skip rebuilding unchanged packages
- Configure `ignoreBuildStep` in `vercel.json` to skip deploys when only non-app files changed (e.g., docs-only commits)
- Avoid installing dev dependencies in production builds when not needed
- Reduce preview deployments by limiting auto-deploy branches in project settings

---

## Per-Project Analysis

Vercel bills at the team level, but the Usage dashboard breaks down consumption per project. Use this to identify disproportionate cost contributors.

**How to identify the top cost driver:**

1. Open the Vercel dashboard and navigate to Team Settings > Usage.
2. Filter by project to compare bandwidth, function invocations, and ISR operations across projects.
3. Look for the 80/20 pattern: one project consuming a majority of a specific resource.

**Common pattern -- a single landing site consuming most bandwidth:**

A marketing site or landing page (e.g., `cosmic-landing`) may generate 80%+ of Fast Origin Transfer because it has heavy assets, SSR on every page, or no CDN caching. For this pattern, evaluate:

- Can the site be fully statically exported (`output: 'export'` in Next.js)?
- Should it move to a platform with free or cheaper bandwidth (Cloudflare Pages, Netlify)?
- Is SSR actually necessary, or is it a default that was never changed?

**Decision framework for project placement:**

| Question | If Yes | If No |
|----------|--------|-------|
| Does the project use Vercel-specific features (ISR, Middleware, Edge Functions)? | Keep on Vercel | Consider alternatives |
| Is bandwidth the primary cost driver? | Evaluate static hosting (Cloudflare Pages) | Optimize functions/ISR first |
| Does the project need SSR? | Optimize SSR caching | Switch to SSG or static export |
| Is the project a low-traffic internal tool? | Hobby tier or self-hosted | N/A |

---

## Common Optimization Checklist

Apply these in order of typical impact:

1. **Switch ISR from time-based to on-demand revalidation.** Replace `revalidate: N` with `revalidatePath` / `revalidateTag` triggered by CMS webhooks or data mutation endpoints.
2. **Add `Cache-Control` headers to API responses.** Use `s-maxage` and `stale-while-revalidate` to let the CDN serve cached responses.
3. **Optimize and pre-compress images.** Set `minimumCacheTTL` to 30 days. Pre-optimize at build time. Use WebP/AVIF.
4. **Scope Edge Middleware matchers.** Exclude `_next/static`, `_next/image`, and other static paths from middleware execution.
5. **Review function memory allocation.** Default is often 1024 MB. Reduce to 256 MB or 512 MB unless the function requires more.
6. **Use SSG for pages that do not need real-time data.** Marketing pages, docs, blog posts, and changelogs are almost always static.
7. **Remove unused preview deployments and branches.** Preview deployments consume build minutes and may serve traffic that counts toward bandwidth. Delete stale branches and configure auto-delete in project settings.
8. **Evaluate whether any project should move to cheaper hosting.** Static-only sites are candidates for Cloudflare Pages (free bandwidth). High-bandwidth apps may be cheaper on Fly.io or self-hosted infrastructure.

---

## Monitoring

### Vercel Usage Dashboard

Check monthly:

- Total bandwidth consumed vs. included allowance
- Function Invocations count and trend (month-over-month)
- ISR Writes count (a spike indicates overly aggressive revalidation)
- Fast Origin Transfer volume per project
- Build minutes consumed vs. included allowance

### Spend Management Alerts

Configure in Team Settings > Billing > Spend Management:

- Set a monthly spend cap or alert threshold (e.g., alert at 80% of budget)
- Vercel pauses deployments or sends alerts when the threshold is reached (behavior depends on configuration)
- Review and adjust thresholds quarterly as traffic patterns change

### Key Metrics to Track

| Metric | Why It Matters | Action Trigger |
|--------|---------------|----------------|
| Function Invocations | Indicates unnecessary SSR or uncached API calls | Sudden spike without traffic increase |
| Fast Origin Transfer (GB) | Largest cost driver for most teams | Exceeds 80% of included allowance mid-cycle |
| ISR Writes | Signals over-regeneration | Write count growing faster than content changes |
| Build Minutes | Can spike with monorepo misconfigurations | Exceeds 50% of allowance in first week |
| Edge Middleware Invocations | High counts suggest missing matcher config | Count >> page views (middleware hitting static assets) |

---

## When to Consider Alternatives

### Static-Only Sites

**Move to:** Cloudflare Pages

- Free bandwidth (unlimited on free tier)
- Free builds (500 builds/month on free tier)
- Global CDN with zero egress fees
- Supports Next.js static export, Astro, Hugo, and other static generators

Best for: marketing sites, landing pages, documentation, blogs with no SSR requirements.

### High-Bandwidth Applications

**Move to:** Self-hosted (VPS) or Fly.io

- Vercel bandwidth costs scale linearly. At high volumes (10+ TB/month), a VPS with unmetered bandwidth is significantly cheaper.
- Fly.io provides edge compute with more predictable bandwidth pricing.
- Trade-off: you take on deployment, scaling, and operational complexity.

Best for: media-heavy applications, file delivery, high-traffic consumer apps.

### Simple APIs and Always-On Workloads

**Move to:** Railway or Render

- Vercel serverless functions have cold start overhead and per-invocation pricing
- Railway and Render offer always-on containers with flat monthly pricing
- Better economics for APIs with consistent baseline traffic (no idle-to-cold-start penalty)

Best for: backend APIs with steady request volume, WebSocket servers, background workers, cron-heavy workloads.
