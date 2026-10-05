# Prioritization Frameworks

Detailed patterns for prioritizing features, initiatives, and deciding what to stop.

---
## Table of Contents

- [Kano Model (Pre-Filter)](#kano-model-pre-filter)
- [RICE Scoring](#rice-scoring)
- [Worked Example](#worked-example)
- [RICE Anti-Patterns](#rice-anti-patterns)
- [RICE Precision Theatre (What a Sharp CPO Catches)](#rice-precision-theatre-what-a-sharp-cpo-catches)
- [ICE Scoring](#ice-scoring)
- [Opportunity Scoring (JTBD-Aligned)](#opportunity-scoring-jtbd-aligned)
- [Cost of Delay](#cost-of-delay)
- [WSJF (Weighted Shortest Job First)](#wsjf-weighted-shortest-job-first)
- [Strategic Bets vs Tactical Backlog](#strategic-bets-vs-tactical-backlog)
- [Reversible vs Irreversible (Asymmetric Cost-of-Being-Wrong)](#reversible-vs-irreversible-asymmetric-cost-of-being-wrong)
- [Scope Negotiation Scripts](#scope-negotiation-scripts)
- ["Can we add X?"](#can-we-add-x)
- ["This is a must-have"](#this-is-a-must-have)
- ["The competitor has this"](#the-competitor-has-this)
- ["Everything is priority 1"](#everything-is-priority-1)
- [Kill Decision Framework](#kill-decision-framework)
- [Pre-Define Kill Criteria (Before Starting)](#pre-define-kill-criteria-before-starting)
- [Kill Decision Meeting](#kill-decision-meeting)
- [What Makes Killing Hard (and How to Handle It)](#what-makes-killing-hard-and-how-to-handle-it)


## Kano Model (Pre-Filter)

Use Kano to classify features before applying RICE. It separates table-stakes work from differentiation work, preventing quantitative scoring from burying must-haves below high-scoring delighters.

| Category | Definition | Implication |
|----------|------------|-------------|
| Basic / Must-be | Absence causes dissatisfaction; presence is expected, not appreciated | Do regardless of RICE score — these are table stakes |
| Performance / Linear | More is better; satisfaction scales with quality or quantity | Score with RICE to sequence investment level |
| Delighter / Excitement | Unexpected; drives differentiation and delight when present | Highest leverage for differentiation — protect in RICE sequencing |
| Indifferent | Users neither satisfied nor dissatisfied | Deprioritize unless very low cost |
| Reverse | Presence causes dissatisfaction for some segments | Segment carefully; do not build for average user |

**How to classify**: Use the functional/dysfunctional question pair. For each feature, ask:
1. Functional: "How do you feel if this feature is present?" (I like it / I expect it / I'm neutral / I can tolerate it / I dislike it)
2. Dysfunctional: "How do you feel if this feature is absent?"

The combination of answers maps to a Kano category. This survey must be run on actual users — the team cannot self-classify.

**Application rule**: Must-be features bypass the ranked list and are budgeted separately. Delighters compete in RICE. Do not mix Kano categories in a single ranked stack.

**When to use**: Product discovery, new market entry, identifying where investment drives loyalty vs. where it is invisible to users.

**Limitation**: Kano categories shift over time. Delighters become Performance, then Must-be as market expectations rise. Re-run the survey annually or after significant competitive moves.

---

## RICE Scoring

**Formula**: (Reach x Impact x Confidence) / Effort

| Factor | How to Estimate | Scale |
|--------|----------------|-------|
| Reach | Number of users/customers affected per quarter | Absolute number |
| Impact | How much this moves the target metric per user | 3 = massive, 2 = high, 1 = medium, 0.5 = low, 0.25 = minimal |
| Confidence | How confident are you in reach and impact estimates | 100% = high, 80% = medium, 50% = low |
| Effort | Person-weeks (or person-days for small items) | Absolute number |

Use this Impact scale consistently across the toolkit (3=massive, 2=high, 1=medium, 0.5=low, 0.25=minimal).

### Worked Example

| Initiative | Reach | Impact | Confidence | Effort | RICE Score |
|-----------|-------|--------|------------|--------|------------|
| Onboarding redesign | 500 new users/qtr | 2 (high) | 80% | 4 weeks | 200 |
| Export to CSV | 100 users/qtr | 1 (medium) | 100% | 0.5 weeks | 200 |
| AI-powered search | 300 users/qtr | 3 (massive) | 50% | 8 weeks | 56 |

**Interpretation**: Onboarding redesign and CSV export score equally. CSV export is faster to validate — ship it first, then start onboarding redesign.

### RICE Anti-Patterns
- Gaming confidence to 100% on pet projects
- Estimating reach based on total users instead of affected users
- Not updating scores after new information
- Using RICE for strategic bets (use cost-of-delay or opportunity scoring instead)

### RICE Precision Theatre (What a Sharp CPO Catches)

RICE produces a number with two decimal places from inputs that are frequently guesses. That precision is fake, and a checklist run of the formula will not catch it — only judgment does. Tells that a RICE stack is precision theatre rather than a real prioritization signal:

- **The ranking never changes.** If the same items are always on top quarter after quarter, the team is scoring to justify a pre-existing roadmap, not to discover priority.
- **Reach and Impact are point estimates with no range.** A single number ("Reach = 500") hides whether the real range is 200-2,000. When the range is wide, the RICE score is noise dressed as signal — say so instead of ranking on it.
- **Effort is systematically underestimated for favored work and inflated for disfavored work.** Compare estimated vs. actual effort after delivery; if favored initiatives are consistently underestimated, the scoring process itself is biased.
- **Two items score identically and the tie is broken by seniority in the room, not by re-examining the inputs** (contrast with the worked example above, where the tie is broken by evidence: which item validates learning fastest).
- **RICE is applied to a decision that is actually reversible-vs-irreversible, not comparable-scope.** See [Strategic Bets vs Tactical Backlog](#strategic-bets-vs-tactical-backlog) — scoring a zero-to-one bet against a tactical backlog item on the same RICE stack is the single most common misuse of the framework, because Effort and Reach denominators structurally penalize anything new and unproven.

**The judgment RICE cannot supply**: whether an initiative is even the right *kind* of decision to score numerically. Use RICE to sequence comparable, validated, similarly-scoped work. Use it to force explicit trade-off conversation, not to outsource the decision. If a stakeholder cites the RICE score as the reason a decision is final, that is a sign the tool has replaced judgment rather than informed it — reopen the conversation on the underlying evidence, not the arithmetic.

---

## ICE Scoring

**Formula**: Impact x Confidence x Ease

Simpler than RICE. Good for quick gut-check sessions.

| Factor | Scale | Description |
|--------|-------|-------------|
| Impact | 1-10 | How much this moves the target metric |
| Confidence | 1-10 | How sure you are about impact and feasibility |
| Ease | 1-10 | How easy to implement (10 = trivial, 1 = massive effort) |

**When to use**: Fast prioritization in a team session. Not rigorous enough for board-level decisions.

---

## Opportunity Scoring (JTBD-Aligned)

**Formula**: Importance + (Importance - Satisfaction)

Based on Tony Ulwick's Outcome-Driven Innovation (ODI) and jobs-to-be-done.

| Step | Action |
|------|--------|
| 1 | List the outcomes (jobs) users are trying to achieve |
| 2 | Survey users: rate importance (1-10) and satisfaction (1-10) for each |
| 3 | Calculate opportunity score: Importance + max(Importance - Satisfaction, 0) |
| 4 | High importance + low satisfaction = underserved opportunity |

**When to use**: Discovery-driven prioritization. Requires user research data.

---

## Cost of Delay

**Formula**: Value per unit time / Duration

| Type | Pattern | Example |
|------|---------|---------|
| Standard | Linear value over time | Feature that saves $10K/month — every month delayed costs $10K |
| Urgent | Decaying value (window closing) | Seasonal feature, competitive response, compliance deadline |
| Fixed date | Binary (value drops to zero after date) | Conference demo, regulatory deadline, contract requirement |

**When to use**: Time-sensitive decisions. Forces the question: "What does it cost us to NOT do this now?"

---

## WSJF (Weighted Shortest Job First)

**Formula**: WSJF = Cost of Delay / Job Size (Duration)

Cost of Delay has three components:

| Component | Description | Example |
|-----------|-------------|---------|
| User / Business Value | How much value does this deliver to users and the business? | Revenue impact, activation, retention |
| Time Criticality | Does value decay or is there a closing window? | Compliance deadline, seasonal demand, competitive response |
| Risk Reduction / Opportunity Enablement | Does this unlock future work or reduce a known risk? | Architectural dependency, regulatory exposure, platform bloat |

**Scoring**: Use a modified Fibonacci scale (1, 2, 3, 5, 8, 13) for each component and for Job Size. Score relative to other items in the backlog — do not attempt absolute dollar values.

**Formula expanded**: WSJF = (User/Business Value + Time Criticality + Risk Reduction/Opportunity Enablement) / Job Size

### Worked Example

| Initiative | User/Biz Value | Time Criticality | Risk Reduction | Cost of Delay | Job Size | WSJF |
|-----------|---------------|-----------------|----------------|---------------|----------|------|
| Compliance reporting | 5 | 13 | 8 | 26 | 3 | 8.7 |
| Mobile search redesign | 8 | 3 | 2 | 13 | 5 | 2.6 |
| API rate limiting | 3 | 5 | 13 | 21 | 2 | 10.5 |
| Onboarding wizard | 8 | 2 | 1 | 11 | 8 | 1.4 |

**Interpretation**: API rate limiting scores highest — high risk-reduction value, small job, moderate time pressure. Compliance reporting is second. Onboarding wizard has high business value but a large job and low urgency — schedule for a dedicated capacity window.

**When to use**: Scaled-agile (SAFe) teams, flow-constrained backlogs, sequencing under shared team capacity limits, large programs with interdependent work items.

**When NOT to use**: Comparing strategic zero-to-one bets against tactical backlog items. WSJF assumes comparable scope and continuous delivery flow. Scoring a platform rebuild against a bug fix produces arbitrary outputs. See [Strategic Bets vs Tactical Backlog](#strategic-bets-vs-tactical-backlog).

---

## Strategic Bets vs Tactical Backlog

RICE and WSJF were designed to rank comparable-scope items within a product area. Mixing a zero-to-one platform bet against a retention bug fix in the same ranked list produces absurd outputs — the bet loses on Effort and Reach denominators even when it is strategically essential.

**Rule**: Separate the backlog into two pools before scoring.

| Pool | Definition | How to prioritize |
|------|------------|-------------------|
| Strategic Bets | Cross-functional platform work, new market entry, zero-to-one bets, multi-quarter architectural changes | Conviction, opportunity size, strategic fit — funded as a portfolio allocation (e.g., a fixed % of total capacity) |
| Tactical Backlog | Feature additions, improvements, bug fixes, optimizations within an existing product area | RICE or WSJF |

Do not mix pools in a single ranked list. Fund each pool independently, then sequence within each pool.

**Portfolio allocation**: Allocate capacity to the strategic pool as a percentage decision (e.g., 20% of engineering on bets, 80% on tactical backlog). Revisit the allocation quarterly at the strategic roadmap review — not item by item.

**Bet evaluation criteria** (apply to the strategic pool instead of RICE):
- Conviction: How strong is the evidence this problem is real and large?
- Opportunity size: What is the revenue or user impact ceiling if the bet works?
- Strategic fit: Does this extend or deepen the core value proposition?
- Reversibility: Can the bet be cut within two quarters if evidence turns negative?

---

## Reversible vs Irreversible (Asymmetric Cost-of-Being-Wrong)

Bezos's one-way vs two-way door framing: not all decisions carry equal cost when wrong.

| Decision type | Definition | Decision standard |
|--------------|------------|-------------------|
| Reversible (two-way door) | Can be undone within days or a sprint at low cost | Bias to action; low evidence bar; move fast |
| Irreversible (one-way door) | Difficult or expensive to undo — data model changes, public API contracts, org restructures, vendor lock-in | High evidence bar; explicit kill/rollback criteria before starting; do not equate expected value with downside risk |

**Application to prioritization**: When sequencing irreversible bets, weight by downside risk, not just expected value. A reversible wrong decision costs one sprint. An irreversible wrong decision can cost quarters and foreclose options.

**Checklist for irreversible items** (complete before scheduling):
- [ ] Kill criteria defined: what signals would cause us to stop?
- [ ] Rollback path described: how do we undo this if we need to?
- [ ] Downside scenario documented: what is the worst case if this fails?
- [ ] Evidence threshold agreed: what must be true before we proceed?

---

## Scope Negotiation Scripts

### "Can we add X?"

> "We can add X. Here's the trade-off: it would push back [existing item] by [time]. Is X more important than [existing item]? If so, let's swap. If not, let's add X to the backlog for next quarter."

### "This is a must-have"

> "I hear you — let me understand the outcome you're trying to achieve. [Listen.] Got it. We could solve that with [smaller scope option] in [shorter time]. Would that achieve 80% of the value? If so, let's start there and iterate."

### "The competitor has this"

> "They do. The question is whether our customers are choosing them because of this feature, or despite not having it. Let me check win/loss data and talk to 3 customers. If it's a real decision driver, we'll prioritize it."

### "Everything is priority 1"

> "If everything is priority 1, nothing is. Let's force-rank the top 5. Which one would you ship if you could only ship one this quarter? That's priority 1."

---

## Kill Decision Framework

### Pre-Define Kill Criteria (Before Starting)

For every initiative, document:
1. **Usage threshold**: Minimum adoption within a defined window
2. **Cost ceiling**: Maximum investment before mandatory review
3. **Time limit**: Ship-or-kill deadline
4. **Metric guardrail**: Metrics that must not degrade

### Kill Decision Meeting

Run quarterly. For each initiative past its evaluation window:
1. Review pre-defined kill criteria vs actuals
2. Three options: **Continue** (criteria met), **Pivot** (partial signal, change approach), **Kill** (criteria missed, no pivot path)
3. Document the decision and reasoning
4. Communicate to stakeholders

### What Makes Killing Hard (and How to Handle It)
- **Sunk cost fallacy**: "We already invested X." → Reframe: "Would we start this today knowing what we know?"
- **Political cost**: "Stakeholder Y pushed for this." → Reframe: "We learned [what]. Here's what we're doing instead."
- **Emotional attachment**: "The team worked hard." → Acknowledge the work, redirect the energy.
