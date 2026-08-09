# Primitive: Interoception & Somatic Markers

## Definition

Interoception is the brain's representation of the body's internal state — hunger, heart rate, gut tension, skin temperature, breath pattern. Two intersecting theories govern its relevance for consumer design:

1. **Somatic marker hypothesis** (Damasio, 1996): The ventromedial prefrontal cortex (vmPFC) integrates body-state signals into decision biases before deliberate reasoning runs. "Gut feelings" are not noise to be overridden — they are low-latency predictions from the somatic system that bias subsequent deliberative processing. In consumer contexts, the somatic state at the moment of purchase or commitment is encoded with the decision and becomes part of the product association.

2. **Insular cortex interoceptive processing** (Craig, 2009): The anterior insula is the primary cortical substrate for interoception — it represents bodily feeling states and generates the "feeling of feeling" (meta-interoception). Insular activation correlates with empathy, risk-aversion, disgust, and the subjective feeling of urgency. Elevated insular activation in an anxious or uncomfortable body state can bias a decision toward avoidance or — when combined with a relief-offering product — toward approach.

Implications:
- The user's body state when they encounter the product shapes their decision, independent of content quality.
- Products in wellness, anxiety-relief, or high-stakes financial contexts are routinely meeting users in elevated insular activation states. This is both a design opportunity and an ethical risk.
- Somatic markers established through product use are durable; the "gut sense" of whether a product is trustworthy is partly an interoceptive memory.

## When to Use

- Designing experiences for users who are likely to be in elevated somatic arousal states (anxiety, physical tension, fatigue).
- Evaluating whether "gut feel" purchase triggers are driven by genuine product value or by manufactured somatic urgency.
- Building trust-repair flows, where the user's interoceptive state at the error moment defines the emotional valence they bring to the repair.
- Designing wellness content where body-state awareness is itself the product value.

## Misuse Boundary

**Ethical use**: acknowledge and work with the user's somatic state to help them make a well-grounded decision. If the product genuinely relieves an anxious state, connecting it to the somatic signal is honest design. Inviting interoceptive attention ("Notice how that lands for you") is respectful of the user's own body knowledge.

**Manipulation**: triggering somatic anxiety signals through product design (countdown timers, scarcity framing, alarming language in a wellness context) to manufacture urgency that then resolves only through purchase. This is the interoceptive equivalent of manufactured scarcity: a fake body-state signal used to drive a decision. In wellness and anxiety contexts, this directly invokes the CMA/DMCC vulnerable-user clause.

**Required condition**: any product-generated somatic signal (urgency, discomfort, anxiety) must reflect a real user-relevant stake. Do not manufacture body-state urgency where none exists. Biometric/physiological measurement of somatic signals (HRV, GSR, skin temperature) requires UK GDPR Article 9 explicit consent.

## Inputs

- The probable body state of the user at entry (elevated arousal, fatigue, anxiety — proxy from referral source or product context).
- The product's genuine somatic value proposition (does it calm, energize, ground, or orient?).
- The pacing design of the experience (how quickly does it modulate the entry somatic state?).

## Outputs

- An experience pacing design that acknowledges entry somatic state and has a named somatic trajectory (deescalate → ground → orient).
- Copy that uses body-state language congruent with the somatic experience the product produces.
- An interoceptive close: a moment at session end where the user is invited to notice their current body state — encoding the product association in a positive somatic marker.

## Failure Modes

| Failure | Cause | Fix |
|---------|-------|-----|
| Wellness product feels clinical | No somatic language; body-state is not acknowledged or invited; insular cortex not engaged in a positive register | Add body-state invitations ("Take a breath before we begin"; "Notice how your body feels as you read this") |
| High cancellation after first "problem" session | Negative somatic marker encoded at error moment; recovery flow is cognitive, not somatic | Redesign error/apology flow to begin with somatic acknowledgment before cognitive explanation |
| Anxiety-relief product increases reported anxiety | Entry somatic state was elevated; product pacing added further arousal (countdown, urgency, dramatic framing) before relief | Diagnose entry arousal arc; remove manufactured urgency from high-arousal-audience entry flows |
| Manufactured urgency backfires in wellness context | CMA vulnerable-user test fails; users report feeling pressured; DMCC risk | Remove countdown timers, scarcity language, and pressure copy from all wellness/anxiety audience entry flows |

## Worked Example

**Scenario**: A spiritual wellness app has a day-1 onboarding quiz with a red progress bar, countdown timers on each question, and a results screen with a pulsing "Start Your Journey NOW" CTA. Day-1 cancellation rate is 18%.

Diagnosis: the quiz is manufacturing somatic urgency (insular activation via countdown, color, pulsing CTA) in an audience that likely entered with elevated arousal. The result is threat-appraisal, not decision clarity. The somatic marker encoded for the product association is anxiety, not relief.

Fix:
1. Remove countdown timers; remove pulsing animations.
2. Open quiz with a somatic grounding instruction: "Take a breath. We'll go at your pace."
3. Replace red progress bar with a calm color. Progress is shown, not weaponized.
4. Results screen: no urgency CTA. Show the personalized result first; let the user sit with it 5 seconds; then offer "Ready to begin?"

**Ethical check**: no manufactured urgency. The product's actual somatic value (calm, grounding) is embodied in the onboarding experience from the first screen.

## Sources

- Damasio, A. R. (1996). _Descartes' Error_. Papermac. — somatic marker hypothesis; vmPFC integration of body-state into decision bias.
- Craig, A. D. (2009). How do you feel — now? The anterior insula and human awareness. _Nature Reviews Neuroscience_, 10(1), 59–70. — insular cortex as interoceptive substrate; meta-interoception.
