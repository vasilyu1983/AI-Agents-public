---
name: foundations-consumer-neuroscience
description: Consumer-neuroscience primitives for attention, arousal, bonding, narrative, memory, and reward. Use when shaping ethical UX, neuro study design, or DMCC/AI Act gates.
compatibility: Portable core only.
version: "1.2"
last_validated: 2026-08-14
---

# Consumer Neuroscience Foundations


12 canonical consumer-neuroscience primitives for product, content, interface, and retention design. Each primitive is domain-agnostic and ethically bounded. Primitives 1–8 cover engagement-time neural responses (salience, arousal, bonding, narrative, regulatory orientation, social mirroring, aesthetics, interoception). Primitives 9–12 cover temporal and predictive mechanisms (memory consolidation, reward anticipation, embodied cognition, predictive processing). Primitive #10 (reward anticipation, Berridge "wanting" vs "liking") is intentionally distinct from `foundations-behavioral-economics` primitive #13 (reinforcement schedules / dopamine prediction-error): that skill covers schedule-of-reinforcement design; this skill covers reward-anticipation research as background for behavioral hypotheses; countdowns, reveals and product metrics do not demonstrate dopamine release. Primitive #12 (predictive processing & active inference) is the unifying primitive that grounds attention (#1), interoception (#8), and narrative (#4) under one prediction-error-minimization frame: the brain continuously generates predictions; violations of priors incur a prediction-error cost that must be "earned" by the design.

**Ethical obligation**: every primitive in this skill operates on pre-conscious or sub-deliberative neural systems. The manipulation risk is higher than for behavioral-economics nudges, because users cannot easily introspect on the mechanism. Read the Misuse Boundary subsection in each playbook before applying any technique. The test from Thaler and Sunstein: "Would you be embarrassed if the technique appeared on the front page of a newspaper?" If yes, it is exploitation, not design. The DMCC Act 2024, in force from 6 April 2025, makes online choice architecture and dark patterns directly actionable by the CMA with fines up to 10% of global annual turnover.

## When to Apply

**Apply consumer-neuroscience when:**
- Attention/salience design — first-7-second hook, visual hierarchy, modal vs inline
- Anxiety-driven engagement loops (cosmic, dating, status apps) — needs DMCC ethical audit
- Parasocial / narrative-led conversion (creator content, branded characters)
- Daily-cadence retention with timing-sensitive triggers (consolidation windows, wake-time)
- Trust repair, reciprocity, or oxytocin-bond design in social/community products

**Skip and use simpler alternatives when:**
- Pure pricing/defaults/anchoring question — foundations-behavioral-economics is sufficient and cheaper
- Audience has no measured anxiety/arousal/attention baseline — neuro framing is decoration, not insight
- B2B SaaS with rational-buyer mode dominant — emotional primitives mostly noise; use behavioral-econ + decision-theory
- The proposed mechanism manipulates without genuine user benefit — fails DMCC Act 2024 ethical gate; do not ship
- The proposed neural mechanism cannot be distinguished from simpler behavioral explanations with the available measures — test the observable behavior first
- Causal lift question — use foundations-causal-inference to measure; neuro primitives suggest mechanisms, not effect sizes

When a recommendation relies on a neural mechanism or biomarker proxy, use three
separate evidence rows: `mechanism evidence` (the process exists), `measurement
evidence` (the measure tracks it in this task), and `product-effect evidence`
(the intervention changes the user outcome). A biomarker association does not
establish the last two. For behavior-first advice that makes no neural claim,
state the behavioral outcome, study or experiment design, and causal limitation
without padding the output with neural evidence rows.

## Contents

- [Quick Reference](#quick-reference)
- [Primitive Index](#primitive-index)
- [Formal Supporting Theory](#formal-supporting-theory)
- [Ethical Bounds](#ethical-bounds)
- [Misuse Boundaries](#misuse-boundaries)
- [Decision Checklist](#decision-checklist)
- [Anti-Patterns](#anti-patterns)
- [Composition Recipes](#composition-recipes)
- [Knowledge Base & Operational Guides](#knowledge-base--operational-guides)
- [Workflow](#workflow)
- [ASCII Flow](#ascii-flow)
- [Navigation](#navigation)
- [Related Skills](#related-skills)
- [Fact-Checking](#fact-checking)

---

## Quick Reference

| # | Primitive | Core Property | When to Use |
|---|-----------|---------------|-------------|
| 1 | [Attention & Salience](assets/templates/consumer-neuroscience/01-attention-salience.md) | Bottom-up capture via contrast/novelty; top-down via relevance | Any surface where visibility or engagement priority matters |
| 2 | [Arousal Physiology](assets/templates/consumer-neuroscience/02-arousal-physiology.md) | Yerkes-Dodson inverted-U; autonomic cost; GSR as autonomic activation, with unknown valence | Engagement loop design; onboarding intensity calibration |
| 3 | [Social Bonding](assets/templates/consumer-neuroscience/03-social-bonding.md) | Affiliation and perceived care hypotheses; no interface-to-oxytocin inference | Trust mechanics, warmth signals, share/referral features |
| 4 | [Narrative Transportation](assets/templates/consumer-neuroscience/04-narrative-transportation.md) | DMN + vmPFC + ventral striatum absorb self-referential story | Personalized content, horoscopes, product storytelling |
| 5 | [Approach-Avoidance & BIS/BAS](assets/templates/consumer-neuroscience/05-approach-avoidance.md) | BIS/BAS and promotion/prevention focus are distinct constructs; validate the task-relevant measure | Copy tone for mixed-orientation audiences; funnel segmentation |
| 6 | [Mirror Systems & Emotional Contagion](assets/templates/consumer-neuroscience/06-mirror-systems.md) | Social perception and emotional-response research; measure local behavioral outcomes | Testimonial design, UGC placement, avatar/face elements |
| 7 | [Neuroaesthetics](assets/templates/consumer-neuroscience/07-neuroaesthetics.md) | Aesthetic-response research; local visual preference hypotheses | Visual hierarchy, brand asset design, landing page aesthetics |
| 8 | [Interoception & Somatic Markers](assets/templates/consumer-neuroscience/08-interoception-somatic.md) | Body-state research; no neural diagnosis from UX proxies | Wellness/anxiety product design; gut-feel purchase triggers |
| 9 | [Memory Consolidation](assets/templates/consumer-neuroscience/09-memory-consolidation.md) | Hebbian potentiation + sleep replay strengthen traces | Sleep-respecting reminders and recall-based content hypotheses |
| 10 | [Reward Anticipation](assets/templates/consumer-neuroscience/10-reward-anticipation.md) | reward-cue responses depend on task and measurement; wanting distinct from liking | Countdown UX, drop reveals, daily unlock mechanics |
| 11 | [Embodied Cognition](assets/templates/consumer-neuroscience/11-embodied-cognition.md) | Sensorimotor grounding of abstract concepts; body-state metaphors | Copy language, spatial UI metaphors, product texture cues |
| 12 | [Predictive Processing & Active Inference](assets/templates/consumer-neuroscience/12-predictive-processing.md) | Computational hypotheses; no UX precision diagnosis or surprise-cost budget | Feature reveals, onboarding surprises, brand consistency |

---

## Primitive Index

Each primitive has a full playbook: Definition / When to use / Misuse boundary / Inputs / Outputs / Failure modes / Worked example / Sources.

| # | Primitive | Failure Mode It Addresses |
|---|-----------|--------------------------|
| 1 | [Attention & Salience](assets/templates/consumer-neuroscience/01-attention-salience.md) | Designs that assume attention is granted, not earned |
| 2 | [Arousal Physiology](assets/templates/consumer-neuroscience/02-arousal-physiology.md) | Engagement loops that ignore stress cost on the user |
| 3 | [Social Bonding](assets/templates/consumer-neuroscience/03-social-bonding.md) | Trust/share mechanics built without warmth signals |
| 4 | [Narrative Transportation](assets/templates/consumer-neuroscience/04-narrative-transportation.md) | "Personal-feeling" content reduced to facts and lists |
| 5 | [Approach-Avoidance & BIS/BAS](assets/templates/consumer-neuroscience/05-approach-avoidance.md) | Single-tone funnels for mixed promotion/prevention users |
| 6 | [Mirror Systems & Emotional Contagion](assets/templates/consumer-neuroscience/06-mirror-systems.md) | Testimonials and UGC ignored as conversion lever |
| 7 | [Neuroaesthetics](assets/templates/consumer-neuroscience/07-neuroaesthetics.md) | Aesthetic choices justified by taste, not neural response |
| 8 | [Interoception & Somatic Markers](assets/templates/consumer-neuroscience/08-interoception-somatic.md) | "Gut-feel" decisions ignored as design surface |
| 9 | [Memory Consolidation](assets/templates/consumer-neuroscience/09-memory-consolidation.md) | Reminders and streaks that fight consolidation timing |
| 10 | [Reward Anticipation](assets/templates/consumer-neuroscience/10-reward-anticipation.md) | Anticipation phase ignored in favor of payoff |
| 11 | [Embodied Cognition](assets/templates/consumer-neuroscience/11-embodied-cognition.md) | Copy and UI ignoring body-state metaphors |
| 12 | [Predictive Processing & Active Inference](assets/templates/consumer-neuroscience/12-predictive-processing.md) | Surprises that violate user priors without earning the prediction-error budget |

---

## Formal Supporting Theory

| Theory Area | Use When | Applied Primitives It Grounds |
|---|---|---|
| Attention theory (Feature Integration Theory, salience maps) | Need to predict what captures or loses user attention | #1 |
| Psychophysiology & autonomic regulation (Yerkes-Dodson, allostatic load) | Need to calibrate engagement intensity without imposing stress cost | #2 |
| Social neuroendocrinology (oxytocin system, affiliative circuits) | Need to understand trust formation or prosocial behavior in product | #3 |
| Narrative cognition & Default Mode Network (DMN, vmPFC, ventral striatum) | Need to design self-referential or immersive content | #4 |
| Regulatory focus & BIS/BAS (Higgins, Carver & White) | Need to distinguish promotion-oriented from prevention-oriented users | #5 |
| Mirror neuron system & emotional contagion (MNS, FFA) | Need to understand social simulation in testimonials or face-based UI | #6 |
| Neuroaesthetics (peak-shift, symmetry, contour, reward from visual beauty) | Need to explain or predict aesthetic preference and visual reward | #7 |
| Interoception & somatic marker theory (Craig insular cortex, Damasio vmPFC) | Need to account for body-state signals in purchase or risk decisions | #8 |
| Systems memory consolidation & sleep-dependent replay (Hebbian, hippocampal-neocortical transfer) | Need to design for durable trace formation — not just exposure | #9 |
| Incentive salience & wanting vs liking (Berridge mesolimbic dopamine, VTA) | Need to distinguish anticipatory drive from hedonic reward | #10 |
| Embodied / grounded cognition (Lakoff & Johnson, Barsalou) | Need to align copy or UI metaphors with sensorimotor experience | #11 |
| Predictive processing & active inference (Friston free energy, Clark, Constant) | Need to manage prediction-error budget: when to surprise, when to confirm | #12 |

Use [`references/formal-theory-map.md`](references/formal-theory-map.md) when the task needs source assumptions, ethical boundaries, or a distinction between observed neural response and normative welfare.

---

## Ethical Bounds

### The Harm Test

A neural design technique is legitimate if it:

1. Steers users toward experiences or decisions they would endorse on reflection.
2. Can be easily overridden or opted out of.
3. Does not exploit pre-conscious neural mechanisms to act against the user's interests.

The same lever — arousal, oxytocin warmth, reward anticipation — can be legitimate or manipulative depending on whether the underlying offer genuinely serves the user.

### Manipulation vs Legitimate Design

| Dimension | Legitimate | Manipulation |
|-----------|-----------|--------------|
| Transparency | Mechanism can be disclosed without destroying the effect | Requires concealment of mechanism to work |
| User-benefit alignment | Steers toward user's own stated goals or wellbeing | Overrides user goals in favor of operator revenue |
| Reversibility | Easy to disengage, unsubscribe, or undo | Designed to make exit costly or invisible |
| Signal honesty | Arousal, urgency, or warmth reflects real content | Signal is manufactured (fake countdown, artificial scarcity, paid "warmth") |
| Regulatory posture | Survives CMA/ASA/ICO scrutiny | Attracts DMCC Act enforcement action |

### UK Regulatory Context (August 2026)

**DMCC Act 2024** entered into force **6 April 2025**, **revoking** the CPRs 2008 outright (s.251(1), commenced by SI 2025/272) and succeeding them with ss. 226 (misleading actions), 227 (misleading omissions), and 228 (aggressive practices), plus the Sch. 20 list of banned practices. The successor provisions are redrafted, not a restatement — old CPRs regulation numbers do not map across cleanly, so cite DMCC sections. The CMA has direct civil-enforcement power and can fine **up to 10% of global annual turnover** without requiring a court order.

Enforcement is now live, not prospective — the first two infringement decisions both concerned online choice architecture rather than advertising content:

- **18 November 2025**: CMA opened its first DMCC enforcement actions against 8 firms (drip pricing, default opt-ins, pressure selling) and issued approximately 100 advisory letters across 14 sectors.
- **18 June 2026**: second infringement decision — **Marks Electrical fined £720,000** (£1.2m reduced 40% for early settlement) and ordered to refund ~£600,000 to ~40,000 customers, for **pre-selected extra charges** (customers auto-opted into paid recycling and unwrapping services). Conduct covered April–November 2025. This is the clearest signal of the enforcement floor: a mid-size retailer, a single default-opt-in pattern, a seven-figure headline penalty plus consumer redress.

**April 2025**: CMA published procedural guidance on DMCC enforcement. **December 2025**: CMA published price transparency guidance under DMCC.

Online Choice Architecture (dark patterns) now directly actionable under DMCC, including:
- Confirm-shaming (manipulative framing on decline options)
- Pre-ticked defaults that benefit the operator at user expense
- Drip pricing (incremental price reveal late in purchase flow)
- False urgency ("Only 2 left!" when stock is unconstrained)
- Forced continuity (auto-renew without prominent disclosure)

Secondary regulatory anchors:
- **ASA CAP Code**: misleading advertising, fabricated testimonials, manufactured social proof
- **DMCC Act 2024 s.228** (aggressive practices — replaced CPRs 2008 Reg. 7, revoked 6 April 2025)
- **UK GDPR**: classify personal data and its processing purpose. Health inference or biometric unique identification may require an Article 9 condition in addition to an Article 6 basis; not every physiological signal is special-category data and explicit consent is not the only possible condition. Informed research participation is a separate requirement.

### EU Regulatory Context (August 2026)

For products serving EU users, the **EU AI Act** is the parallel anchor to DMCC and applies on top of GDPR.

- **Article 5 prohibitions in force from 2 February 2025**: AI systems that deploy "subliminal techniques beyond a person's consciousness" or "purposefully manipulative or deceptive techniques" causing significant harm are prohibited outright. AI systems that exploit vulnerabilities (age, disability, socio-economic situation) are also prohibited. This directly captures the manipulation column of the table above when AI is in the loop. Unaffected by the 2026 delay below — the prohibitions bind now.
- **Emotion-recognition classification**: sensor capture alone does not establish a regulated system. Workplace/education emotion inference raises Article 5(1)(f), including its medical/safety exception; review intended purpose and current text with qualified counsel.
- **High-risk applicability and dates**: classify intended use before choosing a compliance schedule. The Commission confirms the adopted Omnibus timeline; see the dated [classification and source note](references/ethics-operational-checklist.md#dated-eu-classification-source-note). Vendor names and sensor types are not legal classifications.
- **Transparency**: assess applicable Article 50 obligations separately from high-risk status. For relevant deployers, notices address the operation of the system at first interaction/exposure; earlier notice before capture is our research safeguard. Apply current exceptions and transitions only after legal review.
- **GDPR continues to apply**: document the Article 6 basis and any applicable Article 9 condition after assessing health inference and unique-identification purposes. The AI Act does not replace this classification.

For UK-only products, DMCC + UK GDPR are sufficient. For EU users or shared-stack products, both regimes apply and the **stricter** rule binds.

### US Regulatory Context (August 2026)

Four states have enacted neural-data-specific privacy laws (Colorado, California, Montana, Connecticut), and nine further bills were introduced across six states in the first six weeks of 2026 alone (Alabama, California, Illinois, New York, Vermont, Virginia). Treat this as a live patchwork, not a settled regime.

**Scope caution — these laws are narrower than "any biometric signal."** Most define neural data as signals from the nervous system measured directly, and several explicitly exclude the downstream physiological signals this skill most often uses. Montana SB 163 carves out "nonneural information … the downstream physical effects of neural activity, including but not limited to pupil dilation, motor activity, and breathing rate" — which excludes GSR and eye-tracking. California SB 1223 requires neural data be "not inferred from nonneural information," likely excluding facial coding and voice affect. Colorado's definition reaches only data used for **identification** purposes, excluding most consumer applications. Connecticut has no explicit carve-out, leaving GSR and eye-tracking ambiguous there. **Practical consequence**: EEG and fNIRS are squarely in scope; GSR, HRV, eye-tracking, facial coding, and voice affect are mostly *out* of neural-data statutes — but remain covered by general state biometric/sensitive-data law, BIPA-style statutes, and GDPR for EU users. Do not use a neural-data-law exemption as a reason to skip consent; check the general privacy regime instead.

- **California SB 1223** (effective **1 January 2025**): amends CCPA to classify "neural data" (signals from central or peripheral nervous system, not inferred from nonneural information) as sensitive personal information. Opt-in consent required; right to delete and restrict sharing apply. [Primary source](https://leginfo.legislature.ca.gov/faces/billNavClient.xhtml?bill_id=202320240SB1223)
- **Colorado HB 24-1058** (effective **7 August 2024**): amends Colorado Privacy Act to include "neural data" within "biological data" as sensitive data. First US law to define and protect neural data. Scope limited to data used or intended for identification. [Primary source](https://leg.colorado.gov/bills/hb24-1058)
- **Montana SB 163** (effective **1 October 2025**): adds neurotechnology data to Montana's Genetic Information Privacy Act. The **most extensive** of the four: detailed express-consent requirements for collection, marketing and research use, disclosure, transfer, and sale — often requiring separate informed consent per purpose and per third party. Explicitly excludes nonneural downstream signals. If a product captures true neural data from US users, Montana sets the strictest operative bar.
- **Connecticut SB 1295** (signed **24 June 2025**; effective **1 July 2026**): amends CTDPA to add neural data as a sensitive data category; processing requires express consumer consent; selling sensitive data without consent prohibited. [Primary source](https://natlawreview.com/article/connecticut-amends-connecticut-data-privacy-act)
- **Vermont H.814 / Act 101** (signed **18 May 2026**; effective **1 July 2026**): **correction — do not overstate this law.** As enacted, H.814 was substantially narrowed in the Senate: it recognises a largely declaratory statement of "neurological rights" (mental privacy, freedom of thought, non-discrimination in neurotechnology), but the **consent requirement and private right of action were stripped** before passage. Enforcement rests exclusively with the Vermont Attorney General; there is no consent gate for businesses. Its main forward hook is a commissioned study reporting to the next legislative session. Vermont's binding neural-data framework is **Vermont S.71** (neural data as sensitive data), effective **1 January 2028** — track that bill, not H.814, for compliance planning. Treat H.814 as a signal of legislative direction, not a live consent gate. [Primary source](https://www.cooley.com/news/insight/2026/2026-06-23-from-maple-to-mind-taps-new-vermont-law-puts-neurotech-on-notice)
- **UNESCO Recommendation on the Ethics of Neurotechnology** (adopted **12 November 2025**): first global non-binding framework covering neural data across commercial uses. Non-binding but widely cited in board-level compliance discussions and DPA engagement. [Primary source](https://www.unesco.org/en/legal-affairs/recommendation-ethics-neurotechnology)
- **US MIND Act 2025** (proposed): would direct FTC to study neuromarketing as a named use case; not yet law but signals federal regulatory attention. Document FTC-readiness posture if product involves neuromarketing explicitly.

**Practical implication**: any product capturing genuine neural signal (EEG, fNIRS) from US users must run a per-state consent analysis — California CCPA sensitive PI from 1 January 2025, Montana's per-purpose express consent from 1 October 2025, Colorado and Connecticut in parallel. For GSR, HRV, eye-tracking, facial coding, and voice affect, the neural-data statutes mostly do not bite; the governing constraints are general sensitive-data and biometric law plus purpose-specific GDPR classification for EU users. See `references/ethics-operational-checklist.md` US Neural Data Laws section.

### Vulnerable-User Note

CMA enforcement priorities specifically name "aggressive sales practices which take advantage of vulnerability." Wellness, anxiety-relief, and astrology/spiritual audiences are explicitly in scope as vulnerability-risk contexts. EU AI Act Article 5 reinforces this with an outright prohibition on AI systems that exploit vulnerabilities of specific groups (age, disability, socio-economic situation) to materially distort behaviour. Any application in these categories must apply the stricter column of the manipulation table — not the middle ground. Manufactured urgency, oxytocin-proxy warmth without genuine care mechanics, and reward-anticipation loops targeting financially or emotionally vulnerable users are highest-risk under both regimes.

---

## Misuse Boundaries

| Misuse | Why It Is Wrong | Required Correction |
|---|---|---|
| Manufacturing arousal without informational value (#2) | GSR spike earned by stimulus intensity, not content quality — violates prediction-error budget and harms user attention economy. Note: GSR/HRV-as-arousal-proxy claims require qualification — BAAS (Nature Communications 2025, 24-study validation) confirms autonomic signals are statistically distinct from subjective affective arousal; interpret autonomic signals as physiological activation, not as direct proxies for the subjective arousal consumers experience | Earn arousal through genuine novelty or high personal relevance; measure dwell quality, not just engagement duration; acknowledge GSR/HRV–affective-arousal dissociation in any study claiming arousal measurement |
| Exploiting oxytocin proxies without genuine warmth (#3) | Artificial warmth signals (faked testimonials, performed care language) produce short-term affiliation that collapses on discovery, destroying trust. Claiming universal oxytocin-driven trust from warmth signals overstates the evidence; the Declerck 2020 registered replication (Nature Human Behaviour, >95% power) found no main effect of oxytocin on trust under standard conditions — design for genuine warmth and affiliative behavior, not a neuroendocrine mechanism the replication literature does not support uniformly | Use only real social proof and care signals; peripheral oxytocin kinetics do not establish a copy-refresh or trust-maintenance interval; do not claim design patterns universally increase trust via oxytocin mechanism |
| Narrative transport without consent (#4) | DMN immersion suppresses critical evaluation — delivering false information during transportation is a manipulation under DMCC | Narrative content must be accurate; emotional immersion does not override disclosure obligations |
| Physiological personal-data capture without lawful processing (#2, #8) | Data status depends on purpose and inference; physiology is not automatically special-category biometric data | Document Article 6 basis, assess health/identification processing and applicable Article 9 condition; obtain informed research participation separately |
| Single-tone funnel for mixed BIS/BAS audience (#5) | Prevention-oriented users subjected to unrelenting promotion framing experience regulatory mismatch; trust drops | Segment or test copy by regulatory focus; offer prevention-framed and promotion-framed variants |
| Fabricating social contagion signals (#6) | Showing false emotional reactions (fake ratings, manufactured "people are loving this") triggers mirror system without real social proof | All emotional-contagion signals must reflect real user sentiment from verified cohort data |
| Neuroaesthetic dopamine trap — aesthetic beauty without functional value (#7, #10) | Highly polished aesthetics trigger visual reward and reward anticipation; if the underlying product fails to deliver, disappointment amplifies by contrast (prediction error) | Aesthetic quality must be matched by functional delivery; do not use visual reward to paper over a weak product |
| False-prediction surprise (#12) | Violating established user priors without earning the prediction-error budget creates confusion, anxiety, and trust loss | Predict before you surprise; reserve prediction-error violations for high-value reveals backed by strong prior evidence of user benefit |
| Interoceptive exploitation in vulnerable users (#8) | Triggering somatic anxiety signals ("your body is telling you something is wrong") in wellness/anxiety contexts to manufacture urgency is manipulation under DMCC vulnerable-user clause | Do not manufacture somatic urgency; if body-state signals are referenced, they must reflect real data or established scientific context |
| Reward anticipation loops without ceiling (#10) | Unbounded wanting loops (infinite scroll, endless daily unlocks) exploit mesolimbic anticipation without a natural satiation point — compulsion-design risk | Design explicit satiation signals; rate-cap anticipation mechanics; gate any wanting-loop design behind a harm-test sign-off |
| AI-driven affect inference without a classification record (#2, #6, #8) | Inputs, intended purpose, context and deployment determine applicable obligations | Record purpose-specific legal classification, applicable notices, prohibitions and timeline with qualified counsel; avoid vendor-based conclusions |

Check [`references/patterns-scenarios-traps.md`](references/patterns-scenarios-traps.md) before applying primitives to production user flows.

---

## Decision Checklist

- [ ] **Attention earned**: Is the design earning attention through genuine relevance or novelty, not bottom-up hijacking? → attention & salience (#1)
- [ ] **Arousal calibration**: Is the engagement intensity appropriate for the decision being made? Will the arousal level impair or support the user's goal? → arousal physiology (#2)
- [ ] **Warmth signals**: Are trust and affiliation signals real? Is any warmth mechanic backed by genuine social data? → social bonding (#3)
- [ ] **Narrative accuracy**: If the experience transports users emotionally, is the content accurate? Does immersion serve or obscure the user's interests? → narrative transportation (#4)
- [ ] **Regulatory orientation**: Does the audience skew BIS (prevention) or BAS (approach)? Is the primary message tone matched to the audience's dominant orientation? → approach-avoidance (#5)
- [ ] **Social proof quality**: Are testimonials, reactions, and contagion signals from real users in verified data? → mirror systems (#6)
- [ ] **Aesthetic-to-delivery ratio**: Does visual quality match functional delivery? Is aesthetic reward being used to compensate for a weak product? → neuroaesthetics (#7), reward anticipation (#10)
- [ ] **Interoceptive framing**: Is any body-state or "gut feel" framing based on real signals? Is it used to inform, not to manufacture anxiety? → interoception (#8)
- [ ] **Consolidation timing**: Do reminders respect user timing and quiet hours, and has any claimed memory benefit been tested? → memory consolidation (#9)
- [ ] **Wanting vs liking balance**: Is reward anticipation matched by hedonic payoff? Is the anticipation loop capped to prevent compulsion? → reward anticipation (#10)
- [ ] **Embodied language**: Does copy use body-state metaphors congruent with the product experience? → embodied cognition (#11)
- [ ] **Prediction-error budget**: Does the design surprise users only when it has earned the attentional cost? Are established priors preserved during routine use? → predictive processing (#12)
- [ ] **Ethical gate**: Does each technique pass the harm test? Does it survive DMCC scrutiny for vulnerable-user contexts? → ethical bounds section

---

## Anti-Patterns

| Anti-Pattern | Neural Diagnosis | Fix |
|-------------|-----------------|-----|
| Salience hijack without informational reward | Bottom-up capture via contrast/motion violates user prior; attention cost is charged, no prediction-error budget earned (#1, #12) | Use bottom-up salience only when the destination genuinely warrants attentional priority |
| Engagement-loop that never decelerates | Sustained arousal above Yerkes-Dodson optimum drives autonomic stress, not engagement; user associates product with tension (#2) | Build explicit arousal arcs — peak then resolve; do not maintain maximum arousal across full sessions |
| Warmth language without real care mechanics | Warmth copy may influence perceived care, but does not demonstrate oxytocin release; when care is not operationally real, trust destruction is sharper than if no warmth was claimed (#3) | Warmth signals must be backed by actual product behavior: support quality, error recovery, data transparency |
| Narrative immersion used to obscure material terms | Narrative transportation can reduce counterarguing in some tasks; DMN activity alone does not establish suppressed critical evaluation; inserting T&C or pricing in high-immersion narrative flow exploits the suppression (#4) | Material disclosures must occur at low-narrative-load moments; never embed key terms inside story content |
| Single promotional tone for prevention-oriented users | BIS-dominant users interpret promotion-framed copy as threat of insufficient caution; conversion collapses in prevention segments (#5) | Test BAS vs BIS copy variants; offer safety-frame and gain-frame alternatives |
| Testimonial using stock photography or unverified claims | Unverified faces or claims can misrepresent user experience; perceived authenticity and affect are behavioral hypotheses, not established neural warmth (#6) | All testimonials from real verified users; face images from actual customers or replaced with abstract representation |
| Over-polished aesthetics masking under-built product | Visual beauty response releases reward signal; prediction error on first real product interaction is amplified by contrast (#7, #12) | Aesthetic investment must be proportional to functional delivery; do not use polish to buy credibility the product has not earned |
| Push notifications sent for engagement metrics at maximum-interruptibility time | Sleep can support consolidation; notification timing alone does not establish interrupted replay or a negative product association (#9) | Respect user-selected timing and quiet hours; measure timing effects without claiming a consolidation mechanism |
| Wanting loop without satiation design | Open-ended engagement loops can conflict with user goals; investigate reported difficulty stopping, perceived value and harm without inferring dopamine activity (#10) | Provide explicit stopping signals; rate-cap unlock chains; require harm-test sign-off for any open-ended anticipation loop |
| Body-metaphor copy mismatched to product experience | "Lighten your load" applied to a cognitively demanding feature; incongruent embodied metaphor creates cognitive interference (#11) | Map body-state metaphors to the actual sensorimotor experience the product produces |
| Surprise release without prior expectation-setting | Novel feature or UI change without priming violates prediction priors; attentional cost is maximal; anxiety not excitement is the more likely response in cautious users (#12) | Prime before reveal: build the prior (teasers, waitlist, progress signals) so the reveal is a confirmation, not a shock |
| "Neuro-marketing" claim with no mechanism named | Marketing veneer — "scientifically designed for engagement" with no primitive, circuit, or evidence named; same as behavioral-economics habit-loop abuse (#1–#12) | Default to a behavioral/usability hypothesis. Require separate mechanism, measurement-validity and product-intervention evidence before making a neural claim; a circuit name and citation alone are insufficient |

---

## Composition Recipes

### Recipe 1: Anxiety-Relief Consumer Loop (pre-purchase)

**Goal**: guide an anxiety-experiencing user through a reassurance journey to a confident purchase decision, without manufacturing or amplifying anxiety.

**Stack**:
1. **Arousal physiology (#2)**: Use the user’s stated need or an appropriately validated baseline; do not assume elevated arousal from product category. Design the entry experience to begin deescalating arousal — calm visual pacing, low-contrast background, short sentence length. Do not spike arousal at entry.
2. **Predictive processing (#12)**: Establish clear product-structure priors immediately. Anxious users have a high prediction-error cost; predictability is reassurance. Consistent layout, no hidden elements.
3. **Narrative transportation (#4)**: Use a "person like me" story (brief, first-person, past-tense) in which anxiety was the starting state and resolution was the outcome. DMN engagement with a self-relevant arc reduces threat appraisal.
4. **Social bonding (#3)**: Introduce real human warmth — a named support person, a real community count, a genuine care statement backed by operational reality (response time, refund policy). Do not infer endocrine response or a refresh interval from warmth copy.
5. **Interoception (#8)**: Close with a body-state check cue ("How do you feel right now?") that invites somatic attention; let the user register their own shift. This is the somatic marker that encodes the product association positively.

**Ethical-bound check**: The anxiety being relieved must be real. Do not manufacture anxiety (#2 misuse) to then relieve it. DMCC vulnerable-user test must pass: would the CMA say this practice takes advantage of vulnerability?

**Fail signal**: "felt scammed" or "felt manipulated" qualitative reports; CSAT drop post-purchase; CMA/ASA complaint volume rising.

**Inputs:** User-reported need and baseline state; proposed reassurance mechanism; task-comprehension outcome; retention and harm measures; competing behavioral explanations. Do not assume anxiety or infer it from product category.
**Rules:** Define a user-approved reassurance goal and test time-to-comprehension and perceived pressure. No cortisol-derived 90-second deadline is supported. Avoid manufacturing anxiety or variable resolution to compel re-checking; assess actual harms and the applicable legal criteria.
**Outputs:** Proposed reassurance flow; a fit-for-purpose self-report measure with scoring and limitations; controlled comparison of comprehension, satisfaction and perceived pressure; documented ethical review. A custom 1–5 item is not the validated Perceived Stress Scale.

---

### Recipe 2: Parasocial Reading Bond (purchase)

**Goal**: generate a genuine reading bond between user and content (horoscope, tarot, interpretive reading) that drives purchase and repeat engagement without deception.

**Stack**:
1. **Narrative transportation (#4)**: Open with a brief orienting narrative that primes the DMN. The reading itself should use second-person, present-tense framing to maximize self-referential processing in vmPFC.
2. **Mirror systems (#6)**: Include at least one face or depicted emotional state that matches the emotion the user is likely experiencing. FFA activation and MNS simulation generate social presence with a non-present author.
3. **Social bonding (#3)**: "Others who received this reading reported..." — real cohort social framing; affiliative warmth through shared experience, not manufactured intimacy.
4. **Embodied cognition (#11)**: Copy uses body-state metaphors grounded in the product's actual experience ("a weight lifts," "clarity settles in") — not random metaphors.

**Ethical-bound check**: Content accuracy: predictive or interpretive content must be labeled as such (ASA CAP Code; no false claims of scientific accuracy). Social data must be real. Face imagery must be genuine or clearly illustrative.

**Fail signal**: Low share rate despite high session time — narrative bond did not activate social-contagion desire; revisit mirror system (#6) and real social proof (#3).

**Inputs:** Content format, user-stated need, verified social-proof artifacts, proposed timing, behavioral baseline and competing explanations. Do not assume DMN engagement from emotional priming.
**Rules:** Treat framing, imagery and social-proof placement as behavioral hypotheses to test. No grammatical person or tense is biologically required for vmPFC processing. Use genuine, labeled illustrative or verified imagery; distinguish regulatory focus from BIS/BAS and do not infer either from referral source alone.
**Outputs:** Proposed narrative and social-proof sequence; preregistered share/comprehension/value outcomes; local controlled results and uncertainty. Do not label a content cohort “high-DMN” without validated neural measurement.

---

### Recipe 3: Daily-Cadence Retention (post-purchase)

**Goal**: build a voluntary daily engagement habit that the user values, without compulsion design.

**Stack**:
1. **Reward anticipation (#10)**: Design a daily reveal or unlock that creates genuine wanting — a named card, a daily insight, a progress update. reward-cue responses depend on task and measurement; the anticipation, not just the content, is the engagement driver. Cap the chain; provide explicit completion signals.
2. **Memory consolidation (#9)**: Let users select cue timing and quiet hours; test timing without assuming a clock-defined consolidation window. Measure Day-7 and Day-30 retention as a function of notification timing cohort.
3. **Attention & salience (#1)**: The daily notification must use top-down salience (user-relevant, personalized, named) rather than bottom-up salience (loud, high-contrast interruption). Bottom-up salience for a recurring cue trains the user to dismiss it.
4. **Predictive processing (#12)**: Maintain strong format consistency across daily units. Prediction satisfaction — the cue arriving as expected, in expected form — is itself rewarding. Reserve genuine novelty for special events.

**Ethical-bound check**: Wanting loop must have a ceiling. Consolidation-window timing must not interrupt sleep. Notifications must be easy to disable (DMCC reversibility test).

**Fail signal**: Streak completion rate high but re-engagement intent (next-session survey) is low — user is mechanically completing a streak, not experiencing genuine wanting; wanting loop has decoupled from liking.

**Inputs:** Daily content and actual user value; user-selected timing and quiet hours; baseline retention; proposed completion/cadence defaults and their rationale.
**Rules:** No universal notification clock window follows from consolidation research. Respect sleep, quiet hours and user preference; randomize eligible timing cohorts. Choose and disclose any consistency target or unlock cap as a product/safety default, with review criteria; do not present it as a neural threshold.
**Outputs:** Timing-cohort comparison with retention, task value, opt-out and sleep-interruption measures; documented completion/cadence default; uncertainty and ethical decision. Cap activity alone is not evidence of reduced harm.

---

### Recipe 4: Conversion Landing Page, Mixed Audience (pre-purchase)

**Goal**: maximize conversion across a mixed BAS (promotion-seeking) and BIS (prevention-vigilant) audience without a single-tone funnel.

**Stack**:
1. **Attention & salience (#1)**: Above-the-fold uses top-down salience cues (problem statement that matches user prior, personal pronoun "you"). No bottom-up salience noise at entry.
2. **Approach-avoidance / BIS/BAS (#5)**: Headline A/B: promotion frame ("Unlock daily clarity") vs prevention frame ("Never miss an important day again"). BAS users convert on approach; BIS users convert on prevention. Test or personalize by referral source signal.
3. **Neuroaesthetics (#7)**: Visual design uses peak-shift on key differentiating visual element; symmetry in layout; color palette empirically associated with target emotional register (calm, warmth, or energy — product-appropriate). Aesthetic reward at first glance reduces the cognitive cost of reading on.
4. **Mirror systems (#6)**: Testimonials use real face + real emotional expression matching the resolution state (relief, clarity, confidence). MNS simulation must match the emotion, not just any positive face.

**Ethical-bound check**: BIS prevention framing must not manufacture threat. Testimonials must be real. Aesthetic quality must be matched by functional delivery.

**Fail signal**: Bounce concentrated in one regulatory-focus segment — BIS vs BAS mis-match; check copy tone against BIS/BAS segmentation data.

**Inputs:** Audience task and stated priorities, copy-test evidence, verified testimonials and behavioral baseline. An arbitrary 50/50 split is not a measured orientation distribution.
**Rules:** Test gain- and safety-framed variants when the decision context justifies them. Regulatory focus and BIS/BAS are distinct constructs; referral source is not a validated classifier. Use real testimonials and measure comprehension, value and pressure as well as conversion.
**Outputs:** A/B copy variant results (BAS-frame vs. BIS-frame conversion rate by segment); cohort split by referral-source BIS/BAS proxy; ethical pass/fail flag (testimonials verified, no manufactured urgency, aesthetic-to-delivery ratio documented).

---

### Recipe 5: Trust Repair After Error (post-purchase)

**Goal**: restore trust after a product error or service failure without manipulating the user into false forgiveness.

**Stack**:
1. **Social bonding (#3)**: Acknowledge the failure with a named human voice, not a system message. Oxytocin affiliative response requires social presence; automated impersonation of warmth makes trust repair harder. Real person acknowledgment.
2. **Interoception (#8)**: Invite the user to describe their experience before offering a resolution. Somatic marker theory: the user's decision to continue is encoded in body state; helping them articulate and feel heard changes the somatic marker from threat to acknowledgment.
3. **Predictive processing (#12)**: Provide an explicit account of what failed and what changed. The violation was a prediction error; closing it requires a new, more reliable prior — not just an apology, but a systemic explanation that earns a revised trust prior.
4. **Approach-avoidance / BIS (#5)**: BIS-dominant users in error contexts are running prevention-mode appraisals; frame resolution in prevention terms ("We've put a safeguard in place so this cannot recur") not only gain terms ("Here's what you get now").

**Ethical-bound check**: Do not use warmth signals to gloss over a genuine product failure without fixing the underlying issue. The repair must be real.

**Fail signal**: Persisting user-reported harm, unresolved operational errors or reduced trust despite the remedy. An NPS change does not diagnose a somatic-marker shift.

**Inputs:** Incident severity and user impact; available support channels; operational fix; baseline outcome measures and uncertainty. Do not assume all incident users share a prevention-mode state.
**Rules:** Acknowledge the error accurately and identify the responsible service or person without impersonation. Choose response-time and compensation targets from severity, user needs and service constraints; there is no 200ms oxytocin/eye-contact rule or universal repair ratio. Explain the fix and allow user-directed escalation.
**Outputs:** Accurate acknowledgment, explanation, remedy and prevention steps; change in trust/task outcomes with baseline and uncertainty; user feedback and unresolved issues. Predeclare service-specific recovery targets rather than a universal NPS percentage.

---

### Recipe 6: DMCC Compliance Audit

**Goal**: confirm any recipe applying neuroscience primitives passes the DMCC Act 2024 harm test before shipping.

**Stack**:
1. Apply the Ethical Bounds harm test (three gates: user endorsement on reflection, easy reversal, no exploitation of pre-conscious mechanisms against user interests).
2. Check against Online Choice Architecture dark-pattern list: confirm-shaming? pre-ticked defaults? drip pricing? false urgency? forced continuity?
3. Vulnerable-user check: is the target audience in a wellness, anxiety, or financially sensitive context? If yes, apply the stricter manipulation-table column throughout.
4. Biometric/neuro capture check: does the design, research plan, or analytics pipeline capture GSR, HRV, eye-tracking, or facial EMG? If yes, classify purpose and inference, document Article 6 basis and any applicable Article 9 condition before deployment.
5. Anticipation-loop cap check: does any wanting mechanic (#10) have explicit satiation signals and a rate-cap? Document the cap in the design spec.
6. Signal honesty check: are all arousal (#2), warmth (#3), urgency (#6 from behavioral-economics), and social-contagion (#6) signals verifiable and accurate?

**Ethical-bound check**: this recipe IS the harm-test. Fail signal: any "yes" on the dark-pattern list, any vulnerable-user trigger without stricter-side controls, personal-data processing without an Article 6 basis or special-category processing without an applicable Article 9 condition.

**Inputs:** Design spec or recipe output under audit (UX flow, copy variants, notification timing plan, anticipation-loop design); content type and audience context (wellness/anxiety/spiritual = vulnerable-user flag triggered); biometric/neuro-signal capture plan if any (GSR, HRV, eye-tracking, facial EMG); notification timing options as specified in the design.
**Rules:** All six audit gates must be run sequentially — harm test → dark-pattern list → vulnerable-user check → biometric lawful-basis check → anticipation-loop cap check → signal honesty check. A single "fail" on any gate blocks ship. A locally chosen cadence/completion safeguard must be documented with its rationale and review criteria; no seven-unlock neural threshold is established. For EU-market affect-inference systems, record purpose-specific classification and applicable notices, prohibitions and compliance dates with qualified counsel; vulnerability alone does not establish an Article 5 prohibition.
**Outputs:** Audit pass/fail flag per gate (6 gates, each documented with evidence); ethical fail flag (binary: ship-blocked or ship-cleared); remediation list if any gate fails (specific design change required, owner, and re-audit trigger).

---

### Recipe 7: Attention-Aware AI Assistant UX (app-builder)

**Goal**: design an AI assistant or conversational product (chatbot, copilot, AI companion) whose output cadence, response framing, and notification behavior earn and conserve user attention — without exploiting pre-conscious mechanisms.

**Stack**:
1. **Predictive processing (#12)**: Establish a consistent response format prior early. Users build a generative model of how the assistant responds; violating that model (unexpected length shifts, sudden tone changes, unexplained refusals) incurs prediction-error cost that degrades trust. Reserve format novelty for high-value reveals only.
2. **Attention & salience (#1)**: Top-down salience dominates in AI UX — relevance to the user's stated task, not motion or contrast. Avoid decorative animations, status spinners with no informational value, or unsolicited agent proactivity that charges attentional cost without earning it.
3. **Arousal calibration (#2)**: Match response pacing to the cognitive-load state of the task. For high-stakes or complex tasks, reduce sentence length and information density per turn; for exploratory or creative tasks, the user's arousal optimum is higher — match it. Do not sustain high information density across the entire session arc.
4. **Memory consolidation (#9)**: If the product includes proactive reminders or scheduled summaries, respect user-selected timing and quiet hours; clock time alone does not identify a consolidation window. A midnight message may interrupt sleep depending on the user and device settings; measure actual interruption rather than assuming NREM replay.
5. **Reward anticipation (#10)**: For AI products with a reveal arc (agent completing a long task, generating a final output, progressive report building), preserve the anticipation phase — progress signaling can improve task visibility and set expectations; test these usability outcomes without assuming VTA dopamine release. Do not drop the final output silently; surface the completion as a named event.

**Ethical-bound check**: AI assistants must not use proactive nudges, tone modulation, or pacing manipulation to manufacture dependency or increase session frequency beyond the user's own goals. For voice/facial adaptive systems, route a purpose-specific classification to qualified privacy/AI-regulation counsel: record inputs, inferred attributes, intended use, jurisdiction, deployment context and current governing text. Such capture alone does not establish emotion-recognition, biometric-categorisation or high-risk status, nor an Article 9 classification. Confirm applicable notices, prohibitions and dates after that classification. Proactivity requires consent — users must be able to silence or reconfigure assistant-initiated contact with one step (DMCC reversibility test).

**Fail signal**: Session-length metrics rise but task-completion satisfaction drops — the assistant is holding attention without delivering value; attentional debt is accumulating. Qualitative signal: "the assistant feels pushy" or "I feel like I can't stop."

**Inputs:** Task cognitive-load profile (high-stakes decision vs. exploratory vs. creative); response format prior established in onboarding; proactive notification plan (timing, cadence, opt-out path); any affect-inference capability in the assistant pipeline (voice, facial, text tone).
**Rules:** Treat format consistency as a usability hypothesis; do not mandate 90% of turns as a neural threshold. Match response form to the user’s task, make proactivity configurable and apply current purpose-specific privacy/affect-inference obligations after classification.
**Outputs:** Response format spec (consistent structure template + novelty trigger list); notification timing policy (user-selected timing, quiet hours and opt-out path documented); ethical pass/fail flag (affect-inference AI Act readiness checked; proactivity reversibility verified before ship).

---

## Knowledge Base & Operational Guides

The references and playbooks below form the operational layer on top of the 12 primitives and 6 composition recipes above. The primitives describe neural mechanisms. The operational layer describes how to select and compose frameworks, what instrumentation and vendors to use, how to read observed signals, how to pass regulatory gates, and how to run a study or act on an observation.

| File | Use When | Answers the Question |
|------|----------|----------------------|
| [`references/frameworks-meta.md`](references/frameworks-meta.md) | Composing multiple primitives into a coherent design strategy; selecting the right structural frame (SOR, CDJ, Predictive-Coding, Reactance) | "Which meta-framework should I use to organise these primitives, and how do they layer?" |
| [`references/instrumentation-vendor-landscape.md`](references/instrumentation-vendor-landscape.md) | Choosing measurement tools and vendors; assessing regulatory exposure from biometric capture | "What tool or vendor should I use to measure this signal, and what are the EU AI Act / GDPR implications?" |
| [`references/biomarker-signal-dictionary.md`](references/biomarker-signal-dictionary.md) | Interpreting signals from a completed study; mapping a specific biomarker to a primitive and a design action | "I observed signal X in the lab — what primitive does it index and what design move follows?" |
| [`references/ethics-operational-checklist.md`](references/ethics-operational-checklist.md) | Before running any neuro study or shipping any primitive-based feature; DMCC + EU AI Act + GDPR compliance | "Does this study or feature pass the regulatory and ethics go/no-go gates?" |
| [`assets/playbooks/study-design.md`](assets/playbooks/study-design.md) | Designing a neuro study from scratch; setting N requirements; choosing within vs between-subject; writing analysis plan | "How do I design a study that will produce an actionable product decision?" |
| [`assets/playbooks/signal-to-design-cookbook.md`](assets/playbooks/signal-to-design-cookbook.md) | Translating an observed user behaviour or study result into a concrete design move | "We observed X — what do we build or change?" |

---

## Workflow

1. Identify the neural surface you are designing for (attention, arousal, social trust, narrative, regulatory orientation, aesthetics, interoception, memory, anticipation, embodied metaphor, prediction).
2. Use the [Decision Checklist](#decision-checklist) to identify which primitives are relevant.
3. Open the per-primitive playbook in [`assets/templates/consumer-neuroscience/`](assets/templates/consumer-neuroscience/) for the full definition, misuse boundary, and worked example.
4. Apply the [Ethical Bounds](#ethical-bounds) harm test and the DMCC compliance check to each technique before implementation.
5. For compound design problems, use the [Composition Recipes](#composition-recipes) as starting stacks.
6. Check the [Anti-Patterns](#anti-patterns) table to confirm you are not inadvertently shipping an exploitative pattern.

---

## ASCII Flow

```text
Engagement or perception problem
  -> Identify neural surface: attention, arousal, trust, narrative, memory, reward, embodiment
  -> Confirm signal or proxy is available
     +-- no signal -> treat as hypothesis, not neuroscience claim
     +-- signal exists -> select primitive and playbook
  -> Apply ethical and regulatory gates
  -> Compose design pattern and measurement plan
  -> Ship only with user benefit, evidence, and monitoring
```

---

## Local Validation Artifact

- [Operational record, worked case and regression checks](references/evidence-to-product.md). Read before translating a mechanism into a deployment recommendation.

## Navigation

- Per-primitive playbooks: [`assets/templates/consumer-neuroscience/`](assets/templates/consumer-neuroscience/) (one file per primitive)
- Composition guide: [`assets/templates/consumer-neuroscience/README.md`](assets/templates/consumer-neuroscience/README.md)
- Formal theory map: [`references/formal-theory-map.md`](references/formal-theory-map.md)
- Patterns, scenarios, and traps: [`references/patterns-scenarios-traps.md`](references/patterns-scenarios-traps.md)
- Domain-agnostic primitives overview: [`references/primitives-overview.md`](references/primitives-overview.md)
- Sources: [`data/sources.json`](data/sources.json)
- `references/frameworks-meta.md` — meta-frameworks (SOR, Consumer Decision Journey, Predictive Coding, Reactance) for primitive composition
- `references/instrumentation-vendor-landscape.md` — vendor and tool reference (August 2026), modality decision tree
- `references/biomarker-signal-dictionary.md` — signal → primitive → design-action cookbook
- `references/ethics-operational-checklist.md` — DMCC + EU AI Act + GDPR operational gates
- `assets/playbooks/study-design.md` — end-to-end study-design playbook
- `assets/playbooks/signal-to-design-cookbook.md` — observation → action recipes

---

## Related Skills

- `marketing-cro` — conversion rate optimization; applies attention (#1), neuroaesthetics (#7), and social bonding (#3) at the page and funnel level
- `marketing-content-strategy` — narrative and copy; applies narrative transportation (#4), embodied cognition (#11), and mirror systems (#6) in content design
- `marketing-paid-advertising` — ad creative and landing pages; applies salience (#1), BIS/BAS framing (#5), and arousal calibration (#2)
- `software-ui-ux-design` — interface design; applies neuroaesthetics (#7), embodied cognition (#11), predictive processing (#12), and cognitive consistency
- `product-management` — onboarding and feature design; applies reward anticipation (#10), memory consolidation (#9), and retention loop design
- `startup-business-models` — pricing and packaging; applies interoception (#8) and social bonding (#3) in trust-based purchase design

---

## Fact-Checking

- Primary sources are cited in each per-primitive playbook and in [`data/sources.json`](data/sources.json).
- Canonical references: Treisman 1980 + Itti & Koch 2001 (attention and salience), Yerkes & Dodson 1908 + McEwen 2007 (arousal physiology), Zak 2012 + Carter 2014 (social bonding and oxytocin), Green & Brock 2000 + Buckner 2008 (narrative transportation and DMN), Higgins 1997 + Carver & White 1994 (BIS/BAS and regulatory focus), Rizzolatti & Craighero 2004 + Hatfield 1993 (mirror systems and emotional contagion), Ramachandran & Hirstein 1999 + Chatterjee 2014 (neuroaesthetics), Damasio 1996 + Craig 2009 (interoception and somatic markers), Hebb 1949 + Walker 2017 (memory consolidation and sleep), Knutson 2001 + Berridge 2007 (reward anticipation and incentive salience), Lakoff & Johnson 1999 + Barsalou 2008 (embodied cognition), Friston 2010 + Clark 2013 + Constant et al. + Sprevak 2024 (predictive processing and active inference).
- 2025 source anchors: Bigne 2025 P&M (neurophysiological tools); Frontiers in Neuroergonomics 11 July 2025 (neuro-insights systematic review, DOI: 10.3389/fnrgo.2025.1542847); Bansal 2025 IJCS (neuromarketing and marketing mix); F1000Research 14:1132 (noninvasive neuromarketing methods); Frontiers in Human Neuroscience 2024 (xAI/fMRI brand perception); Sprevak 2024/2025 (predictive processing review).
- Neural response timing and peripheral hormone kinetics do not establish interface deadlines. Verify the task and measurement in the primary paper before citing a quantity; do not treat working-memory capacity as a visible-control limit.
- **CORRECTION for #2 (arousal physiology) — BAAS, Nature Communications 2025:** Neural affective arousal (cortical-subcortical signature: prefrontal, periaqueductal gray, thalamo-amygdala-insula) is statistically separable from autonomic arousal (GSR, HRV) and from wakefulness; validated across 24 studies, n=868 (Declerck-independent; Nature Communications, DOI: 10.1038/s41467-025-61706-0). Do not treat GSR/HRV as full proxies for subjective affective arousal — they capture physiological activation but miss the subjective-experience component. Where fMRI/EEG is unavailable, acknowledge this dissociation as a measurement limitation.
- **CORRECTION for #3 (social bonding) — oxytocin–trust replication caution:** The Kosfeld 2005 / Zak 2012 narrative that oxytocin universally increases trust has not replicated under registered conditions (Declerck et al. 2020, Nature Human Behaviour, >95% power: no main effect; DOI: 10.1038/s41562-020-0878-x). A 2025 preregistered high-powered study finds a selective ~15–17% trust increase in low-trust-disposition individuals only (bioRxiv 2025, preprint; DOI: 10.1101/2025.10.01.679711; note: preprint, not yet peer-reviewed). Apply #3 as "oxytocin system is implicated in affiliative bonding and trust formation" — not as "oxytocin = trust lever". Do not claim that oxytocin-adjacent design patterns universally increase trust; effects are context-dependent and moderated by individual trust disposition.
- **EEG metric reliability for ad testing (J. Advertising 2024, DOI: 10.1080/00913367.2024.2418109):** ISC (intersubject correlation) is the highest-reliability EEG metric for video ad testing; n≈11–15 achieves r=0.7 reliability. Alpha-asymmetry reliability does not improve with additional viewings and should be treated with caution. Meta-analytic corroboration: ISC–attention r=0.65 across 14 studies (BMC Psychology 2025, DOI: 10.1186/s40359-025-02879-7). Prefer ISC over alpha-asymmetry as primary EEG metric for ad/content evaluation.
- **UPDATE for #10 (reward anticipation) — neuroforecasting property (Genevsky, Tong & Knutson, PNAS Nexus 2025; DOI: 10.1093/pnasnexus/pgaf029):** NAcc activity during choice forecasts aggregate internet-market outcomes regardless of lab-sample demographic representativeness; MPFC predicts individual but does not generalise to aggregate in commercial market contexts. Minimum viable lab sample ~20–25 subjects. 2026 domain-extension (Srirangarajan et al., PNAS Nexus 2026; DOI: 10.1093/pnasnexus/pgag012; n=34): in conservation/social-media domain, **group MPFC activity** (not NAcc) forecast aggregate engagement on Instagram out-of-sample; NAcc and MPFC both predicted individual liking and donations. The two findings together establish a domain-dependent pattern — NAcc generalises to aggregate in commercial markets (Genevsky 2025); MPFC generalises to aggregate in social-media/conservation domain (Srirangarajan 2026). Practical implication: identify which region to prioritise for aggregate forecasting based on domain; small-N study remains sufficient.
- **EU classification review (2026-09-17):** adopted schedule changes are confirmed by official Commission sources, but exact applicability must be verified against the amended law. The article explorer still displays unamended text. See the dated source note; this scientific skill does not establish legal compliance.
- **CORRECTION (2026-08-14) — US neural-data laws are narrower than prior versions implied.** They do not generally cover GSR, HRV, eye-tracking, facial coding, or voice affect. Montana SB 163 expressly excludes "downstream physical effects of neural activity" (pupil dilation, motor activity, breathing rate); California SB 1223 excludes data "inferred from nonneural information"; Colorado reaches only identification-purpose data. Montana SB 163 (effective 1 Oct 2025) was missing entirely and is the strictest US regime for true neural data (per-purpose, per-recipient express consent). Source: FPF, "The Neural Data Goldilocks Problem"; Cooley neural-data patchwork survey (Feb 2026).
- **EEG preference-measure consistency caveat:** a 174-paper systematic review (Brain Informatics) reports frontal alpha asymmetry as the most-cited time-frequency preference signal and LPP as the most reliable ERP component, but finds **limited consistency across papers**, with each measure showing mixed results against actual preference and purchase behaviour. Combined with the J. Advertising 2024 reliability finding (alpha-asymmetry reliability does not improve with repeated viewings), this is a reason to prefer ISC and to treat any single-metric EEG preference claim as weak evidence.
- **CORRECTION (2026-07-11) — Vermont H.814 overstated in prior versions of this skill:** the enacted Act 101 has **no consent requirement and no private right of action** (both stripped in the Senate); its rights statement is largely declaratory with enforcement resting solely with the Attorney General. It is not a consent gate. Vermont's binding neural-data framework is **S.71**, effective 1 January 2028; see the corrected US Regulatory Context section above and [`references/ethics-operational-checklist.md`](references/ethics-operational-checklist.md).
- **Do not conflate primitive #11 (embodied cognition) with discredited social-priming demonstrations** (Bargh 1996 elderly-priming, money priming, cleanliness priming) — those largely failed multi-lab registered replication (Doyen et al. 2012; Many Labs 2 2018). Primitive #11 is conceptual-metaphor/grounded-simulation fluency, not covert cross-domain behavior steering; see the replication-boundary note in [`assets/templates/consumer-neuroscience/11-embodied-cognition.md`](assets/templates/consumer-neuroscience/11-embodied-cognition.md) and the Anti-Frameworks table in [`references/frameworks-meta.md`](references/frameworks-meta.md).
- If web access is unavailable at runtime, mark any runtime-specific claim as unverified.

## Learnings Loop

When prior decisions or pitfalls are relevant, consult `learnings.consolidated.md` if present; use `learnings.md` only for needed history or as the available fallback. Otherwise skip both.

After applying it, if you encountered a pattern worth remembering, a mistake worth preventing, or a domain fact that surprised you, append one dated bullet to `learnings.md` via `agents-skills-feedback-loop/scripts/append_learning.py`. Do not modify `SKILL.md` itself.
