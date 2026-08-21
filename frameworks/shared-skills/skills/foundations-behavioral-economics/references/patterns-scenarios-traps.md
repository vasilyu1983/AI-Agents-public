---
description: Applied patterns, scenarios, anti-patterns, and known traps for behavioral-economics foundations.
last_verified: 2026-08-14
status: stable
---

# Behavioral Economics Patterns, Scenarios, and Traps

## Use Patterns

| Pattern | Use When | Stack |
|---|---|---|
| Ethical pricing page | Need plan choice without dark patterns | Anchoring -> decoy -> choice architecture -> harm test |
| Churn save flow | Need persuasion without blocking cancellation | Loss aversion -> mental accounting -> easy exit |
| Activation onboarding | Need adoption of valuable defaults | Defaults -> social proof -> reduced cognitive load |
| Commitment design | User wants long-term benefit but defers action | Hyperbolic discounting -> commitment device -> reminder |
| Trust repair | User lacks confidence in action | Accurate social proof -> transparent framing |

## Known Traps

- Scarcity must be real, time-bound, and auditable.
- Defaults must be easy to reverse.
- Social proof can backfire when it normalizes the undesired behavior.
- Anchors need a relevant comparison class.
- Decoys are safest when they clarify tradeoffs, not when they hide true value.
- Published coefficients are not product constants; measure locally.
- An AI agent acting for a user is itself a nudge target, and typically a more susceptible one than the user. Audit per model.
- Instructing an agent to avoid dark patterns does not make it resistant — it may detect one and proceed anyway. Constrain scope and gate irreversible actions instead.
- Conversational manipulation (sycophantic agreement, biased framing, privacy probing) is a dark pattern even with a clean interface. The harm test applies to generated turns.

## Exit Checklist

- [ ] The signal is true.
- [ ] The target choice benefits the user by their stated goal.
- [ ] The user can opt out or reverse easily.
- [ ] The copy can be disclosed without embarrassment.
- [ ] The team is measuring retention, refunds, complaints, and trust, not only conversion.
- [ ] If an AI agent acts in or on this flow, its susceptibility was tested and irreversible actions are structurally gated.
