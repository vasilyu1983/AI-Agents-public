# Evaluative Methods Guide

Operator's reference for UX researchers and PMs validating concepts before build. Each method entry covers when to deploy it, how to run it correctly, and where it breaks.

---

## Table of Contents

1. [Wizard of Oz Testing](#1-wizard-of-oz-testing)
2. [Concierge Testing](#2-concierge-testing)
3. [Painted-Door Testing](#3-painted-door-testing)
4. [Fake-Door / Smoke Testing](#4-fake-door--smoke-testing)
5. [Conjoint Analysis](#5-conjoint-analysis)
6. [MaxDiff (Best-Worst Scaling)](#6-maxdiff-best-worst-scaling)
7. [Kano Analysis](#7-kano-analysis)
8. [Diary / Longitudinal Field](#8-diary--longitudinal-field)
9. [Beta Panels](#9-beta-panels)
10. [Method-Selection Decision Table](#method-selection-decision-table)
11. [Ethics Summary](#ethics-summary)

---

## 1. Wizard of Oz Testing

### Definition

A human operator ("the Wizard") simulates the system's behavior behind a real-feeling interface. Participants believe they are interacting with working technology. The UI looks and feels production-quality; the intelligence is manual.

### When to Use

- Validating AI or agent products before the model or pipeline is built
- Testing complex multi-step flows where engineering cost is high
- Exploring interaction patterns before committing to an infra design
- Any scenario where "does the concept work?" must be answered before "can we build it?"

### Protocol

1. **Script system behavior** — Define a decision tree or response library before the session. The Wizard follows the script; improvisation invalidates comparability across sessions.
2. **Train the Wizard** — Run dry sessions until response latency and phrasing are consistent. Inconsistencies that participants notice will be attributed to product quality, not operator error.
3. **Instrument as if real** — Use the same metrics you would measure on a shipped product: task completion rate, time-on-task, error rate, satisfaction (e.g., SUS, single-item post-task).
4. **Separate observation from operation** — Ideally the Wizard does not observe participant reactions in real time; a second researcher does. Prevents the Wizard from adapting to cues.
5. **Control session pacing** — If real-system latency is relevant (e.g., AI response speed), introduce deliberate delays to match expected production timing.
6. **Debrief every participant** — Mandatory. Explain the simulation method after the session. Capture how participants felt about the deception and whether it affected their feedback.

### Ethics

- **Debrief is non-negotiable.** Participants must be told before they leave that the system was simulated.
- Do not use Wizard of Oz to validate claims that could affect participant decisions about real products, safety, or financial risk.
- If participants interact with fabricated content that could influence belief (e.g., health information), disclose the fabrication immediately in debrief.
- Obtain consent for recording even when the "product" is fake.

### Anti-Patterns

| Anti-pattern | Why it fails |
|---|---|
| Wizard becomes too skilled | Produces a ceiling effect — participants rate a simulation better than any realistic system will ever perform. Decisions built on these results lead to failed launches. |
| Inconsistent Wizard responses | Participants attribute variance to product bugs; you measure operator error, not concept validity. |
| Skipping debrief | Ethical violation; also contaminates your participant pool for future studies. |
| Not measuring as if real | Running qualitative-only sessions squanders the quantitative signal Wizard of Oz can produce. |

### Examples

- Spotify's early "Discover" playlist — before the recommendation algorithm existed, editors manually curated playlists served to test users as if algorithmically generated.
- Early voice assistant prototypes (pre-Siri era) — researchers typed responses while participants spoke to a device, testing the interaction model before NLP was viable.

---

## 2. Concierge Testing

### Definition

The founding team (or a small research team) manually delivers the service end-to-end for a handful of real customers. No automation. The "product" is human labor presented as a service.

### When to Use

- Pre-MVP, before any engineering investment
- Validating willingness to pay and the real workflow — not a surveyed intention, but revealed behavior
- Identifying where customers need help and where they drop off, before you build the wrong automations
- Services where the value proposition is the output, not the interface

### Protocol

1. **Handpick the first customers** — Choose 5–15 people who fit the target persona and have an acute version of the problem. Do not recruit broadly; you need people who will tell you the truth.
2. **Offer the service explicitly** — Tell them you will handle their request personally. Do not imply automation exists yet.
3. **Set an automation horizon** — Communicate upfront: "We're doing this manually while we build the automated version." This sets expectations and prevents customers from being surprised by future service changes.
4. **Measure what matters:**
   - Willingness to pay (did they pay? what did they push back on?)
   - Retention (did they come back? did they refer?)
   - Qualitative friction (what did they ask for that you weren't offering?)
5. **Track your own labor cost** — Time-per-unit is the automation investment signal. High labor per unit + strong retention = worth automating.
6. **Conduct exit interviews when customers churn** — Most important signal for understanding where the concept fails.

### Anti-Patterns

| Anti-pattern | Why it fails |
|---|---|
| Scaling concierge instead of automating | You build a services business, not a product. Unit economics never close. |
| Mistaking concierge enthusiasm for PMF | Customers may love the personal attention, not the underlying service. Automate and re-measure — enthusiasm often drops. |
| Starting too broad | Delivering to 50 customers manually before you understand the workflow means you scale the wrong process. |
| Not setting the automation expectation | Customers feel misled when you switch to a product experience. |

---

## 3. Painted-Door Testing

### Definition

A feature CTA (call-to-action) is surfaced in the live product as if the feature exists. It is not built. Clicks are instrumented; users who click are redirected to a "coming soon" or intent-capture screen.

### When to Use

- Prioritizing a backlog of candidate features by real demand, not PM intuition
- When you have existing traffic and can run in-product experiments
- Comparing multiple feature ideas head-to-head without building any of them

### Protocol

1. **Instrument the click event** — Tag with feature ID, user segment, placement context. You need this for analysis.
2. **After click: acknowledge and capture** — Show a message that acknowledges the user's intent ("We're building this — want to be notified?"). Offer email capture or a brief survey (2–3 questions max).
3. **Do not gate users out of unrelated work** — If clicking the CTA blocks a user from completing another task, you are measuring frustration, not feature demand.
4. **Apologize for the interruption** — The post-click screen should never feel like a bait-and-switch. Tone matters: "We're working on this" lands better than silence.
5. **Run each door for a fixed time window** — Typically 1–2 weeks, or until you reach the sample size threshold (see below).
6. **Analyze by segment** — Overall CTR is rarely actionable. Segment by user cohort, tenure, and use case.

### Sample Size

Stable click-through rate estimates typically require **1,000–2,000 impressions per door**. Below 500 impressions, variance is too high for prioritization decisions. If you cannot reach this threshold organically, the feature is in a low-traffic context — consider a targeted in-app prompt or email campaign instead.

### Ethics

- Users must not be blocked from completing real tasks because of a painted door.
- The post-click screen must not imply a product commitment you cannot keep (e.g., "launching next month" when there is no timeline).
- Capture and honor opt-in emails — if a user signs up for notification, notify them.

### Anti-Patterns

| Anti-pattern | Why it fails |
|---|---|
| Testing too many doors simultaneously | Burns user trust; users learn the pattern and stop clicking on anything new. |
| Assuming click-through equals usage | Intent ≠ adoption. Users click out of curiosity; whether they would use a shipped feature is a separate question. |
| Not segmenting results | Aggregate CTR hides the segment that actually wants the feature. |
| Deploying in a low-context placement | A CTA placed where users are confused yields noise; place where the feature would naturally live. |

---

## 4. Fake-Door / Smoke Testing

### Definition

A variant of painted-door, but applied pre-product: a standalone landing page or ad campaign describes a product that does not yet exist, driving toward a signup or waitlist. Measures market-level interest before any build.

### When to Use

- Pre-product, validating a new market or product wedge
- Comparing multiple product framings or positioning angles
- Testing whether a target audience exists and can be reached at viable CAC

### Protocol

1. **Build a minimal landing page** — Headline, value proposition, one CTA ("Join the waitlist" or "Get early access"). No fabricated screenshots of non-existent UI.
2. **Drive traffic with a small ad budget** — $500–$2,000 is usually enough for a directional read. Use the channel where your target audience actually lives.
3. **Measure cost-per-signup and intent quality** — Cost-per-signup is your demand signal. Intent quality is measured via the optional follow-up question on the confirmation page ("What problem are you trying to solve?").
4. **Respond to every signup within 48 hours** — A personal email explaining you are in early development. This converts signups into interview candidates.
5. **Run at least two framings in parallel** — Different headlines, different audiences. Split-test the idea, not the ad creative.

### Ethics

- The CTA must set accurate expectations. "Join the waitlist" or "Get early access" is honest. "Buy now" for a product that does not exist is not.
- Do not collect payment information for a product that is not shippable.
- Disclose to interviewees that the product is pre-launch and not built yet.

### Anti-Patterns

| Anti-pattern | Why it fails |
|---|---|
| Treating signup rate as PMF signal | Signups measure ad appeal and landing page copy. They do not measure whether users will pay, retain, or integrate the product into their workflow. |
| Over-optimizing the ad creative | A compelling ad for a weak idea produces misleading results. Optimize the idea framing, not the click-bait. |
| Not following up with signups | Signups are your earliest research participants. Not contacting them wastes the richest intent signal you have. |

---

## 5. Conjoint Analysis

### Definition

A quantitative method that decomposes consumer preference into part-worth utilities for individual product attributes by forcing respondents to make realistic tradeoff choices between product profiles. Reveals which attributes drive choice and by how much.

### When to Use

- Pricing decisions: what features justify a price premium?
- Feature bundling: which combination of features maximizes appeal?
- Multi-attribute product decisions where survey-based importance ratings yield inflated scores (everything seems important)
- When you need willingness-to-pay estimates grounded in revealed preference

### Variants

- **CBC (Choice-Based Conjoint)** — Default. Respondents choose among 3–4 product profiles per task. Most realistic to actual purchase behavior.
- **ACBC (Adaptive CBC)** — Adaptive questionnaire that adjusts based on prior responses. More efficient for complex attribute sets. Requires Sawtooth or similar platform.
- **Full-profile traditional conjoint** — Older method; rarely used for consumer research today. CBC is preferred.

### Sample Size

**200–500 respondents** for stable part-worth utility estimates at the aggregate level. For segment-level analysis (e.g., by price sensitivity tier), plan for 200+ per segment.

### Tools

| Tool | Fit |
|---|---|
| Sawtooth Software (Lighthouse Studio) | Full-featured; industry standard for CBC/ACBC |
| Conjointly | SaaS; faster setup; good for straightforward CBC |
| Qualtrics (Conjoint module) | Integrated with broader survey; moderate complexity ceiling |

### Output

- **Part-worth utilities** per attribute level (higher = more preferred)
- **Relative importance scores** per attribute (how much each attribute drives choice)
- **Willingness-to-pay** estimates (derived by including price as an attribute)
- **Market simulation** (predict share-of-preference for proposed configurations)

### Anti-Patterns

| Anti-pattern | Why it fails |
|---|---|
| Asking about features participants cannot evaluate | If respondents have no context for what "API access" or "predictive reordering" means, utilities are noise. Screen or explain. |
| Too many attributes | Cognitive overload degrades response quality. Keep to **5–7 attributes** maximum. |
| Including price as the only differentiator | Respondents learn to always choose the cheapest option. Ensure non-price attributes have real variance. |
| Reporting aggregate utilities without segment cuts | Aggregate masks price-sensitive vs. feature-sensitive segments, which often require different packaging. |

---

## 6. MaxDiff (Best-Worst Scaling)

### Definition

A forced-choice method where respondents repeatedly select the best and worst item from subsets of items drawn from a larger set. Produces utility scores for all items that are more discriminating than Likert-scale ratings.

### When to Use

- Prioritizing 8–30 features, benefit claims, or value propositions
- When Likert-scale surveys are returning uniformly high scores (ceiling effect)
- When you need a defensible rank-ordered list for roadmap decisions
- Comparing messaging claims or product benefit statements

### Sample Size

**150–300 respondents** for stable item-level utility estimates. Fewer respondents are acceptable for directional prioritization (top 5 vs. bottom 5); more are needed for fine-grained middle-tier distinctions.

### Output

- **Utility score per item** (higher = stronger preference; items are directly comparable)
- **Rank-ordered list** across the full item set
- Segment-level breakdowns (e.g., power users vs. casual users often produce different priority rankings)

### Anti-Patterns

| Anti-pattern | Why it fails |
|---|---|
| Using Likert instead because it feels easier | Likert yields ceiling effects — most features rated 4–5 out of 5 with no discrimination. MaxDiff forces tradeoffs that reveal true priorities. |
| Including items that are not independently meaningful | If two items are logically bundled, respondents cannot separate them and scores are unreliable. |
| Over-interpreting small utility gaps | Gaps of 1–3 utility points in the middle of the distribution are often within noise. Focus on the top and bottom tiers. |

---

## 7. Kano Analysis

### Definition

A structured survey method that classifies features into five categories based on two questions per feature: one asking how the user feels if the feature is present (functional), one asking how they feel if it is absent (dysfunctional).

**Kano categories:**

| Category | Meaning |
|---|---|
| **Must-be (M)** | Expected; absence causes dissatisfaction; presence is taken for granted |
| **Performance (P)** | More is better; linear relationship with satisfaction |
| **Attractive (A)** | Unexpected delight; presence increases satisfaction; absence is not missed |
| **Indifferent (I)** | Neither presence nor absence affects satisfaction |
| **Reverse (R)** | Presence causes dissatisfaction for some users |

### When to Use

- Distinguishing "table stakes" features from "delighters"
- Prioritizing across a mixed backlog where some features are expected and others are bets
- Understanding how feature expectations shift over time (Attractive → Must-be migration)

### Protocol

1. **Write functional/dysfunctional question pairs** for each feature being evaluated. Example:
   - Functional: "If [feature] was available, how would you feel?"
   - Dysfunctional: "If [feature] was not available, how would you feel?"
   - Response scale: "I like it / I expect it / I'm neutral / I can tolerate it / I dislike it"
2. **Apply the Kano evaluation table** to map each respondent's answer pair to a category.
3. **Aggregate categories** across respondents. For each feature, report the modal category and the distribution.
4. **Sample size:** 100–200 respondents is sufficient for stable category assignments at the aggregate level.

### Output

- Kano category per feature (modal classification)
- Distribution across categories (useful when a feature splits the population — e.g., 40% Must-be, 30% Attractive)
- Prioritization input: ship Must-be first; invest in Performance for differentiation; treat Attractive as delight bets

### Anti-Patterns

| Anti-pattern | Why it fails |
|---|---|
| Treating Attractive features as higher priority than Must-be | Must-be features cause active dissatisfaction when absent. No amount of delight compensates for failing at the baseline. |
| Ignoring category drift | Attractive features become Must-be as the market matures (e.g., dark mode, search, notifications). Re-run Kano every 12–18 months for mature products. |
| Testing too many features in one survey | Respondents fatigue; past ~15 features, response quality degrades significantly. Break into separate instruments or prioritize which features need classification. |

---

## 8. Diary / Longitudinal Field

Cross-reference: [consumer-experience-quality.md](consumer-experience-quality.md) for full diary study protocol, participant selection, and prompt design.

### Core Use Case

Diary and longitudinal field methods capture behavior and experience as it naturally occurs over time, in real context. They surface what participants cannot reconstruct in a lab session: gradual habit formation, abandonment moments, emotional arcs, and workarounds that develop over days or weeks.

### ESM (Experience Sampling Method) Variant

Experience Sampling Method is a signal-triggered or time-triggered diary protocol that captures in-the-moment experience rather than retrospective end-of-day reflection.

**Two probe types:**

| Probe type | Trigger | Best for |
|---|---|---|
| **Signal-contingent** | Fixed intervals (e.g., 3×/day at random times) | Capturing baseline experience regardless of product interaction; mapping emotional context |
| **Event-contingent** | Participant-initiated when a specified event occurs (e.g., "after you use the app") | Capturing post-use experience with minimal recall decay |

**ESM protocol decisions:**

- **Sampling frequency:** 3–8 prompts per day. Above 8, compliance drops sharply.
- **Prompt length:** 3–5 questions maximum. Single-item affect measures (e.g., valence + arousal) work well at high frequency.
- **Duration:** 7–14 days balances ecological validity with participant fatigue.
- **Platform:** Texting-based (Qualtrics SMS, ExperienceSampler) outperforms app-based for compliance in consumer studies.

**Signal-contingent** probes are better for understanding the emotional context in which your product is used. **Event-contingent** probes are better for measuring in-the-moment reactions to specific product interactions.

**When to use ESM over standard diary:** When you need high-frequency emotional or behavioral data, when retrospective recall is a known distortion risk (e.g., pain, frustration), or when the relevant behavior is sporadic and unpredictable in timing.

---

## 9. Beta Panels

### Definition

A curated cohort of real users who receive recurring access to pre-release product builds in exchange for structured feedback. Distinct from a public beta: membership is intentional, the feedback loop is active, and participation requires ongoing commitment from both researcher and participant.

### When to Use

- Consumer apps with seasonal or weekly release cadence (mobile, SaaS)
- When you need behavioral data from real use over multiple releases, not single-session evaluations
- When qualitative context is needed to explain quantitative signals from analytics
- Validating accessibility, localization, or edge-case scenarios across a diverse use-case segment

### Protocol

1. **Define cohort size and segmentation:**
   - 50–150 participants for small-team consumer apps
   - 150–500 for larger apps with distinct use-case segments
   - Segment by use case, not just demographics. A fitness app needs casual users, competitive athletes, and injury-recovery users — not just age bands.
2. **Establish the value exchange explicitly:**
   - What participants get: early access, influence over roadmap, direct access to the team
   - What they commit to: weekly survey (5–10 min), opt-in to monthly 30-min interview
   - Make this clear at recruitment. Vague commitments produce low engagement.
3. **Weekly survey cadence:**
   - Keep to 5–8 questions. Rotate focus (onboarding one week, a specific feature the next).
   - Include one fixed benchmark item each week for trend tracking (e.g., NPS or a custom satisfaction item).
4. **Opt-in interview rotation:**
   - Target 5–10 interviews per release cycle from the panel.
   - Rotate who you interview — do not only interview the most vocal members.
5. **Manage panel health:**
   - Track response rate per participant. Below 50% over 3 consecutive weeks = flag for re-engagement or replacement.
   - Refresh 20–30% of the panel every 6 months to prevent stagnation.
6. **Close the loop:**
   - After each release, send a brief summary of what feedback influenced. This is the primary retention mechanism for panel participants.

### Anti-Patterns

| Anti-pattern | Why it fails |
|---|---|
| Treating beta panel as PMF audience | Panelists are enthusiasts who opted in. Their satisfaction scores are systematically higher than the general user population. Do not use panel NPS as a proxy for market NPS. |
| Ignoring panel fatigue | Response rates below 40% mean you are collecting biased data from your most engaged advocates. Rotate, refresh, and reduce survey load. |
| Selection bias of enthusiasts | If you recruit from power-user communities, your panel skews toward people who would use any version of your product. Deliberately recruit mid-tier and at-risk users. |
| Not acting on feedback visibly | Participants who see no changes attributable to their input disengage within 4–6 weeks. |

---

## Method-Selection Decision Table

| Research question | Primary method | Secondary / validation |
|---|---|---|
| Does this concept work before we build it? | Wizard of Oz | Concierge |
| Will users pay for this? What is the workflow? | Concierge | Customer interviews |
| Which features should we build first? | MaxDiff | Kano |
| What is the relative value of attributes in a purchase decision? | Conjoint (CBC) | — |
| Is there demand for a feature not yet in the product? | Painted-door | Follow-up survey |
| Does a market exist for a new product? | Fake-door / Smoke | Customer development interviews |
| Which features are table stakes vs. delighters? | Kano | — |
| How does experience evolve over time in real context? | Diary / Longitudinal | ESM for high-frequency affect |
| How does a pre-release build perform across release cycles? | Beta panel | Weekly survey + opt-in interviews |
| How do users feel immediately after using the product? | ESM (event-contingent) | Post-task satisfaction scale |
| What features resonate across 10–30 items when Likert is unhelpful? | MaxDiff | — |

---

## Ethics Summary

### Consent

- All participants must consent before data collection begins, regardless of method.
- For Wizard of Oz and painted-door: obtain consent for session recording and data use even when the full nature of the study is disclosed post-session.
- For beta panels: consent must cover the use of behavioral data from pre-release builds, not just survey responses.

### Deception

- Deception is sometimes methodologically necessary (Wizard of Oz, painted-door). It is acceptable only when:
  1. The research question cannot be answered without it
  2. Participants are debriefed as soon as possible after the session
  3. No participant is harmed by the deception
- Deception is never acceptable when it involves claims about health, safety, financial risk, or legal status.
- "Coming soon" screens are not deception. Fabricated social proof, fake reviews, or false scarcity claims are.

### Debrief

- Required after any study involving deception (Wizard of Oz, any covered observation).
- Debrief should: explain what was simulated, explain why, give participants the opportunity to withdraw their data.
- Document debrief completion in your research log.

### Data Handling

- Do not collect more data than the research question requires.
- PII from painted-door email captures must be stored with the same care as production user data.
- Beta panel behavioral data (usage logs from pre-release builds) requires explicit consent; treat as sensitive.
- Retention policy: set a deletion date for participant data at the outset. Default: delete 12 months after the research question is closed.

### Researcher Obligations

- Report findings accurately, including null results.
- Do not run a study when the conclusion is predetermined — that is stakeholder validation theater, not research.
- If a study reveals that a feature causes harm (even unintentionally), escalate immediately rather than omitting from the report.
