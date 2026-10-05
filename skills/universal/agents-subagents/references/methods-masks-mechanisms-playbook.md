---
description: Practical playbook for the 10 debate methods, 7 decision masks, and 22 game-theory mechanisms — when to use, how to compose, tips, and common mistakes.
last_verified: 2026-09-16
status: stable
---

# Methods, Masks & Mechanisms — Playbook

A single operator's reference for the three template families used in agent teams:

| Family | Files | What it does |
|---|---|---|
| **Debate methods** (10) | [`agents/templates/debate-methods/`](../../../../agents/templates/debate-methods/) | Restructures the team's discussion (round shape, role assignments, cognitive modes) |
| **Decision masks** (4) | [`agents/templates/decision-masks/`](../../../../agents/templates/decision-masks/) | Decorates one agent's brief without restructuring the team |
| **Game-theory mechanisms** (22) | [`foundations-game-theory/assets/templates/game-theory/`](../../foundations-game-theory/assets/templates/game-theory/) (10 incentive mechanisms) and [`foundations-team-theory/assets/templates/team-theory/`](../../foundations-team-theory/assets/templates/team-theory/) (12 shared-payoff aggregation and credit mechanisms) | Coordination, contribution, synthesis, and operating-threshold layers that span the whole run. Agent-team applied recipes: [`game-theory-agent-teams.md`](game-theory-agent-teams.md) |

Hubs already in this folder: [`game-theory-agent-teams.md`](game-theory-agent-teams.md), [`debate-quickstart.md`](debate-quickstart.md), [`negotiation-protocol.md`](negotiation-protocol.md), [`prediction-market-confidence.md`](prediction-market-confidence.md), [`principal-agent-delegation.md`](principal-agent-delegation.md). This file is the **operator's tip sheet** — when to reach for which, how to compose, and where each one fails.

## Contents

- [How the three families fit together](#how-the-three-families-fit-together)
- [Decision tree: which to pick](#decision-tree-which-to-pick)
- [Debate methods — tips & traps](#debate-methods--tips--traps)
- [Decision masks — tips & traps](#decision-masks--tips--traps)
- [Game-theory mechanisms — tips & traps](#game-theory-mechanisms--tips--traps)
- [Operating-threshold cheat-sheet](#operating-threshold-cheat-sheet)
- [Composition recipes](#composition-recipes)
- [Universal anti-patterns](#universal-anti-patterns)

---

## How the three families fit together

Think of them as **three orthogonal layers** stacked on the same team run:

```
┌────────────────────────────────────────────────────────────┐
│  GAME-THEORY MECHANISMS  (always-on, cross-cutting)        │
│  belief briefs · Shapley · synthesis protocol · thresholds  │
├────────────────────────────────────────────────────────────┤
│  DEBATE METHOD  (one per run, restructures rounds)         │
│  e.g. courtroom / dialectical / pre-mortem / six hats      │
├────────────────────────────────────────────────────────────┤
│  DECISION MASKS  (per agent, decorates their brief)        │
│  e.g. inversion on Defense Counsel · second-order on Critic│
└────────────────────────────────────────────────────────────┘
```

Rule of thumb:
- **Pick exactly one debate method** per run — they restructure rounds and don't compose with each other.
- **Layer 1–3 masks** across different agents — each agent wears at most one mask; multiple masks on different agents enrich diversity.
- **Always-on mechanisms** = #1 (belief briefs) + #4 (Shapley) + #7 (synthesis protocol). Add others as the situation demands.

---

## Decision tree: which to pick

```
Is the question NUMERIC (forecast/sizing)?
  → YES: Delphi (anonymous iteration). Skip debate, skip masks.
  → NO: continue ↓

Is the answer a COMPROMISE, not a winner?
  → YES: Negotiation (#12 ZOPA/BATNA) or Polarity Management (recurring tension).
  → NO: continue ↓

Is the question BINARY (A vs B, ship/don't ship)?
  → YES, with audit trail needed → Courtroom (PROClaim, mechanism #8).
  → YES, mutually exclusive paths → Dialectical Inquiry.
  → YES, ego-locked disagreement → Steel-Manning.
  → YES, one-sided / groupthink risk → Devil's Advocate.
  → NO: continue ↓

Is the question STRATEGIC under uncertainty?
  → 12+ month horizon, 2 axes of uncertainty → Scenario 2×2.
  → Pre-launch / pre-commitment → Pre-Mortem.
  → Stuck in one cognitive mode → Six Thinking Hats.
  → Assumptions need surfacing → Socratic Questioning.
```

Then, regardless of method:
- Add **belief briefs** (mechanism #1) so members don't duplicate.
- Add **Shapley assessment** (#4) at the end if you'll re-run this team.
- Add **confidence staking** (#11) if synthesis defaults to verbose-wins.
- Add a **mask** to any agent whose default frame is too narrow.

---

## Debate methods — tips & traps

10 methods. Each row: what it is for, the main operating rule, and the failure mode to prevent.

### 1. Courtroom (PROClaim) — `08-courtroom-proclaim.md`

| | |
|---|---|
| **Use when** | Binary claim with audit trail required (compliance, board, regulatory go/no-go) |
| **Roles** | Plaintiff, Defense, Court, Critic, Judicial Panel (3 heterogeneous judges) |
| **Operator rule** | Run **role-switching** in Round 2.5 when using the PROClaim pattern: plaintiff and defense swap to test position-anchored reasoning |
| **Failure mode** | Same model/specialization for plaintiff and defense — shared bias produces correlated errors |
| **Thresholds** | P-RAG admission = `relevance x credibility > 0.5`; novelty = `1 - max(cos)`; stop at novelty < 0.20 |
| **Be aware of** | LLMs have negativity bias — REFUTE positions converge 0.2–0.3 rounds *faster* than SUPPORT positions |

### 2. Delphi — `delphi-method.md`

| | |
|---|---|
| **Use when** | The answer is a **number** (revenue forecast, sample size, timeline, TAM) |
| **Operator rule** | Enforce anonymity ruthlessly — share only median/IQR/range, never which agent said what. Once names appear, the most senior voice anchors the group |
| **Failure mode** | Running it on binary decisions ("should we launch?" is not a Delphi question) |
| **Convergence rule** | Stop when **IQR < 20% of median**. If IQR is still wide after Round 3, that disagreement IS the signal — report it, don't force convergence |
| **Outlier rule** | A persistent outlier through 3 rounds with clear reasoning is **signal, not noise** — surface their justification in synthesis |
| **Round cap** | 3 max. Beyond that, agents stop reasoning and start averaging |

### 3. Devil's Advocate — `devils-advocate.md`

| | |
|---|---|
| **Use when** | Groupthink risk is high or consensus formed too fast |
| **Operator rule** | Assign the role to someone who would **naturally agree** with the proposal, not the team contrarian. Structural opposition only works if it's structural |
| **Failure mode** | Letting them hedge ("on the other hand…"). Enforce no-hedging |
| **Synthesis must** | Explicitly record which devil's-advocate points were **resolved / partially addressed / left open**. Unresolved = decision risk on the memo |
| **Heritage** | Catholic Church, 1587, *Promotor Fidei*; Israeli IDF "Tenth Man Rule" |

### 4. Dialectical Inquiry — `dialectical-inquiry.md`

| | |
|---|---|
| **Use when** | Two **mutually exclusive** options (monolith vs microservices, build vs buy, PLG vs sales-led) |
| **Team split** | 5 members → 2-2-1; 3 members → 1-1-1 |
| **Operator rule** | Both sides write **at full strength** in Round 1 — no balance, no hedging. A weakened thesis produces a mediocre synthesis |
| **Failure mode** | Synthesis as compromise. "A bit of A and a bit of B" loses both sides' strongest points. Pick one or propose a true third path |
| **Required round** | The cross-critique round. Without it, synthesis is built on unchallenged positions |

### 5. Polarity Management — `polarity-management.md`

| | |
|---|---|
| **Use when** | The team has debated this **more than twice** and keeps oscillating (speed vs quality, centralize vs autonomy, growth vs profit) |
| **Diagnostic** | If picking one side historically led to the other side's downsides emerging, it's a polarity, not a problem |
| **Output is not a decision** | Output is a **management system**: early warning signs per pole + shift action + review cadence |
| **Hard part** | Each group must honestly name the **downsides of their own pole** — not just praise it |
| **Failure mode** | Trying to "solve" a polarity. Polarities don't have solutions; they have ranges of healthy oscillation |

### 6. Pre-Mortem — `pre-mortem.md`

| | |
|---|---|
| **Use when** | Pre-commitment for high-stakes irreversible work (launch, migration, pricing change, fundraise) |
| **Past-tense framing is the entire technique** | "It's 12 months later, the decision failed spectacularly. Write the autopsy." Not "what could go wrong?" — that's just brainstorming and triggers optimism bias |
| **Operator rule** | Always include the punchline question: **"Which of these warning signs are already present in the current proposal?"** Without it, you have a theoretical risk list, not a decision change |
| **Synthesis ranking** | Rank failure modes by **how many independent agents surfaced them**, not by severity. Convergent discovery is the signal |
| **All-5 not 3-of-5** | Run autopsies for all members in parallel — they're written in isolation, so cost scales fine |
| **Evidence note** | Klein's HBR premortem article reports stronger failure-mode discovery than forward brainstorming; treat the exact lift as source-specific |

### 7. Scenario 2×2 — `scenario-2x2.md`

| | |
|---|---|
| **Use when** | High-uncertainty strategic decision with a 12+ month horizon |
| **Hardest step** | Picking the **two axes**. Must be: critical, uncertain, independent, bounded. Bad axes produce useless scenarios — most of the value is in axis selection |
| **Output classification** | ROBUST (works in ≥3 quadrants) / BET WITH HEDGE (2 of 4) / NARROW BET (1–2). Name the bet explicitly |
| **Required output** | Leading indicators per quadrant — the specific signals that tell you which future is emerging |
| **Failure mode** | Vague scenarios. "Things get worse" is not a quadrant — name specific market conditions, user behaviors, competitor moves |

### 8. Six Thinking Hats — `six-thinking-hats.md`

| | |
|---|---|
| **Use when** | Team is stuck in one cognitive mode (too cautious, too optimistic, too data-bound) |
| **Hats** | White (facts), Red (gut), Black (risks), Yellow (upside), Green (alternatives), Blue (process/synthesis) |
| **Operator rule** | Use **3 hats per debate, matched to the gap**: data contested → white+black+yellow; team stuck in pessimism → yellow+green+red. All 6 hats turns the memo into a checklist |
| **Failure mode** | One agent wearing multiple hats (fragments focus); synthesizer wearing a hat (breaks neutrality) |
| **Composition** | Hat assignment is **per round**, not a permanent identity. Same agent can wear different hats in different debates |

### 9. Socratic Questioning — `socratic-questioning.md`

| | |
|---|---|
| **Use when** | Assumptions need surfacing; or as cheap pre-debate scan to find if real disagreement exists |
| **Question categories** | Clarification, Assumption, Evidence, Perspective, Consequence, Meta — cover ≥3 in any round |
| **Cost** | ~2× standard round (vs ~6–8× for full debate). Cheapest way to improve reasoning quality |
| **Operator rule** | The Critic asks **questions only**. The moment they say "I think…" they've broken role. Rhetorical questions ("don't you think this will fail?") are arguments in disguise — not allowed |
| **Synthesis must** | Make the **delta** explicit: which Round 1 positions changed after the Socratic round? That delta IS the value of the method |
| **Question budget** | 5 max per round. More dilutes — agents respond superficially to many questions instead of deeply to a few |

### 10. Steel-Manning — `steel-manning.md`

| | |
|---|---|
| **Use when** | Two agents are ego-locked on opposed positions in Round 1 |
| **The move** | Agents **swap and argue the other side** as strongly as possible. Then return and revise their own position |
| **Quality test** | Would the opposing agent endorse this version of their argument? If not, you strawmanned the steel-man |
| **Failure mode** | Steel-manning then immediately refuting in the same round. Round 2A = steel-man only. Refutation only after both sides have steel-manned |
| **Required round** | Round 2B (return to original position). Without it, you have two agents arguing each other's positions with no synthesis |
| **Synthesis insight** | The "true disagreement" after steel-manning is usually **narrower** than Round 1 suggested. Name the narrowed core and the specific evidence that would resolve it |

---

## Decision masks — tips & traps

7 masks. Layer onto any agent's brief. Mask changes the *question* the agent answers, not the team shape.

### M1. Inversion — `inversion.md`

| | |
|---|---|
| **Use when** | Happy-path thinking dominates; downside under-examined |
| **The reframe** | Not "how do we succeed?" but "**what would guarantee failure?** Then avoid those actions" |
| **Required output** | At least 5 specific failure-causing actions, then check **which are already present** in the proposal |
| **Failure mode** | Treating it as a risk list. Inversion is "things that would *reliably cause* failure if done on purpose" — intentionality sharpens the thinking |
| **Pair with** | Defense Counsel in Courtroom; Black Hat in Six Hats; Pre-Mortem |

### M2. First-Principles — `first-principles.md`

| | |
|---|---|
| **Use when** | Convention-bound reasoning ("everyone uses X", "industry standard is Y") is load-bearing in the argument |
| **The move** | Separate **essential constraints** (physics, hard requirements) from **accidental conventions** (inherited from prior tools/teams) |
| **Required output** | Step 4: "what would the decision look like if you rebuilt it today with no inherited assumptions?" Without this step, you have an audit, not a decision change |
| **Failure mode** | Confusing first-principles with contrarian. Sometimes the convention is right and the analysis confirms it |
| **Pair with** | Architecture RFCs, cost reviews, technology selection |

### M3. Regret Minimization — `regret-minimization.md`

| | |
|---|---|
| **Use when** | The real question is "should we do this at all?" — or reversibility is ambiguous |
| **Step 1** | Classify: **two-way door** (cheap to walk back) or **one-way door** (irreversible/expensive)? |
| **Step 2** | Two-way → bias action, decide with 70% info. One-way → bias deliberation, demand 90% info, layer in pre-mortem + dialectical |
| **Step 3** | Check the current process matches the door type. If mismatched, change the process |
| **Failure mode** | Classifying every decision as one-way (paralysis) or every as two-way (reckless) |
| **Heritage** | Bezos 1997, Amazon's Type 1 / Type 2 framework |

### M4. Second-Order — `second-order.md`

| | |
|---|---|
| **Use when** | First-order win is being celebrated without asking what comes next; competitive responses; cascading policy effects |
| **The chain** | Level 1 → "and then what?" → Level 2 → "and then what?" → Level 3. Stop at 2–3, not at 1 |
| **Required output** | At least 2 complete chains, each going to level 3. Name **specific actors and specific moves**, not "the market reacts" |
| **Diagnostic question** | "At which level is the original benefit preserved? If neutralized by level 2, you need a different approach" |
| **Failure mode** | Stopping at level 1 (most common) or vague chaining (next most common) |
| **Watch for** | Feedback loops — second-order effects often loop back to the original decision |

### M5. Anchoring Reset — `anchoring-mask.md`

| | |
|---|---|
| **Use when** | First number, first option, or first analogy seen is dragging the analysis |
| **The reframe** | "If I had not seen [the anchor], what range / option set would I propose from scratch?" |
| **Required output** | Independent range/option **before** the anchor is reintroduced for comparison |
| **Failure mode** | Letting the anchor reappear too early; the reset is destroyed |
| **Pair with** | Estimation tasks, retrospective bias, post-incident sizing |

### M6. Base-Rate Reset — `base-rate-mask.md`

| | |
|---|---|
| **Use when** | Inside view dominates ("this project is special") and outside view is missing |
| **The reframe** | "What is the historical base rate for projects in this reference class? What's our prior before considering specifics?" |
| **Required output** | Named reference class + base rate + how this case differs (with evidence) |
| **Failure mode** | Choosing the reference class to confirm the desired conclusion. Pre-commit to the class before checking the base rate |
| **Pair with** | Forecasts, project sizing, "this time it's different" arguments |

### M7. Constitutional Mask — `constitutional-mask.md`

| | |
|---|---|
| **Use when** | Solo reviewer with hard non-negotiables (security, compliance, brand voice). No debate behind them |
| **The two passes** | Draft → critique against principles list → revise. Critique log is part of output |
| **Required output** | Revised draft + log showing which principles were tightened vs already met |
| **Failure mode** | Self-sycophancy ("9/10 on every principle") or principle bloat (>10 principles) |
| **Heritage** | Anthropic Constitutional AI (arxiv 2212.08073) |
| **Pair with** | Solo agents in `agents/`, especially `software-security-reviewer`, `qa-test-reviewer`, compliance roles |

### Layering masks across a team

| Team type | Suggested mask layout |
|---|---|
| Architecture RFC | First-Principles on lead architect + Inversion on risk reviewer + Second-Order on platform owner |
| Pricing change | Regret Minimization on synthesis owner + Second-Order on pricing-advisor + Inversion on growth-specialist |
| Migration plan | Inversion on Defense Counsel (in Courtroom) + Second-Order on platform-engineer |
| Founder blindspot | Inversion + Regret Minimization + Socratic Questioning method |
| Estimation / forecast | Anchoring Reset + Base-Rate Reset on every member |
| Solo security review | Constitutional Mask on the reviewer |

---

## Game-theory mechanisms — tips & traps

22 mechanisms. They span the whole run rather than one round. Each row: trigger, operating rule, and failure mode.

### G1. Belief-Driven Coordination (ECON) — `01-econ-belief-driven.md`

| | |
|---|---|
| **Trigger** | Always-on baseline when role overlap is likely. ECON reports higher accuracy and lower token use versus standard multi-agent debate in its benchmark; treat the numbers as benchmark-specific |
| **The move** | Pre-launch belief brief: each member's lane + what they should expect others to cover + what NOT to duplicate |
| **Operator rule** | The brief is the coordination. Cheaper and more reliable than inter-member chat |
| **Failure mode** | Generic briefs ("focus on your area"). Must name specific lanes + specific overlaps to avoid |

### G2. Adversarial Debate (heterogeneous) — `02-adversarial-debate.md`

| | |
|---|---|
| **Trigger** | Standard debate is producing confabulation consensus |
| **Round cap** | **2 max**. Agents converge to consensus regardless of correctness after ~3 rounds |
| **Agreement skip** | If members agree on >80% of points → skip debate, go to synthesis |
| **Operator rule** | Replace majority voting with **reasoning-tree audit** — trace each argument to its evidence; flag where evidence conflicts; flag where reasoning diverges from evidence |
| **Failure mode** | Homogeneous debaters. Same model = same biases = correlated errors. Use members with different specializations |

### G3. Auction-Based Routing — `03-auction-task-routing.md`

| | |
|---|---|
| **Trigger** | Static team-selection map is ambiguous (cross-domain question, novel question) |
| **Bid format** | Relevance score (0–10) + one-sentence unique contribution preview + evidence needed |
| **Operator rule** | Use historical Shapley scores as **priors for bid weighting** — agents who delivered before get heavier weight |
| **Skip when** | Standard question with clear team match, or recurring review with established team |

### G4. Shapley Contribution Scoring — `04-shapley-contribution.md` (in `foundations-team-theory/assets/templates/team-theory/`)

| | |
|---|---|
| **Trigger** | Always-on baseline (post-run) for any team that will run more than once |
| **The score** | Marginal contribution = `quality(team) − quality(team without M)` |
| **Tiers** | >30% = core (keep); 10–30% = useful but replaceable (rotate); <10% = redundant (remove) |
| **Operator rule** | Use the score to **rotate team composition by stage**. `startup-operating-system-reviewer` may add little on early-stage products but become high-value once billing, close cadence, or enterprise controls matter |
| **Failure mode** | Computing once and treating the team composition as fixed. Re-score periodically — Shapley shifts with context |

### G5. Reputation-Gated Autonomy — `05-reputation-gating.md`

| | |
|---|---|
| **Trigger** | Member track records vary; high-stakes decisions |
| **Tiers** | Proven (final-only review) / Standard (key findings) / Probationary (each claim) / Adversarial (independent confirmation) |
| **Inputs** | Shapley history (#4) + calibration history (#11) feed the tier — not set by hand |
| **Operator rule** | Build the **Vickrey rule** into briefs: "honest uncertainty is valued higher than confident guesses." Easier to be honest than to fake confidence |
| **Failure mode** | Static tiers. A member's tier should move when their evidence changes |

### G6. Cooperation/Defection — `06-cooperation-defection.md`

| | |
|---|---|
| **Trigger** | Members producing low-effort or duplicated output |
| **Defection types** | Shallow analysis · Scope dumping · Echo-chambering · Confidence inflation |
| **Detection checks** | Does output cite specific data? Does the member address the **hard** part of their brief? Is contribution unique per Shapley? Evidence-per-claim ratio? |
| **Sustaining mechanism** | Clear ownership + belief briefs + Shapley + reputation tiers. All four together close the free-riding loop |

### G7. Mechanism Design for Synthesis — `07-mechanism-design-synthesis.md`

| | |
|---|---|
| **Trigger** | Always-on baseline for synthesis |
| **Vickrey principle** | Design synthesis so each member's best strategy is **honest reporting**, not telling the synthesis owner what they want to hear |
| **Required outputs** | Decision + evidence strength per element + dissenting views (NOT suppressed) + confidence calibration + gaps |
| **What to value** | Surprising findings with evidence > confirmatory findings · Honest uncertainty > confident guesses · Specific disagreements > generic agreement · "I found nothing noteworthy" > manufactured insights |
| **Failure mode** | Suppressing dissent. Minority may be correct — suppression hides signal |

### G8. Courtroom (PROClaim) — `08-courtroom-proclaim.md`

See debate method #1 above. As a mechanism, the key features are **Progressive RAG** and a **role-switching consistency test**. Treat reported point gains as protocol-benchmark evidence, not portable constants.

### G9. Pareto-Nash — `09-pareto-nash.md`

| | |
|---|---|
| **Trigger** | Multi-objective decision (quality vs speed vs cost; security vs UX; growth vs monetization) |
| **The map** | Each member states findings along their objective; synthesis owner maps the Pareto frontier |
| **Operator move** | Remove **dominated options** (worse on ALL objectives) before presenting. Presenting dominated options wastes decision-maker attention |
| **Final output** | Pareto-optimal options with **explicit tradeoffs named**: "Option A beats B on growth but loses on risk — here's what you're trading" |
| **Skip when** | Single-objective decision (correctness in code review, execution in feature delivery) |

### G10. Evolutionary Coordination Search — `10-alphaevolve.md`

| | |
|---|---|
| **Trigger** | High-frequency teams (daily-weekly cadence) with measurable quality signal |
| **Cost** | Many runs per generation — only worth it for the `expert-board` growth mode, `software-code-review-board`, `dev-feature-delivery`, and similar work |
| **Skip when** | Monthly cadence (hand-tuning is cheaper); no fitness signal; pre-launch (evolve only after baseline) |
| **Operator rule** | Use **Pareto frontier** (quality + cost) as the keep-criterion, not single-metric quality. Otherwise the LLM evolves more verbose teams |

### G11. Prediction Market / Confidence Betting — `11-prediction-market.md`

| | |
|---|---|
| **Trigger** | Synthesis defaults to volume — verbose agents dominate |
| **The mechanic** | Each agent gets **100 confidence points per run**. Allocates across claims |
| **Calibration buckets** | 80+ stake = strong claim; 40-79 = medium confidence; <40 = weak claim |
| **Synthesis weighting** | Weight by stake, not by length. **A 90-point claim from one agent > a 30-point claim from three agents** |
| **Failure mode** | Letting agents spread points evenly (defeats the purpose). Force rank-ordering |
| **Long-game** | Track calibration across runs. Well-calibrated agents get higher reputation tiers (#5) |

### G12. Negotiation (ZOPA/BATNA) — `12-negotiation-zopa-batna.md`

| | |
|---|---|
| **Trigger** | The right answer is a **compromise**, not a winner — debate would force a false binary |
| **Phase 1** | Each agent states: ideal outcome, BATNA (minimum), priority ranking (which constraint to relax first) |
| **Phase 2** | Map ZOPA. If exists → propose Nash point (joint utility max). If not → tightest-BATNA agent relaxes lowest-priority constraint |
| **Phase 3** | One round of accept/counter/dealbreaker. If no deal: escalate to user with ZOPA map (don't loop) |
| **Operator rule** | Prefer value-framed BATNAs over pure number-framed BATNAs when the tradeoff is qualitative |
| **Evidence note** | Practitioner negotiation datasets suggest value framing can improve joint utility; verify before treating this as a general law |

### G13. Reasoning-Tree Audit — `13-reasoning-tree-audit.md`

| | |
|---|---|
| **Trigger** | Members converge on confident-but-wrong consensus; majority-vote synthesis is unsafe |
| **The move** | Synthesis owner reconstructs each member's reasoning tree, finds the **First Point of Disagreement**, picks by evidence quality at that node — not by vote count downstream |
| **Operator rule** | Disagreement at depth 1 = different framing → restate the question. Disagreement at depth 3+ = different evidence weighting → audit the source nodes |
| **Failure mode** | Auditing only the final answer. The leaf is downstream of correlated errors; the branch point is upstream |

### G14. Per-Claim Credibility Scoring — `14-credibility-scoring.md`

| | |
|---|---|
| **Trigger** | Single-claim failure modes (out-of-domain claim, prompt injection, hallucinated step) that reputation-gating can't catch — reputation tracks members, this tracks **claims** |
| **The move** | Each claim gets `credibility = evidence_quality × corroboration`. Claims below threshold are flagged regardless of which member made them |
| **Operator rule** | Use this **in addition to** reputation gating, not instead of. A high-rep member can still produce a low-credibility claim on a single run |
| **Failure mode** | Letting member identity contaminate per-claim scoring — keep the claim audit blind to who said it |

### G15. Generative Social Choice — `15-generative-social-choice.md`

| | |
|---|---|
| **Trigger** | Multi-stakeholder buy-in matters; averaging or loudest-wins is erasing minority evidence |
| **The move** | Generate K candidate synthesis statements, then pick the one that maximizes the **minimum** stakeholder approval (maximin), not the mean |
| **Operator rule** | Use when "the answer most people can live with" beats "the answer the majority prefers" — common for org decisions, deprecation calls, policy changes |
| **Failure mode** | Treating maximin as a tie-breaker. It's the primary criterion; mean approval is the tie-breaker |

### G16. Meta-Debate Role Routing — `16-meta-debate-routing.md`

| | |
|---|---|
| **Trigger** | Cross-domain debates where the "obvious" specialist isn't actually the best plaintiff/defense/judge for *this* claim |
| **The move** | Two-stage: members propose role assignments → peer-review picks the assignment. Dynamic Role Assignment, not static |
| **Operator rule** | Cap stage-1 to 1 round. The point is to surface non-obvious fits, not run a full meta-debate |
| **Failure mode** | Letting role-routing become its own debate. If stage-1 takes more than one round, default to static assignment and move on |

### G17. Online Shapley-Driven Prompt Evolution — `17-online-shapley-prompt-evolution.md` (in `foundations-team-theory/assets/templates/team-theory/`)

| | |
|---|---|
| **Trigger** | High-frequency team (50+ runs) where weak members need targeted prompt tuning **without** disturbing strong ones |
| **The move** | Shapley contribution per member → mutate only sub-threshold members' prompts → A/B test mutation against current prompt |
| **Operator rule** | Lock the team protocol (roles, debate rule, synthesis order). Mutate prompts only. Hysteresis band ±20% to prevent mutation cascade |
| **Failure mode** | Reward hacking the Shapley signal (members claim credit for synthesis findings) — synthesis owner must attribute findings to source member explicitly |
| **Composes well with** | G4 Shapley (the fitness signal) + G5 reputation (long-term retention) + G2 adversarial debate spot-check (catches sycophancy drift) |

### G18. Beyond Majority Voting (BMV) — `18-beyond-majority-voting.md`

| | |
|---|---|
| **Trigger** | Best-of-N synthesis over 3+ heterogeneous candidates where majority vote risks suppressing a minority-correct answer |
| **The move** | **Optimal Weight** (confidence × historical calibration) + **Inverse Surprising Popularity** (non-supporters rate minority candidates' plausibility; high plausibility upweights minority) |
| **Operator rule** | Starting `lambda = 0.5` for ISP weight (untuned, unsourced). Try higher where minority-correct outcomes are common (security, edge cases), lower where consensus is usually right; tune on held-out cases |
| **Failure mode** | Confidence theater (agents always say 0.9). Calibrate first via G11 + CritiCal. Also: ISP spam loop is O(N²); cap minority candidates at 3 per round |
| **Composes well with** | G02 adversarial debate (BMV as synthesis), G11 prediction market (stakes feed OW), G13 reasoning-tree audit (ISP plausibility check reuses audit interface) |

### G19. Radial Consensus Score (RCS) — `19-radial-consensus-score.md`

| | |
|---|---|
| **Trigger** | Best-of-N over 5+ candidates where members produce lexically diverse but semantically equivalent answers (open-ended generation, summaries, naming, design proposals) |
| **The move** | Embed all candidates → compute centroid → pick candidate with highest cosine similarity to centroid. Outliers logged (not discarded) for operator review |
| **Operator rule** | Lock the embedding model for the session. Normalize embeddings before averaging (length bias). N ≥ 5 minimum — centroid unstable below 5 |
| **Failure mode** | Outlier blindness (discarding the minority-correct candidate). Centroid collapse when all agents share a system prompt — force prompt diversity |
| **Composes well with** | G02 adversarial debate (cluster picks centroid; outliers feed second debate round), G18 BMV (RCS clusters, BMV-ISP evaluates outliers), G13 audit (RCS-cluster the verdicts into a consensus diagnosis) |

### G20. Conformal Social Choice — `20-conformal-social-choice.md`

| | |
|---|---|
| **Trigger** | High-stakes team verdict where wrong consensus could trigger an irreversible or customer/regulator-visible action |
| **The move** | Aggregate member probability distributions, calibrate against shadow/history cases, and act only when the prediction set is singleton |
| **Operator rule** | Multi-answer set means escalate or gather evidence. Treat escalation as the safety output, not as a failed run |
| **Failure mode** | Consensus-as-authorization: agents agree, so the system acts without a calibrated refusal boundary |
| **Composes well with** | G11 prediction market (probability elicitation), G13 reasoning-tree audit (candidate actions), G15 social choice (stakeholder-aware candidates) |

### G21. Attested Delegation Contracts — `21-attested-delegation-contracts.md`

| | |
|---|---|
| **Trigger** | Delegate pool crosses a trust boundary: plugin, MCP server, cloud agent, external service, marketplace agent, or dynamic worker |
| **The move** | Filter by attested identity/capability, then issue a bounded contract with objective, authority, budget, acceptance criteria, and typed failure policy |
| **Operator rule** | Self-claimed quality is never a routing weight. Use verified outcomes for reputation updates |
| **Failure mode** | Provenance paradox: inflated quality claims attract work and the router selects the wrong delegate |
| **Composes well with** | G03 auction routing (after eligibility filter), G05 reputation gating (verified outcomes only), G14 credibility scoring (claim-level evidence checks) |

### G22. Coalition Formation Routing — `22-coalition-formation-routing.md` (in `foundations-team-theory/assets/templates/team-theory/`)

| | |
|---|---|
| **Trigger** | 6+ members, department-style team, or distinct workstreams that overload a flat panel |
| **The move** | Form stable subteams around workstreams, run coalition-local analysis, then synthesize coalition leads |
| **Operator rule** | Coalition by evidence dependency, not org chart. Check every load-bearing workstream has an owner |
| **Failure mode** | Flat-panel overload: duplicate work, unstable alliances of evidence, and a synthesis owner absorbing every raw conflict |
| **Composes well with** | G01 belief lanes (per coalition), G04 Shapley (coalition contribution), G20 act/escalate (final high-stakes coalition verdict) |

---

## Operating-threshold cheat-sheet

The library has only a handful of literal numbers. Use these as starting thresholds, not universal truths. Override with run-specific calibration and source evidence.

| Threshold | Source | Value | What it controls |
|---|---|---|---|
| **Confidence stake bucket** | #11 prediction market | 80+ / 40-79 / <40 | Synthesis weighting by conviction; do not present as guaranteed accuracy |
| **Shapley contribution tier** | #4 | >30% / 10–30% / <10% | Keep core / rotate / remove |
| **Debate round cap** | #2 adversarial debate | 2 (extend at divergence only) | Stops false convergence at round 3+ |
| **Skip-debate threshold** | #2 | Members agree on >80% | Don't debate when there's nothing to debate |
| **P-RAG evidence admission** | #8 courtroom | `relevance × credibility > 0.5` | Filters incoming evidence |
| **P-RAG novelty floor** | #8 | `novelty(d) = 1 − max(cos(e_d, e_pool))`, stop at < 0.20 | Stops evidence loop when nothing new is found |
| **P-RAG iteration cap** | #8 | 3 cycles | Hard stop |
| **Delphi convergence rule** | Delphi method | IQR < 20% of median | Stop estimation rounds |
| **Delphi outlier cutoff** | Delphi method | Outside 1.5× IQR | Outlier must justify position with specific evidence |
| **Delphi round cap** | Delphi method | 3 max | Beyond, agents regress to mean |
| **Socratic question budget** | Socratic | 5 max per round | More dilutes focus |
| **Heterogeneity rule** | #2, #8 | Plaintiff/defense use different specs | Prevents correlated bias errors |
| **Critic scoring weights** | #8 courtroom Round 2 | logic 0.4 · novelty 0.3 · rebuttal 0.3 | Scores both sides on independent axes |
| **Judge panel size** | #8 courtroom | 3 heterogeneous judges | Reduces single-judge bias; reported lift is protocol-specific |
| **Anonymity invariant** | Delphi | Names never attached to estimates | Prevents authority anchoring |

The **30%/10% Shapley tiers** and **80/40 confidence buckets** are local operating heuristics. The **0.5 admission and 0.20 novelty** thresholds come from the PROClaim protocol and should still be rechecked before high-stakes use.

---

## Composition recipes

Pre-built combinations for common situations. Each is one debate method + a few mechanisms + (optional) masks.

### Recipe 1: High-stakes irreversible decision

```
Decision masks: Regret Minimization (synthesis owner) + Inversion (one challenger)
Debate method:  Pre-Mortem
Mechanisms:     #1 belief briefs · #4 Shapley · #7 synthesis protocol · #11 confidence stakes

Why: Regret-min sorts the door type, Pre-Mortem flips to past-tense to bypass optimism,
     Inversion specifically asks "what would guarantee failure", confidence stakes prevent
     verbose-wins synthesis.
```

### Recipe 2: Binary claim verification with audit trail

```
Decision masks: Inversion (Defense Counsel) + First-Principles (Critic)
Debate method:  Courtroom (PROClaim)  — IS mechanism #8
Mechanisms:     #1 belief briefs · #4 Shapley · #7 synthesis · #11 confidence

Why: Courtroom + role-switching catches position-anchored reasoning;
     P-RAG + novelty floor prevents evidence stagnation;
     three heterogeneous judges beat single judge by 3.3pp.
```

### Recipe 3: Multi-objective tradeoff (no clear winner)

```
Decision masks: Second-Order on each objective owner
Debate method:  none (negotiation is its own protocol)
Mechanisms:     #9 Pareto-Nash + #12 ZOPA/BATNA + #11 confidence stakes

Why: Pareto frontier removes dominated options; ZOPA/BATNA bargains within the frontier;
     value-framed BATNAs produce higher joint utility than number-framed.
```

### Recipe 4: Numeric forecast / sizing

```
Decision masks: none
Debate method:  Delphi
Mechanisms:     anonymity is the entire mechanism (variant of #1 belief-driven)

Why: Anonymity prevents authority anchoring. Run all 5 members in every round.
     Stop when IQR < 20% of median. Outliers are signal, not noise.
```

### Recipe 5: Architecture / RFC

```
Decision masks: First-Principles (architect) + Second-Order (platform owner) + Inversion (risk)
Debate method:  Dialectical Inquiry (A vs B path)
Mechanisms:     #1 belief briefs · #4 Shapley · #7 synthesis · #2 reasoning-tree audit

Why: First-principles strips inherited convention, second-order chains downstream
     coordination cost, dialectical forces both paths to full strength,
     reasoning-tree synthesis catches confabulation consensus.
```

### Recipe 6: Recurring tension that won't resolve

```
Decision masks: Regret Minimization (to confirm it's not actually a one-time call)
Debate method:  Polarity Management
Mechanisms:     no game-theory layering — output is a management system, not a synthesis

Why: Polarity output is early warning signs + shift action + review cadence.
     Layering Shapley/synthesis on top would imply you're trying to "decide" the polarity,
     which is the main failure mode of polarity management.
```

### Recipe 7: Founder blindspot review / strong intuition + thin evidence

```
Decision masks: Inversion + Regret Minimization
Debate method:  Socratic Questioning
Mechanisms:     #11 confidence stakes (forces calibration on founder's claims)

Why: Socratic deepens reasoning at ~2× cost vs 6–8× for full debate.
     Confidence stakes force the founder to put numbers on intuition.
     Regret minimization checks the door type before commitment.
```

### Recipe 8: Default for daily-cadence team (code review, feature delivery)

```
Decision masks: as needed per change
Debate method:  none by default; Devil's Advocate when groupthink risk fires
Mechanisms:     #1 belief briefs · #4 Shapley · #7 synthesis · (#10 evolutionary search eventually)

Why: High-frequency teams should run lean. The always-on triple is enough baseline.
     Evolutionary coordination search becomes worth it only after many runs with accumulated quality data.
```

---

## Universal anti-patterns

Patterns that fail across all three families. Catch them before launch.

| Anti-pattern | Diagnosis | Fix |
|---|---|---|
| All members read same context, produce same analysis | Pooling equilibrium — no belief differentiation | Belief briefs (G1); each member knows their lane |
| Debate runs every time, even on agreement | Wasted cost on consensus cases | Debate-on-trigger; >80% agreement → skip to synthesis |
| Majority vote in synthesis | LLMs share biases — correlated errors pass | Reasoning-tree audit (G2); trace arguments to evidence |
| One member dominates by being verbose | Volume-wins synthesis | Confidence stakes (G11); weight by conviction not length |
| Synthesis suppresses dissent | Minority may be correct — suppression hides signal | Required dissent section in output (G7) |
| No contribution tracking | Free-riding undetected | Shapley assessment (G4) after each run |
| Same team for all stages of a product | Context-blind composition | Use Shapley + auction (G3) to rotate by stage |
| Method picked by habit, not fit | Wrong tool for the question shape | Run the [decision tree](#decision-tree-which-to-pick) before launch |
| Mask added "for completeness" | Mask without a target frame becomes overhead | Only mask when a specific frame (optimism, convention, irreversibility, cascading) is the gap |
| Heterogeneity ignored in debate | Same model = correlated errors | Plaintiff/defense MUST differ in specialization or model |
| Synthesis owner wears a hat / argues a position | Breaks neutrality | Synthesis stays neutral. If you need them in the debate, they're not the synthesizer |
| Thresholds used without calibration tracking | One-shot confidence is noisy | Track calibration over runs; feed into reputation tiers |

---

## Where each piece lives in the repo

```
agents-subagents/
├── references/
│   ├── methods-masks-mechanisms-playbook.md   ← THIS FILE
│   ├── game-theory-agent-teams.md             — mechanism hub (anti-patterns, manifest fields)
│   ├── debate-quickstart.md                   — operational setup (CC / Codex / MCP)
│   ├── negotiation-protocol.md                — full ZOPA/BATNA spec
│   ├── prediction-market-confidence.md        — full confidence-staking spec
│   └── principal-agent-delegation.md          — full reputation-tier spec
└── agents/templates/
    ├── debate-methods/        — 10 method playbooks (one per file)
    └── decision-masks/        — 7 mask overlays
```

The 22 mechanism playbooks are not in this skill: 10 incentive mechanisms live in `foundations-game-theory/assets/templates/game-theory/`, and the 12 shared-payoff aggregation and credit mechanisms live in `foundations-team-theory/assets/templates/team-theory/`.

Convention: per-method/mask/mechanism playbooks live under `agents/templates/`; cross-cutting hub content (like this file) lives under `references/`.

---

## Sources (deduplicated across all three families)

Treat primary papers and official docs as stronger evidence than practitioner posts or secondary summaries. Effects below are stated as direction only; read the source for magnitudes, and never copy a reported gain into a launch prompt as a guarantee.

- **MAST** (NeurIPS 2025): 14-mode failure taxonomy for multi-agent LLM systems (Cemri et al., 2025): specification/design failures are the largest category, then inter-agent misalignment, then verification. Cross-reference: [`mast-failure-taxonomy.md`](mast-failure-taxonomy.md). [arxiv:2503.13657](https://arxiv.org/abs/2503.13657)
- **HiveMind** (2025): online Shapley-driven prompt evolution for live teams. Source for mechanism #17. [arxiv:2512.06432](https://arxiv.org/abs/2512.06432)
- **FAIRGAME** (2026): payoff-scaled iterated PD + Public Goods probes for measuring defection tendency before deployment. Cited in mechanism #6.
- **Talk Isn't Always Cheap** (2025) + **Persuasion-driven adversarial influence** (Nature Sci Reports 2026): documented cases of debate degrading below single-agent baselines. Source for "When NOT to Debate" anti-triggers in [`debate-quickstart.md`](debate-quickstart.md). [arxiv:2509.05396](https://arxiv.org/abs/2509.05396)
- **Adaptive stability detection** (OpenReview 2026): Beta-Binomial + KS test for non-numeric debate convergence. Source for the adaptive stopping rule in [`debate-quickstart.md`](debate-quickstart.md).
- **ECON** (ICML 2025): Bayesian Nash equilibrium for multi-LLM coordination; reports accuracy gains over debate baselines (token savings are unverified — check the full paper). [arxiv:2506.08292](https://arxiv.org/abs/2506.08292)
- **A-HMAD**: adaptive heterogeneous multi-agent debate; claimed accuracy and factual-error gains are unverified (no primary source located) — do not cite them.
- **PROClaim** (2026): courtroom-style multi-agent debate with Progressive RAG and role-switching; reports gains over standard debate on its benchmark. [arxiv:2603.28488](https://arxiv.org/html/2603.28488v1)
- **AgentAuditor**: reasoning-tree audit replacing majority voting.
- **ShapleyFlow / AgentSHAP**: Shapley values for cooperative agent contribution.
- **AlphaEvolve-style search**: use only as an analogy for evolving team rules against a measured fitness function unless a primary source is attached.
- **Wisdom of the Silicon Crowd** (Science Advances, 2024): LLM ensemble prediction.
- **Conformal Social Choice** (2026): calibrated act/escalate layer for debate outputs. Source for mechanism #20. [arxiv:2604.07667](https://arxiv.org/abs/2604.07667)
- **Provenance Paradox** (2026): delegation contracts and attested identity for cross-trust routing. Source for mechanism #21. [arxiv:2603.18043](https://arxiv.org/abs/2603.18043)
- **Coalition Formation in LLM Agent Networks** (2026): stable coalition formation for large LLM agent teams. Source for mechanism #22. [arxiv:2604.14386](https://arxiv.org/abs/2604.14386)
- **Anti-collusion mechanisms for multi-agent AI** (2026): monitoring, sanctions, leniency, and governance controls for collusion risk in multi-agent AI systems.
- **Herle 2026**: practitioner AI-negotiation dataset; useful as a heuristic source for value-framed BATNAs, not a general benchmark.
- **Klein 2007** (HBR): pre-mortem method; prospective hindsight surfaces more failure modes than forward brainstorming.
- **Mason & Mitroff 1981**: dialectical inquiry adaptation for strategy.
- **Johnson 1992**: Polarity Management.
- **Wack 1985**: Scenario Planning at Royal Dutch Shell.
- **de Bono 1985**: Six Thinking Hats.
- **Dennett 2013**: Steel-manning formalization in *Intuition Pumps*.
- **Janis 1972**: *Groupthink* — devil's advocate as structural antidote.
- **Bezos 1997**: Regret Minimization framework.
- **Munger 1995**: Inversion ("invert, always invert" — adapted from Jacobi).
- **Marks 2011**: Second-Order thinking in *The Most Important Thing*.
- **Feynman / Aristotle**: First-Principles reasoning.
- **Paul & Elder 2002**: Six Socratic question types.
