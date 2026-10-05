# Consumer Recruiting Guide

Audience: UX researchers recruiting participants for consumer product studies.
Tone: practical, ethics-aware.

---

## Table of Contents

- [Recruitment Sources Comparison](#recruitment-sources-comparison)
- [Screener Design](#screener-design)
- [Incentive Ethics & Rates](#incentive-ethics--rates)
- [Kids and Teens (Under 18)](#kids-and-teens-under-18)
- [Hawthorne Effect Mitigation](#hawthorne-effect-mitigation)
- [Time-of-Day and Geographic Bias](#time-of-day-and-geographic-bias)
- [Social-Desirability Bias](#social-desirability-bias)
- [Accessibility Participant Recruitment](#accessibility-participant-recruitment)
- [Recruiting Underrepresented Demographics](#recruiting-underrepresented-demographics)
- [Recruiting Churned Users](#recruiting-churned-users)
- [Panel Bias Awareness](#panel-bias-awareness)
- [Recruitment Ethics Checklist](#recruitment-ethics-checklist)
- [Sample Participant Agreement Clauses](#sample-participant-agreement-clauses)

---

## Recruitment Sources Comparison

| Source | Speed | Cost (per recruit) | Quality | Panel-Bias Risk | Best For |
|---|---|---|---|---|---|
| **Prolific** | Fast (hours) | $20–50 incl. incentive | High for surveys; moderate for usability | High — practiced participants | Screened surveys, comprehension tests, A/B preference studies |
| **Respondent** | Medium (1–3 days) | $50–150 | High — verified professionals | Medium | B2B/professional consumer segments, SaaS power users |
| **User Interviews** | Medium (2–5 days) | $75–200 | High — human-vetted | Medium | Moderated interviews, diary studies, longitudinal panels |
| **UserTesting Panel** | Fast (hours–1 day) | $40–100 | Moderate — thin screener by default | High | Unmoderated task tests, click-path studies |
| **ICW (Intercept)** | Very fast (same day) | Low ($5–20) | High context-validity | Low — real users in context | In-the-moment context discovery, wayfinding, physical space |
| **Customer Base Outreach** | Slow (3–7 days) | Near-zero cash cost | Highest — real users of your product | Low for behavioral; medium for opinion | Retention/churn interviews, feature validation, power-user deep-dives |
| **Social Ads** | Fast setup, slow fill | $20–80 | Variable — screening quality determines fit | Low — not a panel | Hard-to-reach segments, geographic targeting, niche demographics |
| **Snowball (referral)** | Slow, unpredictable | Low | Variable — homophily risk | Low for demographics | Communities of practice, rare conditions, cultural/linguistic subgroups |

**Read the bias column before you pick a source.** Panel respondents behave differently from first-time real users on usability tasks — see Panel Bias Awareness below.

---

## Screener Design

### Job-Task Screening Over Demographic Screening

Screen for what people *do*, not who they *are*. Demographics are proxies; tasks are evidence.

- Weak: "Age 25–40, employed full-time"
- Strong: "Filed a self-assessment tax return in the last 12 months without using an accountant"

Lead with behavior, frequency, and recency. Use demographics only to enforce representation quotas after task criteria are met.

### Anti-Cheat Questions

Use at least two of these three patterns per screener:

| Type | Example | Purpose |
|---|---|---|
| **Red-herring option** | Include a fictitious brand in a brand-recognition list | Catch participants claiming familiarity they cannot have |
| **Attention-check** | "Please select 'Strongly Disagree' for this question to confirm you are reading carefully" | Filter autopilot responders |
| **Behavioral specificity** | "Describe the last app you used to track your expenses" (open text) | Reveals whether experience is genuine |

Never telegraph the correct answer in the question itself ("Do you regularly use budgeting apps to manage your finances?" — this signals what to claim).

### Bias Toward Behavioral Recall

Use "tell me about a time you..." framing in screener open-text fields rather than "would you..." or "do you...":

- Weak: "Would you be interested in testing a new banking feature?"
- Strong: "Describe the last time you switched a financial product and what made you do it."

Hypothetical answers inflate willingness; recalled episodes reveal actual behavior.

### Length Cap: 3 Minutes Maximum

- Limit screeners to 8–12 questions.
- Abandonment rises sharply after the 3-minute mark; screener completion rates for consumer panels drop 20–40% beyond it.
- Move detailed questions to the pre-session consent form, not the screener.

### Quotas vs Natural Mix

Use **quotas** when:
- Representation of a specific subgroup is analytically required (e.g., at least 30% mobile-only users)
- Your product has a known user distribution you want to match

Use **natural mix** when:
- You are in discovery and do not yet know who the real users are
- Quotas would slow recruitment past your research timeline

Document your choice and its rationale in the study plan.

### Common Screener Anti-Patterns

| Anti-Pattern | Problem | Fix |
|---|---|---|
| Leading questions | Signals the "right" answer; inflates qualification rates | Write neutrally; move qualifying criteria to scoring logic |
| Demographic proxy rejection | Excludes valid participants on irrelevant grounds (e.g., rejecting non-graduates for a grocery app study) | Qualify on task fit, not educational attainment or income unless directly relevant |
| Overcrowded screener | Fatigue causes random responding | Cut to essential criteria; move nice-to-haves to a warm-up question in session |
| Binary experience questions | Misses frequency; "yes" could mean once ten years ago | Add frequency/recency follow-up ("How often in the last 3 months?") |
| Telegraphing the product | "We are testing a new food-delivery app — do you use food delivery?" | Describe the task domain obliquely until session consent |

---

## Incentive Ethics & Rates

### Rate Guidance (April 2026)

| Study Type | US Rate | UK Rate |
|---|---|---|
| Consumer interview (30 min, moderated) | $40–60 | £30–50 |
| Specialist domain interview (30 min) | $80–150 | £65–120 |
| Unmoderated usability test (15 min) | $20 | £15 |
| Survey ≤10 min | $5 | £4 |
| Diary study (per daily check-in) | $5–10 | £4–8 |

Adjust upward for: rare segments, accessibility participants, multi-session longitudinal commitments, senior professionals.

### Coercion Threshold

Incentives should fairly compensate time — not exceed it so dramatically that participation becomes economically compelled. A $200 incentive for a 20-minute survey from a low-income participant crosses the line from fair compensation into coercion. Calibrate to: local hourly wage equivalent × session hours × 1.25–1.5x for the value of their expertise and scheduling inconvenience.

### Payment Method Tradeoffs

| Method | Pros | Cons |
|---|---|---|
| Cash (PayPal, Venmo, bank transfer) | Universal; no restrictions | Slower; may require address collection |
| Amazon gift card | Instant; widely usable | Excludes non-Amazon users; geographic restrictions |
| Tango Card / Reward Link | Multi-retailer; flexible | Requires third-party platform |
| Platform-native (Prolific balance) | Frictionless | Only works within that platform |
| Charity donation (participant choice) | Ethical preference for some | Cannot substitute for cash for financial-hardship participants |

Offer choice where operationally feasible. Amazon cards are inaccessible in some countries and to participants without accounts.

### Tax Reporting

- **US**: Aggregate payments to a single participant exceeding **$600/calendar year** trigger IRS 1099-NEC reporting requirements. Track cumulative payments per participant per year. Collect W-9 forms before crossing the threshold.
- **UK**: HMRC treats research incentives as taxable income for participants above their personal allowance. This is the participant's responsibility to declare, but inform them in the participant agreement.
- **EU/Canada/AUS**: Each jurisdiction has equivalent thresholds — document and check locally for any study running >$500/year to a single participant.

### No-Show and Cancellation Policy

State clearly in the invitation:
- Full incentive if cancelled >24 hours before session
- Partial incentive (50%) if cancelled <24 hours before or if participant is >10 minutes late and session cannot run
- No incentive for no-shows without notice (unless documented hardship)
- Researcher-initiated cancellations should be paid in full

### Anti-Pattern: Differential Incentives by Feedback Valence

Never pay more for "confirmatory" feedback or less for negative feedback. Structuring payments to reward positive outcomes introduces systematic bias in who participates and what they say. Flat, time-based incentives only.

---

## Kids and Teens (Under 18)

### Legal Framework

| Regulation | Jurisdiction | Key Rule |
|---|---|---|
| **COPPA** | US | Parental consent required for data collection from under-13s; must use verifiable parental consent (VPC) mechanisms, not a checkbox |
| **ICO Children's Code** | UK | Age-appropriate design; applies to services "likely to be accessed" by under-18s; default to high privacy settings |
| **GDPR Art. 8** | EU | Under-16 requires parental consent for online services (UK: 13, Germany: 16 per member-state derogation) |
| **COPPA-equivalent EU** | EU | Parental consent required for processing children's data |

COPPA VPC methods include: signed consent form sent by postal mail, credit card verification, video call verification, government-ID upload. Email alone is not sufficient.

### Teen-Specific Session Protocol

- **Parent or guardian present** in room (under-13s) or within signal distance and reachable by phone (13–17s)
- **School-day timing**: avoid sessions during school hours unless study requires it; use after-school or weekend scheduling
- **Peer influence**: never recruit two teens who know each other for the same study cohort; peer dynamics suppress honest feedback
- **Assent vs consent**: child provides assent (agreement in age-appropriate language); parent provides legal consent; both are required
- **Moderator training**: researchers running under-18 sessions must have documented safeguarding awareness; single-interviewer remote sessions require a second observer present

### Anti-Patterns

- Recruiting through schools without institutional ethics review equivalent to IRB
- Recording audio or video without explicit written parental consent (separate from the screener)
- Using children's behavioral data from research as an input to marketing targeting — even if consent was technically obtained
- Applying adult screener standards (e.g., self-reported experience) without parent verification

---

## Hawthorne Effect Mitigation

### Definition

Participants change their behavior because they know they are being observed. This affects task performance, stated opinions, and error rates on usability tests — not just moderated sessions.

### Protocol Techniques

- **Think-aloud framing**: introduce as "tell me what you're thinking as you would while texting a friend" not "describe every click" — natural cadence reduces performance anxiety
- **Observer position**: place observers behind one-way glass or on a silent video feed; their presence in the room inflates task success rates
- **Multi-session design**: behavior in session 3 is more naturalistic than session 1; plan for novelty decay when study length allows
- **Acknowledge in writeup**: document the Hawthorne risk and what mitigation was applied; do not present observed behavior as equivalent to real-world behavior

### Anti-Pattern

Do not assume Hawthorne does not apply to "professional" remote unmoderated tests. Screen-recording software, knowing a researcher will review the session, and the explicit task framing all introduce observation effects even when no human is present.

---

## Time-of-Day and Geographic Bias

### Behavioral Patterns Shift by Time

- Commute-context app behavior differs from evening leisure behavior — same user, different intent, different errors
- Weekend usage patterns for consumer finance, entertainment, and health apps differ meaningfully from weekday
- Scheduling all sessions 10am–2pm local time systematically excludes shift workers, parents at school run, and gig workers during peak hours

### Global Product Recruiting

- Recruit across at least three time-zone clusters for global consumer products
- Do not run all international sessions at times convenient for the research team's home timezone
- Note: "global" Prolific samples skew heavily toward UK, US, and English-speaking participants — supplement with regional panel partners for non-English markets

### Documentation Requirement

State the temporal slice explicitly in your research findings: "All sessions conducted weekday mornings 9am–1pm GMT in May 2026." Reviewers and decision-makers need this to weight the findings appropriately.

---

## Social-Desirability Bias

### Sources

- Sensitive topics (finances, health, family conflict, illegal behavior)
- Social comparison contexts (questions about app use time, spending habits)
- Researcher-participant status dynamic (participants want to appear capable/responsible)

### Mitigation Techniques

| Technique | When to Use |
|---|---|
| Anonymous response mode | Surveys covering sensitive financial, health, or political topics |
| Self-administered survey inserts | Sensitive screener items that would be embarrassing to state to a moderator |
| Projective questions | When direct questions trigger defensiveness |
| Observed behavior over claimed | Task-based usability testing as ground truth vs interview self-report |

### "What Would Your Friend Think?" Projection

Ask about a third party to surface true attitudes: "What would your friend who's bad at saving money think about this feature?" — participants answer from their own perspective while attributing it to the fictional friend, reducing social-desirability pressure. Use sparingly; over-use becomes transparent.

---

## Accessibility Participant Recruitment

### Specialist Sources

| Source | Specialty |
|---|---|
| **Fable** | Disability-inclusive research panel, multiple AT types |
| **Applause** | Broad accessibility test pool including mobility, cognitive, visual |
| **Knowbility** | Blind and low-vision specialist participants |
| **AbilityNet / AccessWorks** | UK-based; screen reader and AT users |
| **Local CILs (Centers for Independent Living)** | US community partnerships; trusted by participants |
| **Disability:IN partner network** | Corporate disability inclusion; professional users |

### Recruit Per Assistive Technology, Not Per Disability Category

VoiceOver users, JAWS users, Dragon NaturallySpeaking users, and switch-access users have distinct interaction patterns and will find different failures. Grouping them into a single "screen reader" session produces noise. Recruit per AT type for usability work.

### Incentive Rates

Specialist accessibility participants command $80–150/session. This reflects their expertise, the additional time required for session setup, and the disproportionate burden of being asked to represent a broad population.

### Session Ethics

- Do not ask AT users to "perform" their disability or explain how assistive technology works unless that is explicitly the research question
- Meet participants where they are: use their own device and AT configuration, not a lab setup
- Provide technical support ahead of time for remote sessions — AT setup on unfamiliar software is a barrier, not a participant failure
- AT users are evaluating your product, not auditioning as study subjects

### Anti-Pattern

Bundling all "disabled" users into a single segment (e.g., "5 participants with disabilities") obscures meaningful findings and produces data that cannot drive actionable design changes. Segment by AT type and impairment category.

---

## Recruiting Underrepresented Demographics

### Race and Ethnicity

- Prolific's demographic mix does not mirror US Census distributions, particularly for Black, Hispanic/Latine, and Native American participants
- Partner with community-trusted recruiters (e.g., community radio stations, local nonprofits, churches, culturally specific platforms) for more representative panels
- Avoid extractive recruiting: participants should receive findings summaries when their community is the subject of the research

### Income

- Prolific and panel respondents skew higher-education and middle-income
- Specialist recruiters are required for low-income participant studies; community organizations, food banks, and workforce development programs can be partners
- Acknowledge in findings that low-income participant data likely underrepresents the actual user base if recruited through standard panels

### Rural vs Urban

- Rural participants are chronically underrepresented in UX research
- Connectivity constraints mean remote unmoderated tests need offline-capable backup options
- Rural consumer behavior (app store access, data cost sensitivity, device age) differs in ways that affect product decisions

### Trans and Non-Binary Participants

- Provide explicit pronoun fields in screeners (not just binary gender options)
- State in the screener and consent form how identity information will be stored and who will access it
- Use trauma-informed screening: avoid unnecessary questions about transition history or medical status unless directly relevant to the research question
- Respect withdrawal at any point without requiring explanation

### Anti-Patterns

- **Tokenism**: recruiting one participant from each underrepresented group and treating them as representatives of their entire population
- **Differential pay by region**: if a participant in Mexico performs the same task as a participant in London, paying them 80% less because of location-based rate adjustment devalues their contribution; use regional cost-of-living adjustment for incentive *purchasing power equivalence*, not a simple FX conversion
- **Demographic exhaustion**: repeatedly recruiting the same underrepresented participants because they are easy to find; rotate panels and sources

---

## Recruiting Churned Users

### Source Strategy

Source from your own analytics: users who completed at least 3 sessions then stopped in the last 60–180 days. Participation will skew toward frustrated or disappointed users — that is the point. Churned-user research is not a satisfaction study.

Differentiate:
- **One-time trial then gone**: product-fit mismatch; useful for onboarding research
- **Long-tenure then churned**: push force or pull force from a competitor; useful for retention and competitive research

### Interview Protocol

Use the Jobs-to-Be-Done switch interview format. Focus on the four forces:

1. **Push** from your product (what frustrated them)
2. **Pull** toward the alternative (what attracted them elsewhere)
3. **Anxiety** about switching (what almost kept them)
4. **Habit** that made switching hard (what they miss)

Avoid damage-limitation framing ("we've improved that feature since you left") — it suppresses honest push feedback.

### Anti-Pattern

Recruiting only active, satisfied customers and calling it customer research. Satisfaction studies measure sentiment among the survivors; they miss the exit reasons that matter most for retention strategy.

---

## Panel Bias Awareness

### The Core Problem

Prolific, UserTesting, and similar panel respondents are **practiced participants**. They:
- Complete 50–200+ studies per year
- Have developed efficient task strategies that real first-time users lack
- Are less likely to abandon on confusing flows
- Give more articulate verbal protocols than typical users

This means **task success rates and error rates on usability tests from panel respondents systematically overestimate real-world performance**.

### Mitigation

| Study Type | Source Recommendation |
|---|---|
| Behavioral usability study (what users can do) | Recruit from your own user base or via intercept for highest validity |
| Comprehension or preference study (what users understand or prefer) | Panel is acceptable when screener controls for task fit |
| Survey (attitudes, claimed behavior) | Panel with demographic quota; acknowledge panel-literacy bias in caveats |
| Longitudinal diary study | Panel is acceptable; first-session novelty effect documented |

For behavioral studies where accuracy matters, supplement panel recruiting with at-least-20% from your own customer base or new-to-category recruits.

---

## Recruitment Ethics Checklist

Before closing recruitment for any study, verify:

- [ ] Incentive rate reflects time and expertise fairly — not so excessive it constitutes coercion
- [ ] Participants were not selected or rejected on demographic proxies unrelated to the research question
- [ ] Parental consent obtained (written, verifiable) for all participants under 18 before any session begins
- [ ] Participants were informed of recording before consenting — no post-session surprise about video/audio capture
- [ ] Withdrawal is possible at any point without penalty to incentive already earned for time completed
- [ ] Screener does not telegraph desired answer or exclude participants for holding views unfavorable to the product
- [ ] Accessibility participants recruited per AT type, not bundled into a single "disabled users" cohort
- [ ] Churned and dissatisfied users included if the research question touches retention or product-market fit
- [ ] Tax reporting obligations identified for high-frequency or high-value participants
- [ ] Data retention period communicated to participants before they consent

---

## Sample Participant Agreement Clauses

The following clauses cover the minimum required topics. Legal review is required before use in formal studies; these are drafting starting points only.

---

**Consent to Participate**

> I voluntarily agree to participate in this research study conducted by [Organization]. I understand the study involves [brief description: e.g., a 30-minute usability session using a prototype mobile application]. I understand I may decline to answer any question and may withdraw at any time.

---

**Recording Consent**

> This session may be audio and/or video recorded. Recordings are used solely for internal research analysis and will not be published, shared externally, or used in marketing materials without a separate written agreement. I consent to this recording. I may withdraw recording consent at any time during the session; the session will continue without recording if I choose.

---

**Data Retention**

> Session recordings and notes will be retained for [e.g., 24 months] from the date of the session. After this period, all recordings will be permanently deleted. Anonymized research findings may be retained indefinitely. I may request deletion of my identifiable data at any time during the retention period by contacting [contact address].

---

**Withdrawal**

> I may withdraw from the study at any point without stating a reason. If I withdraw before the session begins, I will receive no incentive. If I withdraw after the session has started, I will receive a pro-rated incentive based on the time I participated. Withdrawal will not result in any penalty or adverse consequence.

---

**Payment**

> I will receive [amount and method] within [timeframe, e.g., 5 business days] following completion of the session. Payments may be reportable income under applicable tax law. It is my responsibility to comply with tax obligations in my jurisdiction. [US studies: if cumulative payments from [Organization] reach $600 in a calendar year, I will be asked to complete a W-9 form for IRS reporting purposes.]

---

*Last reviewed: April 2026. Jurisdiction-specific legal review required before use.*
