# Primitive: Approach-Avoidance & Regulatory Focus (BIS/BAS)

## Definition

Not all users process the same offer with the same motivational system. Two distinct neural orientations govern how users appraise stimuli and approach decisions:

1. **BAS (Behavioral Activation System)**: Governed by dopaminergic approach circuitry; sensitive to reward signals, gains, and positive outcomes. BAS-dominant users are promotion-focused (Higgins, 1997): they make decisions to advance, grow, and acquire. They respond to "gain more," "unlock," "achieve." Their default mode is opportunity-seeking.

2. **BIS (Behavioral Inhibition System)**: Governed by the septo-hippocampal system; sensitive to threat signals, potential losses, and goal conflict (Gray; Carver & White, 1994). BIS-dominant users are prevention-focused: they make decisions to protect, avoid mistakes, and maintain safety. They respond to "protect," "never miss," "stay safe." Their default mode is threat-avoidance.

Regulatory focus theory (Higgins, 1997) extends this to self-regulation: promotion-focused individuals are motivated by the presence/absence of gains; prevention-focused individuals are motivated by the presence/absence of losses. Both orientations can be present in the same person depending on context — chronic orientation is a trait; situational orientation is state-dependent.

Implications:
- A single-tone funnel (uniformly promotional) converts BAS users but produces regulatory mismatch — and trust drop — in BIS users.
- Prevention framing for a product with genuine safety or reliability value is legitimate and more effective for BIS audiences than gain framing.
- The same product can be framed for both orientations; the key is not duplicating work but testing or personalizing tone.

## When to Use

- Writing copy for a mixed audience where BIS/BAS proportions are unknown.
- Segmenting a funnel by referral source (wellness/anxiety content often skews BIS; achievement/growth content skews BAS).
- Designing trust-repair flows, which almost always require prevention framing for the BIS-activated trust-skeptic.
- Auditing single-tone funnels for regulatory-focus mismatch that explains conversion gaps.

## Misuse Boundary

**Ethical use**: match copy tone to the user's genuine motivational orientation. Using prevention framing for a product that has real safety or reliability value is honest. Using promotion framing for an achievement-oriented context is honest.

**Manipulation**: manufacturing threat to activate BIS in users who are not genuinely at risk, in order to drive avoidance-motivated purchase ("If you don't act now, you'll miss [fabricated consequence]"). This overlaps with manufactured scarcity and false urgency under DMCC Act 2024 — pressure selling is explicitly named in the 18 November 2025 CMA enforcement actions.

**Required condition**: prevention framing must be grounded in real risks or real losses the user could experience. BIS activation via fabricated threat is a dark pattern.

## Inputs

- User segment or referral source context (proxy for chronic BIS/BAS orientation).
- The product's genuine value proposition (does it primarily advance or protect?).
- The current funnel stage (pre-purchase prevention framing; post-purchase promotion framing for retention may differ).

## Outputs

- Two copy variants: promotion frame ("Unlock / Achieve / Gain") and prevention frame ("Protect / Never miss / Stay safe").
- A/B test or personalization rule routing by referral source or stated use-case signal.
- A regulatory-focus audit of existing funnel copy identifying mismatch points.

## Failure Modes

| Failure | Cause | Fix |
|---------|-------|-----|
| Bounce concentrated in one referral-source segment | Regulatory-focus mismatch: segment is BIS-dominant but landing page is uniformly promotional | Serve prevention-framed variant to BIS-proxy referral sources |
| Trust-repair flow not recovering NPS | Apology copy is achievement-framed ("get back on track") for a BIS-activated user in threat-appraisal mode | Shift trust-repair to prevention framing: "We've put safeguards in place so this cannot happen again" |
| Wellness audience converts poorly on "unlock your potential" headline | BIS-dominant chronic orientation in wellness/anxiety context; promotion frame triggers mismatch anxiety | Test prevention frame: "Never wonder again whether you're on the right path" |
| High CTR but low form completion | BAS activation got the click; BIS activation on the form (data sharing, commitment) causes abandonment | Address BIS concerns at the form: privacy assurance, easy cancellation, no hidden fees |

## Worked Example

**Scenario**: A daily wellness reading app is running a single landing page headline: "Unlock your daily guidance and live with more clarity." Conversion is 3.2% from organic search but only 0.8% from anxiety-related content referrals.

Diagnosis: organic traffic is BAS-dominant (seeking growth and clarity); anxiety-content referrals are BIS-dominant (seeking protection and reassurance). The promotion-framed headline produces regulatory mismatch for the BIS segment.

Fix:
- BAS page (organic): "Unlock daily guidance. Live with more clarity." (unchanged)
- BIS page (anxiety referrals): "Never face another anxious morning without a grounding read. Your daily anchor, always there."

**Ethical check**: the prevention framing is grounded in a real product behavior (a daily reading that users report helps them feel grounded). No fabricated threat. The offer is the same on both pages.

## Sources

- Higgins, E. T. (1997). Beyond pleasure and pain. _American Psychologist_, 52(12), 1280–1300. — foundational regulatory focus theory.
- Carver, C. S. & White, T. L. (1994). Behavioral inhibition, behavioral activation, and affective responses to impending reward and punishment. _Journal of Personality and Social Psychology_, 67(2), 319–333. — BIS/BAS scale and behavioral evidence.
