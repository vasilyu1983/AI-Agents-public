# App-Class Blueprints

Pick the class your app matches, then copy the listed scaffolds and start. Each blueprint names the stack tier, the exact scaffold files, the monetization model, and the rough cost. Classes are defined by **data + monetization shape**, not domain — a habit tracker and a journal are the same class.

Stack tiers and the graduation logic: [../../references/starter-stacks-and-monetization.md](../../references/starter-stacks-and-monetization.md).
Scaffolds: [entitlement-and-paywall.md](entitlement-and-paywall.md) · [push-and-engagement.md](push-and-engagement.md) · [cloudflare-worker-backend.md](cloudflare-worker-backend.md). CloudKit stack: [../template-ios-cloudkit-persistence-stack.md](../template-ios-cloudkit-persistence-stack.md).

## At a glance

| App class | Tier | Persistence | Monetization | Server? | Scaffolds to copy |
|---|---|---|---|---|---|
| Local-first CRUD / notes | 0–1 | SwiftData + CloudKit private | One-time unlock or light sub | Only if subs | CloudKit stack (+ entitlement/paywall if paid) |
| AI wrapper | 1–2 | SwiftData/CloudKit | Subscription; on-device free / cloud premium | Yes (AI proxy) | All four |
| Content / feed / social | 2–3 | Supabase (Postgres) + CloudKit cache | Subscription, sometimes ads | Yes (data + auth) | entitlement/paywall, push, Worker; Supabase over CloudKit |
| Utility with IAP | 0–2 | SwiftData (local) | One-time unlock or single sub | Usually no | entitlement/paywall (+ push optional) |

## 1. Local-first CRUD / notes

Notes, journals, trackers, habit apps, simple databases. One user, their own data, offline-first.

- **Tier 0** if free or one-time-unlock; **Tier 1** only if you add subscriptions (then you need a Worker for the webhook).
- **Persistence**: SwiftData + CloudKit private DB. Copy [../template-ios-cloudkit-persistence-stack.md](../template-ios-cloudkit-persistence-stack.md). Honor the CloudKit schema rules (no `#Unique`, optional relationships, defaults) — and on iOS 26 check the [sync regression](../../references/swiftdata-core.md#ios-26-cloudkit-sync-regression-known-trap-2026).
- **Monetization**: a one-time non-consumable "unlock pro" converts well here and needs no server. If you go subscription, add [entitlement-and-paywall.md](entitlement-and-paywall.md) + the webhook route of [cloudflare-worker-backend.md](cloudflare-worker-backend.md).
- **Engagement**: gentle reminders via [push-and-engagement.md](push-and-engagement.md), opt-in deferred behind "remind me".
- **Cost**: ~$0 backend at Tier 0; Worker free tier at Tier 1.

## 2. AI wrapper

Chat/assistant/generator apps. The 2026 archetype, and the one with a built-in pricing model.

- **Tier 1–2**. You need a Worker from day one (the [AI proxy](cloudflare-worker-backend.md) keeps the cloud-LLM key off the device) and a subscription store.
- **Monetization (the pattern)**: **on-device Apple Foundation Models = free tier** (zero inference cost, unlimited), **cloud LLM = premium** (~$0.50/user/mo). The free tier is genuinely useful, which is what converts. Engine architecture: `../../../software-ios-ai-engine/references/three-tier-architecture.md`. Gate the cloud route in the Worker by entitlement, not just in the UI.
- **Scaffolds**: all four — CloudKit stack (user history), [entitlement-and-paywall.md](entitlement-and-paywall.md), [push-and-engagement.md](push-and-engagement.md), [cloudflare-worker-backend.md](cloudflare-worker-backend.md).
- **Compliance**: cloud calls need explicit consent disclosure (anti-pattern #28 in `../../../software-ios-design/references/ios-shipping-antipatterns.md`); saturated categories (astrology, tarot) hit the 4.3(b) gate — adding AI raises the bar, not clears it.
- **Cost**: Worker free tier + per-user cloud inference only for paid users.

## 3. Content / feed / social

Shared/public data, multiple users see each other's content, often a web client too.

- **Tier 2–3**. CloudKit's private-by-design model is the wrong core here — you need relational queries, auth at scale, and cross-platform. Use **Supabase (Postgres)** as the source of truth; CloudKit can still cache a user's own slice for offline.
- **Monetization**: subscription (premium content/features) and sometimes ads — if ads, the ATT prompt must be deferred and consented (anti-pattern #1).
- **Scaffolds**: [entitlement-and-paywall.md](entitlement-and-paywall.md), [push-and-engagement.md](push-and-engagement.md), and the webhook route of [cloudflare-worker-backend.md](cloudflare-worker-backend.md) (or Supabase Edge Functions). BaaS tradeoffs: `../../../software-baas-platforms/`.
- **Engagement**: this class lives or dies on push + analytics — graduate to OneSignal/PostHog (Tier 4) early. Define the tracking plan first: `../../../marketing-product-analytics/`.
- **Cost**: Supabase free tier to start; grows with MAU and storage.

## 4. Utility with IAP

Single-purpose tools: converters, scanners, calculators, editors. Usually no server, simple gate.

- **Tier 0–2**. Often **no backend at all** — a one-time unlock verified on-device is enough.
- **Persistence**: SwiftData local; CloudKit only if settings/data should follow the user across devices.
- **Monetization**: one-time non-consumable unlock, or a single subscription tier. Copy [entitlement-and-paywall.md](entitlement-and-paywall.md); skip the Worker unless you sell subscriptions (then add the webhook route).
- **Engagement**: usually minimal; add [push-and-engagement.md](push-and-engagement.md) only if there's a genuine notification benefit.
- **Cost**: ~$0 backend.

## Shared rules across all classes

- Start at the lowest tier that fits; graduate on evidence, never to "future-proof".
- Gate all paid UI from one entitlement store (the scaffold) — never two independent checks.
- Defer every permission prompt (push, ATT, tracking) behind a value moment; first-launch cold prompts burn the one-shot dialog.
- Build with the iOS 26 SDK (mandatory for uploads from 2026-04-28) and re-verify Liquid Glass chrome after the bump.
- Run the pre-submit checklist in `../../../software-ios-design/references/ios-shipping-antipatterns.md` before every release.
