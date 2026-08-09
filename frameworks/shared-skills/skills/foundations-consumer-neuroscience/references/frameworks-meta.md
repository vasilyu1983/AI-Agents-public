---
description: Named meta-frameworks for selecting and composing consumer-neuroscience primitives — SOR, Consumer Decision Journey, Hierarchy of Effects, Affect-as-Information, Predictive-Coding, BIS/BAS Regulatory Focus, Reactance.
last_verified: 2026-07-11
status: stable
---

# Meta-Frameworks for Primitive Composition

## Purpose

A single primitive narrows the design lens to one neural mechanism. Most real product problems require three to five primitives acting in sequence or in tension — attention earned before arousal, arousal calibrated before trust, trust established before narrative absorption. Meta-frameworks provide the structural logic for that composition: they name the causal chain, assign primitives to positions in it, and prevent arbitrary stacking. Without a meta-frame, a designer applying five primitives independently is as likely to create interference as coherence. The frameworks below are complementary rather than mutually exclusive; they operate at different levels of abstraction and are meant to be layered.

---

## Framework Selection Matrix

| Framework | When to Use | Inputs Required | Outputs | Primitives It Composes |
|-----------|-------------|-----------------|---------|------------------------|
| **SOR (Stimulus → Organism → Response)** | Default outer container for any neuromarketing analysis. Maps stimulus features to organism state to behavioural response. | Stimulus description (visual, auditory, copy); target organism state; desired response metric | Causal chain from design feature to user behaviour | #1, #7, #11 (stimulus) → #2, #3, #5, #8 (organism) → #4, #6, #10, #12 (response) |
| **Consumer Decision Journey (CDJ)** | When the design problem spans pre-purchase / purchase / post-purchase stages and primitives must be assigned to the correct stage. | Stage map of the user's journey; known drop-off points | Stage-specific primitive stack; intervention priority by stage | Pre-purchase: #1, #5, #7; Purchase: #2, #3, #8, #10; Post-purchase: #4, #6, #9, #12 |
| **Hierarchy of Effects (Lavidge-Steiner, neuro-updated)** | When measuring persuasion depth: awareness → comprehension → conviction → action. Useful for ad and content campaigns where conversion is not immediate. | Campaign objective; current awareness level; measured comprehension gap | Prioritised primitive by persuasion stage | Awareness: #1; Comprehension: #4, #11; Conviction: #12, #3; Action: #10, #5 |
| **Affect-as-Information (Schwarz & Clore 1983; Damasio 1996)** | When a body-state or mood signal is the proximate cause of a decision — wellness, anxiety, high-stakes purchase. Anchors interoception and arousal as decision inputs, not just engagement signals. | Evidence (or assumption) of elevated interoceptive signal at decision point; somatic-marker encoding moment | Design of body-state cue, framing copy, and somatic-close mechanic | #8 (interoception), #2 (arousal as affect quality); cross-cuts #4 and #10 |
| **Predictive-Coding Hierarchy (Friston 2010; Clark 2013)** | When the design problem is about managing surprise, consistency, and expectation across a product or campaign lifecycle. Meta-frame for when to violate priors and at what cost. | Existing user priors (established by brand or previous use); novelty budget; attentional cost tolerance | Prediction-error allocation plan; prior-setting vs. prior-violating event calendar | #12 (primary), #1 (prior-driven attention), #4 (narrative as generative model), #9 (prior consolidation) |
| **BIS/BAS Regulatory Focus (Higgins 1997)** | When copy tone, offer framing, or risk-disclosure design must serve a mixed promotion-seeking and prevention-vigilant audience, or when segmenting by regulatory orientation is feasible. | Audience regulatory-focus distribution (survey or behavioural proxy); conversion data by segment | Dual-copy variants; BAS-frame and BIS-frame templates; segmentation logic | #5 (primary); cuts across copy (#4, #11), offer (#10), and risk-disclosure design (#8, #12) |
| **Reactance Theory (Brehm 1966)** | As a guardrail check after composition. Detects designs that pass primitive-level checks (attention earned, arousal calibrated, trust signalled) but feel manipulative at the system level because they implicitly threaten perceived freedom. | User-acceptance qualitative data ("felt scammed," "felt pushed"); DMCC OCA audit results | Flag: design feature or copy that triggers reactance; correction priority | Crosses #2 (manufactured urgency), #5 (autonomy threat), #10 (pressure mechanic), #12 (false scarcity); not a primary design tool — applied after composition |

---

## Composition Logic

The frameworks layer rather than substitute:

1. **SOR is the outer container.** Every design problem can be expressed as a stimulus → organism → response chain. Always start here to assign primitives to the correct causal position before applying other frames.
2. **CDJ adds temporal phase.** Not all primitives are relevant at every journey stage. Overlaying the Consumer Decision Journey on SOR prevents misapplied primitives (e.g., reward anticipation (#10) in a post-error trust-repair context where interoception (#8) and predictive processing (#12) belong first).
3. **Hierarchy of Effects adds persuasion depth.** When the product goal is long-horizon attitude change (brand perception, category consideration), the Lavidge-Steiner hierarchy maps which primitives to apply at which persuasion depth. It is most useful for advertising; less relevant for transactional or habitual-use product surfaces.
4. **Predictive-Coding adds hierarchy within each stage.** Friston's free-energy frame governs when prediction-errors are affordable (novelty budget) vs. costly (stable use phase). It sets the surprise budget across all other frames.
5. **Reactance is a guardrail, not a design frame.** Apply it after composition as a system-level audit. If reactance-triggering patterns are detected (autonomy restriction, manipulative urgency, false scarcity), revise the composed stack before shipping. It does not generate design; it prevents misuse.

---

## Anti-Frameworks

Frames that should not be applied in this skill:

| Frame | Why to Avoid | Source of the Critique |
|-------|-------------|----------------------|
| "Neuromarketing as mind reading" — inferring precise purchase intent from brain scans | Neural signals indicate tendencies, not intentions; generalisation from lab fMRI to field purchase is unvalidated. Creates false precision in design briefs. | Plassmann et al. 2015; Bigne 2025 P&M review |
| Triune brain / limbic = emotional, cortex = rational | Debunked taxonomy. Emotion is distributed across cortex (vmPFC, insular, ACC) and subcortex simultaneously; no clean separation. Misroutes design decisions. | MacLean 1990 origin; Damasio 1996 rebuttal; Lieberman 2013 _Social_ |
| Left-brain / right-brain lateralisation as design heuristic | Over-simplification of hemisphere differences; not a valid basis for copy or visual placement decisions. | Hellige 1993; Nielsen 2015 review |
| "Lizard brain" — primitive survival brain drives purchases | Reverse-engineered folk neuroscience; conflates brainstem function with mesolimbic and prefrontal circuits actually implicated in consumer decisions. | Du Plessis 2008 _The Advertised Mind_; Rolls 2014 |
| Incidental behavioral priming — an unrelated environmental cue (color, word, background image) covertly steers downstream behavior in a different domain | The classic demonstrations (Bargh et al. 1996 elderly-words-slow-walking; money priming; cleanliness priming) largely failed multi-lab registered replication. Do not confuse with primitive #11 (embodied cognition), which is about copy/UI metaphor matching a product's actual experiential output — a fluency effect, not a covert cross-domain behavior nudge. | Doyen et al. 2012 (PLOS ONE); Many Labs 2 (2018, Klein et al., AMPPS) |
| Maslow's Hierarchy as neural design frame | Motivational taxonomy with no consistent neurobiological substrate; does not map to measured neural circuits. | Kenrick et al. 2010 reconstruction; irrelevant to mechanism-based design |
| ML classifier as mind-reader / reverse inference via trained prior — using trained ML models on EEG, GSR, or facial signals to assert specific mental states (intent, preference, emotion) | Reverse inference with a trained prior: a classifier reporting "preference" from EEG is making the same inference error as manual ERP interpretation, now amplified by small-N overfitting risk. ML does not eliminate reverse inference — it changes its surface form. Treat any vendor claim of "preference detection" or "purchase intent" from a neural classifier as requiring independent cross-study validation. | Frontiers Human Neuroscience 2025 ML/DL editorial (DOI: 10.3389/fnhum.2025.1638225); Poldrack 2011 Neuron (DOI: 10.1016/j.neuron.2011.11.001); Plassmann et al. 2015 (same family as "neuromarketing as mind reading" above) |

---

## Worked Example

**Context**: anxiety-relief subscription product, pre-purchase through day-7 retention.

**SOR layer**: The stimulus is the landing page and onboarding sequence. Target organism state is reduced threat appraisal + affiliative warmth + low cognitive load. Desired response: purchase + day-7 retention.

**Decision Journey layer**: Pre-purchase phase prioritises #5 (BIS-frame for prevention-oriented anxious users), #7 (neuroaesthetic calm register to begin deescalating arousal on entry), and #1 (top-down salience on "person like me" problem statement). Purchase moment prioritises #8 (somatic-marker close — body-state check after narrative arc), #3 (oxytocin warmth via named human), and #10 (a named daily unlock to create wanting for day-2 return). Post-purchase phase prioritises #9 (consolidation-window notification timing), #12 (format consistency to satisfy prediction priors), and #4 (brief self-referential narrative as daily content frame).

**Predictive-Coding layer**: Anxiety users have a compressed novelty budget — high prediction-error cost. The design should confirm priors on every routine interaction and reserve prediction-error violations strictly for the initial reveal (day-0 "your first insight") and milestone events. No surprise UX changes during the first 30 days.

**Reactance guardrail**: Check for countdown timers, false-scarcity copy, or dark-pattern default settings. Any freedom-limiting pattern in an anxiety-relief context has maximum reactance risk under DMCC vulnerable-user clause.

---

## Sources

- Mehrabian, A. & Russell, J. A. (1974). _An Approach to Environmental Psychology_. MIT Press.
- Bansal, S. (2025). Neuromarketing and the marketing mix. _IJCS_, TMC review citation.
- McKinsey & Company (2009). The consumer decision journey. _McKinsey Quarterly_.
- Frontiers in Neuroergonomics (2025). Consumer neuro-insights systematic review. DOI: 10.3389/fnrgo.2025.1542847.
- Lavidge, R. J. & Steiner, G. A. (1961). A model for predictive measurements of advertising effectiveness. _Journal of Marketing_, 25(6), 59–62.
- Schwarz, N. & Clore, G. L. (1983). Mood, misattribution, and judgments of well-being. _JPSP_, 45(3), 513–523.
- Damasio, A. R. (1996). _Descartes' Error_. Papermac.
- Friston, K. (2010). The free-energy principle. _Nature Reviews Neuroscience_, 11(2), 127–138.
- Clark, A. (2013). Whatever next? _Behavioral and Brain Sciences_, 36(3), 181–204.
- Higgins, E. T. (1997). Beyond pleasure and pain. _American Psychologist_, 52(12), 1280–1300.
- Brehm, J. W. (1966). _A Theory of Psychological Reactance_. Academic Press.
- Du Plessis, E. (2008). _The Advertised Mind_. Kogan Page.
- Lieberman, M. D. (2013). _Social: Why Our Brains Are Wired to Connect_. Crown.
