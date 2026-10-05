# Safety-II, resilience engineering and STAMP

For failure rates, FMEA and fault trees, see [reliability theory](../../foundations-reliability-theory/SKILL.md). This file covers the complements to those methods.

## Safety-I vs Safety-II

- **Safety-I.** FMEA, FTA and root-cause work list deviations from nominal design. Ham (2020) summarizes the aim as "a situation in which as few accidents as possible do happen". They remain valid for component failure.
- **Safety-II** (Hollnagel 2014, as summarized by Ham 2020). Safety is "a condition in which successful work outcomes continue". Performance varies in normal work, and that variability is the source of both good and bad outcomes: the causes of successful outcomes "are not different from those of failed work outcomes". Both quotations are Ham's wording, not Hollnagel's.
- **Work-as-imagined vs work-as-done.** Procedures describe the work that designers anticipated. People adapt what they actually do to real conditions and resources. Incident analysis that only compares events against procedure will miss those adaptations.
- **Resilience abilities** (Ham 2020): respond, monitor, learn and anticipate. Use them as audit questions for an operational team or an agent supervisor loop. For example: what does it monitor, and what does it anticipate?
- **FRAM** (Functional Resonance Analysis Method). It models how variability in coupled functions propagates and "resonates". Use it when failures arise from normal variability combining, not from a component deviating.

**When to add Safety-II.** Add it when human–automation interaction dominates, when normal work varies a lot, or when reviews keep concluding "everything worked as designed, but the combination failed".

## STAMP and STPA

- **STAMP** (Leveson 2011). An accident is a failure of control: constraints were not enforced across the hierarchy of controllers and feedback. Component failure is not the whole explanation.
- **STPA** is the forward hazard analysis built on STAMP ([STPA analysis](stpa-analysis.md)).
- **CAST** is the retrospective analysis built on STAMP ([CAST](cast-incident-analysis.md)).

Choose STPA over or alongside FTA in two cases:

- the system is software-intensive, autonomous or includes a human in the loop;
- the main hazard comes from unsafe interactions between components that each work correctly.

Boolean fault-tree gates cannot represent a flawed process model or feedback that arrives late.

**When not to use.** For a hardware or component failure mode with known rates and independence, use FTA or FMEA in reliability theory. STPA adds effort there without adding insight.
