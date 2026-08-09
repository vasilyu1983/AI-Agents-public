# Behavioral Economics Primitives — Composition Guide

16 domain-agnostic behavioral-economics and behavior-design primitives. Each file is a standalone playbook (Definition / When to use / Misuse boundary / Inputs / Outputs / Failure modes / Worked example / Sources). Cross-cutting guidance — primitives overview, anti-patterns, decision checklist — lives in [`../../../references/primitives-overview.md`](../../../references/primitives-overview.md).

Primitives **1–11** cover decision-time effects (framing, anchoring, choice, option set). Primitives **12–16** cover repetition-time effects (habit formation, reinforcement, working memory, contextual retrieval, planned action) — the canonical mechanisms behind retention and behavior change.

**Ethical obligation**: Every primitive carries a "Misuse boundary" subsection. Read it before applying any technique. Variable-ratio reinforcement (#13) and engineered habit loops (#12) are the highest-risk levers; both have explicit harm-test gates. Consumer applied recipe layers (CRO, business models, content strategy, product management, paid advertising) are the downstream application layer — these primitives are the upstream canon.

---

## Primitives

| # | File | Core Behavioral Mechanism |
|---|------|--------------------------|
| 1 | [01-prospect-theory.md](01-prospect-theory.md) | Gains/losses evaluated relative to reference point; S-shaped value function |
| 2 | [02-loss-aversion.md](02-loss-aversion.md) | Losses ~2× more powerful than equivalent gains (range ~1.3–2.0×; 2.25 is an upper bound) |
| 3 | [03-anchoring.md](03-anchoring.md) | First number seen biases all subsequent numerical judgments |
| 4 | [04-defaults.md](04-defaults.md) | Strong inertia toward pre-set options; opt-out >> opt-in |
| 5 | [05-social-proof.md](05-social-proof.md) | Others' behavior resolves uncertainty about correct action |
| 6 | [06-scarcity.md](06-scarcity.md) | Limited availability increases perceived value |
| 7 | [07-hyperbolic-discounting.md](07-hyperbolic-discounting.md) | Present bias: immediate rewards disproportionately preferred (β-δ model) |
| 8 | [08-mental-accounting.md](08-mental-accounting.md) | Money treated differently by source, category, and temporal framing |
| 9 | [09-choice-architecture.md](09-choice-architecture.md) | Presentation context alters which option is selected |
| 10 | [10-dual-system.md](10-dual-system.md) | System 1 (fast, automatic) vs System 2 (slow, deliberate) |
| 11 | [11-decoy-effect-asymmetric-dominance.md](11-decoy-effect-asymmetric-dominance.md) | Dominated third option shifts preference toward its dominator |
| 12 | [12-habit-loop.md](12-habit-loop.md) | Cue → routine → reward; basal-ganglia stimulus-response system takes over from goal-directed control |
| 13 | [13-reinforcement-schedules.md](13-reinforcement-schedules.md) | Schedule type (FR/VR/FI/VI), not just reward, governs acquisition and resistance to extinction |
| 14 | [14-cognitive-load-working-memory.md](14-cognitive-load-working-memory.md) | Working memory ~4 novel chunks; intrinsic / extraneous / germane load decomposition |
| 15 | [15-context-dependent-retrieval.md](15-context-dependent-retrieval.md) | Encoding specificity; behaviors bound to the cues present at learning collapse on context shift |
| 16 | [16-implementation-intentions.md](16-implementation-intentions.md) | User-authored if-then plans bind cue to response; meta-analytic d ≈ 0.65 |

---

## Composition Recipes

### Pricing Page Packaging

**Problem**: 3-tier pricing page with low conversion on the target (middle) tier.

**Stack**:
1. Anchoring (#3): High-price tier shown first.
2. Decoy effect (#11): Lowest tier is dominated by the middle tier on key dimensions.
3. Loss aversion (#2): Middle tier framed as what users get to keep, not what they gain.
4. Choice architecture (#9): Middle tier highlighted; "Most Popular" label (accurate).
5. Ethical-bound check: Is the middle tier genuinely the best option for the modal user?

### Onboarding Default Sequence

**Problem**: Low feature adoption; users complete sign-up but don't configure the product.

**Stack**:
1. Defaults (#4): Pre-select the configuration most users benefit from.
2. Hyperbolic discounting (#7): Quick-start reward now; deeper setup prompted at Day 3.
3. Social proof (#5): "Most teams start with X integration."
4. Dual-system (#10): One decision per screen; reduce System 2 load.
5. Ethical-bound check: Are pre-selected options genuinely good for this user?

### Churn Prevention Intervention

**Problem**: User initiates cancellation; intervention needed without coercion.

**Stack**:
1. Loss aversion (#2): Show real assets at risk (data, integrations, team content).
2. Mental accounting (#8): Reframe annual cost as daily rate alongside their usage data.
3. Hyperbolic discounting (#7): Offer a pause option as a commitment device.
4. Social proof (#5): Real cohort data on outcomes for users who reconsidered.
5. Ethical-bound check: Cancel path must be as easy as the pause path.

### Trial-to-Paid Conversion

**Problem**: Free trial ends; user has not converted.

**Stack**:
1. Loss aversion (#2): Show what they will lose at expiry (specific data, features, integrations).
2. Prospect theory (#1): Frame upgrade as preventing loss, not acquiring new features.
3. Anchoring (#3): Show annual plan total alongside monthly alternative.
4. Defaults (#4): Pre-select the annual plan if it's genuinely better value for typical users.
5. Ethical-bound check: Trial expiry effects must match what is disclosed in trial onboarding.

### Retention Beyond Week 4 (Habit Formation)

**Problem**: Strong week-1 activation; sharp dropoff at week 2–4 once motivation fades.

**Stack**:
1. Habit loop (#12): Identify a stable user-side cue (calendar event, time of day, preceding routine action). Bind the load-bearing behavior to it.
2. Implementation intentions (#16): Prompt the user to author an if-then plan during activation. User authors; you provide templates.
3. Reinforcement schedules (#13): Default to fixed-interval daily / fixed-ratio weekly. Reward = the user's real outcome being legible. No variable-ratio gloss.
4. Cognitive load (#14): Cue-triggered surface ≤4 novel chunks. Above that, the user reverts to goal-directed mode and the habit doesn't form.
5. Ethical-bound check: User authored the cue; cue is on a surface they control; reward reflects their stated goal, not a substitute counter.

### Migration / Redesign Without Retention Collapse

**Problem**: Major UI or platform change risks breaking the cue surface that triggers existing habits.

**Stack**:
1. Context-dependent retrieval (#15): Pre-redesign cue audit per load-bearing behavior. Preserve the dominant cue across at least one full retention cycle.
2. Habit loop (#12): Distinguish goal-directed from stimulus-response behaviors. The latter are most fragile to cue changes.
3. Cognitive load (#14): Don't force expert chunking patterns to be relearned. Honour learned chunks; offer the redesign as opt-in initially.
4. Implementation intentions (#16): For users whose cue you must remove, offer to re-anchor — let them author a new if-then plan tied to the new cue.
5. Ethical-bound check: Migration framed as user benefit, not platform optics. Lapsed-user reactivation distinguishes "lost the cue" from "left the product."

### Reactivation of Dormant Users

**Problem**: 90+ day dormant cohort; generic "we miss you" emails fail.

**Stack**:
1. Context-dependent retrieval (#15): Treat dormant users as a re-onboarding cohort. The original retrieval cues have decayed.
2. Habit loop (#12): Rebuild cue → routine → reward; do not assume the prior habit will resume.
3. Implementation intentions (#16): Offer the user to author a fresh if-then plan tied to a current routine of theirs (not the routine they had a year ago).
4. Loss aversion (#2): Used only when the user has real assets at stake (data, account state). Do not fabricate loss.
5. Ethical-bound check: Distinguish "dormancy because cue collapsed" from "dormancy because user opted out." Respect the second.

### Comparative Calibration (Megastudy Approach)

**Problem**: You want to deploy a behavioral intervention but don't know which mechanism will dominate for your population. Sequential A/B testing of one variant at a time inflates the apparent winner's effect size and is slow.

**When to use**: Scalable delivery channel (email, app push, in-product message) with a shared, objectively measured outcome metric. High uncertainty about which mechanism will work. Sample large enough for ≥3 simultaneous arms (rough guide: 5,000+ per arm for detecting d ≈ 0.10).

**Stack**:
1. Design ≥3 variants testing distinct behavioral mechanisms (e.g., one loss-framed, one social-proof, one implementation-intention prompt). Do not test copy variants of the same mechanism — test distinct primitives.
2. Assign all variants simultaneously against a shared control and a single primary outcome metric.
3. Score variants on effect size and cost-effectiveness, not just statistical significance. The best-on-effect variant in a single A/B trial is typically upward-biased; the megastudy corrects this by providing a direct comparator.
4. After identifying the dominant mechanism in your population, then optimise copy/timing within that mechanism.
5. Ethical-bound check: All variants pass the harm test independently. Do not use the simultaneous design to run any variant that wouldn't be approved in isolation.

**Fail signal**: All variants show the same direction of effect as the control — check that control is a true no-treatment baseline, not a weak incumbent.

**Source**: Duckworth, A. L. & Milkman, K. L. (2022). A guide to megastudies. _PNAS Nexus_, 1(5). DOI: 10.1093/pnasnexus/pgac214.

### Sludge Audit

**Problem**: Conversion or uptake is lower than expected and you suspect friction in the user journey, but you don't know where it concentrates.

**When to use**: Before launch of a new flow, or as a diagnostic on an existing flow with unexplained abandonment. Especially valuable in compliance/onboarding/benefit-access flows where even minor friction causes material harm.

**Stack**:
1. **Behavioural journey map**: enumerate every distinct step a user must complete from intent to outcome. Include hidden steps (account verification, document upload, waiting periods).
2. **Time-per-step estimate**: measure or estimate the time each step takes. Steps that take longer than expected are candidates.
3. **Friction scoring per step**: for each step, score four cost types — (a) search cost (information clarity), (b) decision cost (option clarity), (c) cognitive cost (mental effort), (d) emotional cost (stigma, anxiety, frustration). Use a simple 1–3 scale per dimension.
4. **Ranked removal list**: sort steps by total friction score and feasibility of removal. Prioritise the top 2–3 as removal or simplification candidates.
5. **Measure impact**: instrument before/after on the primary outcome metric. A single high-friction step can halve uptake (Grieder et al. BPP 2024 field evidence).
6. Ethical-bound check: Friction removal must not inadvertently remove informed-consent steps or legally required disclosures. Audit which steps serve user protection before classifying them as removable sludge.

**Fail signal**: Total friction score looks low but abandonment is high — check for hidden asynchronous steps (email confirmation, manual review wait times) that don't appear in the synchronous journey map.

**Source**: OECD (2024). Fixing Frictions: Sludge Audits Around the World. Public Governance Policy Paper. OECD OPSI / International Sludge Academy. 16 governments, 14 countries.

---

## Related

- [`../../../references/primitives-overview.md`](../../../references/primitives-overview.md) — cross-cutting overview, anti-patterns, decision checklist
- [`../../../data/sources.json`](../../../data/sources.json) — primary source references
