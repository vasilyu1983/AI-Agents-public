---
description: End-to-end study-design playbook for consumer-neuroscience research — from hypothesis to product decision. Covers when not to run one, study-type matrix, N requirements (including EEG ISC), within/between-subject design, ecological validity, analysis, and common failure modes.
status: stable
---

# Study Design Playbook

Before buying or commissioning a study, run the buy/no-buy gate and vendor questions in [neuro-study-validity.md](../../references/neuro-study-validity.md).

## When to Run a Study vs Use Surrogate Signals

Run a physiological study when:
- The decision cannot be answered by an in-market A/B test or holdout in time (e.g., a TV cut chosen before the media buy), **and** the primary metric has published reliability at the planned n.
- The cost of a wrong product decision exceeds the study cost.
- Ethical obligations require confirming that a technique does not harm users before deployment (vulnerability contexts: wellness, anxiety, financial-distress products).
- Do **not** run one because the expected effect is small. A small-n lab study is less able than a large A/B test to detect a subtle effect, unless the lab measure is itself validated against the outcome.

Use surrogate behavioural signals (session replay, A/B test, click data, qualitative usability testing) when:
- Budget is under £5k.
- Consent infrastructure for biometric data capture is absent.
- Regulatory exposure from biometric capture is unacceptable (EU AI Act Article 9 / GDPR constraints).
- The signal of interest has a reliable behavioural proxy (see `assets/playbooks/signal-to-design-cookbook.md`, Surrogate-signal substitutions section).

Neuro studies pre-screen A/B test candidates. A/B tests are the ground truth for behaviour at scale. Run them in sequence, not as substitutes.

---

## Study Type Matrix

| Question Type | Method | Typical N | Duration | Cost Ballpark (UK, 2026) |
|--------------|--------|-----------|----------|--------------------------|
| Ad or creative pre-test: which version earns attention and positive affect? | Eye-tracking + GSR + facial action coding (lab or validated webcam) | 30–50 | 1 week | £5k–£15k |
| Landing-page funnel diagnosis: where is cognitive friction occurring? | Screen-based eye-tracking + GSR; session replay as complement | 30 | 2 weeks | £8k–£20k |
| Narrative / onboarding immersion: does the content produce transportation? | EEG (LPP) + GSR + eye-tracking (research-grade lab) | 20–30 | 3–4 weeks | £20k–£50k |
| Pricing / decision moment: is reward anticipation or loss framing active? | EEG (N400, LPP) lab; fMRI academic only | EEG: 30; fMRI: 20+ | 4–8 weeks | EEG: £15k–£30k; fMRI: £30k–£80k (academic) |
| Brand perception: conscious vs non-conscious brand associations | xAI-integrated fMRI (per Frontiers Human Neuroscience 2024 methods); academic partnership required | 20–25 | 6–12 weeks | £50k+ (academic only) |
| Push / notification timing: which timing maximises day-7 retention? | Field cohort split (no biometric required); surrogate sufficient | 500+ per cell | 4 weeks | Low (internal A/B) |
| Testimonial design: does a verified testimonial with a face beat none? | Behavioural A/B (click-through, conversion); optional facial coding for stated-affect checks. Mu suppression is not an MNS readout | A/B: power-based | 2–4 weeks | Low (internal A/B) |

---

## Protocol Skeleton (7 Steps)

**Step 1 — Hypothesis**
State a falsifiable hypothesis referencing a named primitive. Example: "Inserting a brief anticipation phase before the daily reveal will increase day-7 open rate (#10) compared to immediate reveal, without lowering post-reveal satisfaction." A physiological measure may be secondary; it cannot confirm the mechanism on its own.

Verify: hypothesis names primitive(s), specifies direction, and has at least one measurable outcome.

**Step 2 — Primitives Targeted + IV/DV**
Identify the independent variable (design feature you are manipulating), the dependent variable (behavioural metric first; physiological signal optional), and which primitive maps each DV. Specify the direction of expected effect.

Verify: IV is a single controlled manipulation; the primary DV is behavioural or has published reliability at the planned n.

**Step 3 — Instrumentation Choice**
Select modality using the decision tree in `references/instrumentation-vendor-landscape.md`. Confirm regulatory status: if biometric capture, purpose-based GDPR classification and applicable lawful conditions; if AI-based affect inference, EU AI Act Article 50 transparency (live from 2 August 2026) and Annex III high-risk readiness (deferred to 2 December 2027).

Verify: vendor or tool confirmed; consent mechanism designed; ethics-operational-checklist.md pre-study section completed.

**Step 4 — Recruitment**
Define inclusion/exclusion criteria. Screen for vulnerable cohort (see ethics-operational-checklist.md). Aim for a representative sample on the dimensions that plausibly moderate the effect (age, anxiety trait if relevant, stated goal if regulatory fit is the hypothesis). Collect enough demographic data to check for demographic confounds.

Verify: recruitment screener tested; no under-18 without parental consent; DPIA filed where the processing is likely to result in high risk.

**Step 5 — Pilot Run (n = 5–8)**
Run a pilot to: (a) confirm stimulus timing and protocol flow, (b) check signal quality and artefact rate, (c) verify counterbalancing works, (d) catch debrief issues. Adjust protocol before main run.

Verify: pilot signal quality report reviewed; artefact rate acceptable; timing confirmed.

**Step 6 — Main Run + Analysis**
Run at full N. Apply the N requirements below. Analyse primary DV first; report effect size (Cohen's d or equivalent) and confidence interval, not just p-value. Correct for multiple comparisons if testing multiple signals or conditions (Bonferroni, FDR, or pre-registered comparison plan).

Verify: pre-registration (if applicable) completed before main run; analysis plan documented before data collection.

**Step 7 — Integration into Product Decision**
Map the signal result to a ship / iterate / kill recommendation using the effect-size thresholds below. Provide a behavioural follow-up plan (A/B test to confirm at scale). Write the reporting template (see below).

Verify: recommendation is primitive-anchored; behavioural follow-up is scheduled; results shared with ethics-review stakeholder.

---

## N Requirements (August 2026 Standards)

These are practical lower bounds, not statistical guarantees. Power depends on effect size, which is unknown until the study is run. Pre-register with a sequential analysis plan where feasible.

| Modality | Practical Minimum N | Notes |
|----------|---------------------|-------|
| GSR (event-related phasic analysis) | ≥30 | Within-subject preferred for power |
| Eye-tracking — fixation heatmaps | ≥30 | AOI conversion analysis requires ≥50 |
| Eye-tracking — AOI conversion | ≥50 | |
| EEG — ERP components (N400, P300, LPP) | ≥25 within-subject | Multiple comparisons correction required; Frontiers Neuroergonomics 2025 |
| EEG — video-ad metrics (ISC, spectral bands, FAA) | 30–40 for most metrics | Per van Diepen, Boksem & Smidts (2025, J. Advertising 54(4):506–526) abstract; ISC most reliable, FAA poor. The abstract gives no lower ISC-specific minimum; read the full text before using one |
| fMRI — region-of-interest | ≥25 | Multiple comparisons correction (cluster-FWE or FDR) mandatory |
| Webcam emotion AI | ≥100 | Lower per-trial signal quality requires higher N; treat as exploratory unless validated against lab measure |
| Facial EMG | ≥20 within-subject | |
| HRV — task-epoch analysis | ≥20 | Minimum 5-min baseline epoch required |

Sources: Frontiers in Neuroergonomics (2025) consumer neuro-insights review; Bigne (2025) P&M methodology notes; van Diepen, Boksem & Smidts (2025) for the EEG video-ad row. Other rows are practical conventions, not derived from a power analysis.

---

## Within-Subject vs Between-Subject Design

Neuro studies strongly prefer within-subject designs for power. Within-subject:
- Controls for individual baseline neural variability (critical for EEG ERPs, frontal alpha asymmetry, HRV).
- Usually needs fewer participants than a between-subject design for equal power; how many fewer depends on the within-subject correlation between conditions. Do not quote a fixed percentage saving; compute it from the expected correlation.
- Requires counterbalancing to control order and carryover effects.

Carryover risk: emotional states persist beyond stimulus offset. Insert inter-stimulus intervals of at least 10–15s for GSR recovery; 2–3 minutes for mood carry-over in narrative studies. Randomise stimulus order per participant; do not present all conditions of one type consecutively.

Between-subject design is appropriate when: (a) the manipulation has lasting effects (brand re-evaluation, trust breach), (b) stimulus recognition across conditions would confound the test, or (c) the study tests a feature that changes the product state (onboarding versions).

---

## Ecological Validity Ladder

| Level | Context | Validity | Control | Use When |
|-------|---------|----------|---------|----------|
| Lab pure | Controlled stimulus, unnatural setting | Low | High | ERP research requiring artefact-free signal; preliminary mechanism validation |
| Lab simulated | Screen-based test with naturalistic stimulus (e.g., real website in lab) | Moderate | High | Ad/landing pre-tests; most commercial neuro studies |
| In-cabin / VR | Naturalistic context (automotive, retail simulation) | Moderate–high | Moderate | Automotive HMI; retail shelf placement; spatial product experiences |
| In-the-wild webcam | Participant uses own device at home or work | High | Low | Remote ad pre-tests; webcam eye-tracking; emotion AI (where compliant) |
| Field deployment (surrogate signals) | Real product, real users, behavioural metrics only | Highest | Lowest | A/B test confirmation; session replay; PostHog event analysis |

---

## Analysis and Integration

**Signal to recommendation:**

| Effect Size (Cohen's d or equivalent) | Recommendation |
|---------------------------------------|----------------|
| d ≥ 0.4 | Candidate for A/B: effect is large enough to test; do not ship on the lab result alone |
| d 0.2–0.4 | Iterate: signal present but effect is modest; refine design and re-test before shipping |
| d < 0.2 | Null / inconclusive: do not ship on this basis; consider whether the mechanism hypothesis was wrong |

**Integration with A/B schedule**: neuro studies pre-screen A/B candidates. If d ≥ 0.4 in the neuro pre-screen, the design variant earns a slot in the A/B test queue. The A/B test measures behavioural outcomes (conversion, retention, engagement) and is the definitive commercial signal. The neuro study can show what participants attended to or reacted to; it does not by itself explain why (reverse inference). The A/B test confirms whether it matters at scale.

**Pre-registration**: pre-register the primary hypothesis, sample size, and analysis plan on OSF or AsPredicted before data collection. This is standard practice per Frontiers in Neuroergonomics (2025) review and improves credibility of commercial neuro claims.

---

## Common Failure Modes

| Failure Mode | What Goes Wrong | Fix |
|-------------|----------------|-----|
| Under-powered ERP study | N = 15 produces noisy ERP; cannot distinguish signal from noise | Use within-subject; aim ≥25 for ERPs; run pilot to estimate effect size first |
| No baseline period | Tonic signals (GSR, HRV, frontal alpha) have no reference point; within-participant variation is uninterpretable | Always record 5–10 min resting baseline; EEG alpha asymmetry requires individual baseline normalisation |
| Poor counterbalancing | Order effects inflate or suppress condition differences | Full counterbalance (Latin square or ABBA) for within-subject; randomise per participant |
| Conflating arousal with valence | GSR spike interpreted as positive engagement; may be stress | Pair arousal signal with valence indicator (facial, SAM self-report) in every study |
| Generalising lab to in-the-wild | Lab N400/P300 amplitude or eye-tracking dwell does not predict field behaviour directly | A/B test is required to confirm behavioural translation; a lab signal is neither a mechanism proof nor a sales forecast |
| Missing artefact rejection | Movement artefacts in EEG/GSR inflate signal; facial EMG from speech in ERP studies | Document artefact-rejection criteria in pre-registration; report artefact-exclusion rate in results |
| Vulnerable cohort not screened | Anxiety-relief study recruits unscreened anxious participants; study causes harm | Complete ethics-operational-checklist.md pre-study gate; screen for clinical anxiety if anxiety-adjacent product |

---

## Reporting Template

Use this minimal structure for any neuro-study deliverable to a product team:

```
STUDY REPORT — [Product Feature] — [Date]

Hypothesis: [statement — primitive # named]
Primitives tested: [#N, #N]
Method: [modality, vendor, N, within/between]
Participants: [N, age range, demographics, screening criteria]
Signals: [list of DVs with measurement details]
Effect sizes: [d (CI) per comparison; significance level; correction method]
Behavioural correlate: [linked A/B result if available, or planned A/B]
Recommendation: [Ship / Iterate / Null — with rationale]
Ethics review: [DPIA reference; consent mechanism; vulnerable-user check status]
Limitations: [ecological validity; generalisability; any protocol deviations]
```
