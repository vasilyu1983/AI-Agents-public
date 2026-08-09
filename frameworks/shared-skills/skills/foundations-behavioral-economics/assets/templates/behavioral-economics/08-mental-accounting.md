# Primitive: Mental Accounting

## Definition

Mental accounting is the set of cognitive operations individuals use to organize, evaluate, and keep track of financial activities (Thaler, 1985, 1999). The fundamental insight: money is not fungible in practice — people treat $100 from a bonus differently from $100 from their salary, and $100 in one mental account differently from $100 in another.

Core mechanisms:

1. **Segregated mental accounts**: people categorize money by source (salary, windfall, gift card, expense account) and by purpose (entertainment, groceries, luxuries). A dollar in the "entertainment" account is spent more freely than a dollar in the "savings" account.

2. **Sunk cost effect**: money already spent enters a mental account. People continue investing in something to "get their money's worth," even when future investment is irrational.

3. **Transaction utility**: the pleasure or pain of a transaction is not only about the outcome but about the deal quality — how the price compares to a reference price. A beer on a beach resort costs more than the same beer at a convenience store; the higher price is acceptable because the reference price for a "beach resort beer" is higher.

4. **Temporal framing**: whether a cost is framed as a one-time lump sum, monthly, or daily changes perceived size. $1/day feels less than $365/year, even though they are identical.

5. **Payment decoupling**: separating payment from consumption reduces the "pain of paying" — credit cards, memberships, prepaid accounts, and gift cards all decouple payment from use.

## When to Use

- **Price framing**: present an annual or large cost as a daily or weekly rate to reduce perceived size.
- **Bundling**: package multiple items together so the bundle price is evaluated against the bundle value, not itemized against each component.
- **Gift cards and credits**: money in a product-specific account is spent more freely than cash.
- **Free trial**: users who invest time and data in a product open a sunk-cost account; loss aversion on that investment supports conversion.
- **Expense account products**: B2B products paid from discretionary/opex budget are evaluated differently from personal spending.

## Misuse Boundary

**Ethical use**: Reframing costs accurately (daily rate is a legitimate alternative presentation of an annual cost). Bundling where the bundle is genuinely better value. Using payment decoupling to reduce friction for purchases the user genuinely wants to make.

**Manipulation**: Using daily-rate framing to obscure the total cost; creating sunk-cost traps deliberately designed to make exit feel painful; manufacturing a transaction utility illusion through fake reference prices; designing "free" credit that expires to pressure purchases the user would not otherwise make.

**Required conditions**:
1. Daily/weekly rate framing must always be accompanied by the total cost disclosure — never presented in isolation to obscure the real price.
2. Sunk cost prompts ("you've already invested X in setup") should be used to remind users of genuine value, not to coerce them into continuing a failing commitment.
3. Bundling must reflect genuine value combination, not just confusion about component prices.
4. Gift card/credit expiry must be disclosed at time of issuance.

## Inputs

- The price or cost to be communicated.
- The user's likely mental account category for this expense (personal vs business, discretionary vs essential).
- Whether bundling or unbundling better serves the user's decision.

## Outputs

- A price presentation that matches the user's mental account category.
- For large prices: a legitimate secondary framing (daily rate, alongside the total).
- For bundles: clear communication of what is included and why they belong together.

## Failure Modes

| Failure | Cause | Fix |
|---------|-------|-----|
| Daily rate framing is not believed | User immediately multiplies back to annual; the conversion makes the full price feel larger | Use both framings: "Just $0.99/day ($360/year)" — transparency increases trust |
| Bundle feels like overpricing | User mentally unbundles and compares each item to cheaper standalone options | Clearly articulate the value of items only available in the bundle; anchor the bundle against the unbundled total |
| Sunk cost framing backfires | User is reminded they've already failed to use what they paid for — produces guilt, not retention | Focus on future value, not past investment, unless prior usage was genuinely high |
| Gift card / credit drives unwanted purchases | User buys something they don't need to use expiring credit | Extend credit expiry; notify users before expiry with a genuinely useful suggested use |

## Worked Example

**Scenario**: B2B SaaS, $1,200/year per seat.

Without mental accounting: "Price: $1,200/year."

With mental accounting:
- Temporal reframe: "$100/month per seat." (Accurate; both are shown; monthly framing matches how SaaS budgets are typically evaluated.)
- Transaction utility: "Less than the cost of a day's contractor work, every month." (Relevant reference price for the target buyer's mental account.)
- Bundle framing: "Includes the analytics module ($300 value) and onboarding support ($500 value) — together for $1,200." (Only if those components have real standalone prices.)

**Ethical check**: $100/month is accurate for $1,200/year. The contractor comparison is plausible and relevant. Bundle component prices are real.

## Sources

- Thaler, R. H. (1985). Mental accounting and consumer choice. _Marketing Science_, 4(3), 199–214. — foundational paper.
- Thaler, R. H. (1999). Mental accounting matters. _Journal of Behavioral Decision Making_, 12(3), 183–206. — extended treatment.
- Ariely, D. (2008). _Predictably Irrational_, ch. 4. — pain of paying and payment decoupling.
- Loewenstein, G. & Prelec, D. (1991). Negative time preference. _American Economic Review_, 81(2), 347–352. — temporal framing and payment timing.
