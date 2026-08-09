# Discovery, Economy & Policy (Jul 2026)

The platform forces that shape design decisions for a new world. Principles are durable; **every rate, fee, percentage, age, and threshold here is volatile** and labeled — re-verify before quoting any number.

## Table of Contents

- [The Discovery Algorithm (RFY)](#the-discovery-algorithm-rfy)
- [Cold Start: First Players](#cold-start-first-players)
- [Monetization Models](#monetization-models)
- [Recommended Mix for a New World](#recommended-mix-for-a-new-world)
- [Retention and FTUE Design](#retention-and-ftue-design)
- [Content Maturity and Safety Policy](#content-maturity-and-safety-policy)
- [UGC and Asset Economy](#ugc-and-asset-economy)
- [Economy Design Judgment: Sinks, Sources, and Exploit Economics](#economy-design-judgment-sinks-sources-and-exploit-economics)
- [When Roblox Is the Wrong Platform](#when-roblox-is-the-wrong-platform)

## The Discovery Algorithm (RFY)

The home page **Recommended For You** sort is the dominant algorithmic surface. **It was substantially rewritten and shipped June 15, 2026** (DevForum: "Recommended For You Algorithm Improvements That Better Value Long-Term Retention") — this supersedes the older six-signal, 7-day-window model that circulated through most of 2026 and that you may still see referenced in older tutorials/AI training data. Do not design against the old model as if it were current.

**The 2026 model, per Roblox's own announcement:**

- The measurement window widened from **7 days to 28 days**, split into three phases the algorithm evaluates separately: **Day 1**, **Day 2–7**, and **Day 8–28**.
- **Qualified Play-Through Rate (qPTR) was retired as a single metric** and replaced by two narrower signals — **play-through rate (PTR)** and **first-play bounce rate** — specifically so the algorithm can tell apart "players finish the session but never return" from "players bounce immediately" from "players have short-but-frequent sessions." A single blended qPTR number could not distinguish these failure modes; if you were optimizing for one "playthrough" number, you were probably optimizing for the wrong failure mode.
- Retained signals feeding all three windows: **playtime per user, play days per user, qualified play sessions, intentional co-play days, spend days per user, Robux spent per user.**
- Roblox now publishes each signal's relative importance directly in **Creator Analytics → Acquisition → Home Recommendations** — use the dashboard, not a cached list, since weightings are stated to shift.

**The load-bearing design fact, still true under the new model:** RFY optimizes for durable per-user retention, not lifetime volume — a small new experience with strong Day-1 and Day-2–7 comprehension can still outrank a large declining one. What changed is the granularity: a game that hooks players in session one but leaks them by day 10 now shows up distinctly (strong Day-1, weak Day-8–28) instead of being averaged away — so mid-game retention (the first week after first playable, not just the first session) is now a distinct, visible design target, not an assumption.

`as of Jul 2026 — verify`: confirm no further signal changes have shipped since this rewrite before treating this table as final; Roblox has iterated on RFY roughly twice a year.

Other sorts: Featured (staff-curated, rotates), Popular (by country / worldwide / among premium), Charts (incl. a paid-access sort), and Search (metadata changes can take up to ~14 days to repopulate). `as of Jul 2026 — verify slot counts and cadences`.

## Cold Start: First Players

New experiences take multiple days to surface organically. Durable paths to first players:

1. **Search** — keyword-optimized title/description.
2. **Paid promotion** — Sponsored Experiences and Search Ads via Ads Manager; paid-access experiences are now promotable.
3. **Social graph** — friends-playing notifications and intentional co-play feed back into RFY.
4. **External marketing** — shared/direct links bringing users who play 10+ min count toward Audience Expansion rewards.

## Monetization Models

All rates `as of Jul 2026 — VERIFY before quoting`:

- **DevEx (cash-out):** standard **$0.0038/Earned Robux** — confirmed current, effective since Sep 5 2025. A US 18+ rate of **$0.0054** (≈42% premium) applies to age-checked 18+ US-player spend on R15 experiences (**effective Jun 8 2026**) — marketplace items excluded. Minimum cash-out threshold ~30,000 Earned Robux. (Verified Jul 2026 against Roblox Developer Exchange help docs; re-check before quoting to a client since it has moved twice in under two years.)
- **Game passes:** one-time Robux purchase, permanent benefit; creator keeps ~70% after marketplace fee.
- **Developer products:** repeatable purchases (currency, boosts); same ~70%.
- **In-experience subscriptions:** recurring Robux; ~70% creator first month, ~100% on renewals (minus processing).
- **Creator Rewards** (replaced Premium Payouts, mid-2025; all creators auto-enrolled since Jul 24 2025): a **Daily Engagement Reward** — creators earn Robux when an **Active Spender** (spent ≥$9.99 on Roblox in the trailing 60 days, and not a New/Reactivated user in that window) plays 10+ minutes in an experience that's among their first 3 launches that day. Roblox states a **5 Robux baseline** for the qualifying 10-minute threshold, but the actual payout scales with additional qualifying time and the experience's share of a platform-wide engagement pool — **treat "5 Robux" as a floor, not a fixed per-event rate.** Plus an **Audience Expansion Reward** (~35% on the first ~$100 of a new/reactivated user's spend; requires ~100+ avg DAU over the 60-day window). 60-day hold before crediting.
- **Roblox Plus** (replaced Premium at general availability **Apr 30 2026**, $4.99/mo, benefits-only — **no monthly Robux stipend**, unlike legacy Premium): confirmed subscriber benefits are a 10% marketplace/avatar-purchase discount (20% after 3 consecutive months), free unlimited private-server access even where the experience normally charges per-player Robux for one, and continued marketplace trading/selling eligibility. Integrate `PromptRobloxSubscriptionPurchase` to prompt subscription purchase in-experience; do not assume Plus subscribers receive a monthly Robux grant the way Premium subscribers used to — that changed.
- **Paid access:** Robux or local-currency tiers with higher revenue share at higher prices (~50/60/70% at ~$9.99/$29.99/$49.99) — but a paywall reduces organic reach.
- **Rewarded Video Ads:** opt-in video for an in-experience reward; eligibility ~2,000+ monthly visitors, 13+, ID-verified; under-13 users are auto-excluded; ad revenue doesn't feed RFY.

## Recommended Mix for a New World

Durable sequencing (independent of the volatile rates):

1. Start with **game passes** (lowest friction; feeds the 18+ DevEx uplift if your audience skews adult).
2. Treat **Creator Rewards** as free upside — design to retain Active Spenders and pull new users via shareable links to clear the ~100-DAU Audience Expansion bar.
3. Add **in-experience subscriptions** when you have a recurring-value loop (battle pass, cosmetic stream).
4. Integrate the **Roblox Plus** prompt API — low effort; verify current creator incentive terms before promising a specific bonus number (the subscriber-side benefit is a marketplace discount and free private servers, not a Robux stipend).
5. Add **Rewarded Video Ads** once past the visitor threshold, especially for free-to-play.
6. Use **paid access** only when brand/polish justifies the discovery penalty.

## Retention and FTUE Design

The RFY signals *are* the design brief: PTR and first-play bounce rate reward a strong, non-confusing first impression; play-days across all three windows (not just Day 1) reward genuine return; co-play rewards social hooks; spend-days reward a fair economy. Because the 2026 model separates Day 1 from Day 2–7 from Day 8–28, a launch that nails FTUE but has no mid-game reason to return will now show visibly weak Day-8–28 signal instead of being masked by a strong average.

Official FTUE guidance: introduce the core loop, progression, and short/mid/long-term goals **within the first session**; the goal is that the player understands and enjoys enough to return tomorrow. Roblox recommends visual guidance, just-in-time contextual instruction, and adaptive hints for struggling players.

Durable retention mechanics (community-evidenced, not official benchmarks):
- **Core-loop clarity in FTUE** — most retention failure traces to players not understanding the game in session one.
- **Progression systems** — levels, ranks, unlock trees give a return reason.
- **Social hooks** — friend invite/co-play loops double as a discovery signal.
- **Private servers** — count as intentional co-play; benefit social/roleplay games algorithmically.
- **Daily rewards** — weak on their own; only help atop a compelling core loop.

> No official source publishes specific D1/D7 percentage benchmarks; treat any quoted "good D1 = X%" as UNVERIFIED.

## Content Maturity and Safety Policy

These constrain what you can build and who can find you.

- **Maturity questionnaire is mandatory.** Since **Sep 30 2025** an unrated experience is **fully unplayable platform-wide** for users — not merely hidden from charts/search (the earlier, weaker penalty). Creators can still open and playtest an unrated experience in Studio/Creator Hub. Complete the questionnaire before any public launch.
- **Four labels** (`as of Jul 2026 — verify ages`): **Minimal** (incl. under-13), **Mild** (all ages, descriptors shown), **Moderate** (older audiences), **Restricted** (**18+**, raised from 17+ in late 2025; age verification required; creator must be 18+; under-18s can't see it in search/recommendations).
- **"Sensitive Issues" descriptor** — experiences mostly about polarized social/political/religious topics default to unavailable under-13 (parent-enableable).
- **Under-13 cannot** see Rewarded Video Ads, access Social Hangout / Free-Form User Creation experiences, access Restricted or Sensitive-Issues content, or chat outside trusted connections without age verification.
- **Chat is filtered platform-wide** (discriminatory speech, bullying, PII, off-platform links). **Corrected from "announced":** platform-wide facial age estimation is **live**, not merely planned — Roblox began mandatory age checks for chat access in Nov 2025 and completed a global rollout of facial-age-estimation-based checks in ~Jun 2026. Every account gets an estimated or Persona-verified age band (**Under 9, 9–12, 13–15, 16–17, 18–20, 21+**); chat and DM behavior, and increasingly other social features, are gated by band, not just by the old "13+" binary. Chat is **default-off for under-9** accounts absent parental consent post-age-check. By Roblox's own Q1 2026 disclosure only ~51–65% of DAU had completed a check by end of March 2026 — so design your onboarding assuming a meaningful share of players will hit an age-check wall before your chat/social features are reachable, and don't assume every under-13 has been screened.
- **You cannot deliver sexual content at any maturity level.** Premium/Plus benefits must be supplemental, not required for the core loop.

## UGC and Asset Economy

- **Using avatar items:** players bring their own avatar everywhere — no creator action needed; avatar/fashion culture drives social session engagement.
- **Creating/selling items:** requires standard UGC creator eligibility (13+, ID verification) to sell in the Marketplace at all. **New as of Jul 2026:** publishing **2D avatar clothing** (shirts/pants/T-shirts) additionally requires an active **Roblox Premium 1000 or 2200** subscription tier (not the base Roblox Plus tier) as of a Mar 19 2026 policy change — 3D/accessory items are not subject to this rule. Existing 2D items from non-subscribed creators face delisting; Roblox gave holders until **Jul 31 2026** to comply — if you are building or advising on a UGC-clothing pipeline right now, this deadline is imminent, check it first. (Source: DevForum "Building a Safer Marketplace: Updates to 2D Avatar Items," Mar 2026 — verify current deadline/tier names before acting.)
- **Fees (verified against the official Marketplace Fees doc, Jul 2026):** 3D avatar item (accessory/body/animation) upload fee **300 Robux**; 2D avatar item (shirt/pants/T-shirt) upload fee **10 Robux** (this was previously free — confirm before assuming zero-cost 2D uploads). Marketplace commission on 3D items starts at **30% creator share**, scaling up to ~70% at higher price tiers; in-experience 3D sales split roughly 30% creator / 40% game owner; classic clothing is 70% creator on Marketplace, 60% creator / 10% game owner in-experience. A ~30-day escrow hold applies before commission pays out. Treat exact splits as volatile and re-check the live doc before quoting to a client — Roblox has changed this schedule more than once in the last 12 months.

## Economy Design Judgment: Sinks, Sources, and Exploit Economics

A Roblox economy is a real economy — treat it with the same rigor you'd want from a game economist, not just "let players earn and spend Robux/soft currency."

- **Every source needs a matching sink, or you get hyperinflation.** If soft currency accumulates faster than sinks consume it (daily rewards with no decay, idle-game numbers that only go up), veteran players sit on huge unspent piles, new-item prices have to keep climbing to matter to them, and new players feel priced out immediately. Audit your economy by simulating a 30/60/90-day player: does their currency balance trend toward zero-ish equilibrium, or toward infinity? Design sinks (consumables, cosmetic rotation, repair/upkeep costs, prestige resets) *before* you ship a new source, not after inflation is already visible in the data.
- **Exploit economics: think like the cheater, not just the coder.** Before shipping a tradeable/purchasable item, ask "if someone duplicates or free-mints this, what does it do to the market?" A duped cosmetic tanks resale value and trust; a duped consumable that grants power breaks competitive balance; a duped currency devalues every other player's holdings. This is why the dupe-race pattern in `luau-and-architecture.md` (serialize economy remotes) is an economy-design issue, not just a networking bug — the *cost* of a race-condition exploit scales with how central that currency/item is to the whole economy, so harden the highest-leverage items first, not every item equally.
- **Robux-denominated sinks compete with DevEx.** Every Robux a player spends inside your experience is a Robux you (partially) get to cash out via DevEx — but it's also a Robux Roblox's own cut applies to first. Model your monetization mix (game passes vs. dev products vs. subscriptions) against the actual creator-share percentages above, not against gross Robux volume, before promising a revenue number to a stakeholder.
- **Trading and secondary markets amplify both good and bad design.** A healthy trade economy (Limited items, cosmetics) deepens engagement and co-play; an unaudited one becomes a money-laundering or real-money-trading (RMT) vector that violates platform ToS and risks the whole experience's standing. If you support trading, rate-limit trade frequency per account pair and log anomalous patterns (same two accounts trading repeatedly, one-directional value flow) — this is a policy-compliance issue as much as a design one.

## When Roblox Is the Wrong Platform

Recognizing this early saves months. Roblox is a poor fit when:

- **You need content Roblox's policy can't host** — sexual content at any maturity level, real-money gambling mechanics, or anything requiring content the Restricted/Sensitive-Issues system is explicitly built to exclude. No amount of age-gating fixes this; it's a platform ToS boundary, not a design problem to route around.
- **Your monetization model needs full payment/pricing control** — Roblox mandates its Robux economy and current commission/DevEx structure for in-experience purchases; if the product needs direct fiat pricing, external payment processors, or a materially different revenue split, build outside Roblox (or as a companion app) instead of fighting the platform's economics.
- **You need deterministic, high-fidelity simulation at a scale Luau/DataModel replication can't reasonably carry** — large-scale physics-heavy sims, precise competitive esports netcode with frame-perfect rollback, or workloads that would need to bypass `RemoteEvent`/`FilteringEnabled` semantics entirely. Roblox's networking and Luau's runtime are tuned for the genres it dominates (social, obby, tycoon, roleplay, casual PvP) — not for genres that need engine-level control over netcode.
- **You need distribution outside Roblox's client** — a standalone Steam/console (non-Xbox) release, an offline mode, or a product that must run without the Roblox client/account system. Roblox experiences are inherently platform-locked.
- **Your audience and content are adult-first by design** — Roblox's under-13 population and 2025–26 child-safety policy direction (facial age estimation, chat gating, Restricted-label tightening) mean the platform is investing hard in making itself safer for minors, which structurally narrows what an adult-audience product can do and how discoverable it will be, even if technically compliant.
- **You need full IP/platform independence** — everything you build inherits Roblox's ToS, moderation reach, and economic terms; a founder who needs to own the full stack (payments, distribution, moderation policy) is building the wrong thing on Roblox.

If none of these apply, Roblox's built-in distribution (the Home feed, avatar/social graph, and zero-install play) usually outweighs the platform-lock-in cost for social, casual, and UGC-driven games.

Sources: see [../data/sources.json](../data/sources.json) — RFY algorithm threads (2026 rewrite), Creator Rewards docs, DevEx/Plus announcements, maturity-questionnaire and Restricted-age threads, age-estimation/chat-safety announcements, rewarded-ads and paid-access threads, FTUE thread, marketplace-fees doc, 2D-clothing-Premium-requirement thread.
