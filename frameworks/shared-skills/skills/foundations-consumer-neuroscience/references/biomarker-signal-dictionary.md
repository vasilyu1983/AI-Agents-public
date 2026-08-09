---
description: Signal → primitive → design-action lookup. For each observed biomarker pattern: what it indicates, which primitive it indexes, how to amplify or suppress it, and common misread traps.
last_verified: 2026-05-05
status: stable
---

# Biomarker Signal Dictionary

## Purpose

This file is the cookbook for the question "I observed X — what does it mean and what do I do?" It bridges physiological measurement to product-team action. Every row maps a specific, observable signal pattern to a primitive, a design amplification move, a suppression move, and the most common misinterpretation. It is not a general neuroimaging reference; it covers only signals relevant to the 12 primitives in this skill and the behavioural-economics primitives referenced as `BE #N`. Signal validity is instrument- and population-dependent; verify effect sizes on your own cohort before optimising for specific parameters.

---

## Signal Dictionary

| Signal Pattern | What It Indicates | Primitive | Design Move (amplify) | Design Move (suppress / resolve) | Failure Mode If Misread |
|---------------|------------------|-----------|----------------------|----------------------------------|------------------------|
| GSR phasic spike (1–3s post-stimulus) | Sympathetic arousal; orienting response to salient stimulus | #2 | Lean into the triggering element (novel copy, contrast, unexpected visual) — it is earning attentional cost | Reduce stimulus intensity; increase content density following spike to "spend" the arousal | Confusing arousal valence: spike = engagement AND spike = distress; add valence measure (facial, self-report) |
| Sustained elevated GSR baseline (>15 min) | Allostatic load; chronic stress; overload | #2 (negative) | Do not amplify; indicates design is draining not engaging | Reduce cognitive demands; add explicit resolution/closure beat; shorten session unit | Interpreting sustained baseline as "high engagement"; it is stress accumulation |
| Heart-rate deceleration (orienting response, ~200–600ms post-stimulus) | Attentional capture; stimulus detected as relevant and novel | #1 | Reinforce the triggering stimulus type (relevance, mild novelty, personal reference) | Remove competing distractors that prevent deceleration from occurring | Confusing HR deceleration with HR decrease from calm; temporal precision matters |
| HRV drop (RMSSD or SDNN decrease) | Reduced vagal tone; sympathetic dominance; cognitive load or stress | #2 + BE #14 (cognitive load) | Not a target to amplify; indicates excessive processing demand | Reduce decision complexity; strip extraneous information; provide defaults | Treating HRV drop as a sign of engagement; it indexes cost, not reward |
| Pupil dilation | Arousal + cognitive effort (locus coeruleus-NE system; Kahneman 1973) | #1, #2 | Increase stimulus relevance or novelty (dilation tracks task-engaged arousal) | Reduce cognitive demand (sustained dilation = load not interest) | Pupil ≠ interest; it also indexes cognitive effort and can indicate overload; always pair with performance or behavioural measure |
| Saccadic pattern: short saccades + long fixations on AOI | Top-down attentional engagement; user is reading/processing the element | #1 | Ensure the element is information-rich enough to reward the fixation dwell | If element should not hold attention, reduce information density there | Equating fixation duration with comprehension; fixation can also indicate confusion |
| First-fixation latency (time to first fixation on target element) | Bottom-up salience of target; lower latency = higher salience | #1 | Increase bottom-up cues (contrast, colour pop, motion) on highest-priority element | Remove competing high-salience elements that draw first fixation away from target | Treating low first-fixation latency as equivalent to positive valence; salience is not liking |
| N400 ERP (negative deflection ~400ms, frontal-central) | Semantic prediction violation; word/concept does not fit the established context | #12 | Design deliberate semantic mismatches as engagement hooks (headline incongruity resolved by subheadline) | Ensure brand language and product copy use consistent semantic priors; avoid jargon mismatch | N400 ≠ dislike; it is prediction cost — can be earned (creative hook) or waste (confusing copy) |
| P300 ERP (positive deflection ~300ms, parietal, P3b variant) | Attention allocation to task-relevant oddball or salient category-match stimulus | #1 | Make the target stimulus distinctive within its context (oddball principle) | Reduce P300-irrelevant salience to avoid attentional misfires | P300 amplitude is not proportional to purchase intent; it reflects stimulus salience and categorisation |
| LPP (Late Positive Potential, 400–1000ms+ post-stimulus, centro-parietal) | Sustained motivational/affective engagement with a stimulus; tracks emotional intensity regardless of valence | #4, #10 | Use emotionally intense, self-relevant content (narrative, high-valence imagery) to sustain LPP amplitude | Do not sustain high-LPP content beyond narrative arc resolution; engagement collapse follows unresolved arousal | LPP ≠ positive affect; it amplifies both approach and avoidance motivation; pair with valence measure |
| Frontal alpha asymmetry: greater left-frontal alpha (relative left activation) | Approach motivation; BAS engagement | #5 | Promotion-framed copy, gain-frame offers, forward-momentum UI | Ensure prevention-framed copy does not block approach motivation in BAS-dominant users | **RELIABILITY CAUTION:** FAA is the lowest-reliability EEG metric for ad testing (J. Advertising 2024, DOI 10.1080/00913367.2024.2418109); reliability does not improve with additional viewings. Do not use as primary decision metric; always normalise to individual resting baseline; prefer ISC as primary EEG metric. Group averages without baseline normalisation are unreliable. |
| Frontal alpha asymmetry: greater right-frontal alpha (relative right activation) | Avoidance motivation; BIS engagement | #5 | Prevention framing, risk-reduction copy, reassurance signals | Do not apply promotion frame to right-lateralised users; drives disengagement | **RELIABILITY CAUTION:** Same as above — FAA lowest-reliability EEG metric for ad testing (J. Advertising 2024). Use only relative to individual baseline as a secondary measure; do not report as primary outcome without ISC corroboration. |
| Mu suppression (sensorimotor cortex, 8–13Hz desynchronisation) | Mirror-neuron system activation; motor simulation of observed action | #6 | Show faces in action, not static; depict emotional expression mid-movement; use real testimonials with body language | Limit static stock photography that fails to activate MNS simulation | Mu suppression interpretation is contested in humans; treat as suggestive, not definitive |
| VTA / nucleus accumbens BOLD activation (fMRI) | Reward anticipation (wanting); mesolimbic dopamine signal onset ~200ms before anticipated reward | #10 | Design a distinct anticipation phase before reward delivery (countdown, teaser, partial reveal) | Avoid immediate delivery without anticipation phase; wanting signal not earned | fMRI BOLD is ~2s lag; cannot capture the 200ms dopamine onset precisely; confirm with behavioural anticipation metrics |
| Default Mode Network activation (mPFC, PCC, angular gyrus; fMRI) | Self-referential narrative absorption; mind-wandering or active self-model updating | #4 | Second-person present-tense framing; personal-data-grounded narrative; "person like me" story structure | Reduce third-person or generic copy that fails to engage self-referential processing | DMN activation is not always absorption; it also indexes mind-wandering when task is boring |
| Insular cortex activation (anterior insula; fMRI) | Interoceptive awareness; body-state signal integration; visceral decision input | #8 | Explicit somatic cues ("how do you feel right now?"); copy referencing body experience; product framing grounded in physical sensation | Do not manufacture somatic signals in anxiety contexts; anterior insula tracks real body state, including manufactured threat | Insula activation ≠ negative valence; it tracks interoceptive salience including positive body states |
| Facial AU6 + AU12 (Duchenne smile: cheek raiser + lip corner pull) | Genuine positive affect; cannot be reliably faked without AU6 involvement (Ekman) | #3, #7 | Testimonial content that produces Duchenne response; resolve narrative tension with warmth; aesthetic beauty response | Distinguish from non-Duchenne smile (AU12 alone = polite/social, not genuinely positive) | AU6+AU12 coding requires either facial EMG or high-quality computer-vision coding; webcam consumer tools vary widely in AU6 detection accuracy |
| Facial AU4 (brow lowerer, corrugator supercilii) | Confusion; cognitive friction; negative affect; mild threat appraisal | #12 | Not a target to amplify (cognitive friction may be useful in small doses for prediction-error hooks only) | Reduce complexity; clarify copy; resolve semantic prediction violation (N400 companion signal) | AU4 ≠ dislike exclusively; it also indicates processing effort; a furrowed brow during a pricing decision may indicate deliberation, not rejection |
| Voice prosody pitch range collapse (reduced fundamental frequency range) | Disengagement; emotional flatness; reduced arousal | #2 | Increase content relevance and novelty to re-engage; vary prosodic register in voice UX | If this appears in user-testing narration, treat as disengagement signal; do not infer dislike from flat affect alone | Pitch range collapse ≠ negative sentiment; it is a low-arousal signal that can be positive (calm, relief) or negative (boredom) |

---

## Multimodal Stack Templates

### Ad / Landing Page Test Stack
**Signals**: screen-based eye-tracking + GSR/EDA + facial action coding (lab or webcam with validated tool).
**What it answers**: did the ad earn attention (#1)? did it generate appropriate arousal (#2)? did it produce genuine positive affect (#3, #7)?
**Protocol**: 30–50 participants; within-subject where multiple versions tested; baseline period before stimulus; 15–30s exposure per stimulus; post-stimulus self-report (SAM scale or custom).

### Narrative Immersion Stack
**Signals**: screen-based eye-tracking + GSR + EEG LPP (requires research-grade EEG, 32+ channels).
**What it answers**: was narrative transportation achieved (#4)? did emotional engagement sustain across the arc? did anticipation build toward the resolution (#10)?
**Protocol**: 20–30 participants; within-subject; clear stimulus segmentation for ERP epoching; avoids excessive artefact (still viewing, no chewing); LPP time-window 400–1000ms post-content-event.

### Interoceptive Trust Stack
**Signals**: HRV (wearable, continuous) + voice prosody (if voice UX) + post-task somatic-state self-report.
**What it answers**: did the interaction reduce or maintain vagal tone (low stress = trust signal) (#8)? did voice affect indicate engagement or disengagement (#2)? did users report body-state alignment with product intent (#8)?
**Protocol**: 20–30 participants; HRV requires at least 5-minute baseline epoch; voice recording requires consent; somatic-state self-report at defined task checkpoints.

---

## Misread Traps

| Signal | Common Misread | Correct Interpretation |
|--------|---------------|----------------------|
| GSR spike | = positive engagement | = autonomic/sympathetic activation, which is statistically separable from subjective affective arousal — not a proxy for it (BAAS, Nat. Commun. 2025); valence also unknown without a companion measure |
| Pupil dilation | = interest or liking | = arousal + cognitive effort; overload can cause sustained dilation |
| Frontal alpha asymmetry | Valid without baseline | Must be computed relative to individual resting baseline; group-level averages without normalisation are meaningless |
| Webcam emotion AI output | = lab-grade emotion coding | Consumer-grade facial CV systems have substantially lower per-AU accuracy than lab facial EMG; treat as indicative, not definitive |
| Heart-rate decrease | = calm (parasympathetic) | Short HR deceleration (200–600ms) = orienting/attention; sustained HR decrease = relaxation; context determines interpretation |
| HRV drop | = high engagement | = sympathetic dominance; most likely stress or cognitive overload |

---

## Sources

- Kahneman, D. (1973). _Attention and Effort_. Prentice-Hall. (pupillometry and cognitive load)
- Polich, J. (2007). Updating P300. _Clinical Neurophysiology_, 118(10), 2128–2148.
- Kutas, M. & Federmeier, K. D. (2011). Thirty years and counting: finding meaning in the N400. _Annual Review of Psychology_, 62, 621–647.
- Schultz, W. (1997). Dopamine neurons and their role in reward mechanisms. _Current Opinion in Neurobiology_, 7(2), 191–197.
- Ekman, P. & Friesen, W. V. (1978). _Facial Action Coding System_. Consulting Psychologists Press.
- Schupp, H. T. et al. (2000). Affective picture processing: the late positive potential. _Psychophysiology_, 37(2), 257–261. (LPP)
- Davidson, R. J. (2004). Well-being and affective style. _Philosophical Transactions of the Royal Society B_, 359, 1395–1411. (frontal alpha asymmetry)
- Craig, A. D. (2009). How do you feel — now? _Nature Reviews Neuroscience_, 10(1), 59–70. (interoception and insula)
- Knutson, B. et al. (2001). Anticipation of increasing monetary reward selectively recruits nucleus accumbens. _Journal of Neuroscience_, 21(16), RC159.
- Bigne, E. et al. (2025). Neurophysiological tools in marketing research. _Psychology & Marketing_.
