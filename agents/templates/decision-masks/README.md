# Decision Masks — Index

7 cognitive frames that decorate an existing perspective agent's brief without restructuring the team. Layer one mask onto a member at launch — the mask changes the *question* the agent answers, not the team shape. For methods that restructure the team's discussion, see [`../debate-methods/`](../debate-methods/). For cross-folder stacks, see [`../composition-recipes.md`](../composition-recipes.md).

## Masks

| File | Mask | Use when |
|------|------|----------|
| [first-principles.md](first-principles.md) | Strip assumptions; reason from physical / economic / mathematical primitives | Stated reasoning is convention-bound; analogies dominate |
| [inversion.md](inversion.md) | Reframe forward question as "how would we guarantee the opposite?" | Happy-path thinking dominates; downside under-examined |
| [regret-minimization.md](regret-minimization.md) | Project to long horizon; ask which choice you'd most regret | Reversibility is asymmetric; emotional weight is opaque |
| [second-order.md](second-order.md) | Ask "and then what?" past first-order effects | Decisions look fine at first order but cascade |
| [anchoring-mask.md](anchoring-mask.md) | Discard the stated number; re-derive from primitives; reconcile last | Pricing, budgets, estimates, negotiation — any decision with a planted numeric anchor |
| [base-rate-mask.md](base-rate-mask.md) | Start from population frequency before incorporating salient evidence | Forecasting, risk assessment, "will this work?" decisions where vivid anecdotes dominate |
| [constitutional-mask.md](constitutional-mask.md) | Two-pass self-critique against an explicit principles list, then revise | Solo reviewers with hard non-negotiables (security, compliance, brand voice); agents whose output ships without a debate behind them |

## How to compose

- **Architecture / risk reviews**: inversion (exposes optimism bias)
- **Strategic / long-horizon**: regret-minimization
- **Convention-heavy domains**: first-principles
- **Policy / system changes**: second-order
- **Pricing / budgets / estimates**: anchoring-mask (every member, not just the skeptic)
- **Forecasts / "will this work?" decisions**: base-rate-mask on the optimist
- **Solo security / compliance / brand reviewer**: constitutional-mask with 5-10 explicit principles
- **Multiple frames**: layer 2-3 masks across different agents in the same team — each agent wears one mask
- **Don't compound skepticism**: inversion + base-rate + pre-mortem on one agent collapses into "everything fails" — distribute
- **Constitutional inside a debate is overkill**: debate already provides external critique. Use constitutional only for solo reviewers without a debate behind them

## Layering with debate methods

Masks and debate methods compose:

- Six Thinking Hats team + each hat-wearing agent also gets a Mask → method shapes structure, mask shapes individual reasoning
- Courtroom debate + Inversion mask on Defense Counsel → defense argues "what would guarantee this fails?"
- Pre-Mortem method + Second-Order mask → cascading failure-mode mapping

## Related templates

- [`../debate-methods/`](../debate-methods/) — team-level discussion structures
- [`game-theory/`](../../../skills/universal/foundations-game-theory/assets/templates/game-theory/) — coordination, contribution, and synthesis mechanisms
