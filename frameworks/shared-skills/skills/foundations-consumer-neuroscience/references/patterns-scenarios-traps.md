---
description: Applied patterns, scenarios, anti-patterns, and known traps for consumer-neuroscience foundations.
last_verified: 2026-05-17
status: stable
---

# Consumer Neuroscience Patterns, Scenarios, and Traps

## Use Patterns

| Pattern | Use When | Stack |
|---|---|---|
| Anxiety-relief consumer loop | User is in an elevated arousal / uncertainty state pre-purchase | Arousal deescalation (#2) → prediction priming (#12) → narrative (#4) → warmth (#3) → interoceptive anchor (#8) |
| Parasocial reading bond | Content that must feel personally authored for the reader | Narrative transportation (#4) → mirror contagion (#6) → real social proof (#3) → embodied metaphor (#11) |
| Daily-cadence retention | Product value depends on repeated daily engagement over weeks | Reward anticipation (#10) → consolidation timing (#9) → top-down salience (#1) → prediction confirmation (#12) |
| Conversion landing page, mixed audience | Pre-purchase audience with unknown regulatory orientation | Earned salience (#1) → BIS/BAS copy split (#5) → aesthetic reward (#7) → mirror-matched testimonial (#6) |
| Trust repair after error | User has experienced a service or product failure | Real human warmth (#3) → somatic acknowledgment (#8) → prediction-error closure (#12) → prevention framing (#5) |
| DMCC compliance audit | Pre-ship check for any dark-pattern or vulnerable-user risk | Harm test → dark-pattern checklist → vulnerable-user screen → biometric lawful basis → anticipation cap |

## Known Traps

- Arousal is not engagement. High GSR indicates activation, not positive valence; stress and excitement look the same on the autonomic measure.
- Oxytocin half-life is ~3–5 minutes in plasma. Warmth must be distributed across the session, not front-loaded in a hero banner.
- Narrative transportation suppresses critical evaluation. This is powerful and dangerous: material disclosures made during high-immersion states may not register.
- BIS/BAS mismatch is invisible in aggregate conversion data but visible in segment-level drop-off. Aggregate A/B tests can mask regulatory-focus mis-alignment.
- Mirror simulation is automatic and cannot be consciously filtered by the user. Fabricating emotional-contagion cues (stock-photo testimonials, scripted "authentic" reactions) triggers real neural response; discovery of fabrication incurs disproportionate trust penalty.
- Wanting and liking dissociate. A user can want to open the app (anticipatory dopamine) and not enjoy the experience (liking flat or negative). High DAU with low satisfaction is the signature.
- Published neuroscience effect sizes are from controlled lab conditions. Consumer-product populations, ambient context, and individual baseline arousal differ substantially. Measure on your own cohort.
- **CONSUMER-EEG OVERREACH:** Claiming fine-grained ERP temporal patterns, reliable alpha-asymmetry, or frontal measures from Muse2-class consumer devices is unsupported by 2026 comparative validation data (Scientific Reports 2026, n=30, vs DSI-24 research-grade). Muse2 shows broadband power spectrum distortion and highest test-retest variability of tested consumer devices. Limit consumer-grade EEG claims to ISC and broad spectral bands (alpha power); do not report temporal ERP precision or alpha-asymmetry as primary outcomes from consumer-grade hardware.
- **AUTONOMIC ≠ AFFECTIVE AROUSAL:** GSR and HRV capture sympathetic activation but are statistically distinct from subjective affective arousal (BAAS, Nature Communications 2025, n=868, 24-study validation). Treating a GSR spike as equivalent to the arousal a consumer consciously experiences is an unsupported conflation; note this dissociation when interpreting autonomic signals in consumer studies.
- **ML-ON-NEURO OVERFIT:** Applying supervised ML (Random Forest, SVM, CNN, LSTM) to neuro/biometric signals on N<50 risks severe overfit. Class-imbalance and feature-leakage are endemic in small consumer-neuro datasets. Treat any in-lab ML accuracy above 70% as lab-specific until cross-validated on an independent stimulus set. A single-lab RF result at 81% accuracy (EDA + FEA, Marques 2025, P&M) is promising but not yet replicated across labs or stimulus sets. (Sources: Marques et al. 2025 P&M DOI 10.1002/mar.22118; Frontiers ML/DL Neuromarketing 2025 editorial DOI 10.3389/fnhum.2025.1638225)
- **ML-ON-NEURO REVERSE INFERENCE TRAP:** ML classifiers trained on neuro signals do not resolve the reverse-inference problem — they restate it as a trained-prior problem. A classifier reporting "preference" or "purchase intent" from EEG is making the same reverse inference error as manual ERP interpretation, now amplified by overfitting risk from small N. Any vendor claim of "preference detection" or "purchase intent" from a neural classifier requires independent cross-study validation before treating as evidence. (Sources: Frontiers Human Neuroscience 2025 ML/DL editorial; Poldrack 2011 Neuron DOI 10.1016/j.neuron.2011.11.001)
- **FAA RELIABILITY TRAP:** Frontal alpha asymmetry is the lowest-reliability EEG metric in ad testing (J. Advertising 2024, n≈116, 13 commercials; DOI 10.1080/00913367.2024.2418109); reliability does not improve with repeated viewings. Prefer ISC as primary EEG metric; use FAA only with individual baseline normalisation as a secondary measure. Do not report FAA as a primary decision metric without ISC corroboration.

## Exit Checklist

- [ ] The arousal, warmth, and urgency signals are real and verifiable.
- [ ] The target experience benefits the user by their own stated goal or wellbeing.
- [ ] The user can opt out, disable notifications, or cancel with one step (DMCC reversibility test).
- [ ] Any biometric or neuro-physiological signal capture (GSR, HRV, eye-tracking, EEG, facial EMG) has documented UK GDPR Article 9 lawful basis.
- [ ] Any wanting-loop mechanic (#10) has an explicit satiation signal and a rate-cap documented in the design spec.
- [ ] The copy can be disclosed — including its neural mechanism — without embarrassing the team.
- [ ] For vulnerable-user audiences (wellness, anxiety, financial stress): the stricter column of the manipulation table in SKILL.md has been applied throughout.
