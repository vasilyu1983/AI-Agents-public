# Primitive: Hyperbolic Discounting

## Definition

Hyperbolic discounting is the empirical finding that people discount future rewards at a rate that decreases as the delay increases — contrary to the constant discounting assumed by standard economic theory. The result is **present bias**: disproportionate preference for immediate rewards over delayed ones, even when the absolute delay difference is the same.

The quasi-hyperbolic (β-δ) model (Laibson, 1997; O'Donoghue & Rabin, 1999):
- **β (present bias parameter)**: discount factor applied to anything that is not immediate. β < 1 means future outcomes are discounted more than a patient long-term agent would.
- **δ (long-run discount factor)**: standard exponential discount rate applied uniformly across future time periods.
- **Combined**: Utility of a reward at time t = β × δᵗ × value(reward). The additional β penalty is applied to all future rewards, creating a "today vs not-today" cliff.

Practical implications:
- A user will choose $100 today over $110 in a week, but will choose $110 in 5 weeks over $100 in 4 weeks — the same $10/$7-day gap feels different depending on how far in the future it is.
- **Commitment devices** work because people who anticipate future present bias will voluntarily pre-commit to constrain their future selves.
- **Free trials exploit present bias**: getting the product now (benefit is immediate) while deferring the commitment to pay (cost is future) — ethically acceptable when the trial is fair; manipulative when cancellation is deliberately obstructed.

## When to Use

- **Annual vs monthly billing**: annual plan has a higher upfront cost (present cost) vs monthly (distributed cost). Present bias depresses annual plan adoption.
- **Free trial design**: immediate access (present reward) with deferred payment decision.
- **Commitment devices**: prompt users to pre-commit to an action (schedule a setup call, set a reminder, lock in pricing) before their attention moves elsewhere.
- **Habit-formation features**: streaks, scheduled reminders, recurring reviews — all fight present bias by creating near-term rewards for future-oriented behavior.
- **Savings or long-term investment products**: present bias is the primary adoption barrier; interventions must make future benefit feel proximate.

## Misuse Boundary

**Ethical use**: Design to help users act in accordance with their own stated preferences and long-term interests. Commitment devices are ethical when the user chooses them voluntarily and benefits from the pre-commitment. Trials are ethical when the user can cancel as easily as they signed up.

**Manipulation**: Exploiting present bias by making subscription sign-up trivially easy (immediate gratification) while hiding or obstructing the cancellation path (imposing future costs to override the commitment). Designing "dark patterns" where users get the benefit now and the unwanted cost only materializes months later when the cancellation window has been obscured.

**Required conditions**:
1. Commitment devices are offered, not imposed. The user must choose to pre-commit.
2. Free trials must have a cancellation path that is as easy as the sign-up path.
3. Annual billing must clearly disclose the total upfront cost and refund policy.
4. Any "lock-in" should be disclosed before the user makes the commitment, not revealed after.
5. UK context: auto-renewing subscriptions must comply with CMA guidance on subscription traps; cancellation must be straightforward.

## Inputs

- The decision horizon: when does the user receive the benefit vs incur the cost?
- The present vs future cost-benefit structure of the offer.
- The user's likely present bias level for this domain (financial decisions vs daily habits differ).

## Outputs

- A framing or offer structure that bridges the present-future gap.
- Optional: a commitment device (scheduled follow-up, saved configuration, pre-booked slot).
- Optional: a reframing that makes the future benefit feel more immediate (showing projected outcome now).

## Failure Modes

| Failure | Cause | Fix |
|---------|-------|-----|
| Annual plan conversion is low | Monthly billing is the default; annual cost feels large upfront | Reframe annual cost as daily/monthly rate; offer a comparison to the monthly total; make annual the default with opt-out |
| Commitment device is ignored | User doesn't believe the future self-problem is real for them | Make the benefit of pre-commitment tangible; show evidence of what happens without it |
| Trial converts but churns immediately | User signed up for immediate reward with no intent to continue | Qualify trial sign-ups; show value during trial; use loss aversion at expiry for users who engaged |
| Present-bias mitigation feels patronizing | User reads "you probably won't do this later" as insulting | Frame commitment devices as a convenience tool, not a warning about willpower |

## Worked Example

**Scenario**: Annual plan for a $30/month SaaS product ($360 billed annually vs $30 × 12 = $360, but with 20% annual discount = $288).

Without hyperbolic discounting awareness: "Annual plan: $288/year."

With hyperbolic discounting mitigation:
- Present-frame the benefit: "Save $72 today by switching to annual."
- Reframe the cost: "$24/month — locked in." (Makes $288 feel like a monthly figure.)
- Reduce the perceived upfront cost: "Billed as one payment of $288." (Accurate, but stated neutrally.)
- Commitment device: on the plan-selection screen, offer "Remind me to review monthly vs annual in 3 months" as an alternative if they're not ready to commit.

**Ethical check**: $288 annual figure is accurate. The commitment device is voluntary. The trial-to-annual path discloses the charge date clearly. Cancellation before the billing date is available.

## Sources

- Laibson, D. (1997). Golden eggs and hyperbolic discounting. _Quarterly Journal of Economics_, 112(2), 443–478. — quasi-hyperbolic (β-δ) model.
- O'Donoghue, T. & Rabin, M. (1999). Doing it now or later. _American Economic Review_, 89(1), 103–124. — present bias and procrastination.
- Frederick, S., Loewenstein, G. & O'Donoghue, T. (2002). Time discounting and time preference: A critical review. _Journal of Economic Literature_, 40(2), 351–401. — comprehensive review.
- Thaler, R. H. & Sunstein, C. R. (2008). _Nudge_, ch. 6 (Save More Tomorrow). — commitment devices in the wild.
