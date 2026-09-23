---
description: Operational go/no-go gates for DMCC Act 2024, EU AI Act, US neural-data laws, and UK/EU GDPR. Pre-study and pre-deployment checklists, vulnerable-user gate, decision tree, and documentation pack.
last_verified: 2026-08-14
status: stable
---

# Ethics Operational Checklist

## Table of Contents

- [Purpose](#purpose)
- [Pre-Study Checklist](#pre-study-checklist-any-neuro-research-data-collection)
- [Pre-Deployment Checklist](#pre-deployment-checklist-commercial-product-or-feature)
- [Vulnerable-User Gate](#vulnerable-user-gate-binding)
- [Decision Tree](#decision-tree)
- [Documentation Pack](#documentation-pack)

---

## Purpose

The ethical boundaries stated in SKILL.md and the per-primitive playbooks are conceptual. This checklist converts them to operational gates: concrete yes/no questions with stopping rules. It is a pre-study gate for any neuro-research data collection and a pre-deployment gate for any commercial feature applying primitives to live users. Red-flag answers stop the work; yellow-flag answers require DPO or legal review before proceeding; green answers permit shipping with a documented rationale kept on file.

---

## Pre-Study Checklist (any neuro-research data collection)

Run before initiating any study that captures physiological, biometric, or neuro-signal data from participants.

- [ ] **Lawful processing and participation documented**: obtain informed research consent; identify an Article 6 basis for personal data. Assess whether health information/inference or biometric unique identification invokes Article 9 and record a valid condition if applicable. Physiology alone does not establish special-category status, and explicit consent is not the only Article 9 condition.
- [ ] **DPIA requirement assessed**: complete a DPIA where processing is likely to result in high risk; record the assessment and responsible review. Physiological capture does not automatically determine the requirement.
- [ ] **Ethics board reviewed**: if any academic institution is involved, has the relevant ethics board approved the protocol? If commercial-only, has an internal ethics review (or equivalent external review) been completed?
- [ ] **Vulnerable-cohort screen completed**: does the sample include or potentially include individuals under 18, individuals with mental health conditions, individuals in financial distress, or audiences for wellness/anxiety/spiritual/financial-products? If yes, the Vulnerable-User Gate below applies — do not proceed until it is passed.
- [ ] **Opt-out path is trivial**: can a participant withdraw at any point during data collection without penalty, and does the study protocol document the withdrawal mechanism?
- [ ] **Child / age-gate confirmed**: if under-18 participation is possible, has parental consent been obtained and verified?
- [ ] **Debrief protocol documented**: will participants be debriefed about the study aims and methods, including any deception (if applicable), immediately after participation?
- [ ] **Data retention and deletion policy stated**: is a defined retention period in place, with a deletion mechanism? Is this communicated to participants?
- [ ] **Cross-border transfer mechanism**: if biometric data will be stored or processed outside the UK or EU, is an appropriate transfer mechanism in place (UK-EU adequacy, SCC, BCR)?

---

## Pre-Deployment Checklist (commercial product or feature)

Run before shipping any feature that applies consumer-neuroscience primitives to live user flows.

### DMCC Act 2024 — Online Choice Architecture Audit (in force 6 April 2025)

- [ ] **No drip pricing**: is the full price (including all mandatory charges) displayed before the user enters the purchase flow?
- [ ] **No default opt-ins that benefit the operator at user expense**: are all pre-selected defaults genuinely in the user's interest? This is the pattern that produced the CMA's second DMCC penalty (Marks Electrical, 18 June 2026: £720,000 plus ~£600,000 consumer redress for auto-opting customers into paid add-on services). Any charge a user did not expressly agree to is the highest-probability enforcement trigger.
- [ ] **No false urgency**: are countdown timers, "limited stock" signals, and "X people viewing this" indicators accurate and verifiable? If not, remove.
- [ ] **No confirm-shaming**: does the decline option use neutral language? ("No thanks" not "No, I don't want to improve my life")
- [ ] **No forced continuity**: is auto-renewal prominently disclosed before purchase, with a clear and accessible cancellation path?
- [ ] **Signal honesty gate**: are all arousal triggers (#2), warmth signals (#3), urgency cues, and social-proof indicators (#6) verifiable and accurate? Any fabricated signal = fail.

### EU AI Act Article 5 Prohibitions (in force 2 February 2025)

- [ ] **No subliminal techniques check**: does any feature use stimuli below the threshold of conscious perception to influence behaviour? If yes, stop for review of Article 5(1)(a): impaired informed choice, materially changed decision and actual or reasonably likely significant harm must be assessed. Our ethical gate may be stricter than the statutory prohibition.
- [ ] **No manipulative/deceptive techniques check**: does any AI system use deceptive techniques or techniques that exploit psychological weaknesses to materially distort behaviour in a way that harms the user? If yes, stop for review of Article 5(1)(a), including its informed-decision and significant-harm conditions.
- [ ] **Vulnerability-exploitation check**: does any AI system exploit vulnerabilities of specific groups (age, disability, socio-economic situation) to materially distort their behaviour? If yes, stop for review of Article 5(1)(b), including material distortion and actual or reasonably likely significant harm. Vulnerable cohort membership alone is not a prohibition.

### EU AI Act Article 50 Transparency (in force 2 August 2026 — NOT delayed)

Apply only after purpose-specific classification establishes a relevant obligation. Generic sentiment analysis, sensor capture and a vendor label do not establish emotion recognition or biometric categorisation. See the dated source note below.

- [ ] **Article 50 notice live**: are users explicitly informed, clearly and accessibly at first interaction/exposure (our research safeguard is earlier notice before capture), that an emotion-recognition or biometric-categorisation system is operating? This is a current obligation, not a future one.
- [ ] **Watermarking grace tracked** (if generating/manipulating synthetic content): confirm the applicable synthetic-output marking transition against the current law; watermarking is one possible technique, not the statutory duty itself.

### EU AI Act High-Risk (deferred to 2 December 2027, if applicable)

Apply only after counsel confirms an applicable high-risk use, including current Article 6 criteria, exceptions, research exclusions and provider/deployer role. Follow the dated official timeline below. Physiological inputs or commercial deployment alone do not establish high-risk status.

- [ ] **High-risk classification confirmed**: has the intended use been assessed under the current amended Article 6 and Annex III, including relevant derogations, exclusions and profiling conditions?
- [ ] **Data governance documentation complete**: is the training dataset documented for composition, provenance, and demographic representativeness?
- [ ] **Technical documentation filed** (Article 11): is the required technical documentation prepared and maintainable?
- [ ] **Human oversight mechanism implemented** (Article 14): can a human reviewer identify, monitor, and override the system's outputs?
- [ ] **Post-market monitoring plan documented** (Article 72): is there a plan for ongoing performance monitoring and incident reporting?
- [ ] **Accuracy and robustness testing completed** (Article 15): has the system been tested for accuracy across relevant demographic subgroups?

### UK / EU GDPR

- [ ] **Purpose-based classification recorded**: document Article 6 basis for personal data and an applicable Article 9 condition where health inference or biometric unique identification brings processing within special-category rules. Do not automatically require Article 9 explicit consent for every physiological signal.
- [ ] **Data minimisation applied**: is only the minimum necessary biometric data captured for the stated purpose?
- [ ] **Retention policy implemented**: is a defined retention period enforced with automated deletion?
- [ ] **Cross-border transfer mechanism in place** (if applicable): see pre-study checklist item above.

### US Neural Data Laws (where product serves US users)

**Scope first — do not over-apply.** These statutes target signals from the nervous system measured directly (EEG, fNIRS). Montana expressly excludes "downstream physical effects of neural activity" (pupil dilation, motor activity, breathing rate); California excludes data inferred from nonneural information; Colorado reaches only identification-purpose data. GSR, HRV, eye-tracking, facial coding, and voice affect therefore fall mostly **outside** these laws — but remain governed by general sensitive-data/biometric statutes and GDPR Art. 9. Answer this gate first:

- [ ] **Signal classification done**: is the captured signal true neural data (EEG/fNIRS) or a downstream/inferred physiological signal? Record the determination and the statute relied on. If downstream, route to the general GDPR/biometric gates above rather than claiming exemption.
- [ ] **Montana SB 163 consent gate** (effective 1 Oct 2025) — **strictest US regime**: if the product captures neurotechnology data from Montana users, is express consent obtained *separately for each purpose and each third-party recipient* (collection, marketing use, research use, disclosure, transfer, sale)?
- [ ] **California SB 1223 consent gate** (effective 1 Jan 2025): if the product captures EEG, GSR, voice, facial-coding, or any nervous-system-derived signal from California users, is separate opt-in consent obtained before capture? Is the right to delete and restrict sharing documented in the privacy notice?
- [ ] **Colorado HB 24-1058** (effective 7 Aug 2024): if product serves Colorado users and captures neural data (signals from central or peripheral nervous system), is it treated as sensitive data under the Colorado Privacy Act with opt-in consent?
- [ ] **Connecticut SB 1295** (effective 1 Jul 2026): if product serves Connecticut users and captures neural data, is express consumer consent obtained? Is neural data excluded from sale without consent?
- [ ] **Vermont H.814 / Act 101** (effective 1 Jul 2026) — **no consent gate**: the enacted act states largely declaratory "neurological rights"; the consent requirement and private right of action were stripped before passage, and enforcement rests solely with the Vermont Attorney General. Do not treat it as a consent gate. The binding Vermont framework is **S.71**, effective 1 Jan 2028 — apply that bill's consent/processing requirements when it takes effect, and track it for pre-2028 readiness.
- [ ] **UNESCO Recommendation (Nov 2025) acknowledgement** (global products): for products with global reach using neuro-signal capture, has the team reviewed and documented alignment with the UNESCO Recommendation on the Ethics of Neurotechnology's core principles (mental privacy, transparency, consent)?
- [ ] **MIND Act readiness** (if product involves neuromarketing specifically): if the FTC study proceeds to rulemaking, is there a documented posture on how the product's neuromarketing practices would be justified under an FTC standard?

### ASA CAP Code (UK)

- [ ] **Claims substantiated**: are any neuroscience-based marketing claims (e.g., "scientifically designed," "clinically proven") substantiated by published evidence or internal studies available for ASA review?
- [ ] **Testimonials verified**: are all testimonials from real, identifiable users? Are results described in testimonials typical or clearly qualified as non-typical?

---

## Vulnerable-User Gate (Binding)

If the target audience is any of the following: wellness users, anxiety-relief users, astrology or spiritual users, users experiencing financial distress, minors, or any audience for whom regulatory guidance identifies heightened vulnerability — **the stricter column of every check above applies, and the following patterns are banned by default**:

| Pattern | Ban Rationale |
|---------|---------------|
| Manufactured urgency (countdown, false scarcity) | Exploits heightened stress sensitivity; DMCC vulnerable-user clause + EU AI Act Art. 5 |
| Oxytocin-proxy warmth without genuine care mechanic (#3 misuse) | Short-term affiliation collapse in vulnerable users has amplified harm; DMCC aggressive-practices provision |
| Unbounded reward-anticipation loops (#10 misuse) | Compulsion-design risk is elevated in anxiety and financial-distress contexts; harm-test failure |
| Interoceptive urgency manufacturing (#8 misuse — "your body is telling you something is wrong") | Manufacturing somatic anxiety to drive purchase is manipulation under DMCC vulnerable-user clause |
| AI-driven affect inference without transparency or high-risk readiness | Assess applicable notices and high-risk timetable after intended-use classification; review Article 5 conditions and exceptions independently. A vulnerable audience or sensor label alone does not establish a prohibition |

**Default position for ambiguous primitive deployment in vulnerable-user context: No.** Shift the default to Yes only with documented harm-test outcome showing user benefit on reflection, easy reversibility, and no exploitation of pre-conscious mechanisms.

---

## Decision Tree

```
Any red-flag answer (Article 5 prohibition / DMCC dark-pattern / fabricated signal)?
→ STOP. Do not ship. Redesign required.

Any yellow-flag answer (high-risk AI Act not yet compliant / GDPR gap / vulnerable-user pattern without mitigation)?
→ PAUSE. Route to DPO and/or legal review. Do not ship until cleared.

All green?
→ SHIP with documented rationale (see Documentation Pack below).
```

---

## Documentation Pack

Keep the following on file for any shipped feature that applies consumer-neuroscience primitives:

1. **Harm-test result per primitive**: written record of the three-gate test (user endorsement on reflection; easy reversal; no exploitation of pre-conscious mechanisms) for each primitive applied.
2. **Consent flow screenshots** (if biometric or neuro data is captured in a product context): documented data classification and lawful conditions; capture UI evidence when consent is the condition used.
3. **EU AI Act technical documentation** (if high-risk system): full Annex IV technical documentation file.
4. **DMCC OCA audit log**: completed pre-deployment checklist above, dated and signed by accountable team member.
5. **Vulnerable-user assessment**: written assessment confirming whether the target audience meets vulnerable-user criteria and, if so, the stricter-column controls applied.
6. **DPIA assessment**: record whether processing is likely to result in high risk; retain the DPIA and review date where required.

## Dated EU classification source note

Verified 2026-09-17. The [Commission entry-into-force announcement](https://digital-strategy.ec.europa.eu/en/news/ai-omnibus-enters-force) reports the AI Omnibus adopted and effective 27 July 2026. Its [updated implementation timeline](https://ai-act-service-desk.ec.europa.eu/en/ai-act/timeline/timeline-implementation-eu-ai-act) lists Article 50 from 2 August 2026, certain pre-existing synthetic-content providers' Article 50(2) transition at 2 December 2026, Annex III high-risk rules from 2 December 2027, and Annex I high-risk rules from 2 August 2028. These are application milestones, not automatic classification of every affect-related product.

Source limit: the Commission links [the amending instrument](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=OJ:L_202601744), but EUR-Lex access was bot-blocked in this audit. Official [Article 5](https://ai-act-service-desk.ec.europa.eu/en/ai-act/article-5), [Article 6](https://ai-act-service-desk.ec.europa.eu/en/ai-act/article-6) and [Article 50](https://ai-act-service-desk.ec.europa.eu/en/ai-act/article-50) pages explicitly warn their displayed statutory text is not yet updated. Thus the timeline is officially confirmed; amended classification details require qualified counsel to read current governing text before deployment. Record intended purpose, inputs/inferred attributes, jurisdiction, research/commercial context, operator role and decision consequences. Do not use this checklist as a legal opinion.
