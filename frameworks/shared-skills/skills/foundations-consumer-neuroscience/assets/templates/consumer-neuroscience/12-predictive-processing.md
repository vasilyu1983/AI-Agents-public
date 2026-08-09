# Primitive: Predictive Processing & Active Inference

## Definition

Predictive processing proposes that the brain does not passively register sensory input; it continuously generates probabilistic predictions about incoming signals and updates those predictions when reality deviates. Two interlocking mechanisms:

1. **Free-energy minimization** (Friston, 2010): The brain minimizes "surprise" — the deviation between its generative model (prior predictions) and actual sensory input. Prediction errors propagate upward through the cortical hierarchy and drive model updating. Precision-weighting determines which prediction errors are acted on: high-precision errors (unexpected, high-information signals) command attention and model revision; low-precision errors (noise) are suppressed. This framework unifies attention, perception, learning, and action under a single computational principle.

2. **Active inference and world-shaping** (Friston, Clark, and Constant et al.): The organism does not only update its model to match the world; it also takes actions to make the world match its predictions. In consumer design terms: the product shapes a user's predictive model through consistent design conventions, branded patterns, and repeated experience. Sprevak's 2024/2025 reviews establish predictive processing as the dominant computational framework for cognition and its design implications.

Unifying role: predictive processing grounds primitive #1 (attention = precision-weighting of prediction errors), primitive #4 (narrative transportation = high-precision self-referential prediction running forward), and primitive #8 (interoception = prediction of body states) under one framework. Prediction error is the common attentional currency.

Implications:
- Every design decision sets a prior. A consistent interface creates predictions; a consistent brand creates expectations. Violating those priors incurs a prediction-error cost that must be "earned" by the value of the new information.
- Surprise is not inherently good. Surprise = prediction error = attentional cost. The question is whether the design has earned the right to charge that cost.
- Active inference means users are not passive: they act to confirm predictions (selective attention, skipping ahead, filling in) and feel discomfort when they cannot.

## When to Use

- Designing feature reveals, onboarding surprises, or product updates where violating established user priors is unavoidable.
- Auditing a product for prediction-error budget: are surprises being earned, or are they incurring debt?
- Building brand and interface consistency to create strong, reliable priors that reduce cognitive cost.
- Explaining user anxiety or confusion after a product change in mechanistic terms (prediction error without payoff).

## Misuse Boundary

**Ethical use**: managing the prediction-error budget deliberately — building strong priors through consistent design, then spending that budget on high-value surprises that justify their attentional cost. Active inference used to understand and serve user world-models.

**Manipulation**: engineering persistent prediction-error states to maintain compulsive engagement — variable-ratio schedule-equivalent pattern applied to information delivery, where the unpredictability itself keeps the user's predictive model perpetually unresolved. The closest dark-pattern equivalent: intermittent reinforcement structured at the information level, not just reward level. DMCC Act 2024 digital fairness provisions apply where such design is targeted at vulnerable users.

**Required condition**: prediction-error violations must be earned. The value of the new information must justify the attentional cost of the prediction error. Consistent priors must be respected during routine use; reserve violations for intentional, high-value product moments.

## Inputs

- The established predictions users have formed about the product interface, content structure, and delivery schedule.
- The information value of the planned violation (is the surprise worth its prediction-error cost?).
- The user's prior precision-weighting state (anxious, high-precision users have a lower tolerance for prediction errors).

## Outputs

- A prediction-error budget audit: listing established user priors and the cost of any planned violation.
- A priming design for high-value surprises (teasers, progressions, waitlists that build a new prior before the violation).
- An interface consistency standard: which elements must never change (strong prior anchors) and which can evolve (lower-precision zones).

## Failure Modes

| Failure | Cause | Fix |
|---------|-------|-----|
| User confusion after product update | Established prior violated without warning; prediction error without new-model scaffolding | Prime before the change: communicate what is changing and why before it ships; let users build a new prior |
| "Clever" reveal generates anxiety, not delight | High prediction-error surprise in a high-precision (anxious) user state; attentional cost exceeds information value | Build the prior before the reveal; reserve surprise for contexts where the user's precision-weighting is low (playful, explorative states) |
| Brand inconsistency reduces trust over time | Multiple design eras, inconsistent iconography, varying copy tone; no stable prior for the brand's behavior | Define and enforce a small set of invariant brand-prior anchors (entry gesture, primary color, notification tone) |
| Feature adoption low after launch | New feature violates users' prediction of what the product does; high prediction error without prior investment | Pre-launch: tease the feature; establish the use-case prior; let users predict it before it arrives |

## Worked Example

**Scenario**: A daily reading app introduces a "Weekly Deep Dive" — a longer, narrative-heavy reading that replaces the usual short daily card on Sundays. Engagement on Sunday drops 40% in the first two weeks. Users report "not sure what this is" and "felt wrong."

Diagnosis: the weekly format is a strong prediction-error event. Users had a stable prior (short daily card, specific format, consistent structure). The Sunday replacement violated that prior without earning the attentional cost. Precision-weighting is high for Sunday engagement because the format is tightly learned.

Fix:
1. Prime four weeks before launch: "Something special is coming on Sundays" — build the expectation prior.
2. Launch week 1: "Your first Sunday Deep Dive is here." Frame it as a new prior, not a replacement.
3. Keep the daily card available on Sunday as an opt-out for users who do not want to update their model yet.
4. Measure second-Sunday engagement separately as the new prior stabilizes.

**Ethical check**: no manipulation of prediction states for compulsive engagement. The surprise serves genuine product value (deeper reading). The prior is built before the violation.

## Sources

- Friston, K. (2010). The free-energy principle: a unified brain theory? _Nature Reviews Neuroscience_, 11(2), 127–138. — foundational predictive processing; free-energy minimization.
- Clark, A. (2013). Whatever next? Predictive brains, situated agents, and the future of cognitive science. _Behavioral and Brain Sciences_, 36(3), 181–204. — active inference; predictive processing as unifying cognitive framework.
- Sprevak, M. (2024). Predictive processing: a review. _Topics in Cognitive Science_; and (2025) _Inquiry_. — 2024/2025 anchor; current state of predictive processing theory and its applied scope.
- Constant, A., Clark, A., Kirchhoff, M. & Friston, K. (2019). Extended active inference. _Philosophical Transactions of the Royal Society B_, 374. — active inference extended beyond the skull; design shapes user world-models.
