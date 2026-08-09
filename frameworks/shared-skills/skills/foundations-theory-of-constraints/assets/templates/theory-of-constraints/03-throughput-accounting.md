# Primitive: Throughput Accounting (TA)

**Source**: Goldratt 1990, *The Haystack Syndrome*; Corbett 1998, *Throughput Accounting*; Cox & Spencer 1998.

## Definition

Throughput Accounting is the TOC financial measurement system. It replaces cost accounting's focus on local efficiency with three global metrics:

- **Throughput (T)**: the rate at which the system generates money through sales. `T = Sales Revenue − Totally Variable Costs (TVC)`. TVC is only the costs that change with each unit sold (raw materials, sales commission per unit) — not labor, overhead.
- **Investment / Inventory (I)**: all the money the system has invested to generate throughput. Includes raw materials, WIP, finished goods, equipment, buildings.
- **Operating Expense (OE)**: all the money the system spends to convert Investment into Throughput — salaries, rent, depreciation, utilities.

**Goal**: Increase T, decrease I and OE. This inverts the cost-accounting priority: T comes first.

**Net Profit (NP)** = T − OE
**Return on Investment (ROI)** = (T − OE) / I
**Productivity** = T / OE
**Investment Turns** = T / I

## When to Use

- Evaluating whether a product mix decision increases or decreases system throughput.
- Deciding whether to accept a discounted order (if T per unit > 0 and constraint time is available).
- Comparing process improvement projects by their impact on T, I, OE — not just cost reduction.
- Roadmap prioritization: rank features by T per unit of constraint time consumed.

## Inputs

- Revenue per product/feature/order.
- Truly Variable Costs per unit (materials only — not allocated labor).
- Constraint capacity in time units.
- Current OE (fixed for the planning horizon).

## Outputs

- T/CU (Throughput per Constraint Unit): the ranking metric for product mix optimization.
- Decision: accept or reject an order, a product, or a project.
- Projected NP and ROI before and after the proposed change.

## Failure Modes

| Failure | Root Cause | Fix |
|---------|-----------|-----|
| Allocating labor into TVC | Labor is nearly always a step-fixed cost, not truly variable | Keep TVC = materials + direct commission only |
| Cutting cost instead of growing T | Cost accounting bias — OE reductions feel safe | Evaluate every decision by impact on T first, then I and OE |
| Product mix ignores constraint | Products ranked by margin, not T/CU | Rank by T per minute of constraint time, not gross margin |
| Accepting a negative-T order "to cover overhead" | Overhead allocation thinking | Any positive-T order above zero TVC contributes to NP if OE is fixed |
| Using TA without knowing the constraint | T/CU ranking is meaningless without the constraint identified | Run 5FS (primitive 01) before applying TA |

## Worked Example

**Context**: A SaaS company offers two plans, Pro and Enterprise. Constraint is the onboarding team (100 hours/month).

| Metric | Pro | Enterprise |
|--------|-----|-----------|
| Price per deal | $500 | $3,000 |
| TVC per deal | $50 (infra) | $300 (infra + partner fee) |
| T per deal | $450 | $2,700 |
| Onboarding hours per deal | 2 h | 15 h |
| T/CU (per onboarding hour) | $225 | $180 |

**Cost-accounting view**: Enterprise looks better ($2,700 margin vs $450).
**Throughput-accounting view**: Pro generates $225 per constraint hour vs Enterprise's $180. If the constraint cannot be elevated, a Pro-heavy mix generates more NP.

**Decision**: optimize mix toward Pro until onboarding capacity is elevated (hire or automate).

## Cost-Accounting Decision Traps (Expert Judgment)

Cost accounting is not "wrong" in general — it is required for statutory reporting and it is the correct tool for many decisions. The trap is applying its allocation logic to constrained-capacity decisions, where it systematically produces the wrong answer. Four traps a non-expert reliably misses:

1. **Overhead allocation reverses the ranking.** Allocating fixed OE per unit makes high-volume, low-margin-per-unit products look worse than low-volume, high-margin ones — even when the high-volume product generates far more T per hour of the actual constraint. Any per-unit "fully loaded cost" figure that includes allocated fixed overhead should be treated as unreliable for mix decisions; recompute on T/CU.
2. **Sunk and step-fixed costs get treated as variable.** Labor, most software infrastructure, and equipment depreciation are step-fixed (they don't change with one more unit sold) but are routinely allocated per-unit in cost systems, inflating apparent per-unit cost and killing profitable-at-the-margin decisions. TVC in throughput accounting is deliberately narrow — materials, per-unit commissions, per-transaction fees — precisely to avoid this trap.
3. **"Efficiency" metrics reward the wrong local behavior.** Machine or team utilization targets (e.g., "keep the team at 90%+ utilization") push non-constraint resources to build inventory/WIP that the constraint cannot absorb, which raises I without raising T — the opposite of the goal. This is a policy-constraint trap (#10) masquerading as a productivity metric.
4. **Marginal-cost intuition without constraint-awareness double-counts capacity.** "This order only costs us $X in materials, so anything above $X is profit" is correct only when the constraint has slack. If the order consumes constraint time that a higher-T/CU order could have used, the true cost is the forgone T/CU of the displaced work — not the TVC. Always check constraint headroom before accepting a low-price, low-margin order on marginal-cost logic alone.

**When cost accounting is still the right tool**: capital budgeting across multi-year horizons, statutory/tax reporting, external financial communication, and any decision with no meaningfully constrained resource in the loop. Throughput accounting is a decision lens for constrained-capacity choices, not a replacement for GAAP/IFRS bookkeeping.

## Sources

- Goldratt, E.M. (1990). *The Haystack Syndrome: Sifting Information Out of the Data Ocean*. North River Press.
- Corbett, T. (1998). *Throughput Accounting*. North River Press.
- Cox, J.F. & Spencer, M.S. (1998). *The Constraints Management Handbook*. CRC Press.
- Dettmer, H.W. (2007). *The Logical Thinking Process*. ASQ Quality Press.
