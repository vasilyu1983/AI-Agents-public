# Primitive 09 — Ellsberg and Allais Paradoxes (EU Violations)

## Definition

The Ellsberg and Allais paradoxes are canonical empirical violations of EU theory. They mark the boundary conditions under which EU should be applied with caution or supplemented.

---

### Allais Paradox (1953)

Violates the independence axiom of EU. Most people prefer:

- Problem 1: A certain £1M over B = {89% × £1M, 10% × £5M, 1% × £0}.
- Problem 2: C = {90% × £0, 10% × £5M} over D = {89% × £0, 11% × £1M}.

Under EU, preferences in Problem 1 imply D ≻ C; preferences in Problem 2 imply C ≻ D. The combination violates EU's independence axiom.

**Mechanism**: The certainty effect — people disproportionately prefer certain outcomes over probabilistically equivalent gambles (certainty is weighted beyond its probability). This is captured by prospect theory's probability weighting function.

---

### Ellsberg Paradox (1961)

Violates the sure-thing principle under ambiguity. A classical setup:

An urn contains 90 balls: 30 red, 60 black or yellow (unknown split).

- Problem 1: Most prefer Bet A (£100 if red) over Bet B (£100 if black).
- Problem 2: Most prefer Bet D (£100 if black or yellow) over Bet C (£100 if red or yellow).

Under EU, the preferences in Problem 1 imply p(red) > p(black), and the preferences in Problem 2 imply p(black) > p(red). No consistent probability assignment can explain both.

**Mechanism**: Ambiguity aversion — decision makers prefer known risks (objective probabilities) over unknown risks (ambiguous probabilities). This is not irrational under Ellsberg; it violates Savage's sure-thing principle, not classical probability theory.

## When to Use

- **Diagnostic**: Check whether a choice problem has the structure of an Allais or Ellsberg paradox before applying EU.
- **Allais structure** (independence-axiom risk): Switch to prospect theory (#8) for descriptive accuracy; apply EU correction techniques (rank-dependent utility) for normative work.
- **Ellsberg structure** (ambiguous probabilities): Switch to minimax regret (#3), maximin, or Choquet expected utility. Do not assign flat priors to unknown probabilities.

## Inputs

| Input | Description |
|-------|-------------|
| Choice set | The set of lotteries or bets under consideration |
| Observed preferences | Actual choices or stated preferences from stakeholders |
| Probability structure | Objective (known) vs. ambiguous (unknown) probabilities |

## Outputs

| Output | Description |
|--------|-------------|
| Paradox classification | Allais type (independence violation) or Ellsberg type (ambiguity) |
| Recommended alternative | EU safe / prospect theory / minimax regret |
| Confidence in EU applicability | Whether EU analysis is reliable for this decision |

## Failure Modes

- **Applying EU to ambiguous probabilities**: When probabilities are genuinely unknown, assigning flat priors and using EU is not neutral — it encodes a specific and contestable belief. Use minimax regret (#3) or Choquet EU instead.
- **Dismissing paradoxes as irrationality**: Ellsberg preferences are consistent with a coherent non-EU theory (ambiguity aversion). Treating ambiguity-averse choices as errors leads to wrong recommendations.
- **Ignoring paradox diagnosis in high-stakes decisions**: For major capital allocation or regulatory decisions, check whether the choice structure maps to either paradox before relying on EU rankings.

## Worked Example

A company is allocating a product development budget across two options:

- Option A: Launch into Market X where conversion rate data exists (p(success) = 0.45 from 2 years of comparable launches). Probability is known.
- Option B: Enter Market Y, a newly opened segment. No historical conversion data; probability is genuinely unknown.

EU analysis treats both with the same probability (perhaps 0.45 for Y by analogy). An Ellsberg-aware analysis recognizes that the company's leadership will exhibit ambiguity aversion toward Option B regardless of its expected value. Two responses:
1. For descriptive prediction: predict the choice leans toward Option A due to ambiguity aversion.
2. For normative robustness: apply minimax regret (#3) to Option B's ambiguous outcomes and compare with EU for Option A.

## Sources

- Allais, M. (1953). "Le comportement de l'homme rationnel devant le risque." Econometrica 21(4).
- Ellsberg, D. (1961). "Risk, Ambiguity, and the Savage Axioms." Quarterly Journal of Economics 75(4).
- Gilboa, I. and Schmeidler, D. (1989). "Maxmin Expected Utility with Non-Unique Prior." Journal of Mathematical Economics 18(2).
- Schmeidler, D. (1989). "Subjective Probability and Expected Utility without Additivity." Econometrica 57(3).
