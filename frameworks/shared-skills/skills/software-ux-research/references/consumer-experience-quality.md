# Consumer Experience Quality

How elite consumer products measure and improve experience quality beyond raw usability. This is the playbook the teams behind Duolingo, Strava, Notion, Booking.com, Spotify, Headspace, Things, Linear use to find friction the analytics dashboard misses and to know whether their product is actually loved.

---

## Table of Contents

- [The Quality Lens](#the-quality-lens)
- [Continuous Discovery and Opportunity Solution Trees](#continuous-discovery-and-opportunity-solution-trees)
- [JTBD Interviews That Actually Work](#jtbd-interviews-that-actually-work)
- [Friction Logging](#friction-logging)
- [Delight and Emotion Measurement](#delight-and-emotion-measurement)
- [Diary Studies for Habitual Products](#diary-studies-for-habitual-products)
- [Competitive UX Benchmarking](#competitive-ux-benchmarking)
- [Onboarding Research Patterns](#onboarding-research-patterns)
- [Habit and Retention Research](#habit-and-retention-research)
- [Anti-Patterns](#anti-patterns)
- [Sources](#sources)

---

## The Quality Lens

Most product orgs over-measure task success and under-measure experience quality. The result: products that pass usability tests and lose retention.

A consumer-grade research practice tracks all four:

| Layer | What it answers | Methods |
|-------|-----------------|---------|
| **Task success** | Can users do the thing? | Usability testing, completion rates |
| **Friction** | What makes users hesitate, retry, or abandon mid-task? | Friction logs, session replay + qual, post-task probes |
| **Emotion** | How does the experience feel? | Post-task delight, PrEmo, AttrakDiff, sentiment in diary |
| **Meaning** | Does the product help the user become who they want to be? | JTBD interviews, longitudinal studies, deep narrative |

A "good" usability test that produces no answer to layers 2–4 has missed the point. Consumer products live or die on layers 2–4.

---

## Continuous Discovery and Opportunity Solution Trees

Teresa Torres's Continuous Discovery (book 2021, mainstream by 2024) is the default research operating system for product teams that want to ship the right thing weekly.

### The cadence

- **Weekly**: 1–2 customer interviews. Always-on. Researchers facilitate; PMs and designers attend.
- **Per-discovery cycle (1–4 weeks)**: synthesis → opportunity tree → assumption tests → decision.
- **Per-quarter**: revisit the desired outcome; prune the tree.

### Opportunity Solution Tree (OST)

```
Desired outcome
    │
    ▼
[Opportunity] [Opportunity] [Opportunity]
    │              │              │
    ▼              ▼              ▼
[Solution]     [Solution]     [Solution]
    │              │              │
    ▼              ▼              ▼
[Test]         [Test]         [Test]
```

- **Outcome**: a measurable change in user behavior (not a feature shipped).
- **Opportunity**: a customer pain, desire, or need surfaced by interviews. Phrased in the user's words.
- **Solution**: a specific design or feature that could address an opportunity.
- **Assumption test**: the smallest experiment that would validate or invalidate the solution before building.

### When to use OST

- always, for any team with weekly customer access
- replaces backlog grooming as the strategic surface
- visible in the team's primary tool (Miro, Whimsical, FigJam, or Mural)

### Common OST mistakes

- starting from solutions and inventing opportunities to justify them
- making opportunities so abstract they don't constrain solutions ("Users want to be productive")
- treating the tree as a one-time artifact instead of a living document
- not pruning — every tree needs ruthless pruning weekly

Sources: [Teresa Torres — producttalk.org](https://www.producttalk.org/opportunity-solution-trees/).

---

## JTBD Interviews That Actually Work

Jobs-to-be-Done interviews surface the *forces of progress* — what made someone consider switching to your product, what almost stopped them, and what they're really trying to become. The Switch interview (Bob Moesta, Chris Spiek, Re-Wired Group) is the canonical structure.

### The Switch interview structure

1. **First thought** — when did the user first think about solving this problem? Anchor a date.
2. **Passive looking** — what were they doing before they actively searched?
3. **Active looking** — what triggered the active search?
4. **Decision** — what made them choose your product specifically?
5. **First use** — what was their first experience? What surprised them?
6. **Habit / abandonment** — did they return? Why or why not?

The interview takes 60–90 minutes. Recordings are essential — the *exact words* matter.

### Forces of progress

- **Push** of the current situation (what's bad about today)
- **Pull** of the new solution (what's appealing about your product)
- **Anxiety** of the new (what worries them about switching)
- **Habits** of the present (inertia keeping them on the old solution)

A product wins when push + pull > anxiety + habit.

### What JTBD interviews change

- Marketing copy: use the exact "push" and "pull" language users said.
- Onboarding: address the "anxiety" within the first 60 seconds.
- Pricing: anchor against what the user was previously spending (often more than you charge).
- Roadmap: invest in opportunities that increase pull or reduce anxiety, not features that copy competitors.

### Anti-patterns

- asking "what do you want" — JTBD asks "tell me about the day you decided to switch"
- skipping the timeline; the dates anchor memory
- letting the user speculate about future behavior — JTBD reconstructs past behavior
- recruiting only happy customers — JTBD specifically wants recent switchers (within 90 days), including from your product to a competitor

---

## Friction Logging

Friction logs are the highest-leverage method most consumer teams under-use. They surface the small frustrations that don't show up in success metrics but drive churn.

### The method

1. The researcher uses the product end-to-end as a fresh user, narrating thoughts aloud.
2. Every moment of hesitation, retry, confusion, surprise, or annoyance is logged with a timestamp.
3. Severity is rated 1–5 and tagged by category (cognitive, emotional, technical, content).
4. Output is a single document: timeline + severity + screen + suggested fix.

### Format

```
[09:14:02] [3] [cognitive] Onboarding screen 2: "Set up your workspace"
  Friction: Don't know what a "workspace" means in this product. The illustration doesn't help.
  Suggested fix: Either explain ("A workspace is your team's home for X") or skip — pre-create one.

[09:14:47] [4] [emotional] Permission prompt: notifications
  Friction: Asked on first launch with no context. Said no instinctively. Later realized I needed it for the core loop.
  Suggested fix: Defer to first-relevant-moment with custom pre-prompt.

[09:16:13] [2] [content] Empty inbox: "No notifications"
  Friction: Greyscale illustration, no CTA. Don't know how to get notifications.
  Suggested fix: Empty state with verb CTA ("Invite a teammate to get pinged when they reply").
```

### Who runs friction logs

- Researchers run quarterly across the product.
- Designers run on every flow they've designed, before it ships.
- Product managers run on competitor products to identify gaps.
- New employees in their first week — they catch what tenured employees have stopped seeing.

The friction log is a *cheap, recurring* method. One researcher can produce a 30-item log in 90 minutes. The aggregated quarterly log is one of the most actionable artifacts in the org.

---

## Delight and Emotion Measurement

Standard usability metrics (SEQ, SUS, completion rate) don't capture how the experience *feels*. For consumer products, feelings drive retention.

### Per-task / per-screen

- **Single Ease Question (SEQ)**: 7-point scale, "How easy or difficult was that task?" Captures task-level friction. Use in every moderated study.
- **Post-task delight (5-point or smiley scale)**: "How did that feel?" Captures the emotional layer SEQ misses.
- **Post-task surprise**: "What surprised you, positive or negative?" Open-ended; surfaces unexpected delight or friction.

### Per-session / per-experience

- **PrEmo** (Pieter Desmet, TU Delft): non-verbal emotional self-report using cartoon characters expressing 14 emotions. Removes language bias; works cross-culturally. Used by automotive, F&B, consumer electronics.
- **AttrakDiff**: 28 word pairs across hedonic (stimulation, identity) and pragmatic (controllable, useful) quality. Validated, well-cited; used in academic and applied UX since 2003.
- **Microsoft Desirability Toolkit**: 118 product reaction cards. User picks 5 that describe the product. Surfaces affective vocabulary.
- **Net Easy Score / NES**: "How easy was it to do X?" 5-point. Good predictor of churn for service products.

### Per-product (ongoing)

- **NPS (Net Promoter Score)** is overused and misused. It works as a *trend indicator* over months, not as a verdict. Don't fire teams over NPS dips.
- **PMF survey** (Sean Ellis): "How would you feel if you could no longer use [product]?" — Very disappointed / Somewhat disappointed / Not disappointed / N/A. >40% "Very disappointed" is the classic PMF threshold.
- **Customer Effort Score (CES)**: "The product made it easy to handle my issue." Strong predictor of repeat business.
- **Micro-NPS / sentiment in-product**: quick smiley-tap after completing a meaningful task. Read trends, never individual scores.

### Where to read emotion *without* asking

- session replays at moments of hesitation (3+ second pauses, rapid back-and-forth navigation, rage clicks)
- support ticket sentiment per feature
- app store reviews tagged by feature
- social media mentions with sentiment classification (Brandwatch, Sprinklr, manual)

---

## Diary Studies for Habitual Products

For products people use *over time* (fitness, journaling, learning, finance, sleep, mental health, dating), point-in-time studies miss the most important question: does the product fit into life?

### Diary study structure

- **Duration**: 1–4 weeks, depending on use frequency.
- **Cadence**: 1–2 entries/day for high-frequency products; weekly for lower-frequency.
- **Prompts**: short, mobile-friendly, mix of structured (Likert) and open (photo, voice memo, free text).
- **Tools**: dscout, Indeemo, ethnio, Lookback. For lightweight: a daily Slack DM bot or simple form.

### Prompt patterns

- Morning: "What did you plan for today's session? On a 1–5, how motivated do you feel?"
- After use: "How did that session compare to what you planned? Photo of your face right now (optional)."
- Evening: "Did the product help you do what you wanted today? What got in the way?"
- Weekly close-out: a 30-min synthesis interview reviewing the week's entries together.

### What diary studies surface that other methods miss

- **Skipped sessions** — when and why the user *didn't* use the product. Usability tests can't see this.
- **Compensating behaviors** — what users do *outside* your product to get the same value (other apps, paper, memory).
- **Emotional arcs** — how feelings shift across days, not within a single session.
- **Social context** — did they show the app to a friend? Did anyone notice the streak? Habits live in social context.
- **Permanent abandonment moment** — diary studies often catch the moment the user permanently stops; in-product analytics see only the absence.

---

## Competitive UX Benchmarking

To know whether your craft is competitive, you must directly compare. Most teams know this and skip it.

### Comparative usability test

- Recruit 8–12 users.
- Run identical task scenarios across 3–5 products including yours.
- Measure: completion rate, time-on-task, SEQ, post-task delight, "which would you use?" preference.
- Counterbalance order to control for learning effects.
- Output: a per-task scorecard plus qualitative themes.

### Competitive friction log

- The researcher runs the same flow (signup → first value, e.g.) on each competitor.
- Same severity rating system as your own friction log.
- Compares friction *patterns*: where do all products struggle (industry problem); where does only ours struggle (us-specific debt); where are we strongly ahead (defensible craft).

### Competitive teardown

- 60–90 minute structured walkthrough of competitor onboarding, core loop, settings, and edge cases.
- One researcher, one PM, one designer, one engineer ideally — fresh eyes from each function.
- Captured in a shared doc with screenshots, observations, and "we should steal this" / "we already do this better" / "this is bad and they get away with it" annotations.

Run quarterly per direct competitor; semi-annually per adjacent.

---

## Onboarding Research Patterns

Onboarding is the single highest-leverage research surface. A friction here loses 30–60% of users for the rest of the funnel.

### Methods that work

1. **First-run usability test**: 6–8 users, fresh installs, narrate aloud. Stop the test 5 minutes into the product. The first 5 minutes is where activation succeeds or fails.
2. **Drop-off interview**: contact users who didn't return after their first session within 24 hours. "Tell me about that experience."
3. **Activation funnel + qual sample**: identify drop-off step in analytics, recruit 3–5 users who bailed at that step, ask what happened.
4. **First-week diary**: structured prompts on day 1, day 3, day 7 for new sign-ups. Captures real-context use.
5. **Time-to-first-value measurement**: how long from first launch to first meaningful action? Track distribution, not just median; tail matters.

### What to specifically test

- Does the first screen communicate value in <5s?
- Is the first action small enough to complete on first try?
- Is the first success visible (haptic, animation, copy)?
- Are permissions deferred until the user has reason to grant them?
- Does the empty state of the home screen on day 2 give the user a reason to come back?

---

## Habit and Retention Research

Habit-forming products require a different research lens than transactional ones. The question is not "did the user complete the task" but "did the user come back."

### Key methods

- **Cohort retention curves with qualitative depth**: not just the curve, but interviews at the inflection points (week 1, week 4, week 12) to understand *why* users stayed or left.
- **Trigger map**: what triggers users to open the app? Sketch the trigger landscape for power users vs casual users vs lapsed users.
- **Habit ladder**: identify the smallest reliable use that signals "this user is forming a habit" (e.g., 3 sessions in 7 days for a meditation app). Optimize for crossing this rung.
- **Lapsed user interview**: 30 min with users who used to be active but stopped. Critical for diagnosing retention killers — they remember what new users haven't yet experienced.
- **Streak / progress UX studies**: A/B + qual on different framings (loss-averse vs gain-oriented vs neutral).

### What to avoid

- Only studying retained users — survivorship bias produces flattering, useless insight.
- Treating retention as a single number — different cohorts retain differently for different reasons.
- Studying the streak feature in isolation — habit forms across the whole product surface, not in one component.
- Using "engagement" as a synonym for "value" — engagement can be addictive without being valuable; that gap is where brand damage hides.

---

## Anti-Patterns

- Treating five usability sessions as a verdict on emotion or delight. They aren't.
- NPS as a launch criterion. NPS is a trend metric.
- Synthetic users for habit research. They cannot model context, social, or temporal forces.
- Asking "what do you want" instead of reconstructing past behavior.
- Skipping competitive benchmarks because "we're different." If a user could choose your competitor, you're not different on that dimension.
- Friction logs done once and shelved. The value compounds across recurring runs.
- Diary studies with too-many prompts. Three short prompts per day max; participants drop out otherwise.
- JTBD interviews with prospects who haven't switched yet. The Switch interview requires recent switchers.
- Onboarding A/B tests without qual companion. The numbers will move; you won't know why.
- Treating the OST as documentation. It is a working surface; if it's not edited weekly, it's a graveyard.

---

## Opportunity Sizing

A finding is incomplete without a size estimate. Frame every opportunity as:

**Frequency × Severity × Segment size = Opportunity**

- **Frequency**: how often does this friction or unmet need occur? Combine qual signal (how often this comes up unprompted in interviews) with analytics signal (how many users encounter the step, flow, or error state).
- **Severity**: how badly does it block or degrade the experience? Use the S1–S4 scale from friction logging.
- **Segment size**: what proportion of users are affected? Cross with retention value of the segment.

Output format: "X% of [segment] hit this friction in [task], blocking [conversion action / retention outcome], severity: [S1–S4]."

Sources: analytics funnel data, friction log, interview frequency count.

**Anti-pattern**: treating opportunity sizing as a precise forecast. It is a directional sort for prioritization, not an ROI model. The goal is to distinguish the top two tiers from the bottom half — not to produce a six-decimal confidence interval.

---

## JTBD Outcome Statements (Ulwick)

Outcome statements capture what users are trying to accomplish in a stable, solution-agnostic form. They are the raw material for opportunity ranking and roadmap goal-setting.

**Format**: [Direction] the [unit of measure] of [object] when [contextual constraint]

**Examples**:
- "Minimize the time it takes to plan a week of meals when balancing dietary preferences across family members"
- "Increase the likelihood of correctly identifying a tax-deductible expense when categorizing receipts at end of quarter"
- "Reduce the number of steps required to share a progress update when working from a mobile device"

**Why outcomes over features**: outcomes are stable across solutions and product generations; features come and go. An outcome statement written today is still valid when the solution has been redesigned three times.

**Use as**:
- Roadmap goalposts: "which solution best improves outcome X for segment Y?"
- A/B success metrics: translate the outcome statement into a measurable proxy
- Opportunity ranking: score current satisfaction × importance to identify highest-yield gaps

**Anti-pattern**: writing outcome statements that smuggle in a solution ("Minimize the time it takes to use the new calendar sync feature"). The statement should hold regardless of which solution is chosen.

---

## Watch Parties and War Rooms

### Watch party

A 60–90 minute session where the squad watches 3–5 user research clips together and discusses immediately. Not a debrief — the viewing and reaction happen in the same session.

- **Preparation**: researcher selects clips in advance, codes severity and theme before the session. Do not let the squad vote on which clips to watch — that reintroduces selection bias.
- **Format**: watch clip, 5 minutes open reaction, researcher moderates toward evidence ("what did you observe?") not speculation ("I bet users think...").
- **Output**: 3–5 shared observations the squad owns, not a research report the researcher owns.
- **Cadence**: weekly during active discovery; monthly during build.

### War room

A dedicated physical or virtual space where research artifacts — clips, friction logs, opportunity tree, current hypothesis — live continuously. Squad members drop in; artifacts are updated in place rather than filed away.

**Anti-pattern**: research as gatekeeping — only the researcher has seen the recordings. The whole product squad should hear real users at least once a month. Watch parties are the minimum viable version of this; war rooms sustain it between cycles.

---

## Researcher Embedding Models

| Model | Strengths | Weaknesses | Best for |
|-------|-----------|------------|----------|
| **Embedded** (1 researcher per 1–2 squads) | Continuous discovery, deep PM/EM relationship, fast turnaround | Narrow focus, capture risk (researcher starts advocating for squad's preferred answers) | Product squads with weekly discovery cadence |
| **Shared / pool** (researchers rotate across squads) | Breadth, cross-product pattern recognition | Shallow squad relationship, hard to run continuous discovery | Platform and infrastructure squads, lower research cadence |
| **Consultancy** (central team, squads request studies) | Depth, methodological rigor, independence | Slowest velocity, squads feel research is external | Executive strategic research, sensitive or compliance-adjacent studies |
| **Hybrid** (most common at scale) | Balances depth and breadth | Coordination overhead | Orgs with 4+ squads; embedded researchers supported by a senior central researcher and pooled ResearchOps coordinator |

**Decision rule**: embedded for product squads running weekly customer interviews; pool for infra/platform squads; consultancy model for executive or strategic research. Hybrid is the default at scale — do not try to make one model work across all squad types.

**Capture risk in embedded models**: an embedded researcher who has been on one squad for 12+ months may start filtering findings to protect relationships. Rotation every 12–18 months and cross-squad calibration sessions are the mitigation.

---

## Sources

- [Teresa Torres — Continuous Discovery Habits](https://www.producttalk.org/)
- [Bob Moesta — Demand-Side Sales 101 (JTBD)](https://www.rewiredgroup.com/)
- [NN/g — Diary studies article](https://www.nngroup.com/articles/diary-studies/)
- [NN/g — UX scoring & metrics](https://www.nngroup.com/articles/measuring-ux-scoring/)
- [Pieter Desmet — PrEmo](https://emotiontypology.com/)
- [Hassenzahl — AttrakDiff](https://attrakdiff.de/)
- [Sean Ellis — PMF survey](https://www.startup-marketing.com/the-startup-pyramid/)
- [Microsoft Desirability Toolkit](https://www.microsoft.com/en-us/research/publication/measuring-desirability-new-methods-for-evaluating-desirability-in-a-usability-lab-setting/)
- [Refactoring UI — Adam Wathan, Steve Schoger](https://www.refactoringui.com/)
- [Hooked — Nir Eyal](https://www.nirandfar.com/hooked/)
- [The Mom Test — Rob Fitzpatrick](https://www.momtestbook.com/)
