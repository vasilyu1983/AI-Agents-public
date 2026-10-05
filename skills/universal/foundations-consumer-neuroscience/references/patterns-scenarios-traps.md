---
description: Applied behavioural patterns, known measurement and interpretation traps (FAA, consumer EEG, autonomic arousal, ML reverse inference), and an exit checklist for consumer-neuroscience work.
status: stable
---

# Consumer Neuroscience Patterns, Scenarios, and Traps

## Use Patterns

| Pattern | Use When | Stack |
|---|---|---|
| Anxiety-relief consumer loop | User is in an elevated arousal / uncertainty state pre-purchase | Calm entry (#2) → predictable structure (#12) → "person like me" story (#4) → real care signals (#3) → optional reflective self-check (#8) |
| Parasocial reading bond | Content that must feel personally authored for the reader | Narrative transportation (#4) → verified social imagery (#6) → real social proof (#3) → congruent metaphor (#11) |
| Daily-cadence retention | Product value depends on repeated daily engagement over weeks | Capped reward anticipation (#10) → user-chosen timing (#9) → relevance over loudness (#1) → format consistency (#12) |
| Conversion landing page, mixed audience | Pre-purchase audience with mixed goals | Relevance at entry (#1) → gain vs safety frame test, randomised; stated-goal segments only (#5) → visual credibility (#7) → verified testimonial (#6) |
| Trust repair after error | User has experienced a service or product failure | Named human acknowledgment (#3) → listen to impact (#8) → explain what failed and changed (#12) → truthful safeguard framing (#5) |
| Choice-architecture audit | Pre-ship check for any dark-pattern or vulnerable-user risk | Harm test → dark-pattern checklist → vulnerable-user screen → biometric lawful basis → anticipation cap |

## Known Traps

- Arousal is not engagement. High GSR indicates activation, not positive valence; stress and excitement look the same on the autonomic measure.
- Oxytocin is not a trust lever (Declerck et al. 2020 registered replication: no main effect). Assess perceived care and actual service outcomes.
- Narrative transportation reduces counterarguing (Green & Brock 2000). This is powerful and dangerous: material disclosures made during high-immersion states may not register.
- Regulatory focus is not BIS/BAS, and referral source is not a focus classifier. Fit effects vary by moderators (Motyka et al. 2014); an aggregate A/B can hide a frame × stated-goal interaction, so pre-declare that interaction if you plan to segment.
- Fabricated social proof (stock-photo testimonials, scripted "authentic" reactions) is deceptive and an advertising-code risk. When discovered, it damages trust. Do not justify faces or testimonials by claimed mirror-neuron activation; test them behaviourally.
- Wanting and liking dissociate. A user can want to open the app (anticipation) and not enjoy the experience (liking flat or negative). High DAU with low satisfaction is the signature.
- Published neuroscience effect sizes are from controlled lab conditions. Consumer-product populations, ambient context, and individual baseline arousal differ substantially. Measure on your own cohort.
- **CONSUMER-EEG OVERREACH:** Claiming fine-grained ERP temporal patterns, reliable alpha-asymmetry, or frontal measures from Muse2-class consumer devices is unsupported by 2026 comparative validation data (Scientific Reports 2026, n=30, vs DSI-24 research-grade). Muse2 shows broadband power spectrum distortion and highest test-retest variability of tested consumer devices. Limit consumer-grade EEG claims to ISC and broad spectral bands (alpha power); do not report temporal ERP precision or alpha-asymmetry as primary outcomes from consumer-grade hardware.
- **AUTONOMIC ≠ AFFECTIVE AROUSAL:** GSR and HRV capture sympathetic activation but are statistically distinct from subjective affective arousal (BAAS, Nature Communications 2025, n=868, 24-study validation). Treating a GSR spike as equivalent to the arousal a consumer consciously experiences is an unsupported conflation; note this dissociation when interpreting autonomic signals in consumer studies.
- **ML-ON-NEURO OVERFIT:** Applying supervised ML (Random Forest, SVM, CNN, LSTM) to neuro/biometric signals on N<50 risks severe overfit. Class-imbalance and feature-leakage are endemic in small consumer-neuro datasets. Treat any in-lab ML accuracy above 70% as lab-specific until cross-validated on an independent stimulus set. A single-lab RF result at 81% accuracy (EDA + FEA, Marques 2025, P&M) is promising but not yet replicated across labs or stimulus sets. (Sources: Marques et al. 2025 P&M DOI 10.1002/mar.22118; Frontiers ML/DL Neuromarketing 2025 editorial DOI 10.3389/fnhum.2025.1638225)
- **ML-ON-NEURO REVERSE INFERENCE TRAP:** ML classifiers trained on neuro signals do not resolve the reverse-inference problem — they restate it as a trained-prior problem. A classifier reporting "preference" or "purchase intent" from EEG is making the same reverse inference error as manual ERP interpretation, now amplified by overfitting risk from small N. Any vendor claim of "preference detection" or "purchase intent" from a neural classifier requires independent cross-study validation before treating as evidence. (Sources: Frontiers Human Neuroscience 2025 ML/DL editorial; Poldrack 2011 Neuron DOI 10.1016/j.neuron.2011.11.001)
- **FAA RELIABILITY TRAP:** Frontal alpha asymmetry showed poor reliability in video-ad testing, against excellent reliability for ISC (van Diepen, Boksem & Smidts 2025, J. Advertising 54(4):506–526; DOI 10.1080/00913367.2024.2418109). The abstract reports that repeated viewings improved reliability and that 30–40 participants were needed for most metrics; it does not say that FAA specifically fails to improve with repetition, so do not claim that without the full text. Prefer ISC as primary EEG metric; use FAA only with individual baseline normalisation as a secondary measure. Do not report FAA as a primary decision metric without ISC corroboration.

## Exit Checklist

- [ ] The urgency, warmth and social-proof signals are real and verifiable.
- [ ] The target experience benefits the user by their own stated goal or wellbeing.
- [ ] The user can opt out, disable notifications, or cancel with one step (reversibility test).
- [ ] Any physiological capture (GSR, HRV, eye-tracking, EEG, facial EMG) has a documented Art 6 basis and a purpose-based Art 9 assessment (special category only when processed for unique identification, or when it reveals health or another special category), plus US neural-data scope where relevant ([ethics-operational-checklist.md](ethics-operational-checklist.md)).
- [ ] Any wanting-loop mechanic (#10) has an explicit satiation signal and a rate-cap documented in the design spec.
- [ ] The design and the reason for it can be disclosed without embarrassing the team.
- [ ] For vulnerable-user audiences (wellness, anxiety, financial stress): the stricter defaults of the harm test in SKILL.md have been applied throughout.
