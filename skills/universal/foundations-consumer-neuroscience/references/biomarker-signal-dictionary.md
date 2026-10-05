---
description: Signal interpretation lookup. For each observed biomarker pattern — what it can and cannot index, confounds, misreads and hard constraints. Deliberately contains no "design move to amplify": a signal is an observation, not a target.
status: stable
---

# Biomarker Signal Dictionary

## Purpose

Use this file for the question "I observed X — what can it mean, and what must I not conclude?" Each row lists what a signal can index, the confounds, and the most common misread. Nothing here licenses a design change. A signal supports a **behavioural hypothesis** that must then be tested (see the evidence contract in [evidence-to-product.md](evidence-to-product.md)).

Reverse inference rule (Poldrack 2011): inferring a mental state from a signal requires evidence that the signal is selective for that state in this task. None of the signals below is selective on its own. Signal validity also depends on the instrument and population; verify reliability at your n before optimising anything.

---

## Signal Dictionary

| Signal pattern | What it can index (non-selective) | Template | Confounds, misreads and hard constraints |
|---|---|---|---|
| GSR phasic spike (1–3 s post-stimulus) | Sympathetic activation; orienting to a salient stimulus | #2 | Valence unknown: excitement and distress look the same. Pair with a valence measure (self-report). Not felt arousal (BAAS 2025) |
| Sustained elevated GSR baseline (>15 min) | Sustained autonomic activation; temperature, movement and other causes must be ruled out | #2 | Not "high engagement" and not a diagnosis of chronic stress. If task-related, check cognitive demand and session length |
| Heart-rate deceleration (~200–600 ms post-stimulus) | Orienting / attentional capture | #1 | Distinguish from sustained HR decrease (relaxation); temporal precision matters |
| HRV drop (RMSSD, SDNN) | Reduced vagal tone; load, stress or physical factors | #2, BE #14 | Indexes cost, not reward. Never treat as engagement |
| Pupil dilation | Arousal plus cognitive effort (Kahneman 1973); luminance-sensitive | #1, #2 | Pupil ≠ interest. Control luminance; pair with a performance or behavioural measure |
| Short saccades + long fixations on an AOI | Processing of that element | #1 | Fixation ≠ comprehension; long dwell can mean confusion |
| First-fixation latency on target | Bottom-up salience of the target in that layout | #1 | Salience ≠ liking or intent |
| N400 ERP (~400 ms, centro-parietal) | Semantic expectancy violation in the tested context (Kutas & Federmeier 2011) | #12 | Not dislike, not "engagement". Lab ERP; does not transfer to live copy without a behavioural test |
| P300 / P3b ERP | Attention allocation to a task-relevant or oddball stimulus (Polich 2007) | #1 | Not proportional to purchase intent |
| LPP (400–1000 ms+, centro-parietal) | Motivated attention to emotionally salient stimuli, either valence (Schupp et al. 2000) | #4, #10 | LPP ≠ positive affect. Do not optimise content to sustain LPP; that pushes towards intensity, not value |
| Frontal alpha asymmetry (FAA), either direction | Relative frontal alpha difference; conventionally read as approach/withdrawal, depending on formula, reference and context | #5 | **Poor reliability** for video-ad testing (van Diepen, Boksem & Smidts 2025, J. Advertising 54(4):506–526); inconsistent against preference (174-paper Brain Informatics review). State the formula; normalise to each person's resting baseline; never classify or target an individual; not a primary decision metric |
| Mu-band suppression (8–13 Hz, sensorimotor) | Sensorimotor desynchronisation during action observation or execution; its interpretation as mirror-neuron activity is contested | #6 | Also sensitive to attention and occipital alpha; not an MNS readout and not a reason to add faces or motion |
| Ventral striatum / NAcc BOLD (fMRI) | Reward-related BOLD response; not a direct dopamine measure | #10 | Slow haemodynamics; cannot establish transmitter identity or timing. Aggregate neuroforecasting evidence exists (Venkatraman et al. 2015; Genevsky et al. 2025) but is domain-dependent |
| Default-mode network BOLD (mPFC, PCC, angular gyrus) | Activity common to self-referential thought, memory, social cognition **and** mind-wandering | #4 | Not a transportation or absorption measure; boredom also raises it. Use the transportation scale |
| Anterior insula BOLD | Highly non-selective: interoception, salience, pain, disgust, uncertainty and more | #8 | One of the least selective regions for reverse inference. Never manufacture somatic cues in anxiety contexts |
| Facial AU6 + AU12 (Duchenne configuration) | A smile configuration | #3, #7 | Not proof of felt affect or truthfulness. Webcam tools vary widely in AU6 accuracy; lab EMG or validated coding needed |
| Facial AU4 (brow lowerer) | Effort, confusion or negative affect | #12 | May indicate deliberation, not rejection |
| Voice pitch-range collapse | Lower vocal arousal | #2 | Calm and bored look alike; recording context matters. Do not infer dislike |

---

## Multimodal Stacks: What They Can and Cannot Answer

### Ad or landing-page pre-test
**Signals:** eye-tracking + GSR/EDA + self-report; facial coding only with a validated tool.
**Can answer:** where attention went (fixations), whether a moment was activating (GSR), and stated liking and recall.
**Cannot answer:** whether the ad will lift sales. Anchor on ISC or behavioural outcomes where possible and validate against an in-market test.
**Protocol:** preregister the primary metric; baseline period; counterbalanced order; n set from the metric's published reliability (the J. Advertising abstract reports 30–40 for most EEG metrics).

### Narrative study
**Signals:** transportation scale (Green & Brock 2000) + recall + attitude; EEG ISC as an optional attention measure.
**Can answer:** whether people report being transported and whether recall or attitude moved.
**Cannot answer:** DMN or LPP amplitude cannot certify transportation.

Stack protocols for interoceptive "trust" measures were removed. HRV or vagal-tone changes do not index trust.

---

## Misread Traps

| Signal | Common misread | Correct interpretation |
|---|---|---|
| GSR spike | Positive engagement | Autonomic activation, statistically separable from subjective arousal (BAAS, Nat. Commun. 2025); valence unknown |
| Pupil dilation | Interest or liking | Arousal plus effort; overload causes sustained dilation |
| Frontal alpha asymmetry | Valid without a baseline | Needs an individual resting baseline and a stated formula; poor reliability even then |
| Webcam emotion AI output | Lab-grade emotion coding | Lower per-AU accuracy than lab EMG; indicative only |
| Heart-rate decrease | Calm | Brief deceleration = orienting; sustained decrease = relaxation |
| HRV drop | High engagement | Sympathetic dominance: load or stress |
| Any regional BOLD | "The brain wants it" | Reverse inference; needs selectivity evidence |

---

## Sources

- Poldrack, R. A. (2011). Inferring mental states from neuroimaging data. _Neuron_, 72(5), 692–697.
- van Diepen, R. M., Boksem, M. A. S. & Smidts, A. (2025). Reliability of EEG metrics for assessing video advertisements. _Journal of Advertising_, 54(4), 506–526. DOI 10.1080/00913367.2024.2418109.
- Venkatraman, V. et al. (2015). Predicting advertising success beyond traditional measures. _Journal of Marketing Research_, 52(4), 436–452.
- Kahneman, D. (1973). _Attention and Effort_. Prentice-Hall.
- Polich, J. (2007). Updating P300. _Clinical Neurophysiology_, 118(10), 2128–2148.
- Kutas, M. & Federmeier, K. D. (2011). Thirty years and counting: finding meaning in the N400. _Annual Review of Psychology_, 62, 621–647.
- Schultz, W. (1997). Dopamine neurons and their role in reward mechanisms. _Current Opinion in Neurobiology_, 7(2), 191–197.
- Ekman, P. & Friesen, W. V. (1978). _Facial Action Coding System_. Consulting Psychologists Press.
- Schupp, H. T. et al. (2000). Affective picture processing: the late positive potential. _Psychophysiology_, 37(2), 257–261.
- Davidson, R. J. (2004). Well-being and affective style. _Philosophical Transactions of the Royal Society B_, 359, 1395–1411.
- Craig, A. D. (2009). How do you feel — now? _Nature Reviews Neuroscience_, 10(1), 59–70.
- Knutson, B. et al. (2001). Anticipation of increasing monetary reward selectively recruits nucleus accumbens. _Journal of Neuroscience_, 21(16), RC159.
- Bigne, E. et al. (2025). Neurophysiological tools in marketing research. _Psychology & Marketing_.
