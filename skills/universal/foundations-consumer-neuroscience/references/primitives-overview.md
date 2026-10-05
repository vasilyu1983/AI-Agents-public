---
description: Domain-agnostic overview of the 12 behavioural hypothesis templates (primitives), each with a behavioural definition, misuse boundary and test. Neural findings are background only. For applied recipes, see downstream skills (marketing-cro, marketing-content-strategy, software-ui-ux-design, product-management, marketing-paid-advertising, startup-business-models).
status: stable
---

# Behavioural Hypothesis Templates (Primitives) Overview

## Table of Contents

- [What the Templates Are For](#what-the-templates-are-for)
- [The Ethical Frame](#the-ethical-frame)
- [Primitive Index](#primitive-index)
- [Anti-Patterns by Domain](#anti-patterns-by-domain)
- [Decision Checklist](#decision-checklist)
- [Sources](#sources)

---

## What the Templates Are For

Each template names a behavioural regularity (attention, arousal and load, social trust, narrative transportation, regulatory fit, social proof, aesthetics, felt state, memory, anticipation, embodied metaphor, expectation) and turns it into a testable product hypothesis. Neural research is background for why the regularity might exist. It is never the evidence that a design works, and a brain region is never a diagnosis of a product problem (reverse inference; Poldrack 2011).

| Failure mode | Behavioural hypothesis | What goes wrong |
|-------------|-----------------|-----------------|
| Product is well-built but invisible in a noisy feed | No relevant, differentiating cue earns attention | Attention goes to the competition; the product is present but not seen |
| Onboarding is engaging but users feel drained after 5 minutes | Too much intensity or effort with no resolution | Users associate the product with tension; perceived pressure rises |
| Referral mechanic launches with no uptake | Nothing worth sharing; no credible social reason to share | Sharing costs the sender more than it gives them |
| Personalised content gets low saves despite high reads | Content is not personally relevant or does not transport the reader | Content feels generic even if data-targeted |
| Push notification open rate drops to near zero within 2 weeks | Repetition without relevance leads to habituation; timing ignores user preference | Users classify notifications as noise |

Each template carries a misuse boundary: the same regularity that serves the user when used honestly can be turned against them.

---

## The Ethical Frame

Many of these regularities operate with little deliberation: salience capture, arousal and narrative transportation can all shape choices before people reflect. That makes them more dangerous than nudges people notice, not less.

The Thaler-Sunstein harm test (from _Nudge_, 2008), applied here:

> A technique is legitimate if it steers users toward experiences or decisions they would endorse upon reflection, can be easily overridden, and does not exploit low-deliberation processes to act against the user's interests.

When a technique works by bypassing deliberation, the ethical bar is higher, not lower. UK choice-architecture enforcement (DMCC Act) is covered in `foundations-behavioral-economics`.

Every template has a "Misuse boundary" subsection. It is not a disclaimer. It is a gate.

---

## Primitive Index

12 templates under [`../assets/templates/consumer-neuroscience/`](../assets/templates/consumer-neuroscience/).

| # | Template | Behavioural regularity (neural background, if any) | Primary design domains |
|---|-----------|-----------------|----------------------|
| 1 | [Attention & Salience](../assets/templates/consumer-neuroscience/01-attention-salience.md) | Contrast, motion and novelty capture attention; relevance holds it | Visual hierarchy, notification design, feed ranking |
| 2 | [Arousal Physiology](../assets/templates/consumer-neuroscience/02-arousal-physiology.md) | Performance falls at very low and very high activation and effort; GSR/HRV index activation, not felt arousal | Session pacing, onboarding intensity, stress cost |
| 3 | [Social Bonding](../assets/templates/consumer-neuroscience/03-social-bonding.md) | Trust follows credible, operationally true care; oxytocin→trust not replicated | Trust mechanics, care copy, referral, community |
| 4 | [Narrative Transportation](../assets/templates/consumer-neuroscience/04-narrative-transportation.md) | Transported readers counterargue less and adopt story-consistent beliefs (Green & Brock 2000; van Laer et al. 2014) | Product storytelling, personalised content |
| 5 | [Regulatory Focus & Fit](../assets/templates/consumer-neuroscience/05-approach-avoidance.md) | Frames that fit the goal (gain vs protect) raise value (Higgins 2000; Motyka et al. 2014); BIS/BAS is distinct | Copy framing, funnel framing, stated-goal segmentation |
| 6 | [Mirror Systems & Emotional Contagion](../assets/templates/consumer-neuroscience/06-mirror-systems.md) | People take cues from similar others' actions and expressions; mirror-neuron interpretations are contested | Testimonial design, UGC placement, face-based UI |
| 7 | [Neuroaesthetics](../assets/templates/consumer-neuroscience/07-neuroaesthetics.md) | Visual fluency and quality shape first impressions and inferred quality | Visual brand assets, landing page design |
| 8 | [Interoception & Somatic Markers](../assets/templates/consumer-neuroscience/08-interoception-somatic.md) | People use current feelings as information (Schwarz & Clore 1983); insula activity is non-selective | Wellness/anxiety products, error-state design |
| 9 | [Memory Consolidation](../assets/templates/consumer-neuroscience/09-memory-consolidation.md) | Spacing and retrieval practice improve recall; sleep consolidation is background only | Reminder timing, recall-primed content |
| 10 | [Reward Anticipation](../assets/templates/consumer-neuroscience/10-reward-anticipation.md) | Anticipation (wanting) can decouple from satisfaction (liking) | Daily reveals, drop mechanics, loop caps |
| 11 | [Embodied Cognition](../assets/templates/consumer-neuroscience/11-embodied-cognition.md) | Metaphors congruent with the experience are processed more fluently | Copy language, spatial UI metaphors |
| 12 | [Predictive Processing & Active Inference](../assets/templates/consumer-neuroscience/12-predictive-processing.md) | Learned expectations make consistent flows easier; unannounced changes cause errors | Feature reveals, UI consistency, change management |

---

## Anti-Patterns by Domain

### Attention & Salience

| Anti-pattern | Why it fails (behavioural) | Fix |
|-------------|-----------------|-----|
| High-contrast banner on every page element | Equal-salience items compete; nothing stands out (#1) | Give salience to one highest-priority item per view |
| Notification strategy maximising send volume for open rate | Repetition without relevance habituates users (#1) | User-chosen timing and quiet hours; personalised, relevant content |
| Motion animation on static, informational content | Motion pulls attention from what the user is reading (#1) | Reserve animation for informative state changes (progress, confirmation, error) |

### Arousal & Bonding

| Anti-pattern | Why it fails (behavioural) | Fix |
|-------------|-----------------|-----|
| Escalating intensity without resolution | Users feel drained, not engaged (#2) | Design a peak → resolution arc within each session unit |
| Warmth copy without operational care backing | Care claims that fail in practice turn into distrust (#3, #12) | Use care language only when backed by measurable care (support SLA, refund policy, transparent data use) |
| Stock-photo testimonials with scripted emotional content | Fabricated social proof; advertising-code risk; trust collapses on discovery (#6) | Verified real-user testimonials; images of actual customers |

### Narrative & Memory

| Anti-pattern | Why it fails (behavioural) | Fix |
|-------------|-----------------|-----|
| "Personal" reading delivered in generic language | Content is not personally relevant; transportation is low (#4) | Refer to specific user-provided data; test grammatical person and tense as copy variants |
| Daily streak with no reason to look forward | Completion without anticipation or satisfaction; DAU rises while liking stays flat (#10, #9) | Preview the next reveal; measure wanting and liking separately |
| Push notification late at night | Interrupts sleep and rest; a welfare harm (#9) | Respect user-selected timing and quiet hours; randomise eligible timing cohorts to test Day-7 retention |

---

## Decision Checklist

- [ ] **Which behavioural regularity is the design relying on?** (attention, arousal/load, trust, narrative, regulatory fit, social proof, aesthetics, felt state, memory, anticipation, embodied language, expectation)
- [ ] **Is attention earned or seized?** Does earning it require genuine relevance?
- [ ] **What state is the user in at entry (by self-report or behaviour)?** Is the design adding to or resolving it?
- [ ] **Are warmth and trust signals backed by operational reality?** What happens when the user tests the claim?
- [ ] **Is narrative content accurate?** Would a transported user, on reflection, endorse decisions made during immersion?
- [ ] **Does the frame fit the goal of this decision?** Is any segmentation based on a stated goal, not a proxy?
- [ ] **Are all social-proof signals from verified real users?**
- [ ] **Does aesthetic quality match functional delivery?**
- [ ] **Is any wanting-loop capped?** Has the stop signal been designed and documented?
- [ ] **Does each technique pass the harm test?** Vulnerable-user check completed?
- [ ] **What behavioural test will show whether it works?**

---

## Sources

Primary papers are the strongest evidence tier. Lab effect sizes may not transfer to product contexts; test on your own population before optimising parameters. Neural sources are listed as background, not as evidence for design moves.

- Treisman, A. M. & Gelade, G. (1980). A feature-integration theory of attention. _Cognitive Psychology_, 12(1), 97–136.
- Itti, L. & Koch, C. (2001). Computational modelling of visual attention. _Nature Reviews Neuroscience_, 2(3), 194–203.
- Yerkes, R. M. & Dodson, J. D. (1908). The relation of strength of stimulus to rapidity of habit-formation. _Journal of Comparative Neurology and Psychology_, 18(5), 459–482.
- McEwen, B. S. (2007). Physiology and neurobiology of stress and adaptation. _Physiological Reviews_, 87(3), 873–904.
- Zak, P. J. (2012). _The Moral Molecule_. Dutton.
- Carter, C. S. (2014). Oxytocin pathways and the evolution of human behavior. _Annual Review of Psychology_, 65, 17–39.
- Green, M. C. & Brock, T. C. (2000). The role of transportation in the persuasiveness of public narratives. _Journal of Personality and Social Psychology_, 79(5), 701–721.
- Buckner, R. L., Andrews-Hanna, J. R. & Schacter, D. L. (2008). The brain's default network. _Annals of the New York Academy of Sciences_, 1124(1), 1–38.
- van Laer, T., de Ruyter, K., Visconti, L. M. & Wetzels, M. (2014). The extended transportation-imagery model. _Journal of Consumer Research_, 40(5), 797–817.
- Higgins, E. T. (1997). Beyond pleasure and pain. _American Psychologist_, 52(12), 1280–1300.
- Higgins, E. T. (2000). Making a good decision: Value from fit. _American Psychologist_, 55(11), 1217–1230.
- Motyka, S. et al. (2014). Regulatory fit: A meta-analytic synthesis. _Journal of Consumer Psychology_, 24(3), 394–410.
- Poldrack, R. A. (2011). Inferring mental states from neuroimaging data. _Neuron_, 72(5), 692–697.
- Schwarz, N. & Clore, G. L. (1983). Mood, misattribution, and judgments of well-being. _JPSP_, 45(3), 513–523.
- Carver, C. S. & White, T. L. (1994). Behavioral inhibition, behavioral activation, and affective responses to impending reward and punishment. _Journal of Personality and Social Psychology_, 67(2), 319–333.
- Rizzolatti, G. & Craighero, L. (2004). The mirror-neuron system. _Annual Review of Neuroscience_, 27, 169–192.
- Damasio, A. R. (1996). _Descartes' Error_. Papermac.
- Craig, A. D. (2009). How do you feel — now? The anterior insula and human awareness. _Nature Reviews Neuroscience_, 10(1), 59–70.
- Hebb, D. O. (1949). _The Organization of Behavior_. Wiley.
- Walker, M. P. (2017). _Why We Sleep_. Scribner.
- Berridge, K. C. (2007). The debate over dopamine's role in reward: the case for incentive salience. _Psychopharmacology_, 191(3), 391–431.
- Knutson, B., Adams, C. M., Fong, G. W. & Hommer, D. (2001). Anticipation of increasing monetary reward selectively recruits nucleus accumbens. _Journal of Neuroscience_, 21(16), RC159.
- Lakoff, G. & Johnson, M. (1999). _Philosophy in the Flesh_. Basic Books.
- Barsalou, L. W. (2008). Grounded cognition. _Annual Review of Psychology_, 59, 617–645.
- Friston, K. (2010). The free-energy principle: a unified brain theory? _Nature Reviews Neuroscience_, 11(2), 127–138.
- Clark, A. (2013). Whatever next? Predictive brains, situated agents, and the future of cognitive science. _Behavioral and Brain Sciences_, 36(3), 181–204.
