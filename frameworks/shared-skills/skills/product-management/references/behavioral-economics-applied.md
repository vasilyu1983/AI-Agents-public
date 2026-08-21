---
description: Behavioral economics applied to product management — onboarding defaults, activation nudges, retention framing, feature-discovery choice architecture, and social-proof placement. Anchored to primitives #2, #4, #5, #7, #9, #10 from foundations-behavioral-economics. Every recipe carries a mandatory ethical gate.
last_verified: 2026-05-02
status: stable
---

# Behavioral Economics Applied: Product Management

> **Gate before invoking:** Check [`foundations-behavioral-economics` § When to Apply](../../foundations-behavioral-economics/SKILL.md#when-to-apply) first. The recipes below assume the foundation is the right tool for the situation; the foundation's skip-conditions route you to a different foundation if not.


## Table of Contents

- [Framing Note](#framing-note)
- [Pattern Catalog](#pattern-catalog)
  - [P1 — Onboarding Defaults with Reversibility Test](#p1--onboarding-defaults-with-reversibility-test)
  - [P2 — Retention via Loss-Aversion Framing](#p2--retention-via-loss-aversion-framing)
  - [P3 — Activation Nudges via Present-Bias Mitigation](#p3--activation-nudges-via-present-bias-mitigation)
  - [P4 — Choice Architecture in Feature Discovery](#p4--choice-architecture-in-feature-discovery)
  - [P5 — Social-Proof Placement with Provenance Check](#p5--social-proof-placement-with-provenance-check)
- [Anti-Pattern Catalog](#anti-pattern-catalog)
  - [A1 — Dark-Pattern Onboarding: Forced Continuity and Sneak-In Subscriptions](#a1--dark-pattern-onboarding-forced-continuity-and-sneak-in-subscriptions)
  - [A2 — Manufactured Urgency on Free-Trial Countdowns](#a2--manufactured-urgency-on-free-trial-countdowns)
  - [A3 — Defaults That Exploit Irreversibility](#a3--defaults-that-exploit-irreversibility)
  - [A4 — Loss-Frame Retention Applied to a Neutral Event](#a4--loss-frame-retention-applied-to-a-neutral-event)
  - [A5 — Over-Personalization That Creates Filter Bubbles](#a5--over-personalization-that-creates-filter-bubbles)
- [Recipes](#recipes)
  - [R1 — Activation Default Sequence](#r1--activation-default-sequence)
  - [R2 — Retention Nudge Program](#r2--retention-nudge-program)
  - [R3 — Feature-Discovery Flow](#r3--feature-discovery-flow)
- [Composition](#composition)
- [Sources](#sources)

---

## Framing Note

Behavioral economics is a tool for understanding how users actually decide — not for manufacturing compliance. The primitives from `foundations-behavioral-economics` are domain-agnostic; this file is the PM-specific application layer. Every pattern below is an intervention in a user's decision-making process. That carries an obligation: each technique must steer users toward choices they would endorse on reflection, must remain easy to override, and must not exploit cognitive limitations against the user's interests (Thaler & Sunstein's harm test).

For the underlying mechanics, effect-size evidence, and misuse boundaries of each primitive, open the linked playbooks in `foundations-behavioral-economics/assets/templates/behavioral-economics/`.

---

## Pattern Catalog

### P1 — Onboarding Defaults with Reversibility Test

**The PM problem.** Onboarding flows have many binary decisions: which features to enable, which notifications to allow, which integrations to connect. Requiring the user to actively configure everything produces high drop-off. But pre-selecting everything for the user's convenience can silently enable permissions, spend budgets, or share data the user did not intend to authorize.

**The behavioral mechanism.**

Defaults (#4) work because of status quo bias and the implicit endorsement effect: a pre-selected option is interpreted as the recommended option, and inertia keeps most users from changing it. Inertia is not laziness — it is a rational response to limited attention. The design question is whether you are using that inertia for the user or against them.

**The PM application.**

Step 1: For each default in the onboarding flow, answer: "If this user reviews their settings in 30 days, will they be glad this was pre-selected?"  
Step 2: Apply the **reversibility test** — can the user easily undo or change this default after onboarding? One-click toggle = reversible. Settings buried two levels deep = effectively irreversible.  
Step 3: For defaults that are reversible and pass the endorsement check, apply freely.  
Step 4: For defaults with meaningful downstream consequences (billing triggers, data sharing, email permissions), flip the logic: require explicit opt-in rather than opt-out.

**PM examples.**

- _Onboarding_: Pre-select "weekly digest" email (reversible, high value, low cost) — appropriate default.
- _Onboarding_: Pre-select "contact me about upgrades" — opt-in required; the benefit is the company's, not the user's.
- _Activation_: Pre-populate the user's first project with sample data to reduce blank-slate friction — defaults serving the user's activation path.
- _Monetization_: Pre-select annual billing on first payment screen — requires scrutiny; user may not have compared monthly and annual deliberately.

**Ethical gate.** Apply the reversibility test explicitly before shipping any default. Document in the product decision brief: default state, reversibility path, and endorsement rationale. If the reversibility path requires more than two steps, the default must be opt-in.

**Primitive links.** Defaults (#4) → Dual-system (#10) for cognitive load reduction → Choice architecture (#9) for option framing.

---

### P2 — Retention via Loss-Aversion Framing

**The PM problem.** A user is approaching the end of a free trial, has not engaged in 14 days, or is on a cancel-intent screen. Positive framing ("come back, great things await") underperforms because users are not in a gain-seeking state — they are in a loss-avoidance state. Loss aversion (#2) explains why: losses feel approximately 2.25× more painful than equivalent gains feel rewarding (Kahneman & Tversky 1979).

**The behavioral mechanism.**

Loss framing reactivates the user's sense of ownership over something they are about to forfeit. The psychological trigger is the endowment effect layered on top of loss aversion: users who have invested time, data, or configuration feel they already own something, and framing cancellation as losing that investment is more motivating than framing renewal as gaining access to features.

**The PM application.**

Step 1: Audit what the user genuinely owns or will lose: saved searches, project history, team collaborations, integrations, accumulated data, personalization. These are real losses.  
Step 2: Quantify where possible. "You've created 14 reports and connected 3 integrations" is more motivating than a generic loss frame.  
Step 3: Place the loss frame at the moment the decision is live — not in advance, not retroactively.  
Step 4: Apply the **neutral-event check** (see A4): confirm the loss frame is applied to something the user actually values, not manufactured from a neutral event.

**PM examples.**

- _Retention_: "Your 14 reports and integration with Salesforce will be deleted if your trial ends tomorrow" — specific, real, user-created value at stake.
- _Retention_: "Don't lose your streak" for a user with a 21-day engagement streak — loss framing on a user-created asset.
- _Monetization_: "Your custom dashboard and 6 saved segments will be downgraded to read-only on the free plan" — accurate description of downgrade consequences.
- _Re-engagement_: "Your team hasn't seen your latest changes. They may move ahead without you" — loss frame tied to social/collaboration value.

**Ethical gate.** Every loss claim must be factually accurate and refer to something the user created or configured. Loss frames on synthetic assets ("you'll lose your personalized recommendations") where no real personalization exists are dark patterns. Fabricated urgency ("your data will be deleted" when it will not be) violates CMA/CPR guidelines and destroys trust on discovery.

**Primitive links.** Loss aversion (#2) → Prospect theory (#1) for framing calibration → Mental accounting (#8) for cost reframing if price is a factor.

---

### P3 — Activation Nudges via Present-Bias Mitigation

**The PM problem.** A new user signs up and intends to complete onboarding, connect integrations, and invite teammates. Most do not. The intention-action gap is the primary activation failure. Hyperbolic discounting (#7) explains why: the effort required to complete onboarding is immediate and concrete, while the value is future and abstract. The user's present-biased System 1 reliably underweights future value.

**The behavioral mechanism.**

Present bias produces a preference reversal: users who would rationally prefer to complete onboarding now (future self) consistently defer it (present self). Mitigation strategies address this by either making the present-moment reward immediate or making the future cost salient. The goal is to bring the reward forward, not to manufacture artificial pressure.

**The PM application.**

Step 1: Map the activation path to find where the present-moment reward occurs. For most products, the "aha moment" (the point where the user first sees real value) is the payoff that motivates continuation.  
Step 2: If the aha moment is gated behind significant setup effort (importing data, inviting colleagues, connecting an API), create a **lightweight value preview** that delivers a System 1 reward before the full setup is complete. Sample data, a pre-filled project template, or a simulated output qualify.  
Step 3: Use a **commitment device**: ask the user to schedule the setup step rather than complete it now. "Set a reminder for Thursday?" converts present-bias deferral into a future commitment with lower resistance.  
Step 4: Sequence the activation steps so each step delivers partial value, not just prepares for eventual value.

**PM examples.**

- _Onboarding_: Show the user a pre-populated analytics dashboard with sample data immediately after sign-up so they see the product's output before inputting their own data.
- _Activation_: "Your report is ready — you just need to connect your data source to see your numbers instead of sample ones" — value preview + clear next step.
- _Activation_: Offer a "quick start" checklist with a 3-minute path to the aha moment alongside the full setup path — short path exploits present-bias, full path is available for motivated users.
- _Monetization_: "Lock in your settings before your trial ends" as a commitment framing for users who have configured but not converted — activates sunk-cost and present-bias in the user's favor.

**Ethical gate.** Commitment devices must be transparent and easy to cancel. Do not design commitment mechanics that lock in payment commitments the user did not clearly authorize. Present-bias mitigation is ethical when it helps users do what they already intend; it becomes manipulation when it accelerates commitments the user would decline on reflection.

**Primitive links.** Hyperbolic discounting (#7) → Dual-system (#10) to reduce System 2 load → Defaults (#4) for pre-selected quick-start paths.

---

### P4 — Choice Architecture in Feature Discovery

**The PM problem.** A product with many features has a discoverability problem: users adopt two or three features and never explore the rest. The failure is not awareness — it is choice architecture. Users confronted with an undifferentiated menu of 30 features apply the path of least resistance: use what they already know. Choice architecture (#9) addresses the structure of the option set to make the right next step obvious without removing options.

**The behavioral mechanism.**

Dual-system cognition (#10) governs feature discovery: System 1 acts on what is visually prominent and contextually obvious; System 2 would rationally evaluate the full feature set but is rarely engaged for routine product navigation. The PM's job is to engineer the System 1 path toward high-value features rather than waiting for users to deliberate.

**The PM application.**

Step 1: Segment features by activation value — which features correlate with long-term retention (from cohort data) versus which are used only by power users?  
Step 2: In the UI, give retention-correlated features visual prominence at the moment in the user's workflow when they are most relevant (contextual surfacing), not as a static list in a "features" menu.  
Step 3: Use **progressive disclosure**: show the one or two next-most-useful features for the user's current context; do not present the full catalogue. This reduces choice overload and exploits the goal-gradient effect (users accelerate when the next step is clear).  
Step 4: For feature discovery emails and in-app tooltips, apply the **one-feature-per-message rule**: each communication introduces exactly one feature with a single action. Multiple features compete for attention and produce decision paralysis.

**PM examples.**

- _Activation_: After a user's first report is published, surface the "Schedule delivery" feature contextually — the user has just created value and is in a receptive state.
- _Feature discovery_: A "What's next?" card that adapts to the user's current activation stage (beginner, intermediate, advanced), surfacing the one feature most likely to increase their value realization.
- _Onboarding_: A setup checklist with three highlighted tasks (not fifteen) — the checklist exploits completion bias while choice architecture limits overload.
- _Monetization_: A pricing page with a highlighted "Most teams choose this" tier — choice architecture signals the modal choice without removing other options.

**Ethical gate.** Choice architecture must guide toward features that serve the user's stated goals, not toward options that maximize revenue at the user's expense. The "recommended" option must be genuinely the best fit for the modal user. Surfacing upgrade prompts as contextual "recommendations" when the free tier is sufficient is a dark pattern (see A3).

**Primitive links.** Choice architecture (#9) → Dual-system (#10) → Defaults (#4) for pre-selection within a constrained set → Social proof (#5) for "most popular" signals.

---

### P5 — Social-Proof Placement with Provenance Check

**The PM problem.** Social proof (#5) reduces uncertainty at decision points by signaling what comparable others have done. It is one of the highest-leverage signals in product — and one of the most misused. Vague, fabricated, or stale social proof erodes trust on discovery; specific, accurate, contextual social proof reduces anxiety and accelerates decisions.

**The behavioral mechanism.**

Social proof operates primarily through informational social influence: the user infers correct behavior from what others like them have done. The inference is System 1 and fast. The trigger requires two conditions: the referenced peer group must be perceived as similar (same role, same use case, same context), and the claim must be credible.

**The PM application.**

Step 1: Run the **provenance check** on every social proof claim before it ships:
- Is the number accurate and current?
- Is the peer group correctly defined (not "users" when you mean "enterprise customers")?
- Is the behavior being described the actual behavior the data shows?
- Will this claim survive public scrutiny (ASA/FTC "front page test")?

Step 2: Place social proof at the point of maximum uncertainty — the moment just before the user must make a decision, not after. In onboarding: at the step where most users drop off. In pricing: on the tier selection screen, not on the confirmation page.  
Step 3: Make the peer group specific. "Most product managers in teams of 10–50 start with the workflow integration" outperforms "millions of users trust us" because specificity activates informational social influence.  
Step 4: For B2B products, use **peer behavior data from the onboarding flow** itself: "Teams like yours (SaaS, 12–50 people) typically connect Salesforce first." This requires instrumentation but is the highest-converting social proof format.

**PM examples.**

- _Onboarding_: "87% of users who connected their CRM in their first week were still active at 90 days" — specific, data-grounded, at the decision point.
- _Activation_: "Your peers at [similar company size] run this report weekly" — role- and context-specific peer reference.
- _Monetization_: "The Pro plan is used by 78% of teams your size" — social proof on the pricing tier, not a generic claim.
- _Retention_: "Teams who stayed after considering cancelling saw 34% faster output within 60 days" — real cohort data, placed at the cancel-intent screen.

**Ethical gate.** Social proof claims must pass the provenance check before every deployment. Fabricated or rounded-up numbers ("thousands of users" when you have 400) are deceptive commercial practices under **DMCC Act 2024 s.226** (misleading actions — the CPRs 2008 were revoked 6 April 2025 by DMCC s.251(1)) and ICO GDPR guidance (for consent-related claims). Stale numbers (data older than 6 months in a high-growth product) must be re-verified before use. Never manufacture comparison peer groups to make small user bases appear larger.

**Primitive links.** Social proof (#5) → Dual-system (#10) for credibility framing → Defaults (#4) when social proof is used to reinforce a pre-selected option.

---

## Anti-Pattern Catalog

### A1 — Dark-Pattern Onboarding: Forced Continuity and Sneak-In Subscriptions

**Description.** A free trial requires credit card entry at sign-up with no explicit disclosure of when billing begins. Cancellation requires calling a phone number or is hidden behind multiple confirmation screens. The "continue free trial" button is visually prominent; the "cancel" action is in small grey text or absent entirely from the account UI.

**Why it fails.** Forced continuity (also called a negative-option subscription) defaults the user into a paid state through inertia rather than informed choice. It exploits the same default-and-inertia mechanism as ethical defaults but in the direction of the company's financial interest rather than the user's stated goals. The user who does not cancel does not necessarily endorse the subscription — they may not have noticed it. Discovery produces immediate cancellations, chargebacks, and social media complaints that exceed any short-term revenue gain.

**Regulatory exposure.** In the UK, forced continuity without clear disclosure violates CMA Consumer Markets Investigation guidance on subscription traps (2022), **DMCC Act 2024 s.228** (aggressive practices, in force 6 April 2025, replacing CPRs 2008 Reg. 7), and in some cases ASA CAP rules on misleading promotions. In the EU, the EU Omnibus Directive (2022) requires explicit confirmation before automatic renewal. In the US, the FTC's Negative Option Rule (2023 update) requires clear and conspicuous disclosure and simple cancellation.

**Concrete damage.** Chargebacks imposed by payment processors (Stripe, Braintree) cost the merchant both the refund and a chargeback fee. Chargeback rates above 1% trigger card network reviews and can result in account termination. Beyond direct costs, forced continuity trains users to distrust the product's billing surface permanently.

**Fix.** Require explicit, informed consent at billing entry. Show a clear "your trial ends on [date] and you'll be charged [amount]" notification 72 hours before billing. Match the cancellation path's friction to the sign-up path's friction — if sign-up is one screen, cancellation must also be accessible in one screen.

---

### A2 — Manufactured Urgency on Free-Trial Countdowns

**Description.** A countdown timer on the trial banner says "2 days left." The timer is accurate. But the actual consequence of trial expiry is a graceful downgrade to a free tier, not data loss or service interruption. The messaging implies urgency and loss that is not real.

**Why it fails.** Urgency signals (#6 in the primitive catalog) are valid when scarcity or time limits are real and material. A countdown to a downgrade that preserves all user data, keeps the account active, and offers full reactivation at any time is not a real loss — it is manufactured anxiety. Users who discover the discrepancy (by testing what actually happens at expiry) update their model of the company as one that uses deceptive pressure, reducing their willingness to pay permanently.

**Behavioral diagnosis.** This conflates scarcity (#6) with loss aversion (#2). The scarcity claim (time running out) is real. The implied loss (data gone, work destroyed) is false. Users cannot easily verify the difference before the deadline — which is exactly why the pattern produces a short-term conversion lift despite being dishonest.

**Concrete damage.** Net Promoter Score impact from perceived deception is documented in Reichheld & Markey (2011): customers who feel misled are active detractors with outsized negative influence. For B2B products, sales teams deal with objections seeded by misleading marketing months into the sales cycle.

**Fix.** Use the countdown only when the consequence is real and material: "In 2 days, your 14 saved reports and integrations will be frozen until you upgrade." If the consequence is a feature restriction only, say so: "In 2 days, you'll move to the free plan — your data stays safe." Accurate urgency converts; manufactured urgency destroys brand.

---

### A3 — Defaults That Exploit Irreversibility

**Description.** Onboarding pre-selects "annual billing" at the payment step without surfacing the monthly option in the same visual hierarchy. The upgrade is pre-confirmed with a billing summary shown only after the user has committed intent to the pre-selected plan. Switching from annual to monthly requires a support ticket and carries a penalty.

**Why it fails.** This is a reversibility violation: the default is set in the company's financial interest (higher LTV from annual pre-payment), and the path to reversing it is deliberately harder than the path that was defaulted. The reversibility test from P1 — "can the user undo this in two steps?" — fails explicitly.

**Behavioral diagnosis.** This combines defaults (#4) with choice architecture (#9) to create a funnel in which users are nudged toward the higher-commitment option through framing and default pre-selection, then face asymmetric friction to change their mind. The user's present-biased System 1 accepts the pre-selection; the switching cost makes the commitment sticky beyond what the user intended.

**Regulatory exposure.** ICO GDPR guidance states that consent obtained through deceptive choice architecture is invalid for consent-based processing. CMA guidance on subscription practices (2022) specifically covers pre-ticked boxes and default selections in payment flows. **DMCC Act 2024 s.228** prohibits aggressive practices — harassment, coercion, or undue influence that significantly impairs the average consumer’s freedom of choice. (This replaced CPRs 2008 Reg. 7, revoked 6 April 2025; note the old citation was to a *regulation*, not a section.)

**Fix.** Present monthly and annual options in equal visual prominence. Show the price and total cost clearly for both. Pre-selecting annual is acceptable only when: (1) it is clearly labeled as pre-selected, (2) the monthly option is one click away, and (3) annual can be cancelled for a pro-rated refund within 14 days (matching statutory cooling-off rights under the Consumer Contracts Regulations 2013 in the UK).

---

### A4 — Loss-Frame Retention Applied to a Neutral Event

**Description.** A re-engagement email tells a user who has been inactive for 10 days: "You're falling behind. Don't lose your progress." The user has no streak, no accumulated data, and has made no product investment. They signed up once and never activated. The "progress" and "loss" are manufactured.

**Why it fails.** Loss framing (#2) is powerful precisely because it maps onto real psychological ownership. When users have no real investment — no data, no configuration, no social connections — loss framing attaches to nothing and reads as manipulative. Worse, it signals that the company does not know the user's actual state (because it doesn't), damaging the sense of personalization.

**Behavioral diagnosis.** The trigger condition for ethical loss framing is that the user has a genuine endowment to protect: created content, configured integrations, team relationships, accumulated data. Without an endowment, loss framing is a dark pattern because the premise is false.

**Concrete damage.** Unsubscribe rates for re-engagement emails that over-rely on manufactured urgency or false loss framing run 3–5× higher than contextually accurate emails (Klaviyo email benchmark data, 2024). In regulated industries (financial services, healthcare), manufactured urgency in communications may attract FCA or ICO attention.

**Fix.** Segment re-engagement triggers by actual user state. Users with real investment: use specific loss framing referencing what they created. Users with no investment: use curiosity or social proof framing instead — "See what teams like yours built this week." Never manufacture loss from nothing.

---

### A5 — Over-Personalization That Creates Filter Bubbles

**Description.** A content or feature recommendation engine surfaces only items similar to the user's past behavior. Over time, the algorithm narrows the user's exposure to a progressively smaller slice of the product's value surface. New features, alternative workflows, and cross-cutting capabilities never appear because the user has not previously engaged with them.

**Why it fails.** Choice architecture (#9) and personalization are aligned when the system surfaces what the user genuinely needs next. They diverge when the system optimizes for engagement on the known surface rather than discovering new value. The result is a product that feels increasingly narrow over time, under-delivers on the full value proposition, and fails to drive the up-funnel behaviors (expanded use cases, team invites, cross-functional adoption) that drive net revenue retention.

**Behavioral diagnosis.** The over-personalized product exploits dual-system bias: System 1 is satisfied by familiar, low-effort content that matches existing mental models. System 2, which would evaluate whether the user is seeing the full range of available value, is not engaged. The user's stickiness metric looks healthy while their expansion and upgrade metrics decline.

**Concrete damage.** In B2B SaaS, filter-bubble personalization is a primary driver of "zombie accounts" — accounts with steady logins but no seat expansion, no cross-team adoption, and high churn risk at contract renewal because perceived value has stagnated.

**Fix.** Apply **friction symmetry** to personalization: ensure the algorithm's exploration/exploitation ratio surfaces at least one non-obvious feature or workflow per session, particularly for users who have not expanded their use case in 30+ days. Instrument discovery funnel metrics separately from engagement metrics. If a user has used the same three features for 60 days and never explored beyond them, that is an activation problem masked by engagement, not a success.

---

## Recipes

### R1 — Activation Default Sequence

**Goal.** Drive first-session activation by combining smart defaults, present-bias mitigation, and social proof, while ensuring every pre-selection passes the reversibility test.

**When to use.** A new user has signed up. The product requires at least one configuration step before delivering core value. Day-1 activation rate is below target, or the gap between sign-up and aha-moment is longer than one session.

**Stack.**

**Step 1: Map the activation path and identify the present-moment gap** (primitive #7).

```
Activation path audit:
  - Identify the aha-moment action (retention cohort analysis: which Day-1
    action predicts Day-30 retention most strongly?)
  - Measure median time from sign-up to aha-moment action
  - Identify the first drop-off point in the funnel
  - Ask: is there a present-moment reward available before the setup effort?
```

If the aha moment requires > 5 minutes of setup, a **value preview default** is needed — a pre-populated state (sample data, demo project, guided template) that delivers a System 1 reward before the real setup begins.

**Step 2: Set defaults with the reversibility test** (primitive #4).

For each default in the onboarding flow:

| Default | Reversible in ≤ 2 steps? | User endorsement likely? | Decision |
|---------|--------------------------|--------------------------|---------|
| Sample data pre-populated | Yes (one toggle) | Yes | Apply as default |
| Weekly digest email | Yes (one unsubscribe click) | Yes | Apply as default |
| Notification settings | Yes (Settings > Notifications) | Ambiguous — segment-dependent | Opt-in with recommended option |
| Annual billing | No (support ticket) | No — billing defaults are anti-patterns | Require explicit selection |

**Step 3: Add contextual social proof at the primary drop-off point** (primitive #5).

Identify the step where users most commonly abandon. Add a social proof signal anchored to the specific peer group:

```
"Teams like yours [SaaS, 15–50 people] typically complete this step in 3 minutes.
 It's the most common first action for users who stay active at 90 days."
```

Provenance check: verify the peer group definition, the time estimate, and the retention correlation are all accurate before shipping.

**Step 4: Add a commitment device for deferred steps** (primitive #7).

For high-value setup steps users skip in session 1 (data import, CRM connection, team invite):

```
"You can do this now (takes ~5 minutes) or we can remind you.
 When would you like to connect your CRM?
 [Now] [Tomorrow morning] [Next Monday]"
```

The scheduled reminder is a commitment device: it converts present-bias deferral into a future commitment. Requires: calendar permission request framed as a benefit to the user, not a company re-engagement mechanism.

**Step 5: Reversibility audit before launch.**

Before the activation sequence ships:
- [ ] Every pre-selected state can be undone in ≤ 2 clicks from within the flow
- [ ] Sample/demo data is clearly labeled as sample data — not presented as the user's real data
- [ ] Social proof claims have passed the provenance check (data verified within 30 days)
- [ ] Commitment device reminders are cancellable without calling support
- [ ] No billing state is pre-selected

**Success metric.** Day-1 aha-moment completion rate. Secondary: Day-7 retention. Fail signal: activation rate rises but Day-7 retention is flat or declining — users were activated into a state they did not want (see anti-pattern A3).

**Primitive links.** Defaults (#4) → Hyperbolic discounting (#7) → Social proof (#5) → Dual-system (#10) for System 1 path design.

---

### R2 — Retention Nudge Program

**Goal.** Reduce voluntary cancellation for users at churn risk by combining loss-aversion framing and social proof, while ensuring the intervention addresses a real churn signal rather than simply delaying an inevitable opt-out.

**When to use.** Churn prediction model identifies users at elevated cancellation risk (e.g., 30%+ 30-day churn probability). Trial users approaching day 14 with low engagement. Users who have opened the cancel flow but not completed it.

**Stack.**

**Step 1: Qualify the churn signal before applying retention framing.**

The ethical gate for this recipe: the intervention is justified only when there is real evidence that the user has not yet extracted the product's value — not when the churn signal is simply time-based. Distinguish:

| Signal | Intervention appropriate? | Rationale |
|--------|--------------------------|-----------|
| User has data/integrations, low recent logins | Yes | Genuine re-engagement opportunity |
| User never activated (no aha-moment action) | Retention nudge won't fix this — fix activation instead | Churn is a symptom of activation failure |
| User explicitly stated cancellation reason is pricing | Offer a downgrade or pause, not a loss-frame email | Loss framing on a price-driven churn is manipulative |
| User completed cancellation and confirmed | Do not re-contact with retention nudges | Contact is unwanted after explicit cancellation |

**Step 2: Build the loss-aversion inventory** (primitive #2).

Enumerate what the user will genuinely lose at cancellation:

```
User-created assets:
  - X saved reports / dashboards
  - Y configured integrations (list services by name)
  - Z team members with shared access
  - Days of usage history / activity log

Access that reverts:
  - Features that drop to read-only or are removed on free plan
  - API access level changes
  - Data export limits
```

Use this inventory to generate a personalized loss statement. "Your 14 reports, 3 integrations, and 6 team members' shared work will be affected" outperforms generic framing.

**Step 3: Add social-proof anchoring at the cancel-intent screen** (primitive #5).

The highest-value placement for social proof in a retention flow is at the cancel-intent screen — the moment of maximum uncertainty. Use real cohort data:

```
"Users who reconsidered cancelling at this stage and stayed
 saw [specific outcome] within [timeframe]."
```

Provenance requirement: this claim must come from actual cohort data. Run the analysis: of users who reached the cancel screen and did not complete cancellation, what were their 60-day outcomes? If you do not have this data, do not make the claim — use a pause offer instead (see Step 4).

**Step 4: Offer a pause as a commitment device** (primitive #7).

Users who would cancel often do so to avoid the next billing event, not because they are done with the product. A pause option (billing paused for 30–90 days, account preserved) converts many intention-to-cancel into a temporary halt:

```
"Pause for 30 days — your data stays, your team stays, billing resumes automatically.
 No action needed to continue."
```

The pause must auto-resume to avoid creating a free-indefinite loophole. Communicate clearly when billing resumes and make it easy to extend the pause or cancel during the pause period.

**Ethical gate: the churn-reduction test.**

Before shipping any retention nudge:
- [ ] The intervention targets users with a real activation or value gap — not users who made an informed cancellation decision
- [ ] The loss-frame content is factually accurate — no fabricated losses
- [ ] Social proof claims are from real cohort data, verified within 60 days
- [ ] The cancel path is one click away from every retention screen — retention nudges do not add friction to the cancellation flow itself
- [ ] The pause option auto-resumes with a clear email notification 7 days before billing

Fail signal: cancellation rate drops but chargebacks increase, or cancel-flow completion time increases without a corresponding drop in eventual cancellation. Both indicate users are being blocked rather than persuaded.

**Primitive links.** Loss aversion (#2) → Mental accounting (#8) for cost reframing → Social proof (#5) → Hyperbolic discounting (#7) for the pause commitment device.

---

### R3 — Feature-Discovery Flow

**Goal.** Increase feature adoption breadth for existing users by using choice architecture and dual-system design to surface the right next feature at the right moment, while maintaining friction symmetry across all discovery paths.

**When to use.** A significant percentage of retained users (e.g., > 40%) use only the onboarding-default feature set and have never explored features that predict higher retention or expansion revenue. Feature adoption breadth is a leading indicator of NRR and is below target.

**Stack.**

**Step 1: Build the feature adoption heat map.**

```
For each feature:
  - Adoption rate by cohort (first 7 days, 7–30 days, 30+ days)
  - Retention correlation: does adopting this feature predict Day-30 retention?
    (use causal-inference-applied.md R1 for debiased estimates)
  - Expansion correlation: does adopting this feature predict seat growth or upgrade?

Classify:
  - Tier 1: high retention correlation, low current adoption → primary discovery targets
  - Tier 2: moderate retention correlation, moderate adoption → secondary targets
  - Tier 3: power-user features, adoption not correlated with retention → contextual only
```

**Step 2: Design the System 1 discovery path** (primitives #9 and #10).

System 1 discovery works through contextual surfacing — the right feature appears in the workflow context where it is most relevant, not in a static features list. Design rules:

```
Rule 1 — One signal per session: surface at most one Tier 1 feature per session per user.
          Multiple prompts compete for attention and produce decision paralysis (choice
          architecture failure).

Rule 2 — Context match: the feature prompt appears in the workflow state where
          it is most useful. Example: "Schedule delivery" surfaces after the user
          publishes a report, not on the home screen.

Rule 3 — Progressive disclosure: show the feature benefit in one sentence;
          do not show the full feature documentation at point of discovery.
          One click takes the user to the full context.

Rule 4 — Completion bias: if the discovery path is a checklist, limit it to 3–5
          items maximum. Longer checklists are abandoned (completion bias requires
          the goal to be proximate).
```

**Step 3: Apply the friction-symmetry test.**

Friction symmetry means: the path to adopting a feature must not be significantly easier than the path to dismissing or deferring the feature prompt. Asymmetric friction — where adoption is one click and dismissal requires multiple steps — is a dark pattern (see anti-patterns A3 and A1 for the dismissal side of this).

```
Friction-symmetry checklist:
  [ ] "Try now" requires the same number of clicks as "Not now" or "Remind me later"
  [ ] Dismissal of a feature prompt does not re-surface the same prompt
      in the same session (re-surfacing within 7 days maximum)
  [ ] Feature prompts can be muted ("Don't show me feature tips") in 1 click
  [ ] User who mutes tips is not re-enrolled in feature tips without explicit opt-in
```

**Step 4: Instrument the discovery funnel separately from engagement.**

Discovery metrics require a separate funnel view from engagement metrics:

```
Discovery funnel:
  Prompt shown → Prompt dismissed → Feature explored → Feature adopted
                                                      ↓
                               Prompt shown → Feature explored → Feature adopted
                               (second exposure cohort)

Target metrics:
  - Prompt-to-explore rate: >15% on Tier 1 features (below = wrong context or wrong user)
  - Explore-to-adopt rate: >40% (below = the feature demo or onboarding is failing)
  - Filter-bubble rate: % of users with zero feature discovery events in 30 days
    (target: <20%; above = over-personalization, see anti-pattern A5)
```

**Step 5: Run the anti-filter-bubble check monthly** (anti-pattern A5).

```
Monthly check:
  - Users with no new feature adoption in 30 days and 3+ active sessions:
    flag as "discovery stagnation" cohort
  - For this cohort: inject one Tier 1 feature prompt in next active session
  - Measure: does the injection produce a prompt-to-explore rate above baseline?
    If yes: the user was receptive — the system failed to surface the feature
    If no: the user is truly in a settled workflow — do not over-prompt
```

**Ethical gate: discovery vs. upsell confusion.**

Feature discovery becomes a dark pattern when it conflates free-tier features with paid-tier features without clear labeling. Rules:
- [ ] All discovery prompts for paid/premium features are clearly labeled as upgrade-required
- [ ] The feature benefit shown in the prompt is achievable on the user's current plan, or the upgrade requirement is disclosed in the prompt itself (not revealed only after the user clicks through)
- [ ] Discovery prompts for paid features lead to a clear upgrade page, not to a feature that appears active until a paywall appears mid-flow (bait-and-switch)

**Success metric.** Tier 1 feature adoption rate at Day 30 for new cohorts. Secondary: NRR in the discovery-cohort vs. non-discovery cohort (use R1 from causal-inference-applied.md to estimate debiased feature impact). Fail signal: adoption rate rises but users churn at higher rates after adopting — the prompted feature did not deliver its promised value.

**Primitive links.** Choice architecture (#9) → Dual-system (#10) → Social proof (#5) for peer-behavior signals in prompts → Defaults (#4) for pre-selected feature configurations in the onboarding step.

---

## Composition

The three recipes compose into a connected product lifecycle:

| Stage | Recipe / Pattern | Primary Primitives |
|-------|-----------------|-------------------|
| Day 0–1 onboarding | R1: Activation default sequence | #4, #7, #5, #10 |
| Day 1–14 activation | P3: Present-bias mitigation + P4: Choice architecture | #7, #9, #10 |
| Day 14–30 feature adoption | R3: Feature-discovery flow | #9, #10, #5, #4 |
| Day 30+ retention | R2: Retention nudge program | #2, #5, #7, #8 |
| Social framing at each stage | P5: Social-proof placement | #5, #10 |

**Cross-cutting rule.** Every recipe closes with an ethical gate check. This is not optional. A behavioral intervention without an explicit ethical gate — reversibility test (R1), churn-reduction test (R2), friction-symmetry test (R3) — is not ready to ship. Gate failures must be resolved before the pattern goes to production.

**Primitive coverage in this file:**

| Primitive | Where used |
|-----------|-----------|
| #2 Loss Aversion | P2, A4, R2 |
| #4 Defaults | P1, P3, P4, A3, R1, R3 |
| #5 Social Proof | P5, A2 (contrast), R1, R2, R3 |
| #7 Hyperbolic Discounting | P3, A2, R1, R2 |
| #8 Mental Accounting | P2 (cross-ref), R2 |
| #9 Choice Architecture | P4, A1 (contrast), A5, R3 |
| #10 Dual-System Cognition | P1, P3, P4, P5, R1, R3 |
| #1 Prospect Theory | P2 (framing calibration cross-ref) |
| #6 Scarcity | A2 (misuse diagnosis) |

---

## Sources

1. Kahneman, D., & Tversky, A. (1979). Prospect Theory: An Analysis of Decision under Risk. *Econometrica*, 47(2), 263–292. — Loss aversion coefficient (~2.25), framing effects.
2. Kahneman, D. (2011). *Thinking, Fast and Slow*. Farrar, Straus and Giroux. — Dual-system cognition, System 1/2 design implications.
3. Thaler, R. H., & Sunstein, C. R. (2008). *Nudge: Improving Decisions About Health, Wealth, and Happiness*. Yale University Press. — Choice architecture, harm test, defaults ethics.
4. Ariely, D. (2008). *Predictably Irrational*. Harper. — Anchoring, decoy effect, mental accounting in product contexts.
5. Cialdini, R. B. (1984). *Influence: The Psychology of Persuasion*. Harper Business. — Social proof, scarcity, reciprocity.
6. Frederick, S., Loewenstein, G., & O'Donoghue, T. (2002). Time Discounting and Time Preference: A Critical Review. *Journal of Economic Literature*, 40(2), 351–401. — Hyperbolic discounting, present bias, commitment devices.
7. Eyal, N. (2014). *Hooked: How to Build Habit-Forming Products*. Portfolio. — Hook model, activation mechanics, ethical habit design.
8. CMA (2022). *Subscriptions and Recurring Payments: Consumer Market Research*. Competition and Markets Authority. — UK regulatory context for negative-option billing and cancellation practices.
9. ICO (2022). *Privacy in the Product Design Lifecycle*. Information Commissioner's Office. — Deceptive design patterns and GDPR consent validity.
10. Kohavi, R., Tang, D., & Xu, Y. (2020). *Trustworthy Online Controlled Experiments*. Cambridge University Press. — Instrumentation standards for product experiments; novelty effects.
11. Amplitude (2025). *Product Benchmarks Report*. — Activation, retention, and feature adoption benchmarks for B2B SaaS and B2C products.

---

**Cross-links.**
- Primitive playbooks: [`foundations-behavioral-economics/assets/templates/behavioral-economics/`](../../foundations-behavioral-economics/assets/templates/behavioral-economics/)
- Primitives overview: [`foundations-behavioral-economics/references/primitives-overview.md`](../../foundations-behavioral-economics/references/primitives-overview.md)
- Existing PM behavioral reference: [`behavioral-economics-product-decisions.md`](behavioral-economics-product-decisions.md)
- Causal toolkit (feature impact debiasing): [`causal-inference-applied.md`](causal-inference-applied.md)
- Cognitive load design: [`cognitive-load-product-design.md`](cognitive-load-product-design.md)
- Metrics and guardrails: [`metrics-best-practices.md`](metrics-best-practices.md)
