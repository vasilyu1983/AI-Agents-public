# Primitive: Attention & Salience

## Definition

Attention is selective: at any moment the brain allocates processing priority to a small subset of available stimuli. Two partially dissociable systems govern this allocation:

1. **Bottom-up salience** (stimulus-driven): Pre-attentive feature detectors respond automatically to contrast, motion, color singularity, and sudden onset — mechanisms formalized in Treisman's Feature Integration Theory (1980) and Itti & Koch's computational salience maps (2001). These responses are involuntary; a high-contrast red element in a grey field will capture gaze before any goal is consulted.

2. **Top-down attention** (goal-driven): The prefrontal and parietal control systems weight stimuli by relevance to current goals, prior knowledge, and personal salience. A user actively looking for a price will find it even in a low-contrast position.

Implications for product design:
- Bottom-up capture is rapid (~50–150ms for feature pop-out) but burns attentional budget without delivering value — repeated bottom-up violations without payoff train the user to habituate or flee.
- Top-down attention requires a prior: the user must already have a goal or schema that marks the stimulus as relevant.
- Bigne et al. (2025, P&M) demonstrate that neurophysiological attention measures predict in-market behavior incrementally beyond self-report in both digital and physical environments.

## When to Use

- Designing visual hierarchy on a page where multiple elements compete for attention.
- Setting notification strategy where repeated bottom-up salience risks habituation.
- Evaluating whether a call-to-action is visible by top-down relevance or requiring bottom-up contrast to compete.
- Auditing a feed or dashboard where information density may cause mutual salience suppression.

## Misuse Boundary

**Ethical use**: use bottom-up salience only for the single highest-priority element per view, and only when that element serves the user's current goal. Top-down salience built on genuine personal relevance (personalized subject lines, named data) earns attention rather than seizing it.

**Manipulation**: deploying high-contrast, motion, or red-dot notification badges on non-urgent, operator-interest items to manufacture perceived urgency. Capturing attention without delivering informational value constitutes a dark pattern under DMCC if it leads to a purchase or subscription the user would not otherwise have made.

**Required condition**: the salience intensity must be proportional to the genuine priority of the item for the user. Bottom-up capture for low-value items is an attentional debt that compounds into habituation and distrust.

## Inputs

- The visual or notification environment (competing elements, context luminance, layout).
- The user's current goal or task context (determines top-down weighting).
- The genuine informational priority of each element for the user.

## Outputs

- A salience hierarchy in which the highest-user-value element reliably wins attention first.
- Notification timing and content calibrated to earn top-down relevance.
- A design spec that reserves bottom-up salience for at most one element per view.

## Failure Modes

| Failure | Cause | Fix |
|---------|-------|-----|
| User misses the primary CTA | CTA is in a bottom-up-quiet position, and user has no prior goal-schema to drive top-down search | Add bottom-up contrast to primary CTA only; reduce competing salience from surrounding elements |
| Notification habituation within 2 weeks | Repeated bottom-up badges/alerts without top-down payoff; involuntary capture that delivers low value | Shift to top-down strategy: personalized, timely, user-relevant subject lines that match an active goal |
| Multiple equally salient elements — paralysis | Salience competition suppresses all; none wins; user skips the page | Establish a strict salience hierarchy: one bottom-up winner, everything else recedes |
| High open rate but low engagement | Bottom-up capture achieved (user opened) but top-down relevance was absent (content did not match a real goal) | Align notification content to a verified active user need, not operator interest |

## Worked Example

**Scenario**: A mobile content app has a main feed and a "Today's Reading" card that drives subscription conversion. Open rate on the card is low despite it being the revenue-critical element.

Diagnosis: the card is visually equal to feed items; bottom-up salience competition with eight other cards suppresses it; the user has no trained top-down schema to seek it.

Fix:
1. Bottom-up: assign the "Today's Reading" card a distinct visual treatment (contrast, isolated white space, slightly larger type) so it wins feature pop-out against feed items.
2. Top-down: personalize the card title to the user's name and a data point from their last session ("Your Venus reading, [Name] — based on yesterday's chart").

**Ethical check**: The element being boosted is the product's primary value-delivery item, not a hidden upsell. The personalization uses data the user provided. The salience is earned by relevance, not manufactured by alarm.

## Sources

- Treisman, A. M. & Gelade, G. (1980). A feature-integration theory of attention. _Cognitive Psychology_, 12(1), 97–136. — foundational FIT; pre-attentive feature detection.
- Itti, L. & Koch, C. (2001). Computational modelling of visual attention. _Nature Reviews Neuroscience_, 2(3), 194–203. — salience map formalization.
- Bigne, E. et al. (2025). How to conduct valuable marketing research with neurophysiological tools. _Psychology & Marketing_. — 2025 empirical anchor for neurophysiological attention measures in consumer contexts.
