---
name: foundations-consumer-neuroscience
description: Evaluates neuromarketing studies and neural-data law. Use when judging EEG, fMRI, eye-tracking, or GSR ad study or vendor, or if signals are regulated neural data.
compatibility: Portable core only.
version: "2.0"
last_validated: 2026-08-14
---

# Consumer Neuroscience Foundations

Evaluate study validity and neural-data scope separately. The behavioural templates below generate hypotheses to test with behavioural outcomes; a brain-region label does not validate a design move.

## When to Use

- An agency or vendor pitches a neuromarketing study, an "engagement index", or a neural or biometric ad pre-test.
- A team reports a lab signal (GSR spike, alpha asymmetry, fixation heatmap, emotion-AI score) and wants to act on it.
- A product will capture EEG, fNIRS, HRV, GSR, eye movement, face or voice affect, and someone asks what law applies.
- Someone is designing a copy, framing or narrative test and needs a behavioural hypothesis template (see the table below).

**Skip it and use the owner instead:**

- Pricing, defaults, anchoring, dark-pattern and DMCC/CMA enforcement → `foundations-behavioral-economics`.
- Generic score or survey reliability and validity with no physiological signal → `foundations-measurement-theory`.
- Causal lift of a shipped change → `foundations-causal-inference` or an A/B test.
- Usability or attention research without biometrics → `software-ux-research`.

## Workflow

1. Classify the ask: study purchase or evaluation, signal interpretation, neural-data law scope, or a behavioural design question (route the last to the templates below or to `foundations-behavioral-economics`).
2. For a study or vendor: apply the four-part buy rule and the quick reference, then the vendor questions in `references/neuro-study-validity.md`.
3. For any neural or biometric finding: fill the three evidence rows and refuse reverse inference.
4. For data capture: classify the signal (neural vs downstream) before choosing the legal gate.
5. Turn what survives into a behavioural hypothesis and an in-market test.

## Evidence Contract

When a recommendation relies on a neural mechanism or biomarker, record three separate rows:

- `mechanism evidence`: the process exists.
- `measurement evidence`: this measure tracks that process in this task and population, at this n.
- `product-effect evidence`: the intervention changes the user outcome in the field.

A biomarker association does not establish the last two. Behaviour-first advice that makes no neural claim needs no neural rows. State the behavioural outcome, the test design and the causal limit instead. Full record, confound table and regression checks: [references/evidence-to-product.md](references/evidence-to-product.md).

**No reverse inference.** Going from "region or signal X was active" to "users felt Y" needs evidence that X is selective for Y in this task (Poldrack 2011). Insula, DMN, mu-band suppression, N400, GSR and pupil dilation are all non-selective. Report the observation and test the behavioural hypothesis; do not name a mental state.

## Should We Buy a Neuro Study?

Buy only if **all four** hold. Otherwise run a self-report pre-test plus an in-market holdout or A/B test.

1. **Decision fit.** The decision is between creative or stimulus variants that cannot be field-tested cheaply or quickly (for example TV cuts before a media buy). If an A/B test can answer it within the decision window, the A/B test is the ground truth.
2. **Published reliability at your n.** The primary metric has published test-retest or split-half reliability in a comparable ad task at the planned sample size. Generic claims ("EEG measures attention") do not count.
3. **Out-of-sample validity of any composite.** A vendor's proprietary index (engagement, emotion, "neuro score") must show validity against held-out market or behavioural outcomes, not only correlations inside the calibration set. No validation data means the index is untested and is not evidence.
4. **Preregistered decision rule.** The primary metric, n, exclusion rules and the threshold that changes the decision are written down before data collection.

Why this bar: head-to-head evidence is specific to its tested task. Venkatraman et al. (2015, JMR 52(4):436–452) compared six methods (self-report, implicit, eye-tracking, biometrics, EEG, fMRI) on 30-second TV ads against market-level ad elasticities. fMRI measures explained the most variance beyond traditional measures, and ventral striatum activity was the strongest predictor. That is one study, one ad format and a lab-to-market link, not a licence for any vendor's metric.

**When NOT to buy:** the choice is reversible and testable in-market; the vendor will not disclose reliability or validation data; the metric is frontal alpha asymmetry or a webcam emotion score used as the primary outcome; the sample is below the metric's published requirement; or the product-effect question is really a causal-lift question.

Detail, vendor-evaluation questions and reporting template: [references/neuro-study-validity.md](references/neuro-study-validity.md). Study protocol and n by modality: [assets/playbooks/study-design.md](assets/playbooks/study-design.md).

## Quick Reference: Metric Validity

| Metric | What the evidence supports | Use as primary? |
|---|---|---|
| EEG inter-subject correlation (ISC) | Excellent between-sample reliability for video ads ([van Diepen, Boksem & Smidts 2025](https://pure.eur.nl/en/publications/reliability-of-eeg-metrics-for-assessing-video-advertisements/)). The [Liu et al. 2025 review](https://link.springer.com/article/10.1186/s40359-025-02879-7) pools several modalities and synchrony measures; its attention association is not an EEG-ad calibration | For video attention only with task-specific validation; still needs a behavioural outcome |
| EEG alpha / beta power | Rated good reliability in the same study | Secondary |
| Frontal alpha asymmetry (FAA) | Poor between-sample reliability in the same video-ad study; this does not establish preference or purchase validity | No. Secondary only, baseline-normalised, never to classify an individual |
| GSR / EDA, HRV | Autonomic activation; statistically distinct from subjective affective arousal (BAAS, Nat. Commun. 2025); valence unknown | No. Pair with a valence and a behavioural measure |
| Eye-tracking fixations | Where people looked; not liking, comprehension or intent | For attention allocation only |
| fMRI ventral striatum / NAcc, MPFC | Neuroforecasting of aggregate outcomes; which region generalises depends on the domain (Genevsky et al. 2025; Srirangarajan et al. 2026). A study's successful sample size is not a transferable minimum | Research partnership only |
| Facial coding / webcam emotion AI | A facial configuration is not proof of felt emotion; consumer tools vary widely in accuracy | No |
| ML classifier on neuro signals | Prediction accuracy does not establish mental-state construct validity; participant or stimulus leakage can inflate it | Only with independent cross-study validation and an independently justified target label |

Sample size: the [van Diepen et al. abstract](https://pure.eur.nl/en/publications/reliability-of-eeg-metrics-for-assessing-video-advertisements/) reports that repeated viewings improved reliability and that 30–40 participants were needed for most metrics to assess an ad overall; temporal tracking needed more. Read the full text for the metric, number of viewings and reliability threshold before using a minimum.

## Neural-Data Law Scope (US)

Before classifying a capture, identify the consumer's jurisdiction, the measured signal, intended use and applicable entity exemptions. Use a state-privacy tracker to locate legislation, then read the legislature's enacted text and amendments for its neural-data definition, consent or limitation rights, and effective date. The examples below are scope distinctions, not a current or exhaustive state list.

| State | Status | Scope point |
|---|---|---|
| [Colorado HB 24-1058](https://leg.colorado.gov/bills/hb24-1058) | Original effective date: 7 Aug 2024 | Neural data within biological data; the biological-data definition requires an identification purpose |
| [California SB 1223](https://leginfo.legislature.ca.gov/faces/billNavClient.xhtml?bill_id=202320240SB1223) | Original effective date: 1 Jan 2025 | CNS or PNS signals "not inferred from nonneural information"; CCPA sensitive PI. Right to limit qualifying use and disclosure; this amendment itself creates no general opt-in requirement |
| [Montana SB 163, §4](https://docs.legmt.gov/download-ticket?ticketId=19ba2309-6a40-42d4-9f4e-86c77e44d090) | Original effective date: 1 Oct 2025 | Initial express consent; separate express consent for non-processor third-party transfers/disclosures and uses beyond the primary purpose; informed express consent for specified research disclosures; express consent for marketing and sale. Excludes downstream physical effects (pupil dilation, motor activity, breathing rate) |
| Connecticut SB 1295 | Original effective date: 1 Jul 2026 | CNS-only definition; consent to process; no sale without consent |
| [Vermont S.71 (Act 145)](https://legislature.vermont.gov/bill/status/2026/S.71) | Original obligations date: 1 Jan 2028 | CNS-only definition; consent to process and to sell; AG enforcement with 60-day notice-and-cure until 30 Jun 2029; no private right of action. Check amendments before applying |

- **Vermont H.814 (Act 101)** is a separate, aspirational neurological-rights statement. Its operative provisions were stripped before passage. It has no enforcement mechanism, compliance obligations, consent requirement or penalties for businesses; its operative part is a study directive (Cooley, 2026-06-23). It is not a consent gate.
- **Practical consequence:** assess EEG against each statute's definition and purpose limits. Do not automatically classify fNIRS as direct neural measurement: it [measures haemodynamic changes indirectly](https://pmc.ncbi.nlm.nih.gov/articles/PMC7364176/), so inference and nonneural-information exclusions need counsel's analysis. For GSR, HRV, eye-tracking, facial coding and voice affect, assess downstream-signal exclusions separately. Then check ordinary personal-data, health-data and biometric rules by jurisdiction and purpose; these signals do not all automatically qualify under BIPA or GDPR Art 9. Record the lawful basis and any consent required even where a neural-data statute does not apply.
- **Watch list:** further state bills keep appearing; look them up rather than relying on a count here. The federal MIND Act (introduced 24 Sep 2025) was a proposal; check its current status. UNESCO's non-binding neurotechnology Recommendation was adopted 12 Nov 2025.

**EU and UK.** Classify the purpose first. Sensor capture alone does not make a system emotion recognition, biometric categorisation or high-risk. Workplace or education emotion inference raises AI Act Art 5(1)(f); check the medical or safety exception. Before assigning a compliance deadline, consult the [European Commission's AI Act timeline](https://digital-strategy.ec.europa.eu/en/policies/regulatory-framework-ai), distinguishing Art 5, Art 50 and high-risk obligations. The classification checklist is in [references/ethics-operational-checklist.md](references/ethics-operational-checklist.md). Under GDPR, physiology is not automatically special-category data: record an Art 6 basis and assess whether health inference or unique identification brings in Art 9. DMCC and CMA choice-architecture enforcement is owned by `foundations-behavioral-economics`. Route final classification to qualified counsel; when source access is unavailable, report the affected classification or deadline as unverified.

## Behavioural Hypothesis Templates

Each template gives a definition, misuse boundary, inputs and outputs, failure modes and a worked example. Use them to write a testable behavioural hypothesis. Neural background is context only.

When choosing or combining templates, load the [composition guide](assets/templates/consumer-neuroscience/README.md) for the shared misuse boundaries and recipe selection before opening the selected playbooks.

| # | Template | Behavioural question to test | Evidence caution |
|---|---|---|---|
| 1 | [Attention & Salience](assets/templates/consumer-neuroscience/01-attention-salience.md) | Does the priority element get seen and acted on? | First fixation ≠ liking |
| 2 | [Arousal Physiology](assets/templates/consumer-neuroscience/02-arousal-physiology.md) | Does intensity help or hurt task completion and comfort? | GSR ≠ felt arousal; Yerkes-Dodson is not a design law |
| 3 | [Social Bonding](assets/templates/consumer-neuroscience/03-social-bonding.md) | Do real care signals change perceived care and retention? | The registered replication found no main oxytocin effect under its tested conditions (Declerck et al. 2020) |
| 4 | [Narrative Transportation](assets/templates/consumer-neuroscience/04-narrative-transportation.md) | Does a story format change transportation score, recall and attitude? | Measure transportation by scale (Green & Brock 2000; van Laer et al. 2014), not DMN |
| 5 | [Regulatory Focus & Fit](assets/templates/consumer-neuroscience/05-approach-avoidance.md) | Does message–goal fit beat a mismatched frame for this decision? | Regulatory focus ≠ BIS/BAS; referral source is not a classifier |
| 6 | [Mirror Systems & Emotional Contagion](assets/templates/consumer-neuroscience/06-mirror-systems.md) | Do verified testimonials with faces beat none? | Mu suppression is not an MNS readout |
| 7 | [Neuroaesthetics](assets/templates/consumer-neuroscience/07-neuroaesthetics.md) | Does the visual variant change preference and credibility? | Polish without delivery backfires |
| 8 | [Interoception & Somatic Markers](assets/templates/consumer-neuroscience/08-interoception-somatic.md) | Does body-state framing inform, or does it pressure? | Never manufacture somatic urgency |
| 9 | [Memory Consolidation](assets/templates/consumer-neuroscience/09-memory-consolidation.md) | Does timing or spacing change recall and retention? | No clock-defined consolidation window |
| 10 | [Reward Anticipation](assets/templates/consumer-neuroscience/10-reward-anticipation.md) | Do reveals raise wanting without lowering liking? | Measure wanting and liking separately; cap loops |
| 11 | [Embodied Cognition](assets/templates/consumer-neuroscience/11-embodied-cognition.md) | Does a congruent metaphor improve comprehension? | Social-priming demos failed replication |
| 12 | [Predictive Processing](assets/templates/consumer-neuroscience/12-predictive-processing.md) | Does format consistency or a primed reveal reduce errors and churn? | No "surprise budget" can be measured in UX |

Multi-template recipes (anxiety-relief journey, reading bond, daily cadence, mixed-audience landing page, trust repair, ethics audit, AI assistant UX) and the misuse-boundary table: [references/composition-recipes.md](references/composition-recipes.md).

## Harm Test

A technique is legitimate only if it:

1. steers users towards outcomes they would endorse on reflection;
2. can be easily overridden or opted out of;
3. does not rely on concealment, manufactured signals (fake urgency, fake warmth, fake social proof) or exploitation of vulnerability.

Wellness, anxiety, spiritual and financial-distress audiences get the stricter default: No, unless there is a documented harm-test pass. Operational gates (pre-study, pre-deployment, US neural-data consent, vulnerable-user bans): [references/ethics-operational-checklist.md](references/ethics-operational-checklist.md).

## Anti-Patterns

| Anti-pattern | Why it fails | Instead |
|---|---|---|
| "Region X lit up, so users felt Y" | Reverse inference without selectivity | Report the signal; test the behaviour |
| FAA or a webcam emotion score as the decision metric | Poor or unvalidated reliability | ISC or behavioural outcome as primary |
| Buying a vendor composite index on face value | No out-of-sample validity shown | Demand holdout validation, or do not buy |
| Neuro study instead of an A/B test for a testable choice | Lab-to-field gap; small n | A/B test is ground truth; neuro can only pre-screen |
| Consumer EEG headband reported like research-grade ERPs | Hardware and processing can distort signals and change reliability | Require metric-specific validation on the proposed hardware; ISC and broad bands are not automatic exemptions |
| Personalising by referral source as a "BIS/BAS" proxy | Channel carries intent and traffic-quality confounds | Test message–goal fit directly |
| "Oxytocin-driven trust" copy | No replicated main effect | Real care mechanics; measure perceived care |
| Notifications timed to a "consolidation window" | No clock window is established | User-selected timing, quiet hours, randomised cohorts |
| Treating GSR, eye or face data as outside all privacy law | Out of neural-data statutes does not mean unregulated | General biometric, sensitive-data and GDPR analysis |
| Assuming a hormone or consolidation timer sets an interface deadline | Neural response timing and hormone kinetics do not set UX deadlines — there is no cortisol, oxytocin or consolidation timer for UX | Use measured behavioral timing, not a claimed neural window |

More traps with sources (consumer-EEG validity, ML-on-neuro overfit, social priming): [references/patterns-scenarios-traps.md](references/patterns-scenarios-traps.md).

## Navigation

| File | Read when |
|---|---|
| [references/neuro-study-validity.md](references/neuro-study-validity.md) | Evaluating a vendor, pitch or completed neuro study |
| [references/evidence-to-product.md](references/evidence-to-product.md) | Turning any neural or biometric finding into a product recommendation |
| [references/biomarker-signal-dictionary.md](references/biomarker-signal-dictionary.md) | Interpreting a specific signal: what it can and cannot index, confounds, misreads |
| [references/ethics-operational-checklist.md](references/ethics-operational-checklist.md) | Before any study or launch that captures physiological data; US state neural-data gates |
| [references/instrumentation-vendor-landscape.md](references/instrumentation-vendor-landscape.md) | Choosing a modality or tool; confirm current vendor specifications and terms with the vendor before relying on them |
| [assets/playbooks/study-design.md](assets/playbooks/study-design.md) | Designing a study: n by modality, within/between, preregistration |
| [references/composition-recipes.md](references/composition-recipes.md) | Combining behavioural templates into a flow; misuse boundaries |
| [assets/playbooks/signal-to-design-cookbook.md](assets/playbooks/signal-to-design-cookbook.md) | "We observed X": behavioural hypotheses and verification |
| [references/frameworks-meta.md](references/frameworks-meta.md) | Choosing an organising frame; anti-frameworks (triune brain, "buy button") |
| [references/formal-theory-map.md](references/formal-theory-map.md), [references/primitives-overview.md](references/primitives-overview.md) | Theory background and limits per template |
| [`data/sources.json`](data/sources.json) | Primary sources |

- Key sources: Poldrack 2011 (reverse inference); Venkatraman et al. 2015; van Diepen et al. 2025; Genevsky et al. 2025; Srirangarajan et al. 2026; BAAS 2025; Declerck et al. 2020, Nat Hum Behav 4(6):646–655; Higgins 1997, 2000; Motyka et al. 2014; Green & Brock 2000; van Laer et al. 2014.

## Related Skills

- `foundations-behavioral-economics`: framing, defaults, reinforcement schedules, DMCC and dark-pattern enforcement.
- `foundations-measurement-theory`: reliability and validity of any score or scale.
- `foundations-causal-inference`: field lift and holdouts.
- `marketing-cro`, `marketing-paid-advertising`, `marketing-content-strategy`: apply templates 1, 4 and 5 through their `desire-segmentation.md` references.
- `software-ui-ux-design`, `software-ux-research`, `product-management`: attention, consistency and reward-loop hypotheses.

## Learnings Loop

When prior decisions or pitfalls are relevant, consult `learnings.consolidated.md` if present; use `learnings.md` only for needed history or as the available fallback. Otherwise skip both.

After applying it, if you encountered a pattern worth remembering, a mistake worth preventing, or a domain fact that surprised you, append one dated bullet to `learnings.md` via `agents-skills-feedback-loop/scripts/append_learning.py`. Do not modify `SKILL.md` itself.
