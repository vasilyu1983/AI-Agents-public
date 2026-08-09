# Consumer Neuroscience Primitives — Composition Guide

12 domain-agnostic consumer-neuroscience primitives. Each file is a standalone playbook (Definition / When to use / Misuse boundary / Inputs / Outputs / Failure modes / Worked example / Sources). Cross-cutting guidance — primitives overview, anti-patterns, decision checklist — lives in [`../../../references/primitives-overview.md`](../../../references/primitives-overview.md).

Primitives **1–8** cover engagement-time neural responses (salience, arousal, bonding, narrative, regulatory orientation, social mirroring, aesthetics, interoception). Primitives **9–12** cover temporal and predictive mechanisms (memory consolidation, reward anticipation, embodied cognition, predictive processing).

**Ethical obligation**: every primitive carries a "Misuse boundary" subsection. Read it before applying any technique. Primitives operating on pre-conscious systems (#1, #2, #4, #8, #10, #12) carry the highest manipulation risk. The DMCC Act 2024 (in force 6 April 2025) makes online choice architecture dark patterns directly actionable. Consumer applied layers (CRO, content strategy, UI/UX, product management) are the downstream application layer — these primitives are the upstream canon.

---

## Primitives

| # | File | Core Neural Mechanism |
|---|------|----------------------|
| 1 | [01-attention-salience.md](01-attention-salience.md) | Bottom-up feature capture; top-down relevance gating |
| 2 | [02-arousal-physiology.md](02-arousal-physiology.md) | Yerkes-Dodson inverted-U; autonomic cost; GSR as engagement signal |
| 3 | [03-social-bonding.md](03-social-bonding.md) | Oxytocin-mediated affiliative response; affiliative-signal design lever (trust-causal claim not replicated under registered conditions — see playbook) |
| 4 | [04-narrative-transportation.md](04-narrative-transportation.md) | DMN + vmPFC self-referential; ventral striatum reward; transportation score |
| 5 | [05-approach-avoidance.md](05-approach-avoidance.md) | BAS reward-approach sensitivity; BIS threat-avoidance sensitivity |
| 6 | [06-mirror-systems.md](06-mirror-systems.md) | MNS motor simulation; FFA emotional face processing; affective mirroring |
| 7 | [07-neuroaesthetics.md](07-neuroaesthetics.md) | Peak-shift; symmetry preference; contour completion; beauty-driven reward |
| 8 | [08-interoception-somatic.md](08-interoception-somatic.md) | Insular cortex body-state; vmPFC somatic-marker integration; pre-deliberative bias |
| 9 | [09-memory-consolidation.md](09-memory-consolidation.md) | Hebbian potentiation; hippocampal-neocortical replay; sleep-dependent consolidation |
| 10 | [10-reward-anticipation.md](10-reward-anticipation.md) | Anticipatory mesolimbic dopamine (wanting); VTA onset ~200ms; wanting/liking dissociation |
| 11 | [11-embodied-cognition.md](11-embodied-cognition.md) | Sensorimotor concept grounding; conceptual metaphor; proprioceptive priming |
| 12 | [12-predictive-processing.md](12-predictive-processing.md) | Hierarchical Bayesian generative model; free-energy minimization; prediction-error cost |

---

## Composition Recipes (condensed)

### Anxiety-Relief Consumer Loop (pre-purchase)
Arousal deescalation (#2) → prediction priming (#12) → narrative transportation (#4) → warmth/trust (#3) → interoceptive close (#8). Fail signal: "felt scammed" qualitative reports; DMCC vulnerable-user test fails.

### Parasocial Reading Bond (purchase)
Narrative transportation (#4) → mirror-matched emotional cue (#6) → real social proof (#3) → embodied metaphor (#11). Fail signal: low share rate despite high session time.

### Daily-Cadence Retention (post-purchase)
Reward anticipation arc (#10) → consolidation-window timing (#9) → top-down salience (#1) → prediction confirmation (#12). Fail signal: streak completion without re-engagement intent.

### Conversion Landing Page, Mixed Audience (pre-purchase)
Earned salience (#1) → BIS/BAS copy split (#5) → aesthetic reward (#7) → mirror-matched testimonial (#6). Fail signal: bounce concentrated in one regulatory-focus segment.

### Trust Repair After Error (post-purchase)
Human warmth signal (#3) → somatic acknowledgment (#8) → prediction-error closure (#12) → prevention framing (#5). Fail signal: NPS recovery below 50% of pre-incident baseline.

### DMCC Compliance Audit
Harm test → dark-pattern checklist → vulnerable-user screen → biometric Article 9 lawful basis → wanting-loop cap verification. Fail signal: any "yes" on dark-pattern list; any vulnerable-user trigger without stricter controls.

---

## Related

- [`../../../references/primitives-overview.md`](../../../references/primitives-overview.md) — cross-cutting overview, anti-patterns, decision checklist
- [`../../../references/patterns-scenarios-traps.md`](../../../references/patterns-scenarios-traps.md) — applied patterns and known traps
- [`../../../references/formal-theory-map.md`](../../../references/formal-theory-map.md) — theory area map
- [`../../../data/sources.json`](../../../data/sources.json) — primary source references
