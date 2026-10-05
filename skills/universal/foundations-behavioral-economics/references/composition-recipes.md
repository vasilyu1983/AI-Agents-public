# Composition Recipes 1–5: Compound Design Patterns

Recipe 6 (AI-assistant UX guardrails) stays in `SKILL.md` — it is the skill's most novel content. Recipes 1–5 below are compound stacks for pricing, onboarding, churn, habit formation, and migration. Apply the [Ethical Bounds](../SKILL.md#ethical-bounds) harm test to every step before shipping.

### Recipe 1: Pricing Page Packaging

**Goal**: maximize conversion on a 3-tier pricing page while staying ethical.

**Stack**:
1. **Anchoring (#3)**: Show the highest tier first (or an "Enterprise" row), so the middle tier anchors low by comparison.
2. **Decoy effect (#11)**: If using a true asymmetric-dominance decoy, it must be dominated by the target tier on *every* relevant dimension and not dominated by the cheaper tier — see the [decoy template](../assets/templates/behavioral-economics/11-decoy-effect-asymmetric-dominance.md) and its fragility caveat before relying on this. If the lower tier is merely inferior on one dimension (the common case), call this "good-better-best packaging," not a decoy — it is a different, less fragile mechanism and does not need the decoy's ethical gate.
3. **Loss aversion (#2)**: Frame the middle tier as "everything you need to avoid missing out on [core value]", not just "get more features".
4. **Choice architecture (#9)**: Highlight the recommended tier; reduce visual noise on the others.
5. **Ethical-bound check**: Is the recommended (target) tier genuinely best for the modal customer? If a true decoy is used, is it a real, purchasable option rather than a phantom that disappears when selected? Do not test the decoy's own rationality: a dominated option has no rational use case by construction, so the test sits on the target.

**Fail signal**: conversion goes up but refund/churn increases — users were pushed to a tier above their actual need.

**Inputs:** 3 tier prices + feature lists, modal-customer persona (role, primary job-to-be-done, willingness-to-pay estimate), target conversion metric (e.g. % selecting middle tier).
**Rules:** Anchor on the highest tier first (or an Enterprise row); if using a true decoy, it must be dominated by the target tier on every dimension the modal customer cares about, and not dominated by the cheaper tier; ethical gate — confirm the recommended tier is genuinely best for the modal customer before publishing; if the gate fails, revise the tier structure, not the framing.
**Outputs:** Revised tier display order + highlighted/recommended tier label + ethical gate pass/fail verdict + a hypothesis and local test plan (do not quote a predicted lift number as a forecast — see [nudge-calibration.md](nudge-calibration.md)).

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
**Outputs:** Revised churn-prevention copy using real loss inventory + daily-rate reframe if applicable + recommended intervention sequence (loss frame → pause offer → social proof → cancel CTA) + local randomized comparison of truthful variants, measuring save rate, comprehension, pressure, and cancellation completion; λ supplies no conversion forecast (see [nudge-calibration.md](nudge-calibration.md)).

### Recipe 4: Retention Beyond Week 4 (Habit Formation)

**Goal**: convert week-1 activation into durable usage past the motivation cliff.

**Stack**:
1. **Habit loop (#12)**: Identify a stable user-side cue (existing calendar event, time of day, preceding routine action). Bind the load-bearing behavior to that cue, not to a notification you fully control.
2. **Implementation intentions (#16)**: At the activation step, prompt the user to author an if-then plan ("When [their cue], I will [response]"). Templates as starting points, user edits the cue. Plan rides on the user's existing surfaces (calendar, OS reminder), not a new engagement channel. After the user authors the plan, have them read it back or confirm it in a friction-free step — this rehearsal is an identified efficacy moderator (Sheeran et al. 2024, 642-test meta-analysis); it is not re-authoring.
3. **Reinforcement schedules (#13)**: Default to fixed-interval daily and fixed-ratio weekly. The reward is the user's own outcome being legible (yesterday's progress, today's primed view). No variable-ratio gloss.
4. **Cognitive load (#14)**: The cue-triggered surface minimizes information users must retain without external support. Assess grouping, expertise and task demands; a count of visible controls is not a working-memory-capacity test.
5. **Measurement**: Cue-conditional completion rate per cohort-week. Track automaticity and cue dependence alongside completion — a stable rate or a fixed week threshold cannot on its own establish a habit; motivation and reminders remain alternative explanations. Automaticity timelines are highly variable (Lally et al.: 18–254 days to 95% of asymptote across 96 volunteers) — do not commit to a fixed weeks-to-habit number; instrument the cue-conditional rate per cohort week instead.
6. **Ethical-bound check**: The user authored the cue. The cue is on a surface they can disable. The reward is real progress on their stated goal, not a substitute counter.

**Fail signal**: streak/counter goes up but real user-outcome metrics flatten — substitute reward; the user is engaging with the gamification, not the underlying value.

**Inputs:** Target recurring behavior + candidate stable cues (existing calendar events, time-of-day signals, preceding routine actions), user's stated goal, reward options (real outcome visibility vs. surrogate counter), reinforcement schedule currently in place.
**Rules:** Bind the routine to a user-side cue (not a fully controlled push notification); reward must be a real user-visible outcome, not a surrogate counter; default to fixed-interval daily + fixed-ratio weekly schedule; no variable-ratio component without explicit harm-test sign-off; track cue-conditional completion and self-reported automaticity; stable frequency or a week threshold alone cannot establish habit formation.
**Outputs:** Cue → routine → reward specification + recommended schedule type (FI/FR) + implementation intention template for user authorship + measurement plan (cue-conditional completion rate per cohort week, alert threshold for drop).

### Recipe 5: Migration / Redesign Without Retention Collapse

**Goal**: ship a major UI or platform change without breaking the cue surface that triggers existing behavior.

**Stack**:
1. **Context-dependent retrieval (#15)**: Pre-redesign, catalogue cues per load-bearing behavior — entry-point icon, navigation path, keyboard shortcut, notification time. Preserve the dominant cue per behavior across at least one full retention cycle (typically 2–4 weeks). The effect that motivates this is direction-reliable but moderated by "outshining": other cues in a cue-rich UI (labels, search, in-product goals) can substitute for the moved cue and blunt the disruption — see [primitives-overview.md](primitives-overview.md) grade note for #15.
2. **Habit loop (#12)**: For each recurring behavior, record evidence for goal-directed or automatic cue-based use; leave mechanism unknown where evidence is insufficient. Stimulus-response habits are most fragile — those are where cue preservation matters most.
3. **Cognitive load (#14)**: New surfaces should not require novice-level chunking from existing power users. Provide an expert path that honours their learned chunks; offer the redesigned path as opt-in initially.
4. **Implementation intentions (#16)**: For users whose behavior was triggered by a cue you must remove, offer to re-anchor — let them author a new if-then plan tied to the new cue.
5. **Measurement**: Cue-conditional completion rate per behavior, daily, with an alert threshold. If a behavior's completion rate drops more than X% within Y days, partial rollback or cue restoration is required.
6. **Ethical-bound check**: Migration prompts are framed as user benefit, not platform optics. Reactivation flows for users who lapsed during the migration distinguish between "lost the cue" and "left the product."

**Fail signal**: feature usage drops after redesign: investigate cue changes, discoverability, task value, errors and cohort differences; usage alone does not diagnose habit decay.

**Inputs:** List of load-bearing behaviors + their current cues (entry-point icon, navigation path, keyboard shortcut, notification time), habit type per behavior (goal-directed vs. stimulus-response), planned redesign scope (which cues will move or disappear), baseline cue-conditional completion rate per behavior.
**Rules:** Preserve the dominant cue per stimulus-response behavior across ≥1 full retention cycle (2–4 weeks) before removing it; offer expert path honouring learned chunks; any removed cue triggers a re-anchoring offer (user-authored if-then plan via #16); alert threshold set at completion-rate drop > 15% within 7 days of rollout.
**Outputs:** Cue audit table (behavior → current cue → cue preserved Y/N → re-anchor plan if N) + rollout sequencing recommendation + measurement plan (daily cue-conditional completion rate per behavior, rollback trigger definition).
