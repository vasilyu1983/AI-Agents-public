# Primitive: Embodied Cognition

## Definition

Embodied cognition holds that conceptual thought is grounded in sensorimotor experience — not in abstract, amodal symbols. Two foundational accounts:

1. **Conceptual metaphor theory** (Lakoff & Johnson, 1999): Abstract concepts are structured by mappings from embodied source domains (physical experience) to abstract target domains. "More is up," "understanding is grasping," "time is a path," "emotional burden is weight." These are not mere figures of speech; they are the cognitive structures through which abstract thought is processed. Copy that uses a body-state metaphor congruent with the actual sensorimotor experience the product delivers processes more fluently than copy using incongruent or purely abstract language.

2. **Perceptual symbol systems and grounded simulation** (Barsalou, 2008): Concepts are stored not as abstract propositions but as partial reenactments of the perceptual and motor experiences associated with them. When a user reads "lighten your load," the phrase partially activates the sensorimotor representation of carrying weight and then releasing it. If the product actually produces that experience, the copy creates a prediction that the product experience then confirms. If the product does not produce that experience, the embodied prediction is violated.

Implications:
- Copy using embodied metaphors congruent with the product experience is more fluent, more memorable, and more likely to be confirmed by actual use.
- Incongruent embodied metaphors create cognitive interference: the simulated body-state the language implies does not match the product experience.
- Physical UI metaphors (swiping, flipping, stacking, tapping) carry embodied affordance expectations; violating them creates disproportionate friction.

> **Replication-boundary note — do not conflate this primitive with "social priming."** This primitive rests on conceptual metaphor theory and grounded-simulation research (metaphor comprehension speed, gesture-concept congruence, sensorimotor interference in reading tasks) — a body of psycholinguistic evidence distinct from the incidental-cue behavioral-priming literature (e.g., Bargh et al. 1996 elderly-words-slow-walking; money priming; cleanliness priming) that largely failed multi-lab registered replication (Doyen et al. 2012; Many Labs 2014/2018). Use this primitive to align copy metaphor and UI gesture with a product's real experiential output — a fluency and expectation-matching effect — not to claim that an incidental, unrelated environmental cue (a color, a word, a background image) covertly steers downstream behavior in a different domain. If a design brief invokes "priming" for the latter claim, that is the discredited paradigm, not this primitive.

## When to Use

- Writing copy for any product where the primary value is an experiential or emotional state (calm, clarity, lightness, confidence, warmth).
- Evaluating whether the sensorimotor metaphors in existing copy match the product's actual experiential output.
- Designing spatial UI metaphors (navigation, gestures, card mechanics) for consistency with embodied affordance expectations.
- Explaining why certain copy "feels right" or "feels off" in terms of sensorimotor grounding rather than subjective taste.

## Misuse Boundary

**Ethical use**: embodied metaphors that accurately represent the sensorimotor experience the product produces. "Clarity settles in" for a product that users report experiencing as clarifying — honest, fluent, predictive.

**Manipulation**: using high-potency embodied metaphors (weight lifting, darkness-to-light, constriction-to-release) that imply a profound somatic transformation for a product that delivers a mild experiential change. The metaphor sets a somatic expectation that the product cannot meet. This is a form of misleading claims under ASA CAP Code if the somatic transformation is implied to have therapeutic or medical effect.

**Required condition**: the body-state metaphor in copy must match the body-state that users actually report experiencing. Collect somatic language from open-form user feedback (NPS verbatims, support messages) and use that language back in copy.

## Inputs

- Open-form user feedback in which users describe the product experience in their own words (especially somatic language).
- The product's primary experiential output (what body state does it reliably shift?).
- The UI interaction model (swipe, tap, scroll, flip — what sensorimotor affordance does it imply?).

## Outputs

- A copy vocabulary derived from actual user somatic language, not invented metaphors.
- A UI gesture design that respects embodied affordance expectations for the interaction type.
- An embodied-metaphor audit of existing copy: does each metaphor match the product's experiential output?

## Failure Modes

| Failure | Cause | Fix |
|---------|-------|-----|
| Copy feels "off" in qualitative testing | Embodied metaphors in copy do not match users' own sensorimotor descriptions of the product | Mine NPS verbatims and support messages for the somatic language users actually use; replace copy metaphors with user-sourced language |
| UI gesture interaction causes unexpected friction | Swipe direction, drag affordance, or navigation gesture violates embodied expectation for that interaction class | Audit gesture design against platform convention and sensorimotor affordance; do not invent novel gestures for routine interactions |
| "Transformative" copy generates high trial, high refund | Metaphor implied somatic transformation (darkness to light) that product does not deliver at that intensity | Calibrate metaphor intensity to match actual user-reported somatic shift magnitude |
| Abstract product copy generates no engagement | No sensorimotor grounding; copy is purely propositional ("provides insight and guidance") | Replace with grounded metaphor derived from user somatic vocabulary ("feels like having someone steady to turn to") |

## Worked Example

**Scenario**: A daily spiritual guidance app uses the copy "Navigate your path with cosmic clarity" throughout the onboarding. User testing shows the copy "feels aspirational but distant." Day-1 engagement is moderate.

Diagnosis: "navigate" and "cosmic clarity" are spatial-abstract metaphors. They are not grounded in the actual sensorimotor experience users report: NPS verbatims include "feels like a moment of stillness," "like a breath before the day starts," "I can think more clearly." These are breathing/stillness metaphors, not navigation metaphors. Incongruent grounding.

Fix:
1. Replace "Navigate your path with cosmic clarity" with "A moment of stillness before the day begins. Your reading, ready."
2. UI opening animation: a slow breath-rhythm fade-in rather than a swipe-to-reveal gesture.
3. Opening screen gesture: tap to reveal (not swipe) — congruent with "resting on" rather than "moving through."

**Ethical check**: the somatic experience claimed (stillness, breath, clarity before the day) matches what users actually report. No therapeutic claims implied.

## Sources

- Lakoff, G. & Johnson, M. (1999). _Philosophy in the Flesh_. Basic Books. — conceptual metaphor theory; sensorimotor grounding of abstract thought.
- Barsalou, L. W. (2008). Grounded cognition. _Annual Review of Psychology_, 59, 617–645. — perceptual symbol systems; grounded simulation of concepts.
