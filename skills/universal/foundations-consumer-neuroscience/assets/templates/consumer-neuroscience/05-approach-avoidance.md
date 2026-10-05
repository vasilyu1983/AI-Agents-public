# Primitive: Regulatory Focus & Fit (behavioural)

> File name kept for inbound links. Links elsewhere that say "BAS/promotion" or "BIS/prevention" framing should be read as **promotion/prevention framing**. BIS/BAS is a different construct (see below).

## Definition

**Regulatory focus** (Higgins 1997) describes two self-regulatory orientations:

- **Promotion focus:** goals framed as advancement, gains and ideals. Sensitive to the presence or absence of positive outcomes ("gain", "achieve", "unlock").
- **Prevention focus:** goals framed as safety, duties and avoiding mistakes. Sensitive to the presence or absence of negative outcomes ("protect", "never miss", "stay safe").

Both orientations exist in everyone. Focus can be **chronic** (a disposition), **situationally primed** (by the task or context) or **self-primed**. For product decisions, the decision context often sets the operative focus more than the person does: insurance, security and compliance tasks lean prevention; growth and discovery tasks lean promotion.

**Regulatory fit** (Higgins 2000) is the operative mechanism. When the way a goal is pursued, or the way a message is framed, matches the orientation active for that decision, people "feel right" about it and value the choice more. What matters is the fit between frame and goal, not a label attached to a user.

**Moderators matter.** Motyka et al. (2014), a meta-analysis in the Journal of Consumer Psychology, 24(3):394–410, found fit effects on evaluation, behavioural intention and behaviour. These effects vary by:

- the source of focus (chronic, situation-primed or self-primed);
- orientation (promotion or prevention);
- how fit is created (sustaining vs matching);
- how fit is constructed (action vs observation);
- scope (incidental vs integral).

Do not assume one fit effect size carries across these conditions.

**Not the same as BIS/BAS.** Carver & White's (1994) BIS/BAS scales measure reinforcement sensitivity: behavioural inhibition vs activation. They are a different construct from regulatory focus. Self-report measures of regulatory focus also disagree with each other: Summerville & Roese (2008) found two widely used dispositional scales largely uncorrelated. Do not label a user "BIS-dominant, therefore prevention-focused", and do not treat any one scale as ground truth without validating it for the decision at hand.

## When to Use

- Choosing between gain-framed and safety-framed copy for a specific decision (signup, upgrade, renewal, security step).
- Auditing a funnel where the decision is prevention-shaped (risk, reliability, privacy) but the copy is uniformly promotional, or the reverse.
- Designing trust-repair or safety messaging where a true prevention benefit exists.

## Misuse Boundary

**Ethical use:** a frame that truthfully describes what the product does for that decision. Safety framing is honest when the risk and the protection are real.

**Manipulation:** manufacturing threat to trigger avoidance-motivated purchase ("act now or lose [fabricated consequence]"). This is false urgency and pressure selling, both named in CMA DMCC enforcement. For wellness, anxiety or financial-distress audiences, default to no fear-based framing unless it passes the harm test in SKILL.md.

**Required condition:** every prevention frame points to a real risk the user could face and a real protection the product provides.

## Inputs

- The decision the copy supports and whether it is mainly about gaining or protecting.
- The product's true value on that decision: does it advance, protect, or both?
- Optional segment signal: an **explicit** stated-goal question ("What matters most: getting more done / not missing anything?") or a validated measure. **Not** referral source, channel or demographics as a proxy for orientation.

## Outputs

- Two copy variants for the same offer: a gain frame and a safety frame, each truthful.
- An A/B test with a pre-declared primary outcome (conversion) and guardrails (comprehension, perceived pressure, refunds or cancellations).
- If segmenting: pre-declared stated-goal segments, with the interaction tested rather than assumed.
- An audit of existing copy listing decisions where the frame and the decision type mismatch.

## Failure Modes

| Failure | Likely cause | Fix |
|---|---|---|
| Conversion gap between traffic channels | Intent, traffic quality, page expectations or offer fit differ by channel; orientation is only one of many explanations | Randomise frames **within** each channel; do not route by channel on the assumption |
| Safety frame wins overall but raises anxiety complaints | Fear-based framing crossed into pressure | Keep the protective fact, drop the threat language; add a perceived-pressure guardrail |
| Frame effect disappears at the form step | Frame fit at the headline does not carry to privacy, commitment or cost questions at the form | Answer those questions directly: privacy assurance, easy cancellation, full price |
| Trust-repair message reads as spin | Gain-framed apology ("get back on track") with no real safeguard | State the actual safeguard added and the remedy |
| "Personalised by orientation" beats control in one test, then fails | Segment proxy invalid or test underpowered | Validate the segment measure; replicate before personalising |

## Worked Example

**Scenario:** a daily-reading wellness app shows "Unlock your daily guidance and live with more clarity." Hypothetically, it converts 3.2% of organic-search visitors and 0.8% of visitors from anxiety-related articles.

**Wrong diagnosis:** "Organic traffic is BAS/promotion, anxiety referrals are BIS/prevention, so serve each channel its own page." This treats channel as a classifier. The gap could equally come from intent (article readers were not shopping), expectation mismatch with the referring article, or visitor quality.

**Better approach:**

1. Hypothesis: for visitors whose goal is steadiness rather than growth, a truthful safety-framed headline fits the decision better.
2. Randomise both headlines within each channel:
   - Gain: "Unlock daily guidance. Live with more clarity."
   - Safety: "A steady daily check-in, whenever you need one."
3. Pre-declare the outcomes: conversion, a perceived-pressure item, and 30-day cancellation.
4. Optionally add one stated-goal question at signup to test the fit interaction on the next iteration.

**Ethical check:** the safety frame promises only what the product does. There is no threat language, and the offer is identical in both arms. The audience is vulnerability-adjacent, so fear framing ("never face another anxious morning…") is excluded.

## Sources

- Higgins, E. T. (1997). Beyond pleasure and pain. _American Psychologist_, 52(12), 1280–1300. DOI 10.1037/0003-066X.52.12.1280.
- Higgins, E. T. (2000). Making a good decision: Value from fit. _American Psychologist_, 55(11), 1217–1230. DOI 10.1037/0003-066X.55.11.1217.
- Motyka, S., Grewal, D., Puccinelli, N. M., Roggeveen, A. L., Avnet, T., Daryanto, A., de Ruyter, K. & Wetzels, M. (2014). Regulatory fit: A meta-analytic synthesis. _Journal of Consumer Psychology_, 24(3), 394–410. DOI 10.1016/j.jcps.2013.11.004.
- Summerville, A. & Roese, N. J. (2008). Self-report measures of individual differences in regulatory focus: A cautionary note. _Journal of Research in Personality_, 42(1), 247–254. DOI 10.1016/j.jrp.2007.05.005.
- Carver, C. S. & White, T. L. (1994). Behavioral inhibition, behavioral activation, and affective responses to impending reward and punishment. _JPSP_, 67(2), 319–333. BIS/BAS scales; a distinct construct.
