# Vendor Billing Guide

What each SaaS and infrastructure vendor meters, the levers ranked by typical impact, and the decision rules for tiers, switching and negotiation. It carries no prices, quotas, plan limits or free-tier sizes: every number that feeds a decision comes from the [vendor lookup step](#vendor-lookup-step). Worked examples use illustrative inputs so the arithmetic can be checked.

## Table of Contents

- [Vendor Lookup Step](#vendor-lookup-step)
- [Plan-Tier Crossover](#plan-tier-crossover)
- [Levers That Apply to Every Vendor](#levers-that-apply-to-every-vendor)
- [Vercel](#vercel)
- [Supabase](#supabase)
- [Cloudflare](#cloudflare)
- [Stripe](#stripe)
- [GitHub and CI/CD](#github-and-cicd)
- [IaC Cost Guardrails](#iac-cost-guardrails)
- [Monitoring and Analytics](#monitoring-and-analytics)
- [Email (Resend)](#email-resend)
- [Domains and DNS](#domains-and-dns)

---

## Vendor Lookup Step

Prices, included quantities, overage rates, plan limits and even dimension names change without notice. Every cost decision starts here:

1. **Source.** Read the vendor's pricing page, or better, the invoice or usage export for your account; the export shows what is actually billed, including grandfathered plans and negotiated rates.
2. **Record.** Note the date, the currency, whether prices include tax, and the plan name next to every number you use.
3. **Confirm limits.** Check the included quantities, overage rates and caps on your account's plan, not the marketing page; enterprise and legacy plans differ. Map the dimension names below to the current invoice lines.
4. **Recompute.** Re-run the decision (the [plan-tier crossover](#plan-tier-crossover), a commitment size, a self-host breakeven, a switch) with the fresh inputs. Never reuse a breakeven computed from last quarter's prices.

If web access is unavailable, say so, and label every price-dependent conclusion as unverified with the pricing URL from `data/sources.json`.

## Plan-Tier Crossover

Most usage-priced plans have the same shape: a base fee f, an included quantity q, and an overage rate r per unit above q. For tier A (f_A, q_A, r_A) and a pricier tier B (f_B > f_A) whose included quantity covers the usage in question, the monthly costs cross at

    u* = q_A + (f_B − f_A) / r_A

Upgrade to B when forecast usage stays above u*; stay on A below it. Worked check with illustrative inputs (f_A = 20, q_A = 100, r_A = 0.5, f_B = 100 with q_B = 1000): u* = 100 + 80 / 0.5 = 260 units, where both tiers cost 100.

- If u* exceeds q_B, B's own overage applies too; compare the two cost curves directly instead.
- Use the forecast for the billing period, not today's usage: a spike month does not justify an upgrade, and steady growth may justify one early.
- Add per-seat fees, add-ons and features you need only on B to f_B before comparing; a feature need can override the arithmetic.
- Per-seat or per-zone plans scale with headcount or domain count, not usage: an upgrade decided for one seat or zone should not be copied to all of them.

## Levers That Apply to Every Vendor

State these once per audit instead of per vendor:

- **Cache before you compute.** A cache hit at the CDN costs a fraction of an origin request, a function invocation or a database read. Missing `Cache-Control` on semi-static responses is the most common cross-vendor waste.
- **Seats bill when assigned, not when used.** Audit seat usage quarterly on every per-seat product and reclaim idle seats.
- **Retention defaults are set for the vendor, not for you.** Set artifact, log, recording, backup and branch retention explicitly.
- **Sample telemetry.** Recordings, traces and verbose logs scale with traffic; size the sample to the smallest segment you analyse and keep critical events unsampled.
- **Pooled allowances hide the culprit.** Team- or organization-level allowances are shared, so one project can consume them all. Break usage down per project before optimizing.
- **Switching has a payback period.** A small rate cut that costs months of migration may never pay back; apply the check in [cloud-commitment-and-k8s-cost-guide.md](cloud-commitment-and-k8s-cost-guide.md#the-cheap-but-slow-engineering-time-trap).
- **Egress and bandwidth are where hosts differ most.** When one dimension dominates the bill, compute its cost at forecast volume on the current host and on the alternative before optimizing anything else.

---

## Vercel

**Billing shape:** flat per-seat subscription plus usage-based infrastructure above included allowances, shared across all projects on the team. Confirm whether a usage credit offsets infrastructure only or seats too, and when allowances reset.

| Dimension | Main lever |
|---|---|
| Seats | Remove inactive members; viewer roles where offered |
| Data transfer and origin transfer (GB) | CDN caching, SSG, compression, large files on external storage |
| Edge requests | Cache static assets, trim middleware scope |
| Function invocations, CPU time, memory | Cache responses, right-size memory, move work to background jobs |
| ISR reads and writes | On-demand revalidation, longer intervals, fewer paths |
| Image optimization (transformations, cache reads/writes) | Pre-optimize, long cache TTL, fewer size variants |
| Build minutes | Build caching, skip unchanged builds, fewer preview branches |
| Add-ons (observability, firewall, analytics) | Enable only where used |

**Tier decision:** the hobby tier is non-commercial under the terms of service (check the current terms); a commercial project or a second member needs a paid tier. Between paid usage and a larger allowance, use the crossover. Negotiate enterprise terms once usage is steady, with the per-dimension export in hand.

**Levers, ranked by typical impact:**

1. **Origin transfer.** Every cache miss, SSR request and API call goes back to origin. Statically generate pages that need no per-request data; set `s-maxage` plus `stale-while-revalidate` on API responses; serve large media and downloads from object storage behind a CDN.
2. **ISR writes.** A write re-renders the page and costs far more than a read. Replace time-based `revalidate` with on-demand revalidation (`revalidatePath` / `revalidateTag` from a CMS webhook); where time-based remains, set the interval to the real data freshness (hourly content → 3600, not 60); use plain SSG for content that rarely changes; cut combinatorial paths from locales × slugs; skip ISR on very low-traffic pages where regeneration costs more than caching saves.
3. **Functions.** Duration dominates for slow functions, invocation count for fast high-throughput ones. Cache responses; run independent fetches in parallel (`Promise.all`) instead of waterfalls; right-size memory from measured use (CPU usually scales with memory); keep bundles small to cut cold starts; move heavy work to queued background jobs.
4. **Middleware.** Without a `matcher` it runs on every request, including `_next/static`, `_next/image` and `favicon.ico`. Scope it, and keep database calls and heavy logic out of it. Middleware invocations far above page views mean a missing matcher.
5. **Images.** Source transformations are the expensive operation. Use modern formats, raise `minimumCacheTTL` above the framework default, set `sizes` correctly, pre-optimize at build or upload time, and bypass the platform optimizer (`unoptimized` or a custom loader) when another image CDN already does the work.
6. **Build minutes.** Cache dependencies, use a monorepo task runner to skip unchanged packages, `ignoreBuildStep` for docs-only commits, limit auto-deploy branches, delete stale previews.

**Per-project placement.** Break team usage down per project; one landing site often dominates origin transfer. Keep a project on Vercel if it uses ISR, middleware or edge features; if bandwidth is the main cost and SSR is not needed, statically export it and compare static hosting (for example Cloudflare Pages); if it needs always-on compute with steady traffic, compare flat-priced container hosts (Railway, Render, Fly.io) where per-invocation pricing and cold starts lose; if it is media-heavy, compute metered transfer at forecast volume against a flat or unmetered-bandwidth host and move above the crossover when the team can run it.

**Alerts:** set a spend-management cap or alert threshold, and alert when a dimension passes most of its allowance mid-cycle, ISR writes grow faster than content changes, or build minutes burn half the allowance in the first week.

---

## Supabase

**Billing shape:** base fee per organization, compute per project per hour by size (each size up is a multiple of the one below), and overage on egress, storage, MAUs and function invocations. All projects roll up to one invoice, so attribute per project from the usage breakdown. Pausing a project stops its compute charge; check the tier's pause and auto-pause rules.

| Dimension | Main lever |
|---|---|
| Database compute | Right-size, pooling, query and RLS tuning, pause idle projects |
| Database size and disk | Bloat control, archiving, retention |
| Object storage and transformations | Cleanup policies, compress before upload, CDN in front |
| Egress (database, storage, functions) | Pagination, column selection, server-side aggregation, CDN |
| Auth MAUs | Review anonymous auth and bots |
| Edge Function invocations | Move database logic into database functions, cache, batch |
| Realtime connections and messages | Subscribe only where live data is shown |
| Branches, replicas, add-ons | Delete branches after review; replicas only when the primary saturates |

**Tier decision:** free fits prototypes and dev or staging that stay inside every limit with headroom (check the auto-pause rules before anything user-facing depends on it). Move to paid once a limit is regularly hit, backups are needed, or the fee is less than the engineering time spent working around free constraints. Higher tiers are feature purchases (compliance reports, SLAs); the crossover settles usage and a feature need can override it.

**Levers, ranked by typical impact:**

1. **Compute.** Pool connections on every project (direct connections cost more memory per client); tune queries with `EXPLAIN ANALYZE`; index `WHERE`/`JOIN`/`ORDER BY` columns and drop unused indexes; write RLS policies as simple index-backed predicates (`auth.uid() = user_id`) rather than correlated subqueries, which run per row; tune autovacuum on high-churn tables when dead tuples grow. Downsize when average CPU stays well below capacity (for example consistently under 20%). Run dev and staging on the smallest size or free projects; they need not match production.
2. **Egress.** Paginate every list query, select only needed columns, aggregate server-side with RPC database functions, cache client-side, put a CDN in front of public storage.
3. **Storage.** Delete orphaned uploads on a schedule or by trigger, compress and resize before upload, use short-lived signed URLs for private assets.
4. **Auth MAUs.** Check the current MAU definition; unintended anonymous sign-ins and bots inflate the count on public apps.
5. **Edge Functions.** Logic that only reads or writes the database belongs in a database function called via `.rpc()`; cache non-user-specific responses; batch items per call. Failed invocations still bill.
6. **Realtime.** Open channels only on screens that show live data, clean up presence on unmount or idle, poll for data that changes rarely.

**Watch:** database growth per week (sudden jumps mean bloat or unexpected volume), peak connections against the compute size, egress per project per week.

**Alternatives** only after optimization and when Supabase is the dominant line: scale-to-zero serverless Postgres for spiky or read-heavy loads with simple auth; local-first sync for offline-first mobile (cuts egress and Realtime); self-hosted Postgres plus object storage behind a CDN for media-heavy egress; a distributed SQL database if you need multi-region writes.

---

## Cloudflare

| Product | Metered dimensions | Main lever |
|---|---|---|
| Zone plans | monthly fee per domain; feature set | Stay on the free plan unless a paid-only feature is used |
| Workers | requests; CPU time per invocation, with a per-plan cap | Keep Workers I/O-bound; cache instead of compute |
| R2 | storage GB-month; Class A ops (writes, lists); Class B ops (reads); no egress charge | Batch writes; move egress-heavy objects here |
| Pages | builds; no bandwidth charge on static assets | Move static sites here when bandwidth is the cost |
| Images | images stored; images delivered | Compare with build-time resizing |
| Stream | minutes stored; minutes delivered | Compare with self-encoding plus R2 |
| Workers KV | reads; writes, deletes and lists; storage | Read-heavy use only |
| D1 | rows read (includes rows scanned); rows written; storage | Index filtered columns |

DNS, CDN bandwidth, TLS and basic DDoS protection sit in the free plan; confirm the current free quotas, because they decide whether a small workload costs anything.

**Zone plan decision:** upgrade a zone only when it uses a paid-only feature: managed WAF rulesets or custom firewall rules, edge image optimization with no other image pipeline, detailed cache analytics, more URL rules than free allows (check first whether Transform and Cache Rules cover it), or a support SLA where downtime costs revenue. Downgrade zones whose paid features went unused for a quarter. For usage products with a paid base fee, use the crossover.

**Workers.** CPU time is billed, not wall-clock: a Worker waiting 200 ms on `fetch()` with 2 ms of CPU bills 2 ms, so Workers are cheap for I/O and expensive for parsing, rendering and string work. Watch p50 and p99 CPU; a p99 near the plan cap fails on free or grows the bill on paid. Cron triggers count as requests: every minute is 60 × 24 × 30 = 43,200 requests per 30-day month, every five minutes 8,640. All routed domains and `*.workers.dev` share one quota.

**R2 egress crossover.** Monthly cost per provider = storage GB × storage rate + egress GB × egress rate + writes × write rate + reads × read rate. Compute it for the current provider and R2 from your traffic export. R2 wins when the egress term dominates (media, downloads, CDN origins, uploads read many times); a write-heavy, rarely read bucket may save little because operation rates dominate. Shape, not a quote: serving 1 TB a month pays 1,000 × the per-GB egress rate at a hyperscaler and none of it on R2. Add migration cost and the old provider's egress for the one-time copy.

**Other levers, ranked:** batch R2 writes (Class A ops cost far more than reads; per-request logging to R2 grows faster than storage); keep KV for read-heavy data (config, flags, cached responses) and use D1 or Durable Objects for write-heavy or strongly consistent data; index D1 filters because scanned rows bill; move static sites paying for bandwidth elsewhere to Pages and check builds per month against your merge and preview rate; cache identical per-user Worker responses at the CDN; compare Images and Stream against build-time resizing and your existing pipeline, since for a handful of videos the integration may not pay back.

**Migration safety:** verify imported MX, TXT (SPF, DKIM, DMARC) and CNAME records before switching nameservers; keep mail, SSH and other non-HTTP records DNS-only; test on the preview subdomain before moving DNS; expect a cold cache and higher origin load for a day or two, and compare hit ratios with the old baseline.

---

## Stripe

| Dimension | Unit | Main lever |
|---|---|---|
| Card processing | % of amount + fixed fee per successful charge | IC+ pricing, payment-method mix |
| International card and currency conversion | extra % per charge | Local entities, local methods, pricing in the buyer's currency |
| Bank debits (ACH, SEPA and similar) | % per charge, often capped | Steer large B2B invoices to bank debit |
| Payouts | per payout or % | Batch payouts; avoid instant payouts by default |
| Billing and Tax add-ons | % of billed or taxed volume | Use only needed features; compare flat-fee tools |
| Fraud screening | per screened charge | Skip low-risk traffic; manual-review tier only if used |
| Disputes | fixed fee per dispute, win or lose | Descriptors, 3-D Secure, evidence workflow |
| Connect | depends on charge and account type | Charge type that matches the business model |

**Stacked-fee arithmetic.** Effective % = base card rate + every add-on % that applies (Billing, Tax, international, conversion); fixed part = per-charge fee + per-charge screening fee. Illustrative inputs (base 2.9% + $0.30, Billing 0.5%, Tax 0.5%, screening $0.05): a domestic subscription charge costs 2.9 + 0.5 + 0.5 = **3.90% + $0.30 + $0.05**; an international card adds its surcharge (1.5% in the same set, giving 5.40%), and conversion adds more. The fixed fee dominates small charges: a $5 charge at the same base costs (0.029 × 5 + 0.30) / 5 = 8.9% effective, so compute the effective rate per price point before choosing monthly versus annual billing on low-priced plans.

**Levers, ranked by typical impact:**

1. **Interchange-plus (IC+).** Blended pricing absorbs interchange variance; IC+ passes through interchange and scheme fees plus a markup. Request an IC+ quote when blended rate × monthly volume exceeds Σ over card types of (interchange + scheme fee) × volume share, plus the markup, computed from your own card-mix export, not from a quoted volume threshold. Debit-heavy and domestic mixes gain most; premium-card and international-heavy mixes may gain little.
2. **Payment-method mix.** A capped bank-debit fee beats a percentage card fee at every amount in the illustrative set (on $10K: $5 versus $290.30), and the gap grows with invoice size; the trade-offs are settlement time and return risk. Localize billing entities or offer local methods where international volume justifies the entity cost.
3. **Disputes and screening.** Networks run dispute-ratio monitoring programs with fines and account termination; read the current thresholds from your processor or the network rules. Screening pays when fee per screened charge < dispute rate × share of disputes it prevents × (dispute fee + lost goods or revenue + handling cost); with illustrative inputs ($0.05 fee, $15 dispute fee, $50 ticket, half of disputes prevented) the break-even dispute rate is about 0.15%. Skip screening on low-risk traffic where rules allow, track the false-positive rate (blocked customers are a hidden cost), set clear descriptors, use 3-D Secure on high-risk charges to shift liability, and contest disputes with evidence (a win returns the charge, not the fee).
4. **Billing and Tax add-ons.** Both are percentages of volume, so they grow with revenue while the work they save does not. Billing earns its fee when you use dunning, proration, metered billing or the hosted portal; skip it for a fixed charge with no plan changes or when your app owns subscription logic. Compare Tax's percentage × taxed volume against flat-fee tax tools and merchant-of-record providers; above the crossover the percentage loses. Audit whether enabled features are used.
5. **Connect.** Direct charges: the connected account pays fees, the platform takes an application fee. Destination charges: the platform pays fees on the full amount, then transfers. Separate charges and transfers: full control, manual allocation. Pick the type that matches who owns the customer; remove unused connected accounts; use the application-fee field rather than transfer deductions for clean fee reporting.
6. **Idempotency.** Webhook retries without idempotency keys create duplicate charges that still incur fees.

**Negotiation.** Ask once volume is steady and predictable with a low dispute rate; no fixed threshold holds over time. Negotiable: IC+, the fixed per-charge fee (valuable at low ticket), dispute fees, bundled add-ons. Bring 3–6 months of volume, average ticket, card mix, dispute and refund rates, and competing quotes; contact sales, not support. Annual value = rate reduction × monthly volume × 12; for example, 0.3 percentage points on $200K/month is $7,200 a year. Weigh it against switching or integration effort.

**Watch:** effective fee rate by method and region, dispute rate against the network threshold, refund and failed-payment rates, against your own baseline. Route dispute-created events to an ops channel. A jump in monthly fees usually means a new product was enabled or the international share moved.

**Alternatives:** at high steady volume, processors with lower IC+ markups and routing control; for SaaS needing tax and billing without a tax team, merchant-of-record providers; for low average tickets, any processor with a lower fixed fee.

---

## GitHub and CI/CD

| Service | Metered dimensions | Main lever |
|---|---|---|
| Plan | per user; included Actions minutes and storage | Tier only for features you use |
| Actions (hosted runners) | minutes × OS multiplier, or per-runner-size rate | Linux by default, caching, fewer redundant runs |
| Actions storage | artifact and cache GB-month | Short retention |
| Self-hosted runners | your infrastructure, plus any platform per-minute charge | Breakeven against hosted minutes |
| Copilot | per assigned seat | Seat audit |
| Git LFS | storage and bandwidth in data packs | LFS only for large changing binaries |
| Codespaces | compute hours by machine size; storage while stopped | Auto-stop, retention, small machines |
| Packages | storage; data transfer out | Delete old versions |

**Plan decision:** stay on free while the included minutes suffice and private repos need no governance; move up for required reviewers or CODEOWNERS enforcement on private repos, then for SSO, audit-log streaming, IP allow lists or advanced security. Plans are per user, so upgrade cost grows with headcount while included minutes may not; when minutes drive the decision, compare the tier fee with overage minutes or self-hosted runners via the crossover.

**Actions arithmetic.** Cost in included minutes = wall-clock minutes × OS multiplier; look up the current multipliers. macOS is the most expensive by a wide margin, so a job that runs identically on Linux wastes the difference. A larger runner is cheaper only when speedup > rate_large / rate_standard: a runner at twice the per-minute rate must finish in under half the time. Measure on your own builds; parallel compiles often clear the bar, single-threaded test suites rarely do. Self-hosted saving = hosted minutes × hosted rate − (runner infrastructure + any platform self-hosted charge + engineering time for provisioning, patching, isolation and autoscaling); check whether the platform charges for self-hosted minutes before assuming they are free.

**Levers, ranked by typical impact:**

1. Linux runners for everything that does not need macOS or Windows (unit tests, lint, Docker builds, deploys).
2. Dependency caching keyed on lockfile hashes; confirm cache hits in logs.
3. Path filters (`paths-ignore` for docs and markdown) and no full CI on draft PRs.
4. Cancel superseded runs with a concurrency group per workflow and ref (`cancel-in-progress: true`).
5. Quarterly Copilot seat audit from usage metrics; no automatic reclamation by default. Compare organization and individual plans for small teams without central policy needs.
6. Artifact retention in days, not months, for artifacts consumed within the run.
7. Codespaces: org idle auto-stop in tens of minutes, smallest machine by default, retention policy that deletes stopped Codespaces, slim dev-container images.
8. LFS only for binaries above roughly a megabyte that change often; build artifacts go to artifact or package storage; prune old objects; open-source projects host large assets externally.
9. Packages: delete old versions; for heavy private downloads, compare a cloud registry in the consumers' region.
10. Self-hosted runners when hosted minutes consistently exceed the allowance, or you need GPU or ARM, and the breakeven is positive.

**Switching CI platforms:** compare on monthly minutes by OS, concurrency, cache behaviour, seats and pipeline migration effort. Stay on the platform that hosts the code while usage fits; move CI only when a named need (built-in scanning, your-own-compute scale, advanced parallelism) outweighs migration, and remember that moving CI often means moving the repository.

## IaC Cost Guardrails

Catch infrastructure cost increases at code review: an IaC cost tool (Infracost is the common open-source example) prices the plan's resource changes and posts current cost, proposed cost and delta on the pull request, and can fail the check above a threshold.

**Budget-threshold merge gate:**

1. **Policy:** absolute (block if the monthly delta exceeds an amount), relative (block if the increase exceeds a share of the baseline), or per-resource (block if one new resource exceeds an amount). Set the threshold from your own budget.
2. **Wire it into CI** with the tool's actions pinned to reviewed releases or SHAs.
3. **Express the gate as policy code** beside your other checks:

```rego
# block PRs that raise monthly cost by more than the budget threshold
deny[msg] {
  diff := input.diffTotalMonthlyCost
  diff > 50
  msg := sprintf("PR increases monthly cost by $%.2f. Budget threshold is $50.", [diff])
}
```

The input field names and how the policy file is passed change between releases; check the tool's guardrails documentation (https://www.infracost.io/docs/infracost_cloud/guardrails/).

| Situation | Recommendation |
|---|---|
| IaC changes land weekly or more often | Cost diff on every PR |
| Single developer, infrequent infra changes | Manual cost review before merge |
| Cloud cost is a top business concern | Hard block thresholds; approvals for large deltas |
| Early stage, minimal IaC | Skip; revisit when IaC changes become frequent |

**Scope:** these tools price IaC-managed resources only. SaaS usage (hosting, database-as-a-service, AI APIs) and runtime usage the IaC does not determine need platform dashboards ([cost-monitoring-setup.md](cost-monitoring-setup.md)) and observability.

---

## Monitoring and Analytics

| Vendor type | Metered dimensions | Surprise dimension |
|---|---|---|
| Product analytics (PostHog, Mixpanel) | events; recordings; flag requests; surveys; warehouse rows, each product with its own allowance | Auto-captured events nobody queries |
| Error tracking (Sentry) | errors; spans or transactions; replays; attachments or profiles, with quota tiers or reserved volume | Noisy unactionable errors |
| Full-stack observability (Datadog) | hosts for infra and APM; log GB ingested plus events indexed by retention; RUM sessions; synthetic runs; custom metrics per metric-and-tag combination | Custom-metric cardinality |
| Session replay (LogRocket and others) | sessions, usually a 30-minute activity window | Several sessions per user per day |

**Levers, ranked by typical impact:**

1. **Audit event volume.** Replace auto-capture with an allowlist of the events that appear in a dashboard, report or alert (a few dozen usually covers the questions asked). Aggregate high-frequency signals (scroll depth, time on page) client-side into one summary event. Track actions, not page views; page traffic belongs in a lightweight analytics tool. Opt internal and test users out.
2. **Sample recordings.** Recordings scale with visits: 50K daily visitors at one session each is about 1.5M recordings a month at full capture, most never watched. Record a low baseline share sized to review capacity, plus conditional recording on errors, rage clicks or specific pages; for error-linked replay, set the general session rate near zero and the on-error rate higher.
3. **Filter noisy errors.** Inbound filters for browser extensions, legacy browsers and crawlers; a `beforeSend` hook for unactionable types (for example chunk-load errors); fingerprinting rules so one bug is one issue; per-key rate limits.
4. **Lower trace sample rates** in production (for example 5%), per endpoint where the SDK allows; raise them temporarily for an investigation or for tail latency on rare endpoints.
5. **Control log volume at the source.** Production level `warn` or `error`, no request or response bodies, index only queried fields, archive raw logs to object storage, drop noisy patterns before indexing.
6. **Control custom-metric cardinality.** No user IDs, request IDs or timestamps as tags; each unique combination is a billable metric.
7. **Exclude health, readiness and metrics endpoints from APM**, and buy only the observability products you use; a small team often needs infrastructure monitoring plus error tracking, not the full bundle.
8. **Consolidate overlapping tools.** Paying for separate analytics, replay, flags and error tools often duplicates capability; check which products one vendor covers today before consolidating.
9. **Clean up archived flags and unused SDKs;** stale flags still generate evaluation requests and unused SDKs still send data.

**Self-host versus SaaS:** self-host when you have infrastructure capacity, data-residency rules forbid third-party telemetry, or SaaS cost at your scale exceeds running it yourself (full analytics stacks need ClickHouse- and Kafka-class operations; single-container tools for errors, uptime or simple web analytics are cheap to run). Stay on SaaS when the team is small and infrastructure time is expensive, when usage fits the free allowances, or when the self-hosted edition lacks or lags features you need.

---

## Email (Resend)

| Dimension | Main lever |
|---|---|
| Sends per month, and a daily cap on the free tier | Digests, preference gating, deduplication |
| Overage blocks above the included quantity | Tier crossover, volume reduction |
| Sender domains per tier | Consolidate brands onto fewer domains |
| Dedicated IPs and add-ons | Only when volume and reputation justify them |
| Marketing contacts stored | Remove inactive and suppressed contacts |

Check whether bounced and rejected emails count toward quota, whether unused sends roll over, and when the month resets; these decide how much list hygiene saves.

**Tier decision:** a daily cap is hit on the busiest day, not the average one, so compare the maximum daily send over the last month with the cap. Upgrade when the busiest day approaches it, a second domain or paid feature is needed, or monthly volume will cross the free ceiling within a quarter; between paid tiers, use the crossover.

**Waste, ranked:** a separate email for every minor event (audit each trigger: would the user notice if it stopped?); per-event notifications where a digest serves; sends to dead addresses (suppression list checked on every send; bounces also hurt reputation); duplicate sends from racing workers or webhook handlers (idempotency keys or a sent log); extra sender domains kept by habit; per-recipient calls for bulk sends where a batch endpoint exists. Slow webhook receivers do not cost sends but get retried and mask delivery problems: acknowledge immediately, process asynchronously.

**Alerts:** projected month-end volume above the included quantity; busiest day near the cap; bounce and complaint rates above baseline or above the bulk-sender thresholds mailbox providers publish.

**Switching:** compare providers on monthly and peak-daily volume, domains, deliverability needs and setup. Cloud-provider email services are cheapest per email at high volume but need your own reputation and bounce handling; transactional-focused providers trade price for deliverability. Count migration effort (domain authentication, templates, webhooks, suppression-list export) before switching for a small saving.

---

## Domains and DNS

| Dimension | Main lever |
|---|---|
| Renewal, per domain per year by TLD | Registrar with at-cost or low-markup renewals |
| First-year registration | Ignore promos; compare renewal prices |
| WHOIS privacy | Registrar that includes it |
| DNS hosting | Free DNS at a provider of your choice; premium only for strict uptime needs |
| Transfer | Usually one year of renewal at the new registrar |
| Add-ons (email, builders, "protection" bundles) | Remove what is not used |

Prices vary by TLD more than by registrar; always compare the renewal price for the TLD you hold. First-year prices are often loss leaders several times below renewal. Watch pre-selected add-ons in the cart. DNS need not live at the registrar: point nameservers wherever DNS is free and keep the registration wherever renewal is cheapest. When a registrar sells or closes its domain business, recheck renewal prices at the new owner.

**Transfer arithmetic.** Annual saving per domain = (renewal + privacy + premium DNS at the current registrar) − (the same at the new one). A transfer usually charges one year of renewal and adds that year, so timed before the renewal date it replaces a renewal rather than adding a cost. Portfolio saving = per-domain saving × domains kept: drop unused domains first, since transferring one you will not renew wastes the fee. Registry and ICANN transfer locks follow registration or a previous transfer, and some TLDs add restrictions; check each TLD's policy before picking the date. Steps: unlock, get the EPP code, start the transfer, approve by email, confirm DNS records survived.

**Portfolio hygiene:** audit every domain annually across all registrars (registration and renewal date, renewal price, use: active site, email only, parked, unused); cancel auto-renewal on anything not serving traffic, receiving email or protecting a brand; set reminders about 30 days before each renewal to decide renew, transfer or expire; check that auto-renewal is on a watched card; consolidate DNS onto one provider; report renewal, privacy and DNS as one portfolio line.
