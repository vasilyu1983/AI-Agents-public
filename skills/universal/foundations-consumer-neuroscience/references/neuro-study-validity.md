---
description: Decision rules for buying, evaluating and acting on neuromarketing and biometric consumer studies — buy/no-buy gate, metric reliability, vendor composite-score validation, neuroforecasting sample sizes, reporting template.
status: stable
---

# Neuro-Study Validity and Purchase Decisions

Use this file when a vendor pitches a study, a team hands over a completed neuro or biometric report, or someone proposes to act on a lab signal. The root SKILL.md has the four-part buy rule. This file gives the questions to ask and the thresholds behind them.

## 1. Buy / no-buy gate

| Question | Pass | Fail → do this instead |
|---|---|---|
| Can the decision be answered by an in-market A/B test or holdout within the decision window? | No (e.g. TV cut chosen before the media buy) | Run the A/B test; it is the ground truth |
| Does the primary metric have published reliability in a comparable ad or stimulus task at the planned n? | Citation plus reliability coefficient at n | Choose a different metric, raise n, or do not buy |
| Is any composite or proprietary index validated out of sample against market or behavioural outcomes? | Holdout validation report | Treat the index as untested; ask for raw component metrics |
| Is there a preregistered primary metric, n, exclusion rule and decision threshold? | Written before fieldwork | Write it before signing |
| Is the self-report plus behavioural pre-test already insufficient? | Shown on this decision | Start with the cheaper pre-test |

A small expected effect is **not** a reason to buy a small-n lab study. If the lab measure is not itself validated against the outcome, a subtle effect makes a lab study less informative, not more.

## 2. Metric reliability and validity

- **van Diepen, Boksem & Smidts (2025), J. Advertising 54(4):506–526**, DOI 10.1080/00913367.2024.2418109 (online 2024-12-10). Abstract: reliability ranged from poor (alpha asymmetry) to good (alpha, beta) to excellent (ISC). Repeated viewings improved reliability. 30–40 participants were required for most metrics. The abstract reports no ISC-specific minimum (figures such as n≈11–15 for r≈0.7 circulate) and does not say that FAA fails to improve with repetition; read the full text before using either claim.
- **ISC and attention:** ISC tracked attention with r≈0.65 across 14 studies (BMC Psychology 2025, DOI 10.1186/s40359-025-02879-7). This concerns attention generally, not ad effectiveness.
- **EEG preference measures:** a 174-paper systematic review (Brain Informatics, DOI 10.1186/s40708-022-00175-3) found FAA the most cited and LPP the most reliable ERP, but limited consistency across papers against preference and purchase. Single-metric EEG preference claims are weak evidence.
- **Autonomic arousal:** the brain affective arousal signature (BAAS, Nat. Commun. 2025, DOI 10.1038/s41467-025-61706-0; validation across 24 studies, n=868) is statistically distinct from GSR/HRV autonomic arousal. GSR is activation, not felt arousal, and has no valence.
- **Consumer-grade EEG:** limit claims from consumer headbands to ISC and broad spectral bands; see [patterns-scenarios-traps.md](patterns-scenarios-traps.md).

## 3. Incremental and predictive validity

- **Venkatraman et al. (2015), JMR 52(4):436–452**, DOI 10.1509/jmr.13.0593. Six methods (self-report, implicit, eye-tracking, biometrics, EEG, fMRI) on 30-second TV ads, related to market-level advertising elasticities from sales and GRP time series. fMRI measures explained the most variance beyond traditional measures; ventral striatum activity was the strongest predictor. Use it to bound expectations: incremental validity over self-report is the question to ask of every method.
- **Neuroforecasting:** NAcc activity forecast aggregate internet-market outcomes regardless of lab-sample representativeness, with about 20–25 subjects sufficient (Genevsky, Tong & Knutson 2025, PNAS Nexus 4(2):pgaf029). In a conservation and social-media domain, group MPFC rather than NAcc forecast aggregate engagement out of sample (Srirangarajan et al. 2026, PNAS Nexus 5(2):pgag012; n=34). Which region generalises depends on the domain; preregister it.

## 4. Vendor evaluation questions

1. What is the test-retest or split-half reliability of your primary metric, in which task, at what n? Show the source.
2. How was the composite index built, and what is its validity on a holdout set of ads with known market outcomes?
3. What does the metric add over a self-report pre-test on the same ads (incremental variance)?
4. What artefact-rejection and exclusion rules apply, and what was the exclusion rate?
5. Is any ML classifier cross-validated on independent stimuli and participants, not only on held-out trials?
6. What data do we receive: raw signals or only the index?
7. How is consent and data classification handled (neural data vs biometric vs other personal data), and where is data stored?

A vendor that cannot answer 1–3 is selling an unvalidated score.

## 5. Reporting template

```
STUDY — [decision] — [date]
Decision and alternatives: [what changes depending on the result]
Preregistration: [link/date; primary metric; n; threshold]
Method: [modality, n, within/between, exclusions and rate]
Primary result: [effect size with CI; reliability achieved]
Incremental validity: [vs self-report / behavioural pre-test]
Evidence rows: mechanism / measurement / product-effect (mark missing rows)
Recommendation: [ship to A/B / iterate / no decision value]
Data and consent: [classification; lawful basis; retention]
```

## Sources

See [`../data/sources.json`](../data/sources.json): `Venkatraman2015JMR`, `ReliabilityEEGAds2024JA`, `ISCAttentionMeta2025BMC`, `Genevsky2025PNASNexus`, `Srirangarajan2026PNASNexus`, `BAAS2025NatComms`, `Poldrack2011Neuron`.
