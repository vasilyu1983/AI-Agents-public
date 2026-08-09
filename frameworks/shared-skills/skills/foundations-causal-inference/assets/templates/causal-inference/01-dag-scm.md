# Primitive 1: DAGs and Structural Causal Models

## Definition

A **Directed Acyclic Graph (DAG)** encodes causal assumptions as nodes (variables) and directed edges (X → Y means X directly causes Y). Acyclic means no variable can cause itself through any chain of arrows.

A **Structural Causal Model (SCM)** augments the DAG with equations: each variable X_i = f_i(Pa_i, U_i), where Pa_i are its direct causes (parents) and U_i is an independent exogenous noise term. SCMs support counterfactual reasoning; DAGs alone support identification.

Key graph concepts:
- **Confounder**: a common cause of X and Y (creates a backdoor path)
- **Mediator**: a variable on the directed path from X to Y
- **Collider**: a common effect of two variables; conditioning on a collider opens a spurious path
- **d-separation**: graphical criterion for reading conditional independence from the DAG

## When to Use

Use DAGs as the first step in every causal analysis, regardless of method. Without an explicit DAG:
- Confounders, mediators, and colliders cannot be reliably distinguished
- Adjustment sets cannot be verified
- Identification cannot be checked
- Method selection defaults to guesswork

Draw the DAG before touching data.

## Inputs / Outputs

**Inputs**: domain knowledge about the data-generating process; variable list; directional hypotheses about relationships.

**Outputs**: a DAG encoding assumed causal structure; lists of confounders, mediators, and colliders; a verified adjustment set for the target causal effect; identification status (identifiable or not).

## Worst Failure Modes

1. **Omitting a confounder**: leaving an arrow out of the DAG because data for that variable is unavailable. Omitted confounders bias estimates but are invisible unless modeled explicitly.
2. **Conditioning on a collider**: including a collider in the adjustment set opens a spurious path. Example: including "employee performance" (a collider for ability and effort) in an analysis of training → salary.
3. **Confusing mediator with confounder**: adjusting for a mediator blocks the causal path; adjusting for a confounder removes bias. They look identical in the data.
4. **Drawing the DAG after seeing the data**: post-hoc DAG construction retrofits assumptions to results and defeats the purpose.
5. **Assuming faithfulness when selection is present**: in datasets constructed by conditioning on a collider (e.g., only users who converted), independence assumptions from the DAG no longer hold.

## Worked Example

**Setting**: an e-commerce site wants to estimate whether showing a discount banner (X) increases checkout completion (Y). Age (Z) affects both whether users see the banner (via targeting) and their baseline checkout rate.

**DAG**:
```
Z (Age) → X (Banner shown)
Z (Age) → Y (Checkout)
X (Banner shown) → Y (Checkout)
```

Z is a confounder. The backdoor path X ← Z → Y must be blocked by conditioning on Z. If instead we also added "cart value" (C), where C is caused by both X and Y, C would be a collider. Conditioning on C would open a spurious X ↔ Y path.

**Adjustment set**: {Z} satisfies the backdoor criterion. Regression of Y on X and Z identifies the causal effect.

**Collider trap**: if we filtered the dataset to high-cart-value sessions (conditioned on C), the X-Y association would be distorted even after conditioning on Z.

## Sources

1. Pearl, J. (2009). *Causality: Models, Reasoning, and Inference* (2nd ed.). Cambridge University Press. Chapter 1–2.
2. Hernán, M. A., & Robins, J. M. (2020). *What If*. Chapman & Hall/CRC. Chapters 6–7.
3. Elwert, F. (2013). Graphical Causal Models. In S. Morgan (Ed.), *Handbook of Causal Analysis for Social Research*. Springer.
