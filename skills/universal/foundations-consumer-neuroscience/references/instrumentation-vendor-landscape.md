---
description: Signal modality reference and decision tree for consumer-neuroscience instrumentation. No vendor list or cost tiers; includes the DIY surrogate-signal path.
status: stable
---

# Instrumentation and Modality Reference

## Table of Contents

- [Purpose](#purpose)
- [Signal Modality Reference](#signal-modality-reference)
- [Consumer-Grade Neuro Validity](#consumer-grade-neuro-validity)
- [Decision Tree](#decision-tree)
- [DIY / No-Vendor Path](#diy--no-vendor-path)
- [Sources](#sources)

---

## Purpose

Selecting measurement tools is a design decision, not just a procurement decision. The modality chosen determines which primitives can be observed directly vs. inferred, sets the ecological-validity ceiling, creates regulatory obligations (physiological personal data requires purpose-based classification; health inference or biometric identification may invoke Article 9; affect-inference AI may fall under EU AI Act duties; check the current timeline and purpose-specific classification), and constrains the N achievable in budget (look up current vendor specifications, prices and terms directly; this file lists none). This reference maps signal modalities, a decision tree, and the conditions under which surrogate behavioural signals are the right answer instead of physiological measurement.

---

## Signal Modality Reference

| Signal | What It Measures | Temporal Resolution | Spatial Resolution | Ecological Validity | GDPR Special-Category? | EU AI Act Risk Class |
|--------|-----------------|--------------------|--------------------|---------------------|------------------------|----------------------|
| fMRI (functional MRI) | BOLD signal as proxy for neural activity | ~2s (poor) | ~1–3mm (excellent) | Very low (supine, scanner noise) | Purpose/inference dependent | Low (research-only; no commercial deployment path currently) |
| EEG (research-grade, 64–256 channels) | Millisecond-resolution cortical ERP and oscillatory power | ~1ms (excellent) | Low-moderate (source localisation limited) | Low–moderate (lab) | Purpose/inference dependent | Low–moderate |
| EEG (consumer-grade, 4–14 channels) | Coarse ERP; frontal asymmetry; theta/alpha bands | ~5ms | Very low | Moderate (passive wear) | Purpose/inference dependent | Moderate |
| fNIRS (functional near-infrared spectroscopy) | Prefrontal haemodynamic response; cognitive load proxy | ~1–2s | Low | Moderate (ambulatory) | Purpose/inference dependent | Low |
| Eye-tracking (screen-based) | Fixation, saccade, AOI dwell, pupillometry | ~1–4ms | ~0.5° visual angle | Moderate (lab-like screen context) | Purpose/inference dependent | Low |
| Eye-tracking (glasses, mobile) | Fixation in natural environment; gaze in physical retail | ~1–4ms | ~0.5° | High | Purpose/inference dependent | Low |
| GSR/EDA (skin conductance) | Sympathetic arousal; phasic event-related response; tonic baseline | ~0.5–2s | N/A (peripheral) | Moderate | Purpose/inference dependent | Low |
| HRV (heart rate variability) | Vagal tone; cognitive load; stress; autonomic balance | ~1s | N/A | High (wearable) | Purpose/inference dependent | Low |
| Facial EMG | Specific muscle-group activity (e.g., zygomatic = smile; corrugator = frown) | ~5ms | Muscle-group | Low (electrodes on face) | Purpose/inference dependent | Low |
| Facial action coding — CV (computer vision) | Inferred facial AUs and emotion categories from video | Near real-time | Per-frame | High (any camera) | Purpose/inference dependent | Purpose-specific AI Act/GDPR classification required; sensor or vendor alone is insufficient |
| Voice prosody analysis | Pitch range, rate, energy; arousal/disengagement proxy | ~100ms | N/A | High | Purpose/inference dependent | Purpose-specific AI Act/GDPR classification required; sensor or vendor alone is insufficient |
| Pupillometry (standalone) | Arousal; cognitive effort; locus coeruleus-NE system activity | ~1ms (with eye-tracker) | N/A | Moderate | Purpose/inference dependent | Low |

---

## Consumer-Grade Neuro Validity

**EEG metric reliability for ad testing (van Diepen, Boksem & Smidts 2025, J. Advertising 54(4):506–526):** reliability ranged from poor (alpha asymmetry) to good (alpha, beta) to excellent (ISC, intersubject correlation). Repeated viewings improved reliability, and 30–40 participants were needed for most metrics. The abstract reports no ISC-specific minimum and no repetition result for alpha asymmetry; read the full text before relying on either. Prefer ISC as the primary EEG metric for ad/content evaluation; do not use alpha asymmetry as a primary decision metric. Full buy/no-buy rules: [neuro-study-validity.md](neuro-study-validity.md).

**Consumer-grade EEG validity limits (Scientific Reports 2026, n=30, vs DSI-24 research-grade):** P300 is detectable in consumer devices but ERP temporal resolution is distorted. Consumer devices are more artifact-prone in frontal regions. Muse2 shows the poorest signal quality (broadband power spectrum distortion, highest test-retest variability) among tested devices. Use consumer-grade EEG only for gross attention/engagement indices (ISC, broad spectral bands); do not rely on temporal ERP precision, fine-grained alpha-asymmetry, or frontal measures from consumer devices. A public dataset is available (Scientific Data 2026) for protocol validation and cross-study standardization.

---

## Decision Tree

```
1. BUDGET AND CONSENT INFRASTRUCTURE
   └─ Low budget or no consent infrastructure → behavioural surrogates (session replay, A/B tests)
      Else → continue

2. ECOLOGICAL VALIDITY NEEDED
   └─ Field deployment required → consumer-grade neuro or webcam signals (validity limits above)
      Lab acceptable → continue

3. SIGNAL PRECISION REQUIRED
   └─ ERP-level (N400, P300, LPP) → research-grade EEG
      Attention + arousal only → eye-tracking + GSR
      Facial affect → facial computer vision — see step 4

4. REGULATORY EXPOSURE
   └─ EU users + affect-related AI → qualified counsel confirms purpose-specific classification and applicable duties
      └─ Applicable legal duties verified and met? → proceed with documented assessment
         Not ready? → use facial EMG (lab, no AI inference) or drop facial signal

5. CONSENT FEASIBILITY
   └─ Research context → explicit opt-in, DPIA, ethics board
      Commercial product → Article 6 basis and applicable Article 9 condition after classification; if vulnerable cohort, apply ethics-operational-checklist.md stricter gate

6. OUTPUT
   └─ Pick the cheapest modality that answers the question; confirm vendor specifications and terms with the vendor.
      No-tooling → surrogate-signal substitutions in signal-to-design-cookbook.md
```

---

## DIY / No-Vendor Path

When budget is tight, consent infrastructure is absent, or regulatory exposure from biometric capture is unacceptable: use behavioural surrogate signals. See `assets/playbooks/signal-to-design-cookbook.md` (Surrogate-signal substitutions section) for the primitive → behavioural metric mapping. Session replay combined with standard A/B testing covers primitives #1, #9, #10, and #12 with no biometric risk. Standard usability testing with 5–8 users covers qualitative primitives #3, #4, #5, #7, and #8 without physiological capture.

---

## Sources

- Bigne, E. et al. (2025). Neurophysiological tools in marketing research. _Psychology & Marketing_.
- Frontiers in Neuroergonomics (2025). Consumer neuro-insights review. DOI: 10.3389/fnrgo.2025.1542847.
- F1000Research (2025). Noninvasive neuromarketing methods. 14:1132.
- "Reliability of EEG Metrics for Assessing Video Advertisements." _Journal of Advertising_ (online Dec 2024). DOI: 10.1080/00913367.2024.2418109. n=116, 13 commercials. ISC most reliable.
- "Intersubject correlation as a predictor of attention: a systematic review." _BMC Psychology_ (2025), DOI 10.1186/s40359-025-02879-7. Unsourced — verify; pooled figure not quoted.
- "A comprehensive evaluation framework for consumer-grade EEG devices." _Scientific Reports_ (2026). DOI: 10.1038/s41598-026-39056-8. n=30, 4 consumer devices vs DSI-24.
- "EEG dataset of consumer- and research-grade systems." _Scientific Data_ (2026). DOI: 10.1038/s41597-026-06962-5. Public dataset for consumer EEG validation.
- EU AI Act: see the [dated official-source and access-limit note](ethics-operational-checklist.md#dated-eu-classification-source-note); reverify current law and purpose-specific classification before deployment.
- UK GDPR. Article 9 special-category data.
