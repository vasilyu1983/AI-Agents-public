---
description: Applied patterns, scenarios, anti-patterns, and known traps for behavioral-economics foundations.
last_verified: 2026-05-02
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

## Exit Checklist

- [ ] The signal is true.
- [ ] The target choice benefits the user by their stated goal.
- [ ] The user can opt out or reverse easily.
- [ ] The copy can be disclosed without embarrassment.
- [ ] The team is measuring retention, refunds, complaints, and trust, not only conversion.
