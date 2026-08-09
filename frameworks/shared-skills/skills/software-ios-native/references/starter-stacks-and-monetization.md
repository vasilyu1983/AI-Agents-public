# Starter Stacks: Zero to Monetized + Engaged

Use this reference when the question is "what is the **leanest** stack that gets a native iOS app to monetization and engagement, and when do I graduate to the next combo?" It assembles pieces that live in other skills into one decision ladder. It does not re-explain StoreKit internals (see `../../software-payments/`), the on-device AI engine (see `../../software-ios-ai-engine/`), or BaaS tradeoffs (see `../../software-baas-platforms/`) — it tells you which combination to reach for and what each one cannot do.

Verified June 2026.

## Table of Contents

- [The One Decision](#the-one-decision)
- [The Graduation Ladder](#the-graduation-ladder)
- [Why CloudKit Alone Stops Short](#why-cloudkit-alone-stops-short)
- [The CloudKit + Cloudflare Hybrid](#the-cloudkit--cloudflare-hybrid)
- [Monetization Layer](#monetization-layer)
- [On-Device AI as the Free Tier (2026 pattern)](#on-device-ai-as-the-free-tier-2026-pattern)
- [Engagement Layer](#engagement-layer)
- [Server-Side Monetization Traps](#server-side-monetization-traps)
- [Copy-Paste Scaffolds](#copy-paste-scaffolds)
- [Anti-Patterns](#anti-patterns)
- [Sources](#sources)

## The One Decision

Monetization and engagement both need **server-side state CloudKit cannot hold**: subscription entitlements driven by App Store webhooks, push targeting, and analytics. So the real choice is *how much server* you add to a CloudKit core, and *when*.

Default for a privacy-first Apple-only app shipping fast: **CloudKit for user data + a thin Cloudflare Worker for the server-side jobs + RevenueCat for subscriptions + a push/analytics layer.** Each rung below is added only when the app actually needs it. Do not start at the bottom of the ladder.

## The Graduation Ladder

| Tier | Stack | Adds | Add it when |
|---|---|---|---|
| 0 | SwiftUI + SwiftData/CloudKit private DB | Free offline-first per-user sync, zero server | Single-platform, private data, no subscriptions yet |
| 1 | + Cloudflare Worker (Queues, Workflows, Cron) | Webhooks, async/AI proxy, scheduled jobs — the things CloudKit can't | You add subscriptions, server AI, or any scheduled/server logic |
| 2 | + RevenueCat (on StoreKit 2) | Paywall A/B testing, entitlement sync, subscription analytics | You sell subscriptions and want experiments + cross-platform entitlements |
| 3 | + Supabase (Postgres) | Relational queries, web client, shared/public data, auth at scale | You need cross-platform users, a web app, or relational data CloudKit can't model |
| 4 | + dedicated push/analytics (OneSignal / PostHog) | Delivery analytics, segmentation, rich push, funnels, A/B beyond paywall | Engagement becomes a growth function, not a single `requestAuthorization` call |

Two rules for the ladder: never skip to Tier 3 to "future-proof" (Postgres you don't query is operational surface you don't need), and never collapse Tier 2 into raw StoreKit 2 unless the product is one-time purchases, single-platform, or past the scale where RevenueCat's 1% beats an engineer's time.

## Why CloudKit Alone Stops Short

CloudKit is the correct Tier-0 core — free, offline-first, Apple-native, private-by-default. It structurally **cannot**:

- Receive App Store Server Notifications (subscription webhooks land on a server, not in a CKContainer).
- Serve cross-platform or web clients with the same data contract.
- Run scheduled server work, admin/service-role writes, or moderation queues.
- Provide analytics over all users' data (private DBs are per-user by design).

These are exactly the capabilities monetization and engagement require. See [icloud-cloudkit-app-skeleton.md → No-Server Boundaries](icloud-cloudkit-app-skeleton.md#no-server-boundaries) for the full list. The moment one of them becomes a requirement, you are at Tier 1, not redesigning Tier 0.

## The CloudKit + Cloudflare Hybrid

This is the "super efficient and simple" combination: CloudKit owns private user data; a small Cloudflare Worker (~200 lines is a real, reported size for a push or webhook endpoint) owns the server-side jobs. The Worker is the cheapest place to add exactly what CloudKit lacks, without standing up a database you don't need yet.

Worker responsibilities in this hybrid:

- **Subscription webhook receiver** — App Store Server Notifications V2 endpoint (or the RevenueCat webhook once Tier 2 is in). Verifies, dedupes, updates entitlement state.
- **AI / long-task proxy** — the app calls the Worker, the Worker calls the cloud model, and on completion notifies the app via push or a polled request ID. Keeps API keys off the device.
- **Scheduled work** — Cron Triggers for digests, re-engagement, cleanup; Queues + Workflows for retry-safe async steps.

Keep the data boundary clean: the Worker does not become a second source of truth for user content — that stays in CloudKit. The Worker holds server-only state (entitlements, job status, secrets). For the broader runtime/decomposition view of this split, see `../../software-architecture-design/` (BFF / tool-gateway patterns) and for Worker implementation depth, `../../software-cloudflare-wrangler/`.

## Monetization Layer

The store-of-record is always **StoreKit 2** (Apple policy: digital goods in a native app go through Apple, not Stripe). The June 2026 indie default is **RevenueCat on top of StoreKit 2** — they are layers, not rivals; RevenueCat uses StoreKit 2 under the hood, so migrating off it later is straightforward. RevenueCat is free under $2,500/mo tracked revenue, then ~1%.

- Start raw StoreKit 2 only for: one-time purchases, single-platform, hard zero-dependency requirement, or revenue large enough that 1% outweighs the saved engineering.
- The decision table and the three-layer entitlement registry (registry → API enforcement → UI paywall) live in [../../software-payments/references/storekit2-native-patterns.md](../../software-payments/references/storekit2-native-patterns.md). Do not duplicate them here.
- iOS-side StoreKit traps already in this skill: the **Paid Apps Agreement** silent-empty-products blocker and the Xcode 26 `SubscriptionStatus.all` stale-cache bug — see [../SKILL.md](../SKILL.md) StoreKit rows. Check the Paid Apps Agreement *first* when `Product.products(for:)` returns empty.

Paywall design fact worth the table: RevenueCat's 2026 data across ~115k apps shows **hard paywalls convert ~10.7% vs ~2.1% for free-trial paywalls**. Test in priority order: pricing (annual-vs-monthly default) → trial length → headline framing → feature list → visual asset. This is engagement design, not infra — pair it with the value-preview rule in [../../software-ios-design/references/ios-shipping-antipatterns.md](../../software-ios-design/references/ios-shipping-antipatterns.md) (no paywall before value).

## On-Device AI as the Free Tier (2026 pattern)

The genuinely new monetization combination in 2026: use **Apple Foundation Models on-device for the free tier** (zero inference cost, unlimited, offline, fast) and reserve a **cloud LLM for the premium tier** (~$0.50/user/mo typical). On-device AI stops being just a privacy/latency win and becomes the free-tier value proposition that justifies the upgrade — the marginal cost of the free tier is zero, so generosity there is free.

- The engine architecture (intent router → composer → cloud fallback) and its cost/latency table are in [../../software-ios-ai-engine/references/three-tier-architecture.md](../../software-ios-ai-engine/references/three-tier-architecture.md). This reference only adds the *pricing* framing: Tier 1 (on-device) = free plan, Tier 2 (cloud) = paid plan, and the paywall gates the jump.
- Before scoping any AI app in a saturated category (astrology, tarot, etc.), read the **4.3(b) gate** in [../../software-ios-ai-engine/SKILL.md](../../software-ios-ai-engine/SKILL.md) — "AI horoscope reader with a Day-1 paywall" is a rejection, and adding AI raises the unique/high-quality bar rather than clearing it.
- Cloud calls leaving the device now require **explicit consent disclosure** (2026 App Review rule) — see anti-pattern #28 in [../../software-ios-design/references/ios-shipping-antipatterns.md](../../software-ios-design/references/ios-shipping-antipatterns.md).

## Engagement Layer

Push opt-in correlates with large engagement lifts (reported north of 80% in some verticals), so the highest-leverage decision is **opt-in timing**, not the push vendor. Defer the permission prompt behind a meaningful action with an obvious notification benefit (anti-pattern #2 in the shipping list).

- **Tier 1 push**: a Cloudflare Worker can talk to APNs directly and send for free at small scale. Sufficient for transactional and re-engagement pushes.
- **Graduate to OneSignal / Firebase** when you need delivery + open + click analytics, segmentation, rich media, or push A/B tests — building those on a bare Worker is rebuilding a product.
- **Analytics**: a privacy-preserving product-analytics layer (e.g. PostHog) for activation/retention funnels. Define the tracking plan before instrumenting — see `../../marketing-product-analytics/`. Keep analytics consent consistent with the privacy nutrition label.

## Server-Side Monetization Traps

These are the things a CloudKit-only developer has never had to handle and gets wrong on the first subscription ship. They apply to the Worker (or any server) that receives subscription events.

- **Use App Store Server Notifications V2, not V1.** V1 is deprecated; Apple only improves V2. Configure the endpoint for *both* Production and Sandbox.
- **Make webhook processing idempotent.** Apple and RevenueCat can deliver the same event more than once. Dedupe by the event's unique ID and process exactly once — non-idempotent handlers double-grant or double-revoke entitlements.
- **Re-fetch, don't trust the payload.** After any subscription webhook, call back for the authoritative state (with RevenueCat: `GET /subscribers`) and sync *that* to your store, rather than mutating entitlements from the notification body. One code path, always the same shape, robust to event ordering.
- **Verify the auth header on every notification.** RevenueCat lets you set an `Authorization` header in the dashboard; your endpoint must check it. For raw ASSN, verify Apple's signed JWS. An unauthenticated webhook endpoint is a free entitlement grant for anyone who finds the URL.
- **Return HTTP 200, or expect retries.** Any non-200 is a failure; RevenueCat retries up to 5 times with backoff. Return 200 fast (ack, then process async via a Queue) so a slow downstream doesn't trigger a retry storm.
- **Reconcile client and server entitlement timing.** The client may learn about a new entitlement before your webhook lands (or vice versa). Gate paid UI from a single entitlement store that both the StoreKit `Transaction.updates` stream and the server webhook update; never from two independent sources.

## Copy-Paste Scaffolds

Real drop-in scaffolds live in [../assets/scaffolds/](../assets/scaffolds/). Pick your app class, copy the listed files, fill the `// TODO` markers:

- [app-class-blueprints.md](../assets/scaffolds/app-class-blueprints.md) — **start here**: 4 app classes (CRUD/notes, AI wrapper, content/feed, utility-IAP) → which tier, which scaffolds, which monetization model, rough cost.
- [entitlement-and-paywall.md](../assets/scaffolds/entitlement-and-paywall.md) — `EntitlementStore` (StoreKit 2 single source of truth) + `PaywallGate` modifier. Same store for every paid class.
- [push-and-engagement.md](../assets/scaffolds/push-and-engagement.md) — `PushManager` with deferred opt-in + `Reachability`.
- [cloudflare-worker-backend.md](../assets/scaffolds/cloudflare-worker-backend.md) — Worker: subscription webhook (with the traps below baked in), AI/secret proxy, push sending.

## Anti-Patterns

- **Starting at Tier 3.** Standing up Postgres + auth + edge functions for an app that two devices and one user will ever touch. Start at Tier 0/1 and graduate on evidence.
- **Treating the Worker as a second content store.** User data belongs in CloudKit; the Worker holds server-only state. Splitting content across both creates two sources of truth and sync bugs.
- **Defaulting to RevenueCat reflexively.** It is a coordination layer, not a requirement. For one-time purchases or single-platform simple subscriptions, raw StoreKit 2 is less surface.
- **Webhook handler mutates entitlements directly from the payload.** Non-idempotent, order-sensitive, and wrong on duplicate delivery. Re-fetch authoritative state instead.
- **Cold permission prompts.** Push/ATT/tracking requested on first launch burns the one-shot dialog before the user has any reason to grant it. Gate behind value.
- **On-device AI used only as a cost-saver, not a free-tier product.** If the free tier feels like a degraded paid tier, it doesn't convert. Make the on-device tier genuinely useful — its marginal cost is zero.

## Sources

- Apple: [CloudKit](https://developer.apple.com/icloud/cloudkit/) · [App Store Server Notifications](https://developer.apple.com/documentation/appstoreservernotifications)
- Cloudflare: [Workers](https://developers.cloudflare.com/workers/) (Queues, Workflows, Cron Triggers)
- RevenueCat: [Apple Server Notifications](https://www.revenuecat.com/docs/platform-resources/server-notifications/apple-server-notifications) · [Webhooks](https://www.revenuecat.com/docs/integrations/webhooks) · [State of Subscription Apps 2026](https://www.revenuecat.com/state-of-subscription-apps/)
- The Swift Kit: [StoreKit 2 vs RevenueCat (2026)](https://theswiftk.it.com/blog/storekit-2-vs-revenuecat-ios-subscriptions)
- OneSignal: [Push best practices 2026](https://onesignal.com/blog/onesignal-guide-push-notification-best-practices-2026/)

When in doubt about a specific layer, follow the cross-links above into the owning skill rather than expanding this file — it is a map, not a manual.

To industrialize this stack across *many* apps — shared SPM packages, one-cert multi-app CI, agent build loop, and a default stack per app class — see [ios-app-conveyor.md](ios-app-conveyor.md).
