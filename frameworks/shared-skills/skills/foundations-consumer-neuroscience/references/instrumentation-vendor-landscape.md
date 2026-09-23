---
description: Signal modality reference and vendor landscape for consumer-neuroscience instrumentation, August 2026. Includes modality decision tree, EU AI Act risk flags, and DIY surrogate-signal path.
last_verified: 2026-08-14
status: stable
---

# Instrumentation and Vendor Landscape (August 2026)

## Table of Contents

- [Purpose](#purpose)
- [Signal Modality Reference](#signal-modality-reference)
- [Vendor Landscape (August 2026)](#vendor-landscape-august-2026)
- [Decision Tree](#decision-tree)
- [DIY / No-Vendor Path](#diy--no-vendor-path)
- [Sources](#sources)

---

## Purpose

Selecting measurement tools is a design decision, not just a procurement decision. The modality chosen determines which primitives can be observed directly vs. inferred, sets the ecological-validity ceiling, creates regulatory obligations (physiological personal data requires purpose-based classification; health inference or biometric identification may invoke Article 9; affect-inference AI = EU AI Act high-risk from 2 December 2027, with Article 50 transparency owed from 2 August 2026), and constrains the N achievable in budget. This reference maps signal modalities, vendor tiers, a decision tree, and the conditions under which surrogate behavioural signals are the right answer instead of physiological measurement.

---

## Signal Modality Reference

| Signal | What It Measures | Temporal Resolution | Spatial Resolution | Ecological Validity | Cost Tier | GDPR Special-Category? | EU AI Act Risk Class |
|--------|-----------------|--------------------|--------------------|---------------------|-----------|------------------------|----------------------|
| fMRI (functional MRI) | BOLD signal as proxy for neural activity | ~2s (poor) | ~1–3mm (excellent) | Very low (supine, scanner noise) | ££££ (£500–£2k/participant) | Purpose/inference dependent | Low (research-only; no commercial deployment path currently) |
| EEG (research-grade, 64–256 channels) | Millisecond-resolution cortical ERP and oscillatory power | ~1ms (excellent) | Low-moderate (source localisation limited) | Low–moderate (lab) | ££–£££ | Purpose/inference dependent | Low–moderate |
| EEG (consumer-grade, 4–14 channels) | Coarse ERP; frontal asymmetry; theta/alpha bands | ~5ms | Very low | Moderate (passive wear) | £–££ | Purpose/inference dependent | Moderate |
| fNIRS (functional near-infrared spectroscopy) | Prefrontal haemodynamic response; cognitive load proxy | ~1–2s | Low | Moderate (ambulatory) | ££–£££ | Purpose/inference dependent | Low |
| Eye-tracking (screen-based) | Fixation, saccade, AOI dwell, pupillometry | ~1–4ms | ~0.5° visual angle | Moderate (lab-like screen context) | £–££ | Purpose/inference dependent | Low |
| Eye-tracking (glasses, mobile) | Fixation in natural environment; gaze in physical retail | ~1–4ms | ~0.5° | High | ££–£££ | Purpose/inference dependent | Low |
| GSR/EDA (skin conductance) | Sympathetic arousal; phasic event-related response; tonic baseline | ~0.5–2s | N/A (peripheral) | Moderate | £ | Purpose/inference dependent | Low |
| HRV (heart rate variability) | Vagal tone; cognitive load; stress; autonomic balance | ~1s | N/A | High (wearable) | £ | Purpose/inference dependent | Low |
| Facial EMG | Specific muscle-group activity (e.g., zygomatic = smile; corrugator = frown) | ~5ms | Muscle-group | Low (electrodes on face) | £–££ | Purpose/inference dependent | Low |
| Facial action coding — CV (computer vision) | Inferred facial AUs and emotion categories from video | Near real-time | Per-frame | High (any camera) | £ (SaaS) | Purpose/inference dependent | Purpose-specific AI Act/GDPR classification required; sensor or vendor alone is insufficient |
| Voice prosody analysis | Pitch range, rate, energy; arousal/disengagement proxy | ~100ms | N/A | High | £ (SaaS) | Purpose/inference dependent | Purpose-specific AI Act/GDPR classification required; sensor or vendor alone is insufficient |
| Pupillometry (standalone) | Arousal; cognitive effort; locus coeruleus-NE system activity | ~1ms (with eye-tracker) | N/A | Moderate | £ (if via eye-tracker) | Purpose/inference dependent | Low |

---

## Vendor Landscape (August 2026)

### Lab / Research-Grade

| Vendor | Primary Signal | Typical Use | Cost Tier | Lab vs Field | Risk Flag |
|--------|--------------|-------------|-----------|--------------|-----------|
| iMotions | Multimodal sync (EEG, GSR, eye, facial) | Integrated consumer neuro lab studies | ££££ | Lab | Purpose-specific AI Act/GDPR classification required; sensor or vendor alone is insufficient |
| Tobii (lab systems, Spectrum/TX300) | Eye-tracking, pupillometry | Lab fixation and reading studies | £££ | Lab | GDPR purpose-based classification |
| Smart Eye (Aurora, with Affectiva integration) | Eye-tracking + facial AU inference (in-cabin, research) | Automotive HMI; attention safety; as of early 2026 includes Affectiva affect-inference module | £££–££££ | Lab + in-cabin | Purpose-specific AI Act/GDPR classification required; sensor or vendor alone is insufficient |
| BrainProducts / g.tec | EEG (research-grade, 32–256 ch) | ERP, oscillatory, BCI research | £££ | Lab | GDPR purpose-based classification |
| Biosemi ActiveTwo | EEG (research-grade, DC-coupled) | High-fidelity ERP research | £££ | Lab | GDPR purpose-based classification |

### Mid-Market

| Vendor | Primary Signal | Typical Use | Cost Tier | Lab vs Field | Risk Flag |
|--------|--------------|-------------|-----------|--------------|-----------|
| Tobii Sticky (as of early 2026) | Webcam-based eye-tracking + attention heatmaps | Remote ad and landing page testing | ££ | Remote (in-the-wild) | GDPR classification; no affect-inference AI — lower risk |
| Realeyes | Webcam-based facial AU → emotion inference | Ad pre-testing emotion response | ££ | Remote | Purpose-specific AI Act/GDPR classification required; sensor or vendor alone is insufficient |
| Lookback / Maze | Qualitative screen recording + think-aloud | UX research; behavioural observation | £–££ | Remote | Standard GDPR; no special-category physiological data if no biometric |
| Pulse Labs (as of early 2026) | Voice prosody + transcript NLP | Voice UX testing; call-centre affect monitoring | ££ | Remote + field | Purpose-specific AI Act/GDPR classification required; sensor or vendor alone is insufficient |

### Self-Service / SaaS Behavioural Surrogates

| Vendor | Signal Type | Primitive Proxy | Cost Tier | Lab vs Field | Risk Flag |
|--------|------------|-----------------|-----------|--------------|-----------|
| Hotjar | Session replay, heatmaps, scroll depth | #1 attention (dwell, AOI); #12 friction | £ | Field | No special-category biometric; standard GDPR cookies |
| FullStory | Session replay, rage clicks, error events | #1, #2 (frustration proxy), #12 | £–££ | Field | No biometric; standard GDPR |
| Mouseflow | Heatmaps, funnel analysis | #1, #12 | £ | Field | No biometric |
| ContentSquare | Journey analytics, dwell, scroll, zone analysis | #1, #7 (engagement with design zones) | ££–£££ | Field | No biometric |
| PostHog (session recordings + feature flags) | Click, scroll, retention, funnel | #1, #9 (cohort retention), #10 (event cadence) | £ (open source) | Field | No biometric; standard GDPR |

### Consumer-Grade Neuro

**EEG metric reliability for ad testing (J. Advertising 2024, n=116, 13 commercials):** ISC (intersubject correlation) is the most reliable EEG metric for video advertising assessment; n≈11–15 achieves r=0.7 reliability. Alpha, beta, gamma, and theta reliability improve with repeated viewings. Alpha-asymmetry reliability does not improve with additional viewings — treat alpha-asymmetry with caution for neuromarketing conclusions. Prefer ISC as the primary EEG reliability metric for ad/content evaluation; do not use alpha-asymmetry as a primary decision metric without explicit reliability caveats (J. Advertising 2024; BMC Psychology meta-analysis 2025, ISC–attention r=0.65, 14 studies).

**Consumer-grade EEG validity limits (Scientific Reports 2026, n=30, vs DSI-24 research-grade):** P300 is detectable in consumer devices but ERP temporal resolution is distorted. Consumer devices are more artifact-prone in frontal regions. Muse2 shows the poorest signal quality (broadband power spectrum distortion, highest test-retest variability) among tested devices. Use consumer-grade EEG only for gross attention/engagement indices (ISC, broad spectral bands); do not rely on temporal ERP precision, fine-grained alpha-asymmetry, or frontal measures from consumer devices. A public dataset is available (Scientific Data 2026) for protocol validation and cross-study standardization.

| Vendor | Primary Signal | Typical Use | Cost Tier | Lab vs Field | Risk Flag |
|--------|--------------|-------------|-----------|--------------|-----------|
| Emotiv EPOC X / EPOC Flex | EEG (14–32 ch), facial EMG | Lightweight consumer neuro; academic hobbyist | £–££ | Lab-light | GDPR purpose-based classification |
| Muse (InteraXon) | 4-channel EEG (frontal-temporal) | Meditation feedback; rudimentary alpha/theta | £ | Wearable | GDPR classification; 2026 comparative study: worst signal quality among consumer devices — broadband spectral distortion, highest test-retest variability; not suitable for ERP or alpha-asymmetry research |
| NeuroSky MindWave | 1-channel EEG | Legacy; attention/meditation index only | £ | Wearable | GDPR classification; insufficient for primitive-level research |
| Apple Vision Pro / Vision Pro 2 (as of early 2026) | Eye-tracking (high-precision onboard), arousal-proxy via gaze/dwell | Attention research in spatial computing context; Apple does not expose raw biometric stream to third-party apps by default | ££££ (device) | In-the-wild limited | Apple restricts biometric data access; check current entitlements before research use |

### AI-Driven Affect Inference

Regulatory status follows intended purpose and deployment, including current classification criteria and exceptions; no platform category is automatically high-risk. Consult the [dated classification source note](ethics-operational-checklist.md#dated-eu-classification-source-note) before selecting applicable notices or dates.

| Vendor | Signal | Typical Use | Cost Tier | Risk Flag |
|--------|--------|-------------|-----------|-----------|
| Affectiva (acquired by Smart Eye, 2021) | Facial AU → emotion; voice → emotion | Automotive, media research | ££–£££ | Purpose-specific AI Act/GDPR classification required; sensor or vendor alone is insufficient |
| Hume AI (as of early 2026) | Voice, face, text → multi-dimensional affect | Conversational AI emotional intelligence; user experience research | ££ (API) | Purpose-specific AI Act/GDPR classification required; sensor or vendor alone is insufficient |
| Audeering (as of early 2026) | Voice → emotion, arousal, valence | Call-centre, mental health, automotive | ££ | Purpose-specific AI Act/GDPR classification required; sensor or vendor alone is insufficient |
| Sonde Health (as of early 2026) | Voice → mental health biomarkers | Clinical and wellness applications | ££ | Purpose-specific AI Act/GDPR classification required; sensor or vendor alone is insufficient |

---

## Decision Tree

```
1. BUDGET
   └─ < £5k  → Self-service behavioural surrogates (Hotjar/PostHog/FullStory)
      Else → continue

2. ECOLOGICAL VALIDITY NEEDED
   └─ Field deployment required → consumer-grade neuro or webcam (Tobii Sticky, Realeyes)
      Lab acceptable → continue

3. SIGNAL PRECISION REQUIRED
   └─ ERP-level (N400, P300, LPP) → Research-grade EEG (BrainProducts, Biosemi)
      Attention + arousal only → eye-tracking + GSR (iMotions, Tobii + Shimmer)
      Facial affect → facial CV (Realeyes, Affectiva/Smart Eye) — see step 4

4. REGULATORY EXPOSURE
   └─ EU users + affect-related AI → qualified counsel confirms purpose-specific classification and applicable duties
      └─ Applicable legal duties verified and met? → proceed with documented assessment
         Not ready? → use facial EMG (lab, no AI inference) or drop facial signal

5. CONSENT FEASIBILITY
   └─ Research context → explicit opt-in, DPIA, ethics board
      Commercial product → Article 6 basis and applicable Article 9 condition after classification; if vulnerable cohort, apply ethics-operational-checklist.md stricter gate

6. OUTPUT
   └─ Lab + precision + budget → iMotions multimodal; BrainProducts EEG + Tobii eye
      Mid-market remote → Tobii Sticky + Hotjar (no affect AI)
      No-tooling → surrogate-signal substitutions in signal-to-design-cookbook.md
```

---

## DIY / No-Vendor Path

When budget is under £5k, consent infrastructure is absent, or regulatory exposure from biometric capture is unacceptable: use behavioural surrogate signals. See `assets/playbooks/signal-to-design-cookbook.md` (Surrogate-signal substitutions section) for the primitive → behavioural metric mapping. Session replay (Hotjar, FullStory, PostHog) combined with standard A/B testing (PostHog feature flags) covers primitives #1, #9, #10, and #12 with no biometric risk. Standard usability testing (Maze, Lookback) with 5–8 users covers qualitative primitives #3, #4, #5, #7, and #8 without physiological capture.

---

## Sources

- Bigne, E. et al. (2025). Neurophysiological tools in marketing research. _Psychology & Marketing_.
- Frontiers in Neuroergonomics (2025). Consumer neuro-insights review. DOI: 10.3389/fnrgo.2025.1542847.
- F1000Research (2025). Noninvasive neuromarketing methods. 14:1132.
- "Reliability of EEG Metrics for Assessing Video Advertisements." _Journal of Advertising_ (online Dec 2024). DOI: 10.1080/00913367.2024.2418109. n=116, 13 commercials. ISC most reliable; alpha-asymmetry reliability does not improve with repetition.
- "Intersubject correlation as a predictor of attention: a systematic review." _BMC Psychology_ (2025). DOI: 10.1186/s40359-025-02879-7. 14 studies, 27 effect sizes; ISC–attention r=0.65.
- "A comprehensive evaluation framework for consumer-grade EEG devices." _Scientific Reports_ (2026). DOI: 10.1038/s41598-026-39056-8. n=30, 4 consumer devices vs DSI-24.
- "EEG dataset of consumer- and research-grade systems." _Scientific Data_ (2026). DOI: 10.1038/s41597-026-06962-5. Public dataset for consumer EEG validation.
- EU AI Act: see the [dated official-source and access-limit note](ethics-operational-checklist.md#dated-eu-classification-source-note); reverify current law and purpose-specific classification before deployment.
- UK GDPR. Article 9 special-category data.
