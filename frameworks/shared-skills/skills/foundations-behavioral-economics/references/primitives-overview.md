---
description: Domain-agnostic overview of 16 behavioral-economics primitives. For consumer applied recipes, see downstream consumer skills (marketing-cro, startup-business-models, product-management, marketing-content-strategy, marketing-paid-advertising).
last_verified: 2026-05-17
status: stable
---

# Behavioral Economics Primitives Overview

## Table of Contents

- [Why Choice Architecture Matters](#why-choice-architecture-matters)
- [The Ethical Frame](#the-ethical-frame)
- [Primitive Index](#primitive-index)
- [Anti-Patterns by Domain](#anti-patterns-by-domain)
- [Decision Checklist](#decision-checklist)
- [Sources](#sources)

---

## Why Choice Architecture Matters

Every product, pricing page, and onboarding flow is a choice architecture. Neutrality is impossible — every design decision privileges some options over others. The question is not whether to influence, but whether to influence deliberately and ethically.

Without intentional behavioral design:

| Failure Mode | Behavioral Diagnosis | What Goes Wrong |
|-------------|----------------------|-----------------|
| Pricing page has no anchor | Users import an external reference (competitor price, expectation) that you don't control | Willingness to pay is set by whoever anchors first |
| All plan options are visually equal | No asymmetric dominance; user defaults to cheapest | Revenue per customer is lower than it could be |
| Opt-in requires active effort | Default-bias means most users never complete opt-in | Feature adoption or consent rates are suppressed |
| No urgency signal on limited offer | Present bias: users defer indefinitely | Conversion window is lost |
| Long copy aimed at rational evaluation | System 1 governs most quick decisions | Rational arguments are ignored; emotional cues determine action |

Each primitive in this skill addresses a specific decision failure. Each also carries a misuse boundary — the flip side of every behavioral lever is the potential to exploit rather than help.

---

## The Ethical Frame

Behavioral economics describes how humans actually decide, not how they ideally would. That makes it powerful and dangerous.

The Thaler-Sunstein harm test (from _Nudge_, 2008):

> A choice architecture is a nudge if it steers people toward choices they would endorse upon reflection, can be easily overridden, and does not exploit cognitive limitations against the user's interests.

Every primitive in this skill is annotated with a "Misuse boundary" that states the specific manipulation risk and the condition for ethical use. The boundary is not a disclaimer — it is a gate that must be passed before the technique is applied.

---

## Primitive Index

16 primitives, each with a full playbook under [`../assets/templates/behavioral-economics/`](../assets/templates/behavioral-economics/). Primitives 1–11 cover decision-time effects (framing, anchoring, choice). Primitives 12–16 cover repetition-time effects (habit formation, reinforcement, working memory, contextual retrieval, planned action).

| # | Primitive | Behavioral Mechanism | Primary Domains |
|---|-----------|---------------------|-----------------|
| 1 | [Prospect Theory](../assets/templates/behavioral-economics/01-prospect-theory.md) | S-shaped value function; losses and gains weighted asymmetrically | Pricing, offers, upgrade copy, loss/gain framing |
| 2 | [Loss Aversion](../assets/templates/behavioral-economics/02-loss-aversion.md) | Losses ~2× as powerful as equivalent gains (range ~1.3–2.0×; 2.25 is an upper bound) | Churn prevention, trial expiry, downgrade warnings |
| 3 | [Anchoring](../assets/templates/behavioral-economics/03-anchoring.md) | First number seen distorts all subsequent numerical judgments | Pricing pages, discount display, negotiation setup |
| 4 | [Defaults](../assets/templates/behavioral-economics/04-defaults.md) | Strong bias toward pre-set options; inertia favors the status quo | Onboarding, plan pre-selection, consent flows |
| 5 | [Social Proof](../assets/templates/behavioral-economics/05-social-proof.md) | Uncertainty resolved by observing others' choices | Trust signals, sign-up pages, review placement |
| 6 | [Scarcity](../assets/templates/behavioral-economics/06-scarcity.md) | Perceived value rises with limited availability | Inventory counts, time-limited pricing, waitlists |
| 7 | [Hyperbolic Discounting](../assets/templates/behavioral-economics/07-hyperbolic-discounting.md) | Present is disproportionately preferred; β-δ quasi-hyperbolic model | Trial design, annual vs monthly framing, commitment devices |
| 8 | [Mental Accounting](../assets/templates/behavioral-economics/08-mental-accounting.md) | Money in different mental accounts is treated differently | Bundling, sunk-cost effects, price framing as daily rate |
| 9 | [Choice Architecture](../assets/templates/behavioral-economics/09-choice-architecture.md) | Presentation order, grouping, and defaults alter selection | Menus, onboarding flows, option set design |
| 10 | [Dual-System Cognition](../assets/templates/behavioral-economics/10-dual-system.md) | System 1 (automatic, emotional) vs System 2 (deliberate, rational) | Copy tone, CTA complexity, trust signal placement |
| 11 | [Decoy Effect](../assets/templates/behavioral-economics/11-decoy-effect-asymmetric-dominance.md) | Asymmetrically dominated option shifts preference toward its dominator | Pricing tier design, subscription plan comparison |
| 12 | [Habit Loop](../assets/templates/behavioral-economics/12-habit-loop.md) | Cue → routine → reward; basal-ganglia stimulus-response system takes over from goal-directed control | Daily/recurring usage, retention beyond week 4, durable behavior change |
| 13 | [Reinforcement Schedules](../assets/templates/behavioral-economics/13-reinforcement-schedules.md) | Schedule type (FR/VR/FI/VI), not just reward, governs acquisition and resistance to extinction | Streaks, rewards, gamification, reactivation; auditing existing reward systems |
| 14 | [Cognitive Load & Working Memory](../assets/templates/behavioral-economics/14-cognitive-load-working-memory.md) | Working memory ~4 novel chunks; extraneous load suppresses informed choice | Forms, dashboards, alerts, consent flows, onboarding step count |
| 15 | [Context-Dependent Retrieval](../assets/templates/behavioral-economics/15-context-dependent-retrieval.md) | Encoding specificity; behaviors bound to cues present at learning collapse when context shifts | Migrations, redesigns, cross-surface continuity, dormant-user reactivation |
| 16 | [Implementation Intentions](../assets/templates/behavioral-economics/16-implementation-intentions.md) | User-authored if-then plans bind a specific cue to a specific response, doubling/tripling completion rates | Goal-pursuit features, onboarding into habit-forming behavior, transition-state re-anchoring |

---

## Anti-Patterns by Domain

### Pricing and Packaging

| Anti-Pattern | Behavioral Diagnosis | Fix |
|-------------|----------------------|-----|
| No anchor on pricing page | User imports external reference you don't control | Set a high anchor (enterprise tier, original price) before showing target price |
| Two equal-looking options | No asymmetric dominance; cheapest wins by default | Add a third option that makes the target tier dominant on the key dimension |
| Loss framing on a gain the user hasn't considered | Manufactured anxiety without real value stake | Only use loss framing when the loss is real and relevant to the user's stated goals |

### Onboarding and Defaults

| Anti-Pattern | Behavioral Diagnosis | Fix |
|-------------|----------------------|-----|
| Opt-in requires 4 steps | Default-bias suppresses adoption | Pre-select the best option; require action only to opt out |
| No recommended path | Choice paralysis | Reduce options; add "Most teams start here" guidance |
| Default to data collection without disclosure | Dark pattern; fails harm test | Default must be transparently disclosed and easily overridden |

### Social Proof and Scarcity

| Anti-Pattern | Behavioral Diagnosis | Fix |
|-------------|----------------------|-----|
| Fake countdown timer | Manufactured scarcity | Only display real constraints; reset or remove timer when offer ends |
| "Thousands trust us" at 50 users | Fabricated social proof | Use accurate, specific numbers; specificity is more credible than inflation |
| Review cherry-picking | Biased social proof | Show average rating and distribution, not only five-star quotes |

---

## Decision Checklist

For any choice-design problem, run through these questions before selecting primitives:

- [ ] **What is the decision the user is making?** (purchase, opt-in, cancel, upgrade, select plan)
- [ ] **What is the default state?** Does doing nothing lead to a good or bad outcome for the user?
- [ ] **What reference point does the user bring?** What anchor already exists? Can you set a better one?
- [ ] **Is there real scarcity or urgency?** Would displaying it be accurate?
- [ ] **What social context exists?** What are comparable users doing? Can this be shown accurately?
- [ ] **Is the decision path cognitively expensive?** Is System 2 engagement realistic? Or is System 1 governing?
- [ ] **What would the user lose by not acting?** Is the loss real and relevant?
- [ ] **How many options are presented?** Is the set constrained enough? Is guidance provided?
- [ ] **Does each technique pass the harm test?** Would disclosure embarrass the team?

---

## Sources

Primary papers are the strongest evidence tier. Effect sizes cited in primitives should be treated as empirical anchors for your population, not universal constants — replicate on your own users before optimizing for a specific coefficient.

- Kahneman, D. & Tversky, A. (1979). Prospect theory: An analysis of decision under risk. _Econometrica_, 47(2), 263–292.
- Tversky, A. & Kahneman, D. (1981). The framing of decisions and the psychology of choice. _Science_, 211(4481), 453–458.
- Thaler, R. H. & Sunstein, C. R. (2008). _Nudge: Improving Decisions About Health, Wealth, and Happiness_. Yale University Press.
- Kahneman, D. (2011). _Thinking, Fast and Slow_. Farrar, Straus and Giroux.
- Ariely, D. (2008). _Predictably Irrational_. HarperCollins.
- Cialdini, R. B. (1984). _Influence: The Psychology of Persuasion_. HarperCollins.
- Loewenstein, G. & Prelec, D. (1991). Negative time preference. _American Economic Review_, 81(2), 347–352.
- Frederick, S., Loewenstein, G. & O'Donoghue, T. (2002). Time discounting and time preference: A critical review. _Journal of Economic Literature_, 40(2), 351–401.
- Thaler, R. H. (1985). Mental accounting and consumer choice. _Marketing Science_, 4(3), 199–214.
- Simonson, I. (1989). Choice based on reasons: The case of attraction and compromise effects. _Journal of Consumer Research_, 16(2), 158–174.
- Tversky, A. & Simonson, I. (1993). Context-dependent preferences. _Management Science_, 39(10), 1179–1189.
