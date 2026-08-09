# Cloudflare Cost Guide

Operational reference for understanding Cloudflare's pricing model, maximizing the free tier, and migrating workloads to reduce infrastructure costs. Cloudflare's free tier is unusually generous compared to other cloud providers, and many teams overpay for equivalent services elsewhere.

## Table of Contents

- [Plan Tiers](#plan-tiers)
- [Workers](#workers)
- [R2 Object Storage](#r2-object-storage)
- [Pages](#pages)
- [Images](#images)
- [Stream](#stream)
- [Workers KV](#workers-kv)
- [D1 Database](#d1-database)
- [Cost Drivers](#cost-drivers)
- [Common Waste Patterns](#common-waste-patterns)
- [Optimization Checklist](#optimization-checklist)
- [Migration Checklist](#migration-checklist)
- [When to Upgrade from Free to Pro](#when-to-upgrade-from-free-to-pro)

---

## Plan Tiers

### Free ($0/month)

Included for every domain added to Cloudflare:

- Unlimited DNS hosting (authoritative DNS, fast propagation)
- Global CDN with unlimited bandwidth
- DDoS protection (unmetered, always on)
- Universal SSL/TLS (automatic certificate provisioning)
- 5 Page Rules
- Basic analytics (web traffic, caching, threats)
- Bot Fight Mode (basic bot detection)
- 100K Workers requests/day
- 10 GB R2 storage

The free tier covers the core needs of most small-to-medium sites. DNS, CDN, SSL, and DDoS protection are genuinely unlimited.

### Pro ($20/month per domain)

Everything in Free, plus:

- Web Application Firewall (WAF) with managed rulesets (OWASP, Cloudflare Managed Rules)
- Image optimization (Polish, Mirage)
- Cache Analytics (detailed cache hit/miss breakdown)
- 20 Page Rules
- Mobile optimization (Rocket Loader)
- Enhanced bot detection

### Business ($200/month per domain)

Everything in Pro, plus:

- Advanced WAF with custom rulesets
- 100% uptime SLA with 25x credit
- 50 Page Rules
- Custom SSL certificate upload
- Priority support

### Enterprise (Custom pricing)

Everything in Business, plus:

- Custom SLAs, dedicated account team
- Advanced DDoS analytics and custom mitigations
- Unlimited Page Rules
- Spectrum (TCP/UDP proxy)
- Access to Cloudflare Network Interconnect

---

## Workers

Serverless compute at the edge. Code runs in V8 isolates, not containers.

### Pricing

| Plan | Requests | CPU Time | Notes |
|------|----------|----------|-------|
| Free | 100K requests/day | 10 ms CPU time per invocation | No charge. Daily limit resets at midnight UTC. |
| Paid ($5/month) | 10M requests/month included | 50 ms CPU time per invocation | $0.50 per additional 1M requests. $0.02 per additional 1M ms CPU time. |

### Key Details

- **CPU time, not wall-clock time.** A Worker that waits 200 ms for a `fetch()` response but uses 2 ms of CPU counts as 2 ms, not 200 ms. This makes Workers cheap for I/O-bound tasks.
- **Bundled vs. Unbound models.** The free plan uses the Bundled model (10 ms CPU cap). The paid plan uses the Standard model (previously Unbound) with 30-second wall-clock and 50 ms CPU per invocation defaults.
- **Custom domains.** Each Worker route on a custom domain counts as a request against your plan. Workers on `*.workers.dev` subdomains share the same quota.
- **Cron Triggers.** Scheduled Workers (cron) count against request quotas. A Worker triggered every minute = 43,200 requests/month.

### When Workers Make Sense

- Auth token validation, redirects, header manipulation, A/B routing
- Lightweight API endpoints that do not need a full server
- Edge-side rendering or content transformation
- Replacing API Gateway + Lambda for simple request handling

---

## R2 Object Storage

S3-compatible storage with zero egress fees. This is Cloudflare's most disruptive pricing advantage.

### Pricing

| Resource | Free Tier | Paid Rate |
|----------|-----------|-----------|
| Storage | 10 GB/month | $0.015/GB/month |
| Class A operations (PUT, POST, LIST) | 1M requests/month | $4.50/million requests |
| Class B operations (GET, HEAD) | 10M requests/month | $0.36/million requests |
| Egress (data transfer out) | **Unlimited, free** | **$0** |

### Comparison with S3

| Dimension | AWS S3 Standard | Cloudflare R2 |
|-----------|-----------------|---------------|
| Storage | $0.023/GB/month | $0.015/GB/month |
| Egress | $0.09/GB (first 10 TB) | $0/GB |
| GET requests | $0.0004/1K | $0.36/million ($0.00036/1K) |
| PUT requests | $0.005/1K | $4.50/million ($0.0045/1K) |

For read-heavy workloads, R2 is dramatically cheaper because egress is free. A site serving 1 TB/month of assets from S3 pays ~$90 in egress alone. From R2: $0.

### When R2 Makes Sense

- Any workload where egress costs dominate (media serving, file downloads, CDN origins)
- Replacing S3 as a CDN origin to eliminate egress fees
- User-uploaded content storage (avatars, documents, media)
- Backup and archive storage (cheaper than S3 Standard, no egress for retrieval)

---

## Pages

Static site and full-stack hosting. Deploys from Git or direct upload.

### Pricing

| Resource | Limit |
|----------|-------|
| Bandwidth | **Unlimited, free** |
| Build minutes | 500 builds/month (free), unlimited (paid) |
| Sites | Unlimited |
| Preview deployments | Unlimited |
| Custom domains | Unlimited |

Pages is genuinely free for most static site use cases. There are no bandwidth charges, no per-request fees, and no storage fees for deployed assets.

### Supported Frameworks

Pages supports build output from Next.js (static export and full SSR via Workers), Astro, Nuxt, SvelteKit, Remix, Hugo, Gatsby, Eleventy, and any static site generator.

### When Pages Makes Sense

- Marketing sites, landing pages, documentation, blogs
- Any static site currently on Vercel, Netlify, or GitHub Pages where bandwidth cost is a concern
- JAMstack applications with API backends hosted elsewhere
- Preview deployments for every PR (free, unlimited)

---

## Images

On-demand image optimization and delivery.

### Pricing

| Resource | Cost |
|----------|------|
| Stored images | $1 per 100K stored images/month |
| Delivered images | $5 per 100K served images/month |
| Transformations | Included (no separate per-transformation fee) |

### Key Details

- Images are stored in Cloudflare's edge-optimized pipeline, not R2. Storage and delivery are billed separately.
- Transformations (resize, format conversion, quality adjustment) are applied on first request and cached. Subsequent requests serve the cached variant at no additional transformation cost.
- Supports flexible URL-based transformations: `/cdn-cgi/image/width=400,format=webp/path/to/image.jpg`.

### When to Use

- Sites serving many image variants (thumbnails, responsive sizes) where you want to avoid pre-generating all sizes
- Replacing Imgix, Cloudinary, or Vercel Image Optimization for simpler use cases
- Combined with R2 for user-uploaded images: store originals in R2, serve optimized variants via Images

---

## Stream

Video storage and delivery with adaptive bitrate streaming.

### Pricing

| Resource | Cost |
|----------|------|
| Storage | $5 per 1,000 minutes stored/month |
| Delivery | $1 per 1,000 minutes delivered |
| Live streaming | Same per-minute delivery rate |

### Key Details

- Stream handles encoding, storage, and adaptive bitrate delivery. You upload a video, and Stream produces HLS/DASH manifests automatically.
- No egress fees beyond the per-minute delivery charge.
- Includes an embedded player or you can use your own player with the HLS/DASH URLs.

### When to Use

- Applications with user-uploaded video content (courses, social, reviews)
- Replacing self-managed video encoding pipelines (FFmpeg + S3 + CloudFront)
- Live streaming where you want to avoid managing RTMP ingest infrastructure

### When to Avoid

- If you are already on YouTube or Vimeo for hosting and embedding and do not need programmatic control
- If video volume is very low (a few videos), the base cost may not justify the integration effort

---

## Workers KV

Global, eventually consistent key-value store. Optimized for high-read, low-write workloads.

### Pricing

| Resource | Free Tier | Paid Rate |
|----------|-----------|-----------|
| Reads | 100K reads/day | $0.50/million reads |
| Writes | 1K writes/day | $5.00/million writes |
| Deletes | 1K deletes/day | $5.00/million deletes |
| Lists | 1K lists/day | $5.00/million lists |
| Storage | 1 GB | $0.50/GB/month |

### When to Use

- Configuration storage, feature flags, A/B test assignments
- Edge caching of API responses or computed data
- Session data for stateless Workers

### When to Avoid

- Write-heavy workloads (KV is optimized for reads; writes are expensive and eventually consistent)
- Use D1 or Durable Objects for transactional or strongly consistent data

---

## D1 Database

SQLite-based serverless database at the edge.

### Pricing

| Resource | Free Tier | Paid Rate |
|----------|-----------|-----------|
| Rows read | 5M/day | $0.001/million rows read |
| Rows written | 100K/day | $1.00/million rows written |
| Storage | 5 GB | $0.75/GB/month |

### When to Use

- Small-to-medium databases for edge applications (user profiles, settings, content metadata)
- Applications that need SQL but do not need the scale or features of a managed PostgreSQL instance
- Replacing Supabase or PlanetScale for simple use cases with lower cost

### When to Avoid

- Applications requiring complex joins, stored procedures, or advanced SQL features
- Write-heavy OLTP workloads at significant scale
- Applications needing real-time replication to other regions

---

## Cost Drivers

Ordered by typical impact for teams using multiple Cloudflare products.

### Workers CPU Time

The primary cost driver for compute-heavy Workers. If your Worker does JSON parsing, template rendering, or heavy string manipulation, CPU time accumulates. I/O wait (fetch calls, KV reads) does not count.

**Monitor:** Check Workers analytics in the Cloudflare dashboard for P50 and P99 CPU time per request. If P99 approaches the 50 ms paid limit, optimize or split the Worker.

### R2 Class A Operations

PUT, POST, DELETE, and LIST operations cost $4.50/million. Frequent writes (logging every request to R2, writing per-user files on every page load) add up faster than storage costs.

**Monitor:** Check R2 analytics for operation counts. Batch writes where possible. Use Workers to buffer and write in bulk.

### Workers KV Writes

At $5/million, writes are 10x more expensive than reads. A common mistake is using KV as a general-purpose database with frequent updates instead of as a read-optimized cache.

### Custom Domain Workers Routes

Each custom domain route binding adds overhead. Multiple domains routing to the same Worker multiply request counts against your plan.

---

## Common Waste Patterns

1. **Paying for Pro when Free covers the need.** The most common waste. Teams upgrade to Pro "just in case" without needing WAF rules, image optimization, or cache analytics. The free tier includes CDN, DDoS protection, SSL, and DNS -- which is enough for most sites.

2. **Using S3 + CloudFront when R2 eliminates egress fees.** Teams paying $50-500+/month in S3 egress for serving static assets, user uploads, or backups. Migrating to R2 eliminates egress entirely.

3. **Not using Pages for static sites.** Hosting static sites on Vercel (bandwidth limits), Netlify (bandwidth limits), or S3 (egress fees) when Cloudflare Pages offers unlimited free bandwidth.

4. **Workers for tasks that should be cached.** Running a Worker to generate a response that is identical for all users instead of caching the response at the CDN layer and serving it statically.

5. **KV for write-heavy patterns.** Using Workers KV as a session store or analytics buffer where writes dominate reads. Switch to Durable Objects or D1 for write-heavy patterns.

6. **Not using cache rules.** Serving dynamic-looking URLs (e.g., `/api/config`) that return the same response for hours without setting Cache-Control headers. Every request hits the origin.

---

## Optimization Checklist

Apply in order of typical impact:

1. **Use the free tier aggressively.** DNS, CDN, SSL, DDoS protection, and basic analytics are free and unlimited. Do not pay for these elsewhere. Add every domain to Cloudflare even if you only use DNS.

2. **Migrate static sites to Pages.** Any site currently on Vercel, Netlify, GitHub Pages, or S3 that is static or can be statically exported should move to Cloudflare Pages for unlimited free bandwidth.

3. **Move object storage to R2.** Calculate current S3/GCS egress costs. If egress is a significant line item, migrate to R2. The S3-compatible API makes migration straightforward (update endpoint and credentials).

4. **Set cache rules for static and semi-static content.** Use Cache Rules (or Page Rules on Free) to cache responses for static assets, API responses that change infrequently, and HTML pages that can tolerate staleness.

5. **Use Workers for edge logic, not application logic.** Keep Workers lightweight: auth checks, redirects, header manipulation, A/B routing. Move heavy computation to a backend service.

6. **Batch R2 writes.** If your application writes many small objects to R2, buffer writes in a Worker and flush in batches to reduce Class A operation costs.

7. **Monitor Workers CPU time.** Review P50 and P99 CPU times weekly. Optimize hot paths. Consider splitting complex Workers into smaller, focused Workers.

8. **Evaluate whether Pro features justify $20/month.** If you are on Pro, check whether you actively use WAF rules, image optimization (Polish/Mirage), or cache analytics. If not, downgrade to Free.

---

## Migration Checklist

Steps for migrating DNS, sites, or storage to Cloudflare with zero downtime.

### DNS Transfer

1. **Add the domain to Cloudflare.** Cloudflare scans existing DNS records and imports them.
2. **Verify imported records.** Compare every imported record against the current DNS provider. Pay attention to MX records, TXT records (SPF, DKIM, DMARC), and CNAME records.
3. **Set proxy status.** Decide which records should be proxied (orange cloud) vs. DNS-only (gray cloud). Proxy HTTP/HTTPS traffic. DNS-only for mail, SSH, and non-HTTP services.
4. **Update nameservers at the registrar.** Change NS records to the Cloudflare-assigned nameservers.
5. **Wait for propagation.** DNS propagation typically completes within 24 hours. Monitor with `dig` or a DNS propagation checker.
6. **Verify SSL.** Cloudflare provisions a Universal SSL certificate automatically. Verify HTTPS works after propagation.

### Static Site Migration (to Pages)

1. **Connect the Git repository** or use direct upload (Wrangler CLI).
2. **Configure build settings** (framework preset, build command, output directory).
3. **Deploy and test on the `*.pages.dev` subdomain** before switching DNS.
4. **Add the custom domain** in Pages project settings. Cloudflare automatically creates a CNAME record.
5. **Verify the site** on the custom domain. Check all pages, assets, and functionality.
6. **Remove the old hosting** after confirming everything works.

### Object Storage Migration (to R2)

1. **Create an R2 bucket** in the Cloudflare dashboard or via the S3-compatible API.
2. **Generate R2 API credentials** (Access Key ID + Secret Access Key).
3. **Sync data** using `rclone`, `aws s3 sync` (with R2 endpoint), or a migration script.
4. **Update application configuration** to point to the R2 endpoint and credentials.
5. **Test reads and writes** against R2 before decommissioning the old bucket.
6. **Set up a public bucket or custom domain** if serving assets publicly. R2 supports public access via a custom domain with automatic CDN caching.

### Cache Warming

After migration, the Cloudflare CDN cache is cold. Expect higher origin load for the first few hours.

- Use a crawler or synthetic traffic to warm the cache for high-traffic URLs.
- Monitor origin server load during the first 24-48 hours.
- Verify cache hit ratios in the Cloudflare dashboard. Target 80%+ for static assets within the first day.

---

## When to Upgrade from Free to Pro

Upgrade when any of these conditions apply:

1. **You need WAF rules.** The free tier has no WAF. If you need managed rulesets (OWASP Top 10, Cloudflare Managed Rules) or custom firewall rules beyond basic IP blocking, you need Pro.

2. **You need image optimization.** Polish (lossless/lossy image compression) and Mirage (lazy loading, responsive images) are Pro features. Useful for image-heavy sites that do not use a separate image CDN.

3. **You need cache analytics.** Free tier analytics show basic traffic data. Pro provides detailed cache hit/miss ratios, content type breakdowns, and bandwidth-by-cache-status reports. Useful for diagnosing caching issues.

4. **You need more than 5 Page Rules.** Free tier includes 5 Page Rules. Pro includes 20. If you need complex URL-based caching, redirects, or security rules, the additional Page Rules may justify the upgrade.

5. **You are running a production commercial application.** While the free tier has no restrictions on commercial use, Pro provides faster support response times and more granular controls. For applications where downtime has revenue impact, the $20/month is reasonable insurance.

Stay on Free when:

- Your site is behind Cloudflare primarily for DNS, CDN, and SSL.
- You handle image optimization at build time or via a separate service.
- You do not need WAF rules (basic DDoS protection and rate limiting are included in Free).
- You can manage with 5 or fewer Page Rules (or use Transform Rules and Cache Rules, which have higher free limits).
