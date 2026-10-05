# Behavioural Hypothesis Templates (Primitives) — Composition Guide

12 domain-agnostic templates. Each file is a standalone playbook (Definition / When to use / Misuse boundary / Inputs / Outputs / Failure modes / Worked example / Sources). Use each one to write a **testable behavioural hypothesis**. Neural findings are background only and never evidence that a design works (no reverse inference). Cross-cutting guidance lives in [`../../../references/primitives-overview.md`](../../../references/primitives-overview.md).

**Ethical obligation**: every template carries a "Misuse boundary" subsection. Read it before applying any technique. Templates that act with little deliberation (#1, #2, #4, #8, #10, #12) carry the highest manipulation risk. UK choice-architecture enforcement is covered in `foundations-behavioral-economics`. Consumer applied layers (CRO, content strategy, UI/UX, product management) are downstream; these templates are the upstream canon.

---

## Templates

| # | File | Behavioural regularity (neural background, if any) |
|---|------|----------------------|
| 1 | [01-attention-salience.md](01-attention-salience.md) | Contrast, motion and novelty capture attention; relevance holds it |
| 2 | [02-arousal-physiology.md](02-arousal-physiology.md) | Very high or very low activation and effort hurt performance; GSR is activation, not felt arousal |
| 3 | [03-social-bonding.md](03-social-bonding.md) | Trust follows credible, operationally true care; oxytocin→trust not replicated (Declerck et al. 2020) |
| 4 | [04-narrative-transportation.md](04-narrative-transportation.md) | Transportation (self-report scale) reduces counterarguing (Green & Brock 2000; van Laer et al. 2014) |
| 5 | [05-approach-avoidance.md](05-approach-avoidance.md) | Regulatory focus & fit: frames that fit the goal raise value (Higgins 2000; Motyka et al. 2014); BIS/BAS is distinct |
| 6 | [06-mirror-systems.md](06-mirror-systems.md) | Social proof and modelling from similar others; mirror-neuron interpretations contested |
| 7 | [07-neuroaesthetics.md](07-neuroaesthetics.md) | Visual fluency and quality shape first impressions and inferred quality |
| 8 | [08-interoception-somatic.md](08-interoception-somatic.md) | People use current feelings as information; insula activity is non-selective |
| 9 | [09-memory-consolidation.md](09-memory-consolidation.md) | Spacing and retrieval practice improve recall; sleep consolidation is background only |
| 10 | [10-reward-anticipation.md](10-reward-anticipation.md) | Wanting can decouple from liking; digital behaviour alone does not establish a dopamine response |
| 11 | [11-embodied-cognition.md](11-embodied-cognition.md) | Metaphors congruent with the experience are processed more fluently |
| 12 | [12-predictive-processing.md](12-predictive-processing.md) | Consistent flows are easier; unannounced changes cause errors |

---

## Composition Recipes (condensed)

Full versions: [`../../../references/composition-recipes.md`](../../../references/composition-recipes.md).

### Anxiety-Relief Consumer Loop (pre-purchase)
Calm entry (#2) → predictable structure (#12) → "person like me" story (#4) → real care signals (#3) → optional reflective self-check (#8). Fail signal: "felt scammed" or "felt pushed" reports; vulnerable-user gate fails.

### Personal Reading Bond (purchase)
Narrative frame (#4) → verified social imagery (#6) → real cohort framing (#3) → congruent metaphor (#11). Fail signal: low share rate despite high session time.

### Daily-Cadence Retention (post-purchase)
Capped daily reveal (#10) → user-chosen timing (#9) → relevance over loudness (#1) → format consistency (#12). Fail signal: streak completion without next-session intent.

### Conversion Landing Page, Mixed Audience (pre-purchase)
Relevance at entry (#1) → gain vs safety frame test, randomised; stated-goal segments only, never referral source (#5) → visual credibility (#7) → verified testimonials (#6). Fail signal: a framing gap that reverses across pre-declared stated-goal segments.

### Trust Repair After Error (post-purchase)
Named human acknowledgment (#3) → listen to impact (#8) → explain what failed and what changed (#12) → truthful safeguard framing (#5). Fail signal: trust and task outcomes do not recover against service-specific targets set in advance.

### Choice-Architecture Audit
Harm test → dark-pattern checklist → vulnerable-user screen → personal/special-category classification and lawful conditions → wanting-loop cap verification. Fail signal: any "yes" on the dark-pattern list; any vulnerable-user trigger without stricter controls.

---

## Related

- [`../../../references/primitives-overview.md`](../../../references/primitives-overview.md) — cross-cutting overview, anti-patterns, decision checklist
- [`../../../references/patterns-scenarios-traps.md`](../../../references/patterns-scenarios-traps.md) — applied patterns and known traps
- [`../../../references/formal-theory-map.md`](../../../references/formal-theory-map.md) — theory area map
- [`../../../references/composition-recipes.md`](../../../references/composition-recipes.md) — full recipes and misuse boundaries
- [`../../../data/sources.json`](../../../data/sources.json) — primary source references
