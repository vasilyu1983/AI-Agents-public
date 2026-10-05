# Discovery, Economy & Policy

The platform forces that shape design decisions for a new world. Principles are durable; **every rate, fee, percentage, age, and threshold is volatile** — this reference gives the durable judgment plus a lookup step instead of the number.

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

The home page **Recommended For You** sort is the dominant algorithmic surface. Roblox reworks it periodically, and older tutorials and AI training data describe superseded versions. Before tuning anything, look up the current RFY announcement on the DevForum and the signal importance shown in **Creator Analytics → Acquisition → Home Recommendations**; design against those, not a remembered list, because Roblox states the weightings shift.

**Durable shape of recent versions (confirm against the current announcement):**

- Retention is measured over several windows scored separately (an early window around the first day and later windows over the following weeks), not as one blended average.
- Separate signals tell apart "players bounce immediately", "players finish a session but never return", and "short-but-frequent sessions". Optimizing one blended playthrough number optimizes the wrong failure mode.
- Signals that recur across versions: playtime and play days per user, qualified play sessions, intentional co-play, spend days and spend per user.

**The load-bearing design fact:** RFY optimizes for durable per-user retention, not lifetime volume — a small new experience with strong early comprehension can outrank a large declining one. When windows are scored separately, a game that hooks players in session one but leaks them within two weeks shows up as a weak later window instead of being averaged away — so mid-game retention (the weeks after first playable, not just the first session) is a distinct design target.

Other sorts: Featured (staff-curated, rotates), Popular, Charts (including a paid-access sort), and Search (metadata changes take days to repopulate). Look up current slot counts and cadences before planning a launch around them.

## Cold Start: First Players

New experiences take multiple days to surface organically. Durable paths to first players:

1. **Search** — keyword-optimized title/description.
2. **Paid promotion** — Sponsored Experiences and Search Ads via Ads Manager; check the Ads Manager docs for which experience types, including paid-access ones, can be promoted.
3. **Social graph** — friends-playing notifications and intentional co-play feed back into RFY.
4. **External marketing** — shared/direct links bringing users who play 10+ min count toward Audience Expansion rewards.

## Monetization Models

Every rate, share, threshold, and program term here is volatile. Look up the current values in the Developer Exchange help docs, the Marketplace fees doc, and the monetization docs on create.roblox.com before modelling revenue or quoting to anyone; never quote from memory — DevEx rates and payout programs have changed more than once in two years.

- **DevEx (cash-out):** converts Earned Robux to cash at a published rate above a minimum cash-out threshold; Roblox has at times added a higher rate for age-checked adult spend. Look up the current rate, threshold, and eligibility.
- **Game passes:** one-time Robux purchase, permanent benefit; the creator keeps the share left after the marketplace fee (look it up).
- **Developer products:** repeatable purchases (currency, boosts), same fee model; grant every one through an idempotent `ProcessReceipt` handler (see the Known Traps in `../SKILL.md` and [performance-and-traps.md](performance-and-traps.md#known-traps-catalog)).
- **In-experience subscriptions:** recurring Robux; the creator share differs between the first month and renewals (look it up).
- **Creator Rewards (engagement payouts):** Roblox pays creators for playtime by qualifying spenders and for bringing in new or returning spenders. The qualifying definitions, pool mechanics, DAU bars, and holds change — read the current Creator Rewards docs before designing around them, and treat any per-event figure as an estimate from a shared pool, not a fixed rate.
- **Player subscription (Premium / Plus):** Roblox has restructured its player subscription, including whether subscribers get a monthly Robux stipend. Look up the current tiers, benefits, and the in-experience subscription prompt API before promising subscribers anything.
- **Paid access:** Robux or local-currency tiers with a revenue share that rises with price — but a paywall reduces organic reach.
- **Rewarded Video Ads:** opt-in video for an in-experience reward; eligibility has visitor, age, and ID-verification requirements (look them up), under-13 users are excluded, and ad revenue doesn't feed RFY.

## Recommended Mix for a New World

Durable sequencing (independent of the volatile rates):

1. Start with **game passes** (lowest friction).
2. Treat **Creator Rewards** as free upside — design to retain Active Spenders and pull new users via shareable links (look up the current new-user reward requirements).
3. Add **in-experience subscriptions** when you have a recurring-value loop (battle pass, cosmetic stream).
4. Integrate the player-subscription prompt API — low effort; look up current subscriber benefits and creator incentive terms before promising a specific bonus.
5. Add **Rewarded Video Ads** once eligible, especially for free-to-play.
6. Use **paid access** only when brand/polish justifies the discovery penalty.

## Retention and FTUE Design

The RFY signals *are* the design brief: play-through and first-play bounce signals reward a strong, non-confusing first impression; play days across every window (not just the first day) reward genuine return; co-play rewards social hooks; spend-days reward a fair economy. Because recent versions score early and later windows separately, a launch that nails FTUE but has no mid-game reason to return shows a visibly weak later window instead of being masked by a strong average.

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

- **Maturity questionnaire is mandatory.** The penalty for an unrated experience has tightened over time, from hidden in charts and search to unplayable for users; look up the current rule in the maturity-questionnaire docs. Creators can still open and playtest an unrated experience in Studio/Creator Hub. Complete the questionnaire before any public launch.
- **Maturity labels** (look up the current label set and age thresholds): a lowest label open to under-13s, intermediate labels with content descriptors, and a **Restricted** adults-only label that needs age verification and an adult creator, and that under-age users cannot find in search or recommendations. The Restricted age has been raised before, so never quote it from memory.
- **"Sensitive Issues" descriptor** — experiences mostly about polarized social/political/religious topics default to unavailable under-13 (parent-enableable).
- **Under-13 cannot** see Rewarded Video Ads, access Social Hangout / Free-Form User Creation experiences, access Restricted or Sensitive-Issues content, or chat outside trusted connections without age verification.
- **Chat is filtered platform-wide** (discriminatory speech, bullying, PII, off-platform links). Roblox has moved from announcing age checks to enforcing them: accounts carry an estimated or verified age band, and chat, DMs, and increasingly other social features are gated by band rather than by a single 13+ line. Look up the current bands, which features each gates, and rollout coverage in Roblox's safety announcements. Design onboarding assuming a meaningful share of players will hit an age-check wall before your chat or social features are reachable, and don't assume every young player has been screened.
- **You cannot deliver sexual content at any maturity level.** Subscriber benefits must be supplemental, not required for the core loop.
- **Paid random items need a per-player gate.** Before shipping anything bought with Robux or real money whose contents are random (loot boxes, gacha, random packs), call `PolicyService:GetPolicyInfoForPlayerAsync(player)` on the server for each player and block the purchase where paid random items are restricted — enforce it where the purchase is granted, not only by hiding UI — and disclose odds as current Roblox policy requires. The policy field names, affected regions, and odds-disclosure rule are volatile: look them up in the PolicyService and monetization-policy docs before shipping.

## UGC and Asset Economy

- **Using avatar items:** players bring their own avatar everywhere — no creator action needed; avatar/fashion culture drives social session engagement.
- **Creating/selling items:** requires UGC creator eligibility (age and ID verification) to sell in the Marketplace at all. Roblox has added extra requirements for some item classes — for example a subscription-tier requirement for publishing 2D clothing, with delisting of non-compliant existing items after a deadline. Look up the current eligibility rules and deadlines in the Marketplace policy docs and DevForum before building or advising on a UGC pipeline.
- **Fees and splits:** upload fees, Marketplace commission, the in-experience split between creator and game owner, and escrow holds all differ by item class and have changed repeatedly (2D uploads, for example, went from free to paid). Look up the live Marketplace fees doc before modelling a UGC business or quoting to anyone.

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
- **Your audience and content are adult-first by design** — Roblox's under-13 population and recent child-safety policy direction (facial age estimation, chat gating, Restricted-label tightening) mean the platform is investing hard in making itself safer for minors, which structurally narrows what an adult-audience product can do and how discoverable it will be, even if technically compliant.
- **You need full IP/platform independence** — everything you build inherits Roblox's ToS, moderation reach, and economic terms; a founder who needs to own the full stack (payments, distribution, moderation policy) is building the wrong thing on Roblox.

If none of these apply, Roblox's built-in distribution (the Home feed, avatar/social graph, and zero-install play) usually outweighs the platform-lock-in cost for social, casual, and UGC-driven games.

Sources: see [../data/sources.json](../data/sources.json) — RFY algorithm threads, Creator Rewards docs, DevEx and subscription announcements, maturity-questionnaire and Restricted-age threads, age-estimation/chat-safety announcements, rewarded-ads and paid-access threads, FTUE thread, marketplace-fees doc, 2D-clothing-Premium-requirement thread.
