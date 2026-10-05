---
description: Multi-template behavioural recipes (anxiety-relief journey, reading bond, daily cadence, mixed-audience landing page, trust repair, ethics audit, AI assistant UX) and the misuse-boundary table. Every step is a testable behavioural hypothesis, not a neural mechanism.
status: stable
---

# Composition Recipes and Misuse Boundaries

## Contents

- [Recipe 1: Anxiety-relief journey](#recipe-1-anxiety-relief-journey-pre-purchase)
- [Recipe 2: Personal reading bond](#recipe-2-personal-reading-bond-purchase)
- [Recipe 3: Daily cadence retention](#recipe-3-daily-cadence-retention-post-purchase)
- [Recipe 4: Mixed-audience landing page](#recipe-4-mixed-audience-landing-page-pre-purchase)
- [Recipe 5: Trust repair after an error](#recipe-5-trust-repair-after-an-error-post-purchase)
- [Recipe 6: Ethics audit](#recipe-6-ethics-audit-pre-ship)
- [Recipe 7: Attention-aware AI assistant UX](#recipe-7-attention-aware-ai-assistant-ux)
- [Misuse Boundaries](#misuse-boundaries)

Moved from SKILL.md. Template numbers refer to [`../assets/templates/consumer-neuroscience/`](../assets/templates/consumer-neuroscience/). Each step names a behavioural hypothesis and the outcome to measure. Neural background is not evidence that a step works. Apply the evidence contract in [evidence-to-product.md](evidence-to-product.md) before claiming any mechanism.

## Recipe 1: Anxiety-relief journey (pre-purchase)

**Goal:** help a user with a real, stated worry reach a confident decision without manufacturing or amplifying anxiety.

1. **Calm entry (#2):** low visual intensity, short sentences, no spike at entry. Measure time-to-comprehension and perceived pressure. Do not infer anxiety from the product category.
2. **Predictable structure (#12):** consistent layout, no hidden elements. Measure errors and back-navigation.
3. **"Person like me" story (#4):** brief, first-person, past-tense account from a real user. Measure transportation (self-report scale), comprehension and perceived honesty.
4. **Real human care (#3):** named support person, real community count, operationally true care statements (response time, refund policy).
5. **Optional self-check (#8):** an honest "How do you feel about this now?" prompt for user reflection, not to create an association.

**Ethics:** the worry must be real; never create it to relieve it. Run the vulnerable-user gate. **Fail signal:** "felt scammed" or "felt pushed" reports, CSAT drop after purchase, complaints. **Outputs:** a controlled comparison of comprehension, satisfaction and perceived pressure; a fit-for-purpose self-report measure with its limits (a custom 1–5 item is not the Perceived Stress Scale); a documented ethics review. No cortisol-derived 90-second deadline exists.

## Recipe 2: Personal reading bond (purchase)

**Goal:** make interpretive content (reading, horoscope, report) feel personally relevant without deception.

1. **Narrative frame (#4):** brief orienting story; test second- vs third-person and present vs past tense as copy variants. No grammatical person or tense is biologically required.
2. **Verified social imagery (#6):** genuine or clearly illustrative faces only; test face vs no face.
3. **Real cohort framing (#3):** "Others who received this reading reported…" only from real data.
4. **Congruent metaphor (#11):** body-state metaphors that match the actual experience.

**Ethics:** label interpretive or predictive content as such (ASA CAP Code); no claims of scientific accuracy. **Fail signal:** low share rate despite long sessions. **Outputs:** preregistered share, comprehension and perceived-value outcomes with uncertainty. Never label a cohort "high-DMN" without validated neural measurement.

## Recipe 3: Daily cadence retention (post-purchase)

**Goal:** a voluntary daily habit users value, without compulsion.

1. **Daily reveal (#10):** a named card, insight or progress update. Cap the chain; show explicit completion. Measure wanting ("looking forward to this") and liking ("glad I did this") separately.
2. **User-chosen timing (#9):** users select cue time and quiet hours; randomise eligible timing cohorts; measure Day-7 and Day-30 retention and sleep-time interruptions.
3. **Relevance over loudness (#1):** personalised, named cues rather than high-contrast interruption, which users learn to dismiss.
4. **Format consistency (#12):** stable daily format; reserve novelty for real events.

**Ethics:** loops need a ceiling; notifications must be one-step to disable. **Fail signal:** streak completion high but next-session intent low (wanting has decoupled from liking). Present any cap or cadence as a disclosed product/safety default with review criteria, not a neural threshold.

## Recipe 4: Mixed-audience landing page (pre-purchase)

**Goal:** serve visitors with different goals for the same decision without a single-tone funnel.

1. **Relevance at entry (#1):** a problem statement that matches the visitor's task.
2. **Gain vs safety framing (#5):** test a gain-framed and a safety-framed headline when the product genuinely offers both. What predicts a win is fit between the frame and the goal the decision serves (regulatory fit), not a visitor "type". Do not personalise by referral source: it is not a validated classifier and carries intent and traffic-quality confounds. If you segment, use an explicit stated-goal question or a validated measure.
3. **Visual credibility (#7):** visual quality proportional to what the product delivers.
4. **Verified testimonials (#6):** real users whose outcome matches the page's promise.

**Ethics:** safety framing must describe real risks, never manufactured threat. **Fail signal:** a gap between framing arms that reverses across segments defined by stated goal. **Outputs:** A/B results for gain vs safety frames overall and by stated-goal segment (pre-declared); comprehension and perceived-pressure measures; ethics flag (verified testimonials, no manufactured urgency).

## Recipe 5: Trust repair after an error (post-purchase)

1. **Named human acknowledgment (#3):** accurate acknowledgment from a responsible person or team, not impersonated warmth.
2. **Listen first (#8):** invite users to describe impact before offering a remedy.
3. **Explain the fix (#12):** what failed and what changed, so users can update their expectations.
4. **Safeguard framing (#5):** describe the prevention step ("we added a check so this cannot recur") alongside the remedy, when it is true.

**Fail signal:** persisting reported harm or unresolved errors. **Outputs:** acknowledgment, remedy and prevention steps; trust and task outcomes against baseline with uncertainty; service-specific recovery targets set in advance. There is no 200 ms oxytocin rule and no universal NPS recovery ratio.

## Recipe 6: Ethics audit (pre-ship)

Run in order; any fail blocks shipping:

1. Harm test (three gates in SKILL.md).
2. Choice-architecture list: confirm-shaming, pre-ticked operator-benefit defaults, drip pricing, false urgency, forced continuity (enforcement detail: `foundations-behavioral-economics`).
3. Vulnerable-user check: wellness, anxiety, spiritual or financial-distress audience → stricter defaults.
4. Data classification: any GSR, HRV, eye, face, voice, EEG capture → Art 6 basis, Art 9 assessment, US neural-data scope ([ethics-operational-checklist.md](ethics-operational-checklist.md)).
5. Loop cap: every anticipation mechanic (#10) has a stop signal and a documented cap.
6. Signal honesty: all urgency, warmth, arousal and social-proof signals are true and verifiable.

**Outputs:** pass/fail per gate with evidence, and a remediation list with owner and re-audit trigger.

## Recipe 7: Attention-aware AI assistant UX

1. **Consistent response format (#12):** users learn how the assistant answers. Test whether sudden length or tone shifts reduce trust.
2. **Relevance over decoration (#1):** no decorative animation or uninformative spinners; limit unsolicited proactivity.
3. **Pacing to task load (#2):** shorter turns for high-stakes or complex tasks.
4. **User-chosen reminder timing (#9):** quiet hours; measure real interruption.
5. **Visible progress on long tasks (#10):** progress signals and a named completion event; test these as usability outcomes.

**Ethics:** no nudges, tone modulation or pacing designed to build dependency or session frequency beyond the user's goals. Voice or facial adaptation needs purpose-specific privacy and AI-Act classification by counsel. Users must be able to silence assistant-initiated contact in one step. **Fail signal:** session length up while task satisfaction falls; "feels pushy".

## Misuse Boundaries

| Misuse | Why it is wrong | Required correction |
|---|---|---|
| Manufacturing intensity without informational value (#2) | Stimulus intensity, not content, drives the response; GSR/HRV are not felt arousal (BAAS 2025) | Earn attention with relevance; measure dwell quality and comfort |
| Fake warmth or care language (#3) | Collapses on discovery; oxytocin→trust has no replicated main effect (Declerck et al. 2020) | Only real care mechanics and real social proof |
| False or material content inside a story (#4) | Transportation can reduce counterarguing (Green & Brock 2000) | Accurate content; disclosures at low-narrative-load moments |
| Physiological capture without lawful processing (#2, #8) | Status depends on purpose and inference | Art 6 basis, Art 9 assessment, informed participation |
| Classifying users as "BIS" or "BAS" from channel (#5) | Invalid proxy; confounded | Test message–goal fit; stated-goal segments only |
| Fabricated reactions or ratings (#6) | Fake social proof; ASA/DMCC exposure | Real sentiment from verified users |
| Polish covering a weak product (#7, #10) | Disappointment when delivery lags | Match visual investment to delivery |
| Unannounced changes to core flows (#12) | Errors, confusion and trust loss | Announce and prime changes; keep routine flows stable |
| Somatic urgency in anxiety contexts (#8) | Manipulation of vulnerable users | Never manufacture body-state alarm |
| Uncapped anticipation loops (#10) | Compulsion risk; wanting can outlast liking | Stop signals, rate caps, harm-test sign-off |
| Affect inference without a classification record (#2, #6, #8) | Obligations depend on purpose, context and deployment | Record classification with qualified counsel |
