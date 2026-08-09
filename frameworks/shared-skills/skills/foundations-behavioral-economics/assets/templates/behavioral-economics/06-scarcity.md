# Primitive: Scarcity

## Definition

Scarcity is the psychological principle that objects and opportunities are perceived as more valuable when their availability is limited (Cialdini, 1984). Two distinct mechanisms:

1. **Quantity scarcity**: limited number of units available ("Only 3 seats left").
2. **Time scarcity / urgency**: limited time window for an opportunity ("Offer ends Friday").

Underlying mechanism: scarcity triggers loss aversion (a limited resource activates the fear of missing out — losing the opportunity), and it also serves as a quality signal (if many people want it and supply is constrained, it must be valuable).

Key properties:
- Real scarcity produces genuine urgency; fabricated scarcity produces short-term urgency followed by trust destruction when discovered.
- Scarcity works best when the user already has some desire for the item — it converts intent to action, it does not create desire from nothing.
- Specific counts ("3 left") outperform vague signals ("limited availability").
- Combined quantity + time scarcity compounds the effect but also compounds the manipulation risk if either signal is false.

## When to Use

- **Inventory-constrained products**: seats in a cohort, units of a physical item, slots in a service.
- **Time-limited pricing**: genuine promotional pricing with an end date.
- **Waitlists**: real capacity constraints drive waitlist demand signal.
- **Event registration**: genuine capacity limits.
- **Beta access**: genuinely limited early-access slots.

## Misuse Boundary

**Ethical use**: Display scarcity signals only when the constraint is real. If 3 seats are left, showing "3 seats left" is accurate. If the pricing window has a real end date, a countdown is honest.

**Manipulation**: Perpetual countdown timers that reset; fake "X people are viewing this now"; inventory counts that are fabricated or inflated for effect; false urgency where the offer recurs indefinitely.

**Required conditions**:
1. The scarcity signal reflects a real constraint.
2. Inventory counts are updated in real time or are conservatively estimated.
3. Countdown timers expire and are not reset automatically.
4. If an offer recurs (e.g., monthly pricing), it is not presented as "one-time only."
5. UK ASA CAP Code: claims of limited availability must be verifiable. Fake urgency is a misleading commercial practice under CPRs 2008.

**Signal of misuse**: if removing the scarcity signal would not actually change the outcome for the user (they can still buy at the same price next week), the signal is manipulative.

## Inputs

- Real inventory count, seat count, or time constraint.
- The point in the user journey where scarcity is displayed (must be after intent is established).
- The update mechanism: how is the count kept accurate?

## Outputs

- A scarcity signal tied to a real, verifiable constraint.
- A clear action that lets the user act before the constraint closes.
- An honest message if the constraint expires or changes ("This offer has ended").

## Failure Modes

| Failure | Cause | Fix |
|---------|-------|-----|
| Scarcity signal ignored | User has seen too many fake countdowns; trust is depleted | Use specific, verifiable counts rather than generic urgency language; explain the source of the constraint |
| Scarcity creates anxiety without conversion | User doesn't have enough information to decide; urgency triggers paralysis | Only add scarcity after the user has enough information to act; pair scarcity with a low-friction next step |
| Trust destroyed post-purchase | User finds out the "limited" offer recurred the following week | Never present a recurring offer as one-time; if the price changes periodically, say so honestly |
| Regulatory action | ASA challenge on fake urgency claims | Use only verifiable constraints; remove timer on expiry |
| Scarcity without desire | Scarcity signal on a product the user hasn't expressed interest in | Build desire first; scarcity converts intent, it doesn't create it |

## Worked Example

**Scenario**: Online course with a cohort starting on a fixed date with 30 seats.

Without scarcity: "Enroll now." Deadline is mentioned in the FAQ.

With ethical scarcity:
- Quantity signal: "4 seats remaining in the March cohort." (Updated in real time from enrollment database.)
- Time signal: "Enrollment closes March 15 at 11:59 PM GMT." (Real date; the course starts March 16.)
- Action: "Reserve your seat →"

After enrollment closes: the timer is removed; the page shows "March cohort is full — join the waitlist for April."

**Ethical check**: Both constraints are real. The inventory count is accurate. The timer expires and is not reset. The waitlist is for a real future cohort.

**Contrast with manipulation**: A perpetual "Only 2 spots left!" counter that never decreases, on a self-paced digital product with unlimited capacity — fabricated scarcity, fails harm test.

## Sources

- Cialdini, R. B. (1984). _Influence: The Psychology of Persuasion_, ch. 6 (Scarcity). — foundational.
- Worchel, S., Lee, J. & Adewole, A. (1975). Effects of supply and demand on ratings of object value. _Journal of Personality and Social Psychology_, 32(5), 906–914. — scarcity and perceived value.
- Cialdini, R. B. (2016). _Pre-Suasion_. — scarcity as attention channeling.
- ASA CAP Code (UK). Section 3 (Misleading advertising), Section 8 (Sales Promotions). — fake urgency guidance.
