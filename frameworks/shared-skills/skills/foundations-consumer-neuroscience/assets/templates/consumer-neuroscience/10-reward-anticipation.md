# Primitive: Reward Anticipation (Wanting vs Liking)

## Definition

The mesolimbic dopamine system generates two phenomenologically distinct states that are neurally dissociable:

1. **Wanting (incentive salience)**: Anticipatory dopamine release from the VTA (ventral tegmental area) to the nucleus accumbens is triggered by conditioned stimuli predicting reward — before the reward arrives. This wanting signal generates drive, motivation, and the subjective feeling of craving or eagerness. Knutson et al. (2001) demonstrate that nucleus accumbens activation peaks during reward anticipation, not reward delivery. VTA dopamine onset is approximately 200ms after the predicting cue. Berridge (2007) established that wanting is neurally and functionally dissociable from liking.

2. **Liking (hedonic impact)**: The actual hedonic response to reward delivery is mediated by separate systems — primarily opioid and endocannabinoid activity in the nucleus accumbens shell and ventral pallidum. Liking can be absent while wanting remains high — this is the signature of compulsive use. A user who "can't stop opening the app" but reports low satisfaction is experiencing wanting without liking.

The wanting-liking dissociation is the foundational mechanism behind compulsion design, and the primary reason anticipation-loop mechanics require explicit harm-test gating.

Implications:
- The anticipation phase (countdown, sealed card, pending notification) can generate more behavioral drive than the reward itself.
- Designing for wanting without designing for liking is compulsion design: the user keeps engaging to resolve the anticipatory state, not because each engagement is satisfying.
- Products with high DAU and low satisfaction scores, or high engagement and high churn at week 4, are running a wanting/liking dissociation.

Distinction from `foundations-behavioral-economics` primitive #13 (reinforcement schedules): that primitive covers the schedule of reward delivery (FR/VR/FI/VI) as a behavioral mechanism. This primitive covers the neurochemistry of the anticipatory state — the wanting drive that precedes any schedule — as a separate design lever.

## When to Use

- Designing daily unlock mechanics, card reveals, countdown features, or "what's inside" anticipation UX.
- Diagnosing products with high engagement but flat or declining satisfaction.
- Building a launch or release arc (teaser → waitlist → reveal) that converts wanting into liking.
- Evaluating whether an existing engagement loop is generating wanting, liking, or the dangerous dissociation between them.

## Misuse Boundary

**Ethical use**: design anticipation arcs where wanting is followed by genuine liking — the reveal or reward must deliver hedonic value proportional to the anticipatory drive. Anticipation loops with natural satiation signals and designed completion states.

**Manipulation**: open-ended anticipation loops (infinite scroll, endless daily unlock chains, unresolvable reward cycles) that exploit wanting-drive indefinitely without ever satisfying with genuine liking. These are compulsion-design mechanisms. The harm test is clear: if the user cannot stop because they want to resolve the anticipatory state, not because each session is enjoyable, the design is exploiting a neural vulnerability. DMCC Act 2024 provisions on practices that "take advantage of vulnerability" are directly relevant for audiences with anxiety, low impulse control, or financial vulnerability.

**Required condition**: every anticipation arc must have an explicit satiation signal — a completion state where wanting resolves into a clear hedonic close. Rate-cap any daily unlock chain. Document the cap in the design spec. Gate any open-ended anticipation mechanic behind a harm-test sign-off.

## Inputs

- The predicting cue (notification, sealed card visual, countdown timer).
- The reward content (what is revealed; does it deliver genuine liking value?).
- The loop structure (is there a natural satiation point, or is the loop open-ended?).

## Outputs

- An anticipation arc specification with: cue design, anticipation window length, reveal design, satiation signal (explicit completion state).
- A wanting/liking diagnostic: DAU × satisfaction score correlation; week-4 engagement vs reported value.
- A harm-test record for any mechanic with an anticipation loop longer than one daily cycle.

## Failure Modes

| Failure | Cause | Fix |
|---------|-------|-----|
| High DAU, low satisfaction | Wanting loop active; liking system not engaged; user opens to resolve anticipation, not because they enjoy it | Redesign the reveal to deliver genuine hedonic value; reduce anticipation frequency; add explicit satiation signal |
| User engages but cannot articulate why | Mesolimbic wanting running without conscious liking; common in scroll-based product design | Force a liking diagnostic: "Was today's reading valuable?" visible immediately post-reveal; use this to gate the next loop |
| Daily streak continues but cohort NPS collapses | Wanting-loop persistence masking declining liking; streak gamification is keeping users mechanically engaged | Distinguish streak completion rate from satisfaction; treat divergence as a compulsion-design warning signal |
| Anticipation-less design generates no re-engagement | No wanting cue exists; no dopamine anticipatory signal; the product has nothing to look forward to | Design a named, consistent daily cue that makes the reward predictable (predicting cue is required for VTA activation ~200ms pre-reveal) |

## Worked Example

**Scenario**: A daily spiritual content app has a "Daily Card" feature — a sealed card that reveals a reading when opened. DAU is high. But week-4 cohort retention is 34% and NPS is 28. Users describe the app as "addictive" but "kind of empty."

Diagnosis: the sealed card creates strong wanting (conditioned cue → VTA dopamine → nucleus accumbens anticipation). But the reveal is generic, not personalized, and delivers low liking value. The user is reopening to resolve the anticipatory state, not because previous reveals were satisfying. Wanting/liking dissociation: compulsion without satisfaction.

Fix:
1. Invest in reveal quality: the daily card content must be genuinely personalized and emotionally resonant (Primitive #4 narrative transportation).
2. Add an explicit satiation signal: after the reading, show a "Your reading for today is complete" screen — a closure beat. The wanting loop resolves.
3. Add a satisfaction micro-survey: "Did this land for you?" (yes/not really). Use this data to improve liking delivery; surface it to design as a weekly metric.
4. Cap the daily reveal: one card per day, no "bonus unlocks" that extend the wanting loop without satiation design.

**Ethical check**: satiation signal is designed. Wanting loop is capped at one per day. Satisfaction data is measured and acted on.

## Sources

- Knutson, B., Adams, C. M., Fong, G. W. & Hommer, D. (2001). Anticipation of increasing monetary reward selectively recruits nucleus accumbens. _Journal of Neuroscience_, 21(16), RC159. — nucleus accumbens anticipatory activation; wanting vs delivery.
- Berridge, K. C. (2007). The debate over dopamine's role in reward: the case for incentive salience. _Psychopharmacology_, 191(3), 391–431. — wanting/liking dissociation; incentive salience theory.
