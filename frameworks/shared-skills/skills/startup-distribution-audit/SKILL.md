---
name: startup-distribution-audit
description: "Use when auditing an existing product's distribution capabilities. Evaluates ICP, messaging, activation, retention, content, PLG loops, community, and analytics; produces an evidence-backed 30-day growth plan. Default: bootstrapped/no ads. Updated for 2026 AI-era distribution dynamics."
---

# Startup Distribution Audit (Startup Distribution God)

Use this skill when the product exists and the bottleneck is distribution, not engineering.

2026 context: AI has collapsed the cost to build, so every market is more crowded. Distribution advantage — not product — is the primary moat. Owned audiences, founder-led content, and speed-to-escape-velocity matter more than ever because copycats appear in weeks, not months.

Core promise:

- Audit current growth skills and traction
- Diagnose the current growth stage (0–3)
- Identify the biggest missing distribution capability
- Select 2–3 proven historical playbooks (with real company precedents)
- Produce concrete, executable actions (30-day plan), plus anti-patterns

## When to Use

- “We built it, but we can’t get traction”
- “Audit our growth/distribution capabilities”
- “Give us a 30-day growth plan (no paid ads)”
- “We have some users but don’t know what to do next”

## When NOT to Use

- ICP + GTM motion selection (PLG vs sales-led) -> `startup-go-to-market`
- Positioning/messaging deep dive artifacts -> `marketing-content-strategy`
- Channel-specific execution details (SEO, social, email, CRO) -> use the relevant marketing skill
- Sales pipeline + closing mechanics -> `startup-sales-execution`
- Onboarding/retention systems -> `startup-customer-success`

## Minimum Inputs (Ask These First)

- Product: what it does, who it’s for, pricing/free tier
- Current traction: traffic, signups, activated users, retained users, revenue (or best estimates)
- ICP guess: who is the “obvious” best-fit user today (and who is not)
- Current channels tried: what has been tried, what worked, what didn’t
- Constraints: time/week, budget, channels to avoid (default: no paid ads), and implementation boundaries (for example: no implementation yet)
- Existing stack and tool boundaries: current systems in use (analytics, CRM, scheduling, comms), plus explicit no-new-systems constraints

If numbers are missing, proceed with explicit assumptions and define what to measure in Week 1.

## Mandatory Output Structure (Always Use This Order)

1. Growth Stage Diagnosis
2. Skill Audit (table or bullets)
3. Key Gaps Blocking Growth
4. Proven Startup Playbooks to Apply
5. 30-Day Execution Plan
6. Anti-Patterns to Avoid

Formatting requirements:

- Bullets, checklists, short explanations
- No fluff, no theory-only output
- Every major recommendation cites at least one real company precedent (even if adapted)

## Existing-Stack Constraint Rule (Required)

- Treat the current stack as the default execution surface.
- If the user says no new systems, do not introduce new vendors/platforms in the primary plan.
- Describe tactics as patterns first (for example: invite-link loop), not vendor names.
- If a new system could help materially, label it as optional and keep a stack-native primary path.

## Growth Stage Diagnosis (Required)

Pick exactly one:

- Stage 0 — Invisible: no consistent users, no reliable acquisition surface
- Stage 1 — Used but Not Needed: some users try it, few return (activation/retention failure)
- Stage 2 — Retained but Not Growing: users stay, but no acquisition engine
- Stage 3 — Growing but Fragile: one channel works, not yet defensible/diversified

Use evidence, not vibes. Ask for (or infer) these:

- Activation definition (what is "first value")
- Retention proxy (D7/D30, WAU/MAU, or repeat usage)
- Acquisition surface (repeatable source of new users: community, SEO pages, outbound, integrations)
- ICP clarity (who converts and retains best)
- Competitive window (how fast can a competitor replicate the product with AI tooling?)

## Skill Audit Framework (Required)

Rate each domain as Strong / Weak / Missing and explain impact on traction.

- ICP clarity & problem framing
- Messaging & positioning
- Activation & onboarding
- Retention & habit formation
- Content systems (SEO, social, narrative)
- Product-led growth mechanics (include hybrid PLG + sales-assist if relevant)
- Growth loops & referrals
- Owned distribution (newsletter, community, founder audience, Discord — 2026: this is a structural moat, not optional)
- Community or ecosystem leverage
- Analytics & feedback loops (2026 PLG metrics: activation rate, time-to-value, expansion revenue from self-serve, support request volume as friction proxy)

Guidance:

- If Stage 0: ICP/messaging + “first 100 users” motions matter most; fancy loops are premature.
- If Stage 1: treat distribution as a rounding error; fix activation and retention first.
- If Stage 2: focus on 1 repeatable acquisition surface; don’t expand channels until one works.
- If Stage 3: scale the winner and build a second surface; add compounding loops.

## Playbook Selection Library (Pick 2–3, Stage-Aware)

Select only playbooks that match the stage and constraints. For each: why it worked then, why it fits now, how to adapt for 2026 conditions.

- Content-as-distribution: HubSpot (inbound), Ahrefs (product-led content), Zapier (SEO pages)
- Founder-led distribution: Basecamp (writing + direct audience), ConvertKit (creator-first + founder-led). 2026: every startup needs a "founding content creator" — AI lowers build barriers, so trust/voice is the differentiator
- PLG virality: Dropbox (referrals), invite/link viral loop pattern (Calendly is one example), Slack (team invites). 2026: hybrid PLG + sales-assist is now standard for high-value accounts
- AI-native distribution: Character.AI (100M users via organic social + user-generated characters), Midjourney (Discord-native public generation as virality engine). 2026: platform-native virality where every user action is visible
- Community-led growth: Notion (templates + community), Figma (community + sharing), Webflow (showcase ecosystem). 2026: power users drive 3-7x downstream acquisitions via workplace advocacy
- Programmatic SEO: Zapier (integration pages), Wise (calculator/utility pages), Kinsta (comparison/utilities)
- Integration/ecosystem-led: Shopify App Store, Slack apps, Salesforce AppExchange
- Owned audience + negative CAC: Build newsletter/community/Discord before or alongside product; reduces CAC to near-zero and creates defensible distribution independent of paid channels

## 30-Day Execution Plan (Required Shape)

Produce weekly goals, daily/weekly actions, success signals, and what to stop doing.

2026 urgency: AI tooling compresses competitive windows. Assume a well-funded team can replicate core product functionality in weeks. The 30-day plan must prioritize distribution lock-in (owned audience, network effects, switching costs) alongside acquisition.

Default sequencing (change only if evidence demands it):

- Week 1: Diagnose + instrument + clarify ICP + fix biggest activation leak
- Week 2: Run “unscalable” distribution (founder-led outreach / communities) + tighten onboarding
- Week 3: Commit to 1 acquisition surface (content, ecosystem, outbound, community) + ship one compounding hook
- Week 4: Double down on what worked + cut what didn’t + add repeatable cadence

Use templates when the user wants copy-paste artifacts:

- `assets/distribution-intake.md`
- `assets/skill-audit-scorecard.md`
- `assets/30-day-execution-plan.md`

## Competitive Window Assessment (Use at Stage 2+)

When the user has traction, assess defensibility:

- Time to replicate core product with AI tooling (days/weeks/months)
- Owned audience size (newsletter, community, Discord members)
- Network effects strength (none / weak / strong — does each user make it better for others?)
- Switching costs for retained users (data lock-in, integrations, workflow habits)
- Distribution assets competitors cannot copy (founder audience, ecosystem position, proprietary data)

If competitive window is short (<4 weeks to replicate), the 30-day plan must front-load distribution lock-in over feature work.

## Exemplar (Stage 1 SaaS — Condensed)

Product: AI meeting summarizer, free tier + $12/mo pro. 800 signups, 90 activated (11%), 22 retained D30 (2.75%).

Growth Stage: Stage 1 — Used but Not Needed.

Skill Audit (top gaps):
- Activation: Weak — 11% activation, no guided first-run; users import one meeting, see a generic summary, leave
- Retention: Missing — no triggers to return (no email digest, no calendar integration, no team sharing)
- ICP clarity: Weak — targeting "anyone with meetings" instead of a specific painful persona

Playbooks selected:
1. Invite-link activation fix (reduce time-to-value to <60 seconds with one-click setup)
2. Slack/Notion integration-led retention (summaries appear where users already work)

Week 1 focus: Instrument activation funnel, fix "first value" moment (auto-connect calendar, show first real summary in <60s), define retained = "3+ summaries in 14 days."

Anti-pattern flagged: Founder wanted to add AI action items feature. Blocked — retention problem, not feature problem.

## Anti-Patterns (Mandatory Warnings)

Explicitly call out:

- Scaling tactics before activation/retention (ads, automation, referral loops)
- Multi-channel spray without a winner (no depth, no learning)
- "Build more features" as a substitute for distribution
- Copying big-company playbooks (brand + budget) at zero-traction stage
- Vanity metrics obsession (followers/traffic) without activation/retention improvement
- Platform dependency without owned fallback (2026: assume platform access gets harder, not easier — build owned distribution in parallel)
- Treating AI tooling as a moat (if you can build it in a weekend, so can competitors — distribution is the moat)
- Pure self-serve PLG for enterprise-value deals (2026: hybrid PLG + human touch is the standard, not an exception)
- Recommending tool swaps despite explicit no-new-systems constraints from the user

## Resources

| Resource | Purpose |
|----------|---------|
| [distribution-channel-scoring.md](references/distribution-channel-scoring.md) | Channel evaluation, scoring dimensions, and prioritization |
| [stage-audit-patterns.md](references/stage-audit-patterns.md) | Stage-specific audit methodology and intervention playbooks |
| [competitive-window-analysis.md](references/competitive-window-analysis.md) | Competitive window assessment and defensibility scoring |
| [channel-audit-templates.md](references/channel-audit-templates.md) | Per-domain audit worksheets, scoring rubrics, and summary scorecard |
| [distribution-moat-analysis.md](references/distribution-moat-analysis.md) | Distribution moat types, scoring framework, and competitive defensibility |
| [platform-distribution-playbook.md](references/platform-distribution-playbook.md) | Platform-based distribution: marketplaces, directories, and launch strategies |

## Related Skills

- `startup-growth-playbooks` - Broader stage playbooks + case studies
- `startup-go-to-market` - ICP + motion + channel sequencing
- `marketing-content-strategy` - Positioning + messaging + content systems
- `marketing-seo-complete` - Technical SEO + organic growth execution
- `marketing-social-media` - Channel tactics and content formats
- `marketing-product-analytics` - Event taxonomy + funnels + retention measurement
- `startup-sales-execution` - Founder-led sales, pipeline, discovery, closing
- `startup-customer-success` - Onboarding, retention, churn prevention
