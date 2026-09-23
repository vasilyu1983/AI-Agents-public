# Practical Decision Contract

## Elicitation artifact

Record decision maker, action set including outside/wait actions, horizon and affected population, mutually exclusive exhaustive states, probability provenance and ranges, utility scale/wealth state, constraints and signal likelihoods. Elicit independently before discussion; distinguish measured frequency, subjective forecast and market price. A model-generated probability needs outcome-based calibration evidence, not verbal confidence. Use foundations-statistical-inference for calibration uncertainty and foundations-measurement-theory for input validity.

## Sensitivity and tipping points

For every recommendation vary defensible probabilities, scenario bounds and utility curvature; show where the preferred action changes and which ranges have no defensible prior. State whether a criterion is expected utility, minimax regret or survival-constrained growth. MCDA weight sensitivity and alternative-set rank reversal are separate checks. Do not combine ordinal ranks and utility amounts into an undisclosed scalar.

## Costs, time and sequential decisions

Build a small decision tree: chance nodes use conditional probabilities, decision nodes choose maximum conditional utility, leaves include terminal wealth and sunk versus future costs. Discount consistently and include information delays and foregone actions. Backward induction requires a faithful state/transition model; use planning for legal actions and optimization for the specified mathematical objective.

EVPI/EVSI are on the supplied utility scale. Subtract a monetary study cost directly only under a justified conversion (e.g., risk-neutral net monetary benefit); with nonlinear utility incorporate cost into each terminal outcome and recalculate expected utility. Information arriving after the last relevant decision has no value for that decision, but can have value for later decisions.

Use the existing finite-state calculator for exact finite signal enumeration; it does not model dynamic trees, nonlinear cash-to-utility cost conversion, external population validity or continuous-state optimization. A finite regret matrix is a computation choice, not a theorem restricting minimax regret to finite states.

## Completion and controls

Deliver input/provenance table, selected rule, current and information-contingent actions, utility-compatible cost comparison, sensitivity thresholds and constraints. Unknown utilities or unsupported probabilities mean a conditional scenario recommendation, not objective decision authority.

Known answers: symmetric +1/-1 action and outside zero with 75%-accurate signal has EVPI=.5 and EVSI=.25; uninformative signal has EVSI=0; an irrelevant additional action can change a regret benchmark; utility-scale multiplication also scales utility-denominated study cost. Run the existing calculator tests.
