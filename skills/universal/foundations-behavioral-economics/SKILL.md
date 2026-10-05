---
name: foundations-behavioral-economics
description: "16 evidence-graded behavioral-economics primitives. Use when asking will this nudge work, is a pricing decoy or dark pattern lawful, or what effect size to expect."
compatibility: Portable core only.
version: "1.4"
last_validated: 2026-08-14
---

# Behavioral Economics Foundations

Read each primitive's misuse boundary before applying it. The disclosure test is an ethical screen, not a legal definition: a technique that embarrasses the team on disclosure needs redesign even if it is lawful.

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
- The required lift is larger than the evidence can support — diagnose the offer, audience, and friction before assuming framing can close the gap

## Quick Reference

Each primitive has a full playbook: Definition / When to use / Misuse boundary / Inputs / Outputs / Failure modes / Worked example / Sources. Grades are explained in [Expert Judgment](#expert-judgment-reading-evidence-strength).

| # | Primitive | Core Effect | When to Use | Grade |
|---|-----------|-------------|-------------|---|
| 1 | [Prospect Theory](assets/templates/behavioral-economics/01-prospect-theory.md) | Gains and losses are not mirror images; framing shifts choice | Pricing copy, offer framing, upgrade messaging | A (direction) |
| 2 | [Loss Aversion](assets/templates/behavioral-economics/02-loss-aversion.md) | Loss framing can shift choices; magnitude varies by task, stakes, and elicitation method | Churn prevention, trial expiry, feature removal messaging | B |
| 3 | [Anchoring](assets/templates/behavioral-economics/03-anchoring.md) | First number shown distorts all subsequent judgments | Pricing pages, salary negotiation, discount presentation | A (direction) |
| 4 | [Defaults](assets/templates/behavioral-economics/04-defaults.md) | People disproportionately stick with pre-set options | Onboarding, opt-in/out choices, plan pre-selection | A in specific field settings (enrolment, organ donation); pooled evidence undecided after correction — see [nudge-calibration.md](references/nudge-calibration.md) |
| 5 | [Social Proof](assets/templates/behavioral-economics/05-social-proof.md) | People infer correct action from others' behavior | Sign-up pages, review placement, usage statistics | B |
| 6 | [Scarcity](assets/templates/behavioral-economics/06-scarcity.md) | Limited availability increases perceived value | Inventory counts, time-limited offers, waitlists | B |
| 7 | [Hyperbolic Discounting](assets/templates/behavioral-economics/07-hyperbolic-discounting.md) | Present bias: immediate rewards are disproportionately preferred | Free trials, commitment devices, annual vs monthly pricing | A (direction) |
| 8 | [Mental Accounting](assets/templates/behavioral-economics/08-mental-accounting.md) | People categorize money differently depending on source and label | Bundling, gift cards, credit framing, sunk-cost effects | B |
| 9 | [Choice Architecture](assets/templates/behavioral-economics/09-choice-architecture.md) | How choices are presented alters which option is selected | Option ordering, menu design, default pre-selection | C for "choice overload" specifically (mean effect ≈0, Scheibehenne et al. 2010); B for ordering/default effects generally |
| 10 | [Dual-System Cognition](assets/templates/behavioral-economics/10-dual-system.md) | Two cognitive modes with different speed/effort profiles influence which levers work | Copy tone, complexity of CTA, trust signals | B — a descriptive heuristic, not a literal neural dichotomy |
| 11 | [Decoy Effect / Asymmetric Dominance](assets/templates/behavioral-economics/11-decoy-effect-asymmetric-dominance.md) | A dominated option shifts preference toward its dominator | Pricing tier design, plan comparison tables | C — fragile outside stylized numeric stimuli (Frederick, Lee & Baskin 2014; Yang & Lynn 2014: 11/91 reliable) |
| 12 | [Habit Loop](assets/templates/behavioral-economics/12-habit-loop.md) | Stable cue → routine → reward becomes automatic with repetition | Daily/recurring usage, retention beyond week 4, durable behavior change | A (direction); no fixed weeks-to-automaticity number — see the fixed-weeks trap below |
| 13 | [Reinforcement Schedules](assets/templates/behavioral-economics/13-reinforcement-schedules.md) | Schedule (FR/VR/FI/VI), not just reward, governs acquisition and resistance to extinction | Streaks, rewards, gamification, reactivation; auditing existing reward systems | B |
| 14 | [Cognitive Load & Working Memory](assets/templates/behavioral-economics/14-cognitive-load-working-memory.md) | Working memory holds ~4 novel chunks; extraneous load suppresses informed choice | Forms, dashboards, alerts, error displays, consent flows, onboarding step count | A |
| 15 | [Context-Dependent Retrieval](assets/templates/behavioral-economics/15-context-dependent-retrieval.md) | Behaviors are bound to the cues present at encoding; performance can weaken when context shifts | Migrations, redesigns, cross-surface continuity, dormant-user reactivation | B — direction reliable in meta-analysis (Smith & Vela 2001), moderated by "outshining" from non-contextual cues; the flagship Godden & Baddeley-style replication failed (Murre 2021 + 2022 addendum) |
| 16 | [Implementation Intentions](assets/templates/behavioral-economics/16-implementation-intentions.md) | User-endorsed if-then plans bind a specific cue to a specific response, supporting goal completion | Goal-pursuit features, onboarding into habit-forming behavior, transition-state re-anchoring | B — outcome-specific effects; publication-bias adjustment reduces the overall estimate (Sheeran et al. 2024; see evidence notes below) |

**Failure modes addressed**, one line each: #1/#2 treating gains and losses as symmetric; #3 letting the user anchor on a competitor's number; #4 opt-in flows that require active effort; #5 empty/invisible proof signals; #6 no urgency signal; #7 annual plans losing to a monthly default; #8 lump-sum pricing hiding true perceived size; #9 option overload or unguided menus; #10 System-2 copy aimed at a System-1 decision; #11 two-option pricing with no reference point; #12 attributing retention decline to "habit" without cue-conditional evidence; #13 a reward system that worked at launch then went dead; #14 mid-flow abandonment from working-memory overload; #15 a redesign silently breaking the cue that triggered a behavior; #16 generic reminders standing in for an authored if-then plan.

---

## Formal Supporting Theory

Use [references/formal-theory-map.md](references/formal-theory-map.md) when the task needs source assumptions, ethical boundaries, or a distinction between observed behavior and normative decision quality.


**Canonical references**: Kahneman & Tversky 1979 (prospect theory), Kahneman 2011 (dual-system), Thaler & Sunstein 2008 (nudge/choice architecture), Ariely 2008 (illustrative — anchoring, decoy, mental accounting; treat as a trade-book demonstration, not primary evidence), Cialdini 1984 (social proof, scarcity), Loewenstein & Prelec 1991 (mental accounting), Frederick, Loewenstein & O'Donoghue 2002 (time preferences), Wood & Rünger 2016 + Lally et al. 2010 (habit loop, time-to-automaticity), Ferster & Skinner 1957 + Schultz 1997 (reinforcement schedules), Miller 1956 + Cowan 2001 + Sweller et al. 2019 (working memory, cognitive load), Tulving & Thomson 1973 + Wood, Tam & Witt 2005 (encoding specificity, context-dependent habits), Gollwitzer & Sheeran 2006 (implementation intentions meta-analysis, updated by Sheeran, Listrom & Gollwitzer 2024). Numeric effect sizes are from primary papers; domain-specific applications may differ — always measure on your own population before treating published coefficients as guarantees.

---

## Ethical Bounds

### The Harm Test (Thaler & Sunstein)

A nudge is legitimate if it: (1) steers people toward choices they would endorse on reflection; (2) can be easily overridden or opted out of; (3) does not exploit cognitive limitations to work against the user's interests.

A dark pattern fails one or more of these. The same psychological lever — scarcity, defaults, loss framing — can be a nudge or a dark pattern depending on whether the underlying offer is good for the user.

| Dimension | Nudge | Dark Pattern |
|-----------|-------|--------------|
| Transparency | Can be disclosed without changing its effect | Requires concealment to work |
| User benefit | Steers toward user's own goals | Overrides user's goals in favor of operator's |
| Reversibility | Easy to undo or override | Designed to make undoing difficult |
| Honest signal | Scarcity / proof / urgency is real | Signal is fabricated |
| Regulatory posture | Survives ASA/FTC/CMA scrutiny | Attracts regulatory action |

Every primitive carries a "Misuse boundary" stating its specific manipulation risk and the required condition for ethical use — non-negotiable gates, not optional guidelines.

### AI Agents as Decision Subjects

When LLMs or AI agents make decisions on behalf of users (shopping, booking, form completion), choice-architecture manipulations apply to the agent, not the human — and with dramatically larger effect sizes. Under a default-option nudge, human choice probability shifted from 0.51 (no nudge) to 0.88; several LLMs (GPT-4o, Claude 3 Haiku, o3-Mini, GPT-3.5-Turbo) shifted to ~1.0 from baselines of 0.33–0.58 — a larger jump than humans, though Claude 3.5 Sonnet and Gemini 1.5 Pro stayed close to human levels (~0.89–0.91). The pattern held for suggested alternatives and information highlighting too (Cherep, Maes & Singh, "AI agents are sensitive to nudges," *PNAS* 123(25), 2026, DOI 10.1073/pnas.2537030123; preprint arXiv:2505.11584). Standard remediation (chain-of-thought prompting, in-context human examples) shifts the distribution but does not reliably resolve this sensitivity; reasoning-optimized models partially restore human-level sensitivity, but inconsistently and at substantial inference cost — treat per-model susceptibility as something to test directly, not a property newer models resolve for free.

**Awareness does not confer resistance.** A separate 2025 study of LLM-powered GUI agents across 16 dark-pattern types (Tang et al., arXiv:2509.10723) found agents frequently fail to recognize manipulative interfaces at all, and — critically — even when they *do* recognize one, they prioritize task completion over protective action. Human oversight improved avoidance but added attentional tunneling and supervisor load, so human-in-the-loop is a mitigation with a price, not a solution. Design implication: agent-facing guardrails must be structural (constrained action scope, explicit confirmation gates on irreversible steps) — detection prompts alone do not change agent behavior.

**Conversational dark patterns** are a distinct surface: manipulation enacted in dialogue rather than layout — exaggerated agreement (sycophancy), biased framing of options, privacy-intrusive probing. Users detect these through conversational signals but frequently accept them as normal helpfulness (Shi et al., "The Siren Song of LLMs," CHI 2026; arXiv:2509.10830). If your product ships an LLM interface, the harm test applies to generated turns, not just to screens.

**AI as a persuasion source** (distinct from AI as a nudge *target*, above): as reported in Salvi et al. 2025 (*Nature Human Behaviour*, DOI 10.1038/s41562-025-02194-6), GPT-4 with access to a debate opponent's demographics had 81.2% higher odds of higher post-debate agreement than the Human–Human baseline (Abstract), an odds comparison rather than a completion-rate multiplier. The [3 Sep 2026 Author Correction](https://www.nature.com/articles/s41562-026-02588-0), corrected Aggregate results, reports that the *personalised-vs-non-personalised* GPT-4 comparison was non-significant (+48.7%, 95% CI [−2.9%, +127.6%], P = 0.07) — the advantage over humans stands, but "personalisation specifically adds persuasion" is not established. Separately, Hackenburg et al. 2025 ("The levers of political persuasion with conversational artificial intelligence," *Science* 390, DOI 10.1126/science.aea3884; three experiments, N = 76,977, 19 LLMs) found post-training and prompting raised persuasiveness by up to 51% and 27% respectively — more than personalisation or scale — and that where persuasiveness rose, factual accuracy fell. **That accuracy trade-off is the concrete harm test for an AI sales or support agent**: measure factual accuracy alongside persuasion, not persuasion alone. There is no established method here for auditing agent-as-persuader risk beyond ad hoc accuracy checks; treat this as an open gap.

**When AI/ML systems deliver nudges** (recommendation engines, personalisation, chatbots): (1) disclose the targeting model as an autonomy safeguard, not a general duty; (2) algorithmic personalisation can amplify heterogeneous treatment effects, raising equity concerns when it disproportionately steers vulnerable segments; (3) primitives #4, #9, #10 that produce small average effects in static designs can produce much larger effects when a personalisation model is tuned to exploit individual susceptibility. Apply the standard harm test to the targeting logic, not just the surface.

### Regulatory Context

Before a legality claim about pricing, defaults, cancellation, or AI manipulation, read [references/regulatory-context.md](references/regulatory-context.md). Follow its official-law and regulator links to check territorial scope, current amended text, rule status, and application dates; cached enforcement examples do not establish the governing obligation. Qualified counsel determines the legal conclusion.

---

## Expert Judgment: Reading Evidence Strength

A non-expert treats every named effect the same way — "behavioral economics says X, so X is true." An expert grades each effect by replication status, sample, and design before recommending it. Behavioral economics has an unusually high rate of famous, textbook-cited findings that later failed to replicate or were built on fabricated data (ego depletion, social priming/"elderly walk," the Ariely–Gino "sign-at-top" honesty studies retracted in 2021, power-posing's hormonal claims). None of those are load-bearing evidence in this skill's primitives — but the discipline expects you to ask the same question of every claim brought in from outside it.

**Grade legend**: **A** = replicates across labs, populations, elicitation methods; direction reliable even where magnitude varies. **B** = direction replicates but the coefficient swings ≥2× by design, population, or stimulus. **C** = frequently invoked in product folklore, but the pooled/meta-analytic estimate is near zero or the mechanism is disputed — do not drive a design decision on a C-grade effect without a local pilot. Grades per primitive are in the [Quick Reference table](#quick-reference) above; do not treat "A" as license to skip local measurement, and do not treat "B" as license to quote a specific number (λ, d) to a stakeholder as a forecast.

**Famous but not credible as evidence — do not import even if asked by name**: ego depletion as a standalone effect, social/behavioral priming (Bargh-style), power posing, scarcity-mindset-as-cognitive-tax. If asked, explain the replication failure rather than silently complying.

**Nudge calibration and sample-size arithmetic** (Maier 2022, DellaVigna & Linos 2022, Szaszi 2022 — replacing a single low-quality second-order synthesis as the primary calibration layer): [references/nudge-calibration.md](references/nudge-calibration.md). Read this before promising a board a forecast lift or sizing a test.


**Loss aversion coefficient**: Brown, Imai, Vieider & Camerer, *JEL* 62(2), 2024 (607 estimates, 150 papers) places mean λ at 1.955 [1.820, 2.102]; Walasek, Mullett & Stewart, *J. Econ. Psych.* 103, 2024 (risky choice) at 1.31 [1.10, 1.53]. The canonical λ ≈ 2.25 (Tversky & Kahneman 1992) is a historical task-specific estimate, not a population bound or copy-response multiplier — never use it as a lift multiplier on copy or forecasts. A 2025 re-meta-analysis of the Brown et al. dataset (84 papers, 163 estimates, N=149,218) finds λ ≈ 1.07 (non-significant) for symmetric unordered gain-loss designs.

**Nudge effect sizes at scale**: see [references/nudge-calibration.md](references/nudge-calibration.md) for the full calibration set (Maier, DellaVigna & Linos, Szaszi, Hu). Do not treat any single published nudge effect size as a deployment guarantee.

**Implementation intentions**: Sheeran, Listrom & Gollwitzer 2024 — the [author manuscript](https://www.researchgate.net/profile/Paschal-Sheeran/publication/378870694_The_When_and_How_of_Planning_Meta-Analysis_of_the_Scope_and_Components_of_Implementation_Intentions_in_642_Tests/links/65f06a571f0aec67e282f88a/The-When-and-How-of-Planning-Meta-Analysis-of-the-Scope-and-Components-of-Implementation-Intentions-in-642-Tests.pdf), p. 4, reports d = 0.27 for behavior and d = 0.66 for affect, not a format/rehearsal range. Its 642-test overall estimate is d = 0.36, reduced to d = 0.15 [0.08, 0.22] by Robust Bayesian Meta-Analysis adjusting for publication bias. Format, motivation, and rehearsal moderate effects; none is a product-lift guarantee.

**WEIRD-sample generalization limits**: the primary literature underlying most of these primitives (Kahneman & Tversky's original studies, classroom-recruited replications, Prolific/MTurk convenience samples) draws overwhelmingly from Western, Educated, Industrialized, Rich, Democratic populations. Effect *direction* travels reasonably well across cultures; effect *magnitude* does not — collectivist vs individualist framing changes social-proof and loss-aversion magnitudes, financial literacy changes anchoring susceptibility. Treat a published coefficient as a hypothesis to test locally before applying it to a non-US/UK, non-English-speaking, or non-online-panel population.

**When a nudge backfires** — recognize these before shipping, not after:
- **Reactance**: a default or scarcity signal that feels coercive triggers deliberate defiance, especially in populations primed to distrust the operator. Symptom: the "losing" option's selection rate rises after the nudge ships.
- **Overjustification / crowding-out**: adding an extrinsic reward to a behavior the user already did for intrinsic reasons can reduce long-run engagement once the reward is removed or becomes routine.
- **Negative social proof**: showing a low-adoption base rate to encourage adoption normalizes the low rate instead (Schultz et al. 2007).
- **Trust cliff on discovery**: any fabricated or exaggerated signal produces a below-baseline outcome once discovered — the downside is asymmetric and often larger than the nudge's upside, because it taints future claims from the same source.
- **Diagnostic tell**: if a nudge's projected lift depends on the user *not* looking closely, it is already a backfire waiting for a discovery event.

---

## Misuse and Anti-Patterns

One merged table. Every primitive's "Misuse boundary" subsection restates its own row in more detail — read that before applying the primitive.

| Pattern | Diagnosis | Required Fix |
|---|---|---|
| Fabricated scarcity or social proof | The lever works by deception, not better choice architecture | Use only verifiable constraints and real cohort data; specific numbers ("50 teams") beat vague claims |
| Hidden opt-out or cancellation | Defaults become coercive when exit is costly | Make override and reversal as easy as entry (#4) |
| Loss framing on trivial events | Manufactures anxiety where no real value is at stake | Reserve loss framing for decisions where real value is genuinely at stake (#2) |
| Anchoring with no informational value | The anchor distorts without informing | Anchor with plausible, comparable, explained values (#3) |
| Decoy used to push overbuying or mislead | A dominated option can manipulate plan choice; the mechanism is fragile outside numeric-attribute contexts (Grade C) | Ensure the target is genuinely best for the modal user; use the corrected asymmetric-dominance definition and fragility caveat in [the decoy template](assets/templates/behavioral-economics/11-decoy-effect-asymmetric-dominance.md) (#11) |
| Choice overload used to justify option-cutting | Meta-analytic mean choice-overload effect ≈0 across 63 conditions (Scheibehenne, Greifeneder & Todd, *JCR* 2010, N=5,036); real only under specific moderators | Treat option reduction as a testable hypothesis; measure abandonment with N vs N−3 options before attributing drop-off to overload (#9) |
| Treating lab effect sizes, or any single published coefficient, as a production guarantee | Nudge effects shrink under publication-bias correction and in government at-scale deployments (see [nudge-calibration.md](references/nudge-calibration.md)) | Always measure on your own population; use published effects as priors, not forecasts (#4, #9) |
| Assuming loss aversion is a universal 2× constant | λ ranges from ≈1.07 (non-significant, symmetric unordered design) to 1.955 (cross-domain mean) to 2.25 (historical task-specific estimate, Tversky & Kahneman 1992 — not 1979, and not a copy-response multiplier) | Always measure on your own population and design; do not apply λ as a fixed multiplier to any copy or forecast number (#2) |
| Variable-ratio schedules on non-essential or compulsion-prone actions | Maximises engagement by exploiting prediction error, not by serving the user's goal | Default to fixed schedules; rate-cap any VR component; require explicit harm-test sign-off (#13) |
| Streak counters standing in for the whole habit design | Substitute reward — counter inflation rather than the user's real outcome; collapses on a missed day | Bind the routine's reward to a real user-visible outcome; treat the streak as instrumentation, not the reward (#12, #13) |
| Engineering habits for behaviors the user did not endorse | Cue→routine→reward design used to drive metrics, not user-stated goals | Bind habits to user-acknowledged goals; make cues legible and disable-able (#12) |
| Fixed "N weeks to form a habit" claims | Time-to-automaticity is highly variable (Lally et al.: 18–254 days to 95% of asymptote, 96 volunteers) — no fixed week count generalises | Instrument the cue-conditional completion rate per cohort week instead of committing to a weeks-to-habit number (#12) |
| Material decisions buried under cumulative cognitive load | Late-flow decisions may undermine informed choice; consent validity depends on the full interaction context | Move material decisions to early/low-load positions; strip extraneous load (#14) |
| Major redesign shipped with no cue audit | Behavior weakens when the icon, entry path, or layout cues that triggered it move — moderated by "outshining" from other in-product cues | Catalogue cues per load-bearing behavior pre-redesign; preserve the dominant cue across ≥1 full retention cycle (#15) |
| Generic reminders substituted for implementation intentions | "Don't forget to review" is not a plan — no cue→response binding, no rehearsal | Replace with user-authored if-then ("When [cue], I will [response]"); require confirmation, not pre-fill (#16) |
| Reactivating dormant users on an untested cue | The prior cue may have lost relevance or accessibility; dormancy alone does not establish extinction | Test whether the cue still works; offer re-onboarding when it fails, using a threshold matched to the product's use cycle (#12, #15) |
| Underestimating trivial friction in high-value flows | As reported in [Grieder et al.](https://doi.org/10.1017/bpp.2024.44), Results: 91.7% orders with consultant ordering vs. 51.7% with self-service ordering among 173 Swiss SMEs | Audit ordering friction, then measure local uptake; this field contrast is not a universal per-step halving rule (#9, #14) |
| Telling an AI agent to "avoid dark patterns" and calling it mitigated | Agents that recognise a manipulative interface still prioritise task completion over protective action — detection is not resistance (Tang et al. 2025) | Constrain structurally: narrow action scope, hard confirmation gates on irreversible/spend steps, spend ceiling |
| "Neuroscience-based" retention claim with no named mechanism | Marketing veneer — habit loops dressed up as neuroscience without specifying cue, schedule, or capacity | Force every retention claim to name the primitive: cue (#12), schedule (#13), capacity (#14), cue stability (#15), or planned action (#16) |
| Picking a winner without comparative confirmation | Selecting the largest noisy estimate can exaggerate its effect under either sequential or simultaneous testing | When delivery is scalable and arms can be powered, compare several interventions against a common control and shared outcome; adjust for multiple comparisons and confirm the selected winner (megastudy approach; Duckworth & Milkman, *PNAS Nexus* 2022) |
| Business model whose margin IS the bias | The primitive is the revenue line, not a retention technique. Revenue concentration rising in the top decile is a leading indicator of both whale churn and duty-of-care exposure | Track share of revenue from users whose spend exceeds plausible disposable income as a risk metric; see [`references/patterns-scenarios-traps.md` § Edge-over-appetite business models](references/patterns-scenarios-traps.md#edge-over-appetite-business-models) |

Check [references/patterns-scenarios-traps.md](references/patterns-scenarios-traps.md) before applying primitives to production user flows.

---

## Decision Checklist

- [ ] **Mechanism and outcome**: Select primitives from the [Quick Reference](#quick-reference), name the cue/reference point/default being changed, and specify the user's desired outcome plus a control comparison.
- [ ] **Informed and reversible choice**: Verify truthful anchors/proof/scarcity, an easy override, legible total cost, and low-load material decisions. For recurring behavior, confirm the user's goal, cue, reward, and editable if-then plan.
- [ ] **AI-agent deployment**: Has a nudge-susceptibility audit run against the choice architecture the agent will encounter? Are irreversible actions gated structurally, not by prompt instruction? → [AI agents as decision subjects](#ethical-bounds)
- [ ] **Generated-turn harm test**: If the product ships an LLM interface, do generated responses avoid sycophantic agreement, biased framing, and privacy-intrusive probing, and is factual accuracy checked alongside persuasion? → [AI as a persuasion source](#ethical-bounds)
- [ ] **Ethical gate**: Does each technique pass the harm test? Would disclosure embarrass the team? → [Ethical Bounds](#ethical-bounds)

---

## Composition Recipes

Read [references/composition-recipes.md](references/composition-recipes.md) for pricing, onboarding, churn, retention, or migration stacks.

### Recipe 6: AI-Assistant UX — Ethical Nudge Guardrails

**Goal**: build onboarding flows, pricing pages, and conversational UX for AI-assistant / AI-agent products without crossing into manipulation or EU AI Act Art. 5 violations.

**Context**: Test human-facing choice architecture and the specific AI agent acting on it separately; susceptibility differs by model (see [AI Agents as Decision Subjects](#ethical-bounds)).

**Stack — for the human-facing UX:**
1. **Defaults (#4)**: Pre-select the most privacy-protective and least surprising configuration. For AI features (data retention, training opt-in, autonomous action scope), apply the disclosure test for UX, then separately assess the legal conditions in EU AI Act Art. 5(1)(a).
2. **Cognitive load (#14)**: Consent and scope-setting flows must strip extraneous load. Material decisions (what data the AI accesses, what actions it can take autonomously) must appear early at low cognitive load.
3. **Social proof (#5)**: Usage statistics are valid. Claims about AI accuracy or reliability require accurate sourcing — fabricated precision is a dark pattern with higher stakes (users may over-rely).
4. **Dual-system (#10)**: AI-assistant UX often triggers deliberate System-2 attention because the capability is unfamiliar. Lean into deliberate framing at launch; shift to lighter cues only after the user has formed a mental model.

**Stack — for the AI agent acting on behalf of users:**
5. **Choice architecture audit (#4, #9)**: Before deploying an AI agent in any choice-architecture-heavy environment (marketplaces, booking flows, multi-vendor pricing), run behavioral tests against the nudges present, per model — susceptibility is model-specific, not universal.
6. **Structural guardrails over detection prompts**: Do not rely on instructing the agent to "watch for manipulative interfaces" — detection is not resistance. Constrain what the agent can do: narrow action scope, hard confirmation gates on irreversible or spend-incurring steps, a spend/commitment ceiling the agent cannot exceed without the user.
7. **Human oversight, costed honestly**: Oversight improves avoidance but adds attentional tunneling and supervisor load. Escalate selectively on irreversible actions — a review surface the user stops reading is not oversight.
8. **Transparency disclosure**: explain relevant highlighting/default mechanisms to the user as an autonomy safeguard. Article 5 is a prohibition with specific conditions, not a general duty to disclose every nudge. Assess applicable legal notices separately with qualified counsel.

**Ethical-bound check**: (1) Is the default AI action scope the least-surprise, least-invasive option? (2) Can the user find and operate the scope controls without assistance? (3) Is the AI's behavior disclosure legible without reading a privacy policy? (4) Is factual accuracy checked whenever a persuasive generated turn is shipped (see [AI as a persuasion source](#ethical-bounds))?

**Fail signal**: high initial activation but user complaints of "the AI did something I didn't expect" — the agent's autonomy scope default was set too wide; cognitive load at consent was too high for informed choice.

**Inputs:** AI feature list with autonomy scope per feature (read / suggest / act), default state per feature (on/off), cognitive load estimate of consent/scope-setting flow (steps × decision complexity), target user's technical familiarity level.
**Rules:** Default autonomous actions to off or narrowest scope unless user has explicitly expanded; material scope decisions shown before permission is granted, with comprehension tested in the actual flow; social proof claims must cite verifiable data; agent deployment in third-party environments requires a nudge-susceptibility audit before launch; irreversible and spend-incurring agent actions require a hard confirmation gate.
**Outputs:** Default state table per AI feature (on/off, scope level, reversibility) + consent flow redesign with cognitive load score per step + nudge-susceptibility checklist for any third-party environment the agent operates in + EU AI Act Art. 5 issue list for counsel review.

---

## Workflow

1. Identify the decision point you are designing for (pricing, onboarding, retention, feature adoption, copy).
2. Use the [Decision Checklist](#decision-checklist) to identify which primitives are relevant.
3. Open the per-primitive playbook in [assets/templates/behavioral-economics/](assets/templates/behavioral-economics/) for the full definition, misuse boundary, and worked example.
4. Apply the [Ethical Bounds](#ethical-bounds) harm test to each technique before implementation.
5. For compound design problems, use the [Composition Recipes](#composition-recipes) as starting stacks.
6. Check [Misuse and Anti-Patterns](#misuse-and-anti-patterns) to confirm you are not inadvertently shipping a dark pattern.

## Local Validation Artifact

- [Operational record, worked case and regression checks](references/local-validation.md). Read before translating a mechanism into a deployment recommendation.

## Navigation

- Per-primitive playbooks: [assets/templates/behavioral-economics/](assets/templates/behavioral-economics/) (one file per primitive)
- Composition guide: [assets/templates/behavioral-economics/README.md](assets/templates/behavioral-economics/README.md)
- Recipes 1–5: [references/composition-recipes.md](references/composition-recipes.md)
- Nudge calibration and sample-size arithmetic: [references/nudge-calibration.md](references/nudge-calibration.md)
- Regulatory context (UK/EU/US): [references/regulatory-context.md](references/regulatory-context.md)
- Formal theory map: [references/formal-theory-map.md](references/formal-theory-map.md)
- Patterns, scenarios, and traps: [references/patterns-scenarios-traps.md](references/patterns-scenarios-traps.md)
- Edge-over-appetite business models: [references/patterns-scenarios-traps.md#edge-over-appetite-business-models](references/patterns-scenarios-traps.md#edge-over-appetite-business-models)
- Domain-agnostic primitives overview: [references/primitives-overview.md](references/primitives-overview.md)
- Sources: [`data/sources.json`](data/sources.json)

## Related Skills

_Consumer applied recipe layers that use these primitives link here._

- `marketing-cro` — conversion rate optimization applied recipes
- `startup-business-models` — pricing and packaging applied recipes
- `marketing-content-strategy` — copy and messaging applied recipes
- `product-management` — onboarding and feature adoption applied recipes
- `marketing-paid-advertising` — ad copy and landing page applied recipes

---

## Learnings Loop

When prior decisions or pitfalls are relevant, consult `learnings.consolidated.md` if present; use `learnings.md` only for needed history or as the available fallback. Otherwise skip both.

After applying it, if you encountered a pattern worth remembering, a mistake worth preventing, or a domain fact that surprised you, append one dated bullet to `learnings.md` via `agents-skills-feedback-loop/scripts/append_learning.py`. Do not modify `SKILL.md` itself.
