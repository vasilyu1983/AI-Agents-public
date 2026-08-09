# Primitive 3: Backdoor and Frontdoor Criteria

## Definition

**Backdoor path**: a path from X to Y that starts with an arrow *into* X (i.e., goes "backward" through a cause of X). These paths carry spurious association that must be blocked.

**Backdoor criterion**: A set Z satisfies the backdoor criterion for (X, Y) if:
1. No element of Z is a descendant of X.
2. Z blocks every backdoor path from X to Y.

If Z satisfies the backdoor criterion:
P(Y | do(X = x)) = Σ_z P(Y | X = x, Z = z) P(Z = z)

This is the **adjustment formula** — a weighted average of the conditional outcome over the distribution of Z.

**Frontdoor criterion**: A set M satisfies the frontdoor criterion for (X, Y) if:
1. All directed paths from X to Y pass through M.
2. There are no unblocked backdoor paths from X to M.
3. All backdoor paths from M to Y are blocked by X.

**Minimal adjustment set**: among all valid backdoor adjustment sets, the minimal one minimizes variance and avoids unnecessary conditioning that can amplify noise or introduce collider bias.

## When to Use

- **Backdoor criterion**: whenever you have measured confounders and want to identify the causal effect by regression or stratification.
- **Frontdoor criterion**: when the confounder is unobserved but a mediator satisfying the three conditions exists.
- **Checking both**: before specifying any regression model. The adjustment set is not "all available covariates" — it is the minimal set satisfying the relevant criterion.

## Inputs / Outputs

**Inputs**: a DAG; the target causal effect (X → Y); a candidate adjustment set Z.

**Outputs**: confirmation that Z satisfies the backdoor criterion (or frontdoor); the adjustment formula to apply; identification of variables that should *not* be included (descendants of X, colliders).

## Worst Failure Modes

1. **Including descendants of X**: adjusting for a descendant of the treatment (including outcomes or proxies of outcomes) blocks causal paths and biases the estimate.
2. **Collider conditioning via adjustment**: including a collider in Z opens spurious paths rather than blocking them. Standard regression on all observed covariates routinely does this.
3. **Over-adjustment (M-bias)**: adjusting for a variable that is not on a backdoor path but is a collider for two unobserved variables. Adjusting for it introduces bias where none existed.
4. **Assuming "more controls = better"**: this is false in causal inference. Every conditioning variable must be justified by the DAG.
5. **Ignoring time ordering**: using a variable measured *after* treatment as a control variable can condition on a mediator or post-treatment collider.

## Worked Example

**Setting**: Does job training (X) increase earnings (Y)? Confounders: baseline ability (A) and motivation (M). Motivation is also influenced by participation eligibility rules based on age (G).

**DAG**:
```
A → X
A → Y
M → X
M → Y
G → X [via eligibility, so G → X but not G → Y directly]
```

**Backdoor paths**:
- X ← A → Y: blocked by conditioning on A
- X ← M → Y: blocked by conditioning on M

**Valid adjustment set**: {A, M}. Conditioning on G is unnecessary — G is not on a backdoor path. Conditioning on G doesn't hurt here (it doesn't open new paths), but in more complex graphs it can.

**Adjustment formula**:
P(Y | do(X = 1)) = Σ_{a,m} P(Y | X = 1, A = a, M = m) P(A = a, M = m)

**Numbers** (simplified):
- P(Y=1 | X=1, A=high, M=high) = 0.8
- P(Y=1 | X=0, A=high, M=high) = 0.6 → CACE = 0.2
- P(Y=1 | X=1, A=low, M=low) = 0.5
- P(Y=1 | X=0, A=low, M=low) = 0.4 → CACE = 0.1
- P(A=high, M=high) = 0.4, P(A=low, M=low) = 0.6

ATE = 0.4 × 0.2 + 0.6 × 0.1 = 0.08 + 0.06 = 0.14

## Sources

1. Pearl, J. (2009). *Causality*. Cambridge University Press. Chapter 3.
2. Greenland, S., Pearl, J., & Robins, J. M. (1999). Causal Diagrams for Epidemiologic Research. *Epidemiology*, 10(1), 37–48.
3. VanderWeele, T. J., & Shpitser, I. (2011). A New Criterion for Confounder Selection. *Biometrics*, 67(4), 1406–1413.
