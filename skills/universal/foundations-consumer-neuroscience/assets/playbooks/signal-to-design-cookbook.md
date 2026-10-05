---
description: Observation → behavioural hypothesis → test recipes. Maps what product teams observe (replays, reports, A/B results, study outputs) to a testable behavioural hypothesis, a design move, a fail signal and a verification method. No neural diagnosis.
status: stable
---

# Signal-to-Design Cookbook

## Purpose

This playbook bridges study outputs and product teams. The signal dictionary (`references/biomarker-signal-dictionary.md`) says what a lab signal can and cannot mean. This cookbook starts from what product teams actually observe — session replay patterns, qualitative reports, A/B results, study outputs — and turns each into a **behavioural hypothesis** and a test. Template numbers (#1–#12) name the behavioural primitive a hypothesis draws on. They are not neural diagnoses, and a design move here is justified only by the test that follows it.

---

## Recipe Table

| Observation | Behavioural hypothesis | Design move | Fail signal | Verification |
|-------------|----------------------|-------------|-------------|--------------|
| Users skip the hero image/headline without reading | The hero is not relevant or salient enough to earn attention (#1) | Lead with a problem statement that matches the visitor's task; raise contrast only where it carries information; remove the hero if it cannot earn attention | Users still skip the high-relevance version | First-fixation latency to hero element; click-zone heatmap; scroll depth at hero |
| High dwell time on page, low conversion | Content holds attention but the next action is unclear or badly placed (#4, #12) | Test CTA placement: within the story at the point it resolves vs after it; make the action consistent with the story's promise | Dwell remains high but conversion still low → hypothesis wrong | Scroll-conditional click rate; A/B test CTA position |
| Funnel bounce concentrated mid-flow | Cognitive load or effort spike at that step (#2 + BE #14) | Strip extraneous information from mid-flow screens; one decision per screen; fewer form fields; progress indicator | Bounce moves to next screen — load was downstream | Per-screen drop-off funnel; session replay of bounce sessions; time-on-screen distribution |
| Strong week-1 engagement, decay to near-zero by week-3 | No reason to return once novelty fades; no anticipated next step (#9, #10) | Test a user-chosen daily reminder time; preview tomorrow's content today; add a meaningful milestone | Decay moves to week-5 rather than stopping — partial fix only | Day-7 and Day-30 cohort retention curves; notification open rate by timing cohort |
| Testimonials placed but not converting | Testimonials are not credible or not representative of the visitor (#6) | Use verified testimonials from users whose situation matches the page's promise; test face vs no face and video vs text | Conversion still low → testimonial content or relevance is the issue | A/B test: verified matched testimonial vs current; click-through from testimonial module |
| Users report "felt scammed" or "felt pushed" | Pressure tactics triggered reactance (#2 + reactance) | Audit for countdown timers, false scarcity, confirm-shaming, pre-ticked defaults; remove them; run the choice-architecture audit (ethics-operational-checklist.md) | "Felt pushed" reports continue → the pressure mechanic is elsewhere in the flow | Qualitative exit survey; NPS; CSAT post-purchase; audit log |
| AI chatbot trust collapses after first error | Recovery lacks acknowledgement and an explanation of what changed (#3, #12) | Explicit error acknowledgement from a named team; let the user choose whether and when to re-engage; state what changed. Oxytocin is not a trust lever (Declerck et al. 2020) | Predeclared trust/task outcome fails to recover | Trust or NPS at T+24h and T+7d; session re-engagement rate after error event |
| Anxiety-relief product drives session time but low return visits | Sessions have no clear end and no reason to return (#10, #12) | Add a clear closure beat ("your reading is complete"); cap the core mechanic per day; say what comes next ("tomorrow: X") | Return rate improves but session time drops too far — adjust closure timing | Day-2 and Day-7 return rate; session-length distribution before/after |
| Premium aesthetic tests well pre-launch, flops post-launch | Visual quality promised more than the product delivers (#7, #10) | Match the aesthetic tier to delivered quality, or invest in delivery before relaunch; never use polish to cover product gaps | Users keep cancelling post-trial → functional gap is primary | Post-trial cancellation reason; aesthetic vs functional satisfaction split in CSAT |
| Push notifications opened but in-app action near zero | Timing/preference mismatch, low content value, task friction or cue-behaviour gap | Test separately: (a) a user-preferred timing alternative within quiet hours; (b) copy tied to a cue that already occurs (morning coffee, commute) | Neither improves action → content relevance is the issue | Open → action conversion by timing and copy cohort |
| Onboarding completion drops sharply at step 3 | Step 3 asks for something users hesitate over (effort, data, commitment); frame may not fit that decision (#5) | First fix the content (why is step 3 needed; what happens to the data). Then test a gain frame ("step 3 unlocks your dashboard") vs a safety frame ("a 90-second check that keeps your account secure"), randomised for all users | Both frames drop at step 3 → the issue is content complexity, not framing | A/B completion at step 3; if segmenting, use an explicit stated-goal question, never referral source |
| Pupil dilation observed in user study but no behaviour change | Arousal or effort does not imply intent (interpretation trap) | Do not infer purchase intent from dilation; add a behavioural follow-up (stated preference, next action, A/B test) | Follow-up A/B shows no effect → dilation indexed load, not desire | Paired behavioural measure in the same study; A/B test on the stimulus |
| Voice prosody flat in user testing of onboarding script | Low vocal arousal: calm, bored or recording artefact (#2) | Re-test with more relevant content and a conversational register; do not infer dislike | Prosody stays flat with relevant content → recording context artefact | Re-test in a more naturalistic setting; check recording confounds |
| Users engage with daily content but never share it | Nothing worth sharing, or sharing costs the sender socially (#3, #6) | Add a shareable artefact (result card, insight) that is useful or flattering to the sender; test it | Share rate rises but engagement drops — users optimise for shareability over value | Share rate vs engagement; qualitative: "what made you want to share this?" |
| Retention is high but satisfaction (CSAT) is low | Compulsion-design risk: wanting without liking (#10) | Audit for open-ended loops; add stopping signals; measure wanting and liking separately; redesign if the gap persists | Satiation signal reduces engagement sharply → engagement was anticipation-driven | Survey "looking forward to this" before and "glad I did this" after, in the same cohort |
| Feature has strong lab neuro scores but weak A/B lift | Lab measure did not predict field behaviour | Treat the A/B result as the commercial signal; check the lab metric's reliability and incremental validity ([neuro-study-validity.md](../../references/neuro-study-validity.md)) | Near-zero lift across iterations → drop the lab metric for this decision | Which segments show the effect? Was the lab sample representative? |
| Trial users churn at upgrade | Upgrade copy may not fit what users want to protect or gain (#5) | Test a truthful safety frame ("keep your saved insights") vs a gain frame, randomised across all trial users; no fabricated loss | No frame difference → price or value is the issue | Upgrade conversion and 30-day refund rate by variant; perceived pressure |
| Strong UK performance, weak EU conversion | Localisation gap or consent friction | Check whether the consent flow reduces the funnel; test localised copy and visual register per market | Persists after consent fix → market-specific proposition or trust issue | Funnel drop-off by country; consent acceptance rate; qualitative testing |
| Participants complete study but find it invasive | Consent experience felt surveilling, not participatory | Rewrite debrief and consent language; make opt-out genuinely easy; this is a study-design fix | Satisfaction stays low → reconsider physiological capture for this population | Post-study satisfaction; debrief comments; consent withdrawal rate |

---

## The 4 Question-Archetypes

| Archetype | Symptom | Primary primitive shortlist | Secondary check |
|-----------|---------|---------------------------|-----------------|
| **Attention failed** | Low engagement at entry; hero skipped; notification ignored | #1 (salience/relevance), #12 (layout or copy violates expectations), #7 (visual quality) | Is a relevance hook missing (#4)? |
| **Trust broke** | "Felt scammed"; NPS drop; post-error churn; testimonials not converting | #3 (care claims not backed by reality), #6 (testimonials unverified or unrepresentative), #12 (unexplained changes or errors) | Reactance; choice-architecture audit |
| **They engaged but didn't act** | High dwell / open rate; low conversion | #10 (anticipation not tied to an action), #5 (frame does not fit the decision), #4 (story without a clear next step) | BE #14 (cognitive load at the decision point) |
| **They acted but regret it** | Post-purchase cancellation; low CSAT; "felt manipulated" | #10 (wanting without liking), #7 (aesthetic over-promised), #3 (warmth not backed by care) | Vulnerable-user gate; ethics-operational-checklist.md |

---

## Behavioural Surrogates

When no physiological tooling is available — which is the normal case — measure the behavioural hypothesis directly. These metrics test behaviour; they do not confirm a neural explanation, and the lab column is only what a study *might* add.

| Primitive | Optional lab measure (non-selective) | Behavioural measure | Tool |
|-----------|-----------|----------------------|------|
| #1 Attention & Salience | Eye-tracking first fixation; dwell | Scroll depth; click-zone heatmap; dwell per section | Session analytics |
| #2 Arousal & Load | GSR phasic response | Rage clicks; exit spikes at specific elements; perceived-pressure item | Session analytics; survey |
| #3 Social Bonding | — (no validated lab trust marker) | NPS; referral rate; community join rate; support contact tone | CRM, NPS tool |
| #4 Narrative Transportation | EEG ISC (attention) | Transportation scale; scroll completion; saves; share rate | Analytics + survey |
| #5 Regulatory Focus & Fit | — (FAA reliability is poor) | Gain vs safety frame A/B; stated-goal segments only | Feature flags + survey |
| #6 Social Proof & Modelling | Facial coding (validated tools only) | Verified testimonial vs none A/B; video watch-through | A/B test; video analytics |
| #7 Aesthetics | Self-report SAM scale | 5-second first-impression test; preference survey | Unmoderated testing |
| #8 Interoception / Felt State | HRV (load, not trust) | Post-flow "how do you feel?" item | In-product survey |
| #9 Memory | Delayed recall test | Day-7/Day-30 retention; recall survey at 48h | Cohort analytics |
| #10 Reward Anticipation | GSR before reveal | Open rate before reveal; teaser click-through; wanting vs liking survey | Push analytics; survey |
| #11 Embodied Metaphor | Reaction time to metaphor | Body-metaphor vs abstract copy A/B | A/B test |
| #12 Expectation & Predictability | N400/P300 (lab only) | Task completion; error rate after UI changes; session starts after an update | Error event tracking |
