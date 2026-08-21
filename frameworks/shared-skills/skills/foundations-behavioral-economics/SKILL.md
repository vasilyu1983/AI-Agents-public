---
name: foundations-behavioral-economics
description: "16 behavioral-economics primitives for ethical pricing, choice design, and retention. Use when framing, defaults, habits, dark patterns, AI-agent nudging, or nudge ethics apply."
compatibility: Portable core only.
version: "1.2"
last_validated: 2026-08-14
---

# Behavioral Economics Foundations


16 canonical behavioral-economics and behavior-design primitives for product, pricing, choice design, and retention. Each primitive is domain-agnostic and ethically bounded. Primitives 1–11 cover decision-time effects (framing, anchoring, choice). Primitives 12–16 cover repetition-time effects (habit formation, reinforcement, working memory, contextual retrieval, planned action) — the canonical mechanisms behind retention, behavior change, and the "neuroscience of product" claims commonly made without mechanism. Consumer applied recipes (CRO, business models, content strategy, product management, paid advertising) are the downstream layer — these primitives are the upstream canon.

**Ethical obligation**: every primitive in this skill is a tool for understanding and influencing human decision-making. Each has a "Misuse boundary" subsection. Read it before applying any technique. The test from Thaler and Sunstein: "Would you be embarrassed if the technique appeared on the front page of a newspaper?" If yes, it is a dark pattern, not a nudge.

## When to Apply

**Apply behavioral-economics when:**
- User-facing decision surface — pricing page, onboarding default, churn flow, retention nudge
- Habit-formation or cue-preservation in redesigns
- Loss-aversion / framing matters and downside is concrete
- Choice architecture — defaults, decoys, ordering, anchoring
- Conversion or activation experiment design where biases are exploitable ethically

**Skip and use simpler alternatives when:**
- Decision is between two AI systems or backend strategies (no human in the loop) — use foundations-decision-theory
- Causal "did the nudge work?" question — use foundations-causal-inference to measure
- Strategic multi-actor pricing — use foundations-game-theory (Bertrand, Vickrey)
- The proposed pattern requires deceiving the user about real value — fails the ethical gate; redesign, don't nudge
- Audience or market context is unknown — biases are not universal; lift bands won't generalise
- Lift required > 30% — behavioral nudges rarely deliver that; the underlying offer/value-prop is the problem, not framing

## Contents

- [Quick Reference](#quick-reference)
- [Primitive Index](#primitive-index)
- [Formal Supporting Theory](#formal-supporting-theory)
- [Ethical Bounds](#ethical-bounds)
- [Expert Judgment: Reading Evidence Strength](#expert-judgment-reading-evidence-strength)
- [Misuse Boundaries](#misuse-boundaries)
- [Decision Checklist](#decision-checklist)
- [Anti-Patterns](#anti-patterns)
- [Composition Recipes](#composition-recipes) (Recipes 1–6, including AI-assistant UX guardrails)
- [Workflow](#workflow)
- [ASCII Flow](#ascii-flow)
- [Related Skills](#related-skills)
- [Fact-Checking](#fact-checking)

---

## Quick Reference

| # | Primitive | Core Effect | When to Use |
|---|-----------|-------------|-------------|
| 1 | [Prospect Theory](assets/templates/behavioral-economics/01-prospect-theory.md) | Gains and losses are not mirror images; framing shifts choice | Pricing copy, offer framing, upgrade messaging |
| 2 | [Loss Aversion](assets/templates/behavioral-economics/02-loss-aversion.md) | Losses hurt approximately 2× more than equivalent gains feel good (meta-analytic range: ~1.3–2.0×; canonical λ ≈ 2.25 is an upper-bound estimate) | Churn prevention, trial expiry, feature removal messaging |
| 3 | [Anchoring](assets/templates/behavioral-economics/03-anchoring.md) | First number shown distorts all subsequent judgments | Pricing pages, salary negotiation, discount presentation |
| 4 | [Defaults](assets/templates/behavioral-economics/04-defaults.md) | People disproportionately stick with pre-set options | Onboarding, opt-in/out choices, plan pre-selection |
| 5 | [Social Proof](assets/templates/behavioral-economics/05-social-proof.md) | People infer correct action from others' behavior | Sign-up pages, review placement, usage statistics |
| 6 | [Scarcity](assets/templates/behavioral-economics/06-scarcity.md) | Limited availability increases perceived value | Inventory counts, time-limited offers, waitlists |
| 7 | [Hyperbolic Discounting](assets/templates/behavioral-economics/07-hyperbolic-discounting.md) | Present bias: immediate rewards are disproportionately preferred | Free trials, commitment devices, annual vs monthly pricing |
| 8 | [Mental Accounting](assets/templates/behavioral-economics/08-mental-accounting.md) | People categorize money differently depending on source and label | Bundling, gift cards, credit framing, sunk-cost effects |
| 9 | [Choice Architecture](assets/templates/behavioral-economics/09-choice-architecture.md) | How choices are presented alters which option is selected | Option ordering, menu design, default pre-selection |
| 10 | [Dual-System Cognition](assets/templates/behavioral-economics/10-dual-system.md) | System 1 (fast, automatic) vs System 2 (slow, deliberate) governs which influences work | Copy tone, complexity of CTA, trust signals |
| 11 | [Decoy Effect / Asymmetric Dominance](assets/templates/behavioral-economics/11-decoy-effect-asymmetric-dominance.md) | A dominated option shifts preference toward its dominator | Pricing tier design, plan comparison tables |
| 12 | [Habit Loop](assets/templates/behavioral-economics/12-habit-loop.md) | Stable cue → routine → reward becomes automatic via the basal-ganglia stimulus-response system | Daily/recurring usage, retention beyond week 4, durable behavior change |
| 13 | [Reinforcement Schedules](assets/templates/behavioral-economics/13-reinforcement-schedules.md) | Schedule (FR/VR/FI/VI), not just reward, governs acquisition and resistance to extinction | Streaks, rewards, gamification, reactivation; auditing existing reward systems |
| 14 | [Cognitive Load & Working Memory](assets/templates/behavioral-economics/14-cognitive-load-working-memory.md) | Working memory holds ~4 novel chunks; extraneous load suppresses informed choice | Forms, dashboards, alerts, error displays, consent flows, onboarding step count |
| 15 | [Context-Dependent Retrieval](assets/templates/behavioral-economics/15-context-dependent-retrieval.md) | Behaviors are bound to the cues present at encoding; performance collapses when context shifts | Migrations, redesigns, cross-surface continuity, dormant-user reactivation |
| 16 | [Implementation Intentions](assets/templates/behavioral-economics/16-implementation-intentions.md) | User-authored if-then plans bind a specific cue to a specific response, doubling/tripling completion | Goal-pursuit features, onboarding into habit-forming behavior, transition-state re-anchoring |

---

## Primitive Index

Each primitive has a full playbook: Definition / When to use / Misuse boundary / Inputs / Outputs / Failure modes / Worked example / Sources.

| # | Primitive | Failure Mode It Addresses |
|---|-----------|--------------------------|
| 1 | [Prospect Theory](assets/templates/behavioral-economics/01-prospect-theory.md) | Treating gains and losses as symmetric — missing framing leverage |
| 2 | [Loss Aversion](assets/templates/behavioral-economics/02-loss-aversion.md) | Relying only on positive messaging when preventing loss is more motivating |
| 3 | [Anchoring](assets/templates/behavioral-economics/03-anchoring.md) | Presenting price without context, letting the user anchor on a competitor's number |
| 4 | [Defaults](assets/templates/behavioral-economics/04-defaults.md) | Designing opt-in flows that require active effort, suppressing adoption |
| 5 | [Social Proof](assets/templates/behavioral-economics/05-social-proof.md) | Empty or invisible proof signals that fail to reduce uncertainty |
| 6 | [Scarcity](assets/templates/behavioral-economics/06-scarcity.md) | No urgency signal, leading to indefinite deferral of purchase |
| 7 | [Hyperbolic Discounting](assets/templates/behavioral-economics/07-hyperbolic-discounting.md) | Annual plan presented without present-bias mitigation, losing to monthly default |
| 8 | [Mental Accounting](assets/templates/behavioral-economics/08-mental-accounting.md) | Price presented as a lump sum when installment framing changes perceived size |
| 9 | [Choice Architecture](assets/templates/behavioral-economics/09-choice-architecture.md) | Option overload or unguided menus producing decision paralysis |
| 10 | [Dual-System Cognition](assets/templates/behavioral-economics/10-dual-system.md) | Rational copy aimed at System 2 when System 1 is the actual decision path |
| 11 | [Decoy Effect](assets/templates/behavioral-economics/11-decoy-effect-asymmetric-dominance.md) | Two-option pricing leaving users without a reference point to prefer either |
| 12 | [Habit Loop](assets/templates/behavioral-economics/12-habit-loop.md) | Strong week-1 engagement that collapses by week 4 — motivation carried it; no cue-bound habit ever formed |
| 13 | [Reinforcement Schedules](assets/templates/behavioral-economics/13-reinforcement-schedules.md) | Reward system that worked at launch then went dead — continuous reinforcement extinguished once predictable |
| 14 | [Cognitive Load & Working Memory](assets/templates/behavioral-economics/14-cognitive-load-working-memory.md) | High abandonment mid-flow because the screen exceeds working-memory capacity for the user's expertise level |
| 15 | [Context-Dependent Retrieval](assets/templates/behavioral-economics/15-context-dependent-retrieval.md) | Redesign or migration broke retention even though features didn't change — the cue surface that triggered behavior moved |
| 16 | [Implementation Intentions](assets/templates/behavioral-economics/16-implementation-intentions.md) | Feature reminders are ignored because no cue→response binding was ever authored — generic reminders are not implementation intentions |

---

## Formal Supporting Theory

| Theory Area | Use When | Applied Primitives It Grounds |
|---|---|---|
| Descriptive choice under risk | Need to predict actual gain/loss choices, not prescribe rational choice | #1, #2 |
| Heuristics and biases | Need to explain fast judgment errors under uncertainty | #3, #10 |
| Libertarian paternalism and nudge theory | Need ethical choice architecture with opt-out | #4, #9 |
| Social influence and norms | Need trust, conformity, or proof signals | #5 |
| Scarcity and reactance | Need to distinguish real constraints from manufactured urgency | #6 |
| Intertemporal choice | Need present-bias, procrastination, or commitment-device design | #7 |
| Behavioral finance and accounting | Need account labels, sunk costs, or budget framing | #8 |
| Context-dependent preferences | Need option-set effects, compromise, or asymmetric dominance | #9, #11 |
| Dual-system habit theory (goal-directed vs stimulus-response) | Need durable behavior beyond motivation; designing for retention and automaticity | #12, #15 |
| Operant conditioning and reinforcement learning (Skinner; dopamine prediction error) | Need to choose or audit a reward schedule; diagnosing extinction or compulsion | #13 |
| Cognitive load theory and working-memory capacity | Need to fit a task into capacity; auditing forms, alerts, or consent flows for overload | #14 |
| Encoding specificity and context-dependent memory | Need behaviors to survive context change (migrations, cross-surface, reactivation) | #15 |
| Goal-pursuit and self-regulation (implementation intentions; if-then planning) | Need to bridge stated intent to action when a habit hasn't yet formed | #16 |

Use [`references/formal-theory-map.md`](references/formal-theory-map.md) when the task needs source assumptions, ethical boundaries, or a distinction between observed behavior and normative decision quality.

---

## Ethical Bounds

### The Harm Test (Thaler & Sunstein)

A nudge is legitimate if it:

1. Steers people toward choices they would endorse on reflection.
2. Can be easily overridden or opted out of.
3. Does not exploit cognitive limitations to work against the user's interests.

A dark pattern fails one or more of these. The same psychological lever — scarcity, defaults, loss framing — can be a nudge or a dark pattern depending on whether the underlying offer is good for the user.

### Dark Patterns vs Nudges

| Dimension | Nudge | Dark Pattern |
|-----------|-------|--------------|
| Transparency | Can be disclosed without changing its effect | Requires concealment to work |
| User benefit | Steers toward user's own goals | Overrides user's goals in favor of operator's |
| Reversibility | Easy to undo or override | Designed to make undoing difficult |
| Honest signal | Scarcity / proof / urgency is real | Signal is fabricated |
| Regulatory posture | Survives ASA/FTC/CMA scrutiny | Attracts regulatory action |

### Per-Primitive Ethical Notes

Every primitive in this skill carries an explicit "Misuse boundary" subsection that states the specific manipulation risk for that technique and the required condition for ethical use. These are non-negotiable gates, not optional guidelines.

### AI Agents as Decision Subjects

When LLMs or AI agents make decisions on behalf of users (shopping, booking, form completion), choice architecture manipulations apply to the agent, not the human — and with dramatically larger effect sizes. Under a default-option nudge, human choice probability shifted from 0.51 (no nudge) to 0.88 (+37pp); several LLMs (GPT-4o, Claude 3 Haiku, o3-Mini, GPT-3.5-Turbo) shifted to ~1.0 from baselines of 0.33–0.58 — a larger jump than humans, though Claude 3.5 Sonnet and Gemini 1.5 Pro stayed close to human levels (~0.89–0.91). The pattern held for suggested alternatives and information highlighting too (Cherep et al., "AI agents are sensitive to nudges," *PNAS* 123(25), 15 June 2026, DOI 10.1073/pnas.2537030123; preprint arXiv:2505.11584). Standard remediation strategies (chain-of-thought prompting, in-context human examples) shift the distribution but do not reliably resolve this sensitivity. Reasoning-optimized models can partially restore human-level sensitivity, but do so inconsistently and at substantial inference cost — treat per-model susceptibility as something to test directly, not a property that newer models resolve for free.

**Awareness does not confer resistance.** A separate 2025–2026 study of LLM-powered GUI agents across 16 dark-pattern types found agents frequently fail to recognize manipulative interfaces at all, and — critically — even when they *do* recognize one, they prioritize task completion over protective action. The failure mode differs from the human one: humans succumb via cognitive shortcuts and habitual compliance, agents via procedural blind spots. Human oversight improved avoidance but introduced its own costs (attentional tunneling, added cognitive load on the supervisor), so human-in-the-loop is a mitigation with a price, not a solution (Tang et al., "Dark Patterns Meet GUI Agents," arXiv:2509.10723, 2025). Design implication: agent-facing guardrails must be structural (constrained action scope, explicit confirmation gates on irreversible steps), because detection prompts alone do not change agent behavior.

This creates a new dark-pattern risk: product environments that are merely nudge-grade for humans become effectively coercive for AI agents. Before deploying AI agents in any choice-architecture-heavy environment, behavioral tests against the specific nudges present are required. Relevant to primitives #4 (Defaults) and #9 (Choice Architecture).

**Conversational dark patterns** are a distinct surface from interface dark patterns: manipulation enacted in dialogue rather than layout — exaggerated agreement (sycophancy), biased framing of options, and privacy-intrusive probing. Users detect these through conversational signals but frequently accept them as normal helpfulness, and they disagree about who is accountable (company, model, or themselves). If your product ships an LLM interface, the harm test applies to generated turns, not just to screens (Shi et al., "The Siren Song of LLMs," CHI 2026; arXiv:2509.10830).

**When AI/ML systems deliver nudges** (recommendation engines, personalisation layers, chatbots), distinct ethical requirements apply beyond those for static nudge design: (1) the targeting model should be disclosed to be consistent with autonomy and EU AI Act Art. 5(1)(a) — opaque algorithmic steering is harder to override than a visible default; (2) algorithmic personalisation can amplify heterogeneous treatment effects, which raises equity concerns when the system disproportionately steers vulnerable user segments; (3) the same primitives (#4, #9, #10) that produce small average effects in static designs can produce much larger effects when a personalisation model is tuned to exploit individual susceptibility. Apply the standard harm test: would the targeting logic embarrass the team if disclosed to the targeted user?

### Regulatory Context (UK, EU & US)

In the UK, dark patterns may violate:
- **ASA CAP Code** (misleading advertising, false urgency)
- **CMA Consumer Markets Investigation** (subscription traps, fake reviews)
- **DMCC Act 2024, ss. 226–228** — misleading actions (s.226), misleading omissions (s.227), aggressive practices (s.228), plus the Sch. 20 list of practices banned outright. In force **6 April 2025**. These *replaced* the Consumer Protection from Unfair Trading Regulations 2008, which were **revoked** on that date by DMCC s.251(1) (commenced by SI 2025/272) — cite the DMCC, not the CPRs. The CMA can now impose fines of up to **10% of global annual turnover** by direct civil enforcement, without a court order. First infringement decisions: 8 firms on 18 November 2025 (drip pricing, default opt-ins, pressure selling); Marks Electrical fined £1.2m (reduced to £720,000 for early settlement, plus ~£600,000 redress) on 18 June 2026 for automatic opt-ins to paid add-on services. Verification trap: legislation.gov.uk’s page for SI 2008/1277 may still show no revocation banner because the revised-text pipeline lags commencement — check the *revoking* instrument, not the revoked one.
- **ICO GDPR guidance** (deceptive consent patterns count as invalid consent)

**EU DSA (2022, Art. 25 — active enforcement from 2024–):** Prohibits interface design that deceives or manipulates users or impairs free and informed decisions. First non-compliance fine: €120M against X (formerly Twitter), announced 5 December 2025 (dark patterns in paid-verification flows plus Art. 39/40 transparency and data-access failures). Article 25 is now enforced against Very Large Online Platforms. Covers choice architecture and interface manipulation directly — relevant to all deceptive uses of primitives #4, #6, #9. Does not overlap UCPD/GDPR scope (covered by UK instruments above), but extends to EU users of any product.

**EU AI Act Art. 5(1)(a) (in force 2 Feb 2025):** Prohibits AI systems that use subliminal techniques beyond a person's consciousness, or purposefully manipulative or deceptive techniques, to materially distort behaviour in a way that causes or is likely to cause significant harm. The Commission's Art. 5 guidelines (C(2025) 5052 final, adopted 29 July 2025 — an earlier February 2025 version circulated as informal guidance) explicitly name dark patterns as an example of a prohibited manipulative technique. Penalties: up to €35M or 7% of total worldwide annual turnover (Art. 99(3)), whichever is higher. Applies to any recommendation engine, chatbot, or personalisation layer deployed in or targeting EU users — directly affects algorithmic applications of primitives #4, #9, #10. Note the two-stage timeline: Art. 5 prohibitions have applied since 2 February 2025, while the broader GPAI and high-risk obligations phase in from 2 August 2026 — a manipulative-design violation is therefore already actionable today, independent of whether a system is in scope for the later obligations. Source: Regulation (EU) 2024/1689, Art. 5; artificialintelligenceact.eu/article/5/.

**EU Digital Fairness Act (forthcoming):** Extends dark-pattern prohibition beyond DSA's current Very Large Online Platform scope to broader commercial practices, including addictive design, influencer marketing, and unfair personalisation. Public consultation closed 24 October 2025; the Commission proposal remains scheduled for Q4 2026 (still in preparation phase as of August 2026, so it has not yet been tabled); Parliament and Council negotiations expected through 2027, with adoption in late 2027 at the earliest. Not yet in force — do not cite specific obligations from it, only the direction of travel. The design significance is scope, not novelty: practices currently legal for non-VLOP products because DSA Art. 25 does not reach them are the ones most likely to become non-compliant. Monitor for passage and entry into force.

**US FTC:** Dark patterns are actionable under FTC Act §5 (unfair or deceptive acts) and ROSCA. Largest enforcement to date: **FTC v. Amazon**, settled 25 September 2025 — $2.5B total ($1.0B civil penalty + $1.5B in consumer refunds to ~35M Prime subscribers) over deceptive Prime enrollment and cancellation flows (primitives #4, #9). The "click-to-cancel" rule (cancellation as easy as sign-up) was vacated by the Eighth Circuit in July 2025 on procedural (notice-and-comment) grounds, not on the merits; the FTC sent a reviving ANPRM to OIRA on 30 January 2026, published it for comment in March 2026 (comments closed 13 April 2026), and has restated the enforcement priority publicly. **Treat click-to-cancel as a live enforcement expectation regardless of the rule's status** — the FTC continues to charge the same conduct under §5/ROSCA. Live example: **FTC v. Uber** (amended complaint 15 December 2025, joined by 21 states plus DC) alleges UberOne enrollment without consent and a cancellation path requiring up to 32 actions across 23 screens. Roughly 30 US states also maintain their own automatic-renewal statutes, so a compliant federal posture is not sufficient on its own.

---

## Expert Judgment: Reading Evidence Strength

A non-expert treats every named effect the same way — "behavioral economics says X, so X is true." An expert grades each effect by replication status, sample, and design before recommending it. Behavioral economics has an unusually high rate of famous, textbook-cited findings that later failed to replicate or were built on fabricated data (ego depletion, social priming/"elderly walk," the Ariely–Gino "sign-at-top" honesty studies retracted in 2021, power-posing's hormonal claims). None of those are cited as load-bearing evidence in this skill's primitives — but the underlying discipline expects you to ask the same question of every claim you bring in from outside it.

**Evidence grade by primitive** (as of this validation date — re-check before citing a specific number in a client-facing deliverable):

| Grade | Meaning | Primitives in this band |
|---|---|---|
| **A — robust, mechanism-agnostic** | Replicates across labs, populations, and elicitation methods; direction is reliable even where magnitude varies | Defaults (#4) — opt-in/opt-out gap; Anchoring (#3) — direction of effect; framing direction (#1); basic habit cue-dependence (#12, #15) |
| **B — real but design-dependent magnitude** | Effect direction replicates, but the coefficient swings by 2× or more depending on elicitation method, population, or stimulus symmetry | Loss aversion (#2) — λ ranges ~1.07 (non-significant, symmetric design) to 1.955 (cross-domain mean) to 2.25 (canonical upper bound); prospect-theory parameters generally (#1) — Imai et al. 2025 finds measurement procedure is the strongest predictor of parameter variation; implementation intentions (#16) — d = 0.27–0.66 depending on format and rehearsal |
| **C — contested or near-zero on meta-analysis** | Frequently invoked in product folklore; the pooled/meta-analytic estimate is close to zero or the mechanism is disputed | Choice overload (#9) — mean effect ≈ 0 across 63 conditions (Scheibehenne et al. 2010); nudge effect sizes at scale (#4, #9) — d = 0.27 raw, 0.004 after publication-bias correction (Hu et al. 2025); decision fatigue / ego depletion as a named mechanism (referenced narrowly in #14) — original claims are heavily contested, but a weaker "degradation across long sequences" pattern still holds in field settings |
| **Not used here** | Famous but no longer credible as evidence | Ego depletion as a standalone effect, social/behavioral priming (Bargh-style), power posing, scarcity-mindset-as-cognitive-tax — do not import these into a recommendation even if a stakeholder asks for them by name; if asked, explain the replication failure rather than silently complying |

**How to use the grade**: an A-grade effect can anchor a design decision with modest local validation. A B-grade effect can motivate a hypothesis but the specific number (λ, d) must not be quoted to a stakeholder as a forecast — quote the range and say "we will measure our own." A C-grade effect should not drive a design decision at all without a local pilot showing it holds in this context; treat published product-folklore claims about it as marketing, not evidence.

**Sample-size and effect-size intuition**: most single-mechanism behavioral nudges in production settings land in the d = 0.05–0.20 range (Cohen's d) once measured outside a lab — not the d = 0.5–0.8 range common in original academic demonstrations. Detecting d = 0.10 at conventional power requires roughly 1,500–2,000 users per arm; detecting d = 0.05 requires roughly 6,000+ per arm. A team running a 200-user A/B test that shows a "40% lift" from a single nudge is very likely observing noise, not a stable effect — treat any effect over d ≈ 0.3 detected in a low-N pilot as a red flag for measurement error, not a genuine breakthrough. This is why the megastudy composition recipe (see Composition Recipes) exists: comparing several mechanisms in one large shared-control test corrects for the single-A/B inflation problem.

**WEIRD-sample generalization limits**: the primary literature underlying most of these primitives (Kahneman & Tversky's original studies, most classroom-recruited replications, Prolific/MTurk convenience samples used in modern replications) draws overwhelmingly from Western, Educated, Industrialized, Rich, Democratic populations — predominantly US/UK university students and platform gig workers. Effect direction (loss aversion is negative, defaults work, anchors bias) travels reasonably well across cultures. Effect *magnitude* does not: collectivist vs individualist framing changes social-proof and loss-aversion magnitudes, financial literacy changes anchoring susceptibility, and platform-panel samples (Prolific, MTurk) skew younger, more online-literate, and more experienced with survey-gaming than a typical product's user base. Before applying a published coefficient to a non-US/UK, non-English-speaking, non-online-panel population, treat the number as a hypothesis to test locally, not a starting default.

**When a nudge backfires** — recognize these before shipping, not after:
- **Reactance**: a default or scarcity signal that feels coercive triggers deliberate defiance, especially in populations primed to distrust the operator (repeat cancel-flow victims, regulated/skeptical B2B buyers). Symptom: the "losing" option's selection rate rises after the nudge ships.
- **Overjustification / crowding-out**: adding an extrinsic reward (streak, badge, discount) to a behavior the user already did for intrinsic reasons can reduce long-run engagement once the reward is removed or becomes routine — the reward substitutes for, rather than adds to, the original motivation. Relevant wherever primitive #13 (reinforcement schedules) is layered onto an already-habitual behavior (#12).
- **Negative social proof**: showing a low-adoption base rate to encourage adoption normalizes the low rate instead (Schultz et al. 2007) — see primitive #5's misuse boundary.
- **Trust cliff on discovery**: any fabricated or exaggerated signal (scarcity, social proof, anchor) produces a below-baseline outcome once discovered — the downside is asymmetric and often larger than the nudge's upside, because it taints future claims from the same source, not just the current one.
- **Diagnostic tell**: if a nudge's projected lift depends on the user *not* looking closely (a countdown that doesn't survive a refresh, a testimonial that doesn't survive a search, a default that doesn't survive being pointed out), it is already a backfire waiting for a discovery event — redesign before shipping, not after a complaint.

---

## Misuse Boundaries

| Misuse | Why It Is Wrong | Required Correction |
|---|---|---|
| Fabricating scarcity or proof | The lever works by deception, not better choice architecture | Use only verifiable constraints and real cohort data |
| Hiding opt-out or cancellation | Defaults become coercive when exit is costly | Make override and reversal as easy as entry |
| Using loss aversion to create anxiety | Loss framing can exploit fear when the loss is trivial or invented | Show only real user-relevant losses |
| Anchoring on irrelevant high prices | The anchor distorts without informing | Anchor with plausible, comparable, explained values |
| Using decoys to push overbuying | A dominated option can manipulate plan choice | Ensure the target option is genuinely best for the stated use case |
| Treating lab effect sizes as universal | Behavioral effects vary by domain and population | Run local measurement before optimizing around coefficients |
| Assuming loss aversion is universal regardless of experimental design | Loss aversion is design-dependent: λ drops to ≈1.07, non-significant, for symmetric, unordered gain-loss stimuli (2025 re-meta-analysis of the Brown et al. dataset, 84 papers/163 estimates/N=149,218); the effect is robust when design induces ordinal asymmetry, but not a universal constant | Always measure on your own population and design context; do not assume a 2× multiplier without testing |
| Variable-ratio schedules attached to non-essential or compulsion-prone actions | The schedule maximises engagement by exploiting prediction error, not by serving the user's goal | Default to fixed schedules; rate-cap any variable component; require an explicit harm-test sign-off for VR designs (#13) |
| Engineering habits for behaviors the user did not endorse | Cue→routine→reward design used to drive metrics, not user-stated goals | Bind habits to user-acknowledged goals; make cues legible and disable-able (#12) |
| Burying material decisions under cumulative cognitive load | Late-flow consent obtained when working memory is depleted is invalid consent | Move material decisions to early/low-load positions; strip extraneous load from decision screens (#14) |
| Cue-context redesign without cue preservation | Redesign collapses retention because the cue surface that triggered behavior moved | Preserve dominant cues across one full retention cycle; instrument cue-conditional retention before changing layouts (#15) |
| Pre-filling implementation intentions for the user | Plan binding requires user authorship — the user's mental representation of the cue must form the link | Offer plan templates; require the user to confirm or edit before activation (#16) |
| Reducing options assuming choice overload is universal | Meta-analytic mean choice overload effect ≈ 0 (Scheibehenne, Greifeneder & Todd, JCR 2010; 63 conditions, 50 experiments, N=5,036); effect is real under specific moderators (unclear preferences, high expertise asymmetry, poor option quality) but absent in many product contexts | Treat option reduction as a testable hypothesis; always measure abandonment rate with N options vs N−3 before attributing drop-off to overload (#9) |

Check [`references/patterns-scenarios-traps.md`](references/patterns-scenarios-traps.md) before applying primitives to production user flows.

---

## Decision Checklist

- [ ] **Framing choice**: Is the offer presented as a gain or loss? Does framing match actual value? → prospect theory (#1), loss aversion (#2)
- [ ] **Price reference point**: Is there an anchor before the price is shown? Is the anchor honest? → anchoring (#3)
- [ ] **Default state**: What does "do nothing" lead to? Is it the genuinely best option for the user? → defaults (#4)
- [ ] **Social uncertainty**: Does the user lack signal about whether to trust or act? → social proof (#5)
- [ ] **Urgency signal**: Is there a real constraint that justifies urgency? Is it displayed accurately? → scarcity (#6)
- [ ] **Commitment horizon**: Does the user face a present-vs-future tradeoff? Is a commitment device offered? → hyperbolic discounting (#7)
- [ ] **Price perception**: How is the money mentally categorized? Does reframing change willingness to pay? → mental accounting (#8)
- [ ] **Option set**: How many options? In what order? Which is the recommended option? Is there unnecessary friction (steps, clicks, form fields) in the path to a desired action? Field evidence shows even minor sludge can halve uptake. Run a sludge audit before launch: map the behavioral journey, estimate time per step, score friction (search / decision / cognitive / emotional cost), rank removal candidates. (OECD "Fixing Frictions" 2024 methodology.) → choice architecture (#9)
- [ ] **Cognitive load**: Is the decision path demanding deliberation the user is not performing? → dual-system (#10)
- [ ] **Pricing tiers**: Are there three or more tiers? Does the middle option have a dominant position? → decoy effect (#11)
- [ ] **Recurring action**: Does product value depend on a behavior repeating? Is there a stable cue → routine → reward triple? → habit loop (#12)
- [ ] **Reward schedule**: What schedule (FR/VR/FI/VI) is the system on? Is a variable-ratio component present, capped, and ethically reviewed? → reinforcement schedules (#13)
- [ ] **Capacity fit**: Does any screen exceed ~4 novel chunks? Are material decisions placed where cumulative load is low? → cognitive load (#14)
- [ ] **Cue stability**: For each load-bearing behavior, what cue triggers it? Will a planned redesign or migration disrupt the cue? → context-dependent retrieval (#15)
- [ ] **Plan binding**: For goal-pursuit features, has the user authored an if-then plan tying a specific cue to a specific response? → implementation intentions (#16)
- [ ] **AI-agent deployment**: If an AI agent operates on behalf of users in this flow, has a nudge-susceptibility audit been run against the choice architecture it will encounter, and are irreversible actions gated structurally rather than by prompt instruction? → AI agents as decision subjects (Ethical Bounds)
- [ ] **Generated-turn harm test**: If the product ships an LLM interface, do generated responses avoid sycophantic agreement, biased option framing, and privacy-intrusive probing? → conversational dark patterns (Ethical Bounds)
- [ ] **Ethical gate**: Does each technique pass the harm test? Would disclosure embarrass the team? → ethical bounds section

---

## Anti-Patterns

| Anti-Pattern | Behavioral Diagnosis | Fix |
|-------------|----------------------|-----|
| Dark patterns mistaken for nudges | Scarcity countdown on unlimited inventory; fake social proof numbers | Apply harm test: is the signal real? Would disclosure embarrass the team? |
| Scarcity used when supply is not scarce | Creates short-term urgency but destroys trust on discovery | Only display inventory/time constraints that are accurate and verifiable |
| Decoy used to mislead rather than clarify | Asymmetric dominance engineered to push users to an overpriced tier they don't need | Decoy is ethical only when the target option is genuinely better for the user's stated use case |
| Anchoring without informational value | High price anchor shown that has no relationship to the product being sold | Anchor must be plausible and relevant; explain what the price covers |
| Defaults that exploit irreversibility | Opt-out flows hidden behind multiple screens; subscription auto-renew with obscured cancellation | Default must be the user's best option; exit path must be as easy as entry path |
| Loss framing on trivial events | "You're leaving money on the table" for a $0 decision — erodes trust by manufacturing anxiety | Reserve loss framing for decisions where real value is genuinely at stake |
| Choice overload without guidance | 12 pricing tiers with no recommended option, causing abandonment | Constrain the set; add "Most Popular" or "Best for [persona]" guidance |
| Social proof for a number you don't have yet | "Thousands of users trust us" on a 50-user product | Use specific, accurate numbers; "50 teams already use this" beats a vague claim |
| "Neuroscience-based" claim with no mechanism named | Marketing veneer — habit loops dressed up as neuroscience without specifying cue / schedule / mechanism | Force every retention claim to name the primitive: cue (#12), schedule (#13), capacity (#14), cue stability (#15), or planned action (#16) |
| Streak counter as the entire habit design | Substitute reward — counter inflation rather than the user's real outcome; collapses on a missed day | Bind the routine's reward to a real user-visible outcome; treat the streak as instrumentation, not the reward (#12, #13) |
| "21 days to form a habit" assumption | Folk-myth; field median is ~66 days with wide variance | Plan for 4–12 weeks of cue-routine-reward repetition before automaticity; instrument the cue-conditional completion rate per cohort week (#12) |
| Variable-ratio reward added quietly to drive engagement metrics | VR is the canonical compulsion-design lever; engineering it without ethical review crosses the harm test | Default to fixed schedules; document any VR component, rate-cap it, and gate it behind a harm-test sign-off (#13) |
| Material consent buried in a long flow | Cumulative cognitive load depletes attention; late-flow consent is presumptively invalid | Place material decisions early in the flow with extraneous content stripped (#14) |
| Major redesign with no cue audit | Behavior collapses when the icon, entry path, or layout cues that triggered it move | Pre-redesign: catalogue cues per load-bearing behavior; preserve the dominant cue per behavior across at least one full retention cycle (#15) |
| Generic reminders instead of implementation intentions | "Don't forget to review" is not a plan — no cue→response binding, no automaticity | Replace with user-authored if-then ("When [cue], I will [response]"); offer templates, require user confirmation (#16) |
| Treating dormant users as still-bound to the original cue | Retrieval cues have decayed during dormancy; reactivation built on the prior cue extinguishes immediately | Treat 90+ day dormant users as a re-onboarding cohort; rebuild the cue→routine→reward (#12, #15) |
| Scaling nudges from academic RCT evidence to production without local validation | Nudge effects collapse under publication-bias correction (d=0.27 → 0.004 in a second-order meta-analysis of 1,638 studies; Hu et al. JBDM 2025) and in government at-scale deployments; published effect sizes are not deployment guarantees | Always measure on your own population and deployment context; treat published nudge effect sizes as upper-bound priors, not forecasts (#4, #9) |
| Underestimating trivial friction in high-value flows | A single added ordering step halved uptake of a free, high-value offer in a field experiment (91.7% → 51.7%, −40pp; Grieder et al. BPP 2024); practitioners routinely underestimate sludge by an order of magnitude | Conduct a sludge audit before launch; treat every added step as a potential halving event, not a minor UX inconvenience (#9, #14) |
| Telling an AI agent to "avoid dark patterns" and calling it mitigated | Agents that recognise a manipulative interface still prioritise task completion over protective action; detection is not resistance (Tang et al. 2025, 16 dark-pattern types) | Constrain structurally: narrow action scope, hard confirmation gates on irreversible/spend steps, spend ceiling; reserve human escalation for irreversible actions so oversight stays readable (Ethical Bounds) |
| Picking a single behavioral intervention without comparative testing | Sequential A/B testing of one treatment at a time inflates the apparent winner's effect size and misses mechanisms that dominate in your specific population | When the delivery channel is scalable (email, app push, in-product message), test ≥3 interventions simultaneously against a shared outcome metric before scaling; treat single-A/B pilot results as upper-bound priors, not deployment decisions (megastudy approach; Duckworth & Milkman, PNAS Nexus 2022) |

---

## Composition Recipes

### Recipe 1: Pricing Page Packaging

**Goal**: maximize conversion on a 3-tier pricing page while staying ethical.

**Stack**:
1. **Anchoring (#3)**: Show the highest tier first (or an "Enterprise" row), so the middle tier anchors low by comparison.
2. **Decoy effect (#11)**: Ensure the lowest tier is inferior to the middle on the dimension the target customer cares about, pushing preference toward middle.
3. **Loss aversion (#2)**: Frame the middle tier as "everything you need to avoid missing out on [core value]", not just "get more features".
4. **Choice architecture (#9)**: Highlight the recommended tier; reduce visual noise on the others.
5. **Ethical-bound check**: Is the recommended tier genuinely best for the modal customer? Is the lowest tier a real option, not a decoy with no rational use case?

**Fail signal**: conversion goes up but refund/churn increases — users were pushed to a tier above their actual need.

**Inputs:** 3 tier prices + feature lists, modal-customer persona (role, primary job-to-be-done, willingness-to-pay estimate), target conversion metric (e.g. % selecting middle tier).
**Rules:** Anchor on the highest tier first (or an Enterprise row); decoy (lowest tier) must be strictly inferior to the target tier on ≥1 dimension the modal customer cares about; ethical gate — confirm the recommended tier is genuinely best for the modal customer before publishing; if gate fails, revise the tier structure, not the framing.
**Outputs:** Revised tier display order + highlighted/recommended tier label + ethical gate pass/fail verdict + predicted lift band on target metric.

### Recipe 2: Onboarding Default Sequence

**Goal**: maximize activation without manipulating users into unwanted states.

**Stack**:
1. **Defaults (#4)**: Pre-select the configuration most users benefit from. Disclose it clearly.
2. **Present-bias mitigation (#7)**: If the full-value path requires upfront effort (import data, connect integrations), offer a "quick start" present-moment reward and schedule the deeper setup step.
3. **Social proof (#5)**: Show what comparable users did at the same step ("Most teams connect their CRM first").
4. **Dual-system (#10)**: Reduce System 2 load at each step — one decision per screen, clear language, no jargon.
5. **Ethical-bound check**: Are pre-selected options genuinely good for this user? Is opt-out visible?

**Fail signal**: high activation rate but low Day-7 retention — users were onboarded into a state they didn't want.

**Inputs:** Ordered task list with friction scores per step (time + cognitive effort estimate), user's stated goal, regret cost of each default (low / medium / high, and whether reversible within 24 h).
**Rules:** Default opt-out only if regret cost is low AND the default is aligned with the user's stated goal; require explicit opt-in if regret cost is medium-to-high or reversibility window < 24 h; each screen holds ≤1 decision (cognitive load #14); social proof shown only for verified cohort behaviour.
**Outputs:** Step sequence with default state labelled per step (opt-in / opt-out / neutral) + reversibility map (each step: can undo Y/N, window) + ethical gate pass/fail per default choice.

### Recipe 3: Churn Prevention Intervention

**Goal**: reduce voluntary cancellation without coercion.

**Stack**:
1. **Loss aversion (#2)**: Show the user what they will lose (data, streaks, integrations, colleagues' shared work) — only what is actually lost, not fabricated.
2. **Mental accounting (#8)**: Reframe the annual cost as daily rate; help user re-contextualize the expense relative to current use patterns.
3. **Hyperbolic discounting (#7)**: Offer a pause option as a commitment device — users who would cancel often continue after a pause.
4. **Social proof (#5)**: "Users who considered cancelling and stayed saw [measurable outcome]" — based on real cohort data.
5. **Ethical-bound check**: If the user still wants to cancel, the path must be direct. Cancellation friction is a dark pattern.

**Fail signal**: cancel flow reduces cancellations but increases chargebacks and complaint volume — users were blocked rather than persuaded.

**Inputs:** Baseline cancellation rate + reason-for-cancelling data, list of real assets the user loses on cancellation (data, streaks, integrations, shared work), current annual and monthly price points, cohort data for users who stayed after near-cancel.
**Rules:** Show only real, user-relevant losses — no fabricated or trivial losses; mental-accounting reframe (daily rate) applied only when the annual cost genuinely looks different at that granularity; pause offer surfaced before full cancellation CTA; cancellation path must be reachable in ≤3 clicks from the trigger point (exit must be as easy as entry).
**Outputs:** Revised churn-prevention copy using real loss inventory + daily-rate reframe if applicable + recommended intervention sequence (loss frame → pause offer → social proof → cancel CTA) + predicted lift band on save rate based on λ in range 1.3–2.0 (treat 2.25 as upper bound).

### Recipe 4: Retention Beyond Week 4 (Habit Formation)

**Goal**: convert week-1 activation into durable usage past the motivation cliff.

**Stack**:
1. **Habit loop (#12)**: Identify a stable user-side cue (existing calendar event, time of day, preceding routine action). Bind the load-bearing behavior to that cue, not to a notification you fully control.
2. **Implementation intentions (#16)**: At the activation step, prompt the user to author an if-then plan ("When [their cue], I will [response]"). Templates as starting points, user edits the cue. Plan rides on the user's existing surfaces (calendar, OS reminder), not a new engagement channel. After the user authors the plan, have them read it back or confirm it in a friction-free step — this rehearsal is an identified efficacy moderator (Sheeran et al. 2024, 642-test meta-analysis); it is not re-authoring.
3. **Reinforcement schedules (#13)**: Default to fixed-interval daily and fixed-ratio weekly. The reward is the user's own outcome being legible (yesterday's progress, today's primed view). No variable-ratio gloss.
4. **Cognitive load (#14)**: The cue-triggered surface delivers ≤4 novel chunks. Anything above that pushes the user back into goal-directed mode and breaks habit formation.
5. **Measurement**: Cue-conditional completion rate per cohort-week. Habit is forming when this rate stabilises and starts to dominate motivation-driven sessions (typically week 6–10).
6. **Ethical-bound check**: The user authored the cue. The cue is on a surface they can disable. The reward is real progress on their stated goal, not a substitute counter.

**Fail signal**: streak/counter goes up but real user-outcome metrics flatten — substitute reward; the user is engaging with the gamification, not the underlying value.

**Inputs:** Target recurring behavior + candidate stable cues (existing calendar events, time-of-day signals, preceding routine actions), user's stated goal, reward options (real outcome visibility vs. surrogate counter), reinforcement schedule currently in place.
**Rules:** Bind the routine to a user-side cue (not a fully controlled push notification); reward must be a real user-visible outcome, not a surrogate counter; default to fixed-interval daily + fixed-ratio weekly schedule; no variable-ratio component without explicit harm-test sign-off; habit is confirmed forming only when cue-conditional completion rate stabilises (typically week 6–10).
**Outputs:** Cue → routine → reward specification + recommended schedule type (FI/FR) + implementation intention template for user authorship + measurement plan (cue-conditional completion rate per cohort week, alert threshold for drop).

### Recipe 6: AI-Assistant UX — Ethical Nudge Guardrails

**Goal**: build onboarding flows, pricing pages, and conversational UX for AI-assistant / AI-agent products without crossing into manipulation or EU AI Act Art. 5 violations.

**Context**: AI products face a dual behavioral-economics problem. (1) The *human user* is subject to standard nudges — defaults, anchoring, social proof — just like any product. (2) The *AI agent* itself is a decision subject: several LLM agents shift to near-certain acceptance (probability ~1.0) of default and suggested options from baselines of 0.33–0.58, exceeding human susceptibility (which moves from 0.51 to 0.88 under the same default nudge) — though susceptibility varies substantially by model, so test the specific model in use rather than assuming worst-case (Cherep, Maes & Singh, "AI Agents Are Hypersensitive to Nudges," arXiv:2505.11584, 2025; PNAS 2026). Both problems require separate treatment.

**Stack — for the human-facing UX:**
1. **Defaults (#4)**: Pre-select the most privacy-protective and least surprising configuration. For AI features (data retention, training opt-in, autonomous action scope), the default must pass the "would this embarrass us if disclosed?" test doubly — once for UX and once for EU AI Act Art. 5(1)(a) (no subliminal manipulation to distort behaviour).
2. **Cognitive load (#14)**: AI capabilities are inherently complex. Consent and scope-setting flows must strip extraneous load. Material decisions (what data the AI accesses, what actions it can take autonomously) must appear early at low cognitive load — not buried after 7 onboarding steps.
3. **Social proof (#5)**: Usage statistics ("10,000 teams have connected their CRM") are valid. Claims about AI accuracy or reliability require accurate sourcing — fabricated precision is a dark pattern with higher stakes in AI contexts (users may over-rely).
4. **Dual-system (#10)**: AI-assistant UX often triggers System 2 because the capability is unfamiliar. Lean into deliberate framing at launch; shift to System 1 cues only after the user has formed a mental model.

**Stack — for the AI agent acting on behalf of users:**
5. **Choice architecture audit (#4, #9)**: Before deploying an AI agent in any choice-architecture-heavy environment (marketplaces, booking flows, multi-vendor pricing), run behavioral tests against the nudges present, per model. The agent's environment is not nudge-neutral — several current models accept default/suggested options at or near ceiling (probability ~1.0) where humans sit around 0.51–0.88; other models track human levels — susceptibility is model-specific, not universal.
6. **Structural guardrails over detection prompts**: Do not rely on instructing the agent to "watch for manipulative interfaces." Agents that recognise a dark pattern still prioritise task completion over protective action (Tang et al. 2025). Constrain what the agent can do instead: narrow action scope, hard confirmation gates on irreversible or spend-incurring steps, and a spend/commitment ceiling the agent cannot exceed without the user.
7. **Human oversight, costed honestly**: Oversight improves avoidance but adds attentional tunneling and supervisor load. Escalate selectively on irreversible actions rather than asking the user to review every step — a review surface the user stops reading is not oversight.
8. **Transparency disclosure**: EU AI Act Art. 5(1)(a) applies. If your agent's decision pathway involves information highlighting or default suggestions, disclose the mechanism in the system prompt and surface it to the user.

**Ethical-bound check**: (1) Is the default AI action scope the least-surprise, least-invasive option? (2) Can the user constrain the agent's scope in ≤2 steps? (3) Is the AI's behavior disclosure legible without reading a privacy policy?

**Fail signal**: high initial activation but user complaints of "the AI did something I didn't expect" — the agent's autonomy scope default was set too wide; cognitive load at consent was too high for informed choice.

**Inputs:** AI feature list with autonomy scope per feature (read / suggest / act), default state per feature (on/off), cognitive load estimate of consent/scope-setting flow (steps × decision complexity), target user's technical familiarity level.
**Rules:** Default autonomous actions to off or narrowest scope unless user has explicitly expanded; material scope decisions placed in the first 3 onboarding steps at ≤1 decision per screen; social proof claims must cite verifiable data; agent deployment in third-party environments requires a nudge-susceptibility audit before launch; irreversible and spend-incurring agent actions require a hard confirmation gate — never a prompt-level instruction to be careful.
**Outputs:** Default state table per AI feature (on/off, scope level, reversibility) + consent flow redesign with cognitive load score per step + nudge-susceptibility checklist for any third-party environment the agent operates in + EU AI Act Art. 5 compliance note.

---

### Recipe 5: Migration / Redesign Without Retention Collapse

**Goal**: ship a major UI or platform change without breaking the cue surface that triggers existing behavior.

**Stack**:
1. **Context-dependent retrieval (#15)**: Pre-redesign, catalogue cues per load-bearing behavior — entry-point icon, navigation path, keyboard shortcut, notification time. Preserve the dominant cue per behavior across at least one full retention cycle (typically 2–4 weeks).
2. **Habit loop (#12)**: For each load-bearing habit, identify whether it is goal-directed or stimulus-response. Stimulus-response habits are most fragile — those are where cue preservation matters most.
3. **Cognitive load (#14)**: New surfaces should not require novice-level chunking from existing power users. Provide an expert path that honours their learned chunks; offer the redesigned path as opt-in initially.
4. **Implementation intentions (#16)**: For users whose behavior was triggered by a cue you must remove, offer to re-anchor — let them author a new if-then plan tied to the new cue.
5. **Measurement**: Cue-conditional completion rate per behavior, daily, with an alert threshold. If a behavior's completion rate drops more than X% within Y days, partial rollback or cue restoration is required.
6. **Ethical-bound check**: Migration prompts are framed as user benefit, not platform optics. Reactivation flows for users who lapsed during the migration distinguish between "lost the cue" and "left the product."

**Fail signal**: feature usage drops sharply on the redesign even though the feature works — cue surface moved, habit decayed.

**Inputs:** List of load-bearing behaviors + their current cues (entry-point icon, navigation path, keyboard shortcut, notification time), habit type per behavior (goal-directed vs. stimulus-response), planned redesign scope (which cues will move or disappear), baseline cue-conditional completion rate per behavior.
**Rules:** Preserve the dominant cue per stimulus-response behavior across ≥1 full retention cycle (2–4 weeks) before removing it; offer expert path honouring learned chunks; any removed cue triggers a re-anchoring offer (user-authored if-then plan via #16); alert threshold set at completion-rate drop > 15% within 7 days of rollout.
**Outputs:** Cue audit table (behavior → current cue → cue preserved Y/N → re-anchor plan if N) + rollout sequencing recommendation + measurement plan (daily cue-conditional completion rate per behavior, rollback trigger definition).

---

## Workflow

1. Identify the decision point you are designing for (pricing, onboarding, retention, feature adoption, copy).
2. Use the [Decision Checklist](#decision-checklist) to identify which primitives are relevant.
3. Open the per-primitive playbook in [`assets/templates/behavioral-economics/`](assets/templates/behavioral-economics/) for the full definition, misuse boundary, and worked example.
4. Apply the [Ethical Bounds](#ethical-bounds) harm test to each technique before implementation.
5. For compound design problems, use the [Composition Recipes](#composition-recipes) as starting stacks.
6. Check the [Anti-Patterns](#anti-patterns) table to confirm you are not inadvertently shipping a dark pattern.

---

## ASCII Flow

```text
Human decision surface
  -> Identify choice point and user benefit
  -> Select relevant bias or behavior-change primitive
  -> Open primitive playbook for mechanism and misuse boundary
  -> Apply ethical harm test
     +-- fails test -> redesign without the nudge
     +-- passes test -> compose pattern and experiment
  -> Check anti-patterns and measure on the target audience
```

---

## Navigation

- Per-primitive playbooks: [`assets/templates/behavioral-economics/`](assets/templates/behavioral-economics/) (one file per primitive)
- Composition guide: [`assets/templates/behavioral-economics/README.md`](assets/templates/behavioral-economics/README.md)
- Formal theory map: [`references/formal-theory-map.md`](references/formal-theory-map.md)
- Patterns, scenarios, and traps: [`references/patterns-scenarios-traps.md`](references/patterns-scenarios-traps.md)
- Domain-agnostic primitives overview: [`references/primitives-overview.md`](references/primitives-overview.md)
- Sources: [`data/sources.json`](data/sources.json)

---

## Related Skills

_Consumer applied recipe layers that use these primitives will link here when added._

- `marketing-cro` — conversion rate optimization applied recipes
- `startup-business-models` — pricing and packaging applied recipes
- `marketing-content-strategy` — copy and messaging applied recipes
- `product-management` — onboarding and feature adoption applied recipes
- `marketing-paid-advertising` — ad copy and landing page applied recipes

---

## Fact-Checking

- Primary sources are cited in each per-primitive playbook and in [`data/sources.json`](data/sources.json).
- Canonical references: Kahneman & Tversky 1979 (prospect theory), Kahneman 2011 (dual-system), Thaler & Sunstein 2008 (nudge/choice architecture), Ariely 2008 (anchoring, decoy, mental accounting), Cialdini 1984 (social proof, scarcity), Loewenstein & Prelec 1991 (mental accounting), Frederick, Loewenstein & O'Donoghue 2002 (time preferences, hyperbolic discounting), Wood & Rünger 2016 + Lally et al. 2010 (habit loop, time-to-automaticity), Ferster & Skinner 1957 + Schultz 1997 (reinforcement schedules, dopamine prediction error), Miller 1956 + Cowan 2001 + Sweller et al. 2019 (working memory, cognitive load), Tulving & Thomson 1973 + Wood, Tam & Witt 2005 (encoding specificity, context-dependent habits), Gollwitzer & Sheeran 2006 (implementation intentions meta-analysis).
- Numeric effect sizes are from primary papers. Domain-specific applications may differ — always measure on your own population before treating published coefficients as guarantees.
- **Loss aversion coefficient:** Brown, Imai, Vieider & Camerer, *Journal of Economic Literature* 62(2), 2024 (607 estimates, 150 papers) places mean λ at 1.955 (95% CI [1.820, 2.102]); Walasek, Mullett & Stewart, *Journal of Economic Psychology* 103, 2024 (risky choice) at 1.31 (95% CI [1.10, 1.53]). The canonical λ ≈ 2.25 (Tversky & Kahneman 1992) is now a well-established upper bound, not the central estimate. A 2025 re-meta-analysis of the Brown et al. dataset (84 papers, 163 estimates, N=149,218) finds λ ≈ 1.07 (non-significant) for symmetric unordered gain-loss designs — loss aversion is robust when design induces ordinal asymmetry, but not a universal constant.
- **Nudge effect sizes at scale:** Hu et al. JBDM 2025 (second-order meta-analysis of 14 nudge meta-analyses, 1,638 studies, ~30M participants) finds raw d = 0.27, publication-bias-corrected d = 0.004. Government at-scale deployments show consistently smaller effects than academic RCTs. Do not treat published nudge effect sizes as deployment guarantees.
- **Implementation intentions:** Sheeran, Listrom & Gollwitzer (2024) — 642-test meta-analysis (European Review of Social Psychology, 36(1)) updates Gollwitzer & Sheeran 2006; d = 0.27–0.66 across outcome types; effect is larger when: (1) if-then format used, (2) user is highly motivated, (3) plan is rehearsed ≥1 time. In onboarding: after the user authors the plan, have them read it back or confirm it — this rehearsal step is an identified efficacy moderator, not re-authoring.
- **AI agents as decision subjects:** Cherep et al., "AI agents are sensitive to nudges," *PNAS* 123(25), 15 June 2026 (DOI 10.1073/pnas.2537030123; preprint arXiv:2505.11584) — LLM agents exceed human nudge sensitivity; reasoning-optimized models partially restore human-level response but inconsistently and at cost. Tang et al., arXiv:2509.10723 (2025) — across 16 dark-pattern types, GUI agents often fail to detect manipulative interfaces and, when they do detect them, still prioritise task completion; human oversight helps but adds attentional tunneling. Shi et al., CHI 2026 (arXiv:2509.10830) — conversational dark patterns (sycophancy, biased framing, privacy probing) in LLM dialogue, and user difficulty attributing accountability.
- If web access is unavailable, mark runtime-specific claims as unverified.

## Learnings Loop

Before applying this skill on a non-trivial task, read `learnings.consolidated.md` in this directory (and `learnings.md` if present).

After applying it, if you encountered a pattern worth remembering, a mistake worth preventing, or a domain fact that surprised you, append one dated bullet to `learnings.md` via `agents-skills-feedback-loop/scripts/append_learning.py`. Do not modify `SKILL.md` itself.
