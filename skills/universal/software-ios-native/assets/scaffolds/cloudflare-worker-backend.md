# Scaffold: Cloudflare Worker Backend

Copy-paste serverless backend — the thin server CloudKit can't be. One Worker handles the three jobs a lean iOS app needs server-side: **subscription webhooks**, an **AI/secret proxy**, and **push token storage + sending**. App-class-agnostic; an AI wrapper uses the AI route, a notes app may use only the webhook route. Fill the `// TODO` markers.

Pairs with [entitlement-and-paywall.md](entitlement-and-paywall.md) (client) and [push-and-engagement.md](push-and-engagement.md) (token source). Architecture rationale: [../../references/starter-stacks-and-monetization.md](../../references/starter-stacks-and-monetization.md). For Worker depth: `../../../software-cloudflare-wrangler/`.

## When to Use

- Tier 1+ on the stack ladder: the moment you add subscriptions, server AI, or push.
- Keep user *content* in CloudKit. This Worker holds server-only state: entitlements, device tokens, job status, secrets. Two content stores = sync bugs.

## Cost shape

- Cloudflare Workers free tier covers small apps; KV/D1 for state. The Worker keeps API keys off-device (never ship a cloud-LLM key in the app binary).

## wrangler.toml

```toml
name = "app-backend"
main = "src/index.ts"
compatibility_date = "2026-01-01"

# State: KV for entitlements + dedupe, or swap for D1 if you need SQL.
kv_namespaces = [
  { binding = "ENTITLEMENTS", id = "TODO" },
  { binding = "SEEN_EVENTS",  id = "TODO" },   # webhook idempotency
  { binding = "DEVICE_TOKENS", id = "TODO" },
]

# Secrets (set with `wrangler secret put`): REVENUECAT_AUTH, LLM_API_KEY, APNS_KEY...
[triggers]
crons = ["0 9 * * *"]   # daily re-engagement digest; remove if unused
```

## src/index.ts

```typescript
export interface Env {
  ENTITLEMENTS: KVNamespace;
  SEEN_EVENTS: KVNamespace;
  DEVICE_TOKENS: KVNamespace;
  REVENUECAT_AUTH: string;   // shared secret you set in the RevenueCat dashboard
  LLM_API_KEY: string;       // never shipped in the app
}

export default {
  async fetch(req: Request, env: Env): Promise<Response> {
    const url = new URL(req.url);
    switch (url.pathname) {
      case "/webhook/subscription": return handleSubscriptionWebhook(req, env);
      case "/ai":                   return handleAIProxy(req, env);
      case "/entitlement":          return readEntitlement(req, env);
      default:                      return new Response("Not found", { status: 404 });
    }
  },
  async scheduled(_event: ScheduledEvent, env: Env): Promise<void> {
    // TODO: build + send the re-engagement digest via APNs. Keep it useful or drop it.
  },
};

// --- Subscription webhook: the traps live here ---
async function handleSubscriptionWebhook(req: Request, env: Env): Promise<Response> {
  // TRAP 1 — verify auth. An open webhook URL is a free entitlement grant.
  if (req.headers.get("Authorization") !== env.REVENUECAT_AUTH) {
    return new Response("Unauthorized", { status: 401 });
  }

  const event = await req.json<{ event?: { id?: string; app_user_id?: string } }>();
  const eventId = event.event?.id;
  const userId = event.event?.app_user_id;
  if (!eventId || !userId) return new Response("Bad payload", { status: 400 });

  // TRAP 2 — idempotency. Same event can arrive more than once. Process once.
  if (await env.SEEN_EVENTS.get(eventId)) {
    return new Response("ok (dup)", { status: 200 });
  }
  await env.SEEN_EVENTS.put(eventId, "1", { expirationTtl: 60 * 60 * 24 * 30 });

  // TRAP 3 — re-fetch authoritative state; do NOT mutate from the payload body.
  // One code path, always the same shape, robust to event ordering.
  const authoritative = await fetchSubscriberState(userId, env); // GET /subscribers
  await env.ENTITLEMENTS.put(userId, JSON.stringify(authoritative));

  // TRAP 4 — return 200 fast, or RevenueCat retries up to 5x with backoff.
  // If downstream work is slow, ack now and process via a Queue.
  return new Response("ok", { status: 200 });
}

async function fetchSubscriberState(userId: string, _env: Env) {
  // TODO: call RevenueCat GET /subscribers/{userId} (or App Store Server API for
  // raw ASSN V2 — use V2, V1 is deprecated). Return a normalized { isPro, expires }.
  return { isPro: true, expires: null };
}

async function readEntitlement(req: Request, env: Env): Promise<Response> {
  const userId = new URL(req.url).searchParams.get("userId");
  if (!userId) return new Response("Missing userId", { status: 400 });
  const raw = await env.ENTITLEMENTS.get(userId);
  return new Response(raw ?? JSON.stringify({ isPro: false }), {
    headers: { "content-type": "application/json" },
  });
}

// --- AI proxy: keeps the cloud-LLM key off the device ---
async function handleAIProxy(req: Request, env: Env): Promise<Response> {
  // TODO: authenticate the app's request (signed token / app check).
  const body = await req.json<{ prompt: string }>();
  // TODO: gate on entitlement if AI is a premium feature (on-device = free tier).
  const resp = await fetch("https://api.example-llm.com/v1/messages", {
    method: "POST",
    headers: { "authorization": `Bearer ${env.LLM_API_KEY}`, "content-type": "application/json" },
    body: JSON.stringify({ prompt: body.prompt }),
  });
  return new Response(resp.body, { status: resp.status, headers: resp.headers });
}
```

## Fill-in checklist

- [ ] `wrangler secret put REVENUECAT_AUTH` (and `LLM_API_KEY`, APNs key) — never in `wrangler.toml`.
- [ ] Set the webhook URL in RevenueCat (or ASC for raw ASSN V2) for BOTH production and sandbox.
- [ ] Client reads `/entitlement` on launch as a server cross-check; the StoreKit store stays the live source for UI.
- [ ] If AI is premium, enforce the entitlement in `/ai`, not just in the app UI.
- [ ] Remove the cron trigger + `scheduled` handler if you have no scheduled work (don't ship dead jobs).
- [ ] Add a Queue in front of slow webhook downstream work so you can always 200 fast.
